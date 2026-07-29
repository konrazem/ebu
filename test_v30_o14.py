"""
V3.0 Gate 1D-B / O14 PRE-EXECUTION suite for the multi-out-edge capability
study implementation (o14_v30.py), validating it against the locked plan
v30_o14_multi_edge_plan.json BEFORE the official 60-run study runs.

THIS SUITE DOES NOT EXECUTE THE REGISTERED STUDY. Every check is static,
single-tick, or an explicitly labelled short synthetic horizon far below the
registered 200 ticks; group T15 proves by AST that no registered-horizon
trajectory and no complete 60-run sweep is driven here, and that no result
artifact is written.

Candidate-count clarification registered here (group T4), resolving the
protocol's "96" wording WITHOUT editing any locked file:
  96  = FEASIBLE-WORLD (W1-W5, 12 edges) static boundary-optimality audit
        slots: 12 edges x 4 quantity levels x 2 timesteps;
  120 = FULL six-world edge-quantity-timestep slots (15 edges x 4 x 2);
  24  = O14_W6_infeasible's contribution (3 edges x 4 x 2), fully present in
        candidate enumeration, run reconstruction, metrics and the future
        execution - W6 is not omitted from anything.

Numerical validation is never proof: passing tests do not prove alignment,
safety, the boundary-optimality lemma in general, O3, O12 or O13.
Standard library only; directly executable: python3 test_v30_o14.py
"""
from __future__ import annotations
import ast
import copy
import hashlib
import inspect
import json
import math
import os

import d0_v29 as d0
import p1c_v29 as p1c
import ebu_quote_v30 as eq
import service_v30 as sv
import o14_v30 as o14

PLAN_CANONICAL = ("2524ba268db004969e04f9c8636cc240b643f0f7"
                  "685507edf65350ea98a37745")
PLAN_RAW = ("00c4dd472eb332e57865f845e41265032fa69ef3"
            "535bb170a8ade013f783d22a")

GROUPS: list = []
PASS = FAIL = 0
SHORT = 10                # short synthetic horizon, far below the 200 ticks
TRAJECTORIES_RUN = 0      # every short trajectory increments this (T15)


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


def short_run(world: str, arm: str, dt_label: str):
    """Explicitly labelled NON-STUDY short-horizon run (SHORT ticks)."""
    global TRAJECTORIES_RUN
    TRAJECTORIES_RUN += 1
    return o14.run_arm(world, arm, dt_label, ticks=SHORT)


def world_state(name: str):
    world, x0, cfg, dem, meta = o14.build_world(name)
    u = sv.drive_no_demand(world, x0)
    return world, x0, u, cfg, dem, meta


def menus_at_t0(name: str, dt_label: str):
    world, x0, u, cfg, dem, _ = world_state(name)
    dt = o14.world_dts(name)[dt_label]
    sid = sorted(cfg)[0]
    state, budget, cands = o14.candidate_menu(world, x0, u, sid,
                                              cfg[sid], dt)
    return world, x0, u, cfg, dem, dt, state, budget, cands


# ---------------------------------------------------------------------------
def test_t1():
    group("T1 plan hash lock, strict JSON, schema, tamper refusal")
    raw = open(o14.PLAN_PATH, "rb").read()
    check(hashlib.sha256(raw).hexdigest() == PLAN_RAW,
          "raw plan SHA-256 matches the locked value")
    check(o14.plan_canonical_hash(o14.PLAN) == PLAN_CANONICAL,
          "canonical (sorted-keys compact) hash matches the locked value")
    check(o14.PLAN_CANONICAL == PLAN_CANONICAL and o14.PLAN_RAW == PLAN_RAW,
          "implementation stores the expected hashes as constants")
    # strict JSON: NaN/Infinity constants must be rejected
    try:
        json.loads('{"a": NaN}', parse_constant=o14._reject_nonfinite)
        check(False, "NaN constant must be rejected")
    except ValueError:
        check(True, "NaN constant rejected (strict JSON)")
    # tamper refusals, all in memory (no file is written by this suite)
    t = copy.deepcopy(o14.PLAN)
    t["experiment_size"]["total_runs"] = 61
    try:
        o14.validate_plan(t)
        check(False, "altered total_runs must be rejected")
    except ValueError:
        check(True, "altered value (total_runs=61) rejected")
    check(o14.plan_canonical_hash(t) != PLAN_CANONICAL,
          "any tamper changes the canonical hash")
    t2 = copy.deepcopy(o14.PLAN)
    del t2["quantity_menu"]["fractions"]
    try:
        o14.validate_plan(t2)
        check(False, "missing quantity_menu.fractions must be rejected")
    except ValueError:
        check(True, "missing required field rejected")
    t3 = copy.deepcopy(o14.PLAN)
    t3["quantity_menu"]["fractions"] = [0.5, 1.0]
    try:
        o14.validate_plan(t3)
        check(False, "non-registered menu must be rejected")
    except ValueError:
        check(True, "non-registered quantity menu rejected")
    t4 = copy.deepcopy(o14.PLAN)
    t4["arms"]["E_aggregate_source_group_quote"] = "now executable"
    try:
        o14.validate_plan(t4)
        check(False, "executable arm E must be rejected")
    except ValueError:
        check(True, "arm E must remain non-executable (rejected tamper)")
    try:
        o14.load_plan(expected_canonical="0" * 64)
        check(False, "wrong expected canonical hash must fail closed")
    except SystemExit:
        check(True, "load_plan fails closed on canonical-hash mismatch")
    # no hidden CLI override in the implementation
    tree = ast.parse(open("o14_v30.py").read())
    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    attrs = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    check("argv" not in attrs and "argparse" not in names,
          "no command-line scientific override path exists")


