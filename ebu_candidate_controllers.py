"""Candidate controller drafts C0-C4, and the study's identity registration.

**Study identity (registered here, and nothing more).**  These controllers
belong to the

    prospective stochastic sustained-demand conservative-world study

`IDENTITY` below carries the registration, clause by clause.  The registration
asserts an identity and refuses everything else: it is **not** preregistration,
**not** execution permission and **not** scientific evidence, it assigns no SD
number, and it leaves every scientific parameter unfrozen.  See
`V3.0_PROSPECTIVE_STUDY_CONTROLLER_DECISION_PACKET.md`.

**Status of every controller here: `CANDIDATE_UNAPPROVED`.**  These are drafts
for the author to accept, amend or reject.  None is adopted, preregistered or
implemented as a default; `draft()` returns a declaration record, and `build()`
has **no success path** while a draft is unapproved - including C0, which is
unambiguous but is still an arm and still requires an author act.

**The common context and the typed projections.**  One immutable
`CommonLocalContext` carries all local physical information at a decision
location; it is built WITHOUT any controller argument and is projected into
typed views `C0View`..`C4View`, each carrying exactly the fields its family's
declared formula consumes.  Undeclared quantities are STRUCTURALLY ABSENT
rather than merely unread - `C3View` has no alpha/beta/chi, no mu, no f_e and
no reserve to read at all.  `information_ledger()` keeps three concepts apart:
what is present in the context, what each view exposes, and what each formula
consumes.

**C3 was corrected, twice.**  An earlier draft bounded C3's export by the
reserve coordinate `[x_i - R_i]_+`, which on the illustrative fixture left the
source below its own lower homeostatic band.  A second draft removed reserve
awareness entirely on the mistaken ground that the common P1C layer already
supplied it.  **It does not.**  `R_eff` is a PROVIDER/EXPORT FLOOR bounding what
a source may SEND; `R` (`NodeSpec.reserve`) is the HOMEOSTATIC RESERVE
COORDINATE of a node's own stock.  `R_eff` does not implement `R`, at any node,
and nothing in the resolver moves resource toward a destination below `R`.

C3 is therefore now a THREE-STAGE RESERVE-AND-BAND-AWARE controller with a
source-side band-safe budget `A_i = [x_i - L_i]_+`: stage 1 serves destination
homeostatic RESERVE deficits, stage 2 remaining LOWER-BAND deficits, stage 3
ordinary demand inside the destination UPPER band - each by exact capped
max-min water-filling over the recursively reduced budget.  Its ordering is a
PROPOSAL-LEVEL priority: the common resolver is stage-blind, so where
`sigma < 1` a stage-1 reserve deficit can be left incompletely served while
stage-3 service executes (`P1C_BINDING_ANALYSIS`,
`p1c_binding_demonstration`).  See
`V3.0_PROSPECTIVE_STUDY_CONTROLLER_DECISION_PACKET.md` Part 0 and
`EBU_TEST_DESIGN_CONFORMANCE_MAP.md` CONFLICT-4.

**Illustrative fixtures are DERIVED, never fitted.**  Every worked example is
computed by executing the family's declared symbolic rule (`CANDIDATE_RULES`)
on the fixture; only the prose reading is authored.  The symbolic rule
determines the fixture; the fixture never determines the rule.  Outcomes report
delivered quantity, post-state and band/reserve violations as SEPARATE
dimensions, with no aggregate, score, rank or winner field - dominance is a
relation over registered scientific metrics, and slot S-M is unfilled.

**Execution safety.**  Pure declarations, pure predicates and pure arithmetic
over declared records and individual synthetic states.  Nothing runs a world,
tick, trajectory or search; nothing opens a file or touches the network.  No
controller in this module is callable AS A STUDY ARM: `build()` has no success
path, and the candidate reference functions exist only so the fixtures derive
from the rules.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

import ebu_test_protocol as proto
import ebu_test_world as world

__all__ = [
    "STUDY_NAME", "STUDY_STATUS", "IDENTITY_CLAUSES", "StudyIdentity",
    "IDENTITY", "identity_record", "require_identity_only",
    "CANDIDATE_UNAPPROVED", "AUTHOR_ACCEPTED", "STATUS_VOCABULARY",
    "PIPELINE", "OPPORTUNITY_INVARIANTS", "OpportunitySet",
    "require_within_opportunity", "common_opportunities",
    "WorkedExample", "ControllerDraft", "DRAFTS", "draft",
    "unapproved_drafts", "statuses", "comparison_rows", "build",
    "OPEN_QUESTIONS", "BLOCKING_GAPS", "RESOLVED_QUESTIONS", "CLOSED_GAPS",
    "FIXTURE_LABEL", "OPPORTUNITY_DERIVATION",
    "CommonLocalContext", "build_common_context",
    "C0View", "C1View", "C2View", "C3View", "C4View",
    "CONTEXT_CONTENTS", "FORMULA_CONSUMPTION", "FORBIDDEN_ON_VIEW",
    "information_ledger", "destination_in_degrees",
    "require_single_source_destinations",
    "capped_max_min_water_fill", "CANDIDATE_RULES",
    "c0_candidate_proposal", "c1_candidate_proposal", "c2_candidate_proposal",
    "c3_candidate_proposal", "c3_candidate_stages", "c4_candidate_proposal",
    "c4_candidate_detail",
    "FixtureOutcome", "evaluate_fixture", "fixture_context", "fixture_outcome",
    "FIXTURES", "FIXTURE_BUDGET_READING",
]

STUDY_NAME = "prospective stochastic sustained-demand conservative-world study"

# The label every illustrative number in this module carries.  It is asserted
# on construction, so an unlabelled number cannot reach a worked example.
FIXTURE_LABEL = "ILLUSTRATIVE_FIXTURE_ONLY"


# ---------------------------------------------------------------------------
# identity registration - an identity, and deliberately nothing else
# ---------------------------------------------------------------------------
IDENTITY_CLAUSES: Mapping[str, str] = {
    "no_sd_number": (
        "This study has NO SD number. None is assigned here and none is "
        "implied. It does not occupy a slot in the SD-01..SD-14 programme "
        "register, and no register row may be created for it by this file."),
    "not_sd_01": (
        "It is NOT SD-01. It does not amend SD-01, does not replace SD-01, "
        "does not supersede any registered SD study and does not rewrite any "
        "historical study identity. Design section 45: a stochastic "
        "sustained-demand world requires a prospective NEW registration or an "
        "explicit approved amendment; this record is a candidate for the "
        "former and is not itself either."),
    "not_regenerative": (
        "It is NOT regenerative. The first world is closed and lossless "
        "(eta = 1, design section 3) and regeneration is ABSENT from the "
        "physical plant: no coordinate grows, no source term exists, and "
        "p1c_v29's regenerative branch has no counterpart here. The word "
        "'regenerative' must not be applied to this study unless and until a "
        "regeneration mechanism actually exists in the plant."),
    "nothing_frozen": (
        "All scientific content remains UNFROZEN: parameters, controllers, "
        "metrics, thresholds, seeds, horizons, tolerances and oracle rules. "
        "Registering an identity freezes none of them. Every one is an "
        "unfilled slot in study_protocol_schema.SLOTS and a refusal condition "
        "rather than a default."),
    "registration_is_not_preregistration": (
        "Identity registration is NOT preregistration, NOT execution "
        "permission and NOT scientific evidence. It fixes what the study is "
        "called and what it is not; it fixes nothing about what the study "
        "will do, and it establishes no result."),
    "no_execution_authorization": (
        "AWS and scientific execution remain UNAUTHORIZED. Escalation E5 "
        "stands (no SD-01 successor campaign, no cloud work, no spend), and "
        "coordinate W-2 clause 6 requires separate authorization for every "
        "world, parameter, controller definition, metric, threshold, "
        "preregistration, AWS request and execution packet."),
}


@dataclass(frozen=True)
class StudyIdentity:
    """The registration record. Six clauses, each independently checkable."""
    name: str
    sd_number: None
    registration_kind: str
    clauses: Mapping

    def __post_init__(self):
        if self.sd_number is not None:
            raise proto.NotPreregistered(
                "this study has no SD number; assigning one here would be "
                "exactly the silent renaming design section 45 forbids")
        missing = tuple(sorted(set(IDENTITY_CLAUSES) - set(self.clauses)))
        if missing:
            raise proto.NotPreregistered(
                f"identity clause(s) {missing} missing; an identity "
                f"registration that omits a clause asserts more than it says")

    def declaration(self) -> Mapping:
        return {
            "study": self.name, "sd_number": None,
            "registration_kind": self.registration_kind,
            "is_preregistration": False, "is_execution_permission": False,
            "is_scientific_evidence": False, "is_regenerative": False,
            "amends_or_replaces_sd01": False,
            "scientific_content_frozen": False,
            "aws_authorized": False, "execution_authorized": False,
            "clauses": dict(self.clauses),
        }


IDENTITY = StudyIdentity(
    name=STUDY_NAME, sd_number=None,
    registration_kind=(
        "SEPARATE PROSPECTIVE CANDIDATE - identity only. Registered as a "
        "distinct candidate study, not as an SD stage and not as a variant, "
        "successor or amendment of one."),
    clauses=IDENTITY_CLAUSES)

# Kept as a single string because the surrounding suites and documents quote
# it; it is assembled from the clauses so the two cannot drift apart.
STUDY_STATUS = (
    "CANDIDATE STUDY - no SD number assigned; not SD-01; not a substitute for "
    "any registered SD study; requires a prospective new registration or an "
    "approved amendment before it may be run (design section 45). The world is "
    "conservative (closed, lossless); regeneration is NOT represented in the "
    "physical plant, so the study is not described as regenerative. "
    "Identity registration is not preregistration, not execution permission "
    "and not scientific evidence; all scientific parameters, controllers, "
    "metrics, thresholds, seeds, horizons, tolerances and oracle rules remain "
    "unfrozen; AWS and scientific execution remain unauthorized."
)

# Purposes a bare identity registration can never serve.  Named so that a
# caller has to be explicit about what it is trying to do with the record.
_FORBIDDEN_PURPOSES = {
    "preregistration": "identity registration is not preregistration",
    "execution": "identity registration is not execution permission",
    "aws": "AWS remains unauthorized (escalation E5)",
    "evidence": "identity registration is not scientific evidence",
    "sd_number": "no SD number is assigned",
    "amendment": "this study does not amend or replace SD-01",
}


def identity_record() -> Mapping:
    """The full registration, for a reviewer or a provenance record."""
    return IDENTITY.declaration()


def require_identity_only(purpose: str) -> str:
    """Refuse any use of the registration beyond naming the study."""
    key = str(purpose).strip().lower()
    if key in _FORBIDDEN_PURPOSES:
        raise proto.NotPreregistered(
            f"the {STUDY_NAME!r} identity registration cannot serve purpose "
            f"{purpose!r}: {_FORBIDDEN_PURPOSES[key]}. {STUDY_STATUS}")
    return key


# ---------------------------------------------------------------------------
# the common pipeline - identical physics for every arm
# ---------------------------------------------------------------------------
PIPELINE = (
    "common physical opportunities -> controller proposal -> common physical "
    "resolver -> accepted actions")

# What every arm receives identically.  A controller may rank, size, accept or
# reject inside this set; it may never enlarge it.
OPPORTUNITY_INVARIANTS = (
    "the same initial physical state and the same current physical state "
    "(one frozen WorldState, one spec digest, checked by apply_joint)",
    "the same demand events (one DemandSchedule, generated once and replayed; "
    "never regenerated per arm)",
    "the same topology and edge availability (one frozen Topology digest)",
    "the same physical action types (a non-negative transfer quantity on an "
    "out-edge of the controller's own source, and nothing else)",
    "the same hard feasibility rules (0 <= x <= K on the JOINT increment, "
    "world.hard_feasible; violation is impossibility, not undesirability)",
    "the same continuous feasible quantity set per edge, [0, c_e], with the "
    "same joint cap - the interval is identical, only the point chosen in it "
    "differs between arms",
    "the same physical permission and shared-source resolver "
    "(world.resolve_shared_source, the committed P1C proportional rule), with "
    "the same budget rule and no arm seeing the budget",
    "the same tick schedule, tolerances and record format",
)


class _TypedView:
    """Base of the typed controller projections.

    Every projection is a frozen dataclass whose declared fields are exactly
    what its controller family may read.  Anything undeclared is
    STRUCTURALLY ABSENT - there is no attribute to read and no promise not to
    read one - and `__getattr__` turns an attempt into a loud refusal rather
    than an `AttributeError` a rule might quietly swallow.
    """

    def __getattr__(self, name: str):
        raise proto.LocalityViolation(
            f"{type(self).__name__} carries no {name!r}. A typed projection "
            f"exposes exactly the quantities its controller family's declared "
            f"formula consumes; everything else is absent by construction, "
            f"not by convention.")


@dataclass(frozen=True)
class C0View(_TypedView):
    """C0's projection: edge identifiers only, no physical quantity at all.

    C0 proposes zero unconditionally, so it consumes nothing but the edges it
    must name.  It cannot read a stock, a band, a demand or a cap: its
    independence from its input is structural rather than promised.
    """
    tick: int
    source: str
    out_edges: tuple


@dataclass(frozen=True)
class C1View(_TypedView):
    """C1's projection: own stock, this tick's demand, the common caps.

    No neighbour stock, no band, no reserve, no weight, no edge parameter.
    """
    tick: int
    source: str
    out_edges: tuple
    source_stock: float
    demand_here: Mapping        # edge -> quantity demanded THIS tick
    edge_caps: Mapping          # edge -> common opportunity cap c_e
    source_cap: float


@dataclass(frozen=True)
class C2View(_TypedView):
    """C2's projection: identical FIELDS to C1's, a different rule.

    C2 needed the destination hard headroom in the earlier draft.  Under Q-3's
    resolution that headroom is part of the COMMON cap `c_e`, so C2 no longer
    reads `K_j` or any neighbour stock: the hard physical law is applied once,
    for every arm, by `common_opportunities`.  C1 and C2 therefore differ in
    what they DO with the same information, never in what they receive - which
    is precisely the contrast the pair is meant to isolate.
    """
    tick: int
    source: str
    out_edges: tuple
    source_stock: float
    demand_here: Mapping
    edge_caps: Mapping
    source_cap: float


@dataclass(frozen=True)
class C3View(_TypedView):
    """C3's projection: band edges and states, and nothing of the field.

    Carries the source's own lower band `L_i`, each destination's stock and
    its declared `L_j`/`U_j`, the common caps and this tick's demand.

    It carries NO `alpha`, `beta`, `chi`, no `mu`, no `f_e` and no edge
    conductance or threshold: a C3 rule cannot evaluate the field because the
    quantities are not present, not because it promises not to.

    It DOES carry each destination's homeostatic reserve coordinate `R_j`
    (`NodeSpec.reserve`), because nothing else in the pipeline protects it.
    P1C's `R_eff` is a PROVIDER/EXPORT FLOOR on what a source may send; it does
    not implement the homeostatic reserve condition at any node, and no
    resolver moves resource toward a destination that is below `R`.  What C3
    does NOT carry is `R_eff` itself, its own reserve coordinate, or the
    provider budget: its own floor is the lower band `L_i`, and its export
    permission is the provider's business, decided after it proposes.
    """
    tick: int
    source: str
    out_edges: tuple
    source_stock: float
    source_lower: float                 # L_i
    endpoint_stocks: Mapping            # j -> x_j
    endpoint_lower: Mapping             # j -> L_j
    endpoint_upper: Mapping             # j -> U_j
    endpoint_reserve: Mapping           # j -> R_j (homeostatic, NOT R_eff)
    demand_here: Mapping
    edge_caps: Mapping
    source_cap: float
    eta: float                          # for the dimensional conversions only
    dt: float


@dataclass(frozen=True)
class C4View(_TypedView):
    """C4's projection: everything the committed local law needs, and no more.

    The endpoint `NodeSpec`s are the permitted endpoint views of Lemma 6.6,
    granted through this same common context - never through a private channel.
    It still carries no global `V`, no full state vector, no future demand, no
    oracle and no other arm's outcome: those are absent from
    `CommonLocalContext` itself, so no projection can expose them.
    """
    tick: int
    source: str
    out_edges: tuple
    source_stock: float
    source_spec: object                 # world.NodeSpec: alpha, beta, chi, L, U, R, K
    endpoint_stocks: Mapping
    endpoint_specs: Mapping             # j -> world.NodeSpec
    edge_specs: Mapping                 # e -> world.EdgeSpec: M_e, theta_e
    demand_here: Mapping
    edge_caps: Mapping
    source_cap: float
    eta: float
    dt: float


@dataclass(frozen=True)
class CommonLocalContext:
    """ONE immutable record of all local physical information at a decision.

    This is the single origin of every arm's view, and it is deliberately NOT
    the controller API.  Arms receive typed projections derived from it
    (`project`), so three different things stay separately recordable:

      1. what is PRESENT in the common context;
      2. what each typed projection EXPOSES;
      3. what each candidate formula actually CONSUMES.

    `information_ledger()` reports all three side by side.  Collapsing them is
    how an informational asymmetry hides: a field that is merely "available
    but unused" is indistinguishable, in a declaration, from one a rule
    silently reads.

    Every projection originates from the same frozen state, topology, current
    demand reveal, node specs, edge specs, common opportunity set and physical
    epoch - all carried here and all covered by the two digests.
    """
    tick: int
    source: str
    source_stock: float
    source_spec: object                 # world.NodeSpec
    out_edges: tuple
    endpoint_stocks: Mapping
    endpoint_specs: Mapping             # j -> world.NodeSpec  (closes G-2)
    edge_specs: Mapping                 # e -> world.EdgeSpec  (closes G-1)
    demand_here: Mapping                # edge -> quantity demanded THIS tick
    eta: float
    dt: float
    spec_digest: str
    state_digest: str

    def __post_init__(self):
        for edge in self.out_edges:
            if edge[0] != self.source:
                raise proto.LocalityViolation(
                    f"edge {edge!r} does not leave source {self.source!r}; a "
                    f"context may not reach beyond its own decision location")
            if edge[1] not in self.endpoint_stocks \
                    or edge[1] not in self.endpoint_specs:
                raise proto.LocalityViolation(
                    f"no permitted endpoint view for {edge[1]!r}; Lemma 6.6's "
                    f"endpoint views must be complete or the context is not a "
                    f"faithful projection")
        for edge in self.demand_here:
            if edge not in self.out_edges:
                raise proto.LocalityViolation(
                    f"demand on {edge!r} is not this source's to see")
        if self.eta <= 0.0:
            raise proto.ProtocolError("eta must be positive")
        if self.dt <= 0.0:
            raise proto.ProtocolError("dt must be positive")

    def demand_on(self, edge) -> float:
        """This tick's demanded QUANTITY on one edge; 0.0 where none was revealed."""
        return float(self.demand_here.get(edge, 0.0))

    # -- typed projections --------------------------------------------------
    def project(self, family: str):
        """The typed view for one controller family. The ONLY controller API."""
        try:
            builder = _PROJECTIONS[family]
        except KeyError:
            raise proto.NotPreregistered(
                f"no typed projection for family {family!r}; declared "
                f"projections are {sorted(_PROJECTIONS)}") from None
        return builder(self)

    def _opportunity(self) -> "OpportunitySet":
        return common_opportunities(self)

    def _c0(self) -> C0View:
        return C0View(tick=self.tick, source=self.source,
                      out_edges=self.out_edges)

    def _c1(self) -> C1View:
        opp = self._opportunity()
        return C1View(tick=self.tick, source=self.source,
                      out_edges=self.out_edges,
                      source_stock=self.source_stock,
                      demand_here=dict(self.demand_here),
                      edge_caps=dict(opp.edge_caps), source_cap=opp.source_cap)

    def _c2(self) -> C2View:
        opp = self._opportunity()
        return C2View(tick=self.tick, source=self.source,
                      out_edges=self.out_edges,
                      source_stock=self.source_stock,
                      demand_here=dict(self.demand_here),
                      edge_caps=dict(opp.edge_caps), source_cap=opp.source_cap)

    def _c3(self) -> C3View:
        opp = self._opportunity()
        return C3View(
            tick=self.tick, source=self.source, out_edges=self.out_edges,
            source_stock=self.source_stock,
            source_lower=self.source_spec.lower,
            endpoint_stocks=dict(self.endpoint_stocks),
            endpoint_lower={j: spec.lower
                            for j, spec in self.endpoint_specs.items()},
            endpoint_upper={j: spec.upper
                            for j, spec in self.endpoint_specs.items()},
            endpoint_reserve={j: spec.reserve
                              for j, spec in self.endpoint_specs.items()},
            demand_here=dict(self.demand_here),
            edge_caps=dict(opp.edge_caps), source_cap=opp.source_cap,
            eta=self.eta, dt=self.dt)

    def _c4(self) -> C4View:
        opp = self._opportunity()
        return C4View(
            tick=self.tick, source=self.source, out_edges=self.out_edges,
            source_stock=self.source_stock, source_spec=self.source_spec,
            endpoint_stocks=dict(self.endpoint_stocks),
            endpoint_specs=dict(self.endpoint_specs),
            edge_specs=dict(self.edge_specs),
            demand_here=dict(self.demand_here),
            edge_caps=dict(opp.edge_caps), source_cap=opp.source_cap,
            eta=self.eta, dt=self.dt)


