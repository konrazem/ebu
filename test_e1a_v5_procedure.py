"""E1a v5 candidate: Schur reduction, T11a predicates, gates, likelihood, verdict.

**EXECUTION CLASS: MIXED.** Sections 1-7 are static/pure. Section 8 draws
SYNTHETIC validation RNG and runs SYNTHETIC OU trajectories for generator and
estimator reference checks. No real data, no calibration execution, no
official campaign job, no physical experiment.
"""

from __future__ import annotations

import math

from e1a_v5 import numerics as nm
from e1a_v5 import realization as rf
from e1a_v5.confidence import (
    BUDGET_RESIDUAL, CRITICAL_VALUE_CEILING, DELTA_A, DELTA_C, Interval,
    NORMAL_CRITICAL, build_interval, contrast_bias_from_absolute,
    contrast_qualification, contrast_variance, absolute_qualification,
)
from e1a_v5.diagnostics import (
    ANGULAR_HARMONICS, INNOVATION_LAGS, NullScales, DiagnosticComponents,
)
from e1a_v5.gates import (
    centre_statistic, covariance_log_distance, geometry_statistic,
    irreversibility_from_matrices, stationarity_statistic,
)
from e1a_v5.generate import GeneratorSpec, crosscheck_exposure_blocks, generate_record
from e1a_v5.identity import compute_identities
from e1a_v5.likelihood import (
    Parameters, chol_params_from_spd, drift_of, irreversibility_ratio,
    log_likelihood, sigma_of, spd_from_chol,
)
from e1a_v5.numerics import NumericalFailure
from e1a_v5.observation import build_state_space, localization_ratio, van_loan
from e1a_v5.optimize import OptimizerFailure, minimise
from e1a_v5.reduction import (
    axial_ratio, plane_block_bias, propagate_schur_covariance, reduce_axial,
    schur_complement, schur_jacobian, schur_nonlinear_remainder,
)
from e1a_v5.refusals import AXIAL_REDUCTION_UNQUALIFIED
from e1a_v5.rng import Stream, derive_seed
from e1a_v5.seeds import CALIBRATION, CONTROL, DIAGNOSTIC, FAMILIES, POWER, SIZE, SeedMap
from e1a_v5.verdict import (
    ComponentTally, INCONCLUSIVE, INVALID, NOT_EVALUABLE, SUPPORTED, decide,
)

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


# --------------------------------------------------------------------------
def test_schur_reduction() -> None:
    K = nm.mat([[1.2e-4, 1e-5, 3e-5], [1e-5, 1.0e-4, 2e-5], [3e-5, 2e-5, 5e-5]])
    S = schur_complement(K)
    # exact 2x2 reference: S = A - b b^T / kappa
    b = [3e-5, 2e-5]
    ref = nm.sub(nm.mat([[1.2e-4, 1e-5], [1e-5, 1.0e-4]]),
                 nm.mat([[b[0] * b[0], b[0] * b[1]], [b[1] * b[0], b[1] * b[1]]]))
    ref = nm.scale(ref, 1.0)
    ref = nm.sub(nm.mat([[1.2e-4, 1e-5], [1e-5, 1.0e-4]]),
                 nm.scale(nm.mat([[b[0] * b[0], b[0] * b[1]], [b[1] * b[0], b[1] * b[1]]]), 1 / 5e-5))
    check("Schur complement exact", nm.max_abs(nm.sub(S, ref)) < 1e-20)
    check("K_eff differs from the plane block", nm.max_abs(nm.sub(S, nm.mat([[1.2e-4, 1e-5], [1e-5, 1.0e-4]]))) > 0)
    # pure axial reparametrisation z -> s z leaves S invariant exactly
    for s in (0.5, 2.0, 7.3, 1e3):
        K2 = [row[:] for row in K]
        K2[0][2] /= s; K2[2][0] /= s; K2[1][2] /= s; K2[2][1] /= s; K2[2][2] /= s * s
        check(f"reparametrisation s={s} leaves S invariant",
              nm.max_abs(nm.sub(S, schur_complement(K2))) < 1e-15 * nm.max_abs(S))
    # zero coupling
    K0 = nm.mat([[1e-4, 0, 0], [0, 1e-4, 0], [0, 0, 5e-5]])
    check("zero coupling r = 0", axial_ratio(K0) == 0.0)
    check("zero coupling S = A", nm.max_abs(nm.sub(schur_complement(K0), nm.mat([[1e-4, 0], [0, 1e-4]]))) == 0.0)
    # omitted-correction diagnostics (U.A13)
    r = axial_ratio(K)
    lb, g = plane_block_bias(r)
    check("beta_plane formula", close(lb, math.log(2 * (1 - r) / (2 - r))))
    check("G_plane formula", close(g, -0.5 * math.log1p(-r)))
    check("plane-block bias is nonzero", abs(lb) > 1e-3)
    check("r in [0,1)", 0.0 <= r < 1.0)
    # Jacobian (U.A10) against finite differences
    J = schur_jacobian([3e-5, 2e-5], 5e-5)
    base = [1.2e-4, 1e-5, 1.0e-4, 3e-5, 2e-5, 5e-5]

    def vech_s(v):
        A = [[v[0], v[1]], [v[1], v[2]]]
        bb = [v[3], v[4]]
        kk = v[5]
        M = nm.sub(A, nm.scale([[bb[0] * bb[0], bb[0] * bb[1]], [bb[1] * bb[0], bb[1] * bb[1]]], 1 / kk))
        return [M[0][0], M[0][1], M[1][1]]

    worst = 0.0
    for j in range(6):
        h = 1e-6 * max(abs(base[j]), 1e-9)
        up = list(base); up[j] += h
        dn = list(base); dn[j] -= h
        fd = [(vech_s(up)[i] - vech_s(dn)[i]) / (2 * h) for i in range(3)]
        for i in range(3):
            worst = max(worst, abs(fd[i] - J[i][j]) / max(1.0, abs(J[i][j])))
    check("Schur Jacobian matches finite differences", worst < 1e-5, f"worst {worst:.2e}")
    # near b = 0 the leading Jacobian vanishes but the quadratic term does not
    # V4: the remainder is a TYPED stiffness residual, not a bare float.
    rem = schur_nonlinear_remainder([0.0, 0.0], 5e-5, [1e-6, 1e-6], 0.0)
    check("quadratic Schur term survives at b = 0", nm.max_abs(rem.matrix) > 0.0)
    check("the remainder declares its units", rem.unit == "N/m")
    check("Jacobian in b vanishes at b = 0", schur_jacobian([0.0, 0.0], 5e-5)[0][3] == 0.0)
    # covariance propagation
    Cv = nm.scale(nm.eye(6), 1e-12)
    Cs, ref2 = propagate_schur_covariance(K, Cv)
    check("covariance propagates", not ref2 and nm.is_spd(Cs))
    _, ref2 = propagate_schur_covariance(K, None)
    check("absent covariance refused", bool(ref2))
    _, ref2 = propagate_schur_covariance(K, nm.eye(3))
    check("wrong-shape covariance refused", bool(ref2))


