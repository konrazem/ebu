"""
V2.3 central experiment:
    Does immediate homeostatic improvement destroy future regenerative capacity?

A closed regenerative economy (no external inflow). Producer cells are Allee stocks
that regrow logistically ABOVE a critical threshold A and DECLINE below it. Crucially
A > L, so a source can be inside the viable burden band (x >= L) yet below its
regeneration threshold (x < A) and dying. A myopic rule that only minimises current
burden is free to harvest sources down toward L, pushing them below A, which is
irreversible. A regeneration-aware (H-horizon) rule should foresee the decline and
refuse the over-harvest.

Compares: gradient, safe (H=1), horizon (H=3, 10, 30). A supply shock knocks the
sources down at tick 500 to test recovery.

Run with the project venv:  .../venv/bin/python exp_v23.py
"""
from __future__ import annotations
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from energy_balance import Grid, Actor, regen_at, burden
from ebu_v23 import step_v23

FIGDIR = "figures"
os.makedirs(FIGDIR, exist_ok=True)

N = 8
A_THRESH = 8.0          # Allee threshold (note: A > L)
L_FLOOR = 4.0
SHOCK_TICK = 500
TICKS = 1200
GAMMA = 0.999


def make_regen_world():
    size = N * N
    is_src = [((i // N) + (i % N)) % 2 == 0 for i in range(size)]
    g = Grid(
        n=N,
        x=[15.0 if is_src[i] else 8.0 for i in range(size)],
        K=[20.0] * size, L=[L_FLOOR] * size, U=[16.0] * size,
        alpha=[1.0] * size, beta=[0.3] * size,
        s=[0.0] * size,                                    # closed: no external inflow
        d=[0.0 if is_src[i] else 0.45 for i in range(size)],
        lam=[0.0] * size, x_min=[0.0] * size,
        rho=[0.3 if is_src[i] else 0.0 for i in range(size)],
        A=[A_THRESH if is_src[i] else 0.0 for i in range(size)],
        leak_frac=[0.003] * size,
    )
    actors = [Actor(pos=i, q_max=3.0, M=0.6, theta=0.05, eta=0.95) for i in range(size)]
    return g, actors, is_src


def run_model(mode, H=1, radius=2):
    g, actors, is_src = make_regen_world()
    src = [i for i in range(g.size) if is_src[i]]
    series = dict(viable=[], src_stock=[], below_A=[], B=[])
    cum_unmet = cum_loss = disc_burden = 0.0
    disc = 1.0
    recov_tick = None
    pre_shock_viable = None
    for t in range(1, TICKS + 1):
        if t == SHOCK_TICK:                                # knock sources down 55%
            for i in src:
                g.x[i] *= 0.45
        r = step_v23(g, actors if mode != "none" else [], t, mode=mode, H=H, radius=radius)
        cum_unmet += r.ledger.unmet_demand
        cum_loss += r.ledger.transport_loss
        disc_burden += disc * r.B_withaction
        disc *= GAMMA
        viable = 100.0 * (g.size - r.n_below_L) / g.size
        series["viable"].append(viable)
        series["src_stock"].append(sum(g.x[i] for i in src))
        series["below_A"].append(sum(1 for i in src if g.x[i] < A_THRESH))
        series["B"].append(r.B_withaction)
        if t == SHOCK_TICK - 1:
            pre_shock_viable = viable
        if recov_tick is None and t > SHOCK_TICK and pre_shock_viable and \
                viable >= 0.9 * pre_shock_viable:
            recov_tick = t
    dead_sources = sum(1 for i in src if g.x[i] < A_THRESH and regen_at(g, i, g.x[i]) <= 0)
    metrics = dict(
        viable_final=series["viable"][-1],
        viable_last_half=sum(series["viable"][TICKS // 2:]) / (TICKS - TICKS // 2),
        src_stock_final=series["src_stock"][-1],
        below_A_final=series["below_A"][-1],
        dead_sources=dead_sources, n_sources=len(src),
        unmet=cum_unmet, transport_loss=cum_loss, disc_burden=disc_burden,
        recovery=recov_tick,
    )
    return series, metrics


MODELS = [("gradient", 1), ("safe", 1), ("horizon", 3), ("horizon", 10), ("horizon", 30)]
def label(mode, H):
    return mode if mode != "horizon" else f"horizon H={H}"


def main():
    results = {}
    for mode, H in MODELS:
        results[label(mode, H)] = run_model(mode, H=H)
        print(f"ran {label(mode, H)}")

    # ---- table ----
    print("\n=== V2.3 regeneration: does immediate gain destroy future capacity? ===")
    hdr = f"{'model':13s} {'viable%(end)':>12s} {'viable%(2nd half)':>17s} {'src stock':>10s} " \
          f"{'dead src':>9s} {'unmet':>9s} {'transp':>8s} {'disc.B':>10s} {'shock rec':>10s}"
    print(hdr); print("-" * len(hdr))
    for name, (_, m) in results.items():
        rec = f"tick {m['recovery']}" if m["recovery"] else "none"
        print(f"{name:13s} {m['viable_final']:12.1f} {m['viable_last_half']:17.1f} "
              f"{m['src_stock_final']:10.1f} {m['dead_sources']:>4d}/{m['n_sources']:<4d} "
              f"{m['unmet']:9.0f} {m['transport_loss']:8.0f} {m['disc_burden']:10.1f} {rec:>10s}")

    # ---- figures ----
    colors = {"gradient": "#e67e22", "safe": "#c0392b",
              "horizon H=3": "#2980b9", "horizon H=10": "#16a085", "horizon H=30": "#1b7f4d"}
    t = range(1, TICKS + 1)

    fig, ax = plt.subplots(figsize=(8, 4.3))
    for name, (s, _) in results.items():
        ax.plot(t, s["src_stock"], label=name, color=colors[name], lw=1.7)
    ax.axvline(SHOCK_TICK, color="#888", ls="--", lw=1); ax.text(SHOCK_TICK + 8, ax.get_ylim()[1]*0.05, "shock")
    ax.set_xlabel("tick"); ax.set_ylabel("total regenerative stock (sum over sources)")
    ax.set_title("Remaining regenerative capacity over time")
    ax.legend(fontsize=8); ax.grid(alpha=0.3); fig.tight_layout()
    fig.savefig(f"{FIGDIR}/v23_src_stock.png", dpi=130); plt.close()

    fig, ax = plt.subplots(figsize=(8, 4.3))
    for name, (s, _) in results.items():
        ax.plot(t, s["viable"], label=name, color=colors[name], lw=1.7)
    ax.axvline(SHOCK_TICK, color="#888", ls="--", lw=1)
    ax.set_xlabel("tick"); ax.set_ylabel("viable cells (%)"); ax.set_ylim(0, 105)
    ax.set_title("Viable-cell fraction over time (Allee regenerative world)")
    ax.legend(fontsize=8, loc="lower left"); ax.grid(alpha=0.3); fig.tight_layout()
    fig.savefig(f"{FIGDIR}/v23_viable.png", dpi=130); plt.close()
    print("\nFigures: figures/v23_src_stock.png, figures/v23_viable.png")


if __name__ == "__main__":
    main()
