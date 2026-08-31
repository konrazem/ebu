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
from datetime import datetime, timedelta, timezone
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
    "validate_stage_f_control_state_machine",
    "execute_stage_f_prestart_controller",
    "execute_stage_f_live_prestart_controller",
    "StageFPrestartControllerSession",
    "WindowsStageFPrestartBackend",
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

# These are implementation-control records, not scientific records.  The
# chronological index is deliberately a sequence rather than a mapping: the
# same USN/ledger definitions occur repeatedly and their ordering is evidence.
_CONTROL_ROW_FIELDS = frozenset(("definition", "record"))
_CONTROL_SINGLETON_DEFINITIONS = frozenset(
    (
        "stage_f_execution_attempt_genesis",
        "stage_f_root_protection_epoch",
        "stage_f_evidence_ledger_genesis",
        "stage_f_capacity_publication_observation",
        "stage_f_capacity_consumption_closure",
        "stage_f_scientific_launch_gate",
        "stage_f_container_start_intent",
        "stage_f_container_start_receipt",
        "stage_f_root_protection_release",
    )
)
_CONTROL_ALLOWED_DEFINITIONS = frozenset(
    set(_CONTROL_SINGLETON_DEFINITIONS)
    | {
        "binding_validation_receipt",
        "binding_readiness_record",
        "independent_binding_audit_receipt",
        "sealed_campaign_packet_manifest",
        "post_packet_user_authorization_receipt",
        "campaign_authorization",
        "stage_f_authorized_mutation_ticket",
        "stage_f_ledger_append_ticket",
        "stage_f_evidence_ledger_entry",
        "stage_f_evidence_ledger_append_observation",
        "stage_f_usn_journal_range",
        "stage_f_lid_open_statement_receipt",
        "ntfs_directory_allocation_observation",
        "docker_runtime_identity_observation",
        "docker_engine_request_observation",
        "controller_session_observation",
    }
)
_CONTROL_NESTED_ONLY_DEFINITIONS = frozenset(
    (
        "stage_f_host_prerequisite_snapshot",
        "stage_f_scientific_launch_handoff",
        "stage_f_ledger_create_observation",
        "stage_f_capacity_live_gate",
        "stage_f_raw_volume_capacity_observation",
        "stage_f_inert_container_observation",
        "stage_f_container_start_capability",
        "stage_f_root_watch_live_state",
    )
)
_LEDGER_FIXED_ZERO_HASHES = MappingProxyType(
    {
        4: hashlib.sha256(bytes(4)).hexdigest(),
        8: hashlib.sha256(bytes(8)).hexdigest(),
        24: hashlib.sha256(bytes(24)).hexdigest(),
    }
)

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
    actor_process_id actor_process_creation_filetime_uint64 actor_thread_id
    operations_serialized source_guard_handle_value_uint64
    source_guard_retained_across_move pre_move_guard_observation
    post_move_guard_observation post_move_guard_flush_api
    post_move_guard_flush_handle_value_uint64 post_move_guard_flush_returned_nonzero
    final_open_desired_access final_open_share_mode final_open_creation_disposition
    final_open_flags_and_attributes final_handle_observation
    source_and_final_same_volume_file_id_byte_count_and_sha256
    parent_watch_observation independent_final_open_compared_by_compare_object_handles
    final_and_guard_stable_volume_file_id_attributes_byte_count_and_sha256
    final_handle_close_api final_handle_close_input_handle_value_uint64
    final_handle_close_returned_nonzero final_handle_closed_utc
    duplicate_guard_retained_until_transaction_sealed final_open_api
    final_open_security_attributes final_open_handle_value_uint64
    final_open_returned_valid
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
    canonical_volume_guid_application_path_identity lp_application_name_representation
    command_argv0_representation created_suspended process_image_attestation
    image_attestation_completed_before_resume resume_api
    resume_input_thread_handle_value_uint64 resume_returned_previous_suspend_count
    resume_succeeded resumed_utc thread_close_after_resume refusal_before_user_code
    pre_resume_launch_attestation_sha256 host_validation_process_resume_capability_identity
    capacity_live_gate_identity launch_attestation_capability_gate_and_resume_recomputed
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


def _raw_image(
    record: Mapping[str, Any],
    bytes_field: str,
    sha_field: str,
    label: str,
    *,
    expected_size: int | None = None,
    require_zero: bool = False,
    allow_empty: bool = False,
) -> bytes:
    if allow_empty and record[bytes_field] == "":
        raw = b""
    else:
        raw = _strict_base64(record[bytes_field], f"{label} bytes")
    if expected_size is not None and len(raw) != expected_size:
        _refuse(f"{label} byte count differs")
    if require_zero and raw != bytes(len(raw)):
        _refuse(f"{label} is not the exact zero preimage")
    if hashlib.sha256(raw).hexdigest() != _sha256(record[sha_field], f"{label} SHA-256"):
        _refuse(f"{label} SHA-256 differs")
    return raw


def _embedded_record_identity(
    record: Mapping[str, Any], digest_field: str, *, kind: str | None = None
) -> dict[str, str]:
    identity = verify_embedded_digest(record, digest_field, kind=kind)
    if identity["value"] != record[digest_field]:
        _refuse(f"{digest_field} does not form the embedded record identity")
    return identity


def _validate_science_counters_recursively(value: Any, label: str) -> None:
    if type(value) is dict:
        for key, child in value.items():
            if key in ("scientific_counters", "scientific_counters_before_start"):
                validate_no_science_counters(_mapping(child, f"{label}.{key}"))
            else:
                _validate_science_counters_recursively(child, f"{label}.{key}")
    elif type(value) is list:
        for ordinal, child in enumerate(value, 1):
            _validate_science_counters_recursively(child, f"{label}[{ordinal}]")


def _validate_usn_record_projection(record_value: Any, label: str) -> None:
    record = _mapping(record_value, label)
    raw_record = _raw_image(record, "raw_record_bytes_base64", "raw_record_sha256", label)
    if len(raw_record) != _uint(record["record_length"], 32, f"{label}.record_length", positive=True):
        _refuse(f"{label} raw record length differs")
    major = _uint(record["major_version"], 16, f"{label}.major_version")
    if major == 2:
        width, reference_bytes = 64, 8
    elif major == 3:
        width, reference_bytes = 128, 16
    else:
        _refuse(f"{label} is not a USN_RECORD_V2 or USN_RECORD_V3")
    if record["record_version"] != major or record["minor_version"] != 0:
        _refuse(f"{label} version projection differs")
    if record["file_reference_width_bits"] != width:
        _refuse(f"{label} file-reference width differs")
    child = _strict_base64(record["file_reference_raw_bytes_base64"], f"{label} file reference")
    parent = _strict_base64(record["parent_file_reference_raw_bytes_base64"], f"{label} parent file reference")
    if len(child) != reference_bytes or len(parent) != reference_bytes:
        _refuse(f"{label} raw file-reference width differs")
    child_canonical = (child + bytes(8) if major == 2 else child).hex()
    parent_canonical = (parent + bytes(8) if major == 2 else parent).hex()
    if (
        record["file_reference_number"] != child_canonical
        or record["parent_file_reference_number"] != parent_canonical
        or not record["file_reference_normalization_recomputed_from_raw_bytes"]
        or not record["parent_file_reference_normalization_recomputed_from_raw_bytes"]
    ):
        _refuse(f"{label} file-reference canonicalization differs")
    expected_rule = (
        "V2_RAW_LE_8_PLUS_8_ZERO_BYTES_TO_LOWER_HEX_16_BYTES"
        if major == 2
        else "V3_RAW_LE_16_BYTES_TO_LOWER_HEX_16_BYTES"
    )
    if record["file_reference_normalization"] != expected_rule:
        _refuse(f"{label} file-reference normalization rule differs")
    if not record["strict_projection_exact"]:
        _refuse(f"{label} does not assert an exact raw projection")
    name_raw = _strict_base64(record["file_name_utf16le_base64"], f"{label} name")
    if len(name_raw) != record["file_name_length_bytes"] or len(name_raw) % 2:
        _refuse(f"{label} file-name byte count differs")
    try:
        name = name_raw.decode("utf-16le", "strict")
    except UnicodeDecodeError as exc:
        raise BindingRefusal(f"{label} file name is not strict UTF-16LE") from exc
    if name != record["file_name"]:
        _refuse(f"{label} file-name projection differs")
    if record["scope_disposition"] == "AUTHORIZED_TICKET_MATCH":
        if record["protected_identity_match_count"] != 1:
            _refuse(f"{label} protected identity does not match exactly once")
        if record["mutation_ticket_identity"] is None or record["mutation_ticket_match_count"] != 1:
            _refuse(f"{label} protected record lacks one authorized ticket")
        if (
            not isinstance(record.get("mutation_transaction_identity"), Mapping)
            or not isinstance(record.get("ledger_mutation_entry_identity"), Mapping)
        ):
            _refuse(f"{label} authorized record lacks transaction/ledger joins")
        _identity(
            record["ledger_mutation_entry_identity"],
            "stage_f_evidence_ledger/v1",
            f"{label} ledger mutation entry",
        )
    elif record["scope_disposition"] == "OUTSIDE_PROTECTED_SCOPE":
        if (
            record["protected_identity_match_count"] != 0
            or record["mutation_ticket_identity"] is not None
            or record["mutation_ticket_match_count"] != 0
            or record.get("mutation_transaction_identity") is not None
            or record.get("ledger_mutation_entry_identity") is not None
        ):
            _refuse(f"{label} outside-scope record carries a protected match")
    else:
        _refuse(f"{label} scope disposition differs")


def _validate_usn_range(record_value: Any, label: str) -> None:
    record = _mapping(record_value, label)
    if record["journal_id_unchanged"] is not True or record["range_complete"] is not True:
        _refuse(f"{label} does not close one unchanged USN journal range")
    if record["wrapped_or_gapped"] or record["unknown_record_count"] or record["access_errors"] != 0:
        _refuse(f"{label} reports a journal gap, unknown record, or access error")
    records = record["records"]
    if type(records) is not list or record["record_count"] != len(records):
        _refuse(f"{label} record count differs")
    for ordinal, item in enumerate(records, 1):
        _validate_usn_record_projection(item, f"{label}.records[{ordinal}]")
    protected = sum(
        1
        for item in records
        if item["scope_disposition"] == "AUTHORIZED_TICKET_MATCH"
    )
    if (
        record["protected_ticket_match_count"] != protected
        or record["outside_scope_record_count"] != len(records) - protected
        or record["refused_protected_record_count"] != 0
        or not record["raw_buffers_partition_into_records_exactly"]
        or record.get("ticket_watch_usn_ledger_bijection_recomputed") is not True
    ):
        _refuse(f"{label} raw partition or ticket/scope counts differ")


def _validate_mutation_ticket_semantics(record_value: Any, label: str) -> None:
    record = _mapping(record_value, label)
    verify_embedded_digest(
        record, "ticket_sha256", kind="stage_f_authorized_mutation_ticket/v1"
    )
    issued = _utc(record["issued_utc"], f"{label}.issued_utc")
    expires = _utc(record["expires_utc"], f"{label}.expires_utc")
    if issued >= expires or record.get("single_use_required") is not True:
        _refuse(f"{label} interval or single-use predicate differs")
    if record.get("ticket_watch_usn_ledger_join_kind") != (
        "ROOT_EPOCH_TRANSACTION_TICKET_WATCH_USN_LEDGER_BIJECTION"
    ):
        _refuse(f"{label} watch/USN/ledger join kind differs")
    _identity(
        record.get("root_protection_epoch_identity"),
        "stage_f_root_protection_epoch/v1",
        f"{label}.root_protection_epoch_identity",
    )
    if not isinstance(record.get("ledger_mutation_transaction_identity"), Mapping):
        _refuse(f"{label} lacks its ledger mutation transaction identity")
    scientific = record.get("operation") in (
        "FROZEN_PER_ROUTE_AUTHORIZED_WRITE",
        "FROZEN_CONTINUATION_AUTHORIZED_WRITE",
    )
    projection = record.get("scientific_mutation_authority_projection")
    if not scientific:
        if any(
            record.get(field) is not None
            for field in (
                "scientific_mutation_authority_identity",
                "scientific_mutation_authority_projection",
                "campaign_authorization_identity",
                "route_id",
            )
        ):
            _refuse(f"{label} non-scientific ticket carries scientific authority")
        return
    if not isinstance(projection, Mapping):
        _refuse(f"{label} scientific ticket lacks one route authority projection")
    route_id = record.get("route_id")
    if projection.get("route_id") != route_id or record.get(
        "campaign_authorization_identity"
    ) is None:
        _refuse(f"{label} scientific route/campaign authority differs")
    resolved_field = (
        "scientific_authority_identity"
        if record["operation"] == "FROZEN_PER_ROUTE_AUTHORIZED_WRITE"
        else "continuation_authority_identity"
    )
    if record.get("scientific_mutation_authority_identity") != projection.get(
        resolved_field
    ):
        _refuse(f"{label} resolved scientific authority differs from its exact route")


def _validate_ledger_create_observation(record_value: Any, label: str) -> None:
    record = _mapping(record_value, label)
    handle = _handle(record["ledger_handle_value_uint64"], f"{label}.ledger_handle")
    if (
        record["create_api"] != "CreateFileW"
        or record["create_desired_access"] != 0xC0000000
        or record["create_share_mode"] != 1
        or record["create_disposition"] != 1
        or record["create_flags_and_attributes"] != 0x80200080
        or not record["create_returned_valid_handle"]
    ):
        _refuse(f"{label} is not the frozen CREATE_NEW held-ledger open")
    wchar_capacity = _uint(record["path_query_output_buffer_wchar_capacity"], 32, f"{label}.path_query_output_buffer_wchar_capacity", positive=True)
    _raw_image(
        record,
        "path_query_output_buffer_input_bytes_base64",
        "path_query_output_buffer_input_sha256",
        f"{label} path-query zero preimage",
        expected_size=2 * wchar_capacity,
        require_zero=True,
    )
    for prefix, size, output_prefix in (
        ("file_id_query_output_buffer", 24, "file_id_query_output"),
        ("standard_info_query_output_buffer", 24, "standard_info_query_output"),
        ("attribute_query_output_buffer", 8, "attribute_query_output"),
    ):
        if record[f"{prefix}_capacity"] != size:
            _refuse(f"{label} {prefix} capacity differs")
        _raw_image(record, f"{prefix}_input_bytes_base64", f"{prefix}_input_sha256", f"{label} {prefix} zero preimage", expected_size=size, require_zero=True)
        _raw_image(record, f"{output_prefix}_bytes_base64", f"{output_prefix}_sha256", f"{label} {prefix} returned image", expected_size=size)
    for field in (
        "path_query_input_handle_value_uint64",
        "file_id_query_input_handle_value_uint64",
        "standard_info_query_input_handle_value_uint64",
        "attribute_query_input_handle_value_uint64",
    ):
        if record[field] != handle:
            _refuse(f"{label} {field} differs from the retained ledger handle")
    path_output = _raw_image(record, "path_query_output_bytes_base64", "path_query_output_sha256", f"{label} path-query returned image")
    returned_chars = record["path_query_returned_wchar_count"]
    if (
        len(path_output) != 2 * (returned_chars + 1)
        or not path_output.endswith(b"\x00\x00")
        or returned_chars >= wchar_capacity
        or not record["path_query_returned_count_output_terminator_and_capacity_reconcile"]
        or not record["path_query_output_buffer_input_is_exactly_two_times_wchar_capacity_zero_bytes"]
        or not record["all_raw_call_handles_paths_pointers_counts_images_parsed_values_and_hashes_reconcile"]
        or not record["handle_continuously_retained"]
    ):
        _refuse(f"{label} path/raw/retained-handle reconciliation differs")


def _validate_ledger_append_observation(record_value: Any, label: str) -> None:
    record = _mapping(record_value, label)
    handle = _handle(record["ledger_handle_value_uint64"], f"{label}.ledger_handle")
    for field in (
        "preappend_file_standard_info_handle_value_uint64",
        "set_append_pointer_input_handle_value_uint64",
        "write_input_handle_value_uint64",
        "flush_input_handle_value_uint64",
        "postflush_file_standard_info_handle_value_uint64",
        "set_reread_pointer_input_handle_value_uint64",
        "reread_input_handle_value_uint64",
        "restore_pointer_input_handle_value_uint64",
    ):
        if record[field] != handle:
            _refuse(f"{label} {field} differs from the retained ledger handle")
    for prefix, output_prefix in (
        ("preappend_file_standard_info_output_buffer", "preappend_file_standard_info_output"),
        ("postflush_file_standard_info_output_buffer", "postflush_file_standard_info_output"),
    ):
        if record[f"{prefix}_capacity"] != 24:
            _refuse(f"{label} {prefix} capacity differs")
        _raw_image(record, f"{prefix}_input_bytes_base64", f"{prefix}_input_sha256", f"{label} {prefix} zero preimage", expected_size=24, require_zero=True)
        _raw_image(record, f"{output_prefix}_bytes_base64", f"{output_prefix}_sha256", f"{label} {prefix} returned image", expected_size=24)
    for prefix in (
        "set_append_pointer_new_position",
        "set_reread_pointer_new_position",
        "restore_pointer_new_position",
    ):
        _raw_image(record, f"{prefix}_input_bytes_base64", f"{prefix}_input_sha256", f"{label} {prefix} zero preimage", expected_size=8, require_zero=True)
        _raw_image(record, f"{prefix}_output_bytes_base64", f"{prefix}_output_sha256", f"{label} {prefix} returned image", expected_size=8)
    for prefix, parsed_field in (
        ("write_bytes_written", "written_byte_count"),
        ("reread_bytes_read", "reread_bytes_read"),
    ):
        _raw_image(record, f"{prefix}_input_bytes_base64", f"{prefix}_input_sha256", f"{label} {prefix} zero preimage", expected_size=4, require_zero=True)
        returned = _raw_image(record, f"{prefix}_output_bytes_base64", f"{prefix}_output_sha256", f"{label} {prefix} returned image", expected_size=4)
        if int.from_bytes(returned, "little", signed=False) != record[parsed_field]:
            _refuse(f"{label} {prefix} returned DWORD differs")
    wire = _raw_image(record, "entry_wire_bytes_base64", "entry_wire_sha256", f"{label} entry wire", expected_size=record["entry_wire_buffer_byte_count"])
    if not wire.endswith(b"\n") or wire.endswith(b"\r\n"):
        _refuse(f"{label} entry wire is not canonical JSON followed by one LF")
    try:
        entry = strict_loads(wire[:-1])
    except BindingRefusal as exc:
        raise BindingRefusal(f"{label} entry wire is not strict JSON") from exc
    if canonical_bytes(entry) + b"\n" != wire:
        _refuse(f"{label} entry wire is not canonical")
    start = _uint(record["append_start_offset"], 64, f"{label}.append_start_offset")
    count = _uint(record["append_byte_count"], 32, f"{label}.append_byte_count", positive=True)
    end = start + count
    if end > _UINT64_MAX:
        _refuse(f"{label} append offset overflows uint64")
    if (
        record["preappend_end_of_file_bytes"] != start
        or record["set_append_pointer_result_offset"] != start
        or record["append_end_offset"] != end
        or record["written_byte_count"] != count
        or record["postflush_file_size"] != end
        or record["set_reread_pointer_result_offset"] != start
        or record["reread_start_offset"] != start
        or record["reread_byte_count"] != count
        or record["reread_bytes_read"] != count
        or record["restore_pointer_result_offset"] != end
    ):
        _refuse(f"{label} append/reread/restore offsets differ")
    _raw_image(record, "reread_buffer_input_bytes_base64", "reread_buffer_input_sha256", f"{label} reread zero preimage", expected_size=count, require_zero=True)
    reread = _raw_image(record, "reread_raw_bytes_base64", "reread_sha256", f"{label} reread bytes", expected_size=count)
    if reread != wire:
        _refuse(f"{label} same-handle reread differs from appended wire")
    if (
        not record["reread_buffer_input_zero_initialized"]
        or not record["reread_buffer_input_is_exactly_reread_byte_count_zero_bytes"]
        or not record["all_raw_call_handles_pointers_counts_zero_preimages_returned_images_and_hashes_reconcile"]
        or not record["all_offsets_counts_hashes_and_handles_reconciled"]
    ):
        _refuse(f"{label} raw append reconciliation differs")
    _sha256(record["parent_watch_range_sha256"], f"{label}.parent_watch_range_sha256")
    _sha256(record["usn_range_sha256"], f"{label}.usn_range_sha256")


def _validate_docker_start_attempt(record_value: Any, label: str) -> None:
    record = _mapping(record_value, label)
    connection = _mapping(record["connection"], f"{label}.connection")
    handle = _handle(connection["pipe_handle_value_uint64"], f"{label}.pipe_handle")
    if (
        connection["named_pipe_path"] != r"\\.\pipe\docker_engine"
        or connection["pipe_read_mode"] != "PIPE_READMODE_BYTE"
        or connection["pipe_wait_mode"] != "PIPE_NOWAIT"
        or connection["set_wait_mode_mode_input_bytes_base64"] != "AQAAAA=="
        or record["write_input_handle_value_uint64"] != handle
        or not record["write_overlapped_pointer_is_null"]
    ):
        _refuse(f"{label} does not use the authenticated byte/NOWAIT connection")
    reads = record["ordered_read_calls"]
    if type(reads) is not list or len(reads) != record["read_call_count"] or len(reads) > 1201:
        _refuse(f"{label} read count differs or exceeds 1201")
    for ordinal, read_value in enumerate(reads, 1):
        read = _mapping(read_value, f"{label}.ordered_read_calls[{ordinal}]")
        if read["ordinal"] != ordinal or read["input_handle_value_uint64"] != handle:
            _refuse(f"{label} read ordinal or handle differs")
        if read["last_error"] == 234:
            _refuse(f"{label} records impossible ERROR_MORE_DATA in byte-read mode")
        if not read["overlapped_pointer_is_null"]:
            _refuse(f"{label} read is not synchronous NULL-overlapped I/O")
        _raw_image(read, "bytes_read_input_bytes_base64", "bytes_read_input_sha256", f"{label} read {ordinal} DWORD zero preimage", expected_size=4, require_zero=True)
        returned = _raw_image(read, "bytes_read_output_bytes_base64", "bytes_read_output_sha256", f"{label} read {ordinal} returned DWORD", expected_size=4)
        output = _raw_image(read, "output_bytes_base64", "output_sha256", f"{label} read {ordinal} returned data", expected_size=read["bytes_read"], allow_empty=True)
        if int.from_bytes(returned, "little") != len(output):
            _refuse(f"{label} read {ordinal} returned DWORD differs")
        if read["pre_read_monotonic_tick_uint64"] > read["post_read_monotonic_tick_uint64"]:
            _refuse(f"{label} read {ordinal} ticks are reversed")
    release = _mapping(record["connection_release"], f"{label}.connection_release")
    if (
        release["pipe_handle_value_uint64"] != handle
        or release["close_input_handle_value_uint64"] != handle
        or not release["close_returned_nonzero"]
        or not release["handle_closed_once"]
        or not release["no_use_after_close"]
    ):
        _refuse(f"{label} connection was not closed exactly once")
    if record["transport_disposition"] == "FULL_WRITE_NO_FURTHER_READ_CUT":
        window = _mapping(record["bounded_response_window"], f"{label}.cut")
        if window["schema"] != "stage_f_docker_named_pipe_no_further_read_cut_observation/v1":
            _refuse(f"{label} no-further-read cut evidence differs")
    elif record["write_disposition"] == "FULL_WRITE":
        window = _mapping(record["bounded_response_window"], f"{label}.window")
        if (
            window["schema"] != "stage_f_docker_named_pipe_bounded_response_window_observation/v1"
            or window["timeout_ms"] != 30000
            or window["maximum_poll_delay_ms"] != 25
            or window["maximum_read_attempt_count"] != 1201
            or not window["no_read_or_poll_after_terminal_cut"]
        ):
            _refuse(f"{label} bounded response window differs")
    if record["response_is_exact_complete_http_204"] or not record["daemon_acceptance_unknown"]:
        _refuse(f"{label} failure/ambiguity attempt is not conservatively unknown")


def _validate_retained_subtree_allocation(record_value: Any, label: str) -> int:
    record = _mapping(record_value, label)
    entries = record["inventory_entries"]
    if type(entries) is not list or record["inventory_entry_count"] != len(entries):
        _refuse(f"{label} inventory count differs")
    paths = [entry["relative_path"] for entry in entries]
    if (
        record["ordered_relative_paths_utf8_nfc_ascending"] is not True
        or any(unicodedata.normalize("NFC", path) != path for path in paths)
        or paths != sorted(paths, key=lambda path: path.encode("utf-8"))
    ):
        _refuse(f"{label} inventory path order differs")
    direct_sum = sum(entry["accounted_bytes"] for entry in entries)
    if (
        direct_sum != record["direct_accounted_bytes_sum"]
        or direct_sum != record["retained_evidence_live_allocated_bytes"]
        or not record["direct_sum_equals_live_scalar"]
        or not record["root_entry_included"]
        or not record["all_descendants_included"]
        or record["unknown_entry_count"] != 0
    ):
        _refuse(f"{label} is not one complete direct retained-allocation sum")
    return direct_sum


def _validate_raw_volume_capacity_observation(record_value: Any, label: str) -> int:
    record = _mapping(record_value, label)
    allocation = record["sectors_per_cluster"] * record["bytes_per_sector"]
    win32_free = record["number_of_free_clusters"] * allocation
    win32_capacity = record["total_number_of_clusters"] * allocation
    ntfs = _mapping(record["ntfs_volume_data"], f"{label}.ntfs_volume_data")
    ntfs_free = ntfs["free_clusters"] * ntfs["bytes_per_cluster"]
    ntfs_capacity = ntfs["total_clusters"] * ntfs["bytes_per_cluster"]
    conservative_free = min(
        win32_free,
        record["available_to_caller_bytes"],
        record["total_number_of_free_bytes"],
        ntfs_free,
    )
    conservative_capacity = min(
        win32_capacity, record["total_number_of_bytes"], ntfs_capacity
    )
    if (
        record["allocation_unit_bytes"] != allocation
        or record["get_disk_free_space_w_free_bytes"] != win32_free
        or record["get_disk_free_space_w_capacity_bytes"] != win32_capacity
        or record["ntfs_volume_data_free_bytes"] != ntfs_free
        or record["ntfs_volume_data_capacity_bytes"] != ntfs_capacity
        or record["conservative_observed_free_bytes"] != conservative_free
        or record["conservative_observed_capacity_bytes"] != conservative_capacity
        or not record["all_formulas_recomputed"]
        or not record["free_space_outputs_reconciled"]
        or not record["capacity_outputs_reconciled"]
    ):
        _refuse(f"{label} raw capacity formulas differ")
    return conservative_free


_STAGE_F_CAPACITY_COMPONENT_FIELDS = (
    "primary_logical_output_bytes",
    "independent_audit_copy_bytes",
    "dynamic_growth_physical_write_bytes",
    "checkpoint_and_write_overhead_bytes",
    "temporary_archive_bytes",
    "retained_evidence_bytes",
)
_STAGE_F_CAPACITY_COMPONENT_CEILINGS = MappingProxyType(
    {
        "primary_logical_output_bytes": 253 * 1073741824,
        "independent_audit_copy_bytes": 253 * 1073741824,
        "dynamic_growth_physical_write_bytes": 80 * 1073741824,
        "checkpoint_and_write_overhead_bytes": 64 * 1073741824,
        "temporary_archive_bytes": 8 * 1073741824,
        "retained_evidence_bytes": 8 * 1073741824,
    }
)
_STAGE_F_RESERVED_ENVELOPE_BYTES = 715112054784


def _validate_capacity_usage_projection(
    record_value: Any, label: str
) -> tuple[dict[str, Any], dict[str, str]]:
    record = _mapping(record_value, label)
    identity = _embedded_record_identity(
        record,
        "projection_sha256",
        kind="stage_f_capacity_usage_projection/v1",
    )
    values: list[int] = []
    for field in _STAGE_F_CAPACITY_COMPONENT_FIELDS:
        value = record.get(field)
        if type(value) is not int or value < 0:
            _refuse(f"{label}.{field} is not a nonnegative integer")
        if value > _STAGE_F_CAPACITY_COMPONENT_CEILINGS[field]:
            _refuse(f"{label}.{field} exceeds its frozen ceiling")
        values.append(value)
    if record["retained_evidence_bytes"] != 8 * 1073741824:
        _refuse(f"{label} does not retain the full evidence predebit")
    if record.get("total_envelope_usage_bytes") != sum(values):
        _refuse(f"{label} total is not the exact six-component sum")
    return record, identity


def _validate_capacity_control_record(
    record_value: Any, definition: str, label: str
) -> None:
    record = _mapping(record_value, label)
    if definition == "stage_f_capacity_publication_observation":
        retained_field = "postpublication_retained_subtree_observation"
        raw_field = "postpublication_raw_volume_observation"
        scalar_field = "retained_evidence_live_allocated_bytes"
        free_field = "fresh_observed_free_bytes"
    elif definition == "stage_f_capacity_consumption_closure":
        retained_field = "current_retained_subtree_observation"
        raw_field = "current_raw_volume_observation"
        scalar_field = "retained_evidence_live_allocated_bytes"
        free_field = "observed_free_bytes"
    elif definition == "stage_f_capacity_live_gate":
        retained_field = "fresh_retained_subtree_observation"
        raw_field = "fresh_raw_volume_observation"
        scalar_field = "retained_evidence_live_allocated_bytes"
        free_field = "observed_free_bytes"
    else:
        _refuse(f"{label} capacity definition differs")
    retained = _validate_retained_subtree_allocation(record[retained_field], f"{label}.{retained_field}")
    conservative_free = _validate_raw_volume_capacity_observation(record[raw_field], f"{label}.{raw_field}")
    if retained != record[scalar_field] or conservative_free != record[free_field]:
        _refuse(f"{label} direct retained or conservative free scalar differs")
    if retained > 8589934592:
        _refuse(f"{label} exceeds the retained-evidence predebit")
    if definition == "stage_f_capacity_consumption_closure":
        projection, projection_identity = _validate_capacity_usage_projection(
            record["component_usage_projection"],
            f"{label}.component_usage_projection",
        )
        snapshot = _mapping(record["storage_capacity_snapshot"], f"{label}.snapshot")
        snapshot_usage = _mapping(
            snapshot["current_envelope_usage"], f"{label}.snapshot.current_usage"
        )
        if any(
            snapshot_usage[field] != projection[field]
            for field in _STAGE_F_CAPACITY_COMPONENT_FIELDS
        ):
            _refuse(f"{label} six-component projection differs from its snapshot")
        total = projection["total_envelope_usage_bytes"]
        remaining = _STAGE_F_RESERVED_ENVELOPE_BYTES - total
        if record["retained_evidence_remaining_tail_bytes"] != 8589934592 - retained:
            _refuse(f"{label} retained-evidence remaining-tail formula differs")
        if not (
            record["inventory_difference_equals_causal_rows"]
            and record["direct_sum_equals_live_scalar"]
            and record["remaining_tail_formula_recomputed"]
            and record["remaining_reserved_envelope_formula_recomputed"]
            and record["free_space_floor_and_remaining_envelope_pass"]
            and record["component_usage_projection_identity"] == projection_identity
            and record["total_envelope_usage_bytes"] == total
            and snapshot_usage["total_envelope_usage_bytes"] == total
            and snapshot["remaining_reserved_envelope_bytes"] == remaining
            and record["remaining_reserved_envelope_bytes"] == remaining
        ):
            _refuse(f"{label} capacity consumption closure predicates differ")
    if definition == "stage_f_capacity_live_gate":
        closure = _mapping(
            record["capacity_consumption_closure"], f"{label}.closure"
        )
        projection, projection_identity = _validate_capacity_usage_projection(
            closure["component_usage_projection"],
            f"{label}.closure.component_usage_projection",
        )
        closure_identity = _embedded_record_identity(
            closure,
            "closure_sha256",
            kind="stage_f_capacity_consumption_closure/v1",
        )
        remaining = (
            _STAGE_F_RESERVED_ENVELOPE_BYTES
            - projection["total_envelope_usage_bytes"]
        )
        if (
            record["minimum_free_bytes"] != 375809638400
            or record["retained_evidence_ceiling_bytes"] != 8589934592
            or conservative_free
            < max(
                record["minimum_free_bytes"],
                record["remaining_reserved_envelope_bytes"],
            )
            or not record["all_capacity_predicates_pass"]
            or not record["no_intervening_controller_capacity_affecting_operation"]
            or not record["held_in_controller_memory_through_following_operation"]
            or record["capacity_consumption_closure_identity"] != closure_identity
            or record["component_usage_projection_identity"] != projection_identity
            or record["total_envelope_usage_bytes"]
            != projection["total_envelope_usage_bytes"]
            or record["remaining_reserved_envelope_bytes"] != remaining
            or record.get("closure_projection_total_and_remaining_exactly_repeated")
            is not True
            or record.get("exact_following_operation_capability") is None
            or record["exact_following_operation_capability_identity"]
            != _embedded_record_identity(
                _mapping(
                    record["exact_following_operation_capability"],
                    f"{label}.exact_following_operation_capability",
                ),
                "capability_sha256",
            )
        ):
            _refuse(f"{label} exact prestart capacity gate differs")


