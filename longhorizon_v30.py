"""Long-horizon normalized mechanism study - prospective decision mechanisms.

PROSPECTIVE, NOT ADOPTED. ``V3.0_LONG_HORIZON_NORMALIZED_MECHANISM_CANDIDATE.md``
records the N/H/X families, the four-arm set and every parameter tuple as
"PROPOSED, NOT ADOPTED", and no author-adoption statement is recorded in the
repository. Nothing in this module is adopted, preregistered, or authorized to
run; it carries a prospective design forward and selects nothing.

Supplies only the mechanisms the prospective study needs:

  1. joint two-action budget cap
  2. action-set enumeration, exact joint EBU, and matched set selection
  3. generalized request-shaping identity
  4. persistent checkpoint and restart facility
  5. a fail-closed L0 smoke-test decision-cycle path (never invoked here)

THE DECISION RULE (see ``DECISION_RULE``). P1C admissibility screens the menu;
permitted action sets of size at most ``m`` are enumerated under the
distinct-edge rule; the shared-source proportional joint cap is applied to each
set; the exact finite JOINT EBU is computed for the resulting ACCEPTED action
vector only; selection uses that value; and ``group_quote``, ``naive_sum`` and
``double_count`` are recorded without allocating anything.

The point of the ordering is that the ranked value and the executed value are
the same object. An uncapped requested action is never ranked and then
executed at a different capped quantity.

EXECUTION SAFETY. This module is import-pure. It contains NO tick function, NO
trajectory and NO multi-tick loop, and it never calls ``p1c_v29.p1c_step``,
``service_v30.bounded_step``, or any other step function. ``run_l0_smoke``
is a single-decision-cycle entry point that advances no model state; it is
written to FAIL CLOSED and is never invoked by this repository. The
published P1C aggregate allocation rule and the registered aggregate-quote
formula are *reproduced* from published sources so that a
selector can rank on the quantities it would actually be allocated;
reproducing a rule is not executing a step.

FROZEN SOURCES. ``d0_v29``, ``p1c_v29`` and ``ebu_quote_v30`` are imported
read-only and unmodified. ``gate1dc_v30`` is deliberately NOT imported: it
builds and validates its locked plan at module scope, so importing it would
not be import-pure. Arm identifiers below are copied verbatim from the
registered plan and are asserted against it by the test suite, not here.

EBU MATHEMATICS, UNCHANGED. The governing value is only

    Delta_e(q) = V_loc(z) - V_loc(z + dt*S_e*q) - C_a(q)

evaluated as an exact finite endpoint difference. ``joint_exact_ebu``
implements the registered aggregate form of it verbatim from
``v30_o14_multi_edge_plan.json`` -> ``aggregate_quote_diagnostics``, over the
source and its destinations, with the physical transition counted ONCE. No
per-unit value, weighted burden function, numerical quadrature, EBU wallet,
causal allocation, or replacement objective is ever formed. No EBU value is
ever divided by a quantity, so per-unit ranking (falsifier F8) cannot happen;
the only divisions in this module are the two frozen-rule rates, the State-F
availability rate and the proportional scale sigma. Nothing is settled or
allocated here and O3 remains open.

WHAT IS DERIVED, AND WHAT IS DECLARED. The exact-EBU arm's set-level score is
DERIVED from committed authority: the registered aggregate quote, the
registered strict-positivity act condition, and the registered tie rule
("deterministic identifiers only"). The matched non-EBU comparator's and the
stock-blind control's set-level scores are NOT derivable - both are registered
only as per-candidate, single-action rules - so they are carried here as
AUTHOR-DECLARED PROSPECTIVE SELECTIONS, recorded verbatim in
``DECLARED_SET_SCORES`` and marked as declarations, never as derivations. Both
reduce to the registered per-candidate rule on a single-action set, which is
the only fidelity claim made for them. One question remains open and is
recorded in the candidate document: the settlement form for a multi-action
tick, since aggregate-quote settlement is prohibited while O3 is open. Nothing
here settles, so that gate blocks execution, not this module.

DECISION ORDER. Homeostatic/P1C admissibility first (classify -> budget ->
menu), exact EBU quote second, declared selection third. That ordering is
established by the caller's pipeline, not verified here: this module builds no
menu and cannot confirm where its candidates came from. What it does guarantee
is the negative half - none of these functions can enlarge a budget, reinstate
a rejected candidate, or reorder those stages. A favourable EBU value can
never make an inadmissible action admissible.

REFERENCE-STATE SCOPE. Every check here is a predicate on one frozen state.
Satisfying it at a declared reference state is a necessary design condition
and is NOT a guarantee about an executed trajectory.
"""
from __future__ import annotations

import itertools
import json
import math
import os
from dataclasses import dataclass
from typing import Callable, Mapping, Optional, Sequence

import d0_v29 as d0
import ebu_quote_v30 as eq
import p1c_v29 as p1c

__all__ = [
    "M_BOUND", "PROSPECTIVE_ARMS", "RESTRICTED_ARMS", "ARM_ROLES",
    "DECISION_RULE", "DECLARED_SET_SCORES", "OPEN_LAUNCH_GATES",
    "CHECKPOINT_SCHEMA", "CHECKPOINT_LOG_SCHEMA", "L0_SCOPE",
    "MechanismError", "RequestShapingViolation", "CheckpointChainError",
    "UnregisteredScoringRule", "L0AuthorizationError", "JointAllocation",
    "JointQuote", "SetEvaluation", "DecisionRecord", "Checkpoint",
    "L0Authorization", "L0Request", "source_budget_rate", "joint_budget_cap",
    "enumerate_action_sets", "joint_exact_ebu", "evaluate_action_sets",
    "select_set_by_declared_score", "select_exact_ebu_joint",
    "select_matched_non_ebu_joint", "select_stock_blind_joint",
    "interaction_record", "rest_record", "shaped_active_world",
    "check_request_shaping_identity", "config_digest", "make_checkpoint",
    "verify_chain", "resume_from", "write_chain", "read_chain",
    "append_checkpoint", "resume_from_file", "verify_l0_preconditions",
    "run_l0_smoke",
]

# --------------------------------------------------------------------------
# prospective constants
#
# PROSPECTIVE, NOT ADOPTED. V3.0_LONG_HORIZON_NORMALIZED_MECHANISM_CANDIDATE.md
# records the N/H/X families, the four-arm set and every parameter tuple as
# "PROPOSED, NOT ADOPTED". No author-adoption statement is recorded in the
# repository, so nothing here may be described as adopted. These names carry
# the prospective design forward; they select nothing.
# --------------------------------------------------------------------------
M_BOUND = 2                     # D3-2: proposed simultaneous-action bound

# Registered arm identifiers, verbatim from the locked plan. The first is the
# unrestricted capability reference; the rest are restricted policies sharing
# one menu, one joint cap and one cardinality bound.
PROSPECTIVE_ARMS = (
    "A_full_multi_edge_p1c",
    "D_restricted_exact_total_quote_greedy",
    "B_restricted_matched_non_ebu",
    "S_restricted_local_service_priority",
)
RESTRICTED_ARMS = PROSPECTIVE_ARMS[1:]
ARM_ROLES = {
    "A_full_multi_edge_p1c": "full-capability reference",
    "D_restricted_exact_total_quote_greedy": "exact-EBU restricted policy",
    "B_restricted_matched_non_ebu": "matched non-EBU restricted policy",
    "S_restricted_local_service_priority": "stock-blind control",
}

# The prospective decision rule, in the order it is applied. Step 4 quotes the
# vector that would ACTUALLY execute, which is the correction this module
# exists to carry: an earlier rule ranked an uncapped requested action and
# then executed a different capped quantity, making the ranked value and the
# settled value different objects.
DECISION_RULE = (
    "1. P1C/homeostatic admissibility screens the candidates.",
    "2. Enumerate permitted action sets of size <= m under the distinct-edge "
    "rule.",
    "3. Apply the shared-source proportional joint budget cap to each set.",
    "4. Compute the exact finite JOINT EBU of the resulting accepted action "
    "vector only.",
    "5. Select on that exact joint value for the vector that would execute.",
    "6. Record group_quote, naive_sum and double_count; allocate nothing; "
    "O3 remains open.",
)

# The set-level scores for the two comparator arms are NOT derivable from any
# committed authority - both are registered only as per-candidate, one-action
# rules. They are recorded here exactly as the author declared them in the
# forward-work package, as PROSPECTIVE SELECTIONS. Declared, not derived.
#
# Each reduces to the registered per-candidate rule on a single-action set,
# which is the only fidelity claim made for either, and which the suite checks
# against the frozen selectors.
DECLARED_SET_SCORES = {
    "D_restricted_exact_total_quote_greedy": (
        "DERIVED. The highest strictly positive exact joint EBU of the "
        "accepted vector (registered aggregate quote; registered act "
        "condition)."),
    "B_restricted_matched_non_ebu": (
        "DECLARED. Rank sets by their member force values in descending "
        "lexicographic order; accepted quantities are the next tie level "
        "only."),
    "S_restricted_local_service_priority": (
        "DECLARED. Rank sets by total accepted delivered service to "
        "positive-demand destinations."),
    "_final_ties": (
        "Ascending tuple of edge identifiers, then ascending tuple of "
        "quantity-menu identifiers."),
}

