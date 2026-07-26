"""
Numerical regression validation for Foundation Note V2.8 (discrete draft).

These are finite numerical regression validations of the V2.8 draft. Passing them is
not a mathematical proof. They test declared fixtures, deterministic samples, and
negative controls.

The D0 reference model implemented below is LOCAL TO THIS TEST FILE. It is not a new
production engine and deliberately does NOT import or reuse energy_balance.py or any
ebu_v2x module: Model D0 (synchronous, unconstrained, loss-aware, explicit Euler) is
intentionally different from the DE engine family (Foundation_v2.8_discrete_draft.md,
Def 3.2 vs Def 3.3), so validating D0 against an engine implementation would be a
category error. Plain stdlib, direct execution:  python3 test_v28.py
"""
from __future__ import annotations
import math
import random
import sys
from dataclasses import dataclass

SEED = 20260726

PASS = 0
FAIL = 0
GROUPS: list[list] = []          # [title, passed, failed]
WORST = {                        # residual bookkeeping for the final report
    "remainder_margin": -math.inf,   # max over checks of |r_n| - R_n (<= 0 expected)
    "descent_margin": -math.inf,     # max over checks of V(x^{n+1}) - V(x^n) where
                                     # a theorem asserted non-increase (<= 0 expected)
    "identity_residual": 0.0,        # max |lhs - rhs| over exact identities
    "eig_residual": 0.0,             # max eigenpair residual of the Jacobi solver
}


def group(title: str) -> None:
    GROUPS.append([title, 0, 0])
    print(f"[{len(GROUPS)}] {title}")


def check(name: str, ok: bool, detail: str = "", fail_detail: str = "") -> None:
    global PASS, FAIL
    if ok:
        PASS += 1
        GROUPS[-1][1] += 1
        print(f"  PASS  {name}" + (f"  ({detail})" if detail else ""))
    else:
        FAIL += 1
        GROUPS[-1][2] += 1
        print(f"  FAIL  {name}" + (f"  ({detail})" if detail else ""))
        if fail_detail:
            print(f"        reproduce: {fail_detail}")


def note_descent(dV: float) -> None:
    WORST["descent_margin"] = max(WORST["descent_margin"], dV)


def note_remainder(margin: float) -> None:
    WORST["remainder_margin"] = max(WORST["remainder_margin"], margin)


def note_identity(res: float) -> None:
    WORST["identity_residual"] = max(WORST["identity_residual"], res)


# ===========================================================================
# D0 reference model (Def 2.1-2.4, 3.2 of the V2.8 draft) - local to this file
# ===========================================================================
@dataclass(frozen=True)
class Cell:
    alpha: float
    beta: float
    chi: float
    L: float
    U: float
    R: float


def v_cell(c: Cell, x: float) -> float:
    """v_i(x) = alpha[L-x]_+^2 + beta[x-U]_+^2 + chi[R-x]_+^2  (Def 2.1)."""
    dv = max(0.0, c.L - x)
    ev = max(0.0, x - c.U)
    rv = max(0.0, c.R - x)
    return c.alpha * dv * dv + c.beta * ev * ev + c.chi * rv * rv


def mu_cell(c: Cell, x: float) -> float:
    """Analytic marginal mu_i = v_i'(x)  (Assumption 2.5, branchwise)."""
    m = 0.0
    if x < c.L:
        m += -2.0 * c.alpha * (c.L - x)
    if x > c.U:
        m += 2.0 * c.beta * (x - c.U)
    if x < c.R:
        m += -2.0 * c.chi * (c.R - x)
    return m


def V_total(cells, x) -> float:
    return sum(v_cell(c, xi) for c, xi in zip(cells, x))


def branch_slope(c: Cell, p: float) -> float:
    """a.e. second derivative 2[alpha 1_{x<L} + beta 1_{x>U} + chi 1_{x<R}]."""
    return 2.0 * (c.alpha * (p < c.L) + c.beta * (p > c.U) + c.chi * (p < c.R))


def cell_LV_exact(c: Cell) -> float:
    """Exact branchwise sup of v_i'' (sum of simultaneously active weights)."""
    bps = sorted({c.L, c.U, c.R})
    reps = [bps[0] - 1.0]
    reps += [(a + b) / 2.0 for a, b in zip(bps, bps[1:]) if b > a]
    reps += [bps[-1] + 1.0]
    return max(branch_slope(c, p) for p in reps)


def LV_exact(cells) -> float:
    return max(cell_LV_exact(c) for c in cells)


def LV_safe(cells) -> float:
    """Safe upper bound  L_V <= 2 max_i [max(alpha_i, beta_i) + chi_i]."""
    return 2.0 * max(max(c.alpha, c.beta) + c.chi for c in cells)


@dataclass(frozen=True)
class Edge:
    i: int
    j: int
    M: float
    theta: float
    eta: float


def edge_col(e: Edge, n: int) -> list[float]:
    """Lossy state-change column S_e: -1 at source, +eta at destination (Def 2.2)."""
    col = [0.0] * n
    col[e.i] += -1.0
    col[e.j] += e.eta
    return col


def forces_flux(cells, edges, x):
    """Loss-aware force f_e = mu_i - eta mu_j; Onsager flux J_e = M[f-theta]_+."""
    m = [mu_cell(c, xi) for c, xi in zip(cells, x)]
    f = [m[e.i] - e.eta * m[e.j] for e in edges]
    J = [e.M * max(0.0, fe - e.theta) for e, fe in zip(edges, f)]
    return m, f, J


def transport(edges, J, n) -> list[float]:
    """S J."""
    sj = [0.0] * n
    for e, Je in zip(edges, J):
        sj[e.i] -= Je
        sj[e.j] += e.eta * Je
    return sj


def d0_step(cells, edges, x, u, dt):
    """Synchronous frozen-state explicit-Euler D0 step (Def 3.2):
       x^{n+1} = x^n + dt (u + S J),  everything evaluated at x^n. No clipping."""
    m, f, J = forces_flux(cells, edges, x)
    sj = transport(edges, J, len(x))
    xn = [xi + dt * (ui + si) for xi, ui, si in zip(x, u, sj)]
    return xn, m, f, J, sj


def dissipation(edges, J) -> float:
    return sum(Je * Je / e.M + e.theta * Je for e, Je in zip(edges, J))


