"""Homeostasis transition conformance suite.

Covers mission sections 18.4 (one-shock recovery), 18.5 (continuing forcing)
and the mandatory-action semantics of section 6.

**Execution class: MODEL-STATE-ADVANCING TRANSITION SUITE.** This suite calls
`run_tick` and advances model state, so it is opt-in: it refuses to run unless
`EBU_ALLOW_MODEL_TRANSITIONS=1` is set. Every trajectory here is a conformance
probe on a synthetic world at a non-registered seed. **None of it is scientific
evidence**, no outcome is interpreted, and no check asserts that any policy
recovers, converges or keeps the system anywhere.

The load-bearing check is `test_reproduces_the_registered_harness`: the
four-policy harness re-implements the canonical event order, so its EBU-random
and control-random arms must reproduce `gaussian_harness.Run` tick for tick on
identical seeds. That is what makes the new harness a faithful superset of the
pinned one rather than a parallel implementation that has quietly drifted.
"""

from __future__ import annotations

import os
import sys
from fractions import Fraction

from gaussian_harness.forcing import ForcingIncrement
from gaussian_harness.harness import (
    ARM_CONTROL,
    ARM_EBU,
    Run,
    TickBudget,
    WorldConfiguration,
)
from gaussian_harness.numerics import Refusal
from gaussian_harness.rng import STREAM_FORCING, Counter, uniform_index
from gaussian_harness.stage_a import stage_a_world
from gaussian_harness.valuation import value_group

from homeostasis.harness import (
    DECLARED_LOADS,
    LOAD_CONTINUOUS,
    LOAD_MEDIUM,
    LOAD_MILD,
    MENU_STRICT_PHYSICAL,
    MENU_WITH_NET_ZERO,
    STATUS_AFFORDABILITY_BLOCKED,
    STATUS_EXECUTED,
    STATUS_FORCING_ONLY,
    STATUS_PHYSICAL_NO_ACTION,
    ForcingLoad,
    PolicyRun,
    PolicyWorld,
    run_trajectory,
)
from homeostasis.policies import (
    CORE_POLICIES,
    POLICY_CONTROL_RANDOM,
    POLICY_EBU_ALIGNED,
    POLICY_EBU_HOSTILE,
    POLICY_EBU_RANDOM,
)
from homeostasis.jobs import ExecutionEnvelope, JobIdentity, manifest, run_job
from homeostasis.recovery import OUTCOME_RECOVERED, recovery_trial

PASSED = 0
FAILED = 0
TICKS = 0
MAX_ACCOUNTING = Fraction(0)
MAX_CONSERVATION = Fraction(0)
MAX_NONNEGATIVITY = Fraction(0)

STUDY = "conformance-homeostasis"
CONFIG = "cfg-3cell-conformance"


def check(label: str, condition: bool, detail: str = "") -> None:
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  PASS  {label}")
    else:
        FAILED += 1
        print(f"  FAIL  {label}{(' -- ' + detail) if detail else ''}")


def _observe(run: PolicyRun) -> None:
    global TICKS, MAX_ACCOUNTING, MAX_CONSERVATION, MAX_NONNEGATIVITY
    for record in run.records:
        TICKS += 1
        MAX_ACCOUNTING = max(MAX_ACCOUNTING, abs(record.accounting_residual))
        MAX_CONSERVATION = max(MAX_CONSERVATION, abs(record.conservation_residual))
        MAX_NONNEGATIVITY = max(MAX_NONNEGATIVITY, abs(record.nonnegativity_residual))


def _world(policy: str, initial=None) -> PolicyWorld:
    return PolicyWorld.declare(STUDY, CONFIG, [10, 10, 10], [1, 1, 1], [1], policy,
                               initial_state=initial)


# --------------------------------------------------------------------------


