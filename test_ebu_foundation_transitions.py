"""EBU foundation checks that CALL A MODEL TRANSITION. Separate execution class.

**THIS SUITE IS NOT STATIC AND IS NOT PART OF THE DEFAULT CI PATH.**

Everything here calls a function that returns a successor state -
`world.apply_joint` or `proto.execute_tick`.  Those are pure functions from one
frozen synthetic state to its successor, they loop nothing and they produce no
trajectory, but they ARE model transitions, and a suite containing them cannot
honestly be labelled static-only.  They were previously mixed into
`test_ebu_foundation.py`, whose footer then claimed
`Model-state advancement: NONE`.  That claim was FALSE and is withdrawn; see
section 7 of the controller-correction record.

**Execution class.**  Running this file advances model state on synthetic
fixture data.  It therefore requires an explicit opt-in:

    EBU_ALLOW_MODEL_TRANSITIONS=1 python test_ebu_foundation_transitions.py

Without that variable it refuses and exits non-zero, so it cannot be executed
by accident, by a default CI job, or by a tool that runs every `test_*.py` it
finds.

**What it still is NOT.**  No trajectory, no campaign, no parameter search, no
scientific evidence, no AWS, no network, no subprocess, no file written.  The
tick budget is `TickBudget.conformance()`, which admits exactly ONE tick and
refuses a second, so a trajectory cannot be produced by looping this module even
by accident.  The controller is `FixtureRejectAllController`, which carries
family `FIXTURE-ONLY` and can never be registered as a scientific study arm.

The STATIC suite retains coverage of the same guarantees by AST inspection and
pure-function checks - see `test_transition_guards_statically` there.
"""
from __future__ import annotations

import os
import sys

import ebu_test_protocol as proto
import ebu_test_world as world

PASSED = FAILED = GROUPS = 0
EXACT = 1e-12
OPT_IN = "EBU_ALLOW_MODEL_TRANSITIONS"

# Every transition this suite performs, declared up front so the execution
# record can be written from the declaration rather than from memory.
DECLARED_TRANSITIONS = (
    "F8: one world.apply_joint on a synthetic 3-node state (succeeds; "
    "produces a successor state)",
    "conformance tick: one proto.execute_tick under TickBudget.conformance() "
    "with FixtureRejectAllController (succeeds; its successor is identical to "
    "its pre-state because the fixture controller proposes zero)",
)


def group(title: str) -> None:
    global GROUPS
    GROUPS += 1
    print(f"\n[{GROUPS:02d}] {title}")


def check(condition: bool, label: str) -> None:
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  PASS {label}")
    else:
        FAILED += 1
        print(f"  FAIL {label}")


def rejects(fn, label: str, contains: str = "") -> None:
    try:
        fn()
    except Exception as error:
        check(not contains or contains in str(error), label)
    else:
        check(False, label)


def fixture_spec():
    """The same synthetic world the static suite uses. Meaningless numbers."""
    nodes = ("n0", "n1", "n2")
    topology = world.Topology(nodes, (("n0", "n1"), ("n1", "n2"),
                                      ("n0", "n2")))
    return world.WorldSpec(
        spec_id="fixture", spec_version="0", topology=topology,
        node_specs={n: world.NodeSpec(n, 20.0, 4.0, 16.0, 2.0, 1.0, 1.0, 1.0)
                    for n in nodes},
        eta=1.0, dt=1.0, path_semantics="model_realised_constant_rate")


def test_f8_conservation_transition():
    group("F8 - exact closed-system conservation (PERFORMS ONE TRANSITION)")
    spec = fixture_spec()
    check(spec.is_conservative, "the fixture world is closed and lossless")
    state = world.WorldState(spec.digest, {"n0": 18.0, "n1": 1.0, "n2": 1.0})
    ladder = world.QuantityLadder(4.0, 4.0, 4.0, 4.0, 4.0)
    action = world.Action("A", "fixture", ("n0", "n1"), "scalar", ladder,
                          0, 0, "fixture-permission")
    successor = world.apply_joint(spec, state, [action], tolerance=EXACT)
    residual = world.conservation_residual(spec, state, successor)
    check(residual <= EXACT, f"conservation residual {residual:.3e} is exact")
    check(abs(successor.total() - state.total()) <= EXACT,
          "total resource is unchanged")
    check(abs(successor.values["n0"] - 14.0) <= EXACT, "source lost exactly 4")
    check(abs(successor.values["n1"] - 5.0) <= EXACT,
          "destination gained exactly 4")


