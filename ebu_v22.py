"""
Energy Balance - Foundation Model V2.2
Hardened engine: an explicit conservation ledger + a SAFE discrete movement law.

What changed vs V2.0/V2.1 (all consistent with the seven hard laws):

  1. Conservation ledger. Every tick records each flow separately:
         dX = S + G - D - Lambda - transport_loss - spill
     with unmet demand recorded on the side. The identity is asserted each tick.

  2. Safe discrete movement law. The potential gradient only PROPOSES a direction.
     A transfer executes only if the exact discrete burden check confirms improvement:
                       B_with_action < B_without_action
     (V2.0 Sec. 9 with H=1). Harmful proposals are rejected.

  3. Adaptive transfer size (line search). Instead of the raw q = M[F]_+, the transfer
     size is the amount that MINIMIZES the pair's combined burden (a golden-section
     search over the convex piecewise-quadratic penalty). This prevents overshoot.

Actors are stationary local processes (circulation analogy), as recommended.

Guarantee: in "safe" mode, redistribution can never increase B within a tick, so
Impact = B_without - B_with >= 0 by construction (discrete monotonicity).
"""
from __future__ import annotations
from dataclasses import dataclass, field

from energy_balance import Grid, Actor, clip, local_penalty, burden, mu, regen


# ----------------------------------------------------------------------------
@dataclass
class Ledger:
    S: float = 0.0            # external inflow applied
    G: float = 0.0            # regeneration applied
    D: float = 0.0            # demand actually consumed
    Lam: float = 0.0          # leakage actually lost
    transport_loss: float = 0.0
    spill: float = 0.0        # capacity rejected at the K bound (overflow)
    unmet_demand: float = 0.0 # demand that could not be met (recorded, not a flow)

    def dX(self) -> float:
        """Net change in total capacity implied by the recorded flows."""
        return self.S + self.G - self.D - self.Lam - self.transport_loss - self.spill

    def add(self, o: "Ledger"):
        self.S += o.S; self.G += o.G; self.D += o.D; self.Lam += o.Lam
        self.transport_loss += o.transport_loss; self.spill += o.spill
        self.unmet_demand += o.unmet_demand


@dataclass
class Report:
    tick: int
    B_before: float
    B_noaction: float
    B_withaction: float
    X: float
    n_below_L: int
    n_above_U: int
    proposed: int
    executed: int
    rejected: int
    ledger: Ledger
    impact: float             # B_noaction - B_withaction (>= 0 in safe mode)


# ----------------------------------------------------------------------------
def leak_of(g: Grid, i: int) -> float:
    base = g.lam[i]
    if g.leak_frac is not None:
        base += g.leak_frac[i] * g.x[i]
    return base


def natural_update_ledger(g: Grid) -> tuple[list[float], Ledger]:
    """No-action counterfactual with explicit, ordered flow accounting.

    Order per cell: apply inflow+regen, then leakage, then demand, then cap at K.
    Amounts are the ACTUAL realized values (you cannot leak/consume more than exists,
    and capacity above K spills)."""
    x0 = [0.0] * g.size
    led = Ledger()
    for i in range(g.size):
        s = g.s[i]
        gg = regen(g, i)                       # >= 0 for logistic on [0, K]
        leak = leak_of(g, i)
        d = g.d[i]
        pre = g.x[i] + s + gg
        led.S += s
        led.G += gg
        actual_leak = min(leak, pre) if pre > 0 else 0.0
        after_leak = pre - actual_leak
        actual_demand = min(d, after_leak)
        unmet = d - actual_demand
        after_demand = after_leak - actual_demand
        if after_demand > g.K[i]:
            spill = after_demand - g.K[i]
            xi = g.K[i]
        else:
            spill = 0.0
            xi = after_demand
        led.Lam += actual_leak
        led.D += actual_demand
        led.unmet_demand += unmet
        led.spill += spill
        x0[i] = xi
    return x0, led


def _line_search_q(g: Grid, i: int, j: int, xi: float, xj: float,
                   eta: float, c0: float, q_hi: float, iters: int = 24) -> float:
    """Golden-section minimizer of the convex pair burden
       f(q) = ell_i(xi - c0 - q) + ell_j(xj + eta*q)  over q in [0, q_hi]."""
    if q_hi <= 1e-12:
        return 0.0

    def f(q):
        return local_penalty(g, i, xi - c0 - q) + local_penalty(g, j, xj + eta * q)

    gr = 0.6180339887498949
    lo, hi = 0.0, q_hi
    for _ in range(iters):
        m1 = hi - gr * (hi - lo)
        m2 = lo + gr * (hi - lo)
        if f(m1) < f(m2):
            hi = m2
        else:
            lo = m1
    return 0.5 * (lo + hi)


def _proposals(g: Grid, actors: list[Actor], m: list[float]):
    """Each actor proposes its single best neighbor by positive driving force F_ij."""
    out = []
    for ai, a in enumerate(actors):
        i = a.pos
        best_j, best_F = None, 0.0
        for j in g.neighbors(i):
            F = m[i] - m[j] - a.theta
            if F > best_F:
                best_F, best_j = F, j
        if best_j is not None:
            out.append((ai, i, best_j, best_F))
    return out