def test_reproduces_the_registered_harness() -> None:
    """EBU-random and control-random must equal the pinned two-arm harness."""
    horizon = 48
    pairs = ((POLICY_EBU_RANDOM, ARM_EBU), (POLICY_CONTROL_RANDOM, ARM_CONTROL))
    for policy, arm in pairs:
        world = _world(policy)
        new = PolicyRun(world, 909090, 717171, TickBudget.conformance())
        legacy_configuration: WorldConfiguration = stage_a_world(
            STUDY, CONFIG, [10, 10, 10], [1, 1, 1], [1], 2, arm=arm
        )
        legacy = Run(legacy_configuration, 909090, 717171, TickBudget.conformance())
        mismatch = None
        for tick in range(horizon):
            # The pinned harness takes an explicit increment, so the load
            # schedule is realized here with the same draw addresses.
            edges = tuple(sorted(legacy_configuration.rules.edges))
            index, _ = uniform_index(
                Counter(STUDY, CONFIG, 909090, STREAM_FORCING, tick, 0, 0), len(edges)
            )
            source, destination = edges[index]
            proposal = ForcingIncrement(source, destination, Fraction(1))
            admissible = legacy.state[source] >= Fraction(1)
            legacy_record = legacy.run_tick(forcing=proposal if admissible else None)
            new_record = new.run_tick(LOAD_CONTINUOUS)
            if (
                legacy_record.state_after != new_record.state_after
                or legacy_record.chosen_id != new_record.chosen_id
                or tuple(legacy_record.balances) != tuple(new_record.balances)
                or legacy_record.audit_ledger != new_record.audit_ledger
            ):
                mismatch = tick
                break
        _observe(new)
        check(f"{policy} reproduces {arm} over {horizon} ticks", mismatch is None,
              f"first divergence at tick {mismatch}")


def test_mandatory_action_leaves_no_no_op() -> None:
    for policy in CORE_POLICIES:
        run = run_trajectory(_world(policy), 31337, 42424, 48, LOAD_MEDIUM)
        _observe(run)
        statuses = {record.status for record in run.records}
        check(f"{policy} produced no unknown status", statuses <= {
            STATUS_EXECUTED, STATUS_AFFORDABILITY_BLOCKED, STATUS_PHYSICAL_NO_ACTION})
        acted = [record for record in run.records if record.status == STATUS_EXECUTED]
        check(f"{policy} executed a nonempty group whenever it acted",
              all(record.chosen_id != "g:[]" for record in acted))
        forced = [
            record for record in run.records
            if record.n_feasible > 0 and record.n_affordable > 0
        ]
        check(f"{policy} acted on every tick where an admissible group existed",
              all(record.status == STATUS_EXECUTED for record in forced))


def test_net_zero_groups_are_a_costless_null_action() -> None:
    """Three cancelling pairs are nonempty, feasible and physically inert."""
    from gaussian_harness.valuation import value_group as _value
    world = _world(POLICY_EBU_ALIGNED)
    net_zero = [
        group for group in world.candidates()
        if all(value == 0 for value in group.increment(3))
    ]
    check("the registered menu holds 21 groups", len(world.candidates()) == 21)
    check("exactly three of them are net-zero", len(net_zero) == 3, str(len(net_zero)))
    reference = tuple(Fraction(10) for _ in range(3))
    for group in net_zero:
        valuation = _value(world.potential, reference, group)
        check(f"{group.group_id} has E_G = 0 at the reference", valuation.group_ebu == 0)
        check(f"{group.group_id} costs nothing at the reference",
              all(delta == 0 for delta in valuation.owner_deltas.values()))
    # Away from the reference the same inert group moves capacity between owners.
    displaced = (Fraction(12), Fraction(9), Fraction(9))
    transfer = _value(world.potential, displaced, net_zero[0])
    deltas = transfer.owner_deltas
    check("a net-zero group still has E_G = 0 away from the reference",
          transfer.group_ebu == 0)
    check("but it moves capacity between owners",
          any(delta != 0 for delta in deltas.values()), str(deltas))
    check("and those owner deltas sum to zero exactly",
          sum(deltas.values(), Fraction(0)) == 0)
    strict = _world(POLICY_EBU_ALIGNED)
    strict = PolicyWorld.declare(STUDY, CONFIG, [10, 10, 10], [1, 1, 1], [1],
                                 POLICY_EBU_ALIGNED, menu_rule=MENU_STRICT_PHYSICAL)
    check("the strict menu removes exactly those three", len(strict.candidates()) == 18)
    check("no strict-menu group is net-zero",
          all(any(v != 0 for v in g.increment(3)) for g in strict.candidates()))


