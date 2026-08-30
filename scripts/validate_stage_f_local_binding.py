from __future__ import annotations

import argparse
import base64
import binascii
import builtins
import ctypes
import hashlib
import io
import json
import os
import re
import stat as stat_module
import struct
import subprocess
import sys
import time
import unicodedata
import zipfile
import zlib
from collections.abc import Callable, Mapping
from datetime import datetime, timezone
from pathlib import Path


_BOOTSTRAP_SENTINEL = "_EBU_STAGE_F_LOCKED_ZIPAPP_V1"
_BOOTSTRAP_BASE_OPTIONS = (
    "--validator-zipapp",
    "--validator-zipapp-byte-count",
    "--validator-zipapp-sha256",
    "--host-runtime-lock-acquisition-sha256",
    "--durability-probe-phase",
    "--invocation-preimage",
)
_BOOTSTRAP_POST_OPTIONS = (
    "--restart-challenge",
    "--restart-challenge-sha256",
    "--write-acknowledgement",
)


def _require_preimport_bootstrap_lock() -> tuple[object, int, str, int, str]:
    context = getattr(builtins, _BOOTSTRAP_SENTINEL, None)
    arguments = sys.argv[1:]
    durability_vector = (
        len(arguments) in (12, 18)
        and tuple(arguments[:12:2]) == _BOOTSTRAP_BASE_OPTIONS
        and (
            (len(arguments) == 12 and arguments[9] != "POST_RESTART")
            or (
                len(arguments) == 18
                and arguments[9] == "POST_RESTART"
                and tuple(arguments[12::2]) == _BOOTSTRAP_POST_OPTIONS
            )
        )
    )
    static_vector = bool(arguments) and arguments[0] in {
        "source-artifacts",
        "durability-receipt",
        "readiness-chain",
        "record-chain",
    }
    valid_vector = durability_vector or static_vector
    valid_context = (
        type(context) is tuple
        and len(context) == 5
        and type(context[0]) is object
        and type(context[1]) is int
        and 0 < context[1] < (1 << 64)
        and type(context[2]) is str
        and context[2] == sys.argv[0]
        and type(context[3]) is int
        and 0 < context[3] < (1 << 64)
        and type(context[4]) is str
        and len(context[4]) == 64
        and all(character in "0123456789abcdef" for character in context[4])
    )
    if (
        not valid_vector
        or not valid_context
        or (
            durability_vector
            and (
                arguments[1] != context[2]
                or arguments[3] != str(context[3])
                or arguments[5] != context[4]
            )
        )
    ):
        print(
            "STAGE_F_LOCAL_BINDING_REFUSED: missing or mismatched pre-import locked-bootstrap context",
            file=sys.stderr,
        )
        raise SystemExit(2)
    return context


_BOOTSTRAP_LOCK_CONTEXT = (
    _require_preimport_bootstrap_lock() if __name__ == "__main__" else None
)
_BOOTSTRAP_LOCK_EVIDENCE = getattr(
    builtins, "_EBU_STAGE_F_BOOTSTRAP_LOCK_EVIDENCE_V1", None
)
if isinstance(_BOOTSTRAP_LOCK_EVIDENCE, dict):
    _BOOTSTRAP_LOCK_EVIDENCE["u"] = time.time_ns()


from stage_f_binding.binding import (
    ACCEPTED_BASE,
    AUTHORITY_PATHS,
    AUTHORITY_CANDIDATE_COMMIT,
    AUTHORITY_INTEGRATION_COMMIT,
    AUTHORITY_INTEGRATION_TREE,
    BINDING_FOUNDATION_BASE_COMMIT,
    BINDING_FOUNDATION_BASE_TREE,
    CAMPAIGN_ORDER,
    ClosedSchemaValidator,
    IMPLEMENTATION_PATHS,
    VerifiedGitRepository,
    VALIDATOR_SOURCE_PATHS,
    VALIDATOR_ZIPAPP_PATHS,
    validate_binding_validation_receipt,
    validate_campaign_authorization,
    validate_durability_private_paths,
    validate_independent_audit_receipt,
    validate_immutable_bundle_chain,
    validate_local_binding_bundle,
    validate_post_packet_user_authorization_receipt,
    validate_private_host_manifest,
    validate_public_host_binding,
    validate_readiness_record,
    validate_sealed_campaign_packet,
)
from stage_f_binding.canonical import (
    BindingRefusal,
    assert_zero_science_counters,
    canonical_bytes,
    sha256_identity,
    strict_load,
    strict_loads,
    verify_identity,
)
from stage_f_binding.durability import (
    ZERO_SCIENCE_COUNTERS,
    _windows_finish_recursive_tree_watch,
    _windows_start_recursive_tree_watch,
    _write_temporary,
    execute_durability_probe_phase,
    validate_durability_receipt,
    validate_live_storage_inventory,
    validate_live_volume_capacity,
)


SOURCE_PATHS = (
    "scripts/build_stage_f_local_binding.py",
    "scripts/validate_stage_f_local_binding.py",
    "stage_f_binding/__init__.py",
    "stage_f_binding/canonical.py",
    "stage_f_binding/binding.py",
    "stage_f_binding/durability.py",
    "stage_f_binding/locked_zipapp_bootstrap.py",
)
ZIPAPP_PATHS = (
    ("__main__.py", "scripts/validate_stage_f_local_binding.py"),
    ("stage_f_binding/__init__.py", "stage_f_binding/__init__.py"),
    ("stage_f_binding/canonical.py", "stage_f_binding/canonical.py"),
    ("stage_f_binding/binding.py", "stage_f_binding/binding.py"),
    ("stage_f_binding/durability.py", "stage_f_binding/durability.py"),
)
IDENTITY_KINDS = {
    "binding_implementation_identity": "stage_f_binding_implementation/v1",
    "execution_environment_policy_identity": "stage_f_execution_environment_policy/v1",
    "host_validation_runtime_identity": "stage_f_host_validation_runtime/v1",
}
SOURCE_BUNDLE_KEYS = frozenset(
    {
        "schema",
        "binding_implementation_identity",
        "implementation_commit",
        "implementation_tree",
        "execution_environment_policy_identity",
        "host_validation_runtime_identity",
        "ordered_members",
        "member_count",
    }
)
MEMBER_KEYS = frozenset(
    {"path", "mode", "git_object", "byte_count", "raw_sha256", "content_base64"}
)
SHA256_RE = re.compile(r"[0-9a-f]{64}")
GIT_OBJECT_RE = re.compile(r"[0-9a-f]{40}")
IDENTITY_MATERIAL_INDEX_KEYS = frozenset({"schema", "entries", "entry_count"})
GIT_OBJECT_MATERIAL_INDEX_KEYS = frozenset({"schema", "entries", "entry_count"})
GIT_OBJECT_MATERIAL_ENTRY_KEYS = frozenset(
    {"object_type", "object_id", "byte_count", "raw_sha256", "path"}
)
IDENTITY_MATERIAL_ENTRY_KEYS = frozenset({"identity", "encoding", "path"})
REFERENCED_BINDING_INDEX_KEYS = frozenset({"schema", "entries", "entry_count"})
REFERENCED_BINDING_ENTRY_KEYS = frozenset({"route_id", "record_path", "file_path"})
DURABILITY_RECEIPT_INDEX_KEYS = frozenset({"schema", "entries", "entry_count"})
DURABILITY_RECEIPT_ENTRY_KEYS = frozenset({"identity", "path"})
PROBE_INVOCATION_KEYS = frozenset(
    {
        "schema",
        "phase",
        "binding_validator_identity",
        "execution_environment_policy_identity",
        "host_validation_runtime_identity",
        "host_runtime_lock_acquisition_sha256",
        "bootstrap_source_path",
        "bootstrap_git_row",
        "bootstrap_source_byte_count",
        "bootstrap_source_utf8_base64",
        "executable_path_identity",
        "validator_zipapp_path_identity",
        "validator_zipapp_byte_count",
        "validator_zipapp_sha256",
        "invocation_preimage_path_identity",
        "restart_challenge_path_identity",
        "restart_challenge_sha256",
        "acknowledgement_path_identity",
        "command_schema",
        "command_line_construction",
        "command_line_encoding",
        "command_line_base64",
        "command_line_utf16_code_unit_count",
        "entrypoint_mode",
        "isolated_mode",
        "network_access_permitted",
        "scientific_counters",
    }
)
GIT_ROW_KEYS = frozenset({"path", "mode", "git_object", "byte_count", "raw_sha256"})
AUTHORITY_SCHEMA_PATH = "stage_f_local_execution_binding_evidence_schema.json"
AUTHORITY_SCHEMA_GIT_OBJECT = "ec64c0aa7313ed421657cc1bff2a4b0b332504df"
AUTHORITY_SCHEMA_BYTE_COUNT = 229992
AUTHORITY_SCHEMA_SHA256 = "0062377ea1aea416e09e6c149ec3973f5aab632a0b84b438d7e181aee505a396"


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _blob_id(raw: bytes) -> str:
    framed = b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw
    return hashlib.sha1(framed).hexdigest()


def _load_authority_schema(path: Path, raw: bytes | None = None) -> object:
    if raw is None:
        raw = path.read_bytes()
    if (
        len(raw) != AUTHORITY_SCHEMA_BYTE_COUNT
        or _sha256(raw) != AUTHORITY_SCHEMA_SHA256
        or _blob_id(raw) != AUTHORITY_SCHEMA_GIT_OBJECT
    ):
        raise BindingRefusal("binding evidence schema differs from committed authority bytes")
    return strict_loads(raw)


def _normalized_volume_guid_path(path: Path, label: str) -> str:
    if os.name != "nt":
        raise BindingRefusal(f"{label} volume-GUID resolution requires Windows")
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    create_file = kernel32.CreateFileW
    create_file.argtypes = (
        ctypes.c_wchar_p,
        ctypes.c_uint32,
        ctypes.c_uint32,
        ctypes.c_void_p,
        ctypes.c_uint32,
        ctypes.c_uint32,
        ctypes.c_void_p,
    )
    create_file.restype = ctypes.c_void_p
    close_handle = kernel32.CloseHandle
    close_handle.argtypes = (ctypes.c_void_p,)
    close_handle.restype = ctypes.c_int
    get_final = kernel32.GetFinalPathNameByHandleW
    get_final.argtypes = (ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_uint32, ctypes.c_uint32)
    get_final.restype = ctypes.c_uint32
    handle = create_file(
        os.fspath(path),
        0x80,
        7,
        None,
        3,
        0x02200000,
        None,
    )
    if handle in (None, ctypes.c_void_p(-1).value):
        raise BindingRefusal(f"{label} could not be opened without following reparse points")
    try:
        buffer = ctypes.create_unicode_buffer(32768)
        length = get_final(handle, buffer, len(buffer), 1)
        if not 0 < length < len(buffer):
            raise BindingRefusal(f"{label} volume-GUID final-path query failed")
        result = buffer.value
    finally:
        if not close_handle(handle):
            raise BindingRefusal(f"{label} handle close failed")
    return result.rstrip("\\")


def _verify_private_root_outside_git(
    private_manifest: Mapping[str, object], source: Path
) -> None:
    stage_root_text = private_manifest["filesystem"]["private_directories"]["stage_f_root"]
    stage_root = Path(stage_root_text)
    if not stage_root.is_dir():
        raise BindingRefusal("private Stage F root does not exist as a directory")
    root_stat = stage_root.stat(follow_symlinks=False)
    if getattr(root_stat, "st_file_attributes", 0) & 0x400:
        raise BindingRefusal("private Stage F root is a reparse point")
    for ancestor in (stage_root, *stage_root.parents):
        if (ancestor / ".git").exists():
            raise BindingRefusal("private Stage F root is inside a Git worktree")
    observed_root = _normalized_volume_guid_path(stage_root, "private Stage F root")
    if observed_root != stage_root_text:
        raise BindingRefusal("private Stage F root differs from its handle-resolved path")
    source = source.resolve(strict=True)
    marker = source / ".git"
    worktrees: list[Path] = []
    if marker.is_dir():
        common = marker.resolve(strict=True)
        worktrees.append(source)
    elif marker.is_file():
        marker_text = marker.read_text(encoding="utf-8", errors="strict")
        if not marker_text.startswith("gitdir: ") or "\n" in marker_text.strip("\n"):
            raise BindingRefusal("source Git administrative pointer is malformed")
        administrative = Path(marker_text[8:].strip())
        if not administrative.is_absolute():
            administrative = source / administrative
        administrative = administrative.resolve(strict=True)
        commondir_path = administrative / "commondir"
        if not commondir_path.is_file():
            raise BindingRefusal("linked worktree lacks a common-dir pointer")
        commondir_text = commondir_path.read_text(encoding="utf-8", errors="strict").strip()
        common_candidate = Path(commondir_text)
        if not common_candidate.is_absolute():
            common_candidate = administrative / common_candidate
        common = common_candidate.resolve(strict=True)
        worktrees.append(source)
    else:
        raise BindingRefusal("source has no exact Git administrative marker")
    if common.name != ".git" or not common.is_dir():
        raise BindingRefusal("source Git common directory is malformed")
    main_worktree = common.parent.resolve(strict=True)
    if main_worktree not in worktrees:
        worktrees.append(main_worktree)
    linked = common / "worktrees"
    if linked.exists():
        if not linked.is_dir():
            raise BindingRefusal("Git linked-worktree administration is malformed")
        try:
            administrations = sorted(linked.iterdir(), key=lambda path: path.name.encode("utf-8"))
        except OSError as exc:
            raise BindingRefusal("Git linked-worktree enumeration failed") from exc
        for administrative in administrations:
            pointer = administrative / "gitdir"
            if not administrative.is_dir() or not pointer.is_file():
                raise BindingRefusal("Git linked-worktree entry is incomplete")
            pointer_text = pointer.read_text(encoding="utf-8", errors="strict").strip()
            worktree_marker = Path(pointer_text)
            if not worktree_marker.is_absolute() or worktree_marker.name != ".git":
                raise BindingRefusal("Git linked-worktree pointer is malformed")
            worktree = worktree_marker.parent.resolve(strict=True)
            if worktree not in worktrees:
                worktrees.append(worktree)
    if not worktrees:
        raise BindingRefusal("Git worktree inventory is empty")
    for ordinal, worktree in enumerate(worktrees):
        git_root = _normalized_volume_guid_path(worktree, f"Git worktree {ordinal}")
        if observed_root == git_root or observed_root.startswith(git_root + "\\"):
            raise BindingRefusal("private Stage F root is inside a Git worktree")


