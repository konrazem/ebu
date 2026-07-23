"""
V2.4 clustered audit with GENUINELY randomized, paired layouts.

Fixes the V2.3 caveat (the old clustered builder was deterministic). Each seed draws a
distinct world - random cluster count, centre(s), radius, and producer density - and
every model is run on the IDENTICAL world for that seed (paired comparison). We report
the full distribution, not a single mean.

Producers are external-flow sources (rho=0), so the regeneration-specific rules do not
apply here; we compare: none, gradient, safe (H=1), horizon_gate (H=10), horizon_opt.

Run with the project venv:  .../venv/bin/python exp_v24_clustered.py
"""
from __future__ import annotations
import os, random, statistics as st
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from energy_balance import Grid, Actor
from ebu_v23 import step_v23
from ebu_v24 import step_v24

FIGDIR = "figures"; os.makedirs(FIGDIR, exist_ok=True)


def make_clustered_world(n, seed, supply_ratio=2.0, demand=0.4, kappa=0.02):
    rng = random.Random(seed)
    size = n * n
    n_clusters = rng.choice([1, 1, 2])
    centers = [(rng.uniform(0, n - 1), rng.uniform(0, n - 1)) for _ in range(n_clusters)]
    radius = rng.uniform(1.5, 0.35 * n)
    is_prod = [False] * size
    for i in range(size):
        r, c = divmod(i, n)
        for (cr, cc) in centers:
            if (r - cr) ** 2 + (c - cc) ** 2 <= radius ** 2:
                is_prod[i] = True
                break
    if not any(is_prod):
        is_prod[rng.randrange(size)] = True
    if all(is_prod):
        is_prod[rng.randrange(size)] = False
    n_prod = sum(is_prod)
    n_con = size - n_prod
    inflow = supply_ratio * (n_con * demand) / n_prod
    g = Grid(n=n, x=[10.0] * size, K=[20.0] * size, L=[4.0] * size, U=[16.0] * size,
             alpha=[1.0] * size, beta=[0.3] * size,
             s=[inflow if is_prod[i] else 0.0 for i in range(size)],
             d=[0.0 if is_prod[i] else demand for i in range(size)],
             lam=[0.0] * size, rho=[0.0] * size, x_min=[0.0] * size,
             leak_frac=[kappa] * size)
    actors = [Actor(pos=i, q_max=3.0, M=0.6, theta=0.05, eta=0.95) for i in range(size)]
    meta = dict(n_prod=n_prod, radius=radius, n_clusters=n_clusters)
    return g, actors, meta


def run(n, seed, mode, ticks=800, H=10):
    """Return final viable-cell % after `ticks`, using the mean of the last 100 ticks
    to smooth stochastic-free but noisy transport dynamics."""
    g, ac, _ = make_clustered_world(n, seed)
    tail = []
    for t in range(1, ticks + 1):
        if mode == "none":
            step_v23(g, [], t, mode="none")
        elif mode == "horizon_opt":
            step_v24(g, ac, t, rule="horizon_opt", H=H)
        else:
            step_v23(g, ac, t, mode=("horizon" if mode == "horizon_gate" else mode), H=H)
        if t > ticks - 100:
            tail.append(100.0 * (g.size - sum(1 for i in range(g.size) if g.x[i] < g.L[i])) / g.size)
    return sum(tail) / len(tail)


def summarize(name, vals):
    print(f"  {name:14s} n={len(vals):2d}  mean={st.mean(vals):5.1f}  sd={st.pstdev(vals):4.1f}  "
          f"min={min(vals):5.1f}  max={max(vals):5.1f}")


def main():
    N = 8
    CHEAP = ["none", "gradient", "safe", "horizon_gate"]
    n_cheap, n_opt = 20, 6
    print(f"=== Randomized clustered layouts (paired), n={N} ===")
    results = {}
    for mode in CHEAP:
        results[mode] = [run(N, s, mode) for s in range(n_cheap)]
        summarize(mode, results[mode])
    results["horizon_opt"] = [run(N, s, "horizon_opt") for s in range(n_opt)]
    summarize("horizon_opt", results["horizon_opt"])

    # paired improvement safe->horizon_gate on the same layouts
    diffs = [results["horizon_gate"][s] - results["safe"][s] for s in range(n_cheap)]
    print(f"\n  paired (horizon_gate - safe) over {n_cheap} layouts: "
          f"mean {st.mean(diffs):+.1f}, wins {sum(1 for d in diffs if d>0.5)}/{n_cheap}")

    fig, ax = plt.subplots(figsize=(8, 4.3))
    order = CHEAP + ["horizon_opt"]
    ax.boxplot([results[m] for m in order], tick_labels=order, showmeans=True)
    ax.set_ylabel("viable cells (%)"); ax.set_ylim(0, 105)
    ax.set_title(f"Clustered viability across {n_cheap} randomized layouts (n={N})")
    ax.grid(alpha=0.3, axis="y"); fig.tight_layout()
    fig.savefig(f"{FIGDIR}/v24_clustered.png", dpi=130); plt.close()
    print("\nFigure: figures/v24_clustered.png")


if __name__ == "__main__":
    main()
