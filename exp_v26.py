"""
V2.6 experiments: automated adversarial testing of the guarded EBU ledger.

Two clearly separated objectives (kept apart in the report):
  (I)  Automated adversary that maximises its own cumulative guarded EBU.
  (II) Red-team search that hunts specifically for a PROFITABLE HARMFUL sequence
       (positive net EBU AND persistent physical harm vs a paired no-action baseline).

Positive control: the red-team run on the NAIVE ledger must rediscover a known naive
exploit; if it cannot, the search is too weak to judge the guarded ledger.

FINAL fixed parameters (not tuned on evaluation seeds) are declared at the top.
Run with the project venv:  .../venv/bin/python exp_v26.py
"""
from __future__ import annotations
import os, random, time, statistics as st
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from energy_balance import Grid, Actor
from ebu_v24 import reserve_R
from ebu_v25 import EBULedger, step_v25, b_R
from ebu_v26 import (State, source_cells, phys_metrics, forced_tick, run_random,
                     beam_search, redteam_search, find_exploit, coalition_net,
                     baseline_BR_schedule, persistence_tail, classify_exploit)

FIGDIR = "figures"; os.makedirs(FIGDIR, exist_ok=True)

# ---- FINAL fixed parameters ------------------------------------------------
DELTA, CHI, LAM_L, LAM_F = 3.0, 1.0, 0.1, 1.0
DEPTH, WIDTH, TAIL, QUANTS = 10, 40, 20, (0.5, 1.0)
COALITION = [0, 1]
MARGIN = 1.0
RAND_SEEDS = list(range(12))          # topology study seeds (final)
A_THRESH = 8.0


# ---- worlds ----------------------------------------------------------------
def redteam_world():
    """3x3: centre cell is an Allee source; the 8 rim cells are deficient consumers.
    Two coalition actors (at the source and at a rim relay)."""
    n, size = 3, 9
    is_src = [i == 4 for i in range(size)]
    g = Grid(n=n, x=[15.0 if is_src[i] else 3.0 for i in range(size)],
             K=[20.0] * size, L=[4.0] * size, U=[16.0] * size, alpha=[1.0] * size,
             beta=[0.3] * size, s=[0.0] * size,
             d=[0.0 if is_src[i] else 0.3 for i in range(size)], lam=[0.0] * size,
             rho=[0.3 if is_src[i] else 0.0 for i in range(size)], x_min=[0.0] * size,
             A=[A_THRESH if is_src[i] else 0.0 for i in range(size)],
             leak_frac=[0.005] * size)
    actors = [Actor(pos=4, q_max=4.0, M=0.6, theta=0.05, eta=0.95),
              Actor(pos=1, q_max=4.0, M=0.6, theta=0.05, eta=0.95)]
    return g, actors, source_cells(g)


def random_allee_world(seed, n=5, src_frac=0.4):
    """Randomised Allee layout: ~src_frac of cells are Allee sources, rest consumers.
    Deterministic per seed; different seeds give genuinely different layouts."""
    rng = random.Random(seed)
    size = n * n
    is_src = [rng.random() < src_frac for _ in range(size)]
    if not any(is_src):
        is_src[rng.randrange(size)] = True
    g = Grid(n=n, x=[15.0 if is_src[i] else 6.0 for i in range(size)],
             K=[20.0] * size, L=[4.0] * size, U=[16.0] * size, alpha=[1.0] * size,
             beta=[0.3] * size, s=[0.0] * size,
             d=[0.0 if is_src[i] else 0.4 for i in range(size)], lam=[0.0] * size,
             rho=[0.35 if is_src[i] else 0.0 for i in range(size)], x_min=[0.0] * size,
             A=[A_THRESH if is_src[i] else 0.0 for i in range(size)],
             leak_frac=[0.01] * size)
    actors = [Actor(pos=i, q_max=3.0, M=0.6, theta=0.05, eta=0.95) for i in range(size)]
    return g, actors, source_cells(g), is_src


