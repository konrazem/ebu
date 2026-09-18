"""EBU scientific-test world layer: physical state, topology, actions, resolver.

Implements the PHYSICAL layer of the EBU Scientific Test Design (sections 2-5,
8-10, 22-26, 41).  This module is INFRASTRUCTURE.  It supplies no world
instance, no topology, no capacity, no band, no potential parameter, no demand
distribution and no horizon: every one of those is a preregistration slot owned
by the author (`study_protocol_schema.SLOTS`).  Constructing a `WorldSpec`
requires the caller to supply all of them explicitly, and each is validated.

**Layer separation (design section 0, Principle A/G).**  Resources live here.
The field only *evaluates* what happens here; it never acts.  Conservation
(this module) and homeostatic burden (`ebu_test_settlement`) are different
layers and are never mixed - a conservation failure is INVALID, never EBU-FAIL.

**Hard domain vs homeostatic band (section 5).**  `0 <= x_i <= K_i` is physical
impossibility.  `L_i <= x_i <= U_i` and the reserve `R_i` are declared
viability, and a state may sit outside them and still be physically real.  The
two are separate fields, separately checked, and are never collapsed.

**Execution safety.**  Nothing here runs a world, a tick loop, a trajectory, a
simulation, a parameter search or a network call, and nothing opens a file.
`apply_joint` is a PURE function from one frozen state to its successor; it is
never iterated in this repository, and no runner in `ebu_test_protocol` will
execute while the preregistration and escalation gates stand.
"""
from __future__ import annotations

import hashlib
import json
import types
from dataclasses import dataclass
from typing import Mapping, Sequence

__all__ = [
    "WorldError", "InfeasibleAction", "ConservationFailure", "SpecRefusal",
    "DemandContamination",
    "digest_of", "NodeSpec", "EdgeSpec", "Topology", "WorldSpec", "WorldState",
    "Action", "QuantityLadder", "LADDER_STAGES",
    "hard_feasible", "joint_successor", "conservation_residual", "apply_joint",
    "ResolverOutcome", "resolve_shared_source",
    "DemandEvent", "DemandSchedule", "generate_demand_schedule",
    "UnresolvedContention", "contested_destinations",
    "destination_in_degrees", "require_single_source_destinations",
    "SINGLE_SOURCE_RESTRICTION", "RESERVE_CONCEPTS",
    "NODE_BOUNDARY_ORDERING", "require_nested_boundaries",
    "QUANTITY_SEMANTICS", "delivered_from_sent", "sent_from_delivered",
    "require_reserve_concepts_distinct",
    "require_resolved_destination_contention",
    "tick_quantity_from_rate", "rate_from_tick_quantity",
    "LOSS_ACCOUNT_SEMANTICS", "ConservationProfile", "sink_increment",
    "conservation_profile", "ACTIVE_SUBSYSTEM", "EXPANDED_ACCOUNTING",
]


class WorldError(Exception):
    """Base: the physical world layer refused."""


class InfeasibleAction(WorldError):
    """An action would leave the HARD physical domain. Physically impossible."""


class ConservationFailure(WorldError):
    """Resource was created or destroyed outside a declared channel. INVALID."""


class SpecRefusal(WorldError):
    """A world/spec declaration is absent or inconsistent. Never defaulted."""


class UnresolvedContention(WorldError):
    """Two independently controlled sources contend for one destination.

    Raised when the joint accepted increment at a destination depends on an
    allocation rule that NO committed authority defines.  `p1c_v29` resolves
    contention at the SOURCE (Amendment 4, the proportional rule reproduced in
    `resolve_shared_source`); its incoming quantity is carried explicitly as
    `incoming_usable` and is marked "DIAGNOSTIC ONLY; not budgeted".  There is
    therefore no authoritative destination-side rule to reproduce, and
    inventing one here (first-come, edge order, proportional or max-min
    destination scaling, or any field-priority rule) would author an unreviewed
    scientific choice.  This fails closed instead.
    """


class DemandContamination(WorldError):
    """Demand generation was exposed to field/controller state (section 4/25)."""


def digest_of(value) -> str:
    """SHA-256 over canonical JSON. Shared with study_harness.canonical_bytes."""
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        allow_nan=False).encode("ascii")).hexdigest()


