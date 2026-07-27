"""
V2.9 Gate 2.4 - locked D9/D10 preservation study harness.

Executes ONLY the fixtures preregistered in v29_d9_d10_plan.json (Amendment 5,
Sec 21), whose canonical SHA-256 is locked below. The harness recomputes the
plan hash and refuses to run on mismatch; there is NO command-line option to
disable the check, override a parameter, run a subset, or overwrite completed
results.

Policies reuse the frozen substrate (no physical equation is duplicated):
  P0    no transport (d0 natural dynamics only)
  P1    unconstrained loss-aware D0            (d0_v29.d0_step, chi=0)
  soft  unconstrained D0 with reserve penalty  (d0_v29.d0_step, chi>0)
  P1C   hard aggregate preservation cap        (p1c_v29.p1c_step)

Every dynamical parameter comes from the JSON plan; missing required fields are a
hard error (no hidden defaults). Global metrics (viability, classification,
O_physical) are computed ONLY after each tick's local decisions and physical
update - never on the decision path.

O_physical = sum_n dt*[Q_i^n - Q_max^n]_+ is a PHYSICAL OVER-USE DIAGNOSTIC
(evaluation only). It is NOT issued ecological debt and NOT EBU; no debt ledger,
wallet, or scalarisation exists in this module.

This module is IMPORT-SAFE: importing it runs no fixture, writes no file, and
mutates no state. The study runs only via `main()` / direct execution:
  mkdir -p results/v2.9/d9_d10
  python3 exp_v29_d9_d10.py > results/v2.9/d9_d10/v29_d9_d10_stdout.txt

Standard library only.
"""
from __future__ import annotations
import gzip
import hashlib
import json
import math
import os
import sys

import d0_v29 as d0
import p1c_v29 as p1c

PLAN_PATH = "v29_d9_d10_plan.json"
EXPECTED_PLAN_HASH = "87ad0ae2eb3cca6d86a56378c4a76508b29d7a63cb39ac74f5a362be1004c34a"
OUT_DIR = os.path.join("results", "v2.9", "d9_d10")
SUMMARY_PATH = os.path.join(OUT_DIR, "v29_d9_d10_summary.json")
TRACE_PATH = os.path.join(OUT_DIR, "v29_d9_d10_trace.jsonl")
TRACE_GZ_THRESHOLD = 10 * 1024 * 1024   # gzip (stdlib, documented) above 10 MiB

POLICIES = ("P0", "P1", "soft", "P1C")

# per-tick columnar record fields (section 10)
TICK_FIELDS = [
    "tick", "x_before", "x_after", "u", "requested_export", "safe_budget",
    "accepted_export", "delivered_service", "transport_loss", "unmet_demand",
    "source_state", "reserve_crossed", "allee_crossed", "locally_infeasible",
    "p1c_binding", "ledger_residual", "theorem_eligible", "theorem_ok",
]


