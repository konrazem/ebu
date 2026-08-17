"""Immutable I-3 fault declarations and local boundary validation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import json
from typing import Literal, NoReturn

from .primitives import Epoch, IntegerV1
from .identity import ObjectRef, ScientificId
from .envelopes import CommonObjectEnvelope, parse_ecj1
from .hashing import compute_object_content_hash
from .errors import (
    Applicability,
    FailureCode,
    FailureInterfaceRef,
    FailureObjectRef,
    FailureStage,
    FrameworkError,
    RetryClass,
    ScientificStatusEffect,
    _fail,
)


def _interface(name: str) -> FailureInterfaceRef:
    return FailureInterfaceRef("ebu_framework.faults", name, "1.0.0")


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


def _object_or_applicability(value: object) -> bool:
    return type(value) is ObjectRef or type(value) is Applicability


def _integer_or_applicability(value: object) -> bool:
    return type(value) is IntegerV1 or type(value) is Applicability


def _epoch_or_applicability(value: object) -> bool:
    return type(value) is Epoch or type(value) is Applicability


def _project(value: object) -> object:
    if type(value) is ScientificId:
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


class FaultClass(StrEnum):
    SCIENTIFIC_MODEL_EVENT = "SCIENTIFIC_MODEL_EVENT"
    OPERATIONAL_DURABILITY_INJECTION = "OPERATIONAL_DURABILITY_INJECTION"

    @classmethod
    def _missing_(cls, value: object) -> NoReturn:
        _formation_failure("FaultClass")


class FaultScheduleClass(StrEnum):
    SCIENTIFIC_STUDY = "SCIENTIFIC_STUDY"
    INERT_VALIDATION = "INERT_VALIDATION"

    @classmethod
    def _missing_(cls, value: object) -> NoReturn:
        _formation_failure("FaultScheduleClass")


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class FaultTargetCoordinate:
    target_kind: Literal["MODEL_EVENT", "DURABILITY_BOUNDARY"]
    epoch: Epoch | Applicability
    phase_ordinal: IntegerV1 | Applicability
    scope_ref: ObjectRef | Applicability
    event_kind_ref: ObjectRef | Applicability
    primary_object_ref: ObjectRef | Applicability
    durability_boundary_ref: ObjectRef | Applicability
    occurrence_ordinal: IntegerV1 | Applicability
    local_sequence: IntegerV1

    def __post_init__(self) -> None:
        if not (
            type(self.target_kind) is str
            and self.target_kind in {"MODEL_EVENT", "DURABILITY_BOUNDARY"}
            and _epoch_or_applicability(self.epoch)
            and _integer_or_applicability(self.phase_ordinal)
            and _object_or_applicability(self.scope_ref)
            and _object_or_applicability(self.event_kind_ref)
            and _object_or_applicability(self.primary_object_ref)
            and _object_or_applicability(self.durability_boundary_ref)
            and _integer_or_applicability(self.occurrence_ordinal)
            and type(self.local_sequence) is IntegerV1
        ):
            _formation_failure("FaultTargetCoordinate")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
        }


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class FaultDirectiveV1:
    fault_id: ScientificId
    fault_kind_ref: ObjectRef
    fault_class: FaultClass
    target_coordinate: FaultTargetCoordinate
    trigger_predicate_ref: ObjectRef
    effect_payload_ref: ObjectRef
    declared_priority: IntegerV1
    local_sequence: IntegerV1
    delivery_acknowledgement_rule_ref: ObjectRef
    continuation_or_terminal_rule_ref: ObjectRef

    def __post_init__(self) -> None:
        if not (
            type(self.fault_id) is ScientificId
            and type(self.fault_kind_ref) is ObjectRef
            and type(self.fault_class) is FaultClass
            and type(self.target_coordinate) is FaultTargetCoordinate
            and type(self.trigger_predicate_ref) is ObjectRef
            and type(self.effect_payload_ref) is ObjectRef
            and type(self.declared_priority) is IntegerV1
            and type(self.local_sequence) is IntegerV1
            and type(self.delivery_acknowledgement_rule_ref) is ObjectRef
            and type(self.continuation_or_terminal_rule_ref) is ObjectRef
        ):
            _formation_failure("FaultDirectiveV1")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
        }


def _directive_tuple(value: object) -> bool:
    return type(value) is tuple and all(
        type(item) is FaultDirectiveV1 for item in value
    )


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class FaultScheduleV1:
    envelope: CommonObjectEnvelope
    schedule_class: FaultScheduleClass
    owning_study_or_validation_protocol_ref: ObjectRef
    fault_extension_registry_ref: ObjectRef
    ordered_fault_directives: tuple[FaultDirectiveV1, ...]
    ordering_contract_ref: ObjectRef
    delivery_contract_ref: ObjectRef
    expected_trace_completeness_rule_ref: ObjectRef

    def __post_init__(self) -> None:
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and type(self.schedule_class) is FaultScheduleClass
            and type(self.owning_study_or_validation_protocol_ref) is ObjectRef
            and type(self.fault_extension_registry_ref) is ObjectRef
            and _directive_tuple(self.ordered_fault_directives)
            and type(self.ordering_contract_ref) is ObjectRef
            and type(self.delivery_contract_ref) is ObjectRef
            and type(self.expected_trace_completeness_rule_ref) is ObjectRef
        ):
            _formation_failure("FaultScheduleV1")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
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


def _directive_key(directive: FaultDirectiveV1) -> tuple[bytes, int, int, str]:
    target = json.dumps(
        directive.target_coordinate.to_ecj1(),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8", "strict")
    return (
        target,
        directive.declared_priority.value,
        directive.local_sequence.value,
        str(directive.fault_id),
    )


def _target_is_valid(directive: FaultDirectiveV1) -> bool:
    target = directive.target_coordinate
    def present(value: object, expected: type) -> bool:
        return type(value) is expected or value is Applicability.APPLICABLE

    def absent(value: object) -> bool:
        return value in {
            Applicability.NOT_APPLICABLE,
            Applicability.APPLICABLE,
        }

    model_fields = (
        present(target.epoch, Epoch),
        present(target.phase_ordinal, IntegerV1),
        present(target.scope_ref, ObjectRef),
        present(target.event_kind_ref, ObjectRef),
        present(target.primary_object_ref, ObjectRef),
        absent(target.durability_boundary_ref),
        absent(target.occurrence_ordinal),
    )
    durability_fields = (
        absent(target.epoch),
        absent(target.phase_ordinal),
        absent(target.scope_ref),
        absent(target.event_kind_ref),
        absent(target.primary_object_ref),
        present(target.durability_boundary_ref, ObjectRef),
        present(target.occurrence_ordinal, IntegerV1),
    )
    if directive.fault_class is FaultClass.SCIENTIFIC_MODEL_EVENT:
        return target.target_kind == "MODEL_EVENT" and all(model_fields)
    return target.target_kind == "DURABILITY_BOUNDARY" and all(
        durability_fields
    )


def validate_fault_schedule_boundary(schedule: FaultScheduleV1, /) -> None:
    if type(schedule) is not FaultScheduleV1:
        _formation_failure("FaultScheduleV1")
    interface = "validate_fault_schedule_boundary"
    _object_content_check(schedule, interface, "argument 1 (schedule)")

    applicability_values = tuple(
        value
        for directive in schedule.ordered_fault_directives
        for value in (
            directive.target_coordinate.epoch,
            directive.target_coordinate.phase_ordinal,
            directive.target_coordinate.scope_ref,
            directive.target_coordinate.event_kind_ref,
            directive.target_coordinate.primary_object_ref,
            directive.target_coordinate.durability_boundary_ref,
            directive.target_coordinate.occurrence_ordinal,
        )
    )
    if any(value is Applicability.APPLICABLE for value in applicability_values):
        _failure(FailureCode.IMPLICIT_ABSENCE_FORBIDDEN, interface)

    keys = tuple(_directive_key(item) for item in schedule.ordered_fault_directives)
    if keys != tuple(sorted(keys)):
        _failure(FailureCode.I3_COLLECTION_ORDER_INVALID, interface)
    if any(
        left == right
        for index, left in enumerate(schedule.ordered_fault_directives)
        for right in schedule.ordered_fault_directives[index + 1 :]
    ):
        _failure(FailureCode.I3_DUPLICATE_MEMBER, interface)
    if any(
        not _target_is_valid(directive)
        for directive in schedule.ordered_fault_directives
    ):
        _failure(FailureCode.FAULT_SCHEDULE_INVALID, interface)
    if not _object_hash_matches(schedule):
        _failure(FailureCode.HASH_MISMATCH, interface)
    return None


__all__ = (
    "FaultScheduleV1",
    "FaultDirectiveV1",
    "FaultClass",
    "FaultTargetCoordinate",
    "FaultScheduleClass",
    "validate_fault_schedule_boundary",
)
