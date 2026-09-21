"""Plan enumeration primitives, shared by coupling and menu construction.

Kept separate from both so that the dependency graph stays acyclic: coupling
needs to know what plans *could* serve a demand in order to decide whether two
demands interact, and menu construction needs the same machinery over a whole
component.

Two route sets appear in this package and they are deliberately different.

* The **binding reach** in `coupling` is narrow. It is what decides whether two
  demands are coupled, and a reach that is too wide merges components that do
  not interact, which freezes serviceable demands behind unserviceable ones.
* The **search routes** here are generous: every route touching the transport
  closure of a component's coordinates. Breadth in enumeration is safe in the
  one direction that matters — it can only offer more valid plans, never
  delete one — so the search set is kept wide on purpose.
"""

from __future__ import annotations

from itertools import combinations

from gaussian_harness.numerics import Vector

from .physical import PlanGroup, action_alphabet, can_happen_now
from .service import CoordinateRequirement, serves_all
from .world import DemandWorld


def search_routes(world: DemandWorld, coordinates: frozenset[int]) -> tuple:
    """Every route touching the transport closure of these coordinates."""
    closure: set[int] = set()
    for coordinate in coordinates:
        closure |= world.transport_component(coordinate)
    return tuple(
        route
        for route in world.routes
        if route.source in closure or route.destination in closure
    )


def _groups(world: DemandWorld, routes, limit: int):
    alphabet = action_alphabet(world, routes)
    for size in range(1, limit + 1):
        for chosen in combinations(alphabet, size):
            if len({action.route.route_id for action in chosen}) != size:
                continue
            yield PlanGroup.of(*chosen)


def serving_groups(
    world: DemandWorld,
    state: Vector,
    reqs: tuple[CoordinateRequirement, ...],
    routes,
) -> tuple[PlanGroup, ...]:
    """Complete, executable plans over the given routes. Irredundancy not applied."""
    found = []
    for group in _groups(world, routes, world.max_plan_size):
        if not serves_all(reqs, group.increment(world.dimension)):
            continue
        if not can_happen_now(world, state, group).executable:
            continue
        found.append(group)
    return tuple(found)


def has_serving_group(
    world: DemandWorld,
    state: Vector,
    reqs: tuple[CoordinateRequirement, ...],
    routes,
) -> bool:
    """Early-exit existence test, used by admission.

    Irredundancy is not checked: if any complete executable plan exists then a
    minimal such subset of it is itself complete and executable, so an
    irredundant one exists too.
    """
    for group in _groups(world, routes, world.max_plan_size):
        if not serves_all(reqs, group.increment(world.dimension)):
            continue
        if can_happen_now(world, state, group).executable:
            return True
    return False


def is_irredundant(
    world: DemandWorld,
    state: Vector,
    reqs: tuple[CoordinateRequirement, ...],
    group: PlanGroup,
) -> bool:
    """No proper subset both serves the whole requirement set and can happen.

    Every proper subset is checked, not only the single-action removals. A
    plan can carry an action whose removal breaks nothing on its own while a
    smaller subset still serves, and calling such a plan irredundant would let
    an unnecessary action into a menu.
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
