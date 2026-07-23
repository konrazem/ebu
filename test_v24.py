"""
V2.4 tests: the protective rules and the foresight-artifact control.
Run with the project venv (imports matplotlib via exp_v23):  .../venv/bin/python test_v24.py
"""
from energy_balance import regen_at
from ebu_v24 import step_v24, marg, reserve_R
import exp_v23

A = exp_v23.A_THRESH


def _run(rule, ticks=300, shock=150, H=10):
    g, actors, is_src = exp_v23.make_regen_world()
    src = [i for i in range(g.size) if is_src[i]]
    cum_unmet = 0.0
    for t in range(1, ticks + 1):
        if t == shock:
            for i in src:
                g.x[i] *= 0.45
        r = step_v24(g, actors, t, rule=rule, H=H)
        cum_unmet += r.ledger.unmet_demand
    dead = sum(1 for i in src if g.x[i] < A and regen_at(g, i, g.x[i]) <= 0)
    viable = 100.0 * (g.size - sum(1 for i in range(g.size) if g.x[i] < g.L[i])) / g.size
    return dead, viable, len(src), cum_unmet


def test_horizon_gate_overharvests():
    """Control 1: the V2.3 gate (line-searched q + horizon accept) still over-harvests."""
    dead, viable, n, _ = _run("horizon_gate")
    assert dead > n // 2, (dead, n)
    print(f"PASS  horizon_gate over-harvests: {dead}/{n} sources dead, viable {viable:.0f}%")


def test_horizon_opt_is_sustainable():
    """DECISIVE control: choosing q to MAXIMISE I^H is sustainable -> the V2.3 failure was
    an artifact of the accept/reject architecture, not of foresight itself."""
    dead, viable, n, unmet = _run("horizon_opt")
    assert dead == 0, dead
    assert viable >= 90.0, viable
    assert unmet == 0.0, unmet
    print(f"PASS  horizon_opt sustainable: {dead}/{n} dead, viable {viable:.0f}%, unmet {unmet:.0f} "
          f"(foresight is NOT inherently destructive)")


def test_threshold_penalty_sustainable_and_serves():
    """The threshold-aware burden preserves sources AND serves demand (viable stays high)."""
    dead, viable, n, unmet = _run("threshold_penalty")
    assert dead == 0 and viable >= 90.0, (dead, viable)
    assert unmet == 0.0, unmet          # serves demand, not just preserves sources
    print(f"PASS  threshold_penalty: {dead}/{n} dead, viable {viable:.0f}%, "
          f"cumulative unmet={unmet:.0f} (preserves AND serves)")


def test_hard_reserve_sustainable():
    dead, viable, n, unmet = _run("hard_reserve")
    assert dead == 0 and viable >= 90.0, (dead, viable)
    assert unmet == 0.0, unmet
    print(f"PASS  hard_reserve: {dead}/{n} dead, viable {viable:.0f}%, unmet {unmet:.0f}")


def test_reserve_marginal_protects_depleted_source():
    """A regenerative source below its reserve R gets NEGATIVE extra potential (wants to
    retain), preserving the convex structure the line search needs."""
    g, _, is_src = exp_v23.make_regen_world()
    i = next(k for k in range(g.size) if is_src[k])
    R = reserve_R(g, delta=3.0)
    below = marg(g, i, R[i] - 2.0, R, chi=1.0, ra=True)
    plain = marg(g, i, R[i] - 2.0, R, chi=1.0, ra=False)
    assert below < plain, (below, plain)
    print(f"PASS  reserve potential: below-reserve source marg {below:.2f} < plain {plain:.2f}")


if __name__ == "__main__":
    tests = [
        test_horizon_gate_overharvests,
        test_horizon_opt_is_sustainable,
        test_threshold_penalty_sustainable_and_serves,
        test_hard_reserve_sustainable,
        test_reserve_marginal_protects_depleted_source,
    ]
    print("Energy Balance V2.4 - protective rules + foresight-artifact control\n")
    for t in tests:
        t()
    print(f"\nAll {len(tests)} V2.4 tests passed.")
