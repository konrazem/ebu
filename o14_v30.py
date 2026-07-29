"""
V3.0 Gate 1D-B / O14 implementation of the preregistered multi-out-edge
capability study (plan v30_o14_multi_edge_plan.json, canonical hash below).

THIS MODULE IS A LIBRARY. Importing it runs no experiment, writes no file and
mutates no repository state; it only loads and fail-closed-validates the
locked plan (read-only). The official runner (exp_v30_o14.py) does NOT exist
yet and requires separate authorization; nothing here executes the registered
60-run study.

STRUCTURE (the split is load-bearing for the information boundary):
  1. plan loading / hash lock / schema validation
  2. world + certificate reconstruction (designer side)
  3. DECISION PATH - candidate menu, quote schedules, arm selection rules.
     These functions read ONLY: the source's frozen local stock and declared
     parameters, the authoritative P1C classification and budget, adjacent
     destination LocalViews, edge constants, declared process cost, candidate
     quantities, the committed quote schedule, and deterministic identifiers.
     They never read global V, whole-world service, future states, results,
     wallets, health or prices (asserted by AST + runtime poison in
     test_v30_o14.py).
  4. EVALUATION LAYER - bounded-service tick execution, ledgers, settlement
     records, the settlement-free arm-A group-quote diagnostic, run assembly
     and the Gate 1D predicates/classification (reused VERBATIM from
     service_v30). Physically separate from the selection path.

Reused released modules, unmodified: d0_v29 (local physics, certificates),
p1c_v29 (preservation allocation - the AUTHORITY on budgets), ebu_quote_v30
(exact signed quote), service_v30 (bounded service semantics, Gate 1D-A
corrected reserve tolerance, Gate 1D predicates and outcome precedence).

EPISTEMIC STATUS: numerical validation is never proof. The exact-total-quote
greedy rule is a candidate heuristic, not a theorem. The bounded wrapper is
outside the V2.8 theorem (O13). O3 (aggregate multi-edge settlement) remains
open: NO aggregate settlement exists here. Gate 1E and Gate 2 remain paused.

Standard library only; never imports a test module or a runner.
"""
from __future__ import annotations
import hashlib
import json
import math
from typing import Mapping, Optional, Sequence

import d0_v29 as d0
import p1c_v29 as p1c
import ebu_quote_v30 as eq
import service_v30 as sv

__all__ = [
    "PLAN_PATH", "PLAN_CANONICAL", "PLAN_RAW", "PLAN",
    "EXEC_ARMS", "DT_LABELS", "FRACTIONS", "LAM_L", "C0",
    "load_plan", "plan_canonical_hash", "validate_plan",
    "build_world", "world_certificates", "world_dts",
    "screen_budget", "candidate_menu", "quote_schedule_for",
    "continuous_vertex_diagnostic",
    "select_arm_B", "select_arm_D", "select_arm_S",
    "DECISION_PATH_FUNCS",
    "shaped_active_world", "o14_tick", "run_arm",
    "group_quote_diagnostic",
    "build_run_specs", "run_id",
    "METRIC_FIELDS", "strict_json_dumps",
]

# ---------------------------------------------------------------------------
# 1. plan loading, hash lock, schema validation (fail closed everywhere)
# ---------------------------------------------------------------------------
PLAN_PATH = "v30_o14_multi_edge_plan.json"
PLAN_CANONICAL = ("2524ba268db004969e04f9c8636cc240b643f0f7"
                  "685507edf65350ea98a37745")
PLAN_RAW = ("00c4dd472eb332e57865f845e41265032fa69ef3"
            "535bb170a8ade013f783d22a")


def _reject_nonfinite(name):
    raise ValueError(f"non-finite JSON constant {name!r} rejected (strict)")


def plan_canonical_hash(plan: dict) -> str:
    """Committed V2.9/V3.0 convention: sorted-keys compact JSON, SHA-256."""
    canon = json.dumps(plan, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True, allow_nan=False)
    return hashlib.sha256(canon.encode()).hexdigest()


def load_plan(path: str = PLAN_PATH,
              expected_canonical: str = PLAN_CANONICAL,
              expected_raw: Optional[str] = PLAN_RAW) -> dict:
    """Strict load + fail-closed hash lock. No NaN/Infinity anywhere."""
    with open(path, "rb") as f:
        raw = f.read()
    if expected_raw is not None:
        rh = hashlib.sha256(raw).hexdigest()
        if rh != expected_raw:
            raise SystemExit(f"FATAL: raw O14 plan SHA-256 mismatch: {rh}")
    plan = json.loads(raw.decode("utf-8"), parse_constant=_reject_nonfinite)
    ch = plan_canonical_hash(plan)
    if ch != expected_canonical:
        raise SystemExit(f"FATAL: canonical O14 plan hash mismatch: {ch}")
    return plan


def _need(container, key, kind=None, ctx=""):
    if key not in container:
        raise ValueError(f"plan schema: missing {ctx}{key!r}")
    v = container[key]
    if kind is not None and not isinstance(v, kind):
        raise ValueError(f"plan schema: {ctx}{key!r} has type "
                         f"{type(v).__name__}, expected {kind}")
    return v


