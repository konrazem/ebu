"""
Energy Balance - Foundation Model V2.5
An EBU accounting/incentive layer ON TOP OF the unchanged threshold-aware physics.

The physics (regeneration, transport, demand, conservation, the threshold-aware
burden B_R and its line-searched safe movement) is exactly V2.4's threshold_penalty
rule and is NOT modified here. The EBU layer only:
  * observes executed actions and their verified live-state consequences,
  * maintains per-actor accounts,
  * (optionally) influences SELECTION among physically admissible actions.

Ledger modes
------------
none    : no accounting (pure physics baseline).
naive   : credit = apparent immediate improvement in the PLAIN burden measured
          against the pre-tick full field; no debits. Exploitable by design
          (credits natural regeneration, double-counts across actors, ignores
          transport loss and regenerative-reserve sacrifice).
guarded : credit is the LIVE-STATE change in the threshold-aware burden B_R around
          the action (natural flows excluded), issued sequentially so several actors
          cannot be paid for the same reduction (telescoping). Burden INCREASES are
          debited symmetrically, and there are explicit debits for transport
          dissipation (lambda_L) and irreversible extraction below the Allee
          threshold (lambda_F):
              dEBU_a = [B_R(before_a) - B_R(after_a)] - lambda_L L_a - lambda_F F_a
              issued_credit_a = max(0,  B_R(before_a) - B_R(after_a))
              issued_debit_a  = max(0, -(B_R(before_a) - B_R(after_a)))
                                + lambda_L L_a + lambda_F F_a
          (The symmetric burden-increase debit is a refinement of the plain
          C_a = max(0, .) formula; it is required to make round-trips and
          damage-then-repair non-positive.)

Selection
---------
physics     : actions chosen by the threshold-aware physics (identical trajectory
              regardless of ledger mode -> EBU is observational).
adversarial : each actor chooses the admissible (neighbour, quantity) maximising its
              predicted dEBU under the ledger in force (chasing balance, not health).
"""
from __future__ import annotations
from dataclasses import dataclass, field

from energy_balance import Grid, Actor, local_penalty
from ebu_v22 import _proposals
from ebu_v23 import natural_update_ledger
from ebu_v24 import reserve_R, pen, marg, _golden_min

ADV_SAMPLES = 8


def b_plain(g: Grid, x: list[float]) -> float:
    return sum(local_penalty(g, i, x[i]) for i in range(g.size))


def b_R(g: Grid, x: list[float], R: list[float], chi: float) -> float:
    return sum(pen(g, i, x[i], R, chi, True) for i in range(g.size))


@dataclass
class EBULedger:
    mode: str = "none"                 # none | naive | guarded
    lam_L: float = 0.1                 # transport-dissipation debit weight
    lam_F: float = 1.0                 # irreversible-extraction debit weight
    balances: list[float] = field(default_factory=list)
    issued_credit: float = 0.0
    issued_debit: float = 0.0

    def ensure(self, n):
        if not self.balances:
            self.balances = [0.0] * n

    def record(self, actor, credit, debit):
        self.balances[actor] += credit - debit
        self.issued_credit += credit
        self.issued_debit += debit


def _action_effect(mode, g, i, j, q, eta, c0, xa, R, chi,
                   cur_plainB, pretick_plainB, lam_L, lam_F):
    """Return (credit, debit, xi_new, xj_new, loss) for transferring q from i to j,
    WITHOUT mutating state. Local (O(1)) in i,j."""
    xi0, xj0 = xa[i], xa[j]
    xi1, xj1 = xi0 - c0 - q, xj0 + eta * q
    loss = (1.0 - eta) * q + c0
    if mode == "guarded":
        bR0 = pen(g, i, xi0, R, chi, True) + pen(g, j, xj0, R, chi, True)
        bR1 = pen(g, i, xi1, R, chi, True) + pen(g, j, xj1, R, chi, True)
        dBR = bR0 - bR1                       # > 0 means the action reduced burden
        credit = max(0.0, dBR)
        penalty = max(0.0, -dBR)              # symmetric burden-increase debit
        F_a = 0.0
        if g.rho[i] > 0 and g.A is not None and g.A[i] > 0:
            F_a = max(0.0, max(0.0, g.A[i] - xi1) - max(0.0, g.A[i] - xi0))
        debit = penalty + lam_L * loss + lam_F * F_a
        return credit, debit, xi1, xj1, loss
    if mode == "naive":
        new_plainB = (cur_plainB - local_penalty(g, i, xi0) - local_penalty(g, j, xj0)
                      + local_penalty(g, i, xi1) + local_penalty(g, j, xj1))
        credit = max(0.0, pretick_plainB - new_plainB)   # vs FIXED pre-tick field
        return credit, 0.0, xi1, xj1, loss
    return 0.0, 0.0, xi1, xj1, loss           # mode == none


