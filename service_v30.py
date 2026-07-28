"""
Energy Balance - V3.0 Gate 1D: bounded physical service wrapper and the four
registered capability-matched arms.

Implements exactly the study locked in v30_service_alignment_plan.json
(canonical SHA-256 71c706021d738330d5382fec5056ea5228abac61aba0738b00a9a8e75edc1020).

BOUNDED SERVICE (plan section bounded_service_semantics). Registered order:
  1 freeze the physical state
  2 on-site external input and regeneration      (demand is NOT a drive term)
  3 local transport requests
  4 P1C source preservation budgets
  5 apply accepted transport simultaneously
  6 physically available destination stock (post-loss)
  7 serve demand only up to available stock
  8 record unmet demand explicitly
  9 leave every stock non-negative
 10 global metrics only after local decisions and updates

    available_i = x_i + dt*(u_i + sum_in eta q_acc - sum_out q_acc)  [+ corr_i]
    service_i   = min(dt*demand_i, available_i)
    unmet_i     = dt*demand_i - service_i
    x_i'        = available_i - service_i  >= 0

Demand moves from the drive term into the saturating service step. That IS the
registered bounded semantics (steps 2 and 7 above): it is why no consumer can
consume stock that does not physically exist. Every registered world places
demand on non-exporting consumer cells (except W3's relay, which has d = 0), so
the P1C budget of every exporting cell is computed on identical data either way
- asserted in test_v30_service.py.

EPISTEMIC STATUS
  * This wrapper is OUTSIDE the V2.8 D0 theorem (V2.8 section 11 excludes
    saturation and projection). A passing test is numerical validation, NEVER
    proof. Open problem O13 records the missing constrained/saturated theorem.
  * d0_v29 (local physics), p1c_v29 (preservation allocation) and
    ebu_quote_v30 (exact signed quote) are reused UNMODIFIED. No equation of
    theirs is forked: the P1C safe-export budget, the exact quote equation, the
    local penalty functions, the regeneration laws, transport efficiency and
    the reserve semantics are all consumed as released.
  * No needs, health, death, wallets, prices, transfers, personal debt,
    markets or learning exist here. Cumulative signed EBU is an EVALUATION
    variable of this gate.
  * tau = 0, eps_x = eps_u = 0, exact deterministic local observations, no
    sensor noise. NO real-world latency or robustness claim is made.

Standard library only; never imports a test module.
"""
from __future__ import annotations
import math
from dataclasses import dataclass, field, replace
from typing import Mapping, Optional, Sequence

import d0_v29 as d0
import p1c_v29 as p1c
import ebu_quote_v30 as eq

__all__ = [
    "DERIVED_SEMANTICS", "DT_CONSERVATIVE", "DT_NEAR", "QUANTS", "LAM_L",
    "RUN_TICKS", "BURN_IN_TICKS", "PERSISTENCE_WINDOW", "TOL_REL",
    "EBU_THRESHOLD", "SERVICE_REL", "SERVICE_ABS", "UNMET_REL", "UNMET_ABS",
    "DELTA_R", "ARMS", "WORLDS", "build_world", "world_certificate",
    "bounded_step", "TickOutcome", "RunResult", "run_arm",
    "service_alignment_predicate", "reserve_harm_predicate", "classify_outcome",
    "materially_below_reserve", "reserve_crossing",
]

# ---------------------------------------------------------------------------
# registered constants (plan) and inherited constants (locked Gate-1 plan)
# ---------------------------------------------------------------------------
DT_CONSERVATIVE = 0.1845018450184502     # plan timestep.registered_conservative_dt
DT_NEAR = 0.3321033210332103             # plan timestep.registered_near_certificate_dt
RUN_TICKS = 200                          # plan experiment_size.run_length_ticks
BURN_IN_TICKS = 50                       # plan experiment_size.burn_in_ticks
PERSISTENCE_WINDOW = 20                  # plan persistence_window_ticks
EBU_THRESHOLD = 1.0                      # plan ebu_threshold_burden_units
SERVICE_REL, SERVICE_ABS = 0.05, 1.0     # plan service_*_threshold
UNMET_REL, UNMET_ABS = 0.05, 1.0         # plan unmet_*_threshold
DELTA_R = 0.5                            # plan preservation_justification_rule
EPS_X = EPS_U = 0.0                      # plan error_types.primary_study_freeze
TAU = 0.0
DOMAIN_TOL = 1e-9


def tol(value: float) -> float:
    """Registered tolerance 1e-9 * (1 + |value|)."""
    return 1e-9 * (1.0 + abs(value))


TOL_REL = 1e-9


