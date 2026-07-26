"""
V2.9 Gate 2 - deterministic behavioral wind tunnel (preregistered).

Runs ONLY the fixtures D1-D8 registered in v29_deterministic_plan.json, whose
canonical SHA-256 hash is locked in Pre-experiment Amendment 3 of
V2.9_BEHAVIORAL_PROTOCOL_DRAFT.md. The harness refuses to run if the hash of
the plan file differs from the hash recorded in the amendment. All fixture
parameters come from the JSON plan - none is duplicated here.

Policies (Amendment 3 Sec 19.1):
  P0        no transport (same cells, no edges)          - baseline
  P1        exact D0 (d0_v29.d0_step, unconstrained)     - the theorem object
  P1K-diag  projection wrapper d0_v29.p1k_step           - DIAGNOSTIC ONLY
  P2        loss-blind synchronous ablation              - harness-side control
  P3        sequential-live ablation                     - harness-side control
  P4        exact P1 law at r_dt > 1                     - DELIBERATELY UNSAFE

Information boundary: the decision-path functions below (_p*_decide) read only
frozen local state, declared local parameters, and edge constants. Global V,
viability, served demand, recovery and every other metric are computed by
_tick_diagnostics/_summarize AFTER all local decisions of the tick and are
never inputs to any decision (protocol Sec 4; enforced by test_v29_behavior.py
group 9).

Physical-service rules (Amendment 2 Sec 18.1 / Amendment 3 Sec 19.4): declared
demand counts as served only while the complete raw trajectory has had no
material lower-bound exit; from the first material exit the run is flagged
invalid-service. P1K material shortfall invalidates service attribution for
the tick and is never renamed unmet demand. Projection never converts a failed
P1 run into a success.

Standard library only. Direct execution:
  python3 exp_v29.py > results/v2.9/deterministic/v29_deterministic_stdout.txt
"""
from __future__ import annotations
import gzip
import hashlib
import json
import math
import os
import re
import sys

import d0_v29 as d0

PLAN_PATH = "v29_deterministic_plan.json"
PROTOCOL_PATH = "V2.9_BEHAVIORAL_PROTOCOL_DRAFT.md"
OUT_DIR = os.path.join("results", "v2.9", "deterministic")
SUMMARY_PATH = os.path.join(OUT_DIR, "v29_deterministic_summary.json")
TRACE_PATH = os.path.join(OUT_DIR, "v29_deterministic_trace.json")
TRACE_GZ_THRESHOLD = 10 * 1024 * 1024   # gzip (stdlib, documented) above 10 MiB

HASH_RE = re.compile(r"Canonical plan hash \(SHA-256\):\*\*\s*`([0-9a-f]{64})`")

FIXTURE_IDS = ("D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8")

# per-tick columnar schema shared by every run; P1K runs append P1K_EXTRA
SCHEMA = [
    "tick", "x_before", "x_after", "u", "mu", "f", "J", "sj",
    "V_before", "V_after", "drive_term", "dissipation", "remainder_bound",
    "inequality_residual", "ledger_residual", "transport_loss",
    "min_x", "max_x", "viable_fraction", "source_stock",
    "reserve_below", "allee_below",
    "requested_demand", "served_valid", "invalid_service_flag",
    "lower_violation", "upper_violation", "shock_active",
]
P1K_EXTRA = [
    "raw_x_after", "shortfall", "spill", "material_shortfall",
    "material_spill", "eligible_for_physical_service_claim",
    "p1k_ledger_residual",
]