@dataclass
class StepResult:
    tick: int
    B_plain: float
    B_R: float
    X: float
    n_below_L: int
    n_below_A: int
    executed: int
    tick_credit: float
    tick_debit: float
    transport_loss: float


def step_v25(g: Grid, actors, ledger: EBULedger, tick: int,
             selection="physics", delta=3.0, chi=1.0, eps=1e-9) -> StepResult:
    ledger.ensure(len(actors))
    R = reserve_R(g, delta)
    x_pretick = list(g.x)
    pretick_plainB = b_plain(g, x_pretick)

    x0, flow = natural_update_ledger(g)
    xa = list(x0)
    cur_plainB = b_plain(g, xa)
    tick_credit = tick_debit = 0.0
    executed = 0

    def do(ai, i, j, q):
        nonlocal cur_plainB, tick_credit, tick_debit, executed
        a = actors[ai]
        credit, debit, xi1, xj1, loss = _action_effect(
            ledger.mode, g, i, j, q, a.eta, a.c0, xa, R, chi,
            cur_plainB, pretick_plainB, ledger.lam_L, ledger.lam_F)
        cur_plainB += (local_penalty(g, i, xi1) - local_penalty(g, i, xa[i])
                       + local_penalty(g, j, xj1) - local_penalty(g, j, xa[j]))
        xa[i], xa[j] = xi1, xj1
        flow.transport_loss += loss
        if ledger.mode != "none":
            ledger.record(ai, credit, debit)
            tick_credit += credit
            tick_debit += debit
        executed += 1

    if actors:
        if selection == "physics":
            m = [marg(g, k, xa[k], R, chi, True) for k in range(g.size)]
            for (ai, i, j, F) in sorted(_proposals(g, actors, m), key=lambda p: -p[3]):
                a = actors[ai]
                q_hi = min(a.q_max, xa[i] - g.x_min[i] - a.c0, (g.K[j] - xa[j]) / a.eta)
                if q_hi <= 0:
                    continue
                q = _golden_min(lambda qq: pen(g, i, xa[i] - a.c0 - qq, R, chi, True)
                                + pen(g, j, xa[j] + a.eta * qq, R, chi, True), q_hi)
                f0 = pen(g, i, xa[i], R, chi, True) + pen(g, j, xa[j], R, chi, True)
                fn = pen(g, i, xa[i] - a.c0 - q, R, chi, True) + pen(g, j, xa[j] + a.eta * q, R, chi, True)
                if q > 0 and fn < f0 - eps:
                    do(ai, i, j, q)
        else:  # adversarial: maximise predicted dEBU
            for ai in range(len(actors)):
                a = actors[ai]
                i = a.pos
                best_dE, best_j, best_q = eps, None, 0.0
                for j in g.neighbors(i):
                    q_hi = min(a.q_max, xa[i] - g.x_min[i] - a.c0, (g.K[j] - xa[j]) / a.eta)
                    if q_hi <= 0:
                        continue
                    for k in range(1, ADV_SAMPLES + 1):
                        q = q_hi * k / ADV_SAMPLES
                        c, d, _, _, _ = _action_effect(
                            ledger.mode, g, i, j, q, a.eta, a.c0, xa, R, chi,
                            cur_plainB, pretick_plainB, ledger.lam_L, ledger.lam_F)
                        if (c - d) > best_dE:
                            best_dE, best_j, best_q = c - d, j, q
                if best_j is not None:
                    do(ai, i, best_j, best_q)

    g.x = xa
    return StepResult(
        tick=tick, B_plain=cur_plainB, B_R=b_R(g, xa, R, chi), X=sum(xa),
        n_below_L=sum(1 for i in range(g.size) if xa[i] < g.L[i]),
        n_below_A=sum(1 for i in range(g.size)
                      if g.A is not None and g.A[i] > 0 and g.rho[i] > 0 and xa[i] < g.A[i]),
        executed=executed, tick_credit=tick_credit, tick_debit=tick_debit,
        transport_loss=flow.transport_loss)
