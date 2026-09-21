"""Brute-force global feasible-service oracle, with no demand decomposition.

The decomposition invariant is easy to state and easy to get wrong, so it is
checked against an independent computation rather than argued. For a state and
a demand set this module enumerates, over the whole world at once and without
ever forming a component, every executable plan that completely serves every
demand, and returns the canonical physical increments.

The component path is then run beside it and the two sets are compared.

Each outcome is compared as a pair: the **canonical physical increment** and
the **owner receipts** it settles. Plans are not compared, because two action
orderings are the same physical outcome and must not count as a disagreement.
Increments alone would not be enough either -- an independent audit noted that
equal physical outcomes do not by themselves establish equal owner receipts,
and receipts are what drive affordability -- so the settled owner deltas are
carried into the comparison and must agree exactly.

What this still does **not** establish is a general decomposition theorem.
Passing these fixtures shows agreement on the cases enumerated, nothing wider.

Both sides run at the same action bound, **including the per-plan cap**: the
comparison rebuilds the world with `max_plan_size = bound` before enumerating
either side. That is necessary, not cosmetic. The cap is a computational
enumeration limit applied per component plan
(`DEMAND_DRIVEN_PLAN_CAP_DISPOSITION.md`), so leaving the component side at
the world's own cap while searching the global side to a larger bound compares
two different searches and reports their difference as a decomposition
failure. Equalising it isolates the question this oracle exists to answer.

The asymmetry itself -- a decomposed epoch may execute more total actions than
any single capped plan contains -- is real and declared, and is tested on its
own rather than here.

This is a conformance oracle for small synthetic worlds. It is exponential in
the number of usable routes and is never used inside the model.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations, product

from gaussian_harness.numerics import Refusal, Vector

from .coupling import components
from .demand import ActiveDemandSet
from .enumeration import is_irredundant, live_routes
from .physical import PlanGroup, action_alphabet, can_happen_now
from .plans import enumerate_service_plans
from .service import requirements, serves_all
from .valuation import value_group
from .world import DemandWorld


def _outcome(world: DemandWorld, state: Vector, group: PlanGroup):
    """The canonical comparable: physical increment plus settled receipts."""
    valuation = value_group(world, state, group)
    return (
        tuple(group.increment(world.dimension)),
        tuple(sorted(valuation.owner_deltas)),
    )

ORACLE_BUDGET = 2_000_000


def _bounded_groups(world: DemandWorld, routes, bound: int):
    alphabet = action_alphabet(world, routes)
    for size in range(1, bound + 1):
        for chosen in combinations(alphabet, size):
            if len({action.route.route_id for action in chosen}) != size:
                continue
            yield PlanGroup.of(*chosen)


def global_feasible(world: DemandWorld, state: Vector, demands, bound: int) -> frozenset:
    """Every complete executable irredundant outcome, decomposition-free."""
    reqs = requirements(demands)
    routes = live_routes(world, state)
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
        found.add(_outcome(world, state, group))
    return frozenset(found)


def component_feasible(world: DemandWorld, state: Vector, demands, bound: int) -> frozenset:
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
        outcomes.add(_outcome(world, state, PlanGroup.of(*actions)))
    return frozenset(outcomes)


def at_bound(world: DemandWorld, bound: int) -> DemandWorld:
    """The same world with its per-plan cap set to the comparison bound."""
    return DemandWorld.declare(
        world.world_id, world.coordinates, world.routes, world.quanta, bound
    )


def agree(world: DemandWorld, state: Vector, demands, bound: int) -> tuple[bool, dict]:
    """Compare the two, returning the verdict and the exact difference."""
    equalised = at_bound(world, bound)
    left = global_feasible(equalised, state, demands, bound)
    right = component_feasible(equalised, state, demands, bound)
    return left == right, {
        "global": len(left),
        "components": len(right),
        "only_global": sorted(str(x) for x in (left - right))[:4],
        "only_components": sorted(str(x) for x in (right - left))[:4],
    }
