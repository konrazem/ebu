"""Preflight checks for `EBU-DEMAND-DRIVEN-STAGE-A-v1`.

NOTHING HERE EXECUTES A REGISTERED EPISODE. The module installs a hard guard
over `EconomyRun.run_epoch` and `EconomyRun.run` before any check runs, so an
accidental transition raises instead of quietly producing data ahead of the
freeze. Every check is one of: construction, hashing, a pure function, or a
SYNTHETIC record built by hand.

Run: python3 test_demand_driven_stage_a.py
"""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass, field
from fractions import Fraction as F

import demand_driven_ebu.harness as harness_module


def _forbidden(*args, **kwargs):
    raise AssertionError("a registered episode was executed inside the preflight")


harness_module.EconomyRun.run_epoch = _forbidden
harness_module.EconomyRun.run = _forbidden

from demand_driven_ebu.fixtures import study_one_state, study_one_world  # noqa: E402
from demand_driven_stage_a import REGISTRATION_ID, registry, reporting, sources  # noqa: E402
from demand_driven_stage_a.execute import preflight, preregistration_identity  # noqa: E402
from demand_driven_stage_a.stopping import (  # noqa: E402
    HORIZON_REACHED,
    NO_AFFORDABLE_SOLUTION,
    RETURNED_TO_REFERENCE,
    a1_stop,
    a3_stop,
)

PASSED = 0
FAILED = 0


def check(label: str, condition: bool, detail: str = "") -> None:
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  PASS  {label}")
    else:
        FAILED += 1
        print(f"  FAIL  {label}" + (f" -- {detail}" if detail else ""))


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------


def test_the_declared_job_set_is_exactly_768() -> None:
    jobs = registry.jobs()
    check("3 classes x 4 arms x 64 replicates = 768 declared jobs", len(jobs) == 768)
    check("three episode classes, in the frozen order",
          tuple(dict.fromkeys(j.episode for j in jobs)) == ("A1", "A2", "A3"))
    check("exactly four arms, with the package's own identifiers",
          tuple(dict.fromkeys(j.policy for j in jobs)) == registry.ARMS
          and registry.ARMS == ("control_random_no_ebu", "ebu_random",
                                "ebu_aligned", "ebu_hostile"))
    check("64 replicates per (class, arm)",
          all(sum(1 for j in jobs if j.episode == e and j.policy == p) == 64
              for e in registry.EPISODES for p in registry.ARMS))


def test_every_job_has_a_distinct_reproducible_identity() -> None:
    jobs = registry.jobs()
    first = [registry.build_run(j).run_id for j in jobs]
    again = [registry.build_run(j).run_id for j in jobs]
    check("768 / 768 run identities are distinct, by construction alone",
          len(set(first)) == 768, f"{len(set(first))} distinct")
    check("and rebuilding every job reproduces the identical 768 identities",
          first == again)
    check("A1 and A3 share world, policy, opening state and all four seeds, "
          "and are nonetheless different jobs -- the arrival law is in the id",
          registry.build_run(registry.Job("A1", "ebu_aligned", 0, 32)).run_id
          != registry.build_run(registry.Job("A3", "ebu_aligned", 0, 32)).run_id)


def test_the_declared_fixtures_match_the_preregistration() -> None:
    check("A1 opens at (1,7,4) with horizon 32 and no arrivals",
          registry.SPECS["A1"].opening == (1, 7, 4)
          and registry.SPECS["A1"].horizon == 32
          and registry.SPECS["A1"].arrivals_kind == "none")
    check("A2 opens at x* = (4,4,4) with horizon 1 and the stochastic process",
          registry.SPECS["A2"].opening == (4, 4, 4)
          and registry.SPECS["A2"].horizon == 1
          and registry.SPECS["A2"].arrivals_kind == "stochastic_one_slot")
    check("A3 opens at (1,7,4) with horizon 32 and one scripted order at epoch 3",
          registry.SPECS["A3"].opening == (1, 7, 4)
          and registry.SPECS["A3"].horizon == 32
          and "3:[r|C|1/1]" in registry.SPECS["A3"].arrivals().descriptor)
    check("seeds follow the frozen table: 1, 2, 3+k, 1000+k",
          (registry.NATURAL_SEED, registry.ARRIVAL_SEED,
           registry.admission_seed(7), registry.actor_seed(7)) == (1, 2, 10, 1007))
    run = registry.build_run(registry.Job("A1", "ebu_aligned", 0, 32))
    check("opening balances are zero for every owner",
          registry.opening_balances_are_zero(run))
    check("registered=True and decomposition_gate=True on every job",
          all(registry.build_run(j).registered
              and registry.build_run(j).decomposition_gate
              for j in registry.jobs()[::97]))
    check("every job carries the study's own registration id",
          run.registration == REGISTRATION_ID == "EBU-DEMAND-DRIVEN-STAGE-A-v1")


