"""Immutable I-3 information and policy-memory declarations."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import NoReturn

from .observation import Measurement
from .scheduling import Schedule
from .primitives import Duration, Epoch, ResolutionDetail
from .identity import InformationViewHash, ObjectRef, PolicyMemoryPayloadHash
from .envelopes import (
    CanonicalBytes,
    CommonObjectEnvelope,
    parse_ecj1,
    validate_object_envelope,
)
from .hashing import (
    compute_information_view_hash,
    compute_policy_memory_payload_hash,
)
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
    return FailureInterfaceRef("ebu_framework.policy", name, "1.0.0")


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


def _canonical_bytes(value: object) -> bool:
    if type(value) is not bytes:
        return False
    try:
        parse_ecj1(value)
    except FrameworkError:
        return False
    return True


def _object_ref_tuple(value: object) -> bool:
    return type(value) is tuple and all(type(item) is ObjectRef for item in value)


def _duration_pair_tuple(value: object) -> bool:
    return (
        type(value) is tuple
        and all(
            type(pair) is tuple
            and len(pair) == 2
            and type(pair[0]) is ObjectRef
            and type(pair[1]) is Duration
            for pair in value
        )
    )


def _canonical_pair_tuple(value: object) -> bool:
    return (
        type(value) is tuple
        and all(
            type(pair) is tuple
            and len(pair) == 2
            and type(pair[0]) is ObjectRef
            and _canonical_bytes(pair[1])
            for pair in value
        )
    )


def _object_or_applicability(value: object) -> bool:
    return type(value) is ObjectRef or type(value) is Applicability


def _project(value: object) -> object:
    if type(value) is bytes:
        return parse_ecj1(value)
    if type(value) is PolicyMemoryPayloadHash:
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


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class InformationContract:
    envelope: CommonObjectEnvelope
    visible_field_refs: tuple[ObjectRef, ...]
    max_age_rules: tuple[tuple[ObjectRef, Duration], ...]
    privacy_restriction_refs: tuple[ObjectRef, ...]
    availability_rule_refs: tuple[ObjectRef, ...]

    def __post_init__(self) -> None:
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and _object_ref_tuple(self.visible_field_refs)
            and _duration_pair_tuple(self.max_age_rules)
            and _object_ref_tuple(self.privacy_restriction_refs)
            and _object_ref_tuple(self.availability_rule_refs)
        ):
            _formation_failure("InformationContract")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class InformationView:
    envelope: CommonObjectEnvelope
    policy_ref: ObjectRef
    information_contract_ref: ObjectRef
    decision_epoch: Epoch
    current_policy_memory_payload_hash: PolicyMemoryPayloadHash | Applicability
    visible_field_records: tuple[tuple[ObjectRef, CanonicalBytes], ...]
    visible_object_refs: tuple[ObjectRef, ...]
    information_view_hash: InformationViewHash

    def __post_init__(self) -> None:
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and type(self.policy_ref) is ObjectRef
            and type(self.information_contract_ref) is ObjectRef
            and type(self.decision_epoch) is Epoch
            and (
                type(self.current_policy_memory_payload_hash)
                is PolicyMemoryPayloadHash
                or type(self.current_policy_memory_payload_hash) is Applicability
            )
            and _canonical_pair_tuple(self.visible_field_records)
            and _object_ref_tuple(self.visible_object_refs)
            and type(self.information_view_hash) is InformationViewHash
        ):
            _formation_failure("InformationView")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field not in {"envelope", "information_view_hash"}
        }


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class InformationReadSet:
    envelope: CommonObjectEnvelope
    information_view_ref: ObjectRef
    read_field_refs: tuple[ObjectRef, ...]
    read_object_refs: tuple[ObjectRef, ...]

    def __post_init__(self) -> None:
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and type(self.information_view_ref) is ObjectRef
            and _object_ref_tuple(self.read_field_refs)
            and _object_ref_tuple(self.read_object_refs)
        ):
            _formation_failure("InformationReadSet")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class PolicyMemoryState:
    envelope: CommonObjectEnvelope
    policy_ref: ObjectRef
    memory_schema_ref: ObjectRef
    available_for_decision_epoch: Epoch
    memory_payload: CanonicalBytes
    resolution: ResolutionDetail
    predecessor_memory_ref: ObjectRef | Applicability
    originating_decision_ref: ObjectRef | Applicability
    policy_memory_payload_hash: PolicyMemoryPayloadHash

    def __post_init__(self) -> None:
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and type(self.policy_ref) is ObjectRef
            and type(self.memory_schema_ref) is ObjectRef
            and type(self.available_for_decision_epoch) is Epoch
            and _canonical_bytes(self.memory_payload)
            and type(self.resolution) is ResolutionDetail
            and _object_or_applicability(self.predecessor_memory_ref)
            and _object_or_applicability(self.originating_decision_ref)
            and type(self.policy_memory_payload_hash) is PolicyMemoryPayloadHash
        ):
            _formation_failure("PolicyMemoryState")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field not in {"envelope", "policy_memory_payload_hash"}
        }


class MemoryMode(StrEnum):
    STATELESS = "STATELESS"
    STATEFUL = "STATEFUL"

    @classmethod
    def _missing_(cls, value: object) -> NoReturn:
        _formation_failure("MemoryMode")


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


def _ordered_pairs(values: tuple[tuple[ObjectRef, object], ...]) -> bool:
    keys = tuple(_ref_key(reference) for reference, _ in values)
    return keys == tuple(sorted(keys))


def _duplicate_pairs(values: tuple[tuple[ObjectRef, object], ...]) -> bool:
    first_keys = tuple(_ref_key(reference) for reference, _ in values)
    return len(first_keys) != len(set(first_keys)) or any(
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
    try:
        validate_object_envelope(record.envelope)  # type: ignore[attr-defined]
    except FrameworkError:
        return False
    return True


def _information_view_hash_matches(view: InformationView) -> bool:
    memory = view.current_policy_memory_payload_hash
    memory_input: PolicyMemoryPayloadHash | str
    if type(memory) is PolicyMemoryPayloadHash:
        memory_input = memory
    else:
        memory_input = memory.value
    visible_fields = tuple(
        [reference.to_ecj1(), parse_ecj1(payload)]
        for reference, payload in view.visible_field_records
    )
    recomputed = compute_information_view_hash(
        policy_ref=view.policy_ref,
        information_contract_ref=view.information_contract_ref,
        decision_epoch=view.decision_epoch.to_ecj1(),
        current_policy_memory_payload_hash_or_not_applicable=memory_input,
        ordered_visible_field_records=visible_fields,
        ordered_visible_object_refs=view.visible_object_refs,
    )
    return recomputed == view.information_view_hash


def _policy_memory_hash_matches(record: PolicyMemoryState) -> bool:
    recomputed = compute_policy_memory_payload_hash(
        policy_ref=record.policy_ref,
        memory_schema_ref=record.memory_schema_ref,
        available_for_decision_epoch=record.available_for_decision_epoch.to_ecj1(),
        resolution_state=record.resolution.state.value,
        memory_payload=parse_ecj1(record.memory_payload),
    )
    return recomputed == record.policy_memory_payload_hash


def validate_information_view(
    contract: InformationContract,
    view: InformationView,
    read_set: InformationReadSet | Applicability,
    /,
) -> None:
    if type(contract) is not InformationContract:
        _formation_failure("InformationContract")
    if type(view) is not InformationView:
        _formation_failure("InformationView")
    if type(read_set) not in (InformationReadSet, Applicability):
        _formation_failure("InformationReadSet")
    interface = "validate_information_view"
    _object_content_check(contract, interface, "argument 1 (contract)")
    _object_content_check(view, interface, "argument 2 (view)")
    if type(read_set) is InformationReadSet:
        _object_content_check(read_set, interface, "argument 3 (read_set)")

    if (
        view.current_policy_memory_payload_hash is Applicability.APPLICABLE
        or read_set is Applicability.APPLICABLE
    ):
        _failure(FailureCode.IMPLICIT_ABSENCE_FORBIDDEN, interface)

    ref_collections = (
        contract.visible_field_refs,
        contract.privacy_restriction_refs,
        contract.availability_rule_refs,
        view.visible_object_refs,
    )
    pair_collections: tuple[tuple[tuple[ObjectRef, object], ...], ...] = (
        contract.max_age_rules,
        view.visible_field_records,
    )
    if type(read_set) is InformationReadSet:
        ref_collections += (read_set.read_field_refs, read_set.read_object_refs)
    if any(not _ordered_refs(values) for values in ref_collections) or any(
        not _ordered_pairs(values) for values in pair_collections
    ):
        _failure(FailureCode.I3_COLLECTION_ORDER_INVALID, interface)
    if any(_duplicate_refs(values) for values in ref_collections) or any(
        _duplicate_pairs(values) for values in pair_collections
    ):
        _failure(FailureCode.I3_DUPLICATE_MEMBER, interface)

    visible_field_refs = tuple(
        reference for reference, _ in view.visible_field_records
    )
    declaration_invalid = (
        view.information_contract_ref != _envelope_ref(contract)
        or any(
            reference not in contract.visible_field_refs
            for reference in visible_field_refs
        )
    )
    if type(read_set) is InformationReadSet:
        declaration_invalid = declaration_invalid or (
            read_set.information_view_ref != _envelope_ref(view)
            or any(
                reference not in visible_field_refs
                for reference in read_set.read_field_refs
            )
            or any(
                reference not in view.visible_object_refs
                for reference in read_set.read_object_refs
            )
        )
    if declaration_invalid:
        _failure(FailureCode.INFORMATION_VIEW_DECLARATION_INVALID, interface)

    records = (contract, view) + (
        (read_set,) if type(read_set) is InformationReadSet else ()
    )
    if (
        any(not _object_hash_matches(record) for record in records)
        or not _information_view_hash_matches(view)
    ):
        _failure(FailureCode.HASH_MISMATCH, interface)
    return None


def validate_policy_memory_state(
    record: PolicyMemoryState,
    mode: MemoryMode,
    predecessor_epoch: Epoch | Applicability,
    /,
) -> None:
    if type(record) is not PolicyMemoryState:
        _formation_failure("PolicyMemoryState")
    if type(mode) is not MemoryMode:
        _formation_failure("MemoryMode")
    if type(predecessor_epoch) not in (Epoch, Applicability):
        _formation_failure("Epoch")
    interface = "validate_policy_memory_state"
    _object_content_check(record, interface, "argument 1 (record)")

    if (
        record.predecessor_memory_ref is Applicability.APPLICABLE
        or record.originating_decision_ref is Applicability.APPLICABLE
        or predecessor_epoch is Applicability.APPLICABLE
    ):
        _failure(FailureCode.IMPLICIT_ABSENCE_FORBIDDEN, interface)
    if mode is MemoryMode.STATELESS:
        _failure(FailureCode.POLICY_MEMORY_NOT_APPLICABLE, interface)

    has_predecessor = type(record.predecessor_memory_ref) is ObjectRef
    has_decision = type(record.originating_decision_ref) is ObjectRef
    has_epoch = type(predecessor_epoch) is Epoch
    epoch_matches = (
        has_epoch
        and predecessor_epoch.clock_ref
        == record.available_for_decision_epoch.clock_ref
        and predecessor_epoch.index.value
        == record.available_for_decision_epoch.index.value - 1
    )
    if not (
        has_predecessor == has_decision == has_epoch
        and (not has_epoch or epoch_matches)
    ):
        _failure(FailureCode.EPOCH_MISMATCH, interface)

    if (
        not _object_hash_matches(record)
        or not _policy_memory_hash_matches(record)
    ):
        _failure(FailureCode.HASH_MISMATCH, interface)
    return None


_DEPENDENCY_SENTINELS = (Measurement, Schedule)


__all__ = (
    "InformationContract",
    "InformationView",
    "InformationReadSet",
    "PolicyMemoryState",
    "MemoryMode",
    "validate_information_view",
    "validate_policy_memory_state",
)
