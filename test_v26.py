"""
V2.6 tests: behavior of the adversarial search + exploit machinery.
Run with the project venv (imports matplotlib via exp modules):
  .../venv/bin/python test_v26.py
"""
import importlib, random
from energy_balance import Grid, Actor
from ebu_v24 import reserve_R
from ebu_v25 import EBULedger, step_v25, b_R
from ebu_v26 import (State, forced_tick, source_cells, coalition_net, redteam_search,
                     find_exploit, baseline_BR_schedule, classify_exploit, beam_search)
import exp_v26


def approx(a, b, tol=1e-6):
    return abs(a - b) <= tol


def mk(cells, rho=0.0, A=0.0):
    """2x2; cells 0,1 the pair (cell 0 optionally a regenerative source)."""
    v = [cells[0], cells[1], 10.0, 10.0]
    return Grid(n=2, x=v, K=[20.0] * 4, L=[4.0] * 4, U=[16.0] * 4, alpha=[1.0] * 4,
                beta=[1.0] * 4, s=[0.0] * 4, d=[0.0] * 4, lam=[0.0] * 4,
                rho=[rho, 0.0, 0.0, 0.0], x_min=[0.0] * 4, A=[A, 0.0, 0.0, 0.0])


# ---------------------------------------------------------------------------
def test_prior_33_pass():
    total = 0
    for modname in ("test_energy_balance", "test_v22", "test_v23", "test_v24", "test_v25"):
        m = importlib.import_module(modname)
        fns = [getattr(m, n) for n in dir(m) if n.startswith("test_")]
        for fn in fns:
            fn()
        total += len(fns)
    assert total == 33, total
    print(f"PASS  prior suites: {total} tests all pass")


def test_observational_trajectory_unchanged():
    def run(mode):
        g, actors, _ = exp_v26.redteam_world()
        led = EBULedger(mode=mode)
        traj = []
        for t in range(1, 11):
            step_v25(g, actors, led, t, selection="physics")
            traj.append(tuple(g.x))
        return traj
    assert run("none") == run("guarded")
    print("PASS  observational EBU leaves the physical trajectory exactly unchanged")


def test_conservation_multi_action():
    g, actors, _ = exp_v26.redteam_world()
    st = State(list(g.x), [0.0] * len(actors))
    for t in range(5):
        acts = [(0, 4, 1, 2.0), (1, 1, 0, 1.5)]      # multi-action sequence
        st, rec = forced_tick(g, actors, st, acts, "guarded")
        assert approx(rec["dX"], rec["flow"].dX(), 1e-6), (rec["dX"], rec["flow"].dX())
    print("PASS  conservation holds during searched multi-action sequences (dX == ledger)")


def test_search_reproducible():
    def once():
        g, actors, _ = exp_v26.redteam_world()
        init = State(list(g.x), [0.0] * len(actors))
        base, _ = baseline_BR_schedule(g, actors, init, 8, "guarded")
        beams, expl = redteam_search(g, actors, [0, 1], init, "guarded", 8, 20,
                                     (0.5, 1.0), base[:8])
        return beams[0][2], expl, [b[3] for b in beams[:3]]
    a, b = once(), once()
    assert a[0] == b[0] and a[1] == b[1] and a[2] == b[2]
    print("PASS  search results reproducible with the same seed/inputs")


def test_random_layouts_differ():
    _, _, _, s0 = exp_v26.random_allee_world(0)
    _, _, _, s1 = exp_v26.random_allee_world(1)
    _, _, _, s0b = exp_v26.random_allee_world(0)
    assert s0 != s1, "distinct seeds gave identical layouts"
    assert s0 == s0b, "same seed not reproducible"
    print(f"PASS  random layouts differ across seeds (sources: seed0={sum(s0)}, seed1={sum(s1)})")


def test_search_rediscovers_naive_exploit():
    """Positive control: the search must find a known naive-ledger exploit."""
    g, actors, src = exp_v26.redteam_world()
    init = State(list(g.x), [0.0] * len(actors))
    base, _ = baseline_BR_schedule(g, actors, init, exp_v26.DEPTH + exp_v26.TAIL, "naive")
    beams, _ = redteam_search(g, actors, [0, 1], init, "naive", exp_v26.DEPTH,
                              exp_v26.WIDTH, exp_v26.QUANTS, base[:exp_v26.DEPTH], min_net=0.5)
    v = find_exploit(g, actors, [0, 1], beams, "naive",
                     base[exp_v26.DEPTH:exp_v26.DEPTH + exp_v26.TAIL], exp_v26.TAIL)
    assert v.is_exploit and v.net_ebu > 0 and v.harm_persistent, v
    print(f"PASS  search rediscovers a naive exploit: net={v.net_ebu:+.2f}, persistent harm")


def test_coalition_totals_equal_credit_minus_debit():
    g, actors, _ = exp_v26.redteam_world()
    st = State(list(g.x), [0.0] * len(actors))
    for _ in range(6):
        st, _ = forced_tick(g, actors, st, [(0, 4, 1, 2.0), (1, 1, 4, 1.0)], "guarded")
    assert approx(sum(st.bal), st.issued_c - st.issued_d, 1e-6)
    print(f"PASS  account totals == issued credit - issued debit ({sum(st.bal):.2f})")


