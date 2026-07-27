"""
Conformance validation for p1c_v29.py (V2.9 Gate 2.2).

Passing tests validate the LOCAL PHYSICAL CONFORMANCE of the P1C preservation
controller against Amendment 4 (Sec 20) and the Gate-2.1B review (Theorem 4.1).
They are NOT a proof: they do NOT establish global stability, long-run
sustainability, the infinite-horizon viability kernel, service success under
arbitrary demand, D9/D10 success, ecological-debt/restoration-credit/scalar-EBU
validity, or adversarial security. A passing run validates the tested points
only.

P1C is OUTSIDE the V2.8 theorem. The D0 reference used in group 9 is the frozen
d0_v29.d0_step (compared against, not reimplemented). Plain stdlib, direct
execution:  python3 test_v29_p1c.py
"""
from __future__ import annotations
import ast
import math
import random
import sys

import d0_v29 as d0
import p1c_v29 as p1c

# Fixed regression seed, distinct from behavioral exploratory (0-9), confirmatory
# (100-139), V2.8 (20260726), and V2.9 conformance (29001). Numerical conformance
# validation only - NOT a behavioral experiment.
P1C_SEED = 29002

PASS = 0
FAIL = 0
GROUPS: list[list] = []
WORST = {"preservation": 0.0, "ledger": 0.0, "permutation": 0.0,
         "d0_conformance": 0.0, "budget": 0.0, "proportion": 0.0}
STATS = {"fixtures": 0, "active_edges": 0, "binding": 0, "state_P": 0,
         "state_R": 0, "state_I": 0, "state_F": 0}


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


def band_cell(alpha=1.0, beta=0.5, chi=0.0, L=5.0, U=15.0, R=0.0, K=20.0, **drive):
    return d0.Cell(alpha=alpha, beta=beta, chi=chi, L=L, U=U, R=R, K=K, **drive)


def reg(cell_id, R_eff, eps_x=0.0, eps_u=0.0):
    return p1c.SourceConfig(cell_id, "regenerative", R_eff=R_eff,
                            eps_x=eps_x, eps_u=eps_u)


# ===========================================================================
# [1] validation and units
# ===========================================================================
def test_group1():
    group("validation and units")
    w = d0.World(cells=(band_cell(), band_cell()),
                 edges=(d0.Edge(0, 1, 0.5, 0.05, 0.9),))
    cfgs = {0: reg(0, 8.0)}
    bad = [
        ("dt = 0", lambda: p1c.p1c_step(w, [10.0, 10.0], 0.0, cfgs)),
        ("dt < 0", lambda: p1c.p1c_step(w, [10.0, 10.0], -0.1, cfgs)),
        ("NaN state", lambda: p1c.p1c_step(w, [math.nan, 10.0], 0.5, cfgs)),
        ("inf state", lambda: p1c.p1c_step(w, [math.inf, 10.0], 0.5, cfgs)),
        ("state length mismatch", lambda: p1c.p1c_step(w, [10.0], 0.5, cfgs)),
        ("negative eps_x", lambda: reg(0, 8.0, eps_x=-0.1)),
        ("negative eps_u", lambda: reg(0, 8.0, eps_u=-0.1)),
        ("bad source_type", lambda: p1c.SourceConfig(0, "magic", R_eff=8.0)),
        ("regen without R_eff", lambda: p1c.SourceConfig(0, "regenerative")),
        ("flow without cap", lambda: p1c.SourceConfig(0, "flow")),
        ("flow with R_eff", lambda: p1c.SourceConfig(0, "flow", R_eff=8.0,
                                                     flow_cap=1.0)),
        ("flow_cap on stock", lambda: p1c.SourceConfig(0, "regenerative",
                                                       R_eff=8.0, flow_cap=1.0)),
        ("negative flow_cap", lambda: p1c.SourceConfig(0, "flow", flow_cap=-1.0)),
        ("negative num_tol", lambda: reg(0, 8.0).__class__(0, "regenerative",
                                    R_eff=8.0, num_tol=-1.0)),
        ("config key != id", lambda: p1c.p1c_step(w, [10.0, 10.0], 0.5,
                                                  {1: reg(0, 8.0)})),
        ("config out of range", lambda: p1c.p1c_step(w, [10.0, 10.0], 0.5,
                                                     {5: reg(5, 8.0)})),
        ("configs not mapping", lambda: p1c.p1c_step(w, [10.0, 10.0], 0.5,
                                                     [reg(0, 8.0)])),
        ("unconfigured exporter", lambda: p1c.p1c_step(
            d0.World(cells=(band_cell(), band_cell()),
                     edges=(d0.Edge(0, 1, 1.0, 0.0, 1.0),)), [19.0, 2.0], 0.5, {})),
    ]
    for name, fn in bad:
        try:
            fn()
            ok = False
        except (ValueError, TypeError):
            ok = True
        check(f"rejects {name}", ok)
    # units: budget is a RATE; Q_max*dt is a stock amount consistent with the step
    r = p1c.p1c_step(w, [19.0, 2.0], 0.5, cfgs)
    s = r.sources[0]
    check("robust_budget is a rate: Q_max*dt = usable-stock-above-reserve",
          abs(s.Q_max * 0.5 - ((19.0 + 0.5 * s.u) - 8.0)) < 1e-9,
          f"Q_max={s.Q_max:.4f}")
    check("valid source types accepted",
          all(p1c.SourceConfig(0, t, R_eff=(None if t == 'flow' else 8.0),
                               flow_cap=(1.0 if t == 'flow' else None))
              for t in p1c.SOURCE_TYPES))