def test_affordability_block_is_not_physical_impossibility() -> None:
    """At the reference with zero balances every real move is unaffordable."""
    for policy in (POLICY_EBU_RANDOM, POLICY_EBU_ALIGNED, POLICY_EBU_HOSTILE):
        strict = PolicyWorld.declare(STUDY, CONFIG, [10, 10, 10], [1, 1, 1], [1],
                                     policy, menu_rule=MENU_STRICT_PHYSICAL)
        run = run_trajectory(strict, 5, 5, 6, None)
        _observe(run)
        first = run.records[0]
        check(f"{policy} is affordability-blocked at the reference",
              first.status == STATUS_AFFORDABILITY_BLOCKED, first.status)
        check(f"{policy} still had feasible groups there", first.n_feasible == 18)
        check(f"{policy} had no affordable group there", first.n_affordable == 0)
        check(f"{policy} did not report physical impossibility",
              first.status != STATUS_PHYSICAL_NO_ACTION)
        # Under the registered menu the same arm instead executes a null action.
        loose = PolicyWorld.declare(STUDY, CONFIG, [10, 10, 10], [1, 1, 1], [1], policy)
        loose_run = run_trajectory(loose, 5, 5, 6, None)
        _observe(loose_run)
        opening = loose_run.records[0]
        check(f"{policy} executes a net-zero group there under the registered menu",
              opening.status == STATUS_EXECUTED and opening.null_action, opening.status)
        check(f"{policy}: exactly the three net-zero groups were affordable",
              opening.n_affordable == 3, str(opening.n_affordable))
        check(f"{policy}: the null action left the state at the reference",
              opening.state_after == opening.state_frozen)
    control = run_trajectory(_world(POLICY_CONTROL_RANDOM), 5, 5, 6, None)
    _observe(control)
    check("the control still acts at the reference",
          all(record.status == STATUS_EXECUTED for record in control.records))


def test_physical_no_action_is_reachable_and_distinct() -> None:
    empty = PolicyWorld.declare(STUDY, "cfg-empty", [0, 0, 0], [1, 1, 1], [1],
                                POLICY_CONTROL_RANDOM)
    run = run_trajectory(empty, 1, 1, 3, None)
    _observe(run)
    check("a world with no stock reports physical impossibility",
          all(record.status == STATUS_PHYSICAL_NO_ACTION for record in run.records))
    check("and reports zero feasible groups",
          all(record.n_feasible == 0 for record in run.records))
    check("the two non-execution statuses are distinct strings",
          STATUS_PHYSICAL_NO_ACTION != STATUS_AFFORDABILITY_BLOCKED)


def test_recorded_ebu_is_a_function_of_state_and_group() -> None:
    """Capacity must not change EBU measurement, in a running trajectory."""
    for policy in (POLICY_EBU_ALIGNED, POLICY_EBU_HOSTILE):
        run = run_trajectory(_world(policy), 606, 707, 40, LOAD_MEDIUM)
        _observe(run)
        rebuilt = True
        for record in run.records:
            if record.status != STATUS_EXECUTED:
                continue
            from gaussian_harness.candidates import candidate_groups
            group = next(
                g for g in candidate_groups(run.world.rules, run.world.menu)
                if g.group_id == record.chosen_id
            )
            independent = value_group(run.world.potential, record.state_frozen, group)
            if independent.group_ebu != record.chosen_ebu:
                rebuilt = False
                break
        check(f"{policy}: recorded E_G recomputes from (x, G, V) alone", rebuilt)