def validate_plan(plan: dict) -> None:
    """Schema + internal-consistency validation for every field this module
    needs. Raises on the first inconsistency; accepts no defaults."""
    size = _need(plan, "experiment_size", dict)
    for k, want in (("worlds", 6), ("arms", 5), ("timesteps", 2),
                    ("total_runs", 60), ("run_length_ticks", 200),
                    ("burn_in_ticks", 50), ("persistence_window_ticks", 20)):
        if _need(size, k, int, "experiment_size.") != want:
            raise ValueError(f"plan schema: experiment_size.{k} != {want}")
    if size["total_runs"] != size["worlds"] * size["arms"] * size["timesteps"]:
        raise ValueError("plan schema: total_runs inconsistent")
    if size.get("stochastic_study") is not False:
        raise ValueError("plan schema: study must be deterministic (no seed)")

    qm = _need(plan, "quantity_menu", dict)
    if _need(qm, "fractions", list, "quantity_menu.") != [0.25, 0.5, 0.75, 1.0]:
        raise ValueError("plan schema: quantity_menu.fractions differ from "
                         "the registered (0.25, 0.5, 0.75, 1.0)")
    if sorted(_need(qm, "identical_for_arms", list, "quantity_menu.")) != \
            ["B", "C", "D", "S"]:
        raise ValueError("plan schema: menu must be identical for B/C/D/S")

    arms = _need(plan, "arms", dict)
    for a in ("A_full_multi_edge_p1c", "B_restricted_matched_non_ebu",
              "C_restricted_observational_quote",
              "D_restricted_exact_total_quote_greedy",
              "S_restricted_local_service_priority",
              "E_aggregate_source_group_quote"):
        _need(arms, a, str, "arms.")
    if "NOT REGISTERED FOR EXECUTION" not in arms["E_aggregate_source_group_quote"]:
        raise ValueError("plan schema: arm E must remain non-executable")
    if _need(arms, "primary_comparison", str, "arms.") != "D versus B":
        raise ValueError("plan schema: primary comparison must be D versus B")

    worlds = _need(plan, "worlds", dict)
    if len(worlds) != 6:
        raise ValueError("plan schema: exactly 6 worlds required")
    ts = _need(_need(plan, "timestep", dict), "per_world", dict, "timestep.")
    for name, spec in worlds.items():
        cells = _need(spec, "cells", list, f"worlds.{name}.")
        edges = _need(spec, "edges", list, f"worlds.{name}.")
        x0 = _need(spec, "x0", list, f"worlds.{name}.")
        demand = _need(spec, "demand", list, f"worlds.{name}.")
        types = _need(spec, "types", dict, f"worlds.{name}.")
        _need(spec, "feasible", bool, f"worlds.{name}.")
        if not (len(cells) == len(x0) == len(demand)):
            raise ValueError(f"plan schema: {name} cell/x0/demand lengths differ")
        for c in cells:
            for k in ("alpha", "beta", "chi", "L", "U", "R", "K"):
                _need(c, k, (int, float), f"worlds.{name}.cells.")
        for e in edges:
            for k in ("i", "j", "M", "theta", "eta"):
                _need(e, k, (int, float), f"worlds.{name}.edges.")
            if not (0 <= e["i"] < len(cells) and 0 <= e["j"] < len(cells)):
                raise ValueError(f"plan schema: {name} edge endpoint out of range")
        for cid, kind in types.items():
            if kind != "regenerative":
                raise ValueError(f"plan schema: {name} source type {kind!r} "
                                 "not registered for O14 (regenerative only)")
            if not any(e["i"] == int(cid) for e in edges):
                raise ValueError(f"plan schema: {name} configured source "
                                 f"{cid} has no out-edge")
        if name not in ts:
            raise ValueError(f"plan schema: no timestep entry for {name}")
        t = ts[name]
        for k in ("binding_certificate", "one_edge_certificate",
                  "gershgorin_certificate", "lv_exact",
                  "registered_conservative_dt",
                  "registered_near_certificate_dt"):
            _need(t, k, (int, float), f"timestep.per_world.{name}.")
        if t["r_dt_conservative"] != 0.5 or t["r_dt_near"] != 0.9:
            raise ValueError(f"plan schema: {name} r_dt values differ from "
                             "the registered 0.5 / 0.9")
    for h in ("H" + str(i) for i in range(1, 11)):
        _need(_need(plan, "hypotheses", dict), h, str, "hypotheses.")
    for fkey in ("F" + str(i) for i in range(1, 16)):
        _need(_need(plan, "falsifiers", dict), fkey, str, "falsifiers.")
    _need(plan, "metrics_per_run", list)
    ib = _need(plan, "information_boundary", dict)
    _need(ib, "may_read", list, "information_boundary.")
    _need(ib, "may_not_read", list, "information_boundary.")


PLAN = load_plan()
validate_plan(PLAN)

