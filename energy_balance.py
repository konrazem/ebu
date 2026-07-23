"""
The Energy Balance Project - Foundation Model V2.0
Minimal faithful prototype of the homeostatic field model and local actor-motion law.

This implements, at small scale:
  - One dynamic scalar field x_i(t) >= 0 on a graph/lattice   (Sec. 2)
  - Local parameters: demand d_i, capacity K_i, viable band [L_i, U_i],
    inflow s_i, regeneration g_i(x), leakage lambda_i          (Sec. 2, 3)
  - The natural (no-action counterfactual) update              (Sec. 2)
  - Homeostatic burden functional B and marginal potential mu  (Sec. 6)
  - Gradient-flow actor law with driving force F_ij            (Sec. 7)
  - Continuity accounting + non-negative transport dissipation (Sec. 5, Laws 2/3/4)
  - Proportional conflict resolution                           (Sec. 12.1)
  - Counterfactual impact:  Impact = B_noaction - B_withaction (Sec. 10)

IMPORTANT (Law 6): homeostasis is NOT forced. The engine enforces physics only;
survival/oscillation/collapse must emerge.
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field


# ----------------------------------------------------------------------------
# Grid / field
# ----------------------------------------------------------------------------
@dataclass
class Grid:
    n: int                                   # n x n square lattice
    x: list[float]                           # dynamic capacity per cell
    K: list[float]                           # max capacity (upper bound)
    L: list[float]                           # min viable reserve (lower band)
    U: list[float]                           # oversupply threshold (upper band)
    alpha: list[float]                       # deficit penalty weight
    beta: list[float]                        # excess penalty weight
    s: list[float]                           # external inflow
    d: list[float]                           # demand / metabolism
    lam: list[float]                         # leakage / degradation
    rho: list[float]                         # regeneration rate (0 => none)
    x_min: list[float]                       # hard reserve floor for outflow
    leak_frac: list[float] | None = None     # proportional leakage kappa (leak = kappa * x)
    A: list[float] | None = None             # Allee threshold (None/<=0 => plain logistic)

    @property
    def size(self) -> int:
        return self.n * self.n

    def idx(self, r: int, c: int) -> int:
        return r * self.n + c

    def neighbors(self, i: int) -> list[int]:
        """von Neumann 4-neighborhood (Sec. 2)."""
        r, c = divmod(i, self.n)
        out = []
        if r > 0:            out.append(self.idx(r - 1, c))
        if r < self.n - 1:   out.append(self.idx(r + 1, c))
        if c > 0:            out.append(self.idx(r, c - 1))
        if c < self.n - 1:   out.append(self.idx(r, c + 1))
        return out


def clip(v: float, lo: float, hi: float) -> float:
    return lo if v < lo else hi if v > hi else v


# ----------------------------------------------------------------------------
# Regeneration, burden, marginal potential   (Sec. 3, 6)
# ----------------------------------------------------------------------------
def regen_at(g: Grid, i: int, x: float) -> float:
    """Regeneration g_i(x) at an arbitrary capacity x (Sec. 3).
       rho=0 => finite/external (no regen). Logistic by default; Allee if A_i > 0.
       Note: the Allee form is NEGATIVE for 0 < x < A_i (a source declining below its
       critical threshold), so callers must tolerate g < 0."""
    if g.rho[i] <= 0 or g.K[i] <= 0:
        return 0.0
    logistic = g.rho[i] * x * (1.0 - x / g.K[i])
    if g.A is not None and g.A[i] > 0:
        return logistic * (x / g.A[i] - 1.0)
    return logistic


def regen(g: Grid, i: int) -> float:
    """Regeneration at the cell's current capacity g.x[i]."""
    return regen_at(g, i, g.x[i])


def local_penalty(g: Grid, i: int, x: float) -> float:
    """ell_i(x) = alpha [L-x]_+^2 + beta [x-U]_+^2   (Sec. 6)."""
    deficit = max(0.0, g.L[i] - x)
    excess = max(0.0, x - g.U[i])
    return g.alpha[i] * deficit * deficit + g.beta[i] * excess * excess


