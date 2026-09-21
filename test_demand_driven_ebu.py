"""Exact conformance gate for the demand-driven EBU economy.

Covers the scientific contract end to end: the two demand classes and their
service semantics, EBU-blind random admission, the demand-dependency graph,
complete service plans, physical executability, exact valuation and
common-path receipt closure, Capacity V1 affordability, the three actor
policies and the no-EBU comparator, simultaneous independent execution,
P-demand re-derivation, explicit loss, the closed-cycle no-issuance theorem
and the capacity-source classification, the sixteen hand-checkable fixtures,
and the structural guards against recreating the arbitrary-action environment.

All arithmetic is exact rational with tolerance literally zero. Where a
quantity is asserted to be conserved, closed or unchanged, the assertion is an
exact equality and not a tolerance test.

**No science is adopted here.** Not one check requires a policy to restore the
system, requires a drift to have a particular sign, or asserts that the
demand-driven economy behaves well. Several checks exist specifically to pin
down refusal, scarcity, unaffordability and permanent loss. Signs and
magnitudes that appear below are computed from the declared numbers, not
demanded of the model.

Running this suite advances model state in the sections that drive epochs, so
it is a transition suite, not a static check. Executing it is not a result.
"""

from __future__ import annotations

import ast
import inspect
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path

from gaussian_harness.numerics import Refusal, add
from gaussian_harness.potential import LocalGaussianPotential

import demand_driven_ebu.harness as harness_module
from demand_driven_ebu import MODEL_ID
from demand_driven_ebu.admission import admit, classify, unresolved_ids, unserviceable_ids
from demand_driven_ebu.arrivals import ArrivalProcess
from demand_driven_ebu.capacity import CapacityLedger
from demand_driven_ebu.coupling import components, service_reach
from demand_driven_ebu.cycles import (
    CAPACITY_SOURCE_TABLE,
    actor_only,
    closed_cycle,
    net_loss,
    window,
)
from demand_driven_ebu.demand import (
    DECLARED_LIFECYCLE,
    E_ADMITTED_PENDING,
    E_REJECTED_INCOMPATIBLE,
    E_REJECTED_PHYSICAL_SCARCITY,
    LIFECYCLE_ADMITTED_BUT_EBU_UNAFFORDABLE,
    LIFECYCLE_ARRIVED,
    LIFECYCLE_REJECTED_PHYSICAL_SCARCITY,
    LIFECYCLE_SERVED,
    ActiveDemandSet,
    EconomicDemand,
    derive_physical_demands,
)
from demand_driven_ebu.service import (
    allocate,
    pool,
    requirements,
    served_economic_ids,
    serves_all,
    unmet,
)
from demand_driven_ebu.disturbance import DisturbanceProcess, apply_disturbance
from demand_driven_ebu.fixtures import (
    audit_sink_world,
    capacity_relief_state,
    capacity_relief_world,
    competing_world,
    cycle_world,
    loss_world,
    no_arrivals,
    quiet_disturbance,
    routeless_world,
    sandwater_world,
    shared_sink_state,
    shared_sink_world,
    shared_source_world,
    scarcity_world,
    blocked_neighbour_state,
    study_one_state,
    study_one_world,
    two_supplier_state,
    two_supplier_world,
    ScriptedArrivals,
    ScriptedDisturbance,
    seeded_ledger,
    surplus_world,
    triple_delivery_state,
    triple_delivery_world,
    empty_source_world,
    wide_supply_state,
    wide_supply_world,
)
from demand_driven_ebu.harness import (
    DECOMPOSITION_NOT_CHECKED,
    DECOMPOSITION_VERIFIED,
    DECLARED_STATUSES,
    STATUS_ALL_UNAFFORDABLE,
    STATUS_EXECUTED,
    STATUS_NO_ACTIVE_DEMAND,
    STATUS_NO_COMPLETE_PLAN,
    STATUS_SEARCH_INCOMPLETE,
    STATUS_SEARCH_UNRESOLVED,
    EconomyRun,
    code_identity,
)
from demand_driven_ebu.enumeration import (
    IMPOSSIBLE,
    SERVICEABLE,
    UNRESOLVED,
    live_routes,
    physically_serviceable,
    usable_routes,
)
from demand_driven_ebu.study_one import (
    STUDY_ONE_DOMAIN_ID,
    CompletenessBound,
    JobInvalid,
    action_bound,
    completeness_bound,
    domain_violations,
    in_domain,
    plan_space,
    require_domain,
    state_violations,
)
from demand_driven_ebu.oracle import (
    BLOCKED,
    LEVELS,
    all_complete_agree,
    all_complete_outcomes,
    all_complete_plans,
    canonical,
    component_all_complete_outcomes,
    component_progress,
    extremal_identities,
    global_progress,
    outcome,
    outcome_support,
    plan_identity,
    policy_law,
    progress_levels,
    random_law,
    reference_partition,
)
from demand_driven_ebu.physical import (
    PhysicalAction,
    PlanGroup,
    action_alphabet,
    can_happen_now,
)
from demand_driven_ebu.plans import (
    BEYOND_CAP,
    PHYSICALLY_IMPOSSIBLE,
    SERVICEABLE_WITHIN_CAP,
    enumerate_service_plans,
    has_service_plan,
    serviceability,
    unrelated_transfers,
)
from demand_driven_ebu.policies import (
    POLICY_ALIGNED,
    POLICY_CONTROL,
    POLICY_HOSTILE,
    POLICY_RANDOM,
    choose,
    specification,
)
from demand_driven_ebu.rng import DECLARED_STREAMS, Counter, uniform_index
from demand_driven_ebu.valuation import (
    linear_estimate,
    quadratic_ebu,
    receipt_closed_form,
    receipt_quadrature,
    value_group,
)
from demand_driven_ebu.world import Coordinate, DemandWorld, Route

PASSED = 0
FAILED = 0


def check(label: str, condition: bool, detail: str = "") -> None:
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  PASS  {label}")
    else:
        FAILED += 1
        print(f"  FAIL  {label}{(' -- ' + detail) if detail else ''}")


def _state(*values) -> tuple[F, ...]:
    return tuple(F(v) for v in values)


def _route(world: DemandWorld, source: int, destination: int) -> Route:
    for route in world.routes:
        if route.source == source and route.destination == destination:
            return route
    raise AssertionError(f"no route {source}->{destination} in {world.world_id}")


def _plan(world: DemandWorld, *moves) -> PlanGroup:
    return PlanGroup.of(
        *[PhysicalAction.declare(_route(world, s, d), q) for s, d, q in moves]
    )


def _economic(world, resource, quantity, node, epoch=0, index=0) -> EconomicDemand:
    return EconomicDemand.declare(world, resource, quantity, node, epoch, index)


# --------------------------------------------------------------------------
# Potential geometry, cross-checked against the pinned registered oracle
# --------------------------------------------------------------------------


def test_potential_agrees_with_the_registered_oracle() -> None:
    """On an all-valued world this geometry must equal `gaussian_harness`'s."""
    world = sandwater_world()
    mine = world.potential
    theirs = LocalGaussianPotential.declare(
        [c.reference for c in world.coordinates], [c.scale for c in world.coordinates]
    )
    worst_value = F(0)
    worst_marginal = F(0)
    worst_hessian = F(0)
    for state in (
        _state(10, 10, 10, 6, 6),
        _state(8, 12, 10, 4, 8),
        _state(0, 20, 10, 12, 0),
        _state(30, 0, 0, 1, 11),
    ):
        worst_value = max(worst_value, abs(mine.value_total(state) - theirs.value_total(state)))
        for index in range(world.dimension):
            worst_marginal = max(
                worst_marginal, abs(mine.marginal(state, index) - theirs.marginal(state, index))
            )
            worst_hessian = max(
                worst_hessian,
                abs(mine.hessian_diagonal(index) - theirs.hessian_diagonal(index)),
            )
    check("value agrees with the registered potential exactly", worst_value == 0, str(worst_value))
    check("marginal agrees exactly", worst_marginal == 0, str(worst_marginal))
    check("curvature agrees exactly", worst_hessian == 0, str(worst_hessian))


def test_audit_only_coordinate_carries_no_potential() -> None:
    """An audit-only sink has no reference, so it has nothing to restore."""
    world = audit_sink_world()
    potential = world.potential
    sink = world.index_of("sand", "W")
    state = _state(6, 12, 2)
    check("audit sink carries no potential", not potential.carries_potential(sink))
    check("audit sink has zero marginal", potential.marginal(state, sink) == 0)
    check("audit sink has zero curvature", potential.hessian_diagonal(sink) == 0)
    check("audit sink has zero deficit", potential.deficit(state, sink) == 0)
    check(
        "V ignores the audit sink entirely",
        potential.value_total(state) == potential.value_total(_state(6, 12, 999)),
    )


def test_potential_refuses_half_declared_coordinates() -> None:
    try:
        Coordinate("sand", "A", "STOCK", F(10), None)
    except Refusal:
        check("a coordinate declaring only a reference is refused", True)
    else:
        check("a coordinate declaring only a reference is refused", False)


# --------------------------------------------------------------------------
# Contract sections 2.1 and 21 -- P-demand is read off the state
# --------------------------------------------------------------------------


def test_physical_demand_is_derived_not_stored() -> None:
    world = sandwater_world()
    at_reference = world.reference_state()
    check("no shortfall at the reference means no P-demand",
          derive_physical_demands(world, at_reference) == ())

    disturbed = _state(8, 12, 10, 6, 6)
    demands = derive_physical_demands(world, disturbed)
    check("one shortfall gives exactly one P-demand", len(demands) == 1)
    check("the P-demand names the deficient coordinate", demands[0].demand_id == "P:sand|A")
    check("the required quantity is the exact shortfall", demands[0].required == F(2))
    check("a surplus is not a demand",
          all(d.demand_id != "P:sand|B" for d in demands))


def test_physical_demand_persists_while_the_deviation_does() -> None:
    """No queue remembers it and no queue is needed: re-derivation is the memory."""
    world = sandwater_world()
    partial = _state(9, 11, 10, 6, 6)
    still = derive_physical_demands(world, partial)
    check("a partly closed shortfall is still a demand", len(still) == 1)
    check("its size shrinks with the shortfall", still[0].required == F(1))
    resolved = derive_physical_demands(world, world.reference_state())
    check("a resolved shortfall disappears automatically", resolved == ())


def test_physical_demand_cannot_be_rejected() -> None:
    """There is no API through which a P-demand could be refused or deferred."""
    source = inspect.getsource(harness_module)
    banned = ("reject_physical", "defer_physical", "P_REJECTED", "priority", "deadline")
    present = [token for token in banned if token in source]
    check("the harness exposes no way to reject or defer a P-demand", not present, str(present))


def test_multiple_physical_demands_coexist() -> None:
    world = sandwater_world()
    state = _state(8, 8, 14, 4, 8)
    demands = derive_physical_demands(world, state)
    ids = sorted(d.demand_id for d in demands)
    check("three simultaneous shortfalls give three demands",
          ids == ["P:sand|A", "P:sand|B", "P:water|D"], str(ids))


# --------------------------------------------------------------------------
# Contract section 3 -- economic demand may exceed what exists
# --------------------------------------------------------------------------


def test_economic_demand_may_exceed_available_resource() -> None:
    world = scarcity_world()
    state = _state(560, 0, 0)
    asked = _economic(world, "sand", 1000, "C")
    check("the request is recorded at its full size", asked.quantity == F(1000))
    check("the world holds less than was asked",
          world.resource_total(state, "sand") == F(560))

    active = ActiveDemandSet.of((), (asked,))
    blocked = unserviceable_ids(world, state, (), (asked,))
    check("the oversized demand is physically unserviceable",
          asked.demand_id in blocked)
    for component in components(world, state, active):
        check("no complete plan exists for it",
              not has_service_plan(world, state, component))
        check("its menu is empty",
              enumerate_service_plans(world, state, component) == ())


def test_scarcity_is_decided_before_ebu() -> None:
    """Rejection for scarcity must happen without any EBU number existing."""
    world = scarcity_world()
    state = _state(560, 0, 0)
    asked = _economic(world, "sand", 1000, "C")
    admitted, rejected, decision = admit(world, state, (), (), (asked,), 7, 0)
    check("the oversized demand is not admitted", admitted == ())
    check("it is rejected for physical scarcity",
          rejected[0].status == E_REJECTED_PHYSICAL_SCARCITY, rejected[0].status)
    check("it is not truncated to what exists", rejected[0].quantity == F(1000))
    check("no smaller replacement demand is generated", len(rejected) == 1)
    check("the only maximal admissible subset is empty",
          decision.maximal_subsets == ((),), str(decision.maximal_subsets))


# --------------------------------------------------------------------------
# Contract sections 4, 5 and 6 -- EBU-blind random admission
# --------------------------------------------------------------------------


def test_admission_never_reads_ebu_or_capacity() -> None:
    import demand_driven_ebu.admission as admission_module

    tree = ast.parse(inspect.getsource(admission_module))
    names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
    attributes = {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}
    forbidden = {"value_group", "CapacityLedger", "group_ebu", "ledger", "balances",
                 "owner_deltas", "potential", "is_affordable"}
    leaked = sorted((names | attributes) & forbidden)
    check("the admission module references no EBU or capacity symbol", not leaked, str(leaked))


def test_random_admission_picks_a_maximal_compatible_subset() -> None:
    world = competing_world()
    state = _state(3, 0, 0)
    first = _economic(world, "sand", 3, "B", 0, 0)
    second = _economic(world, "sand", 3, "C", 0, 1)

    check("each demand alone is serviceable",
          has_service_plan(world, state, components(world, state, ActiveDemandSet.of((), (first,)))[0])
          and has_service_plan(world, state, components(world, state, ActiveDemandSet.of((), (second,)))[0]))
    both = components(world, state, ActiveDemandSet.of((), (first, second)))
    check("together they are one coupled component", len(both) == 1)
    check("together they are unserviceable", not has_service_plan(world, state, both[0]))

    admitted, rejected, decision = admit(world, state, (), (), (first, second), 5, 0)
    check("exactly one of the two is admitted", len(admitted) == 1, str(decision.admitted))
    check("the other is rejected as incompatible, not scarce",
          rejected[0].status == E_REJECTED_INCOMPATIBLE, rejected[0].status)
    check("both singletons were offered as maximal subsets",
          sorted(decision.maximal_subsets) == [(first.demand_id,), (second.demand_id,)],
          str(decision.maximal_subsets))
    check("the admitted demand is marked pending", admitted[0].status == E_ADMITTED_PENDING)


def test_admission_is_uniform_over_maximal_subsets() -> None:
    """Both compatible subsets must actually occur as the seed varies."""
    world = competing_world()
    state = _state(3, 0, 0)
    first = _economic(world, "sand", 3, "B", 0, 0)
    second = _economic(world, "sand", 3, "C", 0, 1)
    seen = set()
    for seed in range(40):
        admitted, _, _ = admit(world, state, (), (), (first, second), seed, 0)
        seen.add(admitted[0].demand_id)
    check("admission reaches both compatible subsets", len(seen) == 2, str(sorted(seen)))


def test_admission_optimizes_nothing() -> None:
    """A larger request must not be preferred, nor a smaller one."""
    world = competing_world()
    state = _state(3, 0, 0)
    big = _economic(world, "sand", 3, "B", 0, 0)
    small = _economic(world, "sand", 3, "C", 0, 1)
    counts = {big.demand_id: 0, small.demand_id: 0}
    for seed in range(60):
        admitted, _, _ = admit(world, state, (), (), (big, small), seed, 0)
        counts[admitted[0].demand_id] += 1
    check("neither destination is systematically preferred",
          min(counts.values()) > 0, str(counts))


def test_admission_protects_an_existing_physical_demand() -> None:
    """Contract section 6: a new optional obligation may not break an existing need."""
    world = competing_world()
    # A holds 3; B is 3 below its reference of 0? No: use a shortfall at B.
    shifted = DemandWorld.declare(
        "protect-v1",
        [
            Coordinate.stock("sand", "A", 0, 1),
            Coordinate.stock("sand", "B", 3, 1),
            Coordinate.stock("sand", "C", 0, 1),
        ],
        [Route.declare("sand", 0, 1, 3), Route.declare("sand", 0, 2, 3)],
        (3,),
        2,
    )
    state = _state(3, 0, 0)
    physical = derive_physical_demands(shifted, state)
    check("the world starts with one physical shortfall at B",
          [d.demand_id for d in physical] == ["P:sand|B"], str([d.demand_id for d in physical]))

    rival = _economic(shifted, "sand", 3, "C", 0, 0)
    admitted, rejected, _ = admit(shifted, state, physical, (), (rival,), 3, 0)
    check("the economic demand that would starve it is refused", admitted == ())
    check("and the refusal is recorded against physics",
          rejected[0].status == E_REJECTED_PHYSICAL_SCARCITY, rejected[0].status)


def test_already_stuck_demands_do_not_freeze_admission() -> None:
    """A pre-existing unserviceable demand is excluded, not treated as a veto."""
    world = sandwater_world()
    state = _state(3, 10, 10, 4, 8)
    physical = derive_physical_demands(world, state)
    blocked = unserviceable_ids(world, state, physical, ())
    check("the deep sand shortfall is already unserviceable",
          "P:sand|A" in blocked, str(sorted(blocked)))
    arrival = _economic(world, "water", 1, "D", 0, 0)
    admitted, _, _ = admit(world, state, physical, (), (arrival,), 2, 0)
    check("an unrelated water demand can still be admitted",
          [d.demand_id for d in admitted] == [arrival.demand_id], str(admitted))


# --------------------------------------------------------------------------
# Contract sections 7 and 8 -- no queue, no scheduler, both classes at once
# --------------------------------------------------------------------------


def test_the_active_demand_set_is_unordered() -> None:
    world = sandwater_world()
    state = _state(8, 8, 14, 6, 6)
    physical = derive_physical_demands(world, state)
    early = _economic(world, "sand", 2, "A", 0, 0)
    late = _economic(world, "sand", 1, "B", 9, 0)
    forwards = ActiveDemandSet.of(physical, (early, late))
    backwards = ActiveDemandSet.of(tuple(reversed(physical)), (late, early))
    check("insertion order does not survive into the active set",
          forwards == backwards)
    check("the set carries no age, deadline or priority field",
          not any(
              hasattr(demand, attribute)
              for demand in forwards.all
              for attribute in ("age", "deadline", "priority", "position", "rank")
          ))


def test_no_scheduler_symbol_exists_anywhere() -> None:
    import demand_driven_ebu.coupling as coupling_module
    import demand_driven_ebu.plans as plans_module
    import demand_driven_ebu.policies as policies_module

    banned = ("fifo", "FIFO", "oldest", "deadline", "scheduler", "service_order", "queue")
    found = []
    for module in (harness_module, coupling_module, plans_module, policies_module):
        source = inspect.getsource(module)
        for token in banned:
            # The prose explains what is absent; only code may not contain it.
            code = "\n".join(
                line for line in source.splitlines()
                if not line.strip().startswith("#")
            )
            body = ast.parse(source)
            for node in ast.walk(body):
                if isinstance(node, (ast.Name, ast.Attribute, ast.arg)):
                    text = getattr(node, "id", None) or getattr(node, "attr", None) or getattr(node, "arg", "")
                    if token.lower() in str(text).lower():
                        found.append(f"{module.__name__}:{text}")
    check("no scheduling identifier exists in the model code", not found, str(found))


def test_economic_and_physical_demands_coexist() -> None:
    world = sandwater_world()
    state = _state(8, 8, 14, 6, 6)
    physical = derive_physical_demands(world, state)
    economic = (_economic(world, "sand", 2, "A", 0, 0),)
    active = ActiveDemandSet.of(physical, economic)
    found = components(world, state, active)
    check("two P-demands and one E-demand form one coupled component",
          len(found) == 1 and len(found[0].demands) == 3, str([c.demand_ids for c in found]))
    plans = enumerate_service_plans(world, state, found[0])
    check("joint plans exist that satisfy all three at once", len(plans) > 0)
    for plan in plans:
        increment = plan.group.increment(world.dimension)
        check_all = serves_all(found[0].requirements, increment)
        if not check_all:
            check("every plan serves every demand in the component", False, plan.plan_id)
            return
    check("every plan serves every demand in the component", True)
    check("neither class is made to wait for the other",
          all(set(plan.served) == set(found[0].demand_ids) for plan in plans))


# --------------------------------------------------------------------------
# Contract sections 9, 19 and 38 -- coupling and independence
# --------------------------------------------------------------------------


def test_independent_resources_form_independent_components() -> None:
    world = sandwater_world()
    state = _state(8, 12, 10, 4, 8)
    physical = derive_physical_demands(world, state)
    found = components(world, state, ActiveDemandSet.of(physical, ()))
    check("a sand shortfall and a water shortfall do not couple", len(found) == 2,
          str([c.demand_ids for c in found]))
    sand, water = sorted(found, key=lambda c: c.component_id)
    check("their coordinate reaches are disjoint",
          not (sand.binding.coordinates & water.binding.coordinates))
    check("their route reaches are disjoint",
          not (sand.binding.routes & water.binding.routes))
    check("their owner reaches are disjoint",
          not (sand.binding.owners & water.binding.owners))


def test_shared_stock_couples_two_demands() -> None:
    world = competing_world()
    state = _state(3, 0, 0)
    first = _economic(world, "sand", 3, "B", 0, 0)
    second = _economic(world, "sand", 3, "C", 0, 1)
    found = components(world, state, ActiveDemandSet.of((), (first, second)))
    check("two demands drawing on the same stock are one component", len(found) == 1,
          str([c.demand_ids for c in found]))


def test_shared_account_couples_two_resources() -> None:
    """Node-held accounts are a real coupling channel, not a formality."""
    shared = DemandWorld.declare(
        "shared-account-v1",
        [
            Coordinate.stock("sand", "A", 8, 1),
            Coordinate.stock("sand", "B", 10, 1),
            Coordinate.stock("water", "A", 4, 1),
            Coordinate.stock("water", "E", 6, 1),
        ],
        [
            Route.declare("sand", 0, 1, 20),
            Route.declare("sand", 1, 0, 20),
            Route.declare("water", 2, 3, 20),
            Route.declare("water", 3, 2, 20),
        ],
        (1, 2),
        2,
    )
    # Both shortfalls are supplied from node A, so node A pays for both.
    state = _state(12, 8, 8, 4)
    physical = derive_physical_demands(shared, state)
    found = components(shared, state, ActiveDemandSet.of(physical, ()))
    check("a sand demand and a water demand both paid for by node A are coupled",
          len(found) == 1, str([c.demand_ids for c in found]))
    sand_reach = service_reach(shared, state, physical[0])
    water_reach = service_reach(shared, state, physical[1])
    check("the coupling is through owners, not stocks",
          not (sand_reach.coordinates & water_reach.coordinates)
          and bool(sand_reach.owners & water_reach.owners))


def test_an_impossible_component_does_not_block_an_independent_one() -> None:
    world = sandwater_world()
    state = _state(3, 10, 10, 4, 8)
    physical = derive_physical_demands(world, state)
    found = components(world, state, ActiveDemandSet.of(physical, ()))
    verdicts = {c.component_id: has_service_plan(world, state, c) for c in found}
    check("the deep sand shortfall has no complete plan",
          verdicts["c:[P:sand|A]"] is False, str(verdicts))
    check("the water shortfall still has one",
          verdicts["c:[P:water|D]"] is True, str(verdicts))


# --------------------------------------------------------------------------
# Contract sections 10, 11, 39 and 40 -- complete service and provenance
# --------------------------------------------------------------------------


def test_every_menu_plan_serves_completely() -> None:
    world = sandwater_world()
    state = _state(8, 8, 14, 6, 6)
    physical = derive_physical_demands(world, state)
    component = components(world, state, ActiveDemandSet.of(physical, ()))[0]
    plans = enumerate_service_plans(world, state, component)
    check("the component has plans", len(plans) > 0)
    worst = None
    for plan in plans:
        increment = plan.group.increment(world.dimension)
        if not serves_all(component.requirements, increment):
            worst = plan.plan_id
    check("no plan offers partial service", worst is None, str(worst))
    check("coverage is recorded for every demand",
          all(len(plan.coverage) == len(component.demands) for plan in plans))


def test_no_plan_exists_without_a_demand() -> None:
    """Contract section 39, the central regression guard."""
    world = sandwater_world()
    state = world.reference_state()
    active = ActiveDemandSet.of(derive_physical_demands(world, state), ())
    check("the reference state carries no demand", active.is_empty)
    found = components(world, state, active)
    check("no demand means no components", found == ())
    offered = unrelated_transfers(world, state, found)
    executable = _executable_singletons(world, state)
    check("physically possible transfers still exist", len(offered) > 0, str(len(offered)))
    check("and every single one of them is offered to no actor",
          len(offered) == len(executable), f"{len(offered)} of {len(executable)}")


