"""Synthetic, outcome-blind controls for binding privacy and authorization."""

from __future__ import annotations

import ast
import copy
import hashlib
import inspect
import json
import os
import struct
import sys
import tempfile
import unittest
import zlib
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

from stage_f_binding.binding import (
    ACCEPTED_GAPS,
    CAMPAIGN_ORDER,
    ClosedSchemaValidator,
    VerifiedGitRepository,
    assert_preimport_authorized,
    validate_private_host_manifest,
    validate_public_host_binding,
    validate_route_portfolio,
)
from stage_f_binding.canonical import (
    BindingRefusal,
    ZERO_SCIENCE_COUNTERS,
    canonical_bytes,
    canonical_digest,
    sha256_identity,
    strict_loads,
    verify_embedded_digest,
)
from scripts.build_stage_f_local_binding import (
    BuildRefusal,
    _GitObjectStore,
    _PackIndex,
    _git_sha1,
    _parse_git_batch,
)
from scripts.validate_stage_f_local_binding import (
    _RetainedMaterialLocks,
    _load_identity_materials,
    _load_verified_git_repository,
    _parser,
    _require_not_future_utc,
    _verify_complete_challenge_history,
)


ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).resolve().parent / "fixtures"
SCHEMA_PATH = ROOT / "stage_f_local_execution_binding_evidence_schema.json"


def _load_json(path: Path) -> object:
    return strict_loads(path.read_bytes())


def _git_object(object_type: str, raw: bytes) -> tuple[tuple[str, str], bytes]:
    framed = object_type.encode("ascii") + b" " + str(len(raw)).encode("ascii") + b"\0" + raw
    return (
        (object_type, hashlib.sha1(framed, usedforsecurity=False).hexdigest()),
        raw,
    )


def _git_tree(entries: list[tuple[str, str, str]]) -> tuple[tuple[str, str], bytes]:
    raw = b"".join(
        mode.encode("ascii") + b" " + name.encode("utf-8") + b"\0" + bytes.fromhex(object_id)
        for mode, name, object_id in entries
    )
    return _git_object("tree", raw)


def _git_commit(tree: str, parent: str | None = None) -> tuple[tuple[str, str], bytes]:
    parent_header = b"" if parent is None else f"parent {parent}\n".encode("ascii")
    raw = (
        f"tree {tree}\n".encode("ascii")
        + parent_header
        + b"author Synthetic <synthetic@example.invalid> 0 +0000\n"
        + b"committer Synthetic <synthetic@example.invalid> 0 +0000\n\nsynthetic\n"
    )
    return _git_object("commit", raw)


def _pack_object_header(object_type: int, size: int) -> bytes:
    first = (object_type << 4) | (size & 0x0F)
    size >>= 4
    result = bytearray([first | (0x80 if size else 0)])
    while size:
        size, byte = size >> 7, size & 0x7F
        result.append(byte | (0x80 if size else 0))
    return bytes(result)


def _write_pack_fixture(
    root: Path,
    entries: list[tuple[str, int, bytes, str | None]],
) -> Path:
    pack = bytearray(b"PACK" + struct.pack(">II", 2, len(entries)))
    records: dict[str, tuple[int, int]] = {}
    for object_id, object_type, representation, base_object_id in entries:
        offset = len(pack)
        entry = bytearray(_pack_object_header(object_type, len(representation)))
        if base_object_id is not None:
            if object_type == 7:
                entry.extend(bytes.fromhex(base_object_id))
            elif object_type == 6:
                distance = offset - records[base_object_id][0]
                if not 0 < distance < 0x80:
                    raise AssertionError("synthetic OFS delta requires a one-byte distance")
                entry.append(distance)
            else:
                raise AssertionError("synthetic base identity is only valid for a delta")
        entry.extend(zlib.compress(representation))
        pack.extend(entry)
        records[object_id] = (offset, zlib.crc32(entry) & 0xFFFFFFFF)
    pack_digest = hashlib.sha1(pack, usedforsecurity=False).digest()
    pack.extend(pack_digest)

    ordered = sorted(records)
    fanout = [sum(bytes.fromhex(object_id)[0] <= first for object_id in ordered) for first in range(256)]
    index = bytearray(b"\xfftOc" + struct.pack(">I", 2))
    index.extend(struct.pack(">256I", *fanout))
    index.extend(b"".join(bytes.fromhex(object_id) for object_id in ordered))
    index.extend(struct.pack(f">{len(ordered)}I", *(records[object_id][1] for object_id in ordered)))
    index.extend(struct.pack(f">{len(ordered)}I", *(records[object_id][0] for object_id in ordered)))
    index.extend(pack_digest)
    index.extend(hashlib.sha1(index, usedforsecurity=False).digest())

    stem = f"pack-{pack_digest.hex()}"
    index_path = root / f"{stem}.idx"
    index_path.write_bytes(index)
    index_path.with_suffix(".pack").write_bytes(pack)
    index_ordinals = {object_id: ordinal for ordinal, object_id in enumerate(ordered)}
    reverse = bytearray(b"RIDX" + struct.pack(">II", 1, 1))
    reverse.extend(
        struct.pack(
            f">{len(entries)}I",
            *(index_ordinals[object_id] for object_id, _type, _raw, _base in entries),
        )
    )
    reverse.extend(pack_digest)
    reverse.extend(hashlib.sha1(reverse, usedforsecurity=False).digest())
    index_path.with_suffix(".rev").write_bytes(reverse)
    return index_path