# ---- helpers ---------------------------------------------------------------
def run_stepv25_traj(world, selection, mode, ticks):
    g, actors, src = world()
    led = EBULedger(mode=mode, lam_L=LAM_L, lam_F=LAM_F)
    R = reserve_R(g, DELTA)
    for t in range(1, ticks + 1):
        step_v25(g, actors, led, t, selection=selection, delta=DELTA, chi=CHI)
    m = phys_metrics(g, g.x, R, CHI, src)
    m["net"] = sum(led.balances)
    m["credit"] = led.issued_credit; m["debit"] = led.issued_debit
    return m


# ---- (A) five-policy comparison -------------------------------------------
def five_policy_comparison():
    print("=== (A) Five policies on the red-team world (identical initial state) ===")
    print(f"  {'policy':26s} {'viable%':>8s} {'B_R':>7s} {'dead':>5s} {'stock':>6s} {'net EBU':>8s}")
    rows = {}
    # 1 physics/none, 2 naive greedy, 3 guarded greedy  (via frozen step_v25)
    rows["1 physics / no EBU"] = run_stepv25_traj(redteam_world, "physics", "none", DEPTH)
    rows["2 naive greedy adversary"] = run_stepv25_traj(redteam_world, "adversarial", "naive", DEPTH)
    rows["3 guarded greedy adversary"] = run_stepv25_traj(redteam_world, "adversarial", "guarded", DEPTH)
    # 4 random adversary
    rr = run_random(redteam_world, COALITION, DEPTH, seed=0, mode="guarded",
                    delta=DELTA, chi=CHI, lam_L=LAM_L, lam_F=LAM_F)
    g = rr["g"]; R = reserve_R(g, DELTA)
    m = phys_metrics(g, rr["state"].x, R, CHI, rr["src"]); m["net"] = coalition_net(rr["state"], COALITION)
    rows["4 random adversary"] = m
    # 5 automated guarded adversary (beam, maximise cumulative guarded net EBU)
    g, actors, src = redteam_world()
    init = State(list(g.x), [0.0] * len(actors))
    beams, expl = beam_search(g, actors, COALITION, init, "guarded", DEPTH, WIDTH, QUANTS,
                              objective=lambda s, _src: coalition_net(s, COALITION),
                              delta=DELTA, chi=CHI, lam_L=LAM_L, lam_F=LAM_F)
    bs = beams[0][0]; R = reserve_R(g, DELTA)
    m = phys_metrics(g, bs.x, R, CHI, src); m["net"] = coalition_net(bs, COALITION)
    rows["5 automated guarded (beam)"] = m
    rows["5 automated guarded (beam)"]["explored"] = expl

    for k, m in rows.items():
        print(f"  {k:26s} {m['viable']:8.1f} {m['B_R']:7.1f} {m['dead']:>5d} "
              f"{m['stock']:6.1f} {m.get('net', 0.0):8.2f}")
    print(f"  (beam explored {rows['5 automated guarded (beam)']['explored']} states)")
    return rows


# ---- (B) red-team search: hunt for profitable persistent harm --------------
def red_team():
    print("\n=== (B) Red-team search for a PROFITABLE HARMFUL sequence ===")
    print(f"  params: depth={DEPTH} width={WIDTH} tail={TAIL} quants={QUANTS} coalition={COALITION}")
    out = {}
    for mode in ("naive", "guarded"):
        g, actors, src = redteam_world()
        init = State(list(g.x), [0.0] * len(actors))
        base, _ = baseline_BR_schedule(g, actors, init, DEPTH + TAIL, mode,
                                       DELTA, CHI, LAM_L, LAM_F)
        t0 = time.time()
        beams, expl = redteam_search(g, actors, COALITION, init, mode, DEPTH, WIDTH,
                                     QUANTS, base[:DEPTH], DELTA, CHI, LAM_L, LAM_F, min_net=0.5)
        v = find_exploit(g, actors, COALITION, beams, mode, base[DEPTH:DEPTH + TAIL],
                         TAIL, DELTA, CHI, LAM_L, LAM_F, MARGIN)
        dt = time.time() - t0
        out[mode] = v
        tag = "EXPLOIT FOUND" if v.is_exploit else "no exploit found"
        print(f"  {mode:8s}: {tag}  | net EBU={v.net_ebu:+.2f}  persistent_harm={v.harm_persistent}  "
              f"mean tail-harm(B_R)={v.harm_margin:+.2f}  explored={expl}  {dt:.1f}s")
    ctl = "naive positive control PASSED" if out["naive"].is_exploit else "naive positive control FAILED"
    print(f"  {ctl} (naive rediscovers a known exploit)")
    return out


