"""The demand-dependency graph, and the invariant it must respect.

**Invariant (unusable-infrastructure invariance).** If a world modification
does not change the set of physically executable actions, nor any genuine
binding physical or account constraint, it must not change demand coupling,
complete-service possibilities, or admission. In particular, adding or
removing a route that cannot carry any allowed action quantity must be
behaviorally invisible.

**Invariant (decomposition).** Demand decomposition is an implementation
factorization, not a restriction on the global feasible service set. Splitting
demands into components, or evaluating them jointly, must produce the same
executable outcomes.

Incorrect coupling is scientifically material, not merely a cost in
parallelism. Wherever complete-service, search-size, simultaneity or other
joint constraints exist, merging demands that do not interact can destroy
serviceability outright: a component must be served in full or not at all, so
one unserviceable member takes the rest down with it.

## What coupling is derived from

Not transport connectivity, and not enumerated plans. Two earlier bases both
failed:

* Membership of a shared transport component merged demands that never
  compete.
* Enumerated *serving* plans include padded ones -- plans carrying actions
  unnecessary to the demand -- and those actions dragged unrelated coordinates
  and owners into the reach. Combined with a generous search set, two
  physically unusable routes were enough to merge three independent deliveries
  and destroy all service, while leaving the executable action set identical.

Coupling is therefore derived from the **structural reach**: the exact set of
tokens any *minimal* plan serving a demand could bind, computed from the world
in `enumeration.structural_reach`, which is proved there to be a sound
superset of every minimal plan's support. It is free of the plan-size cap,
free of padding, and blind to routes that can carry no action.

Two demands are coupled when their service possibilities genuinely interact
through:

* a shared **service-delivery pool** -- the same destination coordinate, where
  economic quantities are additive;
* **competing stock** -- a coordinate that plans for both could draw on;
* a **shared executable route**, and therefore its hard capacity;
* a **shared hard physical constraint** or shared potential-bearing
  coordinate, where valuation is not additive;
* **one executable action serving several demands**, which shows up as a
  shared route and destination;
* a **shared owner account**, where joint settlement genuinely binds -- joint
  affordability is checked jointly at execution, so decoupling such demands
  would let the joint gate discover a conflict it should have prevented.

A demand whose structural reach contains no usable delivering route couples
with nothing but demands at its own coordinate. That is sound: it has no
minimal plan, and a joint plan cannot rescue it, since a joint plan has no
more actions available to it under the same limit.
"""

from __future__ import annotations

from dataclasses import dataclass

from gaussian_harness.numerics import Refusal, Vector

from .demand import ActiveDemandSet, Demand
from .enumeration import (
    IMPOSSIBLE,
    SERVICEABLE,
    UNRESOLVED,
    physically_serviceable,
    search_routes,
    structural_reach,
)
from .service import CoordinateRequirement, requirements
from .world import DemandWorld


@dataclass(frozen=True)
class Reach:
    """Tokens any minimal plan serving one demand could bind.

    `verdict` records which of the three serviceability answers produced this
    reach, so an audit can tell a reach that is empty because the demand is
    *proved* impossible from one that is full because the search could not
    decide.
    """

    coordinates: frozenset[int]
    routes: frozenset[str]
    owners: frozenset[str]
    destination: int
    verdict: str = SERVICEABLE

    def interacts_with(self, other: "Reach") -> bool:
        if self.destination == other.destination:
            return True
        if self.coordinates & other.coordinates:
            return True
        if self.routes & other.routes:
            return True
        return bool(self.owners & other.owners)


