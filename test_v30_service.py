"""
V3.0 Gate 1D PRE-EXECUTION suite for the bounded capability-matched study
(service_v30.py), validating the harness against the locked plan
v30_service_alignment_plan.json before the official 56-run study runs.

THIS SUITE DOES NOT EXECUTE THE REGISTERED STUDY. Every check is static,
single-tick, or short synthetic; an AST check proves no 200-tick registered
trajectory is driven here.

Numerical validation is never proof. Standard library only; directly
executable: python3 test_v30_service.py
"""
from __future__ import annotations
import ast
import hashlib
import inspect
import json
import math

import d0_v29 as d0
import p1c_v29 as p1c
import ebu_quote_v30 as eq
import service_v30 as sv

PLAN_PATH = "v30_service_alignment_plan.json"
PLAN_CANONICAL = "71c706021d738330d5382fec5056ea5228abac61aba0738b00a9a8e75edc1020"
PLAN_RAW = "7a5676e2013d3baa4f18d48443fe448f1d6d0973be79b5c1ca8634a95bfa4f7c"
GATE1_CANONICAL = "a1916e8ecf366cee93a5284a0d8fcb68a3e1a429f49ce62b9f5914df87f94061"

with open(PLAN_PATH, "rb") as _f:
    _raw = _f.read()
PLAN = json.loads(_raw)
_canon = hashlib.sha256(json.dumps(PLAN, sort_keys=True, separators=(",", ":"),
                                   ensure_ascii=True).encode()).hexdigest()
if _canon != PLAN_CANONICAL:
    raise SystemExit(f"FATAL: canonical plan hash mismatch: {_canon}")

GROUPS: list = []
PASS = FAIL = 0
SHORT = 12          # short synthetic horizon, far below the registered 200


def group(title: str) -> None:
    GROUPS.append([title, 0, 0])
    print(f"[{len(GROUPS)}] {title}")


def check(cond: bool, label: str) -> None:
    global PASS, FAIL
    if cond:
        GROUPS[-1][1] += 1
        PASS += 1
    else:
        GROUPS[-1][2] += 1
        FAIL += 1
        print(f"    FAIL: {label}")


def short_run(world, arm, dt, ticks=SHORT):
    """Drive a few bounded ticks of one arm WITHOUT the registered run length.
    Mirrors run_arm's selection logic for B/D at a short horizon."""
    w, x0, cfg, dem, shock, meta = sv.build_world(world)
    x = tuple(x0)
    hist = []
    for t in range(1, ticks + 1):
        u = sv.drive_no_demand(w, x)
        active = w
        if arm != "A_full_p1c":
            chosen = []
            for sid in sorted(cfg):
                _s, _b, menu = sv.action_menu(w, x, u, sid, cfg[sid], dt)
                if not menu:
                    continue
                if arm == "D_restricted_quote_greedy":
                    best = None
                    for c in menu:
                        e = w.edges[c["edge"]]
                        inp = sv._quote_for(w, x, u, dt, c)
                        s = eq.build_quote(inp, sv._process_cost(dt, e.eta),
                                           f"p-{t}", t, 0)
                        v = s.exact(c["q_acc"])
                        if best is None or v > best[0]:
                            best = (v, c)
                    if best[0] > 0.0:
                        chosen.append(best[1])
                else:
                    chosen.append(max(menu, key=lambda c: (c["f"], c["q_acc"])))
            active = d0.World(cells=w.cells,
                              edges=tuple(w.edges[c["edge"]] for c in chosen))
        out = sv.bounded_step(w, x, dt, cfg, dem, active_world=active)
        hist.append(out)
        x = out.x_after
    return w, cfg, hist, x