def _write_loose_object(objects: Path, item: tuple[tuple[str, str], bytes]) -> None:
    (object_type, object_id), raw = item
    framed = object_type.encode("ascii") + b" " + str(len(raw)).encode("ascii") + b"\0" + raw
    path = objects / object_id[:2] / object_id[2:]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(zlib.compress(framed))


def _write_index_v2(
    path: Path,
    entries: list[tuple[str, str, str, int]],
) -> None:
    raw = bytearray(b"DIRC" + struct.pack(">II", 2, len(entries)))
    for name, mode, object_id, byte_count in entries:
        name_raw = name.encode("utf-8")
        start = len(raw)
        raw.extend(
            struct.pack(
                ">10I20sH",
                0,
                0,
                0,
                0,
                0,
                0,
                int(mode, 8),
                0,
                0,
                byte_count,
                bytes.fromhex(object_id),
                len(name_raw),
            )
        )
        raw.extend(name_raw + b"\0")
        raw.extend(b"\0" * ((-(len(raw) - start)) % 8))
    raw.extend(hashlib.sha1(raw, usedforsecurity=False).digest())
    path.write_bytes(raw)


class CanonicalAndIdentityTests(unittest.TestCase):
    def test_strict_canonical_json_and_exact_identity(self) -> None:
        value = {"z": [2, 1], "e\u0301": "cafe\u0301", "flag": True}
        expected = '{"flag":true,"z":[2,1],"é":"café"}'.encode("utf-8")
        self.assertEqual(canonical_bytes(value), expected)
        identity = sha256_identity("stage_f_test_synthetic/v1", value)
        self.assertEqual(identity["value"], identity["sha256"])
        self.assertEqual(identity["value"], canonical_digest(value))
        with self.assertRaises(BindingRefusal):
            strict_loads(b'{"duplicate":1,"duplicate":2}')
        with self.assertRaises(BindingRefusal):
            strict_loads(b'{"float":1.0}')
        with self.assertRaises(BindingRefusal):
            strict_loads(b'{"a":1}\n', require_canonical=True)
        with self.assertRaises(BindingRefusal):
            canonical_bytes({"é": 1, "e\u0301": 2})

    def test_embedded_digest_omits_exactly_one_field(self) -> None:
        record = {
            "schema": "stage_f_public_execution_host_binding/v1",
            "synthetic": True,
            "public_binding_sha256": "",
        }
        record["public_binding_sha256"] = canonical_digest(
            {key: value for key, value in record.items() if key != "public_binding_sha256"}
        )
        identity = verify_embedded_digest(
            record,
            "public_binding_sha256",
            kind="stage_f_public_execution_host_binding/v1",
        )
        self.assertEqual(identity["value"], record["public_binding_sha256"])
        changed = dict(record, synthetic=False)
        with self.assertRaises(BindingRefusal):
            verify_embedded_digest(changed, "public_binding_sha256")


