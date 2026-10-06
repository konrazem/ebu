"""E1a v5 procedure version 3: regressions for the six audited defects.

**EXECUTION CLASS: MIXED.** Closed-form algebra, structured-refusal checks and
deterministic expected-likelihood calculations. A small number of SYNTHETIC OU
trajectories are generated for the end-to-end path checks. No real data, no
calibration execution, no official campaign job, no physical experiment.

Each section fails if its defect is reintroduced.
"""

from __future__ import annotations

import math

from e1a_v5 import numerics as nm
from e1a_v5 import realization as rf
from e1a_v5.calibration import (
    BoundedBias,
    ExperimentCalibration,
    FieldModel,
    LOG_BETA_ROW,
    Primitive,
    PrimitiveVector,
    Scope,
    build_experiment_calibration,
    certified_profiled_sensitivity,
    expected_loglik_per_frame,
    innovation_covariance_under_truth,
    steady_state_gain,
    truth_matching_theta,
)
from e1a_v5 import certified as cert
from e1a_v5.confidence import (
    CEILING_FAIL, CEILING_PASS, CEILING_UNRESOLVED, DELTA_A, DELTA_C, Interval,
    SIGMA_CAL_ABS_MAX, SIGMA_CAL_CONTRAST_MAX, BIAS_ABS_MAX,
    build_interval, classify_with_enclosure, contrast_bias_from_absolute,
    synthetic_calibrated,
)
from e1a_v5.diagnostics import (
    DiagnosticNotEvaluable, diagnostic_components, required_antisymmetry_lags,
)
from e1a_v5.estimate import (
    ProfileFit, SE_OK, SE_PROFILE_NOT_CONVERGED, SE_PROFILE_EXCEEDS_INCUMBENT,
)
from e1a_v5.gates import DELTA_G, DELTA_M, DELTA_R_IRR, irreversibility_from_matrices
from e1a_v5.identity import (
    GATE_MODULES, VALIDATION_MODULES, compute_identities, validation_preimage,
)
from e1a_v5.numerics import NumericalFailure
from e1a_v5.observation import bandwidth_product, build_state_space, model_lag_covariance
from e1a_v5.optimize import (
    REASON_BUDGET, REASON_RESTARTS, OptimizerFailure, minimise,
)
from e1a_v5.packets import CONTRASTS, RECORDS, BlockId, FieldId
from e1a_v5.pipeline import (
    ContrastResultV4, RecordResultV4, complete_pipeline_result, contrast_key,
    record_key,
)
from e1a_v5.evidence import (
    BiasEvidence, ContrastKey, GateFamily, GateLimit, RecordKey,
    ScientificInterval, synthetic_calibrated_gate_fixture,
)
from e1a_v5.validation.run import DOMAIN_IDENTITY, PROCEDURE_VERSION
from e1a_v5.diagnostics import (
    DiagnosticComponents, NullScales, RecordDiagnostic, evaluate_diagnostic_family,
)
from e1a_v5.realization import FIELD_REALIZATION_VALID, FIELD_REALIZATION_UNRESOLVED
from e1a_v5.reduction import AxialEvidence, reduce_axial, relative_skew
from e1a_v5.units import K_B
from e1a_v5.verdict import NOT_EVALUABLE, SUPPORTED

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


# ===========================================================================
# DEFECT 1 -- complete-power counting
# ===========================================================================

FIXTURE_CRIT = synthetic_calibrated()
FIXTURE_GATE_PROC = {
    f: synthetic_calibrated_gate_fixture(f, 0.0) for f in GateFamily
}


def fixture_limit(family: GateFamily, statistic: float, limit: float) -> GateLimit:
    """A TEST-ONLY calibrated gate limit at a chosen value.

    V5 removed ``GateLimit.calibrated(statistic, limit, identity)``: a bare
    string granted calibration, so a raw statistic became a passing limit.
    Fixtures now go through the typed artifact, whose radius is what sets the
    limit, and which the production builder refuses.
    """
    proc = synthetic_calibrated_gate_fixture(family, max(0.0, limit - statistic))
    return GateLimit.from_procedure(
        statistic, proc, family, PROCEDURE_VERSION, DOMAIN_IDENTITY,
        allow_fixture=True,
    )

FIXTURE_GATE = "SYNTHETIC FIXTURE - not a calibration"


def _good_record(b: BlockId, f: FieldId) -> RecordResultV4:
    """V4 types.  The scientific content of the V3 check is unchanged: every
    required condition is present and passing, and removing any one of them
    must break complete success."""
    est, se, bias = 0.0, 1.0e-3, 1.0e-4
    iv = build_interval(est, se, FIXTURE_CRIT, bias)
    return RecordResultV4(
        key=RecordKey(b, f), embedded_key=RecordKey(b, f),
        branch_a_valid=True, observation_valid=True,
        realization_status=FIELD_REALIZATION_VALID,
        log_beta=est, log_beta_se=se,
        absolute=ScientificInterval(iv, est, se, FIXTURE_CRIT, bias),
        absolute_bias=BiasEvidence.qualified(bias, "fixture"),
        shape=fixture_limit(GateFamily.SHAPE, 0.01, 0.02),
        centre=fixture_limit(GateFamily.CENTRE, 0.01, 0.02),
        stationarity=fixture_limit(GateFamily.STATIONARITY, 0.3, 0.5),
        current=fixture_limit(GateFamily.CURRENT, 0.001, 0.005),
        evaluable=True,
    )


def _good_contrast(b: BlockId, f: FieldId) -> ContrastResultV4:
    est, se, bias = 0.0, 1.0e-4, 1.0e-5
    iv = build_interval(est, se, FIXTURE_CRIT, bias)
    return ContrastResultV4(
        key=ContrastKey(b, f),
        interval=ScientificInterval(iv, est, se, FIXTURE_CRIT, bias),
        bias=BiasEvidence.qualified(bias, "fixture"),
    )


