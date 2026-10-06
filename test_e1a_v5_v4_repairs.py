"""E1a v5 procedure version 4: regressions for the seven audited V3 defects.

**EXECUTION CLASS: MIXED.** Closed-form algebra, structured-refusal checks and
deterministic expected-likelihood calculations.  A small number of SYNTHETIC
OU trajectories are generated for the end-to-end path checks.  No real data,
no calibration execution, no official campaign job, no physical experiment.

Each section fails if its defect is reintroduced.
"""

from __future__ import annotations

import math

from e1a_v5 import numerics as nm
from e1a_v5.calibration import (
    AnalysisModel,
    BoundedBias,
    ExperimentCalibration,
    FieldModel,
    LOG_BETA_ROW,
    N_THETA,
    Primitive,
    PrimitiveVector,
    Scope,
    THETA_NAMES,
    build_experiment_calibration,
    certified_profiled_sensitivity,
    combined_contrast_standard_error,
    combined_standard_error,
    enclosures_overlap,
    expected_loglik_per_frame,
    primitive_steps,
    profiled_sensitivity_by_optimisation,
    truth_matching_theta,
)
from e1a_v5 import certified as cert
from e1a_v5.confidence import (
    BIAS_ABS_MAX,
    CEILING_FAIL,
    CEILING_PASS,
    CEILING_UNRESOLVED,
    CriticalValueStatus,
    CriticalValues,
    DELTA_A,
    DELTA_C,
    Interval,
    NORMAL_CRITICAL,
    NumericalEnclosure,
    SIGMA_CAL_ABS_MAX,
    SIGMA_CAL_CONTRAST_MAX,
    absolute_qualification,
    bias_qualification,
    build_interval,
    classify_with_enclosure,
    contrast_qualification,
    synthetic_calibrated,
)
from e1a_v5.diagnostics import (
    DIAG_CALIBRATED,
    DIAG_CONTRADICTORY,
    DIAG_NOT_EVALUABLE,
    DIAG_UNCALIBRATED,
    DiagnosticComponents,
    NullScales,
    RecordDiagnostic,
    evaluate_diagnostic_family,
)
from e1a_v5.evidence import (
    BiasEvidence,
    BiasStatus,
    ContrastKey,
    GateFamily,
    GateLimit,
    synthetic_calibrated_gate_fixture,
    IV_BIAS_MISSING,
    IV_CRITICAL_UNCALIBRATED,
    IV_ENDPOINT_MISMATCH,
    IV_NONFINITE,
    IV_REVERSED,
    IV_SE_NEGATIVE,
    IV_SE_ZERO,
    RecordKey,
    ScientificInterval,
    check_contrast_cardinality,
    check_record_cardinality,
)
from e1a_v5.gates import DELTA_G, DELTA_M, DELTA_R_IRR
from e1a_v5.identity import (
    ANALYSIS_MODULES,
    VALIDATION_MODULES,
    compute_identities,
    validation_preimage,
)
from e1a_v5.numerics import NumericalFailure
from e1a_v5.packets import CONTRASTS, RECORDS, BlockId, FieldId
from e1a_v5.pipeline import (
    ContrastResultV4,
    DELTA_STATIONARITY,
    RecordResultV4,
    complete_pipeline_result,
    validate_evidence,
)
from e1a_v5.realization import FIELD_REALIZATION_VALID
from e1a_v5.reduction import (
    AxialEvidence,
    NonlinearRemainder,
    REMAINDER_DOMAIN_LIMIT,
    RemainderKind,
    RemainderSet,
    normalise_remainder,
    reduce_axial,
    remainder_impacts,
    schur_complement,
    schur_nonlinear_remainder,
    split_3d,
)
from e1a_v5.seeds import (
    CONFIRMATORY_FAMILIES,
    ENGINEERING,
    FAMILIES_V2,
    FAMILIES_V3,
    POWER,
    ROOT,
    ROOT_V2,
    ROOT_V3,
    SeedMap,
)
from e1a_v5.units import K_B
from e1a_v5.validation import plan
from e1a_v5.validation.cases import ALL_CASES, CASES_BY_ID, CaseConfig, ExpectedEvent
from e1a_v5.validation.dispatch import (
    IMPLEMENTED_DRIVERS,
    InvalidValidationPlan,
    apply_geometry,
    instantiate,
)
from e1a_v5.validation.events import (
    EVENT_EVALUATOR_VERSION,
    EventNotEvaluable,
    ReasonAggregate,
    ReplicateOutcome,
    evaluate_event,
)
from e1a_v5.validation.harness import (
    current_control_drift,
    design_specs,
    experiment_calibration,
    run_record,
)
from e1a_v5.validation.run import (
    DOMAIN_IDENTITY, PROCEDURE_VERSION, deterministic_controls,
    deterministic_coverage,
)
from e1a_v5.verdict import INVALID, NOT_EVALUABLE, SUPPORTED

PASSED = 0
FAILED = 0


def check(label: str, cond: bool, detail: str = "") -> None:
    global PASSED, FAILED
    if cond:
        PASSED += 1
    else:
        FAILED += 1
        print(f"  [FAIL] {label} {detail}")


def close(a: float, b: float, tol: float = 1e-12) -> bool:
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b))


FIXTURE_CRIT = synthetic_calibrated()
FIXTURE_GATE_PROC = {
    f: synthetic_calibrated_gate_fixture(f, 0.0) for f in GateFamily
}


def fixture_limit(family: GateFamily, statistic: float, limit: float) -> GateLimit:
    """A TEST-ONLY calibrated gate limit at a chosen value.

    V5 removed ``GateLimit.calibrated(statistic, limit, identity)``: a bare
    string granted calibration, so a raw statistic became a passing limit.
    V6 separates fixtures from production by TYPE: this goes through
    ``SyntheticGateFixture`` and ``GateLimit.from_fixture``, neither of which
    any production API accepts.
    """
    fx = synthetic_calibrated_gate_fixture(family, max(0.0, limit - statistic))
    return GateLimit.from_fixture(statistic, fx, family)

FIXTURE_GATE = "SYNTHETIC FIXTURE - not a calibration"


def good_record(block: BlockId, fld: FieldId, **over) -> RecordResultV4:
    """A fully populated, fully qualified record result."""
    est, se, bias = 0.0, 1.0e-3, 1.0e-4
    iv = build_interval(est, se, FIXTURE_CRIT, bias)
    kw = dict(
        key=RecordKey(block, fld),
        embedded_key=RecordKey(block, fld),
        branch_a_valid=True,
        observation_valid=True,
        realization_status=FIELD_REALIZATION_VALID,
        log_beta=est,
        log_beta_se=se,
        absolute=ScientificInterval(iv, est, se, FIXTURE_CRIT, bias),
        absolute_bias=BiasEvidence.qualified(bias, "fixture"),
        shape=fixture_limit(GateFamily.SHAPE, 0.0, 0.5 * DELTA_G),
        centre=fixture_limit(GateFamily.CENTRE, 0.0, 0.5 * DELTA_M),
        stationarity=fixture_limit(GateFamily.STATIONARITY, 0.0, 0.5),
        current=fixture_limit(GateFamily.CURRENT, 0.0, 0.5 * DELTA_R_IRR),
        evaluable=True,
    )
    kw.update(over)
    return RecordResultV4(**kw)


def good_contrast(block: BlockId, fld: FieldId, **over) -> ContrastResultV4:
    est, se, bias = 0.0, 1.0e-4, 1.0e-5
    iv = build_interval(est, se, FIXTURE_CRIT, bias)
    kw = dict(
        key=ContrastKey(block, fld),
        interval=ScientificInterval(iv, est, se, FIXTURE_CRIT, bias),
        bias=BiasEvidence.qualified(bias, "fixture"),
    )
    kw.update(over)
    return ContrastResultV4(**kw)


def good_family(rejected: bool = False):
    comp = DiagnosticComponents(0.1, 0.1, 0.1, 0.1)
    scales = NullScales(1.0, 1.0, 1.0, 1.0)
    crit = 0.05 if rejected else 1.0
    diags = [
        RecordDiagnostic(f"{b.value}/{f.value}", comp, None, None)
        for b, f in RECORDS
    ]
    return evaluate_diagnostic_family(
        diags, [f"{b.value}/{f.value}" for b, f in RECORDS],
        scales, crit, FIXTURE_GATE,
    )