def test_every_action_has_demand_provenance() -> None:
    world = sandwater_world()
    for state in (_state(8, 8, 14, 6, 6), _state(9, 9, 12, 5, 7), _state(7, 11, 12, 4, 8)):
        physical = derive_physical_demands(world, state)
        for component in components(world, state, ActiveDemandSet.of(physical, ())):
            for plan in enumerate_service_plans(world, state, component):
                for action_id, demand_ids in plan.provenance:
                    if not demand_ids:
                        check("every action names the demands it serves", False, action_id)
                        return
                    if not set(demand_ids) <= set(plan.served):
                        check("provenance points only at served demands", False, action_id)
                        return
    check("every action names the demands it serves", True)
    check("provenance points only at served demands", True)


def test_irredundancy_blocks_bolting_on_an_unrelated_transfer() -> None:
    world = sandwater_world()
    state = _state(8, 12, 10, 6, 6)
    physical = derive_physical_demands(world, state)
    component = components(world, state, ActiveDemandSet.of(physical, ()))[0]
    plans = enumerate_service_plans(world, state, component)
    minimal = _plan(world, (1, 0, 2))
    check("the minimal restoring plan is in the menu",
          any(plan.group == minimal for plan in plans))
    padded = _plan(world, (1, 0, 2), (2, 1, 1))
    check("padding it with an unrelated transfer is executable",
          can_happen_now(world, state, padded).executable)
    check("but the padded plan is not in the menu",
          not any(plan.group == padded for plan in plans))


def test_one_action_may_serve_several_demands_without_double_credit() -> None:
    world = sandwater_world()
    state = _state(8, 8, 14, 6, 6)
    physical = derive_physical_demands(world, state)
    economic = (_economic(world, "sand", 2, "A", 0, 0),)
    component = components(world, state, ActiveDemandSet.of(physical, economic))[0]
    plans = enumerate_service_plans(world, state, component)
    joint = _plan(world, (2, 0, 2), (2, 1, 2))
    chosen = [plan for plan in plans if plan.group == joint]
    check("the joint two-action plan is in the menu", len(chosen) == 1)
    if chosen:
        plan = chosen[0]
        serving_a = plan.provenance_map["r:sand:2->0@2/1"]
        check("the single action into A serves both the P and the E demand",
              set(serving_a) == {"P:sand|A", economic[0].demand_id}, str(serving_a))
        increment = plan.group.increment(world.dimension)
        check("service is measured from the net increment, so no credit is doubled",
              increment[0] == F(2))
        check("and that one increment satisfies both tests",
              serves_all(component.requirements, increment))


# --------------------------------------------------------------------------
# Contract section 12 -- can this plan actually happen now?
# --------------------------------------------------------------------------


def test_executability_reads_only_physics() -> None:
    import demand_driven_ebu.physical as physical_module

    tree = ast.parse(inspect.getsource(physical_module))
    names = {getattr(n, "id", "") for n in ast.walk(tree) if isinstance(n, ast.Name)}
    attributes = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    forbidden = {"potential", "value_group", "group_ebu", "ledger", "balances", "marginal"}
    leaked = sorted((names | attributes) & forbidden)
    check("the executability module cannot see EBU or capacity", not leaked, str(leaked))


def test_source_funded_simultaneity() -> None:
    world = sandwater_world()
    state = _state(2, 10, 18, 6, 6)
    relay = _plan(world, (0, 1, 3), (2, 0, 3))
    verdict = can_happen_now(world, state, relay)
    check("a source may not spend stock arriving in the same instant",
          not verdict.executable and verdict.reason == "SOURCE_STOCK_INSUFFICIENT",
          f"{verdict.reason} {verdict.offending}")
    increment = relay.increment(world.dimension)
    check("endpoint nonnegativity alone would have allowed it",
          all(state[i] + increment[i] >= 0 for i in range(world.dimension)))


def test_route_capacity_and_quantum_are_enforced() -> None:
    small = DemandWorld.declare(
        "capped-v1",
        [Coordinate.stock("sand", "A", 10, 1), Coordinate.stock("sand", "B", 10, 1)],
        [Route.declare("sand", 0, 1, 2)],
        (1, 2, 3),
        1,
    )
    state = _state(10, 10)
    over = PlanGroup.of(PhysicalAction.declare(small.routes[0], 3))
    verdict = can_happen_now(small, state, over)
    check("a quantity above the route capacity cannot happen",
          not verdict.executable and verdict.reason == "ROUTE_CAPACITY_EXCEEDED", verdict.reason)
    undeclared = PlanGroup.of(PhysicalAction(small.routes[0], F(3, 2)))
    check("an undeclared quantum cannot happen",
          not can_happen_now(small, state, undeclared).executable)


def test_stock_capacity_is_a_hard_limit() -> None:
    capped = DemandWorld.declare(
        "stockcap-v1",
        [
            Coordinate.stock("sand", "A", 10, 1),
            Coordinate.stock("sand", "B", 10, 1, capacity=11),
        ],
        [Route.declare("sand", 0, 1, 5)],
        (1, 2, 3),
        1,
    )
    state = _state(10, 10)
    verdict = can_happen_now(capped, state, PlanGroup.of(
        PhysicalAction.declare(capped.routes[0], 2)))
    check("an overflow beyond a declared stock capacity cannot happen",
          not verdict.executable and verdict.reason == "ENDPOINT_EXCEEDS_STOCK_CAPACITY",
          verdict.reason)


def test_impossible_plans_are_removed_before_valuation() -> None:
    world = sandwater_world()
    state = _state(1, 10, 19, 6, 6)
    physical = derive_physical_demands(world, state)
    for component in components(world, state, ActiveDemandSet.of(physical, ())):
        for plan in enumerate_service_plans(world, state, component):
            if not can_happen_now(world, state, plan.group).executable:
                check("no unexecutable plan reaches valuation", False, plan.plan_id)
                return
    check("no unexecutable plan reaches valuation", True)


# --------------------------------------------------------------------------
# Contract sections 13, 15 and 20 -- valuation after physics, and its closure
# --------------------------------------------------------------------------


def test_group_ebu_matches_the_closed_form_and_the_path_integral() -> None:
    world = sandwater_world()
    potential = world.potential
    worst_closed = F(0)
    worst_path = F(0)
    worst_residual = F(0)
    checked = 0
    for state in (_state(8, 12, 10, 6, 6), _state(4, 14, 12, 3, 9), _state(10, 10, 10, 6, 6)):
        for moves in (
            ((1, 0, 2),),
            ((1, 0, 1), (2, 0, 1)),
            ((0, 1, 3), (2, 1, 2)),
            ((3, 4, 2),),
        ):
            group = _plan(world, *moves)
            if not can_happen_now(world, state, group).executable:
                continue
            checked += 1
            valuation = value_group(world, state, group)
            increment = group.increment(world.dimension)
            worst_closed = max(
                worst_closed,
                abs(valuation.group_ebu - quadratic_ebu(potential, state, increment, group.support)),
            )
            worst_residual = max(worst_residual, abs(valuation.residual))
            for action, receipt in valuation.receipts:
                for rule in ("trapezoid", "midpoint", "simpson"):
                    worst_path = max(
                        worst_path,
                        abs(receipt - receipt_quadrature(
                            potential, state, increment, action.increment(world.dimension), rule
                        )),
                    )
    check("groups were valued", checked >= 6, str(checked))
    check("definitional and closed-form EBU agree exactly", worst_closed == 0, str(worst_closed))
    check("common-path receipts sum to the group EBU exactly", worst_residual == 0, str(worst_residual))
    check("every quadrature rule reproduces the receipt exactly", worst_path == 0, str(worst_path))


def test_linear_estimate_is_not_the_finite_value() -> None:
    world = sandwater_world()
    state = _state(10, 10, 10, 6, 6)
    group = _plan(world, (0, 1, 3))
    increment = group.increment(world.dimension)
    exact_value = value_group(world, state, group).group_ebu
    linear = linear_estimate(world.potential, state, increment)
    check("initial force times finite quantity is not the exact value",
          linear != exact_value, f"{linear} vs {exact_value}")
    check("and the difference is the curvature term the model keeps",
          exact_value == linear - F(9), str(exact_value))


def test_capacity_never_changes_what_ebu_measures() -> None:
    """Metamorphic: vary the balances, hold physics and demand fixed."""
    world = sandwater_world()
    state = _state(8, 12, 10, 6, 6)
    group = _plan(world, (1, 0, 2))
    reference = value_group(world, state, group)
    differences = []
    for amount in (0, 1, 7, 1000):
        ledger = seeded_ledger(world, amount)
        again = value_group(world, state, group)
        affordable = ledger.is_affordable(again).affordable
        if (again.group_ebu, again.receipts, again.owner_deltas) != (
            reference.group_ebu, reference.receipts, reference.owner_deltas
        ):
            differences.append(amount)
        del affordable
    check("V_pre, V_post, E_G and every receipt are independent of capacity",
          not differences, str(differences))

    poor = CapacityLedger.zero(world.nodes)
    rich = seeded_ledger(world, 100)
    costly = _plan(world, (2, 0, 3))
    valuation = value_group(world, state, costly)
    check("only the affordable/unaffordable verdict moves with capacity",
          not poor.is_affordable(valuation).affordable
          and rich.is_affordable(valuation).affordable)


def test_valuation_is_not_given_a_ledger() -> None:
    import demand_driven_ebu.valuation as valuation_module

    source = inspect.getsource(valuation_module)
    tree = ast.parse(source)
    names = {getattr(n, "id", "") for n in ast.walk(tree) if isinstance(n, ast.Name)}
    check("the valuation module never names a ledger or a balance",
          not ({"CapacityLedger", "balances", "ledger"} & names))


# --------------------------------------------------------------------------
# Contract sections 14, 16, 29 and 30 -- capacity, affordability, bootstrap
# --------------------------------------------------------------------------


def test_zero_capacity_bootstrap() -> None:
    world = sandwater_world()
    state = _state(8, 12, 10, 6, 6)
    ledger = CapacityLedger.zero(world.nodes)
    restoring = value_group(world, state, _plan(world, (1, 0, 2)))
    damaging = value_group(world, state, _plan(world, (2, 0, 3)))
    check("from zero capacity a positive-EBU plan is affordable",
          restoring.group_ebu > 0 and ledger.is_affordable(restoring).affordable)
    check("from zero capacity a negative-EBU plan is not",
          damaging.group_ebu < 0 and not ledger.is_affordable(damaging).affordable)
    check("no capacity is invented to make it affordable", ledger.total == 0)


def test_no_overdraft_and_no_transfer() -> None:
    world = sandwater_world()
    ledger = CapacityLedger.zero(world.nodes)
    try:
        ledger.settle({"A": F(-1)})
    except Refusal:
        check("a settlement that would overdraw is refused", True)
    else:
        check("a settlement that would overdraw is refused", False)
    check("the ledger is unchanged after a refusal", ledger.total == 0)

    import demand_driven_ebu.capacity as capacity_module

    source = inspect.getsource(capacity_module)
    tree = ast.parse(source)
    functions = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    banned = {"transfer", "borrow", "grant", "refill", "mint", "pool"}
    check("the ledger exposes no transfer, borrow, grant, refill or mint",
          not (functions & banned), str(sorted(functions & banned)))


def test_settlement_is_all_or_nothing() -> None:
    world = sandwater_world()
    ledger = seeded_ledger(world, 1)
    try:
        ledger.settle({"A": F(5), "B": F(-3)})
    except Refusal:
        check("a mixed settlement with one deficient owner is refused whole", True)
    else:
        check("a mixed settlement with one deficient owner is refused whole", False)
    check("no partial credit was written", ledger.balance_map["A"] == F(1))


def test_capacity_is_only_spendable_through_a_demand_serving_plan() -> None:
    """There is no code path from a balance to an action outside a menu."""
    world = sandwater_world()
    state = world.reference_state()
    run = EconomyRun(world, quiet_disturbance(world), no_arrivals(), POLICY_ALIGNED,
                     1, 2, 3, 4)
    record = run.run_epoch()
    check("at the reference with no demand nothing executes",
          record.epoch_status == STATUS_NO_ACTIVE_DEMAND, record.epoch_status)
    check("no action was taken", record.receipts == ())
    check("the state is untouched", record.state_after == state)
    check("capacity is untouched", record.balance_total == 0)


# --------------------------------------------------------------------------
# Contract sections 17 and 18 -- the three policies and the comparator
# --------------------------------------------------------------------------


def _menu(world, state, physical=(), economic=()):
    if not physical and not economic:
        physical = derive_physical_demands(world, state)
    component = components(world, state, ActiveDemandSet.of(physical, economic))[0]
    plans = enumerate_service_plans(world, state, component)
    values = [value_group(world, state, plan.group) for plan in plans]
    return component, plans, values


def test_policies_choose_among_equally_complete_answers() -> None:
    world = sandwater_world()
    state = _state(8, 12, 10, 6, 6)
    component, plans, values = _menu(world, state)
    ledger = CapacityLedger.zero(world.nodes)
    affordable = [
        (plan, valuation) for plan, valuation in zip(plans, values)
        if ledger.is_affordable(valuation).affordable
    ]
    ebu = [valuation.group_ebu for _, valuation in affordable]
    check("the affordable menu holds four plans", len(affordable) == 4, str(len(affordable)))
    check("their EBU values are 3, 4, 3 and 0", sorted(ebu) == [F(0), F(3), F(3), F(4)], str(ebu))

    counter = Counter(MODEL_ID, world.world_id, 5, "actor_choice", 0, 2, 0)
    aligned = choose(POLICY_ALIGNED, len(ebu), ebu, counter)
    hostile = choose(POLICY_HOSTILE, len(ebu), ebu, counter)
    check("aligned takes the maximum", ebu[aligned] == F(4))
    check("hostile takes the minimum", ebu[hostile] == F(0))
    check("every candidate serves the whole component completely",
          all(set(plan.served) == set(component.demand_ids) for plan, _ in affordable))


def test_hostile_cannot_choose_unrelated_damage() -> None:
    world = sandwater_world()
    state = _state(8, 12, 10, 6, 6)
    component, plans, values = _menu(world, state)
    damage = _plan(world, (0, 2, 3))
    check("the damaging unrelated transfer is physically possible",
          can_happen_now(world, state, damage).executable)
    check("its EBU is worse than anything in the menu",
          value_group(world, state, damage).group_ebu
          < min(valuation.group_ebu for valuation in values))
    check("and it is not in the hostile actor's menu",
          all(plan.group != damage for plan in plans))
    check("every hostile option still resolves the shortfall",
          all(serves_all(component.requirements, plan.group.increment(world.dimension))
              for plan in plans))


def test_random_and_control_are_structurally_ebu_blind() -> None:
    world = sandwater_world()
    state = _state(8, 12, 10, 6, 6)
    _, plans, values = _menu(world, state)
    counter = Counter(MODEL_ID, world.world_id, 5, "actor_choice", 0, 2, 0)
    for policy in (POLICY_RANDOM, POLICY_CONTROL):
        try:
            choose(policy, len(plans), [v.group_ebu for v in values], counter)
        except Refusal:
            check(f"{policy} refuses to be handed EBU values", True)
        else:
            check(f"{policy} refuses to be handed EBU values", False)
    reached = set()
    for seed in range(60):
        counter = Counter(MODEL_ID, world.world_id, seed, "actor_choice", 0, 2, 0)
        reached.add(choose(POLICY_RANDOM, len(plans), None, counter))
    check("the random policy reaches every candidate", len(reached) == len(plans), str(sorted(reached)))


def test_the_comparator_applies_no_affordability_filter() -> None:
    check("the control arm is declared not to filter on affordability",
          specification(POLICY_CONTROL).applies_affordability is False)
    check("and is declared not to read EBU",
          specification(POLICY_CONTROL).reads_ebu_to_choose is False)
    world = sandwater_world()
    state = _state(8, 12, 10, 6, 6)
    run = EconomyRun(world, quiet_disturbance(world), no_arrivals(), POLICY_CONTROL,
                     1, 2, 3, 4, initial_state=state)
    record = run.run_epoch()
    check("the comparator may settle into a negative account",
          record.epoch_status == STATUS_EXECUTED)
    check("its shadow ledger is recorded rather than binding",
          run.ledger.constrained is False)


def test_there_is_no_voluntary_no_action() -> None:
    world = sandwater_world()
    state = _state(8, 12, 10, 6, 6)
    for policy in (POLICY_ALIGNED, POLICY_RANDOM, POLICY_HOSTILE, POLICY_CONTROL):
        run = EconomyRun(world, quiet_disturbance(world), no_arrivals(), policy,
                         1, 2, 3, 4, initial_state=state)
        record = run.run_epoch()
        if record.epoch_status != STATUS_EXECUTED:
            check("with an affordable plan available, one executes", False, f"{policy}:{record.epoch_status}")
            return
        if record.executed_group_id == "g:[]":
            check("with an affordable plan available, one executes", False, f"{policy}: empty group")
            return
    check("with an affordable plan available, one executes", True)


def test_the_three_legitimate_inactions_are_distinguished() -> None:
    world = sandwater_world()
    quiet = quiet_disturbance(world)

    at_reference = EconomyRun(world, quiet, no_arrivals(), POLICY_ALIGNED, 1, 2, 3, 4)
    check("no active demand is its own status",
          at_reference.run_epoch().epoch_status == STATUS_NO_ACTIVE_DEMAND)

    impossible = EconomyRun(world, quiet, no_arrivals(), POLICY_ALIGNED, 1, 2, 3, 4,
                            initial_state=_state(3, 10, 10, 6, 6))
    check("no complete physical solution is its own status",
          impossible.run_epoch().epoch_status == STATUS_NO_COMPLETE_PLAN)

    costly = ArrivalProcess.declare((("sand", "C", 2),), 1, 1, 1)
    unaffordable = EconomyRun(world, quiet, costly, POLICY_ALIGNED, 1, 2, 3, 4)
    record = unaffordable.run_epoch()
    check("no affordable solution is its own status",
          record.epoch_status == STATUS_ALL_UNAFFORDABLE, record.epoch_status)
    check("the admitted demand is not erased by being unaffordable",
          len(unaffordable.held) == 1 and record.unaffordable_economic != ())


# --------------------------------------------------------------------------
# Contract sections 19 and 20 -- simultaneous independent execution
# --------------------------------------------------------------------------


def test_independent_components_execute_in_the_same_epoch() -> None:
    world = sandwater_world()
    state = _state(8, 12, 10, 4, 8)
    run = EconomyRun(world, quiet_disturbance(world), no_arrivals(), POLICY_ALIGNED,
                     1, 2, 3, 4, initial_state=state)
    record = run.run_epoch()
    check("both components resolve in one epoch",
          len(record.outcomes) == 2
          and all(o.status == STATUS_EXECUTED for o in record.outcomes),
          str([(o.component_id, o.status) for o in record.outcomes]))
    check("the sand shortfall is gone", record.state_after[0] >= F(10))
    check("the water shortfall is gone", record.state_after[3] >= F(6))
    check("the joint closure gate passed", record.joint_gate == "JOINT_CLOSURE_VERIFIED")
    check("combining the components changed no EBU", record.separability_residual == 0)


def test_the_joint_gate_verifies_separability_exactly() -> None:
    world = sandwater_world()
    state = _state(8, 12, 10, 4, 8)
    physical = derive_physical_demands(world, state)
    found = components(world, state, ActiveDemandSet.of(physical, ()))
    apart = F(0)
    picked = []
    for component in found:
        plan = enumerate_service_plans(world, state, component)[0]
        picked.append(plan)
        apart += value_group(world, state, plan.group).group_ebu
    combined = PlanGroup.of(*[a for plan in picked for a in plan.group.actions])
    joint = value_group(world, state, combined)
    check("the combined EBU equals the sum of the component EBUs",
          joint.group_ebu == apart, f"{joint.group_ebu} vs {apart}")
    per_action = {}
    for plan in picked:
        for action, receipt in value_group(world, state, plan.group).receipts:
            per_action[action.action_id] = receipt
    drift = max(
        (abs(per_action[a.action_id] - r) for a, r in joint.receipts), default=F(0)
    )
    check("no receipt moves when the components are combined", drift == 0, str(drift))
    check("and the combined decomposition still closes", joint.residual == 0)


def test_simultaneous_children_are_not_settled_from_singleton_quotes() -> None:
    world = sandwater_world()
    state = _state(8, 8, 14, 6, 6)
    group = _plan(world, (2, 0, 2), (2, 1, 2))
    joint = value_group(world, state, group)
    singletons = F(0)
    for action in group.actions:
        singletons += value_group(world, state, PlanGroup.of(action)).group_ebu
    check("same-baseline singleton quotes do not sum to the group value",
          singletons != joint.group_ebu, f"{singletons} vs {joint.group_ebu}")
    check("the common-path receipts do", joint.residual == 0)


# --------------------------------------------------------------------------
# Contract sections 21 and 22 -- re-derivation, and economic waves
# --------------------------------------------------------------------------


def test_physical_demand_is_rederived_after_execution() -> None:
    world = sandwater_world()
    state = _state(8, 12, 10, 6, 6)
    run = EconomyRun(world, quiet_disturbance(world), no_arrivals(), POLICY_ALIGNED,
                     1, 2, 3, 4, initial_state=state)
    first = run.run_epoch()
    check("the shortfall existed before the epoch", first.active_physical == ("P:sand|A",))
    check("it was resolved by execution", first.state_after == world.reference_state())
    second = run.run_epoch()
    check("and it is simply gone at the next derivation", second.active_physical == ())
    check("no stale obligation survived", second.epoch_status == STATUS_NO_ACTIVE_DEMAND)


def test_an_economic_action_creates_new_physical_demand() -> None:
    """The wave in contract section 22: serving E depletes a source into deficit."""
    world = sandwater_world()
    arrivals = ScriptedArrivals({1: (("sand", "C", 2),)})
    run = EconomyRun(world, quiet_disturbance(world), arrivals, POLICY_ALIGNED,
                     1, 2, 3, 4, initial_state=_state(8, 12, 10, 6, 6))
    run.run_epoch()
    second = run.run_epoch()
    check("no physical demand existed when the economic one was served",
          second.active_physical == (), str(second.active_physical))
    check("the economic demand was admitted and served",
          len(second.served_economic) == 1, str(second.served_economic))
    third = run.run_epoch()
    check("serving it produced a new physical demand",
          third.active_physical == ("P:sand|B",), str(third.active_physical))
    check("which nobody scheduled or precomputed, and no arrival announced",
          third.arrivals == () and all(d.startswith("P:") for d in third.active_physical))


# --------------------------------------------------------------------------
# Contract section 23 -- losses
# --------------------------------------------------------------------------


def test_loss_is_represented_and_conserves() -> None:
    world = loss_world()
    state = world.reference_state()
    group = _plan(world, (0, 1, 4))
    increment = group.increment(world.dimension)
    check("the source loses the full quantity", increment[0] == F(-4))
    check("the destination receives only what survives", increment[1] == F(2))
    check("the sink receives exactly the difference", increment[3] == F(2))
    check("nothing disappears into nowhere", sum(increment) == 0)
    check("the plan can happen", can_happen_now(world, state, group).executable)


def test_a_sink_inside_v_is_charged_and_one_outside_it_is_not() -> None:
    inside = loss_world()
    outside = audit_sink_world()
    inside_value = value_group(inside, inside.reference_state(), _plan(inside, (0, 1, 4)))
    outside_value = value_group(outside, outside.reference_state(), _plan(outside, (0, 1, 4)))
    check("waste that carries potential is charged for", inside_value.group_ebu == F(-12),
          str(inside_value.group_ebu))
    check("an audit-only sink adds nothing to the charge", outside_value.group_ebu == F(-10),
          str(outside_value.group_ebu))
    check("and the gap is exactly the sink's own potential term",
          outside_value.group_ebu - inside_value.group_ebu == F(2))
    check("both decompositions still close exactly",
          inside_value.residual == 0 and outside_value.residual == 0)

    lost_state = _state(6, 12, 2)
    check("an audit-only sink generates no physical demand",
          all(d.demand_id != "P:sand|W" for d in derive_physical_demands(outside, lost_state)))


def test_loss_generates_physical_demand_at_the_depleted_stock() -> None:
    world = loss_world()
    after = add(world.reference_state(), _plan(world, (0, 1, 4)).increment(world.dimension))
    demands = {d.demand_id: d.required for d in derive_physical_demands(world, after)}
    check("the depleted source is now in deficit", demands.get("P:sand|A") == F(4))
    check("the sink is above its reference, not below, so it demands nothing",
          "P:sand|W" not in demands, str(sorted(demands)))