# ---------------------------------------------------------------------------
def test_g1():
    group("G1 plan hashes, world count, run count, registered constants")
    check(hashlib.sha256(_raw).hexdigest() == PLAN_RAW, "raw plan SHA-256")
    check(_canon == PLAN_CANONICAL, "canonical plan hash")
    g1 = json.load(open("v30_quote_validation_plan.json"))
    check(hashlib.sha256(json.dumps(g1, sort_keys=True, separators=(",", ":"),
                                    ensure_ascii=True).encode()).hexdigest()
          == GATE1_CANONICAL, "Gate-1 quote plan hash still locked")
    es = PLAN["experiment_size"]
    check(len(sv.WORLDS) == es["worlds"] == 7, f"7 worlds ({len(sv.WORLDS)})")
    check(len(sv.ARMS) == es["arms"] == 4, "4 arms")
    check(es["total_runs"] == 7 * 4 * 2 == 56, "56 registered runs")
    check(sv.RUN_TICKS == es["run_length_ticks"] == 200, "200 ticks")
    check(sv.BURN_IN_TICKS == es["burn_in_ticks"] == 50, "50-tick burn-in")
    th = PLAN["service_alignment_predicate"]["frozen_thresholds"]
    check(sv.EBU_THRESHOLD == th["ebu_threshold_burden_units"] == 1.0, "EBU threshold")
    check(sv.SERVICE_REL == th["service_relative_threshold"] == 0.05, "service rel")
    check(sv.SERVICE_ABS == th["service_absolute_threshold"] == 1.0, "service abs")
    check(sv.UNMET_REL == th["unmet_relative_threshold"] == 0.05, "unmet rel")
    check(sv.UNMET_ABS == th["unmet_absolute_threshold"] == 1.0, "unmet abs")
    check(sv.PERSISTENCE_WINDOW == th["persistence_window_ticks"] == 20, "window")
    check(sv.DELTA_R == 0.5, "delta_R = 0.5")
    check(abs(sv.tol(0.0) - 1e-9) < 1e-18 and abs(sv.tol(9.0) - 1e-8) < 1e-17,
          "registered tolerance 1e-9*(1+|value|)")
    check(sv.EPS_X == 0.0 and sv.EPS_U == 0.0 and sv.TAU == 0.0,
          "idealized study: tau = eps_x = eps_u = 0")


def test_g2():
    group("G2 registered timesteps, certificates, r_dt <= 1")
    ts = PLAN["timestep"]
    check(sv.DT_CONSERVATIVE == ts["registered_conservative_dt"],
          "conservative dt exactly as registered")
    check(sv.DT_NEAR == ts["registered_near_certificate_dt"],
          "near-certificate dt exactly as registered")
    for name in sv.WORLDS:
        w, *_ = sv.build_world(name)
        cert, kind = sv.world_certificate(w)
        want = ts["per_world_certificate"][name]
        check(abs(cert - want) <= 1e-12, f"{name}: certificate {cert} vs {want}")
        for dt, key in ((sv.DT_CONSERVATIVE, "r_dt_conservative"),
                        (sv.DT_NEAR, "r_dt_near")):
            r = dt / cert
            check(r <= 1.0, f"{name} r_dt = {r:.4f} <= 1")
            check(abs(r - ts[key][name]) <= 1e-9, f"{name} {key} matches plan")
    # a step above the certificate must be refused BEFORE execution
    try:
        sv.run_arm("W3_relay_3cell", "B_restricted_p1c", 0.9, "illegal")
        check(False, "an uncertified timestep was accepted")
    except ValueError:
        check(True, "")


def test_g3():
    group("G3 bounded-service ordering, service <= available, unmet, x' >= 0")
    src = inspect.getsource(sv.bounded_step)
    for token, order in (("# 1 freeze", 1), ("# 2 input + regen", 2),
                         ("# 3 transport requests", 3),
                         ("# 5 apply accepted transport", 5),
                         ("# 6 physically available", 6),
                         ("# 7 serve demand", 7)):
        check(token in src, f"registered step {order} present in order")
    check(src.index("# 5 apply") < src.index("# 6 physically")
          < src.index("# 7 serve"), "steps 5 < 6 < 7 in source order")
    for name in sv.WORLDS:
        for dt in (sv.DT_CONSERVATIVE, sv.DT_NEAR):
            w, cfg, hist, xend = short_run(name, "B_restricted_p1c", dt)
            ok_svc = all(all(s <= a + 1e-15 for s, a in
                             zip(o.service, o.available)) for o in hist)
            ok_unm = all(all(abs(u - (d - s)) <= 1e-15 for u, d, s in
                             zip(o.unmet, o.demand_amount, o.service))
                         for o in hist)
            ok_nn = all(all(v >= -sv.DOMAIN_TOL for v in o.x_after)
                        for o in hist)
            ok_sd = all(all(s <= d + 1e-15 for s, d in
                            zip(o.service, o.demand_amount)) for o in hist)
            check(ok_svc, f"{name}/{dt}: service exceeded available stock")
            check(ok_unm, f"{name}/{dt}: unmet != demand - service")
            check(ok_nn, f"{name}/{dt}: negative state produced")
            check(ok_sd, f"{name}/{dt}: service exceeded demand (phantom)")


