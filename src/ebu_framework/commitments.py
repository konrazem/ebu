"""Immutable I-3 commitment declarations and pure T0 consistency checks."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from fractions import Fraction
from typing import NoReturn, get_args

from .actions import ActionInstance, EffectiveInterval
from .network import CapacityLocus
from .primitives import CoreNumberV1, Epoch, Quantity
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


_CORE_NUMBER_TYPES = get_args(CoreNumberV1)


def _interface(name: str) -> FailureInterfaceRef:
    return FailureInterfaceRef("ebu_framework.commitments", name, "1.0.0")


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


def _ref_key(reference: ObjectRef) -> tuple[str, str, str]:
    return (
        str(reference.object_id),
        str(reference.object_version),
        str(reference.object_content_hash),
    )


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


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class Commitment:
    envelope: CommonObjectEnvelope
    provider_ref: ObjectRef
    beneficiary_ref: ObjectRef
    service_or_quantity_ref: ObjectRef
    time_window: EffectiveInterval
    condition_refs: tuple[ObjectRef, ...]
    guarantee_class_ref: ObjectRef
    status_ref: ObjectRef
    breach_rule_ref: ObjectRef
    quote_ref: ObjectRef
    reservation_refs: tuple[ObjectRef, ...]

    def __post_init__(self) -> None:
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and all(
                type(value) is ObjectRef
                for value in (
                    self.provider_ref,
                    self.beneficiary_ref,
                    self.service_or_quantity_ref,
                    self.guarantee_class_ref,
                    self.status_ref,
                    self.breach_rule_ref,
                    self.quote_ref,
                )
            )
            and type(self.time_window) is EffectiveInterval
            and _object_ref_tuple(self.condition_refs)
            and _object_ref_tuple(self.reservation_refs)
        ):
            _formation_failure("Commitment")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class Reservation:
    envelope: CommonObjectEnvelope
    action_ref: ObjectRef
    capacity_locus_ref: ObjectRef
    resource_type_ref: ObjectRef
    interval: EffectiveInterval
    reserved_quantity: Quantity
    capacity_snapshot_ref: ObjectRef
    uncertainty_rule_ref: ObjectRef
    priority_rule_ref: ObjectRef
    release_condition_ref: ObjectRef
    status_ref: ObjectRef

    def __post_init__(self) -> None:
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and all(
                type(value) is ObjectRef
                for value in (
                    self.action_ref,
                    self.capacity_locus_ref,
                    self.resource_type_ref,
                    self.capacity_snapshot_ref,
                    self.uncertainty_rule_ref,
                    self.priority_rule_ref,
                    self.release_condition_ref,
                    self.status_ref,
                )
            )
            and type(self.interval) is EffectiveInterval
            and type(self.reserved_quantity) is Quantity
        ):
            _formation_failure("Reservation")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class CapacityRecord:
    envelope: CommonObjectEnvelope
    capacity_locus_ref: ObjectRef
    resource_type_ref: ObjectRef
    epoch: Epoch
    installed: Quantity
    availability_factor: CoreNumberV1
    usable: Quantity
    reserved: Quantity
    admitted: Quantity
    completed: Quantity

    def __post_init__(self) -> None:
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and type(self.capacity_locus_ref) is ObjectRef
            and type(self.resource_type_ref) is ObjectRef
            and type(self.epoch) is Epoch
            and all(
                type(value) is Quantity
                for value in (
                    self.installed,
                    self.usable,
                    self.reserved,
                    self.admitted,
                    self.completed,
                )
            )
            and type(self.availability_factor) in _CORE_NUMBER_TYPES
        ):
            _formation_failure("CapacityRecord")

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
    if record.envelope.to_ecj1()["object_content_payload"] != record.to_ecj1():  # type: ignore[attr-defined]
        _failure(
            FailureCode.I3_OBJECT_CONTENT_MISMATCH,
            interface,
            summary=(
                f"{interface} rejected I3_OBJECT_CONTENT_MISMATCH at {position}"
            ),
            object_ref=_failure_object(record),
        )


def _ordered_refs(values: tuple[ObjectRef, ...]) -> bool:
    keys = tuple(_ref_key(item) for item in values)
    return keys == tuple(sorted(keys))


def _duplicate_refs(values: tuple[ObjectRef, ...]) -> bool:
    keys = tuple(_ref_key(item) for item in values)
    return len(keys) != len(set(keys))


def _object_hash_matches(record: object) -> bool:
    try:
        validate_object_envelope(record.envelope)  # type: ignore[attr-defined]
    except FrameworkError:
        return False
    return True


def _interval_reversed(interval: EffectiveInterval) -> bool:
    return interval.end.tick.value < interval.start.tick.value


def _core_fraction(value: CoreNumberV1) -> Fraction:
    projected = value.to_ecj1()
    variant = projected["variant"]
    if variant == "INTEGER_V1":
        return Fraction(projected["value"])
    if variant == "RATIONAL_V1":
        return Fraction(projected["numerator"], projected["denominator"])
    if variant == "DECIMAL_V1":
        coefficient = projected["coefficient"]
        exponent = projected["exponent10"]
        if exponent >= 0:
            return Fraction(coefficient * 10**exponent)
        return Fraction(coefficient, 10 ** (-exponent))

    bits = int(projected["bits"], 16)
    sign = -1 if bits >> 63 else 1
    exponent_bits = (bits >> 52) & 0x7FF
    fraction_bits = bits & ((1 << 52) - 1)
    if exponent_bits == 0:
        significand = fraction_bits
        exponent = -1074
    else:
        significand = (1 << 52) | fraction_bits
        exponent = exponent_bits - 1023 - 52
    if exponent >= 0:
        return Fraction(sign * significand * 2**exponent)
    return Fraction(sign * significand, 2 ** (-exponent))


def _quantity_units_match(left: Quantity, right: Quantity) -> bool:
    return left.unit_ref == right.unit_ref and left.dimension_ref == right.dimension_ref


def _capacity_arithmetic_invalid(record: CapacityRecord) -> bool:
    installed, usable, reserved, admitted, completed = (
        _core_fraction(quantity.magnitude)
        for quantity in (
            record.installed,
            record.usable,
            record.reserved,
            record.admitted,
            record.completed,
        )
    )
    factor = _core_fraction(record.availability_factor)
    return (
        min(installed, usable, reserved, admitted, completed, factor) < 0
        or usable > installed
    )


def validate_commitment(record: Commitment, /) -> None:
    if type(record) is not Commitment:
        _formation_failure("Commitment")
    interface = "validate_commitment"
    _object_content_check(record, interface, "argument 1 (record)")
    collections = (record.condition_refs, record.reservation_refs)
    if any(not _ordered_refs(values) for values in collections):
        _failure(FailureCode.I3_COLLECTION_ORDER_INVALID, interface)
    if any(_duplicate_refs(values) for values in collections):
        _failure(FailureCode.I3_DUPLICATE_MEMBER, interface)
    if _interval_reversed(record.time_window):
        _failure(FailureCode.ACTION_DECLARATION_INVALID, interface)
    if not _object_hash_matches(record):
        _failure(FailureCode.HASH_MISMATCH, interface)
    return None


def validate_reservation(record: Reservation, capacity: CapacityRecord, /) -> None:
    if type(record) is not Reservation:
        _formation_failure("Reservation")
    if type(capacity) is not CapacityRecord:
        _formation_failure("CapacityRecord")
    interface = "validate_reservation"
    _object_content_check(record, interface, "argument 1 (record)")
    _object_content_check(capacity, interface, "argument 2 (capacity)")

    if _interval_reversed(record.interval) or _core_fraction(record.reserved_quantity.magnitude) < 0:
        _failure(FailureCode.ACTION_DECLARATION_INVALID, interface)
    if not _quantity_units_match(record.reserved_quantity, capacity.usable):
        _failure(FailureCode.CONSERVATION_UNIT_MISMATCH, interface)
    capacity_ref = ObjectRef(
        object_id=capacity.envelope.object_id,
        object_version=capacity.envelope.object_version,
        object_content_hash=capacity.envelope.object_content_hash,
    )
    if not (
        record.capacity_locus_ref == capacity.capacity_locus_ref
        and record.resource_type_ref == capacity.resource_type_ref
        and record.capacity_snapshot_ref == capacity_ref
    ):
        _failure(FailureCode.RESERVATION_CAPACITY_MISMATCH, interface)
    if not _object_hash_matches(record) or not _object_hash_matches(capacity):
        _failure(FailureCode.HASH_MISMATCH, interface)
    return None


def validate_capacity_record(record: CapacityRecord, /) -> None:
    if type(record) is not CapacityRecord:
        _formation_failure("CapacityRecord")
    interface = "validate_capacity_record"
    _object_content_check(record, interface, "argument 1 (record)")

    if any(
        not _quantity_units_match(record.installed, quantity)
        for quantity in (
            record.usable,
            record.reserved,
            record.admitted,
            record.completed,
        )
    ):
        _failure(FailureCode.CONSERVATION_UNIT_MISMATCH, interface)
    if _capacity_arithmetic_invalid(record):
        _failure(FailureCode.ACTION_DECLARATION_INVALID, interface)
    if not _object_hash_matches(record):
        _failure(FailureCode.HASH_MISMATCH, interface)
    return None


_DEPENDENCY_SENTINELS = (ActionInstance, CapacityLocus)


__all__ = (
    "Commitment",
    "Reservation",
    "CapacityRecord",
    "validate_commitment",
    "validate_reservation",
    "validate_capacity_record",
)