def _validate_host_prerequisite_snapshot(record_value: Any, label: str) -> None:
    record = _mapping(record_value, label)
    facts = _mapping(record["facts"], f"{label}.facts")
    raw = _raw_image(
        facts,
        "system_power_status_bytes_base64",
        "system_power_status_sha256",
        f"{label} SYSTEM_POWER_STATUS",
        expected_size=12,
    )
    projection = (
        raw[0],
        raw[1],
        raw[2],
        raw[3],
        int.from_bytes(raw[4:8], "little"),
        int.from_bytes(raw[8:12], "little"),
    )
    if projection != (
        facts["ac_line_status"],
        facts["battery_flag"],
        facts["battery_life_percent"],
        facts["system_status_flag"],
        facts["battery_life_time_seconds"],
        facts["battery_full_life_time_seconds"],
    ):
        _refuse(f"{label} SYSTEM_POWER_STATUS raw projection differs")
    lid_map = {0: "DO_NOTHING", 1: "SLEEP", 2: "HIBERNATE", 3: "SHUTDOWN"}
    lid_raw = facts["plugged_in_lid_action_raw_index"]
    if lid_raw not in lid_map or facts["plugged_in_lid_action"] != lid_map[lid_raw]:
        _refuse(f"{label} lid-action raw mapping differs")
    if (
        not facts["get_system_power_status_returned_nonzero"]
        or facts["ac_line_status"] != 1
        or facts["plugged_in_standby_idle_seconds"] != 0
        or (lid_raw != 0 and facts["lid_open_statement_identity"] is None)
        or facts["pending_reboot_registry_row_count"] != 8
        or len(facts["pending_reboot_registry_rows"]) != 8
        or facts["pending_reboot_marker_count"] != 0
        or facts["no_auto_reboot_policy_value"] != 1
        or not facts["controller_session_logged_on"]
        or not facts["derived_power_fields_reconcile_raw_queries"]
        or record["settings_changed_by_validator"]
        or not record["historical_power_snapshot_exact_raw_fact_projection"]
    ):
        _refuse(f"{label} power/reboot/session prerequisites differ")


_STAGE_F_CONTAINER_ID_RE = re.compile(r"^[0-9a-f]{64}$")


def _validate_docker_exchange_binding(
    exchange_value: Any, label: str
) -> tuple[datetime, datetime, tuple[Any, ...]]:
    exchange = _mapping(exchange_value, label)
    connection = _mapping(exchange["connection"], f"{label}.connection")
    release = _mapping(exchange["connection_release"], f"{label}.release")
    handle = _handle(connection["pipe_handle_value_uint64"], f"{label}.pipe_handle")
    request = _strict_base64(exchange["request_wire_bytes_base64"], f"{label}.request")
    expected_prefix = (
        f"{exchange['method']} {exchange['endpoint']} HTTP/1.1\r\n".encode("ascii")
    )
    if (
        not request.startswith(expected_prefix)
        or exchange["request_wire_sha256"] != hashlib.sha256(request).hexdigest()
        or exchange["write_input_handle_value_uint64"] != handle
        or release["pipe_handle_value_uint64"] != handle
        or release["close_input_handle_value_uint64"] != handle
        or release["server_process_id"] != connection["server_process_id"]
        or release["server_process_creation_filetime_uint64"]
        != connection["server_process_creation_filetime_uint64"]
        or release["no_pipe_io_after_close"] is not True
        or release["single_close_ownership_no_double_close_and_no_use_after_close"]
        is not True
    ):
        _refuse(f"{label} request target, handle, server, or close lifetime differs")
    opened = _utc(connection["opened_utc"], f"{label}.opened_utc")
    closed = _utc(release["closed_utc"], f"{label}.closed_utc")
    completed = _utc(exchange["completed_utc"], f"{label}.completed_utc")
    if not opened <= completed <= closed:
        _refuse(f"{label} connection lifetime does not contain all exchange I/O")
    server = (
        connection["server_process_id"],
        connection["server_process_creation_filetime_uint64"],
        canonical_bytes(connection["server_runtime_identity"]),
    )
    return opened, closed, server


def _validate_docker_exchange_sequence(
    exchanges: Sequence[Mapping[str, Any]], label: str
) -> None:
    lifetimes = [
        _validate_docker_exchange_binding(exchange, f"{label}[{ordinal}]")
        for ordinal, exchange in enumerate(exchanges, 1)
    ]
    if not lifetimes:
        _refuse(f"{label} has no authenticated Docker exchange")
    server = lifetimes[0][2]
    for ordinal, (opened, closed, current_server) in enumerate(lifetimes):
        if current_server != server:
            _refuse(f"{label} splices Docker daemon process identities")
        if ordinal and opened < lifetimes[ordinal - 1][1]:
            _refuse(f"{label} fresh Docker connection lifetimes overlap")
        if opened > closed:
            _refuse(f"{label} Docker connection lifetime is reversed")


def _validate_inert_container_observation(record_value: Any, label: str) -> str:
    record = _mapping(record_value, label)
    container_id = record.get("container_id")
    if type(container_id) is not str or _STAGE_F_CONTAINER_ID_RE.fullmatch(
        container_id
    ) is None:
        _refuse(f"{label} container ID is not exact lowercase 64-hex")
    response = _strict_base64(
        record["create_response_bytes_base64"], f"{label}.create_response"
    )
    try:
        response_object = strict_loads(response)
    except BindingRefusal as exc:
        raise BindingRefusal(f"{label} create response is not strict JSON") from exc
    if not isinstance(response_object, Mapping) or response_object.get("Id") != container_id:
        _refuse(f"{label} container ID is not sourced from the exact create response")
    inspect_endpoint = f"/containers/{container_id}/json"
    create_exchange = _mapping(record["create_exchange"], f"{label}.create_exchange")
    inspect_exchange = _mapping(record["inspect_exchange"], f"{label}.inspect_exchange")
    engine = _mapping(record["docker_engine_observation"], f"{label}.engine")
    engine_wrappers = engine["ordered_engine_request_observations"]
    if type(engine_wrappers) is not list:
        _refuse(f"{label} engine observations are not an array")
    engine_exchanges = [
        _mapping(row, f"{label}.engine[{ordinal}]")["exchange"]
        for ordinal, row in enumerate(engine_wrappers, 1)
    ]
    if (
        record["create_endpoint"] != "/containers/create"
        or create_exchange["endpoint"] != "/containers/create"
        or record["inspect_endpoint"] != inspect_endpoint
        or inspect_exchange["endpoint"] != inspect_endpoint
        or record["named_pipe_connection_observation"] != create_exchange["connection"]
    ):
        _refuse(f"{label} create/inspect endpoint or connection projection differs")
    _validate_docker_exchange_sequence(
        [*engine_exchanges, create_exchange, inspect_exchange],
        f"{label}.ordered_connections",
    )
    return container_id


def _validate_root_watch_live_state_links(
    record_value: Any, root_value: Any, label: str
) -> None:
    record = _mapping(record_value, label)
    root = _mapping(root_value, f"{label}.root")
    root_identity = _embedded_record_identity(
        root,
        "epoch_sha256",
        kind="stage_f_root_protection_epoch/v1",
    )
    watches = root["watches"]
    completions = record["completion_rows"]
    pending = record.get("pending_watch_resources")
    if type(watches) is not list or type(completions) is not list or type(pending) is not list:
        _refuse(f"{label} watch/completion/pending resources are not arrays")
    if (
        root["watch_count"] != len(watches)
        or record["watch_count"] != len(watches)
        or record["completion_row_count"] != len(completions)
        or record.get("pending_watch_resource_count") != len(pending)
        or len(pending) != len(watches)
        or record["pending_watch_ordinals"] != list(range(1, len(watches) + 1))
        or record.get("root_protection_epoch_identity") != root_identity
        or record.get("holder_process_id") != root.get("holder_process_id")
        or record.get("holder_process_creation_filetime_uint64")
        != root.get("holder_process_creation_filetime_uint64")
        or record.get("completion_rows_complete_and_strictly_ordered") is not True
        or record.get("counts_and_pending_cycles_reconcile") is not True
        or record.get("all_pending_since_latest_issue_or_reissue") is not True
        or record.get("all_acquired_watches_pending") is not True
        or record.get("unmatched_protected_event_count") != 0
    ):
        _refuse(f"{label} watch/completion/pending counts differ")
    completions_by_watch: dict[int, list[Mapping[str, Any]]] = {}
    for completion in completions:
        completions_by_watch.setdefault(completion["watch_ordinal"], []).append(completion)
    for rows in completions_by_watch.values():
        if [row["cycle_ordinal"] for row in rows] != list(range(1, len(rows) + 1)):
            _refuse(f"{label} completion cycles are not contiguous")
    for ordinal, (watch, resource) in enumerate(zip(watches, pending, strict=True), 1):
        latest_rows = completions_by_watch.get(ordinal, [])
        latest = latest_rows[-1] if latest_rows else watch
        expected_cycle = latest["reissue_cycle_ordinal"] if latest_rows else 1
        expected = {
            "watch_ordinal": ordinal,
            "pending_cycle_ordinal": expected_cycle,
            "role": watch["role"],
            "directory_handle_value_uint64": watch["directory_handle_value_uint64"],
            "buffer_base_address_uint64": watch["buffer_base_address_uint64"],
            "buffer_capacity": watch["buffer_capacity"],
            "overlapped_address_uint64": watch["overlapped_address_uint64"],
            "event_handle_value_uint64": watch["event_handle_value_uint64"],
            "completion_bytes_output_address_uint64": watch[
                "completion_bytes_output_address_uint64"
            ],
            "notification_filter": watch["notification_filter"],
            "watch_subtree": watch["recursive"],
            "request_pending": True,
        }
        if dict(resource) != expected:
            _refuse(f"{label} pending resource {ordinal} substitutes a watch resource")
        if latest_rows and any(
            latest[field] != expected[target]
            for field, target in (
                ("reissue_directory_handle_value_uint64", "directory_handle_value_uint64"),
                ("reissue_buffer_base_address_uint64", "buffer_base_address_uint64"),
                ("reissue_overlapped_address_uint64", "overlapped_address_uint64"),
                ("event_handle_value_uint64", "event_handle_value_uint64"),
                ("completion_bytes_output_address_uint64", "completion_bytes_output_address_uint64"),
                ("notification_filter", "notification_filter"),
                ("watch_subtree", "watch_subtree"),
            )
        ):
            _refuse(f"{label} completion/reissue {ordinal} substitutes resources")
    expected_cycles = [
        (
            completions_by_watch[ordinal][-1]["reissue_cycle_ordinal"]
            if completions_by_watch.get(ordinal)
            else 1
        )
        for ordinal in range(1, len(watches) + 1)
    ]
    if record.get("pending_cycle_ordinals") != expected_cycles:
        _refuse(f"{label} pending-cycle projection differs")
    if record.get("pending_resources_reconcile_acquisition_completion_and_latest_reissue") is not True:
        _refuse(f"{label} does not assert exact pending-resource reconciliation")


def _validate_launch_gate_container_links(
    record_value: Any, root_value: Any | None = None
) -> None:
    gate = _mapping(record_value, "Stage F scientific launch gate")
    inert = _mapping(gate["inert_container_observation"], "launch gate inert container")
    _validate_inert_container_observation(inert, "launch gate inert container")
    inert_identity = _embedded_record_identity(
        inert,
        "container_observation_sha256",
        kind="stage_f_inert_container/v1",
    )
    if gate["inert_container_identity"] != inert_identity:
        _refuse("launch gate inert-container identity differs")
    if root_value is not None:
        root = _mapping(root_value, "Stage F launch-gate root epoch")
        root_identity = _embedded_record_identity(
            root,
            "epoch_sha256",
            kind="stage_f_root_protection_epoch/v1",
        )
        live_state = _mapping(
            gate["root_watch_live_state"], "launch gate root-watch live state"
        )
        live_identity = _embedded_record_identity(
            live_state,
            "live_state_sha256",
            kind="stage_f_root_watch_live_state/v1",
        )
        if (
            gate["root_protection_epoch_identity"] != root_identity
            or gate["root_watch_live_state_identity"] != live_identity
            or gate.get("root_watch_live_state_identity_reconciles") is not True
        ):
            _refuse("launch gate root/watch embedded identities differ")
        _validate_root_watch_live_state_links(
            live_state,
            root,
            "launch gate root-watch live state",
        )


def _validate_start_intent_container_links(
    intent_value: Any, gate_value: Any
) -> None:
    intent = _mapping(intent_value, "Stage F start intent")
    gate = _mapping(gate_value, "Stage F launch gate")
    inert = _mapping(intent["inert_container_observation"], "start intent inert container")
    container_id = _validate_inert_container_observation(
        inert, "start intent inert container"
    )
    inert_identity = _embedded_record_identity(
        inert,
        "container_observation_sha256",
        kind="stage_f_inert_container/v1",
    )
    capability = _mapping(intent["container_start_capability"], "start capability")
    capability_identity = _embedded_record_identity(
        capability,
        "capability_sha256",
        kind="stage_f_container_start_capability/v1",
    )
    endpoint = f"/containers/{container_id}/start"
    request = _strict_base64(capability["request_bytes_base64"], "start request")
    if (
        intent["inert_container_identity"] != inert_identity
        or capability["container_id"] != container_id
        or capability["inert_container_identity"] != inert_identity
        or capability["method"] != "POST"
        or capability["endpoint"] != endpoint
        or not request.startswith(f"POST {endpoint} HTTP/1.1\r\n".encode("ascii"))
        or capability["request_sha256"] != hashlib.sha256(request).hexdigest()
        or capability["request_is_complete_http_wire"] is not True
        or capability["request_constructed_not_sent"] is not True
        or capability["start_call_invoked"] is not False
        or capability["single_use"] is not True
        or intent["container_start_capability_identity"] != capability_identity
        or intent["inert_container_identity"] != gate["inert_container_identity"]
        or inert != gate["inert_container_observation"]
        or intent["scientific_launch_gate_identity"]
        != _embedded_record_identity(
            gate,
            "gate_sha256",
            kind="stage_f_scientific_launch_gate/v1",
        )
        or intent["root_protection_epoch_identity"]
        != gate["root_protection_epoch_identity"]
        or intent.get("all_embedded_identities_and_container_bindings_reconcile")
        is not True
        or intent.get("capability_request_exactly_targets_intent_container")
        is not True
    ):
        _refuse("start intent/capability/gate container target differs")


def _validate_handoff_container_links(
    handoff_value: Any, intent_value: Any, gate_value: Any
) -> None:
    handoff = _mapping(handoff_value, "Stage F scientific handoff")
    intent = _mapping(intent_value, "Stage F start intent")
    gate = _mapping(gate_value, "Stage F launch gate")
    inert = _mapping(handoff["container_observation"], "handoff container")
    container_id = _validate_inert_container_observation(inert, "handoff container")
    inert_identity = _embedded_record_identity(
        inert,
        "container_observation_sha256",
        kind="stage_f_inert_container/v1",
    )
    capability = _mapping(
        handoff["container_start_capability"], "handoff start capability"
    )
    capability_identity = _embedded_record_identity(
        capability,
        "capability_sha256",
        kind="stage_f_container_start_capability/v1",
    )
    intent_identity = _embedded_record_identity(
        intent,
        "intent_sha256",
        kind="stage_f_container_start_intent/v1",
    )
    gate_identity = _embedded_record_identity(
        gate,
        "gate_sha256",
        kind="stage_f_scientific_launch_gate/v1",
    )
    if (
        handoff["container_identity"] != inert_identity
        or handoff["container_identity"] != intent["inert_container_identity"]
        or handoff["container_identity"] != gate["inert_container_identity"]
        or capability["container_id"] != container_id
        or handoff["container_start_intent"] != intent
        or capability != intent["container_start_capability"]
        or handoff["container_start_intent_identity"] != intent_identity
        or handoff["container_start_capability_identity"] != capability_identity
        or handoff["scientific_launch_gate_identity"] != gate_identity
        or handoff["root_protection_epoch_identity"]
        != intent["root_protection_epoch_identity"]
        or handoff["root_protection_epoch_identity"]
        != gate["root_protection_epoch_identity"]
        or handoff["evidence_ledger_predecessor_identity"]
        != intent["evidence_ledger_predecessor_identity"]
        or handoff["root_watch_live_state"] != gate["root_watch_live_state"]
        or handoff["root_watch_live_state_identity"]
        != gate["root_watch_live_state_identity"]
        or handoff.get("all_embedded_identities_and_container_bindings_reconcile")
        is not True
    ):
        _refuse("scientific handoff substitutes its container, intent, or capability")


def _validate_suspended_validator_material(
    state: _WindowsStageFControllerState, observation_value: Any
) -> None:
    observation = _mapping(observation_value, "Stage F suspended validator observation")
    assert state.validate_definition is not None
    host = _mapping(
        observation.get("fresh_host_prerequisite_snapshot"),
        "Stage F suspended validator host snapshot",
    )
    gate = _mapping(
        observation.get("final_capacity_live_gate"),
        "Stage F suspended validator capacity gate",
    )
    attestation = _mapping(
        observation.get("pre_resume_launch_attestation"),
        "Stage F suspended validator attestation",
    )
    capability = _mapping(
        observation.get("resume_capability"),
        "Stage F suspended validator resume capability",
    )
    launch = _mapping(
        observation.get("process_launch_observation"),
        "Stage F suspended validator launch",
    )
    for definition, record in (
        ("stage_f_host_prerequisite_snapshot", host),
        ("stage_f_capacity_live_gate", gate),
        ("durability_suspended_process_launch_attestation", attestation),
        ("stage_f_host_validation_process_resume_capability", capability),
        ("durability_process_launch_observation", launch),
    ):
        state.validate_definition(definition, record)
    _validate_host_prerequisite_snapshot(host, "Stage F suspended validator host")
    _validate_capacity_control_record(
        gate,
        "stage_f_capacity_live_gate",
        "Stage F suspended validator capacity gate",
    )
    capability_identity = _embedded_record_identity(
        capability,
        "capability_sha256",
        kind="stage_f_host_validation_process_resume_capability/v1",
    )
    gate_identity = _embedded_record_identity(
        gate, "gate_sha256", kind="stage_f_capacity_live_gate/v1"
    )
    attestation_identity = _embedded_record_identity(
        attestation,
        "attestation_sha256",
        kind="stage_f_durability_suspended_process_launch_attestation/v1",
    )
    root_identity = _embedded_record_identity(
        state.root_epoch,
        "epoch_sha256",
        kind="stage_f_root_protection_epoch/v1",
    )
    if (
        capability["gate_role"] != "HOST_VALIDATION_PROCESS_RESUME"
        or capability["launch_phase"] != "ORCHESTRATOR"
        or capability["resume_target_role"] != "ORCHESTRATOR_PROCESS"
        or capability["root_protection_epoch_identity"] != root_identity
        or capability["suspended_process_launch_attestation"] != attestation
        or capability["resume_target_process_id"] != attestation["process_id"]
        or capability["resume_target_thread_id"] != attestation["thread_id"]
        or capability["resume_target_thread_handle_value_uint64"]
        != attestation["thread_handle_value_uint64"]
        or gate["gate_role"] != "HOST_VALIDATION_PROCESS_RESUME"
        or gate["exact_following_operation_capability"] != capability
        or gate["exact_following_operation_capability_identity"]
        != capability_identity
        or observation.get("resume_capability_identity") != capability_identity
        or launch["pre_resume_launch_attestation_sha256"]
        != attestation_identity["value"]
        or launch["host_validation_process_resume_capability_identity"]
        != capability_identity
        or launch["capacity_live_gate_identity"] != gate_identity
        or launch["process_id"] != capability["resume_target_process_id"]
        or launch["thread_id"] != capability["resume_target_thread_id"]
        or launch["resume_input_thread_handle_value_uint64"]
        != capability["resume_target_thread_handle_value_uint64"]
        or launch.get("launch_attestation_capability_gate_and_resume_recomputed")
        is not True
    ):
        _refuse(
            "suspended launch attestation/capability/live-gate/resume joins differ"
        )
    _validate_launch(launch, "ORCHESTRATOR", state.holder_process_id)


def _validate_root_epoch_semantics(record_value: Any, label: str) -> None:
    record = _mapping(record_value, label)
    genesis = _mapping(record["execution_attempt_genesis"], f"{label}.genesis")
    anchors = record["anchors"]
    watches = record["watches"]
    locks = record["immutable_file_locks"]
    if (
        type(anchors) is not list
        or record["anchor_count"] != len(anchors)
        or len(anchors) < 2
        or type(watches) is not list
        or record["watch_count"] != len(watches)
        or len(watches) < 2
        or type(locks) is not list
        or record["immutable_file_lock_count"] != len(locks)
        or not locks
    ):
        _refuse(f"{label} anchor/watch/file-lock counts differ")
    retained_values: set[int] = set()
    anchor_roles: list[str] = []
    for ordinal, anchor in enumerate(anchors, 1):
        if (
            anchor["ordinal"] != ordinal
            or anchor["parent_ordinal"] != (None if ordinal == 1 else ordinal - 1)
            or not anchor["compare_object_handles_at_epoch"]
            or anchor["anchor_handle_value_uint64"]
            == anchor["continuity_guard_handle_value_uint64"]
            or anchor["reparse_tag"] != 0
            or not anchor["held_through_launch_handoff"]
        ):
            _refuse(f"{label} anchor {ordinal} continuity differs")
        anchor_roles.append(anchor["role"])
        retained_values.update(
            (
                anchor["anchor_handle_value_uint64"],
                anchor["continuity_guard_handle_value_uint64"],
            )
        )
    if len(retained_values) != 2 * len(anchors):
        _refuse(f"{label} anchor/continuity-guard handles are not exclusive")
    if (
        anchor_roles[0] != "SELECTED_VOLUME_ROOT"
        or anchor_roles[-1] != "EXECUTION_ATTEMPT_ROOT"
        or anchor_roles.count("CAMPAIGN_PARENT") != 1
        or any(
            role not in ("SELECTED_VOLUME_ROOT", "INTERMEDIATE", "CAMPAIGN_PARENT", "EXECUTION_ATTEMPT_ROOT")
            for role in anchor_roles
        )
        or anchors[-1]["path_identity"] != genesis["attempt_path_identity"]
        or not any(
            anchor["role"] == "CAMPAIGN_PARENT"
            and anchor["path_identity"] == genesis["campaign_parent_path_identity"]
            for anchor in anchors
        )
    ):
        _refuse(f"{label} anchor chain does not bind volume, campaign parent, and fresh root")
    watch_resource_values: list[int] = []
    recursive_count = 0
    parent_watch_match_count = 0
    for ordinal, watch in enumerate(watches, 1):
        acquisition = _mapping(watch["acquisition"], f"{label} watch {ordinal} acquisition")
        if (
            watch["ordinal"] != ordinal
            or watch["notify_filter"] != 351
            or watch["buffer_byte_count"] != 65536
            or not watch["read_input_bytes_returned_pointer_is_null"]
            or watch["read_input_completion_routine_is_null"] is not True
            or not watch["read_returned_nonzero"]
            or watch["immediate_result_returned_nonzero"]
            or watch["immediate_result_last_error"] != 996
            or watch["immediate_result_bytes_transferred"] != 0
            or not watch["pending_at_common_epoch"]
            or watch["overflow_or_enumeration_loss"]
            or not watch["held_through_launch_handoff"]
        ):
            _refuse(f"{label} watch {ordinal} is not one pending lossless request")
        if watch["recursive"]:
            recursive_count += 1
        if (
            watch["role"] == "EXECUTION_ATTEMPT_ROOT_SUBTREE"
        ) != watch["recursive"]:
            _refuse(f"{label} watch {ordinal} role/recursive projection differs")
        projection = (
            watch["directory_handle_value_uint64"],
            watch["buffer_base_address_uint64"],
            watch["overlapped_address_uint64"],
            watch["event_handle_value_uint64"],
        )
        if projection != (
            acquisition["directory_handle_value_uint64"],
            acquisition["buffer_base_address_uint64"],
            acquisition["overlapped_address_uint64"],
            acquisition["event_handle_value_uint64"],
        ):
            _refuse(f"{label} watch {ordinal} substituted acquisition resources")
        if (
            watch["watched_path_identity"] != acquisition["directory_path_identity"]
            or watch["read_input_directory_handle_value_uint64"] != projection[0]
            or watch["read_input_buffer_base_address_uint64"] != projection[1]
            or watch["read_input_overlapped_address_uint64"] != projection[2]
            or watch["immediate_result_directory_handle_value_uint64"] != projection[0]
            or watch["immediate_result_overlapped_address_uint64"] != projection[2]
            or watch["read_input_watch_subtree"] != watch["recursive"]
        ):
            _refuse(f"{label} watch {ordinal} call/acquisition projection differs")
        acquisition_identity = sha256_identity(
            "stage_f_directory_watch_acquisition/v1", acquisition
        )
        if acquisition_identity == genesis["parent_watch_identity"]:
            if (
                watch["role"] != "ANCHOR_SELF_DIRECT"
                or watch["recursive"]
                or watch["watched_path_identity"]
                != genesis["campaign_parent_path_identity"]
            ):
                _refuse(f"{label} genesis parent watch targets another scope")
            parent_watch_match_count += 1
        watch_resource_values.extend(projection)
    if (
        recursive_count != 1
        or parent_watch_match_count != 1
        or len(set(watch_resource_values)) != len(watch_resource_values)
    ):
        _refuse(f"{label} requires one recursive watch and exclusive watch resources")
    if retained_values.intersection(watch_resource_values):
        _refuse(f"{label} anchor and watch handles overlap")
    for lock in locks:
        if (
            lock["share_mode"] != 1
            or not lock["locked_before_first_read"]
            or not lock["held_through_launch_handoff"]
        ):
            _refuse(f"{label} immutable file lock permits mutation or was acquired late")
    _validate_usn_range(record["usn_start_observation"], f"{label}.usn_start_observation")
    if not record["active_through_launch_handoff"]:
        _refuse(f"{label} does not remain active through launch handoff")


def _validate_root_release_semantics(
    record_value: Any,
    root_value: Any,
    ledger_value: Any | None,
    label: str,
) -> None:
    record = _mapping(record_value, label)
    root = _mapping(root_value, f"{label}.root")
    rows = record["watch_release_rows"]
    if type(rows) is not list or record["watch_release_count"] != len(rows) or len(rows) != root["watch_count"]:
        _refuse(f"{label} watch-release count differs")
    watches = root["watches"]
    for ordinal, (watch, released) in enumerate(zip(watches, rows, strict=True), 1):
        if released["watch_ordinal"] != ordinal:
            _refuse(f"{label} watch release ordinal differs")
        for acquired_field, release_field in (
            ("directory_handle_value_uint64", "directory_handle_value_uint64"),
            ("buffer_base_address_uint64", "buffer_base_address_uint64"),
            ("overlapped_address_uint64", "overlapped_address_uint64"),
            ("event_handle_value_uint64", "event_handle_value_uint64"),
        ):
            if watch[acquired_field] != released[release_field]:
                _refuse(f"{label} watch {ordinal} release substituted a resource")
        if (
            released["completion_bytes_output_input_bytes_base64"] != "AAAAAA=="
            or released["completion_bytes_output_input_sha256"] != _LEDGER_FIXED_ZERO_HASHES[4]
            or released["completion_last_error"] not in (0, 995)
            or released["completion_bytes_transferred"] < 0
            or not released["close_directory_returned_nonzero"]
            or not released["close_event_returned_nonzero"]
            or not released["free_overlapped_returned_nonzero"]
            or not released["free_buffer_returned_nonzero"]
            or not released["release_order_exact"]
        ):
            _refuse(f"{label} watch {ordinal} cancel-race/release closure differs")
    _validate_usn_range(record["final_usn_range"], f"{label}.final_usn_range")
    if (
        record["unmatched_watch_event_count"] != 0
        or record["unmatched_usn_record_count"] != 0
        or not record["all_resources_released_once"]
    ):
        _refuse(f"{label} leaves unmatched mutation evidence or retained resources")
    if ledger_value is not None:
        ledger = _mapping(ledger_value, f"{label}.ledger")
        if record["ledger_close_input_handle_value_uint64"] != ledger["ledger_handle_value_uint64"]:
            _refuse(f"{label} closes a substituted ledger handle")
    if record["ledger_close_api"] != "CloseHandle" or not record["ledger_close_returned_nonzero"]:
        _refuse(f"{label} ledger handle was not closed exactly once")


def validate_no_science_counters(counters: Mapping[str, Any]) -> None:
    """Require the exact fifteen authority counters, all integer zero."""

    record = _mapping(counters, "scientific_counters")
    _exact_fields(record, frozenset(_SCIENCE_COUNTER_NAMES), "scientific_counters")
    for name in _SCIENCE_COUNTER_NAMES:
        if type(record[name]) is not int or record[name] != 0:
            _refuse(f"scientific counter is nonzero or non-integer: {name}")
    # Keep the canonical half and this independently spelled check in agreement.
    assert_zero_science_counters(record)


