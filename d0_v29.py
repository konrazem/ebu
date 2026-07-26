"""
Energy Balance - V2.9 Stage-A engine: the exact synchronous local D0 law.

Implements Model D0 of Foundation_v2.8_discrete_draft.md (Def 3.2), per the
preregistered V2.9_BEHAVIORAL_PROTOCOL_DRAFT.md (incl. Pre-implementation
Amendment 1):

    x^{n+1} = x^n + dt * ( u(x^n) + S J(x^n) )
    f_e = mu_i - eta_e * mu_j          (loss-aware force, Def 2.3)
    J_e = M_e * [ f_e - theta_e ]_+    (Onsager flux)

Design constraints enforced here:
  * ALL marginals and fluxes are computed from ONE frozen state; exactly one
    synchronous update is applied.
  * Exact D0 (P1) is UNCONSTRAINED: no clipping, no spill, no conflict scaling,
    no sequential live-state application, no line search, no EBU. Negative or
    over-capacity results are permitted and only *flagged* by diagnostics.
  * The local decision function (`edge_flux`) accepts ONLY two LocalView objects
    and one Edge - never the world, the full state vector, global V, or any
    evaluation metric. Global V exists ONLY as a researcher diagnostic computed
    AFTER all decisions.
  * P1K is a separate diagnostic *bounded wrapper* (Amendment 1 Sec 17.2):
    project the raw D0 proposal to [0, K_i], recording lower-bound shortfall and
    spill exactly. P1K is OUTSIDE the V2.8 theorem; clipping is never silent.
  * This is a NEW engine: it does not import energy_balance or any ebu_v2x
    module, and it must never import test modules.

Standard library only. This module makes no behavioral claim; conformance is
validated (not proved) by test_v29.py.
"""
from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Optional, Sequence

__all__ = [
    "Cell", "Edge", "World", "LocalView", "StepResult", "P1KResult",
    "penalty", "marginal", "cell_curvature_sup", "lv_exact", "lv_safe",
    "natural_drive", "local_view", "edge_flux", "d0_step", "p1k_step",
    "V_total", "gershgorin_dt_certificate", "one_edge_dt_certificate",
]

_SOURCE_KINDS = ("none", "finite", "logistic", "allee")


def _req_finite(name: str, v) -> float:
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        raise ValueError(f"{name} must be a finite real number, got {v!r}")
    v = float(v)
    if not math.isfinite(v):
        raise ValueError(f"{name} must be finite, got {v!r}")
    return v


def _req_nonneg(name: str, v) -> float:
    v = _req_finite(name, v)
    if v < 0.0:
        raise ValueError(f"{name} must be >= 0, got {v}")
    return v


# ---------------------------------------------------------------------------
# Data model (immutable, validated on construction)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Cell:
    """Per-cell penalty, physical-capacity, and local natural-drive parameters.

    K is the declared physical capacity: the P1K projection interval is [0, K]
    and K is also the carrying capacity of logistic/Allee regeneration. Exact
    D0 (P1) never enforces it."""
    alpha: float
    beta: float
    chi: float
    L: float
    U: float
    R: float
    K: float
    s: float = 0.0        # declared external inflow
    d: float = 0.0        # demand
    lam: float = 0.0      # constant leak
    kappa: float = 0.0    # proportional leak
    source: str = "none"  # none | finite | logistic | allee
    rho: float = 0.0      # regeneration rate
    A: float = 0.0        # Allee threshold (used when source == "allee")

    def __post_init__(self):
        _req_nonneg("alpha", self.alpha)
        _req_nonneg("beta", self.beta)
        _req_nonneg("chi", self.chi)
        _req_finite("L", self.L)
        _req_finite("U", self.U)
        _req_finite("R", self.R)
        if self.L > self.U:
            raise ValueError(f"L must be <= U, got L={self.L}, U={self.U}")
        K = _req_finite("K", self.K)
        if K <= 0.0:
            raise ValueError(f"K must be > 0 (declared physical capacity), got {K}")
        _req_finite("s", self.s)
        _req_nonneg("d", self.d)
        _req_nonneg("lam", self.lam)
        _req_nonneg("kappa", self.kappa)
        _req_nonneg("rho", self.rho)
        _req_nonneg("A", self.A)
        if self.source not in _SOURCE_KINDS:
            raise ValueError(f"source must be one of {_SOURCE_KINDS}, got {self.source!r}")
        if self.source == "allee" and self.A <= 0.0:
            raise ValueError("allee source requires A > 0")


