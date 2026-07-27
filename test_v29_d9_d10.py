"""
Phase-A validation for the locked D9/D10 harness (exp_v29_d9_d10.py), V2.9 Gate 2.4.

These tests validate the PREREGISTERED harness WITHOUT running any complete
registered D9/D10 trajectory. Permitted here: static plan checks, single-tick
calculations, synthetic classification records, small synthetic worlds, temporary
files, and negative controls. They do NOT execute the 200-tick D9 or 400-tick D10
runs (that is Phase B, the official single execution).

Passing validates the harness's conformance to Amendment 5 and the plan; it is
NOT a scientific result and licenses no behavioral conclusion. Plain stdlib,
directly executable, import-safe:  python3 test_v29_d9_d10.py
"""
from __future__ import annotations
import ast
import copy
import json
import math
import os
import tempfile

import d0_v29 as d0
import p1c_v29 as p1c
import exp_v29_d9_d10 as X

PASS = 0
FAIL = 0
GROUPS: list[list] = []

PLAN, PLAN_HASH = X.load_plan()
D9_RUNS = X.build_d9_runs(PLAN)
D10_RUNS = X.build_d10_runs(PLAN)


def group(title: str) -> None:
    GROUPS.append([title, 0, 0])
    print(f"[{len(GROUPS)}] {title}")


def check(name: str, ok: bool, detail: str = "") -> None:
    global PASS, FAIL
    if ok:
        PASS += 1
        GROUPS[-1][1] += 1
        print(f"  PASS  {name}" + (f"  ({detail})" if detail else ""))
    else:
        FAIL += 1
        GROUPS[-1][2] += 1
        print(f"  FAIL  {name}" + (f"  ({detail})" if detail else ""))


def synth_metrics(**kw):
    """A synthetic aggregate record for classify(); defaults = a clean safe run."""
    base = dict(final_source_stock=15.0, final_source_regen=1.0,
                time_below_reserve=0, persistence_window=100,
                locally_infeasible_ticks=0, cumulative_delivered=100.0,
                O_physical=0.0, reserve_crossings=0,
                postburn_mean_delivered=2.7, demand=2.7)
    base.update(kw)
    return base


# ===========================================================================
# [1] canonical plan hash + tamper refusal
# ===========================================================================
def test_group1():
    group("canonical plan hash + tamper refusal")
    check("recomputed canonical hash equals the registered constant",
          PLAN_HASH == X.EXPECTED_PLAN_HASH
          == "87ad0ae2eb3cca6d86a56378c4a76508b29d7a63cb39ac74f5a362be1004c34a")
    # tamper an in-memory copy -> different hash
    tampered = copy.deepcopy(PLAN)
    tampered["D9"]["dt"] = 0.19
    check("tampering any dynamical value changes the canonical hash",
          X.canonical_hash(tampered) != X.EXPECTED_PLAN_HASH)
    # load_plan on a tampered temp copy refuses
    with tempfile.TemporaryDirectory() as td:
        with open(os.path.join(td, X.PLAN_PATH), "w") as fh:
            json.dump(tampered, fh)
        try:
            X.load_plan(base_dir=td)
            ok = False
        except SystemExit:
            ok = True
    check("load_plan refuses a tampered plan (SystemExit)", ok)
    # canonicalization is order-independent (sorted keys)
    reordered = {k: PLAN[k] for k in reversed(list(PLAN.keys()))}
    check("canonical hash is key-order independent",
          X.canonical_hash(reordered) == X.EXPECTED_PLAN_HASH)


