"""
V2.2.1 audit: separate the causes of the clustered-world failure.

Asks three questions, each isolating one factor:
  A. Variance   - is the failure robust across many random layouts/seeds?
  B. Dissipation - does lossless transport (eta=1) fix the clustered failure?
  C. Myopia      - does foresight (H=3,10,30) alone fix the clustered failure?

Uses step_v23 for every mode so the only thing that changes is the decision rule.
Run with the project venv:  .../venv/bin/python audit_v231.py
"""
from __future__ import annotations
import os
import statistics as st
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from energy_balance import Actor
from ebu_v23 import step_v23
from experiments_v22 import make_world, stats

FIGDIR = "figures"
os.makedirs(FIGDIR, exist_ok=True)


def run(g, actors, ticks, mode, H=1, radius=2, eta=None):
    if eta is not None:
        for a in actors:
            a.eta = eta
    reps = []
    for t in range(1, ticks + 1):
        reps.append(step_v23(g, actors if mode != "none" else [], t,
                             mode=mode, H=H, radius=radius))
    return reps


def viable_of(g, reps):
    return stats(g, reps)["viable"]


# ---------------------------------------------------------------------------
def audit_A_variance(seeds=30, n=10, ticks=1500):
    print(f"\n=== A. Variance over {seeds} seeds (n={n}, {ticks} ticks) ===")
    print(f"  {'world':12s} {'model':9s} {'viable% mean':>13s} {'std':>7s} {'min':>7s} {'max':>7s}")
    out = {}
    for world in ("random", "clustered"):
        for mode in ("gradient", "safe"):
            vs = []
            for s in range(seeds):
                g, ac = make_world(n, world, seed=s)
                vs.append(viable_of(g, run(g, ac, ticks, mode)))
            out[(world, mode)] = vs
            print(f"  {world:12s} {mode:9s} {st.mean(vs):13.1f} {st.pstdev(vs):7.1f} "
                  f"{min(vs):7.1f} {max(vs):7.1f}")
    return out


def audit_B_dissipation(seeds=5, n=10, ticks=1500):
    print(f"\n=== B. Dissipation: clustered, safe rule, vary eta ({seeds} seeds) ===")
    print(f"  {'eta':>5s} {'viable% mean':>13s} {'std':>7s} {'B_mean':>9s} {'unmet(mean)':>12s}")
    etas = [0.90, 0.95, 0.98, 1.00]
    res = {}
    for eta in etas:
        vs, bs, um = [], [], []
        for s in range(seeds):
            g, ac = make_world(n, "clustered", seed=s)
            reps = run(g, ac, ticks, "safe", eta=eta)
            stt = stats(g, reps)
            vs.append(stt["viable"]); bs.append(stt["Bmean"]); um.append(stt["unmet"])
        res[eta] = st.mean(vs)
        print(f"  {eta:5.2f} {st.mean(vs):13.1f} {st.pstdev(vs):7.1f} {st.mean(bs):9.2f} {st.mean(um):12.0f}")
    return res


def audit_C_myopia(seeds=3, n=8, ticks=800):
    print(f"\n=== C. Myopia: clustered, horizon rule, vary H (radius=2, {seeds} seeds, n={n}) ===")
    print(f"  {'H':>3s} {'viable% mean':>13s} {'std':>7s} {'B_mean':>9s} {'unmet(mean)':>12s}")
    Hs = [1, 3, 10, 30]
    res = {}
    for H in Hs:
        vs, bs, um = [], [], []
        for s in range(seeds):
            g, ac = make_world(n, "clustered", seed=s)
            reps = run(g, ac, ticks, "horizon", H=H, radius=2)
            stt = stats(g, reps)
            vs.append(stt["viable"]); bs.append(stt["Bmean"]); um.append(stt["unmet"])
        res[H] = st.mean(vs)
        print(f"  {H:>3d} {st.mean(vs):13.1f} {st.pstdev(vs):7.1f} {st.mean(bs):9.2f} {st.mean(um):12.0f}")
    # a larger radius for H=10 to test whether wider foresight helps
    vs = []
    for s in range(seeds):
        g, ac = make_world(n, "clustered", seed=s)
        vs.append(viable_of(g, run(g, ac, ticks, "horizon", H=10, radius=4)))
    print(f"  H=10, radius=4:  viable% mean {st.mean(vs):.1f}")
    return res


def make_figure(B_res, C_res):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    etas = sorted(B_res); ax1.plot(etas, [B_res[e] for e in etas], "o-", color="#1b7f4d")
    ax1.set_xlabel("transport efficiency  eta"); ax1.set_ylabel("clustered viable cells (%)")
    ax1.set_title("B. Does lossless transport fix it?"); ax1.set_ylim(0, 105); ax1.grid(alpha=0.3)
    Hs = sorted(C_res); ax2.plot(Hs, [C_res[h] for h in Hs], "s-", color="#8e44ad")
    ax2.set_xlabel("foresight horizon  H"); ax2.set_ylabel("clustered viable cells (%)")
    ax2.set_title("C. Does foresight fix it?"); ax2.set_ylim(0, 105); ax2.grid(alpha=0.3)
    fig.suptitle("V2.2.1 audit: isolating the cause of clustered failure")
    fig.tight_layout()
    fig.savefig(f"{FIGDIR}/audit.png", dpi=130); plt.close()


if __name__ == "__main__":
    audit_A_variance()
    B = audit_B_dissipation()
    C = audit_C_myopia()
    make_figure(B, C)
    print("\nFigure written: figures/audit.png")