def test_t2():
    group("T2 exact run inventory (reconstruction only, no execution)")
    specs = o14.build_run_specs()
    check(len(specs) == 60, "exactly 60 run specifications")
    ids = [s["run_id"] for s in specs]
    check(len(set(ids)) == 60, "60 unique identifiers")
    check(len({s["world"] for s in specs}) == 6, "exactly 6 worlds")
    check(len({s["arm"] for s in specs}) == 5, "exactly 5 executable arms")
    check(len({s["dt_label"] for s in specs}) == 2, "exactly 2 timesteps")
    check(all(s["run_id"] ==
              f"{s['world']}|{s['arm']}|{s['dt_label']}" for s in specs),
          "identifier format <world>|<arm>|<dt_label>")
    check(not any("E_aggregate" in s["arm"] for s in specs),
          "no arm-E run exists")
    check(specs == o14.build_run_specs(),
          "deterministic frozen order (rebuild identical)")
    tree = ast.parse(open("o14_v30.py").read())
    idents = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)} \
        | {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    mods = {a.name.split(".")[0] for n in ast.walk(tree)
            if isinstance(n, ast.Import) for a in n.names}
    check("random" not in mods and "secrets" not in mods
          and not any("seed" in i.lower() for i in idents),
          "no randomness or seed identifier anywhere in the implementation")
    check(not os.path.exists("results/v3.0/gate1db"),
          "no result path was created by reconstruction")


def test_t3():
    group("T3 world reconstruction and non-vacuity (static, t0)")
    expect_deg = dict(zip(o14.WORLD_NAMES, (2, 2, 2, 4, 2, 3)))
    for name in o14.WORLD_NAMES:
        world, x0, u, cfg, dem, meta = world_state(name)
        spec = o14.PLAN["worlds"][name]
        deg = sum(1 for e in world.edges if e.i == 0)
        check(deg == expect_deg[name], f"{name}: out-degree {deg}")
        check([list(map(float, (c.alpha, c.beta, c.chi, c.L, c.U, c.R, c.K)))
               for c in world.cells] ==
              [[float(c[k]) for k in
                ("alpha", "beta", "chi", "L", "U", "R", "K")]
               for c in spec["cells"]],
              f"{name}: cells reconstructed exactly from the plan")
        check([(e.i, e.j, e.M, e.theta, e.eta) for e in world.edges] ==
              [(int(e["i"]), int(e["j"]), float(e["M"]), float(e["theta"]),
                float(e["eta"])) for e in spec["edges"]],
              f"{name}: edges reconstructed exactly from the plan")
        for dt_label in o14.DT_LABELS:
            *_, cands = menus_at_t0(name, dt_label)
            active_edges = {c["edge"] for c in cands}
            check(len(active_edges) >= 2,
                  f"{name}/{dt_label}: >= 2 simultaneously active out-edges "
                  f"at t0 (got {len(active_edges)})")
    # W1 activity inequalities x_j < L_j - theta/(2 eta alpha_j)
    world, x0, *_ = world_state("O14_W1_eta_split")
    b1 = 5.0 - 0.05 / (2 * 0.95 * 1.0)
    b2 = 5.0 - 0.05 / (2 * 0.60 * 1.0)
    check(abs(b1 - 4.9736842105263158) < 1e-12 and x0[1] < b1,
          f"W1 dst1 activity bound {b1:.4f} holds with margin")
    check(abs(b2 - 4.9583333333333333) < 1e-12 and x0[2] < b2,
          f"W1 dst2 activity bound {b2:.4f} holds with margin")
    # W2: B and D provably diverge at t0 at BOTH registered timesteps
    for dt_label in o14.DT_LABELS:
        world, x0, u, cfg, dem, dt, _s, _b, cands = \
            menus_at_t0("O14_W2_severity_split", dt_label)
        fs = sorted({round(c["f"], 3) for c in cands})
        check(fs == [1.74, 2.1], f"W2/{dt_label}: forces (2.100, 1.740)")
        pb = o14.select_arm_B(cands)
        exact = [o14.quote_schedule_for(world, x0, u, dt, c, 1)
                 .exact(c["q_acc"]) for c in cands]
        di = o14.select_arm_D(cands, exact)
        check(pb["edge"] == 0 and cands[di]["edge"] == 1,
              f"W2/{dt_label}: B picks edge 0, D picks edge 1 (B != D)")
    _, x0, u, cfg, dem, dt, _s, _b, cands = \
        menus_at_t0("O14_W2_severity_split", "near_certificate")
    world = world_state("O14_W2_severity_split")[0]
    d_quotes = {(c["edge"], c["frac"]):
                o14.quote_schedule_for(world, x0, u, dt, c, 1)
                .exact(c["q_acc"]) for c in cands}
    check(abs(d_quotes[(1, 1.0)] - 0.45554) < 5e-6
          and abs(d_quotes[(0, 1.0)] - 0.22484) < 5e-6,
          "W2/near: registered quote values +0.45554 / +0.22484 reproduced")
    # W3: more EBU from less material; S prefers the high-volume destination
    world, x0, u, cfg, dem, dt, _s, _b, cands = \
        menus_at_t0("O14_W3_volume_split", "near_certificate")
    q1 = next(c for c in cands if c["edge"] == 1 and c["frac"] == 1.0)
    q0 = next(c for c in cands if c["edge"] == 0 and c["frac"] == 1.0)
    dq1 = o14.quote_schedule_for(world, x0, u, dt, q1, 1).exact(q1["q_acc"])
    dq0 = o14.quote_schedule_for(world, x0, u, dt, q0, 1).exact(q0["q_acc"])
    check(q1["q_acc"] < q0["q_acc"] and dq1 > dq0,
          f"W3: chosen q {q1['q_acc']:.3f} < alternative {q0['q_acc']:.3f} "
          f"with larger quote ({dq1:+.4f} > {dq0:+.4f})")
    check(abs(dq1 - 1.94165) < 5e-6 and abs(dq0 - 0.73347) < 5e-6,
          "W3/near: registered quotes +1.94165 / +0.73347 reproduced")
    exact = [o14.quote_schedule_for(world, x0, u, dt, c, 1)
             .exact(c["q_acc"]) for c in cands]
    check(cands[o14.select_arm_D(cands, exact)]["edge"] == 1
          and o14.select_arm_B(cands)["edge"] == 1
          and o14.select_arm_S(cands, dem, world)["edge"] == 0,
          "W3: B and D pick the low-volume dst2; S picks high-volume dst1")
    # W4: budget binds in arm A at both dts (registered sigma values)
    for dt_label, sig_exp, qmax_exp in (("conservative", 0.814, 8.713),
                                        ("near_certificate", 0.575, 6.148)):
        world, x0, u, cfg, dem, dt, state, budget, cands = \
            menus_at_t0("O14_W4_budget_bind", dt_label)
        Js = sorted({round(c["J"], 3) for c in cands})
        sumJ = 4 * 2.675
        check(Js == [2.675], f"W4/{dt_label}: per-edge J = 2.675")
        check(abs(budget - qmax_exp) < 5e-4,
              f"W4/{dt_label}: Q_max = {qmax_exp} (got {budget:.3f})")
        sigma = min(1.0, budget / sumJ)
        check(abs(sigma - sig_exp) < 5e-4 and sumJ > budget,
              f"W4/{dt_label}: sigma_A = {sig_exp}, budget binds")
        check(max(c["q_acc"] for c in cands) < budget,
              f"W4/{dt_label}: restricted single action never budget-limited "
              "(the restriction, not the budget, binds B/C/D/S)")
    # W5: initial ordering and the local reversal-boundary coefficients
    world, x0, u, cfg, dem, dt, _s, _b, cands = \
        menus_at_t0("O14_W5_reversal", "near_certificate")
    fs = sorted({round(c["f"], 3) for c in cands}, reverse=True)
    check(fs == [7.92, 6.48], "W5: initial forces (7.920, 6.480)")
    check(o14.select_arm_B(cands)["edge"] == 0, "W5: B initially edge 0")
    exact = [o14.quote_schedule_for(world, x0, u, dt, c, 1)
             .exact(c["q_acc"]) for c in cands]
    check(cands[o14.select_arm_D(cands, exact)]["edge"] == 0,
          "W5: D initially edge 0")
    c1, c2 = world.cells[1], world.cells[2]
    k1 = 2 * 0.9 * c1.alpha
    k2 = 2 * 0.9 * c2.alpha
    check(abs(k1 - 3.6) < 1e-12 and abs(k2 - 1.44) < 1e-12,
          "W5: reversal boundary 3.6*D1 = 1.44*D2 (coefficients from cells)")
    check(k1 * (c1.L - x0[1]) > k2 * (c2.L - x0[2]),
          "W5: t0 is on the edge-0 side of the reversal boundary")
    # W6: honest infeasibility bound
    world, x0, u, cfg, dem, meta = world_state("O14_W6_infeasible")
    g_max = world.cells[0].rho * world.cells[0].K / 4.0
    check(math.fsum(dem) == 6.0 and 0.9 * g_max == 2.7
          and math.fsum(dem) > 0.9 * g_max and meta["feasible"] is False,
          "W6: demand 6.0 > eta*g_max = 2.7, registered infeasible")


def test_t4():
    group("T4 candidate-count clarification: 96 feasible-audit vs 120 full")
    slots = {}
    for name in o14.WORLD_NAMES:
        world, *_ = o14.build_world(name)
        deg = sum(1 for e in world.edges if e.i == 0)
        slots[name] = deg * len(o14.FRACTIONS) * len(o14.DT_LABELS)
    feasible = [n for n in o14.WORLD_NAMES
                if o14.PLAN["worlds"][n]["feasible"]]
    infeasible = [n for n in o14.WORLD_NAMES
                  if not o14.PLAN["worlds"][n]["feasible"]]
    check(feasible == ["O14_W1_eta_split", "O14_W2_severity_split",
                       "O14_W3_volume_split", "O14_W4_budget_bind",
                       "O14_W5_reversal"] and
          infeasible == ["O14_W6_infeasible"],
          "W1-W5 are the feasible worlds; W6 is the sole infeasible world")
    check(sum(slots[n] for n in feasible) == 96,
          "96 = FEASIBLE-WORLD (W1-W5) boundary-optimality audit slots "
          "(12 edges x 4 levels x 2 dts) - the protocol's '96' scope")
    check(sum(slots.values()) == 120,
          "120 = FULL six-world edge-quantity-timestep slots (15 x 4 x 2)")
    check(slots["O14_W6_infeasible"] == 24,
          "W6 contributes exactly the remaining 24 slots")
    # W6 is not omitted anywhere: enumeration, menu, run reconstruction
    for dt_label in o14.DT_LABELS:
        *_, cands = menus_at_t0("O14_W6_infeasible", dt_label)
        check(len(cands) == 3 * len(o14.FRACTIONS),
              f"W6/{dt_label}: full menu enumerated "
              f"(12 candidates, got {len(cands)})")
    specs = o14.build_run_specs()
    check(sum(1 for s in specs if s["world"] == "O14_W6_infeasible") == 10,
          "W6 present in run reconstruction (10 of 60 runs)")


def test_t5():
    group("T5 timestep certificates (released recomputation, fail closed)")
    for name in o14.WORLD_NAMES:
        got = o14.world_certificates(name)      # itself fail-closed vs plan
        locked = o14.PLAN["timestep"]["per_world"][name]
        check(all(got[k] == locked[k] for k in got),
              f"{name}: recomputed certificates equal locked values exactly")
        dts = o14.world_dts(name)
        for label, r_exp in (("conservative", 0.5), ("near_certificate", 0.9)):
            r = dts[label] / got["binding_certificate"]
            check(abs(r - r_exp) < 1e-12 and r <= 1.0,
                  f"{name}/{label}: r_dt = {r_exp} and <= 1")
    # all arms share dt within a paired world (from two short runs)
    rb = short_run("O14_W2_severity_split", "B_restricted_matched_non_ebu",
                   "near_certificate")
    rc = short_run("O14_W2_severity_split",
                   "C_restricted_observational_quote", "near_certificate")
    check(rb.dt == rc.dt ==
          o14.world_dts("O14_W2_severity_split")["near_certificate"],
          "arms share the single registered dt within a paired world")
    globals()["_RB"], globals()["_RC"] = rb, rc      # reused by T9
    # tampered locked certificate fails closed
    node = o14.PLAN["timestep"]["per_world"]["O14_W1_eta_split"]
    orig = node["binding_certificate"]
    node["binding_certificate"] = orig + 1e-9
    try:
        o14.world_certificates("O14_W1_eta_split")
        check(False, "tampered certificate must fail closed")
    except SystemExit:
        check(True, "tampered locked certificate fails closed")
    finally:
        node["binding_certificate"] = orig
    check(o14.world_certificates("O14_W1_eta_split")
          ["binding_certificate"] == orig, "plan value restored")


def test_t6():
    group("T6 exact quote schedule and arm-D selection")
    world, x0, u, cfg, dem, dt, _s, _b, cands = \
        menus_at_t0("O14_W1_eta_split", "near_certificate")
    c = cands[0]
    sch = o14.quote_schedule_for(world, x0, u, dt, c, 1)
    check(sch.exact(0.0) == 0.0, "q = 0 is the exact zero branch")
    check(o14.select_arm_D(cands, [0.0] * len(cands)) is None
          and o14.select_arm_D(cands, [-1.0] * len(cands)) is None,
          "no strictly positive quote => rest (q = 0), zero/negative alike")
    # exact finite-difference cross-check against a manual recomputation
    e = world.edges[c["edge"]]
    z_i, z_j = x0[e.i] + dt * u[e.i], x0[e.j] + dt * u[e.j]
    def v(cell, val):
        return d0.penalty(cell.alpha, cell.beta, cell.chi,
                          cell.L, cell.U, cell.R, val)
    q = c["q_acc"]
    manual = (v(world.cells[e.i], z_i) + v(world.cells[e.j], z_j)
              - v(world.cells[e.i], z_i - dt * q)
              - v(world.cells[e.j], z_j + dt * e.eta * q)
              - (o14.C0 + o14.LAM_L * dt * (1.0 - e.eta) * q))
    check(abs(sch.exact(q) - manual) < 1e-12 * (1 + abs(manual)),
          "exact quote matches the released finite-difference form")
    # domain discipline and deterministic enumeration over all 120 slots
    inside = ok_det = 0
    increasing_feasible = increasing_all = 0
    boundary_feasible = 0
    for name in o14.WORLD_NAMES:
        feas = o14.PLAN["worlds"][name]["feasible"]
        for dt_label in o14.DT_LABELS:
            w2, xx, uu, cf, dm, dtt, _st, _bu, cds = menus_at_t0(name,
                                                                 dt_label)
            cds2 = menus_at_t0(name, dt_label)[-1]
            ok_det += (cds == cds2)
            inside += all(0.0 < c["q_acc"] <= c["q_e_max"] + 1e-15
                          for c in cds)
            by_edge = {}
            for c in cds:
                by_edge.setdefault(c["edge"], []).append(c)
            quotes = {id(c): o14.quote_schedule_for(w2, xx, uu, dtt, c, 1)
                      .exact(c["q_acc"]) for c in cds}
            inc = all(all(quotes[id(a)] < quotes[id(b)] for a, b in
                          zip(sorted(grp, key=lambda c: c["quant_index"]),
                              sorted(grp, key=lambda c: c["quant_index"])[1:]))
                      for grp in by_edge.values())
            increasing_all += inc
            if feas:
                increasing_feasible += inc
                exact = [quotes[id(c)] for c in cds]
                pick = cds[o14.select_arm_D(cds, exact)]
                boundary_feasible += (pick["quant_index"] ==
                                      len(o14.FRACTIONS) - 1)
    check(ok_det == 12, "menu construction deterministic (12/12 rebuilds)")
    check(inside == 12, "every candidate inside (0, q_e_max] in all menus")
    check(increasing_feasible == 10,
          "96-slot FEASIBLE-WORLD audit: every schedule strictly increasing "
          "across the menu (boundary-optimality lemma scope, W1-W5)")
    check(increasing_all == 12,
          "extended 120-slot audit (W6 included): still strictly increasing "
          "- the protocol conclusion holds in the wider scope")
    check(boundary_feasible == 10,
          "arm D picks the boundary quantity in every feasible world at t0 "
          "(an interior pick would be REPORTED here, never corrected)")
    # negative control: EBU-per-unit ranking must be detectable
    world, x0, u, cfg, dem, dt, _s, _b, cands = \
        menus_at_t0("O14_W2_severity_split", "near_certificate")
    exact = [o14.quote_schedule_for(world, x0, u, dt, c, 1)
             .exact(c["q_acc"]) for c in cands]
    per_unit_pick = max(range(len(cands)),
                        key=lambda i: (exact[i] / cands[i]["q_acc"],
                                       -cands[i]["edge"],
                                       -cands[i]["quant_index"]))
    prod_pick = o14.select_arm_D(cands, exact)
    check(cands[per_unit_pick]["edge"] != cands[prod_pick]["edge"],
          "F8 negative control: a per-unit ranker picks a different edge on "
          "W2, so per-unit ranking would be detected")
    # negative control: the linear diagnostic would act where exact rests
    wsyn = d0.World(
        cells=(d0.Cell(alpha=1.0, beta=0.5, chi=0.0, L=5.0, U=15.0,
                       R=0.0, K=20.0),
               d0.Cell(alpha=1.0, beta=5.0, chi=0.0, L=5.0, U=5.2,
                       R=0.0, K=20.0)),
        edges=(d0.Edge(i=0, j=1, M=0.5, theta=0.05, eta=0.9),))
    xs, us, dts = (10.0, 4.9), (0.0, 0.0), 1.0
    csyn = dict(edge=0, quant_index=0, frac=1.0, f=0.18, J=2.0,
                q_req=2.0, q_e_max=2.0, q_acc=2.0)
    exact_syn = o14.quote_schedule_for(wsyn, xs, us, dts, csyn,
                                       1).exact(2.0)
    linear_syn = dts * 2.0 * 0.18 - (o14.LAM_L * dts * 0.1 * 2.0)
    check(exact_syn < 0.0 < linear_syn,
          "linear-diagnostic negative control: linear says act "
          f"({linear_syn:+.3f}), exact says damage ({exact_syn:+.3f})")
    check(o14.select_arm_D([csyn], [exact_syn]) is None,
          "production D rests on the overshoot fixture (a linear ranker "
          "would act - detected)")
    # identifier-only tie rules
    a = dict(edge=1, quant_index=0, frac=1.0, f=1.0, J=1, q_req=1,
             q_e_max=1, q_acc=1.0)
    b = dict(edge=0, quant_index=0, frac=1.0, f=1.0, J=1, q_req=1,
             q_e_max=1, q_acc=1.0)
    check(o14.select_arm_D([a, b], [2.0, 2.0]) == 1,
          "exact-quote tie -> lower edge index")
    b2 = dict(b, edge=1, quant_index=1)
    check(o14.select_arm_D([b2, a], [2.0, 2.0]) == 1,
          "same-edge tie -> lower quantity-menu index")
    src_d = inspect.getsource(o14.select_arm_D)
    check("continuous_vertex" not in src_d and "q_cont" not in src_d,
          "the continuous vertex cannot affect selection (absent from the "
          "selector)")
    check(o14.continuous_vertex_diagnostic(world, x0, u, dt, cands[0])
          is not None,
          "continuous vertex is still recorded as a diagnostic")


def test_t7():
    group("T7 capability matching (B/C/D/S identical; A excluded)")
    world, x0, cfg, dem, meta = o14.build_world("O14_W2_severity_split")
    dt = o14.world_dts("O14_W2_severity_split")["near_certificate"]
    recs = {arm: o14.o14_tick(world, x0, dt, cfg, dem, arm, 1)
            for arm in o14.EXEC_ARMS}
    menus = {arm: recs[arm]["menus"] for arm in o14.EXEC_ARMS
             if arm != "A_full_multi_edge_p1c"}
    base = menus["B_restricted_matched_non_ebu"]
    check(all(m == base for m in menus.values()),
          "B, C, D and S receive identical candidate menus, budgets and "
          "states at the same tick (F2/F12 invariant)")
    check(recs["B_restricted_matched_non_ebu"]["dt"] ==
          recs["D_restricted_exact_total_quote_greedy"]["dt"],
          "B and D share the timestep")
    # the shared constructor is literal: selectors never build menus
    for fn in (o14.select_arm_B, o14.select_arm_D, o14.select_arm_S):
        check("candidate_menu" not in inspect.getsource(fn),
              f"{fn.__name__} consumes the shared menu, never builds one")
    # capability inequality must be detectable (F2/F12 negative control)
    tampered = copy.deepcopy(base)
    sid = sorted(tampered)[0]
    tampered[sid]["candidates"] = tampered[sid]["candidates"][:-1]
    check(tampered != base,
          "a dropped candidate is detected by the per-tick menu comparison")
    # D's selection is an element of the same menu B saw
    dsel = recs["D_restricted_exact_total_quote_greedy"]["selected"]
    check(any(c == dsel for c in base[sid]["candidates"]),
          "D's selected candidate is an element of B's identical menu")
    check("never the primary" in
          o14.PLAN["arms"]["A_full_multi_edge_p1c"].lower()
          or "not the primary" in
          o14.PLAN["arms"]["A_full_multi_edge_p1c"].lower(),
          "arm A is registered as never the primary comparator")
    check(o14.PLAN["arms"]["primary_comparison"] == "D versus B",
          "primary matched-capability comparison is D versus B")


def test_t8():
    group("T8 request shaping and P1C authority")
    world, x0, cfg, dem, meta = o14.build_world("O14_W1_eta_split")
    u = sv.drive_no_demand(world, x0)
    for dt_label in o14.DT_LABELS:
        dt = o14.world_dts("O14_W1_eta_split")[dt_label]
        sid = 0
        _st, _bu, cands = o14.candidate_menu(world, x0, u, sid,
                                             cfg[sid], dt)
        ok_shape = ok_ident = 0
        for c in cands:
            aw = o14.shaped_active_world(world, c)
            check_edge = aw.edges[0]
            ok_shape += (check_edge.M == c["frac"] *
                         world.edges[c["edge"]].M)
            out = sv.bounded_step(world, x0, dt, cfg, dem, active_world=aw)
            ok_ident += (out.q_acc[0] == c["q_acc"])
        check(ok_shape == len(cands) == 8,
              f"{dt_label}: mobility scaled exactly (frac * M) for all "
              f"{len(cands)} candidates")
        check(ok_ident == len(cands),
              f"{dt_label}: executed q_acc BIT-IDENTICAL to the selected "
              "menu q_acc for every candidate (released p1c_step "
              "regenerates the request itself)")
    # negative control: unscaled mobility executes J, not frac*J
    c_half = next(c for c in cands if c["frac"] == 0.5)
    e = world.edges[c_half["edge"]]
    aw_bad = d0.World(cells=world.cells, edges=(e,))       # full mobility
    out_bad = sv.bounded_step(world, x0, dt, cfg, dem, active_world=aw_bad)
    check(out_bad.q_acc[0] != c_half["q_acc"],
          "negative control: WITHOUT scaling, executed q != selected q "
          "(the shaping is load-bearing, not cosmetic)")
    # budget authority is never bypassed (W4, arm A, both dts)
    world4, x04, cfg4, dem4, _m = o14.build_world("O14_W4_budget_bind")
    for dt_label in o14.DT_LABELS:
        dt4 = o14.world_dts("O14_W4_budget_bind")[dt_label]
        rec = o14.o14_tick(world4, x04, dt4, cfg4, dem4,
                           "A_full_multi_edge_p1c", 1)
        tot_acc = math.fsum(rec["executed_q_acc"])
        sig = list(rec["sigma"].values())[0]
        util = list(rec["budget_utilization"].values())[0]
        u4 = sv.drive_no_demand(world4, x04)
        qmax = p1c.robust_budget(cfg4[0], x04[0], u4[0], dt4)
        check(sig < 1.0 and tot_acc <= qmax * (1 + 1e-12),
              f"W4/{dt_label}: arm A sigma < 1 and total accepted <= Q_max "
              "(aggregate budget authoritative)")
        check(abs(util - 1.0) < 1e-9,
              f"W4/{dt_label}: binding => full budget utilization")
    # q_req, q_acc and delivered eta*q_acc are distinguished
    rec = o14.o14_tick(world, x0, dt, cfg, dem,
                       "B_restricted_matched_non_ebu", 1)
    eta_sel = world.edges[rec["selected"]["edge"]].eta
    check(rec["delivered"][0] == eta_sel * rec["executed_q_acc"][0]
          and rec["q_req"][0] >= rec["executed_q_acc"][0],
          "q_req >= q_acc; delivered = eta * q_acc (distinguished fields)")


def test_t9():
    group("T9 arm B/C observational identity (short horizon)")
    rb, rc = globals()["_RB"], globals()["_RC"]        # from T5, SHORT ticks
    phys = ("service", "unmet", "demand", "burden", "viability", "actions",
            "q_acc", "loss", "min_source", "corrections", "ledger",
            "selected_edge", "service_by_dest", "unmet_by_dest")
    check(all(rb.series[k] == rc.series[k] for k in phys),
          "byte-identical physical series for B and C over the short "
          "horizon (any difference fires F1)")
    check(rb.final["x"] == rc.final["x"]
          and rb.x_trajectory_tail == rc.x_trajectory_tail,
          "byte-identical final states")
    check(rb.totals["ebu"] == 0.0 and rc.totals["ebu"] != 0.0,
          "B carries no EBU; C settles observationally (evaluation "
          "variable, not a wallet)")
    check(rc.totals["quoted"] == rc.totals["accepted"] > 0,
          "C quote coverage 1.0 over accepted actions")
    world, x0, cfg, dem, _m = o14.build_world("O14_W2_severity_split")
    dt = o14.world_dts("O14_W2_severity_split")["near_certificate"]
    rec_c = o14.o14_tick(world, x0, dt, cfg, dem,
                         "C_restricted_observational_quote", 1)
    rec_b = o14.o14_tick(world, x0, dt, cfg, dem,
                         "B_restricted_matched_non_ebu", 1)
    check(rec_c["selected"] == rec_b["selected"],
          "C's selection IS B's selection")
    check(rec_c["candidate_exact_quotes"] and
          len(list(rec_c["candidate_exact_quotes"].values())[0]) ==
          len(list(rec_c["menus"].values())[0]["candidates"]),
          "C records the complete candidate-menu quote diagnostics")
    check(rec_c["x_after"] == rec_b["x_after"]
          and rec_c["service"] == rec_b["service"]
          and rec_c["unmet"] == rec_b["unmet"]
          and rec_c["executed_q_acc"] == rec_b["executed_q_acc"],
          "per-tick physical records byte-identical despite C's quoting")


def test_t10():
    group("T10 arm A and the settlement-free aggregate diagnostic")
    world, x0, cfg, dem, _m = o14.build_world("O14_W4_budget_bind")
    dt = o14.world_dts("O14_W4_budget_bind")["near_certificate"]
    rec = o14.o14_tick(world, x0, dt, cfg, dem, "A_full_multi_edge_p1c", 1)
    check(sum(1 for q in rec["executed_q_acc"] if q > 0.0) == 4,
          "arm A keeps all four requests simultaneously active")
    accs = rec["executed_q_acc"]
    reqs = rec["q_req"]
    sig = list(rec["sigma"].values())[0]
    check(all(abs(a - sig * r) < 1e-15 for a, r in zip(accs, reqs)),
          "proportional sigma scaling applied per edge")
    g = rec["group_diagnostic"]
    check(g is not None and g["n_actions"] == 4,
          "group diagnostic recorded for the executed multi-edge set")
    check(g["double_count"] >= -1e-12,
          "naive independent sum >= exact group quote (Prop 10.2; a "
          "violation fires F9)")
    check(rec["ebu"] == 0.0 and rec["quoted"] == 0,
          "NOTHING is settled or allocated in arm A (O3 stays open)")
    # registered counterexample: source at x = 4, two Delta t q = 2 actions
    wcx = d0.World(
        cells=(d0.Cell(alpha=1.0, beta=0.5, chi=0.0, L=5.0, U=100.0,
                       R=0.0, K=200.0),
               d0.Cell(alpha=1.0, beta=0.5, chi=0.0, L=5.0, U=15.0,
                       R=0.0, K=20.0),
               d0.Cell(alpha=1.0, beta=0.5, chi=0.0, L=5.0, U=15.0,
                       R=0.0, K=20.0)),
        edges=(d0.Edge(i=0, j=1, M=0.5, theta=0.0, eta=1.0),
               d0.Edge(i=0, j=2, M=0.5, theta=0.0, eta=1.0)))
    gd = o14.group_quote_diagnostic(wcx, (4.0, 10.0, 10.0), (0.0, 0.0, 0.0),
                                    1.0, (2.0, 2.0), 1)
    check(gd["naive_independent_sum"] == -16.0,
          "counterexample: naive independent damage = 16")
    check(gd["group_quote"] == -24.0,
          "counterexample: true joint damage = 24")
    check(gd["double_count"] == 8.0,
          "counterexample: independent quotes under-charge by exactly 8")
    src = inspect.getsource(o14.group_quote_diagnostic)
    check("EpochRegistry" not in src and ".settle(" not in src
          and ".register(" not in src,
          "the diagnostic contains no settlement path (no registry, no "
          "settle call)")


def test_t11():
    group("T11 arm S (registered local service-priority comparator)")
    world, x0, cfg, dem, _m = o14.build_world("O14_W3_volume_split")
    u = sv.drive_no_demand(world, x0)
    dt = o14.world_dts("O14_W3_volume_split")["near_certificate"]
    _st, _bu, cands = o14.candidate_menu(world, x0, u, 0, cfg[0], dt)
    pick = o14.select_arm_S(cands, dem, world)
    check(pick["edge"] == 0 and pick["frac"] == 1.0,
          "W3: S selects the registered high-volume destination (edge 0)")
    scores = [world.edges[c["edge"]].eta * c["q_acc"] *
              (1.0 if dem[world.edges[c["edge"]].j] > 0 else 0.0)
              for c in cands]
    best = max(range(len(cands)),
               key=lambda i: (scores[i], -cands[i]["edge"],
                              -cands[i]["quant_index"]))
    check(cands[best] == pick, "score is exactly eta*q_acc*1[d_j>0]")
    check(o14.select_arm_S(cands, tuple(0.0 for _ in dem), world) is None,
          "zero declared demand everywhere => S rests")
    ca = dict(edge=0, quant_index=1, frac=0.5, f=1.0, J=2, q_req=1,
              q_e_max=2, q_acc=1.0)
    cb = dict(edge=1, quant_index=0, frac=0.5, f=1.0, J=2, q_req=1,
              q_e_max=2, q_acc=1.0)
    w2 = d0.World(cells=world.cells[:3],
                  edges=(d0.Edge(0, 1, M=0.5, theta=0.0, eta=0.9),
                         d0.Edge(0, 2, M=0.5, theta=0.0, eta=0.9)))
    tie = o14.select_arm_S([cb, ca], (0.0, 1.0, 1.0), w2)
    check(tie["edge"] == 0, "equal scores => lower edge index wins")
    src = inspect.getsource(o14.select_arm_S)
    check("x[" not in src and "local_view" not in src
          and "burden" not in src and "V_total" not in src,
          "S reads no stock buffer, no LocalView, no global objective")


def test_t12():
    group("T12 bounded service, ledgers, corrected reserve tolerance")
    src = open("o14_v30.py").read()
    check("sv.bounded_step" in src and "def bounded_step" not in src,
          "released Gate 1D bounded_step is reused, never forked")
    check("sv.reserve_crossing" in src and "def reserve_crossing" not in src
          and "def materially_below_reserve" not in src,
          "Gate 1D-A corrected reserve predicates reused, never forked")
    check("def classify_outcome" not in src
          and "def service_alignment_predicate" not in src,
          "Gate 1D classification and predicate are NOT re-implemented")
    world, x0, cfg, dem, _m = o14.build_world("O14_W6_infeasible")
    dt = o14.world_dts("O14_W6_infeasible")["near_certificate"]
    x = x0
    ok_id = ok_bounds = ok_led = ok_nonneg = ok_loss = 0
    N_TICKS = 12  # short non-study horizon: D rotates destinations (the
    #               deepest deficit quotes highest), so W6 stocks run dry
    #               at tick 10 at the near dt; 12 ticks << the 200 horizon
    for t in range(1, N_TICKS + 1):
        rec = o14.o14_tick(world, x, dt, cfg, dem,
                           "D_restricted_exact_total_quote_greedy", t)
        ok_id += all(abs(un - (dm - sv_)) < 1e-15 for un, dm, sv_
                     in zip(rec["unmet"], rec["demand_amount"],
                            rec["service"]))
        ok_bounds += all(0.0 <= s <= dm + 1e-15 for s, dm
                         in zip(rec["service"], rec["demand_amount"]))
        ok_nonneg += all(v >= 0.0 for v in rec["x_after"])
        ok_led += abs(rec["ledger_residual"]) < sv.tol(0.0) * 10
        aw = (o14.shaped_active_world(world, rec["selected"])
              if rec["selected"] else None)
        if aw and aw.edges:
            ok_loss += abs(rec["transport_loss"] -
                           dt * (1 - aw.edges[0].eta) *
                           rec["executed_q_acc"][0]) < 1e-15
        x = tuple(rec["x_after"])
    check(ok_id == N_TICKS, "unmet = demand - service exactly, every tick")
    check(ok_bounds == N_TICKS,
          "service <= demand (and <= available) every tick")
    check(ok_nonneg == N_TICKS, "non-negative states (no phantom stock)")
    check(ok_led == N_TICKS,
          "exact ledger closure within the locked tolerance")
    check(ok_loss == N_TICKS, "named transport loss = dt*(1-eta)*q_acc")
    check(math.fsum(rec["unmet"]) > 0.0,
          "W6 exposes explicit unmet demand under scarcity (H8)")
    ulp = math.nextafter(8.0, -math.inf)
    check(not sv.materially_below_reserve(ulp, 8.0)
          and not sv.reserve_crossing(8.5, ulp, 8.0),
          "one-ULP negative control: no reserve crossing under the "
          "corrected Gate 1D-A tolerance")
    check(sv.reserve_crossing(8.5, 7.0, 8.0),
          "a genuine material breach still counts")
    check("capacity-caused service reduction must never be labelled quote "
          "misalignment" in
          o14.PLAN["service_alignment_predicate"]["prohibitions"],
          "the capacity-vs-quote attribution prohibition is locked")


def test_t13():
    group("T13 information boundary (AST + runtime poison)")
    banned = ("V_total", "wallet", "health", "price", "market",
              "personal_debt", "learning", "migration", "viability",
              "classify_outcome", "service_alignment_predicate",
              "group_quote_diagnostic", "run_arm", "rollout")
    for fn in o14.DECISION_PATH_FUNCS:
        src = inspect.getsource(fn)
        hits = [b for b in banned if b in src]
        check(not hits,
              f"decision path {fn.__name__}: no forbidden identifier {hits}")
    tree = ast.parse(open("o14_v30.py").read())
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom):
            imported.add((node.module or "").split(".")[0])
    check(imported <= {"__future__", "hashlib", "json", "math", "typing",
                       "d0_v29", "p1c_v29", "ebu_quote_v30", "service_v30"},
          f"o14_v30 imports only released modules + stdlib ({imported})")
    # runtime poison: global/forbidden access must raise if ever touched
    world, x0, cfg, dem, _m = o14.build_world("O14_W1_eta_split")
    u = sv.drive_no_demand(world, x0)
    dt = o14.world_dts("O14_W1_eta_split")["conservative"]

    def _poison(*_a, **_k):
        raise AssertionError("decision path touched a forbidden global")
    saved = (d0.V_total, sv.service_alignment_predicate, sv.classify_outcome)
    try:
        d0.V_total = _poison
        sv.service_alignment_predicate = _poison
        sv.classify_outcome = _poison
        _st, _bu, cands = o14.candidate_menu(world, x0, u, 0, cfg[0], dt)
        exact = [o14.quote_schedule_for(world, x0, u, dt, c, 1)
                 .exact(c["q_acc"]) for c in cands]
        pb = o14.select_arm_B(cands)
        pd = o14.select_arm_D(cands, exact)
        ps = o14.select_arm_S(cands, dem, world)
        check(pb is not None and pd is not None and ps is not None,
              "selection completes with the forbidden globals poisoned "
              "(only permitted local information was read)")
    finally:
        d0.V_total, sv.service_alignment_predicate, sv.classify_outcome = \
            saved
    check(d0.V_total is saved[0], "poison restored")
    for f in ("actor_v30.py", "wallet_v30.py", "health_v30.py",
              "market_v30.py", "migration_v30.py", "gate2_v30.py"):
        check(not os.path.exists(f), f"no {f} exists (Gate 2 paused)")


