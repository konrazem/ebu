"""
Energy Balance - V3.0 Gate 1B: pure observational local signed EBU quote.

Implements exactly the settlement equation frozen by the hash-locked plan
v30_quote_validation_plan.json (canonical SHA-256
a1916e8ecf366cee93a5284a0d8fcb68a3e1a429f49ce62b9f5914df87f94061), derived in
V3.0_LOCAL_EBU_FOUNDATION_DRAFT.md and audited by
V3.0_GATE1_INDEPENDENT_REVIEW.md (verdict: PASS WITH CORRECTIONS, all
corrections adopted at Gate 1A.1 and normative here):

    z = x^n + dt * u(x^n)                     (frozen no-action successor)
    de(q) = V_loc(z) - V_loc(z + dt*S_e*q) - C_a(q)
          = v_i(z_i) + v_j(z_j)
            - v_i(z_i - dt*q) - v_j(z_j + dt*eta*q) - C_a(q)

EPISTEMIC STATUS (read before use):
  * This module is OBSERVATIONAL ONLY. It never mutates physical state, never
    replaces or reinterprets P1C, holds no wallet, health, price, market,
    debt, or actor-economy state, evaluates no global functional, and
    performs no future rollout.
  * The EXACT finite difference defines settlement. The first-order form
    de_lin(q) = dt*q*(mu_i - eta*mu_j) - C_a(q) is exposed ONLY as a
    diagnostic (linear_diagnostic) and must never become a settlement value.
  * P1C (p1c_v29.py, unchanged) remains the physical permission layer: this
    module receives q_acc and quotes only [0, q_acc]. A positive quote never
    authorizes anything.
  * Overexecution (q_meas > q_acc) implements ONLY the registered minimum
    fail-closed envelope; full settlement semantics are OPEN (O8).
  * Passing tests are numerical validation at declared points, never proof.

Reuses the released local physical definitions of d0_v29 (penalty, marginal,
LocalView) rather than forking them. Standard library only. Never imports a
test module.
"""
from __future__ import annotations
import hashlib
import json
import math
from dataclasses import dataclass, field
from typing import Optional

import d0_v29 as d0

__all__ = [
    "EQUATION_VERSION", "ALLOWED_COST_CATEGORY", "FORBIDDEN_COST_CATEGORIES",
    "canonical_json", "commitment_hash",
    "ProcessCost", "LocalQuoteInput", "QuoteEpoch", "QuoteSchedule",
    "QuoteEvaluation", "ProtocolViolation", "SettlementResult",
    "EpochRegistry", "build_quote", "epoch_identifier",
]

# The equation/version identifier bound into every epoch. Must match the
# locked plan's quote_law.version.
EQUATION_VERSION = "v3.0-gate0.1"

# Def 6.4 (Gate 1A.1): C_a represents ONLY declared action-process burden not
# already represented by the state transition or the V_loc difference.
ALLOWED_COST_CATEGORY = "unrepresented_action_process_burden"
FORBIDDEN_COST_CATEGORIES = (
    "state_carried_burden",   # category 1: already inside the V_loc difference
    "monetary_cost",          # category 3
    "labour_cost",            # category 3
    "audit_penalty",          # category 4
    "fraud_penalty",          # category 4
    "unspecified",
)


# ---------------------------------------------------------------------------
# validation helpers (mirror the d0_v29 fail-closed style)
# ---------------------------------------------------------------------------
def _req_finite(name: str, v) -> float:
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        raise TypeError(f"{name} must be a finite real number, got {type(v).__name__}")
    v = float(v)
    if not math.isfinite(v):
        raise ValueError(f"{name} must be finite, got {v!r}")
    return v


def _req_nonneg(name: str, v) -> float:
    v = _req_finite(name, v)
    if v < 0.0:
        raise ValueError(f"{name} must be >= 0, got {v}")
    return v


def _req_str(name: str, v) -> str:
    if not isinstance(v, str):
        raise TypeError(f"{name} must be a string, got {type(v).__name__}")
    return v


