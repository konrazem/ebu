"""Demand-serving plans: what an actor is actually allowed to consider.

A plan enters an actor's menu only if all three of the following hold for the
component it addresses.

1. **Complete service of the whole requirement set.** Every coordinate receives
   at least `max(sum of economic orders there, physical shortfall there)`.
   Economic quantities are additive across separate orders; a physical
   shortfall is a condition on the post-state and draws nothing from the
   economic pool. See `service`.
2. **It can actually happen now.** Physical executability is decided on the
   frozen pre-action state, before any EBU number exists.
3. **Irredundancy.** No proper subset of the plan already serves the whole
   requirement set while itself being executable.

The third condition is what enforces demand provenance, and it is the single
structural guard against recreating the old arbitrary-action environment. If an
action could be dropped and the component would still be served, the plan
containing it is not in the menu, so an actor cannot bolt an unrelated transfer
onto a legitimate plan and spend capacity on it. Conversely, in an irredundant
plan every action is necessary for something: for each action `a` there is a
demand that `G \\ {a}` fails, or `G \\ {a}` cannot execute at all. That demand
set is the action's provenance, and it may be many-to-many.

With no active demand there are no components, hence no plans, hence an empty
menu. Nothing needs to forbid the arbitrary transfer separately; it simply has
nowhere to come from.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from gaussian_harness.numerics import Refusal, Vector

from .coupling import DemandComponent
from .enumeration import (
    IMPOSSIBLE,
    SERVICEABLE,
    UNRESOLVED,
    has_serving_group,
    irredundant_serving_groups,
    physically_serviceable,
    search_routes,
)
from .physical import PhysicalAction, PlanGroup, action_alphabet, can_happen_now
from .service import (
    CoordinateRequirement,
    ServiceAllocation,
    allocations,
    requirements,
    serves_all,
    unmet,
)
from .world import DemandWorld


@dataclass(frozen=True)
class ServicePlan:
    """One complete, executable, irredundant way to serve one component."""

    component_id: str
    group: PlanGroup
    served: tuple[str, ...]
    coverage: tuple[tuple[str, Fraction, Fraction], ...]
    allocation: tuple[ServiceAllocation, ...]
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
        for entry in self.allocation:
            if not entry.complete:
                raise Refusal(
                    f"a menu plan must allocate every order in full at coordinate "
                    f"{entry.coordinate}; short by {entry.shortfall}"
                )

    @property
    def plan_id(self) -> str:
        return f"{self.component_id}::{self.group.group_id}"

    @property
    def provenance_map(self) -> dict[str, tuple[str, ...]]:
        return dict(self.provenance)


def component_routes(world: DemandWorld, component: DemandComponent):
    return tuple(route for route in world.routes if route.route_id in component.search)


def serves_component(component: DemandComponent, increment: Vector) -> bool:
    return serves_all(component.requirements, increment)


def _build(
    world: DemandWorld, component: DemandComponent, group: PlanGroup
) -> ServicePlan:
    reqs = component.requirements
    increment = group.increment(world.dimension)
    covered = tuple(
        (demand.demand_id, demand.required_delta, increment[demand.coordinate])
        for demand in component.demands
    )
    provenance = []
    for action in group.actions:
        remainder = group.subsets_without(action)
        failed = unmet(reqs, remainder.increment(world.dimension))
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
        allocations(reqs, increment),
        group.support,
        group.route_support,
        group.owner_support(world),
        tuple(provenance),
    )


def enumerate_service_plans(
    world: DemandWorld, state: Vector, component: DemandComponent
) -> tuple[ServicePlan, ...]:
    """Every complete, executable, irredundant plan for this component.

    **One entry per canonical plan identity.** A plan's identity is its
    physical action set; `PlanGroup` sorts its actions and refuses a repeated
    route, so two encodings of one action set carry one identity. That matters
    beyond tidiness: the random actor samples uniformly over this menu, so a
    duplicated record would silently double an outcome's probability. The
    duplicate check is enforced here rather than assumed.
    """
    groups = irredundant_serving_groups(
        world, state, component.requirements, component_routes(world, component)
    )
    unique: dict[str, object] = {}
    for group in groups:
        identity = group.group_id
        if identity in unique:
            continue
        unique[identity] = group
    built = tuple(
        sorted(
            (_build(world, component, group) for group in unique.values()),
            key=lambda plan: plan.plan_id,
        )
    )
    identities = [plan.group.group_id for plan in built]
    if len(set(identities)) != len(identities):
        raise Refusal("a menu may not carry two records of one plan identity")
    return built


def has_service_plan(
    world: DemandWorld, state: Vector, component: DemandComponent
) -> bool:
    """Whether a complete executable plan exists **within the menu cap**."""
    return has_serving_group(
        world, state, component.requirements, component_routes(world, component)
    )


SERVICEABLE_WITHIN_CAP = "SERVICEABLE_WITHIN_CAP"
BEYOND_CAP = "SEARCH_INCOMPLETE_AT_PLAN_CAP"
PHYSICALLY_IMPOSSIBLE = "PHYSICALLY_IMPOSSIBLE"
SEARCH_UNRESOLVED = "SEARCH_BUDGET_EXCEEDED"


def serviceability(
    world: DemandWorld, state: Vector, component: DemandComponent
) -> str:
    """Why a component has no menu, distinguishing search from physics.

    The plan-size cap is a computational enumeration limit, not a physical
    simultaneity constraint (`DEMAND_DRIVEN_PLAN_CAP_DISPOSITION.md`), so an
    empty menu must never be reported as physical impossibility on its
    authority. When the capped search finds nothing, an exact uncapped search
    over the structural reach decides which of the three answers holds, and
    refuses rather than guessing if its own budget is exceeded.
    """
    if has_service_plan(world, state, component):
        return SERVICEABLE_WITHIN_CAP
    verdict = physically_serviceable(world, state, component.requirements)
    if verdict == SERVICEABLE:
        return BEYOND_CAP
    if verdict == IMPOSSIBLE:
        return PHYSICALLY_IMPOSSIBLE
    return SEARCH_UNRESOLVED


def candidate_menu(
    world: DemandWorld, state: Vector, found: tuple[DemandComponent, ...]
) -> dict[str, tuple[ServicePlan, ...]]:
    """Per-component menus. Empty overall when no demand is active."""
    return {
        component.component_id: enumerate_service_plans(world, state, component)
        for component in found
    }


def unrelated_transfers(
    world: DemandWorld, state: Vector, found: tuple[DemandComponent, ...]
) -> tuple[PhysicalAction, ...]:
    """Physically possible actions that appear in no plan of any menu.

    A regression witness, not a mechanism. The old environment offered these to
    actors; the corrected one must never place one in a menu, and this function
    exists so the conformance suite can show the set is non-empty and yet
    entirely unreachable.
    """
    menu = candidate_menu(world, state, found)
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
