"""Safe harness architecture for prospective EBU study work.

This module is INFRASTRUCTURE.  It defines no world, no potential, no
parameter, no hypothesis, no metric value, no threshold and no outcome
interpretation, and it contains **no default for any of them**.  It supplies
the *mechanisms* the study architecture requires, each fail-closed, so that a
future adopted protocol has something correct to be filled into.

Scope is set by `V3.0_LONG_RUN_STUDY_FRAMEWORK.md` (architecture) and coordinate
W-2 in `V3.0_PROGRAMME_AUTHORITY_COORDINATE.md`.  The pieces built here are the
ones that are safe to build before any science is authorized:

    physical conservation .......... ConservationProfile, check_closure
    immutable state handling ....... State
    deterministic demand replay .... DemandStream
    controller boundaries .......... InformationBoundary
    receipts / audit ............... Receipt, receipt_chain
    event logs ..................... EventLog
    negative controls .............. NegativeControl, run_negative_control
    reproducibility ................ reproducibility_stamp
    metrics ........................ MetricSpec, evaluate_metrics
    classifications ................ ClassificationScheme
    preregistration support ........ delegated to study_protocol_schema.py

**Execution safety.**  Nothing here runs a model, a tick, a trajectory, a
simulation, a runner, a parameter search or a network call, and nothing opens a
file.  Every function is pure, or pure plus an in-memory append.  `State` and
`DemandStream` operate on frozen or synthetic INDIVIDUAL states; neither
advances model state, and no function in this module iterates a dynamics.

**What this module must never become.**  It must not acquire a world, a default
parameter, a default metric, a default threshold, or an outcome interpretation.
Each of those is a slot in `study_protocol_schema.SLOTS`, owned by the author.
A default here would silently invent science, which is the specific failure the
slot design exists to prevent.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Sequence

import authority_coordinate as ac

__all__ = [
    "HarnessError", "ConservationRefusal", "ImmutabilityViolation",
    "InformationLeak", "AuditChainBroken", "NegativeControlPassed",
    "DeclarationMissing",
    "canonical_bytes", "digest",
    "ACCOUNT_LEVELS", "RESIDUAL_POLICIES", "CONSERVATION_PROFILE_FIELDS",
    "ConservationProfile", "Ledger", "check_closure",
    "State", "DemandStream", "InformationBoundary",
    "Receipt", "receipt_chain", "EventLog",
    "NegativeControl", "run_negative_control",
    "reproducibility_stamp",
    "MetricSpec", "evaluate_metrics", "ClassificationScheme",
    "harness_is_executable",
]


# ---------------------------------------------------------------------------
# refusals
# ---------------------------------------------------------------------------
class HarnessError(Exception):
    """Base: the harness refused."""


class ConservationRefusal(HarnessError):
    """A declared conservation profile was violated, or was never declared."""


class ImmutabilityViolation(HarnessError):
    """An attempt to mutate a frozen state or a sealed record."""


class InformationLeak(HarnessError):
    """A controller read outside its declared information boundary."""


class AuditChainBroken(HarnessError):
    """A receipt or event chain does not verify."""


class NegativeControlPassed(HarnessError):
    """A control that MUST fail did not fail. This is a harness failure."""


class DeclarationMissing(HarnessError):
    """Something required was not declared. There is never a default."""


# ---------------------------------------------------------------------------
# canonicalization - one encoding, used by every digest in the module
# ---------------------------------------------------------------------------
def canonical_bytes(value: Any) -> bytes:
    """Canonical JSON: sorted keys, compact, ASCII, no NaN or Infinity.

    Matches ``study_protocol_schema.canonical_bytes`` so that a protocol hash
    and a harness digest are produced by the same rule.  ``allow_nan=False`` is
    load-bearing: a NaN that hashed successfully would make two different
    states collide into one "reproducible" digest.
    """
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def digest(value: Any) -> str:
    """SHA-256 over the canonical encoding."""
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


# ---------------------------------------------------------------------------
# 1. physical conservation
# ---------------------------------------------------------------------------
# Account levels per CONSERVATION_AND_BOUNDARY_ACCOUNTING_FOUNDATION.md 14.2:
# the profile "must allow Level 1 and Level 2 accounts. It must not require
# every domain to pretend to be Level 3."
ACCOUNT_LEVELS = (1, 2, 3)

# "exact or uncertainty-aware residual policy" - both are permitted, and which
# one applies is declared, never inferred from how the numbers happen to land.
RESIDUAL_POLICIES = ("exact", "uncertainty_aware")

# The ten fields section 14.2 requires a profile to contain "at least".
CONSERVATION_PROFILE_FIELDS = (
    "profile_id", "profile_version", "account_level", "boundary_id",
    "boundary_hierarchy", "quantity_id", "units", "state_coordinates",
    "internal_transformation", "boundary_channels", "sign_convention",
    "observability", "residual_policy", "non_claims",
)


@dataclass(frozen=True)
class ConservationProfile:
    """One declared boundary/conservation profile for ONE quantity.

    Every field is required.  A profile that omits anything refuses rather than
    defaulting, because "conservation" with an undefined field list is an
    undefined claim (framework slot S-Q).
    """
    profile_id: str
    profile_version: str
    account_level: int
    boundary_id: str
    boundary_hierarchy: tuple
    quantity_id: str
    units: str
    state_coordinates: tuple
    internal_transformation: str
    boundary_channels: tuple
    sign_convention: str
    observability: str
    residual_policy: str
    non_claims: tuple
    tolerance: float = 0.0

    def __post_init__(self):
        for name in ("profile_id", "profile_version", "boundary_id",
                     "quantity_id", "units", "internal_transformation",
                     "sign_convention", "observability"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise DeclarationMissing(
                    f"conservation profile field {name!r} must be a non-empty "
                    f"string; section 14.2 requires it and there is no default")
        if self.account_level not in ACCOUNT_LEVELS:
            raise DeclarationMissing(
                f"account_level must be one of {ACCOUNT_LEVELS}; Level 1 and "
                f"Level 2 accounts are explicitly permitted and a domain is "
                f"never required to pretend to be Level 3")
        if self.residual_policy not in RESIDUAL_POLICIES:
            raise DeclarationMissing(
                f"residual_policy must be one of {RESIDUAL_POLICIES}")
        if not self.state_coordinates:
            raise DeclarationMissing(
                "state_coordinates must name the coordinates entering c_q")
        if not self.boundary_channels:
            raise DeclarationMissing(
                "boundary_channels must be declared, even if empty of flow: "
                "an undeclared channel is an unaccounted one")
        if not self.non_claims:
            raise DeclarationMissing(
                "non_claims must state explicitly what isolation and "
                "completeness are NOT claimed; 14.2 requires it")
        if self.residual_policy == "exact" and self.tolerance != 0.0:
            raise DeclarationMissing(
                "an 'exact' residual policy cannot carry a non-zero "
                "tolerance; declare 'uncertainty_aware' instead of widening "
                "'exact' until a residual fits")
        if self.tolerance < 0.0:
            raise DeclarationMissing("tolerance must be non-negative")


@dataclass(frozen=True)
class Ledger:
    """The accounting of one quantity across one declared transition.

    ``interior_before``/``interior_after`` are the interior content; ``flows``
    maps a declared boundary channel to its signed contribution.  Nothing here
    is computed from a model: the caller supplies frozen or synthetic numbers
    and this structure only says what closure would mean.
    """
    quantity_id: str
    interior_before: float
    interior_after: float
    flows: Mapping[str, float]

    def residual(self) -> float:
        """(after - before) - sum(flows). Zero iff the account closes."""
        return ((self.interior_after - self.interior_before)
                - sum(self.flows.values()))


def check_closure(profile: ConservationProfile, ledger: Ledger) -> float:
    """Refuse unless the ledger closes under the DECLARED profile.

    Returns the residual when it is acceptable.  Three refusals, in order:

    1. the ledger is for a different quantity than the profile declares;
    2. the ledger uses a channel the profile never declared - an undeclared
       channel is exactly how an unaccounted flow enters an account;
    3. the residual exceeds what the declared residual policy permits.

    Note the direction of (3): the policy is fixed first and the residual is
    judged against it.  Choosing the policy after seeing the residual is how a
    conservation claim becomes unfalsifiable.
    """
    if ledger.quantity_id != profile.quantity_id:
        raise ConservationRefusal(
            f"ledger quantity {ledger.quantity_id!r} does not match profile "
            f"quantity {profile.quantity_id!r}")
    declared = set(profile.boundary_channels)
    used = set(ledger.flows)
    undeclared = tuple(sorted(used - declared))
    if undeclared:
        raise ConservationRefusal(
            f"ledger uses undeclared boundary channel(s) {undeclared}; "
            f"profile {profile.profile_id!r} declares {tuple(sorted(declared))}. "
            f"An undeclared channel is an unaccounted flow.")
    residual = ledger.residual()
    limit = 0.0 if profile.residual_policy == "exact" else profile.tolerance
    if abs(residual) > limit:
        raise ConservationRefusal(
            f"conservation residual {residual!r} exceeds the limit {limit!r} "
            f"declared by residual_policy {profile.residual_policy!r} for "
            f"quantity {profile.quantity_id!r} at account level "
            f"{profile.account_level}. The profile is not widened to fit.")
    return residual


# ---------------------------------------------------------------------------
# 2. immutable state handling
# ---------------------------------------------------------------------------
class State(Mapping):
    """A frozen, hashable, canonical individual state.

    Immutability is enforced, not documented.  There is no setter, no
    ``__setitem__``, and no in-place update; ``evolve`` returns a NEW state and
    leaves the original byte-identical.  This matters because a harness that
    mutates a state in place cannot honestly replay it, and every audit record
    that cited the old digest would silently become wrong.

    A state is ONE individual state, never a trajectory.  Nothing in this class
    advances it in time.
    """
    __slots__ = ("_data", "_digest")

    def __init__(self, data: Mapping):
        if not isinstance(data, Mapping):
            raise ImmutabilityViolation("a state is built from a mapping")
        frozen = {}
        for key, value in data.items():
            if not isinstance(key, str):
                raise ImmutabilityViolation(
                    f"state keys must be strings; got {type(key).__name__}")
            if isinstance(value, (list, dict, set)):
                raise ImmutabilityViolation(
                    f"state field {key!r} is mutable ({type(value).__name__}); "
                    f"use a tuple or a nested State so the state cannot be "
                    f"changed behind a digest that has already been recorded")
            frozen[key] = value
        object.__setattr__(self, "_data", frozen)
        object.__setattr__(self, "_digest", digest(frozen))

    def __getitem__(self, key: str):
        try:
            return self._data[key]
        except KeyError:
            raise KeyError(
                f"{key!r} is not a field of this state; fields are "
                f"{tuple(sorted(self._data))}") from None

    def __iter__(self):
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __setitem__(self, key, value):
        raise ImmutabilityViolation(
            "a State is immutable; use evolve() to derive a new state")

    def __setattr__(self, name, value):
        raise ImmutabilityViolation("a State is immutable")

    def __delattr__(self, name):
        raise ImmutabilityViolation("a State is immutable")

    def __hash__(self) -> int:
        return hash(self._digest)

    def __eq__(self, other) -> bool:
        return isinstance(other, State) and self._digest == other._digest

    def __repr__(self) -> str:
        return f"State({self._data!r}, digest={self._digest[:12]}...)"

    @property
    def digest(self) -> str:
        """Canonical SHA-256 of this state. Stable across processes."""
        return self._digest

    def evolve(self, **changes) -> "State":
        """Return a NEW state with ``changes`` applied. Never mutates self.

        Refuses to introduce a field that does not already exist: a typo that
        silently added a field would produce a state whose digest differs for a
        reason no record explains.
        """
        unknown = tuple(sorted(set(changes) - set(self._data)))
        if unknown:
            raise ImmutabilityViolation(
                f"evolve() cannot introduce new field(s) {unknown}; declared "
                f"fields are {tuple(sorted(self._data))}")
        return State({**self._data, **changes})


# ---------------------------------------------------------------------------
# 3. deterministic demand replay
# ---------------------------------------------------------------------------
class DemandStream:
    """A replayable, seed-addressed stream of declared demand values.

    Deterministic by construction: every value is a pure function of
    ``(seed, stream_id, index)`` via SHA-256 counter mode, so the stream is
    **random-access** and needs no state carried between draws.  Two
    consequences matter for a harness:

    * replay is exact - re-deriving index ``i`` a year later gives the same
      value, on any platform, with no saved RNG state to go stale;
    * a skipped or reordered draw cannot silently shift the stream, which is
      the classic way a "deterministic" replay stops matching its original.

    This is an INPUT stream.  Generating demand values is arithmetic over a
    seed; it advances no model state and is not a trajectory.  The distribution
    is declared by the caller (slot S-D) - there is deliberately no default.
    """
    __slots__ = ("seed", "stream_id", "low", "high")

    def __init__(self, seed: str, stream_id: str, low: float, high: float):
        if not isinstance(seed, str) or not seed.strip():
            raise DeclarationMissing("a demand stream requires a declared seed")
        if not isinstance(stream_id, str) or not stream_id.strip():
            raise DeclarationMissing(
                "a demand stream requires a stream_id, so that two streams "
                "under one seed cannot silently coincide")
        if not (isinstance(low, (int, float))
                and isinstance(high, (int, float))):
            raise DeclarationMissing("demand bounds must be numeric")
        if not high > low:
            raise DeclarationMissing(
                f"demand bounds must satisfy high > low; got {low!r}, {high!r}")
        self.seed, self.stream_id = seed, stream_id
        self.low, self.high = float(low), float(high)

    def value(self, index: int) -> float:
        """The demand at ``index``. Pure; independent of call order."""
        if not isinstance(index, int) or isinstance(index, bool) or index < 0:
            raise DeclarationMissing("demand index must be a non-negative int")
        material = canonical_bytes([self.seed, self.stream_id, index])
        word = int.from_bytes(hashlib.sha256(material).digest()[:8], "big")
        unit = word / float(1 << 64)          # in [0, 1)
        return self.low + unit * (self.high - self.low)

    def replay(self, count: int) -> tuple:
        """The first ``count`` values, as a tuple."""
        if not isinstance(count, int) or isinstance(count, bool) or count < 0:
            raise DeclarationMissing("replay count must be a non-negative int")
        return tuple(self.value(i) for i in range(count))

    def identity(self) -> Mapping:
        """The declaration that reproduces this stream exactly."""
        return {"seed": self.seed, "stream_id": self.stream_id,
                "low": self.low, "high": self.high,
                "construction": "sha256-counter-mode/v1"}


# ---------------------------------------------------------------------------
# 4. controller information boundaries
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class InformationBoundary:
    """What one controller is permitted to observe, declared in advance.

    A controller that reads a field it was never granted is the failure this
    class exists to make impossible: it is how a "local" controller quietly
    becomes global, and how an arm that was supposed to be information-matched
    stops being so.  ``project`` returns ONLY the granted fields, and
    ``require_readable`` refuses anything else by name.
    """
    controller_id: str
    readable_fields: tuple

    def __post_init__(self):
        if not isinstance(self.controller_id, str) \
                or not self.controller_id.strip():
            raise DeclarationMissing("a controller_id is required")
        if not self.readable_fields:
            raise DeclarationMissing(
                f"controller {self.controller_id!r} declares no readable "
                f"fields; an empty boundary is refused rather than treated as "
                f"'everything'")
        if len(set(self.readable_fields)) != len(self.readable_fields):
            raise DeclarationMissing("readable_fields contains duplicates")

    def require_readable(self, name: str) -> str:
        if name not in self.readable_fields:
            raise InformationLeak(
                f"controller {self.controller_id!r} may not read {name!r}; "
                f"its declared boundary is {tuple(self.readable_fields)}. "
                f"Widening a boundary is a protocol change, not a fix.")
        return name

    def project(self, state: State) -> State:
        """The controller's view: exactly the granted fields, nothing else.

        Refuses when a granted field is absent from the state, rather than
        yielding a short view - a controller silently observing fewer fields
        than its arm declares is an unrecorded change of arm.
        """
        if not isinstance(state, State):
            raise InformationLeak("project() requires a frozen State")
        absent = tuple(sorted(set(self.readable_fields) - set(state)))
        if absent:
            raise InformationLeak(
                f"controller {self.controller_id!r} is granted field(s) "
                f"{absent} that this state does not carry")
        return State({name: state[name] for name in self.readable_fields})


# ---------------------------------------------------------------------------
# 5. receipts and audit structures
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Receipt:
    """One sealed, hash-chained record of a declared harness step.

    ``previous`` binds this receipt to its predecessor, so a chain cannot be
    reordered, truncated in the middle, or have an entry replaced without
    breaking verification.  ``seal`` covers the payload AND the link, so
    altering either is detectable.

    A receipt records that something was DECLARED and CHECKED.  It is not
    evidence of a scientific outcome, and carrying one never promotes the
    content it describes (coordinate W-2, clause 5).
    """
    kind: str
    payload: Mapping
    previous: str
    seal: str = ""

    GENESIS = "0" * 64

    def __post_init__(self):
        if not isinstance(self.kind, str) or not self.kind.strip():
            raise DeclarationMissing("a receipt requires a declared kind")
        if not isinstance(self.previous, str) or len(self.previous) != 64:
            raise AuditChainBroken(
                "previous must be a 64-character digest, or Receipt.GENESIS "
                "for the first receipt in a chain")
        computed = digest({"kind": self.kind, "payload": dict(self.payload),
                           "previous": self.previous})
        if self.seal and self.seal != computed:
            raise AuditChainBroken(
                f"receipt seal mismatch: declared {self.seal}, computed "
                f"{computed}. A receipt is never re-sealed to make it agree.")
        object.__setattr__(self, "seal", computed)

    def verify(self, previous: str) -> bool:
        """True iff this receipt links to ``previous`` and its seal holds."""
        if self.previous != previous:
            return False
        return self.seal == digest(
            {"kind": self.kind, "payload": dict(self.payload),
             "previous": self.previous})


def receipt_chain(receipts: Sequence[Receipt]) -> str:
    """Verify a full chain and return its head seal.

    An empty chain returns ``Receipt.GENESIS``: the honest answer for "nothing
    has been recorded yet", rather than a refusal that would tempt a caller to
    skip verification when a chain is legitimately empty.
    """
    previous = Receipt.GENESIS
    for position, item in enumerate(receipts):
        if not isinstance(item, Receipt):
            raise AuditChainBroken(f"entry {position} is not a Receipt")
        if not item.verify(previous):
            raise AuditChainBroken(
                f"receipt chain broken at position {position} "
                f"(kind={item.kind!r}): expected previous {previous}, found "
                f"{item.previous}")
        previous = item.seal
    return previous


# ---------------------------------------------------------------------------
# 6. event logs
# ---------------------------------------------------------------------------
class EventLog:
    """An append-only, tamper-evident, in-memory event log.

    Append-only is enforced: there is no delete, no update and no index
    assignment, and ``entries`` hands back an immutable tuple so a caller
    cannot reach in and edit history.  Each append extends the receipt chain,
    so the log's ``head`` is a single digest covering everything recorded.

    In-memory by design: this module writes no file (see the module docstring).
    Persisting a log is a separate, authorized step.
    """
    __slots__ = ("_receipts",)

    def __init__(self):
        object.__setattr__(self, "_receipts", [])

    def __setattr__(self, name, value):
        raise ImmutabilityViolation("EventLog has no settable attributes")

    def __len__(self) -> int:
        return len(self._receipts)

    @property
    def head(self) -> str:
        return self._receipts[-1].seal if self._receipts else Receipt.GENESIS

    @property
    def entries(self) -> tuple:
        return tuple(self._receipts)

    def append(self, kind: str, payload: Mapping) -> Receipt:
        """Record one event and return its receipt."""
        receipt = Receipt(kind=kind, payload=dict(payload),
                          previous=self.head)
        self._receipts.append(receipt)
        return receipt

    def verify(self) -> str:
        """Verify the whole log; returns the head seal or refuses."""
        return receipt_chain(self._receipts)


# ---------------------------------------------------------------------------
# 7. negative controls
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class NegativeControl:
    """A check that MUST fail, with the reason it must fail declared.

    Negative controls are what distinguish a harness that works from one that
    merely never complains.  If a control that must fail instead passes, the
    predicate is not testing what it claims and the harness is broken - so
    ``run_negative_control`` raises on success, which is the inverted sense
    that makes the control meaningful.
    """
    control_id: str
    must_fail_because: str
    expected_refusal: type

    def __post_init__(self):
        if not isinstance(self.control_id, str) or not self.control_id.strip():
            raise DeclarationMissing("a control_id is required")
        if not isinstance(self.must_fail_because, str) \
                or not self.must_fail_because.strip():
            raise DeclarationMissing(
                f"control {self.control_id!r} must declare WHY it must fail; "
                f"an undeclared reason makes a passing control unreviewable")
        if not (isinstance(self.expected_refusal, type)
                and issubclass(self.expected_refusal, Exception)):
            raise DeclarationMissing(
                "expected_refusal must be an exception type, so that a "
                "control cannot be satisfied by an unrelated crash")


def run_negative_control(control: NegativeControl,
                         probe: Callable[[], Any]) -> Exception:
    """Run a probe that must refuse. Returns the refusal, or raises.

    ``probe`` must be a pure, non-executing callable over frozen or synthetic
    data.  Two failure modes are separated deliberately: the probe succeeding
    (the control is not testing anything) and the probe raising the WRONG
    exception (it fails, but for an unrelated reason, which would let a real
    regression hide behind a green control).
    """
    try:
        probe()
    except control.expected_refusal as refusal:
        return refusal
    except Exception as wrong:
        raise NegativeControlPassed(
            f"negative control {control.control_id!r} failed with "
            f"{type(wrong).__name__} but must fail with "
            f"{control.expected_refusal.__name__}: {wrong}") from wrong
    raise NegativeControlPassed(
        f"negative control {control.control_id!r} PASSED but must fail. "
        f"It must fail because: {control.must_fail_because}. A negative "
        f"control that passes means the check is not testing what it claims.")


# ---------------------------------------------------------------------------
# 8. reproducibility
# ---------------------------------------------------------------------------
def reproducibility_stamp(*, inputs: Mapping, code_digests: Mapping,
                          declarations: Mapping) -> Mapping:
    """The complete digest set needed to reproduce a harness step.

    Three parts, kept separate because they fail differently: ``inputs`` (the
    frozen or synthetic data), ``code_digests`` (what computed on them), and
    ``declarations`` (the profiles, boundaries and seeds in force).  A
    combined digest over all three is returned as ``stamp``.

    It deliberately captures no live environment: reading the interpreter,
    platform or clock would make the stamp differ between two runs that are in
    fact identical, and the environment belongs to an execution record, which
    this module does not produce.
    """
    for name, part in (("inputs", inputs), ("code_digests", code_digests),
                       ("declarations", declarations)):
        if not isinstance(part, Mapping) or not part:
            raise DeclarationMissing(
                f"reproducibility_stamp requires a non-empty {name} mapping; "
                f"an empty part would produce a stamp that reproduces nothing")
    body = {"inputs": dict(inputs), "code_digests": dict(code_digests),
            "declarations": dict(declarations)}
    return {**body, "stamp": digest(body),
            "construction": "sha256-canonical-json/v1"}


# ---------------------------------------------------------------------------
# 9. metrics
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class MetricSpec:
    """A declared metric: name, units, direction, and how it is computed.

    No metric is defined here.  ``compute`` is supplied by the adopted protocol
    (slot S-H); this class only guarantees that a metric cannot be recorded
    without its units and its direction of improvement declared first, which is
    what makes a later comparison interpretable.
    """
    metric_id: str
    units: str
    higher_is_better: bool
    compute: Callable[[State], Any]

    def __post_init__(self):
        if not isinstance(self.metric_id, str) or not self.metric_id.strip():
            raise DeclarationMissing("a metric_id is required")
        if not isinstance(self.units, str) or not self.units.strip():
            raise DeclarationMissing(
                f"metric {self.metric_id!r} must declare units; see slot S-U "
                f"for the potential-unit / EBU-unit question, which is open")
        if not isinstance(self.higher_is_better, bool):
            raise DeclarationMissing(
                f"metric {self.metric_id!r} must declare a direction")
        if not callable(self.compute):
            raise DeclarationMissing(
                f"metric {self.metric_id!r} must supply a compute callable")


def evaluate_metrics(specs: Sequence[MetricSpec], state: State) -> Mapping:
    """Evaluate declared metrics on ONE frozen state. Pure.

    Evaluating a metric on an individual state is arithmetic, not a
    trajectory: nothing here iterates, advances or accumulates across states.
    """
    if not isinstance(state, State):
        raise DeclarationMissing("metrics are evaluated on a frozen State")
    seen, out = set(), {}
    for spec in specs:
        if not isinstance(spec, MetricSpec):
            raise DeclarationMissing("every entry must be a MetricSpec")
        if spec.metric_id in seen:
            raise DeclarationMissing(
                f"duplicate metric_id {spec.metric_id!r}; a duplicate would "
                f"silently overwrite the first result")
        seen.add(spec.metric_id)
        out[spec.metric_id] = spec.compute(state)
    return out


# ---------------------------------------------------------------------------
# 10. classifications
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ClassificationScheme:
    """A declared, exhaustive, mutually exclusive set of outcome classes.

    Both properties are checked, not assumed.  A non-exhaustive scheme silently
    drops outcomes it did not anticipate; an overlapping scheme lets the same
    outcome be reported as two different findings.  ``classify`` therefore
    refuses when zero or more than one class matches, rather than taking the
    first match - taking the first is how an overlap stays invisible.

    The classes themselves are the author's (slot S-H); none is defined here.
    """
    scheme_id: str
    classes: tuple
    predicates: Mapping

    def __post_init__(self):
        if not isinstance(self.scheme_id, str) or not self.scheme_id.strip():
            raise DeclarationMissing("a scheme_id is required")
        if len(self.classes) < 2:
            raise DeclarationMissing(
                f"scheme {self.scheme_id!r} needs at least two classes; a "
                f"one-class scheme classifies nothing")
        if len(set(self.classes)) != len(self.classes):
            raise DeclarationMissing("duplicate outcome class")
        missing = tuple(sorted(set(self.classes) - set(self.predicates)))
        extra = tuple(sorted(set(self.predicates) - set(self.classes)))
        if missing:
            raise DeclarationMissing(
                f"scheme {self.scheme_id!r}: no predicate for class(es) "
                f"{missing}")
        if extra:
            raise DeclarationMissing(
                f"scheme {self.scheme_id!r}: predicate(s) {extra} name no "
                f"declared class")

    def classify(self, state: State) -> str:
        """The single matching class, or refuse."""
        if not isinstance(state, State):
            raise DeclarationMissing("classification requires a frozen State")
        matched = tuple(name for name in self.classes
                        if self.predicates[name](state))
        if len(matched) == 1:
            return matched[0]
        if not matched:
            raise DeclarationMissing(
                f"scheme {self.scheme_id!r} is NOT exhaustive for this state: "
                f"no class matched. An unclassifiable outcome is reported, "
                f"never silently dropped.")
        raise DeclarationMissing(
            f"scheme {self.scheme_id!r} is NOT mutually exclusive for this "
            f"state: classes {matched} all matched. The first match is not "
            f"taken, because that would hide the overlap.")


# ---------------------------------------------------------------------------
# 11. preregistration support and the standing refusal
# ---------------------------------------------------------------------------
def harness_is_executable() -> bool:
    """Always False while any escalation stands. Today: E2-E5 stand.

    The harness being correct is not the harness being permitted. Coordinate
    W-2 clause 6 keeps every world, parameter, controller definition, metric,
    threshold, preregistration, AWS request and execution packet separately
    authorized, and clause 5 records that adopting the Stage D/E/F rulebooks
    is not permission to execute.
    """
    return not ac.OPEN_ESCALATIONS