# ===========================================================================
# [2] state classification (P/R/I/F, incl. Gate 2.1B counterexample)
# ===========================================================================
def test_group2():
    group("state classification P/R/I/F")
    dt = 1.0
    # State P: x>=R and x+dt u>=R
    check("P: x>=R and no-export successor >= R",
          p1c.classify_state(reg(0, 8.0), 12.0, 0.5, dt) == "P")
    # State R: x<R
    check("R: x<R (regardless of drive)",
          p1c.classify_state(reg(0, 8.0), 7.0, 5.0, dt) == "R")
    # State I: x>=R but x+dt u<R -- the Gate 2.1B counterexample x=R, u<0
    check("I: x=R, u<0 -> clamped budget 0 but reserve still breached",
          p1c.classify_state(reg(0, 10.0), 10.0, -1.0, dt) == "I")
    # verify the counterexample end-to-end: State I, zero export, x_after<R
    wI = d0.World(cells=(band_cell(d=1.0),), edges=())  # u = -1
    rI = p1c.p1c_step(wI, [10.0], 1.0, {0: reg(0, 10.0)})
    sI = rI.sources[0]
    check("counterexample: State I, zero export, successor 9 < R=10",
          sI.state == "I" and sI.Q_acc == 0.0 and rI.x_after[0] == 9.0
          and sI.reserve_boundary_ok is False)
    # tolerance-near boundary: x+dt u exactly R -> P (>= is inclusive)
    check("near-boundary: x+dt u == R exactly classifies P",
          p1c.classify_state(reg(0, 10.0), 10.0, 0.0, dt) == "P")
    check("just-below boundary: x+dt u = R - tiny classifies I",
          p1c.classify_state(reg(0, 10.0), 10.0, -1e-9, dt) == "I")
    # State F: flow type
    fcfg = p1c.SourceConfig(0, "flow", flow_cap=1.0)
    check("F: flow source classifies F regardless of stock",
          p1c.classify_state(fcfg, 3.0, -2.0, dt) == "F"
          and p1c.classify_state(fcfg, 30.0, 5.0, dt) == "F")
    # State F budget: min(flow_cap, [x+dt u]_+/dt), enforced with real export
    wF = d0.World(cells=(band_cell(), band_cell()),
                  edges=(d0.Edge(0, 1, 2.0, 0.0, 0.9),))
    rF = p1c.p1c_step(wF, [19.0, 2.0], 1.0,
                      {0: p1c.SourceConfig(0, "flow", flow_cap=0.5)})
    sF = rF.sources[0]
    check("F: flow-cap binds accepted export (Q_acc <= flow_cap)",
          sF.state == "F" and sF.Q_acc <= 0.5 + 1e-12 and sF.Q_max == 0.5)
    # F with tiny stock: budget bounded by available stock (no phantom stock)
    rF2 = p1c.p1c_step(wF, [0.2, 2.0], 1.0,
                       {0: p1c.SourceConfig(0, "flow", flow_cap=100.0)})
    check("F: budget bounded by available [x+dt u]_+/dt (no phantom stock)",
          abs(rF2.sources[0].Q_max - 0.2) < 1e-12 and rF2.x_after[0] >= -1e-12)


