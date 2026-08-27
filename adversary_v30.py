"""
Energy Balance - V3.0 Gate 1C: adversarial replay harness for the local signed
EBU quote (preregistered group Q22 of v30_quote_validation_plan.json,
canonical hash a1916e8ecf366cee93a5284a0d8fcb68a3e1a429f49ce62b9f5914df87f94061).

CENTRAL QUESTION
    Can an automated actor or coalition maximize the exact local signed EBU
    quote, while every action remains subject to P1C, and nevertheless produce
    persistent physical harm?

A profitable persistent-harm exploit requires BOTH positive cumulative signed
EBU AND persistent physical harm under the registered physical predicate.
Positive EBU alone is not an exploit; harm with negative EBU is not a
profitable exploit. "No exploit found" means ONLY: no exploit was found within
the declared fixtures, seeds, action menu, search depth, width, and predicate.
It is NEVER a security proof.

SCOPE
  * Reuses ebu_quote_v30 for every V3.0 quote and settlement, and p1c_v29 for
    every physical permission decision. Neither is forked or modified.
  * Implements NO wallet, health, needs, market, price, transfer, actor
    survival, or behavioral learning. Cumulative signed EBU is an EVALUATION
    variable of this gate, not a wallet.
  * The production-local actor (arm C) reads only permitted local information.
    The red-team oracle is a SEPARATELY LABELLED testing device that may use
    global harm as its external search objective; its results are reported
    separately and never presented as information available to a production
    actor.

DERIVED SEMANTICS AND THEIR PROVENANCE (nothing invented; see GATE1C_SEMANTICS)
Every constant below is either named in the locked plan's Q22 spec or taken
verbatim from the released V2.6 machinery (exp_v26.py / results/v2.6/MANIFEST.md)
that the plan instructs us to replay.

Run with the project venv (the released exp_v26 layout generator imports
matplotlib, exactly as test_v25.py / test_v26.py already do).
"""
from __future__ import annotations
import math
from dataclasses import dataclass, field, replace
from typing import Optional

import d0_v29 as d0
import p1c_v29 as p1c
import ebu_quote_v30 as eq

__all__ = [
    "GATE1C_SEMANTICS", "DEPTH", "WIDTH", "TAIL", "QUANTS", "COALITION",
    "LAYOUT_SEEDS", "H_RUN", "MARGIN", "DELTA", "CHI", "A_THRESH", "DT",
    "RunState", "RunMetrics", "translate_layout", "layout_signature",
    "physical_metrics", "no_action_baseline",
    "arm_a_p1c", "arm_b_observational", "arm_c_quote_greedy",
    "redteam_oracle", "classify_profitable_harm", "certified_dt",
]

# ---------------------------------------------------------------------------
# Frozen constants. "plan" = named in the locked Q22 spec; "v2.6" = released
# exp_v26.py / results/v2.6/MANIFEST.md (the machinery Q22 instructs us to
# replay); "tick-fidelity" = forced by replaying V2.6's unit ticks.
# ---------------------------------------------------------------------------
DEPTH = 10                      # plan
WIDTH = 40                      # plan
TAIL = 20                       # plan
QUANTS = (0.5, 1.0)             # plan
COALITION = (0, 1)              # plan
LAYOUT_SEEDS = tuple(range(12))  # plan (0..11, incl. the seed-0 falsifier)
H_RUN = DEPTH * 3               # v2.6 (exp_v26.H_RUN = DEPTH*3 = 30)
MARGIN = 1.0                    # v2.6 (exp_v26.MARGIN, persistence margin)
DELTA = 3.0                     # v2.6 (exp_v26.DELTA; R_eff = A + DELTA = 11)
CHI = 1.0                       # v2.6 (exp_v26.CHI, reserve penalty weight)
LAM_L = 0.1                     # v2.6 (exp_v26.LAM_L, transport-loss debit)
A_THRESH = 8.0                  # v2.6 (exp_v26.A_THRESH)
GRID_N = 5                      # v2.6 (random_allee_world n=5)
SRC_FRAC = 0.4                  # v2.6 (random_allee_world src_frac=0.4)
ACT_QMAX = 3.0                  # v2.6 (random_allee_world Actor q_max)
ACT_M = 0.6                     # v2.6 (Actor M)
ACT_THETA = 0.05                # v2.6 (Actor theta)
ACT_ETA = 0.95                  # v2.6 (Actor eta)
DT = 1.0                        # tick-fidelity: V2.6 advances in unit ticks
EPS_X = 0.0                     # exact-model conformance (P1C docstring); no
EPS_U = 0.0                     # empirical margin is fitted in this gate
DOMAIN_TOL = 1e-9