_PROJECTIONS = {
    "C0": CommonLocalContext._c0, "C1": CommonLocalContext._c1,
    "C2": CommonLocalContext._c2, "C3": CommonLocalContext._c3,
    "C4": CommonLocalContext._c4,
}


def build_common_context(spec, state, source: str, tick: int,
                         schedule) -> CommonLocalContext:
    """Project one frozen world and state down to ONE source's common context.

    Takes no controller and no arm label, so the context - and therefore every
    projection derived from it - cannot depend on who will read it.  Only the
    endpoints of the source's own out-edges are exposed, so the context does
    not widen into a global read as the topology grows.

    Refuses when an out-edge carries no declared `EdgeSpec`: that is blocking
    gap G-1 surfacing as a missing parameter rather than as an invented
    default.  A world that declares none simply supports no law that needs
    `M_e` or `theta_e`.
    """
    validate_study_configuration(spec)
    out_edges = spec.topology.out_edges(source)
    missing = tuple(e for e in out_edges if e not in spec.edge_specs)
    if missing:
        raise proto.NotPreregistered(
            f"edges {missing} carry no declared EdgeSpec (M_e, theta_e). The "
            f"schema exists (world.EdgeSpec) but the values are unfilled "
            f"preregistration slots; supplying a default here would author "
            f"two scientific parameters. See blocking gap G-1.")
    return CommonLocalContext(
        tick=tick, source=source, source_stock=state.values[source],
        source_spec=spec.node_specs[source], out_edges=out_edges,
        endpoint_stocks={e[1]: state.values[e[1]] for e in out_edges},
        endpoint_specs={e[1]: spec.node_specs[e[1]] for e in out_edges},
        edge_specs={e: spec.edge_specs[e] for e in out_edges},
        demand_here={d.edge: d.quantity for d in schedule.at_tick(tick)
                     if d.edge[0] == source},
        eta=spec.eta, dt=spec.dt,
        spec_digest=spec.digest, state_digest=state.digest)


@dataclass(frozen=True)
class OpportunitySet:
    """The policy-independent candidate opportunities for ONE source, ONE tick.

    Derived from the world, the frozen state and the revealed demand ONLY.  No
    controller identity, arm label or decision rule enters its construction -
    which is what makes "every arm receives the same opportunities" a checkable
    statement rather than a promise.
    """
    tick: int
    source: str
    edge_caps: Mapping          # e -> upper end of the continuous feasible set
    source_cap: float           # joint hard cap on the sum of quantities
    derivation: str             # how each bound was computed, policy-free

    def __post_init__(self):
        if not str(self.derivation).strip():
            raise proto.NotPreregistered(
                "an opportunity set must declare its derivation; an "
                "underived candidate set cannot be shown to be "
                "policy-independent")
        for edge, cap in self.edge_caps.items():
            if not (isinstance(edge, tuple) and len(edge) == 2):
                raise proto.ProtocolError(f"malformed edge {edge!r}")
            if edge[0] != self.source:
                raise proto.LocalityViolation(
                    f"edge {edge!r} does not leave source {self.source!r}")
            if isinstance(cap, bool) or not isinstance(cap, (int, float)) \
                    or cap < 0.0:
                raise proto.ProtocolError(
                    f"cap on {edge!r} must be a non-negative real")
        if isinstance(self.source_cap, bool) \
                or not isinstance(self.source_cap, (int, float)) \
                or self.source_cap < 0.0:
            raise proto.ProtocolError("source_cap must be a non-negative real")

    @property
    def edges(self) -> tuple:
        return tuple(sorted(self.edge_caps))

    def feasible_interval(self, edge) -> tuple:
        """The continuous feasible quantity set on one edge: [0, c_e]."""
        if edge not in self.edge_caps:
            raise proto.LocalityViolation(
                f"{edge!r} carries no candidate opportunity this tick")
        return (0.0, float(self.edge_caps[edge]))


def require_within_opportunity(controller_id: str, proposal: Mapping,
                               opportunity: OpportunitySet) -> Mapping:
    """Refuse a proposal that leaves the common opportunity set.

    This is the mechanism behind "a controller may rank, size, accept or reject
    common opportunities, but must not create physical opportunities
    unavailable to other arms".  It is applied to EVERY arm with the same
    opportunity object, so it cannot be a check that only the comparators face.
    """
    if not isinstance(proposal, Mapping):
        raise proto.ProtocolError(f"{controller_id}: proposal must be a mapping")
    total = 0.0
    for edge, q in proposal.items():
        if edge not in opportunity.edge_caps:
            raise proto.LocalityViolation(
                f"{controller_id} proposed on {edge!r}, which carries no "
                f"candidate opportunity this tick; an arm may choose within "
                f"the common set, never enlarge it")
        if isinstance(q, bool) or not isinstance(q, (int, float)) or q < 0.0:
            raise proto.ProtocolError(
                f"{controller_id}: quantity on {edge!r} must be a "
                f"non-negative real")
        lo, hi = opportunity.feasible_interval(edge)
        if q > hi:
            raise proto.LocalityViolation(
                f"{controller_id} proposed {q} on {edge!r}, outside the common "
                f"continuous feasible set [{lo}, {hi}]")
        total += q
    if total > opportunity.source_cap:
        raise proto.LocalityViolation(
            f"{controller_id} proposed {total} in aggregate, outside the "
            f"common joint cap {opportunity.source_cap}; the joint bound is "
            f"physical and is not an arm's to widen")
    return dict(proposal)


def common_opportunities(context) -> OpportunitySet:
    """Derive the common opportunity set for ONE source at ONE tick.

    **Policy-independent by signature.**  It takes a `CommonLocalContext` and
    nothing else: no controller, no arm label, no decision rule, no proposal,
    no potential, no marginal, no force, no score and no future demand.  There
    is no parameter through which an arm's identity could enter, which is what
    makes "every arm receives the same opportunities" checkable.

    **Q-1, resolved: opportunities are demand-triggered and demand-bounded.**
    The study asks how local policies decide among the SAME externally
    presented service opportunities, so an edge carrying no current demand is
    not an opportunity in this study:

        d_e(t) = 0  =>  c_e(t) = 0,      and always  c_e(t) <= d_e(t).

    Autonomous field-driven rebalancing where no external service opportunity
    exists is a different scientific question and belongs to a separately
    registered future study; it is not mixed into this comparison.  The rule
    binds every arm, including C4, and is applied here - before any
    controller-specific logic runs.

    **Q-3, resolved: hard capacity is common physical feasibility.**  The
    destination's hard headroom is applied here rather than left to each arm,
    so no arm gains or loses by having been coded to rediscover a physical
    law, and an arm that ignores it does not crash its own tick into INVALID.

    The per-edge headroom `[K_j - x_j]_+ / eta` used here is exact for an
    isolated incoming transfer with no same-tick outgoing action at `j`.  It is
    NOT the general law, and it is not treated as final: `world.hard_feasible`
    re-checks the full joint successor (`world.joint_successor`) on the
    accepted vector, and destination contention between several sources fails
    closed in `world.require_resolved_destination_contention`.

    Units: every bound returned is a finite QUANTITY for this tick, matching
    demand events and stocks.
    """
    if not isinstance(context, CommonLocalContext):
        raise proto.ProtocolError(
            "common_opportunities takes a CommonLocalContext and nothing "
            "else; accepting a controller, an arm label or a proposal would "
            "make the opportunity set policy-dependent")
    caps = {}
    for edge in context.out_edges:
        demanded = context.demand_on(edge)
        if demanded <= 0.0:
            caps[edge] = 0.0                       # Q-1: no demand, no opportunity
            continue
        destination = edge[1]
        headroom = max(context.endpoint_specs[destination].capacity
                       - context.endpoint_stocks[destination], 0.0)
        caps[edge] = min(demanded, headroom / context.eta)   # Q-1 and Q-3
    # The joint bound is the source's own hard domain: it cannot send more than
    # it holds.  The PROVIDER budget is deliberately NOT folded in - invariant
    # 7 keeps it invisible to every arm and applies it in the common resolver.
    return OpportunitySet(
        tick=context.tick, source=context.source, edge_caps=caps,
        source_cap=max(context.source_stock, 0.0),
        derivation=OPPORTUNITY_DERIVATION)


OPPORTUNITY_DERIVATION = (
    "policy-independent. c_e = 0 where d_e(t) = 0 (Q-1: this study compares "
    "decisions over the SAME externally presented service opportunities); "
    "otherwise c_e = min( d_e(t), [K_j - x_j]_+ / eta ) (Q-1's demand bound "
    "and Q-3's common hard-capacity clamp). Joint cap = the source's own "
    "stock. Derived from frozen state, topology, node specs and this tick's "
    "revealed demand only - no controller, arm, proposal, V, mu, f_e, future "
    "demand or score enters. The per-edge headroom is exact for an isolated "
    "incoming transfer; world.hard_feasible re-checks the full joint "
    "successor, and multi-source destination contention fails closed."
)


# ---------------------------------------------------------------------------
# the three-way information ledger - present / exposed / consumed
# ---------------------------------------------------------------------------
# Recording these separately is the point.  "The field exists but this
# controller promises not to read it" is not a structural guarantee; "the
# field is not on this controller's view object" is.  The middle column is
# checked against the dataclass fields themselves, so a projection cannot
# drift from what it claims to expose.
CONTEXT_CONTENTS = (
    "tick", "source", "source_stock", "source_spec (K, L, U, R, alpha, beta, "
    "chi)", "out_edges", "endpoint_stocks", "endpoint_specs (K, L, U, R, "
    "alpha, beta, chi per destination)", "edge_specs (M_e, theta_e)",
    "demand_here (THIS tick only)", "eta", "dt", "spec_digest", "state_digest",
)

FORMULA_CONSUMPTION = {
    "C0": ("out_edges (to name the edges it zeroes)",),
    "C1": ("source_stock x_i", "demand_here d_e", "edge_caps c_e"),
    "C2": ("source_stock x_i", "edge_caps c_e (which already carries the "
           "demand bound and the common hard-capacity clamp)"),
    "C3": ("source_stock x_i", "source_lower L_i", "endpoint_stocks x_j",
           "endpoint_reserve R_j (the HOMEOSTATIC reserve coordinate, not "
           "R_eff)", "endpoint_lower L_j", "endpoint_upper U_j",
           "demand_here d_e", "edge_caps c_e", "eta"),
    "C4": ("source_stock x_i", "source_spec (alpha, beta, chi, L, U, R)",
           "endpoint_stocks x_j", "endpoint_specs (alpha, beta, chi, L, U, R)",
           "edge_specs (M_e, theta_e)", "edge_caps c_e (as a CAP only)",
           "eta", "dt"),
}

# Quantities that must be structurally ABSENT from a projection, per family.
FORBIDDEN_ON_VIEW = {
    "C0": ("source_stock", "demand_here", "edge_caps", "endpoint_stocks",
           "source_spec", "endpoint_specs", "edge_specs"),
    "C1": ("endpoint_stocks", "endpoint_specs", "source_spec", "edge_specs"),
    "C2": ("endpoint_stocks", "endpoint_specs", "source_spec", "edge_specs"),
    # C3 DOES read the destination homeostatic reserve R_j - the provider
    # floor R_eff does not implement it, so nothing else would. It still reads
    # no field quantity and no potential weight.
    "C3": ("source_spec", "endpoint_specs", "edge_specs", "alpha", "beta",
           "chi", "mu", "f_e", "R_eff", "budget", "source_reserve"),
    "C4": ("global_V", "future_demand", "oracle", "other_arm_result"),
}


