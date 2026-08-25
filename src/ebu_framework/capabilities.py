"""Synthetic T1 information views and non-reconstructible access capabilities."""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timezone
from enum import StrEnum
import hashlib
import re
from typing import Literal, NoReturn

from . import authorization as _authorization
from . import policy as _policy
from . import observation as _observation
from . import experiment as _experiment
from . import hashing as _hashing
from . import identity as _identity
from .errors import (
    Applicability,
    FailureCode,
    FailureInterfaceRef,
    FailureStage,
    FrameworkError,
    RetryClass,
    ScientificStatusEffect,
    _fail,
    _i4_fail,
)


InformationContract = _policy.InformationContract
InformationView = _policy.InformationView
InformationReadSet = _policy.InformationReadSet
CanonicalBytes = _policy.CanonicalBytes
ObjectRef = _identity.ObjectRef
SourceFileRawSha256 = _identity.SourceFileRawSha256

_UTC_RE = re.compile(
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6}Z",
    re.ASCII,
)
_PRIVATE_CAPABILITY_TOKEN = object()
_ISSUED_CAPABILITY_IDS: set[int] = set()
_ISSUED_CAPABILITIES: list[object] = []
_T2_FIXTURE_PATH = "tests/framework/fixtures/bridge_m1_m9_v1.json"
_T2_FIXTURE_RAW_SHA256 = _identity.SourceFileRawSha256(
    "sha256-raw:8768b2f976b3b928b90c3b6d4b6d141de75fd5873fb52d61048748bf054779af"
)
_T2_CASE_IDS = ("M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9")
_T2_INTERFACES = (
    "classify_joint_groups_fixture",
    "compute_group_measurement_fixture",
    "compute_same_baseline_nonadditivity_fixture",
    "compute_comparator_interaction_fixture",
)
_I7_T2_FIXTURE_PATH = "tests/framework/fixtures/dynamic_static_v1.json"
_I7_T2_FIXTURE_RAW_SHA256 = _identity.SourceFileRawSha256(
    "sha256-raw:cacb79a4b52eb714b79424524c12cba9f8a4d2327abe99c2b76260c4621a898d"
)
_I7_T2_CASE_IDS = ("DC1", "DC2", "DC3", "DC4", "DC5", "DC6")
_I7_T2_INTERFACE = "validate_dynamic_static_identity"
_T2_ALLOWLIST = tuple(
    (
        _T2_FIXTURE_PATH,
        _T2_FIXTURE_RAW_SHA256,
        case_id,
        interface,
    )
    for case_id in _T2_CASE_IDS
    for interface in _T2_INTERFACES
) + tuple(
    (
        _I7_T2_FIXTURE_PATH,
        _I7_T2_FIXTURE_RAW_SHA256,
        case_id,
        _I7_T2_INTERFACE,
    )
    for case_id in _I7_T2_CASE_IDS
)
_T2_CASE_IDS = _T2_CASE_IDS + _I7_T2_CASE_IDS
_T2_INTERFACES = _T2_INTERFACES + (_I7_T2_INTERFACE,)
_ISSUED_T2_CAPABILITY_IDS: set[int] = set()
_ISSUED_T2_CAPABILITY_NONCES: dict[int, object] = {}
_ISSUED_T2_CAPABILITY_ROWS: dict[int, tuple[object, ...]] = {}
_ISSUED_T2_CAPABILITIES: list[object] = []


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


@dataclass(
    frozen=True,
    slots=True,
    eq=False,
    order=False,
    unsafe_hash=False,
    init=False,
)
class T2FixtureCapability:
    fixture_path: str
    fixture_raw_sha256: SourceFileRawSha256
    case_id: Literal[
        "M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9",
        "DC1", "DC2", "DC3", "DC4", "DC5", "DC6",
    ]
    authorized_interface: Literal[
        "classify_joint_groups_fixture",
        "compute_group_measurement_fixture",
        "compute_same_baseline_nonadditivity_fixture",
        "compute_comparator_interaction_fixture",
        "validate_dynamic_static_identity",
    ]
    capability_class: CapabilityClass
    issuance_nonce: object

    def _authorized_failure(self, code: FailureCode) -> NoReturn:
        try:
            interface = object.__getattribute__(self, "authorized_interface")
        except AttributeError:
            interface = "T2FixtureCapability"
        if interface == _I7_T2_INTERFACE:
            _i7_fixture_failure(code, interface)
        if type(interface) is str and interface in _T2_INTERFACES:
            _t2_fixture_failure(code, interface)
        _t2_failure(code, "T2FixtureCapability")

    def __getattribute__(self, name: str) -> object:
        if name != "__class__":
            object.__getattribute__(self, "_authorized_failure")(
                FailureCode.CAPABILITY_ESCALATION_FORBIDDEN
            )
        return object.__getattribute__(self, name)

    def __init__(self, *args: object, **kwargs: object) -> None:
        del args
        interface = kwargs.get("authorized_interface")
        if interface == _I7_T2_INTERFACE:
            _i7_fixture_failure(
                FailureCode.CAPABILITY_ESCALATION_FORBIDDEN,
                interface,
            )
        if type(interface) is str and interface in _T2_INTERFACES:
            _t2_fixture_failure(
                FailureCode.CAPABILITY_ESCALATION_FORBIDDEN,
                interface,
            )
        _t2_failure(
            FailureCode.CAPABILITY_ESCALATION_FORBIDDEN,
            "T2FixtureCapability",
        )

    def __init_subclass__(cls, **kwargs: object) -> None:
        del kwargs
        _t2_failure(
            FailureCode.CAPABILITY_ESCALATION_FORBIDDEN,
            "T2FixtureCapability",
        )

    def __copy__(self) -> NoReturn:
        object.__getattribute__(self, "_authorized_failure")(
            FailureCode.CAPABILITY_ESCALATION_FORBIDDEN
        )

    def __deepcopy__(self, memo: object) -> NoReturn:
        del memo
        object.__getattribute__(self, "_authorized_failure")(
            FailureCode.CAPABILITY_ESCALATION_FORBIDDEN
        )

    def __reduce__(self) -> NoReturn:
        object.__getattribute__(self, "_authorized_failure")(
            FailureCode.CAPABILITY_ESCALATION_FORBIDDEN
        )

    def __reduce_ex__(self, protocol: object) -> NoReturn:
        del protocol
        object.__getattribute__(self, "_authorized_failure")(
            FailureCode.CAPABILITY_ESCALATION_FORBIDDEN
        )


