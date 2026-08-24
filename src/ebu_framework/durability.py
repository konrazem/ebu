"""Inert Framework I-5 durability declarations and consistency checks."""

from __future__ import annotations

from dataclasses import dataclass
from enum import EnumType, StrEnum
from typing import Literal, NoReturn, Protocol, TypeAlias, runtime_checkable

from .events import PhaseCommitRecord, TraceDigest
from .ownership import EpochUpdateOwnership
from . import policy as _policy
from . import ledger as _ledger
from .policy import ObjectRef, PolicyMemoryPayloadHash
from .hashing import (
    CanonicalTracePrefixHash,
    DurabilityEvidenceDigest,
    PhaseCommitDigest,
    compute_durability_evidence_digest,
    compute_phase_commit_digest,
)
from .errors import (
    Applicability,
    FailureCode,
    FailureInterfaceRef,
    FailureStage,
    RetryClass,
    ScientificStatusEffect,
    _fail,
)


def _interface(name: str) -> FailureInterfaceRef:
    return FailureInterfaceRef("ebu_framework.durability", name, "1.0.0")


def _failure(code: FailureCode, interface: str) -> NoReturn:
    _fail(
        code,
        f"{interface} rejected {code.value}",
        stage=FailureStage.I5,
        interface_ref=_interface(interface),
        scientific_status_effect=ScientificStatusEffect.UNSTARTED_PRESERVED,
        retry_class=RetryClass.FORBIDDEN,
    )


def _formation_failure(interface: str) -> NoReturn:
    _failure(FailureCode.I5_RECORD_FORMATION_INVALID, interface)


def _strict_formation(cls: type) -> type:
    generated_init = cls.__init__

    def strict_init(self: object, *args: object, **kwargs: object) -> None:
        expected_fields = set(cls.__dataclass_fields__)  # type: ignore[attr-defined]
        if args or set(kwargs) != expected_fields:
            _formation_failure(cls.__name__)
        generated_init(self, **kwargs)

    strict_init.__wrapped__ = generated_init  # type: ignore[attr-defined]
    cls.__init__ = strict_init  # type: ignore[method-assign]
    return cls


class _I5EnumType(EnumType):
    def __call__(cls, *args: object, **kwargs: object):
        if len(args) != 1 or kwargs or type(args[0]) is not str:
            _formation_failure(cls.__name__)
        try:
            return super().__call__(*args)
        except (TypeError, ValueError):
            _formation_failure(cls.__name__)


class CommitOutcome(StrEnum, metaclass=_I5EnumType):
    REQUESTED = "REQUESTED"
    COMMITTED = "COMMITTED"
    REJECTED = "REJECTED"
    AMBIGUOUS = "AMBIGUOUS"
    UNAVAILABLE = "UNAVAILABLE"


@_strict_formation
@dataclass(frozen=True, slots=True, order=True, kw_only=True)
class PolicyMemoryTransaction:
    decision_ref: ObjectRef
    prior_memory_hash: PolicyMemoryPayloadHash | Applicability
    next_memory_hash: PolicyMemoryPayloadHash | Applicability
    trace_row_digest: TraceDigest


@_strict_formation
@dataclass(frozen=True, slots=True, order=True, kw_only=True)
class PhysicalPhaseTransaction:
    phase_commit: PhaseCommitRecord
    ownership: EpochUpdateOwnership
    ledger_evidence_ref: ObjectRef
    trace_row_digest: TraceDigest


@_strict_formation
@dataclass(frozen=True, slots=True, order=True, kw_only=True)
class AtomicStoreRequest:
    request_ref: ObjectRef
    expected_trace_prefix: TraceDigest
    expected_phase_predecessor: PhaseCommitDigest | Applicability
    policy_memory_transaction: PolicyMemoryTransaction | Applicability
    physical_phase_transaction: PhysicalPhaseTransaction | Applicability
    attempt_ordinal: int


@_strict_formation
@dataclass(frozen=True, slots=True, order=True, kw_only=True)
class DurablePrefixEvidence:
    request_ref: ObjectRef
    committed_prefix: TraceDigest
    phase_commit_digest: PhaseCommitDigest | Applicability
    evidence_digest: DurabilityEvidenceDigest


@_strict_formation
@dataclass(frozen=True, slots=True, order=True, kw_only=True)
class AtomicStoreRejection:
    request_ref: ObjectRef
    preserved_prefix: TraceDigest
    failure_code: FailureCode