@dataclass(frozen=True)
class Edge:
    """Directed lossy transport opportunity i -> j (V2.8 Def 2.2)."""
    i: int
    j: int
    M: float
    theta: float
    eta: float

    def __post_init__(self):
        if not isinstance(self.i, int) or not isinstance(self.j, int):
            raise ValueError("edge endpoints must be integer cell indices")
        if self.i == self.j:
            raise ValueError(f"self-edge not allowed: ({self.i}, {self.j})")
        M = _req_finite("M", self.M)
        if M <= 0.0:
            raise ValueError(f"M must be > 0, got {M}")
        _req_nonneg("theta", self.theta)
        eta = _req_finite("eta", self.eta)
        if not (0.0 <= eta <= 1.0):
            raise ValueError(f"eta must be in [0, 1], got {eta}")


@dataclass(frozen=True)
class World:
    """Topology + parameters. State lives outside (a plain sequence of floats)."""
    cells: tuple
    edges: tuple

    def __post_init__(self):
        cells = tuple(self.cells)
        edges = tuple(self.edges)
        object.__setattr__(self, "cells", cells)
        object.__setattr__(self, "edges", edges)
        n = len(cells)
        if n == 0:
            raise ValueError("world needs at least one cell")
        for c in cells:
            if not isinstance(c, Cell):
                raise ValueError("cells must be Cell instances")
        for e in edges:
            if not isinstance(e, Edge):
                raise ValueError("edges must be Edge instances")
            if not (0 <= e.i < n and 0 <= e.j < n):
                raise ValueError(f"edge ({e.i},{e.j}) references invalid cell index (n={n})")

    @property
    def n(self) -> int:
        return len(self.cells)


@dataclass(frozen=True)
class LocalView:
    """The ONLY state a local decision may see for one endpoint: that cell's
    state plus its declared local parameters (V2.9 protocol Sec 4.1)."""
    x: float
    alpha: float
    beta: float
    chi: float
    L: float
    U: float
    R: float
    K: float   # declared local capacity (headroom information is allowed)


# ---------------------------------------------------------------------------
# Field functional (independent implementation; V2.8 Def 2.1 / Assumption 2.5)
# ---------------------------------------------------------------------------
def penalty(alpha: float, beta: float, chi: float,
            L: float, U: float, R: float, x: float) -> float:
    """v_i(x) = alpha [L-x]_+^2 + beta [x-U]_+^2 + chi [R-x]_+^2."""
    dv = L - x if x < L else 0.0
    ev = x - U if x > U else 0.0
    rv = R - x if x < R else 0.0
    return alpha * dv * dv + beta * ev * ev + chi * rv * rv


def marginal(alpha: float, beta: float, chi: float,
             L: float, U: float, R: float, x: float) -> float:
    """mu_i = -2a[L-x]_+ + 2b[x-U]_+ - 2chi[R-x]_+  (branchwise, continuous)."""
    m = 0.0
    if x < L:
        m += -2.0 * alpha * (L - x)
    if x > U:
        m += 2.0 * beta * (x - U)
    if x < R:
        m += -2.0 * chi * (R - x)
    return m


def _view_penalty(v: LocalView) -> float:
    return penalty(v.alpha, v.beta, v.chi, v.L, v.U, v.R, v.x)


def _view_marginal(v: LocalView) -> float:
    return marginal(v.alpha, v.beta, v.chi, v.L, v.U, v.R, v.x)


def cell_curvature_sup(c: Cell) -> float:
    """Exact branchwise sup of v'' = 2[a 1_{x<L} + b 1_{x>U} + chi 1_{x<R}]:
    the CORRECTED constant sums simultaneously active weights (V2.8 Asm 2.5)."""
    bps = sorted({c.L, c.U, c.R})
    reps = [bps[0] - 1.0]
    reps += [(a + b) / 2.0 for a, b in zip(bps, bps[1:]) if b > a]
    reps += [bps[-1] + 1.0]
    return max(2.0 * (c.alpha * (p < c.L) + c.beta * (p > c.U) + c.chi * (p < c.R))
               for p in reps)