# Registrations that are still missing. Anything that would SETTLE a
# multi-action tick is blocked while this is non-empty; selecting on a joint
# value and recording the triple without allocating is explicitly not
# settlement, so the decision path below is not blocked by it.
OPEN_LAUNCH_GATES = (
    "multi-action settlement form: what is settled and recorded as the "
    "tick's EBU when two actions execute is fixed by no committed authority, "
    "and it must not constitute aggregate-quote settlement while O3 is open "
    "(v30_o14_multi_edge_plan.json: E_aggregate_source_group_quote is NOT "
    "REGISTERED FOR EXECUTION).",
)

# Lexicographic pad. A set of size k < m yields a k-long score segment; every
# segment is padded to width m with this sentinel so all keys compare at one
# arity. Padding with -inf IS the standard lexicographic prefix rule: a
# shorter key ranks below any key that extends it. Under the registered menu
# invariant every member force is strictly positive (a candidate enters the
# menu only when J_e = M_e*[f_e - theta_e]_+ > 0 and theta_e >= 0), so the
# prefix rule and zero-padding coincide, and a second action can never be
# appended to improve a set's rank while making it physically worse. The
# comparator selector enforces that invariant rather than assuming it.
LEX_PAD = -math.inf

CHECKPOINT_SCHEMA = "v30.longhorizon.checkpoint.1"
CHECKPOINT_LOG_SCHEMA = "v30.longhorizon.checkpoint-log.1"
L0_SCOPE = "L0_smoke_one_decision_cycle"

_REQUIRED_CANDIDATE_KEYS = ("edge", "quant_index", "q_req")


class MechanismError(ValueError):
    """Invalid configuration or input. Always fails closed."""


class RequestShapingViolation(AssertionError):
    """The executed action set did not equal the selected action set."""


class CheckpointChainError(MechanismError):
    """A checkpoint chain is broken, forked, rewound, or mismatched."""


def _finite(name: str, value) -> float:
    """Reject bool and non-numeric types, exactly as ``p1c_v29._req_finite``."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise MechanismError(
            f"{name} must be a finite real number, got {value!r}")
    value = float(value)
    if not math.isfinite(value):
        raise MechanismError(f"{name} must be finite, got {value!r}")
    return value


def _nonneg(name: str, value) -> float:
    value = _finite(name, value)
    if value < 0.0:
        raise MechanismError(f"{name} must be >= 0, got {value}")
    return value


def _validate_candidate(candidate) -> None:
    if not isinstance(candidate, Mapping):
        raise MechanismError("candidate must be a mapping")
    for key in _REQUIRED_CANDIDATE_KEYS:
        if key not in candidate:
            raise MechanismError(f"candidate is missing required key {key!r}")
    edge = candidate["edge"]
    quant = candidate["quant_index"]
    if not isinstance(edge, int) or isinstance(edge, bool) or edge < 0:
        raise MechanismError("candidate 'edge' must be a non-negative int")
    if not isinstance(quant, int) or isinstance(quant, bool) or quant < 0:
        raise MechanismError(
            "candidate 'quant_index' must be a non-negative int")
    _nonneg("candidate q_req", candidate["q_req"])


# --------------------------------------------------------------------------
# mechanism 1 - joint two-action budget cap
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class JointAllocation:
    """What one source's aggregate budget grants to a chosen action set."""
    state: str                       # P1C action-time state: F/P/R/I
    budget_rate: float               # Q_max, the aggregate export-rate budget
    requested_total: float           # Q_req over the chosen set
    scale: float                     # sigma = min(1, Q_max/Q_req), else 0
    q_acc: tuple                     # accepted rate per chosen action, in order
    edges: tuple                     # edge index per chosen action, in order

    @property
    def accepted_total(self) -> float:
        return math.fsum(self.q_acc)

    @property
    def binding(self) -> bool:
        """True when the aggregate budget actually constrained the set."""
        return self.scale < 1.0 and self.requested_total > 0.0


def source_budget_rate(cfg: p1c.SourceConfig, x: float, u: float,
                       dt: float) -> tuple:
    """Return ``(state, Q_max)`` for one source, from the published rule.

    Mirrors Amendment 4 Sec 20.3/20.8 exactly as ``p1c_v29`` documents it:

        state F (flow)          -> min(flow_cap, [x + dt*u]_+ / dt)
        state R or state I      -> 0     (export forbidden)
        state P, regenerative   -> robust_budget  (A4.5)
        state P, finite         -> 0     (extraction is depletion)
        state P, irreversible   -> 0     (safe extraction rate is zero)

    Uses only the public entry points ``classify_state`` and
    ``robust_budget``. Never calls ``p1c_step``.
    """
    if not isinstance(cfg, p1c.SourceConfig):
        raise MechanismError("cfg must be a p1c_v29.SourceConfig")
    dt = _finite("dt", dt)
    if dt <= 0.0:
        raise MechanismError(f"dt must be > 0, got {dt}")
    x = _finite("x", x)
    u = _finite("u", u)
    state = p1c.classify_state(cfg, x, u, dt)
    if cfg.source_type == "flow":
        available = x + dt * u
        rate = (available / dt) if available > 0.0 else 0.0
        return state, min(cfg.flow_cap, rate)
    if state != "P":
        return state, 0.0
    if cfg.source_type == "regenerative":
        return state, p1c.robust_budget(cfg, x, u, dt)
    return state, 0.0


def joint_budget_cap(world: d0.World, cfg: p1c.SourceConfig, x_src: float,
                     u_src: float, dt: float, chosen: Sequence[Mapping],
                     m: int = M_BOUND) -> JointAllocation:
    """Apply ONE source's aggregate budget to a chosen action set.

    This is the mechanism the single-action path did not need. The frozen menu
    caps every candidate independently at ``min(q_req, Q_max)``, which
    over-states what any one action receives once a second action draws on the
    same budget in the same tick. The published per-source rule is a
    PROPORTIONAL scale, not an independent clamp:

        Q_req = sum of q_req over the source's active edges
        sigma = min(1, Q_max / Q_req)   (0 when Q_req or Q_max is 0)
        q_acc = sigma * q_req           (per edge)

    For a single action this equals ``min(q_req, Q_max)`` in exact arithmetic.
    In IEEE double it reproduces ``p1c_step``'s ``sigma * q_req`` bit for bit,
    which is the authoritative quantity, and may therefore differ from the
    frozen menu's ``min(q_req, Q_max)`` by one ulp - and may exceed ``Q_max``
    by one ulp. Example: ``q_req = 25.0``, ``Q_max = 7.0`` gives
    ``7.000000000000001``. Agreement with the executed allocation, not with
    the menu's advertised clamp, is what the shaping identity checks.

    ``world`` is required so the function can enforce its own precondition:
    ``p1c_step`` groups requests by source and caps each group separately, so
    applying one source's budget to edges leaving a different source would be
    a silently wrong allocation. Every chosen edge must be an out-edge of
    ``cfg.source_id``.

    Fails closed on: an edge that does not leave this source, an out-of-range
    edge, more than ``m`` actions, repeated edges, a non-positive ``dt``, or a
    malformed candidate.
    """
    if not isinstance(world, d0.World):
        raise MechanismError("world must be a d0_v29.World")
    if not isinstance(m, int) or isinstance(m, bool) or m < 1:
        raise MechanismError(f"m must be a positive int, got {m!r}")
    if m > M_BOUND:
        raise MechanismError(
            f"m={m} exceeds the prospective simultaneous-action bound "
            f"{M_BOUND}")
    chosen = tuple(chosen)
    if len(chosen) > m:
        raise MechanismError(
            f"{len(chosen)} actions exceed the simultaneous-action bound {m}")
    for candidate in chosen:
        _validate_candidate(candidate)
    edges = tuple(int(candidate["edge"]) for candidate in chosen)
    if len(set(edges)) != len(edges):
        raise MechanismError(
            "two actions on the same edge in one tick are not representable "
            "by request shaping; edges must be distinct")
    for edge in edges:
        if edge >= len(world.edges):
            raise MechanismError(f"edge index {edge} out of range")
        if world.edges[edge].i != cfg.source_id:
            raise MechanismError(
                f"edge {edge} leaves cell {world.edges[edge].i}, not source "
                f"{cfg.source_id}; one source's budget must never be applied "
                "to another source's edges")

    state, budget = source_budget_rate(cfg, x_src, u_src, dt)
    requested = tuple(float(candidate["q_req"]) for candidate in chosen)
    total = math.fsum(requested)
    if total > 0.0 and budget > 0.0:
        scale = min(1.0, budget / total)
    else:
        scale = 0.0
    return JointAllocation(
        state=state, budget_rate=budget, requested_total=total, scale=scale,
        q_acc=tuple(scale * value for value in requested), edges=edges)


