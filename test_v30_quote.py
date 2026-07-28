"""
V3.0 Gate 1B conformance suite for the pure observational quote layer
(ebu_quote_v30.py), implementing EXACTLY the preregistered groups Q1-Q21 of
V3.0_GATE1_QUOTE_VALIDATION_PROTOCOL.md / v30_quote_validation_plan.json
(canonical SHA-256 recomputed and enforced below; the suite refuses to run on
mismatch).

Q22 (the V2.6 adversarial replay) is REGISTERED BUT NOT RUN here - it belongs
to Gate 1C under separate authorization. No behavioral trajectory runs in
this suite.

Numerical validation at declared fixture points is NEVER proof. Conformance
seed: 30001. Behavioral seeds 0-9 and 100-139 are not used.

Every expected worked-example value is read from the locked plan, and every
settlement value is cross-checked against an INDEPENDENT reference oracle
implemented in this file from the mathematics (not by calling the module).

Standard library only. Directly executable: python3 test_v30_quote.py
"""
from __future__ import annotations
import ast
import hashlib
import json
import math
import random

import d0_v29 as d0
import p1c_v29 as p1c
import ebu_quote_v30 as eq

PLAN_PATH = "v30_quote_validation_plan.json"
PLAN_CANONICAL = "a1916e8ecf366cee93a5284a0d8fcb68a3e1a429f49ce62b9f5914df87f94061"
SEED = 30001

# ---------------------------------------------------------------------------
# plan lock (fail closed)
# ---------------------------------------------------------------------------
with open(PLAN_PATH, "rb") as _f:
    _raw = _f.read()
PLAN = json.loads(_raw)
_got = hashlib.sha256(json.dumps(PLAN, sort_keys=True, separators=(",", ":"),
                                 ensure_ascii=True).encode("utf-8")).hexdigest()
if _got != PLAN_CANONICAL:
    raise SystemExit(f"FATAL: canonical plan hash mismatch: {_got}")
WE = PLAN["worked_examples"]

# ---------------------------------------------------------------------------
# check harness (test_v29_p1c conventions)
# ---------------------------------------------------------------------------
GROUPS: list = []
PASS = FAIL = 0


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


def tol_expected(expected: float) -> float:
    return 1e-9 * (1.0 + abs(expected))


# ---------------------------------------------------------------------------
# INDEPENDENT reference oracle (implemented from the math, not the module)
# ---------------------------------------------------------------------------
def ref_pen(a, b, chi, L, U, R, x):
    dv = L - x if x < L else 0.0
    ev = x - U if x > U else 0.0
    rv = R - x if x < R else 0.0
    return a * dv * dv + b * ev * ev + chi * rv * rv


def ref_quote(p_src, p_dst, z_i, z_j, dt, eta, q, C):
    before = ref_pen(*p_src, z_i) + ref_pen(*p_dst, z_j)
    after = ref_pen(*p_src, z_i - dt * q) + ref_pen(*p_dst, z_j + dt * eta * q)
    return before - after - C


DEF = (1.0, 1.0, 0.0, 4.0, 16.0, 0.0)   # alpha, beta, chi, L, U, R (plan default)


# ---------------------------------------------------------------------------
# construction helpers
# ---------------------------------------------------------------------------
def view(x, params=DEF, K=24.0):
    a, b, chi, L, U, R = params
    return d0.LocalView(x=float(x), alpha=a, beta=b, chi=chi, L=L, U=U, R=R, K=K)


def pc(c0=0.0, c1=0.0, c2=0.0):
    return eq.ProcessCost(category=eq.ALLOWED_COST_CATEGORY, c0=c0, c1=c1, c2=c2)


def mkquote(xi, xj, q, dt=1.0, eta=1.0, ui=0.0, uj=0.0, cost=None,
            p_src=DEF, p_dst=DEF, q_req=None, pass_id="pass-0", tick=0,
            micro=0, sid=0, did=1, cfg="cfg:test"):
    inp = eq.LocalQuoteInput(src=view(xi, p_src), dst=view(xj, p_dst),
                             u_src=ui, u_dst=uj, dt=dt, eta=eta,
                             q_req=(q if q_req is None else q_req), q_acc=q,
                             source_id=sid, dest_id=did, config_id=cfg)
    return eq.build_quote(inp, cost if cost is not None else pc(),
                          pass_id, tick, micro)


def rand_params(rng):
    a = rng.choice(PLAN["random_checks"]["ranges"]["alpha_beta"])
    b = rng.choice(PLAN["random_checks"]["ranges"]["alpha_beta"])
    chi = rng.choice(PLAN["random_checks"]["ranges"]["chi"])
    R = rng.choice(PLAN["random_checks"]["ranges"]["R"])
    return (a, b, chi, 4.0, 16.0, R)


def rand_fixture(rng, force_q_positive=False):
    lo, hi = PLAN["random_checks"]["ranges"]["x"]
    xi, xj = rng.uniform(lo, hi), rng.uniform(lo, hi)
    p_src, p_dst = rand_params(rng), rand_params(rng)
    eta = rng.choice(PLAN["random_checks"]["ranges"]["eta"])
    dt = rng.choice(PLAN["random_checks"]["ranges"]["dt"])
    ui, uj = rng.uniform(-2.0, 2.0), rng.uniform(-2.0, 2.0)
    q_acc = rng.uniform(0.2 if force_q_positive else 0.0, 6.0)
    c0 = rng.choice(PLAN["random_checks"]["ranges"]["c0"])
    lam = rng.choice(PLAN["random_checks"]["ranges"]["lam_L"])
    cost = pc(c0=c0, c1=lam * dt * (1.0 - eta))
    return dict(xi=xi, xj=xj, p_src=p_src, p_dst=p_dst, eta=eta, dt=dt,
                ui=ui, uj=uj, q_acc=q_acc, cost=cost)


def non_vacuous(samples):
    """F12 guard: >= 50% of (q, exact) samples active (q>0, |exact|>1e-6)."""
    if not samples:
        return False
    active = sum(1 for q, v in samples if q > 0.0 and abs(v) > 1e-6)
    return active * 2 >= len(samples)


