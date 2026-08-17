"""Immutable I-3 causal declarations and local consistency checks."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import NoReturn

from .primitives import Quantity, ResolutionDetail
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
    return FailureInterfaceRef("ebu_framework.causal", name, "1.0.0")


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


class CausalIdentificationStatus(StrEnum):
    IDENTIFIED = "IDENTIFIED"
    PARTIALLY_IDENTIFIED = "PARTIALLY_IDENTIFIED"
    UNIDENTIFIED = "UNIDENTIFIED"

    @classmethod
    def _missing_(cls, value: object) -> NoReturn:
        _formation_failure("CausalIdentificationStatus")


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class CausalRemainder:
    envelope: CommonObjectEnvelope
    result_ref: ObjectRef
    causal_model_ref: ObjectRef
    identification_status: CausalIdentificationStatus
    represented_total: Quantity
    identified_total: Quantity | ResolutionDetail
    remainder: Quantity | ResolutionDetail
    evidence_refs: tuple[ObjectRef, ...]
    nonclaim_refs: tuple[ObjectRef, ...]

    def __post_init__(self) -> None:
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and type(self.result_ref) is ObjectRef
            and type(self.causal_model_ref) is ObjectRef
            and type(self.identification_status) is CausalIdentificationStatus
            and type(self.represented_total) is Quantity
            and type(self.identified_total) in (Quantity, ResolutionDetail)
            and type(self.remainder) in (Quantity, ResolutionDetail)
            and _object_ref_tuple(self.evidence_refs)
            and _object_ref_tuple(self.nonclaim_refs)
        ):
            _formation_failure("CausalRemainder")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


def _failure_object(record: CausalRemainder) -> FailureObjectRef:
    return FailureObjectRef(
        object_id=str(record.envelope.object_id),
        object_version=str(record.envelope.object_version),
        object_content_hash=str(record.envelope.object_content_hash),
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


def _quantity_units_match(left: Quantity, right: Quantity) -> bool:
    return left.unit_ref == right.unit_ref and left.dimension_ref == right.dimension_ref


def _object_hash_matches(record: CausalRemainder) -> bool:
    try:
        validate_object_envelope(record.envelope)
    except FrameworkError:
        return False
    return True


def validate_causal_remainder(record: CausalRemainder, /) -> None:
    if type(record) is not CausalRemainder:
        _formation_failure("CausalRemainder")
    interface = "validate_causal_remainder"
    if record.envelope.to_ecj1()["object_content_payload"] != record.to_ecj1():
        _failure(
            FailureCode.I3_OBJECT_CONTENT_MISMATCH,
            interface,
            summary=(
                f"{interface} rejected I3_OBJECT_CONTENT_MISMATCH "
                "at argument 1 (record)"
            ),
            object_ref=_failure_object(record),
        )

    collections = (record.evidence_refs, record.nonclaim_refs)
    if any(not _ordered_refs(values) for values in collections):
        _failure(FailureCode.I3_COLLECTION_ORDER_INVALID, interface)
    if any(_duplicate_refs(values) for values in collections):
        _failure(FailureCode.I3_DUPLICATE_MEMBER, interface)

    quantities = (record.identified_total, record.remainder)
    if any(
        type(quantity) is Quantity
        and not _quantity_units_match(record.represented_total, quantity)
        for quantity in quantities
    ):
        _failure(FailureCode.CONSERVATION_UNIT_MISMATCH, interface)
    if (
        record.identification_status is not CausalIdentificationStatus.IDENTIFIED
        and any(type(quantity) is Quantity for quantity in quantities)
    ):
        _failure(FailureCode.CAUSAL_ATTRIBUTION_UNRESOLVED, interface)
    if not _object_hash_matches(record):
        _failure(FailureCode.HASH_MISMATCH, interface)
    return None


__all__ = (
    "CausalIdentificationStatus",
    "CausalRemainder",
    "validate_causal_remainder",
)
