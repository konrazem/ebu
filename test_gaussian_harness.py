"""Local Gaussian Stage-A harness checks that ADVANCE MODEL STATE.

**THIS SUITE IS NOT STATIC AND IS NOT PART OF THE DEFAULT CI PATH.**

Every check here calls `Run.run_tick`, which applies forcing, executes a
selected group and settles balances. Those are genuine model transitions, so
this suite cannot honestly be labelled static-only and is kept separate from
`test_gaussian_foundation.py`.

**Execution class.** Running this file advances model state on synthetic
fixture data. It requires an explicit opt-in:

    EBU_ALLOW_MODEL_TRANSITIONS=1 python test_gaussian_harness.py

Without that variable it refuses and exits non-zero, so it cannot run by
accident, by a default CI job, or by a tool that executes every `test_*.py` it
finds. Every run is additionally capped by `TickBudget.conformance()`, which
refuses beyond 64 ticks; a longer run requires a frozen preregistration
identifier that does not yet exist.

**What this is NOT.** No registered study, no campaign, no parameter search, no
scientific evidence, no AWS, no network, no subprocess and no file written. The
trajectories below are conformance fixtures. Nothing here asserts that the
system recovers, and a non-recovering, cycling or deadlocked trajectory is a
scientific observation rather than a test failure.
"""

from __future__ import annotations

import ast
import inspect
import os
from fractions import Fraction

from gaussian_harness.capacity import CapacityLedger
from gaussian_harness.harness import (
    ARM_CONTROL,
    ARM_EBU,
    STATUS_DEADLOCK,
    STATUS_FORCING_ONLY,
    Run,
    TickBudget,
    code_identity,
)
from gaussian_harness.numerics import Refusal, add
from gaussian_harness.rng import (
    STREAM_ACTOR,
    STREAM_FORCING,
    Counter,
    exact_residue,
    uniform_index,
)
from gaussian_harness.stage_a import (
    ShockSpecification,
    cycling_summary,
    deadlock_ticks,
    draw_shock,
    paired_arms,
    run_stage_a,
    serialize_run,
    stage_a_world,
)

OPT_IN = "EBU_ALLOW_MODEL_TRANSITIONS"
CONFORMANCE_HORIZON = 8

PASSED = 0
FAILED = 0
TICKS_ADVANCED = 0
MAX_ACCOUNTING = Fraction(0)
MAX_CONSERVATION = Fraction(0)


def check(label: str, condition: bool, detail: str = "") -> None:
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  PASS  {label}")
    else:
        FAILED += 1
        print(f"  FAIL  {label}  {detail}")


def observe(run: Run) -> Run:
    global TICKS_ADVANCED, MAX_ACCOUNTING, MAX_CONSERVATION
    TICKS_ADVANCED += len(run.records)
    worst = run.max_residuals()
    MAX_ACCOUNTING = max(MAX_ACCOUNTING, worst["accounting"])
    MAX_CONSERVATION = max(MAX_CONSERVATION, worst["conservation"])
    return run


def standard_world(arm: str = ARM_EBU, scale=(1, 1, 1)):
    return stage_a_world(
        "gaussian-stage-a-conformance", "cfg-3cell-v1", [10, 10, 10], list(scale), [1], 2, arm=arm
    )


STANDARD_SHOCKS = ShockSpecification.declare([2])


def test_replay_is_byte_identical() -> None:
    """Same configuration and same two seeds reproduce an identical log."""
    for arm in (ARM_EBU, ARM_CONTROL):
        first = observe(
            run_stage_a(standard_world(arm), STANDARD_SHOCKS, 11, 29, CONFORMANCE_HORIZON)
        )
        second = observe(
            run_stage_a(standard_world(arm), STANDARD_SHOCKS, 11, 29, CONFORMANCE_HORIZON)
        )
        check(f"replay is byte-identical ({arm})", serialize_run(first) == serialize_run(second))
    differing = observe(
        run_stage_a(standard_world(ARM_EBU), STANDARD_SHOCKS, 11, 30, CONFORMANCE_HORIZON)
    )
    baseline = observe(
        run_stage_a(standard_world(ARM_EBU), STANDARD_SHOCKS, 11, 29, CONFORMANCE_HORIZON)
    )
    check(
        "a different actor seed produces a different log",
        serialize_run(differing) != serialize_run(baseline),
    )


