"""
Energy Balance - V2.9 P1C: candidate source-level preservation controller.

P1C is a CANDIDATE PRESERVATION CONTROLLER frozen in Amendment 4 (Sec 20) of
V2.9_BEHAVIORAL_PROTOCOL_DRAFT.md and corrected by the independent Gate-2.1B
review (V2.9_OBJECTIVE_ALIGNMENT_REVIEW.md, Theorem 4.1). It wraps the frozen
exact-D0 local law of d0_v29.py with a source-level barrier-certified aggregate
export constraint and proportional multi-edge allocation.

EPISTEMIC STATUS (read before use):
  * P1C is OUTSIDE the V2.8 theorem. The V2.8 discrete descent theorem assumes
    the unconstrained D0 flux; capping the aggregate export changes the flux, so
    that theorem does NOT transfer. P1C carries its own one-step reserve-
    preservation property (Gate-2.1B Theorem 4.1), validated numerically - NOT
    proved - by test_v29_p1c.py.
  * This gate validates local physical CONFORMANCE only. It does NOT prove
    global stability, long-run sustainability, the infinite-horizon viability
    kernel, or behavioral success, and it runs no D9/D10 experiment.
  * P1C implements NO ecological debt, NO EBU, NO wallet, NO scalarisation, NO
    restoration credit, NO resource-conversion price.
  * P1C uses NO global objective, NO global V/viability/debt, and NO future
    rollout when choosing an action. A diagnostic V is computed only AFTER all
    decisions, by the researcher harness - never on the decision path.

DESIGN (Amendment 4):
  * source update      x_i^{n+1} = x_i + dt ( u_i + sum_in eta_e q_e^acc
                                              - sum_out q_e^acc )            (A4.1)
    - the source loses the FULL accepted withdrawal q_e^acc (pre-loss);
    - the destination receives only eta_e q_e^acc (post-loss).
  * raw request        q_e^req = d0_v29.edge_flux(...).J >= 0  (reused, not forked)
  * robust budget      Q_max^rob = [ (x-eps_x) + dt(u-eps_u) - R_eff ]_+ / dt (A4.5)
    (aggregate, per source; uncommitted incoming flow excluded)
  * feasibility        x + dt u >= R_eff                                     (A4.4)
  * proportional       sigma = min(1, Q_max^rob / Q_req);  q_e^acc = sigma q_e^req

This module reuses d0_v29's public substrate (Cell, Edge, World, LocalView,
natural_drive, local_view, edge_flux) and NEVER imports a test module. Standard
library only.
"""
from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import Mapping, Optional, Sequence

import d0_v29 as d0

__all__ = [
    "SourceConfig", "EdgeResult", "SourceResult", "TickResult",
    "SOURCE_TYPES", "STOCK_TYPES",
    "classify_state", "robust_budget", "p1c_step",
]

