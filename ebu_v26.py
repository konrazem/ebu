"""
Energy Balance - Foundation Model V2.6
Automated adversarial testing of the guarded EBU ledger. NO economic features
(no prices/ownership/transfer) - this is a falsification/search stage only.

Central question:
  Can an automated actor or coalition find action sequences that earn POSITIVE
  cumulative guarded EBU while causing PERSISTENT physical harm?

This module adds, without modifying any frozen file (energy_balance, ebu_v22..v25):
  * a forced-action tick harness that reuses the V2.5 accounting verbatim
    (_action_effect) so guarded/naive semantics are identical to V2.5;
  * physical + EBU metrics;
  * per-tick policies (physics via frozen step_v25, random, greedy);
  * a deterministic beam search over multi-tick, multi-actor action sequences;
  * an explicit exploit predicate (positive net EBU AND persistent physical harm).
"""
from __future__ import annotations
from dataclasses import dataclass, field
from itertools import product

from energy_balance import Grid, Actor, local_penalty, regen_at
from ebu_v23 import natural_update_ledger
from ebu_v24 import reserve_R, pen
from ebu_v25 import EBULedger, _action_effect, b_plain, b_R, step_v25

# ---------------------------------------------------------------- metrics
def source_cells(g: Grid):
    if g.A is None:
        return []
    return [i for i in range(g.size) if g.rho[i] > 0 and g.A[i] > 0]


def phys_metrics(g: Grid, x, R, chi, src):
    below_L = sum(1 for i in range(g.size) if x[i] < g.L[i])
    dead = sum(1 for i in src if x[i] < g.A[i] and regen_at(g, i, x[i]) <= 0)
    below_A = sum(1 for i in src if x[i] < g.A[i])
    return dict(
        viable=100.0 * (g.size - below_L) / g.size,
        dead=dead, below_A=below_A,
        stock=sum(x[i] for i in src),
        B_R=b_R(g, x, R, chi), B_plain=b_plain(g, x), X=sum(x))


# ---------------------------------------------------------------- forced tick harness
@dataclass
class State:
    x: list                       # capacities
    bal: list                     # per-actor EBU balances
    issued_c: float = 0.0
    issued_d: float = 0.0

    def copy(self):
        return State(list(self.x), list(self.bal), self.issued_c, self.issued_d)


def feasible_q(g: Grid, a: Actor, i, j, xa, q):
    return min(q, a.q_max, xa[i] - g.x_min[i] - a.c0, (g.K[j] - xa[j]) / a.eta)


def forced_tick(g: Grid, actors, st: State, actions, mode, delta=3.0, chi=1.0,
                lam_L=0.1, lam_F=1.0):
    """Apply ONE physical tick: natural update, then the given actor actions (each
    feasibility-clipped), with the frozen V2.5 accounting. Returns (new State, record).
    `record` includes the conservation flow so tests can verify dX exactly."""
    g.x = list(st.x)                              # natural_update_ledger / reserve_R read g.x
    R = reserve_R(g, delta)
    pretick_plainB = b_plain(g, g.x)
    x0, flow = natural_update_ledger(g)           # does not mutate g.x
    xa = list(x0)
    cur_plainB = b_plain(g, xa)
    bal = list(st.bal)
    ic, idb, tc, td, loss = st.issued_c, st.issued_d, 0.0, 0.0, 0.0
    for (ai, i, j, q) in actions:
        a = actors[ai]
        qf = feasible_q(g, a, i, j, xa, q)
        if qf <= 1e-12:
            continue
        credit, debit, xi1, xj1, l = _action_effect(
            mode, g, i, j, qf, a.eta, a.c0, xa, R, chi, cur_plainB, pretick_plainB, lam_L, lam_F)
        cur_plainB += (local_penalty(g, i, xi1) - local_penalty(g, i, xa[i])
                       + local_penalty(g, j, xj1) - local_penalty(g, j, xa[j]))
        xa[i], xa[j] = xi1, xj1
        bal[ai] += credit - debit
        ic += credit; idb += debit; tc += credit; td += debit; loss += l
    flow.transport_loss += loss
    new = State(xa, bal, ic, idb)
    rec = dict(credit=tc, debit=td, loss=loss, flow=flow,
               dX=sum(xa) - sum(st.x))
    return new, rec