# ---------------------------------------------------------------------------
# plan loading and hash lock
# ---------------------------------------------------------------------------
def canonical_hash(plan: dict) -> str:
    canon = json.dumps(plan, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(canon).hexdigest()


def recorded_hash(protocol_text: str) -> str:
    m = HASH_RE.search(protocol_text)
    if not m:
        raise SystemExit("FATAL: no canonical plan hash found in Amendment 3 "
                         f"of {PROTOCOL_PATH}; refusing to run.")
    return m.group(1)


def load_plan(base_dir: str = ".") -> tuple[dict, str]:
    with open(os.path.join(base_dir, PLAN_PATH), encoding="utf-8") as fh:
        plan = json.load(fh)
    got = canonical_hash(plan)
    with open(os.path.join(base_dir, PROTOCOL_PATH), encoding="utf-8") as fh:
        want = recorded_hash(fh.read())
    if got != want:
        raise SystemExit(
            "FATAL: canonical plan hash mismatch - the plan file differs from "
            f"the preregistered Amendment 3 hash.\n  plan file: {got}\n  "
            f"amendment: {want}\nRefusing to run.")
    return plan, got


# ---------------------------------------------------------------------------
# world construction (parameters come exclusively from the JSON plan)
# ---------------------------------------------------------------------------
def build_cells(cell_dicts) -> tuple:
    return tuple(d0.Cell(alpha=c["alpha"], beta=c["beta"], chi=c["chi"],
                         L=c["L"], U=c["U"], R=c["R"], K=c["K"],
                         s=c["s"], d=c["d"], lam=c["lam"], kappa=c["kappa"],
                         source=c["source"], rho=c["rho"], A=c["A"])
                 for c in cell_dicts)


def build_edges(edge_dicts) -> tuple:
    return tuple(d0.Edge(i=e["i"], j=e["j"], M=e["M"], theta=e["theta"],
                         eta=e["eta"]) for e in edge_dicts)


def build_world(cell_dicts, edge_dicts) -> d0.World:
    return d0.World(cells=build_cells(cell_dicts), edges=build_edges(edge_dicts))


def extras_for_tick(fx: dict, n: int, tick: int):
    """Per-tick non-negative s_extra/d_extra schedules from the registered
    shock specification (Amendment 2 Sec 18.3 semantics). tick is 1-based."""
    s_extra = [0.0] * n
    d_extra = [0.0] * n
    shock = fx.get("shock")
    active = False
    if shock:
        # tick is 1-based; the registered window [start_tick, end_tick) is
        # 0-based over tick indices, matching the trace's tick-1 offset
        in_shock = shock["start_tick"] <= tick - 1 < shock["end_tick_exclusive"]
        active = in_shock
        if shock["type"] == "supply":
            s_extra[shock["cell"]] = (shock["value_during_shock"] if in_shock
                                      else shock["baseline_s_extra"])
        elif shock["type"] == "demand":
            if in_shock:
                d_extra[shock["cell"]] = shock["d_extra_during_shock"]
        else:
            raise SystemExit(f"FATAL: unknown shock type {shock['type']!r}")
    return s_extra, d_extra, active


# ---------------------------------------------------------------------------
# DECISION PATH - strictly local; no global metric may appear in this section
# (test_v29_behavior.py group 9 disables d0.V_total/lv_exact and re-runs these)
# ---------------------------------------------------------------------------
def _p1_decide(world, x, dt, s_extra, d_extra):
    """Exact D0 (also used for P4 at its registered oversized dt)."""
    res = d0.d0_step(world, x, dt, s_extra=s_extra, d_extra=d_extra,
                     diagnostics=False)
    return {"x_after": list(res.x_after), "u": list(res.u), "mu": list(res.mu),
            "f": list(res.f), "J": list(res.J), "sj": list(res.sj),
            "loss": res.transport_loss}


def _p0_decide(world_no_edges, x, dt, s_extra, d_extra):
    """No transport: natural dynamics only (same cells, no edges)."""
    res = d0.d0_step(world_no_edges, x, dt, s_extra=s_extra, d_extra=d_extra,
                     diagnostics=False)
    return {"x_after": list(res.x_after), "u": list(res.u), "mu": list(res.mu),
            "f": [], "J": [], "sj": list(res.sj), "loss": 0.0}


def _p1k_decide(world, x, dt, s_extra, d_extra):
    """Diagnostic projection wrapper (Amendment 2 Sec 18.1). NOT a successful
    physical policy; flux decisions are the unchanged exact D0 proposals."""
    r = d0.p1k_step(world, x, dt, s_extra=s_extra, d_extra=d_extra,
                    diagnostics=False)
    raw = r.raw
    return {"x_after": list(r.x_after), "u": list(raw.u), "mu": list(raw.mu),
            "f": list(raw.f), "J": list(raw.J), "sj": list(raw.sj),
            "loss": raw.transport_loss,
            "raw_x_after": list(raw.x_after),
            "shortfall": list(r.shortfall), "spill": list(r.spill),
            "material_shortfall": r.material_shortfall,
            "material_spill": r.material_spill,
            "eligible": r.eligible_for_physical_service_claim,
            "p1k_ledger_residual": r.ledger_residual}


def _p2_decide(world, x, dt, s_extra, d_extra):
    """Loss-blind synchronous ablation: force g = mu_i - mu_j (no eta weight),
    J = M[g - theta]_+, applied with the lossy column (-J, +eta J). Reads only
    the two endpoints' local data. Registered negative control (CE-D)."""
    n = world.n
    u = [d0.natural_drive(c, x[k], s_extra[k], d_extra[k])
         for k, c in enumerate(world.cells)]
    mu = [d0.marginal(c.alpha, c.beta, c.chi, c.L, c.U, c.R, x[k])
          for k, c in enumerate(world.cells)]
    f_list, J_list = [], []
    contrib = [[] for _ in range(n)]
    for e in world.edges:
        g = mu[e.i] - mu[e.j]                    # loss-blind force
        J = e.M * (g - e.theta) if g > e.theta else 0.0
        f_list.append(g)
        J_list.append(J)
        if J != 0.0:
            contrib[e.i].append(-J)
            contrib[e.j].append(e.eta * J)
    sj = [math.fsum(parts) for parts in contrib]
    xn = [x[k] + dt * (u[k] + sj[k]) for k in range(n)]
    loss = dt * math.fsum((1.0 - e.eta) * J for e, J in zip(world.edges, J_list))
    return {"x_after": xn, "u": u, "mu": mu, "f": f_list, "J": J_list,
            "sj": sj, "loss": loss}


def _p3_decide(world, x, dt, s_extra, d_extra):
    """Sequential-live ablation: loss-aware per-edge law, but edges ordered by
    descending force at the frozen tick-start state and applied ONE AT A TIME
    against live state (DE-family convention); frozen-state natural drive added
    synchronously at the end. Registered negative control (Obs 9.2)."""
    n = world.n
    u = [d0.natural_drive(c, x[k], s_extra[k], d_extra[k])
         for k, c in enumerate(world.cells)]
    mu = [d0.marginal(c.alpha, c.beta, c.chi, c.L, c.U, c.R, x[k])
          for k, c in enumerate(world.cells)]
    frozen_f = []
    for e in world.edges:
        fe, _ = d0.edge_flux(d0.local_view(world.cells[e.i], x[e.i]),
                             d0.local_view(world.cells[e.j], x[e.j]), e)
        frozen_f.append(fe)
    order = sorted(range(len(world.edges)),
                   key=lambda k: (-frozen_f[k], k))
    y = list(x)
    f_live = [0.0] * len(world.edges)
    J_live = [0.0] * len(world.edges)
    for k in order:
        e = world.edges[k]
        fe, Je = d0.edge_flux(d0.local_view(world.cells[e.i], y[e.i]),
                              d0.local_view(world.cells[e.j], y[e.j]), e)
        f_live[k] = fe
        J_live[k] = Je
        if Je != 0.0:
            y[e.i] -= dt * Je
            y[e.j] += dt * e.eta * Je
    sj = [(y[k] - x[k]) / dt for k in range(n)]
    xn = [y[k] + dt * u[k] for k in range(n)]
    loss = dt * math.fsum((1.0 - e.eta) * J
                          for e, J in zip(world.edges, J_live))
    return {"x_after": xn, "u": u, "mu": mu, "f": f_live, "J": J_live,
            "sj": sj, "loss": loss}
# --------------------------- end of decision path -------------------------


# ---------------------------------------------------------------------------
# researcher diagnostics - computed AFTER the tick's local decisions
# ---------------------------------------------------------------------------
def _tau_b(world, y):
    return 1e-12 * max(1.0, max(c.K for c in world.cells),
                       max(abs(v) for v in y))


def _tick_diagnostics(world, dec, x_before, dt, lv, synchronous_d0: bool):
    """Global evaluation of one recorded tick. Never feeds back into decisions."""
    v_before = d0.V_total(world, x_before)
    v_after = d0.V_total(world, dec["x_after"])
    ledger_lhs = math.fsum(dec["x_after"]) - math.fsum(x_before)
    ledger_rhs = dt * math.fsum(dec["u"]) - dec["loss"]
    ledger_res = ledger_lhs - ledger_rhs
    drive = diss = rn = ineq = None
    if synchronous_d0:
        # V2.8 (*) terms; for P1K these apply to the RAW proposal
        raw_after = dec.get("raw_x_after", dec["x_after"])
        v_raw_after = d0.V_total(world, raw_after)
        drive = dt * math.fsum(m * uu for m, uu in zip(dec["mu"], dec["u"]))
        diss = dt * math.fsum(J * J / e.M + e.theta * J
                              for e, J in zip(world.edges, dec["J"]))
        rn = 0.5 * lv * dt * dt * math.fsum(
            (uu + ss) ** 2 for uu, ss in zip(dec["u"], dec["sj"]))
        ineq = (v_raw_after - v_before) - (drive - diss + rn)
        if "raw_x_after" in dec:
            # P1K ledger is its own identity; the raw-step ledger is checked
            # against the raw proposal instead
            ledger_res = (math.fsum(raw_after) - math.fsum(x_before)) \
                - (dt * math.fsum(dec["u"]) - dec["loss"])
    return v_before, v_after, drive, diss, rn, ineq, ledger_res


def _run_one(fx, cell_dicts, edge_dicts, policy, dt, x0, label=""):
    """Execute one fixture/policy run and return (meta, rows)."""
    world = build_world(cell_dicts, edge_dicts)
    n = world.n
    is_p1k = policy == "P1K-diag"
    decide = {"P0": _p0_decide, "P1": _p1_decide, "P4": _p1_decide,
              "P1K-diag": _p1k_decide, "P2": _p2_decide, "P3": _p3_decide}[policy]
    dec_world = d0.World(cells=world.cells, edges=()) if policy == "P0" else world
    lv = d0.lv_exact(world)
    cert = (d0.gershgorin_dt_certificate(world)
            if world.edges and policy != "P0" else None)
    source_cells = [k for k, c in enumerate(world.cells)
                    if c.source != "none" or c.s > 0.0]
    shock = fx.get("shock")
    if shock and shock["type"] == "supply" and shock["cell"] not in source_cells:
        source_cells.append(shock["cell"])
    reserve_cells = [k for k, c in enumerate(world.cells)
                     if c.R > 0.0 and c.source in ("logistic", "allee")]
    allee_cells = [k for k, c in enumerate(world.cells) if c.source == "allee"]
    demand_base = math.fsum(c.d for c in world.cells)

    rows = []
    x = list(x0)
    invalid_service = False
    for tick in range(1, fx["ticks"] + 1):
        s_extra, d_extra, shock_active = extras_for_tick(fx, n, tick)
        dec = decide(dec_world, x, dt, s_extra, d_extra)
        v_b, v_a, drive, diss, rn, ineq, ledger = _tick_diagnostics(
            world, dec, x, dt, lv,
            synchronous_d0=policy in ("P0", "P1", "P4", "P1K-diag"))
        raw_after = dec.get("raw_x_after", dec["x_after"])
        tb = _tau_b(world, raw_after)
        lower_v = any(v < -tb for v in raw_after)
        upper_v = any(v > world.cells[k].K + tb for k, v in enumerate(raw_after))
        if lower_v:
            invalid_service = True
        requested = dt * (demand_base + math.fsum(d_extra))
        if is_p1k:
            served = requested if dec["eligible"] else 0.0
        else:
            served = 0.0 if invalid_service else requested
        xa = dec["x_after"]
        row = [
            tick, list(x), list(xa), dec["u"], dec["mu"], dec["f"], dec["J"],
            dec["sj"], v_b, v_a, drive, diss, rn, ineq, ledger, dec["loss"],
            min(xa), max(xa),
            math.fsum(1.0 for k in range(n) if xa[k] >= world.cells[k].L) / n,
            [xa[k] for k in source_cells],
            [xa[k] < world.cells[k].R for k in reserve_cells],
            [xa[k] < world.cells[k].A for k in allee_cells],
            requested, served, invalid_service, lower_v, upper_v, shock_active,
        ]
        if is_p1k:
            row += [dec["raw_x_after"], dec["shortfall"], dec["spill"],
                    dec["material_shortfall"], dec["material_spill"],
                    dec["eligible"], dec["p1k_ledger_residual"]]
        rows.append(row)
        x = list(xa)

    meta = {
        "fixture": fx["id"], "config": label or None, "policy": policy,
        "deliberately_unsafe": policy == "P4",
        "covered_by_v28_theorem": policy in ("P0", "P1"),
        "dt": dt, "ticks": fx["ticks"], "burn_in": fx["burn_in"],
        "lv_exact": lv,
        "certificate_kind": "gershgorin" if cert is not None else None,
        "certificate_recomputed": cert,
        "r_dt": (dt / cert) if cert is not None else None,
        "n_cells": n, "initial_state": list(x0),
        "source_cells": source_cells, "reserve_cells": reserve_cells,
        "allee_cells": allee_cells,
        "schema": SCHEMA + (P1K_EXTRA if is_p1k else []),
    }
    return meta, rows


# ---------------------------------------------------------------------------
# summary metrics (recomputed independently by test_v29_behavior.py group 8)
# ---------------------------------------------------------------------------
def _col(meta, rows, name):
    idx = meta["schema"].index(name)
    return [r[idx] for r in rows]


def _stability_class(meta, rows, world_kmax, x0):
    """Frozen dimensionless rules of Amendment 1 Sec 17.4, applied to the
    tick-indexed series V[0..N] and x[0..N] (index 0 = initial state); the
    post-burn-in window W covers indices burn..N for both series."""
    ticks, burn = meta["ticks"], meta["burn_in"]
    v_after = _col(meta, rows, "V_after")
    v_series = [rows[0][meta["schema"].index("V_before")]] + v_after
    x_series = [list(x0)] + _col(meta, rows, "x_after")
    W = v_series[burn:]
    if len(W) < 4:
        return None, None, None
    q = len(W) // 4
    quarters = [W[k * q:(k + 1) * q] for k in range(4)]
    q1, q4 = quarters[0], W[len(W) - q:]
    s0 = max(v_series[burn], 1e-3 * v_series[0], 1e-9)
    tau = (math.fsum(q4) / len(q4) - math.fsum(q1) / len(q1)) / s0
    amp = (max(q4) - min(q4)) / s0
    XW = x_series[burn:]
    bounded = max(max(abs(v) for v in xs) for xs in XW) <= 10.0 * world_kmax
    tot0 = math.fsum(x0)
    sigma = [(math.fsum(xs) / tot0 if tot0 != 0 else math.inf)
             for xs in x_series]
    sigma_w = sigma[burn:]
    sigma_q4 = sigma_w[len(sigma_w) - q:]
    qmeans = [math.fsum(qq) / len(qq) for qq in quarters]
    increasing = all(qmeans[k + 1] > qmeans[k] for k in range(3))
    if not bounded or (tau > 0.05 and increasing):
        cls = "accumulation"
    elif sigma[-1] < 0.05 and not any(s > 0.10 for s in sigma_q4):
        cls = "collapse"
    elif abs(tau) <= 0.01 and amp <= 0.01:
        cls = "converged"
    elif abs(tau) <= 0.05 and amp > 0.01:
        cls = "bounded_oscillation"
    else:
        cls = "unclassified"
    return cls, tau, amp


def _count_down_crossings(series_before, series_after):
    return sum(1 for b, a in zip(series_before, series_after) if (not b) and a)


def _recovery(fx, meta, rows, x0):
    shock = fx.get("shock")
    if not shock:
        return None
    idx_x = meta["schema"].index("x_after")
    cell = 1  # registered metric: sink stock x[1] for D6/D7
    series = [x0[cell]] + [r[idx_x][cell] for r in rows]
    burn, start = fx["burn_in"], shock["start_tick"]
    end = shock["end_tick_exclusive"]
    ref_vals = series[burn:start]
    ref = math.fsum(ref_vals) / len(ref_vals)
    thr = 0.9 * ref
    win = fx["recovery_criterion"]["sustained_window_ticks"]
    rec_tick = None
    t = end
    while t + win <= len(series):
        if all(series[s] >= thr for s in range(t, t + win)):
            rec_tick = t
            break
        t += 1
    return {"reference_mean": ref, "threshold": thr,
            "sustained_window_ticks": win,
            "recovered": rec_tick is not None, "recovery_tick": rec_tick}


def _summarize_run(fx, cell_dicts, meta, rows, x0):
    sch = meta["schema"]
    ticks, burn = meta["ticks"], meta["burn_in"]
    v_before0 = rows[0][sch.index("V_before")]
    v_after = _col(meta, rows, "V_after")
    v_post = v_after[burn:]
    xa = _col(meta, rows, "x_after")
    ineq = [r for r in _col(meta, rows, "inequality_residual") if r is not None]
    ledg = _col(meta, rows, "ledger_residual")
    lower = _col(meta, rows, "lower_violation")
    upper = _col(meta, rows, "upper_violation")
    served = _col(meta, rows, "served_valid")
    req = _col(meta, rows, "requested_demand")
    viable = _col(meta, rows, "viable_fraction")
    res_below = _col(meta, rows, "reserve_below")
    allee_below = _col(meta, rows, "allee_below")
    kmax = max(c["K"] for c in cell_dicts)
    cls, tau, amp = _stability_class(meta, rows, kmax, x0)

    first_lower = next((r[0] for r in rows if r[sch.index("lower_violation")]), None)
    first_upper = next((r[0] for r in rows if r[sch.index("upper_violation")]), None)
    inval = next((r[0] for r in rows if r[sch.index("invalid_service_flag")]), None)

    # descent violations (meaningful for undriven certified runs; recorded always)
    tol = lambda v: 1e-9 * (1.0 + abs(v))
    v_series = [v_before0] + v_after
    descent_viol = sum(1 for a, b in zip(v_series, v_series[1:]) if b > a + tol(a))

    # reserve/Allee downward crossings, counted from TRANSITIONS only,
    # starting from the initial state's below-flags (protocol Sec 8-C)
    def crossings(flag_rows, cell_idxs, threshold_key):
        if not cell_idxs:
            return 0
        prev = [x0[k] < cell_dicts[k][threshold_key] for k in cell_idxs]
        out = 0
        for fl in flag_rows:
            out += sum(1 for p, c in zip(prev, fl) if (not p) and c)
            prev = fl
        return out
    res_cross = crossings(res_below, meta["reserve_cells"], "R")
    allee_cross = crossings(allee_below, meta["allee_cells"], "A")

    # dead sources / collapse basin (Allee cells at run end)
    dead = 0
    trapped = False
    for k in meta["allee_cells"]:
        c = cell_dicts[k]
        x_end = xa[-1][k]
        cell = d0.Cell(alpha=c["alpha"], beta=c["beta"], chi=c["chi"], L=c["L"],
                       U=c["U"], R=c["R"], K=c["K"], source=c["source"],
                       rho=c["rho"], A=c["A"])
        regen_end = d0.natural_drive(cell, x_end)
        if x_end < c["A"] and regen_end <= 0.0:
            dead += 1
            q = max(1, (ticks - burn) // 4)
            tail = [xs[k] for xs in xa[ticks - q:]]
            if all(v < c["A"] for v in tail):
                trapped = True

    out = {
        **{k: meta[k] for k in ("fixture", "config", "policy",
                                "deliberately_unsafe", "covered_by_v28_theorem",
                                "dt", "ticks", "burn_in", "lv_exact",
                                "certificate_kind", "certificate_recomputed",
                                "r_dt", "initial_state")},
        "V_initial": v_before0,
        "V_final": v_after[-1],
        "V_postburn_mean": math.fsum(v_post) / len(v_post),
        "stability_class": cls, "tau_trend": tau, "amplitude": amp,
        "descent_violations": descent_viol,
        "min_state_overall": min(min(xs) for xs in xa),
        "max_state_overall": max(max(xs) for xs in xa),
        "first_material_lower_exit_tick": first_lower,
        "first_upper_exceed_tick": first_upper,
        "invalid_service_from_tick": inval,
        "physically_admissible_throughout": first_lower is None and first_upper is None,
        "requested_total": math.fsum(req),
        "served_valid_total": math.fsum(served),
        "requested_postburn": math.fsum(req[burn:]),
        "served_valid_postburn": math.fsum(served[burn:]),
        "viable_fraction_final": viable[-1],
        "viable_fraction_postburn_mean": math.fsum(viable[burn:]) / len(viable[burn:]),
        "reserve_crossings_down": res_cross,
        "allee_crossings_down": allee_cross,
        "dead_sources": dead,
        "collapse_basin_trapped": trapped,
        "transport_loss_total": math.fsum(_col(meta, rows, "transport_loss")),
        "max_inequality_residual": max(ineq) if ineq else None,
        "max_ledger_residual": max(abs(v) for v in ledg),
        "shock_recovery": _recovery(fx, meta, rows, x0),
    }
    if meta["policy"] == "P1K-diag":
        sf = _col(meta, rows, "material_shortfall")
        sp = _col(meta, rows, "material_spill")
        out["p1k_material_shortfall_ticks"] = sum(1 for v in sf if v)
        out["p1k_material_spill_ticks"] = sum(1 for v in sp if v)
        out["p1k_max_ledger_residual"] = max(
            abs(v) for v in _col(meta, rows, "p1k_ledger_residual"))
        out["eligible_for_any_physical_service_claim"] = all(
            not v for v in sf)
    # preserve-and-serve eligibility (Amendment 2 Sec 18.1 rule 3/8): never
    # claimable after a material lower exit, never claimable for P1K/P4/P2/P3
    permitted = fx.get("preserve_and_serve_claims_permitted", False)
    out["preserve_and_serve_claim_eligible"] = bool(
        permitted and meta["policy"] == "P1" and first_lower is None)
    return out


# ---------------------------------------------------------------------------
# fixture drivers
# ---------------------------------------------------------------------------
def _verify_certificate(fx_id, registered, meta):
    if registered is None or meta["certificate_recomputed"] is None:
        return
    got, want = meta["certificate_recomputed"], registered["value"]
    if abs(got - want) > 1e-9 * max(1.0, abs(want)):
        raise SystemExit(f"FATAL: {fx_id}: recomputed certificate {got!r} "
                         f"differs from registered {want!r}")
    if "r_dt" in registered:
        r = meta["r_dt"]
        if abs(r - registered["r_dt"]) > 1e-9 * max(1.0, abs(r)):
            raise SystemExit(f"FATAL: {fx_id}: r_dt {r!r} differs from "
                             f"registered {registered['r_dt']!r}")


def run_fixture(fx):
    """Run every registered policy of one fixture. Returns (runs, analyses):
    runs = list of (meta, rows); analyses = fixture-level derived records."""
    fid = fx["id"]
    runs = []
    analyses = {}

    if fid == "D5":
        for cfg in fx["configurations"]:
            for pol in fx["policies"]:
                meta, rows = _run_one(fx, cfg["cells"], fx["edges"], pol,
                                      fx["dt"], fx["initial_state"],
                                      label=cfg["config_id"])
                if pol == "P1":
                    _verify_certificate(fid, cfg["dt_certificate"], meta)
                runs.append((cfg["cells"], meta, rows))
        return runs, analyses

    if fid == "D8":
        for spec in fx["runs"]:
            meta, rows = _run_one(fx, fx["cells"], fx["edges"], spec["policy"],
                                  spec["dt"], fx["initial_state"],
                                  label=spec["label"])
            _verify_certificate(fid, {"value": fx["dt_certificate"]["value"],
                                      "r_dt": spec["r_dt"]}, meta)
            runs.append((fx["cells"], meta, rows))
        p4 = next((m, r) for c, m, r in runs if m["policy"] == "P4")
        v0 = p4[1][0][p4[0]["schema"].index("V_before")]
        v1 = p4[1][0][p4[0]["schema"].index("V_after")]
        va = _col(p4[0], p4[1], "V_after")
        analyses["D8"] = {
            "p4_V0": v0, "p4_V1": v1, "p4_tick1_ratio": v1 / v0,
            "p4_monotone_increase": all(b > a for a, b in zip([v0] + va, va)),
            "note": "P4 is the DELIBERATELY UNSAFE negative control (CE-A)",
        }
        return runs, analyses

    if fid == "D3":
        for pol in fx["policies"]:
            for tag, x0 in (("baseline", fx["initial_state"]),
                            ("perturbed", fx["initial_state_perturbed"])):
                meta, rows = _run_one(fx, fx["cells"], fx["edges"], pol,
                                      fx["dt"], x0, label=tag)
                if pol == "P1" and tag == "baseline":
                    _verify_certificate(fid, fx["dt_certificate"], meta)
                runs.append((fx["cells"], meta, rows))
        probe = fx["perturbation"]["probe_cell"]
        pair = {}
        for cells, meta, rows in runs:
            xa = _col(meta, rows, "x_after")
            pair[(meta["policy"], meta["config"])] = xa
        d3 = {}
        for pol in fx["policies"]:
            b = pair[(pol, "baseline")]
            p = pair[(pol, "perturbed")]
            diffs = [abs(pb[probe] - bb[probe]) for bb, pb in zip(b, p)]
            first = next((t + 1 for t, dv in enumerate(diffs) if dv > 1e-15), None)
            d3[pol] = {"tick1_probe_diff": diffs[0],
                       "first_probe_diff_tick": first,
                       "max_probe_diff": max(diffs)}
        analyses["D3"] = {"probe_cell": probe, "paired_probe_differences": d3,
                          "measurement": "difference between paired runs only"}
        return runs, analyses

    for pol in fx["policies"]:
        meta, rows = _run_one(fx, fx["cells"], fx["edges"], pol, fx["dt"],
                              fx["initial_state"])
        if pol == "P1":
            _verify_certificate(fid, fx["dt_certificate"], meta)
        runs.append((fx["cells"], meta, rows))

    if fid == "D2":
        by = {m["policy"]: (m, r) for c, m, r in runs}
        m1, r1 = by["P1"]
        m2, r2 = by["P2"]
        J1 = _col(m1, r1, "J")
        last_active = max((r1[t][0] for t in range(len(r1)) if J1[t][0] > 0.0),
                          default=None)
        xf = _col(m1, r1, "x_after")[-1]
        mu_f = [d0.marginal(c["alpha"], c["beta"], c["chi"], c["L"], c["U"],
                            c["R"], xf[k]) for k, c in enumerate(fx["cells"])]
        e = fx["edges"][0]
        analyses["D2"] = {
            "p1_last_active_tick": last_active,
            "p1_final_state": xf,
            "p1_final_loss_aware_force": mu_f[0] - e["eta"] * mu_f[1],
            "p1_final_loss_blind_force": mu_f[0] - mu_f[1],
            "theta": e["theta"],
            "loss_changes_decision_at_rest": (
                mu_f[0] - e["eta"] * mu_f[1] <= e["theta"]
                < mu_f[0] - mu_f[1]),
            "V_final_P1": _col(m1, r1, "V_after")[-1],
            "V_final_P2": _col(m2, r2, "V_after")[-1],
        }
    return runs, analyses


def run_all(plan):
    """Execute the full preregistered fixture set. Returns (summary, trace)."""
    plan_hash = canonical_hash(plan)
    summary_runs = []
    trace_runs = []
    analyses = {}
    for fid in FIXTURE_IDS:
        fx = plan["fixtures"][fid]
        runs, an = run_fixture(fx)
        analyses.update(an)
        for cells, meta, rows in runs:
            summary_runs.append(_summarize_run(fx, cells, meta, rows,
                                               meta["initial_state"]))
            trace_runs.append({"run_id": f"{meta['fixture']}"
                               f"/{meta['config'] or '-'}/{meta['policy']}",
                               **meta, "rows": rows})
    summary = {
        "gate": plan["gate"],
        "plan_id": plan["plan_id"],
        "plan_hash": plan_hash,
        "engine": plan["engine"],
        "interpretation_limits": (
            "Deterministic fixtures only. Results state what occurred in D1-D8 "
            "and whether registered invariants/hypotheses held IN THESE "
            "FIXTURES. No claim of general stability, scale invariance, "
            "stochastic robustness, superiority across random layouts, "
            "actor-level success, or monetary validity of EBU is made or "
            "implied (Amendment 3 Sec 19.4)."),
        "runs": summary_runs,
        "fixture_analyses": analyses,
    }
    trace = {"plan_hash": plan_hash,
             "format": "columnar: each run has 'schema' naming the per-tick "
                       "fields and 'rows' with one array per tick",
             "runs": trace_runs}
    return summary, trace


# ---------------------------------------------------------------------------
# report + persistence
# ---------------------------------------------------------------------------
def _fmt(v):
    if v is None:
        return "-"
    if isinstance(v, bool):
        return "yes" if v else "no"
    if isinstance(v, float):
        return f"{v:.6g}"
    return str(v)


def print_report(summary):
    print("=" * 78)
    print("V2.9 Gate 2 - deterministic behavioral wind tunnel (preregistered)")
    print("=" * 78)
    print(f"Python {sys.version.split()[0]}")
    print(f"plan: {summary['plan_id']}   canonical hash: {summary['plan_hash']}")
    print("Policies P2-P4 live in this harness; P1K is diagnostic only; no")
    print("stochastic seeds, no P1C, no finite actors. Global metrics are")
    print("computed after local decisions and never enter them.")
    for rec in summary["runs"]:
        tag = f"{rec['fixture']}/{rec['config'] or '-'}/{rec['policy']}"
        if rec["deliberately_unsafe"]:
            tag += "  [DELIBERATELY UNSAFE NEGATIVE CONTROL]"
        print("-" * 78)
        print(tag)
        print(f"  dt={_fmt(rec['dt'])}  r_dt={_fmt(rec['r_dt'])} "
              f"(cert={_fmt(rec['certificate_recomputed'])}, "
              f"{rec['certificate_kind'] or 'n/a'})  ticks={rec['ticks']} "
              f"burn_in={rec['burn_in']}")
        print(f"  V: initial={_fmt(rec['V_initial'])} "
              f"final={_fmt(rec['V_final'])} "
              f"postburn_mean={_fmt(rec['V_postburn_mean'])} "
              f"class={rec['stability_class']}")
        print(f"  descent violations={rec['descent_violations']}  "
              f"max ineq residual={_fmt(rec['max_inequality_residual'])}  "
              f"max ledger residual={_fmt(rec['max_ledger_residual'])}")
        print(f"  state range=[{_fmt(rec['min_state_overall'])}, "
              f"{_fmt(rec['max_state_overall'])}]  admissible throughout="
              f"{_fmt(rec['physically_admissible_throughout'])}  "
              f"lower exit tick={_fmt(rec['first_material_lower_exit_tick'])}  "
              f"upper exceed tick={_fmt(rec['first_upper_exceed_tick'])}")
        print(f"  demand: requested={_fmt(rec['requested_total'])} "
              f"served_valid={_fmt(rec['served_valid_total'])} "
              f"(postburn {_fmt(rec['served_valid_postburn'])}/"
              f"{_fmt(rec['requested_postburn'])})  invalid from tick="
              f"{_fmt(rec['invalid_service_from_tick'])}")
        print(f"  viability: final={_fmt(rec['viable_fraction_final'])} "
              f"postburn_mean={_fmt(rec['viable_fraction_postburn_mean'])}  "
              f"reserve crossings={rec['reserve_crossings_down']}  "
              f"allee crossings={rec['allee_crossings_down']}  dead sources="
              f"{rec['dead_sources']}  trapped={_fmt(rec['collapse_basin_trapped'])}")
        print(f"  transport loss total={_fmt(rec['transport_loss_total'])}")
        if rec["shock_recovery"]:
            sr = rec["shock_recovery"]
            print(f"  shock: reference={_fmt(sr['reference_mean'])} "
                  f"recovered={_fmt(sr['recovered'])} "
                  f"recovery tick={_fmt(sr['recovery_tick'])} "
                  f"(sustained {sr['sustained_window_ticks']} ticks required)")
        if rec["policy"] == "P1K-diag":
            print(f"  P1K DIAGNOSTIC ONLY: material shortfall ticks="
                  f"{rec['p1k_material_shortfall_ticks']}, material spill "
                  f"ticks={rec['p1k_material_spill_ticks']}; ledger closes by "
                  f"construction and never certifies physical availability")
        print(f"  preserve-and-serve claim eligible="
              f"{_fmt(rec['preserve_and_serve_claim_eligible'])}")
    print("-" * 78)
    print("fixture analyses:")
    print(json.dumps(summary["fixture_analyses"], indent=2, sort_keys=True))
    print("-" * 78)
    print("Interpretation limits: " + summary["interpretation_limits"])


def write_outputs(summary, trace):
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(SUMMARY_PATH, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=1, sort_keys=False)
        fh.write("\n")
    blob = json.dumps(trace, separators=(",", ":")).encode("utf-8")
    if len(blob) > TRACE_GZ_THRESHOLD:
        path = TRACE_PATH + ".gz"
        with open(path, "wb") as fh:
            with gzip.GzipFile(fileobj=fh, mode="wb", mtime=0) as gz:
                gz.write(blob)
        note = f"trace written gzip-compressed (stdlib gzip, mtime=0): {path}"
    else:
        path = TRACE_PATH
        with open(path, "wb") as fh:
            fh.write(blob)
        note = f"trace written: {path}"
    print(f"summary written: {SUMMARY_PATH}")
    print(note)
    print(f"trace size (uncompressed JSON): {len(blob)} bytes")


def main():
    plan, plan_hash = load_plan()
    summary, trace = run_all(plan)
    print_report(summary)
    write_outputs(summary, trace)


if __name__ == "__main__":
    main()