# ===========================================================================
# [3] safe-budget formula (direct numerical evaluation)
# ===========================================================================
def test_group3():
    group("robust safe-budget formula")
    # baseline: x=19, u=0.4, R=8, dt=0.5, eps=0
    b0 = p1c.robust_budget(reg(0, 8.0), 19.0, 0.4, 0.5)
    check("baseline Q_max = [x + dt u - R]_+/dt",
          abs(b0 - ((19.0 + 0.5 * 0.4 - 8.0) / 0.5)) < 1e-12, f"{b0:.6f}")
    # eps_x lowers the budget by eps_x/dt
    bx = p1c.robust_budget(reg(0, 8.0, eps_x=0.3), 19.0, 0.4, 0.5)
    check("eps_x reduces budget by eps_x/dt", abs((b0 - bx) - 0.3 / 0.5) < 1e-12)
    # eps_u lowers the budget by eps_u (a rate)
    bu = p1c.robust_budget(reg(0, 8.0, eps_u=0.2), 19.0, 0.4, 0.5)
    check("eps_u reduces budget by eps_u", abs((b0 - bu) - 0.2) < 1e-12)
    # dt: with the same stock margin, smaller dt gives a larger rate
    bsmall = p1c.robust_budget(reg(0, 8.0), 19.0, 0.0, 0.1)
    blarge = p1c.robust_budget(reg(0, 8.0), 19.0, 0.0, 1.0)
    check("smaller dt -> larger rate for fixed stock margin", bsmall > blarge)
    # reserve: higher R lowers budget
    check("higher reserve lowers budget",
          p1c.robust_budget(reg(0, 12.0), 19.0, 0.0, 0.5) <
          p1c.robust_budget(reg(0, 8.0), 19.0, 0.0, 0.5))
    # positive drive raises, negative drive lowers
    bp = p1c.robust_budget(reg(0, 8.0), 12.0, +1.0, 0.5)
    bn = p1c.robust_budget(reg(0, 8.0), 12.0, -1.0, 0.5)
    check("positive drive raises budget, negative lowers", bp > bn)
    # clamp: deeply negative margin gives exactly zero, never negative
    bz = p1c.robust_budget(reg(0, 8.0), 8.0, -5.0, 1.0)
    check("budget clamps at zero (never negative)", bz == 0.0)
    # seeded random cross-check of the closed form
    rng = random.Random(P1C_SEED + 3)
    worst = 0.0
    for _ in range(200):
        x = rng.uniform(-5, 25); u = rng.uniform(-3, 3); R = rng.uniform(0, 15)
        ex = rng.choice([0.0, rng.uniform(0, 1)]); eu = rng.choice([0.0, rng.uniform(0, 1)])
        dt = rng.choice([0.1, 0.25, 0.5, 1.0])
        got = p1c.robust_budget(reg(0, R, eps_x=ex, eps_u=eu), x, u, dt)
        num = (x - ex) + dt * (u - eu) - R
        want = max(0.0, num) / dt
        worst = max(worst, abs(got - want))
    WORST["budget"] = worst
    check("closed-form matches independent recompute over 200 random cases",
          worst < 1e-12, f"max |diff| {worst:.2e}")


# ===========================================================================
# [4] multi-edge proportional allocation
# ===========================================================================
def _fan_world(k, eta=0.9, M=1.0, theta=0.0):
    cells = [band_cell()] + [band_cell() for _ in range(k)]
    edges = tuple(d0.Edge(0, j + 1, M, theta, eta) for j in range(k))
    return d0.World(cells=tuple(cells), edges=edges)


def test_group4():
    group("multi-edge proportional allocation")
    for k in (1, 2, 5, 23):
        w = _fan_world(k)
        x = [19.0] + [1.0 + 0.3 * j for j in range(k)]   # varied deficits
        # bind the budget with a tight reserve
        r = p1c.p1c_step(w, x, 0.5, {0: reg(0, 18.0)})
        s = r.sources[0]
        Qacc = math.fsum(e.q_acc for e in r.edges)
        check(f"k={k}: aggregate accepted <= budget",
              Qacc <= s.Q_max + 1e-12 * (1 + s.Q_max),
              f"Qacc={Qacc:.6f} Qmax={s.Q_max:.6f}")
        # relative proportions preserved when scaling active
        if s.sigma < 1.0 and s.Q_req > 0:
            worst = max(abs(e.q_acc - s.sigma * e.q_req) for e in r.edges)
            WORST["proportion"] = max(WORST["proportion"], worst)
            check(f"k={k}: q_acc == sigma*q_req on every edge (proportions kept)",
                  worst < 1e-12, f"max dev {worst:.2e}, sigma={s.sigma:.4f}")
            check(f"k={k}: scaling is active (sigma<1)", True,
                  f"sigma={s.sigma:.4f}")
    # non-binding: reserve far below stock so the budget never binds
    w = _fan_world(5)
    r = p1c.p1c_step(w, [19.0, 1, 1, 1, 1, 1], 0.5, {0: reg(0, -1e6)})
    check("non-binding source: sigma == 1, q_acc == q_req",
          r.sources[0].sigma == 1.0
          and all(e.q_acc == e.q_req for e in r.edges),
          f"sigma={r.sources[0].sigma}")
    # zero request: sigma == 0, no export
    w2 = _fan_world(3)
    # all destinations in-band and source in-band -> theta gate keeps J=0
    r2 = p1c.p1c_step(w2, [10.0, 11.0, 11.0, 11.0], 0.5, {0: reg(0, 5.0)},)
    check("zero aggregate request: sigma == 0, no export",
          r2.sources[0].Q_req == 0.0 and r2.sources[0].sigma == 0.0
          and all(e.q_acc == 0.0 for e in r2.edges))


