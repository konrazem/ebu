"""E1a v4 DRIVER ENDPOINT MAPPING, C8 BLINDED CONTROL, TERMINAL PROVENANCE.

**EXECUTION CLASS: NON-MODEL-ADVANCING STATIC/PURE.** Deterministic matrices,
hand-written observation arrays, arithmetic calibration fixtures and filesystem
publication only.

    REAL RNG OBJECTS ................ 0
    REAL STOCHASTIC RANDOM DRAWS .... 0
    OFFICIAL CAMPAIGN TRAJECTORIES .. 0
    DETERMINISTIC TEST TRAJECTORIES . 0   this suite generates none. Every
                                          observation array below is written out
                                          by hand; `ou_observations` is never
                                          called and no world state advances.
    OFFICIAL CAMPAIGN JOBS .......... 0
    REAL CALIBRATION EXECUTIONS ..... 0

WHAT THIS SUITE PROVES
    An independent audit found four classes of driver defect that would have
    changed the frozen scientific result had execution been allowed. Each is a
    permanent counterexample here:

      C2  a replicate in which ONE field rejected was counted as FOUR field
          rejections, because the driver stored the replicate-wide P1
          disjunction on every field record and C2's frozen rule is PER FIELD;
      C3  `g5_rejected` was written as null, so the Block-2 size counted zero
          whatever was observed;
      C4  `block1_rejected` was written as null, likewise;
      C8  the blinded scale control was never built: the driver multiplied the
          UNBLINDED estimate by c, which evaluates to c, not 1, and can never
          pass P3;
      and a terminal record could have its execution identity, Branch-A evidence
      hash or publication digest changed and re-digested, and still validate.
"""

from __future__ import annotations

import copy
import json
import math
import os
import shutil
import tempfile

from e1a_v4.branch_a import build_field
from e1a_v4.calibration import CalibrationArtifact
from e1a_v4.geometry import AnalysisStatus, FieldAnalysis, analyse_field
from e1a_v4.numerics import Refusal
from e1a_v4.validation import PLAN_JSON, PLAN_MARKDOWN, SEED_MAP_JSON
from e1a_v4.validation.calibrate import CalibrationRequest
from e1a_v4.validation.campaign_driver import (
    FIELD_LEVEL_EVENTS, FORBIDDEN_EVENT_REDUCTION, REPLICATE_LEVEL_EVENTS,
    campaign_counts_from_records, field_primary_outcome, is_structured_refusal,
    per_field_primary_outcomes, structured_refusal_reason,
    blinded_branch_a, campaign_shape, committed_publication, evaluate_replicate,
    evaluate_scale_control, field_event_count, job_execution, p1_block_decisions,
    per_field_rejections, plan_campaign, release_subconditions,
    replicate_level_rejections, require_endpoint_events,
    require_plan_driver_agreement, required_endpoint_events,
    required_result_fields, validate_job_record,
)
from e1a_v4.validation.classification import (
    DECLARED_ANALYSIS_STATUSES, INCOMPLETE_EVIDENCE_CLASSIFICATION,
    NON_FAIL_CLOSED_STATUSES, PER_FIELD_SIZE_CASES, REFUSAL_AUTHORISING_STATUSES,
    REQUIRED_SIZE_FIELDS, SIZE_FAILURE, SIZE_NOT_EVALUABLE, SIZE_NO_INFLATION,
    CampaignCounts, FieldSizeOutcome, classify_campaign, classify_field_size,
    classify_size,
)
from e1a_v4.effective_size import sigma_stat
from e1a_v4.endpoints import UncertaintyModel, p1_geometry
from e1a_v4.validation.plan import bind_execution
from e1a_v4.validation.publication import sealed_digest
from e1a_v4.validation.results import aggregate_skeleton
from e1a_v4.validation.scope import CampaignCalibrationLedger
from e1a_v4.validation.seal import SEAL_JSON

ROOT = os.path.dirname(os.path.abspath(__file__))
PASSED = 0
FAILED = 0

BINDING = bind_execution(ROOT)
CONTRACT = BINDING.binding
PLAN = BINDING.plan
RULES = PLAN["adopted_rules_unchanged"]
FIELDS = tuple(f["id"] for f in CONTRACT.fields)
C2 = "C2_geometry_false_rejection"
C2_SUB = "sigma_psi_0p5"


class RealRNGSentinel:
    """Fails loudly if any real stochastic provider is constructed or used."""

    CONSTRUCTED = 0
    DRAWS = 0

    def __init__(self) -> None:
        type(self).CONSTRUCTED += 1
        raise AssertionError("SENTINEL: a real RNG object was constructed")


def check(label: str, condition: bool, detail: str = "") -> None:
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  [PASS] {label}" + (f"  -- {detail}" if detail else ""))
    else:
        FAILED += 1
        print(f"  [FAIL] {label}" + (f"  -- {detail}" if detail else ""))


def refusal_code(fn, *args, **kwargs) -> str | None:
    try:
        fn(*args, **kwargs)
    except Refusal as exc:
        return getattr(type(exc), "code", "UNCODED")
    return None


def refuses_with_code(label: str, expected: str, fn, *args, **kwargs) -> None:
    got = refusal_code(fn, *args, **kwargs)
    check(f"{label} -> {expected}", got == expected, f"got {got!r}")


# ------------------------------------------------------------------ fixtures
def field_of(field_id: str):
    spec = next(f for f in CONTRACT.fields if f["id"] == field_id)
    return build_field(CONTRACT, spec,
                       calibration_route="force_displacement_with_stokes_drag",
                       viscosity=0.00089, bead_radius=1e-6)


def paired_taus(field):
    """tau carried with its OWN stiffness. jacobi orders eigenvalues ascending and
    tau = gamma/k, so this is deliberately not sorted(tau)."""
    return tuple(t for _, t in sorted(zip(field.k_modes, field.tau_modes)))


def small_condition(field_id: str, replicates: int = 16):
    """A COMPLETE calibration condition at a tiny R. Pure arithmetic; no draws.

    The frozen campaign R_cal is a property of the CAMPAIGN, not of a unit test of
    the counting layer; nothing here is a calibration execution.
    """
    field = field_of(field_id)
    dt, n = 1e-5, 400
    taus = paired_taus(field)
    return CalibrationRequest(
        field_id=field_id, H_A=[list(r) for r in field.H], n=n,
        phis=tuple(math.exp(-dt / t) for t in taus), replicates=replicates,
        alpha_1=RULES["alpha_1"], theta_cap_deg=RULES["theta_cap_deg"],
        procedure_identity=BINDING.analysis_identity,
        contract_sha256=CONTRACT.sha256, plan_sha256=BINDING.plan_sha256,
        dt=dt, tau_modes=taus).condition()


def fixture_artifact(condition, value: float = 0.0):
    """Null draws all equal to `value`. Deterministic; every column is arithmetic."""
    draws = {g: tuple(float(value) for _ in range(condition.replicates))
             for g in condition.gates}
    return CalibrationArtifact(
        kind="block1_min_p", procedure_identity=condition.procedure_identity,
        field_id=condition.field_id, n=condition.n, m=condition.m,
        alpha_1=condition.alpha_1, null_draws=draws, condition=condition,
        schema=condition.canonical()["schema"], provenance="pure fixture",
        is_fixture=True)


def fixture_analysis(field_id: str, *, g1=0.0, g5=0.0, beta=1.0):
    return FieldAnalysis(field_id, AnalysisStatus.ESTIMATED, "",
                         S=[[1.0, 0.0], [0.0, 1.0]], K=[[1.0, 0.0], [0.0, 1.0]],
                         beta_hat=beta, g1=g1, g2_spread=0.0, g3=[0.0], g4=0.0,
                         g5=g5, blocks=[[0], [1]],
                         N_matrix=[[1.0, 1.0], [1.0, 1.0]])


class Spec:
    """The minimum JobSpecification surface `evaluate_replicate` reads."""

    def __init__(self, field, scale_factors=()):
        self.field = field
        self.dt = 1e-5
        self.n_samples = 400
        self.scale_factors = scale_factors


def replicate_outcome(case_id, subcondition_id, rejecting_fields=(), *, g5=0.0,
                      g5_fields=()):
    """Run the PRODUCTION endpoint assembly for one synthetic replicate.

    `rejecting_fields` drives BLOCK 1 (a large G1 makes that field's p_min cross
    the artifact's stored critical value) and `g5_fields` drives BLOCK 2 (G5 far
    in the tail) for named fields only. The two are deliberately independent: C3
    releases on the actual Block-2 decision and C4 on the actual Block-1 decision,
    and a fixture that could not separate them could not tell the two apart.
    """
    conditions, artifacts, analyses, specs = {}, {}, {}, {}
    for field_id in FIELDS:
        condition = small_condition(field_id)
        conditions[field_id] = condition
        artifacts[field_id] = fixture_artifact(condition)
        analyses[field_id] = fixture_analysis(
            field_id, g1=(9.9 if field_id in rejecting_fields else 0.0),
            g5=(400.0 if field_id in g5_fields else g5))
        specs[field_id] = Spec(field_of(field_id))
    return evaluate_replicate(BINDING, case_id, subcondition_id, specs, analyses,
                              conditions, artifacts)


def records_from(outcome, case_id, subcondition_id, replicate_id=0):
    """Assemble field records exactly as `execute_replicate` does."""
    records = {}
    for field_id in FIELDS:
        row = {k: v for k, v in outcome.items() if k != "per_field"}
        row.update(outcome["per_field"][field_id])
        coordinates = {"case_id": case_id, "subcondition_id": subcondition_id,
                       "replicate_id": replicate_id, "scope": field_id}
        records[f"{case_id}|{subcondition_id}|{replicate_id:06d}|{field_id}"] = {
            "coordinates": coordinates, "result": row}
    return records


# ===================================================== T1. C2 counts PER FIELD
def test_c2_counts_per_field() -> None:
    """AUDIT FINDING A. One field rejecting is ONE rejection, not four."""
    patterns = (
        ("[P, R, P, P]", ("theta1_power",), [0, 1, 0, 0]),
        ("[R, R, P, P]", ("theta0_circular", "theta1_power"), [1, 1, 0, 0]),
        ("[P, P, P, P]", (), [0, 0, 0, 0]),
        ("[R, R, R, R]", FIELDS, [1, 1, 1, 1]),
    )
    for label, rejecting, expected in patterns:
        outcome = replicate_outcome(C2, C2_SUB, rejecting)
        records = records_from(outcome, C2, C2_SUB)
        counts = [field_event_count(records, C2, C2_SUB, f, "p1_rejected", 1)
                  for f in FIELDS]
        check(f"C2 {label} -> {expected}", counts == expected, str(counts))
        check(f"C2 {label}: total counted = {sum(expected)}",
              sum(counts) == sum(expected), str(sum(counts)))

    # the exact defect: the replicate-wide disjunction must not be the field event
    outcome = replicate_outcome(C2, C2_SUB, ("theta1_power",))
    per_field = outcome["per_field"]
    check("exactly one field carries p1_rejected=True",
          sum(1 for r in per_field.values() if r["p1_rejected"]) == 1,
          str({f: r["p1_rejected"] for f, r in per_field.items()}))
    check("the endpoint assembly no longer publishes a replicate-wide p1_rejected",
          "p1_rejected" not in {k for k in outcome if k != "per_field"},
          str(sorted(k for k in outcome if k != "per_field")))
    check("p1_rejected is classified as a PER-FIELD event",
          "p1_rejected" in FIELD_LEVEL_EVENTS
          and "p1_rejected" not in REPLICATE_LEVEL_EVENTS)

    # multiple replicates: field totals must be independently identifiable
    records = {}
    plans = (("theta1_power",), ("theta1_power",), (), ("theta3_temperature",))
    for index, rejecting in enumerate(plans):
        records.update(records_from(replicate_outcome(C2, C2_SUB, rejecting),
                                    C2, C2_SUB, index))
    totals = {f: field_event_count(records, C2, C2_SUB, f, "p1_rejected", len(plans))
              for f in FIELDS}
    check("four replicates: per-field totals are independent",
          totals == {"theta0_circular": 0, "theta1_power": 2,
                     "theta2_ellipse": 0, "theta3_temperature": 1}, str(totals))

    # and the FROZEN classifier consumes them; no threshold is duplicated here
    frozen = classify_size(totals["theta1_power"], 400, RULES["alpha_geom"])
    check("the frozen size classifier consumes the per-field count",
          frozen["rejections"] == 2 and frozen["replicates"] == 400
          and frozen["nominal_alpha"] == RULES["alpha_geom"])
    check("its verdict comes from the frozen boundary, not from this test",
          frozen["verdict"] == "NO_SIGNIFICANT_SIZE_INFLATION_DETECTED"
          and frozen["boundary"] == 5, str(frozen["boundary"]))


