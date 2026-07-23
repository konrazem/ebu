"""
Energy Balance V2.0 - self-sustaining ecosystem experiment.

Question (Sec. 1): can PURELY LOCAL rules keep the field viable forever, with no
central optimizer?  "Like Game of Life": local rules only, run long, watch balance.

Setup: a producer/consumer checkerboard on an n x n lattice.
  - Producer cells:  renewable external inflow s>0, no demand   (Sec. 3, renewable flow)
  - Consumer cells:  demand d>0, no inflow                       (metabolism)
Every consumer's 4 neighbors are producers and vice versa, so the local gradient
rule (Sec. 7) only ever needs ONE-HOP transfers -> locality (Law 1), low transport loss.

One actor sits on every cell and applies the same local law. Nothing is globally
coordinated. We then compare the local rule ON vs OFF over long horizons.
"""
from __future__ import annotations
from energy_balance import Grid, Actor, step, burden


def make_ecosystem(n: int, inflow: float = 0.6, demand: float = 0.4,
                   kappa: float = 0.02) -> tuple[Grid, list[Actor]]:
    size = n * n
    g = Grid(
        n=n,
        x=[10.0] * size,         # start mid-band
        K=[20.0] * size,
        L=[4.0] * size,          # min viable reserve
        U=[16.0] * size,         # oversupply threshold
        alpha=[1.0] * size,      # deficit penalty
        beta=[0.3] * size,       # (milder) excess penalty
        s=[0.0] * size,
        d=[0.0] * size,
        lam=[0.0] * size,
        rho=[0.0] * size,        # renewable-inflow world (g_i = 0), Sec. 3
        x_min=[0.0] * size,
        leak_frac=[kappa] * size,  # proportional leakage: self-regulating sink
    )
    for i in range(size):
        r, c = divmod(i, n)
        if (r + c) % 2 == 0:     # producer: renewable inflow, no demand
            g.s[i] = inflow
            g.d[i] = 0.0
        else:                    # consumer: demand, no inflow -> depends on transport
            g.s[i] = 0.0
            g.d[i] = demand
    # One local actor per cell, all identical, all applying the same rule.
    actors = [Actor(pos=i, q_max=3.0, M=0.6, theta=0.05, eta=0.95)
              for i in range(size)]
    return g, actors


def summarize(g: Grid, reps) -> dict:
    n = g.size
    Bs = [r.B_withaction for r in reps]
    return {
        "ticks": len(reps),
        "B_mean": sum(Bs) / len(Bs),
        "B_final": Bs[-1],
        "B_max": max(Bs),
        "viable_final": sum(1 for i in range(n) if g.x[i] >= g.L[i]),
        "cells": n,
        "min_cell_final": min(g.x),
        "X_final": sum(g.x),
    }


def run_case(n: int, ticks: int, local_rule: bool, inflow: float = 0.6) -> dict:
    g, actors = make_ecosystem(n, inflow=inflow)
    if not local_rule:
        actors = []              # rule OFF: physics runs, but no redistribution
    reps = []
    collapse_tick = None
    for t in range(1, ticks + 1):
        rep = step(g, actors, t)
        reps.append(rep)
        if collapse_tick is None and rep.n_below_L > 0:
            collapse_tick = t
    s = summarize(g, reps)
    s["collapse_tick"] = collapse_tick
    s["local_rule"] = local_rule
    return s


def report(label: str, s: dict):
    frac = 100.0 * s["viable_final"] / s["cells"]
    col = s["collapse_tick"]
    col_str = f"first deficit at tick {col}" if col else "no cell ever fell below L"
    print(f"  {label}")
    print(f"    ticks={s['ticks']}  B_mean={s['B_mean']:.3f}  B_final={s['B_final']:.3f}"
          f"  B_max={s['B_max']:.3f}")
    print(f"    viable cells at end: {s['viable_final']}/{s['cells']} ({frac:.0f}%)"
          f"   min cell={s['min_cell_final']:.2f}   X={s['X_final']:.1f}")
    print(f"    {col_str}")


if __name__ == "__main__":
    N = 10

    # --- Sweep inflow (with proportional leakage) to find real homeostasis ---
    print(f"=== inflow sweep ({N}x{N}, 5000 ticks, rule ON, kappa=0.02) ===")
    print(f"  {'inflow':>7} {'B_mean':>9} {'B_final':>9} {'viable':>7} {'mincell':>8}")
    for inflow in (0.44, 0.50, 0.60, 0.80, 1.00):
        s = run_case(N, 5000, True, inflow=inflow)
        print(f"  {inflow:>7.2f} {s['B_mean']:>9.2f} {s['B_final']:>9.2f}"
              f" {s['viable_final']:>4}/{s['cells']:<2} {s['min_cell_final']:>8.2f}")

    # --- Long-horizon ON vs OFF at a balanced supply level ---
    BAL = 0.8
    for ticks in (200, 5000, 50000):
        print(f"\n=== {N}x{N} ecosystem, {ticks} ticks, inflow={BAL} ===")
        report("LOCAL RULE ON  (gradient-flow actors)", run_case(N, ticks, True, inflow=BAL))
        report("LOCAL RULE OFF (no redistribution)   ", run_case(N, ticks, False, inflow=BAL))