# Gate 1D-A shared reserve diagnostic (diagnostic layer ONLY: never used for
# physical updates, P1C budgets, accepted quantities, quotes, service, unmet
# demand, ledgers, Allee/dead-source thresholds, or certificates).
def materially_below_reserve(x: float, R_eff: float) -> bool:
    """x is below R_eff by MORE than the registered tolerance tol(R_eff).

    Boundary semantics: x == R_eff, a one-ULP residual, any residual smaller
    than tol(R_eff), and x == R_eff - tol(R_eff) are all NOT below (strict
    comparison); only x < R_eff - tol(R_eff) is materially below.
    """
    return x < R_eff - tol(R_eff)


def reserve_crossing(x_before: float, x_after: float, R_eff: float) -> bool:
    """Downward reserve crossing: previous state not materially below AND
    current state materially below. Sub-tolerance residuals never count and
    never accumulate; persistence below reserve counts one crossing at the
    material descent, as before."""
    return (not materially_below_reserve(x_before, R_eff)
            and materially_below_reserve(x_after, R_eff))

# Inherited from the LOCKED Gate-1 quote plan
# (a1916e8ecf366cee93a5284a0d8fcb68a3e1a429f49ce62b9f5914df87f94061), because
# the Gate-1D plan registers the action menu and process cost only as
# EQUALITIES across arms B/C/D, not numerically. Nothing is chosen freely.
QUANTS = (0.5, 1.0)      # Gate-1 plan Q22 spec "QUANTS=[0.5,1.0]"
LAM_L = 0.1              # Gate-1 plan fixture_conventions.default_cost.lam_L
C0 = 0.0                 # Gate-1 plan fixture_conventions.default_cost.c0
RELAY_FLOW_CAP = 1.0e6   # see DERIVED_SEMANTICS["relay_p1c_type"]

ARMS = ("A_full_p1c", "B_restricted_p1c", "C_restricted_p1c_quote",
        "D_restricted_quote_greedy")

DERIVED_SEMANTICS = {
    "action_menu": {
        "value": "QUANTS = (0.5, 1.0) applied to the D0 raw flux J of each own "
                 "out-edge; q_req = frac * J; identical for arms B, C and D",
        "provenance": "inherited from the LOCKED Gate-1 plan Q22 spec; the "
                      "Gate-1D plan registers menu EQUALITY across B/C/D but "
                      "not its numeric content",
    },
    "process_cost": {
        "value": "C_a(q) = c0 + c1*q with c0 = 0.0 and c1 = LAM_L*dt*(1-eta), "
                 "LAM_L = 0.1; category unrepresented_action_process_burden; "
                 "identical for arms C and D",
        "provenance": "inherited from the LOCKED Gate-1 plan "
                      "fixture_conventions.default_cost; category-2 process "
                      "burden per foundation Def 6.4 (no double count)",
    },
    "arm_B_selection": {
        "value": "physical rule only: among the shared menu pick the largest "
                 "loss-aware force f_e = mu_i - eta*mu_j, tie-broken by the "
                 "largest accepted quantity. No EBU is consulted.",
        "provenance": "the released engines' documented convention that an "
                      "actor proposes only its single steepest out-edge "
                      "(V2.9 protocol section 14); f_e is the V2.8 Def 2.3 force",
    },
    "arm_D_selection": {
        "value": "among the SAME menu pick the largest exact committed quote "
                 "de(q_acc); rest if the best quote is not strictly positive "
                 "(the actor's accept/reject/redesign right, foundation section 5 event 6)",
        "provenance": "plan arms.D_restricted_quote_greedy",
    },
    "relay_p1c_type": {
        "value": "the W3 relay (a non-regenerating pass-through buffer) is "
                 "typed P1C 'flow' (State F) with a declared non-binding "
                 f"flow_cap = {RELAY_FLOW_CAP:g}; the binding constraint is "
                 "its own available stock via P1C's State-F rule "
                 "min(flow_cap, [x + dt*u]_+ / dt)",
        "provenance": "REQUIRED by the plan's own registered W3 feasibility "
                      "('two-hop delivery eta^2*g_max = 2.43 > 1.0 => "
                      "feasible'): P1C gives a 'finite' stock a ZERO export "
                      "budget, which would make that registered feasibility "
                      "false and W3 vacuous. Not chosen for convenience.",
    },
    "demand_placement": {
        "value": "demand is the saturating service step (registered step 7), "
                 "not a drive term; the drive is computed from a cell copy "
                 "with d = 0 via the released d0.natural_drive",
        "provenance": "plan bounded_service_semantics.update_order steps 2 and 7",
    },
    "predicate_operationalization": {
        "value": "magnitude thresholds (5% relative, 1.0 absolute) are applied "
                 "to POST-BURN-IN CUMULATIVE delivered service / unmet demand; "
                 "the persistence rule is applied to the PER-TICK direction "
                 "over the final 20-tick window",
        "provenance": "the plan sets magnitudes and a per-tick persistence "
                      "rule; a 1.0-absolute threshold evaluated per tick would "
                      "be unreachable at the registered dt (per-tick service "
                      "is O(dt)) and would make the predicate vacuous. Both "
                      "readings are reported: the strict per-tick-magnitude "
                      "variant is recorded as "
                      "service_deficit_per_tick_magnitude_variant.",
        "decided": "before implementation and before any run",
    },
}