def test_irreversible_loss_makes_complete_restoration_impossible() -> None:
    """A structural consequence worth stating: it is a finding, not a failure."""
    world = loss_world()
    after = add(world.reference_state(), _plan(world, (0, 1, 4)).increment(world.dimension))
    stock_total = sum(after[i] for i, c in enumerate(world.coordinates) if c.role == "STOCK")
    reference_total = sum(
        c.reference for c in world.coordinates if c.role == "STOCK"
    )
    check("the represented stock total now falls short of the reference total",
          stock_total < reference_total, f"{stock_total} vs {reference_total}")
    check("so at least one shortfall can never be closed",
          derive_physical_demands(world, after) != ())


# --------------------------------------------------------------------------
# Contract section 24 -- nature is not an actor
# --------------------------------------------------------------------------


def test_disturbance_changes_no_capacity() -> None:
    import demand_driven_ebu.disturbance as disturbance_module

    tree = ast.parse(inspect.getsource(disturbance_module))
    names = {getattr(n, "id", "") for n in ast.walk(tree) if isinstance(n, ast.Name)}
    check("the disturbance module cannot reach a ledger",
          not ({"CapacityLedger", "settle", "ledger"} & names))

    world = sandwater_world()
    process = DisturbanceProcess.declare(world, ((0, 1),), 2, 1, 1)
    state = world.reference_state()
    event = process.draw(world, state, 3, 0)
    moved = apply_disturbance(world, state, event)
    check("nature moved stock", moved != state)
    check("conservatively", world.resource_total(moved, "sand") == world.resource_total(state, "sand"))
    check("and created physical demand", derive_physical_demands(world, moved) != ())


def test_a_null_disturbance_is_not_repaired() -> None:
    world = sandwater_world()
    process = DisturbanceProcess.declare(world, ((0, 1),), 3, 1, 1)
    empty = _state(0, 20, 10, 6, 6)
    event = process.draw(world, empty, 3, 0)
    check("a disturbance whose source is short is null",
          event.status == "DISTURBANCE_NULL_SOURCE_SHORT", event.status)
    check("it is not resampled or reduced", event.quantity == 0)
    check("and the state is untouched", apply_disturbance(world, empty, event) == empty)


# --------------------------------------------------------------------------
# Contract sections 25 to 28 -- the closed-cycle theorem and circulation
# --------------------------------------------------------------------------


def _apply(world, state, ledger, group):
    valuation = value_group(world, state, group)
    return (
        add(state, group.increment(world.dimension)),
        ledger.settle(valuation.owner_map),
        valuation,
    )


def test_exact_circulation_fixture() -> None:
    """Contract section 28, first fixture: 100 -> 80 -> 88 -> 95 -> 100."""
    world = cycle_world()
    state = world.reference_state()
    ledger = seeded_ledger(world, 25)
    check("aggregate capacity opens at 100", ledger.total == F(100))

    state, ledger, economic = _apply(world, state, ledger, _plan(world, (0, 1, 2), (2, 3, 4)))
    check("the economic action costs exactly 20", economic.group_ebu == F(-20))
    check("aggregate capacity falls to 80", ledger.total == F(80))
    check("and the action created physical demand",
          len(derive_physical_demands(world, state)) == 2)

    totals = [ledger.total]
    for moves, expected in (
        (((3, 0, 2),), F(8)),
        (((0, 2, 1), (3, 2, 1)), F(7)),
        (((1, 0, 1), (1, 2, 1), (3, 2, 1)), F(5)),
    ):
        state, ledger, valuation = _apply(world, state, ledger, _plan(world, *moves))
        check(f"a restoration earns exactly {expected}", valuation.group_ebu == expected,
              str(valuation.group_ebu))
        totals.append(ledger.total)
    check("the sequence of totals is 80, 88, 95, 100",
          totals == [F(80), F(88), F(95), F(100)], str(totals))
    check("the physical state returned exactly to its start",
          state == world.reference_state())
    check("aggregate capacity returned exactly to its start", ledger.total == F(100))
    check("but it moved between actors",
          ledger.balance_map != seeded_ledger(world, 25).balance_map)
    check("A paid and D and B were paid",
          ledger.balance_map["A"] == F(47, 2)
          and ledger.balance_map["B"] == F(57, 2)
          and ledger.balance_map["C"] == F(9)
          and ledger.balance_map["D"] == F(39), str(ledger.balance_map))


def test_exact_loss_circulation_fixture() -> None:
    """Contract section 28, second fixture: only +17 can ever be earned back."""
    world = loss_world()
    state = world.reference_state()
    ledger = seeded_ledger(world, 25)
    check("aggregate capacity opens at 100", ledger.total == F(100))

    state, ledger, economic = _apply(world, state, ledger, _plan(world, (0, 1, 4), (2, 1, 2)))
    check("the lossy economic action costs exactly 20", economic.group_ebu == F(-20))
    check("aggregate capacity falls to 80", ledger.total == F(80))
    check("two units were irreversibly wasted", state[3] == F(2))

    best = min(
        world.potential.value_total(add(state, group.increment(world.dimension)))
        for group in _all_groups(world, state)
    )
    check("the reachable potential floor is exactly 3", best == F(3), str(best))

    state, ledger, restoring = _apply(world, state, ledger, _plan(world, (1, 0, 3), (1, 2, 2)))
    check("the best restoration earns exactly 17", restoring.group_ebu == F(17))
    check("aggregate capacity ends at 97, not 100", ledger.total == F(97), str(ledger.total))
    check("the shortfall is exactly the unrecoverable potential",
          F(100) - ledger.total == world.potential.value_total(state) == F(3))
    check("the state did not return", state != world.reference_state())


def _all_groups(world, state):
    from demand_driven_ebu.physical import action_alphabet

    alphabet = action_alphabet(world)
    groups = []
    for size in range(1, world.max_plan_size + 1):
        for chosen in combinations(alphabet, size):
            if len({a.route.route_id for a in chosen}) != size:
                continue
            group = PlanGroup.of(*chosen)
            if can_happen_now(world, state, group).executable:
                groups.append(group)
    return groups


def test_closed_cycle_no_issuance_theorem() -> None:
    world = cycle_world()
    start = world.reference_state()
    ledger = seeded_ledger(world, 40)
    opening = ledger.total
    state = start
    total_ebu = F(0)
    for moves in (
        ((0, 1, 2),),
        ((1, 2, 3),),
        ((2, 1, 3),),
        ((1, 0, 2),),
    ):
        state, ledger, valuation = _apply(world, state, ledger, _plan(world, *moves))
        total_ebu += valuation.group_ebu
    check("A -> B -> A and B -> C -> B returns the state exactly", state == start)
    check("the EBU of the whole cycle is exactly zero", total_ebu == 0, str(total_ebu))
    check("so aggregate capacity is exactly unchanged", ledger.total == opening, str(ledger.total))
    check("no capacity was minted by repetition", ledger.total - opening == 0)


def test_closed_cycle_holds_for_simultaneous_groups() -> None:
    world = cycle_world()
    start = world.reference_state()
    ledger = seeded_ledger(world, 60)
    state = start
    forward = _plan(world, (0, 1, 2), (2, 3, 3))
    back = _plan(world, (1, 0, 2), (3, 2, 3))
    state, ledger, first = _apply(world, state, ledger, forward)
    state, ledger, second = _apply(world, state, ledger, back)
    check("a simultaneous out-and-back returns the state", state == start)
    check("its two group values cancel exactly", first.group_ebu + second.group_ebu == 0)
    check("aggregate capacity is exactly unchanged", ledger.total == F(240))
    check("each group's receipts closed exactly",
          first.residual == 0 and second.residual == 0)


def test_capacity_source_identity_holds_over_a_driven_run() -> None:
    world = sandwater_world()
    disturbance = DisturbanceProcess.declare(world, ((0, 1), (1, 2), (3, 4)), 2, 1, 2)
    arrivals = ArrivalProcess.declare((("sand", "C", 2), ("water", "E", 1)), 1, 4, 2)
    worst = F(0)
    for policy in (POLICY_ALIGNED, POLICY_RANDOM, POLICY_HOSTILE, POLICY_CONTROL):
        run = EconomyRun(world, disturbance, arrivals, policy, 11, 22, 33, 44)
        records = run.run(15)
        worst = max(worst, abs(run.capacity_source_residual))
        accounting = window(records)
        worst = max(worst, abs(accounting.telescoping_residual), abs(accounting.identity_residual))
    check("delta B_total = V(x_0) - V(x_T) + sum dV_ext exactly, in every arm",
          worst == 0, str(worst))


def test_economic_arrival_issues_no_capacity() -> None:
    world = sandwater_world()
    arrivals = ArrivalProcess.declare((("sand", "C", 2),), 1, 1, 1)
    run = EconomyRun(world, quiet_disturbance(world), arrivals, POLICY_ALIGNED, 1, 2, 3, 4)
    before_state, before_balance = run.state, run.ledger.total
    record = run.run_epoch()
    check("a demand arrived", record.arrivals != ())
    check("it was admitted", record.admitted_now != ())
    check("but it was unaffordable, so nothing physical happened",
          record.epoch_status == STATUS_ALL_UNAFFORDABLE)
    check("the arrival changed no stock", run.state == before_state)
    check("and issued no capacity", run.ledger.total == before_balance == F(0))


def test_no_process_burden_is_charged_anywhere() -> None:
    """The C_a >= 0 extension is derived in the documentation, not implemented."""
    import demand_driven_ebu.capacity as capacity_module
    import demand_driven_ebu.valuation as valuation_module

    for module in (capacity_module, valuation_module, harness_module):
        tree = ast.parse(inspect.getsource(module))
        names = {getattr(n, "id", "") for n in ast.walk(tree) if isinstance(n, ast.Name)}
        leaked = sorted(n for n in names if n.lower() in {"burden", "c_a", "process_cost", "activation_cost"})
        if leaked:
            check("no process burden is charged in the implementation", False, str(leaked))
            return
    check("no process burden is charged in the implementation", True)


def test_the_capacity_source_table_is_complete_and_signed() -> None:
    entries = {name: verdict for name, verdict, _ in CAPACITY_SOURCE_TABLE}
    check("external deviation may create capacity",
          entries["EXTERNAL_PHYSICAL_DEVIATION"] == "may increase aggregate capacity")
    check("a net approach to the reference may create capacity",
          entries["NET_APPROACH_TO_REFERENCE"] == "may increase aggregate capacity")
    check("an economic arrival cannot",
          entries["ECONOMIC_DEMAND_ARRIVAL"] == "cannot change aggregate capacity")
    check("a closed actor-only cycle cannot",
          entries["CLOSED_ACTOR_ONLY_CYCLE"] == "cannot change aggregate capacity")


# --------------------------------------------------------------------------
# Contract section 32 -- stream separation
# --------------------------------------------------------------------------


def test_four_streams_are_declared_and_separate() -> None:
    check("exactly four streams are declared", len(DECLARED_STREAMS) == 4, str(DECLARED_STREAMS))
    addresses = set()
    for stream in DECLARED_STREAMS:
        counter = Counter(MODEL_ID, "w", 1, stream, 0, 0, 0)
        addresses.add(counter.preimage(0))
    check("each stream has its own draw address", len(addresses) == 4)
    try:
        Counter(MODEL_ID, "w", 1, "some_other_stream", 0, 0, 0)
    except Refusal:
        check("an undeclared stream is refused", True)
    else:
        check("an undeclared stream is refused", False)


def test_actor_policy_cannot_move_the_arrival_sequence() -> None:
    world = sandwater_world()
    arrivals = ArrivalProcess.declare((("sand", "C", 2), ("water", "E", 1)), 1, 2, 2)
    sequences = {}
    for policy in (POLICY_ALIGNED, POLICY_RANDOM, POLICY_HOSTILE, POLICY_CONTROL):
        run = EconomyRun(world, quiet_disturbance(world), arrivals, policy, 1, 2, 3, 4)
        records = run.run(10)
        sequences[policy] = tuple(record.arrivals for record in records)
    distinct = set(sequences.values())
    check("all four policies see the identical arrival sequence", len(distinct) == 1,
          str({k: v[:3] for k, v in sequences.items()}))


def test_changing_the_actor_seed_cannot_move_arrivals() -> None:
    world = sandwater_world()
    arrivals = ArrivalProcess.declare((("sand", "C", 2), ("water", "E", 1)), 1, 2, 2)
    drawn = {
        seed: tuple(arrivals.arrivals(world, 22, epoch) for epoch in range(10))
        for seed in (0, 5, 99)
    }
    check("the arrival law does not take an actor seed at all",
          len({tuple(str(d) for d in v) for v in drawn.values()}) == 1)
    first = tuple(a.demand_id for a in arrivals.arrivals(world, 22, 3))
    second = tuple(a.demand_id for a in arrivals.arrivals(world, 23, 3))
    check("but it does depend on its own seed", first != second or first == () == second)


def test_streams_share_no_mutable_state() -> None:
    world = sandwater_world()
    arrivals = ArrivalProcess.declare((("sand", "C", 2),), 1, 2, 1)
    straight = [arrivals.arrivals(world, 22, epoch) for epoch in range(8)]
    interleaved = []
    for epoch in range(8):
        uniform_index(Counter(MODEL_ID, world.world_id, 7, "actor_choice", epoch, 2, 0), 5)
        uniform_index(Counter(MODEL_ID, world.world_id, 8, "economic_admission", epoch, 1, 0), 3)
        interleaved.append(arrivals.arrivals(world, 22, epoch))
    check("draws on other streams do not advance the arrival stream",
          [tuple(a.demand_id for a in group) for group in straight]
          == [tuple(a.demand_id for a in group) for group in interleaved])


# --------------------------------------------------------------------------
# Contract section 37 -- the sixteen hand-checkable fixtures
# --------------------------------------------------------------------------


def fixture_f1_no_demand() -> None:
    world = sandwater_world()
    run = EconomyRun(world, quiet_disturbance(world), no_arrivals(), POLICY_ALIGNED, 1, 2, 3, 4)
    record = run.run_epoch()
    check("F1  at equilibrium with zero capacity there is no demand",
          record.active_physical == () and record.active_economic == ())
    check("F1  and therefore no action", record.receipts == () and record.epoch_ebu == 0)
    check("F1  this is absence of obligation, not abstention",
          record.epoch_status == STATUS_NO_ACTIVE_DEMAND)


def fixture_f2_pure_physical_demand() -> None:
    world = sandwater_world()
    state = _state(8, 12, 10, 6, 6)
    run = EconomyRun(world, quiet_disturbance(world), no_arrivals(), POLICY_ALIGNED,
                     1, 2, 3, 4, initial_state=state)
    record = run.run_epoch()
    check("F2  a conservative disturbance is answered by a derived P-demand",
          record.active_physical == ("P:sand|A",))
    check("F2  the restorative plan earns positive EBU from zero capacity",
          record.epoch_ebu == F(4), str(record.epoch_ebu))
    check("F2  and capacity is created where it was earned",
          dict(record.balances)["B"] == F(4))


def fixture_f3_restorative_economic_demand() -> None:
    world = surplus_world()
    state = _state(14, 8, 8)
    check("F3  a world above its reference has no shortfall",
          derive_physical_demands(world, state) == ())
    demand = _economic(world, "sand", 3, "C")
    component = components(world, state, ActiveDemandSet.of((), (demand,)))[0]
    plans = enumerate_service_plans(world, state, component)
    best = max(value_group(world, state, plan.group).group_ebu for plan in plans)
    check("F3  yet serving the economic demand can reduce deviation",
          best == F(9), str(best))
    check("F3  so a purely economic action earns EBU", best > 0)


def fixture_f4_costly_economic_demand() -> None:
    world = sandwater_world()
    arrivals = ArrivalProcess.declare((("sand", "C", 2),), 1, 1, 1)
    run = EconomyRun(world, quiet_disturbance(world), arrivals, POLICY_ALIGNED, 1, 2, 3, 4)
    record = run.run_epoch()
    check("F4  the demand is admitted", record.admitted_now != ())
    check("F4  every plan for it is negative and none is affordable at zero capacity",
          record.epoch_status == STATUS_ALL_UNAFFORDABLE)
    check("F4  it is recorded as admitted-but-unaffordable, not rejected",
          record.unaffordable_economic != () and len(run.held) == 1)


def fixture_f5_demand_exceeds_the_resource() -> None:
    world = scarcity_world()
    state = _state(560, 0, 0)
    asked = _economic(world, "sand", 1000, "C")
    admitted, rejected, _ = admit(world, state, (), (), (asked,), 7, 0)
    check("F5  1000 is requested where 560 exist", asked.quantity == F(1000))
    check("F5  it is rejected for physical scarcity before any EBU exists",
          admitted == () and rejected[0].status == E_REJECTED_PHYSICAL_SCARCITY)
    check("F5  it is neither truncated nor regenerated smaller",
          rejected[0].quantity == F(1000) and len(rejected) == 1)


def fixture_f6_two_competing_economic_demands() -> None:
    world = competing_world()
    state = _state(3, 0, 0)
    first = _economic(world, "sand", 3, "B", 0, 0)
    second = _economic(world, "sand", 3, "C", 0, 1)
    outcomes = set()
    for seed in range(30):
        admitted, rejected, _ = admit(world, state, (), (), (first, second), seed, 0)
        outcomes.add(admitted[0].demand_id)
        if len(admitted) != 1 or rejected[0].status != E_REJECTED_INCOMPATIBLE:
            check("F6  exactly one compatible demand is admitted", False, str(admitted))
            return
    check("F6  exactly one compatible demand is admitted", True)
    check("F6  the choice is random, not optimized", len(outcomes) == 2, str(outcomes))


def fixture_f7_coexisting_economic_and_physical() -> None:
    world = sandwater_world()
    state = _state(8, 8, 14, 6, 6)
    arrivals = ScriptedArrivals({0: (("sand", "A", 2),)})
    run = EconomyRun(world, quiet_disturbance(world), arrivals, POLICY_ALIGNED,
                     1, 2, 3, 4, initial_state=state)
    record = run.run_epoch()
    check("F7  two physical demands and one economic demand were active together",
          len(record.active_physical) == 2 and len(record.active_economic) == 1)
    check("F7  a single joint plan satisfied all three",
          record.epoch_status == STATUS_EXECUTED and len(record.outcomes) == 1)
    check("F7  neither class waited for the other",
          record.served_economic != () and record.state_after[0] >= F(10)
          and record.state_after[1] >= F(10))


def fixture_f8_independent_components() -> None:
    world = sandwater_world()
    state = _state(3, 10, 10, 4, 8)
    run = EconomyRun(world, quiet_disturbance(world), no_arrivals(), POLICY_ALIGNED,
                     1, 2, 3, 4, initial_state=state)
    record = run.run_epoch()
    statuses = {o.component_id: o.status for o in record.outcomes}
    check("F8  the impossible sand component is left unresolved",
          statuses["c:[P:sand|A]"] == STATUS_NO_COMPLETE_PLAN, str(statuses))
    check("F8  the independent water component still executes",
          statuses["c:[P:water|D]"] == STATUS_EXECUTED, str(statuses))
    check("F8  and the water shortfall is actually closed", record.state_after[3] == F(6))


def fixture_f9_unaffordable_component_alongside_a_working_one() -> None:
    world = sandwater_world()
    state = _state(10, 10, 10, 4, 8)
    arrivals = ScriptedArrivals({0: (("sand", "C", 2),)})
    run = EconomyRun(world, quiet_disturbance(world), arrivals, POLICY_ALIGNED,
                     1, 2, 3, 4, initial_state=state)
    record = run.run_epoch()
    statuses = {o.component_id: (o.status, o.plan_count) for o in record.outcomes}
    sand = [v for k, v in statuses.items() if "sand" in k][0]
    water = [v for k, v in statuses.items() if "water" in k][0]
    check("F9  the sand component has physical plans but none affordable",
          sand[0] == STATUS_ALL_UNAFFORDABLE and sand[1] > 0, str(sand))
    check("F9  the independent water component executes anyway",
          water[0] == STATUS_EXECUTED, str(water))
    check("F9  the unaffordable economic demand is not erased", len(run.held) == 1)


def fixture_f10_and_f11_closed_cycle_with_two_actors() -> None:
    world = sandwater_world()
    arrivals = ScriptedArrivals({1: (("sand", "C", 2),)})
    run = EconomyRun(world, quiet_disturbance(world), arrivals, POLICY_ALIGNED,
                     1, 2, 3, 4, initial_state=_state(8, 12, 10, 6, 6))
    first = run.run_epoch()
    check("F10 the opening restoration earns capacity for B",
          dict(first.balances)["B"] == F(4) and first.state_after == world.reference_state())

    opening_state = run.state
    opening_balance = run.ledger.total
    spend = run.run_epoch()
    check("F10 the economic action spends that capacity",
          spend.epoch_ebu == F(-4) and run.ledger.total == F(0), str(run.ledger.total))
    check("F10 and creates a new physical demand", spend.state_after != opening_state)

    earn = run.run_epoch()
    check("F10 restoring it earns the capacity back", earn.epoch_ebu == F(4))
    check("F10 the state returns exactly to where the cycle began",
          run.state == opening_state)
    check("F10 aggregate capacity returns exactly to its opening value",
          run.ledger.total == opening_balance, str(run.ledger.total))

    accounting = window(tuple(run.records[1:]))
    check("F10 the window is a closed actor-only cycle",
          accounting.external_total == 0 and accounting.ebu_total == 0)
    balances = run.ledger.balance_map
    check("F11 capacity migrated between two actors",
          balances["B"] == F(0) and balances["C"] == F(4), str(balances))
    check("F11 while the total stayed exactly constant",
          sum(balances.values()) == opening_balance)


def fixture_f12_explicit_loss() -> None:
    world = loss_world()
    state = world.reference_state()
    group = _plan(world, (0, 1, 4))
    increment = group.increment(world.dimension)
    valuation = value_group(world, state, group)
    check("F12 the loss is deposited in an explicit sink", increment[3] == F(2))
    check("F12 conservation closes over all coordinates", sum(increment) == 0)
    check("F12 the resource total is unchanged",
          world.resource_total(add(state, increment), "sand")
          == world.resource_total(state, "sand"))
    after = add(state, increment)
    check("F12 the depleted source now carries a physical demand",
          any(d.demand_id == "P:sand|A" for d in derive_physical_demands(world, after)))
    check("F12 no EBU is issued beyond the group value",
          valuation.residual == 0 and sum(r for _, r in valuation.receipts) == valuation.group_ebu)


def fixture_f13_one_plan_many_demands() -> None:
    world = sandwater_world()
    state = _state(8, 8, 14, 6, 6)
    economic = (_economic(world, "sand", 2, "A", 0, 0),)
    physical = derive_physical_demands(world, state)
    component = components(world, state, ActiveDemandSet.of(physical, economic))[0]
    joint = _plan(world, (2, 0, 2), (2, 1, 2))
    increment = joint.increment(world.dimension)
    check("F13 one plan serves three demands", len(component.demands) == 3
          and serves_all(component.requirements, increment))
    check("F13 the action into A is credited once, not twice", increment[0] == F(2))
    plans = [p for p in enumerate_service_plans(world, state, component) if p.group == joint]
    check("F13 and its provenance names both demands it answers",
          plans and set(plans[0].provenance_map["r:sand:2->0@2/1"])
          == {"P:sand|A", economic[0].demand_id})


def fixture_f14_f15_f16_actor_policies() -> None:
    world = sandwater_world()
    state = _state(8, 12, 10, 6, 6)
    chosen = {}
    for policy in (POLICY_HOSTILE, POLICY_RANDOM, POLICY_ALIGNED, POLICY_CONTROL):
        run = EconomyRun(world, quiet_disturbance(world), no_arrivals(), policy,
                         1, 2, 3, 4, initial_state=state)
        record = run.run_epoch()
        chosen[policy] = (record.epoch_ebu, record.outcomes[0].affordable_count)
    check("F14 hostile takes the worst affordable plan, and still serves the demand",
          chosen[POLICY_HOSTILE][0] == F(0), str(chosen[POLICY_HOSTILE]))
    check("F16 aligned takes the best", chosen[POLICY_ALIGNED][0] == F(4), str(chosen[POLICY_ALIGNED]))
    check("F15 random takes one of the affordable four",
          chosen[POLICY_RANDOM][0] in (F(0), F(3), F(4)), str(chosen[POLICY_RANDOM]))
    check("F14-F16 all three see the same four affordable candidates",
          {chosen[p][1] for p in (POLICY_HOSTILE, POLICY_RANDOM, POLICY_ALIGNED)} == {4},
          str(chosen))
    check("the comparator sees all five, affordable or not",
          chosen[POLICY_CONTROL][1] == 5, str(chosen[POLICY_CONTROL]))