def validate_stage_f_control_state_machine(
    records: Sequence[Mapping[str, Any]],
    validate_definition: Callable[[str, Any], None],
) -> dict[str, Any]:
    """Validate one chronological corrected Stage-F control epoch.

    The injected definition validator keeps this module schema-engine and
    import-cycle independent.  No I/O, Docker call, model import, RNG draw, or
    scientific action is reachable from this function.
    """

    if not callable(validate_definition):
        _refuse("control-state definition validator is not callable")
    if type(records) not in (list, tuple) or not records:
        _refuse("control-state records must be one nonempty chronological sequence")
    definitions: list[str] = []
    values: list[dict[str, Any]] = []
    singletons: dict[str, dict[str, Any]] = {}
    for ordinal, row_value in enumerate(records, 1):
        row = _mapping(row_value, f"control row {ordinal}")
        _exact_fields(row, _CONTROL_ROW_FIELDS, f"control row {ordinal}")
        definition = row["definition"]
        if type(definition) is not str or definition not in _CONTROL_ALLOWED_DEFINITIONS:
            if definition in _CONTROL_NESTED_ONLY_DEFINITIONS:
                _refuse(f"control row {ordinal} publishes nested-only {definition}")
            _refuse(f"control row {ordinal} definition is not authorized")
        record = _mapping(row["record"], f"control row {ordinal} record")
        validate_definition(definition, record)
        _validate_science_counters_recursively(record, f"control row {ordinal}")
        if definition in _CONTROL_SINGLETON_DEFINITIONS:
            if definition in singletons:
                _refuse(f"control-state repeats singleton {definition}")
            singletons[definition] = record
        if definition == "stage_f_ledger_create_observation":
            _validate_ledger_create_observation(record, f"control row {ordinal}")
        elif definition == "stage_f_evidence_ledger_append_observation":
            _validate_ledger_append_observation(record, f"control row {ordinal}")
        elif definition == "stage_f_usn_journal_range":
            _validate_usn_range(record, f"control row {ordinal}")
        elif definition == "stage_f_authorized_mutation_ticket":
            _validate_mutation_ticket_semantics(record, f"control row {ordinal}")
        elif definition in (
            "stage_f_capacity_publication_observation",
            "stage_f_capacity_consumption_closure",
        ):
            _validate_capacity_control_record(
                record, definition, f"control row {ordinal}"
            )
        definitions.append(definition)
        values.append(record)
    if definitions[0] != "stage_f_execution_attempt_genesis":
        _refuse("control-state does not begin with fresh attempt genesis")
    if len(definitions) < 2 or definitions[1] != "stage_f_root_protection_epoch":
        _refuse("root protection epoch is not immediately after fresh genesis")
    if "stage_f_root_protection_release" in singletons and definitions[-1] != "stage_f_root_protection_release":
        _refuse("root protection release is not the final control record")
    ledger_indexes = [
        index
        for index, definition in enumerate(definitions)
        if definition
        in ("stage_f_evidence_ledger_genesis", "stage_f_evidence_ledger_entry")
    ]
    if ledger_indexes:
        previous_identity: dict[str, Any] | None = None
        previous_append: dict[str, Any] | None = None
        previous_ordinal = -1
        ledger_projection: tuple[Any, ...] | None = None
        explicit_append_tickets_used: set[int] = set()
        mutation_ticket_rows = [
            (
                index,
                _embedded_record_identity(value, "ticket_sha256"),
            )
            for index, (definition, value) in enumerate(
                zip(definitions, values, strict=True)
            )
            if definition == "stage_f_authorized_mutation_ticket"
        ]
        for sequence_ordinal, index in enumerate(ledger_indexes):
            ledger_record = values[index]
            if index + 1 >= len(values) or definitions[index + 1] != "stage_f_evidence_ledger_append_observation":
                _refuse("each ledger genesis/entry must be immediately followed by its append observation")
            append = values[index + 1]
            ledger_identity = _embedded_record_identity(
                ledger_record, "ledger_sha256", kind="stage_f_evidence_ledger/v1"
            )
            if append["entry_identity"] != ledger_identity:
                _refuse("ledger append observation entry identity differs")
            append_ticket = _mapping(ledger_record["append_ticket"], "embedded ledger append ticket")
            verify_embedded_digest(append_ticket, "ticket_sha256")
            if append["append_ticket_sha256"] != append_ticket["ticket_sha256"]:
                _refuse("ledger append observation ticket SHA-256 differs")
            if index == 0 or definitions[index - 1] != "stage_f_ledger_append_ticket":
                _refuse("each ledger genesis/entry requires its preceding top-level append ticket")
            if values[index - 1] != append_ticket:
                _refuse("top-level and embedded ledger append tickets differ")
            explicit_append_tickets_used.add(index - 1)
            ordinal_value = ledger_record["ordinal"]
            if sequence_ordinal == 0:
                if (
                    definitions[index] != "stage_f_evidence_ledger_genesis"
                    or ordinal_value != 0
                    or ledger_record["previous_entry_identity"] is not None
                ):
                    _refuse("ledger chain does not begin with ordinal-zero genesis")
            else:
                if (
                    definitions[index] != "stage_f_evidence_ledger_entry"
                    or ordinal_value != previous_ordinal + 1
                    or ledger_record["previous_entry_identity"] != previous_identity
                    or ledger_record["previous_entry_append_observation"] != previous_append
                ):
                    _refuse("ledger predecessor ordinal/identity/append chain differs")
                mutation_identity = ledger_record["mutation_ticket_identity"]
                if not any(
                    ticket_index < index and identity == mutation_identity
                    for ticket_index, identity in mutation_ticket_rows
                ):
                    _refuse("ledger entry lacks its top-level authorized mutation ticket")
            prior_usn_indexes = [
                usn_index
                for usn_index in range(index)
                if definitions[usn_index] == "stage_f_usn_journal_range"
            ]
            if not prior_usn_indexes:
                _refuse("ledger record lacks a preceding closed USN range")
            latest_usn = values[prior_usn_indexes[-1]]
            if ledger_record["usn_range_sha256"] != hashlib.sha256(
                canonical_bytes(latest_usn)
            ).hexdigest():
                _refuse("ledger record does not bind the latest preceding USN range")
            current_projection = (
                ledger_record["ledger_file_path_identity"],
                ledger_record["ledger_file_volume_serial_number_uint64"],
                ledger_record["ledger_file_id_128"],
                ledger_record["ledger_handle_value_uint64"],
            )
            if ledger_projection is None:
                ledger_projection = current_projection
            elif current_projection != ledger_projection:
                _refuse("ledger chain substituted its continuously held file or handle")
            if (
                append["ledger_file_path_identity"],
                append["ledger_file_volume_serial_number_uint64"],
                append["ledger_file_id_128"],
                append["ledger_handle_value_uint64"],
            ) != ledger_projection:
                _refuse("ledger append observation substituted the held ledger")
            previous_identity = ledger_identity
            previous_append = append
            previous_ordinal = ordinal_value
        orphan_tickets = {
            index
            for index, definition in enumerate(definitions)
            if definition == "stage_f_ledger_append_ticket"
        } - explicit_append_tickets_used
        if orphan_tickets:
            _refuse("control-state contains an unpaired top-level ledger append ticket")
    elif any(
        definition
        in (
            "stage_f_evidence_ledger_append_observation",
            "stage_f_ledger_append_ticket",
            "stage_f_evidence_ledger_entry",
        )
        for definition in definitions
    ):
        _refuse("control-state contains ledger rows without ledger genesis")
    ordered_singletons = (
        "stage_f_evidence_ledger_genesis",
        "stage_f_capacity_publication_observation",
        "stage_f_capacity_consumption_closure",
        "stage_f_scientific_launch_gate",
        "stage_f_container_start_intent",
        "stage_f_container_start_receipt",
        "stage_f_root_protection_release",
    )
    previous = 1
    for definition in ordered_singletons:
        if definition in definitions:
            current = definitions.index(definition)
            if current <= previous:
                _refuse(f"control-state chronological order differs at {definition}")
            previous = current
    genesis = singletons["stage_f_execution_attempt_genesis"]
    root = singletons["stage_f_root_protection_epoch"]
    _validate_root_epoch_semantics(root, "root protection epoch")
    if root["execution_attempt_genesis"] != genesis:
        _refuse("root protection epoch does not embed the exact fresh genesis")
    genesis_identity = _embedded_record_identity(genesis, "genesis_sha256")
    root_identity = _embedded_record_identity(root, "epoch_sha256")
    mutation_tickets = [
        (
            index,
            value,
            _stage_f_ticket_identity(value),
        )
        for index, (definition, value) in enumerate(
            zip(definitions, values, strict=True)
        )
        if definition == "stage_f_authorized_mutation_ticket"
    ]
    for _index, ticket, _identity_value in mutation_tickets:
        if ticket["root_protection_epoch_identity"] != root_identity:
            _refuse("mutation ticket identifies another root-protection epoch")
    ledger_entry_identities = {
        canonical_bytes(
            _embedded_record_identity(
                value,
                "ledger_sha256",
                kind="stage_f_evidence_ledger/v1",
            )
        )
        for definition, value in zip(definitions, values, strict=True)
        if definition
        in ("stage_f_evidence_ledger_genesis", "stage_f_evidence_ledger_entry")
    }
    consumed_ticket_identities: set[bytes] = set()
    for range_index, (definition, usn_range) in enumerate(
        zip(definitions, values, strict=True)
    ):
        if definition != "stage_f_usn_journal_range":
            continue
        for usn_record in usn_range["records"]:
            if usn_record["scope_disposition"] != "AUTHORIZED_TICKET_MATCH":
                continue
            wanted = canonical_bytes(usn_record["mutation_ticket_identity"])
            matches = [
                (ticket_index, ticket)
                for ticket_index, ticket, identity_value in mutation_tickets
                if ticket_index < range_index
                and canonical_bytes(identity_value) == wanted
            ]
            if len(matches) != 1 or wanted in consumed_ticket_identities:
                _refuse(
                    "authorized USN record lacks one preceding unconsumed mutation ticket"
                )
            _ticket_index, ticket = matches[0]
            ledger_identity = canonical_bytes(
                usn_record["ledger_mutation_entry_identity"]
            )
            if (
                usn_record["mutation_transaction_identity"]
                != ticket["transaction_identity"]
                or usn_record["ledger_mutation_entry_identity"]
                != ticket["ledger_mutation_transaction_identity"]
                or ledger_identity not in ledger_entry_identities
            ):
                _refuse("mutation ticket/USN/ledger transaction bijection differs")
            consumed_ticket_identities.add(wanted)
    ledger = singletons.get("stage_f_evidence_ledger_genesis")
    if ledger is not None:
        _validate_ledger_create_observation(
            ledger["ledger_create_observation"], "ledger genesis create observation"
        )
        _same_identity(ledger["execution_attempt_genesis_identity"], genesis_identity, "ledger genesis/fresh attempt")
        _same_identity(ledger["root_protection_epoch_identity"], root_identity, "ledger genesis/root epoch")
    dependent = (
        "stage_f_capacity_publication_observation",
        "stage_f_capacity_consumption_closure",
        "stage_f_scientific_launch_gate",
        "stage_f_container_start_intent",
        "stage_f_container_start_receipt",
    )
    if any(name in singletons for name in dependent) and ledger is None:
        _refuse("control-state advances without a held append-only ledger genesis")
    for definition in dependent:
        record = singletons.get(definition)
        if record is None:
            continue
        field = "receipt_root_protection_epoch_identity" if definition == "stage_f_container_start_receipt" else "root_protection_epoch_identity"
        _same_identity(record[field], root_identity, f"{definition}/root epoch")
    publication = singletons.get("stage_f_capacity_publication_observation")
    closure = singletons.get("stage_f_capacity_consumption_closure")
    if closure is not None:
        if publication is None:
            _refuse("capacity consumption closure lacks its publication")
        publication_identity = _embedded_record_identity(publication, "publication_sha256", kind="stage_f_capacity_publication_observation/v1")
        _same_identity(closure["capacity_publication_identity"], publication_identity, "capacity closure/publication")
    gate = singletons.get("stage_f_scientific_launch_gate")
    inert: dict[str, Any] | None = None
    if gate is not None:
        if closure is None:
            _refuse("scientific launch gate lacks capacity closure")
        inert = _mapping(
            gate["inert_container_observation"], "launch gate inert container"
        )
        closure_identity = _embedded_record_identity(closure, "closure_sha256", kind="stage_f_capacity_consumption_closure/v1")
        inert_identity = _embedded_record_identity(inert, "container_observation_sha256", kind="stage_f_inert_container/v1")
        _same_identity(gate["capacity_consumption_closure_identity"], closure_identity, "launch gate/capacity closure")
        _same_identity(gate["inert_container_identity"], inert_identity, "launch gate/inert container")
    intent = singletons.get("stage_f_container_start_intent")
    capability: dict[str, Any] | None = None
    if intent is not None:
        if gate is None or inert is None:
            _refuse("container start intent lacks gate, capability, or inert container")
        capability = _mapping(
            intent["container_start_capability"], "start intent capability"
        )
        gate_identity = _embedded_record_identity(gate, "gate_sha256", kind="stage_f_scientific_launch_gate/v1")
        capability_identity = _embedded_record_identity(capability, "capability_sha256", kind="stage_f_container_start_capability/v1")
        inert_identity = _embedded_record_identity(inert, "container_observation_sha256", kind="stage_f_inert_container/v1")
        _same_identity(intent["scientific_launch_gate_identity"], gate_identity, "start intent/launch gate")
        _same_identity(intent["container_start_capability_identity"], capability_identity, "start intent/capability")
        _same_identity(intent["inert_container_identity"], inert_identity, "start intent/inert container")
        if intent["inert_container_observation"] != inert:
            _refuse("start intent does not embed the exact inert container observation")
    receipt = singletons.get("stage_f_container_start_receipt")
    if receipt is not None:
        if intent is None:
            _refuse("container start receipt lacks durable start intent")
        intent_identity = _embedded_record_identity(intent, "intent_sha256", kind="stage_f_container_start_intent/v1")
        _same_identity(receipt["container_start_intent_identity"], intent_identity, "start receipt/intent")
        expected_container_id = intent["inert_container_observation"]["container_id"]
        if receipt.get("container_id") != expected_container_id:
            _refuse("container start receipt identifies another container")
        for exchange_field in (
            "start_exchange",
            "recovery_inspect_exchange",
            "emergency_force_remove_exchange",
            "final_absence_inspect_exchange",
        ):
            exchange = receipt.get(exchange_field)
            if exchange is None:
                continue
            endpoint = exchange.get("endpoint")
            expected_endpoint = {
                "start_exchange": f"/containers/{expected_container_id}/start",
                "recovery_inspect_exchange": f"/containers/{expected_container_id}/json",
                "emergency_force_remove_exchange": f"/containers/{expected_container_id}?force=true&v=false",
                "final_absence_inspect_exchange": f"/containers/{expected_container_id}/json",
            }[exchange_field]
            if endpoint != expected_endpoint:
                _refuse(f"container receipt {exchange_field} targets another container")
        docker_exchanges = [
            receipt[field]
            for field in (
                "start_exchange",
                "recovery_inspect_exchange",
                "emergency_force_remove_exchange",
                "final_absence_inspect_exchange",
            )
            if receipt.get(field) is not None
        ]
        if docker_exchanges:
            _validate_docker_exchange_sequence(
                docker_exchanges, "container start receipt connections"
            )
        if receipt.get("start_attempt") is not None:
            _validate_docker_start_attempt(receipt["start_attempt"], "container start receipt attempt")
        if receipt["classification"] != "NORMAL_RESPONSE_204" and (
            not receipt["emergency_force_remove_required"]
            or not receipt["emergency_force_remove_completed"]
            or receipt["final_absence_inspect_exchange"] is None
            or not receipt["container_absent_after_containment"]
            or not receipt["container_and_attempt_permanently_quarantined"]
        ):
            _refuse("non-normal start receipt lacks force-removal/404 quarantine closure")
    ledgered_roots = (
        (
            "stage_f_capacity_publication_observation",
            "CAPACITY_PUBLICATION",
            "publication_sha256",
            "stage_f_capacity_publication_observation/v1",
        ),
        (
            "stage_f_capacity_consumption_closure",
            "CAPACITY_CONSUMPTION_CLOSURE",
            "closure_sha256",
            "stage_f_capacity_consumption_closure/v1",
        ),
        (
            "stage_f_scientific_launch_gate",
            "LAUNCH_GATE",
            "gate_sha256",
            "stage_f_scientific_launch_gate/v1",
        ),
        (
            "stage_f_container_start_intent",
            "CONTAINER_START_INTENT",
            "intent_sha256",
            "stage_f_container_start_intent/v1",
        ),
        (
            "stage_f_container_start_receipt",
            "CONTAINER_START_RECEIPT",
            "receipt_sha256",
            "stage_f_container_start_receipt/v1",
        ),
    )
    for definition, role, digest_field, kind in ledgered_roots:
        published = singletons.get(definition)
        if published is None:
            continue
        published_index = definitions.index(definition)
        published_identity = _embedded_record_identity(
            published, digest_field, kind=kind
        )
        matching_entry_indexes = [
            index
            for index, (entry_definition, entry) in enumerate(
                zip(definitions, values, strict=True)
            )
            if entry_definition == "stage_f_evidence_ledger_entry"
            and entry["record_role"] == role
            and entry["record_identity"] == published_identity
        ]
        if len(matching_entry_indexes) != 1 or matching_entry_indexes[0] <= published_index:
            _refuse(f"{definition} lacks one later exact ledger entry/append chain")
    release = singletons.get("stage_f_root_protection_release")
    if release is not None:
        _same_identity(release["root_protection_epoch_identity"], root_identity, "root release/epoch")
        _validate_root_release_semantics(
            release, root, ledger, "root protection release"
        )
        if not release["all_resources_released_once"]:
            _refuse("root protection release does not close every resource once")
    if release is not None:
        phase = "CONTROL_EPOCH_RELEASED"
    elif receipt is not None:
        phase = "CONTAINER_START_RECEIPT_RECORDED"
    elif intent is not None:
        phase = "PRESTART_INTENT_DURABLE"
    elif closure is not None:
        phase = "CAPACITY_CONSUMPTION_CLOSED"
    elif ledger is not None:
        phase = "ROOT_LEDGER_EPOCH_ACTIVE"
    else:
        phase = "ROOT_EPOCH_ACTIVE"
    return {
        "schema": "stage_f_corrected_control_state_validation/v1",
        "phase": phase,
        "record_count": len(records),
        "last_definition": definitions[-1],
        "root_protection_epoch_identity": root_identity,
        "scientific_counters": dict(ZERO_SCIENCE_COUNTERS),
        "disposition": "VALIDATED_OUTCOME_BLIND_CONTROL_STATE",
    }


def execute_stage_f_prestart_controller(
    plan: Mapping[str, Any],
    validate_definition: Callable[[str, Any], None],
) -> dict[str, Any]:
    """Freeze a nested pre-call handoff and stop before Docker start/science."""

    plan = _mapping(plan, "Stage F prestart controller plan")
    _exact_fields(plan, frozenset(("control_records", "scientific_launch_handoff", "scientific_counters")), "Stage F prestart controller plan")
    validate_no_science_counters(_mapping(plan["scientific_counters"], "prestart counters"))
    state = validate_stage_f_control_state_machine(plan["control_records"], validate_definition)
    if state["phase"] != "PRESTART_INTENT_DURABLE":
        _refuse("prestart controller requires one durable unsent container-start intent")
    handoff = _mapping(plan["scientific_launch_handoff"], "scientific launch handoff")
    validate_definition("stage_f_scientific_launch_handoff", handoff)
    _validate_science_counters_recursively(handoff, "scientific launch handoff")
    _validate_capacity_control_record(
        handoff["final_prestart_capacity_live_gate"],
        "stage_f_capacity_live_gate",
        "scientific launch handoff final capacity gate",
    )
    _validate_host_prerequisite_snapshot(
        handoff["host_prerequisite_snapshot"],
        "scientific launch handoff host prerequisites",
    )
    by_definition = {row["definition"]: row["record"] for row in plan["control_records"]}
    intent = by_definition["stage_f_container_start_intent"]
    gate = by_definition["stage_f_scientific_launch_gate"]
    capability = _mapping(
        intent["container_start_capability"], "start intent capability"
    )
    root = by_definition["stage_f_root_protection_epoch"]
    final_gate = _mapping(
        handoff["final_prestart_capacity_live_gate"], "handoff final capacity gate"
    )
    host_snapshot = _mapping(
        handoff["host_prerequisite_snapshot"], "handoff host prerequisites"
    )
    intent_append = _mapping(
        handoff["container_start_intent_ledger_append_observation"],
        "handoff intent append observation",
    )
    launch_gate_append = _mapping(
        handoff["launch_gate_ledger_entry_live_observation"],
        "handoff launch-gate live append observation",
    )
    live_watch = _mapping(handoff["root_watch_live_state"], "handoff root-watch live state")
    _validate_root_watch_live_state_links(
        live_watch, root, "handoff root-watch live state"
    )
    _same_identity(handoff["root_protection_epoch_identity"], _embedded_record_identity(root, "epoch_sha256"), "handoff/root epoch")
    _same_identity(handoff["container_start_intent_identity"], _embedded_record_identity(intent, "intent_sha256", kind="stage_f_container_start_intent/v1"), "handoff/start intent")
    _same_identity(handoff["scientific_launch_gate_identity"], _embedded_record_identity(gate, "gate_sha256", kind="stage_f_scientific_launch_gate/v1"), "handoff/launch gate")
    _same_identity(handoff["container_start_capability_identity"], _embedded_record_identity(capability, "capability_sha256", kind="stage_f_container_start_capability/v1"), "handoff/start capability")
    if handoff["container_start_intent"] != intent or handoff["container_start_capability"] != capability:
        _refuse("handoff embedded intent or capability differs")
    live_watch_identity = _embedded_record_identity(
        live_watch,
        "live_state_sha256",
        kind="stage_f_root_watch_live_state/v1",
    )
    if (
        handoff["container_observation"] != gate["inert_container_observation"]
        or handoff["container_observation"] != intent["inert_container_observation"]
        or handoff["root_watch_live_state_identity"] != live_watch_identity
        or live_watch["root_protection_epoch_identity"]
        != handoff["root_protection_epoch_identity"]
        or live_watch["watch_count"] != root["watch_count"]
        or live_watch["pending_watch_ordinals"]
        != list(range(1, root["watch_count"] + 1))
        or not live_watch["all_acquired_watches_pending"]
        or live_watch["unmatched_protected_event_count"] != 0
    ):
        _refuse("handoff container or pending root-watch live state differs")
    if (
        intent_append["entry_identity"] != handoff["evidence_ledger_predecessor_identity"]
        or host_snapshot["evidence_ledger_predecessor_identity"]
        != handoff["evidence_ledger_predecessor_identity"]
        or host_snapshot["evidence_ledger_predecessor_append_observation"]
        != intent_append
        or final_gate["evidence_ledger_predecessor_identity"]
        != handoff["evidence_ledger_predecessor_identity"]
        or final_gate["evidence_ledger_predecessor_append_observation"]
        != intent_append
        or launch_gate_append
        != intent["evidence_ledger_predecessor_append_observation"]
        or launch_gate_append["entry_identity"]
        != intent["evidence_ledger_predecessor_identity"]
    ):
        _refuse("handoff fresh host/capacity gates are not tied to the live intent head")
    capability_identity = _embedded_record_identity(
        capability,
        "capability_sha256",
        kind="stage_f_container_start_capability/v1",
    )
    if (
        final_gate["gate_role"] != "SCIENTIFIC_CONTAINER_START"
        or final_gate["exact_following_operation_capability_identity"]
        != capability_identity
        or not handoff["host_prerequisite_snapshot_remeasured_after_intent_append"]
        or not handoff["final_prestart_capacity_live_gate_completed_after_fresh_host_snapshot"]
    ):
        _refuse("handoff final gate does not immediately authorize the exact start capability")
    if (
        handoff["start_api"] != "DOCKER_ENGINE_CONTAINER_START"
        or not handoff["start_authorized"]
        or handoff["started_utc"] is not None
        or not handoff["handoff_preimage_frozen_before_start_call"]
        or not handoff["handoff_sha256_computed_before_start_call"]
        or not handoff["start_call_not_yet_invoked"]
        or not handoff["handoff_held_in_controller_memory_through_exact_start_call"]
        or not handoff["post_call_container_start_receipt_required"]
    ):
        _refuse("scientific launch handoff is not the exact frozen pre-call state")
    handoff_identity = _embedded_record_identity(handoff, "handoff_sha256", kind="stage_f_scientific_launch_handoff/v1")
    return {
        "schema": "stage_f_prestart_controller_result/v1",
        "control_state_validation": state,
        "scientific_launch_handoff_identity": handoff_identity,
        "scientific_launch_handoff": handoff,
        "scientific_counters": dict(ZERO_SCIENCE_COUNTERS),
        "disposition": "PRESTART_HANDOFF_FROZEN_SCIENCE_NOT_EXECUTED",
    }


_LIVE_PRESTART_OPERATION_NAMES = frozenset(
    (
        "incept_fresh_attempt_root",
        "acquire_root_and_volume_epoch",
        "read_locked_authority_materials",
        "create_held_ledger",
        "launch_suspended_validator",
        "complete_outcome_blind_authorization_chain",
        "publish_capacity_snapshot",
        "close_capacity_consumption",
        "attest_host_docker_and_create_inert_container",
        "publish_durable_start_intent",
        "freeze_uninvoked_handoff",
        "abort_without_start",
    )
)
_LIVE_PHASE_RESULT_FIELDS = frozenset(
    ("state_token", "control_records", "observation", "scientific_counters")
)
_LIVE_PHASES = (
    (
        "incept_fresh_attempt_root",
        "stage_f_execution_attempt_genesis",
        "fresh_directory_created_once",
    ),
    (
        "acquire_root_and_volume_epoch",
        "stage_f_root_protection_epoch",
        "root_volume_handles_watches_and_usn_retained",
    ),
    (
        "read_locked_authority_materials",
        None,
        "private_materials_read_only_after_root_protection_started",
    ),
    (
        "create_held_ledger",
        "stage_f_evidence_ledger_genesis",
        "ledger_create_new_handle_retained_and_genesis_appended",
    ),
    (
        "publish_capacity_snapshot",
        "stage_f_capacity_publication_observation",
        "capacity_snapshot_published_and_ledgered",
    ),
    (
        "close_capacity_consumption",
        "stage_f_capacity_consumption_closure",
        "capacity_consumption_closed_and_ledgered",
    ),
    (
        "launch_suspended_validator",
        None,
        "validator_attested_before_resume_and_returned_outcome_blind",
    ),
    (
        "complete_outcome_blind_authorization_chain",
        None,
        "validation_readiness_audit_packet_user_and_campaign_authority_ledgered",
    ),
    (
        "attest_host_docker_and_create_inert_container",
        "stage_f_scientific_launch_gate",
        "host_docker_inert_container_gate_published_and_ledgered",
    ),
    (
        "publish_durable_start_intent",
        "stage_f_container_start_intent",
        "start_intent_durable_before_fresh_precall_gates",
    ),
)


_WINDOWS_STAGE_F_PHASE_HELPERS: dict[str, Callable[..., Any]] = {}


def _windows_stage_f_backend_not_implemented(phase: str, **_kwargs: Any) -> Any:
    _refuse(
        "corrected Windows Stage F backend helper is not yet implemented for "
        f"{phase}; refusing before host mutation or scientific start"
    )


class WindowsStageFPrestartBackend:
    """Concrete Win32 backend router for the corrected prestart controller.

    Construction is side-effect free.  Each operation resolves a dedicated
    module helper at call time, which keeps synthetic tests injectable while a
    production call still uses only this module's audited ctypes mechanisms.
    There is intentionally no container-start method.
    """

    __slots__ = ()

    @staticmethod
    def _invoke(phase: str, **kwargs: Any) -> Any:
        if sys.platform != "win32" or ctypes.sizeof(ctypes.c_void_p) != 8:
            _refuse("corrected Stage F live backend requires 64-bit Win32")
        helper = _WINDOWS_STAGE_F_PHASE_HELPERS.get(phase)
        if helper is None:
            return _windows_stage_f_backend_not_implemented(phase, **kwargs)
        return helper(**kwargs)

    def operations(self) -> dict[str, Callable[..., Any]]:
        return {
            name: (
                lambda _name=name, **kwargs: self._invoke(_name, **kwargs)
            )
            for name in _LIVE_PRESTART_OPERATION_NAMES
        }


def _live_phase_result(value: Any, phase: str) -> dict[str, Any]:
    result = _mapping(value, f"live prestart {phase} result")
    _exact_fields(result, _LIVE_PHASE_RESULT_FIELDS, f"live prestart {phase} result")
    validate_no_science_counters(
        _mapping(result["scientific_counters"], f"live prestart {phase} counters")
    )
    rows = result["control_records"]
    if type(rows) is not list:
        _refuse(f"live prestart {phase} control records are not a list")
    observation = _mapping(result["observation"], f"live prestart {phase} observation")
    _validate_science_counters_recursively(observation, f"live prestart {phase} observation")
    if result["state_token"] is None:
        _refuse(f"live prestart {phase} did not retain its resource-state token")
    return result


class StageFPrestartControllerSession:
    """One live corrected handle epoch stopped immediately before Docker start.

    The session intentionally exposes no start method.  Its opaque state token
    is retained only so the backend can release all Win32 handles after the
    caller abandons the uninvoked handoff or transfers it to the separately
    authorized start controller.
    """

    __slots__ = (
        "control_records",
        "prestart_result",
        "phase_trace",
        "_abort",
        "_validate_definition",
        "_state_token",
        "_closed",
    )

    def __init__(
        self,
        *,
        control_records: Sequence[Mapping[str, Any]],
        prestart_result: Mapping[str, Any],
        phase_trace: Sequence[str],
        abort: Callable[..., Any],
        validate_definition: Callable[[str, Any], None],
        state_token: Any,
    ) -> None:
        self.control_records = tuple(dict(row) for row in control_records)
        self.prestart_result = dict(prestart_result)
        self.phase_trace = tuple(phase_trace)
        self._abort = abort
        self._validate_definition = validate_definition
        self._state_token = state_token
        self._closed = False

    @property
    def closed(self) -> bool:
        return self._closed

    def abort_without_start(self) -> dict[str, Any]:
        if self._closed:
            _refuse("live prestart session resources were already released")
        result = _complete_live_prestart_abort(
            self._abort(
                state_token=self._state_token,
                control_records=self.control_records,
                reason="PRESTART_HANDOFF_ABANDONED_WITHOUT_START",
            ),
            existing_records=self.control_records,
            state_token=self._state_token,
            validate_definition=self._validate_definition,
            require_precall_receipt=True,
        )
        self._closed = True
        self._state_token = None
        return result