# ---------------------------------------------------------------- per-tick policies
def run_stepv25(world_fn, selection, mode, ticks, shock=None, delta=3.0, chi=1.0,
                lam_L=0.1, lam_F=1.0):
    """Drive the FROZEN step_v25 for physics / greedy-adversary controls. Returns
    per-tick series, final grid, and ledger. Physics-only trajectory is therefore
    identical to the V2.5 baseline by construction."""
    g, actors, src = world_fn()
    led = EBULedger(mode=mode, lam_L=lam_L, lam_F=lam_F)
    R = reserve_R(g, delta)
    series = {k: [] for k in ("viable", "B_R", "stock", "dead")}
    for t in range(1, ticks + 1):
        if shock and t == shock[0]:
            for i in src:
                g.x[i] *= shock[1]
        step_v25(g, actors, led, t, selection=selection, delta=delta, chi=chi)
        m = phys_metrics(g, g.x, R, chi, src)
        for k in series:
            series[k].append(m[k])
    return dict(series=series, g=g, actors=actors, src=src, led=led)


def random_actions(g, actors, coalition, xa, rng, rest_prob=0.3, quants=(0.5, 1.0)):
    acts = []
    for ai in coalition:
        a = actors[ai]
        if rng.random() < rest_prob:
            continue
        nbrs = g.neighbors(a.pos)
        if not nbrs:
            continue
        j = rng.choice(nbrs)
        q = rng.choice(quants) * a.q_max
        acts.append((ai, a.pos, j, q))
    return acts


def run_random(world_fn, coalition, ticks, seed, mode="guarded", shock=None,
               delta=3.0, chi=1.0, lam_L=0.1, lam_F=1.0):
    import random
    rng = random.Random(seed)
    g, actors, src = world_fn()
    R = reserve_R(g, delta)
    st = State(list(g.x), [0.0] * len(actors))
    series = {k: [] for k in ("viable", "B_R", "stock", "dead")}
    for t in range(1, ticks + 1):
        if shock and t == shock[0]:
            st.x = list(st.x)
            for i in src:
                st.x[i] *= shock[1]
        acts = random_actions(g, actors, coalition, st.x, rng)
        st, rec = forced_tick(g, actors, st, acts, mode, delta, chi, lam_L, lam_F)
        m = phys_metrics(g, st.x, R, chi, src)
        for k in series:
            series[k].append(m[k])
    return dict(series=series, state=st, src=src, actors=actors, g=g)


# ---------------------------------------------------------------- beam search
def action_menu(g, actors, coalition, xa, quants):
    """Per coalition-actor candidate actions (None = rest). Includes several transfer
    quantities (small splits + full) to each admissible neighbour."""
    menus = []
    for ai in coalition:
        a = actors[ai]
        i = a.pos
        opts = [None]
        for j in g.neighbors(i):
            if (g.K[j] - xa[j]) <= 1e-9 or (xa[i] - g.x_min[i]) <= 1e-9:
                continue
            for fr in quants:
                opts.append((ai, i, j, fr * a.q_max))
        menus.append(opts)
    return menus


def beam_search(g, actors, coalition, init: State, mode, depth, width, quants,
                objective, delta=3.0, chi=1.0, lam_L=0.1, lam_F=1.0, max_joint=4000):
    """Deterministic beam search over `depth` ticks. `objective(state, src)` -> float
    (higher = better); beam keeps the top `width`. Returns (beams, explored).
    Each beam is (State, score, history_of_action_lists)."""
    src = source_cells(g)
    beams = [(init.copy(), objective(init, src), [])]
    explored = 0
    for _t in range(depth):
        cand = []
        for (st, _sc, hist) in beams:
            menus = action_menu(g, actors, coalition, st.x, quants)
            n_joint = 1
            for mm in menus:
                n_joint *= len(mm)
            combos = product(*menus)
            for k, combo in enumerate(combos):
                if k >= max_joint:
                    break
                acts = [a for a in combo if a is not None]
                ns, _rec = forced_tick(g, actors, st, acts, mode, delta, chi, lam_L, lam_F)
                explored += 1
                cand.append((ns, objective(ns, src), hist + [acts]))
        cand.sort(key=lambda c: -c[1])
        beams = cand[:width]
    return beams, explored


def coalition_net(state: State, coalition):
    return sum(state.bal[a] for a in coalition)


def baseline_BR_schedule(g, actors, init: State, ticks, mode="guarded",
                         delta=3.0, chi=1.0, lam_L=0.1, lam_F=1.0):
    """Paired NO-ACTION baseline: the coalition rests every tick (natural dynamics
    only). Returns the per-tick threshold-aware burden B_R - the reference for harm."""
    R = reserve_R(g, delta)
    s = init.copy()
    sched = []
    for _ in range(ticks):
        s, _ = forced_tick(g, actors, s, [], mode, delta, chi, lam_L, lam_F)
        sched.append(b_R(g, s.x, R, chi))
    return sched, s