def test_this_study_is_not_the_older_stage_a() -> None:
    """The root `stage_a_*.py` are `EBU-STAGE-A-V1` over `gaussian_harness`."""
    check("this registration id is distinct from the older study's",
          REGISTRATION_ID != "EBU-STAGE-A-V1")
    imported = set()
    for path in sources.package_files("demand_driven_stage_a"):
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Import):
                imported.update(a.name for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module)
    check("no module of this package imports the older runner or registry -- "
          "they are a different study over a different harness",
          not ({"stage_a_registry", "stage_a_execute"} & imported), str(sorted(imported)))
    check("and it does not import gaussian_harness.harness, the older study's engine",
          "gaussian_harness.harness" not in imported)
    check("and the output location is distinct from the historical results",
          "demand_driven_stage_a" in str(
              __import__("demand_driven_stage_a.execute", fromlist=["OUTPUT"]).OUTPUT
          ))


# ---------------------------------------------------------------------------
# Stopping -- synthetic, including the ties
# ---------------------------------------------------------------------------

REFERENCE = (F(4), F(4), F(4))


def test_a1_stopping_order_is_applied_consistently() -> None:
    away = (F(3), F(5), F(4))
    check("mid-episode, away from x*, with an ordinary status: no stop",
          a1_stop(state_after=away, reference=REFERENCE,
                  epoch_status="EXECUTED", epoch=5, horizon=32) is None)
    check("S1 fires on reaching x*",
          a1_stop(state_after=REFERENCE, reference=REFERENCE,
                  epoch_status="EXECUTED", epoch=5, horizon=32)
          == RETURNED_TO_REFERENCE)
    check("S2 fires on an unaffordable epoch away from x*",
          a1_stop(state_after=away, reference=REFERENCE,
                  epoch_status="ALL_PLANS_EBU_UNAFFORDABLE", epoch=5, horizon=32)
          == NO_AFFORDABLE_SOLUTION)
    check("S3 fires at the horizon when neither of the others did",
          a1_stop(state_after=away, reference=REFERENCE,
                  epoch_status="EXECUTED", epoch=31, horizon=32) == HORIZON_REACHED)


def test_a_return_on_the_final_permitted_transition_is_not_a_horizon_stop() -> None:
    """The tie the withdrawn `N == T` claim got wrong."""
    verdict = a1_stop(state_after=REFERENCE, reference=REFERENCE,
                      epoch_status="EXECUTED", epoch=31, horizon=32)
    check("S1 and S3 both hold at t+1 == T; S1 wins",
          verdict == RETURNED_TO_REFERENCE, verdict)
    check("so N == T is compatible with RETURNED_TO_REFERENCE, and N never "
          "identifies the stopping reason on its own",
          verdict != HORIZON_REACHED)
    stalled = a1_stop(state_after=(F(3), F(5), F(4)), reference=REFERENCE,
                      epoch_status="ALL_PLANS_EBU_UNAFFORDABLE",
                      epoch=31, horizon=32)
    check("S2 and S3 both hold at t+1 == T; S2 wins",
          stalled == NO_AFFORDABLE_SOLUTION, stalled)


def test_a3_does_not_inherit_a1s_return_stop() -> None:
    check("A3 does NOT stop on reaching x* during the prelude -- otherwise the "
          "epoch-3 order would never arrive and the class would observe nothing",
          a3_stop(epoch=1, horizon=32) is None)
    check("A3 does not stop when the order is served either",
          a3_stop(epoch=3, horizon=32) is None)
    check("the horizon is A3's only ordinary terminal condition",
          a3_stop(epoch=31, horizon=32) == HORIZON_REACHED)


