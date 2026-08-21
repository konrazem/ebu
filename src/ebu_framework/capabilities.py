"""Synthetic T1 information views and non-reconstructible access capabilities."""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timezone
from enum import StrEnum
import hashlib
import re
from typing import NoReturn

from . import authorization as _authorization
from . import policy as _policy
from . import observation as _observation
from . import experiment as _experiment
from . import hashing as _hashing
from . import identity as _identity
from .errors import Applicability, FailureCode, FrameworkError, _i4_fail


InformationContract = _policy.InformationContract
InformationView = _policy.InformationView
InformationReadSet = _policy.InformationReadSet
CanonicalBytes = _policy.CanonicalBytes
ObjectRef = _identity.ObjectRef

_UTC_RE = re.compile(
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6}Z",
    re.ASCII,
)
_PRIVATE_CAPABILITY_TOKEN = object()
_ISSUED_CAPABILITY_IDS: set[int] = set()
_ISSUED_CAPABILITIES: list[object] = []


def _failure(code: FailureCode, check: str) -> NoReturn:
    _i4_fail(
        code,
        "ebu_framework.capabilities",
        "build_synthetic_information_view",
        check,
    )


def _formation_failure(name: str) -> NoReturn:
    _i4_fail(
        FailureCode.I4_RECORD_FORMATION_INVALID,
        "ebu_framework.capabilities",
        name,
        "exact record formation",
    )


def _timestamp(value: object) -> bool:
    if type(value) is not str or _UTC_RE.fullmatch(value) is None:
        return False
    try:
        datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        return False
    return True


def _instant(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ").replace(
        tzinfo=timezone.utc
    )


def _ref_key(reference: ObjectRef) -> bytes:
    return bytes(_authorization._trust.encode_ecj1(reference.to_ecj1()))


def _ordered_unique_refs(values: object) -> bool:
    if not (
        type(values) is tuple
        and all(type(item) is ObjectRef for item in values)
    ):
        return False
    keys = tuple(_ref_key(item) for item in values)
    return keys == tuple(sorted(keys)) and len(keys) == len(set(keys))


def _envelope_ref(record: object) -> ObjectRef:
    envelope = record.envelope  # type: ignore[attr-defined]
    return ObjectRef(
        object_id=envelope.object_id,
        object_version=envelope.object_version,
        object_content_hash=envelope.object_content_hash,
    )


def _validation_ref(kind: str, payload: bytes, template: ObjectRef) -> ObjectRef:
    digest = hashlib.sha256(payload).hexdigest()
    return ObjectRef(
        object_id=_identity.ScientificId(
            f"ebu:{kind}:validation:sha256-{digest}"
        ),
        object_version=template.object_version,
        object_content_hash=_identity.ObjectContentHash.from_hex(digest),
    )


def _contains_traversal(value: object, *, parent_key: str = "") -> bool:
    dangerous_keys = {
        "alias",
        "attribute",
        "callback",
        "descriptor",
        "mapping_key",
        "nested_ref",
        "object_graph",
        "path",
        "registry",
        "uri",
    }
    if type(value) is dict:
        for key, member in value.items():
            if type(key) is not str:
                return True
            normalized = key.lower().replace("-", "_")
            if normalized in dangerous_keys or normalized.endswith("_ref"):
                return True
            if _contains_traversal(member, parent_key=normalized):
                return True
        return False
    if type(value) is list:
        return any(_contains_traversal(item, parent_key=parent_key) for item in value)
    if type(value) is str:
        lowered = value.lower()
        return (
            lowered.startswith(("ebu:", "file:", "http:", "https:", "urn:"))
            or value.startswith(("/", "./", "../", "~"))
            or "callback" in parent_key
        )
    return False


class CapabilityClass(StrEnum):
    T0 = "T0"
    T1 = "T1"
    T2 = "T2"
    T3 = "T3"

    @classmethod
    def _missing_(cls, value: object) -> NoReturn:
        _formation_failure("CapabilityClass")