def _complete_live_prestart_abort(
    value: Any,
    *,
    existing_records: Sequence[Mapping[str, Any]],
    state_token: Any,
    validate_definition: Callable[[str, Any], None],
    require_precall_receipt: bool,
) -> dict[str, Any]:
    result = _mapping(value, "live prestart abort result")
    _exact_fields(
        result,
        frozenset(("state_token", "control_records", "scientific_counters", "observation")),
        "live prestart abort result",
    )
    if result["state_token"] is not state_token:
        _refuse("live prestart abort substituted the retained resource epoch")
    validate_no_science_counters(
        _mapping(result["scientific_counters"], "live prestart abort counters")
    )
    observation = _mapping(result["observation"], "live prestart abort observation")
    if (
        observation.get("all_resources_released_once") is not True
        or observation.get("start_call_count") != 0
        or observation.get("same_live_start_writefile_never_invoked") is not True
    ):
        _refuse("live prestart abort lacks exact no-start resource closure")
    appended = result["control_records"]
    if type(appended) is not list:
        _refuse("live prestart abort records are not a list")
    combined = [dict(row) for row in existing_records]
    combined.extend(dict(row) for row in appended)
    definitions = [row.get("definition") for row in appended if isinstance(row, Mapping)]
    if definitions.count("stage_f_root_protection_release") != 1:
        _refuse("live prestart abort lacks one final root-protection release")
    if require_precall_receipt:
        if definitions.count("stage_f_container_start_receipt") != 1:
            _refuse("post-intent live abort lacks one durable typed start receipt")
        receipt = next(
            row["record"]
            for row in appended
            if row.get("definition") == "stage_f_container_start_receipt"
        )
        if (
            receipt.get("classification") != "PRECALL_ABANDONED_UNSENT"
            or receipt.get("same_live_controller_proves_start_writefile_never_invoked")
            is not True
            or receipt.get("start_may_have_occurred") is not False
        ):
            _refuse("live prestart abort receipt does not prove precall abandonment")
    state = validate_stage_f_control_state_machine(combined, validate_definition)
    if state["phase"] != "CONTROL_EPOCH_RELEASED":
        _refuse("live prestart abort did not durably receipt then release its epoch")
    return {
        **result,
        "control_state_validation": state,
        "all_control_records": combined,
    }


def execute_stage_f_live_prestart_controller(
    plan: Mapping[str, Any],
    validate_definition: Callable[[str, Any], None],
    operations: Mapping[str, Callable[..., Any]],
) -> StageFPrestartControllerSession:
    """Run the corrected live control phases and stop at an uninvoked handoff.

    ``operations`` is the narrow Win32 backend boundary.  Every operation must
    perform its named primitive and return the resulting authority records plus
    the *same* opaque resource token.  This controller never accepts a Docker
    start callback, so neither scientific container start nor user code is
    reachable here.
    """

    plan = _mapping(plan, "live Stage F prestart plan")
    _exact_fields(
        plan,
        frozenset(("controller_input", "scientific_counters")),
        "live Stage F prestart plan",
    )
    validate_no_science_counters(
        _mapping(plan["scientific_counters"], "live prestart plan counters")
    )
    controller_input = _mapping(plan["controller_input"], "live prestart controller input")
    operations = _mapping(operations, "live prestart operations")
    _exact_fields(operations, _LIVE_PRESTART_OPERATION_NAMES, "live prestart operations")
    for name in _LIVE_PRESTART_OPERATION_NAMES:
        if not callable(operations[name]):
            _refuse(f"live prestart operation is not callable: {name}")

    rows: list[dict[str, Any]] = []
    trace: list[str] = []
    state_token: Any = None
    root_active = False
    try:
        for phase, required_definition, predicate in _LIVE_PHASES:
            result = _live_phase_result(
                operations[phase](
                    controller_input=controller_input,
                    state_token=state_token,
                    control_records=tuple(rows),
                ),
                phase,
            )
            if state_token is not None and result["state_token"] is not state_token:
                _refuse(f"live prestart {phase} substituted the retained resource epoch")
            state_token = result["state_token"]
            observation = result["observation"]
            if observation.get(predicate) is not True:
                _refuse(f"live prestart {phase} did not prove {predicate}")
            if phase == "incept_fresh_attempt_root":
                if (
                    observation.get("parent_watch_pending_before_absence_check") is not True
                    or observation.get("ancestor_parent_volume_protection_before_create")
                    is not True
                    or observation.get("direct_watch_count", 0) < 1
                    or observation.get("recursive_watch_count") != 1
                    or observation.get("all_watches_pending") is not True
                    or observation.get("usn_start_query_complete") is not True
                    or observation.get("private_byte_read_count_before_genesis") != 0
                ):
                    _refuse(
                        "attempt-root inception was not parent/volume protected, "
                        "USN-started, watched, and byte-zero"
                    )
                root_active = True
            elif phase == "acquire_root_and_volume_epoch":
                if (
                    not root_active
                    or observation.get("direct_watch_count", 0) < 1
                    or observation.get("recursive_watch_count") != 1
                    or observation.get("all_watches_pending") is not True
                    or observation.get("usn_start_query_complete") is not True
                    or observation.get(
                        "private_byte_read_count_before_root_protection_start"
                    )
                    != 0
                    or type(observation.get("immutable_file_lock_count")) is not int
                    or observation["immutable_file_lock_count"] <= 0
                ):
                    _refuse(
                        "root/volume epoch was not started byte-zero and completed "
                        "with pending watches, USN, and immutable held-file evidence"
                    )
                root_active = True
            elif phase == "read_locked_authority_materials":
                if (
                    not root_active
                    or observation.get("all_consumed_files_locked_before_read") is not True
                    or observation.get("all_file_handles_retained") is not True
                    or type(observation.get("private_material_count")) is not int
                    or observation["private_material_count"] <= 0
                ):
                    _refuse("authority material read escaped the active retained root epoch")
            elif phase == "launch_suspended_validator":
                host_snapshot = _mapping(
                    observation.get("fresh_host_prerequisite_snapshot"),
                    "live suspended validator host prerequisites",
                )
                validate_definition("stage_f_host_prerequisite_snapshot", host_snapshot)
                _validate_host_prerequisite_snapshot(
                    host_snapshot, "live suspended validator host prerequisites"
                )
                live_gate = _mapping(
                    observation.get("final_capacity_live_gate"),
                    "live suspended validator capacity gate",
                )
                validate_definition("stage_f_capacity_live_gate", live_gate)
                _validate_capacity_control_record(
                    live_gate,
                    "stage_f_capacity_live_gate",
                    "live suspended validator capacity gate",
                )
                if (
                    live_gate.get("gate_role") != "HOST_VALIDATION_PROCESS_RESUME"
                    or live_gate.get("no_intervening_controller_capacity_affecting_operation")
                    is not True
                    or live_gate.get("exact_following_operation_capability_identity")
                    != observation.get("resume_capability_identity")
                    or observation.get("host_snapshot_completed_immediately_before_resume")
                    is not True
                ):
                    _refuse(
                        "suspended validator lacks immediate host/capacity gates bound "
                        "to its exact ResumeThread capability"
                    )
                launch = _mapping(
                    observation.get("process_launch_observation"),
                    "live suspended validator launch",
                )
                validate_definition("durability_process_launch_observation", launch)
                actor_pid = _uint(
                    observation.get("controller_process_id"),
                    32,
                    "live suspended validator controller PID",
                    positive=True,
                )
                _validate_launch(launch, "ORCHESTRATOR", actor_pid)
                if (
                    observation.get("user_code_executed_before_attestation") is not False
                    or observation.get("root_watch_or_usn_gap") is not False
                ):
                    _refuse("validator process was not suspended-attested inside the epoch")
            elif phase == "complete_outcome_blind_authorization_chain":
                authorization_rows = observation.get("ordered_authorization_records")
                expected_authorization_definitions = (
                    "binding_validation_receipt",
                    "binding_readiness_record",
                    "independent_binding_audit_receipt",
                    "sealed_campaign_packet_manifest",
                    "post_packet_user_authorization_receipt",
                    "campaign_authorization",
                )
                if (
                    type(authorization_rows) is not list
                    or tuple(
                        row.get("definition")
                        for row in authorization_rows
                        if isinstance(row, Mapping)
                    )
                    != expected_authorization_definitions
                    or observation.get("all_authorization_records_published_and_ledgered")
                    is not True
                    or observation.get("root_epoch_continuous_through_user_receipt")
                    is not True
                ):
                    _refuse("same-epoch validation/audit/packet/user authority chain differs")
                for offset, external_row_value in enumerate(authorization_rows, 1):
                    external_row = _mapping(
                        external_row_value,
                        f"live authorization record {offset}",
                    )
                    _exact_fields(
                        external_row,
                        _CONTROL_ROW_FIELDS,
                        f"live authorization record {offset}",
                    )
                    validate_definition(
                        external_row["definition"], external_row["record"]
                    )
                    _validate_science_counters_recursively(
                        external_row["record"],
                        f"live authorization record {offset}",
                    )

            phase_rows = result["control_records"]
            if required_definition is None and phase not in (
                "launch_suspended_validator",
                "complete_outcome_blind_authorization_chain",
            ) and phase_rows:
                _refuse(f"live prestart {phase} returned unauthorized control records")
            if required_definition is not None and sum(
                row.get("definition") == required_definition
                for row in phase_rows
                if isinstance(row, Mapping)
            ) != 1:
                _refuse(f"live prestart {phase} lacks one {required_definition}")
            for offset, row_value in enumerate(phase_rows, 1):
                row = _mapping(row_value, f"live prestart {phase} row {offset}")
                _exact_fields(
                    row, _CONTROL_ROW_FIELDS, f"live prestart {phase} row {offset}"
                )
                validate_definition(row["definition"], row["record"])
                _validate_science_counters_recursively(
                    row["record"], f"live prestart {phase} row {offset}"
                )
            rows.extend(dict(row) for row in phase_rows)
            if len(rows) >= 2:
                validate_stage_f_control_state_machine(rows, validate_definition)
            trace.append(phase)

        frozen = _mapping(
            operations["freeze_uninvoked_handoff"](
                controller_input=controller_input,
                state_token=state_token,
                control_records=tuple(rows),
            ),
            "live prestart frozen handoff result",
        )
        _exact_fields(
            frozen,
            frozenset(("state_token", "handoff", "observation", "scientific_counters")),
            "live prestart frozen handoff result",
        )
        validate_no_science_counters(
            _mapping(frozen["scientific_counters"], "live frozen handoff counters")
        )
        if frozen["state_token"] is not state_token:
            _refuse("live prestart handoff substituted the retained resource epoch")
        handoff_observation = _mapping(
            frozen["observation"], "live prestart handoff observation"
        )
        if (
            handoff_observation.get("all_resources_retained") is not True
            or handoff_observation.get("start_call_count") != 0
            or handoff_observation.get("scientific_process_count") != 0
        ):
            _refuse("live prestart handoff crossed or released the start boundary")
        prestart = execute_stage_f_prestart_controller(
            {
                "control_records": rows,
                "scientific_launch_handoff": frozen["handoff"],
                "scientific_counters": dict(ZERO_SCIENCE_COUNTERS),
            },
            validate_definition,
        )
        trace.append("freeze_uninvoked_handoff")
        return StageFPrestartControllerSession(
            control_records=rows,
            prestart_result=prestart,
            phase_trace=trace,
            abort=operations["abort_without_start"],
            validate_definition=validate_definition,
            state_token=state_token,
        )
    except BaseException as primary:
        if state_token is not None:
            try:
                cleanup_value = operations["abort_without_start"](
                    state_token=state_token,
                    control_records=tuple(rows),
                    reason="PRESTART_CONTROLLER_FAILURE",
                )
                if len(rows) >= 2:
                    _complete_live_prestart_abort(
                        cleanup_value,
                        existing_records=rows,
                        state_token=state_token,
                        validate_definition=validate_definition,
                        require_precall_receipt=any(
                            row.get("definition") == "stage_f_container_start_intent"
                            for row in rows
                        ),
                    )
            except BaseException as cleanup:
                if hasattr(primary, "add_note"):
                    primary.add_note(
                        f"cleanup failure preserved after primary refusal: {cleanup!r}"
                    )
        raise


# Corrected Stage-F raw-USN backend.  This block is deliberately isolated from
# the legacy durability probe and contains no scientific callback or RNG path.
_STAGE_F_FSCTL_GET_NTFS_VOLUME_DATA = 589924
_STAGE_F_FSCTL_QUERY_USN_JOURNAL = 590068
_STAGE_F_FSCTL_READ_USN_JOURNAL = 590011
_STAGE_F_USN_QUERY_BYTES = 80
_STAGE_F_USN_READ_INPUT_BYTES = 48


class _StageFWindowsUsnApis:
    """Thin, injectable Win32 surface used by :class:`StageFUsnJournalBackend`."""

    def __init__(self) -> None:
        if sys.platform != "win32":
            _refuse("raw Stage F USN collection requires Win32")
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        self.create_file = kernel32.CreateFileW
        self.create_file.argtypes = (
            ctypes.c_wchar_p,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_void_p,
        )
        self.create_file.restype = ctypes.c_void_p
        self.get_volume_information_by_handle = (
            kernel32.GetVolumeInformationByHandleW
        )
        self.get_volume_information_by_handle.argtypes = (
            ctypes.c_void_p,
            ctypes.c_wchar_p,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.c_wchar_p,
            ctypes.c_uint32,
        )
        self.get_volume_information_by_handle.restype = ctypes.c_int
        self.device_io_control = kernel32.DeviceIoControl
        self.device_io_control.argtypes = (
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.c_void_p,
        )
        self.device_io_control.restype = ctypes.c_int
        self.close_handle = kernel32.CloseHandle
        self.close_handle.argtypes = (ctypes.c_void_p,)
        self.close_handle.restype = ctypes.c_int

    @staticmethod
    def last_error() -> int:
        return int(ctypes.get_last_error())


def _stage_f_usn_utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace(
        "+00:00", "Z"
    )


def _stage_f_usn_timestamp(clock: Callable[[], str], label: str) -> str:
    value = clock()
    _utc(value, label)
    return value


def _stage_f_usn_handle_value(value: Any) -> int:
    raw = value.value if isinstance(value, ctypes.c_void_p) else value
    return _handle(raw, "Stage F retained USN volume handle")


def _stage_f_usn_raw_at(address: int, byte_count: int) -> bytes:
    if address <= 0 or byte_count < 0:
        _refuse("raw Stage F USN buffer address or byte count is invalid")
    return ctypes.string_at(address, byte_count)


def _stage_f_usn_sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _stage_f_usn_b64(raw: bytes) -> str:
    return base64.b64encode(raw).decode("ascii")


def _stage_f_usn_decode_filesystem(raw: bytes) -> str:
    terminal = None
    for offset in range(0, len(raw), 2):
        if raw[offset : offset + 2] == b"\x00\x00":
            terminal = offset
            break
    if terminal is None:
        _refuse("GetVolumeInformationByHandleW filesystem output lacks a terminator")
    try:
        return raw[:terminal].decode("utf-16le", "strict")
    except UnicodeDecodeError as exc:
        raise BindingRefusal(
            "GetVolumeInformationByHandleW filesystem output is not strict UTF-16LE"
        ) from exc


def _stage_f_usn_ntfs_projection(value: _NTFS_VOLUME_DATA_BUFFER) -> dict[str, Any]:
    projection = {
        "query_succeeded": True,
        "volume_serial_number": int(value.VolumeSerialNumber),
        "number_sectors": int(value.NumberSectors),
        "total_clusters": int(value.TotalClusters),
        "free_clusters": int(value.FreeClusters),
        "total_reserved_clusters": int(value.TotalReserved),
        "bytes_per_sector": int(value.BytesPerSector),
        "bytes_per_cluster": int(value.BytesPerCluster),
        "bytes_per_file_record_segment": int(value.BytesPerFileRecordSegment),
        "clusters_per_file_record_segment": int(value.ClustersPerFileRecordSegment),
        "mft_valid_data_length": int(value.MftValidDataLength),
        "mft_start_lcn": int(value.MftStartLcn),
        "mft2_start_lcn": int(value.Mft2StartLcn),
        "mft_zone_start": int(value.MftZoneStart),
        "mft_zone_end": int(value.MftZoneEnd),
    }
    if any(
        type(item) is not int or item < 0
        for key, item in projection.items()
        if key != "query_succeeded"
    ):
        _refuse("FSCTL_GET_NTFS_VOLUME_DATA returned a negative field")
    if any(
        projection[key] == 0
        for key in (
            "number_sectors",
            "total_clusters",
            "bytes_per_sector",
            "bytes_per_cluster",
            "bytes_per_file_record_segment",
        )
    ):
        _refuse("FSCTL_GET_NTFS_VOLUME_DATA returned zero geometry")
    return projection


def _stage_f_usn_query_projection(
    raw: bytes,
    *,
    output_preimage: bytes,
    returned_input: bytes,
    returned_output: bytes,
    phase: str,
    handle: int,
    output_address: int,
    returned_address: int,
    started_utc: str,
    returned_utc: str,
    completed_utc: str,
) -> dict[str, Any]:
    if len(raw) != _STAGE_F_USN_QUERY_BYTES:
        _refuse("FSCTL_QUERY_USN_JOURNAL did not return exactly 80 bytes")
    (
        journal_id,
        first_usn,
        next_usn,
        lowest_valid_usn,
        maximum_usn,
        maximum_size,
        allocation_delta,
        minimum_major,
        maximum_major,
        flags,
        range_chunk,
        range_threshold,
    ) = struct.unpack("<QqqqqQQHHIQq", raw)
    if any(
        item < 0
        for item in (
            first_usn,
            next_usn,
            lowest_valid_usn,
            maximum_usn,
            range_threshold,
        )
    ):
        _refuse("FSCTL_QUERY_USN_JOURNAL returned a negative schema field")
    if minimum_major > 2 or maximum_major < 3:
        _refuse("USN journal does not support the frozen V2/V3 request")
    if not (
        first_usn <= next_usn <= maximum_usn
        and lowest_valid_usn <= next_usn
    ):
        _refuse("FSCTL_QUERY_USN_JOURNAL returned inconsistent USN bounds")
    if _utc(started_utc, "USN query start") > _utc(
        returned_utc, "USN query return"
    ) or _utc(returned_utc, "USN query return") > _utc(
        completed_utc, "USN query completion"
    ):
        _refuse("FSCTL_QUERY_USN_JOURNAL timestamps are reversed")
    if output_preimage != bytes(_STAGE_F_USN_QUERY_BYTES):
        _refuse("FSCTL_QUERY_USN_JOURNAL output preimage differs from 80 zero bytes")
    if returned_input != bytes(4) or len(returned_output) != 4:
        _refuse("FSCTL_QUERY_USN_JOURNAL returned-DWORD images differ")
    if int.from_bytes(returned_output, "little", signed=False) != len(raw):
        _refuse("FSCTL_QUERY_USN_JOURNAL returned-DWORD differs from the slice")
    return {
        "schema": "stage_f_usn_query_call_observation/v1",
        "phase": phase,
        "api": "DeviceIoControl",
        "volume_handle_value_uint64": handle,
        "control_code_name": "FSCTL_QUERY_USN_JOURNAL",
        "control_code_uint32": _STAGE_F_FSCTL_QUERY_USN_JOURNAL,
        "input_buffer_pointer_is_null": True,
        "input_buffer_byte_count": 0,
        "input_buffer_bytes_base64": "",
        "output_structure": "USN_JOURNAL_DATA_V2",
        "output_buffer_base_address_uint64": output_address,
        "output_buffer_capacity": _STAGE_F_USN_QUERY_BYTES,
        "bytes_returned_output_address_uint64": returned_address,
        "returned_nonzero": True,
        "last_error": None,
        "bytes_returned": _STAGE_F_USN_QUERY_BYTES,
        "output_buffer_bytes_base64": _stage_f_usn_b64(raw),
        "output_buffer_sha256": _stage_f_usn_sha(raw),
        "journal_id_uint64": journal_id,
        "first_usn": first_usn,
        "next_usn": next_usn,
        "lowest_valid_usn": lowest_valid_usn,
        "maximum_usn": maximum_usn,
        "maximum_size": maximum_size,
        "allocation_delta": allocation_delta,
        "minimum_supported_major_version": minimum_major,
        "maximum_supported_major_version": maximum_major,
        "flags": flags,
        "range_track_chunk_size": range_chunk,
        "range_track_file_size_threshold": range_threshold,
        "requested_record_versions_supported": True,
        "started_utc": started_utc,
        "returned_utc": returned_utc,
        "output_buffer_preimage_byte_count": len(output_preimage),
        "output_buffer_preimage_bytes_base64": _stage_f_usn_b64(output_preimage),
        "output_buffer_preimage_sha256": _stage_f_usn_sha(output_preimage),
        "output_buffer_preimage_all_zero": True,
        "bytes_returned_output_input_bytes_base64": _stage_f_usn_b64(returned_input),
        "bytes_returned_output_input_sha256": _stage_f_usn_sha(returned_input),
        "bytes_returned_output_bytes_base64": _stage_f_usn_b64(returned_output),
        "bytes_returned_output_sha256": _stage_f_usn_sha(returned_output),
        "bytes_returned_output_decoded_uint32": len(raw),
        "returned_slice_byte_count": len(raw),
        "returned_slice_sha256": _stage_f_usn_sha(raw),
        "raw_output_preimage_returned_slice_parsed_scalars_and_dword_reconcile": True,
        "completed_utc": completed_utc,
    }


def _stage_f_usn_parse_records(
    raw_output: bytes,
    *,
    buffer_ordinal: int,
    classifier: Callable[[Mapping[str, Any]], Mapping[str, Any]],
) -> tuple[int, list[dict[str, Any]]]:
    if len(raw_output) < 8:
        _refuse("FSCTL_READ_USN_JOURNAL output is shorter than its leading USN")
    leading_next_usn = struct.unpack_from("<q", raw_output, 0)[0]
    if leading_next_usn < 0:
        _refuse("FSCTL_READ_USN_JOURNAL returned a negative continuation USN")
    records: list[dict[str, Any]] = []
    offset = 8
    while offset < len(raw_output):
        if len(raw_output) - offset < 8:
            _refuse("USN output ends in a partial record header")
        record_length, major, minor = struct.unpack_from("<IHH", raw_output, offset)
        if record_length == 0 or record_length % 8 or offset + record_length > len(raw_output):
            _refuse("USN record length does not exactly partition the raw output")
        if major == 2:
            fixed_size = 60
            reference_width = 8
            child_offset, parent_offset = 8, 16
            usn_offset, timestamp_offset = 24, 32
            reason_offset, source_offset = 40, 44
            security_offset, attributes_offset = 48, 52
            name_length_offset, name_offset_offset = 56, 58
            normalization = "V2_RAW_LE_8_PLUS_8_ZERO_BYTES_TO_LOWER_HEX_16_BYTES"
        elif major == 3:
            fixed_size = 76
            reference_width = 16
            child_offset, parent_offset = 8, 24
            usn_offset, timestamp_offset = 40, 48
            reason_offset, source_offset = 56, 60
            security_offset, attributes_offset = 64, 68
            name_length_offset, name_offset_offset = 72, 74
            normalization = "V3_RAW_LE_16_BYTES_TO_LOWER_HEX_16_BYTES"
        else:
            _refuse("USN output contains an unknown record version")
        if minor != 0 or record_length < fixed_size:
            _refuse("USN record has an unsupported minor version or short header")
        record_raw = raw_output[offset : offset + record_length]
        child_raw = record_raw[child_offset : child_offset + reference_width]
        parent_raw = record_raw[parent_offset : parent_offset + reference_width]
        usn = struct.unpack_from("<q", record_raw, usn_offset)[0]
        timestamp = struct.unpack_from("<Q", record_raw, timestamp_offset)[0]
        reason = struct.unpack_from("<I", record_raw, reason_offset)[0]
        source = struct.unpack_from("<I", record_raw, source_offset)[0]
        security = struct.unpack_from("<I", record_raw, security_offset)[0]
        attributes = struct.unpack_from("<I", record_raw, attributes_offset)[0]
        name_length = struct.unpack_from("<H", record_raw, name_length_offset)[0]
        name_offset = struct.unpack_from("<H", record_raw, name_offset_offset)[0]
        if (
            usn < 0
            or name_length == 0
            or name_length % 2
            or name_offset != fixed_size
            or name_offset + name_length > record_length
        ):
            _refuse("USN record fixed projection or filename bounds differ")
        name_raw = record_raw[name_offset : name_offset + name_length]
        try:
            name = name_raw.decode("utf-16le", "strict")
        except UnicodeDecodeError as exc:
            raise BindingRefusal("USN record filename is not strict UTF-16LE") from exc
        canonical_child = (
            child_raw + bytes(8) if major == 2 else child_raw
        ).hex()
        canonical_parent = (
            parent_raw + bytes(8) if major == 2 else parent_raw
        ).hex()
        projected: dict[str, Any] = {
            "record_version": major,
            "buffer_ordinal": buffer_ordinal,
            "record_offset": offset,
            "raw_record_bytes_base64": _stage_f_usn_b64(record_raw),
            "raw_record_sha256": _stage_f_usn_sha(record_raw),
            "record_length": record_length,
            "major_version": major,
            "minor_version": minor,
            "file_reference_width_bits": reference_width * 8,
            "file_reference_raw_bytes_base64": _stage_f_usn_b64(child_raw),
            "parent_file_reference_raw_bytes_base64": _stage_f_usn_b64(parent_raw),
            "file_reference_number": canonical_child,
            "parent_file_reference_number": canonical_parent,
            "file_reference_normalization": normalization,
            "file_reference_normalization_recomputed_from_raw_bytes": True,
            "parent_file_reference_normalization_recomputed_from_raw_bytes": True,
            "usn": usn,
            "timestamp_filetime_uint64": timestamp,
            "reason_mask": reason,
            "source_info": source,
            "security_id": security,
            "file_attributes": attributes,
            "file_name_length_bytes": name_length,
            "file_name_offset": name_offset,
            "file_name_utf16le_base64": _stage_f_usn_b64(name_raw),
            "file_name": name,
            "strict_projection_exact": True,
        }
        disposition_value = classifier(dict(projected))
        disposition = _mapping(disposition_value, "USN scope classifier result")
        disposition_fields = frozenset(
            (
                "scope_disposition",
                "protected_identity_match_count",
                "mutation_ticket_identity",
                "mutation_ticket_match_count",
                "mutation_transaction_identity",
                "ledger_mutation_entry_identity",
            )
        )
        _exact_fields(disposition, disposition_fields, "USN scope classifier result")
        projected.update(disposition)
        _validate_usn_record_projection(projected, "collected USN record")
        records.append(projected)
        offset += record_length
    if offset != len(raw_output):
        _refuse("USN raw output does not partition exactly")
    return leading_next_usn, records