# Frozen constants derived from the locked plan (no free choice below).
FRACTIONS = tuple(PLAN["quantity_menu"]["fractions"])      # (0.25,0.5,0.75,1.0)
RUN_TICKS = PLAN["experiment_size"]["run_length_ticks"]    # 200
BURN_IN_TICKS = PLAN["experiment_size"]["burn_in_ticks"]   # 50
# plan world_conventions.process_cost: C_a(q) = c0 + c1*q, c0 = 0.0,
# c1 = 0.1 * dt * (1 - eta) - the Gate-1 convention, unchanged.
LAM_L, C0 = 0.1, 0.0
# plan timestep.observation_model: exact observations, tau = 0, eps = 0.
TAU = 0.0
EPS_X = EPS_U = 0.0

# Executable arms in the frozen deterministic order (E is NOT executable).
EXEC_ARMS = ("A_full_multi_edge_p1c",
             "B_restricted_matched_non_ebu",
             "C_restricted_observational_quote",
             "D_restricted_exact_total_quote_greedy",
             "S_restricted_local_service_priority")
# dt-label mapping, frozen: plan field registered_conservative_dt -> label
# "conservative"; registered_near_certificate_dt -> "near_certificate"
# (the Gate 1D label convention).
DT_LABELS = ("conservative", "near_certificate")
_DT_FIELD = {"conservative": "registered_conservative_dt",
             "near_certificate": "registered_near_certificate_dt"}

WORLD_NAMES = tuple(sorted(PLAN["worlds"]))                # W1..W6 order


# ---------------------------------------------------------------------------
# 2. world + certificate reconstruction (designer side, fail closed)
# ---------------------------------------------------------------------------
def build_world(name: str):
    """(world, x0, configs, demand, meta) exactly from the locked plan."""
    spec = PLAN["worlds"][name]
    cells = tuple(d0.Cell(**{k: float(v) for k, v in c.items()
                             if k not in ("source", "rho")},
                          **({"source": c["source"], "rho": float(c["rho"])}
                             if "source" in c else {}))
                  for c in spec["cells"])
    edges = tuple(d0.Edge(i=int(e["i"]), j=int(e["j"]), M=float(e["M"]),
                          theta=float(e["theta"]), eta=float(e["eta"]))
                  for e in spec["edges"])
    world = d0.World(cells=cells, edges=edges)
    configs = {}
    for cid, kind in spec["types"].items():
        k = int(cid)
        configs[k] = p1c.SourceConfig(source_id=k, source_type=kind,
                                      R_eff=world.cells[k].R,
                                      eps_x=EPS_X, eps_u=EPS_U)
    meta = dict(feasible=bool(spec["feasible"]), note=spec["note"],
                family=spec["family"])
    return (world, tuple(float(v) for v in spec["x0"]),
            configs, tuple(float(v) for v in spec["demand"]), meta)


def world_certificates(name: str) -> dict:
    """Recompute every certificate with the released d0_v29 functions and
    fail closed on ANY mismatch with the locked plan (a platform producing a
    different float refuses to run - the conservative direction)."""
    world, *_ = build_world(name)
    locked = PLAN["timestep"]["per_world"][name]
    lv = d0.lv_exact(world)
    oe = min(d0.one_edge_dt_certificate(e, lv) for e in world.edges)
    gg = d0.gershgorin_dt_certificate(world, lv)
    cert = min(oe, gg)
    kind = "gershgorin" if gg <= oe else "one_edge"
    got = dict(lv_exact=lv, one_edge_certificate=oe,
               gershgorin_certificate=gg, binding_certificate=cert,
               binding_kind=kind,
               registered_conservative_dt=0.5 * cert,
               registered_near_certificate_dt=0.9 * cert)
    for k, v in got.items():
        if locked[k] != v:
            raise SystemExit(f"FATAL: {name} certificate field {k} "
                             f"recomputed {v!r} != locked {locked[k]!r}")
    return got


def world_dts(name: str) -> dict:
    """{label: dt} after the fail-closed certificate check; r_dt <= 1 by
    construction (0.5 / 0.9 x binding certificate, locked)."""
    got = world_certificates(name)
    out = {}
    for label in DT_LABELS:
        dt = got[_DT_FIELD[label]]
        if dt / got["binding_certificate"] > 1.0:
            raise SystemExit(f"FATAL: {name}/{label} r_dt > 1")
        out[label] = dt
    return out


# ---------------------------------------------------------------------------
# 3. DECISION PATH (strictly local; see module docstring and F7)
# ---------------------------------------------------------------------------
def screen_budget(cfg: p1c.SourceConfig, x: float, u: float, dt: float):
    """Authoritative source-local classification and aggregate export budget,
    computed with the released p1c functions (screening mirror of what
    p1c_step itself will apply; O14 registers regenerative sources only)."""
    state = p1c.classify_state(cfg, x, u, dt)
    if state == "P" and cfg.source_type == "regenerative":
        return state, p1c.robust_budget(cfg, x, u, dt)
    return state, 0.0