@dataclass(
    frozen=True,
    slots=True,
    eq=True,
    order=False,
    unsafe_hash=False,
    init=False,
)
class AccessCapability:
    authorization_validation_ref: ObjectRef
    configuration_ref_or_not_applicable: ObjectRef | Applicability
    binding_ref_or_not_applicable: ObjectRef | Applicability
    information_contract_ref: ObjectRef
    visible_field_refs: tuple[ObjectRef, ...]
    permitted_read_refs: tuple[ObjectRef, ...]
    available_at: str
    maximum_age_microseconds: int
    current_memory_ref_or_not_applicable: ObjectRef | Applicability
    traversal_allowed: bool
    capability_class: CapabilityClass

    def __getattribute__(self, name: str) -> object:
        if name != "__class__" and id(self) not in _ISSUED_CAPABILITY_IDS:
            _failure(
                FailureCode.CAPABILITY_ESCALATION_FORBIDDEN,
                "unissued AccessCapability reconstruction",
            )
        return object.__getattribute__(self, name)

    def __init__(self, *args: object, **kwargs: object) -> None:
        del args, kwargs
        _failure(
            FailureCode.CAPABILITY_ESCALATION_FORBIDDEN,
            "private AccessCapability constructor",
        )

    def __init_subclass__(cls, **kwargs: object) -> None:
        del kwargs
        _failure(
            FailureCode.CAPABILITY_ESCALATION_FORBIDDEN,
            "AccessCapability subclassing",
        )

    def __copy__(self) -> NoReturn:
        _failure(
            FailureCode.CAPABILITY_ESCALATION_FORBIDDEN,
            "AccessCapability copying",
        )

    def __deepcopy__(self, memo: object) -> NoReturn:
        del memo
        _failure(
            FailureCode.CAPABILITY_ESCALATION_FORBIDDEN,
            "AccessCapability deep copying",
        )

    def __reduce__(self) -> NoReturn:
        _failure(
            FailureCode.CAPABILITY_ESCALATION_FORBIDDEN,
            "AccessCapability pickling",
        )

    def __reduce_ex__(self, protocol: object) -> NoReturn:
        del protocol
        _failure(
            FailureCode.CAPABILITY_ESCALATION_FORBIDDEN,
            "AccessCapability pickling",
        )

    def to_ecj1(self) -> dict[str, object]:
        projection: dict[str, object] = {}
        for field in fields(self):
            value = getattr(self, field.name)
            if type(value) is ObjectRef:
                projected: object = value.to_ecj1()
            elif type(value) is Applicability:
                projected = value.value
            elif isinstance(value, StrEnum):
                projected = value.value
            elif type(value) is tuple:
                projected = [item.to_ecj1() for item in value]
            else:
                projected = value
            projection[field.name] = projected
        return projection


def _new_capability(**values: object) -> AccessCapability:
    capability = object.__new__(AccessCapability)
    for field in fields(AccessCapability):
        object.__setattr__(capability, field.name, values[field.name])
    _ISSUED_CAPABILITY_IDS.add(id(capability))
    valid = (
        type(capability.authorization_validation_ref) is ObjectRef
        and (
            type(capability.configuration_ref_or_not_applicable) is ObjectRef
            or capability.configuration_ref_or_not_applicable
            is Applicability.NOT_APPLICABLE
        )
        and (
            type(capability.binding_ref_or_not_applicable) is ObjectRef
            or capability.binding_ref_or_not_applicable
            is Applicability.NOT_APPLICABLE
        )
        and type(capability.information_contract_ref) is ObjectRef
        and _ordered_unique_refs(capability.visible_field_refs)
        and _ordered_unique_refs(capability.permitted_read_refs)
        and _timestamp(capability.available_at)
        and type(capability.maximum_age_microseconds) is int
        and capability.maximum_age_microseconds >= 0
        and (
            type(capability.current_memory_ref_or_not_applicable) is ObjectRef
            or capability.current_memory_ref_or_not_applicable
            is Applicability.NOT_APPLICABLE
        )
        and capability.traversal_allowed is False
        and capability.capability_class is CapabilityClass.T1
    )
    if not valid:
        _ISSUED_CAPABILITY_IDS.discard(id(capability))
        _formation_failure("AccessCapability")
    _ISSUED_CAPABILITIES.append(capability)
    return capability