# ---------------------------------------------------------------------------
# canonical hashing + plan loading (no hidden defaults)
# ---------------------------------------------------------------------------
def canonical_hash(plan: dict) -> str:
    blob = json.dumps(plan, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def load_plan(base_dir: str = ".") -> tuple[dict, str]:
    with open(os.path.join(base_dir, PLAN_PATH), encoding="utf-8") as fh:
        plan = json.load(fh)
    got = canonical_hash(plan)
    if got != EXPECTED_PLAN_HASH:
        raise SystemExit(
            "FATAL: canonical plan hash mismatch - the plan file differs from "
            f"the preregistered Amendment-5 hash.\n  plan: {got}\n  "
            f"registered: {EXPECTED_PLAN_HASH}\nRefusing to run.")
    return plan, got


def _req(d: dict, key: str, where: str):
    """Fetch a required field; a missing field is a hard error (no default)."""
    if key not in d:
        raise KeyError(f"required plan field '{key}' missing in {where}")
    return d[key]


# ---------------------------------------------------------------------------
# run specifications reconstructed from the plan (NO execution here)
# ---------------------------------------------------------------------------
def _allee_g(rho, K, A, x):
    return rho * x * (1.0 - x / K) * (x / A - 1.0)


def _logistic_g(rho, K, x):
    return rho * x * (1.0 - x / K)


def build_d9_runs(plan: dict) -> list[dict]:
    """Reconstruct the four D9 arms field-by-field from the plan."""
    D9 = _req(plan, "D9", "plan")
    cp = _req(D9, "cell_parameters", "D9")
    sc = _req(cp, "source_common", "D9.cell_parameters")
    srcR = _req(cp, "source_R_by_arm", "D9.cell_parameters")
    snk = _req(cp, "sink", "D9.cell_parameters")
    edge = _req(D9, "topology", "D9")["edges"][0]
    x0 = _req(D9, "initial_state", "D9")
    dt = _req(D9, "dt", "D9")
    ticks = _req(D9, "ticks", "D9")
    burn = _req(D9, "burn_in", "D9")
    persist = _req(D9, "persistence_window", "D9")
    R_eff = _req(_req(D9, "effective_reserve", "D9"), "R_eff", "D9.effective_reserve")
    pol = _req(D9, "policies", "D9")
    runs = []
    for arm_id, spec in (("D9-A", pol["D9-A_reserve_blind"]),
                         ("D9-B", pol["D9-B_soft"]),
                         ("D9-C", pol["D9-C_soft_plus_hardcap"]),
                         ("D9-D", pol["D9-D_blind_plus_hardcap"])):
        chi = _req(spec, "chi", arm_id)
        hard = _req(spec, "hard_cap", arm_id)
        cell_R = _req(spec, "Cell_R", arm_id)
        # sanity: Cell_R matches the by-arm table
        want_R = srcR["chi1_arms"] if chi > 0 else srcR["chi0_arms"]
        if cell_R != want_R:
            raise ValueError(f"{arm_id}: Cell_R {cell_R} != table {want_R}")
        runs.append({
            "run_id": arm_id, "experiment": "D9",
            "policy": ("P1C" if hard else ("soft" if chi > 0 else "P1")),
            "chi": chi, "hard_cap": hard,
            "source": dict(sc, chi=chi, R=cell_R),
            "sink": dict(snk),
            "edge": dict(edge),
            "x0": list(x0), "dt": dt, "ticks": ticks, "burn_in": burn,
            "persistence": persist, "R_eff": R_eff, "eps_x": 0.0, "eps_u": 0.0,
            "source_type": "regenerative",
            "params_note": f"D9 {arm_id}: chi={chi}, hard_cap={hard}",
        })
    return runs


def build_d10_runs(plan: dict) -> list[dict]:
    """Reconstruct the 140 D10 runs (80 core + 60 secondary) from the plan.
    Registered run identities are preserved even when parameter blocks coincide;
    no deduplication is performed."""
    D10 = _req(plan, "D10", "plan")
    world = _req(D10, "world", "D10")
    src_t = _req(world, "source", "D10.world")
    snk_t = _req(world, "sink", "D10.world")
    x0 = _req(world, "initial_state", "D10.world")
    ticks = _req(world, "ticks", "D10.world")
    burn = _req(world, "burn_in", "D10.world")
    persist = _req(world, "persistence_window", "D10.world")
    K = _req(src_t, "K", "D10.world.source")
    sd = _req(_req(D10, "source_dynamics", "D10"), "rho_default", "D10.source_dynamics")
    axes = _req(D10, "axes", "D10")
    prim = _req(axes, "primary", "D10.axes")
    ref = _req(axes, "secondary_reference_point", "D10.axes")
    slices = _req(axes, "secondary_slices", "D10.axes")
    R_eff_default = _req(_req(D10, "effective_reserve", "D10"), "R_eff_default",
                         "D10.effective_reserve")

    dg_levels = _req(prim["d_over_gmax"], "levels", "D10 d_over_gmax")
    eta_levels = _req(prim["eta"], "levels", "D10 eta")

    def make_run(rid, dg, eta, theta, delta, chi_soft, rho, r_dt, policy,
                 demand_override=None):
        g_max = rho * K / 4.0
        # demand: normally d = (d/gmax)*g_max; the rho slice HOLDS d at the
        # reference value (plan D10 rho-slice) so d/gmax varies with rho and the
        # slice deliberately crosses feasibility.
        if demand_override is not None:
            d = demand_override
            dg = d / g_max
        else:
            d = dg * g_max
        R_eff = K / 2.0 + delta
        # chi for THIS policy: soft uses chi_soft; P1C uses chi_soft only within
        # the chi slice (else 0); P0/P1 use 0.
        if policy == "soft":
            chi = chi_soft
        elif policy == "P1C":
            chi = chi_soft if rid_is_chi_slice(rid) else 0.0
        else:
            chi = 0.0
        cell_R = R_eff if chi > 0 else 0.0
        return {
            "run_id": rid, "experiment": "D10", "policy": policy,
            "d_over_gmax": dg, "eta": eta, "theta": theta, "delta": delta,
            "chi": chi, "rho": rho, "r_dt": r_dt,
            "d": d, "g_max": g_max, "R_eff": R_eff, "K": K,
            "source": dict(src_t, chi=chi, R=cell_R, rho=rho, K=K, A=0.0,
                           source="logistic"),
            "sink": dict(snk_t, d=d),
            "edge": {"i": 0, "j": 1, "M": 1.0, "theta": theta, "eta": eta},
            "x0": list(x0), "ticks": ticks, "burn_in": burn,
            "persistence": persist, "R_eff_pres": R_eff,
            "eps_x": 0.0, "eps_u": 0.0, "source_type": "regenerative",
        }

    def rid_is_chi_slice(rid):
        return rid.startswith("D10-slice=chi/")

    runs = []
    # core map: 5 d/gmax x 4 eta x 4 policies = 80
    th0 = _req(ref, "theta", "ref"); de0 = _req(ref, "delta", "ref")
    chi0 = _req(ref, "chi", "ref"); rd0 = _req(ref, "r_dt", "ref")
    for dg in dg_levels:
        for eta in eta_levels:
            for pol in POLICIES:
                rid = f"D10-core/dg={dg}/eta={eta}/{pol}"
                runs.append(make_run(rid, dg, eta, th0, de0, chi0, sd, rd0, pol))
    # secondary slices: 5 x 3 x 4 = 60
    dg_ref = _req(ref, "d_over_gmax", "ref"); eta_ref = _req(ref, "eta", "ref")
    reference_d = dg_ref * (sd * K / 4.0)   # held demand for the rho slice (=2.7)
    slice_axis = {
        "theta": ("theta", slices["theta"]["levels"]),
        "delta_over_K": ("delta_over_K", slices["delta_over_K"]["levels"]),
        "chi": ("chi", slices["chi"]["levels"]),
        "rho": ("rho", slices["rho"]["levels"]),
        "r_dt": ("r_dt", slices["r_dt"]["levels"]),
    }
    for axis_name, (_key, levels) in slice_axis.items():
        for lvl in levels:
            for pol in POLICIES:
                rid = f"D10-slice={axis_name}/level={lvl}/{pol}"
                # start from reference, override the sliced axis
                theta = th0; delta = de0; chi_soft = chi0; rho = sd; r_dt = rd0
                if axis_name == "theta":
                    theta = lvl
                elif axis_name == "delta_over_K":
                    delta = lvl * K
                elif axis_name == "chi":
                    chi_soft = lvl
                elif axis_name == "rho":
                    rho = lvl
                elif axis_name == "r_dt":
                    r_dt = lvl
                # rho slice holds demand at the reference d (plan); others derive d
                dov = reference_d if axis_name == "rho" else None
                runs.append(make_run(rid, dg_ref, eta_ref, theta, delta,
                                     chi_soft, rho, r_dt, pol, demand_override=dov))
    return runs


def _req_K(K):
    return K


# ---------------------------------------------------------------------------
# timestep resolution (shared across policies at a grid point)
# ---------------------------------------------------------------------------
def _worlds_for_run(spec: dict):
    """Build (world, world_no_edges, src_cell, source_config)."""
    s = spec["source"]
    src = d0.Cell(alpha=s["alpha"], beta=s["beta"], chi=s["chi"], L=s["L"],
                  U=s["U"], R=s["R"], K=s["K"], s=s.get("s", 0.0),
                  d=s.get("d", 0.0), lam=s.get("lam", 0.0),
                  kappa=s.get("kappa", 0.0), source=s["source"],
                  rho=s.get("rho", 0.0), A=s.get("A", 0.0))
    k = spec["sink"]
    snk = d0.Cell(alpha=k["alpha"], beta=k["beta"], chi=k["chi"], L=k["L"],
                  U=k["U"], R=k["R"], K=k["K"], s=k.get("s", 0.0),
                  d=k.get("d", 0.0), lam=k.get("lam", 0.0),
                  kappa=k.get("kappa", 0.0), source=k.get("source", "none"),
                  rho=k.get("rho", 0.0), A=k.get("A", 0.0))
    e = spec["edge"]
    edge = d0.Edge(e["i"], e["j"], e["M"], e["theta"], e["eta"])
    world = d0.World(cells=(src, snk), edges=(edge,))
    world0 = d0.World(cells=(src, snk), edges=())
    R_eff = spec.get("R_eff", spec.get("R_eff_pres"))
    cfg = p1c.SourceConfig(0, spec["source_type"], R_eff=R_eff,
                           eps_x=spec["eps_x"], eps_u=spec["eps_u"])
    return world, world0, src, snk, edge, cfg


def resolve_dt(spec: dict) -> float:
    """D9 uses the fixed registered dt; D10 derives dt = r_dt * cert, computed on
    the MOST RESTRICTIVE (largest-chi) world at the grid point so all four
    policies share one dt (static Gershgorin certificate; no state advance)."""
    if spec["experiment"] == "D9":
        return spec["dt"]
    # D10: build the soft-arm (chi = chi at this point, largest L_V) world to
    # get the binding certificate. chi_soft = the run's chi if it is the soft/P1C
    # chi; use max(chi_ref, run chi) to be safe.
    s = spec["source"]
    chi_bind = max(s["chi"], spec.get("chi", 0.0))
    src = d0.Cell(alpha=s["alpha"], beta=s["beta"], chi=chi_bind, L=s["L"],
                  U=s["U"], R=(spec["R_eff"] if chi_bind > 0 else 0.0), K=s["K"],
                  source="logistic", rho=s["rho"])
    k = spec["sink"]
    snk = d0.Cell(alpha=k["alpha"], beta=k["beta"], chi=0.0, L=k["L"], U=k["U"],
                  R=0.0, K=k["K"], d=k["d"])
    e = spec["edge"]
    w = d0.World(cells=(src, snk), edges=(d0.Edge(e["i"], e["j"], e["M"],
                                                  e["theta"], e["eta"]),))
    cert = d0.gershgorin_dt_certificate(w)
    return spec["r_dt"] * cert


# ---------------------------------------------------------------------------
# single-tick step (testable without a full trajectory)
# ---------------------------------------------------------------------------
def step_once(spec: dict, x: list[float], dt: float, cfg: p1c.SourceConfig,
              world: d0.World, world0: d0.World) -> dict:
    """Execute exactly one tick under the run's policy; return a metric record.
    Global/evaluation quantities are computed only AFTER the local decision."""
    policy = spec["policy"]
    src = world.cells[0]
    e = world.edges[0]
    eta = e.eta
    # --- local decision + physical update ---
    if policy == "P0":
        res = d0.d0_step(world0, x, dt, diagnostics=False)
        x_after = list(res.x_after)
        u = list(res.u)
        req = acc = 0.0
        loss = 0.0
        binding = False
        th_elig = th_ok = None
    elif policy in ("P1", "soft"):
        res = d0.d0_step(world, x, dt, diagnostics=False)
        x_after = list(res.x_after)
        u = list(res.u)
        req = res.J[0]            # aggregate source export (one out-edge)
        acc = req                # unconstrained: accepted == requested
        loss = res.transport_loss
        binding = False
        th_elig = th_ok = None
    elif policy == "P1C":
        tr = p1c.p1c_step(world, x, dt, {0: cfg}, diagnostics=False)
        x_after = list(tr.x_after)
        u = list(tr.u)
        ed = tr.edges[0]
        req = ed.q_req
        acc = ed.q_acc
        loss = tr.total_loss
        binding = tr.sources[0].sigma < 1.0 and tr.sources[0].Q_req > 0
        th_elig = tr.theorem_assumptions_hold
        th_ok = tr.theorem_conclusion_observed
    else:
        raise ValueError(f"unregistered policy {policy!r}")
    # --- evaluation-only diagnostics (after decision + update) ---
    delivered = eta * acc
    demand = world.cells[1].d
    unmet = max(0.0, demand - delivered)
    u_src = u[0]
    # source preservation state (evaluation label for all arms)
    state = p1c.classify_state(cfg, x[0], u_src, dt)
    # safe budget the source WOULD have (evaluation)
    safe_budget = p1c.robust_budget(cfg, x[0], u_src, dt)
    # reserve / Allee crossings on the SOURCE
    R_eff = cfg.R_eff
    A = src.A
    reserve_crossed = (x[0] >= R_eff) and (x_after[0] < R_eff)
    allee_crossed = (A > 0.0) and (x[0] >= A) and (x_after[0] < A)
    locally_infeasible = (state == "I")
    # ledger residual
    ledger = (math.fsum(x_after) - math.fsum(x)) - (dt * math.fsum(u) - loss)
    return {
        "x_before": list(x), "x_after": x_after, "u": u,
        "requested_export": req, "safe_budget": safe_budget,
        "accepted_export": acc, "delivered_service": delivered,
        "transport_loss": loss, "unmet_demand": unmet,
        "source_state": state, "reserve_crossed": reserve_crossed,
        "allee_crossed": allee_crossed, "locally_infeasible": locally_infeasible,
        "p1c_binding": binding, "ledger_residual": ledger,
        "theorem_eligible": th_elig, "theorem_ok": th_ok,
    }


# ---------------------------------------------------------------------------
# service / overuse formulas (pure; testable)
# ---------------------------------------------------------------------------
def delivered_service(eta: float, q_accepted: float) -> float:
    return eta * q_accepted


def overuse_increment(dt: float, Q_i: float, Q_max: float) -> float:
    """dt * [Q_i - Q_max]_+ ; the registered physical over-use diagnostic."""
    d = Q_i - Q_max
    return dt * d if d > 0.0 else 0.0


# ---------------------------------------------------------------------------
# classification (first-match precedence; testable with synthetic records)
# ---------------------------------------------------------------------------
CLASS_TOL = {
    "tol_overuse": 1e-9, "service_threshold": 0.9, "reserve_tol": 1e-9,
    "dead_stock_threshold": 1.0,
}


def classify(metrics: dict) -> str:
    """Ordered first-match classification (D10 §17). `metrics` is the aggregate
    per-run record with the frozen fields below."""
    tol = CLASS_TOL
    dead = (metrics["final_source_stock"] < tol["dead_stock_threshold"]
            and metrics["final_source_regen"] <= 0.0)
    persistent_reserve_fail = (metrics["time_below_reserve"]
                               >= metrics["persistence_window"])
    if dead or persistent_reserve_fail:
        return "collapse"
    if metrics["locally_infeasible_ticks"] > 0:
        return "locally_infeasible"
    if (metrics["cumulative_delivered"] > 0.0
            and metrics["O_physical"] > tol["tol_overuse"]):
        return "debt_overuse_service"
    reserve_preserved = (metrics["reserve_crossings"] == 0
                         and metrics["O_physical"] <= tol["tol_overuse"])
    if reserve_preserved:
        served = metrics["postburn_mean_delivered"]
        demand = metrics["demand"]
        if demand <= 0.0 or served >= tol["service_threshold"] * demand:
            return "safe_service"
        return "safe_rationing"
    # falls through only if a reserve crossing occurred without overuse and
    # without infeasibility/persistence - a registered F-D10-2 anomaly (reported)
    return "unclassified"


# ---------------------------------------------------------------------------
# full single run (executes a trajectory - NOT called by Phase-A tests)
# ---------------------------------------------------------------------------
def run_trajectory(spec: dict) -> tuple[dict, list[dict]]:
    world, world0, src, snk, edge, cfg = _worlds_for_run(spec)
    dt = resolve_dt(spec)
    ticks = spec["ticks"]
    burn = spec["burn_in"]
    persist = spec["persistence"]
    R_eff = cfg.R_eff
    A = src.A
    x = list(spec["x0"])
    rows = []
    # aggregates
    reserve_crossings = 0
    first_reserve_tick = None
    allee_crossings = 0
    first_allee_tick = None
    time_below_reserve = 0
    time_below_allee = 0
    infeasible_ticks = 0
    binding_ticks = 0
    cum_loss = 0.0
    cum_req = 0.0
    cum_delivered = 0.0
    cum_unmet = 0.0
    O_physical = 0.0
    min_source = x[0]
    max_ledger = 0.0
    th_elig_ticks = 0
    th_violations = 0
    viab_series = []
    delivered_series = []
    for t in range(1, ticks + 1):
        rec = step_once(spec, x, dt, cfg, world, world0)
        # aggregate
        if rec["reserve_crossed"]:
            reserve_crossings += 1
            if first_reserve_tick is None:
                first_reserve_tick = t
        if rec["allee_crossed"]:
            allee_crossings += 1
            if first_allee_tick is None:
                first_allee_tick = t
        xa = rec["x_after"]
        if xa[0] < R_eff:
            time_below_reserve += 1
        if A > 0.0 and xa[0] < A:
            time_below_allee += 1
        if rec["locally_infeasible"]:
            infeasible_ticks += 1
        if rec["p1c_binding"]:
            binding_ticks += 1
        # transport_loss from d0/p1c is already an AMOUNT (dt*sum(1-eta)J);
        # cum_loss is summed from rows after the loop.
        cum_req += dt * rec["requested_export"]
        cum_delivered += dt * rec["delivered_service"]
        cum_unmet += dt * rec["unmet_demand"]
        O_physical += overuse_increment(dt, rec["accepted_export"],
                                        rec["safe_budget"])
        min_source = min(min_source, xa[0])
        max_ledger = max(max_ledger, abs(rec["ledger_residual"]))
        if rec["theorem_eligible"]:
            th_elig_ticks += 1
            if rec["theorem_ok"] is False:
                th_violations += 1
        viab = (int(xa[0] >= src.L) + int(xa[1] >= snk.L)) / 2.0
        viab_series.append(viab)
        delivered_series.append(rec["delivered_service"])
        rows.append({"tick": t, **rec})
        x = xa
    cum_loss = math.fsum(r["transport_loss"] for r in rows)
    final_src = x[0]
    final_regen = (_allee_g(src.rho, src.K, src.A, final_src) if src.source == "allee"
                   else _logistic_g(src.rho, src.K, final_src) if src.source == "logistic"
                   else 0.0)
    post = slice(burn, ticks)
    postburn_viab = viab_series[burn:]
    postburn_deliv = delivered_series[burn:]
    demand = snk.d
    agg = {
        "run_id": spec["run_id"], "experiment": spec["experiment"],
        "policy": spec["policy"], "dt": dt, "ticks": ticks, "burn_in": burn,
        "persistence_window": persist, "R_eff": R_eff, "A": A,
        "demand": demand,
        "chi": spec.get("chi"), "hard_cap": spec.get("hard_cap", spec["policy"] == "P1C"),
        "d_over_gmax": spec.get("d_over_gmax"), "eta": spec.get("eta"),
        "theta": spec.get("theta"), "delta": spec.get("delta"),
        "rho": spec.get("rho"), "r_dt": spec.get("r_dt"),
        "reserve_crossings": reserve_crossings,
        "first_reserve_crossing_tick": first_reserve_tick,
        "allee_crossings": allee_crossings,
        "first_allee_crossing_tick": first_allee_tick,
        "time_below_reserve": time_below_reserve,
        "time_below_allee": time_below_allee,
        "locally_infeasible_ticks": infeasible_ticks,
        "p1c_binding_ticks": binding_ticks,
        "p1c_binding_fraction": binding_ticks / ticks,
        "cumulative_transport_loss": cum_loss,
        "cumulative_requested_service": cum_req,
        "cumulative_delivered": cum_delivered,
        "cumulative_unmet_demand": cum_unmet,
        "O_physical": O_physical,
        "min_source_stock": min_source,
        "final_source_stock": final_src,
        "final_source_regen": final_regen,
        "final_viability": viab_series[-1],
        "postburn_mean_viability": math.fsum(postburn_viab) / len(postburn_viab),
        "final_delivered": delivered_series[-1],
        "postburn_mean_delivered": math.fsum(postburn_deliv) / len(postburn_deliv),
        "max_ledger_residual": max_ledger,
        "theorem_eligible_ticks": th_elig_ticks,
        "theorem_violation_count": th_violations,
    }
    agg["primary_classification"] = classify(agg)
    return agg, rows


# ---------------------------------------------------------------------------
# study execution (official command only)
# ---------------------------------------------------------------------------
def all_run_specs(plan: dict) -> list[dict]:
    specs = build_d9_runs(plan) + build_d10_runs(plan)
    ids = [s["run_id"] for s in specs]
    if len(ids) != 144:
        raise SystemExit(f"FATAL: expected 144 registered runs, got {len(ids)}")
    if len(set(ids)) != 144:
        raise SystemExit("FATAL: duplicate run identifiers")
    return specs


def _refuse_if_results_exist():
    existing = [p for p in (SUMMARY_PATH, TRACE_PATH, TRACE_PATH + ".gz")
                if os.path.exists(p)]
    if existing:
        raise SystemExit(
            "FATAL: completed result artifacts already exist "
            f"({existing}); refusing to overwrite a confirmatory study.")


def _fmt(v):
    if v is None:
        return "-"
    if isinstance(v, bool):
        return "yes" if v else "no"
    if isinstance(v, float):
        return f"{v:.6g}"
    return str(v)


def main():
    if any(a not in ("",) for a in sys.argv[1:]):
        raise SystemExit("FATAL: this confirmatory command takes NO options "
                         "(no --overwrite/--tune/--subset/parameter override).")
    plan, plan_hash = load_plan()
    _refuse_if_results_exist()
    os.makedirs(OUT_DIR, exist_ok=True)
    specs = all_run_specs(plan)
    pyver = sys.version.split()[0]
    impl_commit = os.environ.get("EBP_IMPL_COMMIT", "unrecorded")

    print("=" * 78)
    print("V2.9 Gate 2.4 - locked D9/D10 preservation study (single execution)")
    print("=" * 78)
    print(f"Python {pyver}   plan hash {plan_hash}")
    print(f"registered runs: {len(specs)} (D9=4, D10=140); executing in order")
    print("O_physical is a PHYSICAL OVER-USE DIAGNOSTIC, not issued EBU/debt.")
    print("No global stability / sustainability / dominance is proved by this map.")

    summary_runs = []
    all_rows = []
    for spec in specs:
        agg, rows = run_trajectory(spec)
        agg["plan_hash"] = plan_hash
        agg["python"] = pyver
        agg["impl_commit"] = impl_commit
        summary_runs.append(agg)
        all_rows.append({"run_id": spec["run_id"], "schema": TICK_FIELDS,
                         "rows": [[r[f] for f in TICK_FIELDS] for r in rows]})

    # ---- D9 report ----
    print("-" * 78)
    print("D9 - Allee reserve-stress (4 arms)")
    d9 = [r for r in summary_runs if r["experiment"] == "D9"]
    for r in d9:
        print(f"  {r['run_id']} [{r['policy']} chi={_fmt(r['chi'])} "
              f"cap={_fmt(r['hard_cap'])}]  class={r['primary_classification']}")
        print(f"    reserve_crossings={r['reserve_crossings']} "
              f"(first tick {_fmt(r['first_reserve_crossing_tick'])})  "
              f"allee_crossings={r['allee_crossings']} "
              f"(first {_fmt(r['first_allee_crossing_tick'])})")
        print(f"    min_source={_fmt(r['min_source_stock'])} "
              f"final_source={_fmt(r['final_source_stock'])}  "
              f"binding_ticks={r['p1c_binding_ticks']}")
        print(f"    delivered(cum)={_fmt(r['cumulative_delivered'])} "
              f"unmet(cum)={_fmt(r['cumulative_unmet_demand'])} "
              f"O_physical={_fmt(r['O_physical'])}  "
              f"postburn_viab={_fmt(r['postburn_mean_viability'])}")
        print(f"    theorem_eligible={r['theorem_eligible_ticks']} "
              f"violations={r['theorem_violation_count']}  "
              f"max_ledger={_fmt(r['max_ledger_residual'])}")

    # ---- D10 report ----
    print("-" * 78)
    print("D10 - service-vs-preservation phase map (140 runs)")
    d10 = [r for r in summary_runs if r["experiment"] == "D10"]
    from collections import Counter
    by_pol = {}
    for pol in POLICIES:
        c = Counter(r["primary_classification"] for r in d10 if r["policy"] == pol)
        by_pol[pol] = c
        print(f"  {pol:5s}: " + ", ".join(f"{k}={v}" for k, v in sorted(c.items())))
    print("  core map (d/gmax x eta) primary class by policy:")
    core = [r for r in d10 if r["run_id"].startswith("D10-core/")]
    dgs = sorted({r["d_over_gmax"] for r in core})
    etas = sorted({r["eta"] for r in core})
    for pol in POLICIES:
        print(f"    [{pol}]")
        for dg in dgs:
            cells = []
            for eta in etas:
                m = next(r for r in core if r["d_over_gmax"] == dg
                         and r["eta"] == eta and r["policy"] == pol)
                cells.append(f"eta{eta}:{m['primary_classification'][:5]}")
            print(f"      d/gmax={dg}: " + "  ".join(cells))
    print(f"  total O_physical>0 runs: "
          f"{sum(1 for r in d10 if r['O_physical'] > 1e-9)}")
    print(f"  collapse runs: {sum(1 for r in d10 if r['primary_classification']=='collapse')}  "
          f"unclassified: {sum(1 for r in d10 if r['primary_classification']=='unclassified')}")

    # ---- persist artifacts ----
    summary = {
        "gate": "V2.9 Gate 2.4 - locked D9/D10 study",
        "plan_hash": plan_hash, "python": pyver, "impl_commit": impl_commit,
        "n_runs": len(summary_runs),
        "classification_tolerances": CLASS_TOL,
        "O_physical_note": "physical over-use diagnostic, NOT issued EBU/debt",
        "interpretation_limits": "deterministic map; no general dominance, "
        "universal sustainability, or proof is claimed.",
        "runs": summary_runs,
    }
    with open(SUMMARY_PATH, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=1)
        fh.write("\n")
    # trace as JSONL (one run per line); gzip if large (documented, no data lost)
    blob = "\n".join(json.dumps(r, separators=(",", ":")) for r in all_rows) + "\n"
    raw = blob.encode("utf-8")
    if len(raw) > TRACE_GZ_THRESHOLD:
        path = TRACE_PATH + ".gz"
        with open(path, "wb") as fh:
            with gzip.GzipFile(fileobj=fh, mode="wb", mtime=0) as gz:
                gz.write(raw)
        trace_written = path
    else:
        path = TRACE_PATH
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(blob)
        trace_written = path
    print("-" * 78)
    print(f"summary written: {SUMMARY_PATH} ({len(summary_runs)} runs)")
    print(f"trace written:   {trace_written} ({len(raw)} bytes uncompressed JSONL)")
    print("done.")


if __name__ == "__main__":
    main()