def test_lossless_cycle_no_positive_ebu():
    """A state-restoring lossless two-actor cycle cannot create positive guarded EBU."""
    g = mk([18.0, 5.0])
    actors = [Actor(pos=0, q_max=10.0, M=1.0, theta=0.0, eta=1.0, c0=0.0),
              Actor(pos=1, q_max=10.0, M=1.0, theta=0.0, eta=1.0, c0=0.0)]
    st = State(list(g.x), [0.0, 0.0])
    st, _ = forced_tick(g, actors, st, [(0, 0, 1, 5.0)], "guarded", lam_L=0.1)
    st, _ = forced_tick(g, actors, st, [(1, 1, 0, 5.0)], "guarded", lam_L=0.1)  # restores start
    assert approx(st.x[0], 18.0) and approx(st.x[1], 5.0), st.x
    assert sum(st.bal) <= 1e-9, sum(st.bal)
    print(f"PASS  lossless restoring cycle: coalition net = {sum(st.bal):+.2e} (<= 0)")


def test_splitting_no_increase():
    def one():
        g = mk([18.0, 4.0]); st = State(list(g.x), [0.0, 0.0])
        st, _ = forced_tick(g, [Actor(pos=0, q_max=8.0, M=1, theta=0, eta=1.0, c0=0.0),
                                 Actor(pos=1, q_max=8, M=1, theta=0, eta=1.0)], st,
                            [(0, 0, 1, 4.0)], "guarded")
        return sum(st.bal)
    def split(n=4):
        g = mk([18.0, 4.0]); st = State(list(g.x), [0.0, 0.0])
        acts_actors = [Actor(pos=0, q_max=8.0, M=1, theta=0, eta=1.0, c0=0.0),
                       Actor(pos=1, q_max=8, M=1, theta=0, eta=1.0)]
        for _ in range(n):
            st, _ = forced_tick(g, acts_actors, st, [(0, 0, 1, 4.0 / n)], "guarded")
        return sum(st.bal)
    s, sp = one(), split()
    assert sp <= s + 1e-9, (sp, s)
    print(f"PASS  splitting (same lossless trajectory) no gain: single {s:.3f} >= split {sp:.3f}")


def test_exploit_classifier_requires_both():
    base = [10.0] * 5
    persistent = [15.0] * 5      # worse than base at every tick
    transient = [15.0, 10.0, 10.0, 10.0, 10.0]
    assert classify_exploit(+5.0, persistent, base).is_exploit is True
    assert classify_exploit(+5.0, transient, base).is_exploit is False   # harm not persistent
    assert classify_exploit(-1.0, persistent, base).is_exploit is False  # not profitable
    assert classify_exploit(0.0, persistent, base).is_exploit is False
    print("PASS  exploit requires BOTH positive net EBU AND persistent physical harm")


def test_search_no_future_access():
    """The search is deterministic and consumes no global RNG, so it cannot peek at
    'future' random events; advancing the global RNG between runs changes nothing."""
    def run():
        g, actors, _ = exp_v26.redteam_world()
        init = State(list(g.x), [0.0] * len(actors))
        base, _ = baseline_BR_schedule(g, actors, init, 6, "guarded")
        beams, _ = redteam_search(g, actors, [0, 1], init, "guarded", 6, 15, (0.5, 1.0), base[:6])
        return beams[0][2]
    a = run()
    for _ in range(1000):
        random.random()            # perturb global RNG
    b = run()
    assert a == b
    print("PASS  search uses no future/global randomness (result invariant to RNG state)")


def test_physics_identical_to_frozen():
    """The V2.6 physics-only path reproduces the frozen step_v25 physics trajectory."""
    def frozen_final():
        g, actors, _ = exp_v26.redteam_world()
        led = EBULedger(mode="none")
        for t in range(1, 11):
            step_v25(g, actors, led, t, selection="physics")
        return tuple(g.x)
    # V2.6 physics-only path runs the SAME frozen step_v25; final state must match,
    # and the frozen physics must be deterministic across runs.
    m = exp_v26.run_stepv25_traj(exp_v26.redteam_world, "physics", "none", 10)
    g2, actors2, src2 = exp_v26.redteam_world()
    R = reserve_R(g2, 3.0)
    assert frozen_final() == frozen_final(), "frozen physics not deterministic"
    # run_stepv25_traj reports final metrics; recompute frozen final metrics and compare B_R/X
    g3, actors3, src3 = exp_v26.redteam_world()
    led3 = EBULedger(mode="none")
    for t in range(1, 11):
        step_v25(g3, actors3, led3, t, selection="physics")
    from ebu_v26 import phys_metrics
    mf = phys_metrics(g3, g3.x, reserve_R(g3, 3.0), 1.0, src3)
    assert approx(m["B_R"], mf["B_R"]) and approx(m["X"], mf["X"])
    print("PASS  physics-only path identical to frozen V2.5 physics (deterministic)")


if __name__ == "__main__":
    tests = [
        test_prior_33_pass,
        test_observational_trajectory_unchanged,
        test_conservation_multi_action,
        test_search_reproducible,
        test_random_layouts_differ,
        test_search_rediscovers_naive_exploit,
        test_coalition_totals_equal_credit_minus_debit,
        test_lossless_cycle_no_positive_ebu,
        test_splitting_no_increase,
        test_exploit_classifier_requires_both,
        test_search_no_future_access,
        test_physics_identical_to_frozen,
    ]
    print("Energy Balance V2.6 - adversarial-search tests\n")
    for t in tests:
        t()
    print(f"\nAll {len(tests)} V2.6 tests passed (plus the 33 prior verified by test 1).")
