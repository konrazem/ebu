"""Synthetic, outcome-blind durability and locked-bootstrap controls."""

from __future__ import annotations

import ast
import base64
import builtins
import copy
import ctypes
import hashlib
import inspect
import json
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile
from unittest import mock
from pathlib import Path

from stage_f_binding.canonical import BindingRefusal
from stage_f_binding.canonical import canonical_bytes, sha256_identity
from stage_f_binding.durability import (
    DURABILITY_ACTIONS,
    ZERO_SCIENCE_COUNTERS,
    _execute_orchestrator_probe,
    _host_runtime_apis,
    _host_runtime_handle_projection,
    _host_runtime_security_lifecycle,
    _validate_artifact_lock,
    atomic_publish,
    execute_host_runtime_composite_controller,
    recover_checkpoint,
    validate_durability_action_trace,
    validate_durability_receipt,
    validate_live_storage_inventory,
    validate_no_science_counters,
    verify_checkpoint_hash,
    write_checkpoint,
)
from stage_f_binding import locked_zipapp_bootstrap as bootstrap


ROOT = Path(__file__).resolve().parents[2]
_EMPTY_SHA256 = hashlib.sha256(b"").hexdigest()
_SYNTHETIC_PAYLOAD = b"stage-f-outcome-blind-durability-control\n"


def _volume_guid_path(path: Path) -> str:
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    mount = ctypes.create_unicode_buffer(32768)
    volume = ctypes.create_unicode_buffer(32768)
    get_mount = kernel32.GetVolumePathNameW
    get_mount.argtypes = (ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32)
    get_mount.restype = ctypes.c_int
    get_volume = kernel32.GetVolumeNameForVolumeMountPointW
    get_volume.argtypes = (ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32)
    get_volume.restype = ctypes.c_int
    absolute = os.path.abspath(path)
    if not get_mount(absolute, mount, len(mount)) or not get_volume(
        mount.value, volume, len(volume)
    ):
        raise OSError(ctypes.get_last_error(), "volume-GUID path resolution failed")
    return (volume.value + absolute[len(mount.value) :]).rstrip("\\")

_ACTION_ROLES = (
    ("EMPTY", "EMPTY", "ZERO", "TERMINATED_PROBE_PROCESS"),
    ("EMPTY", "SYNTHETIC_PAYLOAD", "SYNTHETIC_PAYLOAD", "TERMINATED_PROBE_PROCESS"),
    ("SYNTHETIC_PAYLOAD", "SYNTHETIC_PAYLOAD", "SYNTHETIC_PAYLOAD", "TERMINATED_PROBE_PROCESS"),
    ("SYNTHETIC_PAYLOAD", "SYNTHETIC_PAYLOAD", "SYNTHETIC_PAYLOAD", "TERMINATED_PROBE_PROCESS"),
    ("SYNTHETIC_PAYLOAD", "PUBLISHED_FINAL", "SYNTHETIC_PAYLOAD", "TERMINATED_PROBE_PROCESS"),
    ("PUBLISHED_FINAL", "PUBLISHED_FINAL", "SYNTHETIC_PAYLOAD", "TERMINATED_PROBE_PROCESS"),
    ("PUBLISHED_FINAL", "PUBLISHED_FINAL", "SYNTHETIC_PAYLOAD", "TERMINATED_PROBE_PROCESS"),
    ("PUBLISHED_FINAL", "PUBLISHED_FINAL", "SYNTHETIC_PAYLOAD", "RESUMED_PROBE_PROCESS"),
    ("PUBLISHED_FINAL", "PUBLISHED_FINAL", "SYNTHETIC_PAYLOAD", "RESUMED_PROBE_PROCESS"),
    ("PUBLISHED_FINAL", "POST_RESTART_REREAD", "POST_RESTART_REREAD", "RESUMED_PROBE_PROCESS"),
    ("POST_RESTART_REREAD", "POST_RESTART_REREAD", "POST_RESTART_REREAD", "RESUMED_PROBE_PROCESS"),
    ("PUBLISHED_FINAL", "CORRUPT_FIXTURE", "CORRUPT_FIXTURE", "RESUMED_PROBE_PROCESS"),
    ("CORRUPT_FIXTURE", "CORRUPT_FIXTURE", "CORRUPT_FIXTURE", "RESUMED_PROBE_PROCESS"),
    ("PUBLISHED_FINAL", "ORPHAN_PARTIAL", "ORPHAN_PARTIAL", "RESUMED_PROBE_PROCESS"),
    ("ORPHAN_PARTIAL", "ORPHAN_PARTIAL", "ORPHAN_PARTIAL", "RESUMED_PROBE_PROCESS"),
    ("LAST_VERIFIED_DURABLE_CHECKPOINT", "RECOVERED_FINAL", "SYNTHETIC_PAYLOAD", "RESUMED_PROBE_PROCESS"),
    ("RECOVERED_FINAL", "RECOVERED_FINAL", "SYNTHETIC_PAYLOAD", "RESUMED_PROBE_PROCESS"),
)


def _action_trace() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for index, (action, roles) in enumerate(zip(DURABILITY_ACTIONS, _ACTION_ROLES), 1):
        input_role, output_role, count_role, actor_role = roles
        rows.append(
            {
                "ordinal": index,
                "action": action,
                "observed_utc": f"2026-01-01T00:00:{index:02d}Z",
                "input_sha256": _EMPTY_SHA256,
                "input_hash_role": input_role,
                "output_sha256": _EMPTY_SHA256,
                "output_hash_role": output_role,
                "observed_byte_count": 0,
                "byte_count_role": count_role,
                "actor_process_role": actor_role,
                "actor_process_id": 100 if index <= 7 else 101,
                "actor_process_creation_filetime_uint64": 200 if index <= 7 else 201,
                "os_result_code": 0,
                "status": "PASS",
            }
        )
    return rows


