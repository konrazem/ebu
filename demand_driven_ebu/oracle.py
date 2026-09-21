"""Brute-force global feasible-service oracle, with no demand decomposition.

The decomposition invariant is easy to state and easy to get wrong, so it is
checked against an independent computation rather than argued. For a state and
a demand set this module enumerates, over the whole world at once and without
ever forming a component, every executable plan that completely serves every
demand, and returns the canonical physical increments.

The component path is then run beside it and the two sets are compared.
Increments are compared, not plans: two different action orderings, or two
plans that differ only in which route carried which quantum, are the same
physical outcome and must not count as a disagreement.

Both sides take the same explicit action bound. That matters because the
plan-size cap is a computational enumeration limit applied **per component
plan** (`DEMAND_DRIVEN_PLAN_CAP_DISPOSITION.md`), so a decomposed run may use
more total actions in one epoch than any single capped plan. Holding one bound
across both sides removes that asymmetry from the comparison; the asymmetry
itself is real, declared, and tested separately.

This is a conformance oracle for small synthetic worlds. It is exponential in
the number of usable routes and is never used inside the model.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations, product

from gaussian_harness.numerics import Refusal, Vector

from .coupling import components
from .demand import ActiveDemandSet
from .enumeration import is_irredundant, usable_routes
from .physical import PlanGroup, action_alphabet, can_happen_now
from .plans import enumerate_service_plans
from .service import requirements, serves_all
from .world import DemandWorld

ORACLE_BUDGET = 2_000_000


def _bounded_groups(world: DemandWorld, routes, bound: int):
    alphabet = action_alphabet(world, routes)
    for size in range(1, bound + 1):
        for chosen in combinations(alphabet, size):
            if len({action.route.route_id for action in chosen}) != size:
                continue
            yield PlanGroup.of(*chosen)


def global_feasible(
    world: DemandWorld, state: Vector, demands, bound: int
) -> frozenset[tuple[Fraction, ...]]:
    """Every complete executable irredundant outcome, decomposition-free."""
    reqs = requirements(demands)
    routes = usable_routes(world)
    space = sum(
        len(list(combinations(range(len(action_alphabet(world, routes))), size)))
        for size in range(1, bound + 1)
    )
    if space > ORACLE_BUDGET:
        raise Refusal(f"oracle search space {space} exceeds the declared budget")
    found = set()
    for group in _bounded_groups(world, routes, bound):
        increment = group.increment(world.dimension)
        if not serves_all(reqs, increment):
            continue
        if not can_happen_now(world, state, group).executable:
            continue
        if not is_irredundant(world, state, reqs, group):
            continue
        found.add(tuple(increment))
    return frozenset(found)


def component_feasible(
    world: DemandWorld, state: Vector, demands, bound: int
) -> frozenset[tuple[Fraction, ...]]:
    """Outcomes reachable through decomposition and independent combination."""
    active = ActiveDemandSet.of(
        tuple(d for d in demands if d.demand_class == "P"),
        tuple(d for d in demands if d.demand_class == "E"),
    )
    found = components(world, state, active)
    menus = []
    for component in found:
        plans = enumerate_service_plans(world, state, component)
        if not plans:
            return frozenset()
        menus.append([plan.group for plan in plans])
    outcomes = set()
    for combination in product(*menus):
        actions = tuple(
            action for group in combination for action in group.actions
        )
        if len(actions) > bound:
            continue
        if len({action.route.route_id for action in actions}) != len(actions):
            continue
        outcomes.add(tuple(PlanGroup.of(*actions).increment(world.dimension)))
    return frozenset(outcomes)


def agree(world: DemandWorld, state: Vector, demands, bound: int) -> tuple[bool, dict]:
    """Compare the two, returning the verdict and the exact difference."""
    left = global_feasible(world, state, demands, bound)
    right = component_feasible(world, state, demands, bound)
    return left == right, {
        "global": len(left),
        "components": len(right),
        "only_global": sorted(str(x) for x in (left - right))[:4],
        "only_components": sorted(str(x) for x in (right - left))[:4],
    }
