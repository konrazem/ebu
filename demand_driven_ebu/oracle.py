"""Decomposition-free references for what the runtime actually does.

Three distinct questions live here, and conflating any two of them produced a
defect an independent audit had to find. They are kept apart by name.

## 1. All-demands-complete solvability -- `all_complete_*`

*Can every active demand be completely satisfied in one epoch?* A useful
mathematical query, and the original oracle. It is **not** the runtime's
execution semantics and must never be described as though it were.

The failure that forced this distinction: the runtime lets an independent
component progress while another component is proved impossible, but this
query answers "no" and returns the empty set whenever any demand is
unservable. The component path also returned empty in that case, so the two
agreed -- vacuously. At `study_one_world` and state `(0, 6, 6)` a
four-unit physical demand at `A` is proved impossible while an independent
one-unit order at `C` has two complete plans; the old comparison reported
`0 == 0` and passed. It saw nothing.

## 2. Independent-progress semantics -- `global_progress`

What the runtime is actually allowed to do in one epoch, and therefore the
authoritative scientific reference. Partition the active demands; a part whose
complete-plan set is empty is **BLOCKED** and contributes no physical action,
leaving its demands unresolved; **every other part must contribute exactly one
complete plan**. There is no voluntary no-action: a serviceable part acts.

    G_progress = product over parts of ( P_k  if P_k nonempty
                                       ; {BLOCKED_k}  if impossibility proved )

`SEARCH_UNRESOLVED` is neither branch. It is a computational integrity failure
and the job cannot proceed (`study_one`).

`global_progress` computes this without calling `coupling` or `plans`. It
re-derives the partition from the frozen Study-1 reach definition and
enumerates every part by brute force, then also enumerates the non-blocked
demand set **with no partition at all** and uses that as the reference plan
set. The partitioned product is compared against it as an internal check.
What it re-derives is the frozen *definition*; it does not independently
justify the choice of definition, and it is exact only inside the Study-1
domain, where liveness is necessary and sufficient and the capacity-relief
limb is empty.

## 3. Plans, outcomes, and the map between them

A **plan identity** is a canonical physical action set. Two syntactically
different encodings of the same action set are one plan. Two genuinely
different action sets are two plans **even when they produce the same
post-state, the same aggregate increment and the same owner receipts**.

A **modeled outcome** is what `Phi` returns: the exact physical increment
together with the settled owner receipts.

    Phi : plan -> outcome

**`Phi` is many-to-one.** An earlier version of this module claimed a
bijection from plan tuples to outcomes and drew a sampling conclusion from it.
That was wrong. In `two_supplier_world` there are four irredundant plan
identities and three outcomes: the two cross plans `{A->C, B->D}` and
`{B->C, A->D}` are indistinguishable in increment, post-state and receipts.

So for uniform random plan selection,

    P(outcome = o) = |{ plans G : Phi(G) = o }| / |all eligible plans|

and outcome probability carries plan multiplicity: `1/4, 1/2, 1/4` in that
world, never `1/3` each. The Cartesian-product statement holds over **plan
identities** -- uniform over a product of plan sets is exactly independent
uniform draws per part -- and the outcome distribution is its pushforward.

For `ALIGNED` and `HOSTILE`: restrict to the plans attaining the extremal
group EBU, apply the frozen uniform tie-break over those *plan identities*,
and derive outcome probabilities from that plan distribution.

## 4. Physical eligibility is not execution

Everything above is **pre-affordability**. `G_physical` reads no balance and
no policy, and it is **not the runtime action distribution** for an EBU arm:
an EBU arm samples from the affordable subset, so comparing only `G_physical`
checks a law the model does not have. That was a verification defect, and the
policy-conditioned layer at the bottom of this module is what closes it.

    G_affordable = { G in G_physical :
                     projected balance of every required owner stays >= 0 }

Affordability is per account, never a pooled total. `ebu_random` is uniform
over `G_affordable`; `ebu_aligned` and `ebu_hostile` take their extremum
**within** it and then tie-break uniformly over the tied plan identities;
`control_random_no_ebu` intentionally bypasses it and samples over
`G_physical`.

Restricting before taking the extremum is the substantive part: a hostile
actor's globally worst plan is frequently the one it cannot pay for.

A part with physical plans but no affordable one is `UNAFFORDABLE`. No action
occurs for it and its demand stays pending -- an intended EBU outcome, kept
distinct from `BLOCKED`, from admission scarcity and from search failure.

## Verification levels

Kept separate because none of them implies the next.

    A  plan-set equivalence      same distinct plan identities
    B  outcome support           same Phi images
    C  pre-affordability random  same outcome probabilities over G_physical
    D  pre-affordability extrema same extremal sets over G_physical

**B alone does not prove C or D.** Two plan sets can have identical outcome
supports and different multiplicities, which is exactly what the
`two_supplier_world` fixture exhibits.

**And none of these four is a runtime verification.** All of them read
`G_physical`, which is computed before any balance is consulted. An EBU arm
never samples from `G_physical`; it samples from the affordable subset. The
policy-conditioned levels at the bottom of this module are what close that
gap, and `policy_levels` is what the harness gate runs.

Exponential in the number of live routes. A conformance instrument, used by
`EconomyRun(decomposition_gate=True)` and by the suite, never by the
mechanism's own decision path.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations, product

from gaussian_harness.numerics import Refusal, Vector

from .coupling import components
from .demand import ActiveDemandSet
from .enumeration import is_irredundant, live_routes
from .physical import PlanGroup, action_alphabet, can_happen_now
from .plans import enumerate_service_plans
from .service import CoordinateRequirement, requirements, serves_all
from .valuation import value_group
from .world import DemandWorld

ORACLE_BUDGET = 2_000_000

BLOCKED = "BLOCKED"

LEVEL_A = "A_PLAN_SET_EQUIVALENCE"
LEVEL_B = "B_OUTCOME_SUPPORT"
LEVEL_C = "C_PREAFFORDABILITY_RANDOM_LAW"
LEVEL_D = "D_PREAFFORDABILITY_EXTREMAL_SETS"
LEVELS = (LEVEL_A, LEVEL_B, LEVEL_C, LEVEL_D)


# ---------------------------------------------------------------- identity


def plan_identity(group: PlanGroup) -> str:
    """The canonical name of a physical action set.

    `PlanGroup` sorts its actions and refuses a repeated route, so the group
    id is already canonical: any two encodings of the same action set produce
    the same string, and two different action sets never collide.
    """
    return group.group_id


def canonical(groups) -> tuple[PlanGroup, ...]:
    """Deduplicate by plan identity and order canonically.

    Duplicate *records* of one plan must not change any count, and therefore
    must not change any sampling probability. Everything downstream counts
    identities, so this is where a duplicate would be removed if one ever
    arrived.
    """
    unique: dict[str, PlanGroup] = {}
    for group in groups:
        unique.setdefault(plan_identity(group), group)
    return tuple(unique[key] for key in sorted(unique))


def outcome(world: DemandWorld, state: Vector, group: PlanGroup):
    """`Phi`: the modeled outcome of a plan. Deliberately not injective."""
    valuation = value_group(world, state, group)
    return (
        tuple(group.increment(world.dimension)),
        tuple(sorted(valuation.owner_deltas)),
    )


def group_ebu(world: DemandWorld, state: Vector, group: PlanGroup) -> Fraction:
    if group.is_empty:
        return Fraction(0)
    return value_group(world, state, group).group_ebu


# ------------------------------------------------- brute force, no components


def _bounded_groups(world: DemandWorld, routes, bound: int):
    alphabet = action_alphabet(world, routes)
    for size in range(1, bound + 1):
        for chosen in combinations(alphabet, size):
            if len({action.route.route_id for action in chosen}) != size:
                continue
            yield PlanGroup.of(*chosen)


def _check_budget(world: DemandWorld, routes, bound: int) -> None:
    space = sum(
        len(list(combinations(range(len(action_alphabet(world, routes))), size)))
        for size in range(1, bound + 1)
    )
    if space > ORACLE_BUDGET:
        raise Refusal(f"oracle search space {space} exceeds the declared budget")


def plans_serving(
    world: DemandWorld,
    state: Vector,
    reqs: tuple[CoordinateRequirement, ...],
    bound: int,
) -> tuple[PlanGroup, ...]:
    """Every complete, executable, irredundant plan for this requirement set.

    Brute force over the whole world. No component is formed, no structural
    reach is consulted, and the plan-size cap is not read.
    """
    if not reqs:
        return ()
    routes = live_routes(world, state)
    _check_budget(world, routes, bound)
    found = [
        group
        for group in _bounded_groups(world, routes, bound)
        if serves_all(reqs, group.increment(world.dimension))
        and can_happen_now(world, state, group).executable
        and is_irredundant(world, state, reqs, group)
    ]
    return canonical(found)


# ---------------------------------------------------- F_all_complete (query 1)


def all_complete_plans(world: DemandWorld, state: Vector, demands, bound: int):
    """Plans completely serving **every** active demand in one epoch.

    Answers *can every active demand be completely satisfied at once?* This is
    a narrower question than what the runtime does and must not be presented
    as equivalent to it. Empty here means "not all of them", never "nothing
    can happen".
    """
    return plans_serving(world, state, requirements(demands), bound)


def all_complete_outcomes(world: DemandWorld, state: Vector, demands, bound: int):
    return frozenset(
        outcome(world, state, group)
        for group in all_complete_plans(world, state, demands, bound)
    )


def component_all_complete_outcomes(
    world: DemandWorld, state: Vector, demands, bound: int
):
    """The same query answered through the component path."""
    active = ActiveDemandSet.of(
        tuple(d for d in demands if d.demand_class == "P"),
        tuple(d for d in demands if d.demand_class == "E"),
    )
    menus = []
    for component in components(world, state, active):
        plans = enumerate_service_plans(world, state, component)
        if not plans:
            return frozenset()
        menus.append([plan.group for plan in plans])
    outcomes = set()
    for combination in product(*menus):
        actions = tuple(action for group in combination for action in group.actions)
        if len(actions) > bound:
            continue
        if len({action.route.route_id for action in actions}) != len(actions):
            continue
        outcomes.add(outcome(world, state, PlanGroup.of(*actions)))
    return frozenset(outcomes)


def at_bound(world: DemandWorld, bound: int) -> DemandWorld:
    """The same world with its per-plan cap set to the comparison bound."""
    return DemandWorld.declare(
        world.world_id, world.coordinates, world.routes, world.quanta, bound
    )


def all_complete_agree(world: DemandWorld, state: Vector, demands, bound: int):
    """Compare the narrow query on both paths. Not a runtime-semantics check."""
    equalised = at_bound(world, bound)
    left = all_complete_outcomes(equalised, state, demands, bound)
    right = component_all_complete_outcomes(equalised, state, demands, bound)
    return left == right, {
        "all_complete_global": len(left),
        "all_complete_components": len(right),
        "only_global": sorted(str(x) for x in (left - right))[:4],
        "only_components": sorted(str(x) for x in (right - left))[:4],
    }


# ------------------------------------------- the independent reference partition


def _reference_reach(world: DemandWorld, state: Vector, demand, bound: int):
    """The frozen Study-1 reach of one demand, re-derived from its definition.

    In the Study-1 domain there are no declared storage capacities and no
    sinks, so the closure of `enumeration.structural_reach` is one pass and
    reduces to exactly this: the demand's coordinate, together with the
    sources of the live routes delivering into it. A demand **proved**
    impossible binds nothing but its own destination.

    Serviceability is decided here by brute force, not by the pruned search,
    so this does not inherit the pruning it is meant to help check.
    """
    reqs = requirements((demand,))
    if not plans_serving(world, state, reqs, bound):
        return frozenset(), frozenset(), frozenset(), demand.coordinate, True
    delivering = tuple(
        route
        for route in live_routes(world, state)
        if route.destination == demand.coordinate
    )
    coordinates = {demand.coordinate} | {route.source for route in delivering}
    return (
        frozenset(coordinates),
        frozenset(route.route_id for route in delivering),
        frozenset(world.owner_of(route.source) for route in delivering),
        demand.coordinate,
        False,
    )


def reference_partition(world: DemandWorld, state: Vector, demands, bound: int):
    """Partition the active demands, without calling `coupling`."""
    ordered = tuple(sorted(demands, key=lambda d: d.demand_id))
    if not ordered:
        return ()
    reaches = [_reference_reach(world, state, demand, bound) for demand in ordered]
    parent = list(range(len(ordered)))

    def find(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    for i in range(len(ordered)):
        for j in range(i + 1, len(ordered)):
            left, right = reaches[i], reaches[j]
            touching = (
                left[3] == right[3]
                or (left[0] & right[0])
                or (left[1] & right[1])
                or (left[2] & right[2])
            )
            if touching:
                a, b = find(i), find(j)
                if a != b:
                    parent[max(a, b)] = min(a, b)

    grouped: dict[int, list] = {}
    for index in range(len(ordered)):
        grouped.setdefault(find(index), []).append(ordered[index])
    return tuple(
        tuple(sorted(members, key=lambda d: d.demand_id))
        for members in sorted(
            grouped.values(), key=lambda ms: tuple(d.demand_id for d in ms)
        )
    )


# ---------------------------------------------------- progress reference (query 2)


@dataclass(frozen=True)
class ProgressReference:
    """What one epoch is allowed to do, under independent-progress semantics."""

    parts: tuple[tuple[str, ...], ...]
    part_plans: tuple[tuple[str, ...], ...]
    blocked: tuple[str, ...]
    resolved: tuple[str, ...]
    plans: tuple[str, ...]
    groups: tuple[tuple[str, PlanGroup], ...]

    @property
    def group_map(self) -> dict[str, PlanGroup]:
        return dict(self.groups)

    @property
    def identities(self) -> frozenset[str]:
        return frozenset(self.plans)

    @property
    def blocked_parts(self) -> tuple[tuple[str, ...], ...]:
        return tuple(
            part
            for part, plans in zip(self.parts, self.part_plans)
            if plans == (BLOCKED,)
        )


def _combine(menus) -> tuple[PlanGroup, ...]:
    """One plan per non-blocked part; blocked parts contribute no action."""
    combined = []
    for choice in product(*menus) if menus else [()]:
        actions = tuple(action for group in choice for action in group.actions)
        combined.append(PlanGroup.of(*actions))
    return canonical(combined)


def global_progress(
    world: DemandWorld, state: Vector, demands, bound: int
) -> ProgressReference:
    """The authoritative progress-plan family, decomposition-free."""
    parts = reference_partition(world, state, demands, bound)
    part_plans: list[tuple[str, ...]] = []
    live_menus = []
    blocked: list[str] = []
    resolved: list[str] = []
    for part in parts:
        found = plans_serving(world, state, requirements(part), bound)
        if not found:
            part_plans.append((BLOCKED,))
            blocked.extend(demand.demand_id for demand in part)
            continue
        part_plans.append(tuple(plan_identity(group) for group in found))
        live_menus.append(list(found))
        resolved.extend(demand.demand_id for demand in part)

    # The reference plan set is enumerated over the whole world with no
    # partition at all: it is what the partitioned product has to reproduce,
    # not something derived from it.
    active = tuple(
        demand for demand in demands if demand.demand_id in set(resolved)
    )
    direct = (
        plans_serving(world, state, requirements(active), bound)
        if active
        else (PlanGroup.of(),)
    )
    # Both sides must carry the same action bound. A decomposed epoch may hold
    # more total actions than any single plan enumerated at `bound` -- that
    # asymmetry is declared and is tested on its own -- so comparing an
    # unbounded product against a bounded direct enumeration would report it
    # as a decomposition defect. Inside the Study-1 domain `bound` is the live
    # route count and nothing is removed here at all.
    combined = _combine(live_menus) if live_menus else (PlanGroup.of(),)
    combined = tuple(group for group in combined if len(group.actions) <= bound)
    if frozenset(plan_identity(g) for g in direct) != frozenset(
        plan_identity(g) for g in combined
    ):
        raise Refusal(
            "the partitioned product does not reproduce the decomposition-free "
            f"plan set: {sorted(plan_identity(g) for g in direct)[:3]} vs "
            f"{sorted(plan_identity(g) for g in combined)[:3]}"
        )
    return ProgressReference(
        tuple(tuple(d.demand_id for d in part) for part in parts),
        tuple(part_plans),
        tuple(sorted(blocked)),
        tuple(sorted(resolved)),
        tuple(plan_identity(group) for group in direct),
        tuple((plan_identity(group), group) for group in direct),
    )


def component_progress(
    world: DemandWorld, state: Vector, demands, bound: int
) -> ProgressReference:
    """The same family, built the way the runtime builds it."""
    active = ActiveDemandSet.of(
        tuple(d for d in demands if d.demand_class == "P"),
        tuple(d for d in demands if d.demand_class == "E"),
    )
    found = components(world, state, active)
    parts: list[tuple[str, ...]] = []
    part_plans: list[tuple[str, ...]] = []
    live_menus = []
    blocked: list[str] = []
    resolved: list[str] = []
    for component in found:
        parts.append(component.demand_ids)
        menu = enumerate_service_plans(world, state, component)
        groups = canonical(plan.group for plan in menu)
        if not groups:
            part_plans.append((BLOCKED,))
            blocked.extend(component.demand_ids)
            continue
        part_plans.append(tuple(plan_identity(group) for group in groups))
        live_menus.append(list(groups))
        resolved.extend(component.demand_ids)
    combined = _combine(live_menus) if live_menus else (PlanGroup.of(),)
    combined = tuple(group for group in combined if len(group.actions) <= bound)
    return ProgressReference(
        tuple(parts),
        tuple(part_plans),
        tuple(sorted(blocked)),
        tuple(sorted(resolved)),
        tuple(plan_identity(group) for group in combined),
        tuple((plan_identity(group), group) for group in combined),
    )


# ------------------------------------------------------------- the four levels


def outcome_support(world: DemandWorld, state: Vector, reference: ProgressReference):
    return frozenset(
        outcome(world, state, group) for _, group in reference.groups
    )


def random_law(world: DemandWorld, state: Vector, reference: ProgressReference):
    """Outcome probabilities under uniform sampling over plan identities.

    Multiplicity is the point: `Phi` is many-to-one, so an outcome reachable
    by two distinct plans carries twice the mass of one reachable by a single
    plan.
    """
    groups = [group for _, group in reference.groups]
    if not groups:
        return {}
    weight = Fraction(1, len(groups))
    law: dict = {}
    for group in groups:
        key = outcome(world, state, group)
        law[key] = law.get(key, Fraction(0)) + weight
    return law


def extremal_identities(
    world: DemandWorld, state: Vector, reference: ProgressReference, largest: bool
) -> frozenset[str]:
    """The tie set an aligned (`largest`) or hostile actor would choose from."""
    if not reference.groups:
        return frozenset()
    values = {
        identity: group_ebu(world, state, group)
        for identity, group in reference.groups
    }
    best = max(values.values()) if largest else min(values.values())
    return frozenset(identity for identity, value in values.items() if value == best)


def policy_law(
    world: DemandWorld, state: Vector, reference: ProgressReference, largest: bool
):
    """Outcome probabilities after the frozen uniform tie-break over plans."""
    tied = extremal_identities(world, state, reference, largest)
    if not tied:
        return {}
    groups = reference.group_map
    weight = Fraction(1, len(tied))
    law: dict = {}
    for identity in tied:
        key = outcome(world, state, groups[identity])
        law[key] = law.get(key, Fraction(0)) + weight
    return law


def progress_levels(world: DemandWorld, state: Vector, demands, bound: int):
    """Run all four verification levels. Returns (all passed, detail)."""
    equalised = at_bound(world, bound)
    reference = global_progress(equalised, state, demands, bound)
    runtime = component_progress(equalised, state, demands, bound)

    verdicts = {}
    verdicts[LEVEL_A] = (
        reference.identities == runtime.identities
        and reference.blocked == runtime.blocked
        and reference.resolved == runtime.resolved
    )
    verdicts[LEVEL_B] = outcome_support(equalised, state, reference) == outcome_support(
        equalised, state, runtime
    )
    verdicts[LEVEL_C] = random_law(equalised, state, reference) == random_law(
        equalised, state, runtime
    )
    verdicts[LEVEL_D] = all(
        extremal_identities(equalised, state, reference, largest)
        == extremal_identities(equalised, state, runtime, largest)
        and policy_law(equalised, state, reference, largest)
        == policy_law(equalised, state, runtime, largest)
        for largest in (True, False)
    )
    detail = {
        "blocked": reference.blocked,
        "resolved": reference.resolved,
        "reference_plans": len(reference.plans),
        "runtime_plans": len(runtime.plans),
        "reference_outcomes": len(outcome_support(equalised, state, reference)),
        "only_reference": sorted(reference.identities - runtime.identities)[:3],
        "only_runtime": sorted(runtime.identities - reference.identities)[:3],
        "levels": {level: verdicts[level] for level in LEVELS},
    }
    return all(verdicts.values()), detail


# ==========================================================================
# POLICY-CONDITIONED EXECUTION REFERENCE
# ==========================================================================
#
# Everything above is **pre-affordability**. `global_progress` answers only
# "which complete demand-serving plans can physically execute now?", and it is
# blind to capacity balances, to actor policy and to aligned/random/hostile
# preference by construction. It is **not** the runtime action distribution
# for an EBU arm, and describing it as one was a verification defect: the
# comparison then checked a distribution the model never samples from.
#
# The layer below takes the physical state, the active demands, the node
# balances and the policy identity, and reproduces what the runtime actually
# does.
#
#     G_physical    every complete executable plan, no capacity read
#     G_affordable  those whose projected owner balances all stay >= 0
#     selected      G_affordable restricted by the policy's EBU rule
#
# A part with physical plans but no affordable one is `UNAFFORDABLE`: no
# physical action occurs for it and its demand stays pending. That is an
# intended EBU outcome -- not voluntary no-action, not physical impossibility,
# not scarcity, and not computational failure. It is kept distinct from
# `BLOCKED` throughout.
#
# The comparator `control_random_no_ebu` intentionally bypasses affordability
# and samples over `G_physical`. That is the point of the arm, not an
# oversight.

from .policies import POLICY_ALIGNED, specification  # noqa: E402

PART_UNAFFORDABLE = "UNAFFORDABLE"

POLICY_LEVEL_A = "A_PHYSICAL_ELIGIBILITY"
POLICY_LEVEL_B = "B_AFFORDABLE_PLAN_SET"
POLICY_LEVEL_C = "C_POLICY_PLAN_DISTRIBUTION"
POLICY_LEVEL_D = "D_MODELED_OUTCOME_DISTRIBUTION"
POLICY_LEVELS = (POLICY_LEVEL_A, POLICY_LEVEL_B, POLICY_LEVEL_C, POLICY_LEVEL_D)


@dataclass(frozen=True)
class PolicyReference:
    """What one epoch actually does, given balances and a policy."""

    policy: str
    parts: tuple[tuple[str, ...], ...]
    part_plans: tuple[tuple[str, ...], ...]
    blocked: tuple[str, ...]
    unaffordable: tuple[str, ...]
    resolved: tuple[str, ...]
    physical: tuple[str, ...]
    eligible: tuple[str, ...]
    selected: tuple[str, ...]
    groups: tuple[tuple[str, PlanGroup], ...]

    @property
    def group_map(self) -> dict[str, PlanGroup]:
        return dict(self.groups)

    @property
    def acts(self) -> bool:
        """Whether any physical action occurs at all this epoch."""
        return any(self.group_map[identity].actions for identity in self.selected)


def affordable_subset(world, state, ledger, groups) -> tuple[PlanGroup, ...]:
    """Those plans whose projected balance stays non-negative for every owner.

    Per account, never a pooled total: a plan whose aggregate receipt is
    comfortable but which drives one owner negative is refused. That is
    Capacity V1 as carried over, and `capacity.CapacityLedger.project` is what
    decides it.
    """
    return tuple(
        group
        for group in groups
        if ledger.is_affordable(value_group(world, state, group)).affordable
    )


def _bounded(groups, bound: int) -> tuple[PlanGroup, ...]:
    return tuple(group for group in groups if len(group.actions) <= bound)


def _restrict(world, state, eligible, policy: str) -> tuple[PlanGroup, ...]:
    """Apply the policy's EBU rule to the affordable set, over plan identities.

    Aligned and hostile take the extremum **within the affordable set**, never
    over the physical set. That distinction is the whole point of this layer:
    a hostile actor's globally worst plan is frequently the one it cannot
    afford, so restricting first genuinely changes which plan it takes.
    """
    entry = specification(policy)
    if not entry.reads_ebu_to_choose or not eligible:
        return tuple(eligible)
    values = {plan_identity(group): group_ebu(world, state, group) for group in eligible}
    best = (
        max(values.values()) if policy == POLICY_ALIGNED else min(values.values())
    )
    return tuple(group for group in eligible if values[plan_identity(group)] == best)


def _assemble(world, state, ledger, policy, parts, bound) -> PolicyReference:
    entry = specification(policy)
    part_plans: list[tuple[str, ...]] = []
    blocked: list[str] = []
    unaffordable: list[str] = []
    resolved: list[str] = []
    physical_menus: list[list[PlanGroup]] = []
    eligible_menus: list[list[PlanGroup]] = []
    for members, groups in parts:
        identifiers = [demand.demand_id for demand in members]
        if not groups:
            part_plans.append((BLOCKED,))
            blocked.extend(identifiers)
            continue
        physical_menus.append(list(groups))
        keep = (
            affordable_subset(world, state, ledger, groups)
            if entry.applies_affordability
            else tuple(groups)
        )
        if not keep:
            part_plans.append((PART_UNAFFORDABLE,))
            unaffordable.extend(identifiers)
            continue
        part_plans.append(tuple(plan_identity(group) for group in keep))
        eligible_menus.append(list(keep))
        resolved.extend(identifiers)

    physical = _bounded(_combine(physical_menus) if physical_menus else (PlanGroup.of(),), bound)
    eligible = _bounded(_combine(eligible_menus) if eligible_menus else (PlanGroup.of(),), bound)
    selected = _restrict(world, state, eligible, policy)
    catalogue: dict[str, PlanGroup] = {}
    for group in tuple(physical) + tuple(eligible) + tuple(selected):
        catalogue.setdefault(plan_identity(group), group)
    return PolicyReference(
        policy,
        tuple(tuple(d.demand_id for d in members) for members, _ in parts),
        tuple(part_plans),
        tuple(sorted(blocked)),
        tuple(sorted(unaffordable)),
        tuple(sorted(resolved)),
        tuple(plan_identity(group) for group in physical),
        tuple(plan_identity(group) for group in eligible),
        tuple(plan_identity(group) for group in selected),
        tuple(sorted(catalogue.items())),
    )


def global_policy_reference(
    world: DemandWorld, state: Vector, demands, ledger, policy: str, bound: int
) -> PolicyReference:
    """The policy-conditioned reference, built without decomposition."""
    parts = [
        (part, plans_serving(world, state, requirements(part), bound))
        for part in reference_partition(world, state, demands, bound)
    ]
    return _assemble(world, state, ledger, policy, parts, bound)


def component_policy_reference(
    world: DemandWorld, state: Vector, demands, ledger, policy: str, bound: int
) -> PolicyReference:
    """The same, built the way the runtime builds it."""
    active = ActiveDemandSet.of(
        tuple(d for d in demands if d.demand_class == "P"),
        tuple(d for d in demands if d.demand_class == "E"),
    )
    parts = [
        (
            component.demands,
            canonical(plan.group for plan in enumerate_service_plans(world, state, component)),
        )
        for component in components(world, state, active)
    ]
    return _assemble(world, state, ledger, policy, parts, bound)


def plan_law(reference: PolicyReference) -> dict[str, Fraction]:
    """Uniform over the selected canonical plan identities."""
    if not reference.selected:
        return {}
    weight = Fraction(1, len(reference.selected))
    return {identity: weight for identity in reference.selected}


def induced_outcome_law(world, state, reference: PolicyReference):
    """`Phi` applied to the selected-plan law. Multiplicity is preserved."""
    groups = reference.group_map
    law: dict = {}
    for identity, mass in plan_law(reference).items():
        key = outcome(world, state, groups[identity])
        law[key] = law.get(key, Fraction(0)) + mass
    return law


def policy_levels(
    world: DemandWorld, state: Vector, demands, ledger, policy: str, bound: int
):
    """The four policy-conditioned levels. Level A alone is not verification.

    Level A compares the **pre-affordability** physical plan sets. It says
    nothing about what an EBU arm executes, because the arm never samples from
    that set. B, C and D are what close that gap.
    """
    equalised = at_bound(world, bound)
    reference = global_policy_reference(equalised, state, demands, ledger, policy, bound)
    runtime = component_policy_reference(equalised, state, demands, ledger, policy, bound)

    verdicts = {
        POLICY_LEVEL_A: (
            frozenset(reference.physical) == frozenset(runtime.physical)
            and reference.blocked == runtime.blocked
        ),
        POLICY_LEVEL_B: (
            frozenset(reference.eligible) == frozenset(runtime.eligible)
            and reference.unaffordable == runtime.unaffordable
            and reference.resolved == runtime.resolved
        ),
        POLICY_LEVEL_C: plan_law(reference) == plan_law(runtime),
        POLICY_LEVEL_D: induced_outcome_law(equalised, state, reference)
        == induced_outcome_law(equalised, state, runtime),
    }
    detail = {
        "policy": policy,
        "blocked": reference.blocked,
        "unaffordable": reference.unaffordable,
        "resolved": reference.resolved,
        "physical": len(reference.physical),
        "eligible": len(reference.eligible),
        "selected": len(reference.selected),
        "acts": reference.acts,
        "only_reference": sorted(
            frozenset(reference.eligible) - frozenset(runtime.eligible)
        )[:3],
        "only_runtime": sorted(
            frozenset(runtime.eligible) - frozenset(reference.eligible)
        )[:3],
        "levels": {level: verdicts[level] for level in POLICY_LEVELS},
    }
    return all(verdicts.values()), detail