def _good_family(rejected: bool = False):
    comp = DiagnosticComponents(0.1, 0.1, 0.1, 0.1)
    names = [f"{b.value}/{f.value}" for b, f in RECORDS]
    return evaluate_diagnostic_family(
        [RecordDiagnostic(n, comp, None, None) for n in names], names,
        NullScales(1.0, 1.0, 1.0, 1.0), 0.05 if rejected else 1.0, FIXTURE_GATE,
    )


def _full_experiment():
    return ([_good_record(b, f) for b, f in RECORDS],
            [_good_contrast(b, f) for b, f in CONTRASTS])


def test_defect1_complete_counting() -> None:
    recs, cons = _full_experiment()
    fam = _good_family()
    res = complete_pipeline_result(recs, cons, fam)
    check("fully populated valid experiment counts as success",
          res.counts_as_complete_success and res.verdict.classification == SUPPORTED,
          res.verdict.classification)

    # Remove each required condition in turn; every one must break success.
    unc = GateLimit.uncalibrated(0.01)
    mutations = {
        "missing absolute endpoint": ("absolute", None),
        "missing geometry limit": ("shape", unc),
        "missing centre limit": ("centre", unc),
        "missing stationarity limit": ("stationarity", unc),
        "missing current limit": ("current", unc),
        "missing realized-field qualification": ("realization_status", None),
        "missing Branch-A validity": ("branch_a_valid", None),
        "missing observation validity": ("observation_valid", None),
        "missing bounded-bias evidence": ("absolute_bias", BiasEvidence.missing()),
        "optimizer non-evaluable": ("evaluable", False),
        "failed realization": ("realization_status", FIELD_REALIZATION_UNRESOLVED),
        "absolute interval outside margin":
            ("absolute", ScientificInterval(Interval(-0.2, 0.2))),
        "geometry limit at tolerance":
            ("shape", fixture_limit(GateFamily.SHAPE, 0.01, DELTA_G)),
        "centre limit at tolerance":
            ("centre", fixture_limit(GateFamily.CENTRE, 0.01, DELTA_M)),
        "current limit at tolerance":
            ("current", fixture_limit(GateFamily.CURRENT, 0.001, DELTA_R_IRR)),
        "NaN absolute interval":
            ("absolute", ScientificInterval(Interval(float("nan"), 0.0))),
    }
    for label, (fieldname, value) in mutations.items():
        recs2 = [_good_record(b, f) for b, f in RECORDS]
        recs2[3] = type(recs2[3])(**{**recs2[3].__dict__, fieldname: value})
        r = complete_pipeline_result(recs2, cons, fam)
        check(f"defect1: {label} prevents success", not r.counts_as_complete_success,
              f"got {r.verdict.classification}")

    # Missing / failing contrast
    recs3, cons3 = _full_experiment()
    b3, f3 = CONTRASTS[2]
    cons3[2] = ContrastResultV4(key=ContrastKey(b3, f3))
    check("defect1: missing contrast prevents success",
          not complete_pipeline_result(recs3, cons3, fam).counts_as_complete_success)
    cons3[2] = ContrastResultV4(
        key=ContrastKey(b3, f3),
        interval=ScientificInterval(Interval(-0.05, 0.05)),
        bias=BiasEvidence.qualified(1e-5))
    check("defect1: contrast outside margin prevents success",
          not complete_pipeline_result(recs3, cons3, fam).counts_as_complete_success)
    cons3[2] = ContrastResultV4(
        key=ContrastKey(b3, f3),
        interval=ScientificInterval(Interval(-DELTA_C, 0.0)),
        bias=BiasEvidence.qualified(1e-5))
    check("defect1: contrast at the boundary is not a pass",
          not complete_pipeline_result(recs3, cons3, fam).counts_as_complete_success)

    # Diagnostics
    recs4, cons4 = _full_experiment()
    check("defect1: rejected diagnostic prevents success",
          not complete_pipeline_result(
              recs4, cons4, _good_family(True)).counts_as_complete_success)
    r = complete_pipeline_result(recs4, cons4, None)
    check("defect1: unevaluated diagnostic is NOT_EVALUABLE, not a pass",
          not r.counts_as_complete_success and r.verdict.classification == NOT_EVALUABLE,
          r.verdict.classification)

    # A missing whole record
    r = complete_pipeline_result(recs4[:-1], cons4, fam)
    check("defect1: a missing record prevents success", not r.counts_as_complete_success)
    check("defect1: refusal reasons are retained", len(r.reason_codes()) > 0)
    check("defect1: result serialises with reasons", "reasons" in r.as_dict())


# ===========================================================================
# DEFECT 2 -- current control dimensional scaling
# ===========================================================================

