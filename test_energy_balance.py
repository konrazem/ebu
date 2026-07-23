"""
Physics unit tests required before experiments (Foundation Model V2.0, Sec. 14.1).
Run:  python3 test_energy_balance.py
"""
from energy_balance import (
    Grid, Actor, make_grid, run, step, burden, natural_update, regen,
)


def approx(a, b, tol=1e-9):
    return abs(a - b) <= tol


def test_bounds_respected():
    """A transfer never produces x_i < 0 or x_i > K_i (Law 3)."""
    g = make_grid(4)
    g.x[5] = 20.0            # oversupplied at K
    a = Actor(pos=5, q_max=100.0, M=10.0, theta=0.0, eta=1.0)
    run(g, [a], ticks=10, verbose=False)
    assert all(0.0 <= g.x[i] <= g.K[i] + 1e-9 for i in range(g.size)), g.x
    print("PASS  bounds: 0 <= x_i <= K_i held over 10 ticks")


def test_conservation_when_closed():
    """All sources/sinks/demand/losses disabled -> total capacity conserved (Law 2)."""
    g = make_grid(4)
    g.d = [0.0] * g.size
    g.lam = [0.0] * g.size
    g.s = [0.0] * g.size
    g.rho = [0.0] * g.size
    g.x[5] = 18.0            # imbalance so actor moves capacity around
    total_before = sum(g.x)
    a = Actor(pos=5, q_max=5.0, M=1.0, theta=0.0, eta=1.0, c0=0.0)  # lossless transport
    run(g, [a], ticks=10, verbose=False)
    assert approx(sum(g.x), total_before, 1e-6), (sum(g.x), total_before)
    print(f"PASS  conservation: closed lossless system conserved X = {total_before:.4f}")


def test_loss_accounting():
    """With transport inefficiency, total decreases by exactly the recorded loss (Law 2/4)."""
    g = make_grid(3)
    g.d = [0.0] * g.size
    g.lam = [0.0] * g.size
    g.x[4] = 18.0
    total_before = sum(g.x)
    a = Actor(pos=4, q_max=5.0, M=1.0, theta=0.0, eta=0.8, c0=0.1)  # lossy
    reps = run(g, [a], ticks=5, verbose=False)
    total_loss = sum(r.dissipated for r in reps)
    assert approx(sum(g.x), total_before - total_loss, 1e-6), \
        (sum(g.x), total_before, total_loss)
    print(f"PASS  loss accounting: dX = -{total_loss:.4f} matches recorded dissipation")


def test_finite_source_no_regen():
    """A finite source (rho=0) never regenerates (Law 5)."""
    g = make_grid(2)
    g.rho = [0.0] * g.size
    for i in range(g.size):
        assert regen(g, i) == 0.0
    print("PASS  finite source: regeneration is exactly 0")


def test_regenerative_source_follows_law():
    """A regenerative source follows its DECLARED logistic law (Law 5, Sec. 3).

    Distinct from the finite-source test: here rho>0. We check (a) g_i(x) equals the
    logistic formula exactly at a nontrivial point, and (b) an isolated regenerative
    stock grows monotonically toward its carrying capacity K.
    """
    g = make_grid(1)
    g.rho = [0.3]
    g.K = [20.0]
    g.x = [5.0]
    g.s = [0.0]
    g.d = [0.0]
    g.lam = [0.0]
    g.leak_frac = None
    # (a) exact formula: g = rho * x * (1 - x/K)
    expected = 0.3 * 5.0 * (1.0 - 5.0 / 20.0)
    assert approx(regen(g, 0), expected), (regen(g, 0), expected)
    # (b) isolated stock grows monotonically toward K (no demand/inflow/leak)
    prev = g.x[0]
    for t in range(1, 300):
        step(g, [], t)
        assert g.x[0] >= prev - 1e-9, (t, g.x[0], prev)   # non-decreasing
        assert g.x[0] <= g.K[0] + 1e-9                    # never exceeds K
        prev = g.x[0]
    assert abs(g.x[0] - 20.0) < 0.5, g.x[0]               # converges to carrying capacity
    print(f"PASS  regenerative source: logistic g matches formula; stock grew 5 -> {g.x[0]:.3f} (K=20)")


def test_ideal_gradient_flow_never_increases_B():
    """Ideal lossless gradient flow must never increase B (Sec. 8 monotonicity proof)."""
    g = make_grid(5)
    g.d = [0.0] * g.size
    g.lam = [0.0] * g.size
    g.s = [0.0] * g.size
    g.rho = [0.0] * g.size
    # random-ish imbalance (deterministic)
    for i in range(g.size):
        g.x[i] = 2.0 + (i * 7) % 17
    # many lossless, frictionless actors so redistribution dominates
    actors = [Actor(pos=i, q_max=100.0, M=0.4, theta=0.0, eta=1.0, c0=0.0)
              for i in range(g.size)]
    B = burden(g, g.x)
    for t in range(1, 51):
        rep = step(g, actors, t)
        assert rep.B_withaction <= B + 1e-6, (t, rep.B_withaction, B)
        B = rep.B_withaction
    print(f"PASS  monotonicity: ideal gradient flow drove B down to {B:.4f}, never increased")


def test_branches_reproducible():
    """No-action and action branches are reproducible from the same state."""
    def scenario():
        g = make_grid(3)
        g.x[4] = 18.0
        return g, [Actor(pos=4, q_max=5.0, M=1.0, theta=0.05, eta=0.9)]
    g1, a1 = scenario()
    r1 = run(g1, a1, ticks=5, verbose=False)
    g2, a2 = scenario()
    r2 = run(g2, a2, ticks=5, verbose=False)
    assert [x.impact for x in r1] == [x.impact for x in r2]
    assert g1.x == g2.x
    print("PASS  reproducibility: identical initial state -> identical trajectory")


def test_impact_excludes_natural_flow():
    """Actor impact excludes natural inflow/regen present in both branches (Law 7).

    With NO actor action possible (actor boxed in with no positive F), impact must be
    exactly 0 even though inflow/regen/demand change the field.
    """
    g = make_grid(3)
    g.s = [2.0] * g.size          # inflow present
    g.rho = [0.3] * g.size        # regeneration present
    g.x = [10.0] * g.size         # uniform -> all mu = 0 -> no driving force
    a = Actor(pos=4, q_max=5.0, M=1.0, theta=0.05, eta=0.9)
    reps = run(g, [a], ticks=5, verbose=False)
    assert all(approx(r.impact, 0.0, 1e-9) for r in reps), [r.impact for r in reps]
    print("PASS  counterfactual: natural inflow/regen not credited to actor (impact=0)")


if __name__ == "__main__":
    tests = [
        test_bounds_respected,
        test_conservation_when_closed,
        test_loss_accounting,
        test_finite_source_no_regen,
        test_regenerative_source_follows_law,
        test_ideal_gradient_flow_never_increases_B,
        test_branches_reproducible,
        test_impact_excludes_natural_flow,
    ]
    print("Energy Balance V2.0 - physics unit tests (Sec. 14.1)\n")
    for t in tests:
        t()
    print(f"\nAll {len(tests)} tests passed.")