def test_t14():
    group("T14 metrics, predicates, serialization")
    plan_metrics = o14.PLAN["metrics_per_run"]
    check(set(plan_metrics) == set(o14.METRIC_FIELDS),
          "every plan-registered metric line has a registered field mapping")
    world, x0, cfg, dem, _m = o14.build_world("O14_W2_severity_split")
    dt = o14.world_dts("O14_W2_severity_split")["near_certificate"]
    rec_d = o14.o14_tick(world, x0, dt, cfg, dem,
                         "D_restricted_exact_total_quote_greedy", 1)
    world4, x04, cfg4, dem4, _m4 = o14.build_world("O14_W4_budget_bind")
    dt4 = o14.world_dts("O14_W4_budget_bind")["conservative"]
    rec_a = o14.o14_tick(world4, x04, dt4, cfg4, dem4,
                         "A_full_multi_edge_p1c", 1)
    have = set(rec_d) | set(rec_a)
    missing = [m for m, fields in o14.METRIC_FIELDS.items()
               if not all(f in have for f in fields)]
    check(not missing, f"all mapped metric fields present ({missing})")
    check(rec_d["group_diagnostic"] is None
          and rec_a["group_diagnostic"] is not None,
          "group diagnostic present exactly on arm-A records")
    check(list(o14.PLAN["hypotheses"]) ==
          sorted(f"H{i}" for i in range(1, 11)),
          "H1-H10 identifiers complete and unchanged")
    check(list(o14.PLAN["falsifiers"]) ==
          sorted(f"F{i}" for i in range(1, 16)),
          "F1-F15 identifiers complete and unchanged")
    check("VERBATIM" in o14.PLAN["service_alignment_predicate"]["reuse"]
          and o14.PLAN["outcome_classes"]["reuse"].startswith(
              "Gate 1D locked precedence verbatim"),
          "Gate 1D predicate and precedence locked as verbatim reuse")
    check(tuple(sv.PRECEDENCE) == (
        "numerical_or_domain_failure", "systemic_collapse",
        "destructive_service", "physical_impossibility",
        "distributive_or_policy_under_service",
        "safe_rationing_physical_scarcity", "preserve_but_under_serve",
        "preserve_and_serve", "unclassified"),
          "released precedence order intact")
    try:
        o14.strict_json_dumps({"x": float("nan")})
        check(False, "NaN must not serialize")
    except ValueError:
        check(True, "strict serialization rejects non-finite values")
    blob = o14.strict_json_dumps(dict(rec_d, menus=None,
                                      candidate_continuous_vertices=None))
    check(blob == o14.strict_json_dumps(dict(rec_d, menus=None,
                                             candidate_continuous_vertices=None)),
          "deterministic serialization (identical rebuild)")
    check(not any("wallet" in k for k in rec_d),
          "EBU fields are evaluation variables; no wallet exists")