def lv_exact(world: World) -> float:
    """Exact global Lipschitz constant of grad V (diagnostic / designer tool)."""
    return max(cell_curvature_sup(c) for c in world.cells)


def lv_safe(world: World) -> float:
    """Safe upper bound  L_V <= 2 max_i [max(alpha_i, beta_i) + chi_i]."""
    return 2.0 * max(max(c.alpha, c.beta) + c.chi for c in world.cells)


def V_total(world: World, x: Sequence[float]) -> float:
    """Global state functional. RESEARCHER DIAGNOSTIC ONLY: never called on the
    decision path (enforced by test_v29.py group 9)."""
    return math.fsum(penalty(c.alpha, c.beta, c.chi, c.L, c.U, c.R, xi)
                     for c, xi in zip(world.cells, x))


# ---------------------------------------------------------------------------
# Local natural drive (V2.8 Def 2.4; on-site only)
# ---------------------------------------------------------------------------
def _regen(c: Cell, x: float) -> float:
    """g_i(x): 0 for none/finite; logistic rho x (1 - x/K); Allee-signed variant.
    Negative Allee values below threshold are physical and NOT clipped."""
    if c.source in ("none", "finite") or c.rho <= 0.0:
        return 0.0
    logistic = c.rho * x * (1.0 - x / c.K)
    if c.source == "allee":
        return logistic * (x / c.A - 1.0)
    return logistic


def natural_drive(c: Cell, x: float, s_extra: float = 0.0) -> float:
    """u_i = s_i + s_extra + g_i(x_i) - d_i - lam_i - kappa_i x_i.
    Local: reads only this cell's state, its declared parameters, and the
    declared tick-dependent external input s_extra. Never clipped."""
    x = _req_finite("x", x)
    s_extra = _req_finite("s_extra", s_extra)
    return c.s + s_extra + _regen(c, x) - c.d - c.lam - c.kappa * x


# ---------------------------------------------------------------------------
# Strict local decision API (V2.9 protocol Sec 4; V2.8 Def 2.3)
# ---------------------------------------------------------------------------
def local_view(c: Cell, x: float) -> LocalView:
    return LocalView(x=_req_finite("x", x), alpha=c.alpha, beta=c.beta, chi=c.chi,
                     L=c.L, U=c.U, R=c.R, K=c.K)


def edge_flux(src: LocalView, dst: LocalView, e: Edge):
    """The local law. Accepts ONLY (source view, destination view, edge spec).

    Returns (f_e, J_e) with f_e = mu_i - eta_e mu_j and J_e = M_e [f_e-theta]_+.
    No rollout, no lookahead, no global optimisation, no global V."""
    if not isinstance(src, LocalView) or not isinstance(dst, LocalView):
        raise TypeError("edge_flux accepts LocalView endpoints only - "
                        "never a world, grid, or full state vector")
    if not isinstance(e, Edge):
        raise TypeError("edge_flux requires an Edge specification")
    mu_i = _view_marginal(src)
    mu_j = _view_marginal(dst)
    f = mu_i - e.eta * mu_j
    excess = f - e.theta
    J = e.M * excess if excess > 0.0 else 0.0
    return f, J


# ---------------------------------------------------------------------------
# Exact P1 / D0 synchronous step
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class StepResult:
    """Diagnostics for one exact D0 tick. All decision quantities were computed
    from the frozen input state; global quantities (V, bound terms) were
    computed AFTER the update and never fed back into decisions."""
    model: str                       # "P1-exact-D0"
    covered_by_v28_theorem: bool     # True for P1 under its assumptions
    x_before: tuple
    x_after: tuple
    dt: float
    u: tuple
    mu: tuple
    f: tuple                         # per-edge loss-aware force
    J: tuple                         # per-edge Onsager flux
    sj: tuple                        # (S J)_i per cell
    transport_loss: float            # dt * sum (1-eta_e) J_e
    ledger_residual: Optional[float]
    V_before: Optional[float]
    V_after: Optional[float]
    drive_term: Optional[float]      # dt * mu . u
    dissipation: Optional[float]     # dt * sum(J^2/M + theta J)
    remainder_bound: Optional[float] # (L_V dt^2 / 2) ||u + SJ||^2
    inequality_residual: Optional[float]  # dV - (drive - dissipation + R_n); <= 0 expected
    lv_used: Optional[float]
    out_of_range_cells: tuple        # indices with x_after < 0 or > K (FLAGGED, never changed)


