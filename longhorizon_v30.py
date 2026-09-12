"""Long-horizon normalized mechanism study - the four adopted mechanisms.

Implements ONLY the four gaps authorized for the first normalized mechanism
study (the deterministic N/H/X stress ladder, Option B, ``m = 2``, R-b
reserve-binding), as recorded in
``V3.0_LONG_HORIZON_NORMALIZED_MECHANISM_CANDIDATE.md``:

  1. joint two-action budget cap
  2. matched two-action selection (the non-EBU comparator and its matched
     exact-EBU and stock-blind counterparts)
  3. generalized request-shaping identity
  4. checkpoint and restart mechanism

EXECUTION SAFETY. This module is import-pure. It contains NO runner, NO tick
function, NO trajectory, NO multi-tick loop, and NO world construction, and it
never calls ``p1c_v29.p1c_step``, ``service_v30.bounded_step``, or any other
step function. The published P1C aggregate allocation rule is *reproduced*
from public ``p1c_v29`` entry points so that a selector can rank on the
quantities it would actually be allocated; reproducing a rule is not executing
a step.

FROZEN SOURCES. ``d0_v29``, ``p1c_v29`` and ``ebu_quote_v30`` are imported
read-only and unmodified. ``gate1dc_v30`` is deliberately NOT imported: it
builds and validates its locked plan at module scope, so importing it would
not be import-pure. Arm identifiers below are copied verbatim from the
registered plan and are asserted against it by the test suite, not here.

ADOPTED EBU MATHEMATICS, UNCHANGED. The governing value is only

    Delta_e(q) = V_loc(z) - V_loc(z + dt*S_e*q) - C_a(q)

evaluated as an exact finite endpoint difference by
``ebu_quote_v30.QuoteSchedule.exact``. This module never computes it. It
accepts an exact quote from the caller as an opaque ranking key and never
forms a per-unit value, a weighted burden function, a numerical quadrature, an
EBU wallet, a causal allocation, or a replacement objective.

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

import math
from dataclasses import dataclass
from typing import Callable, Mapping, Optional, Sequence

import d0_v29 as d0
import ebu_quote_v30 as eq
import p1c_v29 as p1c

__all__ = [
    "M_MAX", "ADOPTED_ARMS", "RESTRICTED_ARMS", "ARM_ROLES", "RANKING_BASIS",
    "CHECKPOINT_SCHEMA", "MechanismError", "RequestShapingViolation",
    "CheckpointChainError", "JointAllocation", "Checkpoint",
    "source_budget_rate", "joint_budget_cap", "select_actions",
    "select_matched_non_ebu", "select_exact_ebu", "select_stock_blind",
    "shaped_active_world", "check_request_shaping_identity",
    "config_digest", "make_checkpoint", "verify_chain", "resume_from",
]

# --------------------------------------------------------------------------
# adopted constants
# --------------------------------------------------------------------------
M_MAX = 2                       # D3-2: simultaneous-action bound

# Registered arm identifiers, verbatim from the locked plan. The first is the
# unrestricted capability reference; the rest are restricted policies sharing
# one menu, one joint cap and one cardinality bound.
ADOPTED_ARMS = (
    "A_full_multi_edge_p1c",
    "D_restricted_exact_total_quote_greedy",
    "B_restricted_matched_non_ebu",
    "S_restricted_local_service_priority",
)
RESTRICTED_ARMS = ADOPTED_ARMS[1:]
ARM_ROLES = {
    "A_full_multi_edge_p1c": "full-capability reference",
    "D_restricted_exact_total_quote_greedy": "exact-EBU restricted policy",
    "B_restricted_matched_non_ebu": "matched non-EBU restricted policy",
    "S_restricted_local_service_priority": "stock-blind control",
}

# The single declared selection semantics. Candidates are ranked INDIVIDUALLY
# on the arm's own key over the screened menu, the top `m` on distinct edges
# are taken, and the joint budget cap is applied to that set afterwards. This
# is the faithful generalization of the frozen single-action rule, which also
# ranks individually. Selecting a pair by a joint objective would be a
# different registered rule; it is not implemented, and asking for it fails
# closed. For m = 1 this reduces exactly to the frozen behaviour.
RANKING_BASIS = "menu_rank_then_joint_cap"

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
                     m: int = M_MAX) -> JointAllocation:
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
    if m > M_MAX:
        raise MechanismError(
            f"m={m} exceeds the adopted simultaneous-action bound {M_MAX}")
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
# mechanism 2 - matched two-action selection
# --------------------------------------------------------------------------
def select_actions(candidates: Sequence[Mapping],
                   score: Callable[[Mapping], float],
                   m: int = M_MAX,
                   require_positive_score: bool = False,
                   ranking_basis: str = RANKING_BASIS) -> tuple:
    """Select up to ``m`` candidates on distinct edges by a declared key.

    The ONLY thing that differs between the restricted arms is ``score``.
    Menu, cardinality bound, distinct-edge rule and tie-breaking are shared,
    which is what makes the comparators matched rather than merely similar.

    ``score`` returns a float or a tuple of floats; a tuple is compared
    lexicographically, which is how the frozen ``(f, q_acc)`` key works.

    Tie-breaking reproduces the frozen convention exactly: higher score first,
    then LOWER edge index, then LOWER quantity-menu index. Ordering is total
    and deterministic; no seed, sampling or adaptive rule is involved.

    ``require_positive_score`` reproduces the frozen drop rules for arms D and
    S, which decline to act when their key is not strictly positive.

    Returns candidates ordered by ascending edge index, which is the order the
    shaped active world and the request-shaping identity both use.
    """
    if ranking_basis != RANKING_BASIS:
        raise MechanismError(
            f"unknown ranking_basis {ranking_basis!r}; only {RANKING_BASIS!r} "
            "is implemented. Selecting a set by a joint objective would be a "
            "different registered rule and is deliberately not provided.")
    if not isinstance(m, int) or isinstance(m, bool) or m < 1:
        raise MechanismError(f"m must be a positive int, got {m!r}")
    if m > M_MAX:
        raise MechanismError(
            f"m={m} exceeds the adopted simultaneous-action bound {M_MAX}")
    candidates = tuple(candidates)
    for candidate in candidates:
        _validate_candidate(candidate)
    if not candidates:
        return ()

    def key_of(candidate):
        value = score(candidate)
        if isinstance(value, tuple):
            return tuple(_finite("score component", v) for v in value)
        return (_finite("score", value),)

    # Each key is evaluated exactly ONCE, so a score callable cannot change
    # the answer between ranking and the positivity filter.
    decorated = []
    arity = None
    for candidate in candidates:
        key = key_of(candidate)
        if arity is None:
            arity = len(key)
        elif len(key) != arity:
            raise MechanismError(
                "score must return keys of uniform arity; lexicographic "
                "comparison of different-length keys has no declared meaning")
        decorated.append((tuple(-v for v in key), int(candidate["edge"]),
                          int(candidate["quant_index"]), key, candidate))
    decorated.sort(key=lambda row: row[:3])

    picked = []
    used = set()
    for _negated, edge, _quant, key, candidate in decorated:
        if len(picked) >= m:
            break
        if edge in used:
            continue
        if require_positive_score and not key[0] > 0.0:
            continue
        picked.append(candidate)
        used.add(edge)
    return tuple(sorted(picked, key=lambda c: int(c["edge"])))


def select_matched_non_ebu(candidates: Sequence[Mapping],
                           m: int = M_MAX) -> tuple:
    """Arm B. Rank by the physical force, then by accepted quantity.

    Matched to the exact-EBU arm in every respect except the key: same menu,
    same joint cap, same bound, same tie-breaking. It never consults an EBU
    value. Reproduces ``select_arm_B``'s key ``(f, q_acc)`` and, at ``m = 1``,
    its selection exactly.
    """
    for candidate in candidates:
        for key in ("f", "q_acc"):
            if key not in candidate:
                raise MechanismError(
                    f"matched non-EBU comparator requires candidate key {key!r}")

    # The frozen key is the lexicographic pair (f, q_acc); it is passed
    # through the SHARED selector so menu, bound, distinct-edge rule and
    # tie-breaking are identical to the other arms by construction.
    return select_actions(
        candidates,
        lambda c: (float(c["f"]), float(c["q_acc"])),
        m=m, require_positive_score=False)


def select_exact_ebu(candidates: Sequence[Mapping],
                     exact_quotes: Sequence[float],
                     m: int = M_MAX) -> tuple:
    """Arm D. Rank by the EXACT finite total local EBU quote only.

    ``exact_quotes[k]`` must be ``QuoteSchedule.exact(q)`` for
    ``candidates[k]``, computed by the caller from the authoritative equation.
    Per-unit values never enter, and a non-positive quote is declined, exactly
    as ``select_arm_D`` does.
    """
    candidates = tuple(candidates)
    quotes = tuple(_finite("exact quote", value) for value in exact_quotes)
    if len(candidates) != len(quotes):
        raise MechanismError("candidates/exact_quotes length mismatch")
    quote_by_id = {id(candidate): quote
                   for candidate, quote in zip(candidates, quotes)}
    if len(quote_by_id) != len(candidates):
        raise MechanismError(
            "candidates must be distinct objects so each maps to one quote")
    return select_actions(candidates, lambda c: quote_by_id[id(c)], m=m,
                          require_positive_score=True)


def select_stock_blind(candidates: Sequence[Mapping], world: d0.World,
                       demand_rate: Sequence[float], m: int = M_MAX) -> tuple:
    """Arm S. The registered stock-blind positive control.

    Score ``eta_e * q_acc * 1[declared current-tick demand rate > 0]``, reading
    only the menu and the adjacent destination's declared demand rate, exactly
    as ``select_arm_S`` does. Its declared limitation - blindness to
    destination stock buffers - is the point of the control and is preserved.
    """
    if not isinstance(world, d0.World):
        raise MechanismError("world must be a d0_v29.World")
    rates = tuple(_finite("demand_rate", value) for value in demand_rate)
    if len(rates) != world.n:
        raise MechanismError("demand_rate length must equal the cell count")
    for candidate in candidates:
        if "q_acc" not in candidate:
            raise MechanismError("stock-blind control requires 'q_acc'")
        _validate_candidate(candidate)
        if int(candidate["edge"]) >= len(world.edges):
            raise MechanismError(
                f"edge index {candidate['edge']} out of range")

    def score(candidate):
        edge = world.edges[int(candidate["edge"])]
        indicator = 1.0 if rates[edge.j] > 0.0 else 0.0
        return edge.eta * float(candidate["q_acc"]) * indicator

    return select_actions(candidates, score, m=m, require_positive_score=True)


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
    if len(selected) > M_MAX:
        raise MechanismError(
            f"{len(selected)} actions exceed the bound {M_MAX}")
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
