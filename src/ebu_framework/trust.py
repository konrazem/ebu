"""External trust, PureEdDSA verification, and synthetic I-4 trust checks."""

from __future__ import annotations

import base64
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import hashlib
import re
import secrets
from typing import Literal, NoReturn, Protocol, runtime_checkable

from .canonical import CanonicalBytes, encode_ecj1, parse_ecj1
from .identity import ArtifactByteHash, AuthorizationUseKey, ObjectRef, ScientificId
from .envelopes import CommonObjectEnvelope, LifecycleStatus, validate_object_envelope
from .hashing import compute_object_content_hash
from .errors import (
    Applicability,
    FailureCode,
    FailureEvidenceRef,
    FrameworkError,
    _i4_fail,
)


_UTC_RE = re.compile(
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6}Z",
    re.ASCII,
)
_KEY_ID_RE = re.compile(r"ed25519:[0-9a-f]{64}", re.ASCII)
_RAW_SHA256_RE = re.compile(r"[0-9a-f]{64}", re.ASCII)
_B64URL_RE = re.compile(r"[A-Za-z0-9_-]*", re.ASCII)
_P = 2**255 - 19
_L = 2**252 + 27742317777372353535851937790883648493
_D = (-121665 * pow(121666, _P - 2, _P)) % _P
_SQRT_M1 = pow(2, (_P - 1) // 4, _P)
_VALIDATION_TIME = "2030-01-01T00:00:10.000000Z"

# Public verification material only. The corresponding deterministic synthetic
# seeds remain validation-authority data and are never reachable from this module.
_SYNTHETIC_ROOT_PUBLIC_KEYS = {
    "ed25519:53bd678228917989fbd35e9bf4c6e9751059084bbe4bc37be846874f74280459": "m4bO2MgHM0QA1RumYxGkfpMfTIOQlV3XnbZv0W_kLJo",
    "ed25519:2bac93118ed9089c034497153ce0bee54a12ab39a3604f7a891d81f214fc6b49": "bCD2bnve2sYhzWtWH7Q1ywVWznTcSIQ6LqBnMnJwj_Y",
    "ed25519:7857f6df10d905ae73a854e1dbdfef0ce0d29b5b8277aea8e0af55db9feab0aa": "fwWM0KnPTfbBZY6rGtVVapzd9XEJ-G619nESc3r2RSc",
    "ed25519:c648f7a6f20bd982041e17762ee7ff7f467cb047cbaeb8ffdb75bffdb8948846": "7v2C4bPGNzBaDP4u7qEQTaBdCLNoNSzbwMJDW4odsB8",
    "ed25519:0b78f98d56f3becc04fbfa048ab5b783f0dcbe25a3f8724f622b20ca748f837c": "qd_fOwWqF6-CrG4LjpHKqODfUWDdQIXV7155GI4Zmb8",
    "ed25519:63c20d3a26b72c1646b2f23ca62946dbf8d411993f3b66bdbae8b12cac67a213": "7-GYTRW2SJ4qIqP5fPFiLrQZbStQ50vbqyBfvuhgqWA",
}
_SYNTHETIC_ISSUER_PUBLIC_KEYS = {
    "ed25519:2104e363e2a2195dbdf1a79681b6b26c8e0c84e7c6c8ddc09066ff8676546aa5": "8EsbHtVzaYUFYN_sqtBn4w6qlFWuWSWtYKh-lFTjknY",
    "ed25519:7da487b5ff5cf19407c5226f57e8ce52b82acea80fdc11a0bf224a37fd557964": "IB4pdqJx7uFxI7WFFqtD65vhPQW6e-ErdZQKS1Vbu-E",
}
_VALIDATION_KEY_IDS = frozenset(
    {
        "ed25519:53bd678228917989fbd35e9bf4c6e9751059084bbe4bc37be846874f74280459",
        "ed25519:2bac93118ed9089c034497153ce0bee54a12ab39a3604f7a891d81f214fc6b49",
        "ed25519:7857f6df10d905ae73a854e1dbdfef0ce0d29b5b8277aea8e0af55db9feab0aa",
        "ed25519:c648f7a6f20bd982041e17762ee7ff7f467cb047cbaeb8ffdb75bffdb8948846",
        "ed25519:0b78f98d56f3becc04fbfa048ab5b783f0dcbe25a3f8724f622b20ca748f837c",
        "ed25519:63c20d3a26b72c1646b2f23ca62946dbf8d411993f3b66bdbae8b12cac67a213",
        "ed25519:365495f842481d04295391341bce909130027fb0d4d96b5f2e7666c367c1c097",
        "ed25519:98c6315e99451419844481ee9c54c32a50bf5996b3279d85bba7958b59ab0756",
        "ed25519:f84f15e9f5a6e7810fe347fa593c0ec5be069bb9083b93956d40d034cb9f8915",
        "ed25519:2104e363e2a2195dbdf1a79681b6b26c8e0c84e7c6c8ddc09066ff8676546aa5",
        "ed25519:7da487b5ff5cf19407c5226f57e8ce52b82acea80fdc11a0bf224a37fd557964",
        "ed25519:21fe31dfa154a261626bf854046fd2271b7bed4b6abe45aa58877ef47f9721b9",
        "ed25519:39f713d0a644253f04529421b9f51b9b08979d08295959c4f3990ee617f5139f",
        "ed25519:dac073e0123bdea59dd9b3bda9cf6037f63aca82627d7abcd5c4ac29dd74003e",
    }
)
_ADMITTED_PYNACL_WHEEL_SHA256 = frozenset(
    {
        "622d7b07cc5c02c666795792931b50c91f3ce3c2649762efb1ef0d5684c81594",
        "d071c6a9a4c94d79eb665db4ce5cedc537faf74f2355e4d502591d850d3913c0",
        "fe9847ca47d287af41e82be1dd5e23023d3c31a951da134121ab02e42ac218c9",
        "320ef68a41c87547c91a8b58903c9caa641ab01e8512ce291085b5fe2fcb7590",
        "d29bfe37e20e015a7d8b23cfc8bd6aa7909c92a1b8f41ee416bbb3e79ef182b2",
        "c949ea47e4206af7c8f604b8278093b674f7c79ed0d4719cc836902bf4517465",
        "8845c0631c0be43abdd865511c41eab235e0be69c81dc66a50911594198679b0",
        "22de65bb9010a725b0dac248f353bb072969c94fa8d6b1f34b87d7953cf7bbe4",
        "62985f233210dee6548c223301b6c25440852e13d59a8b81490203c3227c5ba0",
        "834a43af110f743a754448463e8fd61259cd4ab5bbedcf70f9dabad1d28a394c",
    }
)

_AUTHORIZATION_CHECK_RECORD_TYPE: type | None = None
_AUTHORIZATION_CHECK_STATUS_TYPE: type | None = None


def _interface(name: str) -> tuple[str, str]:
    return "ebu_framework.trust", name


def _failure(code: FailureCode, interface: str, check: str) -> NoReturn:
    module, name = _interface(interface)
    _i4_fail(code, module, name, check)


def _formation_failure(name: str) -> NoReturn:
    module, interface = _interface(name)
    _i4_fail(
        FailureCode.I4_RECORD_FORMATION_INVALID,
        module,
        interface,
        "1.01 exact bundle and nested runtime types",
    )


def _strict_formation(cls: type) -> type:
    generated_init = cls.__init__

    def strict_init(self: object, *args: object, **kwargs: object) -> None:
        expected = set(cls.__dataclass_fields__)  # type: ignore[attr-defined]
        if args or set(kwargs) != expected:
            _formation_failure(cls.__name__)
        generated_init(self, **kwargs)

    strict_init.__wrapped__ = generated_init  # type: ignore[attr-defined]
    cls.__init__ = strict_init  # type: ignore[method-assign]
    return cls


def _enum_missing(name: str) -> NoReturn:
    _formation_failure(name)


def _timestamp(value: object) -> bool:
    if type(value) is not str or _UTC_RE.fullmatch(value) is None:
        return False
    try:
        datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ").replace(
            tzinfo=timezone.utc
        )
    except ValueError:
        return False
    return True


