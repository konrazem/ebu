"""Immutable I-3 distortion declaration and its pure T0 validation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import NoReturn

from .state import ProjectionContract as _ProjectionContract
from .primitives import ClaimStatus
from .numeric import CoreNumberV1 as _CoreNumberV1
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
    return FailureInterfaceRef("ebu_framework.distortion", name, "1.0.0")


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


@_strict_formation
@dataclass(
    frozen=True,
    slots=True,
    eq=True,
    order=False,
    unsafe_hash=False,
    kw_only=True,
)
class DistortionModel:
    envelope: CommonObjectEnvelope
    domain_schema_ref: ObjectRef
    boundary_ref: ObjectRef
    parameter_refs: tuple[ObjectRef, ...]
    codomain_unit_ref: ObjectRef
    domain_predicate_ref: ObjectRef
    evaluation_contract_ref: ObjectRef
    numerical_policy_ref: ObjectRef
    scientific_status: ClaimStatus

    def __post_init__(self) -> None:
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and type(self.domain_schema_ref) is ObjectRef
            and type(self.boundary_ref) is ObjectRef
            and _object_ref_tuple(self.parameter_refs)
            and type(self.codomain_unit_ref) is ObjectRef
            and type(self.domain_predicate_ref) is ObjectRef
            and type(self.evaluation_contract_ref) is ObjectRef
            and type(self.numerical_policy_ref) is ObjectRef
            and type(self.scientific_status) is ClaimStatus
        ):
            _formation_failure("DistortionModel")

    def to_ecj1(self) -> dict[str, object]:
        return {
            "domain_schema_ref": self.domain_schema_ref.to_ecj1(),
            "boundary_ref": self.boundary_ref.to_ecj1(),
            "parameter_refs": [item.to_ecj1() for item in self.parameter_refs],
            "codomain_unit_ref": self.codomain_unit_ref.to_ecj1(),
            "domain_predicate_ref": self.domain_predicate_ref.to_ecj1(),
            "evaluation_contract_ref": self.evaluation_contract_ref.to_ecj1(),
            "numerical_policy_ref": self.numerical_policy_ref.to_ecj1(),
            "scientific_status": self.scientific_status.value,
        }


def _failure_object(model: DistortionModel) -> FailureObjectRef:
    envelope = model.envelope
    return FailureObjectRef(
        object_id=str(envelope.object_id),
        object_version=str(envelope.object_version),
        object_content_hash=str(envelope.object_content_hash),
    )


def _object_content_check(model: DistortionModel) -> None:
    stored = model.envelope.to_ecj1()["object_content_payload"]
    if stored != model.to_ecj1():
        interface = "validate_distortion_model"
        _failure(
            FailureCode.I3_OBJECT_CONTENT_MISMATCH,
            interface,
            summary=(
                f"{interface} rejected I3_OBJECT_CONTENT_MISMATCH "
                "at argument 1 (model)"
            ),
            object_ref=_failure_object(model),
        )


def _object_hash_matches(model: DistortionModel) -> bool:
    try:
        validate_object_envelope(model.envelope)
    except FrameworkError:
        return False
    return True


def validate_distortion_model(model: DistortionModel, /) -> None:
    if type(model) is not DistortionModel:
        _formation_failure("DistortionModel")
    _object_content_check(model)

    keys = tuple(_ref_key(item) for item in model.parameter_refs)
    if keys != tuple(sorted(keys)):
        _failure(
            FailureCode.I3_COLLECTION_ORDER_INVALID,
            "validate_distortion_model",
        )
    if len(keys) != len(set(keys)):
        _failure(FailureCode.I3_DUPLICATE_MEMBER, "validate_distortion_model")

    if (
        not model.parameter_refs
        or model.domain_predicate_ref == model.evaluation_contract_ref
    ):
        _failure(
            FailureCode.DISTORTION_DECLARATION_INVALID,
            "validate_distortion_model",
        )

    if not _object_hash_matches(model):
        _failure(FailureCode.HASH_MISMATCH, "validate_distortion_model")
    return None


__all__ = (
    "DistortionModel",
    "validate_distortion_model",
)