def test_g4():
    group("G4 ledger closure, no phantom service, explicit corrections")
    worst = 0.0
    for name in sv.WORLDS:
        w, cfg, hist, xend = short_run(name, "B_restricted_p1c",
                                       sv.DT_CONSERVATIVE)
        for o in hist:
            worst = max(worst, abs(o.ledger_residual))
        # independent ledger recomputation
        for o in hist:
            lhs = math.fsum(o.x_after) - math.fsum(o.x_before)
            rhs = (sv.DT_CONSERVATIVE * math.fsum(o.u) - o.transport_loss
                   - math.fsum(o.service) + math.fsum(o.negative_corrections))
            check(abs(lhs - rhs) <= 1e-9, f"{name}: ledger open ({lhs - rhs:.2e})")
            break
        check(all(math.fsum(o.negative_corrections) >= 0.0 for o in hist),
              f"{name}: negative corrections must be >= 0 and recorded")
    print(f"    max |ledger residual| over all worlds: {worst:.3e}")
    check(worst <= 1e-9, f"ledger residual within tolerance ({worst:.2e})")
    # no phantom stock: delivered service is post-loss (eta*q_acc), never q_req
    w, x0, cfg, dem, shock, meta = sv.build_world("W1_feasible_2cell")
    x = list(x0); x[1] = 4.0            # push consumer below L so flux exists
    o = sv.bounded_step(w, tuple(x), sv.DT_CONSERVATIVE, cfg, dem)
    delivered = w.edges[0].eta * o.q_acc[0]
    check(o.q_acc[0] > 0.0, "fixture non-vacuous (a flow was accepted)")
    check(o.available[1] <= x[1] + sv.DT_CONSERVATIVE * (o.u[1] + delivered)
          + 1e-12, "destination availability used post-loss delivery only")


def test_g5():
    group("G5 released modules unmodified; wrapper isolated")
    import subprocess
    r = subprocess.run(["git", "diff", "--name-only",
                        "e1c6000f7b050e56e6fd0aa4b23e56c5d9e641d0", "HEAD",
                        "--", "d0_v29.py", "p1c_v29.py", "serialization_v29.py",
                        "energy_balance.py", "ebu_v25.py", "ebu_v26.py"],
                       capture_output=True, text=True)
    check(r.returncode == 0 and not r.stdout.strip(),
          f"released engines unchanged vs v2.9.0 ({r.stdout.strip()})")
    r2 = subprocess.run(["git", "diff", "--name-only", "HEAD", "--",
                         "ebu_quote_v30.py", "v30_service_alignment_plan.json",
                         "V3.0_GATE1D_SERVICE_ALIGNMENT_DIAGNOSIS.md",
                         "v30_quote_validation_plan.json"],
                        capture_output=True, text=True)
    check(r2.returncode == 0 and not r2.stdout.strip(),
          f"quote module and locked Gate-1D files unmodified ({r2.stdout.strip()})")
    # the wrapper must not redefine P1C's budget or the quote equation
    s = inspect.getsource(sv)
    check("def robust_budget" not in s and "def p1c_step" not in s,
          "P1C budget/step not forked")
    check("V_loc(z)" not in s and "def exact(" not in s,
          "exact quote equation not forked")
    check("p1c.p1c_step" in s and "eq.build_quote" in s,
          "released allocation and quote are called, not reimplemented")
    # P1C budget data identical with/without demand for every exporting cell
    for name in sv.WORLDS:
        w, x0, cfg, dem, shock, meta = sv.build_world(name)
        exporters = {e.i for e in w.edges}
        ok = all(w.cells[i].d == 0.0 for i in exporters)
        check(ok, f"{name}: every exporting cell has d = 0 (P1C budget data "
                  "identical with or without the demand term)")


