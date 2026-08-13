"""Stable identifiers, versions, exact references, and typed digests."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import ClassVar, Self

from .canonical import _normalize_nfc
from .errors import FailureCode, _fail


_SEGMENT_RE = re.compile(r"[a-z0-9][a-z0-9._-]*", re.ASCII)
_SEMANTIC_VERSION_RE = re.compile(
    r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", re.ASCII
)
_LOWER_HEX_64_RE = re.compile(r"[0-9a-f]{64}", re.ASCII)


def _validated_segment(value: str, field: str) -> str:
    if type(value) is not str or _SEGMENT_RE.fullmatch(value) is None:
        _fail(
            FailureCode.SCIENTIFIC_ID_INVALID,
            f"{field} must be a lowercase ASCII identifier segment",
        )
    return value


@dataclass(frozen=True, slots=True, order=True)
class ScientificId:
    value: str

    def __post_init__(self) -> None:
        if type(self.value) is not str:
            _fail(FailureCode.SCIENTIFIC_ID_INVALID, "ScientificId must be text")
        fields = self.value.split(":")
        if len(fields) != 4 or fields[0] != "ebu":
            _fail(
                FailureCode.SCIENTIFIC_ID_INVALID,
                "ScientificId must have form ebu:<kind>:<namespace>:<local-id>",
            )
        _validated_segment(fields[1], "kind")
        _validated_segment(fields[2], "namespace")
        _validated_segment(fields[3], "local-id")

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(value)

    @property
    def kind(self) -> str:
        return self.value.split(":", 3)[1]

    @property
    def namespace(self) -> str:
        return self.value.split(":", 3)[2]

    @property
    def local_id(self) -> str:
        return self.value.split(":", 3)[3]

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True, order=True)
class SemanticVersion:
    value: str

    def __post_init__(self) -> None:
        if type(self.value) is not str or _SEMANTIC_VERSION_RE.fullmatch(
            self.value
        ) is None:
            _fail(
                FailureCode.SEMANTIC_VERSION_INVALID,
                "semantic version must be MAJOR.MINOR.PATCH with minimal integers",
            )

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(value)

    @property
    def major(self) -> int:
        return int(self.value.split(".", 2)[0])

    @property
    def minor(self) -> int:
        return int(self.value.split(".", 2)[1])

    @property
    def patch(self) -> int:
        return int(self.value.split(".", 2)[2])

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True, order=True)
class _Digest:
    value: str
    prefix: ClassVar[str] = "sha256:"

    def __post_init__(self) -> None:
        if type(self.value) is not str or not self.value.startswith(self.prefix):
            _fail(
                FailureCode.DIGEST_INVALID,
                f"{type(self).__name__} must begin with {self.prefix!r}",
            )
        hexadecimal = self.value[len(self.prefix) :]
        if _LOWER_HEX_64_RE.fullmatch(hexadecimal) is None:
            _fail(
                FailureCode.DIGEST_INVALID,
                f"{type(self).__name__} must contain exactly 64 lowercase hex digits",
            )

    @property
    def hex_digest(self) -> str:
        return self.value[len(self.prefix) :]

    @classmethod
    def from_hex(cls, hexadecimal: str) -> Self:
        return cls(cls.prefix + hexadecimal)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True, order=True)
class ObjectContentHash(_Digest):
    pass


@dataclass(frozen=True, slots=True, order=True)
class StatePayloadHash(_Digest):
    pass


@dataclass(frozen=True, slots=True, order=True)
class PolicyMemoryPayloadHash(_Digest):
    pass


@dataclass(frozen=True, slots=True, order=True)
class AugmentedClosedLoopReplayStateHash(_Digest):
    pass


@dataclass(frozen=True, slots=True, order=True)
class RepresentedStateProjectionHash(_Digest):
    pass


@dataclass(frozen=True, slots=True, order=True)
class InformationViewHash(_Digest):
    pass


@dataclass(frozen=True, slots=True, order=True)
class ProposalSetHash(_Digest):
    pass


@dataclass(frozen=True, slots=True, order=True)
class ExecutionSemanticsHash(_Digest):
    pass


@dataclass(frozen=True, slots=True, order=True)
class CanonicalTraceRowHash(_Digest):
    pass


@dataclass(frozen=True, slots=True, order=True)
class CanonicalTracePrefixHash(_Digest):
    pass


@dataclass(frozen=True, slots=True, order=True)
class CanonicalScientificTracePayloadHash(_Digest):
    pass


@dataclass(frozen=True, slots=True, order=True)
class ArtifactByteHash(_Digest):
    pass


@dataclass(frozen=True, slots=True, order=True)
class SourceFileRawSha256(_Digest):
    prefix: ClassVar[str] = "sha256-raw:"


@dataclass(frozen=True, slots=True, order=True)
class AuthorizationUseKey(_Digest):
    pass


@dataclass(frozen=True, slots=True, order=True)
class ObjectRef:
    object_id: ScientificId
    object_version: SemanticVersion
    object_content_hash: ObjectContentHash

    def __post_init__(self) -> None:
        if type(self.object_id) is not ScientificId:
            _fail(FailureCode.DIGEST_TYPE_MISMATCH, "ObjectRef object_id type mismatch")
        if type(self.object_version) is not SemanticVersion:
            _fail(
                FailureCode.DIGEST_TYPE_MISMATCH,
                "ObjectRef object_version type mismatch",
            )
        if type(self.object_content_hash) is not ObjectContentHash:
            _fail(
                FailureCode.DIGEST_TYPE_MISMATCH,
                "ObjectRef requires ObjectContentHash",
            )

    def to_ecj1(self) -> dict[str, str]:
        return {
            "object_content_hash": str(self.object_content_hash),
            "object_id": str(self.object_id),
            "object_version": str(self.object_version),
        }


@dataclass(frozen=True, slots=True)
class ScientificIdAllocationClaimV1:
    kind: str
    namespace: str
    namespace_registry_ref: ObjectRef
    allocation_authority_ref: ObjectRef
    stable_key: str

    def __post_init__(self) -> None:
        _validated_segment(self.kind, "kind")
        _validated_segment(self.namespace, "namespace")
        if type(self.namespace_registry_ref) is not ObjectRef:
            _fail(
                FailureCode.DIGEST_TYPE_MISMATCH,
                "namespace_registry_ref must be ObjectRef",
            )
        if type(self.allocation_authority_ref) is not ObjectRef:
            _fail(
                FailureCode.DIGEST_TYPE_MISMATCH,
                "allocation_authority_ref must be ObjectRef",
            )
        if type(self.stable_key) is not str or not self.stable_key:
            _fail(FailureCode.STABLE_KEY_INVALID, "stable_key must be nonempty text")
        normalized = _normalize_nfc(self.stable_key)
        if any(ord(character) < 0x20 for character in normalized):
            _fail(
                FailureCode.STABLE_KEY_INVALID,
                "stable_key must not contain control characters",
            )
        object.__setattr__(self, "stable_key", normalized)

    def to_ecj1(self) -> dict[str, object]:
        return {
            "allocation_authority_ref": self.allocation_authority_ref.to_ecj1(),
            "hash_domain": "ebu.scientific-id-allocation.v1",
            "id_scheme": "sha256-fullhex-v1",
            "kind": self.kind,
            "namespace": self.namespace,
            "namespace_registry_ref": self.namespace_registry_ref.to_ecj1(),
            "stable_key": self.stable_key,
        }


def parse_scientific_id(value: str) -> ScientificId:
    return ScientificId.parse(value)


def parse_semantic_version(value: str) -> SemanticVersion:
    return SemanticVersion.parse(value)


__all__ = (
    "ArtifactByteHash",
    "AugmentedClosedLoopReplayStateHash",
    "AuthorizationUseKey",
    "CanonicalScientificTracePayloadHash",
    "CanonicalTracePrefixHash",
    "CanonicalTraceRowHash",
    "ExecutionSemanticsHash",
    "InformationViewHash",
    "ObjectContentHash",
    "ObjectRef",
    "PolicyMemoryPayloadHash",
    "ProposalSetHash",
    "RepresentedStateProjectionHash",
    "ScientificId",
    "ScientificIdAllocationClaimV1",
    "SemanticVersion",
    "SourceFileRawSha256",
    "StatePayloadHash",
    "parse_scientific_id",
    "parse_semantic_version",
)