def _bootstrap_base(phase: str) -> list[str]:
    root = r"\\?\Volume{01234567-89ab-cdef-0123-456789abcdef}\private"
    return [
        "--validator-zipapp",
        root + r"\validator.pyz",
        "--validator-zipapp-byte-count",
        "123",
        "--validator-zipapp-sha256",
        "a" * 64,
        "--host-runtime-lock-acquisition-sha256",
        "b" * 64,
        "--durability-probe-phase",
        phase,
        "--invocation-preimage",
        root + rf"\{phase.lower()}-invocation.json",
    ]


class NoScienceAndTraceTests(unittest.TestCase):
    def test_exact_closed_zero_science_counters(self) -> None:
        validate_no_science_counters(dict(ZERO_SCIENCE_COUNTERS))
        for mutation in ("missing", "extra", "nonzero", "boolean"):
            changed = dict(ZERO_SCIENCE_COUNTERS)
            if mutation == "missing":
                changed.pop("runner_import_count")
            elif mutation == "extra":
                changed["other_count"] = 0
            elif mutation == "nonzero":
                changed["model_execution_count"] = 1
            else:
                changed["stochastic_draw_count"] = False
            with self.subTest(mutation=mutation), self.assertRaises(BindingRefusal):
                validate_no_science_counters(changed)

    def test_exact_seventeen_action_trace_and_closed_negatives(self) -> None:
        rows = _action_trace()
        validate_durability_action_trace(rows)
        mutations = []
        missing = copy.deepcopy(rows)
        missing.pop()
        mutations.append(missing)
        reordered = copy.deepcopy(rows)
        reordered[0], reordered[1] = reordered[1], reordered[0]
        mutations.append(reordered)
        changed_role = copy.deepcopy(rows)
        changed_role[9]["output_hash_role"] = "PUBLISHED_FINAL"
        mutations.append(changed_role)
        changed_actor = copy.deepcopy(rows)
        changed_actor[7]["actor_process_role"] = "TERMINATED_PROBE_PROCESS"
        mutations.append(changed_actor)
        changed_time = copy.deepcopy(rows)
        changed_time[8]["observed_utc"] = "2025-01-01T00:00:00Z"
        mutations.append(changed_time)
        extra = copy.deepcopy(rows)
        extra[0]["claim"] = True
        mutations.append(extra)
        for index, mutation in enumerate(mutations):
            with self.subTest(index=index), self.assertRaises(BindingRefusal):
                validate_durability_action_trace(mutation)

    def test_assertion_only_receipt_refuses(self) -> None:
        with self.assertRaises(BindingRefusal):
            validate_durability_receipt({"disposition": "SYNTHETIC_DURABILITY_PASS"})