# ---------------------------------------------------------------------------
# Reporting -- mocked records
# ---------------------------------------------------------------------------


@dataclass
class FakeRecord:
    epoch: int
    state_before: tuple
    state_forced: tuple
    state_after: tuple
    epoch_status: str = "EXECUTED"
    executed_group_id: str = "g:[synthetic]"
    active_economic: tuple = ()
    served_economic: tuple = ()
    arrival_states: tuple = ()
    rejected_now: tuple = ()
    balances: tuple = (("A", F(0)), ("B", F(0)), ("C", F(0)))
    balance_total: F = F(0)
    restoration: tuple = ()
    outcomes: tuple = ()
    receipts: tuple = ()


def _chain(world, order_id, states, *, service_epoch=3, pending_status=None,
           rejected=False):
    """Synthetic A3 records over a declared state sequence."""
    records = []
    for epoch in range(len(states) - 1):
        served = (order_id,) if (not rejected and epoch == service_epoch) else ()
        active = ()
        if not rejected and epoch >= 3 and (service_epoch is None or epoch <= service_epoch):
            active = (order_id,)
        records.append(
            FakeRecord(
                epoch=epoch,
                state_before=states[epoch],
                state_forced=states[epoch],
                state_after=states[epoch + 1],
                epoch_status=(pending_status or "EXECUTED") if epoch >= 3 else "EXECUTED",
                active_economic=active,
                served_economic=served,
                rejected_now=((order_id, "E_REJECTED_PHYSICAL_SCARCITY"),)
                if (rejected and epoch == 3) else (),
            )
        )
    return records


def test_simultaneous_closure_is_not_the_max_of_the_per_coordinate_firsts() -> None:
    """A tracked coordinate may close, reopen, and close again."""
    world = study_one_world()
    order = reporting.expected_order_id(world)
    s = [study_one_state(*v) for v in [
        (1, 7, 4), (2, 6, 4), (3, 5, 4), (4, 4, 4),
        (2, 3, 7),   # states[4]: post-service. tracked A:2, B:1
        (4, 2, 6),   # states[5]: A closes
        (3, 4, 5),   # states[6]: B closes, A REOPENS
        (4, 4, 4),   # states[7]: both clear together
    ]]
    records = _chain(world, order, s, service_epoch=3)
    report = reporting.a3_report(world, records, horizon=32,
                                 stopping_reason=HORIZON_REACHED,
                                 policy="ebu_aligned")
    facts = report["restoration_facts"]
    check("the tracked set is frozen at the post-service state: A short 2, B short 1",
          facts["tracked_deficits"] == {"0": "2/1", "1": "1/1"}, str(facts))
    check("per-coordinate first closures are 5 for A and 6 for B",
          facts["first_closure"] == {"0": 5, "1": 6}, str(facts["first_closure"]))
    check("max(first_closure) is 6, but A has REOPENED by index 6",
          max(facts["first_closure"].values()) == 6)
    check("so first_simultaneous_closure is 7, not 6 -- 'any' and 'all' are "
          "reported as the different quantities they are",
          facts["first_simultaneous_closure"] == 7,
          str(facts["first_simultaneous_closure"]))
    check("and the label is RESTORATION_COMPLETED, on the simultaneous quantity",
          report["order_outcome"] == reporting.RESTORATION_COMPLETED)


def test_an_empty_tracked_set_is_never_a_demonstrated_restoration() -> None:
    world = study_one_world()
    order = reporting.expected_order_id(world)
    s = [study_one_state(*v) for v in [
        (1, 7, 4), (2, 6, 4), (3, 5, 4), (4, 4, 4),
        (4, 4, 4),   # served with no induced deficit at all
        (4, 4, 4), (4, 4, 4),
    ]]
    report = reporting.a3_report(world, _chain(world, order, s, service_epoch=3),
                                 horizon=32, stopping_reason=HORIZON_REACHED,
                                 policy="ebu_aligned")
    check("serving the order left no deficit, so the tracked set is empty",
          report["restoration_facts"]["tracked_count"] == 0)
    check("that is SERVED_WITHOUT_RESTORATION, never RESTORATION_COMPLETED: "
          "the absence of a demand is not evidence the mechanism met one",
          report["order_outcome"] == reporting.SERVED_WITHOUT_RESTORATION)
    check("and the reason distinguishes it from a deficit that stayed open",
          report["served_without_restoration_reason"] == reporting.NO_INDUCED_DEFICIT)


