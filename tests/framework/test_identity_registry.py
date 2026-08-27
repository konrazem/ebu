"""V1 T0/T1 checks for identity allocation and immutable registries."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import FrozenInstanceError
import json
from pathlib import Path
import unittest
from unittest import mock

from ebu_framework.canonical import encode_ecj1, parse_ecj1
from ebu_framework.errors import FailureCode, FrameworkError
from ebu_framework.hashing import compute_object_content_hash
from ebu_framework.identity import (
    ObjectContentHash,
    ObjectRef,
    ScientificId,
    ScientificIdAllocationClaimV1,
    SemanticVersion,
    parse_scientific_id,
    parse_semantic_version,
)
from ebu_framework.registry import (
    AliasRecord,
    NamespaceRegistrySnapshot,
    RegistryRecord,
    _NamespaceRegistryStore,
    _load_core_namespace_registry,
    allocate_scientific_id,
    register_draft,
    resolve_alias,
    resolve_ref,
)
from safety import (
    assert_safe_test_module,
    synthetic_namespace_store,
    synthetic_object_store,
    synthetic_ref,
)


_HERE = Path(__file__).resolve().parent
_VECTORS = json.loads(
    (_HERE / "fixtures" / "scientific_id_vectors_v1.json").read_text("utf-8")
)


def _ref(value: dict[str, str]) -> ObjectRef:
    return ObjectRef(
        ScientificId(value["object_id"]),
        SemanticVersion(value["object_version"]),
        ObjectContentHash(value["object_content_hash"]),
    )


class IdentityRegistryTests(unittest.TestCase):
    check_count = 0

    def checked_equal(self, left, right) -> None:
        type(self).check_count += 1
        self.assertEqual(left, right)

    def claim(self, stable_key: str = "fixture-alpha") -> ScientificIdAllocationClaimV1:
        return ScientificIdAllocationClaimV1(
            kind=_VECTORS["claim"]["kind"],
            namespace=_VECTORS["claim"]["namespace"],
            namespace_registry_ref=_ref(_VECTORS["registry_ref"]),
            allocation_authority_ref=_ref(_VECTORS["allocation_authority_ref"]),
            stable_key=stable_key,
        )

    def test_identifier_and_version_grammar(self) -> None:
        valid_id = _VECTORS["expected_scientific_id"]
        self.checked_equal(str(parse_scientific_id(valid_id)), valid_id)
        self.checked_equal(str(parse_semantic_version("12.3.0")), "12.3.0")
        for invalid in _VECTORS["invalid_ids"]:
            with self.subTest(identifier=invalid), self.assertRaises(FrameworkError):
                parse_scientific_id(invalid)
            type(self).check_count += 1
        for invalid in _VECTORS["invalid_versions"]:
            with self.subTest(version=invalid), self.assertRaises(FrameworkError):
                parse_semantic_version(invalid)
            type(self).check_count += 1

    def test_allocation_claim_bytes_full_digest_and_idempotency(self) -> None:
        claim = self.claim()
        self.checked_equal(
            bytes(encode_ecj1(claim.to_ecj1())).hex(),
            _VECTORS["claim_canonical_hex"],
        )
        store = synthetic_namespace_store()
        first = allocate_scientific_id(store, claim)
        second = allocate_scientific_id(store, claim)
        self.checked_equal(str(first), _VECTORS["expected_scientific_id"])
        self.checked_equal(first, second)
        self.checked_equal(first.local_id, "sha256-" + _VECTORS["expected_digest"])
        self.checked_equal(len(store.snapshot.allocations), 1)

    def test_concurrent_idempotent_allocation_is_atomic(self) -> None:
        store = synthetic_namespace_store()
        claim = self.claim()
        with ThreadPoolExecutor(max_workers=8) as executor:
            results = tuple(executor.map(lambda _: allocate_scientific_id(store, claim), range(64)))
        self.checked_equal(len(set(results)), 1)
        self.checked_equal(len(store.snapshot.allocations), 1)

    def test_conflicts_unregistered_and_reserved_fail_closed(self) -> None:
        store = synthetic_namespace_store()
        first_id = allocate_scientific_id(store, self.claim())
        with mock.patch("ebu_framework.registry._allocation_id", return_value=first_id):
            with self.assertRaises(FrameworkError) as caught:
                allocate_scientific_id(store, self.claim("fixture-beta"))
        self.checked_equal(
            caught.exception.envelope.failure_code,
            FailureCode.ALLOCATION_COLLISION,
        )
        unregistered = ScientificIdAllocationClaimV1(
            kind="record",
            namespace="missing",
            namespace_registry_ref=store.snapshot.registry_ref,
            allocation_authority_ref=_ref(_VECTORS["allocation_authority_ref"]),
            stable_key="fixture-alpha",
        )
        with self.assertRaises(FrameworkError) as caught:
            allocate_scientific_id(store, unregistered)
        self.checked_equal(
            caught.exception.envelope.failure_code,
            FailureCode.NAMESPACE_UNREGISTERED,
        )
        core = _load_core_namespace_registry()
        core_entry = next(entry for entry in core.entries if entry.namespace == "core")
        reserved = ScientificIdAllocationClaimV1(
            kind="record",
            namespace="core",
            namespace_registry_ref=core.registry_ref,
            allocation_authority_ref=core_entry.owning_authority_ref,
            stable_key="never-allocated",
        )
        with self.assertRaises(FrameworkError) as caught:
            allocate_scientific_id(_NamespaceRegistryStore(core), reserved)
        self.checked_equal(
            caught.exception.envelope.failure_code,
            FailureCode.RESERVED_NAMESPACE,
        )

    def test_registry_insert_resolution_alias_and_deep_immutability(self) -> None:
        store = synthetic_object_store()
        object_id = ScientificId("ebu:record:synthetic:record-a")
        schema_id = ScientificId("ebu:schema:validation:record-v1")
        version = SemanticVersion("1.0.0")
        payload = {"alpha": [1, 2]}
        content_hash = compute_object_content_hash(
            object_id=object_id,
            object_kind="record",
            schema_id=schema_id,
            schema_version=version,
            object_version=version,
            authority_refs=(),
            supersedes_ref=None,
            object_content_payload=payload,
        )
        reference = ObjectRef(object_id, version, content_hash)
        record = RegistryRecord.from_value(
            object_ref=reference,
            object_kind="record",
            value=payload,
        )
        alias = AliasRecord("record-a", reference)
        self.checked_equal(register_draft(store, record, (alias,)), record)
        self.checked_equal(register_draft(store, record, (alias,)), record)
        self.checked_equal(resolve_ref(store, reference), record)
        self.checked_equal(resolve_alias(store, "record-a"), record)
        extracted = record.value()
        extracted["alpha"].append(3)
        self.checked_equal(record.value(), payload)
        with self.assertRaises(FrozenInstanceError):
            record.lifecycle_status = "ACCEPTED"
        type(self).check_count += 1
        wrong_hash = ObjectRef(
            object_id,
            version,
            ObjectContentHash("sha256:" + "f" * 64),
        )
        with self.assertRaises(FrameworkError) as caught:
            resolve_ref(store, wrong_hash)
        self.checked_equal(caught.exception.envelope.failure_code, FailureCode.HASH_MISMATCH)
        wrong_version = ObjectRef(
            object_id,
            SemanticVersion("1.0.1"),
            content_hash,
        )
        with self.assertRaises(FrameworkError) as caught:
            resolve_ref(store, wrong_version)
        self.checked_equal(
            caught.exception.envelope.failure_code,
            FailureCode.VERSION_MISMATCH,
        )
        missing = synthetic_ref("ebu:record:synthetic:missing", "0")
        with self.assertRaises(FrameworkError) as caught:
            resolve_ref(store, missing)
        self.checked_equal(caught.exception.envelope.failure_code, FailureCode.REF_NOT_FOUND)

    def test_literal_bootstrap_registry_and_hash_projection(self) -> None:
        snapshot = _load_core_namespace_registry()
        self.checked_equal(
            tuple(entry.namespace for entry in snapshot.entries),
            ("authority", "core", "schema", "validation"),
        )
        self.checked_equal(
            tuple(entry.reserved for entry in snapshot.entries),
            (True, True, True, True),
        )
        registry_path = (
            Path(__import__("ebu_framework.registry").registry.__file__).parent
            / "data"
            / "core_registry_v1.json"
        )
        root = parse_ecj1(registry_path.read_bytes())
        payload = {key: value for key, value in root.items() if key != "registry_ref"}
        authority_ref = _ref(root["bootstrap_authority_ref"])
        projected = compute_object_content_hash(
            object_id=snapshot.registry_ref.object_id,
            object_kind="registry",
            schema_id=ScientificId("ebu:schema:core:namespace-registry-v1"),
            schema_version=SemanticVersion("1.0.0"),
            object_version=SemanticVersion("1.0.0"),
            authority_refs=(authority_ref,),
            supersedes_ref=None,
            object_content_payload=payload,
        )
        self.checked_equal(projected, snapshot.registry_ref.object_content_hash)
        self.checked_equal(bytes(encode_ecj1(root)), registry_path.read_bytes())

    def test_static_non_reachability(self) -> None:
        self.assertGreater(assert_safe_test_module(Path(__file__)), 0)
        type(self).check_count += 1

    @classmethod
    def tearDownClass(cls) -> None:
        print(f"V1_IDENTITY_REGISTRY_COMPLETED_CHECKS={cls.check_count}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