def transport_loss(edges, J) -> float:
    """Ledger outflow removed by lossy transport per unit time: sum (1-eta) J."""
    return sum((1.0 - e.eta) * Je for e, Je in zip(edges, J))


# ===========================================================================
# Symmetric Jacobi eigensolver (stdlib only), for Theorems 5.2 / 5.5
# ===========================================================================
def jacobi_eigs(A0, tol_factor=1e-13, max_rot=20000):
    """Classic Jacobi rotation eigensolver for a symmetric matrix. Returns
    (eigenvalues, eigenvectors) with eigenvectors[k] the k-th (unit) eigenvector.
    Raises AssertionError if the off-diagonal tolerance is not reached within
    max_rot rotations (a silent non-converged result must never be used)."""
    n = len(A0)
    A = [row[:] for row in A0]
    Vm = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
    if n == 1:
        return [A[0][0]], [[1.0]]
    scale = max(1.0, max(abs(A[i][j]) for i in range(n) for j in range(n)))
    tol = tol_factor * scale
    converged = False
    for _ in range(max_rot):
        p, q, mx = 0, 1, 0.0
        for i in range(n):
            for j in range(i + 1, n):
                if abs(A[i][j]) > mx:
                    mx, p, q = abs(A[i][j]), i, j
        if mx <= tol:
            converged = True
            break
        app, aqq, apq = A[p][p], A[q][q], A[p][q]
        theta = (aqq - app) / (2.0 * apq)
        t = (1.0 if theta >= 0 else -1.0) / (abs(theta) + math.sqrt(theta * theta + 1.0))
        cph = 1.0 / math.sqrt(t * t + 1.0)
        sph = t * cph
        for k in range(n):
            if k != p and k != q:
                akp, akq = A[k][p], A[k][q]
                A[k][p] = A[p][k] = cph * akp - sph * akq
                A[k][q] = A[q][k] = sph * akp + cph * akq
        A[p][p] = cph * cph * app - 2.0 * sph * cph * apq + sph * sph * aqq
        A[q][q] = sph * sph * app + 2.0 * sph * cph * apq + cph * cph * aqq
        A[p][q] = A[q][p] = 0.0
        for k in range(n):
            vkp, vkq = Vm[k][p], Vm[k][q]
            Vm[k][p] = cph * vkp - sph * vkq
            Vm[k][q] = sph * vkp + cph * vkq
    if not converged:
        final_off = max(abs(A[i][j]) for i in range(n) for j in range(i + 1, n))
        raise AssertionError(
            f"jacobi_eigs did not converge: n={n}, max_rot={max_rot} exhausted, "
            f"final max off-diagonal {final_off:.3e} > tol {tol:.3e}")
    eigvals = [A[i][i] for i in range(n)]
    eigvecs = [[Vm[i][k] for i in range(n)] for k in range(n)]
    return eigvals, eigvecs


def matvec(A, v):
    return [sum(a * b for a, b in zip(row, v)) for row in A]


def eig_residual(A0, eigvals, eigvecs) -> float:
    """max_k || A v_k - lambda_k v_k ||_2  - independent eigenpair verification."""
    worst = 0.0
    for lam, v in zip(eigvals, eigvecs):
        Av = matvec(A0, v)
        r = math.sqrt(sum((a - lam * b) ** 2 for a, b in zip(Av, v)))
        worst = max(worst, r)
    return worst


def gram_G(edges, n):
    """G = D_M^{1/2} S^T S D_M^{1/2} = (S D_M^{1/2})^T (S D_M^{1/2}), symmetric PSD;
       lambda_max(G) = ||S D_M^{1/2}||_2^2  (Theorem 5.2)."""
    cols = [edge_col(e, n) for e in edges]
    E = len(edges)
    return [[math.sqrt(edges[a].M * edges[b].M)
             * sum(ca * cb for ca, cb in zip(cols[a], cols[b]))
             for b in range(E)] for a in range(E)]


def spectral_norm_sq(edges, n) -> float:
    """||S D_M^{1/2}||_2^2 via Jacobi, with hard guards on EVERY matrix: eigenpair
    residuals within a scale-aware tolerance, Gram PSD within roundoff, finite
    lambda_max. Any violation raises with the offending matrix and residual."""
    if not edges:
        return 0.0
    G = gram_G(edges, n)
    eigvals, eigvecs = jacobi_eigs(G)
    scale = max(1.0, max(abs(v) for row in G for v in row))
    res = eig_residual(G, eigvals, eigvecs)
    if res > 1e-10 * scale:
        raise AssertionError(
            f"eigenpair residual {res:.3e} exceeds tolerance {1e-10 * scale:.3e} "
            f"for Gram matrix G={G}")
    neg = min(eigvals)
    if neg < -1e-10 * scale:
        raise AssertionError(
            f"Gram matrix not PSD within roundoff: min eigenvalue {neg:.3e} "
            f"(tolerance {-1e-10 * scale:.3e}) for G={G}")
    lam_max = max(eigvals)
    if not math.isfinite(lam_max):
        raise AssertionError(f"non-finite lambda_max {lam_max!r} for G={G}")
    WORST["eig_residual"] = max(WORST["eig_residual"], res)
    return lam_max


def gershgorin_bound(edges, n) -> float:
    """Row-sum bound on lambda_max(D_M S^T S)  (Remark 5.4, via similarity)."""
    cols = [edge_col(e, n) for e in edges]
    E = len(edges)
    dots = [[sum(ca * cb for ca, cb in zip(cols[a], cols[b])) for b in range(E)]
            for a in range(E)]
    return max(edges[a].M * (dots[a][a] + sum(abs(dots[a][b])
               for b in range(E) if b != a)) for a in range(E))


def fixture_repr(cells, edges, x, u, dt) -> str:
    cs = [(c.alpha, c.beta, c.chi, c.L, c.U, c.R) for c in cells]
    es = [(e.i, e.j, e.M, e.theta, e.eta) for e in edges]
    return f"cells={cs} edges={es} x={x} u={u} dt={dt}"