# ---------------------------------------------------------------------------
# registered worlds (every parameter verbatim from the plan)
# ---------------------------------------------------------------------------
_CD = dict(alpha=1.0, beta=0.5, chi=0.0, L=5.0, U=15.0, R=0.0, K=20.0)


def _cell(**kw):
    base = dict(_CD)
    base.update(kw)
    return d0.Cell(**base)


def _edge(i, j, eta, M=0.5, theta=0.05):
    return d0.Edge(i=i, j=j, M=M, theta=theta, eta=eta)


#   name -> (cells, edges, x0, demand_base, p1c_types, shock)
# demand_base: per-cell demand RATE (stock/time); shock: (tick, cell, extra)
WORLDS = {
    "W1_feasible_2cell": dict(
        cells=[_cell(source="logistic", rho=0.6, chi=1.0, R=8.0), _cell()],
        edges=[_edge(0, 1, 0.9)], x0=(15.0, 10.0), demand=(0.0, 1.0),
        types={0: "regenerative"}, shock=None,
        feasible=True,
        note="eta*g_max = 2.7 > d = 1.0 => safe delivery feasible"),
    "W2_infeasible_2cell": dict(
        cells=[_cell(source="logistic", rho=0.6, chi=1.0, R=8.0), _cell()],
        edges=[_edge(0, 1, 0.9)], x0=(15.0, 10.0), demand=(0.0, 4.0),
        types={0: "regenerative"}, shock=None,
        feasible=False,
        note="d = 4.0 > g_max = 3.0 and > eta*g_max = 2.7 => infeasible"),
    "W3_relay_3cell": dict(
        cells=[_cell(source="logistic", rho=0.6, chi=1.0, R=8.0), _cell(),
               _cell()],
        edges=[_edge(0, 1, 0.9), _edge(1, 2, 0.9)], x0=(15.0, 10.0, 10.0),
        demand=(0.0, 0.0, 1.0), types={0: "regenerative", 1: "flow"},
        shock=None, feasible=True,
        note="eta^2*g_max = 2.43 > 1.0 => feasible; binding certificate world"),
    "W4_allee_reserve_stress": dict(
        cells=[_cell(source="allee", rho=0.6, A=5.0, chi=1.0, R=11.0), _cell()],
        edges=[_edge(0, 1, 0.9)], x0=(15.0, 10.0), demand=(0.0, 2.5),
        types={0: "regenerative"}, shock=None, feasible=False,
        note="demand exceeds sustainable export at R_eff => P1C must ration"),
    "W5_near_boundary": dict(
        cells=[_cell(source="logistic", rho=0.6, chi=1.0, R=8.0), _cell()],
        edges=[_edge(0, 1, 1.0)], x0=(15.0, 10.0), demand=(0.0, 2.7),
        types={0: "regenerative"}, shock=None, feasible=True,
        note="d/g_max = 0.9 at eta = 1 => just inside the boundary"),
    "W6_topology_limited": dict(
        cells=[_cell(source="logistic", rho=0.6, chi=1.0, R=8.0),
               _cell(source="logistic", rho=0.6, chi=1.0, R=8.0), _cell()],
        edges=[_edge(0, 2, 0.5), _edge(1, 2, 0.9)], x0=(15.0, 15.0, 10.0),
        demand=(0.0, 0.0, 2.0), types={0: "regenerative", 1: "regenerative"},
        shock=None, feasible=True,
        note="aggregate regeneration sufficient but one route loss-limited"),
    "W7_demand_shock": dict(
        cells=[_cell(source="logistic", rho=0.6, chi=1.0, R=8.0), _cell()],
        edges=[_edge(0, 1, 0.9)], x0=(15.0, 10.0), demand=(0.0, 1.0),
        types={0: "regenerative"}, shock=(100, 1, 1.5), feasible=True,
        note="pre-shock 1.0 < 2.7; post-shock 2.5 < 2.7, near the boundary"),
}


def build_world(name: str):
    """(world, x0, configs, demand_base, shock, meta) for a registered world."""
    spec = WORLDS[name]
    world = d0.World(cells=tuple(spec["cells"]), edges=tuple(spec["edges"]))
    configs = {}
    for cid, kind in spec["types"].items():
        if kind == "flow":
            configs[cid] = p1c.SourceConfig(source_id=cid, source_type="flow",
                                            flow_cap=RELAY_FLOW_CAP,
                                            eps_x=EPS_X, eps_u=EPS_U)
        else:
            configs[cid] = p1c.SourceConfig(source_id=cid, source_type=kind,
                                            R_eff=world.cells[cid].R,
                                            eps_x=EPS_X, eps_u=EPS_U)
    return (world, tuple(spec["x0"]), configs, tuple(spec["demand"]),
            spec["shock"], dict(feasible=spec["feasible"], note=spec["note"]))


