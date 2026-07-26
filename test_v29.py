"""
Conformance validation for d0_v29.py (V2.9 Gate 1).

Passing tests validate IMPLEMENTATION CONFORMANCE of the new synchronous local
D0 engine against the V2.8 note and the V2.9 preregistered protocol. They are
NOT proof of any theorem, and behavioral stability is NOT tested in this gate -
no V2.9 experiment, world study, or behavioral conclusion is produced here.

Oracle: the independent test-local D0 reference inside test_v28.py (imported as
a module; its __main__ suite does not execute on import). d0_v29.py itself never
imports any test module or released engine - group 9 enforces that by AST
inspection. Plain stdlib, direct execution:  python3 test_v29.py
"""
from __future__ import annotations
import ast
import math
import random
import sys

import d0_v29 as d0
import test_v28 as oracle          # independent V2.8 D0 reference + fixtures

V29_SEED = 29001    # validation-only seed range; distinct from behavioral
                    # exploratory seeds 0-9 and confirmatory seeds 100-139.

PASS = 0
FAIL = 0
GROUPS: list[list] = []
WORST = {"conformance": 0.0, "inequality": -math.inf, "ledger": 0.0,
         "permutation": 0.0}


def group(title: str) -> None:
    GROUPS.append([title, 0, 0])
    print(f"[{len(GROUPS)}] {title}")


def check(name: str, ok: bool, detail: str = "", fail_detail: str = "") -> None:
    global PASS, FAIL
    if ok:
        PASS += 1
        GROUPS[-1][1] += 1
        print(f"  PASS  {name}" + (f"  ({detail})" if detail else ""))
    else:
        FAIL += 1
        GROUPS[-1][2] += 1
        print(f"  FAIL  {name}" + (f"  ({detail})" if detail else ""))
        if fail_detail:
            print(f"        reproduce: {fail_detail}")


# ---------------------------------------------------------------------------
# fixture builders (v29 world <-> v28 oracle representation)
# ---------------------------------------------------------------------------
def band_cell(alpha=1.0, beta=0.5, chi=0.0, L=5.0, U=15.0, R=0.0, K=20.0, **drive):
    return d0.Cell(alpha=alpha, beta=beta, chi=chi, L=L, U=U, R=R, K=K, **drive)


def to_oracle(world: d0.World):
    cells = [oracle.Cell(c.alpha, c.beta, c.chi, c.L, c.U, c.R) for c in world.cells]
    edges = [oracle.Edge(e.i, e.j, e.M, e.theta, e.eta) for e in world.edges]
    return cells, edges


def drive_world(cells_params, edges, u_vec):
    """World whose natural drive is exactly the constant vector u, represented
    by the Amendment-2 decomposition u = u+ - u- (supply carries u+, demand
    carries u-); negative supply is never used."""
    cells = [d0.Cell(alpha=a, beta=b, chi=ch, L=L, U=U, R=R, K=K,
                     s=max(uv, 0.0), d=max(-uv, 0.0))
             for (a, b, ch, L, U, R, K), uv in zip(cells_params, u_vec)]
    return d0.World(cells=tuple(cells), edges=tuple(edges))


def random_conformance_fixtures(rng, count=8):
    """Seeded random worlds spanning eta in [0,1], negative/over-K states, chi>0."""
    fixtures = []
    for _ in range(count):
        n = rng.randint(3, 6)
        params = [(round(rng.uniform(0.3, 2.0), 3), round(rng.uniform(0.3, 2.0), 3),
                   rng.choice([0.0, round(rng.uniform(0.2, 1.0), 3)]),
                   5.0, 15.0, round(rng.uniform(0.0, 9.0), 3), 20.0)
                  for _ in range(n)]
        pairs = [(i, j) for i in range(n) for j in range(n) if i != j]
        chosen = rng.sample(pairs, rng.randint(3, min(8, len(pairs))))
        edges = [d0.Edge(i, j, round(rng.uniform(0.2, 2.0), 3),
                         round(rng.uniform(0.0, 0.1), 3),
                         round(rng.uniform(0.0, 1.0), 3)) for (i, j) in chosen]
        x = [round(rng.uniform(-5.0, 25.0), 3) for _ in range(n)]
        u = [round(rng.uniform(-1.5, 1.5), 3) for _ in range(n)]
        fixtures.append((params, edges, x, u))
    return fixtures


RNG = random.Random(V29_SEED)
FIXTURES = random_conformance_fixtures(RNG)
DTS = (0.05, 0.3, 1.0)


def fixture_repr(params, edges, x, u, dt):
    es = [(e.i, e.j, e.M, e.theta, e.eta) for e in edges]
    return f"seed={V29_SEED} params={params} edges={es} x={x} u={u} dt={dt}"


# ===========================================================================
# [1] penalty and marginal
# ===========================================================================
def test_group1():
    group("penalty + marginal + corrected curvature")
    configs = [
        ("deficit+reserve overlap", dict(alpha=1.0, beta=0.5, chi=0.7, L=5.0, U=15.0, R=8.0), 3.4),
        ("excess+reserve overlap", dict(alpha=0.6, beta=0.8, chi=0.9, L=2.0, U=4.0, R=9.0), 3.4),
        ("flat band, no reserve", dict(alpha=1.0, beta=1.0, chi=0.0, L=5.0, U=15.0, R=0.0), 2.0),
        ("R below L", dict(alpha=0.5, beta=2.0, chi=0.4, L=6.0, U=10.0, R=3.0), 4.0),
    ]
    h = 1e-5
    for name, p, lv_expect in configs:
        c = d0.Cell(K=20.0, **p)
        bps = sorted({c.L, c.U, c.R})
        reps = [bps[0] - 2.0] + [(a + b) / 2 for a, b in zip(bps, bps[1:]) if b > a] \
               + [bps[-1] + 2.0]
        worst = max(abs(d0.marginal(c.alpha, c.beta, c.chi, c.L, c.U, c.R, q)
                        - (d0.penalty(c.alpha, c.beta, c.chi, c.L, c.U, c.R, q + h)
                           - d0.penalty(c.alpha, c.beta, c.chi, c.L, c.U, c.R, q - h))
                        / (2 * h)) for q in reps)
        check(f"{name}: marginal == central FD of penalty on every branch",
              worst < 1e-7, f"max err {worst:.2e}")
        got = d0.cell_curvature_sup(c)
        check(f"{name}: exact curvature sup == {lv_expect}",
              abs(got - lv_expect) < 1e-12, f"got {got}")
        w = d0.World(cells=(c,), edges=())
        check(f"{name}: safe L_V bound >= exact", d0.lv_safe(w) >= d0.lv_exact(w) - 1e-12,
              f"{d0.lv_safe(w)} >= {d0.lv_exact(w)}")
        oc = oracle.Cell(c.alpha, c.beta, c.chi, c.L, c.U, c.R)
        worst_x = max(abs(d0.penalty(c.alpha, c.beta, c.chi, c.L, c.U, c.R, q)
                          - oracle.v_cell(oc, q)) +
                      abs(d0.marginal(c.alpha, c.beta, c.chi, c.L, c.U, c.R, q)
                          - oracle.mu_cell(oc, q)) for q in reps)
        check(f"{name}: penalty+marginal agree with the independent V2.8 reference",
              worst_x < 1e-12, f"max diff {worst_x:.2e}")


