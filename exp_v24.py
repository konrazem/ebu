"""
V2.4 regeneration comparison: six harvest rules on the closed Allee economy.

Key control: horizon_opt chooses q to MAXIMISE the H-tick impact. If it over-harvests
like the V2.3 gate, the counterfactual is fundamentally biased; if it is sustainable,
the V2.3 failure was an artifact of gating an immediately-optimised quantity.

Success requires BOTH preserving sources AND serving demand (a rule that never
harvests would preserve everything while starving consumers, and is not a success).

Run with the project venv:  .../venv/bin/python exp_v24.py
"""
from __future__ import annotations
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from energy_balance import regen_at, burden
from ebu_v24 import step_v24, RULES
import exp_v23

FIGDIR = "figures"; os.makedirs(FIGDIR, exist_ok=True)
TICKS, SHOCK, GAMMA = 1000, 500, 0.999
A = exp_v23.A_THRESH
DEMAND = 0.45


def run_rule(rule, H=10):
    g, actors, is_src = exp_v23.make_regen_world()
    src = [i for i in range(g.size) if is_src[i]]
    n_con = g.size - len(src)
    prev = {i: g.x[i] for i in src}
    crossings = 0
    cum_unmet = cum_loss = disc_B = cum_B = 0.0
    disc = 1.0
    series = dict(stock=[], viable=[])
    pre_v = None
    R_reserve = A + 3.0                                # matches ebu_v24 default delta=3
    for t in range(1, TICKS + 1):
        if t == SHOCK:
            for i in src:
                g.x[i] *= 0.45
            prev = {i: g.x[i] for i in src}
        r = step_v24(g, actors, t, rule=rule, H=H)
        for i in src:                                  # downward Allee crossings
            if prev[i] >= A and g.x[i] < A:
                crossings += 1
            prev[i] = g.x[i]
        cum_unmet += r.ledger.unmet_demand
        cum_loss += r.ledger.transport_loss
        cum_B += r.B_withaction
        disc_B += disc * r.B_withaction; disc *= GAMMA
        viable = 100.0 * (g.size - r.n_below_L) / g.size
        series["viable"].append(viable)
        series["stock"].append(sum(g.x[i] for i in src))
        if t == SHOCK - 1:
            pre_v = viable
    dead = sum(1 for i in src if g.x[i] < A and regen_at(g, i, g.x[i]) <= 0)
    served = 100.0 * (1 - cum_unmet / (n_con * DEMAND * TICKS))
    # Sustained recovery: first post-shock tick from which viability stays >= 90% of the
    # pre-shock value AND total source stock stays above the regenerative reserve for a
    # full WINDOW of consecutive ticks. A transient bounce that later collapses does NOT
    # count as recovery (fixes the misleading "1 tick" for horizon_gate).
    WINDOW = 100
    v, stk = series["viable"], series["stock"]
    stock_floor = len(src) * R_reserve
    recovery = None
    for t in range(SHOCK, TICKS - WINDOW + 1):
        if pre_v and all(v[k] >= 0.9 * pre_v and stk[k] >= stock_floor
                         for k in range(t, t + WINDOW)):
            recovery = t - SHOCK + 1
            break
    return series, dict(
        viable_final=v[-1],
        viable_half=sum(v[TICKS // 2:]) / (TICKS - TICKS // 2),
        dead=dead, n_src=len(src), crossings=crossings,
        served=served, unmet=cum_unmet, stock=stk[-1],
        loss=cum_loss, cum_B=cum_B, disc_B=disc_B, recovery=recovery)


def main():
    res = {r: run_rule(r) for r in RULES}
    for r in RULES:
        print("ran", r)

    print("\n=== V2.4: six harvest rules on the closed Allee economy ===")
    print("(success = preserve sources AND serve demand)\n")
    hdr = (f"{'rule':18s} {'viable%end':>10s} {'viable%2ndH':>11s} {'served%':>8s} "
           f"{'dead':>6s} {'cross':>6s} {'stock':>7s} {'unmet':>7s} {'cumB':>9s} "
           f"{'sust.rec':>9s}")
    print(hdr); print("-" * len(hdr))
    for r in RULES:
        m = res[r][1]
        rec = f"{m['recovery']}t" if m["recovery"] is not None else "none"
        print(f"{r:18s} {m['viable_final']:10.1f} {m['viable_half']:11.1f} {m['served']:8.1f} "
              f"{m['dead']:>3d}/{m['n_src']:<2d} {m['crossings']:>6d} {m['stock']:7.1f} "
              f"{m['unmet']:7.0f} {m['cum_B']:9.0f} {rec:>9s}")

    colors = {"safe": "#c0392b", "horizon_gate": "#e67e22", "horizon_opt": "#8e44ad",
              "threshold_penalty": "#1b7f4d", "hard_reserve": "#2980b9",
              "penalty_horizon": "#16a085"}
    t = range(1, TICKS + 1)
    for key, ylab, title, fname, ylim in [
        ("stock", "regenerative stock (sum over sources)", "Remaining regenerative capacity", "v24_stock.png", None),
        ("viable", "viable cells (%)", "Viable-cell fraction", "v24_viable.png", (0, 105))]:
        fig, ax = plt.subplots(figsize=(8, 4.3))
        for r in RULES:
            ax.plot(t, res[r][0][key], label=r, color=colors[r], lw=1.6)
        ax.axvline(SHOCK, color="#888", ls="--", lw=1)
        if ylim:
            ax.set_ylim(*ylim)
        ax.set_xlabel("tick"); ax.set_ylabel(ylab); ax.set_title(title + " (V2.4 Allee world)")
        ax.legend(fontsize=8, ncol=2); ax.grid(alpha=0.3); fig.tight_layout()
        fig.savefig(f"{FIGDIR}/{fname}", dpi=130); plt.close()
    print("\nFigures: figures/v24_stock.png, figures/v24_viable.png")


if __name__ == "__main__":
    main()