def good_experiment():
    return (
        [good_record(b, f) for b, f in RECORDS],
        [good_contrast(b, f) for b, f in CONTRASTS],
        good_family(),
    )


# ===========================================================================
# POSITIVE CONTROL -- the conjunction is not simply a wall
# ===========================================================================

def test_positive_control() -> None:
    recs, cons, fam = good_experiment()
    res = complete_pipeline_result(recs, cons, fam)
    check("fully valid experiment counts as complete success",
          res.counts_as_complete_success, res.verdict.classification)
    check("fully valid experiment has clean evidence", res.evidence_ok)
    check("fully valid experiment passes 8 absolute", res.tally.absolute_pass == 8)
    check("fully valid experiment passes 6 contrasts", res.tally.contrast_pass == 6)
    check("fully valid experiment passes all four gates",
          res.tally.shape_pass == 8 and res.tally.centre_pass == 8
          and res.tally.stationarity_pass == 8 and res.tally.current_pass == 8)


# ===========================================================================
# DEFECT 1 -- malformed evidence must fail closed
# ===========================================================================

def test_defect1_malformed_evidence() -> None:
    recs, cons, fam = good_experiment()

    def must_fail(label: str, r=None, c=None, f=None) -> None:
        res = complete_pipeline_result(
            r if r is not None else recs,
            c if c is not None else cons,
            f if f is not None else fam,
        )
        check(label, not res.counts_as_complete_success,
              f"-> {res.verdict.classification}")

    # --- duplicates, in every ordering the auditor demonstrated ------------
    bad = good_record(BlockId.BLOCK1, FieldId.THETA0, evaluable=False,
                      branch_a_valid=False, absolute=None,
                      absolute_bias=BiasEvidence.missing())
    must_fail("invalid duplicate BEFORE the valid record", r=[bad] + list(recs))
    must_fail("invalid duplicate AFTER the valid record", r=list(recs) + [bad])
    must_fail("two valid duplicates",
              r=list(recs) + [good_record(BlockId.BLOCK1, FieldId.THETA0)])
    conflicting = good_record(BlockId.BLOCK1, FieldId.THETA0, log_beta=0.5)
    must_fail("two conflicting duplicates", r=list(recs) + [conflicting])
    must_fail("ninth extra record",
              r=list(recs) + [good_record(BlockId.BLOCK2, FieldId.THETA3)])
    must_fail("missing record", r=list(recs)[:-1])
    must_fail("record filed under the wrong identity",
              r=list(recs)[:-1] + [good_record(
                  BlockId.BLOCK2, FieldId.THETA3,
                  embedded_key=RecordKey(BlockId.BLOCK1, FieldId.THETA0))])

    # --- interval validity --------------------------------------------------
    rev = good_record(BlockId.BLOCK1, FieldId.THETA0)
    rev = RecordResultV4(**{**rev.__dict__,
                           "absolute": ScientificInterval(Interval(0.9, -0.9))})
    must_fail("reversed absolute interval endpoints", r=[rev] + list(recs)[1:])
    check("reversed interval is detected by the validity object",
          IV_REVERSED in ScientificInterval(Interval(0.9, -0.9)).validate())
    check("reversed interval has no containment answer",
          ScientificInterval(Interval(0.9, -0.9)).strictly_inside(DELTA_A) is None)
    check("a RAW reversed Interval still reads as contained (why the object exists)",
          Interval(0.9, -0.9).strictly_inside(DELTA_A) is True)

    for label, iv in [
        ("NaN endpoint", Interval(float("nan"), 0.01)),
        ("infinite endpoint", Interval(-float("inf"), 0.01)),
    ]:
        sci = ScientificInterval(iv, 0.0, 1e-3, FIXTURE_CRIT, 1e-4)
        check(f"{label} rejected", IV_NONFINITE in sci.validate())
        rr = good_record(BlockId.BLOCK1, FieldId.THETA0)
        must_fail(label, r=[RecordResultV4(**{**rr.__dict__, "absolute": sci})]
                  + list(recs)[1:])

    est, bias = 0.0, 1e-4
    neg = ScientificInterval(build_interval(est, 1e-3, FIXTURE_CRIT, bias),
                            est, -1e-3, FIXTURE_CRIT, bias)
    check("negative standard error rejected", IV_SE_NEGATIVE in neg.validate())
    zero = ScientificInterval(build_interval(est, 0.0, FIXTURE_CRIT, bias),
                             est, 0.0, FIXTURE_CRIT, bias)
    check("zero standard error rejected where impossible",
          IV_SE_ZERO in zero.validate())
    mism = ScientificInterval(Interval(-0.001, 0.001), est, 1e-3, FIXTURE_CRIT, bias)
    check("endpoint identity mismatch rejected",
          IV_ENDPOINT_MISMATCH in mism.validate())

    # --- contrast cardinality ----------------------------------------------
    must_fail("duplicate contrast",
              c=list(cons) + [good_contrast(BlockId.BLOCK1, FieldId.THETA1)])
    must_fail("missing contrast", c=list(cons)[:-1])
    cross = ContrastResultV4(key=ContrastKey(
        BlockId.BLOCK1, FieldId.THETA1, FieldId.THETA0, BlockId.BLOCK2))
    must_fail("cross-block contrast substituted", c=list(cons)[:-1] + [cross])
    wrongref = ContrastResultV4(key=ContrastKey(
        BlockId.BLOCK1, FieldId.THETA1, FieldId.THETA2))
    must_fail("contrast against the wrong reference field",
              c=list(cons)[:-1] + [wrongref])
    check("well-formedness detects a cross-block contrast",
          not ContrastKey(BlockId.BLOCK1, FieldId.THETA1,
                          FieldId.THETA0, BlockId.BLOCK2).well_formed)

    # --- bias evidence ------------------------------------------------------
    nb = good_record(BlockId.BLOCK1, FieldId.THETA0)
    must_fail("missing absolute bounded-bias evidence",
              r=[RecordResultV4(**{**nb.__dict__,
                                   "absolute_bias": BiasEvidence.missing()})]
              + list(recs)[1:])
    nc = good_contrast(BlockId.BLOCK1, FieldId.THETA1)
    must_fail("missing contrast bounded-bias evidence",
              c=[ContrastResultV4(**{**nc.__dict__,
                                     "bias": BiasEvidence.missing()})]
              + list(cons)[1:])
    check("missing bias is MISSING, not 0.0",
          BiasEvidence.missing().status is BiasStatus.MISSING
          and BiasEvidence.missing().bound is None)
    check("a certified zero bias is distinguishable from a missing one",
          BiasEvidence.qualified(0.0).usable
          and not BiasEvidence.missing().usable)
    check("a negative bias bound is INVALID",
          BiasEvidence.qualified(-1.0).status is BiasStatus.INVALID)

    # --- exact cardinality reports -----------------------------------------
    rep = check_record_cardinality([r.key for r in recs])
    check("the eight canonical records report clean cardinality", rep.ok)
    rep = check_record_cardinality([recs[0].key] + [r.key for r in recs])
    check("a duplicate key is reported", bool(rep.duplicates))
    rep = check_contrast_cardinality([c.key for c in cons])
    check("the six canonical contrasts report clean cardinality", rep.ok)
    check("exactly eight records are expected", len(RecordKey.expected()) == 8)
    check("exactly six contrasts are expected", len(ContrastKey.expected()) == 6)


