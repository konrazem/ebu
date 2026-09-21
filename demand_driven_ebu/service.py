"""Additive economic service allocation, and the combined service requirement.

The correction this module exists for: **separate economic demand ids are
separate material obligations**. Two independent orders of two units at the
same destination require four delivered units, not two. Testing each order on
its own against the plan's increment silently let one delivered unit satisfy
both, which is the defect this module removes.

For a plan `G` and a destination coordinate `c`, the **service pool** is what
`G` actually put there:

    pool(G, c) = max(0, delta_G[c])

Net, not gross, and that is deliberate. A unit that arrives at `c` and leaves
again in the same plan is not present afterwards, so it is not available to any
order. Taking gross inflow would re-introduce exactly the double-count this
module is removing, one level down.

An **allocation** assigns each economic order `d` at `c` a served quantity

    0 <= s_d(G) <= q_d,        sum_d s_d(G) <= pool(G, c)

and `d` is completely served exactly when `s_d(G) = q_d`. Because the model
admits only plans that serve every demand in a component completely, the
allocation on any plan in a menu is the trivial one, `s_d = q_d` for all `d`;
the general allocator exists so that shortfalls can be *audited* rather than
inferred.

**Physical demand is not an economic quantity claim.** A shortfall at `c` is a
condition on the post-state, `x_c + delta_G[c] >= x*_c`. It draws nothing from
the economic pool, and nothing is subtracted between the two. The same two
delivered units may fulfil a two-unit order *and* close a two-unit deficit,
because the units being present at `c` afterwards is what both conditions ask
for. What is additive is economic quantity against economic quantity. So the
combined requirement at a coordinate is a maximum, not a sum:

    delta_G[c]  >=  max( sum_d q_d ,  deficit_c )
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from gaussian_harness.numerics import Refusal, Vector

ALLOCATION_RULE_ID = "EBU-DEMAND-ADDITIVE-ECONOMIC-ALLOCATION-v1"


def pool(increment: Vector, coordinate: int) -> Fraction:
    """What the plan actually delivered to this coordinate, floored at zero."""
    delivered = increment[coordinate]
    return delivered if delivered > 0 else Fraction(0)


@dataclass(frozen=True)
class CoordinateRequirement:
    """Everything demanded at one coordinate, with the two claims kept apart."""

    coordinate: int
    economic_total: Fraction
    economic_ids: tuple[str, ...]
    economic_quantities: tuple[tuple[str, Fraction], ...]
    physical_deficit: Fraction
    physical_id: str | None

    def __post_init__(self) -> None:
        if self.economic_total < 0 or self.physical_deficit < 0:
            raise Refusal("a requirement cannot be negative")
        summed = Fraction(0)
        for _, quantity in self.economic_quantities:
            summed += quantity
        if summed != self.economic_total:
            raise Refusal("economic total does not equal the sum of its orders")

    @property
    def required_delta(self) -> Fraction:
        """max(economic, physical). The two claims do not add to each other."""
        return max(self.economic_total, self.physical_deficit)

    @property
    def demand_ids(self) -> tuple[str, ...]:
        ids = list(self.economic_ids)
        if self.physical_id is not None:
            ids.append(self.physical_id)
        return tuple(sorted(ids))


def requirements(demands) -> tuple[CoordinateRequirement, ...]:
    """Collect a demand collection into one requirement per coordinate."""
    economic: dict[int, list] = {}
    physical: dict[int, object] = {}
    for demand in demands:
        if demand.demand_class == "E":
            economic.setdefault(demand.coordinate, []).append(demand)
        else:
            if demand.coordinate in physical:
                raise Refusal(
                    f"two physical demands at coordinate {demand.coordinate}; "
                    "P-demand is derived per coordinate and must be unique"
                )
            physical[demand.coordinate] = demand

    built = []
    for coordinate in sorted(set(economic) | set(physical)):
        orders = sorted(economic.get(coordinate, []), key=lambda d: d.demand_id)
        total = Fraction(0)
        for order in orders:
            total += order.quantity
        shortfall = physical.get(coordinate)
        built.append(
            CoordinateRequirement(
                coordinate,
                total,
                tuple(order.demand_id for order in orders),
                tuple((order.demand_id, order.quantity) for order in orders),
                shortfall.required if shortfall is not None else Fraction(0),
                shortfall.demand_id if shortfall is not None else None,
            )
        )
    return tuple(built)


def serves_all(reqs: tuple[CoordinateRequirement, ...], increment: Vector) -> bool:
    """Whether one plan increment completely serves every demand collected."""
    return all(increment[req.coordinate] >= req.required_delta for req in reqs)


def unmet(reqs: tuple[CoordinateRequirement, ...], increment: Vector) -> tuple[str, ...]:
    """Demand ids this increment does not completely serve.

    An economic shortfall at a coordinate is attributed to **every** order
    there. Which particular order goes unserved is not a fact about the plan:
    the plan delivered a pool, and the pool is short. Naming one of them would
    be inventing a priority the model does not have.
    """
    failed: list[str] = []
    for req in reqs:
        delivered = increment[req.coordinate]
        if req.economic_total > 0 and delivered < req.economic_total:
            failed.extend(req.economic_ids)
        if req.physical_id is not None and delivered < req.physical_deficit:
            failed.append(req.physical_id)
    return tuple(sorted(failed))


@dataclass(frozen=True)
class ServiceAllocation:
    """The explicit `s_d(G)` at one coordinate, plus the pool it drew on."""

    coordinate: int
    pool: Fraction
    demanded: Fraction
    allocations: tuple[tuple[str, Fraction], ...]
    complete: bool
    shortfall: Fraction

    def __post_init__(self) -> None:
        summed = Fraction(0)
        for _, served in self.allocations:
            if served < 0:
                raise Refusal("an allocation cannot be negative")
            summed += served
        if summed > self.pool:
            raise Refusal(
                f"allocation {summed} exceeds the delivered pool {self.pool} "
                f"at coordinate {self.coordinate}"
            )

    @property
    def allocation_map(self) -> dict[str, Fraction]:
        return dict(self.allocations)


def allocate(req: CoordinateRequirement, increment: Vector) -> ServiceAllocation:
    """Allocate the delivered pool across the economic orders at a coordinate.

    When the pool covers every order, each is served in full and the result is
    the only allocation the model ever acts on. When it does not, the orders
    are filled in canonical id order until the pool is exhausted. That partial
    fill is **diagnostic only**: it explains the size and location of a
    shortfall and is never consulted by any completion predicate, because the
    model has no partial service.
    """
    available = pool(increment, req.coordinate)
    if available >= req.economic_total:
        return ServiceAllocation(
            req.coordinate,
            available,
            req.economic_total,
            req.economic_quantities,
            True,
            Fraction(0),
        )
    remaining = available
    filled: list[tuple[str, Fraction]] = []
    for demand_id, quantity in req.economic_quantities:
        served = quantity if quantity <= remaining else remaining
        filled.append((demand_id, served))
        remaining -= served
    return ServiceAllocation(
        req.coordinate,
        available,
        req.economic_total,
        tuple(filled),
        False,
        req.economic_total - available,
    )


def allocations(
    reqs: tuple[CoordinateRequirement, ...], increment: Vector
) -> tuple[ServiceAllocation, ...]:
    return tuple(allocate(req, increment) for req in reqs if req.economic_ids)


def served_economic_ids(
    reqs: tuple[CoordinateRequirement, ...], increment: Vector
) -> tuple[str, ...]:
    """Economic orders completely served by this increment, set-level.

    Every order at a coordinate is served together or none is, because the
    component contract admits no plan that serves them partially.
    """
    done: list[str] = []
    for allocation in allocations(reqs, increment):
        if allocation.complete:
            done.extend(demand_id for demand_id, _ in allocation.allocations)
    return tuple(sorted(done))