def candidate_menu(world: d0.World, x, u, sid: int,
                   cfg: p1c.SourceConfig, dt: float):
    """Shared candidate menu for arms B, C, D and S (literally this one
    function - capability identity is by construction, not comparison).

    Candidates enumerate the registered fractions of each own out-edge's raw
    loss-aware flux, capped by the authoritative budget. q_req is generated
    by evaluating the released d0.edge_flux on the MOBILITY-SCALED edge
    (M_sel = frac * M_e), and q_acc uses p1c_step's own sigma arithmetic, so
    the menu value is bit-identical to what the released allocator will
    execute (request-shaping identity, plan request_shaping.identity).

    Reads only: source frozen stock/parameters, authoritative P1C state and
    budget, adjacent destination LocalViews, edge constants, deterministic
    indices. q = 0 (rest) is the exact zero branch and is not enumerated as
    a candidate."""
    state, budget = screen_budget(cfg, x[sid], u[sid], dt)
    out = []
    if budget <= 0.0:
        return state, budget, out
    src_view = d0.local_view(world.cells[sid], x[sid])
    for eidx, e in enumerate(world.edges):
        if e.i != sid:
            continue
        dst_view = d0.local_view(world.cells[e.j], x[e.j])
        f, J = d0.edge_flux(src_view, dst_view, e)
        if J <= 0.0:
            continue                       # inactive edge this tick
        q_e_max = min(J, budget)           # never exceeded by any candidate
        for qi, frac in enumerate(FRACTIONS):
            scaled = d0.Edge(i=e.i, j=e.j, M=frac * e.M,
                             theta=e.theta, eta=e.eta)
            f2, q_req = d0.edge_flux(src_view, dst_view, scaled)
            if q_req <= 0.0:
                continue
            # p1c_step's own arithmetic for a single-edge source group:
            sigma = min(1.0, budget / q_req)
            q_acc = sigma * q_req
            if q_acc <= 0.0:
                continue
            out.append(dict(edge=eidx, quant_index=qi, frac=frac, f=f,
                            J=J, q_req=q_req, q_e_max=q_e_max, q_acc=q_acc))
    return state, budget, out


def quote_schedule_for(world: d0.World, x, u, dt: float, cand: dict,
                       tick: int):
    """The committed exact quote schedule for one candidate, built with the
    released ebu_quote_v30 implementation from frozen pre-action local state.
    Never evaluated outside [0, q_e_max] (the candidate's q_acc <= q_e_max
    by construction). The linear diagnostic is NEVER built here."""
    e = world.edges[cand["edge"]]
    inp = eq.LocalQuoteInput(
        src=d0.local_view(world.cells[e.i], x[e.i]),
        dst=d0.local_view(world.cells[e.j], x[e.j]),
        u_src=u[e.i], u_dst=u[e.j], dt=dt, eta=e.eta,
        q_req=cand["q_req"], q_acc=cand["q_acc"],
        source_id=e.i, dest_id=e.j,
        config_id=f"cfg:{e.i}:R{world.cells[e.i].R}")
    cost = eq.ProcessCost(category=eq.ALLOWED_COST_CATEGORY, c0=C0,
                          c1=LAM_L * dt * (1.0 - e.eta))
    return eq.build_quote(inp, cost, f"pass-{tick}", tick, 0)


def continuous_vertex_diagnostic(world: d0.World, x, u, dt: float,
                                 cand: dict) -> Optional[float]:
    """Closed-form continuous vertex q_cont* of the deficit-branch schedule
    (protocol section 2.A). DIAGNOSTIC ONLY - recorded, never used to select.
    Returns None when the deficit-branch formula has no interior vertex."""
    e = world.edges[cand["edge"]]
    ci, cj = world.cells[e.i], world.cells[e.j]
    z_i = x[e.i] + dt * u[e.i]
    z_j = x[e.j] + dt * u[e.j]
    D_j = max(0.0, cj.L - z_j)
    S_i = max(0.0, ci.L - z_i)
    a_s = ci.alpha if z_i < ci.L else 0.0
    denom = 2.0 * dt * (cj.alpha * e.eta * e.eta + a_s)
    if denom <= 0.0:
        return None
    num = 2.0 * cj.alpha * e.eta * D_j - 2.0 * a_s * S_i \
        - LAM_L * (1.0 - e.eta)
    return num / denom if num > 0.0 else 0.0


def select_arm_B(candidates: Sequence[dict]) -> Optional[dict]:
    """Restricted matched non-EBU baseline: largest released loss-aware
    force f_e; tie by larger q_acc, then lower edge index, then lower
    quantity-menu index (identifier determinism). No EBU input."""
    if not candidates:
        return None
    return max(candidates,
               key=lambda c: (c["f"], c["q_acc"],
                              -c["edge"], -c["quant_index"]))


def select_arm_D(candidates: Sequence[dict],
                 exact_quotes: Sequence[float]) -> Optional[int]:
    """Exact-total-quote greedy: index of the candidate with the largest
    STRICTLY POSITIVE exact total quote; ties by lower edge index, then
    lower quantity-menu index. Returns None (rest, the exact q = 0 branch)
    when no exact quote is strictly positive. Never ranks per unit; never
    consults the linear diagnostic."""
    if len(candidates) != len(exact_quotes):
        raise ValueError("candidates/quotes length mismatch")
    best = None
    for idx, (c, dq) in enumerate(zip(candidates, exact_quotes)):
        key = (dq, -c["edge"], -c["quant_index"])
        if best is None or key > best[0]:
            best = (key, idx, dq)
    if best is None or best[2] <= 0.0:
        return None
    return best[1]