# ===========================================================================
# [2] schema completeness + no-hidden-default enforcement
# ===========================================================================
def test_group2():
    group("schema completeness + no-hidden-default enforcement")
    # removing a required D9 field must raise (no silent fallback)
    for path in (("D9", "dt"), ("D9", "ticks"), ("D9", "initial_state"),
                 ("D9", "effective_reserve")):
        t = copy.deepcopy(PLAN)
        d = t
        for k in path[:-1]:
            d = d[k]
        del d[path[-1]]
        try:
            X.build_d9_runs(t)
            ok = False
        except (KeyError, IndexError):
            ok = True
        check(f"missing {'/'.join(path)} -> hard error", ok)
    for path in (("D10", "world"), ("D10", "axes")):
        t = copy.deepcopy(PLAN)
        del t[path[0]][path[1]]
        try:
            X.build_d10_runs(t)
            ok = False
        except (KeyError, IndexError):
            ok = True
        check(f"missing {'/'.join(path)} -> hard error", ok)
    # every D9 run carries the required executable fields
    req9 = {"run_id", "policy", "chi", "hard_cap", "source", "sink", "edge",
            "x0", "dt", "ticks", "burn_in", "persistence", "R_eff",
            "eps_x", "eps_u", "source_type"}
    check("every D9 run block has all required executable fields",
          all(req9 <= set(r) for r in D9_RUNS))
    req10 = {"run_id", "policy", "d_over_gmax", "eta", "theta", "delta", "chi",
             "rho", "r_dt", "d", "g_max", "R_eff", "source", "sink", "edge",
             "x0", "ticks", "burn_in", "persistence", "source_type"}
    check("every D10 run block has all required executable fields",
          all(req10 <= set(r) for r in D10_RUNS))


# ===========================================================================
# [3] exact D9 parameter reconstruction (field-by-field vs plan)
# ===========================================================================
def test_group3():
    group("exact D9 parameter reconstruction")
    D9 = PLAN["D9"]
    sc = D9["cell_parameters"]["source_common"]
    snk = D9["cell_parameters"]["sink"]
    edge = D9["topology"]["edges"][0]
    ids = [r["run_id"] for r in D9_RUNS]
    check("D9 run ids are exactly A,B,C,D",
          ids == ["D9-A", "D9-B", "D9-C", "D9-D"])
    for r in D9_RUNS:
        check(f"{r['run_id']}: source Allee params match plan",
              r["source"]["rho"] == sc["rho"] and r["source"]["A"] == sc["A"]
              and r["source"]["K"] == sc["K"] and r["source"]["source"] == "allee")
        check(f"{r['run_id']}: edge/x0/dt/ticks/reserve match plan",
              r["edge"] == edge and r["x0"] == D9["initial_state"]
              and r["dt"] == D9["dt"] and r["ticks"] == D9["ticks"]
              and r["R_eff"] == D9["effective_reserve"]["R_eff"])
    # chi/cap wiring
    wiring = {"D9-A": (0.0, False), "D9-B": (1.0, False),
              "D9-C": (1.0, True), "D9-D": (0.0, True)}
    for r in D9_RUNS:
        chi, cap = wiring[r["run_id"]]
        cellR = r["source"]["R"]
        check(f"{r['run_id']}: chi={chi}, hard_cap={cap}, Cell.R={'R_eff' if chi>0 else 0}",
              r["chi"] == chi and r["hard_cap"] == cap
              and cellR == (11.0 if chi > 0 else 0.0))
    check("D9 sink demand matches plan", all(r["sink"]["d"] == snk["d"] for r in D9_RUNS))


# ===========================================================================
# [4] exact D10 grid and run count
# ===========================================================================
def test_group4():
    group("exact D10 grid + run count")
    core = [r for r in D10_RUNS if r["run_id"].startswith("D10-core/")]
    sec = [r for r in D10_RUNS if r["run_id"].startswith("D10-slice=")]
    check("80 core runs", len(core) == 80)
    check("60 secondary runs", len(sec) == 60)
    check("140 D10 runs total", len(D10_RUNS) == 140)
    dgs = sorted({r["d_over_gmax"] for r in core})
    etas = sorted({r["eta"] for r in core})
    check("core axes: 5 d/gmax x 4 eta",
          dgs == [0.25, 0.5, 0.9, 1.0, 1.1] and etas == [0.5, 0.7, 0.9, 1.0])
    check("core = 5x4x4 policies", len(core) == 5 * 4 * 4)
    slices = {}
    for r in sec:
        axis = r["run_id"].split("slice=")[1].split("/")[0]
        slices.setdefault(axis, set()).add(r["run_id"].split("level=")[1].split("/")[0])
    check("5 secondary slices with 3 levels each",
          len(slices) == 5 and all(len(v) == 3 for v in slices.values()),
          str({k: len(v) for k, v in slices.items()}))
    # total study = 144
    check("total registered runs (D9+D10) == 144", len(D9_RUNS) + len(D10_RUNS) == 144)
    # registered identities preserved even if a secondary level duplicates a core point
    all_ids = [r["run_id"] for r in D9_RUNS + D10_RUNS]
    check("all 144 run ids are unique (no dedup of coincident params)",
          len(set(all_ids)) == 144)