class PrivacyBeforeAccessTests(unittest.TestCase):
    def test_retained_material_outside_root_refuses_before_open(self) -> None:
        locks = object.__new__(_RetainedMaterialLocks)
        locks._root = (
            r"\\?\Volume{01234567-89ab-cdef-0123-456789abcdef}"
            r"\stage-f\independent-audit\retained-evidence"
        )
        locks._root_folded = locks._root.casefold()
        locks._handles = {}
        locks._create_file = mock.Mock(
            side_effect=AssertionError("out-of-scope path was opened")
        )
        with self.assertRaises(BindingRefusal):
            locks._acquire(Path(r"\\attacker\share\credential-trigger"), "material")
        locks._create_file.assert_not_called()

    def test_extra_restart_filename_refuses_before_content_read(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            expected_challenge = (
                root / "stage-f-durability-aaaaaaaaaaaaaaaa-1-1.challenge.json"
            )
            expected_ack = (
                root
                / "stage-f-durability-aaaaaaaaaaaaaaaa-1-1.acknowledgement.json"
            )
            extra = root / "stage-f-durability-bbbbbbbbbbbbbbbb-2-2.challenge.json"
            for path in (expected_challenge, expected_ack, extra):
                path.write_bytes(b"untrusted bytes must not be read")
            challenge_raw = os.fspath(expected_challenge).encode("utf-8")
            acknowledgement_raw = os.fspath(expected_ack).encode("utf-8")
            challenge_identity = sha256_identity(
                "stage_f_private_path/v1", challenge_raw
            )
            acknowledgement_identity = sha256_identity(
                "stage_f_private_path/v1", acknowledgement_raw
            )
            materials = {
                (challenge_identity["kind"], challenge_identity["value"]): challenge_raw,
                (
                    acknowledgement_identity["kind"],
                    acknowledgement_identity["value"],
                ): acknowledgement_raw,
            }
            receipt = {
                "restart_observation": {
                    "challenge_path_identity": challenge_identity,
                    "acknowledgement_path_identity": acknowledgement_identity,
                }
            }
            manifest = {
                "filesystem": {
                    "private_directories": {"temporary": os.fspath(root)}
                }
            }
            with (
                mock.patch(
                    "scripts.validate_stage_f_local_binding._normalized_volume_guid_path",
                    side_effect=lambda path, _label: os.fspath(path),
                ),
                mock.patch.object(
                    Path,
                    "read_bytes",
                    side_effect=AssertionError("unexpected content read"),
                ),
                self.assertRaises(BindingRefusal),
            ):
                _verify_complete_challenge_history(
                    mock.Mock(), manifest, [receipt], materials
                )

    def test_scientific_record_chain_requires_every_authorization_record(self) -> None:
        parser = _parser()
        record_chain = next(
            action.choices["record-chain"]
            for action in parser._actions
            if getattr(action, "choices", None)
            and "record-chain" in action.choices
        )
        readiness_chain = next(
            action.choices["readiness-chain"]
            for action in parser._actions
            if getattr(action, "choices", None)
            and "readiness-chain" in action.choices
        )
        authorization_options = {
            "--preaudit-readiness",
            "--independent-audit",
            "--pass-readiness",
            "--packet",
            "--user-receipt",
            "--authorization",
            "--retained-statement",
        }
        record_required = {
            option
            for action in record_chain._actions
            if action.required
            for option in action.option_strings
        }
        readiness_required = {
            option
            for action in readiness_chain._actions
            if action.required
            for option in action.option_strings
        }
        self.assertTrue(authorization_options.issubset(record_required))
        self.assertTrue(authorization_options.isdisjoint(readiness_required))

    def test_future_capacity_or_power_time_refuses_against_live_clock(self) -> None:
        now = datetime.now(timezone.utc)
        _require_not_future_utc(
            (now - timedelta(seconds=1)).isoformat().replace("+00:00", "Z"),
            not_after=now,
            label="synthetic past observation",
        )
        with self.assertRaises(BindingRefusal):
            _require_not_future_utc(
                (now + timedelta(seconds=1)).isoformat().replace("+00:00", "Z"),
                not_after=now,
                label="synthetic future observation",
            )


class VerifiedGitRepositoryTests(unittest.TestCase):
    def test_builder_git_acquisition_has_no_external_process_route(self) -> None:
        raw = (ROOT / "scripts" / "build_stage_f_local_binding.py").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("--git-executable", raw)
        tree = ast.parse(raw)
        imported_modules = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        } | {
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module is not None
        }
        self.assertNotIn("subprocess", imported_modules)
        self.assertFalse(
            any(
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "os"
                and node.func.attr in {"popen", "spawnl", "spawnle", "spawnlp", "spawnlpe", "spawnv", "spawnve", "spawnvp", "spawnvpe", "system"}
                for node in ast.walk(tree)
            )
        )

    def test_git_batch_transport_parses_exact_content_addresses(self) -> None:
        blob = _git_object("blob", b"transport")
        object_id = blob[0][1]
        batch = f"{object_id} blob 9\n".encode("ascii") + b"transport\n"
        self.assertEqual(
            _parse_git_batch(batch, [object_id]), [("blob", object_id, b"transport")]
        )
        with self.assertRaises(BuildRefusal):
            _parse_git_batch(batch + b"extra", [object_id])

    def test_pure_object_store_reads_exact_loose_object_and_rejects_corruption(self) -> None:
        raw = b"pure-python-loose-object\n"
        object_id = _git_sha1("blob", raw)
        framed = b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw
        with tempfile.TemporaryDirectory() as temporary:
            objects = Path(temporary)
            path = objects / object_id[:2] / object_id[2:]
            path.parent.mkdir()
            path.write_bytes(zlib.compress(framed))

            store = object.__new__(_GitObjectStore)
            store.objects = objects
            store._cache = {}
            store._packed = {}
            self.assertEqual(store.read_object(object_id), ("blob", raw))

            path.write_bytes(zlib.compress(framed + b"corrupt"))
            replacement = object.__new__(_GitObjectStore)
            replacement.objects = objects
            replacement._cache = {}
            replacement._packed = {}
            with self.assertRaisesRegex(BuildRefusal, "size differs|content address differs"):
                replacement.read_object(object_id)

    def test_pure_pack_reader_validates_index_crc_and_ref_delta(self) -> None:
        base = b"alpha"
        result = b"alphabeta"
        base_id = _git_sha1("blob", base)
        result_id = _git_sha1("blob", result)
        ofs_result = b"alphaomega"
        ofs_result_id = _git_sha1("blob", ofs_result)
        delta = b"\x05\x09\x90\x05\x04beta"
        ofs_delta = b"\x05\x0a\x90\x05\x05omega"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            index_path = _write_pack_fixture(
                root,
                [
                    (base_id, 3, base, None),
                    (result_id, 7, delta, base_id),
                    (ofs_result_id, 6, ofs_delta, base_id),
                ],
            )
            pack = _PackIndex(index_path)
            store = object.__new__(_GitObjectStore)
            store.objects = root / "objects"
            store.objects.mkdir()
            store._cache = {}
            store._packed = {base_id: pack, result_id: pack, ofs_result_id: pack}
            self.assertEqual(store.read_object(result_id), ("blob", result))
            self.assertEqual(store.read_object(ofs_result_id), ("blob", ofs_result))

            reverse_path = index_path.with_suffix(".rev")
            raw_reverse = bytearray(reverse_path.read_bytes())
            raw_reverse[12] ^= 1
            reverse_path.write_bytes(raw_reverse)
            with self.assertRaisesRegex(BuildRefusal, "reverse index framing or checksum"):
                _PackIndex(index_path)
            raw_reverse[12] ^= 1
            reverse_path.write_bytes(raw_reverse)

            raw_pack = bytearray(index_path.with_suffix(".pack").read_bytes())
            raw_pack[12] ^= 1
            index_path.with_suffix(".pack").write_bytes(raw_pack)
            with self.assertRaisesRegex(BuildRefusal, "checksum differs"):
                _PackIndex(index_path)

    def test_checkout_byte_rule_is_exact_lf_or_core_autocrlf_projection(self) -> None:
        blob = b"first\nsecond\n"
        self.assertTrue(_GitObjectStore._checkout_bytes_match(blob, blob))
        self.assertTrue(
            _GitObjectStore._checkout_bytes_match(blob, b"first\r\nsecond\r\n")
        )
        self.assertFalse(
            _GitObjectStore._checkout_bytes_match(blob, b"first\r\nsecond\n")
        )
        self.assertFalse(
            _GitObjectStore._checkout_bytes_match(b"binary\0\n", b"binary\0\r\n")
        )

    def test_pure_store_binds_head_index_and_complete_checkout_without_git(self) -> None:
        blob = _git_object("blob", b"tracked\n")
        tree = _git_tree([("100644", "tracked.txt", blob[0][1])])
        commit = _git_commit(tree[0][1])
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            admin = root / ".git"
            objects = admin / "objects"
            (admin / "refs" / "heads").mkdir(parents=True)
            objects.mkdir()
            (admin / "config").write_bytes(
                b"[core]\n\trepositoryformatversion = 0\n\tbare = false\n"
            )
            (admin / "HEAD").write_bytes(b"ref: refs/heads/main\n")
            (admin / "refs" / "heads" / "main").write_bytes(
                commit[0][1].encode("ascii") + b"\n"
            )
            for item in (blob, tree, commit):
                _write_loose_object(objects, item)
            _write_index_v2(
                admin / "index",
                [("tracked.txt", "100644", blob[0][1], len(blob[1]))],
            )
            (root / "tracked.txt").write_bytes(b"tracked\r\n")

            store = _GitObjectStore.open_worktree(root)
            self.assertEqual(store.head_commit(), commit[0][1])
            store.assert_clean_checkout(commit[0][1])

            (root / "untracked.txt").write_bytes(b"must refuse\n")
            with self.assertRaisesRegex(BuildRefusal, "missing, extra, or ignored"):
                store.assert_clean_checkout(commit[0][1])

            pack = objects / "pack"
            pack.mkdir()
            (pack / "pack-forbidden.bitmap").write_bytes(b"must refuse")
            with self.assertRaisesRegex(BuildRefusal, "unsupported Git pack-directory"):
                _GitObjectStore.open_worktree(root)

    def test_linked_worktree_admin_must_be_contained_and_point_back(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "worktree"
            admin = root / "escaped-admin"
            common = root / "common"
            source.mkdir()
            admin.mkdir()
            (common / "worktrees").mkdir(parents=True)
            (common / "objects").mkdir()
            (source / ".git").write_bytes(
                f"gitdir: {admin}\n".encode("utf-8")
            )
            (admin / "commondir").write_bytes(b"../common\n")
            (admin / "gitdir").write_bytes(
                f"{source / '.git'}\n".encode("utf-8")
            )
            with self.assertRaisesRegex(BuildRefusal, "escapes common/worktrees"):
                _GitObjectStore.open_worktree(source)

    def test_raw_objects_reconstruct_ancestry_rows_and_additive_diff(self) -> None:
        blob_a = _git_object("blob", b"alpha\n")
        blob_b = _git_object("blob", b"beta\n")
        base_tree = _git_tree([("100644", "a.txt", blob_a[0][1])])
        base_commit = _git_commit(base_tree[0][1])
        target_tree = _git_tree(
            [
                ("100644", "a.txt", blob_a[0][1]),
                ("100644", "b.txt", blob_b[0][1]),
            ]
        )
        target_commit = _git_commit(target_tree[0][1], base_commit[0][1])
        repository = VerifiedGitRepository(
            dict((blob_a, blob_b, base_tree, base_commit, target_tree, target_commit))
        )
        self.assertEqual(repository.tree_id(base_commit[0][1]), base_tree[0][1])
        self.assertTrue(repository.is_ancestor(base_commit[0][1], target_commit[0][1]))
        self.assertEqual(
            repository.recursive_paths(target_commit[0][1]), ["a.txt", "b.txt"]
        )
        self.assertEqual(
            repository.diff_status(base_commit[0][1], target_commit[0][1]),
            [("A", "b.txt")],
        )
        row = repository.row(
            target_commit[0][1], "b.txt", allowed_modes=frozenset({"100644"})
        )
        self.assertEqual(row["git_object"], blob_b[0][1])
        self.assertEqual(row["raw_sha256"], hashlib.sha256(b"beta\n").hexdigest())
        repository.assert_material_closure((base_commit[0][1], target_commit[0][1]))

        extra = _git_object("blob", b"unreachable")
        repository = VerifiedGitRepository(
            dict(
                (
                    blob_a,
                    blob_b,
                    base_tree,
                    base_commit,
                    target_tree,
                    target_commit,
                    extra,
                )
            )
        )
        with self.assertRaises(BindingRefusal):
            repository.assert_material_closure((base_commit[0][1], target_commit[0][1]))

    def test_wrong_content_address_and_noncanonical_tree_order_refuse(self) -> None:
        with self.assertRaises(BindingRefusal):
            VerifiedGitRepository({("blob", "0" * 40): b"not-zero"})
        blob_a = _git_object("blob", b"a")
        blob_b = _git_object("blob", b"b")
        reversed_tree = _git_tree(
            [
                ("100644", "b", blob_b[0][1]),
                ("100644", "a", blob_a[0][1]),
            ]
        )
        commit = _git_commit(reversed_tree[0][1])
        repository = VerifiedGitRepository(
            dict((blob_a, blob_b, reversed_tree, commit))
        )
        with self.assertRaises(BindingRefusal):
            repository.tree_map(commit[0][1])

    def test_commit_header_order_is_semantic_and_message_cr_is_opaque(self) -> None:
        blob = _git_object("blob", b"value")
        tree = _git_tree([("100644", "value.txt", blob[0][1])])
        parent = _git_commit(tree[0][1])
        late_parent_raw = (
            f"tree {tree[0][1]}\n".encode("ascii")
            + b"author Synthetic <synthetic@example.invalid> 0 +0000\n"
            + f"parent {parent[0][1]}\n".encode("ascii")
            + b"committer Synthetic <synthetic@example.invalid> 0 +0000\n\nlate parent\n"
        )
        late_parent = _git_object("commit", late_parent_raw)
        repository = VerifiedGitRepository(dict((blob, tree, parent, late_parent)))
        with self.assertRaises(BindingRefusal):
            repository.commit(late_parent[0][1])

        cr_message_raw = (
            f"tree {tree[0][1]}\n".encode("ascii")
            + f"parent {parent[0][1]}\n".encode("ascii")
            + b"author Synthetic <synthetic@example.invalid> 0 +0000\n"
            + b"committer Synthetic <synthetic@example.invalid> 0 +0000\n\nmessage\rbytes\n"
        )
        cr_message = _git_object("commit", cr_message_raw)
        repository = VerifiedGitRepository(dict((blob, tree, parent, cr_message)))
        self.assertEqual(repository.commit(cr_message[0][1])[1], (parent[0][1],))

    def test_merge_ancestry_uses_verified_available_witness_paths(self) -> None:
        blob = _git_object("blob", b"merge")
        tree = _git_tree([("100644", "merge.txt", blob[0][1])])
        first = _git_commit(tree[0][1])
        second = _git_commit(tree[0][1], first[0][1])
        merge_raw = (
            f"tree {tree[0][1]}\n".encode("ascii")
            + f"parent {first[0][1]}\nparent {second[0][1]}\n".encode("ascii")
            + b"author Synthetic <synthetic@example.invalid> 0 +0000\n"
            + b"committer Synthetic <synthetic@example.invalid> 0 +0000\n\nmerge\n"
        )
        merge = _git_object("commit", merge_raw)
        repository = VerifiedGitRepository(dict((blob, tree, first, second, merge)))
        self.assertTrue(repository.is_ancestor(first[0][1], merge[0][1]))
        self.assertTrue(repository.is_ancestor(second[0][1], merge[0][1]))

        missing_second = VerifiedGitRepository(dict((blob, tree, first, merge)))
        self.assertTrue(missing_second.is_ancestor(first[0][1], merge[0][1]))
        with self.assertRaises(BindingRefusal):
            missing_second.is_ancestor(second[0][1], merge[0][1])

    def test_material_loader_rejects_unreachable_extra_without_reading_it(self) -> None:
        blob = _git_object("blob", b"retained")
        tree = _git_tree([("100644", "retained.txt", blob[0][1])])
        commit = _git_commit(tree[0][1])
        extra = _git_object("blob", b"forbidden-private-outcome-bytes")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            objects = root / "verified-git-objects"
            objects.mkdir()
            entries: list[dict[str, object]] = []
            paths: dict[tuple[str, str], Path] = {}
            for key, raw in (blob, tree, commit, extra):
                object_type, object_id = key
                path = objects / f"{object_type}-{object_id}.raw"
                path.write_bytes(raw)
                paths[key] = path
                entries.append(
                    {
                        "object_type": object_type,
                        "object_id": object_id,
                        "byte_count": len(raw),
                        "raw_sha256": hashlib.sha256(raw).hexdigest(),
                        "path": str(path),
                    }
                )
            entries.sort(
                key=lambda entry: (
                    str(entry["object_type"]).encode("ascii"),
                    str(entry["object_id"]).encode("ascii"),
                )
            )
            index = root / "verified-git-object-material-index.json"
            index.write_bytes(
                canonical_bytes(
                    {
                        "schema": "stage_f_verified_git_object_material_index/v1",
                        "entries": entries,
                        "entry_count": len(entries),
                    }
                )
            )
            original_read_bytes = Path.read_bytes
            forbidden_path = paths[extra[0]]

            def guarded_read_bytes(path: Path) -> bytes:
                if path == forbidden_path:
                    self.fail("unreachable Git material was inspected before refusal")
                return original_read_bytes(path)

            with mock.patch.object(Path, "read_bytes", guarded_read_bytes):
                repository = _load_verified_git_repository(index)
                with self.assertRaises(BindingRefusal):
                    repository.assert_material_closure((commit[0][1],))

    def test_material_loader_refuses_directory_entries_without_opening_them(self) -> None:
        blob = _git_object("blob", b"retained")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            objects = root / "verified-git-objects"
            objects.mkdir()
            object_type, object_id = blob[0]
            path = objects / f"{object_type}-{object_id}.raw"
            path.write_bytes(blob[1])
            (objects / "unexpected-directory").mkdir()
            index = root / "verified-git-object-material-index.json"
            index.write_bytes(
                canonical_bytes(
                    {
                        "schema": "stage_f_verified_git_object_material_index/v1",
                        "entries": [
                            {
                                "object_type": object_type,
                                "object_id": object_id,
                                "byte_count": len(blob[1]),
                                "raw_sha256": hashlib.sha256(blob[1]).hexdigest(),
                                "path": str(path),
                            }
                        ],
                        "entry_count": 1,
                    }
                )
            )
            with self.assertRaisesRegex(BindingRefusal, "directory, or special entry"):
                _load_verified_git_repository(index)

    def test_unconsumed_identity_material_refuses_without_reading_target(self) -> None:
        raw = b"private-outcome-bytes"
        identity = sha256_identity("stage_f_test_synthetic/v1", raw)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "private.bin"
            target.write_bytes(raw)
            index = root / "identity-index.json"
            index.write_bytes(
                canonical_bytes(
                    {
                        "schema": "stage_f_binding_identity_material_index/v1",
                        "entries": [
                            {
                                "identity": identity,
                                "encoding": "RAW_BYTES",
                                "path": str(target),
                            }
                        ],
                        "entry_count": 1,
                    }
                )
            )
            original_read_bytes = Path.read_bytes

            def guarded_read_bytes(path: Path) -> bytes:
                if path == target:
                    self.fail("unconsumed identity material target was inspected")
                return original_read_bytes(path)

            with mock.patch.object(Path, "read_bytes", guarded_read_bytes):
                materials = _load_identity_materials(index)
                with self.assertRaises(BindingRefusal):
                    materials.assert_complete_consumption()


class SyntheticPrivatePublicBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.validator = ClosedSchemaValidator(_load_json(SCHEMA_PATH))
        cls.private_manifest = _load_json(FIXTURES / "synthetic_private_host_manifest.json")

    def _public_binding(self) -> dict[str, object]:
        projection = validate_private_host_manifest(self.validator, self.private_manifest)
        policies = projection["policy_identities"]
        record: dict[str, object] = {
            "schema": "stage_f_public_execution_host_binding/v1",
            "public_host_alias": "EXECUTION-HOST-01",
            "private_host_manifest_identity": projection["manifest_identity"],
            "environment_identity": policies["environment"],
            "host_validation_runtime_identity": projection["host_validation_runtime_identity"],
            "parallelization_boundary_identity": policies["parallelization_boundary"],
            "worker_allocation_policy_identity": policies["worker_allocation"],
            "storage_location_identity": policies["storage_location"],
            "durability_policy_identity": policies["durability"],
            "restart_policy_identity": policies["restart"],
            "private_durability_bundle_identity": self.private_manifest["durability_bundle_identity"],
            "filesystem_identity": projection["filesystem_identity"],
            "storage_inventory_policy_identity": policies["storage_inventory"],
            "logical_directory_roles": [
                "immutable-results",
                "continuation-checkpoints",
                "independent-audit",
                "temporary",
            ],
            "storage_envelope": {
                "bytes_per_gib": 1073741824,
                "primary_logical_output_gib": 253,
                "independent_audit_copy_gib": 253,
                "dynamic_growth_physical_writes_gib": 80,
                "checkpoint_and_write_overhead_gib": 64,
                "temporary_archives_gib": 8,
                "retained_evidence_gib": 8,
                "total_gib": 666,
                "minimum_free_after_existing_data_gib": 350,
            },
            "private_manifest_retained": True,
            "independent_private_byte_audit_required": True,
            "sensitive_field_disclosure_count": 0,
            "outcome_inspected": False,
            "scientific_counters": dict(ZERO_SCIENCE_COUNTERS),
            "public_binding_sha256": "",
        }
        record["public_binding_sha256"] = canonical_digest(
            {key: value for key, value in record.items() if key != "public_binding_sha256"}
        )
        return record

    def test_synthetic_private_manifest_and_digest_only_public_projection(self) -> None:
        public = self._public_binding()
        identity = validate_public_host_binding(
            self.validator, public, private_manifest=self.private_manifest
        )
        self.assertEqual(identity["kind"], "stage_f_public_execution_host_binding/v1")
        self.assertEqual(identity["value"], public["public_binding_sha256"])
        public_bytes = canonical_bytes(public)
        for private_value in (
            self.private_manifest["host"]["computer_name"],
            self.private_manifest["host"]["user_name"],
        ):
            self.assertNotIn(private_value.encode("utf-8"), public_bytes)

    def test_private_public_substitution_and_nonzero_science_refuse(self) -> None:
        public = self._public_binding()
        public["environment_identity"] = sha256_identity(
            "stage_f_execution_environment_policy/v1", {"different": True}
        )
        public["public_binding_sha256"] = canonical_digest(
            {key: value for key, value in public.items() if key != "public_binding_sha256"}
        )
        with self.assertRaises(BindingRefusal):
            validate_public_host_binding(
                self.validator, public, private_manifest=self.private_manifest
            )
        changed = copy.deepcopy(self.private_manifest)
        changed["scientific_counters"]["runner_import_count"] = 1
        with self.assertRaises(BindingRefusal):
            validate_private_host_manifest(self.validator, changed)


class PortfolioAndInactiveAuthorizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.validator = ClosedSchemaValidator(_load_json(SCHEMA_PATH))

    def _unsealed_portfolio(self) -> list[dict[str, object]]:
        rows: list[dict[str, object]] = []
        for route_id in CAMPAIGN_ORDER:
            rows.append(
                {
                    "route_id": route_id,
                    "study_id": "SD-01" if route_id == "SD-01-GROWTH-v1" else route_id,
                    "campaign_id": route_id,
                    "campaign_execution_binding_file_identity": None,
                    "campaign_execution_binding_identity": None,
                    "seal_status": "UNSEALED_AUTHORITY_GAP",
                    "unresolved_authority_ids": list(ACCEPTED_GAPS[route_id]),
                }
            )
        return rows

    def test_exact_fifteen_route_order_and_nested_growth(self) -> None:
        rows = self._unsealed_portfolio()
        validate_route_portfolio(self.validator, rows)
        rows[0], rows[1] = rows[1], rows[0]
        with self.assertRaises(BindingRefusal):
            validate_route_portfolio(self.validator, rows)
        rows = self._unsealed_portfolio()
        rows[1]["study_id"] = "SD-02"
        with self.assertRaises(BindingRefusal):
            validate_route_portfolio(self.validator, rows)

    def test_all_67_frozen_negative_controls_are_contiguous_and_refuse(self) -> None:
        registry = _load_json(FIXTURES / "negative_cases.json")
        self.assertEqual(registry["schema"], "stage_f_binding_negative_cases/v1")
        self.assertEqual(registry["case_count"], 67)
        self.assertEqual(len(registry["cases"]), 67)
        self.assertEqual(
            [case["case_id"] for case in registry["cases"]],
            [f"SF-BIND-N{number:02d}" for number in range(1, 68)],
        )
        self.assertTrue(all(case["disposition"] == "REFUSE" for case in registry["cases"]))

    def test_import_surface_and_incomplete_authorization_remain_inactive(self) -> None:
        prohibited = {
            "ebu_framework",
            "stage_e_harness",
            "ebu_framework.runner",
            "stage_e_harness.runner",
        }
        self.assertTrue(prohibited.isdisjoint(sys.modules))
        signature = inspect.signature(assert_preimport_authorized)
        self.assertEqual(signature.parameters["identity_preimages"].kind, inspect.Parameter.KEYWORD_ONLY)
        self.assertIs(signature.parameters["identity_preimages"].default, inspect.Parameter.empty)
        self.assertEqual(signature.parameters["referenced_bindings"].kind, inspect.Parameter.KEYWORD_ONLY)
        self.assertIs(signature.parameters["referenced_bindings"].default, inspect.Parameter.empty)
        self.assertIn(
            "in-process pre-import authorization is forbidden",
            inspect.getsource(assert_preimport_authorized),
        )
        with self.assertRaises(BindingRefusal):
            self.validator.validate_definition("campaign_authorization", {})


if __name__ == "__main__":
    unittest.main()