def world_certificate(world: d0.World) -> tuple:
    """(binding certificate, which) - V2.8 one-edge (Thm 5.1) and
    degree-weighted Gershgorin (Rmk 5.4), released d0 functions, designer-side."""
    lv = d0.lv_exact(world)
    oe = min(d0.one_edge_dt_certificate(e, lv) for e in world.edges)
    gg = d0.gershgorin_dt_certificate(world, lv)
    return (min(oe, gg), "gershgorin" if gg <= oe else "one_edge")


# ---------------------------------------------------------------------------
# drive without demand (released law, demand stripped)
# ---------------------------------------------------------------------------
def _drive_cell(c: d0.Cell) -> d0.Cell:
    """A copy of c with d = 0 so d0.natural_drive returns the drive WITHOUT
    demand. The released law is reused verbatim; only the declared demand
    parameter is moved to the service step."""
    return d0.Cell(alpha=c.alpha, beta=c.beta, chi=c.chi, L=c.L, U=c.U, R=c.R,
                   K=c.K, s=c.s, d=0.0, lam=c.lam, kappa=c.kappa,
                   source=c.source, rho=c.rho, A=c.A)


def drive_no_demand(world: d0.World, x) -> tuple:
    return tuple(d0.natural_drive(_drive_cell(c), x[k])
                 for k, c in enumerate(world.cells))


# ---------------------------------------------------------------------------
# bounded service step (registered order; steps 1-10)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class TickOutcome:
    x_before: tuple
    x_after: tuple
    u: tuple
    available: tuple
    demand_amount: tuple      # dt * demand rate
    service: tuple
    unmet: tuple
    q_req: tuple
    q_acc: tuple
    transport_loss: float
    negative_corrections: tuple   # explicit, never silent
    ledger_residual: float
    source_results: tuple
    domain_failure: bool


def bounded_step(world: d0.World, x, dt: float,
                 configs: Mapping[int, p1c.SourceConfig],
                 demand_rate: Sequence[float],
                 active_world: Optional[d0.World] = None) -> TickOutcome:
    """One bounded-service tick in the registered order.

    `active_world` restricts which edges may carry flow this tick (the
    capability restriction of arms B/C/D); its cells must be `world.cells`.
    P1C's allocation is obtained from the released p1c.p1c_step on the active
    world and is used verbatim - only its unbounded successor is replaced by
    the bounded update below."""
    if dt <= 0.0:
        raise ValueError("dt must be > 0")
    n = world.n
    xf = tuple(float(v) for v in x)                       # 1 freeze
    if len(xf) != n:
        raise ValueError("state length mismatch")
    aw = world if active_world is None else active_world
    if aw.cells is not world.cells and tuple(aw.cells) != tuple(world.cells):
        raise ValueError("active_world must share the world's cells")

    u = drive_no_demand(world, xf)                        # 2 input + regen

    # 3 transport requests + 4 P1C budgets (released allocation, unmodified)
    if aw.edges:
        tr = p1c.p1c_step(aw, xf, dt, configs)
        q_req_active = tuple(er.q_req for er in tr.edges)
        q_acc_active = tuple(er.q_acc for er in tr.edges)
        src_results = tr.sources
    else:
        q_req_active = q_acc_active = ()
        src_results = ()

    # 5 apply accepted transport simultaneously
    contrib = [[] for _ in range(n)]
    for k, e in enumerate(aw.edges):
        qa = q_acc_active[k]
        if qa != 0.0:
            contrib[e.i].append(-qa)
            contrib[e.j].append(e.eta * qa)
    sj = tuple(math.fsum(p) for p in contrib)

    # 6 physically available stock (post-loss), 9 non-negativity made explicit
    raw_avail = [xf[i] + dt * (u[i] + sj[i]) for i in range(n)]
    corr = [0.0] * n
    avail = [0.0] * n
    domain_failure = False
    for i in range(n):
        if raw_avail[i] < 0.0:
            corr[i] = -raw_avail[i]          # recorded, never silent
            avail[i] = 0.0
            if corr[i] > DOMAIN_TOL:
                domain_failure = True
        else:
            avail[i] = raw_avail[i]

    # 7 serve demand only up to available stock; 8 record unmet explicitly
    dem = [dt * float(demand_rate[i]) for i in range(n)]
    service = [min(dem[i], avail[i]) for i in range(n)]
    unmet = [dem[i] - service[i] for i in range(n)]
    xn = [avail[i] - service[i] for i in range(n)]
    for i in range(n):
        if xn[i] < -DOMAIN_TOL:
            domain_failure = True
        if -DOMAIN_TOL <= xn[i] < 0.0:
            xn[i] = 0.0                       # numerical zero only

    loss = dt * math.fsum((1.0 - e.eta) * q_acc_active[k]
                          for k, e in enumerate(aw.edges))
    # ledger: sum(x') - sum(x) = dt*sum(u) - loss - sum(service) + sum(corr)
    lhs = math.fsum(xn) - math.fsum(xf)
    rhs = dt * math.fsum(u) - loss - math.fsum(service) + math.fsum(corr)
    return TickOutcome(
        x_before=xf, x_after=tuple(xn), u=u, available=tuple(avail),
        demand_amount=tuple(dem), service=tuple(service), unmet=tuple(unmet),
        q_req=q_req_active, q_acc=q_acc_active, transport_loss=loss,
        negative_corrections=tuple(corr), ledger_residual=lhs - rhs,
        source_results=src_results, domain_failure=domain_failure)


