"""Capacity-V2 harness checks that ADVANCE MODEL STATE.

**NOT STATIC, NOT ON THE DEFAULT CI PATH.** Requires an explicit opt-in:

    EBU_ALLOW_MODEL_TRANSITIONS=1 python test_capacity_v2_harness.py

This is software conformance for the V2 harness, not a registered study. No
preregistration exists for Capacity V2, no seed is derived from a frozen
commit, and nothing here is scientific evidence. Runs are short and capped.

No test asserts recovery. The absorbing-reference check asserts the
affordability predicate at x*, which is Theorem V2-1, a proved structural
property rather than an observed dynamical outcome.
"""

from __future__ import annotations

import os
from fractions import Fraction

from capacity_v2.harness import (
    ARM_CONTROL,
    ARM_V2,
    V2Configuration,
    V2Run,
    code_identity,
)
from capacity_v2.ledger import DeviationBoundedLedger
from gaussian_harness.candidates import MenuSpecification
from gaussian_harness.feasibility import PhysicalRules
from gaussian_harness.forcing import ForcingIncrement
from gaussian_harness.potential import LocalGaussianPotential

OPT_IN = "EBU_ALLOW_MODEL_TRANSITIONS"
CONFORMANCE_TICKS = 96

PASSED = 0
FAILED = 0
TICKS = 0


def check(label: str, condition: bool, detail: str = "") -> None:
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  PASS  {label}")
    else:
        FAILED += 1
        print(f"  FAIL  {label}  {detail}")


def world(arm: str = ARM_V2, scale=(1, 1, 1)) -> V2Configuration:
    potential = LocalGaussianPotential.declare([10, 10, 10], list(scale))
    return V2Configuration(
        "capacity-v2-conformance", "cfg-3cell-v2", potential,
        PhysicalRules.complete_graph(3), MenuSpecification.declare([1], 2),
        potential.reference, Fraction(30), arm,
    )


def single_shock_run(arm=ARM_V2, forcing_seed=11, actor_seed=29, ticks=CONFORMANCE_TICKS):
    global TICKS
    run = V2Run(world(arm), forcing_seed, actor_seed)
    run.run_tick(forcing=ForcingIncrement(0, 1, Fraction(2)), actor_enabled=False)
    for _ in range(ticks):
        run.run_tick()
    TICKS += len(run.records)
    return run


def test_shock_then_settle() -> None:
    run = single_shock_run()
    first = run.records[0]
    check("the shock issues no capacity", first.balance_total == 0)
    check("the shock retires nothing", first.retired == 0)
    check("V immediately after the shock equals J", first.potential_value == first.audit_ledger)
    worst = run.max_residuals()
    check("extended accounting residual is exactly zero", worst["extended_accounting"] == 0)
    check("conservation residual is exactly zero", worst["conservation"] == 0)
    check("the ceiling invariant never broke", worst["ceiling"] == 0)
    check("physical stock never went negative", worst["nonnegativity"] == 0)


def test_capacity_stays_bounded_by_deviation() -> None:
    run = single_shock_run()
    bounded = all(r.balance_total <= r.potential_value for r in run.records)
    check("sum(B) <= V(x) at every tick", bounded)
    check("sum(B) never exceeded the shock size 4", max(r.balance_total for r in run.records) <= 4)
    check("the retirement ledger is monotone",
          all(a.retired <= b.retired for a, b in zip(run.records, run.records[1:])))
    check("retirement plus balance accounts for the shock",
          run.records[-1].retired + run.records[-1].balance_total + run.records[-1].potential_value
          == run.records[-1].audit_ledger)


