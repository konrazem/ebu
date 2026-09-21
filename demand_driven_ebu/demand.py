"""The two demand classes, and what completely serving one means.

`P` is physical demand. It is not sampled, scheduled or stored: it is read off
the physical state every epoch and thrown away again. A coordinate that sits
below its declared reference *is* a physical need, and it stays one for exactly
as long as the shortfall does. Nothing can vote it out of existence; it can
only be resolved, left unresolved, be currently impossible to resolve, or be
currently unaffordable to resolve.

`E` is economic demand. It arrives from outside, it does not have to correspond
to any physical shortfall, and it may ask for more than physically exists. EBU
does not decide why society wants the resource; it measures the physical
consequence of the ways of supplying it.

Both classes reduce to the same service test, which is the reason they can
coexist in one unordered obligation set without a scheduler:

    demand d at coordinate c requiring q is completely served by plan G
    exactly when  delta_G[c] >= q.

For `E`, `q` is the requested quantity. For `P`, `q` is the shortfall
`x*_c - x_c`, so the test reads `x_c + delta_G[c] >= x*_c`. Because the test is
a property of the plan's *net* increment rather than a sum of per-action
credits, one action serving several demands cannot be counted twice, and there
is no credit ledger in which double-counting could occur.

Overshoot is permitted: delivering more than `q` still delivers `q`. That is
deliberate rather than lax. It is what leaves a hostile actor a real choice —
it may serve the obligation destructively — instead of collapsing the hostile
policy into a policy that cannot act at all.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from fractions import Fraction

from gaussian_harness.numerics import Refusal, Vector, exact

from .world import DemandWorld

CLASS_PHYSICAL = "P"
CLASS_ECONOMIC = "E"

E_PROPOSED = "E_PROPOSED"
E_ADMITTED_PENDING = "E_ADMITTED_PENDING"
E_SERVED = "E_SERVED"
E_REJECTED_PHYSICAL_SCARCITY = "E_REJECTED_PHYSICAL_SCARCITY"
E_REJECTED_INCOMPATIBLE = "E_REJECTED_INCOMPATIBLE"
E_ADMITTED_BUT_EBU_UNAFFORDABLE = "E_ADMITTED_BUT_EBU_UNAFFORDABLE"

E_TERMINAL_STATUSES = (E_SERVED, E_REJECTED_PHYSICAL_SCARCITY, E_REJECTED_INCOMPATIBLE)


def state_identity(state: Vector) -> str:
    """A stable name for the physical state a P-demand was read from."""
    text = ";".join(f"{value.numerator}/{value.denominator}" for value in state)
    return hashlib.sha256(text.encode("ascii")).hexdigest()[:16]


@dataclass(frozen=True)
class PhysicalDemand:
    """A shortfall against the declared reference. Derived, never created."""

    coordinate: int
    resource: str
    node: str
    required: Fraction
    origin_state_identity: str

    def __post_init__(self) -> None:
        if self.required <= 0:
            raise Refusal("a physical demand needs a strictly positive shortfall")

    @property
    def demand_id(self) -> str:
        return f"P:{self.resource}|{self.node}"

    @property
    def demand_class(self) -> str:
        return CLASS_PHYSICAL

    @property
    def required_delta(self) -> Fraction:
        return self.required


@dataclass(frozen=True)
class EconomicDemand:
    """An external request for a quantity of a resource at a destination."""

    demand_id: str
    resource: str
    quantity: Fraction
    destination: int
    arrival_epoch: int
    arrival_index: int
    status: str = E_PROPOSED

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise Refusal("an economic demand needs a positive quantity")
        if self.status not in (
            E_PROPOSED,
            E_ADMITTED_PENDING,
            E_SERVED,
            E_REJECTED_PHYSICAL_SCARCITY,
            E_REJECTED_INCOMPATIBLE,
        ):
            raise Refusal(f"undeclared economic demand status {self.status!r}")

    @classmethod
    def declare(
        cls,
        world: DemandWorld,
        resource: str,
        quantity,
        node: str,
        arrival_epoch: int,
        arrival_index: int,
    ) -> "EconomicDemand":
        destination = world.index_of(resource, node)
        if world.coordinates[destination].role != "STOCK":
            raise Refusal("an economic demand must be delivered to a stock, not a sink")
        return cls(
            f"E:{arrival_epoch:06d}:{arrival_index:03d}:{resource}|{node}",
            resource,
            exact(quantity, "quantity"),
            destination,
            arrival_epoch,
            arrival_index,
        )

    @property
    def demand_class(self) -> str:
        return CLASS_ECONOMIC

    @property
    def coordinate(self) -> int:
        return self.destination

    @property
    def required_delta(self) -> Fraction:
        return self.quantity

    def with_status(self, status: str) -> "EconomicDemand":
        return EconomicDemand(
            self.demand_id,
            self.resource,
            self.quantity,
            self.destination,
            self.arrival_epoch,
            self.arrival_index,
            status,
        )


Demand = PhysicalDemand | EconomicDemand


def derive_physical_demands(world: DemandWorld, state: Vector) -> tuple[PhysicalDemand, ...]:
    """Read P-demand off the state. No cache, no queue, no memory.

    A coordinate outside `V` has no declared reference, so it has no shortfall
    to speak of and produces no demand. An audit-only loss sink is therefore
    silent here by construction rather than by a special case.
    """
    if len(state) != world.dimension:
        raise Refusal("state dimension does not match the world")
    potential = world.potential
    identity = state_identity(state)
    demands = []
    for index, coordinate in enumerate(world.coordinates):
        shortfall = potential.deficit(state, index)
        if shortfall > 0:
            demands.append(
                PhysicalDemand(
                    index, coordinate.resource, coordinate.node, shortfall, identity
                )
            )
    return tuple(demands)


def completely_serves(demand: Demand, increment: Vector) -> bool:
    """delta_G[c] >= q. The whole service contract, for either demand class."""
    return increment[demand.coordinate] >= demand.required_delta


def coverage(demand: Demand, increment: Vector) -> tuple[Fraction, Fraction]:
    """(required, delivered) at the demand's coordinate."""
    return demand.required_delta, increment[demand.coordinate]


@dataclass(frozen=True)
class ActiveDemandSet:
    """The unordered obligation set `D_t = D_t^P union D_t^E`.

    Unordered is the point. There is no FIFO position, no age, no deadline, no
    priority and no service order anywhere in this object, and nothing
    downstream can recover one, because insertion order is destroyed by the
    canonical sort on demand id.
    """

    physical: tuple[PhysicalDemand, ...]
    economic: tuple[EconomicDemand, ...]

    def __post_init__(self) -> None:
        identifiers = [demand.demand_id for demand in self.all]
        if len(set(identifiers)) != len(identifiers):
            raise Refusal("duplicate demand id in the active set")

    @classmethod
    def of(cls, physical, economic) -> "ActiveDemandSet":
        return cls(
            tuple(sorted(physical, key=lambda d: d.demand_id)),
            tuple(sorted(economic, key=lambda d: d.demand_id)),
        )

    @property
    def all(self) -> tuple[Demand, ...]:
        return tuple(
            sorted(list(self.physical) + list(self.economic), key=lambda d: d.demand_id)
        )

    @property
    def is_empty(self) -> bool:
        return not self.physical and not self.economic

    def by_id(self, demand_id: str) -> Demand:
        for demand in self.all:
            if demand.demand_id == demand_id:
                return demand
        raise Refusal(f"no active demand {demand_id!r}")
