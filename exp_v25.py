"""
V2.5 experiments: does the EBU incentive layer help or get gamed?

Part A - four comparisons on the closed Allee economy (physics identical in the
first three; only the ledger / selection changes):
    physics/none        : baseline, no accounting
    physics/naive (obs) : naive accounting, physics-driven selection (observational)
    physics/guarded(obs): guarded accounting, physics-driven selection (observational)
    adversarial/naive   : actors maximise their naive EBU balance (gaming)
    adversarial/guarded : actors maximise their guarded EBU balance

Part B - attack suite: for each known gaming strategy, the net EBU an actor earns
under the naive vs the guarded ledger. Guarded should make each attack non-positive
or strictly bounded; any residual is reported honestly.

Run with the project venv:  .../venv/bin/python exp_v25.py
"""
from __future__ import annotations
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from energy_balance import Grid, Actor, regen_at, local_penalty
from ebu_v24 import reserve_R, pen
from ebu_v25 import EBULedger, step_v25, _action_effect, b_R
from ebu_v23 import nat_cell
import exp_v23

FIGDIR = "figures"; os.makedirs(FIGDIR, exist_ok=True)
TICKS, SHOCK, A = 800, 400, exp_v23.A_THRESH


# ----------------------------------------------------------- Part A
def run_case(selection, mode):
    g, actors, is_src = exp_v23.make_regen_world()
    src = [i for i in range(g.size) if is_src[i]]
    led = EBULedger(mode=mode, lam_L=0.1, lam_F=1.0)
    bR_sum = 0.0
    for t in range(1, TICKS + 1):
        if t == SHOCK:
            for i in src:
                g.x[i] *= 0.45
        r = step_v25(g, actors, led, t, selection=selection)
        bR_sum += r.B_R
    dead = sum(1 for i in src if g.x[i] < A and regen_at(g, i, g.x[i]) <= 0)
    viable = 100.0 * (g.size - sum(1 for i in range(g.size) if g.x[i] < g.L[i])) / g.size
    return dict(viable=viable, dead=dead, n=len(src), bR_mean=bR_sum / TICKS,
                credit=led.issued_credit, debit=led.issued_debit,
                net=sum(led.balances))


def part_A():
    cases = [("physics", "none"), ("physics", "naive"), ("physics", "guarded"),
             ("adversarial", "naive"), ("adversarial", "guarded")]
    print("=== Part A: four comparisons (closed Allee economy, shock at 400) ===")
    hdr = f"{'selection/ledger':22s} {'viable%':>8s} {'dead':>7s} {'B_R mean':>9s} " \
          f"{'issued credit':>14s} {'issued debit':>13s} {'net EBU':>9s}"
    print(hdr); print("-" * len(hdr))
    rows = {}
    for sel, mode in cases:
        r = run_case(sel, mode)
        rows[f"{sel}/{mode}"] = r
        print(f"{sel+'/'+mode:22s} {r['viable']:8.1f} {r['dead']:>3d}/{r['n']:<3d} "
              f"{r['bR_mean']:9.2f} {r['credit']:14.1f} {r['debit']:13.1f} {r['net']:9.1f}")
    return rows


# ----------------------------------------------------------- Part B: attacks
def _grid(x, L=4.0, U=16.0, K=20.0, rho=0.0, A=0.0):
    """2x2 grid; cells 0 (regenerative source, if rho/A set) and 1 are the pair under
    test, cells 2 and 3 are in-band filler."""
    vals = [x[0], x[1], 10.0, 10.0]
    return Grid(n=2, x=vals, K=[K] * 4, L=[L] * 4, U=[U] * 4, alpha=[1.0] * 4,
                beta=[1.0] * 4, s=[0.0] * 4, d=[0.0] * 4, lam=[0.0] * 4,
                rho=[rho, 0.0, 0.0, 0.0], x_min=[0.0] * 4, A=[A, 0.0, 0.0, 0.0])


def _net(mode, g, seq, lam_L=0.1, lam_F=1.0, pretick_plainB=None):
    """Apply a sequence of (i,j,q,eta,c0) actions through the ledger accounting on a
    single live state; return net EBU. pretick_plainB fixes the naive baseline."""
    R = reserve_R(g, 3.0)
    xa = list(g.x)
    cur_plainB = sum(local_penalty(g, k, xa[k]) for k in range(g.size))
    if pretick_plainB is None:
        pretick_plainB = cur_plainB
    tot = 0.0
    for (i, j, q, eta, c0) in seq:
        c, d, xi, xj, _ = _action_effect(mode, g, i, j, q, eta, c0, xa, R, 1.0,
                                         cur_plainB, pretick_plainB, lam_L, lam_F)
        cur_plainB += (local_penalty(g, i, xi) - local_penalty(g, i, xa[i])
                       + local_penalty(g, j, xj) - local_penalty(g, j, xa[j]))
        xa[i], xa[j] = xi, xj
        tot += c - d
    return tot