def burden(g: Grid, x: list[float]) -> float:
    """Global burden B(x) = sum_i ell_i(x_i)   (Sec. 6)."""
    return sum(local_penalty(g, i, x[i]) for i in range(g.size))


def mu(g: Grid, i: int, x: float) -> float:
    """Marginal burden potential  mu_i = d ell_i / d x_i   (Sec. 6.1)."""
    if x < g.L[i]:
        return -2.0 * g.alpha[i] * (g.L[i] - x)
    if x > g.U[i]:
        return 2.0 * g.beta[i] * (x - g.U[i])
    return 0.0


# ----------------------------------------------------------------------------
# Actors   (Sec. 4, 7)
# ----------------------------------------------------------------------------
@dataclass
class Actor:
    pos: int                # current cell
    q_max: float            # max redirectable capacity per tick
    M: float = 1.0          # edge mobility / conductance
    theta: float = 0.05     # marginal transport burden along edge
    eta: float = 0.9        # transport efficiency (0..1)
    c0: float = 0.0         # fixed activation cost of a transfer


@dataclass
class Proposal:
    src: int
    dst: int
    q: float                # gross amount to pull from src (before clip)
    actor: int              # index of proposing actor
    eta: float
    c0: float


# ----------------------------------------------------------------------------
# One synchronous tick   (Sec. 12 algorithm)
# ----------------------------------------------------------------------------
@dataclass
class TickReport:
    tick: int
    B_before: float
    B_noaction: float
    B_withaction: float
    X_total: float
    n_below_L: int
    dissipated: float
    impact: float           # B_noaction - B_withaction  (Sec. 10)
    transfers: int


def natural_update(g: Grid) -> list[float]:
    """No-action counterfactual x^0(t+1)   (Sec. 2). Order: inflow, regen, demand, leakage."""
    out = []
    for i in range(g.size):
        leak = g.lam[i]
        if g.leak_frac is not None:
            leak += g.leak_frac[i] * g.x[i]      # proportional loss: bigger stocks leak more
        v = g.x[i] + g.s[i] + regen(g, i) - g.d[i] - leak
        out.append(clip(v, 0.0, g.K[i]))
    return out