def information_ledger() -> Mapping:
    """Present in the context / exposed by the view / consumed by the formula.

    The middle column is read off the projection dataclass itself rather than
    restated, so the ledger cannot claim an exposure the type does not have.
    """
    return {
        "present_in_common_context": CONTEXT_CONTENTS,
        "per_family": {
            family: {
                "exposed_by_typed_view": tuple(sorted(
                    _PROJECTION_TYPES[family].__dataclass_fields__)),
                "consumed_by_formula": FORMULA_CONSUMPTION[family],
                "structurally_absent": FORBIDDEN_ON_VIEW[family],
            } for family in sorted(FORMULA_CONSUMPTION)
        },
    }


_PROJECTION_TYPES = {"C0": C0View, "C1": C1View, "C2": C2View,
                     "C3": C3View, "C4": C4View}


# ---------------------------------------------------------------------------
# multi-source blockers - both fail closed, neither is silently resolved
# ---------------------------------------------------------------------------
# The topology restriction lives in the WORLD layer and is validated at
# CONFIGURATION time (`world.require_single_source_destinations`), so a
# violating topology fails closed before any controller exists.  Re-exported
# here because it is a CANDIDATE FIRST-STUDY design choice owned by this study,
# not a property of the physics.
destination_in_degrees = world.destination_in_degrees
require_single_source_destinations = world.require_single_source_destinations
SINGLE_SOURCE_RESTRICTION = world.SINGLE_SOURCE_RESTRICTION


def validate_study_configuration(spec) -> Mapping:
    """Validate a candidate study world BEFORE any controller is constructed.

    Fails closed on anything that would otherwise survive to `apply_joint` and
    be recorded as an INVALID run, which would mis-attribute a configuration
    error to a controller's outcome.  Checked here:

    * the candidate single-source-destination restriction `indegree(j) <= 1`,
      a property of the CONFIGURED TOPOLOGY itself, not of which edges happen
      to be active in a given tick (G-3 / G-4);
    * the candidate nested boundary ordering `0 <= R <= L <= U <= K`, which
      committed authority does NOT guarantee and which the three-stage C3
      semantics require;
    * the conservative domain the study declares (`eta = 1`, no loss sink);
    * that every edge carries its declared `EdgeSpec` (G-1's values).

    Every one is a PROSPECTIVE FIRST-STUDY DOMAIN RESTRICTION: none is a
    universal EBU theorem, a claim about future worlds, or a frozen
    preregistration parameter, and none fixes a numeric value.

    Returns a record of what was validated.  Passing is NOT approval of the
    world: the world instance itself remains preregistration slot S-W.
    """
    degrees = world.require_single_source_destinations(spec)
    boundaries = world.require_nested_boundaries(spec)
    if not spec.is_conservative:
        raise proto.NotPreregistered(
            f"the {STUDY_NAME!r} declares a CONSERVATIVE world (eta = 1, no "
            f"loss sink); this spec declares eta = {spec.eta!r}, loss_sink "
            f"{spec.loss_sink!r}. A lossy world is a different study and must "
            f"represent loss as a declared coordinate or boundary crossing.")
    missing = tuple(sorted(e for e in spec.topology.edges
                           if e not in spec.edge_specs))
    if missing:
        raise proto.NotPreregistered(
            f"edges {missing} carry no declared EdgeSpec (M_e, theta_e); the "
            f"schema exists but the values are unfilled slots (G-1)")
    return {"study": STUDY_NAME, "validated": "configuration only",
            "is_approval": False, "is_preregistration": False,
            "is_universal_theorem": False,
            "destination_in_degrees": degrees,
            "node_boundaries_R_L_U_K": boundaries,
            "single_source_restriction": world.SINGLE_SOURCE_RESTRICTION,
            "node_boundary_ordering": world.NODE_BOUNDARY_ORDERING,
            "conservative": spec.is_conservative,
            "eta": spec.eta}


# ---------------------------------------------------------------------------
# candidate reference arithmetic - NOT executable arms
# ---------------------------------------------------------------------------
# These functions exist for ONE purpose: so that every illustrative worked
# example below is DERIVED from the declared symbolic rule instead of being
# hand-fitted to a desired answer.  They are pure arithmetic on individual
# synthetic states.  None of them is a controller: `build()` still has no
# success path, nothing here is registered as an arm, and no runner can reach
# them.  The symbolic rule determines the fixture; the fixture never
# determines the rule.
# ---------------------------------------------------------------------------
def capped_max_min_water_fill(available: float, caps: Mapping) -> Mapping:
    """`W_e(B; b) = min(b_e, lambda)`, the exact capped max-min water-fill.

    `lambda >= 0` is the water level satisfying

        sum_e min(b_e, lambda)  =  min( B, sum_e b_e )

    computed in closed form from the sorted cap multiset - never by search,
    bisection or iteration to a tolerance.

    **Every edge case is specified, not left to the arithmetic:**

    | case | result | why |
    |---|---|---|
    | `B = 0` | every edge 0 | the level solves `m * lambda = 0`, so `lambda = 0` |
    | empty edge set | `{}` | `sum_e b_e = 0 <= B`, the saturating branch, vacuously |
    | all caps 0 | every edge 0 | `sum_e b_e = 0 <= B`, so each edge gets its cap, which is 0 |
    | `B >= sum_e b_e` | every edge its full cap | `lambda = +inf`; nothing is withheld |
    | `B < sum_e b_e` | `min(b_e, lambda)`, `lambda` unique | the strictly-binding case |

    **Order independence is a property of the continuous rule, not of the
    implementation.**  `W` is a symmetric function of the cap MULTISET, so
    equal caps receive equal quantities and any permutation of the edges gives
    the identical allocation.  Nothing in the continuous rule consults an edge
    identifier.

    **Finite-precision and discrete residuals.**  In exact arithmetic the
    allocation already sums to `min(B, sum_e b_e)` and no residual exists.  A
    residual can only appear if a caller rounds or discretises the result
    afterwards.  Such a caller must settle it by a declared deterministic key -
    **destination node id ascending** - and that key may ONLY move a residual
    between edges that the continuous rule has already tied.  It must never
    change the continuous allocation itself, and it depends on no EBU
    quantity, no `mu`, no `f_e`, no controller outcome and no future
    information.  This function performs no rounding and therefore reaches no
    tie-break.

    Units: `available` and every cap are finite SOURCE-SIDE QUANTITIES for one
    tick, and so is every returned value.
    """
    if isinstance(available, bool) or not isinstance(available, (int, float)) \
            or available < 0.0:
        raise proto.ProtocolError("available quantity must be a non-negative real")
    for edge, cap in caps.items():
        if isinstance(cap, bool) or not isinstance(cap, (int, float)) or cap < 0.0:
            raise proto.ProtocolError(f"cap on {edge!r} must be a non-negative real")
    total = sum(caps.values())
    # Saturating branch: covers the empty edge set and all-caps-zero, both of
    # which have total = 0 <= available, and every edge receives its own cap.
    if available >= total:
        return {edge: float(cap) for edge, cap in caps.items()}
    ordered = sorted(caps.values())
    m, prefix, level = len(ordered), 0.0, 0.0
    for k, cap in enumerate(ordered):
        candidate = (available - prefix) / (m - k)
        if candidate <= cap:
            level = candidate
            break
        prefix += cap
    else:                                   # pragma: no cover - total > available
        level = ordered[-1]
    return {edge: min(float(cap), level) for edge, cap in caps.items()}


def water_fill_budget_ledger(available: float, stage_caps: Sequence) -> Mapping:
    """Run the recursive stage budgets and report each one, for review.

        B^(1) = A_i
        B^(k+1) = [ A_i - sum_{s<=k} sum_e q_e^(s) ]_+
        q^(k) = W( B^(k) ; caps_k )

    Pure. Returns each stage's budget, allocation and served total, plus the
    grand total, so budget conservation is checkable stage by stage rather
    than only at the end.
    """
    stages, served_so_far = [], 0.0
    for index, caps in enumerate(stage_caps, start=1):
        budget = max(available - served_so_far, 0.0)
        allocation = capped_max_min_water_fill(budget, caps)
        served = sum(allocation.values())
        if served > budget + 1e-12:
            raise proto.ProtocolError(
                f"stage {index} allocated {served} against budget {budget}")
        served_so_far += served
        stages.append({"stage": index, "budget": budget, "caps": dict(caps),
                       "allocation": allocation, "served": served})
    if served_so_far > available + 1e-12:
        raise proto.ProtocolError(
            f"stages allocated {served_so_far} against A_i = {available}")
    return {"available": available, "stages": tuple(stages),
            "total": served_so_far}


def c0_candidate_proposal(view: C0View) -> Mapping:
    """C0: propose zero on every out-edge, unconditionally."""
    return {edge: 0.0 for edge in view.out_edges}


def c1_candidate_proposal(view: C1View) -> Mapping:
    """C1: equal split of own stock, capped by demand and the common cap."""
    asking = tuple(e for e in view.out_edges if view.demand_here.get(e, 0.0) > 0.0)
    if not asking or view.source_stock <= 0.0:
        return {}
    share = view.source_stock / len(asking)
    return {e: min(view.demand_here[e], share, view.edge_caps[e]) for e in asking}


def c2_candidate_proposal(view: C2View) -> Mapping:
    """C2: the service-maximal vector, scaled proportionally to the common caps.

    Under Q-3's resolution the common cap `c_e` already carries both the demand
    bound and the destination's hard headroom, so C2's own rule reduces to
    "ask for the whole opportunity, and scale down proportionally if the source
    cannot cover it".
    """
    caps = {e: view.edge_caps[e] for e in view.out_edges
            if view.edge_caps.get(e, 0.0) > 0.0}
    total = sum(caps.values())
    if not caps or total <= 0.0 or view.source_stock <= 0.0:
        return {}
    scale = min(1.0, view.source_stock / total)
    return {e: cap * scale for e, cap in caps.items()}


def c3_candidate_proposal(view: C3View) -> Mapping:
    """C3: THREE-STAGE reserve-and-band-aware non-field control.

    Lexicographic, in three passes over ONE band-safe source quantity
    `A_i = [x_i - L_i]_+`:

        stage 1  homeostatic reserve emergencies at destinations
        stage 2  remaining lower-band deficits at destinations
        stage 3  ordinary service, capped at the destination upper band

    The source-side budget protects C3's own LOWER BAND.  The destination-side
    priorities protect the destinations' RESERVE first, then their band.  The
    provider/export floor `R_eff` is a separate, common P1C restriction applied
    later by the resolver; it protects export permission and does NOT implement
    the homeostatic reserve condition `R`, which is why C3 carries `R_j`
    itself.

    Uses no `mu`, no `f_e`, no `alpha`, no `beta`, no `chi`.
    """
    return c3_candidate_stages(view)["proposal"]


def c3_candidate_stages(view: C3View) -> Mapping:
    """C3's proposal with every intermediate quantity, for author review.

    Units: `A_i`, every cap and every `q` is a finite QUANTITY for this tick.
    `eta_e` is dimensionless, so `[R_j - x_j]_+ / eta_e` converts a
    DESTINATION-side shortfall into the SOURCE-side quantity that closes it -
    the division is the efficiency correction, not a unit change.
    """
    eta = view.eta
    available = max(view.source_stock - view.source_lower, 0.0)      # A_i

    def water_fill_stage(remaining, caps):
        allocated = capped_max_min_water_fill(remaining, caps)
        return allocated, sum(allocated.values())

    # -- stage 1: destination homeostatic RESERVE emergencies ---------------
    stage1_caps = {}
    for edge in view.out_edges:
        destination = edge[1]
        deficit = max(view.endpoint_reserve[destination]
                      - view.endpoint_stocks[destination], 0.0) / eta
        stage1_caps[edge] = min(view.demand_here.get(edge, 0.0),
                                view.edge_caps.get(edge, 0.0), deficit)
    stage1, served1 = water_fill_stage(available, stage1_caps)

    # -- stage 2: remaining destination LOWER-BAND deficits ------------------
    remaining2 = max(available - served1, 0.0)
    stage2_caps = {}
    for edge in view.out_edges:
        destination = edge[1]
        done = stage1[edge]
        deficit = max(view.endpoint_lower[destination]
                      - view.endpoint_stocks[destination] - eta * done,
                      0.0) / eta
        stage2_caps[edge] = min(
            max(view.demand_here.get(edge, 0.0) - done, 0.0),
            max(view.edge_caps.get(edge, 0.0) - done, 0.0),
            deficit)
    stage2, served2 = water_fill_stage(remaining2, stage2_caps)

    # -- stage 3: ordinary service, inside the destination UPPER band --------
    remaining3 = max(available - served1 - served2, 0.0)
    stage3_caps = {}
    for edge in view.out_edges:
        destination = edge[1]
        done = stage1[edge] + stage2[edge]
        headroom = max(view.endpoint_upper[destination]
                       - view.endpoint_stocks[destination] - eta * done,
                       0.0) / eta
        stage3_caps[edge] = min(
            max(view.demand_here.get(edge, 0.0) - done, 0.0),
            max(view.edge_caps.get(edge, 0.0) - done, 0.0),
            headroom)
    stage3, _served3 = water_fill_stage(remaining3, stage3_caps)

    proposal = {e: stage1[e] + stage2[e] + stage3[e] for e in view.out_edges}
    total = sum(proposal.values())
    if total > available + 1e-12:               # the rule's own invariant
        raise proto.ProtocolError(
            f"C3 proposed {total} against band-safe availability {available}; "
            f"the three-stage rule must never exceed A_i")
    return {"available": available,
            "stage1_caps": stage1_caps, "stage1": stage1,
            "served_stage1": served1,
            "available_stage2": remaining2,
            "stage2_caps": stage2_caps, "stage2": stage2,
            "served_stage2": served2,
            "available_stage3": remaining3,
            "stage3_caps": stage3_caps, "stage3": stage3,
            "proposal": {e: q for e, q in proposal.items() if q > 0.0},
            "total": total}


def c4_candidate_proposal(view: C4View) -> Mapping:
    """C4: the committed local law, reused and not re-derived.

    `mu` comes from `d0_v29.marginal`; `f_e = mu_i - eta mu_j`;
    `J_e = M_e [f_e - theta_e]_+` is a RATE, so the tick quantity is
    `q_e = dt * J_e` (`world.tick_quantity_from_rate`), clipped to the common
    cap and renormalised if the source cannot cover the total.
    """
    return c4_candidate_detail(view)["proposal"]


def c4_candidate_detail(view: C4View) -> Mapping:
    """C4's proposal together with every intermediate quantity, for review."""
    import d0_v29

    def mu_of(spec, x):
        return d0_v29.marginal(spec.alpha, spec.beta, spec.chi,
                               spec.lower, spec.upper, spec.reserve, x)

    mu_source = mu_of(view.source_spec, view.source_stock)
    force, flux, raw = {}, {}, {}
    for edge in view.out_edges:
        destination = edge[1]
        mu_destination = mu_of(view.endpoint_specs[destination],
                               view.endpoint_stocks[destination])
        espec = view.edge_specs[edge]
        f = mu_source - view.eta * mu_destination
        j = espec.conductance * max(f - espec.threshold, 0.0)
        force[edge], flux[edge] = f, j
        raw[edge] = min(world.tick_quantity_from_rate(j, view.dt),
                        view.edge_caps.get(edge, 0.0))
    total = sum(raw.values())
    if total > view.source_stock and total > 0.0:
        scale = view.source_stock / total
        proposal = {e: q * scale for e, q in raw.items()}
    else:
        proposal = dict(raw)
    return {"mu_source": mu_source,
            "mu_endpoints": {e[1]: mu_of(view.endpoint_specs[e[1]],
                                         view.endpoint_stocks[e[1]])
                             for e in view.out_edges},
            "force": force, "flux": flux, "raw": raw,
            "proposal": {e: q for e, q in proposal.items() if q > 0.0},
            "total": sum(proposal.values())}


CANDIDATE_RULES = {
    "C0": c0_candidate_proposal, "C1": c1_candidate_proposal,
    "C2": c2_candidate_proposal, "C3": c3_candidate_proposal,
    "C4": c4_candidate_proposal,
}


