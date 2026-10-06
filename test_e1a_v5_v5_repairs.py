"""E1a v5 procedure version 5: regressions for the five audited V4 blockers.

**EXECUTION CLASS: MIXED.** Closed-form algebra, structured-refusal checks,
interval-arithmetic derivative certification and deterministic expected-
likelihood calculations.  A small number of SYNTHETIC trajectories are
generated for the end-to-end path checks, all from the ``engineering-v5``
namespace.  No real data, no calibration execution, no official campaign job,
no physical experiment.

Each section fails if its blocker is reintroduced.
"""

from __future__ import annotations

import math
import os

from e1a_v5 import certified as cert
from e1a_v5 import numerics as nm
from e1a_v5.calibration import (
    AnalysisModel,
    CertifiedSensitivity,
    FieldModel,
    LOG_BETA_ROW,
    N_THETA,
    THETA_NAMES,
    build_experiment_calibration,
    certified_profiled_sensitivity,
    expected_loglik_per_frame,
    truth_matching_theta,
)
from e1a_v5.certified import IHD, CertificationFailure
from e1a_v5.confidence import (
    BIAS_ABS_MAX,
    CEILING_FAIL,
    CEILING_PASS,
    CEILING_UNRESOLVED,
    CriticalValueStatus,
    NumericalEnclosure,
    SIGMA_CAL_ABS_MAX,
    SIGMA_CAL_CONTRAST_MAX,
    classify_with_enclosure,
    synthetic_calibrated,
)
from e1a_v5.evidence import (
    FIXTURE_NAMESPACE,
    GATE_FIXTURE_IN_PRODUCTION,
    GATE_NO_PROCEDURE,
    GATE_WRONG_DOMAIN,
    GATE_WRONG_FAMILY,
    GATE_WRONG_VERSION,
    CalibratedGateProcedure,
    GateFamily,
    GateLimit,
    synthetic_calibrated_gate_fixture,
)
from e1a_v5.gates import DELTA_G, DELTA_M, DELTA_R_IRR
from e1a_v5.generate import (
    AxialMemorySpec,
    axial_memory_dynamics,
    lateral_lag_covariance,
    markov_closure_residual,
)
from e1a_v5.identity import VALIDATION_MODULES, compute_identities
from e1a_v5.numerics import NumericalFailure
from e1a_v5.observation import (
    BANDWIDTH_CEILING,
    EXPOSURE_CEILING_FRACTION,
    LOCALIZATION_RATIO_CEILING,
    qualify_observation,
)
from e1a_v5.packets import RECORDS, BlockId, FieldId
from e1a_v5.reduction import (
    REMAINDER_DOMAIN_LIMIT,
    AxialEvidence,
    RemainderSet,
    certified_remainder_radius,
    exact_geometry_effect,
    exact_log_beta_bias,
    reduce_axial,
    remainder_impacts,
    remainder_set_effects,
    schur_complement,
    split_3d,
)
from e1a_v5.seeds import (
    CONFIRMATORY_FAMILIES,
    ENGINEERING,
    FAMILIES_V2,
    FAMILIES_V3,
    FAMILIES_V4,
    ROOT,
    ROOT_V2,
    ROOT_V3,
    ROOT_V4,
    SeedMap,
)
from e1a_v5.units import K_B
from e1a_v5.validation import plan
from e1a_v5.validation.cases import ALL_CASES, CASES_BY_ID, ExpectedEvent
from e1a_v5.validation.contract import (
    COMPARED_FIELDS,
    PlanContractViolation,
    check_correspondence,
    load_plan,
    require_correspondence,
)
from e1a_v5.validation.dispatch import instantiate
from e1a_v5.validation.harness import (
    axial_effects,
    axial_memory_specs,
    axial_memory_witness,
    design_specs,
    run_axial_memory_record,
    run_record,
)
from e1a_v5.validation.run import PROCEDURE_VERSION, DOMAIN_IDENTITY, deterministic_controls
from e1a_v5.rng import Stream

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


def _raises(fn) -> bool:
    try:
        fn()
        return False
    except Exception:
        return True


# ===========================================================================
# BLOCKER 1 -- the numerical sensitivity enclosure must be certified
# ===========================================================================

def test_blocker1_fd_agreement_is_not_a_bound() -> None:
    """A smooth objective where fine and coarse differences agree and are wrong.

    ``f(x) = x + (h^2 / 2 pi) sin(2 pi x / h)`` is entire.  Its central
    difference at step ``h`` samples the sine at multiples of its own period,
    so the oscillation cancels EXACTLY and the difference returns 1; the same
    happens at step ``2h``.  The two agree to machine precision while the true
    derivative at the origin is ``1 + h``.

    This is the V4 heuristic's failure mode: fine/coarse agreement constrains
    the difference of the two truncation remainders, not either remainder.
    """
    h = 1.0e-3
    amp = h * h / (2.0 * math.pi)

    def f(x: float) -> float:
        return x + amp * math.sin(2.0 * math.pi * x / h)

    fine = (f(h) - f(-h)) / (2.0 * h)
    coarse = (f(2.0 * h) - f(-2.0 * h)) / (4.0 * h)
    exact = 1.0 + h
    check("the two finite-difference steps agree to machine precision",
          abs(fine - coarse) < 1e-12, f"{abs(fine - coarse)!r}")
    check("both finite differences are wrong by h",
          abs(fine - exact) > 0.5 * h and abs(coarse - exact) > 0.5 * h)
    v4_radius = abs(fine - coarse) + 1e-16
    check("the V4 heuristic radius does NOT cover the error",
          v4_radius < abs(fine - exact),
          f"radius {v4_radius:.3e} vs error {abs(fine - exact):.3e}")

    # The V5 route carries the chain rule, so there is no step and no error.
    x = IHD.seed(0.0, 1.0, 0.0)
    y = x + amp * ((x * (2.0 * math.pi / h)).exp() * 0.0 + _sin_ihd(x * (2.0 * math.pi / h)))
    check("hyper-dual differentiation returns the exact derivative",
          abs(y.first - exact) <= max(y.first_radius, 1e-12),
          f"{y.first!r} vs {exact!r}")