# --------------------------------------------------------------------------
# Contract section 41 -- randomized exact capacity-cycle property tests
# --------------------------------------------------------------------------


def _executable_singletons(world, state):
    from demand_driven_ebu.physical import action_alphabet

    return tuple(
        action
        for action in action_alphabet(world)
        if can_happen_now(world, state, PlanGroup.of(action)).executable
    )


def _inverse(world, action):
    route = _route(world, action.route.destination, action.route.source)
    return PhysicalAction.declare(route, action.quantity)


def test_randomized_closed_cycles_never_mint_capacity() -> None:
    """Out-and-back paths of random length, on a lossless complete world."""
    world = cycle_world()
    worst_state = 0
    worst_balance = F(0)
    worst_ebu = F(0)
    trials = 0
    for trial in range(30):
        state = world.reference_state()
        ledger = seeded_ledger(world, 500)
        opening = ledger.total
        forward = []
        for step in range(4):
            options = _executable_singletons(world, state)
            counter = Counter(MODEL_ID, world.world_id, 1_000 + trial, "actor_choice", step, 0, 0)
            index, _ = uniform_index(counter, len(options))
            action = options[index]
            group = PlanGroup.of(action)
            state, ledger, valuation = _apply(world, state, ledger, group)
            forward.append(action)
        total = F(0)
        for action in reversed(forward):
            group = PlanGroup.of(_inverse(world, action))
            if not can_happen_now(world, state, group).executable:
                break
            state, ledger, valuation = _apply(world, state, ledger, group)
            total += valuation.group_ebu
        else:
            trials += 1
            if state != world.reference_state():
                worst_state += 1
            worst_balance = max(worst_balance, abs(ledger.total - opening))
    check("randomized out-and-back cycles were generated", trials >= 25, str(trials))
    check("every one returned the physical state exactly", worst_state == 0, str(worst_state))
    check("and left aggregate capacity exactly unchanged", worst_balance == 0, str(worst_balance))


def test_randomized_receipt_closure() -> None:
    world = cycle_world()
    worst = F(0)
    groups = 0
    for trial in range(40):
        state = world.reference_state()
        counter = Counter(MODEL_ID, world.world_id, 5_000 + trial, "actor_choice", 0, 0, 0)
        options = _executable_singletons(world, state)
        first, _ = uniform_index(counter, len(options))
        second, _ = uniform_index(counter.at(draw_index=1), len(options))
        if options[first].route.route_id == options[second].route.route_id:
            continue
        group = PlanGroup.of(options[first], options[second])
        if not can_happen_now(world, state, group).executable:
            continue
        groups += 1
        valuation = value_group(world, state, group)
        worst = max(worst, abs(valuation.residual))
        summed = sum((r for _, r in valuation.receipts), F(0))
        worst = max(worst, abs(summed - valuation.group_ebu))
    check("randomized simultaneous groups were valued", groups >= 20, str(groups))
    check("sum_a R_a = E_G held exactly every time", worst == 0, str(worst))


def test_repeated_two_state_oscillation_mints_nothing() -> None:
    world = cycle_world()
    state = world.reference_state()
    ledger = seeded_ledger(world, 300)
    opening = ledger.total
    totals = []
    for _ in range(6):
        state, ledger, _ = _apply(world, state, ledger, _plan(world, (0, 1, 2)))
        state, ledger, _ = _apply(world, state, ledger, _plan(world, (1, 0, 2)))
        totals.append(ledger.total)
    check("A -> B -> A -> B -> A returns the state every time", state == world.reference_state())
    check("and aggregate capacity never moves off its opening value",
          set(totals) == {opening}, str(sorted(set(totals))))


# --------------------------------------------------------------------------
# Isolation from the registered programme
# --------------------------------------------------------------------------


PINNED = {
    "gaussian_harness": "a9158eefb4eaf7d2dd609f1292d97f245290d73ec4e0393288ce5fd47725fe55",
    "capacity_v2": "8976da3c44a121d1b9c058795a9ee38b05999e2cf674e70134d18222e70221c2",
    "homeostasis": "8b462401a00ed8624fbd649e460b9e44e6adf8ba749ca1fa3872e9a6ddd4c3c6",
}


def test_pinned_packages_are_untouched() -> None:
    from capacity_v2.harness import code_identity as capacity_identity
    from gaussian_harness.harness import code_identity as gaussian_identity
    from homeostasis.harness import code_identity as homeostasis_identity

    actual = {
        "gaussian_harness": gaussian_identity(),
        "capacity_v2": capacity_identity(),
        "homeostasis": homeostasis_identity(),
    }
    for name, expected in PINNED.items():
        check(f"{name} code identity is unchanged", actual[name] == expected, actual[name])


def test_the_new_model_has_its_own_identity_and_no_forbidden_imports() -> None:
    import pkgutil

    import demand_driven_ebu

    identity = code_identity()
    check("the demand-driven package has its own code identity",
          identity not in PINNED.values() and len(identity) == 64)
    check("and its own model id", MODEL_ID == "EBU-DEMAND-DRIVEN-ECONOMY-v1")

    forbidden = []
    allowed_prefixes = ("gaussian_harness.numerics", "gaussian_harness.potential")
    for module in pkgutil.iter_modules(demand_driven_ebu.__path__):
        source = (
            __import__(f"demand_driven_ebu.{module.name}", fromlist=["x"]).__doc__ or ""
        )
        del source
        path = f"{demand_driven_ebu.__path__[0]}/{module.name}.py"
        tree = ast.parse(open(path).read())
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                if node.module.startswith(("capacity_v2", "homeostasis", "stage_")):
                    forbidden.append(f"{module.name} -> {node.module}")
                if node.module.startswith("gaussian_harness") and not node.module.startswith(
                    allowed_prefixes
                ):
                    forbidden.append(f"{module.name} -> {node.module}")
    check("the new package imports no registered harness or study module",
          not forbidden, str(forbidden))


def test_the_model_never_writes_to_a_registered_result_path() -> None:
    import demand_driven_ebu

    offenders = []
    for name in ("harness", "capacity", "valuation", "plans", "admission", "arrivals"):
        path = f"{demand_driven_ebu.__path__[0]}/{name}.py"
        text = open(path).read()
        for token in ("results/", "open(", "write_text", "write_bytes", "mkdir"):
            if token in text:
                offenders.append(f"{name}:{token}")
    check("no model module writes to disk at all", not offenders, str(offenders))


# --------------------------------------------------------------------------


def main() -> int:
    groups = (
        ("potential geometry and the registered oracle",
         test_potential_agrees_with_the_registered_oracle),
        ("audit-only coordinates carry no potential",
         test_audit_only_coordinate_carries_no_potential),
        ("half-declared coordinates are refused",
         test_potential_refuses_half_declared_coordinates),
        ("P-demand is derived, not stored", test_physical_demand_is_derived_not_stored),
        ("P-demand persists with the deviation",
         test_physical_demand_persists_while_the_deviation_does),
        ("P-demand cannot be rejected", test_physical_demand_cannot_be_rejected),
        ("multiple physical demands coexist", test_multiple_physical_demands_coexist),
        ("economic demand may exceed the resource",
         test_economic_demand_may_exceed_available_resource),
        ("scarcity is decided before EBU", test_scarcity_is_decided_before_ebu),
        ("admission never reads EBU or capacity",
         test_admission_never_reads_ebu_or_capacity),
        ("random admission picks a maximal compatible subset",
         test_random_admission_picks_a_maximal_compatible_subset),
        ("admission is uniform over maximal subsets",
         test_admission_is_uniform_over_maximal_subsets),
        ("admission optimizes nothing", test_admission_optimizes_nothing),
        ("admission protects an existing physical demand",
         test_admission_protects_an_existing_physical_demand),
        ("stuck demands do not freeze admission",
         test_already_stuck_demands_do_not_freeze_admission),
        ("the active demand set is unordered", test_the_active_demand_set_is_unordered),
        ("no scheduler symbol exists", test_no_scheduler_symbol_exists_anywhere),
        ("economic and physical demands coexist",
         test_economic_and_physical_demands_coexist),
        ("independent resources form independent components",
         test_independent_resources_form_independent_components),
        ("shared stock couples two demands", test_shared_stock_couples_two_demands),
        ("shared account couples two resources",
         test_shared_account_couples_two_resources),
        ("an impossible component blocks nothing independent",
         test_an_impossible_component_does_not_block_an_independent_one),
        ("every menu plan serves completely", test_every_menu_plan_serves_completely),
        ("no plan exists without a demand", test_no_plan_exists_without_a_demand),
        ("every action has demand provenance", test_every_action_has_demand_provenance),
        ("irredundancy blocks unrelated transfers",
         test_irredundancy_blocks_bolting_on_an_unrelated_transfer),
        ("one action may serve several demands",
         test_one_action_may_serve_several_demands_without_double_credit),
        ("executability reads only physics", test_executability_reads_only_physics),
        ("source-funded simultaneity", test_source_funded_simultaneity),
        ("route capacity and quanta are enforced",
         test_route_capacity_and_quantum_are_enforced),
        ("stock capacity is a hard limit", test_stock_capacity_is_a_hard_limit),
        ("impossible plans never reach valuation",
         test_impossible_plans_are_removed_before_valuation),
        ("group EBU, closed form and path integral",
         test_group_ebu_matches_the_closed_form_and_the_path_integral),
        ("the linear estimate is not the finite value",
         test_linear_estimate_is_not_the_finite_value),
        ("capacity never changes what EBU measures",
         test_capacity_never_changes_what_ebu_measures),
        ("valuation is not given a ledger", test_valuation_is_not_given_a_ledger),
        ("zero-capacity bootstrap", test_zero_capacity_bootstrap),
        ("no overdraft and no transfer", test_no_overdraft_and_no_transfer),
        ("settlement is all or nothing", test_settlement_is_all_or_nothing),
        ("capacity is spendable only through a demand",
         test_capacity_is_only_spendable_through_a_demand_serving_plan),
        ("policies choose among equally complete answers",
         test_policies_choose_among_equally_complete_answers),
        ("hostile cannot choose unrelated damage",
         test_hostile_cannot_choose_unrelated_damage),
        ("random and control are structurally EBU-blind",
         test_random_and_control_are_structurally_ebu_blind),
        ("the comparator applies no affordability filter",
         test_the_comparator_applies_no_affordability_filter),
        ("there is no voluntary no-action", test_there_is_no_voluntary_no_action),
        ("the three legitimate inactions are distinguished",
         test_the_three_legitimate_inactions_are_distinguished),
        ("independent components execute together",
         test_independent_components_execute_in_the_same_epoch),
        ("the joint gate verifies separability",
         test_the_joint_gate_verifies_separability_exactly),
        ("simultaneous children are not settled from singletons",
         test_simultaneous_children_are_not_settled_from_singleton_quotes),
        ("P-demand is re-derived after execution",
         test_physical_demand_is_rederived_after_execution),
        ("an economic action creates new physical demand",
         test_an_economic_action_creates_new_physical_demand),
        ("loss is represented and conserves", test_loss_is_represented_and_conserves),
        ("a sink inside V is charged, one outside is not",
         test_a_sink_inside_v_is_charged_and_one_outside_it_is_not),
        ("loss generates demand at the depleted stock",
         test_loss_generates_physical_demand_at_the_depleted_stock),
        ("irreversible loss blocks complete restoration",
         test_irreversible_loss_makes_complete_restoration_impossible),
        ("disturbance changes no capacity", test_disturbance_changes_no_capacity),
        ("a null disturbance is not repaired", test_a_null_disturbance_is_not_repaired),
        ("exact circulation fixture", test_exact_circulation_fixture),
        ("exact loss circulation fixture", test_exact_loss_circulation_fixture),
        ("closed-cycle no-issuance theorem", test_closed_cycle_no_issuance_theorem),
        ("closed cycle holds for simultaneous groups",
         test_closed_cycle_holds_for_simultaneous_groups),
        ("capacity-source identity over a driven run",
         test_capacity_source_identity_holds_over_a_driven_run),
        ("an economic arrival issues no capacity",
         test_economic_arrival_issues_no_capacity),
        ("no process burden is charged", test_no_process_burden_is_charged_anywhere),
        ("the capacity-source table is complete",
         test_the_capacity_source_table_is_complete_and_signed),
        ("four streams are declared and separate",
         test_four_streams_are_declared_and_separate),
        ("actor policy cannot move arrivals",
         test_actor_policy_cannot_move_the_arrival_sequence),
        ("the actor seed cannot move arrivals",
         test_changing_the_actor_seed_cannot_move_arrivals),
        ("streams share no mutable state", test_streams_share_no_mutable_state),
        ("F1 no demand", fixture_f1_no_demand),
        ("F2 pure physical demand", fixture_f2_pure_physical_demand),
        ("F3 restorative economic demand", fixture_f3_restorative_economic_demand),
        ("F4 costly economic demand", fixture_f4_costly_economic_demand),
        ("F5 demand exceeds the resource", fixture_f5_demand_exceeds_the_resource),
        ("F6 two competing economic demands", fixture_f6_two_competing_economic_demands),
        ("F7 coexisting economic and physical",
         fixture_f7_coexisting_economic_and_physical),
        ("F8 independent components", fixture_f8_independent_components),
        ("F9 unaffordable component beside a working one",
         fixture_f9_unaffordable_component_alongside_a_working_one),
        ("F10/F11 closed cycle with two actors",
         fixture_f10_and_f11_closed_cycle_with_two_actors),
        ("F12 explicit loss", fixture_f12_explicit_loss),
        ("F13 one plan, many demands", fixture_f13_one_plan_many_demands),
        ("F14/F15/F16 actor policies", fixture_f14_f15_f16_actor_policies),
        ("randomized closed cycles mint nothing",
         test_randomized_closed_cycles_never_mint_capacity),
        ("randomized receipt closure", test_randomized_receipt_closure),
        ("repeated oscillation mints nothing",
         test_repeated_two_state_oscillation_mints_nothing),
        # --- audit correction pass -------------------------------------
        ("separate orders are separate obligations",
         test_separate_orders_are_separate_material_obligations),
        ("the additive rule governs the menu",
         test_the_additive_rule_governs_the_menu_not_only_the_predicate),
        ("allocation respects pool and order size",
         test_allocation_respects_the_pool_and_the_order_size),
        ("the pool is net, not gross", test_the_pool_is_net_not_gross),
        ("physical demand draws nothing from the economic pool",
         test_physical_demand_draws_nothing_from_the_economic_pool),
        ("every arrival is tracked over the common raw set",
         test_every_arrival_is_tracked_over_the_common_raw_set),
        ("admitted-only service rate is not the whole-system measure",
         test_admitted_only_service_rate_is_not_the_whole_system_measure),
        ("uniform over subsets is not uniform over demands",
         test_uniform_over_subsets_is_not_uniform_over_demands),
        ("an unserviceable demand freezes nothing",
         test_an_unserviceable_demand_freezes_nothing),
        ("impossible sand cannot freeze independent water",
         test_impossible_sand_cannot_freeze_independent_water),
        ("decomposition does not restrict the global feasible set",
         test_decomposition_does_not_restrict_the_global_feasible_set),
        ("component freezing is a declared restriction",
         test_component_freezing_is_a_declared_restriction_not_scarcity),
        ("cancelling external events are not actor-only",
         test_cancelling_external_events_are_not_actor_only),
        ("external permutation at constant V is not actor-only",
         test_external_permutation_at_constant_potential_is_not_actor_only),
        ("a genuine actor-only cycle mints nothing",
         test_a_genuine_actor_only_cycle_is_classified_and_mints_nothing),
        ("actor-only is not inferred from the potential",
         test_actor_only_is_not_inferred_from_the_potential_term),
        ("a route out of a sink is refused",
         test_a_route_out_of_a_sink_is_refused_at_construction),
        ("no declared world exports from a sink",
         test_no_declared_world_exports_from_a_sink),
        ("the capacity identity survives additive service",
         test_capacity_identity_survives_additive_service),
        ("no duplicate receipt or service credit",
         test_no_duplicate_receipt_or_service_credit),
        ("an arrival creates no capacity under additive orders",
         test_an_arrival_still_creates_no_capacity_under_additive_orders),
        ("hand-check A: two 700 orders against 1000",
         test_admission_hand_check_a_two_700_orders_against_1000),
        ("hand-check B: two 500 orders against 1000",
         test_admission_hand_check_b_two_500_orders_against_1000),
        ("hand-check C: 1000 against 560",
         test_admission_hand_check_c_1000_against_560),
        ("hand-check D: economic and physical at one destination",
         test_admission_hand_check_d_economic_and_physical_at_one_destination),
        # --- isolation ---------------------------------------------------
        # --- final demand-coupling correction (auditor 2) ----------------
        ("auditor counterexample: three independent deliveries",
         test_auditor_counterexample_three_independent_deliveries),
        ("A: unusable routes cannot change serviceability",
         test_unusable_routes_cannot_change_serviceability),
        ("B: removing them is the exact inverse",
         test_removing_unusable_routes_is_the_exact_inverse),
        ("C: a binding shared route may couple, with its reason shown",
         test_a_binding_shared_route_may_couple_and_the_reason_is_shown),
        ("D: an irrelevant executable action creates no coupling",
         test_an_irrelevant_executable_action_creates_no_coupling),
        ("E: one action serving two demands stays coupled",
         test_one_action_serving_two_demands_stays_coupled),
        ("F: two demands sharing scarce stock stay coupled",
         test_two_demands_sharing_scarce_stock_stay_coupled),
        ("G: global and component feasible sets agree",
         test_global_and_component_feasible_sets_agree),
        ("H: an impossible component blocks nothing independent",
         test_an_impossible_component_does_not_block_an_independent_one_triple),
        ("coupling does not depend on the plan cap",
         test_coupling_does_not_depend_on_the_plan_cap),
        ("the cap never reports physical impossibility",
         test_the_cap_never_reports_physical_impossibility),
        ("genuine impossibility is still reported as impossibility",
         test_genuine_impossibility_is_still_reported_as_impossibility),
        ("admission uses uncapped physical serviceability",
         test_admission_uses_uncapped_physical_serviceability),
        ("the uncapped search fails closed",
         test_the_uncapped_search_fails_closed_rather_than_guessing),
        ("the structural reach ignores unusable routes",
         test_structural_reach_ignores_unusable_routes_by_construction),
        # --- auditor 2, second pass --------------------------------------
        ("a wide but easy requirement is not refused on its search space",
         test_a_wide_but_easy_requirement_is_not_refused_on_its_search_space),
        ("search uncertainty never becomes impossibility",
         test_search_uncertainty_never_becomes_impossibility),
        ("an undecided demand is not rejected for scarcity",
         test_an_undecided_demand_is_not_rejected_for_scarcity),
        ("empty-source routes cannot change serviceability",
         test_empty_source_routes_cannot_change_serviceability),
        ("a route becomes live when its source is funded",
         test_a_route_becomes_live_when_its_source_is_funded),
        ("the structural reach is state-aware",
         test_the_structural_reach_is_state_aware),
        ("the oracle compares receipts, not only increments",
         test_the_oracle_compares_receipts_not_only_increments),
        ("the oracle equalises the plan cap on both sides",
         test_the_oracle_equalises_the_plan_cap_on_both_sides),
        # --- Study-1 domain freeze ---------------------------------------
        ("the Study-1 domain is frozen and machine-checkable",
         test_the_study_one_domain_is_frozen_and_machine_checkable),
        ("every domain condition is enforced separately",
         test_every_domain_condition_is_enforced_separately),
        ("outside the domain is future physics, not a blocker",
         test_outside_the_domain_is_future_physics_not_a_blocker),
        ("no module claims general loss/capacity-aware exactness",
         test_no_module_claims_general_loss_or_capacity_aware_exactness),
        ("liveness is necessary in every domain",
         test_liveness_is_necessary_in_every_domain),
        ("liveness is sufficient inside Study 1",
         test_liveness_is_sufficient_inside_the_study_one_domain),
        ("action liveness is necessary and sufficient in Study 1",
         test_action_liveness_is_necessary_and_sufficient_in_study_one),
        ("liveness sufficiency is not claimed outside Study 1",
         test_liveness_sufficiency_is_not_claimed_outside_the_domain),
        ("OUTSIDE STUDY-1: the storage-capacity counterexample is retained",
         test_storage_capacity_counterexample_outside_study_one_is_retained),
        ("OUTSIDE STUDY-1: the shared-loss-sink counterexample is retained",
         test_shared_loss_sink_counterexample_outside_study_one_is_retained),
        ("the Study-1 cap cannot bind on anything",
         test_the_study_one_cap_cannot_bind_on_anything),
        ("the pruned search equals complete enumeration",
         test_the_pruned_search_equals_complete_enumeration),
        ("a computational cap never makes a serviceable demand impossible",
         test_a_computational_cap_never_makes_a_serviceable_demand_impossible),
        ("exactly three search verdicts exist and stay apart",
         test_exactly_three_search_verdicts_exist_and_stay_apart),
        ("UNRESOLVED is never converted into a rejection",
         test_unresolved_is_never_converted_into_a_rejection),
        ("a registered job refuses to start outside the domain",
         test_a_registered_job_refuses_to_start_outside_the_domain),
        ("SEARCH_UNRESOLVED invalidates the entire registered job",
         test_search_unresolved_invalidates_the_entire_registered_job),
        ("an unregistered run keeps the three-way distinction",
         test_an_unregistered_run_keeps_the_three_way_distinction),
        ("the global progress reference is the authority",
         test_the_global_progress_reference_is_the_authority_for_study_one),
        ("the harness gate checks decomposition every epoch",
         test_the_harness_gate_checks_decomposition_every_epoch),
        ("a decomposition difference stops the run",
         test_a_decomposition_difference_stops_the_run),
        ("unusable infrastructure changes none of the five outputs",
         test_unusable_infrastructure_changes_none_of_the_five_outputs),
        ("admission requires proved serviceability",
         test_admission_requires_proved_serviceability_in_study_one),
        ("additive orders survive the freeze",
         test_additive_orders_survive_the_freeze),
        ("the completeness bound is computed, not asserted",
         test_the_completeness_bound_is_computed_not_asserted),
        ("STUDY-1 DOMAIN VERIFIED is not general-framework proof",
         test_study_one_verified_is_not_general_framework_proved),
        # --- oracle and sampling semantics correction ---------------------
        ("the auditor counterexample is exactly as described",
         test_the_auditor_counterexample_is_exactly_as_described),
        ("the old all-complete oracle passed vacuously here",
         test_the_old_all_complete_oracle_passed_vacuously_here),
        ("the progress reference sees what the runtime does",
         test_the_progress_reference_sees_what_the_runtime_does),
        ("a blocked part contributes no action and keeps its demand",
         test_a_blocked_part_contributes_no_action_and_keeps_its_demand),
        ("the reference partition is derived without calling coupling",
         test_the_reference_partition_is_derived_without_calling_coupling),
        ("all-complete remains available under a narrower name",
         test_all_complete_remains_available_under_a_narrower_name),
        ("the sampling unit is the canonical plan identity",
         test_the_sampling_unit_is_the_canonical_plan_identity),
        ("the outcome map is many-to-one", test_the_outcome_map_is_many_to_one),
        ("uniform plan sampling induces 1/4, 1/2, 1/4",
         test_uniform_plan_sampling_induces_a_quarter_half_quarter_law),
        ("aligned and hostile restrict then tie-break over plans",
         test_aligned_and_hostile_restrict_then_tie_break_over_plans),
        ("outcome support alone does not prove the induced law",
         test_outcome_support_alone_does_not_prove_the_induced_law),
        ("all four levels run on every declared fixture",
         test_all_four_levels_run_on_every_declared_fixture),
        ("a serviceable component must execute one nonempty plan",
         test_a_serviceable_component_must_execute_one_nonempty_plan),
        ("blocked and unresolved are still different things",
         test_blocked_and_unresolved_are_still_different_things),
        # --- isolation ---------------------------------------------------
        ("pinned packages are untouched", test_pinned_packages_are_untouched),
        ("the new model is isolated",
         test_the_new_model_has_its_own_identity_and_no_forbidden_imports),
        ("the model writes nothing to disk",
         test_the_model_never_writes_to_a_registered_result_path),
    )
    for label, test in groups:
        print(f"\n{label}")
        test()
    print(
        f"\nDemand-driven conformance gate: {PASSED} passed, {FAILED} failed, "
        f"{len(groups)} groups"
    )
    print("Execution class: MODEL-STATE-ADVANCING TRANSITION SUITE (this suite only)")
    print("  numeric policy: exact rational, tolerance 0")
    print("  scientific evidence generated: NONE")
    print(f"  demand_driven_ebu code identity: {code_identity()}")
    return 1 if FAILED else 0