# ===========================================================================
# [5] permutation invariance
# ===========================================================================
def test_group5():
    group("permutation invariance of allocation and physical result")
    rng = random.Random(P1C_SEED + 5)
    worst = 0.0
    tested = 0
    for k in (3, 5, 23):
        w = _fan_world(k)
        x = [19.0] + [rng.uniform(0.0, 4.0) for _ in range(k)]
        base = p1c.p1c_step(w, x, 0.5, {0: reg(0, 17.5)})
        base_acc = sorted(e.q_acc for e in base.edges)
        tol = 1e-12 * (1.0 + max(abs(v) for v in base.x_after))
        for _ in range(8):
            perm = list(range(k)); rng.shuffle(perm)
            wp = d0.World(cells=w.cells, edges=tuple(w.edges[i] for i in perm))
            rp = p1c.p1c_step(wp, x, 0.5, {0: reg(0, 17.5)})
            dev = max(abs(a - b) for a, b in zip(rp.x_after, base.x_after))
            dev = max(dev, abs(rp.sources[0].Q_acc - base.sources[0].Q_acc))
            dev = max(dev, max(abs(a - b) for a, b in
                               zip(sorted(e.q_acc for e in rp.edges), base_acc)))
            worst = max(worst, dev)
            tested += 1
            if dev > tol:
                check(f"k={k}: permutation within tolerance", False,
                      f"dev {dev:.2e} > tol {tol:.2e}")
                return
    WORST["permutation"] = worst
    check(f"{tested} permutations agree within strict scale-aware tolerance",
          True, f"max residual {worst:.3e} (bit identity not promised cross-platform)")


# ===========================================================================
# [6] one-step preservation theorem conformance (direct state evaluation)
# ===========================================================================
def test_group6():
    group("one-step preservation theorem conformance (Gate-2.1B Thm 4.1)")
    # deterministic binding fixture with ACTIVE incoming to the source (the
    # theorem uses I>=0 as slack; verify directly on the applied successor)
    # cell 0 exports to 1 and 2; cell 3 feeds INTO cell 0
    cells = (band_cell(), band_cell(), band_cell(), band_cell())
    edges = (d0.Edge(0, 1, 1.0, 0.0, 0.9), d0.Edge(0, 2, 0.6, 0.0, 0.9),
             d0.Edge(3, 0, 0.5, 0.0, 0.9))
    w = d0.World(cells=cells, edges=edges)
    r = p1c.p1c_step(w, [19.0, 1.0, 1.0, 19.0], 0.5,
                     {0: reg(0, 18.0), 3: reg(3, 0.0)})
    s0 = next(s for s in r.sources if s.source_id == 0)
    check("deterministic: source 0 binds (sigma<1) with active incoming",
          s0.sigma < 1.0 and s0.incoming_usable > 0.0,
          f"sigma={s0.sigma:.4f}, I={s0.incoming_usable:.4f}")
    check("deterministic: successor x_0^{n+1} >= R_eff (direct evaluation)",
          r.x_after[0] >= s0.R_eff - 1e-12, f"x0'={r.x_after[0]:.6f} R={s0.R_eff}")
    # seeded random fixtures satisfying State-P assumptions
    rng = random.Random(P1C_SEED + 6)
    worst = 0.0
    n_elig = n_bind = n_active = n_fix = 0
    for _ in range(300):
        n = rng.randint(2, 6)
        cells = tuple(band_cell(R=rng.choice([0.0, rng.uniform(0, 6)]),
                                d=rng.choice([0.0, rng.uniform(0, 1.5)]))
                      for _ in range(n))
        pairs = [(i, j) for i in range(n) for j in range(n) if i != j]
        chosen = rng.sample(pairs, rng.randint(1, min(6, len(pairs))))
        edges = tuple(d0.Edge(i, j, round(rng.uniform(0.2, 2.0), 3), 0.0,
                              round(rng.uniform(0.5, 1.0), 3)) for i, j in chosen)
        w = d0.World(cells=cells, edges=edges)
        x = [round(rng.uniform(-2.0, 25.0), 3) for _ in range(n)]
        dt = rng.choice([0.1, 0.25, 0.5])
        exporters = {e.i for e in edges}
        cfgs = {k: reg(k, round(rng.uniform(0.0, 12.0), 3)) for k in exporters}
        try:
            r = p1c.p1c_step(w, x, dt, cfgs)
        except ValueError:
            continue
        n_fix += 1
        if any(e.q_acc > 0 for e in r.edges):
            n_active += 1
        for s in r.sources:
            if s.state == "P" and s.source_type in p1c.STOCK_TYPES:
                n_elig += 1
                if s.sigma < 1.0 and s.Q_req > 0:
                    n_bind += 1
                resid = s.R_eff - r.x_after[s.source_id]   # want <= 0
                worst = max(worst, resid)
    WORST["preservation"] = worst
    STATS["state_P"] += n_elig
    check(f"State-P successor >= R_eff on {n_elig} eligible sources "
          f"({n_bind} binding, {n_active}/{n_fix} active fixtures)",
          worst <= 1e-9, f"max (R_eff - x') = {worst:.3e}")
    check("theorem conformance is non-vacuous (binding + active present)",
          n_bind > 0 and n_active > 0, f"{n_bind} binding, {n_active} active")