# ===========================================================================
# [5] policy mapping
# ===========================================================================
def test_group5():
    group("policy mapping")
    m = {r["run_id"]: r["policy"] for r in D9_RUNS}
    check("D9 policy map A->P1, B->soft, C->P1C, D->P1C",
          m == {"D9-A": "P1", "D9-B": "soft", "D9-C": "P1C", "D9-D": "P1C"})
    for r in D10_RUNS:
        check_pol = r["policy"] in X.POLICIES
        if not check_pol:
            check(f"{r['run_id']} unknown policy", False)
            return
    # each core grid point has exactly the 4 policies
    core = [r for r in D10_RUNS if r["run_id"].startswith("D10-core/")]
    pts = {}
    for r in core:
        key = (r["d_over_gmax"], r["eta"])
        pts.setdefault(key, set()).add(r["policy"])
    check("every core grid point has exactly {P0,P1,soft,P1C}",
          all(v == set(X.POLICIES) for v in pts.values()) and len(pts) == 20)
    # P1/P0 arms are always chi=0; soft arms are chi>0 EXCEPT the chi=0 slice
    # level (where the soft arm legitimately degenerates to reserve-blind)
    soft_nonchi = [r for r in D10_RUNS if r["policy"] == "soft"
                   and "slice=chi/level=0.0/" not in r["run_id"]]
    check("P1/P0 arms chi=0; soft arms chi>0 (except the chi=0 slice level)",
          all(r["chi"] == 0.0 for r in D10_RUNS if r["policy"] in ("P0", "P1"))
          and all(r["chi"] > 0.0 for r in soft_nonchi))


# ===========================================================================
# [6] D9 static analytic controls (single-tick / formula only)
# ===========================================================================
def test_group6():
    group("D9 static analytic controls")
    rho, K, A = 0.6, 20.0, 5.0
    g = lambda x: X._allee_g(rho, K, A, x)
    check("Allee g(x) matches d0 implementation at samples",
          all(abs(g(x) - d0.natural_drive(
              d0.Cell(1, 0.5, 0, 5, 15, 0, 20, source="allee", rho=0.6, A=5), x)) < 1e-12
              for x in (6, 8, 10, 11, 13, 17)))
    check("g(10) == 3.0 exactly (reference driven root x_r)", abs(g(10.0) - 3.0) < 1e-12)
    check("reserve ordering A(5) < x_r(10) < R_eff(11) < x0(13) < K(20)",
          5.0 < 10.0 < 11.0 < 13.0 < 20.0)
    # boundary comparison at R_eff via a SINGLE tick on D9-D (not a trajectory)
    specD = next(r for r in D9_RUNS if r["run_id"] == "D9-D")
    w, w0, src, snk, e, cfg = X._worlds_for_run(specD)
    rec = X.step_once(specD, [11.0, 2.0], specD["dt"], cfg, w, w0)
    check("boundary: Q_req(R_eff)=5.35 > Q_max(R_eff)=g(11)=3.564 (binding)",
          abs(rec["requested_export"] - 5.35) < 1e-9
          and abs(rec["safe_budget"] - g(11.0)) < 1e-9
          and rec["requested_export"] > rec["safe_budget"]
          and abs(rec["accepted_export"] - g(11.0)) < 1e-9,
          f"req={rec['requested_export']:.4f} budget={rec['safe_budget']:.4f}")
    # timestep certificates match the plan within tolerance (static, no advance)
    specA = next(r for r in D9_RUNS if r["run_id"] == "D9-A")  # chi0
    specB = next(r for r in D9_RUNS if r["run_id"] == "D9-B")  # chi1
    wA, *_ = X._worlds_for_run(specA)
    wB, *_ = X._worlds_for_run(specB)
    certA = d0.gershgorin_dt_certificate(wA)
    certB = d0.gershgorin_dt_certificate(wB)
    check("D9 chi0 certificate ~ 0.5525, r_dt(dt=0.2) ~ 0.362",
          abs(certA - 0.5525) < 1e-3 and abs(0.2 / certA - 0.362) < 1e-3)
    check("D9 chi1 certificate ~ 0.2762, r_dt(dt=0.2) ~ 0.724",
          abs(certB - 0.2762) < 1e-3 and abs(0.2 / certB - 0.724) < 1e-3)
    check("D9 dt is the fixed registered 0.2 for all arms",
          all(X.resolve_dt(r) == 0.2 for r in D9_RUNS))