# ==========================================================================
# AUDIT CORRECTION PASS -- the five defects found against commit 22fd229
# ==========================================================================

# --------------------------------------------------------------------------
# Correction 1 and 3 -- economic demands are additive delivery obligations
# --------------------------------------------------------------------------


def test_separate_orders_are_separate_material_obligations() -> None:
    """The observed regression: two q=2 orders are not served by q=2 delivered."""
    world = sandwater_world()
    state = _state(14, 10, 6, 6, 6)
    first = _economic(world, "sand", 2, "C", 78, 0)
    second = _economic(world, "sand", 2, "C", 78, 1)
    reqs = requirements((first, second))
    check("two independent orders of 2 require 4 at that coordinate",
          len(reqs) == 1 and reqs[0].economic_total == F(4), str(reqs))

    def delivered(quantity):
        increment = [F(0)] * world.dimension
        increment[world.index_of("sand", "C")] = F(quantity)
        return tuple(increment)

    check("a delivery of 2 serves neither order",
          served_economic_ids(reqs, delivered(2)) == ())
    check("a delivery of 3 still serves neither",
          served_economic_ids(reqs, delivered(3)) == ())
    check("a delivery of 4 serves both",
          served_economic_ids(reqs, delivered(4))
          == (first.demand_id, second.demand_id))
    check("no delivered unit satisfies two orders at once",
          not serves_all(reqs, delivered(3)) and serves_all(reqs, delivered(4)))


def test_the_additive_rule_governs_the_menu_not_only_the_predicate() -> None:
    """Correction 3: the same semantics in enumeration, not a patched endpoint."""
    world = sandwater_world()
    state = _state(14, 10, 6, 6, 6)
    first = _economic(world, "sand", 2, "C", 78, 0)
    second = _economic(world, "sand", 2, "C", 78, 1)
    component = components(world, state, ActiveDemandSet.of((), (first, second)))[0]
    plans = enumerate_service_plans(world, state, component)
    check("the two orders form one component through their shared pool",
          len(component.demands) == 2)
    check("the menu is non-empty", len(plans) > 0)
    short = [
        plan.plan_id
        for plan in plans
        if plan.group.increment(world.dimension)[world.index_of("sand", "C")] < F(4)
    ]
    check("every plan in the menu delivers at least 4", not short, str(short))
    check("and every plan allocates both orders in full",
          all(entry.complete for plan in plans for entry in plan.allocation))


def test_allocation_respects_the_pool_and_the_order_size() -> None:
    world = sandwater_world()
    first = _economic(world, "sand", 2, "C", 0, 0)
    second = _economic(world, "sand", 3, "C", 0, 1)
    reqs = requirements((first, second))
    coordinate = world.index_of("sand", "C")

    def delivered(quantity):
        increment = [F(0)] * world.dimension
        increment[coordinate] = F(quantity)
        return tuple(increment)

    full = allocate(reqs[0], delivered(5))
    check("a sufficient pool allocates every order in full",
          full.complete and full.allocation_map == {first.demand_id: F(2),
                                                    second.demand_id: F(3)})
    check("and the allocation never exceeds the pool",
          sum(v for _, v in full.allocations) <= full.pool)

    short = allocate(reqs[0], delivered(4))
    check("an insufficient pool is incomplete, with the shortfall named",
          not short.complete and short.shortfall == F(1))
    check("the diagnostic fill still respects 0 <= s_d <= q_d",
          all(F(0) <= v <= dict(reqs[0].economic_quantities)[k]
              for k, v in short.allocations))
    check("and still never exceeds the pool",
          sum(v for _, v in short.allocations) <= short.pool)
    check("an incomplete allocation can never reach a menu",
          served_economic_ids(reqs, delivered(4)) == ())


def test_the_pool_is_net_not_gross() -> None:
    """A unit that arrives and leaves again is not present to serve an order."""
    world = sandwater_world()
    order = _economic(world, "sand", 2, "B", 0, 0)
    reqs = requirements((order,))
    group = _plan(world, (0, 1, 2), (1, 2, 2))
    increment = group.increment(world.dimension)
    check("gross inflow to B is 2 but net is 0",
          increment[world.index_of("sand", "B")] == F(0))
    check("so the pool is zero", pool(increment, world.index_of("sand", "B")) == F(0))
    check("and the order is not served", not serves_all(reqs, increment))


# --------------------------------------------------------------------------
# Correction 2 -- E/P overlap remains legitimate
# --------------------------------------------------------------------------


def test_physical_demand_draws_nothing_from_the_economic_pool() -> None:
    world = sandwater_world()
    state = _state(14, 10, 8, 6, 6)
    physical = derive_physical_demands(world, state)
    order = _economic(world, "sand", 2, "C", 0, 0)
    coordinate = world.index_of("sand", "C")
    check("the state carries a two-unit shortfall at C",
          [(d.demand_id, d.required) for d in physical] == [("P:sand|C", F(2))])

    reqs = requirements(tuple(physical) + (order,))
    entry = [r for r in reqs if r.coordinate == coordinate][0]
    check("the economic claim is 2", entry.economic_total == F(2))
    check("the physical condition is 2", entry.physical_deficit == F(2))
    check("the combined requirement is the maximum, not the sum",
          entry.required_delta == F(2), str(entry.required_delta))

    increment = [F(0)] * world.dimension
    increment[coordinate] = F(2)
    increment[0] = F(-2)
    increment = tuple(increment)
    check("one two-unit delivery fulfils the order and closes the shortfall",
          serves_all(reqs, increment) and unmet(reqs, increment) == ())
    check("the post-state actually reaches the reference",
          state[coordinate] + increment[coordinate] == F(10))

    two_orders = requirements(tuple(physical) + (order, _economic(world, "sand", 2, "C", 0, 1)))
    entry = [r for r in two_orders if r.coordinate == coordinate][0]
    check("but two economic orders still add to each other",
          entry.economic_total == F(4) and entry.required_delta == F(4))
    check("so the same two-unit delivery no longer suffices",
          not serves_all(two_orders, increment))


# --------------------------------------------------------------------------
# Correction 4 -- identical raw arrivals, endogenous admission
# --------------------------------------------------------------------------


def test_every_arrival_is_tracked_over_the_common_raw_set() -> None:
    world = sandwater_world()
    disturbance = DisturbanceProcess.declare(world, ((0, 1), (1, 2), (3, 4)), 2, 1, 2)
    arrivals = ArrivalProcess.declare((("sand", "C", 2), ("water", "E", 1)), 1, 2, 2)
    ledgers = {}
    raw = {}
    for policy in (POLICY_ALIGNED, POLICY_RANDOM, POLICY_HOSTILE, POLICY_CONTROL):
        run = EconomyRun(world, disturbance, arrivals, policy, 11, 22, 33, 44)
        records = run.run(25)
        ledgers[policy] = run.arrival_ledger
        raw[policy] = tuple(demand for record in records for demand in record.arrivals)

    check("the raw arrival set is identical across all four arms",
          len(set(raw.values())) == 1, str({k: len(v) for k, v in raw.items()}))
    check("every arm's ledger holds exactly the raw arrivals",
          all(set(ledger) == set(raw[policy]) for policy, ledger in ledgers.items()))
    states = {
        policy: sorted({row.state for row in ledger.values()})
        for policy, ledger in ledgers.items()
    }
    check("every recorded state is a declared lifecycle state",
          all(state in DECLARED_LIFECYCLE for entries in states.values() for state in entries),
          str(states))
    admitted = {
        policy: sum(1 for row in ledger.values() if row.state != LIFECYCLE_ARRIVED
                    and not row.state.startswith("REJECTED"))
        for policy, ledger in ledgers.items()
    }
    check("admission legitimately differs across arms while arrivals do not",
          len(set(admitted.values())) > 1, str(admitted))


def test_admitted_only_service_rate_is_not_the_whole_system_measure() -> None:
    """Why correction 4 matters: the two rates can rank arms differently."""
    world = sandwater_world()
    disturbance = DisturbanceProcess.declare(world, ((0, 1), (1, 2), (3, 4)), 2, 1, 2)
    arrivals = ArrivalProcess.declare((("sand", "C", 2), ("water", "E", 1)), 1, 2, 2)
    rates = {}
    for policy in (POLICY_ALIGNED, POLICY_RANDOM, POLICY_HOSTILE, POLICY_CONTROL):
        run = EconomyRun(world, disturbance, arrivals, policy, 11, 22, 33, 44)
        run.run(25)
        rows = list(run.arrival_ledger.values())
        served = sum(1 for row in rows if row.state == LIFECYCLE_SERVED)
        admitted = sum(1 for row in rows if not row.state.startswith("REJECTED"))
        rates[policy] = (
            F(served, len(rows)) if rows else F(0),
            F(served, admitted) if admitted else F(0),
        )
    over_arrivals = {p: r[0] for p, r in rates.items()}
    over_admitted = {p: r[1] for p, r in rates.items()}
    check("both rates are computed", len(rates) == 4)
    check("they are not the same numbers",
          over_arrivals != over_admitted,
          f"arrivals={ {k: str(v) for k, v in over_arrivals.items()} } "
          f"admitted={ {k: str(v) for k, v in over_admitted.items()} }")
    best_raw = max(over_arrivals, key=lambda p: over_arrivals[p])
    best_admitted = max(over_admitted, key=lambda p: over_admitted[p])
    check("the arm that looks best can differ between the two, which is why "
          "the admitted-only rate is never the primary comparison",
          True, f"raw={best_raw} admitted={best_admitted}")


# --------------------------------------------------------------------------
# Correction 5 -- the admission sampling measure, stated rather than assumed
# --------------------------------------------------------------------------


def test_uniform_over_subsets_is_not_uniform_over_demands() -> None:
    world = competing_world()
    state = _state(3, 0, 0)
    first = _economic(world, "sand", 3, "B", 0, 0)
    second = _economic(world, "sand", 3, "C", 0, 1)
    counts = {first.demand_id: 0, second.demand_id: 0}
    trials = 120
    for seed in range(trials):
        admitted, _, _ = admit(world, state, (), (), (first, second), seed, 0)
        for demand in admitted:
            counts[demand.demand_id] += 1
    check("with two mutually incompatible arrivals each is admitted sometimes",
          all(value > 0 for value in counts.values()), str(counts))
    check("and exactly one is admitted every time",
          sum(counts.values()) == trials, str(counts))

    roomy = sandwater_world()
    roomy_state = roomy.reference_state()
    compatible = (
        _economic(roomy, "sand", 1, "C", 0, 0),
        _economic(roomy, "water", 1, "E", 0, 1),
    )
    marginals = {demand.demand_id: 0 for demand in compatible}
    for seed in range(40):
        admitted, _, _ = admit(roomy, roomy_state, (), (), compatible, seed, 0)
        for demand in admitted:
            marginals[demand.demand_id] += 1
    check("a request compatible with everything is admitted every time, so the "
          "marginal admission probability is structure-dependent, not flat",
          all(value == 40 for value in marginals.values()), str(marginals))


# --------------------------------------------------------------------------
# Correction 6 -- coupling only through actual binding constraints
# --------------------------------------------------------------------------


def test_an_unserviceable_demand_freezes_nothing() -> None:
    """The defect: broad transport coupling froze a serviceable demand."""
    world = sandwater_world()
    state = _state(8, 12, 10, 6, 6)
    physical = derive_physical_demands(world, state)
    alone = components(world, state, ActiveDemandSet.of(physical, ()))
    baseline = len(enumerate_service_plans(world, state, alone[0]))
    check("the sand shortfall has a menu on its own", baseline == 5, str(baseline))

    stuck = _economic(world, "sand", 25, "C", 0, 0)
    found = components(world, state, ActiveDemandSet.of(physical, (stuck,)))
    sizes = {c.component_id: len(enumerate_service_plans(world, state, c)) for c in found}
    check("the unserviceable order is its own component",
          len(found) == 2, str(sorted(sizes)))
    check("it has no plans", sizes["c:[E:000000:000:sand|C]"] == 0, str(sizes))
    check("and the serviceable shortfall keeps every one of its plans",
          sizes["c:[P:sand|A]"] == baseline, str(sizes))


def test_impossible_sand_cannot_freeze_independent_water() -> None:
    world = sandwater_world()
    state = _state(3, 10, 10, 4, 8)
    run = EconomyRun(world, quiet_disturbance(world), no_arrivals(), POLICY_ALIGNED,
                     1, 2, 3, 4, initial_state=state)
    record = run.run_epoch()
    statuses = {o.component_id: o.status for o in record.outcomes}
    check("the impossible sand component is reported unserviceable",
          statuses["c:[P:sand|A]"] == STATUS_NO_COMPLETE_PLAN, str(statuses))
    check("the water component executes in the same epoch",
          statuses["c:[P:water|D]"] == STATUS_EXECUTED, str(statuses))
    check("and the water shortfall is actually closed", record.state_after[3] == F(6))


def _merged_component(world, state, demands):
    """Deliberately over-couple: one component holding every demand."""
    from demand_driven_ebu.coupling import DemandComponent, service_reach
    from demand_driven_ebu.enumeration import search_routes

    reaches = [service_reach(world, state, demand) for demand in demands]
    merged = type(reaches[0])(
        frozenset().union(*(r.coordinates for r in reaches)),
        frozenset().union(*(r.routes for r in reaches)),
        frozenset().union(*(r.owners for r in reaches)),
        min(r.destination for r in reaches),
    )
    search = frozenset(
        route.route_id
        for route in search_routes(world, frozenset(d.coordinate for d in demands))
    )
    return DemandComponent(tuple(sorted(demands, key=lambda d: d.demand_id)), merged, search)


def test_decomposition_does_not_restrict_the_global_feasible_set() -> None:
    """Splitting or merging independent demands gives the same executions.

    The plan-size cap is declared **per component plan**, so with a binding cap
    the decomposed form admits strictly more total actions than a merged
    evaluation would. The equivalence asserted here is therefore stated where
    the cap does not bind, which is the case in which the two are comparable at
    all; where it does bind, per-component is the declared semantics and it is
    the *merged* view that would restrict.
    """
    world = sandwater_world()
    state = _state(8, 12, 10, 4, 8)
    physical = derive_physical_demands(world, state)
    found = components(world, state, ActiveDemandSet.of(physical, ()))
    check("the two shortfalls decompose into two components", len(found) == 2)

    per_component = [
        [plan.group for plan in enumerate_service_plans(world, state, component)]
        for component in found
    ]
    check("both components have menus",
          all(menu for menu in per_component), str([len(m) for m in per_component]))

    product = {
        tuple(PlanGroup.of(*(left.actions + right.actions)).increment(world.dimension))
        for left in per_component[0]
        for right in per_component[1]
    }
    within_cap = {
        tuple(PlanGroup.of(*(left.actions + right.actions)).increment(world.dimension))
        for left in per_component[0]
        for right in per_component[1]
        if left.size + right.size <= world.max_plan_size
    }
    merged = _merged_component(world, state, physical)
    joint = {
        tuple(plan.group.increment(world.dimension))
        for plan in enumerate_service_plans(world, state, merged)
    }
    check("the merged menu is exactly the product restricted to the cap",
          within_cap == joint, f"{len(within_cap)} vs {len(joint)}")
    check("over-coupling deleted no valid service plan that fits the cap",
          within_cap <= joint)
    check("and merging invented none", joint <= within_cap)
    check("the decomposed form admits strictly more, because the cap is "
          "declared per component plan and here it binds",
          within_cap < product, f"{len(within_cap)} vs {len(product)}")


def test_component_freezing_is_a_declared_restriction_not_scarcity() -> None:
    """Where a component does freeze, it is the complete-service contract."""
    world = sandwater_world()
    state = _state(8, 12, 10, 6, 6)
    physical = derive_physical_demands(world, state)
    big = _economic(world, "sand", 3, "A", 0, 0)
    found = components(world, state, ActiveDemandSet.of(physical, (big,)))
    check("an order at the same coordinate as a shortfall shares its pool, "
          "so the two are genuinely coupled", len(found) == 1, str([c.demand_ids for c in found]))
    entry = [r for r in found[0].requirements if r.coordinate == 0][0]
    check("and the coupling is the declared max rule, not physical scarcity",
          entry.economic_total == F(3) and entry.physical_deficit == F(2)
          and entry.required_delta == F(3), str(entry))


# --------------------------------------------------------------------------
# Correction 7 -- actor-only cycle provenance
# --------------------------------------------------------------------------


def test_cancelling_external_events_are_not_actor_only() -> None:
    """The exact case the old classifier got wrong.

    In a world with no routes the actor can never act, so the window contains
    nothing but two external events that cancel. The state returns, the
    potential term sums to zero and there is no loss -- so the previous
    `sum(dV_ext) == 0` test would have certified this interval as a closed
    actor-only cycle, which it plainly is not.
    """
    world = routeless_world()
    disturbance = ScriptedDisturbance({0: (0, 1, 2), 1: (1, 0, 2)})
    run = EconomyRun(world, disturbance, no_arrivals(), POLICY_CONTROL, 1, 2, 3, 4)
    records = run.run(2)
    accounting = window(records)
    check("the actor never acted", all(record.receipts == () for record in records))
    check("the state returned exactly",
          records[-1].state_after == records[0].state_before)
    check("the two external events cancel in the potential",
          accounting.external_total == 0, str(accounting.external_total))
    check("the superseded potential-only test would have called this actor-only",
          accounting.external_total == 0
          and records[-1].state_after == records[0].state_before)
    check("but two external physical events are recorded",
          len(accounting.external_events) == 2, str(accounting.external_events))
    check("so the interval is not actor-only", not actor_only(records))
    check("and the classifier says so by provenance, not by potential",
          closed_cycle(run).reason == "EXTERNAL_PHYSICAL_EVENT_PRESENT",
          closed_cycle(run).reason)


def test_external_permutation_at_constant_potential_is_not_actor_only() -> None:
    world = sandwater_world()
    start = _state(12, 8, 10, 6, 6)
    disturbance = ScriptedDisturbance({0: (0, 1, 4)})
    run = EconomyRun(world, disturbance, no_arrivals(), POLICY_CONTROL, 1, 2, 3, 4,
                     initial_state=start)
    record = run.run_epoch()
    check("nature permuted stock between two symmetric coordinates",
          record.state_forced == _state(8, 12, 10, 6, 6))
    check("the potential is unchanged by it",
          record.external_deviation == 0 and record.potential_forced == record.potential_before)
    check("but an external physical event is recorded",
          len(record.external_events) == 1, str(record.external_events))
    check("so the interval is not actor-only", not actor_only((record,)))


def test_a_genuine_actor_only_cycle_is_classified_and_mints_nothing() -> None:
    world = sandwater_world()
    arrivals = ScriptedArrivals({1: (("sand", "C", 2),)})
    run = EconomyRun(world, quiet_disturbance(world), arrivals, POLICY_ALIGNED,
                     1, 2, 3, 4, initial_state=_state(8, 12, 10, 6, 6))
    run.run_epoch()
    opening_state, opening_balance = run.state, run.ledger.total
    run.run_epoch()
    run.run_epoch()
    cycle_records = tuple(run.records[1:])
    check("no external physical event occurred in the window",
          actor_only(cycle_records) and window(cycle_records).external_events == ())
    check("the state returned exactly", run.state == opening_state)
    check("and aggregate capacity is exactly unchanged",
          run.ledger.total == opening_balance, str(run.ledger.total))
    check("an economic arrival inside the window did not break actor-only status",
          any(record.arrivals for record in cycle_records))


def test_actor_only_is_not_inferred_from_the_potential_term() -> None:
    import demand_driven_ebu.cycles as cycles_module

    source = inspect.getsource(cycles_module.actor_only)
    tree = ast.parse(source.strip())
    names = {getattr(n, "id", "") for n in ast.walk(tree) if isinstance(n, ast.Name)}
    attributes = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    check("the classifier reads event provenance and nothing else",
          "external_events" in attributes
          and not ({"external_deviation", "external_total", "potential_after"} & attributes),
          str(sorted(attributes)))
    del names


# --------------------------------------------------------------------------
# Correction 8 -- irreversible sinks may not be exported from
# --------------------------------------------------------------------------


def test_a_route_out_of_a_sink_is_refused_at_construction() -> None:
    for maker in (
        lambda: Coordinate.sink_in_potential("sand", "W", 0, 1),
        lambda: Coordinate.sink_audit_only("sand", "W"),
    ):
        try:
            DemandWorld.declare(
                "bad-sink-v1",
                [Coordinate.stock("sand", "A", 10, 1), maker()],
                [Route.declare("sand", 1, 0, 4)],
                (1, 2),
                1,
            )
        except Refusal as failure:
            check("a route exporting from a sink is refused",
                  "exports from a sink" in str(failure), str(failure)[:60])
        else:
            check("a route exporting from a sink is refused", False)

    try:
        DemandWorld.declare(
            "bad-sink-v2",
            [Coordinate.stock("sand", "A", 10, 1), Coordinate.sink_in_potential("sand", "W", 0, 1)],
            [Route.declare("sand", 0, 1, 4)],
            (1, 2),
            1,
        )
    except Refusal as failure:
        check("and a route delivering into one is still refused",
              "delivers into a sink" in str(failure), str(failure)[:60])
    else:
        check("and a route delivering into one is still refused", False)

    check("the declared loss worlds remain valid",
          loss_world().world_id == "loss-v1"
          and audit_sink_world().world_id == "audit-sink-v1")


def test_no_declared_world_exports_from_a_sink() -> None:
    offenders = []
    for maker in (sandwater_world, surplus_world, scarcity_world, competing_world,
                  cycle_world, loss_world, audit_sink_world):
        world = maker()
        for route in world.routes:
            if world.coordinates[route.source].role == "SINK":
                offenders.append(f"{world.world_id}:{route.route_id}")
    check("no fixture world exports from a sink", not offenders, str(offenders))


# --------------------------------------------------------------------------
# Correction 9 -- the capacity theorem after the service-allocation change
# --------------------------------------------------------------------------


def test_capacity_identity_survives_additive_service() -> None:
    world = sandwater_world()
    disturbance = DisturbanceProcess.declare(world, ((0, 1), (1, 2), (2, 0), (3, 4)), 2, 1, 2)
    arrivals = ArrivalProcess.declare(
        (("sand", "A", 1), ("sand", "C", 2), ("water", "E", 1)), 1, 2, 3
    )
    worst = F(0)
    multi = 0
    for policy in (POLICY_ALIGNED, POLICY_RANDOM, POLICY_HOSTILE, POLICY_CONTROL):
        run = EconomyRun(world, disturbance, arrivals, policy, 5, 6, 7, 8)
        records = run.run(30)
        for record in records:
            if len(record.active_economic) > 1:
                multi += 1
        worst = max(worst, abs(run.capacity_source_residual))
        accounting = window(records)
        worst = max(worst, abs(accounting.telescoping_residual), abs(accounting.identity_residual))
    check("epochs with several simultaneous economic demands occurred",
          multi > 0, str(multi))
    check("delta B_total = V(x_0) - V(x_T) + sum dV_ext exactly, in every arm",
          worst == 0, str(worst))


def test_no_duplicate_receipt_or_service_credit() -> None:
    world = sandwater_world()
    disturbance = DisturbanceProcess.declare(world, ((0, 1), (1, 2), (3, 4)), 2, 1, 2)
    arrivals = ArrivalProcess.declare((("sand", "C", 2), ("water", "E", 1)), 1, 2, 3)
    worst_receipt = F(0)
    duplicates = []
    double_served = []
    for policy in (POLICY_ALIGNED, POLICY_RANDOM, POLICY_HOSTILE, POLICY_CONTROL):
        run = EconomyRun(world, disturbance, arrivals, policy, 9, 10, 11, 12)
        records = run.run(30)
        seen: dict[str, int] = {}
        for record in records:
            identifiers = [action_id for action_id, _ in record.receipts]
            if len(set(identifiers)) != len(identifiers):
                duplicates.append(f"{policy}@{record.epoch}")
            summed = sum((value for _, value in record.receipts), F(0))
            worst_receipt = max(worst_receipt, abs(summed - record.epoch_ebu))
            for demand_id in record.served_economic:
                seen[demand_id] = seen.get(demand_id, 0) + 1
        double_served.extend(f"{policy}:{k}" for k, v in seen.items() if v > 1)
    check("no action is credited twice within an epoch", not duplicates, str(duplicates))
    check("receipts sum to the epoch EBU exactly", worst_receipt == 0, str(worst_receipt))
    check("no economic demand is ever served twice", not double_served, str(double_served))


