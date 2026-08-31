from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
import os
import platform
import re
import stat
import struct
import sys
import unicodedata
import zipfile
import zlib
from pathlib import Path


SOURCE_PATHS = (
    "scripts/build_stage_f_local_binding.py",
    "scripts/validate_stage_f_local_binding.py",
    "stage_f_binding/__init__.py",
    "stage_f_binding/canonical.py",
    "stage_f_binding/binding.py",
    "stage_f_binding/durability.py",
    "stage_f_binding/locked_zipapp_bootstrap.py",
)
IMPLEMENTATION_PATHS = (
    ".github/workflows/tests.yml",
    "scripts/validate_stage_e_harness.py",
    *SOURCE_PATHS,
    "tests/stage_f_binding/__init__.py",
    "tests/stage_f_binding/fixtures/negative_cases.json",
    "tests/stage_f_binding/fixtures/synthetic_private_host_manifest.json",
    "tests/stage_f_binding/test_binding_privacy_and_authorization.py",
    "tests/stage_f_binding/test_durability_and_no_science.py",
)
ZIPAPP_PATHS = (
    ("__main__.py", "scripts/validate_stage_f_local_binding.py"),
    ("stage_f_binding/__init__.py", "stage_f_binding/__init__.py"),
    ("stage_f_binding/canonical.py", "stage_f_binding/canonical.py"),
    ("stage_f_binding/binding.py", "stage_f_binding/binding.py"),
    ("stage_f_binding/durability.py", "stage_f_binding/durability.py"),
)
SOURCE_BUNDLE_NAME = "stage-f-binding-validator-source-bundle.json"
ZIPAPP_NAME = "stage-f-binding-validator.pyz"
AUTHORITY_SCHEMA_PATH = (
    "stage_f_local_execution_binding_final_evidence_closure_correction_schema.json"
)
MATERIALIZED_SCHEMA_NAME = "stage-f-local-execution-binding-evidence-schema.json"
GIT_OBJECT_DIRECTORY_NAME = "verified-git-objects"
GIT_OBJECT_INDEX_NAME = "verified-git-object-material-index.json"
AUTHORITY_SCHEMA_GIT_OBJECT = "db8268a009ed4a20e056f62f236c12d1b0f7c131"
AUTHORITY_SCHEMA_BYTE_COUNT = 833194
AUTHORITY_SCHEMA_SHA256 = "b3bc610e1e6ded0e75de13ac30c36dafd72d3432fd9517cb80815ecb07396b67"
AUTHORITY_SCHEMA_DEFINITION_COUNT = 228
AUTHORITY_SCHEMA_LOCAL_REFERENCE_COUNT = 2431
AUTHORITY_SCHEMA_ROOT_VARIANT_COUNT = 46
ACCEPTED_BASE_COMMIT = "c43ead831c3e4021405985134ed564b761bb1aed"
ACCEPTED_BASE_TREE = "212777d569af527ce9532ea6c836ff2225465d87"
DESCENDANT_PATH_BASE_COMMIT = "b7ebe8615d54ae5e23645734b1a6c7667ce28bce"
DESCENDANT_PATH_BASE_TREE = "24f2693b6d26d42bf9e360b295e3209a16417f74"
ORIGINAL_AUTHORITY_CANDIDATE_COMMIT = "c683040869ecbbe439835a8fabd0a6c3d7ea0e3d"
ORIGINAL_AUTHORITY_CANDIDATE_TREE = "46ce30f0c3675836b449bc2fb00ae22a688ca287"
ORIGINAL_AUTHORITY_INTEGRATION_COMMIT = "4ab6a8a8b158e6ff32d06e67d29a3d974a6326be"
ORIGINAL_AUTHORITY_INTEGRATION_TREE = "46ce30f0c3675836b449bc2fb00ae22a688ca287"
CORRECTION_REQUIRED_TARGET_COMMIT = "1033501b77f7f55ed9aacd9a71cef95f81966e4a"
CORRECTION_REQUIRED_TARGET_TREE = "d8ffbd105eb76cfbb72472772e07f18a11112db3"
CORRECTION_AUTHORITY_CANDIDATE_COMMIT = "dd1a38aee4a6c1048122cb2b5a4e7cf542c5e101"
CORRECTION_AUTHORITY_INTEGRATION_COMMIT = "db9d305be120e69d00be14f0d07e06999ca77999"
CORRECTION_AUTHORITY_INTEGRATION_TREE = "c5d6e6c53528ae64a90151d286feb2cc62be47be"
REACHABILITY_CANDIDATE_COMMIT = "0b618dafd1cbc795d9b05038a0d298552b5eb372"
REACHABILITY_INTEGRATION_COMMIT = "f47648320be2054edf51a166b0e7fd7e9ab20594"
REACHABILITY_INTEGRATION_TREE = "382472276e7fbb7b483cc120467f23f83bc25ca3"
FINAL_AUTHORITY_REQUIRED_TARGET_COMMIT = REACHABILITY_INTEGRATION_COMMIT
FINAL_AUTHORITY_REQUIRED_TARGET_TREE = REACHABILITY_INTEGRATION_TREE
FINAL_AUTHORITY_CANDIDATE_COMMIT = "b6452dcf69cb9ee46ce01b03f86d97a80c348713"
FINAL_AUTHORITY_CANDIDATE_TREE = "bd9e8610b70b9f06f15fb18d9045d2cb933e173a"
FINAL_AUTHORITY_INTEGRATION_COMMIT = "1f4650411ea360d82df3e9f0708af32a58608729"
FINAL_AUTHORITY_INTEGRATION_TREE = FINAL_AUTHORITY_CANDIDATE_TREE
FINAL_REACHABILITY_CANDIDATE_COMMIT = "4dc2d9d5fac43bb91699a0727eb36f7266996122"
FINAL_REACHABILITY_CANDIDATE_TREE = "ca0bd70c96c0a6d9542ce9656be78a11465662f3"
FINAL_REACHABILITY_INTEGRATION_COMMIT = "06a1b1400d5bd15cdfb50363333602c58b5ac692"
FINAL_REACHABILITY_INTEGRATION_TREE = FINAL_REACHABILITY_CANDIDATE_TREE
REJECTED_FOUNDATION_COMMITS = (
    "0748e88d76ba8c2d86c41f4d7b8d632960041a1c",
    "c6e659305713ba462dbadc54d37d704e2e4de168",
)
ORIGINAL_AUTHORITY_PATHS = (
    "STAGE_F_LOCAL_EXECUTION_BINDING_AUTHORITY_AMENDMENT.md",
    "stage_f_local_execution_binding_contract.json",
    "stage_f_local_execution_binding_evidence_schema.json",
    "stage_f_local_execution_binding_implementation_path_manifest.json",
    "stage_f_local_execution_binding_predecessor_manifest.json",
    "stage_f_local_execution_binding_validation_contract.json",
)
CORRECTION_AUTHORITY_PATHS = (
    "STAGE_F_LOCAL_EXECUTION_BINDING_EVIDENCE_CORRECTION_AUTHORITY_AMENDMENT.md",
    "stage_f_local_execution_binding_evidence_correction_contract.json",
    "stage_f_local_execution_binding_evidence_correction_schema.json",
    "stage_f_local_execution_binding_evidence_correction_implementation_path_manifest.json",
    "stage_f_local_execution_binding_evidence_correction_predecessor_manifest.json",
    "stage_f_local_execution_binding_evidence_correction_validation_contract.json",
)
FINAL_AUTHORITY_PATHS = (
    "STAGE_F_LOCAL_EXECUTION_BINDING_FINAL_EVIDENCE_CLOSURE_CORRECTION_AUTHORITY_AMENDMENT.md",
    "stage_f_local_execution_binding_final_evidence_closure_correction_contract.json",
    "stage_f_local_execution_binding_final_evidence_closure_correction_schema.json",
    "stage_f_local_execution_binding_final_evidence_closure_correction_implementation_path_manifest.json",
    "stage_f_local_execution_binding_final_evidence_closure_correction_predecessor_manifest.json",
    "stage_f_local_execution_binding_final_evidence_closure_correction_validation_contract.json",
)
AUTHORITY_PATHS = (
    ORIGINAL_AUTHORITY_PATHS + CORRECTION_AUTHORITY_PATHS + FINAL_AUTHORITY_PATHS
)
STAGE_E_PATH_MANIFEST = (
    "stage_e_dynamic_growth_harness_reconciliation_implementation_path_manifest.json"
)
REACHABILITY_PATH = "tests/framework/test_validation_reachability.py"
SHA256_RE = re.compile(r"[0-9a-f]{64}")
GIT_OBJECT_RE = re.compile(r"[0-9a-f]{40}")
PACK_FILE_RE = re.compile(r"pack-([0-9a-f]{40})\.(idx|pack|rev)")
IDENTITY_PROJECTION_KEYS = frozenset(
    {
        "schema",
        "binding_implementation_identity",
        "execution_environment_policy_identity",
        "host_validation_runtime_identity",
    }
)


class BuildRefusal(RuntimeError):
    pass