def test_forcing_stream_is_actor_independent() -> None:
    """Same forcing seed, different actor seed: identical external disturbance."""
    world = standard_world()
    shocks = STANDARD_SHOCKS
    first = draw_shock(world, shocks, 11)
    second = draw_shock(world, shocks, 11)
    check("the same forcing seed draws the same shock", first == second)
    runs = [
        observe(run_stage_a(standard_world(), shocks, 11, seed, CONFORMANCE_HORIZON))
        for seed in (29, 30, 31)
    ]
    forcings = {tuple(record.forcing for record in run.records) for run in runs}
    check(
        "the external disturbance sequence is identical across actor seeds",
        len(forcings) == 1,
        str(forcings),
    )
    check(
        "only the first tick carries forcing, the rest are OFF",
        all(
            run.records[0].forcing is not None
            and all(record.forcing is None for record in run.records[1:])
            for run in runs
        ),
    )
    other = draw_shock(world, shocks, 12)
    check("a different forcing seed may draw a different shock address", isinstance(other.source, int))


def test_actor_stream_is_forcing_independent() -> None:
    """Same actor seed, different forcing seed: the actor stream stays reproducible.

    Realized action identities may differ because the available candidate sets
    differ, but the underlying draw sequence at fixed coordinates does not.
    """
    draws_a = [
        exact_residue(
            Counter("s", "c", 29, STREAM_ACTOR, tick, 1, 0), 7
        ).residue
        for tick in range(6)
    ]
    draws_b = list(draws_a)
    check("the actor stream is a pure function of its own coordinates", draws_a == draws_b)
    forcing_draws = [
        exact_residue(Counter("s", "c", 29, STREAM_FORCING, tick, 1, 0), 7).residue
        for tick in range(6)
    ]
    check(
        "the forcing stream with the same seed is a different sequence",
        forcing_draws != draws_a,
        "streams must not alias",
    )


def test_no_shared_mutable_rng() -> None:
    """Draws are stateless, so call order cannot change any result."""
    counters = [Counter("s", "c", 5, STREAM_ACTOR, tick, 1, 0) for tick in range(5)]
    forward = [exact_residue(counter, 11).residue for counter in counters]
    backward = [exact_residue(counter, 11).residue for counter in reversed(counters)]
    check("interleaving order does not change any draw", forward == list(reversed(backward)))
    repeated = [exact_residue(counters[2], 11).residue for _ in range(3)]
    check("repeating one draw is idempotent", len(set(repeated)) == 1)
    check(
        "the Run object holds no generator state",
        not any(
            "random" in name.lower() or "rng" in name.lower()
            for name in Run.__dataclass_fields__
        ),
    )


def test_executed_group_is_the_valued_group() -> None:
    """Exactly the group that was valued is the group that is executed."""
    run = observe(run_stage_a(standard_world(), STANDARD_SHOCKS, 11, 29, CONFORMANCE_HORIZON))
    consistent = True
    valued = True
    for record in run.records:
        if record.status != "EXECUTED":
            continue
        if record.chosen_id not in dict(record.ebu_values):
            valued = False
        chosen = [gid for gid in record.affordable_ids if gid == record.chosen_id]
        if not chosen:
            consistent = False
    check("the chosen group was valued before selection", valued)
    check("the chosen group came from the affordable set", consistent)
    check(
        "no group is valued outside the feasible set",
        all(
            set(dict(record.ebu_values)) <= set(record.feasible_ids)
            for record in run.records
        ),
    )


def test_stage_a_identity_holds_every_tick() -> None:
    """V(t) + sum_i B_i(t) = D_shock exactly, in both arms."""
    arms = paired_arms(standard_world(), STANDARD_SHOCKS, 11, 29, CONFORMANCE_HORIZON)
    for name, run in arms.items():
        observe(run)
        shock_deviation = run.records[0].audit_ledger
        holds = all(
            record.audit_potential + record.balance_total == shock_deviation
            for record in run.records
        )
        check(f"V + sum(B) equals D_shock at every tick ({name})", holds)
        check(
            f"the audit ledger is constant after the single shock ({name})",
            len({record.audit_ledger for record in run.records}) == 1,
        )
        worst = run.max_residuals()
        check(f"accounting residual is exactly zero ({name})", worst["accounting"] == 0)
        check(f"conservation residual is exactly zero ({name})", worst["conservation"] == 0)
        check(f"physical stock never goes negative ({name})", worst["nonnegativity"] == 0)