class _WIN32_FIND_STREAM_DATA(ctypes.Structure):
    _fields_ = (("StreamSize", ctypes.c_int64), ("cStreamName", ctypes.c_wchar * 296))


class _LOCKED_FILE_STANDARD_INFO(ctypes.Structure):
    _fields_ = (
        ("AllocationSize", ctypes.c_int64),
        ("EndOfFile", ctypes.c_int64),
        ("NumberOfLinks", ctypes.c_uint32),
        ("DeletePending", ctypes.c_int32),
        ("Directory", ctypes.c_int32),
    )


class _LOCKED_FILE_ATTRIBUTE_TAG_INFO(ctypes.Structure):
    _fields_ = (("FileAttributes", ctypes.c_uint32), ("ReparseTag", ctypes.c_uint32))


class _LOCKED_FILE_ID_INFO(ctypes.Structure):
    _fields_ = (
        ("VolumeSerialNumber", ctypes.c_uint64),
        ("FileId", ctypes.c_ubyte * 16),
    )


class _RetainedMaterialLocks:
    """Read retained inputs from handles that deny concurrent write/delete access."""

    def __init__(
        self, retained_root: str, selected_volume_serial: int | None = None
    ) -> None:
        if os.name != "nt":
            raise BindingRefusal("retained material locking requires Windows")
        if not isinstance(retained_root, str) or not retained_root.startswith("\\\\?\\Volume{"):
            raise BindingRefusal("retained-evidence root is not a normalized volume-GUID path")
        self._root = retained_root.rstrip("\\")
        self._root_folded = self._root.casefold()
        self._selected_volume_serial = selected_volume_serial
        self._handles: dict[str, tuple[int, str, int, str, int]] = {}
        self._auxiliary_locks: dict[str, _RetainedMaterialLocks] = {}
        self._kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        self._create_file = self._kernel32.CreateFileW
        self._create_file.argtypes = (
            ctypes.c_wchar_p,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_void_p,
        )
        self._create_file.restype = ctypes.c_void_p
        self._close_handle = self._kernel32.CloseHandle
        self._close_handle.argtypes = (ctypes.c_void_p,)
        self._close_handle.restype = ctypes.c_int
        self._get_final = self._kernel32.GetFinalPathNameByHandleW
        self._get_final.argtypes = (
            ctypes.c_void_p,
            ctypes.c_wchar_p,
            ctypes.c_uint32,
            ctypes.c_uint32,
        )
        self._get_final.restype = ctypes.c_uint32
        self._get_info = self._kernel32.GetFileInformationByHandleEx
        self._get_info.argtypes = (
            ctypes.c_void_p,
            ctypes.c_int,
            ctypes.c_void_p,
            ctypes.c_uint32,
        )
        self._get_info.restype = ctypes.c_int
        self._set_pointer = self._kernel32.SetFilePointerEx
        self._set_pointer.argtypes = (
            ctypes.c_void_p,
            ctypes.c_int64,
            ctypes.POINTER(ctypes.c_int64),
            ctypes.c_uint32,
        )
        self._set_pointer.restype = ctypes.c_int
        self._read_file = self._kernel32.ReadFile
        self._read_file.argtypes = (
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.c_void_p,
        )
        self._read_file.restype = ctypes.c_int

    def __enter__(self) -> "_RetainedMaterialLocks":
        return self

    def __exit__(self, exception_type: object, exception: object, traceback: object) -> None:
        close_failed = False
        for auxiliary in reversed(tuple(self._auxiliary_locks.values())):
            try:
                auxiliary.__exit__(exception_type, exception, traceback)
            except BaseException:
                close_failed = True
        self._auxiliary_locks.clear()
        for handle, _path, _size, _file_id, _volume in reversed(
            tuple(self._handles.values())
        ):
            if not self._close_handle(handle):
                close_failed = True
        self._handles.clear()
        if close_failed and exception is None:
            raise BindingRefusal("retained material handle close failed")

    def read_scoped(
        self, path: Path, role_root: str, label: str
    ) -> bytes:
        if (
            not isinstance(role_root, str)
            or not role_root.startswith("\\\\?\\Volume{")
        ):
            raise BindingRefusal(f"{label} role root is not a volume-GUID path")
        key = role_root.rstrip("\\").casefold()
        scoped = self._auxiliary_locks.get(key)
        if scoped is None:
            scoped = _RetainedMaterialLocks(
                role_root, self._selected_volume_serial
            )
            self._auxiliary_locks[key] = scoped
        return scoped.read(path, label)

    def _query(self, handle: int, information_class: int, value: ctypes.Structure) -> None:
        if not self._get_info(
            handle, information_class, ctypes.byref(value), ctypes.sizeof(value)
        ):
            raise BindingRefusal("retained material handle-information query failed")

    def bind_selected_volume_serial(self, selected_volume_serial: int) -> None:
        if type(selected_volume_serial) is not int or selected_volume_serial < 0:
            raise BindingRefusal("selected retained-material volume serial is malformed")
        if any(
            volume_serial != selected_volume_serial
            for _handle, _path, _size, _file_id, volume_serial in self._handles.values()
        ):
            raise BindingRefusal("retained material FileIdInfo volume serial differs")
        self._selected_volume_serial = selected_volume_serial

    def _acquire(self, path: Path, label: str) -> tuple[int, str, int, str, int]:
        path_text = os.fspath(path)
        suffix = path_text[len(self._root) :]
        components = suffix[1:].split("\\") if suffix.startswith("\\") else []
        if (
            not path.is_absolute()
            or unicodedata.normalize("NFC", path_text) != path_text
            or not path_text.startswith(self._root + "\\")
            or not components
            or any(
                not component
                or component in {".", ".."}
                or ":" in component
                or component.endswith((".", " "))
                or "/" in component
                for component in components
            )
        ):
            raise BindingRefusal(
                f"{label} is not a lexical normalized child of retained evidence"
            )
        handle = self._create_file(
            path_text,
            0x80000000,
            0x00000001,
            None,
            3,
            0x00200000,
            None,
        )
        if handle in (None, ctypes.c_void_p(-1).value):
            raise BindingRefusal(
                f"{label} cannot be locked against concurrent write/delete access"
            )
        keep = False
        try:
            final_buffer = ctypes.create_unicode_buffer(32768)
            final_length = self._get_final(handle, final_buffer, len(final_buffer), 1)
            if not 0 < final_length < len(final_buffer):
                raise BindingRefusal(f"{label} normalized handle path query failed")
            final_path = final_buffer.value
            final_folded = final_path.casefold()
            if (
                path_text != final_path
                or not final_folded.startswith(self._root_folded + "\\")
                or ":" in final_path[len(self._root) :]
            ):
                raise BindingRefusal(
                    f"{label} is not an exact normalized child of retained evidence"
                )
            standard = _LOCKED_FILE_STANDARD_INFO()
            attributes = _LOCKED_FILE_ATTRIBUTE_TAG_INFO()
            file_id = _LOCKED_FILE_ID_INFO()
            self._query(handle, 1, standard)
            self._query(handle, 9, attributes)
            self._query(handle, 18, file_id)
            if (
                standard.Directory
                or standard.DeletePending
                or standard.NumberOfLinks != 1
                or standard.EndOfFile < 0
                or attributes.FileAttributes
                & (
                    0x40
                    | 0x200
                    | 0x400
                    | 0x800
                    | 0x1000
                    | 0x4000
                    | 0x8000
                    | 0x10000
                    | 0x20000
                    | 0x40000
                    | 0x80000
                    | 0x100000
                    | 0x400000
                )
                or attributes.ReparseTag != 0
                or (
                    self._selected_volume_serial is not None
                    and file_id.VolumeSerialNumber != self._selected_volume_serial
                )
            ):
                raise BindingRefusal(
                    f"{label} is not a single-link regular selected-volume file"
                )
            if _actual_data_streams(Path(final_path)) != [
                {
                    "stream_name": "::$DATA",
                    "stream_size_bytes": standard.EndOfFile,
                }
            ]:
                raise BindingRefusal(
                    f"{label} has an absent, named, or mismatched data stream"
                )
            key = final_folded
            file_id_hex = bytes(file_id.FileId).hex()
            existing = self._handles.get(key)
            if existing is not None:
                if existing[1] != final_path or existing[3] != file_id_hex:
                    raise BindingRefusal(f"{label} retained material alias differs")
                return existing
            record = (
                handle,
                final_path,
                standard.EndOfFile,
                file_id_hex,
                file_id.VolumeSerialNumber,
            )
            self._handles[key] = record
            keep = True
            return record
        finally:
            if not keep and not self._close_handle(handle):
                raise BindingRefusal(f"{label} rejected handle close failed")

    def read(self, path: Path, label: str) -> bytes:
        path_text = os.fspath(path)
        matching = next(
            (record for record in self._handles.values() if record[1] == path_text),
            None,
        )
        handle, _final_path, size, _file_id, _volume = (
            matching if matching is not None else self._acquire(path, label)
        )
        if "source bundle" in label:
            maximum_size = 512 * 1024 * 1024
        elif label.startswith(
            ("verified Git object material ", "identity material ")
        ):
            maximum_size = 128 * 1024 * 1024
        else:
            maximum_size = 64 * 1024 * 1024
        if size > maximum_size:
            raise BindingRefusal(f"{label} exceeds its retained-material byte ceiling")
        if not self._set_pointer(handle, 0, None, 0):
            raise BindingRefusal(f"{label} locked handle rewind failed")
        remaining = size
        chunks: list[bytes] = []
        while remaining:
            request = min(remaining, 1024 * 1024)
            buffer = ctypes.create_string_buffer(request)
            returned = ctypes.c_uint32()
            if not self._read_file(
                handle, buffer, request, ctypes.byref(returned), None
            ):
                raise BindingRefusal(f"{label} locked handle read failed")
            if returned.value == 0 or returned.value > request:
                raise BindingRefusal(f"{label} locked handle ended unexpectedly")
            chunks.append(buffer.raw[: returned.value])
            remaining -= returned.value
        raw = b"".join(chunks)
        if len(raw) != size:
            raise BindingRefusal(f"{label} locked byte count differs")
        return raw

    def retained_file_observations(self) -> dict[str, dict[str, object]]:
        observations: dict[str, dict[str, object]] = {}
        for handle, path_text, size, file_id, volume_serial in tuple(
            self._handles.values()
        ):
            if not self._set_pointer(handle, 0, None, 0):
                raise BindingRefusal("retained material final hash rewind failed")
            remaining = size
            digest = hashlib.sha256()
            while remaining:
                request = min(remaining, 1024 * 1024)
                buffer = ctypes.create_string_buffer(request)
                returned = ctypes.c_uint32()
                if not self._read_file(
                    handle, buffer, request, ctypes.byref(returned), None
                ):
                    raise BindingRefusal("retained material final hash read failed")
                if returned.value == 0 or returned.value > request:
                    raise BindingRefusal(
                        "retained material final hash ended unexpectedly"
                    )
                digest.update(buffer.raw[: returned.value])
                remaining -= returned.value
            observations[path_text] = {
                "byte_count": size,
                "sha256": digest.hexdigest(),
                "file_id_128": file_id,
                "volume_serial_number": volume_serial,
            }
        return observations


def _actual_data_streams(path: Path) -> list[dict[str, object]]:
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    find_first = kernel32.FindFirstStreamW
    find_first.argtypes = (
        ctypes.c_wchar_p,
        ctypes.c_int,
        ctypes.POINTER(_WIN32_FIND_STREAM_DATA),
        ctypes.c_uint32,
    )
    find_first.restype = ctypes.c_void_p
    find_next = kernel32.FindNextStreamW
    find_next.argtypes = (ctypes.c_void_p, ctypes.POINTER(_WIN32_FIND_STREAM_DATA))
    find_next.restype = ctypes.c_int
    find_close = kernel32.FindClose
    find_close.argtypes = (ctypes.c_void_p,)
    find_close.restype = ctypes.c_int
    data = _WIN32_FIND_STREAM_DATA()
    handle = find_first(os.fspath(path), 0, ctypes.byref(data), 0)
    if handle == ctypes.c_void_p(-1).value:
        if ctypes.get_last_error() == 38:
            return []
        raise BindingRefusal(f"data-stream enumeration failed: {path}")
    streams: list[dict[str, object]] = []
    try:
        while True:
            streams.append(
                {"stream_name": data.cStreamName, "stream_size_bytes": data.StreamSize}
            )
            if not find_next(handle, ctypes.byref(data)):
                if ctypes.get_last_error() != 38:
                    raise BindingRefusal(f"data-stream enumeration ended unexpectedly: {path}")
                break
    finally:
        if not find_close(handle):
            raise BindingRefusal(f"data-stream search handle close failed: {path}")
    return streams


