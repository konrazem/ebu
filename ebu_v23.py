"""
Energy Balance - Foundation Model V2.3
Regeneration + regeneration-aware (H-horizon) movement, built on the V2.2 engine.

Adds:
  * Four source behaviours via existing parameters (Sec. 3):
        external flow : s_i > 0, rho_i = 0
        logistic stock: rho_i > 0, A_i = 0
        Allee stock   : rho_i > 0, A_i > 0   (declines below the critical threshold A_i)
        finite stock  : s_i = 0, rho_i = 0
  * A ledger natural update robust to SIGNED regeneration (Allee can be negative).
  * The regeneration-aware actor (Model D, V2.0 Sec. 9): a candidate transfer is
    accepted only if a short H-tick LOCAL counterfactual predicts net benefit:
        I_a^H = sum_{h=1..H} gamma^{h-1} [ B_Na(x0_{t+h}) - B_Na(xA_{t+h}) ] > eps
    over the cells N_a within an evaluation radius. This lets an actor decline an
    action that helps now but damages a regenerative source later.

Modes: "none", "gradient", "safe" (H=1 instantaneous), "horizon" (Model D, H-tick).
Actors remain stationary local processes.
"""
from __future__ import annotations
from dataclasses import dataclass

from energy_balance import Grid, Actor, clip, local_penalty, burden, mu, regen_at
from ebu_v22 import Ledger, _line_search_q, _proposals, Report


# ----------------------------------------------------------------------------
def leak_at(g: Grid, i: int, x: float) -> float:
    base = g.lam[i]
    if g.leak_frac is not None:
        base += g.leak_frac[i] * x
    return base


def nat_cell(g: Grid, i: int, x: float) -> tuple[float, Ledger]:
    """One tick of natural (no-transfer) dynamics for a single cell, with accounting.
       Robust to signed regeneration (Allee below threshold)."""
    led = Ledger()
    s = g.s[i]
    gg = regen_at(g, i, x)
    v = x + s
    led.S += s
    applied = gg
    if v + applied < 0.0:                 # regeneration decline cannot drive x below 0
        applied = -v
    v += applied
    led.G += applied
    leak = leak_at(g, i, x)
    actual_leak = min(leak, v) if v > 0 else 0.0
    v -= actual_leak
    led.Lam += actual_leak
    actual_demand = min(g.d[i], v) if v > 0 else 0.0
    v -= actual_demand
    led.D += actual_demand
    led.unmet_demand += g.d[i] - actual_demand
    if v > g.K[i]:
        led.spill += v - g.K[i]
        v = g.K[i]
    return v, led


def natural_update_ledger(g: Grid) -> tuple[list[float], Ledger]:
    x0 = [0.0] * g.size
    led = Ledger()
    for i in range(g.size):
        x0[i], cell = nat_cell(g, i, g.x[i])
        led.add(cell)
    return x0, led


# ----------------------------------------------------------------------------
def _radius_cells(g: Grid, center: int, radius: int) -> list[int]:
    """Cells within Manhattan graph distance <= radius (BFS on the lattice)."""
    seen = {center}
    frontier = [center]
    for _ in range(radius):
        nxt = []
        for c in frontier:
            for nb in g.neighbors(c):
                if nb not in seen:
                    seen.add(nb)
                    nxt.append(nb)
        frontier = nxt
    return list(seen)


def _horizon_impact(g: Grid, i: int, j: int, q: float, eta: float, c0: float,
                    cells: list[int], H: int, gamma: float) -> float:
    """Discounted H-tick local counterfactual impact of transferring q from i to j.
       Simulates natural-only dynamics on `cells` for both branches (no other transfers)."""
    x0 = {c: g.x[c] for c in cells}
    xa = dict(x0)
    xa[i] = xa[i] - c0 - q
    xa[j] = xa[j] + eta * q
    total = 0.0
    disc = 1.0
    for _h in range(H):
        x0 = {c: nat_cell(g, c, x0[c])[0] for c in cells}
        xa = {c: nat_cell(g, c, xa[c])[0] for c in cells}
        B0 = sum(local_penalty(g, c, x0[c]) for c in cells)
        BA = sum(local_penalty(g, c, xa[c]) for c in cells)
        total += disc * (B0 - BA)
        disc *= gamma
    return total