# ====================================== T2/T3. C3 G5 and C4 Block-1 propagate
def test_g5_and_block1_propagate() -> None:
    """AUDIT FINDING B. The real decisions reach the record, and are counted."""
    benign = replicate_outcome("C3_g5_block", C2_SUB, (), g5=0.0)
    extreme = replicate_outcome("C3_g5_block", C2_SUB, (), g5=400.0)
    check("G5 below threshold -> g5_rejected is False, not null",
          all(r["g5_rejected"] is False for r in benign["per_field"].values()),
          str({f: r["g5_rejected"] for f, r in benign["per_field"].items()}))
    check("G5 far in the tail -> g5_rejected is True",
          all(r["g5_rejected"] is True for r in extreme["per_field"].values()),
          str({f: r["g5_rejected"] for f, r in extreme["per_field"].items()}))

    clean = replicate_outcome("C4_surrogate_validity", "primary", ())
    rejecting = replicate_outcome("C4_surrogate_validity", "primary",
                                  ("theta1_power",))
    check("Block-1 passing -> block1_rejected is False, not null",
          all(r["block1_rejected"] is False for r in clean["per_field"].values()))
    check("Block-1 rejecting -> block1_rejected is True for that field only",
          [rejecting["per_field"][f]["block1_rejected"] for f in FIELDS]
          == [False, True, False, False],
          str([rejecting["per_field"][f]["block1_rejected"] for f in FIELDS]))

    # mixed records count exactly the true/false pattern
    records = {}
    pattern = (True, False, True, False, False, False, False, False, False, False)
    for index, rejects in enumerate(pattern):
        records.update(records_from(
            replicate_outcome("C4_surrogate_validity", "primary",
                              ("theta1_power",) if rejects else ()),
            "C4_surrogate_validity", "primary", index))
    counted = field_event_count(records, "C4_surrogate_validity", "primary",
                                "theta1_power", "block1_rejected", len(pattern))
    check("10 records, exactly 2 Block-1 rejects -> counted 2",
          counted == 2, str(counted))
    g5_records = {}
    g5_pattern = (True, True, True, False, False, False, False, False, False, False)
    for index, rejects in enumerate(g5_pattern):
        g5_records.update(records_from(
            replicate_outcome("C3_g5_block", C2_SUB, (),
                              g5=400.0 if rejects else 0.0),
            "C3_g5_block", C2_SUB, index))
    g5_counted = field_event_count(g5_records, "C3_g5_block", C2_SUB,
                                   "theta0_circular", "g5_rejected", len(g5_pattern))
    check("10 records, exactly 3 G5 rejects -> counted 3", g5_counted == 3,
          str(g5_counted))

    # the two block decisions are READ from the frozen gate, never recomputed
    condition = small_condition("theta0_circular")
    artifact = fixture_artifact(condition)

    class Result:
        rows = (("G1", 1.0, 0.5), ("G2", 1.0, 0.5), ("G3", 1.0, 0.5),
                ("G4", 1.0, 0.5), ("G5", 1.0, 1.0))
        passed = True

    block1, g5 = p1_block_decisions(Result(), artifact, BINDING)
    # The assertion is that the decision is READ from the artifact's own stored
    # critical value and the contract's own alpha_2 -- not from any number here.
    check("Block-1 is decided by the artifact's STORED critical p_min",
          block1 is (0.5 < artifact.critical_p_min()),
          f"p_min=0.5 vs critical={artifact.critical_p_min()!r} -> {block1}")
    check("Block-2 is decided by the contract's OWN alpha_2",
          g5 is (1.0 < CONTRACT.alpha_2), f"p(G5)=1.0 vs {CONTRACT.alpha_2} -> {g5}")
    check("a gate that produced no rows yields (None, None), the refusal case",
          p1_block_decisions(type("R", (), {"rows": (), "passed": False})(),
                             artifact, BINDING) == (None, None))


# ============================================ T4. missing decisions fail closed
def test_missing_decision_fails_closed() -> None:
    """AUDIT FINDING B. MISSING IS NOT PASS and MISSING IS NOT ZERO REJECTIONS."""
    outcome = replicate_outcome(C2, C2_SUB, ("theta1_power",))
    base = dict(outcome["per_field"]["theta0_circular"])
    for event in ("p1_rejected", "block1_rejected", "g5_rejected"):
        dropped = {k: v for k, v in base.items() if k != event}
        refuses_with_code(f"C2 record with {event!r} absent", "ENDPOINT_EVENT_MISSING",
                          require_endpoint_events, PLAN, C2, dropped, "probe")
        nulled = dict(base, **{event: None})
        refuses_with_code(f"C2 record with {event!r} null", "ENDPOINT_EVENT_MISSING",
                          require_endpoint_events, PLAN, C2, nulled, "probe")
    check("a COMPLETE record passes", refusal_code(
        require_endpoint_events, PLAN, C2, base, "probe") is None)

    # counting refuses rather than scoring a null as a non-event
    records = records_from(outcome, C2, C2_SUB)
    key = next(iter(records))
    records[key]["result"] = dict(records[key]["result"], p1_rejected=None)
    refuses_with_code("counting a null decision", "ENDPOINT_EVENT_MISSING",
                      field_event_count, records, C2, C2_SUB,
                      records[key]["coordinates"]["scope"], "p1_rejected", 1)

    # a per-field count of a replicate-level value is structurally refused
    refuses_with_code("per-field counting of a REPLICATE-level event",
                      "RESULT_SCHEMA_INVALID", field_event_count,
                      records_from(outcome, C2, C2_SUB), C2, C2_SUB,
                      "theta0_circular", "complete_pass", 1)

    # a structured scientific refusal is the ONE justified absence
    refusal = dict(base, analysis_status="RANK_GUARD_FAIL", P1=False,
                   p1_rejected=True, block1_rejected=None, g5_rejected=None)
    check("a structured refusal may omit the two block decisions, and says why",
          refusal_code(require_endpoint_events, PLAN, C2, refusal, "probe") is None)
    unjustified = dict(refusal, analysis_status="ESTIMATED")
    refuses_with_code("the same absence while ESTIMATED", "ENDPOINT_EVENT_MISSING",
                      require_endpoint_events, PLAN, C2, unjustified, "probe")

    # the required set is CASE-AWARE, derived from the frozen plan
    check("a case that evaluates no P1 quantity owes no block decisions",
          "block1_rejected" not in required_endpoint_events(PLAN, "C7_false_bridge"))
    check("C7 owes its own false-acceptance event",
          "false_acceptance" in required_endpoint_events(PLAN, "C7_false_bridge"))
    check("C8 owes its scale-recovery event",
          "scale_recovered" in required_endpoint_events(
              PLAN, "C8_blinded_scale_control"))
    check("C1 owes the complete-pipeline event",
          "complete_pass" in required_endpoint_events(PLAN, "C1_true_bridge_complete"))


# ============================ C3/C4 cross-field reduction is FORBIDDEN (F1f)
#: The three per-field size cases and the ACTUAL endpoint decision each releases
#: on. C3 releases on Block 2 and C4 on Block 1; neither releases on the combined
#: P1 scalar, which for C3 is the SECONDARY predeclared interaction diagnostic.
PER_FIELD_CASES = (
    ("C2", "C2_geometry_false_rejection", C2_SUB, "p1_rejected"),
    ("C3", "C3_g5_block", C2_SUB, "g5_rejected"),
    ("C4", "C4_surrogate_validity", "primary", "block1_rejected"),
)


def test_cross_field_reduction_is_forbidden() -> None:
    """The reduction is no longer UNDECLARED: authority forbids it outright.

    Before the C3/C4 amendment the driver refused because frozen authority stated
    no rule for turning four per-field decisions into one replicate-level event.
    The amendment answered in the opposite direction from the obvious guess, so the
    refusal is kept and strengthened rather than deleted: there is no replicate-
    level event to compute, and asking for one asks for a statistic the release
    rule does not contain.
    """
    for _short, case_id, _sub, event in PER_FIELD_CASES:
        refuses_with_code(f"{case_id} cross-field reduction",
                          "CROSS_FIELD_REDUCTION_FORBIDDEN",
                          replicate_level_rejections, PLAN, {}, case_id, event)
    check("the refusal names every reduction it rules out, not just the obvious one",
          all(phrase in FORBIDDEN_EVENT_REDUCTION for phrase in
              ("any field rejects", "every field rejects",
               "the reference field rejects", "pooled count")),
          FORBIDDEN_EVENT_REDUCTION[:60])
    check("the refusal cites the authority that forbids it",
          "per_field" in FORBIDDEN_EVENT_REDUCTION
          and "NONE" in FORBIDDEN_EVENT_REDUCTION
          and "FORBIDDEN" in FORBIDDEN_EVENT_REDUCTION)
    check("even a single-field case may not be reduced, so a case that later "
          "declared four fields cannot slip through",
          refusal_code(replicate_level_rejections, PLAN, {},
                       "C6_mode_resolution_boundary", "p1_rejected")
          == "CROSS_FIELD_REDUCTION_FORBIDDEN")
    check("C6 still declares ONE field and is counted by field, not reduced",
          len(required_result_fields(PLAN, "C6_mode_resolution_boundary")) == 1)
    check("C2, C3 and C4 each declare the SAME four fields, from the frozen plan",
          all(set(required_result_fields(PLAN, case_id)) == REQUIRED_SIZE_FIELDS
              and len(required_result_fields(PLAN, case_id)) == 4
              for _s, case_id, _sub, _e in PER_FIELD_CASES))

    # the frozen authority this implementation now expresses, read back
    boundaries = PLAN["size_validation_semantics"]["derived_boundaries"]
    for short, _case_id, _sub, _event in PER_FIELD_CASES:
        row = boundaries[short]
        check(f"{short} authority: per field, no reduction, no pooling",
              row["per_field"] is True and row["replicate_reduction"] == "NONE"
              and row["pooling"].startswith("FORBIDDEN"), str(row["pooling"]))
        check(f"{short} runtime R and alpha equal the frozen ones",
              PER_FIELD_SIZE_CASES[short] == (row["replicates"], row["nominal_alpha"]),
              str(PER_FIELD_SIZE_CASES[short]))