def _verify_live_storage_inventory(
    private_manifest: Mapping[str, object], capacity_snapshot: Mapping[str, object]
) -> None:
    if os.name != "nt":
        raise BindingRefusal("live storage inventory verification requires Windows")
    root = Path(private_manifest["filesystem"]["private_directories"]["stage_f_root"])
    observed: dict[str, tuple[Path, os.stat_result, str]] = {}

    def add(path: Path, entry_type: str) -> None:
        relative = "." if path == root else path.relative_to(root).as_posix()
        if relative in observed:
            raise BindingRefusal(f"live storage inventory repeats a path: {relative}")
        stat = path.stat(follow_symlinks=False)
        if getattr(stat, "st_file_attributes", 0) & 0x400 or stat.st_nlink != 1:
            raise BindingRefusal(f"live storage entry is reparse-point or hard-linked: {relative}")
        observed[relative] = (path, stat, entry_type)

    add(root, "DIRECTORY")
    def refuse_walk_error(error: OSError) -> None:
        raise BindingRefusal(
            f"live storage enumeration failed: {error.filename!r}: {error}"
        ) from error

    for directory, directory_names, file_names in os.walk(
        root, topdown=True, onerror=refuse_walk_error, followlinks=False
    ):
        directory_names.sort(key=lambda name: unicodedata.normalize("NFC", name).encode("utf-8"))
        file_names.sort(key=lambda name: unicodedata.normalize("NFC", name).encode("utf-8"))
        directory_path = Path(directory)
        for name in directory_names:
            add(directory_path / name, "DIRECTORY")
        for name in file_names:
            add(directory_path / name, "REGULAR_FILE")
    inventory = capacity_snapshot["inventory_entries"]
    expected_paths = [entry["relative_path"] for entry in inventory]
    observed_paths = sorted(observed, key=lambda value: value.encode("utf-8"))
    if expected_paths != observed_paths:
        raise BindingRefusal("live recursive storage inventory path closure differs")
    for entry in inventory:
        relative = entry["relative_path"]
        path, before, entry_type = observed[relative]
        if entry["entry_type"] != entry_type:
            raise BindingRefusal(f"live storage entry type differs: {relative}")
        streams = _actual_data_streams(path)
        if streams != entry["data_streams"]:
            raise BindingRefusal(f"live storage data-stream projection differs: {relative}")
        if entry_type == "REGULAR_FILE":
            digest = hashlib.sha256()
            with path.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(chunk)
            after = path.stat(follow_symlinks=False)
            if (
                before.st_size != entry["logical_bytes"]
                or digest.hexdigest() != entry["content_sha256"]
                or (before.st_size, before.st_mtime_ns, before.st_ino)
                != (after.st_size, after.st_mtime_ns, after.st_ino)
            ):
                raise BindingRefusal(f"live storage file bytes changed or differ: {relative}")


def _materialized_private_path(
    identity: Mapping[str, object],
    materials: Mapping[tuple[str, str], object],
    label: str,
) -> Path:
    key = (identity.get("kind"), identity.get("value"))
    raw = materials.get(key)
    if not isinstance(raw, bytes) or not raw:
        raise BindingRefusal(f"{label} private-path bytes are absent")
    verify_identity(identity, raw, kind="stage_f_private_path/v1")
    try:
        value = raw.decode("utf-8", "strict")
    except UnicodeDecodeError as exc:
        raise BindingRefusal(f"{label} private-path bytes are not UTF-8") from exc
    _verify_private_path_identity(identity, value, label)
    return Path(value)


def _verify_complete_challenge_history(
    validator: ClosedSchemaValidator,
    private_manifest: Mapping[str, object],
    receipts: Sequence[Mapping[str, object]],
    materials: Mapping[tuple[str, str], object],
    read_control_material: Callable[[Path, str], bytes] | None = None,
) -> None:
    temporary_root = Path(
        private_manifest["filesystem"]["private_directories"]["temporary"]
    )
    if not temporary_root.is_dir():
        raise BindingRefusal("private temporary root is unavailable")
    def fingerprint() -> tuple[tuple[str, int, int, int], ...]:
        rows: list[tuple[str, int, int, int]] = []
        def refuse_walk_error(error: OSError) -> None:
            raise BindingRefusal(
                f"restart-control enumeration failed: {error.filename!r}: {error}"
            ) from error

        for directory, directory_names, file_names in os.walk(
            temporary_root,
            topdown=True,
            onerror=refuse_walk_error,
            followlinks=False,
        ):
            directory_names.sort()
            file_names.sort()
            for name in (*directory_names, *file_names):
                path = Path(directory) / name
                stat = path.stat(follow_symlinks=False)
                rows.append(
                    (
                        os.fspath(path.relative_to(temporary_root)),
                        stat.st_size,
                        stat.st_mtime_ns,
                        stat.st_ino,
                    )
                )
        return tuple(rows)

    initial_fingerprint = fingerprint()
    expected_challenge_paths: set[str] = set()
    expected_acknowledgement_paths: set[str] = set()
    for ordinal, receipt in enumerate(receipts):
        restart = receipt["restart_observation"]
        challenge_path = _materialized_private_path(
            restart["challenge_path_identity"], materials, f"challenge path {ordinal}"
        )
        acknowledgement_path = _materialized_private_path(
            restart["acknowledgement_path_identity"],
            materials,
            f"acknowledgement path {ordinal}",
        )
        for path, suffix, label in (
            (challenge_path, ".challenge.json", "challenge"),
            (acknowledgement_path, ".acknowledgement.json", "acknowledgement"),
        ):
            path_text = os.fspath(path)
            if (
                not path_text.startswith(os.fspath(temporary_root).rstrip("\\") + "\\")
                or not path.name.endswith(suffix)
                or _normalized_volume_guid_path(path, f"retained {label} {ordinal}")
                != path_text
            ):
                raise BindingRefusal(
                    f"retained {label} path {ordinal} escapes the temporary role"
                )
        expected_challenge_paths.add(os.fspath(challenge_path))
        expected_acknowledgement_paths.add(os.fspath(acknowledgement_path))
    discovered_challenge_paths: set[str] = set()
    discovered_acknowledgement_paths: set[str] = set()
    restart_name = re.compile(
        r"stage-f-durability-[0-9a-f]{16}-[1-9][0-9]*-[1-9][0-9]*\."
        r"(challenge|acknowledgement)\.json"
    )

    def refuse_discovery_error(error: OSError) -> None:
        raise BindingRefusal(
            f"restart-control discovery failed: {error.filename!r}: {error}"
        ) from error

    for directory, directory_names, file_names in os.walk(
        temporary_root,
        topdown=True,
        onerror=refuse_discovery_error,
        followlinks=False,
    ):
        directory_names.sort()
        file_names.sort()
        for name in file_names:
            path = Path(directory) / name
            matched_name = restart_name.fullmatch(name)
            if matched_name is None:
                continue
            stat = path.stat(follow_symlinks=False)
            if (
                stat.st_size > 65536
                or getattr(stat, "st_file_attributes", 0) & 0x400
                or stat.st_nlink != 1
            ):
                raise BindingRefusal("retained restart-control candidate is unsafe")
            if matched_name.group(1) == "acknowledgement":
                discovered_acknowledgement_paths.add(os.fspath(path))
            else:
                discovered_challenge_paths.add(os.fspath(path))
    if expected_challenge_paths != discovered_challenge_paths:
        raise BindingRefusal("receipt challenge set differs from retained temporary history")
    if expected_acknowledgement_paths != discovered_acknowledgement_paths:
        raise BindingRefusal(
            "receipt acknowledgement set differs from retained temporary history"
        )
    discovered: list[tuple[datetime, int, str]] = []
    for ordinal, receipt in enumerate(receipts):
        restart = receipt["restart_observation"]
        challenge_path = _materialized_private_path(
            restart["challenge_path_identity"],
            materials,
            f"challenge path {ordinal}",
        )
        acknowledgement_path = _materialized_private_path(
            restart["acknowledgement_path_identity"],
            materials,
            f"acknowledgement path {ordinal}",
        )
        challenge_raw = (
            challenge_path.read_bytes()
            if read_control_material is None
            else read_control_material(challenge_path, f"challenge control {ordinal}")
        )
        acknowledgement_raw = (
            acknowledgement_path.read_bytes()
            if read_control_material is None
            else read_control_material(
                acknowledgement_path, f"acknowledgement control {ordinal}"
            )
        )
        if challenge_raw != canonical_bytes(restart["challenge_preimage"]):
            raise BindingRefusal(f"retained challenge bytes differ: {ordinal}")
        if acknowledgement_raw != canonical_bytes(restart["acknowledgement_preimage"]):
            raise BindingRefusal(f"retained acknowledgement bytes differ: {ordinal}")
        discovered.append(
            (
                datetime.fromisoformat(
                    restart["challenge_preimage"]["challenge_issued_utc"][:-1]
                    + "+00:00"
                ),
                restart["challenge_preimage"]["challenge_counter"],
                os.fspath(challenge_path),
            )
        )
    discovered.sort(key=lambda row: (row[0], row[2].encode("utf-8")))
    if (
        not discovered
        or len({row[0] for row in discovered}) != len(discovered)
        or len({row[1] for row in discovered}) != len(discovered)
        or any(
        current[1] <= previous[1]
        for previous, current in zip(discovered, discovered[1:])
        )
    ):
        raise BindingRefusal("retained challenge history is not a strict high-water sequence")
    if fingerprint() != initial_fingerprint:
        raise BindingRefusal("temporary challenge history changed during validation")


def _require_not_future_utc(
    value: object, *, not_after: datetime, label: str
) -> None:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise BindingRefusal(f"{label} is not a UTC timestamp")
    try:
        observed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise BindingRefusal(f"{label} is not a UTC timestamp") from exc
    if observed > not_after:
        raise BindingRefusal(f"{label} is in the future at live validation")


def _material_for_identity(
    materials: dict[tuple[str, str], object], identity: object, label: str
) -> object:
    if type(identity) is not dict:
        raise BindingRefusal(f"{label} identity is malformed")
    key = (identity.get("kind"), identity.get("value"))
    if key not in materials:
        raise BindingRefusal(f"{label} retained preimage is absent")
    material = materials[key]
    verify_identity(identity, material, kind=key[0])
    return material


def _material_by_kind(
    materials: Mapping[tuple[str, str], object], kind: str, label: str
) -> tuple[dict[str, str], object]:
    keys = [key for key in materials if key[0] == kind]
    if len(keys) != 1:
        raise BindingRefusal(f"{label} must resolve exactly once by kind")
    key = keys[0]
    material = materials[key]
    identity = {"kind": key[0], "value": key[1], "sha256": key[1]}
    verify_identity(identity, material, kind=kind)
    return identity, material


def _closed_keys(value: object, expected: frozenset[str], label: str) -> dict[str, object]:
    if type(value) is not dict or frozenset(value) != expected:
        raise BindingRefusal(f"{label} is not the exact closed object")
    return value


def _strict_base64(value: object, label: str) -> bytes:
    if not isinstance(value, str) or any(character.isspace() for character in value):
        raise BindingRefusal(f"{label} is not canonical padded base64")
    try:
        raw = base64.b64decode(value.encode("ascii", "strict"), validate=True)
    except (UnicodeError, binascii.Error) as exc:
        raise BindingRefusal(f"{label} is not canonical padded base64") from exc
    if base64.b64encode(raw).decode("ascii") != value:
        raise BindingRefusal(f"{label} has noncanonical base64 padding")
    return raw


def _verify_private_path_identity(identity: object, value: str, label: str) -> None:
    if not isinstance(value, str) or unicodedata.normalize("NFC", value) != value:
        raise BindingRefusal(f"{label} is not an exact NFC private path")
    verify_identity(identity, value.encode("utf-8", "strict"), kind="stage_f_private_path/v1")


