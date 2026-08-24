"""Immutable Framework I-5 physical-update ownership declarations."""

from __future__ import annotations

from dataclasses import dataclass
from enum import EnumType, StrEnum
from typing import Literal, NoReturn

from .events import EventKey, PhaseOrdinal, _event_key_projection
from . import state as _state
from .identity import ObjectRef
from .hashing import (
    OwnershipDigest,
    compute_event_key_digest,
    compute_ownership_digest,
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
    return FailureInterfaceRef("ebu_framework.ownership", name, "1.0.0")


def _failure(code: FailureCode, interface: str) -> NoReturn:
    _fail(
        code,
        f"{interface} rejected {code.value}",
        stage=FailureStage.I5,
        interface_ref=_interface(interface),
        scientific_status_effect=ScientificStatusEffect.UNSTARTED_PRESERVED,
        retry_class=RetryClass.FORBIDDEN,
    )


def _formation_failure(interface: str) -> NoReturn:
    _failure(FailureCode.I5_RECORD_FORMATION_INVALID, interface)


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


class _I5EnumType(EnumType):
    def __call__(cls, *args: object, **kwargs: object):
        if len(args) != 1 or kwargs or type(args[0]) is not str:
            _formation_failure(cls.__name__)
        try:
            return super().__call__(*args)
        except (TypeError, ValueError):
            _formation_failure(cls.__name__)


class OwnershipKind(StrEnum, metaclass=_I5EnumType):
    PHYSICAL_UPDATE = "PHYSICAL_UPDATE"
    INFORMATIONAL_POLICY_MEMORY = "INFORMATIONAL_POLICY_MEMORY"


@_strict_formation
@dataclass(frozen=True, slots=True, order=True, kw_only=True)
class OpaqueLocusKey:
    namespace: str
    coordinate: bytes


@_strict_formation
@dataclass(frozen=True, slots=True, order=True, kw_only=True)
class UpdateOwnershipClaim:
    epoch: int
    phase_ordinal: PhaseOrdinal
    event_key: EventKey
    owner_ref: ObjectRef
    locus: OpaqueLocusKey
    ownership_kind: OwnershipKind


@_strict_formation
@dataclass(frozen=True, slots=True, order=True, kw_only=True)
class OwnershipConflict:
    locus: OpaqueLocusKey
    first_claim: UpdateOwnershipClaim
    second_claim: UpdateOwnershipClaim


@_strict_formation
@dataclass(frozen=True, slots=True, order=True, kw_only=True)
class EpochUpdateOwnership:
    epoch: int
    claims: tuple[UpdateOwnershipClaim, ...]
    digest: OwnershipDigest


@_strict_formation
@dataclass(frozen=True, slots=True, order=True, kw_only=True)
class OwnershipValidationRecord:
    status: Literal["DISJOINT", "CONFLICT"]
    ownership: EpochUpdateOwnership | Applicability
    conflict: OwnershipConflict | Applicability


def _visible_ascii(value: object) -> bool:
    return (
        type(value) is str
        and bool(value)
        and value.isascii()
        and all(0x21 <= ord(character) <= 0x7E for character in value)
    )


def _object_ref_key(reference: ObjectRef) -> tuple[str, str, str]:
    return (
        str(reference.object_id),
        str(reference.object_version),
        str(reference.object_content_hash),
    )


def _claim_order_key(
    claim: UpdateOwnershipClaim, /
) -> tuple[object, ...]:
    return (
        claim.locus.namespace,
        claim.locus.coordinate,
        *_event_key_projection(claim.event_key),
        *_object_ref_key(claim.owner_ref),
    )


def _claim_formation_is_valid(claim: object) -> bool:
    return (
        type(claim) is UpdateOwnershipClaim
        and type(claim.epoch) is int
        and type(claim.phase_ordinal) is PhaseOrdinal
        and type(claim.event_key) is EventKey
        and type(claim.owner_ref) is ObjectRef
        and type(claim.locus) is OpaqueLocusKey
        and type(claim.ownership_kind) is OwnershipKind
    )


def _claim_is_valid(claim: UpdateOwnershipClaim) -> bool:
    return (
        claim.epoch >= 0
        and _visible_ascii(claim.locus.namespace)
        and type(claim.locus.coordinate) is bytes
        and bool(claim.locus.coordinate)
        and str(claim.owner_ref.object_id) == claim.event_key.primary_object_id
    )


def _claim_projection(claim: UpdateOwnershipClaim) -> list[str]:
    event_key_digest = compute_event_key_digest(
        epoch=claim.event_key.epoch,
        phase_ordinal=claim.event_key.phase_ordinal.value,
        declared_priority=claim.event_key.declared_priority,
        group_or_scope_id=claim.event_key.group_or_scope_id,
        event_kind=claim.event_key.event_kind,
        primary_object_id=claim.event_key.primary_object_id,
        local_sequence=claim.event_key.local_sequence,
    )
    return [
        str(claim.epoch),
        str(claim.phase_ordinal.value),
        str(event_key_digest),
        str(claim.owner_ref.object_id),
        claim.locus.namespace,
        claim.locus.coordinate.hex(),
        claim.ownership_kind.value,
    ]


def _epoch_digest(
    epoch: int, claims: tuple[UpdateOwnershipClaim, ...]
) -> OwnershipDigest:
    claim_digests = tuple(
        compute_ownership_digest("CLAIM", _claim_projection(claim))
        for claim in claims
    )
    return compute_ownership_digest(
        "EPOCH",
        [
            str(epoch),
            str(len(claim_digests)),
            ",".join(str(item) for item in claim_digests),
        ],
    )


def _validate_claims(
    claims: object,
    *,
    interface: str,
    expected_epoch: int | None,
) -> tuple[UpdateOwnershipClaim, ...]:
    if type(claims) is not tuple or not all(
        _claim_formation_is_valid(item) for item in claims
    ):
        _formation_failure(interface)
    if any(not _claim_is_valid(item) for item in claims):
        _failure(FailureCode.UPDATE_OWNERSHIP_CLAIM_INVALID, interface)
    if any(
        item.ownership_kind is OwnershipKind.INFORMATIONAL_POLICY_MEMORY
        for item in claims
    ):
        _failure(
            FailureCode.INFORMATIONAL_MEMORY_OWNERSHIP_FORBIDDEN,
            interface,
        )
    keys = tuple(_claim_order_key(item) for item in claims)
    if keys != tuple(sorted(keys)) or len(keys) != len(set(keys)):
        _failure(FailureCode.OWNERSHIP_ORDER_INVALID, interface)
    epochs = {item.epoch for item in claims}
    if (
        len(epochs) > 1
        or (
            expected_epoch is not None
            and any(item.epoch != expected_epoch for item in claims)
        )
        or any(
            item.epoch != item.event_key.epoch
            or item.phase_ordinal is not item.event_key.phase_ordinal
            for item in claims
        )
    ):
        _failure(FailureCode.PHASE_OWNERSHIP_MISMATCH, interface)
    for first, second in zip(claims, claims[1:]):
        if first.locus == second.locus:
            _failure(FailureCode.UPDATE_OWNERSHIP_CONFLICT, interface)
    return claims


def build_epoch_update_ownership(
    epoch: int,
    claims: tuple[UpdateOwnershipClaim, ...],
    /,
) -> EpochUpdateOwnership:
    interface = "build_epoch_update_ownership"
    if type(epoch) is not int or epoch < 0:
        _formation_failure(interface)
    checked = _validate_claims(
        claims, interface=interface, expected_epoch=epoch
    )
    return EpochUpdateOwnership(
        epoch=epoch,
        claims=checked,
        digest=_epoch_digest(epoch, checked),
    )


def validate_update_ownership(
    claims: tuple[UpdateOwnershipClaim, ...], /
) -> OwnershipValidationRecord:
    interface = "validate_update_ownership"
    checked = _validate_claims(
        claims, interface=interface, expected_epoch=None
    )
    epoch = checked[0].epoch if checked else 0
    ownership = EpochUpdateOwnership(
        epoch=epoch,
        claims=checked,
        digest=_epoch_digest(epoch, checked),
    )
    return OwnershipValidationRecord(
        status="DISJOINT",
        ownership=ownership,
        conflict=Applicability.NOT_APPLICABLE,
    )


__all__ = (
    "OwnershipKind",
    "OpaqueLocusKey",
    "UpdateOwnershipClaim",
    "OwnershipConflict",
    "EpochUpdateOwnership",
    "OwnershipValidationRecord",
    "build_epoch_update_ownership",
    "validate_update_ownership",
)
