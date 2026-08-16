"""Immutable I-3 state declarations and locally observable T0 validation."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import NoReturn

from .canonical import CanonicalBytes, encode_ecj1, parse_ecj1
from .primitives import Epoch, ResolutionDetail
from .identity import (
    ObjectContentHash,
    ObjectRef,
    RepresentedStateProjectionHash,
    StatePayloadHash,
)
from .envelopes import CommonObjectEnvelope
from .hashing import (
    compute_object_content_hash,
    compute_represented_state_projection_hash,
    compute_state_payload_hash,
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


_SCIENTIFIC_ID_RE = re.compile(
    r"ebu:[a-z0-9][a-z0-9._-]*:[a-z0-9][a-z0-9._-]*:[a-z0-9][a-z0-9._-]*",
    re.ASCII,
)
_SEMANTIC_VERSION_RE = re.compile(
    r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", re.ASCII
)
_DIGEST_RE = re.compile(r"sha256:[0-9a-f]{64}", re.ASCII)
_RESERVED_PHYSICAL_KEYS = frozenset(
    {
        "policy_memory",
        "policy_memory_payload",
        "causal_contribution",
        "settlement_share",
        "settlement_allocation",
    }
)


def _interface(name: str) -> FailureInterfaceRef:
    return FailureInterfaceRef("ebu_framework.state", name, "1.0.0")


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


def _canonical_bytes(value: object, interface: str) -> bool:
    if type(value) is not bytes:
        return False
    try:
        parse_ecj1(value)
    except FrameworkError:
        return False
    return True


def _object_or_applicability(value: object) -> bool:
    return type(value) is ObjectRef or type(value) is Applicability


def _object_ref_tuple(value: object) -> bool:
    return type(value) is tuple and all(type(item) is ObjectRef for item in value)


def _ref_key(reference: ObjectRef) -> tuple[str, str, str]:
    return (
        str(reference.object_id),
        str(reference.object_version),
        str(reference.object_content_hash),
    )


def _project(value: object) -> object:
    if type(value) is bytes:
        return parse_ecj1(value)
    if type(value) is Applicability:
        return value.value
    if type(value) is ObjectRef:
        return value.to_ecj1()
    if type(value) is tuple:
        return [_project(item) for item in value]
    if hasattr(value, "to_ecj1"):
        return value.to_ecj1()  # type: ignore[union-attr]
    return value


@_strict_formation
@dataclass(
    frozen=True,
    slots=True,
    eq=True,
    order=False,
    unsafe_hash=False,
    kw_only=True,
)
class SystemState:
    envelope: CommonObjectEnvelope
    state_schema_ref: ObjectRef
    epoch: Epoch
    physical_state_payload: CanonicalBytes
    topology_state_ref: ObjectRef
    queue_and_transit_state_payload: CanonicalBytes
    commitment_state_payload: CanonicalBytes
    delayed_effect_state_payload: CanonicalBytes
    external_input_refs: tuple[ObjectRef, ...]
    update_ownership_ref: ObjectRef | Applicability
    predecessor_state_ref: ObjectRef | Applicability
    state_payload_hash: StatePayloadHash

    def __post_init__(self) -> None:
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and type(self.state_schema_ref) is ObjectRef
            and type(self.epoch) is Epoch
            and type(self.topology_state_ref) is ObjectRef
            and _object_ref_tuple(self.external_input_refs)
            and _object_or_applicability(self.update_ownership_ref)
            and _object_or_applicability(self.predecessor_state_ref)
            and type(self.state_payload_hash) is StatePayloadHash
            and all(
                _canonical_bytes(value, "SystemState")
                for value in (
                    self.physical_state_payload,
                    self.queue_and_transit_state_payload,
                    self.commitment_state_payload,
                    self.delayed_effect_state_payload,
                )
            )
        ):
            _formation_failure("SystemState")

    def to_ecj1(self) -> dict[str, object]:
        return {
            "state_schema_ref": self.state_schema_ref.to_ecj1(),
            "epoch": self.epoch.to_ecj1(),
            "physical_state_payload": parse_ecj1(self.physical_state_payload),
            "topology_state_ref": self.topology_state_ref.to_ecj1(),
            "queue_and_transit_state_payload": parse_ecj1(
                self.queue_and_transit_state_payload
            ),
            "commitment_state_payload": parse_ecj1(
                self.commitment_state_payload
            ),
            "delayed_effect_state_payload": parse_ecj1(
                self.delayed_effect_state_payload
            ),
            "external_input_refs": [
                item.to_ecj1() for item in self.external_input_refs
            ],
            "update_ownership_ref": _project(self.update_ownership_ref),
            "predecessor_state_ref": _project(self.predecessor_state_ref),
        }


@_strict_formation
@dataclass(
    frozen=True,
    slots=True,
    eq=True,
    order=False,
    unsafe_hash=False,
    kw_only=True,
)
class RepresentedState:
    envelope: CommonObjectEnvelope
    source_state_ref: ObjectRef
    source_state_payload_hash: StatePayloadHash
    boundary_ref: ObjectRef
    projection_contract_ref: ObjectRef
    included_coordinate_refs: tuple[ObjectRef, ...]
    excluded_coordinate_resolutions: tuple[tuple[ObjectRef, ResolutionDetail], ...]
    represented_state_payload: CanonicalBytes
    represented_state_projection_hash: RepresentedStateProjectionHash

    def __post_init__(self) -> None:
        pairs = self.excluded_coordinate_resolutions
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and type(self.source_state_ref) is ObjectRef
            and type(self.source_state_payload_hash) is StatePayloadHash
            and type(self.boundary_ref) is ObjectRef
            and type(self.projection_contract_ref) is ObjectRef
            and _object_ref_tuple(self.included_coordinate_refs)
            and type(pairs) is tuple
            and all(
                type(pair) is tuple
                and len(pair) == 2
                and type(pair[0]) is ObjectRef
                and type(pair[1]) is ResolutionDetail
                for pair in pairs
            )
            and _canonical_bytes(
                self.represented_state_payload, "RepresentedState"
            )
            and type(self.represented_state_projection_hash)
            is RepresentedStateProjectionHash
        ):
            _formation_failure("RepresentedState")

    def to_ecj1(self) -> dict[str, object]:
        return {
            "source_state_ref": self.source_state_ref.to_ecj1(),
            "source_state_payload_hash": str(self.source_state_payload_hash),
            "boundary_ref": self.boundary_ref.to_ecj1(),
            "projection_contract_ref": self.projection_contract_ref.to_ecj1(),
            "included_coordinate_refs": [
                item.to_ecj1() for item in self.included_coordinate_refs
            ],
            "excluded_coordinate_resolutions": [
                [reference.to_ecj1(), resolution.to_ecj1()]
                for reference, resolution in self.excluded_coordinate_resolutions
            ],
            "represented_state_payload": parse_ecj1(
                self.represented_state_payload
            ),
        }


@_strict_formation
@dataclass(
    frozen=True,
    slots=True,
    eq=True,
    order=False,
    unsafe_hash=False,
    kw_only=True,
)
class ProjectionContract:
    envelope: CommonObjectEnvelope
    state_schema_ref: ObjectRef
    boundary_ref: ObjectRef
    required_coordinate_refs: tuple[ObjectRef, ...]
    excluded_coordinate_refs: tuple[ObjectRef, ...]
    distortion_domain_coordinate_refs: tuple[ObjectRef, ...]
    projection_rule_ref: ObjectRef

    def __post_init__(self) -> None:
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and type(self.state_schema_ref) is ObjectRef
            and type(self.boundary_ref) is ObjectRef
            and _object_ref_tuple(self.required_coordinate_refs)
            and _object_ref_tuple(self.excluded_coordinate_refs)
            and _object_ref_tuple(self.distortion_domain_coordinate_refs)
            and type(self.projection_rule_ref) is ObjectRef
        ):
            _formation_failure("ProjectionContract")

    def to_ecj1(self) -> dict[str, object]:
        return {
            "state_schema_ref": self.state_schema_ref.to_ecj1(),
            "boundary_ref": self.boundary_ref.to_ecj1(),
            "required_coordinate_refs": [
                item.to_ecj1() for item in self.required_coordinate_refs
            ],
            "excluded_coordinate_refs": [
                item.to_ecj1() for item in self.excluded_coordinate_refs
            ],
            "distortion_domain_coordinate_refs": [
                item.to_ecj1()
                for item in self.distortion_domain_coordinate_refs
            ],
            "projection_rule_ref": self.projection_rule_ref.to_ecj1(),
        }


def _failure_object(record: object) -> FailureObjectRef:
    envelope = record.envelope  # type: ignore[attr-defined]
    return FailureObjectRef(
        object_id=str(envelope.object_id),
        object_version=str(envelope.object_version),
        object_content_hash=str(envelope.object_content_hash),
    )


def _object_content_check(
    record: SystemState | RepresentedState | ProjectionContract,
    interface: str,
    position: str,
) -> None:
    stored = parse_ecj1(record.envelope.object_content_payload)
    projected = record.to_ecj1()
    if stored != projected:
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


def _pair_order(
    values: tuple[tuple[ObjectRef, ResolutionDetail], ...],
) -> bool:
    keys = tuple(_ref_key(reference) for reference, _ in values)
    return keys == tuple(sorted(keys))


def _pair_duplicates(
    values: tuple[tuple[ObjectRef, ResolutionDetail], ...],
) -> bool:
    first_keys = tuple(_ref_key(reference) for reference, _ in values)
    projections = tuple(
        bytes(encode_ecj1([reference.to_ecj1(), resolution.to_ecj1()]))
        for reference, resolution in values
    )
    return len(first_keys) != len(set(first_keys)) or len(projections) != len(
        set(projections)
    )


def _coordinate_key(value: object) -> tuple[str, str, str] | None:
    if type(value) is not dict or set(value) != {
        "object_content_hash",
        "object_id",
        "object_version",
    }:
        return None
    object_id = value["object_id"]
    object_version = value["object_version"]
    object_hash = value["object_content_hash"]
    if not (
        type(object_id) is str
        and _SCIENTIFIC_ID_RE.fullmatch(object_id)
        and type(object_version) is str
        and _SEMANTIC_VERSION_RE.fullmatch(object_version)
        and type(object_hash) is str
        and _DIGEST_RE.fullmatch(object_hash)
    ):
        return None
    return object_id, object_version, object_hash


def _coordinate_payload(
    payload: object,
) -> tuple[tuple[str, str, str], ...] | None:
    if type(payload) is not dict or set(payload) != {"coordinates"}:
        return None
    coordinates = payload["coordinates"]
    if type(coordinates) is not list:
        return None
    keys: list[tuple[str, str, str]] = []
    for pair in coordinates:
        if type(pair) is not list or len(pair) != 2:
            return None
        key = _coordinate_key(pair[0])
        if key is None:
            return None
        keys.append(key)
    key_tuple = tuple(keys)
    if key_tuple != tuple(sorted(key_tuple)) or len(key_tuple) != len(
        set(key_tuple)
    ):
        return None
    return key_tuple


def _object_hash_matches(
    record: SystemState | RepresentedState | ProjectionContract,
) -> bool:
    envelope = record.envelope
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


def _state_payload_hash_matches(record: SystemState) -> bool:
    recomputed = compute_state_payload_hash(
        state_schema_ref=record.state_schema_ref,
        epoch=record.epoch.to_ecj1(),
        physical_state_x=parse_ecj1(record.physical_state_payload),
        topology_state_g=record.topology_state_ref.to_ecj1(),
        queue_and_transit_state_q=parse_ecj1(
            record.queue_and_transit_state_payload
        ),
        commitment_state_c=parse_ecj1(record.commitment_state_payload),
        delayed_effect_state_ell=parse_ecj1(
            record.delayed_effect_state_payload
        ),
        declared_external_inputs_applied=tuple(record.external_input_refs),
    )
    return recomputed == record.state_payload_hash


def _represented_hash_matches(record: RepresentedState) -> bool:
    excluded = tuple(
        [reference.to_ecj1(), resolution.state.value]
        for reference, resolution in record.excluded_coordinate_resolutions
    )
    recomputed = compute_represented_state_projection_hash(
        source_state_payload_hash=record.source_state_payload_hash,
        boundary_ref=record.boundary_ref,
        projection_contract_ref=record.projection_contract_ref,
        included_coordinate_ids=tuple(record.included_coordinate_refs),
        excluded_coordinate_ids_and_resolution_states=excluded,
        represented_state_payload=parse_ecj1(record.represented_state_payload),
    )
    return recomputed == record.represented_state_projection_hash


def validate_state_record(
    record: SystemState,
    projection_contract: ProjectionContract,
    predecessor_epoch: Epoch | Applicability,
    /,
) -> None:
    if type(record) is not SystemState:
        _formation_failure("SystemState")
    if type(projection_contract) is not ProjectionContract:
        _formation_failure("ProjectionContract")
    if type(predecessor_epoch) not in (Epoch, Applicability):
        _formation_failure("Epoch")

    _object_content_check(
        record, "validate_state_record", "argument 1 (record)"
    )
    _object_content_check(
        projection_contract,
        "validate_state_record",
        "argument 2 (projection_contract)",
    )

    predecessor_is_ref = type(record.predecessor_state_ref) is ObjectRef
    predecessor_is_epoch = type(predecessor_epoch) is Epoch
    if (
        record.update_ownership_ref is Applicability.APPLICABLE
        or record.predecessor_state_ref is Applicability.APPLICABLE
        or predecessor_epoch is Applicability.APPLICABLE
        or predecessor_is_ref != predecessor_is_epoch
    ):
        _failure(
            FailureCode.IMPLICIT_ABSENCE_FORBIDDEN,
            "validate_state_record",
        )

    if not _ordered_refs(record.external_input_refs):
        _failure(
            FailureCode.I3_COLLECTION_ORDER_INVALID,
            "validate_state_record",
        )
    if _duplicate_refs(record.external_input_refs):
        _failure(FailureCode.I3_DUPLICATE_MEMBER, "validate_state_record")

    physical_payload = parse_ecj1(record.physical_state_payload)
    if type(physical_payload) is dict and _RESERVED_PHYSICAL_KEYS.intersection(
        physical_payload
    ):
        _failure(
            FailureCode.PHYSICAL_POLICY_MEMORY_CONFLATION,
            "validate_state_record",
        )

    projection_payload = physical_payload
    if type(physical_payload) is dict:
        projection_payload = {
            key: value
            for key, value in physical_payload.items()
            if key not in _RESERVED_PHYSICAL_KEYS
        }
    coordinate_keys = _coordinate_payload(projection_payload)
    if coordinate_keys is None:
        _failure(FailureCode.STATE_PROJECTION_FAILURE, "validate_state_record")

    required_keys = tuple(
        _ref_key(item) for item in projection_contract.required_coordinate_refs
    )
    if any(key not in coordinate_keys for key in required_keys):
        _failure(FailureCode.MISSING_COORDINATE, "validate_state_record")

    if predecessor_is_epoch and not (
        predecessor_epoch.clock_ref == record.epoch.clock_ref
        and predecessor_epoch.index.value == record.epoch.index.value - 1
    ):
        _failure(FailureCode.EPOCH_MISMATCH, "validate_state_record")

    if not (
        _object_hash_matches(record)
        and _state_payload_hash_matches(record)
        and _object_hash_matches(projection_contract)
    ):
        _failure(FailureCode.HASH_MISMATCH, "validate_state_record")
    return None


def validate_projection_contract(
    represented: RepresentedState,
    contract: ProjectionContract,
    /,
) -> None:
    if type(represented) is not RepresentedState:
        _formation_failure("RepresentedState")
    if type(contract) is not ProjectionContract:
        _formation_failure("ProjectionContract")

    _object_content_check(
        represented,
        "validate_projection_contract",
        "argument 1 (represented)",
    )
    _object_content_check(
        contract,
        "validate_projection_contract",
        "argument 2 (contract)",
    )

    ref_collections = (
        represented.included_coordinate_refs,
        contract.required_coordinate_refs,
        contract.excluded_coordinate_refs,
        contract.distortion_domain_coordinate_refs,
    )
    if any(not _ordered_refs(values) for values in ref_collections) or not _pair_order(
        represented.excluded_coordinate_resolutions
    ):
        _failure(
            FailureCode.I3_COLLECTION_ORDER_INVALID,
            "validate_projection_contract",
        )
    if any(_duplicate_refs(values) for values in ref_collections) or _pair_duplicates(
        represented.excluded_coordinate_resolutions
    ):
        _failure(
            FailureCode.I3_DUPLICATE_MEMBER,
            "validate_projection_contract",
        )

    coordinate_keys = _coordinate_payload(
        parse_ecj1(represented.represented_state_payload)
    )
    if coordinate_keys is None:
        _failure(
            FailureCode.STATE_PROJECTION_FAILURE,
            "validate_projection_contract",
        )
    required_keys = tuple(_ref_key(item) for item in contract.required_coordinate_refs)
    if any(key not in coordinate_keys for key in required_keys):
        _failure(FailureCode.MISSING_COORDINATE, "validate_projection_contract")

    if not (
        _object_hash_matches(represented)
        and _represented_hash_matches(represented)
        and _object_hash_matches(contract)
    ):
        _failure(FailureCode.HASH_MISMATCH, "validate_projection_contract")
    return None


__all__ = (
    "SystemState",
    "RepresentedState",
    "ProjectionContract",
    "validate_state_record",
    "validate_projection_contract",
)