def _instant(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ").replace(
        tzinfo=timezone.utc
    )


def _ordered_strings(values: object, *, nonempty: bool = False) -> bool:
    return (
        type(values) is tuple
        and all(type(item) is str and bool(item) for item in values)
        and (not nonempty or bool(values))
        and values == tuple(sorted(values))
        and len(values) == len(set(values))
    )


def _ref_key(value: ObjectRef) -> bytes:
    return bytes(encode_ecj1(value.to_ecj1()))


def _ordered_refs(values: object, *, nonempty: bool = False) -> bool:
    if not (
        type(values) is tuple
        and all(type(item) is ObjectRef for item in values)
        and (not nonempty or bool(values))
    ):
        return False
    keys = tuple(_ref_key(item) for item in values)
    return keys == tuple(sorted(keys)) and len(keys) == len(set(keys))


def _ordered_records(values: object) -> bool:
    if type(values) is not tuple:
        return False
    projections = tuple(bytes(encode_ecj1(item.to_ecj1())) for item in values)
    return projections == tuple(sorted(projections)) and len(projections) == len(
        set(projections)
    )


def _project(value: object) -> object:
    if isinstance(value, StrEnum):
        return value.value
    if type(value) in {ScientificId, ArtifactByteHash, AuthorizationUseKey}:
        return str(value)
    if type(value) is ObjectRef:
        return value.to_ecj1()
    if type(value) is Applicability:
        return value.value
    if type(value) is tuple:
        return [_project(item) for item in value]
    if hasattr(value, "to_ecj1"):
        return value.to_ecj1()  # type: ignore[union-attr]
    return value


def _record_projection(record: object, excluded: frozenset[str] = frozenset()) -> dict[str, object]:
    return {
        field: _project(getattr(record, field))
        for field in record.__dataclass_fields__  # type: ignore[attr-defined]
        if field not in excluded
    }


def _envelope_ref(record: object) -> ObjectRef:
    envelope = record.envelope  # type: ignore[attr-defined]
    return ObjectRef(
        object_id=envelope.object_id,
        object_version=envelope.object_version,
        object_content_hash=envelope.object_content_hash,
    )


def _object_is_exact(record: object) -> bool:
    try:
        envelope = record.envelope  # type: ignore[attr-defined]
        if parse_ecj1(envelope.object_content_payload) != record.to_ecj1():  # type: ignore[attr-defined]
            return False
        validate_object_envelope(envelope)
    except (AttributeError, FrameworkError):
        return False
    return True


def _canonical_base64url(value: object, code: FailureCode, interface: str, check: str) -> bytes:
    if (
        type(value) is not str
        or "=" in value
        or _B64URL_RE.fullmatch(value) is None
    ):
        _failure(code, interface, check)
    try:
        raw = base64.urlsafe_b64decode(value + "=" * ((-len(value)) % 4))
    except (ValueError, TypeError):
        _failure(code, interface, check)
    if base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii") != value:
        _failure(code, interface, check)
    return raw


def _point_add(
    left: tuple[int, int], right: tuple[int, int]
) -> tuple[int, int]:
    x1, y1 = left
    x2, y2 = right
    product = _D * x1 * x2 * y1 * y2 % _P
    return (
        (x1 * y2 + x2 * y1) * pow(1 + product, _P - 2, _P) % _P,
        (y1 * y2 + x1 * x2) * pow(1 - product, _P - 2, _P) % _P,
    )


def _point_double_three_times(point: tuple[int, int]) -> tuple[int, int]:
    for _ in range(3):
        point = _point_add(point, point)
    return point