def _sin_ihd(x: IHD) -> IHD:
    """``sin`` for the hyper-dual type, by its own chain rule."""
    v = cert.imid(x.v)
    s, c = math.sin(v), math.cos(v)
    return x._chain(cert.iv(s), cert.iv(c), cert.iv(-s))


def test_blocker1_hyper_dual_is_exact() -> None:
    x0, y0 = 1.3, 0.7
    x = IHD.seed(x0, 1.0, 0.0)
    y = IHD.seed(y0, 0.0, 1.0)
    f = (x * y).exp() * (x + y).log()
    s = x0 + y0
    exact = math.exp(x0 * y0) * (
        x0 * y0 * math.log(s) + math.log(s) + x0 / s + y0 / s - 1.0 / s ** 2)
    check("mixed second derivative is exact", abs(f.second - exact) <= f.second_radius,
          f"{f.second!r} vs {exact!r}")
    check("its enclosure brackets the exact value",
          f.d12[0] <= exact <= f.d12[1])
    check("the enclosure is tight", f.second_radius < 1e-12,
          f"{f.second_radius!r}")
    check("interval division by an interval containing zero is refused",
          _raises(lambda: IHD.const(1.0) / IHD(( -1.0, 1.0))))
    check("interval log of a possibly non-positive interval is refused",
          _raises(lambda: IHD((-1.0, 1.0)).log()))


def test_blocker1_generic_kernel_matches_cleared_core() -> None:
    """The generic kernel at float must reproduce the cleared numerical core."""
    from e1a_v5.observation import build_state_space
    K = nm.mat([[1.0e-4, 0.0], [0.0, 0.9e-4]])
    sigma = nm.scale(nm.spd_inverse(K), K_B * 298.0)
    a = nm.scale(K, 1.0 / plan.drag_coefficient())
    vals, _ = nm.eigh(K)
    tau = plan.drag_coefficient() / max(vals)
    dt, te = 0.75 * 0.2 * tau, 0.05 * tau
    r = nm.scale(nm.eye(2), 0.02 * sigma[0][0])
    ss_nm = build_state_space(a, sigma, [0.0, 0.0], nm.eye(2), r, [0.0, 0.0], dt, te)
    ss_g = cert.gbuild_state_space(a, sigma, [0.0, 0.0], nm.eye(2), r, [0.0, 0.0], dt, te)
    for name, pair in (("F", (ss_nm.f, ss_g.f)), ("Q", (ss_nm.q, ss_g.q)),
                       ("C", (ss_nm.c_obs, ss_g.c_obs)),
                       ("R_eff", (ss_nm.r_eff, ss_g.r_eff)),
                       ("S", (ss_nm.s_cross, ss_g.s_cross))):
        check(f"generic state space reproduces {name} exactly",
              nm.max_abs(nm.sub(*pair)) == 0.0)
    l1 = expected_loglik_per_frame(ss_nm, ss_nm)
    l2 = cert.gexpected_loglik(ss_g, ss_g)
    check("generic expected likelihood reproduces the cleared core exactly",
          l1 == l2.value, f"{l1!r} vs {l2.value!r}")
    check("the Riccati fixed-point bound is reported and tiny",
          0.0 <= l2.riccati_fixed_point_bound < 1e-25,
          f"{l2.riccati_fixed_point_bound!r}")


K_TRUE, T_TRUE = 1.0e-4, 298.0
_GAMMA = plan.drag_coefficient()
_K = nm.mat([[K_TRUE, 0.0], [0.0, 0.9 * K_TRUE]])
_SIGMA = nm.scale(nm.spd_inverse(_K), K_B * T_TRUE)
_A = nm.scale(_K, 1.0 / _GAMMA)
_V, _ = nm.eigh(_K)
_TAU = _GAMMA / max(_V)
_DT, _TE = 0.75 * 0.2 * _TAU, 0.05 * _TAU
_R = nm.scale(nm.eye(2), 0.02 * _SIGMA[0][0])
REF_PHI = [0.0, 0.0, 0.0, 0.0]
REF_SIGMA = [6.0e-3, 1.0e-3, 2.0e-9, 5.0e-2]


def ref_float_builder(phi):
    lk, lt, bx, lr = phi
    k_meas = nm.scale(_K, math.exp(lk))
    t_meas = T_TRUE * math.exp(lt)
    return FieldModel(
        h_eff=nm.scale(k_meas, 1.0 / (K_B * t_meas)), k_eff=k_meas,
        temperature=t_meas, a_drift=_A, sigma=_SIGMA, p_matrix=nm.eye(2),
        r_obs=nm.scale(_R, math.exp(lr)), b_det=(bx, 0.0), dt=_DT, t_exp=_TE)


def ref_generic_builder(phi):
    lk, lt, bx, lr = phi
    k_meas = cert.gscale(_K, cert.gexp(lk))
    inv_kt = cert.gexp(-lt) * (1.0 / (K_B * T_TRUE))
    return AnalysisModel(
        h_locked=cert.gscale(k_meas, inv_kt), p_matrix=nm.eye(2),
        r_obs=cert.gscale(_R, cert.gexp(lr)), b_det=(bx, 0.0), dt=_DT, t_exp=_TE)


_CERT_CACHE: list = []


def reference_sensitivity() -> CertifiedSensitivity:
    if not _CERT_CACHE:
        _CERT_CACHE.append(certified_profiled_sensitivity(
            ref_generic_builder, ref_float_builder, REF_PHI, phi_sigma=REF_SIGMA))
    return _CERT_CACHE[0]