def test_axial_refusals() -> None:
    K = nm.mat([[1.2e-4, 1e-5, 3e-5], [1e-5, 1.0e-4, 2e-5], [3e-5, 2e-5, 5e-5]])
    # V3: axial qualification is fail-closed, so every case supplies explicit
    # evidence and the defect under test is the one named.
    from e1a_v5.reduction import (
        AxialEvidence, NonlinearRemainder, REMAINDER_DOMAIN_LIMIT, schur_complement,
    )
    Cv = nm.scale(nm.eye(6), 1e-12)
    # V5: qualification is over a certified SET of admissible normalised
    # remainders, not one evaluated witness, and an "excessive" set is one
    # that leaves the domain where the linearisation it bounds is defined.
    from e1a_v5.reduction import RemainderSet
    full = AxialEvidence.fully_qualified(RemainderSet(1.0e-4, "test"))
    big_remainder = RemainderSet(5.0, "outside the SPD domain")

    def ev(**kw):
        return AxialEvidence(**{**full.__dict__, **kw})

    cases = [
        ("missing K3", dict(k3=None, evidence=full), "K3 present"),
        ("bad kappa",
         dict(k3=nm.mat([[1e-4, 0, 3e-5], [0, 1e-4, 0], [3e-5, 0, -1e-9]]), evidence=full),
         "kappa > 0"),
        ("non-SPD full K",
         dict(k3=nm.mat([[1e-4, 0, 9e-4], [0, 1e-4, 0], [9e-4, 0, 1e-5]]), evidence=full),
         "K3 SPD"),
        ("unqualified support", dict(k3=K, evidence=ev(support_qualified=False)),
         "support_qualified qualified"),
        ("unqualified temporal", dict(k3=K, evidence=ev(temporal_reduction_qualified=False)),
         "temporal_reduction_qualified qualified"),
        ("large remainder set", dict(k3=K, evidence=ev(remainder_set=big_remainder)),
         f"||E_K||_op < {REMAINDER_DOMAIN_LIMIT}"),
        ("missing remainder set", dict(k3=K, evidence=ev(remainder_set=None)),
         "certified remainder set supplied"),
        ("unqualified conservativity", dict(k3=K, evidence=ev(conservativity_qualified=False)),
         "conservativity qualified"),
        ("asymmetric K3",
         dict(k3=nm.mat([[1e-4, 5e-5, 0], [1e-5, 1e-4, 0], [0, 0, 5e-5]]), evidence=full),
         "K3 numerically symmetric after conservativity qualification"),
    ]
    for label, kw, pred in cases:
        red = reduce_axial(temperature=298.0, c_v=Cv, **kw)
        check(f"refused: {label}", any(r.predicate == pred for r in red.refusals),
              f"got {[r.predicate for r in red.refusals]}")
        check(f"no fallback for {label}", not red.ok)
    red = reduce_axial(K, 298.0, full, Cv)
    check("nominal axial reduction qualifies", red.ok and nm.is_spd(red.h_eff))
    check("V3: absent evidence is refused", not reduce_axial(K, 298.0, c_v=Cv).ok)
    check("V3: absent covariance is refused", not reduce_axial(K, 298.0, full).ok)