@_strict_formation
@dataclass(frozen=True, slots=True, order=True, kw_only=True)
class AtomicStoreAmbiguity:
    request_ref: ObjectRef
    last_confirmed_prefix: TraceDigest | Applicability
    evidence_refs: tuple[ObjectRef, ...]


@_strict_formation
@dataclass(frozen=True, slots=True, order=True, kw_only=True)
class AtomicStoreUnavailable:
    request_ref: ObjectRef
    preserved_prefix: TraceDigest


AtomicCommitOutcome: TypeAlias = (
    DurablePrefixEvidence
    | AtomicStoreRejection
    | AtomicStoreAmbiguity
    | AtomicStoreUnavailable
)


@runtime_checkable
class AtomicStore(Protocol):
    def commit(
        self, request: AtomicStoreRequest, /
    ) -> AtomicCommitOutcome: ...


@runtime_checkable
class PolicyDecisionStore(Protocol):
    def commit_policy_decision(
        self,
        transaction: PolicyMemoryTransaction,
        expected_prefix: CanonicalTracePrefixHash,
        /,
    ) -> AtomicCommitOutcome: ...


@runtime_checkable
class PhaseCommitStore(Protocol):
    def commit_phase(
        self,
        transaction: PhysicalPhaseTransaction,
        expected_prefix: CanonicalTracePrefixHash,
        /,
    ) -> AtomicCommitOutcome: ...


def _trace_digest_is_valid(value: object) -> bool:
    return type(value).__name__ in {
        "CanonicalTraceRowHash",
        "CanonicalTracePrefixHash",
        "CanonicalScientificTracePayloadHash",
    } and type(value).__module__ == "ebu_framework.identity"


def _phase_commit_projection(record: PhaseCommitRecord) -> list[str]:
    predecessor = record.previous_phase_commit_digest
    physical = record.physical_phase_record_ref
    return [
        str(record.epoch),
        str(record.phase_ordinal.value),
        str(predecessor)
        if type(predecessor) is PhaseCommitDigest
        else Applicability.NOT_APPLICABLE.value,
        str(len(record.ordered_event_digests)),
        ",".join(str(item) for item in record.ordered_event_digests),
        str(record.epoch_ownership_digest),
        str(record.trace_row_digest)
        if physical is Applicability.NOT_APPLICABLE
        else str(record.trace_row_digest),
    ]


def _phase_commit_digest(record: PhaseCommitRecord) -> PhaseCommitDigest:
    return compute_phase_commit_digest(_phase_commit_projection(record))


def _durability_projection(
    evidence: DurablePrefixEvidence,
) -> list[str]:
    phase = evidence.phase_commit_digest
    return [
        str(evidence.request_ref.object_id),
        str(evidence.committed_prefix),
        str(phase)
        if type(phase) is PhaseCommitDigest
        else Applicability.NOT_APPLICABLE.value,
    ]


def _transaction_trace_digest(
    request: AtomicStoreRequest, /
) -> TraceDigest:
    physical = request.physical_phase_transaction
    if type(physical) is PhysicalPhaseTransaction:
        return physical.trace_row_digest
    policy = request.policy_memory_transaction
    if type(policy) is PolicyMemoryTransaction:
        return policy.trace_row_digest
    _failure(
        FailureCode.ATOMIC_COMMIT_REQUEST_INVALID,
        "_transaction_trace_digest",
    )


def _policy_formation(transaction: object) -> bool:
    return (
        type(transaction) is PolicyMemoryTransaction
        and type(transaction.decision_ref) is ObjectRef
        and (
            type(transaction.prior_memory_hash) is PolicyMemoryPayloadHash
            or transaction.prior_memory_hash is Applicability.NOT_APPLICABLE
        )
        and (
            type(transaction.next_memory_hash) is PolicyMemoryPayloadHash
            or transaction.next_memory_hash is Applicability.NOT_APPLICABLE
        )
        and _trace_digest_is_valid(transaction.trace_row_digest)
    )


def validate_policy_memory_transaction(
    transaction: PolicyMemoryTransaction, /
) -> None:
    _validate_policy_transaction(
        transaction, interface="validate_policy_memory_transaction"
    )
    return None


def _validate_policy_transaction(
    transaction: object, *, interface: str
) -> None:
    if not _policy_formation(transaction):
        _formation_failure(interface)
    if (
        transaction.prior_memory_hash is Applicability.NOT_APPLICABLE
    ) != (transaction.next_memory_hash is Applicability.NOT_APPLICABLE):
        _failure(FailureCode.POLICY_MEMORY_TRANSACTION_INVALID, interface)
    return None