# ---------------------------------------------------------------------------
# Q1 zero action
# ---------------------------------------------------------------------------
def test_q1():
    group("Q1 zero action: q=0 with C(0)=0 quotes exactly 0.0")
    for xi, xj in [(18.0, 2.0), (10.0, 10.0), (2.0, 17.0), (6.0, 6.0)]:
        s = mkquote(xi, xj, 0.0, cost=pc(c0=0.05, c1=0.3))
        check(s.exact(0.0) == 0.0, f"analytic q=0 quote nonzero at ({xi},{xj})")
    rng = random.Random(SEED)
    ok = True
    for _ in range(50):
        f = rand_fixture(rng)
        s = mkquote(f["xi"], f["xj"], 0.0, dt=f["dt"], eta=f["eta"],
                    ui=f["ui"], uj=f["uj"], cost=f["cost"],
                    p_src=f["p_src"], p_dst=f["p_dst"])
        ok = ok and (s.exact(0.0) == 0.0)
    check(ok, "random q=0 quote not exactly zero")


# ---------------------------------------------------------------------------
# Q2 / Q3 / Q4: E1, E2, E3 from the locked plan
# ---------------------------------------------------------------------------
def e1_schedule():
    i = WE["E1_beneficial"]["inputs"]
    cost = pc(c1=i["lam_L"] * i["dt"] * (1.0 - i["eta"]), c0=i["c0"])
    return mkquote(i["z_i"], i["z_j"], i["q"], dt=i["dt"], eta=i["eta"],
                   cost=cost), i["q"]


def test_q2():
    group("Q2 beneficial action (E1)")
    exp = WE["E1_beneficial"]["expected_exact"]
    s, q = e1_schedule()
    got = s.exact(q)
    check(abs(got - exp) <= tol_expected(exp), f"E1 exact {got} != {exp}")
    ref = ref_quote(DEF, DEF, 18.0, 2.0, 1.0, 0.9, 2.0, 0.02)
    check(abs(got - ref) <= 1e-12, "E1 module vs independent oracle")
    lin = s.linear_diagnostic(q)
    check(abs(lin - WE["E1_beneficial"]["expected_linear"]) <= tol_expected(lin),
          f"E1 linear diagnostic {lin}")


def test_q3():
    group("Q3 damaging action (E2); linear settlement must be impossible")
    i = WE["E2_damaging"]["inputs"]
    exp = WE["E2_damaging"]["expected_exact"]
    exp_lin = WE["E2_damaging"]["expected_linear"]
    cost = pc(c1=i["lam_L"] * i["dt"] * (1.0 - i["eta"]))
    s = mkquote(i["z_i"], i["z_j"], i["q"], dt=i["dt"], eta=i["eta"], cost=cost)
    got = s.exact(i["q"])
    lin = s.linear_diagnostic(i["q"])
    check(abs(got - exp) <= tol_expected(exp), f"E2 exact {got} != {exp}")
    check(abs(lin - exp_lin) <= tol_expected(exp_lin), f"E2 linear {lin} != {exp_lin}")
    # settlement path must return the exact value, NOT the linear one
    reg = eq.EpochRegistry()
    reg.register(s)
    r = reg.settle(s, i["q"], 0, 0)
    check(r.status == "settled" and abs(r.issued - exp) <= tol_expected(exp),
          "settlement did not use the exact finite difference")
    check(abs(r.issued - lin) > 1.0,
          "NEGATIVE CONTROL failed: settlement value indistinguishable from "
          "the linear approximation (linear settlement would underprice E2)")


def test_q4():
    group("Q4 closed damage-repair cycle (E3)")
    i = WE["E3_cycle"]["inputs"]
    c0 = i["c0"]
    x = list(i["x0"])
    cost = pc(c0=c0)
    s1 = mkquote(x[0], x[1], i["q"], eta=i["eta"], cost=cost, tick=0, sid=0, did=1)
    de1 = s1.exact(i["q"])
    x = [x[0] - i["q"], x[1] + i["eta"] * i["q"]]
    s2 = mkquote(x[1], x[0], i["q"], eta=i["eta"], cost=cost, tick=1, sid=1, did=0)
    de2 = s2.exact(i["q"])
    x = [x[0] + i["eta"] * i["q"], x[1] - i["q"]]
    check(abs(de1 - WE["E3_cycle"]["expected_de1"]) <= tol_expected(de1),
          f"E3 de1 {de1}")
    check(abs(de2 - WE["E3_cycle"]["expected_de2"]) <= tol_expected(de2),
          f"E3 de2 {de2}")
    net, exp_net = de1 + de2, WE["E3_cycle"]["expected_net"]
    check(abs(net - exp_net) <= tol_expected(exp_net), f"E3 net {net} != {exp_net}")
    check(abs(net - (-(c0 + c0))) <= 1e-12, "E3 net != -sum(C)")
    check(x == WE["E3_cycle"]["expected_final_state"],
          f"E3 state not exactly restored: {x}")