def test_t11a_predicates() -> None:
    # fixed constants reproduce the amendment's published values
    check("c_T*", close(rf.C_T_STAR, 0.06495789627477229))
    check("log 2.1", close(rf.LOG_K_STAR, 0.7419373447293773))
    check("epsilon_2", close(rf.EPSILON_2, 0.05108256237659907, 1e-14))
    check("h_90", close(rf.H90, 0.03778351913824557, 1e-12))
    check("s_c", close(rf.S_C, 0.00372827037646145, 1e-14))
    lo, hi = rf.temperature_band()
    check("temperature band", close(lo, 0.05846210664729507, 1e-13) and close(hi, 1.10 * rf.C_T_STAR))
    klo, khi = rf.stiffness_band()
    check("stiffness band", close(klo, 0.6677436102564396, 1e-13) and close(khi, 0.8161310792023151, 1e-13))
    check("L2* entries", close(rf.L2_STAR[0][0], 0.176392425140, 1e-10)
          and close(rf.L2_STAR[0][1], 0.396765525528, 1e-10)
          and close(rf.L2_STAR[1][1], -0.281752940797, 1e-10))
    # temperature
    o = rf.qualify_temperature_field(rf.Enclosure.point(math.log(318 / 298)))
    check("318 K valid", o.status == rf.VALID and close(o.retained_fraction, 1.0))
    o = rf.qualify_temperature_field(rf.Enclosure.point(math.log(304 / 298)))
    check("304 K out of spec", o.status == rf.OUT_OF_SPEC)
    check("304 K retention", close(o.retained_fraction, 0.3068790100, 1e-9))
    check("304 K planning detection", close(o.worst_case_planning_detection, 0.0002274435852, 1e-9))
    check("lower boundary detection", close(rf.planning_detection(lo), 1 - 4.30590784e-12, 1e-9))
    # boundaries are inclusive
    check("lower boundary inclusive", rf.qualify_temperature_field(rf.Enclosure.point(lo)).status == rf.VALID)
    check("upper boundary inclusive", rf.qualify_temperature_field(rf.Enclosure.point(hi)).status == rf.VALID)
    check("just below lower boundary fails",
          rf.qualify_temperature_field(rf.Enclosure.point(lo * (1 - 1e-12))).status != rf.VALID)
    # reversed labels must not pass via an absolute value
    o = rf.qualify_temperature_field(rf.Enclosure.point(-math.log(318 / 298)))
    check("reversed labels out of spec", o.status == rf.OUT_OF_SPEC)
    # straddling enclosure is unresolved
    o = rf.qualify_temperature_field(rf.Enclosure(lo * 0.99, hi * 1.01, "interval"))
    check("straddling enclosure unresolved", o.status == rf.UNRESOLVED)
    # an uncertified enclosure can never be VALID
    o = rf.qualify_temperature_field(rf.Enclosure(lo, hi, "grid"))
    check("grid enclosure never valid", o.status == rf.UNRESOLVED)
    # policy version
    o = rf.qualify_temperature_field(rf.Enclosure.point(rf.C_T_STAR), policy_version="other")
    check("policy mismatch refused", o.status == rf.SPECIFICATION_MISSING)

    # stiffness: both modes
    K0 = nm.mat([[100.0, 0.0], [0.0, 100.0]])
    modes = rf.stiffness_log_modes(nm.scale(K0, 2.1), K0)
    check("2.1-fold modes", all(close(m, rf.LOG_K_STAR) for m in modes))
    o = rf.qualify_stiffness_field([rf.Enclosure.point(m) for m in modes])
    check("2.1-fold valid", o.status == rf.VALID)
    m1021 = rf.stiffness_log_modes(nm.scale(K0, 1.021), K0)
    o = rf.qualify_stiffness_field([rf.Enclosure.point(m) for m in m1021])
    check("1.021-fold out of spec", o.status == rf.OUT_OF_SPEC)
    check("1.021 retention", close(o.retained_fraction, 0.0280111782, 1e-9))
    check("1.021 planning detection", close(o.worst_case_planning_detection, 0.0005218639151, 1e-9))
    # the documented hidden-weak-mode case: scalar average inside, a mode outside
    mm = rf.stiffness_log_modes(nm.mat([[190.0, 0.0], [0.0, 225.0]]), K0)
    o = rf.qualify_stiffness_field([rf.Enclosure.point(m) for m in mm])
    check("modes (1.9, 2.25) out of spec", o.status == rf.OUT_OF_SPEC)
    check("harmonic scalar would have passed", klo <= math.log(2 / (1 / 1.9 + 1 / 2.25)) <= khi)
    check("least-mode screen used", close(o.worst_case_challenge, min(mm)))
    o = rf.qualify_stiffness_field([rf.Enclosure.point(rf.LOG_K_STAR)])
    check("single mode refused", o.status == rf.UNRESOLVED)
    # nonproportional pair still judged per mode
    Knp = nm.mat([[205.0, 20.0], [20.0, 215.0]])
    mnp = rf.stiffness_log_modes(Knp, K0)
    check("nonproportional pair has two distinct modes", abs(mnp[0] - mnp[1]) > 1e-3)

    # ellipse
    check("nominal ellipse distance zero", rf.ellipse_distance(rf.K2_STAR_UNM, K0) < 1e-14)
    o = rf.qualify_ellipse_field(rf.Enclosure.point(rf.ellipse_distance(rf.K2_STAR_UNM, K0)))
    check("nominal ellipse valid", o.status == rf.VALID)
    unrot = nm.mat([[150.0, 0.0], [0.0, 60.0]])
    d_unrot = rf.ellipse_distance(unrot, K0)
    check("unrotated ellipse distance", close(d_unrot, 0.458145365937, 1e-10))
    o = rf.qualify_ellipse_field(rf.Enclosure.point(d_unrot))
    check("unrotated ellipse out of spec", o.status == rf.OUT_OF_SPEC)
    check("epsilon_2 boundary inclusive",
          rf.qualify_ellipse_field(rf.Enclosure.point(rf.EPSILON_2)).status == rf.VALID)
    check("just above epsilon_2 fails",
          rf.qualify_ellipse_field(rf.Enclosure.point(rf.EPSILON_2 * (1 + 1e-12))).status == rf.OUT_OF_SPEC)
    # orthogonal invariance, including a reflection
    for Q in (nm.mat([[0.6, -0.8], [0.8, 0.6]]), nm.mat([[0.0, 1.0], [1.0, 0.0]])):
        def cong(M):
            return nm.symmetrise(nm.matmul(nm.matmul(Q, M), nm.transpose(Q)))
        d0 = rf.ellipse_distance(rf.K2_STAR_UNM, K0)
        d1 = rf.ellipse_distance(cong(rf.K2_STAR_UNM), cong(K0), cong(rf.L2_STAR))
        check("ellipse metric orthogonally invariant", abs(d0 - d1) < 1e-13, f"{d0} vs {d1}")
        Knc = nm.mat([[140.0, 30.0], [30.0, 70.0]])
        Kref = nm.mat([[110.0, 10.0], [10.0, 95.0]])
        d0 = rf.ellipse_distance(Knc, Kref)
        d1 = rf.ellipse_distance(cong(Knc), cong(Kref), cong(rf.L2_STAR))
        check("noncircular reference invariant", abs(d0 - d1) < 1e-13, f"{d0} vs {d1}")
        # Rotating ONLY the realisation is a physical target departure, not a
        # coordinate change, and must NOT be invariant (T-stage 22.6.4).
        d2 = rf.ellipse_distance(cong(rf.K2_STAR_UNM), K0)
        check("rotating only the realisation is detected",
              abs(d2 - rf.ellipse_distance(rf.K2_STAR_UNM, K0)) > 0.1, f"{d2}")
    # circular reference has a unique inverse square root
    check("circular inverse sqrt unique",
          nm.max_abs(nm.sub(nm.inv_sqrtm_spd(K0), nm.scale(nm.eye(2), 0.1))) < 1e-14)