def select_arm_S(candidates: Sequence[dict],
                 demand_rate: Sequence[float],
                 world: d0.World) -> Optional[dict]:
    """Registered strictly-local service-priority comparator:
    score = eta_e * q_acc * 1[declared demand rate of destination > 0];
    ties by lower edge index, then lower quantity-menu index. Reads only the
    menu and the adjacent destination's declared demand rate. Rests when the
    best score is not positive (no demanding destination is reachable -
    unreachable in the registered worlds, where every destination demands)."""
    if not candidates:
        return None
    def score(c):
        e = world.edges[c["edge"]]
        return e.eta * c["q_acc"] * (1.0 if demand_rate[e.j] > 0.0 else 0.0)
    best = max(candidates,
               key=lambda c: (score(c), -c["edge"], -c["quant_index"]))
    return best if score(best) > 0.0 else None


# Functions whose source constitutes the decision path (AST-scanned and
# runtime-poisoned by test_v30_o14.py; F7).
DECISION_PATH_FUNCS = (screen_budget, candidate_menu, quote_schedule_for,
                       select_arm_B, select_arm_D, select_arm_S)


# ---------------------------------------------------------------------------
# 4. EVALUATION LAYER (harness side; never consulted by the decision path)
# ---------------------------------------------------------------------------
def shaped_active_world(world: d0.World, cand: Optional[dict]) -> d0.World:
    """Locked request shaping: the active world contains ONLY the selected
    edge, with M_sel = frac * M_e, so the released p1c_step regenerates
    exactly the selected request and applies its authoritative budget.
    cand = None (rest) yields an empty active world."""
    if cand is None:
        return d0.World(cells=world.cells, edges=())
    e = world.edges[cand["edge"]]
    return d0.World(cells=world.cells,
                    edges=(d0.Edge(i=e.i, j=e.j, M=cand["frac"] * e.M,
                                   theta=e.theta, eta=e.eta),))


def group_quote_diagnostic(world: d0.World, x, u, dt: float,
                           edge_q_acc: Sequence[float], tick: int) -> dict:
    """Settlement-free arm-A diagnostic (plan aggregate_quote_diagnostics):
    the exact aggregate local quote over the source(s) and destinations of
    the executed multi-edge action set, and the naive sum of independently
    frozen per-edge exact quotes. NOTHING is settled, credited or allocated;
    O3 remains open."""
    active = [(k, e, q) for k, (e, q)
              in enumerate(zip(world.edges, edge_q_acc)) if q > 0.0]
    if not active:
        return dict(group_quote=0.0, naive_independent_sum=0.0,
                    double_count=0.0, n_actions=0)
    involved = sorted({e.i for _, e, _ in active}
                      | {e.j for _, e, _ in active})
    z = {i: x[i] + dt * u[i] for i in involved}

    def v(i, val):
        c = world.cells[i]
        return d0.penalty(c.alpha, c.beta, c.chi, c.L, c.U, c.R, val)

    before = math.fsum(v(i, z[i]) for i in involved)
    succ = dict(z)
    cost = 0.0
    for _, e, q in active:
        succ[e.i] -= dt * q
        succ[e.j] += dt * e.eta * q
        cost += C0 + (LAM_L * dt * (1.0 - e.eta)) * q
    after = math.fsum(v(i, succ[i]) for i in involved)
    group = before - after - cost
    naive = 0.0
    for k, e, q in active:
        cand = dict(edge=k, quant_index=0, frac=1.0,
                    f=0.0, J=q, q_req=q, q_e_max=q, q_acc=q)
        sch = quote_schedule_for(world, x, u, dt, cand, tick)
        naive += sch.exact(q)
    return dict(group_quote=group, naive_independent_sum=naive,
                double_count=naive - group, n_actions=len(active))


