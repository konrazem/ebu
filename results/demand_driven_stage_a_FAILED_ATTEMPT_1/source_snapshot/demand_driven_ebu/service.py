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
condition on the physical state. It draws nothing from the economic pool, and
nothing is subtracted between the two. The same two delivered units may fulfil
a two-unit order *and* restore a two-unit deficit, because the units being
present at `c` afterwards is what both conditions ask for. What is additive is
economic quantity against economic quantity.

## The two completion contracts are NOT the same, and are not collapsed

The earlier revision reduced both claims to one scalar threshold,
`delta_G[c] >= max(sum_d q_d, deficit_c)`. That collapse is withdrawn. It is a
**semantic error**: it imposed the economic completion contract on a physical
condition that does not need it, and in the frozen Study-1 world it made 36 of
the 91 physical states absorbing away from equilibrium for reasons that were
never physical scarcity (finding F-7).

    E-demand   an exogenous contractual obligation with its own identity and
               lifecycle. Its residual, if it were served partially, would have
               to be STORED against that order id -- a backlog quantity, which
               the contract forbids. So E service stays COMPLETE-SERVICE ONLY
               and separate orders stay additive:

                   serves_economic(G, c)  <=>  delta_G[c] >= sum_d q_d

    P-demand   an endogenous condition read off the physical state every epoch
               and thrown away again. Its residual needs no record at all: the
               state IS the record. So P service requires genuine positive
               progress and nothing more:

                   serves_physical(G, c)  <=>  delta_G[c] > 0

               After execution P-demand is re-derived from the new state, so a
               deficit of 4 restored by 2 simply presents as a deficit of 2 at
               the next derivation. There is no residual-demand object anywhere
               in this package, and none is introduced.

## STRONG atomic P-provenance: at least one, not every one

A plan has legitimate physical provenance exactly when it makes **strict
positive progress on at least one P-demand that exists at the pre-action
state**. It is **not** required to progress every other P-demand in the same
coupled component.

That qualifier is the whole of this rule, and dropping it broke sequential
refinement. At `(1,4,7)` with `x* = (4,4,4)` the plan `B->A@2` is legitimate:
it restores two of `A`'s three missing units. Subdividing it into `B->A@1`
twice must stay legitimate at both baselines -- but the first half creates a
**new** deficit at `B`, and a rule demanding progress on every P-demand in the
component would then refuse the second half for not progressing the deficit it
had just created. A restoration that is legal whole and illegal in halves is
not atomic at all.

Coupling survives for what it is actually for: genuine shared physical
constraints, competing stock, shared routes and joint executability. It no
longer carries a contract that one plan must progress every P-demand it
touches. **P-demands are state conditions, not joint economic orders.**

## Two questions that are never collapsed

    demand provenance   "why may this action be considered?"
    EBU valuation       "what is the complete physical consequence?"

Provenance is decided here. Valuation is decided in `valuation`, over the whole
state transition, `E = V(pre) - V(post)`, with every side effect included at
full weight. An action that restores one deficit while deepening another is
admissible -- it has provenance -- and is **not** thereby physically beneficial:
its exact EBU carries the damage, and affordability and every actor policy see
that exact number. Nothing is hidden, netted or removed.

**Attribution is capped, legality is not.** A plan that delivers more than the
represented deficit is legal -- overshoot is permitted physical semantics and
stays so -- but it is credited with restoring only `min(delta_G[c], deficit_c)`.
The overshoot is not a service credit; it is a physical fact that the next
derivation reads back as an opposite deviation.

**What this does not change.** Irredundancy is untouched, so an action
unrelated to a currently represented deficit is still illegal: if dropping it
leaves a plan that still serves and still executes, the plan carrying it is not
in any menu. Incremental restoration buys no new provenance.
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

    # There is deliberately no `required_delta` here. Collapsing the two claims
    # into one scalar threshold was the semantic error F-7 records: it imposed
    # the economic completion contract on a physical condition. The two
    # predicates below are the definition, and nothing may reduce them to a
    # single number.

    def serves_economic(self, delivered: Fraction) -> bool:
        """Complete service of every economic order here. Additive, unchanged.

        **Vacuously true where no order stands.** A coordinate carrying only a
        physical condition imposes no economic threshold at all, so a plan that
        draws stock *out* of it -- which a legitimate restoration elsewhere may
        well do -- is not failing an economic claim that does not exist.
        """
        if self.economic_total == 0:
            return True
        return delivered >= self.economic_total

    def serves_physical(self, delivered: Fraction) -> bool:
        """Genuine positive progress on the represented physical deficit.

        Vacuously true where there is no physical deficit. Never a completion
        threshold: the remainder is carried by the physical state itself and is
        re-derived after the transition.
        """
        if self.physical_id is None:
            return True
        return delivered > 0

    def physical_progress(self, delivered: Fraction) -> Fraction:
        """Restoration credited to the P-demand here, capped at the deficit.

        Legality is decided by `serves_physical`; this is attribution only.
        Overshoot is legal and is simply not credited as service -- it shows up
        as an opposite deviation in the next derivation instead.
        """
        if self.physical_id is None or delivered <= 0:
            return Fraction(0)
        return delivered if delivered <= self.physical_deficit else self.physical_deficit

    def physical_remainder(self, delivered: Fraction) -> Fraction:
        """Diagnostic only: `deficit - progress`.

        The authoritative residual is whatever `derive_physical_demands` reads
        off the post-state. Nothing in the model stores this number, and no
        completion predicate consults it.
        """
        return self.physical_deficit - self.physical_progress(delivered)

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
    """Whether one plan increment serves this requirement set.

    Two conditions, and they are different in kind:

    * **every** economic claim is completely served -- a hard gate, unchanged;
    * the plan actually serves **something**: either some economic claim is
      present (and is therefore complete, by the gate above), or at least one
      physical claim is progressed.

    The physical side is deliberately *existential*. Requiring progress on every
    P-demand of a component would re-impose a joint-service contract on
    conditions that are not joint obligations, and would make a legal
    restoration illegal in halves. See the module docstring and finding F-7.
    """
    if not reqs:
        return False
    for req in reqs:
        if not req.serves_economic(increment[req.coordinate]):
            return False
    if any(req.economic_total > 0 for req in reqs):
        return True
    return any(
        req.serves_physical(increment[req.coordinate])
        for req in reqs
        if req.physical_id is not None
    )