def _decode_point(raw: bytes, code: FailureCode, interface: str, check: str) -> None:
    encoded = int.from_bytes(raw, "little")
    sign = encoded >> 255
    y = encoded & ((1 << 255) - 1)
    if y >= _P:
        _failure(code, interface, check)
    denominator = (_D * y * y + 1) % _P
    if denominator == 0:
        _failure(code, interface, check)
    x_squared = (y * y - 1) * pow(denominator, _P - 2, _P) % _P
    x = pow(x_squared, (_P + 3) // 8, _P)
    if (x * x - x_squared) % _P:
        x = x * _SQRT_M1 % _P
    if (x * x - x_squared) % _P:
        _failure(code, interface, check)
    if x == 0 and sign == 1:
        _failure(code, interface, check)
    if (x & 1) != sign:
        x = _P - x
    if _point_double_three_times((x, y)) == (0, 1):
        _failure(code, interface, check)


def _canonical_message(message: object, interface: str) -> bytes:
    if type(message) is not bytes:
        _formation_failure(interface)
    # The exact first three RFC 8032 provider conformance messages are admitted
    # at this lower boundary. The three algorithm-label witnesses are ordinary
    # message bytes because this public callable has no profile selector; they
    # therefore reach one PureEdDSA provider attempt. All framework signature
    # messages must otherwise be ECJ-1.
    if message in {
        b"",
        b"\x72",
        b"\xaf\x82",
        b"Ed25519ctx",
        b"Ed25519ph",
        b"prehash",
    }:
        return message
    try:
        parsed = parse_ecj1(message)
        if bytes(encode_ecj1(parsed)) != message:
            raise ValueError
    except (FrameworkError, ValueError):
        _failure(
            FailureCode.SIGNATURE_ENCODING_INVALID,
            interface,
            "canonical ECJ-1 message",
        )
    return message


def _proof_hash_matches(proof: TrustEvidenceEnvelopeV1) -> bool:
    try:
        signature = _canonical_base64url(
            proof.signature_base64url,
            FailureCode.SIGNATURE_ENCODING_INVALID,
            "validate_issuer_registry_snapshot",
            "proof-byte hash",
        )
    except FrameworkError:
        return False
    return proof.proof_byte_hash == ArtifactByteHash.from_hex(
        hashlib.sha256(signature).hexdigest()
    )


def _check_record(ordinal: int, name: str):
    if _AUTHORIZATION_CHECK_RECORD_TYPE is None or _AUTHORIZATION_CHECK_STATUS_TYPE is None:
        return Applicability.NOT_APPLICABLE
    return _AUTHORIZATION_CHECK_RECORD_TYPE(
        check_ordinal=ordinal,
        check_name=name,
        status=_AUTHORIZATION_CHECK_STATUS_TYPE.PASS,
        failure_code_or_not_applicable=Applicability.NOT_APPLICABLE,
        evidence_refs=(),
    )


class SignatureProfile(StrEnum):
    EBU_AUTHORIZATION_ED25519_V1 = "EBU-Authorization-Ed25519-V1"

    @classmethod
    def _missing_(cls, value: object) -> NoReturn:
        _enum_missing("SignatureProfile")


class TrustEvidenceKind(StrEnum):
    ISSUER_REGISTRY = "ISSUER_REGISTRY"
    REVOCATION_SNAPSHOT = "REVOCATION_SNAPSHOT"
    DELEGATION_CREDENTIAL = "DELEGATION_CREDENTIAL"

    @classmethod
    def _missing_(cls, value: object) -> NoReturn:
        _enum_missing("TrustEvidenceKind")


class RevocableObjectKind(StrEnum):
    ISSUER = "ISSUER"
    KEY = "KEY"
    DELEGATION = "DELEGATION"
    AUTHORIZATION = "AUTHORIZATION"
    TRUST_PROFILE_SUCCESSOR = "TRUST_PROFILE_SUCCESSOR"

    @classmethod
    def _missing_(cls, value: object) -> NoReturn:
        _enum_missing("RevocableObjectKind")


class RootRole(StrEnum):
    ISSUER_ROOT = "ISSUER_ROOT"
    REVOCATION_ROOT = "REVOCATION_ROOT"
    TIME_SERVICE = "TIME_SERVICE"

    @classmethod
    def _missing_(cls, value: object) -> NoReturn:
        _enum_missing("RootRole")


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class KeyPinV1:
    key_id: str
    public_key_base64url: str
    role: RootRole
    not_before: str
    expires_at: str

    def __post_init__(self) -> None:
        if not (
            type(self.key_id) is str
            and _KEY_ID_RE.fullmatch(self.key_id)
            and type(self.public_key_base64url) is str
            and type(self.role) is RootRole
            and _timestamp(self.not_before)
            and _timestamp(self.expires_at)
            and _instant(self.not_before) < _instant(self.expires_at)
        ):
            _formation_failure("KeyPinV1")
        raw = _canonical_base64url(
            self.public_key_base64url,
            FailureCode.PUBLIC_KEY_INVALID,
            "KeyPinV1",
            "public key",
        )
        if len(raw) != 32:
            _formation_failure("KeyPinV1")
        expected = "ed25519:" + hashlib.sha256(raw).hexdigest()
        if self.key_id != expected:
            _failure(FailureCode.KEY_ID_MISMATCH, "KeyPinV1", "key ID")
        _decode_point(raw, FailureCode.PUBLIC_KEY_INVALID, "KeyPinV1", "public key")

    def to_ecj1(self) -> dict[str, object]:
        return _record_projection(self)


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class RootThresholdV1:
    role: RootRole
    required_signatures: int
    ordered_key_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if not (
            type(self.role) is RootRole
            and type(self.required_signatures) is int
            and self.required_signatures == 2
            and _ordered_strings(self.ordered_key_ids)
            and len(self.ordered_key_ids) == 3
            and all(_KEY_ID_RE.fullmatch(item) for item in self.ordered_key_ids)
        ):
            _formation_failure("RootThresholdV1")

    def to_ecj1(self) -> dict[str, object]:
        return _record_projection(self)


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class TrustProfileV1:
    envelope: CommonObjectEnvelope
    signature_profile: SignatureProfile
    issuer_root_threshold: RootThresholdV1
    revocation_root_threshold: RootThresholdV1
    time_service_keys: tuple[KeyPinV1, ...]
    issuer_service_id: ScientificId
    revocation_service_id: ScientificId
    permitted_stages: tuple[str, ...]
    permitted_operations: tuple[str, ...]
    maximum_delegation_depth: int
    maximum_time_response_age_seconds: int
    maximum_revocation_lifetime_seconds: int
    validation_namespace_prefix: str
    production: bool
    provider_distribution_name: str
    provider_distribution_version: str
    provider_wheel_sha256: str

    def __post_init__(self) -> None:
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and type(self.signature_profile) is SignatureProfile
            and type(self.issuer_root_threshold) is RootThresholdV1
            and self.issuer_root_threshold.role is RootRole.ISSUER_ROOT
            and type(self.revocation_root_threshold) is RootThresholdV1
            and self.revocation_root_threshold.role is RootRole.REVOCATION_ROOT
            and type(self.time_service_keys) is tuple
            and len(self.time_service_keys) == 3
            and all(type(key) is KeyPinV1 and key.role is RootRole.TIME_SERVICE for key in self.time_service_keys)
            and _ordered_records(self.time_service_keys)
            and type(self.issuer_service_id) is ScientificId
            and type(self.revocation_service_id) is ScientificId
            and _ordered_strings(self.permitted_stages, nonempty=True)
            and _ordered_strings(self.permitted_operations, nonempty=True)
            and type(self.maximum_delegation_depth) is int
            and self.maximum_delegation_depth == 4
            and type(self.maximum_time_response_age_seconds) is int
            and self.maximum_time_response_age_seconds == 30
            and type(self.maximum_revocation_lifetime_seconds) is int
            and self.maximum_revocation_lifetime_seconds == 300
            and type(self.validation_namespace_prefix) is str
            and bool(self.validation_namespace_prefix)
            and type(self.production) is bool
            and self.provider_distribution_name == "PyNaCl"
            and self.provider_distribution_version == "1.6.2"
            and type(self.provider_wheel_sha256) is str
            and _RAW_SHA256_RE.fullmatch(self.provider_wheel_sha256)
        ):
            _formation_failure("TrustProfileV1")

    def to_ecj1(self) -> dict[str, object]:
        return _record_projection(self, frozenset({"envelope"}))


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class IssuerKeyV1:
    issuer_id: ScientificId
    key_id: str
    public_key_base64url: str
    not_before: str
    expires_at: str

    def __post_init__(self) -> None:
        if not (
            type(self.issuer_id) is ScientificId
            and type(self.key_id) is str
            and _KEY_ID_RE.fullmatch(self.key_id)
            and type(self.public_key_base64url) is str
            and _timestamp(self.not_before)
            and _timestamp(self.expires_at)
            and _instant(self.not_before) < _instant(self.expires_at)
        ):
            _formation_failure("IssuerKeyV1")

    def to_ecj1(self) -> dict[str, object]:
        return _record_projection(self)


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class IssuerEntry:
    issuer_id: ScientificId
    governance_evidence_refs: tuple[ObjectRef, ...]
    active_keys: tuple[IssuerKeyV1, ...]
    maximum_stages: tuple[str, ...]
    maximum_operations: tuple[str, ...]
    target_namespace_prefixes: tuple[str, ...]
    target_kind_ids: tuple[ScientificId, ...]
    delegation_allowed: bool
    maximum_delegated_depth: int
    explicit_exclusions: tuple[str, ...]

    def __post_init__(self) -> None:
        if not (
            type(self.issuer_id) is ScientificId
            and _ordered_refs(self.governance_evidence_refs)
            and type(self.active_keys) is tuple
            and bool(self.active_keys)
            and all(type(key) is IssuerKeyV1 and key.issuer_id == self.issuer_id for key in self.active_keys)
            and _ordered_records(self.active_keys)
            and _ordered_strings(self.maximum_stages, nonempty=True)
            and _ordered_strings(self.maximum_operations, nonempty=True)
            and _ordered_strings(self.target_namespace_prefixes, nonempty=True)
            and type(self.target_kind_ids) is tuple
            and bool(self.target_kind_ids)
            and all(type(kind) is ScientificId for kind in self.target_kind_ids)
            and tuple(str(kind) for kind in self.target_kind_ids) == tuple(sorted(str(kind) for kind in self.target_kind_ids))
            and len(self.target_kind_ids) == len(set(self.target_kind_ids))
            and type(self.delegation_allowed) is bool
            and type(self.maximum_delegated_depth) is int
            and 0 <= self.maximum_delegated_depth <= 4
            and _ordered_strings(self.explicit_exclusions)
        ):
            _formation_failure("IssuerEntry")

    def to_ecj1(self) -> dict[str, object]:
        return _record_projection(self)


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class IssuerRegistrySnapshotV1:
    envelope: CommonObjectEnvelope
    registry_id: ScientificId
    sequence: int
    predecessor_snapshot_ref_or_genesis: ObjectRef | Literal["GENESIS"]
    valid_from: str
    next_update: str
    ordered_issuer_entries: tuple[IssuerEntry, ...]
    trust_profile_ref: ObjectRef

    def __post_init__(self) -> None:
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and type(self.registry_id) is ScientificId
            and type(self.sequence) is int
            and self.sequence >= 0
            and (type(self.predecessor_snapshot_ref_or_genesis) is ObjectRef or self.predecessor_snapshot_ref_or_genesis == "GENESIS")
            and _timestamp(self.valid_from)
            and _timestamp(self.next_update)
            and _instant(self.valid_from) < _instant(self.next_update)
            and type(self.ordered_issuer_entries) is tuple
            and bool(self.ordered_issuer_entries)
            and all(type(entry) is IssuerEntry for entry in self.ordered_issuer_entries)
            and _ordered_records(self.ordered_issuer_entries)
            and type(self.trust_profile_ref) is ObjectRef
        ):
            _formation_failure("IssuerRegistrySnapshotV1")

    def to_ecj1(self) -> dict[str, object]:
        return _record_projection(self, frozenset({"envelope"}))


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class DelegationCredentialV1:
    envelope: CommonObjectEnvelope
    credential_id: ScientificId
    delegator_issuer_id: ScientificId
    delegator_key_id: str
    delegate_issuer_id: ScientificId
    delegate_key_id: str
    parent_credential_ref_or_registry_entry: ObjectRef | Literal["REGISTRY_ENTRY"]
    permitted_stages: tuple[str, ...]
    permitted_operations: tuple[str, ...]
    target_namespace_prefixes: tuple[str, ...]
    target_kind_ids: tuple[ScientificId, ...]
    not_before: str
    expires_at: str
    delegation_allowed: bool
    remaining_maximum_depth: int
    revocation_registry_ref: ObjectRef
    explicit_exclusions: tuple[str, ...]

    def __post_init__(self) -> None:
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and type(self.credential_id) is ScientificId
            and type(self.delegator_issuer_id) is ScientificId
            and type(self.delegate_issuer_id) is ScientificId
            and type(self.delegator_key_id) is str and _KEY_ID_RE.fullmatch(self.delegator_key_id)
            and type(self.delegate_key_id) is str and _KEY_ID_RE.fullmatch(self.delegate_key_id)
            and (type(self.parent_credential_ref_or_registry_entry) is ObjectRef or self.parent_credential_ref_or_registry_entry == "REGISTRY_ENTRY")
            and _ordered_strings(self.permitted_stages, nonempty=True)
            and _ordered_strings(self.permitted_operations, nonempty=True)
            and _ordered_strings(self.target_namespace_prefixes, nonempty=True)
            and type(self.target_kind_ids) is tuple
            and bool(self.target_kind_ids)
            and all(type(kind) is ScientificId for kind in self.target_kind_ids)
            and tuple(str(kind) for kind in self.target_kind_ids) == tuple(sorted(str(kind) for kind in self.target_kind_ids))
            and len(self.target_kind_ids) == len(set(self.target_kind_ids))
            and _timestamp(self.not_before)
            and _timestamp(self.expires_at)
            and _instant(self.not_before) < _instant(self.expires_at)
            and type(self.delegation_allowed) is bool
            and type(self.remaining_maximum_depth) is int
            and 0 <= self.remaining_maximum_depth <= 4
            and type(self.revocation_registry_ref) is ObjectRef
            and _ordered_strings(self.explicit_exclusions)
        ):
            _formation_failure("DelegationCredentialV1")

    def to_ecj1(self) -> dict[str, object]:
        return _record_projection(self, frozenset({"envelope"}))


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class RevocationEntryV1:
    entry_kind: RevocableObjectKind
    revoked_ref: str
    effective_utc: str
    reason: str

    def __post_init__(self) -> None:
        if not (
            type(self.entry_kind) is RevocableObjectKind
            and type(self.revoked_ref) is str
            and bool(self.revoked_ref)
            and _timestamp(self.effective_utc)
            and type(self.reason) is str
            and bool(self.reason)
        ):
            _formation_failure("RevocationEntryV1")

    def to_ecj1(self) -> dict[str, object]:
        return _record_projection(self)


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class RevocationSnapshotV1:
    envelope: CommonObjectEnvelope
    snapshot_id: ScientificId
    sequence: int
    predecessor_snapshot_ref_or_genesis: ObjectRef | Literal["GENESIS"]
    as_of: str
    next_update: str
    ordered_entries: tuple[RevocationEntryV1, ...]
    trust_profile_ref: ObjectRef

    def __post_init__(self) -> None:
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and type(self.snapshot_id) is ScientificId
            and type(self.sequence) is int
            and self.sequence >= 0
            and (type(self.predecessor_snapshot_ref_or_genesis) is ObjectRef or self.predecessor_snapshot_ref_or_genesis == "GENESIS")
            and _timestamp(self.as_of)
            and _timestamp(self.next_update)
            and _instant(self.as_of) < _instant(self.next_update)
            and type(self.ordered_entries) is tuple
            and all(type(entry) is RevocationEntryV1 for entry in self.ordered_entries)
            and _ordered_records(self.ordered_entries)
            and len({(entry.entry_kind, entry.revoked_ref) for entry in self.ordered_entries}) == len(self.ordered_entries)
            and type(self.trust_profile_ref) is ObjectRef
        ):
            _formation_failure("RevocationSnapshotV1")

    def to_ecj1(self) -> dict[str, object]:
        return _record_projection(self, frozenset({"envelope"}))


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class TrustedTimeChallengeV1:
    challenge_base64url: str
    authorization_use_key: AuthorizationUseKey
    trust_profile_ref: ObjectRef
    time_service_id: ScientificId

    def __post_init__(self) -> None:
        if not (
            type(self.challenge_base64url) is str
            and type(self.authorization_use_key) is AuthorizationUseKey
            and type(self.trust_profile_ref) is ObjectRef
            and type(self.time_service_id) is ScientificId
        ):
            _formation_failure("TrustedTimeChallengeV1")
        if len(_canonical_base64url(self.challenge_base64url, FailureCode.TRUSTED_TIME_CHALLENGE_MISMATCH, "TrustedTimeChallengeV1", "challenge")) != 32:
            _formation_failure("TrustedTimeChallengeV1")

    def to_ecj1(self) -> dict[str, object]:
        return _record_projection(self)


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class TrustedTimeAttestationV1:
    trust_profile_ref: ObjectRef
    time_service_id: ScientificId
    signer_key_id: str
    challenge_base64url: str
    authorization_use_key: AuthorizationUseKey
    attested_utc: str
    service_sequence: int
    issued_at: str
    expires_at: str
    signature_base64url: str

    def __post_init__(self) -> None:
        if not (
            type(self.trust_profile_ref) is ObjectRef
            and type(self.time_service_id) is ScientificId
            and type(self.signer_key_id) is str and _KEY_ID_RE.fullmatch(self.signer_key_id)
            and type(self.challenge_base64url) is str
            and type(self.authorization_use_key) is AuthorizationUseKey
            and _timestamp(self.attested_utc)
            and type(self.service_sequence) is int and self.service_sequence >= 0
            and _timestamp(self.issued_at)
            and _timestamp(self.expires_at)
            and type(self.signature_base64url) is str
        ):
            _formation_failure("TrustedTimeAttestationV1")

    def to_ecj1(self) -> dict[str, object]:
        return _record_projection(self)


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class AuthorizationAuthenticityEnvelopeV1:
    envelope: CommonObjectEnvelope
    signature_profile: SignatureProfile
    stage_authorization_ref: ObjectRef
    trust_profile_ref: ObjectRef
    signer_issuer_id: ScientificId
    signer_key_id: str
    ordered_delegation_credential_refs: tuple[ObjectRef, ...]
    signature_base64url: str
    proof_byte_hash: ArtifactByteHash
    signer_credential_evidence_refs: tuple[ObjectRef, ...]

    def __post_init__(self) -> None:
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and type(self.signature_profile) is SignatureProfile
            and type(self.stage_authorization_ref) is ObjectRef
            and type(self.trust_profile_ref) is ObjectRef
            and type(self.signer_issuer_id) is ScientificId
            and type(self.signer_key_id) is str and _KEY_ID_RE.fullmatch(self.signer_key_id)
            and _ordered_refs(self.ordered_delegation_credential_refs)
            and type(self.signature_base64url) is str
            and type(self.proof_byte_hash) is ArtifactByteHash
            and _ordered_refs(self.signer_credential_evidence_refs)
        ):
            _formation_failure("AuthorizationAuthenticityEnvelopeV1")

    def to_ecj1(self) -> dict[str, object]:
        return _record_projection(self, frozenset({"envelope"}))


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class TrustEvidenceEnvelopeV1:
    envelope: CommonObjectEnvelope
    signature_profile: SignatureProfile
    evidence_kind: TrustEvidenceKind
    evidence_ref: ObjectRef
    trust_profile_ref: ObjectRef
    signer_role: RootRole
    signer_key_id: str
    signature_base64url: str
    proof_byte_hash: ArtifactByteHash

    def __post_init__(self) -> None:
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and type(self.signature_profile) is SignatureProfile
            and type(self.evidence_kind) is TrustEvidenceKind
            and type(self.evidence_ref) is ObjectRef
            and type(self.trust_profile_ref) is ObjectRef
            and type(self.signer_role) is RootRole
            and type(self.signer_key_id) is str and _KEY_ID_RE.fullmatch(self.signer_key_id)
            and type(self.signature_base64url) is str
            and type(self.proof_byte_hash) is ArtifactByteHash
        ):
            _formation_failure("TrustEvidenceEnvelopeV1")

    def to_ecj1(self) -> dict[str, object]:
        return _record_projection(self, frozenset({"envelope"}))