def o14_tick(world: d0.World, x, dt: float,
             configs: Mapping[int, p1c.SourceConfig],
             demand_rate: Sequence[float], arm: str, tick: int) -> dict:
    """One bounded tick of one arm. Selection happens on the decision path;
    physics goes through the released p1c_step inside service_v30.bounded_step
    (Gate 1D bounded-service ordering, unmodified). Returns the per-tick
    record with every plan-registered metric; mutates nothing."""
    if arm not in EXEC_ARMS:
        raise ValueError(f"arm {arm!r} is not executable (E is design-only)")
    u = sv.drive_no_demand(world, x)
    menus, quotes, selected = {}, {}, None
    rested = False
    if arm == "A_full_multi_edge_p1c":
        active = world
    else:
        # exactly one action per source per micro-step; O14 worlds register
        # a single configured source, but the loop is generic and ordered.
        chosen = []
        for sid in sorted(configs):
            state, budget, cands = candidate_menu(world, x, u, sid,
                                                  configs[sid], dt)
            menus[sid] = dict(state=state, budget=budget, candidates=cands)
            if not cands:
                rested = True
                continue
            if arm == "B_restricted_matched_non_ebu":
                pick = select_arm_B(cands)
            elif arm == "C_restricted_observational_quote":
                pick = select_arm_B(cands)          # C is B's selection
                # full candidate-menu schedules recorded OBSERVATIONALLY,
                # strictly after the selection is fixed (plan arms.C)
                quotes[sid] = [quote_schedule_for(world, x, u, dt, c,
                                                  tick).exact(c["q_acc"])
                               for c in cands]
            elif arm == "D_restricted_exact_total_quote_greedy":
                exact = []
                for c in cands:
                    sch = quote_schedule_for(world, x, u, dt, c, tick)
                    dq = sch.exact(c["q_acc"])
                    exact.append(dq)
                quotes[sid] = exact
                idx = select_arm_D(cands, exact)
                pick = cands[idx] if idx is not None else None
            else:                                    # S
                pick = select_arm_S(cands, demand_rate, world)
            if pick is None:
                rested = True                        # exact q = 0 rest branch
            else:
                chosen.append(pick)
        selected = chosen[0] if chosen else None
        active = shaped_active_world(world, selected)

    out = sv.bounded_step(world, x, dt, configs, demand_rate,
                          active_world=active)

    # request-shaping identity (plan request_shaping.identity; F2/F12)
    if arm != "A_full_multi_edge_p1c" and selected is not None:
        if len(out.q_acc) != 1 or out.q_acc[0] != selected["q_acc"]:
            raise AssertionError(
                "request-shaping identity violated: executed "
                f"{out.q_acc!r} != selected menu q_acc {selected['q_acc']!r}")

    # observational settlement (C settles B's executed action; D its own)
    ebu_tick = pos = neg = 0.0
    quoted = 0
    if arm in ("C_restricted_observational_quote",
               "D_restricted_exact_total_quote_greedy") \
            and selected is not None and out.q_acc[0] > 0.0:
        reg = eq.EpochRegistry()
        sch = quote_schedule_for(world, x, u, dt, selected, tick)
        reg.register(sch)
        r = reg.settle(sch, out.q_acc[0], tick, 0)
        if r.status == "settled":
            ebu_tick = r.issued
            pos, neg = max(0.0, r.issued), max(0.0, -r.issued)
            quoted = 1

    n = world.n
    xb, xa = out.x_before, out.x_after
    rx = sum(1 for i in range(n) if i in configs
             and configs[i].R_eff is not None
             and sv.reserve_crossing(xb[i], xa[i], configs[i].R_eff))
    ax = sum(1 for i in range(n) if world.cells[i].source == "allee"
             and xa[i] < world.cells[i].A <= xb[i])
    overuse = math.fsum(max(0.0, sr.Q_acc - sr.Q_max)
                        for sr in out.source_results)
    sigma = {sr.source_id: sr.sigma for sr in out.source_results}
    budget_util = {sr.source_id: (sr.Q_acc / sr.Q_max if sr.Q_max > 0 else 0.0)
                   for sr in out.source_results}
    src_ids = [i for i in configs if configs[i].R_eff is not None]
    rec = dict(
        tick=tick, arm=arm, dt=dt,
        x_before=list(xb), x_after=list(xa), u=list(u),
        active_out_edges=(sorted({c["edge"] for m in menus.values()
                                  for c in m["candidates"]})
                          if menus else
                          [k for k, q in enumerate(out.q_req) if q > 0.0]),
        menus={sid: dict(state=m["state"], budget=m["budget"],
                         candidates=[dict(c) for c in m["candidates"]])
               for sid, m in menus.items()},
        candidate_exact_quotes={sid: list(v) for sid, v in quotes.items()},
        candidate_per_unit_quotes={
            sid: [dq / c["q_acc"] for dq, c
                  in zip(v, menus[sid]["candidates"])]
            for sid, v in quotes.items()},                # diagnostic only
        candidate_continuous_vertices={
            sid: [continuous_vertex_diagnostic(world, x, u, dt, c)
                  for c in m["candidates"]]
            for sid, m in menus.items()},                 # diagnostic only
        selected=(dict(selected) if selected is not None else None),
        rested=bool(rested and selected is None),
        executed_q_acc=list(out.q_acc), q_req=list(out.q_req),
        delivered=[e.eta * q for e, q
                   in zip((active.edges if arm != "A_full_multi_edge_p1c"
                           else world.edges), out.q_acc)],
        sigma=sigma, budget_utilization=budget_util,
        service=list(out.service), unmet=list(out.unmet),
        demand_amount=list(out.demand_amount),
        transport_loss=out.transport_loss,
        negative_corrections=list(out.negative_corrections),
        ledger_residual=out.ledger_residual,
        domain_failure=bool(out.domain_failure),
        reserve_crossings=rx, allee_crossings=ax, physical_overuse=overuse,
        min_source=min((xa[i] for i in src_ids), default=float("nan")),
        burden=d0.V_total(world, xa),                     # evaluation layer
        viability=100.0 * sum(1 for i in range(n)
                              if xa[i] >= world.cells[i].L) / n,
        ebu=ebu_tick, ebu_pos=pos, ebu_neg=neg, quoted=quoted,
        group_diagnostic=(group_quote_diagnostic(world, x, u, dt,
                                                 out.q_acc, tick)
                          if arm == "A_full_multi_edge_p1c" else None),
    )
    return rec