SOURCE_TYPES = ("regenerative", "finite", "irreversible", "flow")
# stock-reserve types get the P/R/I reserve classifier; "flow" is always State F
STOCK_TYPES = ("regenerative", "finite", "irreversible")


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
# Source preservation configuration (Amendment 4 Sec 20.4-20.5, 20.8)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class SourceConfig:
    """Per-source preservation configuration.

    source_type:
      regenerative  - critical regenerative stock; State P export up to the
                      robust budget, R/I export zero.
      finite        - non-regenerating stock; preservation-safe export budget is
                      ZERO (positive extraction is depletion, not preservation).
      irreversible  - irreversible capacity; safe extraction rate ZERO.
      flow          - external renewable flow (State F): a declared non-negative
                      flow cap, no regenerative-stock reserve.

    R_eff       effective regenerative reserve (stock units); required for stock
                types, must be None for flow.
    eps_x       physical stock-measurement/error margin (>= 0).
    eps_u       physical drive-rate uncertainty margin (>= 0).
    flow_cap    declared non-negative external-flow cap (rate); required for
                flow, must be None otherwise.
    num_tol     numerical (floating-point) tolerance - kept STRICTLY separate
                from the physical uncertainty margins eps_x/eps_u (Amendment 4
                Sec 20.4). It is used only for scale-aware comparisons, never as
                a physical safety margin.

    Exact-model conformance fixtures may set eps_x = eps_u = 0; this is NOT an
    empirical recommendation (Amendment 4 Sec 20.4 forbids fitting margins)."""
    source_id: int
    source_type: str
    R_eff: Optional[float] = None
    eps_x: float = 0.0
    eps_u: float = 0.0
    flow_cap: Optional[float] = None
    num_tol: float = 1e-12

    def __post_init__(self):
        if not isinstance(self.source_id, int) or isinstance(self.source_id, bool):
            raise ValueError("source_id must be an integer cell index")
        if self.source_id < 0:
            raise ValueError(f"source_id must be >= 0, got {self.source_id}")
        if self.source_type not in SOURCE_TYPES:
            raise ValueError(f"source_type must be one of {SOURCE_TYPES}, "
                             f"got {self.source_type!r}")
        _req_nonneg("eps_x", self.eps_x)
        _req_nonneg("eps_u", self.eps_u)
        _req_nonneg("num_tol", self.num_tol)
        if self.source_type == "flow":
            if self.R_eff is not None:
                raise ValueError("flow source must not declare R_eff (no stock "
                                 "reserve; use flow_cap)")
            if self.flow_cap is None:
                raise ValueError("flow source requires a declared flow_cap")
            _req_nonneg("flow_cap", self.flow_cap)
        else:  # stock types
            if self.R_eff is None:
                raise ValueError(f"{self.source_type} source requires R_eff")
            _req_finite("R_eff", self.R_eff)
            if self.flow_cap is not None:
                raise ValueError("flow_cap is only for flow sources")


# ---------------------------------------------------------------------------
# Result diagnostics (immutable; audit-complete)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class EdgeResult:
    source_id: int
    dest_id: int
    eta: float
    q_req: float          # raw loss-aware request rate (d0 edge_flux J), >= 0
    q_acc: float          # accepted withdrawal rate (source loses this, pre-loss)
    q_delivered: float    # eta * q_acc (destination receipt, post-loss)
    loss_rate: float      # (1 - eta) * q_acc


@dataclass(frozen=True)
class SourceResult:
    source_id: int
    source_type: str
    state: str                 # "P" | "R" | "I" | "F"
    R_eff: Optional[float]
    x: float
    u: float
    no_export_successor: float  # x + dt*u
    Q_req: float                # aggregate requested rate
    Q_max: float                # aggregate safe budget rate
    Q_acc: float                # aggregate accepted rate
    sigma: float                # proportional scale factor in [0, 1]
    eps_x: float
    eps_u: float
    feasible: bool              # x + dt*u >= R_eff (stock types); True for F
    reserve_boundary_ok: bool   # x_i^{n+1} >= R_eff (stock types); n/a -> True for F
    incoming_usable: float      # sum_in eta_e q_e^acc (DIAGNOSTIC ONLY; not budgeted)
    zero_export_insufficient: bool  # State I: zero export cannot save the reserve
    preservation_success_claimed: bool  # never True for R/I
    reason: str


@dataclass(frozen=True)
class TickResult:
    model: str                 # "P1C-preservation-controller"
    covered_by_v28_theorem: bool  # always False
    dt: float
    x_before: tuple
    x_after: tuple
    u: tuple
    stock_change: float        # sum(x_after) - sum(x_before)
    total_loss: float          # dt * sum (1-eta) q_acc
    ledger_residual: float
    sources: tuple             # SourceResult per configured source
    edges: tuple               # EdgeResult per edge
    # one-step preservation theorem (Gate-2.1B Thm 4.1) conformance:
    theorem_assumptions_hold: bool   # all State-P stock sources eligible this tick
    theorem_conclusion_observed: bool  # x_i^{n+1} >= R_eff for every eligible State-P source
    theorem_excluded_sources: tuple  # ids of R/I/F sources excluded from the claim