def d0_step(world: World, x: Sequence[float], dt: float,
            s_extra: Optional[Sequence[float]] = None,
            diagnostics: bool = True) -> StepResult:
    """One exact synchronous D0 tick (V2.8 Def 3.2).

    Sequence: freeze state -> local drives -> local views -> per-edge fluxes ->
    accumulate all lossy contributions -> ONE synchronous update. Unconstrained:
    no clipping, no conflict scaling, no sequential application, no accept gate.

    Per-cell transport contributions are summed with math.fsum, so the result is
    invariant to edge enumeration order (fsum is a correctly rounded sum)."""
    dt = _req_finite("dt", dt)
    if dt <= 0.0:
        raise ValueError(f"dt must be > 0, got {dt}")
    n = world.n
    xf = tuple(_req_finite(f"x[{k}]", v) for k, v in enumerate(x))   # frozen state
    if len(xf) != n:
        raise ValueError(f"state length {len(xf)} != number of cells {n}")
    if s_extra is None:
        s_extra_t = (0.0,) * n
    else:
        s_extra_t = tuple(_req_finite(f"s_extra[{k}]", v) for k, v in enumerate(s_extra))
        if len(s_extra_t) != n:
            raise ValueError("s_extra length mismatch")

    # --- decision path: frozen state only -------------------------------
    u = tuple(natural_drive(c, xf[k], s_extra_t[k]) for k, c in enumerate(world.cells))
    views = tuple(local_view(c, xf[k]) for k, c in enumerate(world.cells))
    f_list, J_list = [], []
    contrib = [[] for _ in range(n)]           # per-cell lossy contributions
    for e in world.edges:
        fe, Je = edge_flux(views[e.i], views[e.j], e)
        f_list.append(fe)
        J_list.append(Je)
        if Je != 0.0:
            contrib[e.i].append(-Je)
            contrib[e.j].append(e.eta * Je)
    sj = tuple(math.fsum(parts) for parts in contrib)
    xn = tuple(xf[k] + dt * (u[k] + sj[k]) for k in range(n))
    # --- end of decision path; everything below is diagnostics ----------

    loss = dt * math.fsum((1.0 - e.eta) * Je for e, Je in zip(world.edges, J_list))
    flagged = tuple(k for k in range(n)
                    if xn[k] < 0.0 or xn[k] > world.cells[k].K)

    if not diagnostics:
        return StepResult(
            model="P1-exact-D0", covered_by_v28_theorem=True,
            x_before=xf, x_after=xn, dt=dt, u=u,
            mu=tuple(_view_marginal(v) for v in views),
            f=tuple(f_list), J=tuple(J_list), sj=sj,
            transport_loss=loss, ledger_residual=None,
            V_before=None, V_after=None, drive_term=None, dissipation=None,
            remainder_bound=None, inequality_residual=None, lv_used=None,
            out_of_range_cells=flagged)

    mu = tuple(_view_marginal(v) for v in views)
    ledger_res = (math.fsum(xn) - math.fsum(xf)) - dt * (math.fsum(u) - loss / dt)
    v_before = V_total(world, xf)
    v_after = V_total(world, xn)
    drive = dt * math.fsum(m * uu for m, uu in zip(mu, u))
    diss = dt * math.fsum(Je * Je / e.M + e.theta * Je
                          for e, Je in zip(world.edges, J_list))
    lv = lv_exact(world)
    rn = 0.5 * lv * dt * dt * math.fsum((uu + ss) ** 2 for uu, ss in zip(u, sj))
    ineq = (v_after - v_before) - (drive - diss + rn)
    return StepResult(
        model="P1-exact-D0", covered_by_v28_theorem=True,
        x_before=xf, x_after=xn, dt=dt, u=u, mu=mu,
        f=tuple(f_list), J=tuple(J_list), sj=sj,
        transport_loss=loss, ledger_residual=ledger_res,
        V_before=v_before, V_after=v_after, drive_term=drive, dissipation=diss,
        remainder_bound=rn, inequality_residual=ineq, lv_used=lv,
        out_of_range_cells=flagged)