H_RUN = DEPTH * 3                                   # attack horizon for study C (30 ticks)


def studyC_layout(seed):
    """Run one paired layout. Baseline (no-action) and guarded adversary start from
    SEPARATE but identical worlds (both from random_allee_world(seed)). For any
    positive-reward harmful layout, apply the full persistence-window exploit test.
    Returns a per-seed record."""
    g_base, actors_b, src, mask = random_allee_world(seed)
    g_att, actors_a, _, mask2 = random_allee_world(seed)
    assert mask == mask2 and g_base.x == g_att.x        # identical initial states (paired)
    init = State(list(g_base.x), [0.0] * len(actors_b))
    R = reserve_R(g_att, DELTA)

    # paired NO-ACTION baseline over the full horizon (attack + tail), side-effect-free
    base, _ = baseline_BR_schedule(g_base, actors_b, init, H_RUN + TAIL, "guarded",
                                   DELTA, CHI, LAM_L, LAM_F)

    # guarded greedy adversary on the independent identical world
    led = EBULedger(mode="guarded", lam_L=LAM_L, lam_F=LAM_F)
    for t in range(1, H_RUN + 1):
        step_v25(g_att, actors_a, led, t, selection="adversarial", delta=DELTA, chi=CHI)
    m = phys_metrics(g_att, g_att.x, R, CHI, src)
    net = sum(led.balances)
    harm_final = m["B_R"] - base[H_RUN - 1]             # B_R(attack@30) - B_R(no-action@30)

    rec = dict(seed=seed, mask=tuple(mask), net=net, harm_final=harm_final,
               viable=m["viable"], dead=m["dead"], n_src=len(src),
               harmful=(net > 0.0 and harm_final > MARGIN), exploit=False,
               tail_margin=None)
    if rec["harmful"]:
        # FULL persistence test: attackers rest for TAIL ticks; compare to paired baseline tail
        st_final = State(list(g_att.x), list(led.balances))
        atail, s_end = persistence_tail(g_att, actors_a, st_final, "guarded", TAIL,
                                        DELTA, CHI, LAM_L, LAM_F)
        v = classify_exploit(net, atail, base[H_RUN:H_RUN + TAIL], MARGIN)
        mend = phys_metrics(g_att, s_end.x, R, CHI, src)
        rec.update(exploit=v.is_exploit, tail_margin=v.harm_margin,
                   dead_end=mend["dead"], viable_end=mend["viable"])
    return rec


def randomized_study():
    print(f"\n=== (C) Randomized Allee layouts: guarded greedy adversary vs PAIRED no-action ===")
    print(f"  {len(RAND_SEEDS)} seeds (5x5), attack horizon {H_RUN} ticks, persistence tail {TAIL} ticks")
    recs = [studyC_layout(s) for s in RAND_SEEDS]
    masks = [r["mask"] for r in recs]
    distinct = len(set(masks)) == len(masks)
    print(f"  layout masks pairwise distinct: {distinct} ({len(set(masks))}/{len(masks)} unique)")
    nets = [r["net"] for r in recs]; viables = [r["viable"] for r in recs]
    harms = [r["harm_final"] for r in recs]
    def s(v): return f"mean={st.mean(v):.2f} sd={st.pstdev(v):.2f} min={min(v):.2f} max={max(v):.2f}"
    print(f"  net guarded EBU:            {s(nets)}")
    print(f"  final viability %:          {s(viables)}")
    print(f"  harm@{H_RUN} (B_R vs no-act):  {s(harms)}   (positive => worse than doing nothing)")
    harmful = [r for r in recs if r["harmful"]]
    exploits = [r for r in recs if r["exploit"]]
    print(f"  positive-reward harmful layouts (net>0 AND harm>{MARGIN}): {len(harmful)}/{len(recs)}")
    print(f"  CONFIRMED persistent-harm guarded exploits (full definition): {len(exploits)}/{len(recs)}")
    for r in exploits:
        print(f"    seed {r['seed']}: net=+{r['net']:.2f}  harm@{H_RUN}=+{r['harm_final']:.2f}  "
              f"dead@{H_RUN}={r['dead']}/{r['n_src']}  mean tail-harm=+{r['tail_margin']:.2f}  "
              f"dead@end={r.get('dead_end')}/{r['n_src']}  viable@end={r.get('viable_end'):.0f}%")
    return dict(recs=recs, nets=nets, viables=viables, harms=harms,
                n_harmful=len(harmful), n_exploit=len(exploits), distinct=distinct)