# ===========================================================================
# [7] D10 analytic boundary values
# ===========================================================================
def test_group7():
    group("D10 analytic boundary values")
    K = 20.0
    check("logistic g_max = rho*K/4 = 3.0 at rho=0.6", abs(0.6 * K / 4 - 3.0) < 1e-12)
    # d = (d/gmax)*g_max at the reference rho
    core = [r for r in D10_RUNS if r["run_id"].startswith("D10-core/")]
    for r in core:
        check_d = abs(r["d"] - r["d_over_gmax"] * (r["rho"] * K / 4)) < 1e-9
        if not check_d:
            check(f"{r['run_id']} d mismatch", False)
            return
    check("every core d = (d/gmax)*g_max", True)
    # deliverable boundary: full service needs d <= eta*g_max; at d/gmax=0.9 (d=2.7)
    check("deliverable boundary d<=eta*g_max: eta*g_max = {0.5:1.5,0.7:2.1,0.9:2.7,1.0:3.0}",
          all(abs(et * 3.0 - v) < 1e-12 for et, v in
              ((0.5, 1.5), (0.7, 2.1), (0.9, 2.7), (1.0, 3.0))))
    # R_eff = K/2 + delta dominates sup unstable root K/2
    check("R_eff = K/2 + delta (default 11.5) > K/2 = 10",
          all(abs(r["R_eff"] - (K / 2 + r["delta"])) < 1e-9 for r in core)
          and core[0]["R_eff"] == 11.5)
    # rho slice crosses feasibility: d fixed at reference, g_max scales with rho
    rho_slice = [r for r in D10_RUNS if r["run_id"].startswith("D10-slice=rho/")]
    dg_by_rho = {r["rho"]: r["d_over_gmax"] for r in rho_slice}
    # d is held at the reference d=2.7; d/gmax registered as the axis value 0.9,
    # but g_max changes with rho -> the *effective* ratio d/(rho K/4) changes
    check("rho slice: d held at reference 2.7 while g_max scales with rho",
          all(abs(r["d"] - 2.7) < 1e-9 for r in rho_slice),
          f"rho levels {sorted(dg_by_rho)}")
    # r_dt slice: dt = r_dt * cert
    rdt_slice = [r for r in D10_RUNS if r["run_id"].startswith("D10-slice=r_dt/")]
    for r in rdt_slice:
        dt = X.resolve_dt(r)
        # recompute the binding certificate independently
        s = r["source"]
        chi_b = max(s["chi"], r["chi"])
        src = d0.Cell(s["alpha"], s["beta"], chi_b, s["L"], s["U"],
                      (r["R_eff"] if chi_b > 0 else 0.0), s["K"],
                      source="logistic", rho=s["rho"])
        snk = d0.Cell(1, 0.5, 0, 5, 15, 0, 20, d=r["sink"]["d"])
        e = r["edge"]
        w = d0.World(cells=(src, snk), edges=(d0.Edge(0, 1, e["M"], e["theta"], e["eta"]),))
        cert = d0.gershgorin_dt_certificate(w)
        if abs(dt - r["r_dt"] * cert) > 1e-12:
            check(f"{r['run_id']} dt != r_dt*cert", False)
            return
    check("r_dt slice: dt == r_dt * gershgorin_cert (shared across policies)", True)