GATE1C_SEMANTICS = {
    "plan_named": {"DEPTH": DEPTH, "WIDTH": WIDTH, "TAIL": TAIL,
                   "QUANTS": list(QUANTS), "COALITION": list(COALITION),
                   "LAYOUT_SEEDS": list(LAYOUT_SEEDS),
                   "arms": ["A: P1C alone",
                            "B: P1C + observational exact quote",
                            "C: exact-quote-maximizing adversary"]},
    "v2.6_machinery": {"H_RUN": H_RUN, "MARGIN": MARGIN, "DELTA": DELTA,
                       "CHI": CHI, "LAM_L": LAM_L, "A_THRESH": A_THRESH,
                       "GRID_N": GRID_N, "SRC_FRAC": SRC_FRAC,
                       "ACT_QMAX": ACT_QMAX, "ACT_M": ACT_M,
                       "ACT_THETA": ACT_THETA, "ACT_ETA": ACT_ETA},
    "tick_fidelity": {"DT": DT,
                      "note": "V2.6 advances in unit ticks; dt is not a free "
                              "parameter here. r_dt vs the V2.8 one-edge "
                              "certificate is REPORTED per layout, never "
                              "chosen to suit the outcome."},
    "translation": {
        "note": "Grid -> d0.World is a mechanical parameter-for-parameter map "
                "of random_allee_world; no value is chosen for convenience.",
        "cells": "alpha=1.0, beta=0.3, L=4, U=16, K=20 (v2.6); chi=CHI and "
                 "R=A+DELTA=11 on Allee sources, chi=0/R=0 elsewhere; "
                 "d=0.0 sources / 0.4 consumers; kappa=leak_frac=0.01; "
                 "rho=0.35 and A=8 on sources; x0=15 sources / 6 consumers",
        "edges": "both directions of every von Neumann adjacency, with "
                 "M=0.6, theta=0.05, eta=0.95 (v2.6 Actor parameters)",
        "p1c_types": "Allee sources -> 'regenerative' with R_eff=11; "
                     "non-regenerating cells -> 'finite' (P1C gives a finite "
                     "stock a ZERO preservation-safe export budget). This is "
                     "a determined consequence of P1C typing, not a choice.",
        "eps": {"eps_x": EPS_X, "eps_u": EPS_U},
    },
    "predicate": "V2.6 classify_exploit semantics, physical variables only: "
                 "persistent harm = attack tail burden exceeds the PAIRED "
                 "no-action baseline tail burden by >= MARGIN at EVERY tail "
                 "tick; exploit = cumulative signed EBU > 1e-6 AND persistent "
                 "harm. Harm is never measured on EBU.",
}


# ---------------------------------------------------------------------------
# layout translation (released V2.6 generator -> d0/P1C objects)
# ---------------------------------------------------------------------------
def translate_layout(seed: int):
    """Deterministically map the released exp_v26.random_allee_world(seed)
    layout onto (world, x0, configs, is_src). Imported lazily so that modules
    needing no layout do not pull matplotlib."""
    import exp_v26                                  # released, unmodified
    g, _actors, _src, is_src = exp_v26.random_allee_world(
        seed, n=GRID_N, src_frac=SRC_FRAC)
    size = GRID_N * GRID_N
    cells = []
    for i in range(size):
        src = bool(is_src[i])
        cells.append(d0.Cell(
            alpha=g.alpha[i], beta=g.beta[i], chi=(CHI if src else 0.0),
            L=g.L[i], U=g.U[i], R=((A_THRESH + DELTA) if src else 0.0),
            K=g.K[i], s=g.s[i], d=g.d[i], lam=g.lam[i],
            kappa=g.leak_frac[i], source=("allee" if src else "none"),
            rho=g.rho[i], A=(A_THRESH if src else 0.0)))
    edges = []
    for i in range(size):
        for j in g.neighbors(i):
            edges.append(d0.Edge(i=i, j=j, M=ACT_M, theta=ACT_THETA,
                                 eta=ACT_ETA))
    world = d0.World(cells=tuple(cells), edges=tuple(edges))
    configs = {}
    for i in range(size):
        if is_src[i]:
            configs[i] = p1c.SourceConfig(source_id=i,
                                          source_type="regenerative",
                                          R_eff=A_THRESH + DELTA,
                                          eps_x=EPS_X, eps_u=EPS_U)
        else:
            configs[i] = p1c.SourceConfig(source_id=i, source_type="finite",
                                          R_eff=0.0, eps_x=EPS_X, eps_u=EPS_U)
    return world, tuple(g.x), configs, tuple(bool(v) for v in is_src)


