"""Immutable I-3 experiment configuration and binding declarations."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import json
from typing import Literal, NoReturn

from .conservation import ConservationProfileSelection
from .policy import MemoryMode
from .faults import FaultScheduleV1
from .primitives import IntegerV1
from .identity import ExecutionSemanticsHash, ObjectRef
from .envelopes import CommonObjectEnvelope, parse_ecj1
from .hashing import compute_execution_semantics_hash, compute_object_content_hash
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
    return FailureInterfaceRef("ebu_framework.experiment", name, "1.0.0")


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
    if type(value) is ExecutionSemanticsHash:
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


class ExecutionMode(StrEnum):
    DETERMINISTIC = "DETERMINISTIC"
    STOCHASTIC_DECLARATION_ONLY = "STOCHASTIC_DECLARATION_ONLY"

    @classmethod
    def _missing_(cls, value: object) -> NoReturn:
        _formation_failure("ExecutionMode")


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class OperationalExclusion:
    exclusion_kind: Literal["SCIENCE_AFFECTING", "RUN_SPECIFIC"]
    property_ref: ObjectRef
    classification_reason_ref: ObjectRef
    science_affecting: bool

    def __post_init__(self) -> None:
        if not (
            type(self.exclusion_kind) is str
            and self.exclusion_kind in {"SCIENCE_AFFECTING", "RUN_SPECIFIC"}
            and type(self.property_ref) is ObjectRef
            and type(self.classification_reason_ref) is ObjectRef
            and type(self.science_affecting) is bool
        ):
            _formation_failure("OperationalExclusion")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
        }


def _exclusion_tuple(value: object) -> bool:
    return type(value) is tuple and all(
        type(item) is OperationalExclusion for item in value
    )


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class ExperimentConfiguration:
    envelope: CommonObjectEnvelope
    configuration_schema_ref: ObjectRef
    scientific_foundation_refs: tuple[ObjectRef, ...]
    initial_state_ref: ObjectRef
    boundary_ref: ObjectRef
    conservation_profile_selection: ConservationProfileSelection
    distortion_ref: ObjectRef
    action_definition_refs: tuple[ObjectRef, ...]
    schedule_refs: tuple[ObjectRef, ...]
    policy_ref: ObjectRef | Applicability
    policy_memory_mode: MemoryMode
    initial_policy_memory_ref: ObjectRef | Applicability
    comparator_refs: tuple[ObjectRef, ...]
    parameter_refs: tuple[ObjectRef, ...]
    numerical_policy_refs: tuple[ObjectRef, ...]
    metric_refs: tuple[ObjectRef, ...]
    classification_rule_refs: tuple[ObjectRef, ...]
    analysis_rule_refs: tuple[ObjectRef, ...]
    fault_schedule_ref: ObjectRef | Applicability
    seed_refs: tuple[ObjectRef, ...]
    horizon_ref: ObjectRef

    def __post_init__(self) -> None:
        reference_tuples = (
            self.scientific_foundation_refs,
            self.action_definition_refs,
            self.schedule_refs,
            self.comparator_refs,
            self.parameter_refs,
            self.numerical_policy_refs,
            self.metric_refs,
            self.classification_rule_refs,
            self.analysis_rule_refs,
            self.seed_refs,
        )
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and type(self.configuration_schema_ref) is ObjectRef
            and all(_object_ref_tuple(values) for values in reference_tuples)
            and type(self.initial_state_ref) is ObjectRef
            and type(self.boundary_ref) is ObjectRef
            and type(self.conservation_profile_selection)
            is ConservationProfileSelection
            and type(self.distortion_ref) is ObjectRef
            and _object_or_applicability(self.policy_ref)
            and type(self.policy_memory_mode) is MemoryMode
            and _object_or_applicability(self.initial_policy_memory_ref)
            and _object_or_applicability(self.fault_schedule_ref)
            and type(self.horizon_ref) is ObjectRef
        ):
            _formation_failure("ExperimentConfiguration")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class ExecutionBinding:
    envelope: CommonObjectEnvelope
    accepted_configuration_ref: ObjectRef
    implementation_refs: tuple[ObjectRef, ...]
    source_refs: tuple[ObjectRef, ...]
    entrypoint_semantics_ref: ObjectRef
    runtime_constraint_refs: tuple[ObjectRef, ...]
    operational_exclusions: tuple[OperationalExclusion, ...]
    policy_memory_transition_contract_refs: tuple[ObjectRef, ...]
    fault_delivery_contract_refs: tuple[ObjectRef, ...]
    event_order_contract_ref: ObjectRef
    numerical_policy_contract_refs: tuple[ObjectRef, ...]
    information_capability_contract_ref: ObjectRef
    trace_schema_ref: ObjectRef
    result_schema_ref: ObjectRef
    stochastic_contract_ref: ObjectRef | Applicability
    execution_semantics_hash: ExecutionSemanticsHash

    def __post_init__(self) -> None:
        reference_tuples = (
            self.implementation_refs,
            self.source_refs,
            self.runtime_constraint_refs,
            self.policy_memory_transition_contract_refs,
            self.fault_delivery_contract_refs,
            self.numerical_policy_contract_refs,
        )
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and type(self.accepted_configuration_ref) is ObjectRef
            and all(_object_ref_tuple(values) for values in reference_tuples)
            and type(self.entrypoint_semantics_ref) is ObjectRef
            and _exclusion_tuple(self.operational_exclusions)
            and type(self.event_order_contract_ref) is ObjectRef
            and type(self.information_capability_contract_ref) is ObjectRef
            and type(self.trace_schema_ref) is ObjectRef
            and type(self.result_schema_ref) is ObjectRef
            and _object_or_applicability(self.stochastic_contract_ref)
            and type(self.execution_semantics_hash) is ExecutionSemanticsHash
        ):
            _formation_failure("ExecutionBinding")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field not in {"envelope", "execution_semantics_hash"}
        }


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class ExecutionIdentity:
    identity_ref: ObjectRef
    execution_mode: ExecutionMode
    configuration_ref: ObjectRef
    binding_ref: ObjectRef
    attempt_ordinal: IntegerV1

    def __post_init__(self) -> None:
        if not (
            type(self.identity_ref) is ObjectRef
            and type(self.execution_mode) is ExecutionMode
            and type(self.configuration_ref) is ObjectRef
            and type(self.binding_ref) is ObjectRef
            and type(self.attempt_ordinal) is IntegerV1
        ):
            _formation_failure("ExecutionIdentity")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
        }


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


def _exclusion_key(value: OperationalExclusion) -> tuple[tuple[str, str, str], bytes]:
    projection = json.dumps(
        value.to_ecj1(),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8", "strict")
    return _ref_key(value.property_ref), projection


def _ordered_exclusions(values: tuple[OperationalExclusion, ...]) -> bool:
    keys = tuple(_exclusion_key(item) for item in values)
    return keys == tuple(sorted(keys))


def _duplicate_exclusions(values: tuple[OperationalExclusion, ...]) -> bool:
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


def _optional_ref_collection(values: tuple[ObjectRef, ...]) -> object:
    if not values:
        return Applicability.NOT_APPLICABLE.value
    return [_project(value) for value in values]


def _execution_semantics_hash_matches(binding: ExecutionBinding) -> bool:
    science_affecting_exclusions = [
        exclusion.to_ecj1()
        for exclusion in binding.operational_exclusions
        if exclusion.science_affecting
    ]
    stochastic = _project(binding.stochastic_contract_ref)
    recomputed = compute_execution_semantics_hash(
        accepted_configuration_ref=binding.accepted_configuration_ref,
        implementation_refs=binding.implementation_refs,
        source_refs=binding.source_refs,
        implementation_entrypoint_semantics=(
            binding.entrypoint_semantics_ref.to_ecj1()
        ),
        science_affecting_runtime_constraints=[
            reference.to_ecj1() for reference in binding.runtime_constraint_refs
        ],
        science_affecting_operational_exclusions=science_affecting_exclusions,
        policy_memory_transition_contracts_or_not_applicable=(
            _optional_ref_collection(
                binding.policy_memory_transition_contract_refs
            )
        ),
        fault_injection_delivery_contracts_or_not_applicable=(
            _optional_ref_collection(binding.fault_delivery_contract_refs)
        ),
        event_order_contract=binding.event_order_contract_ref.to_ecj1(),
        arithmetic_and_numerical_policy_contracts=[
            reference.to_ecj1()
            for reference in binding.numerical_policy_contract_refs
        ],
        information_capability_contract=(
            binding.information_capability_contract_ref.to_ecj1()
        ),
        canonical_scientific_trace_schema_ref=binding.trace_schema_ref,
        scientific_result_schema_ref=binding.result_schema_ref,
        stochastic_generator_and_stream_contract_or_not_applicable=stochastic,
    )
    return recomputed == binding.execution_semantics_hash


def validate_experiment_configuration(
    configuration: ExperimentConfiguration,
    fault_schedule: FaultScheduleV1 | Applicability,
    /,
) -> None:
    if type(configuration) is not ExperimentConfiguration:
        _formation_failure("ExperimentConfiguration")
    if type(fault_schedule) not in (FaultScheduleV1, Applicability):
        _formation_failure("FaultScheduleV1")
    interface = "validate_experiment_configuration"
    _object_content_check(configuration, interface, "argument 1 (configuration)")
    if type(fault_schedule) is FaultScheduleV1:
        _object_content_check(
            fault_schedule,
            interface,
            "argument 2 (fault_schedule)",
        )

    applicability_values = (
        configuration.policy_ref,
        configuration.initial_policy_memory_ref,
        configuration.fault_schedule_ref,
        fault_schedule,
    )
    if any(value is Applicability.APPLICABLE for value in applicability_values):
        _failure(FailureCode.IMPLICIT_ABSENCE_FORBIDDEN, interface)

    collections = (
        configuration.scientific_foundation_refs,
        configuration.action_definition_refs,
        configuration.schedule_refs,
        configuration.comparator_refs,
        configuration.parameter_refs,
        configuration.numerical_policy_refs,
        configuration.metric_refs,
        configuration.classification_rule_refs,
        configuration.analysis_rule_refs,
        configuration.seed_refs,
    )
    if any(not _ordered_refs(values) for values in collections):
        _failure(FailureCode.I3_COLLECTION_ORDER_INVALID, interface)
    if any(_duplicate_refs(values) for values in collections):
        _failure(FailureCode.I3_DUPLICATE_MEMBER, interface)
    if any(not values for values in collections):
        _failure(FailureCode.CONFIGURATION_INCOMPLETE, interface)

    stateless = configuration.policy_memory_mode is MemoryMode.STATELESS
    policy_absent = configuration.policy_ref is Applicability.NOT_APPLICABLE
    memory_absent = (
        configuration.initial_policy_memory_ref
        is Applicability.NOT_APPLICABLE
    )
    if stateless != (policy_absent and memory_absent) or (
        not stateless and (policy_absent or memory_absent)
    ):
        _failure(FailureCode.POLICY_MEMORY_NOT_APPLICABLE, interface)

    configured_fault = configuration.fault_schedule_ref
    if type(configured_fault) is ObjectRef:
        fault_available = (
            type(fault_schedule) is FaultScheduleV1
            and configured_fault == _envelope_ref(fault_schedule)
        )
    else:
        fault_available = fault_schedule is Applicability.NOT_APPLICABLE
    if not fault_available:
        _failure(FailureCode.FAULT_EXTENSION_UNAVAILABLE, interface)

    records = (configuration,) + (
        (fault_schedule,) if type(fault_schedule) is FaultScheduleV1 else ()
    )
    if any(not _object_hash_matches(record) for record in records):
        _failure(FailureCode.HASH_MISMATCH, interface)
    return None


def validate_execution_binding(binding: ExecutionBinding, /) -> None:
    if type(binding) is not ExecutionBinding:
        _formation_failure("ExecutionBinding")
    interface = "validate_execution_binding"
    _object_content_check(binding, interface, "argument 1 (binding)")

    if binding.stochastic_contract_ref is Applicability.APPLICABLE:
        _failure(FailureCode.IMPLICIT_ABSENCE_FORBIDDEN, interface)
    ref_collections = (
        binding.implementation_refs,
        binding.source_refs,
        binding.runtime_constraint_refs,
        binding.policy_memory_transition_contract_refs,
        binding.fault_delivery_contract_refs,
        binding.numerical_policy_contract_refs,
    )
    if any(not _ordered_refs(values) for values in ref_collections) or not (
        _ordered_exclusions(binding.operational_exclusions)
    ):
        _failure(FailureCode.I3_COLLECTION_ORDER_INVALID, interface)
    if any(_duplicate_refs(values) for values in ref_collections) or (
        _duplicate_exclusions(binding.operational_exclusions)
    ):
        _failure(FailureCode.I3_DUPLICATE_MEMBER, interface)
    if not _execution_semantics_hash_matches(binding):
        _failure(FailureCode.EXECUTION_SEMANTICS_PROJECTION_FAILURE, interface)
    if not _object_hash_matches(binding):
        _failure(FailureCode.HASH_MISMATCH, interface)
    return None


__all__ = (
    "ExperimentConfiguration",
    "ExecutionBinding",
    "ExecutionMode",
    "OperationalExclusion",
    "ExecutionIdentity",
    "validate_experiment_configuration",
    "validate_execution_binding",
)