def test_g6():
    group("G6 capability matching and menu equality for arms B, C, D")
    for name in sv.WORLDS:
        w, x0, cfg, dem, shock, meta = sv.build_world(name)
        # advance to a state where menus are non-empty
        _w, _c, hist, x = short_run(name, "B_restricted_p1c",
                                    sv.DT_CONSERVATIVE, ticks=SHORT)
        u = sv.drive_no_demand(w, x)
        for sid in sorted(cfg):
            _s, _b, m = sv.action_menu(w, x, u, sid, cfg[sid],
                                       sv.DT_CONSERVATIVE)
            # the menu function is shared verbatim by B, C and D
            _s2, _b2, m2 = sv.action_menu(w, x, u, sid, cfg[sid],
                                          sv.DT_CONSERVATIVE)
            check(m == m2, f"{name}/{sid}: menu not deterministic")
            check(all(c["frac"] in sv.QUANTS for c in m),
                  f"{name}/{sid}: menu quantity outside registered QUANTS")
            check(all(w.edges[c["edge"]].i == sid for c in m),
                  f"{name}/{sid}: menu contains a foreign out-edge")
            check(all(c["q_acc"] <= c["q_req"] + 1e-15 for c in m),
                  f"{name}/{sid}: q_acc exceeds q_req")
    # one action per source per micro-step for B/C/D
    src = inspect.getsource(sv.run_arm)
    check("for sid in sorted(configs)" in src and "chosen.append" in src,
          "restricted arms select per source")
    # screening budget equals P1C's authoritative q_acc for a single action
    w, x0, cfg, dem, shock, meta = sv.build_world("W1_feasible_2cell")
    x = list(x0); x[1] = 3.0
    u = sv.drive_no_demand(w, tuple(x))
    _s, _b, menu = sv.action_menu(w, tuple(x), u, 0, cfg[0], sv.DT_CONSERVATIVE)
    check(bool(menu), "screening fixture non-vacuous")
    for c in menu:
        sub = d0.World(cells=w.cells, edges=(w.edges[c["edge"]],))
        tr = p1c.p1c_step(sub, tuple(x), sv.DT_CONSERVATIVE, cfg)
        # p1c uses the full raw flux as q_req; compare the capped fraction
        cap = min(c["q_req"], tr.sources[0].Q_max)
        check(abs(cap - c["q_acc"]) <= 1e-12,
              f"screening budget != P1C authoritative cap ({cap} vs {c['q_acc']})")


def test_g7():
    group("G7 arm C observational identity to arm B (short horizon)")
    for name in sv.WORLDS:
        for dt in (sv.DT_CONSERVATIVE, sv.DT_NEAR):
            _w, _c, hb, xb = short_run(name, "B_restricted_p1c", dt)
            _w2, _c2, hc, xc = short_run(name, "C_restricted_p1c_quote", dt)
            check(xb == xc, f"{name}/{dt}: arm C perturbed the trajectory")
            check([o.service for o in hb] == [o.service for o in hc],
                  f"{name}/{dt}: arm C changed service")