def step_v22(g: Grid, actors: list[Actor], tick: int,
             mode: str = "safe", eps: float = 1e-9, check_ledger: bool = True) -> Report:
    """One synchronous tick.
       mode = "none"     -> physics only, no redistribution
              "gradient" -> raw q=M[F]_+ with proportional source scaling (original rule)
              "safe"     -> line-searched q* + exact discrete acceptance (V2.2)"""
    X_before = sum(g.x)
    B_before = burden(g, g.x)

    x0, led = natural_update_ledger(g)
    B_no = burden(g, x0)
    xa = list(x0)

    proposed = executed = rejected = 0

    if mode != "none" and actors:
        m = [mu(g, i, xa[i]) for i in range(g.size)]
        props = _proposals(g, actors, m)
        proposed = len(props)

        if mode == "gradient":
            # raw magnitude, proportional source scaling, applied together, NO acceptance
            need: dict[int, float] = {}
            raw = []
            for (ai, i, j, F) in props:
                a = actors[ai]
                q = a.M * F
                raw.append((ai, i, j, q))
                need[i] = need.get(i, 0.0) + q + a.c0
            scale = {}
            for i, w in need.items():
                avail = max(0.0, xa[i] - g.x_min[i])
                scale[i] = 1.0 if (w <= avail or w <= 0) else avail / w
            for (ai, i, j, q) in raw:
                a = actors[ai]
                f = scale[i]
                q *= f
                c0 = a.c0 * f
                q = min(q, a.q_max, max(0.0, (g.K[j] - xa[j]) / a.eta))
                if q <= 0:
                    continue
                if q + c0 > xa[i] - g.x_min[i] + 1e-12:
                    q = max(0.0, xa[i] - g.x_min[i] - c0)
                if q <= 0:
                    continue
                xa[i] -= (q + c0)
                xa[j] += a.eta * q
                led.transport_loss += (1.0 - a.eta) * q + c0
                executed += 1
            for k in range(g.size):
                xa[k] = clip(xa[k], 0.0, g.K[k])

        else:  # safe: single pass, strongest force first; line search + exact acceptance
            # Ordering by F (already computed) approximates ordering by benefit at near-zero
            # cost. Each transfer is verified against the LIVE state before applying, so B is
            # guaranteed non-increasing regardless of order (discrete monotonicity holds).
            for (ai, i, j, F) in sorted(props, key=lambda p: -p[3]):
                a = actors[ai]
                q_hi = min(a.q_max, xa[i] - g.x_min[i] - a.c0, (g.K[j] - xa[j]) / a.eta)
                if q_hi <= 0:
                    rejected += 1
                    continue
                q = _line_search_q(g, i, j, xa[i], xa[j], a.eta, a.c0, q_hi)
                f0 = local_penalty(g, i, xa[i]) + local_penalty(g, j, xa[j])
                fn = local_penalty(g, i, xa[i] - a.c0 - q) + local_penalty(g, j, xa[j] + a.eta * q)
                if q > 0 and fn < f0 - eps:
                    xa[i] -= (a.c0 + q)
                    xa[j] += a.eta * q
                    led.transport_loss += (1.0 - a.eta) * q + a.c0
                    executed += 1
                else:
                    rejected += 1

    B_with = burden(g, xa)
    g.x = xa

    if check_ledger:
        delta = sum(xa) - X_before
        if abs(delta - led.dX()) > 1e-6:
            raise AssertionError(f"ledger imbalance at tick {tick}: dX={delta} vs {led.dX()}")

    return Report(
        tick=tick, B_before=B_before, B_noaction=B_no, B_withaction=B_with,
        X=sum(xa),
        n_below_L=sum(1 for i in range(g.size) if xa[i] < g.L[i]),
        n_above_U=sum(1 for i in range(g.size) if xa[i] > g.U[i]),
        proposed=proposed, executed=executed, rejected=rejected,
        ledger=led, impact=B_no - B_with,
    )


if __name__ == "__main__":
    # Smoke test on the checkerboard from V2.1.
    from ecosystem import make_ecosystem
    for mode in ("none", "gradient", "safe"):
        g, actors = make_ecosystem(10, inflow=0.8)
        if mode == "none":
            actors = []
        cum = Ledger()
        Bs, viable, imp_neg = [], [], 0
        for t in range(1, 2001):
            r = step_v22(g, actors, t, mode=mode)
            cum.add(r.ledger)
            Bs.append(r.B_withaction)
            viable.append(g.size - r.n_below_L)
            if r.impact < -1e-9:
                imp_neg += 1
        print(f"mode={mode:8s}  B_mean={sum(Bs)/len(Bs):8.3f}  viable_final={viable[-1]:3d}/100"
              f"  neg-impact ticks={imp_neg:4d}  transport_loss={cum.transport_loss:8.2f}"
              f"  unmet={cum.unmet_demand:8.2f}")
