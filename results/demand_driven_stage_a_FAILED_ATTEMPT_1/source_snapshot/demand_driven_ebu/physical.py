"""Physical actions, and the single question "can this plan actually happen now?".

An action moves a declared quantum of one resource along one declared route.
Where the route is lossy the shortfall is deposited in the route's sink, so the
increment of every action sums to exactly zero over all coordinates and no
quantity is created or destroyed anywhere in the model.

Executability is decided **before** any EBU number is computed, and it may read
only physical facts: stocks, routes, capacities, quanta and hard limits. It
cannot read an EBU value, a receipt, a capacity balance, the potential or an
actor preference, and no function in this module is given access to any of
them. A plan that cannot happen is removed, never valued and then repaired,
clipped or rescaled into one that can.

Simultaneity is source-funded. Every coordinate must already hold, at the
frozen pre-action baseline, the total quantity it sends in the plan. A stock
may not fund an outflow with quantity arriving in the same instant from another
action of the same plan. Endpoint nonnegativity alone would be weaker, because
it silently permits exactly that unspecified intermediate physics.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from gaussian_harness.numerics import Refusal, Vector, exact

from .world import DemandWorld, Route

EXECUTABILITY_RULE_ID = "EBU-DEMAND-EXECUTABILITY-SOURCE-FUNDED-v1"

REASON_EXECUTABLE = "EXECUTABLE"
REASON_DUPLICATE_ROUTE = "DUPLICATE_ROUTE_IN_PLAN"
REASON_UNDECLARED_QUANTUM = "UNDECLARED_QUANTUM"
REASON_ROUTE_CAPACITY = "ROUTE_CAPACITY_EXCEEDED"
REASON_SOURCE_STOCK = "SOURCE_STOCK_INSUFFICIENT"
REASON_ENDPOINT_NEGATIVE = "ENDPOINT_STOCK_NEGATIVE"
REASON_STOCK_CAPACITY = "ENDPOINT_EXCEEDS_STOCK_CAPACITY"
REASON_CONSERVATION = "CONSERVATION_DOES_NOT_CLOSE"


@dataclass(frozen=True, order=True)
class PhysicalAction:
    """One quantum of one resource moved along one route, loss included."""

    route: Route
    quantity: Fraction

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise Refusal("action quantity must be positive")

    @classmethod
    def declare(cls, route: Route, quantity) -> "PhysicalAction":
        return cls(route, exact(quantity, "quantity"))

    @property
    def action_id(self) -> str:
        return f"{self.route.route_id}@{self.quantity.numerator}/{self.quantity.denominator}"

    @property
    def delivered(self) -> Fraction:
        """What actually arrives at the destination after loss."""
        return self.quantity * self.route.efficiency

    @property
    def lost(self) -> Fraction:
        return self.quantity - self.delivered

    def owner(self, world: DemandWorld) -> str:
        return world.owner_of(self.route.source)

    def increment(self, dimension: int) -> Vector:
        values = [Fraction(0)] * dimension
        values[self.route.source] -= self.quantity
        values[self.route.destination] += self.delivered
        if self.route.sink is not None:
            values[self.route.sink] += self.lost
        return tuple(values)

    @property
    def support(self) -> frozenset[int]:
        touched = {self.route.source, self.route.destination}
        if self.route.sink is not None:
            touched.add(self.route.sink)
        return frozenset(touched)


@dataclass(frozen=True)
class PlanGroup:
    """An immutable simultaneous set of actions valued from one baseline.

    Membership is not net change: a nonempty group whose increments cancel
    still has every member's coordinate in its support, and is still a group.
    """

    actions: tuple[PhysicalAction, ...]

    def __post_init__(self) -> None:
        identifiers = [action.action_id for action in self.actions]
        if list(identifiers) != sorted(identifiers):
            raise Refusal("plan actions must be in canonical order")
        routes = [action.route.route_id for action in self.actions]
        if len(set(routes)) != len(routes):
            raise Refusal("a plan may use each route at most once")

    @classmethod
    def of(cls, *actions: PhysicalAction) -> "PlanGroup":
        return cls(tuple(sorted(actions, key=lambda a: a.action_id)))

    @property
    def is_empty(self) -> bool:
        return not self.actions

    @property
    def size(self) -> int:
        return len(self.actions)

    @property
    def group_id(self) -> str:
        return "g:[" + ",".join(action.action_id for action in self.actions) + "]"

    def increment(self, dimension: int) -> Vector:
        values = [Fraction(0)] * dimension
        for action in self.actions:
            values[action.route.source] -= action.quantity
            values[action.route.destination] += action.delivered
            if action.route.sink is not None:
                values[action.route.sink] += action.lost
        return tuple(values)

    @property
    def support(self) -> frozenset[int]:
        touched: set[int] = set()
        for action in self.actions:
            touched |= action.support
        return frozenset(touched)

    @property
    def route_support(self) -> frozenset[str]:
        return frozenset(action.route.route_id for action in self.actions)

    def owner_support(self, world: DemandWorld) -> frozenset[str]:
        return frozenset(action.owner(world) for action in self.actions)

    def subsets_without(self, action: PhysicalAction) -> "PlanGroup":
        return PlanGroup(tuple(a for a in self.actions if a != action))


@dataclass(frozen=True)
class ExecutabilityVerdict:
    executable: bool
    reason: str
    offending: tuple[str, ...] = ()


def can_happen_now(world: DemandWorld, state: Vector, plan: PlanGroup) -> ExecutabilityVerdict:
    """Decide whether this exact plan can physically execute in this state.

    The plan checked here is the plan that later executes. Nothing is proposed,
    valued, and then resolved into something else.
    """
    if plan.is_empty:
        return ExecutabilityVerdict(True, REASON_EXECUTABLE)
    if len(state) != world.dimension:
        raise Refusal("state dimension does not match the world")

    for action in plan.actions:
        if action.route not in world.routes:
            raise Refusal(f"{action.route.route_id} is not a declared route of this world")
        if action.quantity not in world.quanta:
            return ExecutabilityVerdict(False, REASON_UNDECLARED_QUANTUM, (action.action_id,))
        if action.quantity > action.route.capacity:
            return ExecutabilityVerdict(False, REASON_ROUTE_CAPACITY, (action.action_id,))

    outflow: dict[int, Fraction] = {}
    for action in plan.actions:
        source = action.route.source
        outflow[source] = outflow.get(source, Fraction(0)) + action.quantity
    short = tuple(
        world.coordinates[index].key
        for index in sorted(outflow)
        if outflow[index] > state[index]
    )
    if short:
        return ExecutabilityVerdict(False, REASON_SOURCE_STOCK, short)

    increment = plan.increment(world.dimension)
    negative = tuple(
        world.coordinates[index].key
        for index, delta in enumerate(increment)
        if state[index] + delta < 0
    )
    if negative:
        return ExecutabilityVerdict(False, REASON_ENDPOINT_NEGATIVE, negative)

    over = tuple(
        world.coordinates[index].key
        for index, delta in enumerate(increment)
        if world.coordinates[index].capacity is not None
        and state[index] + delta > world.coordinates[index].capacity
    )
    if over:
        return ExecutabilityVerdict(False, REASON_STOCK_CAPACITY, over)

    for resource in world.resources:
        total = Fraction(0)
        for index, coordinate in enumerate(world.coordinates):
            if coordinate.resource == resource:
                total += increment[index]
        if total != 0:
            return ExecutabilityVerdict(False, REASON_CONSERVATION, (resource,))

    return ExecutabilityVerdict(True, REASON_EXECUTABLE)


def action_alphabet(world: DemandWorld, routes: tuple[Route, ...] | None = None) -> tuple[PhysicalAction, ...]:
    """Every declared (route, quantum) pair, in canonical order.

    This is the complete physical vocabulary of the world. It is never the
    actor's menu: contract section 39 requires the menu to be empty when no
    demand is active, and the alphabet is filtered down to demand-serving
    plans before any actor sees it.
    """
    chosen = world.routes if routes is None else routes
    actions = [
        PhysicalAction(route, quantum)
        for route in chosen
        for quantum in world.quanta
        if quantum <= route.capacity
    ]
    return tuple(sorted(actions, key=lambda a: a.action_id))