# ===========================================================================
# [7] recovery and infeasibility honesty
# ===========================================================================
def test_group7():
    group("recovery (R) and infeasibility (I) honesty")
    # R: source below reserve, strong positive drive that WOULD lift it this tick
    wR = d0.World(cells=(band_cell(s=5.0), band_cell()),
                  edges=(d0.Edge(0, 1, 1.0, 0.0, 0.9),))
    rR = p1c.p1c_step(wR, [7.0, 1.0], 1.0, {0: reg(0, 8.0)})
    sR = rR.sources[0]
    check("R: source below reserve exports zero even though drive would lift it",
          sR.state == "R" and sR.Q_acc == 0.0
          and (7.0 + 1.0 * sR.u) > sR.R_eff,
          f"no-export successor={7.0 + sR.u:.2f} > R=8 but export=0")
    check("R: no preservation-success claim", sR.preservation_success_claimed is False)
    # I: above reserve but natural decline crosses it; zero export insufficient
    wI = d0.World(cells=(band_cell(d=2.0), band_cell()),
                  edges=(d0.Edge(0, 1, 1.0, 0.0, 0.9),))
    rI = p1c.p1c_step(wI, [10.0, 1.0], 1.0, {0: reg(0, 9.0)})
    sI = rI.sources[0]
    check("I: above reserve, natural decline breaches it, export forced zero",
          sI.state == "I" and sI.Q_acc == 0.0
          and rI.x_after[0] < sI.R_eff,
          f"x'={rI.x_after[0]:.3f} < R=9")
    check("I: reports zero export insufficient AND no success claim",
          sI.zero_export_insufficient is True
          and sI.preservation_success_claimed is False
          and sI.reserve_boundary_ok is False)
    check("I excluded from theorem claim",
          sI.source_id in rI.theorem_excluded_sources)


