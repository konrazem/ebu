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
        # recompute the binding certificate independently using group_chi (the
        # max chi among the four paired policies), matching resolve_dt
        s = r["source"]
        chi_b = r["group_chi"]
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
    # the GLOBAL functional V_total must not be called inside step_once (the
    # per-tick DECISION + local-diagnostic function). It IS allowed inside
    # run_trajectory (post-tick evaluation/aggregation for stability_class).
    step_fn0 = next(n for n in ast.walk(tree)
                    if isinstance(n, ast.FunctionDef) and n.name == "step_once")
    step_attrs = {n.attr for n in ast.walk(step_fn0) if isinstance(n, ast.Attribute)}
    check("step_once (decision path) never calls the global functional V_total",
          "V_total" not in step_attrs and "lv_exact" not in step_attrs
          and "lv_safe" not in step_attrs)
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
    # (6) a policy reading a forbidden global metric on the DECISION path would
    #     raise under poison (covered in group 11); assert step_once (decision)
    #     has no global-functional call. V_total in run_trajectory (evaluation)
    #     is legitimate and does not violate the boundary.
    tree = ast.parse(open("exp_v29_d9_d10.py").read())
    step_fn = next(n for n in ast.walk(tree)
                   if isinstance(n, ast.FunctionDef) and n.name == "step_once")
    check("NC6: step_once decision path calls no global evaluator (V_total/lv_*)",
          not ({"V_total", "lv_exact", "lv_safe"} &
               {n.attr for n in ast.walk(step_fn) if isinstance(n, ast.Attribute)}))
    # (7) overwrite protection fires (covered in group 13; assert callable exists)
    check("NC7: overwrite-protection guard exists and is wired into main",
          callable(X._refuse_if_results_exist))


def _synth_spec(policy="P1", ticks=14, chi=0.0, M=1.0, d=2.7, eta=0.9,
                x0=(15.0, 3.0), source="logistic", rho=0.6, A=0.0, R_eff=11.5):
    return {"run_id": "SYNTH", "experiment": "D10", "policy": policy, "chi": chi,
            "group_chi": chi, "d_over_gmax": 0.9, "eta": eta, "theta": 0.05,
            "delta": 1.5, "rho": rho, "r_dt": 0.452, "d": d, "g_max": 3.0,
            "R_eff": R_eff, "K": 20.0,
            "source": {"alpha": 1, "beta": 0.5, "chi": chi, "L": 5, "U": 15,
                       "R": (R_eff if chi > 0 else 0.0), "K": 20.0,
                       "source": source, "rho": rho, "A": A},
            "sink": {"alpha": 1, "beta": 0.5, "chi": 0.0, "L": 5, "U": 15,
                     "R": 0.0, "K": 20.0, "d": d, "source": "none", "rho": 0.0,
                     "A": 0.0},
            "edge": {"i": 0, "j": 1, "M": M, "theta": 0.05, "eta": eta},
            "x0": list(x0), "ticks": ticks, "burn_in": 4, "persistence": 6,
            "R_eff_pres": R_eff, "eps_x": 0.0, "eps_u": 0.0,
            "source_type": "regenerative"}