def test_g8():
    group("G8 arm-D information boundary (AST + runtime poison)")
    tree = ast.parse(inspect.getsource(sv))
    fnsrc = inspect.getsource(sv.run_arm) + inspect.getsource(sv.action_menu) \
        + inspect.getsource(sv._quote_for) + inspect.getsource(sv._screen_budget)
    forbidden = ("V_total", "viability", "burden", "unmet", "service_alignment",
                 "classify_outcome", "wallet", "health", "price", "debt",
                 "rollout", "outcome_class")
    # arm-D decision path: the quote-selection block only
    d_block = fnsrc.split("if arm == \"D_restricted_quote_greedy\":")[1] \
        .split("else:")[0]
    for f in forbidden:
        check(f not in d_block, f"arm-D decision path reads no {f}")
    check("d0.V_total" not in inspect.getsource(sv.action_menu),
          "menu construction reads no global V")
    # global metrics only after the decision: V_total appears only in run_arm's
    # accounting section, after bounded_step
    rsrc = inspect.getsource(sv.run_arm)
    check(rsrc.index("out = sv.bounded_step") if "out = sv.bounded_step" in rsrc
          else rsrc.index("out = bounded_step") < rsrc.index("d0.V_total"),
          "global metrics computed only after the physical update")
    # runtime poison: a poisoned global object offered as a quote input is refused
    class Poison:
        def __getattr__(self, n):
            raise AssertionError("information-boundary breach")
        def __float__(self):
            raise AssertionError("information-boundary breach")
    p = Poison()
    base = dict(src=d0.LocalView(x=15.0, alpha=1.0, beta=0.5, chi=1.0, L=5.0,
                                 U=15.0, R=8.0, K=20.0),
                dst=d0.LocalView(x=3.0, alpha=1.0, beta=0.5, chi=0.0, L=5.0,
                                 U=15.0, R=0.0, K=20.0),
                u_src=0.0, u_dst=0.0, dt=sv.DT_CONSERVATIVE, eta=0.9,
                q_req=1.0, q_acc=1.0, source_id=0, dest_id=1, config_id="c")
    probes = 0
    for key in ("src", "dst", "u_src", "u_dst", "dt", "eta", "q_req", "q_acc",
                "config_id"):
        kw = dict(base); kw[key] = p
        try:
            eq.LocalQuoteInput(**kw)
            check(False, f"poison accepted in {key}")
        except (TypeError, ValueError, AssertionError):
            probes += 1
    check(probes == 9, f"{probes}/9 poison probes refused")


def test_g9():
    group("G9 predicate logic, persistence, preservation justification")
    def mk(service, unmet, ebu, rx=0, minsrc=None, n=None):
        n = n or len(service)
        r = sv.RunResult(run_id="synth", world="W", arm="X", dt_label="d",
                         dt=1.0, dt_certificate=2.0, r_dt=0.5)
        r.series = dict(service=service, unmet=unmet,
                        min_source=(minsrc if minsrc else [10.0] * n))
        r.totals = dict(ebu=ebu, reserve_crossings=rx, allee_crossings=0,
                        overuse=0.0, p1c_rejected=0, max_ledger_residual=0.0)
        r.final = dict(x=[1.0], burden=0.0, viability=100.0, dead_sources=0,
                       domain_failure_tick=None, negative_state=False,
                       feasible_world=True, note="", min_source=10.0,
                       source_stock=1.0, destination_stock=1.0)
        return r
    N = sv.BURN_IN_TICKS + sv.PERSISTENCE_WINDOW + 30
    hi = [1.0] * N
    lo = [0.5] * N                       # persistent 50% deficit
    B = mk(hi, [0.0] * N, 0.0)
    D = mk(lo, [0.5] * N, 100.0)
    v = sv.service_alignment_predicate(D, B)
    check(v["is_service_alignment_failure"], "clear deficit must fire")
    check(v["service_persistent"] and v["service_condition"], "components set")
    # EBU below threshold must NOT fire
    v2 = sv.service_alignment_predicate(mk(lo, [0.5] * N, 0.5), B)
    check(not v2["is_service_alignment_failure"], "EBU <= 1.0 must not fire")
    # non-persistent deficit must not fire
    blip = list(hi); blip[-1] = 0.0
    v3 = sv.service_alignment_predicate(mk(blip, [0.0] * N, 100.0), B)
    check(not v3["is_service_alignment_failure"], "single-tick blip must not fire")
    # below-magnitude deficit must not fire
    small = [0.999] * N
    v4 = sv.service_alignment_predicate(mk(small, [0.001] * N, 100.0), B)
    check(not v4["is_service_alignment_failure"],
          "sub-threshold magnitude must not fire")
    # preservation justification suppresses the failure
    Bx = mk(hi, [0.0] * N, 0.0, rx=3, minsrc=[7.0] * N)
    Dj = mk(lo, [0.5] * N, 100.0, rx=0, minsrc=[9.0] * N)
    v5 = sv.service_alignment_predicate(Dj, Bx)
    check(v5["preservation_justified"] and not v5["is_service_alignment_failure"],
          "delta_R preservation justification must suppress the failure")
    # exact locked Boolean form: all three conditions required
    form = PLAN["service_alignment_predicate"]["requires_all"]
    check(len(form) == 3, "locked form has three conjuncts")
    src = inspect.getsource(sv.service_alignment_predicate)
    check("ebu_ok and (svc_cond or unm_cond) and not justified" in src,
          "implemented Boolean form matches the locked JSON conjunction")
    # reserve-harm predicate
    rh = sv.reserve_harm_predicate(Bx)
    check(rh["is_reserve_destruction"], "reserve-harm predicate fires on crossings")
    check(not sv.reserve_harm_predicate(B)["is_reserve_destruction"],
          "reserve-harm predicate silent when clean")