class StageFUsnJournalBackend:
    """Retain one volume handle and collect strict, outcome-blind USN ranges.

    Supplying ``apis`` is solely an injection seam for synthetic tests.  With
    no injection the constructor refuses off Windows before any filesystem or
    device operation.
    """

    def __init__(
        self,
        selected_volume_guid_path: str,
        *,
        apis: Any | None = None,
        clock: Callable[[], str] = _stage_f_usn_utc_now,
        filesystem_name_wchar_capacity: int = 64,
    ) -> None:
        if type(selected_volume_guid_path) is not str or re.fullmatch(
            r"\\\\\?\\Volume\{[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}\}\\",
            selected_volume_guid_path,
        ) is None:
            _refuse("Stage F USN backend requires one normalized volume-GUID root")
        if type(filesystem_name_wchar_capacity) is not int or not (
            8 <= filesystem_name_wchar_capacity <= 32768
        ):
            _refuse("Stage F filesystem-name buffer capacity is invalid")
        if apis is None:
            if sys.platform != "win32":
                _refuse("raw Stage F USN collection requires Win32")
            apis = _StageFWindowsUsnApis()
        for name in (
            "create_file",
            "get_volume_information_by_handle",
            "device_io_control",
            "close_handle",
            "last_error",
        ):
            if not callable(getattr(apis, name, None)):
                _refuse(f"Stage F USN API injection lacks {name}")
        self._apis = apis
        self._clock = clock
        self._closed = False
        self._active_start: dict[str, Any] | None = None
        self._selected_volume = selected_volume_guid_path
        create_input = selected_volume_guid_path[:-1]
        raw_handle = apis.create_file(
            create_input, 0x80000000, 3, None, 3, 0, None
        )
        try:
            self._handle = _stage_f_usn_handle_value(raw_handle)
        except BaseException:
            raise BindingRefusal(
                f"CreateFileW(volume) failed with error {apis.last_error()}"
            ) from None
        try:
            self._volume_observation = self._observe_volume(
                create_input, filesystem_name_wchar_capacity
            )
        except BaseException:
            apis.close_handle(self._handle)
            self._closed = True
            raise

    def _observe_volume(self, create_input: str, fs_capacity: int) -> dict[str, Any]:
        serial = ctypes.c_uint32(0)
        serial_input = _stage_f_usn_raw_at(ctypes.addressof(serial), 4)
        fs_buffer = ctypes.create_string_buffer(fs_capacity * 2)
        returned = self._apis.get_volume_information_by_handle(
            self._handle,
            None,
            0,
            ctypes.byref(serial),
            None,
            None,
            ctypes.cast(fs_buffer, ctypes.c_wchar_p),
            fs_capacity,
        )
        error = None if returned else self._apis.last_error()
        if not returned:
            _refuse(f"GetVolumeInformationByHandleW failed with error {error}")
        serial_output = _stage_f_usn_raw_at(ctypes.addressof(serial), 4)
        if int.from_bytes(serial_output, "little", signed=False) != serial.value:
            _refuse("Win32 volume serial raw projection differs")
        fs_raw = _stage_f_usn_raw_at(ctypes.addressof(fs_buffer), fs_capacity * 2)
        filesystem_name = _stage_f_usn_decode_filesystem(fs_raw)
        if filesystem_name != "NTFS":
            _refuse("selected Stage F USN volume is not NTFS")

        ntfs = _NTFS_VOLUME_DATA_BUFFER()
        ntfs_returned = ctypes.c_uint32(0)
        ntfs_ok = self._apis.device_io_control(
            self._handle,
            _STAGE_F_FSCTL_GET_NTFS_VOLUME_DATA,
            None,
            0,
            ctypes.c_void_p(ctypes.addressof(ntfs)),
            ctypes.sizeof(ntfs),
            ctypes.byref(ntfs_returned),
            None,
        )
        ntfs_error = None if ntfs_ok else self._apis.last_error()
        if not ntfs_ok:
            _refuse(f"FSCTL_GET_NTFS_VOLUME_DATA failed with error {ntfs_error}")
        if not 0 < ntfs_returned.value <= ctypes.sizeof(ntfs):
            _refuse("FSCTL_GET_NTFS_VOLUME_DATA returned an invalid byte count")
        ntfs_raw = _stage_f_usn_raw_at(ctypes.addressof(ntfs), ntfs_returned.value)
        ntfs_projection = _stage_f_usn_ntfs_projection(ntfs)
        opened_utc = _stage_f_usn_timestamp(self._clock, "USN volume opened UTC")
        return {
            "schema": "stage_f_usn_volume_handle_observation/v1",
            "selected_volume_guid_path": self._selected_volume,
            "create_api": "CreateFileW",
            "create_input_path_identity": _private_path_identity(create_input),
            "create_desired_access": 0x80000000,
            "create_share_mode": 3,
            "create_security_attributes": "NULL",
            "create_disposition": 3,
            "create_flags_and_attributes": 0,
            "create_returned_valid_handle": True,
            "volume_handle_value_uint64": self._handle,
            "volume_information_api": "GetVolumeInformationByHandleW",
            "volume_information_input_handle_value_uint64": self._handle,
            "volume_information_volume_name_buffer_pointer_is_null": True,
            "volume_information_volume_name_buffer_wchar_capacity": 0,
            "volume_information_serial_output_address_uint64": ctypes.addressof(serial),
            "volume_information_serial_input_bytes_base64": _stage_f_usn_b64(serial_input),
            "volume_information_serial_input_sha256": _stage_f_usn_sha(serial_input),
            "volume_information_max_component_length_pointer_is_null": True,
            "volume_information_filesystem_flags_pointer_is_null": True,
            "volume_information_filesystem_name_buffer_base_address_uint64": ctypes.addressof(fs_buffer),
            "volume_information_filesystem_name_buffer_wchar_capacity": fs_capacity,
            "volume_information_returned_nonzero": True,
            "volume_information_last_error": None,
            "volume_information_serial_output_bytes_base64": _stage_f_usn_b64(serial_output),
            "volume_information_serial_output_sha256": _stage_f_usn_sha(serial_output),
            "volume_serial_number_uint32": int(serial.value),
            "volume_information_serial_raw_projection_exact": True,
            "volume_information_filesystem_name_output_bytes_base64": _stage_f_usn_b64(fs_raw),
            "volume_information_filesystem_name_output_sha256": _stage_f_usn_sha(fs_raw),
            "filesystem_name": filesystem_name,
            "ntfs_volume_serial_number_uint64": ntfs_projection["volume_serial_number"],
            "ntfs_volume_serial_matches_ntfs_volume_data": True,
            "serial_sources_not_conflated": True,
            "ntfs_volume_data_api": "DeviceIoControl_FSCTL_GET_NTFS_VOLUME_DATA",
            "ntfs_volume_data_input_handle_value_uint64": self._handle,
            "ntfs_volume_data_control_code_uint32": _STAGE_F_FSCTL_GET_NTFS_VOLUME_DATA,
            "ntfs_volume_data_input_buffer_pointer_is_null": True,
            "ntfs_volume_data_input_buffer_byte_count": 0,
            "ntfs_volume_data_output_buffer_base_address_uint64": ctypes.addressof(ntfs),
            "ntfs_volume_data_output_buffer_capacity": ctypes.sizeof(ntfs),
            "ntfs_volume_data_bytes_returned_output_address_uint64": ctypes.addressof(ntfs_returned),
            "ntfs_volume_data_returned_nonzero": True,
            "ntfs_volume_data_last_error": None,
            "ntfs_volume_data_output_bytes_base64": _stage_f_usn_b64(ntfs_raw),
            "ntfs_volume_data_output_byte_count": int(ntfs_returned.value),
            "ntfs_volume_data_output_sha256": _stage_f_usn_sha(ntfs_raw),
            "ntfs_volume_data": ntfs_projection,
            "opened_utc": opened_utc,
            "continuously_retained": True,
        }

    def _query(self, phase: str) -> dict[str, Any]:
        output = ctypes.create_string_buffer(_STAGE_F_USN_QUERY_BYTES)
        output_preimage = _stage_f_usn_raw_at(
            ctypes.addressof(output), _STAGE_F_USN_QUERY_BYTES
        )
        if output_preimage != bytes(_STAGE_F_USN_QUERY_BYTES):
            _refuse("USN_JOURNAL_DATA_V2 output preimage is not exactly 80 zero bytes")
        returned = ctypes.c_uint32(0)
        returned_input = _stage_f_usn_raw_at(ctypes.addressof(returned), 4)
        started_utc = _stage_f_usn_timestamp(self._clock, f"USN {phase} query start")
        ok = self._apis.device_io_control(
            self._handle,
            _STAGE_F_FSCTL_QUERY_USN_JOURNAL,
            None,
            0,
            ctypes.c_void_p(ctypes.addressof(output)),
            _STAGE_F_USN_QUERY_BYTES,
            ctypes.byref(returned),
            None,
        )
        error = None if ok else self._apis.last_error()
        returned_utc = _stage_f_usn_timestamp(self._clock, f"USN {phase} query return")
        if not ok:
            _refuse(f"FSCTL_QUERY_USN_JOURNAL failed with error {error}")
        if returned.value != _STAGE_F_USN_QUERY_BYTES:
            _refuse("FSCTL_QUERY_USN_JOURNAL returned a non-80-byte image")
        raw = _stage_f_usn_raw_at(ctypes.addressof(output), returned.value)
        returned_output = _stage_f_usn_raw_at(ctypes.addressof(returned), 4)
        completed_utc = _stage_f_usn_timestamp(
            self._clock, f"USN {phase} query completion"
        )
        return _stage_f_usn_query_projection(
            raw,
            output_preimage=output_preimage,
            returned_input=returned_input,
            returned_output=returned_output,
            phase=phase,
            handle=self._handle,
            output_address=ctypes.addressof(output),
            returned_address=ctypes.addressof(returned),
            started_utc=started_utc,
            returned_utc=returned_utc,
            completed_utc=completed_utc,
        )

    @property
    def volume_handle_observation(self) -> dict[str, Any]:
        return strict_loads(canonical_bytes(self._volume_observation))

    def begin_range(self) -> dict[str, Any]:
        if self._closed:
            _refuse("Stage F USN volume handle is already closed")
        if self._active_start is not None:
            _refuse("Stage F USN range already has an active START query")
        self._active_start = self._query("START")
        return strict_loads(canonical_bytes(self._active_start))

    def collect_range(
        self,
        classifier: Callable[[Mapping[str, Any]], Mapping[str, Any]],
        *,
        output_capacity: int = 65536,
        maximum_read_calls: int = 1024,
    ) -> dict[str, Any]:
        if self._closed:
            _refuse("Stage F USN volume handle is already closed")
        if self._active_start is None:
            _refuse("Stage F USN range lacks its retained START query")
        if not callable(classifier):
            _refuse("Stage F USN collection requires a scope/ticket classifier")
        if type(output_capacity) is not int or not 4096 <= output_capacity <= _UINT32_MAX:
            _refuse("Stage F USN read output capacity is invalid")
        if type(maximum_read_calls) is not int or not 1 <= maximum_read_calls <= _UINT32_MAX:
            _refuse("Stage F USN maximum read-call count is invalid")
        start_query = self._active_start
        current_usn = start_query["next_usn"]
        if current_usn < start_query["lowest_valid_usn"]:
            _refuse("USN START watermark is already below LowestValidUsn")
        journal_id = start_query["journal_id_uint64"]
        read_calls: list[dict[str, Any]] = []
        records: list[dict[str, Any]] = []
        terminal_next_usn: int | None = None
        for ordinal in range(1, maximum_read_calls + 1):
            input_raw = struct.pack(
                "<qIIQQQHH4x",
                current_usn,
                0xFFFFFFFF,
                0,
                0,
                0,
                journal_id,
                2,
                3,
            )
            if len(input_raw) != _STAGE_F_USN_READ_INPUT_BYTES:
                _refuse("READ_USN_JOURNAL_DATA_V1 implementation is not 48 bytes")
            input_buffer = ctypes.create_string_buffer(input_raw, len(input_raw))
            output = ctypes.create_string_buffer(output_capacity)
            returned = ctypes.c_uint32(0)
            output_preimage = _stage_f_usn_raw_at(
                ctypes.addressof(output), output_capacity
            )
            returned_input = _stage_f_usn_raw_at(ctypes.addressof(returned), 4)
            if output_preimage != bytes(output_capacity) or returned_input != bytes(4):
                _refuse("FSCTL_READ_USN_JOURNAL output preimages are not all zero")
            started_utc = _stage_f_usn_timestamp(self._clock, "USN read start")
            ok = self._apis.device_io_control(
                self._handle,
                _STAGE_F_FSCTL_READ_USN_JOURNAL,
                ctypes.c_void_p(ctypes.addressof(input_buffer)),
                len(input_raw),
                ctypes.c_void_p(ctypes.addressof(output)),
                output_capacity,
                ctypes.byref(returned),
                None,
            )
            error = None if ok else self._apis.last_error()
            returned_utc = _stage_f_usn_timestamp(self._clock, "USN read return")
            if not ok:
                _refuse(f"FSCTL_READ_USN_JOURNAL failed with error {error}")
            if not 8 <= returned.value <= output_capacity:
                _refuse("FSCTL_READ_USN_JOURNAL returned an invalid byte count")
            output_raw = _stage_f_usn_raw_at(ctypes.addressof(output), returned.value)
            returned_output = _stage_f_usn_raw_at(ctypes.addressof(returned), 4)
            leading, parsed = _stage_f_usn_parse_records(
                output_raw, buffer_ordinal=ordinal, classifier=classifier
            )
            completed_utc = _stage_f_usn_timestamp(
                self._clock, "USN read completion"
            )
            if leading < current_usn:
                _refuse("FSCTL_READ_USN_JOURNAL continuation moved backwards")
            if parsed and leading <= current_usn:
                _refuse("nonempty USN continuation made no forward progress")
            if not parsed and leading != current_usn:
                _refuse("empty USN continuation skipped an unexplained range")
            expected_record_usn = current_usn
            for parsed_record in parsed:
                if parsed_record["usn"] != expected_record_usn:
                    _refuse("USN records do not form an exact gapless byte range")
                expected_record_usn += parsed_record["record_length"]
            if parsed and leading != expected_record_usn:
                _refuse("USN leading continuation differs from exact record lengths")
            if _utc(started_utc, "USN read start") > _utc(
                returned_utc, "USN read return"
            ):
                _refuse("FSCTL_READ_USN_JOURNAL timestamps are reversed")
            terminal = not parsed
            read_calls.append(
                {
                    "schema": "stage_f_usn_read_call_observation/v1",
                    "ordinal": ordinal,
                    "api": "DeviceIoControl",
                    "volume_handle_value_uint64": self._handle,
                    "control_code_name": "FSCTL_READ_USN_JOURNAL",
                    "control_code_uint32": _STAGE_F_FSCTL_READ_USN_JOURNAL,
                    "input_structure": "READ_USN_JOURNAL_DATA_V1",
                    "input_buffer_base_address_uint64": ctypes.addressof(input_buffer),
                    "input_buffer_byte_count": len(input_raw),
                    "input_buffer_bytes_base64": _stage_f_usn_b64(input_raw),
                    "input_buffer_sha256": _stage_f_usn_sha(input_raw),
                    "start_usn": current_usn,
                    "reason_mask": 0xFFFFFFFF,
                    "return_only_on_close": 0,
                    "timeout_uint64": 0,
                    "bytes_to_wait_for_uint64": 0,
                    "journal_id_uint64": journal_id,
                    "minimum_major_version": 2,
                    "maximum_major_version": 3,
                    "output_buffer_base_address_uint64": ctypes.addressof(output),
                    "output_buffer_capacity": output_capacity,
                    "bytes_returned_output_address_uint64": ctypes.addressof(returned),
                    "returned_nonzero": True,
                    "last_error": None,
                    "bytes_returned": int(returned.value),
                    "output_buffer_bytes_base64": _stage_f_usn_b64(output_raw),
                    "output_buffer_sha256": _stage_f_usn_sha(output_raw),
                    "leading_next_usn": leading,
                    "record_count": len(parsed),
                    "terminal_for_requested_end": terminal,
                    "started_utc": started_utc,
                    "returned_utc": returned_utc,
                    "input_buffer_struct_fields_recomputed_from_raw_bytes": True,
                    "output_buffer_preimage_byte_count": len(output_preimage),
                    "output_buffer_preimage_bytes_base64": _stage_f_usn_b64(output_preimage),
                    "output_buffer_preimage_sha256": _stage_f_usn_sha(output_preimage),
                    "output_buffer_preimage_all_zero": True,
                    "bytes_returned_output_input_bytes_base64": _stage_f_usn_b64(returned_input),
                    "bytes_returned_output_input_sha256": _stage_f_usn_sha(returned_input),
                    "bytes_returned_output_bytes_base64": _stage_f_usn_b64(returned_output),
                    "bytes_returned_output_sha256": _stage_f_usn_sha(returned_output),
                    "bytes_returned_output_decoded_uint32": int(returned.value),
                    "returned_slice_byte_count": len(output_raw),
                    "returned_slice_sha256": _stage_f_usn_sha(output_raw),
                    "output_capacity_preimage_returned_slice_leading_usn_and_records_reconcile": True,
                    "completed_utc": completed_utc,
                }
            )
            records.extend(parsed)
            current_usn = leading
            if terminal:
                terminal_next_usn = leading
                break
        if terminal_next_usn is None:
            _refuse("USN continuation did not reach a terminal buffer within the cap")
        end_query = self._query("END")
        self._active_start = None
        if end_query["journal_id_uint64"] != journal_id:
            _refuse("USN journal identity changed across the range")
        if end_query["lowest_valid_usn"] > start_query["next_usn"]:
            _refuse("USN journal wrapped beyond the START watermark")
        if end_query["next_usn"] != terminal_next_usn:
            _refuse("USN END watermark differs from the terminal continuation")
        protected = sum(
            row["scope_disposition"] == "AUTHORIZED_TICKET_MATCH" for row in records
        )
        result = {
            "schema": "stage_f_usn_journal_range/v1",
            "selected_volume_guid_path": self._selected_volume,
            "volume_handle_observation": self.volume_handle_observation,
            "start_query": start_query,
            "read_calls": read_calls,
            "read_call_count": len(read_calls),
            "end_query": end_query,
            "journal_id_uint64": journal_id,
            "lowest_valid_usn": end_query["lowest_valid_usn"],
            "first_usn": end_query["first_usn"],
            "next_usn": end_query["next_usn"],
            "maximum_usn": end_query["maximum_usn"],
            "start_watermark_usn": start_query["next_usn"],
            "end_watermark_usn": end_query["next_usn"],
            "records": records,
            "record_count": len(records),
            "continuation_buffer_count": len(read_calls),
            "terminal_next_usn": terminal_next_usn,
            "raw_buffers_partition_into_records_exactly": True,
            "protected_ticket_match_count": protected,
            "outside_scope_record_count": len(records) - protected,
            "refused_protected_record_count": 0,
            "journal_id_unchanged": True,
            "range_complete": True,
            "wrapped_or_gapped": False,
            "unknown_record_count": 0,
            "access_errors": 0,
            "start_end_query_phase_journal_and_raw_outputs_recomputed": True,
            "read_call_ordinals_next_usn_and_terminal_coverage_recomputed": True,
            "ticket_watch_usn_ledger_bijection_recomputed": True,
            "no_hidden_or_unclassified_record": True,
        }
        _validate_usn_range(result, "collected Stage F USN range")
        return result

    def close(self) -> None:
        if self._closed:
            _refuse("Stage F USN volume handle would be closed more than once")
        if self._active_start is not None:
            _refuse("Stage F USN volume handle cannot close with an open range")
        if not self._apis.close_handle(self._handle):
            _refuse(
                f"CloseHandle(Stage F USN volume) failed with error {self._apis.last_error()}"
            )
        self._closed = True

    def abort(self) -> None:
        """Release the retained handle after a refused or incomplete range."""

        if self._closed:
            _refuse("Stage F USN volume handle would be closed more than once")
        if not self._apis.close_handle(self._handle):
            _refuse(
                f"CloseHandle(aborted Stage F USN volume) failed with error {self._apis.last_error()}"
            )
        self._active_start = None
        self._closed = True


# Corrected Stage-F held append-only ledger backend.  This is a separate
# implementation-control primitive; it cannot import or invoke scientific code.
_STAGE_F_LEDGER_CREATE_FLAGS = 0x80200080
_STAGE_F_FILE_STANDARD_INFO_CLASS = 1
_STAGE_F_FILE_ATTRIBUTE_TAG_INFO_CLASS = 9
_STAGE_F_FILE_ID_INFO_CLASS = 18


class _StageFWindowsLedgerApis:
    """Exact synchronous Win32 calls used by the injectable ledger backend."""

    def __init__(self) -> None:
        if sys.platform != "win32":
            _refuse("held Stage F evidence ledger requires Win32")
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        self.create_file = kernel32.CreateFileW
        self.create_file.argtypes = (
            ctypes.c_wchar_p,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_void_p,
        )
        self.create_file.restype = ctypes.c_void_p
        self.get_final_path_name = kernel32.GetFinalPathNameByHandleW
        self.get_final_path_name.argtypes = (
            ctypes.c_void_p,
            ctypes.c_wchar_p,
            ctypes.c_uint32,
            ctypes.c_uint32,
        )
        self.get_final_path_name.restype = ctypes.c_uint32
        self.get_file_information = kernel32.GetFileInformationByHandleEx
        self.get_file_information.argtypes = (
            ctypes.c_void_p,
            ctypes.c_int,
            ctypes.c_void_p,
            ctypes.c_uint32,
        )
        self.get_file_information.restype = ctypes.c_int
        self.set_file_pointer = kernel32.SetFilePointerEx
        self.set_file_pointer.argtypes = (
            ctypes.c_void_p,
            ctypes.c_int64,
            ctypes.POINTER(ctypes.c_int64),
            ctypes.c_uint32,
        )
        self.set_file_pointer.restype = ctypes.c_int
        self.write_file = kernel32.WriteFile
        self.write_file.argtypes = (
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.c_void_p,
        )
        self.write_file.restype = ctypes.c_int
        self.flush_file_buffers = kernel32.FlushFileBuffers
        self.flush_file_buffers.argtypes = (ctypes.c_void_p,)
        self.flush_file_buffers.restype = ctypes.c_int
        self.read_file = kernel32.ReadFile
        self.read_file.argtypes = (
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.c_void_p,
        )
        self.read_file.restype = ctypes.c_int
        self.close_handle = kernel32.CloseHandle
        self.close_handle.argtypes = (ctypes.c_void_p,)
        self.close_handle.restype = ctypes.c_int

    @staticmethod
    def last_error() -> int:
        return int(ctypes.get_last_error())


def _stage_f_ledger_path_is_closed(path: Any) -> bool:
    if type(path) is not str or not path or unicodedata.normalize("NFC", path) != path:
        return False
    if "/" in path or path.endswith("\\"):
        return False
    if re.fullmatch(
        r"\\\\\?\\Volume\{[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}\}\\.+",
        path,
    ) is None:
        return False
    return all(part not in ("", ".", "..") for part in PureWindowsPath(path).parts[1:])