# --------------------------------------------------------------------------
# mechanism 2 - action-set enumeration, joint exact EBU, and set selection
# --------------------------------------------------------------------------
def enumerate_action_sets(candidates: Sequence[Mapping],
                          m: int = M_BOUND) -> tuple:
    """Every permitted action set of size 1..m, under the distinct-edge rule.

    Step 2 of the prospective decision rule. The menu handed in must already
    have passed P1C screening (step 1); this function adds no candidate and
    relaxes no cap. Sets are returned in a deterministic order: by size, then
    by the ascending tuple of edge indices, then by the ascending tuple of
    quantity-menu indices - the registered tie rule's "deterministic
    identifiers only, no hidden physical objective".

    Rest is not enumerated. It is the fallback when no set satisfies the
    strict-positivity act condition, matching the registered
    ``act_condition`` ("otherwise rest; voluntary rest is recorded").
    """
    if not isinstance(m, int) or isinstance(m, bool) or m < 1:
        raise MechanismError(f"m must be a positive int, got {m!r}")
    if m > M_BOUND:
        raise MechanismError(
            f"m={m} exceeds the prospective simultaneous-action bound {M_BOUND}")
    candidates = tuple(candidates)
    for candidate in candidates:
        _validate_candidate(candidate)
    seen = set()
    for candidate in candidates:
        identifier = (int(candidate["edge"]), int(candidate["quant_index"]))
        if identifier in seen:
            raise MechanismError(
                f"duplicate candidate identifier {identifier}; the registered "
                "tie rule uses identifiers only, so duplicates would make the "
                "winner depend on menu order")
        seen.add(identifier)
    sets = []
    for size in range(1, m + 1):
        for combination in itertools.combinations(candidates, size):
            edges = [int(c["edge"]) for c in combination]
            if len(set(edges)) != len(edges):
                continue                      # distinct-edge rule
            sets.append(tuple(sorted(combination,
                                     key=lambda c: int(c["edge"]))))
    sets.sort(key=lambda group: (len(group),
                                 tuple(int(c["edge"]) for c in group),
                                 tuple(int(c["quant_index"]) for c in group)))
    return tuple(sets)


@dataclass(frozen=True)
class JointQuote:
    """The registered aggregate-quote diagnostics for one action vector.

    ``independent`` carries the per-edge quotes that ``naive_sum`` adds, so a
    recorded decision reproduces the interaction term rather than only
    asserting it. That is the full-fidelity part: nothing about the comparison
    is summarised away.
    """
    group_quote: float        # exact joint EBU of the accepted vector
    naive_sum: float          # sum of independently frozen per-edge quotes
    double_count: float       # naive_sum - group_quote
    n_actions: int
    independent: tuple = ()   # the per-edge quotes naive_sum adds, in order

    def as_record(self) -> dict:
        return {"group_quote": self.group_quote, "naive_sum": self.naive_sum,
                "double_count": self.double_count, "n_actions": self.n_actions,
                "independent": list(self.independent)}


def _penalty_of(world: d0.World, cell: int, value: float) -> float:
    spec = world.cells[cell]
    return d0.penalty(spec.alpha, spec.beta, spec.chi, spec.L, spec.U, spec.R,
                      value)


def joint_exact_ebu(world: d0.World, x: Sequence[float], u: Sequence[float],
                    dt: float, edges: Sequence[int],
                    accepted: Sequence[float], lam_l: float) -> JointQuote:
    """Exact finite JOINT EBU of one accepted action vector, plus diagnostics.

    Implements the registered aggregate-quote formula verbatim
    (``v30_o14_multi_edge_plan.json`` -> ``aggregate_quote_diagnostics``):

        Delta e_group(q_vec) = V_loc(z) - V_loc(z + dt * sum_e S_e q_e_acc)
                               - sum_e C_e(q_e_acc),     z = x + dt*u

    evaluated over the source and its destinations as an exact finite endpoint
    difference. Never per unit, never sampled quadrature, never a surrogate.
    The physical transition is counted ONCE: shared cells are displaced by the
    summed contribution of every action, not once per action.

    ``naive_sum`` is the sum of the independently frozen per-edge quotes and
    ``double_count = naive_sum - group_quote`` is the measured interaction, as
    registered. Nothing is allocated between actions and nothing is settled
    here; O3 remains open.
    """
    if not isinstance(world, d0.World):
        raise MechanismError("world must be a d0_v29.World")
    dt = _finite("dt", dt)
    if dt <= 0.0:
        raise MechanismError(f"dt must be > 0, got {dt}")
    lam_l = _nonneg("lam_l", lam_l)
    edges = tuple(edges)
    for edge in edges:
        if isinstance(edge, bool) or not isinstance(edge, int):
            raise MechanismError(
                f"edge index must be an int, got {edge!r}; silent coercion "
                "would quote a different edge than the caller named")
        if edge < 0:
            raise MechanismError(f"edge index must be >= 0, got {edge}")
    accepted = tuple(_nonneg("accepted", value) for value in accepted)
    if len(edges) != len(accepted):
        raise MechanismError("edges/accepted length mismatch")
    if len(set(edges)) != len(edges):
        raise MechanismError("edges must be distinct")
    for edge in edges:
        if edge < 0 or edge >= len(world.edges):
            raise MechanismError(f"edge index {edge} out of range")
    xs = tuple(_finite("x", value) for value in x)
    us = tuple(_finite("u", value) for value in u)
    if len(xs) != world.n or len(us) != world.n:
        raise MechanismError("x and u must have one entry per cell")
    # The frozen diagnostic restricts the involved-cell set to edges that
    # actually move stock (gate1dc_v30.group_quote_diagnostic). Keeping an
    # idle cell in both endpoint sums is not exact: its penalty enters
    # `before` and `after` as separate fsum terms, which can flip the sign of
    # a near-zero group quote and always inflates the active-action count.
    active = [(edge, quantity) for edge, quantity in zip(edges, accepted)
              if quantity > 0.0]
    if not active:
        return JointQuote(0.0, 0.0, 0.0, 0, ())
    edges = tuple(edge for edge, _ in active)
    accepted = tuple(quantity for _, quantity in active)

    involved = sorted({world.edges[e].i for e in edges}
                      | {world.edges[e].j for e in edges})
    z = {cell: xs[cell] + dt * us[cell] for cell in involved}

    before = math.fsum(_penalty_of(world, cell, z[cell]) for cell in involved)
    successor = dict(z)
    process_cost = 0.0
    for edge, quantity in zip(edges, accepted):
        spec = world.edges[edge]
        successor[spec.i] -= dt * quantity
        successor[spec.j] += dt * spec.eta * quantity
        process_cost += (lam_l * dt * (1.0 - spec.eta)) * quantity
    after = math.fsum(_penalty_of(world, cell, successor[cell])
                      for cell in involved)
    group = before - after - process_cost

    independent = []
    for edge, quantity in zip(edges, accepted):
        spec = world.edges[edge]
        pair = (spec.i, spec.j)
        head = math.fsum(_penalty_of(world, cell, z[cell]) for cell in pair)
        moved = {spec.i: z[spec.i] - dt * quantity,
                 spec.j: z[spec.j] + dt * spec.eta * quantity}
        tail = math.fsum(_penalty_of(world, cell, moved[cell]) for cell in pair)
        cost = (lam_l * dt * (1.0 - spec.eta)) * quantity
        independent.append(head - tail - cost)
    naive = math.fsum(independent)
    return JointQuote(group_quote=group, naive_sum=naive,
                      double_count=naive - group, n_actions=len(edges),
                      independent=tuple(independent))


@dataclass(frozen=True)
class SetEvaluation:
    """One enumerated action set, capped and quoted as it would execute."""
    actions: tuple                   # candidates, ascending edge order
    allocation: JointAllocation      # the joint-capped accepted vector
    quote: JointQuote                # exact joint EBU of that vector

    @property
    def edges(self) -> tuple:
        return self.allocation.edges

    @property
    def quant_indices(self) -> tuple:
        return tuple(int(c["quant_index"]) for c in self.actions)


