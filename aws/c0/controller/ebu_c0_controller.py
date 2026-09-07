#!/usr/bin/python3
"""Fail-closed synthetic-only AWS-C0 instance controller.

The controller has two entry points. ``prepare-request-v4`` downloads exact
versions of launch-v5, live-packet-v5, and live-authorization-v5, and
creates a root-only local request plus a closed source-sidecar-v4. ``run``
revalidates those files, atomically claims the attempt in S3, verifies the
installed software and preloaded image, emits start-v6 before container start,
and relays only the synthetic worker's closed records to fresh versioned keys.

Only standard-library modules are imported. AWS CLI and Docker are fixed,
bounded process boundaries. There is no retry and no scientific entry point.
"""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import hashlib
import json
import os
import re
import selectors
import stat
import subprocess
import sys
import tempfile
import time
import unicodedata
import hmac
import http.client
import ssl
import urllib.parse
from pathlib import Path
from typing import Any


AUTHORITY_ID = "EBU-AWS-C0-UNATTENDED-SYNTHETIC-REHEARSAL-AUTHORITY-v1"
CORRECTION_ID = "EBU-AWS-C0-LIVE-PREPARATION-CHOREOGRAPHY-CORRECTION-AUTHORITY-v1"
CLOSURE_ID = "EBU-AWS-C0-COST-RUNTIME-RETRIEVAL-CLOSURE-CORRECTION-AUTHORITY-v1"
REGION = "us-east-1"
INSTANCE_ID = "i-048bac00bdb540a4e"
AWS = "/usr/local/bin/aws"
DOCKER = "/usr/bin/docker"
CONTROLLER = Path("/usr/local/libexec/ebu-c0/ebu_c0_controller.py")
UNIT = Path("/etc/systemd/system/ebu-c0@.service")
REQUESTS = Path("/var/lib/ebu-c0/requests")
ATTEMPTS = Path("/var/lib/ebu-c0/attempts")
STATUS = Path("/var/lib/ebu-c0/status")
MAX_OBJECT_BYTES = 4_194_304
SHA = re.compile(r"^[0-9a-f]{64}$")
VERSION = re.compile(r"^[A-Za-z0-9._+~=/:-]{1,1024}$")
BUCKET = re.compile(r"^(?=.{3,63}$)[a-z0-9][a-z0-9-]*[a-z0-9]$")
REHEARSAL = re.compile(r"^AWS-C0-[A-Z0-9-]{1,64}$")
ATTEMPT = re.compile(r"^ATTEMPT-[A-Z0-9-]{1,64}-(SUCCESS|FAIL-AFTER-CHECKPOINT|TIMEOUT)$")
PREFIX = re.compile(r"^rehearsal/aws-c0/AWS-C0-[A-Z0-9-]{1,64}/ATTEMPT-[A-Z0-9-]{1,64}-(SUCCESS|FAIL-AFTER-CHECKPOINT|TIMEOUT)/$")
EXECUTION_ARN = re.compile(r"^arn:aws:states:us-east-1:[0-9]{12}:execution:[A-Za-z0-9+=,.@_-]{1,80}:[A-Za-z0-9+=,.@_-]{1,80}$")
MODE_BY_SUFFIX = {
    "-SUCCESS": "SUCCESS",
    "-FAIL-AFTER-CHECKPOINT": "FAIL_AFTER_CHECKPOINT",
    "-TIMEOUT": "TIMEOUT",
}
ZERO = {
    "project_runner_import_count": 0,
    "ebu_framework_import_count": 0,
    "stage_e_harness_import_count": 0,
    "registered_configuration_count": 0,
    "model_state_advance_count": 0,
    "trajectory_count": 0,
    "simulation_or_gate_count": 0,
    "scientific_rng_draw_count": 0,
    "outcome_inspection_count": 0,
    "scientific_output_count": 0,
}
FORBIDDEN_FIELDS = {
    "scientific_configuration", "model", "trajectory", "scientific_seed",
    "scientific_rng_stream", "candidate_outcome", "scientific_result",
    "scientific_claim", "figure", "interpretation", "publication",
}
LAUNCH_REQUIRED = {
    "schema", "authority_id", "correction_authority_id", "closure_correction_authority_id", "record_class",
    "scientific_execution_authorized", "stage_f_execution_authorized",
    "stage_f_readiness_claimed", "zero_science_counters", "observed_utc",
    "record_sha256", "rehearsal_id", "attempt_id", "attempt_identity", "region",
    "instance_id", "required_initial_instance_state", "artifact_prefix",
    "preparation_packet_identity", "preparation_packet_object",
    "preparation_authorization_identity", "preparation_authorization_object",
    "authority_audit_identity", "authority_audit_object", "static_validation_identity",
    "static_validation_object", "private_infrastructure_snapshot_identity",
    "private_infrastructure_snapshot_object", "cost_model_identity", "cost_model_object",
    "closure_seed_identity", "closure_seed_object", "artifact_version_receipts",
    "attempt_deadline_utc", "cleanup_deadline_utc", "phase_timeouts_seconds",
    "deployed_lambda_timeout_seconds", "state_machine_timeout_seconds", "iam_pagination_bounds",
    "heartbeat_interval_seconds", "checkpoint_interval_seconds", "cost_envelope",
    "retry_attempts", "cleanup_path",
    "material_correction_authority_id",
}
RUNTIME_POLICY = {
    "schema": "aws_c0_container_runtime_policy/v1",
    "network_mode": "none", "read_only_root": True,
    "no_new_privileges": True, "privileged": False, "cap_drop": ["ALL"],
    "user": "65534:65534", "pids_limit": 64,
    "memory_bytes": 268_435_456, "cpu_quota_nano_cpus": 1_000_000_000,
    "tmpfs_bytes": 16_777_216,
}
IMDS_TOKEN_TTL_SECONDS = 21600
IMDS_BASE = "http://169.254.169.254/latest"
SEMANTIC21 = ("artifact_bucket", "artifact_prefix", "launch_key", "launch_version_id", "launch_sha256", "launch_bytes",
              "live_packet_key", "live_packet_version_id", "live_packet_sha256", "live_packet_bytes",
              "live_authorization_key", "live_authorization_version_id", "live_authorization_sha256",
              "live_authorization_bytes", "rehearsal_id", "attempt_id", "region", "workflow_execution_arn",
              "ssm_client_request_token", "ssm_expected_command_not_before_utc", "ssm_expected_command_not_after_utc")
TRANSPORT2 = ("ssm_dispatch_request_canonical_json_base64", "ssm_dispatch_request_sha256")
SSM_SEMANTIC_NAMES = (
    "ArtifactBucket", "ArtifactPrefix", "LaunchRequestKey", "LaunchRequestVersionId", "LaunchRequestSha256", "LaunchRequestBytes",
    "LivePacketKey", "LivePacketVersionId", "LivePacketSha256", "LivePacketBytes",
    "LiveAuthorizationKey", "LiveAuthorizationVersionId", "LiveAuthorizationSha256", "LiveAuthorizationBytes",
    "RehearsalId", "AttemptId", "Region", "WorkflowExecutionArn", "SsmClientRequestToken",
    "SsmExpectedCommandNotBeforeUtc", "SsmExpectedCommandNotAfterUtc")
CONTROLLER_JOURNAL_SUFFIX = "evidence/controller-capture-journal.json"
CONTROLLER_JOURNAL_HANDOFF_SUFFIX = "evidence/controller-capture-journal-handoff.json"
HANDOFF_HASH_DOMAIN = "AWS_C0_CONTROLLER_JOURNAL_HANDOFF_V1_BODY_NUL"
HANDOFF_EXCLUDED_FIELDS = (
    "handoff_identity", "handoff_canonical_sha256",
    "handoff_canonical_body_byte_count", "handoff_body_excluded_fields_in_order",
    "handoff_body_projection_disposition",
)
PLATFORM_SMOKE_CAPSULE_ID = "platform-smoke-known-case-v1"
PLATFORM_SMOKE_COMMON_RECEIPT_FIELDS = (
    "schema", "capsule_id", "attempt_identity", "sequence", "event_type",
    "payload_identity", "previous_receipt_sha256", "receipt_sha256",
)
PLATFORM_SMOKE_FOUNDATION_CAPABILITIES = (
    "POST_TERMINAL_CONTROLLER_JOURNAL_SEAL",
    "EXACT_VERSION_STORAGE_AND_READBACK",
    "CONTROLLER_JOURNAL_VERSION_AND_TYPED_RECEIPT_HANDOFF",
    "SINGLE_ATTEMPT_NO_RETRY",
    "BOUNDED_STOP_AND_CLEANUP",
    "INTEGER_COST_CEILING",
    "ZERO_SCIENCE_GUARDS",
)
CONTROLLER_HANDOFF_COORDINATE_ROWS = (
    ("HANDOFF_ATTEMPT_PUBLICATION_001", "/attempt_identity/value", "/controller_publication_receipt/attempt_identity/value", "STRING_EQUAL"),
    ("HANDOFF_ATTEMPT_READBACK_002", "/attempt_identity/value", "/controller_readback_receipt/attempt_identity/value", "STRING_EQUAL"),
    ("HANDOFF_ROLE_PUBLICATION_003", "/controller_publication_receipt/journal_role", "CONTROLLER", "LITERAL_EQUAL"),
    ("HANDOFF_ROLE_READBACK_004", "/controller_readback_receipt/journal_role", "CONTROLLER", "LITERAL_EQUAL"),
    ("HANDOFF_BUCKET_PUBLICATION_005", "/controller_publication_receipt/bucket_name", "/controller_journal_object/bucket", "STRING_EQUAL"),
    ("HANDOFF_BUCKET_READBACK_006", "/controller_readback_receipt/bucket_name", "/controller_journal_object/bucket", "STRING_EQUAL"),
    ("HANDOFF_KEY_PUBLICATION_007", "/controller_publication_receipt/key", "/controller_journal_object/key", "STRING_EQUAL"),
    ("HANDOFF_KEY_READBACK_008", "/controller_readback_receipt/key", "/controller_journal_object/key", "STRING_EQUAL"),
    ("HANDOFF_VERSION_PUBLICATION_009", "/controller_publication_receipt/version_id", "/controller_journal_object/version_id", "STRING_EQUAL"),
    ("HANDOFF_VERSION_READBACK_010", "/controller_readback_receipt/version_id", "/controller_journal_object/version_id", "STRING_EQUAL"),
    ("HANDOFF_ETAG_PUBLICATION_011", "/controller_publication_receipt/etag", "/controller_journal_object/etag", "STRING_EQUAL"),
    ("HANDOFF_ETAG_READBACK_012", "/controller_readback_receipt/etag", "/controller_journal_object/etag", "STRING_EQUAL"),
    ("HANDOFF_CHECKSUM_PUBLICATION_013", "/controller_publication_receipt/checksum_sha256_base64", "/controller_journal_object/checksum_sha256_base64", "STRING_EQUAL"),
    ("HANDOFF_CHECKSUM_READBACK_014", "/controller_readback_receipt/checksum_sha256_base64", "/controller_journal_object/checksum_sha256_base64", "STRING_EQUAL"),
    ("HANDOFF_BYTES_PUBLICATION_015", "/controller_publication_receipt/byte_count", "/controller_journal_object/byte_count", "INTEGER_EQUAL"),
    ("HANDOFF_BYTES_READBACK_016", "/controller_readback_receipt/byte_count", "/controller_journal_object/byte_count", "INTEGER_EQUAL"),
    ("HANDOFF_OBJECT_SHA_PUBLICATION_017", "/controller_publication_receipt/published_object_sha256", "/controller_journal_object/object_sha256", "SHA256_EQUAL"),
    ("HANDOFF_OBJECT_SHA_READBACK_018", "/controller_readback_receipt/published_object_sha256", "/controller_journal_object/object_sha256", "SHA256_EQUAL"),
    ("HANDOFF_CHAIN_PUBLICATION_019", "/controller_publication_receipt/content_chain_sha256", "/controller_journal_object/content_chain_sha256", "SHA256_EQUAL"),
    ("HANDOFF_CHAIN_READBACK_020", "/controller_readback_receipt/content_chain_sha256", "/controller_journal_object/content_chain_sha256", "SHA256_EQUAL"),
    ("HANDOFF_PUBLICATION_IDENTITY_021", "/controller_publication_receipt_identity/sha256,/controller_publication_receipt_identity/value", "/controller_publication_receipt/receipt_sha256", "BOTH_SHA256_EQUAL"),
    ("HANDOFF_READBACK_IDENTITY_022", "/controller_readback_receipt_identity/sha256,/controller_readback_receipt_identity/value", "/controller_readback_receipt/receipt_sha256", "BOTH_SHA256_EQUAL"),
)


class Refusal(RuntimeError):
    """Closed control-plane refusal."""


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise Refusal(f"duplicate JSON key: {key}")
        out[key] = value
    return out


def strict_json(raw: bytes) -> Any:
    if len(raw) > MAX_OBJECT_BYTES or raw.endswith(b"\n") or raw.endswith(b"\r"):
        raise Refusal("object size/no-final-LF rule failed")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise Refusal("object is not UTF-8") from exc
    if unicodedata.normalize("NFC", text) != text:
        raise Refusal("object is not NFC")
    try:
        value = json.loads(text, object_pairs_hook=_pairs,
                           parse_float=lambda _: (_ for _ in ()).throw(Refusal("floats forbidden")),
                           parse_constant=lambda _: (_ for _ in ()).throw(Refusal("nonfinite forbidden")))
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise Refusal("invalid JSON") from exc
    if canonical_bytes(value) != raw:
        raise Refusal("object is not canonical JSON")
    return value


def canonical_bytes(value: Any) -> bytes:
    def walk(item: Any) -> None:
        if item is None or isinstance(item, (str, bool)):
            return
        if isinstance(item, int) and not isinstance(item, bool):
            return
        if isinstance(item, list):
            for child in item:
                walk(child)
            return
        if isinstance(item, dict) and all(isinstance(k, str) for k in item):
            for key, child in item.items():
                if unicodedata.normalize("NFC", key) != key:
                    raise Refusal("non-NFC key")
                walk(child)
            return
        raise Refusal("unsupported canonical JSON value")
    walk(value)
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode()


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def identity(kind: str, value: str) -> dict[str, str]:
    if not SHA.fullmatch(value):
        raise Refusal("invalid identity digest")
    return {"kind": kind, "sha256": value, "value": value}


def root_digest(record: dict[str, Any]) -> str:
    if not SHA.fullmatch(str(record.get("record_sha256", ""))):
        raise Refusal("missing root digest")
    preimage = dict(record)
    claimed = preimage.pop("record_sha256")
    actual = digest(canonical_bytes(preimage))
    if claimed != actual:
        raise Refusal("root preimage digest mismatch")
    return actual


def _no_forbidden(value: Any) -> None:
    if isinstance(value, dict):
        bad = FORBIDDEN_FIELDS.intersection(value)
        if bad:
            raise Refusal(f"forbidden field: {sorted(bad)[0]}")
        for child in value.values():
            _no_forbidden(child)
    elif isinstance(value, list):
        for child in value:
            _no_forbidden(child)


def _utc(value: Any) -> dt.datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise Refusal("UTC timestamp required")
    try:
        parsed = dt.datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise Refusal("invalid UTC timestamp") from exc
    if parsed.tzinfo != dt.timezone.utc:
        raise Refusal("timestamp must be UTC")
    return parsed


def _mode(attempt_id: str) -> str:
    matches = [mode for suffix, mode in MODE_BY_SUFFIX.items() if attempt_id.endswith(suffix)]
    if len(matches) != 1 or not ATTEMPT.fullmatch(attempt_id):
        raise Refusal("unsupported attempt suffix")
    return matches[0]


def ssm_semantic_parameters_from_argv(args: argparse.Namespace) -> dict[str, list[str]]:
    """The 21 semantic values come only from explicit argv, never a download."""
    try:
        values = {name: getattr(args, 'bucket' if name == 'artifact_bucket' else name) for name in SEMANTIC21}
    except AttributeError as exc:
        raise Refusal("all 21 explicit SSM semantic arguments required") from exc
    for name, value in values.items():
        if name.endswith('_bytes'):
            if type(value) is not int or not 1 <= value <= MAX_OBJECT_BYTES:
                raise Refusal("SSM source byte count outside bound")
        elif not isinstance(value, str) or not value:
            raise Refusal("SSM semantic string required")
    if values['region'] != REGION or not BUCKET.fullmatch(values['artifact_bucket']):
        raise Refusal("SSM region/bucket mismatch")
    if not REHEARSAL.fullmatch(values['rehearsal_id']) or not ATTEMPT.fullmatch(values['attempt_id']):
        raise Refusal("SSM attempt coordinate invalid")
    prefix = 'rehearsal/aws-c0/' + values['rehearsal_id'] + '/' + values['attempt_id'] + '/'
    if values['artifact_prefix'] != prefix:
        raise Refusal("SSM attempt prefix mismatch")
    for stem, suffix in (('launch', 'launch-request'), ('live_packet', 'live-packet'), ('live_authorization', 'live-authorization')):
        if (values[stem + '_key'] != prefix + suffix + '.json' or not VERSION.fullmatch(values[stem + '_version_id'])
                or not SHA.fullmatch(values[stem + '_sha256'])):
            raise Refusal("SSM exact source coordinate invalid")
    arn = values['workflow_execution_arn']
    if (not EXECUTION_ARN.fullmatch(arn) or not arn.startswith('arn:aws:states:us-east-1:623609441658:execution:')
            or not arn.endswith(':' + values['attempt_id'])):
        raise Refusal("SSM workflow coordinate mismatch")
    if not re.fullmatch(r'[A-Za-z0-9_-]{8,64}', values['ssm_client_request_token']):
        raise Refusal("SSM request token invalid")
    for field in ('ssm_expected_command_not_before_utc', 'ssm_expected_command_not_after_utc'):
        if not re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z', values[field]):
            raise Refusal("SSM exact second-resolution UTC timestamp required")
    if _utc(values['ssm_expected_command_not_before_utc']) >= _utc(values['ssm_expected_command_not_after_utc']):
        raise Refusal("SSM command time interval invalid")
    return {aws_name: [str(values[name])] for name, aws_name in zip(SEMANTIC21, SSM_SEMANTIC_NAMES)}