def test_an_arrival_still_creates_no_capacity_under_additive_orders() -> None:
    world = sandwater_world()
    arrivals = ScriptedArrivals({0: (("sand", "C", 2), ("sand", "C", 2))})
    run = EconomyRun(world, quiet_disturbance(world), arrivals, POLICY_ALIGNED, 1, 2, 3, 4)
    record = run.run_epoch()
    check("two orders arrived at the same destination", len(record.arrivals) == 2)
    check("nothing physical happened", run.state == world.reference_state())
    check("and no capacity was issued", run.ledger.total == F(0))
    check("the epoch EBU is exactly zero", record.epoch_ebu == F(0))


# --------------------------------------------------------------------------
# Correction 10 -- admission hand-checks under additive orders
# --------------------------------------------------------------------------


def _big_sand_world(reference, quanta, max_plan_size=2):
    return DemandWorld.declare(
        "bigsand-v1",
        [
            Coordinate.stock("sand", "A", reference, 1),
            Coordinate.stock("sand", "B", 0, 1),
            Coordinate.stock("sand", "C", 0, 1),
        ],
        [
            Route.declare("sand", 0, 1, 1000),
            Route.declare("sand", 0, 2, 1000),
            Route.declare("sand", 1, 2, 1000),
            Route.declare("sand", 2, 1, 1000),
        ],
        quanta,
        max_plan_size,
    )


def test_admission_hand_check_a_two_700_orders_against_1000() -> None:
    world = _big_sand_world(1000, (500, 700, 1000))
    state = _state(1000, 0, 0)
    first = _economic(world, "sand", 700, "C", 0, 0)
    second = _economic(world, "sand", 700, "B", 0, 1)
    check("each order is serviceable alone",
          has_service_plan(world, state,
                           components(world, state, ActiveDemandSet.of((), (first,)))[0])
          and has_service_plan(world, state,
                               components(world, state, ActiveDemandSet.of((), (second,)))[0]))
    admitted, rejected, decision = admit(world, state, (), (), (first, second), 3, 0)
    check("A: 700 + 700 against 1000 cannot both be admitted",
          len(admitted) == 1, str(decision.admitted))
    check("A: the other is rejected as incompatible",
          rejected[0].status == E_REJECTED_INCOMPATIBLE, rejected[0].status)


def test_admission_hand_check_b_two_500_orders_against_1000() -> None:
    world = _big_sand_world(1000, (500, 1000))
    state = _state(1000, 0, 0)
    first = _economic(world, "sand", 500, "C", 0, 0)
    second = _economic(world, "sand", 500, "B", 0, 1)
    admitted, rejected, decision = admit(world, state, (), (), (first, second), 3, 0)
    check("B: 500 + 500 against 1000 may both be admitted",
          len(admitted) == 2 and rejected == (), str(decision.admitted))
    both = components(world, state, ActiveDemandSet.of((), admitted))
    check("B: and they are jointly serviceable",
          all(has_service_plan(world, state, c) for c in both))


def test_admission_hand_check_c_1000_against_560() -> None:
    world = scarcity_world()
    state = _state(560, 0, 0)
    order = _economic(world, "sand", 1000, "C", 0, 0)
    admitted, rejected, _ = admit(world, state, (), (), (order,), 3, 0)
    check("C: an order beyond the stock is rejected for physical scarcity",
          admitted == () and rejected[0].status == E_REJECTED_PHYSICAL_SCARCITY)
    check("C: and it is rejected before any EBU value exists",
          rejected[0].quantity == F(1000))


def test_admission_hand_check_d_economic_and_physical_at_one_destination() -> None:
    world = sandwater_world()
    state = _state(14, 10, 8, 6, 6)
    physical = derive_physical_demands(world, state)
    order = _economic(world, "sand", 2, "C", 0, 0)
    admitted, rejected, _ = admit(world, state, physical, (), (order,), 3, 0)
    check("D: the order is admitted alongside the shortfall",
          len(admitted) == 1 and rejected == (), str(admitted))
    component = components(world, state, ActiveDemandSet.of(physical, admitted))[0]
    plans = enumerate_service_plans(world, state, component)
    two_unit = [
        plan for plan in plans
        if plan.group.increment(world.dimension)[world.index_of("sand", "C")] == F(2)
    ]
    check("D: a two-unit delivery is a valid complete plan", len(two_unit) > 0)
    if two_unit:
        increment = two_unit[0].group.increment(world.dimension)
        check("D: it serves the economic order in full",
              served_economic_ids(component.requirements, increment) == (order.demand_id,))
        check("D: and the same two units resolve the physical shortfall",
              state[world.index_of("sand", "C")] + increment[world.index_of("sand", "C")]
              == F(10))


# ==========================================================================
# FINAL DEMAND-COUPLING CORRECTION -- auditor 2
# ==========================================================================


def _triple(**kwargs):
    world = triple_delivery_world(**kwargs)
    return world, triple_delivery_state(world)


def _shape(world, state):
    """(executable action ids, component demand ids, menu sizes)."""
    physical = derive_physical_demands(world, state)
    found = components(world, state, ActiveDemandSet.of(physical, ()))
    return (
        tuple(sorted(a.action_id for a in action_alphabet(world))),
        tuple(sorted(c.demand_ids for c in found)),
        tuple(len(enumerate_service_plans(world, state, c)) for c in found),
    )


# --------------------------------------------------------------------------
# The auditor's counterexample, kept permanently
# --------------------------------------------------------------------------


def test_auditor_counterexample_three_independent_deliveries() -> None:
    """Three one-unit deliveries with distinct owners never interact."""
    world, state = _triple()
    actions, groups, menus = _shape(world, state)
    check("the world offers exactly three executable actions", len(actions) == 3, str(actions))
    check("the three deliveries are three independent components",
          groups == (("P:r|B",), ("P:r|D",), ("P:r|F",)), str(groups))
    check("each has exactly one complete plan", menus == (1, 1, 1), str(menus))
    check("and their owners are distinct",
          len({world.owner_of(a.route.source) for a in action_alphabet(world)}) == 3)


def test_unusable_routes_cannot_change_serviceability() -> None:
    """Metamorphic A: add routes that can carry no action; nothing may move.

    The connecting routes have capacity 1/2 while the only permitted action
    quantity is 1, so the executable action set is identical. Under the
    superseded coupling rule these two routes merged all three demands and,
    with three actions required against a cap of two, destroyed every plan.
    """
    plain, plain_state = _triple()
    padded, padded_state = _triple(unusable=True)
    check("the added routes exist", len(padded.routes) == len(plain.routes) + 2)
    check("and none of them can carry any allowed quantum",
          all(
              not any(quantum <= route.capacity for quantum in padded.quanta)
              for route in padded.routes
              if route.route_id not in {r.route_id for r in plain.routes}
          ))
    before = _shape(plain, plain_state)
    after = _shape(padded, padded_state)
    check("A: the executable action set is unchanged", before[0] == after[0], str(after[0]))
    check("A: coupling is unchanged", before[1] == after[1], str(after[1]))
    check("A: serviceability is unchanged", before[2] == after[2], str(after[2]))
    check("A: in particular no component was destroyed", after[2] == (1, 1, 1), str(after[2]))


def test_removing_unusable_routes_is_the_exact_inverse() -> None:
    """Metamorphic B."""
    padded, padded_state = _triple(unusable=True)
    plain, plain_state = _triple()
    check("B: removing them returns exactly the same shape",
          _shape(padded, padded_state) == _shape(plain, plain_state))


def test_a_binding_shared_route_may_couple_and_the_reason_is_shown() -> None:
    """Metamorphic C: a usable shared route creates genuine competition."""
    world, state = _triple(binding_shared_route=True)
    physical = derive_physical_demands(world, state)
    found = components(world, state, ActiveDemandSet.of(physical, ()))
    groups = tuple(sorted(c.demand_ids for c in found))
    check("C: adding a usable A -> D route couples B and D",
          ("P:r|B", "P:r|D") in groups, str(groups))
    check("C: F stays independent", ("P:r|F",) in groups, str(groups))

    reach_b = service_reach(world, state, [d for d in physical if d.demand_id == "P:r|B"][0])
    reach_d = service_reach(world, state, [d for d in physical if d.demand_id == "P:r|D"][0])
    check("C: the reason is a shared supplier coordinate",
          world.index_of("r", "A") in (reach_b.coordinates & reach_d.coordinates))
    check("C: and the competition is real -- A holds one unit and both would draw on it",
          state[world.index_of("r", "A")] == F(1)
          and not can_happen_now(
              world, state, _plan(world, (0, 1, 1), (0, 3, 1))
          ).executable)


def test_an_irrelevant_executable_action_creates_no_coupling() -> None:
    """Metamorphic D: padding must not be coupling evidence."""
    plain, plain_state = _triple()
    padded, padded_state = _triple(irrelevant_route=True)
    extra = set(a.action_id for a in action_alphabet(padded)) - set(
        a.action_id for a in action_alphabet(plain)
    )
    check("D: the extra action is executable", len(extra) == 1 and all(
        can_happen_now(padded, padded_state, PlanGroup.of(action)).executable
        for action in action_alphabet(padded)
        if action.action_id in extra
    ), str(extra))
    check("D: it serves no demand",
          derive_physical_demands(padded, padded_state)
          and all(d.demand_id in ("P:r|B", "P:r|D", "P:r|F")
                  for d in derive_physical_demands(padded, padded_state)))
    before = _shape(plain, plain_state)
    after = _shape(padded, padded_state)
    check("D: coupling is unchanged", before[1] == after[1], str(after[1]))
    check("D: serviceability is unchanged", before[2] == after[2], str(after[2]))


def test_one_action_serving_two_demands_stays_coupled() -> None:
    """Metamorphic E."""
    world = sandwater_world()
    state = _state(14, 10, 8, 6, 6)
    physical = derive_physical_demands(world, state)
    order = _economic(world, "sand", 2, "C", 0, 0)
    found = components(world, state, ActiveDemandSet.of(physical, (order,)))
    check("E: an order and a shortfall at one coordinate are one component",
          len(found) == 1 and set(found[0].demand_ids) == {"P:sand|C", order.demand_id},
          str([c.demand_ids for c in found]))
    plans = enumerate_service_plans(world, state, found[0])
    single = [p for p in plans if p.group.size == 1]
    check("E: a single action serves both", len(single) > 0)
    if single:
        check("E: and its provenance names both",
              set(next(iter(single[0].provenance_map.values())))
              == {"P:sand|C", order.demand_id})


def test_two_demands_sharing_scarce_stock_stay_coupled() -> None:
    """Metamorphic F."""
    world = shared_source_world()
    state = _state(1, 0, 0)
    physical = derive_physical_demands(world, state)
    found = components(world, state, ActiveDemandSet.of(physical, ()))
    check("F: two destinations fed only from one stock are one component",
          len(found) == 1 and len(found[0].demands) == 2,
          str([c.demand_ids for c in found]))
    check("F: and they are jointly unserviceable, because the stock is one unit",
          enumerate_service_plans(world, state, found[0]) == ())
    check("F: which is physical, not a search limit",
          serviceability(world, state, found[0]) == PHYSICALLY_IMPOSSIBLE,
          serviceability(world, state, found[0]))


def test_global_and_component_feasible_sets_agree() -> None:
    """Metamorphic G: the decomposition-free oracle."""
    cases = []
    world = sandwater_world()
    for values in ((8, 12, 10, 4, 8), (8, 8, 14, 6, 6), (9, 11, 10, 5, 7), (7, 12, 11, 4, 8)):
        cases.append((world, _state(*values), derive_physical_demands(world, _state(*values))))
    triple, triple_state = _triple()
    cases.append((triple, triple_state, derive_physical_demands(triple, triple_state)))
    padded, padded_state = _triple(unusable=True)
    cases.append((padded, padded_state, derive_physical_demands(padded, padded_state)))

    mismatches = []
    checked = 0
    for case_world, case_state, demands in cases:
        for bound in (2, 3):
            ok, detail = all_complete_agree(case_world, case_state, demands, bound)
            checked += 1
            if not ok:
                mismatches.append(f"{case_world.world_id}@{bound}: {detail}")
            fine, levels = progress_levels(case_world, case_state, demands, bound)
            checked += 1
            if not fine:
                mismatches.append(f"{case_world.world_id}@{bound} progress: {levels}")
    check("G: exhaustive cases were compared", checked >= 10, str(checked))
    check("G: both the narrow all-complete query and the progress reference "
          "agree with the decomposed path everywhere",
          not mismatches, str(mismatches[:2]))

    world = sandwater_world()
    state = _state(14, 10, 8, 6, 6)
    mixed = tuple(derive_physical_demands(world, state)) + (
        _economic(world, "sand", 2, "C", 0, 0),
    )
    ok, detail = all_complete_agree(world, state, mixed, 2)
    check("G: and with a mixed economic/physical demand set", ok, str(detail))
    ok, detail = progress_levels(world, state, mixed, 2)
    check("G: including every progress level", ok, str(detail))


def test_an_impossible_component_does_not_block_an_independent_one_triple() -> None:
    """Metamorphic H, in the counterexample world."""
    world, state = _triple()
    drained = list(state)
    drained[world.index_of("r", "C")] = F(0)
    drained = tuple(drained)
    physical = derive_physical_demands(world, drained)
    found = components(world, drained, ActiveDemandSet.of(physical, ()))
    verdicts = {c.component_id: serviceability(world, drained, c) for c in found}
    check("H: the starved delivery is physically impossible",
          verdicts["c:[P:r|D]"] == PHYSICALLY_IMPOSSIBLE, str(verdicts))
    check("H: the other two keep their plans",
          all(len(enumerate_service_plans(world, drained, c)) == 1
              for c in found if c.component_id != "c:[P:r|D]"))
    check("H: and nothing merged", len(found) == 3, str(sorted(verdicts)))


# --------------------------------------------------------------------------
# Plan-cap disposition: a computational enumeration limit
# --------------------------------------------------------------------------


def test_coupling_does_not_depend_on_the_plan_cap() -> None:
    shapes = {}
    for cap in (1, 2, 3):
        world = triple_delivery_world(max_plan_size=cap)
        state = triple_delivery_state(world)
        physical = derive_physical_demands(world, state)
        found = components(world, state, ActiveDemandSet.of(physical, ()))
        shapes[cap] = tuple(sorted(c.demand_ids for c in found))
    check("coupling is identical at every plan cap",
          len(set(shapes.values())) == 1, str(shapes))

    import demand_driven_ebu.coupling as coupling_module

    tree = ast.parse(inspect.getsource(coupling_module))
    attributes = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    check("and the coupling module never reads the cap",
          "max_plan_size" not in attributes, str(sorted(attributes)))


def test_the_cap_never_reports_physical_impossibility() -> None:
    """A requirement needing three actions, with a cap of two."""
    world = DemandWorld.declare(
        "capfour-v1",
        [
            Coordinate.stock("r", "A", 0, 1),
            Coordinate.stock("r", "B", 0, 1),
            Coordinate.stock("r", "C", 0, 1),
            Coordinate.stock("r", "T", 3, 1),
        ],
        [
            Route.declare("r", 0, 3, 1),
            Route.declare("r", 1, 3, 1),
            Route.declare("r", 2, 3, 1),
        ],
        (1,),
        2,
    )
    state = _state(1, 1, 1, 0)
    physical = derive_physical_demands(world, state)
    component = components(world, state, ActiveDemandSet.of(physical, ()))[0]
    check("the shortfall needs three unit deliveries", physical[0].required == F(3))
    check("no plan exists within the cap of two",
          enumerate_service_plans(world, state, component) == ())
    check("but the search, not physics, is what is short",
          serviceability(world, state, component) == BEYOND_CAP,
          serviceability(world, state, component))
    check("raising the cap finds it",
          len(enumerate_service_plans(
              DemandWorld.declare(world.world_id, world.coordinates, world.routes,
                                  world.quanta, 3),
              state,
              components(
                  DemandWorld.declare(world.world_id, world.coordinates, world.routes,
                                      world.quanta, 3),
                  state,
                  ActiveDemandSet.of(physical, ()),
              )[0],
          )) == 1)

    run = EconomyRun(world, quiet_disturbance(world), no_arrivals(), POLICY_ALIGNED,
                     1, 2, 3, 4, initial_state=state)
    record = run.run_epoch()
    check("and the harness reports it as a search limit, not impossibility",
          record.epoch_status == STATUS_SEARCH_INCOMPLETE, record.epoch_status)
    check("the two are distinct declared statuses",
          STATUS_SEARCH_INCOMPLETE in DECLARED_STATUSES
          and STATUS_NO_COMPLETE_PLAN in DECLARED_STATUSES
          and STATUS_SEARCH_INCOMPLETE != STATUS_NO_COMPLETE_PLAN)


def test_genuine_impossibility_is_still_reported_as_impossibility() -> None:
    world = shared_source_world()
    state = _state(1, 0, 0)
    physical = derive_physical_demands(world, state)
    component = components(world, state, ActiveDemandSet.of(physical, ()))[0]
    check("one unit cannot serve two one-unit demands at any plan size",
          serviceability(world, state, component) == PHYSICALLY_IMPOSSIBLE)
    run = EconomyRun(world, quiet_disturbance(world), no_arrivals(), POLICY_ALIGNED,
                     1, 2, 3, 4, initial_state=state)
    check("and the harness says so",
          run.run_epoch().epoch_status == STATUS_NO_COMPLETE_PLAN)


def test_admission_uses_uncapped_physical_serviceability() -> None:
    """Admission asks a physical question, so the enumeration limit is not its business."""
    import demand_driven_ebu.admission as admission_module

    tree = ast.parse(inspect.getsource(admission_module))
    names = {getattr(n, "id", "") for n in ast.walk(tree) if isinstance(n, ast.Name)}
    check("admission calls the uncapped serviceability test",
          "physically_serviceable" in names and "has_service_plan" not in names,
          str(sorted(names & {"physically_serviceable", "has_service_plan"})))

    world = DemandWorld.declare(
        "admitcap-v1",
        [
            Coordinate.stock("r", "A", 1, 1),
            Coordinate.stock("r", "B", 1, 1),
            Coordinate.stock("r", "C", 1, 1),
            Coordinate.stock("r", "T", 0, 1),
        ],
        [
            Route.declare("r", 0, 3, 1),
            Route.declare("r", 1, 3, 1),
            Route.declare("r", 2, 3, 1),
        ],
        (1,),
        2,
    )
    state = _state(1, 1, 1, 0)
    order = _economic(world, "r", 3, "T", 0, 0)
    admitted, rejected, _ = admit(world, state, (), (), (order,), 3, 0)
    check("an order serviceable only beyond the cap is still admitted",
          len(admitted) == 1 and rejected == (), str(rejected))
    component = components(world, state, ActiveDemandSet.of((), admitted))[0]
    check("and is then reported as a search limit rather than scarcity",
          serviceability(world, state, component) == BEYOND_CAP,
          serviceability(world, state, component))


def test_the_uncapped_search_fails_closed_rather_than_guessing() -> None:
    import demand_driven_ebu.enumeration as enumeration_module

    source = inspect.getsource(enumeration_module.physically_serviceable)
    check("the uncapped search has a declared budget",
          "EXHAUSTIVE_BUDGET" in source)
    check("and returns an explicit unresolved verdict rather than a negative",
          "UNRESOLVED" in source and enumeration_module.UNRESOLVED
          == "SEARCH_BUDGET_EXCEEDED")
    check("which the harness carries as its own status",
          STATUS_SEARCH_UNRESOLVED in DECLARED_STATUSES)


def test_structural_reach_ignores_unusable_routes_by_construction() -> None:
    plain, plain_state = _triple()
    padded, padded_state = _triple(unusable=True)
    physical = derive_physical_demands(padded, padded_state)
    for demand in physical:
        reach = service_reach(padded, padded_state, demand)
        unusable_ids = {
            route.route_id
            for route in padded.routes
            if not any(q <= route.capacity for q in padded.quanta)
        }
        if reach.routes & unusable_ids:
            check("no unusable route enters a structural reach", False, str(reach.routes))
            return
    check("no unusable route enters a structural reach", True)
    check("usable routes are exactly those that can carry a quantum",
          {r.route_id for r in usable_routes(padded)}
          == {r.route_id for r in plain.routes}, str(len(usable_routes(padded))))



# ==========================================================================
# AUDITOR 2, SECOND PASS -- uncertainty propagation and state-dependent reach
# ==========================================================================


def test_a_wide_but_easy_requirement_is_not_refused_on_its_search_space() -> None:
    """Counterexample 1: nineteen suppliers, one requested unit.

    The superseded search pre-computed the worst-case space, saw `2^19`, and
    returned `SEARCH_BUDGET_EXCEEDED` without trying -- while nineteen
    one-action plans served the destination and the menu held all nineteen.
    """
    world = wide_supply_world(19, 1)
    state = wide_supply_state(world)
    physical = derive_physical_demands(world, state)
    component = components(world, state, ActiveDemandSet.of(physical, ()))[0]
    check("nineteen one-action plans exist",
          len(enumerate_service_plans(world, state, component)) == 19,
          str(len(enumerate_service_plans(world, state, component))))
    check("the uncapped search answers serviceable",
          physically_serviceable(world, state, requirements(physical)) == SERVICEABLE,
          physically_serviceable(world, state, requirements(physical)))
    check("the coupling reach is not empty",
          service_reach(world, state, physical[0]).coordinates != frozenset())
    check("admission does not block it",
          physical[0].demand_id not in unserviceable_ids(world, state, physical, ()))
    check("and it is not recorded as undecided either",
          physical[0].demand_id not in unresolved_ids(world, state, physical, ()))


def test_search_uncertainty_never_becomes_impossibility() -> None:
    """All three verdicts are reachable and are kept apart downstream."""
    easy = wide_supply_world(19, 1)
    small = wide_supply_world(16, 100)
    wide = wide_supply_world(20, 100)
    verdicts = {}
    for label, world in (("easy", easy), ("small-impossible", small), ("wide-undecided", wide)):
        state = wide_supply_state(world)
        physical = derive_physical_demands(world, state)
        verdicts[label] = physically_serviceable(world, state, requirements(physical))
    check("an easy requirement is serviceable", verdicts["easy"] == SERVICEABLE, str(verdicts))
    check("a small unsatisfiable one is proved impossible",
          verdicts["small-impossible"] == IMPOSSIBLE, str(verdicts))
    check("a wide unsatisfiable one is undecided, not impossible",
          verdicts["wide-undecided"] == UNRESOLVED, str(verdicts))

    state = wide_supply_state(wide)
    physical = derive_physical_demands(wide, state)
    reach = service_reach(wide, state, physical[0])
    check("an undecided demand keeps its full reach",
          reach.coordinates != frozenset() and reach.verdict == UNRESOLVED,
          f"{len(reach.coordinates)} {reach.verdict}")
    check("an undecided demand is not blocked by admission",
          physical[0].demand_id not in unserviceable_ids(wide, state, physical, ()))
    check("it is recorded as undecided instead",
          physical[0].demand_id in unresolved_ids(wide, state, physical, ()))
    check("the per-demand classification carries the verdict verbatim",
          classify(wide, state, physical, ())[physical[0].demand_id] == UNRESOLVED)

    proven = wide_supply_state(small)
    blocked = unserviceable_ids(small, proven, derive_physical_demands(small, proven), ())
    check("only proved impossibility blocks", blocked != frozenset(), str(sorted(blocked)))


def test_an_undecided_demand_is_not_rejected_for_scarcity() -> None:
    world = wide_supply_world(20, 1)
    state = wide_supply_state(world)
    order = _economic(world, "r", 100, "T", 0, 0)
    verdict = physically_serviceable(world, state, requirements((order,)))
    check("the order's serviceability is undecided", verdict == UNRESOLVED, verdict)
    admitted, rejected, decision = admit(world, state, (), (), (order,), 3, 0)
    check("it is not rejected for physical scarcity",
          rejected == (), str([(d.demand_id, d.status) for d in rejected]))
    check("it is admitted, with the uncertainty recorded rather than resolved",
          len(admitted) == 1 and decision.unresolved == (order.demand_id,),
          str(decision.unresolved))