def run_arm(world_name: str, arm: str, dt_label: str,
            ticks: Optional[int] = None) -> sv.RunResult:
    """Run one (world, arm, timestep) for `ticks` ticks (default: the
    registered 200). THE OFFICIAL 60-RUN STUDY IS NOT EXECUTED IN THIS
    STAGE - only the future authorized runner may call this at the
    registered horizon for every specification. Produces a service_v30
    RunResult so the Gate 1D predicates and classification apply verbatim."""
    world, x0, configs, demand, meta = build_world(world_name)
    dts = world_dts(world_name)
    dt = dts[dt_label]
    horizon = RUN_TICKS if ticks is None else int(ticks)
    x = tuple(x0)
    ser = dict(service=[], unmet=[], demand=[], burden=[], viability=[],
               ebu=[], actions=[], q_acc=[], loss=[], min_source=[],
               opportunities=[], proposed=[], rests=[], p1c_rejected=[],
               quoted=[], corrections=[], ledger=[],
               selected_edge=[], service_by_dest=[], unmet_by_dest=[])
    tot = dict(service=0.0, unmet=0.0, demand=0.0, ebu=0.0, ebu_pos=0.0,
               ebu_neg=0.0, actions=0, opportunities=0, proposed=0,
               accepted=0, quoted=0, rests=0, p1c_rejected=0, loss=0.0,
               overuse=0.0, reserve_crossings=0, allee_crossings=0,
               corrections=0.0, max_ledger_residual=0.0,
               quote_pos=0, quote_zero=0, quote_neg=0)
    domain_fail_tick = None
    for t in range(1, horizon + 1):
        rec = o14_tick(world, x, dt, configs, demand, arm, t)
        n_act = sum(1 for q in rec["executed_q_acc"] if q > 0.0)
        rejected = sum(1 for k in range(len(rec["q_req"]))
                       if rec["q_req"][k] > 0.0
                       and rec["executed_q_acc"][k] <= 0.0)
        opportunities = sum(len(m["candidates"])
                            for m in rec["menus"].values()) \
            if rec["menus"] else len(world.edges)
        for sid, exact in rec["candidate_exact_quotes"].items():
            for dq in exact:
                if dq > 0.0:
                    tot["quote_pos"] += 1
                elif dq < 0.0:
                    tot["quote_neg"] += 1
                else:
                    tot["quote_zero"] += 1
        svc, unm = math.fsum(rec["service"]), math.fsum(rec["unmet"])
        ser["service"].append(svc); ser["unmet"].append(unm)
        ser["demand"].append(math.fsum(rec["demand_amount"]))
        ser["burden"].append(rec["burden"])
        ser["viability"].append(rec["viability"])
        ser["ebu"].append(rec["ebu"]); ser["actions"].append(n_act)
        ser["q_acc"].append(math.fsum(rec["executed_q_acc"]))
        ser["loss"].append(rec["transport_loss"])
        ser["min_source"].append(rec["min_source"])
        ser["opportunities"].append(opportunities)
        ser["proposed"].append(0 if rec["selected"] is None
                               and rec["menus"] else 1)
        ser["rests"].append(1 if rec["rested"] else 0)
        ser["p1c_rejected"].append(rejected)
        ser["quoted"].append(rec["quoted"])
        ser["corrections"].append(math.fsum(rec["negative_corrections"]))
        ser["ledger"].append(rec["ledger_residual"])
        ser["selected_edge"].append(rec["selected"]["edge"]
                                    if rec["selected"] else None)
        ser["service_by_dest"].append(list(rec["service"]))
        ser["unmet_by_dest"].append(list(rec["unmet"]))
        tot["service"] += svc; tot["unmet"] += unm
        tot["demand"] += math.fsum(rec["demand_amount"])
        tot["ebu"] += rec["ebu"]; tot["ebu_pos"] += rec["ebu_pos"]
        tot["ebu_neg"] += rec["ebu_neg"]
        tot["actions"] += n_act; tot["opportunities"] += opportunities
        tot["proposed"] += ser["proposed"][-1]; tot["accepted"] += n_act
        tot["quoted"] += rec["quoted"]; tot["rests"] += ser["rests"][-1]
        tot["p1c_rejected"] += rejected
        tot["loss"] += rec["transport_loss"]
        tot["overuse"] += rec["physical_overuse"] * dt
        tot["reserve_crossings"] += rec["reserve_crossings"]
        tot["allee_crossings"] += rec["allee_crossings"]
        tot["corrections"] += math.fsum(rec["negative_corrections"])
        tot["max_ledger_residual"] = max(tot["max_ledger_residual"],
                                         abs(rec["ledger_residual"]))
        if rec["domain_failure"] and domain_fail_tick is None:
            domain_fail_tick = t
        x = tuple(rec["x_after"])
    n = world.n
    dead = sum(1 for i in range(n) if world.cells[i].source == "allee"
               and x[i] < world.cells[i].A)
    src_ids = sorted(configs)
    final = dict(
        x=list(x), burden=ser["burden"][-1], viability=ser["viability"][-1],
        min_source=ser["min_source"][-1], dead_sources=dead,
        domain_failure_tick=domain_fail_tick,
        negative_state=any(v < -sv.DOMAIN_TOL for v in x),
        source_stock=math.fsum(x[i] for i in src_ids),
        destination_stock=math.fsum(x[i] for i in range(n)
                                    if i not in src_ids),
        feasible_world=meta["feasible"], note=meta["note"])
    dt_cert = world_certificates(world_name)["binding_certificate"]
    return sv.RunResult(
        run_id=run_id(world_name, arm, dt_label), world=world_name, arm=arm,
        dt_label=dt_label, dt=dt, dt_certificate=dt_cert,
        certificate_kind=world_certificates(world_name)["binding_kind"],
        r_dt=dt / dt_cert, series=ser, totals=tot, final=final,
        x_trajectory_tail=tuple(x))