def test_blocker1_certified_sensitivity() -> None:
    cs = reference_sensitivity()
    check("the production sensitivity is certified", cs.certified)
    check("no finite differences appear in the method",
          "finite difference" in cs.method and "no finite differences" in cs.method)
    check("the profiled nuisance vector is the full production one",
          THETA_NAMES == ("log_beta", "mu_x", "mu_y",
                          "d_chol_0", "d_chol_1", "d_chol_2", "omega")
          and N_THETA == 7 and LOG_BETA_ROW == 0)

    # Analytic references, each derived from the primitive map.
    refs = [
        (LOG_BETA_ROW, 0, -1.0, "d log beta*/d log k_A = -1"),
        (LOG_BETA_ROW, 1, +1.0, "d log beta*/d log T_A = +1"),
        (LOG_BETA_ROW, 2, 0.0, "d log beta*/d b_det_x = 0"),
        (1, 2, -1.0, "d mu_x*/d b_det_x = -1"),
        (2, 2, 0.0, "d mu_y*/d b_det_x = 0"),
    ]
    for i, k, exact, label in refs:
        got, rad = cs.jacobian[i][k], cs.radius[i][k]
        check(f"analytic reference inside the enclosure: {label}",
              abs(got - exact) <= rad, f"err {abs(got - exact):.3e} radius {rad:.3e}")
    check("the point values are exact to better than 1e-8",
          all(abs(cs.jacobian[i][k] - e) < 1e-8 for i, k, e, _ in refs))
    check("the expected information is certifiably nonsingular",
          cs.information_min_eigenvalue > 0.0 and
          math.isfinite(cs.information_inverse_norm))
    check("the Riccati fixed-point bound is reported",
          0.0 <= cs.riccati_bound < 1e-6, f"{cs.riccati_bound!r}")
    check("the second-derivative enclosure is tight",
          cs.worst_second_derivative_radius < 1e-3,
          f"{cs.worst_second_derivative_radius!r}")
    check("the linear-solve residual is reported",
          cs.linear_solve_residual >= 0.0)


def test_blocker1_qualification_rule() -> None:
    c = SIGMA_CAL_ABS_MAX
    check("PASS iff the upper endpoint is within the ceiling",
          classify_with_enclosure(NumericalEnclosure(c - 2e-5, c - 3e-5, c - 1e-5, "m"), c)
          == CEILING_PASS)
    check("FAIL iff the lower endpoint is above the ceiling",
          classify_with_enclosure(NumericalEnclosure(c + 2e-5, c + 1e-5, c + 3e-5, "m"), c)
          == CEILING_FAIL)
    check("a straddling enclosure is UNRESOLVED",
          classify_with_enclosure(NumericalEnclosure(c, c - 1e-5, c + 1e-5, "m"), c)
          == CEILING_UNRESOLVED)
    check("no enclosure at all is UNRESOLVED, which is fail-closed",
          classify_with_enclosure(None, c) == CEILING_UNRESOLVED)
    check("an exact value at the inclusive ceiling PASSES",
          classify_with_enclosure(NumericalEnclosure.exact(c), c) == CEILING_PASS)
    import e1a_v5.calibration as C
    check("the finite-difference production sensitivity is gone",
          not hasattr(C, "profiled_sensitivity"))
    check("the optimisation cross-check is explicitly NOT certified",
          C.ProfiledSensitivity(nm.zeros(1, 1), nm.zeros(1, 1)).certified is False)


# ===========================================================================
# BLOCKER 2 -- exact finite axial remainder effects
# ===========================================================================

def test_blocker2_auditor_counterexamples() -> None:
    e = -0.0004999
    E = nm.scale(nm.eye(2), e)
    first_order = abs(e)           # |tr E| / d, the V4 quantity
    exact = abs(exact_log_beta_bias(E))
    check("the auditor's scale counterexample is reproduced",
          close(exact, 0.00050002499, 1e-8), f"{exact!r}")
    check("the V4 first-order scale effect PASSED the 0.0005 budget",
          first_order <= BIAS_ABS_MAX)
    check("the exact finite scale effect FAILS it", exact > BIAS_ABS_MAX)
    check("V5 classifies the exact finite effect",
          remainder_impacts(E).log_beta_bias > BIAS_ABS_MAX)

    a = 0.048752
    E2 = nm.mat([[a, 0.0], [0.0, -a]])
    first_g = a                     # ||E - tr/d I||_op, the V4 quantity
    exact_g = exact_geometry_effect(E2)
    check("the auditor's geometry counterexample is reproduced",
          close(exact_g, math.atanh(a), 1e-12), f"{exact_g!r}")
    check("the V4 first-order geometry effect PASSED the log(1.05) budget",
          first_g < DELTA_G)
    check("the exact finite geometry effect FAILS it", exact_g >= DELTA_G)
    check("V5 classifies the exact finite effect",
          remainder_impacts(E2).geometry >= DELTA_G)


def test_blocker2_exact_formulae() -> None:
    # b* = log d - log tr((I+E)^-1): check against the independent derivation
    # for a diagonal E.
    for lam in ((0.01, -0.02), (0.1, 0.05), (-0.3, 0.2)):
        E = nm.mat([[lam[0], 0.0], [0.0, lam[1]]])
        tr_inv = 1.0 / (1.0 + lam[0]) + 1.0 / (1.0 + lam[1])
        check(f"exact scale effect at {lam}",
              close(exact_log_beta_bias(E), math.log(2.0) - math.log(tr_inv), 1e-12))
        g = [math.log(1.0 + lam[0]), math.log(1.0 + lam[1])]
        mean = 0.5 * (g[0] + g[1])
        check(f"exact geometry effect at {lam}",
              close(exact_geometry_effect(E), max(abs(g[0] - mean), abs(g[1] - mean)), 1e-12))
    # Isotropic: b* = log(1+e) exactly.
    for e in (0.01, -0.01, 0.2, -0.2):
        check(f"isotropic exact scale effect at {e}",
              close(exact_log_beta_bias(nm.scale(nm.eye(2), e)), math.log1p(e), 1e-12))
    # Congruence invariance of the normalised remainder's spectrum.
    E = nm.mat([[0.03, 0.01], [0.01, -0.02]])
    check("the exact effects depend only on the spectrum of E",
          close(exact_log_beta_bias(E),
                exact_log_beta_bias(nm.symmetrise(E)), 1e-14))