def _windows_command_line() -> tuple[bytes, list[str]]:
    if sys.platform != "win32":
        raise BindingRefusal("durability probes require Win32")
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    shell32 = ctypes.WinDLL("shell32", use_last_error=True)
    get_command_line = kernel32.GetCommandLineW
    get_command_line.argtypes = ()
    get_command_line.restype = ctypes.c_wchar_p
    command_text = get_command_line()
    if not isinstance(command_text, str) or not command_text:
        raise BindingRefusal("GetCommandLineW returned no command")
    argc = ctypes.c_int()
    command_line_to_argv = shell32.CommandLineToArgvW
    command_line_to_argv.argtypes = (ctypes.c_wchar_p, ctypes.POINTER(ctypes.c_int))
    command_line_to_argv.restype = ctypes.POINTER(ctypes.c_wchar_p)
    pointer = command_line_to_argv(command_text, ctypes.byref(argc))
    if not pointer or argc.value <= 0:
        raise BindingRefusal(
            f"CommandLineToArgvW failed with Win32 error {ctypes.get_last_error()}"
        )
    try:
        parsed = [pointer[index] for index in range(argc.value)]
    finally:
        local_free = kernel32.LocalFree
        local_free.argtypes = (ctypes.c_void_p,)
        local_free.restype = ctypes.c_void_p
        if local_free(ctypes.cast(pointer, ctypes.c_void_p)):
            raise BindingRefusal("LocalFree(CommandLineToArgvW) failed")
    raw = command_text.encode("utf-16le", "strict")
    if raw.endswith(b"\x00\x00") or len(raw) // 2 > 32766:
        raise BindingRefusal("observed command line has a terminal NUL or is too long")
    return raw, parsed


class _FILETIME(ctypes.Structure):
    _fields_ = (("low", ctypes.c_uint32), ("high", ctypes.c_uint32))


def _process_creation_filetime() -> int:
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    get_current_process = kernel32.GetCurrentProcess
    get_current_process.argtypes = ()
    get_current_process.restype = ctypes.c_void_p
    get_process_times = kernel32.GetProcessTimes
    get_process_times.argtypes = (
        ctypes.c_void_p,
        ctypes.POINTER(_FILETIME),
        ctypes.POINTER(_FILETIME),
        ctypes.POINTER(_FILETIME),
        ctypes.POINTER(_FILETIME),
    )
    get_process_times.restype = ctypes.c_int
    creation, exit_time, kernel_time, user_time = (_FILETIME() for _ in range(4))
    if not get_process_times(
        get_current_process(),
        ctypes.byref(creation),
        ctypes.byref(exit_time),
        ctypes.byref(kernel_time),
        ctypes.byref(user_time),
    ):
        raise BindingRefusal(
            f"GetProcessTimes(current) failed with Win32 error {ctypes.get_last_error()}"
        )
    value = (creation.high << 32) | creation.low
    if value <= 0:
        raise BindingRefusal("current process creation FILETIME is not positive")
    return value


def _probe_process_instance(
    invocation: dict[str, object], command_raw: bytes, executable_path: str
) -> dict[str, object]:
    executable_raw = Path(executable_path).read_bytes()
    return {
        "process_id": os.getpid(),
        "creation_filetime_uint64": _process_creation_filetime(),
        "executable_path_identity": invocation["executable_path_identity"],
        "executable_sha256": _sha256(executable_raw),
        "command_line_sha256": _sha256(command_raw),
        "invocation_sha256": _sha256(canonical_bytes(invocation)),
        "self_command_line_observation_api": "GetCommandLineW",
        "locked_bootstrap_verified_invocation": True,
    }


def _load_external_host_runtime_acquisition(
    invocation_path: Path, invocation: dict[str, object]
) -> tuple[dict[str, object], Path, Path]:
    acquisition_path = Path(
        os.fspath(invocation_path) + ".host-runtime-lock-acquisition.json"
    )
    schema_path = Path(os.fspath(invocation_path) + ".authority-schema.json")
    schema = _load_authority_schema(schema_path)
    validator = ClosedSchemaValidator(schema)
    acquisition = strict_load(acquisition_path, require_canonical=True)
    validator.validate_definition("host_runtime_lock_acquisition_preimage", acquisition)
    if not isinstance(acquisition, dict):
        raise BindingRefusal("host-runtime-lock acquisition is not an object")
    assert_zero_science_counters(acquisition["scientific_counters"])
    if (
        _sha256(canonical_bytes(acquisition))
        != invocation["host_runtime_lock_acquisition_sha256"]
        or acquisition["host_validation_runtime_identity"]
        != invocation["host_validation_runtime_identity"]
    ):
        raise BindingRefusal(
            "external host-runtime-lock acquisition differs from the invocation"
        )
    return acquisition, acquisition_path, schema_path


def validate_durability_probe_entry(arguments: list[str]) -> dict[str, object]:
    values = dict(zip(arguments[::2], arguments[1::2], strict=True))
    phase = values["--durability-probe-phase"]
    invocation_path = Path(values["--invocation-preimage"])
    invocation = _closed_keys(
        strict_load(invocation_path, require_canonical=True),
        PROBE_INVOCATION_KEYS,
        "durability probe invocation",
    )
    constants = {
        "schema": "stage_f_durability_probe_invocation/v1",
        "phase": phase,
        "bootstrap_source_path": "stage_f_binding/locked_zipapp_bootstrap.py",
        "command_schema": (
            f"PYTHON_LOCKED_ZIPAPP_STAGE_F_BINDING_VALIDATOR_{phase}_V1"
        ),
        "command_line_construction": "BOUND_HOST_CPYTHON_SUBPROCESS_LIST2CMDLINE",
        "command_line_encoding": "UTF-16LE_WITHOUT_TERMINAL_NUL",
        "entrypoint_mode": "EXACT_GIT_BOOTSTRAP_C_OPTION_LOCKED_DETERMINISTIC_ZIPAPP",
        "isolated_mode": True,
        "network_access_permitted": False,
    }
    for field, expected in constants.items():
        if invocation[field] != expected or type(invocation[field]) is not type(expected):
            raise BindingRefusal(f"durability probe invocation differs: {field}")
    for field, kind in (
        ("binding_validator_identity", "stage_f_binding_validator/v1"),
        (
            "execution_environment_policy_identity",
            "stage_f_execution_environment_policy/v1",
        ),
        ("host_validation_runtime_identity", "stage_f_host_validation_runtime/v1"),
    ):
        _identity_shape(invocation[field], kind, field)
    assert_zero_science_counters(invocation["scientific_counters"])
    if (
        invocation["host_runtime_lock_acquisition_sha256"]
        != values["--host-runtime-lock-acquisition-sha256"]
        or invocation["validator_zipapp_byte_count"]
        != int(values["--validator-zipapp-byte-count"])
        or invocation["validator_zipapp_sha256"]
        != values["--validator-zipapp-sha256"]
    ):
        raise BindingRefusal("durability probe invocation artifact or lock projection differs")
    _verify_private_path_identity(
        invocation["validator_zipapp_path_identity"],
        values["--validator-zipapp"],
        "validator zipapp path",
    )
    _verify_private_path_identity(
        invocation["invocation_preimage_path_identity"],
        values["--invocation-preimage"],
        "invocation preimage path",
    )
    bootstrap = _strict_base64(
        invocation["bootstrap_source_utf8_base64"], "locked bootstrap source"
    )
    if (
        not 0 < len(bootstrap) <= 8192
        or invocation["bootstrap_source_byte_count"] != len(bootstrap)
    ):
        raise BindingRefusal("locked bootstrap source byte count differs")
    bootstrap_text = bootstrap.decode("utf-8", "strict")
    row = _closed_keys(invocation["bootstrap_git_row"], GIT_ROW_KEYS, "bootstrap Git row")
    if row != {
        "path": "stage_f_binding/locked_zipapp_bootstrap.py",
        "mode": "100644",
        "git_object": _blob_id(bootstrap),
        "byte_count": len(bootstrap),
        "raw_sha256": _sha256(bootstrap),
    }:
        raise BindingRefusal("locked bootstrap Git row does not reconstruct")
    command_raw = _strict_base64(invocation["command_line_base64"], "command line")
    observed_raw, parsed = _windows_command_line()
    expected_prefix = [parsed[0], "-I", "-S", "-B", "-c", bootstrap_text]
    if (
        command_raw != observed_raw
        or invocation["command_line_utf16_code_unit_count"] != len(command_raw) // 2
        or parsed[:6] != expected_prefix
        or parsed[6:] != arguments
        or subprocess.list2cmdline(parsed).encode("utf-16le", "strict") != command_raw
    ):
        raise BindingRefusal("durability probe command line does not reconstruct exactly")
    _verify_private_path_identity(
        invocation["executable_path_identity"], parsed[0], "host runtime executable path"
    )
    suffix = (
        invocation["restart_challenge_path_identity"],
        invocation["restart_challenge_sha256"],
        invocation["acknowledgement_path_identity"],
    )
    if phase == "POST_RESTART":
        if (
            values.get("--restart-challenge-sha256")
            != invocation["restart_challenge_sha256"]
        ):
            raise BindingRefusal("POST_RESTART challenge digest differs")
        _verify_private_path_identity(
            suffix[0], values["--restart-challenge"], "restart challenge path"
        )
        _verify_private_path_identity(
            suffix[2], values["--write-acknowledgement"], "acknowledgement path"
        )
    elif suffix != (None, None, None):
        raise BindingRefusal("non-POST durability invocation has a POST suffix")
    process = _probe_process_instance(invocation, command_raw, parsed[0])
    values["_executable"] = parsed[0]
    if phase == "ORCHESTRATOR":
        acquisition, acquisition_path, schema_path = (
            _load_external_host_runtime_acquisition(invocation_path, invocation)
        )
        values["_host_runtime_lock_acquisition_preimage"] = acquisition
        values["_host_runtime_lock_acquisition_path"] = os.fspath(acquisition_path)
        values["_authority_schema_path"] = os.fspath(schema_path)
    result: dict[str, object] = {
        "schema": "stage_f_durability_probe_entry_result/v1",
        "phase": phase,
        "process": process,
        "invocation_sha256": _sha256(canonical_bytes(invocation)),
        "acknowledgement_sha256": None,
        **ZERO_SCIENCE_COUNTERS,
    }
    if phase == "POST_RESTART":
        challenge_raw = Path(values["--restart-challenge"]).read_bytes()
        if _sha256(challenge_raw) != values["--restart-challenge-sha256"]:
            raise BindingRefusal("POST_RESTART challenge bytes differ")
        challenge = strict_loads(challenge_raw, require_canonical=True)
        if (
            type(challenge) is not dict
            or set(challenge)
            != {
                "schema",
                "orchestrator_process",
                "terminated_process",
                "published_final_sha256",
                "challenge_counter",
                "challenge_issued_utc",
            }
            or challenge["schema"] != "stage_f_durability_restart_challenge/v1"
        ):
            raise BindingRefusal("POST_RESTART challenge preimage is not closed")
    result.update(
        execute_durability_probe_phase(
            invocation,
            argument_values=values,
            process=process,
        )
    )
    return result


def _identity_shape(value: object, expected_kind: str, label: str) -> None:
    if (
        type(value) is not dict
        or set(value) != {"kind", "value", "sha256"}
        or value.get("kind") != expected_kind
        or not isinstance(value.get("value"), str)
        or SHA256_RE.fullmatch(value["value"]) is None
        or value.get("sha256") != value.get("value")
    ):
        raise BindingRefusal(f"{label} is not the exact digest-only identity shape")


def _source_bundle(raw: bytes) -> tuple[dict[str, object], dict[str, bytes]]:
    bundle = _closed_keys(strict_loads(raw), SOURCE_BUNDLE_KEYS, "source bundle")
    if canonical_bytes(bundle) != raw:
        raise BindingRefusal("source bundle bytes are not canonical")
    if bundle["schema"] != "stage_f_binding_validator_source_bundle/v1":
        raise BindingRefusal("source bundle schema differs")
    if (
        not isinstance(bundle["implementation_commit"], str)
        or GIT_OBJECT_RE.fullmatch(bundle["implementation_commit"]) is None
        or not isinstance(bundle["implementation_tree"], str)
        or GIT_OBJECT_RE.fullmatch(bundle["implementation_tree"]) is None
    ):
        raise BindingRefusal("source bundle Git coordinate differs")
    for field, kind in IDENTITY_KINDS.items():
        _identity_shape(bundle[field], kind, field)
    members = bundle["ordered_members"]
    if type(members) is not list or len(members) != 7 or bundle["member_count"] != 7:
        raise BindingRefusal("source bundle member count differs")
    blobs: dict[str, bytes] = {}
    for expected_path, untrusted in zip(SOURCE_PATHS, members, strict=True):
        member = _closed_keys(untrusted, MEMBER_KEYS, f"source member {expected_path}")
        if (
            member["path"] != expected_path
            or member["mode"] != "100644"
            or not isinstance(member["git_object"], str)
            or GIT_OBJECT_RE.fullmatch(member["git_object"]) is None
            or not isinstance(member["byte_count"], int)
            or isinstance(member["byte_count"], bool)
            or member["byte_count"] < 0
            or not isinstance(member["raw_sha256"], str)
            or SHA256_RE.fullmatch(member["raw_sha256"]) is None
        ):
            raise BindingRefusal(f"source member metadata differs: {expected_path}")
        content = _strict_base64(member["content_base64"], expected_path)
        if (
            len(content) != member["byte_count"]
            or _sha256(content) != member["raw_sha256"]
            or _blob_id(content) != member["git_object"]
            or expected_path in blobs
        ):
            raise BindingRefusal(f"source member bytes differ: {expected_path}")
        blobs[expected_path] = content
    return bundle, blobs