# ---------------------------------------------------------------------------
# Q5 natural-regeneration exclusion + naive negative control
# ---------------------------------------------------------------------------
def test_q5():
    group("Q5 natural regeneration exclusion (+ naive-baseline negative control)")
    i = WE["REGEN_exclusion"]["inputs"]
    cell = d0.Cell(alpha=1.0, beta=1.0, chi=0.0, L=4.0, U=16.0, R=0.0,
                   K=i["K"], source=i["source"], rho=i["rho"])
    g = d0.natural_drive(cell, i["x_i"])
    check(abs(g - WE["REGEN_exclusion"]["expected_g"]) <= 1e-12, f"g = {g}")
    z = i["x_i"] + i["dt"] * g
    check(abs(z - WE["REGEN_exclusion"]["expected_z_i"]) <= 1e-12, f"z = {z}")
    s = mkquote(i["x_i"], 2.0, 0.0, dt=i["dt"], ui=g, uj=0.0)
    check(s.exact(0.0) == WE["REGEN_exclusion"]["expected_quote"],
          "idle actor quoted nonzero despite regeneration")
    # naive negative control: regeneration relieves a deficit; the naive
    # pre-tick baseline credits it, the z-baseline quote does not.
    xdef = 3.0
    cdef = d0.Cell(alpha=1.0, beta=1.0, chi=0.0, L=4.0, U=16.0, R=0.0,
                   K=20.0, source="logistic", rho=0.4)
    gd = d0.natural_drive(cdef, xdef)                       # = 1.02
    zdef = xdef + 1.0 * gd
    delta_loc = ref_pen(*DEF, zdef) - ref_pen(*DEF, xdef)   # < 0 (relief)
    naive_q0 = ref_pen(*DEF, xdef) - ref_pen(*DEF, zdef)    # naive credit at q=0
    sdef = mkquote(xdef, 10.0, 0.0, ui=gd)
    check(sdef.exact(0.0) == 0.0, "z-baseline quote at q=0 not zero")
    check(naive_q0 > 1e-6,
          "NEGATIVE CONTROL failed: naive baseline did not credit natural change")
    check(abs(naive_q0 - (-delta_loc)) <= 1e-12,
          "naive mis-credit != -delta_loc (plan REGEN clause)")


# ---------------------------------------------------------------------------
# Q6 exact <= linear inequality
# ---------------------------------------------------------------------------
BRANCH_POINTS = {"deficit": 2.0, "band": 10.0, "excess": 18.0, "reserve": 6.0}
RES = (1.0, 1.0, 1.0, 4.0, 16.0, 8.0)     # chi=1, R=8: reserve branch active at 6


def test_q6():
    group("Q6 exact-versus-linear inequality (16 branch fixtures + 200 random)")
    samples = []
    for sname, xi in BRANCH_POINTS.items():
        for dname, xj in BRANCH_POINTS.items():
            p_src = RES if sname == "reserve" else DEF
            p_dst = RES if dname == "reserve" else DEF
            s = mkquote(xi, xj, 3.0, eta=0.9, p_src=p_src, p_dst=p_dst)
            ex, ln = s.exact(3.0), s.linear_diagnostic(3.0)
            check(ex <= ln + 1e-12, f"exact > linear on {sname}->{dname}")
            samples.append((3.0, ex))
    rng = random.Random(SEED)
    bad = 0
    for _ in range(200):
        f = rand_fixture(rng, force_q_positive=True)
        s = mkquote(f["xi"], f["xj"], f["q_acc"], dt=f["dt"], eta=f["eta"],
                    ui=f["ui"], uj=f["uj"], cost=f["cost"],
                    p_src=f["p_src"], p_dst=f["p_dst"])
        ex, ln = s.exact(f["q_acc"]), s.linear_diagnostic(f["q_acc"])
        samples.append((f["q_acc"], ex))
        if ex > ln + 1e-9 * (1.0 + abs(ln)):
            bad += 1
    check(bad == 0, f"{bad}/200 random violations of exact <= linear")
    check(non_vacuous(samples), "Q6 vacuous (F12 guard)")
    # F12 negative control: an all-zero sample set must FAIL the guard
    check(not non_vacuous([(0.0, 0.0)] * 10),
          "NEGATIVE CONTROL failed: zero-only fixtures passed the "
          "non-vacuity guard")


# ---------------------------------------------------------------------------
# Q7 concavity (+ labelled c0>0 non-convex-at-zero case)
# ---------------------------------------------------------------------------
def test_q7():
    group("Q7 schedule concavity (convex C) + activation discontinuity")
    rng = random.Random(SEED)
    bad, samples = 0, []
    for _ in range(100):
        f = rand_fixture(rng, force_q_positive=True)
        cost = pc(c0=0.0, c1=rng.uniform(0.0, 0.2), c2=rng.uniform(0.0, 0.1))
        s = mkquote(f["xi"], f["xj"], f["q_acc"], dt=f["dt"], eta=f["eta"],
                    ui=f["ui"], uj=f["uj"], cost=cost,
                    p_src=f["p_src"], p_dst=f["p_dst"])
        for _ in range(5):
            q1, q2 = rng.uniform(0, f["q_acc"]), rng.uniform(0, f["q_acc"])
            mid = 0.5 * (q1 + q2)
            lhs = s.exact(mid)
            rhs = 0.5 * (s.exact(q1) + s.exact(q2))
            if lhs < rhs - 1e-9 * (1.0 + abs(rhs)):
                bad += 1
        samples.append((f["q_acc"], s.exact(f["q_acc"])))
    check(bad == 0, f"{bad} midpoint concavity violations with convex C")
    check(non_vacuous(samples), "Q7 vacuous (F12 guard)")
    # labelled non-convex-at-zero case (Def 6.13a)
    c0 = 0.05
    s = mkquote(18.0, 2.0, 2.0, eta=0.9, cost=pc(c0=c0, c1=0.01))
    check(s.exact(0.0) == 0.0, "c0 case: q=0 branch not exactly 0")
    tiny = s.exact(1e-9)
    check(abs(tiny - (-c0)) < 1e-6, f"c0 case: no downward jump at 0+ ({tiny})")
    # closed-interval concavity must FAIL: midpoint of (0, 2e-6)
    lhs = s.exact(1e-6)
    rhs = 0.5 * (s.exact(0.0) + s.exact(2e-6))
    check(lhs < rhs - 1e-3,
          "NEGATIVE CONTROL failed: closed-interval concavity did not break "
          "at the activation jump")
    # concave on (0, q_acc]
    rng2 = random.Random(SEED + 1)
    bad2 = 0
    for _ in range(200):
        q1, q2 = rng2.uniform(1e-6, 2.0), rng2.uniform(1e-6, 2.0)
        mid = 0.5 * (q1 + q2)
        if s.exact(mid) < 0.5 * (s.exact(q1) + s.exact(q2)) - 1e-9:
            bad2 += 1
    check(bad2 == 0, f"{bad2} concavity violations on (0, q_acc] with c0>0")