def test_gates() -> None:
    H = nm.mat([[2.0, 0.5], [0.5, 3.0]])
    Hi = nm.spd_inverse(H)
    for c in (1.0, 0.5, 7.3):
        check(f"G = 0 for scalar multiple {c}", geometry_statistic(nm.scale(Hi, c), H) < 1e-14)
    check("G documented example", close(geometry_statistic(nm.mat([[1.5, 0], [0, 0.5]]), nm.eye(2)),
                                        math.log(3) / 2, 1e-12))
    # rotation inside an isotropic eigenspace is not a geometry failure
    Q = nm.mat([[0.6, -0.8], [0.8, 0.6]])
    rot = nm.symmetrise(nm.matmul(nm.matmul(Q, nm.eye(2)), nm.transpose(Q)))
    check("isotropic rotation is not a failure", geometry_statistic(rot, nm.eye(2)) < 1e-14)
    # but rotating an anisotropic covariance is detected
    aniso = nm.mat([[1.5, 0.0], [0.0, 0.5]])
    rot_aniso = nm.symmetrise(nm.matmul(nm.matmul(Q, aniso), nm.transpose(Q)))
    check("rotated anisotropy detected", geometry_statistic(rot_aniso, nm.spd_inverse(aniso)) > 0.1)
    # trace-preserving wrong shape: scalar beta plausible, geometry rejects
    tr_pres = nm.mat([[1.5, 0.0], [0.0, 0.5]])
    check("trace-preserving wrong shape detected", geometry_statistic(tr_pres, nm.eye(2)) > math.log(1.05))
    check("centre statistic", close(centre_statistic([0.1, 0.0], [0.0, 0.0], nm.eye(2)), 0.1))
    check("centre is zero at the reference", centre_statistic([0.0, 0.0], [0.0, 0.0], nm.eye(2)) == 0.0)
    # r_irr on the documented counterexample A = I + omega J, Sigma = I
    for w in (0.0, 0.01, 0.02, 0.05, 0.3):
        A = nm.mat([[1.0, -w], [w, 1.0]])
        check(f"r_irr(omega={w})", close(irreversibility_from_matrices(A, nm.eye(2)), w, 1e-12))
    # the counterexample preserves the Gaussian exactly at every omega
    A = nm.mat([[1.0, -0.3], [0.3, 1.0]])
    asig = nm.matmul(A, nm.eye(2))
    check("counterexample preserves the Gaussian",
          nm.max_abs(nm.sub(nm.add(asig, nm.transpose(asig)), nm.scale(nm.eye(2), 2.0))) < 1e-15)
    # stationarity gate: identical quarters give zero, a shifted quarter does not
    means = [[0.0, 0.0]] * 4
    covs = [nm.eye(2)] * 4
    out = stationarity_statistic(means, covs, nm.eye(2))
    check("stationarity zero when identical", out.statistic == 0.0)
    means2 = [[0.0, 0.0], [0.0, 0.0], [0.0, 0.0], [0.05, 0.0]]
    out = stationarity_statistic(means2, covs, nm.eye(2))
    check("stationarity detects a shifted quarter", close(out.statistic, 0.5))
    check("stationarity uses six pairs", out.worst_pair in [(0, 3), (1, 3), (2, 3)])
    covs2 = [nm.eye(2), nm.eye(2), nm.eye(2), nm.scale(nm.eye(2), 1.2)]
    out = stationarity_statistic(means, covs2, nm.eye(2))
    check("stationarity detects a covariance change", out.statistic > 1.0)
    check("covariance log distance symmetric",
          close(covariance_log_distance(nm.eye(2), nm.scale(nm.eye(2), 2.0)),
                covariance_log_distance(nm.scale(nm.eye(2), 2.0), nm.eye(2))))


