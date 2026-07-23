"""
Energy Balance V2.0 - analysis, figures, and animation.

Runs the checkerboard ecosystem, captures per-tick grid states, and produces:
  figures/B_vs_time.png        burden B(t), local rule ON vs OFF
  figures/viable_vs_time.png   fraction of viable cells over time
  figures/heatmap_snapshots.png  capacity heatmaps at t = 0, 25, 200 (ON vs OFF)
  figures/inflow_sweep.png     homeostasis window vs renewable supply
  ecosystem.gif                animated heatmap, ON vs OFF side by side ("Game of Life" view)

Run with the project venv:
  .../venv/bin/python analysis.py
"""
from __future__ import annotations
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

from energy_balance import step
from ecosystem import make_ecosystem

N = 10
FIGDIR = "figures"
os.makedirs(FIGDIR, exist_ok=True)


def run_capture(inflow: float, ticks: int, local_rule: bool):
    g, actors = make_ecosystem(N, inflow=inflow)
    if not local_rule:
        actors = []
    frames = [np.array(g.x).reshape(N, N).copy()]
    Bs, viable_frac = [], []
    for t in range(1, ticks + 1):
        rep = step(g, actors, t)
        frames.append(np.array(g.x).reshape(N, N).copy())
        Bs.append(rep.B_withaction)
        viable_frac.append(100.0 * (g.size - rep.n_below_L) / g.size)
    return frames, Bs, viable_frac


def sweep(inflows, ticks=5000):
    B_means, viable_ends = [], []
    for inf in inflows:
        _, Bs, vf = run_capture(inf, ticks, True)
        B_means.append(sum(Bs) / len(Bs))
        viable_ends.append(vf[-1])
    return B_means, viable_ends


def fig_B_vs_time(inflow=0.8, ticks=500):
    _, B_on, _ = run_capture(inflow, ticks, True)
    _, B_off, _ = run_capture(inflow, ticks, False)
    t = range(1, ticks + 1)
    plt.figure(figsize=(7, 4))
    plt.semilogy(t, [max(b, 1e-3) for b in B_on], label="local rule ON", color="#1b7f4d", lw=2)
    plt.semilogy(t, [max(b, 1e-3) for b in B_off], label="local rule OFF", color="#c0392b", lw=2)
    plt.xlabel("tick"); plt.ylabel("burden  B(t)   (log scale)")
    plt.title(f"Homeostatic burden over time  (inflow={inflow})")
    plt.legend(); plt.grid(True, which="both", alpha=0.3); plt.tight_layout()
    plt.savefig(f"{FIGDIR}/B_vs_time.png", dpi=130); plt.close()


def fig_viable_vs_time(inflow=0.8, ticks=500):
    _, _, v_on = run_capture(inflow, ticks, True)
    _, _, v_off = run_capture(inflow, ticks, False)
    t = range(1, ticks + 1)
    plt.figure(figsize=(7, 4))
    plt.plot(t, v_on, label="local rule ON", color="#1b7f4d", lw=2)
    plt.plot(t, v_off, label="local rule OFF", color="#c0392b", lw=2)
    plt.ylim(0, 105)
    plt.xlabel("tick"); plt.ylabel("viable cells  (% with x >= L)")
    plt.title(f"Fraction of viable cells over time  (inflow={inflow})")
    plt.legend(); plt.grid(True, alpha=0.3); plt.tight_layout()
    plt.savefig(f"{FIGDIR}/viable_vs_time.png", dpi=130); plt.close()


def fig_heatmap_snapshots(inflow=0.8):
    ticks = 200
    frames_on, _, _ = run_capture(inflow, ticks, True)
    frames_off, _, _ = run_capture(inflow, ticks, False)
    snaps = [0, 25, 200]
    fig, axes = plt.subplots(2, 3, figsize=(9, 6))
    for col, s in enumerate(snaps):
        for row, (frames, lbl) in enumerate([(frames_on, "ON"), (frames_off, "OFF")]):
            ax = axes[row][col]
            im = ax.imshow(frames[s], vmin=0, vmax=20, cmap="viridis")
            ax.set_title(f"rule {lbl}  |  t={s}", fontsize=10)
            ax.set_xticks([]); ax.set_yticks([])
    fig.colorbar(im, ax=axes, fraction=0.025, pad=0.02, label="capacity x_i")
    fig.suptitle(f"Field capacity, checkerboard ecosystem  (inflow={inflow})", fontsize=12)
    plt.savefig(f"{FIGDIR}/heatmap_snapshots.png", dpi=130); plt.close()


def fig_inflow_sweep():
    inflows = [0.44, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.2]
    B_means, viable_ends = sweep(inflows)
    fig, ax1 = plt.subplots(figsize=(7, 4))
    ax1.plot(inflows, viable_ends, "o-", color="#1b7f4d", label="viable cells at t=5000")
    ax1.set_xlabel("renewable inflow per producer  s")
    ax1.set_ylabel("viable cells (%)", color="#1b7f4d")
    ax1.set_ylim(0, 105); ax1.tick_params(axis="y", labelcolor="#1b7f4d")
    ax2 = ax1.twinx()
    ax2.semilogy(inflows, [max(b, 1e-3) for b in B_means], "s--", color="#8e44ad",
                 label="mean burden B")
    ax2.set_ylabel("mean burden B  (log)", color="#8e44ad")
    ax2.tick_params(axis="y", labelcolor="#8e44ad")
    plt.title("Homeostasis window vs renewable supply")
    fig.tight_layout()
    plt.savefig(f"{FIGDIR}/inflow_sweep.png", dpi=130); plt.close()


def make_gif(inflow=0.8, ticks=150):
    frames_on, B_on, _ = run_capture(inflow, ticks, True)
    frames_off, B_off, _ = run_capture(inflow, ticks, False)
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(8, 4.4))
    imL = axL.imshow(frames_on[0], vmin=0, vmax=20, cmap="viridis")
    imR = axR.imshow(frames_off[0], vmin=0, vmax=20, cmap="viridis")
    for ax in (axL, axR):
        ax.set_xticks([]); ax.set_yticks([])
    axL.set_title("local rule ON"); axR.set_title("local rule OFF")
    fig.colorbar(imL, ax=[axL, axR], fraction=0.025, pad=0.02, label="capacity x_i")
    sup = fig.suptitle("")

    def update(k):
        imL.set_data(frames_on[k])
        imR.set_data(frames_off[k])
        b_on = B_on[k - 1] if k > 0 else 0.0
        b_off = B_off[k - 1] if k > 0 else 0.0
        sup.set_text(f"tick {k}    B(ON)={b_on:6.2f}    B(OFF)={b_off:7.1f}")
        return imL, imR, sup

    ani = animation.FuncAnimation(fig, update, frames=len(frames_on), interval=120, blit=False)
    ani.save("ecosystem.gif", writer=animation.PillowWriter(fps=8))
    plt.close()


if __name__ == "__main__":
    print("Generating figures ...")
    fig_B_vs_time()
    fig_viable_vs_time()
    fig_heatmap_snapshots()
    fig_inflow_sweep()
    print("Generating animation ecosystem.gif ...")
    make_gif()
    print("Done.")