# ===========================================================================
# [1] Marginals and corrected curvature (Assumption 2.5)
# ===========================================================================
def test_group1():
    group("marginals + corrected curvature L_V (Assumption 2.5)")
    h = 1e-5
    configs = [
        ("deficit+reserve overlap", Cell(1.0, 0.5, 0.7, 5.0, 15.0, 8.0),
         {"exact": 2 * (1.0 + 0.7)}),
        ("excess+reserve overlap", Cell(0.6, 0.8, 0.9, 2.0, 4.0, 9.0),
         {"exact": 2 * (0.8 + 0.9)}),
        ("single-penalty / flat band", Cell(1.0, 1.0, 0.0, 5.0, 15.0, 0.0),
         {"exact": 2.0}),
        ("R below L, strict safe bound", Cell(0.5, 2.0, 0.4, 6.0, 10.0, 3.0),
         {"exact": 4.0}),
    ]
    for name, c, expect in configs:
        bps = sorted({c.L, c.U, c.R})
        reps = [bps[0] - 2.0]
        reps += [(a + b) / 2.0 for a, b in zip(bps, bps[1:]) if b > a]
        reps += [bps[-1] + 2.0]
        # (a) analytic mu vs centered finite difference of v, away from switches
        worst_mu = max(abs(mu_cell(c, p) - (v_cell(c, p + h) - v_cell(c, p - h)) / (2 * h))
                       for p in reps)
        check(f"{name}: mu == central FD of v on every smooth interval",
              worst_mu < 1e-7, f"max err {worst_mu:.2e}")
        # (b) branchwise slope of mu (piecewise-linear => central FD exact)
        worst_sl = max(abs((mu_cell(c, p + h) - mu_cell(c, p - h)) / (2 * h)
                           - branch_slope(c, p)) for p in reps)
        check(f"{name}: FD slope of mu == 2[a 1_(x<L) + b 1_(x>U) + chi 1_(x<R)]",
              worst_sl < 1e-7, f"max err {worst_sl:.2e}")
        # (c) exact branchwise L_V matches hand-computed sup (sum of active weights)
        got = cell_LV_exact(c)
        check(f"{name}: exact L_V == {expect['exact']}",
              abs(got - expect["exact"]) < 1e-12, f"got {got}")
        # (d) safe bound dominates exact
        safe = LV_safe([c])
        check(f"{name}: safe bound 2[max(a,b)+chi] >= exact",
              safe >= got - 1e-12, f"safe {safe} vs exact {got}")
    strict = configs[3][1]
    check("safe bound is strictly larger when chi never overlaps the max branch",
          LV_safe([strict]) > cell_LV_exact(strict) + 1e-9,
          f"safe {LV_safe([strict])} > exact {cell_LV_exact(strict)}")
    flat = configs[2][1]
    check("no-penalty interior: mu == 0 and slope == 0",
          mu_cell(flat, 10.0) == 0.0 and branch_slope(flat, 10.0) == 0.0)


# ===========================================================================
# [2] Counterexample E - negative control for the old curvature constant
# ===========================================================================
def test_group2():
    group("Counterexample E: former max-form Lipschitz constant is too small")
    cells = [Cell(1.0, 1.0, 1.0, 0.0, 0.0, 0.0), Cell(1.0, 1.0, 1.0, 0.0, 0.0, 0.0)]
    edges = [Edge(0, 1, 1.0, 0.0, 1.0)]
    x = [-1.0, -2.0]
    u = [0.0, 0.0]
    dt = 0.4
    xn, m, f, J, sj = d0_step(cells, edges, x, u, dt)
    check("mu == (-4, -8)", abs(m[0] + 4.0) < 1e-12 and abs(m[1] + 8.0) < 1e-12,
          f"mu={m}")
    check("f == 4, J == 4", abs(f[0] - 4.0) < 1e-12 and abs(J[0] - 4.0) < 1e-12)
    check("(-1,-2) -> (-2.6,-0.4) at dt=0.4",
          abs(xn[0] + 2.6) < 1e-12 and abs(xn[1] + 0.4) < 1e-12, f"xn={xn}")
    V0, V1 = V_total(cells, x), V_total(cells, xn)
    check("V: 10 -> 13.84 (V increases)",
          abs(V0 - 10.0) < 1e-12 and abs(V1 - 13.84) < 1e-9 and V1 > V0,
          f"V {V0} -> {V1}")
    # corrected constant: sum of simultaneously active weights (fails if the old
    # max-form constant is accidentally restored, which would give 2 here)
    LVc = LV_exact(cells)
    check("corrected L_V == 2(alpha+chi) == 4 (old max-form would give 2)",
          abs(LVc - 4.0) < 1e-12, f"L_V={LVc}")
    L_old = 2.0 * max(cells[0].alpha, cells[0].beta, cells[0].chi)
    bound_old = 2.0 / (L_old * edges[0].M * (1.0 + edges[0].eta ** 2))
    bound_new = 2.0 / (LVc * edges[0].M * (1.0 + edges[0].eta ** 2))
    check("NEGATIVE CONTROL: former bound 0.5 permits dt=0.4 yet V increases",
          dt <= bound_old + 1e-12 and V1 > V0 + 1e-9,
          f"old bound {bound_old}, dV=+{V1 - V0:.4f}")
    check("corrected bound == 0.25 and forbids dt=0.4",
          abs(bound_new - 0.25) < 1e-12 and dt > bound_new)
    xn2, *_ = d0_step(cells, edges, x, u, bound_new)
    dV = V_total(cells, xn2) - V0
    note_descent(dV)
    check("at the corrected bound dt=0.25, V does not increase",
          dV <= 1e-9, f"dV={dV:.2e}")


# ===========================================================================
# [3] First-order and edge identities (Lemmas 4.1 / 4.2)
# ===========================================================================
def _identity_checks(tag, cells, edges, x):
    m, f, J = forces_flux(cells, edges, x)
    sj = transport(edges, J, len(x))
    lhs = sum(mi * si for mi, si in zip(m, sj))
    rhs_f = -sum(fe * Je for fe, Je in zip(f, J))
    rhs_d = -dissipation(edges, J)
    scale = 1.0 + abs(lhs)
    note_identity(abs(lhs - rhs_f))
    note_identity(abs(lhs - rhs_d))
    check(f"{tag}: mu^T S J == -sum f_e J_e (Lemma 4.1)",
          abs(lhs - rhs_f) < 1e-11 * scale, f"{lhs:.12f} vs {rhs_f:.12f}",
          fixture_repr(cells, edges, x, None, None))
    per_edge = max(abs(fe * Je - (Je * Je / e.M + e.theta * Je))
                   for e, fe, Je in zip(edges, f, J))
    note_identity(per_edge)
    check(f"{tag}: f_e J_e == J_e^2/M_e + theta_e J_e on every edge (Lemma 4.2)",
          per_edge < 1e-11 * scale, f"max edge residual {per_edge:.2e}",
          fixture_repr(cells, edges, x, None, None))
    return f, J