def evaluate_action_sets(world: d0.World, cfg: p1c.SourceConfig,
                         x: Sequence[float], u: Sequence[float], dt: float,
                         candidates: Sequence[Mapping], lam_l: float,
                         m: int = M_BOUND) -> tuple:
    """Steps 2-4: enumerate sets, joint-cap each, quote the ACCEPTED vector.

    This is the correction that matters. An earlier rule ranked candidates on
    their uncapped menu quantities and then executed a different, capped
    quantity. Here every set is capped first and the exact joint EBU is taken
    of the vector that would actually execute, so the ranked value and the
    executed value are the same object.
    """
    if not isinstance(world, d0.World):
        raise MechanismError("world must be a d0_v29.World")
    if not isinstance(cfg, p1c.SourceConfig):
        raise MechanismError("cfg must be a p1c_v29.SourceConfig")
    if not 0 <= cfg.source_id < world.n:
        raise MechanismError(
            f"cfg.source_id {cfg.source_id} is not a cell of this world")
    if len(x) != world.n or len(u) != world.n:
        raise MechanismError("x and u must have one entry per cell")
    evaluations = []
    for group in enumerate_action_sets(candidates, m=m):
        allocation = joint_budget_cap(world, cfg, x[cfg.source_id],
                                      u[cfg.source_id], dt, group, m=m)
        quote = joint_exact_ebu(world, x, u, dt, allocation.edges,
                                allocation.q_acc, lam_l)
        evaluations.append(SetEvaluation(actions=group, allocation=allocation,
                                         quote=quote))
    return tuple(evaluations)


def _score_component(value) -> float:
    """Validate one lexicographic key component.

    Accepts ``LEX_PAD`` (-inf) because that is the declared pad. Rejects NaN,
    +inf, bool and non-numbers: an unordered or unbounded component would make
    the comparison undefined rather than merely unusual.
    """
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise MechanismError(
            f"score component must be a real number, got {value!r}")
    value = float(value)
    if math.isnan(value):
        raise MechanismError("score component must not be NaN")
    if value == math.inf:
        raise MechanismError("score component must not be +inf")
    return value


def _padded_descending(values: Sequence[float], width: int) -> tuple:
    """Descending values, padded to ``width`` with ``LEX_PAD``.

    This is how a set of size k < m is compared against a set of size m under
    the declared "descending lexicographic order": the shorter key is the
    prefix, so it ranks below any key extending it. See ``LEX_PAD``.
    """
    ordered = sorted((float(v) for v in values), reverse=True)
    if len(ordered) > width:
        raise MechanismError(
            f"{len(ordered)} score values exceed the declared width {width}")
    return tuple(ordered) + (LEX_PAD,) * (width - len(ordered))


def select_set_by_declared_score(evaluations: Sequence[SetEvaluation],
                                 score: Callable,
                                 require_positive_score: bool = True) -> Optional[SetEvaluation]:
    """Step 5, shared by every arm. ONLY ``score`` may differ between arms.

    Enumeration, cardinality bound, joint cap, distinct-edge rule and
    tie-breaking are all supplied here, so the arms are matched by
    construction rather than by inspection.

    ``score`` returns a float or a tuple of floats; a tuple is compared
    lexicographically, which is how the declared force-then-quantity key
    works. Every arm uses this one path, so no arm can acquire a different tie
    discipline.

    Tie-breaking is the author-declared final rule, which also GENERALIZES the
    registered one - "deterministic identifiers only, no hidden physical
    objective" - from a single ``(edge, quant_index)`` pair to the tuples of a
    set: higher score first, then the ascending edge-index tuple, then the
    ascending quantity-menu-index tuple. No cardinality preference is imposed,
    because none is declared or registered anywhere.

    ``require_positive_score`` implements the registered ``act_condition``:
    act only on a strictly positive leading score component, otherwise rest.
    """
    evaluations = tuple(evaluations)
    if not evaluations:
        return None
    decorated = []
    arity = None
    for evaluation in evaluations:
        if not isinstance(evaluation, SetEvaluation):
            raise MechanismError("evaluations must be SetEvaluation instances")
        raw = score(evaluation)
        key = (tuple(_score_component(v) for v in raw)
               if isinstance(raw, tuple) else (_score_component(raw),))
        if arity is None:
            arity = len(key)
        elif len(key) != arity:
            raise MechanismError(
                "score must return keys of uniform arity; lexicographic "
                "comparison of different-length keys has no declared meaning")
        decorated.append((tuple(-v for v in key), evaluation.edges,
                          evaluation.quant_indices, key, evaluation))
    decorated.sort(key=lambda row: row[:3])
    best = decorated[0]
    if require_positive_score and not best[3][0] > 0.0:
        return None
    return best[4]


def select_exact_ebu_joint(evaluations: Sequence[SetEvaluation]
                           ) -> Optional[SetEvaluation]:
    """The exact-EBU arm. Selects on the exact joint EBU of what will execute.

    DERIVED from committed authority: the ranking quantity is the registered
    aggregate quote ``Delta e_group(q_vec)`` over the accepted vector; the act
    condition is the registered strict positivity; the tie rule is the
    registered identifier ordering. Per-unit ranking is forbidden (falsifier
    F8) and never occurs - no EBU value is ever divided by a quantity.

    Nothing is allocated between actions and nothing is settled here.
    """
    return select_set_by_declared_score(
        evaluations, lambda evaluation: evaluation.quote.group_quote,
        require_positive_score=True)


class UnregisteredScoringRule(MechanismError):
    """A set-level scoring rule that no committed authority determines.

    Retained so a caller that supplies an out-of-invariant menu to a DECLARED
    comparator score is told precisely why the declaration does not cover it.
    """


def _ordered_accepted(evaluation: SetEvaluation) -> tuple:
    """Accepted quantities of one set, in the set's ascending-edge order."""
    order = sorted(range(len(evaluation.allocation.edges)),
                   key=lambda k: evaluation.allocation.edges[k])
    return tuple(evaluation.allocation.q_acc[k] for k in order)


def select_matched_non_ebu_joint(evaluations: Sequence[SetEvaluation],
                                 m: int = M_BOUND,
                                 set_score: Optional[Callable] = None):
    """Arm B, the matched non-EBU comparator. DECLARED, not derived.

    The declared set-level rule is: rank sets by their member force values in
    descending lexicographic order, with accepted quantities as the next tie
    level only. The key is therefore

        (forces sorted descending, padded to m,
         accepted quantities sorted descending, padded to m)

    compared lexicographically, highest first, then the declared final ties.
    On a single-action set this is exactly the registered per-candidate rule
    "largest f, tie by larger q_acc, then lower edge index, then lower
    quantity-menu index" - the only fidelity claim made for this arm.

    The quantities are the ACCEPTED ones from the joint cap, not the menu's
    independently clamped figures, so this arm ranks the vector that would
    execute, exactly as the exact-EBU arm does.

    Arm B never rests: the registered ``select_arm_B`` returns its maximum
    unconditionally, so no positivity condition is applied.

    Fails closed when a member force is missing or not strictly positive. The
    registered menu admits a candidate only when ``J_e = M_e*[f_e-theta_e]_+``
    is positive with ``theta_e >= 0``, so ``f_e > 0`` holds for every real
    menu candidate; outside that invariant the declared descending-
    lexicographic rule would let a harmful second action raise a set's rank,
    and no authority says what should happen instead.

    ``set_score`` overrides the declared rule with an explicitly registered
    one, routed through the same shared selector so the arms stay matched.
    """
    if set_score is not None:
        return select_set_by_declared_score(evaluations, set_score,
                                            require_positive_score=False)
    if not isinstance(m, int) or isinstance(m, bool) or m < 1:
        raise MechanismError(f"m must be a positive int, got {m!r}")
    if m > M_BOUND:
        raise MechanismError(
            f"m={m} exceeds the prospective simultaneous-action bound "
            f"{M_BOUND}")
    for evaluation in evaluations:
        if not isinstance(evaluation, SetEvaluation):
            raise MechanismError("evaluations must be SetEvaluation instances")
        for action in evaluation.actions:
            if "f" not in action:
                raise MechanismError(
                    "the matched comparator requires candidate key 'f'")
            force = _finite("candidate f", action["f"])
            if force <= 0.0:
                raise UnregisteredScoringRule(
                    f"candidate force f={force} is not strictly positive. The "
                    "registered menu cannot produce this, and the declared "
                    "descending-lexicographic set rule is undefined outside "
                    "that invariant: appending a non-positive-force action "
                    "would raise a set's rank. Register the out-of-invariant "
                    "case explicitly before use.")

    def declared_score(evaluation):
        forces = [float(action["f"]) for action in evaluation.actions]
        return (_padded_descending(forces, m)
                + _padded_descending(_ordered_accepted(evaluation), m))

    return select_set_by_declared_score(evaluations, declared_score,
                                        require_positive_score=False)