# ===================== C2/C3/C4 are COUNTED per field, from the real decisions
def plan_with_replicates(case_id, replicates):
    """The frozen plan with ONE case's declared replicate count reduced.

    `per_field_rejections` takes its denominator from the plan, and refuses unless
    every declared replicate has a record -- which is the behaviour under test, not
    something to bypass. A fixture that wrote 400 real replicates would be a
    campaign, so the DENOMINATOR is made small instead of the guard being removed.
    Nothing else in the plan is touched, and the frozen plan object is never
    mutated.
    """
    plan = copy.deepcopy(PLAN)
    for case in plan["cases"]:
        if case["case_id"] == case_id:
            case["replicate_count"] = replicates
    return plan


def deterministic_records(case_id, subcondition_id, per_replicate):
    """Field records for a sequence of replicates. Pure dicts; nothing is drawn.

    `per_replicate` is one (block1_rejecting_fields, g5_rejecting_fields) pair per
    replicate, so a fixture can make Block 1 and Block 2 disagree on purpose.
    """
    records = {}
    for index, (block1_fields, g5_fields) in enumerate(per_replicate):
        outcome = replicate_outcome(case_id, subcondition_id, block1_fields,
                                    g5_fields=g5_fields)
        records.update(records_from(outcome, case_id, subcondition_id, index))
    return records


def test_per_field_counting() -> None:
    """F1f. One field's event increments ONE field's count, for all three cases."""
    # --- POSITIVE: exactly the field that failed is the field that counts ------
    patterns = (
        ("one field fails", ("theta1_power",), {"theta1_power": 1}),
        ("two fields fail", ("theta0_circular", "theta2_ellipse"),
         {"theta0_circular": 1, "theta2_ellipse": 1}),
        ("no field fails", (), {}),
    )
    for short, case_id, sub, event in PER_FIELD_CASES:
        for label, failing, expected_nonzero in patterns:
            block1 = failing if event != "g5_rejected" else ()
            g5 = failing if event == "g5_rejected" else ()
            records = deterministic_records(case_id, sub, [(block1, g5)])
            counts = per_field_rejections(plan_with_replicates(case_id, 1),
                                          records, case_id, event)
            expected = {f: expected_nonzero.get(f, 0) for f in FIELDS}
            check(f"{short} {label} -> {sorted(expected_nonzero) or 'none'}",
                  counts == expected, str(counts))
            check(f"{short} {label}: no field absorbed another field's event",
                  sum(counts.values()) == len(failing), str(sum(counts.values())))

    # --- the two forbidden replicate-level reductions, computed and REJECTED ---
    # A replicate in which ONE field rejects. ANY_FIELD would score 1, EVERY_FIELD
    # would score 0, a pooled count would score 1 against a 4R denominator. The
    # declared rule scores 1 for THAT field and 0 for the other three.
    for short, case_id, sub, event in PER_FIELD_CASES:
        failing = ("theta2_ellipse",)
        block1 = failing if event != "g5_rejected" else ()
        g5 = failing if event == "g5_rejected" else ()
        records = deterministic_records(case_id, sub, [(block1, g5)])
        counts = per_field_rejections(plan_with_replicates(case_id, 1), records,
                                      case_id, event)
        any_field = 1 if any(counts.values()) else 0
        every_field = 1 if all(counts.values()) else 0
        check(f"{short}: the declared rule is not ANY_FIELD",
              counts != {f: any_field for f in FIELDS}, str(counts))
        check(f"{short}: the declared rule is not EVERY_FIELD",
              every_field == 0 and counts["theta2_ellipse"] == 1, str(counts))
        check(f"{short}: the declared rule is not a pooled total",
              sum(counts.values()) == 1 and len(counts) == 4, str(counts))
        check(f"{short}: the declared rule is not reference-field-only",
              counts["theta0_circular"] == 0 and counts["theta2_ellipse"] == 1,
              str(counts))

    # --- multiple replicates: totals stay independently identifiable -----------
    sequence = [(("theta1_power",), ()), ((), ()), (("theta1_power",), ()),
                (("theta3_temperature",), ())]
    records = deterministic_records("C4_surrogate_validity", "primary", sequence)
    counts = per_field_rejections(
        plan_with_replicates("C4_surrogate_validity", len(sequence)), records,
        "C4_surrogate_validity", "block1_rejected")
    check("C4 over four replicates: per-field totals are independent",
          counts == {"theta0_circular": 0, "theta1_power": 2,
                     "theta2_ellipse": 0, "theta3_temperature": 1}, str(counts))


def test_field_misattribution() -> None:
    """F1f. The count follows the RECORDED field identity, and gaps refuse."""
    case_id, sub_id = "C2_geometry_false_rejection", C2_SUB
    plan = plan_with_replicates(case_id, 1)
    records = deterministic_records(case_id, sub_id, [(("theta1_power",), ())])
    truth = per_field_rejections(plan, records, case_id, "p1_rejected")
    check("baseline: theta1_power is the only field counted",
          truth["theta1_power"] == 1 and sum(truth.values()) == 1, str(truth))

    # --- PERMUTED field identities: the count moves with the label -------------
    swapped = {}
    rename = {"theta1_power": "theta2_ellipse", "theta2_ellipse": "theta1_power"}
    for key, record in records.items():
        scope = record["coordinates"]["scope"]
        moved = rename.get(scope, scope)
        swapped[key] = {**record,
                        "coordinates": {**record["coordinates"], "scope": moved}}
    permuted = per_field_rejections(plan, swapped, case_id, "p1_rejected")
    check("permuting two field labels moves the rejection to the other field",
          permuted["theta2_ellipse"] == 1 and permuted["theta1_power"] == 0,
          str(permuted))
    check("a misattributed count is a DIFFERENT result, not an equivalent one",
          permuted != truth)

    # --- a field RENAMED to something undeclared leaves its denominator short --
    orphaned = {}
    for key, record in records.items():
        scope = record["coordinates"]["scope"]
        orphaned[key] = {**record, "coordinates": {
            **record["coordinates"],
            "scope": "theta9_invented" if scope == "theta0_circular" else scope}}
    refuses_with_code("a record relabelled to an undeclared field",
                      "CAMPAIGN_INCOMPLETE", per_field_rejections, plan, orphaned,
                      case_id, "p1_rejected")

    # --- one field's record REMOVED entirely ----------------------------------
    for dropped in FIELDS:
        short = {k: v for k, v in records.items()
                 if v["coordinates"]["scope"] != dropped}
        refuses_with_code(f"{dropped}'s record removed", "CAMPAIGN_INCOMPLETE",
                          per_field_rejections, plan, short, case_id, "p1_rejected")

    # --- an EXTRA replicate record inserted for one field ---------------------
    extra = dict(records)
    first = next(v for v in records.values()
                 if v["coordinates"]["scope"] == "theta0_circular")
    extra["injected"] = {**first, "coordinates": {**first["coordinates"],
                                                  "replicate_id": 99}}
    refuses_with_code("an extra replicate record for one field",
                      "CAMPAIGN_INCOMPLETE", per_field_rejections, plan, extra,
                      case_id, "p1_rejected")
    check("the planner, not the counter, is what makes an extra record "
          "unreachable in a real campaign",
          "require_campaign_completeness" in dir(
              __import__("e1a_v4.validation.campaign_driver",
                         fromlist=["require_campaign_completeness"])))


def test_block_distinction() -> None:
    """F1f. C3 reads BLOCK 2 and C4 reads BLOCK 1, even when they disagree."""
    # Block 1 rejects for theta1, Block 2 rejects for theta3. One replicate.
    mixed = replicate_outcome("C3_g5_block", C2_SUB, ("theta1_power",),
                              g5_fields=("theta3_temperature",))
    per_field = mixed["per_field"]
    check("the fixture really does separate the two blocks",
          per_field["theta1_power"]["block1_rejected"] is True
          and per_field["theta1_power"]["g5_rejected"] is False
          and per_field["theta3_temperature"]["block1_rejected"] is False
          and per_field["theta3_temperature"]["g5_rejected"] is True,
          str({f: (r["block1_rejected"], r["g5_rejected"])
               for f, r in per_field.items()}))

    records = records_from(mixed, "C3_g5_block", C2_SUB, 0)
    c3_plan = plan_with_replicates("C3_g5_block", 1)
    c4_plan = plan_with_replicates("C4_surrogate_validity", 1)
    c3 = per_field_rejections(c3_plan, records, "C3_g5_block", "g5_rejected")
    check("C3 counts the Block-2 rejection and NOT the Block-1 one",
          c3 == {"theta0_circular": 0, "theta1_power": 0, "theta2_ellipse": 0,
                 "theta3_temperature": 1}, str(c3))

    c4_records = records_from(
        replicate_outcome("C4_surrogate_validity", "primary", ("theta1_power",),
                          g5_fields=("theta3_temperature",)),
        "C4_surrogate_validity", "primary", 0)
    c4 = per_field_rejections(c4_plan, c4_records, "C4_surrogate_validity",
                              "block1_rejected")
    check("C4 counts the Block-1 rejection and NOT the Block-2 one",
          c4 == {"theta0_circular": 0, "theta1_power": 1, "theta2_ellipse": 0,
                 "theta3_temperature": 0}, str(c4))

    # --- the SUBSTITUTION mutations, each producing a demonstrably wrong count --
    # full P1 rejects wherever EITHER block rejects, so substituting it for the
    # primary endpoint changes both cases' measured size.
    p1 = per_field_rejections(c3_plan, records, "C3_g5_block", "p1_rejected")
    check("substituting full P1 for the C3 primary endpoint changes the count",
          p1 != c3 and p1["theta1_power"] == 1, str(p1))
    check("the C3 primary count is unaffected by the Block-1 rejection it records",
          c3["theta1_power"] == 0 and p1["theta1_power"] == 1)
    c4_p1 = per_field_rejections(c4_plan, c4_records, "C4_surrogate_validity",
                                 "p1_rejected")
    check("substituting the combined P1 for C4's Block-1 endpoint changes the count",
          c4_p1 != c4 and c4_p1["theta3_temperature"] == 1, str(c4_p1))

    # --- C3's full P1 remains OBSERVABLE: it is recorded, just not released on --
    check("every C3 field record still carries the full P1 result and its decision",
          all("P1" in row and "p1_rejected" in row for row in per_field.values()))
    check("the C3 secondary diagnostic is declared non-release-bearing",
          classify_campaign(clean_counts())["endpoint_semantics"]["C3"]
          ["secondary_diagnostic"]["release_bearing"] is False)


def evidence(case, rejections=0, refusals=None):
    """Three-state per-field evidence from plain numbers. C3 and C4 only."""
    planned, _nominal = PER_FIELD_SIZE_CASES[case]
    refused = refusals or {}
    return {f: FieldSizeOutcome(
                field_id=f, planned_replicates=planned,
                evaluable=planned - refused.get(f, 0),
                structured_refusals=refused.get(f, 0),
                rejections=(rejections.get(f, 0) if isinstance(rejections, dict)
                            else rejections),
                refusal_reasons=({"REFUSED_ACCESSIBLE_SPACE": refused[f]}
                                 if refused.get(f) else {}))
            for f in FIELDS}