# ---------------------------------------------------------------------------
# can the common P1C resolver still bind after C3 proposes?  YES.
# ---------------------------------------------------------------------------
P1C_BINDING_ANALYSIS = (
    "DERIVED FROM THE FORMULAS, not assumed. C3 guarantees only "
    "sum_e q_e^C3 <= A_i = [x_i - L_i]_+ (source-side quantity). The "
    "committed P1C budget as a QUANTITY is "
    "dt * [ (x - eps_x) + dt(u - eps_u) - R_eff ]_+ / dt "
    "= [ (x - eps_x) + dt(u - eps_u) - R_eff ]_+, and with the first study's "
    "u = 0 this is [ x_i - eps_x - dt*eps_u - R_eff ]_+. "
    "sigma = 1 would be GUARANTEED only if A_i <= budget for every admissible "
    "state, i.e. (for x_i > L_i) only if "
    "L_i >= R_eff + eps_x + dt*eps_u. "
    "NO SUCH ORDERING IS DECLARED. The candidate domain restriction orders "
    "0 <= R <= L <= U <= K and DELIBERATELY EXCLUDES R_eff, because R_eff is a "
    "provider/export floor and not a homeostatic boundary of the node. "
    "Therefore sigma < 1 is reachable and q_e^accepted = sigma * q_e^C3. "
    "CONSEQUENCES, which must not be overstated away: "
    "(a) C3's three-stage ordering is a PROPOSAL-LEVEL lexicographic "
    "priority only; "
    "(b) the common resolver scales the whole vector PROPORTIONALLY and is "
    "stage-blind, so proportional scaling may leave Stage-1 reserve deficits "
    "INCOMPLETELY SERVED while Stage-3 ordinary service still executes; "
    "(c) the accepted vector is NOT proven lexicographically saturated, and "
    "no realised reserve-first or lower-band-first saturation is claimed. "
    "P1C is NOT modified to preserve C3's preference ordering."
)

OPPORTUNITY_CAP_IS_NOT_P1C_SAFE = (
    "The common opportunity layer does NOT expose a P1C-safe joint quantity "
    "cap before proposal. `common_opportunities` sets source_cap = x_i, the "
    "source's own HARD domain bound, and OPPORTUNITY_INVARIANTS item 7 keeps "
    "the provider budget invisible to every arm. C3 therefore cannot and does "
    "not clamp itself to the P1C budget, and later scaling can still occur. "
    "The proposal -> resolver order is unchanged: a controller proposes "
    "without seeing the budget, and the common resolver then decides."
)


def p1c_tick_budget_quantity(*, stock: float, R_eff: float, dt: float,
                             eps_x: float = 0.0, eps_u: float = 0.0,
                             u: float = 0.0) -> float:
    """The committed robust budget, converted to a tick QUANTITY. Pure.

    Reproduces `p1c_v29.robust_budget`'s formula - a RATE - and converts it
    with `world.tick_quantity_from_rate`, so the rate/quantity boundary is
    crossed exactly once and in the open.

    `R_eff` is the PROVIDER/EXPORT reserve floor and is a STOCK QUANTITY (the
    same units as `stock`), not a rate; the division by `dt` is what makes the
    returned BUDGET a rate. `R_eff` is not `NodeSpec.reserve` (`R`) and does
    not implement any node's homeostatic reserve condition.

    **APPLICABILITY WARNING - this helper reproduces ARITHMETIC ONLY.**  The
    committed formula it mirrors is `p1c_v29.robust_budget`, whose own
    docstring states that it "assumes the caller has already classified the
    source as State P and typed it regenerative".  This helper performs
    NEITHER check.  The complete committed permission policy is
    `p1c_v29._source_budget`, which returns ZERO for `finite` and
    `irreversible` stock sources and for States R and I, and reserves the
    robust budget for `regenerative` State-P sources alone.  The candidate
    world declares NO regeneration in its plant (identity clause 3), so under
    a faithful reading of committed P1C its export budget is ZERO and this
    helper's positive output has NO committed permission basis.  It is retained
    for unit-conversion demonstration only.  See
    `V3.0_DESIGN_READINESS_NOTE_C4_DEGENERACY_AND_P1C_APPLICABILITY.md`
    finding 2.
    """
    rate = max((stock - eps_x) + dt * (u - eps_u) - R_eff, 0.0) / dt
    return world.tick_quantity_from_rate(rate, dt)


def p1c_binding_demonstration() -> Mapping:
    """A pure demonstration that P1C can still bind after C3's three stages.

    ILLUSTRATIVE_FIXTURE_ONLY.  Constructs one candidate-domain world in which
    `R_eff > L_i`, runs C3's declared rule, applies the committed resolver, and
    reports that a Stage-1 RESERVE deficit is left incompletely served while
    Stage-3 ordinary service still executes.  No tick, no trajectory.
    """
    boundaries = {                 # (K, L, U, R, alpha, beta, chi)
        "i": (20.0, 4.0, 16.0, 2.0, 1.0, 1.0, 1.0),
        "j1": (20.0, 8.0, 16.0, 6.0, 1.0, 1.0, 1.0),
        "j2": (20.0, 4.0, 16.0, 2.0, 1.0, 1.0, 1.0),
    }
    topology = world.Topology(("i", "j1", "j2"), (("i", "j1"), ("i", "j2")))
    spec = world.WorldSpec(
        spec_id="ILLUSTRATIVE_FIXTURE_ONLY", spec_version="0",
        topology=topology,
        node_specs={n: world.NodeSpec(n, *boundaries[n]) for n in boundaries},
        eta=1.0, dt=1.0, path_semantics="model_realised_constant_rate",
        edge_specs={e: world.EdgeSpec(e, 1.0, 0.0) for e in topology.edges})
    state = world.WorldState(spec.digest, {"i": 14.0, "j1": 0.0, "j2": 12.0})
    schedule = world.DemandSchedule(
        "ILLUSTRATIVE_FIXTURE_ONLY", "illustrative-fixture", 1,
        (world.DemandEvent(0, ("i", "j1"), 6.0),
         world.DemandEvent(0, ("i", "j2"), 4.0)))
    context = build_common_context(spec, state, "i", 0, schedule)
    detail = c3_candidate_stages(context.project("C3"))

    R_eff = 9.0                    # ILLUSTRATIVE ONLY; note R_eff > L_i = 4
    budget = p1c_tick_budget_quantity(stock=state.values["i"], R_eff=R_eff,
                                      dt=spec.dt)
    outcome = world.resolve_shared_source("i", detail["proposal"], budget)
    reserve_need = max(spec.node_specs["j1"].reserve - state.values["j1"], 0.0)
    reserve_served = outcome.accepted.get(("i", "j1"), 0.0)
    stage3_served = outcome.accepted.get(("i", "j2"), 0.0)
    return {
        "label": FIXTURE_LABEL,
        "L_i": spec.node_specs["i"].lower, "R_eff": R_eff,
        "R_eff_exceeds_L_i": R_eff > spec.node_specs["i"].lower,
        "available_A_i": detail["available"],
        "proposal": detail["proposal"], "proposal_total": detail["total"],
        "budget_quantity": budget, "sigma": outcome.sigma,
        "accepted": dict(outcome.accepted),
        "stage1_reserve_need_at_j1": reserve_need,
        "stage1_reserve_actually_served": reserve_served,
        "stage1_reserve_cleared": reserve_served >= reserve_need,
        "stage3_ordinary_service_still_executed": stage3_served,
        "lexicographically_saturated": False,
        "reading": (
            "sigma < 1, so the accepted vector is the PROPOSAL scaled "
            "proportionally. The resolver is stage-blind: it cannot know that "
            "part of the vector was a reserve emergency. j1's Stage-1 reserve "
            "deficit is left incompletely served while j2 still receives "
            "Stage-3 ordinary service into a node already inside its band. "
            "C3's ordering is therefore a proposal-level priority, not a "
            "realised one."),
    }


# ---------------------------------------------------------------------------
# illustrative fixtures - observable dimensions, reported separately
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class FixtureOutcome:
    """What ONE arm does on ONE illustrative fixture. No winner, by construction.

    Every observable dimension is its own field, and there is deliberately no
    aggregate, no score, no rank and no comparison field.  Collapsing these
    into a single verdict would require a definition of dominance over
    REGISTERED scientific metrics, and no scientific metric is registered
    anywhere in this study: slot S-M is unfilled.  "Delivered more" and
    "ended further inside the band" are different axes, and a fixture that
    reported a winner would be asserting a preference between them that no
    author has made.

    Every number here is `ILLUSTRATIVE_FIXTURE_ONLY`.
    """
    fixture: str
    arm: str
    demanded: float
    opportunity_caps: Mapping
    proposal: Mapping
    budget: float
    sigma: float
    accepted: Mapping            # SOURCE-SIDE sent quantities
    delivered_per_edge: Mapping  # DESTINATION-SIDE: eta * accepted
    pre_state: Mapping
    post_state: Mapping
    delivered: float             # DESTINATION-SIDE total
    sent: float                  # SOURCE-SIDE total
    physically_valid: bool
    physical_validity_detail: str
    conservation_residual: float
    v_pre: float
    v_post: float
    delta_v: float
    reserve_membership: Mapping
    band_membership: Mapping
    lower_band_violations: tuple
    upper_band_violations: tuple
    reserve_violations: tuple
    label: str = FIXTURE_LABEL

    def __post_init__(self):
        if self.label != FIXTURE_LABEL:
            raise proto.NotPreregistered(
                f"a fixture outcome must be labelled {FIXTURE_LABEL}")

    def lines(self) -> tuple:
        """The dimensions, one per line, in a fixed order and never merged."""
        def fmt(mapping):
            return "{" + ", ".join(
                f"{k[1] if isinstance(k, tuple) else k}: {v:g}"
                for k, v in sorted(mapping.items(),
                                   key=lambda kv: str(kv[0]))) + "}"

        def fmt_member(mapping):
            return "{" + ", ".join(f"{k}: {v}" for k, v in
                                   sorted(mapping.items())) + "}"
        return (
            f"opportunity caps c_e = {fmt(self.opportunity_caps)} (source-side)",
            f"proposal q = {fmt(self.proposal) if self.proposal else '{} (none)'}"
            f" (source-side sent)",
            f"resolver: budget {self.budget:g}, sigma {self.sigma:g}, "
            f"accepted {fmt(self.accepted) if self.accepted else '{} (none)'}"
            f" (source-side sent)",
            f"delivered per edge eta*q = "
            f"{fmt(self.delivered_per_edge) if self.delivered_per_edge else '{} (none)'}"
            f" (destination-side)",
            f"pre-state {fmt(self.pre_state)}",
            f"post-state {fmt(self.post_state)}",
            f"sent {self.sent:g} (source-side); delivered {self.delivered:g} "
            f"(destination-side) of {self.demanded:g} demanded",
            f"physical validity: "
            f"{'VALID' if self.physically_valid else 'INVALID'} "
            f"({self.physical_validity_detail}); conservation residual "
            f"{self.conservation_residual:.3e}",
            f"potential V: pre {self.v_pre:g}, post {self.v_post:g}, "
            f"delta {self.delta_v:+g}",
            f"reserve membership: {fmt_member(self.reserve_membership)}",
            f"band membership: {fmt_member(self.band_membership)}",
            f"lower-band violations: {self.lower_band_violations or 'none'}",
            f"upper-band violations: {self.upper_band_violations or 'none'}",
            f"reserve violations: {self.reserve_violations or 'none'}",
        )


def evaluate_fixture(context: CommonLocalContext, family: str, *,
                     budget: float, fixture: str, arm: str) -> FixtureOutcome:
    """Run ONE arm's declared arithmetic on ONE fixture context. Pure.

    Advances no model state and calls no transition function: it derives a
    proposal, applies the committed proportional resolver, and computes the
    arithmetic successor of that single hypothetical transfer directly.  No
    tick is planned or executed, `apply_joint` is never called, no trajectory
    is produced, and nothing is recorded as a result.

    Sides are kept apart throughout: `accepted` is SOURCE-SIDE sent quantity,
    `delivered_per_edge` is DESTINATION-SIDE `eta * accepted`, the source loses
    the full sent quantity and each destination gains `eta * q`.
    """
    import d0_v29

    view = context.project(family)
    proposal = CANDIDATE_RULES[family](view)
    proposal = {e: q for e, q in proposal.items() if q > 0.0}
    opportunity = common_opportunities(context)
    require_within_opportunity(arm, proposal, opportunity)
    outcome = world.resolve_shared_source(context.source, proposal, budget)
    accepted = {e: q for e, q in outcome.accepted.items() if q > 0.0}
    delivered_per_edge = {e: world.delivered_from_sent(q, context.eta)
                          for e, q in accepted.items()}

    pre = {context.source: context.source_stock}
    pre.update(dict(context.endpoint_stocks))
    post = dict(pre)
    post[context.source] -= sum(accepted.values())          # full sent leaves
    for edge, q in delivered_per_edge.items():
        post[edge[1]] += q                                  # eta * q arrives

    specs = dict(context.endpoint_specs)
    specs[context.source] = context.source_spec

    # Physical validity: the hard domain on the JOINT successor, plus exact
    # conservation in this conservative (eta = 1) domain.
    outside = tuple(f"{n} ({post[n]:g} outside [0, {specs[n].capacity:g}])"
                    for n in sorted(post)
                    if not specs[n].in_hard_domain(post[n]))
    residual = abs(sum(post.values()) - sum(pre.values())) if context.eta == 1.0 \
        else abs((sum(post.values()) - sum(pre.values()))
                 + (1.0 - context.eta) * sum(accepted.values()))
    valid = not outside and residual <= 1e-12
    detail = ("joint successor inside every hard domain; conservation exact"
              if valid else
              f"hard-domain violation {outside}" if outside else
              f"conservation residual {residual:.3e}")

    # Committed potential, reused and not re-derived - the same
    # `d0_v29.penalty` that `ebu_test_settlement.potential` sums, applied to
    # exactly the nodes this local context covers. The field only EVALUATES
    # what the physical layer did; it never moved any of it (Principle A).
    def burden(node_spec, value):
        return d0_v29.penalty(node_spec.alpha, node_spec.beta, node_spec.chi,
                              node_spec.lower, node_spec.upper,
                              node_spec.reserve, value)

    v_pre = sum(burden(specs[n], pre[n]) for n in sorted(pre))
    v_post = sum(burden(specs[n], post[n]) for n in sorted(post))

    low, high, reserve = [], [], []
    band_member, reserve_member = {}, {}
    for node in sorted(post):
        spec, value = specs[node], post[node]
        band_member[node] = "in band" if spec.in_homeostatic_band(value) \
            else ("below L" if value < spec.lower else "above U")
        reserve_member[node] = "below R" if spec.below_reserve(value) \
            else "at or above R"
        if value < spec.lower:
            low.append(f"{node} ({value:g} < L={spec.lower:g})")
        if value > spec.upper:
            high.append(f"{node} ({value:g} > U={spec.upper:g})")
        if value < spec.reserve:
            reserve.append(f"{node} ({value:g} < R={spec.reserve:g})")
    return FixtureOutcome(
        fixture=fixture, arm=arm,
        demanded=sum(context.demand_here.values()),
        opportunity_caps=dict(opportunity.edge_caps), proposal=proposal,
        budget=float(budget), sigma=outcome.sigma, accepted=accepted,
        delivered_per_edge=delivered_per_edge,
        pre_state=pre, post_state=post,
        delivered=sum(delivered_per_edge.values()),
        sent=sum(accepted.values()),
        physically_valid=valid, physical_validity_detail=detail,
        conservation_residual=residual,
        v_pre=v_pre, v_post=v_post, delta_v=v_post - v_pre,
        reserve_membership=reserve_member, band_membership=band_member,
        lower_band_violations=tuple(low), upper_band_violations=tuple(high),
        reserve_violations=tuple(reserve))


# The two illustrative fixtures.  ILLUSTRATIVE_FIXTURE_ONLY: no parameter,
# preregistration, evidence or authority status; none may enter the candidate
# study configuration.  Fixture A is the case where a straightforward
# comparator does well; fixture B is the case where the field's behaviour is
# visible.  BOTH are retained: a fixture family containing only one of them
# would be a rigged demonstration, and no fixture is selected for which
# controller it flatters.
_FIXTURE_NODES = ("i", "j1", "j2")
_FIXTURE_EDGES = (("i", "j1"), ("i", "j2"))


def _fixture_spec():
    node = lambda n: world.NodeSpec(node_id=n, capacity=20.0, lower=4.0,
                                    upper=16.0, reserve=2.0,
                                    alpha=1.0, beta=1.0, chi=1.0)
    topology = world.Topology(_FIXTURE_NODES, _FIXTURE_EDGES)
    return world.WorldSpec(
        spec_id="ILLUSTRATIVE_FIXTURE_ONLY", spec_version="0",
        topology=topology, node_specs={n: node(n) for n in _FIXTURE_NODES},
        eta=1.0, dt=1.0, path_semantics="model_realised_constant_rate",
        edge_specs={e: world.EdgeSpec(edge=e, conductance=1.0, threshold=0.0)
                    for e in _FIXTURE_EDGES})