def test_equivalence_and_multiplicity() -> None:
    check("delta_a", close(DELTA_A, 0.04879016417, 1e-10))
    check("delta_c", close(DELTA_C, 0.01980262730, 1e-10))
    check("critical ceiling", CRITICAL_VALUE_CEILING == 2.10)
    check("residual budget", close(BUDGET_RESIDUAL, 0.0039, 1e-12))
    i = build_interval(0.0, 0.01, NORMAL_CRITICAL, 0.0005)
    check("interval inside margin", i.strictly_inside(DELTA_A))
    check("boundary equality is not a pass", not Interval(-DELTA_A, 0.0).strictly_inside(DELTA_A))
    check("boundary equality upper is not a pass", not Interval(0.0, DELTA_A).strictly_inside(DELTA_A))
    check("strictly inside passes", Interval(-DELTA_A * 0.999, DELTA_A * 0.999).strictly_inside(DELTA_A))
    # a wide interval containing zero does not pass; a narrow one excluding zero does
    check("wide interval containing one fails", not Interval(-0.08, 0.08).strictly_inside(DELTA_A))
    check("narrow interval excluding zero passes", Interval(0.01, 0.03).strictly_inside(DELTA_A))
    # contrast variance uses the full covariance
    C = nm.mat([[1e-4, 5e-5], [5e-5, 1.2e-4]])
    check("contrast variance", close(contrast_variance(C, 1, 0), 1.2e-4 + 1e-4 - 2 * 5e-5))
    # perfect common-mode cancellation
    Ccom = nm.mat([[1e-4, 1e-4], [1e-4, 1e-4]])
    check("common mode cancels exactly", contrast_variance(Ccom, 1, 0) == 0.0)
    # independent errors do not cancel
    Cind = nm.mat([[1e-4, 0.0], [0.0, 1e-4]])
    check("independent errors do not cancel", close(contrast_variance(Cind, 1, 0), 2e-4))
    # the contrast bias bound is never inferred from two absolute bounds
    check("two 0.0005 bounds imply only 0.001", close(contrast_bias_from_absolute([0.0005, 0.0005]), 0.001))
    ok, sds = absolute_qualification(nm.scale(nm.eye(8), 0.009 ** 2))
    check("0.009 boundary accepted", ok and all(close(s, 0.009) for s in sds))
    ok, _ = absolute_qualification(nm.scale(nm.eye(8), 0.0091 ** 2))
    check("above 0.009 refused", not ok)
    ok, _ = contrast_qualification(nm.scale(nm.eye(4), (0.003 / math.sqrt(2)) ** 2), [(1, 0), (2, 0), (3, 0)])
    check("0.003 contrast boundary accepted", ok)