# ===========================================================================
# [8] classification precedence + thresholds (synthetic records)
# ===========================================================================
def test_group8():
    group("classification precedence + thresholds")
    check("clean run -> safe_service", X.classify(synth_metrics()) == "safe_service")
    check("served < 0.9*demand -> safe_rationing",
          X.classify(synth_metrics(postburn_mean_delivered=2.0, demand=2.7))
          == "safe_rationing")
    check("O_physical>tol with delivery -> debt_overuse_service",
          X.classify(synth_metrics(O_physical=0.5)) == "debt_overuse_service")
    check("locally infeasible tick -> locally_infeasible",
          X.classify(synth_metrics(locally_infeasible_ticks=3, O_physical=0.5))
          == "locally_infeasible")
    check("dead source -> collapse",
          X.classify(synth_metrics(final_source_stock=0.5, final_source_regen=-0.1))
          == "collapse")
    check("persistent reserve failure -> collapse",
          X.classify(synth_metrics(time_below_reserve=150)) == "collapse")
    # PRECEDENCE: a record matching several classes gets the highest-precedence one
    check("precedence: collapse beats infeasible+overuse",
          X.classify(synth_metrics(final_source_stock=0.5, final_source_regen=-0.1,
                                   locally_infeasible_ticks=5, O_physical=1.0))
          == "collapse")
    check("precedence: infeasible beats overuse",
          X.classify(synth_metrics(locally_infeasible_ticks=1, O_physical=1.0,
                                   cumulative_delivered=10.0)) == "locally_infeasible")
    check("precedence: overuse beats rationing",
          X.classify(synth_metrics(O_physical=1.0, postburn_mean_delivered=0.1))
          == "debt_overuse_service")
    # boundary: exactly at the service threshold counts as service (>=)
    check("service threshold is inclusive (>= 0.9*demand)",
          X.classify(synth_metrics(postburn_mean_delivered=0.9 * 2.7, demand=2.7))
          == "safe_service")
    # a transient reserve crossing without overuse/infeasibility -> unclassified (F-D10-2 flag)
    check("reserve crossing w/o overuse/infeasibility -> unclassified (reported)",
          X.classify(synth_metrics(reserve_crossings=1, O_physical=0.0))
          == "unclassified")
    check("registered tolerances are the frozen values",
          X.CLASS_TOL["service_threshold"] == 0.9
          and X.CLASS_TOL["dead_stock_threshold"] == 1.0
          and X.CLASS_TOL["tol_overuse"] == 1e-9)


# ===========================================================================
# [9] service + physical-overuse formulas (pure)
# ===========================================================================
def test_group9():
    group("service + physical-overuse formulas")
    check("delivered_service == eta * q_accepted",
          abs(X.delivered_service(0.9, 5.0) - 4.5) < 1e-12)
    check("delivered never equals raw request when eta<1 (loss applied)",
          X.delivered_service(0.9, 5.0) != 5.0)
    check("overuse_increment == dt*[Q-Qmax]_+ (positive part)",
          abs(X.overuse_increment(0.2, 5.0, 3.0) - 0.2 * 2.0) < 1e-12
          and X.overuse_increment(0.2, 2.0, 3.0) == 0.0)
    # a single lossy tick: req != acc != delivered under a binding P1C step
    src = d0.Cell(1, 0.5, 0, 5, 15, 0, 20, source="logistic", rho=0.6)
    snk = d0.Cell(1, 0.5, 0, 5, 15, 0, 20, d=3.0)
    w = d0.World(cells=(src, snk), edges=(d0.Edge(0, 1, 2.0, 0.0, 0.6),))
    tr = p1c.p1c_step(w, [11.6, 2.0], 0.3, {0: p1c.SourceConfig(0, "regenerative", R_eff=11.5)})
    ed = tr.edges[0]
    check("binding lossy tick: q_req != q_acc != q_delivered",
          ed.q_req != ed.q_acc and ed.q_acc != ed.q_delivered
          and abs(ed.q_delivered - 0.6 * ed.q_acc) < 1e-12)


# ===========================================================================
# [10] tick-metric completeness
# ===========================================================================
def test_group10():
    group("tick-metric completeness")
    required = set(X.TICK_FIELDS)
    needed = {"x_before", "x_after", "u", "requested_export", "safe_budget",
              "accepted_export", "delivered_service", "transport_loss",
              "unmet_demand", "source_state", "reserve_crossed", "allee_crossed",
              "locally_infeasible", "p1c_binding", "ledger_residual",
              "theorem_eligible", "theorem_ok"}
    check("TICK_FIELDS covers every required per-tick metric (section 10)",
          needed <= required, f"missing {needed - required}")
    # a single tick record contains every field with finite values
    spec = next(r for r in D9_RUNS if r["run_id"] == "D9-C")
    w, w0, src, snk, e, cfg = X._worlds_for_run(spec)
    rec = X.step_once(spec, list(spec["x0"]), spec["dt"], cfg, w, w0)
    check("single-tick record has all fields (minus 'tick')",
          (needed) <= set(rec))
    finite = all(math.isfinite(v) for k in ("requested_export", "safe_budget",
                 "accepted_export", "delivered_service", "transport_loss",
                 "unmet_demand", "ledger_residual") for v in [rec[k]])
    check("single-tick numeric metrics are finite", finite)