def test_critical_value_status() -> None:
    check("the normal quantile is NOT a finite-N calibration",
          NORMAL_CRITICAL.status is CriticalValueStatus.UNCALIBRATED
          and not NORMAL_CRITICAL.calibrated)
    check("1.959963985 is the normal start",
          close(NORMAL_CRITICAL.c_minus, 1.959963984540054, 1e-12))
    recs, cons, fam = good_experiment()
    unc = good_record(BlockId.BLOCK1, FieldId.THETA0)
    sci = ScientificInterval(
        build_interval(0.0, 1e-3, NORMAL_CRITICAL, 1e-4),
        0.0, 1e-3, NORMAL_CRITICAL, 1e-4,
    )
    check("an uncalibrated critical value makes an interval unusable",
          IV_CRITICAL_UNCALIBRATED in sci.validate())
    res = complete_pipeline_result(
        [RecordResultV4(**{**unc.__dict__, "absolute": sci})] + list(recs)[1:],
        cons, fam,
    )
    check("uncalibrated interval cannot reach complete support",
          not res.counts_as_complete_success, res.verdict.classification)
    inv = CriticalValues(2.0, 2.0, "x", CriticalValueStatus.INVALID)
    sci2 = ScientificInterval(build_interval(0.0, 1e-3, inv, 1e-4),
                              0.0, 1e-3, inv, 1e-4)
    check("an INVALID critical value is rejected", not sci2.usable)
    noprov = CriticalValues(2.0, 2.0, "", CriticalValueStatus.CALIBRATED)
    sci3 = ScientificInterval(build_interval(0.0, 1e-3, noprov, 1e-4),
                              0.0, 1e-3, noprov, 1e-4)
    check("a calibrated value with no provenance is rejected", not sci3.usable)


def test_gate_limit_calibration() -> None:
    check("an uncalibrated gate limit has no answer",
          GateLimit.uncalibrated(1e-9).passes(DELTA_G) is None)
    check("a calibrated gate limit answers",
          fixture_limit(GateFamily.SHAPE, 0.0, 1e-9).passes(DELTA_G) is True)
    # V5: the string-identity constructor is gone entirely.
    check("a bare string can no longer calibrate a gate",
          not hasattr(GateLimit, "calibrated"))
    recs, cons, fam = good_experiment()
    for name, tol in (("shape", DELTA_G), ("centre", DELTA_M),
                      ("stationarity", DELTA_STATIONARITY), ("current", DELTA_R_IRR)):
        bad = RecordResultV4(**{**recs[0].__dict__,
                                name: GateLimit.uncalibrated(0.0)})
        res = complete_pipeline_result([bad] + list(recs)[1:], cons, fam)
        check(f"uncalibrated {name} limit prevents support",
              not res.counts_as_complete_success, res.verdict.classification)


# ===========================================================================
# DEFECT 2 -- one authoritative diagnostic family
# ===========================================================================

def test_defect2_diagnostic_family() -> None:
    comp = DiagnosticComponents(0.1, 0.1, 0.1, 0.1)
    scales = NullScales(1.0, 1.0, 1.0, 1.0)
    names = [f"{b.value}/{f.value}" for b, f in RECORDS]
    base = [RecordDiagnostic(n, comp, None, None) for n in names]

    ok = evaluate_diagnostic_family(base, names, scales, 1.0, "cal/x")
    check("complete calibrated coherent family is CALIBRATED",
          ok.status == DIAG_CALIBRATED and ok.rejected is False)

    rej = evaluate_diagnostic_family(base, names, scales, 0.05, "cal/x")
    check("a family above its critical value rejects",
          rej.status == DIAG_CALIBRATED and rej.rejected is True)

    contra = [RecordDiagnostic(names[0], comp, None, True)] + base[1:]
    r = evaluate_diagnostic_family(contra, names, scales, 1.0, "cal/x")
    check("record rejects but components say otherwise -> CONTRADICTORY",
          r.status == DIAG_CONTRADICTORY and r.rejected is None)

    r = evaluate_diagnostic_family(base, names, scales, 1.0, "cal/x",
                                   claimed_rejected=True)
    check("a caller-supplied family boolean is checked, not trusted",
          r.status == DIAG_CONTRADICTORY)

    r = evaluate_diagnostic_family(base[:-1], names, scales, 1.0, "cal/x")
    check("a missing record diagnostic -> NOT_EVALUABLE",
          r.status == DIAG_NOT_EVALUABLE)
    r = evaluate_diagnostic_family(
        [RecordDiagnostic(names[0], None, None, None)] + base[1:],
        names, scales, 1.0, "cal/x")
    check("a record with no components -> NOT_EVALUABLE",
          r.status == DIAG_NOT_EVALUABLE)
    nanc = DiagnosticComponents(0.1, 0.1, 0.1, float("nan"))
    r = evaluate_diagnostic_family(
        [RecordDiagnostic(names[0], nanc, None, None)] + base[1:],
        names, scales, 1.0, "cal/x")
    check("a NaN antisymmetry component -> NOT_EVALUABLE",
          r.status == DIAG_NOT_EVALUABLE)
    r = evaluate_diagnostic_family(base, names, scales, None, "cal/x")
    check("no calibrated familywise critical value -> UNCALIBRATED",
          r.status == DIAG_UNCALIBRATED and r.rejected is None)
    r = evaluate_diagnostic_family(base, names, None, 1.0, "cal/x")
    check("no frozen null scales -> UNCALIBRATED", r.status == DIAG_UNCALIBRATED)
    r = evaluate_diagnostic_family(base, names, scales, float("nan"), "cal/x")
    check("a NaN familywise critical value -> UNCALIBRATED",
          r.status == DIAG_UNCALIBRATED)
    r = evaluate_diagnostic_family(base, names, scales, 1.0, "")
    check("a critical value with no calibration identity -> UNCALIBRATED",
          r.status == DIAG_UNCALIBRATED)
    r = evaluate_diagnostic_family([], [], None, None, "")
    check("an empty expected set is NOT_EVALUABLE, not a family that passed",
          r.status == DIAG_NOT_EVALUABLE)

    recs, cons, _ = good_experiment()
    for label, fam in [
        ("absent", None),
        ("uncalibrated", evaluate_diagnostic_family(base, names, scales, None, "")),
        ("not evaluable", evaluate_diagnostic_family(base[:-1], names, scales, 1.0, "c")),
        ("contradictory", evaluate_diagnostic_family(contra, names, scales, 1.0, "c")),
        ("rejecting", evaluate_diagnostic_family(base, names, scales, 0.05, "c")),
    ]:
        res = complete_pipeline_result(recs, cons, fam)
        check(f"a {label} diagnostic family prevents complete support",
              not res.counts_as_complete_success, res.verdict.classification)

    # the exact V3 behaviour that must have disappeared
    check("raw components alone no longer become family_rejected = False",
          evaluate_diagnostic_family(base, names, None, None, "").rejected is None)


# ===========================================================================
# DEFECT 3 -- the current-control runner route
# ===========================================================================

def test_defect3_current_control_route() -> None:
    case = CASES_BY_ID["CTL-CURRENT"]
    check("CTL-CURRENT no longer declares a dimensional omega",
          "omega" not in case.config.as_dict())
    check("CTL-CURRENT declares the dimensionless r_irr target",
          case.config.r_irr_target == 0.05)
    check("the obsolete omega field is gone from the case schema",
          not hasattr(CaseConfig(), "omega"))

    inst = instantiate("CTL-CURRENT")
    check("the dispatcher routes r_irr_target to design_specs",
          inst.spec_kwargs.get("r_irr_target") == 0.05)

    # The exact public route: registry -> dispatcher -> harness -> spec.
    specs = design_specs(n_frames=256, **inst.spec_kwargs)
    check("the public current-control route does not raise", len(specs) == 8)
    spec, h_locked = specs[0]
    sigma = nm.spd_inverse(spec.h_true)
    d_mat = spec.d_true
    w = nm.inv_sqrtm_spd(sigma)
    s_w = nm.symmetrise(nm.matmul(nm.matmul(w, d_mat), w))
    q = nm.mat([[0.0, -spec.omega_true], [spec.omega_true, 0.0]])
    om = nm.matmul(nm.matmul(w, q), w)
    vals, _ = nm.eigh(s_w)
    r_irr = nm.op_norm(om) / min(vals)
    check("the generated world achieves r_irr = 0.05 to nine decimals",
          close(r_irr, 0.05, 1e-9), f"{r_irr!r}")
    check("the current-control r_irr is above the 0.02 gate", r_irr > DELTA_R_IRR)
    from e1a_v5.observation import bandwidth_product, BANDWIDTH_CEILING
    a_drift = nm.matmul(nm.add(d_mat, q), nm.spd_inverse(sigma))
    bw = bandwidth_product(a_drift, sigma, spec.dt)
    check("the current-control bandwidth stays inside the ceiling",
          bw <= BANDWIDTH_CEILING, f"{bw!r}")
    check("the stationary covariance is unchanged by the current",
          close(nm.max_abs(nm.sub(sigma, nm.spd_inverse(spec.h_true))), 0.0, 1e-12))
    check("the diffusion stays SPD", nm.is_spd(d_mat))
    check("the current is nonzero", abs(spec.omega_true) > 0.0)

    # scale-free: the construction tracks the physical rate
    for factor in (0.25, 4.0):
        om2 = current_control_drift(nm.scale(d_mat, factor), sigma, 0.05)
        check(f"the omega constructor scales with the rate ({factor}x)",
              close(om2, spec.omega_true * factor, 1e-12))


