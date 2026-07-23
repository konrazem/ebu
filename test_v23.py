"""
V2.3 tests: source behaviours (regeneration) + the H-horizon counterfactual.
Run:  python3 test_v23.py
"""
from energy_balance import Grid, Actor, regen_at
from ebu_v23 import step_v23, natural_update_ledger, _horizon_impact, Ledger


def approx(a, b, tol=1e-6):
    return abs(a - b) <= tol


def src_cell(x, rho=0.3, A=0.0, K=20.0):
    return Grid(n=1, x=[x], K=[K], L=[4.0], U=[16.0], alpha=[1.0], beta=[1.0],
               s=[0.0], d=[0.0], lam=[0.0], rho=[rho], x_min=[0.0], A=[A])


def test_four_source_types():
    """External / logistic / Allee / finite are distinguished by (s, rho, A)."""
    # finite: rho=0 -> no regen
    assert regen_at(src_cell(10, rho=0.0), 0, 10.0) == 0.0
    # logistic (A=0): g = rho x (1 - x/K) > 0 in (0,K)
    g = src_cell(10, rho=0.3, A=0.0)
    assert approx(regen_at(g, 0, 10.0), 0.3 * 10 * (1 - 10 / 20))
    # Allee (A>0): negative below A, positive between A and K
    g = src_cell(10, rho=0.3, A=8.0)
    assert regen_at(g, 0, 5.0) < 0.0            # below threshold -> declining
    assert regen_at(g, 0, 12.0) > 0.0           # above threshold -> growing
    print("PASS  four source types: finite/logistic/Allee distinguished by (s, rho, A)")


def test_ledger_balances_with_signed_regen():
    """Allee regeneration can be negative; the ledger still balances every tick."""
    size = 36
    g = Grid(n=6, x=[7.0] * size, K=[20.0] * size, L=[4.0] * size, U=[16.0] * size,
             alpha=[1.0] * size, beta=[0.3] * size, s=[0.0] * size, d=[0.2] * size,
             lam=[0.0] * size, rho=[0.3] * size, x_min=[0.0] * size, A=[8.0] * size,
             leak_frac=[0.005] * size)
    actors = [Actor(pos=i, q_max=3.0, M=0.6, theta=0.05, eta=0.95) for i in range(size)]
    X0 = sum(g.x)
    cum = Ledger()
    for t in range(1, 201):
        r = step_v23(g, actors, t, mode="horizon", H=3, radius=2, check_ledger=True)
        cum.add(r.ledger)
    assert approx(sum(g.x) - X0, cum.dX(), 1e-4)
    print(f"PASS  signed-regen ledger: 200 Allee ticks balanced (dX={cum.dX():.2f})")


def test_horizon_counterfactual_overcredits_with_H():
    """DOCUMENTED PATHOLOGY: the single-action Sec. 9 counterfactual credits a harvest
    MORE as the horizon grows, because it assumes the action is not repeated and the
    source regenerates freely. This is why naive long-H 'foresight' over-harvests."""
    g = Grid(n=2, x=[12.0, 5.0, 10.0, 10.0], K=[20.0] * 4, L=[4.0] * 4, U=[16.0] * 4,
             alpha=[1.0] * 4, beta=[0.3] * 4, s=[0.0] * 4, d=[0.0, 0.45, 0.0, 0.45],
             lam=[0.0] * 4, rho=[0.3, 0.0, 0.3, 0.0], x_min=[0.0] * 4,
             A=[8.0, 0.0, 8.0, 0.0], leak_frac=[0.003] * 4)
    imp = [_horizon_impact(g, 0, 1, 4.0, 0.95, 0.0, [0, 1], H, 0.95) for H in (1, 3, 10, 30)]
    assert imp[0] <= imp[1] <= imp[2] <= imp[3], imp
    assert imp[3] > imp[0] + 1.0, imp        # materially larger at long horizon
    print(f"PASS  horizon over-credit: single-harvest impact rises with H {[round(x,2) for x in imp]}")


def test_myopic_preserves_regenerative_sources():
    """In the closed Allee economy, the myopic safe rule keeps sources above A after a
    shock (regeneration-preserving), whereas naive long-horizon over-harvests them."""
    import exp_v23
    _, m_safe = exp_v23.run_model("safe")
    _, m_h10 = exp_v23.run_model("horizon", H=10)
    assert m_safe["dead_sources"] == 0, m_safe["dead_sources"]
    assert m_h10["dead_sources"] > m_safe["dead_sources"]
    print(f"PASS  myopia protective: safe dead={m_safe['dead_sources']}/32 vs "
          f"H=10 dead={m_h10['dead_sources']}/32")


if __name__ == "__main__":
    tests = [
        test_four_source_types,
        test_ledger_balances_with_signed_regen,
        test_horizon_counterfactual_overcredits_with_H,
        test_myopic_preserves_regenerative_sources,
    ]
    print("Energy Balance V2.3 - regeneration + horizon tests\n")
    for t in tests:
        t()
    print(f"\nAll {len(tests)} V2.3 tests passed.")
