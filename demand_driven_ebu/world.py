"""The physical world: coordinates, routes, quanta and transport components.

A coordinate is one homogeneous stock of one resource at one node. Resources do
not convert into one another, so every physical movement stays inside a single
resource and the flat state vector is a product of per-resource sub-worlds.

Accounts are held by **nodes**, not by coordinates. A node that moves its sand
and a node that moves its water spend the same capacity balance. Contract
section 9 lists shared account capacity as a genuine coupling channel between
demands, and node-held accounts are what make that channel real; per-coordinate
wallets would have quietly removed it.

Routes carry a declared hard capacity and a declared efficiency. Efficiency
below one is irreversible loss, and a lossy route must name the sink coordinate
that receives the difference, so that no physical quantity ever disappears into
nowhere and the increment of every action sums to exactly zero.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable

from gaussian_harness.numerics import Refusal, Vector, exact

from .potential import DemandPotential

ROLE_STOCK = "STOCK"
ROLE_SINK = "SINK"
DECLARED_ROLES = (ROLE_STOCK, ROLE_SINK)


@dataclass(frozen=True)
class Coordinate:
    """One stock of one resource at one node."""

    resource: str
    node: str
    role: str = ROLE_STOCK
    reference: Fraction | None = None
    scale: Fraction | None = None
    capacity: Fraction | None = None

    def __post_init__(self) -> None:
        if self.role not in DECLARED_ROLES:
            raise Refusal(f"undeclared coordinate role {self.role!r}")
        if not self.resource or not self.node:
            raise Refusal("coordinate needs a resource and a node")
        if "|" in self.resource or "|" in self.node:
            raise Refusal("resource and node names must not contain '|'")
        if (self.reference is None) != (self.scale is None):
            raise Refusal("declare both reference and scale, or neither")
        if self.capacity is not None and self.capacity <= 0:
            raise Refusal("a declared stock capacity must be positive")

    @classmethod
    def stock(cls, resource: str, node: str, reference, scale, capacity=None) -> "Coordinate":
        return cls(
            resource,
            node,
            ROLE_STOCK,
            exact(reference, "reference"),
            exact(scale, "scale"),
            None if capacity is None else exact(capacity, "capacity"),
        )

    @classmethod
    def sink_in_potential(cls, resource: str, node: str, reference, scale) -> "Coordinate":
        return cls(resource, node, ROLE_SINK, exact(reference, "reference"), exact(scale, "scale"))

    @classmethod
    def sink_audit_only(cls, resource: str, node: str) -> "Coordinate":
        """A boundary ledger entry that closes conservation and nothing else.

        It is outside `V`, so it has no deviation to restore and generates no
        physical demand. Pretending otherwise is exactly what contract section
        23 forbids.
        """
        return cls(resource, node, ROLE_SINK, None, None)

    @property
    def key(self) -> str:
        return f"{self.resource}|{self.node}"

    @property
    def carries_potential(self) -> bool:
        return self.reference is not None


@dataclass(frozen=True)
class Route:
    """A directed physical channel for one resource, with capacity and loss."""

    resource: str
    source: int
    destination: int
    capacity: Fraction
    efficiency: Fraction = Fraction(1)
    sink: int | None = None

    def __post_init__(self) -> None:
        if self.source == self.destination:
            raise Refusal("a route must connect two different coordinates")
        if self.capacity <= 0:
            raise Refusal("route capacity must be positive")
        if not 0 < self.efficiency <= 1:
            raise Refusal("route efficiency must lie in (0, 1]")
        if self.efficiency < 1 and self.sink is None:
            raise Refusal("a lossy route must declare the sink that receives the loss")
        if self.efficiency == 1 and self.sink is not None:
            raise Refusal("a lossless route must not declare a sink")

    @classmethod
    def declare(
        cls,
        resource: str,
        source: int,
        destination: int,
        capacity,
        efficiency=Fraction(1),
        sink: int | None = None,
    ) -> "Route":
        return cls(
            resource,
            source,
            destination,
            exact(capacity, "capacity"),
            exact(efficiency, "efficiency"),
            sink,
        )

    @property
    def route_id(self) -> str:
        return f"r:{self.resource}:{self.source}->{self.destination}"

    @property
    def lossless(self) -> bool:
        return self.efficiency == 1


@dataclass(frozen=True)
class DemandWorld:
    """A complete declared physical world. Immutable; carries no state."""

    world_id: str
    coordinates: tuple[Coordinate, ...]
    routes: tuple[Route, ...]
    quanta: tuple[Fraction, ...]
    max_plan_size: int

    def __post_init__(self) -> None:
        if not self.coordinates:
            raise Refusal("a world needs at least one coordinate")
        keys = [coordinate.key for coordinate in self.coordinates]
        if len(set(keys)) != len(keys):
            raise Refusal("duplicate (resource, node) coordinate")
        if list(keys) != sorted(keys):
            raise Refusal("coordinates must be in canonical (resource, node) order")
        if not self.quanta:
            raise Refusal("a world needs at least one declared transfer quantum")
        if any(quantum <= 0 for quantum in self.quanta):
            raise Refusal("every declared quantum must be positive")
        if tuple(sorted(self.quanta)) != self.quanta or len(set(self.quanta)) != len(self.quanta):
            raise Refusal("quanta must be distinct and in ascending order")
        if self.max_plan_size <= 0:
            raise Refusal("max plan size must be positive")
        seen: set[tuple[int, int]] = set()
        for route in self.routes:
            for index in (route.source, route.destination):
                if not 0 <= index < len(self.coordinates):
                    raise Refusal(f"route endpoint {index} leaves the world")
                if self.coordinates[index].resource != route.resource:
                    raise Refusal(f"{route.route_id} crosses resources at coordinate {index}")
            if self.coordinates[route.destination].role == ROLE_SINK:
                raise Refusal(f"{route.route_id} delivers into a sink; declare it as loss")
            if route.sink is not None:
                if not 0 <= route.sink < len(self.coordinates):
                    raise Refusal("route sink leaves the world")
                if self.coordinates[route.sink].role != ROLE_SINK:
                    raise Refusal("route loss must be received by a SINK coordinate")
                if self.coordinates[route.sink].resource != route.resource:
                    raise Refusal("route loss must stay within its own resource")
            pair = (route.source, route.destination)
            if pair in seen:
                raise Refusal(f"duplicate route {route.route_id}")
            seen.add(pair)
        if tuple(sorted(self.routes, key=lambda r: (r.resource, r.source, r.destination))) != self.routes:
            raise Refusal("routes must be in canonical order")

    @classmethod
    def declare(
        cls,
        world_id: str,
        coordinates: Iterable[Coordinate],
        routes: Iterable[Route],
        quanta: Iterable,
        max_plan_size: int,
    ) -> "DemandWorld":
        ordered_coordinates = tuple(sorted(coordinates, key=lambda c: c.key))
        ordered_routes = tuple(
            sorted(routes, key=lambda r: (r.resource, r.source, r.destination))
        )
        ordered_quanta = tuple(sorted({exact(q, "quantum") for q in quanta}))
        return cls(world_id, ordered_coordinates, ordered_routes, ordered_quanta, max_plan_size)

    @property
    def dimension(self) -> int:
        return len(self.coordinates)

    @property
    def nodes(self) -> tuple[str, ...]:
        return tuple(sorted({coordinate.node for coordinate in self.coordinates}))

    @property
    def resources(self) -> tuple[str, ...]:
        return tuple(sorted({coordinate.resource for coordinate in self.coordinates}))

    def node_index(self, node: str) -> int:
        nodes = self.nodes
        if node not in nodes:
            raise Refusal(f"undeclared node {node!r}")
        return nodes.index(node)

    def index_of(self, resource: str, node: str) -> int:
        key = f"{resource}|{node}"
        for index, coordinate in enumerate(self.coordinates):
            if coordinate.key == key:
                return index
        raise Refusal(f"undeclared coordinate {key!r}")

    def owner_of(self, coordinate_index: int) -> str:
        """owner(a) = the node holding the stock the action moves."""
        return self.coordinates[coordinate_index].node

    @property
    def potential(self) -> DemandPotential:
        return DemandPotential(
            tuple(coordinate.reference for coordinate in self.coordinates),
            tuple(coordinate.scale for coordinate in self.coordinates),
        )

    @property
    def route_by_id(self) -> dict[str, Route]:
        return {route.route_id: route for route in self.routes}

    def routes_from(self, coordinate_index: int) -> tuple[Route, ...]:
        return tuple(route for route in self.routes if route.source == coordinate_index)

    def transport_component(self, coordinate_index: int) -> frozenset[int]:
        """Coordinates weakly reachable from `coordinate_index` by routes.

        Direction is ignored deliberately. A deficit can be supplied from any
        coordinate that can reach it, and a surplus can be drained to any
        coordinate reachable from it, so the set of coordinates a plan serving
        a demand here could possibly touch is the *undirected* component, not
        the forward cone. Over-reaching is the safe error: it can only merge
        demands that were already independent, never split ones that are not.
        """
        if not 0 <= coordinate_index < self.dimension:
            raise Refusal(f"coordinate {coordinate_index} out of range")
        reached = {coordinate_index}
        frontier = [coordinate_index]
        while frontier:
            current = frontier.pop()
            for route in self.routes:
                neighbours = [route.source, route.destination]
                if route.sink is not None:
                    neighbours.append(route.sink)
                if current not in neighbours:
                    continue
                for neighbour in neighbours:
                    if neighbour not in reached:
                        reached.add(neighbour)
                        frontier.append(neighbour)
        return frozenset(reached)

    def resource_total(self, state: Vector, resource: str) -> Fraction:
        result = Fraction(0)
        for index, coordinate in enumerate(self.coordinates):
            if coordinate.resource == resource:
                result += state[index]
        return result

    def reference_state(self) -> Vector:
        """x* on valued coordinates, and zero on audit-only ones."""
        return tuple(
            coordinate.reference if coordinate.reference is not None else Fraction(0)
            for coordinate in self.coordinates
        )