# ===========================================================================
# [8] efficiency and ledger
# ===========================================================================
def test_group8():
    group("efficiency and physical ledger")
    w = d0.World(cells=(band_cell(), band_cell()),
                 edges=(d0.Edge(0, 1, 0.8, 0.0, 0.7),))   # lossy eta=0.7
    r = p1c.p1c_step(w, [19.0, 2.0], 0.5, {0: reg(0, 5.0)})
    e = r.edges[0]
    check("source loses full q_acc; destination receives eta*q_acc",
          abs((r.x_before[0] - r.x_after[0]) - 0.5 * e.q_acc) < 1e-9
          and abs((r.x_after[1] - r.x_before[1]) - 0.5 * e.eta * e.q_acc) < 1e-9,
          f"q_acc={e.q_acc:.4f}")
    check("delivered == eta*q_acc and loss_rate == (1-eta)*q_acc",
          abs(e.q_delivered - e.eta * e.q_acc) < 1e-15
          and abs(e.loss_rate - (1 - e.eta) * e.q_acc) < 1e-15)
    check("total_loss == dt*(1-eta)*q_acc", abs(r.total_loss - 0.5 * 0.3 * e.q_acc) < 1e-12)
    # ledger closes: sum(dx) == dt(sum u - sum (1-eta)q_acc)
    rng = random.Random(P1C_SEED + 8)
    worst = 0.0
    for _ in range(150):
        n = rng.randint(2, 5)
        cells = tuple(band_cell(d=rng.choice([0.0, rng.uniform(0, 1)]),
                                s=rng.choice([0.0, rng.uniform(0, 1)]))
                      for _ in range(n))
        pairs = [(i, j) for i in range(n) for j in range(n) if i != j]
        chosen = rng.sample(pairs, rng.randint(1, min(6, len(pairs))))
        edges = tuple(d0.Edge(i, j, round(rng.uniform(0.3, 2.0), 3), 0.0,
                              round(rng.uniform(0.5, 1.0), 3)) for i, j in chosen)
        w = d0.World(cells=cells, edges=edges)
        x = [round(rng.uniform(0.0, 22.0), 3) for _ in range(n)]
        cfgs = {e.i: reg(e.i, round(rng.uniform(0.0, 10.0), 3)) for e in edges}
        r = p1c.p1c_step(w, x, 0.25, cfgs)
        scale = 1.0 + abs(r.stock_change)
        worst = max(worst, abs(r.ledger_residual) / scale)
    WORST["ledger"] = worst
    check("physical stock ledger closes over 150 random fixtures",
          worst < 1e-12, f"max scaled residual {worst:.2e}")
    # NEGATIVE CONTROL: using eta*q as the source withdrawal breaks the ledger
    w = d0.World(cells=(band_cell(), band_cell()),
                 edges=(d0.Edge(0, 1, 0.8, 0.0, 0.7),))
    r = p1c.p1c_step(w, [19.0, 2.0], 0.5, {0: reg(0, 5.0)})
    q = r.edges[0].q_acc
    # wrong update: source loses only eta*q (as if delivery == withdrawal)
    wrong_src = r.x_before[0] - 0.5 * 0.7 * q
    wrong_dx = (wrong_src - r.x_before[0]) + (r.x_after[1] - r.x_before[1])
    wrong_res = wrong_dx - (0.5 * (r.u[0] + r.u[1]) - r.total_loss)
    check("NEGATIVE CONTROL: 'source loses eta*q' fails the ledger",
          abs(wrong_res) > 1e-6, f"residual {wrong_res:.4f}")


# ===========================================================================
# [9] D0 compatibility when non-binding
# ===========================================================================
def test_group9():
    group("D0 compatibility when non-binding (compare vs frozen d0.d0_step)")
    rng = random.Random(P1C_SEED + 9)
    worst = 0.0
    n = n_active = 0
    for _ in range(200):
        m = rng.randint(2, 6)
        cells = tuple(band_cell(chi=rng.choice([0.0, rng.uniform(0.2, 1.0)]),
                                R=rng.uniform(0, 9),
                                d=rng.choice([0.0, rng.uniform(0, 1.5)]),
                                s=rng.choice([0.0, rng.uniform(0, 1.5)]))
                      for _ in range(m))
        pairs = [(i, j) for i in range(m) for j in range(m) if i != j]
        chosen = rng.sample(pairs, rng.randint(1, min(7, len(pairs))))
        edges = tuple(d0.Edge(i, j, round(rng.uniform(0.2, 2.0), 3),
                              round(rng.uniform(0.0, 0.1), 3),
                              round(rng.uniform(0.5, 1.0), 3)) for i, j in chosen)
        w = d0.World(cells=cells, edges=edges)
        x = [round(rng.uniform(0.0, 22.0), 3) for _ in range(m)]
        dt = rng.choice([0.1, 0.25, 0.5])
        # configure every exporter State P with R_eff so low the budget never binds
        cfgs = {e.i: reg(e.i, -1e6) for e in edges}
        rp = p1c.p1c_step(w, x, dt, cfgs)
        ref = d0.d0_step(w, x, dt, diagnostics=False)
        if any(e.q_acc > 0 for e in rp.edges):
            n_active += 1
        # confirm truly non-binding
        if all(s.sigma == 1.0 for s in rp.sources):
            dev = max(abs(a - b) for a, b in zip(rp.x_after, ref.x_after))
            worst = max(worst, dev)
            n += 1
    WORST["d0_conformance"] = worst
    check(f"non-binding P1C reproduces frozen D0 on {n} fixtures "
          f"({n_active} active) within strict tolerance",
          worst < 1e-12, f"max dev {worst:.2e}")
    check("D0-conformance suite is non-vacuous", n_active >= n // 2 and n > 0,
          f"{n_active}/{n} active")