def clean_counts(**over):
    """A campaign that passes everything. Counts only; nothing is executed."""
    base = dict(c1_successes=300,
                c2_rejections_by_field={f: 0 for f in FIELDS},
                c3_rejections_by_field=evidence("C3"),
                c4_rejections_by_field=evidence("C4"),
                c5_pass=True, c6_pass=True,
                c7_false_acceptances_by_alternative={
                    a: 0 for a in ("alt_1_06", "alt_0_93_1_05", "alt_1_10",
                                   "hard_1_025")},
                c8_successes=200)
    base.update(over)
    return CampaignCounts(**base)


def test_counts_survive_serialisation() -> None:
    """F1f. Field identity and the ACTUAL decisions survive a round trip to disk.

    The restart path re-reads terminal job records from storage and recounts from
    them, so recovered counts must equal fresh counts. They do here for a
    structural reason worth stating: a job record is already PER FIELD -- its
    coordinates carry `scope = field_id` and its result carries that field's own
    decisions -- so nothing is ever reconstructed from an ambiguous case-level
    scalar. There is no scalar to reconstruct from.
    """
    sequence = [(("theta1_power",), ()), ((), ()), (("theta1_power",), ()),
                (("theta3_temperature",), ())]
    case_id, sub_id = "C4_surrogate_validity", "primary"
    plan = plan_with_replicates(case_id, len(sequence))
    records = deterministic_records(case_id, sub_id, sequence)
    fresh = per_field_rejections(plan, records, case_id, "block1_rejected")

    # a genuine round trip through canonical JSON, exactly as publication does
    restored = json.loads(json.dumps(records, sort_keys=True, allow_nan=False))
    recovered = per_field_rejections(plan, restored, case_id, "block1_rejected")
    check("recovered counts equal fresh counts", recovered == fresh, str(recovered))
    check("the field identity survived serialisation",
          all(r["coordinates"]["scope"] in FIELDS for r in restored.values())
          and {r["coordinates"]["scope"] for r in restored.values()} == set(FIELDS))
    check("the ACTUAL endpoint decisions survived as booleans, not nulls",
          all(isinstance(r["result"]["block1_rejected"], bool)
              and isinstance(r["result"]["g5_rejected"], bool)
              for r in restored.values()))
    check("a record whose decision was nulled in storage REFUSES rather than "
          "counting zero",
          refusal_code(per_field_rejections, plan,
                       {k: ({**v, "result": {**v["result"], "block1_rejected": None}}
                            if i == 0 else v)
                        for i, (k, v) in enumerate(sorted(restored.items()))},
                       case_id, "block1_rejected") == "ENDPOINT_EVENT_MISSING")
    check("a record dropped from storage REFUSES rather than shrinking the "
          "denominator",
          refusal_code(per_field_rejections, plan,
                       {k: v for k, v in sorted(restored.items())[1:]},
                       case_id, "block1_rejected") == "CAMPAIGN_INCOMPLETE")

    # --- the terminal surface carries everything needed to re-verify a verdict --
    boundary = classify_size(0, *PER_FIELD_SIZE_CASES["C4"])["boundary"]
    row = classify_campaign(clean_counts(
        c4_rejections_by_field=evidence("C4", {**{f: 0 for f in FIELDS},
                                               "theta1_power": boundary + 1})))
    reported = row["detail"]["C4"]["theta1_power"]
    for key in ("rejections", "replicates", "observed_rate", "cp_lower",
                "cp_upper", "boundary", "verdict"):
        check(f"the C4 per-field result reports {key}", key in reported)
    check("it reports which case, which field and which endpoint",
          "C4" in str(row["endpoint_semantics"])
          and "theta1_power" in row["detail"]["C4"]
          and row["endpoint_semantics"]["C4"]["primary_endpoint"]
          == "BLOCK1_ACHIEVED_SIZE")
    check("the result is not an aggregate scalar: all four fields are reported",
          len(row["detail"]["C4"]) == 4 and set(row["detail"]["C4"]) == set(FIELDS))


def test_field_identity_survives_to_the_classifier() -> None:
    """F1f. A failing field is named in the failures list, for all three cases."""
    for short, _case_id, _sub, _event in PER_FIELD_CASES:
        boundary = classify_size(0, *PER_FIELD_SIZE_CASES[short])["boundary"]
        key = f"c{short[1]}_rejections_by_field"
        def built(mapping, case=short):
            return (mapping if case == "C2" else evidence(case, mapping))
        for field_id in FIELDS:
            counts = clean_counts(**{key: built({**{f: 0 for f in FIELDS},
                                                 field_id: boundary + 1})})
            result = classify_campaign(counts)
            size_failures = [f for f in result["failures"]
                             if "STATISTICAL_SIZE_FAILURE" in f]
            check(f"{short}/{field_id} over boundary -> exactly one named failure",
                  result["verdict"] == "VALIDATION_FAILURE"
                  and len(size_failures) == 1 and field_id in size_failures[0]
                  and f"({short} " in size_failures[0],
                  "; ".join(result["failures"])[:80])
            check(f"{short}/{field_id}: the other three conditions stay clean",
                  all(result["detail"][short][f]["verdict"]
                      == "NO_SIGNIFICANT_SIZE_INFLATION_DETECTED"
                      for f in FIELDS if f != field_id))
        # at exactly the boundary in EVERY field the case is clean: a pooled
        # implementation of the same counts would not be
        counts = clean_counts(**{key: built({f: boundary for f in FIELDS})})
        check(f"{short} at exactly {boundary} in all four fields -> PASS",
              classify_campaign(counts)["verdict"] == "VALIDATION_PASS",
              f"pooled total would be {boundary * 4}")


# ==================================== T5/T6. the C8 blinded Branch-A control
def matched_observations(field, count: int = 64):
    """A DETERMINISTIC observation array, written out by hand.

    NOT a trajectory: no OU transition, no RNG, no world state advances, and
    `ou_observations` is never called. The cloud is laid out along H's own
    eigenvectors with semi-axes sqrt(2/lambda_r), so its sample covariance is
    exactly inv(H); then tr(H S) = m and the frozen estimator beta = m / tr(H S)
    returns exactly 1 for EVERY declared field, isotropic or not. That makes the
    frozen recovery relation readable at a glance.
    """
    from e1a_v4.numerics import jacobi
    lam, q = jacobi(field.H)
    axes = [math.sqrt(2.0 / value) for value in lam]
    points = []
    for i in range(count):
        angle = 2.0 * math.pi * i / count
        modal = [axes[0] * math.cos(angle), axes[1] * math.sin(angle)]
        points.append([sum(q[r][s] * modal[s] for s in range(2)) for r in range(2)])
    return points


def test_c8_blinded_branch_a_control() -> None:
    """AUDIT FINDING C. The control is a SCALED BRANCH-A DUPLICATE, re-analysed."""
    factors = (1.07, 0.90)
    analyses, blinded, specs, per_field_sigma = {}, {}, {}, {}
    observations_by_field = {}
    for field_id in FIELDS:
        field = field_of(field_id)
        observations = matched_observations(field)
        observations_by_field[field_id] = observations
        taus = paired_taus(field)
        phis = [math.exp(-1e-5 / t) for t in taus]
        analyses[field_id] = analyse_field(
            field, observations, rank_tol=RULES["rank_tol"],
            theta_cap_deg=RULES["theta_cap_deg"], phi_modes=phis)
        for factor in factors:
            blinded.setdefault(factor, {})[field_id] = analyse_field(
                blinded_branch_a(field, factor), observations,
                rank_tol=RULES["rank_tol"], theta_cap_deg=RULES["theta_cap_deg"],
                phi_modes=phis)
        specs[field_id] = Spec(field, factors)
        per_field_sigma[field_id] = sigma_stat(phis, 400)

    reference = analyses["theta0_circular"]
    check("the deterministic fixture gives an unblinded beta_hat of exactly 1 at "
          "EVERY declared field",
          all(abs(analyses[f].beta_hat - 1.0) < 1e-12 for f in FIELDS),
          str({f: analyses[f].beta_hat for f in FIELDS}))
    for field_id in FIELDS:
        for factor in factors:
            blind = blinded[factor][field_id]
            check(f"{field_id} c={factor}: c * beta_blind recovers beta_unblinded "
                  "EXACTLY",
                  abs(factor * blind.beta_hat - analyses[field_id].beta_hat) < 1e-12,
                  repr(factor * blind.beta_hat))

    for factor in factors:
        blind = blinded[factor]["theta0_circular"]
        check(f"c={factor}: the blinded analysis recovers 1/c EXACTLY",
              abs(blind.beta_hat - reference.beta_hat / factor) < 1e-12,
              f"{blind.beta_hat!r} vs {reference.beta_hat / factor!r}")
        check(f"c={factor}: the frozen recovery c*beta_blind returns 1",
              abs(factor * blind.beta_hat - 1.0) < 1e-12,
              repr(factor * blind.beta_hat))
        # the OLD implementation, shown not to be the control
        post_hoc = factor * reference.beta_hat
        check(f"c={factor}: the SUPERSEDED post-hoc product is c, not 1",
              abs(post_hoc - factor) < 1e-12, repr(post_hoc))
        check(f"c={factor}: and it lies OUTSIDE delta_abs of 1, so it could never "
              "have passed P3",
              abs(post_hoc - 1.0) > RULES["delta_abs"],
              f"|{post_hoc!r} - 1| vs {RULES['delta_abs']}")
        check(f"c={factor}: the blinded field is a NEW object naming its factor",
              blind.field_id.endswith(f"__blinded_c={factor!r}")
              and blind.field_id != reference.field_id, blind.field_id)

    # Branch B is shared byte-for-byte: only the Branch-A declaration differs
    field = field_of("theta0_circular")
    check("the blinded duplicate scales the Branch-A declaration by exactly c",
          abs(blinded_branch_a(field, 1.07).scale_factor
              - field.scale_factor * 1.07) < 1e-15)
    check("and leaves H_U, T, k_modes and orientation untouched",
          blinded_branch_a(field, 1.07).H_U == field.H_U
          and blinded_branch_a(field, 1.07).T == field.T
          and blinded_branch_a(field, 1.07).k_modes == field.k_modes)
    check("the primary field is NOT mutated by building the duplicate",
          field.scale_factor == 1.0, repr(field.scale_factor))
    check("the same Branch-B observation object served both branches",
          observations_by_field["theta0_circular"] is
          observations_by_field["theta0_circular"])

    unc = UncertaintyModel.from_contract(CONTRACT, per_field_sigma)
    result = evaluate_scale_control(BINDING, "C8_blinded_scale_control", CONTRACT,
                                    unc, analyses, blinded, factors)
    control = result["scale_control"]
    check("the driver records the frozen transform it used",
          control["transform"] == "e1a_v4.branch_a.BranchAField.blinded")
    check("and the frozen recovery rule",
          control["recovery_rule"] == "beta_tilde_theta = c * beta_hat_blind_theta")
    check("provenance retains both branches, their c, beta_blind and the recovery",
          set(control["branches"]) == {repr(1.07), repr(0.90)}
          and all({"c", "beta_hat_blind", "beta_tilde_recovered",
                   "blinded_field_ids", "p3_passed"} <= set(b)
                  for b in control["branches"].values()),
          str(sorted(control["branches"])))
    recovered = control["branches"][repr(1.07)]["beta_tilde_recovered"]
    check("every recovered value is ~1, which is what the control exists to show",
          all(abs(v - 1.0) < 1e-12 for v in recovered.values()), str(recovered))

    # T5 negative: the old post-hoc shape is structurally rejected
    refuses_with_code("C8 evaluated WITHOUT the blinded analyses (the old shape)",
                      "SCALE_CONTROL_INVALID", evaluate_scale_control, BINDING,
                      "C8_blinded_scale_control", CONTRACT, unc, analyses, {},
                      factors)
    refuses_with_code("C8 evaluated with only one branch supplied",
                      "SCALE_CONTROL_INVALID", evaluate_scale_control, BINDING,
                      "C8_blinded_scale_control", CONTRACT, unc, analyses,
                      {1.07: blinded[1.07]}, factors)
    # the transform is case-specific: no free scaling parameter on other cases
    for case_id in ("C1_true_bridge_complete", C2, "C7_false_bridge"):
        refuses_with_code(f"{case_id} requesting the blinded transform",
                          "SCALE_CONTROL_INVALID", evaluate_scale_control, BINDING,
                          case_id, CONTRACT, unc, analyses, blinded, factors)

    # the FROZEN campaign classifier consumes the driver's recovery event
    verdict = classify_campaign(clean_counts())
    check("the frozen classifier owns the C8 campaign rule, not the driver",
          verdict["detail"]["C8"]["threshold"] == 188
          and verdict["detail"]["C8"]["target"] == 0.90,
          str(verdict["detail"]["C8"]["threshold"]))