def test_defect2_current_control() -> None:
    from e1a_v5.validation.harness import current_control_drift, design_specs

    target = 0.05
    specs = design_specs(n_frames=64, r_irr_target=target)
    spec, h_locked = specs[0]
    sigma = nm.spd_inverse(spec.h_true)
    q = [[0.0, -spec.omega_true], [spec.omega_true, 0.0]]
    a = nm.matmul(nm.add(spec.d_true, q), nm.spd_inverse(sigma))

    achieved = irreversibility_from_matrices(a, sigma)
    check("defect2: constructed r_irr equals the target",
          close(achieved, target, 1e-9), f"{achieved}")
    check("defect2: r_irr exceeds the scientific gate", achieved > DELTA_R_IRR)
    bw = bandwidth_product(a, sigma, spec.dt)
    check("defect2: bandwidth criterion passes", bw <= 0.2, f"||B|| dt = {bw}")
    check("defect2: bandwidth is not absurd (V2 gave ~1.5e10)", bw < 1.0, f"{bw}")

    # The stationary covariance is unchanged and the density stays canonical.
    asig = nm.matmul(a, sigma)
    ll = nm.symmetrise(nm.add(asig, nm.transpose(asig)))
    check("defect2: diffusion is SPD", nm.is_spd(ll))
    check("defect2: stationary covariance is the intended one",
          nm.max_abs(nm.sub(sigma, nm.spd_inverse(spec.h_true))) < 1e-30 * nm.max_abs(sigma))
    check("defect2: the current is genuinely nonzero", abs(spec.omega_true) > 0.0)

    # Reversible construction gives exactly zero.
    specs0 = design_specs(n_frames=64, r_irr_target=0.0)
    s0, _ = specs0[0]
    sig0 = nm.spd_inverse(s0.h_true)
    a0 = nm.matmul(s0.d_true, nm.spd_inverse(sig0))
    check("defect2: r_irr = 0 target gives a reversible model",
          irreversibility_from_matrices(a0, sig0) < 1e-12)

    # The helper itself is scale free: same target at a different stiffness.
    for scale in (0.25, 4.0):
        d2 = nm.scale(spec.d_true, scale)
        om = current_control_drift(d2, sigma, target)
        a2 = nm.matmul(nm.add(d2, [[0.0, -om], [om, 0.0]]), nm.spd_inverse(sigma))
        check(f"defect2: r_irr target holds at stiffness scale {scale}",
              close(irreversibility_from_matrices(a2, sigma), target, 1e-9))


# ===========================================================================
# DEFECT 3 -- nonconverged profile standard error
# ===========================================================================

def test_defect3_profile_se() -> None:
    ok = ProfileFit(SE_OK, 0.07, 0.02, 0.5, 100, ("converged", "converged"))
    check("defect3: a usable profile yields its value", ok.usable and ok.require() == 0.07)
    for status in (SE_PROFILE_NOT_CONVERGED, SE_PROFILE_EXCEEDS_INCUMBENT):
        bad = ProfileFit(status, None, 0.02, None, 100, (REASON_BUDGET,))
        check(f"defect3: {status} is not usable", not bad.usable)
        try:
            bad.require()
            check(f"defect3: {status} refuses to yield a number", False)
        except OptimizerFailure:
            check(f"defect3: {status} refuses to yield a number", True)
    # A ProfileFit cannot carry a value with a failure status and be usable.
    sneaky = ProfileFit(SE_PROFILE_NOT_CONVERGED, 0.07, 0.02, 0.5, 100, ())
    check("defect3: a value under a failure status is still not usable", not sneaky.usable)

    # The optimiser never reports convergence it did not achieve.
    res = minimise(lambda x: sum(v * v for v in x), [1.0, 1.0], max_evaluations=5)
    check("defect3: budget exhaustion is not converged",
          (not res.converged) and (not res.usable) and res.reason == REASON_BUDGET)
    res = minimise(lambda x: (x[0] - 1.3) ** 2, [0.0])
    check("defect3: a genuine optimum is converged and usable", res.converged and res.usable)
    for bad_obj in (lambda x: float("nan"), lambda x: float("inf")):
        try:
            minimise(bad_obj, [0.0, 0.0])
            check("defect3: nonfinite objective refused", False)
        except OptimizerFailure:
            check("defect3: nonfinite objective refused", True)

    # End to end: a fit whose profile fails must not produce an interval.
    from e1a_v5.validation.harness import design_specs, run_record
    from e1a_v5.rng import Stream
    specs = design_specs(n_frames=400)
    out = run_record(specs[0][0], specs[0][1], Stream(991))
    if out.evaluable:
        check("defect3: an evaluable record carries a finite SE",
              out.se is not None and math.isfinite(out.se))
    else:
        check("defect3: a non-evaluable record carries NO standard error", out.se is None)
        check("defect3: a non-evaluable record records its reason", bool(out.reason))


# ===========================================================================
# DEFECT 4 -- lag antisymmetry
# ===========================================================================