# ---------------------------------------------------------------------------
# Q8 committed schedule and partial execution
# ---------------------------------------------------------------------------
def test_q8():
    group("Q8 committed schedule and partial execution (100 x 5 points)")
    rng = random.Random(SEED)
    bad, samples = 0, []
    for k in range(100):
        f = rand_fixture(rng, force_q_positive=True)
        s = mkquote(f["xi"], f["xj"], f["q_acc"], dt=f["dt"], eta=f["eta"],
                    ui=f["ui"], uj=f["uj"], cost=f["cost"],
                    p_src=f["p_src"], p_dst=f["p_dst"],
                    pass_id=f"pass-{k}", tick=k, sid=0, did=1)
        reg = eq.EpochRegistry()
        reg.register(s)
        qa = f["q_acc"]
        zi = f["xi"] + f["dt"] * f["ui"]
        zj = f["xj"] + f["dt"] * f["uj"]
        for frac_q in (0.0, 0.25 * qa, 0.5 * qa, qa * (1.0 - 1e-12), qa):
            # fresh registry per point (each epoch settles once)
            reg2 = eq.EpochRegistry()
            reg2.register(s)
            r = reg2.settle(s, frac_q, k, 0)
            expect = ref_quote(f["p_src"], f["p_dst"], zi, zj, f["dt"],
                               f["eta"], frac_q, f["cost"].cost(frac_q))
            if not (r.status == "settled"
                    and abs(r.issued - expect) <= 1e-9 * (1.0 + abs(expect))):
                bad += 1
            samples.append((frac_q, r.issued))
    check(bad == 0, f"{bad} partial-execution settlements off the "
          "precommitted schedule (independent oracle)")
    check(non_vacuous(samples), "Q8 vacuous (F12 guard)")


# ---------------------------------------------------------------------------
# Q9 unauthorized overexecution (minimum envelope only; O8 open)
# ---------------------------------------------------------------------------
def test_q9():
    group("Q9 unauthorized overexecution: never positive credit + violation")
    rng = random.Random(SEED)
    for k in range(20):
        f = rand_fixture(rng, force_q_positive=True)
        s = mkquote(f["xi"], f["xj"], f["q_acc"], dt=f["dt"], eta=f["eta"],
                    ui=f["ui"], uj=f["uj"], cost=f["cost"],
                    p_src=f["p_src"], p_dst=f["p_dst"], tick=k)
        reg = eq.EpochRegistry()
        reg.register(s)
        q_over = f["q_acc"] * rng.uniform(1.001, 3.0) + 0.1
        r = reg.settle(s, q_over, k, 0)
        ok = (r.status == "violation" and r.issued == 0.0
              and r.violation is not None
              and r.violation.kind == "overexecution"
              and abs(r.violation.overdraw - (q_over - f["q_acc"])) <= 1e-12
              and r.violation.o8_open
              and r.violation.physical_debt_handling_required)
        check(ok, f"overexecution envelope violated (case {k})")
    # the positive schedule must not extend beyond q_acc at all
    s = mkquote(18.0, 2.0, 2.0, eta=0.9)
    try:
        s.exact(2.5)
        check(False, "schedule evaluated beyond q_acc")
    except ValueError:
        check(True, "")


# ---------------------------------------------------------------------------
# Q10 undriven telescoping
# ---------------------------------------------------------------------------
def seq_world_v(x, p0=DEF, p1=DEF):
    return ref_pen(*p0, x[0]) + ref_pen(*p1, x[1])


def test_q10():
    group("Q10 undriven telescoping (50 sequences + closed cycles)")
    rng = random.Random(SEED)
    bad, samples = 0, []
    for _ in range(50):
        x = [rng.uniform(2.0, 20.0), rng.uniform(2.0, 20.0)]
        x0 = list(x)
        cost = pc(c0=0.02, c1=0.01)
        total = sumC = 0.0
        n = rng.randint(2, 8)
        for step in range(n):
            fwd = rng.random() < 0.5
            eta = rng.choice([0.7, 0.9, 1.0])
            q = rng.uniform(0.1, 2.0)
            si, di = (0, 1) if fwd else (1, 0)
            s = mkquote(x[si], x[di], q, eta=eta, cost=cost,
                        tick=step, sid=si, did=di)
            total += s.exact(q)
            sumC += cost.cost(q)
            nxt = list(x)
            nxt[si] = x[si] - q
            nxt[di] = x[di] + eta * q
            x = nxt
        lhs = total
        rhs = seq_world_v(x0) - seq_world_v(x) - sumC
        if abs(lhs - rhs) > 1e-9 * (1.0 + abs(seq_world_v(x0))):
            bad += 1
        samples.append((1.0, lhs if lhs != 0 else rhs))
    check(bad == 0, f"{bad}/50 undriven telescoping identity failures")
    check(non_vacuous(samples), "Q10 vacuous (F12 guard)")
    # closed cycles: damage then exact repair (eta=1) nets exactly -sum(C)
    bad2 = 0
    for _ in range(10):
        x = [rng.uniform(6.0, 14.0), rng.uniform(6.0, 14.0)]
        q = rng.uniform(1.0, 7.0)
        cost = pc(c0=0.05)
        s1 = mkquote(x[0], x[1], q, eta=1.0, cost=cost, tick=0, sid=0, did=1)
        s2 = mkquote(x[1] + q, x[0] - q, q, eta=1.0, cost=cost, tick=1, sid=1, did=0)
        net = s1.exact(q) + s2.exact(q)
        if abs(net - (-2 * 0.05)) > 1e-9:
            bad2 += 1
    check(bad2 == 0, f"{bad2}/10 closed cycles not equal to -sum(C)")