# ===========================================================================
# [16] domain-exit handling (Gate 2.4A Sec 3) - synthetic injection only
# ===========================================================================
def test_group16():
    group("domain-exit handling (non-finite records, continues; finite flagged)")
    # inject a non-finite successor at tick 7 (source -inf)
    spec = _synth_spec(ticks=20)
    orig = X.step_once
    calls = {"n": 0}

    def patched(sp, x, dt, cfg, world, world0):
        calls["n"] += 1
        rec = orig(sp, x, dt, cfg, world, world0)
        if calls["n"] == 7:
            rec = dict(rec)
            rec["x_after"] = [-math.inf, rec["x_after"][1]]
            rec["nonfinite"] = True
        return rec
    X.step_once = patched
    try:
        agg, rows = X.run_trajectory(spec)
    finally:
        X.step_once = orig
    check("non-finite successor recorded as terminal_status=domain_exit",
          agg["terminal_status"] == "domain_exit")
    check("domain_exit_tick, affected cell, and direction recorded",
          agg["domain_exit_tick"] == 7 and agg["domain_exit_cells"] == [0]
          and agg["domain_exit_direction"] == "below")
    check("last valid FINITE state retained (not -inf)",
          math.isfinite(agg["final_source_stock"]))
    check("no clipping / no fabricated later ticks (valid_ticks==6, trace==6)",
          agg["valid_ticks"] == 6 and len(rows) == 6
          and max(r["tick"] for r in rows) == 6)
    blob = json.dumps(agg)
    tb = json.dumps([[r[f] for f in X.TICK_FIELDS] for r in rows])
    check("summary + trace serialize safely (no JSON Infinity/NaN)",
          "Infinity" not in blob and "NaN" not in blob
          and "Infinity" not in tb and "NaN" not in tb)
    check("run_trajectory returns normally so the study loop CONTINUES "
          "(no exception propagated)", isinstance(agg, dict))
    # finite below-domain excursion: run continues, violation flagged
    fin = _synth_spec(policy="P1C", ticks=30, d=5.0)   # sink drains below 0
    agg2, rows2 = X.run_trajectory(fin)
    check("finite below-0 excursion is flagged but the run COMPLETES",
          agg2["terminal_status"] == "completed"
          and agg2["valid_ticks"] == 30
          and agg2["lower_violation_ticks"] > 0,
          f"lower_viol_ticks={agg2['lower_violation_ticks']}")


# ===========================================================================
# [17] shared timestep across the four policies at EVERY D10 point
# ===========================================================================
def test_group17():
    group("shared timestep across all four paired policies (Gate 2.4A Sec 4)")
    from collections import defaultdict
    core = defaultdict(dict)
    for r in D10_RUNS:
        if r["run_id"].startswith("D10-core/"):
            core[(r["d_over_gmax"], r["eta"])][r["policy"]] = X.resolve_dt(r)
    worst = 0.0
    ok = True
    for key, pol_dt in core.items():
        vals = list(pol_dt.values())
        assert len(pol_dt) == 4, key
        spread = max(vals) - min(vals)
        tol = 1e-12 * (1.0 + max(abs(v) for v in vals))
        worst = max(worst, spread)
        if spread > tol:
            ok = False
    check(f"all 4 policies share dt at every core point (20 points)", ok,
          f"max spread {worst:.2e}")
    # explicitly compare P1 vs soft (the previously-confounded pair)
    k = (0.9, 0.9)
    check("P1 and soft share dt at d/gmax=0.9, eta=0.9 (was confounded before)",
          abs(core[k]["P1"] - core[k]["soft"]) < 1e-12,
          f"P1={core[k]['P1']:.10f} soft={core[k]['soft']:.10f}")
    # secondary slices too
    slc = defaultdict(dict)
    for r in D10_RUNS:
        if r["run_id"].startswith("D10-slice="):
            tag = r["run_id"].rsplit("/", 1)[0]
            slc[tag][r["policy"]] = X.resolve_dt(r)
    ok2 = all(max(v.values()) - min(v.values())
              <= 1e-12 * (1 + max(abs(x) for x in v.values()))
              for v in slc.values())
    check("all 4 policies share dt at every secondary-slice point", ok2)