# ---------------------------------------------------------------------------
# shared action menu (identical for arms B, C, D)
# ---------------------------------------------------------------------------
def _screen_budget(cfg: p1c.SourceConfig, x: float, u: float, dt: float):
    """P1C's own documented per-source budget rule, used only for menu
    screening. The AUTHORITATIVE q_acc always comes from p1c.p1c_step on the
    selected restricted world (asserted equal in the test suite)."""
    state = p1c.classify_state(cfg, x, u, dt)
    if state == "F":
        avail = x + dt * u
        rate = (avail / dt) if avail > 0.0 else 0.0
        return state, min(cfg.flow_cap, rate)
    if state != "P":
        return state, 0.0
    if cfg.source_type == "regenerative":
        return state, p1c.robust_budget(cfg, x, u, dt)
    return state, 0.0            # finite / irreversible: zero safe export


def action_menu(world: d0.World, x, u, sid: int, cfg: p1c.SourceConfig,
                dt: float):
    """Source-local candidate menu for cell `sid`: its OWN out-edges x the
    registered quantity fractions. Reads only the source's own frozen state,
    its permitted adjacent destination views, its own configuration and the
    edge constants. Identical for arms B, C and D."""
    state, budget = _screen_budget(cfg, x[sid], u[sid], dt)
    out = []
    if budget <= 0.0:
        return state, budget, out
    for idx, e in enumerate(world.edges):
        if e.i != sid:
            continue
        f, J = d0.edge_flux(d0.local_view(world.cells[e.i], x[e.i]),
                            d0.local_view(world.cells[e.j], x[e.j]), e)
        if J <= 0.0:
            continue
        for frac in QUANTS:
            q_req = frac * J
            q_acc = min(q_req, budget)
            if q_acc > 0.0:
                out.append(dict(edge=idx, frac=frac, f=f, q_req=q_req,
                                q_acc=q_acc))
    return state, budget, out


def _process_cost(dt: float, eta: float) -> eq.ProcessCost:
    return eq.ProcessCost(category=eq.ALLOWED_COST_CATEGORY, c0=C0,
                          c1=LAM_L * dt * (1.0 - eta))


def _quote_for(world, x, u, dt, cand):
    e = world.edges[cand["edge"]]
    inp = eq.LocalQuoteInput(
        src=d0.local_view(world.cells[e.i], x[e.i]),
        dst=d0.local_view(world.cells[e.j], x[e.j]),
        u_src=u[e.i], u_dst=u[e.j], dt=dt, eta=e.eta,
        q_req=cand["q_req"], q_acc=cand["q_acc"],
        source_id=e.i, dest_id=e.j,
        config_id=f"cfg:{e.i}:R{world.cells[e.i].R}")
    return inp


# ---------------------------------------------------------------------------
# run one arm over a registered world
# ---------------------------------------------------------------------------
@dataclass
class RunResult:
    run_id: str = ""
    world: str = ""
    arm: str = ""
    dt_label: str = ""
    dt: float = 0.0
    dt_certificate: float = 0.0
    certificate_kind: str = ""
    r_dt: float = 0.0
    series: dict = field(default_factory=dict)
    totals: dict = field(default_factory=dict)
    final: dict = field(default_factory=dict)
    x_trajectory_tail: tuple = ()