def test_blocker2_whole_set() -> None:
    for rho in (1e-4, 1e-3, 0.01, 0.1):
        fe = remainder_set_effects(RemainderSet(rho))
        check(f"sup scale effect over the ball at rho={rho}",
              close(fe.log_beta_bias, -math.log1p(-rho), 1e-14))
        check(f"sup geometry effect over the ball at rho={rho}",
              close(fe.geometry, math.atanh(rho), 1e-12))
        check(f"sup centre factor at rho={rho}",
              close(fe.centre_factor, math.sqrt(1.0 + rho), 1e-14))
        check(f"sup rate factor at rho={rho}", close(fe.rate_factor, 1.0 + rho, 1e-14))
        # The supremum must dominate every member of the set.
        worst_s = worst_g = 0.0
        for lam1 in (-rho, 0.0, rho):
            for lam2 in (-rho, 0.0, rho):
                E = nm.mat([[lam1, 0.0], [0.0, lam2]])
                worst_s = max(worst_s, abs(exact_log_beta_bias(E)))
                worst_g = max(worst_g, exact_geometry_effect(E))
        check(f"the sup dominates every sampled member at rho={rho}",
              fe.log_beta_bias >= worst_s * (1 - 1e-12)
              and fe.geometry >= worst_g * (1 - 1e-12))
    big = remainder_set_effects(RemainderSet(1.5))
    check("a set that leaves the SPD domain is refused",
          not big.within_domain and big.log_beta_bias == float("inf"))
    check("the domain guard is at ||E|| = 1", REMAINDER_DOMAIN_LIMIT == 1.0)


def test_blocker2_certified_radius_and_routing() -> None:
    k3 = plan.nominal_k3(0)
    _, b, kappa = split_3d(nm.symmetrise(k3))
    k_eff = schur_complement(k3)
    sd = plan.PRIMITIVE_RELATIVE_SIGMA * plan.K_REF
    rho = certified_remainder_radius([b[0][0], b[1][0]], kappa, k_eff,
                                     db_norm=3.0 * sd * math.sqrt(2.0), dkappa=3.0 * sd)
    check("the certified radius is finite and positive", 0.0 < rho < 1.0, f"{rho!r}")
    # It must dominate the exact remainder of every sampled perturbation.
    from e1a_v5.reduction import normalise_remainder, schur_nonlinear_remainder
    worst = 0.0
    for s1 in (-3.0, 0.0, 3.0):
        for s2 in (-3.0, 0.0, 3.0):
            for s3 in (-3.0, 0.0, 3.0):
                rem = schur_nonlinear_remainder(
                    [b[0][0], b[1][0]], kappa,
                    [s1 * sd, s2 * sd], s3 * sd)
                worst = max(worst, nm.op_norm_sym(
                    nm.symmetrise(normalise_remainder(rem, k_eff))))
    check("the certified radius dominates every sampled perturbation",
          rho >= worst, f"rho {rho:.3e} vs worst sampled {worst:.3e}")

    c_v = nm.scale(nm.eye(6), sd ** 2)
    red = reduce_axial(k3, 298.0,
                       evidence=AxialEvidence.fully_qualified(RemainderSet(rho)), c_v=c_v)
    check("the reduction qualifies with a certified set", red.ok)
    check("it reports exact finite effects", red.remainder_impacts is not None
          and red.remainder_impacts.log_beta_bias > 0.0)
    missing = AxialEvidence(**{**AxialEvidence.fully_qualified().__dict__,
                               "remainder_set": None})
    check("a missing certified set is refused",
          not reduce_axial(k3, 298.0, evidence=missing, c_v=c_v).ok)
    out = reduce_axial(k3, 298.0,
                       evidence=AxialEvidence.fully_qualified(RemainderSet(1.5)), c_v=c_v)
    check("a set outside the SPD domain is refused", not out.ok)

    eff = axial_effects(0)
    check("the design point's axial effects fit inside the existing bias budget",
          eff.log_beta_bias + plan.BIAS_PER_CELL <= BIAS_ABS_MAX,
          f"{eff.log_beta_bias + plan.BIAS_PER_CELL!r}")
    check("the centre effect is multiplicative, not additive",
          eff.centre_factor > 1.0 and close(eff.centre_factor,
                                            math.sqrt(1.0 + eff.rho), 1e-14))
    check("the rate effect is reported for the observation domain",
          close(eff.rate_factor, 1.0 + eff.rho, 1e-14))


# ===========================================================================
# BLOCKER 3 -- a raw statistic can never become a calibrated limit
# ===========================================================================