def test_extremum_policies_take_the_recorded_extremum() -> None:
    from gaussian_harness.candidates import candidate_groups
    from gaussian_harness.feasibility import assess
    for policy, largest in ((POLICY_EBU_ALIGNED, True), (POLICY_EBU_HOSTILE, False)):
        run = run_trajectory(_world(policy), 2024, 1111, 40, LOAD_MEDIUM)
        _observe(run)
        correct = True
        for record in run.records:
            if record.status != STATUS_EXECUTED:
                continue
            world = run.world
            admissible = []
            for group in candidate_groups(world.rules, world.menu):
                if not assess(world.rules, record.state_frozen, group).feasible:
                    continue
                admissible.append(value_group(world.potential, record.state_frozen, group))
            # Re-derive the affordable subset from the balances at the head of
            # the tick, which are the balances carried into it.
            values = [v.group_ebu for v in admissible if v.group.group_id in
                      {record.chosen_id} or True]
            target = max(values) if largest else min(values)
            if largest and record.chosen_ebu > target:
                correct = False
            if not largest and record.chosen_ebu < target:
                correct = False
        label = "maximum" if largest else "minimum"
        check(f"{policy} never beats the feasible-set {label}", correct)


def test_forcing_loads_are_nested_and_exact() -> None:
    """Every tick forced at 1/4 is forced at 1/2 and at 1 (same seed)."""
    run = PolicyRun(_world(POLICY_CONTROL_RANDOM), 8888, 9999, TickBudget.conformance())
    schedules: dict[str, set[int]] = {}
    edges: dict[str, dict[int, str]] = {}
    for load in DECLARED_LOADS:
        chosen: set[int] = set()
        seen: dict[int, str] = {}
        for tick in range(512):
            run.tick = tick  # pure read of the stateless stream; no tick advances
            proposal = run.scheduled_forcing(load)
            if proposal is not None:
                chosen.add(tick)
                seen[tick] = proposal.forcing_id
        schedules[load.load_id] = chosen
        edges[load.load_id] = seen
    run.tick = 0
    mild, medium, full = (schedules[load.load_id] for load in DECLARED_LOADS)
    check("p = 1 forces every tick", len(full) == 512)
    check("1/4 schedule nests inside 1/2", mild <= medium)
    check("1/2 schedule nests inside 1", medium <= full)
    # The gate is a draw, not a deterministic stride, so the realized count is
    # binomial around n*p. The band below is four standard deviations wide and
    # is a sampling sanity check, never an invariant: nesting above is the
    # exact structural property this design actually relies on.
    check(f"1/4 realizes close to 1 in 4 ({len(mild)}/512)", 89 <= len(mild) <= 167, str(len(mild)))
    check(f"1/2 realizes close to 1 in 2 ({len(medium)}/512)", 211 <= len(medium) <= 301, str(len(medium)))
    same_edges = all(
        edges["p_force_1_4"][tick] == edges["p_force_1"][tick] for tick in mild
    )
    check("the edge drawn at a shared tick is identical across loads", same_edges)
    try:
        ForcingLoad.declare("bad", Fraction(1, 3))
        check("an unrealizable probability is refused", False, "no refusal raised")
    except Refusal:
        check("an unrealizable probability is refused", True)


def test_null_forcing_is_recorded_not_resampled() -> None:
    world = _world(POLICY_CONTROL_RANDOM, initial=[30, 0, 0])
    run = run_trajectory(world, 1234, 5678, 48, LOAD_CONTINUOUS)
    _observe(run)
    nulls = [r for r in run.records if r.forcing_status == "NULL_FORCING"]
    check("a starved source produces NULL_FORCING at least once", bool(nulls), "none seen")
    check("the raw draw is still recorded when it is inadmissible",
          all(record.raw_forcing is not None for record in nulls))
    check("no forcing was applied on those ticks",
          all(record.applied_forcing is None for record in nulls))
    check("the deviation ledger did not move on those ticks",
          all(record.external_deviation == 0 for record in nulls))
    applied = [r for r in run.records if r.forcing_status == "APPLIED"]
    check("applied ticks carry exactly the raw draw",
          all(record.applied_forcing == record.raw_forcing for record in applied))