class SyntheticCheckpointTests(unittest.TestCase):
    def test_write_flush_atomic_publish_restart_reread_and_hash(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            temporary = root / "checkpoint.partial"
            final = root / "checkpoint-v1.json"
            digest = hashlib.sha256(_SYNTHETIC_PAYLOAD).hexdigest()
            result = write_checkpoint(
                _SYNTHETIC_PAYLOAD,
                temporary,
                final,
                synthetic=True,
            )
            self.assertFalse(temporary.exists())
            self.assertEqual(result["byte_count"], len(_SYNTHETIC_PAYLOAD))
            self.assertEqual(result["sha256"], digest)
            self.assertEqual(result["scientific_counters"], dict(ZERO_SCIENCE_COUNTERS))
            self.assertFalse(result["publication"]["replace_existing"])
            verified = verify_checkpoint_hash(
                final,
                digest,
                expected_byte_count=len(_SYNTHETIC_PAYLOAD),
                synthetic=True,
            )
            self.assertEqual(verified["sha256"], digest)

    def test_corruption_existing_target_and_orphan_partial_refuse(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "fresh.partial"
            final = root / "existing.final"
            source.write_bytes(_SYNTHETIC_PAYLOAD)
            final.write_bytes(b"predecessor")
            with self.assertRaises(BindingRefusal):
                atomic_publish(source, final, synthetic=True)
            corrupt = root / "corrupt.final"
            corrupt.write_bytes(b"corrupt")
            with self.assertRaises(BindingRefusal):
                verify_checkpoint_hash(
                    corrupt,
                    hashlib.sha256(_SYNTHETIC_PAYLOAD).hexdigest(),
                    synthetic=True,
                )
            last_good = root / "last-good.final"
            last_good.write_bytes(_SYNTHETIC_PAYLOAD)
            orphan = root / "orphan.partial"
            orphan.write_bytes(b"orphan")
            with self.assertRaises(BindingRefusal):
                recover_checkpoint(
                    last_good,
                    root / "recovered.final",
                    hashlib.sha256(_SYNTHETIC_PAYLOAD).hexdigest(),
                    orphan_partial_paths=(orphan,),
                    synthetic=True,
                )

    def test_recovery_uses_only_verified_last_good_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            last_good = root / "last-good.final"
            last_good.write_bytes(_SYNTHETIC_PAYLOAD)
            recovered = root / "recovered.final"
            digest = hashlib.sha256(_SYNTHETIC_PAYLOAD).hexdigest()
            result = recover_checkpoint(
                last_good,
                recovered,
                digest,
                expected_byte_count=len(_SYNTHETIC_PAYLOAD),
                synthetic=True,
            )
            self.assertEqual(
                result["recovery_disposition"],
                "RECOVERED_LAST_VERIFIED_DURABLE_CHECKPOINT",
            )
            self.assertEqual(recovered.read_bytes(), _SYNTHETIC_PAYLOAD)
            self.assertEqual(result["sha256"], digest)

    def test_recovery_publishes_the_single_verified_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            last_good = root / "last-good.final"
            last_good.write_bytes(_SYNTHETIC_PAYLOAD)
            recovered = root / "recovered.final"
            replacement = b"substituted-after-verification\n"
            original_read = __import__(
                "stage_f_binding.durability", fromlist=["_read_stable"]
            )._read_stable
            last_good_reads = 0

            def raced_read(path: Path) -> tuple[int, str, bytes]:
                nonlocal last_good_reads
                if path == last_good:
                    last_good_reads += 1
                    payload = (
                        _SYNTHETIC_PAYLOAD
                        if last_good_reads == 1
                        else replacement
                    )
                    return (
                        len(payload),
                        hashlib.sha256(payload).hexdigest(),
                        payload,
                    )
                return original_read(path)

            with mock.patch(
                "stage_f_binding.durability._read_stable",
                side_effect=raced_read,
            ):
                result = recover_checkpoint(
                    last_good,
                    recovered,
                    hashlib.sha256(_SYNTHETIC_PAYLOAD).hexdigest(),
                    expected_byte_count=len(_SYNTHETIC_PAYLOAD),
                    synthetic=True,
                )
            self.assertEqual(last_good_reads, 1)
            self.assertEqual(recovered.read_bytes(), _SYNTHETIC_PAYLOAD)
            self.assertEqual(
                result["sha256"], hashlib.sha256(_SYNTHETIC_PAYLOAD).hexdigest()
            )


class CapacityPostwriteClosureTests(unittest.TestCase):
    def test_exact_retained_delta_is_remeasured_and_unlisted_files_refuse(self) -> None:
        if sys.platform != "win32":
            with self.assertRaisesRegex(
                BindingRefusal, r"^live Stage F storage inventory requires Win32$"
            ):
                validate_live_storage_inventory(
                    Path.cwd(),
                    (),
                    capacity_snapshot={},
                    capacity_snapshot_path=Path.cwd() / "capacity.json",
                    retained_evidence_root=Path.cwd() / "retained-evidence",
                    retained_file_observations={},
                )
            source = inspect.getsource(validate_live_storage_inventory)
            tree = ast.parse(source)
            refusal_messages = {
                node.args[0].value
                for node in ast.walk(tree)
                if isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "_refuse"
                and node.args
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)
            }
            self.assertTrue(
                {
                    "retained postwrite files differ from the exact causal role closure",
                    "live recursive inventory path closure differs",
                    "live recursive inventory rows changed between complete scans",
                    (
                        "retained allocation does not reconstruct the immediate capacity "
                        "publication lower bound or exceeds the full predebit"
                    ),
                }.issubset(refusal_messages)
            )
            compact = "".join(source.split())
            self.assertIn("recorded!=reconstructed_postwrite", compact)
            self.assertIn("retained_live_allocated<reconstructed_postwrite", compact)
            self.assertIn("retained_live_allocated>8*1073741824", compact)
            for helper in ("enumerate_tree", "measure_tree"):
                self.assertEqual(
                    sum(
                        isinstance(node, ast.Call)
                        and isinstance(node.func, ast.Name)
                        and node.func.id == helper
                        for node in ast.walk(tree)
                    ),
                    2,
                )
            return
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            retained = root / "independent-audit" / "retained-evidence"
            retained.mkdir(parents=True)
            capacity_path = retained / "capacity.json"
            material_path = retained / "material.bin"
            previous_capacity_path = retained / "previous-capacity.json"
            validation_path = retained / "validation.json"
            capacity_path.write_bytes(b"capacity")
            material_path.write_bytes(b"material")
            previous_capacity_path.write_bytes(b"previous")
            validation_path.write_bytes(b"validate")
            expected = [
                {
                    "relative_path": ".",
                    "storage_category": "CHECKPOINT_AND_WRITE_OVERHEAD",
                    "allocated_bytes": 0,
                },
                {
                    "relative_path": "independent-audit",
                    "storage_category": "CHECKPOINT_AND_WRITE_OVERHEAD",
                    "allocated_bytes": 0,
                },
                {
                    "relative_path": "independent-audit/retained-evidence",
                    "storage_category": "RETAINED_EVIDENCE",
                    "allocated_bytes": 0,
                },
                {
                    "relative_path": "independent-audit/retained-evidence/material.bin",
                    "entry_type": "REGULAR_FILE",
                    "storage_category": "RETAINED_EVIDENCE",
                    "logical_bytes": 8,
                    "content_sha256": hashlib.sha256(b"material").hexdigest(),
                    "file_id_128": "02" * 16,
                    "file_id_volume_serial_number": 7,
                    "allocated_bytes": 4096,
                },
                {
                    "relative_path": "independent-audit/retained-evidence/previous-capacity.json",
                    "entry_type": "REGULAR_FILE",
                    "storage_category": "RETAINED_EVIDENCE",
                    "logical_bytes": 8,
                    "content_sha256": hashlib.sha256(b"previous").hexdigest(),
                    "file_id_128": "03" * 16,
                    "file_id_volume_serial_number": 7,
                    "allocated_bytes": 4096,
                },
            ]
            observations = {
                str(capacity_path): {
                    "byte_count": 8,
                    "sha256": hashlib.sha256(b"capacity").hexdigest(),
                    "file_id_128": "01" * 16,
                    "volume_serial_number": 7,
                },
                str(material_path): {
                    "byte_count": 8,
                    "sha256": hashlib.sha256(b"material").hexdigest(),
                    "file_id_128": "02" * 16,
                    "volume_serial_number": 7,
                },
                str(previous_capacity_path): {
                    "byte_count": 8,
                    "sha256": hashlib.sha256(b"previous").hexdigest(),
                    "file_id_128": "03" * 16,
                    "volume_serial_number": 7,
                },
                str(validation_path): {
                    "byte_count": 8,
                    "sha256": hashlib.sha256(b"validate").hexdigest(),
                    "file_id_128": "04" * 16,
                    "volume_serial_number": 7,
                },
            }
            capacity = {
                "volume_allocation_unit_bytes": 4096,
                "ntfs_volume_data": {"bytes_per_file_record_segment": 1024},
                "retained_evidence_live_allocated_bytes_after_snapshot_write": 12288,
            }

            def measured(
                _path: Path,
                relative: str,
                category: str,
                **_keywords: object,
            ) -> dict[str, object]:
                observation = observations[str(root / Path(relative))]
                return {
                    "relative_path": relative,
                    "entry_type": "REGULAR_FILE",
                    "storage_category": category,
                    "logical_bytes": observation["byte_count"],
                    "content_sha256": observation["sha256"],
                    "file_id_128": observation["file_id_128"],
                    "file_id_volume_serial_number": observation[
                        "volume_serial_number"
                    ],
                    "allocated_bytes": 4096,
                }

            patches = (
                mock.patch(
                    "stage_f_binding.durability._windows_start_recursive_tree_watch",
                    return_value=object(),
                ),
                mock.patch(
                    "stage_f_binding.durability._windows_finish_recursive_tree_watch"
                ),
                mock.patch("stage_f_binding.durability._validate_live_inventory_row"),
                mock.patch(
                    "stage_f_binding.durability._measure_live_inventory_row",
                    side_effect=measured,
                ),
                mock.patch(
                    "stage_f_binding.durability._windows_lock_inventory_regular_files",
                    return_value=(),
                ),
                mock.patch(
                    "stage_f_binding.durability._windows_release_inventory_regular_files"
                ),
            )
            with (
                patches[0],
                patches[1],
                patches[2],
                patches[3],
                patches[4],
                patches[5],
            ):
                live = validate_live_storage_inventory(
                    root,
                    expected,
                    capacity_snapshot=capacity,
                    capacity_snapshot_path=capacity_path,
                    retained_evidence_root=retained,
                    retained_file_observations=observations,
                    permitted_postwrite_paths=(
                        "independent-audit/retained-evidence/capacity.json",
                        "independent-audit/retained-evidence/validation.json",
                    ),
                )
                self.assertEqual(live, 16384)
                capacity[
                    "retained_evidence_live_allocated_bytes_after_snapshot_write"
                ] = 12287
                with self.assertRaises(BindingRefusal):
                    validate_live_storage_inventory(
                        root,
                        expected,
                        capacity_snapshot=capacity,
                        capacity_snapshot_path=capacity_path,
                        retained_evidence_root=retained,
                        retained_file_observations=observations,
                        permitted_postwrite_paths=(
                            "independent-audit/retained-evidence/capacity.json",
                            "independent-audit/retained-evidence/validation.json",
                        ),
                    )
                capacity[
                    "retained_evidence_live_allocated_bytes_after_snapshot_write"
                ] = 12288
                with self.assertRaises(BindingRefusal):
                    validate_live_storage_inventory(
                        root,
                        [
                            row
                            for row in expected
                            if row["relative_path"]
                            != "independent-audit/retained-evidence/previous-capacity.json"
                        ],
                        capacity_snapshot=capacity,
                        capacity_snapshot_path=capacity_path,
                        retained_evidence_root=retained,
                        retained_file_observations=observations,
                        permitted_postwrite_paths=(
                            "independent-audit/retained-evidence/capacity.json",
                            "independent-audit/retained-evidence/validation.json",
                        ),
                    )
                (retained / "unlisted.bin").write_bytes(b"unlisted")
                with self.assertRaises(BindingRefusal):
                    validate_live_storage_inventory(
                        root,
                        expected,
                        capacity_snapshot=capacity,
                        capacity_snapshot_path=capacity_path,
                        retained_evidence_root=retained,
                        retained_file_observations=observations,
                        permitted_postwrite_paths=(
                            "independent-audit/retained-evidence/capacity.json",
                            "independent-audit/retained-evidence/validation.json",
                        ),
                    )


class LockedBootstrapTests(unittest.TestCase):
    def test_exact_phase_vectors_parse_and_forward_unchanged(self) -> None:
        for phase in ("ORCHESTRATOR", "PRE_RESTART"):
            values = bootstrap._parse_args(_bootstrap_base(phase))
            self.assertEqual(values["--durability-probe-phase"], phase)
        post = _bootstrap_base("POST_RESTART") + [
            "--restart-challenge",
            r"\\?\Volume{01234567-89ab-cdef-0123-456789abcdef}\private\challenge.json",
            "--restart-challenge-sha256",
            "c" * 64,
            "--write-acknowledgement",
            r"\\?\Volume{01234567-89ab-cdef-0123-456789abcdef}\private\ack.json",
        ]
        values = bootstrap._parse_args(post)
        self.assertEqual(values["--restart-challenge-sha256"], "c" * 64)

    def test_locked_static_wrapper_parses_and_forwards_only_subcommand_tail(self) -> None:
        root = r"\\?\Volume{01234567-89ab-cdef-0123-456789abcdef}\private"
        wrapper = [
            "--validator-zipapp",
            root + r"\validator.pyz",
            "--validator-zipapp-byte-count",
            "123",
            "--validator-zipapp-sha256",
            "a" * 64,
            "--locked-validator-subcommand",
            "durability-receipt",
            "--schema",
            root + r"\schema.json",
            "--receipt",
            root + r"\receipt.json",
        ]
        values = bootstrap._parse_args(wrapper)
        self.assertEqual(
            values["_forward"],
            ["durability-receipt", *wrapper[8:]],
        )
        for command in ("source-artifacts", "readiness-chain", "record-chain"):
            alternative = list(wrapper)
            alternative[7] = command
            self.assertEqual(
                bootstrap._parse_args(alternative)["_forward"],
                [command, *alternative[8:]],
            )
        observed: list[list[str]] = []
        close = mock.Mock(return_value=1)

        def run_path(path: str, *, run_name: str) -> None:
            self.assertEqual(path, wrapper[1])
            self.assertEqual(run_name, "__main__")
            self.assertTrue(hasattr(builtins, "_EBU_STAGE_F_LOCKED_ZIPAPP_V1"))
            observed.append(list(sys.argv))

        with mock.patch.object(
            bootstrap, "_open_and_verify", return_value=(1234, close)
        ), mock.patch.object(bootstrap.runpy, "run_path", side_effect=run_path):
            bootstrap.main(wrapper)
        self.assertEqual(observed, [[wrapper[1], "durability-receipt", *wrapper[8:]]])
        close.assert_called_once_with(1234)
        self.assertFalse(hasattr(builtins, "_EBU_STAGE_F_LOCKED_ZIPAPP_V1"))

    def test_durability_forwarding_remains_the_unchanged_original_vector(self) -> None:
        vector = _bootstrap_base("PRE_RESTART")
        observed: list[list[str]] = []
        close = mock.Mock(return_value=1)

        def run_path(path: str, *, run_name: str) -> None:
            observed.append(list(sys.argv))

        with mock.patch.object(
            bootstrap, "_open_and_verify", return_value=(1234, close)
        ), mock.patch.object(bootstrap.runpy, "run_path", side_effect=run_path):
            bootstrap.main(vector)
        self.assertEqual(observed, [[vector[1], *vector]])
        close.assert_called_once_with(1234)

    def test_missing_extra_reordered_or_cross_phase_suffix_refuses(self) -> None:
        vectors = []
        missing = _bootstrap_base("PRE_RESTART")[:-1]
        vectors.append(missing)
        extra = _bootstrap_base("ORCHESTRATOR") + ["--extra", "value"]
        vectors.append(extra)
        reordered = _bootstrap_base("ORCHESTRATOR")
        reordered[0], reordered[2] = reordered[2], reordered[0]
        vectors.append(reordered)
        vectors.append(_bootstrap_base("POST_RESTART"))
        wrong_suffix = _bootstrap_base("PRE_RESTART") + [
            "--restart-challenge",
            r"\\?\Volume{01234567-89ab-cdef-0123-456789abcdef}\private\challenge.json",
            "--restart-challenge-sha256",
            "c" * 64,
            "--write-acknowledgement",
            r"\\?\Volume{01234567-89ab-cdef-0123-456789abcdef}\private\ack.json",
        ]
        vectors.append(wrong_suffix)
        root = r"\\?\Volume{01234567-89ab-cdef-0123-456789abcdef}\private"
        vectors.extend(
            (
                [
                    "--validator-zipapp",
                    root + r"\validator.pyz",
                    "--validator-zipapp-byte-count",
                    "123",
                    "--validator-zipapp-sha256",
                    "a" * 64,
                    "--locked-validator-subcommand",
                    "unknown",
                ],
                [
                    "--validator-zipapp-byte-count",
                    "123",
                    "--validator-zipapp",
                    root + r"\validator.pyz",
                    "--validator-zipapp-sha256",
                    "a" * 64,
                    "--locked-validator-subcommand",
                    "source-artifacts",
                ],
            )
        )
        for index, vector in enumerate(vectors):
            with self.subTest(index=index), self.assertRaises(bootstrap.BootstrapRefusal):
                bootstrap._parse_args(vector)

    def test_bootstrap_blob_limit_and_production_import_guard(self) -> None:
        sources = (
            ROOT / "stage_f_binding" / "durability.py",
            ROOT / "stage_f_binding" / "locked_zipapp_bootstrap.py",
        )
        forbidden = {
            "random",
            "secrets",
            "numpy",
            "scipy",
            "pandas",
            "requests",
            "socket",
            "urllib",
            "ebu_framework",
            "stage_e_harness",
        }
        for source in sources:
            raw = source.read_bytes()
            self.assertNotIn(b"\r", raw.replace(b"\r\n", b""))
            normalized = raw.replace(b"\r\n", b"\n")
            text = normalized.decode("utf-8")
            tree = ast.parse(text, filename=str(source))
            imports = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.update(alias.name.split(".")[0] for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imports.add(node.module.split(".")[0])
            self.assertTrue(forbidden.isdisjoint(imports))
        bootstrap_blob = sources[1].read_bytes().replace(b"\r\n", b"\n")
        self.assertLessEqual(len(bootstrap_blob), 8192)
        self.assertTrue({"ctypes", "hashlib", "runpy"}.issubset(imports))
        self.assertTrue({"ebu_framework", "stage_e_harness"}.isdisjoint(sys.modules))


class ExecutableDurabilityOrchestratorTests(unittest.TestCase):
    def test_external_controller_refuses_unexecutable_volume_guid_application(self) -> None:
        if sys.platform != "win32":
            with self.assertRaises(BindingRefusal):
                execute_host_runtime_composite_controller({})
            self.assertTrue(
                {"ebu_framework", "stage_e_harness"}.isdisjoint(sys.modules)
            )
            return
        runtime_root = _volume_guid_path(Path(sys.executable).parent)
        executable_path = runtime_root + r"\python.exe"
        executable_raw = Path(sys.executable).read_bytes()
        apis = _host_runtime_apis()
        directory_handle = apis["create"](
            runtime_root, 131200, 1, None, 3, 35651584, None
        )
        self.assertNotIn(directory_handle, (None, ctypes.c_void_p(-1).value))
        directory_handle = int(directory_handle)
        try:
            directory_projection = _host_runtime_handle_projection(
                apis, directory_handle
            )
            directory_security = _host_runtime_security_lifecycle(
                apis, directory_handle
            )
        finally:
            self.assertTrue(apis["close"](directory_handle))
        runtime = {
            "schema": "stage_f_host_validation_runtime/v1",
            "provider_bundle_version": "SYNTHETIC-OUTCOME-BLIND",
            "implementation": "CPython",
            "python_version": sys.version.split()[0],
            "architecture": "ARM64"
            if os.environ.get("PROCESSOR_ARCHITECTURE", "").upper() == "ARM64"
            else "AMD64",
            "runtime_root_path_identity": sha256_identity(
                "stage_f_private_path/v1", runtime_root.encode("utf-8")
            ),
            "executable_relative_path": "python.exe",
            "python_executable_sha256": hashlib.sha256(executable_raw).hexdigest(),
            "sqlite_version": __import__("sqlite3").sqlite_version,
            "ordered_runtime_file_rows": [
                {
                    "relative_path": "python.exe",
                    "byte_count": len(executable_raw),
                    "sha256": hashlib.sha256(executable_raw).hexdigest(),
                }
            ],
            "runtime_file_count": 1,
            "ordered_runtime_directory_rows": [
                {
                    "relative_path": ".",
                    "volume_serial_number": directory_projection[
                        "volume_serial_number"
                    ],
                    "file_id_128": directory_projection["file_id_128"],
                    "raw_file_attributes": directory_projection[
                        "raw_file_attributes"
                    ],
                    "reparse_tag": 0,
                    "directory": True,
                    "security_information_mask": 7,
                    "security_descriptor_format": "SELF_RELATIVE",
                    "security_descriptor_byte_count": directory_security[
                        "security_descriptor_byte_count"
                    ],
                    "security_descriptor_sha256": directory_security[
                        "security_descriptor_sha256"
                    ],
                }
            ],
            "runtime_directory_count": 1,
            "inventory_complete": True,
            "standard_library_only": True,
            "isolated_mode_required": True,
            "site_initialization_permitted": False,
            "validator_zipapp_bytecode_cache_permitted": False,
            "network_access_permitted": False,
            "project_package_import_permitted": False,
        }
        runtime_identity = sha256_identity(
            "stage_f_host_validation_runtime/v1", runtime
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            zipapp = root / "validator.pyz"
            members = (
                ("__main__.py", ROOT / "scripts" / "validate_stage_f_local_binding.py"),
                ("stage_f_binding/__init__.py", ROOT / "stage_f_binding" / "__init__.py"),
                ("stage_f_binding/canonical.py", ROOT / "stage_f_binding" / "canonical.py"),
                ("stage_f_binding/binding.py", ROOT / "stage_f_binding" / "binding.py"),
                ("stage_f_binding/durability.py", ROOT / "stage_f_binding" / "durability.py"),
            )
            with zipfile.ZipFile(
                zipapp, "w", compression=zipfile.ZIP_STORED, allowZip64=False
            ) as archive:
                for name, source in members:
                    archive.writestr(name, source.read_bytes())
            private_root = _volume_guid_path(root)
            invocation_path = private_root + r"\outer.orchestrator-invocation.json"

            def identity(kind: str, value: str) -> dict[str, str]:
                return {"kind": kind, "value": value * 64, "sha256": value * 64}

            with self.assertRaisesRegex(
                BindingRefusal,
                r"CreateProcessW\(host-runtime ORCHESTRATOR\).*Win32 error 87",
            ):
                execute_host_runtime_composite_controller({
                    "public_host_alias": "EXECUTION-HOST-01",
                    "runtime_root": runtime_root,
                    "host_validation_runtime_preimage": runtime,
                    "host_validation_runtime_identity": runtime_identity,
                    "binding_validator_identity": identity(
                        "stage_f_binding_validator/v1", "a"
                    ),
                    "execution_environment_policy_identity": identity(
                        "stage_f_execution_environment_policy/v1", "b"
                    ),
                    "bootstrap_source_utf8": (
                        ROOT / "stage_f_binding" / "locked_zipapp_bootstrap.py"
                    ).read_bytes(),
                    "validator_zipapp_path": private_root + r"\validator.pyz",
                    "orchestrator_invocation_path": invocation_path,
                    "authority_schema_source_path": _volume_guid_path(
                        ROOT / "stage_f_local_execution_binding_evidence_schema.json"
                    ),
                })
            self.assertTrue(
                Path(invocation_path + ".host-runtime-lock-acquisition.json").is_file()
            )
            self.assertTrue(Path(invocation_path).is_file())
            self.assertFalse(Path(invocation_path + ".bootstrap-lock.json").exists())
            self.assertFalse(
                Path(invocation_path + ".host-runtime-lock-release.json").exists()
            )
            self.assertTrue({"ebu_framework", "stage_e_harness"}.isdisjoint(sys.modules))

    def test_locked_zipapp_runs_exact_seventeen_action_restart_route(self) -> None:
        if sys.platform != "win32":
            source = inspect.getsource(_execute_orchestrator_probe)
            tree = ast.parse(source)
            imported = {
                alias.name.split(".")[0]
                for node in ast.walk(tree)
                if isinstance(node, ast.Import)
                for alias in node.names
            } | {
                node.module.split(".")[0]
                for node in ast.walk(tree)
                if isinstance(node, ast.ImportFrom) and node.module
            }
            self.assertTrue(
                {"ebu_framework", "stage_e_harness", "numpy", "random"}.isdisjoint(
                    imported
                )
            )
            self.assertEqual(len(DURABILITY_ACTIONS), 17)
            return
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            zipapp = root / "validator.pyz"
            members = (
                ("__main__.py", ROOT / "scripts" / "validate_stage_f_local_binding.py"),
                ("stage_f_binding/__init__.py", ROOT / "stage_f_binding" / "__init__.py"),
                ("stage_f_binding/canonical.py", ROOT / "stage_f_binding" / "canonical.py"),
                ("stage_f_binding/binding.py", ROOT / "stage_f_binding" / "binding.py"),
                ("stage_f_binding/durability.py", ROOT / "stage_f_binding" / "durability.py"),
            )
            with zipfile.ZipFile(
                zipapp, "w", compression=zipfile.ZIP_STORED, allowZip64=False
            ) as archive:
                for name, source in members:
                    archive.writestr(name, source.read_bytes())
            zipapp_raw = zipapp.read_bytes()
            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
            mount = ctypes.create_unicode_buffer(32768)
            volume = ctypes.create_unicode_buffer(32768)
            get_mount = kernel32.GetVolumePathNameW
            get_mount.argtypes = (
                ctypes.c_wchar_p,
                ctypes.c_wchar_p,
                ctypes.c_uint32,
            )
            get_mount.restype = ctypes.c_int
            get_volume = kernel32.GetVolumeNameForVolumeMountPointW
            get_volume.argtypes = (
                ctypes.c_wchar_p,
                ctypes.c_wchar_p,
                ctypes.c_uint32,
            )
            get_volume.restype = ctypes.c_int
            self.assertTrue(get_mount(os.fspath(root), mount, len(mount)))
            self.assertTrue(get_volume(mount.value, volume, len(volume)))
            private_root = volume.value + os.fspath(root)[len(mount.value) :]
            zipapp_private = private_root + r"\validator.pyz"
            invocation_private = private_root + r"\orchestrator-invocation.json"
            bootstrap_raw = (ROOT / "stage_f_binding" / "locked_zipapp_bootstrap.py").read_bytes()
            executable = os.path.abspath(sys.executable)

            def identity(kind: str) -> dict[str, str]:
                return {"kind": kind, "value": "a" * 64, "sha256": "a" * 64}

            acquisition = {
                "schema": "stage_f_synthetic_host_runtime_lock_acquisition_test/v1",
                "host_validation_runtime_identity": identity(
                    "stage_f_host_validation_runtime/v1"
                ),
                "scientific_counters": dict(ZERO_SCIENCE_COUNTERS),
            }
            acquisition_sha256 = hashlib.sha256(
                canonical_bytes(acquisition)
            ).hexdigest()
            arguments = [
                "--validator-zipapp",
                zipapp_private,
                "--validator-zipapp-byte-count",
                str(len(zipapp_raw)),
                "--validator-zipapp-sha256",
                hashlib.sha256(zipapp_raw).hexdigest(),
                "--host-runtime-lock-acquisition-sha256",
                acquisition_sha256,
                "--durability-probe-phase",
                "ORCHESTRATOR",
                "--invocation-preimage",
                invocation_private,
            ]
            vector = [
                executable,
                "-I",
                "-S",
                "-B",
                "-c",
                bootstrap_raw.decode("utf-8", "strict"),
                *arguments,
            ]
            command_raw = subprocess.list2cmdline(vector).encode("utf-16le")
            invocation = {
                "schema": "stage_f_durability_probe_invocation/v1",
                "phase": "ORCHESTRATOR",
                "binding_validator_identity": identity("stage_f_binding_validator/v1"),
                "execution_environment_policy_identity": identity(
                    "stage_f_execution_environment_policy/v1"
                ),
                "host_validation_runtime_identity": identity(
                    "stage_f_host_validation_runtime/v1"
                ),
                "host_runtime_lock_acquisition_sha256": acquisition_sha256,
                "bootstrap_source_path": "stage_f_binding/locked_zipapp_bootstrap.py",
                "bootstrap_git_row": {
                    "path": "stage_f_binding/locked_zipapp_bootstrap.py",
                    "mode": "100644",
                    "git_object": hashlib.sha1(
                        f"blob {len(bootstrap_raw)}\0".encode("ascii") + bootstrap_raw
                    ).hexdigest(),
                    "byte_count": len(bootstrap_raw),
                    "raw_sha256": hashlib.sha256(bootstrap_raw).hexdigest(),
                },
                "bootstrap_source_byte_count": len(bootstrap_raw),
                "bootstrap_source_utf8_base64": base64.b64encode(
                    bootstrap_raw
                ).decode("ascii"),
                "executable_path_identity": sha256_identity(
                    "stage_f_private_path/v1", executable.encode("utf-8")
                ),
                "validator_zipapp_path_identity": sha256_identity(
                    "stage_f_private_path/v1", zipapp_private.encode("utf-8")
                ),
                "validator_zipapp_byte_count": len(zipapp_raw),
                "validator_zipapp_sha256": hashlib.sha256(zipapp_raw).hexdigest(),
                "invocation_preimage_path_identity": sha256_identity(
                    "stage_f_private_path/v1", invocation_private.encode("utf-8")
                ),
                "restart_challenge_path_identity": None,
                "restart_challenge_sha256": None,
                "acknowledgement_path_identity": None,
                "command_schema": "PYTHON_LOCKED_ZIPAPP_STAGE_F_BINDING_VALIDATOR_ORCHESTRATOR_V1",
                "command_line_construction": "BOUND_HOST_CPYTHON_SUBPROCESS_LIST2CMDLINE",
                "command_line_encoding": "UTF-16LE_WITHOUT_TERMINAL_NUL",
                "command_line_base64": base64.b64encode(command_raw).decode("ascii"),
                "command_line_utf16_code_unit_count": len(command_raw) // 2,
                "entrypoint_mode": "EXACT_GIT_BOOTSTRAP_C_OPTION_LOCKED_DETERMINISTIC_ZIPAPP",
                "isolated_mode": True,
                "network_access_permitted": False,
                "scientific_counters": dict(ZERO_SCIENCE_COUNTERS),
            }
            (root / "orchestrator-invocation.json").write_bytes(
                canonical_bytes(invocation)
            )
            refused = subprocess.run(
                vector,
                check=False,
                capture_output=True,
                text=True,
                timeout=30,
            )
            self.assertEqual(refused.returncode, 2)
            self.assertIn("STAGE_F_LOCAL_BINDING_REFUSED", refused.stderr)
            self.assertEqual(list(root.glob("*.orchestrator-evidence.json")), [])
            process = {
                "process_id": os.getpid(),
                "creation_filetime_uint64": 1,
                "executable_path_identity": invocation["executable_path_identity"],
                "executable_sha256": hashlib.sha256(
                    Path(executable).read_bytes()
                ).hexdigest(),
                "command_line_sha256": hashlib.sha256(command_raw).hexdigest(),
                "invocation_sha256": hashlib.sha256(
                    canonical_bytes(invocation)
                ).hexdigest(),
                "self_command_line_observation_api": "GetCommandLineW",
                "locked_bootstrap_verified_invocation": True,
            }
            route = _execute_orchestrator_probe(
                invocation,
                process,
                Path(invocation_private),
                executable=executable,
                validator_zipapp=zipapp_private,
                host_runtime_lock_acquisition=acquisition,
                host_runtime_lock_acquisition_path=(
                    invocation_private + ".host-runtime-lock-acquisition.json"
                ),
                authority_schema_path=invocation_private + ".authority-schema.json",
            )
            evidence_paths = list(root.glob("*.orchestrator-evidence.json"))
            self.assertEqual(len(evidence_paths), 1, route)
            evidence = json.loads(evidence_paths[0].read_bytes())
            self.assertEqual(evidence["action_count"], 17)
            self.assertEqual(
                [row["action"] for row in evidence["ordered_actions"]],
                list(DURABILITY_ACTIONS),
            )
            self.assertEqual(evidence["scientific_counters"], dict(ZERO_SCIENCE_COUNTERS))
            self.assertIn("terminated_artifact_lock_observation", evidence)
            self.assertIn("resumed_artifact_lock_observation", evidence)
            receipt_projection = {
                "binding_validator_identity": invocation[
                    "binding_validator_identity"
                ],
                "host_validation_runtime_identity": invocation[
                    "host_validation_runtime_identity"
                ],
            }
            restart = evidence["restart_observation"]
            for role, process, retained_invocation, field in (
                (
                    "TERMINATED_PROBE_PROCESS",
                    restart["terminated_process"],
                    evidence["terminated_invocation_preimage"],
                    "terminated_artifact_lock_observation",
                ),
                (
                    "RESUMED_PROBE_PROCESS",
                    restart["resumed_process"],
                    evidence["resumed_invocation_preimage"],
                    "resumed_artifact_lock_observation",
                ),
            ):
                _validate_artifact_lock(
                    evidence[field],
                    role=role,
                    process=process,
                    invocation=retained_invocation,
                    receipt=receipt_projection,
                )


if __name__ == "__main__":
    unittest.main()