def _t2_failure(code: FailureCode, interface: str) -> NoReturn:
    _fail(
        code,
        f"{interface} rejected {code.value}",
        stage=FailureStage.I6,
        interface_ref=FailureInterfaceRef(
            "ebu_framework.capabilities", interface, "1.0.0"
        ),
        scientific_status_effect=ScientificStatusEffect.UNSTARTED_PRESERVED,
        retry_class=RetryClass.FORBIDDEN,
    )


def _t2_fixture_failure(code: FailureCode, interface: str) -> NoReturn:
    _fail(
        code,
        f"{interface} rejected {code.value}",
        stage=FailureStage.I6,
        interface_ref=FailureInterfaceRef(
            "ebu_framework.bridge", interface, "1.0.0"
        ),
        scientific_status_effect=ScientificStatusEffect.UNSTARTED_PRESERVED,
        retry_class=RetryClass.FORBIDDEN,
    )


def _i7_capability_failure(code: FailureCode, interface: str) -> NoReturn:
    _fail(
        code,
        f"{interface} rejected {code.value}",
        stage=FailureStage.I7,
        interface_ref=FailureInterfaceRef(
            "ebu_framework.capabilities", interface, "1.0.0"
        ),
        scientific_status_effect=ScientificStatusEffect.UNSTARTED_PRESERVED,
        retry_class=RetryClass.FORBIDDEN,
    )


def _i7_fixture_failure(code: FailureCode, interface: str) -> NoReturn:
    _fail(
        code,
        f"{interface} rejected {code.value}",
        stage=FailureStage.I7,
        interface_ref=FailureInterfaceRef(
            "ebu_framework.dynamic", interface, "1.0.0"
        ),
        scientific_status_effect=ScientificStatusEffect.UNSTARTED_PRESERVED,
        retry_class=RetryClass.FORBIDDEN,
    )