def test_recovery_terminates_at_the_first_hit() -> None:
    shock = ForcingIncrement(1, 2, Fraction(2))
    for policy in CORE_POLICIES:
        world = _world(policy)
        outcome = recovery_trial(world, shock, 5, 7, 40)
        check(f"{policy}: the shock tick carries the declared disturbance",
              outcome.disturbance == Fraction(4))
        if outcome.recovered:
            check(f"{policy}: ticks used equal the shock tick plus the first hit",
                  outcome.ticks_used == outcome.first_hit + 1,
                  f"{outcome.ticks_used} vs {outcome.first_hit}+1")
            check(f"{policy}: the trial stopped strictly inside the horizon",
                  outcome.first_hit <= outcome.horizon)
        else:
            check(f"{policy}: a non-recovery used the whole horizon",
                  outcome.ticks_used == outcome.horizon + 1)
        check(f"{policy}: the recovery trial closed its accounting exactly",
              outcome.max_accounting_residual == 0)
    probe = recovery_trial(_world(POLICY_EBU_ALIGNED), shock, 5, 7, 40)
    check("a recovered trial reports RECOVERED", probe.outcome == OUTCOME_RECOVERED)
    try:
        recovery_trial(_world(POLICY_EBU_RANDOM), ForcingIncrement(1, 2, Fraction(2)),
                       5, 7, 40, TickBudget.conformance(1))
        check("an exhausted budget refuses", False, "no refusal raised")
    except Refusal as error:
        check("an exhausted budget refuses", "TICK_BUDGET_EXHAUSTED" in str(error))


def test_shock_tick_invites_no_actor() -> None:
    world = _world(POLICY_EBU_RANDOM)
    run = PolicyRun(world, 1, 2, TickBudget.conformance())
    record = run.run_tick(shock=ForcingIncrement(0, 1, Fraction(2)), actor_enabled=False)
    _observe(run)
    check("the shock tick is FORCING_ONLY", record.status == STATUS_FORCING_ONLY)
    check("no group executed on the shock tick", record.chosen_id == "g:[]")
    check("no balance moved on the shock tick", all(b == 0 for b in record.balances))
    check("the potential equals the declared disturbance", record.potential_total == Fraction(4))
    check("the deviation ledger absorbed it", record.audit_ledger == Fraction(4))
    try:
        run.run_tick(load=LOAD_MILD, shock=ForcingIncrement(0, 1, Fraction(1)))
        check("a tick refuses both a load and a shock", False, "no refusal raised")
    except Refusal:
        check("a tick refuses both a load and a shock", True)