def layout_signature(is_src) -> str:
    """Deterministic layout signature (distinctness / registered-hash check)."""
    return eq.commitment_hash({"kind": "v26_layout_mask",
                               "mask": [1 if v else 0 for v in is_src]})


def certified_dt(world: d0.World) -> float:
    """V2.8 one-edge sufficient step certificate, minimised over edges
    (designer diagnostic; never an actor input, never used to pick DT)."""
    lv = d0.lv_exact(world)
    return min(d0.one_edge_dt_certificate(e, lv) for e in world.edges)


# ---------------------------------------------------------------------------
# search / run state (physical field kept strictly apart from EBU evaluation)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class RunState:
    """One search/run state. Physical field and EBU evaluation variables are
    separate fields; EBU is NOT a wallet and never feeds a decision."""
    x: tuple                              # physical field
    ebu_total: float = 0.0                # cumulative signed EBU (evaluation)
    ebu_positive: float = 0.0             # cumulative positive issuance
    ebu_negative: float = 0.0             # cumulative negative debit
    ebu_by_actor: tuple = ()              # per-source-cell cumulative signed EBU
    actions: int = 0                      # settled actions
    q_req_total: float = 0.0
    q_acc_total: float = 0.0
    q_settled_total: float = 0.0
    loss_total: float = 0.0               # physical transport loss
    overuse: float = 0.0                  # aggregate export beyond P1C budget
    served: float = 0.0                   # delivered service (post-loss)
    unmet: float = 0.0                    # requested-but-undelivered demand
    reserve_crossings: int = 0
    allee_crossings: int = 0
    unquotable_multi_edge: int = 0        # accepted flows the first-model
                                          # production rule forbids quoting
    violations: int = 0
    duplicate_attempts: int = 0
    domain_exit_tick: Optional[int] = None
    history: tuple = ()                   # (tick, source, dest, q_acc, quote)

    def with_field(self, x, **kw):
        return replace(self, x=tuple(x), **kw)


@dataclass
class RunMetrics:
    run_id: str = ""
    arm: str = ""
    seed: int = 0
    data: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# physical metrics (harness evaluation only; never a decision input)
# ---------------------------------------------------------------------------
def _regen_only(c: d0.Cell, x: float) -> float:
    """g(x) alone, via the public natural_drive on a stripped copy."""
    bare = d0.Cell(alpha=c.alpha, beta=c.beta, chi=c.chi, L=c.L, U=c.U,
                   R=c.R, K=c.K, source=c.source, rho=c.rho, A=c.A)
    return d0.natural_drive(bare, x)


def physical_metrics(world: d0.World, x, is_src) -> dict:
    burden = d0.V_total(world, x)
    n = world.n
    viable = 100.0 * sum(1 for i in range(n) if x[i] >= world.cells[i].L) / n
    below_R = sum(1 for i in range(n) if is_src[i] and x[i] < world.cells[i].R)
    below_A = sum(1 for i in range(n) if is_src[i] and x[i] < world.cells[i].A)
    dead = sum(1 for i in range(n) if is_src[i] and x[i] < world.cells[i].A
               and _regen_only(world.cells[i], x[i]) <= 0.0)
    src_stock = math.fsum(x[i] for i in range(n) if is_src[i])
    return dict(burden=burden, viable=viable, below_R=below_R, below_A=below_A,
                dead=dead, source_stock=src_stock, total_stock=math.fsum(x))


def _domain_exit(world: d0.World, x) -> bool:
    return any(x[i] < -DOMAIN_TOL or x[i] > world.cells[i].K + DOMAIN_TOL
               for i in range(world.n))