def _issue_t2_fixture_capability(
    *,
    fixture_path: str,
    fixture_raw_sha256: SourceFileRawSha256,
    case_id: Literal[
        "M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9",
        "DC1", "DC2", "DC3", "DC4", "DC5", "DC6",
    ],
    authorized_interface: Literal[
        "classify_joint_groups_fixture",
        "compute_group_measurement_fixture",
        "compute_same_baseline_nonadditivity_fixture",
        "compute_comparator_interaction_fixture",
        "validate_dynamic_static_identity",
    ],
) -> T2FixtureCapability:
    i7_attempt = (
        fixture_path == _I7_T2_FIXTURE_PATH
        or case_id in _I7_T2_CASE_IDS
        or authorized_interface == _I7_T2_INTERFACE
    )
    if not (
        type(fixture_path) is str
        and type(fixture_raw_sha256) is _identity.SourceFileRawSha256
        and type(case_id) is str
        and case_id in _T2_CASE_IDS
        and type(authorized_interface) is str
        and authorized_interface in _T2_INTERFACES
    ):
        if i7_attempt:
            _i7_capability_failure(
                FailureCode.CAPABILITY_ESCALATION_FORBIDDEN,
                "_issue_t2_fixture_capability",
            )
        _t2_failure(
            FailureCode.CAPABILITY_ESCALATION_FORBIDDEN,
            "_issue_t2_fixture_capability",
        )
    expected_path = _I7_T2_FIXTURE_PATH if i7_attempt else _T2_FIXTURE_PATH
    expected_hash = (
        _I7_T2_FIXTURE_RAW_SHA256 if i7_attempt else _T2_FIXTURE_RAW_SHA256
    )
    if fixture_path != expected_path:
        if i7_attempt:
            _i7_capability_failure(
                FailureCode.CAPABILITY_ESCALATION_FORBIDDEN,
                "_issue_t2_fixture_capability",
            )
        _t2_fixture_failure(
            FailureCode.CAPABILITY_ESCALATION_FORBIDDEN,
            authorized_interface,
        )
    if fixture_raw_sha256 != expected_hash:
        if i7_attempt:
            _i7_capability_failure(
                FailureCode.HASH_MISMATCH,
                "_issue_t2_fixture_capability",
            )
        _t2_fixture_failure(FailureCode.HASH_MISMATCH, authorized_interface)
    if (
        fixture_path,
        fixture_raw_sha256,
        case_id,
        authorized_interface,
    ) not in _T2_ALLOWLIST:
        if i7_attempt:
            _i7_capability_failure(
                FailureCode.CAPABILITY_ESCALATION_FORBIDDEN,
                "_issue_t2_fixture_capability",
            )
        _t2_failure(
            FailureCode.CAPABILITY_ESCALATION_FORBIDDEN,
            "_issue_t2_fixture_capability",
        )

    capability = object.__new__(T2FixtureCapability)
    nonce = object()
    for name, value in (
        ("fixture_path", fixture_path),
        ("fixture_raw_sha256", fixture_raw_sha256),
        ("case_id", case_id),
        ("authorized_interface", authorized_interface),
        ("capability_class", CapabilityClass.T2),
        ("issuance_nonce", nonce),
    ):
        object.__setattr__(capability, name, value)
    _ISSUED_T2_CAPABILITY_IDS.add(id(capability))
    _ISSUED_T2_CAPABILITY_NONCES[id(capability)] = nonce
    _ISSUED_T2_CAPABILITY_ROWS[id(capability)] = (
        fixture_path,
        fixture_raw_sha256,
        case_id,
        authorized_interface,
        CapabilityClass.T2,
        nonce,
    )
    _ISSUED_T2_CAPABILITIES.append(capability)
    return capability


def _consume_t2_fixture_capability(
    capability: T2FixtureCapability,
    interface: Literal[
        "classify_joint_groups_fixture",
        "compute_group_measurement_fixture",
        "compute_same_baseline_nonadditivity_fixture",
        "compute_comparator_interaction_fixture",
        "validate_dynamic_static_identity",
    ],
    case_id: Literal[
        "M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9",
        "DC1", "DC2", "DC3", "DC4", "DC5", "DC6",
    ],
    /,
) -> None:
    i7_attempt = interface == _I7_T2_INTERFACE or case_id in _I7_T2_CASE_IDS
    if not (
        type(capability) is T2FixtureCapability
        and type(interface) is str
        and interface in _T2_INTERFACES
        and type(case_id) is str
        and case_id in _T2_CASE_IDS
        and id(capability) in _ISSUED_T2_CAPABILITY_IDS
    ):
        if i7_attempt:
            _i7_fixture_failure(
                FailureCode.CAPABILITY_ESCALATION_FORBIDDEN,
                _I7_T2_INTERFACE,
            )
        if type(interface) is str and interface in _T2_INTERFACES:
            _t2_fixture_failure(
                FailureCode.CAPABILITY_ESCALATION_FORBIDDEN,
                interface,
            )
        _t2_failure(
            FailureCode.CAPABILITY_ESCALATION_FORBIDDEN,
            "_consume_t2_fixture_capability",
        )
    nonce = object.__getattribute__(capability, "issuance_nonce")
    fixture_path = object.__getattribute__(capability, "fixture_path")
    fixture_raw_sha256 = object.__getattribute__(
        capability, "fixture_raw_sha256"
    )
    if not (
        _ISSUED_T2_CAPABILITY_NONCES.get(id(capability)) is nonce
        and _ISSUED_T2_CAPABILITY_ROWS.get(id(capability))
        == (
            fixture_path,
            fixture_raw_sha256,
            case_id,
            interface,
            CapabilityClass.T2,
            nonce,
        )
        and (
            fixture_path,
            fixture_raw_sha256,
            case_id,
            interface,
        ) in _T2_ALLOWLIST
        and object.__getattribute__(capability, "case_id") == case_id
        and object.__getattribute__(capability, "authorized_interface") == interface
        and object.__getattribute__(capability, "capability_class")
        is CapabilityClass.T2
    ):
        if i7_attempt:
            _i7_fixture_failure(
                FailureCode.CAPABILITY_ESCALATION_FORBIDDEN,
                _I7_T2_INTERFACE,
            )
        _t2_fixture_failure(
            FailureCode.CAPABILITY_ESCALATION_FORBIDDEN,
            interface,
        )
    _ISSUED_T2_CAPABILITY_IDS.remove(id(capability))
    del _ISSUED_T2_CAPABILITY_NONCES[id(capability)]
    del _ISSUED_T2_CAPABILITY_ROWS[id(capability)]
    return None


_DEPENDENCY_SENTINELS = (
    _PRIVATE_CAPABILITY_TOKEN,
    _observation.Measurement,
    _experiment.ExperimentConfiguration,
)


__all__ = (
    "CapabilityClass",
    "AccessCapability",
    "build_synthetic_information_view",
    "T2FixtureCapability",
)