def select_stock_blind_joint(evaluations: Sequence[SetEvaluation],
                             world: Optional[d0.World] = None,
                             demand_rate: Optional[Sequence[float]] = None,
                             set_score: Optional[Callable] = None):
    """Arm S, the stock-blind control. DECLARED, not derived.

    The declared set-level rule is: rank sets by total accepted delivered
    service to positive-demand destinations,

        sum over members of  eta_e * q_acc_e * 1[declared demand rate of the
                             destination > 0]

    then the declared final ties. On a single-action set this is exactly the
    registered per-candidate score ``eta_e * q_acc * 1[demand > 0]``, ties by
    lower edge index then lower quantity-menu index - the only fidelity claim
    made for this arm.

    It reads only the menu and the adjacent destinations' declared demand
    rates. Its declared limitation - blindness to destination stock buffers -
    is the point of the control and is preserved: no destination stock, no
    potential, and no quote enters the score.

    Rests on a non-positive total, matching the registered ``select_arm_S``.
    """
    if set_score is not None:
        return select_set_by_declared_score(evaluations, set_score,
                                            require_positive_score=True)
    if not isinstance(world, d0.World):
        raise MechanismError(
            "the stock-blind control needs the world to read edge eta")
    if demand_rate is None:
        raise MechanismError(
            "the stock-blind control needs the declared demand rates")
    rates = tuple(_finite("demand_rate", value) for value in demand_rate)
    if len(rates) != world.n:
        raise MechanismError("demand_rate length must equal the cell count")

    def declared_score(evaluation):
        delivered = []
        for edge_index, accepted in zip(evaluation.allocation.edges,
                                        evaluation.allocation.q_acc):
            edge = world.edges[int(edge_index)]
            if rates[edge.j] > 0.0:
                delivered.append(edge.eta * float(accepted))
        return math.fsum(delivered)

    return select_set_by_declared_score(evaluations, declared_score,
                                        require_positive_score=True)


# --------------------------------------------------------------------------
# the full-fidelity interaction record
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class DecisionRecord:
    """Everything one declared decision produced. Settlement-free.

    ``settled_ebu`` and ``allocation_between_actions`` are permanently
    ``None``: this module records, it never settles and never divides a joint
    value among actions. ``o3_open`` is permanently ``True``.
    """
    arm: str
    tick: int
    rest: bool
    state: str
    n_actions: int
    edges: tuple
    quant_indices: tuple
    q_req: tuple
    q_acc: tuple
    budget_rate: float
    requested_total: float
    scale: float
    binding: bool
    group_quote: Optional[float]
    naive_sum: Optional[float]
    double_count: Optional[float]
    independent: tuple
    settled_ebu: None = None
    allocation_between_actions: None = None
    o3_open: bool = True

    def as_record(self) -> dict:
        return {
            "arm": self.arm, "tick": self.tick, "rest": self.rest,
            "state": self.state, "n_actions": self.n_actions,
            "edges": list(self.edges),
            "quant_indices": list(self.quant_indices),
            "q_req": list(self.q_req), "q_acc": list(self.q_acc),
            "budget_rate": self.budget_rate,
            "requested_total": self.requested_total, "scale": self.scale,
            "binding": self.binding, "group_quote": self.group_quote,
            "naive_sum": self.naive_sum, "double_count": self.double_count,
            "independent": list(self.independent),
            "settled_ebu": None, "allocation_between_actions": None,
            "o3_open": True,
        }


def interaction_record(arm: str, tick: int,
                       evaluation: SetEvaluation) -> DecisionRecord:
    """Record one selected action set at full fidelity.

    Declared rule 9: ``group_quote``, ``naive_sum`` and ``double_count`` are
    recorded for every two-action decision, and nothing is allocated. They are
    recorded for one-action decisions too, where ``double_count`` is
    identically zero - the degeneracy D3-2 exists to remove.

    The per-edge quotes behind ``naive_sum`` are kept as well, so the
    interaction term is reproducible from the record instead of being asserted
    by it.
    """
    if arm not in PROSPECTIVE_ARMS:
        raise MechanismError(f"unknown arm {arm!r}")
    if not isinstance(tick, int) or isinstance(tick, bool) or tick < 0:
        raise MechanismError("tick must be a non-negative int")
    if not isinstance(evaluation, SetEvaluation):
        raise MechanismError("evaluation must be a SetEvaluation")
    quote = evaluation.quote
    if quote.n_actions >= 2 and len(quote.independent) != quote.n_actions:
        raise MechanismError(
            "a two-action decision must carry one independent quote per "
            "action; the interaction term would not be reproducible")
    allocation = evaluation.allocation
    return DecisionRecord(
        arm=arm, tick=tick, rest=False, state=allocation.state,
        n_actions=quote.n_actions, edges=tuple(allocation.edges),
        quant_indices=evaluation.quant_indices,
        q_req=tuple(float(a["q_req"]) for a in evaluation.actions),
        q_acc=tuple(allocation.q_acc), budget_rate=allocation.budget_rate,
        requested_total=allocation.requested_total, scale=allocation.scale,
        binding=allocation.binding, group_quote=quote.group_quote,
        naive_sum=quote.naive_sum, double_count=quote.double_count,
        independent=tuple(quote.independent))


def rest_record(arm: str, tick: int, state: str,
                budget_rate: float) -> DecisionRecord:
    """Record a voluntary or forced rest, as the registered act condition."""
    if arm not in PROSPECTIVE_ARMS:
        raise MechanismError(f"unknown arm {arm!r}")
    if not isinstance(tick, int) or isinstance(tick, bool) or tick < 0:
        raise MechanismError("tick must be a non-negative int")
    if state not in ("F", "P", "R", "I"):
        raise MechanismError(f"unknown P1C state {state!r}")
    return DecisionRecord(
        arm=arm, tick=tick, rest=True, state=state, n_actions=0, edges=(),
        quant_indices=(), q_req=(), q_acc=(),
        budget_rate=_nonneg("budget_rate", budget_rate), requested_total=0.0,
        scale=0.0, binding=False, group_quote=0.0, naive_sum=0.0,
        double_count=0.0, independent=())


# --------------------------------------------------------------------------
# mechanism 3 - generalized request-shaping identity
# --------------------------------------------------------------------------
def shaped_active_world(world: d0.World,
                        selected: Sequence[Mapping]) -> d0.World:
    """Multi-action generalization of the frozen single-action shaping.

    Each selected candidate contributes one edge whose mobility ``M`` is
    scaled by its declared fraction, so the shaped edge's request equals the
    candidate's ``q_req``. ``cells`` is passed through by identity, which the
    bounded-step contract requires. An empty selection yields an edgeless
    world, i.e. an explicit rest tick.

    Edges appear in ascending original-edge-index order; the identity check
    below relies on that order.
    """
    if not isinstance(world, d0.World):
        raise MechanismError("world must be a d0_v29.World")
    selected = tuple(selected)
    if len(selected) > M_BOUND:
        raise MechanismError(
            f"{len(selected)} actions exceed the bound {M_BOUND}")
    for candidate in selected:
        _validate_candidate(candidate)
        if "frac" not in candidate:
            raise MechanismError("shaping requires candidate key 'frac'")
    edges = [int(candidate["edge"]) for candidate in selected]
    if len(set(edges)) != len(edges):
        raise MechanismError("shaping requires distinct edges")
    for edge in edges:
        if edge >= len(world.edges):
            raise MechanismError(f"edge index {edge} out of range")
    if not selected:
        return d0.World(cells=world.cells, edges=())
    ordered = sorted(selected, key=lambda c: int(c["edge"]))
    shaped = []
    for candidate in ordered:
        edge = world.edges[int(candidate["edge"])]
        fraction = _finite("frac", candidate["frac"])
        if not 0.0 < fraction <= 1.0:
            raise MechanismError(
                f"frac must lie in (0, 1], got {fraction}; a restricted arm "
                "must never be shaped with more mobility than the physical "
                "edge carries")
        shaped.append(d0.Edge(i=edge.i, j=edge.j, M=fraction * edge.M,
                              theta=edge.theta, eta=edge.eta))
    return d0.World(cells=world.cells, edges=tuple(shaped))


def check_request_shaping_identity(selected: Sequence[Mapping],
                                   allocation: JointAllocation,
                                   realized_q_acc: Sequence[float],
                                   tolerance: float = 0.0) -> None:
    """Executed action set == selected action set. Raises, never returns False.

    Generalizes the frozen single-action assertion, which could only check
    ``len(q_acc) == 1``. For up to ``m`` actions it requires the realized
    accepted-quantity vector to match the joint-capped prediction elementwise,
    in ascending edge order.

    ``tolerance`` defaults to 0.0, i.e. exact equality, matching the frozen
    assertion's strictness. Both sides sum with ``math.fsum`` over the same
    values, so exact agreement is attainable; a non-zero tolerance must be
    declared deliberately and is never applied silently.
    """
    if not isinstance(allocation, JointAllocation):
        raise MechanismError("allocation must be a JointAllocation")
    tolerance = _nonneg("tolerance", tolerance)
    selected = tuple(selected)
    realized = tuple(_finite("realized q_acc", v) for v in realized_q_acc)
    expected_edges = tuple(sorted(int(c["edge"]) for c in selected))
    if tuple(sorted(allocation.edges)) != expected_edges:
        raise RequestShapingViolation(
            "request-shaping identity violated: allocation edges "
            f"{allocation.edges} do not match selected edges {expected_edges}")
    if len(realized) != len(selected):
        raise RequestShapingViolation(
            "request-shaping identity violated: executed "
            f"{len(realized)} actions, selected {len(selected)}")
    order = sorted(range(len(allocation.edges)),
                   key=lambda k: allocation.edges[k])
    for position, index in enumerate(order):
        expected = allocation.q_acc[index]
        actual = realized[position]
        if abs(actual - expected) > tolerance:
            raise RequestShapingViolation(
                "request-shaping identity violated on edge "
                f"{allocation.edges[index]}: executed {actual!r}, "
                f"selected {expected!r}")