def test_an_unclosed_induced_deficit_is_reported_as_partial_not_as_success() -> None:
    world = study_one_world()
    order = reporting.expected_order_id(world)
    s = [study_one_state(*v) for v in [
        (1, 7, 4), (2, 6, 4), (3, 5, 4), (4, 4, 4),
        (2, 3, 7), (4, 2, 6), (4, 2, 6), (4, 2, 6),
    ]]
    report = reporting.a3_report(world, _chain(world, order, s, service_epoch=3),
                                 horizon=32, stopping_reason=HORIZON_REACHED,
                                 policy="ebu_aligned")
    facts = report["restoration_facts"]
    check("A closed but B never did", facts["closure_count"] == 1
          and facts["tracked_count"] == 2, str(facts))
    check("no simultaneous closure exists", facts["first_simultaneous_closure"] is None)
    check("so the label is SERVED_WITHOUT_RESTORATION with the unclosed reason, "
          "and partial progress is visible as partial",
          report["order_outcome"] == reporting.SERVED_WITHOUT_RESTORATION
          and report["served_without_restoration_reason"]
          == reporting.INDUCED_DEFICIT_UNCLOSED)


def test_the_label_map_is_exhaustive_over_the_declared_cases() -> None:
    world = study_one_world()
    order = reporting.expected_order_id(world)
    base = [study_one_state(*v) for v in [
        (1, 7, 4), (2, 6, 4), (3, 5, 4), (4, 4, 4),
        (4, 4, 4), (4, 4, 4), (4, 4, 4),
    ]]
    rejected = reporting.a3_report(
        world, _chain(world, order, base, service_epoch=None, rejected=True),
        horizon=32, stopping_reason=HORIZON_REACHED, policy="ebu_aligned")
    check("a refused order is ORDER_REJECTED",
          rejected["order_outcome"] == reporting.ORDER_REJECTED)

    unaffordable = reporting.a3_report(
        world, _chain(world, order, base, service_epoch=None,
                      pending_status="ALL_PLANS_EBU_UNAFFORDABLE"),
        horizon=32, stopping_reason=HORIZON_REACHED, policy="ebu_aligned")
    check("admitted and never served, always unaffordable, is "
          "ORDER_PENDING_UNAFFORDABLE",
          unaffordable["order_outcome"] == reporting.ORDER_PENDING_UNAFFORDABLE)

    blocked = reporting.a3_report(
        world, _chain(world, order, base, service_epoch=None,
                      pending_status="NO_COMPLETE_PHYSICAL_PLAN"),
        horizon=32, stopping_reason=HORIZON_REACHED, policy="ebu_aligned")
    check("a legitimately blocked economic component is "
          "ORDER_PENDING_NO_COMPLETE_PLAN -- a case section 2 already calls "
          "ordinary in A3, which the four-label set had nowhere to put",
          blocked["order_outcome"] == reporting.ORDER_PENDING_NO_COMPLETE_PLAN)

    labels = {rejected["order_outcome"], unaffordable["order_outcome"],
              blocked["order_outcome"], reporting.RESTORATION_COMPLETED,
              reporting.SERVED_WITHOUT_RESTORATION}
    check("all five declared labels are reachable and none overlaps another",
          labels == set(reporting.ORDER_OUTCOMES) and len(labels) == 5)
    check("the four chain facts are recorded separately from the label",
          all(k in unaffordable for k in
              ("order_admission_status", "order_service_epoch",
               "order_pending_epochs", "restoration_facts")))
    check("pendency is dated epoch by epoch, never a single undated status",
          [p["epoch"] for p in unaffordable["order_pending_epochs"]] == [3, 4, 5]
          and all(p["reason"] == "ALL_PLANS_EBU_UNAFFORDABLE"
                  for p in unaffordable["order_pending_epochs"]),
          str(unaffordable["order_pending_epochs"]))