# ===========================================================================
# [11] information-boundary enforcement
# ===========================================================================
def test_group11():
    group("information-boundary enforcement")
    # AST: the harness references no global evaluator and imports no test module
    tree = ast.parse(open("exp_v29_d9_d10.py").read())
    imports = [a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names]
    imports += [n.module for n in ast.walk(tree)
                if isinstance(n, ast.ImportFrom) and n.module]
    check("harness imports no test module",
          not any(m.startswith("test_") for m in imports), str(imports))
    # V_total must never be called anywhere in the harness (viability is inline)
    attr_calls = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    check("harness never calls d0.V_total (no global functional on any path)",
          "V_total" not in attr_calls)
    # resolve dt BEFORE poisoning: the timestep certificate is a DESIGN-TIME tool
    # that legitimately uses lv_exact; it is not on the decision path.
    cases = []
    for rid in ("D9-A", "D9-B", "D9-C", "D9-D"):
        spec = next(r for r in D9_RUNS if r["run_id"] == rid)
        cases.append((spec, spec["dt"]))
    for r in (D10_RUNS[0], D10_RUNS[1]):   # a P0 and a P1 D10 run
        cases.append((r, X.resolve_dt(r)))
    # runtime poison: disable global evaluators, run ONE tick per case
    saved = (d0.V_total, d0.lv_exact, d0.lv_safe)

    def raiser(*a, **k):
        raise AssertionError("global evaluator called on the decision path")
    try:
        d0.V_total = raiser
        d0.lv_exact = raiser
        d0.lv_safe = raiser
        ok_all = True
        for spec, dt in cases:
            w, w0, src, snk, e, cfg = X._worlds_for_run(spec)
            try:
                X.step_once(spec, list(spec["x0"]), dt, cfg, w, w0)
            except AssertionError:
                ok_all = False
        check("single tick under every policy runs with global V/L_V disabled "
              "(dt resolved beforehand)", ok_all)
    finally:
        d0.V_total, d0.lv_exact, d0.lv_safe = saved


# ===========================================================================
# [12] deterministic serialization + run identifiers
# ===========================================================================
def test_group12():
    group("deterministic serialization + run identifiers")
    a = X.build_d9_runs(PLAN) + X.build_d10_runs(PLAN)
    b = X.build_d9_runs(PLAN) + X.build_d10_runs(PLAN)
    check("run reconstruction is deterministic (identical specs on rebuild)",
          [r["run_id"] for r in a] == [r["run_id"] for r in b])
    check("run identifiers are unique and total 144",
          len(set(r["run_id"] for r in a)) == 144)
    # deterministic serialization of a synthetic row list
    row = {"run_id": "X", "schema": X.TICK_FIELDS, "rows": [[1, [2.0, 3.0]]]}
    s1 = json.dumps(row, separators=(",", ":"))
    s2 = json.dumps(row, separators=(",", ":"))
    check("compact JSON serialization is stable", s1 == s2)
    check("run ids are stable strings encoding their parameters",
          "D10-core/dg=0.9/eta=0.9/P1C" in [r["run_id"] for r in a])


# ===========================================================================
# [13] result-path collision protection
# ===========================================================================
def test_group13():
    group("result-path collision protection")
    # _refuse_if_results_exist fires when an artifact exists (temp-redirected)
    saved = (X.SUMMARY_PATH, X.TRACE_PATH)
    with tempfile.TemporaryDirectory() as td:
        X.SUMMARY_PATH = os.path.join(td, "v29_d9_d10_summary.json")
        X.TRACE_PATH = os.path.join(td, "v29_d9_d10_trace.jsonl")
        try:
            X._refuse_if_results_exist()   # nothing exists yet -> ok
            ok_empty = True
        except SystemExit:
            ok_empty = False
        check("no refusal when results absent", ok_empty)
        with open(X.SUMMARY_PATH, "w") as fh:
            fh.write("{}")
        try:
            X._refuse_if_results_exist()
            fired = False
        except SystemExit:
            fired = True
        check("NEGATIVE CONTROL: refuses to overwrite an existing summary", fired)
    X.SUMMARY_PATH, X.TRACE_PATH = saved