# ===========================================================================
# [2] local force and flux
# ===========================================================================
def test_group2():
    group("local force f = mu_i - eta mu_j and flux J = M[f - theta]_+")
    c = band_cell()
    w = d0.World(cells=(c, c), edges=(d0.Edge(0, 1, 1.0, 0.0, 1.0),))
    vi, vj = d0.local_view(c, 19.0), d0.local_view(c, 2.0)   # mu = 4, -6
    f, J = d0.edge_flux(vi, vj, d0.Edge(0, 1, 1.0, 0.0, 1.0))
    check("lossless edge: f == mu_i - mu_j == 10, J == 10",
          abs(f - 10.0) < 1e-12 and abs(J - 10.0) < 1e-12, f"f={f}, J={J}")
    f, J = d0.edge_flux(vi, vj, d0.Edge(0, 1, 0.7, 0.05, 0.8))
    check("lossy edge: f == 4 - 0.8(-6) == 8.8, J == 0.7*8.75",
          abs(f - 8.8) < 1e-12 and abs(J - 0.7 * 8.75) < 1e-12, f"f={f}, J={J}")
    vi2, vj2 = d0.local_view(c, 7.0), d0.local_view(c, 8.0)   # both in band
    f, J = d0.edge_flux(vi2, vj2, d0.Edge(0, 1, 1.0, 0.5, 0.9))
    check("inactive threshold: f <= theta gives J == 0", f == 0.0 and J == 0.0)
    f, J = d0.edge_flux(vi, vj, d0.Edge(0, 1, 1.0, 0.0, 0.0))
    check("zero destination efficiency: f == mu_i exactly, J == M[mu_i]_+",
          abs(f - 4.0) < 1e-12 and abs(J - 4.0) < 1e-12, f"f={f}, J={J}")
    # V2.8 Counterexample D, realized through actual penalties
    cd = band_cell(alpha=1.0, beta=0.5, L=10.0, U=15.0)
    vi3, vj3 = d0.local_view(cd, 8.5), d0.local_view(cd, 8.0)  # mu = -3, -4
    f, J = d0.edge_flux(vi3, vj3, d0.Edge(0, 1, 1.0, 0.0, 0.5))
    check("CE-D: loss-aware f == -1 < 0, production flux stays zero",
          abs(f + 1.0) < 1e-12 and J == 0.0)
    mu_i = d0.marginal(cd.alpha, cd.beta, cd.chi, cd.L, cd.U, cd.R, 8.5)
    mu_j = d0.marginal(cd.alpha, cd.beta, cd.chi, cd.L, cd.U, cd.R, 8.0)
    g_blind = mu_i - mu_j
    check("CE-D: the loss-blind force (test-side only) WOULD transfer (g == 1 > 0)",
          abs(g_blind - 1.0) < 1e-12,
          "harmful negative-control action confirmed; rule absent from d0_v29")