# ---------------------------------------------------------------------------
# run inventory (reconstruction only; nothing here executes anything)
# ---------------------------------------------------------------------------
def run_id(world: str, arm: str, dt_label: str) -> str:
    return f"{world}|{arm}|{dt_label}"


def build_run_specs() -> list:
    """Exactly the 60 registered run specifications in the frozen
    deterministic order: sorted worlds x dt labels x executable arms.
    Reconstruction only - no run is executed by this function."""
    specs = []
    for world in WORLD_NAMES:
        for dt_label in DT_LABELS:
            for arm in EXEC_ARMS:
                specs.append(dict(world=world, arm=arm, dt_label=dt_label,
                                  run_id=run_id(world, arm, dt_label)))
    if len(specs) != PLAN["experiment_size"]["total_runs"]:
        raise SystemExit("FATAL: reconstructed run count != registered 60")
    if len({s["run_id"] for s in specs}) != len(specs):
        raise SystemExit("FATAL: duplicate run identifiers")
    return specs


# mapping from every plan-registered metric line to the record fields that
# realize it (asserted complete by test_v30_o14.py T14)
METRIC_FIELDS = {
    "per-tick source and destination stocks": ("x_before", "x_after"),
    "per-tick active outgoing edges (J_e > 0 count and identity)":
        ("active_out_edges",),
    "per-tick candidate menu: edge, fraction, q_req, q_e_max, q_acc":
        ("menus",),
    "per-tick exact quote for EVERY candidate (full schedule value at its q)":
        ("candidate_exact_quotes",),
    "per-tick per-unit quote per candidate (diagnostic only)":
        ("candidate_per_unit_quotes",),
    "per-tick continuous vertex q_cont* per candidate (diagnostic only)":
        ("candidate_continuous_vertices",),
    "selected edge and selected quantity (q_e*), executed q_acc":
        ("selected", "executed_q_acc"),
    "accepted and delivered quantities per edge": ("executed_q_acc",
                                                   "delivered"),
    "aggregate safe-budget utilization Q_acc/Q_max and sigma":
        ("budget_utilization", "sigma"),
    "service and unmet demand BY DESTINATION and totals":
        ("service", "unmet"),
    "persistent service deficit fields (Gate 1D operationalization)":
        ("service", "unmet"),          # via sv.service_alignment_predicate
    "burden and viability (corroborating only)": ("burden", "viability"),
    "reserve crossings (corrected tolerance) and Allee crossings":
        ("reserve_crossings", "allee_crossings"),
    "dead sources; physical overuse; transport loss":
        ("physical_overuse", "transport_loss"),
    "action counts; voluntary rests; p1c rejections":
        ("executed_q_acc", "rested"),
    "positive, zero and negative exact-quote candidate counts":
        ("candidate_exact_quotes",),
    "quote coverage (quoted actions / accepted actions)": ("quoted",),
    "arm-A group quote and naive independent sum (settlement-free)":
        ("group_diagnostic",),
    "domain status and negative-state corrections":
        ("domain_failure", "negative_corrections"),
    "timestep certificate, binding kind and r_dt": ("dt",),
    "ledger residual and recomputation residuals": ("ledger_residual",),
    "EBU totals (evaluation variable only): total, positive, negative":
        ("ebu", "ebu_pos", "ebu_neg"),
}


def strict_json_dumps(obj) -> str:
    """Deterministic strict serialization (allow_nan=False, sorted keys)."""
    return json.dumps(obj, sort_keys=True, ensure_ascii=True,
                      allow_nan=False)


if __name__ == "__main__":
    raise SystemExit(
        "o14_v30 is a library. The pre-execution suite is test_v30_o14.py; "
        "the official runner (exp_v30_o14.py) is NOT yet authorized and "
        "does not exist.")