# ---------------------------------------------------------------------------
# paired no-action baseline (attackers rest; natural dynamics only)
# ---------------------------------------------------------------------------
def no_action_baseline(world: d0.World, x0, configs, is_src, ticks: int):
    """Burden schedule with NO transport at all (every actor rests). Returns
    (burden_schedule, final_x, domain_exit_tick)."""
    empty = d0.World(cells=world.cells, edges=())
    x = tuple(x0)
    sched, exit_tick = [], None
    for t in range(1, ticks + 1):
        x = p1c.p1c_step(empty, x, DT, {}).x_after
        sched.append(d0.V_total(world, x))
        if exit_tick is None and _domain_exit(world, x):
            exit_tick = t
    return sched, x, exit_tick


# ---------------------------------------------------------------------------
# per-tick accounting shared by the arms
# ---------------------------------------------------------------------------
def _tick_physical_accounting(world, xb, tick_result, st, tick, is_src):
    """Accumulate physical metrics for one executed P1C tick."""
    served = math.fsum(er.q_delivered for er in tick_result.edges) * DT
    loss = tick_result.total_loss
    demand = math.fsum(c.d for c in world.cells) * DT
    unmet = max(0.0, demand - served)
    overuse = 0.0
    for sr in tick_result.sources:
        overuse += max(0.0, sr.Q_acc - sr.Q_max)
    xa = tick_result.x_after
    rc = sum(1 for i in range(world.n)
             if is_src[i] and xa[i] < world.cells[i].R <= xb[i])
    ac = sum(1 for i in range(world.n)
             if is_src[i] and xa[i] < world.cells[i].A <= xb[i])
    return dict(served=served, loss=loss, unmet=unmet, overuse=overuse * DT,
                reserve_crossings=rc, allee_crossings=ac)


def _accumulate(st: RunState, xa, acc, tick, world, extra_actions=0,
                ebu=0.0, ebu_pos=0.0, ebu_neg=0.0, by_actor=None,
                q_req=0.0, q_acc=0.0, q_settled=0.0, unquotable=0,
                violations=0, dups=0, history=()) -> RunState:
    exit_tick = st.domain_exit_tick
    if exit_tick is None and _domain_exit(world, xa):
        exit_tick = tick
    by = list(st.ebu_by_actor) if st.ebu_by_actor else [0.0] * world.n
    if by_actor:
        for k, v in by_actor.items():
            by[k] += v
    return replace(
        st, x=tuple(xa),
        ebu_total=st.ebu_total + ebu,
        ebu_positive=st.ebu_positive + ebu_pos,
        ebu_negative=st.ebu_negative + ebu_neg,
        ebu_by_actor=tuple(by),
        actions=st.actions + extra_actions,
        q_req_total=st.q_req_total + q_req,
        q_acc_total=st.q_acc_total + q_acc,
        q_settled_total=st.q_settled_total + q_settled,
        loss_total=st.loss_total + acc["loss"],
        overuse=st.overuse + acc["overuse"],
        served=st.served + acc["served"],
        unmet=st.unmet + acc["unmet"],
        reserve_crossings=st.reserve_crossings + acc["reserve_crossings"],
        allee_crossings=st.allee_crossings + acc["allee_crossings"],
        unquotable_multi_edge=st.unquotable_multi_edge + unquotable,
        violations=st.violations + violations,
        duplicate_attempts=st.duplicate_attempts + dups,
        domain_exit_tick=exit_tick,
        history=st.history + tuple(history))


# ---------------------------------------------------------------------------
# ARM A - P1C physical baseline (no EBU-guided selection, no quoting)
# ---------------------------------------------------------------------------
def arm_a_p1c(world, x0, configs, is_src, ticks: int, st: RunState = None):
    st = st or RunState(x=tuple(x0))
    for t in range(1, ticks + 1):
        xb = st.x
        tr = p1c.p1c_step(world, xb, DT, configs)
        acc = _tick_physical_accounting(world, xb, tr, st, t, is_src)
        n_act = sum(1 for er in tr.edges if er.q_acc > 0.0)
        st = _accumulate(st, tr.x_after, acc, t, world, extra_actions=n_act,
                         q_req=math.fsum(er.q_req for er in tr.edges),
                         q_acc=math.fsum(er.q_acc for er in tr.edges))
    return st