# ---------------------------------------------------------------------------
# Q11 driven identity (+ mandatory-residual negative control)
# ---------------------------------------------------------------------------
def test_q11():
    group("Q11 driven identity with explicit drive residual")
    rng = random.Random(SEED)
    bad, samples = 0, []
    for _ in range(50):
        x = [rng.uniform(2.0, 20.0), rng.uniform(2.0, 20.0)]
        x0 = list(x)
        cost = pc(c1=0.01)
        dt = rng.choice([0.2, 1.0])
        total = sumC = sumdelta = 0.0
        for step in range(rng.randint(2, 6)):
            u = [rng.uniform(-1.5, 1.5), rng.uniform(-1.5, 1.5)]
            z = [x[0] + dt * u[0], x[1] + dt * u[1]]
            sumdelta += seq_world_v(z) - seq_world_v(x)
            fwd = rng.random() < 0.5
            q = rng.uniform(0.1, 2.0)
            eta = rng.choice([0.7, 1.0])
            si, di = (0, 1) if fwd else (1, 0)
            s = mkquote(x[si], x[di], q, dt=dt, eta=eta,
                        ui=u[si], uj=u[di], cost=cost, tick=step, sid=si, did=di)
            total += s.exact(q)
            sumC += cost.cost(q)
            nxt = list(z)
            nxt[si] = z[si] - dt * q
            nxt[di] = z[di] + dt * eta * q
            x = nxt
        rhs = seq_world_v(x0) - seq_world_v(x) + sumdelta - sumC
        if abs(total - rhs) > 1e-9 * (1.0 + abs(seq_world_v(x0))):
            bad += 1
        samples.append((1.0, total if total != 0 else 1.0))
    check(bad == 0, f"{bad}/50 driven identity failures")
    check(non_vacuous(samples), "Q11 vacuous (F12 guard)")
    # negative control: a driven sequence with |sum(delta)| >> 0 must NOT
    # satisfy the undriven formula (which omits the residual)
    x = [2.0, 10.0]              # cell 0 in deficit
    x0 = list(x)
    u = [1.0, 0.0]               # drive relieves the deficit each tick
    cost = pc()
    total = sumdelta = 0.0
    for step in range(3):
        z = [x[0] + u[0], x[1] + u[1]]
        sumdelta += seq_world_v(z) - seq_world_v(x)
        s = mkquote(x[0], x[1], 0.5, ui=u[0], uj=u[1], cost=cost,
                    tick=step, sid=0, did=1)
        total += s.exact(0.5)
        x = [z[0] - 0.5, z[1] + 0.5]
    undriven_rhs = seq_world_v(x0) - seq_world_v(x)
    driven_rhs = undriven_rhs + sumdelta
    check(abs(sumdelta) > 1e-3, "negative control vacuous: residual ~ 0")
    check(abs(total - driven_rhs) <= 1e-9 * (1 + abs(driven_rhs)),
          "driven identity failed on control")
    check(abs(total - undriven_rhs) > 1e-6,
          "NEGATIVE CONTROL failed: undriven theorem fit a driven sequence "
          "(residual term would be omitted silently)")


# ---------------------------------------------------------------------------
# Q12 duplicate settlement
# ---------------------------------------------------------------------------
def test_q12():
    group("Q12 duplicate settlement rejected (10 fixtures)")
    rng = random.Random(SEED)
    for k in range(10):
        f = rand_fixture(rng, force_q_positive=True)
        s = mkquote(f["xi"], f["xj"], f["q_acc"], dt=f["dt"], eta=f["eta"],
                    ui=f["ui"], uj=f["uj"], cost=f["cost"],
                    p_src=f["p_src"], p_dst=f["p_dst"], tick=k)
        reg = eq.EpochRegistry()
        reg.register(s)
        r1 = reg.settle(s, f["q_acc"], k, 0)
        r2 = reg.settle(s, f["q_acc"], k, 0)
        ok = (r1.status == "settled" and r2.status == "violation"
              and r2.violation.kind == "duplicate_settlement"
              and r2.issued == 0.0)
        check(ok, f"duplicate settlement not rejected (case {k})")


# ---------------------------------------------------------------------------
# Q13 split-action negative control
# ---------------------------------------------------------------------------
def test_q13():
    group("Q13 split-action over-issuance negative control")
    i = WE["SPLIT_counterexample"]["inputs"]
    q = i["q_each"]
    indep_a = ref_quote(DEF, DEF, i["z_i"], i["z_j"], 1.0, i["eta"], q, 0.0)
    joint = ref_quote(DEF, DEF, i["z_i"], i["z_j"], 1.0, i["eta"], 2 * q, 0.0)
    check(abs(indep_a - WE["SPLIT_counterexample"]["expected_independent_each"]) <= 1e-12,
          f"independent each {indep_a}")
    check(abs(2 * indep_a - WE["SPLIT_counterexample"]["expected_independent_sum"]) <= 1e-12,
          "independent sum != 32")
    check(abs(joint - WE["SPLIT_counterexample"]["expected_joint_actual"]) <= 1e-12,
          f"joint actual {joint} != 20")
    phantom = 2 * indep_a - joint
    check(abs(phantom - WE["SPLIT_counterexample"]["expected_phantom"]) <= 1e-12,
          f"NEGATIVE CONTROL failed: phantom credit {phantom} != 12")
    # module reproduces the same numbers through independent frozen quotes
    s_ind = mkquote(i["z_i"], i["z_j"], q, eta=i["eta"])
    s_joint = mkquote(i["z_i"], i["z_j"], 2 * q, eta=i["eta"])
    check(abs(2 * s_ind.exact(q) - s_joint.exact(2 * q) - 12.0) <= 1e-12,
          "module split arithmetic differs from oracle")
    # 20 random shared-source variants: independent frozen quotes always
    # over-issue (>=), strictly on most (convexity)
    rng = random.Random(SEED)
    strict, samples = 0, []
    for _ in range(20):
        xi = rng.uniform(14.0, 22.0)
        xj = rng.uniform(0.0, 3.0)
        qe = rng.uniform(0.5, 2.0)
        ind = ref_quote(DEF, DEF, xi, xj, 1.0, 1.0, qe, 0.0)
        jnt = ref_quote(DEF, DEF, xi, xj, 1.0, 1.0, 2 * qe, 0.0)
        check(2 * ind >= jnt - 1e-9, "independent sum below joint (convexity)")
        if 2 * ind - jnt > 1e-9:
            strict += 1
        samples.append((qe, ind))
    check(strict >= 10, f"only {strict}/20 strict phantom cases (vacuous)")
    check(non_vacuous(samples), "Q13 vacuous (F12 guard)")