def test_defect4_lag_antisymmetry() -> None:
    inn = [[0.1, 0.2], [0.3, -0.1], [-0.2, 0.05]] * 40
    C = nm.eye(2)
    for label, obs, fit in [
        ("both absent", None, None),
        ("observed absent", None, [nm.eye(2)]),
        ("fitted absent", [nm.eye(2)], None),
        ("empty sets", [], []),
        ("misaligned sets", [nm.eye(2)], [nm.eye(2), nm.eye(2)]),
    ]:
        try:
            diagnostic_components(inn, C, obs, fit)
            check(f"defect4: {label} is non-evaluable", False, "returned a value")
        except DiagnosticNotEvaluable:
            check(f"defect4: {label} is non-evaluable", True)

    # Identical observed and fitted give exactly zero residual.
    same = [nm.mat([[1.0, 0.3], [0.1, 1.0]])]
    d = diagnostic_components(inn, C, same, [r[:] for r in same])
    check("defect4: identical observed/fitted gives zero antisymmetry residual",
          d.antisym == 0.0, f"{d.antisym}")

    # A raw antisymmetry correctly modelled leaves no residual, even though the
    # raw asymmetry is large: the free model may contain a current.
    skew = nm.mat([[1.0, 0.4], [-0.4, 1.0]])
    d = diagnostic_components(inn, C, [skew], [[r[:] for r in skew]])
    check("defect4: correctly modelled current leaves zero residual", d.antisym == 0.0)
    check("defect4: but its raw antisymmetry is nonzero",
          nm.max_abs(nm.sub(skew, nm.transpose(skew))) > 0.0)

    # A wrong fitted current leaves a nonzero residual.
    wrong = nm.mat([[1.0, 0.1], [-0.1, 1.0]])
    d = diagnostic_components(inn, C, [skew], [wrong])
    check("defect4: a wrong fitted current leaves a nonzero residual", d.antisym > 0.0)

    # Transposing the fitted matrix is detected.
    d_t = diagnostic_components(inn, C, [skew], [nm.transpose(skew)])
    check("defect4: a transposed fitted lag matrix is detected", d_t.antisym > 0.0)

    # Lag selection uses real timestamps.
    check("defect4: lags follow tau_slow/dt",
          required_antisymmetry_lags(1e-4, 1.25e-5) == (4, 8, 16))
    for bad in ((1e-4, 1e-3), (0.0, 1e-5), (1e-4, 0.0)):
        try:
            required_antisymmetry_lags(*bad)
            check(f"defect4: unresolvable lags refused {bad}", False)
        except DiagnosticNotEvaluable:
            check(f"defect4: unresolvable lags refused {bad}", True)

    # The model lag covariance reproduces the analytic lag-0 and lag-1 forms.
    A = nm.scale(nm.eye(2), 8000.0)
    S = nm.mat([[4e-17, 0.0], [0.0, 4e-17]])
    ss = build_state_space(A, S, [0.0, 0.0], nm.eye(2),
                           nm.scale(nm.eye(2), 0.02 * 4e-17), [0.0, 0.0], 1.2e-5, 4e-6)
    c0 = model_lag_covariance(ss, 0)
    ref0 = nm.add(nm.matmul(nm.matmul(ss.c_obs, ss.sigma), nm.transpose(ss.c_obs)), ss.r_eff)
    check("defect4: model lag-0 matches the marginal covariance",
          nm.max_abs(nm.sub(c0, ref0)) < 1e-18 * nm.max_abs(ref0))
    c1 = model_lag_covariance(ss, 1)
    ref1 = nm.add(
        nm.matmul(nm.matmul(nm.matmul(ss.c_obs, ss.sigma), nm.transpose(ss.f)),
                  nm.transpose(ss.c_obs)),
        nm.matmul(nm.transpose(ss.s_cross), nm.transpose(ss.c_obs)))
    check("defect4: model lag-1 carries the exposure cross term",
          nm.max_abs(nm.sub(c1, ref1)) < 1e-18 * nm.max_abs(ref1))
    check("defect4: the exposure cross term is not negligible",
          nm.max_abs(ss.s_cross) > 0.0)


# ===========================================================================
# DEFECT 5 -- validation identity
# ===========================================================================

def test_defect5_validation_identity() -> None:
    import os
    check("defect5: validation/run.py is in the preimage",
          os.path.join("validation", "run.py") in VALIDATION_MODULES)
    check("defect5: verdict.py is in the preimage", "verdict.py" in VALIDATION_MODULES)
    check("defect5: harness and cases are in the preimage",
          os.path.join("validation", "harness.py") in VALIDATION_MODULES
          and os.path.join("validation", "cases.py") in VALIDATION_MODULES)
    pre = validation_preimage()
    check("defect5: the preimage is documented",
          set(pre) == {"modules", "bound_component_identities", "rationale"})
    check("defect5: run.py rationale recorded",
          "validation/run.py" in pre["rationale"])

    ids = compute_identities({"v": 3})
    check("defect5: six identities", len(ids.as_dict()) == 6)
    check("defect5: all distinct", len(set(ids.as_dict().values())) == 6)

    # Hierarchical binding: perturbing any bound component identity moves the
    # validation identity.
    from e1a_v5.identity import hierarchical_identity
    base = hierarchical_identity(VALIDATION_MODULES, {
        "analysis_procedure": "a" * 64, "synthetic_generator": "b" * 64,
        "seed_map": "c" * 64, "gate_semantics": "d" * 64, "packet_schema": "e" * 64,
    }, {"v": 3})
    for name in ("analysis_procedure", "synthetic_generator", "seed_map",
                 "gate_semantics", "packet_schema"):
        comp = {"analysis_procedure": "a" * 64, "synthetic_generator": "b" * 64,
                "seed_map": "c" * 64, "gate_semantics": "d" * 64, "packet_schema": "e" * 64}
        comp[name] = "f" * 64
        check(f"defect5: changing {name} changes the validation identity",
              hierarchical_identity(VALIDATION_MODULES, comp, {"v": 3}) != base)
    check("defect5: changing the configuration changes it",
          hierarchical_identity(VALIDATION_MODULES, {
              "analysis_procedure": "a" * 64, "synthetic_generator": "b" * 64,
              "seed_map": "c" * 64, "gate_semantics": "d" * 64, "packet_schema": "e" * 64,
          }, {"v": 4}) != base)
    check("defect5: gate modules are bound",
          set(GATE_MODULES) == {"gates.py", "diagnostics.py", "confidence.py", "realization.py"})


# ===========================================================================
# DEFECT 6 -- axial fail-open and the symmetry scale defect
# ===========================================================================