def test_verdict_engine() -> None:
    full = ComponentTally(
        absolute_pass=8, contrast_pass=6, shape_pass=8, centre_pass=8,
        stationarity_pass=8, current_pass=8, realization_valid=8,
        branch_a_valid=8, observation_valid=8,
    )
    check("full conjunction supported", decide(full).classification == SUPPORTED)
    for field_name in ("absolute_pass", "contrast_pass", "shape_pass", "centre_pass"):
        kw = {field_name: getattr(full, field_name) - 1}
        t = ComponentTally(**{**full.__dict__, **kw})
        check(f"{field_name} shortfall is not supported", decide(t).classification != SUPPORTED)
    # density passes but current fails -> inconclusive with the declared qualifier
    t = ComponentTally(**{**full.__dict__, "current_pass": 7})
    v = decide(t)
    check("current failure is inconclusive, not a theorem rejection",
          v.classification == INCONCLUSIVE and "CURRENT DETECTED" in v.qualifier)
    t = ComponentTally(**{**full.__dict__, "current_pass": 7, "current_inconclusive": 1})
    check("wide current interval is reported inconclusive",
          "REVERSIBILITY INCONCLUSIVE" in decide(t).qualifier)
    t = ComponentTally(**{**full.__dict__, "stationarity_pass": 7})
    check("stationarity failure is invalid", decide(t).classification == INVALID)
    t = ComponentTally(**{**full.__dict__, "diagnostic_rejected": True})
    check("rejected diagnostic vetoes support", decide(t).classification == INVALID)
    t = ComponentTally(**{**full.__dict__, "realization_valid": 7})
    check("realization shortfall blocks support", decide(t).classification != SUPPORTED)
    check("optimiser failure is not evaluable",
          decide(full, not_evaluable=True).classification == NOT_EVALUABLE)
    check("a failed equivalence is never auto-relabelled a discrepancy",
          decide(ComponentTally(**{**full.__dict__, "absolute_pass": 7})).classification != "DISCREPANCY_ESTABLISHED")


def test_seeds_and_identity() -> None:
    sm = SeedMap()
    seeds = set()
    for fam in FAMILIES:
        for case in ("A", "B"):
            for rep in range(50):
                seeds.add(sm.replicate_seed(fam, case, rep))
    check("seed namespaces disjoint", len(seeds) == len(FAMILIES) * 2 * 50)
    check("calibration and validation streams differ",
          sm.replicate_seed(CALIBRATION, "X", 0) != sm.replicate_seed(SIZE, "X", 0))
    check("seed derivation is deterministic",
          sm.replicate_seed(POWER, "P", 3) == SeedMap().replicate_seed(POWER, "P", 3))
    # V4 adds the engineering namespace alongside the five confirmatory ones.
    check("every declared family is distinct",
          len({sm.family_seed(f) for f in FAMILIES}) == len(FAMILIES))
    check("there are five confirmatory families plus engineering",
          len(FAMILIES) == 6)
    try:
        sm.family_seed("not_a_family")
        check("unknown seed family refused", False)
    except ValueError:
        check("unknown seed family refused", True)
    check("derive_seed is order sensitive", derive_seed("a", "b") != derive_seed("b", "a"))
    s1 = Stream(derive_seed("t", 1))
    s2 = Stream(derive_seed("t", 1))
    check("same seed reproduces the stream", [s1.gauss() for _ in range(5)] == [s2.gauss() for _ in range(5)])
    st = s1.state()
    a = [s1.gauss() for _ in range(3)]
    s1.set_state(st)
    check("stream state restores exactly", a == [s1.gauss() for _ in range(3)])
    ids = compute_identities({"design": "v5-candidate"})
    check("identities are 64-hex", all(len(v) == 64 and all(c in "0123456789abcdef" for c in v)
                                       for v in ids.as_dict().values()))
    check("identities are distinct", len(set(ids.as_dict().values())) == 6)
    check("V3: six identities including gate semantics",
          set(ids.as_dict()) == {"analysis_procedure", "synthetic_generator",
                                 "validation_procedure", "packet_schema",
                                 "seed_map", "gate_semantics"})
    check("identity depends on configuration",
          compute_identities({"design": "other"}).analysis != ids.analysis)


