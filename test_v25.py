"""
V2.5 guarded-ledger property tests (the gate before experiments).
Run with the project venv (imports matplotlib via exp_v23):  .../venv/bin/python test_v25.py
"""
from energy_balance import Grid
from ebu_v24 import reserve_R
from ebu_v25 import EBULedger, step_v25, _action_effect, b_R, b_plain
from ebu_v23 import natural_update_ledger
import exp_v23


def mk(x0, x1, L=4.0, U=16.0, rho=0.0, A=0.0):
    """2x2 grid; cells 0 and 1 are the adjacent pair under test, 2 and 3 are in-band filler."""
    return Grid(n=2, x=[x0, x1, 10.0, 10.0], K=[20.0] * 4, L=[L] * 4, U=[U] * 4,
                alpha=[1.0] * 4, beta=[1.0] * 4, s=[0.0] * 4, d=[0.0] * 4, lam=[0.0] * 4,
                rho=[rho, 0.0, rho, 0.0], x_min=[0.0] * 4, A=[A, 0.0, A, 0.0])


def eff(g, i, j, q, eta, c0, xa, mode="guarded", lam_L=0.1, lam_F=1.0):
    R = reserve_R(g, 3.0)
    c, d, xi, xj, loss = _action_effect(mode, g, i, j, q, eta, c0, xa, R, 1.0, 0.0, 0.0, lam_L, lam_F)
    return c, d, xi, xj


# ---------------------------------------------------------------------------
def test_no_action_zero_credit():
    """A tick with no admissible beneficial action issues zero credit."""
    g = Grid(n=3, x=[10.0] * 9, K=[20.0] * 9, L=[4.0] * 9, U=[16.0] * 9, alpha=[1.0] * 9,
             beta=[1.0] * 9, s=[0.0] * 9, d=[0.0] * 9, lam=[0.0] * 9, rho=[0.0] * 9,
             x_min=[0.0] * 9)          # uniform, in-band -> no gradient
    from energy_balance import Actor
    led = EBULedger(mode="guarded")
    actors = [Actor(pos=i, q_max=3.0, M=0.6, theta=0.05, eta=0.95) for i in range(9)]
    r = step_v25(g, actors, led, 1, selection="physics")
    assert r.executed == 0 and led.issued_credit == 0.0 and all(b == 0 for b in led.balances)
    print("PASS  no action -> zero credit")


def test_natural_regen_not_credited():
    """Guarded credit excludes natural regeneration; naive credits it (the exploit)."""
    from energy_balance import Actor
    def scen():
        g = mk(4.0, 12.0, L=8.0, rho=0.6, A=0.0)   # cell 0 deep deficit AND regenerating fast
        actors = [Actor(pos=1, q_max=0.5, M=0.6, theta=0.05, eta=0.95)]  # tiny helper at cell 1
        return g, actors
    g, a = scen(); lg = EBULedger(mode="guarded"); rg = step_v25(g, a, lg, 1, selection="physics")
    g, a = scen(); ln = EBULedger(mode="naive");   rn = step_v25(g, a, ln, 1, selection="physics")
    assert lg.issued_credit >= 0.0
    assert ln.issued_credit > lg.issued_credit + 1.0, (ln.issued_credit, lg.issued_credit)
    print(f"PASS  natural regen not credited: guarded={lg.issued_credit:.2f} << naive={ln.issued_credit:.2f}")


def test_telescoping_no_double_credit():
    """Guarded issued credit over a physics tick == the actual B_R reduction from the
    actions (no actor is paid twice for the same reduction)."""
    from energy_balance import Actor
    g = mk(18.0, 2.0)                              # excess source, deep deficit
    # two helpers both able to serve cell 1 (from 0 and from 3 via... keep simple: both on 0->1)
    actors = [Actor(pos=0, q_max=2.0, M=0.6, theta=0.05, eta=1.0),
              Actor(pos=0, q_max=2.0, M=0.6, theta=0.05, eta=1.0)]
    gc = Grid(**{k: (list(v) if isinstance(v, list) else v) for k, v in g.__dict__.items()})
    x0, _ = natural_update_ledger(gc)
    R = reserve_R(g, 3.0)
    bR_before = b_R(g, x0, R, 1.0)
    led = EBULedger(mode="guarded")
    step_v25(g, actors, led, 1, selection="physics")
    bR_after = b_R(g, g.x, R, 1.0)
    assert abs(led.issued_credit - (bR_before - bR_after)) < 1e-6, (led.issued_credit, bR_before - bR_after)
    print(f"PASS  telescoping: issued credit {led.issued_credit:.3f} == B_R reduction {bR_before-bR_after:.3f}")