# ===========================================================================
# [10] service accounting
# ===========================================================================
def test_group10():
    group("service accounting (delivered = eta*q_acc only)")
    # lossy + binding so that q_req != q_acc != q_delivered
    w = _fan_world(3, eta=0.6)
    r = p1c.p1c_step(w, [19.0, 1.0, 1.5, 2.0], 0.5, {0: reg(0, 18.0)})
    s = r.sources[0]
    e = r.edges[0]
    check("binding+lossy: q_req != q_acc != q_delivered on an edge",
          not (abs(e.q_req - e.q_acc) < 1e-9) and s.sigma < 1.0
          and not (abs(e.q_acc - e.q_delivered) < 1e-9),
          f"req={e.q_req:.4f} acc={e.q_acc:.4f} deliv={e.q_delivered:.4f}")
    total_deliv = math.fsum(e.q_delivered for e in r.edges)
    total_req = math.fsum(e.q_req for e in r.edges)
    total_acc = math.fsum(e.q_acc for e in r.edges)
    check("service = sum eta*q_acc; strictly below requested and below accepted",
          total_deliv < total_acc < total_req,
          f"deliv={total_deliv:.4f} acc={total_acc:.4f} req={total_req:.4f}")
    check("delivered equals eta*q_acc per edge (never raw/req/withdrawal)",
          all(abs(e.q_delivered - e.eta * e.q_acc) < 1e-15 for e in r.edges))
    # unmet demand accounting (fixture-side): demand d vs delivered
    demand = 5.0
    delivered_to_1 = r.edges[0].q_delivered
    unmet = max(0.0, demand - delivered_to_1)
    check("unmet demand = requested demand - delivered (fixture-side, honest)",
          abs(unmet - (demand - delivered_to_1)) < 1e-12 and unmet > 0.0)


# ===========================================================================
# [11] information boundary (AST + runtime poison)
# ===========================================================================
def test_group11():
    group("information boundary (AST + runtime poison)")
    tree = ast.parse(open("p1c_v29.py").read())
    imports = [a.name for node in ast.walk(tree) if isinstance(node, ast.Import)
               for a in node.names]
    imports += [node.module for node in ast.walk(tree)
                if isinstance(node, ast.ImportFrom) and node.module]
    check("p1c_v29 imports no test module",
          not any(m.startswith("test_") for m in imports), f"{imports}")
    # decision-path functions must not reference the global evaluator
    decision = {"classify_state", "robust_budget", "_source_budget"}
    offenders = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in decision:
            names = {n.attr for n in ast.walk(node) if isinstance(n, ast.Attribute)}
            names |= {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}
            if names & {"V_total", "lv_exact", "lv_safe"}:
                offenders.append(node.name)
    check("no allocator/classifier references the global evaluator (AST)",
          offenders == [], f"{offenders}")
    # p1c_step must not call itself (no future rollout / recursion)
    step_fn = next(node for node in ast.walk(tree)
                   if isinstance(node, ast.FunctionDef) and node.name == "p1c_step")
    self_calls = [c for c in ast.walk(step_fn) if isinstance(c, ast.Call)
                  and ((isinstance(c.func, ast.Name) and c.func.id == "p1c_step")
                       or (isinstance(c.func, ast.Attribute) and c.func.attr == "p1c_step"))]
    check("p1c_step performs no future rollout (does not call itself)",
          self_calls == [])
    # runtime poison: disable global evaluators; decisions must still work
    saved = (d0.V_total, d0.lv_exact, d0.lv_safe)

    def raiser(*a, **k):
        raise AssertionError("global evaluator called on the P1C decision path")
    try:
        d0.V_total = raiser
        d0.lv_exact = raiser
        d0.lv_safe = raiser
        w = _fan_world(3)
        r = p1c.p1c_step(w, [19.0, 1.0, 1.0, 1.0], 0.5, {0: reg(0, 18.0)})
        check("P1C tick completes with global V/L_V disabled (non-vacuous export)",
              any(e.q_acc > 0 for e in r.edges))
    finally:
        d0.V_total, d0.lv_exact, d0.lv_safe = saved
    # classifier/budget accept only local scalars, not world/state objects
    for bad in (d0.World(cells=(band_cell(),), edges=()), [1.0, 2.0]):
        try:
            p1c.classify_state(reg(0, 8.0), bad, 0.5, 1.0)
            ok = False
        except (TypeError, ValueError):
            ok = True
        check(f"classify_state rejects a non-scalar stock ({type(bad).__name__})", ok)