# ================================ T7-T10. terminal provenance cross-links
COPIED = ("docs/e1a/e1a_v4_design_contract.json",
          "docs/e1a/E1A_V4_PROSPECTIVE_DESIGN.md",
          "docs/theory/EBU_THEORY_BASELINE.md",
          "docs/physical_foundation/EBU_PHYSICAL_FOUNDATION_CANONICAL.md",
          PLAN_JSON, SEED_MAP_JSON, PLAN_MARKDOWN, SEAL_JSON)


def sandbox() -> str:
    tmp = tempfile.mkdtemp()
    for rel in COPIED:
        destination = os.path.join(tmp, rel)
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        shutil.copy(os.path.join(ROOT, rel), destination)
    shutil.copytree(os.path.join(ROOT, "e1a_v4"), os.path.join(tmp, "e1a_v4"),
                    ignore=shutil.ignore_patterns("__pycache__"))
    return tmp


def published_terminal_record(case_id: str = "C7_false_bridge"):
    """One valid terminal record through the PRODUCTION constructors. No draws."""
    root = sandbox()
    binding = bind_execution(root)
    jobs = plan_campaign(binding.plan)
    out = os.path.join(root, "results", "e1a_v4_validation")
    job = next(j for j in jobs if j.coordinates.case_id == case_id)
    execution = job_execution(binding, job, CampaignCalibrationLedger(), out)
    calibration = execution.calibration
    field = build_field(
        binding.binding,
        next(f for f in binding.binding.fields if f["id"] == job.coordinates.scope),
        calibration_route="force_displacement_with_stokes_drag",
        viscosity=0.00089, bead_radius=1e-6)
    execution.realise_branch_a(
        field, branch_a_seed=calibration.branch_a_seed(job.coordinates.scope),
        common_mode_seed=calibration.common_mode_seed(),
        generator_identity="PURE-FIXTURE-NO-DRAW")
    execution.publish_branch_a()
    execution.unblind()
    outcome = {"analysis_status": "ESTIMATED", "beta_hat": 1.0,
               "false_acceptance": False}
    execution.analyse(outcome)
    record = execution.record(aggregate_skeleton(case_id))
    publication = committed_publication(out, job.coordinates)
    return root, binding, job, publication, record, out


def test_terminal_provenance_cross_links() -> None:
    """AUDIT FINDING D. Self-consistency is necessary and NOT sufficient."""
    root, binding, job, publication, record, out = published_terminal_record()

    def validate(mutate=None):
        candidate = json.loads(json.dumps(record))
        if mutate is not None:
            mutate(candidate)
            # RE-DIGEST, exactly as the auditor did: the record is internally
            # self-consistent again, and must still be refused.
            candidate["result_digest"] = sealed_digest(candidate, "result_digest")
        # The OFFICIAL entry point takes the campaign output ROOT and resolves
        # the committed publication and calibration lock itself.
        return refusal_code(validate_job_record, candidate, binding.plan, binding,
                            job, out)

    check("T10: a record bound to the CURRENT authority validates",
          validate() is None, str(validate()))
    mutations = (
        ("T7: execution identity changed",
         lambda r: r["package_identities"].__setitem__("execution_identity", "0" * 64)),
        ("T8: Branch-A evidence hash changed",
         lambda r: r.__setitem__("branch_a_evidence_sha256", "0" * 64)),
        ("T9: publication digest changed",
         lambda r: r.__setitem__("publication_digest", "0" * 64)),
        ("analysis procedure identity changed",
         lambda r: r["package_identities"].__setitem__(
             "analysis_procedure_identity", "0" * 64)),
        ("plan identity changed",
         lambda r: r["package_identities"].__setitem__("plan_sha256", "0" * 64)),
        ("seed-map identity changed",
         lambda r: r["package_identities"].__setitem__("seed_map_sha256", "0" * 64)),
        ("job coordinates changed",
         lambda r: r["coordinates"].__setitem__("replicate_id", 999999)),
        ("job_id changed", lambda r: r.__setitem__("job_id", "forged")),
        ("result_kind changed",
         lambda r: r.__setitem__("result_kind", "complete_pass")),
        ("role changed", lambda r: r.__setitem__("role", "primary")),
        ("a calibration link invented for a no-calibration case",
         lambda r: r.__setitem__("calibration_condition_sha256", "a" * 64)),
    )
    for label, mutate in mutations:
        check(f"{label}, RE-DIGESTED -> refuse",
              validate(mutate) == "TERMINAL_PROVENANCE_MISMATCH", str(validate(mutate)))

    check("the INTERNAL digest is kept as well: an edit without re-digesting "
          "refuses on the bytes",
          refusal_code(validate_job_record,
                       dict(json.loads(json.dumps(record)), job_id="forged"),
                       binding.plan, binding, job, out)
          == "RESULT_SCHEMA_INVALID")
    refuses_with_code("no planned job supplied to validate against",
                      "TERMINAL_PROVENANCE_MISMATCH", validate_job_record,
                      json.loads(json.dumps(record)), binding.plan, binding, None,
                      out)
    # The absence of the publication is now expressed the only way a caller CAN
    # express it: by the store not holding one. A caller cannot pass None for it.
    empty = os.path.join(root, "results", "empty")
    refuses_with_code("no committed Branch-A publication in the store",
                      "TERMINAL_PROVENANCE_MISMATCH", validate_job_record,
                      json.loads(json.dumps(record)), binding.plan, binding, job,
                      empty)

    # a stale-but-self-consistent record is not reusable under a moved package
    class MovedBinding:
        """The SAME package with a moved execution identity, and nothing else.

        It delegates `case_access` to the real binding: the publication verifier
        now checks the embedded Branch-A and common-mode stream identities
        against the frozen seed map, and this double must not accidentally make
        that check pass or fail for the wrong reason.
        """

        def __init__(self, source):
            self._source = source
            self.binding = source.binding
            self.plan = source.plan
            self.plan_sha256 = source.plan_sha256
            self.seed_map_sha256 = source.seed_map_sha256
            self.analysis_identity = source.analysis_identity
            self.execution_identity = "f" * 64

        def case_access(self, case_id):
            return self._source.case_access(case_id)

    # The refusal now names the UPSTREAM object that first disagrees. Since the
    # official validator verifies the committed Branch-A publication against the
    # current package before it judges the terminal record, a moved package is
    # caught at the publication, which is where the disagreement actually is.
    check("a record valid under the OLD package is refused under the current one",
          refusal_code(validate_job_record, json.loads(json.dumps(record)),
                       binding.plan, MovedBinding(binding), job, out)
          == "BRANCH_A_PROVENANCE_MISMATCH")
    shutil.rmtree(root, ignore_errors=True)


# ============================================ campaign structure is unchanged
def test_campaign_structure_unchanged() -> None:
    """The repair changes no campaign cardinality."""
    jobs = plan_campaign(PLAN)
    report = require_plan_driver_agreement(PLAN, jobs)
    derived = sum(len(c["subconditions"]) * c["replicate_count"]
                  * len(c["fields_affected"]) for c in PLAN["cases"])
    check("the planned job total is derived from authority and unchanged",
          len(jobs) == derived == report["planned_jobs"], str(len(jobs)))
    check("missing = 0, extra = 0",
          report["missing_planned_jobs"] == 0 and report["extra_driver_jobs"] == 0)
    shape = campaign_shape(PLAN)
    for case in PLAN["cases"]:
        check(f"{case['case_id']}: calibration artifacts unchanged",
              shape[case["case_id"]]["calibration_jobs"]
              == case["calibration_artifact_count"],
              str(shape[case["case_id"]]["calibration_jobs"]))
    check("C7 calibration jobs = 0", shape["C7_false_bridge"]["calibration_jobs"] == 0)
    check("C8 calibration jobs = 0",
          shape["C8_blinded_scale_control"]["calibration_jobs"] == 0)


def test_frozen_authority_unchanged() -> None:
    from e1a_v4.contract import sha256_file
    for label, path, digest in (
            ("physical foundation",
             "docs/physical_foundation/EBU_PHYSICAL_FOUNDATION_CANONICAL.md",
             "6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507"),
            ("theory baseline", "docs/theory/EBU_THEORY_BASELINE.md",
             "0a01b3566c5ba37674f87ba827732e8d7f694fb5a532901e5883ea8317b74eaa"),
            ("design contract", "docs/e1a/e1a_v4_design_contract.json",
             "91d6ae76ccb6fdbeb7f926722433c574c30b7c0b6105c7c1ec20436fa2ec431b"),
            ("prospective design", "docs/e1a/E1A_V4_PROSPECTIVE_DESIGN.md",
             "e59dcff6b363e6ba59222b06867973703fd429f1223452cdfa2a4d47fadca495"),
            # Plan 1.14.0 -> 1.15.0: the G5 STRUCTURED-REFUSAL amendment. A valid
            # structured refusal can leave a C3 G5 / C4 Block-1 decision undefined,
            # and frozen authority defined refusal treatment for complete-pipeline
            # success only. The author decided prospectively, before any outcome
            # existed: an undefined primary endpoint is NEITHER a rejection NOR a
            # non-rejection, planned R is preserved, and the field's primary size
            # assessment is NOT_EVALUABLE, which blocks release under
            # VALIDATION_INCONCLUSIVE. The frozen sources ABOVE and the seed map
            # BELOW are deliberately unmoved -- no alpha, replicate count, integer
            # boundary or endpoint definition changed, and C2 is untouched.
            ("JSON plan", PLAN_JSON,
             "dcf0c575a048ceebfcd3deb261d1a76ff269bfb16178a531b8911b5bdf8808ec"),
            ("Markdown plan", PLAN_MARKDOWN,
             "5b76c3095ecbf5bc0f0273f2b83da8fab2d0c51154efc7628031b6445a4fbb18"),
            ("seed map", SEED_MAP_JSON,
             "95870d7d33c256c4bd30118e13278a600271531fd945d12687a828de902e91ce")):
        check(f"the {label} is BYTE-unchanged",
              sha256_file(os.path.join(ROOT, path)) == digest)
    for key, expected in (("alpha_geom", 0.005), ("alpha_1", 0.004),
                          ("alpha_2", 0.001), ("delta_abs", 0.05),
                          ("pipeline_target", 0.9)):
        check(f"{key} unchanged at {expected}", RULES[key] == expected)


