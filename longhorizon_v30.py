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
  4. checkpoint and restart mechanism

THE DECISION RULE (see ``DECISION_RULE``). P1C admissibility screens the menu;
permitted action sets of size at most ``m`` are enumerated under the
distinct-edge rule; the shared-source proportional joint cap is applied to each
set; the exact finite JOINT EBU is computed for the resulting ACCEPTED action
vector only; selection uses that value; and ``group_quote``, ``naive_sum`` and
``double_count`` are recorded without allocating anything.

The point of the ordering is that the ranked value and the executed value are
the same object. An uncapped requested action is never ranked and then
executed at a different capped quantity.

EXECUTION SAFETY. This module is import-pure. It contains NO runner, NO tick
function, NO trajectory, NO multi-tick loop, and NO world construction, and it
never calls ``p1c_v29.p1c_step``, ``service_v30.bounded_step``, or any other
step function. The published P1C aggregate allocation rule and the registered
aggregate-quote formula are *reproduced* from published sources so that a
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
availability rate and the proportional scale sigma. Nothing is settled or allocated here and O3 remains open.

WHAT IS DERIVABLE, AND WHAT IS NOT. The exact-EBU arm's set-level score is
derived from committed authority: the registered aggregate quote, the
registered strict-positivity act condition, and the registered tie rule
("deterministic identifiers only"). The matched non-EBU comparator and the
stock-blind control have NO registered set-level score - both are registered
as per-candidate, single-action rules - so ``select_matched_non_ebu_joint``
and ``select_stock_blind_joint`` fail closed with the precise ambiguity rather
than inventing an aggregation. A third open question is recorded in the
candidate document: the settlement form for a multi-action tick, since
aggregate-quote settlement is prohibited while O3 is open.

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
import math
from dataclasses import dataclass
from typing import Callable, Mapping, Optional, Sequence

import d0_v29 as d0
import ebu_quote_v30 as eq
import p1c_v29 as p1c

__all__ = [
    "M_BOUND", "PROSPECTIVE_ARMS", "RESTRICTED_ARMS", "ARM_ROLES",
    "DECISION_RULE", "CHECKPOINT_SCHEMA", "MechanismError",
    "RequestShapingViolation", "CheckpointChainError",
    "UnregisteredScoringRule", "JointAllocation", "JointQuote",
    "SetEvaluation", "Checkpoint", "source_budget_rate", "joint_budget_cap",
    "enumerate_action_sets", "joint_exact_ebu", "evaluate_action_sets",
    "select_set_by_declared_score", "select_exact_ebu_joint",
    "select_matched_non_ebu_joint", "select_stock_blind_joint",
    "shaped_active_world", "check_request_shaping_identity",
    "config_digest", "make_checkpoint", "verify_chain", "resume_from",
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

CHECKPOINT_SCHEMA = "v30.longhorizon.checkpoint.1"

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
    """The registered aggregate-quote diagnostics for one action vector."""
    group_quote: float        # exact joint EBU of the accepted vector
    naive_sum: float          # sum of independently frozen per-edge quotes
    double_count: float       # naive_sum - group_quote
    n_actions: int

    def as_record(self) -> dict:
        return {"group_quote": self.group_quote, "naive_sum": self.naive_sum,
                "double_count": self.double_count, "n_actions": self.n_actions}


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
        return JointQuote(0.0, 0.0, 0.0, 0)
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
                      double_count=naive - group, n_actions=len(edges))


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


