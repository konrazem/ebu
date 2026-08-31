"""Fail-closed, outcome-blind Stage F local-binding validation.

The functions in this module validate retained records supplied by the caller.
They never manufacture missing scientific identities or an execution
authorization, and they never import a project runner.
"""

from __future__ import annotations

import base64
import hashlib
import re
import os
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

from .canonical import (
    BindingRefusal,
    assert_zero_science_counters,
    canonical_bytes,
    sha256_hex,
    sha256_identity,
    strict_loads,
    verify_embedded_digest,
    verify_identity,
)


ACCEPTED_BASE = {
    "commit": "c43ead831c3e4021405985134ed564b761bb1aed",
    "tree": "212777d569af527ce9532ea6c836ff2225465d87",
}
ORIGINAL_AUTHORITY_CANDIDATE_COMMIT = "c683040869ecbbe439835a8fabd0a6c3d7ea0e3d"
ORIGINAL_AUTHORITY_CANDIDATE_TREE = "46ce30f0c3675836b449bc2fb00ae22a688ca287"
ORIGINAL_AUTHORITY_INTEGRATION_COMMIT = "4ab6a8a8b158e6ff32d06e67d29a3d974a6326be"
ORIGINAL_AUTHORITY_INTEGRATION_TREE = "46ce30f0c3675836b449bc2fb00ae22a688ca287"
CORRECTION_REQUIRED_TARGET_COMMIT = "1033501b77f7f55ed9aacd9a71cef95f81966e4a"
CORRECTION_REQUIRED_TARGET_TREE = "d8ffbd105eb76cfbb72472772e07f18a11112db3"
CORRECTION_AUTHORITY_CANDIDATE_COMMIT = "dd1a38aee4a6c1048122cb2b5a4e7cf542c5e101"
CORRECTION_AUTHORITY_CANDIDATE_TREE = "c5d6e6c53528ae64a90151d286feb2cc62be47be"
CORRECTION_AUTHORITY_INTEGRATION_COMMIT = "db9d305be120e69d00be14f0d07e06999ca77999"
CORRECTION_AUTHORITY_INTEGRATION_TREE = "c5d6e6c53528ae64a90151d286feb2cc62be47be"
REACHABILITY_CANDIDATE_COMMIT = "0b618dafd1cbc795d9b05038a0d298552b5eb372"
REACHABILITY_CANDIDATE_TREE = "382472276e7fbb7b483cc120467f23f83bc25ca3"
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
DESCENDANT_PATH_BASE_COMMIT = "b7ebe8615d54ae5e23645734b1a6c7667ce28bce"
DESCENDANT_PATH_BASE_TREE = "24f2693b6d26d42bf9e360b295e3209a16417f74"
BINDING_FOUNDATION_BASE_COMMIT = FINAL_REACHABILITY_INTEGRATION_COMMIT
BINDING_FOUNDATION_BASE_TREE = FINAL_REACHABILITY_INTEGRATION_TREE
REJECTED_IMPLEMENTATION_COMMIT = "c6e659305713ba462dbadc54d37d704e2e4de168"
REJECTED_IMPLEMENTATION_TREE = "52a4039eccca8f860cad3156e44abfd21add37a3"
REJECTED_FOUNDATION_COMMITS = (
    "0748e88d76ba8c2d86c41f4d7b8d632960041a1c",
    REJECTED_IMPLEMENTATION_COMMIT,
)
EFFECTIVE_SCHEMA_PATH = (
    "stage_f_local_execution_binding_final_evidence_closure_correction_schema.json"
)
EFFECTIVE_SCHEMA_GIT_OBJECT = "db8268a009ed4a20e056f62f236c12d1b0f7c131"
EFFECTIVE_SCHEMA_BYTE_COUNT = 833194
EFFECTIVE_SCHEMA_SHA256 = "b3bc610e1e6ded0e75de13ac30c36dafd72d3432fd9517cb80815ecb07396b67"
EFFECTIVE_SCHEMA_DEFINITION_COUNT = 228
EFFECTIVE_SCHEMA_ADDED_DEFINITION_COUNT = 85
EFFECTIVE_SCHEMA_CHANGED_DEFINITION_COUNT = 28
EFFECTIVE_SCHEMA_REMOVED_DEFINITION_COUNT = 0
EFFECTIVE_SCHEMA_LOCAL_REFERENCE_COUNT = 2431
EFFECTIVE_SCHEMA_ROOT_VARIANT_COUNT = 46
STAGE_E_CI_RUN_ID = 33231168021
STAGE_E_ARTIFACT_ID = 9708926559
STAGE_E_ARTIFACT_SHA256 = "2b2b5cc213082392bda715e82b9a23f670b7628b92848ace9455724f903bc345"
PUBLIC_HOST_ALIAS = "EXECUTION-HOST-01"
MAXIMUM_SNAPSHOT_AGE_SECONDS = 300

