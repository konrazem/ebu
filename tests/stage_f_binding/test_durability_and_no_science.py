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
from stage_f_binding import durability as durability_module
from stage_f_binding.durability import (
    DURABILITY_ACTIONS,
    ZERO_SCIENCE_COUNTERS,
    WindowsStageFPrestartBackend,
    _execute_orchestrator_probe,
    _host_runtime_apis,
    _host_runtime_handle_projection,
    _host_runtime_security_lifecycle,
    _orchestrator_create_process,
    _validate_atomic_publication,
    _validate_docker_start_attempt,
    _validate_host_prerequisite_snapshot,
    _validate_ledger_append_observation,
    _validate_ledger_create_observation,
    _validate_raw_volume_capacity_observation,
    _validate_retained_subtree_allocation,
    _validate_usn_record_projection,
    _validate_artifact_lock,
    atomic_publish,
    execute_stage_f_live_prestart_controller,
    execute_stage_f_prestart_controller,
    execute_host_runtime_composite_controller,
    recover_checkpoint,
    validate_durability_action_trace,
    validate_durability_receipt,
    validate_live_storage_inventory,
    validate_no_science_counters,
    validate_stage_f_control_state_machine,
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


class CorrectedControlStateTests(unittest.TestCase):
    @staticmethod
    def _seal(record: dict[str, object], digest_field: str) -> dict[str, object]:
        result = dict(record)
        result[digest_field] = hashlib.sha256(canonical_bytes(record)).hexdigest()
        return result

    def _root_prefix(self) -> list[dict[str, object]]:
        campaign_path = {
            "kind": "stage_f_private_path/v1",
            "value": "1" * 64,
            "sha256": "1" * 64,
        }
        attempt_path = {
            "kind": "stage_f_private_path/v1",
            "value": "2" * 64,
            "sha256": "2" * 64,
        }
        parent_acquisition = {
            "schema": "stage_f_directory_watch_acquisition/v1",
            "directory_path_identity": campaign_path,
            "directory_handle_value_uint64": 101,
            "buffer_base_address_uint64": 201,
            "overlapped_address_uint64": 301,
            "event_handle_value_uint64": 401,
        }
        genesis = self._seal(
            {
                "schema": "stage_f_execution_attempt_genesis/v1",
                "campaign_parent_path_identity": campaign_path,
                "attempt_path_identity": attempt_path,
                "parent_watch_identity": sha256_identity(
                    "stage_f_directory_watch_acquisition/v1", parent_acquisition
                ),
                "scientific_counters": dict(ZERO_SCIENCE_COUNTERS),
            },
            "genesis_sha256",
        )
        usn = {
            "journal_id_unchanged": True,
            "range_complete": True,
            "wrapped_or_gapped": False,
            "unknown_record_count": 0,
            "access_errors": 0,
            "records": [],
            "record_count": 0,
            "protected_ticket_match_count": 0,
            "outside_scope_record_count": 0,
            "refused_protected_record_count": 0,
            "raw_buffers_partition_into_records_exactly": True,
            "ticket_watch_usn_ledger_bijection_recomputed": True,
        }
        watches = []
        for ordinal in (1, 2):
            directory_handle = 100 + ordinal
            buffer_address = 200 + ordinal
            overlapped_address = 300 + ordinal
            event_handle = 400 + ordinal
            watched_path = campaign_path if ordinal == 1 else attempt_path
            acquisition = (
                parent_acquisition
                if ordinal == 1
                else {
                    "schema": "stage_f_directory_watch_acquisition/v1",
                    "directory_path_identity": watched_path,
                    "directory_handle_value_uint64": directory_handle,
                    "buffer_base_address_uint64": buffer_address,
                    "overlapped_address_uint64": overlapped_address,
                    "event_handle_value_uint64": event_handle,
                }
            )
            watches.append(
                {
                    "acquisition": acquisition,
                    "ordinal": ordinal,
                    "role": (
                        "ANCHOR_SELF_DIRECT"
                        if ordinal == 1
                        else "EXECUTION_ATTEMPT_ROOT_SUBTREE"
                    ),
                    "watched_path_identity": watched_path,
                    "recursive": ordinal == 2,
                    "directory_handle_value_uint64": directory_handle,
                    "buffer_base_address_uint64": buffer_address,
                    "buffer_byte_count": 65536,
                    "overlapped_address_uint64": overlapped_address,
                    "event_handle_value_uint64": event_handle,
                    "notify_filter": 351,
                    "read_input_bytes_returned_pointer_is_null": True,
                    "read_input_directory_handle_value_uint64": directory_handle,
                    "read_input_buffer_base_address_uint64": buffer_address,
                    "read_input_overlapped_address_uint64": overlapped_address,
                    "read_input_watch_subtree": ordinal == 2,
                    "read_input_completion_routine_is_null": True,
                    "read_returned_nonzero": True,
                    "immediate_result_returned_nonzero": False,
                    "immediate_result_directory_handle_value_uint64": directory_handle,
                    "immediate_result_overlapped_address_uint64": overlapped_address,
                    "immediate_result_last_error": 996,
                    "immediate_result_bytes_transferred": 0,
                    "pending_at_common_epoch": True,
                    "overflow_or_enumeration_loss": False,
                    "held_through_launch_handoff": True,
                }
            )
        root = self._seal(
            {
                "schema": "stage_f_root_protection_epoch/v1",
                "execution_attempt_genesis": genesis,
                "anchors": [
                    {
                        "ordinal": ordinal,
                        "role": (
                            "SELECTED_VOLUME_ROOT"
                            if ordinal == 1
                            else "CAMPAIGN_PARENT"
                            if ordinal == 2
                            else "EXECUTION_ATTEMPT_ROOT"
                        ),
                        "path_identity": (
                            {"kind": "stage_f_private_path/v1", "value": "0" * 64, "sha256": "0" * 64}
                            if ordinal == 1
                            else campaign_path
                            if ordinal == 2
                            else attempt_path
                        ),
                        "parent_ordinal": None if ordinal == 1 else ordinal - 1,
                        "compare_object_handles_at_epoch": True,
                        "anchor_handle_value_uint64": 10 + ordinal,
                        "continuity_guard_handle_value_uint64": 20 + ordinal,
                        "reparse_tag": 0,
                        "held_through_launch_handoff": True,
                    }
                    for ordinal in (1, 2, 3)
                ],
                "anchor_count": 3,
                "watches": watches,
                "watch_count": 2,
                "immutable_file_locks": [
                    {
                        "share_mode": 1,
                        "locked_before_first_read": True,
                        "held_through_launch_handoff": True,
                    }
                ],
                "immutable_file_lock_count": 1,
                "usn_start_observation": usn,
                "active_through_launch_handoff": True,
                "scientific_counters": dict(ZERO_SCIENCE_COUNTERS),
            },
            "epoch_sha256",
        )
        return [
            {"definition": "stage_f_execution_attempt_genesis", "record": genesis},
            {"definition": "stage_f_root_protection_epoch", "record": root},
        ]

    @staticmethod
    def _put_raw(
        target: dict[str, object], prefix: str, raw: bytes, *, input_image: bool = False
    ) -> None:
        middle = "_input" if input_image else ""
        target[f"{prefix}{middle}_bytes_base64"] = base64.b64encode(raw).decode("ascii")
        target[f"{prefix}{middle}_sha256"] = hashlib.sha256(raw).hexdigest()

    def test_pure_root_epoch_prefix_and_closed_order(self) -> None:
        observed: list[str] = []

        def schema(definition: str, record: object) -> None:
            self.assertIs(type(record), dict)
            observed.append(definition)

        rows = self._root_prefix()
        result = validate_stage_f_control_state_machine(rows, schema)
        self.assertEqual(result["phase"], "ROOT_EPOCH_ACTIVE")
        self.assertEqual(observed, [row["definition"] for row in rows])
        self.assertEqual(result["scientific_counters"], dict(ZERO_SCIENCE_COUNTERS))
        with self.assertRaises(BindingRefusal):
            validate_stage_f_control_state_machine(list(reversed(rows)), schema)
        wrong_watch = self._root_prefix()
        wrong_watch[1]["record"]["watches"][0]["notify_filter"] = 350
        with self.assertRaises(BindingRefusal):
            validate_stage_f_control_state_machine(wrong_watch, schema)
        nested = self._root_prefix()
        nested.append(
            {
                "definition": "stage_f_scientific_launch_handoff",
                "record": {"schema": "stage_f_scientific_launch_handoff/v1"},
            }
        )
        with self.assertRaises(BindingRefusal):
            validate_stage_f_control_state_machine(nested, schema)

    def test_root_ledger_prefix_requires_ticket_usn_entry_and_append_chain(self) -> None:
        rows = self._root_prefix()
        root_identity = {
            "kind": "stage_f_root_protection_epoch/v1",
            "value": rows[1]["record"]["epoch_sha256"],
            "sha256": rows[1]["record"]["epoch_sha256"],
        }
        genesis_identity = {
            "kind": "stage_f_execution_attempt_genesis/v1",
            "value": rows[0]["record"]["genesis_sha256"],
            "sha256": rows[0]["record"]["genesis_sha256"],
        }
        usn = {
            "journal_id_unchanged": True,
            "range_complete": True,
            "wrapped_or_gapped": False,
            "unknown_record_count": 0,
            "access_errors": 0,
            "records": [],
            "record_count": 0,
            "protected_ticket_match_count": 0,
            "outside_scope_record_count": 0,
            "refused_protected_record_count": 0,
            "raw_buffers_partition_into_records_exactly": True,
            "ticket_watch_usn_ledger_bijection_recomputed": True,
        }
        ticket = self._seal(
            {
                "schema": "stage_f_ledger_append_ticket/v1",
                "previous_entry_identity": None,
            },
            "ticket_sha256",
        )
        ledger = self._seal(
            {
                "schema": "stage_f_evidence_ledger/v1",
                "execution_attempt_genesis_identity": genesis_identity,
                "root_protection_epoch_identity": root_identity,
                "ledger_create_observation": {"synthetic": True},
                "append_ticket": ticket,
                "ordinal": 0,
                "previous_entry_identity": None,
                "usn_range_sha256": hashlib.sha256(canonical_bytes(usn)).hexdigest(),
                "ledger_file_path_identity": {"synthetic": "path"},
                "ledger_file_volume_serial_number_uint64": 1,
                "ledger_file_id_128": "01" * 16,
                "ledger_handle_value_uint64": 71,
            },
            "ledger_sha256",
        )
        ledger_identity = {
            "kind": "stage_f_evidence_ledger/v1",
            "value": ledger["ledger_sha256"],
            "sha256": ledger["ledger_sha256"],
        }
        append = {
            "entry_identity": ledger_identity,
            "append_ticket_sha256": ticket["ticket_sha256"],
            "ledger_file_path_identity": ledger["ledger_file_path_identity"],
            "ledger_file_volume_serial_number_uint64": 1,
            "ledger_file_id_128": "01" * 16,
            "ledger_handle_value_uint64": 71,
        }
        rows.extend(
            (
                {"definition": "stage_f_usn_journal_range", "record": usn},
                {"definition": "stage_f_ledger_append_ticket", "record": ticket},
                {"definition": "stage_f_evidence_ledger_genesis", "record": ledger},
                {"definition": "stage_f_evidence_ledger_append_observation", "record": append},
            )
        )
        with mock.patch(
            "stage_f_binding.durability._validate_ledger_create_observation"
        ), mock.patch(
            "stage_f_binding.durability._validate_ledger_append_observation"
        ):
            result = validate_stage_f_control_state_machine(
                rows, lambda _name, _value: None
            )
            self.assertEqual(result["phase"], "ROOT_LEDGER_EPOCH_ACTIVE")
            missing_ticket = copy.deepcopy(rows)
            missing_ticket.pop(3)
            with self.assertRaises(BindingRefusal):
                validate_stage_f_control_state_machine(
                    missing_ticket, lambda _name, _value: None
                )

    def test_recursive_nonzero_science_and_prestart_fail_closed(self) -> None:
        rows = self._root_prefix()
        rows[1]["record"]["scientific_counters"]["model_execution_count"] = 1
        with self.assertRaises(BindingRefusal):
            validate_stage_f_control_state_machine(rows, lambda _name, _value: None)
        with self.assertRaisesRegex(BindingRefusal, "durable unsent"):
            execute_stage_f_prestart_controller(
                {
                    "control_records": self._root_prefix(),
                    "scientific_launch_handoff": {},
                    "scientific_counters": dict(ZERO_SCIENCE_COUNTERS),
                },
                lambda _name, _value: None,
            )

    def test_live_prestart_orders_root_before_first_private_read_and_aborts(self) -> None:
        prefix = self._root_prefix()
        token = object()
        calls: list[str] = []

        def result(name: str, rows: list[dict[str, object]], observation: dict[str, object]):
            calls.append(name)
            return {
                "state_token": token,
                "control_records": rows,
                "observation": observation,
                "scientific_counters": dict(ZERO_SCIENCE_COUNTERS),
            }

        def incept(**_kwargs: object) -> dict[str, object]:
            return result(
                "incept_fresh_attempt_root",
                prefix[:1],
                {
                    "fresh_directory_created_once": True,
                    "parent_watch_pending_before_absence_check": True,
                    "ancestor_parent_volume_protection_before_create": True,
                    "direct_watch_count": 1,
                    "recursive_watch_count": 1,
                    "all_watches_pending": True,
                    "usn_start_query_complete": True,
                    "private_byte_read_count_before_genesis": 0,
                },
            )

        def acquire(**_kwargs: object) -> dict[str, object]:
            return result(
                "acquire_root_and_volume_epoch",
                prefix[1:],
                {
                    "root_volume_handles_watches_and_usn_retained": True,
                    "direct_watch_count": 1,
                    "recursive_watch_count": 1,
                    "all_watches_pending": True,
                    "usn_start_query_complete": True,
                    "private_byte_read_count_before_root_protection_start": 0,
                    "immutable_file_lock_count": 1,
                },
            )

        def private_read(**_kwargs: object) -> dict[str, object]:
            calls.append("read_locked_authority_materials")
            raise BindingRefusal("synthetic outcome-blind stop")

        def abort(**_kwargs: object) -> dict[str, object]:
            calls.append("abort_without_start")
            return {}

        def unreachable(**_kwargs: object) -> dict[str, object]:
            self.fail("a post-read phase was reachable after the synthetic refusal")

        operations = {
            "incept_fresh_attempt_root": incept,
            "acquire_root_and_volume_epoch": acquire,
            "read_locked_authority_materials": private_read,
            "create_held_ledger": unreachable,
            "launch_suspended_validator": unreachable,
            "complete_outcome_blind_authorization_chain": unreachable,
            "publish_capacity_snapshot": unreachable,
            "close_capacity_consumption": unreachable,
            "attest_host_docker_and_create_inert_container": unreachable,
            "publish_durable_start_intent": unreachable,
            "freeze_uninvoked_handoff": unreachable,
            "abort_without_start": abort,
        }
        with self.assertRaisesRegex(BindingRefusal, "synthetic outcome-blind stop"):
            execute_stage_f_live_prestart_controller(
                {
                    "controller_input": {"authority_paths": ["synthetic"]},
                    "scientific_counters": dict(ZERO_SCIENCE_COUNTERS),
                },
                lambda _name, _record: None,
                operations,
            )
        self.assertEqual(
            calls,
            [
                "incept_fresh_attempt_root",
                "acquire_root_and_volume_epoch",
                "read_locked_authority_materials",
                "abort_without_start",
            ],
        )
        with self.assertRaisesRegex(BindingRefusal, "fields differ"):
            execute_stage_f_live_prestart_controller(
                {
                    "controller_input": {},
                    "scientific_counters": dict(ZERO_SCIENCE_COUNTERS),
                },
                lambda _name, _record: None,
                {**operations, "start_scientific_container": unreachable},
            )

    def test_windows_backend_routes_exact_phases_and_has_no_start_surface(self) -> None:
        backend = WindowsStageFPrestartBackend()
        operations = backend.operations()
        self.assertEqual(
            set(operations), set(durability_module._LIVE_PRESTART_OPERATION_NAMES)
        )
        self.assertFalse(hasattr(backend, "start_scientific_container"))
        observed: list[str] = []

        def helper(*, marker: str) -> str:
            observed.append(marker)
            return marker

        helpers = {
            name: (lambda _name=name, **_kwargs: helper(marker=_name))
            for name in operations
        }
        with mock.patch.object(durability_module.sys, "platform", "win32"), mock.patch.object(
            durability_module.ctypes, "sizeof", return_value=8
        ), mock.patch.dict(
            durability_module._WINDOWS_STAGE_F_PHASE_HELPERS,
            helpers,
            clear=True,
        ):
            self.assertEqual(
                [operations[name]() for name in sorted(operations)],
                sorted(operations),
            )
        self.assertEqual(observed, sorted(operations))

    def test_corrected_root_watch_uses_share_seven_pending_recursive_call(self) -> None:
        buffers: list[object] = []
        create_calls: list[tuple[object, ...]] = []
        read_calls: list[tuple[object, ...]] = []
        path = r"\\?\Volume{01234567-89ab-cdef-0123-456789abcdef}\attempt"

        def create(*args: object) -> int:
            create_calls.append(args)
            return 101

        def get_final(_handle: int, output: object, _capacity: int, _flags: int) -> int:
            output.value = path
            return len(path)

        def get_info(_handle: int, info_class: int, output: object, _size: int) -> int:
            if info_class == 18:
                value = ctypes.cast(
                    output, ctypes.POINTER(durability_module._FILE_ID_INFO)
                ).contents
                value.VolumeSerialNumber = 7
                for index in range(16):
                    value.FileId.Identifier[index] = index
            elif info_class == 9:
                value = ctypes.cast(
                    output,
                    ctypes.POINTER(durability_module._FILE_ATTRIBUTE_TAG_INFO),
                ).contents
                value.FileAttributes = 0x10
                value.ReparseTag = 0
            return 1

        def allocate(_base: object, size: int, _kind: int, _protection: int) -> int:
            value = ctypes.create_string_buffer(size)
            buffers.append(value)
            return ctypes.addressof(value)

        def read_changes(*args: object) -> int:
            read_calls.append(args)
            return 1

        def get_overlapped(
            _handle: int, _overlapped: int, transferred: object, _wait: bool
        ) -> int:
            ctypes.cast(transferred, ctypes.POINTER(ctypes.c_uint32)).contents.value = 0
            ctypes.set_last_error(996)
            return 0

        apis = {
            "create": create,
            "get_final": get_final,
            "get_info": get_info,
            "virtual_alloc": allocate,
            "create_event": lambda *_args: 104,
            "read_changes": read_changes,
            "get_overlapped": get_overlapped,
        }
        state = durability_module._WindowsStageFControllerState(apis)
        row = durability_module._windows_stage_f_start_root_watch(
            state, path, ordinal=1, recursive=True
        )
        self.assertEqual(create_calls[0][2], 7)
        self.assertEqual(read_calls[0][4], 351)
        self.assertIsNone(read_calls[0][5])
        self.assertTrue(row["recursive"])
        self.assertEqual(row["immediate_result_last_error"], 996)
        self.assertEqual(row["acquisition"]["file_id_128"], bytes(range(16)).hex())

    def test_usn_v2_v3_reference_canonicalization_and_alias_refusal(self) -> None:
        for major, width in ((2, 8), (3, 16)):
            child = bytes(range(width))
            parent = bytes(range(width, 2 * width))
            raw = bytes(80)
            name_raw = "x".encode("utf-16le")
            suffix = bytes(8) if major == 2 else b""
            record = {
                "record_version": major,
                "raw_record_bytes_base64": base64.b64encode(raw).decode("ascii"),
                "raw_record_sha256": hashlib.sha256(raw).hexdigest(),
                "record_length": len(raw),
                "major_version": major,
                "minor_version": 0,
                "file_reference_width_bits": width * 8,
                "file_reference_raw_bytes_base64": base64.b64encode(child).decode("ascii"),
                "parent_file_reference_raw_bytes_base64": base64.b64encode(parent).decode("ascii"),
                "file_reference_number": (child + suffix).hex(),
                "parent_file_reference_number": (parent + suffix).hex(),
                "file_reference_normalization": (
                    "V2_RAW_LE_8_PLUS_8_ZERO_BYTES_TO_LOWER_HEX_16_BYTES"
                    if major == 2
                    else "V3_RAW_LE_16_BYTES_TO_LOWER_HEX_16_BYTES"
                ),
                "file_reference_normalization_recomputed_from_raw_bytes": True,
                "parent_file_reference_normalization_recomputed_from_raw_bytes": True,
                "file_name_length_bytes": len(name_raw),
                "file_name_utf16le_base64": base64.b64encode(name_raw).decode("ascii"),
                "file_name": "x",
                "strict_projection_exact": True,
                "scope_disposition": "OUTSIDE_PROTECTED_SCOPE",
                "protected_identity_match_count": 0,
                "mutation_ticket_identity": None,
                "mutation_ticket_match_count": 0,
                "mutation_transaction_identity": None,
                "ledger_mutation_entry_identity": None,
            }
            _validate_usn_record_projection(record, f"synthetic v{major}")
            record["file_reference_number"] = str(int.from_bytes(child, "little"))
            with self.assertRaises(BindingRefusal):
                _validate_usn_record_projection(record, f"synthetic v{major} alias")

    def test_ledger_create_all_four_caller_buffers_bind_zero_preimages(self) -> None:
        handle = 41
        path = "X".encode("utf-16le") + b"\0\0"
        record: dict[str, object] = {
            "ledger_handle_value_uint64": handle,
            "create_api": "CreateFileW",
            "create_desired_access": 0xC0000000,
            "create_share_mode": 1,
            "create_disposition": 1,
            "create_flags_and_attributes": 0x80200080,
            "create_returned_valid_handle": True,
            "path_query_output_buffer_wchar_capacity": 4,
            "path_query_returned_wchar_count": 1,
            "path_query_input_handle_value_uint64": handle,
            "file_id_query_input_handle_value_uint64": handle,
            "standard_info_query_input_handle_value_uint64": handle,
            "attribute_query_input_handle_value_uint64": handle,
            "file_id_query_output_buffer_capacity": 24,
            "standard_info_query_output_buffer_capacity": 24,
            "attribute_query_output_buffer_capacity": 8,
            "path_query_returned_count_output_terminator_and_capacity_reconcile": True,
            "path_query_output_buffer_input_is_exactly_two_times_wchar_capacity_zero_bytes": True,
            "all_raw_call_handles_paths_pointers_counts_images_parsed_values_and_hashes_reconcile": True,
            "handle_continuously_retained": True,
        }
        self._put_raw(record, "path_query_output_buffer", bytes(8), input_image=True)
        self._put_raw(record, "path_query_output", path)
        for prefix, size, output_prefix in (
            ("file_id_query_output_buffer", 24, "file_id_query_output"),
            ("standard_info_query_output_buffer", 24, "standard_info_query_output"),
            ("attribute_query_output_buffer", 8, "attribute_query_output"),
        ):
            self._put_raw(record, prefix, bytes(size), input_image=True)
            self._put_raw(record, output_prefix, bytes([size]) * size)
        _validate_ledger_create_observation(record, "synthetic ledger create")
        for prefix in (
            "path_query_output_buffer",
            "file_id_query_output_buffer",
            "standard_info_query_output_buffer",
            "attribute_query_output_buffer",
        ):
            changed = copy.deepcopy(record)
            raw = base64.b64decode(changed[f"{prefix}_input_bytes_base64"])
            changed[f"{prefix}_input_bytes_base64"] = base64.b64encode(b"\1" + raw[1:]).decode("ascii")
            changed[f"{prefix}_input_sha256"] = hashlib.sha256(b"\1" + raw[1:]).hexdigest()
            with self.subTest(prefix=prefix), self.assertRaises(BindingRefusal):
                _validate_ledger_create_observation(changed, "mutated ledger create")

    def test_same_object_atomic_publication_requires_guard_and_independent_final_open(self) -> None:
        def identity(seed: str) -> dict[str, str]:
            return {
                "kind": "stage_f_private_path/v1",
                "value": seed * 64,
                "sha256": seed * 64,
            }

        def measurement(handle: int, path: dict[str, str]) -> dict[str, object]:
            return {
                "path_identity": path,
                "handle_value_uint64": handle,
                "path_query_handle_value_uint64": handle,
                "file_id_query_handle_value_uint64": handle,
                "standard_info_query_handle_value_uint64": handle,
                "attribute_query_handle_value_uint64": handle,
                "read_handle_value_uint64": handle,
                "volume_serial_number_uint64": 9,
                "file_id_128": "01" * 16,
                "raw_file_attributes": 128,
                "reparse_tag": 0,
                "byte_count": 3,
                "sha256": hashlib.sha256(b"abc").hexdigest(),
                "read_from_held_handle": True,
            }

        source = identity("a")
        target = identity("b")
        guard, final_handle = 81, 82
        record = {
            "schema": "stage_f_atomic_publication_observation/v1",
            "primitive": "MoveFileExW",
            "raw_flags": 8,
            "movefile_write_through_flag_set": True,
            "movefile_replace_existing_flag_set": False,
            "source_path_identity": source,
            "target_path_identity": target,
            "same_volume": True,
            "target_exists_before_call": False,
            "target_nonexistence_observation": "GetFileAttributesW_INVALID_FILE_ATTRIBUTES_ERROR_FILE_NOT_FOUND",
            "call_returned_nonzero": True,
            "source_absent_after_call": True,
            "target_present_after_call": True,
            "target_created_once": True,
            "target_overwrite_attempt_count": 0,
            "actor_process_id": 1,
            "actor_process_creation_filetime_uint64": 2,
            "actor_thread_id": 3,
            "operations_serialized": True,
            "source_guard_handle_value_uint64": guard,
            "source_guard_retained_across_move": True,
            "pre_move_guard_observation": measurement(guard, source),
            "post_move_guard_observation": measurement(guard, target),
            "post_move_guard_flush_api": "FlushFileBuffers",
            "post_move_guard_flush_handle_value_uint64": guard,
            "post_move_guard_flush_returned_nonzero": True,
            "final_open_desired_access": 2147483776,
            "final_open_share_mode": 7,
            "final_open_creation_disposition": 3,
            "final_open_flags_and_attributes": 2097152,
            "final_handle_observation": measurement(final_handle, target),
            "source_and_final_same_volume_file_id_byte_count_and_sha256": True,
            "parent_watch_observation": {
                "pending_before_target_check": True,
                "completed_before_same_object_verification_and_final_lock": True,
                "overflow_or_enumeration_loss": False,
                "postcompletion_root_watch_and_usn_coverage": True,
            },
            "independent_final_open_compared_by_compare_object_handles": False,
            "final_and_guard_stable_volume_file_id_attributes_byte_count_and_sha256": True,
            "final_handle_close_api": "CloseHandle",
            "final_handle_close_input_handle_value_uint64": final_handle,
            "final_handle_close_returned_nonzero": True,
            "final_handle_closed_utc": "2026-01-01T00:00:00Z",
            "duplicate_guard_retained_until_transaction_sealed": True,
            "final_open_api": "CreateFileW",
            "final_open_security_attributes": "NULL",
            "final_open_handle_value_uint64": final_handle,
            "final_open_returned_valid": True,
        }
        _validate_atomic_publication(record)
        record["independent_final_open_compared_by_compare_object_handles"] = True
        with self.assertRaises(BindingRefusal):
            _validate_atomic_publication(record)

    def test_ledger_append_same_handle_offsets_and_three_zero_preimage_classes(self) -> None:
        handle = 51
        wire = canonical_bytes({"schema": "synthetic_ledger_entry/v1"}) + b"\n"
        count = len(wire)
        record: dict[str, object] = {
            "ledger_handle_value_uint64": handle,
            "preappend_file_standard_info_handle_value_uint64": handle,
            "set_append_pointer_input_handle_value_uint64": handle,
            "write_input_handle_value_uint64": handle,
            "flush_input_handle_value_uint64": handle,
            "postflush_file_standard_info_handle_value_uint64": handle,
            "set_reread_pointer_input_handle_value_uint64": handle,
            "reread_input_handle_value_uint64": handle,
            "restore_pointer_input_handle_value_uint64": handle,
            "preappend_file_standard_info_output_buffer_capacity": 24,
            "postflush_file_standard_info_output_buffer_capacity": 24,
            "entry_wire_buffer_byte_count": count,
            "append_start_offset": 0,
            "append_byte_count": count,
            "preappend_end_of_file_bytes": 0,
            "set_append_pointer_result_offset": 0,
            "append_end_offset": count,
            "written_byte_count": count,
            "postflush_file_size": count,
            "set_reread_pointer_result_offset": 0,
            "reread_start_offset": 0,
            "reread_byte_count": count,
            "reread_bytes_read": count,
            "restore_pointer_result_offset": count,
            "reread_buffer_input_zero_initialized": True,
            "reread_buffer_input_is_exactly_reread_byte_count_zero_bytes": True,
            "all_raw_call_handles_pointers_counts_zero_preimages_returned_images_and_hashes_reconcile": True,
            "all_offsets_counts_hashes_and_handles_reconciled": True,
            "parent_watch_range_sha256": "a" * 64,
            "usn_range_sha256": "b" * 64,
        }
        for prefix, output_prefix in (
            ("preappend_file_standard_info_output_buffer", "preappend_file_standard_info_output"),
            ("postflush_file_standard_info_output_buffer", "postflush_file_standard_info_output"),
        ):
            self._put_raw(record, prefix, bytes(24), input_image=True)
            self._put_raw(record, output_prefix, bytes(24))
        for prefix, value in (
            ("set_append_pointer_new_position", 0),
            ("set_reread_pointer_new_position", 0),
            ("restore_pointer_new_position", count),
        ):
            self._put_raw(record, prefix, bytes(8), input_image=True)
            self._put_raw(record, prefix + "_output", value.to_bytes(8, "little"))
        for prefix in ("write_bytes_written", "reread_bytes_read"):
            self._put_raw(record, prefix, bytes(4), input_image=True)
            self._put_raw(record, prefix + "_output", count.to_bytes(4, "little"))
        self._put_raw(record, "entry_wire", wire)
        self._put_raw(record, "reread_buffer", bytes(count), input_image=True)
        self._put_raw(record, "reread_raw", wire)
        record["reread_sha256"] = record.pop("reread_raw_sha256")
        _validate_ledger_append_observation(record, "synthetic ledger append")
        changed = copy.deepcopy(record)
        changed["restore_pointer_result_offset"] = count - 1
        with self.assertRaises(BindingRefusal):
            _validate_ledger_append_observation(changed, "mutated ledger append")

    def test_docker_byte_nowait_refuses_error_more_data_and_unclosed_handle(self) -> None:
        handle = 61
        read: dict[str, object] = {
            "ordinal": 1,
            "input_handle_value_uint64": handle,
            "last_error": 234,
            "overlapped_pointer_is_null": True,
            "bytes_read": 0,
            "pre_read_monotonic_tick_uint64": 1,
            "post_read_monotonic_tick_uint64": 2,
        }
        self._put_raw(read, "bytes_read", bytes(4), input_image=True)
        self._put_raw(read, "bytes_read_output", bytes(4))
        self._put_raw(read, "output", b"")
        record = {
            "connection": {
                "named_pipe_path": r"\\.\pipe\docker_engine",
                "pipe_read_mode": "PIPE_READMODE_BYTE",
                "pipe_wait_mode": "PIPE_NOWAIT",
                "set_wait_mode_mode_input_bytes_base64": "AQAAAA==",
                "pipe_handle_value_uint64": handle,
            },
            "write_input_handle_value_uint64": handle,
            "write_overlapped_pointer_is_null": True,
            "ordered_read_calls": [read],
            "read_call_count": 1,
            "connection_release": {
                "pipe_handle_value_uint64": handle,
                "close_input_handle_value_uint64": handle,
                "close_returned_nonzero": True,
                "handle_closed_once": True,
                "no_use_after_close": True,
            },
            "transport_disposition": "READ_TERMINAL_FAILURE_AFTER_ANY_WRITE",
            "write_disposition": "FULL_WRITE",
            "bounded_response_window": {
                "schema": "stage_f_docker_named_pipe_bounded_response_window_observation/v1",
                "timeout_ms": 30000,
                "maximum_poll_delay_ms": 25,
                "maximum_read_attempt_count": 1201,
                "no_read_or_poll_after_terminal_cut": True,
            },
            "response_is_exact_complete_http_204": False,
            "daemon_acceptance_unknown": True,
        }
        with self.assertRaisesRegex(BindingRefusal, "ERROR_MORE_DATA"):
            _validate_docker_start_attempt(record, "synthetic Docker attempt")
        read["last_error"] = 109
        _validate_docker_start_attempt(record, "synthetic Docker attempt")
        record["connection_release"]["no_use_after_close"] = False
        with self.assertRaises(BindingRefusal):
            _validate_docker_start_attempt(record, "mutated Docker attempt")

    def test_legacy_process_launch_cannot_spawn_without_attestation_context(self) -> None:
        identity = {
            "kind": "stage_f_private_path/v1",
            "value": "a" * 64,
            "sha256": "a" * 64,
        }
        with mock.patch("stage_f_binding.durability.sys.platform", "win32"):
            with self.assertRaisesRegex(BindingRefusal, "image-attestation context"):
                _orchestrator_create_process(
                    r"C:\synthetic\python.exe",
                    [r"C:\synthetic\python.exe", "-I"],
                    {"executable_path_identity": identity},
                    phase="PRE_RESTART",
                    orchestrator_process={"process_id": 1},
                )

    def test_direct_retained_sum_and_raw_capacity_formulas_are_recomputed(self) -> None:
        subtree = {
            "inventory_entries": [
                {"relative_path": ".", "accounted_bytes": 4096},
                {"relative_path": "evidence.json", "accounted_bytes": 8192},
            ],
            "inventory_entry_count": 2,
            "ordered_relative_paths_utf8_nfc_ascending": True,
            "direct_accounted_bytes_sum": 12288,
            "retained_evidence_live_allocated_bytes": 12288,
            "direct_sum_equals_live_scalar": True,
            "root_entry_included": True,
            "all_descendants_included": True,
            "unknown_entry_count": 0,
        }
        self.assertEqual(
            _validate_retained_subtree_allocation(subtree, "synthetic subtree"),
            12288,
        )
        raw = {
            "sectors_per_cluster": 8,
            "bytes_per_sector": 512,
            "number_of_free_clusters": 100,
            "total_number_of_clusters": 200,
            "allocation_unit_bytes": 4096,
            "get_disk_free_space_w_free_bytes": 409600,
            "get_disk_free_space_w_capacity_bytes": 819200,
            "available_to_caller_bytes": 409600,
            "total_number_of_free_bytes": 409600,
            "total_number_of_bytes": 819200,
            "ntfs_volume_data": {
                "free_clusters": 100,
                "total_clusters": 200,
                "bytes_per_cluster": 4096,
            },
            "ntfs_volume_data_free_bytes": 409600,
            "ntfs_volume_data_capacity_bytes": 819200,
            "conservative_observed_free_bytes": 409600,
            "conservative_observed_capacity_bytes": 819200,
            "all_formulas_recomputed": True,
            "free_space_outputs_reconciled": True,
            "capacity_outputs_reconciled": True,
        }
        self.assertEqual(
            _validate_raw_volume_capacity_observation(raw, "synthetic volume"),
            409600,
        )
        changed = dict(raw)
        changed["conservative_observed_free_bytes"] += 1
        with self.assertRaises(BindingRefusal):
            _validate_raw_volume_capacity_observation(changed, "mutated volume")

    def test_raw_power_lid_reboot_and_session_projection(self) -> None:
        raw = bytes((1, 128, 75, 0)) + (3600).to_bytes(4, "little") + (7200).to_bytes(4, "little")
        facts = {
            "system_power_status_bytes_base64": base64.b64encode(raw).decode("ascii"),
            "system_power_status_sha256": hashlib.sha256(raw).hexdigest(),
            "ac_line_status": 1,
            "battery_flag": 128,
            "battery_life_percent": 75,
            "system_status_flag": 0,
            "battery_life_time_seconds": 3600,
            "battery_full_life_time_seconds": 7200,
            "plugged_in_lid_action_raw_index": 0,
            "plugged_in_lid_action": "DO_NOTHING",
            "get_system_power_status_returned_nonzero": True,
            "plugged_in_standby_idle_seconds": 0,
            "lid_open_statement_identity": None,
            "pending_reboot_registry_rows": [{} for _ in range(8)],
            "pending_reboot_registry_row_count": 8,
            "pending_reboot_marker_count": 0,
            "no_auto_reboot_policy_value": 1,
            "controller_session_logged_on": True,
            "derived_power_fields_reconcile_raw_queries": True,
        }
        snapshot = {
            "facts": facts,
            "settings_changed_by_validator": False,
            "historical_power_snapshot_exact_raw_fact_projection": True,
        }
        _validate_host_prerequisite_snapshot(snapshot, "synthetic prerequisites")
        facts["plugged_in_lid_action_raw_index"] = 1
        facts["plugged_in_lid_action"] = "SLEEP"
        with self.assertRaises(BindingRefusal):
            _validate_host_prerequisite_snapshot(snapshot, "mutated prerequisites")

    def test_raw_usn_backend_returns_schema_ready_continuation_from_mocked_apis(self) -> None:
        import struct as struct_module

        from stage_f_binding import durability as durability_module
        from stage_f_binding.binding import ClosedSchemaValidator

        name_raw = "a.txt".encode("utf-16le")
        record_length = 72
        record = struct_module.pack(
            "<IHH8s8sqQIIIIHH",
            record_length,
            2,
            0,
            b"\x01\x02\x03\x04\x05\x06\x07\x08",
            b"\x11\x12\x13\x14\x15\x16\x17\x18",
            100,
            133000000000000000,
            0x80000200,
            0,
            7,
            0x20,
            len(name_raw),
            60,
        ) + name_raw + bytes(record_length - 60 - len(name_raw))
        v3_name_raw = "b.txt".encode("utf-16le")
        v3_record_length = 88
        v3_child = bytes(range(16))
        v3_parent = bytes(range(16, 32))
        v3_record = struct_module.pack(
            "<IHH16s16sqQIIIIHH",
            v3_record_length,
            3,
            0,
            v3_child,
            v3_parent,
            172,
            133000000000000001,
            0x80000200,
            0,
            8,
            0x20,
            len(v3_name_raw),
            76,
        ) + v3_name_raw + bytes(v3_record_length - 76 - len(v3_name_raw))
        query_start = struct_module.pack(
            "<QqqqqQQHHIQq", 99, 0, 100, 0, 100000, 1048576, 65536, 2, 3, 0, 0, 0
        )
        query_end = struct_module.pack(
            "<QqqqqQQHHIQq", 99, 0, 260, 0, 100000, 1048576, 65536, 2, 3, 0, 0, 0
        )

        class MockUsnApis:
            def __init__(self) -> None:
                self.query_outputs = [query_start, query_end]
                self.read_outputs = [
                    struct_module.pack("<q", 260) + record + v3_record,
                    struct_module.pack("<q", 260),
                ]
                self.read_inputs: list[bytes] = []
                self.created: tuple[object, ...] | None = None
                self.closed: list[int] = []

            @staticmethod
            def _write(output: object, capacity: int, returned: object, raw: bytes) -> int:
                if len(raw) > capacity:
                    raise AssertionError("synthetic raw output exceeds capacity")
                ctypes.memmove(output, raw, len(raw))
                ctypes.cast(returned, ctypes.POINTER(ctypes.c_uint32)).contents.value = len(raw)
                return 1

            def create_file(self, *args: object) -> int:
                self.created = args
                return 0x1234

            def get_volume_information_by_handle(
                self,
                handle: int,
                volume_name: object,
                volume_name_capacity: int,
                serial: object,
                maximum_component: object,
                flags: object,
                filesystem_name: object,
                filesystem_name_capacity: int,
            ) -> int:
                self.assert_volume_information_inputs = (
                    handle,
                    volume_name,
                    volume_name_capacity,
                    maximum_component,
                    flags,
                    filesystem_name_capacity,
                )
                ctypes.cast(serial, ctypes.POINTER(ctypes.c_uint32)).contents.value = 0x12345678
                ctypes.memmove(filesystem_name, "NTFS\x00".encode("utf-16le"), 10)
                return 1

            def device_io_control(
                self,
                handle: int,
                code: int,
                input_buffer: object,
                input_count: int,
                output_buffer: object,
                output_capacity: int,
                returned: object,
                overlapped: object,
            ) -> int:
                self.last_handle = handle
                if code == durability_module._STAGE_F_FSCTL_GET_NTFS_VOLUME_DATA:
                    ntfs = durability_module._NTFS_VOLUME_DATA_BUFFER()
                    ntfs.VolumeSerialNumber = 0x0123456789ABCDEF
                    ntfs.NumberSectors = 100000
                    ntfs.TotalClusters = 12500
                    ntfs.FreeClusters = 10000
                    ntfs.TotalReserved = 0
                    ntfs.BytesPerSector = 512
                    ntfs.BytesPerCluster = 4096
                    ntfs.BytesPerFileRecordSegment = 1024
                    ntfs.ClustersPerFileRecordSegment = 1
                    ntfs.MftValidDataLength = 4096
                    ntfs.MftStartLcn = 4
                    ntfs.Mft2StartLcn = 8
                    ntfs.MftZoneStart = 16
                    ntfs.MftZoneEnd = 32
                    raw = ctypes.string_at(ctypes.addressof(ntfs), ctypes.sizeof(ntfs))
                elif code == durability_module._STAGE_F_FSCTL_QUERY_USN_JOURNAL:
                    self.assertIsNone(input_buffer)
                    self.assertEqual(input_count, 0)
                    raw = self.query_outputs.pop(0)
                elif code == durability_module._STAGE_F_FSCTL_READ_USN_JOURNAL:
                    raw_input = ctypes.string_at(input_buffer, input_count)
                    self.read_inputs.append(raw_input)
                    raw = self.read_outputs.pop(0)
                else:
                    raise AssertionError(f"unexpected control code {code}")
                return self._write(output_buffer, output_capacity, returned, raw)

            @staticmethod
            def last_error() -> int:
                return 0

            def close_handle(self, handle: int) -> int:
                self.closed.append(handle)
                return 1

            def assertIsNone(self, value: object) -> None:
                if value is not None:
                    raise AssertionError(f"expected None, got {value!r}")

            def assertEqual(self, left: object, right: object) -> None:
                if left != right:
                    raise AssertionError(f"{left!r} != {right!r}")

        tick = 0

        def clock() -> str:
            nonlocal tick
            tick += 1
            return f"2026-08-31T12:00:00.{tick:06d}Z"

        apis = MockUsnApis()
        volume = "\\\\?\\Volume{01234567-89ab-cdef-0123-456789abcdef}\\"
        backend = durability_module.StageFUsnJournalBackend(
            volume, apis=apis, clock=clock
        )
        backend.begin_range()
        result = backend.collect_range(
            lambda row: {
                "scope_disposition": "OUTSIDE_PROTECTED_SCOPE",
                "protected_identity_match_count": 0,
                "mutation_ticket_identity": None,
                "mutation_ticket_match_count": 0,
                "mutation_transaction_identity": None,
                "ledger_mutation_entry_identity": None,
            }
        )
        schema = json.loads(
            (
                ROOT
                / "stage_f_local_execution_binding_final_evidence_closure_correction_schema.json"
            ).read_bytes()
        )
        ClosedSchemaValidator(schema).validate_definition(
            "stage_f_usn_journal_range", result
        )
        self.assertEqual(result["read_call_count"], 2)
        self.assertEqual(result["record_count"], 2)
        self.assertEqual(result["terminal_next_usn"], 260)
        self.assertEqual(result["records"][0]["file_reference_number"], "0102030405060708" + "0" * 16)
        self.assertEqual(result["records"][1]["file_reference_number"], v3_child.hex())
        expected_first = struct_module.pack("<qIIQQQHH4x", 100, 0xFFFFFFFF, 0, 0, 0, 99, 2, 3)
        expected_second = struct_module.pack("<qIIQQQHH4x", 260, 0xFFFFFFFF, 0, 0, 0, 99, 2, 3)
        self.assertEqual(apis.read_inputs, [expected_first, expected_second])
        self.assertEqual(len(expected_first), 48)
        self.assertEqual(apis.created, (volume[:-1], 0x80000000, 3, None, 3, 0, None))
        backend.close()
        self.assertEqual(apis.closed, [0x1234])

    def test_held_ledger_backend_creates_and_appends_two_schema_ready_entries(self) -> None:
        import struct as struct_module

        from stage_f_binding import durability as durability_module
        from stage_f_binding.binding import ClosedSchemaValidator

        ledger_path = "\\\\?\\Volume{01234567-89ab-cdef-0123-456789abcdef}\\attempt\\ledger.jsonl"
        ledger_handle = 0x5678
        volume_serial = 0x0123456789ABCDEF
        file_id_raw = bytes(range(16))

        class MockLedgerApis:
            def __init__(self) -> None:
                self.file = bytearray()
                self.pointer = 0
                self.create_args: tuple[object, ...] | None = None
                self.close_calls: list[int] = []

            def create_file(self, *args: object) -> int:
                self.create_args = args
                return ledger_handle

            def get_final_path_name(
                self, handle: int, output: object, capacity: int, flags: int
            ) -> int:
                if (handle, flags) != (ledger_handle, 1):
                    raise AssertionError("final-path query input differs")
                raw = (ledger_path + "\x00").encode("utf-16le")
                if len(raw) > capacity * 2:
                    raise AssertionError("final-path mock buffer too small")
                ctypes.memmove(output, raw, len(raw))
                return len(ledger_path)

            def get_file_information(
                self, handle: int, info_class: int, output: object, capacity: int
            ) -> int:
                if handle != ledger_handle:
                    raise AssertionError("file-information handle differs")
                if info_class == durability_module._STAGE_F_FILE_ID_INFO_CLASS:
                    raw = struct_module.pack("<Q16s", volume_serial, file_id_raw)
                elif info_class == durability_module._STAGE_F_FILE_STANDARD_INFO_CLASS:
                    allocation = 0 if not self.file else ((len(self.file) + 4095) // 4096) * 4096
                    raw = struct_module.pack(
                        "<qqIBB2x", allocation, len(self.file), 1, 0, 0
                    )
                elif info_class == durability_module._STAGE_F_FILE_ATTRIBUTE_TAG_INFO_CLASS:
                    raw = struct_module.pack("<II", 0x80, 0)
                else:
                    raise AssertionError(f"unexpected information class {info_class}")
                if len(raw) != capacity:
                    raise AssertionError("file-information capacity differs")
                ctypes.memmove(output, raw, len(raw))
                return 1

            def set_file_pointer(
                self, handle: int, distance: object, output: object, method: int
            ) -> int:
                if (handle, method) != (ledger_handle, 0):
                    raise AssertionError("SetFilePointerEx input differs")
                offset = distance.value if hasattr(distance, "value") else int(distance)
                self.pointer = offset
                ctypes.cast(output, ctypes.POINTER(ctypes.c_int64)).contents.value = offset
                return 1

            def write_file(
                self,
                handle: int,
                source: object,
                count: int,
                written: object,
                overlapped: object,
            ) -> int:
                if handle != ledger_handle or overlapped is not None or self.pointer != len(self.file):
                    raise AssertionError("WriteFile is not one synchronous EOF append")
                raw = ctypes.string_at(source, count)
                self.file.extend(raw)
                self.pointer += count
                ctypes.cast(written, ctypes.POINTER(ctypes.c_uint32)).contents.value = count
                return 1

            def flush_file_buffers(self, handle: int) -> int:
                if handle != ledger_handle:
                    raise AssertionError("flush handle differs")
                return 1

            def read_file(
                self,
                handle: int,
                output: object,
                count: int,
                read: object,
                overlapped: object,
            ) -> int:
                if handle != ledger_handle or overlapped is not None:
                    raise AssertionError("ReadFile input differs")
                raw = bytes(self.file[self.pointer : self.pointer + count])
                ctypes.memmove(output, raw, len(raw))
                self.pointer += len(raw)
                ctypes.cast(read, ctypes.POINTER(ctypes.c_uint32)).contents.value = len(raw)
                return 1

            def close_handle(self, handle: int) -> int:
                self.close_calls.append(handle)
                return 1

            @staticmethod
            def last_error() -> int:
                return 0

        schema = json.loads(
            (
                ROOT
                / "stage_f_local_execution_binding_final_evidence_closure_correction_schema.json"
            ).read_bytes()
        )
        validator = ClosedSchemaValidator(schema)
        tick = 0

        def clock() -> str:
            nonlocal tick
            tick += 1
            return f"2026-08-31T12:00:00.{tick:06d}Z"

        def embedded_digest(record: dict[str, object], field: str) -> None:
            record[field] = hashlib.sha256(
                canonical_bytes({key: value for key, value in record.items() if key != field})
            ).hexdigest()

        def append_ticket(
            *,
            root_identity: dict[str, str],
            path_identity: dict[str, str],
            previous_identity: dict[str, str] | None,
            record_role: str,
            record_identity: dict[str, str],
            expected_offset: int,
        ) -> dict[str, object]:
            ticket: dict[str, object] = {
                "schema": "stage_f_ledger_append_ticket/v1",
                "root_protection_epoch_identity": root_identity,
                "ledger_file_path_identity": path_identity,
                "ledger_file_volume_serial_number_uint64": volume_serial,
                "ledger_file_id_128": file_id_raw.hex(),
                "previous_entry_identity": previous_identity,
                "actor_process_id": 10,
                "actor_thread_id": 20,
                "record_role": record_role,
                "record_identity": record_identity,
                "expected_append_start_offset": expected_offset,
                "issued_utc": "2026-08-31T12:00:00.000000Z",
                "expires_utc": "2026-08-31T12:00:00.999999Z",
                "single_use_required": True,
                "ticket_sha256": "",
            }
            embedded_digest(ticket, "ticket_sha256")
            return ticket

        apis = MockLedgerApis()
        backend = durability_module.StageFEvidenceLedgerBackend(
            ledger_path,
            validator.validate_definition,
            apis=apis,
            clock=clock,
            path_wchar_capacity=256,
        )
        create = backend.create_observation
        self.assertEqual(len(create), 76)
        self.assertEqual(
            apis.create_args,
            (
                ledger_path,
                0xC0000000,
                1,
                None,
                1,
                0x80200080,
                None,
            ),
        )
        root_identity = sha256_identity(
            "stage_f_root_protection_epoch/v1", {"synthetic": "root"}
        )
        genesis_record_identity = sha256_identity(
            "stage_f_execution_attempt_genesis/v1", {"synthetic": "attempt"}
        )
        genesis_ticket = append_ticket(
            root_identity=root_identity,
            path_identity=create["ledger_file_path_identity"],
            previous_identity=None,
            record_role="EXECUTION_ATTEMPT_GENESIS",
            record_identity=genesis_record_identity,
            expected_offset=0,
        )
        usn_sha = "2" * 64
        parent_sha = "3" * 64
        genesis: dict[str, object] = {
            "schema": "stage_f_evidence_ledger/v1",
            "entry_type": "GENESIS",
            "execution_attempt_genesis_identity": genesis_record_identity,
            "root_protection_epoch_identity": root_identity,
            "ordinal": 0,
            "previous_entry_identity": None,
            "record_role": "EXECUTION_ATTEMPT_GENESIS",
            "record_identity": genesis_record_identity,
            "published_file_id_128": "4" * 32,
            "published_byte_count": 1,
            "published_sha256": "5" * 64,
            "usn_range_sha256": usn_sha,
            "created_utc": "2026-08-31T12:00:00.000000Z",
            "ledger_sha256": "",
            "ledger_file_path_identity": create["ledger_file_path_identity"],
            "ledger_file_volume_serial_number_uint64": volume_serial,
            "ledger_file_id_128": file_id_raw.hex(),
            "ledger_handle_value_uint64": ledger_handle,
            "ledger_handle_continuously_retained": True,
            "ledger_create_observation": create,
            "entry_start_offset": 0,
            "entry_wire_byte_count": 1,
            "entry_wire_format": "CANONICAL_JSON_OBJECT_UTF8_THEN_SINGLE_LF",
            "append_ticket": genesis_ticket,
        }
        for _ in range(8):
            embedded_digest(genesis, "ledger_sha256")
            actual_count = len(canonical_bytes(genesis)) + 1
            if genesis["entry_wire_byte_count"] == actual_count:
                break
            genesis["entry_wire_byte_count"] = actual_count
        else:
            self.fail("genesis wire byte count did not converge")
        first_append = backend.append_entry(
            genesis,
            parent_watch_range_sha256=parent_sha,
            usn_range_sha256=usn_sha,
        )
        self.assertEqual(len(first_append), 123)
        first_wire = canonical_bytes(genesis) + b"\n"
        self.assertEqual(bytes(apis.file), first_wire)

        next_record_identity = sha256_identity(
            "stage_f_capacity_publication_observation/v1", {"synthetic": "record"}
        )
        next_ticket = append_ticket(
            root_identity=root_identity,
            path_identity=create["ledger_file_path_identity"],
            previous_identity=backend.head_identity,
            record_role="CAPACITY_PUBLICATION",
            record_identity=next_record_identity,
            expected_offset=len(first_wire),
        )
        next_parent_sha = "6" * 64
        next_usn_sha = "7" * 64
        next_entry: dict[str, object] = {
            "schema": "stage_f_evidence_ledger/v1",
            "entry_type": "ENTRY",
            "root_protection_epoch_identity": root_identity,
            "ordinal": 1,
            "previous_entry_identity": backend.head_identity,
            "mutation_ticket_identity": sha256_identity(
                "stage_f_authorized_mutation_ticket/v1", {"synthetic": "mutation"}
            ),
            "mutation_transaction_identity": sha256_identity(
                "stage_f_mutation_transaction/v1", {"synthetic": "transaction"}
            ),
            "record_role": "CAPACITY_PUBLICATION",
            "record_identity": next_record_identity,
            "published_file_id_128": "8" * 32,
            "published_byte_count": 2,
            "published_sha256": "9" * 64,
            "parent_watch_sha256": next_parent_sha,
            "usn_range_sha256": next_usn_sha,
            "created_utc": "2026-08-31T12:00:00.000000Z",
            "ledger_sha256": "",
            "ledger_file_path_identity": create["ledger_file_path_identity"],
            "ledger_file_volume_serial_number_uint64": volume_serial,
            "ledger_file_id_128": file_id_raw.hex(),
            "ledger_handle_value_uint64": ledger_handle,
            "ledger_handle_continuously_retained": True,
            "entry_wire_format": "CANONICAL_JSON_OBJECT_UTF8_THEN_SINGLE_LF",
            "append_ticket": next_ticket,
            "previous_entry_append_observation": first_append,
        }
        embedded_digest(next_entry, "ledger_sha256")
        second_append = backend.append_entry(
            next_entry,
            parent_watch_range_sha256=next_parent_sha,
            usn_range_sha256=next_usn_sha,
        )
        self.assertEqual(len(second_append), 123)
        self.assertEqual(
            bytes(apis.file), first_wire + canonical_bytes(next_entry) + b"\n"
        )
        self.assertEqual(second_append["append_start_offset"], len(first_wire))
        with self.assertRaisesRegex(BindingRefusal, "ticket was reused"):
            backend.append_entry(
                next_entry,
                parent_watch_range_sha256=next_parent_sha,
                usn_range_sha256=next_usn_sha,
            )
        self.assertEqual(apis.close_calls, [])
        with self.assertRaisesRegex(BindingRefusal, "must use explicit abort"):
            backend.release()
        release = backend.abort()
        self.assertEqual(release["close_disposition"], "REFUSED_ATTEMPT_ABORT")
        self.assertEqual(apis.close_calls, [ledger_handle])

    def test_raw_usn_backend_refuses_non_windows_without_injected_apis(self) -> None:
        from stage_f_binding import durability as durability_module

        volume = "\\\\?\\Volume{01234567-89ab-cdef-0123-456789abcdef}\\"
        with mock.patch.object(durability_module.sys, "platform", "linux"):
            with self.assertRaisesRegex(BindingRefusal, "requires Win32"):
                durability_module.StageFUsnJournalBackend(volume)

    def test_held_ledger_backend_refuses_non_windows_without_injected_apis(self) -> None:
        from stage_f_binding import durability as durability_module

        ledger_path = "\\\\?\\Volume{01234567-89ab-cdef-0123-456789abcdef}\\ledger.jsonl"
        with mock.patch.object(durability_module.sys, "platform", "linux"):
            with self.assertRaisesRegex(BindingRefusal, "requires Win32"):
                durability_module.StageFEvidenceLedgerBackend(
                    ledger_path, lambda definition, record: None
                )


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
        for command in (
            "source-artifacts",
            "readiness-chain",
            "record-chain",
            "control-state",
        ):
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
    def test_rejected_v1_controller_and_live_registry_are_closed(self) -> None:
        with self.assertRaisesRegex(
            BindingRefusal, "rejected v1 host-runtime controller"
        ):
            execute_host_runtime_composite_controller({})
        helpers = durability_module._WINDOWS_STAGE_F_PHASE_HELPERS
        self.assertEqual(set(helpers), set(durability_module._LIVE_PRESTART_OPERATION_NAMES))
        self.assertTrue(all(callable(helper) for helper in helpers.values()))
        self.assertNotIn(
            durability_module._windows_stage_f_backend_not_implemented,
            helpers.values(),
        )
        backend = WindowsStageFPrestartBackend()
        self.assertFalse(hasattr(backend, "start_scientific_container"))

    def test_live_material_absence_refuses_before_ledger_creation(self) -> None:
        state = durability_module._WindowsStageFControllerState({})
        state.root_active = True
        state.root_epoch = {"synthetic": "root"}
        state.validate_definition = lambda _definition, _record: None
        state.phase_materials = {}
        state.completed_live_phases = [
            "incept_fresh_attempt_root",
            "acquire_root_and_volume_epoch",
            "read_locked_authority_materials",
        ]
        state.control_records = [{"definition": "synthetic", "record": {}}]
        factory = mock.Mock()
        with self.assertRaisesRegex(BindingRefusal, "entry material is absent"):
            durability_module._windows_stage_f_create_held_ledger(
                controller_input={
                    "ledger_path": (
                        r"\\?\Volume{01234567-89ab-cdef-0123-456789abcdef}"
                        r"\attempt\ledger.jsonl"
                    ),
                    "_stage_f_ledger_backend_factory": factory,
                },
                state_token=state,
                control_records=tuple(state.control_records),
            )
        factory.assert_not_called()

    def test_v3_capacity_projection_is_exact_six_component_sum(self) -> None:
        projection = {
            "schema": "stage_f_capacity_usage_projection/v1",
            "primary_logical_output_bytes": 1,
            "independent_audit_copy_bytes": 2,
            "dynamic_growth_physical_write_bytes": 3,
            "checkpoint_and_write_overhead_bytes": 4,
            "temporary_archive_bytes": 5,
            "retained_evidence_bytes": 8 * 1073741824,
            "total_envelope_usage_bytes": 8 * 1073741824 + 15,
        }
        projection["projection_sha256"] = hashlib.sha256(
            canonical_bytes(projection)
        ).hexdigest()
        observed, identity = durability_module._validate_capacity_usage_projection(
            projection, "synthetic capacity projection"
        )
        self.assertEqual(
            observed["total_envelope_usage_bytes"], 8 * 1073741824 + 15
        )
        self.assertEqual(identity["kind"], "stage_f_capacity_usage_projection/v1")
        changed = copy.deepcopy(projection)
        changed["total_envelope_usage_bytes"] += 1
        changed["projection_sha256"] = hashlib.sha256(
            canonical_bytes(
                {key: value for key, value in changed.items() if key != "projection_sha256"}
            )
        ).hexdigest()
        with self.assertRaisesRegex(BindingRefusal, "six-component sum"):
            durability_module._validate_capacity_usage_projection(
                changed, "changed capacity projection"
            )

    def test_v3_non_scientific_mutation_ticket_has_no_route_authority(self) -> None:
        identity = {
            "kind": "stage_f_root_protection_epoch/v1",
            "value": "a" * 64,
            "sha256": "a" * 64,
        }
        ledger_identity = {
            "kind": "stage_f_evidence_ledger/v1",
            "value": "b" * 64,
            "sha256": "b" * 64,
        }
        ticket = {
            "schema": "stage_f_authorized_mutation_ticket/v1",
            "transaction_identity": {
                "kind": "stage_f_mutation_transaction/v1",
                "value": "c" * 64,
                "sha256": "c" * 64,
            },
            "operation": "INERT_CONTAINER_CREATE",
            "issued_utc": "2026-08-31T12:00:00Z",
            "expires_utc": "2026-08-31T12:01:00Z",
            "single_use_required": True,
            "scientific_mutation_authority_identity": None,
            "scientific_mutation_authority_projection": None,
            "root_protection_epoch_identity": identity,
            "ledger_mutation_transaction_identity": ledger_identity,
            "campaign_authorization_identity": None,
            "route_id": None,
            "ticket_watch_usn_ledger_join_kind": (
                "ROOT_EPOCH_TRANSACTION_TICKET_WATCH_USN_LEDGER_BIJECTION"
            ),
        }
        ticket["ticket_sha256"] = hashlib.sha256(canonical_bytes(ticket)).hexdigest()
        durability_module._validate_mutation_ticket_semantics(
            ticket, "synthetic non-scientific ticket"
        )
        changed = copy.deepcopy(ticket)
        changed["route_id"] = "RG-01"
        changed["ticket_sha256"] = hashlib.sha256(
            canonical_bytes(
                {key: value for key, value in changed.items() if key != "ticket_sha256"}
            )
        ).hexdigest()
        with self.assertRaisesRegex(BindingRefusal, "scientific authority"):
            durability_module._validate_mutation_ticket_semantics(
                changed, "changed non-scientific ticket"
            )

    def test_v3_start_capability_targets_exact_create_response_container_id(self) -> None:
        container_id = "d" * 64
        inert = {"container_id": container_id}
        inert["container_observation_sha256"] = hashlib.sha256(
            canonical_bytes(inert)
        ).hexdigest()
        inert_identity = {
            "kind": "stage_f_inert_container/v1",
            "value": inert["container_observation_sha256"],
            "sha256": inert["container_observation_sha256"],
        }
        request = (
            f"POST /containers/{container_id}/start HTTP/1.1\r\nHost: docker\r\n\r\n".encode(
                "ascii"
            )
        )
        capability = {
            "inert_container_identity": inert_identity,
            "container_id": container_id,
            "method": "POST",
            "endpoint": f"/containers/{container_id}/start",
            "request_bytes_base64": base64.b64encode(request).decode("ascii"),
            "request_sha256": hashlib.sha256(request).hexdigest(),
            "request_is_complete_http_wire": True,
            "request_constructed_not_sent": True,
            "start_call_invoked": False,
            "single_use": True,
        }
        capability["capability_sha256"] = hashlib.sha256(
            canonical_bytes(capability)
        ).hexdigest()
        capability_identity = {
            "kind": "stage_f_container_start_capability/v1",
            "value": capability["capability_sha256"],
            "sha256": capability["capability_sha256"],
        }
        root_identity = {
            "kind": "stage_f_root_protection_epoch/v1",
            "value": "a" * 64,
            "sha256": "a" * 64,
        }
        gate = {
            "inert_container_observation": inert,
            "inert_container_identity": inert_identity,
            "root_protection_epoch_identity": root_identity,
        }
        gate["gate_sha256"] = hashlib.sha256(canonical_bytes(gate)).hexdigest()
        intent = {
            "inert_container_observation": inert,
            "inert_container_identity": inert_identity,
            "container_start_capability": capability,
            "container_start_capability_identity": capability_identity,
            "scientific_launch_gate_identity": {
                "kind": "stage_f_scientific_launch_gate/v1",
                "value": gate["gate_sha256"],
                "sha256": gate["gate_sha256"],
            },
            "root_protection_epoch_identity": root_identity,
            "all_embedded_identities_and_container_bindings_reconcile": True,
            "capability_request_exactly_targets_intent_container": True,
        }
        with mock.patch.object(
            durability_module,
            "_validate_inert_container_observation",
            return_value=container_id,
        ):
            durability_module._validate_start_intent_container_links(intent, gate)
            changed = copy.deepcopy(intent)
            changed["container_start_capability"]["container_id"] = "f" * 64
            with self.assertRaises(BindingRefusal):
                durability_module._validate_start_intent_container_links(
                    changed, gate
                )

    def test_v3_root_watch_live_state_binds_each_pending_native_resource(self) -> None:
        watches = []
        pending = []
        for ordinal in (1, 2):
            watch = {
                "role": (
                    "ANCHOR_SELF_DIRECT"
                    if ordinal == 1
                    else "EXECUTION_ATTEMPT_ROOT_SUBTREE"
                ),
                "recursive": ordinal == 2,
                "directory_handle_value_uint64": 100 + ordinal,
                "buffer_base_address_uint64": 200 + ordinal,
                "buffer_capacity": 65536,
                "overlapped_address_uint64": 300 + ordinal,
                "event_handle_value_uint64": 400 + ordinal,
                "completion_bytes_output_address_uint64": 500 + ordinal,
                "notification_filter": 351,
            }
            watches.append(watch)
            pending.append(
                {
                    "watch_ordinal": ordinal,
                    "pending_cycle_ordinal": 1,
                    "role": watch["role"],
                    "directory_handle_value_uint64": watch[
                        "directory_handle_value_uint64"
                    ],
                    "buffer_base_address_uint64": watch["buffer_base_address_uint64"],
                    "buffer_capacity": 65536,
                    "overlapped_address_uint64": watch[
                        "overlapped_address_uint64"
                    ],
                    "event_handle_value_uint64": watch[
                        "event_handle_value_uint64"
                    ],
                    "completion_bytes_output_address_uint64": watch[
                        "completion_bytes_output_address_uint64"
                    ],
                    "notification_filter": 351,
                    "watch_subtree": watch["recursive"],
                    "request_pending": True,
                }
            )
        root = {
            "holder_process_id": 10,
            "holder_process_creation_filetime_uint64": 20,
            "watches": watches,
            "watch_count": 2,
        }
        root["epoch_sha256"] = hashlib.sha256(canonical_bytes(root)).hexdigest()
        root_identity = {
            "kind": "stage_f_root_protection_epoch/v1",
            "value": root["epoch_sha256"],
            "sha256": root["epoch_sha256"],
        }
        live = {
            "root_protection_epoch_identity": root_identity,
            "holder_process_id": 10,
            "holder_process_creation_filetime_uint64": 20,
            "completion_rows": [],
            "completion_row_count": 0,
            "completion_rows_complete_and_strictly_ordered": True,
            "watch_count": 2,
            "pending_watch_ordinals": [1, 2],
            "pending_cycle_ordinals": [1, 1],
            "counts_and_pending_cycles_reconcile": True,
            "all_pending_since_latest_issue_or_reissue": True,
            "all_acquired_watches_pending": True,
            "unmatched_protected_event_count": 0,
            "pending_watch_resources": pending,
            "pending_watch_resource_count": 2,
            "pending_resources_reconcile_acquisition_completion_and_latest_reissue": True,
        }
        durability_module._validate_root_watch_live_state_links(
            live, root, "synthetic root-watch live state"
        )
        changed = copy.deepcopy(live)
        changed["pending_watch_resources"][1]["buffer_base_address_uint64"] += 1
        with self.assertRaisesRegex(BindingRefusal, "substitutes"):
            durability_module._validate_root_watch_live_state_links(
                changed, root, "changed root-watch live state"
            )

    def test_v3_suspended_launch_validator_contains_all_typed_joins(self) -> None:
        source = inspect.getsource(
            durability_module._validate_suspended_validator_material
        )
        for required in (
            "durability_suspended_process_launch_attestation",
            "stage_f_host_validation_process_resume_capability",
            "stage_f_capacity_live_gate",
            "pre_resume_launch_attestation_sha256",
            "host_validation_process_resume_capability_identity",
            "capacity_live_gate_identity",
            "resume_input_thread_handle_value_uint64",
            "launch_attestation_capability_gate_and_resume_recomputed",
        ):
            self.assertIn(required, source)
        self.assertTrue(
            {
                "pre_resume_launch_attestation_sha256",
                "host_validation_process_resume_capability_identity",
                "capacity_live_gate_identity",
                "launch_attestation_capability_gate_and_resume_recomputed",
            }.issubset(durability_module._LAUNCH_FIELDS)
        )

    def test_locked_zipapp_route_remains_outcome_blind_static_code(self) -> None:
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
        with self.assertRaisesRegex(BindingRefusal, "image-attestation context"):
            with mock.patch("stage_f_binding.durability.sys.platform", "win32"):
                _orchestrator_create_process(
                    r"C:\synthetic\python.exe",
                    [r"C:\synthetic\python.exe", "-I"],
                    {
                        "executable_path_identity": {
                            "kind": "stage_f_private_path/v1",
                            "value": "a" * 64,
                            "sha256": "a" * 64,
                        }
                    },
                    phase="PRE_RESTART",
                    orchestrator_process={"process_id": 1},
                )


if __name__ == "__main__":
    unittest.main()