def _physical_formation(transaction: object) -> bool:
    return (
        type(transaction) is PhysicalPhaseTransaction
        and type(transaction.phase_commit) is PhaseCommitRecord
        and type(transaction.ownership) is EpochUpdateOwnership
        and type(transaction.ledger_evidence_ref) is ObjectRef
        and _trace_digest_is_valid(transaction.trace_row_digest)
    )


def _validate_physical_transaction(
    transaction: PhysicalPhaseTransaction, *, interface: str
) -> None:
    if not _physical_formation(transaction):
        _formation_failure(interface)
    phase = transaction.phase_commit
    if (
        transaction.trace_row_digest != phase.trace_row_digest
        or transaction.ownership.epoch != phase.epoch
        or transaction.ownership.digest != phase.epoch_ownership_digest
    ):
        _failure(FailureCode.PHYSICAL_PHASE_TRANSACTION_INVALID, interface)


def build_atomic_commit_request(
    *,
    request_ref: ObjectRef,
    expected_trace_prefix: TraceDigest,
    expected_phase_predecessor: PhaseCommitDigest | Applicability,
    policy_memory_transaction: PolicyMemoryTransaction | Applicability,
    physical_phase_transaction: PhysicalPhaseTransaction | Applicability,
    attempt_ordinal: int,
) -> AtomicStoreRequest:
    interface = "build_atomic_commit_request"
    if not (
        type(request_ref) is ObjectRef
        and _trace_digest_is_valid(expected_trace_prefix)
        and (
            type(expected_phase_predecessor) is PhaseCommitDigest
            or expected_phase_predecessor is Applicability.NOT_APPLICABLE
        )
        and (
            type(policy_memory_transaction) is PolicyMemoryTransaction
            or policy_memory_transaction is Applicability.NOT_APPLICABLE
        )
        and (
            type(physical_phase_transaction) is PhysicalPhaseTransaction
            or physical_phase_transaction is Applicability.NOT_APPLICABLE
        )
        and type(attempt_ordinal) is int
    ):
        _formation_failure(interface)
    if (
        attempt_ordinal < 0
        or (
            policy_memory_transaction is Applicability.NOT_APPLICABLE
            and physical_phase_transaction is Applicability.NOT_APPLICABLE
        )
    ):
        _failure(FailureCode.ATOMIC_COMMIT_REQUEST_INVALID, interface)
    if type(policy_memory_transaction) is PolicyMemoryTransaction:
        _validate_policy_transaction(
            policy_memory_transaction, interface=interface
        )
    if type(physical_phase_transaction) is PhysicalPhaseTransaction:
        _validate_physical_transaction(
            physical_phase_transaction, interface=interface
        )
        if (
            physical_phase_transaction.phase_commit.previous_phase_commit_digest
            != expected_phase_predecessor
        ):
            _failure(FailureCode.ATOMIC_COMMIT_REQUEST_INVALID, interface)
    return AtomicStoreRequest(
        request_ref=request_ref,
        expected_trace_prefix=expected_trace_prefix,
        expected_phase_predecessor=expected_phase_predecessor,
        policy_memory_transaction=policy_memory_transaction,
        physical_phase_transaction=physical_phase_transaction,
        attempt_ordinal=attempt_ordinal,
    )


def classify_inert_commit_failure(
    request: AtomicStoreRequest,
    observed: Literal["REJECTED", "AMBIGUOUS", "UNAVAILABLE"],
    evidence_refs: tuple[ObjectRef, ...],
    /,
) -> AtomicStoreRejection | AtomicStoreAmbiguity | AtomicStoreUnavailable:
    interface = "classify_inert_commit_failure"
    if not (
        type(request) is AtomicStoreRequest
        and type(observed) is str
        and observed in {"REJECTED", "AMBIGUOUS", "UNAVAILABLE"}
        and type(evidence_refs) is tuple
        and all(type(item) is ObjectRef for item in evidence_refs)
    ):
        _formation_failure(interface)
    if len(evidence_refs) != len(set(evidence_refs)):
        _failure(FailureCode.DURABILITY_EVIDENCE_INCONSISTENT, interface)
    if observed == "REJECTED":
        return AtomicStoreRejection(
            request_ref=request.request_ref,
            preserved_prefix=request.expected_trace_prefix,
            failure_code=FailureCode.COMMIT_REJECTED,
        )
    if observed == "AMBIGUOUS":
        return AtomicStoreAmbiguity(
            request_ref=request.request_ref,
            last_confirmed_prefix=request.expected_trace_prefix,
            evidence_refs=evidence_refs,
        )
    return AtomicStoreUnavailable(
        request_ref=request.request_ref,
        preserved_prefix=request.expected_trace_prefix,
    )


