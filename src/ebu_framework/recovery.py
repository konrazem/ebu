"""Inert, same-bytes-only recovery declarations for Framework I-8."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import hashlib
from typing import NoReturn

from .artifacts import (
    ArtifactByteHash,
    ArtifactRecord,
    ExecutionIdentity,
    ExecutionResultManifest,
    ObjectRef,
    ResolutionDetail,
)
from .traces import (
    CanonicalTracePrefix,
    CanonicalTracePrefixHash,
    CompleteTraceEvidence,
    RunEnvelopeDigest,
    RunTraceEnvelopeV1,
    TraceValidationResult,
    TraceValidationStatus,
)
from .durability import AtomicStore
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
    return FailureInterfaceRef("ebu_framework.recovery", name, "1.0.0")


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


class RecoveryClassification(StrEnum):
    NO_DURABLE_EXECUTION_RECEIPT = "NO_DURABLE_EXECUTION_RECEIPT"
    RECOVERED_IDENTICAL = "RECOVERED_IDENTICAL"
    PARTIAL_DURABLE_PREFIX = "PARTIAL_DURABLE_PREFIX"
    NO_DURABLE_TRACE = "NO_DURABLE_TRACE"
    UNRESOLVED_DURABILITY = "UNRESOLVED_DURABILITY"
    PUBLICATION_INCOMPLETE = "PUBLICATION_INCOMPLETE"

    @classmethod
    def _missing_(cls, value: object) -> NoReturn:
        _formation_failure(cls.__name__)


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class RecoveryRecord:
    classification: RecoveryClassification
    manifest_ref: ObjectRef
    artifact_ref: ObjectRef
    artifact_byte_hash: ArtifactByteHash
    trace_prefix_hash: CanonicalTracePrefixHash
    run_envelope_digest: RunEnvelopeDigest
    execution_identity: ExecutionIdentity
    authorization_validation_ref: ObjectRef
    authorization_use_ref: ObjectRef
    destination_content_address: str
    destination_prior_hash_or_not_applicable: ArtifactByteHash | Applicability
    recovered_artifact_ref: ObjectRef
    completeness: ResolutionDetail

    def __post_init__(self) -> None:
        if not (
            type(self.classification) is RecoveryClassification
            and type(self.manifest_ref) is ObjectRef
            and type(self.artifact_ref) is ObjectRef
            and type(self.artifact_byte_hash) is ArtifactByteHash
            and type(self.trace_prefix_hash) is CanonicalTracePrefixHash
            and type(self.run_envelope_digest) is RunEnvelopeDigest
            and type(self.execution_identity) is ExecutionIdentity
            and type(self.authorization_validation_ref) is ObjectRef
            and type(self.authorization_use_ref) is ObjectRef
            and type(self.destination_content_address) is str
            and bool(self.destination_content_address)
            and (
                type(self.destination_prior_hash_or_not_applicable)
                is ArtifactByteHash
                or self.destination_prior_hash_or_not_applicable
                is Applicability.NOT_APPLICABLE
            )
            and type(self.recovered_artifact_ref) is ObjectRef
            and type(self.completeness) is ResolutionDetail
        ):
            _formation_failure("RecoveryRecord")
        if self.destination_content_address != str(self.artifact_byte_hash):
            _formation_failure("RecoveryRecord")
        if (
            self.classification is RecoveryClassification.RECOVERED_IDENTICAL
            and self.recovered_artifact_ref != self.artifact_ref
        ):
            _formation_failure("RecoveryRecord")

    def to_ecj1(self) -> dict[str, object]:
        projected: dict[str, object] = {}
        for field in self.__dataclass_fields__:
            value = getattr(self, field)
            if isinstance(value, StrEnum):
                projected[field] = value.value
            elif type(value) is Applicability:
                projected[field] = value.value
            elif type(value) in {
                ArtifactByteHash,
                CanonicalTracePrefixHash,
                RunEnvelopeDigest,
            }:
                projected[field] = str(value)
            elif hasattr(value, "to_ecj1"):
                projected[field] = value.to_ecj1()
            else:
                projected[field] = value
        return projected


def _ref_key(reference: ObjectRef) -> tuple[str, str, str]:
    return (
        str(reference.object_content_hash),
        str(reference.object_id),
        str(reference.object_version),
    )


def _envelope_ref(record: object) -> ObjectRef:
    envelope = record.envelope  # type: ignore[attr-defined]
    return ObjectRef(
        object_id=envelope.object_id,
        object_version=envelope.object_version,
        object_content_hash=envelope.object_content_hash,
    )


def _ordered_targets(values: tuple[ObjectRef, ...]) -> tuple[ObjectRef, ...]:
    return tuple(sorted(values, key=_ref_key))


def _fixed_inert_ref(label: str) -> ObjectRef:
    digest = hashlib.sha256(f"i8-ref:{label}".encode("utf-8")).hexdigest()
    return ObjectRef(
        object_id=ScientificId(f"ebu:validation:i8:{label}"),
        object_version=SemanticVersion("1.0.0"),
        object_content_hash=ObjectContentHash(f"sha256:{digest}"),
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
    if not (
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
        == manifest.configuration_ref
        and authorization_use.accepted_execution_binding_ref_or_not_applicable
        == manifest.binding_ref
        and authorization_use.execution_identity_or_not_applicable
        == manifest.execution_identity
    ):
        _failure(
            FailureCode.RECOVERY_AUTHORIZATION_MISMATCH,
            "recover_inert_artifacts",
            6,
        )
    return None


def recover_inert_artifacts(
    manifest: ExecutionResultManifest,
    artifact: ArtifactRecord,
    artifact_bytes: bytes,
    destination_bytes_or_not_applicable: bytes | Applicability,
    trace_validation: TraceValidationResult,
    run_envelope: RunTraceEnvelopeV1,
    authorization_validation: AuthorizationValidationRecord,
    authorization_use: AuthorizationUseRecord,
    /,
) -> RecoveryRecord:
    interface = "recover_inert_artifacts"
    if not (
        type(manifest) is ExecutionResultManifest
        and type(artifact) is ArtifactRecord
        and type(artifact_bytes) is bytes
        and (
            type(destination_bytes_or_not_applicable) is bytes
            or destination_bytes_or_not_applicable
            is Applicability.NOT_APPLICABLE
        )
        and type(trace_validation) is TraceValidationResult
        and type(run_envelope) is RunTraceEnvelopeV1
        and type(authorization_validation) is AuthorizationValidationRecord
        and type(authorization_use) is AuthorizationUseRecord
    ):
        _formation_failure(interface)

    artifact_ref = _envelope_ref(artifact)
    manifest_ref = _envelope_ref(manifest)
    if artifact_ref not in manifest.ordered_artifact_refs:
        _failure(FailureCode.MISSING_ARTIFACT, interface, 2)
    if compute_artifact_byte_hash(artifact_bytes) != artifact.artifact_byte_hash:
        _failure(FailureCode.HASH_MISMATCH, interface, 3)
    if trace_validation.status is TraceValidationStatus.AMBIGUOUS:
        _failure(FailureCode.AMBIGUOUS_PREFIX, interface, 4)
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
    if not (
        (valid_prefix or valid_complete)
        and run_envelope.execution_binding_ref == manifest.binding_ref
        and run_envelope.execution_identity == manifest.execution_identity
        and artifact.producing_execution_identity == manifest.execution_identity
    ):
        _failure(FailureCode.RECOVERY_RUN_BINDING_MISMATCH, interface, 5)

    required_targets = _ordered_targets((manifest_ref, artifact_ref))
    _validate_consumed_i8_authorization(
        required_operation=AuthorizedOperation.RECOVER_EXECUTION_ARTIFACTS,
        required_targets=required_targets,
        manifest=manifest,
        authorization_validation=authorization_validation,
        authorization_use=authorization_use,
    )
    if (
        type(destination_bytes_or_not_applicable) is bytes
        and destination_bytes_or_not_applicable != artifact_bytes
    ):
        _failure(FailureCode.ALREADY_EXISTS_DIFFERENT, interface, 7)

    classification = (
        RecoveryClassification.PARTIAL_DURABLE_PREFIX
        if trace_validation.status is TraceValidationStatus.VALID_PREFIX
        else RecoveryClassification.RECOVERED_IDENTICAL
    )
    prior_hash: ArtifactByteHash | Applicability = (
        artifact.artifact_byte_hash
        if type(destination_bytes_or_not_applicable) is bytes
        else Applicability.NOT_APPLICABLE
    )
    prefix = trace_validation.confirmed_prefix
    return RecoveryRecord(
        classification=classification,
        manifest_ref=manifest_ref,
        artifact_ref=artifact_ref,
        artifact_byte_hash=artifact.artifact_byte_hash,
        trace_prefix_hash=prefix.prefix_digest,  # type: ignore[union-attr]
        run_envelope_digest=run_envelope.envelope_digest,
        execution_identity=manifest.execution_identity,
        authorization_validation_ref=_fixed_inert_ref("authorization-validation"),
        authorization_use_ref=_fixed_inert_ref("authorization-use"),
        destination_content_address=str(artifact.artifact_byte_hash),
        destination_prior_hash_or_not_applicable=prior_hash,
        recovered_artifact_ref=artifact_ref,
        completeness=manifest.completeness,
    )


def recover_artifacts(
    *,
    manifest: ExecutionResultManifest,
    artifacts: tuple[ArtifactRecord, ...],
    authorization_validation: AuthorizationValidationRecord,
    authorization_use: AuthorizationUseRecord,
) -> NoReturn:
    interface = "recover_artifacts"
    if not (
        type(manifest) is ExecutionResultManifest
        and type(artifacts) is tuple
        and all(type(item) is ArtifactRecord for item in artifacts)
        and type(authorization_validation) is AuthorizationValidationRecord
        and type(authorization_use) is AuthorizationUseRecord
    ):
        _formation_failure(interface)
    _failure(FailureCode.REAL_RECOVERY_BACKEND_UNAVAILABLE, interface, 2)


_DEPENDENCY_SENTINELS = (AtomicStore, Ledger)


__all__ = (
    "RecoveryClassification",
    "RecoveryRecord",
    "recover_inert_artifacts",
    "recover_artifacts",
)