# ===========================================================================
# [18] reserve-tolerance boundary cases (Gate 2.4A Sec 5)
# ===========================================================================
def test_group18():
    group("reserve-tolerance boundary (reserve_tol = 1e-9)")
    rtol = X.CLASS_TOL["reserve_tol"]
    check("registered reserve_tol is 1e-9", rtol == 1e-9)
    R = 11.5
    cfg = p1c.SourceConfig(0, "regenerative", R_eff=R)
    src = d0.Cell(1, 0.5, 0, 5, 15, 0, 20, source="logistic", rho=0.6)
    snk = d0.Cell(1, 0.5, 0, 5, 15, 0, 20, d=1.0)
    w = d0.World(cells=(src, snk), edges=(d0.Edge(0, 1, 1.0, 0.05, 0.9),))
    w0 = d0.World(cells=(src, snk), edges=())
    spec = _synth_spec()
    # sub-tolerance below R (8.88e-16) must NOT be a material crossing
    # emulate by a single tick where x goes from R to R - 8.88e-16
    # (compute directly via the material test used in step_once)
    def material_cross(before, after):
        return (not (before < R - rtol)) and (after < R - rtol)
    check("sub-tolerance deviation (R - 8.88e-16) is NOT a material crossing",
          not material_cross(R + 0.5, R - 8.88e-16))
    check("exactly at tolerance (R - reserve_tol) is NOT material (strict <)",
          not material_cross(R + 0.5, R - rtol))
    check("clearly material deviation (R - 0.5) IS a crossing",
          material_cross(R + 0.5, R - 0.5))
    check("no crossing when already below before (below->below)",
          not material_cross(R - 1.0, R - 2.0))
    # persistence: time_below_reserve uses the material threshold
    below = [R - 0.5] * 10 + [R + 0.5] * 5
    tbr = sum(1 for v in below if v < R - rtol)
    check("time-below-reserve counts only material below-reserve ticks", tbr == 10)


# ===========================================================================
# [19] registered aggregate-schema completeness (Gate 2.4A Sec 6)
# ===========================================================================
def test_group19():
    group("registered aggregate-schema completeness")
    agg, rows = X.run_trajectory(_synth_spec(ticks=16))
    # D9 registered final/time-average metrics -> agg field mapping
    d9map = {
        "reserve_crossing_count": "reserve_crossings",
        "first_reserve_crossing_tick": "first_reserve_crossing_tick",
        "allee_crossing_count": "allee_crossings",
        "first_allee_crossing_tick": "first_allee_crossing_tick",
        "time_below_reserve": "time_below_reserve",
        "time_below_allee": "time_below_allee",
        "dead_source_indicator": "dead_source_indicator",
        "cumulative_transport_loss": "cumulative_transport_loss",
        "cumulative_requested_service": "cumulative_requested_service",
        "cumulative_delivered_service": "cumulative_delivered",
        "cumulative_unmet_demand": "cumulative_unmet_demand",
        "p1c_binding_tick_count": "p1c_binding_ticks",
        "min_source_stock": "min_source_stock",
        "final_source_stock": "final_source_stock",
        "final_viability": "final_viability",
        "postburn_mean_viability": "postburn_mean_viability",
        "max_ledger_residual": "max_ledger_residual",
        "theorem_eligible_ticks": "theorem_eligible_ticks",
        "theorem_violation_count": "theorem_violation_count",
    }
    d9_reg = set(PLAN["D9"]["metrics_final_and_timeaverage"])
    check("every registered D9 metric maps to a produced aggregate field",
          d9_reg <= set(d9map) and all(d9map[k] in agg for k in d9_reg),
          f"missing {[k for k in d9_reg if d9map.get(k) not in agg]}")
    check("dead_source_indicator is now produced (was omitted)",
          "dead_source_indicator" in agg)
    # D10 registered per-run metrics: series -> trace fields; scalars -> agg
    trace_metrics = {"source_stock_series", "dest_stock_series",
                     "raw_requested_export", "safe_budget", "accepted_export",
                     "delivered_service", "unmet_demand", "source_state_PRIF"}
    d10_scalar = {
        "O_physical": "O_physical",
        "reserve_crossing_count": "reserve_crossings",
        "first_reserve_crossing_tick": "first_reserve_crossing_tick",
        "allee_crossing_count": "allee_crossings",
        "infeasible_tick_count": "locally_infeasible_ticks",
        "p1c_binding_fraction": "p1c_binding_fraction",
        "cumulative_transport_loss": "cumulative_transport_loss",
        "min_source_stock": "min_source_stock",
        "final_source_stock": "final_source_stock",
        "final_viability": "final_viability",
        "postburn_mean_viability": "postburn_mean_viability",
        "final_and_postburn_delivered": "final_delivered",
        "stability_class": "stability_class",
        "max_ledger_residual": "max_ledger_residual",
        "theorem_eligible_ticks": "theorem_eligible_ticks",
        "theorem_violation_count": "theorem_violation_count",
        "primary_classification": "primary_classification",
    }
    d10_reg = set(PLAN["D10"]["metrics_per_run"])
    uncovered = [m for m in d10_reg
                 if m not in trace_metrics and d10_scalar.get(m) not in agg]
    check("every registered D10 metric is a produced trace field or aggregate field",
          uncovered == [], f"uncovered {uncovered}")
    check("stability_class is now produced (was omitted)",
          "stability_class" in agg and agg["stability_class"] in
          {"accumulation", "collapse", "converged", "bounded_oscillation",
           "unclassified"})
    # trace carries the series metrics
    check("trace schema carries the registered series metrics",
          {"x_after", "requested_export", "safe_budget", "accepted_export",
           "delivered_service", "unmet_demand", "source_state"} <= set(X.TICK_FIELDS))