def test_group3():
    group("first-order and edge identities (Lemmas 4.1-4.2)")
    band = Cell(1.0, 0.5, 0.0, 5.0, 15.0, 0.0)
    # active edge, lossy, theta > 0
    f, J = _identity_checks("active lossy theta>0",
                            [band, band], [Edge(0, 1, 0.7, 0.05, 0.8)], [19.0, 2.0])
    check("fixture is genuinely active (J > 0)", J[0] > 0.0, f"J={J[0]:.4f}")
    # inactive edge: f <= theta -> J = 0, both identity sides vanish
    f, J = _identity_checks("inactive edge",
                            [band, band], [Edge(0, 1, 0.7, 0.5, 0.8)], [7.0, 8.0])
    check("fixture is genuinely inactive (J == 0)", J[0] == 0.0)
    # lossless, cost-free
    _identity_checks("eta=1 theta=0",
                     [band, band], [Edge(0, 1, 1.3, 0.0, 1.0)], [18.0, 3.0])
    # multi-edge graph with mixed active/inactive, eta<1 and eta=1, theta mixed
    cells4 = [band, band, Cell(1.0, 0.5, 0.7, 5.0, 15.0, 8.0), band]
    edges4 = [Edge(0, 1, 0.5, 0.05, 0.9), Edge(1, 2, 1.0, 0.0, 1.0),
              Edge(2, 3, 0.8, 0.1, 0.6), Edge(3, 0, 0.4, 0.05, 0.9),
              Edge(1, 0, 0.5, 0.05, 0.9)]
    f, J = _identity_checks("4-cell mixed graph",
                            cells4, edges4, [19.0, 10.0, 2.0, 7.0])
    check("mixed graph has both active and inactive edges",
          any(Je > 0 for Je in J) and any(Je == 0.0 for Je in J),
          f"J={[round(j, 3) for j in J]}")


# ===========================================================================
# [4] Discrete remainder inequality (Theorem 4.4)
# ===========================================================================
def _remainder_checks(tag, cells, edges, x, u, dts, expect_cross=False):
    LV = LV_exact(cells)
    for dt in dts:
        xn, m, f, J, sj = d0_step(cells, edges, x, u, dt)
        dx = [b - a for a, b in zip(x, xn)]
        r_n = V_total(cells, xn) - V_total(cells, x) - sum(mi * di for mi, di in zip(m, dx))
        usj = [ui + si for ui, si in zip(u, sj)]
        R_n = 0.5 * LV * dt * dt * sum(t * t for t in usj)
        note_remainder(abs(r_n) - R_n)
        ok_r = abs(r_n) <= R_n * (1 + 1e-9) + 1e-12
        check(f"{tag} dt={dt}: |r_n| <= R_n (two-sided remainder bound)",
              ok_r, f"|r_n|={abs(r_n):.6f}, R_n={R_n:.6f}",
              fixture_repr(cells, edges, x, u, dt))
        lhs = V_total(cells, xn) - V_total(cells, x)
        rhs = dt * sum(mi * ui for mi, ui in zip(m, u)) - dt * dissipation(edges, J) + R_n
        check(f"{tag} dt={dt}: full (*) inequality V(x+) - V(x) <= drive - diss + R_n",
              lhs <= rhs + 1e-9 * (1 + abs(rhs)), f"lhs={lhs:.6f}, rhs={rhs:.6f}",
              fixture_repr(cells, edges, x, u, dt))
    if expect_cross:
        _, _, _, _, sj = d0_step(cells, edges, x, u, dts[0])
        cross = sum(ui * si for ui, si in zip(u, sj))
        check(f"{tag}: drive-transport cross term u^T SJ is genuinely nonzero",
              abs(cross) > 1e-6, f"u^T SJ = {cross:.4f}")


def test_group4():
    group("discrete remainder inequality (Theorem 4.4)")
    band = Cell(1.0, 0.5, 0.0, 5.0, 15.0, 0.0)
    _remainder_checks("undriven one edge", [band, band],
                      [Edge(0, 1, 0.8, 0.05, 0.9)], [19.0, 2.0],
                      [0.0, 0.0], dts=[0.05, 0.2, 0.5])
    _remainder_checks("driven, nonzero cross term", [band, band],
                      [Edge(0, 1, 0.8, 0.05, 0.9)], [19.0, 2.0],
                      [1.2, -0.7], dts=[0.05, 0.2, 0.5], expect_cross=True)
    over = Cell(1.0, 0.5, 0.7, 5.0, 15.0, 8.0)
    _remainder_checks("overlapping reserve curvature", [over, over],
                      [Edge(0, 1, 0.6, 0.0, 0.8)], [3.0, 1.0],
                      [0.4, 0.0], dts=[0.1, 0.4])
    cells3 = [band, over, band]
    edges3 = [Edge(0, 1, 0.5, 0.05, 0.9), Edge(1, 2, 0.7, 0.0, 0.8),
              Edge(0, 2, 0.4, 0.05, 1.0), Edge(2, 1, 0.7, 0.0, 0.8)]
    _, _, J = forces_flux(cells3, edges3, [19.0, 3.0, 1.0])
    check("multi-edge fixture has >= 2 simultaneously active edges",
          sum(1 for Je in J if Je > 0) >= 2, f"J={[round(j, 3) for j in J]}")
    _remainder_checks("multiple active edges", cells3, edges3, [19.0, 3.0, 1.0],
                      [0.5, -0.3, 0.2], dts=[0.05, 0.25])


