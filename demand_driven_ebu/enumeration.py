"""Plan enumeration primitives, and the structural reach coupling is built on.

Kept separate from `coupling` and `plans` so the dependency graph stays
acyclic, and because the two use enumeration for different purposes with
different soundness requirements.

## Three route sets, deliberately different

* The **structural reach** is what decides coupling. It is the exact set of
  tokens any *minimal* plan serving a requirement could bind, derived from the
  world rather than from enumerated plans. It is free of the plan-size cap and
  free of padding, and a route that can carry no allowed action quantity is
  invisible to it.
* The **search routes** are generous: every route touching the transport
  closure of a component's coordinates. Breadth here is safe in the only
  direction that matters -- it can offer more valid plans, never delete one --
  so menus are built over this set.
* **Usable routes** are those that can carry at least one declared quantum. A
  route with capacity below every quantum carries no action and must be
  behaviorally invisible.

## Why the structural reach is exact

Let `G` be an irredundant executable plan serving requirement set `R`, and take
`a` in `G`. Irredundancy says `G \\ {a}` either fails to serve `R` or cannot
execute.

*If it fails to serve `R`*, some coordinate `c` of `R` has
`delta_{G\\a}[c] < req(c)` while `delta_G[c] >= req(c)`, so `a` raises the
increment at `c`: `a` **delivers into a requirement coordinate**, either as its
destination or as its loss sink.

*If it cannot execute*, the broken condition can only be the stock capacity at
`a`'s source. Quantum and route-capacity checks are per action and unaffected
by removal; source-funding only relaxes when an outflow is removed; and
endpoint nonnegativity cannot break, because source-funding on `G` gives
`state[i] + delta_S[i] >= state[i] - outflow_G[i] >= 0` for every subset `S`.
Removing `a` removes an outflow from its source, which can only push that
coordinate *up*, so the sole exposure is a declared stock capacity there.

So every action of every minimal plan either delivers into a requirement
coordinate or drains a capacity-bearing coordinate that receives inflow inside
the plan. `structural_reach` closes over exactly those two cases, which makes
it a sound superset of every minimal plan's support and cheap to compute. In a
world declaring no stock capacities the second case is empty and the reach is
one pass.

## The plan-size cap

`world.max_plan_size` is a **computational enumeration limit**, not a physical
simultaneity constraint. See `DEMAND_DRIVEN_PLAN_CAP_DISPOSITION.md`. It
therefore may not decide physical possibility, and nothing here uses it to:
`physically_serviceable` searches without it, by choosing at most one action
per usable reach route, which is exact because minimal plans use only those
routes.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations, product

from gaussian_harness.numerics import Refusal, Vector

from .physical import PhysicalAction, PlanGroup, action_alphabet, can_happen_now
from .service import CoordinateRequirement, serves_all
from .world import DemandWorld, Route

# An exhaustive per-route search is bounded by the product over reach routes of
# (1 + usable quanta). Beyond this many combinations the search refuses rather
# than reporting a negative it did not establish.
EXHAUSTIVE_BUDGET = 500_000


def usable_routes(world: DemandWorld) -> tuple[Route, ...]:
    """Routes that can carry at least one declared quantum.

    A route whose capacity is below every quantum carries no action. It must be
    behaviorally invisible: it may not change coupling, serviceability or
    admission, because it cannot change the executable action set.
    """
    return tuple(
        route
        for route in world.routes
        if any(quantum <= route.capacity for quantum in world.quanta)
    )


def search_routes(world: DemandWorld, coordinates: frozenset[int]) -> tuple[Route, ...]:
    """Every route touching the transport closure of these coordinates."""
    closure: set[int] = set()
    for coordinate in coordinates:
        closure |= world.transport_component(coordinate)
    return tuple(
        route
        for route in world.routes
        if route.source in closure or route.destination in closure
    )


@dataclass(frozen=True)
class StructuralReach:
    coordinates: frozenset[int]
    routes: frozenset[str]
    owners: frozenset[str]


def structural_reach(
    world: DemandWorld, requirement_coordinates: frozenset[int]
) -> StructuralReach:
    """Tokens every minimal plan serving this requirement set could bind."""
    usable = usable_routes(world)
    inflow_targets = set(requirement_coordinates)
    selected: dict[str, Route] = {}
    while True:
        grew = False
        for route in usable:
            if route.route_id in selected:
                continue
            delivers = route.destination in inflow_targets or (
                route.sink is not None and route.sink in inflow_targets
            )
            relieves = (
                route.source in inflow_targets
                and world.coordinates[route.source].capacity is not None
            )
            if delivers or relieves:
                selected[route.route_id] = route
                grew = True
        added = set()
        for route in selected.values():
            added.add(route.destination)
            if route.sink is not None:
                added.add(route.sink)
        if not added <= inflow_targets:
            inflow_targets |= added
            grew = True
        if not grew:
            break

    coordinates = set(requirement_coordinates)
    for route in selected.values():
        coordinates.add(route.source)
        coordinates.add(route.destination)
        if route.sink is not None:
            coordinates.add(route.sink)
    return StructuralReach(
        frozenset(coordinates),
        frozenset(selected),
        frozenset(world.owner_of(route.source) for route in selected.values()),
    )


def _capped_groups(world: DemandWorld, routes, limit: int):
    alphabet = action_alphabet(world, routes)
    for size in range(1, limit + 1):
        for chosen in combinations(alphabet, size):
            if len({action.route.route_id for action in chosen}) != size:
                continue
            yield PlanGroup.of(*chosen)


def exhaustive_space(world: DemandWorld, routes) -> int:
    """Size of the uncapped per-route search over these routes."""
    total = 1
    for route in routes:
        total *= 1 + sum(1 for quantum in world.quanta if quantum <= route.capacity)
        if total > EXHAUSTIVE_BUDGET:
            return total
    return total


def _uncapped_groups(world: DemandWorld, routes):
    """Every plan using at most one action per route, at any size."""
    choices = []
    for route in routes:
        options = [None] + [
            PhysicalAction(route, quantum)
            for quantum in world.quanta
            if quantum <= route.capacity
        ]
        choices.append(options)
    for combination in product(*choices):
        chosen = tuple(action for action in combination if action is not None)
        if chosen:
            yield PlanGroup.of(*chosen)


def serving_groups(
    world: DemandWorld,
    state: Vector,
    reqs: tuple[CoordinateRequirement, ...],
    routes,
) -> tuple[PlanGroup, ...]:
    """Complete, executable plans over the given routes, within the cap."""
    return tuple(
        group
        for group in _capped_groups(world, routes, world.max_plan_size)
        if serves_all(reqs, group.increment(world.dimension))
        and can_happen_now(world, state, group).executable
    )


def has_serving_group(
    world: DemandWorld,
    state: Vector,
    reqs: tuple[CoordinateRequirement, ...],
    routes,
) -> bool:
    """Early-exit existence test within the cap.

    Irredundancy is not checked: if any complete executable plan exists then a
    minimal such subset of it is itself complete and executable, so an
    irredundant one exists too.
    """
    for group in _capped_groups(world, routes, world.max_plan_size):
        if not serves_all(reqs, group.increment(world.dimension)):
            continue
        if can_happen_now(world, state, group).executable:
            return True
    return False


SERVICEABLE = "PHYSICALLY_SERVICEABLE"
IMPOSSIBLE = "PHYSICALLY_IMPOSSIBLE"
UNRESOLVED = "SEARCH_BUDGET_EXCEEDED"


def physically_serviceable(
    world: DemandWorld, state: Vector, reqs: tuple[CoordinateRequirement, ...]
) -> str:
    """Whether the requirement set can be served at all, ignoring the cap.

    Exact: minimal plans use only structural-reach routes and at most one
    action per route, so choosing per route over that set is a complete search.
    If the space exceeds the declared budget the answer is `UNRESOLVED` --
    refusing to report a negative the search did not establish -- rather than
    a silent `IMPOSSIBLE`.
    """
    if not reqs:
        return SERVICEABLE
    reach = structural_reach(world, frozenset(req.coordinate for req in reqs))
    routes = tuple(route for route in world.routes if route.route_id in reach.routes)
    if exhaustive_space(world, routes) > EXHAUSTIVE_BUDGET:
        return UNRESOLVED
    for group in _uncapped_groups(world, routes):
        if not serves_all(reqs, group.increment(world.dimension)):
            continue
        if can_happen_now(world, state, group).executable:
            return SERVICEABLE
    return IMPOSSIBLE


def is_irredundant(
    world: DemandWorld,
    state: Vector,
    reqs: tuple[CoordinateRequirement, ...],
    group: PlanGroup,
) -> bool:
    """No proper subset both serves the whole requirement set and can happen.

    Every proper subset is checked, not only the single-action removals. A plan
    can carry an action whose removal breaks nothing on its own while a smaller
    subset still serves, and calling such a plan irredundant would let an
    unnecessary action into a menu.
    """
    actions = group.actions
    for size in range(len(actions)):
        for chosen in combinations(actions, size):
            smaller = PlanGroup(tuple(chosen))
            if not serves_all(reqs, smaller.increment(world.dimension)):
                continue
            if can_happen_now(world, state, smaller).executable:
                return False
    return True


def irredundant_serving_groups(
    world: DemandWorld,
    state: Vector,
    reqs: tuple[CoordinateRequirement, ...],
    routes,
) -> tuple[PlanGroup, ...]:
    return tuple(
        group
        for group in serving_groups(world, state, reqs, routes)
        if is_irredundant(world, state, reqs, group)
    )