def validate_ssm_semantic_parameters(parameters: Any) -> dict[str, list[str]]:
    if not isinstance(parameters, dict) or set(parameters) != set(SSM_SEMANTIC_NAMES):
        raise Refusal("exact 21 SSM semantic parameter names required")
    arguments = {}
    for name, aws_name in zip(SEMANTIC21, SSM_SEMANTIC_NAMES):
        values = parameters[aws_name]
        if not isinstance(values, list) or len(values) != 1 or not isinstance(values[0], str) or not values[0]:
            raise Refusal("SSM parameters must be nonempty singleton string arrays")
        value = values[0]
        if name.endswith('_bytes'):
            if not re.fullmatch(r'[1-9][0-9]{0,18}', value):
                raise Refusal("SSM byte count must be a canonical positive integer string")
            value = int(value)
        arguments['bucket' if name == 'artifact_bucket' else name] = value
    if ssm_semantic_parameters_from_argv(argparse.Namespace(**arguments)) != parameters:
        raise Refusal("SSM semantic normalization mismatch")
    return parameters


def validate_ssm_dispatch_record_v2(record: Any, *, semantic_parameters: dict[str, list[str]]) -> dict[str, Any]:
    """Validate the complete accepted START envelope, not a bare scalar map."""
    required = {'schema', 'document_name', 'document_version', 'target_instance_id', 'attempt_identity', 'semantic_parameters'}
    if not isinstance(record, dict) or set(record) != required or record['schema'] != 'aws_c0_ssm_dispatch_request/v2':
        raise Refusal("closed full SSM dispatch/v2 envelope required")
    if (record['document_name'] != 'EBU-C0-Start-v1' or record['target_instance_id'] != INSTANCE_ID
            or not isinstance(record['document_version'], str) or not re.fullmatch(r'[1-9][0-9]{0,9}', record['document_version'])):
        raise Refusal("SSM exact document/version/instance mismatch")
    validate_ssm_semantic_parameters(semantic_parameters)
    _identity_field(record, 'attempt_identity', 'aws_c0_attempt/v1')
    if record['semantic_parameters'] != semantic_parameters:
        raise Refusal("SSM transport semantics differ from explicit argv")
    canonical_bytes(record)
    return record


