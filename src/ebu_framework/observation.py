"""Immutable I-3 observation declarations and pure T0 contract checks."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import NoReturn

from .state import SystemState
from .primitives import Epoch, Quantity, ResolutionDetail, UncertaintyRecord
from .identity import ObjectRef
from .envelopes import CommonObjectEnvelope, validate_object_envelope
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
    return FailureInterfaceRef("ebu_framework.observation", name, "1.0.0")


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
class Measurement:
    envelope: CommonObjectEnvelope
    measured_object_ref: ObjectRef
    coordinate_ref: ObjectRef
    value: Quantity | ResolutionDetail
    measurement_epoch: Epoch
    availability_epoch: Epoch
    calibration_ref: ObjectRef
    uncertainty: UncertaintyRecord
    method_ref: ObjectRef
    operator_ref: ObjectRef
    boundary_ref: ObjectRef
    raw_evidence_ref: ObjectRef | Applicability

    def __post_init__(self) -> None:
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and all(
                type(value) is ObjectRef
                for value in (
                    self.measured_object_ref,
                    self.coordinate_ref,
                    self.calibration_ref,
                    self.method_ref,
                    self.operator_ref,
                    self.boundary_ref,
                )
            )
            and (
                type(self.value) is Quantity
                or type(self.value) is ResolutionDetail
            )
            and type(self.measurement_epoch) is Epoch
            and type(self.availability_epoch) is Epoch
            and type(self.uncertainty) is UncertaintyRecord
            and (
                type(self.raw_evidence_ref) is ObjectRef
                or type(self.raw_evidence_ref) is Applicability
            )
        ):
            _formation_failure("Measurement")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class MeasurementContract:
    envelope: CommonObjectEnvelope
    measured_object_ref: ObjectRef
    coordinate_ref: ObjectRef
    unit_ref: ObjectRef
    measurement_epoch_refs: tuple[ObjectRef, ...]
    availability_rule_ref: ObjectRef
    calibration_ref: ObjectRef
    uncertainty_rule_ref: ObjectRef
    evidence_rule_ref: ObjectRef

    def __post_init__(self) -> None:
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and all(
                type(value) is ObjectRef
                for value in (
                    self.measured_object_ref,
                    self.coordinate_ref,
                    self.unit_ref,
                    self.availability_rule_ref,
                    self.calibration_ref,
                    self.uncertainty_rule_ref,
                    self.evidence_rule_ref,
                )
            )
            and _object_ref_tuple(self.measurement_epoch_refs)
        ):
            _formation_failure("MeasurementContract")

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


def validate_measurement(
    measurement: Measurement,
    contract: MeasurementContract,
    /,
) -> None:
    if type(measurement) is not Measurement:
        _formation_failure("Measurement")
    if type(contract) is not MeasurementContract:
        _formation_failure("MeasurementContract")
    interface = "validate_measurement"
    _object_content_check(measurement, interface, "argument 1 (measurement)")
    _object_content_check(contract, interface, "argument 2 (contract)")

    if measurement.raw_evidence_ref is Applicability.APPLICABLE:
        _failure(FailureCode.IMPLICIT_ABSENCE_FORBIDDEN, interface)
    if not _ordered_refs(contract.measurement_epoch_refs):
        _failure(FailureCode.I3_COLLECTION_ORDER_INVALID, interface)
    if _duplicate_refs(contract.measurement_epoch_refs):
        _failure(FailureCode.I3_DUPLICATE_MEMBER, interface)
    if (
        measurement.availability_epoch.clock_ref
        == measurement.measurement_epoch.clock_ref
        and measurement.availability_epoch.index.value
        < measurement.measurement_epoch.index.value
    ):
        _failure(FailureCode.EPOCH_MISMATCH, interface)
    if (
        type(measurement.value) is Quantity
        and measurement.value.unit_ref != contract.unit_ref
    ):
        _failure(FailureCode.CONSERVATION_UNIT_MISMATCH, interface)
    if not (
        measurement.measured_object_ref == contract.measured_object_ref
        and measurement.coordinate_ref == contract.coordinate_ref
        and measurement.calibration_ref == contract.calibration_ref
    ):
        _failure(FailureCode.MEASUREMENT_CONTRACT_MISMATCH, interface)
    if not _object_hash_matches(measurement) or not _object_hash_matches(contract):
        _failure(FailureCode.HASH_MISMATCH, interface)
    return None


_DEPENDENCY_SENTINEL = SystemState


__all__ = (
    "Measurement",
    "MeasurementContract",
    "validate_measurement",
)