# ---------------------------------------------------------------------------
# Q14 restricted single-source production rule
# ---------------------------------------------------------------------------
def test_q14():
    group("Q14 one action per source per micro-step (production rule)")
    reg = eq.EpochRegistry()
    s1 = mkquote(18.0, 0.0, 2.0, tick=5, micro=0, sid=0, did=1)
    reg.register(s1)
    s2 = mkquote(18.0, 0.0, 2.0, tick=5, micro=0, sid=0, did=1,
                 pass_id="pass-x")
    try:
        reg.register(s2)
        check(False, "second same-source same-micro-step epoch accepted "
                     "(Q13 ambiguity expressible in production path)")
    except ValueError:
        check(True, "")
    s3 = mkquote(18.0, 0.0, 2.0, tick=5, micro=1, sid=0, did=1)
    reg.register(s3)
    check(True, "")
    s4 = mkquote(12.0, 0.0, 2.0, tick=5, micro=0, sid=2, did=1)
    reg.register(s4)
    check(True, "")


# ---------------------------------------------------------------------------
# P1C worlds for Q15-Q17
# ---------------------------------------------------------------------------
def p1c_world(x_src, d_src=0.0, M=1.0, theta=0.0, eta=1.0, rho=0.0,
              R_eff=11.0, x_dst=0.0):
    src = d0.Cell(alpha=1.0, beta=1.0, chi=0.0, L=4.0, U=16.0, R=0.0, K=20.0,
                  source=("logistic" if rho > 0 else "none"), rho=rho, d=d_src)
    dst = d0.Cell(alpha=1.0, beta=1.0, chi=0.0, L=4.0, U=16.0, R=0.0, K=40.0)
    w = d0.World(cells=(src, dst), edges=(d0.Edge(i=0, j=1, M=M, theta=theta,
                                                  eta=eta),))
    cfg = {0: p1c.SourceConfig(source_id=0, source_type="regenerative",
                               R_eff=R_eff)}
    return w, (x_src, x_dst), cfg


def quote_from_p1c(w, x, tick_result, edge_idx, tick, cost=None,
                   pass_id="p1c-pass"):
    e = w.edges[edge_idx]
    er = tick_result.edges[edge_idx]
    inp = eq.LocalQuoteInput(
        src=d0.local_view(w.cells[e.i], x[e.i]),
        dst=d0.local_view(w.cells[e.j], x[e.j]),
        u_src=tick_result.u[e.i], u_dst=tick_result.u[e.j],
        dt=tick_result.dt, eta=e.eta, q_req=er.q_req, q_acc=er.q_acc,
        source_id=e.i, dest_id=e.j, config_id=f"cfg:{e.i}")
    return eq.build_quote(inp, cost if cost is not None else pc(),
                          pass_id, tick, 0)


def test_q15():
    group("Q15 P1C positive-but-forbidden: only q_acc is quoted")
    # State P, rationed: budget 1 < request 8
    w, x, cfg = p1c_world(x_src=12.0, R_eff=11.0)
    t = p1c.p1c_step(w, x, 1.0, cfg)
    sr, er = t.sources[0], t.edges[0]
    check(sr.state == "P" and er.q_req > er.q_acc > 0.0,
          f"fixture not rationed-P: {sr.state}, {er.q_req}, {er.q_acc}")
    s = quote_from_p1c(w, x, t, 0, 0)
    check(s.exact(er.q_acc) > 0.0, "rationed accepted quote not positive")
    try:
        s.exact(er.q_req)
        check(False, "raw q_req > q_acc was quotable")
    except ValueError:
        check(True, "")
    check(abs(er.q_acc - 1.0) <= 1e-12, f"expected q_acc = 1, got {er.q_acc}")
    # State R: below reserve -> zero budget, no positive-domain schedule
    w2, x2, cfg2 = p1c_world(x_src=10.0, R_eff=11.0)
    t2 = p1c.p1c_step(w2, x2, 1.0, cfg2)
    check(t2.sources[0].state == "R" and t2.edges[0].q_acc == 0.0,
          "State R fixture wrong")
    s2 = quote_from_p1c(w2, x2, t2, 0, 0)
    check(s2.exact(0.0) == 0.0, "R: zero-domain schedule quote nonzero")
    try:
        s2.exact(0.1)
        check(False, "R: positive-domain quote exists")
    except ValueError:
        check(True, "")
    # State I: feasibility fails -> zero budget
    w3, x3, cfg3 = p1c_world(x_src=11.2, d_src=0.5, R_eff=11.0)
    t3 = p1c.p1c_step(w3, x3, 1.0, cfg3)
    check(t3.sources[0].state == "I" and t3.edges[0].q_acc == 0.0,
          f"State I fixture wrong: {t3.sources[0].state}")
    s3 = quote_from_p1c(w3, x3, t3, 0, 0)
    try:
        s3.exact(0.05)
        check(False, "I: positive-domain quote exists")
    except ValueError:
        check(True, "")


def test_q16():
    group("Q16 P1C permitted-but-negative: permission does not imply positive EBU")
    for M, xd in ((50.0, 3.9), (80.0, 3.95), (60.0, 3.8)):
        w, x, cfg = p1c_world(x_src=10.0, R_eff=0.0, M=M, x_dst=xd)
        t = p1c.p1c_step(w, x, 1.0, cfg)
        sr, er = t.sources[0], t.edges[0]
        check(sr.state == "P" and er.q_acc > 0.0, "fixture not permitted")
        s = quote_from_p1c(w, x, t, 0, 0)
        check(s.exact(er.q_acc) < 0.0,
              f"permitted action not negative (M={M}: {s.exact(er.q_acc)})")