def _decode_ssm_transport(args: argparse.Namespace) -> Any:
    """Bound encoded input before allocation; require one canonical transport."""
    encoded = getattr(args, 'ssm_dispatch_request_canonical_json_base64', None)
    claimed = getattr(args, 'ssm_dispatch_request_sha256', None)
    if (not isinstance(encoded, str) or not 1 <= len(encoded) <= 4*((16384+2)//3)
            or not isinstance(claimed, str) or not SHA.fullmatch(claimed)):
        raise Refusal("SSM transport pair derivation mismatch")
    try:
        decoded = base64.b64decode(encoded, validate=True)
    except (ValueError, TypeError) as exc:
        raise Refusal("SSM transport base64 invalid") from exc
    if (len(decoded) > 16384 or claimed != digest(decoded)
            or base64.b64encode(decoded).decode('ascii') != encoded):
        raise Refusal("SSM transport pair derivation mismatch")
    return strict_json(decoded)


def validate_ssm_dispatch_v2(args: argparse.Namespace) -> dict[str, Any]:
    """Verify semantic21 against the complete envelope and its transport2."""
    semantic = ssm_semantic_parameters_from_argv(args)
    return validate_ssm_dispatch_record_v2(_decode_ssm_transport(args), semantic_parameters=semantic)


def validate_local_helper_transport_v1(args: argparse.Namespace, *, expected_start_dispatch: dict[str, Any],
                                       attempt_deadline_utc: str, now: dt.datetime) -> dict[str, Any]:
    """Decode helper argv, but never obtain trusted START/deadline from it.

    The independently bound local-source loader is a required caller boundary.
    This routine performs no file, credential, network or command operation.
    """
    semantic = ssm_semantic_parameters_from_argv(args)
    return validate_local_helper_request_v1(_decode_ssm_transport(args), semantic_parameters=semantic,
        expected_start_dispatch=expected_start_dispatch, attempt_deadline_utc=attempt_deadline_utc, now=now)


def classify_local_dispatch(args: argparse.Namespace) -> str:
    """No-effect routing only; each destination must run its complete gate."""
    semantic=ssm_semantic_parameters_from_argv(args);record=_decode_ssm_transport(args)
    if isinstance(record,dict) and record.get('schema') == 'aws_c0_ssm_dispatch_request/v2':
        validate_ssm_dispatch_record_v2(record,semantic_parameters=semantic)
        return 'START'
    if (not isinstance(record,dict) or set(record) != {'schema','operation','start_dispatch_request','attempt_deadline_utc'}
            or record['schema'] != 'aws_c0_controller_local_helper_request/v1'
            or record['operation'] not in ('STATUS','SAFE_CLOSE')):
        raise Refusal('unknown local dispatch operation')
    validate_ssm_dispatch_record_v2(record['start_dispatch_request'],semantic_parameters=semantic)
    return record['operation']


def validate_local_helper_request_v1(record: Any, *, semantic_parameters: dict[str, list[str]],
                                     expected_start_dispatch: dict[str, Any], attempt_deadline_utc: str,
                                     now: dt.datetime) -> dict[str, Any]:
    """Pure helper-only validation; no preparation, credentials or execution.

    STATUS and SAFE_CLOSE inherit the exact already accepted START coordinates.
    The caller must obtain expected_start_dispatch and the deadline from the
    bound local source/launch, not from the helper request being checked.
    """
    fields = {'schema', 'operation', 'start_dispatch_request', 'attempt_deadline_utc'}
    if (not isinstance(record, dict) or set(record) != fields
            or record['schema'] != 'aws_c0_controller_local_helper_request/v1'
            or record['operation'] not in ('STATUS', 'SAFE_CLOSE')):
        raise Refusal("closed helper-only request required; START is not a helper")
    if len(canonical_bytes(record)) > 16384:
        raise Refusal("local helper request exceeds bounded transport")
    validate_ssm_dispatch_record_v2(expected_start_dispatch, semantic_parameters=semantic_parameters)
    if record['start_dispatch_request'] != expected_start_dispatch:
        raise Refusal("helper does not bind exact accepted START request")
    deadline = record['attempt_deadline_utc']
    if (not isinstance(deadline, str) or deadline != attempt_deadline_utc
            or not re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z', deadline)):
        raise Refusal("helper attempt deadline differs from bound launch")
    earliest = _utc(semantic_parameters['SsmExpectedCommandNotBeforeUtc'][0])
    end = _utc(deadline)
    if (not isinstance(now, dt.datetime) or now.tzinfo != dt.timezone.utc
            or not earliest <= now < end or not 0 < (end - earliest).total_seconds() <= 43200):
        raise Refusal("helper outside bounded attempt interval")
    return record


def bind_ssm_dispatch_to_authenticated_sources(dispatch: dict[str, Any], launch: dict[str, Any],
                                               live_auth: dict[str, Any]) -> None:
    """Downloaded records may verify, but never supply, argv semantic values."""
    if dispatch['attempt_identity'] != launch['attempt_identity']:
        raise Refusal("SSM dispatch attempt differs from authenticated launch")
    rows = [row for row in live_auth.get('post_deployment_control_preimages', [])
            if isinstance(row, dict) and row.get('control_kind') == 'SSM_DOCUMENT']
    if len(rows) != 1:
        raise Refusal("one authenticated deployed SSM document observation required")
    try:
        raw = base64.b64decode(rows[0]['canonical_json_base64'], validate=True)
    except (KeyError, ValueError, TypeError) as exc:
        raise Refusal("SSM document observation bytes absent") from exc
    observation = strict_json(raw)
    if set(rows[0]) != {'control_kind', 'identity', 'canonical_json_base64', 'observed_utc', 'authenticated_source_identity'}:
        raise Refusal("SSM document observation fields not closed")
    _identity_field(rows[0], 'identity', 'aws_ssm_document_observation/v1')
    _identity_field(rows[0], 'authenticated_source_identity', 'aws_ssm_document_observation_source/v1')
    if not _utc(live_auth['deployment_completed_utc']) <= _utc(rows[0]['observed_utc']) <= _utc(live_auth['observed_utc']):
        raise Refusal("SSM document observation outside authenticated deployment interval")
    if rows[0]['identity']['sha256'] != digest(raw):
        raise Refusal("SSM observed document digest mismatch")
    if (observation.get('Name') != dispatch['document_name'] or observation.get('DocumentVersion') != dispatch['document_version']
            or observation.get('Status') != 'Active' or observation.get('DocumentType') != 'Command'):
        raise Refusal("SSM dispatch does not match authenticated deployed document")


def build_ssm_completion_v2(*, attempt_identity: dict[str, str], dispatch_identity: dict[str, str],
                            command_id: str, invocation_status: str, observed_utc: str) -> dict[str, Any]:
    """Construct the closed authenticated SSM completion observation."""
    if invocation_status != "Success" or not re.fullmatch(r"[A-Za-z0-9-]{1,64}", command_id):
        raise Refusal("SSM completion v2 refused")
    _utc(observed_utc)
    record = {"schema": "aws_c0_ssm_completion_observation/v2", "attempt_identity": attempt_identity,
              "ssm_dispatch_request_identity": dispatch_identity, "command_id": command_id,
              "invocation_status": invocation_status, "observed_utc": observed_utc,
              "zero_science_counters": ZERO}
    return record


def validate_ssm_completion_v2(record: Any) -> dict[str, Any]:
    required = {"schema", "attempt_identity", "ssm_dispatch_request_identity", "command_id",
                "invocation_status", "observed_utc", "zero_science_counters"}
    if not isinstance(record, dict) or set(record) != required or record.get("schema") != "aws_c0_ssm_completion_observation/v2":
        raise Refusal("SSM completion v2 fields refused")
    if record["invocation_status"] != "Success" or record["zero_science_counters"] != ZERO:
        raise Refusal("SSM completion v2 content refused")
    _utc(record["observed_utc"])
    return record


def build_runtime_start_attestation_bundle_v3(*, source_sidecar_identity: dict[str, str],
                                              source_sidecar_bytes: bytes,
                                              dispatch_identity: dict[str, str],
                                              controller_capture_journal_identity: dict[str, str],
                                              controller_capture_journal_authenticated_readback: dict[str, Any]) -> dict[str, Any]:
    record = {"schema": "aws_c0_runtime_start_attestation_bundle/v4",
              "source_sidecar_identity": source_sidecar_identity,
              "source_sidecar_sha256": digest(source_sidecar_bytes),
              "source_sidecar_byte_count": len(source_sidecar_bytes),
              "ssm_dispatch_request_identity": dispatch_identity,
              "controller_capture_journal_identity": controller_capture_journal_identity,
              "controller_capture_journal_authenticated_readback": controller_capture_journal_authenticated_readback,
              "zero_science_counters": ZERO}
    return validate_runtime_start_attestation_bundle_v3(record)


def validate_runtime_start_attestation_bundle_v3(record: Any) -> dict[str, Any]:
    required = {"schema", "source_sidecar_identity", "source_sidecar_sha256", "source_sidecar_byte_count",
                "ssm_dispatch_request_identity", "controller_capture_journal_identity",
                "controller_capture_journal_authenticated_readback", "zero_science_counters"}
    if not isinstance(record, dict) or set(record) != required or record["schema"] != "aws_c0_runtime_start_attestation_bundle/v4":
        raise Refusal("runtime bundle v3 fields refused")
    _identity_field(record, "source_sidecar_identity", "aws_c0_source_sidecar/v5")
    _identity_field(record, "ssm_dispatch_request_identity", "aws_c0_ssm_dispatch_request/v2")
    _identity_field(record, "controller_capture_journal_identity", "aws_c0_controller_capture_journal/v1")
    readback = record["controller_capture_journal_authenticated_readback"]
    if not isinstance(readback, dict) or set(readback) != {
            "schema", "content_chain_sha256", "publication_receipt",
            "publication_receipt_identity", "readback_receipt", "readback_receipt_identity"} or \
       readback["schema"] != "aws_c0_controller_journal_authenticated_readback/v1":
        raise Refusal("runtime bundle journal readback refused")
    if not SHA.fullmatch(record["source_sidecar_sha256"]) or type(record["source_sidecar_byte_count"]) is not int or record["source_sidecar_byte_count"] < 1 or record["zero_science_counters"] != ZERO:
        raise Refusal("runtime bundle v3 content refused")
    return record


def bootstrap_imdsv2_credentials() -> dict[str, str]:
    """Perform the fixed three-exchange IMDSv2 bootstrap without persisting secrets.

    This capability is only reached by the local controller's real ``run``
    command; static validation never calls it.
    """
    token = _run(["/usr/bin/curl", "--fail", "--silent", "--show-error", "--max-time", "2",
                  "-X", "PUT", IMDS_BASE + "/api/token", "-H",
                  f"X-aws-ec2-metadata-token-ttl-seconds: {IMDS_TOKEN_TTL_SECONDS}"], 5).stdout.strip()
    if not token:
        raise Refusal("IMDSv2 token absent")
    token_text = token.decode("ascii", "strict")
    try:
        role = _run(["/usr/bin/curl", "--fail", "--silent", "--show-error", "--max-time", "2",
                     IMDS_BASE + "/meta-data/iam/security-credentials/", "-H",
                     "X-aws-ec2-metadata-token: " + token_text], 5).stdout.strip().decode("ascii", "strict")
        if not re.fullmatch(r"[A-Za-z0-9+=,.@_-]{1,128}", role):
            raise Refusal("IMDS role name invalid")
        document = strict_json(_run(["/usr/bin/curl", "--fail", "--silent", "--show-error", "--max-time", "2",
                                     IMDS_BASE + "/meta-data/iam/security-credentials/" + role, "-H",
                                     "X-aws-ec2-metadata-token: " + token_text], 5).stdout)
        required = {"AccessKeyId", "SecretAccessKey", "Token", "Expiration", "Code", "Type"}
        if not isinstance(document, dict) or not required <= set(document) or document.get("Code") != "Success":
            raise Refusal("IMDS credential document invalid")
        values = (document["AccessKeyId"], document["SecretAccessKey"], document["Token"], document["Expiration"])
        if not all(isinstance(value, str) and value for value in values):
            raise Refusal("IMDS credential values invalid")
        # These values are deliberately returned only to the immediate signing
        # caller.  They are never placed in the sidecar, journal, or request.
        return {"access_key_id": document["AccessKeyId"],
                "secret_access_key": document["SecretAccessKey"],
                "session_token": document["Token"]}
    finally:
        token_buffer = bytearray(token)
        for index in range(len(token_buffer)):
            token_buffer[index] = 0


def sigv4_exact_version_get(bucket: str, key: str, version_id: str, expected_sha256: str,
                             credentials: dict[str, str], transport: Any, now: dt.datetime) -> tuple[bytes, dict[str, Any]]:
    """Local checksum-mode SigV4 S3 GET; transport is injected for offline tests."""
    if not BUCKET.fullmatch(bucket) or not VERSION.fullmatch(version_id) or not SHA.fullmatch(expected_sha256):
        raise Refusal("invalid exact-version source coordinate")
    required = {"access_key_id", "secret_access_key", "session_token"}
    if set(credentials) != required or not all(isinstance(credentials[k], str) and credentials[k] for k in required):
        raise Refusal("IMDS credential object refused")
    host = f"{bucket}.s3.{REGION}.amazonaws.com"; amzdate = now.strftime("%Y%m%dT%H%M%SZ"); day = now.strftime("%Y%m%d")
    query = "versionId=" + urllib.parse.quote(version_id, safe="")
    uri = "/" + urllib.parse.quote(key, safe="/-_.~")
    headers = {"host": host, "x-amz-date": amzdate, "x-amz-security-token": credentials["session_token"],
               "x-amz-content-sha256": hashlib.sha256(b"").hexdigest(), "x-amz-checksum-mode": "ENABLED"}
    names = sorted(headers); canonical_headers = "".join(f"{name}:{headers[name]}\n" for name in names); signed = ";".join(names)
    canonical = "\n".join(("GET", uri, query, canonical_headers, signed, headers["x-amz-content-sha256"]))
    scope = f"{day}/{REGION}/s3/aws4_request"; to_sign = "\n".join(("AWS4-HMAC-SHA256", amzdate, scope, hashlib.sha256(canonical.encode()).hexdigest()))
    secret = bytearray(credentials["secret_access_key"].encode())
    try:
        key_date = hmac.new(b"AWS4" + bytes(secret), day.encode(), hashlib.sha256).digest()
        key_region = hmac.new(key_date, REGION.encode(), hashlib.sha256).digest(); key_service = hmac.new(key_region, b"s3", hashlib.sha256).digest()
        signature = hmac.new(hmac.new(key_service, b"aws4_request", hashlib.sha256).digest(), to_sign.encode(), hashlib.sha256).hexdigest()
        headers["authorization"] = f"AWS4-HMAC-SHA256 Credential={credentials['access_key_id']}/{scope}, SignedHeaders={signed}, Signature={signature}"
        raw, observed = transport(host, uri, query, headers)
    finally:
        for i in range(len(secret)): secret[i] = 0
    if (observed.get("version_id") != version_id or
            observed.get("checksum_sha256") != base64.b64encode(hashlib.sha256(raw).digest()).decode() or
            not isinstance(observed.get("etag"), str) or not observed["etag"] or
            digest(raw) != expected_sha256):
        raise Refusal("authenticated exact-version response refused")
    return raw, {"canonical_request_sha256": digest(canonical.encode()), "string_to_sign_sha256": digest(to_sign.encode()),
                 "response_sha256": digest(raw), "version_id": version_id, "checksum_sha256": observed["checksum_sha256"],
                 "etag": observed["etag"], "tls_certificate_sha256": observed.get("tls_certificate_sha256"),
                 "request_id": observed.get("request_id")}


def https_exact_version_transport(host: str, uri: str, query: str,
                                  headers: dict[str, str]) -> tuple[bytes, dict[str, Any]]:
    """Standard-library HTTPS transport for the injected local SigV4 engine.

    The transport intentionally has no credential-provider behaviour: all
    credentials arrive in the already signed request and only authenticated S3
    response metadata is returned to the caller.
    """
    connection = http.client.HTTPSConnection(host, 443, timeout=10,
                                               context=ssl.create_default_context())
    try:
        connection.request("GET", uri + "?" + query, headers=headers)
        response = connection.getresponse()
        raw = response.read(MAX_OBJECT_BYTES + 1)
        if len(raw) > MAX_OBJECT_BYTES or response.status != 200:
            raise Refusal("exact-version HTTPS response refused")
        socket = connection.sock
        if socket is None:
            raise Refusal("TLS socket absent")
        certificate = socket.getpeercert(binary_form=True)
        metadata = {"version_id": response.getheader("x-amz-version-id"),
                    "etag": response.getheader("etag"),
                    "checksum_sha256": response.getheader("x-amz-checksum-sha256"),
                    "request_id": response.getheader("x-amz-request-id"),
                    "tls_certificate_sha256": digest(certificate)}
        if not all(isinstance(metadata[key], str) and metadata[key] for key in
                   ("version_id", "etag", "checksum_sha256", "request_id", "tls_certificate_sha256")):
            raise Refusal("authenticated HTTPS metadata absent")
        return raw, metadata
    finally:
        connection.close()


def sigv4_conditional_journal_put(bucket: str, key: str, raw: bytes, credentials: dict[str, str],
                                  now: dt.datetime) -> dict[str, Any]:
    """One standard-library, signed conditional journal Put; no SDK/CLI path."""
    if not BUCKET.fullmatch(bucket) or not raw or len(raw) > CaptureJournal.MAX_BYTES:
        raise Refusal("controller journal Put coordinate refused")
    required = {"access_key_id", "secret_access_key", "session_token"}
    if set(credentials) != required or not all(isinstance(credentials[name], str) and credentials[name] for name in required):
        raise Refusal("controller journal credentials refused")
    host = f"{bucket}.s3.{REGION}.amazonaws.com"; uri = "/" + urllib.parse.quote(key, safe="/-_.~")
    day = now.strftime("%Y%m%d"); amzdate = now.strftime("%Y%m%dT%H%M%SZ"); payload = digest(raw)
    headers = {"host": host, "x-amz-date": amzdate, "x-amz-security-token": credentials["session_token"],
               "x-amz-content-sha256": payload, "x-amz-checksum-sha256": base64.b64encode(hashlib.sha256(raw).digest()).decode(),
               "if-none-match": "*", "content-type": "application/json"}
    names = sorted(headers); canonical_headers = "".join(f"{name}:{headers[name]}\n" for name in names); signed = ";".join(names)
    canonical = "\n".join(("PUT", uri, "", canonical_headers, signed, payload)); scope = f"{day}/{REGION}/s3/aws4_request"
    to_sign = "\n".join(("AWS4-HMAC-SHA256", amzdate, scope, digest(canonical.encode())))
    secret = bytearray(credentials["secret_access_key"].encode())
    try:
        date_key = hmac.new(b"AWS4" + bytes(secret), day.encode(), hashlib.sha256).digest()
        region_key = hmac.new(date_key, REGION.encode(), hashlib.sha256).digest(); service_key = hmac.new(region_key, b"s3", hashlib.sha256).digest()
        signature = hmac.new(hmac.new(service_key, b"aws4_request", hashlib.sha256).digest(), to_sign.encode(), hashlib.sha256).hexdigest()
        headers["authorization"] = f"AWS4-HMAC-SHA256 Credential={credentials['access_key_id']}/{scope}, SignedHeaders={signed}, Signature={signature}"
        connection = http.client.HTTPSConnection(host, 443, timeout=10, context=ssl.create_default_context())
        try:
            connection.request("PUT", uri, body=raw, headers=headers); response = connection.getresponse(); response.read()
            version = response.getheader("x-amz-version-id")
            etag = response.getheader("etag")
            request_id = response.getheader("x-amz-request-id")
            if (response.status != 200 or not isinstance(version, str) or
                    not VERSION.fullmatch(version) or not isinstance(etag, str) or
                    not etag or not isinstance(request_id, str) or not request_id):
                raise Refusal("controller journal conditional Put refused")
        finally:
            connection.close()
    finally:
        for index in range(len(secret)): secret[index] = 0
    return {"key": key, "version_id": version, "etag": etag,
            "bytes": len(raw), "sha256": payload,
            "checksum_sha256_base64": headers["x-amz-checksum-sha256"]}


def _identity_field(record: dict[str, Any], field: str, kind: str) -> str:
    value = record.get(field)
    if not isinstance(value, dict) or set(value) != {"kind", "value", "sha256"}:
        raise Refusal(f"invalid {field}")
    if value["kind"] != kind or value["value"] != value["sha256"] or not SHA.fullmatch(value["sha256"]):
        raise Refusal(f"identity closure failed: {field}")
    return value["sha256"]


def validate_launch(record: Any, rehearsal: str, attempt: str) -> dict[str, Any]:
    if not isinstance(record, dict) or set(record) != LAUNCH_REQUIRED:
        raise Refusal("launch-v5 fields are not closed")
    expected = {
        "schema": "aws_c0_launch_request/v7", "authority_id": AUTHORITY_ID,
        "correction_authority_id": CORRECTION_ID,
        "closure_correction_authority_id": CLOSURE_ID,
        "material_correction_authority_id": "EBU-AWS-C0-MATERIAL-IDENTITY-RUNTIME-VALIDATION-CORRECTION-AUTHORITY-v1",
        "record_class": "NON_SCIENTIFIC_AWS_C0_EVIDENCE",
        "scientific_execution_authorized": False,
        "stage_f_execution_authorized": False, "stage_f_readiness_claimed": False,
        "zero_science_counters": ZERO, "rehearsal_id": rehearsal,
        "attempt_id": attempt, "region": REGION, "instance_id": INSTANCE_ID,
        "required_initial_instance_state": "stopped", "retry_attempts": 1,
        "cleanup_path": "STEP_FUNCTIONS_SINGLE_STOP_THEN_FINALIZER_VERIFY",
    }
    for key, wanted in expected.items():
        if record.get(key) != wanted:
            raise Refusal(f"launch mismatch: {key}")
    if not REHEARSAL.fullmatch(rehearsal) or not ATTEMPT.fullmatch(attempt):
        raise Refusal("invalid rehearsal/attempt")
    _mode(attempt)
    exact_prefix = f"rehearsal/aws-c0/{rehearsal}/{attempt}/"
    if record.get("artifact_prefix") != exact_prefix or not PREFIX.fullmatch(exact_prefix):
        raise Refusal("attempt prefix mismatch")
    root_digest(record)
    _no_forbidden(record)
    kinds = {
        "attempt_identity": "aws_c0_attempt/v1",
        "preparation_packet_identity": "aws_c0_preparation_packet/v6",
        "preparation_authorization_identity": "aws_c0_preparation_authorization/v5",
        "authority_audit_identity": "aws_c0_audit_static_handoff_authority_audit/v4",
        "static_validation_identity": "aws_c0_material_runtime_static_validation/v4",
        "private_infrastructure_snapshot_identity": "aws_c0_private_infrastructure_snapshot/v1",
        "cost_model_identity": "aws_c0_cost_model/v2",
        "closure_seed_identity": "aws_c0_closure_seed/v2",
    }
    for field, kind in kinds.items():
        _identity_field(record, field, kind)
    receipts = list(record.get("artifact_version_receipts", []))
    for field in ("preparation_packet_object", "preparation_authorization_object", "authority_audit_object",
                  "static_validation_object", "private_infrastructure_snapshot_object", "cost_model_object",
                  "closure_seed_object"):
        receipts.append(record[field])
    if len(record.get("artifact_version_receipts", [])) != 8:
        raise Refusal("exactly eight artifact receipts required")
    receipt_fields = {"bucket_identity", "key", "version_id", "bytes", "sha256",
                      "checksum_sha256_base64"}
    seen_receipts: set[tuple[str, str]] = set()
    for receipt in receipts:
        if not isinstance(receipt, dict) or set(receipt) != receipt_fields:
            raise Refusal("artifact receipt is not closed")
        _identity_field(receipt, "bucket_identity", "aws_s3_bucket/v1")
        if type(receipt["bytes"]) is not int or receipt["bytes"] < 1 or not VERSION.fullmatch(str(receipt["version_id"])) or not SHA.fullmatch(str(receipt["sha256"])):
            raise Refusal("artifact receipt value invalid")
        if not re.fullmatch(r"[A-Za-z0-9+/]{43}=", str(receipt["checksum_sha256_base64"])):
            raise Refusal("artifact checksum encoding invalid")
        if receipt["checksum_sha256_base64"] != base64.b64encode(bytes.fromhex(receipt["sha256"])).decode():
            raise Refusal("artifact checksum/hash mismatch")
        coordinate = (receipt["key"], receipt["version_id"])
        if coordinate in seen_receipts:
            raise Refusal("duplicate artifact receipt")
        seen_receipts.add(coordinate)
    timeouts = record.get("phase_timeouts_seconds")
    timeout_keys = {"boot", "ssm_online", "ssm_start_delivery", "heartbeat_stale", "worker_runtime", "finalizer", "instance_stop", "overall"}
    if not isinstance(timeouts, dict) or set(timeouts) != timeout_keys or any(type(v) is not int or v < 1 for v in timeouts.values()):
        raise Refusal("invalid phase timeouts")
    if timeouts["finalizer"] > record["deployed_lambda_timeout_seconds"] or record["deployed_lambda_timeout_seconds"] > 900:
        raise Refusal("finalizer exceeds deployed Lambda bound")
    if timeouts["overall"] > record["state_machine_timeout_seconds"]:
        raise Refusal("overall exceeds state-machine timeout")
    observed = _utc(record["observed_utc"])
    attempt_deadline = _utc(record["attempt_deadline_utc"])
    cleanup_deadline = _utc(record["cleanup_deadline_utc"])
    if not observed < attempt_deadline < cleanup_deadline:
        raise Refusal("launch deadlines are unordered")
    if (cleanup_deadline - attempt_deadline).total_seconds() < timeouts["instance_stop"]:
        raise Refusal("cleanup window cannot contain the sealed stop timeout")
    if type(record["heartbeat_interval_seconds"]) is not int or not 1 <= record["heartbeat_interval_seconds"] <= timeouts["heartbeat_stale"]:
        raise Refusal("invalid heartbeat interval")
    if type(record["checkpoint_interval_seconds"]) is not int or not 1 <= record["checkpoint_interval_seconds"] <= timeouts["worker_runtime"]:
        raise Refusal("invalid checkpoint interval")
    cost = record.get("cost_envelope")
    if not isinstance(cost, dict) or set(cost) != {"currency", "ceiling_minor_units", "cost_model_identity", "cost_model_object", "accounting_window", "resource_limits", "iam_pagination_bounds"} or cost["currency"] != "USD" or type(cost["ceiling_minor_units"]) is not int or cost["ceiling_minor_units"] < 1:
        raise Refusal("invalid live cost envelope")
    _identity_field(cost, "cost_model_identity", "aws_c0_cost_model/v2")
    if cost["cost_model_identity"] != record["cost_model_identity"] or cost["cost_model_object"] != record["cost_model_object"]:
        raise Refusal("cost model binding mismatch")
    if cost["iam_pagination_bounds"] != record["iam_pagination_bounds"]:
        raise Refusal("IAM bounds mismatch")
    limits = cost["resource_limits"]
    required_limits = {"instance_running_seconds", "public_ipv4_seconds", "nat_gateway_seconds", "vpc_endpoint_seconds",
        "s3_put_requests", "s3_get_requests", "s3_head_requests", "s3_list_requests", "step_functions_transitions",
        "lambda_invocations", "lambda_duration_milliseconds", "kms_requests", "kms_key_seconds", "data_transfer_bytes",
        "cloudwatch_ingested_bytes", "ebs_volume_gib_seconds", "ebs_provisioned_iops_seconds",
        "ebs_provisioned_throughput_mibps_seconds", "s3_version_byte_seconds", "cloudwatch_log_byte_seconds",
        "ecr_byte_seconds", "snapshot_gib_seconds"}
    if not isinstance(limits, dict) or set(limits) != required_limits or any(type(value) is not int or value < 0 for value in limits.values()):
        raise Refusal("invalid live resource limits")
    if any(limits[name] < 1 for name in ("instance_running_seconds", "s3_put_requests", "s3_get_requests", "s3_head_requests", "s3_list_requests", "step_functions_transitions", "lambda_invocations", "lambda_duration_milliseconds")):
        raise Refusal("required live resource maximum is zero")
    running_phase_bound = sum(timeouts[name] for name in (
        "boot", "ssm_online", "ssm_start_delivery", "heartbeat_stale",
        "worker_runtime", "instance_stop"))
    if limits["instance_running_seconds"] < running_phase_bound:
        raise Refusal("instance-running maximum below reachable phase bound")
    if limits["lambda_duration_milliseconds"] < timeouts["finalizer"] * 1000:
        raise Refusal("Lambda-duration maximum below finalizer timeout")
    window = cost["accounting_window"]
    if set(window) != {"start_inclusive_utc", "end_exclusive_utc", "retained_resource_horizon_seconds", "scope", "invoice_reconciliation_claimed"}:
        raise Refusal("accounting window is not closed")
    if _utc(window["start_inclusive_utc"]) > observed or _utc(window["end_exclusive_utc"]) < cleanup_deadline:
        raise Refusal("accounting window does not dominate attempt")
    return record


def build_platform_smoke_known_case_local_binding(record: Any) -> dict[str, Any]:
    """Bind the first non-scientific capsule to an existing valid SUCCESS launch.

    This is a local planning/validation projection.  It does not authorize or
    invoke AWS and deliberately carries no global aggregate or study payload.
    """
    if not isinstance(record, dict):
        raise Refusal("platform smoke launch must be an object")
    launch = validate_launch(record, record.get("rehearsal_id"), record.get("attempt_id"))
    if _mode(launch["attempt_id"]) != "SUCCESS":
        raise Refusal("platform smoke first capsule requires the SUCCESS known case")
    inputs = (
        ("LAUNCH_REQUEST", identity("aws_c0_launch_request/v7", launch["record_sha256"])),
        ("PREPARATION_PACKET", launch["preparation_packet_identity"]),
        ("PREPARATION_AUTHORIZATION", launch["preparation_authorization_identity"]),
        ("COST_MODEL", launch["cost_model_identity"]),
        ("CLOSURE_SEED", launch["closure_seed_identity"]),
    )
    return {
        "schema": "aws_c0_platform_smoke_known_case_local_binding/v3",
        "capsule_id": PLATFORM_SMOKE_CAPSULE_ID,
        "test_case": "SUCCESS_KNOWN_CASE",
        "attempt_identity": launch["attempt_identity"],
        "input_identities_in_order": [
            {"role": role, "identity": input_identity} for role, input_identity in inputs
        ],
        "expected_artifact_classes_in_order": [
            "ATTEMPT_CLAIM", "START_RECEIPT", "HEARTBEAT", "SAFE_CLOSE_RECEIPT",
            "CHECKPOINT", "SYNTHETIC_MANIFEST", "TERMINAL_RECEIPT",
            "CONTROLLER_CAPTURE_JOURNAL", "CONTROLLER_JOURNAL_HANDOFF",
            "STOPPED_OBSERVATION", "RESOURCE_USE_CLOSURE", "FINALIZER_RECEIPT",
            "FINALIZER_CAPTURE_JOURNAL", "COST_CLOSURE",
            "RETRIEVAL_VERIFICATION", "FINAL_MANIFEST",
        ],
        "common_receipt_fields_in_order": list(PLATFORM_SMOKE_COMMON_RECEIPT_FIELDS),
        "reused_foundation_capabilities_in_order": list(PLATFORM_SMOKE_FOUNDATION_CAPABILITIES),
        "budget_binding": {
            "currency": launch["cost_envelope"]["currency"],
            "ceiling_minor_units": launch["cost_envelope"]["ceiling_minor_units"],
            "cost_model_identity": launch["cost_model_identity"],
            "resource_limits_sha256": digest(canonical_bytes(
                launch["cost_envelope"]["resource_limits"])),
            "accounting_window_sha256": digest(canonical_bytes(
                launch["cost_envelope"]["accounting_window"])),
        },
        "termination_binding": {
            "attempt_deadline_utc": launch["attempt_deadline_utc"],
            "cleanup_deadline_utc": launch["cleanup_deadline_utc"],
            "phase_timeouts_seconds": launch["phase_timeouts_seconds"],
            "state_machine_timeout_seconds": launch["state_machine_timeout_seconds"],
            "retry_attempts": launch["retry_attempts"],
            "cleanup_path": launch["cleanup_path"],
        },
        "scientific_conclusion_authorized": False,
        "live_aws_execution_authorized": False,
        "separate_capsule_authority_required": True,
        "global_aggregate_payload_embedded": False,
    }


def _run(argv: list[str], timeout: int, ok: tuple[int, ...] = (0,)) -> subprocess.CompletedProcess[bytes]:
    result = subprocess.run(argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, timeout=timeout, check=False,
                            shell=False, env={"PATH": "/usr/local/bin:/usr/bin:/bin", "LC_ALL": "C"})
    if result.returncode not in ok:
        raise Refusal(f"bounded child failed: {Path(argv[0]).name}:{result.returncode}")
    return result


def _bounded_lines(pipe: Any, process: subprocess.Popen[bytes], deadline: float):
    """Yield complete LF-framed lines without allowing a silent child to hang."""
    selector = selectors.DefaultSelector()
    selector.register(pipe, selectors.EVENT_READ)
    pending = b""
    try:
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise Refusal("worker runtime timeout")
            ready = selector.select(min(1.0, remaining))
            if not ready:
                if process.poll() is not None:
                    if pending:
                        raise Refusal("worker ended with partial event")
                    return
                continue
            chunk = os.read(pipe.fileno(), 65_536)
            if not chunk:
                if pending:
                    raise Refusal("worker ended with partial event")
                return
            pending += chunk
            while b"\n" in pending:
                line, pending = pending.split(b"\n", 1)
                yield line + b"\n"
    finally:
        selector.close()


def _download(bucket: str, key: str, version: str, expected: str,
              *, journal: "CaptureJournal | None" = None, source_role: str | None = None,
              credential_provider: Any = bootstrap_imdsv2_credentials,
              transport: Any = https_exact_version_transport,
              now: dt.datetime | None = None) -> tuple[bytes, dict[str, Any]]:
    """Read one immutable source through the local checksum-mode SigV4 engine.

    This is the sole controller S3 GET route.  ``credential_provider`` and
    ``transport`` are explicit seams so tests exercise the complete signing
    path without contacting IMDS or AWS.
    """
    if not BUCKET.fullmatch(bucket) or not VERSION.fullmatch(version) or not SHA.fullmatch(expected):
        raise Refusal("invalid S3 coordinate")
    timestamp = now or dt.datetime.now(dt.timezone.utc)
    if timestamp.tzinfo is None:
        raise Refusal("SigV4 timestamp must be timezone-aware")
    requested_utc = timestamp.astimezone(dt.timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")
    capture = {"source_role": source_role, "bucket": bucket, "key": key,
               "version_id": version, "expected_sha256": expected,
               "operation": "S3_GET_OBJECT_EXACT_VERSION",
               "operation_requested_utc": requested_utc,
               "request_envelope_sha256": digest(canonical_bytes({
                   "method": "GET", "bucket": bucket, "key": key,
                   "version_id": version, "checksum_mode": "ENABLED"})),
               "source_object_identity": identity("aws_c0_s3_object/v1", expected)}
    if journal is not None:
        journal.reserve_for_operation(capture)
    try:
        raw, metadata = sigv4_exact_version_get(bucket, key, version, expected,
                                                  credential_provider(), transport,
                                                  timestamp.astimezone(dt.timezone.utc))
        capture["observed_bytes"] = len(raw)
        capture["observed_sha256"] = digest(raw)
        capture["observed_version_id"] = metadata["version_id"]
        capture["observed_checksum_sha256"] = metadata["checksum_sha256"]
        capture["observed_etag"] = metadata["etag"]
        capture["observed_request_id"] = metadata["request_id"]
        capture["operation_completed_utc"] = (now or dt.datetime.now(dt.timezone.utc)).astimezone(dt.timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")
        if journal is not None:
            journal.complete("S3_GET_OBJECT_EXACT_VERSION", "EC2_INSTANCE_PROFILE", capture)
        return raw, metadata
    except Exception as exc:
        if journal is not None:
            capture["failure_class"] = type(exc).__name__
            journal.failed("S3_GET_OBJECT_EXACT_VERSION", "EC2_INSTANCE_PROFILE", capture)
        raise


def _secure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
    os.chmod(path.parent, 0o700)
    if os.geteuid() != 0:
        raise Refusal("controller must run as root")


def _exclusive(path: Path, raw: bytes) -> None:
    _secure_parent(path)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        with os.fdopen(fd, "wb", closefd=False) as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
    finally:
        os.close(fd)


def _read_bound_request_file(path: Path) -> bytes:
    """Read the exact private request/sidecar without path-reopen races."""
    stem = path.name.removesuffix('.source.json') if path.name.endswith('.source.json') else path.stem
    if path.parent != REQUESTS or not path.name.endswith('.json') or not ATTEMPT.fullmatch(stem):
        raise Refusal('helper local request path is not exact')
    if os.geteuid() != 0:
        raise Refusal('helper local request access requires root')
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    parent = os.open(REQUESTS.parent, flags)
    directory = None
    try:
        info = os.fstat(parent)
        if info.st_uid != 0 or stat.S_IMODE(info.st_mode) != 0o700:
            raise Refusal('helper state directory must be private root-owned')
        directory = os.open(REQUESTS.name, flags, dir_fd=parent)
        info = os.fstat(directory)
        if info.st_uid != 0 or stat.S_IMODE(info.st_mode) != 0o700:
            raise Refusal('helper request directory must be private root-owned')
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
        try:
            before = os.fstat(fd)
            if (not stat.S_ISREG(before.st_mode) or before.st_uid != 0 or stat.S_IMODE(before.st_mode) != 0o600
                    or before.st_nlink != 1 or not 1 <= before.st_size <= MAX_OBJECT_BYTES):
                raise Refusal('helper requires one private bounded regular request file')
            with os.fdopen(fd, 'rb', closefd=False) as handle:
                raw = handle.read(MAX_OBJECT_BYTES + 1)
            after = os.fstat(fd)
            if len(raw) != before.st_size or any(getattr(before,k) != getattr(after,k) for k in
                    ('st_dev','st_ino','st_mode','st_uid','st_nlink','st_size','st_mtime_ns','st_ctime_ns')):
                raise Refusal('helper request changed during bounded read')
            return raw
        finally:
            os.close(fd)
    finally:
        if directory is not None: os.close(directory)
        os.close(parent)


def _file_secure(path: Path) -> bytes:
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_uid != 0 or info.st_mode & 0o022:
        raise Refusal(f"insecure file: {path}")
    return path.read_bytes()


def _workflow_identity(arn: str) -> dict[str, str]:
    if not EXECUTION_ARN.fullmatch(arn):
        raise Refusal("invalid workflow execution ARN")
    return identity("aws_step_functions_standard_execution/v1", digest(canonical_bytes({
        "schema": "aws_c0_workflow_execution/v1", "execution_arn": arn,
    })))


def _ssm_request_identity(launch_id: str, live_packet_id: str,
                          live_auth_id: str, workflow_id: dict[str, str],
                          prefix: str) -> dict[str, str]:
    preimage = {
        "schema": "aws_c0_ssm_command_request/v3",
        "artifact_prefix": prefix,
        "launch_request_identity": identity("aws_c0_launch_request/v7", launch_id),
        "live_packet_identity": identity("aws_c0_live_packet/v7", live_packet_id),
        "live_authorization_identity": identity("aws_c0_live_authorization/v7", live_auth_id),
        "workflow_execution_identity": workflow_id,
    }
    return identity("aws_ssm_command/v3", digest(canonical_bytes(preimage)))


OPERATIONAL_SOURCE_FIELDS = {"schema", "artifact_bucket", "launch_key", "launch_version_id", "launch_sha256", "launch_bytes",
    "live_packet_key", "live_packet_version_id", "live_packet_sha256", "live_packet_bytes",
    "live_authorization_key", "live_authorization_version_id", "live_authorization_sha256", "live_authorization_bytes",
    "live_authorization_identity", "workflow_execution_identity", "workflow_execution_arn", "ssm_command_identity",
    "rehearsal_id", "attempt_id", "artifact_prefix", "declared_exact_version_source_get_captures_in_order", "zero_science_counters",
    "ssm_dispatch_semantic21", "ssm_dispatch_transport2"}


def validate_helper_local_source_context(args: argparse.Namespace, launch_raw: bytes, source_raw: bytes) -> dict[str, Any]:
    """Cross-bind previously prepared local inputs, not a full evidence proof.

    These operational inputs must have been read by the private descriptor
    loader. The accepted complete source-sidecar proof remains a separate
    required runtime/evidence attachment; this function cannot substitute it.
    """
    semantic = ssm_semantic_parameters_from_argv(args)
    launch = validate_launch(strict_json(launch_raw), args.rehearsal_id, args.attempt_id)
    source = strict_json(source_raw)
    if not isinstance(source, dict) or set(source) != OPERATIONAL_SOURCE_FIELDS or source.get('schema') != 'aws_c0_source_sidecar/v5':
        raise Refusal('helper operational source field closure failed')
    if (source['ssm_dispatch_semantic21'] != semantic or source['zero_science_counters'] != ZERO
            or any(type(v) is not int for v in source['zero_science_counters'].values())):
        raise Refusal('helper operational source semantics/science mismatch')
    for name in SEMANTIC21:
        # Region/token/window live only in the exact stored START transport.
        if name in source:
            expected = getattr(args, 'bucket' if name == 'artifact_bucket' else name)
            if source[name] != expected or type(source[name]) is not type(expected):
                raise Refusal('helper source scalar differs from explicit argv: '+name)
    if len(launch_raw) != args.launch_bytes or digest(launch_raw) != args.launch_sha256:
        raise Refusal('helper launch bytes differ from exact prepared source')
    transport = source['ssm_dispatch_transport2']
    if not isinstance(transport, dict) or set(transport) != set(TRANSPORT2):
        raise Refusal('helper accepted START transport missing')
    start_args = argparse.Namespace(**{**vars(args), **transport})
    start = validate_ssm_dispatch_v2(start_args)
    workflow_id = _workflow_identity(args.workflow_execution_arn)
    if (start['attempt_identity'] != launch['attempt_identity'] or launch['artifact_prefix'] != args.artifact_prefix
            or source['workflow_execution_identity'] != workflow_id
            or source['live_authorization_identity'] != identity('aws_c0_live_authorization/v7',args.live_authorization_sha256)
            or source['ssm_command_identity'] != _ssm_request_identity(root_digest(launch),args.live_packet_sha256,
                                    args.live_authorization_sha256,workflow_id,args.artifact_prefix)):
        raise Refusal('helper prepared source attempt/workflow/identity mismatch')
    journal = CaptureJournal.restore('EC2_INSTANCE_PROFILE_CONTROLLER',source['declared_exact_version_source_get_captures_in_order'])
    previous_completion = _utc(args.ssm_expected_command_not_before_utc)
    for stem,envelope in zip(('launch','live_packet','live_authorization'),journal.envelopes):
        capture=envelope['operation_capture_preimage'];expected_sha=getattr(args,stem+'_sha256')
        wanted={'bucket':args.bucket,'key':getattr(args,stem+'_key'),'version_id':getattr(args,stem+'_version_id'),
            'operation':'S3_GET_OBJECT_EXACT_VERSION',
            'source_object_identity':identity('aws_c0_s3_object/v1',expected_sha),
            'request_envelope_sha256':digest(canonical_bytes({'method':'GET','bucket':args.bucket,
                'key':getattr(args,stem+'_key'),'version_id':getattr(args,stem+'_version_id'),'checksum_mode':'ENABLED'})),
            'expected_sha256':expected_sha,'observed_version_id':getattr(args,stem+'_version_id'),
            'observed_sha256':expected_sha,'observed_bytes':getattr(args,stem+'_bytes'),
            'observed_checksum_sha256':base64.b64encode(bytes.fromhex(expected_sha)).decode()}
        if any(capture.get(k) != v for k,v in wanted.items()) or type(capture.get('observed_bytes')) is not int:
            raise Refusal('helper prepared GET capture differs from exact argv source')
        if not previous_completion <= _utc(capture['operation_requested_utc']) <= _utc(capture['operation_completed_utc']) <= _utc(launch['attempt_deadline_utc']):
            raise Refusal('helper prepared GET capture chronology invalid')
        previous_completion = _utc(capture['operation_completed_utc'])
    return {'launch':launch,'expected_start_dispatch':start,'workflow_execution_arn':args.workflow_execution_arn,
            'attempt_deadline_utc':launch['attempt_deadline_utc']}


def load_local_helper_context(args: argparse.Namespace) -> dict[str, Any]:
    # Reject malformed command/semantic input before filesystem access. Only the
    # later helper validator may compare its deadline to independently read data.
    ssm_semantic_parameters_from_argv(args)
    request = _decode_ssm_transport(args)
    if (not isinstance(request, dict) or set(request) != {'schema','operation','start_dispatch_request','attempt_deadline_utc'}
            or request.get('schema') != 'aws_c0_controller_local_helper_request/v1'
            or request['operation'] not in ('STATUS','SAFE_CLOSE')):
        raise Refusal('local helper cannot load START or unknown request kinds')
    path = REQUESTS / (args.attempt_id+'.json')
    return validate_helper_local_source_context(args,_read_bound_request_file(path),
                                                _read_bound_request_file(path.with_suffix('.source.json')))


def prepare_request(args: argparse.Namespace, *, credential_provider: Any = bootstrap_imdsv2_credentials,
                    transport: Any = https_exact_version_transport,
                    now: dt.datetime | None = None) -> None:
    dispatch = validate_ssm_dispatch_v2(args)
    semantic = dispatch['semantic_parameters']
    current = now or dt.datetime.now(dt.timezone.utc)
    if not _utc(args.ssm_expected_command_not_before_utc) <= current <= _utc(args.ssm_expected_command_not_after_utc):
        raise Refusal("SSM command outside explicit authorized time interval")
    if not REHEARSAL.fullmatch(args.rehearsal_id) or not ATTEMPT.fullmatch(args.attempt_id):
        raise Refusal("invalid attempt coordinates")
    journal = CaptureJournal("EC2_INSTANCE_PROFILE_CONTROLLER")
    # The frozen IMDSv2 flow is exactly token, role, credential document once;
    # all three declared source GETs share that one short-lived credential set.
    credentials = credential_provider()
    source_credentials = lambda: credentials
    raw, _ = _download(args.bucket, args.launch_key, args.launch_version_id, args.launch_sha256,
                       journal=journal, source_role="LAUNCH_REQUEST_V5",
                       credential_provider=source_credentials, transport=transport, now=now)
    if len(raw) != args.launch_bytes:
        raise Refusal("launch byte length mismatch")
    launch = validate_launch(strict_json(raw), args.rehearsal_id, args.attempt_id)
    if not args.workflow_execution_arn.endswith(":" + args.attempt_id):
        raise Refusal("workflow execution name must equal the single-use attempt id")
    live_raw, _ = _download(args.bucket, args.live_packet_key,
                            args.live_packet_version_id, args.live_packet_sha256,
                            journal=journal, source_role="LIVE_PACKET_V5",
                            credential_provider=source_credentials, transport=transport, now=now)
    if len(live_raw) != args.live_packet_bytes:
        raise Refusal("live packet byte length mismatch")
    live_packet = strict_json(live_raw)
    if not isinstance(live_packet, dict) or live_packet.get("schema") != "aws_c0_live_packet/v7" or "record_sha256" in live_packet:
        raise Refusal("invalid live packet")
    launch_id = root_digest(launch)
    bucket_identity = launch["closure_seed_object"]["bucket_identity"]
    launch_receipt = {"bucket_identity": bucket_identity, "key": args.launch_key,
        "version_id": args.launch_version_id, "bytes": args.launch_bytes, "sha256": args.launch_sha256,
        "checksum_sha256_base64": base64.b64encode(bytes.fromhex(args.launch_sha256)).decode()}
    if live_packet.get("launch_request_identity") != identity("aws_c0_launch_request/v7", launch_id) or live_packet.get("launch_request_object") != launch_receipt or live_packet.get("packet_disposition") != "AWS_C0_LIVE_PACKET_COMPLETE_UNAUTHORIZED":
        raise Refusal("live packet does not bind exact launch-v5")
    auth_raw, _ = _download(args.bucket, args.live_authorization_key,
                            args.live_authorization_version_id, args.live_authorization_sha256,
                            journal=journal, source_role="LIVE_AUTHORIZATION_V5",
                            credential_provider=source_credentials, transport=transport, now=now)
    if len(auth_raw) != args.live_authorization_bytes:
        raise Refusal("live authorization byte length mismatch")
    live_auth = strict_json(auth_raw)
    packet_receipt = {"bucket_identity": bucket_identity, "key": args.live_packet_key,
        "version_id": args.live_packet_version_id, "bytes": args.live_packet_bytes, "sha256": args.live_packet_sha256,
        "checksum_sha256_base64": base64.b64encode(bytes.fromhex(args.live_packet_sha256)).decode()}
    if not isinstance(live_auth, dict) or live_auth.get("schema") != "aws_c0_live_authorization/v7" or "record_sha256" in live_auth or live_auth.get("live_packet_identity") != identity("aws_c0_live_packet/v7", args.live_packet_sha256) or live_auth.get("live_packet_object") != packet_receipt or live_auth.get("attempt_identity") != launch["attempt_identity"]:
        raise Refusal("live authorization does not bind exact packet/attempt")
    bind_ssm_dispatch_to_authenticated_sources(dispatch, launch, live_auth)
    workflow_id = _workflow_identity(args.workflow_execution_arn)
    ssm_id = _ssm_request_identity(launch_id, args.live_packet_sha256,
                                   args.live_authorization_sha256, workflow_id,
                                   launch["artifact_prefix"])
    request_path = Path(args.output)
    if request_path.name != f"{args.attempt_id}.json" or request_path.parent != REQUESTS:
        raise Refusal("request path is not exact")
    source = {
        "schema": "aws_c0_source_sidecar/v5",
        "artifact_bucket": args.bucket,
        "launch_key": args.launch_key, "launch_version_id": args.launch_version_id,
        "launch_sha256": args.launch_sha256, "launch_bytes": args.launch_bytes,
        "live_packet_key": args.live_packet_key,
        "live_packet_version_id": args.live_packet_version_id,
        "live_packet_sha256": args.live_packet_sha256, "live_packet_bytes": args.live_packet_bytes,
        "live_authorization_key": args.live_authorization_key,
        "live_authorization_version_id": args.live_authorization_version_id,
        "live_authorization_sha256": args.live_authorization_sha256,
        "live_authorization_bytes": args.live_authorization_bytes,
        "live_authorization_identity": identity("aws_c0_live_authorization/v7", args.live_authorization_sha256),
        "workflow_execution_identity": workflow_id,
        "workflow_execution_arn": args.workflow_execution_arn,
        "ssm_command_identity": ssm_id,
        "rehearsal_id": args.rehearsal_id, "attempt_id": args.attempt_id,
        "artifact_prefix": launch["artifact_prefix"],
        "declared_exact_version_source_get_captures_in_order": journal.envelopes,
        "zero_science_counters": ZERO,
        "ssm_dispatch_semantic21": semantic,
        "ssm_dispatch_transport2": {name: getattr(args, name) for name in TRANSPORT2},
    }
    # semantic21 comes only from explicit argv and the transport pair is kept
    # separate; this local source journal never discovers a semantic value.
    _exclusive(request_path, raw)
    try:
        _exclusive(request_path.with_suffix(".source.json"), canonical_bytes(source))
    except Exception:
        request_path.unlink(missing_ok=True)
        raise


def _s3_put(bucket: str, key: str, raw: bytes, content_type: str = "application/json") -> dict[str, Any]:
    fd, name = tempfile.mkstemp(prefix="ebu-c0-put-", dir="/tmp")
    os.close(fd)
    try:
        Path(name).write_bytes(raw)
        checksum = base64.b64encode(hashlib.sha256(raw).digest()).decode()
        result = _run([AWS, "s3api", "put-object", "--bucket", bucket, "--key", key,
                       "--body", name, "--content-type", content_type,
                       "--checksum-algorithm", "SHA256", "--checksum-sha256", checksum,
                       "--if-none-match", "*", "--region", REGION], 120)
        response = json.loads(result.stdout)
        version = response.get("VersionId")
        if not isinstance(version, str) or not VERSION.fullmatch(version):
            raise Refusal("versioned S3 receipt missing")
        return {"key": key, "version_id": version, "bytes": len(raw),
                "sha256": digest(raw), "checksum_sha256_base64": checksum}
    finally:
        Path(name).unlink(missing_ok=True)


class CaptureJournal:
    """Bounded acyclic provenance journal; callers reserve failure capacity."""
    MAX_BYTES = 1048576
    MAX_ENVELOPES = 512
    def __init__(self, producer: str) -> None:
        self.producer, self.envelopes, self._bytes, self._previous = producer, [], 0, None
        self._sealed = False

    @classmethod
    def restore(cls, producer: str, envelopes: Any) -> "CaptureJournal":
        """Resume the three authenticated preparation captures in ``run``."""
        if not isinstance(envelopes, list) or len(envelopes) != 3:
            raise Refusal("controller journal preparation prefix refused")
        journal = cls(producer)
        previous: str | None = None
        expected_roles = ("LAUNCH_REQUEST_V5", "LIVE_PACKET_V5", "LIVE_AUTHORIZATION_V5")
        for role, envelope in zip(expected_roles, envelopes):
            required = {"schema", "producer", "operation", "authorization_context",
                        "operation_capture_preimage", "body_sha256", "disposition",
                        "previous_envelope_sha256"}
            if (not isinstance(envelope, dict) or set(envelope) != required or
                    envelope["schema"] != "aws_c0_capture_journal_envelope/v1" or
                    envelope["producer"] != producer or
                    envelope["operation"] != "S3_GET_OBJECT_EXACT_VERSION" or
                    envelope["authorization_context"] != "EC2_INSTANCE_PROFILE" or
                    envelope["disposition"] != "OBSERVED_COMPLETE" or
                    envelope["previous_envelope_sha256"] != previous):
                raise Refusal("controller journal preparation envelope refused")
            capture = envelope["operation_capture_preimage"]
            if (not isinstance(capture, dict) or capture.get("source_role") != role or
                    envelope["body_sha256"] != digest(canonical_bytes(capture))):
                raise Refusal("controller journal preparation capture refused")
            raw = canonical_bytes(envelope)
            journal.envelopes.append(envelope)
            journal._bytes += len(raw)
            previous = digest(raw)
        if journal._bytes > journal.MAX_BYTES:
            raise Refusal("controller journal preparation prefix too large")
        journal._previous = previous
        return journal
    def reserve(self, estimated_bytes: int) -> None:
        if len(self.envelopes) + 2 > self.MAX_ENVELOPES or self._bytes + estimated_bytes > self.MAX_BYTES:
            raise Refusal("journal capture capacity exhausted before S3 operation")
    def reserve_for_operation(self, preimage: dict[str, Any]) -> None:
        # Reserve the success and failure envelopes before the external action.
        self.reserve(len(canonical_bytes(preimage)) * 2 + 1024)

    def append(self, operation: str, authorization_context: str, body: dict[str, Any], disposition: str) -> None:
        if self._sealed:
            raise Refusal("sealed journal cannot append")
        canonical = canonical_bytes(body)
        envelope = {"schema": "aws_c0_capture_journal_envelope/v1", "producer": self.producer,
                    "operation": operation, "authorization_context": authorization_context,
                    "operation_capture_preimage": body, "body_sha256": digest(canonical),
                    "disposition": disposition, "previous_envelope_sha256": self._previous}
        envelope_bytes = canonical_bytes(envelope)
        if len(self.envelopes) >= self.MAX_ENVELOPES or self._bytes + len(envelope_bytes) > self.MAX_BYTES:
            raise Refusal("journal reservation violated")
        self._previous = digest(envelope_bytes); self.envelopes.append(envelope); self._bytes += len(envelope_bytes)

    def complete(self, operation: str, authorization_context: str, observed: dict[str, Any]) -> None:
        self.append(operation, authorization_context, observed, "OBSERVED_COMPLETE")

    def failed(self, operation: str, authorization_context: str, observed: dict[str, Any]) -> None:
        self.append(operation, authorization_context, observed, "OBSERVED_FAILURE")

    def seal(self) -> tuple[bytes, dict[str, str]]:
        """Seal the finite journal once, without a recursive publication row."""
        if self._sealed:
            raise Refusal("journal sealed more than once")
        if not self.envelopes or len(self.envelopes) > self.MAX_ENVELOPES or self._bytes > self.MAX_BYTES:
            raise Refusal("journal seal bounds refused")
        body = {"schema": "aws_c0_controller_capture_journal/v1", "producer": self.producer,
                "envelopes": self.envelopes, "envelope_count": len(self.envelopes),
                "canonical_envelope_bytes": self._bytes,
                "content_chain_sha256": self._previous}
        raw = canonical_bytes(body)
        if len(raw) > self.MAX_BYTES:
            raise Refusal("sealed journal byte bound refused")
        self._sealed = True
        return raw, identity("aws_c0_controller_capture_journal/v1", digest(raw))


def _execution_receipt(order: int, descriptor_id: str, left: str, right: str,
                       comparison: str, left_value: Any, right_value: Any) -> dict[str, Any]:
    def equal(lhs: Any, rhs: Any) -> bool:
        if isinstance(lhs, list) and not isinstance(rhs, list):
            return bool(lhs) and all(equal(item, rhs) for item in lhs)
        if isinstance(rhs, list) and not isinstance(lhs, list):
            return bool(rhs) and all(equal(lhs, item) for item in rhs)
        return lhs == rhs
    if not equal(left_value, right_value):
        raise Refusal(f"comparison failed: {descriptor_id}")
    left_raw, right_raw = canonical_bytes(left_value), canonical_bytes(right_value)
    domain = "AWS_C0_CLOSED_POINTER_COMPARISON_EXECUTION_RECEIPT_V1_NUL"
    preimage = (domain.encode() + b"\0" + order.to_bytes(8, "big") + descriptor_id.encode() +
                left.encode() + right.encode() + comparison.encode() + len(left_raw).to_bytes(8, "big") +
                bytes.fromhex(digest(left_raw)) + len(right_raw).to_bytes(8, "big") +
                bytes.fromhex(digest(right_raw)) + b"\x01")
    return {
        "schema": "aws_c0_closed_pointer_comparison_execution_receipt/v1",
        "order": order, "descriptor_id": descriptor_id, "left": left, "right": right,
        "comparison": comparison,
        "left_resolved_nonsecret_value_byte_count": len(left_raw),
        "left_resolved_nonsecret_value_sha256": digest(left_raw),
        "right_resolved_nonsecret_value_byte_count": len(right_raw),
        "right_resolved_nonsecret_value_sha256": digest(right_raw),
        "raw_secret_or_bearer_token_bytes_present": False, "comparison_result": True,
        "receipt_hash_domain": domain,
        "receipt_hash_formula": "SHA256(DOMAIN_UTF8_CONCAT_ORDER_INT64BE_CONCAT_DESCRIPTOR_ID_UTF8_CONCAT_LEFT_POINTER_EXPRESSION_UTF8_CONCAT_RIGHT_POINTER_EXPRESSION_UTF8_CONCAT_COMPARISON_ALGORITHM_UTF8_CONCAT_LEFT_RESOLVED_RFC8785_CANONICAL_NONSECRET_VALUE_BYTE_COUNT_INT64BE_CONCAT_LEFT_RESOLVED_RFC8785_CANONICAL_NONSECRET_VALUE_SHA256_CONCAT_RIGHT_RESOLVED_RFC8785_CANONICAL_NONSECRET_VALUE_BYTE_COUNT_INT64BE_CONCAT_RIGHT_RESOLVED_RFC8785_CANONICAL_NONSECRET_VALUE_SHA256_CONCAT_COMPARISON_RESULT_BYTE)",
        "receipt_sha256": digest(preimage),
        "receipt_disposition": "POINTER_EXPRESSIONS_RESOLVED_AGAINST_THE_DECLARED_COMPLETE_ENCLOSING_PREIMAGE_OR_RECORD_SECRET_OPERANDS_RESOLVED_ONLY_AS_AUTHORIZED_HASH_AND_COUNT_VALUES_COMPARISON_EXECUTED_TRUE_AND_DOMAIN_SEPARATED_RECEIPT_RECOMPUTED_PASS",
    }


def _attempt_prefix_for_journal(key: str) -> str:
    if not key.endswith(CONTROLLER_JOURNAL_SUFFIX):
        raise Refusal("controller journal key refused")
    prefix = key[:-len(CONTROLLER_JOURNAL_SUFFIX)]
    if not re.fullmatch(r"rehearsal/aws-c0/[A-Za-z0-9._-]+/[A-Za-z0-9._-]+/", prefix):
        raise Refusal("controller journal attempt prefix refused")
    return prefix


def _typed_publication_receipt(*, attempt_identity: dict[str, str], bucket: str, key: str,
                               raw: bytes, content_chain_sha256: str,
                               observed: dict[str, Any]) -> dict[str, Any]:
    object_receipt = {
        "key": key, "version_id": observed["version_id"], "etag": observed["etag"],
        "checksum_sha256_base64": observed["checksum_sha256_base64"],
        "byte_count": len(raw), "sha256": digest(raw),
    }
    serialization = _execution_receipt(
        1, "JOURNAL_PREPUBLICATION_EXACT_SERIALIZATION_001",
        "AUTHENTICATED_JOURNAL_BODY_/journal_content_projection_byte_count,/journal_content_projection_sha256,/journal_content_projection_hash_domain,/journal_content_projection_hash_formula,/journal_prepublication_size_guard_receipts_in_order,RUNTIME_PREPUBLICATION_EPHEMERAL_RFC8785_SERIALIZATION_BUFFER_/byte_count,/sha256",
        "/byte_count,/published_object_sha256,/object_receipt/byte_count,/object_receipt/sha256",
        "RUNTIME_GUARD_EXECUTED_BEFORE_PUT;EXACT_COMPLETE_RFC8785_JOURNAL_BYTES_SERIALIZED_ONCE;ACTUAL_BYTE_COUNT_LTE_1048576;EXACT_BUFFER_SHA256_AND_BYTE_COUNT_EQUAL_SIGNED_PUT_PAYLOAD_AND_AUTHENTICATED_VERSIONED_OBJECT_RECEIPT",
        [len(raw), digest(raw)], [len(raw), digest(raw)])
    domain = "AWS_C0_CAPTURE_JOURNAL_PUBLICATION_RECEIPT_BODY_V1_NUL"
    core = {
        "schema": "aws_c0_capture_journal_publication_receipt/v1", "journal_role": "CONTROLLER",
        "bucket_name": bucket, "key": key, "if_none_match": "*",
        "version_id": observed["version_id"], "etag": observed["etag"],
        "checksum_sha256_base64": observed["checksum_sha256_base64"],
        "byte_count": len(raw), "published_object_sha256": digest(raw),
        "content_chain_sha256": content_chain_sha256,
        "object_receipt_identity": identity("aws_c0_s3_object_receipt/v1", digest(canonical_bytes(object_receipt))),
        "object_receipt": object_receipt, "excluded_from_recursive_capture_scope": True,
        "publication_disposition": "ONE_EXACT_KEY_CONDITIONAL_NO_REPLACE_VERSIONED_JOURNAL_PUBLICATION_BOUND_PASS",
        "attempt_identity": attempt_identity, "attempt_prefix": _attempt_prefix_for_journal(key),
        "attempt_role_key_cross_binding_disposition": "ATTEMPT_IDENTITY_PREFIX_ROLE_AND_EXACT_DERIVED_JOURNAL_KEY_EQUAL_PASS",
        "programme_count_class": "NON_SEMANTIC_CAPTURE_CHANNEL_AUXILIARY",
        "published_object_cross_binding_disposition": "AUTHENTICATED_EXACT_VERSION_OBJECT_BYTES_HAVE_ACTUAL_COMPLETE_RAW_BYTE_COUNT_LTE_1048576_AND_RAW_SHA256_EQUAL_PUBLISHED_OBJECT_SHA256;ETAG_CHECKSUM_VERSION_KEY_ROLE_AND_CONTENT_CHAIN_COORDINATES_MATCH_PASS",
        "prepublication_exact_serialization_execution_receipt": serialization,
        "receipt_hash_domain": domain,
        "receipt_hash_formula": "SHA256(DOMAIN_UTF8_CONCAT_RFC8785_CANONICAL_COMPLETE_CAPTURE_JOURNAL_PUBLICATION_RECEIPT_WITH_RECEIPT_SHA256_RECEIPT_BODY_BYTE_COUNT_RECEIPT_BODY_EXCLUDED_FIELDS_IN_ORDER_AND_RECEIPT_BODY_PROJECTION_DISPOSITION_REMOVED)",
    }
    body = canonical_bytes(core)
    return {**core, "receipt_sha256": digest(domain.encode() + b"\0" + body),
            "receipt_body_byte_count": len(body),
            "receipt_body_excluded_fields_in_order": ["receipt_sha256", "receipt_body_byte_count", "receipt_body_excluded_fields_in_order", "receipt_body_projection_disposition"],
            "receipt_body_projection_disposition": "DIRECT_RFC8785_CANONICAL_BODY_IS_COMPLETE_CAPTURE_JOURNAL_PUBLICATION_RECEIPT_WITH_EXACT_FOUR_DERIVED_BODY_FIELDS_REMOVED;DIRECT_BODY_BYTE_COUNT_AND_DOMAIN_SEPARATED_RECEIPT_SHA256_RECOMPUTE_PASS"}


def _typed_readback_receipt(*, attempt_identity: dict[str, str], bucket: str, key: str,
                            raw: bytes, content_chain_sha256: str,
                            observed: dict[str, Any]) -> dict[str, Any]:
    domain = "AWS_C0_CAPTURE_JOURNAL_READBACK_RECEIPT_BODY_V1_NUL"
    core = {
        "schema": "aws_c0_capture_journal_readback_receipt/v1", "journal_role": "CONTROLLER",
        "bucket_name": bucket, "key": key, "version_id": observed["version_id"],
        "etag": observed["etag"], "checksum_sha256_base64": observed["checksum_sha256_base64"],
        "byte_count": len(raw), "published_object_sha256": digest(raw),
        "content_chain_sha256": content_chain_sha256, "excluded_from_recursive_capture_scope": True,
        "exact_version_and_content_disposition": "EXACT_KEY_VERSION_ETAG_CHECKSUM_BYTES_AND_SHA_MATCH_PUBLICATION_RECEIPT_PASS",
        "attempt_identity": attempt_identity, "attempt_prefix": _attempt_prefix_for_journal(key),
        "attempt_role_key_cross_binding_disposition": "ATTEMPT_IDENTITY_PREFIX_ROLE_AND_EXACT_DERIVED_JOURNAL_KEY_EQUAL_PASS",
        "programme_count_class": "NON_SEMANTIC_CAPTURE_CHANNEL_AUXILIARY",
        "published_object_cross_binding_disposition": "AUTHENTICATED_EXACT_VERSION_OBJECT_BYTES_HAVE_ACTUAL_COMPLETE_RAW_BYTE_COUNT_LTE_1048576_AND_RAW_SHA256_EQUAL_PUBLISHED_OBJECT_SHA256;ETAG_CHECKSUM_VERSION_KEY_ROLE_AND_CONTENT_CHAIN_COORDINATES_MATCH_PASS",
        "receipt_hash_domain": domain,
        "receipt_hash_formula": "SHA256(DOMAIN_UTF8_CONCAT_RFC8785_CANONICAL_COMPLETE_CAPTURE_JOURNAL_READBACK_RECEIPT_WITH_RECEIPT_SHA256_RECEIPT_BODY_BYTE_COUNT_RECEIPT_BODY_EXCLUDED_FIELDS_IN_ORDER_AND_RECEIPT_BODY_PROJECTION_DISPOSITION_REMOVED)",
    }
    body = canonical_bytes(core)
    return {**core, "receipt_sha256": digest(domain.encode() + b"\0" + body),
            "receipt_body_byte_count": len(body),
            "receipt_body_excluded_fields_in_order": ["receipt_sha256", "receipt_body_byte_count", "receipt_body_excluded_fields_in_order", "receipt_body_projection_disposition"],
            "receipt_body_projection_disposition": "DIRECT_RFC8785_CANONICAL_BODY_IS_COMPLETE_CAPTURE_JOURNAL_READBACK_RECEIPT_WITH_EXACT_FOUR_DERIVED_BODY_FIELDS_REMOVED;DIRECT_BODY_BYTE_COUNT_AND_DOMAIN_SEPARATED_RECEIPT_SHA256_RECOMPUTE_PASS"}


def publish_and_readback_controller_journal(*, journal: CaptureJournal, bucket: str, key: str,
                                            attempt_identity: dict[str, str], publisher: Any,
                                            readback: Any) -> tuple[dict[str, str], dict[str, Any]]:
    """Publish exactly one sealed journal and verify its exact-version readback.

    Publisher/readback are explicit injected SigV4 operation seams.  Their
    production adapters own signed transport; the journal never records its
    own Put/Get, which keeps the capture graph finite and acyclic.
    """
    raw, journal_identity = journal.seal()
    receipt = publisher(bucket, key, raw)
    required = {"key", "version_id", "etag", "bytes", "sha256", "checksum_sha256_base64"}
    if not isinstance(receipt, dict) or set(receipt) != required or receipt["key"] != key or \
       receipt["bytes"] != len(raw) or receipt["sha256"] != digest(raw) or not VERSION.fullmatch(receipt["version_id"]):
        raise Refusal("controller journal publication receipt refused")
    read_raw, read_receipt = readback(bucket, key, receipt["version_id"])
    read_required = required | {"request_id"}
    if (read_raw != raw or not isinstance(read_receipt, dict) or
            set(read_receipt) != read_required or read_receipt["key"] != key or
            read_receipt["version_id"] != receipt["version_id"] or
            read_receipt["etag"] != receipt["etag"] or
            read_receipt["bytes"] != receipt["bytes"] or
            read_receipt["sha256"] != digest(raw) or
            read_receipt["checksum_sha256_base64"] != receipt["checksum_sha256_base64"]):
        raise Refusal("controller journal exact-version readback refused")
    journal_body = strict_json(raw)
    publication = _typed_publication_receipt(
        attempt_identity=attempt_identity, bucket=bucket, key=key, raw=raw,
        content_chain_sha256=journal_body["content_chain_sha256"], observed=receipt)
    typed_readback = _typed_readback_receipt(
        attempt_identity=attempt_identity, bucket=bucket, key=key, raw=read_raw,
        content_chain_sha256=journal_body["content_chain_sha256"], observed=read_receipt)
    publication_identity = identity("aws_c0_capture_journal_publication_receipt/v1",
                                    publication["receipt_sha256"])
    readback_identity = identity("aws_c0_capture_journal_readback_receipt/v1",
                                 typed_readback["receipt_sha256"])
    return journal_identity, {"schema": "aws_c0_controller_journal_authenticated_readback/v1",
                              "content_chain_sha256": journal_body["content_chain_sha256"],
                              "publication_receipt": publication,
                              "publication_receipt_identity": publication_identity,
                              "readback_receipt": typed_readback,
                              "readback_receipt_identity": readback_identity}


def _pointer_value(record: dict[str, Any], expression: str) -> Any:
    values: list[Any] = []
    for pointer in expression.split(","):
        if not pointer.startswith("/"):
            values.append(pointer)
            continue
        value: Any = record
        for token in pointer[1:].split("/"):
            if not isinstance(value, dict) or token not in value:
                raise Refusal(f"unresolved comparison pointer: {pointer}")
            value = value[token]
        values.append(value)
    return values[0] if len(values) == 1 else values


def build_controller_journal_handoff_v1(*, attempt_identity: dict[str, str], bucket: str,
                                        journal_identity: dict[str, str],
                                        authenticated_readback: dict[str, Any]) -> dict[str, Any]:
    """Build the fixed-key acyclic carrier consumed by the finalizer.

    The carrier contains the already observed controller journal VersionId and
    publication-receipt identity.  It deliberately contains no coordinate or
    receipt for its own future PutObject.
    """
    if not BUCKET.fullmatch(bucket) or attempt_identity.get("sha256") != attempt_identity.get("value"):
        raise Refusal("controller handoff attempt/bucket refused")
    if journal_identity.get("kind") != "aws_c0_controller_capture_journal/v1" or \
       journal_identity.get("sha256") != journal_identity.get("value"):
        raise Refusal("controller handoff journal identity refused")
    expected_readback_fields = {
        "schema", "content_chain_sha256", "publication_receipt", "publication_receipt_identity",
        "readback_receipt", "readback_receipt_identity",
    }
    if not isinstance(authenticated_readback, dict) or set(authenticated_readback) != expected_readback_fields or \
       authenticated_readback.get("schema") != "aws_c0_controller_journal_authenticated_readback/v1":
        raise Refusal("controller handoff authenticated readback refused")
    publication = authenticated_readback["publication_receipt"]
    readback = authenticated_readback["readback_receipt"]
    publication_identity = authenticated_readback["publication_receipt_identity"]
    readback_identity = authenticated_readback["readback_receipt_identity"]
    if (not isinstance(publication, dict) or not isinstance(readback, dict) or
            publication.get("schema") != "aws_c0_capture_journal_publication_receipt/v1" or
            readback.get("schema") != "aws_c0_capture_journal_readback_receipt/v1" or
            publication.get("journal_role") != "CONTROLLER" or readback.get("journal_role") != "CONTROLLER" or
            publication.get("attempt_identity") != attempt_identity or readback.get("attempt_identity") != attempt_identity or
            publication.get("version_id") != readback.get("version_id") or
            publication.get("key") != readback.get("key") or
            publication.get("etag") != readback.get("etag") or
            publication.get("byte_count") != readback.get("byte_count") or
            publication.get("published_object_sha256") != readback.get("published_object_sha256") or
            publication.get("content_chain_sha256") != readback.get("content_chain_sha256") or
            publication.get("checksum_sha256_base64") != readback.get("checksum_sha256_base64") or
            not VERSION.fullmatch(str(publication.get("version_id", ""))) or
            not SHA.fullmatch(str(publication.get("published_object_sha256", "")))):
        raise Refusal("controller handoff publication/readback coordinates refused")
    expected_publication_identity = identity("aws_c0_capture_journal_publication_receipt/v1",
                                             publication["receipt_sha256"])
    expected_readback_identity = identity("aws_c0_capture_journal_readback_receipt/v1",
                                          readback["receipt_sha256"])
    if publication_identity != expected_publication_identity or readback_identity != expected_readback_identity:
        raise Refusal("controller handoff receipt reference refused")
    chain = authenticated_readback["content_chain_sha256"]
    if not SHA.fullmatch(str(chain)):
        raise Refusal("controller handoff content chain refused")
    controller_object = {
        "bucket": bucket, "key": publication["key"],
        "version_id": publication["version_id"], "etag": publication["etag"],
        "checksum_sha256_base64": publication["checksum_sha256_base64"],
        "byte_count": publication["byte_count"],
        "object_sha256": publication["published_object_sha256"],
        "content_chain_sha256": chain,
    }
    comparison_root = {
        "attempt_identity": attempt_identity, "controller_journal_object": controller_object,
        "controller_publication_receipt": publication, "controller_readback_receipt": readback,
        "controller_publication_receipt_identity": publication_identity,
        "controller_readback_receipt_identity": readback_identity,
    }
    receipts = [_execution_receipt(index, *row,
                                   _pointer_value(comparison_root, row[1]),
                                   _pointer_value(comparison_root, row[2]))
                for index, row in enumerate(CONTROLLER_HANDOFF_COORDINATE_ROWS, 1)]
    local_preimage = {**comparison_root,
                      "coordinate_receipt_sha256s": [row["receipt_sha256"] for row in receipts]}
    local_sha = digest(canonical_bytes(local_preimage))
    core = {
        "schema": "controller_journal_handoff_v1", "attempt_identity": attempt_identity,
        "controller_journal_object": controller_object,
        "controller_publication_receipt": publication,
        "controller_readback_receipt": readback,
        "controller_publication_receipt_identity": publication_identity,
        "controller_readback_receipt_identity": readback_identity,
        "controller_local_validation_receipt_identity": identity(
            "aws_c0_controller_journal_local_validation_receipt/v1", local_sha),
        "controller_local_validation_receipt_sha256": local_sha,
        "controller_receipt_coordinate_execution_receipts_in_order": receipts,
        "zero_science_counters": ZERO,
        "handoff_hash_domain": HANDOFF_HASH_DOMAIN,
        "handoff_hash_formula": "SHA256(DOMAIN_UTF8_CONCAT_RFC8785_CANONICAL_COMPLETE_CONTROLLER_JOURNAL_HANDOFF_V1_WITH_EXACT_FIVE_DERIVED_FIELDS_REMOVED)",
        "handoff_identity_recomputation_disposition": "HANDOFF_IDENTITY_SHA256_AND_VALUE_AND_HANDOFF_CANONICAL_SHA256_ALL_EQUAL_RECOMPUTED_DOMAIN_SEPARATED_CANONICAL_BODY_DIGEST_PASS",
    }
    body_raw = canonical_bytes(core)
    handoff_sha = digest(HANDOFF_HASH_DOMAIN.encode() + b"\0" + body_raw)
    return {
        **core,
        "handoff_canonical_body_byte_count": len(body_raw),
        "handoff_body_excluded_fields_in_order": list(HANDOFF_EXCLUDED_FIELDS),
        "handoff_body_projection_disposition": "RFC8785_CANONICAL_COMPLETE_CLOSED_HANDOFF_BODY_WITH_EXACT_FIVE_DERIVED_FIELDS_REMOVED_RECOMPUTES_BYTES_AND_SHA256_NO_SELF_HASH_FIXED_POINT_PASS",
        "handoff_identity": identity("aws_c0_controller_journal_handoff/v1", handoff_sha),
        "handoff_canonical_sha256": handoff_sha,
    }


def publish_controller_journal_handoff(*, bucket: str, key: str,
                                       handoff: dict[str, Any], publisher: Any) -> dict[str, Any]:
    """Conditionally publish the sole fixed-key carrier after journal readback."""
    if not key.endswith("/" + CONTROLLER_JOURNAL_HANDOFF_SUFFIX):
        raise Refusal("controller journal handoff key refused")
    raw = canonical_bytes(handoff)
    receipt = publisher(bucket, key, raw)
    required = {"key", "version_id", "etag", "bytes", "sha256", "checksum_sha256_base64"}
    if (not isinstance(receipt, dict) or set(receipt) != required or
            receipt["key"] != key or receipt["bytes"] != len(raw) or
            receipt["sha256"] != digest(raw) or
            not VERSION.fullmatch(str(receipt["version_id"]))):
        raise Refusal("controller journal handoff publication refused")
    return receipt


def _root_record(schema: str, fields: dict[str, Any]) -> tuple[dict[str, Any], bytes, str]:
    record = {
        "schema": schema, "authority_id": AUTHORITY_ID,
        "record_class": "NON_SCIENTIFIC_AWS_C0_EVIDENCE",
        "scientific_execution_authorized": False,
        "stage_f_readiness_claimed": False,
        "zero_science_counters": ZERO,
        "observed_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        **fields,
    }
    if schema == "aws_c0_start_receipt/v7":
        record["correction_authority_id"] = CORRECTION_ID
        record["closure_correction_authority_id"] = CLOSURE_ID
        record["stage_f_execution_authorized"] = False
    record_id = digest(canonical_bytes(record))
    record["record_sha256"] = record_id
    raw = canonical_bytes(record)
    return record, raw, record_id


def _status_directory_fd(*, create: bool = False) -> int:
    """Pin the existing root-owned state directory and its private status child.

    StateDirectory survives service exit; RuntimeDirectory does not. Descriptor
    relative operations refuse symlink substitution and never chmod a target.
    """
    if os.geteuid() != 0:
        raise Refusal("local status access requires root")
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    parent = os.open(STATUS.parent, flags)
    try:
        info = os.fstat(parent)
        if not stat.S_ISDIR(info.st_mode) or info.st_uid != 0 or stat.S_IMODE(info.st_mode) != 0o700:
            raise Refusal("state directory must be root-owned mode 0700")
        if create:
            try: os.mkdir(STATUS.name, mode=0o700, dir_fd=parent)
            except FileExistsError: pass
        child = os.open(STATUS.name, flags, dir_fd=parent)
        try:
            info = os.fstat(child)
            if not stat.S_ISDIR(info.st_mode) or info.st_uid != 0 or stat.S_IMODE(info.st_mode) != 0o700:
                raise Refusal("status directory must be root-owned mode 0700")
        except BaseException:
            os.close(child)
            raise
        return child
    finally:
        os.close(parent)


def _publish_status(path: Path, payload: dict[str, Any]) -> None:
    if path.parent != STATUS or path.suffix != '.json' or not ATTEMPT.fullmatch(path.stem):
        raise Refusal("local status path is not exact")
    raw = canonical_bytes(payload)
    if len(raw) > 16384:
        raise Refusal("local status publication exceeds bound")
    temporary = path.name + '.' + os.urandom(16).hex()
    directory = _status_directory_fd(create=True)
    created = False
    try:
        fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                     0o600, dir_fd=directory)
        created = True
        with os.fdopen(fd, 'wb') as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path.name, src_dir_fd=directory, dst_dir_fd=directory)
        created = False
        os.fsync(directory)
    finally:
        try:
            if created: os.unlink(temporary, dir_fd=directory)
        finally:
            os.close(directory)


def read_local_operational_status(*, launch: dict[str, Any], workflow_execution_arn: str) -> dict[str, Any]:
    """Read one pinned private status file, not evidence authentication.

    Missing status is not successful completion. Callers must separately bind
    the launch/workflow, validate helper authority/freshness, and authenticate
    actual published evidence during closure. No directory is created here.
    """
    expected = new_local_operational_status(launch, workflow_execution_arn)
    directory = _status_directory_fd()
    try:
        fd = os.open(expected['attempt_id'] + '.json', os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                     dir_fd=directory)
        try:
            before = os.fstat(fd)
            if (not stat.S_ISREG(before.st_mode) or before.st_uid != 0
                    or stat.S_IMODE(before.st_mode) != 0o600 or before.st_nlink != 1
                    or not 1 <= before.st_size <= 16384):
                raise Refusal("local status requires one private bounded regular file")
            with os.fdopen(fd, 'rb', closefd=False) as handle:
                raw = handle.read(16385)
            after = os.fstat(fd)
            attributes = ('st_dev','st_ino','st_mode','st_uid','st_nlink','st_size','st_mtime_ns','st_ctime_ns')
            if len(raw) != before.st_size or any(getattr(before,k) != getattr(after,k) for k in attributes):
                raise Refusal("local status changed during bounded read")
        finally:
            os.close(fd)
    finally:
        os.close(directory)
    return validate_local_operational_status(strict_json(raw), launch=launch, workflow_execution_arn=workflow_execution_arn)


LOCAL_STATUS_FIELDS = {'schema', 'attempt_id', 'attempt_identity', 'workflow_execution_arn',
    'workflow_execution_identity', 'launch_request_identity', 'artifact_prefix', 'start',
    'heartbeat_zero', 'latest_heartbeat', 'terminal', 'controller_journal_handoff_complete', 'zero_science_counters'}


def new_local_operational_status(launch: dict[str, Any], workflow_execution_arn: str) -> dict[str, Any]:
    """An operational cache, not an authenticated root or extra S3 object."""
    if launch.get('schema') != 'aws_c0_launch_request/v7':
        raise Refusal("local status requires the current validated launch kind")
    launch_id = root_digest(launch)
    _identity_field(launch, 'attempt_identity', 'aws_c0_attempt/v1')
    if (not ATTEMPT.fullmatch(launch['attempt_id']) or not REHEARSAL.fullmatch(launch['rehearsal_id'])
            or launch['artifact_prefix'] != 'rehearsal/aws-c0/' + launch['rehearsal_id'] + '/' + launch['attempt_id'] + '/'):
        raise Refusal("local status attempt coordinates invalid")
    if (not workflow_execution_arn.startswith('arn:aws:states:us-east-1:623609441658:execution:')
            or not workflow_execution_arn.endswith(':' + launch['attempt_id'])):
        raise Refusal("local status workflow/attempt mismatch")
    return {'schema':'aws_c0_controller_operational_status/v2','attempt_id':launch['attempt_id'],
        'attempt_identity':launch['attempt_identity'],'workflow_execution_arn':workflow_execution_arn,
        'workflow_execution_identity':_workflow_identity(workflow_execution_arn),
        'launch_request_identity':identity('aws_c0_launch_request/v7',launch_id),'artifact_prefix':launch['artifact_prefix'],
        'start':None,'heartbeat_zero':None,'latest_heartbeat':None,'terminal':None,
        'controller_journal_handoff_complete':False,'zero_science_counters':dict(ZERO)}


def validate_local_operational_status(value: Any, *, launch: dict[str, Any], workflow_execution_arn: str) -> dict[str, Any]:
    expected = new_local_operational_status(launch, workflow_execution_arn)
    if not isinstance(value, dict) or set(value) != LOCAL_STATUS_FIELDS or len(canonical_bytes(value)) > 16384:
        raise Refusal("closed bounded local operational status required")
    variable = {'start','heartbeat_zero','latest_heartbeat','terminal','controller_journal_handoff_complete'}
    if any(value[k] != expected[k] for k in LOCAL_STATUS_FIELDS - variable):
        raise Refusal("local operational status source binding mismatch")
    if any(type(x) is not int for x in value['zero_science_counters'].values()):
        raise Refusal("local status counters must be exact integer zeros")
    if type(value['controller_journal_handoff_complete']) is not bool:
        raise Refusal("local status handoff flag must be boolean")
    roles = {'start':('aws_c0_start_receipt/v7','start'),
        'heartbeat_zero':('aws_c0_heartbeat/v1','heartbeat'),'latest_heartbeat':('aws_c0_heartbeat/v1','heartbeat'),
        'terminal':('aws_c0_terminal_receipt/v1','terminal')}
    for field,(kind,category) in roles.items():
        item = value[field]
        if item is None: continue
        if not isinstance(item,dict) or set(item) != {'identity','object','observed_utc','sequence'}:
            raise Refusal("local status root projection not closed")
        rid = _identity_field(item,'identity',kind)
        obj = item['object']
        if (not isinstance(obj,dict) or set(obj) != {'key','version_id','bytes','sha256','checksum_sha256_base64'}
                or obj['key'] != value['artifact_prefix']+'evidence/'+category+'-'+rid+'.json'
                or not isinstance(obj['version_id'],str) or not VERSION.fullmatch(obj['version_id'])
                or type(obj['bytes']) is not int or not 1 <= obj['bytes'] <= MAX_OBJECT_BYTES
                or not isinstance(obj['sha256'],str) or not SHA.fullmatch(obj['sha256'])
                or obj['checksum_sha256_base64'] != base64.b64encode(bytes.fromhex(obj['sha256'])).decode()):
            raise Refusal("local status exact publication coordinate invalid")
        if not isinstance(item['observed_utc'],str) or not re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z',item['observed_utc']):
            raise Refusal("local status exact UTC required")
        _utc(item['observed_utc'])
        if category == 'heartbeat':
            if type(item['sequence']) is not int or not 0 <= item['sequence'] < 512:
                raise Refusal("local heartbeat sequence outside capture bound")
        elif item['sequence'] is not None: raise Refusal("non-heartbeat local sequence must be null")
    start,zero,last,terminal=(value[k] for k in ('start','heartbeat_zero','latest_heartbeat','terminal'))
    if start is None and any(x is not None for x in (zero,last,terminal)):
        raise Refusal("local status roots precede accepted start")
    if (zero is None) != (last is None) or zero is not None and (zero['sequence'] != 0
            or _utc(zero['observed_utc']) < _utc(start['observed_utc'])
            or _utc(last['observed_utc']) < _utc(zero['observed_utc'])
            or last['sequence'] == 0 and last != zero
            or last['sequence'] > 0 and last['identity'] == zero['identity']):
        raise Refusal("local status heartbeat-zero/last binding invalid")
    if terminal is not None and (last is None or _utc(terminal['observed_utc']) < _utc(last['observed_utc'])):
        raise Refusal("local terminal precedes heartbeat evidence")
    if value['controller_journal_handoff_complete'] and terminal is None:
        raise Refusal("local journal handoff cannot precede terminal")
    return value


def advance_local_operational_status(status: dict[str, Any], root_bytes: bytes, publication: dict[str, Any], *,
                                     launch: dict[str, Any], workflow_execution_arn: str) -> dict[str, Any]:
    """Called only after a successful persistent-controller root publication.

    It binds root identity separately from published-byte hash, retains heartbeat
    zero, and accepts only the next published heartbeat or one terminal root.
    It performs no I/O and makes no independent authentication claim.
    """
    validate_local_operational_status(status,launch=launch,workflow_execution_arn=workflow_execution_arn)
    if status['terminal'] is not None: raise Refusal("local status already has terminal publication")
    record = strict_json(root_bytes)
    if not isinstance(record, dict) or not isinstance(publication, dict):
        raise Refusal("published root and publication receipt must be objects")
    rid = root_digest(record)
    if (record.get('attempt_identity') != status['attempt_identity'] or record.get('zero_science_counters') != ZERO
            or record.get('authority_id') != AUTHORITY_ID or record.get('record_class') != 'NON_SCIENTIFIC_AWS_C0_EVIDENCE'
            or record.get('scientific_execution_authorized') is not False or record.get('stage_f_readiness_claimed') is not False):
        raise Refusal("published local status root attempt/science mismatch")
    if any(type(x) is not int for x in record['zero_science_counters'].values()):
        raise Refusal("published root counters must be integer zeros")
    kind = record.get('schema')
    if kind == 'aws_c0_start_receipt/v7':
        if (status['start'] is not None or record.get('start_disposition') != 'AWS_C0_START_ACCEPTED'
                or record.get('failure_phase') is not None or record.get('failure_code') is not None
                or record.get('workflow_execution_identity') != status['workflow_execution_identity']
                or record.get('workflow_execution_arn') != workflow_execution_arn
                or record.get('launch_request_identity') != status['launch_request_identity']):
            raise Refusal("local accepted start binding invalid")
        field,category,sequence='start','start',None
    elif kind == 'aws_c0_heartbeat/v1':
        last=status['latest_heartbeat']
        if (status['start'] is None or type(record.get('sequence')) is not int
                or record['sequence'] != (0 if last is None else last['sequence']+1)
                or record.get('previous_heartbeat_identity') != (None if last is None else last['identity'])
                or last is not None and _utc(record['observed_utc']) < _utc(last['observed_utc'])):
            raise Refusal("local heartbeat publication chain invalid")
        field,category,sequence='latest_heartbeat','heartbeat',record['sequence']
    elif kind == 'aws_c0_terminal_receipt/v1':
        last=status['latest_heartbeat']
        if (last is None or type(record.get('last_heartbeat_sequence')) is not int
                or record['last_heartbeat_sequence'] != last['sequence']
                or record.get('disposition') not in ('AWS_C0_SYNTHETIC_PASS','AWS_C0_SYNTHETIC_FAIL')):
            raise Refusal("local terminal publication sequence invalid")
        field,category,sequence='terminal','terminal',None
    else: raise Refusal("unsupported local operational status root")
    expected_key=status['artifact_prefix']+'evidence/'+category+'-'+rid+'.json'
    if (publication.get('key') != expected_key or publication.get('sha256') != digest(root_bytes)
            or publication.get('bytes') != len(root_bytes)
            or publication.get('checksum_sha256_base64') != base64.b64encode(hashlib.sha256(root_bytes).digest()).decode()):
        raise Refusal("local status does not bind actual published root bytes")
    result=json.loads(canonical_bytes(status))
    result[field]={'identity':identity(kind,rid),'object':{k:publication[k] for k in
        ('key','version_id','bytes','sha256','checksum_sha256_base64')},'observed_utc':record['observed_utc'],'sequence':sequence}
    if field == 'latest_heartbeat' and sequence == 0: result['heartbeat_zero']=result[field]
    return validate_local_operational_status(result,launch=launch,workflow_execution_arn=workflow_execution_arn)


def build_local_status_response(request: dict[str, Any], status: Any, *, context: dict[str, Any],
                                now: dt.datetime) -> dict[str, Any]:
    """A bounded operational response, never a synthetic pass or evidence root."""
    launch=context['launch'];start=context['expected_start_dispatch']
    validate_local_helper_request_v1(request,semantic_parameters=start['semantic_parameters'],
        expected_start_dispatch=start,attempt_deadline_utc=context['attempt_deadline_utc'],now=now)
    if request['operation'] != 'STATUS':
        raise Refusal('status helper cannot execute another operation')
    state='WAITING_FOR_START';age=None
    if status is not None:
        validate_local_operational_status(status,launch=launch,workflow_execution_arn=context['workflow_execution_arn'])
        for key in ('start','heartbeat_zero','latest_heartbeat','terminal'):
            if status[key] is not None and _utc(status[key]['observed_utc']) > now:
                raise Refusal('local status contains a future publication timestamp')
        if status['start'] is not None: state='WAITING_FOR_HEARTBEAT'
        heartbeat=status['latest_heartbeat']
        if heartbeat is not None:
            elapsed=(now-_utc(heartbeat['observed_utc'])).total_seconds();age=int(elapsed)
            state='HEARTBEAT_STALE' if elapsed >= launch['phase_timeouts_seconds']['heartbeat_stale'] else 'RUNNING'
        if status['terminal'] is not None:
            state='TERMINAL_AWAITING_JOURNAL_HANDOFF'
        if status['controller_journal_handoff_complete']:
            state='CONTROLLER_HANDOFF_COMPLETE'
    result={'schema':'aws_c0_controller_local_status_response/v1','operation':'STATUS',
        'helper_request_identity':identity('aws_c0_controller_local_helper_request/v1',digest(canonical_bytes(request))),
        'attempt_identity':launch['attempt_identity'],'workflow_execution_identity':_workflow_identity(context['workflow_execution_arn']),
        'observed_utc':now.isoformat(timespec='seconds').replace('+00:00','Z'),'state':state,
        'heartbeat_age_seconds':age,'status':status,'authentication_disposition':'LOCAL_OPERATIONAL_ONLY_NOT_AUTHENTICATED_EVIDENCE',
        'synthetic_outcome_claimed':False,'zero_science_counters':dict(ZERO)}
    if len(canonical_bytes(result)) > 20000:
        raise Refusal('status helper response exceeds SSM inline output bound')
    return result


def execute_local_status_helper(args: argparse.Namespace, *, now: dt.datetime | None = None) -> dict[str, Any]:
    request=_decode_ssm_transport(args)
    if not isinstance(request,dict) or request.get('operation') != 'STATUS':
        raise Refusal('status entry point refuses START and SAFE_CLOSE')
    context=load_local_helper_context(args)
    current=now or dt.datetime.now(dt.timezone.utc)
    validate_local_helper_transport_v1(args,expected_start_dispatch=context['expected_start_dispatch'],
        attempt_deadline_utc=context['attempt_deadline_utc'],now=current)
    try:
        status=read_local_operational_status(launch=context['launch'],workflow_execution_arn=context['workflow_execution_arn'])
    except FileNotFoundError:
        status=None
    return build_local_status_response(request,status,context=context,now=current)


def build_local_safe_close_marker(request: dict[str, Any], status: Any, *, context: dict[str, Any],
                                   now: dt.datetime) -> dict[str, Any]:
    """Request safe-close evidence while healthy; do not stop the controller.

    The workflow continues after this observation request. The later closure
    must prove its accepted readiness and actual cleanup independently.
    """
    start=context['expected_start_dispatch'];launch=context['launch']
    validate_local_helper_request_v1(request,semantic_parameters=start['semantic_parameters'],
        expected_start_dispatch=start,attempt_deadline_utc=context['attempt_deadline_utc'],now=now)
    if request['operation'] != 'SAFE_CLOSE':
        raise Refusal('safe-close helper refuses other operations')
    validate_local_operational_status(status,launch=launch,workflow_execution_arn=context['workflow_execution_arn'])
    if status['start'] is None or status['heartbeat_zero'] is None or status['terminal'] is not None:
        raise Refusal('safe-close intent requires accepted start and heartbeat zero without terminal')
    if any(_utc(status[k]['observed_utc']) > now for k in ('start','heartbeat_zero','latest_heartbeat')):
        raise Refusal('safe-close intent cannot use future status')
    stale=launch['phase_timeouts_seconds']['heartbeat_stale']
    if any((now-_utc(status[k]['observed_utc'])).total_seconds() >= stale for k in ('heartbeat_zero','latest_heartbeat')):
        raise Refusal('safe-close observation requires fresh heartbeat-zero and latest heartbeat')
    marker={'schema':'aws_c0_controller_local_safe_close_marker/v1','operation':'SAFE_CLOSE',
        'attempt_identity':launch['attempt_identity'],'workflow_execution_identity':_workflow_identity(context['workflow_execution_arn']),
        'helper_request_identity':identity('aws_c0_controller_local_helper_request/v1',digest(canonical_bytes(request))),
        'request_disposition':'LOCAL_SAFE_CLOSE_OBSERVATION_REQUESTED',
        'observed_utc':now.isoformat(timespec='seconds').replace('+00:00','Z'),
        'start_identity':status['start']['identity'],'heartbeat_zero_identity':status['heartbeat_zero']['identity'],
        'latest_heartbeat_identity':status['latest_heartbeat']['identity'],
        'status_sha256':digest(canonical_bytes(status)),'safe_close_completed':False,'synthetic_outcome_claimed':False,
        'authentication_disposition':'LOCAL_OPERATIONAL_ONLY_NOT_AUTHENTICATED_EVIDENCE','zero_science_counters':dict(ZERO)}
    if len(canonical_bytes(marker)) > 4096:
        raise Refusal('local safe-close marker exceeds bound')
    return marker


def _write_local_safe_close_marker(attempt: str, marker: dict[str, Any]) -> None:
    if not isinstance(attempt,str) or not ATTEMPT.fullmatch(attempt):
        raise Refusal('local safe-close attempt path invalid')
    raw=canonical_bytes(marker)
    if len(raw) > 4096:
        raise Refusal('local safe-close marker exceeds bound')
    directory=_status_directory_fd();name=attempt+'.safe-close.json';created=False
    try:
        fd=os.open(name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=directory)
        created=True
        with os.fdopen(fd,'wb') as handle:
            handle.write(raw);handle.flush();os.fsync(handle.fileno())
        os.fsync(directory)
    except BaseException:
        if created:os.unlink(name,dir_fd=directory)
        raise
    finally:
        os.close(directory)


def execute_local_safe_close_helper(args: argparse.Namespace, *, now: dt.datetime | None = None) -> dict[str, Any]:
    request=_decode_ssm_transport(args)
    if not isinstance(request,dict) or request.get('operation') != 'SAFE_CLOSE':
        raise Refusal('safe-close entry point refuses START and STATUS')
    context=load_local_helper_context(args);current=now or dt.datetime.now(dt.timezone.utc)
    validate_local_helper_transport_v1(args,expected_start_dispatch=context['expected_start_dispatch'],
        attempt_deadline_utc=context['attempt_deadline_utc'],now=current)
    status=read_local_operational_status(launch=context['launch'],workflow_execution_arn=context['workflow_execution_arn'])
    marker=build_local_safe_close_marker(request,status,context=context,now=current)
    _write_local_safe_close_marker(args.attempt_id,marker)
    return {'schema':'aws_c0_controller_local_safe_close_response/v1','operation':'SAFE_CLOSE',
        'marker_identity':identity(marker['schema'],digest(canonical_bytes(marker))),'marker':marker,
        'marker_written':True,'safe_close_completed':False}


def _software_contract(live_packet: dict[str, Any]) -> dict[str, Any]:
    matches = [item for item in live_packet.get("runtime_control_preimages", [])
               if isinstance(item, dict) and item.get("control_kind") == "SOFTWARE_AND_IMAGE_SET"]
    if len(matches) != 1:
        raise Refusal("exact software/image preimage absent")
    item = matches[0]
    try:
        raw = base64.b64decode(item["canonical_json_base64"], validate=True)
    except (KeyError, ValueError) as exc:
        raise Refusal("software preimage encoding invalid") from exc
    contract = strict_json(raw)
    required = {"schema", "controller_identity", "service_identity", "image_identity", "image_reference",
                "container_runtime_policy_identity"}
    if not isinstance(contract, dict) or set(contract) != required or contract["schema"] != "aws_c0_software_image_set/v1":
        raise Refusal("software preimage is not closed")
    if item.get("identity") != identity("aws_c0_software_image_set/v1", digest(raw)):
        raise Refusal("software preimage identity mismatch")
    return contract


def _verify_software(live_packet: dict[str, Any]) -> dict[str, Any]:
    contract = _software_contract(live_packet)
    if digest(_file_secure(CONTROLLER)) != _identity_field(contract, "controller_identity", "aws_c0_controller_software/v1"):
        raise Refusal("installed controller mismatch")
    if digest(_file_secure(UNIT)) != _identity_field(contract, "service_identity", "aws_c0_service_unit/v1"):
        raise Refusal("installed unit mismatch")
    policy_id = digest(canonical_bytes(RUNTIME_POLICY))
    if policy_id != _identity_field(contract, "container_runtime_policy_identity", "aws_c0_container_runtime_policy/v1"):
        raise Refusal("runtime policy mismatch")
    image_reference = contract["image_reference"]
    if not isinstance(image_reference, str) or not re.fullmatch(r"[^\s@]+@sha256:[0-9a-f]{64}", image_reference):
        raise Refusal("image reference is not immutable")
    if contract["image_identity"] != identity("oci_image_digest/v1", image_reference.rsplit(":", 1)[-1]):
        raise Refusal("image identity mismatch")
    # Docker .Id is the image configuration digest, not the repository's OCI
    # manifest digest. Preserve the immutable reference binding through the
    # local RepoDigests mapping; never substitute an ID for a manifest digest.
    raw_inspection = _run([DOCKER, "image", "inspect", image_reference], 30).stdout
    if len(raw_inspection) > MAX_OBJECT_BYTES:
        raise Refusal("preloaded image inspection exceeds bound")
    try:
        inspected = json.loads(raw_inspection, object_pairs_hook=_pairs,
                               parse_constant=lambda _: (_ for _ in ()).throw(Refusal("nonfinite image metadata")))
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise Refusal("invalid image inspection JSON") from exc
    if not isinstance(inspected, list) or len(inspected) != 1 or not isinstance(inspected[0], dict):
        raise Refusal("preloaded image inspection is not singular")
    image = inspected[0]
    references = image.get("RepoDigests")
    if (not isinstance(references, list) or not all(isinstance(item, str) for item in references)
            or image_reference not in references):
        raise Refusal("preloaded repository manifest digest not exact")
    if (not isinstance(image.get("Id"), str) or not re.fullmatch(r"sha256:[0-9a-f]{64}", image["Id"])
            or image.get("Os") != "linux" or image.get("Architecture") != "amd64"):
        raise Refusal("preloaded image configuration or platform mismatch")
    return contract


def run_attempt(args: argparse.Namespace) -> None:
    request_path = Path(args.launch_request)
    if request_path.parent != REQUESTS or request_path.suffix != ".json" or request_path.name.endswith(".source.json"):
        raise Refusal("invalid local request path")
    launch_raw = _file_secure(request_path)
    source_raw = _file_secure(request_path.with_suffix(".source.json"))
    launch = strict_json(launch_raw)
    source = strict_json(source_raw)
    if not isinstance(source, dict) or set(source) != OPERATIONAL_SOURCE_FIELDS or source.get("schema") != "aws_c0_source_sidecar/v5":
        raise Refusal("invalid source sidecar")
    attempt = source.get("attempt_id")
    rehearsal = source.get("rehearsal_id")
    launch = validate_launch(launch, rehearsal, attempt)
    if digest(launch_raw) != source.get("launch_sha256") or len(launch_raw) != source.get("launch_bytes") or launch["artifact_prefix"] != source.get("artifact_prefix"):
        raise Refusal("local source binding mismatch")
    mode = _mode(attempt)
    bucket = source["artifact_bucket"]
    prefix = launch["artifact_prefix"]
    launch_id = root_digest(launch)
    limits = launch["cost_envelope"]["resource_limits"]
    journal = CaptureJournal.restore("EC2_INSTANCE_PROFILE_CONTROLLER",
                                     source["declared_exact_version_source_get_captures_in_order"])
    credentials = bootstrap_imdsv2_credentials()
    credential_provider = lambda: credentials
    exact_launch, _ = _download(bucket, source["launch_key"], source["launch_version_id"], source["launch_sha256"],
                                journal=journal, source_role="RUNTIME_LAUNCH_REQUEST_V5",
                                credential_provider=credential_provider)
    live_raw, _ = _download(bucket, source["live_packet_key"], source["live_packet_version_id"], source["live_packet_sha256"],
                            journal=journal, source_role="RUNTIME_LIVE_PACKET_V5",
                            credential_provider=credential_provider)
    auth_raw, _ = _download(bucket, source["live_authorization_key"], source["live_authorization_version_id"], source["live_authorization_sha256"],
                            journal=journal, source_role="RUNTIME_LIVE_AUTHORIZATION_V5",
                            credential_provider=credential_provider)
    if exact_launch != launch_raw or len(live_raw) != source["live_packet_bytes"] or len(auth_raw) != source["live_authorization_bytes"]:
        raise Refusal("exact-version replay bytes mismatch")
    live_packet = strict_json(live_raw); live_auth = strict_json(auth_raw)
    if live_packet.get("schema") != "aws_c0_live_packet/v7" or live_auth.get("schema") != "aws_c0_live_authorization/v7":
        raise Refusal("runtime control schema mismatch")
    put_count = 0

    def put(key: str, raw: bytes) -> dict[str, Any]:
        nonlocal put_count
        if put_count + 1 > limits["s3_put_requests"]:
            raise Refusal("sealed S3 put maximum exceeded")
        requested = dt.datetime.now(dt.timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")
        capture = {"operation": "S3_PUT_OBJECT", "bucket": bucket, "key": key,
                   "payload_byte_count": len(raw), "payload_sha256": digest(raw),
                   "source_object_identity": identity("aws_c0_s3_object/v1", digest(raw)),
                   "operation_requested_utc": requested,
                   "request_envelope_sha256": digest(canonical_bytes({
                       "method": "PUT", "bucket": bucket, "key": key,
                       "if_none_match": "*", "payload_sha256": digest(raw)}))}
        journal.reserve_for_operation(capture)
        try:
            receipt = _s3_put(bucket, key, raw)
            capture.update({"observed_version_id": receipt["version_id"],
                            "observed_checksum_sha256": receipt["checksum_sha256_base64"],
                            "observed_sha256": receipt["sha256"],
                            "observed_bytes": receipt["bytes"],
                            "operation_completed_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")})
            journal.complete("S3_PUT_OBJECT", "EC2_INSTANCE_PROFILE", capture)
            put_count += 1
            return receipt
        except Exception as exc:
            capture.update({"failure_class": type(exc).__name__,
                            "operation_completed_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")})
            journal.failed("S3_PUT_OBJECT", "EC2_INSTANCE_PROFILE", capture)
            raise
    claim = {
        "schema": "aws_c0_attempt_claim/v3",
        "attempt_identity": launch["attempt_identity"],
        "launch_request_identity": identity("aws_c0_launch_request/v7", launch_id),
        "live_packet_identity": identity("aws_c0_live_packet/v7", source["live_packet_sha256"]),
        "live_authorization_identity": source["live_authorization_identity"],
        "closure_seed_identity": launch["closure_seed_identity"],
        "workflow_execution_identity": source["workflow_execution_identity"],
        "ssm_command_identity": source["ssm_command_identity"],
        "artifact_prefix": prefix, "zero_science_counters": ZERO,
    }
    claim_raw = canonical_bytes(claim)
    claim_sha = digest(claim_raw)
    put(f"{prefix}control/attempt-claim-{claim_sha}.json", claim_raw)
    software = _verify_software(live_packet)
    invocation_id = os.environ.get("INVOCATION_ID", "")
    if not re.fullmatch(r"[0-9a-f]{32}", invocation_id):
        raise Refusal("systemd invocation ID absent")
    systemd_id = identity("systemd_unit_invocation/v1", digest(canonical_bytes({
        "schema": "systemd_unit_invocation/v1", "attempt_id": attempt,
        "invocation_id": invocation_id, "service_identity": software["service_identity"],
        "ssm_command_identity": source["ssm_command_identity"],
    })))
    container_name = "ebu-c0-" + attempt.lower().replace("_", "-")
    container_id = identity("oci_container_instance/v1", digest(canonical_bytes({
        "schema": "oci_container_instance/v1", "attempt_id": attempt, "container_name": container_name,
        "image_identity": software["image_identity"], "runtime_policy": RUNTIME_POLICY,
    })))
    bucket_identity = launch["closure_seed_object"]["bucket_identity"]
    def exact_receipt(label: str) -> dict[str, Any]:
        return {"bucket_identity": bucket_identity, "key": source[label + "_key"],
            "version_id": source[label + "_version_id"], "bytes": source[label + "_bytes"],
            "sha256": source[label + "_sha256"],
            "checksum_sha256_base64": base64.b64encode(bytes.fromhex(source[label + "_sha256"])).decode()}
    start, start_raw, start_id = _root_record("aws_c0_start_receipt/v7", {
        "attempt_identity": launch["attempt_identity"],
        "launch_request_identity": identity("aws_c0_launch_request/v7", launch_id),
        "launch_request_object": exact_receipt("launch"),
        "live_packet_identity": identity("aws_c0_live_packet/v7", source["live_packet_sha256"]),
        "live_packet_object": exact_receipt("live_packet"),
        "live_authorization_identity": source["live_authorization_identity"],
        "live_authorization_object": exact_receipt("live_authorization"),
        "closure_seed_identity": launch["closure_seed_identity"],
        "closure_seed_object": launch["closure_seed_object"],
        "workflow_execution_identity": source["workflow_execution_identity"],
        "workflow_execution_arn": source["workflow_execution_arn"],
        "ssm_command_identity": source["ssm_command_identity"],
        "systemd_invocation_identity": systemd_id,
        "container_identity": container_id,
        "runtime_attestation_identities": [software["controller_identity"], software["service_identity"], software["image_identity"]],
        "instance_id": INSTANCE_ID,
        "attempt_claim_identity": identity("aws_c0_attempt_claim/v3", claim_sha),
        "start_disposition": "AWS_C0_START_ACCEPTED",
        "failure_phase": None, "failure_code": None,
    })
    start_publication = put(f"{prefix}evidence/start-{start_id}.json", start_raw)
    operational_status = advance_local_operational_status(
        new_local_operational_status(launch,source['workflow_execution_arn']),start_raw,start_publication,
        launch=launch,workflow_execution_arn=source['workflow_execution_arn'])
    _publish_status(STATUS / f"{attempt}.json", operational_status)
    max_runtime = min(launch["phase_timeouts_seconds"]["worker_runtime"], limits["instance_running_seconds"])
    cidfile = ATTEMPTS / f"{attempt}.cid"
    ATTEMPTS.mkdir(parents=True, mode=0o700, exist_ok=True)
    if cidfile.exists() or cidfile.is_symlink():
        raise Refusal("container claim file already exists")
    argv = [DOCKER, "run", "--rm", "--pull", "never", "--name", container_name,
            "--cidfile", str(cidfile), "--network", "none", "--read-only",
            "--security-opt", "no-new-privileges", "--cap-drop", "ALL",
            "--user", "65534:65534", "--pids-limit", "64", "--memory", "268435456",
            "--cpus", "1", "--tmpfs", "/tmp:rw,noexec,nosuid,size=16777216",
            "--env", f"AWS_C0_ATTEMPT_ID={attempt}", "--env", f"AWS_C0_MODE={mode}",
            "--env", f"AWS_C0_HEARTBEAT_SECONDS={launch['heartbeat_interval_seconds']}",
            "--env", f"AWS_C0_CHECKPOINT_SECONDS={launch['checkpoint_interval_seconds']}",
            software["image_reference"]]
    process = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, shell=False,
                               env={"PATH": "/usr/bin:/bin", "LC_ALL": "C"})
    deadline = time.monotonic() + max_runtime
    terminal_seen = False
    terminal_disposition: str | None = None
    previous_heartbeat: dict[str, str] | None = None
    previous_checkpoint: dict[str, str] | None = None
    heartbeat_count = 0
    checkpoint_count = 0
    try:
        assert process.stdout is not None
        for line in _bounded_lines(process.stdout, process, deadline):
            if not line.endswith(b"\n") or line.endswith(b"\r\n"):
                raise Refusal("worker event framing invalid")
            event_raw = line[:-1]
            event = strict_json(event_raw)
            if not isinstance(event, dict):
                raise Refusal("worker event must be an object")
            kind = event.get("event")
            if kind == "heartbeat":
                if set(event) != {"event", "sequence", "monotonic_nanoseconds", "payload_sha256"}:
                    raise Refusal("heartbeat event is not closed")
                if type(event["sequence"]) is not int or event["sequence"] < 0 or type(event["monotonic_nanoseconds"]) is not int or event["monotonic_nanoseconds"] < 0 or not SHA.fullmatch(str(event["payload_sha256"])):
                    raise Refusal("heartbeat event values invalid")
                expected_payload = digest(canonical_bytes({"attempt_id": attempt, "event": "heartbeat",
                                                           "mode": mode, "sequence": event["sequence"]}))
                if event["sequence"] != heartbeat_count or event["payload_sha256"] != expected_payload:
                    raise Refusal("heartbeat sequence/payload mismatch")
                schema, category = "aws_c0_heartbeat/v1", "heartbeat"
                fields = {"attempt_identity": claim["attempt_identity"],
                          "sequence": event["sequence"],
                          "monotonic_nanoseconds": event["monotonic_nanoseconds"],
                          "previous_heartbeat_identity": previous_heartbeat,
                          "payload_sha256": event["payload_sha256"]}
            elif kind == "checkpoint":
                if set(event) != {"event", "sequence", "synthetic_progress_units", "payload_sha256"}:
                    raise Refusal("checkpoint event is not closed")
                if type(event["sequence"]) is not int or event["sequence"] < 0 or type(event["synthetic_progress_units"]) is not int or event["synthetic_progress_units"] < 0 or not SHA.fullmatch(str(event["payload_sha256"])):
                    raise Refusal("checkpoint event values invalid")
                checkpoint_payload = canonical_bytes({"attempt_id": attempt, "event": "checkpoint",
                    "mode": mode, "sequence": event["sequence"],
                    "synthetic_progress_units": event["synthetic_progress_units"]})
                expected_payload = digest(checkpoint_payload)
                if event["sequence"] != checkpoint_count or event["synthetic_progress_units"] != checkpoint_count + 1 or event["payload_sha256"] != expected_payload:
                    raise Refusal("checkpoint sequence/payload mismatch")
                payload_receipt = put(f"{prefix}payload/checkpoint-{expected_payload}.json", checkpoint_payload)
                schema, category = "aws_c0_checkpoint/v1", "checkpoint"
                fields = {"attempt_identity": claim["attempt_identity"],
                          "sequence": event["sequence"],
                          "synthetic_progress_units": event["synthetic_progress_units"],
                          "previous_checkpoint_identity": previous_checkpoint,
                          "object_receipt": {key: payload_receipt[key]
                                             for key in ("key", "version_id", "bytes", "sha256")}}
            elif kind == "terminal":
                expected_terminal = {"event", "disposition", "failure_phase", "failure_code",
                                     "last_heartbeat_sequence", "last_checkpoint_sequence",
                                     "synthetic_manifest_sha256"}
                if set(event) != expected_terminal or event["disposition"] not in {"AWS_C0_SYNTHETIC_PASS", "AWS_C0_SYNTHETIC_FAIL"}:
                    raise Refusal("terminal event is invalid")
                if event["last_heartbeat_sequence"] != heartbeat_count - 1 or event["last_checkpoint_sequence"] != checkpoint_count - 1:
                    raise Refusal("terminal sequences mismatch")
                if event["disposition"] == "AWS_C0_SYNTHETIC_PASS":
                    manifest_payload = canonical_bytes({"attempt_id": attempt,
                        "checkpoint_count": checkpoint_count, "heartbeat_count": heartbeat_count,
                        "mode": "SUCCESS", "schema": "aws_c0_synthetic_manifest_payload/v1",
                        "synthetic_progress_units": checkpoint_count})
                    expected_manifest = digest(manifest_payload)
                    if mode != "SUCCESS" or event["failure_phase"] != "NONE" or event["failure_code"] is not None or event["synthetic_manifest_sha256"] != expected_manifest:
                        raise Refusal("success terminal closure mismatch")
                    put(f"{prefix}payload/synthetic-manifest-{expected_manifest}.json", manifest_payload)
                    manifest_identity: dict[str, str] | None = identity("aws_c0_synthetic_manifest/v1", expected_manifest)
                else:
                    if mode != "FAIL_AFTER_CHECKPOINT" or event["failure_phase"] != "WORKER" or event["failure_code"] != "DECLARED_FAIL_AFTER_CHECKPOINT" or event["synthetic_manifest_sha256"] is not None:
                        raise Refusal("failure terminal closure mismatch")
                    manifest_identity = None
                schema, category = "aws_c0_terminal_receipt/v1", "terminal"
                fields = {"attempt_identity": claim["attempt_identity"],
                          "disposition": event["disposition"], "failure_phase": event["failure_phase"],
                          "failure_code": event["failure_code"],
                          "last_heartbeat_sequence": event["last_heartbeat_sequence"],
                          "last_checkpoint_sequence": event["last_checkpoint_sequence"],
                          "synthetic_manifest_identity": manifest_identity}
                terminal_disposition = event["disposition"]
            else:
                raise Refusal("worker emitted unsupported event")
            _, raw, record_id = _root_record(schema, fields)
            root_publication = put(f"{prefix}evidence/{category}-{record_id}.json", raw)
            if schema != 'aws_c0_checkpoint/v1':
                operational_status = advance_local_operational_status(operational_status,raw,root_publication,
                    launch=launch,workflow_execution_arn=source['workflow_execution_arn'])
                _publish_status(STATUS / f"{attempt}.json", operational_status)
            if schema == "aws_c0_heartbeat/v1":
                previous_heartbeat = identity(schema, record_id)
                heartbeat_count += 1
            elif schema == "aws_c0_checkpoint/v1":
                previous_checkpoint = identity(schema, record_id)
                checkpoint_count += 1
            else:
                terminal_seen = True
        remaining = max(1, int(deadline - time.monotonic()))
        code = process.wait(timeout=remaining)
    except Exception:
        _run([DOCKER, "stop", "--time", "10", container_name], 20, ok=(0, 1))
        _run([DOCKER, "kill", container_name], 15, ok=(0, 1))
        process.kill()
        process.wait(timeout=10)
        raise
    finally:
        cidfile.unlink(missing_ok=True)
    expected_exit = 0 if terminal_disposition == "AWS_C0_SYNTHETIC_PASS" else 23
    if code != expected_exit or not terminal_seen:
        raise Refusal("worker failed without durable terminal receipt")
    # The terminal result Put above is the last substantive controller S3
    # operation. These three calls are the finite publication exceptions.
    journal_bytes: dict[str, bytes] = {}
    def journal_publisher(publish_bucket: str, publish_key: str, publish_raw: bytes) -> dict[str, Any]:
        journal_bytes[publish_key] = publish_raw
        return sigv4_conditional_journal_put(publish_bucket, publish_key, publish_raw,
                                              credentials, dt.datetime.now(dt.timezone.utc))
    def journal_readback(read_bucket: str, read_key: str,
                         read_version: str) -> tuple[bytes, dict[str, Any]]:
        expected_raw = journal_bytes.get(read_key)
        if expected_raw is None:
            raise Refusal("journal readback before publication")
        returned_raw, metadata = sigv4_exact_version_get(
            read_bucket, read_key, read_version, digest(expected_raw), credentials,
            https_exact_version_transport, dt.datetime.now(dt.timezone.utc))
        return returned_raw, {"key": read_key, "version_id": metadata["version_id"],
                              "etag": metadata["etag"], "bytes": len(returned_raw),
                              "sha256": digest(returned_raw),
                              "checksum_sha256_base64": metadata["checksum_sha256"],
                              "request_id": metadata["request_id"]}
    journal_identity, journal_readback_receipt = publish_and_readback_controller_journal(
        journal=journal, bucket=bucket, key=prefix + CONTROLLER_JOURNAL_SUFFIX,
        attempt_identity=launch["attempt_identity"],
        publisher=journal_publisher, readback=journal_readback)
    handoff = build_controller_journal_handoff_v1(
        attempt_identity=launch["attempt_identity"], bucket=bucket,
        journal_identity=journal_identity, authenticated_readback=journal_readback_receipt)
    publish_controller_journal_handoff(
        bucket=bucket, key=prefix + CONTROLLER_JOURNAL_HANDOFF_SUFFIX,
        handoff=handoff, publisher=journal_publisher)
    operational_status['controller_journal_handoff_complete'] = True
    validate_local_operational_status(operational_status,launch=launch,workflow_execution_arn=source['workflow_execution_arn'])
    _publish_status(STATUS / f"{attempt}.json", operational_status)