# ===========================================================================
# [5] One-edge bound (Theorem 5.1) + Counterexample A tightness
# ===========================================================================
def test_group5():
    group("one-edge step-size bound (Theorem 5.1) + Counterexample A")
    states = [(19.0, 1.0), (4.0, 1.0), (18.0, 10.0)]
    for (a, b) in [(1.0, 1.0), (2.0, 0.5), (0.5, 2.0)]:
        cell = Cell(a, b, 0.0, 5.0, 15.0, 0.0)
        cells = [cell, cell]
        LV = LV_exact(cells)
        combos = violations = 0
        worst = -math.inf
        bad = ""
        for M in (0.4, 2.0):
            for eta in (0.5, 1.0):
                for theta in (0.0, 0.05):
                    for x0 in states:
                        e = Edge(0, 1, M, theta, eta)
                        bound = 2.0 / (LV * M * (1.0 + eta * eta))
                        for dt in (0.5 * bound, bound):
                            xn, *_ = d0_step(cells, [e], list(x0), [0.0, 0.0], dt)
                            dV = V_total(cells, xn) - V_total(cells, list(x0))
                            note_descent(dV)
                            combos += 1
                            if dV > 1e-9 * (1 + abs(dV)):
                                violations += 1
                                if dV > worst:
                                    worst = dV
                                    bad = fixture_repr(cells, [e], list(x0),
                                                       [0.0, 0.0], dt)
        check(f"weights a={a},b={b}: dt <= 2/(L_V M(1+eta^2)) never increases V",
              violations == 0, f"{combos} deterministic combos", bad)
    # chi > 0 fixture under the same bound (overlapping curvature in L_V)
    over = Cell(1.0, 0.5, 0.7, 5.0, 15.0, 8.0)
    LV = LV_exact([over, over])
    e = Edge(0, 1, 1.0, 0.0, 0.8)
    bound = 2.0 / (LV * e.M * (1.0 + e.eta ** 2))
    xn, *_ = d0_step([over, over], [e], [3.0, 1.0], [0.0, 0.0], bound)
    dV = V_total([over, over], xn) - V_total([over, over], [3.0, 1.0])
    note_descent(dV)
    check("chi>0 overlap fixture: non-increase at the corrected bound", dV <= 1e-9,
          f"L_V={LV}, dV={dV:.2e}")
    # Counterexample A: pure-quadratic zero-width band, exact threshold 1/(2Mw)
    w, M, d = 1.0, 1.0, 1.0
    q = Cell(w, w, 0.0, 0.0, 0.0, 0.0)
    cells = [q, q]
    e = Edge(0, 1, M, 0.0, 1.0)
    x0 = [d, -d]
    dt_star = 1.0 / (2.0 * M * w)
    thm = 2.0 / (LV_exact(cells) * M * (1.0 + 1.0))
    check("CE-A: Theorem 5.1 bound equals the exact threshold 1/(2Mw)",
          abs(thm - dt_star) < 1e-15, f"{thm} vs {dt_star}")
    V0 = V_total(cells, x0)
    xn, *_ = d0_step(cells, [e], x0, [0.0, 0.0], 0.999 * dt_star)
    check("CE-A: dt just below threshold strictly decreases V",
          V_total(cells, xn) < V0 - 1e-9, f"V {V0} -> {V_total(cells, xn):.6f}")
    xn, *_ = d0_step(cells, [e], x0, [0.0, 0.0], dt_star)
    check("CE-A: dt at threshold leaves V unchanged (within tolerance)",
          abs(V_total(cells, xn) - V0) < 1e-9, f"V {V0} -> {V_total(cells, xn):.12f}")
    xn, *_ = d0_step(cells, [e], x0, [0.0, 0.0], 1.001 * dt_star)
    check("NEGATIVE CONTROL (CE-A): dt just above threshold strictly increases V",
          V_total(cells, xn) > V0 + 1e-9, f"V {V0} -> {V_total(cells, xn):.6f}")
    xn, *_ = d0_step(cells, [e], x0, [0.0, 0.0], 0.6)
    check("CE-A: draft's numeric point dt=0.6 gives V: 2 -> 3.92",
          abs(V_total(cells, xn) - 3.92) < 1e-9, f"got {V_total(cells, xn):.6f}")


# ===========================================================================
# Shared deterministic + seeded random graphs for groups 6 and 7
# ===========================================================================
def build_random_graphs(rng, count=6):
    graphs = []
    for gi in range(count):
        n = rng.randint(4, 6)
        cells = [Cell(alpha=rng.uniform(0.3, 2.0), beta=rng.uniform(0.3, 2.0),
                      chi=rng.choice([0.0, round(rng.uniform(0.2, 1.0), 3)]),
                      L=5.0, U=15.0, R=round(rng.uniform(0.0, 9.0), 3))
                 for _ in range(n)]
        pairs = [(i, j) for i in range(n) for j in range(n) if i != j]
        chosen = rng.sample(pairs, rng.randint(4, min(9, len(pairs))))
        edges = [Edge(i, j, round(rng.uniform(0.2, 2.0), 3),
                      round(rng.uniform(0.0, 0.1), 3),
                      round(rng.uniform(0.5, 1.0), 3)) for (i, j) in chosen]
        x = [round(rng.uniform(0.0, 20.0), 3) for _ in range(n)]
        graphs.append((gi, cells, edges, x))
    return graphs


RANDOM_GRAPHS = build_random_graphs(random.Random(SEED))


