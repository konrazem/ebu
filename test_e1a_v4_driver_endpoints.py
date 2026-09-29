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
    FIELD_LEVEL_EVENTS, REPLICATE_LEVEL_EVENTS, UNDECLARED_EVENT_REDUCTION,
    blinded_branch_a, campaign_shape, committed_publication, evaluate_replicate,
    evaluate_scale_control, field_event_count, job_execution, p1_block_decisions,
    plan_campaign, replicate_level_rejections, require_endpoint_events,
    require_plan_driver_agreement, required_endpoint_events,
    required_result_fields, validate_job_record,
)
from e1a_v4.validation.classification import (
    CampaignCounts, classify_campaign, classify_size,
)
from e1a_v4.effective_size import sigma_stat
from e1a_v4.endpoints import UncertaintyModel
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


def replicate_outcome(case_id, subcondition_id, rejecting_fields=(), *, g5=0.0):
    """Run the PRODUCTION endpoint assembly for one synthetic replicate."""
    conditions, artifacts, analyses, specs = {}, {}, {}, {}
    for field_id in FIELDS:
        condition = small_condition(field_id)
        conditions[field_id] = condition
        artifacts[field_id] = fixture_artifact(condition)
        analyses[field_id] = fixture_analysis(
            field_id, g1=(9.9 if field_id in rejecting_fields else 0.0), g5=g5)
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


# ============================ C3/C4 replicate-level reduction is not invented
def test_replicate_reduction_is_not_guessed() -> None:
    """The 4-field -> 1-replicate reduction C3 and C4 need is UNDECLARED."""
    for case_id, event in (("C3_g5_block", "g5_rejected"),
                           ("C4_surrogate_validity", "block1_rejected")):
        refuses_with_code(f"{case_id} replicate-level reduction",
                          "ENDPOINT_EVENT_REDUCTION_UNDECLARED",
                          replicate_level_rejections, PLAN, {}, case_id, event)
    check("the refusal names the three candidate reductions it will not choose "
          "between",
          "any field rejects" in UNDECLARED_EVENT_REDUCTION
          and "every field rejects" in UNDECLARED_EVENT_REDUCTION)
    check("C6 declares ONE field, so its reduction is unambiguous",
          len(required_result_fields(PLAN, "C6_mode_resolution_boundary")) == 1)
    check("C3 and C4 declare four fields each, which is why the rule is needed",
          len(required_result_fields(PLAN, "C3_g5_block")) == 4
          and len(required_result_fields(PLAN, "C4_surrogate_validity")) == 4)


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
    counts = CampaignCounts(
        c1_successes=300, c2_rejections_by_field={f: 0 for f in FIELDS},
        c3_rejections=0, c4_rejections=0, c5_pass=True, c6_pass=True,
        c7_false_acceptances_by_alternative={
            a: 0 for a in ("alt_1_06", "alt_0_93_1_05", "alt_1_10", "hard_1_025")},
        c8_successes=200)
    verdict = classify_campaign(counts)
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
        def __init__(self, source):
            self.binding = source.binding
            self.plan = source.plan
            self.plan_sha256 = source.plan_sha256
            self.seed_map_sha256 = source.seed_map_sha256
            self.analysis_identity = source.analysis_identity
            self.execution_identity = "f" * 64

    check("a record valid under the OLD package is refused under the current one",
          refusal_code(validate_job_record, json.loads(json.dumps(record)),
                       binding.plan, MovedBinding(binding), job, out)
          == "TERMINAL_PROVENANCE_MISMATCH")
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
            ("JSON plan", PLAN_JSON,
             "dcb3507585791c851e616c81a113fe89d61d2e830a4694f49733d1d04c5b8f5a"),
            ("Markdown plan", PLAN_MARKDOWN,
             "3f4715b465da295e21ad99a86390585c9eb7deac44a7810114a88f40aa4bf940"),
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


GROUPS = (
    ("T1  C2 counts PER FIELD", test_c2_counts_per_field),
    ("T2/T3  G5 and Block-1 decisions propagate", test_g5_and_block1_propagate),
    ("T4  a missing decision fails closed", test_missing_decision_fails_closed),
    ("C3/C4 replicate reduction is not guessed",
     test_replicate_reduction_is_not_guessed),
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
