"""Closed, supplied-value provenance declarations for Framework I-8."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Literal, NoReturn

from .experiment import ExecutionBinding
from .artifacts import ArtifactRecord, ResolutionDetail
from .traces import (
    CanonicalTracePrefix,
    CompleteTraceEvidence,
    RunTraceEnvelopeV1,
    TraceValidationResult,
    TraceValidationStatus,
)
from .identity import (
    ArtifactByteHash,
    ExecutionSemanticsHash,
    ObjectRef,
    SourceFileRawSha256,
)
from .hashing import compute_execution_semantics_hash
from .errors import (
    Applicability,
    FailureCode,
    FailureInterfaceRef,
    FailureStage,
    RetryClass,
    ScientificStatusEffect,
    _fail,
)


_EXECUTION_SEMANTICS_CLASSES = (
    "SCIENTIFIC_BINDING",
    "FRAMEWORK_AND_DOMAIN_IMPLEMENTATION",
    "SOURCE",
    "INTERPRETER",
    "DEPENDENCY_CLOSURE",
    "OS_AND_ARCHITECTURE_CONTRACT",
    "NUMERICAL_HARDWARE_BACKEND",
    "ARITHMETIC",
    "CONCURRENCY",
    "ENVIRONMENT_ALLOWLIST",
    "ENTRY_SEMANTICS",
    "INFORMATION_AND_MEMORY",
    "FAULT_DELIVERY",
    "TRACE_AND_RESULT",
    "OPERATIONAL_EXCLUSIONS_THAT_AFFECT_SCIENCE",
    "STOCHASTIC_CONTRACT",
)
_RUN_METADATA_CLASSES = (
    "RUN_IDENTITY",
    "HUMAN_AND_HOST_IDENTITY",
    "WALL_CLOCK_OBSERVATION",
    "LOCATION_AND_STORAGE",
    "RESOURCE_OBSERVATIONS",
    "CONTEXTUAL_VCS",
    "NON_READ_ENVIRONMENT",
    "BLOCKED_HOST_TEXT_DATABASES",
    "LOGS_AND_DIAGNOSTICS",
    "TRUST_AND_PERMISSION_EVIDENCE",
    "PUBLICATION",
    "UNDECLARED_OPERATIONAL_FAILURE",
)
_LOWER_HEX40 = re.compile(r"[0-9a-f]{40}", re.ASCII)


def _interface(name: str) -> FailureInterfaceRef:
    return FailureInterfaceRef("ebu_framework.provenance", name, "1.0.0")


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


def _ref_key(reference: ObjectRef) -> tuple[str, str, str]:
    return (
        str(reference.object_id),
        str(reference.object_version),
        str(reference.object_content_hash),
    )


def _ref_tuple(value: object, *, canonical: bool = False) -> bool:
    if type(value) is not tuple or not all(type(item) is ObjectRef for item in value):
        return False
    keys = tuple(_ref_key(item) for item in value)
    return len(keys) == len(set(keys)) and (
        not canonical or keys == tuple(sorted(keys))
    )


def _object_or_not_applicable(value: object) -> bool:
    return type(value) is ObjectRef or value is Applicability.NOT_APPLICABLE


def _project(value: object) -> object:
    if type(value) in {ArtifactByteHash, ExecutionSemanticsHash, SourceFileRawSha256}:
        return str(value)
    if type(value) is Applicability:
        return value.value
    if type(value) is ObjectRef:
        return value.to_ecj1()
    if type(value) is tuple:
        return [_project(item) for item in value]
    if hasattr(value, "to_ecj1"):
        return value.to_ecj1()  # type: ignore[union-attr]
    return value


def classify_execution_runtime_property(
    property_class: str, /
) -> Literal["EXECUTION_SEMANTICS", "RUN_METADATA"]:
    if type(property_class) is not str:
        _formation_failure("classify_execution_runtime_property")
    if property_class in _EXECUTION_SEMANTICS_CLASSES:
        return "EXECUTION_SEMANTICS"
    if property_class in _RUN_METADATA_CLASSES:
        return "RUN_METADATA"
    _failure(
        FailureCode.SOURCE_RUNTIME_PROPERTY_OUTSIDE_SECTION7,
        "classify_execution_runtime_property",
        2,
    )


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class SourceProvenance:
    repository_identity_ref: ObjectRef
    source_commit: str
    ordered_source_refs: tuple[ObjectRef, ...]
    ordered_source_raw_sha256: tuple[SourceFileRawSha256, ...]
    ordered_source_artifact_byte_hashes: tuple[ArtifactByteHash, ...]
    dirty_source_state: Literal["FORBIDDEN"]
    completeness: ResolutionDetail

    def __post_init__(self) -> None:
        if not (
            type(self.repository_identity_ref) is ObjectRef
            and type(self.source_commit) is str
            and _LOWER_HEX40.fullmatch(self.source_commit) is not None
            and type(self.ordered_source_refs) is tuple
            and all(type(item) is ObjectRef for item in self.ordered_source_refs)
            and type(self.ordered_source_raw_sha256) is tuple
            and all(
                type(item) is SourceFileRawSha256
                for item in self.ordered_source_raw_sha256
            )
            and type(self.ordered_source_artifact_byte_hashes) is tuple
            and all(
                type(item) is ArtifactByteHash
                for item in self.ordered_source_artifact_byte_hashes
            )
            and type(self.dirty_source_state) is str
            and self.dirty_source_state == "FORBIDDEN"
            and type(self.completeness) is ResolutionDetail
        ):
            _formation_failure("SourceProvenance")
        lengths = {
            len(self.ordered_source_refs),
            len(self.ordered_source_raw_sha256),
            len(self.ordered_source_artifact_byte_hashes),
        }
        if lengths != {len(self.ordered_source_refs)} or not self.ordered_source_refs:
            _failure(
                FailureCode.PROVENANCE_INVENTORY_INVALID,
                "SourceProvenance",
                2,
            )
        for values in (
            self.ordered_source_refs,
            self.ordered_source_raw_sha256,
            self.ordered_source_artifact_byte_hashes,
        ):
            if len(values) != len(set(values)):
                _failure(
                    FailureCode.PROVENANCE_INVENTORY_INVALID,
                    "SourceProvenance",
                    2,
                )

    def to_ecj1(self) -> dict[str, object]:
        return {field: _project(getattr(self, field)) for field in self.__dataclass_fields__}


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class RuntimeProvenance:
    interpreter_ref: ObjectRef
    dependency_closure_refs: tuple[ObjectRef, ...]
    os_architecture_contract_ref: ObjectRef
    numerical_hardware_backend_ref_or_not_applicable: ObjectRef | Applicability
    arithmetic_contract_refs: tuple[ObjectRef, ...]
    concurrency_contract_ref: ObjectRef
    entry_semantics_ref: ObjectRef
    fault_delivery_contract_ref_or_not_applicable: ObjectRef | Applicability
    stochastic_contract_ref_or_not_applicable: ObjectRef | Applicability
    included_property_classes: tuple[str, ...]
    completeness: ResolutionDetail

    def __post_init__(self) -> None:
        if not (
            type(self.interpreter_ref) is ObjectRef
            and _ref_tuple(self.dependency_closure_refs, canonical=True)
            and type(self.os_architecture_contract_ref) is ObjectRef
            and _object_or_not_applicable(
                self.numerical_hardware_backend_ref_or_not_applicable
            )
            and _ref_tuple(self.arithmetic_contract_refs, canonical=True)
            and type(self.concurrency_contract_ref) is ObjectRef
            and type(self.entry_semantics_ref) is ObjectRef
            and _object_or_not_applicable(
                self.fault_delivery_contract_ref_or_not_applicable
            )
            and _object_or_not_applicable(
                self.stochastic_contract_ref_or_not_applicable
            )
            and type(self.included_property_classes) is tuple
            and all(type(item) is str for item in self.included_property_classes)
            and type(self.completeness) is ResolutionDetail
        ):
            _formation_failure("RuntimeProvenance")
        if self.included_property_classes != _EXECUTION_SEMANTICS_CLASSES:
            _failure(
                FailureCode.SOURCE_RUNTIME_PROPERTY_OUTSIDE_SECTION7,
                "RuntimeProvenance",
                2,
            )

    def to_ecj1(self) -> dict[str, object]:
        return {field: _project(getattr(self, field)) for field in self.__dataclass_fields__}


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class EnvironmentProvenance:
    normalized_allowlist_refs: tuple[ObjectRef, ...]
    operational_exclusion_refs: tuple[ObjectRef, ...]
    blocked_nonread_property_names: tuple[str, ...]
    run_specific_property_classes: tuple[str, ...]
    run_specific_evidence_refs: tuple[ObjectRef, ...]
    completeness: ResolutionDetail

    def __post_init__(self) -> None:
        if not (
            _ref_tuple(self.normalized_allowlist_refs, canonical=True)
            and _ref_tuple(self.operational_exclusion_refs, canonical=True)
            and type(self.blocked_nonread_property_names) is tuple
            and all(
                type(item) is str and bool(item)
                for item in self.blocked_nonread_property_names
            )
            and self.blocked_nonread_property_names
            == tuple(sorted(self.blocked_nonread_property_names))
            and len(self.blocked_nonread_property_names)
            == len(set(self.blocked_nonread_property_names))
            and type(self.run_specific_property_classes) is tuple
            and all(type(item) is str for item in self.run_specific_property_classes)
            and _ref_tuple(self.run_specific_evidence_refs)
            and type(self.completeness) is ResolutionDetail
        ):
            _formation_failure("EnvironmentProvenance")
        if (
            self.run_specific_property_classes != _RUN_METADATA_CLASSES
            or len(self.run_specific_property_classes)
            != len(self.run_specific_evidence_refs)
        ):
            _failure(
                FailureCode.PROVENANCE_INVENTORY_INVALID,
                "EnvironmentProvenance",
                2,
            )

    def to_ecj1(self) -> dict[str, object]:
        return {field: _project(getattr(self, field)) for field in self.__dataclass_fields__}


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class ExecutionSemanticsProjection:
    accepted_configuration_ref: ObjectRef
    binding: ExecutionBinding
    execution_semantics_hash: ExecutionSemanticsHash
    source_provenance_ref: ObjectRef
    runtime_provenance_ref: ObjectRef
    environment_provenance_ref: ObjectRef
    included_property_classes: tuple[str, ...]
    excluded_run_metadata_classes: tuple[str, ...]

    def __post_init__(self) -> None:
        if not (
            type(self.accepted_configuration_ref) is ObjectRef
            and type(self.binding) is ExecutionBinding
            and type(self.execution_semantics_hash) is ExecutionSemanticsHash
            and type(self.source_provenance_ref) is ObjectRef
            and type(self.runtime_provenance_ref) is ObjectRef
            and type(self.environment_provenance_ref) is ObjectRef
            and type(self.included_property_classes) is tuple
            and all(type(item) is str for item in self.included_property_classes)
            and type(self.excluded_run_metadata_classes) is tuple
            and all(
                type(item) is str for item in self.excluded_run_metadata_classes
            )
        ):
            _formation_failure("ExecutionSemanticsProjection")
        if not (
            self.included_property_classes == _EXECUTION_SEMANTICS_CLASSES
            and self.excluded_run_metadata_classes == _RUN_METADATA_CLASSES
            and not set(self.included_property_classes)
            & set(self.excluded_run_metadata_classes)
        ):
            _failure(
                FailureCode.EXECUTION_SEMANTICS_CLASSIFICATION_INVALID,
                "ExecutionSemanticsProjection",
                2,
            )
        if not (
            self.accepted_configuration_ref == self.binding.accepted_configuration_ref
            and self.execution_semantics_hash == self.binding.execution_semantics_hash
        ):
            _failure(
                FailureCode.EXECUTION_SEMANTICS_PROJECTION_FAILURE,
                "ExecutionSemanticsProjection",
                3,
            )

    def to_ecj1(self) -> dict[str, object]:
        return {field: _project(getattr(self, field)) for field in self.__dataclass_fields__}


def _validate_execution_provenance(
    source: SourceProvenance,
    runtime: RuntimeProvenance,
    environment: EnvironmentProvenance,
    semantics: ExecutionSemanticsProjection,
    /,
) -> None:
    if not (
        type(source) is SourceProvenance
        and type(runtime) is RuntimeProvenance
        and type(environment) is EnvironmentProvenance
        and type(semantics) is ExecutionSemanticsProjection
    ):
        _formation_failure("_validate_execution_provenance")
    if not (
        runtime.included_property_classes == semantics.included_property_classes
        and environment.run_specific_property_classes
        == semantics.excluded_run_metadata_classes
    ):
        _failure(
            FailureCode.EXECUTION_SEMANTICS_CLASSIFICATION_INVALID,
            "_validate_execution_provenance",
            2,
        )
    return None


_DEPENDENCY_SENTINELS = (
    ArtifactRecord,
    TraceValidationResult,
    compute_execution_semantics_hash,
)


__all__ = (
    "SourceProvenance",
    "RuntimeProvenance",
    "EnvironmentProvenance",
    "ExecutionSemanticsProjection",
    "classify_execution_runtime_property",
)
