"""Immutable common envelopes and pure I-2 lifecycle validation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from .canonical import CanonicalBytes, parse_ecj1
from .errors import (
    Applicability,
    FailureCode,
    FailureEnvelope,
    FailureInterfaceRef,
    FailureStage,
    _fail,
)
from .hashing import compute_object_content_hash
from .identity import (
    ObjectContentHash,
    ObjectRef,
    ScientificId,
    SemanticVersion,
)


def _interface(name: str) -> FailureInterfaceRef:
    return FailureInterfaceRef("ebu_framework.envelopes", name, "1.0.0")


def _failure(code: FailureCode, interface: str, summary: str) -> "NoReturn":
    _fail(
        code,
        summary,
        stage=FailureStage.I2,
        interface_ref=_interface(interface),
    )


from typing import NoReturn  # noqa: E402


def _project(value: object) -> object:
    if isinstance(value, StrEnum):
        return value.value
    if type(value) is ObjectRef:
        return value.to_ecj1()
    if hasattr(value, "to_ecj1"):
        return value.to_ecj1()  # type: ignore[union-attr]
    if type(value) is tuple:
        return [_project(item) for item in value]
    return value


def _ref_key(reference: ObjectRef) -> tuple[str, str, str]:
    return (
        str(reference.object_id),
        str(reference.object_version),
        str(reference.object_content_hash),
    )


def _ordered_unique_refs(values: tuple[ObjectRef, ...], *, nonempty: bool = False) -> bool:
    if type(values) is not tuple or not all(type(item) is ObjectRef for item in values):
        return False
    keys = tuple(_ref_key(item) for item in values)
    return (not nonempty or bool(values)) and keys == tuple(sorted(keys)) and len(keys) == len(set(keys))


class LifecycleStatus(StrEnum):
    DRAFT = "DRAFT"
    REVIEWED = "REVIEWED"
    ACCEPTED = "ACCEPTED"
    SUPERSEDED = "SUPERSEDED"
    REVOKED_BEFORE_EXECUTION = "REVOKED_BEFORE_EXECUTION"


@dataclass(frozen=True, slots=True)
class CompatibilityResult:
    """Private common implementation, publicly owned by ``primitives``."""

    compatible: bool
    checked_predicates: tuple[str, ...]
    conversion_rule_ref: ObjectRef | Applicability
    parent_ref: ObjectRef | Applicability
    failure: FailureEnvelope | Applicability

    def __post_init__(self) -> None:
        if type(self.compatible) is not bool or type(self.checked_predicates) is not tuple or not all(
            type(item) is str and bool(item) for item in self.checked_predicates
        ):
            _failure(FailureCode.CORE_NUMBER_INVALID, "CompatibilityResult", "compatibility result has invalid fields")
        if not (
            type(self.conversion_rule_ref) is ObjectRef or type(self.conversion_rule_ref) is Applicability
        ) or not (type(self.parent_ref) is ObjectRef or type(self.parent_ref) is Applicability):
            _failure(FailureCode.IMPLICIT_ABSENCE_FORBIDDEN, "CompatibilityResult", "compatibility refs require typed applicability")
        if self.compatible:
            valid = self.failure is Applicability.NOT_APPLICABLE
        else:
            valid = type(self.failure) is FailureEnvelope
        if not valid:
            _failure(FailureCode.RESOLUTION_STATE_INVALID, "CompatibilityResult", "compatibility and failure fields contradict")

    def to_ecj1(self) -> dict[str, object]:
        return {
            "checked_predicates": list(self.checked_predicates),
            "compatible": self.compatible,
            "conversion_rule_ref": _project(self.conversion_rule_ref),
            "failure": _project(self.failure),
            "parent_ref": _project(self.parent_ref),
            "schema_version": 1,
        }


def _success(
    labels: tuple[str, ...],
    *,
    conversion: ObjectRef | Applicability = Applicability.NOT_APPLICABLE,
    parent: ObjectRef | Applicability = Applicability.NOT_APPLICABLE,
) -> CompatibilityResult:
    return CompatibilityResult(
        True,
        labels,
        conversion,
        parent,
        Applicability.NOT_APPLICABLE,
    )


@dataclass(frozen=True, slots=True)
class CommonObjectEnvelope:
    object_id: ScientificId
    object_kind_id: ScientificId
    schema_id: ScientificId
    schema_version: SemanticVersion
    object_version: SemanticVersion
    authority_refs: tuple[ObjectRef, ...]
    supersedes_ref: ObjectRef | Applicability
    object_content_payload: CanonicalBytes
    object_content_hash: ObjectContentHash
    lifecycle_status: LifecycleStatus
    record_metadata_ref: ObjectRef | Applicability

    def __post_init__(self) -> None:
        if type(self.object_content_payload) is not bytes:
            _fail(
                FailureCode.INVALID_ECJ1,
                "object_content_payload must be exact immutable canonical bytes",
                stage=FailureStage.I1,
            )
        parse_ecj1(self.object_content_payload)

    def to_ecj1(self) -> dict[str, object]:
        payload = parse_ecj1(self.object_content_payload)
        return {
            "authority_refs": [item.to_ecj1() for item in self.authority_refs],
            "lifecycle_status": _project(self.lifecycle_status),
            "object_content_hash": str(self.object_content_hash),
            "object_content_payload": payload,
            "object_id": str(self.object_id),
            "object_kind_id": str(self.object_kind_id),
            "object_version": str(self.object_version),
            "record_metadata_ref": _project(self.record_metadata_ref),
            "schema_id": str(self.schema_id),
            "schema_version": str(self.schema_version),
            "supersedes_ref": _project(self.supersedes_ref),
        }


@dataclass(frozen=True, slots=True)
class RecordMetadata:
    metadata_id: ScientificId
    storage_locator: ObjectRef | Applicability
    database_identity: ObjectRef | Applicability
    ingestion_time_ref: ObjectRef | Applicability
    host_process_ref: ObjectRef | Applicability
    transport_ref: ObjectRef | Applicability
    presentation_annotation_ref: ObjectRef | Applicability
    operational_provenance_ref: ObjectRef | Applicability

    def __post_init__(self) -> None:
        if type(self.metadata_id) is not ScientificId or not all(
            type(value) is ObjectRef or type(value) is Applicability
            for value in (
                self.storage_locator,
                self.database_identity,
                self.ingestion_time_ref,
                self.host_process_ref,
                self.transport_ref,
                self.presentation_annotation_ref,
                self.operational_provenance_ref,
            )
        ):
            _failure(FailureCode.CORE_NUMBER_INVALID, "RecordMetadata", "metadata fields require exact IDs and applicability unions")


@dataclass(frozen=True, slots=True)
class LifecycleTransition:
    object_ref: ObjectRef
    from_status: LifecycleStatus
    to_status: LifecycleStatus
    evidence_refs: tuple[ObjectRef, ...]
    authorization_ref: ObjectRef | Applicability

    def __post_init__(self) -> None:
        if type(self.object_ref) is not ObjectRef or type(self.from_status) is not LifecycleStatus or type(self.to_status) is not LifecycleStatus:
            _failure(FailureCode.CORE_NUMBER_INVALID, "LifecycleTransition", "transition identity and statuses must be typed")
        if type(self.evidence_refs) is not tuple or not all(type(item) is ObjectRef for item in self.evidence_refs):
            _failure(FailureCode.CORE_NUMBER_INVALID, "LifecycleTransition", "transition evidence must be an exact ObjectRef tuple")
        if not (type(self.authorization_ref) is ObjectRef or type(self.authorization_ref) is Applicability):
            _failure(FailureCode.IMPLICIT_ABSENCE_FORBIDDEN, "LifecycleTransition", "transition authorization applicability must be typed")

    def to_ecj1(self) -> dict[str, object]:
        return {
            "authorization_ref": _project(self.authorization_ref),
            "evidence_refs": [item.to_ecj1() for item in self.evidence_refs],
            "from_status": self.from_status.value,
            "object_ref": self.object_ref.to_ecj1(),
            "schema_version": 1,
            "to_status": self.to_status.value,
        }


@dataclass(frozen=True, slots=True)
class LifecycleValidationResult:
    valid: bool
    transition: LifecycleTransition
    checked_predicates: tuple[str, ...]
    failure: FailureEnvelope | Applicability

    def __post_init__(self) -> None:
        if type(self.valid) is not bool or type(self.transition) is not LifecycleTransition or type(self.checked_predicates) is not tuple or not all(type(item) is str for item in self.checked_predicates):
            _failure(FailureCode.CORE_NUMBER_INVALID, "LifecycleValidationResult", "lifecycle validation result has invalid fields")
        if (self.valid and self.failure is not Applicability.NOT_APPLICABLE) or (
            not self.valid and type(self.failure) is not FailureEnvelope
        ):
            _failure(FailureCode.RESOLUTION_STATE_INVALID, "LifecycleValidationResult", "lifecycle result and failure contradict")

    def to_ecj1(self) -> dict[str, object]:
        return {
            "checked_predicates": list(self.checked_predicates),
            "failure": _project(self.failure),
            "schema_version": 1,
            "transition": self.transition.to_ecj1(),
            "valid": self.valid,
        }


@dataclass(frozen=True, slots=True)
class SupersessionRelation:
    predecessor_ref: ObjectRef
    successor_ref: ObjectRef
    predecessor_object_kind_id: ScientificId
    successor_object_kind_id: ScientificId
    predecessor_schema_id: ScientificId
    successor_schema_id: ScientificId
    predecessor_status: LifecycleStatus
    successor_status: LifecycleStatus
    predecessor_supersedes_chain: tuple[ObjectRef, ...]
    relation_evidence_refs: tuple[ObjectRef, ...]
    authorization_ref: ObjectRef | Applicability

    def __post_init__(self) -> None:
        if not all(
            type(value) is ObjectRef for value in (self.predecessor_ref, self.successor_ref)
        ) or not all(
            type(value) is ScientificId
            for value in (
                self.predecessor_object_kind_id,
                self.successor_object_kind_id,
                self.predecessor_schema_id,
                self.successor_schema_id,
            )
        ) or type(self.predecessor_status) is not LifecycleStatus or type(self.successor_status) is not LifecycleStatus:
            _failure(FailureCode.CORE_NUMBER_INVALID, "SupersessionRelation", "supersession identity fields must be typed")
        if type(self.predecessor_supersedes_chain) is not tuple or not all(
            type(item) is ObjectRef for item in self.predecessor_supersedes_chain
        ) or type(self.relation_evidence_refs) is not tuple or not all(
            type(item) is ObjectRef for item in self.relation_evidence_refs
        ):
            _failure(FailureCode.CORE_NUMBER_INVALID, "SupersessionRelation", "supersession collections must be exact ObjectRef tuples")
        if not (type(self.authorization_ref) is ObjectRef or type(self.authorization_ref) is Applicability):
            _failure(FailureCode.IMPLICIT_ABSENCE_FORBIDDEN, "SupersessionRelation", "authorization applicability must be typed")

    def to_ecj1(self) -> dict[str, object]:
        return {
            "authorization_ref": _project(self.authorization_ref),
            "predecessor_object_kind_id": str(self.predecessor_object_kind_id),
            "predecessor_ref": self.predecessor_ref.to_ecj1(),
            "predecessor_schema_id": str(self.predecessor_schema_id),
            "predecessor_status": self.predecessor_status.value,
            "predecessor_supersedes_chain": [item.to_ecj1() for item in self.predecessor_supersedes_chain],
            "relation_evidence_refs": [item.to_ecj1() for item in self.relation_evidence_refs],
            "schema_version": 1,
            "successor_object_kind_id": str(self.successor_object_kind_id),
            "successor_ref": self.successor_ref.to_ecj1(),
            "successor_schema_id": str(self.successor_schema_id),
            "successor_status": self.successor_status.value,
        }


@dataclass(frozen=True, slots=True)
class SupersessionValidationResult:
    valid: bool
    relation: SupersessionRelation
    checked_predicates: tuple[str, ...]
    failure: FailureEnvelope | Applicability

    def __post_init__(self) -> None:
        if type(self.valid) is not bool or type(self.relation) is not SupersessionRelation or type(self.checked_predicates) is not tuple or not all(type(item) is str for item in self.checked_predicates):
            _failure(FailureCode.CORE_NUMBER_INVALID, "SupersessionValidationResult", "supersession validation result has invalid fields")
        if (self.valid and self.failure is not Applicability.NOT_APPLICABLE) or (
            not self.valid and type(self.failure) is not FailureEnvelope
        ):
            _failure(FailureCode.RESOLUTION_STATE_INVALID, "SupersessionValidationResult", "supersession result and failure contradict")

    def to_ecj1(self) -> dict[str, object]:
        return {
            "checked_predicates": list(self.checked_predicates),
            "failure": _project(self.failure),
            "relation": self.relation.to_ecj1(),
            "schema_version": 1,
            "valid": self.valid,
        }


def _contains_exact_string(value: object, target: str) -> bool:
    if type(value) is str:
        return value == target
    if type(value) is list:
        return any(_contains_exact_string(item, target) for item in value)
    if type(value) is dict:
        return any(
            key == target or _contains_exact_string(item, target)
            for key, item in value.items()
        )
    return False


def validate_object_envelope(envelope: CommonObjectEnvelope) -> CompatibilityResult:
    interface = "validate_object_envelope"
    labels = (
        "exact_field_types",
        "authority_ref_order",
        "payload_canonical_bytes",
        "lifecycle_status",
        "direct_content_hash_exclusion",
        "object_content_hash",
    )
    if type(envelope) is not CommonObjectEnvelope:
        _failure(FailureCode.CORE_NUMBER_INVALID, interface, "envelope field types are invalid")
    if not all(
        condition
        for condition in (
            type(envelope.object_id) is ScientificId,
            type(envelope.object_kind_id) is ScientificId,
            type(envelope.schema_id) is ScientificId,
            type(envelope.schema_version) is SemanticVersion,
            type(envelope.object_version) is SemanticVersion,
            type(envelope.authority_refs) is tuple,
            type(envelope.object_content_payload) is bytes,
            type(envelope.object_content_hash) is ObjectContentHash,
            type(envelope.supersedes_ref) is ObjectRef or type(envelope.supersedes_ref) is Applicability,
            type(envelope.record_metadata_ref) is ObjectRef or type(envelope.record_metadata_ref) is Applicability,
        )
    ):
        _failure(FailureCode.CORE_NUMBER_INVALID, interface, "envelope field types are invalid")
    if not _ordered_unique_refs(envelope.authority_refs):
        _failure(FailureCode.CORE_NUMBER_INVALID, interface, "authority refs must be ordered and duplicate-free")
    payload = parse_ecj1(envelope.object_content_payload)
    if type(envelope.lifecycle_status) is not LifecycleStatus:
        _failure(FailureCode.LIFECYCLE_TRANSITION_INVALID, interface, "lifecycle status is invalid")
    if _contains_exact_string(payload, str(envelope.object_content_hash)):
        _failure(FailureCode.HASH_MISMATCH, interface, "payload directly contains its stored content hash")
    recomputed = compute_object_content_hash(
        object_id=envelope.object_id,
        object_kind=str(envelope.object_kind_id),
        schema_id=envelope.schema_id,
        schema_version=envelope.schema_version,
        object_version=envelope.object_version,
        authority_refs=envelope.authority_refs,
        supersedes_ref=(None if envelope.supersedes_ref is Applicability.NOT_APPLICABLE else envelope.supersedes_ref),
        object_content_payload=payload,
    )
    del payload
    if recomputed != envelope.object_content_hash:
        _failure(FailureCode.HASH_MISMATCH, interface, "object content hash does not match canonical payload")
    return _success(labels)


def validate_lifecycle_transition(transition: LifecycleTransition) -> LifecycleValidationResult:
    interface = "validate_lifecycle_transition"
    labels = ("closed_edge", "authorization_applicability", "evidence_order")
    edges = {
        (LifecycleStatus.DRAFT, LifecycleStatus.REVIEWED),
        (LifecycleStatus.REVIEWED, LifecycleStatus.DRAFT),
        (LifecycleStatus.REVIEWED, LifecycleStatus.ACCEPTED),
        (LifecycleStatus.ACCEPTED, LifecycleStatus.SUPERSEDED),
        (LifecycleStatus.ACCEPTED, LifecycleStatus.REVOKED_BEFORE_EXECUTION),
    }
    if type(transition) is not LifecycleTransition or (transition.from_status, transition.to_status) not in edges:
        _failure(FailureCode.LIFECYCLE_TRANSITION_INVALID, interface, "lifecycle edge is outside the closed graph")
    review_edge = transition.to_status in {LifecycleStatus.DRAFT, LifecycleStatus.REVIEWED}
    authorization_valid = (
        transition.authorization_ref is Applicability.NOT_APPLICABLE
        if review_edge
        else type(transition.authorization_ref) is ObjectRef
    )
    if not authorization_valid:
        _failure(FailureCode.IMPLICIT_ABSENCE_FORBIDDEN, interface, "lifecycle authorization applicability is invalid")
    if not _ordered_unique_refs(transition.evidence_refs, nonempty=True):
        _failure(FailureCode.LIFECYCLE_TRANSITION_INVALID, interface, "lifecycle evidence must be nonempty, ordered, and unique")
    return LifecycleValidationResult(True, transition, labels, Applicability.NOT_APPLICABLE)


def _version_key(version: SemanticVersion) -> tuple[int, int, int]:
    return (version.major, version.minor, version.patch)


def validate_supersession_relation(relation: SupersessionRelation) -> SupersessionValidationResult:
    interface = "validate_supersession_relation"
    labels = (
        "logical_object_id",
        "object_kind_id",
        "schema_id",
        "version_increase",
        "content_change",
        "lifecycle_pair",
        "predecessor_not_in_own_ancestry",
        "successor_not_in_ancestry",
        "unique_linear_ancestry",
        "ancestry_ends_at_predecessor",
        "evidence_nonempty",
        "authorization_applicable",
    )
    if type(relation.authorization_ref) is not ObjectRef:
        _failure(FailureCode.IMPLICIT_ABSENCE_FORBIDDEN, interface, "supersession requires an authorization ref")
    if not (
        relation.predecessor_status is LifecycleStatus.ACCEPTED
        and relation.successor_status is LifecycleStatus.REVIEWED
    ):
        _failure(FailureCode.LIFECYCLE_TRANSITION_INVALID, interface, "supersession lifecycle pair is invalid")
    if relation.predecessor_ref.object_id != relation.successor_ref.object_id:
        _failure(FailureCode.SUPERSESSION_INVALID, interface, "supersession must retain logical object identity")
    if relation.predecessor_object_kind_id != relation.successor_object_kind_id:
        _failure(FailureCode.SUPERSESSION_INVALID, interface, "supersession must retain object kind identity")
    if relation.predecessor_schema_id != relation.successor_schema_id:
        _failure(FailureCode.SUPERSESSION_INVALID, interface, "supersession must retain schema identity")
    if _version_key(relation.successor_ref.object_version) <= _version_key(relation.predecessor_ref.object_version):
        _failure(FailureCode.SUPERSESSION_INVALID, interface, "successor version must increase")
    if relation.successor_ref.object_content_hash == relation.predecessor_ref.object_content_hash:
        _failure(FailureCode.SUPERSESSION_INVALID, interface, "successor content must change")
    chain = relation.predecessor_supersedes_chain
    if relation.predecessor_ref in chain[:-1]:
        _failure(FailureCode.SUPERSESSION_INVALID, interface, "predecessor repeats inside its own ancestry")
    if relation.successor_ref in chain:
        _failure(FailureCode.SUPERSESSION_INVALID, interface, "successor occurs in predecessor ancestry")
    chain_keys = tuple(_ref_key(item) for item in chain)
    linear = bool(chain) and len(chain_keys) == len(set(chain_keys))
    if not linear:
        _failure(FailureCode.SUPERSESSION_INVALID, interface, "ancestry must be one unique linear chain")
    if chain[-1] != relation.predecessor_ref:
        _failure(FailureCode.SUPERSESSION_INVALID, interface, "ancestry must end at the predecessor")
    if not relation.relation_evidence_refs:
        _failure(FailureCode.SUPERSESSION_INVALID, interface, "supersession requires evidence")
    return SupersessionValidationResult(True, relation, labels, Applicability.NOT_APPLICABLE)


__all__ = (
    "CommonObjectEnvelope",
    "LifecycleStatus",
    "LifecycleTransition",
    "LifecycleValidationResult",
    "RecordMetadata",
    "SupersessionRelation",
    "SupersessionValidationResult",
    "validate_lifecycle_transition",
    "validate_object_envelope",
    "validate_supersession_relation",
)