# --------------------------------------------------------------------------
# mechanism 4 - checkpoint and restart
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class Checkpoint:
    """One link in an unkeyed hash chain over a study's recorded progress.

    The chain is TAMPER-EVIDENT, not forgery-resistant: it detects alteration,
    truncation, forking and rewinding of a recorded chain, and it detects a
    changed study identity or configuration. It cannot detect a chain forged
    wholesale by someone with access to the same hashing path, and it is not a
    signature. Verification requires the chain from its root: a chain must
    begin at ``sequence == 0``, so a retained tail cannot be verified or
    resumed on its own.
    """
    schema: str
    study_id: str
    config_digest: str
    sequence: int
    tick: int
    state: tuple
    prior_digest: Optional[str]
    digest: str

    def as_record(self) -> dict:
        return {
            "schema": self.schema, "study_id": self.study_id,
            "config_digest": self.config_digest, "sequence": self.sequence,
            "tick": self.tick, "state": list(self.state),
            "prior_digest": self.prior_digest, "digest": self.digest,
        }


def config_digest(config: Mapping) -> str:
    """SHA-256 over the strict canonical JSON of a study configuration.

    Reuses ``ebu_quote_v30.commitment_hash``, so the digest is produced by the
    same committed hashing path as every other identifier in V3.
    """
    if not isinstance(config, Mapping):
        raise MechanismError("config must be a mapping")
    try:
        return eq.commitment_hash(config)
    except (TypeError, ValueError) as error:
        raise MechanismError(f"config is not canonically serialisable: {error}")


def _checkpoint_digest(schema, study_id, cfg_digest, sequence, tick, state,
                       prior_digest) -> str:
    return eq.commitment_hash({
        "schema": schema, "study_id": study_id, "config_digest": cfg_digest,
        "sequence": sequence, "tick": tick, "state": list(state),
        "prior_digest": prior_digest,
    })


def make_checkpoint(study_id: str, cfg_digest: str, tick: int,
                    state: Sequence[float],
                    prior: Optional[Checkpoint] = None) -> Checkpoint:
    """Create the next link in a study's checkpoint chain.

A restart must not become a rerun. The chain makes that detectable:
    sequence and tick both strictly increase, every link commits to its
    predecessor's digest, and ``study_id``, ``config_digest`` and the state
    dimension must be constant along the chain. A fresh attempt is exactly a
    chain whose first link has ``sequence == 0`` and ``prior_digest is None``.
    See ``Checkpoint`` for what this does and does not establish.
    """
    if not isinstance(study_id, str) or not study_id:
        raise MechanismError("study_id must be a non-empty string")
    if not isinstance(cfg_digest, str) or len(cfg_digest) != 64:
        raise MechanismError("cfg_digest must be a 64-character SHA-256 hex")
    if not isinstance(tick, int) or isinstance(tick, bool) or tick < 0:
        raise MechanismError("tick must be a non-negative int")
    values = tuple(_finite("state", value) for value in state)
    if not values:
        raise MechanismError("state must be non-empty")
    if prior is None:
        sequence, prior_digest = 0, None
    else:
        if not isinstance(prior, Checkpoint):
            raise MechanismError("prior must be a Checkpoint")
        if prior.study_id != study_id:
            raise CheckpointChainError(
                "study_id changed along the chain: a restart must continue "
                "the same attempt")
        if prior.config_digest != cfg_digest:
            raise CheckpointChainError(
                "config_digest changed along the chain: the configuration was "
                "altered, so this would be a different study, not a restart")
        if tick <= prior.tick:
            raise CheckpointChainError(
                f"tick {tick} does not advance past {prior.tick}: rewinding "
                "would re-execute ticks and break single-attempt discipline")
        sequence, prior_digest = prior.sequence + 1, prior.digest
    digest = _checkpoint_digest(CHECKPOINT_SCHEMA, study_id, cfg_digest,
                                sequence, tick, values, prior_digest)
    return Checkpoint(schema=CHECKPOINT_SCHEMA, study_id=study_id,
                      config_digest=cfg_digest, sequence=sequence, tick=tick,
                      state=values, prior_digest=prior_digest, digest=digest)


def verify_chain(checkpoints: Sequence[Checkpoint]) -> None:
    """Fail closed on a broken, forked, rewound, or altered chain."""
    checkpoints = tuple(checkpoints)
    if not checkpoints:
        raise CheckpointChainError("empty checkpoint chain")
    first = checkpoints[0]
    for index, point in enumerate(checkpoints):
        if not isinstance(point, Checkpoint):
            raise CheckpointChainError("chain contains a non-Checkpoint")
        if point.schema != CHECKPOINT_SCHEMA:
            raise CheckpointChainError(f"unknown schema {point.schema!r}")
        if point.study_id != first.study_id:
            raise CheckpointChainError("study_id is not constant on the chain")
        if point.config_digest != first.config_digest:
            raise CheckpointChainError(
                "config_digest is not constant on the chain")
        if point.sequence != index:
            raise CheckpointChainError(
                f"sequence {point.sequence} out of order at position {index}; "
                "a chain must be verified from its root at sequence 0")
        if len(point.state) != len(first.state):
            raise CheckpointChainError(
                "state dimension changed along the chain: the world is not "
                "the one the chain was started under")
        expected = _checkpoint_digest(
            point.schema, point.study_id, point.config_digest, point.sequence,
            point.tick, point.state, point.prior_digest)
        if point.digest != expected:
            raise CheckpointChainError(
                f"digest mismatch at sequence {point.sequence}: the record was "
                "altered after it was written")
        if index == 0:
            if point.prior_digest is not None:
                raise CheckpointChainError(
                    "the first checkpoint must have no predecessor")
        else:
            previous = checkpoints[index - 1]
            if point.prior_digest != previous.digest:
                raise CheckpointChainError(
                    f"chain broken between sequence {previous.sequence} and "
                    f"{point.sequence}")
            if point.tick <= previous.tick:
                raise CheckpointChainError(
                    f"tick {point.tick} does not advance past {previous.tick}")


def resume_from(checkpoints: Sequence[Checkpoint], study_id: str,
                cfg_digest: str) -> tuple:
    """Verify a chain and return ``(next_tick, state, last_checkpoint)``.

    Refuses to resume when the study identity or the configuration digest
    differs from the chain, because that would silently turn a restart into a
    new attempt under an altered configuration.
    """
    verify_chain(checkpoints)
    last = tuple(checkpoints)[-1]
    if last.study_id != study_id:
        raise CheckpointChainError(
            f"cannot resume {study_id!r} from a chain recorded for "
            f"{last.study_id!r}")
    if last.config_digest != cfg_digest:
        raise CheckpointChainError(
            "cannot resume: the configuration digest differs from the one the "
            "chain was recorded under, so this would be a different study")
    return last.tick + 1, last.state, last


# --------------------------------------------------------------------------
# mechanism 4b - persistent checkpoint file: closed format, atomic writes
# --------------------------------------------------------------------------
# FORMAT (closed and versioned). A checkpoint file is UTF-8 text, one strict
# JSON object per line, LF-terminated:
#
#   line 0 .. n-1   checkpoint records, schema CHECKPOINT_SCHEMA, exactly the
#                   keys in _RECORD_KEYS, in chain order from sequence 0
#   line n          one footer, schema CHECKPOINT_LOG_SCHEMA, exactly the keys
#                   in _FOOTER_KEYS
#
# The footer is what makes TRUNCATION detectable. A hash chain alone cannot
# see a removed tail: every remaining link still verifies. The footer commits
# to the record count and the final digest, so a file that lost records, or
# lost part of its last record, is refused rather than silently resumed from
# an earlier tick. Unknown keys and unknown schemas are refused too, which is
# what makes the format closed: a reader can never be handed a field it does
# not understand and carry on.
#
# Writes are atomic: the whole file is built in a sibling temporary, flushed,
# fsynced, and then os.replace'd over the target, and the containing directory
# is fsynced afterwards. A reader therefore sees either the complete previous
# file or the complete new one, never a partial line. The file is rewritten in
# full on every append rather than appended to, because an append is not
# atomic and a torn append is exactly the failure the footer would then have
# to catch after the fact.
_RECORD_KEYS = ("config_digest", "digest", "prior_digest", "schema",
                "sequence", "state", "study_id", "tick")