def service_reach(world: DemandWorld, state: Vector, demand: Demand) -> Reach:
    """The structural reach of one demand, gated on it being serviceable at all.

    A demand **proved** to have no physically realizable service possibility
    binds nothing. There are no service possibilities for anything to interact
    with, so it competes for no stock, no route and no account, and it is
    reduced to its own destination coordinate.

    A demand whose serviceability the search could not decide keeps its **full**
    reach. Uncertainty is not evidence of impossibility, and decoupling on it
    would delete real dependencies because a search ran out of budget.

    That is sound rather than merely convenient. If no plan serves `d` alone,
    no joint plan serves it either: the actions of a joint plan that raise the
    increment at `d`'s coordinate would themselves serve `d`, and they are
    drawn from the same structural reach, which already includes any
    capacity-relief route. So an unserviceable demand cannot be rescued by
    company, and coupling it to a serviceable neighbour would destroy that
    neighbour's service for nothing -- the very artifact this module exists to
    prevent.

    Its destination is still recorded, so two economic orders at one
    coordinate stay coupled by their additive requirement even when neither is
    serviceable alone; but its *coordinate set* is empty, so a serviceable
    neighbour that merely draws supply from the unserviceable demand's
    destination is not dragged in. That asymmetry costs nothing: the
    neighbour's plan can only make an already-impossible demand no more
    impossible, and there is no state in which coupling them would have
    rescued it.

    The serviceability test is uncapped and reads only usable routes, so the
    gate inherits both invariants: it cannot move with the plan-size cap, and
    it cannot move when a route that carries no action is added or removed.
    """
    verdict = physically_serviceable(world, state, requirements((demand,)))
    if verdict == IMPOSSIBLE:
        return Reach(
            frozenset(), frozenset(), frozenset(), demand.coordinate, IMPOSSIBLE
        )
    # SERVICEABLE and UNRESOLVED both take the full reach. Emptying it is an
    # optimization licensed only by *proved* impossibility; doing it on an
    # undecided search would silently delete real dependencies on the strength
    # of a computational limit.
    reach = structural_reach(world, state, frozenset({demand.coordinate}))
    return Reach(
        reach.coordinates, reach.routes, reach.owners, demand.coordinate, verdict
    )


@dataclass(frozen=True)
class DemandComponent:
    """A coupled set of demands, resolved jointly or not at all."""

    demands: tuple[Demand, ...]
    binding: Reach
    search: frozenset[str]

    def __post_init__(self) -> None:
        if not self.demands:
            raise Refusal("a demand component must contain at least one demand")
        identifiers = [demand.demand_id for demand in self.demands]
        if list(identifiers) != sorted(identifiers):
            raise Refusal("component demands must be in canonical order")

    @property
    def component_id(self) -> str:
        return "c:[" + ",".join(demand.demand_id for demand in self.demands) + "]"

    @property
    def demand_ids(self) -> tuple[str, ...]:
        return tuple(demand.demand_id for demand in self.demands)

    @property
    def economic_ids(self) -> tuple[str, ...]:
        return tuple(
            demand.demand_id for demand in self.demands if demand.demand_class == "E"
        )

    @property
    def requirements(self) -> tuple[CoordinateRequirement, ...]:
        return requirements(self.demands)


def components(
    world: DemandWorld, state: Vector, active: ActiveDemandSet
) -> tuple[DemandComponent, ...]:
    """Connected components of the binding-constraint graph."""
    demands = active.all
    if not demands:
        return ()
    reaches = [service_reach(world, state, demand) for demand in demands]

    parent = list(range(len(demands)))

    def find(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    def union(left: int, right: int) -> None:
        a, b = find(left), find(right)
        if a != b:
            parent[max(a, b)] = min(a, b)

    for i in range(len(demands)):
        for j in range(i + 1, len(demands)):
            if reaches[i].interacts_with(reaches[j]):
                union(i, j)

    grouped: dict[int, list[int]] = {}
    for index in range(len(demands)):
        grouped.setdefault(find(index), []).append(index)

    built = []
    for members in grouped.values():
        verdicts = {reaches[i].verdict for i in members}
        merged = Reach(
            frozenset().union(*(reaches[i].coordinates for i in members)),
            frozenset().union(*(reaches[i].routes for i in members)),
            frozenset().union(*(reaches[i].owners for i in members)),
            min(reaches[i].destination for i in members),
            UNRESOLVED if UNRESOLVED in verdicts
            else (SERVICEABLE if SERVICEABLE in verdicts else IMPOSSIBLE),
        )
        member_demands = tuple(
            sorted((demands[i] for i in members), key=lambda d: d.demand_id)
        )
        search = frozenset(
            route.route_id
            for route in search_routes(
                world, frozenset(demand.coordinate for demand in member_demands)
            )
        )
        built.append(DemandComponent(member_demands, merged, search))
    return tuple(sorted(built, key=lambda c: c.component_id))