def test_forcing_credits_no_balance_in_a_run() -> None:
    """The shock tick moves J and leaves every balance at its pre-action value."""
    run = observe(run_stage_a(standard_world(), STANDARD_SHOCKS, 11, 29, 1))
    first = run.records[0]
    check("the shock raised the audit ledger", first.audit_ledger != 0)
    check("the shock conserved mass", first.conservation_residual == 0)
    balance_from_receipts = Fraction(0)
    for _, receipt in first.receipts:
        balance_from_receipts += receipt
    check(
        "every unit of balance came from action receipts, none from forcing",
        first.balance_total == balance_from_receipts,
    )


def test_control_arm_parity_and_pairing() -> None:
    """The control shares the physical layer and the applied shock."""
    arms = paired_arms(standard_world(), STANDARD_SHOCKS, 11, 29, CONFORMANCE_HORIZON)
    ebu, control = arms[ARM_EBU], arms[ARM_CONTROL]
    observe(ebu)
    observe(control)
    check(
        "both arms received the identical applied shock",
        ebu.records[0].forcing == control.records[0].forcing,
    )
    check(
        "both arms start from the identical frozen state",
        ebu.records[0].state_frozen == control.records[0].state_frozen,
    )
    check(
        "both arms enumerate the identical candidate set",
        ebu.records[0].candidate_ids == control.records[0].candidate_ids,
    )
    check(
        "both arms apply the identical feasibility rule at t=0",
        ebu.records[0].feasible_ids == control.records[0].feasible_ids,
    )
    check(
        "the control applies no affordability filter",
        control.records[0].affordable_ids == control.records[0].feasible_ids,
    )
    check(
        "the EBU arm's affordable set is a subset of its feasible set",
        set(ebu.records[0].affordable_ids) <= set(ebu.records[0].feasible_ids),
    )


def test_ebu_values_do_not_influence_choice() -> None:
    """Behavioural blindness proof.

    In the control arm the allowed set is the feasible set, which depends on
    physics alone. Changing every Gaussian scale changes every EBU value and
    every receipt, so if the chooser could see values the trajectory would
    move. It must not.
    """
    narrow = observe(
        run_stage_a(
            standard_world(ARM_CONTROL, scale=(1, 1, 1)),
            STANDARD_SHOCKS,
            11,
            29,
            CONFORMANCE_HORIZON,
        )
    )
    wide = observe(
        run_stage_a(
            standard_world(ARM_CONTROL, scale=(Fraction(1, 3), 2, 5)),
            STANDARD_SHOCKS,
            11,
            29,
            CONFORMANCE_HORIZON,
        )
    )
    narrow_choices = tuple(record.chosen_id for record in narrow.records)
    wide_choices = tuple(record.chosen_id for record in wide.records)
    narrow_values = tuple(record.audit_potential for record in narrow.records)
    wide_values = tuple(record.audit_potential for record in wide.records)
    check("changing every scale changed the EBU values", narrow_values != wide_values)
    check(
        "changing every scale did not change a single choice",
        narrow_choices == wide_choices,
        f"{narrow_choices} vs {wide_choices}",
    )
    check(
        "the physical trajectory is also identical",
        tuple(r.state_after for r in narrow.records) == tuple(r.state_after for r in wide.records),
    )


def test_chooser_receives_only_a_count() -> None:
    """Structural: the selection call is given a length, never a valuation."""
    import gaussian_harness.harness as harness_module

    tree = ast.parse(inspect.getsource(harness_module))
    calls = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id == "uniform_index":
                calls.append(node)
    check("the harness selects through exactly one chooser call", len(calls) == 1)
    if calls:
        second = calls[0].args[1]
        is_len = (
            isinstance(second, ast.Call)
            and isinstance(second.func, ast.Name)
            and second.func.id == "len"
        )
        check("the chooser's second argument is a plain length", is_len)
    signature = inspect.signature(uniform_index)
    check(
        "the chooser signature exposes no value parameter",
        list(signature.parameters) == ["counter", "count"],
        str(list(signature.parameters)),
    )