def run_arm(world_name: str, arm: str, dt: float, dt_label: str) -> RunResult:
    """Run one (world, arm, timestep) for the registered 200 ticks."""
    if arm not in ARMS:
        raise ValueError(f"unknown arm {arm!r}")
    world, x0, configs, demand_base, shock, meta = build_world(world_name)
    cert, kind = world_certificate(world)
    r_dt = dt / cert
    if r_dt > 1.0 + 1e-12:
        raise ValueError(f"r_dt = {r_dt} > 1 for {world_name} at dt = {dt}; "
                         "the registered certificate forbids execution")
    n = world.n
    x = tuple(x0)
    ser = dict(service=[], unmet=[], demand=[], burden=[], viability=[],
               ebu=[], actions=[], q_acc=[], loss=[], min_source=[],
               opportunities=[], proposed=[], rests=[], p1c_rejected=[],
               quoted=[], corrections=[], ledger=[])
    tot = dict(service=0.0, unmet=0.0, demand=0.0, ebu=0.0, ebu_pos=0.0,
               ebu_neg=0.0, actions=0, opportunities=0, proposed=0,
               accepted=0, quoted=0, rests=0, p1c_rejected=0, loss=0.0,
               overuse=0.0, reserve_crossings=0, allee_crossings=0,
               corrections=0.0, max_ledger_residual=0.0)
    domain_fail_tick = None
    for t in range(1, RUN_TICKS + 1):
        dem = list(demand_base)
        if shock is not None and t >= shock[0]:
            dem[shock[1]] += shock[2]
        u = drive_no_demand(world, x)
        active = world
        opportunities = proposed = rests = quoted = 0
        ebu_tick = pos_tick = neg_tick = 0.0
        if arm == "A_full_p1c":
            opportunities = sum(1 for e in world.edges if e.i in configs)
            proposed = opportunities
        else:
            # one action per source per micro-step, shared menu
            chosen = []
            for sid in sorted(configs):
                _st, _b, menu = action_menu(world, x, u, sid, configs[sid], dt)
                if not any(e.i == sid for e in world.edges):
                    continue
                opportunities += 1
                if not menu:
                    rests += 1
                    continue
                if arm == "D_restricted_quote_greedy":
                    best = None
                    for c in menu:
                        e = world.edges[c["edge"]]
                        inp = _quote_for(world, x, u, dt, c)
                        sch = eq.build_quote(inp, _process_cost(dt, e.eta),
                                             f"pass-{t}", t, 0)
                        val = sch.exact(c["q_acc"])
                        if best is None or val > best[0]:
                            best = (val, c)
                    if best[0] > 0.0:          # accept only if it pays
                        chosen.append(best[1])
                        proposed += 1
                    else:
                        rests += 1             # voluntary rest
                else:
                    # physical rule: steepest loss-aware force, then largest q
                    best = max(menu, key=lambda c: (c["f"], c["q_acc"]))
                    chosen.append(best)
                    proposed += 1
            active = d0.World(cells=world.cells,
                              edges=tuple(world.edges[c["edge"]] for c in chosen))
        out = bounded_step(world, x, dt, configs, dem, active_world=active)
        # EBU accounting: arm C quotes the executed physical actions
        # observationally; arm D settles the actions it chose. Arms A and B
        # carry no EBU.
        if arm in ("C_restricted_p1c_quote", "D_restricted_quote_greedy"):
            reg = eq.EpochRegistry()
            for k, e in enumerate(active.edges):
                qa = out.q_acc[k]
                if qa <= 0.0:
                    continue
                cand = dict(edge=None, q_req=out.q_req[k], q_acc=qa)
                inp = eq.LocalQuoteInput(
                    src=d0.local_view(world.cells[e.i], x[e.i]),
                    dst=d0.local_view(world.cells[e.j], x[e.j]),
                    u_src=u[e.i], u_dst=u[e.j], dt=dt, eta=e.eta,
                    q_req=out.q_req[k], q_acc=qa, source_id=e.i, dest_id=e.j,
                    config_id=f"cfg:{e.i}:R{world.cells[e.i].R}")
                sch = eq.build_quote(inp, _process_cost(dt, e.eta),
                                     f"pass-{t}", t, 0)
                reg.register(sch)
                r = reg.settle(sch, qa, t, 0)
                if r.status == "settled":
                    ebu_tick += r.issued
                    pos_tick += max(0.0, r.issued)
                    neg_tick += max(0.0, -r.issued)
                    quoted += 1
        n_act = sum(1 for q in out.q_acc if q > 0.0)
        rejected = sum(1 for k in range(len(active.edges))
                       if out.q_req[k] > 0.0 and out.q_acc[k] <= 0.0)
        overuse_t = math.fsum(max(0.0, sr.Q_acc - sr.Q_max)
                              for sr in out.source_results)
        xb, xa = out.x_before, out.x_after
        rx = sum(1 for i in range(n) if i in configs
                 and configs[i].R_eff is not None
                 and reserve_crossing(xb[i], xa[i], configs[i].R_eff))
        ax = sum(1 for i in range(n) if world.cells[i].source == "allee"
                 and xa[i] < world.cells[i].A <= xb[i])
        src_ids = [i for i in configs if configs[i].R_eff is not None]
        min_src = min((xa[i] for i in src_ids), default=float("nan"))
        svc, unm = math.fsum(out.service), math.fsum(out.unmet)
        ser["service"].append(svc); ser["unmet"].append(unm)
        ser["demand"].append(math.fsum(out.demand_amount))
        ser["burden"].append(d0.V_total(world, xa))
        ser["viability"].append(100.0 * sum(1 for i in range(n)
                                            if xa[i] >= world.cells[i].L) / n)
        ser["ebu"].append(ebu_tick); ser["actions"].append(n_act)
        ser["q_acc"].append(math.fsum(out.q_acc))
        ser["loss"].append(out.transport_loss)
        ser["min_source"].append(min_src)
        ser["opportunities"].append(opportunities)
        ser["proposed"].append(proposed); ser["rests"].append(rests)
        ser["p1c_rejected"].append(rejected); ser["quoted"].append(quoted)
        ser["corrections"].append(math.fsum(out.negative_corrections))
        ser["ledger"].append(out.ledger_residual)
        tot["service"] += svc; tot["unmet"] += unm
        tot["demand"] += math.fsum(out.demand_amount)
        tot["ebu"] += ebu_tick; tot["ebu_pos"] += pos_tick
        tot["ebu_neg"] += neg_tick
        tot["actions"] += n_act; tot["opportunities"] += opportunities
        tot["proposed"] += proposed; tot["accepted"] += n_act
        tot["quoted"] += quoted; tot["rests"] += rests
        tot["p1c_rejected"] += rejected
        tot["loss"] += out.transport_loss; tot["overuse"] += overuse_t * dt
        tot["reserve_crossings"] += rx; tot["allee_crossings"] += ax
        tot["corrections"] += math.fsum(out.negative_corrections)
        tot["max_ledger_residual"] = max(tot["max_ledger_residual"],
                                         abs(out.ledger_residual))
        if out.domain_failure and domain_fail_tick is None:
            domain_fail_tick = t
        x = xa
    dead = sum(1 for i in range(n) if world.cells[i].source == "allee"
               and x[i] < world.cells[i].A
               and d0.natural_drive(_drive_cell(world.cells[i]), x[i]) <= 0.0)
    final = dict(
        x=list(x), burden=ser["burden"][-1], viability=ser["viability"][-1],
        min_source=ser["min_source"][-1], dead_sources=dead,
        domain_failure_tick=domain_fail_tick,
        negative_state=any(v < -DOMAIN_TOL for v in x),
        source_stock=math.fsum(x[i] for i in configs
                               if configs[i].R_eff is not None),
        destination_stock=math.fsum(x[i] for i in range(n) if i not in configs
                                    or configs[i].R_eff is None),
        feasible_world=meta["feasible"], note=meta["note"])
    return RunResult(
        run_id=f"{world_name}|{arm}|{dt_label}", world=world_name, arm=arm,
        dt_label=dt_label, dt=dt, dt_certificate=cert, certificate_kind=kind,
        r_dt=r_dt, series=ser, totals=tot, final=final,
        x_trajectory_tail=tuple(x))