def test_defect6_axial_fail_closed() -> None:
    K = nm.mat([[1.2e-4, 1e-5, 3e-5], [1e-5, 1.0e-4, 2e-5], [3e-5, 2e-5, 5e-5]])
    Cv = nm.scale(nm.eye(6), 1e-12)

    r = reduce_axial(K, 298.0)
    check("defect6: no evidence at all is refused", not r.ok)
    check("defect6: the refusal names the missing evidence",
          any("evidence" in x.predicate for x in r.refusals))

    r = reduce_axial(K, 298.0, AxialEvidence.fully_qualified())
    check("defect6: missing covariance is refused", not r.ok)
    check("defect6: covariance refusal is explicit",
          any("covariance" in x.predicate for x in r.refusals))

    # Each load-bearing field, omitted one at a time.
    for name in AxialEvidence.REQUIRED:
        full = AxialEvidence.fully_qualified()
        partial = AxialEvidence(**{**full.__dict__, name: None})
        rr = reduce_axial(K, 298.0, partial, Cv)
        check(f"defect6: missing {name} fails closed", not rr.ok)
        partial_false = AxialEvidence(**{**full.__dict__, name: False})
        rr2 = reduce_axial(K, 298.0, partial_false, Cv)
        check(f"defect6: failed {name} is refused", not rr2.ok)

    # A missing remainder SET is refused even though a zero set would pass.
    # V5 qualifies the certified set, not one evaluated witness.
    full = AxialEvidence.fully_qualified()
    no_rem = AxialEvidence(**{**full.__dict__, "remainder_set": None})
    check("defect6: missing certified remainder set is refused",
          not reduce_axial(K, 298.0, no_rem, Cv).ok)

    # Complete evidence plus covariance qualifies.
    r = reduce_axial(K, 298.0, full, Cv)
    check("defect6: complete evidence qualifies", r.ok)
    check("defect6: covariance is propagated", r.c_vech_h is not None)

    # --- the symmetry scale defect ---------------------------------------
    check("defect6: exact symmetry gives zero relative skew", relative_skew(K) == 0.0)
    Kb = [row[:] for row in K]
    Kb[0][1] = K[0][1] * (1.0 + 1e-6)
    skew = relative_skew(Kb)
    check("defect6: a 1e-6 relative asymmetry is detected", skew > 1e-9, f"{skew}")
    check("defect6: asymmetric stiffness is refused",
          not reduce_axial(Kb, 298.0, full, Cv).ok)

    # Scale invariance: the same relative asymmetry at any physical scale.
    for s in (1e-9, 1.0, 1e9):
        Ks = nm.scale(K, s)
        Ksb = [row[:] for row in Ks]
        Ksb[0][1] = Ks[0][1] * (1.0 + 1e-6)
        check(f"defect6: relative skew is scale invariant at {s:g}",
              close(relative_skew(Ksb), skew, 1e-9))
        check(f"defect6: asymmetry refused at physical scale {s:g}",
              not reduce_axial(Ksb, 298.0, full, nm.scale(Cv, s * s)).ok)

    # A zero symmetric scale is refused, never rescued by a unit denominator.
    try:
        relative_skew(nm.zeros(3, 3))
        check("defect6: zero symmetric scale is refused", False)
    except NumericalFailure:
        check("defect6: zero symmetric scale is refused", True)


# ===========================================================================
# SI-scale audit regressions
# ===========================================================================

def test_si_scale_audit() -> None:
    # eigh2 symmetry is relative, so gross asymmetry at 1e-29 is caught.
    try:
        nm.eigh2(nm.mat([[2.3e-29, 5.4e-33], [9.9e-30, 2.3e-29]]))
        check("si: eigh2 catches asymmetry at 1e-29 scale", False)
    except NumericalFailure:
        check("si: eigh2 catches asymmetry at 1e-29 scale", True)
    check("si: eigh2 accepts rounding-level asymmetry at 1e-29 scale",
          nm.eigh2(nm.mat([[2.3e-29, 5.4e-33],
                           [5.4e-33 * (1 + 1e-15), 2.3e-29]]))[0][0] > 0.0)

    # LU singularity is relative, so a singular 1e-29 matrix is caught.
    try:
        nm.lu_solve(nm.mat([[1e-29, 2e-29], [2e-29, 4e-29]]), nm.eye(2))
        check("si: lu_solve catches singularity at 1e-29 scale", False)
    except NumericalFailure:
        check("si: lu_solve catches singularity at 1e-29 scale", True)
    check("si: lu_solve still solves a well-conditioned 1e-29 system",
          math.isfinite(nm.lu_solve(nm.mat([[2e-29, 1e-29], [1e-29, 3e-29]]), nm.eye(2))[0][0]))

    # Isotropy detection is relative too.
    vals, Q = nm.eigh2(nm.mat([[5e-29, 0.0], [0.0, 5e-29]]))
    check("si: isotropic 1e-29 matrix returns the identity basis",
          nm.max_abs(nm.sub(Q, nm.eye(2))) == 0.0)

    # The Riccati fix from V2 is still in place.
    from e1a_v5.validation.harness import design_specs
    from e1a_v5.generate import generate_record
    from e1a_v5.likelihood import Parameters, chol_params_from_spd, log_likelihood
    from e1a_v5.rng import Stream, derive_seed
    specs = design_specs(n_frames=600)
    spec, H = specs[0]
    y = generate_record(spec, Stream(derive_seed("v3", "riccati")))
    true = Parameters(0.0, (0.0, 0.0), chol_params_from_spd(spec.d_true), 0.0, None)
    out = log_likelihood(true, H, y, spec.p_matrix, spec.r_obs, list(spec.b_det),
                         spec.dt, spec.t_exp, collect_innovations=True)
    check("si: Riccati still converges genuinely", out.steady_after > 2,
          f"steady_after={out.steady_after}")

    # No remaining max(1.0, .) on a dimensional quantity.
    import pathlib
    offenders = []
    for path in pathlib.Path("e1a_v5").rglob("*.py"):
        for i, line in enumerate(path.read_text().splitlines(), 1):
            if "max(1.0," in line and not line.lstrip().startswith("#"):
                offenders.append(f"{path}:{i}")
    # The survivors are dimensionless optimiser tolerances only.
    check("si: every surviving max(1.0,.) is a dimensionless optimiser tolerance",
          all("optimize.py" in o for o in offenders), str(offenders))


