"""Inert write-once publication and correction boundaries for Framework I-8."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from typing import Literal, NoReturn, Protocol, runtime_checkable

from . import artifacts as _artifacts
from .artifacts import (
    ArtifactByteHash,
    ArtifactRecord,
    CorrectionRecord,
    ExecutionResultManifest,
    ObjectRef,
    PublicationRecord,
    ResolutionState,
)
from .provenance import (
    CanonicalTracePrefix,
    CompleteTraceEvidence,
    EnvironmentProvenance,
    ExecutionSemanticsProjection,
    RunTraceEnvelopeV1,
    RuntimeProvenance,
    SourceProvenance,
    TraceValidationResult,
    TraceValidationStatus,
    _validate_execution_provenance,
)
from .recovery import RecoveryRecord
from .authorization import (
    AuthorizationValidationRecord,
    AuthorizationValidationStatus,
    AuthorizedOperation,
)
from .authorization_use import AuthorizationUseRecord, AuthorizationUseStatus
from .ledger import Ledger
from .hashing import (
    ObjectContentHash,
    ScientificId,
    SemanticVersion,
    compute_artifact_byte_hash,
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
    return FailureInterfaceRef("ebu_framework.publication", name, "1.0.0")


def _failure(code: FailureCode, interface: str, ordinal: int) -> NoReturn:
    _fail(
        code,
        f"{interface} rejected {code.value}",
        stage=FailureStage.I8,
        interface_ref=_interface(interface),
        failure_ordinal=ordinal,
        scientific_status_effect=ScientificStatusEffect.UNSTARTED_PRESERVED,
        retry_class=RetryClass.FORBIDDEN,
    )


def _formation_failure(interface: str) -> NoReturn:
    _failure(FailureCode.I8_RECORD_FORMATION_INVALID, interface, 1)


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


@runtime_checkable
class WriteOnceStore(Protocol):
    def observe(self, content_address: str, /) -> bytes | Applicability: ...

    def put_if_absent_or_identical(
        self, content_address: str, artifact_bytes: bytes, /
    ) -> PublicationReceipt: ...


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class PublicationReceipt:
    receipt_ref: ObjectRef
    content_address: str
    artifact_byte_hash: ArtifactByteHash
    prior_state: Literal["ABSENT", "SAME_BYTES"]
    write_outcome: Literal["WRITTEN_ONCE", "ALREADY_IDENTICAL"]
    stored_byte_count: int

    def __post_init__(self) -> None:
        if not (
            type(self.receipt_ref) is ObjectRef
            and type(self.content_address) is str
            and type(self.artifact_byte_hash) is ArtifactByteHash
            and type(self.prior_state) is str
            and self.prior_state in {"ABSENT", "SAME_BYTES"}
            and type(self.write_outcome) is str
            and self.write_outcome in {"WRITTEN_ONCE", "ALREADY_IDENTICAL"}
            and type(self.stored_byte_count) is int
            and self.stored_byte_count >= 0
        ):
            _formation_failure("PublicationReceipt")
        if not (
            self.content_address == str(self.artifact_byte_hash)
            and (
                (self.prior_state, self.write_outcome)
                == ("ABSENT", "WRITTEN_ONCE")
                or (self.prior_state, self.write_outcome)
                == ("SAME_BYTES", "ALREADY_IDENTICAL")
            )
        ):
            _formation_failure("PublicationReceipt")

    def to_ecj1(self) -> dict[str, object]:
        return {
            "receipt_ref": self.receipt_ref.to_ecj1(),
            "content_address": self.content_address,
            "artifact_byte_hash": str(self.artifact_byte_hash),
            "prior_state": self.prior_state,
            "write_outcome": self.write_outcome,
            "stored_byte_count": self.stored_byte_count,
        }


_STORE_TOKEN = object()


def _receipt_ref(content_address: str, outcome: str) -> ObjectRef:
    label = outcome.lower().replace("_", "-")
    digest = hashlib.sha256(
        f"i8-publication-receipt:{outcome}:{content_address}".encode("utf-8")
    ).hexdigest()
    return ObjectRef(
        object_id=ScientificId(f"ebu:validation:i8:publication-receipt-{label}"),
        object_version=SemanticVersion("1.0.0"),
        object_content_hash=ObjectContentHash(f"sha256:{digest}"),
    )


def _fixed_inert_ref(label: str) -> ObjectRef:
    digest = hashlib.sha256(f"i8-ref:{label}".encode("utf-8")).hexdigest()
    return ObjectRef(
        object_id=ScientificId(f"ebu:validation:i8:{label}"),
        object_version=SemanticVersion("1.0.0"),
        object_content_hash=ObjectContentHash(f"sha256:{digest}"),
    )


class _InertWriteOnceStore:
    __slots__ = ("_entries",)

    def __new__(cls, token: object, entries: dict[str, bytes]):
        if cls is not _InertWriteOnceStore or token is not _STORE_TOKEN:
            _failure(FailureCode.WRITE_ONCE_STORE_INVALID, "_InertWriteOnceStore", 1)
        return super().__new__(cls)

    def __init__(self, token: object, entries: dict[str, bytes]) -> None:
        if token is not _STORE_TOKEN or type(entries) is not dict:
            _failure(FailureCode.WRITE_ONCE_STORE_INVALID, "_InertWriteOnceStore", 1)
        object.__setattr__(self, "_entries", dict(entries))

    def __setattr__(self, name: str, value: object) -> NoReturn:
        _failure(FailureCode.WRITE_ONCE_STORE_INVALID, "_InertWriteOnceStore", 1)

    def __init_subclass__(cls, **kwargs: object) -> NoReturn:
        _failure(FailureCode.WRITE_ONCE_STORE_INVALID, "_InertWriteOnceStore", 1)

    def __copy__(self) -> NoReturn:
        _failure(FailureCode.WRITE_ONCE_STORE_INVALID, "_InertWriteOnceStore", 1)

    def __deepcopy__(self, memo: object) -> NoReturn:
        _failure(FailureCode.WRITE_ONCE_STORE_INVALID, "_InertWriteOnceStore", 1)

    def __reduce__(self) -> NoReturn:
        _failure(FailureCode.WRITE_ONCE_STORE_INVALID, "_InertWriteOnceStore", 1)

    def observe(self, content_address: str, /) -> bytes | Applicability:
        if type(content_address) is not str or not content_address:
            _formation_failure("_InertWriteOnceStore.observe")
        observed = self._entries.get(content_address)
        return bytes(observed) if observed is not None else Applicability.NOT_APPLICABLE

    def put_if_absent_or_identical(
        self, content_address: str, artifact_bytes: bytes, /
    ) -> PublicationReceipt:
        if not (
            type(content_address) is str
            and bool(content_address)
            and type(artifact_bytes) is bytes
        ):
            _formation_failure("_InertWriteOnceStore.put_if_absent_or_identical")
        artifact_hash = compute_artifact_byte_hash(artifact_bytes)
        if content_address != str(artifact_hash):
            _failure(
                FailureCode.ALREADY_EXISTS_DIFFERENT,
                "publish_inert_artifacts",
                9,
            )
        observed = self._entries.get(content_address)
        if observed is not None and observed != artifact_bytes:
            _failure(
                FailureCode.ALREADY_EXISTS_DIFFERENT,
                "publish_inert_artifacts",
                9,
            )
        if observed is None:
            self._entries[content_address] = bytes(artifact_bytes)
            prior_state = "ABSENT"
            outcome = "WRITTEN_ONCE"
        else:
            prior_state = "SAME_BYTES"
            outcome = "ALREADY_IDENTICAL"
        return PublicationReceipt(
            receipt_ref=_receipt_ref(content_address, outcome),
            content_address=content_address,
            artifact_byte_hash=artifact_hash,
            prior_state=prior_state,
            write_outcome=outcome,
            stored_byte_count=len(artifact_bytes),
        )


def _make_inert_write_once_store(
    observed_entries: tuple[tuple[str, bytes], ...], /
) -> _InertWriteOnceStore:
    if not (
        type(observed_entries) is tuple
        and all(
            type(item) is tuple
            and len(item) == 2
            and type(item[0]) is str
            and bool(item[0])
            and len(item[0]) == 71
            and item[0].startswith("sha256:")
            and all(character in "0123456789abcdef" for character in item[0][7:])
            and type(item[1]) is bytes
            for item in observed_entries
        )
        and len({item[0] for item in observed_entries}) == len(observed_entries)
    ):
        _formation_failure("_make_inert_write_once_store")
    return _InertWriteOnceStore(
        _STORE_TOKEN,
        {address: bytes(payload) for address, payload in observed_entries},
    )


def _ref_key(reference: ObjectRef) -> tuple[str, str, str]:
    return (
        str(reference.object_content_hash),
        str(reference.object_id),
        str(reference.object_version),
    )


def _ordered_targets(values: tuple[ObjectRef, ...]) -> tuple[ObjectRef, ...]:
    return tuple(sorted(values, key=_ref_key))


def _envelope_ref(record: object) -> ObjectRef:
    envelope = record.envelope  # type: ignore[attr-defined]
    return ObjectRef(
        object_id=envelope.object_id,
        object_version=envelope.object_version,
        object_content_hash=envelope.object_content_hash,
    )


def _authorization_matches(
    *,
    required_operation: AuthorizedOperation,
    required_targets: tuple[ObjectRef, ...],
    configuration_ref: ObjectRef,
    binding_ref: ObjectRef,
    execution_identity: object,
    authorization_validation: AuthorizationValidationRecord,
    authorization_use: AuthorizationUseRecord,
) -> bool:
    return (
        authorization_validation.status
        is AuthorizationValidationStatus.VALIDATED_NOT_CONSUMED
        and authorization_use.status is AuthorizationUseStatus.CONSUMED
        and authorization_validation.authorization_use_key
        == authorization_use.authorization_use_key
        and authorization_validation.authorization_ref
        == authorization_use.authorization_ref
        and authorization_use.requested_operation is required_operation
        and authorization_use.target_object_refs == required_targets
        and authorization_validation.effective_target_object_refs
        == required_targets
        and authorization_validation.effective_operations
        == (required_operation.value,)
        and authorization_validation.effective_stages == ("I-8",)
        and authorization_use.accepted_configuration_ref_or_not_applicable
        == configuration_ref
        and authorization_use.accepted_execution_binding_ref_or_not_applicable
        == binding_ref
        and authorization_use.execution_identity_or_not_applicable
        == execution_identity
    )


def _validate_consumed_i8_authorization(
    *,
    required_operation: AuthorizedOperation,
    required_targets: tuple[ObjectRef, ...],
    manifest: ExecutionResultManifest,
    authorization_validation: AuthorizationValidationRecord,
    authorization_use: AuthorizationUseRecord,
) -> None:
    if not (
        type(required_operation) is AuthorizedOperation
        and type(required_targets) is tuple
        and all(type(item) is ObjectRef for item in required_targets)
        and type(manifest) is ExecutionResultManifest
        and type(authorization_validation) is AuthorizationValidationRecord
        and type(authorization_use) is AuthorizationUseRecord
    ):
        _formation_failure("_validate_consumed_i8_authorization")
    if required_operation is AuthorizedOperation.FINALIZE_EXECUTION_RESULT_MANIFEST:
        owner = "finalize_inert_manifest"
        ordinal = 7
    else:
        owner = "publish_inert_artifacts"
        ordinal = 5
    if not _authorization_matches(
        required_operation=required_operation,
        required_targets=required_targets,
        configuration_ref=manifest.configuration_ref,
        binding_ref=manifest.binding_ref,
        execution_identity=manifest.execution_identity,
        authorization_validation=authorization_validation,
        authorization_use=authorization_use,
    ):
        _failure(FailureCode.PUBLICATION_AUTHORIZATION_MISMATCH, owner, ordinal)
    return None


def _artifacts_and_bytes_form(
    artifacts: object, artifact_bytes: object
) -> bool:
    return (
        type(artifacts) is tuple
        and all(type(item) is ArtifactRecord for item in artifacts)
        and type(artifact_bytes) is tuple
        and all(type(item) is bytes for item in artifact_bytes)
        and len(artifacts) == len(artifact_bytes)
    )


def _artifact_bytes_match(
    artifacts: tuple[ArtifactRecord, ...], artifact_bytes: tuple[bytes, ...]
) -> bool:
    return all(
        compute_artifact_byte_hash(payload) == artifact.artifact_byte_hash
        for artifact, payload in zip(artifacts, artifact_bytes, strict=True)
    )


def _trace_and_run_match(
    manifest: ExecutionResultManifest,
    trace_validation: TraceValidationResult,
    run_envelope: RunTraceEnvelopeV1,
) -> bool:
    valid_prefix = (
        trace_validation.status is TraceValidationStatus.VALID_PREFIX
        and type(trace_validation.confirmed_prefix) is CanonicalTracePrefix
        and trace_validation.complete_evidence is Applicability.NOT_APPLICABLE
        and run_envelope.canonical_trace_digest is Applicability.NOT_APPLICABLE
    )
    valid_complete = (
        trace_validation.status is TraceValidationStatus.VALID_COMPLETE
        and type(trace_validation.confirmed_prefix) is CanonicalTracePrefix
        and type(trace_validation.complete_evidence) is CompleteTraceEvidence
        and run_envelope.canonical_trace_digest
        == trace_validation.complete_evidence.trace_digest
    )
    return (
        (valid_prefix or valid_complete)
        and run_envelope.execution_binding_ref == manifest.binding_ref
        and run_envelope.execution_identity == manifest.execution_identity
    )


def _manifest_embedded_artifacts(
    manifest: ExecutionResultManifest,
    artifacts: tuple[ArtifactRecord, ...],
) -> tuple[ArtifactRecord, ...]:
    by_ref = {_envelope_ref(artifact): artifact for artifact in artifacts}
    return tuple(
        by_ref[reference]
        for reference in manifest.ordered_artifact_refs
        if reference in by_ref
    )


def finalize_inert_manifest(
    expected_manifest_ref: ObjectRef,
    manifest: ExecutionResultManifest,
    artifacts: tuple[ArtifactRecord, ...],
    artifact_bytes: tuple[bytes, ...],
    source: SourceProvenance,
    runtime: RuntimeProvenance,
    environment: EnvironmentProvenance,
    semantics: ExecutionSemanticsProjection,
    trace_validation: TraceValidationResult,
    run_envelope: RunTraceEnvelopeV1,
    authorization_validation: AuthorizationValidationRecord,
    authorization_use: AuthorizationUseRecord,
    /,
) -> ExecutionResultManifest:
    interface = "finalize_inert_manifest"
    if not (
        type(expected_manifest_ref) is ObjectRef
        and type(manifest) is ExecutionResultManifest
        and _artifacts_and_bytes_form(artifacts, artifact_bytes)
        and type(source) is SourceProvenance
        and type(runtime) is RuntimeProvenance
        and type(environment) is EnvironmentProvenance
        and type(semantics) is ExecutionSemanticsProjection
        and type(trace_validation) is TraceValidationResult
        and type(run_envelope) is RunTraceEnvelopeV1
        and type(authorization_validation) is AuthorizationValidationRecord
        and type(authorization_use) is AuthorizationUseRecord
    ):
        _formation_failure(interface)
    manifest_ref = _envelope_ref(manifest)
    if expected_manifest_ref != manifest_ref:
        _failure(FailureCode.MANIFEST_MUTATION_FORBIDDEN, interface, 2)
    if not artifacts:
        _failure(FailureCode.MISSING_ARTIFACT, interface, 3)
    if not _artifact_bytes_match(artifacts, artifact_bytes):
        _failure(FailureCode.HASH_MISMATCH, interface, 4)
    if trace_validation.status is TraceValidationStatus.AMBIGUOUS:
        _failure(FailureCode.AMBIGUOUS_PREFIX, interface, 5)
    if not _trace_and_run_match(manifest, trace_validation, run_envelope):
        _failure(FailureCode.RECOVERY_RUN_BINDING_MISMATCH, interface, 6)
    targets = _ordered_targets((manifest.execution_identity.identity_ref, manifest_ref))
    _validate_consumed_i8_authorization(
        required_operation=AuthorizedOperation.FINALIZE_EXECUTION_RESULT_MANIFEST,
        required_targets=targets,
        manifest=manifest,
        authorization_validation=authorization_validation,
        authorization_use=authorization_use,
    )
    embedded = _manifest_embedded_artifacts(manifest, artifacts)
    if not _artifacts._artifact_completeness_matches(manifest, embedded):
        _failure(FailureCode.MANIFEST_COMPLETENESS_INVALID, interface, 8)
    _validate_execution_provenance(source, runtime, environment, semantics)
    _artifacts.validate_execution_result_manifest(manifest, embedded)
    return manifest


def finalize_execution_result_manifest(
    *,
    manifest: ExecutionResultManifest,
    artifacts: tuple[ArtifactRecord, ...],
    authorization_validation: AuthorizationValidationRecord,
    authorization_use: AuthorizationUseRecord,
) -> NoReturn:
    interface = "finalize_execution_result_manifest"
    if not (
        type(manifest) is ExecutionResultManifest
        and type(artifacts) is tuple
        and all(type(item) is ArtifactRecord for item in artifacts)
        and type(authorization_validation) is AuthorizationValidationRecord
        and type(authorization_use) is AuthorizationUseRecord
    ):
        _formation_failure(interface)
    _failure(FailureCode.REAL_FINALIZATION_AUTHORITY_UNAVAILABLE, interface, 2)


def _candidate_receipt_ref_is_inert(reference: ObjectRef) -> bool:
    return str(reference.object_id).startswith(
        "ebu:validation:i8:publication-receipt"
    )


def publish_inert_artifacts(
    store: _InertWriteOnceStore,
    candidate: PublicationRecord,
    manifest: ExecutionResultManifest,
    artifacts: tuple[ArtifactRecord, ...],
    artifact_bytes: tuple[bytes, ...],
    authorization_validation: AuthorizationValidationRecord,
    authorization_use: AuthorizationUseRecord,
    /,
) -> PublicationRecord:
    interface = "publish_inert_artifacts"
    if not (
        type(candidate) is PublicationRecord
        and type(manifest) is ExecutionResultManifest
        and _artifacts_and_bytes_form(artifacts, artifact_bytes)
        and type(authorization_validation) is AuthorizationValidationRecord
        and type(authorization_use) is AuthorizationUseRecord
    ):
        _formation_failure(interface)
    if len(artifacts) != 1:
        _failure(FailureCode.MISSING_ARTIFACT, interface, 2)
    if not _artifact_bytes_match(artifacts, artifact_bytes):
        _failure(FailureCode.HASH_MISMATCH, interface, 3)
    embedded = _manifest_embedded_artifacts(manifest, artifacts)
    if not (
        manifest.completeness.state is ResolutionState.PRESENT
        and not manifest.missing_artifact_kind_refs
        and _artifacts._artifact_completeness_matches(manifest, embedded)
    ):
        _failure(FailureCode.MANIFEST_COMPLETENESS_INVALID, interface, 4)
    manifest_ref = _envelope_ref(manifest)
    artifact_refs = tuple(_envelope_ref(artifact) for artifact in artifacts)
    targets = _ordered_targets((manifest_ref,) + artifact_refs)
    _validate_consumed_i8_authorization(
        required_operation=AuthorizedOperation.PUBLISH_ARTIFACTS,
        required_targets=targets,
        manifest=manifest,
        authorization_validation=authorization_validation,
        authorization_use=authorization_use,
    )
    if type(store) is not _InertWriteOnceStore:
        _failure(FailureCode.WRITE_ONCE_STORE_INVALID, interface, 6)
    addresses = tuple(str(artifact.artifact_byte_hash) for artifact in artifacts)
    hashes = tuple(artifact.artifact_byte_hash for artifact in artifacts)
    observed = store._entries.get(addresses[0])
    expected_receipt_outcome = (
        "ALREADY_IDENTICAL"
        if observed == artifact_bytes[0]
        else "WRITTEN_ONCE"
    )
    if not (
        candidate.authorization_ref == authorization_validation.authorization_ref
        and candidate.authorization_validation_ref
        == _fixed_inert_ref("authorization-validation")
        and candidate.authorization_use_ref
        == _fixed_inert_ref("authorization-use")
        and candidate.ordered_published_artifact_refs == artifact_refs
        and candidate.ordered_published_artifact_byte_hashes == hashes
        and candidate.publisher_identity_ref == _fixed_inert_ref("publisher")
        and candidate.destination_content_addresses == addresses
        and candidate.publication_time_evidence_ref
        is Applicability.NOT_APPLICABLE
        and _candidate_receipt_ref_is_inert(candidate.publication_receipt_ref)
        and candidate.publication_receipt_ref
        == _receipt_ref(addresses[0], expected_receipt_outcome)
        and candidate.completeness.state is ResolutionState.PRESENT
        and _artifacts._object_hash_matches(candidate)
    ):
        _failure(FailureCode.PUBLICATION_RECORD_INVALID, interface, 7)
    if candidate.manifest_ref != manifest_ref:
        _failure(FailureCode.MANIFEST_MUTATION_FORBIDDEN, interface, 8)
    store.put_if_absent_or_identical(addresses[0], artifact_bytes[0])
    return candidate


def publish_artifacts(
    *,
    manifest: ExecutionResultManifest,
    artifacts: tuple[ArtifactRecord, ...],
    authorization_validation: AuthorizationValidationRecord,
    authorization_use: AuthorizationUseRecord,
) -> NoReturn:
    interface = "publish_artifacts"
    if not (
        type(manifest) is ExecutionResultManifest
        and type(artifacts) is tuple
        and all(type(item) is ArtifactRecord for item in artifacts)
        and type(authorization_validation) is AuthorizationValidationRecord
        and type(authorization_use) is AuthorizationUseRecord
    ):
        _formation_failure(interface)
    _failure(FailureCode.REAL_PUBLICATION_BACKEND_UNAVAILABLE, interface, 2)


def create_inert_correction_record(
    candidate: CorrectionRecord,
    original: ArtifactRecord,
    replacement: ArtifactRecord,
    original_bytes: bytes,
    replacement_bytes: bytes,
    authorization_validation: AuthorizationValidationRecord,
    authorization_use: AuthorizationUseRecord,
    /,
) -> CorrectionRecord:
    interface = "create_inert_correction_record"
    if not (
        type(candidate) is CorrectionRecord
        and type(original) is ArtifactRecord
        and type(replacement) is ArtifactRecord
        and type(original_bytes) is bytes
        and type(replacement_bytes) is bytes
        and type(authorization_validation) is AuthorizationValidationRecord
        and type(authorization_use) is AuthorizationUseRecord
    ):
        _formation_failure(interface)
    if not (
        type(original.content_ref) is ObjectRef
        and type(original.completeness.present_value_ref) is ObjectRef
        and type(replacement.content_ref) is ObjectRef
        and type(replacement.completeness.present_value_ref) is ObjectRef
    ):
        _failure(FailureCode.MISSING_ARTIFACT, interface, 2)
    if not (
        compute_artifact_byte_hash(original_bytes) == original.artifact_byte_hash
        and compute_artifact_byte_hash(replacement_bytes)
        == replacement.artifact_byte_hash
    ):
        _failure(FailureCode.HASH_MISMATCH, interface, 3)
    original_ref = _envelope_ref(original)
    replacement_ref = _envelope_ref(replacement)
    candidate_ref = _envelope_ref(candidate)
    targets = _ordered_targets((original_ref, candidate_ref))
    identity = original.producing_execution_identity
    if not _authorization_matches(
        required_operation=AuthorizedOperation.CREATE_CORRECTION_RECORD,
        required_targets=targets,
        configuration_ref=identity.configuration_ref,
        binding_ref=identity.binding_ref,
        execution_identity=identity,
        authorization_validation=authorization_validation,
        authorization_use=authorization_use,
    ):
        _failure(FailureCode.CORRECTION_AUTHORIZATION_MISMATCH, interface, 4)
    if original_ref == replacement_ref or original_bytes == replacement_bytes:
        _failure(FailureCode.CORRECTION_AS_OVERWRITE_FORBIDDEN, interface, 5)
    if not (
        candidate.original_artifact_or_manifest_ref == original_ref
        and candidate.replacement_artifact_or_manifest_ref == replacement_ref
        and candidate.correction_scope_ref == _fixed_inert_ref("correction-scope")
        and candidate.reason_ref == _fixed_inert_ref("correction-reason")
        and candidate.method_ref == _fixed_inert_ref("correction-method")
        and candidate.authorization_ref == authorization_validation.authorization_ref
        and candidate.authorization_validation_ref
        == _fixed_inert_ref("authorization-validation")
        and candidate.authorization_use_ref
        == _fixed_inert_ref("authorization-use")
        and candidate.scientific_execution_repeated is False
        and candidate.prior_publication_refs
        == (_fixed_inert_ref("prior-publication"),)
        and candidate.new_manifest_ref_or_not_applicable
        == _fixed_inert_ref("new-manifest")
        and candidate.evidence_ledger_relation_ref
        == _fixed_inert_ref("evidence-ledger-relation")
        and candidate.completeness.state is ResolutionState.PRESENT
        and _artifacts._object_hash_matches(candidate)
    ):
        _failure(FailureCode.CORRECTION_RECORD_INVALID, interface, 6)
    return candidate


def create_correction_record(
    *,
    candidate: CorrectionRecord,
    original: ArtifactRecord,
    replacement: ArtifactRecord,
    authorization_validation: AuthorizationValidationRecord,
    authorization_use: AuthorizationUseRecord,
) -> NoReturn:
    interface = "create_correction_record"
    if not (
        type(candidate) is CorrectionRecord
        and type(original) is ArtifactRecord
        and type(replacement) is ArtifactRecord
        and type(authorization_validation) is AuthorizationValidationRecord
        and type(authorization_use) is AuthorizationUseRecord
    ):
        _formation_failure(interface)
    _failure(FailureCode.REAL_CORRECTION_AUTHORITY_UNAVAILABLE, interface, 2)


_DEPENDENCY_SENTINELS = (RecoveryRecord, Ledger)


__all__ = (
    "WriteOnceStore",
    "PublicationReceipt",
    "finalize_inert_manifest",
    "finalize_execution_result_manifest",
    "create_inert_correction_record",
    "create_correction_record",
    "publish_inert_artifacts",
    "publish_artifacts",
)