def step(g: Grid, actors: list[Actor], tick: int) -> TickReport:
    B_before = burden(g, g.x)

    # (1) no-action branch + (2-4) natural update
    x0 = natural_update(g)

    # Action branch starts from the same natural update, then actors redistribute.
    xa = list(x0)

    # (5) marginal potentials on the post-natural state
    m = [mu(g, i, xa[i]) for i in range(g.size)]

    # (6-8) each actor proposes its single best feasible edge (Sec. 7.3)
    proposals: list[Proposal] = []
    for ai, a in enumerate(actors):
        i = a.pos
        best_j, best_F = None, 0.0
        for j in g.neighbors(i):
            F = m[i] - m[j] - a.theta          # driving force (Sec. 7.1)
            if F > best_F:
                best_F, best_j = F, j
        if best_j is None:                     # no positive force -> rest
            continue
        q_gross = a.M * best_F                  # linear flux rule q = M[F]_+ (Sec. 7.2)
        proposals.append(Proposal(i, best_j, q_gross, ai, a.eta, a.c0))

    # (9) conflict resolution: scale oversubscribed source outflow proportionally (Sec. 12.1)
    # cost to source = q + c0; cannot pull source below x_min.
    demand_on_src: dict[int, float] = {}
    for p in proposals:
        demand_on_src[p.src] = demand_on_src.get(p.src, 0.0) + p.q + p.c0
    scale: dict[int, float] = {}
    for src, want in demand_on_src.items():
        avail = max(0.0, xa[src] - g.x_min[src])
        scale[src] = 1.0 if want <= avail or want <= 0 else avail / want

    # (10) apply accepted transfers + transport losses (Laws 2, 3, 4)
    dissipated = 0.0
    n_transfers = 0
    for p in proposals:
        f = scale[p.src]
        q = p.q * f
        c0 = p.c0 * f
        # respect actor q_max and destination headroom
        q = min(q, actors[p.actor].q_max, max(0.0, g.K[p.dst] - xa[p.dst]))
        if q <= 0:
            continue
        pulled = q + c0
        if pulled > xa[p.src] - g.x_min[p.src] + 1e-12:
            pulled = max(0.0, xa[p.src] - g.x_min[p.src])
            q = max(0.0, pulled - c0)
        delivered = p.eta * q
        loss = (1.0 - p.eta) * q + c0          # transport loss >= 0 (Law 4)
        xa[p.src] -= (q + c0)
        xa[p.dst] += delivered
        xa[p.src] = clip(xa[p.src], 0.0, g.K[p.src])
        xa[p.dst] = clip(xa[p.dst], 0.0, g.K[p.dst])
        dissipated += loss
        n_transfers += 1

    # (11) commit action branch, recompute burden, record impact
    B_noaction = burden(g, x0)
    B_withaction = burden(g, xa)
    g.x = xa

    return TickReport(
        tick=tick,
        B_before=B_before,
        B_noaction=B_noaction,
        B_withaction=B_withaction,
        X_total=sum(xa),
        n_below_L=sum(1 for i in range(g.size) if xa[i] < g.L[i]),
        dissipated=dissipated,
        impact=B_noaction - B_withaction,      # positive => actor helped (Sec. 10)
        transfers=n_transfers,
    )


# ----------------------------------------------------------------------------
# Scenario builder + runner
# ----------------------------------------------------------------------------
def make_grid(n: int) -> Grid:
    size = n * n
    return Grid(
        n=n,
        x=[10.0] * size,
        K=[20.0] * size,
        L=[5.0] * size,
        U=[15.0] * size,
        alpha=[1.0] * size,
        beta=[0.5] * size,
        s=[0.0] * size,
        d=[1.0] * size,
        lam=[0.2] * size,
        rho=[0.0] * size,
        x_min=[0.0] * size,
    )


def run(g: Grid, actors: list[Actor], ticks: int, verbose: bool = True) -> list[TickReport]:
    reports = []
    if verbose:
        print(f"Running {g.n}x{g.n} grid, {len(actors)} actor(s), {ticks} ticks\n")
        hdr = f"{'tick':>4} {'B_before':>10} {'B_noact':>10} {'B_action':>10} " \
              f"{'impact':>9} {'X_total':>9} {'<L':>4} {'diss':>7} {'xfers':>5}"
        print(hdr)
        print("-" * len(hdr))
    for t in range(1, ticks + 1):
        rep = step(g, actors, t)
        reports.append(rep)
        if verbose:
            print(f"{rep.tick:>4} {rep.B_before:>10.3f} {rep.B_noaction:>10.3f} "
                  f"{rep.B_withaction:>10.3f} {rep.impact:>9.3f} {rep.X_total:>9.2f} "
                  f"{rep.n_below_L:>4} {rep.dissipated:>7.3f} {rep.transfers:>5}")
    return reports


if __name__ == "__main__":
    # Small grid, 5 ticks. Create a deficit/surplus imbalance so an actor has work to do.
    g = make_grid(3)                 # 3x3 = 9 cells
    # cell 0 (top-left) starts deficient; cell 8 (bottom-right) starts oversupplied
    g.x[0] = 1.0                     # below L=5  -> strong negative mu
    g.x[4] = 18.0                    # center oversupplied -> positive mu
    g.d[0] = 3.0                     # extra demand at the deficient cell

    actor = Actor(pos=4, q_max=6.0, M=0.5, theta=0.05, eta=0.9)
    run(g, [actor], ticks=5)