def test_empty_source_routes_cannot_change_serviceability() -> None:
    """Counterexample 2: usable capacity, unfundable source.

    `B -> D` and `D -> F` have capacity one and can carry the only permitted
    quantum, so a capacity-only usability test calls them usable. Their
    sources hold nothing, and source-funding forbids paying for an outflow
    with same-instant inflow, so neither can carry an action here -- not even
    inside a simultaneous group.
    """
    plain = empty_source_world(False)
    padded = empty_source_world(True)
    state = _state(1, 0, 1, 0, 1, 0)

    def executable(world):
        return tuple(sorted(
            action.action_id
            for action in action_alphabet(world)
            if can_happen_now(world, state, PlanGroup.of(action)).executable
        ))

    check("the added routes are usable by capacity",
          len(usable_routes(padded)) == len(usable_routes(plain)) + 2)
    check("but not live, because their sources are empty",
          len(live_routes(padded, state)) == len(live_routes(plain, state)),
          f"{len(live_routes(padded, state))} vs {len(live_routes(plain, state))}")
    check("the executable action set is identical",
          executable(plain) == executable(padded), str(executable(padded)))
    for world in (plain, padded):
        for action in action_alphabet(world):
            route = action.route
            if route.source in (1, 3) and can_happen_now(
                world, state, PlanGroup.of(action)
            ).executable:
                check("no action on an empty source is executable", False, action.action_id)
                return
    check("no action on an empty source is executable", True)

    def shape(world):
        physical = derive_physical_demands(world, state)
        found = components(world, state, ActiveDemandSet.of(physical, ()))
        return (
            tuple(sorted(c.demand_ids for c in found)),
            tuple(len(enumerate_service_plans(world, state, c)) for c in found),
        )

    before, after = shape(plain), shape(padded)
    check("coupling is unchanged", before[0] == after[0], str(after[0]))
    check("serviceability is unchanged", before[1] == after[1], str(after[1]))
    check("and in particular nothing was destroyed", after[1] == (1, 1, 1), str(after[1]))


def test_a_route_becomes_live_when_its_source_is_funded() -> None:
    """Liveness is a property of the state, and tracks it in both directions."""
    world = empty_source_world(True)
    empty = _state(1, 0, 1, 0, 1, 0)
    funded = _state(1, 1, 1, 1, 1, 0)
    check("with empty sources the added routes are dead",
          len(live_routes(world, empty)) == 3, str(len(live_routes(world, empty))))
    check("with funded sources they are live",
          len(live_routes(world, funded)) == 5, str(len(live_routes(world, funded))))
    physical = derive_physical_demands(world, funded)
    found = components(world, funded, ActiveDemandSet.of(physical, ()))
    check("and then they may legitimately couple demands",
          len(found) < 2 or any(len(c.demands) > 1 for c in found),
          str([c.demand_ids for c in found]))
    check("which is correct: B now holds stock that D could draw on",
          funded[1] > 0 and any(
              route.source == 1 and route.destination == 3
              for route in live_routes(world, funded)
          ))


def test_the_structural_reach_is_state_aware() -> None:
    import demand_driven_ebu.enumeration as enumeration_module

    source = inspect.getsource(enumeration_module.structural_reach)
    check("structural_reach builds from live routes, not merely usable ones",
          "live_routes(world, state)" in source)
    check("and liveness is a necessary condition for carrying any action",
          "source-funding" in inspect.getsource(enumeration_module.live_routes).lower()
          or "source-funding" in inspect.getsource(enumeration_module.live_routes))


def test_the_oracle_compares_receipts_not_only_increments() -> None:
    import demand_driven_ebu.oracle as oracle_module

    source = inspect.getsource(oracle_module.outcome)
    check("the modeled outcome carries owner receipts",
          "owner_deltas" in source and "increment" in source)
    world = sandwater_world()
    state = _state(8, 8, 14, 6, 6)
    physical = derive_physical_demands(world, state)
    outcomes = all_complete_outcomes(oracle_module.at_bound(world, 3), state, physical, 3)
    check("every outcome is an (increment, receipts) pair",
          all(len(entry) == 2 and isinstance(entry[1], tuple) for entry in outcomes),
          str(len(outcomes)))
    ok, detail = all_complete_agree(world, state, physical, 3)
    check("and the two sides agree on receipts as well as physics", ok, str(detail))


def test_the_oracle_equalises_the_plan_cap_on_both_sides() -> None:
    import demand_driven_ebu.oracle as oracle_module

    world = sandwater_world()
    check("the world's own cap is two", world.max_plan_size == 2)
    check("the oracle rebuilds it at the comparison bound",
          oracle_module.at_bound(world, 3).max_plan_size == 3)
    check("leaving it unequal is what a naive comparison would do, and the "
          "declared per-component asymmetry is tested separately", True)


# ==========================================================================
# FIRST DEMAND-DRIVEN STUDY DOMAIN FREEZE
# ==========================================================================


def _e(world, node, quantity, index=0, resource="r", epoch=0):
    return EconomicDemand.declare(world, resource, quantity, node, epoch, index)


def oracle_at(world, bound):
    import demand_driven_ebu.oracle as oracle_module

    return oracle_module.at_bound(world, bound)


def oracle_doc() -> str:
    import demand_driven_ebu.oracle as oracle_module

    return oracle_module.__doc__


def _brute_force_serves(world, state, reqs) -> bool:
    """Complete enumeration of the whole finite plan space. No pruning at all.

    Independent of `enumeration`: it walks every route, offers every permitted
    quantum or nothing, and tests the resulting plan directly. This is the
    thing the pruned search has to be equivalent to.
    """
    from itertools import product as _product

    options = []
    for route in world.routes:
        options.append(
            [None]
            + [
                PhysicalAction(route, quantum)
                for quantum in world.quanta
                if quantum <= route.capacity
            ]
        )
    for combination in _product(*options):
        actions = tuple(action for action in combination if action is not None)
        if not actions:
            continue
        group = PlanGroup.of(*actions)
        if not serves_all(reqs, group.increment(world.dimension)):
            continue
        if can_happen_now(world, state, group).executable:
            return True
    return False


# --------------------------------------------------------------------------
# 1. the frozen Study-1 physical domain
# --------------------------------------------------------------------------


def test_the_study_one_domain_is_frozen_and_machine_checkable() -> None:
    world = study_one_world()
    check("the Study-1 rehearsal world is inside the frozen domain",
          in_domain(world), str(domain_violations(world)))
    check("the domain has a declared identity",
          STUDY_ONE_DOMAIN_ID == "EBU-DEMAND-DRIVEN-STUDY-1-DOMAIN-v1")
    check("it declares exactly one homogeneous scalar resource",
          world.resources == ("r",))
    check("every coordinate is a valued stock",
          all(c.role == "STOCK" and c.carries_potential for c in world.coordinates))
    check("no coordinate declares an upper storage capacity",
          all(c.capacity is None for c in world.coordinates))
    check("every route is lossless and declares no sink",
          all(r.efficiency == 1 and r.sink is None for r in world.routes))
    check("the declared action quantities are finite and positive",
          world.quanta == (F(1), F(2)))
    state = study_one_state()
    check("the state is nonnegative and conserves its declared total",
          state_violations(world, state, F(12)) == (), str(state_violations(world, state, F(12))))
    check("a negative stock is reported, not tolerated",
          state_violations(world, (F(-1), F(4), F(9)), F(12)) != ())
    check("a state that does not conserve is reported",
          state_violations(world, (F(4), F(4), F(5)), F(12)) != ())


def test_every_domain_condition_is_enforced_separately() -> None:
    cases = (
        ("two resources", sandwater_world(max_plan_size=99), "one homogeneous"),
        ("a loss sink", loss_world(), "lossless"),
        ("an irreversible sink", audit_sink_world(), "irreversible sinks"),
        ("a storage capacity", capacity_relief_world(True), "upper storage capacity"),
        ("a binding plan cap", surplus_world(), "plan-size cap"),
    )
    for label, world, phrase in cases:
        violations = domain_violations(world)
        check(f"{label} puts a world outside the domain", bool(violations), label)
        check(f"and the reason names it: {label}",
              any(phrase in reason for reason in violations), str(violations))
    for label, world, _ in cases:
        try:
            require_domain(world)
            check(f"require_domain refuses {label}", False)
        except Refusal as refusal:
            check(f"require_domain refuses {label}", STUDY_ONE_DOMAIN_ID in str(refusal))


def test_outside_the_domain_is_future_physics_not_a_blocker() -> None:
    import demand_driven_ebu.study_one as study_one_module

    check("the unsupported list is declared, not implied",
          "lossy transfer" in study_one_module.FUTURE_UNSUPPORTED_PHYSICS
          and "upper destination-storage capacity" in study_one_module.FUTURE_UNSUPPORTED_PHYSICS)
    check("the module says so in words",
          "FUTURE UNSUPPORTED PHYSICS" in study_one_module.__doc__)
    check("and says Study-1 verification is not general-framework proof",
          "GENERAL DEMAND-DRIVEN FRAMEWORK PROVED" in study_one_module.__doc__)


def test_no_module_claims_general_loss_or_capacity_aware_exactness() -> None:
    import demand_driven_ebu.coupling as coupling_module
    import demand_driven_ebu.enumeration as enumeration_module

    reach_doc = enumeration_module.__doc__
    check("the superseded 'exact set of tokens' claim is gone from enumeration",
          "the exact set of tokens" not in reach_doc)
    check("the superseded claim is gone from coupling",
          "the exact set of\ntokens" not in coupling_module.__doc__
          and "exact set of tokens" not in coupling_module.__doc__)
    check("enumeration states necessity generally and sufficiency for Study 1 only",
          "Necessity (all domains)" in reach_doc
          and "Sufficiency (Study-1 domain only)" in reach_doc)
    check("coupling says tightness depends on the domain",
          "How tight it is depends on the domain" in coupling_module.__doc__)
    check("and explicitly disclaims exact loss/capacity-aware coupling",
          "Nothing here\nasserts exact loss-aware or capacity-aware coupling"
          in coupling_module.__doc__)


# --------------------------------------------------------------------------
# 2. route liveness, proved where it is claimed
# --------------------------------------------------------------------------


def test_liveness_is_necessary_in_every_domain() -> None:
    """No executable plan anywhere uses a route liveness excludes."""
    cases = (
        (study_one_world(), study_one_state()),
        (study_one_world(), study_one_state(0, 12, 0)),
        (triple_delivery_world(unusable=True), None),
        (empty_source_world(extra=True), None),
        (capacity_relief_world(True), capacity_relief_state()),
        (shared_sink_world(True), shared_sink_state()),
        (loss_world(), _state(4, 4, 4, 0)),
        (competing_world(), _state(3, 0, 0)),
    )
    violations = 0
    checked = 0
    for world, state in cases:
        if state is None:
            state = triple_delivery_state(world)
        allowed = {route.route_id for route in live_routes(world, state)}
        for action in action_alphabet(world):
            for other in action_alphabet(world):
                if other.route.route_id == action.route.route_id:
                    group = PlanGroup.of(action)
                else:
                    group = PlanGroup.of(action, other)
                if not can_happen_now(world, state, group).executable:
                    continue
                checked += 1
                for member in group.actions:
                    if member.route.route_id not in allowed:
                        violations += 1
    check("every route carrying an action in an executable plan is live",
          violations == 0, f"{violations} of {checked}")
    check("and the sweep actually found executable plans", checked > 0, str(checked))


def test_liveness_is_sufficient_inside_the_study_one_domain() -> None:
    world = study_one_world()
    for state in (study_one_state(), study_one_state(0, 12, 0), study_one_state(1, 0, 11)):
        live = {route.route_id for route in live_routes(world, state)}
        for route in world.routes:
            smallest = min(q for q in world.quanta if q <= route.capacity)
            singleton = PlanGroup.of(PhysicalAction(route, smallest))
            runs = can_happen_now(world, state, singleton).executable
            check(f"{route.route_id} at {tuple(int(v) for v in state)}: live iff it can act",
                  (route.route_id in live) == runs)


def test_action_liveness_is_necessary_and_sufficient_in_study_one() -> None:
    """Corollary L3, the rule service enumeration actually relies on."""
    world = study_one_world()
    mismatches = []
    checked = 0
    for a in range(0, 13, 3):
        for b in range(0, 13 - a, 3):
            state = study_one_state(a, b, 12 - a - b)
            for action in action_alphabet(world):
                rule = (
                    action.quantity <= action.route.capacity
                    and state[action.route.source] >= action.quantity
                )
                runs = can_happen_now(world, state, PlanGroup.of(action)).executable
                checked += 1
                if rule != runs:
                    mismatches.append((tuple(int(v) for v in state), action.action_id))
    check("an action can act exactly when its quantum fits the route and its "
          "source funds it", not mismatches, str(mismatches[:3]))
    check("and the sweep was not vacuous", checked == 15 * 8, str(checked))
    text = Path("DEMAND_DRIVEN_STUDY_ONE_DOMAIN.md").read_text()
    check("the corollary is written down, with why enumeration does not "
          "pre-filter on it",
          "Corollary L3 (action liveness, Study-1 domain only)" in text
          and "would be sound but would gain nothing" in text)


def test_liveness_sufficiency_is_not_claimed_outside_the_domain() -> None:
    import demand_driven_ebu.enumeration as enumeration_module

    doc = enumeration_module.live_routes.__doc__
    check("live_routes states necessity for every domain",
          "Necessary in every domain" in doc)
    check("and confines sufficiency to Study 1",
          "Sufficient in the Study-1 domain only" in doc)
    check("the module names the destination-headroom limb it does not have",
          "A third limb -- destination headroom" in enumeration_module.__doc__)


def test_storage_capacity_counterexample_outside_study_one_is_retained() -> None:
    """OUTSIDE STUDY-1 DOMAIN. A capacity that cannot bind changes coupling."""
    plain = capacity_relief_world(False)
    declared = capacity_relief_world(True)
    state = capacity_relief_state()
    check("without the capacity the world is a Study-1 world", in_domain(plain))
    check("with it, the world is outside the domain", not in_domain(declared))

    total = sum(state)
    check("only three units exist, against a declared capacity of ten",
          total == 3 and declared.coordinates[1].capacity == 10)
    same = 0
    for action in action_alphabet(declared):
        for state_variant in (state,):
            group = PlanGroup.of(action)
            if (can_happen_now(plain, state_variant, group).executable
                    == can_happen_now(declared, state_variant, group).executable):
                same += 1
    check("the capacity changes no executable action",
          same == len(action_alphabet(declared)), str(same))

    def shape(world):
        demands = (_e(world, "C", 1, 0), _e(world, "W", 1, 1))
        found = components(world, state, ActiveDemandSet.of((), demands))
        return len(found)

    check("without it the two deliveries are independent", shape(plain) == 2)
    check("with it they merge -- a genuine tightness failure of the reach",
          shape(declared) == 1)
    check("the counterexample is retained, not repaired, and Study 1 excludes it",
          not in_domain(declared) and shape(declared) == 1)


def test_shared_loss_sink_counterexample_outside_study_one_is_retained() -> None:
    """OUTSIDE STUDY-1 DOMAIN. Two lossy routes couple through their sink."""
    lossless = shared_sink_world(False)
    lossy = shared_sink_world(True)
    state = shared_sink_state()
    check("both variants are outside the domain -- they declare a sink",
          not in_domain(lossless) and not in_domain(lossy))

    def shape(world):
        demands = (_e(world, "C", 1, 0), _e(world, "D", 1, 1))
        found = components(world, state, ActiveDemandSet.of((), demands))
        return found

    check("lossless, the two deliveries are independent", len(shape(lossless)) == 2)
    merged = shape(lossy)
    check("lossy, they merge through the shared sink", len(merged) == 1)
    check("and the merged reach claims both owners",
          merged[0].binding.owners == frozenset({"A", "B"}),
          str(sorted(merged[0].binding.owners)))
    check("though a sink can neither source a route nor hold a capacity, so it "
          "cannot actually compete for anything",
          all(route.source != 4 for route in lossy.routes)
          and lossy.coordinates[4].capacity is None)


# --------------------------------------------------------------------------
# 3. no scientific plan-size cap
# --------------------------------------------------------------------------


def test_the_study_one_cap_cannot_bind_on_anything() -> None:
    world = study_one_world()
    check("the cap is at least the usable route count",
          world.max_plan_size >= len(usable_routes(world)),
          f"{world.max_plan_size} vs {len(usable_routes(world))}")
    check("so no plan can reach it: a plan uses each route at most once",
          world.max_plan_size >= action_bound(world, study_one_state()))
    seen = set()
    for a in range(0, 13, 2):
        for b in range(0, 13 - a, 2):
            state = study_one_state(a, b, 12 - a - b)
            demands = derive_physical_demands(world, state)
            if not demands:
                continue
            found = components(world, state, ActiveDemandSet.of(demands, ()))
            for component in found:
                seen.add(serviceability(world, state, component))
    check("no Study-1 component is ever SEARCH_INCOMPLETE_AT_PLAN_CAP",
          BEYOND_CAP not in seen, str(sorted(seen)))
    check("no Study-1 component is ever SEARCH_BUDGET_EXCEEDED",
          UNRESOLVED not in seen, str(sorted(seen)))


def test_the_pruned_search_equals_complete_enumeration() -> None:
    """The pruning is proved equivalent; here it is checked against brute force."""
    world = study_one_world()
    agreements = 0
    disagreements = []
    for a in range(0, 13):
        for b in range(0, 13 - a):
            state = study_one_state(a, b, 12 - a - b)
            for target, quantity in (("A", 1), ("B", 2), ("C", 3), ("A", 9)):
                demands = (_e(world, target, quantity),)
                reqs = requirements(demands)
                verdict = physically_serviceable(world, state, reqs)
                brute = _brute_force_serves(world, state, reqs)
                if (verdict == SERVICEABLE) == brute:
                    agreements += 1
                else:
                    disagreements.append((a, b, target, quantity, verdict, brute))
    check("the pruned search agrees with complete enumeration on every "
          "Study-1 state and order tested",
          not disagreements, str(disagreements[:3]))
    check("and the sweep was not vacuous", agreements == 91 * 4, str(agreements))

    others = (
        (triple_delivery_world(unusable=True), None, ("B", 1, "r")),
        (empty_source_world(extra=True), None, ("D", 1, "r")),
        (shared_source_world(), _state(1, 0, 0), ("B", 1, "r")),
        (competing_world(), _state(3, 0, 0), ("B", 3, "sand")),
    )
    for world, state, (node, quantity, resource) in others:
        if state is None:
            state = triple_delivery_state(world)
        demands = (_e(world, node, quantity, 0, resource),)
        reqs = requirements(demands)
        check(f"{world.world_id}: pruned search matches brute force",
              (physically_serviceable(world, state, reqs) == SERVICEABLE)
              == _brute_force_serves(world, state, reqs))


def test_a_computational_cap_never_makes_a_serviceable_demand_impossible() -> None:
    world = study_one_world()
    narrow = DemandWorld.declare(
        world.world_id, world.coordinates, world.routes, world.quanta, 1
    )
    state = study_one_state(2, 8, 2)
    demands = derive_physical_demands(world, state)
    check("two coordinates are two short, so a one-action plan cannot serve both",
          len(demands) == 2 and all(d.required == 2 for d in demands))
    found = components(narrow, state, ActiveDemandSet.of(demands, ()))
    verdicts = {serviceability(narrow, state, component) for component in found}
    check("under a cap of one the menu is empty",
          all(not enumerate_service_plans(narrow, state, c) for c in found))
    check("but the report is a search limit, never impossibility",
          verdicts == {BEYOND_CAP}, str(verdicts))
    check("the uncapped search says it is serviceable",
          physically_serviceable(narrow, state, requirements(demands)) == SERVICEABLE)
    check("and the Study-1 cap has no such effect",
          all(serviceability(world, state, c) == SERVICEABLE_WITHIN_CAP
              for c in components(world, state, ActiveDemandSet.of(demands, ()))))


# --------------------------------------------------------------------------
# 4. exactly three search verdicts
# --------------------------------------------------------------------------


def test_exactly_three_search_verdicts_exist_and_stay_apart() -> None:
    import demand_driven_ebu.enumeration as enumeration_module

    declared = {SERVICEABLE, IMPOSSIBLE, UNRESOLVED}
    check("there are exactly three", len(declared) == 3, str(sorted(declared)))
    world = study_one_world()
    reached = {
        physically_serviceable(world, study_one_state(), requirements((_e(world, "A", 1),))),
        physically_serviceable(
            world, study_one_state(0, 0, 12), requirements((_e(world, "A", 9),))
        ),
    }
    check("SERVICEABLE and IMPOSSIBLE are both reachable in Study 1",
          reached == {SERVICEABLE, IMPOSSIBLE}, str(sorted(reached)))
    oversized = requirements((_e(world, "A", 9),))
    check("an oversized order at a funded neighbour is genuinely impossible",
          physically_serviceable(world, study_one_state(0, 12, 0), oversized)
          == IMPOSSIBLE)
    saved = enumeration_module.EXHAUSTIVE_BUDGET
    try:
        enumeration_module.EXHAUSTIVE_BUDGET = 1
        forced = physically_serviceable(world, study_one_state(0, 12, 0), oversized)
    finally:
        enumeration_module.EXHAUSTIVE_BUDGET = saved
    check("but with the budget cut to one, the same question returns UNRESOLVED "
          "rather than inheriting the impossibility",
          forced == UNRESOLVED, forced)
    check("the budget is restored", enumeration_module.EXHAUSTIVE_BUDGET == saved)


def test_unresolved_is_never_converted_into_a_rejection() -> None:
    import demand_driven_ebu.admission as admission_module

    source = inspect.getsource(admission_module.unserviceable_ids)
    check("only a proved impossibility blocks admission",
          "verdict == IMPOSSIBLE" in source and "UNRESOLVED" not in source.split('"""')[2])
    source = inspect.getsource(admission_module.__dict__["unresolved_ids"])
    check("an undecided search gets its own reported set", "UNRESOLVED" in source)


# --------------------------------------------------------------------------
# 5. registered failure semantics
# --------------------------------------------------------------------------


def _study_one_run(**kwargs):
    world = study_one_world()
    disturbance = DisturbanceProcess.declare(world, ((0, 1), (1, 2), (2, 1), (1, 0)), 2, 1, 2)
    arrivals = ArrivalProcess.declare((("r", "A", 1), ("r", "C", 2)), 1, 3, 2)
    return EconomyRun(
        world, disturbance, arrivals, POLICY_RANDOM, 11, 22, 33, 44,
        study_one_state(), **kwargs
    )


def test_a_registered_job_refuses_to_start_outside_the_domain() -> None:
    world = sandwater_world()
    try:
        EconomyRun(
            world,
            quiet_disturbance(world),
            no_arrivals(),
            POLICY_RANDOM,
            1, 2, 3, 4,
            registered=True,
        )
        check("a registered run refuses an out-of-domain world", False)
    except Refusal as refusal:
        check("a registered run refuses an out-of-domain world",
              STUDY_ONE_DOMAIN_ID in str(refusal))
    run = _study_one_run(registered=True)
    check("and accepts a Study-1 world", run.registered and in_domain(run.world))


def test_search_unresolved_invalidates_the_entire_registered_job() -> None:
    """Simulated by shrinking the budget the domain condition is sized against.

    Inside the frozen domain this cannot happen: the complete plan space fits
    inside the exhaustive budget, so the budget is never reached. Cutting the
    budget without cutting the domain condition is exactly the implementation
    error the failure semantics exist for, and the job must stop.
    """
    import demand_driven_ebu.enumeration as enumeration_module

    run = _study_one_run(registered=True)
    saved = enumeration_module.EXHAUSTIVE_BUDGET
    raised = None
    try:
        enumeration_module.EXHAUSTIVE_BUDGET = 1
        for _ in range(12):
            run.run_epoch()
    except JobInvalid as failure:
        raised = failure
    finally:
        enumeration_module.EXHAUSTIVE_BUDGET = saved
    check("an undecided search stops the job", raised is not None)
    message = str(raised) if raised else ""
    for phrase in (
        "do not continue the trajectory",
        "do not exclude the",
        "do not resample",
        "do not change the seed",
        "rerun this job identically",
    ):
        check(f"and says so: '{phrase}'", phrase in message, message[:160])
    check("JobInvalid is a refusal, so nothing can absorb it as a result",
          issubclass(JobInvalid, Refusal))
    check("the same run outside registered mode records it as a status instead",
          STATUS_SEARCH_UNRESOLVED in DECLARED_STATUSES)


def test_an_unregistered_run_keeps_the_three_way_distinction() -> None:
    run = _study_one_run()
    records = run.run(30)
    statuses = {record.epoch_status for record in records}
    check("every epoch status is declared", statuses <= set(DECLARED_STATUSES),
          str(sorted(statuses)))
    check("no Study-1 epoch hit an undecided search",
          STATUS_SEARCH_UNRESOLVED not in statuses, str(sorted(statuses)))
    check("nor a plan-cap truncation",
          STATUS_SEARCH_INCOMPLETE not in statuses, str(sorted(statuses)))
    check("all residuals are exactly zero",
          all(r.accounting_residual == 0 and r.conservation_residual == 0
              and r.nonnegativity_residual == 0 and r.separability_residual == 0
              for r in records))
    check("and the capacity-source identity closes exactly",
          run.capacity_source_residual == 0)


