"""Immutable Framework I-5 event declarations and inert validation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import EnumType, IntEnum, StrEnum
from typing import NoReturn

from . import actions as _actions
from . import faults as _faults
from . import primitives as _primitives
from .identity import ObjectRef, _Digest as Sha256Digest
from .hashing import (
    CanonicalScientificTracePayloadHash,
    CanonicalTracePrefixHash,
    CanonicalTraceRowHash,
    EventDeclarationDigest,
    EventKeyDigest,
    OwnershipDigest,
    PhaseCommitDigest,
    TraceDigest,
    compute_event_key_digest,
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
    return FailureInterfaceRef("ebu_framework.events", name, "1.0.0")


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
        expected_type = int if issubclass(cls, IntEnum) else str
        if (
            len(args) != 1
            or kwargs
            or type(args[0]) is not expected_type
        ):
            _formation_failure(cls.__name__)
        try:
            return super().__call__(*args)
        except (TypeError, ValueError):
            _formation_failure(cls.__name__)


class PhaseOrdinal(IntEnum, metaclass=_I5EnumType):
    PHASE_1 = 1
    PHASE_2 = 2
    PHASE_3 = 3
    PHASE_4 = 4
    PHASE_5 = 5
    PHASE_6 = 6
    PHASE_7 = 7
    PHASE_8 = 8
    PHASE_9 = 9
    PHASE_10 = 10


@_strict_formation
@dataclass(frozen=True, slots=True, order=True, kw_only=True)
class EventKey:
    epoch: int
    phase_ordinal: PhaseOrdinal
    declared_priority: int
    group_or_scope_id: str
    event_kind: str
    primary_object_id: str
    local_sequence: int


@_strict_formation
@dataclass(frozen=True, slots=True, order=True, kw_only=True)
class EventDeclaration:
    key: EventKey
    event_ref: ObjectRef
    declared_simultaneity_ref: ObjectRef | Applicability
    payload_hash: Sha256Digest
    predecessor_event_key: EventKey | Applicability


@_strict_formation
@dataclass(frozen=True, slots=True, order=True, kw_only=True)
class PhaseCommitRecord:
    epoch: int
    phase_ordinal: PhaseOrdinal
    previous_phase_commit_digest: PhaseCommitDigest | Applicability
    ordered_event_digests: tuple[EventDeclarationDigest, ...]
    epoch_ownership_digest: OwnershipDigest
    physical_phase_record_ref: ObjectRef | Applicability
    trace_row_digest: TraceDigest


class TraceCompleteness(StrEnum, metaclass=_I5EnumType):
    COMPLETE = "COMPLETE"
    DECLARED_FAULT_TERMINAL = "DECLARED_FAULT_TERMINAL"
    PARTIAL_DURABLE_PREFIX = "PARTIAL_DURABLE_PREFIX"
    NO_DURABLE_TRACE = "NO_DURABLE_TRACE"
    UNRESOLVED_DURABILITY = "UNRESOLVED_DURABILITY"
    INVALID = "INVALID"


def _visible_ascii(value: object) -> bool:
    return (
        type(value) is str
        and bool(value)
        and value.isascii()
        and all(0x21 <= ord(character) <= 0x7E for character in value)
    )


def _scientific_id_text(value: object) -> bool:
    if type(value) is not str:
        return False
    fields = value.split(":")
    if len(fields) != 4 or fields[0] != "ebu":
        return False
    alphabet = frozenset("abcdefghijklmnopqrstuvwxyz0123456789._-")
    return all(
        bool(field)
        and field[0] in "abcdefghijklmnopqrstuvwxyz0123456789"
        and all(character in alphabet for character in field)
        for field in fields[1:]
    )


def _trace_digest(value: object) -> bool:
    return type(value) in {
        CanonicalTraceRowHash,
        CanonicalTracePrefixHash,
        CanonicalScientificTracePayloadHash,
    }


def _event_key_projection(key: EventKey, /) -> tuple[object, ...]:
    return (
        key.epoch,
        key.phase_ordinal.value
        if type(key.phase_ordinal) is PhaseOrdinal
        else key.phase_ordinal,
        key.declared_priority,
        key.group_or_scope_id,
        key.event_kind,
        key.primary_object_id,
        key.local_sequence,
    )


def _key_is_valid(key: object) -> bool:
    return (
        type(key) is EventKey
        and type(key.epoch) is int
        and key.epoch >= 0
        and type(key.phase_ordinal) is PhaseOrdinal
        and type(key.declared_priority) is int
        and _visible_ascii(key.group_or_scope_id)
        and _visible_ascii(key.event_kind)
        and _scientific_id_text(key.primary_object_id)
        and type(key.local_sequence) is int
        and key.local_sequence >= 0
    )


def _declaration_formation_is_valid(declaration: object) -> bool:
    if type(declaration) is not EventDeclaration:
        return False
    return (
        type(declaration.key) is EventKey
        and type(declaration.event_ref) is ObjectRef
        and (
            type(declaration.declared_simultaneity_ref) is ObjectRef
            or declaration.declared_simultaneity_ref
            is Applicability.NOT_APPLICABLE
        )
        and isinstance(declaration.payload_hash, Sha256Digest)
        and (
            type(declaration.predecessor_event_key) is EventKey
            or declaration.predecessor_event_key
            is Applicability.NOT_APPLICABLE
        )
    )


def validate_event_declaration(declaration: EventDeclaration, /) -> None:
    interface = "validate_event_declaration"
    if not _declaration_formation_is_valid(declaration):
        _formation_failure(interface)
    if type(declaration.key.phase_ordinal) is not PhaseOrdinal:
        _failure(FailureCode.PHASE_ORDINAL_INVALID, interface)
    if not _key_is_valid(declaration.key):
        _failure(FailureCode.EVENT_KEY_INVALID, interface)
    if str(declaration.event_ref.object_id) != declaration.key.primary_object_id:
        _failure(FailureCode.EVENT_IDENTITY_INVALID, interface)
    return None


def _phase_identity_guard(
    declarations: tuple[EventDeclaration, ...], /
) -> None:
    phase_8_identifiers = {
        (declaration.key.epoch, declaration.key.primary_object_id)
        for declaration in declarations
        if declaration.key.phase_ordinal is PhaseOrdinal.PHASE_8
    }
    if any(
        declaration.key.phase_ordinal is PhaseOrdinal.PHASE_9
        and (declaration.key.epoch, declaration.key.primary_object_id)
        in phase_8_identifiers
        for declaration in declarations
    ):
        _failure(
            FailureCode.PHASE_8_PHASE_9_DUPLICATE_IDENTIFIER,
            "order_event_keys",
        )


def order_event_keys(
    declarations: tuple[EventDeclaration, ...], /
) -> tuple[EventDeclaration, ...]:
    interface = "order_event_keys"
    if type(declarations) is not tuple or not all(
        _declaration_formation_is_valid(item) for item in declarations
    ):
        _formation_failure(interface)
    if any(not _key_is_valid(item.key) for item in declarations):
        _failure(FailureCode.EVENT_KEY_INVALID, interface)
    keys = tuple(_event_key_projection(item.key) for item in declarations)
    if len(keys) != len(set(keys)):
        _failure(FailureCode.EVENT_KEY_DUPLICATE, interface)
    if keys != tuple(sorted(keys)):
        _failure(FailureCode.EVENT_ORDER_INVALID, interface)
    for index, declaration in enumerate(declarations):
        expected = (
            Applicability.NOT_APPLICABLE
            if index == 0
            else declarations[index - 1].key
        )
        if declaration.predecessor_event_key != expected:
            _failure(FailureCode.PHASE_PREDECESSOR_MISMATCH, interface)
    _phase_identity_guard(declarations)
    return declarations


def _phase_commit_formation_is_valid(record: object) -> bool:
    return (
        type(record) is PhaseCommitRecord
        and type(record.epoch) is int
        and type(record.phase_ordinal) is PhaseOrdinal
        and (
            type(record.previous_phase_commit_digest) is PhaseCommitDigest
            or record.previous_phase_commit_digest
            is Applicability.NOT_APPLICABLE
        )
        and type(record.ordered_event_digests) is tuple
        and all(
            type(item) is EventDeclarationDigest
            for item in record.ordered_event_digests
        )
        and type(record.epoch_ownership_digest) is OwnershipDigest
        and (
            type(record.physical_phase_record_ref) is ObjectRef
            or record.physical_phase_record_ref is Applicability.NOT_APPLICABLE
        )
        and _trace_digest(record.trace_row_digest)
    )


def validate_phase_commit_record(
    record: PhaseCommitRecord,
    expected_previous: PhaseCommitDigest | Applicability,
    /,
) -> None:
    interface = "validate_phase_commit_record"
    if not (
        _phase_commit_formation_is_valid(record)
        and (
            type(expected_previous) is PhaseCommitDigest
            or expected_previous is Applicability.NOT_APPLICABLE
        )
    ):
        _formation_failure(interface)
    phase_is_first = record.phase_ordinal is PhaseOrdinal.PHASE_1
    physical_is_applicable = type(record.physical_phase_record_ref) is ObjectRef
    if (
        record.epoch < 0
        or (
            phase_is_first
            and type(record.previous_phase_commit_digest) is PhaseCommitDigest
        )
        or (
            not phase_is_first
            and record.previous_phase_commit_digest
            is Applicability.NOT_APPLICABLE
        )
        or (
            record.phase_ordinal is PhaseOrdinal.PHASE_8
            and not physical_is_applicable
        )
        or (
            record.phase_ordinal is not PhaseOrdinal.PHASE_8
            and physical_is_applicable
        )
    ):
        _failure(FailureCode.PHASE_COMMIT_RECORD_INVALID, interface)
    if record.previous_phase_commit_digest != expected_previous:
        _failure(FailureCode.PHASE_PREDECESSOR_MISMATCH, interface)
    if len(record.ordered_event_digests) != len(
        set(record.ordered_event_digests)
    ):
        _failure(FailureCode.EVENT_ORDER_INVALID, interface)
    return None


__all__ = (
    "PhaseOrdinal",
    "EventKey",
    "EventDeclaration",
    "PhaseCommitRecord",
    "TraceCompleteness",
    "order_event_keys",
    "validate_event_declaration",
    "validate_phase_commit_record",
)
