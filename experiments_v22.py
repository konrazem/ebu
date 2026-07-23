"""
Energy Balance V2.2 - experiments.

Compares three movement models:
    none      - no redistribution (physics only)
    gradient  - raw q = M[F]_+  (original rule, no safeguard)
    safe      - line-searched q* + exact discrete acceptance (V2.2)

on several worlds (checkerboard / random / clustered), across grid sizes and a
supply shock, and produces a PHASE MAP over (supply_ratio, kappa) classifying each
outcome as: deficit collapse / homeostatic / excess accumulation / oscillation.

Run with the project venv:  .../venv/bin/python experiments_v22.py
"""
from __future__ import annotations
import os
import random
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
import numpy as np

from energy_balance import Grid, Actor
from ebu_v22 import step_v22, Ledger

FIGDIR = "figures"
os.makedirs(FIGDIR, exist_ok=True)


# ---------------------------------------------------------------------------
def make_world(n: int, topology: str, supply_ratio: float = 2.0, demand: float = 0.4,
               kappa: float = 0.02, seed: int = 0):
    """Build a world with a fixed TOTAL supply budget = supply_ratio * total_demand,
    distributed evenly among producer cells, so topologies are comparable and only
    their spatial structure differs."""
    size = n * n
    rng = random.Random(seed)
    is_prod = [False] * size
    if topology == "checkerboard":
        for i in range(size):
            r, c = divmod(i, n)
            is_prod[i] = (r + c) % 2 == 0
    elif topology == "random":
        for i in range(size):
            is_prod[i] = rng.random() < 0.5
    elif topology == "clustered":
        # producers packed in the top-left block; consumers everywhere else
        side = max(1, int(round((size * 0.5) ** 0.5)))
        for i in range(size):
            r, c = divmod(i, n)
            is_prod[i] = (r < side and c < side)
    else:
        raise ValueError(topology)

    n_prod = sum(is_prod) or 1
    n_cons = size - sum(is_prod)
    total_demand = n_cons * demand
    inflow_each = supply_ratio * total_demand / n_prod

    g = Grid(
        n=n, x=[10.0] * size, K=[20.0] * size, L=[4.0] * size, U=[16.0] * size,
        alpha=[1.0] * size, beta=[0.3] * size,
        s=[inflow_each if is_prod[i] else 0.0 for i in range(size)],
        d=[0.0 if is_prod[i] else demand for i in range(size)],
        lam=[0.0] * size, rho=[0.0] * size, x_min=[0.0] * size,
        leak_frac=[kappa] * size,
    )
    actors = [Actor(pos=i, q_max=3.0, M=0.6, theta=0.05, eta=0.95) for i in range(size)]
    return g, actors


def run(g, actors, ticks, mode, shock=None):
    """shock = (start, end): set all inflow to 0 during [start, end)."""
    s_save = list(g.s)
    reps = []
    for t in range(1, ticks + 1):
        if shock and shock[0] <= t < shock[1]:
            g.s = [0.0] * g.size
        else:
            g.s = list(s_save)
        reps.append(step_v22(g, actors if mode != "none" else [], t, mode=mode,
                             check_ledger=False))
    return reps


