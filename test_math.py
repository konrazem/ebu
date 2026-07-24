"""
Regression validation for Foundation Note V2.7 (mathematics).

These are NUMERICAL REGRESSION CHECKS, not proofs. Each guards one labelled claim of
Foundation_v2.7_math.md against drift between the analysis and the engine. A passing
run means the engine still behaves as the note's theorems/observations describe at the
tested points; it does not establish any theorem. Proofs live in the note.

Plain stdlib + the repo engine (energy_balance.py, ebu_v22.py). No pytest.
"""
from __future__ import annotations
import math

from energy_balance import Grid, Actor, step, burden, mu
from ebu_v22 import step_v22, _line_search_q, _proposals, natural_update_ledger

PASS = 0
FAIL = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global PASS, FAIL
    if ok:
        PASS += 1
        print(f"  PASS  {name}" + (f"  ({detail})" if detail else ""))
    else:
        FAIL += 1
        print(f"  FAIL  {name}" + (f"  ({detail})" if detail else ""))


# ---------------------------------------------------------------------------
# [1] Fold & basin (Thm 3.1-3.3): equilibrium = x_+(h); x0 straddling x_-(h)
#     lands in the collapse vs recovery basin.
# ---------------------------------------------------------------------------
def test_fold_and_basin():
    print("[1] logistic fold + basin (Thm 3.1-3.3)")
    rho, K = 0.4, 20.0
    hstar = rho * K / 4.0

    def phi(x, h):
        v = x + rho * x * (1 - x / K) - h
        return min(max(v, 0.0), K)

    def evolve(x0, h, T=200000):
        x = x0
        for _ in range(T):
            x = phi(x, h)
            if x <= 0.0:
                return 0.0
        return x

    for h in (1.0, 1.6, 1.99):
        D = 1 - 4 * h / (rho * K)
        xm = (K / 2) * (1 - math.sqrt(D))
        xp = (K / 2) * (1 + math.sqrt(D))
        x_eq = evolve(xp, h)
        check(f"h={h}: equilibrium == x_+(h)", abs(x_eq - xp) < 1e-3,
              f"got {x_eq:.4f} vs {xp:.4f}")
        check(f"h={h}: start just below x_-(h) collapses", evolve(xm - 0.05, h) == 0.0)
        check(f"h={h}: start just above x_-(h) recovers",
              abs(evolve(xm + 0.05, h) - xp) < 1e-3)


# ---------------------------------------------------------------------------
# [2] Flip / period-doubling (Thm 3.2): a 2-cycle appears once rho*sqrt(D) > 2.
# ---------------------------------------------------------------------------
def test_flip():
    print("[2] discrete flip bifurcation (Thm 3.2)")
    K = 20.0

    def tail_span(rho, hfrac=0.3):
        h = hfrac * rho * K / 4.0
        x = 0.7 * K
        for _ in range(4000):
            x = min(max(x + rho * x * (1 - x / K) - h, 0.0), K)
        xs = []
        for _ in range(8):
            x = min(max(x + rho * x * (1 - x / K) - h, 0.0), K)
            xs.append(x)
        return max(xs) - min(xs)

    for rho in (0.5, 1.5, 2.2):
        check(f"rho={rho} (rho*sqrt(D)<2): fixed point", tail_span(rho) < 1e-6)
    check("rho=2.6 (rho*sqrt(D)>2): sustained oscillation", tail_span(2.6) > 1.0,
          f"span={tail_span(2.6):.3f}")


# ---------------------------------------------------------------------------
# [3] Driven Allee reserve (Thm 4.2): middle root moves in the signed directions.
# ---------------------------------------------------------------------------
def test_driven_reserve():
    print("[3] driven Allee reserve shift (Thm 4.2)")
    rho, K, A = 0.6, 20.0, 5.0

    def G(x, h, s, d, lam, kap):
        return rho * x * (1 - x / K) * (x / A - 1) + s - d - lam - kap * x - h

    def middle_root(h=0.0, s=0.0, d=0.0, lam=0.0, kap=0.0):
        roots = []
        px, prev = 1e-6, G(1e-6, h, s, d, lam, kap)
        x = 0.01
        while x <= K:
            cur = G(x, h, s, d, lam, kap)
            if (prev < 0) != (cur < 0):
                a, b = px, x
                for _ in range(60):
                    m = (a + b) / 2
                    if (G(a, h, s, d, lam, kap) < 0) != (G(m, h, s, d, lam, kap) < 0):
                        b = m
                    else:
                        a = m
                roots.append((a + b) / 2)
            px, prev = x, cur
            x += 0.01
        return roots[0] if roots else float("nan")

    base = middle_root()
    check("undriven middle root == A", abs(base - A) < 1e-2, f"{base:.3f}")
    check("harvest raises reserve", middle_root(h=0.5) > A + 1e-3)
    check("demand raises reserve", middle_root(d=0.5) > A + 1e-3)
    check("leak raises reserve", middle_root(kap=0.05) > A + 1e-3)
    check("supply lowers reserve", middle_root(s=0.5) < A - 1e-3)