# ----------------------------------------------------------------------------
def step_v23(g: Grid, actors: list[Actor], tick: int, mode: str = "horizon",
             H: int = 3, gamma: float = 0.95, radius: int = 2,
             eps: float = 1e-9, check_ledger: bool = False) -> Report:
    X_before = sum(g.x)
    B_before = burden(g, g.x)
    x0, led = natural_update_ledger(g)
    B_no = burden(g, x0)
    xa = list(x0)
    proposed = executed = rejected = 0

    if mode != "none" and actors:
        m = [mu(g, i, xa[i]) for i in range(g.size)]
        props = _proposals(g, actors, m)
        proposed = len(props)

        if mode == "gradient":
            need: dict[int, float] = {}
            raw = []
            for (ai, i, j, F) in props:
                a = actors[ai]
                raw.append((ai, i, j, a.M * F))
                need[i] = need.get(i, 0.0) + a.M * F + a.c0
            scale = {i: (1.0 if (w <= max(0.0, xa[i] - g.x_min[i]) or w <= 0)
                         else max(0.0, xa[i] - g.x_min[i]) / w) for i, w in need.items()}
            for (ai, i, j, q) in raw:
                a = actors[ai]
                q *= scale[i]
                c0 = a.c0 * scale[i]
                q = min(q, a.q_max, max(0.0, (g.K[j] - xa[j]) / a.eta))
                if q <= 0:
                    continue
                if q + c0 > xa[i] - g.x_min[i] + 1e-12:
                    q = max(0.0, xa[i] - g.x_min[i] - c0)
                if q <= 0:
                    continue
                xa[i] -= (q + c0); xa[j] += a.eta * q
                led.transport_loss += (1.0 - a.eta) * q + c0
                executed += 1
            for k in range(g.size):
                xa[k] = clip(xa[k], 0.0, g.K[k])

        else:  # "safe" (H=1 instantaneous)  or  "horizon" (Model D)
            for (ai, i, j, F) in sorted(props, key=lambda p: -p[3]):
                a = actors[ai]
                q_hi = min(a.q_max, xa[i] - g.x_min[i] - a.c0, (g.K[j] - xa[j]) / a.eta)
                if q_hi <= 0:
                    rejected += 1
                    continue
                q = _line_search_q(g, i, j, xa[i], xa[j], a.eta, a.c0, q_hi)
                if q <= 0:
                    rejected += 1
                    continue
                if mode == "safe":
                    f0 = local_penalty(g, i, xa[i]) + local_penalty(g, j, xa[j])
                    fn = local_penalty(g, i, xa[i] - a.c0 - q) + local_penalty(g, j, xa[j] + a.eta * q)
                    ok = fn < f0 - eps
                else:  # horizon: H-tick local counterfactual on live state
                    # temporarily set g.x to xa for regen/leak evaluation inside the sim
                    saved = g.x
                    g.x = xa
                    cells = _radius_cells(g, i, radius)
                    if j not in cells:
                        cells.append(j)
                    impact = _horizon_impact(g, i, j, q, a.eta, a.c0, cells, H, gamma)
                    g.x = saved
                    ok = impact > eps
                if ok:
                    xa[i] -= (a.c0 + q); xa[j] += a.eta * q
                    led.transport_loss += (1.0 - a.eta) * q + a.c0
                    executed += 1
                else:
                    rejected += 1

    B_with = burden(g, xa)
    g.x = xa
    if check_ledger:
        if abs((sum(xa) - X_before) - led.dX()) > 1e-6:
            raise AssertionError(f"ledger imbalance tick {tick}")
    return Report(
        tick=tick, B_before=B_before, B_noaction=B_no, B_withaction=B_with, X=sum(xa),
        n_below_L=sum(1 for i in range(g.size) if xa[i] < g.L[i]),
        n_above_U=sum(1 for i in range(g.size) if xa[i] > g.U[i]),
        proposed=proposed, executed=executed, rejected=rejected,
        ledger=led, impact=B_no - B_with,
    )