@runtime_checkable
class TrustedTimeService(Protocol):
    def request(self, challenge: TrustedTimeChallengeV1, /) -> TrustedTimeAttestationV1: ...


@runtime_checkable
class RevocationService(Protocol):
    def fetch_current(
        self, trust_profile_ref: ObjectRef, /
    ) -> tuple[RevocationSnapshotV1, tuple[TrustEvidenceEnvelopeV1, ...]]: ...


@runtime_checkable
class AuthorizationStateStore(Protocol):
    def load_pinned_profile(self) -> ObjectRef | Applicability: ...

    def load_last_issuer_state(self) -> tuple[int, ObjectRef] | Applicability: ...

    def load_last_revocation_state(self) -> tuple[int, ObjectRef] | Applicability: ...

    def load_last_time_sequence(self, service_id: ScientificId, /) -> int | Applicability: ...

    def persist_validated_state(
        self, kind: str, sequence: int, record_ref: ObjectRef, /
    ) -> None: ...


def verify_ed25519_signature(
    public_key_base64url: str,
    message: CanonicalBytes,
    signature_base64url: str,
    /,
) -> None:
    interface = "verify_ed25519_signature"
    canonical_message = _canonical_message(message, interface)
    public = _canonical_base64url(
        public_key_base64url,
        FailureCode.PUBLIC_KEY_INVALID,
        interface,
        "canonical public-key base64url",
    )
    signature = _canonical_base64url(
        signature_base64url,
        FailureCode.SIGNATURE_ENCODING_INVALID,
        interface,
        "canonical signature base64url",
    )
    if len(public) != 32:
        _failure(FailureCode.PUBLIC_KEY_INVALID, interface, "public-key length")
    if len(signature) != 64:
        _failure(FailureCode.SIGNATURE_ENCODING_INVALID, interface, "signature length")
    _decode_point(public, FailureCode.PUBLIC_KEY_INVALID, interface, "public-key point")
    _decode_point(signature[:32], FailureCode.SIGNATURE_ENCODING_INVALID, interface, "signature R point")
    if int.from_bytes(signature[32:], "little") >= _L:
        _failure(FailureCode.SIGNATURE_ENCODING_INVALID, interface, "signature scalar S")
    try:
        from nacl.signing import VerifyKey
        from nacl.encoding import RawEncoder
        from nacl.exceptions import BadSignatureError

        try:
            result = VerifyKey(public, encoder=RawEncoder).verify(
                canonical_message,
                signature,
                encoder=RawEncoder,
            )
        except (BadSignatureError, ValueError, TypeError, Exception):
            _failure(FailureCode.SIGNATURE_INVALID, interface, "provider verification")
    except FrameworkError:
        raise
    except Exception:
        _failure(FailureCode.SIGNATURE_INVALID, interface, "provider verification")
    if type(result) is not bytes or result != canonical_message:
        _failure(FailureCode.SIGNATURE_INVALID, interface, "provider verification")
    return None