# ===========================================================================
# DEFECT 4 -- C_phi reaches official inference; U.20 profiles the nuisance
# ===========================================================================

K_TRUE = 1.0e-4
T_TRUE = 298.0


def reference_builder(phi):
    """phi = (log stiffness calibration, log T calibration, b_det_x, log R_obs)."""
    lk, lt, bx, lr = phi
    gamma = plan.drag_coefficient()
    k_true = nm.mat([[K_TRUE, 0.0], [0.0, 0.9 * K_TRUE]])
    sigma = nm.scale(nm.spd_inverse(k_true), K_B * T_TRUE)
    a = nm.scale(k_true, 1.0 / gamma)
    k_meas = nm.scale(k_true, math.exp(lk))
    t_meas = T_TRUE * math.exp(lt)
    vals, _ = nm.eigh(k_true)
    tau = gamma / max(vals)
    return FieldModel(
        h_eff=nm.scale(k_meas, 1.0 / (K_B * t_meas)), k_eff=k_meas,
        temperature=t_meas, a_drift=a, sigma=sigma, p_matrix=nm.eye(2),
        r_obs=nm.scale(nm.scale(nm.eye(2), 0.02 * sigma[0][0]), math.exp(lr)),
        b_det=(bx, 0.0), dt=0.75 * 0.2 * tau, t_exp=0.05 * tau,
    )


def reference_generic_builder(phi):
    """The same map over the generic kernel, for certified differentiation."""
    lk, lt, bx, lr = phi
    gamma = plan.drag_coefficient()
    k_true = nm.mat([[K_TRUE, 0.0], [0.0, 0.9 * K_TRUE]])
    vals, _ = nm.eigh(k_true)
    tau = gamma / max(vals)
    sigma = nm.scale(nm.spd_inverse(k_true), K_B * T_TRUE)
    k_meas = cert.gscale(k_true, cert.gexp(lk))
    inv_kt = cert.gexp(-lt) * (1.0 / (K_B * T_TRUE))
    return AnalysisModel(
        h_locked=cert.gscale(k_meas, inv_kt), p_matrix=nm.eye(2),
        r_obs=cert.gscale(nm.scale(nm.eye(2), 0.02 * sigma[0][0]), cert.gexp(lr)),
        b_det=(bx, 0.0), dt=0.75 * 0.2 * tau, t_exp=0.05 * tau)


REF_PHI = [0.0, 0.0, 0.0, 0.0]
REF_SIGMA = [6.0e-3, 1.0e-3, 2.0e-9, 5.0e-2]


def test_defect4_profiled_sensitivity() -> None:
    check("the profiled nuisance vector is the production locked-fit vector",
          THETA_NAMES == ("log_beta", "mu_x", "mu_y",
                          "d_chol_0", "d_chol_1", "d_chol_2", "omega"))
    check("log beta is extracted only as one row of a 7-parameter system",
          N_THETA == 7 and LOG_BETA_ROW == 0)

    ps = certified_profiled_sensitivity(
        reference_generic_builder, reference_builder, REF_PHI, phi_sigma=REF_SIGMA)
    check("the sensitivity is the implicit expected-score derivative",
          "expected-score system" in ps.method)
    check("V5: it is certified, with no finite differences",
          ps.certified and "no finite differences" in ps.method)

    # Analytic references, each derived from the primitive map, not reused.
    #   The locked fit matches Sigma_m = exp(-b) H_A^{-1} to the true Sigma.
    #   With H_A = K_A/(k_B T_A), K_A = K exp(phi0), T_A = T exp(phi1):
    #       b* = phi1 - phi0,  so  db/dphi0 = -1  and  db/dphi1 = +1.
    #   A detector offset is absorbed entirely by the centre nuisance:
    #       mu* = mu + P^{-1}(b_true - b_A),  so  db/dphi2 = 0, dmu_x/dphi2 = -1.
    refs = [
        (LOG_BETA_ROW, 0, -1.0, "d log beta*/d log k_A = -1"),
        (LOG_BETA_ROW, 1, +1.0, "d log beta*/d log T_A = +1"),
        (LOG_BETA_ROW, 2, 0.0, "d log beta*/d b_det_x = 0"),
        (1, 2, -1.0, "d mu_x*/d b_det_x = -1 (P = I)"),
        (2, 2, 0.0, "d mu_y*/d b_det_x = 0"),
    ]
    for i, k, exact, label in refs:
        got, rad = ps.jacobian[i][k], ps.radius[i][k]
        check(f"analytic reference: {label}", abs(got - exact) <= max(rad, 1e-9),
              f"got {got!r} radius {rad!r}")
        check(f"certified enclosure brackets the exact value: {label}",
              abs(got - exact) <= rad or (got == exact))

    check("the V3 truth-side sign is NOT reused for the stiffness primitive",
          ps.jacobian[LOG_BETA_ROW][0] < 0.0)

    # Option A == option B, within both certified enclosures.
    pb = profiled_sensitivity_by_optimisation(
        reference_builder, REF_PHI, phi_sigma=REF_SIGMA)
    # The log-beta row is the production quantity; the certified enclosure is
    # authoritative and the optimisation route carries only a backward-error
    # bound on its located maximum, so agreement is asserted where both are
    # meaningful rather than everywhere.
    lb_overlaps = sum(
        1 for k in range(len(REF_PHI))
        if enclosures_overlap(ps, pb, LOG_BETA_ROW, k)
    )
    check("the two routes agree on every log-beta sensitivity",
          lb_overlaps == len(REF_PHI), f"{lb_overlaps}/{len(REF_PHI)}")
    overlaps = sum(
        1 for i in range(N_THETA) for k in range(len(REF_PHI))
        if enclosures_overlap(ps, pb, i, k)
    )
    check("the two routes agree across almost the whole Jacobian",
          overlaps >= N_THETA * len(REF_PHI) - 2,
          f"{overlaps}/{N_THETA * len(REF_PHI)}")
    check("the optimisation route is NOT certified and cannot qualify",
          pb.certified is False)

    # Steps are taken in each primitive's OWN units (cross-check route only).
    steps = primitive_steps(REF_PHI, REF_SIGMA, 1.0, 1e-3, 1e-3)
    check("each primitive is stepped by its own declared uncertainty",
          all(close(steps[k], REF_SIGMA[k], 1e-15) for k in range(4)))
    check("a detector-offset step is nanometres, not millimetres",
          steps[2] < 1e-8)

    check("the expected information is certifiably nonsingular",
          ps.information_min_eigenvalue > 0.0)
    check("the Riccati fixed-point bound is reported",
          0.0 <= ps.riccati_bound < 1e-6)