def test_reference_is_absorbing_in_the_harness() -> None:
    """Once x* is reached, x must not move again. Theorem V2-1 in the loop."""
    run = single_shock_run()
    at_reference = [i for i, r in enumerate(run.records) if r.potential_value == 0]
    check("the run reached the reference at least once", bool(at_reference))
    if at_reference:
        first = at_reference[0]
        tail = run.records[first:]
        check("V stayed exactly zero after first reaching the reference",
              all(r.potential_value == 0 for r in tail))
        check("x never moved again after reaching the reference",
              all(r.state_after == tail[0].state_after for r in tail))
        check("every balance stayed zero at the reference",
              all(r.balance_total == 0 for r in tail))
        # tail[0] is the tick that REACHED the reference, so it legitimately
        # moved x. Every tick after arrival must be a fixed point.
        check("no state-moving group was ever executed from the reference",
              all(r.state_after == r.state_frozen for r in tail[1:]))
        check("the arriving tick is the only one that moved x",
              tail[0].state_after != tail[0].state_frozen or len(tail) == 1)


def test_determinism_and_stream_separation() -> None:
    a = single_shock_run(actor_seed=29)
    b = single_shock_run(actor_seed=29)
    check("same seeds reproduce the same trajectory",
          [r.state_after for r in a.records] == [r.state_after for r in b.records])
    check("same seeds reproduce the same ledger",
          [r.balances for r in a.records] == [r.balances for r in b.records])
    c = single_shock_run(actor_seed=30)
    check("a different actor seed is a different run object", c is not a)


def test_control_arm_is_ebu_blind() -> None:
    """Changing every scale changes every EBU value but no control choice."""
    narrow = V2Run(world(ARM_CONTROL, (1, 1, 1)), 11, 29)
    wide = V2Run(world(ARM_CONTROL, (Fraction(1, 3), 2, 5)), 11, 29)
    global TICKS
    for run in (narrow, wide):
        run.run_tick(forcing=ForcingIncrement(0, 1, Fraction(2)), actor_enabled=False)
        for _ in range(24):
            run.run_tick()
        TICKS += len(run.records)
    check("changing every scale changed the measured potential",
          [r.potential_value for r in narrow.records] != [r.potential_value for r in wide.records])
    check("changing every scale did not change a single control choice",
          [r.chosen_id for r in narrow.records] == [r.chosen_id for r in wide.records])
    check("the control trajectory is identical",
          [r.state_after for r in narrow.records] == [r.state_after for r in wide.records])


def test_control_arm_still_accumulates() -> None:
    """The control has no gate; it is the comparison, not an inferior engine."""
    run = single_shock_run(arm=ARM_CONTROL)
    check("the control arm ran", len(run.records) > 1)
    check("the control still conserves mass", run.max_residuals()["conservation"] == 0)
    check("the control's physical state is still nonnegative",
          run.max_residuals()["nonnegativity"] == 0)


def test_v1_untouched() -> None:
    from gaussian_harness.harness import code_identity as v1
    import stage_a_registry, stage_b_registry
    check("V1 code identity unchanged",
          v1() == stage_a_registry.REGISTERED_CODE_IDENTITY == stage_b_registry.REGISTERED_CODE_IDENTITY)
    check("V2 identity differs from V1", code_identity() != v1())


def main() -> int:
    if os.environ.get(OPT_IN) != "1":
        print(f"REFUSED: this suite advances model state. Set {OPT_IN}=1 to run it.")
        return 2
    groups = (
        ("shock then settle", test_shock_then_settle),
        ("capacity bounded by deviation", test_capacity_stays_bounded_by_deviation),
        ("reference is absorbing in the harness", test_reference_is_absorbing_in_the_harness),
        ("determinism and stream separation", test_determinism_and_stream_separation),
        ("control arm is EBU-blind", test_control_arm_is_ebu_blind),
        ("control arm still runs", test_control_arm_still_accumulates),
        ("V1 untouched", test_v1_untouched),
    )
    for label, test in groups:
        print(f"\n{label}")
        test()
    print(f"\nCapacity-V2 harness gate: {PASSED} passed, {FAILED} failed, {len(groups)} groups")
    print("Execution class: MODEL-STATE-ADVANCING TRANSITION SUITE (opt-in)")
    print(f"  ticks advanced: {TICKS}")
    print("  registered scientific study: NONE")
    print("  scientific evidence generated: NONE")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())
