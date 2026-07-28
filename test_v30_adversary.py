"""
V3.0 Gate 1C PRE-EXECUTION suite for the adversarial replay harness
(adversary_v30.py). Validates the harness, its frozen constants, its
information boundaries, and every registered control BEFORE the official Q22
study runs.

THIS SUITE DOES NOT RUN THE REGISTERED Q22 STUDY. All checks are static,
single-step, synthetic, short-horizon, or historical-replay of released V2.6
code. Anything requiring the official study to have finished belongs in a
post-result audit, not here.

Numerical validation is never proof. Run with the project venv (the released
exp_v26 layout generator imports matplotlib, as test_v25/test_v26 already do).
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
import adversary_v30 as adv

PLAN_PATH = "v30_quote_validation_plan.json"
PLAN_CANONICAL = "a1916e8ecf366cee93a5284a0d8fcb68a3e1a429f49ce62b9f5914df87f94061"
PLAN_RAW = "5f01a1fd554bfb2f5e684dc318a805f2887d51274e456c98d1a1d5788d1a6f4f"

with open(PLAN_PATH, "rb") as _f:
    _raw = _f.read()
PLAN = json.loads(_raw)
_canon = hashlib.sha256(json.dumps(PLAN, sort_keys=True, separators=(",", ":"),
                                   ensure_ascii=True).encode()).hexdigest()
if _canon != PLAN_CANONICAL:
    raise SystemExit(f"FATAL: canonical plan hash mismatch: {_canon}")

GROUPS: list = []
PASS = FAIL = 0


def active_state(world, x0, cfg, max_ticks=25):
    """Advance the P1C field until at least one edge is physically active.

    In the V2.6 layouts every cell starts inside its viable band, so all
    marginals - hence all fluxes - are exactly zero at tick 1: transport only
    begins once consumers drain below L. This is a property of the released
    fixture, not of the quote law; the pre-execution checks that need an
    active action start from the first such state."""
    x = tuple(x0)
    for t in range(1, max_ticks + 1):
        tr = p1c.p1c_step(world, x, adv.DT, cfg)
        if any(er.q_acc > 0.0 for er in tr.edges):
            return x, tr, t
        x = tr.x_after
    raise AssertionError("no active edge within the probe horizon")


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


# ---------------------------------------------------------------------------
# A1 plan-hash enforcement and frozen constants
# ---------------------------------------------------------------------------
def test_a1():
    group("A1 plan-hash enforcement and exact frozen constants")
    check(hashlib.sha256(_raw).hexdigest() == PLAN_RAW, "raw plan SHA-256")
    check(_canon == PLAN_CANONICAL, "canonical plan hash")
    spec = PLAN["groups"]["Q22"]["spec"]
    for token, value in (("DEPTH=10", adv.DEPTH == 10),
                         ("WIDTH=40", adv.WIDTH == 40),
                         ("TAIL=20", adv.TAIL == 20)):
        check(token in spec and value, f"{token} matches the locked spec")
    check(adv.QUANTS == (0.5, 1.0) and "[0.5,1.0]" in spec.replace(" ", ""),
          "QUANTS frozen at (0.5, 1.0)")
    check(adv.COALITION == (0, 1) and "COALITION=[0,1]" in spec.replace(" ", ""),
          "COALITION frozen at [0, 1]")
    check(adv.LAYOUT_SEEDS == tuple(range(12)), "layout seeds 0..11")
    check(0 in adv.LAYOUT_SEEDS, "seed 0 (standing falsifier) included")
    check(adv.H_RUN == adv.DEPTH * 3 == 30, "H_RUN = DEPTH*3 (V2.6)")
    check(adv.MARGIN == 1.0 and adv.DELTA == 3.0 and adv.CHI == 1.0,
          "V2.6 margin/delta/chi")
    check("12 layouts x 3 arms" in PLAN["groups"]["Q22"]["cases"],
          "registered case count is 12 layouts x 3 arms")
    check(isinstance(adv.GATE1C_SEMANTICS["translation"], dict)
          and adv.GATE1C_SEMANTICS["tick_fidelity"]["DT"] == 1.0,
          "derived semantics declared with provenance")


# ---------------------------------------------------------------------------
# A2 seed/layout coverage and distinctness
# ---------------------------------------------------------------------------
def test_a2():
    group("A2 seed and layout coverage, distinctness, registered signatures")
    sigs, masks = {}, {}
    for s in adv.LAYOUT_SEEDS:
        world, x0, cfg, is_src = adv.translate_layout(s)
        sigs[s] = adv.layout_signature(is_src)
        masks[s] = is_src
        check(world.n == 25, f"seed {s}: 25 cells")
        check(len(cfg) == 25, f"seed {s}: every cell configured")
        check(any(is_src), f"seed {s}: at least one source")
    check(len(set(sigs.values())) == len(sigs),
          f"all 12 layout signatures distinct ({len(set(sigs.values()))}/12)")
    # reproducible per seed
    for s in (0, 5, 11):
        _w, _x, _c, is_src2 = adv.translate_layout(s)
        check(masks[s] == is_src2, f"seed {s} layout reproducible")
    # matches the released V2.6 generator mask exactly
    import exp_v26
    for s in (0, 1, 11):
        _g, _a, _sr, mask = exp_v26.random_allee_world(s)
        check(tuple(bool(v) for v in mask) == masks[s],
              f"seed {s} mask == released random_allee_world mask")


# ---------------------------------------------------------------------------
# A3 translation fidelity to the released V2.6 layout
# ---------------------------------------------------------------------------
def test_a3():
    group("A3 layout translation fidelity (parameter-for-parameter)")
    import exp_v26
    g, _a, _s, is_src = exp_v26.random_allee_world(0)
    world, x0, cfg, tr_src = adv.translate_layout(0)
    check(tuple(g.x) == x0, "initial state copied verbatim")
    for i in (0, 7, 24):
        c = world.cells[i]
        check(c.K == g.K[i] and c.L == g.L[i] and c.U == g.U[i]
              and c.alpha == g.alpha[i] and c.beta == g.beta[i]
              and c.d == g.d[i] and c.kappa == g.leak_frac[i]
              and c.rho == g.rho[i], f"cell {i} parameters verbatim")
    for i in range(25):
        c = world.cells[i]
        if tr_src[i]:
            check(c.source == "allee" and c.A == 8.0
                  and c.R == 11.0 and c.chi == 1.0
                  and cfg[i].source_type == "regenerative"
                  and cfg[i].R_eff == 11.0, f"source {i} typed correctly")
        else:
            check(cfg[i].source_type == "finite", f"cell {i} typed finite")
    check(all(e.M == 0.6 and e.theta == 0.05 and e.eta == 0.95
              for e in world.edges), "edge constants = V2.6 actor parameters")
    # finite (non-regenerating) cells get a ZERO export budget from P1C
    u = tuple(d0.natural_drive(c, x0[k]) for k, c in enumerate(world.cells))
    fin = [i for i in range(25) if not tr_src[i]]
    st = p1c.classify_state(cfg[fin[0]], x0[fin[0]], u[fin[0]], adv.DT)
    xa, tr, _t0 = active_state(world, x0, cfg)
    zero_exports = all(er.q_acc == 0.0 for er in tr.edges
                       if not tr_src[er.source_id])
    check(any(er.q_acc > 0.0 for er in tr.edges),
          "probe state has at least one active accepted flow (non-vacuous)")
    check(zero_exports, "finite cells never export under P1C (determined)")
    check(st in ("P", "R", "I"), f"finite classifier returns a stock state ({st})")


# ---------------------------------------------------------------------------
# A4 information boundary and production/oracle separation
# ---------------------------------------------------------------------------
def test_a4():
    group("A4 information boundary; production-local vs red-team oracle")
    src = open("adversary_v30.py").read()
    tree = ast.parse(src)
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom):
            imports.add((node.module or "").split(".")[0])
    check("ebu_quote_v30" in imports and "p1c_v29" in imports,
          "harness reuses the quote module and P1C")
    check(not any(m.startswith("test_") for m in imports),
          "harness never imports test modules")
    # the production-local selector must not touch global evaluation objects
    prod = inspect.getsource(adv._candidate_menu) + inspect.getsource(
        adv.arm_c_quote_greedy)
    for forbidden in ("V_total", "physical_metrics", "baseline_burden",
                      "redteam", "wallet", "health", "price"):
        check(forbidden not in prod,
              f"production-local path reads no {forbidden}")
    # the oracle is separately labelled AND does use global harm (by design)
    orc = inspect.getsource(adv.redteam_oracle)
    check("V_total" in orc and "baseline_burden" in orc,
          "oracle uses global harm as an external objective (labelled)")
    check("ORACLE" in src or "oracle" in src.lower(),
          "oracle is explicitly labelled in the source")
    # candidate menus are source-local: only own out-edges appear
    world, x0, cfg, is_src = adv.translate_layout(0)
    xa, _tr, _t0 = active_state(world, x0, cfg)
    u = tuple(d0.natural_drive(c, xa[k]) for k, c in enumerate(world.cells))
    sid = next(i for i in range(25) if is_src[i]
               and adv._candidate_menu(world, xa, u, i, cfg)[2])
    _st, _b, menu = adv._candidate_menu(world, xa, u, sid, cfg)
    check(all(world.edges[idx].i == sid for idx, _q, _a in menu),
          "menu contains only the source's own out-edges")
    check(all(qa <= qr + 1e-12 for _i, qr, qa in menu),
          "menu q_acc never exceeds q_req")
    # menu respects the V2.6 quantity fractions and q_max
    check(all(qr <= adv.ACT_QMAX + 1e-12 for _i, qr, _a in menu),
          "menu respects the V2.6 actor q_max")


# ---------------------------------------------------------------------------
# A5 P1C-before-quote ordering, exact-quote use, q_acc use
# ---------------------------------------------------------------------------
def test_a5():
    group("A5 P1C-before-quote ordering, exact quote, q_acc (not q_req)")
    world, x0, cfg, is_src = adv.translate_layout(0)
    xa, tr, t0 = active_state(world, x0, cfg)
    idx = next(k for k, er in enumerate(tr.edges) if er.q_acc > 0.0)
    s = adv._quote_edge(world, xa, tr, idx, 1, "pass-1",
                        adv._process_cost(world.edges[idx].eta))
    er = tr.edges[idx]
    check(s.inp.q_acc == er.q_acc and s.inp.q_req == er.q_req,
          "quote is built on P1C's q_acc / q_req")
    check(s.epoch.q_acc == er.q_acc, "epoch binds q_acc")
    # exact, not linear
    check(abs(s.exact(er.q_acc) - s.linear_diagnostic(er.q_acc)) >= 0.0
          and s.exact(er.q_acc) <= s.linear_diagnostic(er.q_acc) + 1e-12,
          "exact <= linear (settlement uses exact)")
    reg = eq.EpochRegistry()
    reg.register(s)
    r = reg.settle(s, er.q_acc, 1, 0)
    check(r.status == "settled" and abs(r.issued - s.exact(er.q_acc)) <= 1e-12,
          "settlement equals the exact committed value")
    # cannot quote beyond q_acc
    if er.q_req > er.q_acc:
        try:
            s.exact(er.q_req)
            check(False, "q_req beyond q_acc was quotable")
        except ValueError:
            check(True, "")
    else:
        check(True, "")
    # one action per source per micro-step
    reg2 = eq.EpochRegistry()
    reg2.register(s)
    s_dup = adv._quote_edge(world, xa, tr, idx, 1, "pass-1b",
                            adv._process_cost(world.edges[idx].eta))
    try:
        reg2.register(s_dup)
        check(False, "second same-source same-micro-step epoch accepted")
    except ValueError:
        check(True, "")


# ---------------------------------------------------------------------------
# A6 registered controls 3-5: duplicate / stale / overexecution give no EBU
# ---------------------------------------------------------------------------
def test_a6():
    group("A6 duplicate, stale, and overexecution cannot increase EBU")
    world, x0, cfg, is_src = adv.translate_layout(0)
    xa, tr, _t0 = active_state(world, x0, cfg)
    idx = next(k for k, er in enumerate(tr.edges) if er.q_acc > 0.0)
    q = tr.edges[idx].q_acc
    cost = adv._process_cost(world.edges[idx].eta)
    # duplicate
    s = adv._quote_edge(world, xa, tr, idx, 1, "pass-1", cost)
    reg = eq.EpochRegistry()
    reg.register(s)
    r1 = reg.settle(s, q, 1, 0)
    r2 = reg.settle(s, q, 1, 0)
    check(r1.status == "settled" and r2.status == "violation"
          and r2.issued == 0.0
          and r2.violation.kind == "duplicate_settlement",
          "duplicate settlement issues nothing")
    # stale epoch
    s2 = adv._quote_edge(world, xa, tr, idx, 2, "pass-A", cost)
    reg2 = eq.EpochRegistry()
    reg2.register(s2)
    reg2.invalidate_allocation_pass("pass-A")
    r3 = reg2.settle(s2, q, 2, 0)
    check(r3.status == "violation" and r3.issued == 0.0
          and r3.violation.kind == "stale_epoch", "stale epoch issues nothing")
    # overexecution
    s3 = adv._quote_edge(world, xa, tr, idx, 3, "pass-B", cost)
    reg3 = eq.EpochRegistry()
    reg3.register(s3)
    r4 = reg3.settle(s3, q * 2.0 + 1.0, 3, 0)
    check(r4.status == "violation" and r4.issued == 0.0
          and r4.violation.kind == "overexecution" and r4.violation.o8_open,
          "overexecution issues nothing and flags O8")


# ---------------------------------------------------------------------------
# A7 observational identity (arm B physically identical to arm A)
# ---------------------------------------------------------------------------
def test_a7():
    group("A7 observational identity: arm B == arm A physically (short horizon)")
    for seed in (0, 3):
        world, x0, cfg, is_src = adv.translate_layout(seed)
        a = adv.arm_a_p1c(world, x0, cfg, is_src, 12)
        b = adv.arm_b_observational(world, x0, cfg, is_src, 12)
        check(a.x == b.x, f"seed {seed}: quote layer perturbed the trajectory")
        check(a.actions >= b.actions,
              f"seed {seed}: arm B quoted more actions than P1C accepted")
        check(a.served == b.served and a.loss_total == b.loss_total,
              f"seed {seed}: physical accounting differs between arms")
        check(a.ebu_total == 0.0, f"seed {seed}: arm A carries no EBU")


# ---------------------------------------------------------------------------
# A8 determinism, non-vacuity, beam/depth enforcement
# ---------------------------------------------------------------------------
def test_a8():
    group("A8 determinism, non-vacuity guard, beam/depth enforcement")
    world, x0, cfg, is_src = adv.translate_layout(0)
    c1 = adv.arm_c_quote_greedy(world, x0, cfg, is_src, 12)
    c2 = adv.arm_c_quote_greedy(world, x0, cfg, is_src, 12)
    check(c1.x == c2.x and c1.ebu_total == c2.ebu_total
          and c1.history == c2.history, "arm C deterministic")
    check(c1.actions > 0 and abs(c1.ebu_total) > 1e-6,
          f"NON-VACUITY: arm C must act ({c1.actions} actions, "
          f"EBU {c1.ebu_total})")
    # an all-rest search is vacuous and must be detectable
    rest = adv.RunState(x=tuple(x0))
    check(rest.actions == 0 and rest.ebu_total == 0.0,
          "all-rest state is detectably vacuous")
    # beam width/depth enforcement on a tiny oracle run
    xa, _tr, _t0 = active_state(world, x0, cfg)
    base, _fx, _ex = adv.no_action_baseline(world, xa, cfg, is_src, 2)
    beams, explored = adv.redteam_oracle(world, xa, cfg, is_src, 2, 5, base)
    check(len(beams) <= 5, f"beam width honoured ({len(beams)})")
    check(explored > 0, "oracle explored candidate states")
    check(all(len(b[0].history) <= 2 for b in beams), "oracle depth honoured")
    b1, e1 = adv.redteam_oracle(world, xa, cfg, is_src, 2, 5, base)
    check([b[1] for b in beams] == [b[1] for b in b1] and explored == e1,
          "oracle deterministic")


# ---------------------------------------------------------------------------
# A9 exploit predicate: physical only, persistence required
# ---------------------------------------------------------------------------
def test_a9():
    group("A9 exploit predicate (physical only, persistence required)")
    base = [10.0] * 5
    persistent = [15.0] * 5
    transient = [15.0, 10.0, 10.0, 10.0, 10.0]
    check(adv.classify_profitable_harm(+5.0, persistent, base)["is_exploit"],
          "positive EBU + persistent harm must be an exploit")
    check(not adv.classify_profitable_harm(+5.0, transient, base)["is_exploit"],
          "transient harm must not be an exploit")
    check(not adv.classify_profitable_harm(-1.0, persistent, base)["is_exploit"],
          "harm without profit must not be an exploit")
    check(not adv.classify_profitable_harm(0.0, persistent, base)["is_exploit"],
          "zero EBU must not be an exploit")
    check(not adv.classify_profitable_harm(+5.0, [10.5] * 5, base)["is_exploit"],
          "harm below the margin must not be an exploit")
    # predicate reads no EBU in its harm component
    psrc = inspect.getsource(adv.classify_profitable_harm)
    check("ebu" not in psrc.split("persistent =")[1].split("mean_margin")[0],
          "persistence test contains no EBU term")
    # registered control 2: a known harmful synthetic sequence fires the
    # PHYSICAL harm predicate
    world, x0, cfg, is_src = adv.translate_layout(0)
    sid = [i for i in range(25) if is_src[i]][0]
    x_harm = list(x0)
    x_harm[sid] = 1.0                       # far below A=8 and R=11
    m = adv.physical_metrics(world, tuple(x_harm), is_src)
    check(m["below_A"] >= 1 and m["dead"] >= 1,
          "synthetic sub-Allee state registers Allee crossing and dead source")
    base_b = [d0.V_total(world, x0)] * 3
    atk_b = [d0.V_total(world, tuple(x_harm))] * 3
    v = adv.classify_profitable_harm(+1.0, atk_b, base_b)
    check(v["harm_persistent"] and v["is_exploit"],
          "known harmful sequence triggers the harm predicate")


# ---------------------------------------------------------------------------
# A10 historical positive controls (released V2.6 code, unmodified)
# ---------------------------------------------------------------------------
def test_a10():
    group("A10 historical V2.6 positive controls (released code)")
    import exp_v26
    from ebu_v26 import (State, baseline_BR_schedule, redteam_search,
                         find_exploit)
    g, actors, src = exp_v26.redteam_world()
    init = State(list(g.x), [0.0] * len(actors))
    base, _ = baseline_BR_schedule(g, actors, init, adv.DEPTH + adv.TAIL,
                                   "naive")
    beams, _ = redteam_search(g, actors, list(adv.COALITION), init, "naive",
                              adv.DEPTH, adv.WIDTH, adv.QUANTS,
                              base[:adv.DEPTH], min_net=0.5)
    v = find_exploit(g, actors, list(adv.COALITION), beams, "naive",
                     base[adv.DEPTH:adv.DEPTH + adv.TAIL], adv.TAIL)
    check(v.is_exploit and v.net_ebu > 0 and v.harm_persistent,
          "naive-ledger positive control rediscovered")
    print(f"    naive control: net EBU {v.net_ebu:+.2f}, "
          f"mean tail harm {v.harm_margin:+.2f}")
    r0 = exp_v26.studyC_layout(0)
    check(r0["net"] > 0.0 and r0["harmful"] and r0["exploit"],
          "seed-0 guarded exploit (standing falsifier) reproduced")
    check(r0["dead_end"] == r0["n_src"] and r0["viable_end"] == 0.0,
          "seed-0 control: all sources die, viability 0%")
    print(f"    seed-0 guarded control: net EBU +{r0['net']:.2f}, "
          f"{r0['dead_end']}/{r0['n_src']} sources dead, "
          f"viability {r0['viable_end']:.0f}%")


# ---------------------------------------------------------------------------
# A11 baseline pairing, run recording, strict JSON
# ---------------------------------------------------------------------------
def test_a11():
    group("A11 baseline pairing, terminal/domain-exit recording, strict JSON")
    world, x0, cfg, is_src = adv.translate_layout(0)
    b1, f1, e1 = adv.no_action_baseline(world, x0, cfg, is_src, 12)
    b2, f2, e2 = adv.no_action_baseline(world, x0, cfg, is_src, 12)
    check(b1 == b2 and f1 == f2 and e1 == e2, "no-action baseline deterministic")
    check(len(b1) == 12, "baseline schedule length == ticks")
    a = adv.arm_a_p1c(world, x0, cfg, is_src, 12)
    check(a.x != f1, "baseline is not identical to the acting arm (paired, "
                     "but distinct trajectories)")
    # domain exit is recorded, never dropped
    bad = adv.RunState(x=tuple([-5.0] + list(x0[1:])))
    st = adv._accumulate(bad, bad.x, dict(served=0.0, loss=0.0, unmet=0.0,
                                          overuse=0.0, reserve_crossings=0,
                                          allee_crossings=0), 7, world)
    check(st.domain_exit_tick == 7, "domain exit recorded with its tick")
    # strict JSON of a metrics record
    m = adv.physical_metrics(world, a.x, is_src)
    blob = eq.canonical_json(m)
    check(all(math.isfinite(v) for v in m.values()), "metrics finite")
    check(json.loads(blob) == m, "metrics strict-JSON round trip")
    try:
        eq.canonical_json({"x": float("inf")})
        check(False, "strict JSON accepted Infinity")
    except ValueError:
        check(True, "")
    try:
        eq.canonical_json({"x": float("nan")})
        check(False, "strict JSON accepted NaN")
    except ValueError:
        check(True, "")


# ---------------------------------------------------------------------------
# A12 no Q22 execution during tests
# ---------------------------------------------------------------------------
def test_a12():
    group("A12 this suite does not execute the registered Q22 study")
    tree = ast.parse(open("test_v30_adversary.py").read())
    # (1) no call in this file drives an arm/oracle for H_RUN ticks or more
    run_fns = {"arm_a_p1c", "arm_b_observational", "arm_c_quote_greedy",
               "no_action_baseline", "redteam_oracle"}
    horizons = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                and node.func.attr in run_fns:
            horizons += [a.value for a in node.args
                         if isinstance(a, ast.Constant)
                         and isinstance(a.value, int)
                         and not isinstance(a.value, bool)]
    check(bool(horizons), "arm/oracle horizons are inspectable")
    check(max(horizons) < adv.H_RUN,
          f"every suite horizon is short (max {max(horizons)} < {adv.H_RUN})")
    # (2) the official runner is never imported or invoked here
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom):
            imported.add((node.module or "").split(".")[0])
    check(not any(m.startswith("exp_v30") for m in imported),
          f"official runner never imported ({sorted(imported)})")
    # (3) no registered Q22 artifact exists yet
    import os
    check(not os.path.exists("results/v3.0/gate1c/v30_adversarial_summary.json"),
          "no Q22 summary exists at pre-execution time")


if __name__ == "__main__":
    print("EBP V3.0 Gate 1C - adversarial harness PRE-EXECUTION suite "
          f"(plan {PLAN_CANONICAL[:12]}...)")
    print("The registered Q22 study is NOT executed by this suite.\n")
    for fn in (test_a1, test_a2, test_a3, test_a4, test_a5, test_a6, test_a7,
               test_a8, test_a9, test_a10, test_a11, test_a12):
        fn()
    print()
    for k, (title, p, f) in enumerate(GROUPS, 1):
        print(f"group {k:>2}: {p:>3} passed, {f} failed - {title}")
    print(f"total checks: {PASS} passed, {FAIL} failed in {len(GROUPS)} groups")
    print("Numerical validation is not proof; no Q22 trajectory was executed.")
    if FAIL:
        raise SystemExit(1)