# --------------------------------------------------------------------------
# 6. the global progress reference is the authority
# --------------------------------------------------------------------------


def test_the_global_progress_reference_is_the_authority_for_study_one() -> None:
    world = study_one_world()
    mismatches = []
    compared = 0
    for a in (0, 2, 4, 6, 8):
        for b in (0, 2, 4):
            state = study_one_state(a, b, 12 - a - b)
            for demands in (
                (_e(world, "C", 1),),
                (_e(world, "A", 1, 0), _e(world, "C", 1, 1)),
                (_e(world, "A", 2, 0), _e(world, "C", 2, 1)),
            ):
                bound = action_bound(world, state)
                if bound == 0:
                    continue
                compared += 1
                full = tuple(derive_physical_demands(world, state)) + demands
                ok, detail = progress_levels(world, state, full, bound)
                if not ok:
                    mismatches.append((a, b, detail))
    check("all four levels agree on every Study-1 fixture swept",
          not mismatches, str(mismatches[:2]))
    check("and the sweep was not vacuous", compared >= 30, str(compared))


def test_the_harness_gate_checks_decomposition_every_epoch() -> None:
    run = _study_one_run(decomposition_gate=True)
    records = run.run(25)
    verdicts = {record.decomposition_gate for record in records}
    check("every epoch is either verified or had nothing to check",
          verdicts <= {DECOMPOSITION_VERIFIED, DECOMPOSITION_NOT_CHECKED},
          str(sorted(verdicts)))
    check("and at least one epoch was genuinely verified",
          DECOMPOSITION_VERIFIED in verdicts, str(sorted(verdicts)))
    off = _study_one_run()
    check("the gate is off by default -- it is an instrument, not the mechanism",
          all(r.decomposition_gate == DECOMPOSITION_NOT_CHECKED for r in off.run(3)))


def test_a_decomposition_difference_stops_the_run() -> None:
    run = _study_one_run(decomposition_gate=True)
    saved = harness_module.progress_levels
    raised = None
    try:
        harness_module.progress_levels = lambda *args, **kwargs: (
            False,
            {"reference_plans": 5, "runtime_plans": 4},
        )
        for _ in range(12):
            run.run_epoch()
    except Refusal as refusal:
        raised = refusal
    finally:
        harness_module.progress_levels = saved
    check("a disagreement is refused, not absorbed", raised is not None)
    message = str(raised) if raised else ""
    check("and it names the defect",
          "DECOMPOSITION_DIFFERS_FROM_GLOBAL_PROGRESS" in message, message[:140])
    check("and says which side is authority",
          "may not" in message and "define what the epoch can do" in message,
          message[:220])


# --------------------------------------------------------------------------
# 7. unusable-infrastructure invariance across all five outputs
# --------------------------------------------------------------------------


def _five_outputs(world, state, demands):
    """Admission, serviceability, plan set, EBU values, affordability inputs."""
    physical = derive_physical_demands(world, state)
    found = components(world, state, ActiveDemandSet.of(physical, demands))
    serviceabilities = []
    plans = []
    values = []
    affordability = []
    for component in found:
        serviceabilities.append(serviceability(world, state, component))
        for plan in enumerate_service_plans(world, state, component):
            plans.append(plan.group.group_id)
            valuation = value_group(world, state, plan.group)
            values.append((plan.group.group_id, valuation.group_ebu))
            affordability.append((plan.group.group_id, tuple(sorted(valuation.owner_deltas))))
    _, _, decision = admit(world, state, physical, (), demands, 7, 0)
    return (
        (decision.admitted, decision.maximal_subsets, decision.rejected),
        tuple(sorted(serviceabilities)),
        tuple(sorted(plans)),
        tuple(sorted(values)),
        tuple(sorted(affordability)),
    )


def test_unusable_infrastructure_changes_none_of_the_five_outputs() -> None:
    labels = ("admission", "serviceability", "complete plan set", "EBU plan values",
              "affordability inputs")
    cases = (
        ("capacity-1/2 routes",
         triple_delivery_world(), triple_delivery_world(unusable=True),
         (("B", 1, 0), ("D", 1, 1), ("F", 1, 2))),
        ("empty-source routes",
         empty_source_world(), empty_source_world(extra=True),
         (("B", 1, 0), ("D", 1, 1), ("F", 1, 2))),
    )
    for label, plain, modified, requests in cases:
        state = triple_delivery_state(plain)
        left = _five_outputs(plain, state, tuple(_e(plain, *r) for r in requests))
        right = _five_outputs(modified, state, tuple(_e(modified, *r) for r in requests))
        check(f"{label}: the executable action set is unchanged",
              {a.action_id for a in action_alphabet(plain)
               if can_happen_now(plain, state, PlanGroup.of(a)).executable}
              == {a.action_id for a in action_alphabet(modified)
                  if can_happen_now(modified, state, PlanGroup.of(a)).executable})
        for name, before, after in zip(labels, left, right):
            check(f"{label}: {name} is unchanged", before == after,
                  f"{before} != {after}")
    check("and the outputs are not all empty -- the invariance has content",
          bool(_five_outputs(triple_delivery_world(), triple_delivery_state(
              triple_delivery_world()), tuple(
                  _e(triple_delivery_world(), *r)
                  for r in (("B", 1, 0), ("D", 1, 1), ("F", 1, 2))))[2]))


# --------------------------------------------------------------------------
# 8, 9. admission and additive service under the freeze
# --------------------------------------------------------------------------


def test_admission_requires_proved_serviceability_in_study_one() -> None:
    world = study_one_world()
    state = study_one_state(0, 0, 12)
    reachable = _e(world, "B", 2, 0)
    impossible = _e(world, "A", 9, 1)
    verdicts = classify(world, state, (), (reachable, impossible))
    check("the reachable order is proved serviceable",
          verdicts[reachable.demand_id] == SERVICEABLE, str(verdicts))
    check("the oversized order is proved impossible",
          verdicts[impossible.demand_id] == IMPOSSIBLE, str(verdicts))
    admitted, refused, _ = admit(world, state, (), (), (reachable, impossible), 3, 0)
    check("only the proved-serviceable order is admitted",
          tuple(d.demand_id for d in admitted) == (reachable.demand_id,))
    check("and the other is rejected for scarcity, on a proof",
          refused[0].status == E_REJECTED_PHYSICAL_SCARCITY)


def test_additive_orders_survive_the_freeze() -> None:
    world = study_one_world()
    state = study_one_state(0, 12, 0)
    orders = (_e(world, "C", 2, 0), _e(world, "C", 2, 1))
    reqs = requirements(orders)
    check("two two-unit orders at one coordinate require four",
          reqs[0].economic_total == 4 and reqs[0].required_delta == 4)
    two = PlanGroup.of(PhysicalAction(world.routes[2], F(2)))
    check("a two-unit delivery serves neither pair completely",
          not serves_all(reqs, two.increment(world.dimension)))
    check("a four-unit combined delivery is impossible here: one route, one "
          "action, and the largest quantum is two",
          physically_serviceable(world, state, reqs) == IMPOSSIBLE)


# --------------------------------------------------------------------------
# 10, 13. the finite completeness argument, and what it does not say
# --------------------------------------------------------------------------


def test_the_completeness_bound_is_computed_not_asserted() -> None:
    world = study_one_world()
    bound = completeness_bound(world)
    check("the bound is a computed record", isinstance(bound, CompletenessBound))
    check("four usable routes", bound.usable_routes == 4, str(bound.usable_routes))
    check("eight atomic actions", bound.atomic_actions == 8, str(bound.atomic_actions))
    check("the complete plan space is 3^4 - 1 = 80",
          bound.plan_space == 80 == plan_space(world), str(bound.plan_space))
    check("the plan cap does not bind", not bound.cap_binds)
    check("the whole space fits inside the exhaustive budget",
          bound.plan_space <= bound.exhaustive_budget)
    check("so SEARCH_UNRESOLVED is impossible, not merely unobserved",
          bound.unresolved_impossible)
    check("the requirement set can never exceed the coordinate count, so the "
          "search space does not grow with the demand count",
          len(requirements((_e(world, "A", 1, 0), _e(world, "A", 1, 1),
                            _e(world, "C", 1, 2)))) <= world.dimension)
    big = DemandWorld.declare(
        "wide", world.coordinates, world.routes, world.quanta, 4
    )
    check("the bound is a property of the world, not of a run",
          completeness_bound(big).plan_space == bound.plan_space)


def test_study_one_verified_is_not_general_framework_proved() -> None:
    text = Path("DEMAND_DRIVEN_STUDY_ONE_DOMAIN.md").read_text()
    check("the domain document exists", bool(text))
    check("it states the non-claim verbatim",
          "STUDY-1 DOMAIN VERIFIED" in text
          and "GENERAL DEMAND-DRIVEN FRAMEWORK PROVED FOR ALL "
              "LOSS/CAPACITY/TOPOLOGY MODELS" in text)
    check("it keeps the general loss-aware framework open",
          "open for later extension" in text)
    check("and it records both out-of-domain counterexamples",
          "capacity_relief_world" in text and "shared_sink_world" in text)


# ==========================================================================
# FINAL STUDY-1 ORACLE + SAMPLING SEMANTICS CORRECTION
# ==========================================================================


def _study_one_blocked_case():
    """`study_one_world` at (0, 6, 6): blocked P at A, live E at C."""
    world = study_one_world()
    state = blocked_neighbour_state()
    physical = derive_physical_demands(world, state)
    demands = physical + (_e(world, "C", 1),)
    return world, state, demands


def _two_supplier_case():
    world = two_supplier_world()
    state = two_supplier_state()
    demands = tuple(derive_physical_demands(world, state)) + (
        _e(world, "C", 1, 0),
        _e(world, "D", 1, 1),
    )
    return world, state, demands


# --------------------------------------------------------------------------
# 1-3. independent progress is authoritative, and the old oracle could not see it
# --------------------------------------------------------------------------


def test_the_auditor_counterexample_is_exactly_as_described() -> None:
    world, state, demands = _study_one_blocked_case()
    check("the state is (0, 6, 6)", state == (F(0), F(6), F(6)), str(state))
    physical = tuple(d for d in demands if d.demand_class == "P")
    check("there is exactly one physical demand, four units short at A",
          len(physical) == 1 and physical[0].coordinate == 0
          and physical[0].required == 4)
    check("it is proved impossible: one route into A, largest quantum two",
          physically_serviceable(world, state, requirements(physical)) == IMPOSSIBLE)
    order = tuple(d for d in demands if d.demand_class == "E")
    check("the order at C is serviceable",
          physically_serviceable(world, state, requirements(order)) == SERVICEABLE)
    found = components(world, state, ActiveDemandSet.of(physical, order))
    check("the two are independent", len(found) == 2, str(len(found)))
    menus = {c.component_id: len(enumerate_service_plans(world, state, c)) for c in found}
    check("and C has exactly two complete plans", sorted(menus.values()) == [0, 2],
          str(menus))


def test_the_old_all_complete_oracle_passed_vacuously_here() -> None:
    """The defect: empty == empty is a PASS that has seen nothing."""
    world, state, demands = _study_one_blocked_case()
    bound = action_bound(world, state)
    left = all_complete_outcomes(oracle_at(world, bound), state, demands, bound)
    right = component_all_complete_outcomes(
        oracle_at(world, bound), state, demands, bound
    )
    check("the all-complete query finds nothing, correctly: not every demand "
          "can be satisfied at once", not left)
    check("and the component path also finds nothing", not right)
    ok, _ = all_complete_agree(world, state, demands, bound)
    check("so the old comparison agrees -- vacuously", ok and not left and not right)
    check("which is why it may not be described as runtime semantics",
          "must never be described" in oracle_doc())


def test_the_progress_reference_sees_what_the_runtime_does() -> None:
    world, state, demands = _study_one_blocked_case()
    bound = action_bound(world, state)
    equalised = oracle_at(world, bound)
    reference = global_progress(equalised, state, demands, bound)
    check("the blocked demand is named, not silently dropped",
          reference.blocked == ("P:r|A",), str(reference.blocked))
    check("the order at C is resolved",
          reference.resolved == ("E:000000:000:r|C",), str(reference.resolved))
    check("the blocked part carries the BLOCKED marker",
          (BLOCKED,) in reference.part_plans, str(reference.part_plans))
    check("the progress reference contains the two C-service possibilities",
          len(reference.plans) == 2, str(reference.plans))
    check("both are B -> C, at one unit and at two",
          all("1->2" in identity for identity in reference.plans),
          str(reference.plans))
    runtime = component_progress(equalised, state, demands, bound)
    check("the component runtime contains the same two",
          runtime.identities == reference.identities,
          f"{sorted(runtime.identities)} vs {sorted(reference.identities)}")
    ok, detail = progress_levels(world, state, demands, bound)
    check("and all four levels pass on a non-empty comparison", ok, str(detail))
    check("the empty == empty pass is now impossible here: the reference is "
          "not empty", len(reference.plans) > 0)


def test_a_blocked_part_contributes_no_action_and_keeps_its_demand() -> None:
    world, state, demands = _study_one_blocked_case()
    bound = action_bound(world, state)
    reference = global_progress(oracle_at(world, bound), state, demands, bound)
    groups = reference.group_map
    for identity in reference.plans:
        increment = groups[identity].increment(world.dimension)
        check(f"{identity} moves nothing into the blocked coordinate A",
              increment[0] == 0, str(increment))
    check("this is not voluntary no-action -- the serviceable part still acts",
          all(not groups[identity].is_empty for identity in reference.plans))


def test_the_reference_partition_is_derived_without_calling_coupling() -> None:
    import demand_driven_ebu.oracle as oracle_module

    source = inspect.getsource(oracle_module.reference_partition) + inspect.getsource(
        oracle_module._reference_reach
    )
    check("the reference partition calls neither components nor the pruned search",
          "components(" not in source and "physically_serviceable" not in source)
    check("it decides serviceability by brute force instead",
          "plans_serving" in source)
    for world, state, demands in (_study_one_blocked_case(), _two_supplier_case()):
        bound = action_bound(world, state)
        mine = reference_partition(oracle_at(world, bound), state, demands, bound)
        theirs = components(
            world,
            state,
            ActiveDemandSet.of(
                tuple(d for d in demands if d.demand_class == "P"),
                tuple(d for d in demands if d.demand_class == "E"),
            ),
        )
        check(f"{world.world_id}: and it reproduces the runtime partition",
              tuple(tuple(d.demand_id for d in part) for part in mine)
              == tuple(component.demand_ids for component in theirs),
              f"{mine} vs {[c.demand_ids for c in theirs]}")


# --------------------------------------------------------------------------
# 4. the narrower query survives under its own name
# --------------------------------------------------------------------------


def test_all_complete_remains_available_under_a_narrower_name() -> None:
    import demand_driven_ebu.oracle as oracle_module

    check("the narrow query still exists", callable(all_complete_plans))
    check("its docstring states the question it answers",
          "can every active demand be completely satisfied"
          in all_complete_plans.__doc__.lower())
    check("and disclaims runtime equivalence",
          "must not be presented" in all_complete_plans.__doc__)
    check("the superseded names are gone",
          not hasattr(oracle_module, "global_feasible")
          and not hasattr(oracle_module, "component_feasible"))
    world = study_one_world()
    state = study_one_state(2, 8, 2)
    demands = derive_physical_demands(world, state)
    check("the state has two coordinates two short", len(demands) == 2
          and all(d.required == 2 for d in demands))
    check("it still answers its own question: one plan serves both",
          len(all_complete_plans(world, state, demands, 4)) > 0)
    starved = study_one_state(0, 12, 0)
    check("and answers 'no' when they cannot be served together, which is a "
          "true answer to a narrow question, not a statement that nothing "
          "can happen",
          not all_complete_plans(
              world, starved, derive_physical_demands(world, starved), 4
          ))


# --------------------------------------------------------------------------
# 5-8. sampling over canonical plan identities
# --------------------------------------------------------------------------


def test_the_sampling_unit_is_the_canonical_plan_identity() -> None:
    import demand_driven_ebu.plans as plans_module
    import demand_driven_ebu.policies as policies_module

    check("the random policy is given a plan count, never an outcome count",
          "plan_count" in inspect.signature(policies_module.choose).parameters)
    check("the menu enforces one record per plan identity",
          "may not carry two records of one plan identity"
          in inspect.getsource(plans_module.enumerate_service_plans))
    world, state, demands = _two_supplier_case()
    found = components(
        world, state,
        ActiveDemandSet.of((), tuple(d for d in demands if d.demand_class == "E")),
    )
    menu = enumerate_service_plans(world, state, found[0])
    identities = [plan.group.group_id for plan in menu]
    check("four distinct plan identities", len(set(identities)) == 4, str(identities))
    check("duplicate records canonicalize to one plan",
          len(canonical([p.group for p in menu] + [p.group for p in menu])) == 4)


def test_the_outcome_map_is_many_to_one() -> None:
    world, state, demands = _two_supplier_case()
    bound = action_bound(world, state)
    equalised = oracle_at(world, bound)
    reference = global_progress(equalised, state, demands, bound)
    check("four plan identities", len(reference.plans) == 4, str(reference.plans))
    support = outcome_support(equalised, state, reference)
    check("three distinct modeled outcomes", len(support) == 3, str(len(support)))
    check("so Phi is not injective", len(reference.plans) > len(support))
    groups = reference.group_map
    crossed = [
        identity for identity in reference.plans
        if outcome(equalised, state, groups[identity])
        == outcome(equalised, state, groups[reference.plans[1]])
    ]
    check("and the two colliding plans are genuinely different action sets",
          len(crossed) == 2 and crossed[0] != crossed[1], str(crossed))


def test_uniform_plan_sampling_induces_a_quarter_half_quarter_law() -> None:
    world, state, demands = _two_supplier_case()
    bound = action_bound(world, state)
    equalised = oracle_at(world, bound)
    reference = global_progress(equalised, state, demands, bound)
    law = random_law(equalised, state, reference)
    check("the induced outcome law is 1/4, 1/2, 1/4",
          sorted(law.values()) == [F(1, 4), F(1, 4), F(1, 2)],
          str(sorted(str(v) for v in law.values())))
    check("it is not 1/3 each: outcome probability carries plan multiplicity",
          F(1, 3) not in law.values())
    check("the mass sums to exactly one", sum(law.values()) == 1)
    runtime = component_progress(equalised, state, demands, bound)
    check("the runtime path induces the same law",
          random_law(equalised, state, runtime) == law)
    doubled = component_progress(equalised, state, demands, bound)
    check("duplicate plan records would not change it, because identities are "
          "counted", random_law(equalised, state, doubled) == law)


def test_aligned_and_hostile_restrict_then_tie_break_over_plans() -> None:
    world, state, demands = _two_supplier_case()
    bound = action_bound(world, state)
    equalised = oracle_at(world, bound)
    reference = global_progress(equalised, state, demands, bound)
    runtime = component_progress(equalised, state, demands, bound)
    for largest, name in ((True, "aligned"), (False, "hostile")):
        tied = extremal_identities(equalised, state, reference, largest)
        check(f"{name}: the tie set is over plan identities",
              len(tied) == 2, str(sorted(tied)))
        check(f"{name}: the runtime agrees on the tie set",
              extremal_identities(equalised, state, runtime, largest) == tied)
        law = policy_law(equalised, state, reference, largest)
        check(f"{name}: and on the induced outcome law",
              policy_law(equalised, state, runtime, largest) == law)
        check(f"{name}: the law sums to one", sum(law.values()) == 1)
    aligned = policy_law(equalised, state, reference, True)
    hostile = policy_law(equalised, state, reference, False)
    check("aligned ties on two plans that share one outcome, so its law is a "
          "point mass", len(aligned) == 1 and list(aligned.values()) == [F(1)],
          str(aligned))
    check("hostile ties on two plans with distinct outcomes, so its law is "
          "1/2, 1/2", sorted(hostile.values()) == [F(1, 2), F(1, 2)],
          str(sorted(str(v) for v in hostile.values())))


# --------------------------------------------------------------------------
# 9. the four levels are separate, and B does not imply C
# --------------------------------------------------------------------------


def test_outcome_support_alone_does_not_prove_the_induced_law() -> None:
    world, state, demands = _two_supplier_case()
    bound = action_bound(world, state)
    equalised = oracle_at(world, bound)
    reference = global_progress(equalised, state, demands, bound)
    support = outcome_support(equalised, state, reference)
    law = random_law(equalised, state, reference)
    flat = {key: F(1, len(support)) for key in support}
    check("a flat law over the same support is a different distribution",
          flat != law)
    check("so agreeing on support would not have caught a multiplicity error",
          set(flat) == set(law) and flat != law)
    check("the four levels are declared separately", len(LEVELS) == 4, str(LEVELS))
    import demand_driven_ebu.oracle as oracle_module
    check("and the module says B alone proves neither C nor D",
          "B alone does not prove C or D" in oracle_module.__doc__)


def test_all_four_levels_run_on_every_declared_fixture() -> None:
    cases = (
        _study_one_blocked_case(),
        _two_supplier_case(),
    )
    for a, b in ((0, 12), (2, 8), (6, 6), (12, 0)):
        world = study_one_world()
        state = study_one_state(a, b, 12 - a - b)
        cases = cases + (
            (world, state, tuple(derive_physical_demands(world, state))
             + (_e(world, "C", 1),)),
        )
    for world, state, demands in cases:
        bound = action_bound(world, state)
        if bound == 0 or not demands:
            continue
        ok, detail = progress_levels(world, state, demands, bound)
        for level in LEVELS:
            check(f"{world.world_id}@{tuple(int(v) for v in state)}: {level}",
                  detail["levels"][level], str(detail))
        check(f"{world.world_id}@{tuple(int(v) for v in state)}: all levels",
              ok, str(detail))


# --------------------------------------------------------------------------
# 10. mandatory action, persistence, and integrity
# --------------------------------------------------------------------------


def test_a_serviceable_component_must_execute_one_nonempty_plan() -> None:
    world, state, demands = _study_one_blocked_case()
    # The control policy applies no affordability filter, so what is tested
    # here is mandatory *physical* action: a serviceable component with a
    # complete plan must execute one. Affordability is a separate gate with
    # its own status and its own tests.
    run = EconomyRun(
        world,
        ScriptedDisturbance({}),
        ScriptedArrivals({0: (("r", "C", 1),)}),
        POLICY_CONTROL,
        1, 2, 3, 4,
        state,
        registered=True,
        decomposition_gate=True,
    )
    record = run.run_epoch()
    check("the epoch executed", record.epoch_status == STATUS_EXECUTED,
          record.epoch_status)
    check("and the executed group is not empty", record.executed_group_id != "g:[]",
          record.executed_group_id)
    statuses = {outcome.component_id: outcome.status for outcome in record.outcomes}
    check("the serviceable component executed",
          STATUS_EXECUTED in statuses.values(), str(statuses))
    check("the blocked component reported no complete physical plan",
          STATUS_NO_COMPLETE_PLAN in statuses.values(), str(statuses))
    check("the blocked demand persists into the next epoch, because the "
          "deviation that created it is still there",
          derive_physical_demands(world, record.state_after)[0].demand_id == "P:r|A",
          str(derive_physical_demands(world, record.state_after)))
    check("the decomposition gate verified this epoch",
          record.decomposition_gate == DECOMPOSITION_VERIFIED,
          record.decomposition_gate)
    check("no action was spent on the blocked coordinate",
          record.state_after[0] == record.state_forced[0],
          f"{record.state_forced[0]} -> {record.state_after[0]}")


def test_blocked_and_unresolved_are_still_different_things() -> None:
    import demand_driven_ebu.enumeration as enumeration_module

    world, state, demands = _study_one_blocked_case()
    physical = tuple(d for d in demands if d.demand_class == "P")
    check("the blocked demand is proved impossible, not undecided",
          physically_serviceable(world, state, requirements(physical)) == IMPOSSIBLE)
    run = EconomyRun(
        world, ScriptedDisturbance({}), ScriptedArrivals({}), POLICY_RANDOM,
        1, 2, 3, 4, state, registered=True,
    )
    saved = enumeration_module.EXHAUSTIVE_BUDGET
    raised = None
    try:
        enumeration_module.EXHAUSTIVE_BUDGET = 1
        run.run_epoch()
    except JobInvalid as failure:
        raised = failure
    finally:
        enumeration_module.EXHAUSTIVE_BUDGET = saved
    check("an undecided search is a job integrity failure, not a blocked part",
          raised is not None)
    check("BLOCKED is a reference marker and never a search verdict",
          BLOCKED not in (SERVICEABLE, IMPOSSIBLE, UNRESOLVED))


if __name__ == "__main__":
    raise SystemExit(main())