# ---------------------------------------------------------------------------
# P1K - bounded diagnostic wrapper (Amendment 1 Sec 17.2). OUTSIDE the theorem.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class P1KResult:
    """Bounded-wrapper diagnostics. The V2.8 descent inequality is NOT claimed
    for this model; clipping is never silent (shortfall/spill are exact)."""
    model: str                       # "P1K-bounded-wrapper"
    covered_by_v28_theorem: bool     # always False
    raw: StepResult                  # the unchanged exact D0 proposal
    x_after: tuple                   # projected to [0, K_i]
    shortfall: tuple                 # [-y_i]_+ per cell (lower-bound shortfall)
    spill: tuple                     # [y_i - K_i]_+ per cell
    ledger_residual: float           # P1K ledger identity residual


def p1k_step(world: World, x: Sequence[float], dt: float,
             s_extra: Optional[Sequence[float]] = None,
             diagnostics: bool = True) -> P1KResult:
    """Diagnostic physical wrapper: exact raw D0 proposal first (flux decisions
    unchanged), then per-cell projection to [0, K_i] with exact accounting:

        x'_i = min(K_i, max(0, y_i)) = y_i + shortfall_i - spill_i

    Ledger (Amendment 1 Sec 17.2):
        sum(x' - x) = dt [sum u - sum (1-eta) J] + sum shortfall - sum spill
    """
    raw = d0_step(world, x, dt, s_extra=s_extra, diagnostics=diagnostics)
    shortfall, spill, xb = [], [], []
    for k, c in enumerate(world.cells):
        y = raw.x_after[k]
        lo = -y if y < 0.0 else 0.0
        hi = y - c.K if y > c.K else 0.0
        shortfall.append(lo)
        spill.append(hi)
        xb.append(y + lo - hi)
    lhs = math.fsum(xb) - math.fsum(raw.x_before)
    rhs = (dt * math.fsum(raw.u) - raw.transport_loss
           + math.fsum(shortfall) - math.fsum(spill))
    return P1KResult(
        model="P1K-bounded-wrapper", covered_by_v28_theorem=False,
        raw=raw, x_after=tuple(xb),
        shortfall=tuple(shortfall), spill=tuple(spill),
        ledger_residual=lhs - rhs)


# ---------------------------------------------------------------------------
# Timestep certificates - EXPERIMENT-DESIGNER / PROOF TOOLS, not actor knowledge.
# Configuration is computed once per world by the harness; the local law never
# calls these. No eigensolver is duplicated here (the guarded solver lives with
# the V2.8 validation suite); this is the conservative local certificate of
# V2.8 Remark 5.4 plus the one-edge bound of Theorem 5.1.
# ---------------------------------------------------------------------------
def gershgorin_dt_certificate(world: World, lv: Optional[float] = None) -> float:
    """Conservative sufficient dt from the degree-weighted Gershgorin bound:
       dt <= 2 / ( L_V * max_e M_e [ (1+eta_e^2) + sum_{e'!=e} |S_e . S_e'| ] ).
    Designer-side configuration; guarantees undriven per-step non-increase."""
    if not world.edges:
        raise ValueError("certificate undefined for a world with no edges")
    if lv is None:
        lv = lv_exact(world)
    lv = _req_finite("lv", lv)
    if lv <= 0.0:
        raise ValueError("L_V must be > 0 for a finite certificate")
    n = world.n
    cols = []
    for e in world.edges:
        col = [0.0] * n
        col[e.i] += -1.0
        col[e.j] += e.eta
        cols.append(col)
    E = len(cols)
    worst = 0.0
    for a in range(E):
        row = math.fsum(abs(math.fsum(ca * cb for ca, cb in zip(cols[a], cols[b])))
                        for b in range(E) if b != a)
        diag = 1.0 + world.edges[a].eta ** 2
        worst = max(worst, world.edges[a].M * (diag + row))
    return 2.0 / (lv * worst)


def one_edge_dt_certificate(e: Edge, lv: float) -> float:
    """dt <= 2 / (L_V M_e (1 + eta_e^2))  (V2.8 Theorem 5.1). Designer tool."""
    lv = _req_finite("lv", lv)
    if lv <= 0.0:
        raise ValueError("L_V must be > 0")
    return 2.0 / (lv * e.M * (1.0 + e.eta ** 2))