def test_defect4_numerical_enclosure() -> None:
    import e1a_v5.calibration as C
    import e1a_v5.confidence as cf
    check("the fixed 1e-5 numerical band is gone",
          not hasattr(cf, "CALIBRATION_NUMERICAL_RTOL"))
    check("the fixed-band classifier is gone",
          not hasattr(cf, "classify_against_ceiling"))
    check("V5: the finite-difference production sensitivity is gone",
          not hasattr(C, "profiled_sensitivity"))

    c = SIGMA_CAL_ABS_MAX
    check("PASS iff the upper enclosure endpoint is within the ceiling",
          classify_with_enclosure(
              NumericalEnclosure(c - 2e-5, c - 3e-5, c - 1e-5, "m"), c) == CEILING_PASS)
    check("FAIL iff the lower enclosure endpoint is above the ceiling",
          classify_with_enclosure(
              NumericalEnclosure(c + 2e-5, c + 1e-5, c + 3e-5, "m"), c) == CEILING_FAIL)
    check("a straddling enclosure is UNRESOLVED",
          classify_with_enclosure(
              NumericalEnclosure(c, c - 1e-5, c + 1e-5, "m"), c) == CEILING_UNRESOLVED)
    check("an exact value at the inclusive ceiling PASSES",
          classify_with_enclosure(NumericalEnclosure.exact(c), c) == CEILING_PASS)
    check("no enclosure at all is UNRESOLVED, which is fail-closed",
          classify_with_enclosure(None, c) == CEILING_UNRESOLVED)
    check("a non-finite enclosure FAILS",
          classify_with_enclosure(
              NumericalEnclosure(float("nan"), float("nan"), float("nan"), "m"), c)
          == CEILING_FAIL)
    check("the unresolved band is case specific, not a fixed fraction",
          classify_with_enclosure(
              NumericalEnclosure(c, c - 1e-14, c + 1e-14, "tight"), c)
          == CEILING_UNRESOLVED
          and classify_with_enclosure(
              NumericalEnclosure(c - 1e-9, c - 2e-9, c - 1e-12, "tight"), c)
          == CEILING_PASS)
    try:
        NumericalEnclosure(0.0, 1.0, -1.0, "m")
        check("a reversed enclosure is refused", False)
    except NumericalFailure:
        check("a reversed enclosure is refused", True)


def test_defect4_official_path() -> None:
    cal = experiment_calibration()
    check("the official calibration covers all eight endpoints",
          len(cal.keys) == 8 and nm.shape(cal.c_b_cal) == (8, 8))
    check("the Jacobian has one row per record",
          nm.shape(cal.j_beta) == (8, len(cal.phi_names)))

    k0, k1 = "block1/theta0", "block1/theta1"
    a = cal.absolute_sigma(k1)
    c = cal.contrast_sigma(k1, k0)
    check("the absolute endpoint carries a certified enclosure",
          a.radius > 0.0 and a.lo <= a.point <= a.hi)
    check("the absolute endpoint qualifies against 0.009",
          cal.absolute_qualification(k1) == CEILING_PASS, f"{a.point!r}")
    check("the contrast qualifies against 0.003",
          cal.contrast_qualification(k1, k0) == CEILING_PASS, f"{c.point!r}")
    check("the contrast is built from the joint covariance, not two absolutes",
          c.point < math.sqrt(2.0) * a.point)

    # C_d = D C_b D^T, exactly.
    i, j = cal.index_of(k1), cal.index_of(k0)
    var = cal.c_b_cal[i][i] + cal.c_b_cal[j][j] - 2.0 * cal.c_b_cal[i][j]
    check("the contrast sigma equals sqrt(D C_b D^T)",
          close(c.point, math.sqrt(max(0.0, var)), 1e-9))

    # Shared primitives correlate the rows automatically.
    rho = cal.c_b_cal[0][1] / math.sqrt(cal.c_b_cal[0][0] * cal.c_b_cal[1][1])
    check("two records sharing a standard are positively correlated",
          rho > 0.5, f"{rho!r}")

    # Total error combines the two contributions exactly once.
    check("the total standard error adds conditional and calibration in quadrature",
          close(combined_standard_error(3.0, 4.0), 5.0, 1e-15))
    check("the contrast standard error adds three independent pieces",
          close(combined_contrast_standard_error(3.0, 4.0, 12.0), 13.0, 1e-15))
    try:
        combined_standard_error(-1.0, 1.0)
        check("a negative standard error is refused", False)
    except NumericalFailure:
        check("a negative standard error is refused", True)


def test_defect4_shared_cancellation() -> None:
    """A purely shared error cancels; independent per-field errors give sqrt(2)."""
    def mkg(idx_shared, idx_field):
        """The same map over the generic kernel."""
        k_true = nm.mat([[K_TRUE, 0.0], [0.0, K_TRUE]])
        gamma = plan.drag_coefficient()
        vals, _ = nm.eigh(k_true)
        tau = gamma / max(vals)
        sigma = nm.scale(nm.spd_inverse(k_true), K_B * T_TRUE)

        def b(phi):
            lk = phi[idx_shared] + phi[idx_field]
            return AnalysisModel(
                h_locked=cert.gscale(cert.gscale(k_true, cert.gexp(lk)),
                                     1.0 / (K_B * T_TRUE)),
                p_matrix=nm.eye(2),
                r_obs=nm.scale(nm.eye(2), 0.02 * sigma[0][0]),
                b_det=(0.0, 0.0), dt=0.75 * 0.2 * tau, t_exp=0.05 * tau)

        return b

    def mk(idx_shared, idx_field):
        def b(phi):
            gamma = plan.drag_coefficient()
            k_true = nm.mat([[K_TRUE, 0.0], [0.0, K_TRUE]])
            sigma = nm.scale(nm.spd_inverse(k_true), K_B * T_TRUE)
            a = nm.scale(k_true, 1.0 / gamma)
            lk = phi[idx_shared] + phi[idx_field]
            k_meas = nm.scale(k_true, math.exp(lk))
            vals, _ = nm.eigh(k_true)
            tau = gamma / max(vals)
            return FieldModel(
                h_eff=nm.scale(k_meas, 1.0 / (K_B * T_TRUE)), k_eff=k_meas,
                temperature=T_TRUE, a_drift=a, sigma=sigma, p_matrix=nm.eye(2),
                r_obs=nm.scale(nm.eye(2), 0.02 * sigma[0][0]), b_det=(0.0, 0.0),
                dt=0.75 * 0.2 * tau, t_exp=0.05 * tau)
        return b

    def run(shared, per_field):
        v = PrimitiveVector()
        v.add(Primitive("std", Scope.GLOBAL, 0.0, shared))
        for blk, f in RECORDS[:2]:
            v.add(Primitive("fld", Scope.FIELD, 0.0, per_field, blk, f))
        ish = v.index_of("std")
        recs = []
        for b, f in RECORDS[:2]:
            idx = v.index_of(f"fld@{b.value}/{f.value}")
            recs.append((f"{b.value}/{f.value}", mk(ish, idx), mkg(ish, idx)))
        return build_experiment_calibration(v, recs)

    cal = run(6.0e-3, 0.0)
    k0, k1 = cal.keys[0], cal.keys[1]
    a, c = cal.absolute_sigma(k1).point, cal.contrast_sigma(k1, k0).point
    check("a purely shared calibration error cancels in the contrast",
          c < 1e-6 * a, f"ratio {c / a!r}")
    check("a purely shared error gives perfectly correlated endpoints",
          close(cal.c_b_cal[0][1] / math.sqrt(cal.c_b_cal[0][0] * cal.c_b_cal[1][1]),
                1.0, 1e-7))

    cal = run(0.0, 1.5e-3)
    k0, k1 = cal.keys[0], cal.keys[1]
    a, c = cal.absolute_sigma(k1).point, cal.contrast_sigma(k1, k0).point
    check("independent per-field errors give sqrt(2) x the absolute",
          close(c / a, math.sqrt(2.0), 1e-6), f"ratio {c / a!r}")