def test_likelihood_and_generator() -> None:
    """SYNTHETIC RNG and SYNTHETIC OU trajectories are used from here."""
    H = nm.mat([[2.4e7, 0.0], [0.0, 2.4e7]])
    Sig = nm.spd_inverse(H)
    A = nm.scale(nm.eye(2), 80.0)
    asig = nm.matmul(A, Sig)
    D = nm.symmetrise(nm.scale(nm.add(asig, nm.transpose(asig)), 0.5))

    # Van Loan against the scalar OU analytic transition
    F, Q = van_loan(nm.mat([[-1.0]]), nm.mat([[4.0]]), 0.3)
    check("Van Loan F", close(F[0][0], math.exp(-0.3)))
    check("Van Loan Q", close(Q[0][0], 2.0 * (1 - math.exp(-0.6))))

    # generator and estimator agree through independently derived formulas
    for te in (0.002, 0.005, 0.01):
        cc = crosscheck_exposure_blocks(nm.mat([[80.0, 10.0], [10.0, 120.0]]),
                                        nm.mat([[1.2e-2, 2e-3], [2e-3, 8e-3]]), te)
        check(f"quadrature vs Van Loan at t_exp={te}", max(cc.values()) < 1e-13, str(cc))

    # exposure creates a genuine transition/observation correlation
    ss = build_state_space(A, Sig, [0.0, 0.0], nm.eye(2), nm.scale(nm.eye(2), 1e-18),
                           [0.0, 0.0], 0.005, 0.001)
    check("exposure correlates noises", nm.max_abs(ss.s_cross) > 0.0)
    ss0 = build_state_space(A, Sig, [0.0, 0.0], nm.eye(2), nm.scale(nm.eye(2), 1e-18),
                            [0.0, 0.0], 0.005, 0.0)
    check("instantaneous limit has no correlation", nm.max_abs(ss0.s_cross) == 0.0)
    check("instantaneous limit loads P directly", nm.max_abs(nm.sub(ss0.c_obs, nm.eye(2))) == 0.0)
    check("zero exposure recovers the OU transition",
          nm.max_abs(nm.sub(ss0.f, nm.expm(nm.scale(A, -0.005)))) < 1e-15)
    check("localisation ratio", close(localization_ratio(Sig, nm.scale(Sig, 0.05)), 0.05))

    # r_irr through the likelihood parameterisation matches the matrix route
    for w in (0.0, 0.05, 0.2):
        p = Parameters(0.0, (0.0, 0.0), chol_params_from_spd(D), w * D[0][0])
        sig = sigma_of(p, H)
        check(f"r_irr parameterisation consistent (omega scale {w})",
              close(irreversibility_ratio(p, sig),
                    irreversibility_from_matrices(drift_of(p, sig), sig), 1e-10))

    # ideal reference: zero observation noise, zero exposure, known transition
    spec = GeneratorSpec(h_true=H, beta_true=1.0, mu_true=(0.0, 0.0), d_true=D, omega_true=0.0,
                         p_matrix=nm.eye(2), r_obs=nm.scale(nm.eye(2), 1e-24), b_det=(0.0, 0.0),
                         dt=0.005, t_exp=0.0, n_frames=3000)
    y = generate_record(spec, Stream(derive_seed("unit", "ideal")))
    p_true = Parameters(0.0, (0.0, 0.0), chol_params_from_spd(D), 0.0)
    ll_true = log_likelihood(p_true, H, y, nm.eye(2), spec.r_obs, [0.0, 0.0], 0.005, 0.0).loglik
    # the true parameters beat a clearly wrong scale
    for wrong in (-0.3, 0.3):
        p_w = Parameters(wrong, (0.0, 0.0), chol_params_from_spd(D), 0.0)
        ll_w = log_likelihood(p_w, H, y, nm.eye(2), spec.r_obs, [0.0, 0.0], 0.005, 0.0).loglik
        check(f"true scale beats log beta = {wrong}", ll_true > ll_w, f"{ll_true} vs {ll_w}")
    # the fast steady-state path matches the generic recursion
    o_fast = log_likelihood(p_true, H, y, nm.eye(2), spec.r_obs, [0.0, 0.0], 0.005, 0.0,
                            collect_innovations=False)
    o_gen = log_likelihood(p_true, H, y, nm.eye(2), spec.r_obs, [0.0, 0.0], 0.005, 0.0,
                           collect_innovations=True)
    check("fast path matches generic recursion",
          abs(o_fast.loglik - o_gen.loglik) <= 1e-12 * abs(o_gen.loglik),
          f"{o_fast.loglik} vs {o_gen.loglik}")
    check("innovations collected", len(o_gen.innovations) == len(y))

    # optimiser failure is a declared outcome, never a fabricated beta
    try:
        minimise(lambda x: float("nan"), [0.0, 0.0])
        check("NaN objective refused", False)
    except OptimizerFailure:
        check("NaN objective refused", True)
    try:
        minimise(lambda x: float("inf"), [0.0, 0.0])
        check("inadmissible start refused", False)
    except OptimizerFailure:
        check("inadmissible start refused", True)
    res = minimise(lambda x: (x[0] - 1.3) ** 2 + (x[1] + 0.7) ** 2, [0.0, 0.0])
    check("optimiser finds a known minimum",
          res.converged and abs(res.x[0] - 1.3) < 1e-5 and abs(res.x[1] + 0.7) < 1e-5)
    res = minimise(lambda x: sum(v * v for v in x), [0.0] * 3, max_evaluations=5)
    check("evaluation budget exhaustion is reported", not res.converged)
    # The (D + Q) parameterisation GUARANTEES L L^T = 2 D is SPD for every
    # omega, which is precisely how the model permits currents without ever
    # producing an inadmissible diffusion.
    for w in (0.0, 1e3, 1e9):
        pw = Parameters(0.0, (0.0, 0.0), chol_params_from_spd(D), w * D[0][0])
        sg = sigma_of(pw, H)
        Aw = drift_of(pw, sg)
        asg = nm.matmul(Aw, sg)
        ll_mat = nm.symmetrise(nm.add(asg, nm.transpose(asg)))
        check(f"diffusion is 2D by construction (omega scale {w})",
              nm.max_abs(nm.sub(ll_mat, nm.scale(D, 2.0))) < 1e-9 * nm.max_abs(D))
        check(f"diffusion SPD for omega scale {w}", nm.is_spd(ll_mat))
    # A drift supplied directly, outside that parameterisation, CAN be
    # inadmissible, and is refused rather than silently clipped.
    try:
        build_state_space(nm.scale(nm.eye(2), -1.0), Sig, [0.0, 0.0], nm.eye(2),
                          nm.scale(nm.eye(2), 1e-20), [0.0, 0.0], 0.005, 0.0)
        check("non-SPD diffusion refused", False)
    except NumericalFailure:
        check("non-SPD diffusion refused", True)