def _normalize(value: object) -> object:
    if value is None or type(value) in {bool, int}:
        return value
    if type(value) is float:
        raise BuildRefusal("floating-point JSON values are forbidden")
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value)
    if isinstance(value, (list, tuple)):
        return [_normalize(item) for item in value]
    if isinstance(value, dict):
        normalized: dict[str, object] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise BuildRefusal("canonical JSON object keys must be strings")
            normalized_key = unicodedata.normalize("NFC", key)
            if normalized_key in normalized:
                raise BuildRefusal("duplicate canonical JSON object key")
            normalized[normalized_key] = _normalize(item)
        return normalized
    raise BuildRefusal(f"unsupported canonical JSON type: {type(value).__name__}")


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        _normalize(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8", "strict")


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _identity(kind: str, preimage: object) -> dict[str, str]:
    digest = _sha256(_canonical_bytes(preimage))
    if SHA256_RE.fullmatch(digest) is None:
        raise BuildRefusal("invalid SHA-256 implementation result")
    return {"kind": kind, "value": digest, "sha256": digest}


def _reject_float(value: str) -> None:
    raise BuildRefusal(f"floating-point JSON value is forbidden: {value}")


def _reject_constant(value: str) -> None:
    raise BuildRefusal(f"non-finite JSON value is forbidden: {value}")


def _pairs_no_duplicates(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise BuildRefusal(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _strict_canonical_json(path: Path) -> object:
    raw = path.read_bytes()
    try:
        value = json.loads(
            raw.decode("utf-8", "strict"),
            object_pairs_hook=_pairs_no_duplicates,
            parse_int=int,
            parse_float=_reject_float,
            parse_constant=_reject_constant,
        )
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise BuildRefusal(f"identity projection is not strict UTF-8 JSON: {exc}") from exc
    if _canonical_bytes(value) != raw:
        raise BuildRefusal("identity projection bytes are not canonical JSON")
    return value


def _strict_json_blob(raw: bytes, label: str) -> object:
    try:
        value = json.loads(
            raw.decode("utf-8", "strict"),
            object_pairs_hook=_pairs_no_duplicates,
            parse_float=_reject_float,
            parse_constant=_reject_constant,
        )
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise BuildRefusal(f"{label} is not strict UTF-8 JSON") from exc
    return value


def _count_local_references(value: object) -> int:
    if isinstance(value, dict):
        count = 0
        for key, item in value.items():
            if key == "$ref":
                if not isinstance(item, str) or not item.startswith("#/$defs/"):
                    raise BuildRefusal("authority schema contains a nonlocal reference")
                count += 1
            count += _count_local_references(item)
        return count
    if isinstance(value, list):
        return sum(_count_local_references(item) for item in value)
    return 0


def _assert_effective_schema(raw: bytes) -> None:
    schema = _strict_json_blob(raw, "effective Stage F authority schema")
    if (
        type(schema) is not dict
        or schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema"
        or schema.get("$id")
        != "https://ebu.example/schema/stage-f-local-execution-binding-final-evidence-closure-correction-v3.json"
        or schema.get("schema_version") != "3.0.0-candidate"
        or schema.get("scientific_execution_count") != 0
        or type(schema.get("$defs")) is not dict
        or len(schema["$defs"]) != AUTHORITY_SCHEMA_DEFINITION_COUNT
        or type(schema.get("oneOf")) is not list
        or len(schema["oneOf"]) != AUTHORITY_SCHEMA_ROOT_VARIANT_COUNT
        or _count_local_references(schema) != AUTHORITY_SCHEMA_LOCAL_REFERENCE_COUNT
    ):
        raise BuildRefusal("effective Stage F authority schema counts or roots differ")


def _checked_identity(value: object, kind: str, label: str) -> dict[str, str]:
    if (
        type(value) is not dict
        or set(value) != {"kind", "value", "sha256"}
        or value.get("kind") != kind
        or not isinstance(value.get("value"), str)
        or SHA256_RE.fullmatch(value["value"]) is None
        or value.get("sha256") != value.get("value")
    ):
        raise BuildRefusal(f"{label} is not the exact digest-only identity")
    return dict(value)


def _load_identity_projection(path: Path) -> dict[str, dict[str, str]]:
    value = _strict_canonical_json(path.resolve(strict=True))
    if (
        type(value) is not dict
        or frozenset(value) != IDENTITY_PROJECTION_KEYS
        or value.get("schema") != "stage_f_binding_validator_identity_projection/v3"
    ):
        raise BuildRefusal("identity projection is not the exact closed object")
    return {
        "binding_implementation_identity": _checked_identity(
            value["binding_implementation_identity"],
            "stage_f_binding_implementation/v3",
            "binding implementation identity",
        ),
        "execution_environment_policy_identity": _checked_identity(
            value["execution_environment_policy_identity"],
            "stage_f_execution_environment_policy/v1",
            "execution environment policy identity",
        ),
        "host_validation_runtime_identity": _checked_identity(
            value["host_validation_runtime_identity"],
            "stage_f_host_validation_runtime/v1",
            "host validation runtime identity",
        ),
    }


def _git_sha1(object_type: str, raw: bytes) -> str:
    framed = object_type.encode("ascii") + b" " + str(len(raw)).encode("ascii") + b"\0" + raw
    return hashlib.sha1(framed, usedforsecurity=False).hexdigest()


def _exact_node_stat(path: Path, label: str, *, directory: bool) -> os.stat_result:
    try:
        info = path.stat(follow_symlinks=False)
    except OSError as exc:
        raise BuildRefusal(f"{label} is absent or unreadable") from exc
    expected_type = stat.S_ISDIR if directory else stat.S_ISREG
    if (
        not expected_type(info.st_mode)
        or stat.S_ISLNK(info.st_mode)
        or getattr(info, "st_file_attributes", 0) & 0x400
        or (not directory and info.st_nlink != 1)
        or (directory and os.name == "nt" and info.st_nlink != 1)
    ):
        raise BuildRefusal(f"{label} is not an exact nonreparse, non-hard-linked {'directory' if directory else 'file'}")
    return info


def _exact_directory(path: Path, label: str) -> Path:
    before = _exact_node_stat(path, label, directory=True)
    resolved = path.resolve(strict=True)
    after = _exact_node_stat(resolved, label, directory=True)
    if (before.st_dev, before.st_ino) != (after.st_dev, after.st_ino):
        raise BuildRefusal(f"{label} changed while it was resolved")
    return resolved


def _read_exact_file(path: Path, label: str) -> bytes:
    before = _exact_node_stat(path, label, directory=False)
    raw = path.read_bytes()
    after = _exact_node_stat(path, label, directory=False)
    if (
        (before.st_size, before.st_mtime_ns, before.st_ino)
        != (after.st_size, after.st_mtime_ns, after.st_ino)
        or len(raw) != before.st_size
    ):
        raise BuildRefusal(f"{label} changed while it was read")
    return raw


class _PackIndex:
    def __init__(self, index_path: Path) -> None:
        self.index_path = index_path
        self.pack_path = index_path.with_suffix(".pack")
        name_match = PACK_FILE_RE.fullmatch(index_path.name)
        if name_match is None or name_match.group(2) != "idx":
            raise BuildRefusal("Git pack index filename is malformed")
        raw = _read_exact_file(index_path, "Git pack index")
        pack = _read_exact_file(self.pack_path, "Git pack")
        if len(raw) < 8 + 256 * 4 + 40 or raw[:4] != b"\xfftOc":
            raise BuildRefusal("Git pack index is not version 2")
        version = struct.unpack_from(">I", raw, 4)[0]
        if version != 2:
            raise BuildRefusal("Git pack index version differs")
        fanout = struct.unpack_from(">256I", raw, 8)
        if tuple(fanout) != tuple(sorted(fanout)):
            raise BuildRefusal("Git pack fanout table is not monotone")
        count = fanout[-1]
        names_start = 8 + 256 * 4
        crc_start = names_start + count * 20
        offset_start = crc_start + count * 4
        fixed_end = offset_start + count * 4
        if fixed_end + 40 > len(raw) or (len(raw) - fixed_end - 40) % 8:
            raise BuildRefusal("Git pack index length differs")
        large_count = (len(raw) - fixed_end - 40) // 8
        names = tuple(
            raw[names_start + ordinal * 20 : names_start + (ordinal + 1) * 20].hex()
            for ordinal in range(count)
        )
        if names != tuple(sorted(names)) or len(set(names)) != count:
            raise BuildRefusal("Git pack object names are unordered or repeated")
        calculated_fanout = []
        for first in range(256):
            calculated_fanout.append(sum(bytes.fromhex(name)[0] <= first for name in names))
        if tuple(calculated_fanout) != tuple(fanout):
            raise BuildRefusal("Git pack fanout does not reconstruct from object names")
        if hashlib.sha1(raw[:-20], usedforsecurity=False).digest() != raw[-20:]:
            raise BuildRefusal("Git pack index checksum differs")
        if (
            len(pack) < 32
            or pack[:4] != b"PACK"
            or struct.unpack_from(">I", pack, 4)[0] not in {2, 3}
            or struct.unpack_from(">I", pack, 8)[0] != count
            or hashlib.sha1(pack[:-20], usedforsecurity=False).digest() != pack[-20:]
            or raw[-40:-20] != pack[-20:]
            or name_match.group(1) != pack[-20:].hex()
        ):
            raise BuildRefusal("Git pack filename, header, count, or checksum differs")
        large_offsets = struct.unpack_from(f">{large_count}Q", raw, fixed_end) if large_count else ()
        offsets: list[int] = []
        large_ordinals: list[int] = []
        crcs = struct.unpack_from(f">{count}I", raw, crc_start) if count else ()
        words = struct.unpack_from(f">{count}I", raw, offset_start) if count else ()
        for word in words:
            if word & 0x80000000:
                ordinal = word & 0x7FFFFFFF
                if ordinal >= len(large_offsets):
                    raise BuildRefusal("Git pack large-offset ordinal is out of range")
                large_ordinals.append(ordinal)
                offset = large_offsets[ordinal]
            else:
                offset = word
            if offset < 12 or offset >= len(pack) - 20:
                raise BuildRefusal("Git pack object offset is out of range")
            offsets.append(offset)
        if len(set(offsets)) != len(offsets):
            raise BuildRefusal("Git pack object offsets repeat")
        if large_ordinals != list(range(large_count)):
            raise BuildRefusal("Git pack large-offset table is sparse or reordered")
        self.pack = pack
        self.records = {
            name: (offset, crc) for name, offset, crc in zip(names, offsets, crcs, strict=True)
        }
        self.offset_names = {offset: name for name, offset in zip(names, offsets, strict=True)}
        self._entry_ends = self._validate_pack_partition()
        reverse_path = index_path.with_suffix(".rev")
        if os.path.lexists(reverse_path):
            self._validate_reverse_index(reverse_path, names, offsets, pack[-20:])

    @staticmethod
    def _validate_reverse_index(
        path: Path,
        names: tuple[str, ...],
        offsets: list[int],
        pack_digest: bytes,
    ) -> None:
        raw = _read_exact_file(path, "Git pack reverse index")
        count = len(names)
        if (
            len(raw) != 12 + count * 4 + 40
            or raw[:4] != b"RIDX"
            or struct.unpack_from(">II", raw, 4) != (1, 1)
            or raw[-40:-20] != pack_digest
            or hashlib.sha1(raw[:-20], usedforsecurity=False).digest() != raw[-20:]
        ):
            raise BuildRefusal("Git pack reverse index framing or checksum differs")
        positions = struct.unpack_from(f">{count}I", raw, 12) if count else ()
        if tuple(sorted(positions)) != tuple(range(count)):
            raise BuildRefusal("Git pack reverse index is not a permutation")
        expected = tuple(
            ordinal
            for ordinal, _offset in sorted(enumerate(offsets), key=lambda row: row[1])
        )
        if positions != expected:
            raise BuildRefusal("Git pack reverse index does not reconstruct pack order")

    def _entry_envelope(
        self, start: int, end: int
    ) -> tuple[int, int, str | None, int]:
        offset = start
        if offset >= end:
            raise BuildRefusal("Git pack object entry is empty")
        first = self.pack[offset]
        offset += 1
        object_type = (first >> 4) & 7
        declared_size = first & 0x0F
        shift = 4
        current = first
        while current & 0x80:
            if offset >= end or shift > 63:
                raise BuildRefusal("Git pack object header is truncated or overwide")
            current = self.pack[offset]
            offset += 1
            declared_size |= (current & 0x7F) << shift
            shift += 7
        base_oid: str | None = None
        if object_type == 6:
            if offset >= end:
                raise BuildRefusal("Git OFS delta base is truncated")
            byte = self.pack[offset]
            offset += 1
            distance = byte & 0x7F
            while byte & 0x80:
                if offset >= end:
                    raise BuildRefusal("Git OFS delta base is truncated")
                byte = self.pack[offset]
                offset += 1
                distance = ((distance + 1) << 7) | (byte & 0x7F)
            base_offset = start - distance
            base_oid = self.offset_names.get(base_offset)
            if distance == 0 or base_offset >= start or base_oid is None:
                raise BuildRefusal("Git OFS delta base offset is absent or not earlier")
        elif object_type == 7:
            if offset + 20 > end:
                raise BuildRefusal("Git REF delta base is truncated")
            base_oid = self.pack[offset : offset + 20].hex()
            offset += 20
            if base_oid not in self.records:
                raise BuildRefusal("stored Git REF delta has an external base")
        elif object_type not in {1, 2, 3, 4}:
            raise BuildRefusal("Git pack object type is forbidden")
        return object_type, declared_size, base_oid, offset

    def _inflate_entry(self, start: int, end: int) -> tuple[int, str | None, bytes]:
        object_type, declared_size, base_oid, compressed_offset = self._entry_envelope(
            start, end
        )
        inflater = zlib.decompressobj()
        try:
            inflated = inflater.decompress(self.pack[compressed_offset:end])
            inflated += inflater.flush()
        except zlib.error as exc:
            raise BuildRefusal("Git pack object zlib stream differs") from exc
        if (
            not inflater.eof
            or inflater.unused_data
            or inflater.unconsumed_tail
            or len(inflated) != declared_size
        ):
            raise BuildRefusal("Git pack object zlib boundary or size differs")
        return object_type, base_oid, inflated

    def _validate_pack_partition(self) -> dict[int, int]:
        physical_offsets = sorted(self.offset_names)
        if physical_offsets and physical_offsets[0] != 12:
            raise BuildRefusal("Git pack has bytes before its first indexed object")
        if not physical_offsets and len(self.pack) != 32:
            raise BuildRefusal("empty Git pack has unindexed bytes")
        ends = physical_offsets[1:] + [len(self.pack) - 20]
        result: dict[int, int] = {}
        for start, end in zip(physical_offsets, ends, strict=True):
            if start >= end:
                raise BuildRefusal("Git pack object ranges overlap or are empty")
            self._inflate_entry(start, end)
            object_id = self.offset_names[start]
            expected_crc = self.records[object_id][1]
            if (zlib.crc32(self.pack[start:end]) & 0xFFFFFFFF) != expected_crc:
                raise BuildRefusal("Git pack object CRC differs")
            result[start] = end
        return result

    @staticmethod
    def _delta_varint(raw: bytes, offset: int) -> tuple[int, int]:
        value = 0
        shift = 0
        while True:
            if offset >= len(raw) or shift > 63:
                raise BuildRefusal("Git delta varint is truncated or overwide")
            byte = raw[offset]
            offset += 1
            value |= (byte & 0x7F) << shift
            if not byte & 0x80:
                return value, offset
            shift += 7

    @classmethod
    def _apply_delta(cls, base: bytes, delta: bytes) -> bytes:
        base_size, offset = cls._delta_varint(delta, 0)
        result_size, offset = cls._delta_varint(delta, offset)
        if base_size != len(base):
            raise BuildRefusal("Git delta base size differs")
        result = bytearray()
        while offset < len(delta):
            command = delta[offset]
            offset += 1
            if command & 0x80:
                copy_offset = 0
                copy_size = 0
                for bit, shift in ((0x01, 0), (0x02, 8), (0x04, 16), (0x08, 24)):
                    if command & bit:
                        if offset >= len(delta):
                            raise BuildRefusal("Git delta copy offset is truncated")
                        copy_offset |= delta[offset] << shift
                        offset += 1
                for bit, shift in ((0x10, 0), (0x20, 8), (0x40, 16)):
                    if command & bit:
                        if offset >= len(delta):
                            raise BuildRefusal("Git delta copy size is truncated")
                        copy_size |= delta[offset] << shift
                        offset += 1
                if copy_size == 0:
                    copy_size = 0x10000
                end = copy_offset + copy_size
                if end > len(base):
                    raise BuildRefusal("Git delta copy exceeds its base")
                result.extend(base[copy_offset:end])
            elif command:
                end = offset + command
                if end > len(delta):
                    raise BuildRefusal("Git delta literal is truncated")
                result.extend(delta[offset:end])
                offset = end
            else:
                raise BuildRefusal("Git delta command zero is forbidden")
            if len(result) > result_size:
                raise BuildRefusal("Git delta output exceeds its declared size")
        if len(result) != result_size:
            raise BuildRefusal("Git delta output size differs")
        return bytes(result)

    def read(self, oid: str, store: "_GitObjectStore", visiting: frozenset[str]) -> tuple[str, bytes]:
        offset, expected_crc = self.records[oid]
        start = offset
        end = self._entry_ends[start]
        object_type, base_oid, inflated = self._inflate_entry(start, end)
        if (zlib.crc32(self.pack[start:end]) & 0xFFFFFFFF) != expected_crc:
            raise BuildRefusal("Git pack object CRC differs")
        if base_oid is None:
            type_name = {1: "commit", 2: "tree", 3: "blob", 4: "tag"}[object_type]
            raw = inflated
        else:
            type_name, base = store._read_object(base_oid, visiting)
            raw = self._apply_delta(base, inflated)
        return type_name, raw


def _validate_multi_pack_index(
    path: Path, packs_by_name: dict[str, _PackIndex]
) -> None:
    """Validate a nonincremental SHA-1 MIDX against every parsed pack index."""

    raw = _read_exact_file(path, "Git multi-pack index")
    if len(raw) < 12 + 5 * 12 + 20:
        raise BuildRefusal("Git multi-pack index is truncated")
    signature, version, oid_version, chunk_count, base_count, pack_count = (
        struct.unpack_from(">4sBBBBI", raw, 0)
    )
    if (
        signature != b"MIDX"
        or version != 1
        or oid_version != 1
        or base_count != 0
        or chunk_count not in {4, 5}
        or pack_count != len(packs_by_name)
        or hashlib.sha1(raw[:-20], usedforsecurity=False).digest() != raw[-20:]
    ):
        raise BuildRefusal("Git multi-pack index header or checksum differs")
    table_end = 12 + (chunk_count + 1) * 12
    chunks: list[tuple[bytes, int]] = []
    for ordinal in range(chunk_count + 1):
        chunk_id = raw[12 + ordinal * 12 : 16 + ordinal * 12]
        offset = struct.unpack_from(">Q", raw, 16 + ordinal * 12)[0]
        chunks.append((chunk_id, offset))
    expected_ids = [b"PNAM", b"OIDF", b"OIDL", b"OOFF"]
    if chunk_count == 5:
        expected_ids.append(b"LOFF")
    if (
        [chunk_id for chunk_id, _offset in chunks[:-1]] != expected_ids
        or chunks[-1][0] != bytes(4)
        or chunks[0][1] != table_end
        or chunks[-1][1] != len(raw) - 20
        or any(
            left[1] >= right[1]
            for left, right in zip(chunks[:-1], chunks[1:], strict=True)
        )
    ):
        raise BuildRefusal("Git multi-pack index chunk table differs")
    bodies = {
        chunk_id: raw[start:end]
        for (chunk_id, start), (_next_id, end) in zip(
            chunks[:-1], chunks[1:], strict=True
        )
    }
    expected_pack_names = tuple(sorted(packs_by_name))
    encoded_names = tuple(name.encode("ascii", "strict") for name in expected_pack_names)
    name_payload = b"".join(name + b"\0" for name in encoded_names)
    name_padding = bytes((-len(name_payload)) % 4)
    if bodies[b"PNAM"] != name_payload + name_padding:
        raise BuildRefusal("Git multi-pack index pack-name chunk differs")
    fanout_raw = bodies[b"OIDF"]
    if len(fanout_raw) != 256 * 4:
        raise BuildRefusal("Git multi-pack index fanout length differs")
    fanout = struct.unpack(">256I", fanout_raw)
    if tuple(fanout) != tuple(sorted(fanout)):
        raise BuildRefusal("Git multi-pack index fanout is not monotone")
    object_count = fanout[-1]
    oid_raw = bodies[b"OIDL"]
    offset_raw = bodies[b"OOFF"]
    if len(oid_raw) != object_count * 20 or len(offset_raw) != object_count * 8:
        raise BuildRefusal("Git multi-pack index object chunk length differs")
    object_ids = tuple(
        oid_raw[ordinal * 20 : (ordinal + 1) * 20].hex()
        for ordinal in range(object_count)
    )
    if object_ids != tuple(sorted(object_ids)) or len(set(object_ids)) != object_count:
        raise BuildRefusal("Git multi-pack index object names are unordered or repeated")
    expected_fanout = tuple(
        sum(bytes.fromhex(object_id)[0] <= first for object_id in object_ids)
        for first in range(256)
    )
    if fanout != expected_fanout:
        raise BuildRefusal("Git multi-pack index fanout does not reconstruct")
    large_raw = bodies.get(b"LOFF", b"")
    if len(large_raw) % 8:
        raise BuildRefusal("Git multi-pack index large-offset chunk is misaligned")
    large_offsets = (
        struct.unpack(f">{len(large_raw) // 8}Q", large_raw) if large_raw else ()
    )
    large_ordinals: list[int] = []
    observed: dict[str, tuple[str, int]] = {}
    for ordinal, object_id in enumerate(object_ids):
        pack_ordinal, offset_word = struct.unpack_from(">II", offset_raw, ordinal * 8)
        if pack_ordinal >= len(expected_pack_names):
            raise BuildRefusal("Git multi-pack index pack ordinal is out of range")
        if offset_word & 0x80000000:
            large_ordinal = offset_word & 0x7FFFFFFF
            if large_ordinal >= len(large_offsets):
                raise BuildRefusal("Git multi-pack index large-offset ordinal is out of range")
            large_ordinals.append(large_ordinal)
            offset = large_offsets[large_ordinal]
        else:
            offset = offset_word
        pack_name = expected_pack_names[pack_ordinal]
        pack = packs_by_name[pack_name]
        packed = pack.records.get(object_id)
        if packed is None or packed[0] != offset:
            raise BuildRefusal("Git multi-pack index object/pack/offset projection differs")
        observed[object_id] = (pack_name, offset)
    if large_ordinals != list(range(len(large_offsets))):
        raise BuildRefusal("Git multi-pack index large-offset table is sparse or reordered")
    expected_objects = {
        object_id: (pack_name, row[0])
        for pack_name, pack in packs_by_name.items()
        for object_id, row in pack.records.items()
    }
    if observed != expected_objects:
        raise BuildRefusal("Git multi-pack index does not exactly cover the parsed packs")


class _GitObjectStore:
    def __init__(self, source: Path) -> None:
        self.source = _exact_directory(source, "source worktree")
        marker = self.source / ".git"
        try:
            marker_info = marker.stat(follow_symlinks=False)
        except OSError as exc:
            raise BuildRefusal("source has no exact Git administrative marker") from exc
        linked_worktree = stat.S_ISREG(marker_info.st_mode)
        if stat.S_ISDIR(marker_info.st_mode):
            self.admin = _exact_directory(marker, "Git administrative directory")
        elif linked_worktree:
            text = _read_exact_file(marker, "Git administrative pointer").decode("utf-8", "strict")
            lines = text.splitlines()
            if len(lines) != 1 or not lines[0].startswith("gitdir: "):
                raise BuildRefusal("Git administrative pointer is malformed")
            candidate = Path(lines[0][8:])
            if not candidate.is_absolute():
                candidate = self.source / candidate
            self.admin = _exact_directory(candidate, "linked-worktree Git administrative directory")
        else:
            raise BuildRefusal("Git administrative marker is not a directory or regular pointer")
        commondir = self.admin / "commondir"
        if linked_worktree:
            text = _read_exact_file(commondir, "Git common-directory pointer").decode("utf-8", "strict")
            lines = text.splitlines()
            if len(lines) != 1:
                raise BuildRefusal("Git common-directory pointer is malformed")
            candidate = Path(lines[0])
            if not candidate.is_absolute():
                candidate = self.admin / candidate
            self.common = _exact_directory(candidate, "Git common directory")
            worktrees = _exact_directory(self.common / "worktrees", "Git worktrees directory")
            if (
                self.admin.parent != worktrees
                or self.admin.name in {"", ".", ".."}
                or unicodedata.normalize("NFC", self.admin.name) != self.admin.name
            ):
                raise BuildRefusal("linked-worktree Git administrative directory escapes common/worktrees")
            backlink_text = _read_exact_file(
                self.admin / "gitdir", "linked-worktree Git administrative backlink"
            ).decode("utf-8", "strict")
            backlink_lines = backlink_text.splitlines()
            if len(backlink_lines) != 1:
                raise BuildRefusal("linked-worktree Git administrative backlink is malformed")
            backlink = Path(backlink_lines[0])
            if not backlink.is_absolute():
                backlink = self.admin / backlink
            if backlink.resolve(strict=True) != marker.resolve(strict=True):
                raise BuildRefusal("linked-worktree Git administrative backlink differs")
        else:
            self.common = self.admin
            if os.path.lexists(commondir):
                raise BuildRefusal("ordinary Git administrative directory has a common-directory pointer")
        self.objects = _exact_directory(self.common / "objects", "Git object directory")
        forbidden = (
            self.common / "shallow",
            self.common / "info" / "grafts",
            self.objects / "info" / "alternates",
            self.objects / "info" / "http-alternates",
            self.common / "refs" / "replace",
        )
        if any(os.path.lexists(path) for path in forbidden):
            raise BuildRefusal("shallow, alternate, graft, or replacement Git state is forbidden")
        config = _read_exact_file(self.common / "config", "Git repository config").lower()
        if any(marker in config for marker in (b"partialclone", b"promisor", b"objectformat", b"refstorage")):
            raise BuildRefusal("partial, promisor, alternate-format, or reftable Git state is forbidden")
        self._cache: dict[str, tuple[str, bytes]] = {}
        self._packs: list[_PackIndex] = []
        self._packed: dict[str, _PackIndex] = {}
        pack_directory = self.objects / "pack"
        if os.path.lexists(pack_directory):
            pack_directory = _exact_directory(pack_directory, "Git pack directory")
            entries = tuple(sorted(pack_directory.iterdir(), key=lambda path: path.name))
            names = tuple(path.name for path in entries)
            for path in entries:
                _exact_node_stat(path, f"Git pack-directory entry {path.name}", directory=False)
                if PACK_FILE_RE.fullmatch(path.name) is None and path.name != "multi-pack-index":
                    raise BuildRefusal(f"unsupported Git pack-directory entry is forbidden: {path.name}")
            stems_by_suffix = {
                suffix: {
                    match.group(1)
                    for name in names
                    if (match := PACK_FILE_RE.fullmatch(name)) is not None
                    and match.group(2) == suffix
                }
                for suffix in ("idx", "pack", "rev")
            }
            if (
                stems_by_suffix["idx"] != stems_by_suffix["pack"]
                or not stems_by_suffix["rev"].issubset(stems_by_suffix["idx"])
            ):
                raise BuildRefusal("Git pack directory has an unpaired index, pack, or reverse index")
            for index_path in (pack_directory / f"pack-{stem}.idx" for stem in sorted(stems_by_suffix["idx"])):
                pack_index = _PackIndex(index_path)
                for oid in pack_index.records:
                    if oid in self._packed:
                        raise BuildRefusal("Git packed object is duplicated across packs")
                    self._packed[oid] = pack_index
                self._packs.append(pack_index)
            multi_pack_index = pack_directory / "multi-pack-index"
            if os.path.lexists(multi_pack_index):
                _validate_multi_pack_index(
                    multi_pack_index,
                    {pack.index_path.name: pack for pack in self._packs},
                )
            if tuple(sorted(path.name for path in pack_directory.iterdir())) != names:
                raise BuildRefusal("Git pack directory changed during acquisition")
        self._head_at_open = self.head_commit()

    @classmethod
    def open_worktree(cls, source: Path) -> "_GitObjectStore":
        return cls(source)

    @staticmethod
    def _parse_object(raw: bytes, oid: str) -> tuple[str, bytes]:
        nul = raw.find(b"\0")
        if nul <= 0 or b" " not in raw[:nul]:
            raise BuildRefusal("loose Git object header is malformed")
        type_raw, size_raw = raw[:nul].split(b" ", 1)
        try:
            type_name = type_raw.decode("ascii", "strict")
            size = int(size_raw.decode("ascii", "strict"))
        except (UnicodeError, ValueError) as exc:
            raise BuildRefusal("loose Git object header differs") from exc
        body = raw[nul + 1 :]
        if type_name not in {"commit", "tree", "blob", "tag"} or size != len(body):
            raise BuildRefusal("loose Git object type or size differs")
        if _git_sha1(type_name, body) != oid:
            raise BuildRefusal("loose Git object content address differs")
        return type_name, body

    def _read_object(self, oid: str, visiting: frozenset[str]) -> tuple[str, bytes]:
        if GIT_OBJECT_RE.fullmatch(oid) is None:
            raise BuildRefusal("Git object identity is malformed")
        cached = self._cache.get(oid)
        if cached is not None:
            return cached
        if oid in visiting or len(visiting) >= 128:
            raise BuildRefusal("Git delta graph is cyclic or too deep")
        loose_directory = self.objects / oid[:2]
        if os.path.lexists(loose_directory):
            loose_directory = _exact_directory(
                loose_directory, "loose Git object fanout directory"
            )
        loose = loose_directory / oid[2:]
        if os.path.lexists(loose):
            compressed = _read_exact_file(loose, "loose Git object")
            inflater = zlib.decompressobj()
            try:
                framed = inflater.decompress(compressed) + inflater.flush()
            except zlib.error as exc:
                raise BuildRefusal("loose Git object zlib stream differs") from exc
            if not inflater.eof or inflater.unused_data or inflater.unconsumed_tail:
                raise BuildRefusal("loose Git object zlib framing differs")
            result = self._parse_object(framed, oid)
        else:
            pack = self._packed.get(oid)
            if pack is None:
                raise BuildRefusal(f"required Git object is absent: {oid}")
            result = pack.read(oid, self, visiting | {oid})
            if _git_sha1(result[0], result[1]) != oid:
                raise BuildRefusal("packed Git object content address differs")
        self._cache[oid] = result
        return result

    def read_object(self, oid: str) -> tuple[str, bytes]:
        return self._read_object(oid, frozenset())

    def _resolve_ref(self, name: str) -> str:
        if (
            not name.startswith("refs/")
            or ".." in name
            or "\\" in name
            or "//" in name
            or not all(component and component not in {".", ".."} for component in name.split("/"))
        ):
            raise BuildRefusal("Git symbolic ref is malformed")
        candidates = (self.admin / name, self.common / name)
        for path in candidates:
            if path.is_file():
                text = _read_exact_file(path, "Git loose ref").decode("ascii", "strict").strip()
                if GIT_OBJECT_RE.fullmatch(text) is None:
                    raise BuildRefusal("Git loose ref target is malformed")
                return text
        packed = self.common / "packed-refs"
        if packed.is_file():
            found: str | None = None
            for line in _read_exact_file(packed, "Git packed refs").decode("utf-8", "strict").splitlines():
                if not line or line.startswith(("#", "^")):
                    continue
                try:
                    oid, ref = line.split(" ", 1)
                except ValueError as exc:
                    raise BuildRefusal("Git packed ref row is malformed") from exc
                if ref == name:
                    if found is not None or GIT_OBJECT_RE.fullmatch(oid) is None:
                        raise BuildRefusal("Git packed ref target is repeated or malformed")
                    found = oid
            if found is not None:
                return found
        raise BuildRefusal("Git symbolic ref target is absent")

    def head_commit(self) -> str:
        text = _read_exact_file(self.admin / "HEAD", "Git HEAD").decode("ascii", "strict").strip()
        oid = self._resolve_ref(text[5:]) if text.startswith("ref: ") else text
        if GIT_OBJECT_RE.fullmatch(oid) is None or self.read_object(oid)[0] != "commit":
            raise BuildRefusal("Git HEAD is not an exact commit")
        return oid

    def commit(self, oid: str) -> tuple[str, tuple[str, ...]]:
        object_type, raw = self.read_object(oid)
        if object_type != "commit" or b"\n\n" not in raw:
            raise BuildRefusal("Git commit object is malformed")
        headers = raw.split(b"\n\n", 1)[0].split(b"\n")
        if (
            not headers
            or len(headers[0]) != 45
            or not headers[0].startswith(b"tree ")
        ):
            raise BuildRefusal("Git commit lacks its initial tree")
        try:
            tree = headers[0][5:].decode("ascii", "strict")
            parent_rows: list[str] = []
            ordinal = 1
            while ordinal < len(headers) and headers[ordinal].startswith(b"parent "):
                header = headers[ordinal]
                if len(header) != 47:
                    raise BuildRefusal("Git commit parent header is malformed")
                parent_rows.append(header[7:].decode("ascii", "strict"))
                ordinal += 1
            if any(
                header.startswith((b"tree ", b"parent "))
                for header in headers[ordinal:]
            ):
                raise BuildRefusal("Git commit has a late or repeated coordinate header")
            parents = tuple(parent_rows)
        except UnicodeError as exc:
            raise BuildRefusal("Git commit coordinate header is non-ASCII") from exc
        if (
            GIT_OBJECT_RE.fullmatch(tree) is None
            or len(parents) != len(set(parents))
            or any(GIT_OBJECT_RE.fullmatch(parent) is None for parent in parents)
        ):
            raise BuildRefusal("Git commit tree or parent identity is malformed")
        return tree, parents

    def tree(self, oid: str) -> tuple[tuple[str, str, str], ...]:
        object_type, raw = self.read_object(oid)
        if object_type != "tree":
            raise BuildRefusal("Git tree object has another type")
        result: list[tuple[str, str, str]] = []
        offset = 0
        while offset < len(raw):
            space = raw.find(b" ", offset)
            nul = raw.find(b"\0", space + 1) if space >= 0 else -1
            if space <= offset or nul <= space + 1 or nul + 21 > len(raw):
                raise BuildRefusal("Git tree entry is truncated")
            mode_raw = raw[offset:space]
            name_raw = raw[space + 1 : nul]
            child = raw[nul + 1 : nul + 21].hex()
            offset = nul + 21
            if mode_raw == b"40000":
                mode = "40000"
            elif mode_raw in {b"100644", b"100755"}:
                mode = mode_raw.decode("ascii")
            else:
                raise BuildRefusal("Git tree mode is forbidden")
            try:
                name = name_raw.decode("utf-8", "strict")
            except UnicodeError as exc:
                raise BuildRefusal("Git tree name is not UTF-8") from exc
            if not name or name in {".", ".."} or "/" in name or unicodedata.normalize("NFC", name) != name:
                raise BuildRefusal("Git tree name is not an exact NFC component")
            result.append((mode, name, child))
        keys = [name.encode("utf-8") + (b"/" if mode == "40000" else b"") for mode, name, _ in result]
        if keys != sorted(keys) or len({name for _mode, name, _child in result}) != len(result):
            raise BuildRefusal("Git tree order or uniqueness differs")
        return tuple(result)

    def tree_map(self, commit: str) -> dict[str, tuple[str, str, bytes]]:
        result: dict[str, tuple[str, str, bytes]] = {}

        def visit(tree_oid: str, prefix: str, stack: frozenset[str]) -> None:
            if tree_oid in stack:
                raise BuildRefusal("Git tree graph is cyclic")
            for mode, name, child in self.tree(tree_oid):
                path = f"{prefix}/{name}" if prefix else name
                if mode == "40000":
                    visit(child, path, stack | {tree_oid})
                else:
                    object_type, raw = self.read_object(child)
                    if object_type != "blob" or path in result:
                        raise BuildRefusal("Git recursive tree path is repeated or non-blob")
                    result[path] = (mode, child, raw)

        visit(self.commit(commit)[0], "", frozenset())
        return dict(sorted(result.items(), key=lambda row: row[0].encode("utf-8")))

    def ancestry_witness(self, descendant: str, ancestor: str) -> tuple[str, ...]:
        pending: list[tuple[str, tuple[str, ...]]] = [(descendant, (descendant,))]
        visited: set[str] = set()
        while pending:
            candidate, path = pending.pop()
            if candidate == ancestor:
                return path
            if candidate in visited:
                continue
            visited.add(candidate)
            for parent in reversed(self.commit(candidate)[1]):
                pending.append((parent, (*path, parent)))
        raise BuildRefusal("required immutable Git ancestry witness is absent")

    def is_ancestor(self, descendant: str, ancestor: str) -> bool:
        """Return ancestry only after parsing every visited raw commit object."""

        pending = [descendant]
        visited: set[str] = set()
        while pending:
            candidate = pending.pop()
            if candidate == ancestor:
                return True
            if candidate in visited:
                continue
            visited.add(candidate)
            pending.extend(reversed(self.commit(candidate)[1]))
        return False

    def complete_tree_object_ids(self, commit: str) -> set[str]:
        result: set[str] = set()

        def visit(tree_oid: str) -> None:
            if tree_oid in result:
                return
            result.add(tree_oid)
            for mode, _name, child in self.tree(tree_oid):
                result.add(child)
                if mode == "40000":
                    visit(child)

        visit(self.commit(commit)[0])
        return result

    def _index_rows(self) -> dict[str, tuple[str, str]]:
        raw = _read_exact_file(self.admin / "index", "Git index")
        if len(raw) < 32 or raw[:4] != b"DIRC" or struct.unpack_from(">I", raw, 4)[0] != 2:
            raise BuildRefusal("Git index is not exact version 2")
        if hashlib.sha1(raw[:-20], usedforsecurity=False).digest() != raw[-20:]:
            raise BuildRefusal("Git index checksum differs")
        count = struct.unpack_from(">I", raw, 8)[0]
        offset = 12
        result: dict[str, tuple[str, str]] = {}
        for _ordinal in range(count):
            start = offset
            if offset + 62 > len(raw) - 20:
                raise BuildRefusal("Git index entry is truncated")
            fields = struct.unpack_from(">10I20sH", raw, offset)
            mode = fields[6]
            oid = fields[10].hex()
            flags = fields[11]
            offset += 62
            nul = raw.find(b"\0", offset, len(raw) - 20)
            if nul < 0:
                raise BuildRefusal("Git index path is unterminated")
            name_raw = raw[offset:nul]
            name_length = flags & 0x0FFF
            if (name_length != 0x0FFF and name_length != len(name_raw)) or flags & 0xF000:
                raise BuildRefusal("Git index flags or path length differ")
            try:
                name = name_raw.decode("utf-8", "strict")
            except UnicodeError as exc:
                raise BuildRefusal("Git index path is not UTF-8") from exc
            if not name or unicodedata.normalize("NFC", name) != name or name in result:
                raise BuildRefusal("Git index path is malformed or repeated")
            mode_text = format(mode, "o")
            if mode_text not in {"100644", "100755"}:
                raise BuildRefusal("Git index mode is forbidden")
            result[name] = (mode_text, oid)
            offset = start + ((nul + 1 - start + 7) // 8) * 8
        while offset < len(raw) - 20:
            if offset + 8 > len(raw) - 20:
                raise BuildRefusal("Git index extension is truncated")
            signature = raw[offset : offset + 4]
            size = struct.unpack_from(">I", raw, offset + 4)[0]
            offset += 8
            if offset + size > len(raw) - 20 or signature != b"TREE":
                raise BuildRefusal("Git index extension is unknown or truncated")
            offset += size
        if offset != len(raw) - 20:
            raise BuildRefusal("Git index has trailing bytes")
        return result

    @staticmethod
    def _checkout_bytes_match(blob: bytes, checkout: bytes) -> bool:
        if checkout == blob:
            return True
        return b"\0" not in blob and b"\r" not in blob and checkout == blob.replace(b"\n", b"\r\n")

    def assert_clean_checkout(self, commit: str) -> None:
        if self.head_commit() != commit:
            raise BuildRefusal("Git HEAD changed or differs from the requested commit")
        tree = self.tree_map(commit)
        expected_index = {path: row[:2] for path, row in tree.items()}
        if self._index_rows() != expected_index:
            raise BuildRefusal("Git index differs from the exact HEAD tree")
        expected_files = set(tree)
        expected_directories = {
            "/".join(path.split("/")[:ordinal])
            for path in expected_files
            for ordinal in range(1, len(path.split("/")))
        }
        observed_files: set[str] = set()
        observed_directories: set[str] = set()
        for directory, directory_names, file_names in os.walk(self.source, topdown=True, followlinks=False):
            parent = Path(directory)
            if parent == self.source:
                directory_names[:] = [name for name in directory_names if name != ".git"]
                file_names = [name for name in file_names if name != ".git"]
            directory_names.sort(key=lambda name: unicodedata.normalize("NFC", name).encode("utf-8"))
            file_names.sort(key=lambda name: unicodedata.normalize("NFC", name).encode("utf-8"))
            for name in directory_names:
                path = parent / name
                relative = path.relative_to(self.source).as_posix()
                info = path.stat(follow_symlinks=False)
                if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
                    raise BuildRefusal("Git checkout directory is reparse")
                observed_directories.add(relative)
            for name in file_names:
                path = parent / name
                relative = path.relative_to(self.source).as_posix()
                observed_files.add(relative)
                if relative not in tree:
                    continue
                mode, _oid, blob = tree[relative]
                checkout = _read_exact_file(path, f"Git checkout file {relative}")
                if not self._checkout_bytes_match(blob, checkout):
                    raise BuildRefusal(f"Git checkout bytes differ: {relative}")
                if os.name != "nt" and bool(path.stat().st_mode & 0o111) != (mode == "100755"):
                    raise BuildRefusal(f"Git checkout executable mode differs: {relative}")
        if observed_files != expected_files or observed_directories != expected_directories:
            raise BuildRefusal("Git checkout has a missing, extra, or ignored filesystem entry")
        if self.head_commit() != commit or self._index_rows() != expected_index:
            raise BuildRefusal("Git checkout coordinate or index changed during validation")


def _coordinate(store: _GitObjectStore) -> tuple[str, str]:
    commit = store.head_commit()
    return commit, store.commit(commit)[0]


def _file_row(
    store: _GitObjectStore, commit: str, relative: str
) -> tuple[dict[str, object], bytes]:
    entry = store.tree_map(commit).get(relative)
    if entry is None or entry[0] != "100644":
        raise BuildRefusal(f"Git path is not the required 100644 blob: {relative}")
    mode, git_object, raw = entry
    return (
        {
            "path": relative,
            "mode": mode,
            "git_object": git_object,
            "byte_count": len(raw),
            "raw_sha256": _sha256(raw),
        },
        raw,
    )


def _assert_corrected_repository(
    store: _GitObjectStore, implementation_commit: str
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """Bind the accepted v3 authority and the exact 2M+12A implementation."""

    exact_coordinates = (
        (DESCENDANT_PATH_BASE_COMMIT, DESCENDANT_PATH_BASE_TREE),
        (ACCEPTED_BASE_COMMIT, ACCEPTED_BASE_TREE),
        (ORIGINAL_AUTHORITY_CANDIDATE_COMMIT, ORIGINAL_AUTHORITY_CANDIDATE_TREE),
        (ORIGINAL_AUTHORITY_INTEGRATION_COMMIT, ORIGINAL_AUTHORITY_INTEGRATION_TREE),
        (CORRECTION_REQUIRED_TARGET_COMMIT, CORRECTION_REQUIRED_TARGET_TREE),
        (CORRECTION_AUTHORITY_CANDIDATE_COMMIT, CORRECTION_AUTHORITY_INTEGRATION_TREE),
        (CORRECTION_AUTHORITY_INTEGRATION_COMMIT, CORRECTION_AUTHORITY_INTEGRATION_TREE),
        (REACHABILITY_CANDIDATE_COMMIT, REACHABILITY_INTEGRATION_TREE),
        (REACHABILITY_INTEGRATION_COMMIT, REACHABILITY_INTEGRATION_TREE),
        (FINAL_AUTHORITY_CANDIDATE_COMMIT, FINAL_AUTHORITY_CANDIDATE_TREE),
        (FINAL_AUTHORITY_INTEGRATION_COMMIT, FINAL_AUTHORITY_INTEGRATION_TREE),
        (FINAL_REACHABILITY_CANDIDATE_COMMIT, FINAL_REACHABILITY_CANDIDATE_TREE),
        (FINAL_REACHABILITY_INTEGRATION_COMMIT, FINAL_REACHABILITY_INTEGRATION_TREE),
    )
    for coordinate, expected_tree in exact_coordinates:
        if store.commit(coordinate)[0] != expected_tree:
            raise BuildRefusal(f"immutable Git tree differs: {coordinate}")
    if store.commit(ORIGINAL_AUTHORITY_INTEGRATION_COMMIT)[1] != (
        ACCEPTED_BASE_COMMIT,
        ORIGINAL_AUTHORITY_CANDIDATE_COMMIT,
    ):
        raise BuildRefusal("original-authority integration parentage differs")
    if store.commit(CORRECTION_AUTHORITY_INTEGRATION_COMMIT)[1] != (
        CORRECTION_REQUIRED_TARGET_COMMIT,
        CORRECTION_AUTHORITY_CANDIDATE_COMMIT,
    ):
        raise BuildRefusal("correction-authority integration parentage differs")
    if store.commit(REACHABILITY_CANDIDATE_COMMIT)[1] != (
        CORRECTION_AUTHORITY_INTEGRATION_COMMIT,
    ):
        raise BuildRefusal("reachability candidate parentage differs")
    if store.commit(REACHABILITY_INTEGRATION_COMMIT)[1] != (
        CORRECTION_AUTHORITY_INTEGRATION_COMMIT,
        REACHABILITY_CANDIDATE_COMMIT,
    ):
        raise BuildRefusal("reachability integration parentage differs")
    if store.commit(FINAL_AUTHORITY_CANDIDATE_COMMIT)[1] != (
        FINAL_AUTHORITY_REQUIRED_TARGET_COMMIT,
    ):
        raise BuildRefusal("final-authority candidate parentage differs")
    if store.commit(FINAL_AUTHORITY_INTEGRATION_COMMIT)[1] != (
        FINAL_AUTHORITY_REQUIRED_TARGET_COMMIT,
        FINAL_AUTHORITY_CANDIDATE_COMMIT,
    ):
        raise BuildRefusal("final-authority integration parentage differs")
    if store.commit(FINAL_REACHABILITY_CANDIDATE_COMMIT)[1] != (
        FINAL_AUTHORITY_INTEGRATION_COMMIT,
    ):
        raise BuildRefusal("final reachability candidate parentage differs")
    if store.commit(FINAL_REACHABILITY_INTEGRATION_COMMIT)[1] != (
        FINAL_AUTHORITY_INTEGRATION_COMMIT,
        FINAL_REACHABILITY_CANDIDATE_COMMIT,
    ):
        raise BuildRefusal("final reachability integration parentage differs")
    if not store.is_ancestor(
        implementation_commit, FINAL_REACHABILITY_INTEGRATION_COMMIT
    ):
        raise BuildRefusal("implementation does not descend from final accepted reachability")
    if (
        not store.is_ancestor(ORIGINAL_AUTHORITY_CANDIDATE_COMMIT, ACCEPTED_BASE_COMMIT)
        or not store.is_ancestor(
            CORRECTION_REQUIRED_TARGET_COMMIT, ORIGINAL_AUTHORITY_INTEGRATION_COMMIT
        )
        or not store.is_ancestor(
            CORRECTION_AUTHORITY_CANDIDATE_COMMIT, CORRECTION_REQUIRED_TARGET_COMMIT
        )
    ):
        raise BuildRefusal("predecessor authority ancestry differs")
    if any(
        store.is_ancestor(implementation_commit, rejected)
        for rejected in REJECTED_FOUNDATION_COMMITS
    ):
        raise BuildRefusal("implementation contains a rejected foundation ancestor")

    authority_rows: list[dict[str, object]] = []
    for ordinal, path in enumerate(AUTHORITY_PATHS):
        integrated_row, integrated_raw = _file_row(
            store, FINAL_AUTHORITY_INTEGRATION_COMMIT, path
        )
        candidate_commit = (
            ORIGINAL_AUTHORITY_CANDIDATE_COMMIT
            if ordinal < len(ORIGINAL_AUTHORITY_PATHS)
            else CORRECTION_AUTHORITY_CANDIDATE_COMMIT
            if ordinal < len(ORIGINAL_AUTHORITY_PATHS) + len(CORRECTION_AUTHORITY_PATHS)
            else FINAL_AUTHORITY_CANDIDATE_COMMIT
        )
        candidate_row, candidate_raw = _file_row(store, candidate_commit, path)
        implementation_row, implementation_raw = _file_row(
            store, implementation_commit, path
        )
        if (
            candidate_row != integrated_row
            or candidate_raw != integrated_raw
            or implementation_row != integrated_row
            or implementation_raw != integrated_raw
        ):
            raise BuildRefusal(f"implementation changed an integrated authority row: {path}")
        authority_rows.append(integrated_row)

    base_tree = store.tree_map(FINAL_REACHABILITY_INTEGRATION_COMMIT)
    implementation_tree = store.tree_map(implementation_commit)
    changed_paths = tuple(
        sorted(
            (
                path
                for path in set(base_tree) | set(implementation_tree)
                if base_tree.get(path) != implementation_tree.get(path)
            ),
            key=lambda value: value.encode("utf-8"),
        )
    )
    if frozenset(changed_paths) != frozenset(IMPLEMENTATION_PATHS):
        raise BuildRefusal("implementation differs from the exact fourteen-path scope")
    implementation_rows: list[dict[str, object]] = []
    for ordinal, path in enumerate(IMPLEMENTATION_PATHS):
        before = base_tree.get(path)
        after = implementation_tree.get(path)
        expected_status = "M" if ordinal < 2 else "A"
        observed_status = (
            "A" if before is None and after is not None
            else "M" if before is not None and after is not None
            else "D" if before is not None
            else "ABSENT"
        )
        if observed_status != expected_status:
            raise BuildRefusal(
                f"implementation add/modify classification differs: {path}"
            )
        row, _raw = _file_row(store, implementation_commit, path)
        implementation_rows.append(row)

    manifest_row, manifest_raw = _file_row(
        store, implementation_commit, STAGE_E_PATH_MANIFEST
    )
    del manifest_row
    manifest = _strict_json_blob(manifest_raw, "Stage E path manifest")
    try:
        scope = manifest["prospective_harness_implementation"]
        stage_e_paths = tuple(scope["modified_paths"]) + tuple(scope["new_paths"])
    except (KeyError, TypeError) as exc:
        raise BuildRefusal("Stage E path manifest projection is absent") from exc
    if (
        scope.get("modified_path_count") != 1
        or scope.get("new_path_count") != 50
        or scope.get("total_path_count") != 51
        or len(stage_e_paths) != 51
        or len(set(stage_e_paths)) != 51
    ):
        raise BuildRefusal("Stage E path manifest count or uniqueness differs")
    expected_descendant_paths = frozenset(
        (*stage_e_paths, *AUTHORITY_PATHS, REACHABILITY_PATH, *IMPLEMENTATION_PATHS[2:])
    )
    descendant_base_tree = store.tree_map(DESCENDANT_PATH_BASE_COMMIT)
    descendant_tree = store.tree_map(implementation_commit)
    observed_descendant_paths = frozenset(
        path
        for path in set(descendant_base_tree) | set(descendant_tree)
        if descendant_base_tree.get(path) != descendant_tree.get(path)
    )
    if (
        len(expected_descendant_paths) != 82
        or observed_descendant_paths != expected_descendant_paths
        or any(descendant_tree.get(path) is None for path in expected_descendant_paths)
    ):
        raise BuildRefusal("final corrected descendant path closure is not exactly 82")
    return authority_rows, implementation_rows


def _runtime_projection() -> dict[str, object]:
    return {
        "schema": "stage_f_binding_foundation_build_runtime_projection/v1",
        "implementation": sys.implementation.name,
        "cache_tag": sys.implementation.cache_tag,
        "python_version": list(sys.version_info[:5]),
        "platform": sys.platform,
        "machine": platform.machine(),
        "pointer_bits": 8 * struct.calcsize("P"),
    }


def _environment_projection() -> dict[str, object]:
    return {
        "schema": "stage_f_binding_foundation_build_environment_projection/v1",
        "image_digest": (
            "sha256:a1f225293efe68c4cb9dddb084b04fa1a21a4d751ad130d0224902e00b1e55ab"
        ),
        "python": "CPython 3.14.4 final",
        "sqlite": "3.46.1",
        "installed_artifact_sha256": (
            "3d11dca3efe1798f02da5faf16e1eeff30b0ddb38cf0a9dccb8ab43193b794c2"
        ),
    }


def _zipapp_bytes(blobs: dict[str, bytes]) -> bytes:
    stream = io.BytesIO()
    if stream.tell() != 0 or stream.getvalue() != b"":
        raise BuildRefusal("ZIP build stream is not empty at offset zero")
    with zipfile.ZipFile(
        stream,
        mode="w",
        compression=zipfile.ZIP_STORED,
        allowZip64=False,
        strict_timestamps=True,
    ) as archive:
        archive.comment = b""
        for archive_path, source_path in ZIPAPP_PATHS:
            info = zipfile.ZipInfo(archive_path, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_STORED
            info.create_system = 3
            info.create_version = 20
            info.extract_version = 20
            info.reserved = 0
            info.volume = 0
            info.internal_attr = 0
            info.external_attr = 0o100644 << 16
            info.flag_bits = 0
            info.extra = b""
            info.comment = b""
            info._compresslevel = None
            archive.writestr(info, blobs[source_path])
    raw = stream.getvalue()
    _verify_zipapp(raw, blobs)
    return raw


def _take_struct(raw: bytes, offset: int, format_string: str, label: str) -> tuple[tuple[int, ...], int]:
    size = struct.calcsize(format_string)
    end = offset + size
    if end > len(raw):
        raise BuildRefusal(f"truncated zipapp {label}")
    return struct.unpack_from(format_string, raw, offset), end


def _verify_raw_zip_headers(raw: bytes, blobs: dict[str, bytes]) -> None:
    expected_local: list[tuple[str, str, int, int]] = []
    offset = 0
    for archive_path, source_path in ZIPAPP_PATHS:
        local_offset = offset
        fields, offset = _take_struct(raw, offset, "<IHHHHHIIIHH", "local header")
        (
            signature,
            version_needed,
            flags,
            compression,
            mod_time,
            mod_date,
            crc,
            compressed_size,
            uncompressed_size,
            name_size,
            extra_size,
        ) = fields
        name = archive_path.encode("ascii", "strict")
        content = blobs[source_path]
        if (
            signature != 0x04034B50
            or version_needed != 20
            or flags != 0
            or compression != 0
            or mod_time != 0
            or mod_date != 33
            or crc != (zlib.crc32(content) & 0xFFFFFFFF)
            or compressed_size != len(content)
            or uncompressed_size != len(content)
            or name_size != len(name)
            or extra_size != 0
            or raw[offset : offset + name_size] != name
        ):
            raise BuildRefusal(f"zipapp local header differs: {archive_path}")
        offset += name_size
        if raw[offset : offset + len(content)] != content:
            raise BuildRefusal(f"zipapp local member bytes differ: {archive_path}")
        offset += len(content)
        expected_local.append((archive_path, source_path, local_offset, crc))

    central_offset = offset
    for archive_path, source_path, local_offset, crc in expected_local:
        fields, offset = _take_struct(
            raw, offset, "<IHHHHHHIIIHHHHHII", "central header"
        )
        (
            signature,
            version_made_by,
            version_needed,
            flags,
            compression,
            mod_time,
            mod_date,
            central_crc,
            compressed_size,
            uncompressed_size,
            name_size,
            extra_size,
            comment_size,
            disk_start,
            internal_attributes,
            external_attributes,
            returned_local_offset,
        ) = fields
        name = archive_path.encode("ascii", "strict")
        content = blobs[source_path]
        if (
            signature != 0x02014B50
            or version_made_by != 788
            or version_needed != 20
            or flags != 0
            or compression != 0
            or mod_time != 0
            or mod_date != 33
            or central_crc != crc
            or compressed_size != len(content)
            or uncompressed_size != len(content)
            or name_size != len(name)
            or extra_size != 0
            or comment_size != 0
            or disk_start != 0
            or internal_attributes != 0
            or external_attributes != (0o100644 << 16)
            or returned_local_offset != local_offset
            or raw[offset : offset + name_size] != name
        ):
            raise BuildRefusal(f"zipapp central header differs: {archive_path}")
        offset += name_size

    central_size = offset - central_offset
    fields, offset = _take_struct(raw, offset, "<IHHHHIIH", "EOCD")
    (
        signature,
        disk_number,
        central_start_disk,
        entries_on_disk,
        total_entries,
        returned_central_size,
        returned_central_offset,
        comment_size,
    ) = fields
    if (
        signature != 0x06054B50
        or disk_number != 0
        or central_start_disk != 0
        or entries_on_disk != len(ZIPAPP_PATHS)
        or total_entries != len(ZIPAPP_PATHS)
        or returned_central_size != central_size
        or returned_central_offset != central_offset
        or comment_size != 0
        or offset != len(raw)
    ):
        raise BuildRefusal("zipapp EOCD or trailing bytes differ")


def _verify_zipapp(raw: bytes, blobs: dict[str, bytes]) -> None:
    if not raw.startswith(b"PK\x03\x04"):
        raise BuildRefusal("zipapp has a prefix or missing local header")
    _verify_raw_zip_headers(raw, blobs)
    with zipfile.ZipFile(io.BytesIO(raw), mode="r", allowZip64=False) as archive:
        if archive.comment != b"" or tuple(archive.namelist()) != tuple(
            row[0] for row in ZIPAPP_PATHS
        ):
            raise BuildRefusal("zipapp member order or archive comment differs")
        for info, (archive_path, source_path) in zip(
            archive.infolist(), ZIPAPP_PATHS, strict=True
        ):
            if (
                info.filename != archive_path
                or info.date_time != (1980, 1, 1, 0, 0, 0)
                or info.compress_type != zipfile.ZIP_STORED
                or info.create_system != 3
                or info.create_version != 20
                or info.extract_version != 20
                or info.reserved != 0
                or info.volume != 0
                or info.internal_attr != 0
                or info.external_attr != 0o100644 << 16
                or info.flag_bits != 0
                or info.extra != b""
                or info.comment != b""
                or archive.read(info) != blobs[source_path]
            ):
                raise BuildRefusal(f"zipapp member differs: {archive_path}")


def _write_new(path: Path, raw: bytes) -> None:
    try:
        with path.open("xb") as stream:
            stream.write(raw)
            stream.flush()
    except FileExistsError as exc:
        raise BuildRefusal(f"output already exists: {path.name}") from exc


def _parse_git_batch(
    batch: bytes, ordered_object_ids: list[str]
) -> list[tuple[str, str, bytes]]:
    """Parse legacy synthetic batch fixtures; production uses the pure store."""

    material: list[tuple[str, str, bytes]] = []
    offset = 0
    for requested_id in ordered_object_ids:
        header_end = batch.find(b"\n", offset)
        if header_end < 0:
            raise BuildRefusal("Git batch object header is truncated")
        try:
            returned_id, object_type, size_text = batch[offset:header_end].decode(
                "ascii", "strict"
            ).split(" ")
            size = int(size_text)
        except (UnicodeError, ValueError) as exc:
            raise BuildRefusal("Git batch object header is malformed") from exc
        if (
            returned_id != requested_id
            or object_type not in {"commit", "tree", "blob"}
            or size < 0
        ):
            raise BuildRefusal("Git batch object identity, type, or size differs")
        start = header_end + 1
        end = start + size
        if end >= len(batch) or batch[end : end + 1] != b"\n":
            raise BuildRefusal("Git batch object body is truncated")
        raw = batch[start:end]
        offset = end + 1
        framed = (
            object_type.encode("ascii")
            + b" "
            + str(len(raw)).encode("ascii")
            + b"\0"
            + raw
        )
        if hashlib.sha1(framed, usedforsecurity=False).hexdigest() != requested_id:
            raise BuildRefusal(
                f"reachable Git object content address differs: {requested_id}"
            )
        material.append((object_type, requested_id, raw))
    if offset != len(batch):
        raise BuildRefusal("Git batch object output has trailing bytes")
    return material


def _materialize_verified_git_objects(
    store: _GitObjectStore,
    output: Path,
    implementation_commit: str,
    additional_complete_tree_commits: tuple[str, ...] = (),
) -> Path:
    coordinate_chain = (
        DESCENDANT_PATH_BASE_COMMIT,
        ACCEPTED_BASE_COMMIT,
        ORIGINAL_AUTHORITY_CANDIDATE_COMMIT,
        ORIGINAL_AUTHORITY_INTEGRATION_COMMIT,
        CORRECTION_REQUIRED_TARGET_COMMIT,
        CORRECTION_AUTHORITY_CANDIDATE_COMMIT,
        CORRECTION_AUTHORITY_INTEGRATION_COMMIT,
        REACHABILITY_CANDIDATE_COMMIT,
        REACHABILITY_INTEGRATION_COMMIT,
        FINAL_AUTHORITY_CANDIDATE_COMMIT,
        FINAL_AUTHORITY_INTEGRATION_COMMIT,
        FINAL_REACHABILITY_CANDIDATE_COMMIT,
        FINAL_REACHABILITY_INTEGRATION_COMMIT,
        implementation_commit,
    )
    required_coordinates = set(coordinate_chain)
    required_coordinates.update(REJECTED_FOUNDATION_COMMITS)
    object_ids: set[str] = set()
    for ancestor, descendant in zip(coordinate_chain, coordinate_chain[1:]):
        object_ids.update(store.ancestry_witness(descendant, ancestor))
    for complete_tree_commit in additional_complete_tree_commits:
        object_ids.update(
            store.ancestry_witness(complete_tree_commit, implementation_commit)
        )
        required_coordinates.add(complete_tree_commit)
    for commit in sorted(required_coordinates):
        object_ids.update(store.complete_tree_object_ids(commit))
    ordered_object_ids = sorted(object_ids)
    material = []
    for object_id in ordered_object_ids:
        object_type, raw = store.read_object(object_id)
        if object_type not in {"commit", "tree", "blob"}:
            raise BuildRefusal("required Git material has a forbidden object type")
        material.append((object_type, object_id, raw))
    material.sort(key=lambda row: (row[0].encode("ascii"), row[1].encode("ascii")))
    object_directory = output / GIT_OBJECT_DIRECTORY_NAME
    try:
        object_directory.mkdir()
    except FileExistsError as exc:
        raise BuildRefusal(f"output already exists: {object_directory.name}") from exc
    entries: list[dict[str, object]] = []
    for object_type, object_id, raw in material:
        path = object_directory / f"{object_type}-{object_id}.raw"
        _write_new(path, raw)
        entries.append(
            {
                "object_type": object_type,
                "object_id": object_id,
                "byte_count": len(raw),
                "raw_sha256": _sha256(raw),
                "path": os.fspath(path.resolve(strict=True)),
            }
        )
    index = {
        "schema": "stage_f_verified_git_object_material_index/v1",
        "entries": entries,
        "entry_count": len(entries),
    }
    index_path = output / GIT_OBJECT_INDEX_NAME
    _write_new(index_path, _canonical_bytes(index))
    return index_path


def build(
    source: Path,
    output: Path,
    identity_projection_path: Path | None = None,
) -> tuple[Path, Path]:
    source = source.resolve(strict=True)
    output = output.resolve(strict=True)
    if not source.is_dir() or not output.is_dir():
        raise BuildRefusal("source and output must be existing directories")
    store = _GitObjectStore.open_worktree(source)
    commit, tree = _coordinate(store)
    store.assert_clean_checkout(commit)
    authority_rows, implementation_rows = _assert_corrected_repository(store, commit)
    source_rows: dict[str, dict[str, object]] = {}
    blobs: dict[str, bytes] = {}
    for relative in IMPLEMENTATION_PATHS:
        row, raw = _file_row(store, commit, relative)
        if relative in SOURCE_PATHS:
            source_rows[relative] = row
            blobs[relative] = raw
    implementation_preimage = {
        "schema": "stage_f_binding_foundation_build_implementation_projection/v3",
        "integrated_authority_commit": FINAL_AUTHORITY_INTEGRATION_COMMIT,
        "integrated_authority_tree": FINAL_AUTHORITY_INTEGRATION_TREE,
        "accepted_reachability_commit": FINAL_REACHABILITY_INTEGRATION_COMMIT,
        "accepted_reachability_tree": FINAL_REACHABILITY_INTEGRATION_TREE,
        "ordered_integrated_authority_file_rows": authority_rows,
        "integrated_authority_file_count": len(authority_rows),
        "implementation_commit": commit,
        "implementation_tree": tree,
        "ordered_implementation_file_rows": implementation_rows,
        "implementation_file_count": len(implementation_rows),
    }
    if identity_projection_path is None:
        identities = {
            "binding_implementation_identity": _identity(
                "stage_f_binding_implementation/v3", implementation_preimage
            ),
            "execution_environment_policy_identity": _identity(
                "stage_f_execution_environment_policy/v1", _environment_projection()
            ),
            "host_validation_runtime_identity": _identity(
                "stage_f_host_validation_runtime/v1", _runtime_projection()
            ),
        }
        identity_projection_disposition = "SYNTHETIC_NON_EVIDENCE"
    else:
        identities = _load_identity_projection(identity_projection_path)
        identity_projection_disposition = "BOUND_EXACT_INPUT"
    members = []
    for relative in SOURCE_PATHS:
        member = dict(source_rows[relative])
        member["content_base64"] = base64.b64encode(blobs[relative]).decode("ascii")
        members.append(member)
    source_bundle = {
        "schema": "stage_f_binding_validator_source_bundle/v1",
        "binding_implementation_identity": identities["binding_implementation_identity"],
        "implementation_commit": commit,
        "implementation_tree": tree,
        "execution_environment_policy_identity": identities[
            "execution_environment_policy_identity"
        ],
        "host_validation_runtime_identity": identities["host_validation_runtime_identity"],
        "ordered_members": members,
        "member_count": len(members),
    }
    source_bundle_raw = _canonical_bytes(source_bundle)
    zipapp_raw = _zipapp_bytes(blobs)
    schema_row, schema_raw = _file_row(store, commit, AUTHORITY_SCHEMA_PATH)
    if (
        schema_row["git_object"] != AUTHORITY_SCHEMA_GIT_OBJECT
        or schema_row["byte_count"] != AUTHORITY_SCHEMA_BYTE_COUNT
        or schema_row["raw_sha256"] != AUTHORITY_SCHEMA_SHA256
    ):
        raise BuildRefusal("authority schema differs from the exact integrated Git blob")
    _assert_effective_schema(schema_raw)
    bundle_path = output / SOURCE_BUNDLE_NAME
    zipapp_path = output / ZIPAPP_NAME
    schema_path = output / MATERIALIZED_SCHEMA_NAME
    _write_new(bundle_path, source_bundle_raw)
    _write_new(zipapp_path, zipapp_raw)
    _write_new(schema_path, schema_raw)
    git_object_index_path = _materialize_verified_git_objects(store, output, commit)
    store.assert_clean_checkout(commit)
    print(f"SOURCE_BUNDLE_SHA256={_sha256(source_bundle_raw)}")
    print(f"SOURCE_BUNDLE_BYTES={len(source_bundle_raw)}")
    print(f"ZIPAPP_SHA256={_sha256(zipapp_raw)}")
    print(f"ZIPAPP_BYTES={len(zipapp_raw)}")
    print(f"AUTHORITY_SCHEMA_SHA256={_sha256(schema_raw)}")
    print(f"AUTHORITY_SCHEMA_BYTES={len(schema_raw)}")
    print(f"GIT_OBJECT_MATERIAL_INDEX={git_object_index_path}")
    print("GIT_OBJECT_ACQUISITION=PURE_PYTHON_CONTENT_ADDRESSED")
    print(f"IDENTITY_PROJECTION_DISPOSITION={identity_projection_disposition}")
    print("SCIENTIFIC_EXECUTION_COUNT=0")
    return bundle_path, zipapp_path


def export_git_material(
    source: Path,
    output: Path,
    foundation_implementation_commit: str,
    complete_tree_commits: tuple[str, ...],
) -> Path:
    source = source.resolve(strict=True)
    output = output.resolve(strict=True)
    if (
        not source.is_dir()
        or not output.is_dir()
        or GIT_OBJECT_RE.fullmatch(foundation_implementation_commit) is None
        or not complete_tree_commits
        or len(complete_tree_commits) != len(set(complete_tree_commits))
        or any(GIT_OBJECT_RE.fullmatch(commit) is None for commit in complete_tree_commits)
    ):
        raise BuildRefusal("Git-material export inputs are malformed")
    store = _GitObjectStore.open_worktree(source)
    head = store.head_commit()
    store.assert_clean_checkout(head)
    _assert_corrected_repository(store, foundation_implementation_commit)
    path = _materialize_verified_git_objects(
        store,
        output,
        foundation_implementation_commit,
        complete_tree_commits,
    )
    store.assert_clean_checkout(head)
    print(f"GIT_OBJECT_MATERIAL_INDEX={path}")
    print("GIT_OBJECT_ACQUISITION=PURE_PYTHON_CONTENT_ADDRESSED")
    print("SCIENTIFIC_EXECUTION_COUNT=0")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--identity-projection", type=Path)
    parser.add_argument("--material-only", action="store_true")
    parser.add_argument("--foundation-implementation-commit")
    parser.add_argument("--complete-tree-commit", action="append", default=[])
    args = parser.parse_args(argv)
    try:
        if args.material_only:
            if args.identity_projection is not None or args.foundation_implementation_commit is None:
                raise BuildRefusal("material-only arguments differ")
            export_git_material(
                args.source,
                args.output,
                args.foundation_implementation_commit,
                tuple(args.complete_tree_commit),
            )
        else:
            if args.foundation_implementation_commit is not None or args.complete_tree_commit:
                raise BuildRefusal("foundation build received material-only arguments")
            build(
                args.source,
                args.output,
                args.identity_projection,
            )
    except (BuildRefusal, OSError, UnicodeError, zipfile.BadZipFile) as exc:
        print(f"STAGE_F_BINDING_BUILD_REFUSED: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