def fixture_context(stocks: Mapping, demand: Mapping) -> CommonLocalContext:
    """Build one illustrative decision context. Pure; constructs no runner."""
    spec = _fixture_spec()
    state = world.WorldState(spec.digest, dict(stocks))
    schedule = world.DemandSchedule(
        "ILLUSTRATIVE_FIXTURE_ONLY", "illustrative-fixture", 1,
        tuple(world.DemandEvent(0, e, q) for e, q in sorted(demand.items())))
    return build_common_context(spec, state, "i", 0, schedule)


FIXTURES = {
    "A": {"title": "fixture A (ample stock)",
          "stocks": {"i": 10.0, "j1": 3.0, "j2": 15.0},
          "demand": {("i", "j1"): 6.0, ("i", "j2"): 6.0},
          "budget": 8.0},
    "B": {"title": "fixture B (scarcity, asymmetric demand)",
          "stocks": {"i": 3.0, "j1": 3.0, "j2": 1.0},
          "demand": {("i", "j1"): 2.0, ("i", "j2"): 10.0},
          "budget": 1.0},
}

# The budget figures above are an ARBITRARY ILLUSTRATIVE NUMBER, carried only
# so the fixtures show the resolver stage doing something visible.  They are
# NOT derived from R, and they are NOT a claim about what the provider layer
# would permit.
FIXTURE_BUDGET_READING = (
    "ILLUSTRATIVE_FIXTURE_ONLY: the per-fixture B_i is an arbitrary "
    "illustrative source-side QUANTITY, shown only so the resolver stage is "
    "visible. It is NOT computed from the homeostatic reserve coordinate R, "
    "and citing it as 'the reserve budget' would be exactly the R_eff/R "
    "conflation this study forbids. The authoritative provider budget is "
    "p1c_v29.robust_budget - a RATE, converted with tick_quantity_from_rate - "
    "computed from the PROVIDER/EXPORT FLOOR R_eff. R_eff is not R, does not "
    "implement R at any node, and moves nothing toward a destination below R. "
    "R_eff's value is an unfilled preregistration parameter. Because the "
    "fixture budgets happen to exceed C3's A_i, sigma = 1 for C3 on BOTH "
    "fixtures - a property of these numbers, NOT a guarantee; "
    "p1c_binding_demonstration() exhibits sigma < 1."
)


def fixture_outcome(fixture_key: str, family: str, arm: str) -> FixtureOutcome:
    """One arm's outcome on one illustrative fixture, derived from its rule."""
    fixture = FIXTURES[fixture_key]
    context = fixture_context(fixture["stocks"], fixture["demand"])
    return evaluate_fixture(context, family, budget=fixture["budget"],
                            fixture=fixture["title"], arm=arm)


# ---------------------------------------------------------------------------
# controller drafts
# ---------------------------------------------------------------------------
CANDIDATE_UNAPPROVED = "CANDIDATE_UNAPPROVED"
AUTHOR_ACCEPTED = "AUTHOR_ACCEPTED"
STATUS_VOCABULARY = (CANDIDATE_UNAPPROVED, AUTHOR_ACCEPTED)


@dataclass(frozen=True)
class WorkedExample:
    """One hand-worked example. Every number in it is a fixture, not a value."""
    title: str
    given: str
    steps: tuple
    result: str
    reading: str
    label: str = FIXTURE_LABEL

    def __post_init__(self):
        if self.label != FIXTURE_LABEL:
            raise proto.NotPreregistered(
                f"a worked example's numbers must be labelled "
                f"{FIXTURE_LABEL}; they have no parameter, preregistration or "
                f"authority status and must not enter the candidate study "
                f"configuration")
        if not self.steps:
            raise proto.NotPreregistered(
                f"{self.title}: a worked example must show its steps")


@dataclass(frozen=True)
class ControllerDraft:
    """One candidate controller, with every disclosure the review needs.

    The fields are not documentation for its own sake: each is a thing a
    reviewer must be able to check independently before the controller can be
    preregistered as a fair comparator rather than a strawman (design
    section 27).
    """
    controller_id: str
    family: str
    decision_formula: str            # 1. exact symbolic decision formula
    information_available: tuple     # 2. exact information available
    candidate_logic: str             # 3. ranking / sizing / accept / reject
    tie_breaking: str                # 4. deterministic ordering and ties
    no_feasible_action: str          # 5. handling when nothing is feasible
    information_use: Mapping         # 6. use / non-use of L,U,R,mu,f_e,...
    resolver_interaction: str        # 7. interaction with the common resolver
    proof_no_global_V: str           # 8. cannot access global V
    proof_no_future_demand: str      # 9. cannot access future demand
    proof_no_oracle_or_arms: str     # 10. no oracle, no other arm's outcome
    config_to_preregister: tuple     # 11. every configuration value needed
    worked_examples: tuple           # 12. at least two, hand-worked
    anti_strawman: str               # 13. could a researcher genuinely use it
    # comparison-table disclosures
    added_information: str
    informational_asymmetry: str
    decision_power: str
    quantity_freedom: str
    credibility: str
    # opportunity-set conformance
    same_action_set_as_ebu: str
    use_of_L_U_R: str
    status: str = CANDIDATE_UNAPPROVED

    def __post_init__(self):
        if self.family not in proto.CONTROLLER_FAMILIES:
            raise proto.NotPreregistered(f"unknown family {self.family!r}")
        if self.status not in STATUS_VOCABULARY:
            raise proto.NotPreregistered(
                f"{self.controller_id}: status must be one of "
                f"{STATUS_VOCABULARY}")
        for name in ("decision_formula", "candidate_logic", "tie_breaking",
                     "no_feasible_action", "resolver_interaction",
                     "proof_no_global_V", "proof_no_future_demand",
                     "proof_no_oracle_or_arms", "anti_strawman",
                     "added_information", "informational_asymmetry",
                     "decision_power", "quantity_freedom", "credibility",
                     "same_action_set_as_ebu", "use_of_L_U_R"):
            if not str(getattr(self, name)).strip():
                raise proto.NotPreregistered(
                    f"{self.controller_id}: {name} must be declared; an "
                    f"undeclared comparator cannot be shown not to be a "
                    f"strawman (design section 27)")
        missing = tuple(sorted(set(_INFORMATION_SYMBOLS)
                               - set(self.information_use)))
        if missing:
            raise proto.NotPreregistered(
                f"{self.controller_id}: use or non-use of {missing} is "
                f"undeclared; silence about an input is not a statement that "
                f"it is unused")
        if len(self.worked_examples) < 2:
            raise proto.NotPreregistered(
                f"{self.controller_id}: at least two hand-worked examples are "
                f"required")
        if not self.config_to_preregister:
            raise proto.NotPreregistered(
                f"{self.controller_id}: the configuration values that must "
                f"later be preregistered must be listed; an empty list would "
                f"claim the controller needs no preregistered choice")

    @property
    def approved(self) -> bool:
        return self.status == AUTHOR_ACCEPTED

    def declaration(self) -> Mapping:
        return {
            "study": STUDY_NAME, "status": self.status,
            "identity": identity_record(),
            "controller_id": self.controller_id, "family": self.family,
            "decision_formula": self.decision_formula,
            "information_available": self.information_available,
            "candidate_logic": self.candidate_logic,
            "tie_breaking": self.tie_breaking,
            "no_feasible_action": self.no_feasible_action,
            "information_use": dict(self.information_use),
            "resolver_interaction": self.resolver_interaction,
            "proof_no_global_V": self.proof_no_global_V,
            "proof_no_future_demand": self.proof_no_future_demand,
            "proof_no_oracle_or_arms": self.proof_no_oracle_or_arms,
            "config_to_preregister": self.config_to_preregister,
            "worked_examples": tuple(e.title for e in self.worked_examples),
            "worked_example_label": FIXTURE_LABEL,
            "anti_strawman": self.anti_strawman,
            "added_information": self.added_information,
            "informational_asymmetry": self.informational_asymmetry,
            "decision_power": self.decision_power,
            "quantity_freedom": self.quantity_freedom,
            "credibility": self.credibility,
            "same_action_set_as_ebu": self.same_action_set_as_ebu,
            "use_of_L_U_R": self.use_of_L_U_R,
            "pipeline": PIPELINE,
        }


# The quantities every draft must speak to, one way or the other.
_INFORMATION_SYMBOLS = ("L", "U", "R", "mu", "f_e", "demand", "neighbour_state",
                        "reserve_information")

# The information set is identical for all five drafts, and it is exactly what
# `proto.LocalView` exposes today. Stating it once makes any divergence between
# a draft and the enforced boundary visible - including the two gaps G-1 and
# G-2 below, where a draft needs MORE than the view currently carries.
def _exposed(family: str) -> tuple:
    """What a family's typed projection actually exposes, read off the type.

    Declared this way so a draft cannot claim an information set the
    projection does not have: the tuple IS the dataclass's fields.
    """
    return tuple(sorted(_PROJECTION_TYPES[family].__dataclass_fields__))


C0_INFORMATION = (
    "C0View: edge identifiers only. No stock, no band, no demand, no cap, no "
    "neighbour state, no parameter of any kind is present on the object.",
    f"exposed fields: {_exposed('C0')}",
)
C1_INFORMATION = (
    "C1View: own stock x_i, this tick's demand d_e, and the common "
    "opportunity caps c_e with their joint bound. No neighbour stock, no "
    "band, no reserve, no weight, no edge parameter.",
    f"exposed fields: {_exposed('C1')}",
)
C2_INFORMATION = (
    "C2View: identical FIELDS to C1View. Under Q-3's resolution the "
    "destination hard headroom is carried inside the common cap c_e, so C2 no "
    "longer reads K_j or any neighbour stock; C1 and C2 differ in rule, never "
    "in information.",
    f"exposed fields: {_exposed('C2')}",
)
C3_INFORMATION = (
    "C3View: own stock x_i and own lower band L_i; each destination's stock "
    "x_j and its declared homeostatic boundaries R_j, L_j, U_j; this tick's "
    "demand; the common caps; eta and dt for the efficiency conversions. "
    "R_j is the HOMEOSTATIC RESERVE COORDINATE (NodeSpec.reserve), which the "
    "provider floor R_eff does not implement and which nothing else in the "
    "pipeline protects. NO alpha, beta, chi, NO mu, NO f_e, NO edge "
    "conductance or threshold, and NO sight of R_eff or the provider budget - "
    "each structurally absent from the projection, not merely unread.",
    f"exposed fields: {_exposed('C3')}",
)
C4_INFORMATION = (
    "C4View: own stock and own full NodeSpec (alpha, beta, chi, L, U, R, K); "
    "each destination's stock and full NodeSpec, which is what mu_j requires; "
    "the per-edge EdgeSpec (M_e, theta_e); this tick's demand; the common "
    "caps; eta and dt. Granted through the SAME CommonLocalContext as every "
    "other arm - there is no private channel.",
    f"exposed fields: {_exposed('C4')}",
)

# Retained for the disclosures that speak about the common context as a whole
# rather than about one projection.
LOCAL_INFORMATION = (
    "own source stock x_i",
    "own NodeSpec: capacity K_i, band L_i/U_i, reserve R_i, weights",
    "own out-edges",
    "endpoint stock of each own out-edge destination",
    "demand revealed at THIS tick on own out-edges",
)

_NO_GLOBAL_V = (
    "Structural. The controller receives only a `proto.LocalView`, whose "
    "`__getattr__` refuses every undeclared attribute; there is no field "
    "carrying V, no full state vector and no accessor that could compute one. "
    "Negative control NC10 asserts that reading 'global_V' raises "
    "LocalityViolation. Global V is computed only by the evaluator, after "
    "execution."
)
_NO_FUTURE = (
    "Structural. The view carries `demand_here`, built by "
    "`proto.build_local_view` from `DemandSchedule.at_tick(t)` for the current "
    "t only. `DemandSchedule` exposes no `future()`, no slicing and no "
    "`__getitem__`. Negative control NC11 asserts the view carries only this "
    "tick's demand."
)
_NO_ORACLE = (
    "Structural. `LocalView` has no oracle, arm, result or score field, and "
    "`__getattr__` refuses any such read. The `FeasibilityOracle` is "
    "constructed by the evaluator and is never passed to `plan_tick`, which "
    "takes only (spec, state, tick, schedule, controller, budgets). Arms are "
    "planned against the SAME frozen pre-state, so no arm's outcome exists "
    "when another proposes; `ArmResult` and `OracleResult` are assembled after "
    "execution and flow only into `conclude_claim`."
)
_SAME_ACTIONS = (
    "Yes. Every controller proposes non-negative quantities on its own "
    "out-edges and nothing else; `DeclaredController.propose` refuses a "
    "proposal on any edge that is not an out-edge of its own source, and "
    "`require_within_opportunity` refuses a quantity outside the common "
    "continuous feasible set [0, c_e] or the common joint cap. All arms then "
    "pass through the SAME resolver (`world.resolve_shared_source`), so no arm "
    "can obtain a quantity another arm could not."
)


def _fixture_given(fixture_key: str) -> str:
    """The fixture's declared inputs, restated from the fixture itself."""
    fixture = FIXTURES[fixture_key]
    stocks = ", ".join(f"x_{n} = {v:g}"
                       for n, v in sorted(fixture["stocks"].items()))
    demand = ", ".join(f"d_{e[1]} = {q:g}"
                       for e, q in sorted(fixture["demand"].items()))
    return (f"{stocks}; {demand}; K = 20, L = 4, U = 16, R = 2; "
            f"alpha = beta = chi = 1; eta = 1, dt = 1, M_e = 1, theta_e = 0; "
            f"B_i = {fixture['budget']:g} ({FIXTURE_BUDGET_READING})")


def _derivation(fixture_key: str, family: str) -> tuple:
    """The rule-specific intermediate quantities, computed from the rule."""
    fixture = FIXTURES[fixture_key]
    context = fixture_context(fixture["stocks"], fixture["demand"])
    view = context.project(family)

    def fmt(mapping):
        return "{" + ", ".join(f"{k[1]}: {v:g}" for k, v in sorted(
            mapping.items(), key=lambda kv: str(kv[0]))) + "}"

    if family == "C0":
        return ("reads nothing; proposes 0 on every out-edge unconditionally",)
    if family == "C1":
        asking = [e for e in view.out_edges if view.demand_here.get(e, 0.0) > 0]
        return (f"edges with demand: {len(asking)}; equal share "
                f"x_i / n_i = {view.source_stock / max(len(asking), 1):g}",
                f"q_e = min(d_e, share, c_e) -> "
                f"{fmt(c1_candidate_proposal(view))}")
    if family == "C2":
        caps = {e: view.edge_caps[e] for e in view.out_edges
                if view.edge_caps.get(e, 0.0) > 0}
        total = sum(caps.values())
        return (f"common caps {fmt(caps)}, sum = {total:g} vs x_i = "
                f"{view.source_stock:g}",
                f"proportional scale min(1, x_i / sum c) = "
                f"{min(1.0, view.source_stock / total) if total else 1.0:g} -> "
                f"{fmt(c2_candidate_proposal(view))}")
    if family == "C3":
        d = c3_candidate_stages(view)
        return (f"band-safe source quantity A_i = [x_i - L_i]_+ = "
                f"{d['available']:g}  (source-side quantity)",
                f"B^(1) = A_i = {d['available']:g}; stage-1 RESERVE caps "
                f"r_e = min(d_e, c_e, [R_j - x_j]_+ / eta) = "
                f"{fmt(d['stage1_caps'])}",
                f"q^(1) = W(B^(1); r) = {fmt(d['stage1'])}, served "
                f"{d['served_stage1']:g}",
                f"B^(2) = [A_i - sum q^(1)]_+ = {d['available_stage2']:g}; "
                f"stage-2 LOWER-BAND caps l_e = {fmt(d['stage2_caps'])}",
                f"q^(2) = W(B^(2); l) = {fmt(d['stage2'])}, served "
                f"{d['served_stage2']:g}",
                f"B^(3) = [A_i - sum q^(1) - sum q^(2)]_+ = "
                f"{d['available_stage3']:g}; stage-3 UPPER-BAND caps "
                f"h_e = {fmt(d['stage3_caps'])}",
                f"q^(3) = W(B^(3); h) = {fmt(d['stage3'])}",
                f"q^C3 = q^(1) + q^(2) + q^(3) = {fmt(d['proposal'])}, total "
                f"{d['total']:g} <= A_i = {d['available']:g}")
    if family == "C4":
        d = c4_candidate_detail(view)
        return (f"mu_i = {d['mu_source']:g}; mu_j = " + "{" + ", ".join(
                    f"{n}: {v:g}" for n, v in sorted(d['mu_endpoints'].items()))
                + "}",
                f"f_e = mu_i - eta mu_j = {fmt(d['force'])}",
                f"J_e = M_e [f_e - theta_e]_+ = {fmt(d['flux'])} (a RATE)",
                f"q_e = min(dt * J_e, c_e) = {fmt(d['raw'])}",
                f"renormalised to x_i where needed -> {fmt(d['proposal'])}")
    raise proto.NotPreregistered(f"no derivation for family {family!r}")


