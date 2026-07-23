"""
V2.2 hardening tests: conservation ledger + safe discrete movement law.
Run:  python3 test_v22.py
"""
from energy_balance import Grid, Actor
from ebu_v22 import step_v22, Ledger, natural_update_ledger
from ecosystem import make_ecosystem


def approx(a, b, tol=1e-6):
    return abs(a - b) <= tol


def one_cell(x, s=0.0, d=0.0, K=20.0, leak=0.0):
    return Grid(n=1, x=[x], K=[K], L=[5.0], U=[15.0], alpha=[1.0], beta=[1.0],
               s=[s], d=[d], lam=[leak], rho=[0.0], x_min=[0.0])


def two_cell(x0v, x1v, x2v, x3v):
    return Grid(n=2, x=[x0v, x1v, x2v, x3v], K=[20.0] * 4, L=[5.0] * 4, U=[15.0] * 4,
                alpha=[1.0] * 4, beta=[1.0] * 4, s=[0.0] * 4, d=[0.0] * 4,
                lam=[0.0] * 4, rho=[0.0] * 4, x_min=[0.0] * 4)


# ---------------------------------------------------------------------------
def test_overflow_spill():
    """Overflow above K is recorded as spill; x is capped; ledger balances."""
    g = one_cell(x=10.0, s=15.0, K=20.0)      # 10 + 15 = 25 -> cap 20, spill 5
    r = step_v22(g, [], 1)
    assert approx(g.x[0], 20.0), g.x[0]
    assert approx(r.ledger.spill, 5.0), r.ledger.spill
    assert approx(r.ledger.S, 15.0)
    assert approx(r.ledger.unmet_demand, 0.0)
    print(f"PASS  overflow: spill={r.ledger.spill:.1f}, x capped at {g.x[0]:.1f}, ledger balances")


def test_unmet_demand():
    """Demand beyond available capacity is recorded as unmet; x floors at 0; ledger balances."""
    g = one_cell(x=3.0, d=10.0)               # only 3 available, demand 10 -> unmet 7
    r = step_v22(g, [], 1)
    assert approx(g.x[0], 0.0), g.x[0]
    assert approx(r.ledger.D, 3.0), r.ledger.D
    assert approx(r.ledger.unmet_demand, 7.0), r.ledger.unmet_demand
    print(f"PASS  unmet demand: consumed={r.ledger.D:.1f}, unmet={r.ledger.unmet_demand:.1f}, x=0")


def test_ledger_balances_over_run():
    """Every tick: dX_realized == S+G-D-Lambda-loss-spill (checked inside step, plus cumulative)."""
    g, actors = make_ecosystem(10, inflow=0.8)
    X0 = sum(g.x)
    cum = Ledger()
    for t in range(1, 501):
        r = step_v22(g, actors, t, mode="safe", check_ledger=True)  # raises on imbalance
        cum.add(r.ledger)
    assert approx(sum(g.x) - X0, cum.dX(), 1e-4), (sum(g.x) - X0, cum.dX())
    print(f"PASS  ledger: 500 ticks balanced; X change {sum(g.x)-X0:.2f} == ledger dX {cum.dX():.2f}")


def test_harmful_proposal_rejected():
    """The gradient may PROPOSE a transfer that raises B; safe mode must reject it.

    Cell 0 is barely above U; its in-band neighbor needs almost nothing. A large-M raw
    gradient overshoots and increases burden; the safe rule line-searches to the optimum
    and only executes a beneficial transfer.
    """
    # gradient (unsafe): overshoots -> global burden increases -> impact < 0
    g = two_cell(16.0, 14.0, 10.0, 10.0)
    a = Actor(pos=0, q_max=20.0, M=5.0, theta=0.05, eta=1.0, c0=0.0)
    rg = step_v22(g, [a], 1, mode="gradient")
    assert rg.impact < -1e-6, f"expected harmful gradient, impact={rg.impact}"

    # safe: same state -> never harmful, and it does help
    g2 = two_cell(16.0, 14.0, 10.0, 10.0)
    a2 = Actor(pos=0, q_max=20.0, M=5.0, theta=0.05, eta=1.0, c0=0.0)
    rs = step_v22(g2, [a2], 1, mode="safe")
    assert rs.impact >= -1e-9, f"safe mode raised B, impact={rs.impact}"
    assert rs.B_withaction <= rs.B_noaction + 1e-9
    assert rs.executed >= 1, "safe mode should still execute the beneficial part"
    print(f"PASS  safeguard: gradient impact={rg.impact:+.2f} (harmful) vs "
          f"safe impact={rs.impact:+.2f} (beneficial, executed={rs.executed})")


def test_discrete_monotonicity_pure_redistribution():
    """With no natural dynamics, safe redistribution makes B non-increasing every tick."""
    g = Grid(n=5, x=[2.0 + (i * 7) % 17 for i in range(25)], K=[20.0] * 25,
             L=[5.0] * 25, U=[15.0] * 25, alpha=[1.0] * 25, beta=[1.0] * 25,
             s=[0.0] * 25, d=[0.0] * 25, lam=[0.0] * 25, rho=[0.0] * 25, x_min=[0.0] * 25)
    actors = [Actor(pos=i, q_max=100.0, M=1.0, theta=0.0, eta=1.0) for i in range(25)]
    from energy_balance import burden
    prev = burden(g, g.x)
    for t in range(1, 101):
        r = step_v22(g, actors, t, mode="safe")
        assert r.B_withaction <= prev + 1e-9, (t, r.B_withaction, prev)
        assert r.impact >= -1e-9
        prev = r.B_withaction
    print(f"PASS  discrete monotonicity: B never increased over 100 ticks, ended at {prev:.4f}")


def test_impact_nonnegative_in_dynamic_world():
    """In the full dynamic checkerboard, safe redistribution never worsens burden vs no-action."""
    g, actors = make_ecosystem(10, inflow=0.8)
    worst = 0.0
    for t in range(1, 501):
        r = step_v22(g, actors, t, mode="safe")
        worst = min(worst, r.impact)
    assert worst >= -1e-6, worst
    print(f"PASS  impact >= 0: worst redistribution impact over 500 ticks was {worst:+.2e}")


def test_bounds_safe():
    """0 <= x_i <= K_i in safe mode over a long run."""
    g, actors = make_ecosystem(10, inflow=0.8)
    for t in range(1, 501):
        step_v22(g, actors, t, mode="safe")
    assert all(0.0 <= g.x[i] <= g.K[i] + 1e-9 for i in range(g.size))
    print("PASS  bounds: 0 <= x_i <= K_i held over 500 safe ticks")


if __name__ == "__main__":
    tests = [
        test_overflow_spill,
        test_unmet_demand,
        test_ledger_balances_over_run,
        test_harmful_proposal_rejected,
        test_discrete_monotonicity_pure_redistribution,
        test_impact_nonnegative_in_dynamic_world,
        test_bounds_safe,
    ]
    print("Energy Balance V2.2 - ledger + safe-movement tests\n")
    for t in tests:
        t()
    print(f"\nAll {len(tests)} V2.2 tests passed.")
