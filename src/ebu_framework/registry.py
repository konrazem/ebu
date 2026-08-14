"""Immutable namespace and object registry foundations for I-1."""

from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
from pathlib import Path
import threading
from typing import Any

from .canonical import CanonicalBytes, ECJ1Value, _normalize_nfc, encode_ecj1, parse_ecj1
from .errors import FailureCode, _fail
from .envelopes import LifecycleStatus
from .identity import (
    ObjectRef,
    ScientificId,
    ScientificIdAllocationClaimV1,
    SemanticVersion,
)


RESERVED_NAMESPACES = frozenset({"authority", "core", "schema", "validation"})


@dataclass(frozen=True, slots=True, order=True)
class NamespaceEntry:
    namespace: str
    namespace_id: ScientificId
    owning_authority_ref: ObjectRef
    allocation_policy_ref: ObjectRef
    reserved: bool

    def __post_init__(self) -> None:
        probe = ScientificId(f"ebu:namespace:core:{self.namespace}")
        if self.namespace_id != probe:
            _fail(
                FailureCode.SCIENTIFIC_ID_INVALID,
                "namespace_id must be the literal ebu:namespace:core:<namespace> ID",
            )
        if type(self.owning_authority_ref) is not ObjectRef:
            _fail(
                FailureCode.DIGEST_TYPE_MISMATCH,
                "owning_authority_ref must be ObjectRef",
            )
        if type(self.allocation_policy_ref) is not ObjectRef:
            _fail(
                FailureCode.DIGEST_TYPE_MISMATCH,
                "allocation_policy_ref must be ObjectRef",
            )
        if type(self.reserved) is not bool:
            _fail(FailureCode.REGISTRY_RECORD_CONFLICT, "reserved must be bool")
        if self.reserved != (self.namespace in RESERVED_NAMESPACES):
            _fail(
                FailureCode.REGISTRY_RECORD_CONFLICT,
                "reserved namespace classification mismatch",
            )


@dataclass(frozen=True, slots=True)
class NamespaceRegistrySnapshot:
    registry_ref: ObjectRef
    entries: tuple[NamespaceEntry, ...]
    allocations: tuple[
        tuple[ScientificIdAllocationClaimV1, ScientificId], ...
    ] = ()

    def __post_init__(self) -> None:
        if type(self.registry_ref) is not ObjectRef:
            _fail(FailureCode.DIGEST_TYPE_MISMATCH, "registry_ref must be ObjectRef")
        if type(self.entries) is not tuple or not all(
            type(entry) is NamespaceEntry for entry in self.entries
        ):
            _fail(
                FailureCode.REGISTRY_RECORD_CONFLICT,
                "namespace entries must be an immutable tuple",
            )
        names = tuple(entry.namespace for entry in self.entries)
        if names != tuple(sorted(names)) or len(names) != len(set(names)):
            _fail(
                FailureCode.REGISTRY_RECORD_CONFLICT,
                "namespace entries must be unique and sorted",
            )
        if type(self.allocations) is not tuple:
            _fail(
                FailureCode.REGISTRY_RECORD_CONFLICT,
                "allocations must be an immutable tuple",
            )
        ids: set[ScientificId] = set()
        coordinates: set[tuple[str, str, str]] = set()
        for claim, scientific_id in self.allocations:
            if type(claim) is not ScientificIdAllocationClaimV1 or type(
                scientific_id
            ) is not ScientificId:
                _fail(
                    FailureCode.REGISTRY_RECORD_CONFLICT,
                    "invalid allocation record type",
                )
            coordinate = (claim.kind, claim.namespace, claim.stable_key)
            if scientific_id in ids or coordinate in coordinates:
                _fail(
                    FailureCode.ALLOCATION_COLLISION,
                    "duplicate allocation in namespace snapshot",
                )
            ids.add(scientific_id)
            coordinates.add(coordinate)