def _example(fixture_key: str, family: str, arm: str, title: str,
             reading: str) -> WorkedExample:
    """A worked example DERIVED from the declared rule, never hand-fitted.

    The steps and the result are computed by running the family's declared
    symbolic rule on the fixture and reporting each observable dimension
    separately.  Only the `reading` is authored prose, and a reading that
    contradicted the computed dimensions would contradict numbers standing
    directly above it.
    """
    outcome = fixture_outcome(fixture_key, family, arm)
    return WorkedExample(
        title=title, given=_fixture_given(fixture_key),
        steps=_derivation(fixture_key, family) + outcome.lines(),
        result=" | ".join(outcome.lines()[3:]), reading=reading)


DRAFTS = (
    ControllerDraft(
        controller_id="C0-reject-all",
        family="C0",
        decision_formula=(
            "q_e^req(t) = 0 for every e in out(i), at every tick, "
            "unconditionally. No state, band, demand or field value enters."),
        information_available=C0_INFORMATION,
        candidate_logic=(
            "Rejection is total and unconditional: every candidate "
            "opportunity is rejected, none is ranked and none is sized. This "
            "is the only arm whose proposal is independent of its input."),
        tie_breaking=(
            "Vacuous - the map is constant, so no ordering is ever consulted. "
            "Declared explicitly so that 'no tie-break' is a statement rather "
            "than an omission."),
        no_feasible_action=(
            "Indistinguishable from its ordinary behaviour: it proposes zero "
            "whether or not anything is feasible. This is precisely why it is "
            "the sanity control - it is the fixed point of 'refuse "
            "everything', and the run label must never read SUCCESS for it."),
        information_use={
            "L": "not read", "U": "not read", "R": "not read",
            "mu": "not read", "f_e": "not read",
            "demand": "not read - revealed demand is ignored, not merely "
                      "unserved",
            "neighbour_state": "not read",
            "reserve_information": "not read; C0 protects the reserve as a "
                                   "side effect of doing nothing, which is "
                                   "exactly the confound it exists to expose",
        },
        resolver_interaction=(
            "Passes through the resolver like every other arm. With a total "
            "request of 0, sigma = 1 by the `total <= budget` branch and the "
            "accepted vector is 0. It is never exempted from the resolver: an "
            "arm that bypassed a common stage would not be a control."),
        proof_no_global_V=_NO_GLOBAL_V,
        proof_no_future_demand=_NO_FUTURE,
        proof_no_oracle_or_arms=_NO_ORACLE,
        config_to_preregister=(
            "nothing in the rule itself - it has no parameter",
            "its inclusion in the arm set (design section 27 requires it)",
            "the service floor below which NO arm may be labelled SUCCESS - "
            "a uniform criterion applied identically to every arm, never a "
            "rule about C0's identity (`ArmResult`, section 36)",
            "whether C0 is also run as the reference trajectory for the "
            "no-service viability baseline, or only as a control",
        ),
        worked_examples=(
            _example(
                "A", "C0", "C0-reject-all",
                "C0 under ample stock (fixture A)",
                "Zero is proposed without inspecting anything, so the state is "
                "exactly its pre-state. Perfect conservation, zero service, and "
                "j1 left at 3 - below L = 4 - for as long as C0 runs. This is "
                "the concrete content of 'trivial state preservation is not "
                "scientific success': the source's own position is untouched "
                "and the network's is abandoned."),
            _example(
                "B", "C0", "C0-reject-all",
                "C0 under scarcity (fixture B)",
                "Unchanged by the scarcity, as by everything else. j2 stays at "
                "1, below both its band and its reserve of 2, while the source "
                "holds stock that could have lifted it. C0 records what the "
                "viability metrics read when delivered service is zero, which "
                "is the only reason it is in the arm set."),
        ),
        anti_strawman=(
            "Not a policy anyone would deploy, and not offered as one. C0 is a "
            "CONTROL, and its scientific job is the opposite of winning: it "
            "measures what the viability metrics read when service is zero, so "
            "that any arm's viability score can be compared against the "
            "do-nothing floor. Removing it would let a cautious arm's "
            "viability advantage go unexplained. Design section 27 requires "
            "it. Section 36 then does the work UNIFORMLY: SUCCESS requires "
            "viability AND delivered service above the declared floor, and C0 "
            "fails that test because it delivers nothing - not because any "
            "rule names C0. No arm is granted or denied an outcome by its "
            "identity, and `ArmResult` carries no controller-specific branch: "
            "a C0-family arm that did meet both axes would record TARGET_MET "
            "like any other."),
        added_information=(
            "None - it is the bottom of the ladder. Every other arm adds to "
            "this baseline, and the C1 - C0 difference is the value of "
            "responding to demand at all."),
        informational_asymmetry=(
            "None in its favour. It reads strictly less than every other arm: "
            "nothing."),
        decision_power=(
            "Strictly least: a single point of the feasible set, the origin, "
            "chosen without reference to input."),
        quantity_freedom=(
            "Formally continuous like the others - it may choose any point of "
            "[0, c_e] - and it always chooses 0. The restriction is its rule, "
            "not its permission."),
        credibility=(
            "Credible as a control, not as a policy. It is the standard "
            "no-action baseline, and its presence is what makes 'EBU preserved "
            "homeostasis' a non-trivial claim."),
        same_action_set_as_ebu=_SAME_ACTIONS,
        use_of_L_U_R="None. C0 reads no band, no reserve and no field.",
    ),
    ControllerDraft(
        controller_id="C1-local-greedy",
        family="C1",
        decision_formula=(
            "Let D_i(t) = { e in out(i) : d_e(t) > 0 } and n_i(t) = |D_i(t)|. "
            "For e = (i,j) in D_i(t):  q_e^req = min( d_e(t), x_i / n_i(t), "
            "c_e ),  and q_e^req = 0 otherwise, where c_e is the common "
            "per-edge cap of the opportunity set. Equivalently: split the "
            "source's own stock equally among the edges asking for something, "
            "and never ask for more than was requested."),
        information_available=C1_INFORMATION,
        candidate_logic=(
            "No ranking: every candidate with positive demand is accepted for "
            "sizing, and sizing is an equal split of x_i. Rejection happens "
            "only where d_e = 0 or the common cap is 0. It does not compare "
            "edges against each other, which is exactly what distinguishes it "
            "from C2."),
        tie_breaking=(
            "The equal share x_i / n_i is symmetric across D_i(t), so equal "
            "demands receive equal requests and the rule is invariant to edge "
            "ordering. Where an explicit order is unavoidable (residual "
            "assignment under a declared rounding rule), sort by destination "
            "node id ascending - declared, deterministic, and independent of "
            "any field value. The same tie rule is used by all five arms."),
        no_feasible_action=(
            "If D_i(t) is empty, or x_i = 0, or every c_e = 0, it proposes the "
            "empty map; `plan_tick` builds no action and the tick records zero "
            "accepted quantity. It never falls back to an unrequested "
            "transfer, and it never retries."),
        information_use={
            "L": "not read", "U": "not read", "R": "not read",
            "mu": "not read", "f_e": "not read",
            "demand": "read, this tick only, as the per-edge upper bound d_e",
            "neighbour_state": "not read - the destination's stock does not "
                               "enter the rule; the only destination-dependent "
                               "term is the COMMON cap c_e, which every arm "
                               "receives identically",
            "reserve_information": "not read. It may export the source down to "
                                   "0 as far as its own rule is concerned; "
                                   "whether it actually can depends on the "
                                   "common budget rule (open question Q-2)",
        },
        resolver_interaction=(
            "Proposes only; the P1C proportional resolver may scale the "
            "request down by sigma = min(1, B_i / sum_e q_e^req). The "
            "controller never sees B_i, never learns sigma before the fact and "
            "never retries within the tick."),
        proof_no_global_V=_NO_GLOBAL_V,
        proof_no_future_demand=_NO_FUTURE,
        proof_no_oracle_or_arms=_NO_ORACLE,
        config_to_preregister=(
            "the share rule: equal split of the full stock x_i / n_i "
            "(drafted) versus an equal split of some declared band-safe "
            "quantity - the latter would make C1 a weak C3 rather than the "
            "band-blind baseline it is meant to be, and is NOT drafted",
            "whether n_i counts all out-edges or only those with d_e > 0 "
            "(drafted: only those with d_e > 0)",
            "the residual/rounding rule, if quantities are ever discretised",
            "the tie-break key (drafted: destination node id ascending)",
        ),
        worked_examples=(
            _example(
                "A", "C1", "C1-local-greedy",
                "C1 under ample stock (fixture A)",
                "The equal split asks for 5 on each edge; the provider budget "
                "binds at 8, so sigma = 0.8 and 4 is accepted on each. Two "
                "things the rule had no instrument to notice: the source ends "
                "at 2, below its own L = 4, and j2 is pushed to 19, above "
                "U = 16. Both are inside the hard domain, so this is "
                "undesirability rather than impossibility - and C1 reads "
                "neither band, so neither outcome is a failure of its rule so "
                "much as a demonstration of what the rule cannot see."),
            _example(
                "B", "C1", "C1-local-greedy",
                "C1 under scarcity and asymmetric demand (fixture B)",
                "The equal split ignores that e2 asked for five times as much "
                "AND that j2 is below its reserve; the budget then binds "
                "hard, and the single delivered unit is halved between the "
                "two destinations, leaving j2 at 1.5 and still under its "
                "reserve. C2 follows the demand shape here, C4 follows the "
                "deficit, and C3 declines entirely - four arms, four "
                "different reasons, on one fixture."),
        ),
        anti_strawman=(
            "Yes. 'Serve what is asked, split your stock evenly, never go "
            "negative' is the first rule a reasonable engineer writes for a "
            "distribution network, and it needs no knowledge of EBU. It is "
            "weak by design but not crippled: it respects hard feasibility and "
            "this tick's demand, which are the only things it is told about."),
        added_information=(
            "Over C0: this tick's demand, and the source's own stock. That is "
            "the whole addition - the C1 - C0 difference isolates the value of "
            "responding to demand at all."),
        informational_asymmetry=(
            "None. It is granted the same LocalView as every other arm and "
            "uses a strict subset of it. Unused availability is not an "
            "asymmetry; every arm could read what it declines to read."),
        decision_power=(
            "Same action space as every arm. Its effective reach is narrower "
            "only because the equal-split rule is a one-dimensional family "
            "inside the feasible set."),
        quantity_freedom=(
            "Continuous. It chooses a point in [0, c_e] per edge; it is not "
            "restricted to ranking a supplied menu."),
        credibility=(
            "Credible as the naive local baseline: it is what an "
            "implementation looks like before anyone has modelled viability. "
            "If EBU cannot beat this, nothing further needs testing."),
        same_action_set_as_ebu=_SAME_ACTIONS,
        use_of_L_U_R=(
            "None. This is the point of C1: it isolates how much of any EBU "
            "advantage comes merely from respecting declared bands."),
    ),
    ControllerDraft(
        controller_id="C2-myopic-service",
        family="C2",
        decision_formula=(
            "Maximise immediate delivered service subject to HARD physical "
            "feasibility alone. With per-edge hard caps c_e (demand and "
            "destination headroom) and the source's hard cap x_i: "
            "q_e^req = c_e * min( 1, x_i / sum_{e' in D_i} c_{e'} ), "
            "c_e = min( d_e(t), [K_j - x_j]_+ / eta ). No band, no reserve, no "
            "field, no lookahead. It is the solution of "
            "max sum_e q_e s.t. 0 <= q_e <= c_e, sum_e q_e <= x_i, with the "
            "demand-proportional selection among the optima."),
        information_available=C2_INFORMATION,
        candidate_logic=(
            "Accept every candidate with positive demand; size each at its "
            "hard cap, then scale the whole vector down proportionally if the "
            "source cannot cover the total. Ranking is implicit and by demand "
            "size: a larger request receives a proportionally larger share. "
            "Nothing is ever rejected for a homeostatic reason - only for a "
            "physical one."),
        tie_breaking=(
            "Proportional-to-cap scaling is order-invariant by construction, "
            "so no tie-break is reached in the continuous case; first-come "
            "allocation is explicitly NOT used, because it would make the "
            "result depend on edge ordering and would be gameable. Residual "
            "ordering, if ever needed, is by destination node id ascending - "
            "the same key as every other arm."),
        no_feasible_action=(
            "If sum_e c_e = 0 (no demand, or no headroom anywhere) or x_i = 0, "
            "it proposes the empty map. The proportional scale factor is "
            "defined as 1 when the denominator is 0, so the rule has no "
            "division-by-zero branch and no implicit fallback."),
        information_use={
            "L": "not read", "U": "not read",
            "R": "not read - deliberately. C2 may drive the source to 0 as far "
                 "as its own rule is concerned",
            "mu": "not read", "f_e": "not read",
            "demand": "read, this tick only; it is the objective AND the "
                      "per-edge bound",
            "neighbour_state": "NOT read. Under Q-3's resolution the "
                               "destination hard headroom is applied once, for "
                               "EVERY arm, inside the common cap c_e, so C2 "
                               "reads no neighbour stock at all: no arm gains "
                               "or loses by having been coded to rediscover a "
                               "hard physical law. The declared band is never "
                               "read",
            "reserve_information": "not read; the only reserve protection C2 "
                                   "experiences is whatever the common budget "
                                   "rule imposes (Q-2)",
        },
        resolver_interaction=(
            "Identical to C1: propose, then accept whatever the shared-source "
            "resolver permits. Because C2 requests the most, it is the arm "
            "most often scaled by sigma < 1, and the arm whose realised "
            "behaviour depends most on the budget rule."),
        proof_no_global_V=_NO_GLOBAL_V,
        proof_no_future_demand=_NO_FUTURE,
        proof_no_oracle_or_arms=_NO_ORACLE,
        config_to_preregister=(
            "the tie rule among service-optimal vectors: proportional-to-cap "
            "(drafted), proportional-to-demand, or max-min fair - these select "
            "different points of the same optimal face",
            "Q-3 is RESOLVED: the destination hard headroom belongs to the "
            "common opportunity set, not to C2's own rule, so C2's remaining "
            "choice is only how to distribute within the common caps",
            "whether service is measured as accepted, delivered or measured "
            "quantity (the QuantityLadder stage that the metric reads)",
        ),
        worked_examples=(
            _example(
                "A", "C2", "C2-myopic-service",
                "C2 under ample stock (fixture A)",
                "The common caps are (6, 5) - the demand bound and the "
                "destination hard headroom, both applied once for every arm - "
                "and C2 asks for the whole opportunity, scaled to what the "
                "source holds. Same TOTAL delivered as C1, distributed by cap "
                "rather than evenly: C1 and C2 coincide in volume whenever the "
                "binding constraint is the source, and are separated by SHAPE. "
                "j2 still ends above U, for the same reason as C1 - neither "
                "arm reads the band."),
            _example(
                "B", "C2", "C2-myopic-service",
                "C2 under scarcity and asymmetric demand (fixture B)",
                "C2 tracks the demand shape (5:1) exactly where C1 split "
                "evenly, so it happens to send more to the reserve-breaching "
                "node than C1 did - but only because that node ASKED for more, "
                "not because it is in trouble. Under mirrored demand it would "
                "do the opposite, which is precisely what distinguishes a "
                "service rule from a viability rule."),
        ),
        anti_strawman=(
            "Yes, and this is the strongest service comparator. 'Meet demand "
            "now, as fully as physics allows' is the default objective of most "
            "real dispatch systems, and on the service axis alone it is very "
            "hard to beat. If EBU cannot match it on service it must justify "
            "that on the viability axis - which is exactly the tradeoff "
            "section 36 requires to be reported on both axes."),
        added_information=(
            "Over C1: the relative sizes of the requests, and the "
            "destinations' hard headroom. It adds an objective (maximise "
            "delivered quantity) where C1 had only a heuristic."),
        informational_asymmetry=(
            "None. Same view; it reads the hard headroom that C1 declines to "
            "read, and neither reads the declared band."),
        decision_power=(
            "Same action space. It reaches the service-maximal face of the "
            "feasible set, which C1 generally does not."),
        quantity_freedom=(
            "Continuous, over the same [0, c_e] as every arm."),
        credibility=(
            "The most credible comparator on the service axis, and the one "
            "most likely to beat EBU there. Its presence is what stops a "
            "service loss being reported as a wash."),
        same_action_set_as_ebu=_SAME_ACTIONS,
        use_of_L_U_R=(
            "None, deliberately. C2 exists to show what happens when current "
            "service is maximised with no homeostatic guidance at all - "
            "including driving a destination above U or a source below R."),
    ),
    ControllerDraft(
        controller_id="C3-reserve-and-band-aware",
        family="C3",
        decision_formula=(
            "THREE-STAGE RESERVE-AND-BAND-AWARE NON-FIELD CONTROL, "
            "lexicographic, deterministic. UNITS: every symbol is a finite "
            "SOURCE-SIDE QUANTITY for the current tick except where stated; "
            "d_e is source-side requested transfer; eta_e is dimensionless, "
            "so a division by eta_e converts a DESTINATION-side shortfall into "
            "the source-side quantity that closes it. "
            "SOURCE-SIDE BAND-SAFE BUDGET:  A_i = [ x_i - L_i ]_+  - C3 never "
            "voluntarily takes its own source below its lower homeostatic "
            "band. STAGE BUDGETS, recursively: "
            "B_i^(1) = A_i ;  "
            "B_i^(2) = [ A_i - sum_e q_e^(1) ]_+ ;  "
            "B_i^(3) = [ A_i - sum_e q_e^(1) - sum_e q_e^(2) ]_+ . "
            "STAGE 1, destination homeostatic RESERVE emergencies: "
            "r_e = min( d_e, c_e, [R_j - x_j]_+ / eta_e ) ,  "
            "q^(1) = W(B_i^(1); r) . "
            "STAGE 2, remaining destination LOWER-BAND deficits: "
            "l_e = min( d_e - q_e^(1), c_e - q_e^(1), "
            "[L_j - x_j - eta_e q_e^(1)]_+ / eta_e ) ,  "
            "q^(2) = W(B_i^(2); l) . "
            "STAGE 3, ordinary service inside the destination UPPER band: "
            "h_e = min( d_e - q_e^(1) - q_e^(2), c_e - q_e^(1) - q_e^(2), "
            "[U_j - x_j - eta_e(q_e^(1) + q_e^(2))]_+ / eta_e ) ,  "
            "q^(3) = W(B_i^(3); h) . "
            "PROPOSAL  q_e^C3 = q_e^(1) + q_e^(2) + q_e^(3) , with "
            "sum_e q_e^C3 <= A_i by construction. "
            "W is exact capped max-min water-filling: W_e(B; b) = "
            "min(b_e, lambda) with sum_e min(b_e, lambda) = min(B, sum_e b_e); "
            "lambda = +inf when B >= sum_e b_e; every edge receives 0 when "
            "B = 0; the empty edge set and all-zero caps both return zero "
            "allocations through the saturating branch. "
            "Uses NO mu, NO f_e, NO alpha, NO beta, NO chi. "
            "R_j here is the HOMEOSTATIC RESERVE COORDINATE "
            "(NodeSpec.reserve); it is NOT P1C's provider/export floor R_eff, "
            "and R_eff does not implement it."),
        information_available=C3_INFORMATION,
        candidate_logic=(
            "Three lexicographic passes over ONE source-side budget A_i, each "
            "pass receiving what the previous passes did not spend. Pass one "
            "accepts only the part of a candidate that reduces a destination "
            "below its declared homeostatic RESERVE R_j. Pass two accepts the "
            "part that reduces a remaining deficit below L_j. Pass three "
            "accepts ordinary remaining demand, capped so no destination is "
            "pushed above U_j. Water-filling is the STRONG share rule: an edge "
            "capped below the water level does not forfeit the remainder, it "
            "is redistributed, so C3 exhausts its band-safe budget rather than "
            "leaving it unused. IMPORTANT AND NOT OVERSTATED: this ordering is "
            "a PROPOSAL-LEVEL priority. The common resolver is stage-blind and "
            "scales the whole vector proportionally, so where sigma < 1 a "
            "Stage-1 reserve deficit can be left incompletely served while "
            "Stage-3 service still executes. No realised saturation is "
            "claimed - see P1C_BINDING_ANALYSIS."),
        tie_breaking=(
            "For CONTINUOUS quantities the rule reaches no tie-break at all. W "
            "is a symmetric function of the cap MULTISET, so every stage is "
            "invariant under any permutation of the edges and equal caps "
            "receive equal quantities; lambda is unique whenever the caps "
            "bind; nothing in the continuous rule consults an edge identifier. "
            "A residual can arise ONLY if a caller rounds or discretises the "
            "allocation afterwards. Such a residual is settled by a declared "
            "deterministic key - destination node id ascending - which may "
            "only move a residual between edges the continuous rule has "
            "ALREADY TIED and must never change the continuous allocation. "
            "The key depends on no EBU quantity, no mu, no f_e, no controller "
            "outcome and no future information. All five arms declare it."),
        no_feasible_action=(
            "If A_i = [x_i - L_i]_+ = 0 - the source is at or below its own "
            "lower homeostatic band - ALL THREE stage budgets are zero and C3 "
            "proposes the empty map, however severe the destination deficits "
            "it can see. That is a genuine refusal, not a fallback to a "
            "smaller transfer. The same happens when every r_e, l_e and h_e is "
            "zero. C3's tick record then looks like C0's, and the metrics must "
            "tell them apart by HOW OFTEN it happens, not by any single tick."),
        information_use={
            "L": "READ, and central. L_i bounds C3's own export "
                 "(A_i = [x_i - L_i]_+); L_j sets the stage-2 deficit caps. "
                 "Band EDGES only, never the burden they define",
            "U": "READ, as a hard side condition at stage 3: C3's own proposal "
                 "pushes no destination above U_j. Per source only - see G-4, "
                 "which the configuration-level single-source restriction "
                 "currently enforces",
            "R": "READ, and central to stage 1: [R_j - x_j]_+ is the "
                 "destination's HOMEOSTATIC RESERVE deficit. This is "
                 "NodeSpec.reserve, NOT P1C's provider/export floor R_eff. "
                 "R_eff bounds what a source may SEND and does not implement "
                 "the homeostatic reserve condition at any node, least of all "
                 "a destination's - nothing in the resolver moves resource "
                 "toward a node below R. C3 carries R_j because otherwise "
                 "nothing in the pipeline would",
            "mu": "NOT read, and structurally absent from C3View. C3 never "
                  "evaluates the marginal - that is the point of the "
                  "comparator",
            "f_e": "NOT read, and structurally absent from C3View. No force, "
                   "flux, conductance or threshold",
            "demand": "read, THIS tick only, as a per-edge source-side upper "
                      "bound at all three stages",
            "neighbour_state": "read: x_j and the destination's declared "
                               "homeostatic boundaries R_j, L_j, U_j, granted "
                               "to every arm through the same "
                               "CommonLocalContext",
            "reserve_information": "reads DESTINATION homeostatic reserve R_j "
                                   "(stage 1). It does NOT read R_eff, does "
                                   "NOT read the provider budget B_i, and does "
                                   "NOT read its own R_i - its own floor is "
                                   "the lower band L_i, and its export "
                                   "permission is the provider's business",
        },
        resolver_interaction=(
            "C3 proposes; the same common P1C resolver then decides, exactly "
            "as for every other arm. THE RESOLVER CAN STILL BIND. C3 "
            "guarantees only sum_e q_e^C3 <= A_i = [x_i - L_i]_+, while the "
            "P1C quantity budget is "
            "[ (x_i - eps_x) + dt(u - eps_u) - R_eff ]_+ ; sigma = 1 would be "
            "guaranteed only if L_i >= R_eff + eps_x + dt*eps_u, and NO SUCH "
            "ORDERING IS DECLARED - the candidate domain restriction orders "
            "0 <= R <= L <= U <= K and deliberately EXCLUDES R_eff. So "
            "sigma < 1 is reachable, the accepted vector is sigma * q^C3, and "
            "proportional scaling is stage-blind: a Stage-1 reserve deficit "
            "may be left incompletely served while Stage-3 ordinary service "
            "executes. `p1c_binding_demonstration()` exhibits exactly that. "
            "The accepted vector is NOT proven lexicographically saturated, "
            "and P1C is NOT modified to preserve C3's ordering. The common "
            "opportunity layer exposes no P1C-safe joint cap before proposal "
            "(source_cap is the source's own stock, and invariant 7 keeps the "
            "budget invisible), so C3 cannot pre-clamp to it; the "
            "proposal-then-resolve order is unchanged."),
        proof_no_global_V=_NO_GLOBAL_V,
        proof_no_future_demand=_NO_FUTURE,
        proof_no_oracle_or_arms=_NO_ORACLE,
        config_to_preregister=(
            "the share rule within each stage: capped max-min water-filling "
            "(drafted) versus proportional-to-demand within the stage budget",
            "the stage ORDER: reserve, then lower band, then ordinary service "
            "(drafted). Both the reserve stage and the deficit-first ordering "
            "are TAKEN in this draft and recorded now, so neither can be "
            "presented later as a post-hoc strengthening",
            "whether the stage-3 destination bound is U_j (drafted) or L_j",
            "whether A_i = [x_i - L_i]_+ is a hard floor (drafted) or a soft "
            "target C3 may cross to answer a destination reserve emergency - "
            "the drafted answer means C3 will NOT breach its own band to "
            "rescue a node below R, which fixture B exhibits",
            "whether any residual/rounding rule is needed at all, and if so "
            "that it may only settle ties the continuous rule already created",
            "the candidate domain restrictions this rule assumes: "
            "0 <= R <= L <= U <= K per node, and indegree(j) <= 1, both "
            "validated at CONFIGURATION time and neither a universal theorem",
            "whether a later world with autonomous drift u != 0 re-derives "
            "A_i from the authoritative no-action-successor baseline instead "
            "of reusing [x_i - L_i]_+, which is meaningful only at u = 0",
        ),
        worked_examples=(
            _example(
                "A", "C3", "C3-reserve-and-band-aware",
                "C3 under ample stock (fixture A)",
                "Stage 1 allocates NOTHING here: neither destination is below "
                "its reserve (j1 = 3 and j2 = 15 against R = 2), so every "
                "stage-1 cap is zero and the reserve stage is inert. Stage 2 "
                "finds j1's single unit of lower-band deficit and spends it. "
                "Stage 3 water-fills the remaining 5 and is capped at 1 on j2 "
                "by that destination's upper-band headroom. The source stops "
                "exactly at its own band edge, x_i = 4 = L_i, with no margin "
                "left - C3 spends its band-safe budget to the last unit by "
                "construction, which is both the strong form of the rule and "
                "its exposure. sigma = 1 here only because the illustrative "
                "budget happens to exceed A_i; that is a property of this "
                "fixture, NOT a guarantee. Every node ends inside its band on "
                "THIS fixture, under the configuration-level single-source "
                "restriction; it is not a general property of C3."),
            _example(
                "B", "C3", "C3-reserve-and-band-aware",
                "C3 under scarcity, source already below its band (fixture B)",
                "The source is at 3 against L_i = 4, so A_i = [3 - 4]_+ = 0 "
                "and ALL THREE stage budgets are zero. C3 proposes the empty "
                "map and serves none of the 12 demanded. Read the stage caps "
                "carefully: the stage-1 RESERVE cap on e2 is 1.0, because j2 "
                "sits at 1 against R = 2 - so C3 explicitly SEES a destination "
                "reserve emergency, and the stage-2 caps show two lower-band "
                "deficits as well, and it still exports nothing. The refusal "
                "comes from the source-side budget, never from the caps. That "
                "is the drafted answer to 'may C3 breach its own band to "
                "rescue a node below its reserve?' - no - and it is listed as "
                "an explicit preregistration choice rather than buried. The "
                "fixture is retained precisely because it is unfavourable to "
                "C3; no fixture is selected for which arm it flatters."),
        ),
        anti_strawman=(
            "Yes, and it is the decisive comparator. C3 is what a competent "
            "engineer builds when told 'serve demand, keep your own stock "
            "inside its declared band, rescue anyone below their reserve "
            "first, then fix band deficits, then serve ordinary demand without "
            "overfilling anyone' - no EBU knowledge required, and every term "
            "is a declared quantity an operator with a homeostatic band and a "
            "reserve already has. It is drafted in its STRONG form: the "
            "reserve stage and the deficit-first ordering are TAKEN, not "
            "listed as optional strengthenings, and the share rule is the "
            "redistributing water-filling rather than a proportional split "
            "that would leave band-safe budget unused. All of this is recorded "
            "BEFORE any result is seen, so C3 can neither be quietly left weak "
            "nor strengthened later in response to an outcome. If EBU cannot "
            "beat C3, the field's added structure has not earned its "
            "complexity, and that is a legitimate and publishable negative "
            "result (Principle J)."),
        added_information=(
            "Over C2: the declared homeostatic boundaries - its own L_i, and "
            "R_j, L_j, U_j per destination - plus destination stocks, a "
            "three-stage lexicographic structure and a redistribution rule "
            "(water-filling) that C1 and C2 lack. Note what this is NOT: it is "
            "not provider information. C3 never sees R_eff or the budget."),
        informational_asymmetry=(
            "None relative to C4 in either direction. Both read own state, own "
            "band, destination state and the destinations' declared "
            "homeostatic boundaries, from the SAME CommonLocalContext. C4 "
            "additionally reads the potential WEIGHTS (alpha, beta, chi) and "
            "the edge parameters (M_e, theta_e); C3's rule has no term that "
            "could consume them, and C3View therefore does not carry them - "
            "structurally, not by promise. Neither arm sees the other's "
            "proposal, R_eff, the provider budget, the oracle or any future."),
        decision_power=(
            "Same action space, same continuous freedom. It reaches points C2 "
            "will not - it withholds quantity above its own band floor and "
            "stops at U_j - and points C1 will not, since it redistributes and "
            "orders reserve emergencies and band deficits ahead of ordinary "
            "demand."),
        quantity_freedom=(
            "Continuous, over the same [0, c_e] as every arm."),
        credibility=(
            "The most credible comparator overall, and the one the study "
            "exists to be measured against. Every quantity it uses is already "
            "declared in any operational system that has a homeostatic band "
            "and a reserve."),
        same_action_set_as_ebu=_SAME_ACTIONS,
        use_of_L_U_R=(
            "Declared homeostatic boundaries only, never the burden they "
            "define. L_i bounds its own export; R_j orders stage 1; L_j orders "
            "stage 2; U_j bounds stage 3. It reads the band and reserve EDGES "
            "as constraints and evaluates no potential. P1C's provider floor "
            "R_eff is absent from its view entirely."),
    ),
    ControllerDraft(
        controller_id="C4-ebu-local-field",
        family="C4",
        decision_formula=(
            "The committed local law, reused and not re-derived "
            "(`d0_v29.edge_flux`). With the separable burden "
            "v_i(x) = alpha[L_i - x]_+^2 + beta[x - U_i]_+^2 + "
            "chi[R_i - x]_+^2 and its marginal "
            "mu_i = -2 alpha [L_i - x_i]_+ + 2 beta [x_i - U_i]_+ "
            "- 2 chi [R_i - x_i]_+ : "
            "f_e = mu_i - eta_e mu_j ,  J_e = M_e [f_e - theta_e]_+ ,  "
            "q_e^req = min( dt * J_e , c_e ) , then, if "
            "sum_e q_e^req > x_i , scale the whole vector by "
            "x_i / sum_e q_e^req . Screening comes FIRST and the value only "
            "orders and sizes what survives it: a favourable f_e never makes "
            "an inadmissible action admissible."),
        information_available=C4_INFORMATION,
        candidate_logic=(
            "Rank by the local force f_e, which is positive exactly when the "
            "destination's marginal burden is lower than the source's. Reject "
            "every edge with f_e <= theta_e (the flux is identically 0 there) "
            "- so C4 refuses transfers the other arms would make whenever the "
            "move does not reduce local burden. Size by the flux dt * J_e, "
            "clipped to the common cap. The ordering is a consequence of the "
            "sizing, not a separate step."),
        tie_breaking=(
            "The committed law is a deterministic function of the local view, "
            "so exact ties are measure-zero; where they occur (identical "
            "destination states and parameters), order by destination node id "
            "ascending - the same declared rule as C0-C3, so no arm gains from "
            "a different tie policy."),
        no_feasible_action=(
            "If every f_e <= theta_e, every J_e = 0 and C4 proposes the empty "
            "map: it declines to move resource that no local burden gradient "
            "justifies, even where demand exists. This is a real and frequent "
            "case, not an edge case, and it is the main mechanism by which C4 "
            "can lose on the service axis. If x_i = 0 or every c_e = 0 the map "
            "is empty for the ordinary physical reason."),
        information_use={
            "L": "read, through the potential: it sets the deficit branch of "
                 "mu for the source and for each destination",
            "U": "read, through the potential: the excess branch of mu",
            "R": "read, through the potential: the reserve branch of mu, "
                 "weighted by chi. Note this is SOFT - the reserve enters as a "
                 "penalty, not as the hard floor C3 imposes",
            "mu": "read and central, for the source and for each out-edge "
                  "destination. Never summed into a global V",
            "f_e": "read and central; f_e and J_e ARE the decision rule",
            "demand": "read, this tick only - and used ONLY as a cap through "
                      "c_e, never as a driver. C4's sizing does not increase "
                      "with demand, which is a real and deliberate weakness on "
                      "the service axis and must be reported as such",
            "neighbour_state": "read: x_j and the destination's full declared "
                               "NodeSpec, which is what mu_j requires. G-2 is "
                               "closed by CommonLocalContext.endpoint_specs, "
                               "the permitted endpoint views of Lemma 6.6; "
                               "the widening is to the COMMON context, and "
                               "C3's projection draws its band edges from "
                               "the same object, so no arm received a "
                               "private channel",
            "reserve_information": "read as chi[R - x]_+ only. C4 does NOT see "
                                   "the resolver budget B_i, exactly as the "
                                   "other arms do not",
        },
        resolver_interaction=(
            "Identical to the other arms: propose, then the SAME P1C "
            "proportional resolver decides. C4 receives no privileged budget "
            "information, no second attempt and no feedback about sigma within "
            "the tick. Note the consequence the study must report: the ranked "
            "value is the value of the ACCEPTED vector, so where sigma < 1 the "
            "vector C4 reasoned about is not the vector that executes."),
        proof_no_global_V=(
            _NO_GLOBAL_V + " Additionally, locality here is exact rather than "
            "approximate: V is separable (Definition 6.1), so the local "
            "marginal needs only the source, its out-edges and their permitted "
            "endpoint views (Lemma 6.6). C4 therefore loses nothing by being "
            "denied the global sum."),
        proof_no_future_demand=_NO_FUTURE,
        proof_no_oracle_or_arms=_NO_ORACLE,
        config_to_preregister=(
            "alpha, beta, chi per node (the potential weights) - S-P",
            "L, U, R, K per node - S-W and S-V",
            "M_e and theta_e per edge (Onsager conductance and threshold); "
            "neither exists in the world model today - gap G-1",
            "dt, and whether q = dt * J is clipped or renormalised when the "
            "source cannot cover it (drafted: proportional renormalisation)",
            "whether demand caps the flux (drafted: yes, through c_e) or the "
            "flux may exceed demand - this depends on Q-1 and changes what C4 "
            "is",
            "the resolution of E3: f_e, Psi_e and J_e are unregistered for the "
            "declared domain, so C4's chain cannot be evaluated as registered",
        ),
        worked_examples=(
            _example(
                "A", "C4", "C4-ebu-local-field",
                "C4 under ample stock (fixture A)",
                "Only j1 carries a burden gradient - it is below L, so "
                "mu_j1 = -2 - and j2 is comfortable, so f_e2 = 0 and its flux "
                "is identically zero. C4 moves 2 units to j1 and refuses the "
                "other 10 demanded units, including every unit j2 asked for. "
                "Read against C3 on the same fixture, on separate axes: "
                "delivered 2 versus 6; source post-state 8 versus 4, i.e. 4 "
                "above L_i versus exactly at it; and neither arm leaves any "
                "band or reserve violated. C4 delivers less and retains more "
                "source margin. No registered scientific metric ranks those "
                "two axes against each other - slot S-M is unfilled - so this "
                "is a trade-off between mechanisms and not an ordering of "
                "them."),
            _example(
                "B", "C4", "C4-ebu-local-field",
                "C4 under scarcity, one node below reserve (fixture B)",
                "j2 is below L AND below R, so both branches of mu fire and "
                "mu_j2 = -8 against the source's -2: the force is 6 on that "
                "edge and exactly 0 toward the equally-supplied j1. Every "
                "available unit is therefore aimed at j2, and after the budget "
                "scales the proposal the single delivered unit lifts j2 from 1 "
                "to 2, clearing its reserve breach. C4 pays for that by taking "
                "its own source from 3 to 2, deepening its own lower-band "
                "shortfall - the graded field accepts a worse local band "
                "position where it judges the local burden effect favourable. "
                "C3 on this same fixture does the opposite and refuses to move "
                "at all. The two encode genuinely different local decision "
                "principles; neither response is the correct one, and this "
                "fixture is not evidence for either."),
        ),
        anti_strawman=(
            "Not applicable in the usual direction - C4 is the tested policy, "
            "not a comparator. The corresponding risk is the opposite one: "
            "that C4 is privileged. It is not. It sees the same LocalView, "
            "proposes on the same edges, chooses from the same continuous "
            "feasible set, passes through the same resolver, faces the same "
            "demand history, and is denied global V, future demand, rollout, "
            "oracle output and other arms' outcomes by the same structural "
            "means. The two places where privilege could enter are named: the "
            "endpoint parameters C4 needs (G-2) must be granted to every arm, "
            "and the unsolicited-transfer question (Q-1) must be decided once "
            "for all arms, because C4 is the only arm whose sizing does not "
            "start from d_e and would therefore be the only beneficiary."),
        added_information=(
            "Over C3: the potential WEIGHTS alpha, beta, chi (how much each "
            "band violation matters, not merely where the band is), and the "
            "edge parameters M_e, theta_e. That is the entire informational "
            "increment - the state and band information is identical."),
        informational_asymmetry=(
            "The weights and edge parameters are the only quantities C4 reads "
            "that C3 does not, and C3's rule has no term that could use them. "
            "They are world declarations, frozen in the spec digest, and are "
            "available to any arm whose rule calls for them. No arm sees "
            "another's proposal, the budget, the oracle, or any future."),
        decision_power=(
            "Same action space and the same continuous freedom. C4's reach is "
            "different in shape, not larger: it concentrates where the "
            "burden gradient is steep and declines transfers the others make."),
        quantity_freedom=(
            "Continuous, over the same [0, c_e] as every arm. It is not merely "
            "ranking a supplied menu - and neither is any other arm, which is "
            "the symmetry that makes the comparison meaningful."),
        credibility=(
            "C4 is the tested mechanism, so credibility is not the question; "
            "fairness is. The relevant check is that its two structural "
            "advantages - endpoint parameters and possible unsolicited "
            "transfers - are either granted to all arms or withheld from all."),
        same_action_set_as_ebu=(
            "C4 IS the EBU arm; the action set is the reference against which "
            "the other four are checked. All five propose non-negative "
            "quantities on their own out-edges, from the same common "
            "opportunity set, and share one resolver."),
        use_of_L_U_R=(
            "Through the potential only: L, U and R enter as the band and "
            "reserve parameters of v_i(x) = alpha[L-x]_+^2 + beta[x-U]_+^2 + "
            "chi[R-x]_+^2, and the controller uses its LOCAL marginal. It "
            "never evaluates the global sum."),
    ),
)