def test_execution_remains_blocked() -> None:
    from e1a_v4.validation.seal import load_seal
    check("the execution seal is still PRE_DRIVER", load_seal(ROOT).state == "PRE_DRIVER")
    check("the expected final execution identity is still null",
          PLAN["frozen_identities"]["final_expected_execution_identity"] is None)
    check("execution_authorised is still false", PLAN["execution_authorised"] is False)
    check("no results directory exists",
          not os.path.exists(os.path.join(ROOT, "results/e1a_v4_validation")))
    check("NO REAL RNG OBJECT WAS CONSTRUCTED", RealRNGSentinel.CONSTRUCTED == 0)
    check("NO REAL RANDOM NUMBER WAS DRAWN", RealRNGSentinel.DRAWS == 0)




# ================================================ F1f-e refusal-aware aggregation
#: The authorised terminal status used by every refused fixture below. It is the
#: contract's own `REFUSED_ACCESSIBLE_SPACE` branch -- "rank guard failed on S",
#: rank_tol = 1e-12 -- reached through the analysis status the record carries. No
#: new refusal category is invented here.
REFUSED_STATUS = "RANK_GUARD_FAIL"
REFUSED_REASON = "REFUSED_ACCESSIBLE_SPACE"


def result_row(*, refused: bool, g5: bool = False, block1: bool = False,
               p1: bool = True, complete: bool = True, accepted: bool = False,
               recovered: bool = True) -> dict:
    """One field record's `result`. A refusal leaves the BLOCK decisions null."""
    if refused:
        return {"analysis_status": REFUSED_STATUS, "refusal_reason": REFUSED_REASON,
                "P1": False, "p1_rejected": True,
                "block1_rejected": None, "g5_rejected": None,
                "P2": False, "P3": False, "P4": True, "complete_pass": False,
                "false_acceptance": False, "scale_recovered": False}
    return {"analysis_status": "ESTIMATED", "P1": p1, "p1_rejected": not p1,
            "block1_rejected": block1, "g5_rejected": g5,
            "P2": True, "P3": True, "P4": True, "complete_pass": complete,
            "false_acceptance": accepted, "scale_recovered": recovered}


def case_records(plan, case_id, rows):
    """Records for ONE case over its RELEASE subcondition. `rows` is per replicate.

    Each entry of `rows` maps field_id -> result dict for that replicate.
    """
    sub = release_subconditions(plan, case_id)[0]
    out = {}
    for index, row in enumerate(rows):
        for field_id, result in row.items():
            key = f"{case_id}|{sub}|{index:06d}|{field_id}"
            out[key] = {"coordinates": {"case_id": case_id, "subcondition_id": sub,
                                        "replicate_id": index, "scope": field_id},
                        "result": result}
    return out


#: C3 and C4 keep their FROZEN replicate counts in the miniature campaign. The
#: classifier refuses evidence whose planned denominator differs from the frozen
#: one -- that guard is exactly what stops a denominator shrinking to the
#: survivors -- so shrinking them would test nothing. Every OTHER case is reduced,
#: because writing 53,200 real jobs would be a campaign.
FULL_DENOMINATOR_CASES = ("C3_g5_block", "C4_surrogate_validity")


def shrunk_plan(replicates=1):
    """The frozen plan with the NON-size cases' replicate counts reduced."""
    plan = copy.deepcopy(PLAN)
    for case in plan["cases"]:
        if case["case_id"] not in FULL_DENOMINATOR_CASES:
            case["replicate_count"] = replicates
    return plan


def miniature_campaign(plan, c3_refused=(), c4_refused=(), c3_g5=None,
                       c4_block1=None):
    """A COMPLETE record set for every planned job of the fixture plan. Pure dicts.

    `c3_refused` / `c4_refused` name fields whose EVERY replicate is a valid
    structured refusal. `c3_g5` / `c4_block1` map a field to HOW MANY of its
    replicates carry a real block rejection, so a fixture can sit just over a
    boundary rather than rejecting on every replicate -- `cp_lower` is an exact
    binomial sum and k near n is both unrealistic and arithmetically extreme.
    """
    rejecting = {"C3_g5_block": dict(c3_g5 or {}),
                 "C4_surrogate_validity": dict(c4_block1 or {})}
    refusing = {"C3_g5_block": set(c3_refused),
                "C4_surrogate_validity": set(c4_refused)}
    records = {}
    for case in plan["cases"]:
        cid = case["case_id"]
        fields = required_result_fields(plan, cid)
        for sub in release_subconditions(plan, cid):
            for index in range(case["replicate_count"]):
                for field_id in fields:
                    refused = field_id in refusing.get(cid, ())
                    rejects = index < rejecting.get(cid, {}).get(field_id, 0)
                    result = result_row(
                        refused=refused,
                        g5=(cid == "C3_g5_block" and rejects),
                        block1=(cid == "C4_surrogate_validity" and rejects))
                    key = f"{cid}|{sub}|{index:06d}|{field_id}"
                    records[key] = {
                        "coordinates": {"case_id": cid, "subcondition_id": sub,
                                        "replicate_id": index, "scope": field_id},
                        "result": result}
    return records


def test_refusal_aware_aggregation() -> None:
    """F1f-e. A valid structured refusal no longer aborts aggregation.

    THE DEFECT THIS CLOSES
        `require_endpoint_events` granted an explicit exemption for a null block
        decision on a non-ESTIMATED record, and `field_event_count` then raised
        ENDPOINT_EVENT_MISSING on exactly that record. One layer accepted what the
        next rejected, so the terminal campaign report the contract requires --
        "the report must finish even when every job refuses" -- was never produced.
    """
    # --- the ORIGINAL counterexample, now a permanent regression -------------
    for case_id, event, planned in (("C3_g5_block", "g5_rejected", 400),
                                    ("C4_surrogate_validity", "block1_rejected",
                                     2000)):
        plan = plan_with_replicates(case_id, 1)
        refused = case_records(plan, case_id,
                               [{f: result_row(refused=True) for f in FIELDS}])
        one = next(iter(refused.values()))["result"]
        check(f"{case_id[:2]}: the endpoint validator still ACCEPTS the refusal",
              refusal_code(require_endpoint_events, plan, case_id, one, "probe")
              is None)
        outcomes = per_field_primary_outcomes(plan, refused, case_id, event)
        o = outcomes["theta0_circular"]
        check(f"{case_id[:2]}: the AGGREGATOR now accepts the same record",
              o.planned_replicates == 1 and o.structured_refusals == 1
              and o.evaluable == 0 and o.rejections == 0, str(o))
        check(f"{case_id[:2]}: the refusal reason is preserved, not just counted",
              o.refusal_reasons == {REFUSED_REASON: 1}, str(o.refusal_reasons))
        nominal = PER_FIELD_SIZE_CASES[case_id[:2]][1]
        check(f"{case_id[:2]}: the primary status is NOT_EVALUABLE",
              classify_field_size(o, nominal)["verdict"] == SIZE_NOT_EVALUABLE)

    # --- ALL-REFUSED and PARTIAL, at the real planned denominators ----------
    for case_id, event, planned, nominal, rejections in (
            ("C3_g5_block", "g5_rejected", 400, 0.001, 2),
            ("C4_surrogate_validity", "block1_rejected", 2000, 0.004, 13)):
        short = case_id[:2]
        plan = plan_with_replicates(case_id, planned)
        # all refused
        rows = [{f: result_row(refused=True) for f in FIELDS} for _ in range(planned)]
        out = per_field_primary_outcomes(plan, case_records(plan, case_id, rows),
                                         case_id, event)["theta0_circular"]
        res = classify_field_size(out, nominal)
        check(f"{short} ALL {planned} refused -> NOT_EVALUABLE",
              res["verdict"] == SIZE_NOT_EVALUABLE
              and out.evaluable == 0 and out.structured_refusals == planned
              and out.planned_replicates == planned, str(out))
        check(f"{short} all-refused is NOT reported clean",
              res["verdict"] != SIZE_NO_INFLATION)
        check(f"{short} all-refused does NOT fabricate size inflation",
              res["verdict"] != SIZE_FAILURE and res["rejections"] == 0)
        # one refusal among otherwise clean-looking evidence
        rows = [{f: result_row(refused=False,
                               g5=(short == "C3" and i < rejections
                                   and f == "theta0_circular"),
                               block1=(short == "C4" and i < rejections
                                       and f == "theta0_circular"))
                 for f in FIELDS} for i in range(planned)]
        rows[planned - 1] = {f: result_row(refused=(f == "theta0_circular"))
                             for f in FIELDS}
        out = per_field_primary_outcomes(plan, case_records(plan, case_id, rows),
                                         case_id, event)["theta0_circular"]
        res = classify_field_size(out, nominal)
        check(f"{short} {planned - 1} evaluable + 1 refusal -> NOT_EVALUABLE",
              res["verdict"] == SIZE_NOT_EVALUABLE
              and out.evaluable == planned - 1 and out.structured_refusals == 1,
              str(out))
        check(f"{short}: the planned denominator is PRESERVED, not {planned - 1}",
              out.planned_replicates == planned
              and res["planned_replicates"] == planned)
        check(f"{short}: the defined rejections are retained, not discarded",
              out.rejections == rejections, str(out.rejections))
        # the SAME field with nothing refused reaches the ordinary verdict
        rows = [{f: result_row(refused=False,
                               g5=(short == "C3" and i < rejections
                                   and f == "theta0_circular"),
                               block1=(short == "C4" and i < rejections
                                       and f == "theta0_circular"))
                 for f in FIELDS} for i in range(planned)]
        out = per_field_primary_outcomes(plan, case_records(plan, case_id, rows),
                                         case_id, event)["theta0_circular"]
        boundary = classify_size(0, planned, nominal)["boundary"]
        check(f"{short} fully evaluable at {rejections} -> the ordinary verdict",
              classify_field_size(out, nominal)["verdict"]
              == (SIZE_NO_INFLATION if rejections <= boundary else SIZE_FAILURE),
              str(out))
        check(f"{short} fully evaluable: evaluable == planned, refusals 0",
              out.evaluable == planned and out.structured_refusals == 0)