def figures(rowsA, studyC):
    labels = list(rowsA.keys())
    fig, ax1 = plt.subplots(figsize=(9, 4.6))
    x = range(len(labels))
    ax1.bar([i - 0.2 for i in x], [rowsA[k]["viable"] for k in labels], 0.4,
            color="#1b7f4d", label="viable %")
    ax1.set_ylabel("viable %", color="#1b7f4d"); ax1.set_ylim(0, 105)
    ax2 = ax1.twinx()
    ax2.bar([i + 0.2 for i in x], [rowsA[k].get("net", 0.0) for k in labels], 0.4,
            color="#8e44ad", label="coalition net EBU")
    ax2.set_ylabel("coalition net EBU", color="#8e44ad")
    ax1.set_xticks(list(x)); ax1.set_xticklabels(labels, rotation=25, ha="right", fontsize=7)
    ax1.set_title("V2.6 (A): five policies on the red-team world")
    fig.tight_layout(); fig.savefig(f"{FIGDIR}/v26_policies.png", dpi=130); plt.close()

    fig, ax = plt.subplots(figsize=(7.5, 4.3))
    recs = studyC["recs"]
    for r in recs:
        col = "#c0392b" if r["exploit"] else ("#e67e22" if r["harmful"] else "#8e44ad")
        ax.scatter(r["net"], r["harm_final"], c=col, s=55,
                   edgecolors="black" if r["exploit"] else "none", linewidths=1.2)
        if r["exploit"]:
            ax.annotate(f"seed {r['seed']}\n(confirmed exploit)", (r["net"], r["harm_final"]),
                        fontsize=8, color="#c0392b", xytext=(6, -4), textcoords="offset points")
    ax.axhline(0, color="#888", ls="--", lw=1)
    ax.set_xlabel("coalition net guarded EBU (paired)")
    ax.set_ylabel("harm@30: B_R(attack) - B_R(no-action)")
    ax.set_title(f"V2.6 (C): guarded greedy adversary vs paired no-action ({len(recs)} random layouts)")
    ax.text(0.02, 0.96, "above 0 = worse than doing nothing; red = confirmed persistent exploit",
            transform=ax.transAxes, fontsize=8, va="top", color="#c0392b")
    ax.grid(alpha=0.3); fig.tight_layout(); fig.savefig(f"{FIGDIR}/v26_random.png", dpi=130); plt.close()


if __name__ == "__main__":
    rowsA = five_policy_comparison()
    out = red_team()
    studyC = randomized_study()
    figures(rowsA, studyC)
    print("\nFigures: figures/v26_policies.png, figures/v26_random.png")
    print("\nSUMMARY:")
    print(f"  naive positive control: {'PASSED' if out['naive'].is_exploit else 'FAILED'}")
    print(f"  hand-built guarded red-team (B): {'exploit found' if out['guarded'].is_exploit else 'no exploit found'}")
    print(f"  randomized guarded study (C): {studyC['n_exploit']} CONFIRMED persistent-harm "
          f"exploit(s) out of {len(studyC['recs'])} layouts")
    if studyC["n_exploit"] > 0:
        print("  => CONCLUSION: the hand-built search found no failure, but the corrected randomized")
        print("     study found at least one PROFITABLE PERSISTENT-HARM guarded trajectory.")
    else:
        print("  => No profitable persistent-harm guarded exploit found within the declared budget.")
