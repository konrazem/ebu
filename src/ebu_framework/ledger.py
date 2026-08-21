"""Immutable I-3 ledger declarations and local chain validation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import NoReturn

from .primitives import IntegerV1
from .identity import ObjectRef, ScientificId
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
    return FailureInterfaceRef("ebu_framework.ledger", name, "1.0.0")


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


class LedgerKind(StrEnum):
    OPERATIONAL = "OPERATIONAL"
    SCIENTIFIC_EVIDENCE = "SCIENTIFIC_EVIDENCE"

    @classmethod
    def _missing_(cls, value: object) -> NoReturn:
        _formation_failure("LedgerKind")


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class Ledger:
    envelope: CommonObjectEnvelope
    ledger_kind: LedgerKind
    entry_refs: tuple[ObjectRef, ...]
    head_entry_ref: ObjectRef | Applicability

    def __post_init__(self) -> None:
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and type(self.ledger_kind) is LedgerKind
            and _object_ref_tuple(self.entry_refs)
            and _object_or_applicability(self.head_entry_ref)
        ):
            _formation_failure("Ledger")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class LedgerEntry:
    envelope: CommonObjectEnvelope
    ledger_id: ScientificId
    predecessor_entry_ref: ObjectRef | Applicability
    entry_ordinal: IntegerV1
    payload_ref: ObjectRef
    evidence_refs: tuple[ObjectRef, ...]

    def __post_init__(self) -> None:
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and type(self.ledger_id) is ScientificId
            and _object_or_applicability(self.predecessor_entry_ref)
            and type(self.entry_ordinal) is IntegerV1
            and type(self.payload_ref) is ObjectRef
            and _object_ref_tuple(self.evidence_refs)
        ):
            _formation_failure("LedgerEntry")

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


def validate_ledger(ledger: Ledger, entries: tuple[LedgerEntry, ...], /) -> None:
    if type(ledger) is not Ledger:
        _formation_failure("Ledger")
    if not (
        type(entries) is tuple
        and all(type(entry) is LedgerEntry for entry in entries)
    ):
        _formation_failure("LedgerEntry")
    interface = "validate_ledger"
    _object_content_check(ledger, interface, "argument 1 (ledger)")
    for index, entry in enumerate(entries):
        _object_content_check(
            entry,
            interface,
            f"argument 2 (entries), member {index}",
        )

    applicability_values = (ledger.head_entry_ref,) + tuple(
        entry.predecessor_entry_ref for entry in entries
    )
    if any(value is Applicability.APPLICABLE for value in applicability_values):
        _failure(FailureCode.IMPLICIT_ABSENCE_FORBIDDEN, interface)

    entry_refs = tuple(_envelope_ref(entry) for entry in entries)
    ordinals = tuple(entry.entry_ordinal.value for entry in entries)
    same_entry_ref_members = set(ledger.entry_refs) == set(entry_refs)
    if (
        (same_entry_ref_members and ledger.entry_refs != entry_refs)
        or ordinals != tuple(sorted(ordinals))
        or any(not _ordered_refs(entry.evidence_refs) for entry in entries)
    ):
        _failure(FailureCode.I3_COLLECTION_ORDER_INVALID, interface)
    if (
        _duplicate_refs(ledger.entry_refs)
        or any(_duplicate_refs(entry.evidence_refs) for entry in entries)
        or any(
            left == right
            for index, left in enumerate(entries)
            for right in entries[index + 1 :]
        )
    ):
        _failure(FailureCode.I3_DUPLICATE_MEMBER, interface)

    link_invalid = (
        any(entry.ledger_id != ledger.envelope.object_id for entry in entries)
        or ordinals != tuple(range(len(entries)))
        or ledger.entry_refs != entry_refs
    )
    for index, entry in enumerate(entries):
        expected_predecessor: ObjectRef | Applicability = (
            Applicability.NOT_APPLICABLE
            if index == 0
            else entry_refs[index - 1]
        )
        if entry.predecessor_entry_ref != expected_predecessor:
            link_invalid = True
    expected_head: ObjectRef | Applicability = (
        Applicability.NOT_APPLICABLE if not entries else entry_refs[-1]
    )
    if ledger.head_entry_ref != expected_head:
        link_invalid = True
    if link_invalid:
        _failure(FailureCode.LEDGER_LINK_INVALID, interface)

    if not _object_hash_matches(ledger) or any(
        not _object_hash_matches(entry) for entry in entries
    ):
        _failure(FailureCode.HASH_MISMATCH, interface)
    return None


def _validate_operational_append(ledger: Ledger, entry: LedgerEntry, /) -> None:
    if type(ledger) is not Ledger or type(entry) is not LedgerEntry:
        _formation_failure("_validate_operational_append")
    if ledger.ledger_kind is not LedgerKind.OPERATIONAL:
        _failure(FailureCode.LEDGER_LINK_INVALID, "_validate_operational_append")
    entry_ref = _envelope_ref(entry)
    if not (
        entry.ledger_id == ledger.envelope.object_id
        and entry.entry_ordinal.value == len(ledger.entry_refs) - 1
        and bool(ledger.entry_refs)
        and ledger.entry_refs[-1] == entry_ref
        and ledger.head_entry_ref == entry_ref
        and (
            (entry.entry_ordinal.value == 0 and entry.predecessor_entry_ref is Applicability.NOT_APPLICABLE)
            or (
                entry.entry_ordinal.value > 0
                and entry.predecessor_entry_ref == ledger.entry_refs[-2]
            )
        )
    ):
        _failure(FailureCode.LEDGER_LINK_INVALID, "_validate_operational_append")
    if not _object_hash_matches(ledger) or not _object_hash_matches(entry):
        _failure(FailureCode.HASH_MISMATCH, "_validate_operational_append")


__all__ = (
    "Ledger",
    "LedgerEntry",
    "LedgerKind",
    "validate_ledger",
)