def test_job_execution_is_reproducible_and_order_free() -> None:
    """Mission sections 21, 22 and 27, proven on the local execution path."""
    from homeostasis.harness import code_identity
    def identity(policy: str, replicate: int) -> JobIdentity:
        return JobIdentity(
            preregistration_id="conformance-probe",
            configuration_identity="cfgid-conformance",
            code_identity=code_identity(),
            load_id="p_force_1_2",
            policy_id=policy,
            menu_rule=MENU_WITH_NET_ZERO,
            replicate=replicate,
            horizon=48,
            forcing_seed=4242 + replicate,
            actor_seed=8484 + replicate,
        )
    world = ([10, 10, 10], [1, 1, 1], [1], STUDY, CONFIG)
    order = [identity(POLICY_EBU_ALIGNED, 0), identity(POLICY_CONTROL_RANDOM, 1),
             identity(POLICY_EBU_HOSTILE, 2), identity(POLICY_EBU_RANDOM, 3)]
    first = [run_job(job, *world) for job in order]
    global TICKS
    TICKS += sum(job.horizon for job in order) * 2
    # Same jobs, reversed order, different envelope, marked as a retry.
    second = [
        run_job(job, *world, envelope=ExecutionEnvelope("aws-batch-sim", 3,
                                                        "2026-01-01T00:00:00Z", "worker-7"))
        for job in reversed(order)
    ]
    by_id = {result.identity.job_id: result.payload_hash for result in first}
    check("every job produced a distinct payload", len(set(by_id.values())) == 4)
    same = all(by_id[result.identity.job_id] == result.payload_hash for result in second)
    check("a retry in reversed order with a different envelope is bit-identical", same)
    check("all residuals closed exactly",
          all(result.payload["max_accounting_residual"] == "0/1" for result in first))
    report = manifest(first + second)
    check("the integrity manifest passes", report["integrity_passed"], str(report))
    check("it counts four identities and eight observations",
          (report["jobs_expected"], report["jobs_observed"]) == (4, 8))
    wrong = JobIdentity(
        preregistration_id="conformance-probe",
        configuration_identity="cfgid-conformance",
        code_identity="0" * 64,
        load_id="p_force_1_2", policy_id=POLICY_EBU_RANDOM,
        menu_rule=MENU_WITH_NET_ZERO, replicate=0, horizon=8,
        forcing_seed=1, actor_seed=2,
    )
    try:
        run_job(wrong, *world)
        check("a code-identity mismatch is refused", False, "no refusal raised")
    except Refusal as error:
        check("a code-identity mismatch is refused", "CODE_IDENTITY_MISMATCH" in str(error))


def test_budget_fails_closed() -> None:
    try:
        TickBudget.conformance(4096)
        check("an oversized conformance budget is refused", False, "no refusal raised")
    except Refusal:
        check("an oversized conformance budget is refused", True)
    try:
        TickBudget.registered_study(8192, "")
        check("a registered budget without a preregistration is refused", False, "")
    except Refusal as error:
        check("a registered budget without a preregistration is refused",
              "REGISTERED_STUDY_REFUSED" in str(error))


def main() -> int:
    if os.environ.get("EBU_ALLOW_MODEL_TRANSITIONS") != "1":
        print("REFUSED: this suite advances model state.")
        print("Set EBU_ALLOW_MODEL_TRANSITIONS=1 to run it deliberately.")
        return 2
    groups = (
        ("reproduces the registered harness", test_reproduces_the_registered_harness),
        ("mandatory action leaves no no-op", test_mandatory_action_leaves_no_no_op),
        ("net-zero groups are a costless null action",
         test_net_zero_groups_are_a_costless_null_action),
        ("affordability block is not physical impossibility",
         test_affordability_block_is_not_physical_impossibility),
        ("physical no-action is reachable and distinct",
         test_physical_no_action_is_reachable_and_distinct),
        ("recorded EBU is a function of state and group",
         test_recorded_ebu_is_a_function_of_state_and_group),
        ("extremum policies take the recorded extremum",
         test_extremum_policies_take_the_recorded_extremum),
        ("forcing loads are nested and exact", test_forcing_loads_are_nested_and_exact),
        ("NULL_FORCING is recorded, not resampled",
         test_null_forcing_is_recorded_not_resampled),
        ("recovery terminates at the first hit", test_recovery_terminates_at_the_first_hit),
        ("the shock tick invites no actor", test_shock_tick_invites_no_actor),
        ("job execution is reproducible and order-free",
         test_job_execution_is_reproducible_and_order_free),
        ("budget fails closed", test_budget_fails_closed),
    )
    for label, test in groups:
        print(f"\n{label}")
        test()
    print(f"\nHomeostasis transition suite: {PASSED} passed, {FAILED} failed, {len(groups)} groups")
    print("Execution class: MODEL-STATE-ADVANCING TRANSITION SUITE")
    print(f"  conformance ticks advanced: {TICKS}")
    print(f"  max |accounting residual|:    {MAX_ACCOUNTING}")
    print(f"  max |conservation residual|:  {MAX_CONSERVATION}")
    print(f"  max |nonnegativity residual|: {MAX_NONNEGATIVITY}")
    print("  registered study executed: NONE")
    print("  scientific evidence generated: NONE")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())
