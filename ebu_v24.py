"""
Energy Balance - Foundation Model V2.4
Distinguishing genuine ecological foresight from an artifact of the accept/reject
architecture, plus three protective harvest rules.

Six rules (all share the same physics + ledger):
  safe             - H=1 line-searched q, immediate acceptance         (V2.2)
  horizon_gate     - H=1 line-searched q, gated by H-tick counterfactual (V2.3 Model D)
  horizon_opt      - q chosen to MAXIMISE the H-tick impact:  q_H* = argmax_q I^H(q)
  threshold_penalty- burden augmented with a regenerative-reserve penalty (below)
  hard_reserve     - harvest capped at max(0, x - R); forbidden while x < A
  penalty_horizon  - regenerative-reserve burden AND horizon-optimised quantity

Threshold-aware burden (regenerative reserve R_i = A_i + delta_i):
  B_regen = B + sum_i chi_i [R_i - x_i]_+^2
  mu_i^regen adds  -2 chi_i (R_i - x_i)   for x_i < R_i
This preserves the convex piecewise-quadratic structure the line search relies on.

The horizon_opt rule is the key control: if maximising I^H over q STILL over-harvests,
the single-action counterfactual is fundamentally biased (not merely the gate).
"""
from __future__ import annotations
from energy_balance import Grid, Actor, clip, local_penalty, burden, mu
from ebu_v22 import Ledger, Report, _proposals
from ebu_v23 import nat_cell, natural_update_ledger, _radius_cells

RULES = ["safe", "horizon_gate", "horizon_opt", "threshold_penalty",
         "hard_reserve", "penalty_horizon"]


def reserve_R(g: Grid, delta: float) -> list[float]:
    """R_i = A_i + delta for regenerative sources; 0 (inactive) elsewhere."""
    R = [0.0] * g.size
    if g.A is not None:
        for i in range(g.size):
            if g.rho[i] > 0 and g.A[i] > 0:
                R[i] = g.A[i] + delta
    return R


def pen(g: Grid, i: int, x: float, R: list[float], chi: float, ra: bool) -> float:
    v = local_penalty(g, i, x)
    if ra and R[i] > 0 and x < R[i]:
        v += chi * (R[i] - x) ** 2
    return v


def marg(g: Grid, i: int, x: float, R: list[float], chi: float, ra: bool) -> float:
    v = mu(g, i, x)
    if ra and R[i] > 0 and x < R[i]:
        v += -2.0 * chi * (R[i] - x)
    return v


def _golden_min(f, q_hi, iters=24):
    if q_hi <= 1e-12:
        return 0.0
    gr = 0.6180339887498949
    lo, hi = 0.0, q_hi
    for _ in range(iters):
        m1 = hi - gr * (hi - lo)
        m2 = lo + gr * (hi - lo)
        if f(m1) < f(m2):
            hi = m2
        else:
            lo = m1
    return 0.5 * (lo + hi)


def _horizon_impact(g, i, j, q, eta, c0, cells, H, gamma, R, chi, ra):
    x0 = {c: g.x[c] for c in cells}
    xa = dict(x0)
    xa[i] = xa[i] - c0 - q
    xa[j] = xa[j] + eta * q
    total, disc = 0.0, 1.0
    for _h in range(H):
        x0 = {c: nat_cell(g, c, x0[c])[0] for c in cells}
        xa = {c: nat_cell(g, c, xa[c])[0] for c in cells}
        b0 = sum(pen(g, c, x0[c], R, chi, ra) for c in cells)
        ba = sum(pen(g, c, xa[c], R, chi, ra) for c in cells)
        total += disc * (b0 - ba)
        disc *= gamma
    return total


def _horizon_opt_q(g, i, j, eta, c0, q_hi, cells, H, gamma, R, chi, ra, samples=8):
    """q_H* = argmax_{0<=q<=q_hi} I^H(q). Coarse grid then one local refinement."""
    if q_hi <= 1e-12:
        return 0.0, 0.0
    best_q, best_I = 0.0, 0.0
    for k in range(1, samples + 1):
        q = q_hi * k / samples
        I = _horizon_impact(g, i, j, q, eta, c0, cells, H, gamma, R, chi, ra)
        if I > best_I:
            best_I, best_q = I, q
    # local refinement around the best grid point
    step = q_hi / samples
    for dq in (-step / 2, step / 2):
        q = min(q_hi, max(0.0, best_q + dq))
        I = _horizon_impact(g, i, j, q, eta, c0, cells, H, gamma, R, chi, ra)
        if I > best_I:
            best_I, best_q = I, q
    return best_q, best_I