# ===========================================================================
# [12] negative controls (must fire)
# ===========================================================================
def test_group12():
    group("negative controls (deliberately wrong alternatives must fail)")
    w = _fan_world(4)
    x = [19.0, 1.0, 1.0, 1.0, 1.0]
    r = p1c.p1c_step(w, x, 0.5, {0: reg(0, 18.0)})
    s = r.sources[0]
    Qmax = s.Q_max
    # (1) every edge given the full budget -> aggregate overdraw below reserve
    over_export = sum(min(Qmax, e.q_req) for e in r.edges)  # each capped at Qmax
    x_over = 19.0 + 0.5 * (s.u - over_export)
    check("NC1: giving every edge the full budget overdraws below reserve",
          over_export > Qmax + 1e-9 and x_over < s.R_eff,
          f"sum={over_export:.3f} > Qmax={Qmax:.3f}, x'={x_over:.3f} < R=18")
    # (2) using eta*q as source withdrawal (tested in group 8 ledger); re-assert
    q = r.edges[0].q_acc
    check("NC2: 'source loses eta*q' understates withdrawal (source too high)",
          (19.0 - 0.5 * 0.9 * q) > (19.0 - 0.5 * q) + 1e-9)
    # (3) clamped-zero budget treated as feasibility -> State I breach
    wI = d0.World(cells=(band_cell(d=2.0),), edges=())
    rI = p1c.p1c_step(wI, [10.0], 1.0, {0: reg(0, 9.0)})
    check("NC3: clamped-zero budget is NOT feasibility (State I still breaches)",
          rI.sources[0].Q_max == 0.0 and rI.x_after[0] < rI.sources[0].R_eff
          and rI.sources[0].reserve_boundary_ok is False)
    # (4) sequential live-state allocation differs from simultaneous P1C
    # fan-out: apply edges one at a time against live source stock
    def sequential_export(x0, edges, u0, dt, Qmax):
        live = x0
        acc = []
        for e in edges:
            vi = d0.local_view(w.cells[e.i], live)
            vj = d0.local_view(w.cells[e.j], x[e.j])
            _f, J = d0.edge_flux(vi, vj, e)
            take = min(J, max(0.0, Qmax))   # naive per-edge cap against live
            acc.append(take)
            live = live - dt * take
        return acc
    seq = sequential_export(19.0, w.edges, s.u, 0.5, Qmax)
    sim = [e.q_acc for e in r.edges]
    check("NC4: sequential live-state allocation differs from simultaneous P1C",
          any(abs(a - b) > 1e-9 for a, b in zip(seq, sim)),
          f"seq sum={sum(seq):.3f} vs sim sum={sum(sim):.3f}")
    # (5) counting requested flow as delivered overcounts service
    total_req = math.fsum(e.q_req for e in r.edges)
    total_deliv = math.fsum(e.q_delivered for e in r.edges)
    check("NC5: counting requested flow as service overcounts vs delivered",
          total_req > total_deliv + 1e-9,
          f"req={total_req:.3f} > delivered={total_deliv:.3f}")


# ===========================================================================
if __name__ == "__main__":
    print("=" * 76)
    print("V2.9 Gate 2.2 - P1C preservation-controller conformance (NOT proof)")
    print("=" * 76)
    print(f"Python {sys.version.split()[0]}   regression seed = {P1C_SEED} "
          f"(distinct from 0-9 / 100-139 / 20260726 / 29001)")
    for fn in (test_group1, test_group2, test_group3, test_group4, test_group5,
               test_group6, test_group7, test_group8, test_group9, test_group10,
               test_group11, test_group12):
        fn()
    print("-" * 76)
    for k, (title, p, f) in enumerate(GROUPS, 1):
        print(f"group {k:>2}: {p:>3} passed, {f} failed - {title}")
    print(f"total checks: {PASS} passed, {FAIL} failed in {len(GROUPS)} groups")
    print(f"max preservation residual (R_eff - x'):  {WORST['preservation']:.3e} "
          f"(<= 0 expected for State-P; fp-tolerance positive acceptable)")
    print(f"max ledger residual (scaled):            {WORST['ledger']:.3e}")
    print(f"max permutation residual:                {WORST['permutation']:.3e}")
    print(f"max D0 non-binding conformance residual: {WORST['d0_conformance']:.3e}")
    print(f"max budget-formula residual:             {WORST['budget']:.3e}")
    print(f"max proportion residual:                 {WORST['proportion']:.3e}")
    print("NOT claimed: global stability, long-run sustainability, "
          "infinite-horizon reserve invariance, service under arbitrary demand,")
    print("D9/D10 success, ecological-debt/restoration-credit/scalar-EBU "
          "validity, adversarial security, or proof from passing tests.")
    if FAIL:
        print("P1C CONFORMANCE VALIDATION FAILED.")
        raise SystemExit(1)
    print("P1C conformance validation passed; this is not a proof and makes no "
          "behavioral or global-stability claim.")