def serves_jointly(
    reqs: tuple[CoordinateRequirement, ...], increment: Vector
) -> bool:
    """Every economic claim complete **and** every physical claim progressed.

    **Not the menu predicate, and it must never be used as one.** `serves_all`
    is existential on the physical side by design (strong atomic provenance).
    This is the *coexistence* question, which is a different question:

        is there a plan that completely serves these new economic obligations
        and still makes progress on every physical need that already exists?

    Admission asks exactly that, and only that, to honour contract section 6 --
    a new *optional* economic obligation may not starve an existing physical
    need when that can be seen in advance. It is a statement about competing
    stock and simultaneous executability, not a service contract: nothing here
    obliges any menu plan to progress every P-demand of its component.
    """
    return all(
        req.serves_economic(increment[req.coordinate])
        and req.serves_physical(increment[req.coordinate])
        for req in reqs
    )


def served_ids(
    reqs: tuple[CoordinateRequirement, ...], increment: Vector
) -> tuple[str, ...]:
    """Exactly the demands this increment serves, each under its own contract.

    Economic ids appear when their coordinate's additive total is met.
    Physical ids appear when their deficit is **progressed**, which is what
    provenance is attached to -- never the P-demands a plan merely leaves
    alone or makes worse.
    """
    found: list[str] = []
    for req in reqs:
        delivered = increment[req.coordinate]
        if req.economic_total > 0 and req.serves_economic(delivered):
            found.extend(req.economic_ids)
        if req.physical_id is not None and req.serves_physical(delivered):
            found.append(req.physical_id)
    return tuple(sorted(found))


def unmet(reqs: tuple[CoordinateRequirement, ...], increment: Vector) -> tuple[str, ...]:
    """Demand ids this increment does not serve, each under its own contract.

    An economic order is unmet when the pool is short of the additive total. A
    physical demand is unmet when the plan makes **no progress** on it -- not
    when a remainder survives, because a remainder is the normal outcome of
    incremental restoration and is carried by the physical state.

    An economic shortfall at a coordinate is attributed to **every** order
    there. Which particular order goes unserved is not a fact about the plan:
    the plan delivered a pool, and the pool is short. Naming one of them would
    be inventing a priority the model does not have.
    """
    failed: list[str] = []
    for req in reqs:
        delivered = increment[req.coordinate]
        if req.economic_total > 0 and not req.serves_economic(delivered):
            failed.extend(req.economic_ids)
        if req.physical_id is not None and not req.serves_physical(delivered):
            failed.append(req.physical_id)
    return tuple(sorted(failed))


# `unmet` lists every demand this increment does not serve, which is the right
# diagnostic for an economic shortfall but is NOT the provenance rule for a
# physical one: under strong atomic provenance a plan is never obliged to
# progress every P-demand, so P-demands it leaves alone are not failures.
# Provenance is built from `served_ids` differences instead; see `plans._build`.


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


@dataclass(frozen=True)
class PhysicalService:
    """What one plan actually did to one represented physical deficit.

    Every field is a function of the pre-state, the plan and the post-state.
    Nothing here is stored between epochs and nothing here is a completion
    predicate: the authoritative remainder is re-derived from the post-state by
    `derive_physical_demands`, and `remainder` below is the diagnostic that
    explains it, exactly as `ServiceAllocation` explains an economic shortfall.
    """

    coordinate: int
    demand_id: str
    deficit_before: Fraction
    delivered: Fraction
    progress: Fraction
    remainder: Fraction
    overshoot: Fraction

    def __post_init__(self) -> None:
        if self.progress > self.deficit_before:
            raise Refusal(
                f"attributed progress {self.progress} exceeds the represented "
                f"deficit {self.deficit_before} at coordinate {self.coordinate}"
            )
        if self.progress < 0 or self.remainder < 0 or self.overshoot < 0:
            raise Refusal("physical service quantities cannot be negative")
        if self.progress + self.remainder != self.deficit_before:
            raise Refusal("progress and remainder must close on the deficit")

    @property
    def complete(self) -> bool:
        """Whether this one plan happened to close the whole deficit.

        Reporting only. It is **not** a legality condition: incremental
        restoration is legitimate precisely because this may be false.
        """
        return self.remainder == 0


def physical_service(req: CoordinateRequirement, increment: Vector) -> PhysicalService:
    delivered = increment[req.coordinate]
    progress = req.physical_progress(delivered)
    overshoot = delivered - progress if delivered > progress else Fraction(0)
    return PhysicalService(
        req.coordinate,
        req.physical_id,
        req.physical_deficit,
        delivered,
        progress,
        req.physical_deficit - progress,
        overshoot,
    )


def physical_services(
    reqs: tuple[CoordinateRequirement, ...], increment: Vector
) -> tuple[PhysicalService, ...]:
    """One record per represented physical deficit this plan progressed."""
    return tuple(
        physical_service(req, increment)
        for req in reqs
        if req.physical_id is not None and req.serves_physical(increment[req.coordinate])
    )


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