def validate_atomic_commit_outcome(
    request: AtomicStoreRequest, outcome: AtomicCommitOutcome, /
) -> None:
    interface = "validate_atomic_commit_outcome"
    outcome_types = (
        DurablePrefixEvidence,
        AtomicStoreRejection,
        AtomicStoreAmbiguity,
        AtomicStoreUnavailable,
    )
    if type(request) is not AtomicStoreRequest or type(outcome) not in outcome_types:
        _formation_failure(interface)
    if type(outcome) is AtomicStoreAmbiguity:
        observed_prefix = outcome.last_confirmed_prefix
    else:
        observed_prefix = (
            outcome.committed_prefix
            if type(outcome) is DurablePrefixEvidence
            else outcome.preserved_prefix
        )
    if (
        observed_prefix is not Applicability.NOT_APPLICABLE
        and observed_prefix != request.expected_trace_prefix
    ):
        _failure(FailureCode.EXPECTED_TRACE_PREFIX_MISMATCH, interface)
    if type(outcome) is AtomicStoreRejection:
        _failure(FailureCode.COMMIT_REJECTED, interface)
    if type(outcome) is AtomicStoreAmbiguity:
        _failure(FailureCode.COMMIT_AMBIGUOUS, interface)
    if type(outcome) is AtomicStoreUnavailable:
        _failure(FailureCode.DURABILITY_UNAVAILABLE, interface)
    physical = request.physical_phase_transaction
    if (
        type(physical) is PhysicalPhaseTransaction
        and outcome.phase_commit_digest is Applicability.NOT_APPLICABLE
    ):
        _failure(FailureCode.DURABILITY_EVIDENCE_MISSING, interface)
    expected_digest = compute_durability_evidence_digest(
        _durability_projection(outcome)
    )
    if (
        outcome.request_ref != request.request_ref
        or outcome.evidence_digest != expected_digest
        or (
            type(physical) is PhysicalPhaseTransaction
            and outcome.phase_commit_digest
            != _phase_commit_digest(physical.phase_commit)
        )
    ):
        _failure(FailureCode.DURABILITY_EVIDENCE_INCONSISTENT, interface)
    return None


def validate_durable_prefix(
    expected: CanonicalTracePrefix,
    observed: CanonicalTracePrefix,
    outcome: CommitOutcome,
    /,
) -> None:
    interface = "validate_durable_prefix"
    if not (
        type(expected).__name__ == "CanonicalTracePrefix"
        and type(expected).__module__ == "ebu_framework.traces"
        and type(observed) is type(expected)
        and type(outcome) is CommitOutcome
    ):
        _formation_failure(interface)
    expected_bytes = b"".join(frame.frame_bytes for frame in expected.row_frames)
    observed_bytes = b"".join(frame.frame_bytes for frame in observed.row_frames)
    if outcome in {CommitOutcome.REJECTED, CommitOutcome.UNAVAILABLE}:
        if expected_bytes != observed_bytes or expected != observed:
            _failure(FailureCode.EXPECTED_TRACE_PREFIX_MISMATCH, interface)
        return None
    if outcome is CommitOutcome.AMBIGUOUS:
        return None
    if outcome is not CommitOutcome.COMMITTED:
        _failure(FailureCode.ATOMIC_COMMIT_REQUEST_INVALID, interface)
    if not observed_bytes.startswith(expected_bytes):
        _failure(FailureCode.TRACE_PREFIX_MUTATION_FORBIDDEN, interface)
    if observed_bytes == expected_bytes:
        _failure(FailureCode.TRACE_EXTENSION_IDENTITY_INVALID, interface)
    return None


__all__ = (
    "CommitOutcome",
    "PolicyMemoryTransaction",
    "PhysicalPhaseTransaction",
    "AtomicStoreRequest",
    "DurablePrefixEvidence",
    "AtomicStoreRejection",
    "AtomicStoreAmbiguity",
    "AtomicStoreUnavailable",
    "AtomicCommitOutcome",
    "AtomicStore",
    "PolicyDecisionStore",
    "PhaseCommitStore",
    "build_atomic_commit_request",
    "classify_inert_commit_failure",
    "validate_atomic_commit_outcome",
    "validate_policy_memory_transaction",
    "validate_durable_prefix",
)