def build_synthetic_information_view(
    contract: InformationContract,
    expected_current_memory_ref_or_not_applicable: ObjectRef | Applicability,
    fabricated_fields: tuple[tuple[ObjectRef, CanonicalBytes, str], ...],
    attempted_read_set: InformationReadSet | Applicability,
    injected_now: str,
    /,
) -> tuple[InformationView, AccessCapability]:
    if not (
        type(contract) is InformationContract
        and (
            type(expected_current_memory_ref_or_not_applicable) is ObjectRef
            or expected_current_memory_ref_or_not_applicable
            is Applicability.NOT_APPLICABLE
        )
        and type(fabricated_fields) is tuple
        and all(
            type(item) is tuple
            and len(item) == 3
            and type(item[0]) is ObjectRef
            and type(item[1]) is bytes
            and type(item[2]) is str
            for item in fabricated_fields
        )
        and (
            type(attempted_read_set) is InformationReadSet
            or attempted_read_set is Applicability.NOT_APPLICABLE
        )
        and _timestamp(injected_now)
    ):
        _formation_failure("build_synthetic_information_view")
    try:
        _policy.validate_object_envelope(contract.envelope)
    except FrameworkError:
        _failure(
            FailureCode.INFORMATION_CAPABILITY_INVALID,
            "synthetic contract envelope",
        )
    contract_ref = _envelope_ref(contract)
    all_refs = tuple(item[0] for item in fabricated_fields)
    if not (
        fabricated_fields
        and _ordered_unique_refs(all_refs)
        and all(
            reference.object_id.namespace == "validation"
            for reference in all_refs + (contract_ref,)
        )
        and all(reference in contract.visible_field_refs for reference in all_refs)
    ):
        _failure(FailureCode.INFORMATION_NOT_VISIBLE, "1 explicit visibility")

    now = _instant(injected_now)
    if any(not _timestamp(available_at) for _, _, available_at in fabricated_fields):
        _formation_failure("build_synthetic_information_view")
    if any(_instant(available_at) > now for _, _, available_at in fabricated_fields):
        _failure(
            FailureCode.INFORMATION_NOT_AVAILABLE,
            "2 availability no later than injected now",
        )

    age_by_ref = {reference: duration for reference, duration in contract.max_age_rules}
    if any(reference not in age_by_ref for reference in all_refs):
        _failure(FailureCode.INFORMATION_TOO_OLD, "3 declared maximum age")
    maximum_age = min(age_by_ref[reference].ticks.value for reference in all_refs)
    for reference, _, available_at in fabricated_fields:
        age = int((now - _instant(available_at)).total_seconds() * 1_000_000)
        if age < 0 or age > age_by_ref[reference].ticks.value:
            _failure(FailureCode.INFORMATION_TOO_OLD, "3 maximum age")

    current_memory: ObjectRef | Applicability = Applicability.NOT_APPLICABLE
    memory_hash: _identity.PolicyMemoryPayloadHash | Applicability = (
        Applicability.NOT_APPLICABLE
    )
    read_object_refs: tuple[ObjectRef, ...] = ()
    if type(attempted_read_set) is InformationReadSet:
        read_object_refs = attempted_read_set.read_object_refs
    expected_memory = expected_current_memory_ref_or_not_applicable
    if expected_memory is Applicability.NOT_APPLICABLE:
        if read_object_refs:
            _failure(
                FailureCode.INFORMATION_CAPABILITY_INVALID,
                "4 stateless current memory must be absent",
            )
    else:
        if (
            expected_memory.object_id.namespace != "validation"
            or len(read_object_refs) != 1
            or read_object_refs[0] != expected_memory
        ):
            _failure(
                FailureCode.CURRENT_MEMORY_MISMATCH,
                "4 expected current memory equality and cardinality",
            )
        current_memory = expected_memory
        memory_hash = _identity.PolicyMemoryPayloadHash.from_hex(
            hashlib.sha256(_ref_key(current_memory)).hexdigest()
        )

    parsed_fields: list[tuple[ObjectRef, CanonicalBytes, object]] = []
    for reference, payload, available_at in fabricated_fields:
        try:
            parsed = _authorization._trust.parse_ecj1(payload)
        except FrameworkError:
            _formation_failure("build_synthetic_information_view")
        if _contains_traversal(parsed):
            _failure(
                FailureCode.INFORMATION_TRAVERSAL_FORBIDDEN,
                "5 no traversal",
            )
        parsed_fields.append((reference, payload, parsed))

    read_refs: tuple[ObjectRef, ...] = ()
    if type(attempted_read_set) is InformationReadSet:
        read_refs = attempted_read_set.read_field_refs
        if not (
            _ordered_unique_refs(read_refs)
            and set(read_refs) <= set(all_refs)
            and attempted_read_set.information_view_ref.object_id.namespace
            == "validation"
        ):
            _failure(
                FailureCode.INFORMATION_READ_SET_DENIED,
                "6 read-set subset, order, and uniqueness",
            )

    policy_ref = (
        contract.availability_rule_refs[0]
        if contract.availability_rule_refs
        else contract_ref
    )
    if policy_ref.object_id.namespace != "validation":
        _failure(
            FailureCode.INFORMATION_CAPABILITY_INVALID,
            "4 validation policy reference",
        )
    clock_ref = age_by_ref[all_refs[0]].clock_ref
    decision_epoch = _policy.Epoch(
        clock_ref=clock_ref,
        index=type(age_by_ref[all_refs[0]].ticks)(
            int(now.timestamp() * 1_000_000)
        ),
    )
    field_records = tuple((reference, payload) for reference, payload, _ in parsed_fields)
    hash_fields = tuple(
        [reference.to_ecj1(), parsed]
        for reference, _, parsed in parsed_fields
    )
    information_view_hash = _hashing.compute_information_view_hash(
        policy_ref=policy_ref,
        information_contract_ref=contract_ref,
        decision_epoch=decision_epoch.to_ecj1(),
        current_policy_memory_payload_hash_or_not_applicable=(
            memory_hash
            if type(memory_hash) is _identity.PolicyMemoryPayloadHash
            else Applicability.NOT_APPLICABLE.value
        ),
        ordered_visible_field_records=hash_fields,
        ordered_visible_object_refs=(),
    )
    view_payload = {
        "current_policy_memory_payload_hash": (
            str(memory_hash)
            if type(memory_hash) is _identity.PolicyMemoryPayloadHash
            else Applicability.NOT_APPLICABLE.value
        ),
        "decision_epoch": decision_epoch.to_ecj1(),
        "information_contract_ref": contract_ref.to_ecj1(),
        "policy_ref": policy_ref.to_ecj1(),
        "visible_field_records": list(hash_fields),
        "visible_object_refs": [],
    }
    canonical_payload = bytes(_authorization._trust.encode_ecj1(view_payload))
    view_id = _identity.ScientificId(
        "ebu:information-view:validation:sha256-"
        + hashlib.sha256(canonical_payload).hexdigest()
    )
    envelope = _policy.CommonObjectEnvelope(
        object_id=view_id,
        object_kind_id=_identity.ScientificId(
            "ebu:kind:validation:information-view"
        ),
        schema_id=contract.envelope.schema_id,
        schema_version=contract.envelope.schema_version,
        object_version=contract.envelope.object_version,
        authority_refs=contract.envelope.authority_refs,
        supersedes_ref=Applicability.NOT_APPLICABLE,
        object_content_payload=canonical_payload,
        object_content_hash=_hashing.compute_object_content_hash(
            object_id=view_id,
            object_kind="ebu:kind:validation:information-view",
            schema_id=contract.envelope.schema_id,
            schema_version=contract.envelope.schema_version,
            object_version=contract.envelope.object_version,
            authority_refs=contract.envelope.authority_refs,
            supersedes_ref=None,
            object_content_payload=view_payload,
        ),
        lifecycle_status=contract.envelope.lifecycle_status,
        record_metadata_ref=Applicability.NOT_APPLICABLE,
    )
    view = InformationView(
        envelope=envelope,
        policy_ref=policy_ref,
        information_contract_ref=contract_ref,
        decision_epoch=decision_epoch,
        current_policy_memory_payload_hash=memory_hash,
        visible_field_records=field_records,
        visible_object_refs=(),
        information_view_hash=information_view_hash,
    )
    capability = _new_capability(
        authorization_validation_ref=_validation_ref(
            "authorization-validation",
            canonical_payload,
            contract_ref,
        ),
        configuration_ref_or_not_applicable=Applicability.NOT_APPLICABLE,
        binding_ref_or_not_applicable=Applicability.NOT_APPLICABLE,
        information_contract_ref=contract_ref,
        visible_field_refs=all_refs,
        permitted_read_refs=all_refs,
        available_at=max(item[2] for item in fabricated_fields),
        maximum_age_microseconds=maximum_age,
        current_memory_ref_or_not_applicable=current_memory,
        traversal_allowed=False,
        capability_class=CapabilityClass.T1,
    )
    return view, capability


_DEPENDENCY_SENTINELS = (
    _PRIVATE_CAPABILITY_TOKEN,
    _observation.Measurement,
    _experiment.ExperimentConfiguration,
)


__all__ = (
    "CapabilityClass",
    "AccessCapability",
    "build_synthetic_information_view",
)