def select_set_by_declared_score(evaluations: Sequence[SetEvaluation],
                                 score: Callable,
                                 require_positive_score: bool = True) -> Optional[SetEvaluation]:
    """Step 5, shared by every arm. ONLY ``score`` may differ between arms.

    Enumeration, cardinality bound, joint cap, distinct-edge rule and
    tie-breaking are all supplied here, so the arms are matched by
    construction rather than by inspection.

    ``score`` returns a float or a tuple of floats; a tuple is compared
    lexicographically, which is how the frozen ``(f, q_acc)`` key works. Every
    arm uses this one path, so no arm can acquire a different tie discipline.

    Tie-breaking GENERALIZES the registered rule - "deterministic identifiers
    only, no hidden physical objective" - from one ``(edge, quant_index)``
    pair to the ascending tuples of a set: higher score first, then the lower
    edge-index tuple, then the lower quantity-menu-index tuple. Comparing
    tuples is the minimal generalization; no cardinality preference is
    imposed, because none is registered anywhere.

    ``require_positive_score`` implements the registered ``act_condition``:
    act only on a strictly positive score, otherwise rest.
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
        key = (tuple(_finite("score component", v) for v in raw)
               if isinstance(raw, tuple) else (_finite("score", raw),))
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

    Derived from committed authority: the ranking quantity is the registered
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
    """A set-level scoring rule that no committed authority determines."""


_B_AMBIGUITY = (
    "the matched non-EBU comparator has no registered set-level score. "
    "v30_o14_multi_edge_plan.json registers arm B as 'one outgoing action per "
    "source per micro-step', scored by the per-edge loss-aware force f_e with "
    "ties by larger q_acc then lower edge index. No aggregation of f_e over a "
    "set of edges is registered anywhere, and f_e is a per-edge marginal, so "
    "summing, maximising or averaging it across a set are all different rules "
    "with different physics. Register one explicitly before use.")

_S_AMBIGUITY = (
    "the stock-blind control has no registered set-level score. "
    "v30_o14_multi_edge_plan.json registers arm S's score as the per-candidate "
    "eta_e * q_acc * 1[declared demand rate > 0], described as a 'volume "
    "maximizer toward a demanding destination'. Summing delivered volume over "
    "a set is the natural reading of that phrase but is NOT registered, and "
    "the alternative of scoring only the best single action is equally "
    "consistent with the registered text. Register one explicitly before use.")


def _require_singletons(evaluations, ambiguity: str) -> None:
    """The ambiguity bites only for sets of size >= 2.

    For a singleton there is nothing to aggregate, so the registered
    per-candidate score applies directly and unambiguously. As soon as a set
    of two or more actions must be scored, an aggregation is needed and none
    is registered - so this fails closed rather than inventing one.
    """
    for evaluation in evaluations:
        if not isinstance(evaluation, SetEvaluation):
            raise MechanismError("evaluations must be SetEvaluation instances")
        if len(evaluation.actions) > 1:
            raise UnregisteredScoringRule(ambiguity)


def select_matched_non_ebu_joint(evaluations: Sequence[SetEvaluation],
                                 set_score: Optional[Callable] = None):
    """Arm B. Registered per-candidate score for singletons; else fails closed.

    With no ``set_score`` supplied this accepts only singleton sets, which it
    scores by the registered loss-aware force key ``(f, q_acc)``. Supply
    ``set_score`` once an author registers an aggregation; it is then routed
    through the same shared selector as every other arm, so the arms stay
    matched in enumeration, cap, bound, distinct-edge rule and ties.
    """
    if set_score is None:
        _require_singletons(evaluations, _B_AMBIGUITY)
        for evaluation in evaluations:
            for key in ("f", "q_acc"):
                if key not in evaluation.actions[0]:
                    raise MechanismError(
                        f"the matched comparator requires candidate key "
                        f"{key!r}")

        def set_score(evaluation):
            # q_acc is the ACCEPTED quantity, so under a joint cap it is the
            # allocation's, not the menu's independently-clamped figure. The
            # arms therefore all score the vector that would execute.
            action = evaluation.actions[0]
            return (float(action["f"]), float(evaluation.allocation.q_acc[0]))

        return select_set_by_declared_score(evaluations, set_score,
                                            require_positive_score=False)
    return select_set_by_declared_score(evaluations, set_score,
                                        require_positive_score=False)


def select_stock_blind_joint(evaluations: Sequence[SetEvaluation],
                             world: Optional[d0.World] = None,
                             demand_rate: Optional[Sequence[float]] = None,
                             set_score: Optional[Callable] = None):
    """Arm S. Registered per-candidate score for singletons; else fails closed.

    With no ``set_score`` supplied this accepts only singleton sets, scored by
    the registered ``eta_e * q_acc * 1[declared current-tick demand rate > 0]``,
    reading only the menu and the adjacent destination's declared demand rate.
    Its declared limitation - blindness to destination stock buffers - is the
    point of the control and is preserved.
    """
    if set_score is None:
        _require_singletons(evaluations, _S_AMBIGUITY)
        if not isinstance(world, d0.World):
            raise MechanismError(
                "the stock-blind control needs the world to read edge eta")
        if demand_rate is None:
            raise MechanismError(
                "the stock-blind control needs the declared demand rates")
        rates = tuple(_finite("demand_rate", value) for value in demand_rate)
        if len(rates) != world.n:
            raise MechanismError(
                "demand_rate length must equal the cell count")

        def set_score(evaluation):
            action = evaluation.actions[0]
            edge = world.edges[int(action["edge"])]
            indicator = 1.0 if rates[edge.j] > 0.0 else 0.0
            return (edge.eta * float(evaluation.allocation.q_acc[0])
                    * indicator)

        return select_set_by_declared_score(evaluations, set_score,
                                            require_positive_score=True)
    return select_set_by_declared_score(evaluations, set_score,
                                        require_positive_score=True)


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