def test_blocker3_gate_artifact() -> None:
    check("the string-identity constructor is gone",
          not hasattr(GateLimit, "calibrated"))
    check("the arbitrary-identity failure cannot be expressed",
          _raises(lambda: GateLimit.calibrated(0.0, 0.0, "arbitrary")))

    real = CalibratedGateProcedure(
        GateFamily.SHAPE, PROCEDURE_VERSION, "proc-id", "cal/4000", 0.975,
        DOMAIN_IDENTITY, 1.0e-3, CriticalValueStatus.CALIBRATED)
    ok = GateLimit.from_procedure(0.0, real, GateFamily.SHAPE, PROCEDURE_VERSION,
                                  DOMAIN_IDENTITY)
    check("a complete artifact yields a usable limit", ok.usable and ok.passes(DELTA_G))
    check("the limit is statistic + radius, never the statistic",
          close(ok.limit, 1.0e-3) and ok.statistic == 0.0)

    cases = [
        ("no procedure at all", None, GateFamily.SHAPE, PROCEDURE_VERSION,
         DOMAIN_IDENTITY, GATE_NO_PROCEDURE),
        ("wrong gate family", real, GateFamily.CENTRE, PROCEDURE_VERSION,
         DOMAIN_IDENTITY, GATE_WRONG_FAMILY),
        ("wrong procedure version", real, GateFamily.SHAPE, PROCEDURE_VERSION - 1,
         DOMAIN_IDENTITY, GATE_WRONG_VERSION),
        ("wrong nuisance domain", real, GateFamily.SHAPE, PROCEDURE_VERSION,
         "a-different-envelope", GATE_WRONG_DOMAIN),
    ]
    for label, proc, fam, ver, dom, code in cases:
        g = GateLimit.from_procedure(0.0, proc, fam, ver, dom)
        check(f"{label} yields no calibrated gate",
              not g.usable and g.passes(DELTA_G) is None and code in g.defects,
              str(g.defects))

    for label, proc in [
        ("uncalibrated status", CalibratedGateProcedure(
            GateFamily.SHAPE, PROCEDURE_VERSION, "p", "c", 0.975,
            DOMAIN_IDENTITY, 1e-3)),
        ("missing calibration identity", CalibratedGateProcedure(
            GateFamily.SHAPE, PROCEDURE_VERSION, "p", "", 0.975,
            DOMAIN_IDENTITY, 1e-3, CriticalValueStatus.CALIBRATED)),
        ("missing procedure identity", CalibratedGateProcedure(
            GateFamily.SHAPE, PROCEDURE_VERSION, "", "c", 0.975,
            DOMAIN_IDENTITY, 1e-3, CriticalValueStatus.CALIBRATED)),
        ("missing domain identity", CalibratedGateProcedure(
            GateFamily.SHAPE, PROCEDURE_VERSION, "p", "c", 0.975, "",
            1e-3, CriticalValueStatus.CALIBRATED)),
        ("negative radius", CalibratedGateProcedure(
            GateFamily.SHAPE, PROCEDURE_VERSION, "p", "c", 0.975,
            DOMAIN_IDENTITY, -1e-3, CriticalValueStatus.CALIBRATED)),
        ("impossible coverage target", CalibratedGateProcedure(
            GateFamily.SHAPE, PROCEDURE_VERSION, "p", "c", 1.5,
            DOMAIN_IDENTITY, 1e-3, CriticalValueStatus.CALIBRATED)),
    ]:
        g = GateLimit.from_procedure(0.0, proc, GateFamily.SHAPE,
                                     PROCEDURE_VERSION, DOMAIN_IDENTITY)
        check(f"{label} yields no calibrated gate", not g.usable, str(g.defects))

    fx = synthetic_calibrated_gate_fixture(GateFamily.SHAPE, 1e-3)
    check("the fixture is marked fixture-only", fx.fixture_only)
    check("every fixture identity sits in the fixture namespace",
          all(FIXTURE_NAMESPACE in s for s in
              (fx.procedure_identity, fx.calibration_identity, fx.domain_identity)))
    prod = GateLimit.from_procedure(0.0, fx, GateFamily.SHAPE,
                                    PROCEDURE_VERSION, DOMAIN_IDENTITY)
    check("the fixture is refused in production mode",
          not prod.usable and GATE_FIXTURE_IN_PRODUCTION in prod.defects)
    test = GateLimit.from_procedure(0.0, fx, GateFamily.SHAPE, PROCEDURE_VERSION,
                                    DOMAIN_IDENTITY, allow_fixture=True)
    check("the fixture works when explicitly allowed", test.usable)
    check("an unusable procedure refuses to produce a limit at all",
          _raises(lambda: CalibratedGateProcedure(
              GateFamily.SHAPE, 5, "", "", 0.975, "", 1e-3).upper_limit(0.0)))
    check("enlarging an unusable limit leaves it unusable",
          not prod.enlarged(1.0).usable and not prod.scaled(2.0).usable)


# ===========================================================================
# BLOCKER 4 -- observation qualification enforces T 15.2
# ===========================================================================

def _obs_world(ratio_target: float, frames: int = 200):
    spec, h = design_specs(n_frames=frames,
                           localization_ratio_target=ratio_target)[0]
    sigma = nm.spd_inverse(spec.h_true)
    a = nm.matmul(spec.d_true, nm.spd_inverse(sigma))
    return spec, sigma, a


def test_blocker4_observation_qualification() -> None:
    check("the declared ceiling is 0.05", LOCALIZATION_RATIO_CEILING == 0.05)
    for target, want in ((0.02, True), (0.049999, True), (0.05, True),
                         (0.050001, False), (0.25, False)):
        spec, sigma, a = _obs_world(target)
        q = qualify_observation(sigma, spec.r_obs, spec.p_matrix, a,
                                spec.dt, spec.t_exp, spec.noise_model)
        check(f"localisation ratio {target} -> valid={want}", q.valid is want,
              f"ratio {q.localization_ratio!r}")
    # Inclusive semantics, and a straddling enclosure does NOT pass.
    spec, sigma, a = _obs_world(0.05)
    q = qualify_observation(sigma, spec.r_obs, spec.p_matrix, a, spec.dt,
                            spec.t_exp, spec.noise_model, rate_factor=1.0 + 1e-9)
    check("an enclosure straddling the ceiling does not pass", not q.valid)
    q = qualify_observation(sigma, spec.r_obs, spec.p_matrix, a, spec.dt,
                            spec.t_exp, "heavy")
    check("a non-Gaussian noise model is unqualified", not q.valid)
    bad_r = nm.mat([[1.0, 2.0], [2.0, 1.0]])
    q = qualify_observation(sigma, bad_r, spec.p_matrix, a, spec.dt, spec.t_exp)
    check("a non-PSD R_obs is unqualified", not q.valid)
    q = qualify_observation(sigma, spec.r_obs, nm.zeros(2, 2), a, spec.dt, spec.t_exp)
    check("a singular detector map is unqualified", not q.valid)
    q = qualify_observation(sigma, spec.r_obs, spec.p_matrix, a, spec.dt,
                            spec.dt * 2.0)
    check("an exposure longer than the frame interval is unqualified", not q.valid)
    spec2, sigma2, a2 = _obs_world(0.02)
    q = qualify_observation(sigma2, spec2.r_obs, spec2.p_matrix, a2, spec2.dt,
                            spec2.dt * 0.999)
    check("an exposure beyond the blur envelope is unqualified", not q.valid)