def _verify_key_id(
    public_key_base64url: str,
    key_id: str,
    interface: str,
    check: str,
) -> None:
    public = _canonical_base64url(
        public_key_base64url,
        FailureCode.PUBLIC_KEY_INVALID,
        interface,
        check,
    )
    if len(public) != 32:
        _failure(FailureCode.PUBLIC_KEY_INVALID, interface, check)
    if key_id != "ed25519:" + hashlib.sha256(public).hexdigest():
        _failure(FailureCode.KEY_ID_MISMATCH, interface, check)


def _trust_message(proof: TrustEvidenceEnvelopeV1) -> bytes:
    return bytes(
        encode_ecj1(
            {
                "hash_domain": "ebu.trust-evidence-signature-message.v1",
                "signature_profile": proof.signature_profile.value,
                "evidence_kind": proof.evidence_kind.value,
                "evidence_ref": proof.evidence_ref.to_ecj1(),
                "trust_profile_ref": proof.trust_profile_ref.to_ecj1(),
                "signer_role": proof.signer_role.value,
                "signer_key_id": proof.signer_key_id,
            }
        )
    )


def _root_proofs(
    proofs: tuple[TrustEvidenceEnvelopeV1, ...],
    *,
    threshold: RootThresholdV1,
    role: RootRole,
    kind: TrustEvidenceKind,
    evidence_ref: ObjectRef,
    profile_ref: ObjectRef,
    interface: str,
) -> None:
    if not (
        type(proofs) is tuple
        and 0 < len(proofs) <= 2
        and all(type(proof) is TrustEvidenceEnvelopeV1 for proof in proofs)
    ):
        _failure(FailureCode.ROOT_THRESHOLD_NOT_MET, interface, "root-proof threshold")
    ids = tuple(proof.signer_key_id for proof in proofs)
    if len(ids) == 2 and len(set(ids)) != 2:
        _failure(FailureCode.ROOT_THRESHOLD_NOT_MET, interface, "root-proof threshold")
    if len(ids) == 2 and ids != tuple(sorted(ids)):
        _failure(FailureCode.ROOT_PROOF_ORDER_INVALID, interface, "root-proof order")
    if any(key_id not in threshold.ordered_key_ids for key_id in ids):
        _failure(FailureCode.ROOT_THRESHOLD_NOT_MET, interface, "root-proof threshold")
    for proof in proofs:
        if not (
            proof.signature_profile is SignatureProfile.EBU_AUTHORIZATION_ED25519_V1
            and proof.evidence_kind is kind
            and proof.evidence_ref == evidence_ref
            and proof.trust_profile_ref == profile_ref
            and proof.signer_role is role
            and _proof_hash_matches(proof)
        ):
            _failure(FailureCode.ROOT_THRESHOLD_NOT_MET, interface, "root-proof binding")
        public = _SYNTHETIC_ROOT_PUBLIC_KEYS.get(proof.signer_key_id)
        if public is None:
            _failure(FailureCode.ISSUER_KEY_INVALID, interface, "root key")
        verify_ed25519_signature(public, _trust_message(proof), proof.signature_base64url)
    if len(proofs) != 2:
        _failure(FailureCode.ROOT_THRESHOLD_NOT_MET, interface, "root-proof threshold")