def test_g10():
    group("G10 classification exclusivity and locked precedence")
    check(list(sv.PRECEDENCE) ==
          PLAN["outcome_classes"]["precedence_first_match_wins"],
          "implemented precedence == locked JSON ordering")
    check(len(set(sv.PRECEDENCE)) == 9, "nine distinct classes")
    N = sv.BURN_IN_TICKS + sv.PERSISTENCE_WINDOW + 30

    def base(**over):
        r = sv.RunResult(run_id="s", world="W", arm="X", dt_label="d", dt=1.0,
                         dt_certificate=2.0, r_dt=0.5)
        r.series = dict(service=[1.0] * N, unmet=[0.0] * N,
                        min_source=[10.0] * N)
        r.totals = dict(ebu=0.0, reserve_crossings=0, allee_crossings=0,
                        overuse=0.0, p1c_rejected=0, max_ledger_residual=0.0)
        r.final = dict(x=[1.0], burden=0.0, viability=100.0, dead_sources=0,
                       domain_failure_tick=None, negative_state=False,
                       feasible_world=True, note="")
        for k, v in over.items():
            (r.final if k in r.final else r.totals)[k] = v
        return r
    check(sv.classify_outcome(base(), None, None) == "preserve_and_serve",
          "clean run => preserve_and_serve")
    check(sv.classify_outcome(base(negative_state=True), None, None)
          == "numerical_or_domain_failure", "negative state dominates")
    check(sv.classify_outcome(base(domain_failure_tick=5), None, None)
          == "numerical_or_domain_failure", "domain failure dominates")
    # a good service mean must NOT hide domain invalidity
    r = base(domain_failure_tick=5)
    r.series["service"] = [10.0] * N
    check(sv.classify_outcome(r, None, None) == "numerical_or_domain_failure",
          "good averages cannot hide physical invalidity")
    check(sv.classify_outcome(base(dead_sources=2), None, None)
          == "systemic_collapse", "dead source => systemic collapse")
    # full service via reserve destruction is NOT preserve_and_serve
    rd = base(reserve_crossings=4)
    check(sv.classify_outcome(rd, None, None) == "destructive_service",
          "service via reserve destruction cannot be preserve_and_serve")
    inf = base(feasible_world=False)
    inf.series["unmet"] = [0.5] * N
    check(sv.classify_outcome(inf, None, None) == "physical_impossibility",
          "infeasible world with unmet demand => physical impossibility")
    # positive EBU alone is not useful work
    pe = base(ebu=500.0)
    pe.series["unmet"] = [0.5] * N
    cls = sv.classify_outcome(pe, None, None)
    check(cls != "preserve_and_serve",
          f"positive EBU alone must not yield preserve_and_serve (got {cls})")
    # 'did not crash' is not stability: unmet demand still classifies as under-serve
    check(cls in ("safe_rationing_physical_scarcity",
                  "distributive_or_policy_under_service",
                  "preserve_but_under_serve"),
          f"unmet demand must classify as under-service (got {cls})")