def test_blocker4_no_caller_override() -> None:
    sm = SeedMap()
    spec, h = design_specs(n_frames=400,
                           **instantiate("CTL-NOISE-HI").spec_kwargs)[0]
    out = run_record(spec, h, Stream(sm.replicate_seed(ENGINEERING, "OBS", 1)))
    check("CTL-NOISE-HI generates a ratio far above the ceiling",
          out.observation is not None
          and out.observation.localization_ratio > 4.0 * LOCALIZATION_RATIO_CEILING)
    check("the record is NOT observation-valid", out.observation.valid is False)
    check("the refusal is the observation-model one",
          any(r.code == "OBSERVATION_MODEL_UNQUALIFIED" for r in out.reasons))
    code = "".join(
        line for _, line in _code_lines(os.path.join("e1a_v5", "validation", "run.py"))
    ).replace(" ", "")
    check("the record builder never asserts observation_valid=True",
          "observation_valid=True" not in code)


# ===========================================================================
# BLOCKER 5 -- the validation obligations are restored
# ===========================================================================

def test_blocker5_plan_counts_from_the_machine_plan() -> None:
    doc = load_plan()
    plan_cases = {c["case_id"]: c for c in doc["cases"]}
    for cid in ("CTL-ETA-T-COV", "CTL-AXIAL-MEMORY"):
        check(f"the machine plan requires 200 replicates for {cid}",
              plan_cases[cid]["replicates"] == 200,
              str(plan_cases[cid]["replicates"]))
        check(f"the registry matches the plan for {cid}",
              CASES_BY_ID[cid].replicates == 200,
              str(CASES_BY_ID[cid].replicates))
        check(f"{cid} is a stochastic full-pipeline case",
              CASES_BY_ID[cid].expected_event is ExpectedEvent.COMPLETE_SUPPORT)
        check(f"{cid} routes to the complete-experiment driver",
              instantiate(cid).driver == "complete_experiment")


def test_blocker5_plan_code_correspondence() -> None:
    check("the plan is the compared source of truth",
          "e1a_v5_validation_plan.json" in
          __import__("e1a_v5.validation.contract", fromlist=["x"]).PLAN_PATH)
    report = check_correspondence(ALL_CASES)
    check("every case matches the machine plan field by field", report.ok,
          "; ".join(report.as_list()[:4]))
    check("the compared fields cover the declared set",
          set(COMPARED_FIELDS) >= {"case_id", "purpose", "replicates",
                                   "seed_namespace", "expected_event",
                                   "family", "detail"})

    # A difference in ANY compared field must fail, with no warning-only mode.
    doc = load_plan()
    for field, value in (("replicates", 1), ("expected_event", "deterministic_control"),
                         ("seed_namespace", "wrong-family"), ("family", "power"),
                         ("purpose", "something else"), ("detail", {"noise_ratio": 9.0})):
        mutated = {**doc, "cases": [
            ({**c, field: value} if c["case_id"] == "CTL-AXIAL-MEMORY" else c)
            for c in doc["cases"]]}
        r = check_correspondence(ALL_CASES, mutated)
        check(f"a plan/code difference in {field!r} fails", not r.ok)
        check(f"require_correspondence raises on a {field!r} difference",
              _raises(lambda m=mutated: require_correspondence(ALL_CASES, m)))
    dropped = {**doc, "cases": [c for c in doc["cases"]
                                if c["case_id"] != "CTL-ETA-T-COV"]}
    check("a case missing from the plan fails",
          not check_correspondence(ALL_CASES, dropped).ok)
    added = {**doc, "cases": doc["cases"] + [{"case_id": "GHOST"}]}
    check("a case missing from the code fails",
          not check_correspondence(ALL_CASES, added).ok)


def test_blocker5_axial_memory_witness() -> None:
    specs = axial_memory_specs(n_frames=64)
    check("the hidden-memory world covers all eight records", len(specs) == 8)
    w = axial_memory_witness(specs[0][0])
    check("K3 is positive definite", w["k3_spd"])
    check("the Schur complement is valid", w["schur_spd"])
    check("the lateral MARGINAL density is exactly the Schur one",
          w["lateral_marginal_relative_error"] < 1e-12,
          f"{w['lateral_marginal_relative_error']!r}")
    check("the lateral lag structure is NOT 2D Markov",
          w["worst_markov_closure_residual"] > 1e-3,
          f"{w['worst_markov_closure_residual']!r}")
    check("the lateral field stays inside the conditioning limit",
          w["condition_k_eff"] <= 100.0)

    # The witness is a property of the world: with no coupling it vanishes.
    k3 = plan.k3_from_lateral(plan.nominal_stiffness(0), coupling=0.0,
                              axial_fraction=plan.AXIAL_MEMORY_AXIAL_FRACTION)
    flat = AxialMemorySpec(k3, 298.0, plan.drag_coefficient(), nm.eye(2),
                           nm.eye(2), (0.0, 0.0), 1e-5, 1e-6, 16)
    a3, s3 = axial_memory_dynamics(flat)
    vals, _ = nm.eigh(nm.symmetrise(k3))
    res = markov_closure_residual(a3, s3, 0.5 * flat.gamma / min(vals))
    check("with no lateral-axial coupling the Markov closure holds exactly",
          res < 1e-15, f"{res!r}")
    check("the control's coupling is the one the plan declares",
          plan.AXIAL_MEMORY_COUPLING == 0.15)

    sm = SeedMap()
    spec, h = specs[0]
    out = run_axial_memory_record(
        spec, h, Stream(sm.replicate_seed(ENGINEERING, "AXMEM", 1)))
    check("the 3D world runs through the ordinary 2D pipeline",
          out.evaluable or bool(out.reasons))


