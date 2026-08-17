"""Immutable I-3 scheduling declarations and pure T0 coordination checks."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import NoReturn

from .actions import ActionInstance
from .network import RoutePlan
from .commitments import Reservation
from .primitives import Epoch, IntegerV1
from .identity import ObjectRef
from .envelopes import CommonObjectEnvelope, validate_object_envelope
from .errors import (
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
    return FailureInterfaceRef("ebu_framework.scheduling", name, "1.0.0")


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


def _ref_pair_tuple(value: object) -> bool:
    return (
        type(value) is tuple
        and all(
            type(pair) is tuple
            and len(pair) == 2
            and type(pair[0]) is ObjectRef
            and type(pair[1]) is ObjectRef
            for pair in value
        )
    )


def _epoch_tuple(value: object) -> bool:
    return type(value) is tuple and all(type(item) is Epoch for item in value)


def _ref_key(reference: ObjectRef) -> tuple[str, str, str]:
    return (
        str(reference.object_id),
        str(reference.object_version),
        str(reference.object_content_hash),
    )


def _epoch_key(epoch: Epoch) -> tuple[tuple[str, str, str], int]:
    return _ref_key(epoch.clock_ref), epoch.index.value


def _project(value: object) -> object:
    if isinstance(value, StrEnum):
        return value.value
    if type(value) is ObjectRef:
        return value.to_ecj1()
    if type(value) is tuple:
        return [_project(item) for item in value]
    if hasattr(value, "to_ecj1"):
        return value.to_ecj1()  # type: ignore[union-attr]
    return value


class ComparatorKind(StrEnum):
    OPEN_LOOP_REFERENCE = "OPEN_LOOP_REFERENCE"
    SEQUENTIAL_ORDER = "SEQUENTIAL_ORDER"
    DECLARED_ALTERNATIVE = "DECLARED_ALTERNATIVE"

    @classmethod
    def _missing_(cls, value: object) -> NoReturn:
        _formation_failure("ComparatorKind")


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class Schedule:
    envelope: CommonObjectEnvelope
    action_instance_refs: tuple[ObjectRef, ...]
    coordination_event_refs: tuple[ObjectRef, ...]
    precedence_edges: tuple[tuple[ObjectRef, ObjectRef], ...]
    allowed_overlap_pairs: tuple[tuple[ObjectRef, ObjectRef], ...]
    placement_refs: tuple[ObjectRef, ...]
    route_refs: tuple[ObjectRef, ...]
    reservation_refs: tuple[ObjectRef, ...]
    capacity_allocation_rule_refs: tuple[ObjectRef, ...]
    queue_rule_refs: tuple[ObjectRef, ...]
    failure_rule_refs: tuple[ObjectRef, ...]
    measurement_epochs: tuple[Epoch, ...]
    horizon_ref: ObjectRef
    comparator_schedule_refs: tuple[ObjectRef, ...]

    def __post_init__(self) -> None:
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and _object_ref_tuple(self.action_instance_refs)
            and _object_ref_tuple(self.coordination_event_refs)
            and _ref_pair_tuple(self.precedence_edges)
            and _ref_pair_tuple(self.allowed_overlap_pairs)
            and all(
                _object_ref_tuple(values)
                for values in (
                    self.placement_refs,
                    self.route_refs,
                    self.reservation_refs,
                    self.capacity_allocation_rule_refs,
                    self.queue_rule_refs,
                    self.failure_rule_refs,
                    self.comparator_schedule_refs,
                )
            )
            and _epoch_tuple(self.measurement_epochs)
            and type(self.horizon_ref) is ObjectRef
        ):
            _formation_failure("Schedule")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class ComparatorSchedule:
    envelope: CommonObjectEnvelope
    comparator_kind: ComparatorKind
    schedule_ref: ObjectRef
    ordering_rule_ref: ObjectRef
    baseline_state_ref: ObjectRef
    boundary_ref: ObjectRef
    horizon_ref: ObjectRef

    def __post_init__(self) -> None:
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and type(self.comparator_kind) is ComparatorKind
            and all(
                type(value) is ObjectRef
                for value in (
                    self.schedule_ref,
                    self.ordering_rule_ref,
                    self.baseline_state_ref,
                    self.boundary_ref,
                    self.horizon_ref,
                )
            )
        ):
            _formation_failure("ComparatorSchedule")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class CoordinationEventDeclaration:
    envelope: CommonObjectEnvelope
    event_kind_ref: ObjectRef
    epoch: Epoch
    actor_refs: tuple[ObjectRef, ...]
    object_refs: tuple[ObjectRef, ...]
    local_sequence: IntegerV1

    def __post_init__(self) -> None:
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and type(self.event_kind_ref) is ObjectRef
            and type(self.epoch) is Epoch
            and _object_ref_tuple(self.actor_refs)
            and _object_ref_tuple(self.object_refs)
            and type(self.local_sequence) is IntegerV1
        ):
            _formation_failure("CoordinationEventDeclaration")

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


def _object_content_check(record: object, interface: str) -> None:
    if record.envelope.to_ecj1()["object_content_payload"] != record.to_ecj1():  # type: ignore[attr-defined]
        _failure(
            FailureCode.I3_OBJECT_CONTENT_MISMATCH,
            interface,
            summary=(
                f"{interface} rejected I3_OBJECT_CONTENT_MISMATCH "
                "at argument 1 (record)"
            ),
            object_ref=_failure_object(record),
        )


def _ordered_refs(values: tuple[ObjectRef, ...]) -> bool:
    keys = tuple(_ref_key(item) for item in values)
    return keys == tuple(sorted(keys))


def _duplicate_refs(values: tuple[ObjectRef, ...]) -> bool:
    keys = tuple(_ref_key(item) for item in values)
    return len(keys) != len(set(keys))


def _ordered_pairs(values: tuple[tuple[ObjectRef, ObjectRef], ...]) -> bool:
    keys = tuple(_ref_key(left) for left, _ in values)
    return keys == tuple(sorted(keys))


def _duplicate_pairs(values: tuple[tuple[ObjectRef, ObjectRef], ...]) -> bool:
    first_keys = tuple(_ref_key(left) for left, _ in values)
    complete_keys = tuple((_ref_key(left), _ref_key(right)) for left, right in values)
    return len(first_keys) != len(set(first_keys)) or len(complete_keys) != len(
        set(complete_keys)
    )


def _ordered_epochs(values: tuple[Epoch, ...]) -> bool:
    keys = tuple(_epoch_key(item) for item in values)
    return keys == tuple(sorted(keys))


def _duplicate_epochs(values: tuple[Epoch, ...]) -> bool:
    keys = tuple(_epoch_key(item) for item in values)
    return len(keys) != len(set(keys))


def _object_hash_matches(record: object) -> bool:
    try:
        validate_object_envelope(record.envelope)  # type: ignore[attr-defined]
    except FrameworkError:
        return False
    return True


def validate_schedule(
    record: Schedule | ComparatorSchedule | CoordinationEventDeclaration,
    /,
) -> None:
    if type(record) not in (Schedule, ComparatorSchedule, CoordinationEventDeclaration):
        _formation_failure("Schedule")
    interface = "validate_schedule"
    _object_content_check(record, interface)

    if type(record) is Schedule:
        ref_collections = (
            record.placement_refs,
            record.route_refs,
            record.reservation_refs,
            record.capacity_allocation_rule_refs,
            record.queue_rule_refs,
            record.failure_rule_refs,
            record.comparator_schedule_refs,
        )
        if (
            any(not _ordered_refs(values) for values in ref_collections)
            or not _ordered_pairs(record.precedence_edges)
            or not _ordered_pairs(record.allowed_overlap_pairs)
            or not _ordered_epochs(record.measurement_epochs)
        ):
            _failure(FailureCode.I3_COLLECTION_ORDER_INVALID, interface)
        if (
            any(_duplicate_refs(values) for values in ref_collections)
            or _duplicate_refs(record.action_instance_refs)
            or _duplicate_refs(record.coordination_event_refs)
            or _duplicate_pairs(record.precedence_edges)
            or _duplicate_pairs(record.allowed_overlap_pairs)
            or _duplicate_epochs(record.measurement_epochs)
        ):
            _failure(FailureCode.I3_DUPLICATE_MEMBER, interface)
        precedence = {
            (_ref_key(left), _ref_key(right))
            for left, right in record.precedence_edges
        }
        overlap = {
            (_ref_key(left), _ref_key(right))
            for left, right in record.allowed_overlap_pairs
        }
        if any(left == right for left, right in precedence) or precedence & overlap:
            _failure(FailureCode.INADMISSIBLE_SCHEDULE, interface)
        if record.action_instance_refs and not record.comparator_schedule_refs:
            _failure(FailureCode.MISSING_COMPARATOR, interface)

    elif type(record) is CoordinationEventDeclaration:
        collections = (record.actor_refs, record.object_refs)
        if any(not _ordered_refs(values) for values in collections):
            _failure(FailureCode.I3_COLLECTION_ORDER_INVALID, interface)
        if any(_duplicate_refs(values) for values in collections):
            _failure(FailureCode.I3_DUPLICATE_MEMBER, interface)

    if not _object_hash_matches(record):
        _failure(FailureCode.HASH_MISMATCH, interface)
    return None


_DEPENDENCY_SENTINELS = (ActionInstance, RoutePlan, Reservation)


__all__ = (
    "Schedule",
    "ComparatorSchedule",
    "ComparatorKind",
    "CoordinationEventDeclaration",
    "validate_schedule",
)