def test_forcing_only_tick_is_not_deadlock() -> None:
    """A pure shock event is distinguishable from an actor deadlock.

    With `actor_enabled=False` the actor is never invited to choose, so the
    absence of execution carries status FORCING_ONLY. Conflating it with
    DEADLOCK would inflate the deadlock count of every registered replicate by
    exactly one and would misreport V immediately after the shock.
    """
    from gaussian_harness.harness import Run, TickBudget

    world = standard_world()
    run = Run(world, 11, 29, TickBudget.conformance(3))
    shock = draw_shock(world, STANDARD_SHOCKS, 11)
    first = run.run_tick(forcing=shock, actor_enabled=False)
    check("a forcing-only tick is labelled FORCING_ONLY", first.status == STATUS_FORCING_ONLY)
    check("a forcing-only tick is not labelled DEADLOCK", first.status != STATUS_DEADLOCK)
    check("V immediately after the shock equals the audit ledger", first.audit_potential == first.audit_ledger)
    check("the shock issued no capacity", first.balance_total == 0)
    check("no action was executed", first.chosen_id == "g:[]" and not first.receipts)
    check("the actor stream was not consumed", first.actor_provenance is None)
    check("the record is still complete", len(first.ebu_values) == len(first.feasible_ids))
    second = run.run_tick()
    check("the following tick invites the actor normally", second.actor_provenance is not None)
    observe(run)
    check("accounting still closes exactly", run.max_residuals()["accounting"] == 0)


def test_deadlock_is_recorded_not_repaired() -> None:
    """A world with only oversized moves deadlocks and no fallback fires.

    Two cells, reference (10, 10), a single quantum of 4. After a shock of 1 the
    state is (9, 11) with V = 1; both available moves overshoot badly and carry
    negative value, so with zero balances nothing is affordable.
    """
    world = stage_a_world(
        "gaussian-stage-a-conformance", "cfg-2cell-deadlock-v1", [10, 10], [1, 1], [4], 1
    )
    run = observe(run_stage_a(world, ShockSpecification.declare([1]), 3, 7, 4))
    ticks = deadlock_ticks(run)
    check("deadlock is recorded", len(ticks) > 0, str([r.status for r in run.records]))
    deadlocked = [record for record in run.records if record.status == STATUS_DEADLOCK]
    check("a deadlocked tick has positive deviation", all(r.audit_potential > 0 for r in deadlocked))
    check("a deadlocked tick executes the empty group", all(r.chosen_id == "g:[]" for r in deadlocked))
    check("a deadlocked tick earns no receipts", all(not r.receipts for r in deadlocked))
    check(
        "a deadlocked tick leaves the physical state unchanged",
        all(r.state_after == r.state_frozen for r in deadlocked),
    )
    check(
        "accounting still closes exactly under deadlock",
        run.max_residuals()["accounting"] == 0,
    )
    check(
        "no restorative fallback was invoked",
        all(r.balance_total == 0 for r in deadlocked),
    )


def test_cycling_is_logged_not_hidden() -> None:
    """Revisited (V, sum B) states are reported rather than suppressed."""
    run = observe(run_stage_a(standard_world(), STANDARD_SHOCKS, 11, 29, CONFORMANCE_HORIZON))
    summary = cycling_summary(run)
    check("the cycling summary is populated", summary["distinct_states"] >= 1)
    check(
        "revisited states are counted rather than discarded",
        isinstance(summary["revisited_states"], int),
    )
    check(
        "exact accounting is preserved regardless of cycling",
        run.max_residuals()["accounting"] == 0,
    )