# ---------------------------------------------------------------------------
# Preservation-state classifier (Amendment 4 Sec 20.5)
# ---------------------------------------------------------------------------
def classify_state(cfg: SourceConfig, x: float, u: float, dt: float) -> str:
    """Return the Amendment-4 action-time state on the frozen (x, u):

      flow type              -> "F"
      x < R_eff              -> "R"   (recovery required; export zero)
      x + dt*u >= R_eff      -> "P"   (preservable)
      otherwise              -> "I"   (locally reserve-infeasible; export zero,
                                       zero export cannot save the boundary)

    Reads ONLY source-local data (cfg, x, u, dt)."""
    if dt <= 0.0:
        raise ValueError(f"dt must be > 0, got {dt}")
    if cfg.source_type == "flow":
        return "F"
    R = cfg.R_eff
    if x < R:
        return "R"
    if x + dt * u >= R:
        return "P"
    return "I"


# ---------------------------------------------------------------------------
# Robust aggregate export budget (Amendment 4 Sec 20.3-20.4; A4.5)
# ---------------------------------------------------------------------------
def robust_budget(cfg: SourceConfig, x: float, u: float, dt: float) -> float:
    """Aggregate source-export-RATE budget Q_max^rob for a State-P *regenerative*
    source:

        Q_max^rob = [ (x - eps_x) + dt(u - eps_u) - R_eff ]_+ / dt.

    Reads ONLY source-local data. This function assumes the caller has already
    classified the source as State P and typed it regenerative; it is exposed for
    direct numerical testing of the formula. dt must be > 0."""
    if dt <= 0.0:
        raise ValueError(f"dt must be > 0, got {dt}")
    if cfg.R_eff is None:
        raise ValueError("robust_budget requires a stock reserve R_eff")
    num = (x - cfg.eps_x) + dt * (u - cfg.eps_u) - cfg.R_eff
    return (num / dt) if num > 0.0 else 0.0


def _source_budget(cfg: SourceConfig, state: str, x: float, u: float,
                   dt: float) -> tuple[float, str]:
    """(budget_rate, reason) given the classified state and source type.

    Amendment 4 Sec 20.3/20.8:
      State P regenerative -> robust budget (A4.5)
      State P finite       -> 0 (extraction is depletion, not preservation)
      State P irreversible -> 0 (safe extraction rate is zero)
      State R / I          -> 0 (export forbidden)
      State F (flow)       -> min(flow_cap, [x + dt*u]_+ / dt), no phantom stock
    """
    if state == "F":
        avail = (x + dt * u)
        avail_rate = (avail / dt) if avail > 0.0 else 0.0
        b = min(cfg.flow_cap, avail_rate)
        return b, ("flow-cap and available-stock bound (State F): "
                   f"min(flow_cap={cfg.flow_cap:g}, avail_rate={avail_rate:g})")
    if state == "R":
        return 0.0, ("State R (recovery required): export zero even if drive "
                     "would lift the source above reserve this tick")
    if state == "I":
        return 0.0, ("State I (locally reserve-infeasible): export zero; zero "
                     "export cannot prevent the next reserve breach")
    # state == "P"
    if cfg.source_type == "regenerative":
        return robust_budget(cfg, x, u, dt), "State P regenerative: robust budget A4.5"
    if cfg.source_type == "finite":
        return 0.0, ("finite source: preservation-safe export budget is zero "
                     "(positive extraction is depletion, not preservation)")
    # irreversible
    return 0.0, ("irreversible source: safe extraction rate is zero (loss would "
                 "be irreversible debt, outside P1C preservation)")