def parser() -> argparse.ArgumentParser:
    top = argparse.ArgumentParser()
    commands = top.add_subparsers(dest="command", required=True)
    prep = commands.add_parser("prepare-request-v4")
    legacy = commands.add_parser("prepare-request-v3")
    helper = commands.add_parser("local-status-v1")
    close_helper = commands.add_parser("local-safe-close-v1")
    classifier = commands.add_parser("classify-dispatch-v1")
    for flag in ("bucket", "region", "artifact-prefix", "launch-key", "launch-version-id", "launch-sha256",
                 "live-packet-key", "live-packet-version-id", "live-packet-sha256",
                 "live-authorization-key", "live-authorization-version-id", "live-authorization-sha256",
                 "rehearsal-id", "attempt-id",
                 "workflow-execution-arn", "ssm-client-request-token", "ssm-expected-command-not-before-utc",
                 "ssm-expected-command-not-after-utc", "ssm-dispatch-request-canonical-json-base64", "ssm-dispatch-request-sha256"):
        for command in (prep,legacy,helper,close_helper,classifier):command.add_argument("--" + flag, required=True)
    for command in (prep,legacy):command.add_argument('--output',required=True)
    for flag in ("launch-bytes", "live-packet-bytes", "live-authorization-bytes"):
        for command in (prep,legacy,helper,close_helper,classifier):command.add_argument("--" + flag, required=True, type=int)
    run = commands.add_parser("run")
    run.add_argument("--launch-request", required=True)
    return top


def main(argv: list[str] | None = None) -> int:
    try:
        args = parser().parse_args(argv)
        if args.command in {"prepare-request-v3", "prepare-request-v4"}:
            prepare_request(args)
        elif args.command == 'classify-dispatch-v1':
            print(classify_local_dispatch(args))
        elif args.command in ('local-status-v1','local-safe-close-v1'):
            response=(execute_local_status_helper(args) if args.command == 'local-status-v1' else execute_local_safe_close_helper(args))
            sys.stdout.buffer.write(canonical_bytes(response)+b'\n')
            sys.stdout.buffer.flush()
        else:
            run_attempt(args)
        return 0
    except (Refusal, OSError, subprocess.SubprocessError, ValueError, KeyError) as exc:
        print(f"AWS_C0_REFUSAL:{type(exc).__name__}:{exc}", file=sys.stderr)
        return 64


if __name__ == "__main__":
    raise SystemExit(main())