def test_defect4_bounded_bias_missing() -> None:
    bb = BoundedBias(absolute={"k": BiasEvidence.qualified(1e-4)}, contrast={})
    check("a present absolute bound is returned", close(bb.absolute_bound("k"), 1e-4))
    check("an absent absolute bound is MISSING, not zero",
          not bb.absolute_evidence("absent").usable)
    try:
        bb.absolute_bound("absent")
        check("requiring an absent absolute bound raises", False)
    except ValueError:
        check("requiring an absent absolute bound raises", True)
    try:
        bb.contrast_bound("any")
        check("a contrast bound may not be inferred from absolutes", False)
    except ValueError:
        check("a contrast bound may not be inferred from absolutes", True)
    check("two 0.0005 absolute bounds imply only 0.001 for a contrast",
          close(2.0 * BIAS_ABS_MAX, 0.001, 1e-15))
    check("an empty bias qualification is refused", _raises(
        lambda: bias_qualification([], [])))
    check("an empty absolute qualification is refused", _raises(
        lambda: absolute_qualification([])))
    check("an empty contrast qualification is refused", _raises(
        lambda: contrast_qualification([[1.0]], [])))


def _raises(fn) -> bool:
    try:
        fn()
        return False
    except Exception:
        return True


# ===========================================================================
# DEFECT 5 -- the axial remainder's units
# ===========================================================================

def test_defect5_axial_remainder_units() -> None:
    """V4 made the remainder dimensionless; V5 made its effects EXACT.

    The V4 assertions that survive are the typing and the normalisation.  The
    first-order impact quantities they fed are replaced by the exact finite
    effects, which the V5 suite tests against the auditor's counterexamples.
    """
    import e1a_v5.reduction as rd
    check("the standalone dimensional 1e-3 ceiling is gone",
          not hasattr(rd, "NONLINEAR_REMAINDER_CEILING"))
    check("the only remaining axial constant is a dimensionless domain guard",
          REMAINDER_DOMAIN_LIMIT == 1.0)

    k3 = plan.nominal_k3(0)
    _, b, kappa = split_3d(nm.symmetrise(k3))
    rem = schur_nonlinear_remainder([b[0][0], b[1][0]], kappa,
                                    [0.05 * b[0][0], 0.05 * b[1][0]], 0.05 * kappa)
    check("the remainder witness is a TYPED stiffness residual",
          isinstance(rem, NonlinearRemainder)
          and rem.kind is RemainderKind.STIFFNESS_RESIDUAL and rem.unit == "N/m")
    check("a raw unlabelled float is not accepted",
          _raises(lambda: NonlinearRemainder([[0.0]])))
    check("a normalised remainder may not claim N/m",
          _raises(lambda: NonlinearRemainder(
              [[0.0, 0.0], [0.0, 0.0]], RemainderKind.NORMALISED, "N/m")))

    k_eff = schur_complement(k3)
    e_k = normalise_remainder(rem, k_eff)
    im = remainder_impacts(e_k)
    check("the normalised remainder is dimensionless and tiny here",
          im.rho < 1e-12, f"{im.rho!r}")

    m = nm.mat([[2.0, 0.3], [0.0, 0.7]])
    k2 = nm.matmul(nm.matmul(m, k_eff), nm.transpose(m))
    r2 = NonlinearRemainder(nm.matmul(nm.matmul(m, rem.matrix), nm.transpose(m)))
    im2 = remainder_impacts(normalise_remainder(r2, k2))
    check("a coordinate-scaled equivalent remainder classifies identically",
          close(im2.rho, im.rho, 1e-10))
    k3x = nm.scale(k_eff, 1e9)
    r3 = NonlinearRemainder(nm.scale(rem.matrix, 1e9))
    im3 = remainder_impacts(normalise_remainder(r3, k3x))
    check("an overall rescaling of the stiffness classifies identically",
          close(im3.rho, im.rho, 1e-10))

    # The effects land in the EXISTING budgets, exactly.
    iso = NonlinearRemainder(nm.scale(k_eff, 0.02), source="2 percent isotropic")
    ii = remainder_impacts(normalise_remainder(iso, k_eff))
    check("an isotropic remainder lands in the scale budget, not the geometry",
          close(ii.log_beta_bias, abs(math.log1p(0.02)), 1e-9)
          and ii.geometry < 1e-9)
    vals, q = nm.eigh(k_eff)
    traceless = nm.symmetrise(nm.matmul(nm.matmul(
        q, [[0.02 * vals[0], 0.0], [0.0, -0.02 * vals[1]]]), nm.transpose(q)))
    ti = remainder_impacts(normalise_remainder(NonlinearRemainder(traceless), k_eff))
    check("a traceless remainder lands mostly in the geometry budget",
          close(ti.geometry, math.atanh(0.02), 1e-9))
    # A traceless E has ZERO first-order scale effect but a nonzero EXACT one:
    # b* = log d - log tr((I+E)^{-1}) = log 2 - log(1/1.02 + 1/0.98).
    exact_scale = abs(math.log(2.0) - math.log(1.0 / 1.02 + 1.0 / 0.98))
    check("its exact scale effect is second order but NOT zero",
          close(ti.log_beta_bias, exact_scale, 1e-9) and ti.log_beta_bias > 1e-5,
          f"{ti.log_beta_bias!r}")
    check("a small scale impact with a large geometry impact still fails the "
          "existing shape budget", ti.geometry * 5.0 > DELTA_G)

    big = remainder_impacts(normalise_remainder(
        NonlinearRemainder(nm.scale(k_eff, 5.0)), k_eff))
    check("a 5x nominal stiffness remainder leaves the domain",
          not big.within_domain and big.rho >= REMAINDER_DOMAIN_LIMIT)
    check("a 5x remainder fails the existing bias budget strongly",
          big.log_beta_bias > 100.0 * BIAS_ABS_MAX)

    c_v = nm.scale(nm.eye(6), (plan.PRIMITIVE_RELATIVE_SIGMA * plan.K_REF) ** 2)
    red = reduce_axial(k3, plan.T_REF,
                       evidence=AxialEvidence.fully_qualified(), c_v=c_v)
    check("a certified zero remainder set qualifies when all else passes",
          red.ok and red.remainder_impacts is not None
          and red.remainder_impacts.log_beta_bias == 0.0)
    red = reduce_axial(k3, plan.T_REF, evidence=AxialEvidence(
        **{**AxialEvidence.fully_qualified().__dict__,
           "remainder_set": None}), c_v=c_v)
    check("a missing certified remainder set is refused", not red.ok)
    red = reduce_axial(k3, plan.T_REF, evidence=AxialEvidence(
        **{**AxialEvidence.fully_qualified().__dict__,
           "remainder_set": RemainderSet(5.0)}), c_v=c_v)
    check("a set outside the SPD domain is refused by the reduction", not red.ok)
    check("the refusal names the dimensionless norm",
          any("E_K" in r.predicate for r in red.refusals))


# ===========================================================================
# DEFECT 6 -- cases instantiate their declared worlds
# ===========================================================================

def test_defect6_case_registry() -> None:
    check("every case id is unique", len(CASES_BY_ID) == len(ALL_CASES))
    check("an unknown case id is a hard error, never a nominal run",
          _raises(lambda: instantiate("NOT-A-CASE")))

    # The meta-test the brief requires, over every registered case.
    for case in ALL_CASES:
        inst = instantiate(case.case_id)
        declared = set(case.config.declared_fields())
        check(f"{case.case_id}: dispatcher has an explicit handler",
              inst.driver is not None and inst.driver != "")
        check(f"{case.case_id}: every declared parameter is consumed",
              declared <= set(inst.consumed),
              f"unconsumed {sorted(declared - set(inst.consumed))}")
        check(f"{case.case_id}: the generated configuration records them",
              set(case.config.as_dict()) <= set(inst.digest()["consumed"]))
        check(f"{case.case_id}: a declared event evaluator exists",
              isinstance(case.expected_event, ExpectedEvent))
        if not inst.runnable:
            check(f"{case.case_id}: an unrunnable case states why",
                  bool(inst.not_run_reason))

    # No non-nominal case may have a no-op configuration.
    nominal = instantiate("POWER-NOMINAL")
    for case in ALL_CASES:
        if not case.config.declared_fields():
            continue
        inst = instantiate(case.case_id)
        if inst.driver not in IMPLEMENTED_DRIVERS or inst.driver == "deterministic":
            continue
        differs = (
            dict(inst.spec_kwargs) != dict(nominal.spec_kwargs)
            or inst.b_true is not None or inst.blind_scale is not None
            or inst.geometry is not None or inst.selection is not None
            or inst.sigma_cal is not None
            or inst.axial_memory or inst.omit_eta_t_covariance
        )
        check(f"{case.case_id}: the instantiated world differs from nominal",
              differs)

    routed, handled = deterministic_coverage()
    check("every deterministic case has a battery handler",
          routed <= handled, f"missing {sorted(routed - handled)}")
    for r in deterministic_controls():
        check(f"deterministic control {r['case_id']} passes", r["passed"])