# ---------------------------------------------------------------------------
# Synchronous P1C tick (Amendment 4 Sec 20.6; A4.1)
# ---------------------------------------------------------------------------
def p1c_step(world: d0.World, x: Sequence[float], dt: float,
             configs: Mapping[int, SourceConfig],
             s_extra: Optional[Sequence[float]] = None,
             d_extra: Optional[Sequence[float]] = None,
             diagnostics: bool = True) -> TickResult:
    """One synchronous P1C preservation tick (Amendment 4 Sec 20.6).

    Frozen order: validate+freeze state -> on-site drives (d0 semantics) ->
    local views -> raw loss-aware edge requests (d0.edge_flux) -> group by source
    -> classify -> per-source budget -> proportional scaling -> ONE simultaneous
    update -> diagnostics.

    `configs` maps a cell index to its SourceConfig; every cell that is the
    SOURCE endpoint of an edge must have a config (an unconfigured exporter would
    be unconstrained, defeating preservation). Cells that never export need no
    config.

    All decisions read only frozen local data. Global V/viability/debt and any
    future rollout are never consulted; a diagnostic V is left to the harness."""
    dt = _req_finite("dt", dt)
    if dt <= 0.0:
        raise ValueError(f"dt must be > 0, got {dt}")
    n = world.n
    xf = tuple(_req_finite(f"x[{k}]", v) for k, v in enumerate(x))
    if len(xf) != n:
        raise ValueError(f"state length {len(xf)} != number of cells {n}")
    if not isinstance(configs, Mapping):
        raise ValueError("configs must be a mapping {cell_index: SourceConfig}")
    for k, cfg in configs.items():
        if not isinstance(cfg, SourceConfig):
            raise ValueError("configs values must be SourceConfig instances")
        if cfg.source_id != k:
            raise ValueError(f"config key {k} != cfg.source_id {cfg.source_id}")
        if not (0 <= k < n):
            raise ValueError(f"config cell index {k} out of range (n={n})")

    def _extra(name, seq):
        if seq is None:
            return (0.0,) * n
        t = tuple(_req_nonneg(f"{name}[{j}]", v) for j, v in enumerate(seq))
        if len(t) != n:
            raise ValueError(f"{name} length mismatch")
        return t

    s_extra_t = _extra("s_extra", s_extra)
    d_extra_t = _extra("d_extra", d_extra)

    # --- decision path: frozen state only --------------------------------
    # (1-2) on-site drives via the frozen D0 semantics (reused, not forked)
    u = tuple(d0.natural_drive(c, xf[k], s_extra_t[k], d_extra_t[k])
              for k, c in enumerate(world.cells))
    # (3-4) local views + raw loss-aware requests via the frozen D0 local law
    views = tuple(d0.local_view(c, xf[k]) for k, c in enumerate(world.cells))
    q_req = []
    for e in world.edges:
        _f, J = d0.edge_flux(views[e.i], views[e.j], e)   # J = M[f-theta]_+ >= 0
        q_req.append(J)
    # (5) group outgoing requests by source; every exporter needs a config
    out_edges: dict[int, list[int]] = {}
    for idx, e in enumerate(world.edges):
        if q_req[idx] != 0.0 and e.i not in configs:
            raise ValueError(f"cell {e.i} exports (edge {idx}) but has no "
                             "SourceConfig; unconfigured export is forbidden")
        out_edges.setdefault(e.i, []).append(idx)
    # (6-8) per-source classify -> budget -> proportional scale (source-local)
    q_acc = [0.0] * len(world.edges)
    src_results: dict[int, SourceResult] = {}
    for k, cfg in configs.items():
        edge_ids = out_edges.get(k, [])
        Q_req = math.fsum(q_req[idx] for idx in edge_ids)
        state = classify_state(cfg, xf[k], u[k], dt)
        Q_max, reason = _source_budget(cfg, state, xf[k], u[k], dt)
        if Q_req > 0.0 and Q_max > 0.0:
            sigma = min(1.0, Q_max / Q_req)
        else:
            sigma = 0.0
        for idx in edge_ids:
            q_acc[idx] = sigma * q_req[idx]
        Q_acc = math.fsum(q_acc[idx] for idx in edge_ids)
        feasible = (state != "I") if cfg.source_type != "flow" else True
        src_results[k] = SourceResult(
            source_id=k, source_type=cfg.source_type, state=state,
            R_eff=cfg.R_eff, x=xf[k], u=u[k],
            no_export_successor=xf[k] + dt * u[k],
            Q_req=Q_req, Q_max=Q_max, Q_acc=Q_acc, sigma=sigma,
            eps_x=cfg.eps_x, eps_u=cfg.eps_u, feasible=feasible,
            reserve_boundary_ok=False,   # filled after the update below
            incoming_usable=0.0,         # filled after the update below
            zero_export_insufficient=(state == "I"),
            preservation_success_claimed=(state == "P"),
            reason=reason)
    # (9) ONE simultaneous update: x_i^{n+1} = x_i + dt(u_i + sum_in eta q_acc
    #                                                  - sum_out q_acc)
    contrib = [[] for _ in range(n)]
    for idx, e in enumerate(world.edges):
        qa = q_acc[idx]
        if qa != 0.0:
            contrib[e.i].append(-qa)
            contrib[e.j].append(e.eta * qa)
    sj = tuple(math.fsum(parts) for parts in contrib)
    xn = tuple(xf[k] + dt * (u[k] + sj[k]) for k in range(n))
    # --- end of decision path; everything below is diagnostics -----------

    if not diagnostics:
        # still finalize the reserve-boundary observation for eligible sources
        pass

    # per-cell certified incoming usable rate (DIAGNOSTIC; never budgeted)
    incoming = [0.0] * n
    for idx, e in enumerate(world.edges):
        if q_acc[idx] != 0.0:
            incoming[e.j] = incoming[e.j] + e.eta * q_acc[idx]

    edge_results = tuple(
        EdgeResult(source_id=e.i, dest_id=e.j, eta=e.eta,
                   q_req=q_req[idx], q_acc=q_acc[idx],
                   q_delivered=e.eta * q_acc[idx],
                   loss_rate=(1.0 - e.eta) * q_acc[idx])
        for idx, e in enumerate(world.edges))

    # finalize per-source reserve-boundary observation + incoming diagnostic
    finalized = {}
    for k, sr in src_results.items():
        ok = True
        if sr.source_type != "flow":
            ok = xn[k] >= sr.R_eff - configs[k].num_tol * (1.0 + abs(sr.R_eff))
        finalized[k] = _replace_source(sr, reserve_boundary_ok=ok,
                                        incoming_usable=incoming[k])

    # one-step preservation theorem (Gate-2.1B Thm 4.1) conformance summary:
    # eligible = State-P STOCK sources (the theorem object); R/I/F excluded.
    eligible = [k for k, sr in finalized.items()
                if sr.state == "P" and sr.source_type in STOCK_TYPES]
    excluded = tuple(sorted(k for k, sr in finalized.items()
                            if not (sr.state == "P" and sr.source_type in STOCK_TYPES)))
    concl = all(finalized[k].reserve_boundary_ok for k in eligible)

    total_loss = dt * math.fsum((1.0 - e.eta) * q_acc[idx]
                                for idx, e in enumerate(world.edges))
    stock_change = math.fsum(xn) - math.fsum(xf)
    ledger_rhs = dt * math.fsum(u) - total_loss
    ledger_res = stock_change - ledger_rhs

    return TickResult(
        model="P1C-preservation-controller", covered_by_v28_theorem=False,
        dt=dt, x_before=xf, x_after=xn, u=u,
        stock_change=stock_change, total_loss=total_loss,
        ledger_residual=ledger_res,
        sources=tuple(finalized[k] for k in sorted(finalized)),
        edges=edge_results,
        theorem_assumptions_hold=len(eligible) > 0,
        theorem_conclusion_observed=concl,
        theorem_excluded_sources=excluded)


def _replace_source(sr: SourceResult, **kw) -> SourceResult:
    from dataclasses import replace
    return replace(sr, **kw)