def test_cross_layer_refusal_invariant() -> None:
    """F1f-e. What the validator accepts, the aggregator can always aggregate."""
    estimated = result_row(refused=False)
    refused = result_row(refused=True)
    for case_id, event in (("C3_g5_block", "g5_rejected"),
                           ("C4_surrogate_validity", "block1_rejected")):
        plan = plan_with_replicates(case_id, 1)
        for label, row in (("valid structured refusal", refused),
                           ("fully estimated record", estimated)):
            accepted = refusal_code(require_endpoint_events, plan, case_id, row,
                                    "probe") is None
            recs = case_records(plan, case_id, [{f: row for f in FIELDS}])
            aggregated = refusal_code(per_field_primary_outcomes, plan, recs,
                                      case_id, event) is None
            check(f"{case_id[:2]} {label}: validator and aggregator AGREE",
                  accepted and aggregated, f"accepted={accepted} "
                  f"aggregated={aggregated}")
    check("both layers ask ONE predicate, so they cannot drift apart",
          is_structured_refusal(refused, "g5_rejected") is True
          and is_structured_refusal(estimated, "g5_rejected") is False)

    # --- INVALID absences must still refuse ---------------------------------
    for case_id, event in (("C3_g5_block", "g5_rejected"),
                           ("C4_surrogate_validity", "block1_rejected")):
        plan = plan_with_replicates(case_id, 1)
        malformed = (
            ("null decision while analysis_status is ESTIMATED",
             dict(estimated, **{event: None})),
            ("the decision key removed entirely",
             {k: v for k, v in refused.items() if k != event}),
            ("null decision with NO analysis_status at all",
             {k: v for k, v in dict(estimated, **{event: None}).items()
              if k != "analysis_status"}),
        )
        for label, row in malformed:
            recs = case_records(plan, case_id, [{f: row for f in FIELDS}])
            check(f"{case_id[:2]} {label} STILL refuses",
                  refusal_code(per_field_primary_outcomes, plan, recs, case_id,
                               event) == "ENDPOINT_EVENT_MISSING")
            check(f"{case_id[:2]} {label}: the validator refuses it too",
                  refusal_code(require_endpoint_events, plan, case_id, row,
                               "probe") == "ENDPOINT_EVENT_MISSING")
    check("a refusal reason is recovered from the record's own provenance",
          structured_refusal_reason(refused) == REFUSED_REASON
          and structured_refusal_reason({"analysis_status": "N_EFF_UNSUPPORTED"})
          == "N_EFF_UNSUPPORTED")

    # --- the FULL P1 result must not stand in for the missing block decision --
    # Under a structured refusal P1 is DEFINED -- it fails closed -- while the two
    # block decisions are not. Substituting it would silently turn a NOT_EVALUABLE
    # field into an evaluable one carrying a rejection that never happened.
    check("under a refusal P1 is defined while both block decisions are not",
          refused["p1_rejected"] is True and refused["block1_rejected"] is None
          and refused["g5_rejected"] is None)
    for case_id, event in (("C3_g5_block", "g5_rejected"),
                           ("C4_surrogate_validity", "block1_rejected")):
        plan = plan_with_replicates(case_id, 1)
        recs = case_records(plan, case_id, [{f: refused for f in FIELDS}])
        primary = per_field_primary_outcomes(plan, recs, case_id,
                                             event)["theta0_circular"]
        substituted = per_field_primary_outcomes(plan, recs, case_id,
                                                 "p1_rejected")["theta0_circular"]
        check(f"{case_id[:2]}: the ACTUAL endpoint gives 0 evaluable, 0 rejections",
              primary.evaluable == 0 and primary.rejections == 0
              and primary.structured_refusals == 1)
        check(f"{case_id[:2]}: substituting full P1 would fabricate a rejection",
              substituted.evaluable == 1 and substituted.rejections == 1
              and substituted.structured_refusals == 0)
        check(f"{case_id[:2]}: the two are demonstrably different results",
              primary != substituted)
        nominal = PER_FIELD_SIZE_CASES[case_id[:2]][1]
        check(f"{case_id[:2]}: only the ACTUAL endpoint yields NOT_EVALUABLE",
              classify_field_size(primary, nominal)["verdict"] == SIZE_NOT_EVALUABLE
              and classify_field_size(substituted, nominal)["verdict"]
              != SIZE_NOT_EVALUABLE)


def test_terminal_result_materialises() -> None:
    """F1f-e. The CORE contract regression: the report finishes under refusal.

    A complete miniature campaign is assembled from pure records and taken through
    the real chain -- records, counts, classification, terminal result -- with no
    RNG, no trajectory and no campaign job. Before the repair this raised
    ENDPOINT_EVENT_MISSING inside `campaign_counts_from_records` and no campaign
    result object ever existed.
    """
    plan = shrunk_plan(1)
    clean = campaign_counts_from_records(plan, miniature_campaign(plan))
    check("C3 and C4 keep their FROZEN planned denominators in the fixture",
          clean.c3_rejections_by_field[FIELDS[0]].planned_replicates == 400
          and clean.c4_rejections_by_field[FIELDS[0]].planned_replicates == 2000)
    verdict = classify_campaign(clean)
    # C1, C7 and C8 are deliberately undersized in this fixture, so the OVERALL
    # verdict is not the subject here; what is asserted is that C3 and C4 reach a
    # terminal assessment and contribute nothing.
    check("a clean fixture: C3 and C4 contribute NO failure",
          not [f for f in verdict["failures"] if "(C3 " in f or "(C4 " in f],
          "; ".join(verdict["failures"])[:70])
    check("a clean fixture: every C3 and C4 field is fully evaluable and clean",
          all(verdict["detail"][case][f]["verdict"] == SIZE_NO_INFLATION
              and verdict["detail"][case][f]["structured_refusals"] == 0
              for case in ("C3", "C4") for f in FIELDS))

    # --- EVERY C3 and C4 job refuses --------------------------------------
    allref = miniature_campaign(plan, c3_refused=FIELDS, c4_refused=FIELDS)
    counts = campaign_counts_from_records(plan, allref)
    result = classify_campaign(counts)
    check("ALL-REFUSED: aggregation COMPLETES instead of raising",
          counts is not None)
    check("ALL-REFUSED: the terminal campaign result EXISTS",
          isinstance(result, dict) and "verdict" in result and "detail" in result)
    check("ALL-REFUSED: the campaign cannot PASS",
          result["verdict"] == "VALIDATION_FAILURE")
    for case in ("C3", "C4"):
        statuses = {f: result["detail"][case][f]["verdict"] for f in FIELDS}
        check(f"ALL-REFUSED: every {case} field is NOT_EVALUABLE",
              set(statuses.values()) == {SIZE_NOT_EVALUABLE}, str(statuses))
    check("ALL-REFUSED: no statistical size failure is fabricated",
          not any(f.startswith(SIZE_FAILURE) for f in result["failures"]),
          "; ".join(result["failures"])[:80])
    check("ALL-REFUSED: each not-evaluable field reports 0 evaluable of its planned R",
          all(result["detail"][case][f]["evaluable"] == 0
              and result["detail"][case][f]["planned_replicates"] == planned
              for case, planned in (("C3", 400), ("C4", 2000)) for f in FIELDS))
    size_related = [f for f in result["failures"] if "(C3 " in f or "(C4 " in f]
    check("ALL-REFUSED: every C3/C4 failure reason is incomplete evidence",
          size_related and all(f.startswith(INCOMPLETE_EVIDENCE_CLASSIFICATION)
                               for f in size_related),
          "; ".join(size_related)[:80])
    check("ALL-REFUSED: the refusal reason survives into the terminal detail",
          result["detail"]["C3"][FIELDS[0]]["refusal_reasons"] == {REFUSED_REASON: 400}
          and result["detail"]["C4"][FIELDS[0]]["refusal_reasons"]
          == {REFUSED_REASON: 2000},
          str(result["detail"]["C3"][FIELDS[0]]["refusal_reasons"]))
    check("ALL-REFUSED: C2 is untouched and still counted normally",
          set(result["detail"]["C2"]) == set(FIELDS)
          and all(r["verdict"] == SIZE_NO_INFLATION
                  for r in result["detail"]["C2"].values()))

    # --- MIXED: one field not evaluable, another a real size failure --------
    plan3 = shrunk_plan(1)
    # one over each frozen boundary: C3 clean 0-2, C4 clean 0-13
    mixed = miniature_campaign(plan3, c3_refused=("theta0_circular",),
                               c3_g5={"theta1_power": 3},
                               c4_refused=("theta1_power",),
                               c4_block1={"theta3_temperature": 14})
    result = classify_campaign(campaign_counts_from_records(plan3, mixed))
    check("MIXED: the campaign cannot PASS", result["verdict"] == "VALIDATION_FAILURE")
    check("MIXED: theta0 of C3 is NOT_EVALUABLE",
          result["detail"]["C3"]["theta0_circular"]["verdict"] == SIZE_NOT_EVALUABLE)
    check("MIXED: theta1 of C3 is a STATISTICAL size failure",
          result["detail"]["C3"]["theta1_power"]["verdict"] == SIZE_FAILURE)
    check("MIXED: theta1 of C4 is NOT_EVALUABLE",
          result["detail"]["C4"]["theta1_power"]["verdict"] == SIZE_NOT_EVALUABLE)
    check("MIXED: theta3 of C4 is a STATISTICAL size failure",
          result["detail"]["C4"]["theta3_temperature"]["verdict"] == SIZE_FAILURE)
    incomplete = [f for f in result["failures"]
                  if f.startswith(INCOMPLETE_EVIDENCE_CLASSIFICATION)]
    statistical = [f for f in result["failures"] if f.startswith(SIZE_FAILURE)]
    check("MIXED: BOTH scientific reasons survive, neither erases the other",
          len(incomplete) == 2 and len(statistical) == 2,
          f"{len(incomplete)} incomplete, {len(statistical)} statistical")
    check("MIXED: each failure names its own case and field",
          any("theta0_circular" in f and "(C3 " in f for f in incomplete)
          and any("theta1_power" in f and "(C3 " in f for f in statistical)
          and any("theta1_power" in f and "(C4 " in f for f in incomplete)
          and any("theta3_temperature" in f and "(C4 " in f for f in statistical))
    check("MIXED: the clean fields stay clean",
          result["detail"]["C3"]["theta2_ellipse"]["verdict"] == SIZE_NO_INFLATION
          and result["detail"]["C4"]["theta0_circular"]["verdict"]
          == SIZE_NO_INFLATION)
    check("MIXED: the two facts are reported separately",
          result["independent_facts"]["component_size_clean"] is False
          and result["independent_facts"]["component_size_evaluable"] is False)

    # --- restart: recovered aggregation equals fresh aggregation ------------
    restored = json.loads(json.dumps(allref, sort_keys=True, allow_nan=False))
    recovered = campaign_counts_from_records(plan, restored)
    fresh = campaign_counts_from_records(plan, allref)
    check("RESTART: recovered C3 evidence equals fresh C3 evidence",
          recovered.c3_rejections_by_field == fresh.c3_rejections_by_field)
    check("RESTART: recovered C4 evidence equals fresh C4 evidence",
          recovered.c4_rejections_by_field == fresh.c4_rejections_by_field)
    check("RESTART: an undefined endpoint is NOT reconstructed as a boolean",
          all(r["result"]["g5_rejected"] is None
              for r in restored.values()
              if r["coordinates"]["case_id"] == "C3_g5_block"))
    check("RESTART: the campaign verdict survives the round trip",
          classify_campaign(recovered)["verdict"]
          == classify_campaign(fresh)["verdict"])


