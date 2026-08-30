"""Outcome-blind Stage F checkpoint and durability mechanics.

This module contains no scientific callback, runner, configuration loader, or
random-number source.  Its filesystem functions operate only on caller-supplied
bytes and fresh paths.  POSIX operations are available solely for synthetic CI
controls; an admissible Stage F receipt remains bound to the authority's exact
Windows observations and is checked as such by :func:`validate_durability_receipt`.
"""

from __future__ import annotations

import base64
import ctypes
import errno
import hashlib
import os
import re
import stat
import struct
import subprocess
import sys
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path, PureWindowsPath
from types import MappingProxyType
from typing import Any, Callable, Mapping, Sequence

from .canonical import (
    BindingRefusal,
    assert_zero_science_counters,
    canonical_bytes,
    sha256_hex,
    sha256_identity,
    strict_loads,
    verify_embedded_digest,
)

__all__ = (
    "BindingRefusal",
    "ZERO_SCIENCE_COUNTERS",
    "DURABILITY_ACTIONS",
    "validate_no_science_counters",
    "validate_durability_action_trace",
    "validate_durability_receipt",
    "validate_live_storage_inventory",
    "validate_live_volume_capacity",
    "execute_host_runtime_composite_controller",
    "execute_durability_probe_phase",
    "write_checkpoint",
    "atomic_publish",
    "verify_checkpoint_hash",
    "recover_checkpoint",
)


_SCIENCE_COUNTER_NAMES = (
    "model_execution_count",
    "trajectory_execution_count",
    "runner_import_count",
    "gate_execution_count",
    "transform_execution_count",
    "benchmark_execution_count",
    "simulation_execution_count",
    "stochastic_draw_count",
    "registered_configuration_count",
    "outcome_inspection_count",
    "result_count",
    "figure_count",
    "book_count",
    "release_action_count",
    "publication_action_count",
)
ZERO_SCIENCE_COUNTERS = MappingProxyType(
    {name: 0 for name in _SCIENCE_COUNTER_NAMES}
)

_ACTION_SPECS = (
    (1, "CREATE_FRESH_TEMPORARY", "EMPTY", "EMPTY", "ZERO", "TERMINATED_PROBE_PROCESS"),
    (2, "WRITE_SYNTHETIC_PAYLOAD", "EMPTY", "SYNTHETIC_PAYLOAD", "SYNTHETIC_PAYLOAD", "TERMINATED_PROBE_PROCESS"),
    (3, "FLUSH_FILE_BUFFERS", "SYNTHETIC_PAYLOAD", "SYNTHETIC_PAYLOAD", "SYNTHETIC_PAYLOAD", "TERMINATED_PROBE_PROCESS"),
    (4, "CLOSE_TEMPORARY_HANDLE", "SYNTHETIC_PAYLOAD", "SYNTHETIC_PAYLOAD", "SYNTHETIC_PAYLOAD", "TERMINATED_PROBE_PROCESS"),
    (5, "ATOMIC_PUBLISH_FRESH_VERSIONED_FINAL", "SYNTHETIC_PAYLOAD", "PUBLISHED_FINAL", "SYNTHETIC_PAYLOAD", "TERMINATED_PROBE_PROCESS"),
    (6, "CONFIRM_WRITE_THROUGH_TARGET_PARENT_METADATA_DURABILITY", "PUBLISHED_FINAL", "PUBLISHED_FINAL", "SYNTHETIC_PAYLOAD", "TERMINATED_PROBE_PROCESS"),
    (7, "TERMINATE_PROBE_PROCESS", "PUBLISHED_FINAL", "PUBLISHED_FINAL", "SYNTHETIC_PAYLOAD", "TERMINATED_PROBE_PROCESS"),
    (8, "START_FRESH_PROBE_PROCESS", "PUBLISHED_FINAL", "PUBLISHED_FINAL", "SYNTHETIC_PAYLOAD", "RESUMED_PROBE_PROCESS"),
    (9, "REOPEN_FINAL_READ_ONLY", "PUBLISHED_FINAL", "PUBLISHED_FINAL", "SYNTHETIC_PAYLOAD", "RESUMED_PROBE_PROCESS"),
    (10, "REREAD_COMPLETE_FINAL", "PUBLISHED_FINAL", "POST_RESTART_REREAD", "POST_RESTART_REREAD", "RESUMED_PROBE_PROCESS"),
    (11, "RECOMPUTE_FINAL_SHA256", "POST_RESTART_REREAD", "POST_RESTART_REREAD", "POST_RESTART_REREAD", "RESUMED_PROBE_PROCESS"),
    (12, "PRESENT_CORRUPT_FINAL_FIXTURE", "PUBLISHED_FINAL", "CORRUPT_FIXTURE", "CORRUPT_FIXTURE", "RESUMED_PROBE_PROCESS"),
    (13, "REFUSE_CORRUPT_FINAL", "CORRUPT_FIXTURE", "CORRUPT_FIXTURE", "CORRUPT_FIXTURE", "RESUMED_PROBE_PROCESS"),
    (14, "PRESENT_ORPHAN_PARTIAL_FIXTURE", "PUBLISHED_FINAL", "ORPHAN_PARTIAL", "ORPHAN_PARTIAL", "RESUMED_PROBE_PROCESS"),
    (15, "REFUSE_ORPHAN_PARTIAL", "ORPHAN_PARTIAL", "ORPHAN_PARTIAL", "ORPHAN_PARTIAL", "RESUMED_PROBE_PROCESS"),
    (16, "RECOVER_LAST_VERIFIED_DURABLE_FINAL", "LAST_VERIFIED_DURABLE_CHECKPOINT", "RECOVERED_FINAL", "SYNTHETIC_PAYLOAD", "RESUMED_PROBE_PROCESS"),
    (17, "RECOMPUTE_RECOVERED_SHA256", "RECOVERED_FINAL", "RECOVERED_FINAL", "SYNTHETIC_PAYLOAD", "RESUMED_PROBE_PROCESS"),
)
DURABILITY_ACTIONS = tuple(row[1] for row in _ACTION_SPECS)

_EMPTY_SHA256 = hashlib.sha256(b"").hexdigest()
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_UTC_RE = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?Z$"
)
_UINT32_MAX = (1 << 32) - 1
_UINT64_MAX = (1 << 64) - 1
_INVALID_HANDLE_VALUE = _UINT64_MAX

_ACTION_FIELDS = frozenset(
    {
        "ordinal",
        "action",
        "observed_utc",
        "input_sha256",
        "input_hash_role",
        "output_sha256",
        "output_hash_role",
        "observed_byte_count",
        "byte_count_role",
        "actor_process_role",
        "actor_process_id",
        "actor_process_creation_filetime_uint64",
        "os_result_code",
        "status",
    }
)

_RECEIPT_FIELDS = frozenset(
    """
    schema filesystem_identity durability_policy_identity restart_policy_identity
    binding_validator_identity execution_environment_policy_identity
    host_validation_runtime_identity host_runtime_lock_acquisition_preimage
    host_runtime_lock_acquisition_sha256 host_runtime_lock_release_observation
    orchestrator_probe_invocation_preimage terminated_probe_invocation_preimage
    resumed_probe_invocation_preimage orchestrator_artifact_lock_observation
    terminated_artifact_lock_observation resumed_artifact_lock_observation
    synthetic_payload_identity temporary_path_identity final_path_identity
    directory_target_identity storage_capacity_snapshot_identity
    probe_started_utc probe_completed_utc synthetic_payload_byte_count
    synthetic_payload_sha256 published_final_sha256
    post_restart_reread_byte_count post_restart_reread_sha256
    corrupt_fixture_byte_count corrupt_fixture_sha256 orphan_partial_byte_count
    orphan_partial_sha256 last_verified_durable_checkpoint_sha256
    recovered_final_sha256 ordered_actions action_count
    atomic_publication_observation directory_durability_observation
    restart_observation recovery_disposition same_volume file_flush_completed
    file_durability_primitive directory_durability_completed
    directory_durability_primitive atomic_publication_completed
    restart_reread_completed content_hash_reconciled corrupt_final_refused
    orphan_partial_refused last_good_recovery_completed observed_free_bytes
    reserved_envelope_bytes disposition scientific_counters receipt_sha256
    """.split()
)

_ATOMIC_FIELDS = frozenset(
    """
    schema primitive raw_flags movefile_write_through_flag_set
    movefile_replace_existing_flag_set source_path_identity target_path_identity
    same_volume target_exists_before_call target_nonexistence_observation
    call_returned_nonzero source_absent_after_call target_present_after_call
    target_created_once target_overwrite_attempt_count
    """.split()
)

_DIRECTORY_FIELDS = frozenset(
    """
    schema actor_process_id actor_process_creation_filetime_uint64 actor_thread_id
    operations_serialized evidence_source atomic_publication_observation_sha256
    primitive raw_flags movefile_write_through_flag_set
    movefile_replace_existing_flag_set source_path_identity
    published_final_path_identity target_parent_path_identity final_open_api
    final_open_path_identity final_open_desired_access final_open_share_mode
    final_open_security_attributes final_open_creation_disposition
    final_open_flags_and_attributes final_open_handle_value_uint64
    final_open_returned_valid final_open_completed_utc path_buffer_allocation_api
    path_buffer_requested_base_pointer path_buffer_byte_count
    path_buffer_allocation_type path_buffer_protection
    path_buffer_base_address_uint64 path_buffer_wchar_capacity
    path_buffer_zero_initialized path_buffer_allocated_utc final_path_query_api
    final_path_query_input_handle_value_uint64
    final_path_query_output_buffer_address_uint64 final_path_query_wchar_capacity
    final_path_query_raw_flags final_path_query_returned_length_uint32
    final_path_query_succeeded resolved_final_path_identity
    final_path_query_completed_utc target_parent_derivation_api
    target_parent_derivation_input_buffer_address_uint64
    target_parent_derivation_wchar_capacity target_parent_derivation_hresult
    target_parent_resolution_succeeded target_parent_derivation_completed_utc
    final_close_api final_close_input_handle_value_uint64
    final_close_returned_nonzero final_handle_closed_once final_handle_closed_utc
    path_buffer_free_api path_buffer_free_input_address_uint64
    path_buffer_free_size path_buffer_free_type path_buffer_free_returned_nonzero
    path_buffer_freed_once path_buffer_freed_utc same_volume
    call_returned_nonzero move_completed_on_disk_before_return
    normalized_os_result_code observation_utc
    """.split()
)

_PROCESS_FIELDS = frozenset(
    """
    process_id creation_filetime_uint64 executable_path_identity executable_sha256
    command_line_sha256 invocation_sha256 self_command_line_observation_api
    locked_bootstrap_verified_invocation
    """.split()
)

_RESTART_FIELDS = frozenset(
    """
    orchestrator_process terminated_process resumed_process process_identity_api
    terminated_process_launch_observation resumed_process_launch_observation
    terminated_wait_api terminated_wait_input_process_handle_value_uint64
    terminated_wait_started_utc terminated_wait_timeout_milliseconds
    terminated_wait_result terminated_wait_result_raw terminated_query_actor_process_id
    terminated_query_actor_thread_id terminated_query_calls_serialized
    terminated_get_exit_code_api terminated_get_exit_code_started_utc
    terminated_get_exit_code_input_process_handle_value_uint64
    terminated_get_exit_code_output_observation terminated_get_exit_code_returned_nonzero
    terminated_process_exit_code terminated_get_exit_code_returned_utc
    terminated_get_exit_code_completed_utc terminated_get_process_times_api
    terminated_get_process_times_started_utc
    terminated_get_process_times_input_process_handle_value_uint64
    terminated_get_process_times_creation_output_observation
    terminated_get_process_times_exit_output_observation
    terminated_get_process_times_kernel_output_observation
    terminated_get_process_times_user_output_observation
    terminated_get_process_times_output_intervals_pairwise_disjoint
    terminated_get_process_times_returned_nonzero
    terminated_process_creation_filetime_uint64 terminated_process_exit_filetime_uint64
    terminated_process_kernel_filetime_uint64 terminated_process_user_filetime_uint64
    terminated_get_process_times_returned_utc terminated_get_process_times_completed_utc
    terminated_process_exit_utc terminated_wait_completed_utc
    terminated_process_close_api terminated_process_close_started_utc
    terminated_process_close_input_handle_value_uint64
    terminated_process_close_returned_nonzero terminated_process_handle_closed_utc
    challenge_path_identity challenge_preimage challenge_sha256
    challenge_publication_observation acknowledgement_path_identity
    acknowledgement_preimage acknowledgement_sha256 acknowledgement_write_observation
    resumed_process_acknowledged_exact_challenge resumed_wait_api
    resumed_wait_input_process_handle_value_uint64 resumed_wait_started_utc
    resumed_wait_timeout_milliseconds resumed_wait_result resumed_wait_result_raw
    resumed_query_actor_process_id resumed_query_actor_thread_id
    resumed_query_calls_serialized resumed_get_exit_code_api
    resumed_get_exit_code_started_utc resumed_get_exit_code_input_process_handle_value_uint64
    resumed_get_exit_code_output_observation resumed_get_exit_code_returned_nonzero
    resumed_process_exit_code resumed_get_exit_code_returned_utc
    resumed_get_exit_code_completed_utc resumed_get_process_times_api
    resumed_get_process_times_started_utc
    resumed_get_process_times_input_process_handle_value_uint64
    resumed_get_process_times_creation_output_observation
    resumed_get_process_times_exit_output_observation
    resumed_get_process_times_kernel_output_observation
    resumed_get_process_times_user_output_observation
    resumed_get_process_times_output_intervals_pairwise_disjoint
    resumed_get_process_times_returned_nonzero resumed_process_creation_filetime_uint64
    resumed_process_exit_filetime_uint64 resumed_process_kernel_filetime_uint64
    resumed_process_user_filetime_uint64 resumed_get_process_times_returned_utc
    resumed_get_process_times_completed_utc resumed_process_exit_utc
    resumed_wait_completed_utc resumed_process_close_api
    resumed_process_close_started_utc resumed_process_close_input_handle_value_uint64
    resumed_process_close_returned_nonzero resumed_process_handle_closed_utc
    launch_utc handshake_completed_utc restart_utc
    """.split()
)

_LAUNCH_FIELDS = frozenset(
    """
    schema phase launch_actor_process_id launch_actor_thread_id
    launch_and_thread_close_serialized launch_api application_name_path_identity
    command_line_buffer_base_address_uint64 command_line_buffer_exclusive_end_address_uint64
    command_line_buffer_wchar_capacity command_line_buffer_byte_count_including_terminal_nul
    command_line_base64 command_line_utf16_code_unit_count command_line_terminal_nul_present
    command_line_mutable_buffer command_line_buffer_call_time_bytes_base64
    command_line_buffer_call_time_sha256 command_line_hash_input_address_uint64
    command_line_hash_input_byte_count command_line_hash_completed_utc
    process_security_attributes thread_security_attributes inherit_handles
    raw_creation_flags environment_pointer current_directory_pointer
    startup_info_address_uint64 startup_info_exclusive_end_address_uint64
    startup_info_byte_count startup_info_zero_initialized_before_cb_assignment
    startup_info_cb startup_info_call_time_bytes_base64 startup_info_call_time_sha256
    startup_info_hash_input_address_uint64 startup_info_hash_input_byte_count
    startup_info_hash_completed_utc startup_info_reserved_pointer
    startup_info_desktop_pointer startup_info_title_pointer startup_info_x startup_info_y
    startup_info_x_size startup_info_y_size startup_info_x_count_chars
    startup_info_y_count_chars startup_info_fill_attribute startup_info_dwflags
    startup_info_show_window startup_info_standard_input startup_info_standard_output
    startup_info_standard_error startup_info_reserved2_byte_count startup_info_reserved2_pointer
    process_information_address_uint64 process_information_exclusive_end_address_uint64
    process_information_byte_count process_information_zero_initialized_before_call
    process_information_input_bytes_base64 process_information_input_sha256
    process_information_input_hash_address_uint64 process_information_input_hash_byte_count
    process_information_input_hash_completed_utc process_information_output_bytes_base64
    process_information_output_sha256 process_information_output_hash_address_uint64
    process_information_output_hash_byte_count process_information_output_hash_completed_utc
    create_process_input_images_unchanged_from_hash_through_call_entry
    create_process_memory_intervals_nonoverflowing
    create_process_memory_intervals_pairwise_disjoint
    create_process_memory_intervals_live_through_return
    process_information_interval_live_through_output_hash create_process_started_utc
    create_process_returned_nonzero create_process_completed_utc
    process_handle_value_uint64 thread_handle_value_uint64 returned_handles_distinct
    process_id thread_id thread_close_api thread_close_started_utc
    thread_close_input_handle_value_uint64 thread_close_returned_nonzero
    thread_handle_closed_utc process_handle_retained_after_launch launch_utc
    """.split()
)

_OUTPUT_FIELDS = frozenset(
    """
    schema base_address_uint64 exclusive_end_address_uint64 byte_count
    interval_nonoverflowing input_bytes_base64 input_sha256
    input_hash_input_address_uint64 input_hash_input_byte_count
    input_hash_completed_utc output_bytes_base64 output_sha256
    output_hash_input_address_uint64 output_hash_input_byte_count
    output_hash_completed_utc live_through_call_return live_through_output_hash
    """.split()
)

_INVOCATION_FIELDS = frozenset(
    """
    schema phase binding_validator_identity execution_environment_policy_identity
    host_validation_runtime_identity host_runtime_lock_acquisition_sha256
    bootstrap_source_path bootstrap_git_row bootstrap_source_byte_count
    bootstrap_source_utf8_base64 executable_path_identity
    validator_zipapp_path_identity validator_zipapp_byte_count
    validator_zipapp_sha256 invocation_preimage_path_identity
    restart_challenge_path_identity restart_challenge_sha256
    acknowledgement_path_identity command_schema command_line_construction
    command_line_encoding command_line_base64 command_line_utf16_code_unit_count
    entrypoint_mode isolated_mode network_access_permitted scientific_counters
    """.split()
)

_ARTIFACT_LOCK_FIELDS = frozenset(
    """
    schema actor_process_role actor_process_id
    actor_process_creation_filetime_uint64 binding_validator_identity
    host_validation_runtime_identity invocation_sha256 artifact_path_identity
    expected_byte_count expected_sha256 open_api desired_access share_mode
    security_attributes creation_disposition flags_and_attributes handle_valid
    artifact_handle_value_uint64 resolved_path_api
    resolved_path_query_handle_value_uint64 resolved_path_identity
    file_id_query_api file_id_query_handle_value_uint64 volume_serial_number
    file_id_128 file_standard_info_query_api
    file_standard_info_query_handle_value_uint64 number_of_links delete_pending
    directory file_attribute_tag_query_api
    file_attribute_tag_query_handle_value_uint64 raw_file_attributes reparse_tag
    read_api read_input_handle_value_uint64 read_from_held_handle
    observed_byte_count observed_sha256 lock_acquired_utc
    validator_entrypoint_loaded_utc close_api close_input_handle_value_uint64
    close_returned_nonzero handle_closed_utc lock_released_utc
    write_share_permitted delete_share_permitted
    lock_held_from_before_zipapp_read_until_after_zipapp_return status lock_sha256
    """.split()
)

_CONTROL_WRITE_FIELDS = frozenset(
    """
    schema content_role actor_process_id actor_thread_id operations_serialized
    actor_process_creation_filetime_uint64 target_path_identity
    target_nonexistence_observation create_api desired_access share_mode
    security_attributes creation_disposition flags_and_attributes handle_valid
    created_handle_value_uint64 create_started_utc create_completed_utc write_api
    write_input_handle_value_uint64 write_buffer_base_address_uint64
    write_buffer_exclusive_end_address_uint64 write_buffer_byte_count
    write_buffer_call_time_bytes_base64 write_buffer_call_time_sha256
    write_buffer_interval_nonoverflowing
    write_buffer_live_and_unchanged_through_return
    write_buffer_hash_input_address_uint64 write_buffer_hash_input_byte_count
    write_buffer_hash_completed_utc write_bytes_written_output_observation
    write_input_and_output_intervals_disjoint write_started_utc
    write_overlapped_pointer write_returned_nonzero written_byte_count
    written_sha256 write_completed_utc flush_api flush_started_utc
    flush_input_handle_value_uint64 flush_returned_nonzero flush_completed_utc
    close_api close_started_utc close_input_handle_value_uint64
    close_returned_nonzero close_completed_utc handle_closed_once
    target_created_once
    """.split()
)

_CHALLENGE_PUBLICATION_FIELDS = frozenset(
    """
    schema actor_process_id actor_process_creation_filetime_uint64
    temporary_write_observation atomic_publication_observation
    directory_durability_observation published_path_identity
    published_byte_count published_sha256 completed_before_launch
    """.split()
)

_SECURITY_LIFECYCLE_FIELDS = frozenset(
    """
    security_query_api security_information_mask security_query_handle_value_uint64
    security_query_result_code security_descriptor_address_uint64
    security_descriptor_validation_api security_descriptor_validation_input_address_uint64
    security_descriptor_validation_returned_nonzero security_descriptor_control_api
    security_descriptor_control_input_address_uint64
    security_descriptor_control_returned_nonzero security_descriptor_control_uint16
    security_descriptor_self_relative_control_mask security_descriptor_revision_uint32
    security_descriptor_self_relative security_descriptor_length_api
    security_descriptor_length_input_address_uint64 security_descriptor_byte_count
    security_descriptor_hash_input_address_uint64 security_descriptor_hash_input_byte_count
    security_descriptor_sha256 security_query_completed_utc security_descriptor_hashed_utc
    security_descriptor_free_api security_descriptor_free_input_address_uint64
    security_descriptor_free_called_once security_descriptor_free_result
    security_descriptor_freed_utc
    """.split()
)

_HOST_RELEASE_FIELDS = frozenset(
    """
    schema host_runtime_lock_acquisition_sha256 lock_holder_process_id
    lock_holder_process_creation_filetime_uint64
    lock_holder_process_identity_equals_acquisition locked_validator_processes
    last_validator_process_returned_utc protection_epoch_ended_utc
    release_started_utc ordered_runtime_change_watch_release_rows
    runtime_change_watch_release_count all_runtime_change_watches_released_utc
    ordered_runtime_path_anchor_release_rows runtime_path_anchor_release_count
    ordered_runtime_file_release_rows runtime_file_release_count
    release_completed_utc
    any_retained_anchor_watch_or_file_handle_released_before_all_validator_processes_returned
    complete_acquisition_projection_remeasured all_handles_closed_once
    scientific_counters
    """.split()
)


def _refuse(message: str) -> None:
    raise BindingRefusal(message)


def _mapping(value: Any, label: str) -> dict[str, Any]:
    if type(value) is not dict:
        _refuse(f"{label} must be an exact object")
    return value


def _exact_fields(value: Mapping[str, Any], expected: frozenset[str], label: str) -> None:
    actual = frozenset(value)
    if actual != expected:
        _refuse(
            f"{label} fields differ; missing={sorted(expected - actual)!r} "
            f"extra={sorted(actual - expected)!r}"
        )


def _uint(value: Any, bits: int, label: str, *, positive: bool = False) -> int:
    if type(value) is not int:
        _refuse(f"{label} must be an integer")
    lower = 1 if positive else 0
    maximum = (1 << bits) - 1
    if value < lower or value > maximum:
        _refuse(f"{label} is outside uint{bits}")
    return value


def _handle(value: Any, label: str) -> int:
    result = _uint(value, 64, label, positive=True)
    if result == _INVALID_HANDLE_VALUE:
        _refuse(f"{label} is INVALID_HANDLE_VALUE")
    return result


def _sha256(value: Any, label: str) -> str:
    if type(value) is not str or _SHA256_RE.fullmatch(value) is None:
        _refuse(f"{label} must be a lowercase SHA-256")
    return value


def _utc(value: Any, label: str) -> datetime:
    if type(value) is not str or _UTC_RE.fullmatch(value) is None:
        _refuse(f"{label} must be a canonical UTC timestamp")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise BindingRefusal(f"{label} is not a real UTC timestamp") from exc
    if parsed.tzinfo != timezone.utc:
        _refuse(f"{label} is not UTC")
    return parsed


def _ordered_times(record: Mapping[str, Any], fields: Sequence[str], label: str) -> None:
    values = [_utc(record[field], f"{label}.{field}") for field in fields]
    if values != sorted(values):
        _refuse(f"{label} timestamps are not nondecreasing: {tuple(fields)!r}")


def _strict_base64(value: Any, label: str) -> bytes:
    if type(value) is not str or not value:
        _refuse(f"{label} must be nonempty standard padded base64")
    try:
        raw = base64.b64decode(value.encode("ascii"), validate=True)
    except (UnicodeEncodeError, ValueError) as exc:
        raise BindingRefusal(f"{label} is not strict standard base64") from exc
    if base64.b64encode(raw).decode("ascii") != value:
        _refuse(f"{label} is not canonical padded base64")
    return raw


def _identity(value: Any, kind: str, label: str) -> dict[str, Any]:
    record = _mapping(value, label)
    _exact_fields(record, frozenset({"kind", "value", "sha256"}), label)
    if record["kind"] != kind:
        _refuse(f"{label}.kind differs")
    digest = _sha256(record["value"], f"{label}.value")
    if record["sha256"] != digest:
        _refuse(f"{label} value and sha256 differ")
    return record


def _same_identity(left: Any, right: Any, label: str) -> None:
    if left != right:
        _refuse(f"{label} identity projection differs")


def validate_no_science_counters(counters: Mapping[str, Any]) -> None:
    """Require the exact fifteen authority counters, all integer zero."""

    record = _mapping(counters, "scientific_counters")
    _exact_fields(record, frozenset(_SCIENCE_COUNTER_NAMES), "scientific_counters")
    for name in _SCIENCE_COUNTER_NAMES:
        if type(record[name]) is not int or record[name] != 0:
            _refuse(f"scientific counter is nonzero or non-integer: {name}")
    # Keep the canonical half and this independently spelled check in agreement.
    assert_zero_science_counters(record)


def validate_durability_action_trace(
    ordered_actions: Sequence[Mapping[str, Any]],
    *,
    receipt: Mapping[str, Any] | None = None,
) -> None:
    """Validate the frozen seventeen action rows and optional receipt projections."""

    if type(ordered_actions) not in (list, tuple) or len(ordered_actions) != 17:
        _refuse("durability action trace must contain exactly seventeen rows")
    started = completed = None
    hashes: dict[str, str] | None = None
    counts: dict[str, int] | None = None
    actors: dict[str, tuple[int, int]] | None = None
    if receipt is not None:
        receipt = _mapping(receipt, "receipt")
        started = _utc(receipt["probe_started_utc"], "probe_started_utc")
        completed = _utc(receipt["probe_completed_utc"], "probe_completed_utc")
        if started > completed:
            _refuse("probe timestamps are reversed")
        hashes = {
            "EMPTY": _EMPTY_SHA256,
            "SYNTHETIC_PAYLOAD": receipt["synthetic_payload_sha256"],
            "PUBLISHED_FINAL": receipt["published_final_sha256"],
            "POST_RESTART_REREAD": receipt["post_restart_reread_sha256"],
            "CORRUPT_FIXTURE": receipt["corrupt_fixture_sha256"],
            "ORPHAN_PARTIAL": receipt["orphan_partial_sha256"],
            "LAST_VERIFIED_DURABLE_CHECKPOINT": receipt[
                "last_verified_durable_checkpoint_sha256"
            ],
            "RECOVERED_FINAL": receipt["recovered_final_sha256"],
        }
        counts = {
            "ZERO": 0,
            "SYNTHETIC_PAYLOAD": receipt["synthetic_payload_byte_count"],
            "POST_RESTART_REREAD": receipt["post_restart_reread_byte_count"],
            "CORRUPT_FIXTURE": receipt["corrupt_fixture_byte_count"],
            "ORPHAN_PARTIAL": receipt["orphan_partial_byte_count"],
        }
        restart = _mapping(receipt["restart_observation"], "restart_observation")
        terminated = _mapping(restart["terminated_process"], "terminated_process")
        resumed = _mapping(restart["resumed_process"], "resumed_process")
        actors = {
            "TERMINATED_PROBE_PROCESS": (
                terminated["process_id"],
                terminated["creation_filetime_uint64"],
            ),
            "RESUMED_PROBE_PROCESS": (
                resumed["process_id"],
                resumed["creation_filetime_uint64"],
            ),
        }

    prior_time: datetime | None = None
    for row_value, spec in zip(ordered_actions, _ACTION_SPECS, strict=True):
        row = _mapping(row_value, f"durability action {spec[0]}")
        _exact_fields(row, _ACTION_FIELDS, f"durability action {spec[0]}")
        ordinal, action, input_role, output_role, count_role, actor_role = spec
        expected = {
            "ordinal": ordinal,
            "action": action,
            "input_hash_role": input_role,
            "output_hash_role": output_role,
            "byte_count_role": count_role,
            "actor_process_role": actor_role,
            "status": "PASS",
        }
        for field, wanted in expected.items():
            if row[field] != wanted:
                _refuse(f"durability action {ordinal} has wrong {field}")
        _sha256(row["input_sha256"], f"action {ordinal} input_sha256")
        _sha256(row["output_sha256"], f"action {ordinal} output_sha256")
        _uint(row["observed_byte_count"], 64, f"action {ordinal} byte count")
        _uint(row["os_result_code"], 64, f"action {ordinal} OS result")
        _uint(row["actor_process_id"], 32, f"action {ordinal} PID", positive=True)
        _uint(
            row["actor_process_creation_filetime_uint64"],
            64,
            f"action {ordinal} creation FILETIME",
            positive=True,
        )
        observed = _utc(row["observed_utc"], f"action {ordinal} observed_utc")
        if prior_time is not None and observed < prior_time:
            _refuse("durability action timestamps are not ordered")
        prior_time = observed
        if started is not None and not (started <= observed <= completed):
            _refuse(f"durability action {ordinal} is outside the probe interval")
        if hashes is not None:
            if row["input_sha256"] != hashes[input_role]:
                _refuse(f"durability action {ordinal} input hash projection differs")
            if row["output_sha256"] != hashes[output_role]:
                _refuse(f"durability action {ordinal} output hash projection differs")
            if row["observed_byte_count"] != counts[count_role]:
                _refuse(f"durability action {ordinal} byte-count projection differs")
            if (
                row["actor_process_id"],
                row["actor_process_creation_filetime_uint64"],
            ) != actors[actor_role]:
                _refuse(f"durability action {ordinal} actor projection differs")
        if ordinal == 6 and row["os_result_code"] != 0:
            _refuse("durability action 6 must carry normalized OS result zero")


def _validate_atomic_publication(record_value: Any) -> dict[str, Any]:
    record = _mapping(record_value, "atomic_publication_observation")
    _exact_fields(record, _ATOMIC_FIELDS, "atomic_publication_observation")
    constants = {
        "schema": "stage_f_atomic_publication_observation/v1",
        "primitive": "MoveFileExW",
        "raw_flags": 8,
        "movefile_write_through_flag_set": True,
        "movefile_replace_existing_flag_set": False,
        "same_volume": True,
        "target_exists_before_call": False,
        "target_nonexistence_observation": (
            "GetFileAttributesW_INVALID_FILE_ATTRIBUTES_ERROR_FILE_NOT_FOUND"
        ),
        "call_returned_nonzero": True,
        "source_absent_after_call": True,
        "target_present_after_call": True,
        "target_created_once": True,
        "target_overwrite_attempt_count": 0,
    }
    for field, wanted in constants.items():
        if type(wanted) is bool:
            if record[field] is not wanted:
                _refuse(f"atomic publication {field} differs")
        elif record[field] != wanted:
            _refuse(f"atomic publication {field} differs")
    _identity(record["source_path_identity"], "stage_f_private_path/v1", "atomic source")
    _identity(record["target_path_identity"], "stage_f_private_path/v1", "atomic target")
    if record["source_path_identity"] == record["target_path_identity"]:
        _refuse("atomic source and target identities must differ")
    return record


def _validate_directory_durability(
    record_value: Any,
    atomic: Mapping[str, Any],
    *,
    actor_process: Mapping[str, Any],
    evidence_source: str,
    expected_observation_utc: str | None,
) -> None:
    record = _mapping(record_value, "directory_durability_observation")
    _exact_fields(record, _DIRECTORY_FIELDS, "directory_durability_observation")
    constants = {
        "schema": "stage_f_directory_durability_observation/v1",
        "operations_serialized": True,
        "evidence_source": evidence_source,
        "primitive": "MoveFileExW",
        "raw_flags": 8,
        "movefile_write_through_flag_set": True,
        "movefile_replace_existing_flag_set": False,
        "final_open_api": "CreateFileW",
        "final_open_desired_access": 128,
        "final_open_share_mode": 7,
        "final_open_security_attributes": "NULL",
        "final_open_creation_disposition": 3,
        "final_open_flags_and_attributes": 2097152,
        "final_open_returned_valid": True,
        "path_buffer_allocation_api": "VirtualAlloc",
        "path_buffer_requested_base_pointer": "NULL",
        "path_buffer_byte_count": 65536,
        "path_buffer_allocation_type": 12288,
        "path_buffer_protection": 4,
        "path_buffer_wchar_capacity": 32768,
        "path_buffer_zero_initialized": True,
        "final_path_query_api": "GetFinalPathNameByHandleW",
        "final_path_query_wchar_capacity": 32768,
        "final_path_query_raw_flags": 1,
        "final_path_query_succeeded": True,
        "target_parent_derivation_api": (
            "GetFinalPathNameByHandleW_FILE_NAME_NORMALIZED_VOLUME_NAME_GUID_"
            "PathCchRemoveFileSpec"
        ),
        "target_parent_derivation_wchar_capacity": 32768,
        "target_parent_derivation_hresult": 0,
        "target_parent_resolution_succeeded": True,
        "final_close_api": "CloseHandle",
        "final_close_returned_nonzero": True,
        "final_handle_closed_once": True,
        "path_buffer_free_api": "VirtualFree",
        "path_buffer_free_size": 0,
        "path_buffer_free_type": 32768,
        "path_buffer_free_returned_nonzero": True,
        "path_buffer_freed_once": True,
        "same_volume": True,
        "call_returned_nonzero": True,
        "move_completed_on_disk_before_return": True,
        "normalized_os_result_code": 0,
    }
    for field, wanted in constants.items():
        if type(wanted) is bool:
            if record[field] is not wanted:
                _refuse(f"directory durability {field} differs")
        elif record[field] != wanted:
            _refuse(f"directory durability {field} differs")
    _uint(record["actor_process_id"], 32, "directory actor PID", positive=True)
    _uint(
        record["actor_process_creation_filetime_uint64"],
        64,
        "directory actor creation FILETIME",
        positive=True,
    )
    _uint(record["actor_thread_id"], 32, "directory actor TID", positive=True)
    if (
        record["actor_process_id"],
        record["actor_process_creation_filetime_uint64"],
    ) != (
        actor_process["process_id"],
        actor_process["creation_filetime_uint64"],
    ):
        _refuse("directory durability actor differs from bound process")
    expected_atomic_hash = sha256_hex(canonical_bytes(atomic))
    if record["atomic_publication_observation_sha256"] != expected_atomic_hash:
        _refuse("directory durability atomic-publication digest differs")
    _same_identity(record["source_path_identity"], atomic["source_path_identity"], "directory source")
    _same_identity(
        record["published_final_path_identity"],
        atomic["target_path_identity"],
        "directory final",
    )
    _same_identity(
        record["final_open_path_identity"],
        record["published_final_path_identity"],
        "directory final open",
    )
    _same_identity(
        record["resolved_final_path_identity"],
        record["published_final_path_identity"],
        "directory resolved final",
    )
    handle = _handle(record["final_open_handle_value_uint64"], "directory final handle")
    if record["final_path_query_input_handle_value_uint64"] != handle:
        _refuse("GetFinalPathNameByHandleW used a substituted handle")
    if record["final_close_input_handle_value_uint64"] != handle:
        _refuse("CloseHandle used a substituted final handle")
    buffer_address = _uint(
        record["path_buffer_base_address_uint64"],
        64,
        "directory path buffer",
        positive=True,
    )
    if record["final_path_query_output_buffer_address_uint64"] != buffer_address:
        _refuse("final-path query used a substituted path buffer")
    if record["target_parent_derivation_input_buffer_address_uint64"] != buffer_address:
        _refuse("PathCchRemoveFileSpec used a substituted path buffer")
    if record["path_buffer_free_input_address_uint64"] != buffer_address:
        _refuse("VirtualFree used a substituted path buffer")
    length = _uint(
        record["final_path_query_returned_length_uint32"],
        32,
        "final path length",
        positive=True,
    )
    if length >= 32768:
        _refuse("final path query length reaches or exceeds capacity")
    time_fields = (
        "final_open_completed_utc",
        "path_buffer_allocated_utc",
        "final_path_query_completed_utc",
        "target_parent_derivation_completed_utc",
        "final_handle_closed_utc",
        "path_buffer_freed_utc",
        "observation_utc",
    )
    _ordered_times(record, time_fields, "directory durability")
    if record["path_buffer_freed_utc"] != record["observation_utc"]:
        _refuse("directory observation time differs from buffer release")
    if (
        expected_observation_utc is not None
        and record["observation_utc"] != expected_observation_utc
    ):
        _refuse("directory observation time differs from bound action")


def _validate_process_instance(value: Any, label: str) -> dict[str, Any]:
    record = _mapping(value, label)
    _exact_fields(record, _PROCESS_FIELDS, label)
    _uint(record["process_id"], 32, f"{label}.process_id", positive=True)
    _uint(
        record["creation_filetime_uint64"],
        64,
        f"{label}.creation_filetime_uint64",
        positive=True,
    )
    _identity(record["executable_path_identity"], "stage_f_private_path/v1", f"{label}.executable_path_identity")
    for field in ("executable_sha256", "command_line_sha256", "invocation_sha256"):
        _sha256(record[field], f"{label}.{field}")
    if record["self_command_line_observation_api"] != "GetCommandLineW":
        _refuse(f"{label} command-line observation API differs")
    if record["locked_bootstrap_verified_invocation"] is not True:
        _refuse(f"{label} did not verify the locked bootstrap")
    return record


def _validate_invocation(
    value: Any,
    *,
    phase: str,
    receipt: Mapping[str, Any],
) -> tuple[dict[str, Any], bytes, bytes]:
    label = f"{phase} invocation"
    record = _mapping(value, label)
    _exact_fields(record, _INVOCATION_FIELDS, label)
    constants = {
        "schema": "stage_f_durability_probe_invocation/v1",
        "phase": phase,
        "bootstrap_source_path": "stage_f_binding/locked_zipapp_bootstrap.py",
        "command_schema": f"PYTHON_LOCKED_ZIPAPP_STAGE_F_BINDING_VALIDATOR_{phase}_V1",
        "command_line_construction": "BOUND_HOST_CPYTHON_SUBPROCESS_LIST2CMDLINE",
        "command_line_encoding": "UTF-16LE_WITHOUT_TERMINAL_NUL",
        "entrypoint_mode": "EXACT_GIT_BOOTSTRAP_C_OPTION_LOCKED_DETERMINISTIC_ZIPAPP",
        "isolated_mode": True,
        "network_access_permitted": False,
    }
    for field, wanted in constants.items():
        if type(wanted) is bool:
            if record[field] is not wanted:
                _refuse(f"{label} {field} differs")
        elif record[field] != wanted:
            _refuse(f"{label} {field} differs")
    for field, kind in (
        ("binding_validator_identity", "stage_f_binding_validator/v1"),
        ("execution_environment_policy_identity", "stage_f_execution_environment_policy/v1"),
        ("host_validation_runtime_identity", "stage_f_host_validation_runtime/v1"),
        ("executable_path_identity", "stage_f_private_path/v1"),
        ("validator_zipapp_path_identity", "stage_f_private_path/v1"),
        ("invocation_preimage_path_identity", "stage_f_private_path/v1"),
    ):
        _identity(record[field], kind, f"{label}.{field}")
    for field in (
        "binding_validator_identity",
        "execution_environment_policy_identity",
        "host_validation_runtime_identity",
    ):
        receipt_field = (
            "execution_environment_policy_identity"
            if field == "execution_environment_policy_identity"
            else field
        )
        _same_identity(record[field], receipt[receipt_field], f"{label}.{field}")
    if record["host_runtime_lock_acquisition_sha256"] != receipt["host_runtime_lock_acquisition_sha256"]:
        _refuse(f"{label} host-runtime-lock acquisition digest differs")
    validate_no_science_counters(record["scientific_counters"])
    bootstrap = _strict_base64(record["bootstrap_source_utf8_base64"], f"{label} bootstrap")
    if bootstrap.startswith(b"\xef\xbb\xbf"):
        _refuse(f"{label} bootstrap has a UTF-8 BOM")
    try:
        bootstrap.decode("utf-8", "strict")
    except UnicodeDecodeError as exc:
        raise BindingRefusal(f"{label} bootstrap is not UTF-8") from exc
    if not 0 < len(bootstrap) <= 8192 or record["bootstrap_source_byte_count"] != len(bootstrap):
        _refuse(f"{label} bootstrap byte count differs")
    row = _mapping(record["bootstrap_git_row"], f"{label} bootstrap Git row")
    _exact_fields(
        row,
        frozenset({"path", "mode", "git_object", "byte_count", "raw_sha256"}),
        f"{label} bootstrap Git row",
    )
    git_object = hashlib.sha1(
        f"blob {len(bootstrap)}\0".encode("ascii") + bootstrap
    ).hexdigest()
    if row != {
        "path": "stage_f_binding/locked_zipapp_bootstrap.py",
        "mode": "100644",
        "git_object": git_object,
        "byte_count": len(bootstrap),
        "raw_sha256": hashlib.sha256(bootstrap).hexdigest(),
    }:
        _refuse(f"{label} bootstrap Git row does not reconstruct")
    _uint(record["validator_zipapp_byte_count"], 64, f"{label} ZIP byte count", positive=True)
    _sha256(record["validator_zipapp_sha256"], f"{label} ZIP digest")
    command = _strict_base64(record["command_line_base64"], f"{label} command line")
    if len(command) % 2 or command.endswith(b"\x00\x00"):
        _refuse(f"{label} command line is not UTF-16LE without a terminal NUL")
    try:
        command.decode("utf-16le", "strict")
    except UnicodeDecodeError as exc:
        raise BindingRefusal(f"{label} command line is invalid UTF-16LE") from exc
    units = len(command) // 2
    if units != record["command_line_utf16_code_unit_count"] or not 1 <= units <= 32766:
        _refuse(f"{label} command-line code-unit count differs")
    suffix = (
        record["restart_challenge_path_identity"],
        record["restart_challenge_sha256"],
        record["acknowledgement_path_identity"],
    )
    if phase == "POST_RESTART":
        _identity(suffix[0], "stage_f_private_path/v1", f"{label} challenge path")
        _sha256(suffix[1], f"{label} challenge digest")
        _identity(suffix[2], "stage_f_private_path/v1", f"{label} acknowledgement path")
        if suffix[0] == suffix[2]:
            _refuse(f"{label} challenge and acknowledgement paths are equal")
    elif suffix != (None, None, None):
        _refuse(f"{label} has a forbidden POST_RESTART suffix")
    return record, bootstrap, command


def _validate_artifact_lock(
    value: Any,
    *,
    role: str,
    process: Mapping[str, Any],
    invocation: Mapping[str, Any],
    receipt: Mapping[str, Any],
) -> dict[str, Any]:
    label = f"{role} artifact lock"
    record = _mapping(value, label)
    _exact_fields(record, _ARTIFACT_LOCK_FIELDS, label)
    constants = {
        "schema": "stage_f_validator_artifact_lock_observation/v1",
        "actor_process_role": role,
        "open_api": "CreateFileW",
        "desired_access": 2147483648,
        "share_mode": 1,
        "security_attributes": "NULL",
        "creation_disposition": 3,
        "flags_and_attributes": 2097152,
        "handle_valid": True,
        "resolved_path_api": "GetFinalPathNameByHandleW_FILE_NAME_NORMALIZED_VOLUME_NAME_GUID",
        "file_id_query_api": "GetFileInformationByHandleEx_FileIdInfo",
        "file_standard_info_query_api": "GetFileInformationByHandleEx_FileStandardInfo",
        "number_of_links": 1,
        "delete_pending": False,
        "directory": False,
        "file_attribute_tag_query_api": "GetFileInformationByHandleEx_FileAttributeTagInfo",
        "reparse_tag": 0,
        "read_api": "ReadFile",
        "read_from_held_handle": True,
        "close_api": "CloseHandle",
        "close_returned_nonzero": True,
        "write_share_permitted": False,
        "delete_share_permitted": False,
        "lock_held_from_before_zipapp_read_until_after_zipapp_return": True,
        "status": "PASS",
    }
    for field, wanted in constants.items():
        if type(wanted) is bool:
            if record[field] is not wanted:
                _refuse(f"{label} {field} differs")
        elif record[field] != wanted:
            _refuse(f"{label} {field} differs")
    actor = (
        _uint(record["actor_process_id"], 32, f"{label} PID", positive=True),
        _uint(
            record["actor_process_creation_filetime_uint64"],
            64,
            f"{label} creation FILETIME",
            positive=True,
        ),
    )
    if actor != (process["process_id"], process["creation_filetime_uint64"]):
        _refuse(f"{label} actor process differs")
    for field in ("binding_validator_identity", "host_validation_runtime_identity"):
        _same_identity(record[field], receipt[field], f"{label}.{field}")
    invocation_digest = sha256_hex(canonical_bytes(invocation))
    if record["invocation_sha256"] != invocation_digest or process["invocation_sha256"] != invocation_digest:
        _refuse(f"{label} invocation digest differs")
    _same_identity(record["artifact_path_identity"], invocation["validator_zipapp_path_identity"], f"{label} path")
    _same_identity(record["resolved_path_identity"], record["artifact_path_identity"], f"{label} resolved path")
    if (
        record["expected_byte_count"] != invocation["validator_zipapp_byte_count"]
        or record["observed_byte_count"] != record["expected_byte_count"]
        or record["expected_sha256"] != invocation["validator_zipapp_sha256"]
        or record["observed_sha256"] != record["expected_sha256"]
    ):
        _refuse(f"{label} count or digest differs")
    handle = _handle(record["artifact_handle_value_uint64"], f"{label} handle")
    for field in (
        "resolved_path_query_handle_value_uint64",
        "file_id_query_handle_value_uint64",
        "file_standard_info_query_handle_value_uint64",
        "file_attribute_tag_query_handle_value_uint64",
        "read_input_handle_value_uint64",
        "close_input_handle_value_uint64",
    ):
        if record[field] != handle:
            _refuse(f"{label} used a substituted handle: {field}")
    _uint(record["volume_serial_number"], 64, f"{label} volume serial")
    _uint(record["raw_file_attributes"], 32, f"{label} file attributes")
    if record["raw_file_attributes"] & 0x400:
        _refuse(f"{label} has FILE_ATTRIBUTE_REPARSE_POINT")
    _ordered_times(
        record,
        ("lock_acquired_utc", "validator_entrypoint_loaded_utc", "handle_closed_utc", "lock_released_utc"),
        label,
    )
    if record["handle_closed_utc"] != record["lock_released_utc"]:
        _refuse(f"{label} release time differs from CloseHandle completion")
    verify_embedded_digest(record, "lock_sha256", kind="stage_f_validator_artifact_lock_observation/v1")
    return record


def _validate_output_storage(
    value: Any,
    *,
    bits: int,
    expected_value: int,
    label: str,
) -> None:
    record = _mapping(value, label)
    _exact_fields(record, _OUTPUT_FIELDS, label)
    count = bits // 8
    schema = f"stage_f_uint{bits}_output_storage/v1"
    if record["schema"] != schema or record["byte_count"] != count:
        _refuse(f"{label} schema or byte count differs")
    base = _uint(record["base_address_uint64"], 64, f"{label}.base", positive=True)
    if base > _UINT64_MAX - count or record["exclusive_end_address_uint64"] != base + count:
        _refuse(f"{label} interval formula differs or overflows")
    if record["interval_nonoverflowing"] is not True:
        _refuse(f"{label} interval is not marked nonoverflowing")
    zero = bytes(count)
    if _strict_base64(record["input_bytes_base64"], f"{label}.input") != zero:
        _refuse(f"{label} input image is not zero")
    if record["input_sha256"] != hashlib.sha256(zero).hexdigest():
        _refuse(f"{label} input digest differs")
    output = _strict_base64(record["output_bytes_base64"], f"{label}.output")
    if len(output) != count or int.from_bytes(output, "little") != expected_value:
        _refuse(f"{label} output image does not encode the retained value")
    if record["output_sha256"] != hashlib.sha256(output).hexdigest():
        _refuse(f"{label} output digest differs")
    for prefix in ("input", "output"):
        if record[f"{prefix}_hash_input_address_uint64"] != base:
            _refuse(f"{label} {prefix} hash used a substituted address")
        if record[f"{prefix}_hash_input_byte_count"] != count:
            _refuse(f"{label} {prefix} hash byte count differs")
        _utc(record[f"{prefix}_hash_completed_utc"], f"{label}.{prefix}_hash_completed_utc")
    if record["live_through_call_return"] is not True or record["live_through_output_hash"] is not True:
        _refuse(f"{label} storage lifetime is incomplete")


def _validate_control_write(
    value: Any,
    *,
    content_role: str,
    actor_process: Mapping[str, Any],
    target_path_identity: Mapping[str, Any],
    expected_bytes: bytes,
    label: str,
) -> dict[str, Any]:
    record = _mapping(value, label)
    _exact_fields(record, _CONTROL_WRITE_FIELDS, label)
    constants = {
        "schema": "stage_f_durability_control_file_write/v1",
        "content_role": content_role,
        "operations_serialized": True,
        "target_nonexistence_observation": (
            "GetFileAttributesW_INVALID_FILE_ATTRIBUTES_ERROR_FILE_NOT_FOUND"
        ),
        "create_api": "CreateFileW",
        "desired_access": 1073741824,
        "share_mode": 0,
        "security_attributes": "NULL",
        "creation_disposition": 1,
        "flags_and_attributes": 2147483648,
        "handle_valid": True,
        "write_api": "WriteFile",
        "write_buffer_interval_nonoverflowing": True,
        "write_buffer_live_and_unchanged_through_return": True,
        "write_input_and_output_intervals_disjoint": True,
        "write_overlapped_pointer": "NULL",
        "write_returned_nonzero": True,
        "flush_api": "FlushFileBuffers",
        "flush_returned_nonzero": True,
        "close_api": "CloseHandle",
        "close_returned_nonzero": True,
        "handle_closed_once": True,
        "target_created_once": True,
    }
    for field, wanted in constants.items():
        if type(wanted) is bool:
            if record[field] is not wanted:
                _refuse(f"{label} {field} differs")
        elif record[field] != wanted:
            _refuse(f"{label} {field} differs")
    if (
        record["actor_process_id"],
        record["actor_process_creation_filetime_uint64"],
    ) != (
        actor_process["process_id"],
        actor_process["creation_filetime_uint64"],
    ):
        _refuse(f"{label} actor process differs")
    _uint(record["actor_thread_id"], 32, f"{label} actor thread", positive=True)
    _same_identity(record["target_path_identity"], target_path_identity, f"{label} target")
    handle = _handle(record["created_handle_value_uint64"], f"{label} handle")
    for field in (
        "write_input_handle_value_uint64",
        "flush_input_handle_value_uint64",
        "close_input_handle_value_uint64",
    ):
        if record[field] != handle:
            _refuse(f"{label} used a substituted handle: {field}")
    count = len(expected_bytes)
    if not 0 < count <= _UINT32_MAX:
        _refuse(f"{label} expected byte count is outside positive uint32")
    base = _uint(
        record["write_buffer_base_address_uint64"],
        64,
        f"{label} write buffer",
        positive=True,
    )
    if (
        base > _UINT64_MAX - count
        or record["write_buffer_exclusive_end_address_uint64"] != base + count
        or record["write_buffer_byte_count"] != count
        or record["write_buffer_hash_input_address_uint64"] != base
        or record["write_buffer_hash_input_byte_count"] != count
        or _strict_base64(
            record["write_buffer_call_time_bytes_base64"], f"{label} write bytes"
        )
        != expected_bytes
        or record["write_buffer_call_time_sha256"]
        != hashlib.sha256(expected_bytes).hexdigest()
    ):
        _refuse(f"{label} write-buffer projection differs")
    output = record["write_bytes_written_output_observation"]
    _validate_output_storage(
        output, bits=32, expected_value=count, label=f"{label} bytes-written output"
    )
    output_interval = (
        output["base_address_uint64"],
        output["exclusive_end_address_uint64"],
    )
    if max(base, output_interval[0]) < min(base + count, output_interval[1]):
        _refuse(f"{label} write input/output intervals overlap")
    if (
        record["written_byte_count"] != count
        or record["written_sha256"] != hashlib.sha256(expected_bytes).hexdigest()
    ):
        _refuse(f"{label} written bytes differ")
    times = (
        record["create_started_utc"],
        record["create_completed_utc"],
        record["write_buffer_hash_completed_utc"],
        output["input_hash_completed_utc"],
        record["write_started_utc"],
        record["write_completed_utc"],
        output["output_hash_completed_utc"],
        record["flush_started_utc"],
        record["flush_completed_utc"],
        record["close_started_utc"],
        record["close_completed_utc"],
    )
    parsed = [_utc(item, f"{label} operation time") for item in times]
    if parsed != sorted(parsed):
        _refuse(f"{label} operation order differs")
    return record


def _validate_security_lifecycle(
    value: Any,
    *,
    anchor_handle: int,
    label: str,
) -> dict[str, Any]:
    record = _mapping(value, label)
    _exact_fields(record, _SECURITY_LIFECYCLE_FIELDS, label)
    constants = {
        "security_query_api": "GetSecurityInfo_SE_FILE_OBJECT",
        "security_information_mask": 7,
        "security_query_result_code": 0,
        "security_descriptor_validation_api": "IsValidSecurityDescriptor",
        "security_descriptor_validation_returned_nonzero": True,
        "security_descriptor_control_api": "GetSecurityDescriptorControl",
        "security_descriptor_control_returned_nonzero": True,
        "security_descriptor_self_relative_control_mask": 32768,
        "security_descriptor_revision_uint32": 1,
        "security_descriptor_self_relative": True,
        "security_descriptor_length_api": "GetSecurityDescriptorLength",
        "security_descriptor_free_api": "LocalFree",
        "security_descriptor_free_called_once": True,
        "security_descriptor_free_result": "NULL",
    }
    for field, wanted in constants.items():
        if type(wanted) is bool:
            if record[field] is not wanted:
                _refuse(f"{label} {field} differs")
        elif record[field] != wanted:
            _refuse(f"{label} {field} differs")
    if record["security_query_handle_value_uint64"] != anchor_handle:
        _refuse(f"{label} security query used a substituted anchor handle")
    pointer = _uint(
        record["security_descriptor_address_uint64"],
        64,
        f"{label} descriptor pointer",
        positive=True,
    )
    for field in (
        "security_descriptor_validation_input_address_uint64",
        "security_descriptor_control_input_address_uint64",
        "security_descriptor_length_input_address_uint64",
        "security_descriptor_hash_input_address_uint64",
        "security_descriptor_free_input_address_uint64",
    ):
        if record[field] != pointer:
            _refuse(f"{label} used a substituted descriptor pointer: {field}")
    count = _uint(
        record["security_descriptor_byte_count"],
        32,
        f"{label} descriptor byte count",
        positive=True,
    )
    if record["security_descriptor_hash_input_byte_count"] != count:
        _refuse(f"{label} descriptor hash byte count differs")
    _sha256(record["security_descriptor_sha256"], f"{label} descriptor digest")
    if (
        record["security_descriptor_control_uint16"]
        & record["security_descriptor_self_relative_control_mask"]
    ) != record["security_descriptor_self_relative_control_mask"]:
        _refuse(f"{label} descriptor is not marked self-relative")
    _ordered_times(
        record,
        (
            "security_query_completed_utc",
            "security_descriptor_hashed_utc",
            "security_descriptor_freed_utc",
        ),
        label,
    )
    return record


def _same_projection(
    left: Mapping[str, Any],
    right: Mapping[str, Any],
    fields: Sequence[str],
    label: str,
) -> None:
    for field in fields:
        if left[field] != right[field]:
            _refuse(f"{label} projection differs: {field}")


def _validate_host_runtime_inventory(
    acquisition_value: Any,
    runtime_preimage_value: Any,
    *,
    processes: Sequence[Mapping[str, Any]],
) -> None:
    acquisition = _mapping(acquisition_value, "host-runtime-lock acquisition")
    runtime = _mapping(runtime_preimage_value, "host-validation runtime preimage")
    if runtime.get("schema") != "stage_f_host_validation_runtime/v1":
        _refuse("host-validation runtime preimage schema differs")
    _same_identity(
        acquisition["runtime_root_path_identity"],
        runtime["runtime_root_path_identity"],
        "host-runtime acquisition root",
    )
    runtime_files = runtime["ordered_runtime_file_rows"]
    acquired_files = acquisition["ordered_runtime_file_lock_rows"]
    if (
        type(runtime_files) is not list
        or runtime["runtime_file_count"] != len(runtime_files)
        or len(runtime_files) != len(acquired_files)
        or acquisition["runtime_file_lock_count"] != len(acquired_files)
        or acquisition["runtime_inventory_file_count"] != len(acquired_files)
    ):
        _refuse("host-runtime immutable/acquired file inventory counts differ")
    relative_paths = [row["relative_path"] for row in runtime_files]
    normalized_paths = [unicodedata.normalize("NFC", path) for path in relative_paths]
    if (
        relative_paths != normalized_paths
        or normalized_paths
        != sorted(normalized_paths, key=lambda path: path.encode("utf-8"))
        or len(normalized_paths) != len(set(normalized_paths))
    ):
        _refuse("host-runtime immutable file inventory order differs")
    executable_acquisition: Mapping[str, Any] | None = None
    file_lock_times: list[datetime] = []
    for ordinal, (manifest_row, acquired_row) in enumerate(
        zip(runtime_files, acquired_files, strict=True), start=1
    ):
        if (
            acquired_row["ordinal"] != ordinal
            or acquired_row["runtime_relative_path"] != manifest_row["relative_path"]
            or acquired_row["expected_byte_count"] != manifest_row["byte_count"]
            or acquired_row["expected_sha256"] != manifest_row["sha256"]
            or acquired_row["observed_byte_count"] != manifest_row["byte_count"]
            or acquired_row["observed_sha256"] != manifest_row["sha256"]
        ):
            _refuse(f"host-runtime acquired file differs from immutable row {ordinal}")
        if manifest_row["relative_path"] == runtime["executable_relative_path"]:
            if executable_acquisition is not None:
                _refuse("host-runtime inventory repeats its executable path")
            executable_acquisition = acquired_row
        file_lock_times.append(
            _utc(acquired_row["lock_acquired_utc"], f"runtime file {ordinal} lock")
        )
    if (
        executable_acquisition is None
        or executable_acquisition["expected_sha256"]
        != runtime["python_executable_sha256"]
    ):
        _refuse("host-runtime executable is absent or has another digest")
    holder = acquisition["lock_holder_process"]
    _same_identity(
        holder["executable_path_identity"],
        executable_acquisition["runtime_path_identity"],
        "host-runtime lock-holder executable path",
    )
    if holder["executable_sha256"] != runtime["python_executable_sha256"]:
        _refuse("host-runtime lock-holder executable digest differs")
    for phase, process in zip(
        ("ORCHESTRATOR", "PRE_RESTART", "POST_RESTART"), processes, strict=True
    ):
        _same_identity(
            process["executable_path_identity"],
            executable_acquisition["runtime_path_identity"],
            f"{phase} host-runtime executable path",
        )
        if process["executable_sha256"] != runtime["python_executable_sha256"]:
            _refuse(f"{phase} process executable digest differs from host runtime")

    runtime_directories = runtime["ordered_runtime_directory_rows"]
    acquired_directories = acquisition["ordered_runtime_directory_rows"]
    if (
        type(runtime_directories) is not list
        or runtime["runtime_directory_count"] != len(runtime_directories)
        or acquisition["runtime_directory_count"] != len(acquired_directories)
        or len(runtime_directories) != len(acquired_directories)
    ):
        _refuse("host-runtime immutable/acquired directory inventory counts differ")
    directory_paths = [row["relative_path"] for row in runtime_directories]
    normalized_directories = [
        unicodedata.normalize("NFC", path) for path in directory_paths
    ]
    if (
        not normalized_directories
        or normalized_directories[0] != "."
        or directory_paths != normalized_directories
        or normalized_directories[1:]
        != sorted(normalized_directories[1:], key=lambda path: path.encode("utf-8"))
        or len(normalized_directories) != len(set(normalized_directories))
    ):
        _refuse("host-runtime immutable directory inventory order differs")
    directory_close_times: list[datetime] = []
    for ordinal, (manifest_row, acquired_row) in enumerate(
        zip(runtime_directories, acquired_directories, strict=True), start=1
    ):
        if acquired_row["ordinal"] != ordinal or acquired_row["manifest_row"] != manifest_row:
            _refuse(f"host-runtime acquired directory manifest row differs: {ordinal}")
        handle = _handle(
            acquired_row["directory_handle_value_uint64"],
            f"runtime directory {ordinal} handle",
        )
        for field in (
            "resolved_path_query_handle_value_uint64",
            "file_id_query_handle_value_uint64",
            "file_attribute_tag_query_handle_value_uint64",
            "close_input_handle_value_uint64",
        ):
            if acquired_row[field] != handle:
                _refuse(f"runtime directory {ordinal} substituted its handle: {field}")
        _same_identity(
            acquired_row["resolved_path_identity"],
            acquired_row["runtime_path_identity"],
            f"runtime directory {ordinal} resolved path",
        )
        security = _validate_security_lifecycle(
            acquired_row["security_descriptor_query_lifecycle"],
            anchor_handle=handle,
            label=f"runtime directory {ordinal} security",
        )
        projection = {
            "volume_serial_number": acquired_row["volume_serial_number"],
            "file_id_128": acquired_row["file_id_128"],
            "raw_file_attributes": acquired_row["raw_file_attributes"],
            "reparse_tag": acquired_row["reparse_tag"],
            "directory": acquired_row["directory"],
            "security_information_mask": security["security_information_mask"],
            "security_descriptor_format": "SELF_RELATIVE",
            "security_descriptor_byte_count": security[
                "security_descriptor_byte_count"
            ],
            "security_descriptor_sha256": security["security_descriptor_sha256"],
        }
        for field, expected in projection.items():
            if manifest_row[field] != expected:
                _refuse(
                    f"runtime directory {ordinal} dynamic projection differs: {field}"
                )
        directory_close = _utc(
            acquired_row["directory_handle_closed_utc"],
            f"runtime directory {ordinal} handle close",
        )
        if _utc(
            security["security_descriptor_freed_utc"],
            f"runtime directory {ordinal} security free",
        ) > directory_close:
            _refuse(f"runtime directory {ordinal} closed before security lifecycle")
        directory_close_times.append(directory_close)
    directory_start = _utc(
        acquisition["directory_inventory_started_utc"], "runtime directory inventory start"
    )
    directory_completed = _utc(
        acquisition["directory_inventory_completed_utc"],
        "runtime directory inventory completion",
    )
    file_locks_completed = _utc(
        acquisition["file_lock_acquisition_completed_utc"],
        "runtime file-lock acquisition completion",
    )
    if (
        any(not directory_start <= time <= directory_completed for time in directory_close_times)
        or any(not directory_completed <= time <= file_locks_completed for time in file_lock_times)
    ):
        _refuse("host-runtime directory/file inventory timestamps differ")


def _validate_host_runtime_lock_release(
    acquisition_value: Any,
    release_value: Any,
    *,
    processes: Sequence[Mapping[str, Any]],
    invocations: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    acquisition = _mapping(acquisition_value, "host-runtime-lock acquisition")
    release = _mapping(release_value, "host-runtime-lock release")
    _exact_fields(release, _HOST_RELEASE_FIELDS, "host-runtime-lock release")
    if acquisition.get("schema") != "stage_f_host_validation_runtime_lock_acquisition/v1":
        _refuse("host-runtime-lock acquisition schema differs")
    if release["schema"] != "stage_f_host_validation_runtime_lock_release/v1":
        _refuse("host-runtime-lock release schema differs")
    acquisition_sha = sha256_hex(canonical_bytes(acquisition))
    if release["host_runtime_lock_acquisition_sha256"] != acquisition_sha:
        _refuse("host-runtime-lock release acquisition digest differs")
    validate_no_science_counters(acquisition["scientific_counters"])
    validate_no_science_counters(release["scientific_counters"])
    holder = _mapping(acquisition["lock_holder_process"], "runtime lock holder")
    if (
        release["lock_holder_process_id"],
        release["lock_holder_process_creation_filetime_uint64"],
    ) != (
        holder["process_id"],
        holder["process_creation_filetime_uint64"],
    ) or release["lock_holder_process_identity_equals_acquisition"] is not True:
        _refuse("host-runtime-lock release holder differs from acquisition")

    process_rows = release["locked_validator_processes"]
    if type(process_rows) is not list or len(process_rows) != 3:
        _refuse("host-runtime-lock release must bind exactly three validator processes")
    phases = ("ORCHESTRATOR", "PRE_RESTART", "POST_RESTART")
    returned_times: list[datetime] = []
    for row, phase, process, invocation in zip(
        process_rows, phases, processes, invocations, strict=True
    ):
        row = _mapping(row, f"{phase} locked-validator process reference")
        if row["phase"] != phase or row["exit_code"] != 0:
            _refuse(f"{phase} locked-validator process disposition differs")
        if (
            row["process_id"],
            row["process_creation_filetime_uint64"],
        ) != (
            process["process_id"],
            process["creation_filetime_uint64"],
        ):
            _refuse(f"{phase} locked-validator process identity differs")
        invocation_sha = sha256_hex(canonical_bytes(invocation))
        if row["invocation_sha256"] != invocation_sha:
            _refuse(f"{phase} locked-validator invocation digest differs")
        returned_times.append(
            _utc(row["process_returned_utc"], f"{phase} process returned UTC")
        )
    last_return = max(returned_times)
    if (
        _utc(release["last_validator_process_returned_utc"], "last validator return")
        != last_return
        or _utc(release["protection_epoch_ended_utc"], "protection epoch end")
        != last_return
    ):
        _refuse("host-runtime protection epoch does not end at the latest process return")
    release_started = _utc(release["release_started_utc"], "release start")
    release_completed = _utc(release["release_completed_utc"], "release completion")
    if not last_return <= release_started <= release_completed:
        _refuse("host-runtime release starts before validator return or completes early")
    if (
        release[
            "any_retained_anchor_watch_or_file_handle_released_before_all_validator_processes_returned"
        ]
        is not False
        or release["complete_acquisition_projection_remeasured"] is not True
        or release["all_handles_closed_once"] is not True
        or acquisition[
            "any_retained_anchor_watch_or_file_handle_released_before_completion"
        ]
        is not False
    ):
        _refuse("host-runtime retained-handle lifetime declaration differs")

    anchors = acquisition["ordered_runtime_path_anchor_lock_rows"]
    epoch_anchors = acquisition["ordered_path_anchor_protection_epoch_rows"]
    released_anchors = release["ordered_runtime_path_anchor_release_rows"]
    anchor_count = acquisition["runtime_path_anchor_lock_count"]
    if (
        anchor_count != len(anchors)
        or acquisition["path_anchor_protection_epoch_count"] != len(epoch_anchors)
        or release["runtime_path_anchor_release_count"] != len(released_anchors)
        or not len(anchors) == len(epoch_anchors) == len(released_anchors)
    ):
        _refuse("host-runtime anchor counts differ")
    if (
        anchors[0]["anchor_path_identity"]
        != acquisition["selected_volume_root_path_identity"]
        or anchors[-1]["anchor_path_identity"]
        != acquisition["runtime_root_path_identity"]
        or (
            len(anchors) > 1
            and anchors[-2]["anchor_path_identity"]
            != acquisition["runtime_parent_path_identity"]
        )
    ):
        _refuse("host-runtime anchor endpoints differ from the selected runtime paths")
    expected_anchor_roles = [
        "SELECTED_VOLUME_ROOT",
        *(["RUNTIME_PATH_ANCESTOR"] * max(0, len(anchors) - 2)),
        "RUNTIME_ROOT",
    ]
    if [row["anchor_role"] for row in anchors] != expected_anchor_roles:
        _refuse("host-runtime anchor roles differ from the exact root-to-runtime chain")
    anchor_final_times: list[datetime] = []
    anchor_release_times: list[datetime] = []
    anchor_acquisition_times: list[datetime] = []
    anchor_epoch_times: list[datetime] = []
    retained_handles: set[int] = set()
    for ordinal, (acquired, epoch, released) in enumerate(
        zip(anchors, epoch_anchors, released_anchors, strict=True), start=1
    ):
        if any(row["ordinal"] != ordinal for row in (acquired, epoch, released)):
            _refuse("host-runtime anchor ordinals are not exact and gapless")
        expected_parent = None if ordinal == 1 else ordinal - 1
        if acquired["parent_anchor_ordinal"] != expected_parent:
            _refuse("host-runtime anchor parent chain differs")
        _same_projection(
            acquired,
            epoch,
            (
                "anchor_role",
                "anchor_path_identity",
                "volume_serial_number",
                "file_id_128",
                "raw_file_attributes",
                "reparse_tag",
                "directory",
            ),
            f"anchor {ordinal} acquisition/epoch",
        )
        _same_projection(
            acquired,
            released,
            (
                "anchor_role",
                "anchor_path_identity",
                "volume_serial_number",
                "file_id_128",
                "raw_file_attributes",
                "reparse_tag",
                "directory",
            ),
            f"anchor {ordinal} acquisition/release",
        )
        anchor_handle = _handle(
            acquired["anchor_handle_value_uint64"], f"anchor {ordinal} handle"
        )
        guard_handle = _handle(
            acquired["continuity_guard_handle_value_uint64"],
            f"anchor {ordinal} continuity guard",
        )
        if anchor_handle == guard_handle:
            _refuse(f"anchor {ordinal} and continuity-guard handles are equal")
        for retained_handle in (anchor_handle, guard_handle):
            if retained_handle in retained_handles:
                _refuse("host-runtime retained anchor handles are not pairwise distinct")
            retained_handles.add(retained_handle)
        for row, phase in ((acquired, "acquisition"), (epoch, "epoch"), (released, "release")):
            for field in (
                "resolved_path_query_handle_value_uint64",
                "file_id_query_handle_value_uint64",
                "file_attribute_tag_query_handle_value_uint64",
            ):
                if row[field] != anchor_handle:
                    _refuse(f"anchor {ordinal} {phase} used a substituted handle: {field}")
        _same_identity(
            acquired["resolved_path_identity"],
            acquired["anchor_path_identity"],
            f"anchor {ordinal} resolved acquisition path",
        )
        if acquired["continuity_guard_source_handle_value_uint64"] != anchor_handle:
            _refuse(f"anchor {ordinal} guard duplication used a substituted source handle")
        for row, phase in ((epoch, "epoch"), (released, "release")):
            if (
                row["same_anchor_handle_value_uint64"] != anchor_handle
                or row["same_continuity_guard_handle_value_uint64"] != guard_handle
                or row["handle_continuity_compare_first_handle_value_uint64"]
                != anchor_handle
                or row["handle_continuity_compare_second_handle_value_uint64"]
                != guard_handle
            ):
                _refuse(f"anchor {ordinal} {phase} substituted continuity handles")
        acquired_security = _validate_security_lifecycle(
            acquired["security_descriptor_query_lifecycle"],
            anchor_handle=anchor_handle,
            label=f"anchor {ordinal} acquisition security",
        )
        epoch_security = _validate_security_lifecycle(
            epoch["security_descriptor_query_lifecycle"],
            anchor_handle=anchor_handle,
            label=f"anchor {ordinal} epoch security",
        )
        released_security = _validate_security_lifecycle(
            released["security_descriptor_query_lifecycle"],
            anchor_handle=anchor_handle,
            label=f"anchor {ordinal} release security",
        )
        stable_security_fields = (
            "security_descriptor_control_uint16",
            "security_descriptor_revision_uint32",
            "security_descriptor_byte_count",
            "security_descriptor_sha256",
        )
        _same_projection(
            acquired_security,
            epoch_security,
            stable_security_fields,
            f"anchor {ordinal} acquisition/epoch security",
        )
        _same_projection(
            acquired_security,
            released_security,
            stable_security_fields,
            f"anchor {ordinal} acquisition/release security",
        )
        acquisition_anchor_order = (
            _utc(acquired["anchor_handle_opened_utc"], f"anchor {ordinal} open"),
            _utc(
                acquired["continuity_guard_duplicated_utc"],
                f"anchor {ordinal} guard duplicate",
            ),
            _utc(
                acquired["metadata_and_security_queries_started_utc"],
                f"anchor {ordinal} query start",
            ),
            _utc(
                acquired_security["security_query_completed_utc"],
                f"anchor {ordinal} security query completion",
            ),
            _utc(
                acquired_security["security_descriptor_hashed_utc"],
                f"anchor {ordinal} security hash",
            ),
            _utc(
                acquired_security["security_descriptor_freed_utc"],
                f"anchor {ordinal} security free",
            ),
            _utc(acquired["lock_acquired_utc"], f"anchor {ordinal} lock acquisition"),
        )
        if list(acquisition_anchor_order) != sorted(acquisition_anchor_order):
            _refuse(f"anchor {ordinal} acquisition lifecycle order differs")
        epoch_remeasurement = _utc(
            epoch["protection_epoch_remeasurement_utc"],
            f"anchor {ordinal} protection-epoch remeasurement",
        )
        if _utc(
            epoch_security["security_descriptor_freed_utc"],
            f"anchor {ordinal} epoch security free",
        ) > epoch_remeasurement:
            _refuse(f"anchor {ordinal} epoch remeasurement precedes security lifecycle")
        anchor_acquisition_times.append(acquisition_anchor_order[-1])
        anchor_epoch_times.append(epoch_remeasurement)
        if (
            released["close_input_handle_value_uint64"] != anchor_handle
            or released["continuity_guard_close_input_handle_value_uint64"] != guard_handle
        ):
            _refuse(f"anchor {ordinal} release closed a substituted handle")
        final_time = _utc(
            released["final_remeasurement_utc"], f"anchor {ordinal} final remeasurement"
        )
        if _utc(
            released_security["security_descriptor_freed_utc"],
            f"anchor {ordinal} release security free",
        ) > final_time:
            _refuse(f"anchor {ordinal} final remeasurement precedes security lifecycle")
        anchor_closed = _utc(
            released["anchor_handle_closed_utc"], f"anchor {ordinal} handle close"
        )
        guard_closed = _utc(
            released["continuity_guard_released_utc"],
            f"anchor {ordinal} guard close",
        )
        lock_released = _utc(
            released["lock_released_utc"], f"anchor {ordinal} lock release"
        )
        if lock_released != max(anchor_closed, guard_closed):
            _refuse(f"anchor {ordinal} release UTC is not its final successful close")
        if not release_started <= final_time <= min(anchor_closed, guard_closed):
            _refuse(f"anchor {ordinal} release order differs")
        anchor_final_times.append(final_time)
        anchor_release_times.append(lock_released)

    anchor_acquisition_completed = _utc(
        acquisition["path_anchor_lock_acquisition_completed_utc"],
        "path-anchor acquisition completion",
    )
    protection_started = _utc(
        acquisition["protection_epoch_started_utc"], "protection epoch start"
    )
    anchor_epoch_completed = _utc(
        acquisition["path_anchor_protection_epoch_completed_utc"],
        "path-anchor protection-epoch completion",
    )
    if any(time > anchor_acquisition_completed for time in anchor_acquisition_times):
        _refuse("path-anchor acquisition completion precedes an anchor lock")
    if any(
        not protection_started <= time <= anchor_epoch_completed
        for time in anchor_epoch_times
    ):
        _refuse("path-anchor protection-epoch remeasurement is outside its interval")

    files = acquisition["ordered_runtime_file_lock_rows"]
    released_files = release["ordered_runtime_file_release_rows"]
    if (
        acquisition["runtime_file_lock_count"] != len(files)
        or acquisition["runtime_inventory_file_count"] != len(files)
        or release["runtime_file_release_count"] != len(released_files)
        or len(files) != len(released_files)
    ):
        _refuse("host-runtime file-lock counts differ")
    file_final_times: list[datetime] = []
    file_release_times: list[datetime] = []
    stable_file_fields = (
        "ordinal",
        "runtime_relative_path",
        "runtime_path_identity",
        "volume_serial_number",
        "file_id_128",
        "number_of_links",
        "delete_pending",
        "directory",
        "raw_file_attributes",
        "reparse_tag",
    )
    for ordinal, (acquired, released) in enumerate(
        zip(files, released_files, strict=True), start=1
    ):
        if acquired["ordinal"] != ordinal or released["ordinal"] != ordinal:
            _refuse("host-runtime file ordinals are not exact and gapless")
        _same_projection(acquired, released, stable_file_fields, f"runtime file {ordinal}")
        _same_identity(
            acquired["resolved_path_identity"],
            acquired["runtime_path_identity"],
            f"runtime file {ordinal} resolved path",
        )
        handle = _handle(acquired["file_handle_value_uint64"], f"runtime file {ordinal} handle")
        if handle in retained_handles:
            _refuse("host-runtime retained file/anchor handles are not pairwise distinct")
        retained_handles.add(handle)
        for row, fields, phase in (
            (
                acquired,
                (
                    "resolved_path_query_handle_value_uint64",
                    "file_id_query_handle_value_uint64",
                    "file_standard_info_query_handle_value_uint64",
                    "file_attribute_tag_query_handle_value_uint64",
                    "read_input_handle_value_uint64",
                ),
                "acquisition",
            ),
            (
                released,
                (
                    "same_file_handle_value_uint64",
                    "resolved_path_query_handle_value_uint64",
                    "file_id_query_handle_value_uint64",
                    "file_standard_info_query_handle_value_uint64",
                    "file_attribute_tag_query_handle_value_uint64",
                    "rewind_input_handle_value_uint64",
                    "final_read_input_handle_value_uint64",
                    "close_input_handle_value_uint64",
                ),
                "release",
            ),
        ):
            if any(row[field] != handle for field in fields):
                _refuse(f"runtime file {ordinal} {phase} substituted its held handle")
        if (
            acquired["observed_byte_count"] != acquired["expected_byte_count"]
            or acquired["observed_sha256"] != acquired["expected_sha256"]
            or released["final_observed_byte_count"] != acquired["expected_byte_count"]
            or released["final_observed_sha256"] != acquired["expected_sha256"]
        ):
            _refuse(f"runtime file {ordinal} bytes differ across retained handle")
        final_time = _utc(
            released["final_remeasurement_utc"], f"runtime file {ordinal} final remeasurement"
        )
        lock_released = _utc(
            released["lock_released_utc"], f"runtime file {ordinal} lock release"
        )
        if not release_started <= final_time <= lock_released:
            _refuse(f"runtime file {ordinal} release order differs")
        file_final_times.append(final_time)
        file_release_times.append(lock_released)

    watches = acquisition["ordered_runtime_change_watch_acquisition_rows"]
    released_watches = release["ordered_runtime_change_watch_release_rows"]
    if (
        acquisition["runtime_change_watch_count"] != len(watches)
        or release["runtime_change_watch_release_count"] != len(released_watches)
        or len(watches) != len(released_watches)
        or len(watches) != anchor_count
    ):
        _refuse("host-runtime change-watch counts differ")
    event_handles: list[int] = []
    resource_values: set[int] = set()
    watch_release_times: list[datetime] = []
    watch_pre_cancel_times: list[datetime] = []
    watch_pending_times: list[datetime] = []
    stable_watch_fields = (
        "schema",
        "ordinal",
        "watch_role",
        "protected_anchor_ordinal",
        "watched_anchor_ordinal",
        "runtime_root_path_identity",
        "watched_directory_path_identity",
        "watch_subtree",
        "volume_serial_number",
        "file_id_128",
    )
    for ordinal, (acquired, released) in enumerate(
        zip(watches, released_watches, strict=True), start=1
    ):
        if acquired["ordinal"] != ordinal or released["ordinal"] != ordinal:
            _refuse("host-runtime watch ordinals are not exact and gapless")
        # The schemas use different acquisition/release names but the release
        # repeats the acquisition identity projection exactly.
        for field in stable_watch_fields[1:]:
            if acquired[field] != released[field]:
                _refuse(f"runtime watch {ordinal} projection differs: {field}")
        if ordinal < anchor_count:
            if (
                acquired["watch_role"] != "ANCHOR_SELF_DIRECT"
                or acquired["protected_anchor_ordinal"] != ordinal + 1
                or acquired["watched_anchor_ordinal"] != ordinal
                or acquired["watch_subtree"] is not False
            ):
                _refuse(f"runtime direct watch {ordinal} anchor projection differs")
        elif (
            acquired["watch_role"] != "RUNTIME_ROOT_SUBTREE"
            or acquired["protected_anchor_ordinal"] != anchor_count
            or acquired["watched_anchor_ordinal"] != anchor_count
            or acquired["watch_subtree"] is not True
        ):
            _refuse("runtime-root subtree watch projection differs")
        watched_anchor = anchors[acquired["watched_anchor_ordinal"] - 1]
        _same_identity(
            acquired["watched_directory_path_identity"],
            watched_anchor["anchor_path_identity"],
            f"runtime watch {ordinal} watched anchor path",
        )
        _same_identity(
            acquired["resolved_path_identity"],
            acquired["watched_directory_path_identity"],
            f"runtime watch {ordinal} resolved watched path",
        )
        _same_identity(
            acquired["runtime_root_path_identity"],
            acquisition["runtime_root_path_identity"],
            f"runtime watch {ordinal} runtime root",
        )
        directory_handle = _handle(
            acquired["directory_handle_value_uint64"],
            f"runtime watch {ordinal} directory handle",
        )
        buffer_address = _uint(
            acquired["buffer_base_address_uint64"],
            64,
            f"runtime watch {ordinal} buffer",
            positive=True,
        )
        overlapped_address = _uint(
            acquired["overlapped_address_uint64"],
            64,
            f"runtime watch {ordinal} OVERLAPPED",
            positive=True,
        )
        event_handle = _handle(
            acquired["event_handle_value_uint64"],
            f"runtime watch {ordinal} event handle",
        )
        for retained_handle in (directory_handle, event_handle):
            if retained_handle in retained_handles:
                _refuse("host-runtime retained watch/anchor/file handles are not distinct")
            retained_handles.add(retained_handle)
        event_handles.append(event_handle)
        for value in (directory_handle, buffer_address, overlapped_address, event_handle):
            if value in resource_values:
                _refuse("runtime watch handles or storage addresses are not pairwise distinct")
            resource_values.add(value)
        if any(
            acquired[field] != directory_handle
            for field in (
                "resolved_path_query_handle_value_uint64",
                "file_id_query_handle_value_uint64",
                "file_attribute_tag_query_handle_value_uint64",
                "watch_call_directory_handle_value_uint64",
                "initial_pending_check_directory_handle_value_uint64",
            )
        ):
            _refuse(f"runtime watch {ordinal} acquisition substituted directory handle")
        if (
            acquired["watch_call_buffer_base_address_uint64"] != buffer_address
            or acquired["watch_call_overlapped_address_uint64"] != overlapped_address
            or acquired["initial_pending_check_overlapped_address_uint64"]
            != overlapped_address
            or acquired["overlapped_event_handle_value_uint64"] != event_handle
        ):
            _refuse(f"runtime watch {ordinal} acquisition substituted storage")
        watch_issued = _utc(
            acquired["watch_issued_utc"], f"runtime watch {ordinal} issue"
        )
        watch_pending = _utc(
            acquired["initial_pending_check_utc"],
            f"runtime watch {ordinal} initial pending check",
        )
        if not anchor_acquisition_completed <= watch_issued <= watch_pending:
            _refuse(f"runtime watch {ordinal} issue/pending order differs")
        watch_pending_times.append(watch_pending)
        release_handle_fields = (
            "same_directory_handle_value_uint64",
            "pre_cancel_directory_handle_value_uint64",
            "cancel_directory_handle_value_uint64",
            "cancel_completion_directory_handle_value_uint64",
            "close_input_directory_handle_value_uint64",
        )
        if any(released[field] != directory_handle for field in release_handle_fields):
            _refuse(f"runtime watch {ordinal} release substituted directory handle")
        if any(
            released[field] != overlapped_address
            for field in (
                "same_overlapped_address_uint64",
                "pre_cancel_overlapped_address_uint64",
                "cancel_overlapped_address_uint64",
                "cancel_completion_overlapped_address_uint64",
                "overlapped_storage_release_base_address_uint64",
            )
        ):
            _refuse(f"runtime watch {ordinal} release substituted OVERLAPPED storage")
        if (
            released["same_event_handle_value_uint64"] != event_handle
            or released["event_close_input_handle_value_uint64"] != event_handle
            or released["same_buffer_base_address_uint64"] != buffer_address
            or released["buffer_hash_input_address_uint64"] != buffer_address
            or released["buffer_release_base_address_uint64"] != buffer_address
            or released["buffer_hash_byte_count"] != acquired["buffer_byte_count"]
            or released["unchanged_buffer_sha256"]
            != hashlib.sha256(bytes(acquired["buffer_byte_count"])).hexdigest()
        ):
            _refuse(f"runtime watch {ordinal} release substituted retained storage")
        watch_order = [
            _utc(released["pre_cancel_check_utc"], f"watch {ordinal} pre-cancel"),
            _utc(released["cancel_completed_utc"], f"watch {ordinal} cancel completion"),
            _utc(released["buffer_hash_observed_utc"], f"watch {ordinal} buffer hash"),
            _utc(released["directory_handle_closed_utc"], f"watch {ordinal} directory close"),
            _utc(released["event_handle_closed_utc"], f"watch {ordinal} event close"),
            _utc(released["overlapped_storage_released_utc"], f"watch {ordinal} OVERLAPPED free"),
            _utc(released["buffer_released_utc"], f"watch {ordinal} buffer free"),
        ]
        if watch_order[0] < release_started or any(
            watch_order[index] > watch_order[index + 1]
            for index in range(2)
        ) or any(time < watch_order[2] for time in watch_order[3:]):
            _refuse(f"runtime watch {ordinal} cancellation/release order differs")
        released_utc = _utc(released["watch_released_utc"], f"watch {ordinal} release")
        if released_utc != max(watch_order[3:]):
            _refuse(f"runtime watch {ordinal} release UTC differs from final resource release")
        watch_pre_cancel_times.append(watch_order[0])
        watch_release_times.append(released_utc)
    if acquisition["prelaunch_watch_set_pending_check_ordered_event_handle_values_uint64"] != event_handles:
        _refuse("prelaunch pending-set event-handle order differs from watch acquisition")
    if acquisition["prelaunch_watch_set_pending_check_count"] != len(event_handles):
        _refuse("prelaunch pending-set count differs from watch acquisition")
    latest_pending = max(watch_pending_times)
    if _utc(
        acquisition["all_runtime_change_watches_pending_utc"],
        "all watches pending",
    ) != latest_pending:
        _refuse("all-watches-pending UTC is not the latest individual check")
    if acquisition["prelaunch_watch_set_pending_check_utc"] != acquisition["protection_epoch_started_utc"]:
        _refuse("runtime protection epoch does not start at the common pending-set check")
    if _utc(
        acquisition["prelaunch_watch_set_pending_check_utc"],
        "prelaunch common pending-set check",
    ) < latest_pending:
        _refuse("prelaunch common pending-set check precedes an individual watch check")
    acquisition_times = (
        _utc(acquisition["acquisition_started_utc"], "runtime acquisition start"),
        _utc(
            acquisition["path_anchor_lock_acquisition_completed_utc"],
            "runtime anchor acquisition completion",
        ),
        _utc(acquisition["all_runtime_change_watches_pending_utc"], "all watches pending"),
        _utc(acquisition["protection_epoch_started_utc"], "protection epoch start"),
        _utc(
            acquisition["path_anchor_protection_epoch_completed_utc"],
            "anchor protection-epoch completion",
        ),
        _utc(acquisition["directory_inventory_started_utc"], "directory inventory start"),
        _utc(acquisition["directory_inventory_completed_utc"], "directory inventory completion"),
        _utc(acquisition["file_lock_acquisition_completed_utc"], "file-lock completion"),
        _utc(acquisition["acquisition_completed_utc"], "runtime acquisition completion"),
    )
    if list(acquisition_times) != sorted(acquisition_times):
        _refuse("host-runtime acquisition timestamps are not in the frozen order")
    latest_final_remeasurement = max(anchor_final_times + file_final_times)
    if any(time < latest_final_remeasurement for time in watch_pre_cancel_times):
        _refuse("a runtime watch was cancelled before all final remeasurements")
    latest_watch_release = max(watch_release_times)
    if _utc(
        release["all_runtime_change_watches_released_utc"],
        "all runtime watches released",
    ) != latest_watch_release:
        _refuse("all-watches-released UTC is not the latest watch release")
    if any(time < latest_watch_release for time in anchor_release_times + file_release_times):
        _refuse("an anchor or runtime-file handle was released before all watches")
    if release_completed < max(anchor_release_times + file_release_times + [latest_watch_release]):
        _refuse("host-runtime release completed before all retained resources closed")
    return release


def _validate_launch(value: Any, phase: str, orchestrator_pid: int) -> dict[str, Any]:
    record = _mapping(value, f"{phase} launch")
    _exact_fields(record, _LAUNCH_FIELDS, f"{phase} launch")
    constants = {
        "schema": "stage_f_durability_process_launch/v1",
        "phase": phase,
        "launch_and_thread_close_serialized": True,
        "launch_api": "CreateProcessW",
        "command_line_terminal_nul_present": True,
        "command_line_mutable_buffer": True,
        "process_security_attributes": "NULL",
        "thread_security_attributes": "NULL",
        "inherit_handles": False,
        "raw_creation_flags": 0,
        "environment_pointer": "NULL",
        "current_directory_pointer": "NULL",
        "startup_info_byte_count": 104,
        "startup_info_zero_initialized_before_cb_assignment": True,
        "startup_info_cb": 104,
        "startup_info_reserved_pointer": "NULL",
        "startup_info_desktop_pointer": "NULL",
        "startup_info_title_pointer": "NULL",
        "startup_info_x": 0,
        "startup_info_y": 0,
        "startup_info_x_size": 0,
        "startup_info_y_size": 0,
        "startup_info_x_count_chars": 0,
        "startup_info_y_count_chars": 0,
        "startup_info_fill_attribute": 0,
        "startup_info_dwflags": 0,
        "startup_info_show_window": 0,
        "startup_info_standard_input": "NULL",
        "startup_info_standard_output": "NULL",
        "startup_info_standard_error": "NULL",
        "startup_info_reserved2_byte_count": 0,
        "startup_info_reserved2_pointer": "NULL",
        "process_information_byte_count": 24,
        "process_information_zero_initialized_before_call": True,
        "create_process_input_images_unchanged_from_hash_through_call_entry": True,
        "create_process_memory_intervals_nonoverflowing": True,
        "create_process_memory_intervals_pairwise_disjoint": True,
        "create_process_memory_intervals_live_through_return": True,
        "process_information_interval_live_through_output_hash": True,
        "create_process_returned_nonzero": True,
        "returned_handles_distinct": True,
        "thread_close_api": "CloseHandle",
        "thread_close_returned_nonzero": True,
        "process_handle_retained_after_launch": True,
    }
    for field, wanted in constants.items():
        if type(wanted) is bool:
            if record[field] is not wanted:
                _refuse(f"{phase} launch {field} differs")
        elif record[field] != wanted:
            _refuse(f"{phase} launch {field} differs")
    if record["launch_actor_process_id"] != orchestrator_pid:
        _refuse(f"{phase} launch actor differs from orchestrator")
    _uint(record["launch_actor_thread_id"], 32, f"{phase} launch actor TID", positive=True)
    _identity(record["application_name_path_identity"], "stage_f_private_path/v1", f"{phase} application")
    command = _strict_base64(record["command_line_base64"], f"{phase} command line")
    if len(command) % 2 or command.endswith(b"\x00\x00"):
        _refuse(f"{phase} command line is not UTF-16LE without terminal NUL")
    try:
        command.decode("utf-16le", "strict")
    except UnicodeDecodeError as exc:
        raise BindingRefusal(f"{phase} command line is invalid UTF-16LE") from exc
    units = len(command) // 2
    if units != record["command_line_utf16_code_unit_count"] or not 1 <= units <= 32766:
        _refuse(f"{phase} command-line code-unit count differs")
    call_image = _strict_base64(
        record["command_line_buffer_call_time_bytes_base64"],
        f"{phase} command buffer",
    )
    if call_image != command + b"\x00\x00":
        _refuse(f"{phase} command buffer is not command plus one terminal NUL")
    capacity = units + 1
    if record["command_line_buffer_wchar_capacity"] != capacity:
        _refuse(f"{phase} command-buffer capacity differs")
    if record["command_line_buffer_byte_count_including_terminal_nul"] != 2 * capacity:
        _refuse(f"{phase} command-buffer byte count differs")
    command_base = _uint(record["command_line_buffer_base_address_uint64"], 64, f"{phase} command base", positive=True)
    command_count = len(call_image)
    if command_base > _UINT64_MAX - command_count or record["command_line_buffer_exclusive_end_address_uint64"] != command_base + command_count:
        _refuse(f"{phase} command-buffer interval differs or overflows")
    if record["command_line_buffer_call_time_sha256"] != hashlib.sha256(call_image).hexdigest():
        _refuse(f"{phase} command-buffer digest differs")
    if record["command_line_hash_input_address_uint64"] != command_base or record["command_line_hash_input_byte_count"] != command_count:
        _refuse(f"{phase} command-buffer hash input differs")
    startup = _strict_base64(record["startup_info_call_time_bytes_base64"], f"{phase} STARTUPINFO")
    expected_startup = struct.pack("<I", 104) + bytes(100)
    if startup != expected_startup or record["startup_info_call_time_sha256"] != hashlib.sha256(startup).hexdigest():
        _refuse(f"{phase} STARTUPINFOW image differs")
    startup_base = _uint(record["startup_info_address_uint64"], 64, f"{phase} STARTUPINFO base", positive=True)
    if startup_base > _UINT64_MAX - 104 or record["startup_info_exclusive_end_address_uint64"] != startup_base + 104:
        _refuse(f"{phase} STARTUPINFOW interval differs")
    if record["startup_info_hash_input_address_uint64"] != startup_base or record["startup_info_hash_input_byte_count"] != 104:
        _refuse(f"{phase} STARTUPINFOW hash input differs")
    pi_input = _strict_base64(record["process_information_input_bytes_base64"], f"{phase} PI input")
    if pi_input != bytes(24) or record["process_information_input_sha256"] != hashlib.sha256(pi_input).hexdigest():
        _refuse(f"{phase} PROCESS_INFORMATION input differs")
    pi_output = _strict_base64(record["process_information_output_bytes_base64"], f"{phase} PI output")
    if len(pi_output) != 24 or record["process_information_output_sha256"] != hashlib.sha256(pi_output).hexdigest():
        _refuse(f"{phase} PROCESS_INFORMATION output differs")
    pi_base = _uint(record["process_information_address_uint64"], 64, f"{phase} PI base", positive=True)
    if pi_base > _UINT64_MAX - 24 or record["process_information_exclusive_end_address_uint64"] != pi_base + 24:
        _refuse(f"{phase} PROCESS_INFORMATION interval differs")
    if record["process_information_input_hash_address_uint64"] != pi_base or record["process_information_output_hash_address_uint64"] != pi_base:
        _refuse(f"{phase} PROCESS_INFORMATION hash address differs")
    if record["process_information_input_hash_byte_count"] != 24 or record["process_information_output_hash_byte_count"] != 24:
        _refuse(f"{phase} PROCESS_INFORMATION hash count differs")
    parsed_process_handle, parsed_thread_handle, parsed_pid, parsed_tid = struct.unpack("<QQII", pi_output)
    if (
        parsed_process_handle != record["process_handle_value_uint64"]
        or parsed_thread_handle != record["thread_handle_value_uint64"]
        or parsed_pid != record["process_id"]
        or parsed_tid != record["thread_id"]
    ):
        _refuse(f"{phase} PROCESS_INFORMATION parsed projection differs")
    _handle(parsed_process_handle, f"{phase} process handle")
    _handle(parsed_thread_handle, f"{phase} thread handle")
    _uint(parsed_pid, 32, f"{phase} PID", positive=True)
    _uint(parsed_tid, 32, f"{phase} TID", positive=True)
    if parsed_process_handle == parsed_thread_handle:
        _refuse(f"{phase} returned handles are equal")
    if record["thread_close_input_handle_value_uint64"] != parsed_thread_handle:
        _refuse(f"{phase} thread close used a substituted handle")
    intervals = (
        (command_base, command_base + command_count),
        (startup_base, startup_base + 104),
        (pi_base, pi_base + 24),
    )
    for index, left in enumerate(intervals):
        for right in intervals[index + 1 :]:
            if max(left[0], right[0]) < min(left[1], right[1]):
                _refuse(f"{phase} CreateProcessW memory intervals overlap")
    create_started = _utc(record["create_process_started_utc"], f"{phase} create start")
    for field in (
        "command_line_hash_completed_utc",
        "startup_info_hash_completed_utc",
        "process_information_input_hash_completed_utc",
    ):
        if _utc(record[field], f"{phase}.{field}") > create_started:
            _refuse(f"{phase} input-image hash completed after CreateProcessW started")
    _ordered_times(
        record,
        (
            "create_process_started_utc",
            "create_process_completed_utc",
            "process_information_output_hash_completed_utc",
            "thread_close_started_utc",
            "thread_handle_closed_utc",
        ),
        f"{phase} launch",
    )
    if record["launch_utc"] != record["create_process_completed_utc"]:
        _refuse(f"{phase} launch_utc differs from CreateProcessW completion")
    return record


def _validate_restart(
    record_value: Any, *, expected_published_final_sha256: str
) -> dict[str, Any]:
    record = _mapping(record_value, "restart_observation")
    _exact_fields(record, _RESTART_FIELDS, "restart_observation")
    orchestrator = _validate_process_instance(record["orchestrator_process"], "orchestrator_process")
    terminated = _validate_process_instance(record["terminated_process"], "terminated_process")
    resumed = _validate_process_instance(record["resumed_process"], "resumed_process")
    instances = {
        (item["process_id"], item["creation_filetime_uint64"])
        for item in (orchestrator, terminated, resumed)
    }
    if len(instances) != 3:
        _refuse("orchestrator, terminated, and resumed process instances are not distinct")
    if record["process_identity_api"] != "GetProcessId_GetProcessTimes_QueryFullProcessImageNameW_GetCommandLineW_LOCKED_BOOTSTRAP_VERIFIED_INVOCATION":
        _refuse("restart process identity API differs")
    pre = _validate_launch(record["terminated_process_launch_observation"], "PRE_RESTART", orchestrator["process_id"])
    post = _validate_launch(record["resumed_process_launch_observation"], "POST_RESTART", orchestrator["process_id"])
    if (pre["process_id"], terminated["creation_filetime_uint64"]) != (terminated["process_id"], record["terminated_process_creation_filetime_uint64"]):
        _refuse("PRE_RESTART launch/process identity differs")
    if (post["process_id"], resumed["creation_filetime_uint64"]) != (resumed["process_id"], record["resumed_process_creation_filetime_uint64"]):
        _refuse("POST_RESTART launch/process identity differs")
    for prefix, launch, process in (("terminated", pre, terminated), ("resumed", post, resumed)):
        process_handle = launch["process_handle_value_uint64"]
        constants = {
            f"{prefix}_wait_api": "WaitForSingleObject",
            f"{prefix}_wait_timeout_milliseconds": _UINT32_MAX,
            f"{prefix}_wait_result": "WAIT_OBJECT_0",
            f"{prefix}_wait_result_raw": 0,
            f"{prefix}_query_calls_serialized": True,
            f"{prefix}_get_exit_code_api": "GetExitCodeProcess",
            f"{prefix}_get_exit_code_returned_nonzero": True,
            f"{prefix}_process_exit_code": 0,
            f"{prefix}_get_process_times_api": "GetProcessTimes",
            f"{prefix}_get_process_times_output_intervals_pairwise_disjoint": True,
            f"{prefix}_get_process_times_returned_nonzero": True,
            f"{prefix}_process_close_api": "CloseHandle",
            f"{prefix}_process_close_returned_nonzero": True,
        }
        for field, wanted in constants.items():
            if type(wanted) is bool:
                if record[field] is not wanted:
                    _refuse(f"restart {field} differs")
            elif record[field] != wanted:
                _refuse(f"restart {field} differs")
        if record[f"{prefix}_query_actor_process_id"] != orchestrator["process_id"]:
            _refuse(f"{prefix} query actor differs from orchestrator")
        if record[f"{prefix}_query_actor_thread_id"] != launch["launch_actor_thread_id"]:
            _refuse(f"{prefix} query actor thread differs from launch actor")
        for field in (
            f"{prefix}_wait_input_process_handle_value_uint64",
            f"{prefix}_get_exit_code_input_process_handle_value_uint64",
            f"{prefix}_get_process_times_input_process_handle_value_uint64",
            f"{prefix}_process_close_input_handle_value_uint64",
        ):
            if record[field] != process_handle:
                _refuse(f"{prefix} process operation used a substituted handle")
        _validate_output_storage(
            record[f"{prefix}_get_exit_code_output_observation"],
            bits=32,
            expected_value=0,
            label=f"{prefix} exit code output",
        )
        values = (
            ("creation", record[f"{prefix}_process_creation_filetime_uint64"]),
            ("exit", record[f"{prefix}_process_exit_filetime_uint64"]),
            ("kernel", record[f"{prefix}_process_kernel_filetime_uint64"]),
            ("user", record[f"{prefix}_process_user_filetime_uint64"]),
        )
        intervals: list[tuple[int, int]] = []
        for name, value in values:
            _uint(value, 64, f"{prefix} {name} FILETIME", positive=name in ("creation", "exit"))
            output = record[f"{prefix}_get_process_times_{name}_output_observation"]
            _validate_output_storage(output, bits=64, expected_value=value, label=f"{prefix} {name} FILETIME output")
            intervals.append((output["base_address_uint64"], output["exclusive_end_address_uint64"]))
        for index, left in enumerate(intervals):
            for right in intervals[index + 1 :]:
                if max(left[0], right[0]) < min(left[1], right[1]):
                    _refuse(f"{prefix} process-times output intervals overlap")
        if record[f"{prefix}_process_creation_filetime_uint64"] != process["creation_filetime_uint64"]:
            _refuse(f"{prefix} creation FILETIME differs from process instance")
        if (
            record[f"{prefix}_process_exit_filetime_uint64"]
            <= record[f"{prefix}_process_creation_filetime_uint64"]
        ):
            _refuse(f"{prefix} exit FILETIME does not follow creation FILETIME")
        order = (
            launch["launch_utc"],
            launch["process_information_output_hash_completed_utc"],
            launch["thread_close_started_utc"],
            launch["thread_handle_closed_utc"],
            record[f"{prefix}_wait_started_utc"],
            record[f"{prefix}_wait_completed_utc"],
            record[f"{prefix}_get_exit_code_started_utc"],
            record[f"{prefix}_get_exit_code_returned_utc"],
            record[f"{prefix}_get_exit_code_output_observation"]["output_hash_completed_utc"],
            record[f"{prefix}_get_exit_code_completed_utc"],
            record[f"{prefix}_get_process_times_started_utc"],
            record[f"{prefix}_get_process_times_returned_utc"],
            max(
                record[f"{prefix}_get_process_times_{name}_output_observation"]["output_hash_completed_utc"]
                for name in ("creation", "exit", "kernel", "user")
            ),
            record[f"{prefix}_get_process_times_completed_utc"],
            record[f"{prefix}_process_close_started_utc"],
            record[f"{prefix}_process_handle_closed_utc"],
        )
        parsed_order = [_utc(value, f"{prefix} frozen process order") for value in order]
        if parsed_order != sorted(parsed_order):
            _refuse(f"{prefix} wait/query/close order differs")
        process_exit_utc = _utc(
            record[f"{prefix}_process_exit_utc"], f"{prefix} process exit UTC"
        )
        if not (
            _utc(launch["launch_utc"], f"{prefix} process launch UTC")
            <= process_exit_utc
            <= _utc(
                record[f"{prefix}_wait_completed_utc"],
                f"{prefix} wait completion UTC",
            )
        ):
            _refuse(f"{prefix} process exit UTC is outside launch/wait completion")
    challenge = _mapping(record["challenge_preimage"], "challenge_preimage")
    _exact_fields(
        challenge,
        frozenset(
            {
                "schema",
                "orchestrator_process",
                "terminated_process",
                "published_final_sha256",
                "challenge_counter",
                "challenge_issued_utc",
            }
        ),
        "challenge_preimage",
    )
    if challenge["schema"] != "stage_f_durability_restart_challenge/v1":
        _refuse("restart challenge schema differs")
    if challenge["orchestrator_process"] != orchestrator or challenge["terminated_process"] != terminated:
        _refuse("restart challenge process binding differs")
    _uint(challenge["challenge_counter"], 64, "challenge counter", positive=True)
    _utc(challenge["challenge_issued_utc"], "challenge_issued_utc")
    if challenge["published_final_sha256"] != expected_published_final_sha256:
        _refuse("restart challenge names another published final digest")
    if record["challenge_sha256"] != sha256_hex(canonical_bytes(challenge)):
        _refuse("restart challenge digest differs")
    challenge_bytes = canonical_bytes(challenge)
    publication = _mapping(
        record["challenge_publication_observation"],
        "challenge_publication_observation",
    )
    _exact_fields(
        publication,
        _CHALLENGE_PUBLICATION_FIELDS,
        "challenge_publication_observation",
    )
    if publication["schema"] != "stage_f_durability_challenge_publication/v1":
        _refuse("challenge publication schema differs")
    if (
        publication["actor_process_id"],
        publication["actor_process_creation_filetime_uint64"],
    ) != (
        orchestrator["process_id"],
        orchestrator["creation_filetime_uint64"],
    ):
        _refuse("challenge publication actor differs from orchestrator")
    temporary_write_value = _mapping(
        publication["temporary_write_observation"],
        "challenge temporary write observation",
    )
    temporary_path_identity = _identity(
        temporary_write_value.get("target_path_identity"),
        "stage_f_private_path/v1",
        "challenge temporary path",
    )
    challenge_write = _validate_control_write(
        temporary_write_value,
        content_role="RESTART_CHALLENGE_TEMPORARY",
        actor_process=orchestrator,
        target_path_identity=temporary_path_identity,
        expected_bytes=challenge_bytes,
        label="challenge temporary write observation",
    )
    challenge_atomic = _validate_atomic_publication(
        publication["atomic_publication_observation"]
    )
    _same_identity(
        challenge_atomic["source_path_identity"],
        challenge_write["target_path_identity"],
        "challenge atomic source",
    )
    _same_identity(
        challenge_atomic["target_path_identity"],
        record["challenge_path_identity"],
        "challenge atomic final",
    )
    _same_identity(
        publication["published_path_identity"],
        record["challenge_path_identity"],
        "challenge published path",
    )
    if (
        publication["published_byte_count"] != len(challenge_bytes)
        or publication["published_sha256"] != record["challenge_sha256"]
        or publication["completed_before_launch"] is not True
    ):
        _refuse("challenge publication byte projection or completion differs")
    _validate_directory_durability(
        publication["directory_durability_observation"],
        challenge_atomic,
        actor_process=orchestrator,
        evidence_source=(
            "RESTART_CHALLENGE_ATOMIC_PUBLICATION_MOVEFILEEXW_WRITE_THROUGH"
        ),
        expected_observation_utc=None,
    )
    publication_completed = _utc(
        publication["directory_durability_observation"]["observation_utc"],
        "challenge publication completion",
    )
    challenge_order = (
        _utc(record["terminated_process_handle_closed_utc"], "terminated process close"),
        _utc(challenge["challenge_issued_utc"], "challenge issue"),
        _utc(challenge_write["create_started_utc"], "challenge write start"),
        publication_completed,
        _utc(
            record["resumed_process_launch_observation"]["create_process_started_utc"],
            "POST_RESTART CreateProcessW start",
        ),
    )
    if list(challenge_order) != sorted(challenge_order):
        _refuse("terminated close, challenge publication, and resumed launch order differs")
    acknowledgement = _mapping(record["acknowledgement_preimage"], "acknowledgement_preimage")
    _exact_fields(
        acknowledgement,
        frozenset({"schema", "challenge_sha256", "resumed_process", "acknowledged_utc"}),
        "acknowledgement_preimage",
    )
    if acknowledgement["schema"] != "stage_f_durability_restart_acknowledgement/v1":
        _refuse("restart acknowledgement schema differs")
    if acknowledgement["challenge_sha256"] != record["challenge_sha256"] or acknowledgement["resumed_process"] != resumed:
        _refuse("restart acknowledgement binding differs")
    if record["acknowledgement_sha256"] != sha256_hex(canonical_bytes(acknowledgement)):
        _refuse("restart acknowledgement digest differs")
    acknowledgement_bytes = canonical_bytes(acknowledgement)
    _identity(record["challenge_path_identity"], "stage_f_private_path/v1", "challenge path")
    _identity(record["acknowledgement_path_identity"], "stage_f_private_path/v1", "acknowledgement path")
    if record["challenge_path_identity"] == record["acknowledgement_path_identity"]:
        _refuse("challenge and acknowledgement paths are not distinct")
    if record["resumed_process_acknowledged_exact_challenge"] is not True:
        _refuse("resumed process did not acknowledge the exact challenge")
    acknowledgement_write = _validate_control_write(
        record["acknowledgement_write_observation"],
        content_role="RESTART_ACKNOWLEDGEMENT_FINAL",
        actor_process=resumed,
        target_path_identity=record["acknowledgement_path_identity"],
        expected_bytes=acknowledgement_bytes,
        label="acknowledgement write observation",
    )
    if acknowledgement_write["close_completed_utc"] != record["handshake_completed_utc"]:
        _refuse("restart handshake differs from acknowledgement close completion")
    if _utc(acknowledgement["acknowledged_utc"], "acknowledged_utc") > _utc(
        acknowledgement_write["create_started_utc"],
        "acknowledgement write start",
    ):
        _refuse("acknowledgement content time follows acknowledgement creation")
    if record["launch_utc"] != post["launch_utc"]:
        _refuse("receipt restart launch UTC differs from POST_RESTART launch")
    _ordered_times(
        record,
        ("launch_utc", "handshake_completed_utc", "restart_utc"),
        "restart handshake",
    )
    return record


def validate_durability_receipt(
    receipt_value: Mapping[str, Any],
    *,
    host_runtime_preimage: Mapping[str, Any] | None = None,
) -> None:
    """Validate the closed receipt's durability-specific semantic relations.

    The caller must additionally validate the complete evidence object against
    ``stage_f_local_execution_binding_evidence_schema.json``.  This function
    independently closes the receipt itself and recomputes its action, process,
    atomic-publication, directory-durability, recovery, and zero-science links.
    """

    receipt = _mapping(receipt_value, "durability receipt")
    _exact_fields(receipt, _RECEIPT_FIELDS, "durability receipt")
    if receipt["schema"] != "stage_f_durability_probe_receipt/v1":
        _refuse("durability receipt schema differs")
    identities = {
        "filesystem_identity": "stage_f_filesystem_binding/v1",
        "durability_policy_identity": "stage_f_durability_policy/v1",
        "restart_policy_identity": "stage_f_restart_policy/v1",
        "binding_validator_identity": "stage_f_binding_validator/v1",
        "execution_environment_policy_identity": "stage_f_execution_environment_policy/v1",
        "host_validation_runtime_identity": "stage_f_host_validation_runtime/v1",
        "synthetic_payload_identity": "stage_f_synthetic_durability_payload/v1",
        "temporary_path_identity": "stage_f_private_path/v1",
        "final_path_identity": "stage_f_private_path/v1",
        "directory_target_identity": "stage_f_private_path/v1",
        "storage_capacity_snapshot_identity": "stage_f_storage_capacity_snapshot/v1",
    }
    for field, kind in identities.items():
        _identity(receipt[field], kind, field)
    if not isinstance(host_runtime_preimage, Mapping):
        _refuse("retained host-validation runtime preimage is required")
    if (
        receipt["host_validation_runtime_identity"]["value"]
        != sha256_hex(canonical_bytes(host_runtime_preimage))
    ):
        _refuse("durability receipt host-runtime identity/preimage digest differs")
    path_identities = (
        receipt["temporary_path_identity"],
        receipt["final_path_identity"],
        receipt["directory_target_identity"],
    )
    if len({item["value"] for item in path_identities}) != 3:
        _refuse("temporary, final, and directory identities are not distinct")
    for field in (
        "synthetic_payload_sha256",
        "published_final_sha256",
        "post_restart_reread_sha256",
        "corrupt_fixture_sha256",
        "orphan_partial_sha256",
        "last_verified_durable_checkpoint_sha256",
        "recovered_final_sha256",
        "host_runtime_lock_acquisition_sha256",
        "receipt_sha256",
    ):
        _sha256(receipt[field], field)
    for field in (
        "synthetic_payload_byte_count",
        "post_restart_reread_byte_count",
        "corrupt_fixture_byte_count",
        "orphan_partial_byte_count",
        "observed_free_bytes",
    ):
        _uint(receipt[field], 64, field, positive=True)
    if receipt["reserved_envelope_bytes"] != 715112054784:
        _refuse("reserved envelope differs from 666 GiB")
    if receipt["action_count"] != 17:
        _refuse("durability action count differs")
    constants = {
        "recovery_disposition": "RECOVERED_LAST_VERIFIED_DURABLE_CHECKPOINT",
        "same_volume": True,
        "file_flush_completed": True,
        "directory_durability_completed": True,
        "directory_durability_primitive": "MoveFileExW_WRITE_THROUGH_TARGET_PARENT_METADATA_COMPLETION",
        "atomic_publication_completed": True,
        "restart_reread_completed": True,
        "content_hash_reconciled": True,
        "corrupt_final_refused": True,
        "orphan_partial_refused": True,
        "last_good_recovery_completed": True,
        "disposition": "STAGE_F_SYNTHETIC_DURABILITY_PASS",
    }
    for field, wanted in constants.items():
        if type(wanted) is bool:
            if receipt[field] is not wanted:
                _refuse(f"durability receipt {field} differs")
        elif receipt[field] != wanted:
            _refuse(f"durability receipt {field} differs")
    if receipt["file_durability_primitive"] not in ("FlushFileBuffers", "FSYNC"):
        _refuse("file durability primitive differs")
    payload_hash = receipt["synthetic_payload_sha256"]
    if receipt["synthetic_payload_identity"]["value"] != payload_hash:
        _refuse("synthetic payload identity digest differs from payload")
    for field in (
        "published_final_sha256",
        "post_restart_reread_sha256",
        "last_verified_durable_checkpoint_sha256",
        "recovered_final_sha256",
    ):
        if receipt[field] != payload_hash:
            _refuse(f"durable checkpoint hash projection differs: {field}")
    if receipt["post_restart_reread_byte_count"] != receipt["synthetic_payload_byte_count"]:
        _refuse("post-restart byte count differs from payload")
    fixture_hashes = {receipt["corrupt_fixture_sha256"], receipt["orphan_partial_sha256"]}
    if len(fixture_hashes) != 2 or payload_hash in fixture_hashes:
        _refuse("corrupt and orphan fixture hashes are not distinct refusals")
    validate_no_science_counters(receipt["scientific_counters"])
    acquisition = _mapping(
        receipt["host_runtime_lock_acquisition_preimage"],
        "host_runtime_lock_acquisition_preimage",
    )
    if sha256_hex(canonical_bytes(acquisition)) != receipt["host_runtime_lock_acquisition_sha256"]:
        _refuse("host-runtime-lock acquisition digest differs")
    _same_identity(
        acquisition["host_validation_runtime_identity"],
        receipt["host_validation_runtime_identity"],
        "host-runtime-lock acquisition identity",
    )
    restart = _validate_restart(
        receipt["restart_observation"],
        expected_published_final_sha256=receipt["published_final_sha256"],
    )
    invocation_rows = (
        _validate_invocation(
            receipt["orchestrator_probe_invocation_preimage"],
            phase="ORCHESTRATOR",
            receipt=receipt,
        ),
        _validate_invocation(
            receipt["terminated_probe_invocation_preimage"],
            phase="PRE_RESTART",
            receipt=receipt,
        ),
        _validate_invocation(
            receipt["resumed_probe_invocation_preimage"],
            phase="POST_RESTART",
            receipt=receipt,
        ),
    )
    invocations = tuple(row[0] for row in invocation_rows)
    if len({row["invocation_preimage_path_identity"]["value"] for row in invocations}) != 3:
        _refuse("durability invocation paths are not pairwise distinct")
    for field in (
        "binding_validator_identity",
        "execution_environment_policy_identity",
        "host_validation_runtime_identity",
        "host_runtime_lock_acquisition_sha256",
        "validator_zipapp_path_identity",
        "validator_zipapp_byte_count",
        "validator_zipapp_sha256",
    ):
        if any(row[field] != invocations[0][field] for row in invocations[1:]):
            _refuse(f"durability invocations mix {field}")
    if any(row[1] != invocation_rows[0][1] for row in invocation_rows[1:]):
        _refuse("durability invocations mix locked-bootstrap bytes")
    post = invocations[2]
    if (
        post["restart_challenge_sha256"] != restart["challenge_sha256"]
        or post["restart_challenge_path_identity"] != restart["challenge_path_identity"]
        or post["acknowledgement_path_identity"] != restart["acknowledgement_path_identity"]
    ):
        _refuse("POST_RESTART invocation differs from challenge/acknowledgement chain")
    processes = (
        restart["orchestrator_process"],
        restart["terminated_process"],
        restart["resumed_process"],
    )
    _validate_host_runtime_inventory(
        acquisition,
        host_runtime_preimage,
        processes=processes,
    )
    for phase, process, invocation_row in zip(
        ("ORCHESTRATOR", "PRE_RESTART", "POST_RESTART"),
        processes,
        invocation_rows,
        strict=True,
    ):
        invocation, _bootstrap, command = invocation_row
        invocation_digest = sha256_hex(canonical_bytes(invocation))
        if process["invocation_sha256"] != invocation_digest:
            _refuse(f"{phase} process invocation digest differs")
        _same_identity(
            process["executable_path_identity"],
            invocation["executable_path_identity"],
            f"{phase} process executable",
        )
        if process["command_line_sha256"] != hashlib.sha256(command).hexdigest():
            _refuse(f"{phase} process command-line digest differs")
    for phase, launch, process, invocation_row in (
        (
            "PRE_RESTART",
            restart["terminated_process_launch_observation"],
            processes[1],
            invocation_rows[1],
        ),
        (
            "POST_RESTART",
            restart["resumed_process_launch_observation"],
            processes[2],
            invocation_rows[2],
        ),
    ):
        invocation, _bootstrap, command = invocation_row
        _same_identity(
            launch["application_name_path_identity"],
            invocation["executable_path_identity"],
            f"{phase} launch executable",
        )
        if _strict_base64(launch["command_line_base64"], f"{phase} launch command") != command:
            _refuse(f"{phase} launch command differs from retained invocation")
        if launch["process_id"] != process["process_id"]:
            _refuse(f"{phase} launch PID differs from process instance")
    lock_fields = (
        "orchestrator_artifact_lock_observation",
        "terminated_artifact_lock_observation",
        "resumed_artifact_lock_observation",
    )
    lock_roles = (
        "ORCHESTRATOR_PROCESS",
        "TERMINATED_PROBE_PROCESS",
        "RESUMED_PROBE_PROCESS",
    )
    artifact_locks: list[dict[str, Any]] = []
    for field, role, process, invocation in zip(
        lock_fields, lock_roles, processes, invocations, strict=True
    ):
        artifact_locks.append(
            _validate_artifact_lock(
                receipt[field],
                role=role,
                process=process,
                invocation=invocation,
                receipt=receipt,
            )
        )
    validate_durability_action_trace(receipt["ordered_actions"], receipt=receipt)
    action_times = [
        _utc(row["observed_utc"], f"durability action {index} UTC")
        for index, row in enumerate(receipt["ordered_actions"], start=1)
    ]
    if not (
        action_times[6]
        <= _utc(restart["terminated_process_exit_utc"], "terminated process exit")
        <= _utc(restart["terminated_wait_started_utc"], "terminated wait start")
        <= _utc(restart["terminated_process_handle_closed_utc"], "terminated process close")
        <= _utc(restart["launch_utc"], "resumed launch")
        <= _utc(restart["handshake_completed_utc"], "restart handshake")
        <= _utc(restart["restart_utc"], "restart UTC")
        <= action_times[7]
    ):
        _refuse("termination, restart handshake, and fresh-process action order differs")
    if not (
        action_times[16]
        <= _utc(restart["resumed_process_exit_utc"], "resumed process exit")
        <= _utc(restart["resumed_wait_started_utc"], "resumed wait start")
    ):
        _refuse("resumed process wait began before action 17")
    if any(
        action_time < _utc(restart["handshake_completed_utc"], "restart handshake")
        for action_time in action_times[7:]
    ):
        _refuse("a post-restart action precedes the durable acknowledgement")
    if not (
        _utc(artifact_locks[1]["lock_acquired_utc"], "terminated artifact lock start")
        <= action_times[0]
        <= action_times[6]
        <= _utc(artifact_locks[1]["lock_released_utc"], "terminated artifact lock release")
        and _utc(artifact_locks[2]["lock_acquired_utc"], "resumed artifact lock start")
        <= _utc(
            restart["acknowledgement_write_observation"]["create_started_utc"],
            "acknowledgement create start",
        )
        <= action_times[7]
        <= action_times[16]
        <= _utc(artifact_locks[2]["lock_released_utc"], "resumed artifact lock release")
        and _utc(artifact_locks[0]["lock_acquired_utc"], "orchestrator artifact lock start")
        <= _utc(receipt["probe_started_utc"], "probe start")
        <= _utc(receipt["probe_completed_utc"], "probe completion")
        <= _utc(artifact_locks[0]["lock_released_utc"], "orchestrator artifact lock release")
    ):
        _refuse("validator artifact-lock lifetime does not span its bound work")
    host_release = _validate_host_runtime_lock_release(
        acquisition,
        receipt["host_runtime_lock_release_observation"],
        processes=processes,
        invocations=invocations,
    )
    atomic = _validate_atomic_publication(receipt["atomic_publication_observation"])
    _same_identity(atomic["source_path_identity"], receipt["temporary_path_identity"], "atomic temporary")
    _same_identity(atomic["target_path_identity"], receipt["final_path_identity"], "atomic final")
    _validate_directory_durability(
        receipt["directory_durability_observation"],
        atomic,
        actor_process=restart["terminated_process"],
        evidence_source=(
            "SYNTHETIC_PAYLOAD_ATOMIC_PUBLICATION_ACTION_5_MOVEFILEEXW_WRITE_THROUGH"
        ),
        expected_observation_utc=receipt["ordered_actions"][5]["observed_utc"],
    )
    _same_identity(
        receipt["directory_durability_observation"]["target_parent_path_identity"],
        receipt["directory_target_identity"],
        "directory target parent",
    )
    started = _utc(receipt["probe_started_utc"], "probe_started_utc")
    completed = _utc(receipt["probe_completed_utc"], "probe_completed_utc")
    if started > completed:
        _refuse("probe completion precedes start")
    if _utc(
        acquisition["acquisition_completed_utc"],
        "host-runtime acquisition completion",
    ) > started:
        _refuse("host-runtime acquisition did not complete before the probe")
    if _utc(host_release["release_completed_utc"], "host-runtime release completion") > completed:
        _refuse("host-runtime release completes after durability receipt")
    # The canonical helper independently enforces omission of only receipt_sha256.
    verify_embedded_digest(
        receipt,
        "receipt_sha256",
        kind="stage_f_durability_probe_receipt/v1",
    )


def _path(value: os.PathLike[str] | str, label: str) -> Path:
    try:
        path = Path(value)
    except TypeError as exc:
        raise BindingRefusal(f"{label} is not a filesystem path") from exc
    if not path.is_absolute():
        _refuse(f"{label} must be absolute")
    return path


def _ensure_fresh_regular(path: Path, label: str) -> None:
    try:
        current = path.lstat()
    except FileNotFoundError:
        return
    if stat.S_ISLNK(current.st_mode):
        _refuse(f"{label} is a symlink")
    _refuse(f"{label} already exists")


def _same_volume(source: Path, target_parent: Path) -> bool:
    return source.stat().st_dev == target_parent.stat().st_dev


def _write_all_fd(fd: int, payload: bytes) -> None:
    offset = 0
    while offset < len(payload):
        written = os.write(fd, payload[offset:])
        if written <= 0:
            _refuse("checkpoint write made no progress")
        offset += written


def _windows_error(operation: str) -> BindingRefusal:
    error = ctypes.get_last_error()
    return BindingRefusal(f"{operation} failed with Win32 error {error}")


def _windows_write_temporary(payload: bytes, temporary: Path) -> str:
    """CREATE_NEW, write, FlushFileBuffers, and close one exact handle."""

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
    write_file = kernel32.WriteFile
    write_file.argtypes = (
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_void_p,
    )
    write_file.restype = ctypes.c_int
    flush_file_buffers = kernel32.FlushFileBuffers
    flush_file_buffers.argtypes = (ctypes.c_void_p,)
    flush_file_buffers.restype = ctypes.c_int
    close_handle = kernel32.CloseHandle
    close_handle.argtypes = (ctypes.c_void_p,)
    close_handle.restype = ctypes.c_int

    # GENERIC_WRITE, zero sharing, CREATE_NEW, and exact
    # FILE_FLAG_WRITE_THROUGH.  FlushFileBuffers remains mandatory.
    handle = create_file(
        str(temporary),
        0x40000000,
        0,
        None,
        1,
        0x80000000,
        None,
    )
    if handle in (None, ctypes.c_void_p(-1).value):
        raise _windows_error("CreateFileW(CREATE_NEW)")
    failure: BaseException | None = None
    try:
        offset = 0
        while offset < len(payload):
            chunk = payload[offset : offset + _UINT32_MAX]
            buffer = ctypes.create_string_buffer(chunk, len(chunk))
            written = ctypes.c_uint32(0)
            if not write_file(handle, buffer, len(chunk), ctypes.byref(written), None):
                raise _windows_error("WriteFile")
            if written.value != len(chunk) or written.value == 0:
                _refuse("WriteFile did not write the exact requested checkpoint bytes")
            offset += written.value
        if not flush_file_buffers(handle):
            raise _windows_error("FlushFileBuffers")
    except BaseException as exc:
        failure = exc
    if not close_handle(handle):
        close_failure = _windows_error("CloseHandle(checkpoint temporary)")
        if failure is None:
            raise close_failure
    if failure is not None:
        raise failure
    return "FlushFileBuffers"


def _write_temporary(payload: bytes, temporary: Path) -> str:
    if sys.platform == "win32":
        return _windows_write_temporary(payload, temporary)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_BINARY"):
        flags |= os.O_BINARY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(temporary, flags, 0o600)
    except OSError as exc:
        raise BindingRefusal(f"cannot create fresh checkpoint temporary: {exc}") from exc
    try:
        _write_all_fd(fd, payload)
        os.fsync(fd)
    except Exception:
        try:
            os.close(fd)
        finally:
            raise
    else:
        os.close(fd)
    return "FSYNC"


def _movefileex_write_through(source: Path, target: Path) -> None:
    if sys.platform != "win32":
        _refuse("MoveFileExW durability is available only on Windows")
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    move = kernel32.MoveFileExW
    move.argtypes = (ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32)
    move.restype = ctypes.c_int
    if not move(str(source), str(target), 8):
        error = ctypes.get_last_error()
        raise BindingRefusal(f"MoveFileExW(MOVEFILE_WRITE_THROUGH) failed: {error}")


def _renameat2_noreplace(source: Path, target: Path) -> None:
    if not sys.platform.startswith("linux"):
        _refuse("synthetic no-replace atomic rename is unavailable on this platform")
    library = ctypes.CDLL(None, use_errno=True)
    try:
        renameat2 = library.renameat2
    except AttributeError as exc:
        raise BindingRefusal("renameat2(RENAME_NOREPLACE) is unavailable") from exc
    renameat2.argtypes = (
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_uint,
    )
    renameat2.restype = ctypes.c_int
    source_bytes = os.fsencode(source)
    target_bytes = os.fsencode(target)
    if renameat2(-100, source_bytes, -100, target_bytes, 1) != 0:
        error = ctypes.get_errno()
        raise BindingRefusal(
            f"renameat2(RENAME_NOREPLACE) failed: {os.strerror(error)}"
        )


def _fsync_directory(path: Path) -> None:
    flags = os.O_RDONLY
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    fd = os.open(path, flags)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def atomic_publish(
    temporary_path: os.PathLike[str] | str,
    final_path: os.PathLike[str] | str,
    *,
    synthetic: bool = False,
) -> dict[str, Any]:
    """Publish a fresh temporary to a fresh final path without replacement.

    Windows uses exactly ``MoveFileExW`` flag 8.  Linux support is a
    non-evidence synthetic control using ``renameat2(RENAME_NOREPLACE)`` plus a
    parent-directory fsync.  No copy, overwrite, or fallback rename exists.
    """

    temporary = _path(temporary_path, "temporary_path")
    final = _path(final_path, "final_path")
    if temporary == final:
        _refuse("temporary and final paths must differ")
    try:
        source_stat = temporary.lstat()
    except FileNotFoundError as exc:
        raise BindingRefusal("checkpoint temporary does not exist") from exc
    if stat.S_ISLNK(source_stat.st_mode) or not stat.S_ISREG(source_stat.st_mode):
        _refuse("checkpoint temporary must be a non-symlink regular file")
    _ensure_fresh_regular(final, "final_path")
    if not final.parent.is_dir() or final.parent.is_symlink():
        _refuse("final parent must be an existing non-symlink directory")
    if not _same_volume(temporary, final.parent):
        _refuse("atomic publication paths are on different volumes")
    if sys.platform == "win32":
        _movefileex_write_through(temporary, final)
        primitive = "MoveFileExW"
        raw_flags = 8
        directory_primitive = "MoveFileExW_WRITE_THROUGH_TARGET_PARENT_METADATA_COMPLETION"
    else:
        if synthetic is not True:
            _refuse("non-Windows durability operations are synthetic-only")
        _renameat2_noreplace(temporary, final)
        _fsync_directory(final.parent)
        primitive = "renameat2"
        raw_flags = 1
        directory_primitive = "FSYNC"
    if temporary.exists() or not final.is_file() or final.is_symlink():
        _refuse("atomic publication postconditions failed")
    return {
        "primitive": primitive,
        "raw_flags": raw_flags,
        "replace_existing": False,
        "same_volume": True,
        "source_absent_after_call": True,
        "target_present_after_call": True,
        "target_created_once": True,
        "target_overwrite_attempt_count": 0,
        "directory_durability_primitive": directory_primitive,
        "synthetic_non_evidence": sys.platform != "win32",
    }


def write_checkpoint(
    payload: bytes,
    temporary_path: os.PathLike[str] | str,
    final_path: os.PathLike[str] | str,
    *,
    synthetic: bool = False,
) -> dict[str, Any]:
    """Write, fsync/flush, close, and atomically publish caller-supplied bytes."""

    if type(payload) is not bytes or not payload:
        _refuse("checkpoint payload must be nonempty exact bytes")
    temporary = _path(temporary_path, "temporary_path")
    final = _path(final_path, "final_path")
    _ensure_fresh_regular(temporary, "temporary_path")
    _ensure_fresh_regular(final, "final_path")
    if temporary.parent.is_symlink() or not temporary.parent.is_dir():
        _refuse("temporary parent must be an existing non-symlink directory")
    file_primitive = _write_temporary(payload, temporary)
    publication = atomic_publish(temporary, final, synthetic=synthetic)
    verified = verify_checkpoint_hash(
        final,
        hashlib.sha256(payload).hexdigest(),
        expected_byte_count=len(payload),
        synthetic=synthetic,
    )
    return {
        "byte_count": verified["byte_count"],
        "sha256": verified["sha256"],
        "file_durability_primitive": "FlushFileBuffers" if sys.platform == "win32" else file_primitive,
        "publication": publication,
        "scientific_counters": dict(ZERO_SCIENCE_COUNTERS),
    }


class _FILE_STANDARD_INFO(ctypes.Structure):
    _fields_ = (
        ("AllocationSize", ctypes.c_int64),
        ("EndOfFile", ctypes.c_int64),
        ("NumberOfLinks", ctypes.c_uint32),
        ("DeletePending", ctypes.c_ubyte),
        ("Directory", ctypes.c_ubyte),
        ("_padding", ctypes.c_ubyte * 2),
    )


class _FILE_ID_128(ctypes.Structure):
    _fields_ = (("Identifier", ctypes.c_ubyte * 16),)


class _FILE_ID_INFO(ctypes.Structure):
    _fields_ = (
        ("VolumeSerialNumber", ctypes.c_uint64),
        ("FileId", _FILE_ID_128),
    )


class _FILE_ATTRIBUTE_TAG_INFO(ctypes.Structure):
    _fields_ = (
        ("FileAttributes", ctypes.c_uint32),
        ("ReparseTag", ctypes.c_uint32),
    )


def _windows_query_file_info(
    query: Any,
    handle: int,
) -> tuple[tuple[int, int, int, int, int], tuple[int, bytes], tuple[int, int]]:
    standard = _FILE_STANDARD_INFO()
    file_id = _FILE_ID_INFO()
    attribute = _FILE_ATTRIBUTE_TAG_INFO()
    for info_class, value, label in (
        (1, standard, "FileStandardInfo"),
        (18, file_id, "FileIdInfo"),
        (9, attribute, "FileAttributeTagInfo"),
    ):
        if not query(handle, info_class, ctypes.byref(value), ctypes.sizeof(value)):
            raise _windows_error(f"GetFileInformationByHandleEx({label})")
    standard_tuple = (
        int(standard.AllocationSize),
        int(standard.EndOfFile),
        int(standard.NumberOfLinks),
        int(standard.DeletePending),
        int(standard.Directory),
    )
    file_id_tuple = (int(file_id.VolumeSerialNumber), bytes(file_id.FileId.Identifier))
    attribute_tuple = (int(attribute.FileAttributes), int(attribute.ReparseTag))
    return standard_tuple, file_id_tuple, attribute_tuple


def _windows_read_stable(path: Path) -> tuple[int, str, bytes]:
    """Read one deny-write/delete held handle and prove its identity stayed fixed."""

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
    query = kernel32.GetFileInformationByHandleEx
    query.argtypes = (ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_uint32)
    query.restype = ctypes.c_int
    read_file = kernel32.ReadFile
    read_file.argtypes = (
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_void_p,
    )
    read_file.restype = ctypes.c_int
    close_handle = kernel32.CloseHandle
    close_handle.argtypes = (ctypes.c_void_p,)
    close_handle.restype = ctypes.c_int

    # GENERIC_READ, FILE_SHARE_READ only, OPEN_EXISTING,
    # FILE_FLAG_OPEN_REPARSE_POINT: the held object denies mutation/replacement.
    handle = create_file(str(path), 0x80000000, 1, None, 3, 0x00200000, None)
    if handle in (None, ctypes.c_void_p(-1).value):
        raise _windows_error("CreateFileW(checkpoint read-only)")
    failure: BaseException | None = None
    result: tuple[int, str, bytes] | None = None
    try:
        before = _windows_query_file_info(query, handle)
        standard, _, attribute = before
        if standard[1] < 0 or standard[2] != 1 or standard[3] or standard[4]:
            _refuse("checkpoint held handle is not one live single-link regular file")
        if attribute[0] & 0x400 or attribute[1] != 0:
            _refuse("checkpoint held handle is a reparse point")
        digest = hashlib.sha256()
        chunks: list[bytes] = []
        buffer = ctypes.create_string_buffer(1024 * 1024)
        while True:
            read = ctypes.c_uint32(0)
            if not read_file(handle, buffer, len(buffer), ctypes.byref(read), None):
                raise _windows_error("ReadFile(checkpoint)")
            if read.value == 0:
                break
            chunk = buffer.raw[: read.value]
            digest.update(chunk)
            chunks.append(chunk)
        after = _windows_query_file_info(query, handle)
        if before != after:
            _refuse("checkpoint metadata or file identity changed while held for hashing")
        payload = b"".join(chunks)
        if len(payload) != standard[1]:
            _refuse("checkpoint reread byte count differs from FileStandardInfo.EndOfFile")
        result = (len(payload), digest.hexdigest(), payload)
    except BaseException as exc:
        failure = exc
    if not close_handle(handle):
        close_failure = _windows_error("CloseHandle(checkpoint read-only)")
        if failure is None:
            raise close_failure
    if failure is not None:
        raise failure
    if result is None:
        _refuse("checkpoint read produced no result")
    return result


def _read_stable(path: Path) -> tuple[int, str, bytes]:
    if sys.platform == "win32":
        return _windows_read_stable(path)
    flags = os.O_RDONLY
    if hasattr(os, "O_BINARY"):
        flags |= os.O_BINARY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        raise BindingRefusal(f"cannot open checkpoint read-only: {exc}") from exc
    digest = hashlib.sha256()
    chunks: list[bytes] = []
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode):
            _refuse("checkpoint is not a regular file")
        while True:
            chunk = os.read(fd, 1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
            chunks.append(chunk)
        after = os.fstat(fd)
    finally:
        os.close(fd)
    stable = (
        before.st_dev,
        before.st_ino,
        before.st_size,
        before.st_mtime_ns,
    ) == (
        after.st_dev,
        after.st_ino,
        after.st_size,
        after.st_mtime_ns,
    )
    if not stable:
        _refuse("checkpoint changed while held for hashing")
    payload = b"".join(chunks)
    if len(payload) != after.st_size:
        _refuse("checkpoint reread byte count differs from file size")
    return len(payload), digest.hexdigest(), payload


def _verified_checkpoint_payload(
    path: Path,
    expected_sha256: str,
    *,
    expected_byte_count: int | None = None,
    synthetic: bool = False,
) -> tuple[dict[str, Any], bytes]:
    _sha256(expected_sha256, "expected_sha256")
    if sys.platform != "win32" and synthetic is not True:
        _refuse("non-Windows checkpoint verification is synthetic-only")
    try:
        path_stat = path.lstat()
    except FileNotFoundError as exc:
        raise BindingRefusal("checkpoint is absent") from exc
    if stat.S_ISLNK(path_stat.st_mode) or not stat.S_ISREG(path_stat.st_mode):
        _refuse("checkpoint must be a non-symlink regular file")
    byte_count, digest, payload = _read_stable(path)
    if expected_byte_count is not None:
        _uint(expected_byte_count, 64, "expected_byte_count")
        if byte_count != expected_byte_count:
            _refuse("checkpoint byte count differs")
    if digest != expected_sha256:
        _refuse("checkpoint SHA-256 differs")
    return ({
        "byte_count": byte_count,
        "sha256": digest,
        "scientific_counters": dict(ZERO_SCIENCE_COUNTERS),
    }, payload)


def verify_checkpoint_hash(
    checkpoint_path: os.PathLike[str] | str,
    expected_sha256: str,
    *,
    expected_byte_count: int | None = None,
    synthetic: bool = False,
) -> dict[str, Any]:
    """Reread a held regular file completely and reconcile count and SHA-256."""

    verified, _payload = _verified_checkpoint_payload(
        _path(checkpoint_path, "checkpoint_path"),
        expected_sha256,
        expected_byte_count=expected_byte_count,
        synthetic=synthetic,
    )
    return verified


def recover_checkpoint(
    last_good_path: os.PathLike[str] | str,
    recovered_path: os.PathLike[str] | str,
    expected_sha256: str,
    *,
    expected_byte_count: int | None = None,
    orphan_partial_paths: Sequence[os.PathLike[str] | str] = (),
    synthetic: bool = False,
) -> dict[str, Any]:
    """Recover only from a verified last-good checkpoint to a fresh final path."""

    last_good = _path(last_good_path, "last_good_path")
    recovered = _path(recovered_path, "recovered_path")
    if last_good == recovered:
        _refuse("last-good and recovered paths must differ")
    for orphan_value in orphan_partial_paths:
        orphan = _path(orphan_value, "orphan_partial_path")
        if orphan.exists() or orphan.is_symlink():
            _refuse("orphan partial is present and must be refused")
    verified, payload = _verified_checkpoint_payload(
        last_good,
        expected_sha256,
        expected_byte_count=expected_byte_count,
        synthetic=synthetic,
    )
    temporary = recovered.with_name(recovered.name + ".partial")
    _ensure_fresh_regular(temporary, "recovery temporary")
    _ensure_fresh_regular(recovered, "recovered_path")
    published = write_checkpoint(
        payload,
        temporary,
        recovered,
        synthetic=synthetic,
    )
    if published["sha256"] != verified["sha256"] or published["byte_count"] != verified["byte_count"]:
        _refuse("recovered checkpoint differs from last verified durable checkpoint")
    return {
        "recovery_disposition": "RECOVERED_LAST_VERIFIED_DURABLE_CHECKPOINT",
        "byte_count": published["byte_count"],
        "sha256": published["sha256"],
        "scientific_counters": dict(ZERO_SCIENCE_COUNTERS),
    }


class _WIN32_FIND_STREAM_DATA(ctypes.Structure):
    _fields_ = (("StreamSize", ctypes.c_int64), ("cStreamName", ctypes.c_wchar * 296))


class _WIN32_STREAM_ID(ctypes.Structure):
    _fields_ = (
        ("dwStreamId", ctypes.c_uint32),
        ("dwStreamAttributes", ctypes.c_uint32),
        ("Size", ctypes.c_int64),
        ("dwStreamNameSize", ctypes.c_uint32),
    )


_INVENTORY_PROHIBITED_ATTRIBUTES = (
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


def _windows_inventory_data_streams(path: Path) -> list[dict[str, Any]]:
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    first = kernel32.FindFirstStreamW
    first.argtypes = (
        ctypes.c_wchar_p,
        ctypes.c_int,
        ctypes.POINTER(_WIN32_FIND_STREAM_DATA),
        ctypes.c_uint32,
    )
    first.restype = ctypes.c_void_p
    next_stream = kernel32.FindNextStreamW
    next_stream.argtypes = (ctypes.c_void_p, ctypes.POINTER(_WIN32_FIND_STREAM_DATA))
    next_stream.restype = ctypes.c_int
    close = kernel32.FindClose
    close.argtypes = (ctypes.c_void_p,)
    close.restype = ctypes.c_int
    row = _WIN32_FIND_STREAM_DATA()
    handle = first(os.fspath(path), 0, ctypes.byref(row), 0)
    if handle == ctypes.c_void_p(-1).value:
        if ctypes.get_last_error() == 38:
            return []
        raise _windows_error("FindFirstStreamW(inventory)")
    result: list[dict[str, Any]] = []
    failure: BaseException | None = None
    try:
        while True:
            result.append(
                {
                    "stream_name": row.cStreamName,
                    "stream_size_bytes": int(row.StreamSize),
                }
            )
            if not next_stream(handle, ctypes.byref(row)):
                if ctypes.get_last_error() != 38:
                    raise _windows_error("FindNextStreamW(inventory)")
                break
    except BaseException as exc:
        failure = exc
    if not close(handle) and failure is None:
        raise _windows_error("FindClose(inventory)")
    if failure is not None:
        raise failure
    return result


def _windows_backup_streams(handle: int) -> list[dict[str, Any]]:
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    backup_read = kernel32.BackupRead
    backup_read.argtypes = (
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_int,
        ctypes.c_int,
        ctypes.POINTER(ctypes.c_void_p),
    )
    backup_read.restype = ctypes.c_int
    context = ctypes.c_void_p()

    def read_up_to(count: int) -> bytes:
        buffer = ctypes.create_string_buffer(count)
        read = ctypes.c_uint32(0)
        if not backup_read(
            handle,
            buffer,
            count,
            ctypes.byref(read),
            False,
            True,
            ctypes.byref(context),
        ):
            raise _windows_error("BackupRead(inventory)")
        return buffer.raw[: read.value]

    def read_exact(count: int) -> bytes:
        chunks: list[bytes] = []
        remaining = count
        while remaining:
            chunk = read_up_to(min(remaining, 1024 * 1024))
            if not chunk:
                _refuse("BackupRead ended before the declared stream length")
            chunks.append(chunk)
            remaining -= len(chunk)
        return b"".join(chunks)

    labels = {1: "BACKUP_DATA", 3: "BACKUP_SECURITY_DATA", 5: "BACKUP_LINK"}
    masks = {1: 0, 3: 2, 5: 0}
    result: list[dict[str, Any]] = []
    failure: BaseException | None = None
    try:
        header_size = ctypes.sizeof(_WIN32_STREAM_ID)
        while True:
            header_raw = read_up_to(header_size)
            if not header_raw:
                break
            if len(header_raw) != header_size:
                _refuse("BackupRead returned a partial stream header")
            header = _WIN32_STREAM_ID.from_buffer_copy(header_raw)
            stream_id = int(header.dwStreamId)
            attributes = int(header.dwStreamAttributes)
            size = int(header.Size)
            name_size = int(header.dwStreamNameSize)
            if (
                stream_id not in labels
                or attributes != masks[stream_id]
                or size < 0
                or name_size != 0
            ):
                _refuse("BackupRead exposed a forbidden stream id, mask, size, or name")
            digest = hashlib.sha256()
            remaining = size
            while remaining:
                chunk = read_exact(min(remaining, 1024 * 1024))
                digest.update(chunk)
                remaining -= len(chunk)
            result.append(
                {
                    "stream_id": labels[stream_id],
                    "stream_id_uint32": stream_id,
                    "stream_attributes": attributes,
                    "stream_size_bytes": size,
                    "stream_name": None,
                    "stream_content_sha256": digest.hexdigest(),
                }
            )
    except BaseException as exc:
        failure = exc
    aborted = ctypes.c_uint32(0)
    if not backup_read(
        handle,
        None,
        0,
        ctypes.byref(aborted),
        True,
        True,
        ctypes.byref(context),
    ) and failure is None:
        raise _windows_error("BackupRead(abort inventory)")
    if failure is not None:
        raise failure
    return result


def _windows_retrieval_extents(handle: int) -> tuple[str, str, list[dict[str, int]]]:
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    device_io = kernel32.DeviceIoControl
    device_io.argtypes = (
        ctypes.c_void_p,
        ctypes.c_uint32,
        ctypes.c_void_p,
        ctypes.c_uint32,
        ctypes.c_void_p,
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_void_p,
    )
    device_io.restype = ctypes.c_int
    starting_vcn = ctypes.c_int64(0)
    result: list[dict[str, int]] = []
    initial = "EXTENTS_FOUND"
    terminal = "SUCCESS_COMPLETE"
    first_call = True
    while True:
        output = ctypes.create_string_buffer(1024 * 1024)
        returned = ctypes.c_uint32(0)
        ctypes.set_last_error(0)
        success = device_io(
            handle,
            0x00090073,
            ctypes.byref(starting_vcn),
            ctypes.sizeof(starting_vcn),
            output,
            len(output),
            ctypes.byref(returned),
            None,
        )
        error = 0 if success else ctypes.get_last_error()
        if not success and error == 38 and first_call and returned.value == 0:
            return "ERROR_HANDLE_EOF_RESIDENT", "ERROR_HANDLE_EOF", []
        if not success and error not in (38, 234):
            raise _windows_error("DeviceIoControl(FSCTL_GET_RETRIEVAL_POINTERS)")
        if not success and error == 38 and not first_call and returned.value == 0:
            terminal = "ERROR_HANDLE_EOF"
            break
        if returned.value < 16:
            _refuse("retrieval-pointer output is truncated")
        extent_count = struct.unpack_from("<I", output.raw, 0)[0]
        output_start = struct.unpack_from("<q", output.raw, 8)[0]
        if output_start != starting_vcn.value or returned.value < 16 + extent_count * 16:
            _refuse("retrieval-pointer output header differs")
        for index in range(extent_count):
            next_vcn, lcn = struct.unpack_from("<qq", output.raw, 16 + index * 16)
            if next_vcn <= starting_vcn.value or lcn < 0:
                _refuse("retrieval-pointer extent is empty, reversed, or sparse")
            result.append(
                {
                    "starting_vcn": int(starting_vcn.value),
                    "next_vcn": int(next_vcn),
                    "lcn": int(lcn),
                }
            )
            starting_vcn.value = next_vcn
        first_call = False
        if success:
            terminal = "SUCCESS_COMPLETE"
            break
        if error == 38:
            terminal = "ERROR_HANDLE_EOF"
            break
        if extent_count == 0:
            _refuse("retrieval-pointer continuation made no progress")
    return initial, terminal, result


def _windows_hash_inventory_handle(handle: int) -> tuple[int, str]:
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    set_pointer = kernel32.SetFilePointerEx
    set_pointer.argtypes = (
        ctypes.c_void_p,
        ctypes.c_int64,
        ctypes.POINTER(ctypes.c_int64),
        ctypes.c_uint32,
    )
    set_pointer.restype = ctypes.c_int
    read_file = kernel32.ReadFile
    read_file.argtypes = (
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_void_p,
    )
    read_file.restype = ctypes.c_int
    if not set_pointer(handle, 0, None, 0):
        raise _windows_error("SetFilePointerEx(inventory)")
    digest = hashlib.sha256()
    total = 0
    buffer = ctypes.create_string_buffer(1024 * 1024)
    while True:
        read = ctypes.c_uint32(0)
        if not read_file(handle, buffer, len(buffer), ctypes.byref(read), None):
            raise _windows_error("ReadFile(inventory)")
        if read.value == 0:
            break
        digest.update(buffer.raw[: read.value])
        total += read.value
    return total, digest.hexdigest()


def _inventory_round_up(value: int, unit: int) -> int:
    return 0 if value == 0 else ((value + unit - 1) // unit) * unit


def _measure_live_inventory_row(
    path: Path,
    relative_path: str,
    storage_category: str,
    *,
    entry_type: str,
    allocation_unit: int,
    file_record_bytes: int,
) -> dict[str, Any]:
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
    query = kernel32.GetFileInformationByHandleEx
    query.argtypes = (ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_uint32)
    query.restype = ctypes.c_int
    close = kernel32.CloseHandle
    close.argtypes = (ctypes.c_void_p,)
    close.restype = ctypes.c_int
    flags = 0x00200000 | (0x02000000 if entry_type == "DIRECTORY" else 0)
    desired_access = 0x80000000 | 0x00020000 | 0x01000000
    handle = create_file(os.fspath(path), desired_access, 1, None, 3, flags, None)
    if handle in (None, ctypes.c_void_p(-1).value):
        raise _windows_error("CreateFileW(inventory deny-write/delete)")
    failure: BaseException | None = None
    try:
        before = _windows_query_file_info(query, handle)
        standard, file_id, attributes = before
        if (
            bool(standard[4]) != (entry_type == "DIRECTORY")
            or standard[2] != 1
            or standard[3]
            or attributes[0] & _INVENTORY_PROHIBITED_ATTRIBUTES
            or attributes[1] != 0
        ):
            _refuse("live inventory handle metadata is prohibited")
        data_streams = _windows_inventory_data_streams(path)
        backup_streams = _windows_backup_streams(handle)
        initial, terminal, extents = _windows_retrieval_extents(handle)
        if entry_type == "REGULAR_FILE":
            ctypes.set_last_error(0)
            high = ctypes.c_uint32(0)
            get_compressed = kernel32.GetCompressedFileSizeW
            get_compressed.argtypes = (ctypes.c_wchar_p, ctypes.POINTER(ctypes.c_uint32))
            get_compressed.restype = ctypes.c_uint32
            low = get_compressed(os.fspath(path), ctypes.byref(high))
            if low == 0xFFFFFFFF and ctypes.get_last_error() != 0:
                raise _windows_error("GetCompressedFileSizeW(inventory)")
            compressed_size = (int(high.value) << 32) | int(low)
            byte_count, digest = _windows_hash_inventory_handle(handle)
            if (
                byte_count != standard[1]
                or data_streams
                != [{"stream_name": "::$DATA", "stream_size_bytes": byte_count}]
            ):
                _refuse("live inventory regular-file stream projection differs")
            logical_bytes = byte_count
            content_sha256: str | None = digest
            data_stream_initial = "STREAM_FOUND"
            data_stream_handle_opened = True
            data_stream_handle_closed = True
            bitmap_clusters = 0
            bitmap_bytes = 0
        else:
            if standard[1] != 0 or data_streams:
                _refuse("live inventory directory stream projection differs")
            compressed_size = None
            logical_bytes = 0
            content_sha256 = None
            data_stream_initial = "ERROR_HANDLE_EOF"
            data_stream_handle_opened = False
            data_stream_handle_closed = False
            raw_bitmap_bytes = (standard[0] + 32768 - 1) // 32768
            bitmap_bytes = _inventory_round_up(raw_bitmap_bytes, allocation_unit)
            bitmap_clusters = bitmap_bytes // allocation_unit
        non_data = [
            stream for stream in backup_streams if stream["stream_id"] != "BACKUP_DATA"
        ]
        non_data_bytes = sum(
            _inventory_round_up(stream["stream_size_bytes"], allocation_unit)
            for stream in non_data
        )
        non_data_clusters = sum(
            _inventory_round_up(stream["stream_size_bytes"], allocation_unit)
            // allocation_unit
            for stream in non_data
        )
        if entry_type == "REGULAR_FILE":
            allocated = max(logical_bytes, compressed_size, standard[0]) + non_data_bytes
        else:
            allocated = standard[0] + bitmap_bytes + non_data_bytes
        metadata = _inventory_round_up(
            (1 + len(extents) + bitmap_clusters + non_data_clusters)
            * file_record_bytes,
            allocation_unit,
        )
        measured = {
            "relative_path": relative_path,
            "entry_type": entry_type,
            "storage_category": storage_category,
            "logical_bytes": logical_bytes,
            "get_compressed_file_size_bytes": compressed_size,
            "file_standard_allocation_size_bytes": standard[0],
            "file_standard_end_of_file_bytes": standard[1],
            "file_standard_number_of_links": standard[2],
            "file_standard_delete_pending": bool(standard[3]),
            "file_standard_directory": bool(standard[4]),
            "raw_file_attributes": attributes[0],
            "file_attribute_reparse_tag": attributes[1],
            "file_id_volume_serial_number": file_id[0],
            "file_id_128": file_id[1].hex(),
            "prohibited_file_attribute_bits_set": (
                attributes[0] & _INVENTORY_PROHIBITED_ATTRIBUTES
            ),
            "backup_read_completed": True,
            "backup_read_security_included": True,
            "backup_read_sacl_included": True,
            "backup_read_abort_completed": True,
            "backup_seek_call_count": 0,
            "backup_streams": backup_streams,
            "backup_stream_count": len(backup_streams),
            "permitted_non_data_backup_stream_count": len(non_data),
            "permitted_non_data_backup_stream_allocation_cluster_count": non_data_clusters,
            "permitted_non_data_backup_stream_accounted_bytes": non_data_bytes,
            "retrieval_pointer_enumeration_completed": True,
            "retrieval_pointer_initial_result": initial,
            "retrieval_pointer_terminal_result": terminal,
            "retrieval_extents": extents,
            "retrieval_extent_count": len(extents),
            "metadata_record_upper_bound_bytes": metadata,
            "directory_bitmap_allocation_cluster_count": bitmap_clusters,
            "directory_bitmap_upper_bound_bytes": bitmap_bytes,
            "allocated_bytes": allocated,
            "accounted_bytes": allocated + metadata,
            "hard_link_count": standard[2],
            "reparse_point": bool(attributes[0] & 0x400),
            "sparse": bool(attributes[0] & 0x200),
            "compressed": bool(attributes[0] & 0x800),
            "data_stream_enumeration_completed": True,
            "data_stream_initial_result": data_stream_initial,
            "data_stream_terminal_result": "ERROR_HANDLE_EOF",
            "data_stream_search_handle_opened": data_stream_handle_opened,
            "data_stream_search_handle_closed": data_stream_handle_closed,
            "data_streams": data_streams,
            "content_sha256": content_sha256,
        }
        if _windows_query_file_info(query, handle) != before:
            _refuse("live inventory entry changed while its handle was held")
    except BaseException as exc:
        failure = exc
    if not close(handle) and failure is None:
        raise _windows_error("CloseHandle(inventory)")
    if failure is not None:
        raise failure
    return measured


def _validate_live_inventory_row(
    path: Path,
    row: Mapping[str, Any],
    *,
    allocation_unit: int,
    file_record_bytes: int,
) -> None:
    measured = _measure_live_inventory_row(
        path,
        row["relative_path"],
        row["storage_category"],
        entry_type=row["entry_type"],
        allocation_unit=allocation_unit,
        file_record_bytes=file_record_bytes,
    )
    if measured != row:
        _refuse(f"live inventory row differs: {row['relative_path']}")


class _OVERLAPPED(ctypes.Structure):
    _fields_ = (
        ("Internal", ctypes.c_void_p),
        ("InternalHigh", ctypes.c_void_p),
        ("Offset", ctypes.c_uint32),
        ("OffsetHigh", ctypes.c_uint32),
        ("hEvent", ctypes.c_void_p),
    )


def _windows_start_tree_watch(
    root: Path, *, recursive: bool
) -> tuple[Any, int, int, _OVERLAPPED, Any]:
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
    create_event = kernel32.CreateEventW
    create_event.argtypes = (ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_wchar_p)
    create_event.restype = ctypes.c_void_p
    read_changes = kernel32.ReadDirectoryChangesW
    read_changes.argtypes = (
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_uint32,
        ctypes.c_int,
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(_OVERLAPPED),
        ctypes.c_void_p,
    )
    read_changes.restype = ctypes.c_int
    handle = create_file(
        os.fspath(root),
        0x0001,
        7,
        None,
        3,
        0x02000000 | 0x40000000,
        None,
    )
    if handle in (None, ctypes.c_void_p(-1).value):
        raise _windows_error("CreateFileW(recursive inventory watch)")
    event = create_event(None, True, False, None)
    if not event:
        error = _windows_error("CreateEventW(recursive inventory watch)")
        kernel32.CloseHandle(handle)
        raise error
    overlapped = _OVERLAPPED()
    overlapped.hEvent = event
    buffer = ctypes.create_string_buffer(65536)
    # FILE_NOTIFY_CHANGE_FILE_NAME | DIR_NAME | ATTRIBUTES | SIZE |
    # LAST_WRITE | CREATION | SECURITY.  The frozen overlapped call supplies
    # NULL for lpBytesReturned.
    filters = 351
    if not read_changes(
        handle,
        buffer,
        len(buffer),
        recursive,
        filters,
        None,
        ctypes.byref(overlapped),
        None,
    ):
        error = _windows_error("ReadDirectoryChangesW(recursive inventory watch)")
        kernel32.CloseHandle(event)
        kernel32.CloseHandle(handle)
        raise error
    return kernel32, int(handle), int(event), overlapped, buffer


def _windows_start_recursive_tree_watch(
    root: Path,
) -> tuple[
    tuple[Any, int, int, _OVERLAPPED, Any],
    tuple[Any, int, int, _OVERLAPPED, Any],
]:
    """Protect both the root entry and its complete descendant tree."""

    parent_watch = _windows_start_tree_watch(root.parent, recursive=False)
    try:
        recursive_watch = _windows_start_tree_watch(root, recursive=True)
    except BaseException:
        _windows_finish_tree_watch(parent_watch, require_quiet=False)
        raise
    return parent_watch, recursive_watch


def _windows_finish_tree_watch(
    state: tuple[Any, int, int, _OVERLAPPED, Any], *, require_quiet: bool
) -> None:
    kernel32, handle, event, overlapped, _buffer = state
    get_result = kernel32.GetOverlappedResult
    get_result.argtypes = (
        ctypes.c_void_p,
        ctypes.POINTER(_OVERLAPPED),
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_int,
    )
    get_result.restype = ctypes.c_int
    cancel = kernel32.CancelIoEx
    cancel.argtypes = (ctypes.c_void_p, ctypes.POINTER(_OVERLAPPED))
    cancel.restype = ctypes.c_int
    close = kernel32.CloseHandle
    close.argtypes = (ctypes.c_void_p,)
    close.restype = ctypes.c_int
    transferred = ctypes.c_uint32(0)
    ctypes.set_last_error(0)
    completed = bool(
        get_result(handle, ctypes.byref(overlapped), ctypes.byref(transferred), False)
    )
    error = 0 if completed else ctypes.get_last_error()
    quiet = not completed and error == 996
    cleanup_error: BaseException | None = None
    if quiet:
        ctypes.set_last_error(0)
        if not cancel(handle, ctypes.byref(overlapped)):
            cleanup_error = _windows_error("CancelIoEx(recursive inventory watch)")
        else:
            transferred.value = 0
            ctypes.set_last_error(0)
            cancelled_completion = bool(
                get_result(
                    handle,
                    ctypes.byref(overlapped),
                    ctypes.byref(transferred),
                    True,
                )
            )
            cancelled_error = 0 if cancelled_completion else ctypes.get_last_error()
            if cancelled_completion or cancelled_error != 995 or transferred.value != 0:
                cleanup_error = BindingRefusal(
                    "cancelled recursive inventory watch did not complete with "
                    "ERROR_OPERATION_ABORTED and zero bytes"
                )
    elif not completed:
        cleanup_error = _windows_error("GetOverlappedResult(recursive inventory watch)")
    if not close(event) and cleanup_error is None:
        cleanup_error = _windows_error("CloseHandle(recursive inventory watch event)")
    if not close(handle) and cleanup_error is None:
        cleanup_error = _windows_error("CloseHandle(recursive inventory watch directory)")
    if cleanup_error is not None:
        raise cleanup_error
    if require_quiet and not quiet:
        _refuse("Stage F storage tree changed during live inventory validation")


def _windows_finish_recursive_tree_watch(
    state: tuple[
        tuple[Any, int, int, _OVERLAPPED, Any],
        tuple[Any, int, int, _OVERLAPPED, Any],
    ],
    *,
    require_quiet: bool,
) -> None:
    first_failure: BaseException | None = None
    for watch in reversed(state):
        try:
            _windows_finish_tree_watch(watch, require_quiet=require_quiet)
        except BaseException as exc:
            if first_failure is None:
                first_failure = exc
    if first_failure is not None:
        raise first_failure


def _windows_lock_inventory_regular_files(
    observed: Mapping[str, Path],
    ordered_paths: Sequence[str],
    expected: Mapping[str, Mapping[str, Any]],
) -> tuple[int, ...]:
    """Hold every inventory file against write/delete and outside-alias mutation."""

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
    query = kernel32.GetFileInformationByHandleEx
    query.argtypes = (ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_uint32)
    query.restype = ctypes.c_int
    final_path = kernel32.GetFinalPathNameByHandleW
    final_path.argtypes = (ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_uint32, ctypes.c_uint32)
    final_path.restype = ctypes.c_uint32
    close = kernel32.CloseHandle
    close.argtypes = (ctypes.c_void_p,)
    close.restype = ctypes.c_int
    handles: list[int] = []
    try:
        for relative in ordered_paths:
            if expected.get(relative, {}).get("entry_type", "REGULAR_FILE") != "REGULAR_FILE":
                continue
            path = observed[relative]
            handle = create_file(
                os.fspath(path),
                0x80000000,
                0x00000001,
                None,
                3,
                0x00200000,
                None,
            )
            if handle in (None, ctypes.c_void_p(-1).value):
                raise _windows_error("CreateFileW(inventory epoch lock)")
            handles.append(handle)
            standard, _file_id, attributes = _windows_query_file_info(query, handle)
            buffer = ctypes.create_unicode_buffer(32768)
            length = final_path(handle, buffer, len(buffer), 1)
            if (
                not 0 < length < len(buffer)
                or buffer.value != os.fspath(path)
                or standard[2] != 1
                or standard[3]
                or standard[4]
                or attributes[0] & _INVENTORY_PROHIBITED_ATTRIBUTES
                or attributes[1] != 0
            ):
                _refuse("inventory epoch file lock metadata or normalized path differs")
        return tuple(handles)
    except BaseException:
        for handle in reversed(handles):
            close(handle)
        raise


def _windows_release_inventory_regular_files(handles: Sequence[int]) -> None:
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    close = kernel32.CloseHandle
    close.argtypes = (ctypes.c_void_p,)
    close.restype = ctypes.c_int
    failed = False
    for handle in reversed(handles):
        if not close(handle):
            failed = True
    if failed:
        raise _windows_error("CloseHandle(inventory epoch lock)")


def validate_live_storage_inventory(
    stage_f_root: os.PathLike[str] | str,
    inventory_entries: Sequence[Mapping[str, Any]],
    *,
    capacity_snapshot: Mapping[str, Any],
    capacity_snapshot_path: os.PathLike[str] | str,
    retained_evidence_root: os.PathLike[str] | str,
    retained_file_observations: Mapping[str, Mapping[str, Any]],
    permitted_postwrite_paths: Sequence[str] = (),
    final_checks: Callable[[], None] | None = None,
) -> int:
    """Independently rescan the complete locked NTFS tree and compare every row."""

    if sys.platform != "win32":
        _refuse("live Stage F storage inventory requires Win32")
    root = _path(stage_f_root, "stage_f_root")
    if not root.is_dir():
        _refuse("Stage F inventory root is absent")
    expected = {row["relative_path"]: row for row in inventory_entries}
    if len(expected) != len(inventory_entries):
        _refuse("inventory rows repeat a relative path")
    root_text = os.fspath(root).rstrip("\\")
    retained_root_text = os.fspath(retained_evidence_root).rstrip("\\")
    if retained_root_text != root_text + "\\independent-audit\\retained-evidence":
        _refuse("retained-evidence live root differs from the exact private role")
    if not retained_file_observations:
        _refuse("retained postwrite material closure is empty")
    file_observations_by_relative: dict[str, Mapping[str, Any]] = {}
    for absolute_path, observation in retained_file_observations.items():
        if (
            not isinstance(absolute_path, str)
            or not absolute_path.startswith(retained_root_text + "\\")
            or ":" in absolute_path[len(retained_root_text) :]
        ):
            _refuse("retained postwrite material path escapes the exact role")
        relative = absolute_path[len(root_text) + 1 :].replace("\\", "/")
        if (
            not relative
            or unicodedata.normalize("NFC", relative) != relative
            or relative in file_observations_by_relative
        ):
            _refuse("retained postwrite material path is malformed or repeated")
        file_observations_by_relative[relative] = observation
    capacity_path_text = os.fspath(capacity_snapshot_path)
    capacity_relative = capacity_path_text[len(root_text) + 1 :].replace("\\", "/")
    postwrite = set(permitted_postwrite_paths)
    if (
        capacity_path_text not in retained_file_observations
        or capacity_relative in expected
        or capacity_relative.rpartition("/")[0]
        != "independent-audit/retained-evidence"
        or capacity_relative not in postwrite
        or any(
            not isinstance(relative, str)
            or unicodedata.normalize("NFC", relative) != relative
            or relative.rpartition("/")[0]
            != "independent-audit/retained-evidence"
            or relative in expected
            for relative in postwrite
        )
        or set(file_observations_by_relative) - set(expected) != postwrite
    ):
        _refuse(
            "retained postwrite files differ from the exact causal role closure"
        )
    allowed_paths = {*expected, *postwrite}
    ordered_allowed_paths = tuple(
        sorted(allowed_paths, key=lambda value: value.encode("utf-8"))
    )
    allocation_unit = capacity_snapshot["volume_allocation_unit_bytes"]
    file_record_bytes = capacity_snapshot["ntfs_volume_data"][
        "bytes_per_file_record_segment"
    ]

    def enumerate_tree() -> dict[str, Path]:
        observed: dict[str, Path] = {".": root}

        def refuse_walk_error(error: OSError) -> None:
            raise BindingRefusal(
                f"live storage inventory enumeration failed: {error.filename!r}: {error}"
            ) from error

        for directory, directory_names, file_names in os.walk(
            root, topdown=True, onerror=refuse_walk_error, followlinks=False
        ):
            directory_names.sort(
                key=lambda value: unicodedata.normalize("NFC", value).encode("utf-8")
            )
            file_names.sort(
                key=lambda value: unicodedata.normalize("NFC", value).encode("utf-8")
            )
            parent = Path(directory)
            for name in (*directory_names, *file_names):
                path = parent / name
                relative = path.relative_to(root).as_posix()
                if relative in observed:
                    _refuse("live inventory repeats a relative path")
                observed[relative] = path
        if tuple(sorted(observed, key=lambda value: value.encode("utf-8"))) != (
            ordered_allowed_paths
        ):
            _refuse("live recursive inventory path closure differs")
        return observed

    def measure_tree(observed: Mapping[str, Path]) -> dict[str, dict[str, Any]]:
        measured_rows: dict[str, dict[str, Any]] = {}
        for relative in ordered_allowed_paths:
            path = observed[relative]
            if relative in expected:
                row = expected[relative]
                _validate_live_inventory_row(
                    path,
                    row,
                    allocation_unit=allocation_unit,
                    file_record_bytes=file_record_bytes,
                )
                measured = dict(row)
            else:
                entry_type = (
                    "REGULAR_FILE"
                    if relative in file_observations_by_relative
                    else "DIRECTORY"
                )
                measured = _measure_live_inventory_row(
                    path,
                    relative,
                    "RETAINED_EVIDENCE",
                    entry_type=entry_type,
                    allocation_unit=allocation_unit,
                    file_record_bytes=file_record_bytes,
                )
            if measured["storage_category"] == "RETAINED_EVIDENCE":
                observation = file_observations_by_relative.get(relative)
                if observation is not None and (
                    measured["entry_type"] != "REGULAR_FILE"
                    or measured["logical_bytes"] != observation["byte_count"]
                    or measured["content_sha256"] != observation["sha256"]
                    or measured["file_id_128"] != observation["file_id_128"]
                    or measured["file_id_volume_serial_number"]
                    != observation["volume_serial_number"]
                ):
                    _refuse("retained locked material observation differs from live row")
            measured_rows[relative] = measured
        return measured_rows

    watch = _windows_start_recursive_tree_watch(root)
    failure: BaseException | None = None
    retained_live_allocated = -1
    inventory_file_locks: tuple[int, ...] = ()
    try:
        observed = enumerate_tree()
        inventory_file_locks = _windows_lock_inventory_regular_files(
            observed, ordered_allowed_paths, expected
        )
        first_rows = measure_tree(observed)
        final_observed = enumerate_tree()
        second_rows = measure_tree(final_observed)
        if first_rows != second_rows:
            _refuse("live recursive inventory rows changed between complete scans")
        retained_live_allocated = sum(
            row["allocated_bytes"]
            for row in second_rows.values()
            if row["storage_category"] == "RETAINED_EVIDENCE"
        )
        prewrite_retained_allocated = sum(
            row["allocated_bytes"]
            for row in expected.values()
            if row["storage_category"] == "RETAINED_EVIDENCE"
        )
        recorded = capacity_snapshot[
            "retained_evidence_live_allocated_bytes_after_snapshot_write"
        ]
        reconstructed_postwrite = (
            prewrite_retained_allocated
            + second_rows[capacity_relative]["allocated_bytes"]
        )
        if (
            recorded != reconstructed_postwrite
            or retained_live_allocated < reconstructed_postwrite
            or retained_live_allocated > 8 * 1073741824
        ):
            _refuse(
                "retained allocation does not reconstruct the immediate capacity "
                "publication lower bound or exceeds the full predebit"
            )
        if final_checks is not None:
            final_checks()
    except BaseException as exc:
        failure = exc
    try:
        _windows_finish_recursive_tree_watch(watch, require_quiet=failure is None)
    except BaseException as exc:
        if failure is None:
            failure = exc
    try:
        _windows_release_inventory_regular_files(inventory_file_locks)
    except BaseException as exc:
        if failure is None:
            failure = exc
    if failure is not None:
        raise failure
    return retained_live_allocated


class _NTFS_VOLUME_DATA_BUFFER(ctypes.Structure):
    _fields_ = (
        ("VolumeSerialNumber", ctypes.c_uint64),
        ("NumberSectors", ctypes.c_int64),
        ("TotalClusters", ctypes.c_int64),
        ("FreeClusters", ctypes.c_int64),
        ("TotalReserved", ctypes.c_int64),
        ("BytesPerSector", ctypes.c_uint32),
        ("BytesPerCluster", ctypes.c_uint32),
        ("BytesPerFileRecordSegment", ctypes.c_uint32),
        ("ClustersPerFileRecordSegment", ctypes.c_uint32),
        ("MftValidDataLength", ctypes.c_int64),
        ("MftStartLcn", ctypes.c_int64),
        ("Mft2StartLcn", ctypes.c_int64),
        ("MftZoneStart", ctypes.c_int64),
        ("MftZoneEnd", ctypes.c_int64),
    )


def _validate_live_private_path(path: str, selected_volume: str) -> None:
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    get_mount = kernel32.GetVolumePathNameW
    get_mount.argtypes = (ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32)
    get_mount.restype = ctypes.c_int
    get_volume = kernel32.GetVolumeNameForVolumeMountPointW
    get_volume.argtypes = (ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32)
    get_volume.restype = ctypes.c_int
    mount = ctypes.create_unicode_buffer(32768)
    volume = ctypes.create_unicode_buffer(32768)
    if not get_mount(path, mount, len(mount)):
        raise _windows_error("GetVolumePathNameW(private path)")
    if not get_volume(mount.value, volume, len(volume)):
        raise _windows_error("GetVolumeNameForVolumeMountPointW(private path)")
    if volume.value != selected_volume:
        _refuse("private path resolves to another selected volume")

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
    query = kernel32.GetFileInformationByHandleEx
    query.argtypes = (ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_uint32)
    query.restype = ctypes.c_int
    final_path = kernel32.GetFinalPathNameByHandleW
    final_path.argtypes = (ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_uint32, ctypes.c_uint32)
    final_path.restype = ctypes.c_uint32
    close = kernel32.CloseHandle
    close.argtypes = (ctypes.c_void_p,)
    close.restype = ctypes.c_int
    handle = create_file(path, 0x80, 7, None, 3, 0x02200000, None)
    if handle in (None, ctypes.c_void_p(-1).value):
        raise _windows_error("CreateFileW(private path)")
    failure: BaseException | None = None
    try:
        attribute = _FILE_ATTRIBUTE_TAG_INFO()
        if not query(handle, 9, ctypes.byref(attribute), ctypes.sizeof(attribute)):
            raise _windows_error("GetFileInformationByHandleEx(private path attributes)")
        if attribute.FileAttributes & 0x400 or attribute.ReparseTag != 0:
            _refuse("private path is a reparse point")
        buffer = ctypes.create_unicode_buffer(32768)
        length = final_path(handle, buffer, len(buffer), 1)
        if not 0 < length < len(buffer) or buffer.value.rstrip("\\") != path.rstrip("\\"):
            _refuse("private path handle resolution differs")
    except BaseException as exc:
        failure = exc
    if not close(handle) and failure is None:
        raise _windows_error("CloseHandle(private path)")
    if failure is not None:
        raise failure


def validate_live_volume_capacity(
    filesystem: Mapping[str, Any], capacity_snapshot: Mapping[str, Any]
) -> None:
    """Requery the exact NTFS volume, nine paths, capacity, and free-space facts."""

    if sys.platform != "win32":
        _refuse("live Stage F capacity verification requires Win32")
    selected_volume = filesystem["selected_volume_guid_path"]
    if not isinstance(selected_volume, str) or not selected_volume.endswith("\\"):
        _refuse("selected volume GUID path is malformed")
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    get_info = kernel32.GetVolumeInformationW
    get_info.argtypes = (
        ctypes.c_wchar_p,
        ctypes.c_wchar_p,
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_wchar_p,
        ctypes.c_uint32,
    )
    get_info.restype = ctypes.c_int
    serial = ctypes.c_uint32(0)
    maximum_component = ctypes.c_uint32(0)
    flags = ctypes.c_uint32(0)
    filesystem_name = ctypes.create_unicode_buffer(64)
    if not get_info(
        selected_volume,
        None,
        0,
        ctypes.byref(serial),
        ctypes.byref(maximum_component),
        ctypes.byref(flags),
        filesystem_name,
        len(filesystem_name),
    ):
        raise _windows_error("GetVolumeInformationW")
    get_space = kernel32.GetDiskFreeSpaceW
    get_space.argtypes = (
        ctypes.c_wchar_p,
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(ctypes.c_uint32),
    )
    get_space.restype = ctypes.c_int
    sectors_per_cluster = ctypes.c_uint32(0)
    bytes_per_sector = ctypes.c_uint32(0)
    free_clusters = ctypes.c_uint32(0)
    total_clusters = ctypes.c_uint32(0)
    if not get_space(
        selected_volume,
        ctypes.byref(sectors_per_cluster),
        ctypes.byref(bytes_per_sector),
        ctypes.byref(free_clusters),
        ctypes.byref(total_clusters),
    ):
        raise _windows_error("GetDiskFreeSpaceW")
    get_space_ex = kernel32.GetDiskFreeSpaceExW
    get_space_ex.argtypes = (
        ctypes.c_wchar_p,
        ctypes.POINTER(ctypes.c_uint64),
        ctypes.POINTER(ctypes.c_uint64),
        ctypes.POINTER(ctypes.c_uint64),
    )
    get_space_ex.restype = ctypes.c_int
    available = ctypes.c_uint64(0)
    total_bytes = ctypes.c_uint64(0)
    total_free = ctypes.c_uint64(0)
    if not get_space_ex(
        selected_volume,
        ctypes.byref(available),
        ctypes.byref(total_bytes),
        ctypes.byref(total_free),
    ):
        raise _windows_error("GetDiskFreeSpaceExW")
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
    device_io = kernel32.DeviceIoControl
    device_io.argtypes = (
        ctypes.c_void_p,
        ctypes.c_uint32,
        ctypes.c_void_p,
        ctypes.c_uint32,
        ctypes.c_void_p,
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_void_p,
    )
    device_io.restype = ctypes.c_int
    close = kernel32.CloseHandle
    close.argtypes = (ctypes.c_void_p,)
    close.restype = ctypes.c_int
    volume_handle = create_file(selected_volume[:-1], 0, 7, None, 3, 0, None)
    if volume_handle in (None, ctypes.c_void_p(-1).value):
        raise _windows_error("CreateFileW(selected NTFS volume)")
    ntfs = _NTFS_VOLUME_DATA_BUFFER()
    returned = ctypes.c_uint32(0)
    failure: BaseException | None = None
    try:
        if not device_io(
            volume_handle,
            0x00090064,
            None,
            0,
            ctypes.byref(ntfs),
            ctypes.sizeof(ntfs),
            ctypes.byref(returned),
            None,
        ) or returned.value != ctypes.sizeof(ntfs):
            raise _windows_error("DeviceIoControl(FSCTL_GET_NTFS_VOLUME_DATA)")
    except BaseException as exc:
        failure = exc
    if not close(volume_handle) and failure is None:
        raise _windows_error("CloseHandle(selected NTFS volume)")
    if failure is not None:
        raise failure
    actual_ntfs = {
        "query_succeeded": True,
        "volume_serial_number": int(ntfs.VolumeSerialNumber),
        "number_sectors": int(ntfs.NumberSectors),
        "total_clusters": int(ntfs.TotalClusters),
        "free_clusters": int(ntfs.FreeClusters),
        "total_reserved_clusters": int(ntfs.TotalReserved),
        "bytes_per_sector": int(ntfs.BytesPerSector),
        "bytes_per_cluster": int(ntfs.BytesPerCluster),
        "bytes_per_file_record_segment": int(ntfs.BytesPerFileRecordSegment),
        "clusters_per_file_record_segment": int(ntfs.ClustersPerFileRecordSegment),
        "mft_valid_data_length": int(ntfs.MftValidDataLength),
        "mft_start_lcn": int(ntfs.MftStartLcn),
        "mft2_start_lcn": int(ntfs.Mft2StartLcn),
        "mft_zone_start": int(ntfs.MftZoneStart),
        "mft_zone_end": int(ntfs.MftZoneEnd),
    }
    stable_actual = {
        "volume_serial_number": int(serial.value),
        "filesystem_name": filesystem_name.value,
        "maximum_component_length": int(maximum_component.value),
        "filesystem_flags": int(flags.value),
        "sectors_per_cluster": int(sectors_per_cluster.value),
        "bytes_per_sector": int(bytes_per_sector.value),
        "get_disk_free_space_total_clusters": int(total_clusters.value),
        "get_disk_free_space_ex_total_caller_bytes": int(total_bytes.value),
    }
    if any(
        capacity_snapshot[field] != value for field, value in stable_actual.items()
    ):
        _refuse("live stable NTFS volume/capacity facts differ from the snapshot")
    stable_ntfs_fields = (
        "query_succeeded",
        "volume_serial_number",
        "number_sectors",
        "total_clusters",
        "bytes_per_sector",
        "bytes_per_cluster",
        "bytes_per_file_record_segment",
        "clusters_per_file_record_segment",
        "mft_start_lcn",
        "mft2_start_lcn",
    )
    if any(
        capacity_snapshot["ntfs_volume_data"][field] != actual_ntfs[field]
        for field in stable_ntfs_fields
    ):
        _refuse("live stable NTFS volume geometry differs from the snapshot")
    live_free = min(int(available.value), int(total_free.value))
    required_free = max(
        350 * 1073741824,
        capacity_snapshot["remaining_reserved_envelope_bytes"],
    )
    if live_free < required_free:
        _refuse("live selected-volume free bytes fall below the frozen requirement")
    path_values = {
        *filesystem["private_directories"].values(),
        *filesystem["storage_category_directories"].values(),
    }
    if len(path_values) != 9:
        _refuse("private path projection is not nine unique locations")
    for path in path_values:
        _validate_live_private_path(path, selected_volume)
    final_available = ctypes.c_uint64(0)
    final_total_bytes = ctypes.c_uint64(0)
    final_total_free = ctypes.c_uint64(0)
    if not get_space_ex(
        selected_volume,
        ctypes.byref(final_available),
        ctypes.byref(final_total_bytes),
        ctypes.byref(final_total_free),
    ):
        raise _windows_error("GetDiskFreeSpaceExW(final)")
    final_live_free = min(
        live_free,
        int(final_available.value),
        int(final_total_free.value),
    )
    if int(final_total_bytes.value) != int(total_bytes.value):
        _refuse("selected-volume total bytes changed during live capacity validation")
    if final_live_free < required_free:
        _refuse("final selected-volume free bytes fall below the frozen requirement")


# ---------------------------------------------------------------------------
# Executable, outcome-blind durability probe route
# ---------------------------------------------------------------------------

_SYNTHETIC_DURABILITY_PAYLOAD = b"stage-f-outcome-blind-durability-control\n"
_CORRUPT_DURABILITY_FIXTURE = b"stage-f-corrupt-durability-control\n"
_ORPHAN_DURABILITY_FIXTURE = b"stage-f-orphan-partial-control\n"


class _ORCH_STARTUPINFOW(ctypes.Structure):
    _fields_ = (
        ("cb", ctypes.c_uint32),
        ("lpReserved", ctypes.c_void_p),
        ("lpDesktop", ctypes.c_void_p),
        ("lpTitle", ctypes.c_void_p),
        ("dwX", ctypes.c_uint32),
        ("dwY", ctypes.c_uint32),
        ("dwXSize", ctypes.c_uint32),
        ("dwYSize", ctypes.c_uint32),
        ("dwXCountChars", ctypes.c_uint32),
        ("dwYCountChars", ctypes.c_uint32),
        ("dwFillAttribute", ctypes.c_uint32),
        ("dwFlags", ctypes.c_uint32),
        ("wShowWindow", ctypes.c_uint16),
        ("cbReserved2", ctypes.c_uint16),
        ("lpReserved2", ctypes.c_void_p),
        ("hStdInput", ctypes.c_void_p),
        ("hStdOutput", ctypes.c_void_p),
        ("hStdError", ctypes.c_void_p),
    )


class _ORCH_PROCESS_INFORMATION(ctypes.Structure):
    _fields_ = (
        ("hProcess", ctypes.c_void_p),
        ("hThread", ctypes.c_void_p),
        ("dwProcessId", ctypes.c_uint32),
        ("dwThreadId", ctypes.c_uint32),
    )


class _ORCH_FILETIME(ctypes.Structure):
    _fields_ = (("low", ctypes.c_uint32), ("high", ctypes.c_uint32))


def _orchestrator_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace(
        "+00:00", "Z"
    )


def _orchestrator_thread_id() -> int:
    if sys.platform != "win32":
        _refuse("the executable durability orchestrator requires Win32")
    get_tid = ctypes.WinDLL("kernel32", use_last_error=True).GetCurrentThreadId
    get_tid.argtypes = ()
    get_tid.restype = ctypes.c_uint32
    result = int(get_tid())
    if result <= 0:
        raise _windows_error("GetCurrentThreadId")
    return result


def _private_path_identity(path: Path | str) -> dict[str, str]:
    text = os.fspath(path)
    if not isinstance(text, str) or unicodedata.normalize("NFC", text) != text:
        _refuse("durability probe path is not an exact NFC string")
    return sha256_identity("stage_f_private_path/v1", text.encode("utf-8", "strict"))


def _orchestrator_output_observation(
    value: ctypes._SimpleCData, *, bits: int, input_hash_completed_utc: str
) -> dict[str, Any]:
    count = bits // 8
    address = ctypes.addressof(value)
    output = ctypes.string_at(address, count)
    return {
        "schema": f"stage_f_uint{bits}_output_storage/v1",
        "base_address_uint64": address,
        "exclusive_end_address_uint64": address + count,
        "byte_count": count,
        "interval_nonoverflowing": True,
        "input_bytes_base64": base64.b64encode(bytes(count)).decode("ascii"),
        "input_sha256": hashlib.sha256(bytes(count)).hexdigest(),
        "input_hash_input_address_uint64": address,
        "input_hash_input_byte_count": count,
        "input_hash_completed_utc": input_hash_completed_utc,
        "output_bytes_base64": base64.b64encode(output).decode("ascii"),
        "output_sha256": hashlib.sha256(output).hexdigest(),
        "output_hash_input_address_uint64": address,
        "output_hash_input_byte_count": count,
        "output_hash_completed_utc": _orchestrator_utc(),
        "live_through_call_return": True,
        "live_through_output_hash": True,
    }


def _orchestrator_control_write(
    path: Path,
    payload: bytes,
    *,
    content_role: str,
    actor_process: Mapping[str, Any],
) -> dict[str, Any]:
    """Perform and retain the exact CREATE_NEW/WriteFile/flush/close lifecycle."""

    if sys.platform != "win32" or not payload or len(payload) > _UINT32_MAX:
        _refuse("control-file write requires Win32 and positive uint32 bytes")
    _ensure_fresh_regular(path, "control-file target")
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    attrs = kernel32.GetFileAttributesW
    attrs.argtypes = (ctypes.c_wchar_p,)
    attrs.restype = ctypes.c_uint32
    ctypes.set_last_error(0)
    if attrs(os.fspath(path)) != _UINT32_MAX or ctypes.get_last_error() != 2:
        _refuse("control-file target nonexistence was not ERROR_FILE_NOT_FOUND")
    create = kernel32.CreateFileW
    create.argtypes = (
        ctypes.c_wchar_p,
        ctypes.c_uint32,
        ctypes.c_uint32,
        ctypes.c_void_p,
        ctypes.c_uint32,
        ctypes.c_uint32,
        ctypes.c_void_p,
    )
    create.restype = ctypes.c_void_p
    write = kernel32.WriteFile
    write.argtypes = (
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_void_p,
    )
    write.restype = ctypes.c_int
    flush = kernel32.FlushFileBuffers
    flush.argtypes = (ctypes.c_void_p,)
    flush.restype = ctypes.c_int
    close = kernel32.CloseHandle
    close.argtypes = (ctypes.c_void_p,)
    close.restype = ctypes.c_int
    created_started = _orchestrator_utc()
    handle = create(os.fspath(path), 0x40000000, 0, None, 1, 0x80000000, None)
    created_completed = _orchestrator_utc()
    if handle in (None, _INVALID_HANDLE_VALUE):
        raise _windows_error("CreateFileW(CREATE_NEW durability control)")
    handle_value = int(handle)
    payload_buffer = (ctypes.c_ubyte * len(payload)).from_buffer_copy(payload)
    payload_address = ctypes.addressof(payload_buffer)
    payload_image = ctypes.string_at(payload_address, len(payload))
    payload_hash_completed = _orchestrator_utc()
    written = ctypes.c_uint32(0)
    written_address = ctypes.addressof(written)
    written_input_hash_completed = _orchestrator_utc()
    write_started = _orchestrator_utc()
    failure: BaseException | None = None
    write_returned = False
    flush_returned = False
    close_returned = False
    try:
        write_returned = bool(
            write(
                handle,
                ctypes.c_void_p(payload_address),
                len(payload),
                ctypes.byref(written),
                None,
            )
        )
        write_completed = _orchestrator_utc()
        if not write_returned or written.value != len(payload):
            raise _windows_error("WriteFile(durability control)")
        written_observation = _orchestrator_output_observation(
            written, bits=32, input_hash_completed_utc=written_input_hash_completed
        )
        flush_started = _orchestrator_utc()
        flush_returned = bool(flush(handle))
        flush_completed = _orchestrator_utc()
        if not flush_returned:
            raise _windows_error("FlushFileBuffers(durability control)")
        close_started = _orchestrator_utc()
    except BaseException as exc:
        failure = exc
        write_completed = locals().get("write_completed", _orchestrator_utc())
        written_observation = locals().get("written_observation")
        flush_started = locals().get("flush_started", write_completed)
        flush_completed = locals().get("flush_completed", flush_started)
        close_started = _orchestrator_utc()
    close_returned = bool(close(handle))
    close_completed = _orchestrator_utc()
    if failure is not None:
        raise failure
    if not close_returned:
        raise _windows_error("CloseHandle(durability control)")
    assert isinstance(written_observation, dict)
    output_interval = (
        written_observation["base_address_uint64"],
        written_observation["exclusive_end_address_uint64"],
    )
    disjoint = max(payload_address, output_interval[0]) >= min(
        payload_address + len(payload), output_interval[1]
    )
    return {
        "schema": "stage_f_durability_control_file_write/v1",
        "content_role": content_role,
        "actor_process_id": actor_process["process_id"],
        "actor_thread_id": _orchestrator_thread_id(),
        "operations_serialized": True,
        "actor_process_creation_filetime_uint64": actor_process[
            "creation_filetime_uint64"
        ],
        "target_path_identity": _private_path_identity(path),
        "target_nonexistence_observation": "GetFileAttributesW_INVALID_FILE_ATTRIBUTES_ERROR_FILE_NOT_FOUND",
        "create_api": "CreateFileW",
        "desired_access": 0x40000000,
        "share_mode": 0,
        "security_attributes": "NULL",
        "creation_disposition": 1,
        "flags_and_attributes": 0x80000000,
        "handle_valid": True,
        "created_handle_value_uint64": handle_value,
        "create_started_utc": created_started,
        "create_completed_utc": created_completed,
        "write_api": "WriteFile",
        "write_input_handle_value_uint64": handle_value,
        "write_buffer_base_address_uint64": payload_address,
        "write_buffer_exclusive_end_address_uint64": payload_address + len(payload),
        "write_buffer_byte_count": len(payload),
        "write_buffer_call_time_bytes_base64": base64.b64encode(payload_image).decode(
            "ascii"
        ),
        "write_buffer_call_time_sha256": hashlib.sha256(payload_image).hexdigest(),
        "write_buffer_interval_nonoverflowing": True,
        "write_buffer_live_and_unchanged_through_return": ctypes.string_at(
            payload_address, len(payload)
        )
        == payload_image,
        "write_buffer_hash_input_address_uint64": payload_address,
        "write_buffer_hash_input_byte_count": len(payload),
        "write_buffer_hash_completed_utc": payload_hash_completed,
        "write_bytes_written_output_observation": written_observation,
        "write_input_and_output_intervals_disjoint": disjoint,
        "write_started_utc": write_started,
        "write_overlapped_pointer": "NULL",
        "write_returned_nonzero": write_returned,
        "written_byte_count": int(written.value),
        "written_sha256": hashlib.sha256(payload_image).hexdigest(),
        "write_completed_utc": write_completed,
        "flush_api": "FlushFileBuffers",
        "flush_started_utc": flush_started,
        "flush_input_handle_value_uint64": handle_value,
        "flush_returned_nonzero": flush_returned,
        "flush_completed_utc": flush_completed,
        "close_api": "CloseHandle",
        "close_started_utc": close_started,
        "close_input_handle_value_uint64": handle_value,
        "close_returned_nonzero": close_returned,
        "close_completed_utc": close_completed,
        "handle_closed_once": True,
        "target_created_once": True,
    }


def _orchestrator_atomic_publish(
    source: Path, target: Path
) -> tuple[dict[str, Any], str]:
    if sys.platform != "win32":
        _refuse("the frozen atomic publication requires Win32")
    _ensure_fresh_regular(target, "atomic publication target")
    if not source.is_file() or not _same_volume(source, target.parent):
        _refuse("atomic publication source is absent or cross-volume")
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    attrs = kernel32.GetFileAttributesW
    attrs.argtypes = (ctypes.c_wchar_p,)
    attrs.restype = ctypes.c_uint32
    ctypes.set_last_error(0)
    if attrs(os.fspath(target)) != _UINT32_MAX or ctypes.get_last_error() != 2:
        _refuse("atomic target was not freshly absent")
    move = kernel32.MoveFileExW
    move.argtypes = (ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32)
    move.restype = ctypes.c_int
    if not move(os.fspath(source), os.fspath(target), 8):
        raise _windows_error("MoveFileExW(MOVEFILE_WRITE_THROUGH)")
    completed = _orchestrator_utc()
    source_absent = attrs(os.fspath(source)) == _UINT32_MAX
    target_present = attrs(os.fspath(target)) != _UINT32_MAX
    if not source_absent or not target_present:
        _refuse("MoveFileExW postcondition differs")
    return (
        {
            "schema": "stage_f_atomic_publication_observation/v1",
            "primitive": "MoveFileExW",
            "raw_flags": 8,
            "movefile_write_through_flag_set": True,
            "movefile_replace_existing_flag_set": False,
            "source_path_identity": _private_path_identity(source),
            "target_path_identity": _private_path_identity(target),
            "same_volume": True,
            "target_exists_before_call": False,
            "target_nonexistence_observation": "GetFileAttributesW_INVALID_FILE_ATTRIBUTES_ERROR_FILE_NOT_FOUND",
            "call_returned_nonzero": True,
            "source_absent_after_call": source_absent,
            "target_present_after_call": target_present,
            "target_created_once": True,
            "target_overwrite_attempt_count": 0,
        },
        completed,
    )


def _orchestrator_directory_observation(
    final_path: Path,
    atomic: Mapping[str, Any],
    *,
    actor_process: Mapping[str, Any],
    evidence_source: str,
) -> dict[str, Any]:
    """Observe the exact published file and its parent with the frozen APIs."""

    if sys.platform != "win32" or ctypes.sizeof(ctypes.c_void_p) != 8:
        _refuse("directory durability observation requires 64-bit Win32")
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    # PathCchRemoveFileSpec is forwarded by the Windows API-set and exported
    # by KernelBase on the accepted host even when pathcch.dll is not present
    # as a standalone file.
    pathcch = ctypes.WinDLL("kernelbase", use_last_error=True)
    create = kernel32.CreateFileW
    create.argtypes = (
        ctypes.c_wchar_p,
        ctypes.c_uint32,
        ctypes.c_uint32,
        ctypes.c_void_p,
        ctypes.c_uint32,
        ctypes.c_uint32,
        ctypes.c_void_p,
    )
    create.restype = ctypes.c_void_p
    virtual_alloc = kernel32.VirtualAlloc
    virtual_alloc.argtypes = (
        ctypes.c_void_p,
        ctypes.c_size_t,
        ctypes.c_uint32,
        ctypes.c_uint32,
    )
    virtual_alloc.restype = ctypes.c_void_p
    get_final = kernel32.GetFinalPathNameByHandleW
    get_final.argtypes = (
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_uint32,
        ctypes.c_uint32,
    )
    get_final.restype = ctypes.c_uint32
    remove_spec = pathcch.PathCchRemoveFileSpec
    remove_spec.argtypes = (ctypes.c_void_p, ctypes.c_size_t)
    remove_spec.restype = ctypes.c_long
    close = kernel32.CloseHandle
    close.argtypes = (ctypes.c_void_p,)
    close.restype = ctypes.c_int
    virtual_free = kernel32.VirtualFree
    virtual_free.argtypes = (ctypes.c_void_p, ctypes.c_size_t, ctypes.c_uint32)
    virtual_free.restype = ctypes.c_int
    handle = create(os.fspath(final_path), 128, 7, None, 3, 0x00200000, None)
    final_open_completed = _orchestrator_utc()
    if handle in (None, _INVALID_HANDLE_VALUE):
        raise _windows_error("CreateFileW(published final attributes)")
    handle_value = int(handle)
    buffer = virtual_alloc(None, 65536, 0x3000, 4)
    allocated = _orchestrator_utc()
    if not buffer:
        close(handle)
        raise _windows_error("VirtualAlloc(directory path buffer)")
    buffer_value = int(buffer)
    failure: BaseException | None = None
    try:
        if ctypes.string_at(buffer_value, 65536) != bytes(65536):
            _refuse("VirtualAlloc directory path buffer was not zero initialized")
        length = int(get_final(handle, buffer, 32768, 1))
        query_completed = _orchestrator_utc()
        if length <= 0 or length >= 32768:
            raise _windows_error("GetFinalPathNameByHandleW(published final)")
        resolved = ctypes.wstring_at(buffer_value, length)
        if resolved != os.fspath(final_path):
            _refuse("held final path did not resolve to its exact volume-GUID path")
        hresult = int(remove_spec(buffer, 32768))
        parent_completed = _orchestrator_utc()
        if hresult != 0:
            _refuse(f"PathCchRemoveFileSpec failed with HRESULT {hresult}")
        parent = ctypes.wstring_at(buffer_value)
        expected_parent = os.fspath(final_path.parent).rstrip("\\")
        if parent.rstrip("\\") != expected_parent:
            _refuse("derived published-final parent path differs")
    except BaseException as exc:
        failure = exc
        length = locals().get("length", 0)
        resolved = locals().get("resolved", "")
        hresult = locals().get("hresult", -1)
        query_completed = locals().get("query_completed", _orchestrator_utc())
        parent_completed = locals().get("parent_completed", query_completed)
        parent = locals().get("parent", "")
    close_returned = bool(close(handle))
    handle_closed = _orchestrator_utc()
    free_returned = bool(virtual_free(buffer, 0, 0x8000))
    freed = _orchestrator_utc()
    if failure is not None:
        raise failure
    if not close_returned or not free_returned:
        raise _windows_error("directory observation resource release")
    return {
        "schema": "stage_f_directory_durability_observation/v1",
        "actor_process_id": actor_process["process_id"],
        "actor_process_creation_filetime_uint64": actor_process[
            "creation_filetime_uint64"
        ],
        "actor_thread_id": _orchestrator_thread_id(),
        "operations_serialized": True,
        "evidence_source": evidence_source,
        "atomic_publication_observation_sha256": hashlib.sha256(
            canonical_bytes(atomic)
        ).hexdigest(),
        "primitive": "MoveFileExW",
        "raw_flags": 8,
        "movefile_write_through_flag_set": True,
        "movefile_replace_existing_flag_set": False,
        "source_path_identity": atomic["source_path_identity"],
        "published_final_path_identity": atomic["target_path_identity"],
        "target_parent_path_identity": _private_path_identity(parent),
        "final_open_api": "CreateFileW",
        "final_open_path_identity": atomic["target_path_identity"],
        "final_open_desired_access": 128,
        "final_open_share_mode": 7,
        "final_open_security_attributes": "NULL",
        "final_open_creation_disposition": 3,
        "final_open_flags_and_attributes": 0x00200000,
        "final_open_handle_value_uint64": handle_value,
        "final_open_returned_valid": True,
        "final_open_completed_utc": final_open_completed,
        "path_buffer_allocation_api": "VirtualAlloc",
        "path_buffer_requested_base_pointer": "NULL",
        "path_buffer_byte_count": 65536,
        "path_buffer_allocation_type": 0x3000,
        "path_buffer_protection": 4,
        "path_buffer_base_address_uint64": buffer_value,
        "path_buffer_wchar_capacity": 32768,
        "path_buffer_zero_initialized": True,
        "path_buffer_allocated_utc": allocated,
        "final_path_query_api": "GetFinalPathNameByHandleW",
        "final_path_query_input_handle_value_uint64": handle_value,
        "final_path_query_output_buffer_address_uint64": buffer_value,
        "final_path_query_wchar_capacity": 32768,
        "final_path_query_raw_flags": 1,
        "final_path_query_returned_length_uint32": length,
        "final_path_query_succeeded": True,
        "resolved_final_path_identity": _private_path_identity(resolved),
        "final_path_query_completed_utc": query_completed,
        "target_parent_derivation_api": "GetFinalPathNameByHandleW_FILE_NAME_NORMALIZED_VOLUME_NAME_GUID_PathCchRemoveFileSpec",
        "target_parent_derivation_input_buffer_address_uint64": buffer_value,
        "target_parent_derivation_wchar_capacity": 32768,
        "target_parent_derivation_hresult": hresult,
        "target_parent_resolution_succeeded": True,
        "target_parent_derivation_completed_utc": parent_completed,
        "final_close_api": "CloseHandle",
        "final_close_input_handle_value_uint64": handle_value,
        "final_close_returned_nonzero": close_returned,
        "final_handle_closed_once": True,
        "final_handle_closed_utc": handle_closed,
        "path_buffer_free_api": "VirtualFree",
        "path_buffer_free_input_address_uint64": buffer_value,
        "path_buffer_free_size": 0,
        "path_buffer_free_type": 0x8000,
        "path_buffer_free_returned_nonzero": free_returned,
        "path_buffer_freed_once": True,
        "path_buffer_freed_utc": freed,
        "same_volume": True,
        "call_returned_nonzero": True,
        "move_completed_on_disk_before_return": True,
        "normalized_os_result_code": 0,
        "observation_utc": freed,
    }


def _orchestrator_create_process(
    executable: str,
    command_vector: Sequence[str],
    invocation: Mapping[str, Any],
    *,
    phase: str,
    orchestrator_process: Mapping[str, Any],
) -> tuple[int, dict[str, Any]]:
    """Launch one frozen probe with CreateProcessW and retain every call image."""

    if sys.platform != "win32" or ctypes.sizeof(ctypes.c_void_p) != 8:
        _refuse("the frozen CreateProcessW observation requires 64-bit Win32")
    if phase not in ("PRE_RESTART", "POST_RESTART"):
        _refuse("CreateProcessW probe phase differs")
    command_text = subprocess.list2cmdline(list(command_vector))
    command = command_text.encode("utf-16le", "strict")
    if not command or command.endswith(b"\x00\x00") or len(command) // 2 > 32766:
        _refuse("probe command line is not admissible UTF-16LE")
    command_buffer = ctypes.create_unicode_buffer(command_text)
    command_base = ctypes.addressof(command_buffer)
    command_call_image = ctypes.string_at(command_base, len(command) + 2)
    command_hash_completed = _orchestrator_utc()
    startup = _ORCH_STARTUPINFOW()
    if ctypes.sizeof(startup) != 104:
        _refuse("STARTUPINFOW does not have the frozen x64 size")
    startup.cb = 104
    startup_base = ctypes.addressof(startup)
    startup_image = ctypes.string_at(startup_base, 104)
    if startup_image != struct.pack("<I", 104) + bytes(100):
        _refuse("STARTUPINFOW did not begin as the frozen zero image")
    startup_hash_completed = _orchestrator_utc()
    process_info = _ORCH_PROCESS_INFORMATION()
    if ctypes.sizeof(process_info) != 24:
        _refuse("PROCESS_INFORMATION does not have the frozen x64 size")
    pi_base = ctypes.addressof(process_info)
    pi_input = ctypes.string_at(pi_base, 24)
    if pi_input != bytes(24):
        _refuse("PROCESS_INFORMATION was not zero initialized")
    pi_input_hash_completed = _orchestrator_utc()
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    create = kernel32.CreateProcessW
    create.argtypes = (
        ctypes.c_wchar_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_int,
        ctypes.c_uint32,
        ctypes.c_void_p,
        ctypes.c_wchar_p,
        ctypes.POINTER(_ORCH_STARTUPINFOW),
        ctypes.POINTER(_ORCH_PROCESS_INFORMATION),
    )
    create.restype = ctypes.c_int
    close = kernel32.CloseHandle
    close.argtypes = (ctypes.c_void_p,)
    close.restype = ctypes.c_int
    create_started = _orchestrator_utc()
    returned = bool(
        create(
            executable,
            ctypes.c_void_p(command_base),
            None,
            None,
            False,
            0,
            None,
            None,
            ctypes.byref(startup),
            ctypes.byref(process_info),
        )
    )
    create_completed = _orchestrator_utc()
    if not returned:
        raise _windows_error(f"CreateProcessW({phase})")
    process_handle = int(process_info.hProcess)
    thread_handle = int(process_info.hThread)
    if (
        process_handle in (0, _INVALID_HANDLE_VALUE)
        or thread_handle in (0, _INVALID_HANDLE_VALUE)
        or process_handle == thread_handle
        or process_info.dwProcessId <= 0
        or process_info.dwThreadId <= 0
    ):
        close(process_info.hThread)
        close(process_info.hProcess)
        _refuse(f"CreateProcessW({phase}) returned invalid process information")
    pi_output = ctypes.string_at(pi_base, 24)
    pi_output_hash_completed = _orchestrator_utc()
    thread_close_started = _orchestrator_utc()
    thread_close_returned = bool(close(process_info.hThread))
    thread_closed = _orchestrator_utc()
    if not thread_close_returned:
        close(process_info.hProcess)
        raise _windows_error(f"CloseHandle({phase} thread)")
    application_identity = _private_path_identity(executable)
    if application_identity != invocation["executable_path_identity"]:
        close(process_info.hProcess)
        _refuse(f"{phase} application identity differs from invocation")
    record = {
        "schema": "stage_f_durability_process_launch/v1",
        "phase": phase,
        "launch_actor_process_id": orchestrator_process["process_id"],
        "launch_actor_thread_id": _orchestrator_thread_id(),
        "launch_and_thread_close_serialized": True,
        "launch_api": "CreateProcessW",
        "application_name_path_identity": application_identity,
        "command_line_buffer_base_address_uint64": command_base,
        "command_line_buffer_exclusive_end_address_uint64": command_base
        + len(command_call_image),
        "command_line_buffer_wchar_capacity": len(command) // 2 + 1,
        "command_line_buffer_byte_count_including_terminal_nul": len(
            command_call_image
        ),
        "command_line_base64": base64.b64encode(command).decode("ascii"),
        "command_line_utf16_code_unit_count": len(command) // 2,
        "command_line_terminal_nul_present": True,
        "command_line_mutable_buffer": True,
        "command_line_buffer_call_time_bytes_base64": base64.b64encode(
            command_call_image
        ).decode("ascii"),
        "command_line_buffer_call_time_sha256": hashlib.sha256(
            command_call_image
        ).hexdigest(),
        "command_line_hash_input_address_uint64": command_base,
        "command_line_hash_input_byte_count": len(command_call_image),
        "command_line_hash_completed_utc": command_hash_completed,
        "process_security_attributes": "NULL",
        "thread_security_attributes": "NULL",
        "inherit_handles": False,
        "raw_creation_flags": 0,
        "environment_pointer": "NULL",
        "current_directory_pointer": "NULL",
        "startup_info_address_uint64": startup_base,
        "startup_info_exclusive_end_address_uint64": startup_base + 104,
        "startup_info_byte_count": 104,
        "startup_info_zero_initialized_before_cb_assignment": True,
        "startup_info_cb": 104,
        "startup_info_call_time_bytes_base64": base64.b64encode(startup_image).decode(
            "ascii"
        ),
        "startup_info_call_time_sha256": hashlib.sha256(startup_image).hexdigest(),
        "startup_info_hash_input_address_uint64": startup_base,
        "startup_info_hash_input_byte_count": 104,
        "startup_info_hash_completed_utc": startup_hash_completed,
        "startup_info_reserved_pointer": "NULL",
        "startup_info_desktop_pointer": "NULL",
        "startup_info_title_pointer": "NULL",
        "startup_info_x": 0,
        "startup_info_y": 0,
        "startup_info_x_size": 0,
        "startup_info_y_size": 0,
        "startup_info_x_count_chars": 0,
        "startup_info_y_count_chars": 0,
        "startup_info_fill_attribute": 0,
        "startup_info_dwflags": 0,
        "startup_info_show_window": 0,
        "startup_info_standard_input": "NULL",
        "startup_info_standard_output": "NULL",
        "startup_info_standard_error": "NULL",
        "startup_info_reserved2_byte_count": 0,
        "startup_info_reserved2_pointer": "NULL",
        "process_information_address_uint64": pi_base,
        "process_information_exclusive_end_address_uint64": pi_base + 24,
        "process_information_byte_count": 24,
        "process_information_zero_initialized_before_call": True,
        "process_information_input_bytes_base64": base64.b64encode(pi_input).decode(
            "ascii"
        ),
        "process_information_input_sha256": hashlib.sha256(pi_input).hexdigest(),
        "process_information_input_hash_address_uint64": pi_base,
        "process_information_input_hash_byte_count": 24,
        "process_information_input_hash_completed_utc": pi_input_hash_completed,
        "process_information_output_bytes_base64": base64.b64encode(pi_output).decode(
            "ascii"
        ),
        "process_information_output_sha256": hashlib.sha256(pi_output).hexdigest(),
        "process_information_output_hash_address_uint64": pi_base,
        "process_information_output_hash_byte_count": 24,
        "process_information_output_hash_completed_utc": pi_output_hash_completed,
        "create_process_input_images_unchanged_from_hash_through_call_entry": (
            ctypes.string_at(startup_base, 104) == startup_image
            and ctypes.string_at(pi_base, 24) == pi_output
        ),
        "create_process_memory_intervals_nonoverflowing": True,
        "create_process_memory_intervals_pairwise_disjoint": True,
        "create_process_memory_intervals_live_through_return": True,
        "process_information_interval_live_through_output_hash": True,
        "create_process_started_utc": create_started,
        "create_process_returned_nonzero": returned,
        "create_process_completed_utc": create_completed,
        "process_handle_value_uint64": process_handle,
        "thread_handle_value_uint64": thread_handle,
        "returned_handles_distinct": True,
        "process_id": int(process_info.dwProcessId),
        "thread_id": int(process_info.dwThreadId),
        "thread_close_api": "CloseHandle",
        "thread_close_started_utc": thread_close_started,
        "thread_close_input_handle_value_uint64": thread_handle,
        "thread_close_returned_nonzero": thread_close_returned,
        "thread_handle_closed_utc": thread_closed,
        "process_handle_retained_after_launch": True,
        "launch_utc": create_completed,
    }
    _validate_launch(record, phase, orchestrator_process["process_id"])
    return process_handle, record


def _filetime_uint64(value: _ORCH_FILETIME) -> int:
    return (int(value.high) << 32) | int(value.low)


def _filetime_utc(value: int) -> str:
    windows_epoch = datetime(1601, 1, 1, tzinfo=timezone.utc)
    moment = windows_epoch + __import__("datetime").timedelta(
        microseconds=value // 10
    )
    return moment.isoformat(timespec="microseconds").replace("+00:00", "Z")


def _orchestrator_wait_and_query(
    process_handle: int,
    launch: Mapping[str, Any],
    *,
    prefix: str,
    child_evidence_path: Path,
) -> dict[str, Any]:
    """Wait, query, and close the exact retained CreateProcessW handle."""

    if prefix not in ("terminated", "resumed"):
        _refuse("durability wait prefix differs")
    # The frozen ordering requires the child exit to precede the one retained
    # INFINITE wait.  The child publishes its evidence immediately before
    # returning; waiting for that write and a bounded grace period avoids an
    # unrecorded process-handle wait or query.
    deadline = time.monotonic() + 30.0
    while not child_evidence_path.is_file() and time.monotonic() < deadline:
        time.sleep(0.01)
    time.sleep(0.5)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    wait = kernel32.WaitForSingleObject
    wait.argtypes = (ctypes.c_void_p, ctypes.c_uint32)
    wait.restype = ctypes.c_uint32
    get_exit = kernel32.GetExitCodeProcess
    get_exit.argtypes = (ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint32))
    get_exit.restype = ctypes.c_int
    get_times = kernel32.GetProcessTimes
    get_times.argtypes = (
        ctypes.c_void_p,
        ctypes.POINTER(_ORCH_FILETIME),
        ctypes.POINTER(_ORCH_FILETIME),
        ctypes.POINTER(_ORCH_FILETIME),
        ctypes.POINTER(_ORCH_FILETIME),
    )
    get_times.restype = ctypes.c_int
    close = kernel32.CloseHandle
    close.argtypes = (ctypes.c_void_p,)
    close.restype = ctypes.c_int
    wait_started = _orchestrator_utc()
    wait_result = int(wait(ctypes.c_void_p(process_handle), _UINT32_MAX))
    wait_completed = _orchestrator_utc()
    if wait_result != 0:
        close(ctypes.c_void_p(process_handle))
        _refuse(f"WaitForSingleObject({prefix}) did not return WAIT_OBJECT_0")
    exit_code = ctypes.c_uint32(0)
    exit_input_hash = _orchestrator_utc()
    exit_started = _orchestrator_utc()
    exit_returned = bool(
        get_exit(ctypes.c_void_p(process_handle), ctypes.byref(exit_code))
    )
    exit_returned_utc = _orchestrator_utc()
    if not exit_returned:
        close(ctypes.c_void_p(process_handle))
        raise _windows_error(f"GetExitCodeProcess({prefix})")
    exit_observation = _orchestrator_output_observation(
        exit_code, bits=32, input_hash_completed_utc=exit_input_hash
    )
    exit_completed = _orchestrator_utc()
    creation, exit_time, kernel_time, user_time = (
        _ORCH_FILETIME() for _ in range(4)
    )
    time_values = (creation, exit_time, kernel_time, user_time)
    time_input_hashes = [_orchestrator_utc() for _ in time_values]
    times_started = _orchestrator_utc()
    times_returned = bool(
        get_times(
            ctypes.c_void_p(process_handle),
            ctypes.byref(creation),
            ctypes.byref(exit_time),
            ctypes.byref(kernel_time),
            ctypes.byref(user_time),
        )
    )
    times_returned_utc = _orchestrator_utc()
    if not times_returned:
        close(ctypes.c_void_p(process_handle))
        raise _windows_error(f"GetProcessTimes({prefix})")
    numeric_times = [_filetime_uint64(item) for item in time_values]
    time_observations = [
        _orchestrator_output_observation(
            item, bits=64, input_hash_completed_utc=input_hash
        )
        for item, input_hash in zip(time_values, time_input_hashes, strict=True)
    ]
    times_completed = _orchestrator_utc()
    close_started = _orchestrator_utc()
    close_returned = bool(close(ctypes.c_void_p(process_handle)))
    closed = _orchestrator_utc()
    if not close_returned:
        raise _windows_error(f"CloseHandle({prefix} process)")
    if exit_code.value != 0:
        _refuse(f"{prefix} durability probe returned {exit_code.value}")
    process_exit_utc = _filetime_utc(numeric_times[1])
    if _utc(process_exit_utc, "child exit") > _utc(wait_started, "wait start"):
        _refuse(f"{prefix} process had not exited before the frozen retained wait")
    result: dict[str, Any] = {
        f"{prefix}_wait_api": "WaitForSingleObject",
        f"{prefix}_wait_input_process_handle_value_uint64": process_handle,
        f"{prefix}_wait_started_utc": wait_started,
        f"{prefix}_wait_timeout_milliseconds": _UINT32_MAX,
        f"{prefix}_wait_result": "WAIT_OBJECT_0",
        f"{prefix}_wait_result_raw": wait_result,
        f"{prefix}_query_actor_process_id": os.getpid(),
        f"{prefix}_query_actor_thread_id": launch["launch_actor_thread_id"],
        f"{prefix}_query_calls_serialized": True,
        f"{prefix}_get_exit_code_api": "GetExitCodeProcess",
        f"{prefix}_get_exit_code_started_utc": exit_started,
        f"{prefix}_get_exit_code_input_process_handle_value_uint64": process_handle,
        f"{prefix}_get_exit_code_output_observation": exit_observation,
        f"{prefix}_get_exit_code_returned_nonzero": exit_returned,
        f"{prefix}_process_exit_code": int(exit_code.value),
        f"{prefix}_get_exit_code_returned_utc": exit_returned_utc,
        f"{prefix}_get_exit_code_completed_utc": exit_completed,
        f"{prefix}_get_process_times_api": "GetProcessTimes",
        f"{prefix}_get_process_times_started_utc": times_started,
        f"{prefix}_get_process_times_input_process_handle_value_uint64": process_handle,
        f"{prefix}_get_process_times_output_intervals_pairwise_disjoint": True,
        f"{prefix}_get_process_times_returned_nonzero": times_returned,
        f"{prefix}_process_creation_filetime_uint64": numeric_times[0],
        f"{prefix}_process_exit_filetime_uint64": numeric_times[1],
        f"{prefix}_process_kernel_filetime_uint64": numeric_times[2],
        f"{prefix}_process_user_filetime_uint64": numeric_times[3],
        f"{prefix}_get_process_times_returned_utc": times_returned_utc,
        f"{prefix}_get_process_times_completed_utc": times_completed,
        f"{prefix}_process_exit_utc": process_exit_utc,
        f"{prefix}_wait_completed_utc": wait_completed,
        f"{prefix}_process_close_api": "CloseHandle",
        f"{prefix}_process_close_started_utc": close_started,
        f"{prefix}_process_close_input_handle_value_uint64": process_handle,
        f"{prefix}_process_close_returned_nonzero": close_returned,
        f"{prefix}_process_handle_closed_utc": closed,
    }
    for name, observation in zip(
        ("creation", "exit", "kernel", "user"), time_observations, strict=True
    ):
        result[f"{prefix}_get_process_times_{name}_output_observation"] = observation
    return result


def _durability_action(
    ordinal: int,
    *,
    observed_utc: str,
    actor_process: Mapping[str, Any],
    hashes: Mapping[str, str],
    counts: Mapping[str, int],
) -> dict[str, Any]:
    spec = _ACTION_SPECS[ordinal - 1]
    _expected_ordinal, action, input_role, output_role, count_role, actor_role = spec
    return {
        "ordinal": ordinal,
        "action": action,
        "observed_utc": observed_utc,
        "input_sha256": hashes[input_role],
        "input_hash_role": input_role,
        "output_sha256": hashes[output_role],
        "output_hash_role": output_role,
        "observed_byte_count": counts[count_role],
        "byte_count_role": count_role,
        "actor_process_role": actor_role,
        "actor_process_id": actor_process["process_id"],
        "actor_process_creation_filetime_uint64": actor_process[
            "creation_filetime_uint64"
        ],
        "os_result_code": 0,
        "status": "PASS",
    }


def _probe_prefix(invocation_path: Path, phase: str) -> tuple[Path, str]:
    suffix = f".{phase.lower().replace('_', '-')}-invocation.json"
    name = invocation_path.name
    if not name.endswith(suffix) or len(name) <= len(suffix):
        _refuse(f"{phase} invocation path does not carry the orchestrator token")
    return invocation_path.parent, name[: -len(suffix)]


def _write_probe_evidence(path: Path, value: Mapping[str, Any]) -> None:
    raw = canonical_bytes(value)
    _write_temporary(raw, path)
    observed = path.read_bytes()
    if observed != raw:
        _refuse("retained durability probe evidence did not reread byte-exactly")


def _execute_pre_restart_probe(
    invocation: Mapping[str, Any], process: Mapping[str, Any], invocation_path: Path
) -> dict[str, Any]:
    parent, token = _probe_prefix(invocation_path, "PRE_RESTART")
    temporary = parent / f"{token}.payload.partial"
    final = parent / f"{token}.payload.final"
    evidence_path = parent / f"{token}.pre-evidence.json"
    payload = _SYNTHETIC_DURABILITY_PAYLOAD
    payload_hash = hashlib.sha256(payload).hexdigest()
    write_observation = _orchestrator_control_write(
        temporary,
        payload,
        content_role="SYNTHETIC_PAYLOAD_TEMPORARY",
        actor_process=process,
    )
    atomic, move_completed = _orchestrator_atomic_publish(temporary, final)
    directory = _orchestrator_directory_observation(
        final,
        atomic,
        actor_process=process,
        evidence_source="SYNTHETIC_PAYLOAD_ATOMIC_PUBLICATION_ACTION_5_MOVEFILEEXW_WRITE_THROUGH",
    )
    hashes = {
        "EMPTY": _EMPTY_SHA256,
        "SYNTHETIC_PAYLOAD": payload_hash,
        "PUBLISHED_FINAL": payload_hash,
    }
    counts = {"ZERO": 0, "SYNTHETIC_PAYLOAD": len(payload)}
    action_times = (
        write_observation["create_completed_utc"],
        write_observation["write_completed_utc"],
        write_observation["flush_completed_utc"],
        write_observation["close_completed_utc"],
        move_completed,
        directory["observation_utc"],
        _orchestrator_utc(),
    )
    actions = [
        _durability_action(
            ordinal,
            observed_utc=action_times[ordinal - 1],
            actor_process=process,
            hashes=hashes,
            counts=counts,
        )
        for ordinal in range(1, 8)
    ]
    evidence = {
        "schema": "stage_f_durability_pre_restart_execution_evidence/v1",
        "phase": "PRE_RESTART",
        "process": dict(process),
        "invocation_sha256": hashlib.sha256(canonical_bytes(invocation)).hexdigest(),
        "payload_base64": base64.b64encode(payload).decode("ascii"),
        "synthetic_payload_identity": sha256_identity(
            "stage_f_synthetic_durability_payload/v1", payload
        ),
        "temporary_path": os.fspath(temporary),
        "temporary_path_identity": _private_path_identity(temporary),
        "final_path": os.fspath(final),
        "final_path_identity": _private_path_identity(final),
        "directory_target_path": os.fspath(final.parent),
        "directory_target_identity": _private_path_identity(final.parent),
        "payload_write_observation": write_observation,
        "atomic_publication_observation": atomic,
        "directory_durability_observation": directory,
        "ordered_actions": actions,
        "scientific_counters": dict(ZERO_SCIENCE_COUNTERS),
    }
    _write_probe_evidence(evidence_path, evidence)
    return {
        "execution_evidence_path": os.fspath(evidence_path),
        "execution_evidence_sha256": hashlib.sha256(canonical_bytes(evidence)).hexdigest(),
        "ordered_action_count": 7,
    }


def _execute_post_restart_probe(
    invocation: Mapping[str, Any],
    process: Mapping[str, Any],
    invocation_path: Path,
    *,
    challenge_path: Path,
    challenge_sha256: str,
    acknowledgement_path: Path,
) -> dict[str, Any]:
    parent, token = _probe_prefix(invocation_path, "POST_RESTART")
    final = parent / f"{token}.payload.final"
    corrupt = parent / f"{token}.corrupt.final"
    orphan = parent / f"{token}.orphan.partial"
    recovered = parent / f"{token}.recovered.final"
    evidence_path = parent / f"{token}.post-evidence.json"
    payload = _SYNTHETIC_DURABILITY_PAYLOAD
    payload_hash = hashlib.sha256(payload).hexdigest()
    challenge_raw = challenge_path.read_bytes()
    if hashlib.sha256(challenge_raw).hexdigest() != challenge_sha256:
        _refuse("POST_RESTART challenge digest differs at execution entry")
    try:
        import json as _json

        challenge = _json.loads(challenge_raw.decode("utf-8", "strict"))
    except (UnicodeError, ValueError) as exc:
        raise BindingRefusal("POST_RESTART challenge is not canonical JSON") from exc
    if canonical_bytes(challenge) != challenge_raw:
        _refuse("POST_RESTART challenge bytes are not canonical")
    acknowledgement = {
        "schema": "stage_f_durability_restart_acknowledgement/v1",
        "challenge_sha256": challenge_sha256,
        "resumed_process": dict(process),
        "acknowledged_utc": _orchestrator_utc(),
    }
    acknowledgement_raw = canonical_bytes(acknowledgement)
    acknowledgement_write = _orchestrator_control_write(
        acknowledgement_path,
        acknowledgement_raw,
        content_role="RESTART_ACKNOWLEDGEMENT_FINAL",
        actor_process=process,
    )
    action8_time = _orchestrator_utc()
    count, reread_hash, reread = _read_stable(final)
    if count != len(payload) or reread_hash != payload_hash or reread != payload:
        _refuse("POST_RESTART final did not reconcile with the synthetic payload")
    action9_time = _orchestrator_utc()
    action10_time = _orchestrator_utc()
    recomputed = hashlib.sha256(reread).hexdigest()
    action11_time = _orchestrator_utc()
    if recomputed != payload_hash:
        _refuse("POST_RESTART complete reread hash differs")
    _write_temporary(_CORRUPT_DURABILITY_FIXTURE, corrupt)
    corrupt_hash = hashlib.sha256(_CORRUPT_DURABILITY_FIXTURE).hexdigest()
    action12_time = _orchestrator_utc()
    corrupt_refused = False
    try:
        verify_checkpoint_hash(
            corrupt,
            payload_hash,
            expected_byte_count=len(payload),
            synthetic=True,
        )
    except BindingRefusal:
        corrupt_refused = True
    if not corrupt_refused:
        _refuse("corrupt durability fixture was not refused")
    action13_time = _orchestrator_utc()
    _write_temporary(_ORPHAN_DURABILITY_FIXTURE, orphan)
    orphan_hash = hashlib.sha256(_ORPHAN_DURABILITY_FIXTURE).hexdigest()
    action14_time = _orchestrator_utc()
    orphan_refused = False
    try:
        recover_checkpoint(
            final,
            parent / f"{token}.forbidden-orphan-recovery.final",
            payload_hash,
            expected_byte_count=len(payload),
            orphan_partial_paths=(orphan,),
            synthetic=True,
        )
    except BindingRefusal:
        orphan_refused = True
    if not orphan_refused:
        _refuse("orphan partial durability fixture was not refused")
    action15_time = _orchestrator_utc()
    recovery = recover_checkpoint(
        final,
        recovered,
        payload_hash,
        expected_byte_count=len(payload),
        synthetic=True,
    )
    action16_time = _orchestrator_utc()
    recovered_check = verify_checkpoint_hash(
        recovered,
        payload_hash,
        expected_byte_count=len(payload),
        synthetic=True,
    )
    action17_time = _orchestrator_utc()
    hashes = {
        "PUBLISHED_FINAL": payload_hash,
        "POST_RESTART_REREAD": reread_hash,
        "CORRUPT_FIXTURE": corrupt_hash,
        "ORPHAN_PARTIAL": orphan_hash,
        "LAST_VERIFIED_DURABLE_CHECKPOINT": payload_hash,
        "RECOVERED_FINAL": recovered_check["sha256"],
        "SYNTHETIC_PAYLOAD": payload_hash,
    }
    counts = {
        "SYNTHETIC_PAYLOAD": len(payload),
        "POST_RESTART_REREAD": count,
        "CORRUPT_FIXTURE": len(_CORRUPT_DURABILITY_FIXTURE),
        "ORPHAN_PARTIAL": len(_ORPHAN_DURABILITY_FIXTURE),
    }
    times = (
        action8_time,
        action9_time,
        action10_time,
        action11_time,
        action12_time,
        action13_time,
        action14_time,
        action15_time,
        action16_time,
        action17_time,
    )
    actions = [
        _durability_action(
            ordinal,
            observed_utc=times[ordinal - 8],
            actor_process=process,
            hashes=hashes,
            counts=counts,
        )
        for ordinal in range(8, 18)
    ]
    evidence = {
        "schema": "stage_f_durability_post_restart_execution_evidence/v1",
        "phase": "POST_RESTART",
        "process": dict(process),
        "invocation_sha256": hashlib.sha256(canonical_bytes(invocation)).hexdigest(),
        "challenge_path": os.fspath(challenge_path),
        "challenge_sha256": challenge_sha256,
        "acknowledgement_path": os.fspath(acknowledgement_path),
        "acknowledgement_preimage": acknowledgement,
        "acknowledgement_sha256": hashlib.sha256(acknowledgement_raw).hexdigest(),
        "acknowledgement_write_observation": acknowledgement_write,
        "final_path": os.fspath(final),
        "post_restart_reread_base64": base64.b64encode(reread).decode("ascii"),
        "post_restart_reread_byte_count": count,
        "post_restart_reread_sha256": reread_hash,
        "corrupt_fixture_path": os.fspath(corrupt),
        "corrupt_fixture_byte_count": len(_CORRUPT_DURABILITY_FIXTURE),
        "corrupt_fixture_sha256": corrupt_hash,
        "orphan_partial_path": os.fspath(orphan),
        "orphan_partial_byte_count": len(_ORPHAN_DURABILITY_FIXTURE),
        "orphan_partial_sha256": orphan_hash,
        "recovered_path": os.fspath(recovered),
        "recovered_final_sha256": recovered_check["sha256"],
        "recovery_observation": recovery,
        "ordered_actions": actions,
        "scientific_counters": dict(ZERO_SCIENCE_COUNTERS),
    }
    _write_probe_evidence(evidence_path, evidence)
    return {
        "execution_evidence_path": os.fspath(evidence_path),
        "execution_evidence_sha256": hashlib.sha256(canonical_bytes(evidence)).hexdigest(),
        "acknowledgement_sha256": evidence["acknowledgement_sha256"],
        "ordered_action_count": 10,
    }


def _read_canonical_probe_evidence(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    try:
        import json as _json

        value = _json.loads(raw.decode("utf-8", "strict"))
    except (UnicodeError, ValueError) as exc:
        raise BindingRefusal(f"probe evidence is not UTF-8 JSON: {path}") from exc
    if not isinstance(value, dict) or canonical_bytes(value) != raw:
        _refuse(f"probe evidence is not a canonical object: {path}")
    return value


def _unix_ns_utc(value: Any, label: str) -> str:
    if type(value) is not int or value <= 0:
        _refuse(f"{label} is not a positive Unix-nanosecond timestamp")
    seconds, nanoseconds = divmod(value, 1_000_000_000)
    prefix = datetime.fromtimestamp(seconds, timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%S"
    )
    return f"{prefix}.{nanoseconds:09d}Z"


def _artifact_lock_from_raw(
    raw: Mapping[str, Any],
    *,
    role: str,
    process: Mapping[str, Any],
    invocation: Mapping[str, Any],
) -> dict[str, Any]:
    expected_keys = {
        "s",
        "h",
        "p",
        "v",
        "f",
        "a",
        "e",
        "n",
        "d",
        "i",
        "t",
        "g",
        "c",
        "x",
        "o",
        "q",
        "u",
        "r",
        "k",
    }
    if set(raw) != expected_keys or raw["s"] != "stage_f_locked_zipapp_raw/v1":
        _refuse("locked-bootstrap raw evidence is not closed")
    for field in ("h", "v", "a", "e", "n", "t", "g", "c", "o", "q", "u", "r", "k"):
        if type(raw[field]) is not int or raw[field] < 0:
            _refuse(f"locked-bootstrap raw integer differs: {field}")
    if raw["d"] is not False or raw["i"] is not False:
        _refuse("locked-bootstrap raw standard info differs")
    if (
        not isinstance(raw["p"], str)
        or not isinstance(raw["f"], str)
        or re.fullmatch(r"[0-9a-f]{32}", raw["f"]) is None
        or not isinstance(raw["x"], str)
        or _SHA256_RE.fullmatch(raw["x"]) is None
    ):
        _refuse("locked-bootstrap raw path, file ID, or digest differs")
    if not raw["o"] <= raw["q"] <= raw["u"] <= raw["r"] <= raw["k"]:
        _refuse("locked-bootstrap raw timestamps are not ordered")
    if (
        raw["p"] != invocation.get("_validator_zipapp_path", raw["p"])
        or raw["e"] != invocation["validator_zipapp_byte_count"]
        or raw["c"] != raw["e"]
        or raw["x"] != invocation["validator_zipapp_sha256"]
        or raw["n"] != 1
        or raw["a"] < raw["e"]
        or raw["t"] & 0x400
        or raw["g"] != 0
    ):
        _refuse("locked-bootstrap raw artifact projection differs")
    path_identity = _private_path_identity(raw["p"])
    if path_identity != invocation["validator_zipapp_path_identity"]:
        _refuse("locked-bootstrap raw path identity differs")
    record: dict[str, Any] = {
        "schema": "stage_f_validator_artifact_lock_observation/v1",
        "actor_process_role": role,
        "actor_process_id": process["process_id"],
        "actor_process_creation_filetime_uint64": process[
            "creation_filetime_uint64"
        ],
        "binding_validator_identity": invocation["binding_validator_identity"],
        "host_validation_runtime_identity": invocation[
            "host_validation_runtime_identity"
        ],
        "invocation_sha256": hashlib.sha256(canonical_bytes(invocation)).hexdigest(),
        "artifact_path_identity": path_identity,
        "expected_byte_count": invocation["validator_zipapp_byte_count"],
        "expected_sha256": invocation["validator_zipapp_sha256"],
        "open_api": "CreateFileW",
        "desired_access": 0x80000000,
        "share_mode": 1,
        "security_attributes": "NULL",
        "creation_disposition": 3,
        "flags_and_attributes": 0x00200000,
        "handle_valid": True,
        "artifact_handle_value_uint64": raw["h"],
        "resolved_path_api": "GetFinalPathNameByHandleW_FILE_NAME_NORMALIZED_VOLUME_NAME_GUID",
        "resolved_path_query_handle_value_uint64": raw["h"],
        "resolved_path_identity": path_identity,
        "file_id_query_api": "GetFileInformationByHandleEx_FileIdInfo",
        "file_id_query_handle_value_uint64": raw["h"],
        "volume_serial_number": raw["v"],
        "file_id_128": raw["f"],
        "file_standard_info_query_api": "GetFileInformationByHandleEx_FileStandardInfo",
        "file_standard_info_query_handle_value_uint64": raw["h"],
        "number_of_links": raw["n"],
        "delete_pending": raw["d"],
        "directory": raw["i"],
        "file_attribute_tag_query_api": "GetFileInformationByHandleEx_FileAttributeTagInfo",
        "file_attribute_tag_query_handle_value_uint64": raw["h"],
        "raw_file_attributes": raw["t"],
        "reparse_tag": raw["g"],
        "read_api": "ReadFile",
        "read_input_handle_value_uint64": raw["h"],
        "read_from_held_handle": True,
        "observed_byte_count": raw["c"],
        "observed_sha256": raw["x"],
        "lock_acquired_utc": _unix_ns_utc(raw["o"], "artifact lock acquisition"),
        "validator_entrypoint_loaded_utc": _unix_ns_utc(
            raw["u"], "validator entrypoint load"
        ),
        "close_api": "CloseHandle",
        "close_input_handle_value_uint64": raw["h"],
        "close_returned_nonzero": True,
        "handle_closed_utc": _unix_ns_utc(raw["k"], "artifact handle close"),
        "lock_released_utc": _unix_ns_utc(raw["k"], "artifact lock release"),
        "write_share_permitted": False,
        "delete_share_permitted": False,
        "lock_held_from_before_zipapp_read_until_after_zipapp_return": True,
        "status": "PASS",
    }
    record["lock_sha256"] = hashlib.sha256(canonical_bytes(record)).hexdigest()
    return record


def _next_challenge_counter(root: Path) -> int:
    maximum = 0
    for candidate in root.rglob("*"):
        if candidate.is_symlink():
            _refuse("temporary durability tree contains a reparse/symlink entry")
        if not candidate.is_file():
            continue
        try:
            value = _read_canonical_probe_evidence(candidate)
        except (BindingRefusal, OSError):
            continue
        if value.get("schema") == "stage_f_durability_restart_challenge/v1":
            counter = value.get("challenge_counter")
            if type(counter) is not int or not 0 < counter <= _UINT64_MAX:
                _refuse("retained durability challenge has an invalid counter")
            maximum = max(maximum, counter)
    candidate = max(maximum + 1, time.time_ns())
    if candidate > _UINT64_MAX:
        _refuse("durability challenge counter space is exhausted")
    return candidate


def _child_invocation(
    template: Mapping[str, Any],
    *,
    phase: str,
    executable: str,
    validator_zipapp: str,
    invocation_path: Path,
    challenge_path: Path | None = None,
    challenge_sha256: str | None = None,
    acknowledgement_path: Path | None = None,
) -> tuple[dict[str, Any], list[str]]:
    if phase not in ("PRE_RESTART", "POST_RESTART"):
        _refuse("child durability invocation phase differs")
    if phase == "POST_RESTART":
        if challenge_path is None or challenge_sha256 is None or acknowledgement_path is None:
            _refuse("POST_RESTART child invocation is incomplete")
    elif any(
        item is not None
        for item in (challenge_path, challenge_sha256, acknowledgement_path)
    ):
        _refuse("PRE_RESTART child invocation has a POST suffix")
    arguments = [
        "--validator-zipapp",
        validator_zipapp,
        "--validator-zipapp-byte-count",
        str(template["validator_zipapp_byte_count"]),
        "--validator-zipapp-sha256",
        template["validator_zipapp_sha256"],
        "--host-runtime-lock-acquisition-sha256",
        template["host_runtime_lock_acquisition_sha256"],
        "--durability-probe-phase",
        phase,
        "--invocation-preimage",
        os.fspath(invocation_path),
    ]
    if phase == "POST_RESTART":
        assert challenge_path is not None
        assert challenge_sha256 is not None
        assert acknowledgement_path is not None
        arguments.extend(
            (
                "--restart-challenge",
                os.fspath(challenge_path),
                "--restart-challenge-sha256",
                challenge_sha256,
                "--write-acknowledgement",
                os.fspath(acknowledgement_path),
            )
        )
    bootstrap = base64.b64decode(
        template["bootstrap_source_utf8_base64"].encode("ascii", "strict"),
        validate=True,
    ).decode("utf-8", "strict")
    vector = [executable, "-I", "-S", "-B", "-c", bootstrap, *arguments]
    command_raw = subprocess.list2cmdline(vector).encode("utf-16le", "strict")
    invocation = {
        "schema": "stage_f_durability_probe_invocation/v1",
        "phase": phase,
        "binding_validator_identity": template["binding_validator_identity"],
        "execution_environment_policy_identity": template[
            "execution_environment_policy_identity"
        ],
        "host_validation_runtime_identity": template[
            "host_validation_runtime_identity"
        ],
        "host_runtime_lock_acquisition_sha256": template[
            "host_runtime_lock_acquisition_sha256"
        ],
        "bootstrap_source_path": "stage_f_binding/locked_zipapp_bootstrap.py",
        "bootstrap_git_row": template["bootstrap_git_row"],
        "bootstrap_source_byte_count": template["bootstrap_source_byte_count"],
        "bootstrap_source_utf8_base64": template[
            "bootstrap_source_utf8_base64"
        ],
        "executable_path_identity": _private_path_identity(executable),
        "validator_zipapp_path_identity": _private_path_identity(validator_zipapp),
        "validator_zipapp_byte_count": template["validator_zipapp_byte_count"],
        "validator_zipapp_sha256": template["validator_zipapp_sha256"],
        "invocation_preimage_path_identity": _private_path_identity(invocation_path),
        "restart_challenge_path_identity": (
            _private_path_identity(challenge_path) if challenge_path else None
        ),
        "restart_challenge_sha256": challenge_sha256,
        "acknowledgement_path_identity": (
            _private_path_identity(acknowledgement_path)
            if acknowledgement_path
            else None
        ),
        "command_schema": f"PYTHON_LOCKED_ZIPAPP_STAGE_F_BINDING_VALIDATOR_{phase}_V1",
        "command_line_construction": "BOUND_HOST_CPYTHON_SUBPROCESS_LIST2CMDLINE",
        "command_line_encoding": "UTF-16LE_WITHOUT_TERMINAL_NUL",
        "command_line_base64": base64.b64encode(command_raw).decode("ascii"),
        "command_line_utf16_code_unit_count": len(command_raw) // 2,
        "entrypoint_mode": "EXACT_GIT_BOOTSTRAP_C_OPTION_LOCKED_DETERMINISTIC_ZIPAPP",
        "isolated_mode": True,
        "network_access_permitted": False,
        "scientific_counters": dict(ZERO_SCIENCE_COUNTERS),
    }
    _write_temporary(canonical_bytes(invocation), invocation_path)
    return invocation, vector


def _execute_orchestrator_probe(
    invocation: Mapping[str, Any],
    process: Mapping[str, Any],
    invocation_path: Path,
    *,
    executable: str,
    validator_zipapp: str,
    host_runtime_lock_acquisition: Mapping[str, Any],
    host_runtime_lock_acquisition_path: str,
    authority_schema_path: str,
) -> dict[str, Any]:
    parent = invocation_path.parent
    if not parent.is_dir() or parent.is_symlink():
        _refuse("orchestrator invocation parent is not a stable private directory")
    token = (
        "stage-f-durability-"
        + hashlib.sha256(canonical_bytes(invocation)).hexdigest()[:16]
        + f"-{os.getpid()}-{time.time_ns()}"
    )
    pre_invocation_path = parent / f"{token}.pre-restart-invocation.json"
    post_invocation_path = parent / f"{token}.post-restart-invocation.json"
    pre_evidence_path = parent / f"{token}.pre-evidence.json"
    post_evidence_path = parent / f"{token}.post-evidence.json"
    pre_lock_path = Path(os.fspath(pre_invocation_path) + ".bootstrap-lock.json")
    post_lock_path = Path(os.fspath(post_invocation_path) + ".bootstrap-lock.json")
    challenge_temporary = parent / f"{token}.challenge.partial"
    challenge_path = parent / f"{token}.challenge.json"
    acknowledgement_path = parent / f"{token}.acknowledgement.json"
    orchestrator_evidence_path = parent / f"{token}.orchestrator-evidence.json"
    probe_work_started = _orchestrator_utc()
    if (
        not isinstance(host_runtime_lock_acquisition, Mapping)
        or hashlib.sha256(canonical_bytes(host_runtime_lock_acquisition)).hexdigest()
        != invocation["host_runtime_lock_acquisition_sha256"]
    ):
        _refuse("validated external host-runtime-lock acquisition is absent")
    pre_invocation, pre_vector = _child_invocation(
        invocation,
        phase="PRE_RESTART",
        executable=executable,
        validator_zipapp=validator_zipapp,
        invocation_path=pre_invocation_path,
    )
    pre_handle, pre_launch = _orchestrator_create_process(
        executable,
        pre_vector,
        pre_invocation,
        phase="PRE_RESTART",
        orchestrator_process=process,
    )
    pre_wait = _orchestrator_wait_and_query(
        pre_handle,
        pre_launch,
        prefix="terminated",
        child_evidence_path=pre_evidence_path,
    )
    pre_evidence = _read_canonical_probe_evidence(pre_evidence_path)
    terminated_process = pre_evidence.get("process")
    if not isinstance(terminated_process, dict):
        _refuse("PRE_RESTART evidence omits its process instance")
    if (
        terminated_process.get("process_id") != pre_launch["process_id"]
        or terminated_process.get("creation_filetime_uint64")
        != pre_wait["terminated_process_creation_filetime_uint64"]
    ):
        _refuse("PRE_RESTART child process evidence differs from Win32 queries")
    pre_lock = _artifact_lock_from_raw(
        _read_canonical_probe_evidence(pre_lock_path),
        role="TERMINATED_PROBE_PROCESS",
        process=terminated_process,
        invocation=pre_invocation,
    )
    challenge = {
        "schema": "stage_f_durability_restart_challenge/v1",
        "orchestrator_process": dict(process),
        "terminated_process": terminated_process,
        "published_final_sha256": hashlib.sha256(
            _SYNTHETIC_DURABILITY_PAYLOAD
        ).hexdigest(),
        "challenge_counter": _next_challenge_counter(parent),
        "challenge_issued_utc": _orchestrator_utc(),
    }
    challenge_raw = canonical_bytes(challenge)
    challenge_sha256 = hashlib.sha256(challenge_raw).hexdigest()
    challenge_write = _orchestrator_control_write(
        challenge_temporary,
        challenge_raw,
        content_role="RESTART_CHALLENGE_TEMPORARY",
        actor_process=process,
    )
    challenge_atomic, _challenge_move_completed = _orchestrator_atomic_publish(
        challenge_temporary, challenge_path
    )
    challenge_directory = _orchestrator_directory_observation(
        challenge_path,
        challenge_atomic,
        actor_process=process,
        evidence_source="RESTART_CHALLENGE_ATOMIC_PUBLICATION_MOVEFILEEXW_WRITE_THROUGH",
    )
    challenge_publication = {
        "schema": "stage_f_durability_challenge_publication/v1",
        "actor_process_id": process["process_id"],
        "actor_process_creation_filetime_uint64": process[
            "creation_filetime_uint64"
        ],
        "temporary_write_observation": challenge_write,
        "atomic_publication_observation": challenge_atomic,
        "directory_durability_observation": challenge_directory,
        "published_path_identity": _private_path_identity(challenge_path),
        "published_byte_count": len(challenge_raw),
        "published_sha256": challenge_sha256,
        "completed_before_launch": True,
    }
    post_invocation, post_vector = _child_invocation(
        invocation,
        phase="POST_RESTART",
        executable=executable,
        validator_zipapp=validator_zipapp,
        invocation_path=post_invocation_path,
        challenge_path=challenge_path,
        challenge_sha256=challenge_sha256,
        acknowledgement_path=acknowledgement_path,
    )
    post_handle, post_launch = _orchestrator_create_process(
        executable,
        post_vector,
        post_invocation,
        phase="POST_RESTART",
        orchestrator_process=process,
    )
    post_wait = _orchestrator_wait_and_query(
        post_handle,
        post_launch,
        prefix="resumed",
        child_evidence_path=post_evidence_path,
    )
    post_evidence = _read_canonical_probe_evidence(post_evidence_path)
    resumed_process = post_evidence.get("process")
    if not isinstance(resumed_process, dict):
        _refuse("POST_RESTART evidence omits its process instance")
    if (
        resumed_process.get("process_id") != post_launch["process_id"]
        or resumed_process.get("creation_filetime_uint64")
        != post_wait["resumed_process_creation_filetime_uint64"]
    ):
        _refuse("POST_RESTART child process evidence differs from Win32 queries")
    post_lock = _artifact_lock_from_raw(
        _read_canonical_probe_evidence(post_lock_path),
        role="RESUMED_PROBE_PROCESS",
        process=resumed_process,
        invocation=post_invocation,
    )
    pre_actions = pre_evidence.get("ordered_actions")
    post_actions = post_evidence.get("ordered_actions")
    if not isinstance(pre_actions, list) or not isinstance(post_actions, list):
        _refuse("child durability evidence omits its ordered actions")
    ordered_actions = [*pre_actions, *post_actions]
    validate_durability_action_trace(ordered_actions)
    acknowledgement = post_evidence.get("acknowledgement_preimage")
    acknowledgement_write = post_evidence.get("acknowledgement_write_observation")
    if not isinstance(acknowledgement, dict) or not isinstance(
        acknowledgement_write, dict
    ):
        _refuse("POST_RESTART evidence omits the acknowledgement lifecycle")
    restart = {
        "orchestrator_process": dict(process),
        "terminated_process": terminated_process,
        "resumed_process": resumed_process,
        "process_identity_api": "GetProcessId_GetProcessTimes_QueryFullProcessImageNameW_GetCommandLineW_LOCKED_BOOTSTRAP_VERIFIED_INVOCATION",
        "terminated_process_launch_observation": pre_launch,
        "resumed_process_launch_observation": post_launch,
        **pre_wait,
        "challenge_path_identity": _private_path_identity(challenge_path),
        "challenge_preimage": challenge,
        "challenge_sha256": challenge_sha256,
        "challenge_publication_observation": challenge_publication,
        "acknowledgement_path_identity": _private_path_identity(
            acknowledgement_path
        ),
        "acknowledgement_preimage": acknowledgement,
        "acknowledgement_sha256": post_evidence["acknowledgement_sha256"],
        "acknowledgement_write_observation": acknowledgement_write,
        "resumed_process_acknowledged_exact_challenge": True,
        **post_wait,
        "launch_utc": post_launch["launch_utc"],
        "handshake_completed_utc": acknowledgement_write["close_completed_utc"],
        "restart_utc": post_actions[0]["observed_utc"],
    }
    _validate_restart(
        restart,
        expected_published_final_sha256=hashlib.sha256(
            _SYNTHETIC_DURABILITY_PAYLOAD
        ).hexdigest(),
    )
    probe_work_completed = _orchestrator_utc()
    evidence = {
        "schema": "stage_f_durability_orchestrator_execution_evidence/v1",
        "orchestrator_process": dict(process),
        "orchestrator_invocation_preimage": dict(invocation),
        "host_runtime_lock_acquisition_preimage": dict(
            host_runtime_lock_acquisition
        ),
        "host_runtime_lock_acquisition_path": host_runtime_lock_acquisition_path,
        "authority_schema_path": authority_schema_path,
        "terminated_invocation_preimage": pre_invocation,
        "resumed_invocation_preimage": post_invocation,
        "terminated_artifact_lock_observation": pre_lock,
        "resumed_artifact_lock_observation": post_lock,
        "probe_work_started_utc": probe_work_started,
        "probe_work_completed_utc": probe_work_completed,
        "synthetic_payload_base64": base64.b64encode(
            _SYNTHETIC_DURABILITY_PAYLOAD
        ).decode("ascii"),
        "synthetic_payload_identity": pre_evidence["synthetic_payload_identity"],
        "temporary_path": pre_evidence["temporary_path"],
        "temporary_path_identity": pre_evidence["temporary_path_identity"],
        "final_path": pre_evidence["final_path"],
        "final_path_identity": pre_evidence["final_path_identity"],
        "directory_target_path": pre_evidence["directory_target_path"],
        "directory_target_identity": pre_evidence["directory_target_identity"],
        "payload_write_observation": pre_evidence["payload_write_observation"],
        "atomic_publication_observation": pre_evidence[
            "atomic_publication_observation"
        ],
        "directory_durability_observation": pre_evidence[
            "directory_durability_observation"
        ],
        "restart_observation": restart,
        "post_restart_reread_byte_count": post_evidence[
            "post_restart_reread_byte_count"
        ],
        "post_restart_reread_sha256": post_evidence[
            "post_restart_reread_sha256"
        ],
        "corrupt_fixture_byte_count": post_evidence["corrupt_fixture_byte_count"],
        "corrupt_fixture_sha256": post_evidence["corrupt_fixture_sha256"],
        "orphan_partial_byte_count": post_evidence["orphan_partial_byte_count"],
        "orphan_partial_sha256": post_evidence["orphan_partial_sha256"],
        "recovered_final_sha256": post_evidence["recovered_final_sha256"],
        "ordered_actions": ordered_actions,
        "action_count": len(ordered_actions),
        "child_execution_evidence": [
            {
                "phase": "PRE_RESTART",
                "path": os.fspath(pre_evidence_path),
                "sha256": hashlib.sha256(pre_evidence_path.read_bytes()).hexdigest(),
                "bootstrap_lock_path": os.fspath(pre_lock_path),
                "bootstrap_lock_sha256": hashlib.sha256(
                    pre_lock_path.read_bytes()
                ).hexdigest(),
            },
            {
                "phase": "POST_RESTART",
                "path": os.fspath(post_evidence_path),
                "sha256": hashlib.sha256(post_evidence_path.read_bytes()).hexdigest(),
                "bootstrap_lock_path": os.fspath(post_lock_path),
                "bootstrap_lock_sha256": hashlib.sha256(
                    post_lock_path.read_bytes()
                ).hexdigest(),
            },
        ],
        "scientific_counters": dict(ZERO_SCIENCE_COUNTERS),
    }
    _write_probe_evidence(orchestrator_evidence_path, evidence)
    return {
        "execution_evidence_path": os.fspath(orchestrator_evidence_path),
        "execution_evidence_sha256": hashlib.sha256(canonical_bytes(evidence)).hexdigest(),
        "ordered_action_count": 17,
    }


def execute_durability_probe_phase(
    invocation: Mapping[str, Any],
    *,
    argument_values: Mapping[str, Any],
    process: Mapping[str, Any],
) -> dict[str, Any]:
    """Execute one frozen durability phase without importing scientific code.

    ORCHESTRATOR launches PRE_RESTART and POST_RESTART with the retained direct
    CreateProcessW route.  Child phases retain canonical evidence in fresh
    sibling files, which lets the orchestrator reconstruct the complete
    seventeen-action trace after each process has returned and been queried.
    Host-runtime and outer bootstrap lock acquisition/release remain controller
    responsibilities and are intentionally not fabricated here.
    """

    validate_no_science_counters(invocation["scientific_counters"])
    phase = invocation["phase"]
    invocation_path = _path(
        argument_values["--invocation-preimage"], "durability invocation path"
    )
    if phase == "ORCHESTRATOR":
        return _execute_orchestrator_probe(
            invocation,
            process,
            invocation_path,
            executable=os.fspath(argument_values.get("_executable", "")),
            validator_zipapp=argument_values["--validator-zipapp"],
            host_runtime_lock_acquisition=argument_values.get(
                "_host_runtime_lock_acquisition_preimage", {}
            ),
            host_runtime_lock_acquisition_path=os.fspath(
                argument_values.get("_host_runtime_lock_acquisition_path", "")
            ),
            authority_schema_path=os.fspath(
                argument_values.get("_authority_schema_path", "")
            ),
        )
    if phase == "PRE_RESTART":
        return _execute_pre_restart_probe(invocation, process, invocation_path)
    if phase == "POST_RESTART":
        return _execute_post_restart_probe(
            invocation,
            process,
            invocation_path,
            challenge_path=_path(
                argument_values["--restart-challenge"], "restart challenge"
            ),
            challenge_sha256=argument_values["--restart-challenge-sha256"],
            acknowledgement_path=_path(
                argument_values["--write-acknowledgement"],
                "restart acknowledgement",
            ),
        )
    _refuse("durability probe phase differs")
    raise AssertionError("unreachable")


# ---------------------------------------------------------------------------
# External host-runtime protection and composite controller
# ---------------------------------------------------------------------------


def _host_runtime_path_parts(runtime_root: str) -> list[str]:
    """Return the exact volume-root-to-runtime-root volume-GUID anchor chain."""

    if (
        not isinstance(runtime_root, str)
        or unicodedata.normalize("NFC", runtime_root) != runtime_root
        or not runtime_root.startswith("\\\\?\\Volume{")
    ):
        _refuse("host runtime root is not an exact NFC volume-GUID path")
    parsed = PureWindowsPath(runtime_root.rstrip("\\"))
    anchor = parsed.anchor.rstrip("\\")
    if not anchor.startswith("\\\\?\\Volume{") or not anchor.endswith("}"):
        _refuse("host runtime root has no normalized volume-GUID anchor")
    parts = parsed.parts[1:]
    if not parts:
        _refuse("host runtime root must be below the selected volume root")
    result = [anchor]
    current = anchor
    for part in parts:
        if part in ("", ".", "..") or "\\" in part or "/" in part:
            _refuse("host runtime path anchor chain is malformed")
        current += "\\" + part
        result.append(current)
    if len(result) > 64:
        _refuse("host runtime path anchor chain exceeds sixty-four anchors")
    return result


def _host_runtime_child(root: str, relative: str) -> str:
    if not isinstance(relative, str) or unicodedata.normalize("NFC", relative) != relative:
        _refuse("host runtime relative path is not exact NFC")
    if relative == ".":
        return root
    parts = relative.split("/")
    if (
        not parts
        or any(part in ("", ".", "..") or "\\" in part for part in parts)
        or PureWindowsPath(relative).is_absolute()
    ):
        _refuse("host runtime relative path is not a canonical child path")
    return root.rstrip("\\") + "\\" + "\\".join(parts)


def _host_runtime_apis() -> dict[str, Any]:
    if sys.platform != "win32":
        _refuse("host-runtime composite control requires Win32")
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    advapi32 = ctypes.WinDLL("advapi32", use_last_error=True)
    kernelbase = ctypes.WinDLL("KernelBase", use_last_error=True)

    def bind(dll: Any, name: str, arguments: tuple[Any, ...], result: Any) -> Any:
        function = getattr(dll, name)
        function.argtypes = arguments
        function.restype = result
        return function

    return {
        "kernel32": kernel32,
        "create": bind(
            kernel32,
            "CreateFileW",
            (
                ctypes.c_wchar_p,
                ctypes.c_uint32,
                ctypes.c_uint32,
                ctypes.c_void_p,
                ctypes.c_uint32,
                ctypes.c_uint32,
                ctypes.c_void_p,
            ),
            ctypes.c_void_p,
        ),
        "close": bind(kernel32, "CloseHandle", (ctypes.c_void_p,), ctypes.c_int),
        "get_final": bind(
            kernel32,
            "GetFinalPathNameByHandleW",
            (ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_uint32, ctypes.c_uint32),
            ctypes.c_uint32,
        ),
        "get_info": bind(
            kernel32,
            "GetFileInformationByHandleEx",
            (ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_uint32),
            ctypes.c_int,
        ),
        "read": bind(
            kernel32,
            "ReadFile",
            (
                ctypes.c_void_p,
                ctypes.c_void_p,
                ctypes.c_uint32,
                ctypes.POINTER(ctypes.c_uint32),
                ctypes.c_void_p,
            ),
            ctypes.c_int,
        ),
        "rewind": bind(
            kernel32,
            "SetFilePointerEx",
            (ctypes.c_void_p, ctypes.c_int64, ctypes.c_void_p, ctypes.c_uint32),
            ctypes.c_int,
        ),
        "duplicate": bind(
            kernel32,
            "DuplicateHandle",
            (
                ctypes.c_void_p,
                ctypes.c_void_p,
                ctypes.c_void_p,
                ctypes.POINTER(ctypes.c_void_p),
                ctypes.c_uint32,
                ctypes.c_int,
                ctypes.c_uint32,
            ),
            ctypes.c_int,
        ),
        "current_process": bind(kernel32, "GetCurrentProcess", (), ctypes.c_void_p),
        "compare": bind(
            kernelbase,
            "CompareObjectHandles",
            (ctypes.c_void_p, ctypes.c_void_p),
            ctypes.c_int,
        ),
        "virtual_alloc": bind(
            kernel32,
            "VirtualAlloc",
            (ctypes.c_void_p, ctypes.c_size_t, ctypes.c_uint32, ctypes.c_uint32),
            ctypes.c_void_p,
        ),
        "virtual_free": bind(
            kernel32,
            "VirtualFree",
            (ctypes.c_void_p, ctypes.c_size_t, ctypes.c_uint32),
            ctypes.c_int,
        ),
        "create_event": bind(
            kernel32,
            "CreateEventW",
            (ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_wchar_p),
            ctypes.c_void_p,
        ),
        "read_changes": bind(
            kernel32,
            "ReadDirectoryChangesW",
            (
                ctypes.c_void_p,
                ctypes.c_void_p,
                ctypes.c_uint32,
                ctypes.c_int,
                ctypes.c_uint32,
                ctypes.c_void_p,
                ctypes.c_void_p,
                ctypes.c_void_p,
            ),
            ctypes.c_int,
        ),
        "get_overlapped": bind(
            kernel32,
            "GetOverlappedResult",
            (
                ctypes.c_void_p,
                ctypes.c_void_p,
                ctypes.POINTER(ctypes.c_uint32),
                ctypes.c_int,
            ),
            ctypes.c_int,
        ),
        "cancel": bind(
            kernel32,
            "CancelIoEx",
            (ctypes.c_void_p, ctypes.c_void_p),
            ctypes.c_int,
        ),
        "wait_many": bind(
            kernel32,
            "WaitForMultipleObjects",
            (ctypes.c_uint32, ctypes.c_void_p, ctypes.c_int, ctypes.c_uint32),
            ctypes.c_uint32,
        ),
        "get_security": bind(
            advapi32,
            "GetSecurityInfo",
            (
                ctypes.c_void_p,
                ctypes.c_uint32,
                ctypes.c_uint32,
                ctypes.c_void_p,
                ctypes.c_void_p,
                ctypes.c_void_p,
                ctypes.c_void_p,
                ctypes.POINTER(ctypes.c_void_p),
            ),
            ctypes.c_uint32,
        ),
        "security_valid": bind(
            advapi32,
            "IsValidSecurityDescriptor",
            (ctypes.c_void_p,),
            ctypes.c_int,
        ),
        "security_control": bind(
            advapi32,
            "GetSecurityDescriptorControl",
            (ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint16), ctypes.POINTER(ctypes.c_uint32)),
            ctypes.c_int,
        ),
        "security_length": bind(
            advapi32,
            "GetSecurityDescriptorLength",
            (ctypes.c_void_p,),
            ctypes.c_uint32,
        ),
        "local_free": bind(kernel32, "LocalFree", (ctypes.c_void_p,), ctypes.c_void_p),
    }


def _host_runtime_handle_projection(
    apis: Mapping[str, Any], handle: int
) -> dict[str, Any]:
    buffer = ctypes.create_unicode_buffer(32768)
    length = int(apis["get_final"](handle, buffer, len(buffer), 1))
    if not 0 < length < len(buffer):
        raise _windows_error("GetFinalPathNameByHandleW(host runtime)")
    resolved = buffer.value.rstrip("\\")
    standard, file_id, attributes = _windows_query_file_info(apis["get_info"], handle)
    return {
        "resolved_path": resolved,
        "resolved_path_identity": _private_path_identity(resolved),
        "volume_serial_number": file_id[0],
        "file_id_128": file_id[1].hex(),
        "allocation_size": standard[0],
        "end_of_file": standard[1],
        "number_of_links": standard[2],
        "delete_pending": bool(standard[3]),
        "directory": bool(standard[4]),
        "raw_file_attributes": attributes[0],
        "reparse_tag": attributes[1],
    }


def _host_runtime_security_lifecycle(
    apis: Mapping[str, Any], handle: int
) -> dict[str, Any]:
    descriptor = ctypes.c_void_p()
    result = int(
        apis["get_security"](
            handle, 1, 7, None, None, None, None, ctypes.byref(descriptor)
        )
    )
    query_completed = _orchestrator_utc()
    if result != 0 or not descriptor.value:
        _refuse(f"GetSecurityInfo(host runtime) failed with result {result}")
    address = int(descriptor.value)
    failure: BaseException | None = None
    try:
        valid = bool(apis["security_valid"](descriptor))
        control = ctypes.c_uint16(0)
        revision = ctypes.c_uint32(0)
        control_ok = bool(
            apis["security_control"](
                descriptor, ctypes.byref(control), ctypes.byref(revision)
            )
        )
        count = int(apis["security_length"](descriptor))
        if not valid or not control_ok or not count or not control.value & 0x8000:
            _refuse("host-runtime security descriptor lifecycle is invalid")
        digest = hashlib.sha256(ctypes.string_at(address, count)).hexdigest()
        hashed = _orchestrator_utc()
    except BaseException as exc:
        failure = exc
        valid = False
        control_ok = False
        count = 0
        digest = ""
        hashed = _orchestrator_utc()
    freed_result = apis["local_free"](descriptor)
    freed = _orchestrator_utc()
    if failure is not None:
        raise failure
    if freed_result not in (None, 0):
        raise _windows_error("LocalFree(host runtime security descriptor)")
    return {
        "security_query_api": "GetSecurityInfo_SE_FILE_OBJECT",
        "security_information_mask": 7,
        "security_query_handle_value_uint64": handle,
        "security_query_result_code": result,
        "security_descriptor_address_uint64": address,
        "security_descriptor_validation_api": "IsValidSecurityDescriptor",
        "security_descriptor_validation_input_address_uint64": address,
        "security_descriptor_validation_returned_nonzero": valid,
        "security_descriptor_control_api": "GetSecurityDescriptorControl",
        "security_descriptor_control_input_address_uint64": address,
        "security_descriptor_control_returned_nonzero": control_ok,
        "security_descriptor_control_uint16": int(control.value),
        "security_descriptor_self_relative_control_mask": 32768,
        "security_descriptor_revision_uint32": int(revision.value),
        "security_descriptor_self_relative": True,
        "security_descriptor_length_api": "GetSecurityDescriptorLength",
        "security_descriptor_length_input_address_uint64": address,
        "security_descriptor_byte_count": count,
        "security_descriptor_hash_input_address_uint64": address,
        "security_descriptor_hash_input_byte_count": count,
        "security_descriptor_sha256": digest,
        "security_query_completed_utc": query_completed,
        "security_descriptor_hashed_utc": hashed,
        "security_descriptor_free_api": "LocalFree",
        "security_descriptor_free_input_address_uint64": address,
        "security_descriptor_free_called_once": True,
        "security_descriptor_free_result": "NULL",
        "security_descriptor_freed_utc": freed,
    }


def _host_runtime_read_handle(
    apis: Mapping[str, Any], handle: int, count: int
) -> bytes:
    if count < 0:
        _refuse("host runtime file has a negative byte count")
    chunks: list[bytes] = []
    remaining = count
    while remaining:
        requested = min(remaining, 1024 * 1024, _UINT32_MAX)
        buffer = ctypes.create_string_buffer(requested)
        returned = ctypes.c_uint32(0)
        if not apis["read"](
            handle, buffer, requested, ctypes.byref(returned), None
        ):
            raise _windows_error("ReadFile(host runtime)")
        if returned.value == 0 or returned.value > requested:
            _refuse("host runtime file ended before its held-handle byte count")
        chunks.append(bytes(buffer.raw[: returned.value]))
        remaining -= returned.value
    extra = ctypes.create_string_buffer(1)
    returned = ctypes.c_uint32(0)
    if not apis["read"](handle, extra, 1, ctypes.byref(returned), None):
        raise _windows_error("ReadFile(host runtime EOF)")
    if returned.value != 0:
        _refuse("host runtime file grew beyond its held-handle byte count")
    return b"".join(chunks)


class _HostRuntimeProtectionState:
    """Own every retained host-runtime resource until one final release."""

    def __init__(self, apis: Mapping[str, Any]) -> None:
        self.apis = apis
        self.anchors: list[dict[str, Any]] = []
        self.watches: list[dict[str, Any]] = []
        self.files: list[dict[str, Any]] = []
        self.released = False

    def abort(self) -> None:
        if self.released:
            return
        first: BaseException | None = None
        for watch in reversed(self.watches):
            try:
                if not watch.get("cancelled"):
                    self.apis["cancel"](watch["handle"], watch["overlapped"])
                    transferred = ctypes.c_uint32(0)
                    self.apis["get_overlapped"](
                        watch["handle"],
                        watch["overlapped"],
                        ctypes.byref(transferred),
                        True,
                    )
                for name in ("event", "handle"):
                    value = watch.get(name)
                    if value and not self.apis["close"](value) and first is None:
                        first = _windows_error("CloseHandle(aborted host-runtime watch)")
                for name in ("overlapped", "buffer"):
                    value = watch.get(name)
                    if value and not self.apis["virtual_free"](value, 0, 0x8000) and first is None:
                        first = _windows_error("VirtualFree(aborted host-runtime watch)")
            except BaseException as exc:
                if first is None:
                    first = exc
        for file_state in reversed(self.files):
            if file_state.get("handle") and not self.apis["close"](file_state["handle"]):
                if first is None:
                    first = _windows_error("CloseHandle(aborted host-runtime file)")
        for anchor in reversed(self.anchors):
            for name in ("guard", "handle"):
                value = anchor.get(name)
                if value and not self.apis["close"](value) and first is None:
                    first = _windows_error("CloseHandle(aborted host-runtime anchor)")
        self.released = True
        if first is not None:
            raise first


def _host_runtime_current_holder(
    apis: Mapping[str, Any], executable_path: str, executable_sha256: str
) -> dict[str, Any]:
    kernel32 = apis["kernel32"]
    get_pid = kernel32.GetCurrentProcessId
    get_pid.argtypes = ()
    get_pid.restype = ctypes.c_uint32
    get_times = kernel32.GetProcessTimes
    get_times.argtypes = (
        ctypes.c_void_p,
        ctypes.POINTER(_ORCH_FILETIME),
        ctypes.POINTER(_ORCH_FILETIME),
        ctypes.POINTER(_ORCH_FILETIME),
        ctypes.POINTER(_ORCH_FILETIME),
    )
    get_times.restype = ctypes.c_int
    get_command = kernel32.GetCommandLineW
    get_command.argtypes = ()
    get_command.restype = ctypes.c_void_p
    creation, exit_time, kernel_time, user_time = (_ORCH_FILETIME() for _ in range(4))
    if not get_times(
        apis["current_process"](),
        ctypes.byref(creation),
        ctypes.byref(exit_time),
        ctypes.byref(kernel_time),
        ctypes.byref(user_time),
    ):
        raise _windows_error("GetProcessTimes(host-runtime lock holder)")
    command_pointer = int(get_command() or 0)
    if not command_pointer:
        raise _windows_error("GetCommandLineW(host-runtime lock holder)")
    query_image = kernel32.QueryFullProcessImageNameW
    query_image.argtypes = (
        ctypes.c_void_p,
        ctypes.c_uint32,
        ctypes.c_wchar_p,
        ctypes.POINTER(ctypes.c_uint32),
    )
    query_image.restype = ctypes.c_int
    image_buffer = ctypes.create_unicode_buffer(32768)
    image_count = ctypes.c_uint32(len(image_buffer))
    if not query_image(
        apis["current_process"](),
        0,
        image_buffer,
        ctypes.byref(image_count),
    ):
        raise _windows_error("QueryFullProcessImageNameW(host-runtime lock holder)")
    image_handle = apis["create"](
        image_buffer.value, 0x80000000, 1, None, 3, 0x00200000, None
    )
    if image_handle in (None, _INVALID_HANDLE_VALUE):
        raise _windows_error("CreateFileW(host-runtime lock-holder image)")
    image_handle = int(image_handle)
    failure: BaseException | None = None
    try:
        image_projection = _host_runtime_handle_projection(apis, image_handle)
        if image_projection["resolved_path"] != executable_path.rstrip("\\"):
            _refuse("designated controller is not executing from the frozen host runtime")
    except BaseException as exc:
        failure = exc
    if not apis["close"](image_handle) and failure is None:
        failure = _windows_error("CloseHandle(host-runtime lock-holder image)")
    if failure is not None:
        raise failure
    command_raw = ctypes.wstring_at(command_pointer).encode("utf-16le", "strict")
    return {
        "actor_role": "DESIGNATED_LOCAL_STAGE_F_CONTROLLER_LOCK_HOLDER",
        "trust_boundary": "DESIGNATED_LOCAL_CONTROLLER_PROCESS_AND_WINDOWS_KERNEL",
        "process_id": int(get_pid()),
        "process_creation_filetime_uint64": _filetime_uint64(creation),
        "executable_path_identity": _private_path_identity(executable_path),
        "executable_sha256": executable_sha256,
        "command_line_sha256": hashlib.sha256(command_raw).hexdigest(),
        "windows_kernel_share_enforcement_relied_upon": True,
        "scientific_counters": dict(ZERO_SCIENCE_COUNTERS),
    }


def _host_runtime_open_anchor(
    state: _HostRuntimeProtectionState,
    path: str,
    *,
    ordinal: int,
    count: int,
) -> dict[str, Any]:
    apis = state.apis
    opened = _orchestrator_utc()
    open_path = path + "\\" if ordinal == 1 else path
    handle = apis["create"](open_path, 131200, 1, None, 3, 35651584, None)
    if handle in (None, _INVALID_HANDLE_VALUE):
        raise _windows_error("CreateFileW(host-runtime path anchor)")
    handle = int(handle)
    anchor_state: dict[str, Any] = {"path": path, "handle": handle, "guard": 0}
    state.anchors.append(anchor_state)
    duplicate = ctypes.c_void_p()
    current = apis["current_process"]()
    if not apis["duplicate"](
        current,
        handle,
        current,
        ctypes.byref(duplicate),
        0,
        False,
        2,
    ) or not duplicate.value:
        raise _windows_error("DuplicateHandle(host-runtime path anchor)")
    guard = int(duplicate.value)
    if guard == handle:
        _refuse("host-runtime continuity guard equals its source handle")
    anchor_state["guard"] = guard
    duplicated = _orchestrator_utc()
    query_started = _orchestrator_utc()
    projection = _host_runtime_handle_projection(apis, handle)
    if (
        projection["resolved_path"] != path.rstrip("\\")
        or not projection["directory"]
        or projection["reparse_tag"] != 0
        or projection["raw_file_attributes"] & 0x400
    ):
        _refuse("host-runtime anchor handle resolved to another or reparse path")
    security = _host_runtime_security_lifecycle(apis, handle)
    acquired = _orchestrator_utc()
    role = (
        "SELECTED_VOLUME_ROOT"
        if ordinal == 1
        else "RUNTIME_ROOT"
        if ordinal == count
        else "RUNTIME_PATH_ANCESTOR"
    )
    row = {
        "ordinal": ordinal,
        "anchor_role": role,
        "parent_anchor_ordinal": None if ordinal == 1 else ordinal - 1,
        "anchor_path_identity": _private_path_identity(path.rstrip("\\")),
        "open_api": "CreateFileW",
        "desired_access": 131200,
        "share_mode": 1,
        "security_attributes": "NULL",
        "creation_disposition": 3,
        "flags_and_attributes": 35651584,
        "handle_valid": True,
        "anchor_handle_value_uint64": handle,
        "anchor_handle_opened_utc": opened,
        "continuity_guard_duplicate_api": "DuplicateHandle",
        "continuity_guard_source_process": "GetCurrentProcess",
        "continuity_guard_source_handle_value_uint64": handle,
        "continuity_guard_target_process": "GetCurrentProcess",
        "continuity_guard_inherit_handle": False,
        "continuity_guard_options_raw": 2,
        "continuity_guard_duplicate_returned_nonzero": True,
        "continuity_guard_handle_value_uint64": guard,
        "continuity_guard_handle_distinct_from_anchor": True,
        "continuity_guard_duplicated_utc": duplicated,
        "continuity_guard_held_at_acquisition_completion": True,
        "metadata_and_security_queries_started_utc": query_started,
        "resolved_path_api": "GetFinalPathNameByHandleW_FILE_NAME_NORMALIZED_VOLUME_NAME_GUID",
        "resolved_path_query_handle_value_uint64": handle,
        "resolved_path_identity": projection["resolved_path_identity"],
        "file_id_query_api": "GetFileInformationByHandleEx_FileIdInfo",
        "file_id_query_handle_value_uint64": handle,
        "volume_serial_number": projection["volume_serial_number"],
        "file_id_128": projection["file_id_128"],
        "file_attribute_tag_query_api": "GetFileInformationByHandleEx_FileAttributeTagInfo",
        "file_attribute_tag_query_handle_value_uint64": handle,
        "raw_file_attributes": projection["raw_file_attributes"],
        "reparse_tag": projection["reparse_tag"],
        "directory": True,
        "security_descriptor_query_lifecycle": security,
        "lock_acquired_utc": acquired,
        "file_share_write_flag_present": False,
        "file_share_delete_flag_present": False,
        "handle_held_at_acquisition_completion": True,
    }
    anchor_state["row"] = row
    return row


def _host_runtime_start_watch(
    state: _HostRuntimeProtectionState,
    anchors: Sequence[Mapping[str, Any]],
    *,
    ordinal: int,
) -> dict[str, Any]:
    apis = state.apis
    anchor_count = len(anchors)
    watched_ordinal = ordinal if ordinal < anchor_count else anchor_count
    protected_ordinal = ordinal + 1 if ordinal < anchor_count else anchor_count
    watched = state.anchors[watched_ordinal - 1]
    watched_row = anchors[watched_ordinal - 1]
    subtree = ordinal == anchor_count
    handle = apis["create"](
        watched["path"] + ("\\" if watched_ordinal == 1 else ""),
        1,
        1,
        None,
        3,
        1109393408,
        None,
    )
    if handle in (None, _INVALID_HANDLE_VALUE):
        raise _windows_error("CreateFileW(host-runtime change watch)")
    handle = int(handle)
    watch: dict[str, Any] = {
        "handle": handle,
        "event": 0,
        "buffer": 0,
        "overlapped": 0,
        "cancelled": False,
    }
    state.watches.append(watch)
    projection = _host_runtime_handle_projection(apis, handle)
    if (
        projection["resolved_path"] != watched["path"].rstrip("\\")
        or not projection["directory"]
        or projection["reparse_tag"] != 0
    ):
        _refuse("host-runtime watch resolved to another or reparse directory")
    buffer = int(apis["virtual_alloc"](None, 65536, 0x3000, 4) or 0)
    overlapped = int(apis["virtual_alloc"](None, 32, 0x3000, 4) or 0)
    if not buffer or not overlapped or buffer % 4 or overlapped % 4:
        _refuse("host-runtime watch storage allocation failed or is unaligned")
    watch["buffer"] = buffer
    watch["overlapped"] = overlapped
    if ctypes.string_at(buffer, 65536) != bytes(65536) or ctypes.string_at(overlapped, 32) != bytes(32):
        _refuse("host-runtime watch storage is not initially zero")
    event = apis["create_event"](None, True, False, None)
    if not event:
        raise _windows_error("CreateEventW(host-runtime change watch)")
    event = int(event)
    watch["event"] = event
    overlapped_view = _OVERLAPPED.from_address(overlapped)
    if ctypes.sizeof(overlapped_view) != 32:
        _refuse("host-runtime OVERLAPPED storage is not exactly 32 bytes")
    overlapped_view.hEvent = event
    if not apis["read_changes"](
        handle,
        buffer,
        65536,
        subtree,
        351,
        None,
        overlapped,
        None,
    ):
        raise _windows_error("ReadDirectoryChangesW(host runtime)")
    issued = _orchestrator_utc()
    transferred = ctypes.c_uint32(0)
    ctypes.set_last_error(0)
    completed = bool(
        apis["get_overlapped"](
            handle, overlapped, ctypes.byref(transferred), False
        )
    )
    error = 0 if completed else ctypes.get_last_error()
    pending = _orchestrator_utc()
    if completed or error != 996 or transferred.value != 0:
        _refuse("host-runtime change watch was not initially pending and quiet")
    row = {
        "schema": "stage_f_host_validation_runtime_tree_watch_acquisition/v1",
        "ordinal": ordinal,
        "watch_role": "RUNTIME_ROOT_SUBTREE" if subtree else "ANCHOR_SELF_DIRECT",
        "protected_anchor_ordinal": protected_ordinal,
        "watched_anchor_ordinal": watched_ordinal,
        "runtime_root_path_identity": anchors[-1]["anchor_path_identity"],
        "watched_directory_path_identity": watched_row["anchor_path_identity"],
        "open_api": "CreateFileW",
        "desired_access": 1,
        "share_mode": 1,
        "security_attributes": "NULL",
        "creation_disposition": 3,
        "flags_and_attributes": 1109393408,
        "handle_valid": True,
        "directory_handle_value_uint64": handle,
        "resolved_path_api": "GetFinalPathNameByHandleW_FILE_NAME_NORMALIZED_VOLUME_NAME_GUID",
        "resolved_path_query_handle_value_uint64": handle,
        "resolved_path_identity": projection["resolved_path_identity"],
        "file_id_query_api": "GetFileInformationByHandleEx_FileIdInfo",
        "file_id_query_handle_value_uint64": handle,
        "volume_serial_number": projection["volume_serial_number"],
        "file_id_128": projection["file_id_128"],
        "file_attribute_tag_query_api": "GetFileInformationByHandleEx_FileAttributeTagInfo",
        "file_attribute_tag_query_handle_value_uint64": handle,
        "raw_file_attributes": projection["raw_file_attributes"],
        "reparse_tag": 0,
        "directory": True,
        "change_watch_api": "ReadDirectoryChangesW",
        "watch_subtree": subtree,
        "notify_filter_raw": 351,
        "buffer_allocation_api": "VirtualAlloc",
        "buffer_allocation_type": 12288,
        "buffer_protection": 4,
        "buffer_base_address_uint64": buffer,
        "buffer_byte_count": 65536,
        "buffer_dword_aligned": True,
        "buffer_zero_initialized": True,
        "buffer_exclusive_to_watch": True,
        "overlapped_mode": True,
        "overlapped_allocation_api": "VirtualAlloc",
        "overlapped_allocation_type": 12288,
        "overlapped_storage_protection": 4,
        "overlapped_address_uint64": overlapped,
        "overlapped_byte_count": 32,
        "overlapped_dword_aligned": True,
        "overlapped_zero_initialized": True,
        "overlapped_storage_exclusive_to_watch": True,
        "overlapped_offset": 0,
        "overlapped_offset_high": 0,
        "event_creation_api": "CreateEventW",
        "event_security_attributes": "NULL",
        "event_name": "NULL",
        "event_manual_reset": True,
        "event_initial_state": False,
        "event_creation_returned_nonnull": True,
        "event_handle_value_uint64": event,
        "overlapped_event_handle_value_uint64": event,
        "overlapped_event_handle_nonnull": True,
        "overlapped_event_unique": True,
        "overlapped_event_initially_nonsignaled": True,
        "completion_routine": "NULL",
        "watch_call_directory_handle_value_uint64": handle,
        "watch_call_buffer_base_address_uint64": buffer,
        "watch_call_overlapped_address_uint64": overlapped,
        "watch_call_bytes_returned_pointer": "NULL",
        "watch_call_returned_nonzero": True,
        "initial_pending_check_api": "GetOverlappedResult",
        "initial_pending_check_directory_handle_value_uint64": handle,
        "initial_pending_check_overlapped_address_uint64": overlapped,
        "initial_pending_check_wait": False,
        "initial_pending_check_returned_nonzero": False,
        "initial_pending_check_last_error": 996,
        "initial_pending_check_bytes_transferred": 0,
        "initial_pending_check_utc": pending,
        "watch_pending": True,
        "watch_issued_utc": issued,
    }
    watch["row"] = row
    return row


def _host_runtime_anchor_remeasurement(
    state: _HostRuntimeProtectionState,
    anchor: Mapping[str, Any],
    *,
    ordinal: int,
    phase: str,
) -> dict[str, Any]:
    apis = state.apis
    acquired = anchor["row"]
    handle = anchor["handle"]
    guard = anchor["guard"]
    projection = _host_runtime_handle_projection(apis, handle)
    security = _host_runtime_security_lifecycle(apis, handle)
    if not apis["compare"](handle, guard):
        raise _windows_error("CompareObjectHandles(host-runtime path anchor)")
    observed = _orchestrator_utc()
    stable = (
        projection["resolved_path_identity"] == acquired["anchor_path_identity"]
        and projection["volume_serial_number"] == acquired["volume_serial_number"]
        and projection["file_id_128"] == acquired["file_id_128"]
        and projection["raw_file_attributes"] == acquired["raw_file_attributes"]
        and projection["reparse_tag"] == 0
        and projection["directory"] is True
    )
    if not stable:
        _refuse("host-runtime anchor identity changed while its handle was retained")
    common = {
        "ordinal": ordinal,
        "anchor_role": acquired["anchor_role"],
        "anchor_path_identity": acquired["anchor_path_identity"],
        "resolved_path_api": "GetFinalPathNameByHandleW_FILE_NAME_NORMALIZED_VOLUME_NAME_GUID",
        "resolved_path_query_handle_value_uint64": handle,
        "file_id_query_api": "GetFileInformationByHandleEx_FileIdInfo",
        "file_id_query_handle_value_uint64": handle,
        "volume_serial_number": projection["volume_serial_number"],
        "file_id_128": projection["file_id_128"],
        "file_attribute_tag_query_api": "GetFileInformationByHandleEx_FileAttributeTagInfo",
        "file_attribute_tag_query_handle_value_uint64": handle,
        "raw_file_attributes": projection["raw_file_attributes"],
        "reparse_tag": 0,
        "directory": True,
        "security_descriptor_query_lifecycle": security,
        "same_handle_retained_from_acquisition": True,
        "same_anchor_handle_value_uint64": handle,
        "same_continuity_guard_handle_value_uint64": guard,
        "handle_continuity_compare_module": "KernelBase.dll",
        "handle_continuity_compare_api": "CompareObjectHandles",
        "handle_continuity_compare_first_handle_value_uint64": handle,
        "handle_continuity_compare_second_handle_value_uint64": guard,
        "handle_continuity_compare_returned_nonzero": True,
    }
    if phase == "EPOCH":
        return {
            **common,
            "protection_epoch_remeasurement_utc": observed,
            "handle_held_at_protection_epoch_completion": True,
        }
    if phase != "RELEASE":
        _refuse("host-runtime anchor remeasurement phase differs")
    return {**common, "final_remeasurement_utc": observed}


def _host_runtime_directory_inventory_row(
    state: _HostRuntimeProtectionState,
    runtime_root: str,
    manifest_row: Mapping[str, Any],
    *,
    ordinal: int,
) -> dict[str, Any]:
    apis = state.apis
    path = _host_runtime_child(runtime_root, manifest_row["relative_path"])
    handle = apis["create"](path, 131200, 1, None, 3, 35651584, None)
    if handle in (None, _INVALID_HANDLE_VALUE):
        raise _windows_error("CreateFileW(host-runtime directory inventory)")
    handle = int(handle)
    failure: BaseException | None = None
    try:
        projection = _host_runtime_handle_projection(apis, handle)
        security = _host_runtime_security_lifecycle(apis, handle)
        dynamic = {
            "volume_serial_number": projection["volume_serial_number"],
            "file_id_128": projection["file_id_128"],
            "raw_file_attributes": projection["raw_file_attributes"],
            "reparse_tag": projection["reparse_tag"],
            "directory": projection["directory"],
            "security_information_mask": 7,
            "security_descriptor_format": "SELF_RELATIVE",
            "security_descriptor_byte_count": security["security_descriptor_byte_count"],
            "security_descriptor_sha256": security["security_descriptor_sha256"],
        }
        if (
            projection["resolved_path"] != path.rstrip("\\")
            or projection["directory"] is not True
            or projection["reparse_tag"] != 0
            or any(manifest_row[field] != value for field, value in dynamic.items())
        ):
            _refuse("host-runtime directory differs from its immutable manifest row")
    except BaseException as exc:
        failure = exc
    close_ok = bool(apis["close"](handle))
    closed = _orchestrator_utc()
    if failure is not None:
        raise failure
    if not close_ok:
        raise _windows_error("CloseHandle(host-runtime directory inventory)")
    return {
        "ordinal": ordinal,
        "manifest_row": dict(manifest_row),
        "runtime_path_identity": _private_path_identity(path.rstrip("\\")),
        "open_api": "CreateFileW",
        "desired_access": 131200,
        "share_mode": 1,
        "security_attributes": "NULL",
        "creation_disposition": 3,
        "flags_and_attributes": 35651584,
        "handle_valid": True,
        "directory_handle_value_uint64": handle,
        "resolved_path_api": "GetFinalPathNameByHandleW_FILE_NAME_NORMALIZED_VOLUME_NAME_GUID",
        "resolved_path_query_handle_value_uint64": handle,
        "resolved_path_identity": projection["resolved_path_identity"],
        "file_id_query_api": "GetFileInformationByHandleEx_FileIdInfo",
        "file_id_query_handle_value_uint64": handle,
        "volume_serial_number": projection["volume_serial_number"],
        "file_id_128": projection["file_id_128"],
        "file_attribute_tag_query_api": "GetFileInformationByHandleEx_FileAttributeTagInfo",
        "file_attribute_tag_query_handle_value_uint64": handle,
        "raw_file_attributes": projection["raw_file_attributes"],
        "reparse_tag": 0,
        "directory": True,
        "security_descriptor_query_lifecycle": security,
        "manifest_projection_reconciled": True,
        "close_api": "CloseHandle",
        "close_input_handle_value_uint64": handle,
        "close_returned_nonzero": True,
        "directory_handle_closed_utc": closed,
    }


def _host_runtime_open_file(
    state: _HostRuntimeProtectionState,
    runtime_root: str,
    manifest_row: Mapping[str, Any],
    *,
    ordinal: int,
) -> dict[str, Any]:
    apis = state.apis
    path = _host_runtime_child(runtime_root, manifest_row["relative_path"])
    handle = apis["create"](path, 0x80000000, 1, None, 3, 0x00200000, None)
    if handle in (None, _INVALID_HANDLE_VALUE):
        raise _windows_error("CreateFileW(host-runtime file lock)")
    handle = int(handle)
    file_state: dict[str, Any] = {"path": path, "handle": handle}
    state.files.append(file_state)
    projection = _host_runtime_handle_projection(apis, handle)
    if (
        projection["resolved_path"] != path.rstrip("\\")
        or projection["directory"]
        or projection["delete_pending"]
        or projection["number_of_links"] != 1
        or projection["reparse_tag"] != 0
        or projection["end_of_file"] < 0
    ):
        _refuse("host-runtime file is not an exact single-link regular file")
    raw = _host_runtime_read_handle(apis, handle, projection["end_of_file"])
    digest = hashlib.sha256(raw).hexdigest()
    if len(raw) != manifest_row["byte_count"] or digest != manifest_row["sha256"]:
        _refuse("host-runtime file bytes differ from the immutable manifest")
    acquired = _orchestrator_utc()
    row = {
        "ordinal": ordinal,
        "runtime_relative_path": manifest_row["relative_path"],
        "runtime_path_identity": _private_path_identity(path.rstrip("\\")),
        "expected_byte_count": manifest_row["byte_count"],
        "expected_sha256": manifest_row["sha256"],
        "open_api": "CreateFileW",
        "desired_access": 2147483648,
        "share_mode": 1,
        "security_attributes": "NULL",
        "creation_disposition": 3,
        "flags_and_attributes": 2097152,
        "handle_valid": True,
        "file_handle_value_uint64": handle,
        "resolved_path_api": "GetFinalPathNameByHandleW_FILE_NAME_NORMALIZED_VOLUME_NAME_GUID",
        "resolved_path_query_handle_value_uint64": handle,
        "resolved_path_identity": projection["resolved_path_identity"],
        "file_id_query_api": "GetFileInformationByHandleEx_FileIdInfo",
        "file_id_query_handle_value_uint64": handle,
        "volume_serial_number": projection["volume_serial_number"],
        "file_id_128": projection["file_id_128"],
        "file_standard_info_query_api": "GetFileInformationByHandleEx_FileStandardInfo",
        "file_standard_info_query_handle_value_uint64": handle,
        "number_of_links": 1,
        "delete_pending": False,
        "directory": False,
        "file_attribute_tag_query_api": "GetFileInformationByHandleEx_FileAttributeTagInfo",
        "file_attribute_tag_query_handle_value_uint64": handle,
        "raw_file_attributes": projection["raw_file_attributes"],
        "reparse_tag": 0,
        "read_api": "ReadFile",
        "read_input_handle_value_uint64": handle,
        "read_from_held_handle": True,
        "observed_byte_count": len(raw),
        "observed_sha256": digest,
        "lock_acquired_utc": acquired,
        "write_share_permitted": False,
        "delete_share_permitted": False,
        "handle_held_at_acquisition_completion": True,
    }
    file_state["row"] = row
    return row


def _acquire_host_runtime_protection(
    runtime_root: str,
    runtime_preimage: Mapping[str, Any],
    host_runtime_identity: Mapping[str, Any],
    *,
    public_host_alias: str,
) -> tuple[_HostRuntimeProtectionState, dict[str, Any]]:
    apis = _host_runtime_apis()
    state = _HostRuntimeProtectionState(apis)
    acquisition_started = _orchestrator_utc()
    try:
        if (
            runtime_preimage.get("schema") != "stage_f_host_validation_runtime/v1"
            or sha256_identity(
                "stage_f_host_validation_runtime/v1", dict(runtime_preimage)
            )
            != host_runtime_identity
        ):
            _refuse("host runtime preimage and identity differ")
        anchor_paths = _host_runtime_path_parts(runtime_root)
        runtime_root_identity = _private_path_identity(runtime_root.rstrip("\\"))
        if runtime_preimage["runtime_root_path_identity"] != runtime_root_identity:
            _refuse("host runtime root path differs from its immutable preimage")
        anchor_rows = [
            _host_runtime_open_anchor(
                state, path, ordinal=ordinal, count=len(anchor_paths)
            )
            for ordinal, path in enumerate(anchor_paths, start=1)
        ]
        anchor_completed = _orchestrator_utc()
        watch_rows = [
            _host_runtime_start_watch(
                state, anchor_rows, ordinal=ordinal
            )
            for ordinal in range(1, len(anchor_rows) + 1)
        ]
        all_pending = max(row["initial_pending_check_utc"] for row in watch_rows)
        event_array = (ctypes.c_void_p * len(state.watches))(
            *(watch["event"] for watch in state.watches)
        )
        ctypes.set_last_error(0)
        wait_result = int(
            apis["wait_many"](
                len(state.watches), ctypes.addressof(event_array), False, 0
            )
        )
        common_pending = _orchestrator_utc()
        if wait_result != 258:
            _refuse("host-runtime watch set is not wholly pending before launch")
        epoch_rows = [
            _host_runtime_anchor_remeasurement(
                state, anchor, ordinal=ordinal, phase="EPOCH"
            )
            for ordinal, anchor in enumerate(state.anchors, start=1)
        ]
        epoch_completed = _orchestrator_utc()
        directory_started = _orchestrator_utc()
        directory_manifest = runtime_preimage["ordered_runtime_directory_rows"]
        directory_rows = [
            _host_runtime_directory_inventory_row(
                state,
                runtime_root,
                row,
                ordinal=ordinal,
            )
            for ordinal, row in enumerate(directory_manifest, start=1)
        ]
        directory_completed = _orchestrator_utc()
        file_manifest = runtime_preimage["ordered_runtime_file_rows"]
        file_rows = [
            _host_runtime_open_file(
                state,
                runtime_root,
                row,
                ordinal=ordinal,
            )
            for ordinal, row in enumerate(file_manifest, start=1)
        ]
        file_completed = _orchestrator_utc()
        executable_path = _host_runtime_child(
            runtime_root, runtime_preimage["executable_relative_path"]
        )
        holder = _host_runtime_current_holder(
            apis, executable_path, runtime_preimage["python_executable_sha256"]
        )
        acquisition_completed = _orchestrator_utc()
        acquisition = {
            "schema": "stage_f_host_validation_runtime_lock_acquisition/v1",
            "public_host_alias": public_host_alias,
            "host_validation_runtime_identity": dict(host_runtime_identity),
            "selected_volume_root_path_identity": anchor_rows[0]["anchor_path_identity"],
            "runtime_parent_path_identity": anchor_rows[-2]["anchor_path_identity"],
            "runtime_root_path_identity": anchor_rows[-1]["anchor_path_identity"],
            "lock_holder_process": holder,
            "ordered_runtime_path_anchor_lock_rows": anchor_rows,
            "runtime_path_anchor_lock_count": len(anchor_rows),
            "path_anchor_lock_acquisition_completed_utc": anchor_completed,
            "ordered_runtime_change_watch_acquisition_rows": watch_rows,
            "runtime_change_watch_count": len(watch_rows),
            "all_runtime_change_watches_pending_utc": all_pending,
            "prelaunch_watch_set_pending_check_api": "WaitForMultipleObjects",
            "prelaunch_watch_set_pending_check_count": len(watch_rows),
            "prelaunch_watch_set_pending_check_handle_array_base_address_uint64": ctypes.addressof(event_array),
            "prelaunch_watch_set_pending_check_ordered_event_handle_values_uint64": [
                watch["event"] for watch in state.watches
            ],
            "prelaunch_watch_set_pending_check_wait_all": False,
            "prelaunch_watch_set_pending_check_milliseconds": 0,
            "prelaunch_watch_set_pending_check_result_raw": wait_result,
            "prelaunch_watch_set_pending_check_utc": common_pending,
            "protection_epoch_started_utc": common_pending,
            "ordered_path_anchor_protection_epoch_rows": epoch_rows,
            "path_anchor_protection_epoch_count": len(epoch_rows),
            "path_anchor_protection_epoch_completed_utc": epoch_completed,
            "selected_volume_root_transient_self_metadata_change_refusal_claimed": False,
            "selected_volume_root_local_principal_confidentiality_claimed": False,
            "selected_volume_root_final_identity_remeasurement_required": True,
            "controller_source_correctness_inside_operational_trust_base": True,
            "controller_internal_handle_and_io_history_independently_traced": False,
            "ordered_runtime_directory_rows": directory_rows,
            "runtime_directory_count": len(directory_rows),
            "directory_inventory_started_utc": directory_started,
            "directory_inventory_completed_utc": directory_completed,
            "ordered_runtime_file_lock_rows": file_rows,
            "runtime_file_lock_count": len(file_rows),
            "runtime_inventory_file_count": len(file_rows),
            "file_lock_acquisition_completed_utc": file_completed,
            "acquisition_started_utc": acquisition_started,
            "acquisition_completed_utc": acquisition_completed,
            "complete_runtime_inventory_projection": True,
            "ordinal_and_relative_path_order_exact": True,
            "all_expected_bytes_reconciled": True,
            "any_retained_anchor_watch_or_file_handle_released_before_completion": False,
            "scientific_counters": dict(ZERO_SCIENCE_COUNTERS),
        }
        return state, acquisition
    except BaseException:
        state.abort()
        raise


def _host_runtime_prepare_file_release(
    state: _HostRuntimeProtectionState,
    file_state: Mapping[str, Any],
    *,
    ordinal: int,
) -> dict[str, Any]:
    apis = state.apis
    acquired = file_state["row"]
    handle = file_state["handle"]
    projection = _host_runtime_handle_projection(apis, handle)
    if not apis["rewind"](handle, 0, None, 0):
        raise _windows_error("SetFilePointerEx(host-runtime final remeasurement)")
    raw = _host_runtime_read_handle(apis, handle, projection["end_of_file"])
    digest = hashlib.sha256(raw).hexdigest()
    if (
        projection["resolved_path_identity"] != acquired["runtime_path_identity"]
        or projection["volume_serial_number"] != acquired["volume_serial_number"]
        or projection["file_id_128"] != acquired["file_id_128"]
        or projection["number_of_links"] != 1
        or projection["delete_pending"]
        or projection["directory"]
        or projection["raw_file_attributes"] != acquired["raw_file_attributes"]
        or projection["reparse_tag"] != 0
        or len(raw) != acquired["expected_byte_count"]
        or digest != acquired["expected_sha256"]
    ):
        _refuse("host-runtime file changed while its lock handle was retained")
    return {
        "ordinal": ordinal,
        "runtime_relative_path": acquired["runtime_relative_path"],
        "runtime_path_identity": acquired["runtime_path_identity"],
        "same_file_handle_value_uint64": handle,
        "resolved_path_api": "GetFinalPathNameByHandleW_FILE_NAME_NORMALIZED_VOLUME_NAME_GUID",
        "resolved_path_query_handle_value_uint64": handle,
        "file_id_query_api": "GetFileInformationByHandleEx_FileIdInfo",
        "file_id_query_handle_value_uint64": handle,
        "volume_serial_number": projection["volume_serial_number"],
        "file_id_128": projection["file_id_128"],
        "file_standard_info_query_api": "GetFileInformationByHandleEx_FileStandardInfo",
        "file_standard_info_query_handle_value_uint64": handle,
        "number_of_links": 1,
        "delete_pending": False,
        "directory": False,
        "file_attribute_tag_query_api": "GetFileInformationByHandleEx_FileAttributeTagInfo",
        "file_attribute_tag_query_handle_value_uint64": handle,
        "raw_file_attributes": projection["raw_file_attributes"],
        "reparse_tag": 0,
        "same_handle_retained_from_acquisition": True,
        "rewind_api": "SetFilePointerEx",
        "rewind_input_handle_value_uint64": handle,
        "rewind_distance_to_move": 0,
        "rewind_move_method": 0,
        "rewind_returned_nonzero": True,
        "final_read_api": "ReadFile",
        "final_read_input_handle_value_uint64": handle,
        "final_read_from_held_handle": True,
        "final_observed_byte_count": len(raw),
        "final_observed_sha256": digest,
        "final_remeasurement_utc": _orchestrator_utc(),
        "close_api": "CloseHandle",
        "close_input_handle_value_uint64": handle,
    }


def _host_runtime_release_watch(
    state: _HostRuntimeProtectionState,
    watch: dict[str, Any],
    *,
    ordinal: int,
) -> dict[str, Any]:
    apis = state.apis
    acquired = watch["row"]
    handle = watch["handle"]
    event = watch["event"]
    overlapped = watch["overlapped"]
    buffer = watch["buffer"]
    transferred = ctypes.c_uint32(0)
    ctypes.set_last_error(0)
    completed = bool(
        apis["get_overlapped"](
            handle, overlapped, ctypes.byref(transferred), False
        )
    )
    error = 0 if completed else ctypes.get_last_error()
    pre_cancel = _orchestrator_utc()
    if completed or error != 996 or transferred.value != 0:
        _refuse("host-runtime watch observed a change before final cancellation")
    ctypes.set_last_error(0)
    if not apis["cancel"](handle, overlapped):
        raise _windows_error("CancelIoEx(host-runtime change watch)")
    transferred.value = 0
    ctypes.set_last_error(0)
    completed = bool(
        apis["get_overlapped"](
            handle, overlapped, ctypes.byref(transferred), True
        )
    )
    error = 0 if completed else ctypes.get_last_error()
    cancelled = _orchestrator_utc()
    if completed or error != 995 or transferred.value != 0:
        _refuse(
            "host-runtime watch cancellation did not complete with "
            "ERROR_OPERATION_ABORTED and zero bytes"
        )
    watch["cancelled"] = True
    unchanged = hashlib.sha256(ctypes.string_at(buffer, 65536)).hexdigest()
    buffer_hashed = _orchestrator_utc()
    if unchanged != hashlib.sha256(bytes(65536)).hexdigest():
        _refuse("host-runtime change-watch buffer is not unchanged zero storage")
    close_directory = bool(apis["close"](handle))
    directory_closed = _orchestrator_utc()
    watch["handle"] = 0
    close_event = bool(apis["close"](event))
    event_closed = _orchestrator_utc()
    watch["event"] = 0
    free_overlapped = bool(apis["virtual_free"](overlapped, 0, 0x8000))
    overlapped_released = _orchestrator_utc()
    watch["overlapped"] = 0
    free_buffer = bool(apis["virtual_free"](buffer, 0, 0x8000))
    buffer_released = _orchestrator_utc()
    watch["buffer"] = 0
    if not all((close_directory, close_event, free_overlapped, free_buffer)):
        _refuse("host-runtime watch resource release failed")
    released = max(
        directory_closed, event_closed, overlapped_released, buffer_released
    )
    return {
        "schema": "stage_f_host_validation_runtime_tree_watch_release/v1",
        "ordinal": ordinal,
        "watch_role": acquired["watch_role"],
        "protected_anchor_ordinal": acquired["protected_anchor_ordinal"],
        "watched_anchor_ordinal": acquired["watched_anchor_ordinal"],
        "runtime_root_path_identity": acquired["runtime_root_path_identity"],
        "watched_directory_path_identity": acquired["watched_directory_path_identity"],
        "watch_subtree": acquired["watch_subtree"],
        "volume_serial_number": acquired["volume_serial_number"],
        "file_id_128": acquired["file_id_128"],
        "same_handle_retained_from_acquisition": True,
        "same_directory_handle_value_uint64": handle,
        "same_overlapped_structure": True,
        "same_overlapped_address_uint64": overlapped,
        "same_event_handle": True,
        "same_event_handle_value_uint64": event,
        "same_buffer_base_address_uint64": buffer,
        "buffer_exclusively_retained_until_cancel_completion": True,
        "buffer_not_freed_or_reused_before_cancel_completion": True,
        "overlapped_storage_not_freed_or_reused_before_cancel_completion": True,
        "watch_held_before_inventory_through_all_validator_returns": True,
        "pre_cancel_result_api": "GetOverlappedResult",
        "pre_cancel_directory_handle_value_uint64": handle,
        "pre_cancel_overlapped_address_uint64": overlapped,
        "pre_cancel_result_returned_nonzero": False,
        "pre_cancel_wait": False,
        "pre_cancel_last_error": 996,
        "pre_cancel_bytes_transferred": 0,
        "pre_cancel_check_utc": pre_cancel,
        "file_notify_record_count": 0,
        "buffer_overflow_observed": False,
        "cancel_api": "CancelIoEx",
        "cancel_directory_handle_value_uint64": handle,
        "cancel_overlapped_address_uint64": overlapped,
        "cancel_returned_nonzero": True,
        "cancel_completion_api": "GetOverlappedResult",
        "cancel_completion_directory_handle_value_uint64": handle,
        "cancel_completion_overlapped_address_uint64": overlapped,
        "cancel_completion_wait": True,
        "cancel_completion_returned_nonzero": False,
        "cancel_completion_last_error": 995,
        "cancel_completion_bytes_transferred": 0,
        "cancel_completed_utc": cancelled,
        "close_api": "CloseHandle",
        "close_input_directory_handle_value_uint64": handle,
        "close_returned_nonzero": True,
        "directory_handle_closed_utc": directory_closed,
        "event_close_api": "CloseHandle",
        "event_close_input_handle_value_uint64": event,
        "event_close_returned_nonzero": True,
        "event_handle_closed_utc": event_closed,
        "overlapped_storage_release_api": "VirtualFree",
        "overlapped_storage_release_size": 0,
        "overlapped_storage_release_type": 32768,
        "overlapped_storage_release_returned_nonzero": True,
        "overlapped_storage_release_base_address_uint64": overlapped,
        "overlapped_storage_released_utc": overlapped_released,
        "unchanged_buffer_sha256": unchanged,
        "buffer_hash_input_address_uint64": buffer,
        "buffer_hash_byte_count": 65536,
        "buffer_hash_observed_utc": buffer_hashed,
        "buffer_release_api": "VirtualFree",
        "buffer_release_size": 0,
        "buffer_release_type": 32768,
        "buffer_release_base_address_uint64": buffer,
        "buffer_release_returned_nonzero": True,
        "buffer_released_utc": buffer_released,
        "watch_released_utc": released,
    }


def _release_host_runtime_protection(
    state: _HostRuntimeProtectionState,
    acquisition: Mapping[str, Any],
    *,
    locked_process_rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    if state.released:
        _refuse("host-runtime protection resources were already released")
    if len(locked_process_rows) != 3:
        _refuse("host-runtime release requires exactly three locked processes")
    last_returned = max(row["process_returned_utc"] for row in locked_process_rows)
    release_started = _orchestrator_utc()
    if _utc(release_started, "host-runtime release start") < _utc(
        last_returned, "last locked process return"
    ):
        _refuse("host-runtime release began before a validator returned")
    try:
        anchor_rows = [
            _host_runtime_anchor_remeasurement(
                state, anchor, ordinal=ordinal, phase="RELEASE"
            )
            for ordinal, anchor in enumerate(state.anchors, start=1)
        ]
        file_rows = [
            _host_runtime_prepare_file_release(
                state, file_state, ordinal=ordinal
            )
            for ordinal, file_state in enumerate(state.files, start=1)
        ]
        watch_rows = [
            _host_runtime_release_watch(state, watch, ordinal=ordinal)
            for ordinal, watch in enumerate(state.watches, start=1)
        ]
        all_watches_released = max(row["watch_released_utc"] for row in watch_rows)
        for file_state, row in zip(state.files, file_rows, strict=True):
            handle = file_state["handle"]
            if not state.apis["close"](handle):
                raise _windows_error("CloseHandle(host-runtime file release)")
            file_state["handle"] = 0
            row["close_returned_nonzero"] = True
            row["lock_released_utc"] = _orchestrator_utc()
        for anchor, row in zip(state.anchors, anchor_rows, strict=True):
            handle = anchor["handle"]
            guard = anchor["guard"]
            if not state.apis["close"](handle):
                raise _windows_error("CloseHandle(host-runtime anchor release)")
            anchor_closed = _orchestrator_utc()
            anchor["handle"] = 0
            if not state.apis["close"](guard):
                raise _windows_error("CloseHandle(host-runtime anchor guard release)")
            guard_closed = _orchestrator_utc()
            anchor["guard"] = 0
            row.update(
                {
                    "close_api": "CloseHandle",
                    "close_input_handle_value_uint64": handle,
                    "close_returned_nonzero": True,
                    "anchor_handle_closed_utc": anchor_closed,
                    "continuity_guard_close_api": "CloseHandle",
                    "continuity_guard_close_input_handle_value_uint64": guard,
                    "continuity_guard_close_returned_nonzero": True,
                    "continuity_guard_released_utc": guard_closed,
                    "lock_released_utc": max(anchor_closed, guard_closed),
                }
            )
        release_completed = _orchestrator_utc()
        state.released = True
        holder = acquisition["lock_holder_process"]
        return {
            "schema": "stage_f_host_validation_runtime_lock_release/v1",
            "host_runtime_lock_acquisition_sha256": hashlib.sha256(
                canonical_bytes(acquisition)
            ).hexdigest(),
            "lock_holder_process_id": holder["process_id"],
            "lock_holder_process_creation_filetime_uint64": holder[
                "process_creation_filetime_uint64"
            ],
            "lock_holder_process_identity_equals_acquisition": True,
            "locked_validator_processes": [dict(row) for row in locked_process_rows],
            "last_validator_process_returned_utc": last_returned,
            "protection_epoch_ended_utc": last_returned,
            "release_started_utc": release_started,
            "ordered_runtime_change_watch_release_rows": watch_rows,
            "runtime_change_watch_release_count": len(watch_rows),
            "all_runtime_change_watches_released_utc": all_watches_released,
            "ordered_runtime_path_anchor_release_rows": anchor_rows,
            "runtime_path_anchor_release_count": len(anchor_rows),
            "ordered_runtime_file_release_rows": file_rows,
            "runtime_file_release_count": len(file_rows),
            "release_completed_utc": release_completed,
            "any_retained_anchor_watch_or_file_handle_released_before_all_validator_processes_returned": False,
            "complete_acquisition_projection_remeasured": True,
            "all_handles_closed_once": True,
            "scientific_counters": dict(ZERO_SCIENCE_COUNTERS),
        }
    except BaseException:
        state.abort()
        raise


_HOST_RUNTIME_CONTROLLER_PLAN_FIELDS = frozenset(
    {
        "public_host_alias",
        "runtime_root",
        "host_validation_runtime_preimage",
        "host_validation_runtime_identity",
        "binding_validator_identity",
        "execution_environment_policy_identity",
        "bootstrap_source_utf8",
        "validator_zipapp_path",
        "orchestrator_invocation_path",
        "authority_schema_source_path",
    }
)


def _host_runtime_orchestrator_invocation(
    plan: Mapping[str, Any], acquisition_sha256: str
) -> tuple[dict[str, Any], list[str]]:
    runtime = plan["host_validation_runtime_preimage"]
    executable = _host_runtime_child(
        plan["runtime_root"], runtime["executable_relative_path"]
    )
    bootstrap = plan["bootstrap_source_utf8"]
    zipapp_path = plan["validator_zipapp_path"]
    invocation_path = plan["orchestrator_invocation_path"]
    zipapp_raw = Path(zipapp_path).read_bytes()
    arguments = [
        "--validator-zipapp",
        zipapp_path,
        "--validator-zipapp-byte-count",
        str(len(zipapp_raw)),
        "--validator-zipapp-sha256",
        hashlib.sha256(zipapp_raw).hexdigest(),
        "--host-runtime-lock-acquisition-sha256",
        acquisition_sha256,
        "--durability-probe-phase",
        "ORCHESTRATOR",
        "--invocation-preimage",
        invocation_path,
    ]
    vector = [
        executable,
        "-I",
        "-S",
        "-B",
        "-c",
        bootstrap.decode("utf-8", "strict"),
        *arguments,
    ]
    command_raw = subprocess.list2cmdline(vector).encode("utf-16le", "strict")
    git_framed = b"blob " + str(len(bootstrap)).encode("ascii") + b"\0" + bootstrap
    invocation = {
        "schema": "stage_f_durability_probe_invocation/v1",
        "phase": "ORCHESTRATOR",
        "binding_validator_identity": dict(plan["binding_validator_identity"]),
        "execution_environment_policy_identity": dict(
            plan["execution_environment_policy_identity"]
        ),
        "host_validation_runtime_identity": dict(
            plan["host_validation_runtime_identity"]
        ),
        "host_runtime_lock_acquisition_sha256": acquisition_sha256,
        "bootstrap_source_path": "stage_f_binding/locked_zipapp_bootstrap.py",
        "bootstrap_git_row": {
            "path": "stage_f_binding/locked_zipapp_bootstrap.py",
            "mode": "100644",
            "git_object": hashlib.sha1(git_framed).hexdigest(),
            "byte_count": len(bootstrap),
            "raw_sha256": hashlib.sha256(bootstrap).hexdigest(),
        },
        "bootstrap_source_byte_count": len(bootstrap),
        "bootstrap_source_utf8_base64": base64.b64encode(bootstrap).decode("ascii"),
        "executable_path_identity": _private_path_identity(executable),
        "validator_zipapp_path_identity": _private_path_identity(zipapp_path),
        "validator_zipapp_byte_count": len(zipapp_raw),
        "validator_zipapp_sha256": hashlib.sha256(zipapp_raw).hexdigest(),
        "invocation_preimage_path_identity": _private_path_identity(invocation_path),
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
    return invocation, vector


def _controller_launch_orchestrator(
    executable: str, vector: Sequence[str]
) -> dict[str, Any]:
    if sys.platform != "win32" or ctypes.sizeof(ctypes.c_void_p) != 8:
        _refuse("host-runtime controller launch requires 64-bit Win32")
    command = subprocess.list2cmdline(list(vector))
    command_buffer = ctypes.create_unicode_buffer(command)
    startup = _ORCH_STARTUPINFOW()
    startup.cb = ctypes.sizeof(startup)
    process = _ORCH_PROCESS_INFORMATION()
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    create = kernel32.CreateProcessW
    create.argtypes = (
        ctypes.c_wchar_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_int,
        ctypes.c_uint32,
        ctypes.c_void_p,
        ctypes.c_wchar_p,
        ctypes.POINTER(_ORCH_STARTUPINFOW),
        ctypes.POINTER(_ORCH_PROCESS_INFORMATION),
    )
    create.restype = ctypes.c_int
    close = kernel32.CloseHandle
    close.argtypes = (ctypes.c_void_p,)
    close.restype = ctypes.c_int
    wait = kernel32.WaitForSingleObject
    wait.argtypes = (ctypes.c_void_p, ctypes.c_uint32)
    wait.restype = ctypes.c_uint32
    get_exit = kernel32.GetExitCodeProcess
    get_exit.argtypes = (ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint32))
    get_exit.restype = ctypes.c_int
    get_times = kernel32.GetProcessTimes
    get_times.argtypes = (
        ctypes.c_void_p,
        ctypes.POINTER(_ORCH_FILETIME),
        ctypes.POINTER(_ORCH_FILETIME),
        ctypes.POINTER(_ORCH_FILETIME),
        ctypes.POINTER(_ORCH_FILETIME),
    )
    get_times.restype = ctypes.c_int
    if not create(
        executable,
        ctypes.addressof(command_buffer),
        None,
        None,
        False,
        0,
        None,
        None,
        ctypes.byref(startup),
        ctypes.byref(process),
    ):
        raise _windows_error("CreateProcessW(host-runtime ORCHESTRATOR)")
    process_handle = int(process.hProcess)
    thread_handle = int(process.hThread)
    if not close(thread_handle):
        close(process_handle)
        raise _windows_error("CloseHandle(host-runtime ORCHESTRATOR thread)")
    wait_result = int(wait(process_handle, _UINT32_MAX))
    returned = _orchestrator_utc()
    if wait_result != 0:
        close(process_handle)
        _refuse("host-runtime ORCHESTRATOR wait did not return WAIT_OBJECT_0")
    exit_code = ctypes.c_uint32(0)
    creation, exit_time, kernel_time, user_time = (_ORCH_FILETIME() for _ in range(4))
    if not get_exit(process_handle, ctypes.byref(exit_code)) or not get_times(
        process_handle,
        ctypes.byref(creation),
        ctypes.byref(exit_time),
        ctypes.byref(kernel_time),
        ctypes.byref(user_time),
    ):
        close(process_handle)
        raise _windows_error("query host-runtime ORCHESTRATOR process")
    if not close(process_handle):
        raise _windows_error("CloseHandle(host-runtime ORCHESTRATOR process)")
    if exit_code.value != 0:
        _refuse(f"locked ORCHESTRATOR returned {exit_code.value}")
    return {
        "process_id": int(process.dwProcessId),
        "process_creation_filetime_uint64": _filetime_uint64(creation),
        "process_returned_utc": returned,
        "exit_code": int(exit_code.value),
    }


def _controller_write_fresh(path: Path, raw: bytes) -> None:
    if not raw:
        _refuse("host-runtime controller companion is empty")
    _write_temporary(raw, path)
    if path.read_bytes() != raw:
        _refuse("host-runtime controller companion did not reread byte-exactly")


def execute_host_runtime_composite_controller(
    plan: Mapping[str, Any],
) -> dict[str, Any]:
    """Execute the outcome-blind outer durability route and stop before science.

    The caller supplies only committed identities/material locations and one
    immutable runtime preimage.  This process owns every runtime lock and
    asynchronous watch across ORCHESTRATOR, PRE_RESTART, and POST_RESTART,
    validates both acquisition and release against the committed schema, and
    emits the exact inputs needed to construct the final durability receipt.
    It has no scientific callback or post-durability launch facility.
    """

    plan = _mapping(plan, "host-runtime composite-controller plan")
    _exact_fields(
        plan, _HOST_RUNTIME_CONTROLLER_PLAN_FIELDS, "host-runtime controller plan"
    )
    validate_no_science_counters(dict(ZERO_SCIENCE_COUNTERS))
    bootstrap = plan["bootstrap_source_utf8"]
    if type(bootstrap) is not bytes or not 0 < len(bootstrap) <= 8192:
        _refuse("host-runtime controller bootstrap is not one to 8192 exact bytes")
    runtime_root = plan["runtime_root"]
    anchor_paths = _host_runtime_path_parts(runtime_root)
    invocation_path = plan["orchestrator_invocation_path"]
    if (
        not isinstance(invocation_path, str)
        or not invocation_path.startswith("\\\\?\\Volume{")
        or invocation_path.casefold().startswith(runtime_root.rstrip("\\").casefold() + "\\")
        or not invocation_path.endswith(".orchestrator-invocation.json")
    ):
        _refuse("ORCHESTRATOR invocation path is not an external volume-GUID result path")
    for field in ("validator_zipapp_path", "authority_schema_source_path"):
        value = plan[field]
        if not isinstance(value, str) or not value.startswith("\\\\?\\Volume{"):
            _refuse(f"host-runtime controller {field} is not a volume-GUID path")
    runtime = _mapping(
        plan["host_validation_runtime_preimage"], "host-validation runtime preimage"
    )
    schema_raw = Path(plan["authority_schema_source_path"]).read_bytes()
    schema = strict_loads(schema_raw)
    if type(schema) is not dict:
        _refuse("host-runtime controller authority schema is not an object")
    # Local import avoids a module cycle during the locked validator entry.
    from .binding import ClosedSchemaValidator

    schema_validator = ClosedSchemaValidator(schema)
    schema_validator.validate_definition("host_validation_runtime_preimage", runtime)
    schema_validator.validate_definition(
        "host_validation_runtime_identity", plan["host_validation_runtime_identity"]
    )
    schema_validator.validate_definition(
        "binding_validator_identity", plan["binding_validator_identity"]
    )
    schema_validator.validate_definition(
        "environment_policy_identity",
        plan["execution_environment_policy_identity"],
    )
    if len(anchor_paths) < 2:
        _refuse("host-runtime controller requires at least two path anchors")
    state, acquisition = _acquire_host_runtime_protection(
        runtime_root,
        runtime,
        plan["host_validation_runtime_identity"],
        public_host_alias=plan["public_host_alias"],
    )
    try:
        schema_validator.validate_definition(
            "host_runtime_lock_acquisition_preimage", acquisition
        )
        acquisition_sha = hashlib.sha256(canonical_bytes(acquisition)).hexdigest()
        invocation, vector = _host_runtime_orchestrator_invocation(
            plan, acquisition_sha
        )
        schema_validator.validate_definition(
            "durability_probe_invocation_preimage", invocation
        )
        invocation_file = Path(invocation_path)
        acquisition_file = Path(
            invocation_path + ".host-runtime-lock-acquisition.json"
        )
        schema_file = Path(invocation_path + ".authority-schema.json")
        _controller_write_fresh(schema_file, schema_raw)
        _controller_write_fresh(acquisition_file, canonical_bytes(acquisition))
        _controller_write_fresh(invocation_file, canonical_bytes(invocation))
        executable = _host_runtime_child(
            runtime_root, runtime["executable_relative_path"]
        )
        outer_process = _controller_launch_orchestrator(executable, vector)
        parent, token = _probe_prefix(invocation_file, "ORCHESTRATOR")
        evidence_file = parent / f"{token}.orchestrator-evidence.json"
        bootstrap_file = Path(invocation_path + ".bootstrap-lock.json")
        evidence = _read_canonical_probe_evidence(evidence_file)
        orchestrator_process = evidence.get("orchestrator_process")
        if not isinstance(orchestrator_process, dict) or (
            orchestrator_process.get("process_id"),
            orchestrator_process.get("creation_filetime_uint64"),
        ) != (
            outer_process["process_id"],
            outer_process["process_creation_filetime_uint64"],
        ):
            _refuse("ORCHESTRATOR process evidence differs from retained process queries")
        orchestrator_lock = _artifact_lock_from_raw(
            _read_canonical_probe_evidence(bootstrap_file),
            role="ORCHESTRATOR_PROCESS",
            process=orchestrator_process,
            invocation=invocation,
        )
        restart = evidence["restart_observation"]
        processes = [
            orchestrator_process,
            restart["terminated_process"],
            restart["resumed_process"],
        ]
        invocations = [
            invocation,
            evidence["terminated_invocation_preimage"],
            evidence["resumed_invocation_preimage"],
        ]
        process_rows = [
            {
                "phase": "ORCHESTRATOR",
                "process_id": orchestrator_process["process_id"],
                "process_creation_filetime_uint64": orchestrator_process[
                    "creation_filetime_uint64"
                ],
                "invocation_sha256": hashlib.sha256(
                    canonical_bytes(invocation)
                ).hexdigest(),
                "process_returned_utc": outer_process["process_returned_utc"],
                "exit_code": 0,
            },
            {
                "phase": "PRE_RESTART",
                "process_id": restart["terminated_process"]["process_id"],
                "process_creation_filetime_uint64": restart["terminated_process"][
                    "creation_filetime_uint64"
                ],
                "invocation_sha256": hashlib.sha256(
                    canonical_bytes(invocations[1])
                ).hexdigest(),
                "process_returned_utc": restart["terminated_wait_completed_utc"],
                "exit_code": restart["terminated_process_exit_code"],
            },
            {
                "phase": "POST_RESTART",
                "process_id": restart["resumed_process"]["process_id"],
                "process_creation_filetime_uint64": restart["resumed_process"][
                    "creation_filetime_uint64"
                ],
                "invocation_sha256": hashlib.sha256(
                    canonical_bytes(invocations[2])
                ).hexdigest(),
                "process_returned_utc": restart["resumed_wait_completed_utc"],
                "exit_code": restart["resumed_process_exit_code"],
            },
        ]
        _validate_host_runtime_inventory(
            acquisition, runtime, processes=processes
        )
        release = _release_host_runtime_protection(
            state, acquisition, locked_process_rows=process_rows
        )
        schema_validator.validate_definition(
            "host_runtime_lock_release_observation", release
        )
        _validate_host_runtime_lock_release(
            acquisition, release, processes=processes, invocations=invocations
        )
        receipt_inputs = {
            "schema": "stage_f_durability_receipt_inputs/v1",
            "host_validation_runtime_preimage": dict(runtime),
            "host_runtime_lock_acquisition_preimage": acquisition,
            "host_runtime_lock_acquisition_sha256": acquisition_sha,
            "host_runtime_lock_release_observation": release,
            "orchestrator_probe_invocation_preimage": invocation,
            "terminated_probe_invocation_preimage": invocations[1],
            "resumed_probe_invocation_preimage": invocations[2],
            "orchestrator_artifact_lock_observation": orchestrator_lock,
            "terminated_artifact_lock_observation": evidence[
                "terminated_artifact_lock_observation"
            ],
            "resumed_artifact_lock_observation": evidence[
                "resumed_artifact_lock_observation"
            ],
            "execution_evidence": evidence,
            "ordered_actions": evidence["ordered_actions"],
            "action_count": evidence["action_count"],
            "scientific_counters": dict(ZERO_SCIENCE_COUNTERS),
        }
        release_file = Path(invocation_path + ".host-runtime-lock-release.json")
        inputs_file = Path(invocation_path + ".durability-receipt-inputs.json")
        _controller_write_fresh(release_file, canonical_bytes(release))
        _controller_write_fresh(inputs_file, canonical_bytes(receipt_inputs))
        return {
            "host_runtime_lock_acquisition_preimage": acquisition,
            "host_runtime_lock_release_observation": release,
            "orchestrator_invocation_preimage": invocation,
            "orchestrator_artifact_lock_observation": orchestrator_lock,
            "durability_receipt_inputs": receipt_inputs,
            "acquisition_path": os.fspath(acquisition_file),
            "release_path": os.fspath(release_file),
            "receipt_inputs_path": os.fspath(inputs_file),
            "scientific_counters": dict(ZERO_SCIENCE_COUNTERS),
            "disposition": "DURABILITY_COMPLETE_SCIENCE_NOT_AUTHORIZED",
        }
    except BaseException:
        state.abort()
        raise