@dataclass(frozen=True, slots=True)
class RegistryRecord:
    object_ref: ObjectRef
    object_kind: str
    canonical_value: CanonicalBytes
    lifecycle_status: LifecycleStatus = LifecycleStatus.DRAFT

    def __post_init__(self) -> None:
        if type(self.object_ref) is not ObjectRef:
            _fail(FailureCode.DIGEST_TYPE_MISMATCH, "object_ref must be ObjectRef")
        if type(self.object_kind) is not str or not self.object_kind:
            _fail(
                FailureCode.REGISTRY_RECORD_CONFLICT,
                "object_kind must be nonempty text",
            )
        if type(self.canonical_value) is not bytes:
            _fail(
                FailureCode.REGISTRY_RECORD_CONFLICT,
                "canonical_value must be canonical bytes",
            )
        parse_ecj1(bytes(self.canonical_value))
        if (
            type(self.lifecycle_status) is not LifecycleStatus
            or self.lifecycle_status is not LifecycleStatus.DRAFT
        ):
            _fail(
                FailureCode.REGISTRY_RECORD_CONFLICT,
                "I-1 registry records support DRAFT only; acceptance belongs to I-2",
            )

    @classmethod
    def from_value(
        cls,
        *,
        object_ref: ObjectRef,
        object_kind: str,
        value: ECJ1Value,
    ) -> "RegistryRecord":
        return cls(
            object_ref=object_ref,
            object_kind=object_kind,
            canonical_value=encode_ecj1(value),
        )

    def value(self) -> ECJ1Value:
        return parse_ecj1(bytes(self.canonical_value))


@dataclass(frozen=True, slots=True, order=True)
class AliasRecord:
    alias: str
    target_ref: ObjectRef

    def __post_init__(self) -> None:
        if type(self.alias) is not str or not self.alias:
            _fail(FailureCode.ALIAS_INVALID, "alias must be nonempty text")
        normalized = _normalize_nfc(self.alias)
        if normalized != self.alias or any(ord(char) < 0x20 for char in normalized):
            _fail(
                FailureCode.ALIAS_INVALID,
                "alias must already be NFC and contain no control characters",
            )
        if type(self.target_ref) is not ObjectRef:
            _fail(FailureCode.DIGEST_TYPE_MISMATCH, "target_ref must be ObjectRef")


@dataclass(frozen=True, slots=True)
class ResolutionRecord:
    requested_ref: ObjectRef | None
    requested_alias: str | None
    resolved_ref: ObjectRef
    via_alias: bool


class _NamespaceRegistryStore:
    """Thread-safe compare-and-replace store used only by the T1 allocator."""

    def __init__(self, snapshot: NamespaceRegistrySnapshot) -> None:
        if type(snapshot) is not NamespaceRegistrySnapshot:
            _fail(
                FailureCode.REGISTRY_RECORD_CONFLICT,
                "namespace store requires NamespaceRegistrySnapshot",
            )
        self._lock = threading.RLock()
        self._snapshot = snapshot

    @property
    def snapshot(self) -> NamespaceRegistrySnapshot:
        with self._lock:
            return self._snapshot