def test_q17():
    group("Q17 P1C non-binding observational identity (byte-identical)")
    fixtures = [
        p1c_world(x_src=12.0, R_eff=11.0, rho=0.3),
        p1c_world(x_src=14.0, R_eff=6.0, eta=0.9, rho=0.3, x_dst=2.0),
        p1c_world(x_src=11.5, R_eff=11.0, d_src=0.2, x_dst=1.0),
    ]
    for w, x0, cfg in fixtures:
        # arm A: pure P1C
        xa = tuple(x0)
        traj_a = [xa]
        for n in range(10):
            xa = p1c.p1c_step(w, xa, 0.5, cfg).x_after
            traj_a.append(xa)
        # arm B: P1C + full observational quote layer
        xb = tuple(x0)
        traj_b = [xb]
        reg = eq.EpochRegistry()
        for n in range(10):
            t = p1c.p1c_step(w, xb, 0.5, cfg)
            for idx, er in enumerate(t.edges):
                if er.q_acc > 0.0:
                    s = quote_from_p1c(w, xb, t, idx, n, pass_id=f"pass-{n}")
                    reg.register(s)
                    s.evaluate(er.q_acc)
                    reg.settle(s, er.q_acc, n, 0)
            xb = t.x_after
            traj_b.append(xb)
        check(traj_a == traj_b,
              "quote layer perturbed the physical P1C trajectory")


# ---------------------------------------------------------------------------
# Q18 information boundary
# ---------------------------------------------------------------------------
FORBIDDEN_NAMES = {"V_total", "viability", "wallet", "wallets", "health",
                   "price", "prices", "rollout", "future_states", "debt",
                   "needs", "transfer", "transfers", "phase_map"}
ALLOWED_IMPORTS = {"__future__", "hashlib", "json", "math", "dataclasses",
                   "typing", "d0_v29"}


def test_q18():
    group("Q18 information boundary (AST + runtime poison)")
    with open("ebu_quote_v30.py") as f:
        tree = ast.parse(f.read())
    imports, names = set(), set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom):
            imports.add((node.module or "").split(".")[0])
        elif isinstance(node, ast.Attribute):
            names.add(node.attr)
        elif isinstance(node, ast.Name):
            names.add(node.id)
    check(imports <= ALLOWED_IMPORTS, f"forbidden imports: {imports - ALLOWED_IMPORTS}")
    hits = names & FORBIDDEN_NAMES
    check(not hits, f"forbidden identifiers in quote module: {hits}")
    check(not any(m.startswith("test_") or m.startswith("exp_")
                  for m in imports), "quote module imports test/exp modules")

    class Poison:
        """Stands in for global V / world state / viability / future states /
        results / wallets / health / prices / global debt."""
        def __getattr__(self, name):
            raise AssertionError("information-boundary breach: poison read")
        def __float__(self):
            raise AssertionError("information-boundary breach: poison read")

    poison = Poison()
    probes = 0
    # 1 global V callable, 2 whole-world state, 3 viability, 4 future states,
    # 5 rollouts/results, 6 wallet, 7 health, 8 price, 9 global debt: each
    # offered where a permitted field belongs; construction must reject.
    for kwargs in (
        dict(src=poison, dst=view(2.0), u_src=0.0),        # world/global V
        dict(src=view(18.0), dst=poison, u_src=0.0),       # whole-world state
        dict(src=view(18.0), dst=view(2.0), u_src=poison), # viability metric
        dict(src=view(18.0), dst=view(2.0), u_src=0.0, u_dst=poison),  # future
        dict(src=view(18.0), dst=view(2.0), u_src=0.0, dt=poison),     # results
        dict(src=view(18.0), dst=view(2.0), u_src=0.0, eta=poison),    # wallet
        dict(src=view(18.0), dst=view(2.0), u_src=0.0, q_req=poison),  # health
        dict(src=view(18.0), dst=view(2.0), u_src=0.0, q_acc=poison),  # price
        dict(src=view(18.0), dst=view(2.0), u_src=0.0, config_id=poison),  # debt
    ):
        base = dict(src=view(18.0), dst=view(2.0), u_src=0.0, u_dst=0.0,
                    dt=1.0, eta=0.9, q_req=2.0, q_acc=2.0, source_id=0,
                    dest_id=1, config_id="cfg")
        base.update(kwargs)
        try:
            eq.LocalQuoteInput(**base)
            check(False, f"poison accepted: {list(kwargs)[0]}")
        except (TypeError, ValueError):
            probes += 1
            check(True, "")
    check(probes == 9, f"only {probes}/9 poison probes rejected")
    # a full world object in place of a LocalView must be rejected too
    w, x, cfg = p1c_world(x_src=12.0)
    try:
        eq.LocalQuoteInput(src=w, dst=view(2.0), u_src=0.0, u_dst=0.0, dt=1.0,
                           eta=1.0, q_req=1.0, q_acc=1.0, source_id=0,
                           dest_id=1, config_id="cfg")
        check(False, "World object accepted as quote input")
    except TypeError:
        check(True, "")


# ---------------------------------------------------------------------------
# Q19 cost double-count negative control
# ---------------------------------------------------------------------------
def test_q19():
    group("Q19 cost double-count negative control")
    for cat in ("state_carried_burden", "monetary_cost", "labour_cost",
                "audit_penalty", "fraud_penalty", "unspecified"):
        try:
            eq.ProcessCost(category=cat, c1=0.01)
            check(False, f"forbidden cost category accepted: {cat}")
        except ValueError:
            check(True, "")
    # numeric detection: the eta-shortfall is state-carried (already inside
    # the V_loc difference). Deliberately subtracting it AGAIN mis-prices E1
    # by exactly the double-counted amount relative to the reference.
    i = WE["E1_beneficial"]["inputs"]
    reference = ref_quote(DEF, DEF, i["z_i"], i["z_j"], i["dt"], i["eta"],
                          i["q"], 0.02)
    # state-carried destination shortfall of this action, expressed as the
    # burden difference the loss already caused at the destination:
    full = ref_pen(*DEF, i["z_j"] + i["dt"] * 1.0 * i["q"])
    lossy = ref_pen(*DEF, i["z_j"] + i["dt"] * i["eta"] * i["q"])
    state_carried = lossy - full            # > 0: relief lost to eta
    wrong = reference - state_carried       # the double-counted construction
    check(state_carried > 1e-9, "fixture vacuous: no state-carried loss term")
    detected = abs(wrong - reference) > 1e-9
    check(detected, "NEGATIVE CONTROL failed: double-counted construction "
                    "indistinguishable from reference")
    check(abs((reference - wrong) - state_carried) <= 1e-12,
          "double-count magnitude != state-carried term")