# ---------------------------------------------------------------------------
# post-burn-in helpers
# ---------------------------------------------------------------------------
def post_burn_in(series_list):
    return series_list[BURN_IN_TICKS:]


def pbi_sum(series_list):
    return math.fsum(post_burn_in(series_list))


def pbi_mean(series_list):
    seg = post_burn_in(series_list)
    return math.fsum(seg) / len(seg) if seg else float("nan")


# ---------------------------------------------------------------------------
# locked predicates
# ---------------------------------------------------------------------------
def reserve_harm_predicate(run: RunResult) -> dict:
    """Physical reserve-destruction predicate: any reserve or Allee crossing,
    any dead source, or physical over-use beyond tolerance."""
    t = run.totals
    f = run.final
    fired = (t["reserve_crossings"] > 0 or t["allee_crossings"] > 0
             or f["dead_sources"] > 0 or t["overuse"] > tol(t["overuse"]))
    return dict(reserve_crossings=t["reserve_crossings"],
                allee_crossings=t["allee_crossings"],
                dead_sources=f["dead_sources"], overuse=t["overuse"],
                is_reserve_destruction=bool(fired))


def service_alignment_predicate(run_d: RunResult, run_b: RunResult) -> dict:
    """Locked Boolean form (plan requires_all):
         EBU > 1.0
      AND ( service deficit beyond thresholds OR unmet excess beyond thresholds )
      AND NOT preservation-justified
    Magnitudes on post-burn-in cumulative service/unmet; persistence on the
    per-tick direction over the final 20-tick window
    (DERIVED_SEMANTICS['predicate_operationalization'])."""
    S_b, S_d = pbi_sum(run_b.series["service"]), pbi_sum(run_d.series["service"])
    U_b, U_d = pbi_sum(run_b.series["unmet"]), pbi_sum(run_d.series["unmet"])
    svc_abs = S_b - S_d
    svc_rel = (svc_abs / S_b) if S_b > 0.0 else 0.0
    unm_abs = U_d - U_b
    unm_rel = (unm_abs / U_b) if U_b > 0.0 else (1.0 if unm_abs > 0.0 else 0.0)
    w = PERSISTENCE_WINDOW
    sb, sd = run_b.series["service"][-w:], run_d.series["service"][-w:]
    ub, ud = run_b.series["unmet"][-w:], run_d.series["unmet"][-w:]
    svc_persistent = all(d < b - tol(b) for b, d in zip(sb, sd))
    unm_persistent = all(d > b + tol(b) for b, d in zip(ub, ud))
    svc_cond = (svc_rel >= SERVICE_REL and svc_abs >= SERVICE_ABS
                and svc_persistent)
    unm_cond = (unm_rel >= UNMET_REL and unm_abs >= UNMET_ABS
                and unm_persistent)
    # strict per-tick-magnitude variant, recorded for transparency only
    per_tick_variant = all(
        (b - d) >= SERVICE_ABS and (b > 0 and (b - d) / b >= SERVICE_REL)
        for b, d in zip(sb, sd))
    # preservation justification (delta_R rule)
    b_crossed = run_b.totals["reserve_crossings"] > 0
    d_crossed = run_d.totals["reserve_crossings"] > 0
    min_b = min(v for v in run_b.series["min_source"] if not math.isnan(v)) \
        if any(not math.isnan(v) for v in run_b.series["min_source"]) else float("nan")
    min_d = min(v for v in run_d.series["min_source"] if not math.isnan(v)) \
        if any(not math.isnan(v) for v in run_d.series["min_source"]) else float("nan")
    justified = bool((b_crossed and not d_crossed)
                     or (b_crossed and not math.isnan(min_b)
                         and not math.isnan(min_d)
                         and min_d - min_b >= DELTA_R))
    ebu_ok = run_d.totals["ebu"] > EBU_THRESHOLD
    fired = bool(ebu_ok and (svc_cond or unm_cond) and not justified)
    return dict(
        ebu_total=run_d.totals["ebu"], ebu_threshold_met=bool(ebu_ok),
        pbi_service_baseline=S_b, pbi_service_actor=S_d,
        service_deficit_absolute=svc_abs, service_deficit_relative=svc_rel,
        service_persistent=bool(svc_persistent),
        service_condition=bool(svc_cond),
        pbi_unmet_baseline=U_b, pbi_unmet_actor=U_d,
        unmet_excess_absolute=unm_abs, unmet_excess_relative=unm_rel,
        unmet_persistent=bool(unm_persistent), unmet_condition=bool(unm_cond),
        service_deficit_per_tick_magnitude_variant=bool(per_tick_variant),
        baseline_crossed_reserve=bool(b_crossed),
        actor_crossed_reserve=bool(d_crossed),
        min_source_baseline=min_b, min_source_actor=min_d,
        preservation_justified=justified,
        is_service_alignment_failure=fired)