def part_B():
    print("\n=== Part B: attack suite (net EBU an actor earns) ===")
    print(f"  {'attack':34s} {'naive':>9s} {'guarded':>9s}  closed?")
    attacks = []

    # round trip (back-and-forth), lossy
    g = _grid([18.0, 5.0])
    seq = [(0, 1, 5.0, 0.95, 0.0), (1, 0, 5.0, 0.95, 0.0)]
    attacks.append(("back-and-forth (round trip)", _net("naive", g, seq), _net("guarded", g, seq)))

    # damage then repair (lossless -> guarded nets 0)
    g = _grid([10.0, 10.0])
    seq = [(0, 1, 8.0, 1.0, 0.0), (1, 0, 8.0, 1.0, 0.0)]
    attacks.append(("damage then repair", _net("naive", g, seq), _net("guarded", g, seq)))

    # split one transfer into many (c0>0)
    g = _grid([18.0, 4.0])
    one = [(0, 1, 4.0, 0.95, 0.2)]
    many = [(0, 1, 1.0, 0.95, 0.2)] * 4
    attacks.append(("split 1 transfer into 4",
                    _net("naive", g, many) - _net("naive", g, one),
                    _net("guarded", g, many) - _net("guarded", g, one)))

    # sacrifice regenerative stock: harvest a source from just above A to below A
    g = _grid([10.0, 4.0], rho=0.4, A=8.0)      # cell0 source at 10 (>A=8), cell1 deficit
    seq = [(0, 1, 5.0, 0.95, 0.0)]              # pulls source to ~5 (below A)
    attacks.append(("sacrifice regen (harvest below A)", _net("naive", g, seq), _net("guarded", g, seq)))

    # claim natural regeneration: tiny action while a big regen happens this tick.
    # naive credits vs pre-regen field; guarded only the action's live effect.
    g = _grid([4.0, 12.0], L=8.0, rho=0.6)
    pre = sum(local_penalty(g, k, g.x[k]) for k in range(g.size))
    x0 = [nat_cell(g, k, g.x[k])[0] for k in range(g.size)]   # after natural regen
    gr = _grid(x0, L=8.0, rho=0.6)
    seq = [(1, 0, 0.5, 0.95, 0.0)]
    attacks.append(("claim natural regeneration",
                    _net("naive", gr, seq, pretick_plainB=pre),
                    _net("guarded", gr, seq, pretick_plainB=pre)))

    # duplicate credit: two actors serve the same deficit in sequence
    g = _grid([18.0, 2.0])
    seq = [(0, 1, 3.0, 1.0, 0.0), (0, 1, 3.0, 1.0, 0.0)]     # two identical claims
    # naive re-credits vs fixed pretick; guarded telescopes
    attacks.append(("duplicate credit (2 actors, same fix)", _net("naive", g, seq), _net("guarded", g, seq)))

    for name, nv, gd in attacks:
        closed = "yes" if gd <= 1e-6 or gd < nv - 1e-6 else "partial"
        print(f"  {name:34s} {nv:9.2f} {gd:9.2f}  {closed}")
    return attacks


def figure(rowsA):
    labels = list(rowsA.keys())
    viable = [rowsA[k]["viable"] for k in labels]
    net = [rowsA[k]["net"] for k in labels]
    fig, ax1 = plt.subplots(figsize=(9, 4.5))
    x = range(len(labels))
    ax1.bar([i - 0.2 for i in x], viable, width=0.4, color="#1b7f4d", label="viable %")
    ax1.set_ylabel("viable cells (%)", color="#1b7f4d"); ax1.set_ylim(0, 105)
    ax2 = ax1.twinx()
    ax2.bar([i + 0.2 for i in x], net, width=0.4, color="#8e44ad", label="net EBU issued")
    ax2.set_ylabel("net EBU (sum of balances)", color="#8e44ad")
    ax1.set_xticks(list(x)); ax1.set_xticklabels(labels, rotation=20, ha="right", fontsize=8)
    ax1.set_title("V2.5: health vs EBU across ledger/selection")
    fig.tight_layout(); fig.savefig(f"{FIGDIR}/v25_compare.png", dpi=130); plt.close()


if __name__ == "__main__":
    rowsA = part_A()
    part_B()
    figure(rowsA)
    print("\nFigure: figures/v25_compare.png")