def stats(g, reps):
    half = reps[len(reps) // 2:]
    n = g.size
    below = sum(r.n_below_L for r in half) / len(half) / n
    above = sum(r.n_above_U for r in half) / len(half) / n
    Bmean = sum(r.B_withaction for r in half) / len(half)
    Xs = [r.X for r in half]
    Xmean = sum(Xs) / len(Xs)
    Xamp = (max(Xs) - min(Xs)) / Xmean if Xmean > 1e-9 else 0.0
    loss = sum(r.ledger.transport_loss for r in reps)
    unmet = sum(r.ledger.unmet_demand for r in reps)
    viable = 100.0 * (1.0 - below)
    return dict(below=below, above=above, Bmean=Bmean, Xamp=Xamp,
                loss=loss, unmet=unmet, viable=viable)


REGIMES = ["deficit", "homeostatic", "excess", "oscillation"]


def classify(st) -> str:
    if st["below"] > 0.15:
        return "deficit"
    if st["above"] > 0.15:
        return "excess"
    if st["Xamp"] > 0.08 and st["Bmean"] > 0.05:
        return "oscillation"
    return "homeostatic"


# ---------------------------------------------------------------------------
def exp_topologies(n=10, ticks=2000):
    print("\n=== Topology x model  (n=%d, %d ticks, supply_ratio=2.0, kappa=0.02) ===" % (n, ticks))
    print(f"  {'topology':12s} {'model':9s} {'viable%':>8s} {'B_mean':>9s} "
          f"{'transp.loss':>12s} {'unmet':>10s} {'regime':>13s}")
    for topo in ("checkerboard", "random", "clustered"):
        for mode in ("none", "gradient", "safe"):
            g, actors = make_world(n, topo, seed=1)
            reps = run(g, actors, ticks, mode)
            st = stats(g, reps)
            reg = classify(st) if mode != "none" else "-"
            print(f"  {topo:12s} {mode:9s} {st['viable']:8.1f} {st['Bmean']:9.3f} "
                  f"{st['loss']:12.1f} {st['unmet']:10.1f} {reg:>13s}")


def exp_gridsizes(ticks=2000):
    print("\n=== Grid-size scan  (checkerboard, safe, supply_ratio=2.0, kappa=0.02) ===")
    print(f"  {'n':>3s} {'cells':>6s} {'viable%':>8s} {'B_mean':>9s} {'regime':>13s}")
    for n in (6, 10, 14):
        g, actors = make_world(n, "checkerboard", seed=1)
        reps = run(g, actors, ticks, "safe")
        st = stats(g, reps)
        print(f"  {n:>3d} {n*n:>6d} {st['viable']:8.1f} {st['Bmean']:9.3f} {classify(st):>13s}")


def exp_shock(n=10, ticks=1200):
    print("\n=== Supply shock  (inflow=0 for ticks 400..600), recovery of viable%% ===")
    shock = (400, 600)
    fig, ax = plt.subplots(figsize=(7.5, 4))
    colors = {"none": "#c0392b", "gradient": "#e67e22", "safe": "#1b7f4d"}
    for mode in ("none", "gradient", "safe"):
        g, actors = make_world(n, "checkerboard", seed=1)
        reps = run(g, actors, ticks, mode, shock=shock)
        viab = [100.0 * (g.size - r.n_below_L) / g.size for r in reps]
        ax.plot(range(1, ticks + 1), viab, label=mode, color=colors[mode], lw=1.8)
        # recovery: first tick after shock end where viable >= 90
        rec = next((t for t in range(shock[1], ticks) if viab[t - 1] >= 90.0), None)
        rec_s = f"tick {rec}" if rec else "did not recover"
        print(f"  {mode:9s}  min viable during shock = {min(viab[shock[0]:shock[1]]):5.1f}%   "
              f"recovery to 90% : {rec_s}")
    ax.axvspan(shock[0], shock[1], color="#888888", alpha=0.2, label="shock")
    ax.set_xlabel("tick"); ax.set_ylabel("viable cells (%)"); ax.set_ylim(0, 105)
    ax.set_title("Recovery after a supply interruption (checkerboard)")
    ax.legend(loc="lower right"); ax.grid(alpha=0.3); fig.tight_layout()
    fig.savefig(f"{FIGDIR}/shock_recovery.png", dpi=130); plt.close()


def exp_phase_map(n=8, ticks=1500):
    print("\n=== Phase map  (safe model, checkerboard, eta=0.95, M=0.6) ===")
    supply_ratios = [1.0, 1.4, 1.8, 2.2, 2.6, 3.0]
    kappas = [0.005, 0.01, 0.02, 0.035, 0.05]
    grid = np.zeros((len(kappas), len(supply_ratios)), dtype=int)
    for r, kap in enumerate(kappas):
        row = []
        for c, sr in enumerate(supply_ratios):
            g, actors = make_world(n, "checkerboard", supply_ratio=sr, kappa=kap, seed=1)
            reps = run(g, actors, ticks, "safe")
            reg = classify(stats(g, reps))
            grid[r, c] = REGIMES.index(reg)
            row.append(reg[0].upper())
        print(f"  kappa={kap:5.3f} | " + "  ".join(f"{sr:.1f}:{x}" for sr, x in zip(supply_ratios, row)))

    cmap = ListedColormap(["#8e2b2b", "#1b7f4d", "#b7950b", "#5b2c83"])  # deficit,homeo,excess,osc
    norm = BoundaryNorm([-.5, .5, 1.5, 2.5, 3.5], cmap.N)
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    ax.imshow(grid, cmap=cmap, norm=norm, aspect="auto", origin="lower")
    ax.set_xticks(range(len(supply_ratios))); ax.set_xticklabels([f"{s:.1f}" for s in supply_ratios])
    ax.set_yticks(range(len(kappas))); ax.set_yticklabels([f"{k:.3f}" for k in kappas])
    ax.set_xlabel("supply ratio  (total supply / total demand)")
    ax.set_ylabel("leakage coefficient  kappa")
    ax.set_title("Phase map: outcome of the safe local rule (checkerboard, 8x8)")
    for r in range(len(kappas)):
        for c in range(len(supply_ratios)):
            ax.text(c, r, REGIMES[grid[r, c]][:4], ha="center", va="center",
                    color="white", fontsize=8)
    from matplotlib.patches import Patch
    leg = [Patch(color="#8e2b2b", label="deficit collapse"),
           Patch(color="#1b7f4d", label="homeostatic"),
           Patch(color="#b7950b", label="excess accumulation"),
           Patch(color="#5b2c83", label="oscillation")]
    ax.legend(handles=leg, bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8)
    fig.tight_layout()
    fig.savefig(f"{FIGDIR}/phase_map.png", dpi=130); plt.close()


if __name__ == "__main__":
    exp_topologies()
    exp_gridsizes()
    exp_shock()
    exp_phase_map()
    print("\nFigures written: figures/shock_recovery.png, figures/phase_map.png")