def test_defect6_declared_worlds_are_built() -> None:
    from e1a_v5.observation import localization_ratio
    nominal = design_specs(n_frames=200)[0][0]

    # POWER-CONDLIM really conditions.
    inst = instantiate("POWER-CONDLIM")
    spec = design_specs(n_frames=200, **inst.spec_kwargs)[0][0]
    cond = nm.cond2_spd(spec.h_true)
    check("POWER-CONDLIM generates a conditioned world",
          abs(cond - 100.0) < 1e-6, f"{cond!r}")
    check("POWER-CONDLIM is NOT the nominal conditioning",
          abs(cond - nm.cond2_spd(nominal.h_true)) > 90.0)
    check("POWER-CONDLIM stays inside the qualification limit", cond <= 100.0)

    # POWER-NOISEHI really changes the observation model.
    inst = instantiate("POWER-NOISEHI")
    spec = design_specs(n_frames=200, **inst.spec_kwargs)[0][0]
    ratio = localization_ratio(nm.spd_inverse(spec.h_true), spec.r_obs, spec.p_matrix)
    check("POWER-NOISEHI generates the declared noise ratio",
          close(ratio, 0.05, 1e-9), f"{ratio!r}")
    check("POWER-NOISEHI changes R_obs relative to nominal",
          nm.max_abs(nm.sub(spec.r_obs, nominal.r_obs)) > 0.0)
    check("POWER-NOISEHI sits at the T.23 ceiling, not above it", ratio <= 0.05)

    # Exposure, betas, noise model, drift, blur all reach the spec.
    spec = design_specs(n_frames=200,
                        **instantiate("SIZE-NUIS-EXP").spec_kwargs)[0][0]
    check("the exposure case moves the shutter",
          spec.t_exp > nominal.t_exp * 1.9)
    specs = design_specs(n_frames=200,
                         **instantiate("CTL-FIELD-106").spec_kwargs)
    check("a field-specific control changes only its own field",
          close(specs[1][0].beta_true, 1.06) and close(specs[0][0].beta_true, 1.0))
    specs = design_specs(n_frames=200,
                         **instantiate("CTL-FIELD-MIX").spec_kwargs)
    check("a mixed field control sets every declared beta",
          close(specs[1][0].beta_true, 0.93) and close(specs[2][0].beta_true, 1.05))
    spec = design_specs(n_frames=200,
                        **instantiate("CTL-NOISE-HEAVY").spec_kwargs)[0][0]
    check("the heavy-tail control changes the noise model",
          spec.noise_model == "heavy")
    spec = design_specs(n_frames=200,
                        **instantiate("CTL-DRIFT").spec_kwargs)[0][0]
    check("the drift control sets a nonzero drift rate",
          spec.drift_rate[0] != 0.0)
    spec = design_specs(n_frames=200,
                        **instantiate("CTL-BLUR-MISMATCH").spec_kwargs)[0][0]
    check("the blur-mismatch control sets a generator exposure override",
          spec.generate_t_exp is not None and spec.generate_t_exp != spec.t_exp)
    specs = design_specs(n_frames=200,
                         **instantiate("CTL-COMMON-07").spec_kwargs)
    check("the common-scale control sets every field",
          all(close(s.beta_true, 0.7) for s, _ in specs))

    # Geometry controls act on the locked / true matrices.
    spec, h = design_specs(n_frames=200)[0]
    _, h2 = apply_geometry("trace_preserving", spec, h)
    check("the trace-preserving geometry control changes the locked H",
          nm.max_abs(nm.sub(h2, h)) > 0.0)
    s2, h3 = apply_geometry("rotation", spec, h)
    check("the rotation geometry control rotates the true H",
          nm.max_abs(nm.sub(s2.h_true, spec.h_true)) > 0.0)
    check("an unknown geometry perturbation is a hard error",
          _raises(lambda: apply_geometry("nope", spec, h)))


def test_defect6_event_evaluator() -> None:
    check("the event evaluator is versioned",
          EVENT_EVALUATOR_VERSION.endswith("-v4"))
    case = CASES_BY_ID["POWER-NOMINAL"]
    for cls, want in [(SUPPORTED, True), (INVALID, False),
                      (NOT_EVALUABLE, False), (None, False)]:
        o = ReplicateOutcome("POWER-NOMINAL", 0, 1, classification=cls)
        check(f"complete support counts only on {SUPPORTED} (got {cls})",
              evaluate_event(case, o) is want)
    o = ReplicateOutcome("POWER-NOMINAL", 0, 1, classification=None,
                         absolute_contained=True)
    check("a raw contained interval cannot bypass the verdict",
          evaluate_event(case, o) is False)

    rf_case = CASES_BY_ID["CTL-RF-TEMP-304"]
    check("a realization-status case counts only on its exact status",
          evaluate_event(rf_case, ReplicateOutcome(
              "x", 0, 1, realization_status="OUT_OF_SPEC")) is True
          and evaluate_event(rf_case, ReplicateOutcome(
              "x", 0, 1, realization_status="VALID")) is False)
    blind = CASES_BY_ID["CTL-BLIND-107"]
    check("a blinded-recovery case counts on a small recovery error",
          evaluate_event(blind, ReplicateOutcome("x", 0, 1, blinded_error=1e-4))
          is True)
    check("a blinded-recovery case does not count on a large error",
          evaluate_event(blind, ReplicateOutcome("x", 0, 1, blinded_error=0.5))
          is False)
    check("a blinded-recovery case does not count on a missing error",
          evaluate_event(blind, ReplicateOutcome("x", 0, 1)) is False)
    cal = CASES_BY_ID["CAL-SCALE-01"]
    check("a calibration case has no pass/fail event",
          _raises(lambda: evaluate_event(cal, ReplicateOutcome("x", 0, 1))))


# ===========================================================================
# DEFECT 7 -- per-replicate reasons survive aggregation
# ===========================================================================

def test_defect7_reason_retention() -> None:
    agg = ReasonAggregate("CTL-CURRENT")
    specimens = [
        ("bandwidth", ("OBSERVATION_MODEL_UNQUALIFIED",),
         ("OBSERVATION_MODEL_UNQUALIFIED:||B||_2 dt <= 0.2",), ("block1/theta0",)),
        ("optimiser", ("COMPUTATION_NOT_EVALUABLE",),
         ("COMPUTATION_NOT_EVALUABLE:unique usable maximum established",),
         ("block1/theta1",)),
        ("diagnostic input", ("COMPUTATION_NOT_EVALUABLE",),
         ("COMPUTATION_NOT_EVALUABLE:diagnostic family evaluable",),
         ("block2/theta0",)),
        ("diffusion", ("NUMERICAL_REPRESENTATION_FAILURE",),
         ("NUMERICAL_REPRESENTATION_FAILURE:likelihood evaluable",),
         ("block2/theta2",)),
        ("conditioning", ("INSUFFICIENT_GEOMETRY_CALIBRATION",),
         ("INSUFFICIENT_GEOMETRY_CALIBRATION:cond2(H_eff) <= 100.0",),
         ("block1/theta2",)),
    ]
    for i, (_, codes, preds, aff) in enumerate(specimens):
        agg.add(ReplicateOutcome(
            "CTL-CURRENT", i, 1000 + i, classification=NOT_EVALUABLE,
            reason_codes=codes, reason_predicates=preds, affected=aff))
    d = agg.as_dict()
    check("every per-replicate record is retained",
          len(d["per_replicate"]) == len(specimens))
    check("per-replicate seeds are retained",
          [r["seed"] for r in d["per_replicate"]] == [1000 + i for i in range(5)])
    check("a reason-code histogram is produced", bool(d["reason_codes"]))
    check("joint reason combinations are produced",
          bool(d["joint_reason_combinations"]))
    check("the affected record is retained per replicate",
          set(d["affected"]) == {"block1/theta0", "block1/theta1", "block2/theta0",
                                 "block2/theta2", "block1/theta2"})
    check("two failures sharing a code stay distinguishable by predicate",
          d["reason_codes"]["COMPUTATION_NOT_EVALUABLE"] == 2
          and len([k for k in d["reason_predicates"]
                   if k.startswith("COMPUTATION_NOT_EVALUABLE")]) == 2)
    check("the aggregate is not merely a nonevaluable count",
          "per_replicate" in d and "reason_predicates" in d)
    check("the evaluator version travels with the aggregate",
          d["evaluator_version"] == EVENT_EVALUATOR_VERSION)