class _ObjectRegistryStore:
    """Thread-safe store whose inserted record values are immutable bytes."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._records: dict[
            tuple[ScientificId, SemanticVersion], RegistryRecord
        ] = {}
        self._aliases: dict[str, AliasRecord] = {}


def _allocation_id(claim: ScientificIdAllocationClaimV1) -> ScientificId:
    digest = hashlib.sha256(bytes(encode_ecj1(claim.to_ecj1()))).hexdigest()
    return ScientificId(
        f"ebu:{claim.kind}:{claim.namespace}:sha256-{digest}"
    )


def allocate_scientific_id(
    registry: _NamespaceRegistryStore,
    claim: ScientificIdAllocationClaimV1,
) -> ScientificId:
    """Atomically record one content-neutral allocation claim."""

    if type(registry) is not _NamespaceRegistryStore:
        _fail(
            FailureCode.REGISTRY_RECORD_CONFLICT,
            "allocator requires the I-1 namespace registry store",
        )
    if type(claim) is not ScientificIdAllocationClaimV1:
        _fail(
            FailureCode.REGISTRY_RECORD_CONFLICT,
            "allocator requires ScientificIdAllocationClaimV1",
        )
    with registry._lock:
        snapshot = registry._snapshot
        if claim.namespace_registry_ref != snapshot.registry_ref:
            _fail(
                FailureCode.HASH_MISMATCH,
                "allocation claim names a different namespace registry snapshot",
            )
        entries = {entry.namespace: entry for entry in snapshot.entries}
        entry = entries.get(claim.namespace)
        if entry is None:
            _fail(
                FailureCode.NAMESPACE_UNREGISTERED,
                f"namespace is not registered: {claim.namespace}",
            )
        if entry.reserved:
            _fail(
                FailureCode.RESERVED_NAMESPACE,
                f"reserved namespace uses literal bootstrap IDs: {claim.namespace}",
            )
        if claim.allocation_authority_ref != entry.owning_authority_ref:
            _fail(
                FailureCode.ALLOCATION_CLAIM_CONFLICT,
                "allocation authority does not own the namespace",
            )
        coordinate = (claim.kind, claim.namespace, claim.stable_key)
        by_coordinate = {
            (existing.kind, existing.namespace, existing.stable_key): (
                existing,
                scientific_id,
            )
            for existing, scientific_id in snapshot.allocations
        }
        existing = by_coordinate.get(coordinate)
        if existing is not None:
            existing_claim, existing_id = existing
            if existing_claim == claim:
                return existing_id
            _fail(
                FailureCode.ALLOCATION_CLAIM_CONFLICT,
                "stable_key was already used with different claim fields",
            )
        scientific_id = _allocation_id(claim)
        by_id = {item_id: item_claim for item_claim, item_id in snapshot.allocations}
        if scientific_id in by_id and by_id[scientific_id] != claim:
            _fail(
                FailureCode.ALLOCATION_COLLISION,
                "full allocation digest collides with a different claim",
            )
        allocations = tuple(
            sorted(
                snapshot.allocations + ((claim, scientific_id),),
                key=lambda item: str(item[1]),
            )
        )
        registry._snapshot = replace(snapshot, allocations=allocations)
        return scientific_id


def register_draft(
    registry: _ObjectRegistryStore,
    record: RegistryRecord,
    aliases: tuple[AliasRecord, ...] = (),
) -> RegistryRecord:
    """Atomically insert immutable draft bytes and optional presentation aliases."""

    if type(registry) is not _ObjectRegistryStore or type(record) is not RegistryRecord:
        _fail(
            FailureCode.REGISTRY_RECORD_CONFLICT,
            "register_draft received an invalid store or record",
        )
    if type(aliases) is not tuple or not all(type(alias) is AliasRecord for alias in aliases):
        _fail(
            FailureCode.ALIAS_INVALID,
            "aliases must be an immutable tuple of AliasRecord values",
        )
    if any(alias.target_ref != record.object_ref for alias in aliases):
        _fail(FailureCode.ALIAS_CONFLICT, "alias target must equal the draft ref")
    key = (record.object_ref.object_id, record.object_ref.object_version)
    with registry._lock:
        existing = registry._records.get(key)
        if existing is not None:
            if existing == record and all(
                registry._aliases.get(alias.alias) == alias for alias in aliases
            ):
                return existing
            _fail(
                FailureCode.REGISTRY_RECORD_CONFLICT,
                "ID/version already names different immutable draft bytes",
            )
        for alias in aliases:
            prior = registry._aliases.get(alias.alias)
            if prior is not None and prior != alias:
                _fail(
                    FailureCode.ALIAS_CONFLICT,
                    f"alias already names another exact ref: {alias.alias}",
                )
        registry._records[key] = record
        for alias in aliases:
            registry._aliases[alias.alias] = alias
        return record


def resolve_ref(registry: _ObjectRegistryStore, reference: ObjectRef) -> RegistryRecord:
    if type(registry) is not _ObjectRegistryStore or type(reference) is not ObjectRef:
        _fail(FailureCode.REF_NOT_FOUND, "invalid registry or reference")
    with registry._lock:
        versions = {
            version: record
            for (object_id, version), record in registry._records.items()
            if object_id == reference.object_id
        }
        if not versions:
            _fail(FailureCode.REF_NOT_FOUND, f"object not found: {reference.object_id}")
        record = versions.get(reference.object_version)
        if record is None:
            _fail(
                FailureCode.VERSION_MISMATCH,
                f"version not found for {reference.object_id}",
            )
        if record.object_ref.object_content_hash != reference.object_content_hash:
            _fail(FailureCode.HASH_MISMATCH, "object reference hash mismatch")
        return record


def resolve_alias(registry: _ObjectRegistryStore, alias: str) -> RegistryRecord:
    if type(registry) is not _ObjectRegistryStore or type(alias) is not str:
        _fail(FailureCode.ALIAS_INVALID, "invalid registry or alias")
    normalized = _normalize_nfc(alias)
    if normalized != alias:
        _fail(FailureCode.ALIAS_INVALID, "alias lookup must already be NFC")
    with registry._lock:
        alias_record = registry._aliases.get(alias)
        if alias_record is None:
            _fail(FailureCode.REF_NOT_FOUND, f"alias not found: {alias}")
    return resolve_ref(registry, alias_record.target_ref)


def _ref_from_ecj1(value: Any) -> ObjectRef:
    if type(value) is not dict or set(value) != {
        "object_content_hash",
        "object_id",
        "object_version",
    }:
        _fail(FailureCode.REGISTRY_RECORD_CONFLICT, "malformed literal ObjectRef")
    from .identity import ObjectContentHash

    return ObjectRef(
        object_id=ScientificId(value["object_id"]),
        object_version=SemanticVersion(value["object_version"]),
        object_content_hash=ObjectContentHash(value["object_content_hash"]),
    )


def _load_core_namespace_registry() -> NamespaceRegistrySnapshot:
    path = Path(__file__).resolve().parent / "data" / "core_registry_v1.json"
    data = parse_ecj1(path.read_bytes())
    if type(data) is not dict or set(data) != {
        "allocation_policy_ref",
        "bootstrap_authority_ref",
        "namespace_entries",
        "registry_ref",
        "schema_ids",
    }:
        _fail(FailureCode.REGISTRY_RECORD_CONFLICT, "malformed core registry root")
    allocation_policy_ref = _ref_from_ecj1(data["allocation_policy_ref"])
    authority_ref = _ref_from_ecj1(data["bootstrap_authority_ref"])
    registry_ref = _ref_from_ecj1(data["registry_ref"])
    raw_entries = data["namespace_entries"]
    if type(raw_entries) is not list:
        _fail(FailureCode.REGISTRY_RECORD_CONFLICT, "namespace_entries must be array")
    entries: list[NamespaceEntry] = []
    for raw_entry in raw_entries:
        if type(raw_entry) is not dict or set(raw_entry) != {
            "namespace",
            "namespace_id",
            "reserved",
        }:
            _fail(FailureCode.REGISTRY_RECORD_CONFLICT, "malformed namespace entry")
        entries.append(
            NamespaceEntry(
                namespace=raw_entry["namespace"],
                namespace_id=ScientificId(raw_entry["namespace_id"]),
                owning_authority_ref=authority_ref,
                allocation_policy_ref=allocation_policy_ref,
                reserved=raw_entry["reserved"],
            )
        )
    schema_ids = data["schema_ids"]
    if type(schema_ids) is not list or not all(type(item) is str for item in schema_ids):
        _fail(FailureCode.REGISTRY_RECORD_CONFLICT, "schema_ids must be text array")
    for item in schema_ids:
        scientific_id = ScientificId(item)
        if scientific_id.kind != "schema" or scientific_id.namespace != "core":
            _fail(FailureCode.REGISTRY_RECORD_CONFLICT, "invalid bootstrap schema ID")
    return NamespaceRegistrySnapshot(
        registry_ref=registry_ref,
        entries=tuple(entries),
    )


__all__ = (
    "AliasRecord",
    "NamespaceEntry",
    "NamespaceRegistrySnapshot",
    "RegistryRecord",
    "ResolutionRecord",
    "allocate_scientific_id",
    "register_draft",
    "resolve_alias",
    "resolve_ref",
)