def test_perfect_roundtrip_zero():
    """A lossless round trip returning the system to its start earns exactly zero."""
    g = mk(18.0, 5.0); xa = list(g.x)
    c1, d1, xi, xj = eff(g, 0, 1, 5.0, 1.0, 0.0, xa); xa[0], xa[1] = xi, xj
    c2, d2, xi, xj = eff(g, 1, 0, 5.0, 1.0, 0.0, xa); xa[1], xa[0] = xi, xj   # reverse: (i=1, j=0)
    net = (c1 - d1) + (c2 - d2)
    assert abs(net) < 1e-9 and abs(xa[0] - 18.0) < 1e-9 and abs(xa[1] - 5.0) < 1e-9
    print(f"PASS  perfect round trip: net EBU = {net:+.2e} (state restored)")


def test_pointless_move_is_costly():
    """Moving capacity between two in-band cells (no burden change) with lossy transport
    is strictly negative EBU under guarded (back-and-forth cannot pay)."""
    g = mk(10.0, 10.0); xa = list(g.x)
    c, d, _, _ = eff(g, 0, 1, 3.0, 0.9, 0.0, xa)
    assert (c - d) < 0.0, (c, d)
    print(f"PASS  pointless move costly: net EBU = {c - d:+.3f}")


def test_damage_then_repair_nonpositive():
    """Damaging then exactly repairing (lossless) nets zero; never positive."""
    g = mk(10.0, 10.0); xa = list(g.x)
    c1, d1, xi, xj = eff(g, 0, 1, 8.0, 1.0, 0.0, xa); xa[0], xa[1] = xi, xj   # damage: 0->2, 1->18
    c2, d2, xi, xj = eff(g, 1, 0, 8.0, 1.0, 0.0, xa); xa[1], xa[0] = xi, xj   # repair: (i=1, j=0)
    net = (c1 - d1) + (c2 - d2)
    assert net <= 1e-9, net
    print(f"PASS  damage+repair: net EBU = {net:+.2e} (<= 0)")


def test_splitting_does_not_increase_reward():
    """Splitting one transfer into many (each paying its own transport cost) cannot earn
    more than the single transfer."""
    def single():
        g = mk(18.0, 4.0); xa = list(g.x)
        c, d, xi, xj = eff(g, 0, 1, 4.0, 0.95, 0.2, xa)
        return c - d
    def split(n=4):
        g = mk(18.0, 4.0); xa = list(g.x); tot = 0.0
        for _ in range(n):
            c, d, xi, xj = eff(g, 0, 1, 4.0 / n, 0.95, 0.2, xa); xa[0], xa[1] = xi, xj
            tot += c - d
        return tot
    s, sp = single(), split()
    assert sp <= s + 1e-9, (sp, s)
    print(f"PASS  splitting no gain: single {s:.3f} >= split {sp:.3f}")


def test_accounts_sum_to_credit_minus_debit():
    """Sum of account changes == issued credit - issued debit."""
    from energy_balance import Actor
    g, actors, _ = exp_v23.make_regen_world()
    led = EBULedger(mode="guarded")
    for t in range(1, 51):
        step_v25(g, actors, led, t, selection="physics")
    assert abs(sum(led.balances) - (led.issued_credit - led.issued_debit)) < 1e-6
    print(f"PASS  conservation of accounts: sum(bal)={sum(led.balances):.2f} == credit-debit")


def test_observational_identity():
    """With physics selection, the trajectory is identical whether EBU is off or guarded."""
    def run(mode):
        g, actors, _ = exp_v23.make_regen_world()
        led = EBULedger(mode=mode)
        traj = []
        for t in range(1, 51):
            step_v25(g, actors, led, t, selection="physics")
            traj.append(tuple(round(v, 9) for v in g.x))
        return traj
    assert run("none") == run("guarded")
    print("PASS  observational identity: physics trajectory unchanged by the EBU layer")


if __name__ == "__main__":
    tests = [
        test_no_action_zero_credit,
        test_natural_regen_not_credited,
        test_telescoping_no_double_credit,
        test_perfect_roundtrip_zero,
        test_pointless_move_is_costly,
        test_damage_then_repair_nonpositive,
        test_splitting_does_not_increase_reward,
        test_accounts_sum_to_credit_minus_debit,
        test_observational_identity,
    ]
    print("Energy Balance V2.5 - guarded-ledger property tests\n")
    for t in tests:
        t()
    print(f"\nAll {len(tests)} V2.5 tests passed.")