class StageFEvidenceLedgerBackend:
    """CREATE_NEW one ledger and retain its exact handle through all appends."""

    def __init__(
        self,
        ledger_path: str,
        validate_definition: Callable[[str, Any], None],
        *,
        apis: Any | None = None,
        clock: Callable[[], str] = _stage_f_usn_utc_now,
        path_wchar_capacity: int = 32768,
    ) -> None:
        if not _stage_f_ledger_path_is_closed(ledger_path):
            _refuse("Stage F ledger path is not one closed volume-GUID file path")
        if not callable(validate_definition):
            _refuse("Stage F ledger definition validator is not callable")
        if type(path_wchar_capacity) is not int or not 2 <= path_wchar_capacity <= 32768:
            _refuse("Stage F ledger path buffer capacity is invalid")
        if apis is None:
            if sys.platform != "win32":
                _refuse("held Stage F evidence ledger requires Win32")
            apis = _StageFWindowsLedgerApis()
        for name in (
            "create_file",
            "get_final_path_name",
            "get_file_information",
            "set_file_pointer",
            "write_file",
            "flush_file_buffers",
            "read_file",
            "close_handle",
            "last_error",
        ):
            if not callable(getattr(apis, name, None)):
                _refuse(f"Stage F ledger API injection lacks {name}")
        self._apis = apis
        self._clock = clock
        self._validate_definition = validate_definition
        self._ledger_path = ledger_path
        self._path_identity = _private_path_identity(ledger_path)
        self._last_time: datetime | None = None
        self._closed = False
        self._invalid = False
        self._head_identity: dict[str, str] | None = None
        self._last_append_observation: dict[str, Any] | None = None
        self._ordinal = -1
        self._eof = 0
        self._root_identity: dict[str, Any] | None = None
        self._used_append_tickets: set[str] = set()
        raw_handle = apis.create_file(
            ledger_path,
            0xC0000000,
            1,
            None,
            1,
            _STAGE_F_LEDGER_CREATE_FLAGS,
            None,
        )
        try:
            self._handle = _stage_f_usn_handle_value(raw_handle)
        except BaseException:
            raise BindingRefusal(
                f"CreateFileW(CREATE_NEW ledger) failed with error {apis.last_error()}"
            ) from None
        try:
            self._create_observation = self._observe_create(path_wchar_capacity)
            validate_definition(
                "stage_f_ledger_create_observation", self._create_observation
            )
            _validate_ledger_create_observation(
                self._create_observation, "created Stage F ledger"
            )
        except BaseException:
            self._invalid = True
            if not apis.close_handle(self._handle):
                self._closed = True
            else:
                self._closed = True
            raise

    def _tick(self, label: str) -> str:
        value = _stage_f_usn_timestamp(self._clock, label)
        parsed = _utc(value, label)
        if self._last_time is not None and parsed < self._last_time:
            _refuse("Stage F ledger call timestamps are not monotonic")
        self._last_time = parsed
        return value

    def _query_info(self, info_class: int, size: int, label: str) -> dict[str, Any]:
        output = ctypes.create_string_buffer(size)
        address = ctypes.addressof(output)
        zero = _stage_f_usn_raw_at(address, size)
        if zero != bytes(size):
            _refuse(f"{label} output preimage is not exactly zero")
        started = self._tick(f"{label} started UTC")
        returned = self._apis.get_file_information(
            self._handle, info_class, ctypes.c_void_p(address), size
        )
        error = None if returned else self._apis.last_error()
        completed = self._tick(f"{label} completed UTC")
        if not returned:
            _refuse(f"{label} failed with error {error}")
        raw = _stage_f_usn_raw_at(address, size)
        return {
            "address": address,
            "capacity": size,
            "input": zero,
            "output": raw,
            "started_utc": started,
            "completed_utc": completed,
        }

    @staticmethod
    def _parse_standard(raw: bytes) -> dict[str, Any]:
        if len(raw) != 24:
            _refuse("FILE_STANDARD_INFO raw image is not 24 bytes")
        allocation, eof, links, delete_pending, directory = struct.unpack(
            "<qqIBB2x", raw
        )
        if allocation < 0 or eof < 0 or allocation < eof:
            _refuse("FILE_STANDARD_INFO size projection is invalid")
        if delete_pending not in (0, 1) or directory not in (0, 1):
            _refuse("FILE_STANDARD_INFO Boolean projection is invalid")
        return {
            "allocation": allocation,
            "eof": eof,
            "links": links,
            "delete_pending": bool(delete_pending),
            "directory": bool(directory),
        }

    def _observe_create(self, path_capacity: int) -> dict[str, Any]:
        path_buffer = ctypes.create_string_buffer(path_capacity * 2)
        path_address = ctypes.addressof(path_buffer)
        path_zero = _stage_f_usn_raw_at(path_address, path_capacity * 2)
        if path_zero != bytes(path_capacity * 2):
            _refuse("ledger final-path output preimage is not exactly zero")
        path_started = self._tick("ledger final-path query started UTC")
        returned_count = self._apis.get_final_path_name(
            self._handle,
            ctypes.cast(path_buffer, ctypes.c_wchar_p),
            path_capacity,
            1,
        )
        path_error = None if returned_count else self._apis.last_error()
        path_completed = self._tick("ledger final-path query completed UTC")
        if not returned_count:
            _refuse(f"GetFinalPathNameByHandleW(ledger) failed with error {path_error}")
        if returned_count >= path_capacity:
            _refuse("GetFinalPathNameByHandleW(ledger) output is truncated")
        path_raw = _stage_f_usn_raw_at(path_address, 2 * (returned_count + 1))
        if not path_raw.endswith(b"\x00\x00"):
            _refuse("GetFinalPathNameByHandleW(ledger) output lacks its terminator")
        try:
            returned_path = path_raw[:-2].decode("utf-16le", "strict")
        except UnicodeDecodeError as exc:
            raise BindingRefusal("ledger final path is not strict UTF-16LE") from exc
        if returned_path != self._ledger_path:
            _refuse("ledger CreateFileW input and retained-handle final path differ")

        file_id_row = self._query_info(
            _STAGE_F_FILE_ID_INFO_CLASS, 24, "ledger FileIdInfo query"
        )
        volume_serial, file_id_raw = struct.unpack("<Q16s", file_id_row["output"])
        standard_row = self._query_info(
            _STAGE_F_FILE_STANDARD_INFO_CLASS, 24, "ledger FileStandardInfo query"
        )
        standard = self._parse_standard(standard_row["output"])
        if (
            standard["eof"] != 0
            or standard["links"] != 1
            or standard["delete_pending"]
            or standard["directory"]
        ):
            _refuse("fresh CREATE_NEW ledger is not one empty retained regular file")
        attribute_row = self._query_info(
            _STAGE_F_FILE_ATTRIBUTE_TAG_INFO_CLASS,
            8,
            "ledger FileAttributeTagInfo query",
        )
        attributes, reparse_tag = struct.unpack("<II", attribute_row["output"])
        if reparse_tag != 0 or attributes & 0x400:
            _refuse("fresh ledger is reparse-backed")
        created_utc = self._tick("ledger created UTC")
        return {
            "schema": "stage_f_ledger_create_observation/v1",
            "ledger_file_path_identity": self._path_identity,
            "create_api": "CreateFileW",
            "create_input_path_identity": self._path_identity,
            "create_desired_access": 0xC0000000,
            "create_share_mode": 1,
            "create_security_attributes_pointer_is_null": True,
            "create_disposition": 1,
            "create_flags_and_attributes": _STAGE_F_LEDGER_CREATE_FLAGS,
            "create_returned_valid_handle": True,
            "ledger_handle_value_uint64": self._handle,
            "path_query_api": "GetFinalPathNameByHandleW_FILE_NAME_NORMALIZED_VOLUME_NAME_GUID",
            "path_query_input_handle_value_uint64": self._handle,
            "path_query_output_buffer_base_address_uint64": path_address,
            "path_query_output_buffer_wchar_capacity": path_capacity,
            "path_query_output_buffer_input_zero_initialized": True,
            "path_query_output_buffer_input_bytes_base64": _stage_f_usn_b64(path_zero),
            "path_query_output_buffer_input_sha256": _stage_f_usn_sha(path_zero),
            "path_query_output_buffer_input_is_exactly_two_times_wchar_capacity_zero_bytes": True,
            "path_query_returned_wchar_count": int(returned_count),
            "path_query_returned_nonzero": True,
            "path_query_last_error": None,
            "path_query_output_bytes_base64": _stage_f_usn_b64(path_raw),
            "path_query_output_sha256": _stage_f_usn_sha(path_raw),
            "path_query_started_utc": path_started,
            "path_query_completed_utc": path_completed,
            "path_query_returned_count_output_terminator_and_capacity_reconcile": True,
            "path_query_output_identity": _private_path_identity(returned_path),
            "file_id_query_api": "GetFileInformationByHandleEx_FileIdInfo",
            "file_id_query_input_handle_value_uint64": self._handle,
            "file_id_query_output_buffer_base_address_uint64": file_id_row["address"],
            "file_id_query_output_buffer_capacity": 24,
            "file_id_query_output_buffer_input_bytes_base64": _stage_f_usn_b64(file_id_row["input"]),
            "file_id_query_output_buffer_input_sha256": _stage_f_usn_sha(file_id_row["input"]),
            "file_id_query_returned_nonzero": True,
            "file_id_query_last_error": None,
            "file_id_query_output_bytes_base64": _stage_f_usn_b64(file_id_row["output"]),
            "file_id_query_output_sha256": _stage_f_usn_sha(file_id_row["output"]),
            "file_id_query_started_utc": file_id_row["started_utc"],
            "file_id_query_completed_utc": file_id_row["completed_utc"],
            "ledger_file_volume_serial_number_uint64": volume_serial,
            "ledger_file_id_128": file_id_raw.hex(),
            "standard_info_query_api": "GetFileInformationByHandleEx_FileStandardInfo",
            "standard_info_query_input_handle_value_uint64": self._handle,
            "standard_info_query_output_buffer_base_address_uint64": standard_row["address"],
            "standard_info_query_output_buffer_capacity": 24,
            "standard_info_query_output_buffer_input_bytes_base64": _stage_f_usn_b64(standard_row["input"]),
            "standard_info_query_output_buffer_input_sha256": _stage_f_usn_sha(standard_row["input"]),
            "standard_info_query_returned_nonzero": True,
            "standard_info_query_last_error": None,
            "standard_info_query_output_bytes_base64": _stage_f_usn_b64(standard_row["output"]),
            "standard_info_query_output_sha256": _stage_f_usn_sha(standard_row["output"]),
            "standard_info_query_started_utc": standard_row["started_utc"],
            "standard_info_query_completed_utc": standard_row["completed_utc"],
            "allocation_size_bytes": standard["allocation"],
            "end_of_file_bytes": standard["eof"],
            "number_of_links": standard["links"],
            "delete_pending": standard["delete_pending"],
            "directory": standard["directory"],
            "attribute_query_api": "GetFileInformationByHandleEx_FileAttributeTagInfo",
            "attribute_query_input_handle_value_uint64": self._handle,
            "attribute_query_output_buffer_base_address_uint64": attribute_row["address"],
            "attribute_query_output_buffer_capacity": 8,
            "attribute_query_output_buffer_input_bytes_base64": _stage_f_usn_b64(attribute_row["input"]),
            "attribute_query_output_buffer_input_sha256": _stage_f_usn_sha(attribute_row["input"]),
            "attribute_query_returned_nonzero": True,
            "attribute_query_last_error": None,
            "attribute_query_output_bytes_base64": _stage_f_usn_b64(attribute_row["output"]),
            "attribute_query_output_sha256": _stage_f_usn_sha(attribute_row["output"]),
            "attribute_query_started_utc": attribute_row["started_utc"],
            "attribute_query_completed_utc": attribute_row["completed_utc"],
            "raw_file_attributes": attributes,
            "reparse_tag": reparse_tag,
            "all_raw_call_handles_paths_pointers_counts_images_parsed_values_and_hashes_reconcile": True,
            "handle_continuously_retained": True,
            "created_utc": created_utc,
        }

    @property
    def create_observation(self) -> dict[str, Any]:
        return strict_loads(canonical_bytes(self._create_observation))

    @property
    def head_identity(self) -> dict[str, str] | None:
        if self._head_identity is None:
            return None
        return dict(self._head_identity)

    @property
    def last_append_observation(self) -> dict[str, Any] | None:
        if self._last_append_observation is None:
            return None
        return strict_loads(canonical_bytes(self._last_append_observation))

    def _set_pointer(self, offset: int, label: str) -> dict[str, Any]:
        if not 0 <= offset <= (1 << 63) - 1:
            _refuse(f"{label} offset is outside SetFilePointerEx range")
        output = ctypes.c_int64(0)
        address = ctypes.addressof(output)
        input_raw = _stage_f_usn_raw_at(address, 8)
        if input_raw != bytes(8):
            _refuse(f"{label} output preimage is not exactly zero")
        returned = self._apis.set_file_pointer(
            self._handle, ctypes.c_int64(offset), ctypes.byref(output), 0
        )
        error = None if returned else self._apis.last_error()
        completed = self._tick(f"{label} UTC")
        if not returned:
            _refuse(f"{label} failed with error {error}")
        output_raw = _stage_f_usn_raw_at(address, 8)
        if output.value != offset or int.from_bytes(output_raw, "little", signed=True) != offset:
            _refuse(f"{label} raw returned position differs")
        return {
            "address": address,
            "input": input_raw,
            "output": output_raw,
            "offset": int(output.value),
            "utc": completed,
        }

    def _validate_entry_continuity(self, entry: Mapping[str, Any], wire: bytes) -> tuple[dict[str, str], str]:
        definition = (
            "stage_f_evidence_ledger_genesis"
            if entry.get("entry_type") == "GENESIS"
            else "stage_f_evidence_ledger_entry"
        )
        self._validate_definition(definition, entry)
        identity = _embedded_record_identity(
            entry, "ledger_sha256", kind="stage_f_evidence_ledger/v1"
        )
        ticket = _mapping(entry["append_ticket"], "ledger append ticket")
        self._validate_definition("stage_f_ledger_append_ticket", ticket)
        verify_embedded_digest(ticket, "ticket_sha256")
        ticket_sha = ticket["ticket_sha256"]
        if ticket_sha in self._used_append_tickets:
            _refuse("Stage F ledger append ticket was reused")
        expected_ordinal = self._ordinal + 1
        expected_type = "GENESIS" if expected_ordinal == 0 else "ENTRY"
        if entry["ordinal"] != expected_ordinal or entry["entry_type"] != expected_type:
            _refuse("Stage F ledger entry ordinal/type continuity differs")
        if entry["previous_entry_identity"] != self._head_identity:
            _refuse("Stage F ledger entry predecessor differs from the durable head")
        if ticket["previous_entry_identity"] != self._head_identity:
            _refuse("Stage F ledger ticket predecessor differs from the durable head")
        if ticket["expected_append_start_offset"] != self._eof:
            _refuse("Stage F ledger ticket append offset differs from durable EOF")
        if (
            entry["ledger_file_path_identity"] != self._path_identity
            or entry["ledger_file_volume_serial_number_uint64"]
            != self._create_observation["ledger_file_volume_serial_number_uint64"]
            or entry["ledger_file_id_128"]
            != self._create_observation["ledger_file_id_128"]
            or entry["ledger_handle_value_uint64"] != self._handle
            or not entry["ledger_handle_continuously_retained"]
            or entry["entry_wire_format"]
            != "CANONICAL_JSON_OBJECT_UTF8_THEN_SINGLE_LF"
        ):
            _refuse("Stage F ledger entry substituted its retained file or handle")
        if (
            ticket["ledger_file_path_identity"] != self._path_identity
            or ticket["ledger_file_volume_serial_number_uint64"]
            != self._create_observation["ledger_file_volume_serial_number_uint64"]
            or ticket["ledger_file_id_128"]
            != self._create_observation["ledger_file_id_128"]
            or ticket["root_protection_epoch_identity"]
            != entry["root_protection_epoch_identity"]
            or ticket["record_role"] != entry["record_role"]
            or ticket["record_identity"] != entry["record_identity"]
        ):
            _refuse("Stage F ledger append ticket projection differs from the entry")
        if self._root_identity is not None and entry["root_protection_epoch_identity"] != self._root_identity:
            _refuse("Stage F ledger entry changed its root-protection epoch")
        if expected_ordinal == 0:
            if (
                entry["ledger_create_observation"] != self._create_observation
                or entry["entry_start_offset"] != 0
                or entry["entry_wire_byte_count"] != len(wire)
            ):
                _refuse("Stage F ledger genesis does not bind its exact creation/wire")
        elif entry["previous_entry_append_observation"] != self._last_append_observation:
            _refuse("Stage F ledger entry lacks the exact predecessor append observation")
        return identity, ticket_sha

    def append_entry(
        self,
        entry_value: Mapping[str, Any],
        *,
        parent_watch_range_sha256: str,
        usn_range_sha256: str,
    ) -> dict[str, Any]:
        if self._closed:
            _refuse("Stage F ledger handle is already closed")
        if self._invalid:
            _refuse("Stage F ledger state is invalid and requires explicit abort")
        try:
            entry = _mapping(entry_value, "Stage F ledger entry")
            wire = canonical_bytes(entry) + b"\n"
            if not wire.endswith(b"\n") or wire.endswith(b"\r\n"):
                _refuse("Stage F ledger wire is not canonical JSON plus one LF")
            if len(wire) > _UINT32_MAX:
                _refuse("Stage F ledger entry exceeds one synchronous WriteFile call")
            identity, ticket_sha = self._validate_entry_continuity(entry, wire)
            ticket = entry["append_ticket"]
            _sha256(parent_watch_range_sha256, "ledger parent-watch range SHA-256")
            _sha256(usn_range_sha256, "ledger USN range SHA-256")
            if entry["usn_range_sha256"] != usn_range_sha256:
                _refuse("Stage F ledger entry and append use different USN ranges")
            if entry["entry_type"] == "ENTRY" and entry["parent_watch_sha256"] != parent_watch_range_sha256:
                _refuse("Stage F ledger entry and append use different parent-watch ranges")
            self._used_append_tickets.add(ticket_sha)

            pre_row = self._query_info(
                _STAGE_F_FILE_STANDARD_INFO_CLASS,
                24,
                "ledger preappend FileStandardInfo query",
            )
            pre = self._parse_standard(pre_row["output"])
            if (
                pre["eof"] != self._eof
                or pre["links"] != 1
                or pre["delete_pending"]
                or pre["directory"]
            ):
                _refuse("Stage F ledger preappend EOF/object state differs")
            pre_observed_utc = pre_row["completed_utc"]
            issued = _utc(ticket["issued_utc"], "ledger append ticket issued UTC")
            expires = _utc(ticket["expires_utc"], "ledger append ticket expires UTC")
            observed = _utc(pre_observed_utc, "ledger preappend observed UTC")
            if not issued <= observed <= expires:
                _refuse("Stage F ledger append ticket is not live before the write")

            append_pointer = self._set_pointer(self._eof, "ledger append pointer set")
            wire_buffer = ctypes.create_string_buffer(wire, len(wire))
            wire_address = ctypes.addressof(wire_buffer)
            written = ctypes.c_uint32(0)
            written_address = ctypes.addressof(written)
            written_zero = _stage_f_usn_raw_at(written_address, 4)
            if written_zero != bytes(4):
                _refuse("WriteFile bytes-written output preimage is not exactly zero")
            write_started = self._tick("ledger WriteFile started UTC")
            if not issued <= _utc(write_started, "ledger WriteFile started UTC") <= expires:
                _refuse("Stage F ledger append ticket expired before WriteFile")
            write_returned = self._apis.write_file(
                self._handle,
                ctypes.c_void_p(wire_address),
                len(wire),
                ctypes.byref(written),
                None,
            )
            write_error = None if write_returned else self._apis.last_error()
            write_completed = self._tick("ledger WriteFile completed UTC")
            if not write_returned:
                _refuse(f"WriteFile(ledger append) failed with error {write_error}")
            written_raw = _stage_f_usn_raw_at(written_address, 4)
            if written.value != len(wire) or int.from_bytes(written_raw, "little") != len(wire):
                _refuse("WriteFile(ledger append) returned a partial count")
            flush_returned = self._apis.flush_file_buffers(self._handle)
            flush_error = None if flush_returned else self._apis.last_error()
            flush_completed = self._tick("ledger FlushFileBuffers completed UTC")
            if not flush_returned:
                _refuse(f"FlushFileBuffers(ledger) failed with error {flush_error}")

            end = self._eof + len(wire)
            post_row = self._query_info(
                _STAGE_F_FILE_STANDARD_INFO_CLASS,
                24,
                "ledger postflush FileStandardInfo query",
            )
            post = self._parse_standard(post_row["output"])
            if (
                post["eof"] != end
                or post["links"] != 1
                or post["delete_pending"]
                or post["directory"]
            ):
                _refuse("Stage F ledger postflush EOF/object state differs")

            reread_pointer = self._set_pointer(
                self._eof, "ledger reread pointer set"
            )
            reread_buffer = ctypes.create_string_buffer(len(wire))
            reread_address = ctypes.addressof(reread_buffer)
            reread_zero = _stage_f_usn_raw_at(reread_address, len(wire))
            if reread_zero != bytes(len(wire)):
                _refuse("ledger reread data preimage is not exactly zero")
            bytes_read = ctypes.c_uint32(0)
            bytes_read_address = ctypes.addressof(bytes_read)
            bytes_read_zero = _stage_f_usn_raw_at(bytes_read_address, 4)
            if bytes_read_zero != bytes(4):
                _refuse("ReadFile bytes-read output preimage is not exactly zero")
            reread_returned = self._apis.read_file(
                self._handle,
                ctypes.c_void_p(reread_address),
                len(wire),
                ctypes.byref(bytes_read),
                None,
            )
            reread_error = None if reread_returned else self._apis.last_error()
            reread_completed = self._tick("ledger reread completed UTC")
            if not reread_returned:
                _refuse(f"ReadFile(ledger reread) failed with error {reread_error}")
            bytes_read_raw = _stage_f_usn_raw_at(bytes_read_address, 4)
            reread_raw = _stage_f_usn_raw_at(reread_address, len(wire))
            if (
                bytes_read.value != len(wire)
                or int.from_bytes(bytes_read_raw, "little") != len(wire)
                or reread_raw != wire
            ):
                _refuse("same-handle ledger reread differs from the appended wire")
            restore_pointer = self._set_pointer(end, "ledger EOF pointer restored")
            completed_utc = self._tick("ledger append completed UTC")

            observation = {
                "schema": "stage_f_evidence_ledger_append_observation/v1",
                "entry_identity": identity,
                "append_ticket_sha256": ticket_sha,
                "ledger_file_path_identity": self._path_identity,
                "ledger_file_volume_serial_number_uint64": self._create_observation["ledger_file_volume_serial_number_uint64"],
                "ledger_file_id_128": self._create_observation["ledger_file_id_128"],
                "ledger_handle_value_uint64": self._handle,
                "preappend_file_standard_info_api": "GetFileInformationByHandleEx_FileStandardInfo",
                "preappend_file_standard_info_handle_value_uint64": self._handle,
                "preappend_file_standard_info_output_buffer_base_address_uint64": pre_row["address"],
                "preappend_file_standard_info_output_buffer_capacity": 24,
                "preappend_file_standard_info_output_buffer_input_bytes_base64": _stage_f_usn_b64(pre_row["input"]),
                "preappend_file_standard_info_output_buffer_input_sha256": _stage_f_usn_sha(pre_row["input"]),
                "preappend_file_standard_info_returned_nonzero": True,
                "preappend_file_standard_info_last_error": None,
                "preappend_file_standard_info_output_bytes_base64": _stage_f_usn_b64(pre_row["output"]),
                "preappend_file_standard_info_output_sha256": _stage_f_usn_sha(pre_row["output"]),
                "preappend_allocation_size_bytes": pre["allocation"],
                "preappend_end_of_file_bytes": pre["eof"],
                "preappend_end_of_file_observed_utc": pre_observed_utc,
                "append_start_offset": self._eof,
                "set_append_pointer_api": "SetFilePointerEx",
                "set_append_pointer_input_handle_value_uint64": self._handle,
                "set_append_pointer_distance_to_move": self._eof,
                "set_append_pointer_move_method": "FILE_BEGIN",
                "set_append_pointer_new_position_output_address_uint64": append_pointer["address"],
                "set_append_pointer_new_position_input_bytes_base64": _stage_f_usn_b64(append_pointer["input"]),
                "set_append_pointer_new_position_input_sha256": _stage_f_usn_sha(append_pointer["input"]),
                "set_append_pointer_returned_nonzero": True,
                "set_append_pointer_last_error": None,
                "set_append_pointer_new_position_output_bytes_base64": _stage_f_usn_b64(append_pointer["output"]),
                "set_append_pointer_new_position_output_sha256": _stage_f_usn_sha(append_pointer["output"]),
                "set_append_pointer_result_offset": append_pointer["offset"],
                "append_pointer_set_utc": append_pointer["utc"],
                "append_byte_count": len(wire),
                "append_end_offset": end,
                "entry_wire_bytes_base64": _stage_f_usn_b64(wire),
                "entry_wire_buffer_base_address_uint64": wire_address,
                "entry_wire_buffer_byte_count": len(wire),
                "entry_wire_sha256": _stage_f_usn_sha(wire),
                "write_api": "WriteFile",
                "write_input_handle_value_uint64": self._handle,
                "write_input_buffer_base_address_uint64": wire_address,
                "write_input_byte_count": len(wire),
                "write_bytes_written_output_address_uint64": written_address,
                "write_bytes_written_input_bytes_base64": _stage_f_usn_b64(written_zero),
                "write_bytes_written_input_sha256": _stage_f_usn_sha(written_zero),
                "write_overlapped_pointer_is_null": True,
                "write_started_utc": write_started,
                "write_returned_nonzero": True,
                "write_last_error": None,
                "write_bytes_written_output_bytes_base64": _stage_f_usn_b64(written_raw),
                "write_bytes_written_output_sha256": _stage_f_usn_sha(written_raw),
                "written_byte_count": int(written.value),
                "write_completed_utc": write_completed,
                "flush_api": "FlushFileBuffers",
                "flush_input_handle_value_uint64": self._handle,
                "flush_returned_nonzero": True,
                "flush_completed_utc": flush_completed,
                "postflush_file_standard_info_api": "GetFileInformationByHandleEx_FileStandardInfo",
                "postflush_file_standard_info_handle_value_uint64": self._handle,
                "postflush_file_standard_info_output_buffer_base_address_uint64": post_row["address"],
                "postflush_file_standard_info_output_buffer_capacity": 24,
                "postflush_file_standard_info_output_buffer_input_bytes_base64": _stage_f_usn_b64(post_row["input"]),
                "postflush_file_standard_info_output_buffer_input_sha256": _stage_f_usn_sha(post_row["input"]),
                "postflush_file_standard_info_returned_nonzero": True,
                "postflush_file_standard_info_last_error": None,
                "postflush_file_standard_info_output_bytes_base64": _stage_f_usn_b64(post_row["output"]),
                "postflush_file_standard_info_output_sha256": _stage_f_usn_sha(post_row["output"]),
                "postflush_file_size": post["eof"],
                "postflush_file_size_observed_utc": post_row["completed_utc"],
                "set_reread_pointer_api": "SetFilePointerEx",
                "set_reread_pointer_input_handle_value_uint64": self._handle,
                "set_reread_pointer_distance_to_move": self._eof,
                "set_reread_pointer_move_method": "FILE_BEGIN",
                "set_reread_pointer_new_position_output_address_uint64": reread_pointer["address"],
                "set_reread_pointer_new_position_input_bytes_base64": _stage_f_usn_b64(reread_pointer["input"]),
                "set_reread_pointer_new_position_input_sha256": _stage_f_usn_sha(reread_pointer["input"]),
                "set_reread_pointer_returned_nonzero": True,
                "set_reread_pointer_last_error": None,
                "set_reread_pointer_new_position_output_bytes_base64": _stage_f_usn_b64(reread_pointer["output"]),
                "set_reread_pointer_new_position_output_sha256": _stage_f_usn_sha(reread_pointer["output"]),
                "set_reread_pointer_result_offset": reread_pointer["offset"],
                "reread_pointer_set_utc": reread_pointer["utc"],
                "reread_api": "ReadFile",
                "reread_input_handle_value_uint64": self._handle,
                "reread_start_offset": self._eof,
                "reread_buffer_base_address_uint64": reread_address,
                "reread_byte_count": len(wire),
                "reread_buffer_input_zero_initialized": True,
                "reread_buffer_input_bytes_base64": _stage_f_usn_b64(reread_zero),
                "reread_buffer_input_sha256": _stage_f_usn_sha(reread_zero),
                "reread_buffer_input_is_exactly_reread_byte_count_zero_bytes": True,
                "reread_bytes_read_output_address_uint64": bytes_read_address,
                "reread_bytes_read_input_bytes_base64": _stage_f_usn_b64(bytes_read_zero),
                "reread_bytes_read_input_sha256": _stage_f_usn_sha(bytes_read_zero),
                "reread_overlapped_pointer_is_null": True,
                "reread_returned_nonzero": True,
                "reread_last_error": None,
                "reread_bytes_read_output_bytes_base64": _stage_f_usn_b64(bytes_read_raw),
                "reread_bytes_read_output_sha256": _stage_f_usn_sha(bytes_read_raw),
                "reread_bytes_read": int(bytes_read.value),
                "reread_raw_bytes_base64": _stage_f_usn_b64(reread_raw),
                "reread_sha256": _stage_f_usn_sha(reread_raw),
                "reread_completed_utc": reread_completed,
                "restore_pointer_api": "SetFilePointerEx",
                "restore_pointer_input_handle_value_uint64": self._handle,
                "restore_pointer_distance_to_move": end,
                "restore_pointer_move_method": "FILE_BEGIN",
                "restore_pointer_new_position_output_address_uint64": restore_pointer["address"],
                "restore_pointer_new_position_input_bytes_base64": _stage_f_usn_b64(restore_pointer["input"]),
                "restore_pointer_new_position_input_sha256": _stage_f_usn_sha(restore_pointer["input"]),
                "restore_pointer_returned_nonzero": True,
                "restore_pointer_last_error": None,
                "restore_pointer_new_position_output_bytes_base64": _stage_f_usn_b64(restore_pointer["output"]),
                "restore_pointer_new_position_output_sha256": _stage_f_usn_sha(restore_pointer["output"]),
                "restore_pointer_result_offset": restore_pointer["offset"],
                "pointer_restored_utc": restore_pointer["utc"],
                "all_raw_call_handles_pointers_counts_zero_preimages_returned_images_and_hashes_reconcile": True,
                "all_offsets_counts_hashes_and_handles_reconciled": True,
                "parent_watch_range_sha256": parent_watch_range_sha256,
                "usn_range_sha256": usn_range_sha256,
                "completed_utc": completed_utc,
            }
            self._validate_definition(
                "stage_f_evidence_ledger_append_observation", observation
            )
            _validate_ledger_append_observation(
                observation, "completed Stage F ledger append"
            )
            self._eof = end
            self._ordinal = entry["ordinal"]
            self._head_identity = identity
            self._root_identity = entry["root_protection_epoch_identity"]
            self._last_append_observation = observation
            return strict_loads(canonical_bytes(observation))
        except BaseException:
            self._invalid = True
            raise

    def _close(self, disposition: str) -> dict[str, Any]:
        if self._closed:
            _refuse("Stage F ledger handle would be closed more than once")
        returned = self._apis.close_handle(self._handle)
        error = None if returned else self._apis.last_error()
        closed_utc = self._tick(f"Stage F ledger {disposition} close UTC")
        if not returned:
            self._invalid = True
            _refuse(f"CloseHandle(Stage F ledger) failed with error {error}")
        self._closed = True
        return {
            "close_api": "CloseHandle",
            "close_input_handle_value_uint64": self._handle,
            "close_returned_nonzero": True,
            "close_last_error": None,
            "close_disposition": disposition,
            "closed_utc": closed_utc,
        }

    def release(self) -> dict[str, Any]:
        if self._invalid:
            _refuse("invalid Stage F ledger must use explicit abort")
        return self._close("ROOT_RELEASE_AFTER_HANDOFF")

    def abort(self) -> dict[str, Any]:
        return self._close("REFUSED_ATTEMPT_ABORT")


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
        "operations_serialized": True,
        "source_guard_retained_across_move": True,
        "post_move_guard_flush_api": "FlushFileBuffers",
        "post_move_guard_flush_returned_nonzero": True,
        "final_open_desired_access": 2147483776,
        "final_open_share_mode": 7,
        "final_open_creation_disposition": 3,
        "final_open_flags_and_attributes": 2097152,
        "source_and_final_same_volume_file_id_byte_count_and_sha256": True,
        "independent_final_open_compared_by_compare_object_handles": False,
        "final_and_guard_stable_volume_file_id_attributes_byte_count_and_sha256": True,
        "final_handle_close_api": "CloseHandle",
        "final_handle_close_returned_nonzero": True,
        "duplicate_guard_retained_until_transaction_sealed": True,
        "final_open_api": "CreateFileW",
        "final_open_security_attributes": "NULL",
        "final_open_returned_valid": True,
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
    guard = _handle(
        record["source_guard_handle_value_uint64"], "atomic source guard handle"
    )
    final_handle = _handle(
        record["final_open_handle_value_uint64"], "atomic final handle"
    )
    if guard == final_handle:
        _refuse("atomic independent final open reused the retained guard handle")
    if record["post_move_guard_flush_handle_value_uint64"] != guard:
        _refuse("atomic guard flush used a substituted handle")
    if record["final_handle_close_input_handle_value_uint64"] != final_handle:
        _refuse("atomic final close used a substituted handle")
    pre = _mapping(record["pre_move_guard_observation"], "atomic pre-move guard")
    post = _mapping(record["post_move_guard_observation"], "atomic post-move guard")
    final = _mapping(record["final_handle_observation"], "atomic final handle")
    for observation, expected_handle, name in (
        (pre, guard, "pre-move guard"),
        (post, guard, "post-move guard"),
        (final, final_handle, "final handle"),
    ):
        handle_fields = (
            "handle_value_uint64",
            "path_query_handle_value_uint64",
            "file_id_query_handle_value_uint64",
            "standard_info_query_handle_value_uint64",
            "attribute_query_handle_value_uint64",
            "read_handle_value_uint64",
        )
        if any(observation[field] != expected_handle for field in handle_fields):
            _refuse(f"atomic {name} substituted a query/read handle")
        if observation["reparse_tag"] != 0 or not observation["read_from_held_handle"]:
            _refuse(f"atomic {name} is reparse-backed or not read from its held handle")
    stable_fields = (
        "volume_serial_number_uint64",
        "file_id_128",
        "raw_file_attributes",
        "reparse_tag",
        "byte_count",
        "sha256",
    )
    stable = tuple(pre[field] for field in stable_fields)
    if tuple(post[field] for field in stable_fields) != stable or tuple(
        final[field] for field in stable_fields
    ) != stable:
        _refuse("atomic guard/final stable object projection differs")
    parent_watch = _mapping(
        record["parent_watch_observation"], "atomic publication parent watch"
    )
    if (
        not parent_watch["pending_before_target_check"]
        or not parent_watch["completed_before_same_object_verification_and_final_lock"]
        or parent_watch["overflow_or_enumeration_loss"]
        or not parent_watch["postcompletion_root_watch_and_usn_coverage"]
    ):
        _refuse("atomic publication parent-watch continuity differs")
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
        ("binding_validator_identity", "stage_f_binding_validator/v3"),
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
        "raw_creation_flags": 4,
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
        "lp_application_name_representation": "HANDLE_DERIVED_NORMALIZED_EXTENDED_DOS_PATH",
        "command_argv0_representation": "NORMALIZED_VOLUME_GUID_PATH",
        "created_suspended": True,
        "image_attestation_completed_before_resume": True,
        "resume_api": "ResumeThread",
        "resume_returned_previous_suspend_count": 1,
        "resume_succeeded": True,
        "thread_close_api": "CloseHandle",
        "thread_close_returned_nonzero": True,
        "thread_close_after_resume": True,
        "refusal_before_user_code": False,
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
    application_identity = _identity(
        record["application_name_path_identity"],
        "stage_f_private_path/v1",
        f"{phase} lpApplicationName",
    )
    canonical_identity = _identity(
        record["canonical_volume_guid_application_path_identity"],
        "stage_f_private_path/v1",
        f"{phase} canonical volume-GUID argv0",
    )
    if application_identity == canonical_identity:
        _refuse(f"{phase} DOS alias and volume-GUID path identities were conflated")
    attestation = _mapping(record["process_image_attestation"], f"{phase} image attestation")
    if (
        attestation.get("schema") != "stage_f_attested_process_image/v1"
        or attestation.get("expected_volume_guid_path_identity") != canonical_identity
        or attestation.get("lp_application_name_dos_path_identity")
        != application_identity
        or attestation.get("dos_alias_same_stable_file_identity_attributes_byte_count_and_sha256")
        is not True
        or attestation.get("native_image_same_stable_file_identity_attributes_byte_count_and_sha256")
        is not True
        or attestation.get("independent_dos_alias_open_compared_by_compare_object_handles")
        is not False
        or attestation.get("independent_native_image_open_compared_by_compare_object_handles")
        is not False
        or attestation.get("user_code_executed_before_attestation") is not False
        or attestation.get("unexpected_root_watch_or_usn_event") is not False
    ):
        _refuse(f"{phase} image attestation is not outcome-blind and root-protected")
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
    if record["resume_input_thread_handle_value_uint64"] != parsed_thread_handle:
        _refuse(f"{phase} ResumeThread used a substituted handle")
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
            "resumed_utc",
            "thread_close_started_utc",
            "thread_handle_closed_utc",
        ),
        f"{phase} launch",
    )
    if _utc(attestation["attestation_completed_utc"], f"{phase} attestation completion") > _utc(record["resumed_utc"], f"{phase} resume"):
        _refuse(f"{phase} image attestation completed after ResumeThread")
    if record["launch_utc"] != record["resumed_utc"]:
        _refuse(f"{phase} launch_utc differs from ResumeThread completion")
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
        "binding_validator_identity": "stage_f_binding_validator/v3",
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
    attestation_context: Mapping[str, Any] | None = None,
) -> tuple[int, dict[str, Any]]:
    """Launch one frozen probe suspended, attest its image, then resume it."""

    if sys.platform != "win32" or ctypes.sizeof(ctypes.c_void_p) != 8:
        _refuse("the frozen CreateProcessW observation requires 64-bit Win32")
    if phase not in ("PRE_RESTART", "POST_RESTART"):
        _refuse("CreateProcessW probe phase differs")
    if attestation_context is None:
        _refuse(
            "corrected CreateProcessW requires retained root/USN image-attestation context"
        )
    attestation_context = _mapping(attestation_context, "process image-attestation context")
    _exact_fields(
        attestation_context,
        frozenset(
            (
                "canonical_volume_guid_application_path_identity",
                "lp_application_name_path_identity",
                "attest_process_image",
            )
        ),
        "process image-attestation context",
    )
    attest_process_image = attestation_context["attest_process_image"]
    if not callable(attest_process_image):
        _refuse("process image attestor is not callable")
    _identity(
        attestation_context["canonical_volume_guid_application_path_identity"],
        "stage_f_private_path/v1",
        "canonical volume-GUID application path",
    )
    _identity(
        attestation_context["lp_application_name_path_identity"],
        "stage_f_private_path/v1",
        "lpApplicationName DOS-alias path",
    )
    if (
        attestation_context["canonical_volume_guid_application_path_identity"]
        != invocation["executable_path_identity"]
    ):
        _refuse("canonical application identity differs from invocation")
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
    resume = kernel32.ResumeThread
    resume.argtypes = (ctypes.c_void_p,)
    resume.restype = ctypes.c_uint32
    terminate = kernel32.TerminateProcess
    terminate.argtypes = (ctypes.c_void_p, ctypes.c_uint32)
    terminate.restype = ctypes.c_int
    wait = kernel32.WaitForSingleObject
    wait.argtypes = (ctypes.c_void_p, ctypes.c_uint32)
    wait.restype = ctypes.c_uint32
    create_started = _orchestrator_utc()
    returned = bool(
        create(
            executable,
            ctypes.c_void_p(command_base),
            None,
            None,
            False,
            4,
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
    try:
        attestation = _mapping(
            attest_process_image(
                executable=executable,
                process_handle=process_handle,
                thread_handle=thread_handle,
                process_id=int(process_info.dwProcessId),
                phase=phase,
                canonical_volume_guid_application_path_identity=attestation_context[
                    "canonical_volume_guid_application_path_identity"
                ],
                lp_application_name_path_identity=attestation_context[
                    "lp_application_name_path_identity"
                ],
            ),
            f"{phase} process image attestation",
        )
        if (
            attestation.get("schema") != "stage_f_attested_process_image/v1"
            or attestation.get("user_code_executed_before_attestation") is not False
            or attestation.get("unexpected_root_watch_or_usn_event") is not False
        ):
            _refuse(f"{phase} process image attestation differs")
    except BaseException:
        terminate(process_info.hProcess, 1)
        wait(process_info.hProcess, _UINT32_MAX)
        close(process_info.hThread)
        close(process_info.hProcess)
        raise
    previous_suspend_count = int(resume(process_info.hThread))
    resumed_utc = _orchestrator_utc()
    if previous_suspend_count != 1:
        terminate(process_info.hProcess, 1)
        wait(process_info.hProcess, _UINT32_MAX)
        close(process_info.hThread)
        close(process_info.hProcess)
        _refuse(f"ResumeThread({phase}) did not return previous suspend count one")
    thread_close_started = _orchestrator_utc()
    thread_close_returned = bool(close(process_info.hThread))
    thread_closed = _orchestrator_utc()
    if not thread_close_returned:
        terminate(process_info.hProcess, 1)
        wait(process_info.hProcess, _UINT32_MAX)
        close(process_info.hProcess)
        raise _windows_error(f"CloseHandle({phase} thread)")
    application_identity = attestation_context["lp_application_name_path_identity"]
    canonical_application_identity = attestation_context[
        "canonical_volume_guid_application_path_identity"
    ]
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
        "raw_creation_flags": 4,
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
        "launch_utc": resumed_utc,
        "canonical_volume_guid_application_path_identity": canonical_application_identity,
        "lp_application_name_representation": "HANDLE_DERIVED_NORMALIZED_EXTENDED_DOS_PATH",
        "command_argv0_representation": "NORMALIZED_VOLUME_GUID_PATH",
        "created_suspended": True,
        "process_image_attestation": attestation,
        "image_attestation_completed_before_resume": True,
        "resume_api": "ResumeThread",
        "resume_input_thread_handle_value_uint64": thread_handle,
        "resume_returned_previous_suspend_count": previous_suspend_count,
        "resume_succeeded": True,
        "resumed_utc": resumed_utc,
        "thread_close_after_resume": True,
        "refusal_before_user_code": False,
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
        "reset_event": bind(
            kernel32, "ResetEvent", (ctypes.c_void_p,), ctypes.c_int
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
        "get_attributes": bind(
            kernel32,
            "GetFileAttributesW",
            (ctypes.c_wchar_p,),
            ctypes.c_uint32,
        ),
        "create_directory": bind(
            kernel32,
            "CreateDirectoryW",
            (ctypes.c_wchar_p, ctypes.c_void_p),
            ctypes.c_int,
        ),
        "get_process_id": bind(
            kernel32, "GetCurrentProcessId", (), ctypes.c_uint32
        ),
        "get_thread_id": bind(
            kernel32, "GetCurrentThreadId", (), ctypes.c_uint32
        ),
        "get_process_times": bind(
            kernel32,
            "GetProcessTimes",
            (
                ctypes.c_void_p,
                ctypes.POINTER(_ORCH_FILETIME),
                ctypes.POINTER(_ORCH_FILETIME),
                ctypes.POINTER(_ORCH_FILETIME),
                ctypes.POINTER(_ORCH_FILETIME),
            ),
            ctypes.c_int,
        ),
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


class _WindowsStageFControllerState(_HostRuntimeProtectionState):
    """Retained corrected Stage-F resources; never owns a start capability."""

    def __init__(self, apis: Mapping[str, Any]) -> None:
        super().__init__(apis)
        self.root_active = False
        self.private_reads_started = False
        self.attempt_root = ""
        self.usn_backend: Any = None
        self.usn_start_record: dict[str, Any] | None = None
        self.control_records: list[dict[str, Any]] = []
        self.genesis: dict[str, Any] | None = None
        self.root_epoch: dict[str, Any] | None = None
        self.root_mutation_ticket: dict[str, Any] | None = None
        self.private_materials: dict[str, bytes] = {}
        self.ledger_backend: Any = None
        self.invalidated = False
        self.protection_started_utc = ""
        self.holder_process_id = 0
        self.holder_creation_filetime = 0
        self.parent_creation_completion: dict[str, Any] | None = None
        self.completed_live_phases: list[str] = []
        self.validate_definition: Callable[[str, Any], None] | None = None
        self.phase_materials: Mapping[str, Any] | None = None
        self.capacity_publication: dict[str, Any] | None = None
        self.capacity_closure: dict[str, Any] | None = None
        self.validator_observation: dict[str, Any] | None = None
        self.authorization_records: list[dict[str, Any]] = []
        self.launch_gate: dict[str, Any] | None = None
        self.start_intent: dict[str, Any] | None = None
        self.frozen_handoff: dict[str, Any] | None = None

    def abort(self) -> None:
        if self.released:
            return
        first: BaseException | None = None
        if self.ledger_backend is not None:
            try:
                self.ledger_backend.abort()
            except BaseException as exc:
                first = exc
            self.ledger_backend = None
        if self.usn_backend is not None:
            try:
                self.usn_backend.abort()
            except BaseException as exc:
                if first is None:
                    first = exc
            self.usn_backend = None
        for watch in self.watches:
            completion_bytes = int(watch.get("completion_bytes", 0) or 0)
            if completion_bytes:
                try:
                    if not self.apis["virtual_free"](
                        completion_bytes, 0, 0x8000
                    ) and first is None:
                        first = _windows_error(
                            "VirtualFree(aborted Stage F root-watch completion DWORD)"
                        )
                except BaseException as exc:
                    if first is None:
                        first = exc
                watch["completion_bytes"] = 0
        try:
            super().abort()
        except BaseException as exc:
            if first is None:
                first = exc
        self.invalidated = True
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
        "completion_bytes": 0,
        "cancelled": False,
        "cycle": 1,
        "pending": False,
        "completions": [],
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


def _windows_stage_f_start_root_watch(
    state: _WindowsStageFControllerState,
    path: str,
    *,
    ordinal: int,
    recursive: bool,
) -> dict[str, Any]:
    """Acquire one corrected share-compatible watch and leave one request pending."""

    apis = state.apis
    normalized = path.rstrip("\\")
    opened = _orchestrator_utc()
    handle_value = apis["create"](
        path,
        1,
        7,
        None,
        3,
        1109393408,
        None,
    )
    if handle_value in (None, _INVALID_HANDLE_VALUE):
        raise _windows_error("CreateFileW(corrected Stage F root watch)")
    handle = int(handle_value)
    watch: dict[str, Any] = {
        "handle": handle,
        "event": 0,
        "buffer": 0,
        "overlapped": 0,
        "cancelled": False,
    }
    state.watches.append(watch)

    path_buffer = ctypes.create_unicode_buffer(32768)
    path_started = _orchestrator_utc()
    ctypes.set_last_error(0)
    path_count = int(apis["get_final"](handle, path_buffer, 32768, 1))
    path_error = 0 if path_count else ctypes.get_last_error()
    path_completed = _orchestrator_utc()
    if not 0 < path_count < 32768:
        raise _windows_error("GetFinalPathNameByHandleW(corrected root watch)")
    resolved = path_buffer.value.rstrip("\\")
    if resolved.casefold() != normalized.casefold():
        _refuse("corrected root watch resolved to another directory")
    path_raw = ctypes.string_at(ctypes.addressof(path_buffer), 2 * (path_count + 1))

    file_id = _FILE_ID_INFO()
    file_id_started = _orchestrator_utc()
    ctypes.set_last_error(0)
    file_id_ok = bool(
        apis["get_info"](handle, 18, ctypes.byref(file_id), ctypes.sizeof(file_id))
    )
    file_id_error = 0 if file_id_ok else ctypes.get_last_error()
    file_id_completed = _orchestrator_utc()
    if not file_id_ok:
        raise _windows_error("GetFileInformationByHandleEx(FileIdInfo root watch)")
    file_id_raw = ctypes.string_at(ctypes.addressof(file_id), 24)

    attributes = _FILE_ATTRIBUTE_TAG_INFO()
    ctypes.set_last_error(0)
    attribute_ok = bool(
        apis["get_info"](
            handle, 9, ctypes.byref(attributes), ctypes.sizeof(attributes)
        )
    )
    if not attribute_ok:
        raise _windows_error(
            "GetFileInformationByHandleEx(FileAttributeTagInfo root watch)"
        )
    if int(attributes.ReparseTag) != 0 or not int(attributes.FileAttributes) & 0x10:
        _refuse("corrected root watch target is reparse-backed or not a directory")

    buffer = int(apis["virtual_alloc"](None, 65536, 0x3000, 4) or 0)
    overlapped = int(apis["virtual_alloc"](None, 32, 0x3000, 4) or 0)
    completion_bytes = int(apis["virtual_alloc"](None, 4, 0x3000, 4) or 0)
    if (
        not buffer
        or not overlapped
        or not completion_bytes
        or buffer % 4
        or overlapped % 4
        or completion_bytes % 4
    ):
        _refuse("corrected root-watch storage allocation failed or is unaligned")
    watch["buffer"] = buffer
    watch["overlapped"] = overlapped
    watch["completion_bytes"] = completion_bytes
    if (
        ctypes.string_at(buffer, 65536) != bytes(65536)
        or ctypes.string_at(overlapped, 32) != bytes(32)
        or ctypes.string_at(completion_bytes, 4) != bytes(4)
    ):
        _refuse("corrected root-watch storage is not the exact zero preimage")
    event_value = apis["create_event"](None, True, False, None)
    if not event_value:
        raise _windows_error("CreateEventW(corrected root watch)")
    event = int(event_value)
    watch["event"] = event
    resources = (handle, buffer, overlapped, event, completion_bytes)
    if len(set(resources)) != 5:
        _refuse("corrected root-watch resources are not distinct")
    overlapped_view = _OVERLAPPED.from_address(overlapped)
    overlapped_view.hEvent = event

    acquisition = {
        "schema": "stage_f_directory_watch_acquisition/v1",
        "directory_path_identity": _private_path_identity(normalized),
        "create_api": "CreateFileW",
        "create_input_path_identity": _private_path_identity(normalized),
        "create_desired_access": 1,
        "create_share_mode": 7,
        "create_security_attributes": "NULL",
        "create_disposition": 3,
        "create_flags_and_attributes": 1109393408,
        "create_returned_valid_handle": True,
        "directory_handle_value_uint64": handle,
        "opened_utc": opened,
        "path_query_api": "GetFinalPathNameByHandleW_FILE_NAME_NORMALIZED_VOLUME_NAME_GUID",
        "path_query_input_handle_value_uint64": handle,
        "path_query_output_buffer_base_address_uint64": ctypes.addressof(path_buffer),
        "path_query_output_buffer_wchar_capacity": 32768,
        "path_query_returned_wchar_count": path_count,
        "path_query_returned_nonzero": True,
        "path_query_last_error": path_error,
        "path_query_output_bytes_base64": base64.b64encode(path_raw).decode("ascii"),
        "path_query_output_sha256": hashlib.sha256(path_raw).hexdigest(),
        "path_query_started_utc": path_started,
        "path_query_completed_utc": path_completed,
        "path_query_output_identity": _private_path_identity(resolved),
        "file_id_query_api": "GetFileInformationByHandleEx_FileIdInfo",
        "file_id_query_input_handle_value_uint64": handle,
        "file_id_query_output_buffer_base_address_uint64": ctypes.addressof(file_id),
        "file_id_query_output_buffer_capacity": 24,
        "file_id_query_returned_nonzero": True,
        "file_id_query_last_error": file_id_error,
        "file_id_query_output_bytes_base64": base64.b64encode(file_id_raw).decode("ascii"),
        "file_id_query_output_sha256": hashlib.sha256(file_id_raw).hexdigest(),
        "file_id_query_started_utc": file_id_started,
        "file_id_query_completed_utc": file_id_completed,
        "volume_serial_number_uint64": int(file_id.VolumeSerialNumber),
        "file_id_128": bytes(file_id.FileId.Identifier).hex(),
        "attribute_query_api": "GetFileInformationByHandleEx_FileAttributeTagInfo",
        "attribute_query_input_handle_value_uint64": handle,
        "raw_file_attributes": int(attributes.FileAttributes),
        "reparse_tag": 0,
        "directory_attribute_set": True,
        "buffer_allocate_api": "VirtualAlloc",
        "buffer_allocate_address_is_null": True,
        "buffer_allocate_size": 65536,
        "buffer_allocate_type": 12288,
        "buffer_allocate_protection": 4,
        "buffer_allocate_returned_nonzero": True,
        "buffer_base_address_uint64": buffer,
        "buffer_dword_aligned": True,
        "buffer_initial_sha256": hashlib.sha256(bytes(65536)).hexdigest(),
        "overlapped_allocate_api": "VirtualAlloc",
        "overlapped_allocate_address_is_null": True,
        "overlapped_allocate_size": 32,
        "overlapped_allocate_type": 12288,
        "overlapped_allocate_protection": 4,
        "overlapped_allocate_returned_nonzero": True,
        "overlapped_address_uint64": overlapped,
        "overlapped_dword_aligned": True,
        "overlapped_initial_sha256": hashlib.sha256(bytes(32)).hexdigest(),
        "event_create_api": "CreateEventW",
        "event_security_attributes": "NULL",
        "event_manual_reset": True,
        "event_initial_state": False,
        "event_name": "NULL",
        "event_handle_value_uint64": event,
        "overlapped_event_handle_value_uint64": event,
        "all_resources_distinct_and_exclusive": True,
    }
    issued = _orchestrator_utc()
    if not apis["read_changes"](
        handle, buffer, 65536, recursive, 351, None, overlapped, None
    ):
        raise _windows_error("ReadDirectoryChangesW(corrected root watch)")
    transferred = ctypes.c_uint32(0)
    ctypes.set_last_error(0)
    immediate = bool(
        apis["get_overlapped"](
            handle, overlapped, ctypes.byref(transferred), False
        )
    )
    immediate_error = 0 if immediate else ctypes.get_last_error()
    if immediate or immediate_error != 996 or transferred.value != 0:
        _refuse("corrected root watch did not enter the exact pending state")
    watch["pending"] = True
    row = {
        "schema": "stage_f_root_watch/v1",
        "acquisition": acquisition,
        "ordinal": ordinal,
        "role": "EXECUTION_ATTEMPT_ROOT_SUBTREE" if recursive else "ANCHOR_SELF_DIRECT",
        "watched_path_identity": acquisition["directory_path_identity"],
        "recursive": recursive,
        "directory_handle_value_uint64": handle,
        "buffer_base_address_uint64": buffer,
        "buffer_byte_count": 65536,
        "overlapped_address_uint64": overlapped,
        "event_handle_value_uint64": event,
        "notify_filter": 351,
        "buffer_capacity": 65536,
        "completion_bytes_output_address_uint64": completion_bytes,
        "completion_bytes_output_byte_count": 4,
        "notification_filter": 351,
        "resource_identity_reconciles_acquisition": True,
        "read_api": "ReadDirectoryChangesW",
        "read_input_directory_handle_value_uint64": handle,
        "read_input_buffer_base_address_uint64": buffer,
        "read_input_buffer_byte_count": 65536,
        "read_input_watch_subtree": recursive,
        "read_input_notify_filter": 351,
        "read_input_bytes_returned_pointer_is_null": True,
        "read_input_overlapped_address_uint64": overlapped,
        "read_input_completion_routine_is_null": True,
        "read_returned_nonzero": True,
        "immediate_result_api": "GetOverlappedResult",
        "immediate_result_directory_handle_value_uint64": handle,
        "immediate_result_overlapped_address_uint64": overlapped,
        "immediate_result_wait": False,
        "immediate_result_returned_nonzero": False,
        "immediate_result_last_error": 996,
        "immediate_result_bytes_transferred": 0,
        "issued_utc": issued,
        "pending_at_common_epoch": True,
        "overflow_or_enumeration_loss": False,
        "held_through_launch_handoff": True,
    }
    watch["row"] = row
    return row


def _stage_f_record_with_digest(
    record: Mapping[str, Any], digest_field: str
) -> dict[str, Any]:
    """Return one canonical record whose only omitted preimage is its digest."""

    result = dict(record)
    if digest_field in result:
        _refuse(f"record preimage already contains {digest_field}")
    result[digest_field] = hashlib.sha256(canonical_bytes(result)).hexdigest()
    return result


def _stage_f_current_process_instance(apis: Mapping[str, Any]) -> tuple[int, int]:
    pid = int(apis["get_process_id"]())
    if not 0 < pid <= 0xFFFFFFFF:
        _refuse("Stage F controller process ID is invalid")
    creation, exit_time, kernel_time, user_time = (_ORCH_FILETIME() for _ in range(4))
    if not apis["get_process_times"](
        apis["current_process"](),
        ctypes.byref(creation),
        ctypes.byref(exit_time),
        ctypes.byref(kernel_time),
        ctypes.byref(user_time),
    ):
        raise _windows_error("GetProcessTimes(Stage F controller)")
    creation_value = _filetime_uint64(creation)
    if creation_value <= 0:
        _refuse("Stage F controller creation FILETIME is zero")
    return pid, creation_value


def _stage_f_ticket_identity(ticket: Mapping[str, Any]) -> dict[str, str]:
    return verify_embedded_digest(
        ticket, "ticket_sha256", kind="stage_f_authorized_mutation_ticket/v1"
    )


def _stage_f_new_root_ticket(
    apis: Mapping[str, Any],
    attempt_path: str,
    *,
    root_protection_epoch_identity: Mapping[str, Any],
    ledger_mutation_entry_identity: Mapping[str, Any],
) -> dict[str, Any]:
    issued = datetime.now(timezone.utc)
    expires = issued + timedelta(minutes=5)
    pid = int(apis["get_process_id"]())
    thread_id = int(apis["get_thread_id"]())
    transaction = sha256_identity(
        "stage_f_attempt_root_creation_transaction/v1",
        canonical_bytes(
            {
                "attempt_path_identity": _private_path_identity(attempt_path),
                "actor_process_id": pid,
                "actor_thread_id": thread_id,
                "issued_utc": issued.isoformat(timespec="microseconds").replace(
                    "+00:00", "Z"
                ),
            }
        ),
    )
    return _stage_f_record_with_digest(
        {
            "schema": "stage_f_authorized_mutation_ticket/v1",
            "transaction_identity": transaction,
            "ordinal": 1,
            "actor_process_id": pid,
            "actor_thread_id": thread_id,
            "operation": "CREATE_ATTEMPT_ROOT",
            "temporary_path_identity": None,
            "final_path_identity": _private_path_identity(attempt_path),
            "expected_old_file_id_128": None,
            "expected_new_file_id_128": None,
            "expected_byte_count": 0,
            "expected_sha256": None,
            "permitted_watch_actions": ["FILE_ACTION_ADDED"],
            "permitted_usn_reason_mask": 0x80000100,
            "issued_utc": issued.isoformat(timespec="microseconds").replace(
                "+00:00", "Z"
            ),
            "expires_utc": expires.isoformat(timespec="microseconds").replace(
                "+00:00", "Z"
            ),
            "single_use_required": True,
            "scientific_mutation_authority_identity": None,
            "scientific_mutation_authority_projection": None,
            "root_protection_epoch_identity": dict(root_protection_epoch_identity),
            "ledger_mutation_transaction_identity": dict(
                ledger_mutation_entry_identity
            ),
            "campaign_authorization_identity": None,
            "route_id": None,
            "ticket_watch_usn_ledger_join_kind": "ROOT_EPOCH_TRANSACTION_TICKET_WATCH_USN_LEDGER_BIJECTION",
        },
        "ticket_sha256",
    )


_STAGE_F_NOTIFY_ACTION_NAMES = {
    1: "FILE_ACTION_ADDED",
    2: "FILE_ACTION_REMOVED",
    3: "FILE_ACTION_MODIFIED",
    4: "FILE_ACTION_RENAMED_OLD_NAME",
    5: "FILE_ACTION_RENAMED_NEW_NAME",
}


def _stage_f_parse_notify_records(
    raw: bytes,
    *,
    expected_name: str,
    ticket_identity: Mapping[str, Any],
) -> list[dict[str, Any]]:
    if not raw:
        _refuse("completed Stage F root watch returned no bytes")
    rows: list[dict[str, Any]] = []
    offset = 0
    while offset < len(raw):
        if len(raw) - offset < 12 or offset % 4:
            _refuse("FILE_NOTIFY_INFORMATION header is truncated or unaligned")
        next_offset, action, name_count = struct.unpack_from("<III", raw, offset)
        if action not in _STAGE_F_NOTIFY_ACTION_NAMES or name_count % 2:
            _refuse("FILE_NOTIFY_INFORMATION action/name length differs")
        minimum = 12 + name_count
        record_count = next_offset if next_offset else len(raw) - offset
        if (
            record_count < minimum
            or offset + record_count > len(raw)
            or (next_offset and next_offset % 4)
        ):
            _refuse("FILE_NOTIFY_INFORMATION record bounds differ")
        name_raw = raw[offset + 12 : offset + 12 + name_count]
        try:
            name = name_raw.decode("utf-16le", "strict")
        except UnicodeDecodeError as exc:
            raise BindingRefusal(
                "FILE_NOTIFY_INFORMATION name is not strict UTF-16LE"
            ) from exc
        record_raw = raw[offset : offset + record_count]
        authorized = (
            name.casefold() == expected_name.casefold()
            and action == 1
            and len(rows) == 0
        )
        rows.append(
            {
                "buffer_ordinal": len(rows) + 1,
                "record_offset": offset,
                "next_entry_offset": next_offset,
                "action_uint32": action,
                "action": _STAGE_F_NOTIFY_ACTION_NAMES[action],
                "file_name_length_bytes": name_count,
                "file_name_utf16le_base64": base64.b64encode(name_raw).decode(
                    "ascii"
                ),
                "name": name,
                "record_byte_count": record_count,
                "raw_record_bytes_base64": base64.b64encode(record_raw).decode(
                    "ascii"
                ),
                "raw_record_sha256": hashlib.sha256(record_raw).hexdigest(),
                "scope_disposition": (
                    "AUTHORIZED_TICKET_MATCH"
                    if authorized
                    else "REFUSED_PROTECTED_MUTATION"
                ),
                "protected_identity_match_count": 1,
                "mutation_ticket_identity": (
                    dict(ticket_identity) if authorized else None
                ),
                "mutation_ticket_match_count": 1 if authorized else 0,
            }
        )
        if not next_offset:
            offset = len(raw)
        else:
            offset += next_offset
    if len(rows) != 1 or rows[0]["scope_disposition"] != "AUTHORIZED_TICKET_MATCH":
        _refuse("attempt-root watch completion is not exactly one authorized add")
    return rows


def _windows_stage_f_complete_and_reissue_root_creation_watch(
    state: _WindowsStageFControllerState,
    watch: dict[str, Any],
    *,
    expected_name: str,
    ticket_identity: Mapping[str, Any],
) -> dict[str, Any]:
    """Drain exactly one root-creation notification and re-enter pending state."""

    if watch.get("pending") is not True or watch.get("cycle") != 1:
        _refuse("attempt-root parent watch is not in its first pending cycle")
    apis = state.apis
    completion_bytes = int(watch.get("completion_bytes", 0) or 0)
    if not completion_bytes or ctypes.string_at(completion_bytes, 4) != bytes(4):
        _refuse("attempt-root watch completion DWORD preimage is not exactly zero")
    if not apis["get_overlapped"](
        watch["handle"],
        watch["overlapped"],
        ctypes.c_void_p(completion_bytes),
        True,
    ):
        raise _windows_error("GetOverlappedResult(attempt-root creation)")
    completed = _orchestrator_utc()
    transferred_raw = ctypes.string_at(completion_bytes, 4)
    transferred_value = int.from_bytes(transferred_raw, "little", signed=False)
    if not 0 < transferred_value <= 65536:
        _refuse("attempt-root parent watch completed with an invalid byte count")
    raw = ctypes.string_at(watch["buffer"], transferred_value)
    records = _stage_f_parse_notify_records(
        raw, expected_name=expected_name, ticket_identity=ticket_identity
    )
    if not apis["reset_event"](watch["event"]):
        raise _windows_error("ResetEvent(attempt-root parent watch)")
    ctypes.memset(watch["buffer"], 0, 65536)
    ctypes.memset(watch["overlapped"], 0, 32)
    ctypes.memset(completion_bytes, 0, 4)
    if ctypes.string_at(watch["buffer"], 65536) != bytes(65536):
        _refuse("attempt-root parent watch buffer did not return to zero")
    overlapped = _OVERLAPPED.from_address(watch["overlapped"])
    overlapped.hEvent = watch["event"]
    ready = ctypes.string_at(watch["overlapped"], 32)
    if not apis["read_changes"](
        watch["handle"],
        watch["buffer"],
        65536,
        False,
        351,
        None,
        watch["overlapped"],
        None,
    ):
        raise _windows_error("ReadDirectoryChangesW(reissue attempt-root parent)")
    ctypes.set_last_error(0)
    immediate = bool(
        apis["get_overlapped"](
            watch["handle"],
            watch["overlapped"],
            ctypes.c_void_p(completion_bytes),
            False,
        )
    )
    immediate_error = 0 if immediate else ctypes.get_last_error()
    reissued = _orchestrator_utc()
    reissue_raw = ctypes.string_at(completion_bytes, 4)
    if immediate or immediate_error != 996 or reissue_raw != bytes(4):
        _refuse("attempt-root parent watch reissue is not pending")
    row = {
        "schema": "stage_f_root_watch_completion_observation/v1",
        "watch_ordinal": watch["row"]["ordinal"],
        "cycle_ordinal": 1,
        "directory_handle_value_uint64": watch["handle"],
        "buffer_base_address_uint64": watch["buffer"],
        "overlapped_address_uint64": watch["overlapped"],
        "event_handle_value_uint64": watch["event"],
        "completion_api": "GetOverlappedResult",
        "completion_directory_handle_value_uint64": watch["handle"],
        "completion_overlapped_address_uint64": watch["overlapped"],
        "completion_wait": True,
        "completion_returned_nonzero": True,
        "completion_bytes_transferred": transferred_value,
        "raw_buffer_bytes_base64": base64.b64encode(raw).decode("ascii"),
        "raw_buffer_byte_count": len(raw),
        "raw_buffer_sha256": hashlib.sha256(raw).hexdigest(),
        "records": records,
        "record_count": len(records),
        "strict_parser_projection_exact": True,
        "overflow_or_enumeration_loss": False,
        "authorized_ticket_match_count": 1,
        "outside_scope_record_count": 0,
        "refused_protected_record_count": 0,
        "completed_utc": completed,
        "reset_event_api": "ResetEvent",
        "reset_event_input_handle_value_uint64": watch["event"],
        "reset_event_returned_nonzero": True,
        "buffer_zeroed_sha256": hashlib.sha256(bytes(65536)).hexdigest(),
        "overlapped_zeroed_sha256": hashlib.sha256(bytes(32)).hexdigest(),
        "overlapped_ready_bytes_base64": base64.b64encode(ready).decode("ascii"),
        "overlapped_ready_sha256": hashlib.sha256(ready).hexdigest(),
        "overlapped_event_assignment_handle_value_uint64": watch["event"],
        "reissue_api": "ReadDirectoryChangesW",
        "reissue_directory_handle_value_uint64": watch["handle"],
        "reissue_buffer_base_address_uint64": watch["buffer"],
        "reissue_buffer_byte_count": 65536,
        "reissue_watch_subtree": False,
        "reissue_notify_filter": 351,
        "reissue_bytes_returned_pointer_is_null": True,
        "reissue_overlapped_address_uint64": watch["overlapped"],
        "reissue_completion_routine_is_null": True,
        "reissue_returned_nonzero": True,
        "reissue_immediate_result_api": "GetOverlappedResult",
        "reissue_immediate_directory_handle_value_uint64": watch["handle"],
        "reissue_immediate_overlapped_address_uint64": watch["overlapped"],
        "reissue_immediate_wait": False,
        "reissue_immediate_returned_nonzero": False,
        "reissue_immediate_last_error": 996,
        "reissue_immediate_bytes_transferred": 0,
        "reissued_pending_utc": reissued,
        "role": watch["row"]["role"],
        "recursive": watch["row"]["recursive"],
        "buffer_capacity": 65536,
        "notification_filter": 351,
        "watch_subtree": watch["row"]["recursive"],
        "completion_bytes_output_address_uint64": completion_bytes,
        "completion_bytes_output_input_bytes_base64": "AAAAAA==",
        "completion_bytes_output_input_sha256": _LEDGER_FIXED_ZERO_HASHES[4],
        "completion_bytes_output_bytes_base64": base64.b64encode(
            transferred_raw
        ).decode("ascii"),
        "completion_bytes_output_sha256": hashlib.sha256(
            transferred_raw
        ).hexdigest(),
        "completion_bytes_output_decoded_equals_completion_bytes_transferred": True,
        "raw_buffer_capacity": 65536,
        "raw_buffer_returned_slice_equals_completion_count": True,
        "buffer_zeroed_bytes_base64": base64.b64encode(bytes(65536)).decode(
            "ascii"
        ),
        "overlapped_zeroed_bytes_base64": base64.b64encode(bytes(32)).decode(
            "ascii"
        ),
        "completion_capture_and_reconciliation_completed_utc": completed,
        "reissue_started_utc": completed,
        "reissue_cycle_ordinal": 2,
        "reissue_pending_request_count": 1,
        "resources_reconcile_originating_watch_and_preceding_cycle": True,
    }
    watch["cycle"] = 2
    watch["pending"] = True
    watch["completions"].append(row)
    return row


def _stage_f_root_anchor_projection(
    state: _WindowsStageFControllerState,
    anchor: Mapping[str, Any],
    *,
    ordinal: int,
    role: str,
) -> dict[str, Any]:
    row = _mapping(anchor["row"], f"Stage F root anchor {ordinal}")
    handle = int(anchor["handle"])
    guard = int(anchor["guard"])
    if not state.apis["compare"](handle, guard):
        raise _windows_error("CompareObjectHandles(Stage F root anchor)")
    security = _mapping(
        row["security_descriptor_query_lifecycle"],
        f"Stage F root anchor {ordinal} security",
    )
    return {
        "ordinal": ordinal,
        "role": role,
        "path_identity": row["anchor_path_identity"],
        "parent_ordinal": None if ordinal == 1 else ordinal - 1,
        "anchor_handle_value_uint64": handle,
        "continuity_guard_handle_value_uint64": guard,
        "compare_object_handles_at_epoch": True,
        "volume_serial_number_uint64": row["volume_serial_number"],
        "file_id_128": row["file_id_128"],
        "raw_file_attributes": row["raw_file_attributes"],
        "reparse_tag": row["reparse_tag"],
        "security_information_mask": security["security_information_mask"],
        "security_descriptor_byte_count": security[
            "security_descriptor_byte_count"
        ],
        "security_descriptor_sha256": security["security_descriptor_sha256"],
        "held_through_launch_handoff": True,
    }


def _stage_f_open_and_measure_immutable_file(
    state: _WindowsStageFControllerState,
    manifest_row_value: Any,
) -> dict[str, Any]:
    row = _mapping(manifest_row_value, "Stage F immutable authority manifest row")
    _exact_fields(
        row,
        frozenset(("relative_path", "path", "byte_count", "sha256")),
        "Stage F immutable authority manifest row",
    )
    relative = row["relative_path"]
    path = row["path"]
    if (
        type(relative) is not str
        or not relative
        or unicodedata.normalize("NFC", relative) != relative
        or type(path) is not str
        or unicodedata.normalize("NFC", path) != path
    ):
        _refuse("Stage F immutable authority path is not exact NFC text")
    expected_count = _uint(
        row["byte_count"], 64, "Stage F immutable authority byte count"
    )
    expected_sha = _sha256(row["sha256"], "Stage F immutable authority SHA-256")
    apis = state.apis
    raw_handle = apis["create"](
        path, 0x80000080, 1, None, 3, 0x00200000, None
    )
    if raw_handle in (None, _INVALID_HANDLE_VALUE):
        raise _windows_error("CreateFileW(Stage F immutable authority lock)")
    handle = int(raw_handle)
    file_state: dict[str, Any] = {"path": path, "handle": handle}
    state.files.append(file_state)
    projection = _host_runtime_handle_projection(apis, handle)
    if (
        projection["resolved_path"].casefold() != path.rstrip("\\").casefold()
        or projection["directory"]
        or projection["delete_pending"]
        or projection["number_of_links"] != 1
        or projection["reparse_tag"] != 0
        or projection["end_of_file"] != expected_count
    ):
        _refuse("Stage F immutable authority handle identity/type differs")
    raw = _host_runtime_read_handle(apis, handle, expected_count)
    digest = hashlib.sha256(raw).hexdigest()
    if digest != expected_sha:
        _refuse("Stage F immutable authority held-handle bytes differ")
    state.private_materials[relative] = raw
    result = {
        "relative_path": relative,
        "path_identity": _private_path_identity(projection["resolved_path"]),
        "handle_value_uint64": handle,
        "volume_serial_number_uint64": projection["volume_serial_number"],
        "file_id_128": projection["file_id_128"],
        "byte_count": expected_count,
        "sha256": digest,
        "share_mode": 1,
        "locked_before_first_read": True,
        "held_through_launch_handoff": True,
    }
    file_state["row"] = result
    return result


def _stage_f_check_root_watches_pending(
    state: _WindowsStageFControllerState,
) -> str:
    for ordinal, watch in enumerate(state.watches, 1):
        transferred = ctypes.c_uint32(0)
        ctypes.set_last_error(0)
        completed = bool(
            state.apis["get_overlapped"](
                watch["handle"],
                watch["overlapped"],
                ctypes.byref(transferred),
                False,
            )
        )
        error = 0 if completed else ctypes.get_last_error()
        if completed or error != 996 or transferred.value != 0:
            _refuse(
                f"Stage F root watch {ordinal} is not quiet/pending at common epoch"
            )
        watch["pending"] = True
    return _orchestrator_utc()


def _stage_f_root_usn_classifier(
    state: _WindowsStageFControllerState,
) -> Callable[[Mapping[str, Any]], Mapping[str, Any]]:
    if not state.anchors or state.root_mutation_ticket is None:
        _refuse("Stage F root USN classifier lacks retained anchor/ticket state")
    root_id = state.anchors[-1]["row"]["file_id_128"]
    parent_id = next(
        anchor["row"]["file_id_128"]
        for anchor in state.anchors
        if anchor["path"].casefold()
        == str(PureWindowsPath(state.attempt_root).parent).rstrip("\\").casefold()
    )
    basename = PureWindowsPath(state.attempt_root).name
    protected_ids = {
        anchor["row"]["file_id_128"] for anchor in state.anchors
    }
    ticket_identity = _stage_f_ticket_identity(state.root_mutation_ticket)
    permitted_mask = state.root_mutation_ticket["permitted_usn_reason_mask"]

    def classify(record: Mapping[str, Any]) -> Mapping[str, Any]:
        child = record["file_reference_number"]
        parent = record["parent_file_reference_number"]
        authorized = (
            child == root_id
            and parent == parent_id
            and record["file_name"].casefold() == basename.casefold()
            and record["reason_mask"] != 0
            and record["reason_mask"] & ~permitted_mask == 0
        )
        if authorized:
            return {
                "scope_disposition": "AUTHORIZED_TICKET_MATCH",
                "protected_identity_match_count": 1,
                "mutation_ticket_identity": dict(ticket_identity),
                "mutation_ticket_match_count": 1,
                "mutation_transaction_identity": dict(
                    state.root_mutation_ticket["transaction_identity"]
                ),
                "ledger_mutation_entry_identity": dict(
                    state.root_mutation_ticket["ledger_mutation_transaction_identity"]
                ),
            }
        if child in protected_ids or parent in protected_ids:
            return {
                "scope_disposition": "REFUSED_PROTECTED_MUTATION",
                "protected_identity_match_count": 1,
                "mutation_ticket_identity": None,
                "mutation_ticket_match_count": 0,
                "mutation_transaction_identity": None,
                "ledger_mutation_entry_identity": None,
            }
        return {
            "scope_disposition": "OUTSIDE_PROTECTED_SCOPE",
            "protected_identity_match_count": 0,
            "mutation_ticket_identity": None,
            "mutation_ticket_match_count": 0,
            "mutation_transaction_identity": None,
            "ledger_mutation_entry_identity": None,
        }

    return classify


def _stage_f_live_phase_result(
    state: _WindowsStageFControllerState,
    rows: Sequence[Mapping[str, Any]],
    observation: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "state_token": state,
        "control_records": [dict(row) for row in rows],
        "observation": dict(observation),
        "scientific_counters": dict(ZERO_SCIENCE_COUNTERS),
    }


def _windows_stage_f_incept_fresh_attempt_root(
    *,
    controller_input: Mapping[str, Any],
    state_token: Any,
    control_records: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Create one fresh attempt root under a pending parent watch and USN START."""

    if state_token is not None or control_records:
        _refuse("Stage F root inception requires a fresh empty controller epoch")
    validate_definition = controller_input.get("_stage_f_validate_definition")
    phase_materials = controller_input.get("_stage_f_phase_materials")
    if not callable(validate_definition) or not isinstance(phase_materials, Mapping):
        _refuse(
            "Stage F root inception requires the exact schema validator and phase materials"
        )
    incept_material = phase_materials.get("incept_fresh_attempt_root")
    if callable(incept_material):
        incept_material = incept_material(phase="incept_fresh_attempt_root")
    incept_material = _mapping(incept_material, "Stage F root-inception material")
    _exact_fields(
        incept_material,
        frozenset(("root_mutation_ticket",)),
        "Stage F root-inception material",
    )
    root_mutation_ticket = _mapping(
        incept_material["root_mutation_ticket"],
        "Stage F root-inception mutation ticket",
    )
    validate_definition("stage_f_authorized_mutation_ticket", root_mutation_ticket)
    _validate_mutation_ticket_semantics(
        root_mutation_ticket, "Stage F root-inception mutation ticket"
    )
    selected_volume = controller_input.get("selected_volume_guid_path")
    campaign_parent = controller_input.get("campaign_parent_path")
    attempt_root = controller_input.get("attempt_root_path")
    if not all(type(value) is str for value in (selected_volume, campaign_parent, attempt_root)):
        _refuse("Stage F root inception paths are missing")
    selected_volume = str(selected_volume)
    campaign_parent = str(campaign_parent).rstrip("\\")
    attempt_root = str(attempt_root).rstrip("\\")
    if (
        unicodedata.normalize("NFC", campaign_parent) != campaign_parent
        or unicodedata.normalize("NFC", attempt_root) != attempt_root
        or not selected_volume.endswith("\\")
        or str(PureWindowsPath(attempt_root).parent).rstrip("\\").casefold()
        != campaign_parent.casefold()
    ):
        _refuse("Stage F attempt root is not one exact NFC campaign-parent child")
    _refuse(
        "committed v3 authority is circular for CREATE_ATTEMPT_ROOT: the immutable "
        "pre-use mutation ticket requires the exact root-protection epoch identity, "
        "but that epoch digest includes post-create genesis/USN evidence; refusing "
        "before Win32 handle acquisition or filesystem mutation"
    )
    injected_apis = controller_input.get("_stage_f_win32_apis")
    apis = injected_apis if injected_apis is not None else _host_runtime_apis()
    state = _WindowsStageFControllerState(apis)
    state.validate_definition = validate_definition
    state.phase_materials = phase_materials
    state.attempt_root = attempt_root
    state.protection_started_utc = _orchestrator_utc()
    state.holder_process_id, state.holder_creation_filetime = (
        _stage_f_current_process_instance(apis)
    )
    try:
        parent_paths = _host_runtime_path_parts(campaign_parent)
        if parent_paths[0].casefold() != selected_volume.rstrip("\\").casefold():
            _refuse("campaign parent is not rooted at the selected volume GUID")
        for ordinal, path in enumerate(parent_paths, 1):
            _host_runtime_open_anchor(
                state, path, ordinal=ordinal, count=len(parent_paths) + 1
            )
        for ordinal, path in enumerate(parent_paths[1:], 1):
            _windows_stage_f_start_root_watch(
                state, path, ordinal=ordinal, recursive=False
            )
        parent_watch = state.watches[-1]
        usn_factory = controller_input.get("_stage_f_usn_backend_factory")
        usn_apis = controller_input.get("_stage_f_usn_apis")
        if usn_factory is None:
            state.usn_backend = StageFUsnJournalBackend(
                selected_volume, apis=usn_apis
            )
        else:
            if not callable(usn_factory):
                _refuse("Stage F USN backend factory is not callable")
            state.usn_backend = usn_factory(selected_volume)
        state.usn_start_record = state.usn_backend.begin_range()
        ctypes.set_last_error(0)
        attributes = int(apis["get_attributes"](attempt_root))
        absent_error = ctypes.get_last_error()
        if attributes != 0xFFFFFFFF or absent_error != 2:
            _refuse("Stage F execution-attempt root is not freshly absent")
        state.root_mutation_ticket = dict(root_mutation_ticket)
        if (
            state.root_mutation_ticket.get("operation") != "CREATE_ATTEMPT_ROOT"
            or state.root_mutation_ticket.get("actor_process_id")
            != state.holder_process_id
            or state.root_mutation_ticket.get("final_path_identity")
            != _private_path_identity(attempt_root)
        ):
            _refuse("Stage F root-inception mutation ticket target or actor differs")
        if not apis["create_directory"](attempt_root, None):
            raise _windows_error("CreateDirectoryW(Stage F attempt root)")
        created = _orchestrator_utc()
        _host_runtime_open_anchor(
            state,
            attempt_root,
            ordinal=len(parent_paths) + 1,
            count=len(parent_paths) + 1,
        )
        _windows_stage_f_start_root_watch(
            state,
            attempt_root,
            ordinal=len(state.watches) + 1,
            recursive=True,
        )
        state.parent_creation_completion = (
            _windows_stage_f_complete_and_reissue_root_creation_watch(
                state,
                parent_watch,
                expected_name=PureWindowsPath(attempt_root).name,
                ticket_identity=_stage_f_ticket_identity(
                    state.root_mutation_ticket
                ),
            )
        )
        common_pending = _stage_f_check_root_watches_pending(state)
        root_projection = _host_runtime_handle_projection(
            apis, int(state.anchors[-1]["handle"])
        )
        parent_watch_identity = sha256_identity(
            "stage_f_directory_watch_acquisition/v1",
            parent_watch["row"]["acquisition"],
        )
        state.genesis = _stage_f_record_with_digest(
            {
                "schema": "stage_f_execution_attempt_genesis/v1",
                "campaign_parent_path_identity": _private_path_identity(
                    campaign_parent
                ),
                "attempt_path_identity": _private_path_identity(attempt_root),
                "attempt_absent_observation": "GetFileAttributesW_INVALID_FILE_ATTRIBUTES_ERROR_FILE_NOT_FOUND",
                "parent_watch_identity": parent_watch_identity,
                "create_api": "CreateDirectoryW",
                "create_returned_nonzero": True,
                "created_once": True,
                "attempt_root_file_id_128": root_projection["file_id_128"],
                "attempt_root_volume_serial_number_uint64": root_projection[
                    "volume_serial_number"
                ],
                "created_utc": created,
                "scientific_counters": dict(ZERO_SCIENCE_COUNTERS),
            },
            "genesis_sha256",
        )
        validate_definition("stage_f_execution_attempt_genesis", state.genesis)
        genesis_row = {
            "definition": "stage_f_execution_attempt_genesis",
            "record": state.genesis,
        }
        state.control_records.append(genesis_row)
        state.completed_live_phases.append("incept_fresh_attempt_root")
        state.root_active = True
        return _stage_f_live_phase_result(
            state,
            [genesis_row],
            {
                "fresh_directory_created_once": True,
                "parent_watch_pending_before_absence_check": True,
                "ancestor_parent_volume_protection_before_create": True,
                "direct_watch_count": sum(
                    not item["row"]["recursive"] for item in state.watches
                ),
                "recursive_watch_count": sum(
                    item["row"]["recursive"] for item in state.watches
                ),
                "all_watches_pending": True,
                "usn_start_query_complete": True,
                "private_byte_read_count_before_genesis": 0,
                "parent_creation_watch_completion": state.parent_creation_completion,
                "common_pending_check_utc": common_pending,
            },
        )
    except BaseException:
        try:
            state.abort()
        except BaseException:
            pass
        raise


def _windows_stage_f_acquire_root_and_volume_epoch(
    *,
    controller_input: Mapping[str, Any],
    state_token: Any,
    control_records: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Lock and measure all immutable inputs, close USN, and publish root epoch."""

    if not isinstance(state_token, _WindowsStageFControllerState):
        _refuse("Stage F root epoch lacks its retained Win32 state")
    state = state_token
    if (
        not state.root_active
        or state.invalidated
        or state.root_epoch is not None
        or state.genesis is None
        or state.root_mutation_ticket is None
        or state.usn_backend is None
        or len(control_records) != 1
        or state.completed_live_phases != ["incept_fresh_attempt_root"]
        or [dict(row) for row in control_records] != state.control_records
    ):
        _refuse("Stage F root epoch state/order differs")
    manifests = controller_input.get("immutable_authority_files")
    if type(manifests) is not list or not manifests:
        _refuse("Stage F root epoch requires immutable authority file manifest rows")
    locks = [
        _stage_f_open_and_measure_immutable_file(state, manifest)
        for manifest in manifests
    ]
    usn_range = state.usn_backend.collect_range(
        _stage_f_root_usn_classifier(state)
    )
    common_pending = _stage_f_check_root_watches_pending(state)
    campaign_parent = str(controller_input["campaign_parent_path"]).rstrip("\\")
    anchor_rows: list[dict[str, Any]] = []
    for ordinal, anchor in enumerate(state.anchors, 1):
        if ordinal == 1:
            role = "SELECTED_VOLUME_ROOT"
        elif ordinal == len(state.anchors):
            role = "EXECUTION_ATTEMPT_ROOT"
        elif anchor["path"].casefold() == campaign_parent.casefold():
            role = "CAMPAIGN_PARENT"
        else:
            role = "INTERMEDIATE"
        anchor_rows.append(
            _stage_f_root_anchor_projection(
                state, anchor, ordinal=ordinal, role=role
            )
        )
    state.root_epoch = _stage_f_record_with_digest(
        {
            "schema": "stage_f_root_protection_epoch/v1",
            "execution_attempt_genesis": state.genesis,
            "holder_process_id": state.holder_process_id,
            "holder_process_creation_filetime_uint64": state.holder_creation_filetime,
            "anchors": anchor_rows,
            "anchor_count": len(anchor_rows),
            "watches": [dict(item["row"]) for item in state.watches],
            "watch_count": len(state.watches),
            "immutable_file_locks": locks,
            "immutable_file_lock_count": len(locks),
            "usn_start_observation": usn_range,
            "common_pending_check_utc": common_pending,
            "protection_epoch_started_utc": state.protection_started_utc,
            "active_through_launch_handoff": True,
            "scientific_counters": dict(ZERO_SCIENCE_COUNTERS),
        },
        "epoch_sha256",
    )
    if state.validate_definition is None:
        _refuse("Stage F root epoch lost its schema validator")
    state.validate_definition("stage_f_root_protection_epoch", state.root_epoch)
    root_identity = _embedded_record_identity(
        state.root_epoch,
        "epoch_sha256",
        kind="stage_f_root_protection_epoch/v1",
    )
    if state.root_mutation_ticket.get("root_protection_epoch_identity") != root_identity:
        _refuse(
            "Stage F attempt-root mutation ticket does not identify the completed root epoch"
        )
    rows = [
        {
            "definition": "stage_f_root_protection_epoch",
            "record": state.root_epoch,
        },
        {
            "definition": "stage_f_authorized_mutation_ticket",
            "record": state.root_mutation_ticket,
        },
        {
            "definition": "stage_f_usn_journal_range",
            "record": usn_range,
        },
    ]
    state.control_records.extend(rows)
    state.completed_live_phases.append("acquire_root_and_volume_epoch")
    return _stage_f_live_phase_result(
        state,
        rows,
        {
            "root_volume_handles_watches_and_usn_retained": True,
            "direct_watch_count": sum(
                not item["row"]["recursive"] for item in state.watches
            ),
            "recursive_watch_count": sum(
                item["row"]["recursive"] for item in state.watches
            ),
            "all_watches_pending": True,
            "usn_start_query_complete": True,
            "private_byte_read_count_before_root_protection_start": 0,
            "immutable_file_lock_count": len(locks),
            "common_pending_check_utc": common_pending,
        },
    )


def _windows_stage_f_read_locked_authority_materials(
    *,
    controller_input: Mapping[str, Any],
    state_token: Any,
    control_records: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Expose only held-handle measurements; private bytes remain controller-owned."""

    del controller_input
    if (
        not isinstance(state_token, _WindowsStageFControllerState)
        or state_token.root_epoch is None
        or not state_token.private_materials
        or state_token.invalidated
        or state_token.completed_live_phases
        != ["incept_fresh_attempt_root", "acquire_root_and_volume_epoch"]
        or [dict(row) for row in control_records] != state_token.control_records
    ):
        _refuse("Stage F immutable material read lacks a completed root epoch")
    state_token.private_reads_started = True
    state_token.completed_live_phases.append("read_locked_authority_materials")
    return _stage_f_live_phase_result(
        state_token,
        [],
        {
            "private_materials_read_only_after_root_protection_started": True,
            "all_consumed_files_locked_before_read": True,
            "all_file_handles_retained": True,
            "private_material_count": len(state_token.private_materials),
            "private_material_measurements": [
                {
                    "relative_path": row["row"]["relative_path"],
                    "byte_count": row["row"]["byte_count"],
                    "sha256": row["row"]["sha256"],
                }
                for row in state_token.files
            ],
        },
    )


_STAGE_F_MATERIAL_FIELDS = frozenset(
    ("preappend_control_records", "ledger_appends", "postappend_control_records", "observation")
)
_STAGE_F_LEDGER_APPEND_MATERIAL_FIELDS = frozenset(
    ("append_ticket", "entry", "parent_watch_range_sha256", "usn_range_sha256")
)


def _stage_f_require_live_state(
    state_token: Any,
    control_records: Sequence[Mapping[str, Any]],
    *,
    preceding_phase: str,
) -> _WindowsStageFControllerState:
    if not isinstance(state_token, _WindowsStageFControllerState):
        _refuse(f"Stage F {preceding_phase} successor lacks retained Win32 state")
    state = state_token
    if (
        state.invalidated
        or state.released
        or not state.root_active
        or state.root_epoch is None
        or state.validate_definition is None
        or state.phase_materials is None
        or not state.completed_live_phases
        or state.completed_live_phases[-1] != preceding_phase
        or [dict(row) for row in control_records] != state.control_records
    ):
        _refuse(
            f"Stage F live state/order/control continuity differs after {preceding_phase}"
        )
    return state


def _stage_f_phase_material(
    state: _WindowsStageFControllerState,
    phase: str,
    *,
    context: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    assert state.phase_materials is not None
    if phase not in state.phase_materials:
        _refuse(f"Stage F {phase} exact raw material is absent")
    value = state.phase_materials[phase]
    if callable(value):
        value = value(
            phase=phase,
            context=dict(context or {}),
            control_records=tuple(dict(row) for row in state.control_records),
        )
    return _mapping(value, f"Stage F {phase} material")


def _stage_f_validate_control_rows(
    state: _WindowsStageFControllerState,
    rows_value: Any,
    label: str,
) -> list[dict[str, Any]]:
    if type(rows_value) is not list:
        _refuse(f"{label} is not an exact control-record array")
    assert state.validate_definition is not None
    rows: list[dict[str, Any]] = []
    for ordinal, row_value in enumerate(rows_value, 1):
        row = _mapping(row_value, f"{label}[{ordinal}]")
        _exact_fields(row, _CONTROL_ROW_FIELDS, f"{label}[{ordinal}]")
        definition = row["definition"]
        if definition not in _CONTROL_ALLOWED_DEFINITIONS:
            _refuse(f"{label}[{ordinal}] publishes an unauthorized definition")
        record = _mapping(row["record"], f"{label}[{ordinal}].record")
        state.validate_definition(definition, record)
        _validate_science_counters_recursively(record, f"{label}[{ordinal}].record")
        rows.append({"definition": definition, "record": dict(record)})
    return rows


def _stage_f_apply_exact_material(
    state: _WindowsStageFControllerState,
    phase: str,
    material_value: Mapping[str, Any],
    *,
    require_ledger_appends: bool,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    material = _mapping(material_value, f"Stage F {phase} material")
    _exact_fields(material, _STAGE_F_MATERIAL_FIELDS, f"Stage F {phase} material")
    before = _stage_f_validate_control_rows(
        state,
        material["preappend_control_records"],
        f"Stage F {phase} preappend records",
    )
    after = _stage_f_validate_control_rows(
        state,
        material["postappend_control_records"],
        f"Stage F {phase} postappend records",
    )
    append_values = material["ledger_appends"]
    if type(append_values) is not list:
        _refuse(f"Stage F {phase} ledger appends are not an exact array")
    if require_ledger_appends and not append_values:
        _refuse(f"Stage F {phase} lacks its required retained-ledger append")
    if append_values and state.ledger_backend is None:
        _refuse(f"Stage F {phase} lacks the retained ledger backend")
    rows = list(before)
    assert state.validate_definition is not None
    for ordinal, append_value in enumerate(append_values, 1):
        append_material = _mapping(
            append_value, f"Stage F {phase} ledger append {ordinal}"
        )
        _exact_fields(
            append_material,
            _STAGE_F_LEDGER_APPEND_MATERIAL_FIELDS,
            f"Stage F {phase} ledger append {ordinal}",
        )
        ticket = _mapping(
            append_material["append_ticket"],
            f"Stage F {phase} ledger append ticket {ordinal}",
        )
        entry = _mapping(
            append_material["entry"],
            f"Stage F {phase} ledger entry {ordinal}",
        )
        state.validate_definition("stage_f_ledger_append_ticket", ticket)
        state.validate_definition(
            "stage_f_evidence_ledger_genesis"
            if entry.get("entry_type") == "GENESIS"
            else "stage_f_evidence_ledger_entry",
            entry,
        )
        _validate_science_counters_recursively(entry, f"Stage F {phase} ledger entry")
        if entry.get("append_ticket") != ticket:
            _refuse(f"Stage F {phase} top-level and embedded append tickets differ")
        parent_sha = _sha256(
            append_material["parent_watch_range_sha256"],
            f"Stage F {phase} parent-watch range SHA-256",
        )
        usn_sha = _sha256(
            append_material["usn_range_sha256"],
            f"Stage F {phase} USN range SHA-256",
        )
        if entry.get("usn_range_sha256") != usn_sha:
            _refuse(f"Stage F {phase} ledger entry USN range differs")
        definition = (
            "stage_f_evidence_ledger_genesis"
            if entry.get("entry_type") == "GENESIS"
            else "stage_f_evidence_ledger_entry"
        )
        rows.append({"definition": "stage_f_ledger_append_ticket", "record": dict(ticket)})
        rows.append({"definition": definition, "record": dict(entry)})
        append_observation = state.ledger_backend.append_entry(
            entry,
            parent_watch_range_sha256=parent_sha,
            usn_range_sha256=usn_sha,
        )
        state.validate_definition(
            "stage_f_evidence_ledger_append_observation", append_observation
        )
        rows.append(
            {
                "definition": "stage_f_evidence_ledger_append_observation",
                "record": append_observation,
            }
        )
    rows.extend(after)
    observation = _mapping(material["observation"], f"Stage F {phase} observation")
    _validate_science_counters_recursively(observation, f"Stage F {phase} observation")
    state.control_records.extend(rows)
    state.completed_live_phases.append(phase)
    return rows, dict(observation)


def _windows_stage_f_create_held_ledger(
    *,
    controller_input: Mapping[str, Any],
    state_token: Any,
    control_records: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    state = _stage_f_require_live_state(
        state_token, control_records, preceding_phase="read_locked_authority_materials"
    )
    if state.ledger_backend is not None:
        _refuse("Stage F held ledger would be created more than once")
    ledger_path = controller_input.get("ledger_path")
    if not _stage_f_ledger_path_is_closed(ledger_path):
        _refuse("Stage F held-ledger path is absent or not closed")
    if "create_held_ledger" not in state.phase_materials:
        _refuse("Stage F held-ledger exact entry material is absent")
    backend_factory = controller_input.get("_stage_f_ledger_backend_factory")
    ledger_apis = controller_input.get("_stage_f_ledger_apis")
    if backend_factory is None:
        state.ledger_backend = StageFEvidenceLedgerBackend(
            str(ledger_path),
            state.validate_definition,
            apis=ledger_apis,
        )
    else:
        if not callable(backend_factory):
            _refuse("Stage F ledger backend factory is not callable")
        state.ledger_backend = backend_factory(
            str(ledger_path), state.validate_definition
        )
        if not callable(getattr(state.ledger_backend, "append_entry", None)):
            _refuse("Stage F injected ledger backend lacks append_entry")
    material = _stage_f_phase_material(
        state,
        "create_held_ledger",
        context={"ledger_create_observation": state.ledger_backend.create_observation},
    )
    rows, observation = _stage_f_apply_exact_material(
        state, "create_held_ledger", material, require_ledger_appends=True
    )
    if (
        sum(row["definition"] == "stage_f_evidence_ledger_genesis" for row in rows)
        != 1
        or observation.get(
            "ledger_create_new_handle_retained_and_genesis_appended"
        )
        is not True
    ):
        _refuse("Stage F held-ledger genesis material differs")
    return _stage_f_live_phase_result(state, rows, observation)


def _windows_stage_f_material_phase(
    phase: str,
    preceding_phase: str,
    *,
    controller_input: Mapping[str, Any],
    state_token: Any,
    control_records: Sequence[Mapping[str, Any]],
    required_definition: str | None,
    require_ledger_appends: bool,
) -> tuple[_WindowsStageFControllerState, list[dict[str, Any]], dict[str, Any]]:
    del controller_input
    state = _stage_f_require_live_state(
        state_token, control_records, preceding_phase=preceding_phase
    )
    material = _stage_f_phase_material(state, phase)
    rows, observation = _stage_f_apply_exact_material(
        state, phase, material, require_ledger_appends=require_ledger_appends
    )
    if required_definition is not None and sum(
        row["definition"] == required_definition for row in rows
    ) != 1:
        _refuse(f"Stage F {phase} lacks one exact {required_definition}")
    return state, rows, observation


def _windows_stage_f_publish_capacity_snapshot(**kwargs: Any) -> dict[str, Any]:
    state, rows, observation = _windows_stage_f_material_phase(
        "publish_capacity_snapshot",
        "create_held_ledger",
        required_definition="stage_f_capacity_publication_observation",
        require_ledger_appends=True,
        **kwargs,
    )
    publication = next(
        row["record"]
        for row in rows
        if row["definition"] == "stage_f_capacity_publication_observation"
    )
    _validate_capacity_control_record(
        publication,
        "stage_f_capacity_publication_observation",
        "Stage F live capacity publication",
    )
    state.capacity_publication = publication
    return _stage_f_live_phase_result(state, rows, observation)


def _windows_stage_f_close_capacity_consumption(**kwargs: Any) -> dict[str, Any]:
    state, rows, observation = _windows_stage_f_material_phase(
        "close_capacity_consumption",
        "publish_capacity_snapshot",
        required_definition="stage_f_capacity_consumption_closure",
        require_ledger_appends=True,
        **kwargs,
    )
    closure = next(
        row["record"]
        for row in rows
        if row["definition"] == "stage_f_capacity_consumption_closure"
    )
    _validate_capacity_control_record(
        closure,
        "stage_f_capacity_consumption_closure",
        "Stage F live capacity closure",
    )
    state.capacity_closure = closure
    return _stage_f_live_phase_result(state, rows, observation)


def _windows_stage_f_launch_suspended_validator(**kwargs: Any) -> dict[str, Any]:
    state, rows, observation = _windows_stage_f_material_phase(
        "launch_suspended_validator",
        "close_capacity_consumption",
        required_definition=None,
        require_ledger_appends=False,
        **kwargs,
    )
    if rows:
        _refuse("Stage F suspended-validator evidence is nested and may not publish rows")
    _validate_suspended_validator_material(state, observation)
    state.validator_observation = observation
    return _stage_f_live_phase_result(state, [], observation)


def _windows_stage_f_complete_outcome_blind_authorization_chain(
    **kwargs: Any,
) -> dict[str, Any]:
    state, rows, observation = _windows_stage_f_material_phase(
        "complete_outcome_blind_authorization_chain",
        "launch_suspended_validator",
        required_definition=None,
        require_ledger_appends=True,
        **kwargs,
    )
    wanted = (
        "binding_validation_receipt",
        "binding_readiness_record",
        "independent_binding_audit_receipt",
        "sealed_campaign_packet_manifest",
        "post_packet_user_authorization_receipt",
        "campaign_authorization",
    )
    published = [row for row in rows if row["definition"] in wanted]
    if tuple(row["definition"] for row in published) != wanted:
        _refuse("Stage F outcome-blind authorization records differ or are reordered")
    if observation.get("ordered_authorization_records") != published:
        _refuse("Stage F authorization observation does not embed the exact records")
    state.authorization_records = published
    return _stage_f_live_phase_result(state, rows, observation)


def _windows_stage_f_attest_host_docker_and_create_inert_container(
    **kwargs: Any,
) -> dict[str, Any]:
    state, rows, observation = _windows_stage_f_material_phase(
        "attest_host_docker_and_create_inert_container",
        "complete_outcome_blind_authorization_chain",
        required_definition="stage_f_scientific_launch_gate",
        require_ledger_appends=True,
        **kwargs,
    )
    gate = next(
        row["record"]
        for row in rows
        if row["definition"] == "stage_f_scientific_launch_gate"
    )
    _validate_launch_gate_container_links(gate, state.root_epoch)
    state.launch_gate = gate
    return _stage_f_live_phase_result(state, rows, observation)


def _windows_stage_f_publish_durable_start_intent(**kwargs: Any) -> dict[str, Any]:
    state, rows, observation = _windows_stage_f_material_phase(
        "publish_durable_start_intent",
        "attest_host_docker_and_create_inert_container",
        required_definition="stage_f_container_start_intent",
        require_ledger_appends=True,
        **kwargs,
    )
    intent = next(
        row["record"]
        for row in rows
        if row["definition"] == "stage_f_container_start_intent"
    )
    _validate_start_intent_container_links(intent, state.launch_gate)
    state.start_intent = intent
    return _stage_f_live_phase_result(state, rows, observation)


def _windows_stage_f_freeze_uninvoked_handoff(
    *,
    controller_input: Mapping[str, Any],
    state_token: Any,
    control_records: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    del controller_input
    state = _stage_f_require_live_state(
        state_token, control_records, preceding_phase="publish_durable_start_intent"
    )
    material = _stage_f_phase_material(state, "freeze_uninvoked_handoff")
    _exact_fields(
        material,
        frozenset(("handoff", "observation")),
        "Stage F freeze handoff material",
    )
    handoff = _mapping(material["handoff"], "Stage F frozen handoff")
    assert state.validate_definition is not None
    state.validate_definition("stage_f_scientific_launch_handoff", handoff)
    _validate_handoff_container_links(handoff, state.start_intent, state.launch_gate)
    observation = _mapping(material["observation"], "Stage F frozen handoff observation")
    _validate_science_counters_recursively(handoff, "Stage F frozen handoff")
    state.frozen_handoff = dict(handoff)
    state.completed_live_phases.append("freeze_uninvoked_handoff")
    return {
        "state_token": state,
        "handoff": dict(handoff),
        "observation": dict(observation),
        "scientific_counters": dict(ZERO_SCIENCE_COUNTERS),
    }


def _windows_stage_f_abort_without_start(
    *,
    state_token: Any,
    control_records: Sequence[Mapping[str, Any]],
    reason: str,
) -> dict[str, Any]:
    if not isinstance(state_token, _WindowsStageFControllerState):
        _refuse("Stage F abort lacks its retained Win32 state")
    state = state_token
    if (
        state.invalidated
        or state.released
        or [dict(row) for row in control_records] != state.control_records
        or reason not in (
            "PRESTART_HANDOFF_ABANDONED_WITHOUT_START",
            "PRESTART_CONTROLLER_FAILURE",
        )
    ):
        _refuse("Stage F abort state, control rows, or reason differs")
    material = _stage_f_phase_material(state, "abort_without_start")
    rows, observation = _stage_f_apply_exact_material(
        state, "abort_without_start", material, require_ledger_appends=state.start_intent is not None
    )
    definitions = [row["definition"] for row in rows]
    if definitions.count("stage_f_root_protection_release") != 1:
        _refuse("Stage F abort material lacks one root-protection release")
    if definitions[-1] != "stage_f_root_protection_release":
        _refuse("Stage F root-protection release is not the final abort record")
    if state.start_intent is not None and definitions.count(
        "stage_f_container_start_receipt"
    ) != 1:
        _refuse("Stage F post-intent abort lacks one typed no-start receipt")
    state.abort()
    return {
        "state_token": state,
        "control_records": rows,
        "observation": dict(observation),
        "scientific_counters": dict(ZERO_SCIENCE_COUNTERS),
    }


_WINDOWS_STAGE_F_PHASE_HELPERS.update(
    {
        "incept_fresh_attempt_root": _windows_stage_f_incept_fresh_attempt_root,
        "acquire_root_and_volume_epoch": _windows_stage_f_acquire_root_and_volume_epoch,
        "read_locked_authority_materials": _windows_stage_f_read_locked_authority_materials,
        "create_held_ledger": _windows_stage_f_create_held_ledger,
        "publish_capacity_snapshot": _windows_stage_f_publish_capacity_snapshot,
        "close_capacity_consumption": _windows_stage_f_close_capacity_consumption,
        "launch_suspended_validator": _windows_stage_f_launch_suspended_validator,
        "complete_outcome_blind_authorization_chain": _windows_stage_f_complete_outcome_blind_authorization_chain,
        "attest_host_docker_and_create_inert_container": _windows_stage_f_attest_host_docker_and_create_inert_container,
        "publish_durable_start_intent": _windows_stage_f_publish_durable_start_intent,
        "freeze_uninvoked_handoff": _windows_stage_f_freeze_uninvoked_handoff,
        "abort_without_start": _windows_stage_f_abort_without_start,
    }
)


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
    executable: str,
    vector: Sequence[str],
    *,
    attestation_context: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if sys.platform != "win32" or ctypes.sizeof(ctypes.c_void_p) != 8:
        _refuse("host-runtime controller launch requires 64-bit Win32")
    _refuse(
        "rejected v1 host-runtime ORCHESTRATOR launch is disabled; corrected "
        "root-protected suspended image attestation must use the control-state route"
    )
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
    _refuse(
        "rejected v1 host-runtime controller lacks fresh Stage-F root/ledger/USN epoch; "
        "use the corrected control-state route"
    )
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