def _req_int(name: str, v) -> int:
    if isinstance(v, bool) or not isinstance(v, int):
        raise TypeError(f"{name} must be an integer, got {type(v).__name__}")
    return v


def canonical_json(obj) -> str:
    """Strict canonical JSON: sorted keys, compact separators, ASCII only,
    fail-closed on NaN/Infinity (allow_nan=False). Every identifier, schedule
    commitment, and saved record must pass through this."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)


def commitment_hash(obj) -> str:
    """SHA-256 of the canonical strict JSON of obj (deterministic id)."""
    return hashlib.sha256(canonical_json(obj).encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# declarative process cost (Def 6.4 / 6.13a; NOT an arbitrary callback)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ProcessCost:
    """Immutable declarative action-process cost:

        C(0) = 0
        C(q) = c0 + c1*q + c2*q^2      for q > 0

    with validated non-negative coefficients. `category` MUST be the single
    allowed value: the code cannot verify real-world honesty, but it fails
    closed on any category that would be a double count (state-carried
    burden) or a silent unit-laundering (monetary/labour) or a layer
    violation (audit/fraud penalty), per the Gate-1A review section E.

    q = 0 is an exact separate branch (Def 6.13a): it is never approximated
    by the q -> 0+ limit when c0 > 0."""
    category: str
    c0: float = 0.0
    c1: float = 0.0
    c2: float = 0.0

    def __post_init__(self):
        cat = _req_str("category", self.category)
        if cat in FORBIDDEN_COST_CATEGORIES:
            raise ValueError(
                f"cost category {cat!r} is forbidden in C_a: state-carried "
                "burden is priced by the V_loc difference only; monetary/"
                "labour cost must not silently become physical EBU cost; "
                "audit/fraud penalties belong to the security layer "
                "(no-double-count condition, Def 6.4)")
        if cat != ALLOWED_COST_CATEGORY:
            raise ValueError(
                f"cost category must be {ALLOWED_COST_CATEGORY!r}, got {cat!r}")
        _req_nonneg("c0", self.c0)
        _req_nonneg("c1", self.c1)
        _req_nonneg("c2", self.c2)

    def cost(self, q: float) -> float:
        q = _req_nonneg("q", q)
        if q == 0.0:
            return 0.0                      # exact separate branch, never a limit
        return self.c0 + self.c1 * q + self.c2 * q * q

    @property
    def cost_id(self) -> str:
        return commitment_hash({
            "kind": "process_cost", "category": self.category,
            "c0": float(self.c0), "c1": float(self.c1), "c2": float(self.c2)})


# ---------------------------------------------------------------------------
# frozen local quote input (the ONLY information the quote may read; §4.2)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class LocalQuoteInput:
    """Frozen local data for one edge action i -> j. Accepts ONLY two
    d0_v29.LocalView endpoints (never a world, grid, full state vector,
    wallet, health, price, or any global object), the frozen local drives,
    and the declared action data. q_acc must come from P1C; this module
    never chooses, enlarges, or reinterprets it."""
    src: d0.LocalView
    dst: d0.LocalView
    u_src: float
    u_dst: float
    dt: float
    eta: float
    q_req: float
    q_acc: float
    source_id: int
    dest_id: int
    config_id: str

    def __post_init__(self):
        if not isinstance(self.src, d0.LocalView) or not isinstance(self.dst, d0.LocalView):
            raise TypeError("LocalQuoteInput accepts d0_v29.LocalView endpoints "
                            "only - never a world, grid, full state, or any "
                            "global/economic object")
        _req_finite("u_src", self.u_src)
        _req_finite("u_dst", self.u_dst)
        dt = _req_finite("dt", self.dt)
        if dt <= 0.0:
            raise ValueError(f"dt must be > 0, got {dt}")
        eta = _req_finite("eta", self.eta)
        if not (0.0 <= eta <= 1.0):
            raise ValueError(f"eta must be in [0, 1], got {eta}")
        q_req = _req_nonneg("q_req", self.q_req)
        q_acc = _req_nonneg("q_acc", self.q_acc)
        if q_acc > q_req:
            raise ValueError(f"q_acc ({q_acc}) must not exceed q_req ({q_req}); "
                             "q_acc is the P1C-accepted quantity")
        _req_int("source_id", self.source_id)
        _req_int("dest_id", self.dest_id)
        _req_str("config_id", self.config_id)

    @property
    def z_src(self) -> float:
        return self.src.x + self.dt * self.u_src

    @property
    def z_dst(self) -> float:
        return self.dst.x + self.dt * self.u_dst

    def state_commitment(self) -> str:
        v = self
        return commitment_hash({
            "kind": "local_quote_input",
            "src": {"x": v.src.x, "alpha": v.src.alpha, "beta": v.src.beta,
                    "chi": v.src.chi, "L": v.src.L, "U": v.src.U,
                    "R": v.src.R, "K": v.src.K},
            "dst": {"x": v.dst.x, "alpha": v.dst.alpha, "beta": v.dst.beta,
                    "chi": v.dst.chi, "L": v.dst.L, "U": v.dst.U,
                    "R": v.dst.R, "K": v.dst.K},
            "u_src": float(v.u_src), "u_dst": float(v.u_dst),
            "dt": float(v.dt), "eta": float(v.eta),
            "q_req": float(v.q_req), "q_acc": float(v.q_acc),
            "source_id": v.source_id, "dest_id": v.dest_id,
            "config_id": v.config_id})


# ---------------------------------------------------------------------------
# quote epoch (§5.1: binds the full committed context)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class QuoteEpoch:
    """One quote epoch. epoch_id is deterministically derived from every
    bound field (epoch_identifier); the registry re-derives and verifies it
    at registration and settlement (tamper / mismatched-binding detection)."""
    equation_version: str
    allocation_pass_id: str
    state_commitment: str
    source_id: int
    dest_id: int
    config_id: str
    dt: float
    eta: float
    q_req: float
    q_acc: float
    cost_id: str
    tick: int
    micro_step: int
    attribution_id: str
    epoch_id: str


def epoch_identifier(e: QuoteEpoch) -> str:
    """Deterministic epoch/event identifier from canonical committed data."""
    return commitment_hash({
        "kind": "quote_epoch",
        "equation_version": e.equation_version,
        "allocation_pass_id": e.allocation_pass_id,
        "state_commitment": e.state_commitment,
        "source_id": e.source_id, "dest_id": e.dest_id,
        "config_id": e.config_id,
        "dt": float(e.dt), "eta": float(e.eta),
        "q_req": float(e.q_req), "q_acc": float(e.q_acc),
        "cost_id": e.cost_id,
        "tick": e.tick, "micro_step": e.micro_step,
        "attribution_id": e.attribution_id})


# ---------------------------------------------------------------------------
# quote schedule and evaluation
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class QuoteEvaluation:
    """One evaluated point of a committed schedule. `exact` is the settlement
    quantity; `linear_diagnostic` is analysis-only and never settles."""
    epoch_id: str
    q: float
    exact: float
    linear_diagnostic: float


@dataclass(frozen=True)
class QuoteSchedule:
    """The committed object: the complete exact function q -> de(q) on
    [0, q_acc], deterministically recoverable from these immutable committed
    parameters (no sampled table needed; the piecewise-quadratic family is
    exact). All decision inputs are frozen local data only."""
    epoch: QuoteEpoch
    inp: LocalQuoteInput
    cost: ProcessCost

    def _domain(self, name: str, q) -> float:
        q = _req_nonneg(name, q)
        if q > self.inp.q_acc:
            raise ValueError(
                f"{name}={q} outside the committed schedule domain "
                f"[0, q_acc={self.inp.q_acc}]; the positive schedule is never "
                "extended beyond the physically accepted quantity")
        return q

    def state_difference(self, q: float) -> float:
        """V_loc(z) - V_loc(z + dt*S_e*q), exact, affected cells only
        (exact locality under separability, foundation Lemma 6.6)."""
        q = self._domain("q", q)
        v = self.inp
        s, d = v.src, v.dst
        before = (d0.penalty(s.alpha, s.beta, s.chi, s.L, s.U, s.R, v.z_src)
                  + d0.penalty(d.alpha, d.beta, d.chi, d.L, d.U, d.R, v.z_dst))
        after = (d0.penalty(s.alpha, s.beta, s.chi, s.L, s.U, s.R,
                            v.z_src - v.dt * q)
                 + d0.penalty(d.alpha, d.beta, d.chi, d.L, d.U, d.R,
                              v.z_dst + v.dt * v.eta * q))
        return before - after

    def exact(self, q: float) -> float:
        """THE settlement value: exact finite difference minus process cost.
        q = 0 is the exact zero branch (state part and C are both exactly 0)."""
        q = self._domain("q", q)
        return self.state_difference(q) - self.cost.cost(q)

    def linear_diagnostic(self, q: float) -> float:
        """First-order form dt*q*(mu_i - eta*mu_j) - C(q). DIAGNOSTIC ONLY:
        over-quotes for convex v (foundation Thm 6.9) and must never settle."""
        q = self._domain("q", q)
        v = self.inp
        s, d = v.src, v.dst
        mu_i = d0.marginal(s.alpha, s.beta, s.chi, s.L, s.U, s.R, v.z_src)
        mu_j = d0.marginal(d.alpha, d.beta, d.chi, d.L, d.U, d.R, v.z_dst)
        return v.dt * q * (mu_i - v.eta * mu_j) - self.cost.cost(q)

    def evaluate(self, q: float) -> QuoteEvaluation:
        return QuoteEvaluation(epoch_id=self.epoch.epoch_id, q=float(q),
                               exact=self.exact(q),
                               linear_diagnostic=self.linear_diagnostic(q))


def build_quote(inp: LocalQuoteInput, cost: ProcessCost,
                allocation_pass_id: str, tick: int, micro_step: int,
                attribution_id: str = "") -> QuoteSchedule:
    """Construct the committed quote schedule for one accepted action.
    Purely functional: reads only the frozen LocalQuoteInput and the declared
    cost; mutates nothing."""
    if not isinstance(inp, LocalQuoteInput):
        raise TypeError("build_quote requires a LocalQuoteInput")
    if not isinstance(cost, ProcessCost):
        raise TypeError("build_quote requires a declarative ProcessCost "
                        "(arbitrary callbacks are not auditable)")
    _req_str("allocation_pass_id", allocation_pass_id)
    _req_int("tick", tick)
    _req_int("micro_step", micro_step)
    _req_str("attribution_id", attribution_id)
    partial = QuoteEpoch(
        equation_version=EQUATION_VERSION,
        allocation_pass_id=allocation_pass_id,
        state_commitment=inp.state_commitment(),
        source_id=inp.source_id, dest_id=inp.dest_id,
        config_id=inp.config_id,
        dt=inp.dt, eta=inp.eta, q_req=inp.q_req, q_acc=inp.q_acc,
        cost_id=cost.cost_id, tick=tick, micro_step=micro_step,
        attribution_id=attribution_id, epoch_id="")
    eid = epoch_identifier(partial)
    epoch = QuoteEpoch(**{**partial.__dict__, "epoch_id": eid})
    return QuoteSchedule(epoch=epoch, inp=inp, cost=cost)


# ---------------------------------------------------------------------------
# violations and settlement results
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ProtocolViolation:
    """Audit-layer record. Never a valuation: a violation issues nothing and
    invents no punishment (Def 6.13b)."""
    kind: str            # overexecution | stale_epoch | duplicate_settlement |
                         # expired_epoch | wrong_equation_version |
                         # mismatched_binding | unregistered_epoch |
                         # malformed_measurement | negative_quantity |
                         # production_rule
    epoch_id: str
    q_meas: Optional[float] = None
    q_acc: Optional[float] = None
    overdraw: Optional[float] = None
    physical_debt_handling_required: bool = False
    o8_open: bool = False
    note: str = ""

    def record(self) -> str:
        return canonical_json({
            "kind": self.kind, "epoch_id": self.epoch_id,
            "q_meas": self.q_meas, "q_acc": self.q_acc,
            "overdraw": self.overdraw,
            "physical_debt_handling_required": self.physical_debt_handling_required,
            "o8_open": self.o8_open, "note": self.note})


@dataclass(frozen=True)
class SettlementResult:
    """Outcome of one settlement attempt. `issued` is the settled signed EBU
    amount for status 'settled' (may be negative: a precommitted debit) and
    exactly 0.0 for every violation. This is an audit record, not a wallet."""
    status: str                       # "settled" | "violation"
    epoch_id: str
    q_meas: Optional[float]
    issued: float
    violation: Optional[ProtocolViolation] = None

    def record(self) -> str:
        return canonical_json({
            "status": self.status, "epoch_id": self.epoch_id,
            "q_meas": self.q_meas, "issued": self.issued,
            "violation": None if self.violation is None
            else json.loads(self.violation.record())})


# ---------------------------------------------------------------------------
# epoch registry (a small dedicated audit registry - NOT a wallet or ledger)
# ---------------------------------------------------------------------------
class EpochRegistry:
    """Tracks committed epochs, allocation-pass staleness, the first-model
    production rule (one action per source per micro-step for overlapping
    support), and settled/consumed event identifiers.

    It holds NO balances, NO wallet, NO economic state, and never touches
    physical state. Rejections issue nothing."""

    def __init__(self, equation_version: str = EQUATION_VERSION):
        self.equation_version = _req_str("equation_version", equation_version)
        self._epochs: dict = {}          # epoch_id -> QuoteSchedule
        self._by_slot: dict = {}         # (source_id, tick, micro_step) -> epoch_id
        self._stale_passes: set = set()
        self._consumed: set = set()      # settled or violation-consumed epoch ids
        self.violations: list = []

    # -- registration ------------------------------------------------------
    def register(self, schedule: QuoteSchedule) -> str:
        if not isinstance(schedule, QuoteSchedule):
            raise TypeError("register requires a QuoteSchedule")
        e = schedule.epoch
        if e.equation_version != self.equation_version:
            raise ValueError(f"wrong equation version {e.equation_version!r}; "
                             f"registry expects {self.equation_version!r}")
        if epoch_identifier(e) != e.epoch_id:
            raise ValueError("epoch identifier does not match its committed "
                             "fields (mismatched binding)")
        slot = (e.source_id, e.tick, e.micro_step)
        if slot in self._by_slot:
            raise ValueError(
                f"production rule: one action per source per micro-step - "
                f"source {e.source_id} already has a committed epoch at tick "
                f"{e.tick} micro-step {e.micro_step} (first-model restriction; "
                "shared-source simultaneity is the registered open extension O3)")
        self._epochs[e.epoch_id] = schedule
        self._by_slot[slot] = e.epoch_id
        return e.epoch_id

    # -- rejection / reallocation (§5.1 first-model semantics) --------------
    def reject(self, epoch_id: str) -> None:
        """Actor rejection: the action becomes zero. Freed capacity is NOT
        redistributed in this epoch; every other committed schedule remains
        unchanged and valid. (The epoch is consumed and cannot settle.)"""
        _req_str("epoch_id", epoch_id)
        if epoch_id in self._epochs:
            self._consumed.add(epoch_id)

    def invalidate_allocation_pass(self, allocation_pass_id: str) -> None:
        """A reallocation opens a NEW allocation pass; every epoch of the old
        pass becomes stale and can never settle."""
        self._stale_passes.add(_req_str("allocation_pass_id", allocation_pass_id))

    # -- settlement ---------------------------------------------------------
    def _reject(self, kind: str, epoch_id: str, q_meas=None, q_acc=None,
                overdraw=None, requires_physical_handling=False, o8=False,
                note="") -> SettlementResult:
        v = ProtocolViolation(kind=kind, epoch_id=epoch_id, q_meas=q_meas,
                              q_acc=q_acc, overdraw=overdraw,
                              physical_debt_handling_required=requires_physical_handling,
                              o8_open=o8, note=note)
        self.violations.append(v)
        return SettlementResult(status="violation", epoch_id=epoch_id,
                                q_meas=q_meas, issued=0.0, violation=v)

    def settle(self, schedule: QuoteSchedule, q_meas,
               execution_tick: int, execution_micro_step: int) -> SettlementResult:
        """Audit/settlement boundary. Selection from the precommitted exact
        schedule for 0 <= q_meas <= q_acc; the registered minimum fail-closed
        envelope for q_meas > q_acc (O8 remains open); explicit rejection for
        every malformed, stale, expired, mismatched, or duplicate case."""
        if not isinstance(schedule, QuoteSchedule):
            raise TypeError("settle requires a QuoteSchedule")
        e = schedule.epoch
        eid = e.epoch_id
        # 1. malformed measurement (fail closed before anything else)
        if isinstance(q_meas, bool) or not isinstance(q_meas, (int, float)) \
                or not math.isfinite(float(q_meas)):
            return self._reject("malformed_measurement", eid, note=repr(q_meas))
        q_meas = float(q_meas)
        # 2. negative measured quantity
        if q_meas < 0.0:
            return self._reject("negative_quantity", eid, q_meas=q_meas)
        # 3. epoch must be registered here
        if eid not in self._epochs:
            return self._reject("unregistered_epoch", eid, q_meas=q_meas,
                                note="epoch was never committed to this registry")
        # 4. binding integrity (tamper detection)
        if epoch_identifier(e) != eid or self._epochs[eid].epoch != e:
            return self._reject("mismatched_binding", eid, q_meas=q_meas)
        # 5. equation version
        if e.equation_version != self.equation_version:
            return self._reject("wrong_equation_version", eid, q_meas=q_meas)
        # 6. staleness (superseded allocation pass)
        if e.allocation_pass_id in self._stale_passes:
            return self._reject("stale_epoch", eid, q_meas=q_meas,
                                note="allocation pass was superseded; old "
                                     "quotes are invalid (§5.1)")
        # 7. expiration (epoch is valid only for its own tick/micro-step)
        if execution_tick != e.tick or execution_micro_step != e.micro_step:
            return self._reject("expired_epoch", eid, q_meas=q_meas,
                                note=f"epoch bound to tick {e.tick} micro "
                                     f"{e.micro_step}, execution at "
                                     f"{execution_tick}/{execution_micro_step}")
        # 8. duplicate settlement / consumed epoch
        if eid in self._consumed:
            return self._reject("duplicate_settlement", eid, q_meas=q_meas,
                                note="this event identifier already settled "
                                     "or was consumed")
        # 9. overexecution: ONLY the registered minimum fail-closed envelope.
        if q_meas > e.q_acc:
            self._consumed.add(eid)
            return self._reject(
                "overexecution", eid, q_meas=q_meas, q_acc=e.q_acc,
                overdraw=q_meas - e.q_acc, requires_physical_handling=True,
                o8=True,
                note="never positive credit; the committed schedule is not "
                     "extended beyond q_acc; physical/ecological-debt "
                     "handling is required externally; settlement semantics "
                     "beyond q_acc are OPEN (O8) - no post-hoc rule is "
                     "invented, no debit is silently applied")
        # 10. settle: selection from the precommitted exact function.
        value = schedule.exact(q_meas)
        self._consumed.add(eid)
        return SettlementResult(status="settled", epoch_id=eid,
                                q_meas=q_meas, issued=value, violation=None)