# ---------------------------------------------------------------------------
# section 5 - hard physical domain vs declared homeostatic/reserve bands
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class NodeSpec:
    """One node's HARD domain, its DECLARED bands, and its potential weights.

    `capacity` is the hard physical ceiling: `0 <= x <= capacity`.  `lower`,
    `upper` and `reserve` are declared viability, not physical impossibility.
    Keeping them in separate fields is what makes section 5's distinction
    checkable instead of a matter of convention.

    The weights `alpha`, `beta`, `chi` belong to the committed potential
    `v_i(x) = alpha[L-x]_+^2 + beta[x-U]_+^2 + chi[R-x]_+^2`
    (`V3.0_LOCAL_EBU_FOUNDATION_DRAFT.md` Definition 6.1, implemented as
    `d0_v29.penalty`).  No value is supplied here; every one is preregistered.
    """
    node_id: str
    capacity: float
    lower: float
    upper: float
    reserve: float
    alpha: float
    beta: float
    chi: float

    def __post_init__(self):
        if not isinstance(self.node_id, str) or not self.node_id.strip():
            raise SpecRefusal("a node_id is required")
        for name in ("capacity", "lower", "upper", "reserve",
                     "alpha", "beta", "chi"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise SpecRefusal(
                    f"{self.node_id}.{name} must be a real number; there is no "
                    f"default - it is a preregistered parameter")
        if self.capacity <= 0:
            raise SpecRefusal(f"{self.node_id}: capacity must be positive")
        for name in ("alpha", "beta", "chi"):
            if getattr(self, name) < 0:
                raise SpecRefusal(
                    f"{self.node_id}.{name} must be non-negative; a negative "
                    f"weight would make the burden functional non-convex and "
                    f"break Definition 6.1's convex C^1 assumption")
        if not self.lower <= self.upper:
            raise SpecRefusal(
                f"{self.node_id}: homeostatic band requires lower <= upper")
        # The bands must be REACHABLE inside the hard domain, otherwise the
        # world declares a viability target physics forbids, and every run
        # would classify PHYSICALLY-IMPOSSIBLE for a declaration error.
        for name in ("lower", "upper", "reserve"):
            value = getattr(self, name)
            if not 0.0 <= value <= self.capacity:
                raise SpecRefusal(
                    f"{self.node_id}.{name}={value} lies outside the hard "
                    f"domain [0, {self.capacity}]; a declared band that "
                    f"physics forbids is a specification error, not a result")

    def in_hard_domain(self, x: float) -> bool:
        """Section 5: physical possibility. Violation is impossible, not bad."""
        return 0.0 <= x <= self.capacity

    def in_homeostatic_band(self, x: float) -> bool:
        """Section 5: declared desirability. Violation is real but undesirable."""
        return self.lower <= x <= self.upper

    def below_reserve(self, x: float) -> bool:
        """Declared viability model, NOT automatic physical impossibility."""
        return x < self.reserve


# An immutable empty mapping, so a WorldSpec that declares no edge parameters
# cannot be mutated into one that does.
_NO_EDGE_SPECS: Mapping = types.MappingProxyType({})


@dataclass(frozen=True)
class EdgeSpec:
    """One edge's DECLARED transport parameters (design section 6 / `d0_v29.Edge`).

    This exists to close blocking gap **G-1**: the committed local law
    `J_e = M_e [f_e - theta_e]_+` needs a per-edge conductance and threshold,
    and `Topology.edges` carries bare `(source, destination)` pairs.  Declaring
    the SCHEMA is not selecting the parameters: there is no default for either
    field, construction refuses without both, and every value remains an
    unfilled preregistration slot.

    `eta` is deliberately NOT represented here.  Transfer efficiency is a
    single world-global declaration on `WorldSpec`, and a second per-edge copy
    would create two sources of truth for the same physical quantity.  The
    conservative first study declares `eta = 1` (design section 3).

    Units: `conductance` carries the units of `d0_v29`'s Onsager conductance,
    so `M_e [f_e - theta_e]_+` is a RATE.  A finite tick quantity is
    `q_e = dt * J_e` (`tick_quantity_from_rate`), never `J_e` itself.
    """
    edge: tuple
    conductance: float          # M_e > 0
    threshold: float            # theta_e >= 0

    def __post_init__(self):
        if not (isinstance(self.edge, tuple) and len(self.edge) == 2):
            raise SpecRefusal(f"edge {self.edge!r} must be (source, destination)")
        for name in ("conductance", "threshold"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise SpecRefusal(
                    f"{self.edge}.{name} must be a real number; there is no "
                    f"default - it is a preregistered parameter (G-1)")
        # Matches `d0_v29.Edge`'s own validation, reproduced rather than
        # re-derived, so the two cannot drift apart.
        if self.conductance <= 0.0:
            raise SpecRefusal(f"{self.edge}: conductance M_e must be > 0")
        if self.threshold < 0.0:
            raise SpecRefusal(f"{self.edge}: threshold theta_e must be >= 0")


@dataclass(frozen=True)
class Topology:
    """A finite directed local network. Frozen and content-addressed."""
    nodes: tuple
    edges: tuple            # ((source_id, destination_id), ...)

    def __post_init__(self):
        if not self.nodes:
            raise SpecRefusal("a topology needs at least one node")
        if len(set(self.nodes)) != len(self.nodes):
            raise SpecRefusal("duplicate node id in topology")
        known = set(self.nodes)
        seen = set()
        for edge in self.edges:
            if not (isinstance(edge, tuple) and len(edge) == 2):
                raise SpecRefusal(f"edge {edge!r} must be (source, destination)")
            source, destination = edge
            if source not in known or destination not in known:
                raise SpecRefusal(f"edge {edge!r} names an unknown node")
            if source == destination:
                raise SpecRefusal(
                    f"edge {edge!r} is a self-loop; it moves no resource "
                    f"between nodes and would settle a null physical event")
            if edge in seen:
                raise SpecRefusal(f"duplicate edge {edge!r}")
            seen.add(edge)

    @property
    def digest(self) -> str:
        return digest_of({"nodes": list(self.nodes),
                          "edges": [list(e) for e in self.edges]})

    def out_edges(self, node_id: str) -> tuple:
        return tuple(e for e in self.edges if e[0] == node_id)


@dataclass(frozen=True)
class WorldSpec:
    """The complete frozen physical world (section 22's immutable definition).

    Every one of the twelve things section 22 forbids changing between
    controller arms is either in this object or in the demand schedule and the
    initial state, each separately hashed.  `digest` is what an arm cites to
    prove it faced the same world.

    `eta` is the transfer efficiency.  Section 3 prefers `eta = 1` for the
    first world.  A lossy transfer is NOT silently allowed: `loss_sink` must
    name a declared coordinate that receives the loss, or construction refuses,
    because section 3 forbids resource disappearing without an explicit
    channel.
    """
    spec_id: str
    spec_version: str
    topology: Topology
    node_specs: Mapping
    eta: float = 1.0
    dt: float = 1.0
    loss_sink: str = ""
    path_semantics: str = ""
    edge_specs: Mapping = _NO_EDGE_SPECS

    def __post_init__(self):
        if not isinstance(self.spec_id, str) or not self.spec_id.strip():
            raise SpecRefusal("a spec_id is required")
        if not isinstance(self.spec_version, str) or not self.spec_version.strip():
            raise SpecRefusal("a spec_version is required")
        missing = tuple(sorted(set(self.topology.nodes) - set(self.node_specs)))
        extra = tuple(sorted(set(self.node_specs) - set(self.topology.nodes)))
        if missing:
            raise SpecRefusal(f"no NodeSpec for node(s) {missing}")
        if extra:
            raise SpecRefusal(f"NodeSpec(s) {extra} name no topology node")
        # Edge parameters are OPTIONAL at the schema level and REQUIRED by any
        # rule that reads them.  Declaring them here closes G-1's schema half;
        # a world that omits them simply cannot support a law needing M_e or
        # theta_e, and the reader refuses rather than inventing a default.
        unknown = tuple(sorted(set(self.edge_specs) - set(self.topology.edges)))
        if unknown:
            raise SpecRefusal(
                f"EdgeSpec(s) {unknown} name no topology edge")
        for edge, espec in self.edge_specs.items():
            if not isinstance(espec, EdgeSpec):
                raise SpecRefusal(f"edge_specs[{edge!r}] must be an EdgeSpec")
            if espec.edge != edge:
                raise SpecRefusal(
                    f"edge_specs[{edge!r}] declares edge {espec.edge!r}; a "
                    f"mislabelled edge parameter would attach a conductance to "
                    f"the wrong transport opportunity")
        if not 0.0 < self.eta <= 1.0:
            raise SpecRefusal("eta must lie in (0, 1]")
        if self.dt <= 0.0:
            raise SpecRefusal("dt must be positive")
        if self.eta < 1.0 and not self.loss_sink:
            raise SpecRefusal(
                f"eta={self.eta} < 1 destroys resource on every transfer. "
                f"Section 3 forbids silent destruction: declare a loss_sink "
                f"coordinate that receives it, or use eta = 1.")
        if self.loss_sink and self.loss_sink in self.topology.nodes:
            raise SpecRefusal(
                "loss_sink must be a declared boundary coordinate, not an "
                "ordinary node whose stock the controllers can also move")
        # The path-settlement law is part of the frozen world (section 22,
        # items 4 and 10), so the declared path semantics lives here and enters
        # the digest. There is no default: whether the straight common path is
        # the model-realised physical path or an endpoint interpolation is a
        # statement about the declared synchronous model, and defaulting it
        # would silently choose an interpretation.
        if self.path_semantics not in ("model_realised_constant_rate",
                                       "endpoint_interpolation"):
            raise SpecRefusal(
                "path_semantics must be declared as either "
                "'model_realised_constant_rate' (the declared synchronous "
                "model specifies accepted actions acting simultaneously at "
                "constant rates over the tick, so x(lambda) = z + lambda*sum "
                "dx_a IS the model-realised physical path) or "
                "'endpoint_interpolation' (only endpoints are known, so the "
                "same interpolation is a declared accounting convention)")

    @property
    def is_conservative(self) -> bool:
        """True iff the world is closed and lossless (section 3's first world)."""
        return self.eta == 1.0 and not self.loss_sink

    def edge_spec(self, edge) -> EdgeSpec:
        """The declared parameters of one edge, or a refusal naming G-1.

        There is deliberately no fallback.  A law that needs `M_e` or
        `theta_e` on an edge the world never declared them for cannot be
        evaluated, and substituting `M_e = 1`, `theta_e = 0` would silently
        author two preregistration values.
        """
        if edge not in self.topology.edges:
            raise SpecRefusal(f"{edge!r} is not an edge of this topology")
        if edge not in self.edge_specs:
            raise SpecRefusal(
                f"edge {edge!r} declares no EdgeSpec: this world carries no "
                f"M_e or theta_e for it (blocking gap G-1). A rule that needs "
                f"them cannot be evaluated here, and no default is supplied - "
                f"both are preregistered parameters.")
        return self.edge_specs[edge]

    @property
    def digest(self) -> str:
        body = {
            "spec_id": self.spec_id, "spec_version": self.spec_version,
            "topology": self.topology.digest, "eta": self.eta, "dt": self.dt,
            "loss_sink": self.loss_sink,
            "path_semantics": self.path_semantics,
            "nodes": {n: [s.capacity, s.lower, s.upper, s.reserve,
                          s.alpha, s.beta, s.chi]
                      for n, s in sorted(self.node_specs.items())},
            # Section 22: edge parameters are part of the frozen world an arm
            # cites, so they enter the digest exactly as the node parameters do.
            "edges": {f"{e[0]}->{e[1]}": [p.conductance, p.threshold]
                      for e, p in sorted(self.edge_specs.items())},
        }
        return digest_of(body)


@dataclass(frozen=True)
class WorldState:
    """One frozen physical state. Immutable and content-addressed.

    This is ONE individual state, never a trajectory.  `successor` returns a
    NEW state; nothing here advances time by itself.
    """
    spec_digest: str
    values: Mapping
    loss_accumulated: float = 0.0

    def __post_init__(self):
        for node, value in self.values.items():
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise SpecRefusal(f"state at {node!r} must be a real number")
        if self.loss_accumulated < 0.0:
            raise SpecRefusal("loss_accumulated cannot be negative")

    @property
    def digest(self) -> str:
        return digest_of({"spec": self.spec_digest,
                          "values": {k: float(v)
                                     for k, v in sorted(self.values.items())},
                          "loss": float(self.loss_accumulated)})

    def total(self) -> float:
        """Interior total. Excludes the declared loss sink by construction."""
        return sum(self.values.values())

    def successor(self, deltas: Mapping, loss: float = 0.0) -> "WorldState":
        unknown = tuple(sorted(set(deltas) - set(self.values)))
        if unknown:
            raise SpecRefusal(f"delta names unknown node(s) {unknown}")
        return WorldState(
            self.spec_digest,
            {n: v + deltas.get(n, 0.0) for n, v in self.values.items()},
            self.loss_accumulated + loss)


# ---------------------------------------------------------------------------
# section 8 - requested / permitted / accepted / measured / delivered
# ---------------------------------------------------------------------------
LADDER_STAGES = ("requested", "permitted", "accepted", "measured", "delivered")


@dataclass(frozen=True)
class QuantityLadder:
    """The five distinct quantities of section 8, kept separate by type.

    Collapsing any two of these is one of the deliberate errors section 19
    requires the harness to catch: settling a request of 10 that the resolver
    reduced to 6 must settle the physical event of 6.  The monotonicity below
    is what makes that collapse detectable rather than merely discouraged.
    """
    requested: float
    permitted: float
    accepted: float
    measured: float
    delivered: float

    def __post_init__(self):
        for stage in LADDER_STAGES:
            value = getattr(self, stage)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise SpecRefusal(f"{stage} quantity must be a real number")
            if value < 0.0:
                raise SpecRefusal(f"{stage} quantity must be non-negative")
        # permitted <= requested and accepted <= permitted: the resolver and the
        # provider only ever narrow. measured is what physically happened and
        # must equal accepted on an audit-clean schedule (Thm 8.2 (T4)).
        if self.permitted > self.requested + 1e-12:
            raise SpecRefusal(
                f"permitted {self.permitted} exceeds requested "
                f"{self.requested}: permission cannot create demand")
        if self.accepted > self.permitted + 1e-12:
            raise SpecRefusal(
                f"accepted {self.accepted} exceeds permitted {self.permitted}: "
                f"the resolver cannot grant more than the provider permitted")
        if self.delivered > self.measured + 1e-12:
            raise SpecRefusal(
                f"delivered {self.delivered} exceeds measured {self.measured}")

    def audit_clean(self, tolerance: float = 1e-12) -> bool:
        """Theorem 8.2 (T4): the realised change equals the quoted change."""
        return abs(self.measured - self.accepted) <= tolerance

    def unmet(self) -> float:
        """Section 31's Q_unmet for this action."""
        return max(0.0, self.requested - self.delivered)


@dataclass(frozen=True)
class Action:
    """One atomic physical transformation (sections 1, 10).

    Deliberately NOT recursive: an action carries no upstream cause and no
    downstream consequence.  Section 1 requires a causal chain to be a chain of
    separate atomic actions, each with its own state change, receipt and epoch,
    rather than one recursively expanded mega-action.  There is therefore no
    `parent`, `children` or `expand()` on this class, and adding one would
    break Principle C.

    `world_snapshot` is deliberately absent too (section 10): an action does
    not carry global state.
    """
    action_id: str
    actor_id: str
    edge: tuple
    carrier: str
    ladder: QuantityLadder
    start_epoch: int
    end_epoch: int
    permission_evidence: str

    def __post_init__(self):
        for name in ("action_id", "actor_id", "carrier", "permission_evidence"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise SpecRefusal(f"action field {name!r} is required")
        if not (isinstance(self.edge, tuple) and len(self.edge) == 2):
            raise SpecRefusal("edge must be (source, destination)")
        if self.end_epoch < self.start_epoch:
            raise SpecRefusal("end_epoch precedes start_epoch")

    @property
    def source(self) -> str:
        return self.edge[0]

    @property
    def destination(self) -> str:
        return self.edge[1]

    @property
    def is_instantaneous(self) -> bool:
        """Section 21: the first long-run world may use within-tick actions."""
        return self.end_epoch == self.start_epoch

    def increment(self, spec: WorldSpec) -> Mapping:
        """The physical state increment of this action alone (section 3).

        The source loses the FULL accepted withdrawal and the destination
        receives `eta * accepted` - the committed P1C convention
        (`p1c_v29.py` A4.1), not a re-derivation.
        """
        q = self.ladder.accepted
        return {self.source: -q, self.destination: spec.eta * q}

    def loss(self, spec: WorldSpec) -> float:
        return (1.0 - spec.eta) * self.ladder.accepted


# ---------------------------------------------------------------------------
# sections 3, 5, 7 - feasibility, conservation, and the joint physical update
# ---------------------------------------------------------------------------
def joint_successor(spec: WorldSpec, state: WorldState,
                    actions: Sequence[Action]) -> Mapping:
    """The successor value of every node under the FULL joint increment.

    This is the authoritative simultaneous-feasibility object.  For each node
    `j`, summing this module's own incidence convention
    (`Action.increment`: the source loses the full accepted withdrawal, the
    destination receives `eta * accepted`) gives

        x_j' = x_j + sum_{e -> j} eta_e q_e^acc - sum_{e : j -> k} q_e^acc

    so a node that simultaneously receives and sends is evaluated once, on its
    net increment.  Per-edge headroom `[K_j - x_j]_+ / eta` is a correct bound
    only for an isolated incoming transfer with no same-tick outgoing action;
    it is NOT the general law, and nothing here treats it as one.
    """
    totals = dict.fromkeys(state.values, 0.0)
    for action in actions:
        for node, delta in action.increment(spec).items():
            totals[node] += delta
    return {node: state.values[node] + delta for node, delta in totals.items()}


def hard_feasible(spec: WorldSpec, state: WorldState,
                  actions: Sequence[Action]) -> tuple:
    """Nodes whose HARD domain the joint successor would violate.

    Checked on the JOINT successor, not action by action: two individually
    feasible withdrawals from one source can be jointly infeasible, and
    checking them separately is exactly how a source goes negative.  The same
    applies at a destination that both receives and sends within one tick.

    Returns the offending `(node, resulting_value)` pairs; empty means feasible.
    """
    bad = []
    for node, resulting in joint_successor(spec, state, actions).items():
        if not spec.node_specs[node].in_hard_domain(resulting):
            bad.append((node, resulting))
    return tuple(sorted(bad))


def contested_destinations(spec: WorldSpec,
                           actions: Sequence[Action]) -> tuple:
    """Destinations receiving simultaneously from TWO OR MORE distinct sources.

    Pure detection, no allocation.  Returns `(destination, (source, ...))`
    pairs, sorted, for every node fed by more than one source in the same tick.
    """
    incoming = {}
    for action in actions:
        if action.ladder.accepted <= 0.0:
            continue
        incoming.setdefault(action.destination, set()).add(action.source)
    return tuple(sorted((node, tuple(sorted(sources)))
                        for node, sources in incoming.items()
                        if len(sources) > 1))


def require_resolved_destination_contention(
        spec: WorldSpec, state: WorldState, actions: Sequence[Action]) -> tuple:
    """Fail closed when contention at a destination needs an undefined rule.

    Contention alone is not an error: several sources may feed one destination
    and still fit inside it.  What has no committed authority is what to do
    when their individually valid proposals JOINTLY exceed the destination's
    hard capacity.  `p1c_v29` resolves at the source (Amendment 4) and carries
    the incoming quantity as `incoming_usable`, explicitly "DIAGNOSTIC ONLY;
    not budgeted", so there is no destination-side rule to reproduce.

    Returns the contested `(destination, sources)` pairs when they are jointly
    feasible; raises `UnresolvedContention` when they are not.
    """
    contested = contested_destinations(spec, actions)
    if not contested:
        return ()
    successor = joint_successor(spec, state, actions)
    over = tuple(sorted((node, successor[node])
                        for node, _ in contested
                        if not spec.node_specs[node].in_hard_domain(
                            successor[node])))
    if over:
        raise UnresolvedContention(
            f"destination(s) {over} are jointly over their hard capacity under "
            f"simultaneous transfers from several sources, and NO committed "
            f"authority defines how to allocate the shortfall at a "
            f"destination. First-come, edge-order, proportional, max-min and "
            f"field-priority allocations are all refused: choosing one here "
            f"would author an unreviewed scientific rule. The resolver choice "
            f"is returned to the author (blocking gap G-3).")
    return contested


# ---------------------------------------------------------------------------
# R_eff vs R - two different quantities, kept apart by declaration
# ---------------------------------------------------------------------------
# Declared as data so documents, schemas and tests all cite ONE statement, and
# so a check can assert that no module re-equates them.
RESERVE_CONCEPTS: Mapping = types.MappingProxyType({
    "R_eff": (
        "PROVIDER / EXPORT RESERVE FLOOR, and a STOCK QUANTITY - the same "
        "units as x, not a rate. p1c_v29 documents it as 'effective "
        "regenerative reserve (stock units)'. It is subtracted inside the "
        "committed robust budget "
        "[ (x - eps_x) + dt(u - eps_u) - R_eff ]_+ / dt; the DIVISION BY dt "
        "is what makes the BUDGET a rate, and R_eff itself is never a rate. "
        "Converting R_eff with tick_quantity_from_rate would be a unit error. "
        "It bounds what a source is PERMITTED TO SEND. "
        "APPLICABILITY: robust_budget is the State-P REGENERATIVE branch only; "
        "p1c_v29._source_budget gives 0 for finite and irreversible stock "
        "sources, and for States R and I. See the design-readiness note."),
    "R": (
        "HOMEOSTATIC RESERVE COORDINATE. NodeSpec.reserve, a declared "
        "viability condition on a node's OWN stock. It enters the committed "
        "potential through the chi[R - x]_+^2 branch (d0_v29.penalty) and may "
        "be read by any controller whose rule is eligible to read it. It is "
        "a QUANTITY."),
    "relationship": (
        "NONE is assumed. R_eff does NOT implement R. A budget computed from "
        "R_eff protects the provider's export floor and says nothing about "
        "any node's homeostatic reserve condition - least of all a "
        "DESTINATION's deficit [R_j - x_j]_+, toward which no resolver moves "
        "anything. Equating them, or citing provider protection as reserve "
        "awareness, is a scientific error. Their numeric values are separate "
        "unfilled preregistration parameters."),
})


# Phrases that ASSERT the conflation this study forbids.
_CONFLATION_PHRASES = (
    "r_eff is r", "r_eff = r", "r_eff equals r",
    "r_eff is the homeostatic reserve", "r_eff implements r",
    "r_eff protects the homeostatic", "reserve is protected for every arm",
    "provider layer already protects the reserve",
)

# Markers that turn a nearby occurrence into a WITHDRAWAL or a denial rather
# than an assertion.  A document that records "this inference was FALSE" must
# be able to quote the inference it is retracting.
_REFUTATION_MARKERS = (
    "false", "wrong", "not ", "never", "no ", "refut", "withdraw", "superseded",
    "error", "mistaken", "does not", "cannot", "forbid", "refuse", "denies",
)


def require_reserve_concepts_distinct(claim: str, *, window: int = 240) -> str:
    """Refuse a statement that ASSERTS the provider floor is the reserve.

    Enforced at the point a claim is made rather than left to review.  A
    quotation that marks the conflation false is not an assertion of it, so a
    match is only refused when no refutation marker appears nearby - otherwise
    a correction notice could not name the error it corrects.
    """
    text = " ".join(str(claim).split()).lower()
    for phrase in _CONFLATION_PHRASES:
        start = text.find(phrase)
        while start != -1:
            context = text[max(0, start - window):start + len(phrase) + window]
            if not any(marker in context for marker in _REFUTATION_MARKERS):
                raise SpecRefusal(
                    f"refused claim {claim!r}: "
                    f"{RESERVE_CONCEPTS['relationship']}")
            start = text.find(phrase, start + 1)
    return claim


# ---------------------------------------------------------------------------
# quantity semantics - which SIDE of an edge each quantity is measured on
# ---------------------------------------------------------------------------
# eta_e is dimensionless, so "source-side" and "destination-side" are not
# different UNITS - they are different POINTS OF MEASUREMENT, and a conversion
# between them is an efficiency correction.  At eta = 1 they coincide
# numerically, which is exactly why the distinction has to be declared rather
# than inferred from the arithmetic.
QUANTITY_SEMANTICS: Mapping = types.MappingProxyType({
    "q_e": "SOURCE-SIDE SENT quantity for this tick. What leaves node i.",
    "d_e": (
        "SOURCE-SIDE REQUESTED TRANSFER quantity for this tick. "
        "`DemandEvent.quantity` is compared directly against q_e and c_e "
        "throughout this repository, so it is declared source-side. If a "
        "study ever wants DESTINATION-SIDE delivered demand it must use the "
        "distinct symbol D_e and convert explicitly: d_e = D_e / eta_e "
        "(`sent_from_delivered`). The two coincide only at eta = 1."),
    "D_e": (
        "DESTINATION-SIDE DELIVERED demand. NOT used by the current candidate "
        "study; declared so that a future lossy study cannot reuse d_e for it "
        "by accident."),
    "c_e": "SOURCE-SIDE opportunity cap for this tick.",
    "requested/permitted/accepted/measured": (
        "SOURCE-SIDE quantities (QuantityLadder). The provider and the "
        "resolver only ever narrow them."),
    "delivered": (
        "DESTINATION-SIDE quantity: eta_e * accepted. This is the only ladder "
        "stage measured at the destination."),
    "destination stock increment": "eta_e * q_e (see Action.increment).",
    "source stock increment": "-q_e - the source loses the FULL sent quantity.",
    "eta_e": (
        "PROSPECTIVE FIRST-STUDY RESTRICTION: eta_e = 1 for this candidate "
        "study (conservative, closed, lossless). This is a domain restriction "
        "on the first study, NOT a universal EBU assumption; WorldSpec accepts "
        "eta in (0, 1] and refuses eta < 1 without a declared loss_sink."),
})


def delivered_from_sent(sent: float, eta: float) -> float:
    """Destination-side delivered quantity from a source-side sent quantity."""
    for name, value in (("sent", sent), ("eta", eta)):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise SpecRefusal(f"{name} must be a real number")
    if not 0.0 < eta <= 1.0:
        raise SpecRefusal("eta must lie in (0, 1]")
    return float(sent) * float(eta)


def sent_from_delivered(delivered: float, eta: float) -> float:
    """Source-side sent quantity needed to deliver a destination-side amount."""
    for name, value in (("delivered", delivered), ("eta", eta)):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise SpecRefusal(f"{name} must be a real number")
    if not 0.0 < eta <= 1.0:
        raise SpecRefusal("eta must lie in (0, 1]")
    return float(delivered) / float(eta)


# ---------------------------------------------------------------------------
# candidate first-study NODE BOUNDARY ORDERING - not a committed guarantee
# ---------------------------------------------------------------------------
# Checked against committed authority before being declared: `NodeSpec`
# requires only `lower <= upper` and that each of lower/upper/reserve lies in
# the hard domain [0, capacity].  It does NOT require `reserve <= lower`.  So
# the nested ordering the three-stage C3 semantics assume is NOT guaranteed by
# committed authority, and it is declared here as a PROSPECTIVE STUDY-DOMAIN
# RESTRICTION rather than added to NodeSpec, which would elevate it to a
# universal law of every EBU world.
NODE_BOUNDARY_ORDERING = (
    "PROSPECTIVE FIRST-STUDY DOMAIN RESTRICTION: 0 <= R_i <= L_i <= U_i <= K_i "
    "for every modeled node. Committed authority does NOT guarantee it - "
    "NodeSpec requires only lower <= upper and each boundary inside [0, K] - "
    "so a world with R_i > L_i is constructible and would make the "
    "three-stage lexicographic reading of 'reserve emergency before lower-band "
    "deficit' incoherent, because the reserve deficit would be the WIDER "
    "condition. It is NOT a universal EBU theorem, NOT a claim about future "
    "worlds, and NOT a frozen preregistration parameter; it fixes no numeric "
    "value. R_eff is deliberately ABSENT from this ordering: it is a "
    "provider/export floor, not a homeostatic boundary of the node, and "
    "R_eff != R."
)


def require_nested_boundaries(spec: WorldSpec) -> tuple:
    """Fail closed at configuration time on 0 <= R <= L <= U <= K violations.

    A CONFIGURATION refusal, not a run outcome.  Returns the validated
    per-node boundary tuples when the restriction holds.
    """
    bad = []
    for node in sorted(spec.node_specs):
        node_spec = spec.node_specs[node]
        ordered = (0.0 <= node_spec.reserve <= node_spec.lower
                   <= node_spec.upper <= node_spec.capacity)
        if not ordered:
            bad.append((node, node_spec.reserve, node_spec.lower,
                        node_spec.upper, node_spec.capacity))
    if bad:
        raise SpecRefusal(
            f"node boundary ordering refused at configuration validation for "
            f"(node, R, L, U, K) = {tuple(bad)}. {NODE_BOUNDARY_ORDERING}")
    return tuple((node, spec.node_specs[node].reserve,
                  spec.node_specs[node].lower, spec.node_specs[node].upper,
                  spec.node_specs[node].capacity)
                 for node in sorted(spec.node_specs))


# ---------------------------------------------------------------------------
# candidate first-study topology restriction - validated at CONFIGURATION time
# ---------------------------------------------------------------------------
def destination_in_degrees(spec: WorldSpec) -> Mapping:
    """How many distinct sources can feed each node. Pure topology."""
    counts = {node: 0 for node in spec.topology.nodes}
    for _source, destination in spec.topology.edges:
        counts[destination] += 1
    return counts


SINGLE_SOURCE_RESTRICTION = (
    "CANDIDATE FIRST-STUDY DESIGN CHOICE: indegree(j) <= 1 for every "
    "destination participating in a simultaneous tick. It is NOT a general "
    "EBU theorem, NOT a property of all future worlds, and NOT yet a "
    "scientific preregistration. It exists because no committed authority "
    "defines a destination-side allocation rule (p1c_v29 resolves at the "
    "SOURCE and carries incoming quantity as 'incoming_usable', explicitly "
    "'DIAGNOSTIC ONLY; not budgeted'), and because a per-source controller "
    "band claim cannot be supported under multi-source contention. It is "
    "validated at CONFIGURATION time so a violating topology fails closed "
    "BEFORE any controller is constructed, rather than surviving to "
    "apply_joint and being recorded as an INVALID run."
)


def require_single_source_destinations(spec: WorldSpec) -> tuple:
    """Fail closed at configuration time on a multiply-fed destination.

    Returns the in-degree map when the restriction holds.  Raises `SpecRefusal`
    - a CONFIGURATION refusal, not a run outcome - when it does not.
    """
    degrees = destination_in_degrees(spec)
    contended = tuple(sorted(node for node, count in degrees.items()
                             if count > 1))
    if contended:
        raise SpecRefusal(
            f"topology refused at configuration validation: destination(s) "
            f"{contended} can be fed by more than one source. "
            f"{SINGLE_SOURCE_RESTRICTION} Open problem G-3/Q-5 records the "
            f"missing policy-neutral multi-source destination resolver; "
            f"open problem G-4/Q-4 records the unsupported per-source band "
            f"claim. Neither is resolved by this refusal.")
    return tuple(sorted(degrees.items()))


# ---------------------------------------------------------------------------
# unit convention - rates and finite tick quantities are never mixed
# ---------------------------------------------------------------------------
def tick_quantity_from_rate(rate: float, dt: float) -> float:
    """`q = dt * J`. The only sanctioned rate -> quantity conversion.

    The committed layers speak in RATES: `d0_v29.edge_flux` returns a flux
    `J_e`, and `p1c_v29.robust_budget` returns
    `[ (x - eps_x) + dt(u - eps_u) - R_eff ]_+ / dt`, also a rate.  Stocks,
    demand events and `QuantityLadder` stages are finite QUANTITIES for one
    tick.  Comparing the two directly is a unit error that happens to be
    invisible whenever `dt = 1`, which is exactly why it is routed through a
    named function instead of being written inline.
    """
    for name, value in (("rate", rate), ("dt", dt)):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise SpecRefusal(f"{name} must be a real number")
    if dt <= 0.0:
        raise SpecRefusal("dt must be positive")
    return float(rate) * float(dt)


def rate_from_tick_quantity(quantity: float, dt: float) -> float:
    """`J = q / dt`. The inverse, for reporting a quantity in the rate layer."""
    for name, value in (("quantity", quantity), ("dt", dt)):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise SpecRefusal(f"{name} must be a real number")
    if dt <= 0.0:
        raise SpecRefusal("dt must be positive")
    return float(quantity) / float(dt)


def conservation_residual(spec: WorldSpec, before: WorldState,
                          after: WorldState) -> float:
    """Section 3's r_cons, including any declared loss channel.

    For a conservative world this is `|sum(after) - sum(before)|`.  When a
    `loss_sink` is declared, the loss that left the interior must appear in the
    sink, so the residual accounts for it explicitly rather than tolerating it.
    """
    interior = after.total() - before.total()
    sank = after.loss_accumulated - before.loss_accumulated
    return abs(interior + sank)


# ---------------------------------------------------------------------------
# THE LOSS ACCOUNT w AND THE TWO ACCOUNTING BOUNDARIES
# ---------------------------------------------------------------------------
# `conservation_residual` above is CORRECT as a residual: it is exactly the
# r_cons of the design, |(sum x' + w') - (sum x + w)|.  It is also, by itself,
# INSUFFICIENT, and the committed foundation says so in terms:
#
#   CONSERVATION_AND_BOUNDARY_ACCOUNTING_FOUNDATION.md, section 4.1 -
#   "a zero residual means that the observed inventory change agrees with the
#   declared boundary exchange for the selected quantity, boundary, resolution,
#   and transition. It does not prove that every exchange was observed or that
#   the chosen state is physically complete."
#
# Two concrete ways a zero residual can be produced by an INVALID transition,
# both verified against this module rather than hypothesised:
#
#   (1) UNDECLARED SINK CHANGE.  In a world with NO declared loss channel
#       (`loss_sink == ""`), an interior loss of 2.0 paired with a sink credit
#       of 2.0 returns residual 0.0.  The sink the world never declared has
#       absorbed an active-stock discrepancy.
#   (2) SINK WITHDRAWAL.  A sink that DECREASES by 3.0 while the interior gains
#       3.0 also returns residual 0.0 - resource recovered from an irreversible
#       cumulative loss account, which design section 8 forbids and for which
#       no physical transformation exists in this model.
#
# `WorldState` does not catch either: it refuses only a NEGATIVE
# `loss_accumulated`, not a DECREASING one, and it has no view of the spec.
#
# The fix is the one the design itself prescribes - check the individual
# identities separately - and NOT a change to `conservation_residual`, whose
# formula is right, nor to `apply_joint`, which already builds its successor
# from the action law and so cannot exhibit either failure.  Everything below
# is additive: no existing call site changes behaviour.
#
# UNITS.  `interior_delta`, `sink_delta`, `expected_sink` and every per-node
# quantity are CARRIER QUANTITY units for one transition - the same units as
# `x_i`, `q_e` and `WorldState.loss_accumulated`.  They are NOT rates (see
# `tick_quantity_from_rate`) and NOT EBU burden units.  A burden-valued
# expression may not be added to any of them without a separately justified
# conversion.
LOSS_ACCOUNT_SEMANTICS: Mapping = types.MappingProxyType({
    "w": (
        "`WorldState.loss_accumulated`. An IRREVERSIBLE CUMULATIVE LOSS "
        "ACCOUNT of represented carrier quantity removed from the active "
        "domain. Nonnegative and NONDECREASING under the declared "
        "transfer-only model."),
    "w is not": (
        "not an available transfer source; not a demand-generating node; not "
        "service; not a wallet or issuance account; not a Mobius or "
        "interaction account; not automatically a homeostatic-potential "
        "factor. It is excluded from transfer opportunities STRUCTURALLY: "
        "`WorldSpec` refuses a `loss_sink` that names a topology node, and "
        "`Topology` refuses an edge whose endpoint is not a node, so no edge "
        "can touch it."),
    "w and V": (
        "V is a function of the ACTIVE stocks only - `potential(spec, values)` "
        "reads `values`, never `loss_accumulated`. Equivalently the extended "
        "potential is Vtilde(x, w) = V(x), explicitly independent of w. This "
        "is a DECLARED OMISSION of sink burden from this model. It is NOT a "
        "finding that waste is harmless or that loss has no physical "
        "consequence."),
    "w and C_a": (
        "UNRESOLVED AUTHORITY SCOPE QUESTION - deliberately NOT decided here. "
        "Committed Definition 6.4 offers a candidate "
        "`C_a(q) = c0*1[q>0] + lambda_L*dt*(1-eta)*q` and calls the lambda_L "
        "term CATEGORY 2, justified by the parenthetical 'the state vector "
        "has no destroyed stock coordinate'. THAT PREMISE IS FALSE of this "
        "working tree, which carries `WorldState.loss_accumulated` in the "
        "declared transition and in the state digest. Four clauses then point "
        "AWAY from category 2: (a) the Definition 6.4 body excludes from C_a "
        "any burden already represented by 'the physical state transition' or "
        "by 'transport loss ALREADY VISIBLE THROUGH THE STATE'; (b) category "
        "1 is keyed to 'the state transition OR V_loc', not V_loc alone; (c) "
        "category 2's own admission condition requires 'NO CORRESPONDING "
        "STATE COORDINATE', without the V_loc-arguments qualifier; (d) the "
        "no-double-count condition tests expressibility as a V_loc difference "
        "under the declared 'OR ANY ADMISSIBLE EXTENDED' state functional, "
        "and the source never defines which extensions are admissible. Only "
        "category 2's headline phrasing ('no state coordinate in V_loc's "
        "ARGUMENTS') points toward category 2. Open problem O9 (partially "
        "represented dissipation) registers exactly this case - a channel "
        "carried by a state coordinate but absent from the potential - as "
        "OPEN. STATUS: unresolved wording/scope conflict; it is NOT resolved "
        "by this module, and an earlier revision of this text asserted 'still "
        "category 2, no conflict', which selected one clause while ignoring "
        "the other four. That assertion is WITHDRAWN."),
    "w and C_a - what IS settled": (
        "Independently of the classification question: conservation "
        "bookkeeping does not by itself VALUE any burden, so the presence of "
        "this ledger proves nothing about whether a burden of loss has been "
        "priced; V does not read w; C_a is identically 0 in every fixture "
        "here; and no synthetic loss surcharge is added anywhere. These are "
        "mechanical facts about this implementation, NOT a resolution of the "
        "Definition 6.4 scope question."),
    "w and C_a - why Study 1 is unaffected": (
        "At eta = 1 the lambda_L term is IDENTICALLY ZERO whichever category "
        "it belongs to, and the first study declares the idealized scope "
        "C_a = 0. The unresolved classification therefore blocks nothing in "
        "the lossless study; it must be settled before any study that "
        "declares a NONZERO lambda_L."),
    "interpretation": (
        "Whether w is an inactive physical sink INVENTORY or cumulative "
        "OUTWARD-FLOW accounting is left open; neither reading licenses "
        "treating it as reusable stock. Material recovery would require a "
        "separate physical transformation with its own feasibility "
        "conditions, quantity, state changes, affected potential factors and "
        "audit record - not a withdrawal from this account."),
    "units": (
        "CARRIER QUANTITY units, identical to x_i and q_e. Never a rate, "
        "never EBU burden units."),
})

# The two accounting boundaries of design section 6, named so that a ledger
# always says which one it describes.  Counting the same loss BOTH as an
# expanded internal sink increment AND as an additional external outflow at the
# same level is double counting.
ACTIVE_SUBSYSTEM = "active_subsystem"       # d(sum x) = -dw ; loss flows OUT
EXPANDED_ACCOUNTING = "expanded_accounting"  # d(sum x + w) = 0 ; sink included


@dataclass(frozen=True)
class ConservationProfile:
    """The DECOMPOSED transition ledger: every identity checked separately.

    Total closure alone does not prove that the source, destination and sink
    increments are individually correct, so all of them are reported and
    checked here rather than being collapsed into one residual.
    """
    boundary: str
    interior_delta: float        # sum_i (x_i' - x_i)
    sink_delta: float            # w' - w
    expected_sink: float         # sum_e (1 - eta_e) q_e, FROM THE ACTION LAW
    expected_interior: float     # -expected_sink
    residual: float              # the same r_cons as conservation_residual
    per_node: Mapping            # node -> (expected_delta, actual_delta)
    loss_channel_declared: bool

    @property
    def active_balance_holds(self) -> bool:
        """The active-resource balance d(sum x) = -dw, as a reported fact."""
        return self.interior_delta == -self.sink_delta


def sink_increment(spec: WorldSpec, before: WorldState,
                   after: WorldState) -> float:
    """`dw = w' - w`, refusing the two ways a sink change can be illegitimate.

    Refuses a nonzero increment in a world that declares NO loss channel, and
    refuses ANY decrease.  Both are inert in the conservative first study,
    where `eta = 1` makes every `Action.loss` zero and `dw` identically 0.
    """
    delta = float(after.loss_accumulated) - float(before.loss_accumulated)
    if delta < 0.0:
        raise ConservationFailure(
            f"the loss account DECREASED by {-delta!r}. w is an irreversible "
            f"cumulative loss account: resource is never withdrawn from it. "
            f"Material recovery would be a SEPARATE physical transformation "
            f"with its own feasibility conditions, quantity, state changes "
            f"and audit record, acting on an actual recoverable waste stock - "
            f"not a credit against this account.")
    if delta != 0.0 and not spec.loss_sink:
        raise ConservationFailure(
            f"the loss account changed by {delta!r} in a world that declares "
            f"NO loss channel (loss_sink is empty). An undeclared sink change "
            f"can offset an active-stock discrepancy and drive r_cons to zero, "
            f"so the transition would report as conserved while active "
            f"resource vanished. Declare a loss_sink coordinate, or keep the "
            f"sink constant.")
    return delta


def conservation_profile(spec: WorldSpec, before: WorldState,
                         after: WorldState, actions: Sequence[Action],
                         *, tolerance: float,
                         boundary: str = EXPANDED_ACCOUNTING
                         ) -> ConservationProfile:
    """Check the source, destination and sink increments SEPARATELY.

    PURE: three supplied objects in, one record out.  Nothing is advanced;
    `after` is supplied by the caller, not produced here.

    The expected sink increment is computed FROM THE DECLARED ACTION LAW
    (`Action.loss`), never as a balancing plug chosen to make the residual
    vanish.  `tolerance` is a required argument so that no default can quietly
    widen it; the committed foundation (section 4.3) declares that there is no
    universal zero-residual rule and no hidden global tolerance.
    """
    if boundary not in (ACTIVE_SUBSYSTEM, EXPANDED_ACCOUNTING):
        raise SpecRefusal(
            f"boundary must be {ACTIVE_SUBSYSTEM!r} (loss is outward flow) or "
            f"{EXPANDED_ACCOUNTING!r} (the sink is inside the balance); a "
            f"ledger that does not say which one it describes invites "
            f"counting the same loss at both levels")
    if not isinstance(tolerance, (int, float)) or isinstance(tolerance, bool) \
            or tolerance < 0.0:
        raise SpecRefusal("an explicit non-negative tolerance is required")
    if before.spec_digest != spec.digest or after.spec_digest != spec.digest:
        raise SpecRefusal(
            "both states must be built against this WorldSpec; comparing "
            "states from different worlds compares different quantities")

    delta = sink_increment(spec, before, after)          # refuses first
    expected_sink = 0.0
    expected_nodes = dict.fromkeys(before.values, 0.0)
    for action in actions:
        expected_sink += action.loss(spec)
        for node, step in action.increment(spec).items():
            expected_nodes[node] += step

    if abs(delta - expected_sink) > tolerance:
        raise ConservationFailure(
            f"sink increment {delta!r} does not match the declared action law "
            f"{expected_sink!r} (sum_e (1 - eta) q_e). The sink increment must "
            f"COME FROM the action law; a value chosen to close the balance is "
            f"a plug, and a plug makes the residual meaningless.")
    bad = tuple(sorted(
        (node, expected, float(after.values[node]) - float(before.values[node]))
        for node, expected in expected_nodes.items()
        if abs((float(after.values[node]) - float(before.values[node]))
               - expected) > tolerance))
    if bad:
        raise ConservationFailure(
            f"per-node increments disagree with the action law at {bad} "
            f"(node, expected, actual). Total closure alone does NOT prove "
            f"the source, destination and sink increments are individually "
            f"correct, which is exactly why they are checked separately here.")
    return ConservationProfile(
        boundary=boundary,
        interior_delta=after.total() - before.total(),
        sink_delta=delta,
        expected_sink=expected_sink,
        expected_interior=-expected_sink,
        residual=conservation_residual(spec, before, after),
        per_node={n: (e, float(after.values[n]) - float(before.values[n]))
                  for n, e in sorted(expected_nodes.items())},
        loss_channel_declared=bool(spec.loss_sink))

def apply_joint(spec: WorldSpec, state: WorldState, actions: Sequence[Action],
                *, tolerance: float) -> WorldState:
    """The section 7 step-9 joint physical update. PURE; one state to one state.

    This is a single transition, never a loop.  Nothing in this repository
    iterates it: `ebu_test_protocol.ExperimentRunner` refuses to execute while
    the preregistration and escalation gates stand.

    Refuses on hard infeasibility (physically impossible) and on a conservation
    residual beyond the DECLARED tolerance (INVALID, per section 34 - never
    EBU-FAIL).  The tolerance is a required argument precisely so that no
    default can quietly widen it.
    """
    if not isinstance(tolerance, (int, float)) or isinstance(tolerance, bool) \
            or tolerance < 0.0:
        raise SpecRefusal("an explicit non-negative tolerance is required")
    if state.spec_digest != spec.digest:
        raise SpecRefusal(
            "state was built against a different WorldSpec; section 22 "
            "requires every arm to face the identical frozen world")
    bad = hard_feasible(spec, state, actions)
    if bad:
        raise InfeasibleAction(
            f"joint increment leaves the hard physical domain at {bad}; this "
            f"is physical impossibility (section 5), not homeostatic "
            f"undesirability, and it must not be recorded as EBU-FAIL")
    for action in actions:
        if not action.ladder.audit_clean():
            raise ConservationFailure(
                f"action {action.action_id!r} is not audit-clean: measured "
                f"{action.ladder.measured} != accepted {action.ladder.accepted} "
                f"(Theorem 8.2 assumption (T4))")
    totals = dict.fromkeys(state.values, 0.0)
    loss = 0.0
    for action in actions:
        for node, delta in action.increment(spec).items():
            totals[node] += delta
        loss += action.loss(spec)
    successor = state.successor(totals, loss)
    residual = conservation_residual(spec, state, successor)
    if residual > tolerance:
        raise ConservationFailure(
            f"conservation residual {residual!r} exceeds the declared "
            f"tolerance {tolerance!r}. Section 3: the run is INVALID, not an "
            f"EBU scientific failure. Resource is never silently destroyed.")
    return successor


# ---------------------------------------------------------------------------
# section 9 - provider permission and shared-source resolution (committed P1C)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ResolverOutcome:
    """The result of jointly resolving one source's outgoing actions."""
    source: str
    budget: float
    total_requested: float
    sigma: float
    accepted: Mapping

    @property
    def was_scaled(self) -> bool:
        return self.sigma < 1.0


def resolve_shared_source(source: str, requests: Mapping,
                          budget: float) -> ResolverOutcome:
    """Proportional shared-source resolution, exactly as committed P1C defines.

    `p1c_v29.py` (Amendment 4): `sigma = min(1, Q_max_rob / Q_req)` and
    `q_e_acc = sigma * q_e_req`.  This is reproduced, not re-derived, and the
    committed module remains the authority for how `budget` itself is computed
    from the source's reserve and robustness margins.

    Section 9 is explicit that this is a PHYSICAL permission mechanism.  It is
    not a social priority rule, not a fairness theorem and not an EBU-value
    statement, and nothing here consults the field.

    **Units.**  `budget` and every value in `requests` are finite QUANTITIES
    for one tick, in the same units as a stock.  `p1c_v29.robust_budget`
    returns a RATE (it divides by `dt`), so a caller wiring that committed
    function to this one must convert with `tick_quantity_from_rate`.  Passing
    the rate straight through is a unit error that is invisible at `dt = 1`.

    **`R_eff` is NOT `R`.**  Two different quantities, and conflating them is a
    scientific error, not a naming preference:

    * `R_eff` (`p1c_v29.SourceConfig.R_eff`) is the PROVIDER / EXPORT floor.
      It bounds what a source is permitted to send out, and it is what the
      committed robust budget subtracts.
    * `R` (`NodeSpec.reserve`) is the HOMEOSTATIC RESERVE COORDINATE.  It is a
      declared viability condition on a node's own stock, used by the committed
      potential `v_i` through its `chi[R - x]_+^2` branch and by any controller
      whose rule is eligible to read it.

    A budget computed from `R_eff` therefore protects the PROVIDER's export
    floor for every arm.  It does **not** implement the homeostatic reserve
    condition `R`, at this source or at any destination, and it must never be
    cited as doing so.  In particular it says nothing whatever about a
    DESTINATION's reserve deficit `[R_j - x_j]_+`: nothing in this resolver
    moves resource toward a node that is below `R`.  A controller that wants
    the homeostatic reserve respected must carry that in its own rule.

    This function neither adds nor removes any reserve protection of either
    kind; it only scales to the budget it is given, identically for every arm.
    """
    if not isinstance(budget, (int, float)) or isinstance(budget, bool):
        raise SpecRefusal("budget must be a real number")
    if budget < 0.0:
        raise SpecRefusal("an export budget cannot be negative")
    for edge, q in requests.items():
        if isinstance(q, bool) or not isinstance(q, (int, float)) or q < 0.0:
            raise SpecRefusal(f"request on {edge!r} must be a non-negative real")
    total = sum(requests.values())
    sigma = 1.0 if total <= budget else (budget / total if total > 0.0 else 1.0)
    sigma = min(1.0, sigma)
    return ResolverOutcome(
        source=source, budget=float(budget), total_requested=float(total),
        sigma=float(sigma),
        accepted={edge: sigma * q for edge, q in requests.items()})


# ---------------------------------------------------------------------------
# sections 24-26 - exogenous demand, generated once and replayed identically
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class DemandEvent:
    """One externally generated request. Carries no field information."""
    tick: int
    edge: tuple
    quantity: float

    def __post_init__(self):
        if self.tick < 0:
            raise SpecRefusal("tick must be non-negative")
        if isinstance(self.quantity, bool) \
                or not isinstance(self.quantity, (int, float)) \
                or self.quantity < 0.0:
            raise SpecRefusal("demand quantity must be a non-negative real")


@dataclass(frozen=True)
class DemandSchedule:
    """A complete, frozen, hashed demand history (sections 24, 26, 38).

    Generated ONCE per seed and replayed byte-identically for every controller
    arm - common random numbers.  `digest` is what each arm cites to prove it
    faced the same history; `verify_replay` makes a divergence a refusal rather
    than a silent difference in results.
    """
    seed: str
    model_id: str
    horizon: int
    events: tuple

    def __post_init__(self):
        if not isinstance(self.seed, str) or not self.seed.strip():
            raise SpecRefusal("a demand seed is required")
        if not isinstance(self.model_id, str) or not self.model_id.strip():
            raise SpecRefusal(
                "a demand model_id is required; section 24 forbids an "
                "undocumented hard-coded distribution")
        if self.horizon <= 0:
            raise SpecRefusal("horizon must be positive")
        for event in self.events:
            if event.tick >= self.horizon:
                raise SpecRefusal(
                    f"demand event at tick {event.tick} exceeds horizon "
                    f"{self.horizon}")

    @property
    def digest(self) -> str:
        return digest_of({
            "seed": self.seed, "model_id": self.model_id,
            "horizon": self.horizon,
            "events": [[e.tick, list(e.edge), float(e.quantity)]
                       for e in self.events]})

    def at_tick(self, tick: int) -> tuple:
        """The events revealed at one tick (section 7 step 2).

        Reveals the present only.  There is deliberately no `future()` and no
        slice accessor on this class: section 28 forbids a controller reading
        future demand, and the cheapest way to enforce that is to give the
        runtime no method that returns it.
        """
        if not isinstance(tick, int) or isinstance(tick, bool) or tick < 0:
            raise SpecRefusal("tick must be a non-negative int")
        return tuple(e for e in self.events if e.tick == tick)

    def verify_replay(self, other: "DemandSchedule") -> bool:
        """Section 26: every arm must face the identical history."""
        return self.digest == other.digest


def generate_demand_schedule(*, seed: str, model_id: str, horizon: int,
                             edges: Sequence, draw) -> DemandSchedule:
    """Generate the complete demand history up front, from the seed alone.

    `draw(unit, tick, edge) -> float` maps a uniform variate to a quantity and
    is supplied by the preregistered demand model (slot S-D).  No distribution
    is chosen here: section 24 requires the canonical model and its parameters
    to be preregistered rather than picked silently in code.

    **Section 4 / 25 are enforced structurally.**  `draw` receives a variate, a
    tick and an edge - and NO world state, NO potential, NO gradient, NO
    reserve status and NO controller identity.  The homeostatically intelligent
    environment section 25 forbids ("if node is below L, send resource toward
    it") is therefore not merely discouraged: it cannot be written against this
    signature.  Passing a `WorldState` in is refused below.

    Determinism (section 41): values come from SHA-256 counter mode keyed by
    `(seed, tick, edge)`, so the history is reproducible and random-access, and
    no global RNG is touched anywhere.
    """
    if not isinstance(seed, str) or not seed.strip():
        raise SpecRefusal("a demand seed is required")
    if not callable(draw):
        raise SpecRefusal("draw must be callable")
    if isinstance(horizon, bool) or not isinstance(horizon, int) or horizon <= 0:
        raise SpecRefusal("horizon must be a positive int")
    events = []
    for tick in range(horizon):
        for edge in edges:
            material = json.dumps([seed, tick, list(edge)],
                                  separators=(",", ":")).encode("ascii")
            word = int.from_bytes(hashlib.sha256(material).digest()[:8], "big")
            unit = word / float(1 << 64)
            quantity = draw(unit, tick, tuple(edge))
            if isinstance(quantity, WorldState):
                raise DemandContamination(
                    "a demand model returned world state; demand must be "
                    "exogenous (sections 4, 25)")
            if isinstance(quantity, bool) \
                    or not isinstance(quantity, (int, float)):
                raise SpecRefusal("draw must return a real quantity")
            if quantity < 0.0:
                raise SpecRefusal("demand quantity must be non-negative")
            if quantity > 0.0:
                events.append(DemandEvent(tick, tuple(edge), float(quantity)))
    return DemandSchedule(seed=seed, model_id=model_id, horizon=horizon,
                          events=tuple(events))