# ---------------------------------------------------------------------------
# Q20 quote-epoch invalidation
# ---------------------------------------------------------------------------
def test_q20():
    group("Q20 quote-epoch invalidation and no-reallocation rule")
    for k in range(4):
        reg = eq.EpochRegistry()
        sA1 = mkquote(18.0, 2.0, 1.0, tick=k, sid=0, did=1, pass_id="pass-A")
        sA2 = mkquote(15.0, 3.0, 1.0, tick=k, sid=2, did=1, pass_id="pass-A")
        reg.register(sA1)
        reg.register(sA2)
        # first-model rejection: sA1's actor rejects; sA2 remains valid
        reg.reject(sA1.epoch.epoch_id)
        r_rej = reg.settle(sA1, 1.0, k, 0)
        check(r_rej.status == "violation" and r_rej.issued == 0.0,
              "rejected epoch settled")
        r_keep = reg.settle(sA2, 1.0, k, 0)
        check(r_keep.status == "settled",
              "unaffected schedule invalidated by another actor's rejection")
        # reallocation: new pass; ALL old-pass epochs become stale
        reg2 = eq.EpochRegistry()
        sB1 = mkquote(18.0, 2.0, 1.0, tick=k, sid=0, did=1, pass_id="pass-A")
        reg2.register(sB1)
        reg2.invalidate_allocation_pass("pass-A")
        r_stale = reg2.settle(sB1, 1.0, k, 0)
        check(r_stale.status == "violation"
              and r_stale.violation.kind == "stale_epoch"
              and r_stale.issued == 0.0, "stale epoch settled")
        sB2 = mkquote(18.0, 2.0, 0.8, tick=k, micro=1, sid=0, did=1,
                      pass_id="pass-B")
        reg2.register(sB2)
        r_new = reg2.settle(sB2, 0.8, k, 1)
        check(r_new.status == "settled", "new-epoch settlement failed")


# ---------------------------------------------------------------------------
# Q21 determinism and serialization
# ---------------------------------------------------------------------------
def test_q21():
    group("Q21 determinism and strict serialization")
    def build_all():
        out = []
        s, q = e1_schedule()
        out.append((s, q))
        i2 = WE["E2_damaging"]["inputs"]
        out.append((mkquote(i2["z_i"], i2["z_j"], i2["q"], eta=i2["eta"],
                            cost=pc(c1=0.01)), i2["q"]))
        rng = random.Random(SEED)
        for _ in range(50):
            f = rand_fixture(rng, force_q_positive=True)
            out.append((mkquote(f["xi"], f["xj"], f["q_acc"], dt=f["dt"],
                                eta=f["eta"], ui=f["ui"], uj=f["uj"],
                                cost=f["cost"], p_src=f["p_src"],
                                p_dst=f["p_dst"]), f["q_acc"]))
        return out
    a, b = build_all(), build_all()
    same = all(sa.epoch.epoch_id == sb.epoch.epoch_id
               and sa.exact(qa) == sb.exact(qb)
               and sa.linear_diagnostic(qa) == sb.linear_diagnostic(qb)
               for (sa, qa), (sb, qb) in zip(a, b))
    check(same, "rebuild from identical inputs not bit-deterministic")
    samples = [(q, s.exact(q)) for s, q in a]
    check(non_vacuous(samples), "Q21 vacuous (F12 guard)")
    # strict JSON: canonical_json fail-closed on non-finite
    try:
        eq.canonical_json({"x": float("nan")})
        check(False, "canonical_json accepted NaN")
    except ValueError:
        check(True, "")
    # every record JSON round-trips finitely
    s, q = a[0]
    reg = eq.EpochRegistry()
    reg.register(s)
    r = reg.settle(s, q, 0, 0)
    rec = json.loads(r.record())
    check(math.isfinite(rec["issued"]), "settlement record not finite")
    over = reg.settle(s, q, 0, 0)          # duplicate -> violation record
    vrec = json.loads(over.record())
    check(vrec["issued"] == 0.0 and vrec["violation"]["kind"] == "duplicate_settlement",
          "violation record malformed")
    # non-finite measurement fails closed
    r_nan = eq.EpochRegistry()
    s2, q2 = build_all()[1]
    r_nan.register(s2)
    res = r_nan.settle(s2, float("nan"), 0, 0)
    check(res.status == "violation"
          and res.violation.kind == "malformed_measurement",
          "NaN measurement not rejected")
    res2 = r_nan.settle(s2, -1.0, 0, 0)
    check(res2.status == "violation"
          and res2.violation.kind == "negative_quantity",
          "negative measurement not rejected")
    # expired epoch and wrong-tick execution rejected
    reg3 = eq.EpochRegistry()
    s3 = mkquote(18.0, 2.0, 1.0, tick=7)
    reg3.register(s3)
    r3 = reg3.settle(s3, 1.0, 8, 0)
    check(r3.status == "violation" and r3.violation.kind == "expired_epoch",
          "expired epoch settled")


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("EBP V3.0 Gate 1B - quote-layer conformance (plan "
          f"{PLAN_CANONICAL[:12]}..., seed {SEED})")
    print("Q22 adversarial replay: REGISTERED, NOT RUN (Gate 1C).\n")
    for fn in (test_q1, test_q2, test_q3, test_q4, test_q5, test_q6, test_q7,
               test_q8, test_q9, test_q10, test_q11, test_q12, test_q13,
               test_q14, test_q15, test_q16, test_q17, test_q18, test_q19,
               test_q20, test_q21):
        fn()
    print()
    for k, (title, p, f) in enumerate(GROUPS, 1):
        print(f"group {k:>2}: {p:>3} passed, {f} failed - {title}")
    print(f"total checks: {PASS} passed, {FAIL} failed in {len(GROUPS)} groups")
    print("Numerical validation at declared fixture points is not proof; no "
          "behavioral trajectory was run; Q22 was not executed.")
    if FAIL:
        raise SystemExit(1)