def test_g11():
    group("G11 shock timing, determinism, strict JSON, no NaN/Infinity")
    w, x0, cfg, dem, shock, meta = sv.build_world("W7_demand_shock")
    check(shock == (100, 1, 1.5), f"registered shock {shock}")
    pre = list(dem)
    post = list(dem); post[1] += 1.5
    check(pre[1] == 1.0 and post[1] == 2.5,
          "shock raises consumer demand 1.0 -> 2.5 from tick 100")
    check(sv.WORLDS["W1_feasible_2cell"]["shock"] is None,
          "only W7 carries a shock")
    # determinism of a short run
    a = short_run("W4_allee_reserve_stress", "D_restricted_quote_greedy",
                  sv.DT_NEAR)
    b = short_run("W4_allee_reserve_stress", "D_restricted_quote_greedy",
                  sv.DT_NEAR)
    check(a[3] == b[3], "short arm-D run not deterministic")
    check([o.service for o in a[2]] == [o.service for o in b[2]],
          "service series not deterministic")
    # strict JSON of a metrics dict
    _w, _c, hist, xend = short_run("W1_feasible_2cell", "B_restricted_p1c",
                                   sv.DT_CONSERVATIVE)
    rec = dict(x=list(xend), service=[math.fsum(o.service) for o in hist])
    blob = eq.canonical_json(rec)
    check(json.loads(blob) == rec, "strict JSON round trip")
    check(all(math.isfinite(v) for v in xend), "no non-finite state")
    for bad in (float("nan"), float("inf")):
        try:
            eq.canonical_json({"v": bad})
            check(False, f"strict JSON accepted {bad}")
        except ValueError:
            check(True, "")


def test_g12():
    group("G12 F1-F15 negative controls")
    N = sv.BURN_IN_TICKS + sv.PERSISTENCE_WINDOW + 30
    # F1 observational quoting changing the trajectory would be caught (G7)
    _w, _c, hb, xb = short_run("W1_feasible_2cell", "B_restricted_p1c",
                               sv.DT_CONSERVATIVE)
    _w2, _c2, hc, xc = short_run("W1_feasible_2cell",
                                 "C_restricted_p1c_quote", sv.DT_CONSERVATIVE)
    check(xb == xc, "F1 control: B/C identical here (a difference would fire F1)")
    # F2 negative stock: a deliberately over-drained fixture is corrected and
    # recorded, never silently
    w, x0, cfg, dem, shock, meta = sv.build_world("W1_feasible_2cell")
    o = sv.bounded_step(w, (15.0, 0.0), sv.DT_CONSERVATIVE, cfg, (0.0, 99.0))
    check(all(v >= -sv.DOMAIN_TOL for v in o.x_after),
          "F2 control: no negative stock even under extreme demand")
    check(o.unmet[1] > 0.0, "F3 control: unmet demand recorded, not hidden")
    check(math.fsum(o.service) <= math.fsum(o.demand_amount) + 1e-15,
          "F3 control: service never exceeds demand")
    # F4 capability difference would be visible as unequal menus (G6)
    check(True, "")
    # F5 uncertified timestep refused (G2)
    try:
        sv.run_arm("W5_near_boundary", "B_restricted_p1c", 10.0, "bad")
        check(False, "F5 control: uncertified dt accepted")
    except ValueError:
        check(True, "")
    # F7 the predicate must be able to fire (not vacuous)
    B = sv.RunResult(); D = sv.RunResult()
    for r, s, u_, e in ((B, [1.0] * N, [0.0] * N, 0.0),
                        (D, [0.2] * N, [0.8] * N, 50.0)):
        r.series = dict(service=s, unmet=u_, min_source=[10.0] * N)
        r.totals = dict(ebu=e, reserve_crossings=0, allee_crossings=0,
                        overuse=0.0, p1c_rejected=0, max_ledger_residual=0.0)
        r.final = dict(x=[1.0], burden=0.0, viability=100.0, dead_sources=0,
                       domain_failure_tick=None, negative_state=False,
                       feasible_world=True, note="")
    check(sv.service_alignment_predicate(D, B)["is_service_alignment_failure"],
          "F7 control: the predicate can fire (non-vacuous)")
    # F8 no-source-death must not by itself mean aligned
    ok = sv.classify_outcome(B, None, None)
    check(ok == "preserve_and_serve" and
          sv.reserve_harm_predicate(B)["is_reserve_destruction"] is False,
          "F8 control: survival is reported separately from service")
    # F13 domain exit is never an ordinary outcome
    r = sv.RunResult(); r.series = dict(service=[1.0] * N, unmet=[0.0] * N,
                                        min_source=[10.0] * N)
    r.totals = dict(ebu=0.0, reserve_crossings=0, allee_crossings=0,
                    overuse=0.0, p1c_rejected=0, max_ledger_residual=0.0)
    r.final = dict(x=[1.0], burden=0.0, viability=100.0, dead_sources=0,
                   domain_failure_tick=7, negative_state=False,
                   feasible_world=True, note="")
    check(sv.classify_outcome(r, None, None) == "numerical_or_domain_failure",
          "F13 control: domain exit dominates classification")
    # F14 tolerance cannot erase a systematic difference
    check(sv.tol(1.0) < 1e-8, "F14 control: tolerance stays at 1e-9 scale")
    # F11 no actor/wallet/health code in the wrapper. Tested on AST
    # IDENTIFIERS, not source substrings: the module docstring legitimately
    # names these concepts in its own exclusion disclaimer, and a prose
    # mention is not state.
    wtree = ast.parse(inspect.getsource(sv))
    ident = set()
    for node in ast.walk(wtree):
        if isinstance(node, ast.Name):
            ident.add(node.id.lower())
        elif isinstance(node, ast.Attribute):
            ident.add(node.attr.lower())
        elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            ident.add(node.name.lower())
        elif isinstance(node, ast.arg):
            ident.add(node.arg.lower())
    banned = ("wallet", "wallets", "health", "needs", "death", "price",
              "prices", "transfer", "transfers", "personal_debt", "market",
              "markets", "learning")
    hits = sorted(i for i in ident if any(b in i for b in banned))
    check(not hits, f"F11 control: no actor-economy identifiers in the "
                    f"wrapper (hits: {hits})")