# ===========================================================================
# [6] Spectral graph bound (Theorem 5.2, Remark 5.4) + eigensolver validation
# ===========================================================================
def test_group6():
    group("spectral graph bound (Theorem 5.2) + independent eigensolver checks")
    # --- eigensolver validation ---
    diag = [[3.0, 0.0, 0.0], [0.0, 7.0, 0.0], [0.0, 0.0, 1.5]]
    vals, vecs = jacobi_eigs(diag)
    check("Jacobi: diagonal matrix returns its diagonal as eigenvalues",
          sorted(round(v, 12) for v in vals) == [1.5, 3.0, 7.0], f"{sorted(vals)}")
    # two edges sharing a source: G analytic 2x2
    M1, M2, eta = 0.7, 1.3, 0.8
    e2 = [Edge(0, 1, M1, 0.0, eta), Edge(0, 2, M2, 0.0, eta)]
    G2 = gram_G(e2, 3)
    aa, dd, bb = M1 * (1 + eta * eta), M2 * (1 + eta * eta), math.sqrt(M1 * M2)
    lam_analytic = (aa + dd) / 2.0 + math.sqrt(((aa - dd) / 2.0) ** 2 + bb * bb)
    vals, vecs = jacobi_eigs(G2)
    check("Jacobi: two-edge shared-source matrix matches analytic lambda_max",
          abs(max(vals) - lam_analytic) < 1e-12,
          f"{max(vals):.12f} vs {lam_analytic:.12f}")
    res = eig_residual(G2, vals, vecs)
    WORST["eig_residual"] = max(WORST["eig_residual"], res)
    check("Jacobi: eigenpair residuals ||Gv - lambda v|| < 1e-10", res < 1e-10,
          f"max residual {res:.2e}")
    rng = random.Random(SEED + 1)
    A = [[0.0] * 5 for _ in range(5)]
    for i in range(5):
        for j in range(i, 5):
            A[i][j] = A[j][i] = rng.uniform(-2.0, 2.0)
    vals, vecs = jacobi_eigs(A)
    res = eig_residual(A, vals, vecs)
    WORST["eig_residual"] = max(WORST["eig_residual"], res)
    check("Jacobi: random symmetric 5x5 residuals + eigenvalue sum == trace",
          res < 1e-10 and abs(sum(vals) - sum(A[i][i] for i in range(5))) < 1e-10,
          f"residual {res:.2e}")
    # 3-cycle, lossless: S^T S eigenvalues {0, 3, 3}
    cyc = [Edge(0, 1, 1.0, 0.0, 1.0), Edge(1, 2, 1.0, 0.0, 1.0),
           Edge(2, 0, 1.0, 0.0, 1.0)]
    lam = spectral_norm_sq(cyc, 3)
    check("lossless 3-cycle: ||S D^{1/2}||^2 == 3 (analytic)",
          abs(lam - 3.0) < 1e-10, f"{lam:.12f}")
    # single edge: recovers Corollary 5.3 exactly
    single = [Edge(0, 1, 0.9, 0.0, 0.7)]
    lam = spectral_norm_sq(single, 2)
    check("single edge: ||S D^{1/2}||^2 == M(1+eta^2) (Corollary 5.3)",
          abs(lam - 0.9 * (1 + 0.49)) < 1e-12, f"{lam:.12f}")
    # --- graph-bound descent on deterministic + seeded random graphs ---
    any_active = False
    for gi, cells, edges, x in RANDOM_GRAPHS:
        n = len(x)
        lam = spectral_norm_sq(edges, n)
        gersh = gershgorin_bound(edges, n)
        check(f"graph{gi}: lambda_max <= Gershgorin bound on D_M S^T S",
              lam <= gersh + 1e-9, f"{lam:.4f} <= {gersh:.4f}",
              fixture_repr(cells, edges, x, [0.0] * n, None))
        LV = LV_exact(cells)
        dt = 0.95 * 2.0 / (LV * lam)
        _, _, J = forces_flux(cells, edges, x)
        if any(Je > 0 for Je in J):
            any_active = True
        xn, *_ = d0_step(cells, edges, x, [0.0] * n, dt)
        dV = V_total(cells, xn) - V_total(cells, x)
        note_descent(dV)
        check(f"graph{gi}: V non-increasing at 0.95 x graph bound (u=0)",
              dV <= 1e-9 * (1 + abs(dV)), f"n={n}, |E|={len(edges)}, dV={dV:.2e}",
              fixture_repr(cells, edges, x, [0.0] * n, dt))
    check("at least one random graph exercises an active edge (non-vacuous)",
          any_active)


# ===========================================================================
# [7] Active-set and state-specific bounds (Theorems 5.5, 5.6, Lemma 5.6a)
# ===========================================================================
def test_group7():
    group("active-set + state-specific bounds (Thms 5.5, 5.6; Lemma 5.6a)")
    any_nonzero = False
    for gi, cells, edges, x in RANDOM_GRAPHS:
        n = len(x)
        LV = LV_exact(cells)
        m, f, J = forces_flux(cells, edges, x)
        active = [e for e, fe in zip(edges, f) if fe > e.theta]
        lam_full = spectral_norm_sq(edges, n)
        if active:
            lam_act = spectral_norm_sq(active, n)
            check(f"graph{gi}: active-set spectral norm <= full-edge norm",
                  lam_act <= lam_full + 1e-9, f"{lam_act:.4f} <= {lam_full:.4f}",
                  fixture_repr(cells, edges, x, [0.0] * n, None))
            dt = 0.95 * 2.0 / (LV * lam_act)
            xn, *_ = d0_step(cells, edges, x, [0.0] * n, dt)
            dV = V_total(cells, xn) - V_total(cells, x)
            note_descent(dV)
            check(f"graph{gi}: V non-increasing at 0.95 x active-set bound",
                  dV <= 1e-9 * (1 + abs(dV)), f"|A|={len(active)}, dV={dV:.2e}",
                  fixture_repr(cells, edges, x, [0.0] * n, dt))
        sj = transport(edges, J, n)
        nsj2 = sum(s * s for s in sj)
        if any(Je > 0 for Je in J):
            any_nonzero = True
            check(f"graph{gi}: Onsager J != 0 implies SJ != 0 (Lemma 5.6a)",
                  nsj2 > 1e-18, f"||SJ||^2={nsj2:.4e}",
                  fixture_repr(cells, edges, x, [0.0] * n, None))
            dt_state = 2.0 * dissipation(edges, J) / (LV * nsj2)
            xn, *_ = d0_step(cells, edges, x, [0.0] * n, 0.95 * dt_state)
            dV = V_total(cells, xn) - V_total(cells, x)
            note_descent(dV)
            check(f"graph{gi}: V non-increasing at 0.95 x state-specific bound",
                  dV <= 1e-9 * (1 + abs(dV)), f"dt_state={dt_state:.4f}, dV={dV:.2e}",
                  fixture_repr(cells, edges, x, [0.0] * n, 0.95 * dt_state))
    check("at least one graph has J != 0 (Lemma 5.6a checks are non-vacuous)",
          any_nonzero)
    # J == 0 fixture: all cells inside their bands, theta > 0 -> transport trivial
    band = Cell(1.0, 0.5, 0.0, 5.0, 15.0, 0.0)
    cells = [band, band, band]
    edges = [Edge(0, 1, 1.0, 0.05, 0.9), Edge(1, 2, 1.0, 0.05, 0.9)]
    x = [10.0, 11.0, 9.0]
    m, f, J = forces_flux(cells, edges, x)
    xn, *_ = d0_step(cells, edges, x, [0.0, 0.0, 0.0], 0.7)
    check("J == 0 fixture: no active edge and transport leaves x exactly unchanged",
          all(Je == 0.0 for Je in J) and xn == x, f"J={J}")