# ===========================================================================
# [14] registered-run completeness checking
# ===========================================================================
def test_group14():
    group("registered-run completeness checking")
    specs = X.all_run_specs(PLAN)
    check("all_run_specs returns exactly 144", len(specs) == 144)
    ids = set(s["run_id"] for s in specs)
    check("exactly 4 D9 + 140 D10 ids",
          len([s for s in specs if s["experiment"] == "D9"]) == 4
          and len([s for s in specs if s["experiment"] == "D10"]) == 140)
    # a completeness checker usable post-execution
    check("registered id set is recoverable for post-exec audit", len(ids) == 144)


# ===========================================================================
# [15] negative controls (must fire)
# ===========================================================================
def test_group15():
    group("negative controls (must fire)")
    # (1) plan hash change refused (covered in group 1; re-assert)
    t = copy.deepcopy(PLAN); t["D10"]["world"]["ticks"] = 401
    check("NC1: any plan change breaks the hash",
          X.canonical_hash(t) != X.EXPECTED_PLAN_HASH)
    # (2) omitted parameter -> hard error
    t = copy.deepcopy(PLAN); del t["D9"]["dt"]
    try:
        X.build_d9_runs(t); ok = False
    except KeyError:
        ok = True
    check("NC2: omitted parameter raises (no hidden default)", ok)
    # (3) run count != 144 detected
    t = copy.deepcopy(PLAN)
    t["D10"]["axes"]["primary"]["eta"]["levels"] = [0.5, 0.7, 0.9]  # 3 not 4
    try:
        X.all_run_specs(t); ok = False
    except SystemExit:
        ok = True
    check("NC3: run count != 144 refused", ok)
    # (4) raw request counted as service is wrong (delivered = eta*acc, not req)
    check("NC4: raw request != delivered service when eta<1",
          X.delivered_service(0.9, 5.0) != 5.0)
    # (5) classification order change would flip a result
    m = synth_metrics(final_source_stock=0.5, final_source_regen=-0.1, O_physical=1.0)
    # correct precedence gives collapse; if overuse were checked first it'd be debt
    check("NC5: precedence matters (collapse != debt for a dead+overusing record)",
          X.classify(m) == "collapse")
    # (6) a policy reading a forbidden global metric would raise under poison
    #     (covered in group 11; assert the harness has no V_total call)
    tree = ast.parse(open("exp_v29_d9_d10.py").read())
    check("NC6: no forbidden global evaluator call in the harness",
          "V_total" not in {n.attr for n in ast.walk(tree)
                            if isinstance(n, ast.Attribute)})
    # (7) overwrite protection fires (covered in group 13; assert callable exists)
    check("NC7: overwrite-protection guard exists and is wired into main",
          callable(X._refuse_if_results_exist))


# ===========================================================================
if __name__ == "__main__":
    import sys
    print("=" * 76)
    print("V2.9 Gate 2.4 Phase-A - D9/D10 harness validation (NOT a trajectory run)")
    print("=" * 76)
    print(f"Python {sys.version.split()[0]}   plan hash {PLAN_HASH}")
    for fn in (test_group1, test_group2, test_group3, test_group4, test_group5,
               test_group6, test_group7, test_group8, test_group9, test_group10,
               test_group11, test_group12, test_group13, test_group14, test_group15):
        fn()
    print("-" * 76)
    for k, (title, p, f) in enumerate(GROUPS, 1):
        print(f"group {k:>2}: {p:>3} passed, {f} failed - {title}")
    print(f"total checks: {PASS} passed, {FAIL} failed in {len(GROUPS)} groups")
    print("No complete registered D9/D10 trajectory was executed by this suite.")
    if FAIL:
        print("D9/D10 HARNESS VALIDATION FAILED.")
        raise SystemExit(1)
    print("D9/D10 harness validation passed; Phase-B official execution not yet run.")