def test_physical_scale_regressions() -> None:
    """Regressions for two defects that only appear at physical SI scale.

    Both were found by running the pipeline, not by the algebraic suites, and
    both are invisible in dimensionless test fixtures.
    """
    from e1a_v5.estimate import _fit
    from e1a_v5.validation import plan as vplan
    from e1a_v5.validation.harness import design_specs, run_record

    specs = design_specs(n_frames=vplan.SMOKE_FRAMES)
    spec, H = specs[0]
    sigma = nm.spd_inverse(H)
    check("physical covariance really is tiny", sigma[0][0] < 1e-15)

    y = generate_record(spec, Stream(derive_seed("regression", "riccati")))
    true = Parameters(0.0, (0.0, 0.0), chol_params_from_spd(spec.d_true), 0.0, None)
    out = log_likelihood(true, H, y, spec.p_matrix, spec.r_obs, list(spec.b_det),
                         spec.dt, spec.t_exp, collect_innovations=True)

    # Defect 1: the Riccati convergence test must be relative to the
    # covariance's OWN scale. A max(1.0, ||P||) floor makes it trivially true
    # at 1e-17 and freezes the Kalman gain after one frame.
    check("Riccati reaches steady state by genuine convergence", out.steady_after > 2,
          f"steady_after = {out.steady_after}")

    # Defect 2: with the gain frozen, the likelihood rewarded a degenerate
    # D -> 0 limit. The true parameters must beat that degenerate point.
    degenerate = Parameters(
        1.3, (0.0, 0.0),
        (true.d_chol[0] - 8.0, 0.0, true.d_chol[2] - 4.5), 0.0, None,
    )
    ll_deg = log_likelihood(degenerate, H, y, spec.p_matrix, spec.r_obs,
                            list(spec.b_det), spec.dt, spec.t_exp).loglik
    check("true parameters beat the degenerate D -> 0 point",
          out.loglik > ll_deg, f"{out.loglik} vs {ll_deg}")

    # The MLE must land near the truth, and beat it only by the usual
    # overfitting margin of about half the free-parameter count.
    best, ll_fit, _, conv, _ = _fit(y, H, spec.p_matrix, spec.r_obs, list(spec.b_det),
                                    spec.dt, spec.t_exp, free_sigma=False)
    check("locked fit converges", conv)
    check("MLE recovers log beta near zero", abs(best.log_beta) < 0.25, f"{best.log_beta}")
    check("MLE recovers the diffusion scale",
          0.5 < (math.exp(best.d_chol[0]) / math.exp(true.d_chol[0])) ** 2 < 2.0)
    check("MLE beats truth only by the overfitting margin",
          0.0 <= ll_fit - out.loglik < 20.0, f"{ll_fit - out.loglik}")

    # Defect 3: optimiser coordinates must be dimensionless. A 5 percent
    # relative step on d_chol (magnitude ~ 14 to 40) is a factor-of-several
    # jump; the scaling layer keeps every coordinate of order one.
    from e1a_v5.estimate import _initial_parameters, _scaling_for
    init = _initial_parameters(y, H, spec.p_matrix, list(spec.b_det), spec.dt, False)
    sc = _scaling_for(init, sigma_of(init, H), False)
    u0 = sc.from_parameters(init, False)
    check("optimiser coordinates are order one", all(abs(v) < 5.0 for v in u0), str(u0))
    check("scaling round-trips", nm.max_abs([[
        a - b for a, b in zip(sc.from_parameters(sc.to_parameters(u0, False), False), u0)]]) < 1e-9)

    # The whole record pipeline must be evaluable at the physical design point.
    out2 = run_record(spec, H, Stream(derive_seed("regression", "pipeline")))
    check("record pipeline is evaluable at physical scale", out2.evaluable, out2.reason)
    check("record reports every gate statistic",
          all(v is not None for v in (out2.log_beta, out2.se, out2.geometry,
                                      out2.centre, out2.r_irr, out2.stationarity)))


def main() -> int:
    print("Schur reduction")
    test_schur_reduction()
    print("\naxial refusal predicates")
    test_axial_refusals()
    print("\nT11a realized-field predicates")
    test_t11a_predicates()
    print("\ngeometry / centre / stationarity / current gates")
    test_gates()
    print("\nequivalence and multiplicity")
    test_equivalence_and_multiplicity()
    print("\nverdict engine")
    test_verdict_engine()
    print("\nseeds and identities")
    test_seeds_and_identity()
    print("\nlikelihood, generator and optimiser [SYNTHETIC RNG]")
    test_likelihood_and_generator()
    print("\nphysical-scale regressions [SYNTHETIC RNG]")
    test_physical_scale_regressions()
    print(f"\nRESULT: {PASSED} passed, {FAILED} failed")
    print("Execution class: MIXED STATIC/PURE + SYNTHETIC VALIDATION RNG")
    print("  SYNTHETIC OU TRAJECTORIES .. 4")
    print("  REAL EXPERIMENT DATA ....... 0")
    print("  CALIBRATION EXECUTIONS ..... 0")
    print("  OFFICIAL CAMPAIGN JOBS ..... 0")
    return 0 if FAILED == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