# ===========================================================================
# [3] independent cross-conformance with the V2.8 reference
# ===========================================================================
def test_group3():
    group("cross-conformance vs test_v28 D0 reference (independent oracle)")
    # deterministic fixtures from the V2.8 suite
    det = [
        ([(1.0, 0.5, 0.0, 5.0, 15.0, 0.0, 20.0)] * 2,
         [d0.Edge(0, 1, 0.8, 0.05, 0.9)], [19.0, 2.0], [0.0, 0.0]),
        ([(1.0, 0.5, 0.0, 5.0, 15.0, 0.0, 20.0)] * 2,
         [d0.Edge(0, 1, 0.8, 0.05, 0.9)], [19.0, 2.0], [1.2, -0.7]),
        ([(1.0, 0.5, 0.7, 5.0, 15.0, 8.0, 20.0)] * 2,
         [d0.Edge(0, 1, 0.6, 0.0, 0.8)], [3.0, 1.0], [0.4, 0.0]),
        ([(1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 20.0)] * 2,          # CE-E overlap
         [d0.Edge(0, 1, 1.0, 0.0, 1.0)], [-1.0, -2.0], [0.0, 0.0]),
    ]
    n_active = 0
    worst = 0.0
    worst_fix = ""
    all_fixtures = det + FIXTURES
    n_checked = 0
    for params, edges, x, u in all_fixtures:
        world = drive_world(params, edges, u)
        ocells = [oracle.Cell(a, b, ch, L, U, R)
                  for (a, b, ch, L, U, R, K) in params]
        oedges = [oracle.Edge(e.i, e.j, e.M, e.theta, e.eta) for e in edges]
        for dt in DTS:
            res = d0.d0_step(world, x, dt)
            oxn, om, of, oJ, osj = oracle.d0_step(ocells, oedges, list(x), list(u), dt)
            if any(j > 0 for j in oJ):
                n_active += 1
            diff = max(
                max(abs(a - b) for a, b in zip(res.mu, om)),
                max(abs(a - b) for a, b in zip(res.f, of)),
                max(abs(a - b) for a, b in zip(res.J, oJ)),
                max(abs(a - b) for a, b in zip(res.sj, osj)),
                max(abs(a - b) for a, b in zip(res.x_after, oxn)),
                max(abs(a - b) for a, b in zip(res.u, u)))
            n_checked += 1
            if diff > worst:
                worst, worst_fix = diff, fixture_repr(params, edges, x, u, dt)
    WORST["conformance"] = worst
    check(f"mu/f/J/SJ/u/x' agree with the oracle on {n_checked} fixture-dt cases",
          worst < 1e-9, f"max |diff| = {worst:.2e}", worst_fix)
    check("active-edge coverage is non-vacuous (>= half of cases active)",
          n_active >= n_checked // 2, f"{n_active}/{n_checked} active")
    hashes = {hash((tuple(map(tuple, p)), tuple((e.i, e.j, e.M, e.theta, e.eta)
              for e in ed), tuple(x), tuple(u))) for p, ed, x, u in FIXTURES}
    check("random fixtures genuinely differ (layout-hash diversity)",
          len(hashes) == len(FIXTURES), f"{len(hashes)} distinct / {len(FIXTURES)}")
    print(f"        seed={V29_SEED}, fixtures={len(all_fixtures)} (4 deterministic "
          f"+ {len(FIXTURES)} random), dts={DTS}, ranges: alpha,beta in [0.3,2], "
          f"chi in {{0}}u[0.2,1], eta in [0,1], M in [0.2,2], theta in [0,0.1], "
          f"x in [-5,25], u in [-1.5,1.5]")


# ===========================================================================
# [4] exact synchronous update
# ===========================================================================
def test_group4():
    group("exact synchronous frozen-state update")
    params, edges, x, u = FIXTURES[0]
    world = drive_world(params, edges, u)
    res = d0.d0_step(world, x, 0.3)
    # (a) fluxes use the frozen state: recompute every flux from x directly
    worst = 0.0
    for e, fe, Je in zip(world.edges, res.f, res.J):
        vi = d0.local_view(world.cells[e.i], x[e.i])
        vj = d0.local_view(world.cells[e.j], x[e.j])
        f2, J2 = d0.edge_flux(vi, vj, e)
        worst = max(worst, abs(fe - f2), abs(Je - J2))
    check("every flux equals its frozen-state recomputation (bitwise)", worst == 0.0)
    # (b) accumulation matches direct matrix/column calculation
    n = world.n
    sj_direct = [0.0] * n
    for e, Je in zip(world.edges, res.J):
        col = [0.0] * n
        col[e.i] += -1.0
        col[e.j] += e.eta
        for k in range(n):
            sj_direct[k] += col[k] * Je
    worst = max(abs(a - b) for a, b in zip(res.sj, sj_direct))
    check("S J accumulation matches explicit incidence-column calculation",
          worst < 1e-12, f"max diff {worst:.2e}")
    # (c) edge-order permutation invariance within strict tolerance (observed
    # bit-identical here via fsum; cross-platform bit identity is NOT claimed)
    rng = random.Random(V29_SEED + 1)
    tol = 1e-12 * (1.0 + max(abs(v) for v in res.x_after))
    for trial in range(3):
        perm = list(edges)
        rng.shuffle(perm)
        wp = drive_world(params, perm, u)
        rp = d0.d0_step(wp, x, 0.3)
        dev = max(abs(a - b) for a, b in zip(rp.x_after, res.x_after))
        check(f"edge-order shuffle {trial}: permutation-invariant within tolerance",
              dev <= tol, f"observed residual {dev:.1e}")
    # (d) distance-2 cell untouched after one tick (no sequential leakage)
    cq = d0.Cell(alpha=1.0, beta=1.0, chi=0.0, L=10.0, U=10.0, R=0.0, K=20.0)
    chain = d0.World(cells=(cq, cq, cq),
                     edges=(d0.Edge(0, 1, 0.2, 0.0, 0.9), d0.Edge(1, 0, 0.2, 0.0, 0.9),
                            d0.Edge(1, 2, 0.2, 0.0, 0.9), d0.Edge(2, 1, 0.2, 0.0, 0.9)))
    b = d0.d0_step(chain, [12.0, 10.5, 10.2], 0.5)
    p = d0.d0_step(chain, [12.5, 10.5, 10.2], 0.5)
    check("distance-2 cell bit-identical after one synchronous tick",
          b.x_after[2] == p.x_after[2], f"x2 = {b.x_after[2]!r}")
    check("chain fixture genuinely active on both hops",
          b.J[0] > 0 and b.J[2] > 0, f"J={[round(j, 4) for j in b.J]}")


# ===========================================================================
# [5] theorem inequality (independent evaluation, never engine rearrangement)
# ===========================================================================
def test_group5():
    group("V2.8 one-step inequality, evaluated independently")
    worst = -math.inf
    worst_fix = ""
    n_cases = n_active = 0
    for params, edges, x, u in FIXTURES:
        world = drive_world(params, edges, u)
        ocells = [oracle.Cell(a, b, ch, L, U, R) for (a, b, ch, L, U, R, K) in params]
        oedges = [oracle.Edge(e.i, e.j, e.M, e.theta, e.eta) for e in edges]
        lv = oracle.LV_exact(ocells)                      # oracle-side constant
        for dt in DTS:
            res = d0.d0_step(world, x, dt, diagnostics=False)  # decision only
            # ALL inequality terms recomputed on the oracle side:
            om, of, oJ = oracle.forces_flux(ocells, oedges, list(x))
            osj = oracle.transport(oedges, oJ, len(x))
            lhs = oracle.V_total(ocells, res.x_after) - oracle.V_total(ocells, list(x))
            drive = dt * sum(m * uu for m, uu in zip(om, u))
            diss = dt * oracle.dissipation(oedges, oJ)
            rn = 0.5 * lv * dt * dt * sum((uu + ss) ** 2 for uu, ss in zip(u, osj))
            resid = lhs - (drive - diss + rn)
            n_cases += 1
            if any(j > 0 for j in oJ):
                n_active += 1
            if resid > worst:
                worst, worst_fix = resid, fixture_repr(params, edges, x, u, dt)
    WORST["inequality"] = worst
    check(f"inequality residual <= 0 on all {n_cases} cases (any dt; Thm 4.4)",
          worst <= 1e-9, f"max residual {worst:.3e}", worst_fix)
    check("inequality coverage non-vacuous", n_active >= n_cases // 2,
          f"{n_active}/{n_cases} active")
    # undriven descent below and AT the certified bounds
    for k, (params, edges, x, _u) in enumerate(FIXTURES[:4]):
        world = drive_world(params, edges, [0.0] * len(x))
        cert = d0.gershgorin_dt_certificate(world)
        for frac, label in ((0.5, "below"), (1.0, "at")):
            res = d0.d0_step(world, x, frac * cert)
            dV = (oracle.V_total(*_as_oracle_state(params, res.x_after))
                  - oracle.V_total(*_as_oracle_state(params, x)))
            check(f"fixture {k}: V non-increasing {label} certified dt "
                  f"(dt={frac * cert:.4f})", dV <= 1e-9 * (1 + abs(dV)),
                  f"dV={dV:.2e}", fixture_repr(params, edges, x, [0] * len(x), frac * cert))
    # one-edge certificate matches Theorem 5.1 form
    e = d0.Edge(0, 1, 0.8, 0.0, 0.9)
    check("one-edge certificate == 2/(L_V M (1+eta^2))",
          abs(d0.one_edge_dt_certificate(e, 2.0) - 2.0 / (2.0 * 0.8 * 1.81)) < 1e-15)


def _as_oracle_state(params, x):
    return [oracle.Cell(a, b, ch, L, U, R) for (a, b, ch, L, U, R, K) in params], list(x)


# ===========================================================================
# [6] negative controls (must fire when deliberately invoked)
# ===========================================================================
def test_group6():
    group("negative controls (deliberately invoked; must fire)")
    # (a) oversized timestep on the CE-A pure-quadratic fixture
    q = d0.Cell(alpha=1.0, beta=1.0, chi=0.0, L=0.0, U=0.0, R=0.0, K=20.0)
    wa = d0.World(cells=(q, q), edges=(d0.Edge(0, 1, 1.0, 0.0, 1.0),))
    x0 = [1.0, -1.0]
    dt_star = 0.5
    lo = d0.d0_step(wa, x0, 0.999 * dt_star)
    hi = d0.d0_step(wa, x0, 1.001 * dt_star)
    check("CE-A: below exact threshold V decreases",
          lo.V_after < lo.V_before - 1e-9, f"{lo.V_before} -> {lo.V_after:.6f}")
    check("NEGATIVE CONTROL fires: above threshold V increases",
          hi.V_after > hi.V_before + 1e-9, f"{hi.V_before} -> {hi.V_after:.6f}")
    # (b) the old max-form curvature constant would permit a V-increasing step
    ce = d0.Cell(alpha=1.0, beta=1.0, chi=1.0, L=0.0, U=0.0, R=0.0, K=20.0)
    we = d0.World(cells=(ce, ce), edges=(d0.Edge(0, 1, 1.0, 0.0, 1.0),))
    res = d0.d0_step(we, [-1.0, -2.0], 0.4)
    old_L = 2.0 * max(ce.alpha, ce.beta, ce.chi)
    old_bound = 2.0 / (old_L * 1.0 * 2.0)
    check("NEGATIVE CONTROL fires: old constant permits dt=0.4 yet V: 10 -> 13.84",
          0.4 <= old_bound and abs(res.V_before - 10.0) < 1e-9
          and abs(res.V_after - 13.84) < 1e-9)
    check("corrected engine curvature == 4 (sums overlapping weights)",
          abs(d0.lv_exact(we) - 4.0) < 1e-12, f"lv={d0.lv_exact(we)}")
    # (c) loss-blind force under eta < 1 increases V (test-side execution)
    cd = band_cell(alpha=1.0, beta=0.5, L=10.0, U=15.0)
    wd = d0.World(cells=(cd, cd), edges=(d0.Edge(0, 1, 1.0, 0.0, 0.5),))
    xd = [8.5, 8.0]
    res = d0.d0_step(wd, xd, 0.01)
    check("production D0 makes no transfer on CE-D (J == 0, V unchanged)",
          res.J[0] == 0.0 and res.x_after == tuple(xd))
    q_blind = 1.0                                    # M * (mu_i - mu_j) = 1
    xb = [xd[0] - 0.01 * q_blind, xd[1] + 0.5 * 0.01 * q_blind]
    Vb = d0.V_total(wd, xd)
    Va = d0.V_total(wd, xb)
    check("NEGATIVE CONTROL fires: loss-blind transfer increases V",
          Va > Vb + 1e-9, f"dV=+{Va - Vb:.6f}")
    # (d) sequential live-state application leaks to distance 2 (test-side only)
    cq = d0.Cell(alpha=1.0, beta=1.0, chi=0.0, L=10.0, U=10.0, R=0.0, K=20.0)
    cells = (cq, cq, cq)

    def sequential_tick(x, dt):   # NEGATIVE-CONTROL FIXTURE, not a released engine
        y = list(x)
        for e in (d0.Edge(0, 1, 0.2, 0.0, 0.9), d0.Edge(1, 2, 0.2, 0.0, 0.9)):
            _f, J = d0.edge_flux(d0.local_view(cells[e.i], y[e.i]),
                                 d0.local_view(cells[e.j], y[e.j]), e)
            y[e.i] -= dt * J
            y[e.j] += dt * e.eta * J
        return y

    sb = sequential_tick([12.0, 10.5, 10.2], 0.5)
    sp = sequential_tick([12.5, 10.5, 10.2], 0.5)
    check("NEGATIVE CONTROL fires: sequential live-state tick leaks to distance 2",
          abs(sp[2] - sb[2]) > 1e-9, f"leak={abs(sp[2] - sb[2]):.6f}")


# ===========================================================================
# [7] stock/loss ledger
# ===========================================================================
def _ledger(tag, world, x, dt, s_extra=None):
    res = d0.d0_step(world, x, dt, s_extra=s_extra)
    # independent recomputation (not the engine's ledger_residual field)
    lhs = math.fsum(res.x_after) - math.fsum(res.x_before)
    u2 = [d0.natural_drive(c, xi, (s_extra[k] if s_extra else 0.0))
          for k, (c, xi) in enumerate(zip(world.cells, x))]
    loss2 = dt * math.fsum((1 - e.eta) * J for e, J in zip(world.edges, res.J))
    rhs = dt * math.fsum(u2) - loss2
    scale = 1.0 + abs(lhs) + abs(rhs)
    WORST["ledger"] = max(WORST["ledger"], abs(lhs - rhs))
    check(f"{tag}: sum(dx) == dt[sum u - sum (1-eta)J] (independent recompute)",
          abs(lhs - rhs) < 1e-12 * scale, f"lhs={lhs:.12f} rhs={rhs:.12f}")
    check(f"{tag}: engine ledger_residual agrees",
          abs(res.ledger_residual) < 1e-12 * scale, f"{res.ledger_residual:.2e}")
    return res


def test_group7():
    group("stock/loss ledger (Theorem 8.1)")
    c = band_cell()
    w = d0.World(cells=(c, c), edges=(d0.Edge(0, 1, 0.8, 0.0, 1.0),))
    res = _ledger("lossless transport", w, [19.0, 2.0], 0.3)
    check("lossless: transport loss exactly 0 and J > 0",
          res.transport_loss == 0.0 and res.J[0] > 0)
    w = d0.World(cells=(c, c), edges=(d0.Edge(0, 1, 0.8, 0.05, 0.7),))
    res = _ledger("lossy transport", w, [19.0, 2.0], 0.3)
    check("lossy: accounted loss > 0", res.transport_loss > 0.0)
    # multi-edge + full drive: supply, demand, leaks, logistic + Allee regen
    cells = (band_cell(s=1.2, d=0.2, lam=0.1, kappa=0.02),
             d0.Cell(alpha=1.0, beta=0.5, chi=0.7, L=5.0, U=15.0, R=8.0, K=20.0,
                     source="logistic", rho=0.6),
             d0.Cell(alpha=1.0, beta=0.5, chi=0.7, L=5.0, U=15.0, R=8.0, K=20.0,
                     source="allee", rho=0.6, A=5.0),
             band_cell(d=0.8))
    edges = (d0.Edge(0, 1, 0.5, 0.05, 0.9), d0.Edge(1, 2, 1.0, 0.0, 1.0),
             d0.Edge(2, 3, 0.8, 0.1, 0.6), d0.Edge(3, 0, 0.4, 0.05, 0.9))
    w = d0.World(cells=cells, edges=edges)
    _ledger("drive + regeneration + demand + leak", w, [19.0, 10.0, 3.0, 2.0], 0.25)
    # seeded random fixtures
    for k, (params, edges2, x, u) in enumerate(FIXTURES[:4]):
        _ledger(f"random fixture {k}", drive_world(params, edges2, u), x, 0.3)


# ===========================================================================
# [8] P1K bounded-wrapper accounting
# ===========================================================================
def test_group8():
    group("P1K bounded wrapper (outside the V2.8 theorem; clipping never silent)")
    # heavy demand drives raw proposal negative
    c_low = band_cell(d=8.0)
    w = d0.World(cells=(c_low, band_cell()), edges=(d0.Edge(0, 1, 0.5, 0.05, 0.9),))
    r = d0.p1k_step(w, [0.5, 10.0], 1.0)
    check("floor case: raw proposal went negative, wrapper stayed in [0, K]",
          r.raw.x_after[0] < 0.0 and all(0.0 <= v <= 20.0 for v in r.x_after))
    check("floor case: shortfall exact and identity x' == y + shortfall - spill",
          all(r.x_after[k] == r.raw.x_after[k] + r.shortfall[k] - r.spill[k]
              for k in range(2)) and r.shortfall[0] > 0.0)
    check("floor case: P1K ledger closes", abs(r.ledger_residual) < 1e-12,
          f"{r.ledger_residual:.2e}")
    # heavy supply drives raw proposal above K
    c_hi = band_cell(s=8.0)
    w = d0.World(cells=(c_hi, band_cell()), edges=())
    r = d0.p1k_step(w, [19.0, 10.0], 1.0)
    check("ceiling case: spill exact, output at K",
          r.spill[0] > 0.0 and r.x_after[0] == 20.0 and abs(r.ledger_residual) < 1e-12)
    check("clipping never silent: components reported per cell",
          len(r.shortfall) == 2 and len(r.spill) == 2 and r.raw.x_after[0] > 20.0)
    # feasible case: P1K == P1 bitwise, zero shortfall/spill
    w = d0.World(cells=(band_cell(), band_cell()),
                 edges=(d0.Edge(0, 1, 0.5, 0.05, 0.9),))
    r = d0.p1k_step(w, [14.0, 6.0], 0.2)
    check("feasible case: P1K output bit-identical to exact P1",
          r.x_after == r.raw.x_after
          and all(v == 0.0 for v in r.shortfall) and all(v == 0.0 for v in r.spill))
    check("labels: P1K marked outside the theorem, raw P1 marked covered",
          r.covered_by_v28_theorem is False and r.model == "P1K-bounded-wrapper"
          and r.raw.covered_by_v28_theorem is True and r.raw.model == "P1-exact-D0")
    # the suite itself never applies the V2.8 descent claim to P1K: assert the
    # wrapper result carries no inequality field at all
    check("no descent claim attached to P1K results",
          not hasattr(r, "inequality_residual"))


# ===========================================================================
# [9] information boundary
# ===========================================================================
def test_group9():
    group("information boundary of the local decision function")
    c = band_cell()
    w = d0.World(cells=(c, c), edges=(d0.Edge(0, 1, 1.0, 0.0, 0.9),))
    v1, v2 = d0.local_view(c, 19.0), d0.local_view(c, 2.0)
    e = d0.Edge(0, 1, 1.0, 0.0, 0.9)
    for bad in (w, [19.0, 2.0], (v1, v2)):
        try:
            d0.edge_flux(bad, v2, e)
            ok = False
        except TypeError:
            ok = True
        check(f"decision function rejects non-LocalView source ({type(bad).__name__})", ok)
    try:
        d0.edge_flux(v1, v2, "not-an-edge")
        ok = False
    except TypeError:
        ok = True
    check("decision function rejects a non-Edge specification", ok)
    # AST inspection of the production module
    tree = ast.parse(open("d0_v29.py").read())
    imports = [a.name for node in ast.walk(tree) if isinstance(node, ast.Import)
               for a in node.names]
    imports += [node.module for node in ast.walk(tree)
                if isinstance(node, ast.ImportFrom) and node.module]
    banned = [m for m in imports
              if m.startswith(("energy_balance", "ebu_v2", "test_"))]
    check("d0_v29 imports no released engine and no test module",
          banned == [], f"imports={imports}")
    decision_funcs = {"edge_flux", "natural_drive", "local_view",
                      "_view_marginal", "_view_penalty", "_regen"}
    offenders = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in decision_funcs:
            names = {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}
            if "V_total" in names or "lv_exact" in names:
                offenders.append(node.name)
    check("no decision-path function references the global evaluator (AST)",
          offenders == [], f"offenders={offenders}")
    # runtime guard: replace the global evaluator with a raiser
    saved = d0.V_total
    try:
        def _raiser(*a, **k):
            raise AssertionError("global V called on the decision path")
        d0.V_total = _raiser
        f, J = d0.edge_flux(v1, v2, e)
        res = d0.d0_step(w, [19.0, 2.0], 0.2, diagnostics=False)
        check("decision + flux + non-diagnostic step work with global V disabled",
              J > 0 and res.x_after is not None)
    finally:
        d0.V_total = saved
    # translation invariance: identical local data in different worlds
    other = d0.World(cells=(band_cell(), c, c, band_cell(alpha=2.0)),
                     edges=(d0.Edge(1, 2, 1.0, 0.0, 0.9),))
    f1, J1 = d0.edge_flux(d0.local_view(c, 19.0), d0.local_view(c, 2.0), e)
    f2, J2 = d0.edge_flux(d0.local_view(other.cells[1], 19.0),
                          d0.local_view(other.cells[2], 2.0),
                          d0.Edge(1, 2, 1.0, 0.0, 0.9))
    check("identical local neighbourhood data gives identical decisions",
          f1 == f2 and J1 == J2)
    # non-neighbour independence inside a full step
    c3 = band_cell()
    w3a = d0.World(cells=(c3, c3, c3), edges=(d0.Edge(0, 1, 1.0, 0.0, 0.9),))
    ra = d0.d0_step(w3a, [19.0, 2.0, 10.0], 0.2)
    rb = d0.d0_step(w3a, [19.0, 2.0, 3.14], 0.2)
    check("changing a non-neighbouring cell leaves the edge decision unchanged",
          ra.f == rb.f and ra.J == rb.J)


# ===========================================================================
# [10] determinism and validation
# ===========================================================================
def test_group10():
    group("determinism + input validation")
    params, edges, x, u = FIXTURES[1]
    world = drive_world(params, edges, u)
    r1 = d0.d0_step(world, x, 0.3)
    r2 = d0.d0_step(world, x, 0.3)
    check("same input twice gives bit-identical output", r1.x_after == r2.x_after)
    bad_cases = [
        ("NaN state", lambda: d0.d0_step(world, [math.nan] + list(x[1:]), 0.3)),
        ("infinite state", lambda: d0.d0_step(world, [math.inf] + list(x[1:]), 0.3)),
        ("dt == 0", lambda: d0.d0_step(world, x, 0.0)),
        ("dt < 0", lambda: d0.d0_step(world, x, -0.1)),
        ("state length mismatch", lambda: d0.d0_step(world, list(x) + [1.0], 0.3)),
        ("NaN alpha", lambda: d0.Cell(alpha=math.nan, beta=1, chi=0, L=5, U=15, R=0, K=20)),
        ("negative alpha", lambda: d0.Cell(alpha=-1, beta=1, chi=0, L=5, U=15, R=0, K=20)),
        ("L > U", lambda: d0.Cell(alpha=1, beta=1, chi=0, L=16, U=15, R=0, K=20)),
        ("K <= 0", lambda: d0.Cell(alpha=1, beta=1, chi=0, L=5, U=15, R=0, K=0.0)),
        ("M <= 0", lambda: d0.Edge(0, 1, 0.0, 0.0, 0.9)),
        ("eta > 1", lambda: d0.Edge(0, 1, 1.0, 0.0, 1.5)),
        ("eta < 0", lambda: d0.Edge(0, 1, 1.0, 0.0, -0.1)),
        ("theta < 0", lambda: d0.Edge(0, 1, 1.0, -0.05, 0.9)),
        ("self edge", lambda: d0.Edge(1, 1, 1.0, 0.0, 0.9)),
        ("bad edge index", lambda: d0.World(cells=(band_cell(),),
                                            edges=(d0.Edge(0, 1, 1.0, 0.0, 0.9),))),
        ("empty world", lambda: d0.World(cells=(), edges=())),
        ("bad source kind", lambda: d0.Cell(alpha=1, beta=1, chi=0, L=5, U=15,
                                            R=0, K=20, source="magic")),
        ("allee without A", lambda: d0.Cell(alpha=1, beta=1, chi=0, L=5, U=15,
                                            R=0, K=20, source="allee", rho=0.5)),
    ]
    for name, fn in bad_cases:
        try:
            fn()
            ok = False
        except (ValueError, TypeError):
            ok = True
        check(f"rejects {name}", ok)
    # zero-flux and empty-edge worlds
    c = band_cell()
    w0 = d0.World(cells=(c, c), edges=(d0.Edge(0, 1, 1.0, 0.5, 0.9),))
    r = d0.d0_step(w0, [10.0, 11.0], 0.5)
    check("zero-flux world: J == 0 and state exactly unchanged (u = 0)",
          all(j == 0.0 for j in r.J) and r.x_after == (10.0, 11.0))
    wn = d0.World(cells=(c,), edges=())
    r = d0.d0_step(wn, [10.0], 0.5)
    check("empty-edge world steps cleanly", r.x_after == (10.0,))
    try:
        d0.gershgorin_dt_certificate(wn)
        ok = False
    except ValueError:
        ok = True
    check("certificate on an edgeless world is a defined error", ok)


# ===========================================================================
# [11] local regenerative drive laws
# ===========================================================================
def test_group11():
    group("natural drive laws (finite / logistic / Allee / external)")
    fin = band_cell(s=1.5, d=0.5, lam=0.2, kappa=0.05, source="finite")
    for xq in (0.0, 5.0, 20.0):
        expect = 1.5 - 0.5 - 0.2 - 0.05 * xq
        check(f"finite source at x={xq}: u == s-d-lam-kappa*x",
              abs(d0.natural_drive(fin, xq) - expect) < 1e-12)
    logi = d0.Cell(alpha=1, beta=0.5, chi=0, L=5, U=15, R=0, K=20.0,
                   source="logistic", rho=0.6)
    check("logistic: g(0) == 0", d0.natural_drive(logi, 0.0) == 0.0)
    check("logistic: g(K) == 0", abs(d0.natural_drive(logi, 20.0)) < 1e-12)
    check("logistic: g(K/2) == rho*K/4 (maximum sustainable isolated yield)",
          abs(d0.natural_drive(logi, 10.0) - 0.6 * 20.0 / 4.0) < 1e-12)
    alle = d0.Cell(alpha=1, beta=0.5, chi=0, L=5, U=15, R=0, K=20.0,
                   source="allee", rho=0.6, A=5.0)
    check("Allee: g(0) == 0 and g(A) == 0 and g(K) == 0",
          d0.natural_drive(alle, 0.0) == 0.0
          and abs(d0.natural_drive(alle, 5.0)) < 1e-12
          and abs(d0.natural_drive(alle, 20.0)) < 1e-12)
    check("Allee: negative below threshold, positive above",
          d0.natural_drive(alle, 3.0) < 0.0 and d0.natural_drive(alle, 8.0) > 0.0)
    # cross-check the regeneration formula against the RELEASED physics
    import energy_balance as eb
    g = eb.Grid(n=1, x=[10.0], K=[20.0], L=[5.0], U=[15.0], alpha=[1.0], beta=[0.5],
                s=[0.0], d=[0.0], lam=[0.0], rho=[0.6], x_min=[0.0], A=[5.0])
    worst = max(abs(d0.natural_drive(alle, q) - eb.regen_at(g, 0, q))
                for q in (0.5, 3.0, 5.0, 8.0, 12.5, 20.0))
    check("Allee regeneration matches released energy_balance.regen_at (unmodified)",
          worst < 1e-12, f"max diff {worst:.2e}")
    g.A = None
    worst = max(abs(d0.natural_drive(logi, q) - eb.regen_at(g, 0, q))
                for q in (0.5, 3.0, 10.0, 12.5, 20.0))
    check("logistic regeneration matches released energy_balance.regen_at",
          worst < 1e-12, f"max diff {worst:.2e}")
    check("declared external input shifts u by exactly s_extra",
          abs(d0.natural_drive(fin, 10.0, s_extra=0.7)
              - d0.natural_drive(fin, 10.0) - 0.7) < 1e-15)


# ===========================================================================
# [12] P1K nonphysical-service trap (Gate 1.1 Group A)
# ===========================================================================
def test_group12():
    group("P1K trap: ledger closure does not certify physical service")
    import dataclasses
    c = band_cell()
    w = d0.World(cells=(c, c), edges=(d0.Edge(0, 1, 2.2, 0.0, 0.6),))
    x = [19.0, 0.5]
    r = d0.p1k_step(w, x, 1.0)
    check("raw D0 overdraws the source (J = 20.68 > 19 available; y_src < 0)",
          abs(r.raw.J[0] - 20.68) < 1e-12 and r.raw.x_after[0] < 0.0,
          f"y_src={r.raw.x_after[0]:.6f}")
    check("destination nevertheless received the full raw lossy inflow",
          abs(r.raw.x_after[1] - (0.5 + 0.6 * 20.68)) < 1e-12,
          f"y_dst={r.raw.x_after[1]:.6f}")
    check("P1K projects the source to exactly zero", r.x_after[0] == 0.0)
    check("exact lower-bound shortfall recorded (1.68, unrounded)",
          abs(r.shortfall[0] - 1.68) < 1e-12, f"shortfall={r.shortfall[0]!r}")
    check("P1K ledger closes ONLY via the explicit +shortfall correction",
          abs(r.ledger_residual) < 1e-12 and r.shortfall[0] > 1.0,
          f"residual={r.ledger_residual:.2e} - closure alone is insufficient "
          f"evidence of physical availability")
    check("material_shortfall flag is true", r.material_shortfall is True,
          f"tau_b={r.boundary_tolerance:.2e}")
    check("physical-service-claim eligibility is false",
          r.eligible_for_physical_service_claim is False
          and r.raw_within_lower_bound is False)
    check("no result field describes the destination as validly served",
          all("served" not in f.name for f in dataclasses.fields(r)))
    check("P1K remains outside the theorem", r.covered_by_v28_theorem is False)


# ===========================================================================
# [13] boundary tolerance classification (Gate 1.1 Group B)
# ===========================================================================
def test_group13():
    group("boundary tolerance: noise vs material projection")
    c = band_cell(d=1.0)
    w = d0.World(cells=(c,), edges=())
    tiny = d0.p1k_step(w, [1.0], 1.0, d_extra=[1e-14])       # y = -1e-14
    check("tiny projection below tau_b is classified as numerical noise",
          tiny.material_shortfall is False
          and tiny.eligible_for_physical_service_claim is True,
          f"shortfall={tiny.shortfall[0]:.2e} < tau_b={tiny.boundary_tolerance:.2e}")
    check("tiny case: exact shortfall still stored, not erased by classification",
          0.0 < tiny.shortfall[0] < 1e-13, f"{tiny.shortfall[0]!r}")
    mat = d0.p1k_step(w, [1.0], 1.0, d_extra=[0.5])          # y = -0.5
    check("projection above tau_b is material and removes eligibility",
          mat.material_shortfall is True
          and mat.eligible_for_physical_service_claim is False
          and abs(mat.shortfall[0] - 0.5) < 1e-12)
    hi = d0.p1k_step(d0.World(cells=(band_cell(),), edges=()), [19.0], 1.0,
                     s_extra=[8.0])                          # y = 27 > K = 20
    check("material spill flagged; upper-bound flag false; exact spill stored",
          hi.material_spill is True and hi.raw_within_upper_bound is False
          and abs(hi.spill[0] - 7.0) < 1e-12)
    check("spill alone does not remove service-claim eligibility",
          hi.material_shortfall is False
          and hi.eligible_for_physical_service_claim is True)


# ===========================================================================
# [14] supply/demand semantics (Gate 1.1 Group C)
# ===========================================================================
def test_group14():
    group("supply/demand semantics: non-negative, signed drives by decomposition")
    rejections = [
        ("negative s", lambda: d0.Cell(alpha=1, beta=1, chi=0, L=5, U=15, R=0,
                                       K=20, s=-0.1)),
        ("negative d", lambda: d0.Cell(alpha=1, beta=1, chi=0, L=5, U=15, R=0,
                                       K=20, d=-0.1)),
        ("negative s_extra", lambda: d0.d0_step(
            d0.World(cells=(band_cell(),), edges=()), [10.0], 0.5, s_extra=[-0.1])),
        ("negative d_extra", lambda: d0.d0_step(
            d0.World(cells=(band_cell(),), edges=()), [10.0], 0.5, d_extra=[-0.1])),
        ("negative lam", lambda: d0.Cell(alpha=1, beta=1, chi=0, L=5, U=15, R=0,
                                         K=20, lam=-0.1)),
    ]
    for name, fn in rejections:
        try:
            fn()
            ok = False
        except (ValueError, TypeError):
            ok = True
        check(f"rejects {name}", ok)
    up = d0.natural_drive(band_cell(s=1.3), 10.0)
    dn = d0.natural_drive(band_cell(d=0.7), 10.0)
    check("positive drive represented by supply: u == +1.3", up == 1.3)
    check("negative drive represented by demand: u == -0.7", dn == -0.7)
    params, edges, x, u = FIXTURES[2]
    res = d0.d0_step(drive_world(params, edges, u), x, 0.3)
    check("decomposed representation reproduces the signed test drive exactly",
          max(abs(a - b) for a, b in zip(res.u, u)) == 0.0,
          f"u={u}")
    # equivalence of a legacy all-positive-supply representation
    pos_u = [abs(v) for v in u]
    w_dec = drive_world(params, edges, pos_u)
    w_leg = d0.World(cells=tuple(
        d0.Cell(alpha=a, beta=b, chi=ch, L=L, U=U, R=R, K=K, s=uv)
        for (a, b, ch, L, U, R, K), uv in zip(params, pos_u)), edges=tuple(edges))
    r1 = d0.d0_step(w_dec, x, 0.3)
    r2 = d0.d0_step(w_leg, x, 0.3)
    check("pure-supply and decomposed forms agree for non-negative drives",
          r1.x_after == r2.x_after)


# ===========================================================================
# [15] permutation robustness (Gate 1.1 Group D)
# ===========================================================================
def test_group15():
    group("permutation robustness of the synchronous update")
    rng = random.Random(V29_SEED + 2)
    n_perms_total = 0
    n_active = 0
    worst = 0.0
    tested = 0
    for params, edges, x, u in FIXTURES:
        if len(edges) < 3:
            continue
        tested += 1
        base_w = drive_world(params, edges, u)
        base = d0.d0_step(base_w, x, 0.3)
        if any(j > 0 for j in base.J):
            n_active += 1
        tol = 1e-12 * (1.0 + max(abs(v) for v in base.x_after))
        perms = [list(reversed(edges))] + [
            rng.sample(list(edges), len(edges)) for _ in range(11)]
        for perm in perms:
            n_perms_total += 1
            rp = d0.d0_step(drive_world(params, perm, u), x, 0.3)
            dev = max(abs(a - b) for a, b in zip(rp.x_after, base.x_after))
            dev = max(dev, abs(rp.ledger_residual - base.ledger_residual))
            worst = max(worst, dev)
            if dev > tol:
                check("permutation deviation within strict tolerance", False,
                      f"dev={dev:.2e} > tol={tol:.2e}",
                      fixture_repr(params, perm, x, u, 0.3))
                return
    WORST["permutation"] = worst
    check(f"{n_perms_total} permutations over {tested} multi-edge fixtures agree "
          f"within strict scale-aware tolerance",
          True, f"max residual {worst:.3e} (observed; cross-platform bit "
          f"identity is not claimed)")
    check("permutation fixtures include active edges",
          n_active >= tested // 2, f"{n_active}/{tested} active")


# ===========================================================================
if __name__ == "__main__":
    print("=" * 74)
    print("V2.9 Gate 1/1.1 - D0 engine conformance validation (NOT proof; no behavior)")
    print("=" * 74)
    print(f"Python {sys.version.split()[0]}   validation seed = {V29_SEED} "
          f"(distinct from behavioral seeds 0-9 / 100-139)")
    test_group1()
    test_group2()
    test_group3()
    test_group4()
    test_group5()
    test_group6()
    test_group7()
    test_group8()
    test_group9()
    test_group10()
    test_group11()
    test_group12()
    test_group13()
    test_group14()
    test_group15()
    print("-" * 74)
    for k, (title, p, f) in enumerate(GROUPS, 1):
        print(f"group {k:>2}: {p:>3} passed, {f} failed - {title}")
    print(f"total checks: {PASS} passed, {FAIL} failed in {len(GROUPS)} groups")
    print(f"max cross-conformance |diff|:   {WORST['conformance']:.3e}")
    print(f"max inequality residual:        {WORST['inequality']:.3e} "
          f"(<= 0 expected; fp-tolerance positive values acceptable)")
    print(f"max ledger residual:            {WORST['ledger']:.3e}")
    print(f"max permutation residual:       {WORST['permutation']:.3e} "
          f"(strict-tolerance contract; bit identity not promised cross-platform)")
    if FAIL:
        print("CONFORMANCE VALIDATION FAILED - see reproduce lines above.")
        raise SystemExit(1)
    print("Conformance validation passed; this is not a proof and makes no "
          "behavioral claim.")