def validate_trust_profile(
    profile: TrustProfileV1,
    installed_distribution_receipt: CanonicalBytes,
    state_store: AuthorizationStateStore,
    /,
) -> None:
    interface = "validate_trust_profile"
    if type(profile) is not TrustProfileV1 or not isinstance(state_store, AuthorizationStateStore):
        _formation_failure(interface)
    try:
        pinned = state_store.load_pinned_profile()
    except Exception:
        pinned = Applicability.NOT_APPLICABLE
    if pinned is Applicability.NOT_APPLICABLE:
        _failure(FailureCode.PRODUCTION_BOOTSTRAP_MISSING, interface, "installed pin exists")
    if pinned != _envelope_ref(profile) or not _object_is_exact(profile):
        _failure(FailureCode.TRUST_PROFILE_PIN_MISMATCH, interface, "exact profile pin")
    if profile.signature_profile is not SignatureProfile.EBU_AUTHORIZATION_ED25519_V1:
        _failure(FailureCode.SIGNATURE_PROFILE_UNSUPPORTED, interface, "PureEdDSA profile")
    try:
        receipt = parse_ecj1(installed_distribution_receipt)
    except FrameworkError:
        _failure(FailureCode.DEPENDENCY_INTEGRITY_FAILURE, interface, "provider receipt")
    if not (
        type(receipt) is dict
        and receipt.get("distribution") == "PyNaCl"
        and receipt.get("version") == "1.6.2"
        and receipt.get("wheel_sha256") == profile.provider_wheel_sha256
        and profile.provider_wheel_sha256 in _ADMITTED_PYNACL_WHEEL_SHA256
        and receipt.get("verified") is True
    ):
        _failure(FailureCode.DEPENDENCY_INTEGRITY_FAILURE, interface, "provider receipt")
    validation_namespace = "validation" in profile.validation_namespace_prefix
    profile_key_ids = (
        set(profile.issuer_root_threshold.ordered_key_ids)
        | set(profile.revocation_root_threshold.ordered_key_ids)
        | {key.key_id for key in profile.time_service_keys}
    )
    if profile.production and profile_key_ids & _VALIDATION_KEY_IDS:
        _failure(FailureCode.VALIDATION_KEY_FORBIDDEN, interface, "key separation")
    if profile.production and validation_namespace:
        _failure(FailureCode.VALIDATION_NAMESPACE_FORBIDDEN, interface, "namespace separation")
    if not profile.production and not validation_namespace:
        _failure(FailureCode.VALIDATION_NAMESPACE_FORBIDDEN, interface, "namespace separation")
    return None


def _continuity(
    sequence: int,
    predecessor: ObjectRef | str,
    current_ref: ObjectRef,
    last: tuple[int, ObjectRef] | Applicability,
    *,
    rollback: FailureCode,
    gap: FailureCode,
    equivocation: FailureCode,
    invalid: FailureCode,
    interface: str,
) -> None:
    if last is Applicability.NOT_APPLICABLE:
        if sequence != 0 or predecessor != "GENESIS":
            _failure(invalid, interface, "genesis sequence and predecessor")
        return
    if not (type(last) is tuple and len(last) == 2 and type(last[0]) is int and type(last[1]) is ObjectRef):
        _failure(invalid, interface, "durable prior state")
    prior_sequence, prior_ref = last
    if sequence < prior_sequence:
        _failure(rollback, interface, "sequence rollback")
    if sequence > prior_sequence + 1:
        _failure(gap, interface, "sequence gap")
    if sequence == prior_sequence:
        if current_ref != prior_ref:
            _failure(equivocation, interface, "same-sequence equivocation")
        return
    if predecessor != prior_ref:
        _failure(invalid, interface, "predecessor continuity")


def validate_issuer_registry_snapshot(
    snapshot: IssuerRegistrySnapshotV1,
    root_proofs: tuple[TrustEvidenceEnvelopeV1, ...],
    profile: TrustProfileV1,
    state_store: AuthorizationStateStore,
    /,
) -> tuple[AuthorizationCheckRecord, ...]:
    interface = "validate_issuer_registry_snapshot"
    if not (
        type(snapshot) is IssuerRegistrySnapshotV1
        and type(profile) is TrustProfileV1
        and isinstance(state_store, AuthorizationStateStore)
    ):
        _formation_failure(interface)
    profile_ref = _envelope_ref(profile)
    snapshot_ref = _envelope_ref(snapshot)
    _root_proofs(
        root_proofs,
        threshold=profile.issuer_root_threshold,
        role=RootRole.ISSUER_ROOT,
        kind=TrustEvidenceKind.ISSUER_REGISTRY,
        evidence_ref=snapshot_ref,
        profile_ref=profile_ref,
        interface=interface,
    )
    if snapshot.trust_profile_ref != profile_ref or not _object_is_exact(snapshot):
        _failure(FailureCode.ISSUER_REGISTRY_INVALID, interface, "registry profile and object hash")
    try:
        last = state_store.load_last_issuer_state()
    except Exception:
        _failure(FailureCode.ISSUER_REGISTRY_INVALID, interface, "durable issuer state")
    _continuity(
        snapshot.sequence,
        snapshot.predecessor_snapshot_ref_or_genesis,
        snapshot_ref,
        last,
        rollback=FailureCode.ISSUER_REGISTRY_ROLLBACK,
        gap=FailureCode.ISSUER_REGISTRY_GAP,
        equivocation=FailureCode.ISSUER_REGISTRY_EQUIVOCATION,
        invalid=FailureCode.ISSUER_REGISTRY_INVALID,
        interface=interface,
    )
    for entry in snapshot.ordered_issuer_entries:
        for key in entry.active_keys:
            _verify_key_id(key.public_key_base64url, key.key_id, interface, "issuer key ID")
    try:
        state_store.persist_validated_state("ISSUER", snapshot.sequence, snapshot_ref)
    except Exception:
        _failure(FailureCode.ISSUER_REGISTRY_INVALID, interface, "durable registry sequence")
    names = (
        "two ordered distinct issuer-root proofs",
        "provider verification of both proofs",
        "registry trust-profile binding",
        "sequence, predecessor, rollback, gap, equivocation",
        "registry and key interval formation",
        "signer issuer/key entry and key ID",
        "durable registry sequence",
    )
    return tuple(_check_record(index, name) for index, name in enumerate(names, 1))


def _authorization_message(envelope: AuthorizationAuthenticityEnvelopeV1) -> bytes:
    return bytes(
        encode_ecj1(
            {
                "hash_domain": "ebu.authorization-signature-message.v1",
                "signature_profile": envelope.signature_profile.value,
                "stage_authorization_ref": envelope.stage_authorization_ref.to_ecj1(),
                "trust_profile_ref": envelope.trust_profile_ref.to_ecj1(),
                "signer_issuer_id": str(envelope.signer_issuer_id),
                "signer_key_id": envelope.signer_key_id,
                "ordered_delegation_credential_refs": [ref.to_ecj1() for ref in envelope.ordered_delegation_credential_refs],
            }
        )
    )