# ---------------------------------------------------------------------------
# ARM B - P1C + observational exact quote (physically identical to A)
# ---------------------------------------------------------------------------
def _quote_edge(world, x, tr, edge_idx, tick, pass_id, cost):
    e = world.edges[edge_idx]
    er = tr.edges[edge_idx]
    inp = eq.LocalQuoteInput(
        src=d0.local_view(world.cells[e.i], x[e.i]),
        dst=d0.local_view(world.cells[e.j], x[e.j]),
        u_src=tr.u[e.i], u_dst=tr.u[e.j], dt=tr.dt, eta=e.eta,
        q_req=er.q_req, q_acc=er.q_acc,
        source_id=e.i, dest_id=e.j, config_id=f"cfg:{e.i}:R{world.cells[e.i].R}")
    return eq.build_quote(inp, cost, pass_id, tick, 0)


def _process_cost(eta: float) -> eq.ProcessCost:
    """Declared action-process cost: the dissipated stock priced as process
    burden (category 2 of Def 6.4; lam_L is the released V2.6 weight). No
    state-carried term is included (no-double-count condition)."""
    return eq.ProcessCost(category=eq.ALLOWED_COST_CATEGORY,
                          c1=LAM_L * DT * (1.0 - eta))


def arm_b_observational(world, x0, configs, is_src, ticks: int,
                        st: RunState = None):
    """Same accepted physical actions as arm A; each quoted and settled
    observationally. Sources with more than one accepted out-edge in a tick
    are NOT independently quoted (that is exactly the Q13 phantom-credit
    error); such accepted flows are counted in `unquotable_multi_edge`."""
    st = st or RunState(x=tuple(x0))
    for t in range(1, ticks + 1):
        xb = st.x
        tr = p1c.p1c_step(world, xb, DT, configs)
        acc = _tick_physical_accounting(world, xb, tr, st, t, is_src)
        by_src: dict = {}
        for idx, er in enumerate(tr.edges):
            if er.q_acc > 0.0:
                by_src.setdefault(er.source_id, []).append(idx)
        reg = eq.EpochRegistry()
        ebu = pos = neg = 0.0
        by_actor: dict = {}
        n_act = unq = viol = 0
        hist = []
        for sid, idxs in sorted(by_src.items()):
            if len(idxs) != 1:
                unq += len(idxs)
                continue
            idx = idxs[0]
            cost = _process_cost(world.edges[idx].eta)
            s = _quote_edge(world, xb, tr, idx, t, f"p1c-A-{t}", cost)
            reg.register(s)
            r = reg.settle(s, tr.edges[idx].q_acc, t, 0)
            if r.status == "settled":
                ebu += r.issued
                pos += max(0.0, r.issued)
                neg += max(0.0, -r.issued)
                by_actor[sid] = by_actor.get(sid, 0.0) + r.issued
                n_act += 1
                hist.append((t, sid, tr.edges[idx].dest_id,
                             tr.edges[idx].q_acc, r.issued))
            else:
                viol += 1
        st = _accumulate(st, tr.x_after, acc, t, world, extra_actions=n_act,
                         ebu=ebu, ebu_pos=pos, ebu_neg=neg, by_actor=by_actor,
                         q_req=math.fsum(er.q_req for er in tr.edges),
                         q_acc=math.fsum(er.q_acc for er in tr.edges),
                         q_settled=math.fsum(h[3] for h in hist),
                         unquotable=unq, violations=viol, history=hist)
    return st


# ---------------------------------------------------------------------------
# ARM C - production-local exact-quote-maximizing adversary
# ---------------------------------------------------------------------------
def _candidate_menu(world, x, u, sid, configs):
    """Source-local candidate menu for cell `sid`: for each of its own
    out-edges and each registered quantity fraction, the locally computable
    (edge_idx, q_req, q_acc). Reads ONLY the source's own frozen data, its
    permitted adjacent destination views, its own P1C configuration, and the
    edge constants. No global object, no rollout."""
    cfg = configs[sid]
    state = p1c.classify_state(cfg, x[sid], u[sid], DT)
    if state != "P" or cfg.source_type != "regenerative":
        return state, 0.0, []
    budget = p1c.robust_budget(cfg, x[sid], u[sid], DT)
    out = []
    for idx, e in enumerate(world.edges):
        if e.i != sid:
            continue
        _f, J = d0.edge_flux(d0.local_view(world.cells[e.i], x[e.i]),
                             d0.local_view(world.cells[e.j], x[e.j]), e)
        if J <= 0.0:
            continue
        for frac in QUANTS:
            q_req = min(frac * J, ACT_QMAX)
            if q_req <= 0.0:
                continue
            q_acc = min(q_req, budget)          # P1C sigma for a single edge
            if q_acc <= 0.0:
                continue
            out.append((idx, q_req, q_acc))
    return state, budget, out


