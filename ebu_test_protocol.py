"""EBU test protocol: tick discipline, controllers, metrics, classification.

Implements the SYNCHRONOUS TICK, CONTROLLER, ORACLE, METRIC, CLASSIFICATION,
EVENT-LOG, REPRODUCIBILITY and PREREGISTRATION layers of the EBU Scientific
Test Design (sections 7-9, 27-35, 38-39, 41, 44, 50).

**Runtime locality is enforced by architecture, not documentation** (section 28,
Principle B).  A controller is handed a `LocalView` and nothing else.  There is
no accessor on that object for global `V`, for distant nodes, for future
demand, for a rollout, for the oracle, for another arm's outcome or for the
research score - so the forbidden reads are not merely discouraged, they are
unreachable.  Global `V` is computed only by the evaluator, after execution.

**No trajectory runs here.**  `execute_tick` is a PURE single transition
guarded by a `TickBudget`; the conformance budget admits exactly one tick, so a
loop refuses by construction.  `ExperimentRunner.run_campaign` has no success
path while the preregistration is unfrozen or any escalation stands - today,
both.  This module therefore cannot produce scientific evidence.

**Status separation.**  Tick discipline, the quantity ladder, metric plumbing,
classification structure and the event-log schema are IMPLEMENTATION.  Every
parameter, band, distribution, horizon, threshold and success criterion is a
CANDIDATE scientific choice awaiting preregistration, and none is supplied.
Nothing here is EVIDENCE.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Sequence

import authority_coordinate as ac
import ebu_test_settlement as settle
import ebu_test_world as world

__all__ = [
    "ProtocolError", "LocalityViolation", "BudgetExhausted",
    "NotPreregistered", "ExecutionRefused", "OracleLeak",
    "LocalView", "build_local_view", "Controller",
    "FixtureOnlyController", "FixtureRejectAllController",
    "FIXTURE_ONLY_FAMILY", "require_study_controller",
    "DeclaredController", "CONTROLLER_FAMILIES",
    "TickBudget", "TickRecord", "plan_tick", "execute_tick",
    "ServiceMetrics", "ViabilityMetrics", "PhysicalMetrics",
    "PHYSICAL_VALIDITY", "TARGET_OUTCOMES", "TARGET_PREDICATE",
    "target_met", "ORACLE_RESULTS",
    "PhysicalValidity", "ArmResult", "OracleResult",
    "RUN_STATUSES", "derive_ebu_run_label", "Inconclusive",
    "CONCLUSION_STATUSES", "CLAIM_KINDS", "REASON_CODES",
    "ClaimConclusion", "conclude_claim",
    "FeasibilityOracle", "ReproducibilityRecord", "REPRODUCIBILITY_FIELDS",
    "PREREGISTRATION_FIELDS", "Preregistration",
    "ExperimentRunner", "READINESS_VERDICTS", "readiness_report",
]


class ProtocolError(Exception):
    """Base: the protocol layer refused."""


class LocalityViolation(ProtocolError):
    """A controller reached for information section 28 forbids."""


class BudgetExhausted(ProtocolError):
    """A tick budget was exceeded - a trajectory was attempted."""


class NotPreregistered(ProtocolError):
    """A frozen preregistration is required and absent."""


class ExecutionRefused(ProtocolError):
    """Execution is refused by a standing gate."""


class OracleLeak(ProtocolError):
    """Oracle output was offered to a runtime controller (section 29)."""


# ---------------------------------------------------------------------------
# section 28 - the ONLY thing a controller ever sees
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class LocalView:
    """A controller's complete information set. Local by construction.

    Carries the source's own stock, its declared bands and weights, its
    out-edges, the permitted endpoint stocks, and the demand revealed at THIS
    tick.  It deliberately carries no global `V`, no full state vector, no
    future demand, no rollout, no oracle verdict and no research metric.

    This matches the committed locality result: `V` is separable, so a local
    rule needs only the source, its out-edges and their permitted endpoint
    views (`V3.0_LOCAL_EBU_FOUNDATION_DRAFT.md` Lemma 6.6, "locality is exact,
    not approximate").
    """
    tick: int
    source: str
    source_stock: float
    source_spec: world.NodeSpec
    out_edges: tuple
    endpoint_stocks: Mapping
    demand_here: tuple

    def __getattr__(self, name: str):
        # Any attribute NOT declared above is a forbidden read. Raising here
        # turns a typo'd global lookup into a loud refusal rather than an
        # AttributeError a controller might quietly catch.
        raise LocalityViolation(
            f"a controller may not read {name!r}. Section 28 permits only the "
            f"declared local fields; global V, distant state, future demand, "
            f"rollout, oracle output, other arms' outcomes and the research "
            f"score are all outside the decision path.")


def build_local_view(spec: world.WorldSpec, state: world.WorldState,
                     source: str, tick: int,
                     schedule: world.DemandSchedule) -> LocalView:
    """Project the frozen state down to one source's permitted local view.

    Only the endpoints of the source's own out-edges are exposed - not the rest
    of the network - so the view cannot widen into a global read as the
    topology grows.
    """
    out_edges = spec.topology.out_edges(source)
    endpoints = {e[1]: state.values[e[1]] for e in out_edges}
    here = tuple(d for d in schedule.at_tick(tick) if d.edge[0] == source)
    return LocalView(tick=tick, source=source,
                     source_stock=state.values[source],
                     source_spec=spec.node_specs[source],
                     out_edges=out_edges, endpoint_stocks=endpoints,
                     demand_here=here)


# ---------------------------------------------------------------------------
# section 27 - controller families
# ---------------------------------------------------------------------------
CONTROLLER_FAMILIES = {
    "C0": "no-action / reject control; preserves state by delivering nothing",
    "C1": "local greedy; local information and hard feasibility only, no field",
    "C2": "myopic service; maximise immediate satisfaction within feasibility",
    "C3": "band-aware non-field; declared homeostatic band L/U, no EBU "
          "gradient. The provider reserve is protected for EVERY arm by the "
          "common P1C layer and is NOT duplicated in this controller",
    "C4": "EBU local-field; the committed local marginal/force mechanism",
}


class Controller:
    """Base controller. Receives a `LocalView` and returns requested quantities.

    `propose` must be a pure function of the view.  Every controller's output
    then passes through the SAME physical resolver (section 27), so no arm can
    obtain quantities another arm could not.
    """
    family = ""
    controller_id = ""

    def propose(self, view: LocalView) -> Mapping:
        raise NotImplementedError

    def declaration(self) -> Mapping:
        return {"controller_id": self.controller_id, "family": self.family}


# The family label carried by every fixture-only controller.  It is
# deliberately NOT a key of CONTROLLER_FAMILIES, so a fixture can never be
# registered as a study arm by any code path that validates a family.
FIXTURE_ONLY_FAMILY = "FIXTURE-ONLY"

# A module-private token.  Construction requires it, and only the named
# fixture constructor holds it, so a fixture-only controller cannot be built
# by accident or by a caller that merely imports the class.
_FIXTURE_TOKEN = object()


class FixtureOnlyController(Controller):
    """Base of the conformance fixtures. NEVER a scientific study arm.

    The foundation gate needs a controller to drive its single-transition
    fixtures, and the study needs a C0 control.  Those are different objects
    with different authority, and conflating them is how a test double
    acquires a scientific status it was never granted.  The separation here is
    structural, not a naming convention:

    * `family` is `FIXTURE-ONLY`, which `CONTROLLER_FAMILIES` does not contain,
      so `DeclaredController`'s family check and every study-arm registration
      path refuse it;
    * `is_fixture_only` is True, and `require_study_controller` refuses on it;
    * construction requires a module-private token.

    The study's C0 is a separate `CANDIDATE_UNAPPROVED` draft in
    `ebu_candidate_controllers`, whose `build()` path fails closed.
    """
    family = FIXTURE_ONLY_FAMILY
    is_fixture_only = True

    def __init__(self, token, controller_id: str):
        if token is not _FIXTURE_TOKEN:
            raise NotPreregistered(
                f"{type(self).__name__} is a conformance fixture, not a study "
                f"controller. It is constructible only through its named "
                f"fixture constructor, so that a test double cannot be handed "
                f"to a scientific path. The study's C0 arm is the "
                f"CANDIDATE_UNAPPROVED draft in ebu_candidate_controllers, "
                f"whose build() refuses.")
        self.controller_id = controller_id

    def declaration(self) -> Mapping:
        return {"controller_id": self.controller_id, "family": self.family,
                "is_fixture_only": True,
                "scientific_status": "NOT A STUDY ARM - conformance fixture"}


class FixtureRejectAllController(FixtureOnlyController):
    """Proposes zero on every out-edge. A test double for the F1-F10 gate.

    Used to drive the single-transition conformance check, where a controller
    that provably moves nothing keeps the fixture's successor state equal to
    its pre-state.  It is NOT the study's C0 control and carries no scientific
    status whatsoever: see `FixtureOnlyController`.
    """

    @classmethod
    def for_conformance_fixture(cls) -> "FixtureRejectAllController":
        """The only way to obtain one. Named so the call site reads as a test."""
        return cls(_FIXTURE_TOKEN, "fixture-only:reject-all")

    def propose(self, view: LocalView) -> Mapping:
        return {edge: 0.0 for edge in view.out_edges}


def require_study_controller(controller: Controller) -> Controller:
    """Refuse a conformance fixture anywhere a scientific study arm is meant.

    Called by every path that would give a controller scientific standing.  It
    checks a STRUCTURAL property (the fixture-only marker and the family), not
    a controller's identity: no arm is singled out by name, and no arm is
    granted or denied an outcome here.
    """
    if getattr(controller, "is_fixture_only", False) \
            or getattr(controller, "family", "") == FIXTURE_ONLY_FAMILY:
        raise NotPreregistered(
            f"{getattr(controller, 'controller_id', controller)!r} is a "
            f"conformance fixture ({FIXTURE_ONLY_FAMILY}) and may not serve as "
            f"a scientific study arm: it cannot be registered as C0, cannot "
            f"satisfy the study's approved-controller requirement, cannot "
            f"acquire a controller status and cannot bypass the candidate "
            f"controller build gate.")
    if getattr(controller, "family", "") not in CONTROLLER_FAMILIES:
        raise NotPreregistered(
            f"{getattr(controller, 'controller_id', controller)!r} declares "
            f"family {getattr(controller, 'family', '')!r}, which is not a "
            f"declared controller family {sorted(CONTROLLER_FAMILIES)}")
    return controller


class DeclaredController(Controller):
    """C1-C4. A controller whose heuristic comes from the preregistration.

    Section 27 requires each comparison controller's exact formula to be
    documented and preregistered, and to be a plausible control rather than a
    strawman.  Supplying a default here would silently author a scientific
    choice, so the rule is a required argument and construction refuses without
    one.

    The `rule` is handed ONLY the `LocalView`; it cannot be given anything else,
    which is how section 28's boundary survives a custom controller.
    """

    def __init__(self, controller_id: str, family: str, rule, *,
                 declared_formula: str):
        if family not in CONTROLLER_FAMILIES:
            raise NotPreregistered(
                f"unknown controller family {family!r}; declared families are "
                f"{sorted(CONTROLLER_FAMILIES)}")
        if not callable(rule):
            raise NotPreregistered(f"{controller_id}: rule must be callable")
        if not isinstance(declared_formula, str) or not declared_formula.strip():
            raise NotPreregistered(
                f"{controller_id}: section 27 requires the exact formula to be "
                f"declared; an undeclared heuristic cannot be preregistered "
                f"and cannot be shown not to be a strawman")
        self.controller_id, self.family = controller_id, family
        self._rule, self.declared_formula = rule, declared_formula

    def propose(self, view: LocalView) -> Mapping:
        proposed = self._rule(view)
        if not isinstance(proposed, Mapping):
            raise ProtocolError(f"{self.controller_id}: rule must return a mapping")
        for edge, q in proposed.items():
            if edge not in view.out_edges:
                raise LocalityViolation(
                    f"{self.controller_id} proposed on {edge!r}, which is not "
                    f"an out-edge of its own source {view.source!r}")
            if isinstance(q, bool) or not isinstance(q, (int, float)) or q < 0.0:
                raise ProtocolError("a proposed quantity must be a non-negative real")
        return dict(proposed)

    def declaration(self) -> Mapping:
        return {"controller_id": self.controller_id, "family": self.family,
                "declared_formula": self.declared_formula}


# ---------------------------------------------------------------------------
# section 7 - the frozen synchronous tick
# ---------------------------------------------------------------------------
class TickBudget:
    """A hard cap on how many ticks may be executed.

    The conformance budget is ONE.  A second `execute_tick` refuses, so a
    trajectory cannot be produced by looping this module even by accident.
    Raising the cap is not an implementation detail: a long-run horizon is
    preregistration slot S-T and execution authorization is S-X.
    """
    __slots__ = ("limit", "used", "purpose")

    def __init__(self, limit: int, purpose: str):
        if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
            raise ProtocolError("a tick budget must be a positive int")
        if not isinstance(purpose, str) or not purpose.strip():
            raise ProtocolError("a tick budget must declare its purpose")
        self.limit, self.used, self.purpose = limit, 0, purpose

    @classmethod
    def conformance(cls) -> "TickBudget":
        """Exactly one tick: enough for a fixture, never a trajectory."""
        return cls(1, "single-transition conformance fixture")

    def spend(self) -> None:
        if self.used >= self.limit:
            raise BudgetExhausted(
                f"tick budget for {self.purpose!r} is exhausted after "
                f"{self.used} tick(s). Executing further ticks would be a "
                f"trajectory, which requires a frozen preregistration (slots "
                f"S-T, S-X) and clearance of the standing escalations.")
        self.used += 1


@dataclass(frozen=True)
class TickRecord:
    """The section 39 machine-readable record of ONE tick."""
    tick: int
    pre_state_digest: str
    post_state_digest: str
    demand_events: tuple
    proposals: Mapping
    requested: Mapping
    permitted: Mapping
    accepted: Mapping
    measured: Mapping
    increments: Mapping
    v_pre: float
    v_post: float
    per_action_receipts: Mapping
    group_receipt: float
    conservation_residual: float
    settlement_residual: float
    controller_id: str
    invalidity_flags: tuple

    @property
    def is_valid(self) -> bool:
        return not self.invalidity_flags


def plan_tick(spec: world.WorldSpec, state: world.WorldState, tick: int,
              schedule: world.DemandSchedule, controller: Controller,
              budgets: Mapping) -> Mapping:
    """Section 7 steps 1-7: freeze, reveal, propose, permit, resolve, accept.

    Advances NOTHING.  Every controller sees the same frozen `state`; no
    proposal is applied before another controller proposes, which is exactly
    the partial-update failure section 7 forbids.  Round-robin execution is
    never used as the synchronous model.

    `budgets` maps a source to its permitted aggregate export, computed by the
    committed P1C rule; this function does not invent one.
    """
    ladders, proposals = {}, {}
    for source in spec.topology.nodes:
        out_edges = spec.topology.out_edges(source)
        if not out_edges:
            continue
        view = build_local_view(spec, state, source, tick, schedule)
        requested = controller.propose(view)
        proposals[source] = dict(requested)
        if source not in budgets:
            raise NotPreregistered(
                f"no export budget declared for source {source!r}; section 9 "
                f"requires the provider layer to decide what may be served")
        outcome = world.resolve_shared_source(source, requested, budgets[source])
        for edge, q_req in requested.items():
            q_acc = outcome.accepted[edge]
            ladders[edge] = world.QuantityLadder(
                requested=q_req,
                permitted=min(q_req, budgets[source]),
                accepted=q_acc,
                measured=q_acc,          # audit-clean by construction here
                delivered=spec.eta * q_acc)
    return {"ladders": ladders, "proposals": proposals}


def execute_tick(spec: world.WorldSpec, state: world.WorldState, tick: int,
                 schedule: world.DemandSchedule, controller: Controller,
                 budgets: Mapping, *, budget: TickBudget,
                 conservation_tolerance: float,
                 settlement_tolerance: float) -> tuple:
    """Section 7 steps 8-12 for ONE tick. Pure; returns (record, successor).

    Guarded by `budget`, which admits one tick in conformance mode.  Both
    tolerances are required arguments: section 34 makes a breach INVALID rather
    than EBU-FAIL, and a default tolerance could quietly widen either test.
    """
    budget.spend()
    planned = plan_tick(spec, state, tick, schedule, controller, budgets)
    ladders = planned["ladders"]

    actions, increments = [], {}
    for edge, ladder in sorted(ladders.items()):
        if ladder.accepted <= 0.0:
            continue
        action_id = f"t{tick}:{edge[0]}->{edge[1]}"
        action = world.Action(
            action_id=action_id, actor_id=controller.controller_id, edge=edge,
            carrier="scalar", ladder=ladder, start_epoch=tick, end_epoch=tick,
            permission_evidence=f"p1c-proportional:{edge[0]}")
        actions.append(action)
        increments[action_id] = action.increment(spec)

    flags = []
    v_pre = settle.potential(spec, state.values)
    if increments:
        # The world's own declaration governs; the tick never picks one.
        group = settle.settle_group(spec, state.values, increments,
                                    tolerance=settlement_tolerance,
                                    path_semantics=spec.path_semantics,
                                    reading="diagnostic")
        receipts = {r.action_id: r.value for r in group.receipts}
        group_receipt, settlement_residual = group.endpoint_value, group.residual
    else:
        receipts, group_receipt, settlement_residual = {}, 0.0, 0.0

    successor = world.apply_joint(spec, state, actions,
                                  tolerance=conservation_tolerance)
    v_post = settle.potential(spec, successor.values)
    conservation = world.conservation_residual(spec, state, successor)
    if conservation > conservation_tolerance:
        flags.append("CONSERVATION_RESIDUAL")
    if settlement_residual > settlement_tolerance:
        flags.append("SETTLEMENT_CLOSURE")

    record = TickRecord(
        tick=tick, pre_state_digest=state.digest,
        post_state_digest=successor.digest,
        demand_events=tuple((d.tick, d.edge, d.quantity)
                            for d in schedule.at_tick(tick)),
        proposals=planned["proposals"],
        requested={e: l.requested for e, l in ladders.items()},
        permitted={e: l.permitted for e, l in ladders.items()},
        accepted={e: l.accepted for e, l in ladders.items()},
        measured={e: l.measured for e, l in ladders.items()},
        increments=increments, v_pre=v_pre, v_post=v_post,
        per_action_receipts=receipts, group_receipt=group_receipt,
        conservation_residual=conservation,
        settlement_residual=settlement_residual,
        controller_id=controller.controller_id, invalidity_flags=tuple(flags))
    return record, successor


# ---------------------------------------------------------------------------
# sections 31-33 - metrics, reported on separate axes
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ServiceMetrics:
    """Section 31. Reported as its own axis, never folded into one score."""
    requested: float
    permitted: float
    accepted: float
    measured: float
    delivered: float
    unmet: float

    @property
    def service_ratio(self):
        """Delivered / requested, or None when nothing was requested.

        `None` rather than 1.0: a tick with no demand is not perfect service,
        and scoring it as such would reward a controller for an empty world.
        """
        return self.delivered / self.requested if self.requested > 0.0 else None

    @classmethod
    def from_ladders(cls, ladders: Sequence) -> "ServiceMetrics":
        return cls(
            requested=sum(l.requested for l in ladders),
            permitted=sum(l.permitted for l in ladders),
            accepted=sum(l.accepted for l in ladders),
            measured=sum(l.measured for l in ladders),
            delivered=sum(l.delivered for l in ladders),
            unmet=sum(l.unmet() for l in ladders))


@dataclass(frozen=True)
class ViabilityMetrics:
    """Section 32. Raw counts are kept so analysis is not locked to one summary."""
    v_value: float
    below_lower: int
    above_upper: int
    reserve_violations: int
    max_violation_depth: float

    @classmethod
    def evaluate(cls, spec: world.WorldSpec,
                 state: world.WorldState) -> "ViabilityMetrics":
        below = above = reserve = 0
        depth = 0.0
        for node, x in state.values.items():
            s = spec.node_specs[node]
            if x < s.lower:
                below += 1
                depth = max(depth, s.lower - x)
            if x > s.upper:
                above += 1
                depth = max(depth, x - s.upper)
            if s.below_reserve(x):
                reserve += 1
        return cls(v_value=settle.potential(spec, state.values),
                   below_lower=below, above_upper=above,
                   reserve_violations=reserve, max_violation_depth=depth)


@dataclass(frozen=True)
class PhysicalMetrics:
    """Section 33. Conservation and settlement closure live here, not in science."""
    total_resource: float
    conservation_residual: float
    settlement_residual: float
    source_capacity_violations: int


# ---------------------------------------------------------------------------
# section 35 - the four top-level run statuses
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# RAW RUN FACTS - recorded separately, and never mixed with inference
# ---------------------------------------------------------------------------
# One enum must not carry both "what happened" and "what it means". These three
# records are RAW: each is observed or computed directly, with no scientific
# reading attached. The derived labels below are built FROM them, and only when
# their conditions are actually established.

PHYSICAL_VALIDITY = ("VALID", "INVALID")
TARGET_OUTCOMES = ("TARGET_MET", "TARGET_MISSED")
ORACLE_RESULTS = ("CONTROLLABLE", "PHYSICALLY_IMPOSSIBLE", "UNRESOLVED")


@dataclass(frozen=True)
class PhysicalValidity:
    """Raw fact: did the run keep its own assumptions?

    `INVALID` here is a statement about the HARNESS, never about EBU. Section
    34: a conservation or settlement-closure breach makes a run invalid, not an
    EBU scientific failure.
    """
    status: str
    flags: tuple = ()

    def __post_init__(self):
        if self.status not in PHYSICAL_VALIDITY:
            raise ProtocolError(f"status must be one of {PHYSICAL_VALIDITY}")
        if self.status == "VALID" and self.flags:
            raise ProtocolError(
                f"a VALID run cannot carry invalidity flags {self.flags}")
        if self.status == "INVALID" and not self.flags:
            raise ProtocolError("an INVALID run must record why")

    @property
    def is_valid(self) -> bool:
        return self.status == "VALID"


# The ONE preregistered target predicate, applied to every controller.
TARGET_PREDICATE = (
    "TARGET_MET iff viability_ok AND service_ok, where service_ok is a "
    "POSITIVE service floor (design section 36). This predicate is "
    "CONTROLLER-IDENTITY-NEUTRAL: it takes no arm id, no family and no "
    "controller object, so no identity can be special-cased into or out of a "
    "target outcome. C0 misses the target because delivering nothing fails a "
    "positive service floor - naturally, on the same predicate every other arm "
    "faces - and NOT because any rule names C0."
)


def target_met(*, viability_ok: bool, service_ok: bool) -> str:
    """The common target predicate. Keyword-only, and takes NO identity.

    Deliberately impossible to pass a controller, arm id or family to: the
    signature itself is the guarantee that no arm is granted or denied a
    target outcome by who it is.
    """
    for name, value in (("viability_ok", viability_ok),
                        ("service_ok", service_ok)):
        if not isinstance(value, bool):
            raise ProtocolError(f"{name} must be a bool")
    return "TARGET_MET" if (viability_ok and service_ok) else "TARGET_MISSED"


@dataclass(frozen=True)
class ArmResult:
    """Raw fact: one controller arm's target outcome. No inference attached.

    Every arm gets one of these - EBU and comparators alike. A comparator
    missing its target is an ordinary, expected observation about that
    comparator; it is not a judgement about EBU, and nothing here turns it into
    one.

    `target_outcome` is decided by `target_met`, the single preregistered
    predicate, which cannot see `arm_id` or `family`. Those two fields are
    carried for REPORTING and for selecting the EBU-specific label vocabulary
    (`derive_ebu_run_label`); neither participates in deciding whether the
    target was met.
    """
    arm_id: str
    family: str
    target_outcome: str
    validity: PhysicalValidity
    viability_ok: bool
    service_ok: bool

    def __post_init__(self):
        if self.target_outcome not in TARGET_OUTCOMES:
            raise ProtocolError(f"target_outcome must be one of {TARGET_OUTCOMES}")
        # Identity is NOT passed in: the predicate cannot see who is asking.
        implied = target_met(viability_ok=self.viability_ok,
                             service_ok=self.service_ok)
        if self.target_outcome != implied:
            raise ProtocolError(
                f"{self.arm_id}: target_outcome {self.target_outcome!r} "
                f"contradicts viability_ok={self.viability_ok} and "
                f"service_ok={self.service_ok}. Section 36 requires BOTH "
                f"viability and meaningful delivered service; recording a "
                f"target as met on viability alone is the reject-everything "
                f"loophole.")


@dataclass(frozen=True)
class OracleResult:
    """Raw fact: the offline feasibility verdict, including 'not resolved'.

    `UNRESOLVED` is a first-class outcome, not a missing value. Recording it
    honestly is what stops an unproven challenge from being read as either
    EBU-FAIL or PHYSICALLY-IMPOSSIBLE.
    """
    result: str
    oracle_id: str = ""

    def __post_init__(self):
        if self.result not in ORACLE_RESULTS:
            raise ProtocolError(f"result must be one of {ORACLE_RESULTS}")


# ---------------------------------------------------------------------------
# section 35 - DERIVED run labels, for the EBU arm, when established
# ---------------------------------------------------------------------------
RUN_STATUSES = ("SUCCESS", "EBU-FAIL", "PHYSICALLY-IMPOSSIBLE", "INVALID")


def derive_ebu_run_label(arm: ArmResult, oracle: OracleResult) -> str:
    """The section 35 label for the EBU arm - only when its conditions hold.

    **Scope, stated explicitly.** This function derives EBU-SPECIFIC
    VOCABULARY (`SUCCESS`, `EBU-FAIL`) and is applicable only to the EBU arm.
    Its `family != "C4"` guard is therefore a restriction on which LABEL SET
    applies, not a success predicate: it neither grants nor withholds a target
    outcome, which `ArmResult` has already decided through the
    identity-neutral `target_met`. A comparison arm keeps its raw `ArmResult`
    and its per-claim `ClaimConclusion` records, and needs no label.


    Precedence, and why each step is where it is:

    1. **INVALID** first: a run that broke its own assumptions is neither a
       success nor a failure, and scoring it either way would let a broken
       harness produce a scientific claim.
    2. **PHYSICALLY-IMPOSSIBLE** when the oracle says no admissible policy
       could have met the target - section 35 forbids calling that EBU-FAIL.
    3. **SUCCESS** when the target was met (viability AND service, section 36).
    4. **EBU-FAIL** only when the oracle independently established the
       challenge as CONTROLLABLE.

    With the oracle `UNRESOLVED` and the target missed, no label is derivable:
    EBU-FAIL requires a controllability finding that does not exist. That is
    reported by refusing, and the run is then carried as raw facts plus an
    INCONCLUSIVE claim - not as a guessed label.
    """
    if arm.family != "C4":
        raise ProtocolError(
            f"{arm.arm_id!r} is family {arm.family!r}; the section 35 labels "
            f"SUCCESS/EBU-FAIL are defined for the EBU arm. A comparator's "
            f"outcome is carried as the raw ArmResult, which needs no label.")
    if not arm.validity.is_valid:
        return "INVALID"
    if oracle.result == "PHYSICALLY_IMPOSSIBLE":
        return "PHYSICALLY-IMPOSSIBLE"
    if arm.target_outcome == "TARGET_MET":
        return "SUCCESS"
    if oracle.result == "CONTROLLABLE":
        return "EBU-FAIL"
    raise Inconclusive(
        "no section 35 label is derivable: the EBU arm missed its target but "
        "the oracle is UNRESOLVED, so the challenge was never independently "
        "shown to be physically controllable. EBU-FAIL is not available and is "
        "not guessed. Record the raw facts and an INCONCLUSIVE claim with "
        "reason ORACLE_UNRESOLVED.")


# ---------------------------------------------------------------------------
# CONCLUSION STATUS - per registered scientific claim, separate from the run
# ---------------------------------------------------------------------------
CONCLUSION_STATUSES = ("CONCLUSIVE", "INCONCLUSIVE")
CLAIM_KINDS = ("absolute", "comparative")
REASON_CODES = (
    "ORACLE_UNRESOLVED",        # feasibility never established
    "COMPARATOR_INVALID",       # a required comparator broke its assumptions
    "MISSING_REQUIRED_ARM",     # a registered arm was not run
    "EBU_ARM_INVALID",          # the EBU arm itself was INVALID
)


class Inconclusive(ProtocolError):
    """A label was requested whose establishing conditions do not hold."""


@dataclass(frozen=True)
class ClaimConclusion:
    """Whether ONE registered scientific claim is concluded, and why not.

    Per claim, not per run: the same run can support a concluded absolute claim
    and leave a comparative claim open.
    """
    claim_id: str
    kind: str
    status: str
    reasons: tuple = ()

    def __post_init__(self):
        if self.kind not in CLAIM_KINDS:
            raise ProtocolError(f"kind must be one of {CLAIM_KINDS}")
        if self.status not in CONCLUSION_STATUSES:
            raise ProtocolError(f"status must be one of {CONCLUSION_STATUSES}")
        for reason in self.reasons:
            if reason not in REASON_CODES:
                raise ProtocolError(
                    f"unknown reason code {reason!r}; declared codes are "
                    f"{REASON_CODES}")
        if self.status == "INCONCLUSIVE" and not self.reasons:
            raise ProtocolError(
                "an INCONCLUSIVE claim must carry at least one reason code")
        if self.status == "CONCLUSIVE" and self.reasons:
            raise ProtocolError("a CONCLUSIVE claim carries no reason codes")


def conclude_claim(*, claim_id: str, kind: str, ebu_arm: ArmResult,
                   oracle: OracleResult, comparators: Sequence = (),
                   required_arms: Sequence = ()) -> ClaimConclusion:
    """Decide CONCLUSIVE / INCONCLUSIVE for one registered claim.

    The distinction that matters, and the reason claim kind is a required
    argument:

    * An **absolute** claim ("EBU met the registered target") depends on the
      EBU arm and the oracle. **A comparator missing its target does NOT make
      it inconclusive** - a comparator underperforming is an ordinary
      observation, and in a well-posed comparison it is often the expected one.
    * A **comparative** claim ("EBU did better than X") depends on X being
      present and valid. There, a comparator that is INVALID or absent leaves
      nothing to compare against, so the claim is INCONCLUSIVE - but note the
      trigger is comparator *invalidity or absence*, never a comparator merely
      missing its target.
    """
    if kind not in CLAIM_KINDS:
        raise ProtocolError(f"kind must be one of {CLAIM_KINDS}")
    reasons = []
    if not ebu_arm.validity.is_valid:
        reasons.append("EBU_ARM_INVALID")
    present = {c.arm_id for c in comparators}
    for needed in required_arms:
        if needed not in present:
            reasons.append("MISSING_REQUIRED_ARM")
            break
    if kind == "absolute":
        # Only an unresolved oracle can leave an absolute claim open, and only
        # when the target was missed: if EBU met the target, feasibility is
        # demonstrated by the run itself.
        if ebu_arm.target_outcome == "TARGET_MISSED" \
                and oracle.result == "UNRESOLVED":
            reasons.append("ORACLE_UNRESOLVED")
    else:
        for comparator in comparators:
            if not comparator.validity.is_valid:
                reasons.append("COMPARATOR_INVALID")
                break
    status = "INCONCLUSIVE" if reasons else "CONCLUSIVE"
    return ClaimConclusion(claim_id=claim_id, kind=kind, status=status,
                           reasons=tuple(dict.fromkeys(reasons)))


# ---------------------------------------------------------------------------
# section 29 - the offline feasibility oracle, structurally isolated
# ---------------------------------------------------------------------------
class FeasibilityOracle:
    """Offline reference oracle. May see everything; reaches no controller.

    Section 29 permits the oracle global information AND future demand,
    because it is not a runtime controller: its only job is to separate
    "the controller failed" from "the challenge was impossible".

    Isolation is structural.  The verdict is reachable only through
    `verdict_for_evaluator`, which refuses unless the caller names itself the
    evaluator, and `as_local_view` exists solely to refuse - so wiring the
    oracle into a decision path fails loudly instead of silently leaking.

    The feasibility computation itself is NOT implemented here: whether the
    preregistered service/viability target is achievable depends on that
    target, which is slot S-H and unfilled.  A `decide` callable must be
    supplied by the adopted protocol.
    """
    __slots__ = ("_decide", "oracle_id")

    def __init__(self, oracle_id: str, decide):
        if not isinstance(oracle_id, str) or not oracle_id.strip():
            raise NotPreregistered("an oracle_id is required")
        if not callable(decide):
            raise NotPreregistered(
                "an oracle needs a decide callable; whether the preregistered "
                "target is achievable depends on that target (slot S-H), so "
                "there is deliberately no default")
        self.oracle_id, self._decide = oracle_id, decide

    def verdict_for_evaluator(self, *, caller: str, spec, schedule):
        """The achievability verdict. Offline evaluator only."""
        if caller != "evaluator":
            raise OracleLeak(
                f"oracle output requested by {caller!r}. Section 29: oracle "
                f"verdicts are never exposed to a tested controller. Only the "
                f"offline evaluator may read them.")
        return self._decide(spec, schedule)

    def as_local_view(self, *args, **kwargs):
        raise OracleLeak(
            "an oracle can never be presented as a controller's LocalView; "
            "that would put global and future information on the decision path")


# ---------------------------------------------------------------------------
# section 38 - reproducibility
# ---------------------------------------------------------------------------
REPRODUCIBILITY_FIELDS = (
    "repository_commit", "spec_version", "spec_hash", "controller_version",
    "topology_hash", "initial_state_hash", "demand_seed", "demand_hash",
    "conservation_tolerance", "settlement_tolerance", "python_version",
    "run_id",
)


@dataclass(frozen=True)
class ReproducibilityRecord:
    """Every field section 38 requires, with none defaulted.

    `python_version` is supplied by the caller rather than read from the live
    interpreter: this module reads no environment, and an official run records
    the environment it actually used rather than the one that happened to
    re-read the record later.
    """
    values: Mapping

    def __post_init__(self):
        missing = tuple(f for f in REPRODUCIBILITY_FIELDS
                        if not str(self.values.get(f, "")).strip())
        if missing:
            raise NotPreregistered(
                f"reproducibility record is incomplete: {missing}. Section 38 "
                f"requires a result to be reproducible from saved inputs, and "
                f"an absent field is a refusal, never a default.")

    @property
    def digest(self) -> str:
        return world.digest_of({k: str(v) for k, v in sorted(self.values.items())})


# ---------------------------------------------------------------------------
# section 44 - preregistration
# ---------------------------------------------------------------------------
PREREGISTRATION_FIELDS = (
    "canonical_topology", "node_count", "capacities", "homeostatic_bands",
    "reserve_bands", "potential_parameters", "demand_model",
    "demand_parameters", "seed_list", "controller_definitions",
    "physical_resolver", "initial_state", "horizon", "numerical_tolerances",
    "success_criteria", "failure_criteria", "physically_impossible_criteria",
    "metrics", "early_stop_rules", "mobius_audit_sampling_policy",
)


@dataclass(frozen=True)
class Preregistration:
    """The frozen, versioned experiment specification of section 44.

    All twenty fields are required and none has a default: each is a scientific
    choice belonging to the author.  `freeze` binds the content to a hash so
    that section 44's prohibition - tuning after inspecting EBU results and
    presenting the tuned run as preregistered - is detectable rather than
    merely forbidden.
    """
    values: Mapping
    frozen_hash: str = ""

    def __post_init__(self):
        if not isinstance(self.values, Mapping):
            raise NotPreregistered("a preregistration is a mapping")
        unknown = tuple(sorted(set(self.values) - set(PREREGISTRATION_FIELDS)))
        if unknown:
            raise NotPreregistered(
                f"unknown preregistration field(s) {unknown}; an unrecognized "
                f"field is refused rather than ignored, so a protocol cannot "
                f"smuggle in an undeclared choice")
        missing = tuple(f for f in PREREGISTRATION_FIELDS
                        if f not in self.values
                        or self.values[f] is None
                        or (isinstance(self.values[f], (str, list, tuple, dict))
                            and len(self.values[f]) == 0))
        if missing:
            raise NotPreregistered(
                f"preregistration is incomplete: {missing}. Section 44 "
                f"requires every one of the twenty fields before official "
                f"evidence is generated. Each is an author decision.")
        computed = world.digest_of(
            {k: self.values[k] for k in sorted(self.values)})
        if self.frozen_hash and self.frozen_hash != computed:
            raise NotPreregistered(
                f"preregistration hash mismatch: declared {self.frozen_hash}, "
                f"computed {computed}. A frozen preregistration is never "
                f"altered to make an implementation or a result pass.")
        object.__setattr__(self, "frozen_hash", computed)


# ---------------------------------------------------------------------------
# sections 30, 49 (Phase 12), 50 - the runner, and the readiness verdict
# ---------------------------------------------------------------------------
class ExperimentRunner:
    """Owns state transition (section 40). Refuses to run a campaign.

    Controllers never mutate world state; the runner does.  But `run_campaign`
    has no success path today and is not expected to acquire one without
    explicit author decisions: it requires a frozen preregistration AND every
    standing escalation cleared, and `authority_coordinate.OPEN_ESCALATIONS`
    currently carries E2-E5.

    This is the section 49 Phase 12 boundary made executable: official
    long-run evidence runs happen only after the preregistration lock, and
    nothing in this repository can reach them by accident.
    """
    __slots__ = ("spec", "preregistration")

    def __init__(self, spec: world.WorldSpec,
                 preregistration: Preregistration = None):
        self.spec, self.preregistration = spec, preregistration

    def run_campaign(self, *args, controllers=(), **kwargs):
        # Fixture doubles are refused BEFORE the preregistration and escalation
        # gates, so the refusal names the real reason rather than a later one.
        for controller in controllers:
            require_study_controller(controller)
        if self.preregistration is None:
            raise ExecutionRefused(
                "no frozen preregistration. Section 44 requires the versioned "
                "experiment specification to be frozen before official "
                "evidence is generated; section 49 puts that lock at Phase 12, "
                "before any long-run run.")
        standing = tuple(sorted(ac.OPEN_ESCALATIONS))
        if standing:
            detail = "; ".join(f"{c}: {ac.OPEN_ESCALATIONS[c]}" for c in standing)
            raise ExecutionRefused(
                f"execution refused: {len(standing)} standing escalation(s) "
                f"require an author decision. {detail} See "
                f"{ac.COORDINATE_DOCUMENT} section 6. Adopting the Stage D/E/F "
                f"rulebooks is not permission to execute (coordinate W-2, "
                f"clause 5).")
        raise ExecutionRefused(
            "execution additionally requires slot S-X (execution "
            "authorization, host and caps), which no adopted protocol supplies")


READINESS_VERDICTS = ("READY FOR PREREGISTERED RUN", "FOUNDATION INCOMPLETE",
                      "IMPLEMENTATION INVALID")


def readiness_report(*, fixtures_passed: bool, negative_controls_passed: bool,
                     preregistration: Preregistration = None,
                     open_escalations: Mapping = None) -> Mapping:
    """Section 50's pre-run report and its three-valued verdict.

    Precedence is deliberate: a failing fixture or a negative control that did
    not fail means the IMPLEMENTATION is invalid, and that is reported before
    any question of readiness - a harness whose identities fail cannot be
    "incomplete but nearly ready", and section 50 forbids launching in that
    state.
    """
    escalations = (ac.OPEN_ESCALATIONS if open_escalations is None
                   else open_escalations)
    if not fixtures_passed or not negative_controls_passed:
        verdict = "IMPLEMENTATION INVALID"
    elif escalations or preregistration is None:
        verdict = "FOUNDATION INCOMPLETE"
    else:
        verdict = "READY FOR PREREGISTERED RUN"
    return {
        "verdict": verdict,
        "foundation_fixtures_passed": bool(fixtures_passed),
        "negative_controls_passed": bool(negative_controls_passed),
        "preregistration_hash": (preregistration.frozen_hash
                                 if preregistration else None),
        "open_escalations": tuple(sorted(escalations)),
        "coordinate": ac.COORDINATE_ID,
        "non_claim": ("this report is not evidence and does not authorize "
                      "execution"),
    }