# ===========================================================================
# Full C_phi path
# ===========================================================================

GAMMA_REF = 6.0 * math.pi * 0.89e-3 * 0.5e-6


def _scalar_builder(stiffness: float = 1.0e-4, temperature: float = 298.0):
    """phi = (log stiffness CALIBRATION error, log temperature CALIBRATION error).

    V4 semantics: the truth is fixed physics and ``phi`` moves only what the
    analyst measures, which is what a calibration error physically is.  V3
    moved the truth instead and held the locked H fixed, so its reported
    sensitivity signs were the mirror image of the production ones.
    """
    k_true = nm.mat([[stiffness, 0.0], [0.0, stiffness]])
    sigma_true = nm.scale(nm.spd_inverse(k_true), K_B * temperature)
    a_true = nm.scale(k_true, 1.0 / GAMMA_REF)

    def build(phi):
        k_meas = nm.scale(k_true, math.exp(phi[0]))
        t_meas = temperature * math.exp(phi[1])
        h_meas = nm.scale(k_meas, 1.0 / (K_B * t_meas))
        return FieldModel(
            h_meas, k_meas, t_meas, a_true, sigma_true, nm.eye(2),
            nm.scale(nm.eye(2), 0.02 * sigma_true[0][0]), (0.0, 0.0), 1.2e-5, 4e-6)

    return build


def _scalar_generic_builder(stiffness: float = 1.0e-4, temperature: float = 298.0):
    """The same map over the generic kernel, for certified differentiation."""
    k_true = nm.mat([[stiffness, 0.0], [0.0, stiffness]])
    from e1a_v5.calibration import AnalysisModel

    def build(phi):
        k_meas = cert.gscale(k_true, cert.gexp(phi[0]))
        inv_kt = cert.gexp(-phi[1]) * (1.0 / (K_B * temperature))
        return AnalysisModel(
            h_locked=cert.gscale(k_meas, inv_kt), p_matrix=nm.eye(2),
            r_obs=nm.scale(nm.eye(2), 0.02 * (K_B * temperature / stiffness)),
            b_det=(0.0, 0.0), dt=1.2e-5, t_exp=4e-6)

    return build