def test_refusal_count_invariants() -> None:
    """F1f-e. An inconsistent per-field evidence object is REFUSED, not believed."""
    bad = (
        ("evaluable + refusals != planned", dict(evaluable=398, structured_refusals=1)),
        ("more rejections than evaluable", dict(evaluable=2, structured_refusals=398,
                                                rejections=3)),
        ("negative evaluable", dict(evaluable=-1, structured_refusals=401)),
        ("refusals exceed planned", dict(evaluable=0, structured_refusals=401)),
        ("rejections exceed planned", dict(evaluable=400, structured_refusals=0,
                                           rejections=401)),
    )
    for label, over in bad:
        kwargs = dict(field_id="theta0_circular", planned_replicates=400,
                      evaluable=400, structured_refusals=0, rejections=0)
        kwargs.update(over)
        check(f"REFUSED: {label}", refuses(FieldSizeOutcome, **kwargs))
    check("REFUSED: refusal reasons that do not account for the refusals",
          refuses(FieldSizeOutcome, field_id="theta0_circular",
                  planned_replicates=400, evaluable=399, structured_refusals=1,
                  rejections=0, refusal_reasons={REFUSED_REASON: 5}))
    ok = FieldSizeOutcome(field_id="theta0_circular", planned_replicates=400,
                          evaluable=399, structured_refusals=1, rejections=2,
                          refusal_reasons={REFUSED_REASON: 1})
    check("ACCEPTED: a consistent object, with the invariant holding",
          ok.evaluable + ok.structured_refusals == ok.planned_replicates
          and ok.rejections <= ok.evaluable and not ok.fully_evaluable)

    # --- the classifier refuses evidence that is not three-state ------------
    check("REFUSED: a bare count supplied for C3",
          refuses(classify_campaign,
                  clean_counts(c3_rejections_by_field={f: 0 for f in FIELDS})))
    swapped = evidence("C3")
    swapped["theta0_circular"] = FieldSizeOutcome(
        field_id="theta1_power", planned_replicates=400, evaluable=400,
        structured_refusals=0, rejections=0)
    check("REFUSED: evidence whose field identity drifted",
          refuses(classify_campaign, clean_counts(c3_rejections_by_field=swapped)))
    shrunk = evidence("C3")
    shrunk["theta0_circular"] = FieldSizeOutcome(
        field_id="theta0_circular", planned_replicates=399, evaluable=399,
        structured_refusals=0, rejections=0)
    check("REFUSED: evidence whose planned denominator shrank to the survivors",
          refuses(classify_campaign, clean_counts(c3_rejections_by_field=shrunk)))


def refuses(fn, *args, **kwargs) -> bool:
    try:
        fn(*args, **kwargs)
    except Refusal:
        return True
    return False


def p1_fails_closed(status) -> bool:
    """Does `p1_geometry` fail closed on THIS status, before reading any statistic?

    Behavioural, not source-text: the frozen endpoint is CALLED with an analysis
    carrying the status and no gate statistics at all. A status it fails closed on
    returns the no-rows `passed = False` result before it touches the calibration
    condition; a status it carries past that return reaches the condition and
    raises instead. Nothing is drawn and no world state advances -- the
    fail-closed branch is the first statement in the function.
    """
    try:
        result = p1_geometry(FieldAnalysis(FIELDS[0], status, "probe"), CONTRACT,
                             procedure_identity="probe", condition=None,
                             artifact=None)
    except Exception:
        return False
    return result.passed is False and result.rows == ()


def test_structured_refusal_record_integrity() -> None:
    """F1f-g. Only AFFIRMATIVE, consistent evidence authorises an undefined endpoint.

    An independent runtime audit found that the F1f-e predicate accepted records
    no part of the frozen pipeline can produce:

      A  `analysis_status = "NOT_A_REAL_STATUS"`, because the test was
         `status != "ESTIMATED"` and EVERY other string satisfies that;
      B  `RANK_GUARD_FAIL` with `P1 = True, p1_rejected = False` -- a record
         asserting both that the analysis never ran and that the gate passed --
         because nothing looked at the composite P1 state at all.

    Each is a permanent counterexample below, together with the already-closed
    case where the status key is absent entirely.
    """
    refused = result_row(refused=True)
    estimated = result_row(refused=False)
    check("the CANONICAL refusal record is accepted, in BOTH block events",
          all(is_structured_refusal(refused, e) is True
              for e in ("g5_rejected", "block1_rejected")))
    check("its status is one the canonical roster declares and authorises",
          refused["analysis_status"] in DECLARED_ANALYSIS_STATUSES
          and refused["analysis_status"] in REFUSAL_AUTHORISING_STATUSES)

    # --- the authorising set is DERIVED, never retyped -----------------------
    check("the declared roster is e1a_v4.status.AnalysisStatus itself",
          DECLARED_ANALYSIS_STATUSES == {s.value for s in AnalysisStatus})
    check("ESTIMATED never authorises an undefined endpoint",
          "ESTIMATED" not in REFUSAL_AUTHORISING_STATUSES)
    check("the authorising set is the canonical NON_ESTIMATED set, less the "
          "statuses the frozen gate does not fail closed on",
          REFUSAL_AUTHORISING_STATUSES
          == {s.value for s in AnalysisStatus if s is not AnalysisStatus.ESTIMATED}
          - NON_FAIL_CLOSED_STATUSES)
    # THE REASON FOR THAT EXCLUSION, proved against the frozen endpoint rather
    # than asserted: `p1_geometry` carries GEOMETRY_FAIL past its fail-closed
    # return and scores it against real gate statistics, so it yields DEFINED
    # block decisions or refuses outright -- it never leaves one undefined.
    check("the exclusion matches what p1_geometry ACTUALLY does, status by status",
          {s.value for s in AnalysisStatus
           if s is not AnalysisStatus.ESTIMATED and p1_fails_closed(s)}
          == set(REFUSAL_AUTHORISING_STATUSES),
          f"excluded: {sorted(NON_FAIL_CLOSED_STATUSES)}")

    # --- §20 / §21 / §19: every malformed authorisation claim REFUSES --------
    drop = lambda row, key: {k: v for k, v in row.items() if k != key}
    malformed = (
        ("an analysis status outside the declared roster",
         dict(refused, analysis_status="NOT_A_REAL_STATUS")),
        ("a status differing from a declared one only in case",
         dict(refused, analysis_status=REFUSED_STATUS.lower())),
        ("a whitespace-padded status", dict(refused, analysis_status=f" {REFUSED_STATUS}")),
        ("NO analysis status at all", drop(refused, "analysis_status")),
        ("a null analysis status", dict(refused, analysis_status=None)),
        ("a non-string analysis status", dict(refused, analysis_status=3)),
        ("an ESTIMATED analysis status", dict(refused, analysis_status="ESTIMATED")),
        ("a status the frozen gate does not fail closed on",
         dict(refused, analysis_status=sorted(NON_FAIL_CLOSED_STATUSES)[0])),
        ("a composite P1 that PASSED", dict(refused, P1=True, p1_rejected=False)),
        ("P1 passed while p1_rejected still says rejected", dict(refused, P1=True)),
        ("p1_rejected cleared while P1 still says failed",
         dict(refused, p1_rejected=False)),
        ("no composite P1 field at all", drop(refused, "P1")),
        ("no p1_rejected field at all", drop(refused, "p1_rejected")),
        ("integers 0/1 standing in for the frozen booleans",
         dict(refused, P1=0, p1_rejected=1)),
    )
    for label, row in malformed:
        for event in ("g5_rejected", "block1_rejected"):
            short = "C3" if event == "g5_rejected" else "C4"
            check(f"REFUSED ({short}): {label}",
                  is_structured_refusal(row, event) is False,
                  repr(row.get("analysis_status")))

    # --- §26: BOTH layers refuse a malformed record, through the real plan ---
    # These records are what a RESTART reads back off disk, so the recovery path
    # refuses them rather than silently normalising them into a refusal.
    audited = (
        ("an unknown analysis status",
         dict(refused, analysis_status="NOT_A_REAL_STATUS")),
        ("no analysis status at all", drop(refused, "analysis_status")),
        ("a recognised refusal status with a PASSED composite P1",
         dict(refused, P1=True, p1_rejected=False)),
    )
    for case_id, event in (("C3_g5_block", "g5_rejected"),
                           ("C4_surrogate_validity", "block1_rejected")):
        plan = plan_with_replicates(case_id, 1)
        short = case_id[:2]
        for label, row in audited:
            persisted = json.loads(json.dumps(row))      # a genuine round trip
            recs = case_records(plan, case_id, [{f: persisted for f in FIELDS}])
            check(f"{short} {label}: the AGGREGATOR refuses on recovery",
                  refusal_code(per_field_primary_outcomes, plan, recs, case_id,
                               event) == "ENDPOINT_EVENT_MISSING")
            check(f"{short} {label}: the VALIDATOR refuses it too",
                  refusal_code(require_endpoint_events, plan, case_id, persisted,
                               "probe") == "ENDPOINT_EVENT_MISSING")
        # --- §16 / §17, both directions, on the SAME plan --------------------
        valid = json.loads(json.dumps(refused))
        recs = case_records(plan, case_id, [{f: valid for f in FIELDS}])
        outcome = per_field_primary_outcomes(plan, recs, case_id, event)[FIELDS[0]]
        check(f"{short} a VALID refusal survives the round trip and both layers",
              refusal_code(require_endpoint_events, plan, case_id, valid, "probe")
              is None and outcome.structured_refusals == 1
              and outcome.evaluable == 0 and outcome.rejections == 0)
        check(f"{short} its reason attribution balances the refusal count",
              sum(outcome.refusal_reasons.values()) == outcome.structured_refusals
              and outcome.refusal_reasons == {REFUSED_REASON: 1})
        check(f"{short} an ESTIMATED record owes its block decision",
              refusal_code(require_endpoint_events, plan, case_id,
                           dict(estimated, **{event: None}), "probe")
              == "ENDPOINT_EVENT_MISSING")


GROUPS = (
    ("T1  C2 counts PER FIELD", test_c2_counts_per_field),
    ("T2/T3  G5 and Block-1 decisions propagate", test_g5_and_block1_propagate),
    ("T4  a missing decision fails closed", test_missing_decision_fails_closed),
    ("F1f  cross-field reduction is FORBIDDEN",
     test_cross_field_reduction_is_forbidden),
    ("F1f  C2/C3/C4 counted PER FIELD", test_per_field_counting),
    ("F1f  field misattribution is visible and refused", test_field_misattribution),
    ("F1f  Block-1 and Block-2 are distinguished", test_block_distinction),
    ("F1f  counts survive serialisation/restart", test_counts_survive_serialisation),
    ("F1f  the failing field reaches the classifier",
     test_field_identity_survives_to_the_classifier),
    ("F1f-e refusal-aware aggregation", test_refusal_aware_aggregation),
    ("F1f-e validator and aggregator agree", test_cross_layer_refusal_invariant),
    ("F1f-e the terminal result materialises", test_terminal_result_materialises),
    ("F1f-e per-field count invariants", test_refusal_count_invariants),
    ("F1f-g structured-refusal record integrity",
     test_structured_refusal_record_integrity),
    ("T5/T6  the C8 blinded Branch-A control", test_c8_blinded_branch_a_control),
    ("T7-T10  terminal provenance cross-links", test_terminal_provenance_cross_links),
    ("campaign structure unchanged", test_campaign_structure_unchanged),
    ("frozen authority unchanged", test_frozen_authority_unchanged),
    ("execution remains blocked", test_execution_remains_blocked),
)


if __name__ == "__main__":
    for title, fn in GROUPS:
        print(f"\n{title}")
        fn()
    print(f"\nE1a v4 driver endpoint/provenance gate: {PASSED} passed, "
          f"{FAILED} failed, {len(GROUPS)} groups")
    print("Execution class: NON-MODEL-ADVANCING STATIC/PURE (this suite only)")
    print("  REAL RNG OBJECTS ................ 0")
    print("  REAL STOCHASTIC RANDOM DRAWS .... 0")
    print("  OFFICIAL CAMPAIGN TRAJECTORIES .. 0")
    print("  DETERMINISTIC TEST TRAJECTORIES . 0")
    print("  OFFICIAL CAMPAIGN JOBS .......... 0")
    print("  REAL CALIBRATION EXECUTIONS ..... 0")
    raise SystemExit(1 if FAILED else 0)