# ===========================================================================
# [8] Counterexample D - loss-blind force negative control
# ===========================================================================
def test_group8():
    group("Counterexample D: loss-blind force increases V under loss (eta=0.5)")
    # realizable marginals: alpha=1, L=10 -> mu = -2(10 - x)
    cell = Cell(1.0, 0.5, 0.0, 10.0, 15.0, 0.0)
    cells = [cell, cell]
    x = [8.5, 8.0]
    eta, M, theta = 0.5, 1.0, 0.0
    e = Edge(0, 1, M, theta, eta)
    m, f, J = forces_flux(cells, [e], x)
    check("realized marginals mu == (-3, -4) from actual penalties",
          abs(m[0] + 3.0) < 1e-12 and abs(m[1] + 4.0) < 1e-12, f"mu={m}")
    g_blind = m[0] - m[1] - theta
    check("loss-blind force mu_i - mu_j == 1 > 0 (would transfer)",
          abs(g_blind - 1.0) < 1e-12)
    check("loss-aware force mu_i - eta mu_j == -1 < 0 (must not transfer)",
          abs(f[0] + 1.0) < 1e-12 and f[0] < 0.0)
    check("D0 Onsager flux correctly stays zero on this edge", J[0] == 0.0)
    # negative control: execute the loss-blind transfer directly and evaluate V
    dt = 0.01
    q = M * g_blind
    x_blind = [x[0] - dt * q, x[1] + eta * dt * q]
    V0, V1 = V_total(cells, x), V_total(cells, x_blind)
    check("NEGATIVE CONTROL (CE-D): loss-blind transfer strictly increases V",
          V1 > V0 + 1e-9, f"V {V0} -> {V1} (dV=+{V1 - V0:.6f})")
    first_order = -f[0] * dt * q          # predicted dV to first order = +dt*q
    check("dV matches the first-order prediction -f_e * (dt q) within 20%",
          abs((V1 - V0) - first_order) < 0.2 * abs(first_order),
          f"dV={V1 - V0:.6f} vs first-order {first_order:.6f}")


# ===========================================================================
# [9] Stock and transport-loss ledger (Theorem 8.1, Corollary 8.2)
# ===========================================================================
def _ledger_check(tag, cells, edges, x, u, dt):
    xn, m, f, J, sj = d0_step(cells, edges, x, u, dt)
    lhs = sum(xn) - sum(x)
    rhs = dt * (sum(u) - transport_loss(edges, J))
    scale = 1.0 + abs(lhs) + abs(rhs)
    note_identity(abs(lhs - rhs))
    check(f"{tag}: 1^T dx == dt(1^T u - sum (1-eta) J) to machine precision",
          abs(lhs - rhs) < 1e-12 * scale, f"lhs={lhs:.12f}, rhs={rhs:.12f}",
          fixture_repr(cells, edges, x, u, dt))
    return J


def test_group9():
    group("stock/loss ledger (Theorem 8.1)")
    band = Cell(1.0, 0.5, 0.0, 5.0, 15.0, 0.0)
    J = _ledger_check("lossless single edge (stock conserved by transport)",
                      [band, band], [Edge(0, 1, 0.8, 0.0, 1.0)], [19.0, 2.0],
                      [0.0, 0.0], 0.3)
    check("lossless fixture: transport loss is exactly zero and J > 0",
          transport_loss([Edge(0, 1, 0.8, 0.0, 1.0)], J) == 0.0 and J[0] > 0)
    J = _ledger_check("lossy single edge", [band, band],
                      [Edge(0, 1, 0.8, 0.05, 0.7)], [19.0, 2.0], [0.0, 0.0], 0.3)
    check("lossy fixture: accounted outflow (1-eta) J > 0",
          transport_loss([Edge(0, 1, 0.8, 0.05, 0.7)], J) > 0.0)
    # multi-edge, mixed active/inactive, with a nonzero natural drive
    cells = [band, band, Cell(1.0, 0.5, 0.7, 5.0, 15.0, 8.0), band]
    edges = [Edge(0, 1, 0.5, 0.05, 0.9), Edge(1, 2, 1.0, 0.0, 1.0),
             Edge(2, 3, 0.8, 0.1, 0.6), Edge(3, 0, 0.4, 0.5, 0.9)]
    x = [19.0, 10.0, 2.0, 7.0]
    s, d, lam, kap = [1.2, 0.0, 0.3, 0.0], [0.0, 0.5, 0.0, 0.2], \
                     [0.1, 0.0, 0.0, 0.1], [0.02, 0.0, 0.01, 0.0]
    u = [s[i] - d[i] - lam[i] - kap[i] * x[i] for i in range(4)]
    J = _ledger_check("multi-edge mixed + nonzero drive", cells, edges, x, u, 0.25)
    check("mixed fixture: both active and inactive edges present",
          any(Je > 0 for Je in J) and any(Je == 0.0 for Je in J),
          f"J={[round(j, 3) for j in J]}")


# ===========================================================================
# [10] Locality (Theorem 9.1) + sequential negative control (Observation 9.2)
# ===========================================================================
def _chain():
    # zero-width band => pure quadratic v = (x-10)^2; every deviation forces flow
    c = Cell(1.0, 1.0, 0.0, 10.0, 10.0, 0.0)
    cells = [c, c, c]
    edges = [Edge(0, 1, 0.2, 0.0, 0.9), Edge(1, 0, 0.2, 0.0, 0.9),
             Edge(1, 2, 0.2, 0.0, 0.9), Edge(2, 1, 0.2, 0.0, 0.9)]
    return cells, edges


def _sequential_tick(cells, order, x, dt):
    """NEGATIVE-CONTROL FIXTURE ONLY: transfers applied one at a time against LIVE
    state (Gauss-Seidel style), the way the DE family sequences transfers. This is
    NOT an implementation of any released engine and is defined only to demonstrate
    the locality violation of Observation 9.2 / Counterexample B."""
    y = list(x)
    for e in order:
        mi, mj = mu_cell(cells[e.i], y[e.i]), mu_cell(cells[e.j], y[e.j])
        Je = e.M * max(0.0, mi - e.eta * mj - e.theta)
        y[e.i] -= dt * Je
        y[e.j] += dt * e.eta * Je
    return y