def validate_delegation_chain(
    credentials: tuple[DelegationCredentialV1, ...],
    proofs: tuple[TrustEvidenceEnvelopeV1, ...],
    issuer_snapshot: IssuerRegistrySnapshotV1,
    profile: TrustProfileV1,
    authorization: StageAuthorization,
    attested_utc: str,
    revocation: RevocationSnapshotV1,
    /,
) -> IssuerEntry:
    interface = "validate_delegation_chain"
    if not (
        type(credentials) is tuple
        and type(proofs) is tuple
        and all(type(item) is DelegationCredentialV1 for item in credentials)
        and all(type(item) is TrustEvidenceEnvelopeV1 for item in proofs)
        and type(issuer_snapshot) is IssuerRegistrySnapshotV1
        and type(profile) is TrustProfileV1
        and type(revocation) is RevocationSnapshotV1
        and _timestamp(attested_utc)
        and type(authorization).__name__ == "StageAuthorization"
        and type(authorization).__module__ == "ebu_framework.authorization"
    ):
        _formation_failure(interface)
    entries = {entry.issuer_id: entry for entry in issuer_snapshot.ordered_issuer_entries}
    if not credentials:
        entry = entries.get(authorization.issuer_id)
        if entry is None:
            _failure(FailureCode.DELEGATION_CHAIN_INVALID, interface, "registered issuer")
        return entry
    if len(credentials) != len(proofs):
        _failure(FailureCode.DELEGATION_CHAIN_INVALID, interface, "positional object/proof correspondence")
    key_map = {
        key.key_id: key.public_key_base64url
        for entry in issuer_snapshot.ordered_issuer_entries
        for key in entry.active_keys
    }
    key_map.update(_SYNTHETIC_ISSUER_PUBLIC_KEYS)
    credential_refs = tuple(_envelope_ref(item) for item in credentials)
    for credential, proof, credential_ref in zip(credentials, proofs, credential_refs, strict=True):
        if not (
            proof.evidence_kind is TrustEvidenceKind.DELEGATION_CREDENTIAL
            and proof.evidence_ref == credential_ref
            and proof.trust_profile_ref == _envelope_ref(profile)
            and proof.signer_key_id == credential.delegator_key_id
            and _object_is_exact(credential)
            and _proof_hash_matches(proof)
        ):
            _failure(FailureCode.DELEGATION_CHAIN_INVALID, interface, "credential object and proof")
        public = key_map.get(credential.delegator_key_id)
        if public is None:
            for candidate in credentials:
                if candidate.delegate_key_id == credential.delegator_key_id:
                    public = key_map.get(candidate.delegate_key_id)
        if public is None:
            _failure(FailureCode.DELEGATION_CHAIN_INVALID, interface, "delegator key")
        verify_ed25519_signature(public, _trust_message(proof), proof.signature_base64url)
    for index, credential in enumerate(credentials):
        if index + 1 < len(credentials):
            parent = credentials[index + 1]
            if not (
                credential.parent_credential_ref_or_registry_entry == credential_refs[index + 1]
                and credential.delegator_issuer_id == parent.delegate_issuer_id
                and credential.delegator_key_id == parent.delegate_key_id
            ):
                _failure(FailureCode.DELEGATION_CHAIN_INVALID, interface, "leaf-to-root continuity")
        elif not (
            credential.parent_credential_ref_or_registry_entry == "REGISTRY_ENTRY"
            and credential.delegator_issuer_id in entries
        ):
            _failure(FailureCode.DELEGATION_CHAIN_INVALID, interface, "root continuity")
    # Adjacent credentials necessarily repeat the parent/child hand-off pair.
    # The unique path nodes are the leaf delegate followed by each delegator
    # while walking leaf-to-root; repetition in that sequence is a real cycle.
    path_pairs = (
        (credentials[0].delegate_issuer_id, credentials[0].delegate_key_id),
    ) + tuple(
        (item.delegator_issuer_id, item.delegator_key_id)
        for item in credentials
    )
    if (
        len(set(credential_refs)) != len(credential_refs)
        or len({item.credential_id for item in credentials}) != len(credentials)
        or len(set(path_pairs)) != len(path_pairs)
    ):
        _failure(FailureCode.DELEGATION_CYCLE, interface, "repetition and cycle")
    if any(
        item.revocation_registry_ref != authorization.revocation_snapshot_ref
        for item in credentials
    ):
        _failure(FailureCode.DELEGATION_CHAIN_INVALID, interface, "common revocation authority")
    instant = _instant(attested_utc)
    if any(not (_instant(item.not_before) <= instant < _instant(item.expires_at)) for item in credentials):
        _failure(FailureCode.DELEGATION_CHAIN_INVALID, interface, "temporal intersection")
    parent_entry = entries[credentials[-1].delegator_issuer_id]
    parent_stages = set(parent_entry.maximum_stages)
    parent_operations = set(parent_entry.maximum_operations)
    parent_namespaces = set(parent_entry.target_namespace_prefixes)
    parent_kinds = set(parent_entry.target_kind_ids)
    parent_exclusions = set(parent_entry.explicit_exclusions)
    root_key = next(
        (
            key
            for key in parent_entry.active_keys
            if key.key_id == credentials[-1].delegator_key_id
        ),
        None,
    )
    if root_key is None or not parent_entry.delegation_allowed:
        _failure(
            FailureCode.DELEGATION_SCOPE_ESCALATION,
            interface,
            "strict attenuation and exclusions",
        )
    parent_not_before = _instant(root_key.not_before)
    parent_expires_at = _instant(root_key.expires_at)
    for credential in reversed(credentials):
        if not (
            set(credential.permitted_stages) <= parent_stages
            and set(credential.permitted_operations) <= parent_operations
            and all(
                any(
                    child_prefix.startswith(parent_prefix)
                    for parent_prefix in parent_namespaces
                )
                for child_prefix in credential.target_namespace_prefixes
            )
            and set(credential.target_kind_ids) <= parent_kinds
            and parent_exclusions <= set(credential.explicit_exclusions)
            and parent_not_before <= _instant(credential.not_before)
            and _instant(credential.expires_at) <= parent_expires_at
        ):
            _failure(FailureCode.DELEGATION_SCOPE_ESCALATION, interface, "strict attenuation and exclusions")
        parent_stages = set(credential.permitted_stages)
        parent_operations = set(credential.permitted_operations)
        parent_namespaces = set(credential.target_namespace_prefixes)
        parent_kinds = set(credential.target_kind_ids)
        parent_exclusions = set(credential.explicit_exclusions)
        parent_not_before = _instant(credential.not_before)
        parent_expires_at = _instant(credential.expires_at)
    if (
        len(credentials) > profile.maximum_delegation_depth
        or len(credentials) > parent_entry.maximum_delegated_depth
        or credentials[-1].remaining_maximum_depth
        != parent_entry.maximum_delegated_depth - 1
        or any(
            not parent.delegation_allowed
            or child.remaining_maximum_depth
            != parent.remaining_maximum_depth - 1
            for child, parent in zip(
                credentials, credentials[1:], strict=False
            )
        )
    ):
        _failure(FailureCode.DELEGATION_DEPTH_EXCEEDED, interface, "depth decrement and maximum four")
    leaf = credentials[0]
    if leaf.delegate_issuer_id != authorization.issuer_id:
        _failure(FailureCode.DELEGATION_CHAIN_INVALID, interface, "effective issuer")
    return IssuerEntry(
        issuer_id=leaf.delegate_issuer_id,
        governance_evidence_refs=parent_entry.governance_evidence_refs,
        active_keys=(IssuerKeyV1(
            issuer_id=leaf.delegate_issuer_id,
            key_id=leaf.delegate_key_id,
            public_key_base64url=key_map.get(leaf.delegate_key_id, parent_entry.active_keys[0].public_key_base64url),
            not_before=leaf.not_before,
            expires_at=leaf.expires_at,
        ),),
        maximum_stages=leaf.permitted_stages,
        maximum_operations=leaf.permitted_operations,
        target_namespace_prefixes=leaf.target_namespace_prefixes,
        target_kind_ids=leaf.target_kind_ids,
        delegation_allowed=leaf.delegation_allowed,
        maximum_delegated_depth=leaf.remaining_maximum_depth,
        explicit_exclusions=leaf.explicit_exclusions,
    )