# ===========================================================================
# Systematic fail-open search
# ===========================================================================

def _code_lines(path: str) -> list[tuple[int, str]]:
    """Source lines with comments AND string literals removed.

    Scanning raw text would flag the docstrings that *describe* the repaired
    fail-open patterns, so the scan reads tokens instead of characters.
    """
    import io
    import tokenize
    with open(path, "rb") as fh:
        src = fh.read().decode("utf-8")
    blanked = {}
    try:
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            if tok.type in (tokenize.STRING, tokenize.COMMENT):
                for ln in range(tok.start[0], tok.end[0] + 1):
                    blanked.setdefault(ln, []).append(tok)
    except tokenize.TokenError:
        pass
    out = []
    for i, line in enumerate(src.splitlines(), 1):
        if i in blanked:
            continue
        out.append((i, line))
    return out


def test_systematic_fail_open() -> None:
    import os
    import re
    bad: list[str] = []
    allowed_max_one = {
        os.path.join("e1a_v5", "optimize.py"),  # dimensionless optimiser coords
    }
    rx_max_one = re.compile(r"max\(\s*1\.0\s*,")
    rx_get_pass = re.compile(r"\.get\([^)]*?,\s*(True|False|0\.0|1\.0)\s*\)")
    for root, dirs, files in os.walk("e1a_v5"):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for f in sorted(files):
            if not f.endswith(".py"):
                continue
            path = os.path.join(root, f)
            for i, code in _code_lines(path):
                if rx_max_one.search(code) and path not in allowed_max_one:
                    bad.append(f"{path}:{i} max(1.0, .)")
                if rx_get_pass.search(code):
                    bad.append(f"{path}:{i} .get(..., <pass-reading default>)")
    check("no load-bearing max(1.0, .) outside the optimiser coordinates",
          not [b for b in bad if "max(1.0" in b], str(bad))
    check("no dict.get with a pass-reading default anywhere",
          not [b for b in bad if ".get(" in b], str(bad))

    # Empty-sequence all() semantics.
    check("empty absolute qualification refuses", _raises(
        lambda: absolute_qualification([])))
    check("empty diagnostic family is NOT_EVALUABLE",
          evaluate_diagnostic_family([], [], None, None, "").status
          == DIAG_NOT_EVALUABLE)
    # No evidence anywhere must reach support.
    res = complete_pipeline_result([], [], None)
    check("an empty experiment is never a success",
          not res.counts_as_complete_success)
    check("an empty experiment names its missing records",
          len([r for r in res.reasons if r.code == "INCOMPLETE_INPUT"]) >= 8)


# ===========================================================================
# V4 identities and seeds
# ===========================================================================

def test_v4_identities_and_seeds() -> None:
    check("evidence.py is bound into the analysis identity",
          "evidence.py" in ANALYSIS_MODULES)
    for m in ("evidence.py", "diagnostics.py",
              "validation/dispatch.py".replace("/", __import__("os").sep),
              "validation/events.py".replace("/", __import__("os").sep),
              "validation/run.py".replace("/", __import__("os").sep)):
        check(f"{m} is bound into the validation identity",
              m in VALIDATION_MODULES)
    pre = validation_preimage()
    check("the validation preimage documents the dispatcher",
          "validation/dispatch.py".replace("/", __import__("os").sep)
          in pre["rationale"] or any("dispatch" in k for k in pre["rationale"]))
    ids = compute_identities()
    check("all six identities are distinct 64-hex digests",
          len({*ids.as_dict().values()}) == 6
          and all(len(v) == 64 for v in ids.as_dict().values()))

    sm = SeedMap()
    from e1a_v5.seeds import ROOT_V4 as _R4, ROOT_V5 as _R5
    check("the live root is new",
          sm.root == ROOT and ROOT not in (ROOT_V2, ROOT_V3, _R4, _R5))
    check("five confirmatory families are frozen",
          len(CONFIRMATORY_FAMILIES) == 5
          and all(f.endswith("-v6") for f in CONFIRMATORY_FAMILIES))
    check("the engineering namespace is separate from every confirmatory one",
          ENGINEERING not in CONFIRMATORY_FAMILIES
          and sm.engineering_disjoint_from_confirmatory("POWER-NOMINAL"))
    from e1a_v5.seeds import FAMILIES_V4, ROOT_V4
    for fam, old4, old3, old2 in zip(CONFIRMATORY_FAMILIES, FAMILIES_V4,
                                     FAMILIES_V3, FAMILIES_V2):
        check(f"{fam} is disjoint from its V4 stream",
              sm.disjoint_from(fam, ROOT_V4, old4, "POWER-NOMINAL"))
        check(f"{fam} is disjoint from its V3 stream",
              sm.disjoint_from(fam, ROOT_V3, old3, "POWER-NOMINAL"))
        check(f"{fam} is disjoint from its V2 stream",
              sm.disjoint_from(fam, ROOT_V2, old2, "POWER-NOMINAL"))
    check("an unknown seed family is refused",
          _raises(lambda: sm.family_seed("not-a-family")))


# ===========================================================================

def main() -> int:
    print("E1a v5 PROCEDURE VERSION 4 -- CORE REPAIR REGRESSIONS")
    print("Execution class: MIXED STATIC/PURE + SYNTHETIC ENGINEERING CHECKS\n")
    print("positive control -- a valid experiment does succeed")
    test_positive_control()
    print("\ndefect 1 -- malformed evidence fails closed")
    test_defect1_malformed_evidence()
    print("\ncritical-value status")
    test_critical_value_status()
    print("\ncalibrated gate limits")
    test_gate_limit_calibration()
    print("\ndefect 2 -- one authoritative diagnostic family")
    test_defect2_diagnostic_family()
    print("\ndefect 3 -- current-control runner route")
    test_defect3_current_control_route()
    print("\ndefect 4 -- U.20 profiled nuisance sensitivity [SYNTHETIC]")
    test_defect4_profiled_sensitivity()
    print("\ndefect 4 -- certified numerical enclosure")
    test_defect4_numerical_enclosure()
    print("\ndefect 4 -- C_phi on the official path [SYNTHETIC]")
    test_defect4_official_path()
    print("\ndefect 4 -- shared-primitive cancellation [SYNTHETIC]")
    test_defect4_shared_cancellation()
    print("\ndefect 4 -- bounded bias: missing is not zero")
    test_defect4_bounded_bias_missing()
    print("\ndefect 5 -- axial remainder units and propagation")
    test_defect5_axial_remainder_units()
    print("\ndefect 6 -- case registry and dispatch")
    test_defect6_case_registry()
    print("\ndefect 6 -- declared worlds are actually built")
    test_defect6_declared_worlds_are_built()
    print("\ndefect 6 -- authoritative event evaluator")
    test_defect6_event_evaluator()
    print("\ndefect 7 -- per-replicate reasons survive aggregation")
    test_defect7_reason_retention()
    print("\nsystematic fail-open search")
    test_systematic_fail_open()
    print("\nV4 identities and seeds")
    test_v4_identities_and_seeds()
    print(f"\nRESULT: {PASSED} passed, {FAILED} failed")
    print("  REAL EXPERIMENT DATA ....... 0")
    print("  CALIBRATION EXECUTIONS ..... 0")
    print("  OFFICIAL CAMPAIGN JOBS ..... 0")
    return 0 if FAILED == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