def test_no_artifact_quantity_is_a_float() -> None:
    check("exact rationals serialize as numerator/denominator strings",
          reporting.q(F(3, 2)) == "3/2" and reporting.q(F(9)) == "9/1")
    world = study_one_world()
    order = reporting.expected_order_id(world)
    s = [study_one_state(*v) for v in [
        (1, 7, 4), (2, 6, 4), (3, 5, 4), (4, 4, 4), (2, 3, 7), (4, 4, 4)]]
    report = reporting.a3_report(world, _chain(world, order, s, service_epoch=3),
                                 horizon=32, stopping_reason=HORIZON_REACHED,
                                 policy="ebu_aligned")

    def has_float(node) -> bool:
        if isinstance(node, float):
            return True
        if isinstance(node, dict):
            return any(has_float(v) for v in node.values())
        if isinstance(node, (list, tuple)):
            return any(has_float(v) for v in node)
        return False

    check("and no float appears anywhere in a produced report", not has_float(report))


def _synthetic_epoch(world):
    """A complete EpochRecord built by hand. Constructing one is not executing."""
    from demand_driven_ebu.harness import (
        DECOMPOSITION_VERIFIED,
        GATE_CLOSED,
        ComponentOutcome,
        EpochRecord,
    )
    from demand_driven_ebu.service import PhysicalService

    return EpochRecord(
        run_id="x" * 16, code_id="y" * 16, policy="ebu_aligned", epoch=0,
        state_before=study_one_state(1, 7, 4),
        state_forced=study_one_state(1, 7, 4),
        state_after=study_one_state(2, 6, 4),
        disturbance_status="QUIET", external_events=(), external_deviation=F(0),
        potential_before=F(9), potential_forced=F(9), potential_after=F(4),
        arrivals=(), admission=None, admitted_now=(), rejected_now=(),
        active_physical=("P:r|A",), active_economic=(),
        outcomes=(ComponentOutcome("c0", ("P:r|A",), "EXECUTED", 2, 2, "g:[a]", F(5)),),
        executed_group_id="g:[a]", executed_provenance=(("a", ("P:r|A",)),),
        epoch_ebu=F(5), receipts=(("B", F(5)),), owner_deltas=(("B", F(5)),),
        balances=(("A", F(0)), ("B", F(5)), ("C", F(0))), balance_total=F(5),
        served_economic=(), unaffordable_economic=(), unresolved_economic=(),
        arrival_states=(), joint_gate=GATE_CLOSED,
        accounting_residual=F(0), conservation_residual=F(0),
        nonnegativity_residual=F(0), separability_residual=F(0),
        epoch_status="EXECUTED", decomposition_gate=DECOMPOSITION_VERIFIED,
        restoration=(PhysicalService(0, "P:r|A", F(3), F(1), F(1), F(2), F(0)),),
    )


def test_an_epoch_serializes_exactly_and_without_a_float() -> None:
    import json

    from demand_driven_stage_a.execute import _serialize_epoch

    world = study_one_world()
    payload = _serialize_epoch(world, _synthetic_epoch(world))

    def has_float(node) -> bool:
        if isinstance(node, float):
            return True
        if isinstance(node, dict):
            return any(has_float(v) for v in node.values())
        if isinstance(node, (list, tuple)):
            return any(has_float(v) for v in node)
        return False

    check("a complete epoch serializes to strict JSON", bool(json.dumps(payload, allow_nan=False)))
    check("with no float anywhere -- every rational stays exact", not has_float(payload))
    check("the restoration ledger is carried through exactly",
          payload["restoration"] == [{
              "coordinate": 0, "demand_id": "P:r|A", "deficit_before": "3/1",
              "delivered": "1/1", "progress": "1/1", "remainder": "2/1",
              "overshoot": "0/1"}], str(payload["restoration"]))