def test_hard_domain_refusals_through_apply_joint():
    group("NC8 - apply_joint itself refuses an infeasible joint increment")
    spec = fixture_spec()
    state = world.WorldState(spec.digest, {"n0": 18.0, "n1": 1.0, "n2": 1.0})
    huge = world.Action("X", "fixture", ("n0", "n1"), "scalar",
                        world.QuantityLadder(30.0, 30.0, 30.0, 30.0, 30.0),
                        0, 0, "fixture")
    rejects(lambda: world.apply_joint(spec, state, [huge], tolerance=EXACT),
            "NC8 leaving the hard physical domain refuses",
            "hard physical domain")
    half = [world.Action("H0", "fixture", ("n0", "n1"), "scalar",
                         world.QuantityLadder(10.0, 10.0, 10.0, 10.0, 10.0),
                         0, 0, "fixture"),
            world.Action("H1", "fixture", ("n0", "n2"), "scalar",
                         world.QuantityLadder(10.0, 10.0, 10.0, 10.0, 10.0),
                         0, 0, "fixture")]
    rejects(lambda: world.apply_joint(spec, state, half, tolerance=EXACT),
            "NC8 two individually feasible withdrawals are jointly refused")


def test_single_conformance_tick():
    group("the conformance tick (PERFORMS ONE TRANSITION), and its budget")
    spec = fixture_spec()
    state = world.WorldState(spec.digest, {"n0": 18.0, "n1": 1.0, "n2": 2.0})
    schedule = world.DemandSchedule("s", "declared-model", 1, ())
    controller = proto.FixtureRejectAllController.for_conformance_fixture()
    check(controller.family == proto.FIXTURE_ONLY_FAMILY,
          "the tick is driven by a FIXTURE-ONLY controller, never a study arm")

    budget = proto.TickBudget.conformance()
    check(budget.limit == 1, "the conformance budget admits exactly one tick")
    record, successor = proto.execute_tick(
        spec, state, 0, schedule, controller, {"n0": 0.0}, budget=budget,
        conservation_tolerance=EXACT, settlement_tolerance=EXACT)
    check(record.is_valid, "the single conformance tick is valid")
    check(successor.digest == state.digest,
          "the fixture controller proposes zero, so the successor is identical")
    check(budget.used == 1, "exactly one tick was spent")
    rejects(lambda: proto.execute_tick(
                spec, state, 1, schedule, controller, {"n0": 0.0},
                budget=budget, conservation_tolerance=EXACT,
                settlement_tolerance=EXACT),
            "a SECOND tick refuses - a trajectory cannot be produced",
            "budget for")


def main() -> int:
    if os.environ.get(OPT_IN) != "1":
        print(__doc__)
        print(f"REFUSED: this suite performs model transitions and requires "
              f"{OPT_IN}=1. Declared transitions:")
        for item in DECLARED_TRANSITIONS:
            print(f"  - {item}")
        return 2
    for test in (test_f8_conservation_transition,
                 test_hard_domain_refusals_through_apply_joint,
                 test_single_conformance_tick):
        test()
    print(f"\nEBU foundation TRANSITION suite: {PASSED} passed, {FAILED} "
          f"failed, {GROUPS} groups")
    print("Execution class: MODEL TRANSITIONS PERFORMED on synthetic fixtures.")
    print("  foundation fixture model-state advancement: "
          "2 single transitions (F8 apply_joint; 1 conformance tick)")
    print("  scientific-study execution: NONE")
    print("  scientific trajectories generated: 0")
    print("  scientific evidence generated: NONE")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