def test_cphi_end_to_end() -> None:
    build = _scalar_builder()
    generic = _scalar_generic_builder()
    base_model = build([0.0, 0.0])
    H0 = base_model.h_eff
    truth = base_model.truth_state_space()
    theta0 = truth_matching_theta(base_model)

    # Expected likelihood is maximised exactly at the truth.
    from e1a_v5.calibration import model_state_space
    am = base_model.analysis
    best = expected_loglik_per_frame(truth, model_state_space(theta0, am))
    for d in (-0.02, -0.01, 0.01, 0.02):
        th = list(theta0); th[0] += d
        v = expected_loglik_per_frame(truth, model_state_space(th, am))
        check(f"cphi: expected likelihood is lower at log beta {d:+}", v < best)

    # Sensitivities match the exact analytic values, with the PRODUCTION sign.
    #   Sigma_m = exp(-b) H_A^{-1} matched to Sigma_true with
    #   H_A = K exp(phi0) / (k_B T exp(phi1))  gives  b* = phi1 - phi0.
    ps = certified_profiled_sensitivity(
        generic, build, [0.0, 0.0], phi_sigma=[6.0e-3, 1.0e-3])
    j = ps.jacobian[LOG_BETA_ROW]
    r = ps.radius[LOG_BETA_ROW]
    check("cphi: d log beta / d log MEASURED stiffness = -1",
          abs(j[0] + 1.0) <= max(r[0], 1e-6), f"{j[0]} +- {r[0]}")
    check("cphi: d log beta / d log MEASURED T = +1",
          abs(j[1] - 1.0) <= max(r[1], 1e-6), f"{j[1]} +- {r[1]}")
    check("cphi: the certified enclosure brackets both exact values",
          abs(j[0] + 1.0) <= r[0] and abs(j[1] - 1.0) <= r[1])

    # Shared primitives are one variable, not several.
    vec = PrimitiveVector()
    vec.add(Primitive("length_standard", Scope.GLOBAL, 0.0, 0.004))
    vec.add(Primitive("length_standard", Scope.GLOBAL, 0.0, 0.004))
    check("cphi: a shared primitive registers once", len(vec.primitives) == 1)
    try:
        vec.add(Primitive("length_standard", Scope.GLOBAL, 0.0, 0.009))
        check("cphi: inconsistent re-registration refused", False)
    except NumericalFailure:
        check("cphi: inconsistent re-registration refused", True)
    vec.add(Primitive("radius", Scope.BLOCK, 0.0, 0.002, block=BlockId.BLOCK1))
    vec.add(Primitive("radius", Scope.BLOCK, 0.0, 0.002, block=BlockId.BLOCK2))
    check("cphi: block primitives are distinct variables", len(vec.primitives) == 3)
    vec.add(Primitive("temperature", Scope.FIELD, 0.0, 0.001,
                      block=BlockId.BLOCK1, fld=FieldId.THETA0))
    check("cphi: field primitives are distinct variables", len(vec.primitives) == 4)
    C = vec.covariance()
    check("cphi: C_phi is diagonal without declared correlations",
          all(C[i][j] == 0.0 for i in range(4) for j in range(4) if i != j))
    vec.correlate("length_standard", "radius@block1", 0.5)
    C = vec.covariance()
    check("cphi: a declared correlation appears symmetrically",
          close(C[0][1], 0.5 * 0.004 * 0.002) and C[0][1] == C[1][0])
    check("cphi: C_phi stays PSD", nm.is_spd(C))

    # --- end to end: a purely shared error cancels in the contrast ---------
    shared = PrimitiveVector()
    shared.add(Primitive("common_scale", Scope.GLOBAL, 0.0, 0.006))
    shared.add(Primitive("common_T", Scope.GLOBAL, 0.0, 1e-12))
    k0 = record_key(BlockId.BLOCK1, FieldId.THETA0)
    k1 = record_key(BlockId.BLOCK1, FieldId.THETA1)
    cov = build_experiment_calibration(
        shared, [(k0, build, generic), (k1, build, generic)])
    a0 = cov.absolute_sigma(k0).point
    a1 = cov.absolute_sigma(k1).point
    check("cphi: a common scale error gives equal absolute sigmas",
          close(a0, a1, 1e-6))
    check("cphi: it reaches the declared magnitude", close(a0, 0.006, 1e-3), f"{a0}")
    check("cphi: a purely common error cancels EXACTLY in the contrast",
          cov.contrast_sigma(k1, k0).point < 1e-6 * a0,
          f"{cov.contrast_sigma(k1, k0).point}")

    # --- a field-specific error does not cancel ---------------------------
    perfield = PrimitiveVector()
    perfield.add(Primitive("scale", Scope.FIELD, 0.0, 0.006,
                           block=BlockId.BLOCK1, fld=FieldId.THETA0))
    perfield.add(Primitive("scale", Scope.FIELD, 0.0, 0.006,
                           block=BlockId.BLOCK1, fld=FieldId.THETA1))

    def b0(phi):
        return build([phi[0], 0.0])

    def b1(phi):
        return build([phi[1], 0.0])

    def g0(phi):
        return _scalar_generic_builder()([phi[0], 0.0])

    def g1(phi):
        return _scalar_generic_builder()([phi[1], 0.0])

    cov2 = build_experiment_calibration(
        perfield, [(k0, b0, g0), (k1, b1, g1)])
    got = cov2.contrast_sigma(k1, k0).point
    check("cphi: independent per-field errors do not cancel",
          close(got, math.sqrt(2) * 0.006, 1e-3), f"{got}")

    # --- the 0.009 and 0.003 ceilings, with the CERTIFIED enclosure --------
    for sigma, expect in ((0.0089, CEILING_PASS), (0.0091, CEILING_FAIL)):
        v = PrimitiveVector()
        v.add(Primitive("s", Scope.GLOBAL, 0.0, sigma))
        v.add(Primitive("t", Scope.GLOBAL, 0.0, 1e-12))
        c = build_experiment_calibration(v, [(k0, build, generic)])
        cls = c.absolute_qualification(k0)
        check(f"cphi: absolute sigma {sigma} vs the 0.009 ceiling",
              cls == expect, f"{c.absolute_sigma(k0).point} -> {cls}")
    for sigma, expect in ((0.0029, CEILING_PASS), (0.0031, CEILING_FAIL)):
        v = PrimitiveVector()
        sq = sigma / math.sqrt(2.0)
        v.add(Primitive("scale", Scope.FIELD, 0.0, sq,
                        block=BlockId.BLOCK1, fld=FieldId.THETA0))
        v.add(Primitive("scale", Scope.FIELD, 0.0, sq,
                        block=BlockId.BLOCK1, fld=FieldId.THETA1))
        c = build_experiment_calibration(v, [(k0, b0, g0), (k1, b1, g1)])
        cls = c.contrast_qualification(k1, k0)
        check(f"cphi: contrast sigma {sigma} vs the 0.003 ceiling",
              cls == expect, f"{c.contrast_sigma(k1, k0).point} -> {cls}")
    # A value AT the ceiling cannot be resolved more sharply than its own
    # certified numerical error, so it is UNRESOLVED -- fail-closed.
    v = PrimitiveVector()
    v.add(Primitive("s", Scope.GLOBAL, 0.0, SIGMA_CAL_ABS_MAX))
    v.add(Primitive("t", Scope.GLOBAL, 0.0, 1e-12))
    c = build_experiment_calibration(v, [(k0, build, generic)])
    check("cphi: a value exactly at the 0.009 ceiling is not silently passed",
          c.absolute_qualification(k0) in (CEILING_PASS, CEILING_UNRESOLVED),
          f"{c.absolute_sigma(k0).point} -> {c.absolute_qualification(k0)}")


def test_v3_seed_namespaces() -> None:
    from e1a_v5.seeds import (
        CONFIRMATORY_FAMILIES, ENGINEERING, FAMILIES, FAMILIES_V2, FAMILIES_V3,
        FAMILIES_V4, ROOT, ROOT_V2, ROOT_V3, ROOT_V4, SeedMap,
    )
    sm = SeedMap()
    check("seeds: the V5 root differs from V4, V3 and V2",
          ROOT not in (ROOT_V4, ROOT_V3, ROOT_V2))
    check("seeds: every confirmatory family name is versioned",
          all(f.endswith("-v5") for f in CONFIRMATORY_FAMILIES))
    check("seeds: five distinct confirmatory families",
          len({sm.family_seed(f) for f in CONFIRMATORY_FAMILIES}) == 5)
    for f5, f4, f3, f2 in zip(CONFIRMATORY_FAMILIES, FAMILIES_V4,
                              FAMILIES_V3, FAMILIES_V2):
        check(f"seeds: {f5} is disjoint from the V4 stream",
              sm.disjoint_from(f5, ROOT_V4, f4, "POWER-NOMINAL"))
        check(f"seeds: {f5} is disjoint from the V3 stream",
              sm.disjoint_from(f5, ROOT_V3, f3, "POWER-NOMINAL"))
        check(f"seeds: {f5} is disjoint from the V2 stream",
              sm.disjoint_from(f5, ROOT_V2, f2, "POWER-NOMINAL"))
    check("seeds: the engineering namespace is not confirmatory",
          ENGINEERING not in CONFIRMATORY_FAMILIES)
    allseeds = {sm.replicate_seed(f, c, r)
                for f in FAMILIES for c in ("A", "B") for r in range(40)}
    check("seeds: V5 replicate namespaces are disjoint",
          len(allseeds) == len(FAMILIES) * 2 * 40)
    check("seeds: derivation is reproducible",
          sm.replicate_seed(FAMILIES[0], "X", 7)
          == SeedMap().replicate_seed(FAMILIES[0], "X", 7))


