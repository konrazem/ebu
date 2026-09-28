"""E1a v4 bounded-implementation conformance gate.

**EXECUTION CLASS: NON-MODEL-ADVANCING STATIC/PURE.** Every input below is
hand-authored. No random number is drawn, no initial state is generated, no
trajectory is produced and no OU process is stepped. The stochastic
synthetic-validation campaign is a separate authorised stage and has NOT run.

Calibration artifacts used here are hand-written FIXTURES, marked `is_fixture`,
and exist only to exercise decision semantics. They are not calibration.
"""

from __future__ import annotations

import json
import math
import os
import shutil
import tempfile

from e1a_v4 import K_B
from e1a_v4.branch_a import BranchAField, assert_not_branch_b, build_field, stiffness_matrix
from e1a_v4.calibration import (
    BLOCK1_GATES, CalibrationArtifact, CalibrationCondition, block2_p_value,
    branch_a_signature, normalised_H, require_calibration,
)
from e1a_v4.contract import load_contract
from e1a_v4.effective_size import (
    A_closed_form, A_from_sum, N_element, N_g2, phi_of, sigma_stat, var_g2,
)
from e1a_v4.endpoints import (
    EndpointResult, UncertaintyModel, declared_entropy_relation,
    p1_geometry, p2_cross_field, p3_absolute, p4_consistency,
)
from e1a_v4.geometry import (
    FieldAnalysis, G1, G2, G3, G4, G5, analyse_field, beta_mle, rank_guard,
    resolvability_blocks, resolvability_boundary_ratio, resolvable, sample_covariance,
)
from e1a_v4.identity import procedure_identity
from e1a_v4.numerics import Refusal, chol, inv, jacobi, mm, sym_pow
from e1a_v4.seeds import SeedFamily, SeedMap
from e1a_v4.status import AnalysisStatus
from e1a_v4.world import ForbiddenRNG, WorldConfig

PASSED = 0
FAILED = 0
ROOT = os.path.dirname(os.path.abspath(__file__))


def check(label: str, condition: bool, detail: str = "") -> None:
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  [PASS] {label}" + (f"  -- {detail}" if detail else ""))
    else:
        FAILED += 1
        print(f"  [FAIL] {label}" + (f"  -- {detail}" if detail else ""))


def refuses(fn, *args, **kwargs) -> bool:
    try:
        fn(*args, **kwargs)
    except Refusal:
        return True
    return False


BINDING = load_contract(ROOT)
ETA = {298.0: 0.890e-3, 318.0: 0.596e-3}
A_BEAD = 6.366e-6
ROUTE = "force_displacement_with_stokes_drag"


def field_for(index: int) -> BranchAField:
    spec = BINDING.fields[index]
    return build_field(BINDING, spec, calibration_route=ROUTE,
                       viscosity=ETA[float(spec["T_K"])], bead_radius=A_BEAD)


def exact_covariance_points(sigma, beta: float = 1.0):
    """2m hand-written points whose SAMPLE covariance is EXACTLY sigma/beta.

    x = +- sqrt(m) * (i-th Cholesky column). Then (1/n) sum x x^T = L L^T.
    No randomness is involved.
    """
    scaled = [[sigma[i][j] / beta for j in range(len(sigma))] for i in range(len(sigma))]
    low = chol(scaled)
    m = len(scaled)
    cols = [[low[r][c] for r in range(m)] for c in range(m)]
    pts = []
    for col in cols:
        pts.append([math.sqrt(m) * v for v in col])
        pts.append([-math.sqrt(m) * v for v in col])
    return pts