_FOOTER_KEYS = ("config_digest", "final_digest", "record_count", "schema",
                "study_id")


def _atomic_write_text(path: str, payload: str) -> None:
    """Write ``payload`` to ``path`` atomically, or leave ``path`` untouched.

    Uses O_EXCL on the temporary so two concurrent writers cannot interleave
    into one another's partial file, fsyncs the data before the rename, and
    fsyncs the directory after it so the rename itself is durable.
    """
    if not isinstance(path, str) or not path:
        raise MechanismError("path must be a non-empty string")
    target = os.path.abspath(path)
    directory = os.path.dirname(target)
    if not os.path.isdir(directory):
        raise MechanismError(f"output directory does not exist: {directory}")
    temporary = os.path.join(directory, f".{os.path.basename(target)}.partial")
    descriptor = os.open(temporary,
                         os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
    except BaseException:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise
    directory_descriptor = os.open(directory, os.O_RDONLY)
    try:
        os.fsync(directory_descriptor)
    finally:
        os.close(directory_descriptor)


def write_chain(path: str, checkpoints: Sequence[Checkpoint]) -> str:
    """Verify a chain, then persist it atomically. Returns the final digest.

    The chain is verified BEFORE it is written, so a broken, forked or rewound
    chain never reaches disk in the first place.
    """
    checkpoints = tuple(checkpoints)
    verify_chain(checkpoints)
    last = checkpoints[-1]
    lines = [eq.canonical_json(point.as_record()) for point in checkpoints]
    lines.append(eq.canonical_json({
        "schema": CHECKPOINT_LOG_SCHEMA, "study_id": last.study_id,
        "config_digest": last.config_digest,
        "record_count": len(checkpoints), "final_digest": last.digest,
    }))
    _atomic_write_text(path, "\n".join(lines) + "\n")
    return last.digest


def _strict_object(line: str, where: str) -> dict:
    try:
        parsed = json.loads(line)
    except ValueError as error:
        raise CheckpointChainError(
            f"{where} is not strict JSON, so the file is truncated or "
            f"corrupt: {error}")
    if not isinstance(parsed, dict):
        raise CheckpointChainError(f"{where} is not a JSON object")
    return parsed


def _require_exact_keys(parsed: dict, expected: Sequence[str],
                        where: str) -> None:
    """Closed format: no missing key, and no key the reader does not know."""
    found = tuple(sorted(parsed))
    if found != tuple(expected):
        missing = [key for key in expected if key not in parsed]
        unknown = [key for key in found if key not in expected]
        raise CheckpointChainError(
            f"{where} has the wrong key set (missing {missing}, unknown "
            f"{unknown}); the checkpoint format is closed")


def read_chain(path: str) -> tuple:
    """Read and fully verify a persisted chain. Fails closed on any defect.

    Refuses on: a missing or unreadable file, a non-JSON or non-object line, a
    wrong or unknown key set, a wrong schema, a wrong value type, a missing
    footer (truncation), a record count or final digest that disagrees with
    the footer, a footer identity that disagrees with the records, and every
    chain defect ``verify_chain`` detects - digest mismatch, break, fork,
    rewind, changed study identity, changed configuration, changed state
    dimension, and a chain that does not start at sequence 0.
    """
    if not isinstance(path, str) or not path:
        raise MechanismError("path must be a non-empty string")
    try:
        with open(path, "r", encoding="utf-8") as handle:
            text = handle.read()
    except OSError as error:
        raise CheckpointChainError(f"cannot read checkpoint file: {error}")
    lines = [line for line in text.split("\n") if line.strip()]
    if not lines:
        raise CheckpointChainError("checkpoint file is empty")
    footer = _strict_object(lines[-1], "the last line")
    if footer.get("schema") != CHECKPOINT_LOG_SCHEMA:
        raise CheckpointChainError(
            "the checkpoint file has no footer: it was truncated, or it was "
            "written by something that does not close its files")
    _require_exact_keys(footer, _FOOTER_KEYS, "the footer")
    count = footer["record_count"]
    if not isinstance(count, int) or isinstance(count, bool) or count < 1:
        raise CheckpointChainError(
            "footer record_count must be a positive int")
    records = lines[:-1]
    if len(records) != count:
        raise CheckpointChainError(
            f"the footer claims {count} records but {len(records)} are "
            f"present: the file was truncated or edited")
    checkpoints = []
    for index, line in enumerate(records):
        parsed = _strict_object(line, f"record {index}")
        _require_exact_keys(parsed, _RECORD_KEYS, f"record {index}")
        if parsed["schema"] != CHECKPOINT_SCHEMA:
            raise CheckpointChainError(
                f"record {index} has unknown schema {parsed['schema']!r}")
        for key in ("study_id", "config_digest", "digest"):
            if not isinstance(parsed[key], str):
                raise CheckpointChainError(
                    f"record {index} field {key!r} must be a string")
        for key in ("sequence", "tick"):
            value = parsed[key]
            if not isinstance(value, int) or isinstance(value, bool):
                raise CheckpointChainError(
                    f"record {index} field {key!r} must be an int")
        prior = parsed["prior_digest"]
        if prior is not None and not isinstance(prior, str):
            raise CheckpointChainError(
                f"record {index} prior_digest must be a string or null")
        state = parsed["state"]
        if not isinstance(state, list) or not state:
            raise CheckpointChainError(
                f"record {index} state must be a non-empty list")
        checkpoints.append(Checkpoint(
            schema=parsed["schema"], study_id=parsed["study_id"],
            config_digest=parsed["config_digest"],
            sequence=parsed["sequence"], tick=parsed["tick"],
            state=tuple(_finite("state", value) for value in state),
            prior_digest=prior, digest=parsed["digest"]))
    verify_chain(checkpoints)
    last = checkpoints[-1]
    if footer["final_digest"] != last.digest:
        raise CheckpointChainError(
            "the footer's final_digest does not match the last record: the "
            "file was altered after it was written")
    if footer["study_id"] != last.study_id:
        raise CheckpointChainError("the footer's study_id disagrees with the "
                                   "records")
    if footer["config_digest"] != last.config_digest:
        raise CheckpointChainError("the footer's config_digest disagrees with "
                                   "the records")
    return tuple(checkpoints)


def append_checkpoint(path: str, study_id: str, cfg_digest: str, tick: int,
                      state: Sequence[float]) -> Checkpoint:
    """Extend a persisted chain by one link, atomically.

    Reads and fully verifies the existing file first, so a corrupt or foreign
    chain can never be extended. When ``path`` does not exist this starts a
    fresh chain at sequence 0; when it does, the new link must continue the
    same study under the same configuration and must advance the tick.
    """
    if os.path.exists(path):
        existing = read_chain(path)
        last = existing[-1]
        if last.study_id != study_id:
            raise CheckpointChainError(
                f"cannot extend a chain recorded for {last.study_id!r} with "
                f"{study_id!r}")
        if last.config_digest != cfg_digest:
            raise CheckpointChainError(
                "cannot extend: the configuration digest differs from the one "
                "the chain was recorded under")
        point = make_checkpoint(study_id, cfg_digest, tick, state, prior=last)
        write_chain(path, existing + (point,))
        return point
    point = make_checkpoint(study_id, cfg_digest, tick, state, prior=None)
    write_chain(path, (point,))
    return point


def resume_from_file(path: str, study_id: str, cfg_digest: str) -> tuple:
    """Read, verify and resume: ``(next_tick, state, last_checkpoint)``."""
    return resume_from(read_chain(path), study_id, cfg_digest)


# --------------------------------------------------------------------------
# L0 smoke-test decision-cycle path - IMPLEMENTED, NEVER INVOKED
# --------------------------------------------------------------------------
# This is the smallest path that could exercise one declared two-action
# decision cycle end to end: screen, enumerate, joint-cap, quote the accepted
# vector, select, record. It advances NO model state - there is no tick
# function here, no trajectory, and no call to any step function - so it
# produces a decision record, not a scientific result.
#
# It is written to FAIL CLOSED. Every one of the four required inputs is
# checked before any decision work begins, and the very first statement of
# ``run_l0_smoke`` is the verification call, so an unauthorized or
# under-specified request cannot reach the decision code at all:
#
#   1. a frozen plan file, whose recomputed canonical hash must equal the
#      hash the caller declares independently;
#   2. exact identities - the study id and configuration digest in the
#      request must equal the ones inside the plan;
#   3. an output location that exists and does not already hold a file;
#   4. an authorization object naming this exact scope, carrying a non-empty
#      author statement, and explicitly permitting one decision cycle.
#
# No plan file exists in this repository, and none is generated here, so this
# path refuses at step 1 as things stand. That is the intended state.
L0_PLAN_SCHEMA = "v30.longhorizon.l0-smoke-plan.1"
_L0_PLAN_KEYS = ("arm", "candidates", "cells", "config_digest", "demand_rate",
                 "dt", "edges", "lam_l", "m", "schema", "source", "study_id",
                 "tick", "u", "x")
_L0_CELL_KEYS = ("A", "K", "L", "R", "U", "alpha", "beta", "chi", "d",
                 "kappa", "lam", "rho", "s", "source")
_L0_EDGE_KEYS = ("M", "eta", "i", "j", "theta")
_L0_SOURCE_KEYS = ("R_eff", "eps_u", "eps_x", "source_id", "source_type")


class L0AuthorizationError(MechanismError):
    """The L0 path was asked to run without complete authorization."""


@dataclass(frozen=True)
class L0Authorization:
    """An explicit, scoped authorization for one L0 decision cycle.

    Being a dataclass makes it cheap to construct, which is deliberate: the
    protection is not that the object is hard to build, it is that building
    one is an unambiguous, recorded act naming this scope. Nothing in this
    repository constructs a permitting instance.
    """
    scope: str
    author_statement: str
    permits_decision_cycle: bool = False


@dataclass(frozen=True)
class L0Request:
    """The complete input the L0 path needs. Missing any part is a refusal."""
    plan_path: str
    expected_plan_hash: str
    study_id: str
    config_digest: str
    output_path: str
    authorization: L0Authorization


def _require_exact_plan_keys(parsed, expected, where: str) -> None:
    if not isinstance(parsed, Mapping):
        raise L0AuthorizationError(f"{where} must be a JSON object")
    found = tuple(sorted(parsed))
    if found != tuple(expected):
        missing = [key for key in expected if key not in parsed]
        unknown = [key for key in found if key not in expected]
        raise L0AuthorizationError(
            f"{where} has the wrong key set (missing {missing}, unknown "
            f"{unknown}); the L0 plan schema is closed")


def verify_l0_preconditions(request: L0Request) -> dict:
    """Check all four required inputs. Returns the validated plan, or raises.

    Refuses rather than defaults on every branch. There is no permissive mode
    and no flag that relaxes any of these checks.
    """
    if not isinstance(request, L0Request):
        raise L0AuthorizationError("request must be an L0Request")

    authorization = request.authorization
    if not isinstance(authorization, L0Authorization):
        raise L0AuthorizationError(
            "an L0Authorization object is required; the L0 path never runs "
            "unauthorized")
    if authorization.scope != L0_SCOPE:
        raise L0AuthorizationError(
            f"authorization scope {authorization.scope!r} is not "
            f"{L0_SCOPE!r}; "
            "authorization for one stage never carries to another")
    if not isinstance(authorization.author_statement, str) \
            or not authorization.author_statement.strip():
        raise L0AuthorizationError(
            "the authorization must carry a non-empty author statement")
    if authorization.permits_decision_cycle is not True:
        raise L0AuthorizationError(
            "the authorization does not permit a decision cycle")

    for name, value in (("study_id", request.study_id),
                        ("config_digest", request.config_digest),
                        ("plan_path", request.plan_path),
                        ("output_path", request.output_path),
                        ("expected_plan_hash", request.expected_plan_hash)):
        if not isinstance(value, str) or not value:
            raise L0AuthorizationError(f"{name} must be a non-empty string")
    if len(request.expected_plan_hash) != 64:
        raise L0AuthorizationError(
            "expected_plan_hash must be a 64-character SHA-256 hex digest")
    if len(request.config_digest) != 64:
        raise L0AuthorizationError(
            "config_digest must be a 64-character SHA-256 hex digest")

    # The output location is checked BEFORE the plan is read and hashed: a
    # request that could not record its result is refused without touching a
    # frozen file at all.
    if os.path.exists(request.output_path):
        raise L0AuthorizationError(
            f"{request.output_path!r} already exists; the L0 path never "
            "overwrites a recorded output")
    output_directory = os.path.dirname(os.path.abspath(request.output_path))
    if not os.path.isdir(output_directory):
        raise L0AuthorizationError(
            f"output directory does not exist: {output_directory}")

    if not os.path.isfile(request.plan_path):
        raise L0AuthorizationError(
            f"no frozen plan at {request.plan_path!r}; the L0 path never "
            "generates a plan and never runs without one")
    try:
        with open(request.plan_path, "r", encoding="utf-8") as handle:
            plan = json.load(handle)
    except (OSError, ValueError) as error:
        raise L0AuthorizationError(f"the plan is not strict JSON: {error}")
    try:
        actual_hash = eq.commitment_hash(plan)
    except (TypeError, ValueError) as error:
        raise L0AuthorizationError(
            f"the plan is not canonically serialisable: {error}")
    if actual_hash != request.expected_plan_hash:
        raise L0AuthorizationError(
            f"plan hash mismatch: the file hashes to {actual_hash}, the "
            f"request declares {request.expected_plan_hash}")

    _require_exact_plan_keys(plan, _L0_PLAN_KEYS, "the plan")
    if plan["schema"] != L0_PLAN_SCHEMA:
        raise L0AuthorizationError(
            f"unknown plan schema {plan['schema']!r}")
    if plan["study_id"] != request.study_id:
        raise L0AuthorizationError(
            "the plan's study_id does not match the request's; the identity "
            "must be exact")
    if plan["config_digest"] != request.config_digest:
        raise L0AuthorizationError(
            "the plan's config_digest does not match the request's")
    if plan["arm"] not in PROSPECTIVE_ARMS:
        raise L0AuthorizationError(f"unknown arm {plan['arm']!r}")
    if plan["arm"] == "A_full_multi_edge_p1c":
        raise L0AuthorizationError(
            "the capability reference is the released p1c_step on the full "
            "world; it is not a menu-and-select arm and this path cannot "
            "stand in for it")
    bound = plan["m"]
    if not isinstance(bound, int) or isinstance(bound, bool) or bound < 1 \
            or bound > M_BOUND:
        raise L0AuthorizationError(
            f"plan m must be an int in 1..{M_BOUND}, got {bound!r}")
    tick = plan["tick"]
    if not isinstance(tick, int) or isinstance(tick, bool) or tick < 0:
        raise L0AuthorizationError("plan tick must be a non-negative int")
    for cell in plan["cells"]:
        _require_exact_plan_keys(cell, _L0_CELL_KEYS, "a plan cell")
    for edge in plan["edges"]:
        _require_exact_plan_keys(edge, _L0_EDGE_KEYS, "a plan edge")
    _require_exact_plan_keys(plan["source"], _L0_SOURCE_KEYS,
                             "the plan source")
    for candidate in plan["candidates"]:
        _validate_candidate(candidate)

    return plan


def run_l0_smoke(request: L0Request) -> DecisionRecord:
    """One declared decision cycle from a frozen plan. Advances no state.

    Verification is the first statement, so nothing below it is reachable
    without all four required inputs. The cycle is: P1C screening (already
    reflected in the plan's menu), enumerate, joint-cap, quote the accepted
    vector, select, record - and then write the record atomically.

    It settles nothing. ``OPEN_LAUNCH_GATES`` records why: no committed
    authority fixes what a two-action tick settles while O3 is open. Recording
    the triple without allocating is registered as non-settling, which is all
    this path does.
    """
    plan = verify_l0_preconditions(request)

    cells = tuple(d0.Cell(**cell) for cell in plan["cells"])
    edges = tuple(d0.Edge(**edge) for edge in plan["edges"])
    world = d0.World(cells=cells, edges=edges)
    cfg = p1c.SourceConfig(**plan["source"])
    x = tuple(_finite("plan x", value) for value in plan["x"])
    u = tuple(_finite("plan u", value) for value in plan["u"])
    dt = _finite("plan dt", plan["dt"])
    lam_l = _nonneg("plan lam_l", plan["lam_l"])
    demand = tuple(_finite("plan demand_rate", v) for v in plan["demand_rate"])
    arm, bound, tick = plan["arm"], plan["m"], plan["tick"]

    state, budget = source_budget_rate(cfg, x[cfg.source_id], u[cfg.source_id],
                                       dt)
    evaluations = evaluate_action_sets(world, cfg, x, u, dt,
                                       plan["candidates"], lam_l, m=bound)
    if arm == "D_restricted_exact_total_quote_greedy":
        chosen = select_exact_ebu_joint(evaluations)
    elif arm == "B_restricted_matched_non_ebu":
        chosen = select_matched_non_ebu_joint(evaluations, m=bound)
    else:
        chosen = select_stock_blind_joint(evaluations, world=world,
                                          demand_rate=demand)
    record = (rest_record(arm, tick, state, budget) if chosen is None
              else interaction_record(arm, tick, chosen))
    _atomic_write_text(request.output_path, eq.canonical_json({
        "schema": L0_PLAN_SCHEMA, "plan_hash": request.expected_plan_hash,
        "study_id": request.study_id, "config_digest": request.config_digest,
        "decision": record.as_record(),
        "open_launch_gates": list(OPEN_LAUNCH_GATES),
        "model_state_advanced": False, "settled": False,
    }) + "\n")
    return record