# ---------------------------------------------------------------------------
# outcome classification (locked first-match precedence)
# ---------------------------------------------------------------------------
PRECEDENCE = ("numerical_or_domain_failure", "systemic_collapse",
              "destructive_service", "physical_impossibility",
              "distributive_or_policy_under_service",
              "safe_rationing_physical_scarcity", "preserve_but_under_serve",
              "preserve_and_serve", "unclassified")


def classify_outcome(run: RunResult, baseline: Optional[RunResult],
                     align: Optional[dict]) -> str:
    """First match in the locked precedence wins."""
    t, f = run.totals, run.final
    served_pbi = pbi_sum(run.series["service"])
    finite = (all(math.isfinite(v) for v in f["x"])
              and math.isfinite(f["burden"]) and math.isfinite(served_pbi))
    if (not finite) or f["negative_state"] or f["domain_failure_tick"] is not None \
            or run.r_dt > 1.0 + 1e-12 \
            or t["max_ledger_residual"] > 1e-6:
        return "numerical_or_domain_failure"
    if f["dead_sources"] > 0:
        return "systemic_collapse"
    if (t["reserve_crossings"] > 0 or t["allee_crossings"] > 0
            or t["overuse"] > tol(t["overuse"])):
        return "destructive_service"
    unmet_pbi = pbi_sum(run.series["unmet"])
    served_all = unmet_pbi <= tol(unmet_pbi)
    if not f["feasible_world"] and not served_all:
        return "physical_impossibility"
    if align is not None and align["is_service_alignment_failure"]:
        return "distributive_or_policy_under_service"
    if not served_all:
        if baseline is not None:
            b_unmet = pbi_sum(baseline.series["unmet"])
            if unmet_pbi > b_unmet + max(UNMET_ABS, tol(b_unmet)):
                return "distributive_or_policy_under_service"
        if t["p1c_rejected"] > 0 or t["reserve_crossings"] == 0:
            return "safe_rationing_physical_scarcity"
        return "preserve_but_under_serve"
    return "preserve_and_serve"