def test_blocker5_eta_t_covariance() -> None:
    from e1a_v5.validation.harness import experiment_calibration
    correct = experiment_calibration()
    omitted = experiment_calibration(omit_eta_t_covariance=True)
    k = correct.keys[0]
    s_correct = correct.absolute_sigma(k).point
    s_omitted = omitted.absolute_sigma(k).point
    check("the two covariance models give different uncertainties",
          not close(s_correct, s_omitted, 1e-6),
          f"{s_correct!r} vs {s_omitted!r}")
    check("the declared correlation is positive", plan.ETA_T_CORRELATION > 0.0)
    # d log beta/d log k = -1 and d log beta/d log T = +1, so a POSITIVE
    # correlation reduces the correct variance and the omission OVERSTATES.
    check("at this design point the omission OVERSTATES the uncertainty",
          s_omitted > s_correct)
    # The phrase may appear in prose that REMOVES the claim; what must not
    # exist is executable code asserting a direction.
    code = "".join(
        line for _, line in _code_lines(os.path.join("e1a_v5", "validation", "run.py"))
    )
    check("no executable code asserts a universal direction",
          "understate" not in code and "overstate" not in code)
    doc = load_plan()
    check("the plan records that no direction claim is made",
          doc["restored_controls"]["CTL-ETA-T-COV"]["direction_claim"].startswith("NONE"))
    check("the plan records the exact wording ambiguity",
          "ambiguity" in " ".join(
              doc["restored_controls"]["CTL-ETA-T-COV"].keys()))


# ===========================================================================
# Systematic fail-open re-audit
# ===========================================================================

def _code_lines(path: str):
    import io
    import tokenize
    with open(path, "rb") as fh:
        src = fh.read().decode("utf-8")
    blanked = set()
    try:
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            if tok.type in (tokenize.STRING, tokenize.COMMENT):
                for ln in range(tok.start[0], tok.end[0] + 1):
                    blanked.add(ln)
    except tokenize.TokenError:
        pass
    return [(i, line) for i, line in enumerate(src.splitlines(), 1)
            if i not in blanked]


def test_systematic_fail_open() -> None:
    import re
    patterns = {
        "max(1.0, .) absolute scale": re.compile(r"max\(\s*1\.0\s*,"),
        ".get with a pass-reading default": re.compile(
            r"\.get\([^)]*?,\s*(True|False|0\.0|1\.0)\s*\)"),
        "bare except": re.compile(r"except\s*:"),
        "or <literal> fallback": re.compile(r"\bor\s+(0\.0|1\.0|True)\b"),
    }
    allowed = {os.path.join("e1a_v5", "optimize.py")}
    found: dict[str, list[str]] = {k: [] for k in patterns}
    for root, dirs, files in os.walk("e1a_v5"):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for f in sorted(files):
            if not f.endswith(".py"):
                continue
            path = os.path.join(root, f)
            for i, code in _code_lines(path):
                for name, rx in patterns.items():
                    if rx.search(code):
                        if name.startswith("max(1.0") and path in allowed:
                            continue
                        found[name].append(f"{path}:{i}")
    for name, hits in found.items():
        check(f"no load-bearing {name}", not hits, str(hits[:4]))

    # Bare strings must not grant scientific status anywhere.
    check("a bare string cannot calibrate a gate",
          _raises(lambda: GateLimit.calibrated(0.0, 0.0, "x")))
    # Empty sequences must not pass a qualification.
    from e1a_v5.confidence import absolute_qualification, bias_qualification
    check("an empty absolute qualification refuses",
          _raises(lambda: absolute_qualification([])))
    check("an empty bias qualification refuses",
          _raises(lambda: bias_qualification([], [])))
    # Missing bounds must not become zero.
    from e1a_v5.evidence import BiasEvidence
    check("a missing bias bound is not zero", not BiasEvidence.missing().usable)
    # Fixture objects must not be accepted in production.
    fx = synthetic_calibrated_gate_fixture(GateFamily.CURRENT, 1e-9)
    check("a fixture gate is refused in production",
          not GateLimit.from_procedure(0.0, fx, GateFamily.CURRENT,
                                       PROCEDURE_VERSION, DOMAIN_IDENTITY).usable)
    # Unknown case IDs must not become nominal runs.
    check("an unknown case id is refused", _raises(lambda: instantiate("NOPE")))


def test_event_search() -> None:
    """No ExpectedEvent can fabricate calibrated support from a raw identity."""
    from e1a_v5.validation import events as EV
    lines = _code_lines(os.path.join("e1a_v5", "validation", "events.py"))
    start = next(i for i, (_, l) in enumerate(lines)
                 if l.startswith("def evaluate_event"))
    end = next((i for i, (_, l) in enumerate(lines)
                if i > start and l.startswith("def ")), len(lines))
    body = "".join(l for _, l in lines[start:end])
    for forbidden in ("GateLimit", "gate_identity", "DELTA_G", "DELTA_M",
                      "DELTA_A", "DELTA_R_IRR", "upper_limit", ".limit"):
        check(f"the event evaluator never references {forbidden!r}",
              forbidden not in body)
    whole = "".join(l for _, l in lines)
    for ev in ExpectedEvent:
        check(f"event {ev.name} has an explicit branch", ev.name in whole)


