"""Demand-serving plans: what an actor is actually allowed to consider.

A plan enters an actor's menu only if all three of the following hold for the
component it addresses.

1. **Complete service.** Every demand in the component is served in full.
   Partial service, backlog, fractional fulfilment and deadlines do not exist
   in this model; a component that cannot be served completely is left
   unresolved.
2. **It can actually happen now.** Physical executability is decided on the
   frozen pre-action state, before any EBU number exists.
3. **Irredundancy.** No proper subset of the plan already serves the whole
   component while itself being executable.

The third condition is what enforces demand provenance, and it is the single
structural guard against recreating the old arbitrary-action environment. If an
action could be dropped and the component would still be served, the plan
containing it is not in the menu — so an actor cannot bolt an unrelated
transfer onto a legitimate plan and spend capacity on it. Conversely, in an
irredundant plan every action is necessary for something: for each action `a`
there is a demand that `G \\ {a}` fails, or `G \\ {a}` cannot execute at all.
That demand set is the action's provenance, and it may be many-to-many.

With no active demand there are no components, hence no plans, hence an empty
menu. Nothing needs to forbid the arbitrary transfer separately; it simply has
nowhere to come from.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations

from gaussian_harness.numerics import Refusal, Vector

from .coupling import DemandComponent
from .demand import Demand, completely_serves, coverage
from .physical import PhysicalAction, PlanGroup, action_alphabet, can_happen_now
from .world import DemandWorld


@dataclass(frozen=True)
class ServicePlan:
    """One complete, executable, irredundant way to serve one component."""

    component_id: str
    group: PlanGroup
    served: tuple[str, ...]
    coverage: tuple[tuple[str, Fraction, Fraction], ...]
    physical_support: frozenset[int]
    constraint_support: frozenset[str]
    owner_support: frozenset[str]
    provenance: tuple[tuple[str, tuple[str, ...]], ...]

    def __post_init__(self) -> None:
        if not self.served:
            raise Refusal("a service plan must serve at least one demand")
        for action_id, demand_ids in self.provenance:
            if not demand_ids:
                raise Refusal(f"action {action_id} has no demand provenance")

    @property
    def plan_id(self) -> str:
        return f"{self.component_id}::{self.group.group_id}"

    @property
    def provenance_map(self) -> dict[str, tuple[str, ...]]:
        return dict(self.provenance)


def serves_component(component: DemandComponent, increment: Vector) -> bool:
    return all(completely_serves(demand, increment) for demand in component.demands)


def _build(
    world: DemandWorld, component: DemandComponent, group: PlanGroup
) -> ServicePlan:
    increment = group.increment(world.dimension)
    covered = tuple(
        (demand.demand_id,) + coverage(demand, increment) for demand in component.demands
    )
    provenance = []
    for action in group.actions:
        remainder = group.subsets_without(action)
        reduced = remainder.increment(world.dimension)
        failed = tuple(
            demand.demand_id
            for demand in component.demands
            if not completely_serves(demand, reduced)
        )
        if not failed:
            # Irredundancy already guarantees the remainder cannot both execute
            # and serve; reaching here means it serves but cannot happen, so
            # this action is what makes the plan physically possible at all.
            failed = component.demand_ids
        provenance.append((action.action_id, failed))
    return ServicePlan(
        component.component_id,
        group,
        component.demand_ids,
        covered,
        group.support,
        group.route_support,
        group.owner_support(world),
        tuple(provenance),
    )


def enumerate_service_plans(
    world: DemandWorld, state: Vector, component: DemandComponent
) -> tuple[ServicePlan, ...]:
    """Every complete, executable, irredundant plan for this component."""
    routes = tuple(
        route for route in world.routes if route.route_id in component.reach.routes
    )
    alphabet = action_alphabet(world, routes)
    found: list[ServicePlan] = []
    for size in range(1, world.max_plan_size + 1):
        for chosen in combinations(alphabet, size):
            used = {action.route.route_id for action in chosen}
            if len(used) != size:
                continue
            group = PlanGroup.of(*chosen)
            increment = group.increment(world.dimension)
            if not serves_component(component, increment):
                continue
            if not can_happen_now(world, state, group).executable:
                continue
            if not _is_irredundant(world, state, component, group):
                continue
            found.append(_build(world, component, group))
    return tuple(sorted(found, key=lambda plan: plan.plan_id))


def _is_irredundant(
    world: DemandWorld, state: Vector, component: DemandComponent, group: PlanGroup
) -> bool:
    actions = group.actions
    for size in range(len(actions)):
        for chosen in combinations(actions, size):
            smaller = PlanGroup(tuple(chosen))
            if not serves_component(component, smaller.increment(world.dimension)):
                continue
            if can_happen_now(world, state, smaller).executable:
                return False
    return True


def candidate_menu(
    world: DemandWorld, state: Vector, components: tuple[DemandComponent, ...]
) -> dict[str, tuple[ServicePlan, ...]]:
    """Per-component menus. Empty overall when no demand is active."""
    return {
        component.component_id: enumerate_service_plans(world, state, component)
        for component in components
    }


def unrelated_transfers(
    world: DemandWorld, state: Vector, components: tuple[DemandComponent, ...]
) -> tuple[PhysicalAction, ...]:
    """Physically possible actions that appear in no plan of any menu.

    A regression witness, not a mechanism. The old environment offered these to
    actors; the corrected one must never place one in a menu, and this function
    exists so the conformance suite can show the set is non-empty and yet
    entirely unreachable.
    """
    menu = candidate_menu(world, state, components)
    offered = {
        action.action_id
        for plans in menu.values()
        for plan in plans
        for action in plan.group.actions
    }
    return tuple(
        action
        for action in action_alphabet(world)
        if action.action_id not in offered
        and can_happen_now(world, state, PlanGroup.of(action)).executable
    )


def has_service_plan(
    world: DemandWorld, state: Vector, component: DemandComponent
) -> bool:
    """Whether the component can be served completely at all, right now.

    Early-exit form of `enumerate_service_plans`, used by the admission policy.
    Irredundancy is not checked here: existence of any complete executable plan
    implies existence of an irredundant one, because a minimal such subset of
    it is itself complete and executable.
    """
    routes = tuple(
        route for route in world.routes if route.route_id in component.reach.routes
    )
    alphabet = action_alphabet(world, routes)
    for size in range(1, world.max_plan_size + 1):
        for chosen in combinations(alphabet, size):
            used = {action.route.route_id for action in chosen}
            if len(used) != size:
                continue
            group = PlanGroup.of(*chosen)
            if not serves_component(component, group.increment(world.dimension)):
                continue
            if can_happen_now(world, state, group).executable:
                return True
    return False