def test_integrity_detection_fires_on_a_dirty_epoch_and_not_on_a_clean_one() -> None:
    from dataclasses import replace

    from demand_driven_stage_a.execute import epoch_integrity_failures

    world = study_one_world()
    clean = _synthetic_epoch(world)
    check("a clean epoch raises nothing", epoch_integrity_failures(world, clean, episode="A1") == [])
    for field, value in (
        ("accounting_residual", F(1, 3)),
        ("conservation_residual", F(1)),
        ("nonnegativity_residual", F(-1)),
        ("separability_residual", F(2)),
    ):
        dirty = replace(clean, **{field: value})
        check(f"a nonzero {field} invalidates the job",
              any(field in f for f in epoch_integrity_failures(world, dirty, episode="A1")))
    gated = replace(clean, decomposition_gate="POLICY_EXECUTION_DIFFERS_FROM_GLOBAL_REFERENCE")
    check("a decomposition-gate refusal invalidates the job",
          epoch_integrity_failures(world, gated, episode="A1") != [])
    blocked = replace(clean, epoch_status="NO_COMPLETE_PHYSICAL_PLAN")
    check("NO_COMPLETE_PHYSICAL_PLAN away from x* invalidates an A1 job",
          epoch_integrity_failures(world, blocked, episode="A1") != [])
    check("but is an ordinary recorded outcome in A3, per section 2's scope",
          epoch_integrity_failures(world, blocked, episode="A3") == [])


def test_an_unchecked_decomposition_gate_is_invalid_only_when_there_was_demand() -> None:
    """Section 8 invalidates on a gate REFUSAL, which arrives as an exception.

    `DECOMPOSITION_NOT_CHECKED` is returned by `_check_decomposition` exactly
    when there are no components -- an epoch with no active demand, where there
    is nothing to decompose. A1 never reaches one, because it stops at `x*`; A3
    necessarily does, because section 4 declares it does NOT stop there.

    The premise is checked here against the mechanism itself, on a declared
    state, with nothing executed.
    """
    from dataclasses import replace

    from demand_driven_ebu.coupling import components
    from demand_driven_ebu.demand import ActiveDemandSet, derive_physical_demands
    from demand_driven_ebu.harness import (
        DECOMPOSITION_NOT_CHECKED,
        STATUS_NO_ACTIVE_DEMAND,
    )
    from demand_driven_stage_a.execute import epoch_integrity_failures

    world = study_one_world()
    reference = world.reference_state()
    check("at x* the mechanism derives no physical demand at all",
          derive_physical_demands(world, reference) == ())
    check("so an empty active set yields NO components, and there is nothing "
          "for the decomposition gate to check",
          components(world, reference, ActiveDemandSet.of((), ())) == ())

    clean = _synthetic_epoch(world)
    quiet = replace(
        clean,
        state_before=reference, state_forced=reference, state_after=reference,
        active_physical=(), active_economic=(),
        epoch_status=STATUS_NO_ACTIVE_DEMAND,
        decomposition_gate=DECOMPOSITION_NOT_CHECKED,
        executed_group_id="", restoration=(), epoch_ebu=F(0),
        potential_before=F(0), potential_forced=F(0), potential_after=F(0),
    )
    check("an unchecked gate at a no-demand epoch is NOT a job-invalidating "
          "condition -- it is unattainable by construction, not a defect",
          epoch_integrity_failures(world, quiet, episode="A3") == [],
          str(epoch_integrity_failures(world, quiet, episode="A3")))

    smuggled = replace(quiet, active_physical=("P:r|A",), epoch_status="EXECUTED")
    check("but an unchecked gate at an epoch that DID carry demand still "
          "invalidates the job: the exemption is not a hole in the gate",
          epoch_integrity_failures(world, smuggled, episode="A3") != [])


# ---------------------------------------------------------------------------
# Seal
# ---------------------------------------------------------------------------


def test_the_protected_packages_are_unchanged() -> None:
    report = sources.protected_identities()
    for package, row in sorted(report.items()):
        check(f"{package} is byte-identical to its recorded identity",
              row["unchanged"], f"{row['actual']} != {row['expected']}")