def _new_zipinfo(path: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(path, date_time=(1980, 1, 1, 0, 0, 0))
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
    return info


def _rebuild_zipapp(blobs: dict[str, bytes]) -> bytes:
    stream = io.BytesIO()
    with zipfile.ZipFile(
        stream,
        mode="w",
        compression=zipfile.ZIP_STORED,
        allowZip64=False,
        strict_timestamps=True,
    ) as archive:
        archive.comment = b""
        for archive_path, source_path in ZIPAPP_PATHS:
            archive.writestr(_new_zipinfo(archive_path), blobs[source_path])
    return stream.getvalue()


def _take_struct(raw: bytes, offset: int, format_string: str, label: str) -> tuple[tuple[int, ...], int]:
    size = struct.calcsize(format_string)
    end = offset + size
    if end > len(raw):
        raise BindingRefusal(f"truncated zipapp {label}")
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
            raise BindingRefusal(f"zipapp local header differs: {archive_path}")
        offset += name_size
        if raw[offset : offset + len(content)] != content:
            raise BindingRefusal(f"zipapp local member bytes differ: {archive_path}")
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
            raise BindingRefusal(f"zipapp central header differs: {archive_path}")
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
        raise BindingRefusal("zipapp EOCD or trailing bytes differ")


def _verify_zipapp(raw: bytes, blobs: dict[str, bytes]) -> None:
    if not raw.startswith(b"PK\x03\x04"):
        raise BindingRefusal("zipapp has a prefix or no local header")
    _verify_raw_zip_headers(raw, blobs)
    if raw != _rebuild_zipapp(blobs):
        raise BindingRefusal("zipapp does not rebuild byte-identically")
    try:
        archive = zipfile.ZipFile(io.BytesIO(raw), mode="r", allowZip64=False)
    except zipfile.BadZipFile as exc:
        raise BindingRefusal("zipapp is not a valid closed ZIP archive") from exc
    with archive:
        if archive.comment != b"" or tuple(archive.namelist()) != tuple(
            row[0] for row in ZIPAPP_PATHS
        ):
            raise BindingRefusal("zipapp member order or comment differs")
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
                raise BindingRefusal(f"zipapp member differs: {archive_path}")


def validate_source_artifacts(
    source_bundle: Path,
    zipapp: Path,
    *,
    validator: ClosedSchemaValidator,
    repository: VerifiedGitRepository,
    identity_preimages: dict[tuple[str, str], object],
    enforce_material_closure: bool = True,
    read_material=None,
) -> dict[str, object]:
    source_raw = (
        source_bundle.read_bytes()
        if read_material is None
        else read_material(source_bundle, "validator source bundle")
    )
    zipapp_raw = (
        zipapp.read_bytes()
        if read_material is None
        else read_material(zipapp, "validator zipapp")
    )
    bundle, blobs = _source_bundle(source_raw)
    validator.validate_definition("validator_source_bundle_artifact", bundle)
    _verify_zipapp(zipapp_raw, blobs)
    binding_preimage = _material_for_identity(
        identity_preimages,
        bundle["binding_implementation_identity"],
        "binding implementation",
    )
    validator.validate_definition("binding_implementation_preimage", binding_preimage)
    authority_preimage = _material_for_identity(
        identity_preimages,
        binding_preimage["integrated_authority_set_identity"],
        "integrated authority set",
    )
    validator.validate_definition("binding_authority_set_preimage", authority_preimage)
    environment_preimage = _material_for_identity(
        identity_preimages,
        bundle["execution_environment_policy_identity"],
        "execution environment policy",
    )
    validator.validate_definition(
        "execution_environment_policy_preimage", environment_preimage
    )
    runtime_preimage = _material_for_identity(
        identity_preimages,
        bundle["host_validation_runtime_identity"],
        "host validation runtime",
    )
    validator.validate_definition("host_validation_runtime_preimage", runtime_preimage)
    validator_identity, validator_preimage = _material_by_kind(
        identity_preimages,
        "stage_f_binding_validator/v1",
        "binding validator",
    )
    validator.validate_definition("binding_validator_preimage", validator_preimage)
    if (
        binding_preimage["accepted_base"] != ACCEPTED_BASE
        or authority_preimage["accepted_base"] != ACCEPTED_BASE
        or binding_preimage["integrated_authority_set_identity"]
        != {
            "kind": "stage_f_binding_authority_set/v1",
            "value": _sha256(canonical_bytes(authority_preimage)),
            "sha256": _sha256(canonical_bytes(authority_preimage)),
        }
        or binding_preimage["integrated_authority_commit"]
        != authority_preimage["integrated_authority_commit"]
        or binding_preimage["ordered_integrated_authority_file_rows"]
        != authority_preimage["ordered_local_authority_file_rows"]
    ):
        raise BindingRefusal("binding implementation and authority-set provenance differ")
    implementation_commit = binding_preimage["implementation_commit"]
    authority_commit = authority_preimage["integrated_authority_commit"]
    if (
        authority_commit != AUTHORITY_INTEGRATION_COMMIT
        or authority_preimage["integrated_authority_tree"]
        != AUTHORITY_INTEGRATION_TREE
        or binding_preimage["integrated_authority_commit"]
        != AUTHORITY_INTEGRATION_COMMIT
        or repository.tree_id(AUTHORITY_CANDIDATE_COMMIT)
        != AUTHORITY_INTEGRATION_TREE
        or repository.tree_id(AUTHORITY_INTEGRATION_COMMIT)
        != AUTHORITY_INTEGRATION_TREE
        or repository.tree_id(BINDING_FOUNDATION_BASE_COMMIT)
        != BINDING_FOUNDATION_BASE_TREE
        or binding_preimage["implementation_tree"]
        != repository.tree_id(implementation_commit)
        or authority_preimage["integrated_authority_tree"]
        != repository.tree_id(authority_commit)
        or not repository.is_ancestor(ACCEPTED_BASE["commit"], AUTHORITY_CANDIDATE_COMMIT)
        or not repository.is_ancestor(AUTHORITY_CANDIDATE_COMMIT, AUTHORITY_INTEGRATION_COMMIT)
        or not repository.is_ancestor(AUTHORITY_INTEGRATION_COMMIT, BINDING_FOUNDATION_BASE_COMMIT)
        or not repository.is_ancestor(BINDING_FOUNDATION_BASE_COMMIT, implementation_commit)
    ):
        raise BindingRefusal("binding implementation Git ancestry or tree differs")
    diff_rows = repository.diff_status(BINDING_FOUNDATION_BASE_COMMIT, implementation_commit)
    expected_status = {
        **{path: "M" for path in IMPLEMENTATION_PATHS[:2]},
        **{path: "A" for path in IMPLEMENTATION_PATHS[2:]},
    }
    observed_status: dict[str, str] = {}
    for status, path in diff_rows:
        if path in observed_status:
            raise BindingRefusal("binding implementation repeats a Git diff path")
        observed_status[path] = status
    if observed_status != expected_status:
        raise BindingRefusal("binding implementation exact 2M+12A Git scope differs")
    for expected_path, row in zip(
        AUTHORITY_PATHS,
        authority_preimage["ordered_local_authority_file_rows"],
        strict=True,
    ):
        if row != repository.row(
            authority_commit, expected_path, allowed_modes=frozenset({"100644"})
        ) or row != repository.row(
            implementation_commit, expected_path, allowed_modes=frozenset({"100644"})
        ):
            raise BindingRefusal(f"authority Git row differs: {expected_path}")
    for expected_path, row in zip(
        IMPLEMENTATION_PATHS,
        binding_preimage["ordered_implementation_file_rows"],
        strict=True,
    ):
        if row != repository.row(
            implementation_commit, expected_path, allowed_modes=frozenset({"100644"})
        ):
            raise BindingRefusal(f"implementation Git row differs: {expected_path}")
    if (
        bundle["implementation_commit"] != implementation_commit
        or bundle["implementation_tree"] != binding_preimage["implementation_tree"]
        or validator_preimage["binding_implementation_identity"]
        != bundle["binding_implementation_identity"]
        or validator_preimage["implementation_commit"] != implementation_commit
        or validator_preimage["implementation_tree"] != bundle["implementation_tree"]
        or validator_preimage["execution_environment_policy_identity"]
        != bundle["execution_environment_policy_identity"]
        or validator_preimage["host_validation_runtime_identity"]
        != bundle["host_validation_runtime_identity"]
    ):
        raise BindingRefusal("source bundle and validator provenance differ")
    implementation_rows = {
        row["path"]: row for row in binding_preimage["ordered_implementation_file_rows"]
    }
    validator_rows = validator_preimage["ordered_validator_source_file_rows"]
    for path, row, member in zip(
        VALIDATOR_SOURCE_PATHS, validator_rows, bundle["ordered_members"], strict=True
    ):
        member_row = {key: member[key] for key in GIT_ROW_KEYS}
        if (
            row != implementation_rows[path]
            or row != repository.row(
                implementation_commit, path, allowed_modes=frozenset({"100644"})
            )
            or member_row != row
            or blobs[path] != repository.blob(row["git_object"])
        ):
            raise BindingRefusal(f"validator source provenance differs: {path}")
    source_digest = _sha256(source_raw)
    executable = validator_preimage["executable_zipapp_manifest"]
    if (
        validator_preimage["built_artifact_byte_count"] != len(source_raw)
        or validator_preimage["built_artifact_sha256"] != source_digest
        or executable["source_bundle_sha256"] != source_digest
        or executable["artifact_byte_count"] != len(zipapp_raw)
        or executable["artifact_sha256"] != _sha256(zipapp_raw)
        or executable["host_validation_runtime_identity"]
        != bundle["host_validation_runtime_identity"]
    ):
        raise BindingRefusal("validator artifact byte projection differs")
    for member, (archive_path, source_path), source_row in zip(
        executable["ordered_members"],
        VALIDATOR_ZIPAPP_PATHS,
        (implementation_rows[path] for path in (row[1] for row in VALIDATOR_ZIPAPP_PATHS)),
        strict=True,
    ):
        if (
            member["archive_path"] != archive_path
            or member["source_path"] != source_path
            or any(
                member[field] != source_row[field]
                for field in ("mode", "git_object", "byte_count", "raw_sha256")
            )
        ):
            raise BindingRefusal(f"validator executable member provenance differs: {archive_path}")
    if enforce_material_closure:
        repository.assert_material_closure(
            (
                ACCEPTED_BASE["commit"],
                AUTHORITY_CANDIDATE_COMMIT,
                AUTHORITY_INTEGRATION_COMMIT,
                BINDING_FOUNDATION_BASE_COMMIT,
                implementation_commit,
            )
        )
    return {
        "schema": "stage_f_binding_foundation_artifact_validation/v1",
        "validator_identity": validator_identity,
        "binding_implementation_identity": bundle["binding_implementation_identity"],
        "implementation_commit": bundle["implementation_commit"],
        "implementation_tree": bundle["implementation_tree"],
        "source_bundle_byte_count": len(source_raw),
        "source_bundle_sha256": _sha256(source_raw),
        "zipapp_byte_count": len(zipapp_raw),
        "zipapp_sha256": _sha256(zipapp_raw),
        **ZERO_SCIENCE_COUNTERS,
    }


class _LazyIdentityMaterials(Mapping[tuple[str, str], object]):
    def __init__(
        self,
        specifications: Mapping[
            tuple[str, str], tuple[Path, str, Mapping[str, object], int]
        ],
        read_material,
    ) -> None:
        self._specifications = dict(specifications)
        self._read_material = read_material
        self._loaded: dict[tuple[str, str], object] = {}

    def __iter__(self):
        return iter(self._specifications)

    def __len__(self) -> int:
        return len(self._specifications)

    def __getitem__(self, key: tuple[str, str]) -> object:
        if key in self._loaded:
            return self._loaded[key]
        try:
            path, encoding, identity, ordinal = self._specifications[key]
        except KeyError:
            raise KeyError(key) from None
        raw = (
            path.read_bytes()
            if self._read_material is None
            else self._read_material(path, f"identity material {ordinal}")
        )
        if encoding == "CANONICAL_JSON":
            material = strict_loads(raw, require_canonical=True)
        else:
            material = raw
        verify_identity(identity, material, kind=key[0])
        self._loaded[key] = material
        return material

    def assert_complete_consumption(self) -> None:
        if set(self._loaded) != set(self._specifications):
            extras = sorted(set(self._specifications) - set(self._loaded))
            raise BindingRefusal(
                f"identity material index has an unconsumed extra identity: {extras[0]}"
            )


def _load_identity_materials(
    index_path: Path, read_material=None
) -> _LazyIdentityMaterials:
    index_raw = (
        index_path.read_bytes()
        if read_material is None
        else read_material(index_path, "identity material index")
    )
    index = _closed_keys(
        strict_loads(index_raw, require_canonical=True),
        IDENTITY_MATERIAL_INDEX_KEYS,
        "identity material index",
    )
    if index["schema"] != "stage_f_binding_identity_material_index/v1":
        raise BindingRefusal("identity material index schema differs")
    entries = index["entries"]
    if (
        type(entries) is not list
        or type(index["entry_count"]) is not int
        or isinstance(index["entry_count"], bool)
        or index["entry_count"] != len(entries)
        or not entries
    ):
        raise BindingRefusal("identity material index count differs")
    specifications: dict[
        tuple[str, str], tuple[Path, str, Mapping[str, object], int]
    ] = {}
    for ordinal, untrusted in enumerate(entries):
        entry = _closed_keys(
            untrusted,
            IDENTITY_MATERIAL_ENTRY_KEYS,
            f"identity material entry {ordinal}",
        )
        identity = entry["identity"]
        if type(identity) is not dict or set(identity) != {"kind", "value", "sha256"}:
            raise BindingRefusal(f"identity material entry {ordinal} has a malformed identity")
        kind = identity.get("kind")
        value = identity.get("value")
        if (
            not isinstance(kind, str)
            or not kind
            or not isinstance(value, str)
            or SHA256_RE.fullmatch(value) is None
            or identity.get("sha256") != value
        ):
            raise BindingRefusal(f"identity material entry {ordinal} has an invalid identity")
        if not isinstance(entry["path"], str):
            raise BindingRefusal(f"identity material entry {ordinal} path is not a string")
        material_path = Path(entry["path"])
        if not material_path.is_absolute():
            raise BindingRefusal(f"identity material entry {ordinal} path is not absolute")
        if entry["encoding"] not in {"CANONICAL_JSON", "RAW_BYTES"}:
            raise BindingRefusal(f"identity material entry {ordinal} encoding differs")
        key = (kind, value)
        if key in specifications:
            raise BindingRefusal("identity material index has a duplicate identity")
        specifications[key] = (material_path, entry["encoding"], identity, ordinal)
    return _LazyIdentityMaterials(specifications, read_material)


def _load_verified_git_repository(
    index_path: Path, read_material=None
) -> VerifiedGitRepository:
    if read_material is None:
        index_path = index_path.resolve(strict=True)
    index_stat = index_path.stat(follow_symlinks=False)
    if (
        not index_path.is_file()
        or getattr(index_stat, "st_file_attributes", 0) & 0x400
        or index_stat.st_nlink != 1
    ):
        raise BindingRefusal("verified Git object material index is reparse or linked")
    index_raw = (
        index_path.read_bytes()
        if read_material is None
        else read_material(index_path, "verified Git object material index")
    )
    index = _closed_keys(
        strict_loads(index_raw, require_canonical=True),
        GIT_OBJECT_MATERIAL_INDEX_KEYS,
        "verified Git object material index",
    )
    entries = index["entries"]
    if (
        index["schema"] != "stage_f_verified_git_object_material_index/v1"
        or type(entries) is not list
        or type(index["entry_count"]) is not int
        or isinstance(index["entry_count"], bool)
        or index["entry_count"] != len(entries)
        or not entries
    ):
        raise BindingRefusal("verified Git object material index differs")
    objects: dict[tuple[str, str], object] = {}
    order: list[tuple[bytes, bytes]] = []
    object_directory = index_path.parent / "verified-git-objects"
    try:
        object_directory_stat = object_directory.stat(follow_symlinks=False)
    except OSError as exc:
        raise BindingRefusal(
            "verified Git object material directory is unavailable"
        ) from exc
    if not stat_module.S_ISDIR(object_directory_stat.st_mode) or (
        getattr(object_directory_stat, "st_file_attributes", 0) & 0x400
    ):
        raise BindingRefusal("verified Git object material directory is absent or reparse")
    try:
        directory_entries = list(object_directory.iterdir())
    except OSError as exc:
        raise BindingRefusal("verified Git object material directory enumeration failed") from exc
    actual_names: set[str] = set()
    for child in directory_entries:
        try:
            child_stat = child.stat(follow_symlinks=False)
        except OSError as exc:
            raise BindingRefusal(
                "verified Git object material directory has an unreadable entry"
            ) from exc
        if (
            child.name in actual_names
            or getattr(child_stat, "st_file_attributes", 0) & 0x400
            or not stat_module.S_ISREG(child_stat.st_mode)
            or child_stat.st_nlink != 1
        ):
            raise BindingRefusal(
                "verified Git object material directory has a repeated, reparse, "
                "linked, directory, or special entry"
            )
        actual_names.add(child.name)
    expected_names: set[str] = set()
    for ordinal, untrusted in enumerate(entries):
        entry = _closed_keys(
            untrusted,
            GIT_OBJECT_MATERIAL_ENTRY_KEYS,
            f"verified Git object material entry {ordinal}",
        )
        object_type = entry["object_type"]
        object_id = entry["object_id"]
        path_value = entry["path"]
        if (
            object_type not in {"commit", "tree", "blob"}
            or not isinstance(object_id, str)
            or GIT_OBJECT_RE.fullmatch(object_id) is None
            or not isinstance(path_value, str)
            or type(entry["byte_count"]) is not int
            or entry["byte_count"] < 0
            or not isinstance(entry["raw_sha256"], str)
            or SHA256_RE.fullmatch(entry["raw_sha256"]) is None
        ):
            raise BindingRefusal("verified Git object material entry fields differ")
        path = Path(path_value)
        expected_name = f"{object_type}-{object_id}.raw"
        expected_path = object_directory / expected_name
        if (
            not path.is_absolute()
            or path != expected_path
        ):
            raise BindingRefusal("verified Git object material path/name differs")
        try:
            stat = path.stat(follow_symlinks=False)
        except OSError as exc:
            raise BindingRefusal("verified Git object material path is unavailable") from exc
        if (
            getattr(stat, "st_file_attributes", 0) & 0x400
            or stat.st_nlink != 1
            or not stat_module.S_ISREG(stat.st_mode)
            or expected_name in expected_names
        ):
            raise BindingRefusal("verified Git object material is reparse, linked, or repeated")
        expected_names.add(expected_name)
        key = (object_type, object_id)
        if key in objects:
            raise BindingRefusal("verified Git object material repeats an object")

        def load(
            material_path: Path = path,
            expected_byte_count: int = entry["byte_count"],
            expected_raw_sha256: str = entry["raw_sha256"],
            material_label: str = f"verified Git object material {ordinal}",
        ) -> bytes:
            raw = (
                material_path.read_bytes()
                if read_material is None
                else read_material(material_path, material_label)
            )
            if (
                expected_byte_count != len(raw)
                or expected_raw_sha256 != _sha256(raw)
            ):
                raise BindingRefusal("verified Git object material bytes differ")
            return raw

        objects[key] = load
        order.append((object_type.encode("ascii"), object_id.encode("ascii")))
    if order != sorted(order):
        raise BindingRefusal("verified Git object material order differs")
    if actual_names != expected_names:
        raise BindingRefusal("verified Git object material directory closure differs")
    return VerifiedGitRepository(objects)


def _load_referenced_bindings(
    index_path: Path, read_material=None
) -> dict[str, dict[str, object]]:
    index_raw = (
        index_path.read_bytes()
        if read_material is None
        else read_material(index_path, "referenced binding index")
    )
    index = _closed_keys(
        strict_loads(index_raw, require_canonical=True),
        REFERENCED_BINDING_INDEX_KEYS,
        "referenced binding index",
    )
    if index["schema"] != "stage_f_referenced_campaign_binding_material_index/v1":
        raise BindingRefusal("referenced binding index schema differs")
    entries = index["entries"]
    if (
        type(entries) is not list
        or index["entry_count"] != len(entries)
        or len(entries) != len(CAMPAIGN_ORDER)
    ):
        raise BindingRefusal("referenced binding index count differs")
    result: dict[str, dict[str, object]] = {}
    for route_id, untrusted in zip(CAMPAIGN_ORDER, entries, strict=True):
        entry = _closed_keys(
            untrusted,
            REFERENCED_BINDING_ENTRY_KEYS,
            f"referenced binding entry {route_id}",
        )
        if entry["route_id"] != route_id:
            raise BindingRefusal("referenced binding index route order differs")
        if not isinstance(entry["record_path"], str) or not isinstance(entry["file_path"], str):
            raise BindingRefusal(f"referenced binding paths are not strings: {route_id}")
        record_path = Path(entry["record_path"])
        file_path = Path(entry["file_path"])
        if not record_path.is_absolute() or not file_path.is_absolute():
            raise BindingRefusal(f"referenced binding paths are not absolute: {route_id}")
        record_raw = (
            record_path.read_bytes()
            if read_material is None
            else read_material(record_path, f"referenced binding record {route_id}")
        )
        file_raw = (
            file_path.read_bytes()
            if read_material is None
            else read_material(file_path, f"referenced binding file {route_id}")
        )
        record = strict_loads(record_raw, require_canonical=True)
        file_record = strict_loads(file_raw, require_canonical=True)
        if record_raw != file_raw or record != file_record:
            raise BindingRefusal(
                f"referenced binding record/file bytes differ: {route_id}"
            )
        result[route_id] = {"record": record, "file_bytes": file_raw}
    return result


def _load_durability_receipts(
    index_path: Path, read_material=None
) -> list[dict[str, object]]:
    index_raw = (
        index_path.read_bytes()
        if read_material is None
        else read_material(index_path, "durability receipt index")
    )
    index = _closed_keys(
        strict_loads(index_raw, require_canonical=True),
        DURABILITY_RECEIPT_INDEX_KEYS,
        "durability receipt index",
    )
    if index["schema"] != "stage_f_durability_receipt_material_index/v1":
        raise BindingRefusal("durability receipt index schema differs")
    entries = index["entries"]
    if (
        type(entries) is not list
        or type(index["entry_count"]) is not int
        or isinstance(index["entry_count"], bool)
        or index["entry_count"] != len(entries)
        or not entries
    ):
        raise BindingRefusal("durability receipt index count differs")
    receipts: list[dict[str, object]] = []
    identities: set[tuple[str, str]] = set()
    for ordinal, untrusted in enumerate(entries):
        entry = _closed_keys(
            untrusted,
            DURABILITY_RECEIPT_ENTRY_KEYS,
            f"durability receipt entry {ordinal}",
        )
        _identity_shape(
            entry["identity"],
            "stage_f_durability_probe_receipt/v1",
            f"durability receipt identity {ordinal}",
        )
        if not isinstance(entry["path"], str):
            raise BindingRefusal(f"durability receipt path {ordinal} is not a string")
        path = Path(entry["path"])
        if not path.is_absolute():
            raise BindingRefusal(f"durability receipt path {ordinal} is not absolute")
        receipt_raw = (
            path.read_bytes()
            if read_material is None
            else read_material(path, f"durability receipt {ordinal}")
        )
        receipt = strict_loads(receipt_raw, require_canonical=True)
        verify_identity(
            entry["identity"],
            {key: value for key, value in receipt.items() if key != "receipt_sha256"},
            kind="stage_f_durability_probe_receipt/v1",
        )
        key = (entry["identity"]["kind"], entry["identity"]["value"])
        if key in identities:
            raise BindingRefusal("durability receipt index repeats an identity")
        identities.add(key)
        receipts.append(receipt)
    return receipts


def _validate_record_chain_locked(
    args: argparse.Namespace,
    validator: ClosedSchemaValidator,
    private_manifest: dict[str, object],
    locks: _RetainedMaterialLocks,
) -> dict[str, object]:
    live_validation_started_utc = datetime.now(timezone.utc)
    if args.command not in {"readiness-chain", "record-chain"}:
        raise BindingRefusal("record-chain validation purpose is not closed")
    launch_gate = args.command == "record-chain"
    authorization_arguments = (
        args.preaudit_readiness,
        args.independent_audit,
        args.pass_readiness,
        args.packet,
        args.user_receipt,
        args.authorization,
        args.retained_statement,
    )
    if launch_gate and any(value is None for value in authorization_arguments):
        raise BindingRefusal(
            "scientific-launch record-chain gate lacks the complete authorization chain"
        )
    locked_manifest = strict_loads(
        locks.read(args.private_manifest, "private host manifest"),
        require_canonical=True,
    )
    if locked_manifest != private_manifest:
        raise BindingRefusal("private host manifest changed during trust-anchor locking")
    public_binding = strict_loads(
        locks.read(args.public_binding, "public host binding"), require_canonical=True
    )
    bundle = strict_loads(
        locks.read(args.bundle, "local binding bundle"), require_canonical=True
    )
    capacity = strict_loads(
        locks.read(args.capacity_snapshot, "current capacity snapshot"),
        require_canonical=True,
    )
    capacity_history = [
        strict_loads(
            locks.read(path, f"previous capacity snapshot {ordinal}"),
            require_canonical=True,
        )
        for ordinal, path in enumerate(args.previous_capacity_snapshot)
    ]
    capacity_history.append(capacity)
    power = strict_loads(
        locks.read(args.power_snapshot, "power snapshot"), require_canonical=True
    )
    validation_receipt = strict_loads(
        locks.read(args.validation_receipt, "binding validation receipt"),
        require_canonical=True,
    )
    identity_preimages = _load_identity_materials(
        args.identity_material_index, locks.read
    )
    repository = _load_verified_git_repository(
        args.git_object_material_index, locks.read
    )
    referenced_bindings = _load_referenced_bindings(
        args.referenced_binding_index, locks.read
    )
    private_durability_bundle = strict_loads(
        locks.read(args.private_durability_bundle, "private durability bundle"),
        require_canonical=True,
    )
    durability_receipts = _load_durability_receipts(
        args.durability_receipt_index, locks.read
    )
    executing_zipapp = Path(_BOOTSTRAP_LOCK_CONTEXT[2])
    for ordinal, receipt in enumerate(durability_receipts):
        validator.validate_definition("durability_probe_receipt", receipt)
        invocation = receipt["orchestrator_probe_invocation_preimage"]
        _require_executing_artifact(
            executing_zipapp,
            observed_byte_count=invocation["validator_zipapp_byte_count"],
            observed_sha256=invocation["validator_zipapp_sha256"],
        )
        _verify_private_path_identity(
            invocation["validator_zipapp_path_identity"],
            _BOOTSTRAP_LOCK_CONTEXT[2],
            f"record-chain durability validator zipapp {ordinal}",
        )
    source_artifact_validation = validate_source_artifacts(
        args.source_bundle,
        args.validator_zipapp,
        validator=validator,
        repository=repository,
        identity_preimages=identity_preimages,
        enforce_material_closure=False,
        read_material=locks.read,
    )
    validate_private_host_manifest(validator, private_manifest)
    _verify_private_root_outside_git(private_manifest, args.source)
    validate_public_host_binding(
        validator, public_binding, private_manifest=private_manifest
    )
    validate_local_binding_bundle(
        validator,
        bundle,
        public_host_binding=public_binding,
        referenced_bindings=referenced_bindings,
    )
    validate_immutable_bundle_chain(
        validator,
        bundle,
        public_host_binding=public_binding,
        identity_preimages=identity_preimages,
        referenced_bindings=referenced_bindings,
        repository=repository,
    )
    if source_artifact_validation["validator_identity"] != bundle["validator_identity"]:
        raise BindingRefusal("validated source artifact belongs to another validator")
    validate_binding_validation_receipt(
        validator,
        validation_receipt,
        bundle=bundle,
        private_manifest=private_manifest,
        public_host_binding=public_binding,
        capacity_snapshot=capacity,
        capacity_snapshot_history=capacity_history,
        power_snapshot=power,
        private_durability_bundle=private_durability_bundle,
        durability_receipts=durability_receipts,
        identity_preimages=identity_preimages,
    )
    temporary_role_root = private_manifest["filesystem"]["private_directories"][
        "temporary"
    ]
    _verify_complete_challenge_history(
        validator,
        private_manifest,
        durability_receipts,
        identity_preimages,
        lambda path, label: locks.read_scoped(path, temporary_role_root, label),
    )
    result: dict[str, object] = {
        "schema": (
            "stage_f_scientific_launch_authorization_gate/v1"
            if launch_gate
            else "stage_f_binding_readiness_chain_validation/v1"
        ),
        "disposition": (
            "AUTHORIZED_FOR_EXTERNAL_SCIENTIFIC_LAUNCH"
            if launch_gate
            else "READINESS_CHAIN_VALIDATED_NOT_SCIENTIFIC_AUTHORIZATION"
        ),
        **ZERO_SCIENCE_COUNTERS,
    }
    preaudit = (
        strict_loads(
            locks.read(args.preaudit_readiness, "pre-audit readiness"),
            require_canonical=True,
        )
        if args.preaudit_readiness
        else None
    )
    audit = (
        strict_loads(
            locks.read(args.independent_audit, "independent audit receipt"),
            require_canonical=True,
        )
        if args.independent_audit
        else None
    )
    passed = (
        strict_loads(
            locks.read(args.pass_readiness, "PASS readiness"),
            require_canonical=True,
        )
        if args.pass_readiness
        else None
    )
    packet = (
        strict_loads(
            locks.read(args.packet, "sealed campaign packet"),
            require_canonical=True,
        )
        if args.packet
        else None
    )
    user_receipt = (
        strict_loads(
            locks.read(args.user_receipt, "post-packet user receipt"),
            require_canonical=True,
        )
        if args.user_receipt
        else None
    )
    authorization = (
        strict_loads(
            locks.read(args.authorization, "campaign authorization"),
            require_canonical=True,
        )
        if args.authorization
        else None
    )
    statement = (
        locks.read(args.retained_statement, "retained user authorization statement")
        if args.retained_statement
        else None
    )
    if preaudit is not None:
        validate_readiness_record(
            validator,
            preaudit,
            bundle=bundle,
            validation_receipt=validation_receipt,
            capacity_snapshot=capacity,
            power_snapshot=power,
        )
    if audit is not None:
        if preaudit is None:
            raise BindingRefusal("audit requires pre-audit readiness")
        validate_independent_audit_receipt(
            validator,
            audit,
            preaudit_readiness=preaudit,
            bundle=bundle,
            validation_receipt=validation_receipt,
            private_manifest=private_manifest,
            public_host_binding=public_binding,
            capacity_snapshot=capacity,
            power_snapshot=power,
        )
    if passed is not None:
        if audit is None:
            raise BindingRefusal("PASS readiness requires independent audit")
        validate_readiness_record(
            validator,
            passed,
            bundle=bundle,
            validation_receipt=validation_receipt,
            capacity_snapshot=capacity,
            power_snapshot=power,
            independent_audit=audit,
        )
    if packet is not None:
        if passed is None or audit is None:
            raise BindingRefusal("sealed packet requires PASS readiness and audit")
        validate_sealed_campaign_packet(
            validator,
            packet,
            pass_readiness=passed,
            audit=audit,
            bundle=bundle,
            validation_receipt=validation_receipt,
            private_manifest=private_manifest,
            public_host_binding=public_binding,
            capacity_snapshot=capacity,
            power_snapshot=power,
        )
    if user_receipt is not None:
        if packet is None or statement is None:
            raise BindingRefusal("user receipt requires packet and retained statement")
        validate_post_packet_user_authorization_receipt(
            validator,
            user_receipt,
            packet=packet,
            retained_statement_bytes=statement,
        )
    if authorization is not None:
        if any(
            value is None
            for value in (
                packet,
                user_receipt,
                passed,
                audit,
                preaudit,
                statement,
            )
        ):
            raise BindingRefusal("authorization requires one complete audited chain")
        validate_campaign_authorization(
            validator,
            authorization,
            packet=packet,
            user_receipt=user_receipt,
            pass_readiness=passed,
            audit=audit,
            preaudit_readiness=preaudit,
            bundle=bundle,
            validation_receipt=validation_receipt,
            private_manifest=private_manifest,
            public_host_binding=public_binding,
            capacity_snapshot=capacity,
            capacity_snapshot_history=capacity_history,
            power_snapshot=power,
            retained_statement_bytes=statement,
            identity_preimages=identity_preimages,
            referenced_bindings=referenced_bindings,
            private_durability_bundle=private_durability_bundle,
            durability_receipts=durability_receipts,
            repository=repository,
        )
    if launch_gate and authorization is None:
        raise BindingRefusal(
            "scientific-launch record-chain gate did not validate authorization"
        )
    for ordinal, snapshot in enumerate(capacity_history):
        _require_not_future_utc(
            snapshot["snapshot_started_utc"],
            not_after=live_validation_started_utc,
            label=f"capacity snapshot {ordinal} start",
        )
        _require_not_future_utc(
            snapshot["snapshot_completed_utc"],
            not_after=live_validation_started_utc,
            label=f"capacity snapshot {ordinal} completion",
        )
    _require_not_future_utc(
        power["facts"]["snapshot_utc"],
        not_after=live_validation_started_utc,
        label="power observation",
    )
    _require_not_future_utc(
        validation_receipt["validated_utc"],
        not_after=live_validation_started_utc,
        label="binding validation",
    )
    for ordinal, receipt in enumerate(durability_receipts):
        _require_not_future_utc(
            receipt["probe_completed_utc"],
            not_after=live_validation_started_utc,
            label=f"durability receipt {ordinal} completion",
        )
    for record, field, label in (
        (preaudit, "readiness_utc", "pre-audit readiness"),
        (audit, "audit_completed_utc", "independent audit completion"),
        (passed, "readiness_utc", "PASS readiness"),
        (packet, "packet_created_utc", "packet creation"),
        (user_receipt, "statement_received_utc", "user statement receipt"),
        (authorization, "authorization_utc", "campaign authorization"),
    ):
        if record is not None:
            _require_not_future_utc(
                record[field],
                not_after=live_validation_started_utc,
                label=label,
            )
    identity_preimages.assert_complete_consumption()
    retained_root = (
        private_manifest["filesystem"]["private_directories"]["independent_audit"]
        + "\\retained-evidence"
    )
    stage_f_root = private_manifest["filesystem"]["private_directories"][
        "stage_f_root"
    ].rstrip("\\")
    inventory_paths = {
        row["relative_path"] for row in capacity["inventory_entries"]
    }

    def retained_relative(path: Path, label: str) -> str:
        path_text = os.fspath(path)
        if not path_text.startswith(stage_f_root + "\\"):
            raise BindingRefusal(f"{label} is outside the exact Stage F root")
        relative = path_text[len(stage_f_root) + 1 :].replace("\\", "/")
        if (
            not relative
            or unicodedata.normalize("NFC", relative) != relative
            or relative.rpartition("/")[0]
            != "independent-audit/retained-evidence"
        ):
            raise BindingRefusal(
                f"{label} is not a direct retained-evidence publication"
            )
        return relative

    mandatory_postwrite_roles: list[tuple[Path, str]] = [
        (args.capacity_snapshot, "current capacity snapshot"),
        (args.validation_receipt, "binding validation receipt"),
    ]
    mandatory_postwrite_roles.extend(
        (path, label)
        for path, label in (
            (args.preaudit_readiness, "pre-audit readiness"),
            (args.independent_audit, "independent audit receipt"),
            (args.pass_readiness, "PASS readiness"),
            (args.packet, "sealed campaign packet"),
            (args.user_receipt, "post-packet user receipt"),
            (args.authorization, "campaign authorization"),
            (args.retained_statement, "retained user authorization statement"),
        )
        if path is not None
    )
    capacity_relative = retained_relative(
        args.capacity_snapshot, "current capacity snapshot"
    )
    validation_relative = retained_relative(
        args.validation_receipt, "binding validation receipt"
    )
    if (
        capacity_relative in inventory_paths
        or validation_relative in inventory_paths
    ):
        raise BindingRefusal(
            "capacity or capacity-identifying validation receipt is self-inventoried"
        )
    initial_capacity = private_manifest["initial_storage_capacity_snapshot_identity"]
    current_is_initial = (
        initial_capacity["kind"] == capacity["schema"]
        and initial_capacity["value"] == capacity["snapshot_sha256"]
        and initial_capacity["sha256"] == capacity["snapshot_sha256"]
    )
    if current_is_initial:
        mandatory_postwrite_roles.extend(
            (
                (args.private_manifest, "private host manifest"),
                (args.public_binding, "public host binding"),
                (args.bundle, "local binding bundle"),
                (args.power_snapshot, "power snapshot"),
            )
        )
    else:
        for path, label in (
            (args.private_manifest, "private host manifest"),
            (args.public_binding, "public host binding"),
            (args.bundle, "local binding bundle"),
        ):
            if retained_relative(path, label) not in inventory_paths:
                raise BindingRefusal(
                    "non-initial capacity snapshot omits a stable host-chain record"
                )
        power_relative = retained_relative(args.power_snapshot, "power snapshot")
        if power_relative not in inventory_paths:
            capacity_completed = datetime.fromisoformat(
                capacity["snapshot_completed_utc"][:-1] + "+00:00"
            )
            power_observed = datetime.fromisoformat(
                power["facts"]["snapshot_utc"][:-1] + "+00:00"
            )
            if power_observed <= capacity_completed:
                raise BindingRefusal(
                    "pre-capacity power snapshot is absent from the non-initial inventory"
                )
            mandatory_postwrite_roles.append(
                (args.power_snapshot, "power snapshot")
            )
    causal_postwrite_paths = {
        retained_relative(path, label)
        for path, label in mandatory_postwrite_roles
    }
    if causal_postwrite_paths & inventory_paths:
        raise BindingRefusal(
            "capacity-identifying or causally later record is self-inventoried"
        )
    validate_live_storage_inventory(
        stage_f_root,
        capacity["inventory_entries"],
        capacity_snapshot=capacity,
        capacity_snapshot_path=args.capacity_snapshot,
        retained_evidence_root=retained_root,
        retained_file_observations=locks.retained_file_observations(),
        permitted_postwrite_paths=tuple(
            sorted(causal_postwrite_paths, key=lambda value: value.encode("utf-8"))
        ),
        final_checks=lambda: validate_live_volume_capacity(
            private_manifest["filesystem"], capacity
        ),
    )
    assert_zero_science_counters(
        {name: result.get(name) for name in ZERO_SCIENCE_COUNTERS}
    )
    return result


def validate_record_chain(args: argparse.Namespace) -> dict[str, object]:
    if _BOOTSTRAP_LOCK_CONTEXT is None:
        raise BindingRefusal("record-chain validation requires the locked validator")
    manifest_path_text = os.fspath(args.private_manifest)
    marker = "\\independent-audit\\retained-evidence\\"
    marker_offset = manifest_path_text.casefold().find(marker.casefold())
    if (
        not manifest_path_text.startswith("\\\\?\\Volume{")
        or marker_offset <= 0
        or manifest_path_text.casefold().find(
            marker.casefold(), marker_offset + len(marker)
        )
        >= 0
        or not manifest_path_text[marker_offset + len(marker) :]
        or ".." in Path(manifest_path_text).parts
        or ":" in manifest_path_text[marker_offset:]
    ):
        raise BindingRefusal(
            "private host manifest is not an exact retained-evidence volume-GUID path"
        )
    retained_root = manifest_path_text[: marker_offset + len(marker) - 1]
    stage_f_root = manifest_path_text[:marker_offset]
    watch = _windows_start_recursive_tree_watch(Path(stage_f_root))
    failure: BaseException | None = None
    result: dict[str, object] | None = None
    try:
        with _RetainedMaterialLocks(retained_root) as locks:
            manifest_raw = locks.read(
                args.private_manifest, "private host manifest trust anchor"
            )
            private_manifest = strict_loads(manifest_raw, require_canonical=True)

            source = args.source.resolve(strict=True)
            source_schema = (source / AUTHORITY_SCHEMA_PATH).resolve(strict=True)
            try:
                supplied_schema = args.schema.resolve(strict=True)
            except OSError as exc:
                raise BindingRefusal("authority schema path is unavailable") from exc
            if supplied_schema == source_schema:
                source_role_root = _normalized_volume_guid_path(
                    source, "record-chain committed source root"
                )
                source_schema_private = Path(
                    _normalized_volume_guid_path(
                        source_schema, "record-chain committed authority schema"
                    )
                )
                schema = _load_authority_schema(
                    source_schema_private,
                    locks.read_scoped(
                        source_schema_private,
                        source_role_root,
                        "committed authority schema",
                    ),
                )
            else:
                schema = _load_authority_schema(
                    args.schema,
                    locks.read(
                        args.schema, "retained materialized authority schema"
                    ),
                )
            validator = ClosedSchemaValidator(schema)
            validate_private_host_manifest(validator, private_manifest)
            expected_retained_root = (
                private_manifest["filesystem"]["private_directories"][
                    "independent_audit"
                ]
                + "\\retained-evidence"
            )
            if (
                stage_f_root
                != private_manifest["filesystem"]["private_directories"]["stage_f_root"]
                or retained_root != expected_retained_root
            ):
                raise BindingRefusal(
                    "private host manifest path is outside its own exact Stage F role"
                )
            locks.bind_selected_volume_serial(
                private_manifest["filesystem"]["ntfs_volume_data"][
                    "volume_serial_number"
                ]
            )
            _verify_private_root_outside_git(private_manifest, args.source)
            executing_zipapp = Path(_BOOTSTRAP_LOCK_CONTEXT[2])
            if args.validator_zipapp != executing_zipapp:
                raise BindingRefusal(
                    "record-chain validator path differs from the executing locked zipapp"
                )
            result = _validate_record_chain_locked(
                args, validator, private_manifest, locks
            )
    except BaseException as exc:
        failure = exc
    try:
        _windows_finish_recursive_tree_watch(watch, require_quiet=failure is None)
    except BaseException as exc:
        if failure is None:
            failure = exc
    if failure is not None:
        raise failure
    if result is None:
        raise BindingRefusal("record-chain validation produced no result")
    return result


def validate_standalone_durability_receipt(
    args: argparse.Namespace,
) -> dict[str, object]:
    """Validate one receipt under the same scope-before-read and held-lock epoch."""

    manifest_path_text = os.fspath(args.private_manifest)
    marker = "\\independent-audit\\retained-evidence\\"
    marker_offset = manifest_path_text.casefold().find(marker.casefold())
    if (
        not manifest_path_text.startswith("\\\\?\\Volume{")
        or marker_offset <= 0
        or manifest_path_text.casefold().find(
            marker.casefold(), marker_offset + len(marker)
        )
        >= 0
        or not manifest_path_text[marker_offset + len(marker) :]
        or ".." in Path(manifest_path_text).parts
        or ":" in manifest_path_text[marker_offset:]
    ):
        raise BindingRefusal(
            "durability private manifest is not an exact retained volume-GUID path"
        )
    retained_root = manifest_path_text[: marker_offset + len(marker) - 1]
    stage_f_root = manifest_path_text[:marker_offset]
    watch = _windows_start_recursive_tree_watch(Path(stage_f_root))
    failure: BaseException | None = None
    result: dict[str, object] | None = None
    try:
        with _RetainedMaterialLocks(retained_root) as locks:
            private_manifest = strict_loads(
                locks.read(args.private_manifest, "private host manifest trust anchor"),
                require_canonical=True,
            )
            source = args.source.resolve(strict=True)
            source_schema = (source / AUTHORITY_SCHEMA_PATH).resolve(strict=True)
            supplied_schema = args.schema.resolve(strict=True)
            if supplied_schema == source_schema:
                source_role_root = _normalized_volume_guid_path(
                    source, "durability committed source root"
                )
                source_schema_private = Path(
                    _normalized_volume_guid_path(
                        source_schema, "durability committed authority schema"
                    )
                )
                schema = _load_authority_schema(
                    source_schema_private,
                    locks.read_scoped(
                        source_schema_private,
                        source_role_root,
                        "committed authority schema",
                    ),
                )
            else:
                schema = _load_authority_schema(
                    args.schema,
                    locks.read(args.schema, "retained materialized authority schema"),
                )
            receipt_validator = ClosedSchemaValidator(schema)
            validate_private_host_manifest(receipt_validator, private_manifest)
            expected_stage_root = private_manifest["filesystem"][
                "private_directories"
            ]["stage_f_root"]
            expected_retained_root = (
                private_manifest["filesystem"]["private_directories"][
                    "independent_audit"
                ]
                + "\\retained-evidence"
            )
            if (
                stage_f_root != expected_stage_root
                or retained_root != expected_retained_root
            ):
                raise BindingRefusal(
                    "durability manifest trust anchor differs from its private roles"
                )
            locks.bind_selected_volume_serial(
                private_manifest["filesystem"]["ntfs_volume_data"][
                    "volume_serial_number"
                ]
            )
            receipt = strict_loads(
                locks.read(args.receipt, "durability receipt"),
                require_canonical=True,
            )
            host_runtime_preimage = strict_loads(
                locks.read(args.host_runtime_preimage, "host runtime preimage"),
                require_canonical=True,
            )
            path_materials = _load_identity_materials(
                args.identity_material_index, locks.read
            )
            receipt_validator.validate_definition("durability_probe_receipt", receipt)
            receipt_validator.validate_definition(
                "host_validation_runtime_preimage", host_runtime_preimage
            )
            _verify_private_root_outside_git(private_manifest, args.source)
            verify_identity(
                receipt["host_validation_runtime_identity"],
                host_runtime_preimage,
                kind="stage_f_host_validation_runtime/v1",
            )
            if (
                private_manifest["host_validation_runtime_preimage"]
                != host_runtime_preimage
                or private_manifest["host_validation_runtime_identity"]
                != receipt["host_validation_runtime_identity"]
            ):
                raise BindingRefusal(
                    "durability receipt runtime differs from the private manifest"
                )
            validate_durability_receipt(
                receipt, host_runtime_preimage=host_runtime_preimage
            )
            validate_durability_private_paths(
                receipt,
                private_manifest=private_manifest,
                identity_preimages=path_materials,
            )
            temporary_role_root = private_manifest["filesystem"][
                "private_directories"
            ]["temporary"]
            _verify_complete_challenge_history(
                receipt_validator,
                private_manifest,
                [receipt],
                path_materials,
                lambda path, label: locks.read_scoped(
                    path, temporary_role_root, label
                ),
            )
            path_materials.assert_complete_consumption()
            invocation = receipt["orchestrator_probe_invocation_preimage"]
            _require_executing_artifact(
                Path(_BOOTSTRAP_LOCK_CONTEXT[2]),
                observed_byte_count=invocation["validator_zipapp_byte_count"],
                observed_sha256=invocation["validator_zipapp_sha256"],
            )
            _verify_private_path_identity(
                invocation["validator_zipapp_path_identity"],
                _BOOTSTRAP_LOCK_CONTEXT[2],
                "executing durability validator zipapp",
            )
            result = {
                "schema": "stage_f_binding_durability_validation/v1",
                **ZERO_SCIENCE_COUNTERS,
            }
    except BaseException as exc:
        failure = exc
    try:
        _windows_finish_recursive_tree_watch(watch, require_quiet=failure is None)
    except BaseException as exc:
        if failure is None:
            failure = exc
    if failure is not None:
        raise failure
    if result is None:
        raise BindingRefusal("durability receipt validation produced no result")
    return result


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    artifacts = subparsers.add_parser("source-artifacts")
    artifacts.add_argument("--schema", type=Path, required=True)
    artifacts.add_argument("--source", type=Path, required=True)
    artifacts.add_argument("--git-object-material-index", type=Path, required=True)
    artifacts.add_argument("--identity-material-index", type=Path, required=True)
    artifacts.add_argument("--source-bundle", type=Path, required=True)
    artifacts.add_argument("--validator-zipapp", type=Path, required=True)
    durability = subparsers.add_parser("durability-receipt")
    durability.add_argument("--schema", type=Path, required=True)
    durability.add_argument("--receipt", type=Path, required=True)
    durability.add_argument("--host-runtime-preimage", type=Path, required=True)
    durability.add_argument("--private-manifest", type=Path, required=True)
    durability.add_argument("--identity-material-index", type=Path, required=True)
    durability.add_argument("--source", type=Path, required=True)
    for command, full_authorization_required in (
        ("readiness-chain", False),
        ("record-chain", True),
    ):
        chain = subparsers.add_parser(command)
        for name in (
            "schema",
            "private-manifest",
            "public-binding",
            "bundle",
            "capacity-snapshot",
            "power-snapshot",
            "validation-receipt",
        ):
            chain.add_argument(f"--{name}", type=Path, required=True)
        chain.add_argument("--source", type=Path, required=True)
        chain.add_argument("--git-object-material-index", type=Path, required=True)
        chain.add_argument("--source-bundle", type=Path, required=True)
        chain.add_argument("--validator-zipapp", type=Path, required=True)
        chain.add_argument("--identity-material-index", type=Path, required=True)
        chain.add_argument("--referenced-binding-index", type=Path, required=True)
        chain.add_argument("--private-durability-bundle", type=Path, required=True)
        chain.add_argument("--durability-receipt-index", type=Path, required=True)
        chain.add_argument(
            "--previous-capacity-snapshot", type=Path, action="append", default=[]
        )
        for name in (
            "preaudit-readiness",
            "independent-audit",
            "pass-readiness",
            "packet",
            "user-receipt",
            "authorization",
            "retained-statement",
        ):
            chain.add_argument(
                f"--{name}", type=Path, required=full_authorization_required
            )
    return parser


def _locked_zipapp_context() -> bool:
    source_name = str(__file__).replace("\\", "/").lower()
    argv_zero = str(sys.argv[0]).replace("\\", "/").lower()
    return (
        ".pyz/" in source_name
        and argv_zero.endswith(".pyz")
        and _BOOTSTRAP_LOCK_CONTEXT is not None
        and getattr(builtins, _BOOTSTRAP_SENTINEL, None) is _BOOTSTRAP_LOCK_CONTEXT
    )


def _require_executing_artifact(
    path: Path,
    *,
    observed_byte_count: int | None = None,
    observed_sha256: str | None = None,
) -> None:
    if _BOOTSTRAP_LOCK_CONTEXT is None:
        raise BindingRefusal("locked executing-artifact context is absent")
    _token, _handle, locked_path, locked_count, locked_sha256 = _BOOTSTRAP_LOCK_CONTEXT
    if os.fspath(path) != locked_path:
        raise BindingRefusal("validated artifact path differs from executing locked zipapp")
    if observed_byte_count is not None and observed_byte_count != locked_count:
        raise BindingRefusal("validated artifact byte count differs from executing locked zipapp")
    if observed_sha256 is not None and observed_sha256 != locked_sha256:
        raise BindingRefusal("validated artifact digest differs from executing locked zipapp")


def main(argv: list[str] | None = None) -> int:
    if not _locked_zipapp_context():
        print(
            "STAGE_F_LOCAL_BINDING_REFUSED: validator must execute as the locked source-only zipapp",
            file=sys.stderr,
        )
        return 2
    arguments = list(sys.argv[1:] if argv is None else argv)
    try:
        if arguments and arguments[0] == "--validator-zipapp":
            result = validate_durability_probe_entry(arguments)
        else:
            args = _parser().parse_args(arguments)
        if arguments and arguments[0] == "--validator-zipapp":
            pass
        elif args.command == "source-artifacts":
            _require_executing_artifact(args.validator_zipapp)
            validator = ClosedSchemaValidator(_load_authority_schema(args.schema))
            repository = _load_verified_git_repository(
                args.git_object_material_index
            )
            identity_preimages = _load_identity_materials(
                args.identity_material_index
            )
            result = validate_source_artifacts(
                args.source_bundle,
                args.validator_zipapp,
                validator=validator,
                repository=repository,
                identity_preimages=identity_preimages,
            )
            identity_preimages.assert_complete_consumption()
            _require_executing_artifact(
                args.validator_zipapp,
                observed_byte_count=result["zipapp_byte_count"],
                observed_sha256=result["zipapp_sha256"],
            )
        elif args.command == "durability-receipt":
            result = validate_standalone_durability_receipt(args)
        else:
            _require_executing_artifact(args.validator_zipapp)
            result = validate_record_chain(args)
        assert_zero_science_counters(
            {name: result.get(name) for name in ZERO_SCIENCE_COUNTERS}
        )
    except (BindingRefusal, OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        print(f"STAGE_F_LOCAL_BINDING_REFUSED: {exc}", file=sys.stderr)
        return 2
    print(canonical_bytes(result).decode("utf-8", "strict"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