def arm_c_quote_greedy(world, x0, configs, is_src, ticks: int,
                       st: RunState = None, coalition=None):
    """Each configured source independently proposes the ONE action from its
    own permitted menu whose committed exact quote at q_acc is largest
    (redesign loop of foundation §5 event 6). Selected proposals are then
    executed by the real P1C on the restricted edge set, so P1C - not this
    module - remains the physical authority."""
    st = st or RunState(x=tuple(x0))
    members = set(range(world.n) if coalition is None else coalition)
    for t in range(1, ticks + 1):
        xb = st.x
        u = tuple(d0.natural_drive(c, xb[k]) for k, c in enumerate(world.cells))
        chosen: dict = {}
        for sid in sorted(configs):
            if sid not in members:
                continue
            _state, _b, menu = _candidate_menu(world, xb, u, sid, configs)
            best = None
            for (idx, q_req, q_acc) in menu:
                e = world.edges[idx]
                cost = _process_cost(e.eta)
                inp = eq.LocalQuoteInput(
                    src=d0.local_view(world.cells[e.i], xb[e.i]),
                    dst=d0.local_view(world.cells[e.j], xb[e.j]),
                    u_src=u[e.i], u_dst=u[e.j], dt=DT, eta=e.eta,
                    q_req=q_req, q_acc=q_acc, source_id=e.i, dest_id=e.j,
                    config_id=f"cfg:{e.i}:R{world.cells[e.i].R}")
                cand = eq.build_quote(inp, cost, f"cand-{t}-{sid}", t, 0)
                val = cand.exact(q_acc)
                if best is None or val > best[0]:
                    best = (val, idx, q_req, q_acc)
            if best is not None and best[0] > 0.0:      # accept only if it pays
                chosen[sid] = best
        # execute the selected single action per source via the real P1C
        sel = sorted(v[1] for v in chosen.values())
        sub = d0.World(cells=world.cells,
                       edges=tuple(world.edges[i] for i in sel))
        tr = p1c.p1c_step(sub, xb, DT, configs)
        acc = _tick_physical_accounting(sub, xb, tr, st, t, is_src)
        reg = eq.EpochRegistry()
        ebu = pos = neg = 0.0
        by_actor: dict = {}
        n_act = viol = 0
        hist = []
        q_req_tot = q_acc_tot = 0.0
        for k, e in enumerate(sub.edges):
            er = tr.edges[k]
            if er.q_acc <= 0.0:
                continue
            cost = _process_cost(e.eta)
            s = _quote_edge(sub, xb, tr, k, t, f"pass-{t}", cost)
            reg.register(s)
            r = reg.settle(s, er.q_acc, t, 0)
            q_req_tot += er.q_req
            q_acc_tot += er.q_acc
            if r.status == "settled":
                ebu += r.issued
                pos += max(0.0, r.issued)
                neg += max(0.0, -r.issued)
                by_actor[e.i] = by_actor.get(e.i, 0.0) + r.issued
                n_act += 1
                hist.append((t, e.i, e.j, er.q_acc, r.issued))
            else:
                viol += 1
        st = _accumulate(st, tr.x_after, acc, t, world, extra_actions=n_act,
                         ebu=ebu, ebu_pos=pos, ebu_neg=neg, by_actor=by_actor,
                         q_req=q_req_tot, q_acc=q_acc_tot,
                         q_settled=q_acc_tot, violations=viol, history=hist)
    return st


