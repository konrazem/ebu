"""The demand-dependency graph, and the invariant it must respect.

**Invariant.** Demand decomposition is an implementation factorization, not a
restriction on the global feasible service set. Splitting demands into
components, or evaluating them jointly, must produce the same set of globally
executable outcomes. Over-coupling is therefore not a harmless conservatism:
merging two demands that never interact makes an unserviceable one freeze a
serviceable one, and that freeze is an artifact of the partition rather than a
physical fact.

Coupling is consequently decided from **actual binding constraints**, not from
membership of a shared transport component. Two demands are coupled when their
service possibilities genuinely interact through one of:

* a shared service-delivery pool — the same destination coordinate, where
  economic quantities are additive;
* competing stock — a source coordinate that plans for both could draw on;
* a shared route, and therefore its hard capacity;
* a shared potential-bearing coordinate, where valuation would not be additive;
* a shared owner account, where joint affordability genuinely binds.

The first four are all visible as an overlap of the **touched coordinates** of
the two demands' individually-serving plans, since a plan touches its sources,
its destination and its sinks. The fifth is separate, because accounts are held
by nodes and a node may host several resources.

A demand with no individually-serving plan has an empty reach and couples with
nothing. That is correct rather than convenient: a demand that cannot be served
alone cannot be served inside a larger plan either, because a joint plan has
*fewer* actions available for it under the same plan-size cap, so it competes
for nothing. It becomes a singleton component and is reported unserviceable
without freezing anything.

The one exception is a shared destination: economic orders at the same
coordinate draw on the same pool and are coupled even when neither is
individually serviceable, because their requirement is additive and only
meaningful jointly.
"""

from __future__ import annotations

from dataclasses import dataclass

from gaussian_harness.numerics import Refusal, Vector

from .demand import ActiveDemandSet, Demand
from .enumeration import search_routes, serving_groups
from .service import CoordinateRequirement, requirements
from .world import DemandWorld


@dataclass(frozen=True)
class Reach:
    """Tokens any plan serving one demand alone could actually bind."""

    coordinates: frozenset[int]
    routes: frozenset[str]
    owners: frozenset[str]
    destination: int
    serviceable: bool

    def interacts_with(self, other: "Reach") -> bool:
        if self.destination == other.destination:
            return True
        if self.coordinates & other.coordinates:
            return True
        if self.routes & other.routes:
            return True
        return bool(self.owners & other.owners)


def service_reach(world: DemandWorld, state: Vector, demand: Demand) -> Reach:
    """What a plan serving this demand *on its own* could touch, exactly."""
    reqs = requirements((demand,))
    routes = search_routes(world, frozenset({demand.coordinate}))
    groups = serving_groups(world, state, reqs, routes)
    coordinates: set[int] = set()
    used: set[str] = set()
    owners: set[str] = set()
    for group in groups:
        coordinates |= group.support
        used |= group.route_support
        owners |= group.owner_support(world)
    return Reach(
        frozenset(coordinates), frozenset(used), frozenset(owners), demand.coordinate, bool(groups)
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
        merged = Reach(
            frozenset().union(*(reaches[i].coordinates for i in members)),
            frozenset().union(*(reaches[i].routes for i in members)),
            frozenset().union(*(reaches[i].owners for i in members)),
            min(reaches[i].destination for i in members),
            any(reaches[i].serviceable for i in members),
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