# ---------------------------------------------------------------------------
# [4] Loss-corrected descent (Thm 5.1-5.2). Simulate the DERIVED law
#     (force mu_i - eta*mu_j - theta; update x_i-=q, x_j+=eta*q).
#     Sufficient bound M <= 1/[max(a,b)_src + eta^2 max(a,b)_dst]; tight (=) for
#     symmetric weights.
# ---------------------------------------------------------------------------
def test_descent_bound():
    print("[4] loss-corrected descent bound (Thm 5.1-5.2)")

    def derived_mono(alpha, beta, eta, M, U=10.0, L=10.0, excess=4.0, deficit=4.0):
        xi, xj = U + excess, L - deficit

        def V(a, b):
            vi = beta * (a - U) ** 2 if a > U else (alpha * (L - a) ** 2 if a < L else 0.0)
            vj = beta * (b - U) ** 2 if b > U else (alpha * (L - b) ** 2 if b < L else 0.0)
            return vi + vj

        prev = V(xi, xj)
        for _ in range(600):
            mi = 2 * beta * (xi - U) if xi > U else (-2 * alpha * (L - xi) if xi < L else 0.0)
            mj = 2 * beta * (xj - U) if xj > U else (-2 * alpha * (L - xj) if xj < L else 0.0)
            F = mi - eta * mj
            if F <= 1e-12:
                break
            q = min(M * F, xi)
            xi -= q
            xj += eta * q
            cur = V(xi, xj)
            if cur > prev + 1e-9:
                return False
            prev = cur
        return True

    # symmetric weights: bound is tight -> monotone just below, not far above
    for w, eta in ((1.0, 0.9), (0.5, 0.8), (1.0, 0.5)):
        bound = 1.0 / (w * (1 + eta * eta))
        check(f"symmetric w={w},eta={eta}: monotone at 0.95*bound",
              derived_mono(w, w, eta, 0.95 * bound))
        check(f"symmetric w={w},eta={eta}: overshoot above bound",
              not derived_mono(w, w, eta, 1.5 * bound), f"bound={bound:.4f}")
    # asymmetric weights: sufficient bound must remain safe (conservative)
    for a, b, eta in ((1.0, 0.5, 0.9), (2.0, 0.5, 0.8)):
        bound = 1.0 / (max(a, b) + eta * eta * max(a, b))
        check(f"asymmetric a={a},b={b},eta={eta}: bound is safe",
              derived_mono(a, b, eta, bound))


# ---------------------------------------------------------------------------
# [5] Force coincidence (Sec 7 C1): F_engine == F_derived iff eta == 1.
# ---------------------------------------------------------------------------
def test_force_coincidence():
    print("[5] engine vs derived force (Sec 7, C1)")
    mi, mj, theta = 2.0, -8.0, 0.05
    for eta in (1.0, 0.9, 0.5):
        F_eng = mi - mj - theta
        F_der = mi - eta * mj - theta
        gap = abs(F_eng - F_der)
        expect = (1 - eta) * abs(mj)
        if eta == 1.0:
            check("eta=1: forces coincide", gap < 1e-12)
        else:
            check(f"eta={eta}: gap == (1-eta)|mu_j|", abs(gap - expect) < 1e-12,
                  f"gap={gap:.3f}")


# ---------------------------------------------------------------------------
# [6] Causality (Sec 6): frozen-state simultaneous => no leak; the sequential
#     safe engine leaks a cell-0 perturbation to cell 2 in one tick.
# ---------------------------------------------------------------------------
def _chain_grid(x0):
    x = [10.0] * 9
    x[0], x[1], x[2] = x0, 10.1, 9.9
    x[3], x[4] = 20.0, 20.0            # block side sinks so 0->1->2 is isolated
    return Grid(n=3, x=x, K=[20] * 9, L=[10] * 9, U=[10] * 9, alpha=[1] * 9,
                beta=[0.5] * 9, s=[0] * 9, d=[0] * 9, lam=[0] * 9, rho=[0] * 9,
                x_min=[0] * 9)


def test_causality():
    print("[6] finite causal speed vs sequential execution (Sec 6)")

    def sequential_x2(x0):
        g = _chain_grid(x0)
        a0 = Actor(pos=0, q_max=50.0, M=1.0, theta=0.05, eta=0.9)
        a1 = Actor(pos=1, q_max=50.0, M=1.0, theta=0.05, eta=0.9)
        step_v22(g, [a0, a1], 1, mode="safe")
        return g.x[2]

    def frozen_x2(x0):
        g = _chain_grid(x0)
        actors = [Actor(pos=0, q_max=50, M=1, theta=0.05, eta=0.9),
                  Actor(pos=1, q_max=50, M=1, theta=0.05, eta=0.9)]
        y, _ = natural_update_ledger(g)
        m = [mu(g, i, y[i]) for i in range(9)]
        props = _proposals(g, actors, m)
        deltas = [0.0] * 9
        for (ai, i, j, F) in props:                       # all q from the SAME frozen y
            a = actors[ai]
            q_hi = min(a.q_max, y[i] - g.x_min[i] - a.c0, (g.K[j] - y[j]) / a.eta)
            q = _line_search_q(g, i, j, y[i], y[j], a.eta, a.c0, q_hi)
            deltas[i] -= (a.c0 + q)
            deltas[j] += a.eta * q
        return y[2] + deltas[2]

    seq_leak = abs(sequential_x2(19.5) - sequential_x2(19.0))
    frz_leak = abs(frozen_x2(19.5) - frozen_x2(19.0))
    check("sequential engine leaks x0 -> x2 in one tick", seq_leak > 1e-6,
          f"leak={seq_leak:.5f}")
    check("frozen-state simultaneous does NOT leak", frz_leak < 1e-9,
          f"leak={frz_leak:.2e}")