# ---------------------------------------------------------------------------
# RED-TEAM ORACLE - separately labelled testing device.
# Uses global harm as an EXTERNAL search objective. This information is NOT
# available to any production actor (arm C); results are reported separately
# and must never be relabelled as production behavior.
# ---------------------------------------------------------------------------
def redteam_oracle(world, x0, configs, is_src, depth: int, width: int,
                   baseline_burden, min_net: float = 0.5):
    """Beam search over per-tick single-action-per-source selections that
    maximizes cumulative harm (attack burden minus the paired no-action
    baseline) while requiring positive cumulative EBU. Returns
    (beams, explored)."""
    BIG = 1e6
    beams = [(RunState(x=tuple(x0)), 0.0, 0.0)]     # (state, score, cum_harm)
    explored = 0
    for t in range(1, depth + 1):
        cand = []
        for (st, _sc, harm) in beams:
            xb = st.x
            u = tuple(d0.natural_drive(c, xb[k])
                      for k, c in enumerate(world.cells))
            # per-source menus (production-local objects); the ORACLE chooses
            # the combination, which is what makes it an oracle.
            menus = {}
            for sid in sorted(configs):
                _s, _b, m = _candidate_menu(world, xb, u, sid, configs)
                if m:
                    menus[sid] = m
            options = [None]
            for sid, m in menus.items():
                for (idx, q_req, q_acc) in m:
                    options.append((sid, idx, q_req, q_acc))
            for opt in options:
                sel = [] if opt is None else [opt[1]]
                sub = d0.World(cells=world.cells,
                               edges=tuple(world.edges[i] for i in sel))
                tr = p1c.p1c_step(sub, xb, DT, configs)
                acc = _tick_physical_accounting(sub, xb, tr, st, t, is_src)
                reg = eq.EpochRegistry()
                ebu = pos = neg = 0.0
                n_act = 0
                hist = []
                by_actor = {}
                for k, e in enumerate(sub.edges):
                    er = tr.edges[k]
                    if er.q_acc <= 0.0:
                        continue
                    s = _quote_edge(sub, xb, tr, k, t, f"oracle-{t}",
                                    _process_cost(e.eta))
                    reg.register(s)
                    r = reg.settle(s, er.q_acc, t, 0)
                    if r.status == "settled":
                        ebu += r.issued
                        pos += max(0.0, r.issued)
                        neg += max(0.0, -r.issued)
                        by_actor[e.i] = by_actor.get(e.i, 0.0) + r.issued
                        n_act += 1
                        hist.append((t, e.i, e.j, er.q_acc, r.issued))
                ns = _accumulate(st, tr.x_after, acc, t, world,
                                 extra_actions=n_act, ebu=ebu, ebu_pos=pos,
                                 ebu_neg=neg, by_actor=by_actor,
                                 q_req=math.fsum(er.q_req for er in tr.edges),
                                 q_acc=math.fsum(er.q_acc for er in tr.edges),
                                 q_settled=math.fsum(er.q_acc for er in tr.edges),
                                 history=hist)
                explored += 1
                h = harm + (d0.V_total(world, ns.x) - baseline_burden[t - 1])
                score = h + 1e-3 * ns.ebu_total + BIG * min(0.0, ns.ebu_total - min_net)
                cand.append((ns, score, h))
        cand.sort(key=lambda c: -c[1])
        beams = cand[:width]
    return beams, explored


# ---------------------------------------------------------------------------
# exploit predicate (physical variables only; V2.6 classify_exploit semantics)
# ---------------------------------------------------------------------------
def classify_profitable_harm(ebu_total: float, attack_tail_burden,
                            base_tail_burden, margin: float = MARGIN) -> dict:
    """persistent harm = attack tail burden exceeds the paired baseline by at
    least `margin` at EVERY tail tick (never a one-tick blip). exploit =
    positive cumulative signed EBU AND persistent harm. Harm is measured on a
    physical variable; EBU never enters the harm test."""
    n = len(attack_tail_burden)
    persistent = (n > 0 and n == len(base_tail_burden)
                  and all(a > b + margin
                          for a, b in zip(attack_tail_burden, base_tail_burden)))
    mean_margin = ((math.fsum(attack_tail_burden) - math.fsum(base_tail_burden))
                   / max(1, n))
    profitable = ebu_total > 1e-6
    return dict(profitable=profitable, harm_persistent=persistent,
                mean_tail_harm=mean_margin,
                first_tail_gap=(attack_tail_burden[0] - base_tail_burden[0]
                                if n else None),
                is_exploit=bool(profitable and persistent))