CAMPAIGN_ORDER = (
    "SD-01",
    "SD-01-GROWTH-v1",
    "SD-02",
    "SD-03",
    "SD-04",
    "SD-05",
    "SD-06",
    "SD-07",
    "SD-08",
    "SD-09",
    "SD-10",
    "SD-11",
    "SD-12",
    "SD-13",
    "SD-14",
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
IMPLEMENTATION_PATHS = (
    ".github/workflows/tests.yml",
    "scripts/validate_stage_e_harness.py",
    "scripts/build_stage_f_local_binding.py",
    "scripts/validate_stage_f_local_binding.py",
    "stage_f_binding/__init__.py",
    "stage_f_binding/canonical.py",
    "stage_f_binding/binding.py",
    "stage_f_binding/durability.py",
    "stage_f_binding/locked_zipapp_bootstrap.py",
    "tests/stage_f_binding/__init__.py",
    "tests/stage_f_binding/fixtures/negative_cases.json",
    "tests/stage_f_binding/fixtures/synthetic_private_host_manifest.json",
    "tests/stage_f_binding/test_binding_privacy_and_authorization.py",
    "tests/stage_f_binding/test_durability_and_no_science.py",
)
VALIDATOR_SOURCE_PATHS = (
    "scripts/build_stage_f_local_binding.py",
    "scripts/validate_stage_f_local_binding.py",
    "stage_f_binding/__init__.py",
    "stage_f_binding/canonical.py",
    "stage_f_binding/binding.py",
    "stage_f_binding/durability.py",
    "stage_f_binding/locked_zipapp_bootstrap.py",
)
VALIDATOR_ZIPAPP_PATHS = (
    ("__main__.py", "scripts/validate_stage_f_local_binding.py"),
    ("stage_f_binding/__init__.py", "stage_f_binding/__init__.py"),
    ("stage_f_binding/canonical.py", "stage_f_binding/canonical.py"),
    ("stage_f_binding/binding.py", "stage_f_binding/binding.py"),
    ("stage_f_binding/durability.py", "stage_f_binding/durability.py"),
)

CAMPAIGN_BINDING_FIELDS = frozenset(
    {
        "schema", "campaign_id", "study_id", "ordered_scientific_run_identities",
        "authority_identity", "continuation_authority_identity", "code_identity",
        "installed_artifact_identity", "environment_identity", "configuration_set_identity",
        "algorithm_set_identity", "oracle_set_identity", "numerical_policy_identity",
        "stochastic_rule_identity", "uncertainty_policy_identity", "seed_set_identity",
        "permitted_stream_set_identity", "dependency_topology_identity",
        "cache_key_schema_identity", "invalidation_policy_identity", "exact_or_approximate_label",
        "horizon_identity", "control_set_identity", "falsifier_set_identity",
        "checkpoint_policy_identity", "parallelization_boundary_identity",
        "worker_allocation_policy_identity", "storage_location_identity",
        "durability_policy_identity", "restart_policy_identity", "continuation_mode",
        "attempt_watchdogs", "campaign_budget", "atomic_case_identity_rule",
        "silent_approximation_permitted", "arbitrary_n_completion_claim", "sealed_before_stage_f",
        "outcome_inspected_before_seal", "binding_sha256",
    }
)

ACCEPTED_GAPS = {
    "SD-01": ("STAGE_F_SD01_ADAPTER_AND_RUN_ID_CLOSURE",),
    "SD-01-GROWTH-v1": ("STAGE_F_DYNAMIC_GROWTH_RUNNER_AND_DURABLE_RECORD_CLOSURE",),
    "SD-02": ("GATE_1D_C_LOCAL_HOST_REBINDING_AND_RECORD_TRANSLATION",),
    "SD-03": ("ATOMIC_GENERATOR_EXECUTABLE_CHAIN_AND_EXACT_ORACLE",),
    "SD-04": ("TAYLOR_COEFFICIENT_REMAINDER_AND_COMMUTATOR_ORACLE",),
    "SD-05": ("PARALLEL_AND_SUBSET_VALUE_SEMANTICS",),
    "SD-06": ("FINITE_POSET_INPUT_VALUE_TABLES",),
    "SD-07": ("CONCRETE_REUSE_QUERY_AND_BOUNDARY_CERTIFICATES",),
    "SD-08": ("PART_VII_ROUTE_QUEUE_AND_TIE_BREAKING_SEMANTICS",),
    "SD-09": ("FAIRNESS_METRIC_AUTHORITY", "SD_08_AUDITED_RESULT_BASIS"),
    "SD-10": ("CORRECTION_COST_RECEIPT_AND_PROPAGATION_MODEL",),
    "SD-11": ("EVENT_FIXTURE_AND_INDEPENDENT_LEDGER_ORACLE_CLOSURE",),
    "SD-12": ("COOPERATION_DISCLOSURE_AND_GOVERNANCE_MODEL_AUTHORITY",),
    "SD-13": ("SETTLEMENT_RESERVE_APPEAL_FRAUD_AND_GOVERNANCE_AUTHORITY",),
    "SD-14": (
        "COMPLETE_ECONOMY_MODEL_AND_EXCHANGE_AUTHORITY",
        "SD_01_THROUGH_SD_13_ACCEPTED_DISPOSITIONS",
    ),
}

IDENTITY_KINDS = {
    "binding_authority_set": "stage_f_binding_authority_set/v3",
    "binding_implementation": "stage_f_binding_implementation/v3",
    "binding_readiness": "stage_f_local_binding_readiness/v2",
    "binding_validation_receipt": "stage_f_binding_validation_receipt/v2",
    "binding_validator": "stage_f_binding_validator/v3",
    "campaign_authorization": "stage_f_campaign_authorization/v2",
    "campaign_binding": "campaign_execution_binding/v2",
    "campaign_binding_file": "campaign_execution_binding_file/v2",
    "durability_policy": "stage_f_durability_policy/v1",
    "durability_probe_receipt": "stage_f_durability_probe_receipt/v1",
    "environment_policy": "stage_f_execution_environment_policy/v1",
    "filesystem_binding": "stage_f_filesystem_binding/v1",
    "host_validation_runtime": "stage_f_host_validation_runtime/v1",
    "independent_binding_audit": "stage_f_independent_binding_audit/v2",
    "installed_python_distribution": "stage_f_installed_python_distribution/v1",
    "installed_scientific_artifact": "stage_f_installed_scientific_artifact/v1",
    "local_binding_bundle": "stage_f_local_binding_bundle/v2",
    "parallelization_boundary_policy": "stage_f_parallelization_boundary_policy/v1",
    "post_packet_user_authorization_receipt": "stage_f_post_packet_user_authorization_receipt/v2",
    "power_snapshot": "stage_f_power_snapshot/v1",
    "private_durability_bundle": "stage_f_private_durability_bundle/v1",
    "private_host_manifest": "stage_f_private_execution_host_manifest/v1",
    "private_path": "stage_f_private_path/v1",
    "public_host_binding": "stage_f_public_execution_host_binding/v1",
    "restart_policy": "stage_f_restart_policy/v1",
    "scientific_code": "stage_f_scientific_code/v1",
    "scientific_implementation": "stage_f_scientific_implementation/v1",
    "sealed_campaign_packet": "stage_f_sealed_campaign_packet/v2",
    "stage_e_exact_target_evidence_artifact": "stage_e_exact_target_evidence_artifact/v1",
    "stage_e_exact_target_integration": "stage_e_exact_target_integration/v1",
    "storage_capacity_snapshot": "stage_f_storage_capacity_snapshot/v1",
    "storage_inventory_policy": "stage_f_storage_inventory_policy/v1",
    "storage_location_policy": "stage_f_storage_location_policy/v1",
    "synthetic_durability_payload": "stage_f_synthetic_durability_payload/v1",
    "verifier_implementation": "stage_f_verifier_implementation/v1",
    "worker_allocation_policy": "stage_f_worker_allocation_policy/v1",
    "authorized_mutation_ticket": "stage_f_authorized_mutation_ticket/v1",
    "capacity_consumption_closure": "stage_f_capacity_consumption_closure/v1",
    "capacity_live_gate": "stage_f_capacity_live_gate/v1",
    "capacity_publication": "stage_f_capacity_publication_observation/v1",
    "container_start_capability": "stage_f_container_start_capability/v1",
    "container_start_intent": "stage_f_container_start_intent/v1",
    "container_start_receipt": "stage_f_container_start_receipt/v1",
    "evidence_ledger": "stage_f_evidence_ledger/v1",
    "execution_attempt_genesis": "stage_f_execution_attempt_genesis/v1",
    "host_prerequisite_snapshot": "stage_f_host_prerequisite_snapshot/v1",
    "inert_container": "stage_f_inert_container/v1",
    "launch_handoff": "stage_f_scientific_launch_handoff/v1",
    "lid_open_statement": "stage_f_lid_open_statement_receipt/v1",
    "root_protection_epoch": "stage_f_root_protection_epoch/v1",
    "root_protection_release": "stage_f_root_protection_release/v1",
    "root_watch_live_state": "stage_f_root_watch_live_state/v1",
    "scientific_launch_gate": "stage_f_scientific_launch_gate/v1",
    "host_validation_process_resume_capability": "stage_f_host_validation_process_resume_capability/v1",
    "continuation_segment_start_capability": "stage_f_continuation_segment_start_capability/v1",
    "capacity_usage_projection": "stage_f_capacity_usage_projection/v1",
}

EMBEDDED_DIGEST_FIELDS = {
    "stage_f_binding_validation_receipt/v2": "receipt_sha256",
    "stage_f_campaign_authorization/v2": "authorization_sha256",
    "stage_f_durability_probe_receipt/v1": "receipt_sha256",
    "stage_f_independent_binding_audit/v2": "audit_sha256",
    "stage_f_local_binding_bundle/v2": "bundle_sha256",
    "stage_f_local_binding_readiness/v2": "readiness_sha256",
    "stage_f_post_packet_user_authorization_receipt/v2": "receipt_sha256",
    "stage_f_power_snapshot/v1": "snapshot_sha256",
    "stage_f_private_durability_bundle/v1": "bundle_sha256",
    "stage_f_public_execution_host_binding/v1": "public_binding_sha256",
    "stage_f_storage_capacity_snapshot/v1": "snapshot_sha256",
    "stage_f_validator_artifact_lock_observation/v1": "lock_sha256",
    "stage_f_execution_attempt_genesis/v1": "genesis_sha256",
    "stage_f_authorized_mutation_ticket/v1": "ticket_sha256",
    "stage_f_ledger_append_ticket/v1": "ticket_sha256",
    "stage_f_evidence_ledger/v1": "ledger_sha256",
    "stage_f_root_protection_epoch/v1": "epoch_sha256",
    "stage_f_root_protection_release/v1": "release_sha256",
    "stage_f_capacity_publication_observation/v1": "publication_sha256",
    "stage_f_capacity_consumption_closure/v1": "closure_sha256",
    "stage_f_capacity_live_gate/v1": "gate_sha256",
    "stage_f_lid_open_statement_receipt/v1": "receipt_sha256",
    "stage_f_host_prerequisite_snapshot/v1": "snapshot_sha256",
    "stage_f_inert_container_observation/v1": "container_observation_sha256",
    "stage_f_container_start_capability/v1": "capability_sha256",
    "stage_f_container_start_intent/v1": "intent_sha256",
    "stage_f_container_start_receipt/v1": "receipt_sha256",
    "stage_f_root_watch_live_state/v1": "live_state_sha256",
    "stage_f_scientific_launch_gate/v1": "gate_sha256",
    "stage_f_scientific_launch_handoff/v1": "handoff_sha256",
    "stage_f_capacity_usage_projection/v1": "projection_sha256",
    "stage_f_durability_suspended_process_launch_attestation/v1": "attestation_sha256",
    "stage_f_host_validation_process_resume_capability/v1": "capability_sha256",
    "stage_f_continuation_segment_start_capability/v1": "capability_sha256",
}

NESTED_ONLY_DEFINITIONS = frozenset(
    {
        "stage_f_capacity_live_gate",
        "stage_f_continuation_segment_start_capability",
        "stage_f_host_validation_process_resume_capability",
        "stage_f_host_prerequisite_snapshot",
        "stage_f_scientific_launch_handoff",
    }
)

EFFECTIVE_SCHEMA_ADDED_DEFINITIONS = (
    "attested_process_image_observation",
    "capacity_causal_file_row",
    "capacity_directory_remeasurement",
    "controller_session_observation",
    "directory_watch_acquisition_observation",
    "docker_engine_observation",
    "docker_engine_request_observation",
    "docker_named_pipe_bounded_response_window_observation",
    "docker_named_pipe_connection_observation",
    "docker_named_pipe_connection_release_observation",
    "docker_named_pipe_http_exchange_observation",
    "docker_named_pipe_http_start_attempt_observation",
    "docker_named_pipe_no_further_read_cut_observation",
    "docker_named_pipe_read_attempt_observation",
    "docker_runtime_identity_observation",
    "durability_suspended_process_launch_attestation",
    "file_object_measurement",
    "ntfs_directory_allocation_observation",
    "ntfs_directory_stream_allocation_observation",
    "ntfs_file_record_call_observation",
    "ntfs_retrieval_pointers_call_observation",
    "publication_parent_watch_observation",
    "registry_probe_row",
    "stage_f_active_power_scheme_observation",
    "stage_f_authorized_mutation_ticket",
    "stage_f_capacity_consumption_closure",
    "stage_f_capacity_consumption_closure_identity",
    "stage_f_capacity_live_gate",
    "stage_f_capacity_live_gate_identity",
    "stage_f_capacity_publication_identity",
    "stage_f_capacity_publication_observation",
    "stage_f_capacity_usage_projection",
    "stage_f_capacity_usage_projection_identity",
    "stage_f_container_mount_observation",
    "stage_f_container_start_capability",
    "stage_f_container_start_capability_identity",
    "stage_f_container_start_intent",
    "stage_f_container_start_intent_identity",
    "stage_f_container_start_receipt",
    "stage_f_container_start_receipt_identity",
    "stage_f_continuation_segment_start_capability",
    "stage_f_continuation_segment_start_capability_identity",
    "stage_f_evidence_ledger_append_observation",
    "stage_f_evidence_ledger_entry",
    "stage_f_evidence_ledger_genesis",
    "stage_f_evidence_ledger_identity",
    "stage_f_execution_attempt_genesis",
    "stage_f_file_notify_record",
    "stage_f_host_prerequisite_snapshot",
    "stage_f_host_prerequisite_snapshot_identity",
    "stage_f_host_validation_process_resume_capability",
    "stage_f_host_validation_process_resume_capability_identity",
    "stage_f_immutable_file_lock",
    "stage_f_inert_container_identity",
    "stage_f_inert_container_observation",
    "stage_f_ledger_append_ticket",
    "stage_f_ledger_create_observation",
    "stage_f_lid_open_statement_identity",
    "stage_f_lid_open_statement_receipt",
    "stage_f_power_setting_query_observation",
    "stage_f_raw_volume_capacity_observation",
    "stage_f_readonly_recovery_file_observation",
    "stage_f_recovery_file_read_call_observation",
    "stage_f_recovery_held_file_release_observation",
    "stage_f_recovery_original_intent_binding_observation",
    "stage_f_retained_subtree_allocation_observation",
    "stage_f_root_path_anchor",
    "stage_f_root_protection_epoch",
    "stage_f_root_protection_epoch_identity",
    "stage_f_root_protection_release",
    "stage_f_root_watch",
    "stage_f_root_watch_completion_observation",
    "stage_f_root_watch_live_state",
    "stage_f_root_watch_live_state_identity",
    "stage_f_root_watch_pending_resource_projection",
    "stage_f_root_watch_release_observation",
    "stage_f_scientific_launch_gate",
    "stage_f_scientific_launch_gate_identity",
    "stage_f_scientific_launch_handoff",
    "stage_f_scientific_launch_handoff_identity",
    "stage_f_usn_journal_range",
    "stage_f_usn_query_call_observation",
    "stage_f_usn_read_call_observation",
    "stage_f_usn_record",
    "stage_f_usn_volume_handle_observation",
)

EFFECTIVE_SCHEMA_CHANGED_DEFINITIONS = (
    "atomic_publication_observation",
    "binding_authority_set_identity",
    "binding_authority_set_preimage",
    "binding_implementation_identity",
    "binding_implementation_preimage",
    "binding_readiness_identity",
    "binding_readiness_record",
    "binding_validation_receipt",
    "binding_validation_receipt_identity",
    "binding_validator_identity",
    "binding_validator_preimage",
    "campaign_authorization",
    "campaign_authorization_identity",
    "durability_control_file_write_observation",
    "durability_probe_receipt",
    "durability_process_launch_observation",
    "durability_restart_observation",
    "independent_binding_audit_identity",
    "independent_binding_audit_receipt",
    "local_binding_bundle",
    "local_binding_bundle_identity",
    "post_packet_authorization_receipt_identity",
    "post_packet_user_authorization_receipt",
    "power_facts",
    "power_snapshot",
    "sealed_campaign_packet_identity",
    "sealed_campaign_packet_manifest",
    "storage_capacity_snapshot",
)

IMMEDIATE_SCHEMA_ADDED_DEFINITIONS = (
    "durability_suspended_process_launch_attestation",
    "stage_f_capacity_usage_projection",
    "stage_f_capacity_usage_projection_identity",
    "stage_f_continuation_segment_start_capability",
    "stage_f_continuation_segment_start_capability_identity",
    "stage_f_host_validation_process_resume_capability",
    "stage_f_host_validation_process_resume_capability_identity",
    "stage_f_root_watch_pending_resource_projection",
)

IMMEDIATE_SCHEMA_CHANGED_DEFINITIONS = (
    "binding_authority_set_identity",
    "binding_authority_set_preimage",
    "binding_implementation_identity",
    "binding_implementation_preimage",
    "binding_readiness_identity",
    "binding_readiness_record",
    "binding_validation_receipt",
    "binding_validation_receipt_identity",
    "binding_validator_identity",
    "binding_validator_preimage",
    "campaign_authorization",
    "campaign_authorization_identity",
    "directory_watch_acquisition_observation",
    "docker_engine_observation",
    "docker_named_pipe_bounded_response_window_observation",
    "docker_named_pipe_http_exchange_observation",
    "docker_named_pipe_http_start_attempt_observation",
    "durability_process_launch_observation",
    "durability_restart_observation",
    "independent_binding_audit_identity",
    "independent_binding_audit_receipt",
    "local_binding_bundle",
    "local_binding_bundle_identity",
    "post_packet_authorization_receipt_identity",
    "post_packet_user_authorization_receipt",
    "power_facts",
    "registry_probe_row",
    "sealed_campaign_packet_identity",
    "sealed_campaign_packet_manifest",
    "stage_f_authorized_mutation_ticket",
    "stage_f_capacity_consumption_closure",
    "stage_f_capacity_live_gate",
    "stage_f_container_start_receipt",
    "stage_f_evidence_ledger_entry",
    "stage_f_file_notify_record",
    "stage_f_recovery_original_intent_binding_observation",
    "stage_f_root_watch",
    "stage_f_root_watch_completion_observation",
    "stage_f_root_watch_live_state",
    "stage_f_root_watch_release_observation",
    "stage_f_usn_journal_range",
    "stage_f_usn_query_call_observation",
    "stage_f_usn_read_call_observation",
    "stage_f_usn_record",
)

POLICY_DEFINITIONS = {
    "environment": ("execution_environment_policy_preimage", IDENTITY_KINDS["environment_policy"]),
    "parallelization_boundary": (
        "parallelization_boundary_policy_preimage",
        IDENTITY_KINDS["parallelization_boundary_policy"],
    ),
    "worker_allocation": ("worker_allocation_policy_preimage", IDENTITY_KINDS["worker_allocation_policy"]),
    "storage_location": ("storage_location_policy_preimage", IDENTITY_KINDS["storage_location_policy"]),
    "durability": ("durability_policy_preimage", IDENTITY_KINDS["durability_policy"]),
    "restart": ("restart_policy_preimage", IDENTITY_KINDS["restart_policy"]),
    "storage_inventory": ("storage_inventory_policy_preimage", IDENTITY_KINDS["storage_inventory_policy"]),
}

PUBLIC_POLICY_IDENTITY_FIELDS = {
    "environment": "environment_identity",
    "parallelization_boundary": "parallelization_boundary_identity",
    "worker_allocation": "worker_allocation_policy_identity",
    "storage_location": "storage_location_identity",
    "durability": "durability_policy_identity",
    "restart": "restart_policy_identity",
    "storage_inventory": "storage_inventory_policy_identity",
}

SUPPORTED_SCHEMA_KEYWORDS = frozenset(
    {
        "$comment", "$defs", "$id", "$ref", "$schema", "additionalProperties",
        "allOf", "anyOf", "const", "contains", "description", "else", "enum", "format", "if", "items",
        "maxContains", "maxItems", "maxLength", "maximum", "minContains", "minItems", "minLength", "minProperties", "minimum",
        "not", "oneOf", "pattern", "prefixItems", "properties", "required", "then", "title",
        "type", "uniqueItems",
    }
)
SCHEMA_METADATA_KEYS = frozenset(
    {"completion_marker", "schema_version", "scientific_execution_count"}
)


def _same(left: Any, right: Any) -> bool:
    if type(left) is not type(right):
        return False
    if isinstance(left, list):
        return len(left) == len(right) and all(_same(a, b) for a, b in zip(left, right))
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(_same(left[key], right[key]) for key in left)
    return bool(left == right)


def _is_integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _matches_type(value: Any, type_name: str) -> bool:
    return {
        "null": value is None,
        "boolean": isinstance(value, bool),
        "integer": _is_integer(value),
        "number": _is_integer(value) or isinstance(value, float) and not isinstance(value, bool),
        "string": isinstance(value, str),
        "array": isinstance(value, list),
        "object": isinstance(value, dict),
    }.get(type_name, False)


def _resolve_pointer(root: Any, reference: str) -> Any:
    if not isinstance(reference, str) or not reference.startswith("#/"):
        raise BindingRefusal(f"only local schema references are permitted: {reference!r}")
    value = root
    for raw in reference[2:].split("/"):
        token = raw.replace("~1", "/").replace("~0", "~")
        if isinstance(value, list):
            if not token.isdecimal() or int(token) >= len(value):
                raise BindingRefusal(f"unresolved local schema reference: {reference}")
            value = value[int(token)]
        elif isinstance(value, dict) and token in value:
            value = value[token]
        else:
            raise BindingRefusal(f"unresolved local schema reference: {reference}")
    return value


def _schema_children(key: str, value: Any) -> Iterable[Any]:
    if key in {"$defs", "properties"}:
        if not isinstance(value, dict):
            raise BindingRefusal(f"{key} must be an object")
        return value.values()
    if key in {"allOf", "anyOf", "oneOf", "prefixItems"}:
        if not isinstance(value, list):
            raise BindingRefusal(f"{key} must be an array")
        return value
    if key in {"additionalProperties", "contains", "items", "if", "then", "else", "not"}:
        if not isinstance(value, (dict, bool)):
            raise BindingRefusal(f"{key} must be a schema object or boolean")
        return (value,)
    return ()


def audit_schema(schema: Mapping[str, Any]) -> tuple[int, int]:
    """Refuse unsupported vocabulary or unresolved/non-local references."""

    if not isinstance(schema, Mapping):
        raise BindingRefusal("schema root must be an object")
    references: list[str] = []

    def visit(node: Any, *, root: bool = False) -> None:
        if isinstance(node, bool):
            return
        if not isinstance(node, dict):
            raise BindingRefusal("schema node must be an object or boolean")
        for key, value in node.items():
            if key == "$ref":
                if not isinstance(value, str) or not value.startswith("#/$defs/"):
                    raise BindingRefusal(
                        f"only closed local $defs references are permitted: {value!r}"
                    )
                references.append(value)
            if key in SUPPORTED_SCHEMA_KEYWORDS:
                for child in _schema_children(key, value):
                    visit(child)
            elif not (root and key in SCHEMA_METADATA_KEYS):
                raise BindingRefusal(f"unsupported schema keyword or metadata key: {key}")
        if "enum" in node:
            enum = node["enum"]
            if not isinstance(enum, list) or not enum:
                raise BindingRefusal("schema enum must be a nonempty array")
            encoded = [canonical_bytes(item) for item in enum]
            if len(encoded) != len(set(encoded)):
                raise BindingRefusal("schema enum values are not unique")
        if "required" in node:
            required = node["required"]
            if (
                not isinstance(required, list)
                or not all(isinstance(item, str) for item in required)
                or len(required) != len(set(required))
            ):
                raise BindingRefusal("schema required list is malformed or duplicated")
        if node.get("additionalProperties") is False and "properties" in node:
            properties = node["properties"]
            required = node.get("required")
            if not isinstance(properties, dict) or not isinstance(required, list):
                raise BindingRefusal("closed schema object lacks properties/required closure")
            if set(properties) != set(required):
                raise BindingRefusal("closed schema object has an optional or unknown property")
        if "pattern" in node:
            try:
                re.compile(node["pattern"])
            except (re.error, TypeError) as exc:
                raise BindingRefusal("schema contains an invalid pattern") from exc
        if "contains" in node:
            minimum = node.get("minContains", 1)
            maximum = node.get("maxContains")
            if (
                not _is_integer(minimum)
                or minimum < 0
                or maximum is not None
                and (not _is_integer(maximum) or maximum < minimum)
            ):
                raise BindingRefusal("schema contains bounds are malformed")
        elif "minContains" in node or "maxContains" in node:
            raise BindingRefusal("schema contains bounds exist without contains")

    visit(dict(schema), root=True)
    for reference in references:
        _resolve_pointer(schema, reference)
    return len(references), len(set(references))


def audit_effective_schema(
    schema: Mapping[str, Any],
    *,
    historical_schema: Mapping[str, Any] | None = None,
    immediate_predecessor_schema: Mapping[str, Any] | None = None,
) -> tuple[int, int]:
    """Verify the frozen v3 final-closure schema and optional v1-to-v3 delta."""

    references, unique_references = audit_schema(schema)
    definitions = schema.get("$defs")
    roots = schema.get("oneOf")
    if (
        not isinstance(definitions, dict)
        or len(definitions) != EFFECTIVE_SCHEMA_DEFINITION_COUNT
        or references != EFFECTIVE_SCHEMA_LOCAL_REFERENCE_COUNT
        or not isinstance(roots, list)
        or len(roots) != EFFECTIVE_SCHEMA_ROOT_VARIANT_COUNT
        or schema.get("$id")
        != "https://ebu.example/schema/stage-f-local-execution-binding-final-evidence-closure-correction-v3.json"
        or schema.get("schema_version") != "3.0.0-candidate"
        or schema.get("scientific_execution_count") != 0
    ):
        raise BindingRefusal("effective correction-schema coordinate or structural count differs")
    names = tuple(sorted(definitions, key=lambda value: value.encode("utf-8")))
    if any(name != unicodedata.normalize("NFC", name) for name in names):
        raise BindingRefusal("effective schema definition name is not NFC")
    expected_added = tuple(EFFECTIVE_SCHEMA_ADDED_DEFINITIONS)
    if (
        len(expected_added) != EFFECTIVE_SCHEMA_ADDED_DEFINITION_COUNT
        or tuple(sorted(expected_added, key=lambda value: value.encode("utf-8")))
        != expected_added
        or not set(expected_added).issubset(definitions)
    ):
        raise BindingRefusal("effective schema added-definition lock differs")
    root_references = tuple(
        branch.get("$ref") for branch in roots if isinstance(branch, Mapping)
    )
    if len(root_references) != len(roots) or len(set(root_references)) != len(roots):
        raise BindingRefusal("effective schema root variants are malformed or duplicated")
    forbidden_roots = {f"#/$defs/{name}" for name in NESTED_ONLY_DEFINITIONS}
    if forbidden_roots.intersection(root_references):
        raise BindingRefusal("nested-only correction evidence is exposed as a root variant")
    create = definitions.get("stage_f_ledger_create_observation")
    append = definitions.get("stage_f_evidence_ledger_append_observation")
    for definition, count, label in (
        (create, 76, "ledger create"),
        (append, 123, "ledger append"),
    ):
        if (
            not isinstance(definition, Mapping)
            or not isinstance(definition.get("properties"), Mapping)
            or not isinstance(definition.get("required"), list)
            or len(definition["properties"]) != count
            or len(definition["required"]) != count
            or set(definition["properties"]) != set(definition["required"])
        ):
            raise BindingRefusal(f"effective schema {label} required/property closure differs")
    if historical_schema is not None:
        audit_schema(historical_schema)
        historical_definitions = historical_schema.get("$defs")
        if not isinstance(historical_definitions, dict) or len(historical_definitions) != 143:
            raise BindingRefusal("historical schema definition count differs")
        added = tuple(
            sorted(set(definitions) - set(historical_definitions), key=lambda value: value.encode("utf-8"))
        )
        removed = tuple(
            sorted(set(historical_definitions) - set(definitions), key=lambda value: value.encode("utf-8"))
        )
        changed = tuple(
            sorted(
                (
                    name
                    for name in set(definitions).intersection(historical_definitions)
                    if not _same(definitions[name], historical_definitions[name])
                ),
                key=lambda value: value.encode("utf-8"),
            )
        )
        if (
            added != EFFECTIVE_SCHEMA_ADDED_DEFINITIONS
            or changed != EFFECTIVE_SCHEMA_CHANGED_DEFINITIONS
            or removed
            or len(added) != EFFECTIVE_SCHEMA_ADDED_DEFINITION_COUNT
            or len(changed) != EFFECTIVE_SCHEMA_CHANGED_DEFINITION_COUNT
        ):
            raise BindingRefusal("effective schema 143-to-228 definition delta differs")
    if immediate_predecessor_schema is not None:
        audit_schema(immediate_predecessor_schema)
        predecessor_definitions = immediate_predecessor_schema.get("$defs")
        if (
            not isinstance(predecessor_definitions, dict)
            or len(predecessor_definitions) != 220
        ):
            raise BindingRefusal("immediate predecessor schema definition count differs")
        added = tuple(
            sorted(
                set(definitions) - set(predecessor_definitions),
                key=lambda value: value.encode("utf-8"),
            )
        )
        removed = tuple(
            sorted(
                set(predecessor_definitions) - set(definitions),
                key=lambda value: value.encode("utf-8"),
            )
        )
        changed = tuple(
            sorted(
                (
                    name
                    for name in set(definitions).intersection(predecessor_definitions)
                    if not _same(definitions[name], predecessor_definitions[name])
                ),
                key=lambda value: value.encode("utf-8"),
            )
        )
        if (
            added != IMMEDIATE_SCHEMA_ADDED_DEFINITIONS
            or changed != IMMEDIATE_SCHEMA_CHANGED_DEFINITIONS
            or removed
        ):
            raise BindingRefusal("effective schema 220-to-228 definition delta differs")
    return references, unique_references


def verify_effective_schema_blob(
    raw: bytes,
    *,
    historical_schema: Mapping[str, Any] | None = None,
    immediate_predecessor_schema: Mapping[str, Any] | None = None,
) -> Mapping[str, Any]:
    """Verify the exact committed LF Git blob and its frozen schema structure."""

    if not isinstance(raw, bytes):
        raise BindingRefusal("effective correction schema material is not bytes")
    framed = b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw
    if (
        len(raw) != EFFECTIVE_SCHEMA_BYTE_COUNT
        or sha256_hex(raw) != EFFECTIVE_SCHEMA_SHA256
        or hashlib.sha1(framed, usedforsecurity=False).hexdigest()
        != EFFECTIVE_SCHEMA_GIT_OBJECT
    ):
        raise BindingRefusal("effective correction schema Git blob identity differs")
    value = strict_loads(raw)
    if not isinstance(value, Mapping):
        raise BindingRefusal("effective correction schema is not a JSON object")
    audit_effective_schema(
        value,
        historical_schema=historical_schema,
        immediate_predecessor_schema=immediate_predecessor_schema,
    )
    return value


class ClosedSchemaValidator:
    """Validator for the exact Draft 2020-12 subset used by Stage F authority."""

    def __init__(self, schema: Mapping[str, Any], *, allowed_metadata: Iterable[str] = ()) -> None:
        self.schema = dict(schema)
        global SCHEMA_METADATA_KEYS
        unexpected = set(allowed_metadata) - SCHEMA_METADATA_KEYS
        if unexpected:
            raise BindingRefusal(f"unsupported root metadata allowance: {sorted(unexpected)}")
        if self.schema.get("schema_version") == "3.0.0-candidate":
            audit_effective_schema(self.schema)
        else:
            audit_schema(self.schema)

    def definition(self, name: str) -> Any:
        definitions = self.schema.get("$defs")
        if not isinstance(definitions, dict) or name not in definitions:
            raise BindingRefusal(f"unknown schema definition: {name}")
        return definitions[name]

    def validate_definition(self, name: str, instance: Any) -> None:
        self.validate(instance, self.definition(name), path=f"$defs.{name}")

    def validate(self, instance: Any, schema: Any | None = None, *, path: str = "$") -> None:
        self._validate(instance, self.schema if schema is None else schema, path)

    def is_valid(self, instance: Any, schema: Any | None = None) -> bool:
        try:
            self.validate(instance, schema)
        except BindingRefusal:
            return False
        return True

    def _validate(self, instance: Any, schema: Any, path: str) -> None:
        if schema is True:
            return
        if schema is False:
            raise BindingRefusal(f"{path}: false schema")
        if not isinstance(schema, dict):
            raise BindingRefusal(f"{path}: malformed schema node")
        if "$ref" in schema:
            self._validate(instance, _resolve_pointer(self.schema, schema["$ref"]), path)
        if "type" in schema:
            required_types = schema["type"]
            if isinstance(required_types, str):
                required_types = [required_types]
            if not isinstance(required_types, list) or not required_types or not all(
                isinstance(item, str) for item in required_types
            ):
                raise BindingRefusal(f"{path}: malformed type")
            if not any(_matches_type(instance, item) for item in required_types):
                raise BindingRefusal(f"{path}: type mismatch")
        if "const" in schema and not _same(instance, schema["const"]):
            raise BindingRefusal(f"{path}: const mismatch")
        if "enum" in schema:
            enum = schema["enum"]
            if not isinstance(enum, list) or not any(_same(instance, item) for item in enum):
                raise BindingRefusal(f"{path}: enum mismatch")
        if isinstance(instance, str):
            if "minLength" in schema and len(instance) < schema["minLength"]:
                raise BindingRefusal(f"{path}: minLength")
            if "maxLength" in schema and len(instance) > schema["maxLength"]:
                raise BindingRefusal(f"{path}: maxLength")
            if "pattern" in schema:
                try:
                    matches = re.search(schema["pattern"], instance) is not None
                except (re.error, TypeError) as exc:
                    raise BindingRefusal(f"{path}: invalid schema pattern") from exc
                if not matches:
                    raise BindingRefusal(f"{path}: pattern")
        if _is_integer(instance) or isinstance(instance, float) and not isinstance(instance, bool):
            if "minimum" in schema and instance < schema["minimum"]:
                raise BindingRefusal(f"{path}: minimum")
            if "maximum" in schema and instance > schema["maximum"]:
                raise BindingRefusal(f"{path}: maximum")
        if isinstance(instance, list):
            if "minItems" in schema and len(instance) < schema["minItems"]:
                raise BindingRefusal(f"{path}: minItems")
            if "maxItems" in schema and len(instance) > schema["maxItems"]:
                raise BindingRefusal(f"{path}: maxItems")
            if schema.get("uniqueItems"):
                serialized = [canonical_bytes(item) for item in instance]
                if len(serialized) != len(set(serialized)):
                    raise BindingRefusal(f"{path}: uniqueItems")
            prefix = schema.get("prefixItems", [])
            for index, subschema in enumerate(prefix[: len(instance)]):
                self._validate(instance[index], subschema, f"{path}[{index}]")
            if "items" in schema:
                for index in range(len(prefix), len(instance)):
                    self._validate(instance[index], schema["items"], f"{path}[{index}]")
            if "contains" in schema:
                matches = sum(
                    self.is_valid(item, schema["contains"]) for item in instance
                )
                minimum = schema.get("minContains", 1)
                maximum = schema.get("maxContains")
                if matches < minimum or maximum is not None and matches > maximum:
                    raise BindingRefusal(f"{path}: contains matched {matches} items")
        if isinstance(instance, dict):
            if "minProperties" in schema and len(instance) < schema["minProperties"]:
                raise BindingRefusal(f"{path}: minProperties")
            required = schema.get("required", [])
            if not isinstance(required, list) or not all(isinstance(item, str) for item in required):
                raise BindingRefusal(f"{path}: malformed required")
            missing = [item for item in required if item not in instance]
            if missing:
                raise BindingRefusal(f"{path}: missing required {missing}")
            properties = schema.get("properties", {})
            if not isinstance(properties, dict):
                raise BindingRefusal(f"{path}: malformed properties")
            for key, subschema in properties.items():
                if key in instance:
                    self._validate(instance[key], subschema, f"{path}.{key}")
            extras = [key for key in instance if key not in properties]
            additional = schema.get("additionalProperties", True)
            if additional is False and extras:
                raise BindingRefusal(f"{path}: additional properties {extras}")
            if isinstance(additional, dict):
                for key in extras:
                    self._validate(instance[key], additional, f"{path}.{key}")
        for index, subschema in enumerate(schema.get("allOf", [])):
            self._validate(instance, subschema, f"{path}.allOf[{index}]")
        if "anyOf" in schema and not any(
            self.is_valid(instance, subschema) for subschema in schema["anyOf"]
        ):
            raise BindingRefusal(f"{path}: anyOf matched no branches")
        if "oneOf" in schema:
            matches = sum(self.is_valid(instance, subschema) for subschema in schema["oneOf"])
            if matches != 1:
                raise BindingRefusal(f"{path}: oneOf matched {matches} branches")
        if "not" in schema and self.is_valid(instance, schema["not"]):
            raise BindingRefusal(f"{path}: not matched forbidden schema")
        if "if" in schema:
            branch = "then" if self.is_valid(instance, schema["if"]) else "else"
            if branch in schema:
                self._validate(instance, schema[branch], f"{path}.{branch}")


def validate_identity_preimage(
    identity: Mapping[str, Any], preimage: Any, *, expected_kind: str
) -> None:
    if expected_kind not in IDENTITY_KINDS.values():
        raise BindingRefusal(f"identity kind is outside the frozen Stage F registry: {expected_kind}")
    verify_identity(identity, preimage, kind=expected_kind)


def _resolve_preimage(
    identity_preimages: Mapping[Any, Any], identity: Mapping[str, Any]
) -> Any:
    keys = (
        (identity.get("kind"), identity.get("value")),
        f"{identity.get('kind')}:{identity.get('value')}",
        identity.get("value"),
    )
    matches = [identity_preimages[key] for key in keys if key in identity_preimages]
    if len(matches) != 1:
        raise BindingRefusal(
            f"identity preimage must resolve exactly once: {identity.get('kind')}:{identity.get('value')}"
        )
    return matches[0]


_VOLUME_GUID_PATH_RE = re.compile(
    r"^\\\\\?\\Volume\{[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}\}\\"
)


def _private_path_value(
    identity: Mapping[str, Any],
    identity_preimages: Mapping[Any, Any],
    label: str,
) -> str:
    if identity.get("kind") != IDENTITY_KINDS["private_path"]:
        raise BindingRefusal(f"{label} is not a private-path identity")
    raw = _resolve_preimage(identity_preimages, identity)
    if not isinstance(raw, bytes) or not raw:
        raise BindingRefusal(f"{label} private-path preimage is not raw UTF-8 bytes")
    verify_identity(identity, raw, kind=IDENTITY_KINDS["private_path"])
    try:
        path = raw.decode("utf-8", "strict")
    except UnicodeDecodeError as exc:
        raise BindingRefusal(f"{label} private path is not UTF-8") from exc
    return _private_absolute_path(path, label)


def _private_absolute_path(path: Any, label: str) -> str:
    if (
        not isinstance(path, str)
        or path != unicodedata.normalize("NFC", path)
        or "/" in path
        or "\x00" in path
        or _VOLUME_GUID_PATH_RE.match(path) is None
    ):
        raise BindingRefusal(f"{label} is not a normalized volume-GUID path")
    prefix = _VOLUME_GUID_PATH_RE.match(path).group(0)
    remainder = path[len(prefix) :]
    components = remainder.rstrip("\\").split("\\") if remainder else []
    if any(
        not component
        or component in {".", ".."}
        or ":" in component
        or component.endswith((".", " "))
        for component in components
    ):
        raise BindingRefusal(f"{label} has a forbidden private-path component")
    if remainder.endswith("\\") and remainder.rstrip("\\"):
        raise BindingRefusal(f"{label} has a non-root trailing separator")
    return path


def _validate_private_directory_layout(filesystem: Mapping[str, Any]) -> None:
    selected_volume = _private_absolute_path(
        filesystem["selected_volume_guid_path"], "selected volume"
    )
    if _VOLUME_GUID_PATH_RE.fullmatch(selected_volume) is None:
        raise BindingRefusal("selected volume is not an exact volume-GUID root")
    private = {
        name: _private_absolute_path(value, f"private directory {name}")
        for name, value in filesystem["private_directories"].items()
    }
    root = private["stage_f_root"]
    expected_private = {
        "stage_f_root": root,
        "immutable_results": _join_private(root, "immutable-results"),
        "continuation_checkpoints": _join_private(root, "continuation-checkpoints"),
        "independent_audit": _join_private(root, "independent-audit"),
        "temporary": _join_private(root, "temporary"),
    }
    if private != expected_private or not _path_under(root, selected_volume):
        raise BindingRefusal("private logical-directory hierarchy differs")
    roles = [private[name] for name in (
        "immutable_results",
        "continuation_checkpoints",
        "independent_audit",
        "temporary",
    )]
    if any(
        left == right or _path_under(left, right) or _path_under(right, left)
        for index, left in enumerate(roles)
        for right in roles[index + 1 :]
    ):
        raise BindingRefusal("private logical-directory roles alias or overlap")
    categories = {
        name: _private_absolute_path(value, f"storage category {name}")
        for name, value in filesystem["storage_category_directories"].items()
    }
    expected_categories = {
        "primary_logical_output": _join_private(
            private["immutable_results"], "primary-logical-output"
        ),
        "independent_audit_copy": _join_private(
            private["independent_audit"], "complete-copy"
        ),
        "dynamic_growth_physical_writes": _join_private(
            private["immutable_results"], "dynamic-growth-physical-writes"
        ),
        "checkpoint_and_write_overhead": private["continuation_checkpoints"],
        "temporary_archives": private["temporary"],
        "retained_evidence": _join_private(
            private["independent_audit"], "retained-evidence"
        ),
    }
    if categories != expected_categories:
        raise BindingRefusal("storage category-directory hierarchy differs")
    if len(set((root, *roles, *categories.values()))) != 9:
        raise BindingRefusal("private root/role/category path projection is not nine unique paths")
    volume_projection = filesystem["resolved_private_path_volume_guids"]
    if any(value != selected_volume for value in volume_projection.values()):
        raise BindingRefusal("private root/role/category path resolves to another volume")


def _path_under(path: str, root: str) -> bool:
    normalized_root = root.rstrip("\\")
    return path == normalized_root or path.startswith(normalized_root + "\\")


def _join_private(root: str, relative: str) -> str:
    if relative == ".":
        return root.rstrip("\\")
    normalized = unicodedata.normalize("NFC", relative).replace("/", "\\")
    components = normalized.split("\\")
    if (
        relative != normalized
        or any(
            not component
            or component in {".", ".."}
            or ":" in component
            or component.endswith((".", " "))
            for component in components
        )
        or re.match(r"^[A-Za-z]:", normalized)
    ):
        raise BindingRefusal(f"runtime-relative path is not closed: {relative!r}")
    return root.rstrip("\\") + "\\" + "\\".join(components)


def validate_durability_private_paths(
    receipt: Mapping[str, Any],
    *,
    private_manifest: Mapping[str, Any],
    identity_preimages: Mapping[Any, Any],
) -> None:
    filesystem = private_manifest["filesystem"]
    selected_volume = filesystem["selected_volume_guid_path"]
    if (
        not isinstance(selected_volume, str)
        or _VOLUME_GUID_PATH_RE.fullmatch(selected_volume) is None
    ):
        raise BindingRefusal("private manifest selected volume is not a canonical GUID root")
    private_directories = filesystem["private_directories"]
    storage_directories = filesystem["storage_category_directories"]
    temporary_root = private_directories["temporary"]
    retained_root = storage_directories["retained_evidence"]
    for label, value in (
        ("private temporary root", temporary_root),
        ("private retained-evidence root", retained_root),
    ):
        if not isinstance(value, str) or not _path_under(value, selected_volume):
            raise BindingRefusal(f"{label} is outside the selected volume")
        # The actual binding uses normalized volume-GUID paths, not DOS aliases.
        if _VOLUME_GUID_PATH_RE.match(value) is None:
            raise BindingRefusal(f"{label} is not a normalized volume-GUID path")

    resolved: dict[tuple[Any, Any], str] = {}

    def visit(value: Any, label: str) -> None:
        if isinstance(value, Mapping):
            if value.get("kind") == IDENTITY_KINDS["private_path"]:
                key = (value.get("kind"), value.get("value"))
                path = _private_path_value(value, identity_preimages, label)
                if not _path_under(path, selected_volume):
                    raise BindingRefusal(f"{label} is outside the selected volume")
                prior = resolved.setdefault(key, path)
                if prior != path:
                    raise BindingRefusal(f"{label} private-path identity is rebound")
            else:
                for key, child in value.items():
                    visit(child, f"{label}.{key}")
        elif isinstance(value, list):
            for index, child in enumerate(value):
                visit(child, f"{label}[{index}]")

    visit(receipt, "durability receipt")

    def path_of(identity: Mapping[str, Any], label: str) -> str:
        key = (identity.get("kind"), identity.get("value"))
        if key not in resolved:
            raise BindingRefusal(f"{label} private-path material was not resolved")
        return resolved[key]

    def require_under(
        identity: Mapping[str, Any],
        root: str,
        label: str,
        *,
        allow_root: bool = False,
    ) -> str:
        path = path_of(identity, label)
        if not _path_under(path, root) or (
            not allow_root and path.rstrip("\\") == root.rstrip("\\")
        ):
            raise BindingRefusal(f"{label} is outside its exact private role")
        return path

    acquisition = receipt["host_runtime_lock_acquisition_preimage"]
    runtime = private_manifest["host_validation_runtime_preimage"]
    runtime_root = path_of(runtime["runtime_root_path_identity"], "host runtime root")
    if path_of(
        acquisition["selected_volume_root_path_identity"],
        "runtime acquisition selected volume",
    ) != selected_volume:
        raise BindingRefusal("runtime acquisition selected-volume path differs")
    if path_of(
        acquisition["runtime_root_path_identity"], "runtime acquisition root"
    ) != runtime_root:
        raise BindingRefusal("runtime acquisition root path differs from retained runtime")
    runtime_parent = runtime_root.rsplit("\\", 1)[0]
    if runtime_parent == selected_volume.rstrip("\\"):
        runtime_parent = selected_volume
    if path_of(
        acquisition["runtime_parent_path_identity"], "runtime acquisition parent"
    ) != runtime_parent:
        raise BindingRefusal("runtime acquisition parent path differs")
    volume_prefix = _VOLUME_GUID_PATH_RE.match(runtime_root).group(0)
    suffix = runtime_root[len(volume_prefix) :]
    components = suffix.split("\\") if suffix else []
    expected_anchors = [volume_prefix]
    current = volume_prefix.rstrip("\\")
    for component in components:
        current += "\\" + component
        expected_anchors.append(current)
    observed_anchors = [
        path_of(row["anchor_path_identity"], "runtime anchor path")
        for row in acquisition["ordered_runtime_path_anchor_lock_rows"]
    ]
    if observed_anchors != expected_anchors:
        raise BindingRefusal("runtime acquisition anchor path chain differs")
    for row in acquisition["ordered_runtime_file_lock_rows"]:
        actual = path_of(row["runtime_path_identity"], "runtime file path")
        expected = _join_private(runtime_root, row["runtime_relative_path"])
        if actual != expected:
            raise BindingRefusal("runtime file identity differs from relative path")
    for row in acquisition["ordered_runtime_directory_rows"]:
        actual = path_of(row["runtime_path_identity"], "runtime directory path")
        expected = _join_private(runtime_root, row["manifest_row"]["relative_path"])
        if actual != expected:
            raise BindingRefusal("runtime directory identity differs from manifest path")

    restart = receipt["restart_observation"]
    temporary_identities = [
        receipt["temporary_path_identity"],
        receipt["final_path_identity"],
        receipt["directory_target_identity"],
        restart["challenge_path_identity"],
        restart["acknowledgement_path_identity"],
        restart["challenge_publication_observation"]["temporary_write_observation"][
            "target_path_identity"
        ],
        restart["acknowledgement_write_observation"]["target_path_identity"],
    ]
    for invocation_field in (
        "orchestrator_probe_invocation_preimage",
        "terminated_probe_invocation_preimage",
        "resumed_probe_invocation_preimage",
    ):
        invocation = receipt[invocation_field]
        temporary_identities.append(invocation["invocation_preimage_path_identity"])
        if invocation["restart_challenge_path_identity"] is not None:
            temporary_identities.extend(
                (
                    invocation["restart_challenge_path_identity"],
                    invocation["acknowledgement_path_identity"],
                )
            )
    for index, identity in enumerate(temporary_identities):
        require_under(
            identity,
            temporary_root,
            f"temporary-role path {index}",
            allow_root=index == 2,
        )
    top_final = path_of(receipt["final_path_identity"], "synthetic final path")
    top_parent = path_of(
        receipt["directory_target_identity"], "synthetic final parent path"
    )
    if top_final.rsplit("\\", 1)[0] != top_parent.rstrip("\\"):
        raise BindingRefusal("synthetic final directory-target path differs")
    challenge_final = path_of(
        restart["challenge_path_identity"], "restart challenge final path"
    )
    challenge_parent = path_of(
        restart["challenge_publication_observation"][
            "directory_durability_observation"
        ]["target_parent_path_identity"],
        "restart challenge parent path",
    )
    require_under(
        restart["challenge_publication_observation"][
            "directory_durability_observation"
        ]["target_parent_path_identity"],
        temporary_root,
        "restart challenge parent path",
        allow_root=True,
    )
    if (
        challenge_final.rsplit("\\", 1)[0]
        != challenge_parent.rstrip("\\")
    ):
        raise BindingRefusal("restart challenge directory-target path differs")

    invocations = (
        receipt["orchestrator_probe_invocation_preimage"],
        receipt["terminated_probe_invocation_preimage"],
        receipt["resumed_probe_invocation_preimage"],
    )
    executable_path = _join_private(runtime_root, runtime["executable_relative_path"])
    for phase, invocation in zip(
        ("ORCHESTRATOR", "PRE_RESTART", "POST_RESTART"), invocations, strict=True
    ):
        if path_of(
            invocation["executable_path_identity"], f"{phase} executable"
        ) != executable_path:
            raise BindingRefusal(f"{phase} executable path is outside the retained runtime")
        require_under(
            invocation["validator_zipapp_path_identity"],
            retained_root,
            f"{phase} validator artifact",
        )
    for field in (
        "orchestrator_artifact_lock_observation",
        "terminated_artifact_lock_observation",
        "resumed_artifact_lock_observation",
    ):
        require_under(
            receipt[field]["artifact_path_identity"], retained_root, field
        )
    artifact_locks = (
        receipt["orchestrator_artifact_lock_observation"],
        receipt["terminated_artifact_lock_observation"],
        receipt["resumed_artifact_lock_observation"],
    )
    artifact_metadata_fields = (
        "resolved_path_identity",
        "volume_serial_number",
        "file_id_128",
        "number_of_links",
        "delete_pending",
        "directory",
        "raw_file_attributes",
        "reparse_tag",
        "observed_byte_count",
        "observed_sha256",
    )
    if any(
        any(lock[field] != artifact_locks[0][field] for field in artifact_metadata_fields)
        for lock in artifact_locks[1:]
    ):
        raise BindingRefusal("validator-artifact lock metadata projections differ")
    selected_file_id_volume = filesystem["ntfs_volume_data"]["volume_serial_number"]

    def require_selected_volume(value: Any, label: str) -> None:
        if isinstance(value, Mapping):
            if (
                "volume_serial_number" in value
                and value["volume_serial_number"] != selected_file_id_volume
            ):
                raise BindingRefusal(f"{label} FileIdInfo volume serial differs")
            for key, child in value.items():
                require_selected_volume(child, f"{label}.{key}")
        elif isinstance(value, list):
            for index, child in enumerate(value):
                require_selected_volume(child, f"{label}[{index}]")

    require_selected_volume(receipt, "durability receipt")


def _require_exact_git_rows(
    rows: Any, expected_paths: Sequence[str], label: str
) -> dict[str, Mapping[str, Any]]:
    if not isinstance(rows, list) or len(rows) != len(expected_paths):
        raise BindingRefusal(f"{label} row count differs")
    if tuple(row.get("path") for row in rows if isinstance(row, Mapping)) != tuple(
        expected_paths
    ):
        raise BindingRefusal(f"{label} path order differs")
    result: dict[str, Mapping[str, Any]] = {}
    for path, row in zip(expected_paths, rows, strict=True):
        if (
            not isinstance(row, Mapping)
            or set(row) != {"path", "mode", "git_object", "byte_count", "raw_sha256"}
            or row["path"] != path
            or row["mode"] != "100644"
            or path in result
        ):
            raise BindingRefusal(f"{label} row differs: {path}")
        result[path] = row
    return result


class VerifiedGitRepository:
    """Content-addressed, pure-Python view of retained raw Git objects."""

    _OID = re.compile(r"[0-9a-f]{40}")
    _TYPES = frozenset({"commit", "tree", "blob"})

    def __init__(
        self,
        objects: Mapping[tuple[str, str], bytes | Callable[[], bytes]],
    ) -> None:
        if not isinstance(objects, Mapping) or not objects:
            raise BindingRefusal("verified Git object material is empty")
        self._objects: dict[tuple[str, str], bytes | Callable[[], bytes]] = {}
        self._commits: dict[str, tuple[str, tuple[str, ...]]] = {}
        self._trees: dict[str, tuple[tuple[str, str, str], ...]] = {}
        self._tree_maps: dict[str, dict[str, tuple[str, str, bytes]]] = {}
        for key, raw in objects.items():
            if (
                not isinstance(key, tuple)
                or len(key) != 2
                or key[0] not in self._TYPES
                or not isinstance(key[1], str)
                or self._OID.fullmatch(key[1]) is None
                or (not isinstance(raw, bytes) and not callable(raw))
                or key in self._objects
            ):
                raise BindingRefusal("verified Git object material entry is malformed")
            self._objects[key] = raw
            if isinstance(raw, bytes):
                self._verify_loaded_object(key, raw)

    @staticmethod
    def _verify_loaded_object(key: tuple[str, str], raw: bytes) -> None:
        object_type, object_id = key
        framed = (
            object_type.encode("ascii")
            + b" "
            + str(len(raw)).encode("ascii")
            + b"\0"
            + raw
        )
        if hashlib.sha1(framed, usedforsecurity=False).hexdigest() != object_id:
            raise BindingRefusal(f"Git object content address differs: {object_id}")

    @classmethod
    def _oid(cls, value: Any, label: str) -> str:
        if not isinstance(value, str) or cls._OID.fullmatch(value) is None:
            raise BindingRefusal(f"{label} Git object id is malformed")
        return value

    def object(self, object_type: str, object_id: str) -> bytes:
        self._oid(object_id, object_type)
        key = (object_type, object_id)
        material = self._objects.get(key)
        if material is None:
            raise BindingRefusal(
                f"retained verified Git {object_type} object is absent: {object_id}"
            )
        if callable(material):
            raw = material()
            if not isinstance(raw, bytes):
                raise BindingRefusal(
                    f"verified Git object loader returned non-bytes: {object_id}"
                )
            self._verify_loaded_object(key, raw)
            self._objects[key] = raw
        else:
            raw = material
        return raw

    def has_object(self, object_type: str, object_id: str) -> bool:
        return (object_type, object_id) in self._objects

    def commit(self, object_id: str) -> tuple[str, tuple[str, ...]]:
        object_id = self._oid(object_id, "commit")
        cached = self._commits.get(object_id)
        if cached is not None:
            return cached
        raw = self.object("commit", object_id)
        if b"\0" in raw or b"\n\n" not in raw:
            raise BindingRefusal(f"Git commit object is malformed: {object_id}")
        header_raw = raw.split(b"\n\n", 1)[0]
        if b"\r" in header_raw:
            raise BindingRefusal(f"Git commit headers contain CR: {object_id}")
        headers = header_raw.split(b"\n")
        if not headers or not headers[0].startswith(b"tree "):
            raise BindingRefusal(f"Git commit lacks one initial tree header: {object_id}")
        try:
            tree = headers[0][5:].decode("ascii", "strict")
        except UnicodeDecodeError as exc:
            raise BindingRefusal(f"Git commit header is non-ASCII: {object_id}") from exc
        self._oid(tree, "commit tree")
        index = 1
        parents_list: list[str] = []
        while index < len(headers) and headers[index].startswith(b"parent "):
            try:
                parent = headers[index][7:].decode("ascii", "strict")
            except UnicodeDecodeError as exc:
                raise BindingRefusal(f"Git commit parent is non-ASCII: {object_id}") from exc
            parents_list.append(self._oid(parent, "commit parent"))
            index += 1
        parents = tuple(parents_list)
        for parent in parents:
            self._oid(parent, "commit parent")
        if index >= len(headers) or not headers[index].startswith(b"author "):
            raise BindingRefusal(f"Git commit lacks its ordered author header: {object_id}")
        index += 1
        if index >= len(headers) or not headers[index].startswith(b"committer "):
            raise BindingRefusal(f"Git commit lacks its ordered committer header: {object_id}")
        index += 1
        for header_index, header in enumerate(headers[index:], start=index):
            if header.startswith(b" "):
                if header_index == index:
                    raise BindingRefusal(f"Git commit has orphan continuation: {object_id}")
                continue
            if (
                b" " not in header
                or header.startswith((b"tree ", b"parent ", b"author ", b"committer "))
            ):
                raise BindingRefusal(f"Git commit header is malformed: {object_id}")
        cached = (tree, parents)
        self._commits[object_id] = cached
        return cached

    def tree_id(self, commit: str) -> str:
        return self.commit(commit)[0]

    def is_ancestor(self, ancestor: str, descendant: str) -> bool:
        ancestor = self._oid(ancestor, "ancestor")
        descendant = self._oid(descendant, "descendant")
        self.object("commit", ancestor)
        self.object("commit", descendant)
        pending = [descendant]
        visited: set[str] = set()
        while pending:
            current = pending.pop()
            if current == ancestor:
                return True
            if current in visited:
                continue
            visited.add(current)
            if not self.has_object("commit", current):
                continue
            pending.extend(self.commit(current)[1])
        return False

    def tree(self, object_id: str) -> tuple[tuple[str, str, str], ...]:
        object_id = self._oid(object_id, "tree")
        cached = self._trees.get(object_id)
        if cached is not None:
            return cached
        raw = self.object("tree", object_id)
        entries: list[tuple[str, str, str]] = []
        offset = 0
        while offset < len(raw):
            space = raw.find(b" ", offset)
            nul = raw.find(b"\0", space + 1) if space >= 0 else -1
            if space <= offset or nul <= space + 1 or nul + 21 > len(raw):
                raise BindingRefusal(f"Git tree entry is truncated: {object_id}")
            mode_raw = raw[offset:space]
            name_raw = raw[space + 1 : nul]
            child = raw[nul + 1 : nul + 21].hex()
            offset = nul + 21
            if mode_raw == b"40000":
                mode = "40000"
            elif mode_raw in (b"100644", b"100755"):
                mode = mode_raw.decode("ascii")
            else:
                raise BindingRefusal(f"Git tree has a forbidden mode: {object_id}")
            try:
                name = name_raw.decode("utf-8", "strict")
            except UnicodeDecodeError as exc:
                raise BindingRefusal(f"Git tree name is not UTF-8: {object_id}") from exc
            if (
                not name
                or unicodedata.normalize("NFC", name) != name
                or name in {".", ".."}
                or "/" in name
                or "\0" in name
            ):
                raise BindingRefusal(f"Git tree name is not an exact NFC component: {object_id}")
            entries.append((mode, name, child))
        keys = [
            name.encode("utf-8") + (b"/" if mode == "40000" else b"")
            for mode, name, _child in entries
        ]
        if keys != sorted(keys) or len({name for _mode, name, _child in entries}) != len(entries):
            raise BindingRefusal(f"Git tree order or uniqueness differs: {object_id}")
        cached = tuple(entries)
        self._trees[object_id] = cached
        return cached

    def tree_map(self, commit: str) -> dict[str, tuple[str, str, bytes]]:
        commit = self._oid(commit, "commit")
        cached = self._tree_maps.get(commit)
        if cached is not None:
            return dict(cached)
        result: dict[str, tuple[str, str, bytes]] = {}

        def visit(tree_id: str, prefix: str, stack: frozenset[str]) -> None:
            if tree_id in stack:
                raise BindingRefusal("Git tree graph is cyclic")
            for mode, name, child in self.tree(tree_id):
                path = f"{prefix}/{name}" if prefix else name
                if mode == "40000":
                    visit(child, path, stack | {tree_id})
                else:
                    if path in result:
                        raise BindingRefusal(f"Git recursive tree repeats a path: {path}")
                    result[path] = (mode, child, self.object("blob", child))

        visit(self.tree_id(commit), "", frozenset())
        if not result:
            raise BindingRefusal("Git recursive tree is empty")
        ordered = dict(sorted(result.items(), key=lambda item: item[0].encode("utf-8")))
        self._tree_maps[commit] = ordered
        return dict(ordered)

    def recursive_paths(self, commit: str) -> list[str]:
        return list(self.tree_map(commit))

    def row(
        self, commit: str, relative: str, *, allowed_modes: frozenset[str]
    ) -> dict[str, Any]:
        if not isinstance(relative, str) or unicodedata.normalize("NFC", relative) != relative:
            raise BindingRefusal("Git row path is malformed")
        entry = self.tree_map(commit).get(relative)
        if entry is None or entry[0] not in allowed_modes:
            expected = "/".join(sorted(allowed_modes))
            raise BindingRefusal(f"Git row is not an exact {expected} blob: {relative}")
        mode, object_id, raw = entry
        return {
            "path": relative,
            "mode": mode,
            "git_object": object_id,
            "byte_count": len(raw),
            "raw_sha256": sha256_hex(raw),
        }

    def blob(self, object_id: str) -> bytes:
        return self.object("blob", object_id)

    def diff_status(self, base: str, target: str) -> list[tuple[str, str]]:
        before = self.tree_map(base)
        after = self.tree_map(target)
        deleted = sorted(set(before) - set(after), key=lambda value: value.encode("utf-8"))
        if deleted:
            raise BindingRefusal(f"Git provenance diff deletes a path: {deleted[0]}")
        result: list[tuple[str, str]] = []
        for path in sorted(after, key=lambda value: value.encode("utf-8")):
            if path not in before:
                result.append(("A", path))
            elif after[path][:2] != before[path][:2]:
                result.append(("M", path))
        if any(after[path][0] != "100644" for _status, path in result):
            raise BindingRefusal("Git provenance diff changes a non-100644 target")
        return result

    def assert_material_closure(self, complete_tree_commits: Iterable[str]) -> None:
        roots = tuple(dict.fromkeys(complete_tree_commits))
        if not roots:
            raise BindingRefusal("verified Git material closure has no roots")
        reachable: set[tuple[str, str]] = set()
        commit_pending = list(roots)
        while commit_pending:
            commit_id = commit_pending.pop()
            key = ("commit", self._oid(commit_id, "material closure commit"))
            if key in reachable:
                continue
            if key not in self._objects:
                raise BindingRefusal(f"material closure commit is absent: {commit_id}")
            reachable.add(key)
            _tree, parents = self.commit(commit_id)
            commit_pending.extend(
                parent for parent in parents if self.has_object("commit", parent)
            )

        def visit_tree(tree_id: str) -> None:
            key = ("tree", tree_id)
            if key in reachable:
                return
            if key not in self._objects:
                raise BindingRefusal(f"material closure tree is absent: {tree_id}")
            reachable.add(key)
            for mode, _name, child in self.tree(tree_id):
                if mode == "40000":
                    visit_tree(child)
                else:
                    blob_key = ("blob", child)
                    if blob_key not in self._objects:
                        raise BindingRefusal(f"material closure blob is absent: {child}")
                    reachable.add(blob_key)

        for commit_id in roots:
            visit_tree(self.tree_id(commit_id))
        if set(self._objects) != reachable:
            extras = sorted(set(self._objects) - reachable)
            label = extras[0] if extras else "unreachable material"
            raise BindingRefusal(f"verified Git material has an extra object: {label}")


def _validate_repository_provenance(
    validator: ClosedSchemaValidator,
    *,
    repository: VerifiedGitRepository,
    bundle: Mapping[str, Any],
    resolved: Mapping[str, Any],
    identity_preimages: Mapping[Any, Any],
) -> None:
    implementation = resolved["binding_implementation_identity"]
    authority = resolved["authority_set_identity"]
    implementation_commit = implementation["implementation_commit"]
    if (
        authority["integrated_authority_commit"] != FINAL_AUTHORITY_INTEGRATION_COMMIT
        or authority["integrated_authority_tree"] != FINAL_AUTHORITY_INTEGRATION_TREE
        or implementation["integrated_authority_commit"]
        != FINAL_AUTHORITY_INTEGRATION_COMMIT
        or repository.tree_id(ORIGINAL_AUTHORITY_CANDIDATE_COMMIT)
        != ORIGINAL_AUTHORITY_CANDIDATE_TREE
        or repository.tree_id(ORIGINAL_AUTHORITY_INTEGRATION_COMMIT)
        != ORIGINAL_AUTHORITY_INTEGRATION_TREE
        or repository.tree_id(CORRECTION_REQUIRED_TARGET_COMMIT)
        != CORRECTION_REQUIRED_TARGET_TREE
        or repository.tree_id(CORRECTION_AUTHORITY_CANDIDATE_COMMIT)
        != CORRECTION_AUTHORITY_CANDIDATE_TREE
        or repository.tree_id(CORRECTION_AUTHORITY_INTEGRATION_COMMIT)
        != CORRECTION_AUTHORITY_INTEGRATION_TREE
        or repository.tree_id(REACHABILITY_CANDIDATE_COMMIT)
        != REACHABILITY_CANDIDATE_TREE
        or repository.tree_id(REACHABILITY_INTEGRATION_COMMIT)
        != REACHABILITY_INTEGRATION_TREE
        or repository.tree_id(FINAL_AUTHORITY_CANDIDATE_COMMIT)
        != FINAL_AUTHORITY_CANDIDATE_TREE
        or repository.tree_id(FINAL_AUTHORITY_INTEGRATION_COMMIT)
        != FINAL_AUTHORITY_INTEGRATION_TREE
        or repository.tree_id(FINAL_REACHABILITY_CANDIDATE_COMMIT)
        != FINAL_REACHABILITY_CANDIDATE_TREE
        or repository.tree_id(FINAL_REACHABILITY_INTEGRATION_COMMIT)
        != FINAL_REACHABILITY_INTEGRATION_TREE
        or repository.commit(FINAL_AUTHORITY_CANDIDATE_COMMIT)[1]
        != (FINAL_AUTHORITY_REQUIRED_TARGET_COMMIT,)
        or repository.commit(FINAL_AUTHORITY_INTEGRATION_COMMIT)[1]
        != (
            FINAL_AUTHORITY_REQUIRED_TARGET_COMMIT,
            FINAL_AUTHORITY_CANDIDATE_COMMIT,
        )
        or repository.commit(FINAL_REACHABILITY_CANDIDATE_COMMIT)[1]
        != (FINAL_AUTHORITY_INTEGRATION_COMMIT,)
        or repository.commit(FINAL_REACHABILITY_INTEGRATION_COMMIT)[1]
        != (
            FINAL_AUTHORITY_INTEGRATION_COMMIT,
            FINAL_REACHABILITY_CANDIDATE_COMMIT,
        )
        or repository.tree_id(DESCENDANT_PATH_BASE_COMMIT)
        != DESCENDANT_PATH_BASE_TREE
        or repository.tree_id(BINDING_FOUNDATION_BASE_COMMIT)
        != BINDING_FOUNDATION_BASE_TREE
        or repository.tree_id(implementation_commit) != implementation["implementation_tree"]
        or not repository.is_ancestor(
            ACCEPTED_BASE["commit"], ORIGINAL_AUTHORITY_CANDIDATE_COMMIT
        )
        or not repository.is_ancestor(
            ORIGINAL_AUTHORITY_CANDIDATE_COMMIT,
            ORIGINAL_AUTHORITY_INTEGRATION_COMMIT,
        )
        or not repository.is_ancestor(
            ORIGINAL_AUTHORITY_INTEGRATION_COMMIT,
            CORRECTION_REQUIRED_TARGET_COMMIT,
        )
        or not repository.is_ancestor(
            CORRECTION_REQUIRED_TARGET_COMMIT,
            CORRECTION_AUTHORITY_CANDIDATE_COMMIT,
        )
        or not repository.is_ancestor(
            CORRECTION_AUTHORITY_CANDIDATE_COMMIT,
            CORRECTION_AUTHORITY_INTEGRATION_COMMIT,
        )
        or not repository.is_ancestor(
            CORRECTION_AUTHORITY_INTEGRATION_COMMIT,
            REACHABILITY_CANDIDATE_COMMIT,
        )
        or not repository.is_ancestor(
            REACHABILITY_CANDIDATE_COMMIT,
            REACHABILITY_INTEGRATION_COMMIT,
        )
        or not repository.is_ancestor(
            FINAL_AUTHORITY_REQUIRED_TARGET_COMMIT,
            FINAL_AUTHORITY_CANDIDATE_COMMIT,
        )
        or not repository.is_ancestor(
            FINAL_AUTHORITY_CANDIDATE_COMMIT,
            FINAL_AUTHORITY_INTEGRATION_COMMIT,
        )
        or not repository.is_ancestor(
            FINAL_AUTHORITY_INTEGRATION_COMMIT,
            FINAL_REACHABILITY_CANDIDATE_COMMIT,
        )
        or not repository.is_ancestor(
            FINAL_REACHABILITY_CANDIDATE_COMMIT,
            FINAL_REACHABILITY_INTEGRATION_COMMIT,
        )
        or not repository.is_ancestor(BINDING_FOUNDATION_BASE_COMMIT, implementation_commit)
        or any(
            repository.is_ancestor(rejected, implementation_commit)
            for rejected in REJECTED_FOUNDATION_COMMITS
        )
    ):
        raise BindingRefusal("corrected binding-foundation immutable Git coordinate chain differs")
    binding_diff = repository.diff_status(BINDING_FOUNDATION_BASE_COMMIT, implementation_commit)
    expected_binding_status = {
        **{path: "M" for path in IMPLEMENTATION_PATHS[:2]},
        **{path: "A" for path in IMPLEMENTATION_PATHS[2:]},
    }
    if {path: status for status, path in binding_diff} != expected_binding_status:
        raise BindingRefusal("binding-foundation Git diff is not the exact 2M+12A scope")
    for index, row in enumerate(authority["ordered_local_authority_file_rows"]):
        if row != repository.row(
            FINAL_AUTHORITY_INTEGRATION_COMMIT,
            row["path"],
            allowed_modes=frozenset({"100644"}),
        ):
            raise BindingRefusal(f"authority-set Git row differs: {row['path']}")
        if row != repository.row(
            implementation_commit, row["path"], allowed_modes=frozenset({"100644"})
        ):
            raise BindingRefusal(f"implementation changed authority row: {row['path']}")
        predecessor_commit = (
            ORIGINAL_AUTHORITY_INTEGRATION_COMMIT
            if index < len(ORIGINAL_AUTHORITY_PATHS)
            else CORRECTION_AUTHORITY_CANDIDATE_COMMIT
            if index < len(ORIGINAL_AUTHORITY_PATHS) + len(CORRECTION_AUTHORITY_PATHS)
            else FINAL_AUTHORITY_CANDIDATE_COMMIT
        )
        if row != repository.row(
            predecessor_commit, row["path"], allowed_modes=frozenset({"100644"})
        ):
            raise BindingRefusal(
                f"authority row differs from its accepted candidate tree: {row['path']}"
            )
    for row in implementation["ordered_implementation_file_rows"]:
        if row != repository.row(
            implementation_commit, row["path"], allowed_modes=frozenset({"100644"})
        ):
            raise BindingRefusal(f"binding implementation Git row differs: {row['path']}")
    reachability_path = "tests/framework/test_validation_reachability.py"
    reachability_row = repository.row(
        FINAL_REACHABILITY_CANDIDATE_COMMIT,
        reachability_path,
        allowed_modes=frozenset({"100644"}),
    )
    for commit in (FINAL_REACHABILITY_INTEGRATION_COMMIT, implementation_commit):
        if reachability_row != repository.row(
            commit, reachability_path, allowed_modes=frozenset({"100644"})
        ):
            raise BindingRefusal("accepted correction-reachability byte changed")

    stage_e = resolved["stage_e_integration_identity"]
    if (
        stage_e["integration_commit"] != ACCEPTED_BASE["commit"]
        or stage_e["integration_tree"] != ACCEPTED_BASE["tree"]
        or repository.tree_id(stage_e["integration_commit"]) != stage_e["integration_tree"]
        or stage_e["implementation_path_manifest_path"]
        != "stage_e_dynamic_growth_harness_reconciliation_implementation_path_manifest.json"
    ):
        raise BindingRefusal("Stage E exact integration Git coordinate differs")
    manifest_path = stage_e["implementation_path_manifest_path"]
    manifest_row = repository.row(
        stage_e["integration_commit"], manifest_path, allowed_modes=frozenset({"100644"})
    )
    if stage_e["implementation_path_manifest_git_row"] != manifest_row:
        raise BindingRefusal("Stage E implementation-path manifest Git row differs")
    manifest = strict_loads(repository.blob(manifest_row["git_object"]))
    scope = manifest["prospective_harness_implementation"]
    stage_e_paths = [*scope["modified_paths"], *scope["new_paths"]]
    if (
        scope["modified_path_count"] != 1
        or scope["new_path_count"] != 50
        or scope["total_path_count"] != 51
        or stage_e["implementation_path_count"] != 51
        or [row["path"] for row in stage_e["ordered_implementation_file_rows"]]
        != stage_e_paths
    ):
        raise BindingRefusal("Stage E exact 51-path projection differs")
    for row in stage_e["ordered_implementation_file_rows"]:
        if row != repository.row(
            stage_e["integration_commit"], row["path"], allowed_modes=frozenset({"100644"})
        ):
            raise BindingRefusal(f"Stage E implementation Git row differs: {row['path']}")
    reachability_path = "tests/framework/test_validation_reachability.py"
    expected_descendant_paths = frozenset(
        (
            *stage_e_paths,
            *AUTHORITY_PATHS,
            reachability_path,
            *IMPLEMENTATION_PATHS[2:],
        )
    )
    descendant_diff = repository.diff_status(
        DESCENDANT_PATH_BASE_COMMIT, implementation_commit
    )
    if (
        len(expected_descendant_paths) != 82
        or frozenset(path for _status, path in descendant_diff)
        != expected_descendant_paths
        or any(status not in {"A", "M"} for status, _path in descendant_diff)
    ):
        raise BindingRefusal("final corrected descendant path closure is not exactly 82")

    code = resolved["scientific_code_identity"]
    science_commit = code["implementation_commit"]
    if repository.tree_id(science_commit) != code["implementation_tree"]:
        raise BindingRefusal("scientific-code Git tree differs")
    complete_paths = repository.recursive_paths(science_commit)
    complete_rows = code["ordered_complete_tree_file_rows"]
    if (
        code["complete_tree_file_count"] != len(complete_rows)
        or [row["path"] for row in complete_rows] != complete_paths
    ):
        raise BindingRefusal("scientific-code complete recursive tree projection differs")
    for row in complete_rows:
        if row != repository.row(
            science_commit, row["path"], allowed_modes=frozenset({"100644", "100755"})
        ):
            raise BindingRefusal(f"scientific-code Git row differs: {row['path']}")

    scientific = resolved.get("scientific_implementation_identity")
    verifier_preimage = resolved.get("verifier_identity")
    material_roots = (
        ACCEPTED_BASE["commit"],
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
        DESCENDANT_PATH_BASE_COMMIT,
        *REJECTED_FOUNDATION_COMMITS,
        BINDING_FOUNDATION_BASE_COMMIT,
        implementation_commit,
        science_commit,
    )
    if scientific is None:
        if verifier_preimage is not None:
            raise BindingRefusal("verifier exists without a scientific implementation")
        repository.assert_material_closure(material_roots)
        return
    if (
        scientific["foundation_commit"] != implementation_commit
        or scientific["foundation_tree"] != implementation["implementation_tree"]
        or scientific["implementation_commit"] != science_commit
        or scientific["implementation_tree"] != code["implementation_tree"]
        or not repository.is_ancestor(implementation_commit, science_commit)
    ):
        raise BindingRefusal("scientific implementation foundation/Git coordinates differ")
    science_diff = repository.diff_status(implementation_commit, science_commit)
    science_rows = scientific["ordered_implementation_file_rows"]
    if (
        scientific["implementation_file_count"] != len(science_rows)
        or [row["path"] for row in science_rows]
        != [path for _status, path in science_diff]
    ):
        raise BindingRefusal("scientific implementation diff closure differs")
    status_names = {"A": "ADDED", "M": "MODIFIED"}
    for (status, path), row in zip(science_diff, science_rows, strict=True):
        expected_row = {
            "status": status_names[status],
            **repository.row(
                science_commit, path, allowed_modes=frozenset({"100644"})
            ),
        }
        if row != expected_row:
            raise BindingRefusal(f"scientific implementation Git row differs: {row['path']}")
    predecessor_path = "stage_f_local_execution_binding_predecessor_manifest.json"
    predecessor_row = repository.row(
        ORIGINAL_AUTHORITY_INTEGRATION_COMMIT,
        predecessor_path,
        allowed_modes=frozenset({"100644"}),
    )
    predecessor_manifest = strict_loads(repository.blob(predecessor_row["git_object"]))
    source_rows = predecessor_manifest["source_rows"]
    if (
        predecessor_manifest["source_count"] != len(source_rows)
        or len(source_rows) != 28
        or len({row["path"] for row in source_rows}) != len(source_rows)
    ):
        raise BindingRefusal("authority predecessor source-row closure differs")
    preserved_authority_rows: list[dict[str, Any]] = []
    for source_row in source_rows:
        expected_row = {
            "path": source_row["path"],
            "mode": source_row["mode"],
            "git_object": source_row["git_object"],
            "byte_count": source_row["bytes"],
            "raw_sha256": source_row["sha256"],
        }
        if expected_row != repository.row(
            ACCEPTED_BASE["commit"],
            source_row["path"],
            allowed_modes=frozenset({"100644"}),
        ):
            raise BindingRefusal(
                f"accepted authority predecessor row differs: {source_row['path']}"
            )
        preserved_authority_rows.append(expected_row)
    stage_e_guard_row = repository.row(
        ACCEPTED_BASE["commit"],
        "stage_e_harness/execution.py",
        allowed_modes=frozenset({"100644"}),
    )
    foundation_paths = {
        row["path"] for row in implementation["ordered_implementation_file_rows"]
    }
    stage_e_preserved_rows = [
        stage_e["implementation_path_manifest_git_row"],
        *stage_e["ordered_implementation_file_rows"],
    ]
    preserved_rows = (
        *(("accepted authority", row) for row in preserved_authority_rows),
        *(
            ("Stage E implementation", row)
            for row in stage_e_preserved_rows
            if row["path"] not in foundation_paths
        ),
        ("Stage E execution guard", stage_e_guard_row),
        *(
            ("local authority", row)
            for row in authority["ordered_local_authority_file_rows"]
        ),
        *(
            ("binding foundation", row)
            for row in implementation["ordered_implementation_file_rows"]
        ),
    )
    for label, row in preserved_rows:
        if row != repository.row(
            science_commit, row["path"], allowed_modes=frozenset({"100644"})
        ):
            raise BindingRefusal(
                f"scientific implementation changed preserved {label} row: {row['path']}"
            )
    if verifier_preimage is None:
        raise BindingRefusal("scientific implementation lacks verifier provenance")
    verifier_rows = verifier_preimage["ordered_verifier_file_rows"]
    verifier_paths = [row["path"] for row in verifier_rows]
    projected_paths = sorted(
        {
            path
            for projection in verifier_preimage["ordered_route_verifier_projections"]
            for path in projection["verifier_file_paths"]
        },
        key=lambda path: path.encode("utf-8"),
    )
    if (
        verifier_preimage["verifier_file_count"] != len(verifier_rows)
        or verifier_paths != projected_paths
    ):
        raise BindingRefusal("verifier complete route-file union differs")
    for row in verifier_rows:
        if row != repository.row(
            science_commit, row["path"], allowed_modes=frozenset({"100644"})
        ):
            raise BindingRefusal(f"verifier Git row differs: {row['path']}")
    repository.assert_material_closure(material_roots)


def validate_immutable_bundle_chain(
    validator: ClosedSchemaValidator,
    bundle: Mapping[str, Any],
    *,
    public_host_binding: Mapping[str, Any],
    identity_preimages: Mapping[Any, Any],
    referenced_bindings: Mapping[str, Mapping[str, Any]],
    repository: VerifiedGitRepository,
) -> None:
    """Recompute the complete local implementation/provenance identity chain."""

    specifications = (
        ("binding_implementation_identity", "binding_implementation_preimage", IDENTITY_KINDS["binding_implementation"]),
        ("authority_set_identity", "binding_authority_set_preimage", IDENTITY_KINDS["binding_authority_set"]),
        ("scientific_code_identity", "scientific_code_preimage", IDENTITY_KINDS["scientific_code"]),
        ("validator_identity", "binding_validator_preimage", IDENTITY_KINDS["binding_validator"]),
        ("stage_e_integration_identity", "stage_e_integration_preimage", IDENTITY_KINDS["stage_e_exact_target_integration"]),
    )
    resolved: dict[str, Any] = {}
    for field, definition, kind in specifications:
        identity = bundle[field]
        preimage = _resolve_preimage(identity_preimages, identity)
        validator.validate_definition(definition, preimage)
        verify_identity(identity, preimage, kind=kind)
        resolved[field] = preimage
    embedded_preimages = (
        (
            "authority_set_preimage",
            "authority_set_identity",
            "binding_authority_set_preimage",
            IDENTITY_KINDS["binding_authority_set"],
        ),
        (
            "binding_implementation_preimage",
            "binding_implementation_identity",
            "binding_implementation_preimage",
            IDENTITY_KINDS["binding_implementation"],
        ),
        (
            "binding_validator_preimage",
            "validator_identity",
            "binding_validator_preimage",
            IDENTITY_KINDS["binding_validator"],
        ),
    )
    for preimage_field, identity_field, definition, kind in embedded_preimages:
        embedded = bundle[preimage_field]
        validator.validate_definition(definition, embedded)
        verify_identity(bundle[identity_field], embedded, kind=kind)
        if not _same(embedded, resolved[identity_field]):
            raise BindingRefusal(
                f"bundle embedded v3 provenance differs: {preimage_field}"
            )
    for field, definition, kind in (
        ("scientific_implementation_identity", "scientific_implementation_preimage", IDENTITY_KINDS["scientific_implementation"]),
        ("verifier_identity", "verifier_implementation_preimage", IDENTITY_KINDS["verifier_implementation"]),
    ):
        identity = bundle[field]
        if identity is not None:
            preimage = _resolve_preimage(identity_preimages, identity)
            validator.validate_definition(definition, preimage)
            verify_identity(identity, preimage, kind=kind)
            resolved[field] = preimage
    for field, expected_kind in (
        ("installed_artifact_identity", IDENTITY_KINDS["installed_scientific_artifact"]),
        ("stage_e_evidence_identity", IDENTITY_KINDS["stage_e_exact_target_evidence_artifact"]),
    ):
        identity = bundle[field]
        raw = _resolve_preimage(identity_preimages, identity)
        if not isinstance(raw, bytes):
            raise BindingRefusal(f"raw artifact preimage is not bytes: {field}")
        verify_identity(identity, raw, kind=expected_kind)
    if bundle["stage_e_evidence_identity"]["value"] != STAGE_E_ARTIFACT_SHA256:
        raise BindingRefusal("Stage E evidence identity is not the accepted raw artifact digest")

    implementation = resolved["binding_implementation_identity"]
    authority = resolved["authority_set_identity"]
    correction_base = {
        "commit": FINAL_AUTHORITY_REQUIRED_TARGET_COMMIT,
        "tree": FINAL_AUTHORITY_REQUIRED_TARGET_TREE,
    }
    if not _same(implementation["accepted_base"], correction_base) or not _same(
        authority["accepted_base"], correction_base
    ):
        raise BindingRefusal("binding implementation/authority final-base mismatch")
    if not _same(implementation["integrated_authority_set_identity"], bundle["authority_set_identity"]):
        raise BindingRefusal("binding implementation names another authority set")
    if implementation["integrated_authority_commit"] != authority["integrated_authority_commit"]:
        raise BindingRefusal("binding implementation/authority integration commit mismatch")
    if not _same(
        implementation["ordered_integrated_authority_file_rows"], authority["ordered_local_authority_file_rows"]
    ):
        raise BindingRefusal("eighteen integrated authority rows differ across preimages")
    authority_rows = _require_exact_git_rows(
        authority["ordered_local_authority_file_rows"],
        AUTHORITY_PATHS,
        "authority-set local authority",
    )
    integrated_rows = _require_exact_git_rows(
        implementation["ordered_integrated_authority_file_rows"],
        AUTHORITY_PATHS,
        "binding implementation integrated authority",
    )
    implementation_rows = _require_exact_git_rows(
        implementation["ordered_implementation_file_rows"],
        IMPLEMENTATION_PATHS,
        "binding implementation",
    )
    if authority_rows != integrated_rows:
        raise BindingRefusal("authority rows do not reproduce across local preimages")

    binding_validator = resolved["validator_identity"]
    if not _same(binding_validator["binding_implementation_identity"], bundle["binding_implementation_identity"]):
        raise BindingRefusal("binding validator names another implementation")
    if binding_validator["implementation_commit"] != implementation["implementation_commit"] or binding_validator["implementation_tree"] != implementation["implementation_tree"]:
        raise BindingRefusal("binding validator source coordinate differs from binding implementation")
    if not _same(binding_validator["execution_environment_policy_identity"], public_host_binding["environment_identity"]):
        raise BindingRefusal("binding validator names another scientific environment policy")
    if not _same(binding_validator["host_validation_runtime_identity"], public_host_binding["host_validation_runtime_identity"]):
        raise BindingRefusal("binding validator names another host-validation runtime")
    validator_rows = _require_exact_git_rows(
        binding_validator["ordered_validator_source_file_rows"],
        VALIDATOR_SOURCE_PATHS,
        "binding validator source",
    )
    for path in VALIDATOR_SOURCE_PATHS:
        if not _same(validator_rows[path], implementation_rows[path]):
            raise BindingRefusal(f"binding validator source row differs from implementation: {path}")
    executable = binding_validator["executable_zipapp_manifest"]
    if (
        binding_validator["artifact_build_method"]
        != "CANONICAL_VALIDATOR_SOURCE_BUNDLE_V1"
        or binding_validator["executable_artifact_build_method"]
        != "DETERMINISTIC_LOCKED_VALIDATOR_ZIPAPP_V1"
        or executable["source_bundle_sha256"]
        != binding_validator["built_artifact_sha256"]
        or not _same(
            executable["host_validation_runtime_identity"],
            binding_validator["host_validation_runtime_identity"],
        )
    ):
        raise BindingRefusal("binding validator artifact projection differs")
    zip_members = executable["ordered_members"]
    if tuple(
        (row.get("archive_path"), row.get("source_path"))
        for row in zip_members
        if isinstance(row, Mapping)
    ) != VALIDATOR_ZIPAPP_PATHS:
        raise BindingRefusal("binding validator zipapp member order differs")
    for member, (archive_path, source_path) in zip(
        zip_members, VALIDATOR_ZIPAPP_PATHS, strict=True
    ):
        source_row = validator_rows[source_path]
        if (
            member["archive_path"] != archive_path
            or member["source_path"] != source_path
            or any(
                member[field] != source_row[field]
                for field in ("mode", "git_object", "byte_count", "raw_sha256")
            )
        ):
            raise BindingRefusal(f"binding validator zipapp source row differs: {archive_path}")

    scientific = resolved.get("scientific_implementation_identity")
    verifier = resolved.get("verifier_identity")
    code = resolved["scientific_code_identity"]
    if scientific is not None:
        expected_bindings = [row["campaign_execution_binding_identity"] for row in bundle["ordered_route_bindings"]]
        authority_projections = authority["ordered_route_authority_projections"]
        if [row["route_id"] for row in authority_projections] != list(CAMPAIGN_ORDER):
            raise BindingRefusal("authority-set route projection order mismatch")
        if not _same(
            [row["campaign_execution_binding_identity"] for row in authority_projections],
            expected_bindings,
        ):
            raise BindingRefusal("authority-set campaign-binding projection mismatch")
        for projection in authority_projections:
            reference = referenced_bindings.get(projection["route_id"])
            if not isinstance(reference, Mapping) or not isinstance(reference.get("record"), Mapping):
                raise BindingRefusal("authority-set projection lacks retained campaign binding")
            record = reference["record"]
            if not _same(projection["scientific_authority_identity"], record["authority_identity"]):
                raise BindingRefusal("authority-set scientific-authority projection mismatch")
            if not _same(
                projection["continuation_authority_identity"], record["continuation_authority_identity"]
            ):
                raise BindingRefusal("authority-set continuation-authority projection mismatch")
        relations = (
            (scientific["accepted_base"], ACCEPTED_BASE, "scientific implementation accepted base"),
            (scientific["binding_foundation_identity"], bundle["binding_implementation_identity"], "scientific binding foundation"),
            (scientific["authority_set_identity"], bundle["authority_set_identity"], "scientific authority set"),
            (scientific["scientific_code_identity"], bundle["scientific_code_identity"], "scientific code"),
            (scientific["installed_artifact_identity"], bundle["installed_artifact_identity"], "scientific artifact"),
            (scientific["ordered_route_ids"], list(CAMPAIGN_ORDER), "scientific route order"),
            (scientific["ordered_campaign_execution_binding_identities"], expected_bindings, "scientific campaign bindings"),
        )
        for actual, expected, label in relations:
            if not _same(actual, expected):
                raise BindingRefusal(f"{label} projection mismatch")
        if scientific["implementation_commit"] != code["implementation_commit"] or scientific["implementation_tree"] != code["implementation_tree"]:
            raise BindingRefusal("scientific code and implementation coordinates differ")
        if scientific["installed_artifact_source_commit"] != scientific["implementation_commit"] or scientific["installed_artifact_source_tree"] != scientific["implementation_tree"]:
            raise BindingRefusal("installed artifact source coordinate differs from scientific implementation")
        if scientific["installed_artifact_raw_sha256"] != bundle["installed_artifact_identity"]["value"]:
            raise BindingRefusal("installed artifact raw digest differs from scientific implementation")
        if verifier is None or not _same(verifier["scientific_implementation_identity"], bundle["scientific_implementation_identity"]):
            raise BindingRefusal("verifier does not name the exact scientific implementation")
        if verifier["implementation_commit"] != scientific["implementation_commit"] or verifier["implementation_tree"] != scientific["implementation_tree"]:
            raise BindingRefusal("verifier coordinate differs from scientific implementation")
        verifier_projections = verifier["ordered_route_verifier_projections"]
        if [row["route_id"] for row in verifier_projections] != list(CAMPAIGN_ORDER) or not _same(
            [row["campaign_execution_binding_identity"] for row in verifier_projections],
            expected_bindings,
        ):
            raise BindingRefusal("verifier route/campaign-binding projection mismatch")

    stage_e = resolved["stage_e_integration_identity"]
    if not _same(stage_e["stage_e_evidence_identity"], bundle["stage_e_evidence_identity"]):
        raise BindingRefusal("Stage E integration names another evidence artifact")
    if (
        stage_e["artifact_sha256"] != STAGE_E_ARTIFACT_SHA256
        or stage_e["stage_e_evidence_identity"]["value"] != STAGE_E_ARTIFACT_SHA256
        or stage_e["implementation_path_manifest_git_row"]["path"]
        != stage_e["implementation_path_manifest_path"]
        or stage_e["implementation_path_count"]
        != len(stage_e["ordered_implementation_file_rows"])
    ):
        raise BindingRefusal("Stage E integration artifact or path projection differs")
    _validate_repository_provenance(
        validator,
        repository=repository,
        bundle=bundle,
        resolved=resolved,
        identity_preimages=identity_preimages,
    )


def _record_identity(record: Mapping[str, Any]) -> dict[str, str]:
    schema_name = record.get("schema")
    if schema_name == "private_execution_host_manifest/v1":
        return sha256_identity(IDENTITY_KINDS["private_host_manifest"], dict(record))
    if schema_name == "stage_f_sealed_campaign_packet/v2":
        return sha256_identity(IDENTITY_KINDS["sealed_campaign_packet"], dict(record))
    digest_field = EMBEDDED_DIGEST_FIELDS.get(schema_name)
    if digest_field is None:
        raise BindingRefusal(f"record has no frozen identity preimage rule: {schema_name}")
    identity_kind = {
        "stage_f_inert_container_observation/v1": IDENTITY_KINDS["inert_container"],
    }.get(schema_name, schema_name)
    return verify_embedded_digest(record, digest_field, kind=identity_kind)


def _expect_identity(actual: Any, record: Mapping[str, Any], label: str) -> None:
    if not _same(actual, _record_identity(record)):
        raise BindingRefusal(f"{label} does not identify the supplied retained record")


def _parse_utc(value: Any, label: str) -> datetime:
    if not isinstance(value, str) or re.fullmatch(
        r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?Z", value
    ) is None:
        raise BindingRefusal(f"{label} is not a closed UTC timestamp")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise BindingRefusal(f"{label} is not a real UTC timestamp") from exc
    if parsed.tzinfo != timezone.utc:
        raise BindingRefusal(f"{label} is not UTC")
    return parsed


def _require_order(before: tuple[datetime, str], after: tuple[datetime, str]) -> None:
    if before[0] > after[0]:
        raise BindingRefusal(f"timestamp order violation: {before[1]} after {after[1]}")


def _require_fresh(observed: tuple[datetime, str], consumed: tuple[datetime, str]) -> None:
    _require_order(observed, consumed)
    age = (consumed[0] - observed[0]).total_seconds()
    if age > MAXIMUM_SNAPSHOT_AGE_SECONDS:
        raise BindingRefusal(f"stale evidence: {observed[1]} is {age:g}s before {consumed[1]}")


def _zero(record: Mapping[str, Any]) -> None:
    assert_zero_science_counters(record.get("scientific_counters"))


_CORRECTION_CONTEXT_IDENTITY_KINDS = {
    "root_protection_epoch_identity": IDENTITY_KINDS["root_protection_epoch"],
    "evidence_ledger_predecessor_identity": IDENTITY_KINDS["evidence_ledger"],
    "capacity_publication_identity": IDENTITY_KINDS["capacity_publication"],
    "capacity_consumption_closure_identity": IDENTITY_KINDS["capacity_consumption_closure"],
    "host_prerequisite_snapshot_identity": IDENTITY_KINDS["host_prerequisite_snapshot"],
}

_INLINE_RECORD_IDENTITY_PAIRS = (
    ("inert_container_identity", "inert_container_observation"),
    ("container_identity", "container_observation"),
    ("container_start_capability_identity", "container_start_capability"),
    ("container_start_intent_identity", "container_start_intent"),
    ("root_watch_live_state_identity", "root_watch_live_state"),
    ("final_prestart_capacity_live_gate_identity", "final_prestart_capacity_live_gate"),
    ("host_prerequisite_snapshot_identity", "host_prerequisite_snapshot"),
    ("scientific_launch_handoff_identity", "scientific_launch_handoff"),
)


def _require_identity_kind(identity: Any, kind: str, label: str) -> None:
    _validate_external_identity(identity, label)
    if identity["kind"] != kind:
        raise BindingRefusal(f"{label} identity kind differs: expected {kind}")


def _decode_canonical_base64(value: Any, label: str) -> bytes:
    if not isinstance(value, str):
        raise BindingRefusal(f"{label} is not base64 text")
    try:
        raw = base64.b64decode(value, validate=True)
    except (ValueError, base64.binascii.Error) as exc:
        raise BindingRefusal(f"{label} is not strict base64") from exc
    if base64.b64encode(raw).decode("ascii") != value:
        raise BindingRefusal(f"{label} has noncanonical padding bits")
    return raw


def _validate_raw_volume_capacity(record: Mapping[str, Any]) -> None:
    raw = _decode_canonical_base64(
        record["ntfs_volume_data_output_bytes_base64"], "NTFS volume-data output"
    )
    allocation_unit = record["sectors_per_cluster"] * record["bytes_per_sector"]
    disk_free = record["number_of_free_clusters"] * allocation_unit
    disk_capacity = record["total_number_of_clusters"] * allocation_unit
    ntfs = record["ntfs_volume_data"]
    ntfs_free = ntfs["free_clusters"] * ntfs["bytes_per_cluster"]
    ntfs_capacity = ntfs["total_clusters"] * ntfs["bytes_per_cluster"]
    conservative_free = min(
        disk_free,
        record["available_to_caller_bytes"],
        record["total_number_of_free_bytes"],
        ntfs_free,
    )
    conservative_capacity = min(
        disk_capacity,
        record["total_number_of_bytes"],
        ntfs_capacity,
    )
    if (
        record["ntfs_volume_data_output_byte_count"] != len(raw)
        or record["ntfs_volume_data_output_sha256"] != sha256_hex(raw)
        or record["allocation_unit_bytes"] != allocation_unit
        or record["get_disk_free_space_w_free_bytes"] != disk_free
        or record["get_disk_free_space_w_capacity_bytes"] != disk_capacity
        or record["ntfs_volume_data_free_bytes"] != ntfs_free
        or record["ntfs_volume_data_capacity_bytes"] != ntfs_capacity
        or record["conservative_observed_free_bytes"] != conservative_free
        or record["conservative_observed_capacity_bytes"] != conservative_capacity
        or ntfs["bytes_per_sector"] != record["bytes_per_sector"]
        or ntfs["bytes_per_cluster"] != allocation_unit
        or ntfs["free_clusters"] != record["number_of_free_clusters"]
        or ntfs["total_clusters"] != record["total_number_of_clusters"]
        or ntfs["number_sectors"]
        != record["total_number_of_clusters"] * record["sectors_per_cluster"]
    ):
        raise BindingRefusal("raw volume-capacity outputs or formulas do not reconcile")


def _validate_retained_subtree(record: Mapping[str, Any]) -> None:
    entries = record["inventory_entries"]
    paths = [entry["relative_path"] for entry in entries]
    expected_paths = sorted(
        (unicodedata.normalize("NFC", path) for path in paths),
        key=lambda path: path.encode("utf-8"),
    )
    direct_sum = sum(entry["accounted_bytes"] for entry in entries)
    if (
        record["inventory_entry_count"] != len(entries)
        or paths != expected_paths
        or len(paths) != len(set(paths))
        or "." not in paths
        or record["direct_accounted_bytes_sum"] != direct_sum
        or record["retained_evidence_live_allocated_bytes"] != direct_sum
    ):
        raise BindingRefusal("retained-subtree inventory/count/order/direct sum differs")


def _validate_capacity_directory_rows(rows: Any) -> None:
    if not isinstance(rows, list):
        raise BindingRefusal("capacity affected-directory rows are not an array")
    paths: list[bytes] = []
    for row in rows:
        if not isinstance(row, Mapping):
            raise BindingRefusal("capacity affected-directory row is not an object")
        path = canonical_bytes(row["path_identity"])
        paths.append(path)
        before = (
            row["before_allocation_size_bytes"]
            + row["before_bitmap_upper_bound_bytes"]
            + row["before_metadata_record_upper_bound_bytes"]
        )
        after = (
            row["after_allocation_size_bytes"]
            + row["after_bitmap_upper_bound_bytes"]
            + row["after_metadata_record_upper_bound_bytes"]
        )
        if (
            row["before_file_id_128"] != row["after_file_id_128"]
            or after < before
            or row["directory_allocation_growth_upper_bound_bytes"] != after - before
        ):
            raise BindingRefusal("capacity directory continuity/growth formula differs")
    if len(paths) != len(set(paths)):
        raise BindingRefusal("capacity affected-directory rows repeat a path identity")


def _validate_corrected_capacity(definition: str, record: Mapping[str, Any]) -> None:
    gib = 1073741824
    component_fields = (
        "primary_logical_output_bytes",
        "independent_audit_copy_bytes",
        "dynamic_growth_physical_write_bytes",
        "checkpoint_and_write_overhead_bytes",
        "temporary_archive_bytes",
        "retained_evidence_bytes",
    )
    if definition == "stage_f_capacity_usage_projection":
        if record["total_envelope_usage_bytes"] != sum(
            record[field] for field in component_fields
        ):
            raise BindingRefusal("capacity usage projection six-component sum differs")
        _record_identity(record)
        return
    if definition == "stage_f_raw_volume_capacity_observation":
        _validate_raw_volume_capacity(record)
        return
    if definition == "stage_f_retained_subtree_allocation_observation":
        _validate_retained_subtree(record)
        return
    if definition == "stage_f_capacity_publication_observation":
        _validate_capacity_directory_rows(record["affected_directory_rows"])
        subtree = record["postpublication_retained_subtree_observation"]
        raw = record["postpublication_raw_volume_observation"]
        _validate_retained_subtree(subtree)
        _validate_raw_volume_capacity(raw)
        if (
            record["affected_directory_row_count"] != len(record["affected_directory_rows"])
            or record["retained_evidence_live_allocated_bytes"]
            != subtree["retained_evidence_live_allocated_bytes"]
            or record["retained_evidence_live_allocated_bytes"] > 8 * gib
            or record["fresh_observed_free_bytes"]
            != raw["conservative_observed_free_bytes"]
        ):
            raise BindingRefusal("capacity publication direct observations do not reconcile")
        return
    if definition == "stage_f_capacity_consumption_closure":
        causal = record["causal_postcutoff_files"]
        paths = [row["relative_path"] for row in causal]
        expected_paths = sorted(
            (unicodedata.normalize("NFC", path) for path in paths),
            key=lambda path: path.encode("utf-8"),
        )
        _validate_capacity_directory_rows(record["affected_directory_rows"])
        subtree = record["current_retained_subtree_observation"]
        raw = record["current_raw_volume_observation"]
        _validate_retained_subtree(subtree)
        _validate_raw_volume_capacity(raw)
        live = subtree["retained_evidence_live_allocated_bytes"]
        snapshot = record["storage_capacity_snapshot"]
        projection = record["component_usage_projection"]
        projected_usage = {field: projection[field] for field in component_fields}
        projected_usage["total_envelope_usage_bytes"] = projection[
            "total_envelope_usage_bytes"
        ]
        _expect_identity(
            record["storage_capacity_snapshot_identity"],
            snapshot,
            "capacity closure storage snapshot",
        )
        _expect_identity(
            record["component_usage_projection_identity"],
            projection,
            "capacity closure component projection",
        )
        if (
            record["causal_postcutoff_file_count"] != len(causal)
            or paths != expected_paths
            or len(paths) != len(set(paths))
            or record["retained_evidence_live_allocated_bytes"] != live
            or record["retained_evidence_remaining_tail_bytes"] != 8 * gib - live
            or record["observed_free_bytes"] != raw["conservative_observed_free_bytes"]
            or record["observed_free_bytes"]
            < max(350 * gib, record["remaining_reserved_envelope_bytes"])
            or projection["total_envelope_usage_bytes"]
            != sum(projection[field] for field in component_fields)
            or snapshot["current_envelope_usage"] != projected_usage
            or record["total_envelope_usage_bytes"]
            != projection["total_envelope_usage_bytes"]
            or record["remaining_reserved_envelope_bytes"]
            != 715112054784 - record["total_envelope_usage_bytes"]
        ):
            raise BindingRefusal(
                "capacity-consumption direct rows/projection/tail/free-space formula differs"
            )
        return
    if definition == "stage_f_capacity_live_gate":
        subtree = record["fresh_retained_subtree_observation"]
        raw = record["fresh_raw_volume_observation"]
        _validate_retained_subtree(subtree)
        _validate_raw_volume_capacity(raw)
        closure = record["capacity_consumption_closure"]
        capability = record["exact_following_operation_capability"]
        capability_kind = {
            "HOST_VALIDATION_PROCESS_RESUME": IDENTITY_KINDS[
                "host_validation_process_resume_capability"
            ],
            "SCIENTIFIC_CONTAINER_START": IDENTITY_KINDS["container_start_capability"],
            "CONTINUATION_SEGMENT_START": IDENTITY_KINDS[
                "continuation_segment_start_capability"
            ],
        }[record["gate_role"]]
        _expect_identity(
            record["capacity_consumption_closure_identity"],
            closure,
            "capacity live gate closure",
        )
        verify_embedded_digest(
            capability,
            "capability_sha256",
            kind=capability_kind,
        )
        if (
            record["retained_evidence_live_allocated_bytes"]
            != subtree["retained_evidence_live_allocated_bytes"]
            or record["observed_free_bytes"] != raw["conservative_observed_free_bytes"]
            or record["retained_evidence_ceiling_bytes"] != 8 * gib
            or record["minimum_free_bytes"] != 350 * gib
            or record["observed_free_bytes"]
            < max(record["minimum_free_bytes"], record["remaining_reserved_envelope_bytes"])
            or not _same(
                record["exact_following_operation_capability_identity"],
                sha256_identity(
                    capability_kind,
                    {
                        key: value
                        for key, value in capability.items()
                        if key != "capability_sha256"
                    },
                ),
            )
            or not _same(
                record["component_usage_projection_identity"],
                closure["component_usage_projection_identity"],
            )
            or record["total_envelope_usage_bytes"]
            != closure["total_envelope_usage_bytes"]
            or record["remaining_reserved_envelope_bytes"]
            != closure["remaining_reserved_envelope_bytes"]
        ):
            raise BindingRefusal(
                "capacity live-gate direct observations/projection/capability formula differs"
            )


def _validate_ledger_record_links(record: Mapping[str, Any]) -> None:
    ticket = record["append_ticket"]
    _record_identity(ticket)
    projections = (
        ("root_protection_epoch_identity", "root_protection_epoch_identity"),
        ("ledger_file_path_identity", "ledger_file_path_identity"),
        ("ledger_file_volume_serial_number_uint64", "ledger_file_volume_serial_number_uint64"),
        ("ledger_file_id_128", "ledger_file_id_128"),
        ("previous_entry_identity", "previous_entry_identity"),
        ("record_role", "record_role"),
        ("record_identity", "record_identity"),
    )
    if any(not _same(ticket[left], record[right]) for left, right in projections):
        raise BindingRefusal("ledger append ticket does not project the ledger record")
    issued = _parse_utc(ticket["issued_utc"], "ledger append ticket issuance")
    expires = _parse_utc(ticket["expires_utc"], "ledger append ticket expiry")
    created = _parse_utc(record["created_utc"], "ledger record creation")
    if issued > created or created > expires:
        raise BindingRefusal("ledger record was created outside its append-ticket interval")
    if record["entry_type"] == "GENESIS":
        if (
            ticket["expected_append_start_offset"] != 0
            or not _same(record["record_identity"], record["execution_attempt_genesis_identity"])
        ):
            raise BindingRefusal("ledger genesis ticket/record projection differs")
    else:
        previous_append = record["previous_entry_append_observation"]
        if (
            not _same(previous_append["entry_identity"], record["previous_entry_identity"])
            or ticket["expected_append_start_offset"]
            != previous_append["postflush_file_size"]
            or any(
                not _same(previous_append[field], record[field])
                for field in (
                    "ledger_file_path_identity",
                    "ledger_file_volume_serial_number_uint64",
                    "ledger_file_id_128",
                    "ledger_handle_value_uint64",
                )
            )
        ):
            raise BindingRefusal("ledger predecessor append/ticket/file continuity differs")


def _validate_mutation_ticket(record: Mapping[str, Any]) -> None:
    operation = record["operation"]
    projection = record["scientific_mutation_authority_projection"]
    if operation in {
        "FROZEN_PER_ROUTE_AUTHORIZED_WRITE",
        "FROZEN_CONTINUATION_AUTHORIZED_WRITE",
    }:
        selected_field = (
            "scientific_authority_identity"
            if operation == "FROZEN_PER_ROUTE_AUTHORIZED_WRITE"
            else "continuation_authority_identity"
        )
        if (
            projection["route_id"] != record["route_id"]
            or not _same(
                projection[selected_field],
                record["scientific_mutation_authority_identity"],
            )
        ):
            raise BindingRefusal(
                "scientific mutation ticket route/selected authority projection differs"
            )
    issued = _parse_utc(record["issued_utc"], "mutation ticket issuance")
    expires = _parse_utc(record["expires_utc"], "mutation ticket expiry")
    if issued > expires:
        raise BindingRefusal("mutation ticket expires before it is issued")
    _record_identity(record)


def _validate_start_record_links(definition: str, record: Mapping[str, Any]) -> None:
    if definition == "stage_f_host_validation_process_resume_capability":
        attestation = record["suspended_process_launch_attestation"]
        _record_identity(attestation)
        expected_role = {
            "ORCHESTRATOR": "ORCHESTRATOR_PROCESS",
            "PRE_RESTART": "PRE_RESTART_PROCESS",
            "POST_RESTART": "POST_RESTART_PROCESS",
        }[record["launch_phase"]]
        projections = (
            ("launch_phase", "phase"),
            ("resume_target_role", "projected_process_role"),
            ("root_protection_epoch_identity", "root_protection_epoch_identity"),
            ("immutable_invocation_identity", "immutable_invocation_identity"),
            ("application_name_path_identity", "application_name_path_identity"),
            ("command_line_sha256", "command_line_sha256"),
            ("resume_target_process_id", "process_id"),
            ("resume_target_thread_id", "thread_id"),
            ("resume_target_thread_handle_value_uint64", "thread_handle_value_uint64"),
            (
                "resume_target_process_creation_filetime_uint64",
                "process_creation_filetime_uint64",
            ),
        )
        if record["resume_target_role"] != expected_role or any(
            not _same(record[left], attestation[right]) for left, right in projections
        ):
            raise BindingRefusal(
                "host-validation resume capability/attestation phase-role target differs"
            )
        _record_identity(record)
        return
    if definition == "stage_f_continuation_segment_start_capability":
        projection = record["route_authority_projection"]
        if (
            projection["route_id"] != record["route_id"]
            or not _same(
                projection["continuation_authority_identity"],
                record["resolved_continuation_authority_identity"],
            )
        ):
            raise BindingRefusal(
                "continuation capability route/continuation-authority projection differs"
            )
        _record_identity(record)
        return
    if definition == "stage_f_container_start_capability":
        if record["endpoint"] != f"/containers/{record['container_id']}/start":
            raise BindingRefusal("start capability endpoint identifies another container")
        raw = _decode_canonical_base64(record["request_bytes_base64"], "start request")
        if record["request_sha256"] != sha256_hex(raw):
            raise BindingRefusal("start capability request digest differs")
        return
    if definition == "stage_f_container_start_intent":
        inert = record["inert_container_observation"]
        capability = record["container_start_capability"]
        if (
            not _same(capability["inert_container_identity"], record["inert_container_identity"])
            or capability["container_id"] != inert["container_id"]
        ):
            raise BindingRefusal("start intent capability/inert-container target differs")
        return
    if definition == "stage_f_scientific_launch_handoff":
        intent = record["container_start_intent"]
        capability = record["container_start_capability"]
        if (
            not _same(record["container_identity"], intent["inert_container_identity"])
            or not _same(record["container_start_capability_identity"], intent["container_start_capability_identity"])
            or not _same(capability, intent["container_start_capability"])
            or not _same(
                record["final_prestart_capacity_live_gate"]["exact_following_operation_capability_identity"],
                record["container_start_capability_identity"],
            )
            or record["final_prestart_capacity_live_gate"]["gate_role"]
            != "SCIENTIFIC_CONTAINER_START"
        ):
            raise BindingRefusal("scientific handoff intent/capability/final-gate projection differs")
        return
    if definition == "stage_f_container_start_receipt" and record["scientific_launch_handoff"] is not None:
        handoff = record["scientific_launch_handoff"]
        for receipt_field, handoff_field in (
            ("container_start_intent_identity", "container_start_intent_identity"),
            ("final_prestart_capacity_live_gate_identity", "final_prestart_capacity_live_gate_identity"),
            ("host_prerequisite_snapshot_identity", "host_prerequisite_snapshot_identity"),
            ("container_start_capability_identity", "container_start_capability_identity"),
            ("inert_container_identity", "container_identity"),
        ):
            if not _same(record[receipt_field], handoff[handoff_field]):
                raise BindingRefusal("start receipt does not project its frozen handoff")


def _validate_correction_context(
    validator: ClosedSchemaValidator,
    record: Mapping[str, Any],
) -> None:
    """Validate corrected context links after the record's schema has passed."""

    if "scientific_counters" in record:
        _zero(record)
    for field, kind in _CORRECTION_CONTEXT_IDENTITY_KINDS.items():
        if field in record:
            _require_identity_kind(record[field], kind, field)
    if "evidence_ledger_predecessor_append_observation" in record:
        append_observation = record["evidence_ledger_predecessor_append_observation"]
        validator.validate_definition(
            "stage_f_evidence_ledger_append_observation",
            append_observation,
        )
        if (
            "evidence_ledger_predecessor_identity" not in record
            or not _same(
                append_observation["entry_identity"],
                record["evidence_ledger_predecessor_identity"],
            )
        ):
            raise BindingRefusal(
                "ledger predecessor append observation identifies another entry"
            )
    for identity_field, record_field in _INLINE_RECORD_IDENTITY_PAIRS:
        if identity_field not in record or record_field not in record:
            continue
        identity = record[identity_field]
        nested = record[record_field]
        if identity is None or nested is None:
            if identity is not None or nested is not None:
                raise BindingRefusal(
                    f"{identity_field}/{record_field} null-presence projection differs"
                )
            continue
        if not isinstance(nested, Mapping):
            raise BindingRefusal(f"{record_field} is not an embedded record")
        _expect_identity(identity, nested, f"embedded {record_field}")


def validate_corrected_record(
    validator: ClosedSchemaValidator,
    definition: str,
    record: Mapping[str, Any],
    *,
    as_root: bool = False,
) -> dict[str, str] | None:
    """Schema-first validation for one corrected record, including digest links.

    ``as_root`` additionally proves membership in the correction schema's closed
    root union and refuses all three explicitly nested-only record definitions.
    """

    if not isinstance(definition, str) or not isinstance(record, Mapping):
        raise BindingRefusal("corrected record definition/value is malformed")
    validator.validate_definition(definition, record)
    if as_root:
        if definition in NESTED_ONLY_DEFINITIONS:
            raise BindingRefusal(f"nested-only correction record used as a root: {definition}")
        validator.validate(record)
    _validate_correction_context(validator, record)
    _validate_corrected_capacity(definition, record)
    if definition in {
        "stage_f_evidence_ledger_genesis",
        "stage_f_evidence_ledger_entry",
    }:
        _validate_ledger_record_links(record)
    if definition == "stage_f_authorized_mutation_ticket":
        _validate_mutation_ticket(record)
    _validate_start_record_links(definition, record)
    if record.get("schema") in EMBEDDED_DIGEST_FIELDS:
        return _record_identity(record)
    return None


def _require_same_stable_correction_context(
    left: Mapping[str, Any], right: Mapping[str, Any], label: str
) -> None:
    for field in (
        "root_protection_epoch_identity",
        "capacity_publication_identity",
        "capacity_consumption_closure_identity",
        "host_prerequisite_snapshot_identity",
    ):
        if field in left and field in right and not _same(left[field], right[field]):
            raise BindingRefusal(f"{label} stable correction context differs: {field}")


def _require_same_v3_provenance(
    left: Mapping[str, Any], right: Mapping[str, Any], label: str
) -> None:
    """Require every successor consumer to carry the same direct v3 chain."""

    fields_and_kinds = (
        ("authority_set_identity", IDENTITY_KINDS["binding_authority_set"]),
        ("binding_implementation_identity", IDENTITY_KINDS["binding_implementation"]),
        ("validator_identity", IDENTITY_KINDS["binding_validator"]),
    )
    for field, kind in fields_and_kinds:
        if field not in left or field not in right:
            raise BindingRefusal(f"{label} lacks direct v3 provenance: {field}")
        _require_identity_kind(left[field], kind, f"{label}.{field}.left")
        _require_identity_kind(right[field], kind, f"{label}.{field}.right")
        if not _same(left[field], right[field]):
            raise BindingRefusal(f"{label} direct v3 provenance differs: {field}")


def _identity_values(identities: Iterable[Mapping[str, Any]]) -> list[tuple[Any, Any]]:
    return [(item.get("kind"), item.get("value")) for item in identities]


def _assert_distinct_identities(identities: Iterable[Mapping[str, Any]], label: str) -> None:
    values = _identity_values(identities)
    if len(values) != len(set(values)):
        raise BindingRefusal(f"duplicate or reused {label}")


def _validate_sorted_installed_files(preimage: Mapping[str, Any], label: str) -> None:
    rows = preimage["installed_files"]
    paths = [row["relative_path"] for row in rows]
    normalized = [unicodedata.normalize("NFC", value) for value in paths]
    expected = sorted(normalized, key=lambda value: value.encode("utf-8"))
    if paths != normalized or normalized != expected or len(normalized) != len(set(normalized)):
        raise BindingRefusal(f"{label} installed-file projection is not unique UTF-8 byte order")


def validate_private_host_manifest(
    validator: ClosedSchemaValidator, manifest: Mapping[str, Any]
) -> dict[str, Any]:
    validator.validate_definition("private_execution_host_manifest", manifest)
    _zero(manifest)
    if manifest["public_host_alias"] != PUBLIC_HOST_ALIAS:
        raise BindingRefusal("private host alias mismatch")
    validator.validate_definition("host_validation_runtime_preimage", manifest["host_validation_runtime_preimage"])
    verify_identity(
        manifest["host_validation_runtime_identity"],
        manifest["host_validation_runtime_preimage"],
        kind=IDENTITY_KINDS["host_validation_runtime"],
    )
    runtime = manifest["runtime"]
    if runtime["python_executable_sha256"] != manifest["host_validation_runtime_preimage"]["python_executable_sha256"]:
        raise BindingRefusal("host-runtime Python executable digest mismatch")
    dependency_preimages = runtime["dependency_preimages"]
    dependency_identities = runtime["dependency_identities"]
    if len(dependency_preimages) != len(dependency_identities):
        raise BindingRefusal("installed dependency identity/preimage count mismatch")
    for index, (identity, preimage) in enumerate(zip(dependency_identities, dependency_preimages)):
        validator.validate_definition("installed_distribution_preimage", preimage)
        _validate_sorted_installed_files(preimage, f"dependency[{index}]")
        verify_identity(identity, preimage, kind=IDENTITY_KINDS["installed_python_distribution"])
    policy_identities: dict[str, dict[str, str]] = {}
    for name, (definition, kind) in POLICY_DEFINITIONS.items():
        serialized = manifest["policy_preimages"][name]
        parsed = strict_loads(serialized, require_canonical=True)
        validator.validate_definition(definition, parsed)
        policy_identities[name] = sha256_identity(kind, parsed)
    environment = strict_loads(manifest["policy_preimages"]["environment"], require_canonical=True)
    if environment["python_executable_sha256"] != runtime["python_executable_sha256"]:
        raise BindingRefusal("environment policy Python executable digest mismatch")
    if not _same(environment["dependency_identities"], dependency_identities):
        raise BindingRefusal("environment policy dependency identity order mismatch")
    expected_dependencies = [
        f"{preimage['name']}=={preimage['version']}" for preimage in dependency_preimages
    ]
    if environment["dependencies_in_order"] != expected_dependencies:
        raise BindingRefusal("environment dependency labels do not match retained distributions")
    _validate_private_directory_layout(manifest["filesystem"])
    filesystem_preimage = {
        key: value for key, value in manifest["filesystem"].items() if key != "filesystem_identity"
    }
    verify_identity(
        manifest["filesystem"]["filesystem_identity"],
        filesystem_preimage,
        kind=IDENTITY_KINDS["filesystem_binding"],
    )
    return {
        "manifest_identity": sha256_identity(IDENTITY_KINDS["private_host_manifest"], dict(manifest)),
        "policy_identities": policy_identities,
        "filesystem_identity": manifest["filesystem"]["filesystem_identity"],
        "host_validation_runtime_identity": manifest["host_validation_runtime_identity"],
    }


def _assert_no_public_path(value: Any, path: str = "$") -> None:
    if isinstance(value, str):
        if re.match(r"^[A-Za-z]:[\\/]", value) or value.startswith("\\\\") or value.startswith("/"):
            raise BindingRefusal(f"personal or absolute path disclosed at {path}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _assert_no_public_path(item, f"{path}[{index}]")
    elif isinstance(value, dict):
        for key, item in value.items():
            _assert_no_public_path(item, f"{path}.{key}")


def validate_public_host_binding(
    validator: ClosedSchemaValidator,
    public_binding: Mapping[str, Any],
    *,
    private_manifest: Mapping[str, Any],
) -> dict[str, str]:
    validator.validate_definition("public_execution_host_binding", public_binding)
    _zero(public_binding)
    _assert_no_public_path(public_binding)
    private_projection = validate_private_host_manifest(validator, private_manifest)
    if public_binding["public_host_alias"] != private_manifest["public_host_alias"]:
        raise BindingRefusal("public/private alias mismatch")
    if not _same(public_binding["private_host_manifest_identity"], private_projection["manifest_identity"]):
        raise BindingRefusal("public binding does not identify retained private manifest bytes")
    for name, field in PUBLIC_POLICY_IDENTITY_FIELDS.items():
        if not _same(public_binding[field], private_projection["policy_identities"][name]):
            raise BindingRefusal(f"public/private {name} policy digest mismatch")
    if not _same(public_binding["filesystem_identity"], private_projection["filesystem_identity"]):
        raise BindingRefusal("public/private filesystem identity mismatch")
    if not _same(
        public_binding["host_validation_runtime_identity"],
        private_projection["host_validation_runtime_identity"],
    ):
        raise BindingRefusal("public/private host-validation-runtime identity mismatch")
    if not _same(
        public_binding["private_durability_bundle_identity"],
        private_manifest["durability_bundle_identity"],
    ):
        raise BindingRefusal("public/private durability-bundle identity mismatch")
    return _record_identity(public_binding)


def _campaign_preimage(record: Mapping[str, Any]) -> dict[str, Any]:
    if record.get("schema") != "campaign_execution_binding/v2" or "binding_sha256" not in record:
        raise BindingRefusal("referenced campaign binding is not campaign_execution_binding/v2")
    return {key: value for key, value in record.items() if key != "binding_sha256"}


def _validate_external_identity(value: Any, label: str) -> None:
    if not isinstance(value, Mapping) or set(value) != {"kind", "value", "sha256"}:
        raise BindingRefusal(f"{label} is not a closed identity")
    if not isinstance(value["kind"], str) or not value["kind"]:
        raise BindingRefusal(f"{label} identity kind is empty")
    if not isinstance(value["value"], str) or re.fullmatch(r"[0-9a-f]{64}", value["value"]) is None:
        raise BindingRefusal(f"{label} identity value is not a SHA-256 digest")
    if value["sha256"] != value["value"]:
        raise BindingRefusal(f"{label} identity value and sha256 differ")


def _positive_integer(value: Any, label: str) -> None:
    if not _is_integer(value) or value < 1:
        raise BindingRefusal(f"{label} is not a positive integer")


def _validate_inherited_campaign_binding(record: Mapping[str, Any]) -> None:
    if not isinstance(record, Mapping) or set(record) != CAMPAIGN_BINDING_FIELDS:
        raise BindingRefusal("referenced campaign binding field closure mismatch")
    if record["schema"] != "campaign_execution_binding/v2":
        raise BindingRefusal("referenced campaign binding schema mismatch")
    if record["study_id"] not in {route for route in CAMPAIGN_ORDER if route != "SD-01-GROWTH-v1"}:
        raise BindingRefusal("referenced campaign binding study ID is outside SD-01..SD-14")
    if not isinstance(record["campaign_id"], str) or not record["campaign_id"]:
        raise BindingRefusal("referenced campaign ID is empty")
    if record["exact_or_approximate_label"] not in {"EXACT", "MODEL_EXACT_NUMERICAL"}:
        raise BindingRefusal("referenced exact/approximate label is invalid")
    if record["continuation_mode"] not in {
        "WITHIN_RUN_CHECKPOINT_CONTINUATION",
        "BETWEEN_ATOMIC_CASE_CONTINUATION_ONLY",
        "INHERITED_AUTHORITY_REQUIRED",
    }:
        raise BindingRefusal("referenced continuation mode is invalid")
    for field, expected in (
        ("silent_approximation_permitted", False),
        ("arbitrary_n_completion_claim", False),
        ("sealed_before_stage_f", True),
        ("outcome_inspected_before_seal", False),
    ):
        if record[field] is not expected:
            raise BindingRefusal(f"referenced campaign binding invariant mismatch: {field}")
    identity_fields = CAMPAIGN_BINDING_FIELDS - {
        "schema", "campaign_id", "study_id", "ordered_scientific_run_identities",
        "exact_or_approximate_label", "continuation_mode", "attempt_watchdogs", "campaign_budget",
        "atomic_case_identity_rule", "silent_approximation_permitted", "arbitrary_n_completion_claim",
        "sealed_before_stage_f", "outcome_inspected_before_seal", "binding_sha256",
    }
    for field in identity_fields:
        _validate_external_identity(record[field], f"campaign.{field}")
    runs = record["ordered_scientific_run_identities"]
    if not isinstance(runs, list) or not runs:
        raise BindingRefusal("referenced campaign has no ordered scientific-run identities")
    for index, identity in enumerate(runs):
        _validate_external_identity(identity, f"campaign.ordered_scientific_run_identities[{index}]")
    if not isinstance(record["atomic_case_identity_rule"], str) or not record["atomic_case_identity_rule"]:
        raise BindingRefusal("referenced atomic-case identity rule is empty")
    watchdogs = record["attempt_watchdogs"]
    watchdog_fields = {
        "wall_time_nanoseconds", "process_tree_peak_resident_memory_bytes", "primary_evaluations",
        "physical_trace_bytes_written", "physical_output_bytes_written", "maximum_depth",
        "applicable_stage_d_hard_cap_profile_identity", "within_accepted_stage_d_profile",
    }
    if not isinstance(watchdogs, Mapping) or set(watchdogs) != watchdog_fields:
        raise BindingRefusal("campaign attempt-watchdog field closure mismatch")
    for field in watchdog_fields - {"applicable_stage_d_hard_cap_profile_identity", "within_accepted_stage_d_profile"}:
        _positive_integer(watchdogs[field], f"attempt_watchdogs.{field}")
    _validate_external_identity(
        watchdogs["applicable_stage_d_hard_cap_profile_identity"],
        "attempt_watchdogs.applicable_stage_d_hard_cap_profile_identity",
    )
    if watchdogs["within_accepted_stage_d_profile"] is not True:
        raise BindingRefusal("attempt watchdogs exceed the accepted Stage D profile")
    budget = record["campaign_budget"]
    budget_fields = {
        "maximum_attempt_count", "maximum_cumulative_active_wall_time_nanoseconds",
        "maximum_cumulative_primary_evaluations", "maximum_cumulative_physical_trace_bytes_written",
        "maximum_cumulative_physical_output_bytes_written", "maximum_durable_logical_trace_bytes",
        "maximum_durable_logical_output_bytes", "maximum_process_tree_peak_resident_memory_bytes",
        "maximum_campaign_calendar_duration_seconds", "study_specific_dimensions",
        "stage_e_feasibility_evidence_identities", "independent_audit_identity",
        "post_start_change_permitted",
    }
    if not isinstance(budget, Mapping) or set(budget) != budget_fields:
        raise BindingRefusal("campaign budget field closure mismatch")
    for field in budget_fields - {
        "study_specific_dimensions", "stage_e_feasibility_evidence_identities",
        "independent_audit_identity", "post_start_change_permitted",
    }:
        _positive_integer(budget[field], f"campaign_budget.{field}")
    if budget["post_start_change_permitted"] is not False:
        raise BindingRefusal("campaign budget permits a post-start change")
    _validate_external_identity(budget["independent_audit_identity"], "campaign_budget.independent_audit_identity")
    evidence = budget["stage_e_feasibility_evidence_identities"]
    if not isinstance(evidence, list) or not evidence:
        raise BindingRefusal("campaign budget lacks Stage E feasibility evidence")
    for index, identity in enumerate(evidence):
        _validate_external_identity(identity, f"campaign_budget.stage_e_feasibility[{index}]")
    dimensions = budget["study_specific_dimensions"]
    if not isinstance(dimensions, list) or not dimensions:
        raise BindingRefusal("campaign budget lacks study-specific dimensions")
    for index, dimension in enumerate(dimensions):
        if not isinstance(dimension, Mapping) or set(dimension) != {"name", "value", "unit", "non_sliceable"}:
            raise BindingRefusal(f"campaign budget dimension closure mismatch: {index}")
        if not isinstance(dimension["name"], str) or not dimension["name"] or not isinstance(dimension["unit"], str) or not dimension["unit"]:
            raise BindingRefusal(f"campaign budget dimension label is empty: {index}")
        if not _is_integer(dimension["value"]) or dimension["value"] < 0 or not isinstance(dimension["non_sliceable"], bool):
            raise BindingRefusal(f"campaign budget dimension type mismatch: {index}")
    digest = sha256_hex(canonical_bytes(_campaign_preimage(record)))
    if record["binding_sha256"] != digest:
        raise BindingRefusal("referenced campaign binding_sha256 mismatch")


def validate_route_portfolio(
    validator: ClosedSchemaValidator,
    route_bindings: Sequence[Mapping[str, Any]],
    *,
    referenced_bindings: Mapping[str, Mapping[str, Any]] | None = None,
    bundle: Mapping[str, Any] | None = None,
    public_host_binding: Mapping[str, Any] | None = None,
) -> None:
    if not isinstance(route_bindings, (list, tuple)) or len(route_bindings) != len(CAMPAIGN_ORDER):
        raise BindingRefusal("portfolio must contain exactly fifteen route bindings")
    for route in route_bindings:
        validator.validate_definition("route_binding", route)
    route_ids = tuple(route["route_id"] for route in route_bindings)
    if route_ids != CAMPAIGN_ORDER:
        raise BindingRefusal("route portfolio order differs from frozen campaign order")
    campaign_ids = [route["campaign_id"] for route in route_bindings]
    if len(campaign_ids) != len(set(campaign_ids)):
        raise BindingRefusal("route campaign IDs are not pairwise distinct")
    binding_identities: list[Mapping[str, Any]] = []
    file_identities: list[Mapping[str, Any]] = []
    for route in route_bindings:
        route_id = route["route_id"]
        expected_study = "SD-01" if route_id == "SD-01-GROWTH-v1" else route_id
        if route["study_id"] != expected_study:
            raise BindingRefusal(f"route-to-study mapping mismatch: {route_id}")
        if route_id == "SD-01-GROWTH-v1" and route["campaign_id"] != route_id:
            raise BindingRefusal("nested growth campaign ID is not the frozen nested ID")
        sealed = route["seal_status"] == "SEALED"
        binding_identity = route["campaign_execution_binding_identity"]
        file_identity = route["campaign_execution_binding_file_identity"]
        gaps = route["unresolved_authority_ids"]
        if sealed:
            if binding_identity is None or file_identity is None or gaps:
                raise BindingRefusal(f"sealed route has null identities or gaps: {route_id}")
            binding_identities.append(binding_identity)
            file_identities.append(file_identity)
        elif binding_identity is not None or file_identity is not None or not gaps:
            raise BindingRefusal(f"unsealed route does not have two null identities and gaps: {route_id}")
        if referenced_bindings is not None and sealed:
            reference = referenced_bindings.get(route_id)
            if not isinstance(reference, Mapping) or set(reference) != {"record", "file_bytes"}:
                raise BindingRefusal(f"missing closed referenced binding material: {route_id}")
            record = reference["record"]
            file_bytes = reference["file_bytes"]
            if not isinstance(record, Mapping) or not isinstance(file_bytes, bytes):
                raise BindingRefusal(f"malformed retained binding material: {route_id}")
            if file_bytes != canonical_bytes(record):
                raise BindingRefusal(
                    f"referenced campaign record/file bytes differ: {route_id}"
                )
            _validate_inherited_campaign_binding(record)
            verify_identity(file_identity, file_bytes, kind=IDENTITY_KINDS["campaign_binding_file"])
            verify_identity(binding_identity, _campaign_preimage(record), kind=IDENTITY_KINDS["campaign_binding"])
            if record["binding_sha256"] != binding_identity["value"]:
                raise BindingRefusal(f"referenced binding embedded digest mismatch: {route_id}")
            if record["campaign_id"] != route["campaign_id"] or record["study_id"] != route["study_id"]:
                raise BindingRefusal(f"wrapper/referenced campaign projection mismatch: {route_id}")
            if bundle is not None:
                for field in ("code_identity", "installed_artifact_identity"):
                    if not _same(record[field], bundle[field if field != "code_identity" else "scientific_code_identity"]):
                        raise BindingRefusal(f"referenced {field} differs from bundle: {route_id}")
            if public_host_binding is not None:
                links = {
                    "environment_identity": "environment_identity",
                    "parallelization_boundary_identity": "parallelization_boundary_identity",
                    "worker_allocation_policy_identity": "worker_allocation_policy_identity",
                    "storage_location_identity": "storage_location_identity",
                    "durability_policy_identity": "durability_policy_identity",
                    "restart_policy_identity": "restart_policy_identity",
                }
                for record_field, public_field in links.items():
                    if not _same(record[record_field], public_host_binding[public_field]):
                        raise BindingRefusal(f"referenced policy differs from public binding: {route_id}.{record_field}")
    _assert_distinct_identities(binding_identities, "campaign binding identity")
    _assert_distinct_identities(file_identities, "campaign binding file identity")


def validate_local_binding_bundle(
    validator: ClosedSchemaValidator,
    bundle: Mapping[str, Any],
    *,
    public_host_binding: Mapping[str, Any],
    referenced_bindings: Mapping[str, Mapping[str, Any]] | None = None,
) -> dict[str, str]:
    validator.validate_definition("local_binding_bundle", bundle)
    _validate_correction_context(validator, bundle)
    _require_same_v3_provenance(bundle, bundle, "local binding bundle")
    _zero(bundle)
    if not _same(bundle["accepted_base"], ACCEPTED_BASE):
        raise BindingRefusal("bundle accepted base mismatch")
    if (
        bundle["stage_e_ci_run_id"] != STAGE_E_CI_RUN_ID
        or bundle["stage_e_artifact_id"] != STAGE_E_ARTIFACT_ID
        or bundle["stage_e_artifact_sha256"] != STAGE_E_ARTIFACT_SHA256
    ):
        raise BindingRefusal("bundle Stage E exact-target evidence mismatch")
    _expect_identity(bundle["public_host_binding_identity"], public_host_binding, "bundle public host")
    validate_route_portfolio(
        validator,
        bundle["ordered_route_bindings"],
        referenced_bindings=referenced_bindings,
        bundle=bundle,
        public_host_binding=public_host_binding,
    )
    sealed_count = sum(row["seal_status"] == "SEALED" for row in bundle["ordered_route_bindings"])
    if bundle["disposition"] == "READY_FOR_INDEPENDENT_BINDING_AUDIT":
        if sealed_count != 15 or bundle["scientific_implementation_identity"] is None or bundle["verifier_identity"] is None:
            raise BindingRefusal("ready bundle lacks fifteen sealed routes or complete implementation identities")
    else:
        if sealed_count == 15:
            raise BindingRefusal("not-sealable bundle has a complete sealed route portfolio")
        if bundle["accepted_base"] == ACCEPTED_BASE:
            for row in bundle["ordered_route_bindings"]:
                if row["seal_status"] == "UNSEALED_AUTHORITY_GAP" and tuple(row["unresolved_authority_ids"]) != ACCEPTED_GAPS[row["route_id"]]:
                    raise BindingRefusal(f"accepted-base authority-gap registry mismatch: {row['route_id']}")
    return _record_identity(bundle)


def _snapshot_times(
    capacity_snapshot: Mapping[str, Any], power_snapshot: Mapping[str, Any]
) -> tuple[tuple[datetime, str], tuple[datetime, str]]:
    return (
        (_parse_utc(capacity_snapshot["snapshot_completed_utc"], "capacity completion"), "capacity completion"),
        (_parse_utc(power_snapshot["facts"]["snapshot_utc"], "power snapshot"), "power snapshot"),
    )


def _round_up(value: int, unit: int) -> int:
    return 0 if value == 0 else ((value + unit - 1) // unit) * unit


_PROHIBITED_FILE_ATTRIBUTE_MASK = (
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


def _inventory_category(relative_path: str) -> str:
    roots = (
        ("immutable-results/primary-logical-output", "PRIMARY_LOGICAL_OUTPUT"),
        ("independent-audit/complete-copy", "INDEPENDENT_AUDIT_COPY"),
        (
            "immutable-results/dynamic-growth-physical-writes",
            "DYNAMIC_GROWTH_PHYSICAL_WRITE",
        ),
        ("continuation-checkpoints", "CHECKPOINT_AND_WRITE_OVERHEAD"),
        ("temporary", "TEMPORARY_ARCHIVE"),
        ("independent-audit/retained-evidence", "RETAINED_EVIDENCE"),
    )
    if relative_path in {".", "immutable-results", "independent-audit"}:
        return "CHECKPOINT_AND_WRITE_OVERHEAD"
    for root, category in roots:
        if relative_path == root or relative_path.startswith(root + "/"):
            return category
    raise BindingRefusal(f"unclassified storage inventory path: {relative_path}")


def _validate_inventory_entry(
    entry: Mapping[str, Any],
    *,
    allocation_unit: int,
    file_record_bytes: int,
    volume_serial_number: int,
) -> None:
    path = entry["relative_path"]
    if path != ".":
        components = path.split("/")
        if (
            path != unicodedata.normalize("NFC", path)
            or "\\" in path
            or any(
                not component
                or component in {".", ".."}
                or ":" in component
                or component.endswith((".", " "))
                for component in components
            )
        ):
            raise BindingRefusal(f"storage inventory path is not a closed NFC relative path: {path}")
    if entry["storage_category"] != _inventory_category(path):
        raise BindingRefusal(f"storage inventory category differs: {path}")
    if (
        entry["file_id_volume_serial_number"] != volume_serial_number
        or entry["file_standard_number_of_links"] != entry["hard_link_count"]
        or entry["file_standard_delete_pending"]
        or entry["file_attribute_reparse_tag"] != 0
        or entry["raw_file_attributes"] & _PROHIBITED_FILE_ATTRIBUTE_MASK
        != entry["prohibited_file_attribute_bits_set"]
        or entry["prohibited_file_attribute_bits_set"] != 0
        or entry["reparse_point"]
        or entry["sparse"]
        or entry["compressed"]
    ):
        raise BindingRefusal(f"storage inventory handle facts differ or are prohibited: {path}")

    streams = entry["backup_streams"]
    if (
        entry["backup_stream_count"] != len(streams)
        or len({stream["stream_id_uint32"] for stream in streams}) != len(streams)
    ):
        raise BindingRefusal(f"backup-stream closure differs: {path}")
    non_data = [stream for stream in streams if stream["stream_id"] != "BACKUP_DATA"]
    non_data_bytes = sum(
        _round_up(stream["stream_size_bytes"], allocation_unit)
        for stream in non_data
    )
    non_data_clusters = sum(
        _round_up(stream["stream_size_bytes"], allocation_unit) // allocation_unit
        for stream in non_data
    )
    if (
        entry["permitted_non_data_backup_stream_count"] != len(non_data)
        or entry["permitted_non_data_backup_stream_accounted_bytes"] != non_data_bytes
        or entry["permitted_non_data_backup_stream_allocation_cluster_count"]
        != non_data_clusters
    ):
        raise BindingRefusal(f"backup-stream accounting differs: {path}")

    extents = entry["retrieval_extents"]
    if entry["retrieval_extent_count"] != len(extents):
        raise BindingRefusal(f"retrieval-extent count differs: {path}")
    if extents:
        if (
            entry["retrieval_pointer_initial_result"] != "EXTENTS_FOUND"
            or extents[0]["starting_vcn"] != 0
            or any(
                row["next_vcn"] <= row["starting_vcn"]
                or (index and row["starting_vcn"] != extents[index - 1]["next_vcn"])
                for index, row in enumerate(extents)
            )
            or extents[-1]["next_vcn"] * allocation_unit
            != entry["file_standard_allocation_size_bytes"]
        ):
            raise BindingRefusal(f"retrieval-extent allocation chain differs: {path}")
    elif (
        entry["retrieval_pointer_initial_result"] != "ERROR_HANDLE_EOF_RESIDENT"
        or entry["file_standard_allocation_size_bytes"] != 0
    ):
        raise BindingRefusal(f"resident retrieval-pointer evidence differs: {path}")

    entry_type = entry["entry_type"]
    if entry_type == "REGULAR_FILE":
        if (
            entry["file_standard_directory"]
            or entry["logical_bytes"] != entry["file_standard_end_of_file_bytes"]
            or len(entry["data_streams"]) != 1
            or entry["data_streams"][0]["stream_name"] != "::$DATA"
            or entry["data_streams"][0]["stream_size_bytes"] != entry["logical_bytes"]
        ):
            raise BindingRefusal(f"regular-file data-stream facts differ: {path}")
        data_streams = [stream for stream in streams if stream["stream_id"] == "BACKUP_DATA"]
        if len(data_streams) > 1 or any(
            stream["stream_size_bytes"] != entry["logical_bytes"]
            or stream["stream_content_sha256"] != entry["content_sha256"]
            for stream in data_streams
        ):
            raise BindingRefusal(f"regular-file BackupRead data differs: {path}")
        allocated = max(
            entry["logical_bytes"],
            entry["get_compressed_file_size_bytes"],
            entry["file_standard_allocation_size_bytes"],
        ) + non_data_bytes
        bitmap_clusters = 0
        bitmap_bytes = 0
    else:
        if (
            not entry["file_standard_directory"]
            or entry["logical_bytes"] != 0
            or entry["file_standard_end_of_file_bytes"] != 0
            or entry["data_streams"]
            or any(stream["stream_id"] == "BACKUP_DATA" for stream in streams)
        ):
            raise BindingRefusal(f"directory stream facts differ: {path}")
        raw_bitmap_bytes = (
            entry["file_standard_allocation_size_bytes"] + 32768 - 1
        ) // 32768
        bitmap_bytes = _round_up(raw_bitmap_bytes, allocation_unit)
        bitmap_clusters = bitmap_bytes // allocation_unit
        allocated = (
            entry["file_standard_allocation_size_bytes"]
            + bitmap_bytes
            + non_data_bytes
        )
    if (
        entry["directory_bitmap_allocation_cluster_count"] != bitmap_clusters
        or entry["directory_bitmap_upper_bound_bytes"] != bitmap_bytes
    ):
        raise BindingRefusal(f"directory-bitmap accounting differs: {path}")
    metadata = _round_up(
        (
            1
            + len(extents)
            + bitmap_clusters
            + non_data_clusters
        )
        * file_record_bytes,
        allocation_unit,
    )
    if (
        entry["metadata_record_upper_bound_bytes"] != metadata
        or entry["allocated_bytes"] != allocated
        or entry["accounted_bytes"] != allocated + metadata
    ):
        raise BindingRefusal(f"storage entry allocation/accounting differs: {path}")


def _validate_capacity_history(
    validator: ClosedSchemaValidator,
    history: Sequence[Mapping[str, Any]],
    private_manifest: Mapping[str, Any],
    public_host_binding: Mapping[str, Any],
) -> Mapping[str, Any]:
    if not isinstance(history, (list, tuple)) or not history:
        raise BindingRefusal("capacity history is empty")
    filesystem = private_manifest["filesystem"]
    previous: Mapping[str, Any] | None = None
    identities: set[tuple[str, str]] = set()
    required_roots = {
        ".",
        "immutable-results",
        "continuation-checkpoints",
        "independent-audit",
        "temporary",
        "immutable-results/primary-logical-output",
        "independent-audit/complete-copy",
        "immutable-results/dynamic-growth-physical-writes",
        "independent-audit/retained-evidence",
    }
    for ordinal, snapshot in enumerate(history):
        validator.validate_definition("storage_capacity_snapshot", snapshot)
        _validate_correction_context(validator, snapshot)
        _zero(snapshot)
        identity = _record_identity(snapshot)
        identity_key = (identity["kind"], identity["value"])
        if identity_key in identities:
            raise BindingRefusal("capacity history repeats a snapshot identity")
        identities.add(identity_key)
        stable_fields = (
            "volume_measurement_apis",
            "selected_volume_guid_path",
            "resolved_private_path_volume_guids",
            "volume_serial_number",
            "maximum_component_length",
            "filesystem_flags",
            "sectors_per_cluster",
            "bytes_per_sector",
            "volume_allocation_unit_bytes",
            "reserved_envelope_bytes",
        )
        if any(snapshot[field] != filesystem[field] for field in stable_fields):
            raise BindingRefusal(f"capacity snapshot {ordinal} differs from filesystem facts")
        if not _same(snapshot["filesystem_identity"], filesystem["filesystem_identity"]):
            raise BindingRefusal(f"capacity snapshot {ordinal} names another filesystem")
        if not _same(
            snapshot["storage_inventory_policy_identity"],
            public_host_binding["storage_inventory_policy_identity"],
        ):
            raise BindingRefusal(f"capacity snapshot {ordinal} names another inventory policy")
        started = _parse_utc(snapshot["snapshot_started_utc"], "capacity start")
        completed = _parse_utc(snapshot["snapshot_completed_utc"], "capacity completion")
        cutoff = _parse_utc(snapshot["inventory_cutoff_utc"], "capacity inventory cutoff")
        if started > cutoff or cutoff > completed:
            raise BindingRefusal("capacity snapshot timestamps run backwards")
        if previous is not None and _parse_utc(
            previous["snapshot_completed_utc"], "previous capacity completion"
        ) > started:
            raise BindingRefusal("capacity snapshots overlap or run backwards")
        allocation_unit = snapshot["sectors_per_cluster"] * snapshot["bytes_per_sector"]
        ntfs = snapshot["ntfs_volume_data"]
        if (
            snapshot["volume_allocation_unit_bytes"] != allocation_unit
            or ntfs["bytes_per_cluster"] != allocation_unit
            or ntfs["bytes_per_sector"] != snapshot["bytes_per_sector"]
            or snapshot["get_disk_free_space_free_clusters"] != ntfs["free_clusters"]
            or snapshot["get_disk_free_space_total_clusters"] != ntfs["total_clusters"]
            or ntfs["number_sectors"]
            != ntfs["total_clusters"] * snapshot["sectors_per_cluster"]
            or ntfs["free_clusters"] > ntfs["total_clusters"]
            or ntfs["total_reserved_clusters"] > ntfs["total_clusters"]
            or ntfs["mft_start_lcn"] >= ntfs["total_clusters"]
            or ntfs["mft2_start_lcn"] >= ntfs["total_clusters"]
            or ntfs["mft_zone_start"] > ntfs["mft_zone_end"]
            or ntfs["mft_zone_end"] > ntfs["total_clusters"]
            or ntfs["mft_valid_data_length"]
            > ntfs["total_clusters"] * allocation_unit
            or any(
                ntfs[field] != filesystem["ntfs_volume_data"][field]
                for field in (
                    "volume_serial_number",
                    "bytes_per_sector",
                    "bytes_per_cluster",
                    "bytes_per_file_record_segment",
                    "clusters_per_file_record_segment",
                    "mft_start_lcn",
                    "mft2_start_lcn",
                )
            )
        ):
            raise BindingRefusal("capacity volume geometry differs")
        if snapshot["observed_capacity_bytes"] != snapshot["get_disk_free_space_ex_total_caller_bytes"]:
            raise BindingRefusal("observed capacity formula mismatch")
        expected_free = min(
            snapshot["get_disk_free_space_ex_available_to_caller_bytes"],
            snapshot["get_disk_free_space_ex_total_free_bytes"],
        )
        if snapshot["observed_free_bytes"] != expected_free:
            raise BindingRefusal("observed free-space formula mismatch")
        entries = snapshot["inventory_entries"]
        paths = [entry["relative_path"] for entry in entries]
        if (
            paths != [unicodedata.normalize("NFC", value) for value in paths]
            or paths != sorted(paths, key=lambda value: value.encode("utf-8"))
            or len(paths) != len(set(paths))
            or not required_roots.issubset(paths)
        ):
            raise BindingRefusal("storage inventory path/root closure differs")
        for entry in entries:
            _validate_inventory_entry(
                entry,
                allocation_unit=allocation_unit,
                file_record_bytes=ntfs["bytes_per_file_record_segment"],
                volume_serial_number=ntfs["volume_serial_number"],
            )
        by_category = {
            category: sum(
                entry["accounted_bytes"]
                for entry in entries
                if entry["storage_category"] == category
            )
            for category in (
                "PRIMARY_LOGICAL_OUTPUT",
                "INDEPENDENT_AUDIT_COPY",
                "DYNAMIC_GROWTH_PHYSICAL_WRITE",
                "CHECKPOINT_AND_WRITE_OVERHEAD",
                "TEMPORARY_ARCHIVE",
                "RETAINED_EVIDENCE",
            )
        }
        usage = snapshot["current_envelope_usage"]
        expected_usage = {
            "primary_logical_output_bytes": by_category["PRIMARY_LOGICAL_OUTPUT"],
            "independent_audit_copy_bytes": by_category["INDEPENDENT_AUDIT_COPY"],
            "dynamic_growth_physical_write_bytes": by_category[
                "DYNAMIC_GROWTH_PHYSICAL_WRITE"
            ],
            "checkpoint_and_write_overhead_bytes": by_category[
                "CHECKPOINT_AND_WRITE_OVERHEAD"
            ],
            "temporary_archive_bytes": by_category["TEMPORARY_ARCHIVE"],
            "retained_evidence_bytes": 8589934592,
        }
        if any(usage[field] != value for field, value in expected_usage.items()):
            raise BindingRefusal("storage component usage does not reconstruct from inventory")
        ceilings = {
            "primary_logical_output_bytes": 253 * 1073741824,
            "independent_audit_copy_bytes": 253 * 1073741824,
            "dynamic_growth_physical_write_bytes": 80 * 1073741824,
            "checkpoint_and_write_overhead_bytes": 64 * 1073741824,
            "temporary_archive_bytes": 8 * 1073741824,
            "retained_evidence_bytes": 8 * 1073741824,
        }
        if any(usage[field] > ceiling for field, ceiling in ceilings.items()):
            raise BindingRefusal("storage component exceeds its frozen ceiling")
        retained_prewrite_allocated = sum(
            entry["allocated_bytes"]
            for entry in entries
            if entry["storage_category"] == "RETAINED_EVIDENCE"
        )
        retained_prepublication_allocated = snapshot[
            "retained_evidence_prepublication_allocated_bytes_at_cutoff"
        ]
        if (
            retained_prepublication_allocated != retained_prewrite_allocated
            or retained_prepublication_allocated > 8 * 1073741824
        ):
            raise BindingRefusal(
                "retained-evidence prepublication allocation does not equal the cutoff "
                "inventory or exceeds the frozen predebit"
            )
        components = tuple(expected_usage)
        total = sum(usage[field] for field in components)
        if usage["total_envelope_usage_bytes"] != total:
            raise BindingRefusal("storage envelope component sum mismatch")
        remaining = snapshot["reserved_envelope_bytes"] - total
        if remaining < 0 or snapshot["remaining_reserved_envelope_bytes"] != remaining:
            raise BindingRefusal("remaining storage envelope formula mismatch")
        if snapshot["observed_free_bytes"] < max(350 * 1073741824, remaining):
            raise BindingRefusal("selected volume fails the current free-space rule")
        if previous is None:
            if snapshot["previous_snapshot_identity"] is not None or any(
                entry["entry_type"] == "REGULAR_FILE"
                and entry["storage_category"] != "RETAINED_EVIDENCE"
                for entry in entries
            ):
                raise BindingRefusal("null predecessor is not an empty migration snapshot")
            if not _same(
                private_manifest["initial_storage_capacity_snapshot_identity"],
                identity,
            ):
                raise BindingRefusal("private manifest does not identify the migration snapshot")
        else:
            if not _same(snapshot["previous_snapshot_identity"], _record_identity(previous)):
                raise BindingRefusal("capacity predecessor identity chain differs")
            retained = {entry["relative_path"]: entry for entry in entries}
            for prior_entry in previous["inventory_entries"]:
                current_entry = retained.get(prior_entry["relative_path"])
                if current_entry is None:
                    raise BindingRefusal("capacity predecessor row was removed")
                if prior_entry["entry_type"] == "REGULAR_FILE":
                    if current_entry != prior_entry:
                        raise BindingRefusal(
                            "capacity predecessor non-metadata row was changed"
                    )
                    continue
                allocation_dependent_fields = {
                    "file_standard_allocation_size_bytes",
                    "retrieval_pointer_initial_result",
                    "retrieval_extents",
                    "retrieval_extent_count",
                    "metadata_record_upper_bound_bytes",
                    "directory_bitmap_allocation_cluster_count",
                    "directory_bitmap_upper_bound_bytes",
                    "allocated_bytes",
                    "accounted_bytes",
                }
                if (
                    current_entry["entry_type"] != "DIRECTORY"
                    or {
                        key: value
                        for key, value in current_entry.items()
                        if key not in allocation_dependent_fields
                    }
                    != {
                        key: value
                        for key, value in prior_entry.items()
                        if key not in allocation_dependent_fields
                    }
                    or current_entry["file_standard_allocation_size_bytes"]
                    < prior_entry["file_standard_allocation_size_bytes"]
                    or current_entry["metadata_record_upper_bound_bytes"]
                    < prior_entry["metadata_record_upper_bound_bytes"]
                    or current_entry["allocated_bytes"]
                    < prior_entry["allocated_bytes"]
                    or current_entry["accounted_bytes"]
                    < prior_entry["accounted_bytes"]
                ):
                    raise BindingRefusal(
                        "capacity predecessor directory immutable facts or monotone allocation differ"
                    )
        previous = snapshot
    return history[-1]


def _validate_storage_and_power_links(
    validator: ClosedSchemaValidator,
    capacity_history: Sequence[Mapping[str, Any]],
    capacity_snapshot: Mapping[str, Any],
    power_snapshot: Mapping[str, Any],
    private_manifest: Mapping[str, Any],
    public_host_binding: Mapping[str, Any],
) -> None:
    filesystem = private_manifest["filesystem"]
    if _validate_capacity_history(
        validator, capacity_history, private_manifest, public_host_binding
    ) != capacity_snapshot:
        raise BindingRefusal("current capacity snapshot is not the final retained history row")
    _validate_correction_context(validator, power_snapshot)
    _expect_identity(power_snapshot["private_host_manifest_identity"], private_manifest, "power private host")


def _power_preconditions_pass(power_snapshot: Mapping[str, Any]) -> bool:
    facts = power_snapshot["facts"]
    return bool(
        power_snapshot["raw_host_prerequisites_complete"]
        and facts["get_system_power_status_returned_nonzero"]
        and facts["ac_line_status"] == 1
        and facts["power_get_active_scheme_result"] == 0
        and facts["plugged_in_standby_idle_seconds"] == 0
        and facts["power_read_ac_standby_result"] == 0
        and facts["power_read_ac_lid_result"] == 0
        and facts["plugged_in_lid_action"] in {"DO_NOTHING", "SLEEP"}
        and (
            facts["plugged_in_lid_action"] == "DO_NOTHING"
            or facts["lid_open_statement_identity"] is not None
        )
        and facts["docker_engine_observation"]["engine_response_succeeded"]
        and facts["docker_engine_observation"]["scientific_image_present"]
        and facts["pending_reboot_marker_count"] == 0
        and facts["no_auto_reboot_policy_value"] == 1
        and facts["controller_session_logged_on"]
        and facts["derived_power_fields_reconcile_raw_queries"]
    )


def validate_private_durability_bundle(
    validator: ClosedSchemaValidator,
    bundle: Mapping[str, Any],
    *,
    receipts: Sequence[Mapping[str, Any]],
    host_runtime_preimage: Mapping[str, Any],
    private_manifest: Mapping[str, Any],
    identity_preimages: Mapping[Any, Any],
) -> dict[str, str]:
    from .durability import validate_durability_receipt

    validator.validate_definition("private_durability_bundle", bundle)
    validator.validate_definition("host_validation_runtime_preimage", host_runtime_preimage)
    verify_identity(
        bundle["host_validation_runtime_identity"],
        host_runtime_preimage,
        kind=IDENTITY_KINDS["host_validation_runtime"],
    )
    _zero(bundle)
    if not isinstance(receipts, (list, tuple)) or not receipts:
        raise BindingRefusal("private durability bundle has no retained receipts")
    if (
        bundle["probe_receipt_count"] != len(receipts)
        or len(bundle["ordered_probe_receipt_identities"]) != len(receipts)
    ):
        raise BindingRefusal("private durability bundle receipt count differs")
    observed_identities: list[dict[str, str]] = []
    prior_challenge_counter = 0
    prior_probe_completed: datetime | None = None
    retained_control_paths: set[tuple[Any, Any]] = set()
    root_epoch_identity: Mapping[str, Any] | None = None
    link_fields = (
        "filesystem_identity",
        "durability_policy_identity",
        "restart_policy_identity",
        "binding_validator_identity",
        "execution_environment_policy_identity",
        "host_validation_runtime_identity",
    )
    for ordinal, receipt in enumerate(receipts):
        validator.validate_definition("durability_probe_receipt", receipt)
        _validate_correction_context(validator, receipt)
        if root_epoch_identity is None:
            root_epoch_identity = receipt["root_protection_epoch_identity"]
        elif not _same(root_epoch_identity, receipt["root_protection_epoch_identity"]):
            raise BindingRefusal("durability receipts cross root-protection epochs")
        validate_durability_private_paths(
            receipt,
            private_manifest=private_manifest,
            identity_preimages=identity_preimages,
        )
        validate_durability_receipt(
            receipt, host_runtime_preimage=host_runtime_preimage
        )
        _zero(receipt)
        if receipt["disposition"] != "STAGE_F_SYNTHETIC_DURABILITY_PASS":
            raise BindingRefusal(f"durability receipt {ordinal} is not PASS")
        for field in link_fields:
            if not _same(receipt[field], bundle[field]):
                raise BindingRefusal(
                    f"durability receipt {ordinal} differs from bundle: {field}"
                )
        restart = receipt["restart_observation"]
        if restart["ledger_predecessor_chain_verified"] is not True:
            raise BindingRefusal("durability restart lacks a verified ledger chain")
        for field in (
            "challenge_ledger_entry_identity",
            "acknowledgement_ledger_entry_identity",
        ):
            _require_identity_kind(
                restart[field], IDENTITY_KINDS["evidence_ledger"], f"restart.{field}"
            )
        if _same(
            restart["challenge_ledger_entry_identity"],
            restart["acknowledgement_ledger_entry_identity"],
        ):
            raise BindingRefusal("challenge and acknowledgement reuse one ledger entry")
        challenge_counter = restart["challenge_preimage"]["challenge_counter"]
        if challenge_counter <= prior_challenge_counter:
            raise BindingRefusal(
                f"durability receipt {ordinal} challenge counter is not a strict high-water mark"
            )
        probe_started = _parse_utc(
            receipt["probe_started_utc"], f"durability receipt {ordinal} start"
        )
        probe_completed = _parse_utc(
            receipt["probe_completed_utc"], f"durability receipt {ordinal} completion"
        )
        if prior_probe_completed is not None and probe_started < prior_probe_completed:
            raise BindingRefusal("ordered durability receipts overlap or run backwards")
        for path_field in ("challenge_path_identity", "acknowledgement_path_identity"):
            path_identity = restart[path_field]
            key = (path_identity["kind"], path_identity["value"])
            if key in retained_control_paths:
                raise BindingRefusal("durability receipts reuse a challenge/acknowledgement path")
            retained_control_paths.add(key)
        prior_challenge_counter = challenge_counter
        prior_probe_completed = probe_completed
        observed_identities.append(_record_identity(receipt))
    if not _same(bundle["ordered_probe_receipt_identities"], observed_identities):
        raise BindingRefusal("private durability bundle receipt identity order differs")
    if len({identity["value"] for identity in observed_identities}) != len(
        observed_identities
    ):
        raise BindingRefusal("private durability bundle repeats a receipt identity")
    return _record_identity(bundle)


def validate_binding_validation_receipt(
    validator: ClosedSchemaValidator,
    receipt: Mapping[str, Any],
    *,
    bundle: Mapping[str, Any],
    private_manifest: Mapping[str, Any],
    public_host_binding: Mapping[str, Any],
    capacity_snapshot: Mapping[str, Any],
    capacity_snapshot_history: Sequence[Mapping[str, Any]],
    power_snapshot: Mapping[str, Any],
    private_durability_bundle: Mapping[str, Any],
    durability_receipts: Sequence[Mapping[str, Any]],
    identity_preimages: Mapping[Any, Any],
) -> dict[str, str]:
    validator.validate_definition("binding_validation_receipt", receipt)
    _validate_correction_context(validator, receipt)
    _require_same_stable_correction_context(bundle, receipt, "bundle/validation")
    _require_same_v3_provenance(bundle, receipt, "bundle/validation")
    validator.validate_definition("storage_capacity_snapshot", capacity_snapshot)
    validator.validate_definition("power_snapshot", power_snapshot)
    _zero(receipt)
    _zero(capacity_snapshot)
    _zero(power_snapshot)
    _expect_identity(receipt["bundle_identity"], bundle, "validation bundle")
    _expect_identity(receipt["private_manifest_identity"], private_manifest, "validation private manifest")
    _expect_identity(receipt["public_host_binding_identity"], public_host_binding, "validation public host")
    _expect_identity(receipt["storage_capacity_snapshot_identity"], capacity_snapshot, "validation capacity")
    _expect_identity(receipt["power_snapshot_identity"], power_snapshot, "validation power")
    durability_bundle_identity = validate_private_durability_bundle(
        validator,
        private_durability_bundle,
        receipts=durability_receipts,
        host_runtime_preimage=private_manifest["host_validation_runtime_preimage"],
        private_manifest=private_manifest,
        identity_preimages=identity_preimages,
    )
    if not _same(
        durability_bundle_identity, private_manifest["durability_bundle_identity"]
    ) or not _same(
        durability_bundle_identity,
        public_host_binding["private_durability_bundle_identity"],
    ):
        raise BindingRefusal("validation durability bundle differs from private/public host")
    _validate_storage_and_power_links(
        validator,
        capacity_snapshot_history,
        capacity_snapshot,
        power_snapshot,
        private_manifest,
        public_host_binding,
    )
    if tuple(receipt["validated_route_order"]) != CAMPAIGN_ORDER:
        raise BindingRefusal("validation receipt route order mismatch")
    validated = (_parse_utc(receipt["validated_utc"], "validation"), "validation")
    for observed in _snapshot_times(capacity_snapshot, power_snapshot):
        _require_order(observed, validated)
    if not receipt["stage_e_guard_preserved"] and receipt["disposition"] != "STAGE_F_LOCAL_BINDING_VALIDATION_FAIL":
        raise BindingRefusal("Stage E guard failure is encoded as a non-failure disposition")
    if receipt["disposition"] == "STAGE_F_LOCAL_BINDING_VALIDATION_PASS":
        flags = (
            "identity_preimages_pass", "portfolio_projection_pass", "storage_preconditions_pass",
            "power_preconditions_pass", "durability_preconditions_pass",
            "private_public_digest_reconciled", "stage_e_guard_preserved",
        )
        if receipt["unresolved_authority_ids"] or not all(receipt[field] for field in flags):
            raise BindingRefusal("validation PASS has a failed check or unresolved authority")
        if bundle["disposition"] != "READY_FOR_INDEPENDENT_BINDING_AUDIT":
            raise BindingRefusal("validation PASS names a not-sealable bundle")
    if receipt["power_preconditions_pass"] != _power_preconditions_pass(power_snapshot):
        raise BindingRefusal("power-precondition boolean is not truthful")
    if receipt["disposition"] == "STAGE_F_LOCAL_BINDING_NOT_SEALABLE":
        if bundle["disposition"] != "BINDING_NOT_SEALABLE" or not receipt["unresolved_authority_ids"]:
            raise BindingRefusal("NOT_SEALABLE receipt lacks a matching gap-bearing bundle")
    if receipt["disposition"] == "STAGE_F_LOCAL_BINDING_VALIDATION_FAIL":
        flags = (
            "identity_preimages_pass",
            "portfolio_projection_pass",
            "storage_preconditions_pass",
            "power_preconditions_pass",
            "durability_preconditions_pass",
            "private_public_digest_reconciled",
            "stage_e_guard_preserved",
        )
        if not receipt["unresolved_authority_ids"] and all(
            receipt[field] for field in flags
        ):
            raise BindingRefusal("validation FAIL does not retain a failed check")
    return _record_identity(receipt)


def _project_bundle(readiness: Mapping[str, Any], bundle: Mapping[str, Any]) -> None:
    fields = (
        "public_host_binding_identity", "scientific_code_identity", "scientific_implementation_identity",
        "installed_artifact_identity", "verifier_identity", "binding_implementation_identity",
        "authority_set_identity", "stage_e_integration_identity", "stage_e_evidence_identity",
        "validator_identity",
    )
    for field in fields:
        if not _same(readiness[field], bundle[field]):
            raise BindingRefusal(f"readiness/bundle projection mismatch: {field}")
    if tuple(readiness["ordered_route_ids"]) != CAMPAIGN_ORDER:
        raise BindingRefusal("readiness route order mismatch")
    expected_bindings = [row["campaign_execution_binding_identity"] for row in bundle["ordered_route_bindings"]]
    if not _same(readiness["ordered_campaign_execution_binding_identities"], expected_bindings):
        raise BindingRefusal("readiness campaign-binding projection mismatch")


def validate_readiness_record(
    validator: ClosedSchemaValidator,
    readiness: Mapping[str, Any],
    *,
    bundle: Mapping[str, Any],
    validation_receipt: Mapping[str, Any],
    capacity_snapshot: Mapping[str, Any],
    power_snapshot: Mapping[str, Any],
    independent_audit: Mapping[str, Any] | None = None,
) -> dict[str, str]:
    validator.validate_definition("binding_readiness_record", readiness)
    _validate_correction_context(validator, readiness)
    _require_same_stable_correction_context(bundle, readiness, "bundle/readiness")
    _require_same_v3_provenance(bundle, readiness, "bundle/readiness")
    _require_same_stable_correction_context(
        validation_receipt, readiness, "validation/readiness"
    )
    _zero(readiness)
    _expect_identity(readiness["local_binding_bundle_identity"], bundle, "readiness bundle")
    _expect_identity(readiness["binding_validation_receipt_identity"], validation_receipt, "readiness validation")
    _expect_identity(readiness["storage_capacity_snapshot_identity"], capacity_snapshot, "readiness capacity")
    _expect_identity(readiness["power_snapshot_identity"], power_snapshot, "readiness power")
    _project_bundle(readiness, bundle)
    for field in ("storage_preconditions_pass", "power_preconditions_pass", "durability_preconditions_pass", "private_public_digest_reconciled"):
        if readiness[field] != validation_receipt[field]:
            raise BindingRefusal(f"readiness/validation projection mismatch: {field}")
    if readiness["unresolved_authority_ids"] != validation_receipt["unresolved_authority_ids"]:
        raise BindingRefusal("readiness/validation authority-gap mismatch")
    readiness_time = (_parse_utc(readiness["readiness_utc"], "readiness"), "readiness")
    validation_time = (_parse_utc(validation_receipt["validated_utc"], "validation"), "validation")
    _require_order(validation_time, readiness_time)
    for observed in _snapshot_times(capacity_snapshot, power_snapshot):
        _require_fresh(observed, readiness_time)
    disposition = readiness["disposition"]
    validation_disposition = validation_receipt["disposition"]
    if validation_disposition == "STAGE_F_LOCAL_BINDING_VALIDATION_FAIL":
        raise BindingRefusal("a failed validation receipt is terminal and cannot produce readiness")
    if disposition == "NOT_READY_AUTHORITY_GAPS":
        if validation_disposition != "STAGE_F_LOCAL_BINDING_NOT_SEALABLE":
            raise BindingRefusal("NOT_READY readiness does not consume NOT_SEALABLE validation")
        if bundle["disposition"] != "BINDING_NOT_SEALABLE" or not readiness["unresolved_authority_ids"]:
            raise BindingRefusal("NOT_READY readiness lacks a matching not-sealable gap chain")
        if readiness["independent_audit_identity"] is not None:
            raise BindingRefusal("NOT_READY readiness unexpectedly names an independent audit")
    elif disposition == "READY_FOR_INDEPENDENT_BINDING_AUDIT":
        if validation_disposition != "STAGE_F_LOCAL_BINDING_VALIDATION_PASS":
            raise BindingRefusal("READY readiness does not consume passing validation")
        if bundle["disposition"] != disposition or readiness["unresolved_authority_ids"]:
            raise BindingRefusal("pre-audit readiness lacks a complete ready bundle")
        if readiness["independent_audit_identity"] is not None:
            raise BindingRefusal("pre-audit readiness creates an audit identity cycle")
        if not all(readiness[field] for field in ("storage_preconditions_pass", "power_preconditions_pass", "durability_preconditions_pass", "private_public_digest_reconciled")):
            raise BindingRefusal("pre-audit readiness has a failed precondition")
    else:
        if validation_disposition != "STAGE_F_LOCAL_BINDING_VALIDATION_PASS":
            raise BindingRefusal("final readiness does not consume passing validation")
        if independent_audit is None:
            raise BindingRefusal("final readiness disposition lacks retained independent audit")
        _expect_identity(readiness["independent_audit_identity"], independent_audit, "final readiness audit")
        expected = "INDEPENDENT_BINDING_PASS" if disposition == "INDEPENDENT_BINDING_PASS" else "INDEPENDENT_BINDING_FAIL"
        if independent_audit["disposition"] != expected:
            raise BindingRefusal("final readiness/audit disposition mismatch")
        audit_time = (_parse_utc(independent_audit["audit_completed_utc"], "audit completion"), "audit completion")
        _require_order(audit_time, readiness_time)
    return _record_identity(readiness)


def validate_independent_audit_receipt(
    validator: ClosedSchemaValidator,
    audit: Mapping[str, Any],
    *,
    preaudit_readiness: Mapping[str, Any],
    bundle: Mapping[str, Any],
    validation_receipt: Mapping[str, Any],
    private_manifest: Mapping[str, Any],
    public_host_binding: Mapping[str, Any],
    capacity_snapshot: Mapping[str, Any],
    power_snapshot: Mapping[str, Any],
) -> dict[str, str]:
    validator.validate_definition("independent_binding_audit_receipt", audit)
    _validate_correction_context(validator, audit)
    _require_same_stable_correction_context(bundle, audit, "bundle/audit")
    _require_same_v3_provenance(bundle, audit, "bundle/audit")
    _zero(audit)
    if preaudit_readiness["disposition"] != "READY_FOR_INDEPENDENT_BINDING_AUDIT":
        raise BindingRefusal("audit does not name the pre-audit ready disposition")
    links = (
        (audit["audited_bundle_identity"], bundle, "audit bundle"),
        (audit["audited_ready_readiness_identity"], preaudit_readiness, "audit pre-readiness"),
        (audit["private_host_manifest_identity"], private_manifest, "audit private manifest"),
        (audit["public_host_binding_identity"], public_host_binding, "audit public host"),
        (audit["storage_capacity_snapshot_identity"], capacity_snapshot, "audit capacity"),
        (audit["power_snapshot_identity"], power_snapshot, "audit power"),
        (audit["binding_validation_receipt_identity"], validation_receipt, "audit validation"),
    )
    for identity, record, label in links:
        _expect_identity(identity, record, label)
    if audit["disposition"] == "INDEPENDENT_BINDING_PASS" and audit["issue_ids"]:
        raise BindingRefusal("independent PASS has issue IDs")
    if audit["disposition"] == "INDEPENDENT_BINDING_FAIL" and not audit["issue_ids"]:
        raise BindingRefusal("independent FAIL has no issue ID")
    ready_time = (_parse_utc(preaudit_readiness["readiness_utc"], "pre-audit readiness"), "pre-audit readiness")
    audit_time = (_parse_utc(audit["audit_completed_utc"], "audit completion"), "audit completion")
    _require_order(ready_time, audit_time)
    return _record_identity(audit)


def validate_sealed_campaign_packet(
    validator: ClosedSchemaValidator,
    packet: Mapping[str, Any],
    *,
    pass_readiness: Mapping[str, Any],
    audit: Mapping[str, Any],
    bundle: Mapping[str, Any],
    validation_receipt: Mapping[str, Any],
    private_manifest: Mapping[str, Any],
    public_host_binding: Mapping[str, Any],
    capacity_snapshot: Mapping[str, Any],
    power_snapshot: Mapping[str, Any],
) -> dict[str, str]:
    validator.validate_definition("sealed_campaign_packet_manifest", packet)
    _validate_correction_context(validator, packet)
    _require_same_stable_correction_context(bundle, packet, "bundle/packet")
    _require_same_v3_provenance(bundle, packet, "bundle/packet")
    _zero(packet)
    if pass_readiness["disposition"] != "INDEPENDENT_BINDING_PASS" or audit["disposition"] != "INDEPENDENT_BINDING_PASS":
        raise BindingRefusal("sealed packet lacks an independent PASS chain")
    links = (
        (packet["local_binding_bundle_identity"], bundle, "packet bundle"),
        (packet["independent_binding_pass_readiness_identity"], pass_readiness, "packet PASS readiness"),
        (packet["independent_binding_audit_identity"], audit, "packet audit"),
        (packet["binding_validation_receipt_identity"], validation_receipt, "packet validation"),
        (packet["public_host_binding_identity"], public_host_binding, "packet public host"),
        (packet["private_host_manifest_identity"], private_manifest, "packet private manifest"),
        (packet["storage_capacity_snapshot_identity"], capacity_snapshot, "packet capacity"),
        (packet["power_snapshot_identity"], power_snapshot, "packet power"),
    )
    for identity, record, label in links:
        _expect_identity(identity, record, label)
    fields = (
        "scientific_code_identity", "scientific_implementation_identity", "installed_artifact_identity",
        "verifier_identity", "binding_implementation_identity", "authority_set_identity",
        "stage_e_integration_identity", "stage_e_evidence_identity", "validator_identity",
    )
    for field in fields:
        if not _same(packet[field], bundle[field]) or not _same(packet[field], pass_readiness[field]):
            raise BindingRefusal(f"packet chain projection mismatch: {field}")
    if tuple(packet["ordered_route_ids"]) != CAMPAIGN_ORDER:
        raise BindingRefusal("packet route order mismatch")
    expected_bindings = [row["campaign_execution_binding_identity"] for row in bundle["ordered_route_bindings"]]
    if not _same(packet["ordered_campaign_execution_binding_identities"], expected_bindings):
        raise BindingRefusal("packet campaign-binding projection mismatch")
    _assert_distinct_identities(packet["ordered_campaign_execution_binding_identities"], "packet campaign binding")
    pass_time = (_parse_utc(pass_readiness["readiness_utc"], "final PASS readiness"), "final PASS readiness")
    packet_time = (_parse_utc(packet["packet_created_utc"], "packet creation"), "packet creation")
    _require_order(pass_time, packet_time)
    return sha256_identity(IDENTITY_KINDS["sealed_campaign_packet"], dict(packet))


def validate_post_packet_user_authorization_receipt(
    validator: ClosedSchemaValidator,
    receipt: Mapping[str, Any],
    *,
    packet: Mapping[str, Any],
    retained_statement_bytes: bytes,
) -> dict[str, str]:
    validator.validate_definition("post_packet_user_authorization_receipt", receipt)
    _validate_correction_context(validator, receipt)
    _require_same_stable_correction_context(packet, receipt, "packet/user receipt")
    _require_same_v3_provenance(packet, receipt, "packet/user receipt")
    _zero(receipt)
    _expect_identity(receipt["sealed_campaign_packet_identity"], packet, "user receipt packet")
    if not isinstance(retained_statement_bytes, bytes) or not retained_statement_bytes:
        raise BindingRefusal("explicit retained user statement bytes are missing")
    if receipt["statement_sha256"] != sha256_hex(retained_statement_bytes):
        raise BindingRefusal("retained explicit user statement digest mismatch")
    packet_time = (_parse_utc(packet["packet_created_utc"], "packet creation"), "packet creation")
    statement_time = (_parse_utc(receipt["statement_received_utc"], "user statement"), "user statement")
    _require_order(packet_time, statement_time)
    return _record_identity(receipt)


def _authorization_projection(authorization: Mapping[str, Any], packet: Mapping[str, Any]) -> None:
    packet_to_authorization = {
        "local_binding_bundle_identity": "sealed_binding_bundle_identity",
        "independent_binding_pass_readiness_identity": "independent_binding_pass_readiness_identity",
        "independent_binding_audit_identity": "independent_binding_audit_identity",
        "binding_validation_receipt_identity": "binding_validation_receipt_identity",
        "public_host_binding_identity": "public_host_binding_identity",
        "private_host_manifest_identity": "private_host_manifest_identity",
        "storage_capacity_snapshot_identity": "storage_capacity_snapshot_identity",
        "power_snapshot_identity": "power_snapshot_identity",
        "scientific_code_identity": "scientific_code_identity",
        "scientific_implementation_identity": "scientific_implementation_identity",
        "installed_artifact_identity": "installed_artifact_identity",
        "verifier_identity": "verifier_identity",
        "binding_implementation_identity": "binding_implementation_identity",
        "authority_set_identity": "authority_set_identity",
        "stage_e_integration_identity": "stage_e_integration_identity",
        "stage_e_evidence_identity": "stage_e_evidence_identity",
        "validator_identity": "validator_identity",
        "ordered_route_ids": "ordered_route_ids",
        "ordered_campaign_execution_binding_identities": "ordered_campaign_execution_binding_identities",
    }
    for packet_field, authorization_field in packet_to_authorization.items():
        if not _same(packet[packet_field], authorization[authorization_field]):
            raise BindingRefusal(f"authorization/packet projection mismatch: {authorization_field}")


def validate_campaign_authorization(
    validator: ClosedSchemaValidator,
    authorization: Mapping[str, Any],
    *,
    packet: Mapping[str, Any],
    user_receipt: Mapping[str, Any],
    pass_readiness: Mapping[str, Any],
    audit: Mapping[str, Any],
    preaudit_readiness: Mapping[str, Any],
    bundle: Mapping[str, Any],
    validation_receipt: Mapping[str, Any],
    private_manifest: Mapping[str, Any],
    public_host_binding: Mapping[str, Any],
    capacity_snapshot: Mapping[str, Any],
    capacity_snapshot_history: Sequence[Mapping[str, Any]],
    power_snapshot: Mapping[str, Any],
    retained_statement_bytes: bytes,
    identity_preimages: Mapping[Any, Any],
    referenced_bindings: Mapping[str, Mapping[str, Any]],
    private_durability_bundle: Mapping[str, Any],
    durability_receipts: Sequence[Mapping[str, Any]],
    repository: VerifiedGitRepository,
) -> dict[str, str]:
    validator.validate_definition("campaign_authorization", authorization)
    _validate_correction_context(validator, authorization)
    _require_same_stable_correction_context(
        packet, authorization, "packet/authorization"
    )
    _require_same_v3_provenance(packet, authorization, "packet/authorization")
    _zero(authorization)
    validate_public_host_binding(
        validator, public_host_binding, private_manifest=private_manifest
    )
    validate_local_binding_bundle(
        validator,
        bundle,
        public_host_binding=public_host_binding,
        referenced_bindings=referenced_bindings,
    )
    validate_immutable_bundle_chain(
        validator,
        bundle,
        public_host_binding=public_host_binding,
        identity_preimages=identity_preimages,
        referenced_bindings=referenced_bindings,
        repository=repository,
    )
    validate_binding_validation_receipt(
        validator,
        validation_receipt,
        bundle=bundle,
        private_manifest=private_manifest,
        public_host_binding=public_host_binding,
        capacity_snapshot=capacity_snapshot,
        capacity_snapshot_history=capacity_snapshot_history,
        power_snapshot=power_snapshot,
        private_durability_bundle=private_durability_bundle,
        durability_receipts=durability_receipts,
        identity_preimages=identity_preimages,
    )
    validate_readiness_record(
        validator,
        preaudit_readiness,
        bundle=bundle,
        validation_receipt=validation_receipt,
        capacity_snapshot=capacity_snapshot,
        power_snapshot=power_snapshot,
    )
    validate_independent_audit_receipt(
        validator,
        audit,
        preaudit_readiness=preaudit_readiness,
        bundle=bundle,
        validation_receipt=validation_receipt,
        private_manifest=private_manifest,
        public_host_binding=public_host_binding,
        capacity_snapshot=capacity_snapshot,
        power_snapshot=power_snapshot,
    )
    validate_readiness_record(
        validator,
        pass_readiness,
        bundle=bundle,
        validation_receipt=validation_receipt,
        capacity_snapshot=capacity_snapshot,
        power_snapshot=power_snapshot,
        independent_audit=audit,
    )
    packet_identity = validate_sealed_campaign_packet(
        validator,
        packet,
        pass_readiness=pass_readiness,
        audit=audit,
        bundle=bundle,
        validation_receipt=validation_receipt,
        private_manifest=private_manifest,
        public_host_binding=public_host_binding,
        capacity_snapshot=capacity_snapshot,
        power_snapshot=power_snapshot,
    )
    receipt_identity = validate_post_packet_user_authorization_receipt(
        validator, user_receipt, packet=packet, retained_statement_bytes=retained_statement_bytes
    )
    if not _same(authorization["sealed_campaign_packet_identity"], packet_identity):
        raise BindingRefusal("authorization sealed-packet identity mismatch")
    if not _same(authorization["post_packet_explicit_user_authorization_receipt_identity"], receipt_identity):
        raise BindingRefusal("authorization user-receipt identity mismatch")
    _authorization_projection(authorization, packet)
    if not _same(audit["audited_ready_readiness_identity"], _record_identity(preaudit_readiness)):
        raise BindingRefusal("authorization audit/pre-audit readiness chain mismatch")
    if not _same(pass_readiness["independent_audit_identity"], _record_identity(audit)):
        raise BindingRefusal("authorization PASS-readiness/audit chain mismatch")
    authorization_time = (_parse_utc(authorization["authorization_utc"], "authorization"), "authorization")
    statement_time = (_parse_utc(user_receipt["statement_received_utc"], "user statement"), "user statement")
    _require_order(statement_time, authorization_time)
    validation_time = (_parse_utc(validation_receipt["validated_utc"], "validation"), "validation")
    _require_fresh(validation_time, authorization_time)
    for observed in _snapshot_times(capacity_snapshot, power_snapshot):
        _require_fresh(observed, authorization_time)
    return _record_identity(authorization)


def assert_preimport_authorized(
    validator: ClosedSchemaValidator,
    authorization: Mapping[str, Any],
    *,
    packet: Mapping[str, Any],
    user_receipt: Mapping[str, Any],
    pass_readiness: Mapping[str, Any],
    audit: Mapping[str, Any],
    preaudit_readiness: Mapping[str, Any],
    bundle: Mapping[str, Any],
    validation_receipt: Mapping[str, Any],
    private_manifest: Mapping[str, Any],
    public_host_binding: Mapping[str, Any],
    capacity_snapshot: Mapping[str, Any],
    capacity_snapshot_history: Sequence[Mapping[str, Any]],
    power_snapshot: Mapping[str, Any],
    retained_statement_bytes: bytes,
    identity_preimages: Mapping[Any, Any],
    referenced_bindings: Mapping[str, Mapping[str, Any]],
    private_durability_bundle: Mapping[str, Any],
    durability_receipts: Sequence[Mapping[str, Any]],
    repository: VerifiedGitRepository,
) -> dict[str, str]:
    """Refuse unsafe in-process use; the full locked record-chain CLI is the gate."""

    raise BindingRefusal(
        "in-process pre-import authorization is forbidden; execute the exact locked "
        "validator record-chain with the complete authorization chain immediately "
        "before the external scientific launch"
    )


__all__ = (
    "ACCEPTED_BASE",
    "ACCEPTED_GAPS",
    "AUTHORITY_PATHS",
    "BINDING_FOUNDATION_BASE_COMMIT",
    "BINDING_FOUNDATION_BASE_TREE",
    "CAMPAIGN_ORDER",
    "ClosedSchemaValidator",
    "CORRECTION_AUTHORITY_CANDIDATE_COMMIT",
    "CORRECTION_AUTHORITY_CANDIDATE_TREE",
    "CORRECTION_AUTHORITY_INTEGRATION_COMMIT",
    "CORRECTION_AUTHORITY_INTEGRATION_TREE",
    "CORRECTION_AUTHORITY_PATHS",
    "CORRECTION_REQUIRED_TARGET_COMMIT",
    "CORRECTION_REQUIRED_TARGET_TREE",
    "DESCENDANT_PATH_BASE_COMMIT",
    "DESCENDANT_PATH_BASE_TREE",
    "EMBEDDED_DIGEST_FIELDS",
    "EFFECTIVE_SCHEMA_ADDED_DEFINITIONS",
    "EFFECTIVE_SCHEMA_ADDED_DEFINITION_COUNT",
    "EFFECTIVE_SCHEMA_BYTE_COUNT",
    "EFFECTIVE_SCHEMA_CHANGED_DEFINITIONS",
    "EFFECTIVE_SCHEMA_CHANGED_DEFINITION_COUNT",
    "EFFECTIVE_SCHEMA_DEFINITION_COUNT",
    "EFFECTIVE_SCHEMA_GIT_OBJECT",
    "EFFECTIVE_SCHEMA_LOCAL_REFERENCE_COUNT",
    "EFFECTIVE_SCHEMA_PATH",
    "EFFECTIVE_SCHEMA_REMOVED_DEFINITION_COUNT",
    "EFFECTIVE_SCHEMA_ROOT_VARIANT_COUNT",
    "EFFECTIVE_SCHEMA_SHA256",
    "FINAL_AUTHORITY_CANDIDATE_COMMIT",
    "FINAL_AUTHORITY_CANDIDATE_TREE",
    "FINAL_AUTHORITY_INTEGRATION_COMMIT",
    "FINAL_AUTHORITY_INTEGRATION_TREE",
    "FINAL_AUTHORITY_PATHS",
    "FINAL_AUTHORITY_REQUIRED_TARGET_COMMIT",
    "FINAL_AUTHORITY_REQUIRED_TARGET_TREE",
    "FINAL_REACHABILITY_CANDIDATE_COMMIT",
    "FINAL_REACHABILITY_CANDIDATE_TREE",
    "FINAL_REACHABILITY_INTEGRATION_COMMIT",
    "FINAL_REACHABILITY_INTEGRATION_TREE",
    "IDENTITY_KINDS",
    "IMPLEMENTATION_PATHS",
    "MAXIMUM_SNAPSHOT_AGE_SECONDS",
    "NESTED_ONLY_DEFINITIONS",
    "ORIGINAL_AUTHORITY_PATHS",
    "PUBLIC_HOST_ALIAS",
    "REACHABILITY_CANDIDATE_COMMIT",
    "REACHABILITY_CANDIDATE_TREE",
    "REACHABILITY_INTEGRATION_COMMIT",
    "REACHABILITY_INTEGRATION_TREE",
    "REJECTED_FOUNDATION_COMMITS",
    "STAGE_E_ARTIFACT_ID",
    "STAGE_E_ARTIFACT_SHA256",
    "STAGE_E_CI_RUN_ID",
    "VALIDATOR_SOURCE_PATHS",
    "VALIDATOR_ZIPAPP_PATHS",
    "VerifiedGitRepository",
    "assert_preimport_authorized",
    "audit_effective_schema",
    "audit_schema",
    "validate_binding_validation_receipt",
    "validate_campaign_authorization",
    "validate_corrected_record",
    "validate_durability_private_paths",
    "validate_identity_preimage",
    "validate_immutable_bundle_chain",
    "validate_independent_audit_receipt",
    "validate_local_binding_bundle",
    "validate_post_packet_user_authorization_receipt",
    "validate_private_durability_bundle",
    "validate_private_host_manifest",
    "validate_public_host_binding",
    "validate_readiness_record",
    "validate_route_portfolio",
    "validate_sealed_campaign_packet",
    "verify_effective_schema_blob",
)