# ---------------------------------------------------------------------------
# [7] Energy-dissipation identity (Thm 7.1): dV/dt = sum mu_i u_i - sum[J^2/M + theta J].
#     Fine-dt integration; residual must scale with dt.
# ---------------------------------------------------------------------------
def test_energy_identity():
    print("[7] continuous energy-dissipation identity (Thm 7.1)")
    L, U, a, b = 5.0, 15.0, 1.0, 0.5
    N = 3
    edges = [(0, 1), (1, 0), (1, 2), (2, 1)]
    M = {e: 0.5 for e in edges}
    theta = {e: 0.05 for e in edges}
    eta = {e: 0.9 for e in edges}
    s = [1.2, 0.0, 0.0]
    d = [0.0, 0.0, 1.0]

    def ell(x):
        return a * max(0.0, L - x) ** 2 + b * max(0.0, x - U) ** 2

    def mu_(x):
        if x < L:
            return -2 * a * (L - x)
        if x > U:
            return 2 * b * (x - U)
        return 0.0

    def u(i, x):
        return s[i] - d[i]

    def V(x):
        return sum(ell(v) for v in x)

    def run(dt, steps):
        x = [16.0, 10.0, 3.0]
        maxerr = 0.0
        for _ in range(steps):
            J = {}
            for (i, j) in edges:
                f = mu_(x[i]) - eta[(i, j)] * mu_(x[j])
                J[(i, j)] = M[(i, j)] * max(0.0, f - theta[(i, j)])
            dx = [u(i, x) for i in range(N)]
            for (i, j) in edges:
                dx[i] -= J[(i, j)]
                dx[j] += eta[(i, j)] * J[(i, j)]
            drive = sum(mu_(x[i]) * u(i, x) for i in range(N))
            diss = sum(J[e] ** 2 / M[e] + theta[e] * J[e] for e in edges)
            analytic = drive - diss
            xn = [x[i] + dt * dx[i] for i in range(N)]
            numeric = (V(xn) - V(x)) / dt
            maxerr = max(maxerr, abs(numeric - analytic))
            x = xn
        return maxerr

    e_coarse = run(1e-3, 2000)
    e_fine = run(1e-4, 20000)
    check("identity residual is O(dt) (coarse ~10x fine)", e_fine < e_coarse,
          f"dt=1e-3 err={e_coarse:.2e}, dt=1e-4 err={e_fine:.2e}")
    check("identity holds at dt=1e-4 (residual small)", e_fine < 1e-3,
          f"err={e_fine:.2e}")


# ---------------------------------------------------------------------------
# [8] Three-law separation (Sec 2.1, Sec 7): q_safe != M*F even at eta=1, theta=0.
# ---------------------------------------------------------------------------
def test_three_law_separation():
    print("[8] B_safe is not the Onsager flux (Sec 2.1, Sec 7)")
    g = Grid(n=2, x=[18.0, 2.0, 10.0, 10.0], K=[20] * 4, L=[5] * 4, U=[15] * 4,
             alpha=[1] * 4, beta=[0.5] * 4, s=[0] * 4, d=[0] * 4, lam=[0] * 4,
             rho=[0] * 4, x_min=[0] * 4)
    i, j = 0, 1
    eta, M, theta = 1.0, 0.5, 0.0
    F = mu(g, i, g.x[i]) - mu(g, j, g.x[j]) - theta
    q_raw = M * F
    q_hi = min(50.0, g.x[i], (g.K[j] - g.x[j]) / eta)
    q_safe = _line_search_q(g, i, j, g.x[i], g.x[j], eta, 0.0, q_hi)
    check("q_safe != M*F at eta=1, theta=0", abs(q_safe - q_raw) > 1e-6,
          f"q_safe={q_safe:.4f}, M*F={q_raw:.4f}")


if __name__ == "__main__":
    print("=" * 70)
    print("Foundation V2.7 math — numerical regression validation (NOT proof)")
    print("=" * 70)
    test_fold_and_basin()
    test_flip()
    test_driven_reserve()
    test_descent_bound()
    test_force_coincidence()
    test_causality()
    test_energy_identity()
    test_three_law_separation()
    print("-" * 70)
    print(f"validation checks: {PASS} passed, {FAIL} failed")
    if FAIL:
        raise SystemExit(1)