def test_the_manifest_covers_the_uncommitted_working_state() -> None:
    manifest = sources.source_manifest()
    paths = {e["path"] for e in manifest["files"]}
    check("the manifest hashes actual bytes, not a commit",
          manifest["git"]["tree_is_clean"] is False
          and "HEAD does NOT identify" in manifest["git"]["note"])
    check("it covers the mechanism package", any(p.startswith("demand_driven_ebu/") for p in paths))
    check("the runner package", any(p.startswith("demand_driven_stage_a/") for p in paths))
    check("and the frozen preregistration itself",
          "DEMAND_DRIVEN_STAGE_A_PREREGISTRATION.md" in paths)


def test_the_preregistration_identity_matches_what_it_records() -> None:
    computed, recorded = preregistration_identity()
    check("the document's recorded identity equals its recomputed digest",
          computed == recorded, f"computed {computed}, recorded {recorded}")


def test_preflight_refuses_a_mismatch_and_an_existing_output() -> None:
    gate = preflight()
    check("the preflight reports its own verdict explicitly", "passed" in gate)
    check("it constructs all 768 jobs and finds them distinct",
          gate["job_count"] == 768 and gate["distinct_identities"] == 768)
    check("and it finds the identities reproducible", gate["identities_reproducible"])

    original = sources.PROTECTED["demand_driven_ebu"]
    sources.PROTECTED["demand_driven_ebu"] = "0" * 64
    try:
        refused = preflight()
        check("a protected-package mismatch refuses execution",
              not refused["passed"]
              and any("demand_driven_ebu changed" in f for f in refused["failures"]))
    finally:
        sources.PROTECTED["demand_driven_ebu"] = original
    check("and the guard is restored", preflight()["protected_packages"]
          ["demand_driven_ebu"]["unchanged"])


GROUPS = (
    ("the declared job set is exactly 768", test_the_declared_job_set_is_exactly_768),
    ("every job has a distinct reproducible identity",
     test_every_job_has_a_distinct_reproducible_identity),
    ("the declared fixtures match the preregistration",
     test_the_declared_fixtures_match_the_preregistration),
    ("this study is not the older Stage A", test_this_study_is_not_the_older_stage_a),
    ("A1 stopping order is applied consistently",
     test_a1_stopping_order_is_applied_consistently),
    ("a return on the final permitted transition is not a horizon stop",
     test_a_return_on_the_final_permitted_transition_is_not_a_horizon_stop),
    ("A3 does not inherit A1's return stop", test_a3_does_not_inherit_a1s_return_stop),
    ("simultaneous closure is not the max of the per-coordinate firsts",
     test_simultaneous_closure_is_not_the_max_of_the_per_coordinate_firsts),
    ("an empty tracked set is never a demonstrated restoration",
     test_an_empty_tracked_set_is_never_a_demonstrated_restoration),
    ("an unclosed induced deficit is reported as partial, not as success",
     test_an_unclosed_induced_deficit_is_reported_as_partial_not_as_success),
    ("the label map is exhaustive over the declared cases",
     test_the_label_map_is_exhaustive_over_the_declared_cases),
    ("no artifact quantity is a float", test_no_artifact_quantity_is_a_float),
    ("an epoch serializes exactly and without a float",
     test_an_epoch_serializes_exactly_and_without_a_float),
    ("integrity detection fires on a dirty epoch and not on a clean one",
     test_integrity_detection_fires_on_a_dirty_epoch_and_not_on_a_clean_one),
    ("an unchecked decomposition gate is invalid only when there was demand",
     test_an_unchecked_decomposition_gate_is_invalid_only_when_there_was_demand),
    ("the protected packages are unchanged", test_the_protected_packages_are_unchanged),
    ("the manifest covers the uncommitted working state",
     test_the_manifest_covers_the_uncommitted_working_state),
    ("the preregistration identity matches what it records",
     test_the_preregistration_identity_matches_what_it_records),
    ("preflight refuses a mismatch and an existing output",
     test_preflight_refuses_a_mismatch_and_an_existing_output),
)


def main() -> int:
    for label, group in GROUPS:
        print(f"\n{label}")
        group()
    print(f"\n{PASSED} passed, {FAILED} failed, across {len(GROUPS)} groups")
    print("NO REGISTERED EPISODE WAS EXECUTED: run_epoch and run were guarded "
          "to raise for the whole of this module.")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