def redteam_search(g, actors, coalition, init: State, mode, depth, width, quants,
                   base_BR, delta=3.0, chi=1.0, lam_L=0.1, lam_F=1.0, max_joint=4000,
                   min_net=0.5):
    """Search specifically for PROFITABLE HARM: maximise cumulative
    (B_R_attack - B_R_noaction) while requiring coalition net EBU >= min_net (states
    below that are heavily penalised, so the search is pushed toward harm that is also
    profitable). Returns beams of (state, score, cum_harm, history)."""
    R = reserve_R(g, delta)
    beams = [(init.copy(), 0.0, 0.0, [])]         # (state, score, cum_harm, hist)
    explored = 0
    BIG = 1e6
    for t in range(depth):
        cand = []
        for (st, _sc, harm, hist) in beams:
            menus = action_menu(g, actors, coalition, st.x, quants)
            for k, combo in enumerate(product(*menus)):
                if k >= max_joint:
                    break
                acts = [a for a in combo if a is not None]
                ns, _rec = forced_tick(g, actors, st, acts, mode, delta, chi, lam_L, lam_F)
                explored += 1
                h = harm + (b_R(g, ns.x, R, chi) - base_BR[t])
                net = coalition_net(ns, coalition)
                score = h + 1e-3 * net + BIG * min(0.0, net - min_net)
                cand.append((ns, score, h, hist + [acts]))
        cand.sort(key=lambda c: -c[1])
        beams = cand[:width]
    return beams, explored


def find_exploit(g, actors, coalition, beams, mode, base_BR_tail, tail,
                 delta=3.0, chi=1.0, lam_L=0.1, lam_F=1.0, margin=1.0):
    """Scan every state in the final beam; run a no-action persistence tail on each and
    return the strongest qualifying exploit (positive net EBU AND persistent harm), or
    the best non-qualifying verdict for reporting. Deterministic."""
    best = None
    best_nonexploit = None
    for (st, _sc, _h, hist) in beams:
        net = coalition_net(st, coalition)
        atail, _ = persistence_tail(g, actors, st, mode, tail, delta, chi, lam_L, lam_F)
        v = classify_exploit(net, atail, base_BR_tail, margin)
        v.detail["history"] = hist
        if v.is_exploit and (best is None or v.net_ebu > best.net_ebu):
            best = v
        if best_nonexploit is None or v.harm_margin > best_nonexploit.harm_margin:
            best_nonexploit = v
    return best if best is not None else best_nonexploit


# ---------------------------------------------------------------- exploit predicate
@dataclass
class ExploitVerdict:
    is_exploit: bool
    net_ebu: float
    harm_persistent: bool
    harm_margin: float
    detail: dict = field(default_factory=dict)


def persistence_tail(g, actors, st: State, mode, tail, delta, chi, lam_L, lam_F):
    """Let the world relax with attackers RESTING for `tail` ticks (natural dynamics
    only). Returns the per-tick B_R (physical) during the tail."""
    R = reserve_R(g, delta)
    s = st.copy()
    bR = []
    for _ in range(tail):
        s, _ = forced_tick(g, actors, s, [], mode, delta, chi, lam_L, lam_F)
        bR.append(b_R(g, s.x, R, chi))
    return bR, s


def classify_exploit(net_ebu, attack_tail_BR, base_tail_BR, margin=1.0):
    """An exploit requires (1) positive net EBU AND (2) persistent physical harm:
    the attack's threshold-aware burden exceeds the paired baseline's at EVERY tail
    tick by at least `margin` (persistent, not a one-tick blip). Harm is measured on a
    physical variable (B_R), never on EBU."""
    persistent = (len(attack_tail_BR) == len(base_tail_BR) and len(attack_tail_BR) > 0
                  and all(a > b + margin for a, b in zip(attack_tail_BR, base_tail_BR)))
    mean_margin = (sum(attack_tail_BR) - sum(base_tail_BR)) / max(1, len(attack_tail_BR))
    return ExploitVerdict(
        is_exploit=(net_ebu > 1e-6 and persistent),
        net_ebu=net_ebu, harm_persistent=persistent, harm_margin=mean_margin,
        detail=dict(attack_tail_BR=attack_tail_BR, base_tail_BR=base_tail_BR))