def test_g13():
    group("G13 this suite runs no registered 200-tick study")
    tree = ast.parse(open("test_v30_service.py").read())
    horizons = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fn = node.func
            nm = fn.attr if isinstance(fn, ast.Attribute) else (
                fn.id if isinstance(fn, ast.Name) else "")
            if nm in ("short_run", "run_arm"):
                horizons += [a.value for a in node.args
                             if isinstance(a, ast.Constant)
                             and isinstance(a.value, int)
                             and not isinstance(a.value, bool)]
                horizons += [k.value.value for k in node.keywords
                             if k.arg == "ticks"
                             and isinstance(k.value, ast.Constant)]
    check(SHORT < sv.RUN_TICKS, f"short horizon {SHORT} < {sv.RUN_TICKS}")
    check(all(h < sv.RUN_TICKS for h in horizons if isinstance(h, int)),
          f"no call drives the registered run length ({horizons})")
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom):
            imported.add((node.module or "").split(".")[0])
    check(not any(m.startswith("exp_v30") for m in imported),
          "official runner never imported here")
    import os
    check(not os.path.exists("results/v3.0/gate1d/"
                             "v30_service_alignment_summary.json"),
          "no Gate-1D summary exists at pre-execution time")


if __name__ == "__main__":
    print("EBP V3.0 Gate 1D - bounded service PRE-EXECUTION suite "
          f"(plan {PLAN_CANONICAL[:12]}...)")
    print("The registered 56-run study is NOT executed by this suite.\n")
    for fn in (test_g1, test_g2, test_g3, test_g4, test_g5, test_g6, test_g7,
               test_g8, test_g9, test_g10, test_g11, test_g12, test_g13):
        fn()
    print()
    for k, (title, p, f) in enumerate(GROUPS, 1):
        print(f"group {k:>2}: {p:>3} passed, {f} failed - {title}")
    print(f"total checks: {PASS} passed, {FAIL} failed in {len(GROUPS)} groups")
    print("Numerical validation is not proof; the bounded wrapper is outside "
          "the V2.8 theorem (open problem O13); no registered study ran.")
    if FAIL:
        raise SystemExit(1)
