"""Literal, inert Framework I-5 trace records and validation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import EnumType, StrEnum
import hashlib
from typing import NoReturn

from .events import (
    EventDeclaration,
    EventKey,
    ObjectRef,
    PhaseCommitRecord,
    PhaseOrdinal,
    Sha256Digest,
    TraceCompleteness,
    TraceDigest,
    _event_key_projection,
    order_event_keys,
)
from .policy import PolicyMemoryPayloadHash
from .state import ObjectContentHash, StatePayloadHash
from .experiment import ExecutionIdentity, ExecutionSemanticsHash
from . import artifacts as _artifacts
from .hashing import (
    CanonicalScientificTracePayloadHash,
    CanonicalTracePrefixHash,
    CanonicalTraceRowHash,
    OwnershipDigest,
    PhaseCommitDigest,
    RunEnvelopeDigest,
    compute_phase_commit_digest,
    compute_run_envelope_digest,
)
from .canonical import encode_ecj1, parse_ecj1
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
    return FailureInterfaceRef("ebu_framework.traces", name, "1.0.0")


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


class TraceRowKind(StrEnum, metaclass=_I5EnumType):
    EVENT_DECLARATION = "EVENT_DECLARATION"
    PROPOSAL = "PROPOSAL"
    SCREENING = "SCREENING"
    PHASE_COMMIT = "PHASE_COMMIT"
    POLICY_MEMORY = "POLICY_MEMORY"
    DURABILITY_OUTCOME = "DURABILITY_OUTCOME"


@_strict_formation
@dataclass(frozen=True, slots=True, order=True, kw_only=True)
class TraceHeader:
    trace_schema_ref: ObjectRef
    accepted_configuration_object_content_hash: ObjectContentHash | Applicability
    execution_semantics_hash: ExecutionSemanticsHash | Applicability
    initial_state_payload_hash: StatePayloadHash | Applicability
    initial_policy_memory_payload_hash: PolicyMemoryPayloadHash | Applicability


@_strict_formation
@dataclass(frozen=True, slots=True, order=True, kw_only=True)
class TraceFooter:
    terminal_or_last_confirmed_state_payload_hash: StatePayloadHash | Applicability
    terminal_or_last_confirmed_policy_memory_payload_hash: (
        PolicyMemoryPayloadHash | Applicability
    )
    confirmed_row_count: int
    trace_completeness: TraceCompleteness


@_strict_formation
@dataclass(frozen=True, slots=True, order=True, kw_only=True)
class CanonicalScientificTracePayloadV1:
    header: TraceHeader
    ordered_rows: tuple[CanonicalTraceRow, ...]
    footer: TraceFooter
    payload_hash: CanonicalScientificTracePayloadHash


@_strict_formation
@dataclass(frozen=True, slots=True, order=True, kw_only=True)
class CanonicalTraceRow:
    row_index: int
    row_kind: TraceRowKind
    event_key: EventKey | Applicability
    phase_ordinal: PhaseOrdinal
    predecessor_row_digest: TraceDigest | Applicability
    record_refs: tuple[ObjectRef, ...]
    payload_hashes: tuple[Sha256Digest, ...]


@_strict_formation
@dataclass(frozen=True, slots=True, order=True, kw_only=True)
class TraceRowFrame:
    row_digest: TraceDigest
    frame_bytes: bytes


@_strict_formation
@dataclass(frozen=True, slots=True, order=True, kw_only=True)
class CanonicalTracePrefix:
    row_frames: tuple[TraceRowFrame, ...]
    row_count: int
    prefix_digest: TraceDigest


@_strict_formation
@dataclass(frozen=True, slots=True, order=True, kw_only=True)
class TraceExtensionEvidence:
    prior_prefix_digest: TraceDigest
    extended_prefix_digest: TraceDigest
    appended_row_digests: tuple[TraceDigest, ...]


@_strict_formation
@dataclass(frozen=True, slots=True, order=True, kw_only=True)
class CompleteTraceEvidence:
    trace_digest: TraceDigest
    last_prefix_digest: TraceDigest
    confirmed_row_count: int
    completeness: TraceCompleteness
    terminal_state_hash: StatePayloadHash | Applicability
    terminal_memory_hash: PolicyMemoryPayloadHash | Applicability


@_strict_formation
@dataclass(frozen=True, slots=True, order=True, kw_only=True)
class MinimumReconstructableTrace:
    accepted_event_keys: tuple[EventKey, ...]
    phase_commit_digests: tuple[PhaseCommitDigest, ...]
    ownership_digest: OwnershipDigest
    proposal_and_screen_refs: tuple[ObjectRef, ...]
    policy_memory_transaction_refs: tuple[ObjectRef, ...]
    trace_prefix: CanonicalTracePrefix
    commit_dispositions: tuple[CommitOutcome, ...]
    completeness: TraceCompleteness


@_strict_formation
@dataclass(frozen=True, slots=True, order=True, kw_only=True)
class RunTraceEnvelopeV1:
    canonical_trace_digest: TraceDigest | Applicability
    execution_binding_ref: ObjectRef | Applicability
    execution_identity: ExecutionIdentity | Applicability
    operational_evidence_refs: tuple[ObjectRef, ...]
    completeness: TraceCompleteness
    envelope_digest: RunEnvelopeDigest


class TraceValidationStatus(StrEnum, metaclass=_I5EnumType):
    VALID_PREFIX = "VALID_PREFIX"
    VALID_COMPLETE = "VALID_COMPLETE"
    INVALID = "INVALID"
    AMBIGUOUS = "AMBIGUOUS"


@_strict_formation
@dataclass(frozen=True, slots=True, order=True, kw_only=True)
class TraceValidationResult:
    status: TraceValidationStatus
    confirmed_prefix: CanonicalTracePrefix | Applicability
    complete_evidence: CompleteTraceEvidence | Applicability


def _trace_digest_is_valid(value: object) -> bool:
    return type(value).__name__ in {
        "CanonicalTraceRowHash",
        "CanonicalTracePrefixHash",
        "CanonicalScientificTracePayloadHash",
    } and type(value).__module__ == "ebu_framework.identity"


def _commit_outcome_is_valid(value: object) -> bool:
    return (
        type(value).__name__ == "CommitOutcome"
        and type(value).__module__ == "ebu_framework.durability"
        and getattr(value, "value", None)
        in {"REQUESTED", "COMMITTED", "REJECTED", "AMBIGUOUS", "UNAVAILABLE"}
    )


def _epoch_ownership_is_valid(value: object) -> bool:
    return (
        type(value).__name__ == "EpochUpdateOwnership"
        and type(value).__module__ == "ebu_framework.ownership"
    )


def _ref_key(reference: ObjectRef) -> tuple[str, str, str]:
    return (
        str(reference.object_id),
        str(reference.object_version),
        str(reference.object_content_hash),
    )


def _trace_row_formation(row: object) -> bool:
    return (
        type(row) is CanonicalTraceRow
        and type(row.row_index) is int
        and type(row.row_kind) is TraceRowKind
        and (
            type(row.event_key) is EventKey
            or row.event_key is Applicability.NOT_APPLICABLE
        )
        and type(row.phase_ordinal) is PhaseOrdinal
        and (
            _trace_digest_is_valid(row.predecessor_row_digest)
            or row.predecessor_row_digest is Applicability.NOT_APPLICABLE
        )
        and type(row.record_refs) is tuple
        and all(type(item) is ObjectRef for item in row.record_refs)
        and type(row.payload_hashes) is tuple
        and all(isinstance(item, Sha256Digest) for item in row.payload_hashes)
    )


def _trace_row_ecj1_projection(
    row: CanonicalTraceRow, /
) -> dict[str, object]:
    event_key = row.event_key
    predecessor = row.predecessor_row_digest
    return {
        "event_key": (
            list(_event_key_projection(event_key))
            if type(event_key) is EventKey
            else Applicability.NOT_APPLICABLE.value
        ),
        "payload_hashes": [str(item) for item in row.payload_hashes],
        "phase_ordinal": row.phase_ordinal.value,
        "predecessor_row_digest": (
            str(predecessor)
            if _trace_digest_is_valid(predecessor)
            else Applicability.NOT_APPLICABLE.value
        ),
        "record_refs": [item.to_ecj1() for item in row.record_refs],
        "row_index": row.row_index,
        "row_kind": row.row_kind.value,
        "schema_tag": "ebu.trace-row.v1",
    }


def _validate_row(row: object, *, interface: str) -> CanonicalTraceRow:
    if not _trace_row_formation(row):
        _formation_failure(interface)
    if (
        row.row_index < 0
        or (
            row.row_kind
            in {
                TraceRowKind.EVENT_DECLARATION,
                TraceRowKind.PROPOSAL,
                TraceRowKind.SCREENING,
            }
            and type(row.event_key) is not EventKey
        )
        or (
            row.row_kind
            in {
                TraceRowKind.PHASE_COMMIT,
                TraceRowKind.POLICY_MEMORY,
                TraceRowKind.DURABILITY_OUTCOME,
            }
            and row.event_key is not Applicability.NOT_APPLICABLE
        )
        or tuple(_ref_key(item) for item in row.record_refs)
        != tuple(sorted(_ref_key(item) for item in row.record_refs))
        or len(row.record_refs) != len(set(row.record_refs))
        or tuple(str(item) for item in row.payload_hashes)
        != tuple(sorted(str(item) for item in row.payload_hashes))
        or len(row.payload_hashes) != len(set(row.payload_hashes))
    ):
        _failure(FailureCode.TRACE_ROW_INVALID, interface)
    if (
        row.row_index == 0
        and row.predecessor_row_digest is not Applicability.NOT_APPLICABLE
    ) or (
        row.row_index > 0
        and not _trace_digest_is_valid(row.predecessor_row_digest)
    ):
        _failure(FailureCode.TRACE_ROW_PREDECESSOR_MISMATCH, interface)
    return row


def project_canonical_trace_row(row: CanonicalTraceRow, /) -> bytes:
    checked = _validate_row(row, interface="project_canonical_trace_row")
    return bytes(encode_ecj1(_trace_row_ecj1_projection(checked)))


def frame_trace_row(row: CanonicalTraceRow, /) -> TraceRowFrame:
    row_bytes = project_canonical_trace_row(row)
    return TraceRowFrame(
        row_digest=CanonicalTraceRowHash.from_hex(
            hashlib.sha256(row_bytes).hexdigest()
        ),
        frame_bytes=len(row_bytes).to_bytes(8, "big") + row_bytes,
    )


def _decode_frame(
    frame: TraceRowFrame, *, interface: str, verify_digest: bool = True
) -> tuple[dict[str, object], bytes]:
    if type(frame) is not TraceRowFrame or not _trace_digest_is_valid(
        frame.row_digest
    ) or type(frame.frame_bytes) is not bytes:
        _formation_failure(interface)
    if not frame.frame_bytes:
        _failure(FailureCode.TRACE_PREFIX_NOT_LITERAL, interface)
    if len(frame.frame_bytes) < 8:
        _failure(FailureCode.TRACE_PREFIX_INVALID, interface)
    declared_length = int.from_bytes(frame.frame_bytes[:8], "big")
    row_bytes = frame.frame_bytes[8:]
    if declared_length != len(row_bytes):
        _failure(FailureCode.TRACE_PREFIX_INVALID, interface)
    try:
        projection = parse_ecj1(row_bytes)
    except Exception:
        _failure(FailureCode.TRACE_PREFIX_INVALID, interface)
    if type(projection) is not dict:
        _failure(FailureCode.TRACE_PREFIX_INVALID, interface)
    actual = CanonicalTraceRowHash.from_hex(hashlib.sha256(row_bytes).hexdigest())
    if verify_digest and frame.row_digest != actual:
        _failure(FailureCode.TRACE_PREFIX_INVALID, interface)
    return projection, row_bytes


def _prefix_digest(exact_bytes: bytes) -> CanonicalTracePrefixHash:
    domain = b"ebu.trace-prefix.v1"
    preimage = (
        len(domain).to_bytes(8, "big")
        + domain
        + len(exact_bytes).to_bytes(8, "big")
        + exact_bytes
    )
    return CanonicalTracePrefixHash.from_hex(hashlib.sha256(preimage).hexdigest())


def _literal_prefix_bytes(prefix: CanonicalTracePrefix, /) -> bytes:
    return b"".join(frame.frame_bytes for frame in prefix.row_frames)


def _validated_frame_sequence(
    frames: object,
    *,
    interface: str,
    start_index: int,
    predecessor: TraceDigest | Applicability,
    mutation_code: FailureCode,
    gap_first: bool,
) -> tuple[TraceRowFrame, ...]:
    if type(frames) is not tuple or not all(
        type(item) is TraceRowFrame for item in frames
    ):
        _formation_failure(interface)
    previous = predecessor
    for offset, frame in enumerate(frames):
        projection, row_bytes = _decode_frame(
            frame, interface=interface, verify_digest=False
        )
        row_index = projection.get("row_index")
        supplied_predecessor = projection.get("predecessor_row_digest")
        expected_predecessor = (
            Applicability.NOT_APPLICABLE.value
            if previous is Applicability.NOT_APPLICABLE
            else str(previous)
        )
        has_gap = type(row_index) is not int or row_index != start_index + offset
        has_predecessor_mismatch = supplied_predecessor != expected_predecessor
        if gap_first and has_gap:
            _failure(FailureCode.TRACE_ROW_GAP, interface)
        if has_predecessor_mismatch:
            _failure(mutation_code, interface)
        if has_gap:
            _failure(FailureCode.TRACE_ROW_GAP, interface)
        actual = CanonicalTraceRowHash.from_hex(
            hashlib.sha256(row_bytes).hexdigest()
        )
        if frame.row_digest != actual:
            _failure(FailureCode.TRACE_PREFIX_INVALID, interface)
        previous = frame.row_digest
    return frames


def build_trace_prefix(
    frames: tuple[TraceRowFrame, ...], /
) -> CanonicalTracePrefix:
    checked = _validated_frame_sequence(
        frames,
        interface="build_trace_prefix",
        start_index=0,
        predecessor=Applicability.NOT_APPLICABLE,
        mutation_code=FailureCode.TRACE_ROW_PREDECESSOR_MISMATCH,
        gap_first=True,
    )
    literal = b"".join(frame.frame_bytes for frame in checked)
    return CanonicalTracePrefix(
        row_frames=checked,
        row_count=len(checked),
        prefix_digest=_prefix_digest(literal),
    )


def _validate_prefix_shape(
    prefix: object, *, interface: str
) -> CanonicalTracePrefix:
    if not (
        type(prefix) is CanonicalTracePrefix
        and type(prefix.row_frames) is tuple
        and type(prefix.row_count) is int
        and _trace_digest_is_valid(prefix.prefix_digest)
    ):
        _formation_failure(interface)
    if prefix.row_count != len(prefix.row_frames):
        _failure(FailureCode.TRACE_PREFIX_INVALID, interface)
    rebuilt = build_trace_prefix(prefix.row_frames)
    if prefix.prefix_digest != rebuilt.prefix_digest:
        _failure(FailureCode.TRACE_PREFIX_INVALID, interface)
    return prefix


def extend_trace_prefix(
    prefix: CanonicalTracePrefix,
    appended: tuple[TraceRowFrame, ...],
    /,
) -> tuple[CanonicalTracePrefix, TraceExtensionEvidence]:
    interface = "extend_trace_prefix"
    checked_prefix = _validate_prefix_shape(prefix, interface=interface)
    if type(appended) is not tuple or not all(
        type(item) is TraceRowFrame for item in appended
    ):
        _formation_failure(interface)
    if not appended:
        _failure(FailureCode.TRACE_EXTENSION_IDENTITY_INVALID, interface)
    predecessor: TraceDigest | Applicability = (
        checked_prefix.row_frames[-1].row_digest
        if checked_prefix.row_frames
        else Applicability.NOT_APPLICABLE
    )
    checked_appended = _validated_frame_sequence(
        appended,
        interface=interface,
        start_index=checked_prefix.row_count,
        predecessor=predecessor,
        mutation_code=FailureCode.TRACE_PREFIX_MUTATION_FORBIDDEN,
        gap_first=False,
    )
    extended = build_trace_prefix(
        checked_prefix.row_frames + checked_appended
    )
    return (
        extended,
        TraceExtensionEvidence(
            prior_prefix_digest=checked_prefix.prefix_digest,
            extended_prefix_digest=extended.prefix_digest,
            appended_row_digests=tuple(
                frame.row_digest for frame in checked_appended
            ),
        ),
    )


def _complete_evidence_formation(evidence: object) -> bool:
    return (
        type(evidence) is CompleteTraceEvidence
        and _trace_digest_is_valid(evidence.trace_digest)
        and _trace_digest_is_valid(evidence.last_prefix_digest)
        and type(evidence.confirmed_row_count) is int
        and type(evidence.completeness) is TraceCompleteness
        and (
            type(evidence.terminal_state_hash) is StatePayloadHash
            or evidence.terminal_state_hash is Applicability.NOT_APPLICABLE
        )
        and (
            type(evidence.terminal_memory_hash) is PolicyMemoryPayloadHash
            or evidence.terminal_memory_hash is Applicability.NOT_APPLICABLE
        )
    )


def validate_complete_trace_evidence(
    prefix: CanonicalTracePrefix,
    evidence: CompleteTraceEvidence,
    /,
) -> TraceValidationResult:
    interface = "validate_complete_trace_evidence"
    if type(prefix) is not CanonicalTracePrefix or not _complete_evidence_formation(
        evidence
    ):
        _formation_failure(interface)
    if (
        evidence.confirmed_row_count < 0
        or evidence.confirmed_row_count != prefix.row_count
        or evidence.completeness
        not in {
            TraceCompleteness.COMPLETE,
            TraceCompleteness.DECLARED_FAULT_TERMINAL,
        }
    ):
        _failure(FailureCode.TRACE_COMPLETENESS_INVALID, interface)
    if (
        evidence.trace_digest != prefix.prefix_digest
        or evidence.last_prefix_digest != prefix.prefix_digest
    ):
        _failure(FailureCode.TRACE_EQUIVOCAL, interface)
    if not prefix.row_frames or any(
        not frame.frame_bytes for frame in prefix.row_frames
    ):
        _failure(FailureCode.TRACE_EVIDENCE_MISSING, interface)
    projections = [
        _decode_frame(frame, interface=interface)[0]
        for frame in prefix.row_frames
    ]
    if any(
        projection.get("row_kind") == TraceRowKind.PHASE_COMMIT.value
        and not (
            projection.get("record_refs")
            or projection.get("payload_hashes")
        )
        for projection in projections
    ):
        _failure(FailureCode.MINIMUM_TRACE_INCOMPLETE, interface)
    if (
        evidence.completeness is TraceCompleteness.COMPLETE
        and evidence.terminal_state_hash is Applicability.NOT_APPLICABLE
    ):
        _failure(FailureCode.TRACE_EVIDENCE_MISSING, interface)
    return TraceValidationResult(
        status=TraceValidationStatus.VALID_COMPLETE,
        confirmed_prefix=prefix,
        complete_evidence=evidence,
    )


def _phase_projection(record: PhaseCommitRecord) -> list[str]:
    predecessor = record.previous_phase_commit_digest
    return [
        str(record.epoch),
        str(record.phase_ordinal.value),
        str(predecessor)
        if type(predecessor) is PhaseCommitDigest
        else Applicability.NOT_APPLICABLE.value,
        str(len(record.ordered_event_digests)),
        ",".join(str(item) for item in record.ordered_event_digests),
        str(record.epoch_ownership_digest),
        str(record.trace_row_digest),
    ]


def build_minimum_reconstructable_trace(
    *,
    events: tuple[EventDeclaration, ...],
    phases: tuple[PhaseCommitRecord, ...],
    ownership: EpochUpdateOwnership,
    proposal_and_screen_refs: tuple[ObjectRef, ...],
    policy_memory_transaction_refs: tuple[ObjectRef, ...],
    prefix: CanonicalTracePrefix,
    commit_dispositions: tuple[CommitOutcome, ...],
    completeness: TraceCompleteness,
) -> MinimumReconstructableTrace:
    interface = "build_minimum_reconstructable_trace"
    if not (
        type(events) is tuple
        and all(type(item) is EventDeclaration for item in events)
        and type(phases) is tuple
        and all(type(item) is PhaseCommitRecord for item in phases)
        and _epoch_ownership_is_valid(ownership)
        and type(proposal_and_screen_refs) is tuple
        and all(type(item) is ObjectRef for item in proposal_and_screen_refs)
        and type(policy_memory_transaction_refs) is tuple
        and all(type(item) is ObjectRef for item in policy_memory_transaction_refs)
        and type(prefix) is CanonicalTracePrefix
        and type(commit_dispositions) is tuple
        and all(_commit_outcome_is_valid(item) for item in commit_dispositions)
        and type(completeness) is TraceCompleteness
    ):
        _formation_failure(interface)
    order_event_keys(events)
    _validate_prefix_shape(prefix, interface=interface)
    expected_ownership_digest = (
        phases[0].epoch_ownership_digest if phases else ownership.digest
    )
    if ownership.digest != expected_ownership_digest:
        _failure(FailureCode.MINIMUM_TRACE_INCOMPLETE, interface)
    if len(commit_dispositions) != len(phases):
        _failure(FailureCode.MINIMUM_TRACE_INCOMPLETE, interface)
    if (
        proposal_and_screen_refs
        != tuple(sorted(proposal_and_screen_refs, key=_ref_key))
        or len(proposal_and_screen_refs) != len(set(proposal_and_screen_refs))
        or policy_memory_transaction_refs
        != tuple(sorted(policy_memory_transaction_refs, key=_ref_key))
        or len(policy_memory_transaction_refs)
        != len(set(policy_memory_transaction_refs))
    ):
        _failure(FailureCode.MINIMUM_TRACE_INCOMPLETE, interface)
    phase_digests = tuple(
        compute_phase_commit_digest(_phase_projection(item)) for item in phases
    )
    return MinimumReconstructableTrace(
        accepted_event_keys=tuple(item.key for item in events),
        phase_commit_digests=phase_digests,
        ownership_digest=ownership.digest,
        proposal_and_screen_refs=proposal_and_screen_refs,
        policy_memory_transaction_refs=policy_memory_transaction_refs,
        trace_prefix=prefix,
        commit_dispositions=commit_dispositions,
        completeness=completeness,
    )


def _execution_identity_projection(value: ExecutionIdentity) -> str:
    return str(value.identity_ref.object_id)


def build_run_trace_envelope(
    *,
    canonical_trace_digest: TraceDigest | Applicability,
    execution_binding_ref: ObjectRef | Applicability,
    execution_identity: ExecutionIdentity | Applicability,
    operational_evidence_refs: tuple[ObjectRef, ...],
    completeness: TraceCompleteness,
) -> RunTraceEnvelopeV1:
    interface = "build_run_trace_envelope"
    if not (
        _trace_digest_is_valid(canonical_trace_digest)
        or canonical_trace_digest is Applicability.NOT_APPLICABLE
    ) or not (
        type(execution_binding_ref) is ObjectRef
        or execution_binding_ref is Applicability.NOT_APPLICABLE
    ) or not (
        type(execution_identity) is ExecutionIdentity
        or execution_identity is Applicability.NOT_APPLICABLE
    ) or not (
        type(operational_evidence_refs) is tuple
        and all(type(item) is ObjectRef for item in operational_evidence_refs)
        and type(completeness) is TraceCompleteness
    ):
        _formation_failure(interface)
    binding_present = type(execution_binding_ref) is ObjectRef
    identity_present = type(execution_identity) is ExecutionIdentity
    if (
        canonical_trace_digest is Applicability.NOT_APPLICABLE
        and completeness
        not in {
            TraceCompleteness.NO_DURABLE_TRACE,
            TraceCompleteness.UNRESOLVED_DURABILITY,
        }
    ):
        _failure(FailureCode.TRACE_EVIDENCE_MISSING, interface)
    if binding_present != identity_present:
        _failure(FailureCode.RUN_TRACE_ENVELOPE_INVALID, interface)
    if operational_evidence_refs != tuple(
        sorted(operational_evidence_refs, key=_ref_key)
    ) or len(operational_evidence_refs) != len(set(operational_evidence_refs)):
        _failure(FailureCode.RUN_TRACE_ENVELOPE_INVALID, interface)
    projection = [
        str(canonical_trace_digest)
        if _trace_digest_is_valid(canonical_trace_digest)
        else Applicability.NOT_APPLICABLE.value,
        str(execution_binding_ref.object_id)
        if binding_present
        else Applicability.NOT_APPLICABLE.value,
        _execution_identity_projection(execution_identity)
        if identity_present
        else Applicability.NOT_APPLICABLE.value,
        str(len(operational_evidence_refs)),
        completeness.value,
    ]
    return RunTraceEnvelopeV1(
        canonical_trace_digest=canonical_trace_digest,
        execution_binding_ref=execution_binding_ref,
        execution_identity=execution_identity,
        operational_evidence_refs=operational_evidence_refs,
        completeness=completeness,
        envelope_digest=compute_run_envelope_digest(projection),
    )


__all__ = (
    "TraceRowKind",
    "TraceHeader",
    "TraceFooter",
    "CanonicalScientificTracePayloadV1",
    "CanonicalTraceRow",
    "TraceRowFrame",
    "CanonicalTracePrefix",
    "TraceExtensionEvidence",
    "CompleteTraceEvidence",
    "MinimumReconstructableTrace",
    "RunTraceEnvelopeV1",
    "TraceValidationStatus",
    "TraceValidationResult",
    "project_canonical_trace_row",
    "frame_trace_row",
    "build_trace_prefix",
    "extend_trace_prefix",
    "validate_complete_trace_evidence",
    "build_minimum_reconstructable_trace",
    "build_run_trace_envelope",
)
