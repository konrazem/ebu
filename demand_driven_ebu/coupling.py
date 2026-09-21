"""The demand-dependency graph and its joint-resolution components.

Not every demand interacts physically with every other one. Two demands are
connected when serving them could compete for, or share, the same physical
stock, the same route, the same hard capacity, or the same actor account. The
connected components of that graph are the units that are resolved jointly, and
independent components may resolve in the same epoch: one impossible sand
demand must not block an unrelated water restoration.

The footprint of a demand is computed conservatively, as everything any plan
serving it could possibly touch, rather than as the exact set some particular
plan does touch. Over-coupling is the safe direction of error. It can only merge
components that were in fact independent, which costs parallelism; under-coupling
would let two "independent" plans collide at execution, which costs correctness.
The final joint gate in `harness` re-checks the merged plan anyway and reports
any surviving collision as an implementation defect rather than sequencing
around it quietly.

Account sharing is a real edge here, not a formality. Because accounts are held
by nodes, a sand demand and a water demand whose plans would both be paid for
by node `A` are coupled through joint affordability even though no stock and no
route is shared.
"""

from __future__ import annotations

from dataclasses import dataclass

from gaussian_harness.numerics import Refusal

from .demand import ActiveDemandSet, Demand
from .world import DemandWorld


@dataclass(frozen=True)
class Footprint:
    """Everything a plan serving one demand could possibly touch."""

    coordinates: frozenset[int]
    routes: frozenset[str]
    owners: frozenset[str]

    def intersects(self, other: "Footprint") -> bool:
        return bool(
            self.coordinates & other.coordinates
            or self.routes & other.routes
            or self.owners & other.owners
        )


def footprint(world: DemandWorld, demand: Demand) -> Footprint:
    reachable = world.transport_component(demand.coordinate)
    routes = frozenset(
        route.route_id
        for route in world.routes
        if route.source in reachable or route.destination in reachable
    )
    owners = frozenset(
        world.owner_of(route.source)
        for route in world.routes
        if route.route_id in routes
    )
    owners |= {world.coordinates[demand.coordinate].node}
    return Footprint(reachable, routes, owners)


@dataclass(frozen=True)
class DemandComponent:
    """A coupled set of active demands, resolved jointly or not at all."""

    demands: tuple[Demand, ...]
    reach: Footprint

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


def components(world: DemandWorld, active: ActiveDemandSet) -> tuple[DemandComponent, ...]:
    """Connected components of the demand-dependency graph, canonically ordered."""
    demands = active.all
    if not demands:
        return ()
    prints = [footprint(world, demand) for demand in demands]

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
            if prints[i].intersects(prints[j]):
                union(i, j)

    grouped: dict[int, list[int]] = {}
    for index in range(len(demands)):
        grouped.setdefault(find(index), []).append(index)

    built = []
    for members in grouped.values():
        merged = Footprint(
            frozenset().union(*(prints[i].coordinates for i in members)),
            frozenset().union(*(prints[i].routes for i in members)),
            frozenset().union(*(prints[i].owners for i in members)),
        )
        built.append(
            DemandComponent(
                tuple(sorted((demands[i] for i in members), key=lambda d: d.demand_id)),
                merged,
            )
        )
    return tuple(sorted(built, key=lambda c: c.component_id))