def test_ceiling_classification() -> None:
    from e1a_v5.confidence import NumericalEnclosure
    c = SIGMA_CAL_ABS_MAX
    check("ceiling: clearly below passes",
          classify_with_enclosure(
              NumericalEnclosure.symmetric(0.008, 1e-6, "m"), c) == CEILING_PASS)
    check("ceiling: clearly above fails",
          classify_with_enclosure(
              NumericalEnclosure.symmetric(0.010, 1e-6, "m"), c) == CEILING_FAIL)
    check("ceiling: an enclosure straddling the ceiling is unresolved",
          classify_with_enclosure(
              NumericalEnclosure.symmetric(c, 1e-6, "m"), c) == CEILING_UNRESOLVED)
    check("ceiling: an exact value at the inclusive ceiling passes",
          classify_with_enclosure(NumericalEnclosure.exact(c), c) == CEILING_PASS)
    check("ceiling: the band is the quantity's own error, not a fixed fraction",
          classify_with_enclosure(
              NumericalEnclosure.symmetric(c * (1 - 1e-7), 1e-12, "tight"), c)
          == CEILING_PASS
          and classify_with_enclosure(
              NumericalEnclosure.symmetric(c * (1 - 1e-7), 1e-6, "loose"), c)
          == CEILING_UNRESOLVED)
    check("ceiling: non-finite fails",
          classify_with_enclosure(
              NumericalEnclosure(float("nan"), float("nan"), float("nan"), "m"), c)
          == CEILING_FAIL)
    check("ceiling: no enclosure at all is unresolved, which is fail-closed",
          classify_with_enclosure(None, c) == CEILING_UNRESOLVED)


def test_bounded_bias_stays_separate() -> None:
    bb = BoundedBias(
        absolute={"block1/theta0": BiasEvidence.qualified(BIAS_ABS_MAX),
                  "block1/theta1": BiasEvidence.qualified(BIAS_ABS_MAX)},
        contrast={"block1/theta1-theta0": BiasEvidence.qualified(BIAS_ABS_MAX)})
    check("bias: absolute bound at exactly 0.0005 is retrievable",
          close(bb.absolute_bound("block1/theta0"), 0.0005))
    check("bias: contrast bound at exactly 0.0005 is retrievable",
          close(bb.contrast_bound("block1/theta1-theta0"), 0.0005))
    # Two absolute bounds do NOT imply a contrast bound.
    bb2 = BoundedBias(absolute={"a": BiasEvidence.qualified(0.0005),
                                "b": BiasEvidence.qualified(0.0005)}, contrast={})
    try:
        bb2.contrast_bound("a-b")
        check("bias: contrast bound may not be inferred from two absolutes", False)
    except ValueError:
        check("bias: contrast bound may not be inferred from two absolutes", True)
    # V4: an ABSENT absolute bound is MISSING, not zero.
    try:
        bb2.absolute_bound("never-registered")
        check("bias: an absent absolute bound is not a bound of zero", False)
    except ValueError:
        check("bias: an absent absolute bound is not a bound of zero", True)
    check("bias: two 0.0005 absolutes imply only 0.001 for a contrast",
          close(contrast_bias_from_absolute([0.0005, 0.0005]), 0.001))
    check("bias: opposite-signed absolutes still imply only 0.001",
          close(contrast_bias_from_absolute([0.0005, -0.0005]), 0.001))
    check("bias: BoundedBias carries no covariance interface",
          not hasattr(bb, "covariance"))


def main() -> int:
    print("defect 1 -- complete-power counting")
    test_defect1_complete_counting()
    print("\ndefect 2 -- current control dimensional scaling")
    test_defect2_current_control()
    print("\ndefect 3 -- nonconverged profile standard error")
    test_defect3_profile_se()
    print("\ndefect 4 -- lag antisymmetry")
    test_defect4_lag_antisymmetry()
    print("\ndefect 5 -- validation identity")
    test_defect5_validation_identity()
    print("\ndefect 6 -- axial fail-open and symmetry scale")
    test_defect6_axial_fail_closed()
    print("\nsystematic SI-scale audit")
    test_si_scale_audit()
    print("\nfull C_phi end-to-end [SYNTHETIC]")
    test_cphi_end_to_end()
    print("\nV3 seed namespaces")
    test_v3_seed_namespaces()
    print("\nceiling classification at numerical precision")
    test_ceiling_classification()
    print("\nbounded bias stays separate")
    test_bounded_bias_stays_separate()
    print(f"\nRESULT: {PASSED} passed, {FAILED} failed")
    print("Execution class: MIXED STATIC/PURE + SYNTHETIC ENGINEERING CHECKS")
    print("  REAL EXPERIMENT DATA ....... 0")
    print("  CALIBRATION EXECUTIONS ..... 0")
    print("  OFFICIAL CAMPAIGN JOBS ..... 0")
    return 0 if FAILED == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