def test_live_gate_state() -> None:
    from e1a_v5.validation.run import NO_GATE_PROCEDURES
    check("live V5 has no calibrated gate procedure", not NO_GATE_PROCEDURES)
    for fam in GateFamily:
        g = GateLimit.from_procedure(0.0, NO_GATE_PROCEDURES.get(fam), fam,
                                     PROCEDURE_VERSION, DOMAIN_IDENTITY)
        check(f"the {fam.value} gate is UNCALIBRATED in live V5",
              g.passes(1.0) is None)


# ===========================================================================
# Identities and seeds
# ===========================================================================

def test_v5_identities_and_seeds() -> None:
    for m in ("certified.py", "evidence.py", "observation.py", "reduction.py",
              os.path.join("validation", "contract.py"),
              os.path.join("validation", "dispatch.py"),
              os.path.join("validation", "events.py"),
              os.path.join("validation", "run.py")):
        check(f"{m} is bound into the validation identity",
              m in VALIDATION_MODULES, str(VALIDATION_MODULES))
    ids = compute_identities()
    check("all six identities are distinct 64-hex digests",
          len({*ids.as_dict().values()}) == 6
          and all(len(v) == 64 for v in ids.as_dict().values()))

    sm = SeedMap()
    check("the V5 root is new",
          sm.root == ROOT and ROOT not in (ROOT_V2, ROOT_V3, ROOT_V4))
    check("five confirmatory families are frozen",
          len(CONFIRMATORY_FAMILIES) == 5
          and all(f.endswith("-v5") for f in CONFIRMATORY_FAMILIES))
    for i, fam in enumerate(CONFIRMATORY_FAMILIES):
        for root, old, label in ((ROOT_V4, FAMILIES_V4[i], "V4"),
                                 (ROOT_V3, FAMILIES_V3[i], "V3"),
                                 (ROOT_V2, FAMILIES_V2[i], "V2")):
            check(f"{fam} is disjoint from its {label} stream",
                  sm.disjoint_from(fam, root, old, "POWER-NOMINAL"))
        check(f"{fam} is disjoint from every engineering stream",
              sm.disjoint_from_all_engineering(fam, "POWER-NOMINAL"))
    check("the engineering namespace is separate",
          ENGINEERING not in CONFIRMATORY_FAMILIES
          and sm.engineering_disjoint_from_confirmatory("POWER-NOMINAL"))
    doc = load_plan()
    check("the plan records the confirmatory streams as unconsumed",
          all(not f["executed"] for f in
              __import__("json").load(open(os.path.join(
                  "docs", "e1a", "e1a_v5_seed_map.json")))["families"].values()
              if f["confirmatory"]))
    check("the plan declares procedure version 5", doc["procedure_version"] == 5)


def test_deterministic_battery() -> None:
    results = deterministic_controls()
    for r in results:
        check(f"deterministic control {r['case_id']} passes", r["passed"])
    ids = {r["case_id"] for r in results}
    check("the two restored controls are NOT in the deterministic battery",
          "CTL-ETA-T-COV" not in ids and "CTL-AXIAL-MEMORY" not in ids)
    check("their exact checks survive as supplementary references",
          {"REF-ETA-T-COV-ALGEBRA", "REF-AXIAL-REFUSAL",
           "REF-AXIAL-MEMORY-WITNESS"} <= ids)


# ===========================================================================

def main() -> int:
    print("E1a v5 PROCEDURE VERSION 5 -- CORE REPAIR REGRESSIONS")
    print("Execution class: MIXED STATIC/PURE + SYNTHETIC ENGINEERING CHECKS\n")
    print("blocker 1 -- finite-difference agreement is not a bound")
    test_blocker1_fd_agreement_is_not_a_bound()
    print("\nblocker 1 -- hyper-dual arithmetic is exact")
    test_blocker1_hyper_dual_is_exact()
    print("\nblocker 1 -- the generic kernel reproduces the cleared core")
    test_blocker1_generic_kernel_matches_cleared_core()
    print("\nblocker 1 -- certified U.20 sensitivity [SYNTHETIC]")
    test_blocker1_certified_sensitivity()
    print("\nblocker 1 -- the three-way qualification rule")
    test_blocker1_qualification_rule()
    print("\nblocker 2 -- the auditor's exact counterexamples")
    test_blocker2_auditor_counterexamples()
    print("\nblocker 2 -- exact finite formulae")
    test_blocker2_exact_formulae()
    print("\nblocker 2 -- the whole certified remainder set")
    test_blocker2_whole_set()
    print("\nblocker 2 -- certified radius and budget routing")
    test_blocker2_certified_radius_and_routing()
    print("\nblocker 3 -- the calibrated gate artifact")
    test_blocker3_gate_artifact()
    print("\nblocker 4 -- observation qualification [SYNTHETIC]")
    test_blocker4_observation_qualification()
    print("\nblocker 4 -- no caller override [SYNTHETIC]")
    test_blocker4_no_caller_override()
    print("\nblocker 5 -- plan counts, read from the machine plan")
    test_blocker5_plan_counts_from_the_machine_plan()
    print("\nblocker 5 -- plan/code correspondence")
    test_blocker5_plan_code_correspondence()
    print("\nblocker 5 -- the actual 3D hidden-memory witness [SYNTHETIC]")
    test_blocker5_axial_memory_witness()
    print("\nblocker 5 -- the eta/T covariance consequence [SYNTHETIC]")
    test_blocker5_eta_t_covariance()
    print("\nsystematic fail-open re-audit")
    test_systematic_fail_open()
    print("\nvalidation event search")
    test_event_search()
    print("\nlive gate state")
    test_live_gate_state()
    print("\nV5 identities and seeds")
    test_v5_identities_and_seeds()
    print("\ndeterministic battery")
    test_deterministic_battery()
    print(f"\nRESULT: {PASSED} passed, {FAILED} failed")
    print("  REAL EXPERIMENT DATA ....... 0")
    print("  CALIBRATION EXECUTIONS ..... 0")
    print("  OFFICIAL CAMPAIGN JOBS ..... 0")
    return 0 if FAILED == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