# ---------------------------------------------------------------------------
# open questions and blocking gaps - author decisions, not agent decisions
# ---------------------------------------------------------------------------
RESOLVED_QUESTIONS: Mapping[str, str] = {
    "Q-1": (
        "RESOLVED - opportunities are demand-triggered and demand-bounded. "
        "This study asks how local policies decide among the SAME externally "
        "presented service opportunities, so d_e(t) = 0 implies c_e(t) = 0, "
        "and always c_e(t) <= d_e(t), after the common hard physical caps. "
        "Applied in `common_opportunities` - which takes no controller "
        "argument - so it binds every arm before any controller logic runs. "
        "C4 may therefore not create an autonomous field-driven transfer "
        "where no external service opportunity exists; autonomous EBU "
        "homeostatic rebalancing is a DIFFERENT scientific question and is "
        "left to a separately registered future study rather than mixed into "
        "the sustained-demand comparison."),
    "Q-2": (
        "RESOLVED, AND AN EARLIER ANSWER TO IT WAS WRONG. The committed P1C "
        "robust budget [ (x - eps_x) + dt(u - eps_u) - R_eff ]_+ / dt "
        "subtracts R_eff, the PROVIDER/EXPORT FLOOR. A previous revision "
        "inferred from this that 'the reserve is protected for every arm' and "
        "removed reserve awareness from C3 as redundant. THAT INFERENCE WAS "
        "FALSE. R_eff bounds what a source may SEND; R (NodeSpec.reserve) is "
        "the HOMEOSTATIC RESERVE COORDINATE of a node's own stock, used by the "
        "committed potential's chi[R - x]_+^2 branch. R_eff does not implement "
        "R at any node, and NOTHING in the resolver moves resource toward a "
        "DESTINATION below its R - the resolver only ever narrows what a "
        "source sends. The correct resolution: the provider floor is common "
        "and invisible to every arm; the homeostatic reserve condition is NOT "
        "supplied by any common layer, so a controller that wants it must "
        "carry it. C3 therefore reads R_j and serves destination reserve "
        "deficits in its stage 1, while its own source-side floor remains the "
        "lower band L_i. Neither R_eff nor R is given a value here; both "
        "remain unfilled parameters, and they are never equated."),
    "Q-3": (
        "RESOLVED - destination hard capacity is common physical feasibility. "
        "[K_j - x_j]_+ / eta is clamped inside `common_opportunities` for "
        "every arm, so no controller gains or loses by having been coded to "
        "rediscover a hard physical law, and an arm that ignores it does not "
        "crash its own tick into INVALID. That per-edge bound is exact only "
        "for an isolated incoming transfer with no same-tick outgoing action; "
        "the authoritative simultaneous condition is the JOINT successor "
        "constraint 0 <= x_j + sum_{e->j} eta_e q_e^acc - sum_{j->k} q_e^acc "
        "<= K_j, re-checked on the full accepted increment by "
        "`world.hard_feasible` via `world.joint_successor`."),
}