def test_group10():
    group("one-tick locality (Theorem 9.1) vs sequential control (Obs 9.2)")
    cells, edges = _chain()
    dt = 0.5
    base = [12.0, 10.5, 10.2]
    pert = [12.5, 10.5, 10.2]           # +0.5 at cell 0 only
    u = [0.0, 0.0, 0.0]
    _, _, J = forces_flux(cells, edges, base)
    check("chain fixture: edges 0->1 and 1->2 are both active",
          J[0] > 0 and J[2] > 0, f"J={[round(j, 4) for j in J]}")
    b1, *_ = d0_step(cells, edges, base, u, dt)
    p1, *_ = d0_step(cells, edges, pert, u, dt)
    check("synchronous D0: distance-2 cell bit-identical after one tick",
          p1[2] == b1[2], f"x2 = {b1[2]!r} in both runs")
    b2, *_ = d0_step(cells, edges, b1, u, dt)
    p2, *_ = d0_step(cells, edges, p1, u, dt)
    check("synchronous D0: distance-2 cell changes after two ticks",
          abs(p2[2] - b2[2]) > 1e-9, f"|diff|={abs(p2[2] - b2[2]):.6f}")
    order = [edges[0], edges[2]]        # apply 0->1, then 1->2, against live state
    sb = _sequential_tick(cells, order, base, dt)
    sp = _sequential_tick(cells, order, pert, dt)
    check("NEGATIVE CONTROL: sequential live-state tick leaks to distance 2 in ONE tick",
          abs(sp[2] - sb[2]) > 1e-9, f"leak={abs(sp[2] - sb[2]):.6f}")


# ===========================================================================
# [11] O(dt^2) functional-remainder scaling (Theorem 4.4, Remark 4.5, Sec 7)
# ===========================================================================
def _remainder_of(cells, edges, x, u, dt):
    xn, m, f, J, sj = d0_step(cells, edges, x, u, dt)
    dx = [b - a for a, b in zip(x, xn)]
    r = V_total(cells, xn) - V_total(cells, x) - sum(mi * di for mi, di in zip(m, dx))
    usj = [ui + si for ui, si in zip(u, sj)]
    R = 0.5 * LV_exact(cells) * dt * dt * sum(t * t for t in usj)
    return r, R


def _scaling_checks(tag, cells, edges, x, u, dt0):
    dts = [dt0, dt0 / 2, dt0 / 4, dt0 / 8]
    rs = []
    ok_bound = True
    for dt in dts:
        r, R = _remainder_of(cells, edges, x, u, dt)
        note_remainder(abs(r) - R)
        if abs(r) > R * (1 + 1e-9) + 1e-14:
            ok_bound = False
        rs.append(abs(r))
    check(f"{tag}: |r_n| <= R_n at every dt in the halving sequence", ok_bound,
          f"dts={dts}", fixture_repr(cells, edges, x, u, dt0))
    ratios = [r / (dt * dt) for r, dt in zip(rs, dts)]
    spread = max(ratios) / max(min(ratios), 1e-300)
    check(f"{tag}: |r_n|/dt^2 stays bounded across the sequence",
          all(math.isfinite(t) for t in ratios) and spread < 1.5,
          f"ratios={[f'{t:.6f}' for t in ratios]}")
    consec = [rs[k] / rs[k + 1] for k in range(3) if rs[k + 1] > 1e-12]
    check(f"{tag}: consecutive halvings shrink |r_n| ~4x (second order)",
          all(3.5 < c < 4.5 for c in consec) and consec,
          f"observed factors {[f'{c:.3f}' for c in consec]}")


def test_group11():
    group("O(dt^2) functional-remainder scaling (smooth fixtures)")
    # smooth fixture 1: both cells deep in the deficit branch, away from switches
    band = Cell(1.0, 0.5, 0.0, 10.0, 15.0, 0.0)
    _scaling_checks("deficit-branch pair, driven", [band, band],
                    [Edge(0, 1, 0.1, 0.0, 0.9)], [9.0, 4.0], [0.3, -0.2], 0.1)
    # smooth fixture 2: overlapping deficit+reserve curvature, lossy, undriven
    over = Cell(1.0, 0.5, 0.7, 5.0, 15.0, 8.0)
    _scaling_checks("overlap-branch pair, undriven", [over, over],
                    [Edge(0, 1, 0.1, 0.0, 0.8)], [4.0, 1.0], [0.0, 0.0], 0.1)
    # steps must stay inside the smooth region for the largest dt (sanity guard)
    xn, *_ = d0_step([band, band], [Edge(0, 1, 0.1, 0.0, 0.9)],
                     [9.0, 4.0], [0.3, -0.2], 0.1)
    check("largest step stays strictly inside the smooth region (no switch crossed)",
          all(v < 10.0 for v in xn), f"xn={xn}")


# ===========================================================================
if __name__ == "__main__":
    print("=" * 74)
    print("Foundation V2.8 discrete draft - numerical regression validation")
    print("(finite validation of declared fixtures and negative controls; NOT proof)")
    print("=" * 74)
    print(f"Python {sys.version.split()[0]}   deterministic seed = {SEED}")
    test_group1()
    test_group2()
    test_group3()
    test_group4()
    test_group5()
    test_group6()
    test_group7()
    test_group8()
    test_group9()
    test_group10()
    test_group11()
    print("-" * 74)
    for k, (title, p, f) in enumerate(GROUPS, 1):
        print(f"group {k:>2}: {p:>3} passed, {f} failed - {title}")
    print(f"total checks: {PASS} passed, {FAIL} failed in {len(GROUPS)} groups")
    print(f"max |r_n| - R_n margin observed: {WORST['remainder_margin']:.3e} "
          f"(<= 0 expected; tiny positive values within the declared fp tolerance are acceptable)")
    print(f"max descent margin observed:     {WORST['descent_margin']:.3e} "
          f"(<= 0 expected; tiny positive values within the declared fp tolerance are acceptable)")
    print(f"max exact-identity residual:     {WORST['identity_residual']:.3e}")
    print(f"max eigenpair residual:          {WORST['eig_residual']:.3e}")
    if FAIL:
        print("NUMERICAL VALIDATION FAILED - see reproduce lines above.")
        raise SystemExit(1)
    print("Numerical validation passed; this is not a proof.")