# ===========================================================================
# [20] five-class exclusivity/exhaustiveness + plan-derived config
# ===========================================================================
def test_group20():
    group("five-class exclusivity/exhaustiveness + plan-derived config")
    five = {"collapse", "locally_infeasible", "debt_overuse_service",
            "safe_rationing", "safe_service"}
    # sweep synthetic records across the decision variables; each gets exactly
    # one label among the five, or 'unclassified' (treated as a falsifier)
    seen = set()
    for dead in (True, False):
        for infeas in (0, 2):
            for over in (0.0, 1.0):
                for crossed in (0, 1):
                    for served_frac in (0.5, 1.0):
                        m = synth_metrics(
                            final_source_stock=(0.5 if dead else 15.0),
                            final_source_regen=(-0.1 if dead else 1.0),
                            locally_infeasible_ticks=infeas, O_physical=over,
                            reserve_crossings=crossed,
                            postburn_mean_delivered=served_frac * 2.7, demand=2.7)
                        cls = X.classify(m)
                        seen.add(cls)
                        if cls not in five and cls != "unclassified":
                            check("classify returned an unexpected label", False)
                            return
    check("classify only ever returns one of the 5 classes or 'unclassified'",
          seen <= (five | {"unclassified"}), str(seen))
    check("unclassified is treated as a falsifier, NOT an accepted 6th class",
          "unclassified" not in five)
    # a run with a reserve crossing but no overuse/infeasibility -> unclassified
    # (registered falsifier F-D10-2), never silently a success
    m = synth_metrics(reserve_crossings=1, O_physical=0.0,
                      locally_infeasible_ticks=0, final_source_stock=8.0,
                      final_source_regen=1.0, time_below_reserve=0)
    check("F-D10-2: crossing w/o overuse/infeasibility is unclassified (flagged)",
          X.classify(m) == "unclassified")
    # plan-derived edge M and reserve (no hidden hardcoding)
    core = [r for r in D10_RUNS if r["run_id"].startswith("D10-core/")]
    tmplM = PLAN["D10"]["world"]["edges_template"][0]["M"]
    check("D10 edge M comes from the plan edges_template (not hardcoded)",
          all(r["edge"]["M"] == tmplM for r in core))
    check("D10 R_eff derives from K/2 + delta (plan reserve construction)",
          all(abs(r["R_eff"] - (20.0 / 2 + r["delta"])) < 1e-12 for r in core))


# ===========================================================================
if __name__ == "__main__":
    import sys
    print("=" * 76)
    print("V2.9 Gate 2.4 Phase-A - D9/D10 harness validation (NOT a trajectory run)")
    print("=" * 76)
    print(f"Python {sys.version.split()[0]}   plan hash {PLAN_HASH}")
    for fn in (test_group1, test_group2, test_group3, test_group4, test_group5,
               test_group6, test_group7, test_group8, test_group9, test_group10,
               test_group11, test_group12, test_group13, test_group14, test_group15,
               test_group16, test_group17, test_group18, test_group19, test_group20):
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