def test_t15():
    group("T15 determinism and the no-study-execution guard")
    check(o14.build_run_specs() == o14.build_run_specs(),
          "run reconstruction deterministic")
    world, x0, cfg, dem, _m = o14.build_world("O14_W5_reversal")
    dt = o14.world_dts("O14_W5_reversal")["conservative"]
    r1 = o14.o14_tick(world, x0, dt, cfg, dem,
                      "D_restricted_exact_total_quote_greedy", 1)
    r2 = o14.o14_tick(world, x0, dt, cfg, dem,
                      "D_restricted_exact_total_quote_greedy", 1)
    check(r1 == r2, "repeated selection and tick records identical")
    import importlib
    before = set(os.listdir(".")) | set(os.listdir("results/v3.0"))
    importlib.reload(o14)
    after = set(os.listdir(".")) | set(os.listdir("results/v3.0"))
    check(before == after, "importing o14_v30 creates no file (no side "
                           "effects)")
    check(not os.path.exists("exp_v30_o14.py"),
          "no runner exists at this stage")
    check(not os.path.exists("results/v3.0/gate1db"),
          "no result directory or artifact was created")
    check(not any(os.path.exists(p) for p in
                  ("v30_o14_summary.json", "v30_o14_trace.jsonl.gz",
                   "v30_o14_stdout.txt")),
          "no experiment summary, trace, stdout or manifest exists")
    # AST self-guard: no registered-horizon call, no full-study sweep
    tree = ast.parse(open("test_v30_o14.py").read())
    tick_consts = []
    run_arm_calls = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fn = node.func
            nm = fn.attr if isinstance(fn, ast.Attribute) else (
                fn.id if isinstance(fn, ast.Name) else "")
            if nm == "run_arm":
                run_arm_calls += 1
                kw = {k.arg: k.value for k in node.keywords}
                check("ticks" in kw,
                      "every run_arm call passes an explicit short horizon")
                if "ticks" in kw and isinstance(kw["ticks"], ast.Name):
                    tick_consts.append(SHORT)
                elif "ticks" in kw and isinstance(kw["ticks"], ast.Constant):
                    tick_consts.append(kw["ticks"].value)
    check(SHORT < o14.RUN_TICKS
          and all(t < o14.RUN_TICKS for t in tick_consts),
          f"no test approaches the registered 200-tick horizon "
          f"(SHORT={SHORT}, horizons={sorted(set(tick_consts))})")
    check(run_arm_calls <= 3,
          f"only {run_arm_calls} short trajectory call site(s); the 60-run "
          "study is never swept")
    check(TRAJECTORIES_RUN < 60 and TRAJECTORIES_RUN <= 4,
          f"only {TRAJECTORIES_RUN} short non-study trajectories were run "
          "(never the 60 specifications)")
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom):
            imported.add((node.module or "").split(".")[0])
    check(not any(m.startswith("exp_v30") for m in imported),
          "no runner is imported by this suite")


if __name__ == "__main__":
    print("EBP V3.0 Gate 1D-B / O14 - PRE-EXECUTION suite "
          f"(plan {PLAN_CANONICAL[:12]}...)")
    print("The registered 60-run study is NOT executed by this suite.\n")
    for fn in (test_t1, test_t2, test_t3, test_t4, test_t5, test_t6,
               test_t7, test_t8, test_t9, test_t10, test_t11, test_t12,
               test_t13, test_t14, test_t15):
        fn()
    print()
    for k, (title, p, f) in enumerate(GROUPS, 1):
        print(f"group {k:>2}: {p:>3} passed, {f} failed - {title}")
    print(f"total checks: {PASS} passed, {FAIL} failed in {len(GROUPS)} "
          "groups")
    print("Numerical validation is not proof: nothing here proves "
          "alignment, safety, the boundary-optimality lemma in general, "
          "O3, O12 or O13; no registered study ran.")
    if FAIL:
        raise SystemExit(1)