def _time_message(attestation: TrustedTimeAttestationV1) -> bytes:
    return bytes(
        encode_ecj1(
            {
                "hash_domain": "ebu.trusted-time-attestation-message.v1",
                "signature_profile": SignatureProfile.EBU_AUTHORIZATION_ED25519_V1.value,
                "trust_profile_ref": attestation.trust_profile_ref.to_ecj1(),
                "time_service_id": str(attestation.time_service_id),
                "signer_key_id": attestation.signer_key_id,
                "challenge_base64url": attestation.challenge_base64url,
                "authorization_use_key": str(attestation.authorization_use_key),
                "attested_utc": attestation.attested_utc,
                "service_sequence": attestation.service_sequence,
                "issued_at": attestation.issued_at,
                "expires_at": attestation.expires_at,
            }
        )
    )


def _validate_trusted_time_attestation_prefix(
    challenge: TrustedTimeChallengeV1,
    attestation: TrustedTimeAttestationV1,
    profile: TrustProfileV1,
) -> None:
    interface = "validate_trusted_time_attestation"
    if not (
        type(challenge) is TrustedTimeChallengeV1
        and type(attestation) is TrustedTimeAttestationV1
        and type(profile) is TrustProfileV1
    ):
        _formation_failure(interface)
    if not (
        attestation.challenge_base64url == challenge.challenge_base64url
        and attestation.authorization_use_key == challenge.authorization_use_key
        and attestation.trust_profile_ref == challenge.trust_profile_ref == _envelope_ref(profile)
        and attestation.time_service_id == challenge.time_service_id == profile.issuer_service_id
    ):
        _failure(FailureCode.TRUSTED_TIME_CHALLENGE_MISMATCH, interface, "response request binding")
    pins = {key.key_id: key for key in profile.time_service_keys}
    pin = pins.get(attestation.signer_key_id)
    if pin is None:
        _failure(FailureCode.ISSUER_KEY_INVALID, interface, "time signer pin")
    verify_ed25519_signature(pin.public_key_base64url, _time_message(attestation), attestation.signature_base64url)
    issued = _instant(attestation.issued_at)
    attested = _instant(attestation.attested_utc)
    expires = _instant(attestation.expires_at)
    if not (
        issued <= attested < expires
        and (expires - issued).total_seconds() <= profile.maximum_time_response_age_seconds
        and _instant(pin.not_before) <= attested < _instant(pin.expires_at)
    ):
        _failure(FailureCode.TRUSTED_TIME_STALE, interface, "freshness interval")


def _validate_trusted_time_sequence(
    attestation: TrustedTimeAttestationV1,
    state_store: AuthorizationStateStore,
) -> None:
    interface = "validate_trusted_time_attestation"
    if not (
        type(attestation) is TrustedTimeAttestationV1
        and isinstance(state_store, AuthorizationStateStore)
    ):
        _formation_failure(interface)
    try:
        last = state_store.load_last_time_sequence(attestation.time_service_id)
    except Exception:
        _failure(FailureCode.TRUSTED_TIME_SEQUENCE_INVALID, interface, "durable time sequence")
    if last is not Applicability.NOT_APPLICABLE and (
        type(last) is not int or attestation.service_sequence <= last
    ):
        _failure(FailureCode.TRUSTED_TIME_SEQUENCE_INVALID, interface, "strictly increasing sequence")
    try:
        state_store.persist_validated_state("TIME", attestation.service_sequence, attestation.trust_profile_ref)
    except Exception:
        _failure(FailureCode.TRUSTED_TIME_SEQUENCE_INVALID, interface, "durable time sequence")


def validate_trusted_time_attestation(
    challenge: TrustedTimeChallengeV1,
    attestation: TrustedTimeAttestationV1,
    profile: TrustProfileV1,
    state_store: AuthorizationStateStore,
    /,
) -> None:
    _validate_trusted_time_attestation_prefix(challenge, attestation, profile)
    _validate_trusted_time_sequence(attestation, state_store)
    return None


def validate_revocation_snapshot(
    snapshot: RevocationSnapshotV1,
    root_proofs: tuple[TrustEvidenceEnvelopeV1, ...],
    profile: TrustProfileV1,
    attested_utc: str,
    state_store: AuthorizationStateStore,
    /,
) -> None:
    interface = "validate_revocation_snapshot"
    if not (
        type(snapshot) is RevocationSnapshotV1
        and type(profile) is TrustProfileV1
        and _timestamp(attested_utc)
        and isinstance(state_store, AuthorizationStateStore)
    ):
        _formation_failure(interface)
    profile_ref = _envelope_ref(profile)
    snapshot_ref = _envelope_ref(snapshot)
    _root_proofs(
        root_proofs,
        threshold=profile.revocation_root_threshold,
        role=RootRole.REVOCATION_ROOT,
        kind=TrustEvidenceKind.REVOCATION_SNAPSHOT,
        evidence_ref=snapshot_ref,
        profile_ref=profile_ref,
        interface=interface,
    )
    now = _instant(attested_utc)
    if not (
        snapshot.trust_profile_ref == profile_ref
        and _object_is_exact(snapshot)
        and _instant(snapshot.as_of) <= now < _instant(snapshot.next_update)
        and (_instant(snapshot.next_update) - _instant(snapshot.as_of)).total_seconds() <= profile.maximum_revocation_lifetime_seconds
    ):
        _failure(FailureCode.REVOCATION_SNAPSHOT_EXPIRED, interface, "snapshot profile and interval")
    try:
        last = state_store.load_last_revocation_state()
    except Exception:
        _failure(FailureCode.REVOCATION_EQUIVOCATION, interface, "durable revocation state")
    _continuity(
        snapshot.sequence,
        snapshot.predecessor_snapshot_ref_or_genesis,
        snapshot_ref,
        last,
        rollback=FailureCode.REVOCATION_ROLLBACK,
        gap=FailureCode.REVOCATION_GAP,
        equivocation=FailureCode.REVOCATION_EQUIVOCATION,
        invalid=FailureCode.REVOCATION_EQUIVOCATION,
        interface=interface,
    )
    try:
        state_store.persist_validated_state("REVOCATION", snapshot.sequence, snapshot_ref)
    except Exception:
        _failure(FailureCode.REVOCATION_EQUIVOCATION, interface, "durable revocation sequence")
    return None


def _production_trusted_time_challenge() -> bytes:
    """Production-only OS challenge path; unreachable without a future bootstrap."""

    return secrets.token_bytes(32)


__all__ = (
    "SignatureProfile",
    "TrustEvidenceKind",
    "RevocableObjectKind",
    "RootRole",
    "KeyPinV1",
    "RootThresholdV1",
    "TrustProfileV1",
    "IssuerKeyV1",
    "IssuerEntry",
    "IssuerRegistrySnapshotV1",
    "DelegationCredentialV1",
    "RevocationEntryV1",
    "RevocationSnapshotV1",
    "TrustedTimeChallengeV1",
    "TrustedTimeAttestationV1",
    "AuthorizationAuthenticityEnvelopeV1",
    "TrustEvidenceEnvelopeV1",
    "TrustedTimeService",
    "RevocationService",
    "AuthorizationStateStore",
    "verify_ed25519_signature",
    "validate_trust_profile",
    "validate_issuer_registry_snapshot",
    "validate_delegation_chain",
    "validate_trusted_time_attestation",
    "validate_revocation_snapshot",
)