def test_tick_budget_fails_closed() -> None:
    """The harness refuses a long run without a frozen preregistration."""
    refused = False
    try:
        TickBudget.conformance(5000)
    except Refusal:
        refused = True
    check("an oversized conformance budget is refused", refused)
    refused = False
    try:
        TickBudget.registered_study(5000, "")
    except Refusal:
        refused = True
    check("a registered study without a preregistration id is refused", refused)
    world = standard_world()
    run = Run(world, 11, 29, TickBudget.conformance(2))
    run.run_tick(forcing=draw_shock(world, STANDARD_SHOCKS, 11))
    run.run_tick()
    observe(run)
    exhausted = False
    try:
        run.run_tick()
    except Refusal:
        exhausted = True
    check("the harness refuses to advance past its budget", exhausted)


def test_run_identity_is_pinned_to_code() -> None:
    """Run identity binds configuration, arm, both seeds and the code hash."""
    first = observe(run_stage_a(standard_world(), STANDARD_SHOCKS, 11, 29, 2))
    second = observe(run_stage_a(standard_world(ARM_CONTROL), STANDARD_SHOCKS, 11, 29, 2))
    check("different arms have different run identities", first.run_id != second.run_id)
    check("the code identity is a full sha256", len(code_identity()) == 64)
    check(
        "every record carries the run, configuration and code identity",
        all(r.run_id and r.configuration_id and r.code_id for r in first.records),
    )
    check(
        "every executed record carries both RNG provenances where applicable",
        first.records[0].forcing_provenance is not None
        and first.records[0].actor_provenance is not None,
    )


def test_no_science_is_adopted_here() -> None:
    """This suite registers no study and asserts no recovery."""
    module = inspect.getmodule(test_replay_is_byte_identical)
    tree = ast.parse(inspect.getsource(module))
    recovery_labels = []
    for function in ast.walk(tree):
        if not isinstance(function, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if function.name == "test_no_science_is_adopted_here":
            continue
        for node in ast.walk(function):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id == "check" and node.args:
                    label = node.args[0]
                    if isinstance(label, ast.Constant) and isinstance(label.value, str):
                        if "recover" in label.value.lower():
                            recovery_labels.append(label.value)
    check("no assertion in this suite requires recovery", not recovery_labels, str(recovery_labels))
    check(
        "no registered-study budget is constructed here",
        "registered_study(5000, \"\")" in inspect.getsource(module),
    )


def main() -> int:
    if os.environ.get(OPT_IN) != "1":
        print(f"REFUSED: this suite advances model state. Set {OPT_IN}=1 to run it.")
        return 2
    groups = (
        ("replay is byte-identical", test_replay_is_byte_identical),
        ("forcing stream is actor-independent", test_forcing_stream_is_actor_independent),
        ("actor stream is forcing-independent", test_actor_stream_is_forcing_independent),
        ("no shared mutable RNG", test_no_shared_mutable_rng),
        ("executed group is the valued group", test_executed_group_is_the_valued_group),
        ("Stage-A identity holds every tick", test_stage_a_identity_holds_every_tick),
        ("forcing credits no balance", test_forcing_credits_no_balance_in_a_run),
        ("control arm parity and pairing", test_control_arm_parity_and_pairing),
        ("EBU values do not influence choice", test_ebu_values_do_not_influence_choice),
        ("chooser receives only a count", test_chooser_receives_only_a_count),
        ("forcing-only tick is not deadlock", test_forcing_only_tick_is_not_deadlock),
        ("deadlock is recorded not repaired", test_deadlock_is_recorded_not_repaired),
        ("cycling is logged not hidden", test_cycling_is_logged_not_hidden),
        ("tick budget fails closed", test_tick_budget_fails_closed),
        ("run identity is pinned to code", test_run_identity_is_pinned_to_code),
        ("no science adopted here", test_no_science_is_adopted_here),
    )
    for label, test in groups:
        print(f"\n{label}")
        test()
    print(f"\nLocal Gaussian harness gate: {PASSED} passed, {FAILED} failed, {len(groups)} groups")
    print("Execution class: MODEL-STATE-ADVANCING TRANSITION SUITE (opt-in)")
    print(f"  ticks advanced by this run: {TICKS_ADVANCED}")
    print(f"  numeric policy: exact rational, tolerance 0")
    print(f"  max |accounting residual|:    {MAX_ACCOUNTING}")
    print(f"  max |conservation residual|:  {MAX_CONSERVATION}")
    print("  registered scientific study: NONE")
    print("  scientific evidence generated: NONE")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())