_CFG = {
    "safe":              dict(ra=False, size="line", gate="imm",     hard=False),
    "horizon_gate":      dict(ra=False, size="line", gate="horizon", hard=False),
    "horizon_opt":       dict(ra=False, size="hopt", gate="hopt",    hard=False),
    "threshold_penalty": dict(ra=True,  size="line", gate="imm",     hard=False),
    "hard_reserve":      dict(ra=False, size="line", gate="imm",     hard=True),
    "penalty_horizon":   dict(ra=True,  size="hopt", gate="hopt",    hard=False),
}


def step_v24(g: Grid, actors, tick, rule="safe", H=10, gamma=0.95, radius=2,
             delta=3.0, chi=1.0, eps=1e-9) -> Report:
    cfg = _CFG[rule]
    ra = cfg["ra"]
    R = reserve_R(g, delta)

    X_before = sum(g.x)
    B_before = burden(g, g.x)
    x0, led = natural_update_ledger(g)
    B_no = burden(g, x0)
    xa = list(x0)
    proposed = executed = rejected = 0

    if actors:
        m = [marg(g, i, xa[i], R, chi, ra) for i in range(g.size)]
        props = _proposals(g, actors, m)
        proposed = len(props)
        for (ai, i, j, F) in sorted(props, key=lambda p: -p[3]):
            a = actors[ai]
            q_hi = min(a.q_max, xa[i] - g.x_min[i] - a.c0, (g.K[j] - xa[j]) / a.eta)
            if cfg["hard"] and R[i] > 0:
                if g.A is not None and xa[i] < g.A[i]:
                    q_hi = 0.0
                else:
                    q_hi = min(q_hi, max(0.0, xa[i] - R[i]))
            if q_hi <= 0:
                rejected += 1
                continue

            if cfg["size"] == "line":
                q = _golden_min(
                    lambda qq: pen(g, i, xa[i] - a.c0 - qq, R, chi, ra)
                    + pen(g, j, xa[j] + a.eta * qq, R, chi, ra), q_hi)
                if cfg["gate"] == "imm":
                    f0 = pen(g, i, xa[i], R, chi, ra) + pen(g, j, xa[j], R, chi, ra)
                    fn = pen(g, i, xa[i] - a.c0 - q, R, chi, ra) + pen(g, j, xa[j] + a.eta * q, R, chi, ra)
                    ok = q > 0 and fn < f0 - eps
                else:  # horizon gate on line-searched q
                    saved = g.x; g.x = xa
                    cells = _radius_cells(g, i, radius)
                    if j not in cells:
                        cells.append(j)
                    ok = q > 0 and _horizon_impact(g, i, j, q, a.eta, a.c0, cells, H, gamma, R, chi, ra) > eps
                    g.x = saved
            else:  # size == hopt : horizon-optimised quantity
                saved = g.x; g.x = xa
                cells = _radius_cells(g, i, radius)
                if j not in cells:
                    cells.append(j)
                q, bestI = _horizon_opt_q(g, i, j, a.eta, a.c0, q_hi, cells, H, gamma, R, chi, ra)
                g.x = saved
                ok = q > 0 and bestI > eps

            if ok:
                xa[i] -= (a.c0 + q); xa[j] += a.eta * q
                led.transport_loss += (1.0 - a.eta) * q + a.c0
                executed += 1
            else:
                rejected += 1

    B_with = burden(g, xa)
    g.x = xa
    return Report(
        tick=tick, B_before=B_before, B_noaction=B_no, B_withaction=B_with, X=sum(xa),
        n_below_L=sum(1 for i in range(g.size) if xa[i] < g.L[i]),
        n_above_U=sum(1 for i in range(g.size) if xa[i] > g.U[i]),
        proposed=proposed, executed=executed, rejected=rejected,
        ledger=led, impact=B_no - B_with)