# ----------------------------------------------------------------- contract tests
def test_contract() -> None:
    check("valid contract accepted and bound to all three authority documents",
          BINDING.data["contract_id"] == "e1a_v4_prospective_design"
          and len(BINDING.foundation_sha256) == 64
          and len(BINDING.baseline_sha256) == 64
          and len(BINDING.design_sha256) == 64,
          f"contract sha {BINDING.sha256[:12]}, foundation {BINDING.foundation_sha256[:12]}")
    check("adopted constants read from contract, not typed",
          (BINDING.delta_cross, BINDING.delta_abs, BINDING.alpha_geom,
           BINDING.alpha_1, BINDING.alpha_2, BINDING.theta_cap_deg, BINDING.rank_tol,
           BINDING.pipeline_target) == (0.02, 0.05, 0.005, 0.004, 0.001, 5.0, 1e-12, 0.9))
    check("z_cross == z_abs == 1.959963985",
          BINDING.z_cross == 1.959963985 and BINDING.z_abs == 1.959963985)
    with tempfile.TemporaryDirectory() as tmp:
        for rel in ("docs/e1a/e1a_v4_design_contract.json",
                    "docs/e1a/E1A_V4_PROSPECTIVE_DESIGN.md",
                    "docs/theory/EBU_THEORY_BASELINE.md",
                    "docs/physical_foundation/EBU_PHYSICAL_FOUNDATION_CANONICAL.md"):
            dst = os.path.join(tmp, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy(os.path.join(ROOT, rel), dst)
        cpath = os.path.join(tmp, "docs/e1a/e1a_v4_design_contract.json")
        good = json.load(open(cpath))

        bad = json.loads(json.dumps(good))
        bad["endpoints"]["P2_cross_field"]["delta_cross"] = 0.05
        json.dump(bad, open(cpath, "w"))
        loaded = load_contract(tmp)
        check("modified constant is READ, not overridden by code", loaded.delta_cross == 0.05,
              "the design wins; implementation never substitutes its own value")

        bad2 = json.loads(json.dumps(good))
        bad2["endpoints"]["P2_cross_field"]["multiplicity_correction"] = "Bonferroni x3"
        json.dump(bad2, open(cpath, "w"))
        check("reintroduced Bonferroni rejected", refuses(load_contract, tmp))

        bad3 = json.loads(json.dumps(good))
        bad3["endpoints"]["P3_absolute"]["applies_to"] = "reference field only"
        json.dump(bad3, open(cpath, "w"))
        check("P3 narrowed to the reference field rejected", refuses(load_contract, tmp))

        bad4 = json.loads(json.dumps(good))
        bad4["endpoints"]["P1_geometry"]["alpha_1"] = 0.003
        json.dump(bad4, open(cpath, "w"))
        check("incoherent alpha split rejected", refuses(load_contract, tmp))

        bad5 = json.loads(json.dumps(good))
        bad5["authority"]["binds"]["frozen_foundation"]["sha256"] = "0" * 64
        json.dump(bad5, open(cpath, "w"))
        check("bad foundation hash rejected (fail closed)", refuses(load_contract, tmp))

        bad6 = json.loads(json.dumps(good))
        bad6["authority"]["binds"]["design_document"]["sha256"] = "1" * 64
        json.dump(bad6, open(cpath, "w"))
        check("design identity mismatch rejected", refuses(load_contract, tmp))

        bad7 = json.loads(json.dumps(good))
        del bad7["endpoints"]["P4_entropy"]
        json.dump(bad7, open(cpath, "w"))
        check("missing mandatory endpoint rejected", refuses(load_contract, tmp))

        bad8 = json.loads(json.dumps(good))
        bad8["contract_version"] = "9.9.9"
        json.dump(bad8, open(cpath, "w"))
        check("unsupported contract version rejected", refuses(load_contract, tmp))


# ----------------------------------------------------------------- beta tests
def test_beta() -> None:
    f = field_for(2)                      # theta2, anisotropic, rotated 30 deg
    sigma = inv(f.H)
    pts = exact_covariance_points(sigma, beta=1.0)
    S = sample_covariance(pts, f.x_star)
    check("hand-written points reproduce sigma exactly",
          max(abs(S[i][j] - sigma[i][j]) / abs(sigma[i][j]) for i in range(2) for j in range(2)) < 1e-12)
    check("ideal beta = 1 recovered exactly", abs(beta_mle(f.H, S) - 1.0) < 1e-12,
          f"{beta_mle(f.H, S):.15f}")
    for beta_true in (0.75, 1.3):
        p = exact_covariance_points(sigma, beta=beta_true)
        check(f"beta_true={beta_true} recovered, estimate never forced to 1",
              abs(beta_mle(f.H, sample_covariance(p, f.x_star)) - beta_true) < 1e-12)
    H2 = [[2 * f.H[i][j] for j in range(2)] for i in range(2)]
    check("scalar H scaling: beta_hat halves exactly",
          abs(beta_mle(f.H, S) / beta_mle(H2, S) - 2.0) < 1e-12)
    lam, q = jacobi(f.H)
    def modes(d1, d2):
        d = [[lam[0] * (1 + d1), 0.0], [0.0, lam[1] * (1 + d2)]]
        from e1a_v4.numerics import TT
        return mm(mm(q, d), TT(q))
    check("differential stiffness with zero mean leaves beta exactly unchanged",
          abs(beta_mle(modes(0.02, -0.02), S) - 1.0) < 1e-9,
          f"{beta_mle(modes(0.02, -0.02), S):.12f}")
    check("mean stiffness error moves beta by 1/(1+delta_bar)",
          abs(beta_mle(modes(0.03, 0.03), S) - 1.0 / 1.03) < 1e-9)
    from e1a_v4.branch_a import rotation
    from e1a_v4.numerics import TT
    r1 = rotation(1.0)
    Hrot = mm(mm(r1, f.H), TT(r1))
    ratio = max(lam) / min(lam)
    predicted = 2.0 / (2.0 + math.sin(math.radians(1.0)) ** 2 * (ratio + 1 / ratio - 2))
    check("orientation error enters beta only at second order, exactly",
          abs(beta_mle(Hrot, S) - predicted) < 1e-9,
          f"{beta_mle(Hrot, S):.12f} vs {predicted:.12f}")
    collinear = [[1.0, 2.0], [-1.0, -2.0], [2.0, 4.0], [-2.0, -4.0]]
    Sc = sample_covariance(collinear, [0.0, 0.0])
    check("rank-deficient S refused, not regularised",
          refuses(rank_guard, Sc, BINDING.rank_tol))


# ----------------------------------------------------------------- geometry tests
def test_geometry() -> None:
    H = [[3.0, 0.7], [0.7, 2.0]]
    S = [[0.42, -0.11], [-0.11, 0.63]]
    K = inv(S)
    H2 = [[2 * H[i][j] for j in range(2)] for i in range(2)]
    check("G1 deterministic fixture", abs(G1(H, K) - 0.035238095238095) < 1e-12, f"{G1(H,K):.15f}")
    check("G2 deterministic fixture", abs(G2(H, K) - 1.165935010017951) < 1e-9, f"{G2(H,K):.15f}")
    check("G4 deterministic fixture", abs(G4(H, K) - 0.114033105039501) < 1e-12, f"{G4(H,K):.15f}")
    lam, _ = jacobi(H)
    nm = [[1e6, 1e6], [1e6, 1e6]]
    blocks = resolvability_blocks(lam, nm, BINDING.theta_cap_deg)
    g3 = G3(H, K, blocks)
    check("G3 deterministic fixture", abs(max(g3) - 4.065051177078) < 1e-9, f"{max(g3):.12f}")
    pts = [[0.10, -0.20], [-0.30, 0.15], [0.25, 0.05], [-0.05, -0.35],
           [0.40, 0.30], [-0.45, 0.10], [0.05, 0.45], [-0.15, -0.05]]
    check("G5 deterministic fixture", abs(G5(pts, H, [0.0, 0.0]) - 0.961945787584) < 1e-9,
          f"{G5(pts,H,[0.0,0.0]):.12f}")
    check("G1 scale-invariant in H", abs(G1(H, K) - G1(H2, K)) < 1e-15)
    check("G2 scale-invariant in H", abs(G2(H, K) - G2(H2, K)) < 1e-12)
    check("G3 scale-invariant in H", abs(max(G3(H, K, blocks)) - max(G3(H2, K, blocks))) < 1e-12)
    check("G4 scale-invariant in H", abs(G4(H, K) - G4(H2, K)) < 1e-15)
    check("G5 scale-invariant in H", abs(G5(pts, H, [0.0, 0.0]) - G5(pts, H2, [0.0, 0.0])) < 1e-12)
    two_valued = [[1.0, 0.5], [-1.0, -0.5], [1.0, -0.5], [-1.0, 0.5]]
    identity = [[1.0, 0.0], [0.0, 1.0]]
    check("G5 is the kurtosis estimator, not a raw fourth moment",
          abs(G5(two_valued, identity, [0.0, 0.0]) - 2.0) < 1e-12,
          "a two-valued coordinate has g2 = m4/m2^2 - 3 = -2 exactly; "
          f"a raw fourth moment would give {sum(v[0]**4 for v in two_valued)/4:.1f}")
    check("G5 refuses a degenerate whitened coordinate rather than returning NaN",
          refuses(G5, [[1.0, 0.0], [-1.0, 0.0], [1.0, 0.0], [-1.0, 0.0]],
                  identity, [0.0, 0.0]))


def test_mode_resolution() -> None:
    n12 = 224726.0
    cap = BINDING.theta_cap_deg
    boundary = resolvability_boundary_ratio(n12, cap)
    check("boundary ratio matches the adopted design", abs(boundary - 1.024467) < 1e-5,
          f"{boundary:.6f} at theta_cap={cap} deg")
    check("perfectly circular field is merged", not resolvable(1.0, 1.0, n12, cap))
    check("slightly below boundary merged", not resolvable(1.0, boundary * 0.999, n12, cap))
    check("exactly at boundary merged (equality merges)",
          not resolvable(1.0, boundary, n12, cap))
    check("slightly above boundary resolved", resolvable(1.0, boundary * 1.001, n12, cap))
    check("strongly elliptical theta2-like field resolved", resolvable(1.0, 2.5, n12, cap))
    nm = [[n12, n12], [n12, n12]]
    check("circular field gives ONE block, no inferred directions",
          resolvability_blocks([1.0, 1.0], nm, cap) == [[0, 1]])
    check("elliptical field gives TWO blocks",
          resolvability_blocks([1.0, 2.5], nm, cap) == [[0], [1]])


def test_status_propagation() -> None:
    f = field_for(0)
    pts = exact_covariance_points(inv(f.H))
    ok = analyse_field(f, pts, rank_tol=BINDING.rank_tol,
                       theta_cap_deg=BINDING.theta_cap_deg, phi_modes=(0.9, 0.9))
    check("valid analysis reaches ESTIMATED", ok.status is AnalysisStatus.ESTIMATED)
    check("ESTIMATED result exposes beta", ok.require_beta() is not None)
    collinear = [[1.0, 2.0], [-1.0, -2.0], [2.0, 4.0], [-2.0, -4.0]]
    bad = analyse_field(f, collinear, rank_tol=BINDING.rank_tol,
                        theta_cap_deg=BINDING.theta_cap_deg, phi_modes=(0.9, 0.9))
    check("rank failure yields RANK_GUARD_FAIL", bad.status is AnalysisStatus.RANK_GUARD_FAIL)
    check("no beta on a refused analysis", bad.beta_hat is None)
    check("require_beta fails closed instead of crashing on a missing key",
          refuses(bad.require_beta))
    invalid = BranchAField(field_id="npd", H_U=[[1.0, 2.0], [2.0, 1.0]], T=298.0,
                           x_star=[0.0, 0.0], k_modes=(1.0, 1.0), rot_deg=0.0,
                           viscosity=1e-3, bead_radius=1e-6, calibration_route=ROUTE)
    res = analyse_field(invalid, pts, rank_tol=BINDING.rank_tol,
                        theta_cap_deg=BINDING.theta_cap_deg, phi_modes=(0.9, 0.9))
    check("non-positive-definite Branch A yields BRANCH_A_INVALID",
          res.status is AnalysisStatus.BRANCH_A_INVALID)


# ----------------------------------------------------------------- effective size
def test_effective_size() -> None:
    for n in (2, 3, 5, 17, 64, 257):
        for x in (0.0, 0.25, 0.5, 0.81873):
            check(f"closed form == finite sum (n={n}, x={x})",
                  abs(A_closed_form(x, n) - A_from_sum(x, n)) < 1e-12)
    f = field_for(2)
    dt = 1.2e-4
    phis = [phi_of(dt, tau) for tau in f.tau_modes]
    n = int(round(240.0 / dt))
    check("anisotropic field: modes have DIFFERENT effective sizes",
          abs(N_element(phis[0], phis[0], n) - N_element(phis[1], phis[1], n)) > 1.0,
          f"{N_element(phis[0],phis[0],n):.0f} vs {N_element(phis[1],phis[1],n):.0f}")
    check("cross element uses phi_a*phi_b, lying between the diagonals",
          min(N_element(phis[0], phis[0], n), N_element(phis[1], phis[1], n))
          < N_element(phis[0], phis[1], n)
          < max(N_element(phis[0], phis[0], n), N_element(phis[1], phis[1], n)))
    check("second moments use A2 (x = phi^2)",
          abs(N_element(phis[0], phis[0], n) - n / A_closed_form(phis[0] ** 2, n)) < 1e-6)
    check("G5 uses A4 (x = phi^4)",
          abs(N_g2(phis[0], n) - n / A_closed_form(phis[0] ** 4, n)) < 1e-6)
    check("N_g2 is about twice N_2, as the adopted design records",
          1.85 < N_g2(phis[0], n) / N_element(phis[0], phis[0], n) < 2.01,
          f"ratio {N_g2(phis[0],n)/N_element(phis[0],phis[0],n):.3f}")
    check("var(g2) = 24/N_g2", abs(var_g2(phis[0], n) - 24.0 / N_g2(phis[0], n)) < 1e-18)
    check("sigma_stat positive and small at the declared record length",
          0.0 < sigma_stat(phis, n) < 0.01, f"{sigma_stat(phis,n)*100:.4f}%")


# ----------------------------------------------------------------- endpoint tests
def analyses_from(betas: dict[str, float | None]) -> dict[str, FieldAnalysis]:
    out = {}
    for fid, b in betas.items():
        if b is None:
            out[fid] = FieldAnalysis(fid, AnalysisStatus.RANK_GUARD_FAIL, "fixture")
        else:
            out[fid] = FieldAnalysis(fid, AnalysisStatus.ESTIMATED, "", beta_hat=b)
    return out


IDS = [f["id"] for f in BINDING.fields]
REF = BINDING.reference_field_id
UNC = UncertaintyModel(sigma_cm=0.0115, sigma_fs=0.00242747,
                       sigma_stat={i: 0.002 for i in IDS})
TIGHT = UncertaintyModel(sigma_cm=1e-9, sigma_fs=1e-9, sigma_stat={i: 1e-9 for i in IDS})


def test_p2() -> None:
    r = p2_cross_field(analyses_from({i: 1.0 for i in IDS}), BINDING, UNC)
    check("P2 clear pass when every ratio is 1", r.passed)
    r = p2_cross_field(analyses_from({**{i: 1.0 for i in IDS}, IDS[1]: 1.10}), BINDING, UNC)
    check("P2 clear fail at a 10% disparity", not r.passed)
    r = p2_cross_field(analyses_from({**{i: 1.0 for i in IDS}, IDS[2]: 1.06}), BINDING, UNC)
    check("P2 one failing comparison fails the whole endpoint", not r.passed,
          "intersection-union: all three required")
    delta = BINDING.delta_cross
    inside = p2_cross_field(analyses_from({**{i: 1.0 for i in IDS}, IDS[1]: 1.0 + delta * 0.5}),
                            BINDING, TIGHT)
    outside = p2_cross_field(analyses_from({**{i: 1.0 for i in IDS}, IDS[1]: 1.0 + delta * 1.5}),
                             BINDING, TIGHT)
    check("P2 boundary convention: interval must lie WHOLLY inside the margin",
          inside.passed and not outside.passed)
    r = p2_cross_field(analyses_from({**{i: 1.0 for i in IDS}, IDS[3]: None}), BINDING, UNC)
    check("P2 fails closed on a non-estimated comparison field", not r.passed)
    r = p2_cross_field(analyses_from({**{i: 1.0 for i in IDS}, REF: None}), BINDING, UNC)
    check("P2 fails closed on a non-estimated REFERENCE", not r.passed)
    wide = p2_cross_field(analyses_from({i: 1.0 for i in IDS}), BINDING,
                          UncertaintyModel(0.0, 0.02, {i: 0.0 for i in IDS}))
    check("P2 is equivalence, not 'CI contains 1': a wide interval FAILS", not wide.passed,
          "ratio exactly 1 but the interval overflows the margin")


def test_p3() -> None:
    r = p3_absolute(analyses_from({i: 1.0 for i in IDS}), BINDING, TIGHT)
    check("P3 all four fields pass", r.passed)
    r = p3_absolute(analyses_from({**{i: 1.0 for i in IDS}, IDS[2]: 1.12}), BINDING, TIGHT)
    check("P3 one field outside 5% fails the endpoint", not r.passed)
    r = p3_absolute(analyses_from({**{i: 1.0 for i in IDS}, IDS[3]: None}), BINDING, TIGHT)
    check("P3 one non-estimated field fails the endpoint", not r.passed)
    r = p3_absolute(analyses_from({**{i: 1.12 for i in IDS}, REF: 1.0}), BINDING, TIGHT)
    check("P3 reference alone passing is insufficient", not r.passed,
          "every tested field is required")
    check("P3 evaluates all four declared fields", len(r.rows) == 4)


def test_p4() -> None:
    r = p4_consistency(BINDING)
    check("P4 declared consistency relation passes", r.passed)
    check("P4 needs no Branch-B observations",
          "observations" not in p4_consistency.__code__.co_varnames)
    def altered(E, T):
        d = declared_entropy_relation(E, T)
        d["ds_tot"] = 1e-20
        return d
    check("P4 fails on a deliberately altered relation",
          not p4_consistency(BINDING, relation=altered).passed)
    def wrong_sign(E, T):
        d = declared_entropy_relation(E, T)
        d["ds_sys"] = +K_B * E
        return d
    check("P4 fails when ds_sys loses its sign",
          not p4_consistency(BINDING, relation=wrong_sign).passed)
    meds = [row[2] for row in r.rows]
    check("ds_med identical across temperatures though the heat differs",
          abs(max(meds) - min(meds)) < 1e-12 and
          abs(r.rows[0][1] - r.rows[1][1]) > 1e-22,
          f"ds_med {meds[0]:.4f} k_B at both T; heat differs by "
          f"{100*(r.rows[1][1]/r.rows[0][1]-1):.2f}%")


# ----------------------------------------------------------------- P1 semantics
def test_p1_semantics() -> None:
    f = field_for(0)
    pts = exact_covariance_points(inv(f.H))
    a = analyse_field(f, pts, rank_tol=BINDING.rank_tol,
                      theta_cap_deg=BINDING.theta_cap_deg, phi_modes=(0.9, 0.9))
    pid = procedure_identity(BINDING, {"stage": "test"}, ROOT)

    def cond_for(fld, n, phis=(0.9, 0.9), R=200, alpha=None):
        """The COMPLETE calibration condition. Replaces the (H_A, n) pair, which
        did not identify a null law."""
        return CalibrationCondition(
            field_id=fld.field_id, m=2, H_normalised=normalised_H(fld.H), n=n,
            dt=1.2e-4, tau_modes=tuple(-1.2e-4 / math.log(p) for p in phis),
            phi_modes=tuple(phis), mode_blocks=((0,), (1,)),
            theta_cap_deg=BINDING.theta_cap_deg,
            alpha_1=BINDING.alpha_1 if alpha is None else alpha, replicates=R,
            gates=BLOCK1_GATES, calibrator_identity="TEST-FIXTURE",
            procedure_identity=pid, contract_sha256=BINDING.sha256,
            plan_sha256="0" * 64)

    cond = cond_for(f, len(pts))
    check("P1 refuses when calibration is ABSENT",
          refuses(p1_geometry, a, BINDING, procedure_identity=pid, condition=cond,
                  artifact=None),
          "no hard-coded threshold, no v3 substitution")
    fixture = CalibrationArtifact(
        kind="block1_min_p", procedure_identity=pid, field_id=f.field_id,
        n=len(pts), m=2, alpha_1=BINDING.alpha_1,
        null_draws={g: tuple(0.001 * k for k in range(1, 201)) for g in
                    ("G1", "G2", "G3", "G4")},
        condition=cond,
        provenance="HAND-WRITTEN FIXTURE, not calibration", is_fixture=True)
    check("fixture artifact accepted when the complete condition matches",
          require_calibration(fixture, procedure_identity=pid, condition=cond) is fixture)
    other = CalibrationArtifact(
        kind="block1_min_p", procedure_identity="0" * 64, field_id=f.field_id,
        n=len(pts), m=2, alpha_1=BINDING.alpha_1,
        null_draws=fixture.null_draws,
        condition=cond_for(f, len(pts)).__class__(**{**cond.__dict__,
                                                    "procedure_identity": "0" * 64}),
        is_fixture=True)
    check("artifact from a different procedure identity refused",
          refuses(require_calibration, other, procedure_identity=pid, condition=cond))
    g = field_for(2)
    check("artifact calibrated at a different geometry refused",
          refuses(require_calibration, fixture, procedure_identity=pid,
                  condition=cond_for(g, len(pts))))
    check("artifact calibrated at a different TEMPORAL law refused",
          refuses(require_calibration, fixture, procedure_identity=pid,
                  condition=cond_for(f, len(pts), phis=(0.5, 0.5))),
          "equal geometry, different phi: the superseded signature accepted this")
    t0, t1 = field_for(0), field_for(1)
    check("the superseded geometry signature CANNOT tell theta0 from theta1",
          branch_a_signature(t0.H, 2_000_000) == branch_a_signature(t1.H, 2_000_000),
          "both isotropic: identical eigenvalue ratios, tau differs by 2.1x")
    check("the complete condition CAN",
          cond_for(t0, 2_000_000, phis=(0.4890438527906016,) * 2).sha256
          != cond_for(t1, 2_000_000, phis=(0.22265394220297993,) * 2).sha256,
          "field_id and phi_modes both differ")
    check("block-2 p-value is a number in [0,1]",
          0.0 <= block2_p_value(0.01, 0.9, 10000) <= 1.0)
    check("block-2 p-value shrinks as G5 grows",
          block2_p_value(5.0, 0.9, 10000) < block2_p_value(0.01, 0.9, 10000))
    check("union bound: alpha_1 + alpha_2 == alpha_geom, no independence asserted",
          abs(BINDING.alpha_1 + BINDING.alpha_2 - BINDING.alpha_geom) < 1e-15)


# ----------------------------------------------------------------- identity + boundary
def test_procedure_identity() -> None:
    a = procedure_identity(BINDING, {"stage": "bounded_implementation"}, ROOT)
    b = procedure_identity(BINDING, {"stage": "bounded_implementation"}, ROOT)
    c = procedure_identity(BINDING, {"stage": "something_else"}, ROOT)
    check("same inputs -> same procedure identity", a == b, a[:16] + "...")
    check("relevant changed input -> different identity", a != c)
    check("identity is a sha256 hex digest", len(a) == 64 and all(ch in "0123456789abcdef" for ch in a))


def test_information_boundary() -> None:
    class FakeBranchB:
        sample_covariance = [[1.0, 0.0], [0.0, 1.0]]
    check("Branch-A construction refuses an object carrying Branch-B output",
          refuses(assert_not_branch_b, FakeBranchB(), "field specification"))
    check("forbidden corner-frequency route refused", refuses(
        build_field, BINDING, BINDING.fields[0],
        calibration_route="corner_frequency_fluctuation_spectrum_route_k_equals_2pi_fc_gamma",
        viscosity=1e-3, bead_radius=1e-6))
    check("forbidden equipartition route refused", refuses(
        build_field, BINDING, BINDING.fields[0],
        calibration_route="equipartition_k_equals_kBT_over_sigma_squared",
        viscosity=1e-3, bead_radius=1e-6))
    check("unlisted route refused rather than assumed", refuses(
        build_field, BINDING, BINDING.fields[0], calibration_route="guesswork",
        viscosity=1e-3, bead_radius=1e-6))
    f = field_for(0)
    c = 1.37
    blinded = f.blinded(c)
    sigma = inv(f.H)
    S = sample_covariance(exact_covariance_points(sigma), f.x_star)
    check("blinded scale control recovers beta = 1/c exactly",
          abs(beta_mle(blinded.H, S) - 1.0 / c) < 1e-12,
          f"{beta_mle(blinded.H,S):.12f} vs {1/c:.12f}")
    check("blinding does not mutate the primary field", abs(beta_mle(f.H, S) - 1.0) < 1e-12)


def test_no_stochastic_execution() -> None:
    f = field_for(0)
    w = WorldConfig(f, 240.0, 1.2e-4)
    check("world config computes per-mode tau deterministically",
          len(w.tau_modes) == 2 and all(t > 0 for t in w.tau_modes))
    check("stationary covariance available without any draw",
          len(w.stationary_covariance) == 2)
    spec = w.stationary_initial_spec()
    check("stationary initial distribution is a SPECIFICATION, not a draw",
          spec["drawn_in_this_stage"] is False and spec["burn_in_steps"] == 0)
    check("the only available RNG refuses every call", refuses(ForbiddenRNG().normal, 1))
    check("trajectory generation refuses", refuses(w.sample, ForbiddenRNG()))
    sm = SeedMap()
    check("no seed values assigned in this stage",
          refuses(sm.stream_for, SeedFamily.CALIBRATION, SeedFamily.CALIBRATION))
    sm2 = SeedMap({SeedFamily.CALIBRATION: 1, SeedFamily.VALIDATION: 2})
    check("a consumer cannot read another family's stream",
          refuses(sm2.stream_for, SeedFamily.VALIDATION, SeedFamily.CALIBRATION))
    check("a family may read its own stream",
          sm2.stream_for(SeedFamily.CALIBRATION, SeedFamily.CALIBRATION) == 1)
    check("duplicate seeds across families refused",
          refuses(SeedMap, {SeedFamily.CALIBRATION: 7, SeedFamily.VALIDATION: 7}))


def main() -> int:
    groups = (
        ("contract binding", test_contract),
        ("beta estimator", test_beta),
        ("G1-G5 geometry", test_geometry),
        ("mode resolvability", test_mode_resolution),
        ("status propagation", test_status_propagation),
        ("effective sample size", test_effective_size),
        ("P1 decision semantics", test_p1_semantics),
        ("P2 cross-field", test_p2),
        ("P3 absolute", test_p3),
        ("P4 deterministic check", test_p4),
        ("procedure identity", test_procedure_identity),
        ("information boundary", test_information_boundary),
        ("no stochastic execution", test_no_stochastic_execution),
    )
    for label, fn in groups:
        print(f"\n{label}")
        fn()
    print(f"\nE1a v4 implementation gate: {PASSED} passed, {FAILED} failed, {len(groups)} groups")
    print("Execution class: NON-MODEL-ADVANCING STATIC/PURE (this suite only)")
    print(f"  contract sha256      : {BINDING.sha256}")
    print(f"  procedure identity   : {procedure_identity(BINDING, {'stage': 'bounded_implementation'}, ROOT)}")
    print("  stochastic calibration: NOT AUTHORISED IN THIS STAGE")
    print("  synthetic campaign    : NOT AUTHORISED IN THIS STAGE")
    print("  random numbers drawn  : 0")
    print("  trajectories generated: 0")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())