OPEN_QUESTIONS: Mapping[str, str] = {
    "Q-4": (
        "Which resolution does the author take for G-4 (multi-source "
        "upper-band preservation)? Restrict the prospective topology to "
        "single-source destinations; specify a C3-specific destination-side "
        "coordination rule; or accept the limitation and report C3's "
        "upper-band claim as conditional. A topology restriction is available "
        "as a CANDIDATE simplification and is deliberately NOT baked into the "
        "prospective study here."),
    "Q-5": (
        "Which destination-side allocation rule applies when several "
        "independently controlled sources jointly exceed a destination's hard "
        "capacity (G-3)? No committed authority defines one: p1c_v29 resolves "
        "at the SOURCE and carries the incoming quantity as `incoming_usable`, "
        "explicitly 'DIAGNOSTIC ONLY; not budgeted'. First-come, edge-order, "
        "proportional, max-min and field-priority allocations are all refused "
        "here rather than chosen."),
}

BLOCKING_GAPS: Mapping[str, str] = {
    "G-3": (
        "NO authoritative contested-destination allocation rule exists. When "
        "several sources simultaneously feed one destination and their "
        "individually valid proposals jointly exceed K_j, "
        "`world.require_resolved_destination_contention` DETECTS the "
        "contention and fails closed, because inventing an allocation would "
        "author an unreviewed scientific rule. Contention that stays within "
        "K_j is reported and permitted; only the over-capacity case refuses."),
    "G-4": (
        "C3's upper-band preservation is per-source and is NOT established "
        "under multi-source contention: two sources may each observe "
        "U_j - x_j, each send a band-safe quantity, and jointly push "
        "x_j' > U_j. Moving U_j into the common resolver is refused - it "
        "would hand C1, C2 and C4 a homeostatic protection they did not "
        "choose and destroy the contrast the study measures. "
        "`require_single_source_destinations` fails closed on any topology "
        "with a multiply-fed destination. The illustrative fixture topology "
        "has in-degree 1 at every destination and is unaffected."),
}

CLOSED_GAPS: Mapping[str, str] = {
    "G-1": (
        "CLOSED AT THE SCHEMA LEVEL. `world.EdgeSpec` carries the per-edge "
        "conductance M_e and threshold theta_e, `WorldSpec.edge_specs` holds "
        "them and they enter the spec digest, so an arm can cite them as part "
        "of the frozen world. Declaring a schema is NOT selecting parameters: "
        "there is no default for either field, `WorldSpec.edge_spec` and "
        "`build_common_context` refuse when a world omits them, and both "
        "values remain unfilled preregistration slots."),
    "G-2": (
        "CLOSED. `CommonLocalContext` carries `endpoint_specs` - the full "
        "declared NodeSpec of each out-edge destination, i.e. Lemma 6.6's "
        "permitted endpoint views - and every typed projection is derived "
        "from that ONE common object. C3's projection takes the band edges "
        "L_j and U_j from it and C4's takes the full parameters from it, so "
        "the widening was granted to the common context rather than to any "
        "arm, which is what the anti-strawman analysis requires."),
}


# ---------------------------------------------------------------------------
# accessors
# ---------------------------------------------------------------------------
def draft(controller_id: str) -> ControllerDraft:
    for item in DRAFTS:
        if item.controller_id == controller_id:
            return item
    raise proto.NotPreregistered(
        f"{controller_id!r} is not a declared draft; drafts are "
        f"{[d.controller_id for d in DRAFTS]}")


def unapproved_drafts() -> tuple:
    """Every draft still awaiting author approval. Today: all of them."""
    return tuple(d.controller_id for d in DRAFTS if not d.approved)


def statuses() -> Mapping:
    """The status of every arm, for the decision packet and any record."""
    return {d.controller_id: d.status for d in DRAFTS}


def comparison_rows() -> tuple:
    """The cross-arm comparison, assembled from the drafts themselves.

    Built from the same fields the reviewer checks, so the table cannot say
    something the controller's own declaration does not.
    """
    return tuple({
        "controller_id": d.controller_id, "family": d.family,
        "status": d.status,
        "added_information": d.added_information,
        "informational_asymmetry": d.informational_asymmetry,
        "decision_power": d.decision_power,
        "sees_L_U_R": d.use_of_L_U_R,
        "sees_mu": d.information_use["mu"],
        "sees_f_e": d.information_use["f_e"],
        "quantity_freedom": d.quantity_freedom,
        "credibility": d.credibility,
    } for d in DRAFTS)


def build(controller_id: str, rule) -> proto.DeclaredController:
    """Refuse to instantiate a candidate controller that is not yet approved.

    The draft records what a controller WOULD do. Turning it into something
    runnable is an adoption, and adoption is the author's. There is no
    exception for C0: it is unambiguous, but it is still an arm, and an arm set
    is a scientific choice.
    """
    item = draft(controller_id)
    if getattr(rule, "is_fixture_only", False):
        raise proto.NotPreregistered(
            f"a conformance fixture cannot supply the rule for study arm "
            f"{controller_id!r}: the foundation fixture controller and the "
            f"scientific study controller are separate types with separate "
            f"authority (see proto.require_study_controller)")
    if not item.approved:
        raise proto.NotPreregistered(
            f"{controller_id!r} is {item.status} in the {STUDY_NAME!r} and "
            f"has not been approved. {STUDY_STATUS} Preregistration slot S-R "
            f"(arms and their selection rules) is unfilled; open questions "
            f"{tuple(sorted(OPEN_QUESTIONS))} and blocking gaps "
            f"{tuple(sorted(BLOCKING_GAPS))} are unresolved. Resolving "
            f"{tuple(sorted(RESOLVED_QUESTIONS))} and closing "
            f"{tuple(sorted(CLOSED_GAPS))} removed obstacles; it granted no "
            f"approval, and approval remains an author act.")
    return proto.DeclaredController(
        item.controller_id, item.family, rule,
        declared_formula=item.decision_formula)
