"""Immutable I-3 artifact and result-manifest declarations."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import NoReturn

from .experiment import ExecutionIdentity
from .ledger import Ledger
from .primitives import ResolutionDetail, ResolutionState
from .identity import ArtifactByteHash, ObjectRef
from .envelopes import CommonObjectEnvelope, parse_ecj1
from .hashing import compute_object_content_hash
from .errors import (
    Applicability,
    FailureCode,
    FailureInterfaceRef,
    FailureObjectRef,
    FailureStage,
    RetryClass,
    ScientificStatusEffect,
    _fail,
)


def _interface(name: str) -> FailureInterfaceRef:
    return FailureInterfaceRef("ebu_framework.artifacts", name, "1.0.0")


def _failure(
    code: FailureCode,
    interface: str,
    *,
    summary: str | None = None,
    object_ref: FailureObjectRef | None = None,
) -> NoReturn:
    _fail(
        code,
        summary or f"{interface} rejected {code.value}",
        stage=FailureStage.I3,
        interface_ref=_interface(interface),
        object_refs=() if object_ref is None else (object_ref,),
        scientific_status_effect=ScientificStatusEffect.UNSTARTED_PRESERVED,
        retry_class=RetryClass.FORBIDDEN,
    )


def _formation_failure(interface: str) -> NoReturn:
    _failure(FailureCode.I3_RECORD_FORMATION_INVALID, interface)


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


def _object_ref_tuple(value: object) -> bool:
    return type(value) is tuple and all(type(item) is ObjectRef for item in value)


def _object_or_applicability(value: object) -> bool:
    return type(value) is ObjectRef or type(value) is Applicability


def _project(value: object) -> object:
    if type(value) is ArtifactByteHash:
        return str(value)
    if type(value) is Applicability:
        return value.value
    if isinstance(value, StrEnum):
        return value.value
    if type(value) is ObjectRef:
        return value.to_ecj1()
    if type(value) is tuple:
        return [_project(item) for item in value]
    if hasattr(value, "to_ecj1"):
        return value.to_ecj1()  # type: ignore[union-attr]
    return value


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class ArtifactRecord:
    envelope: CommonObjectEnvelope
    artifact_kind_ref: ObjectRef
    artifact_byte_hash: ArtifactByteHash
    media_type: str
    schema_ref: ObjectRef | Applicability
    producing_execution_identity: ExecutionIdentity
    content_ref: ObjectRef | Applicability
    completeness: ResolutionDetail

    def __post_init__(self) -> None:
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and type(self.artifact_kind_ref) is ObjectRef
            and type(self.artifact_byte_hash) is ArtifactByteHash
            and type(self.media_type) is str
            and _object_or_applicability(self.schema_ref)
            and type(self.producing_execution_identity) is ExecutionIdentity
            and _object_or_applicability(self.content_ref)
            and type(self.completeness) is ResolutionDetail
        ):
            _formation_failure("ArtifactRecord")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class ExecutionResultManifest:
    envelope: CommonObjectEnvelope
    configuration_ref: ObjectRef
    binding_ref: ObjectRef
    execution_identity: ExecutionIdentity
    ordered_artifact_refs: tuple[ObjectRef, ...]
    trace_completeness_ref: ObjectRef
    terminal_state_ref: ObjectRef | Applicability
    last_confirmed_state_ref: ObjectRef | Applicability
    policy_memory_ref: ObjectRef | Applicability
    required_artifact_kind_refs: tuple[ObjectRef, ...]
    missing_artifact_kind_refs: tuple[ObjectRef, ...]
    completeness: ResolutionDetail

    def __post_init__(self) -> None:
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and type(self.configuration_ref) is ObjectRef
            and type(self.binding_ref) is ObjectRef
            and type(self.execution_identity) is ExecutionIdentity
            and _object_ref_tuple(self.ordered_artifact_refs)
            and type(self.trace_completeness_ref) is ObjectRef
            and _object_or_applicability(self.terminal_state_ref)
            and _object_or_applicability(self.last_confirmed_state_ref)
            and _object_or_applicability(self.policy_memory_ref)
            and _object_ref_tuple(self.required_artifact_kind_refs)
            and _object_ref_tuple(self.missing_artifact_kind_refs)
            and type(self.completeness) is ResolutionDetail
        ):
            _formation_failure("ExecutionResultManifest")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


def _artifact_tuple(value: object) -> bool:
    return type(value) is tuple and all(type(item) is ArtifactRecord for item in value)


def _failure_object(record: object) -> FailureObjectRef:
    envelope = record.envelope  # type: ignore[attr-defined]
    return FailureObjectRef(
        object_id=str(envelope.object_id),
        object_version=str(envelope.object_version),
        object_content_hash=str(envelope.object_content_hash),
    )


def _object_content_check(record: object, interface: str, position: str) -> None:
    if parse_ecj1(record.envelope.object_content_payload) != record.to_ecj1():  # type: ignore[attr-defined]
        _failure(
            FailureCode.I3_OBJECT_CONTENT_MISMATCH,
            interface,
            summary=(
                f"{interface} rejected I3_OBJECT_CONTENT_MISMATCH at {position}"
            ),
            object_ref=_failure_object(record),
        )


def _ref_key(reference: ObjectRef) -> tuple[str, str, str]:
    return (
        str(reference.object_id),
        str(reference.object_version),
        str(reference.object_content_hash),
    )


def _ordered_refs(values: tuple[ObjectRef, ...]) -> bool:
    keys = tuple(_ref_key(item) for item in values)
    return keys == tuple(sorted(keys))


def _duplicate_refs(values: tuple[ObjectRef, ...]) -> bool:
    keys = tuple(_ref_key(item) for item in values)
    return len(keys) != len(set(keys))


def _duplicate_records(values: tuple[ArtifactRecord, ...]) -> bool:
    return any(
        left == right
        for index, left in enumerate(values)
        for right in values[index + 1 :]
    )


def _envelope_ref(record: object) -> ObjectRef:
    envelope = record.envelope  # type: ignore[attr-defined]
    return ObjectRef(
        object_id=envelope.object_id,
        object_version=envelope.object_version,
        object_content_hash=envelope.object_content_hash,
    )


def _object_hash_matches(record: object) -> bool:
    envelope = record.envelope  # type: ignore[attr-defined]
    supersedes = (
        envelope.supersedes_ref
        if type(envelope.supersedes_ref) is ObjectRef
        else None
    )
    recomputed = compute_object_content_hash(
        object_id=envelope.object_id,
        object_kind=str(envelope.object_kind_id),
        schema_id=envelope.schema_id,
        schema_version=envelope.schema_version,
        object_version=envelope.object_version,
        authority_refs=envelope.authority_refs,
        supersedes_ref=supersedes,
        object_content_payload=parse_ecj1(envelope.object_content_payload),
    )
    return recomputed == envelope.object_content_hash


def _artifact_completeness_matches(
    manifest: ExecutionResultManifest,
    artifacts: tuple[ArtifactRecord, ...],
) -> bool:
    artifact_refs = tuple(_envelope_ref(artifact) for artifact in artifacts)
    if manifest.ordered_artifact_refs != artifact_refs:
        return False

    artifact_kinds = {artifact.artifact_kind_ref for artifact in artifacts}
    required_kinds = set(manifest.required_artifact_kind_refs)
    missing_kinds = set(manifest.missing_artifact_kind_refs)
    if missing_kinds != required_kinds - artifact_kinds:
        return False

    state = manifest.completeness.state
    if state is ResolutionState.PRESENT:
        return (
            type(manifest.terminal_state_ref) is ObjectRef
            and manifest.terminal_state_ref == manifest.last_confirmed_state_ref
        )
    if state in {
        ResolutionState.PARTIAL,
        ResolutionState.FAILED,
        ResolutionState.UNRESOLVED,
    }:
        return (
            manifest.terminal_state_ref is Applicability.NOT_APPLICABLE
            and type(manifest.last_confirmed_state_ref) is ObjectRef
        )
    return (
        manifest.terminal_state_ref is Applicability.NOT_APPLICABLE
        and manifest.last_confirmed_state_ref is Applicability.NOT_APPLICABLE
    )


def validate_execution_result_manifest(
    manifest: ExecutionResultManifest,
    artifacts: tuple[ArtifactRecord, ...],
    /,
) -> None:
    if type(manifest) is not ExecutionResultManifest:
        _formation_failure("ExecutionResultManifest")
    if not _artifact_tuple(artifacts):
        _formation_failure("ArtifactRecord")
    interface = "validate_execution_result_manifest"
    _object_content_check(manifest, interface, "argument 1 (manifest)")
    for index, artifact in enumerate(artifacts):
        _object_content_check(
            artifact,
            interface,
            f"argument 2 (artifacts), member {index}",
        )

    applicability_values = (
        manifest.terminal_state_ref,
        manifest.last_confirmed_state_ref,
        manifest.policy_memory_ref,
    ) + tuple(
        value
        for artifact in artifacts
        for value in (artifact.schema_ref, artifact.content_ref)
    )
    if any(value is Applicability.APPLICABLE for value in applicability_values):
        _failure(FailureCode.IMPLICIT_ABSENCE_FORBIDDEN, interface)

    artifact_refs = tuple(_envelope_ref(artifact) for artifact in artifacts)
    same_members = set(manifest.ordered_artifact_refs) == set(artifact_refs)
    if (
        (same_members and manifest.ordered_artifact_refs != artifact_refs)
        or not _ordered_refs(manifest.required_artifact_kind_refs)
        or not _ordered_refs(manifest.missing_artifact_kind_refs)
    ):
        _failure(FailureCode.I3_COLLECTION_ORDER_INVALID, interface)
    if (
        _duplicate_refs(manifest.ordered_artifact_refs)
        or _duplicate_refs(manifest.required_artifact_kind_refs)
        or _duplicate_refs(manifest.missing_artifact_kind_refs)
        or _duplicate_records(artifacts)
    ):
        _failure(FailureCode.I3_DUPLICATE_MEMBER, interface)
    if not _artifact_completeness_matches(manifest, artifacts):
        _failure(FailureCode.ARTIFACT_COMPLETENESS_INVALID, interface)
    if not _object_hash_matches(manifest) or any(
        not _object_hash_matches(artifact) for artifact in artifacts
    ):
        _failure(FailureCode.HASH_MISMATCH, interface)
    return None


_DEPENDENCY_SENTINEL = Ledger


__all__ = (
    "ArtifactRecord",
    "ExecutionResultManifest",
    "validate_execution_result_manifest",
)
