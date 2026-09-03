"""AWS-C0 packet verifier, observer, and durable closure Lambda.

This module deliberately uses only Python's standard library. It implements
the small SigV4 surface needed for exact-version S3 reads/appends and read-only
EC2/IAM/CloudFormation preflight. It never starts or stops an instance; the
Standard workflow owns the single start and non-reentrant stop request.
"""

from __future__ import annotations

import base64
import datetime as dt
import hashlib
import hmac
import json
import os
import re
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from typing import Any

CONTROLLER_JOURNAL_SUFFIX = "evidence/controller-capture-journal.json"
CONTROLLER_JOURNAL_HANDOFF_SUFFIX = "evidence/controller-capture-journal-handoff.json"
FINALIZER_JOURNAL_SUFFIX = "evidence/finalizer-capture-journal.json"
HANDOFF_HASH_DOMAIN = "AWS_C0_CONTROLLER_JOURNAL_HANDOFF_V1_BODY_NUL"
HANDOFF_EXCLUDED_FIELDS = (
    "handoff_identity", "handoff_canonical_sha256",
    "handoff_canonical_body_byte_count", "handoff_body_excluded_fields_in_order",
    "handoff_body_projection_disposition",
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


class CaptureJournal:
    """Finalizer-owned, bounded, acyclic evidence journal.

    The journal is deliberately fed only request/response observations.  A
    reservation is made before an AWS operation and a failure envelope is
    retained if that operation raises, so a later closure record cannot infer
    an unobserved success from a planned coordinate.
    """
    MAX_ENVELOPES = 512
    MAX_BYTES = 1_048_576

    def __init__(self, producer: str = "LAMBDA_FINALIZER_EXECUTION_ROLE") -> None:
        self.producer = producer
        self.envelopes: list[dict[str, Any]] = []
        self._bytes = 0
        self._previous: str | None = None
        self._sealed = False

    def reserve(self, preimage: dict[str, Any]) -> None:
        estimate = len(canonical_bytes(preimage)) * 2 + 1024
        if len(self.envelopes) + 2 > self.MAX_ENVELOPES or self._bytes + estimate > self.MAX_BYTES:
            raise Refusal("finalizer journal capacity exhausted before operation")

    def append(self, operation: str, preimage: dict[str, Any], disposition: str) -> None:
        if self._sealed:
            raise Refusal("sealed finalizer journal cannot append")
        envelope = {"schema": "aws_c0_capture_journal_envelope/v1", "producer": self.producer,
                    "sequence": len(self.envelopes) + 1, "operation": operation,
                    "operation_capture_preimage": preimage, "disposition": disposition,
                    "previous_envelope_sha256": self._previous}
        raw = canonical_bytes(envelope)
        if len(self.envelopes) >= self.MAX_ENVELOPES or self._bytes + len(raw) > self.MAX_BYTES:
            raise Refusal("finalizer journal reservation violated")
        self.envelopes.append(envelope); self._bytes += len(raw); self._previous = digest(raw)

    def aggregate(self) -> dict[str, Any]:
        raw = canonical_bytes(self.envelopes)
        return {"schema": "aws_c0_capture_journal_projection/v1", "producer": self.producer,
                "envelope_count": len(self.envelopes), "envelopes_sha256": digest(raw)}

    def seal(self) -> tuple[bytes, dict[str, str]]:
        if self._sealed or not self.envelopes or len(self.envelopes) > self.MAX_ENVELOPES or self._bytes > self.MAX_BYTES:
            raise Refusal("finalizer journal seal refused")
        raw = canonical_bytes({"schema": "aws_c0_finalizer_capture_journal/v1", "producer": self.producer,
                               "envelopes": self.envelopes, "envelope_count": len(self.envelopes),
                               "canonical_envelope_bytes": self._bytes,
                               "content_chain_sha256": self._previous})
        if len(raw) > self.MAX_BYTES:
            raise Refusal("finalizer journal seal byte bound refused")
        self._sealed = True
        return raw, identity("aws_c0_finalizer_capture_journal/v1", digest(raw))


def build_three_coordinate_capture_aggregate(*, attempt_identity: dict[str, str],
                                             handoff: dict[str, Any],
                                             carrier_observation: dict[str, Any],
                                             finalizer_journal_identity: dict[str, str],
                                             finalizer_readback: dict[str, Any],
                                             finalizer_projection: dict[str, Any],
                                             finalizer_journal: CaptureJournal,
                                             final_manifest_identity: dict[str, str],
                                             final_manifest_receipt: dict[str, Any],
                                             final_manifest_put_response: dict[str, Any],
                                             final_manifest_preimage: dict[str, Any],
                                             publication_observation: dict[str, Any],
                                             publication_observation_identity: dict[str, str],
                                             retrieval_identity: dict[str, str],
                                             retrieval_receipt: dict[str, Any]) -> dict[str, Any]:
    """Construct the accepted fixed-size 100-field capture aggregate."""
    return _build_accepted_capture_aggregate(
        attempt_identity=attempt_identity, handoff=handoff,
        carrier_observation=carrier_observation,
        finalizer_journal_identity=finalizer_journal_identity,
        finalizer_readback=finalizer_readback,
        finalizer_projection=finalizer_projection,
        finalizer_journal=finalizer_journal,
        final_manifest_identity=final_manifest_identity,
        final_manifest_receipt=final_manifest_receipt,
        final_manifest_put_response=final_manifest_put_response,
        final_manifest_preimage=final_manifest_preimage,
        publication_observation=publication_observation,
        publication_observation_identity=publication_observation_identity,
        retrieval_identity=retrieval_identity,
        retrieval_receipt=retrieval_receipt)

def publish_and_readback_finalizer_journal(*, journal: CaptureJournal, bucket: str, key: str,
                                           publisher: Any, readback: Any) -> tuple[dict[str, str], dict[str, Any]]:
    """One conditional journal publication followed by its exact-version readback."""
    raw, journal_identity = journal.seal()
    receipt = publisher(bucket, key, raw)
    required = {"key", "version_id", "etag", "bytes", "sha256", "checksum_sha256_base64"}
    if not isinstance(receipt, dict) or set(receipt) != required or receipt["key"] != key or \
       receipt["bytes"] != len(raw) or receipt["sha256"] != digest(raw) or not VERSION.fullmatch(receipt["version_id"]):
        raise Refusal("finalizer journal publication refused")
    returned, observed = readback(bucket, key, receipt["version_id"])
    if (returned != raw or not isinstance(observed, dict) or
            set(observed) != required | {"request_id"} or
            any(receipt[name] != observed[name] for name in required) or
            observed["sha256"] != digest(raw)):
        raise Refusal("finalizer journal exact-version readback refused")
    publication_identity = identity(
        "aws_c0_capture_journal_publication_receipt/v1",
        digest(canonical_bytes({"bucket_name": bucket, **receipt})),
    )
    readback_identity = identity(
        "aws_c0_capture_journal_readback_receipt/v1",
        digest(canonical_bytes({"bucket_name": bucket, **observed})),
    )
    return journal_identity, {
        "schema": "aws_c0_journal_authenticated_readback/v1",
        "content_chain_sha256": strict_json(raw)["content_chain_sha256"],
        "publication_receipt": receipt,
        "publication_receipt_identity": publication_identity,
        "readback_receipt": observed,
        "readback_receipt_identity": readback_identity,
    }


# This binding is populated only for one closure invocation.  It records a
# reservation before every authenticated request and never retains credentials
# or authorization headers.
_ACTIVE_JOURNAL: CaptureJournal | None = None


AUTHORITY_ID = "EBU-AWS-C0-UNATTENDED-SYNTHETIC-REHEARSAL-AUTHORITY-v1"
CORRECTION_ID = "EBU-AWS-C0-LIVE-PREPARATION-CHOREOGRAPHY-CORRECTION-AUTHORITY-v1"
CLOSURE_ID = "EBU-AWS-C0-COST-RUNTIME-RETRIEVAL-CLOSURE-CORRECTION-AUTHORITY-v1"
REGION = "us-east-1"
INSTANCE_ID = "i-048bac00bdb540a4e"
MAX_BYTES = 4_194_304
SHA = re.compile(r"^[0-9a-f]{64}$")
VERSION = re.compile(r"^[A-Za-z0-9._+~=/:-]{1,1024}$")
BUCKET = re.compile(r"^(?=.{3,63}$)[a-z0-9][a-z0-9-]*[a-z0-9]$")
FROZEN_PRELIVE_OBJECT_COUNT = 21
EXECUTION = re.compile(r"^arn:aws:states:us-east-1:[0-9]{12}:execution:[A-Za-z0-9+=,.@_-]{1,80}:[A-Za-z0-9+=,.@_-]{1,80}$")
ZERO = {
    "project_runner_import_count": 0, "ebu_framework_import_count": 0,
    "stage_e_harness_import_count": 0, "registered_configuration_count": 0,
    "model_state_advance_count": 0, "trajectory_count": 0,
    "simulation_or_gate_count": 0, "scientific_rng_draw_count": 0,
    "outcome_inspection_count": 0, "scientific_output_count": 0,
}
LIVE_AUTH_FIELDS = {
    "schema", "authority_id", "correction_authority_id", "record_class",
    "scientific_execution_authorized", "stage_f_execution_authorized",
    "stage_f_readiness_claimed", "zero_science_counters", "observed_utc",
    "live_packet_identity", "live_packet_object", "change_set_identity",
    "account_identity", "region", "instance_id", "attempt_identity",
    "live_session_assumer_identity", "execution_operator_role_identity",
    "execution_operator_identity", "execution_session_policy_identity",
    "execution_session_policy_subset_proof_identity", "execution_operator_type",
    "execution_operator_is_root", "execution_session_expires_utc",
    "statement_sha256", "authorization_source_identity", "authorized_actions",
    "denied_actions",
}
LAUNCH_FIELDS = {
    "schema", "authority_id", "correction_authority_id", "record_class",
    "scientific_execution_authorized", "stage_f_execution_authorized",
    "stage_f_readiness_claimed", "zero_science_counters", "observed_utc",
    "record_sha256", "rehearsal_id", "attempt_id", "preparation_packet_identity",
    "preparation_authorization_identity", "account_identity",
    "private_infrastructure_snapshot_identity", "region", "instance_id",
    "required_initial_instance_state", "workflow_identity", "ssm_document_identity",
    "controller_identity", "service_identity", "finalizer_identity", "image_digest",
    "container_runtime_policy_identity", "iam_policy_set_identity",
    "artifact_version_receipts", "s3_prefix", "static_validation_identity",
    "quota_observation_identity", "attempt_deadline_utc", "cleanup_deadline_utc",
    "phase_timeouts_seconds", "heartbeat_interval_seconds", "checkpoint_interval_seconds",
    "cost_envelope", "retry_attempts", "cleanup_path",
}
LIVE_PACKET_FIELDS = {
    "schema", "authority_id", "correction_authority_id", "record_class",
    "scientific_execution_authorized", "stage_f_execution_authorized",
    "stage_f_readiness_claimed", "zero_science_counters", "observed_utc",
    "preparation_packet_identity", "preparation_authorization_identity",
    "preparation_closure_identity", "preparation_closure_object",
    "preparation_disposition", "launch_request", "launch_request_object",
    "change_set_observation", "change_set_effect_api_set_identity",
    "change_set_effect_resource_set_identity", "final_preflight",
    "live_session_assumer_identity", "live_session_assumer_expires_utc",
    "execution_operator_role_identity", "execution_session_policy_identity",
    "live_session_policy_ceiling_identity", "execution_session_policy_subset_proof_identity",
    "execution_operator_type", "execution_operator_is_root",
    "execution_session_max_duration_seconds", "packet_disposition",
}
FINAL_CAPTURE_AGGREGATE_FIELDS = {
    "schema", "attempt_identity", "controller_journal_identity", "controller_journal_byte_count",
    "controller_published_object_sha256", "controller_content_chain_sha256", "controller_journal_version_id", "controller_journal_etag",
    "controller_journal_checksum_sha256_base64", "controller_publication_receipt_identity", "controller_publication_receipt_sha256", "controller_readback_receipt_identity",
    "controller_readback_receipt_sha256", "controller_journal_handoff_identity", "controller_journal_handoff_sha256", "controller_journal_handoff_key",
    "controller_journal_handoff_version_id", "controller_journal_handoff_bucket_name", "controller_journal_handoff_etag", "controller_journal_handoff_checksum_sha256_base64",
    "controller_journal_handoff_byte_count", "controller_journal_handoff_object_sha256", "controller_journal_handoff_external_publication_readback_proof", "controller_journal_handoff_embedded_receipt_preimage_disposition",
    "controller_envelope_count", "controller_aggregate_sha256", "finalizer_journal_identity", "finalizer_journal_byte_count",
    "finalizer_published_object_sha256", "finalizer_content_chain_sha256", "finalizer_journal_version_id", "finalizer_journal_etag",
    "finalizer_journal_checksum_sha256_base64", "finalizer_publication_receipt_identity", "finalizer_publication_receipt_sha256", "finalizer_readback_receipt_identity",
    "finalizer_readback_receipt_sha256", "finalizer_envelope_count", "finalizer_aggregate_sha256", "last_substantive_s3_operation_completed_utc",
    "total_envelope_count", "combined_order_and_hash_chain_sha256", "excluded_evidence_channel_operations_in_order", "all_substantive_s3_operations_present",
    "no_later_substantive_s3_operation", "step_functions_carried_full_history", "full_history_embedded_in_closure_response", "aggregate_disposition",
    "proof_sha256", "proof_body_byte_count", "proof_body_excluded_fields_in_order", "proof_body_projection_disposition",
    "proof_hash_domain", "proof_hash_formula", "fixed_size_identity_and_receipt_hash_binding_receipts_in_order", "fixed_size_identity_and_receipt_hash_binding_disposition",
    "prepare_request_get_capture_aggregate_sha256", "controller_prepare_get_subsequence_cross_binding_receipt", "controller_local_journal_validation_receipt_identity", "controller_local_journal_validation_receipt_sha256",
    "finalizer_local_journal_validation_receipt_identity", "finalizer_local_journal_validation_receipt_sha256", "controller_terminal_result_put_operation_capture_identity", "controller_terminal_result_put_completed_utc",
    "controller_terminal_result_put_membership_receipt", "controller_terminal_receipt_identity", "controller_terminal_receipt_key", "finalizer_terminal_manifest_put_operation_capture_identity",
    "finalizer_terminal_manifest_put_completed_utc", "finalizer_terminal_manifest_put_membership_receipt", "finalizer_terminal_manifest_identity", "finalizer_terminal_manifest_key",
    "lambda_application_release_operation_coverage_receipt", "terminal_operation_cross_binding_receipts_in_order", "controller_aggregate_hash_domain", "controller_aggregate_hash_formula",
    "finalizer_aggregate_hash_domain", "finalizer_aggregate_hash_formula", "combined_aggregate_hash_domain", "combined_aggregate_hash_formula",
    "aggregate_arithmetic_time_and_hash_execution_receipts_in_order", "controller_journal_bucket_name", "controller_journal_key", "finalizer_journal_bucket_name",
    "finalizer_journal_key", "journal_coordinate_receipt_equalities_in_order", "journal_coordinate_receipt_equality_execution_receipts_in_order", "three_key_pairwise_distinctness_execution_receipt",
    "final_manifest_publication_observation_identity", "final_manifest_publication_observation_preimage", "final_manifest_publication_observation_preimage_byte_count", "final_manifest_publication_observation_preimage_sha256",
    "final_manifest_publication_observation_hash_domain", "final_manifest_publication_observation_hash_formula", "final_manifest_canonical_byte_count", "final_manifest_put_response_etag",
    "final_manifest_put_response_x_amz_request_id", "final_manifest_publication_observation_binding_receipts_in_order", "final_manifest_publication_observation_binding_disposition", "preserved_programme_count_disposition",
}
TIMEOUT_FIELDS = {"boot", "ssm_online", "ssm_start_delivery", "heartbeat_stale",
                  "worker_runtime", "finalizer", "instance_stop", "overall"}
RESOURCE_LIMIT_FIELDS = {
    "max_instance_running_seconds", "max_s3_new_bytes", "max_s3_put_requests",
    "max_s3_get_requests", "max_s3_head_requests", "max_s3_list_requests",
    "max_ecr_stored_bytes", "max_cloudwatch_ingested_bytes",
    "max_step_functions_transitions", "max_lambda_invocations",
    "max_lambda_duration_milliseconds", "max_kms_requests", "max_data_transfer_bytes",
    "max_public_ipv4_seconds", "max_nat_gateway_seconds", "max_vpc_endpoint_seconds",
}


class Refusal(RuntimeError):
    """Typed preflight/closure refusal."""


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise Refusal(f"duplicate key: {key}")
        out[key] = value
    return out


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
        raise Refusal("noncanonical value")
    walk(value)
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode()


def strict_json(raw: bytes) -> Any:
    if raw.endswith(b"\n") or raw.endswith(b"\r") or len(raw) > MAX_BYTES:
        raise Refusal("canonical object boundary failed")
    try:
        text = raw.decode("utf-8")
        if unicodedata.normalize("NFC", text) != text:
            raise Refusal("non-NFC JSON")
        value = json.loads(text, object_pairs_hook=_pairs,
                           parse_float=lambda _: (_ for _ in ()).throw(Refusal("float forbidden")),
                           parse_constant=lambda _: (_ for _ in ()).throw(Refusal("nonfinite forbidden")))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise Refusal("invalid JSON") from exc
    if canonical_bytes(value) != raw:
        raise Refusal("noncanonical JSON")
    return value


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def identity(kind: str, value: str) -> dict[str, str]:
    if not SHA.fullmatch(value):
        raise Refusal("invalid identity")
    return {"kind": kind, "sha256": value, "value": value}


def _pointer_value(record: dict[str, Any], expression: str) -> Any:
    values: list[Any] = []
    for pointer in expression.split(","):
        if not pointer.startswith("/"):
            values.append(pointer)
            continue
        value: Any = record
        for token in pointer[1:].split("/"):
            if isinstance(value, list) and token.isdigit():
                value = value[int(token)]
            elif isinstance(value, dict) and token in value:
                value = value[token]
            else:
                raise Refusal(f"unresolved comparison pointer: {pointer}")
        values.append(value)
    return values[0] if len(values) == 1 else values


def _execution_receipt(order: int, descriptor_id: str, left: str, right: str,
                       comparison: str, left_value: Any, right_value: Any,
                       *, comparison_result: bool | None = None) -> dict[str, Any]:
    result = _equal_values(left_value, right_value) if comparison_result is None else comparison_result
    if not result:
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


def _validate_execution_receipt(receipt: Any, order: int, root: dict[str, Any]) -> None:
    fields = {"schema", "order", "descriptor_id", "left", "right", "comparison",
              "left_resolved_nonsecret_value_byte_count", "left_resolved_nonsecret_value_sha256",
              "right_resolved_nonsecret_value_byte_count", "right_resolved_nonsecret_value_sha256",
              "raw_secret_or_bearer_token_bytes_present", "comparison_result", "receipt_hash_domain",
              "receipt_hash_formula", "receipt_sha256", "receipt_disposition"}
    if not isinstance(receipt, dict) or set(receipt) != fields or receipt.get("order") != order:
        raise Refusal("comparison execution receipt fields refused")
    expected = _execution_receipt(order, receipt["descriptor_id"], receipt["left"], receipt["right"],
                                  receipt["comparison"], _pointer_value(root, receipt["left"]),
                                  _pointer_value(root, receipt["right"]))
    if receipt != expected:
        raise Refusal("comparison execution receipt recomputation refused")


def _membership_receipt(*, journal_role: str, journal_object_sha256: str,
                        content_chain_sha256: str, envelopes: list[dict[str, Any]],
                        sequence: int, expected_operation: str, bucket: str, key: str,
                        expected_identity: dict[str, str]) -> dict[str, Any]:
    envelope = envelopes[sequence - 1]
    capture = envelope["operation_capture_preimage"]
    capture_sha = digest(canonical_bytes(capture))
    requested = capture["operation_requested_utc"]
    completed = capture["operation_completed_utc"]
    request_sha = capture["request_envelope_sha256"]
    context = "LIVE_EC2_INSTANCE_PROFILE" if journal_role == "CONTROLLER" else "CLOSURE_LAMBDA_EXECUTION_ROLE"
    domain = "AWS_C0_CAPTURE_JOURNAL_OPERATION_MEMBERSHIP_RECEIPT_V1_NUL"
    core = {
        "schema": "aws_c0_capture_journal_operation_membership_receipt/v1",
        "journal_role": journal_role, "journal_published_object_sha256": journal_object_sha256,
        "journal_content_chain_sha256": content_chain_sha256,
        "journal_envelope_count": len(envelopes), "envelope_sequence": sequence,
        "selected_operation_capture_identity": identity("aws_c0_authenticated_s3_operation_capture/v1", capture_sha),
        "selected_operation_capture_preimage_sha256": capture_sha,
        "selected_request_envelope_sha256": request_sha,
        "expected_source_object_identity": expected_identity,
        "expected_authorization_context_kind": context, "expected_operation": expected_operation,
        "expected_bucket_name": bucket, "expected_key": key,
        "operation_requested_utc": requested, "operation_completed_utc": completed,
        "membership_hash_domain": domain,
        "membership_hash_formula": "SHA256(DOMAIN_UTF8_CONCAT_JOURNAL_PUBLISHED_OBJECT_SHA256_CONCAT_CONTENT_CHAIN_SHA256_CONCAT_INT64BE_ENVELOPE_COUNT_CONCAT_INT64BE_SEQUENCE_CONCAT_OPERATION_CAPTURE_IDENTITY_VALUE_CONCAT_OPERATION_CAPTURE_PREIMAGE_SHA256_CONCAT_REQUEST_ENVELOPE_SHA256_CONCAT_SOURCE_OBJECT_IDENTITY_VALUE_CONCAT_CONTEXT_UTF8_CONCAT_OPERATION_UTF8_CONCAT_BUCKET_UTF8_CONCAT_KEY_UTF8_CONCAT_REQUESTED_UTC_UTF8_CONCAT_COMPLETED_UTC_UTF8)",
        "membership_validation_disposition": "TRANSIENT_EXACT_VERSION_JOURNAL_READBACK_VALIDATED_SEQUENCE_INDEX_SELECTED_OPERATION_IDENTITY_AND_PREIMAGE_HASH_CONTEXT_OPERATION_BUCKET_KEY_REQUESTED_AND_COMPLETED_TIME_WITH_NO_JOURNAL_BYTES_OR_ENVELOPES_EMBEDDED_PASS",
    }
    material = canonical_bytes(core)
    return {**core, "membership_receipt_sha256": digest(domain.encode() + b"\0" + material)}


def _operation_aggregate(envelopes: list[dict[str, Any]], domain: str) -> str:
    rows = [{"sequence": index, "capture_identity": identity(
                "aws_c0_authenticated_s3_operation_capture/v1",
                digest(canonical_bytes(envelope["operation_capture_preimage"]))),
             "preimage_sha256": digest(canonical_bytes(envelope["operation_capture_preimage"])),
             "previous_envelope_sha256": envelope.get("previous_envelope_sha256")}
            for index, envelope in enumerate(envelopes, 1)]
    return digest(domain.encode() + b"\0" + canonical_bytes(rows))


def _capture_projection(capture: dict[str, Any], *, bucket: str, key: str,
                        version_id: str | None, etag: str | None,
                        checksum: str | None, body_byte_count: int,
                        body_sha256: str) -> dict[str, Any]:
    capture_sha = digest(canonical_bytes(capture))
    return {
        "capture_sha256": capture_sha,
        "authorization_credential_access_key_id_extraction_preimage": {
            "sanitized_request_envelope_preimage": {
                "bucket_name": bucket, "object_key": key, "version_id": version_id,
            }
        },
        "response_envelope_preimage": {
            "version_id": version_id, "etag": etag,
            "checksum_sha256_base64": checksum,
            "content_length": body_byte_count, "body_sha256": body_sha256,
            "x_amz_request_id": capture.get("observed_request_id"),
        },
        "operation_requested_utc": capture["operation_requested_utc"],
        "operation_completed_utc": capture["operation_completed_utc"],
        "request_envelope_sha256": capture["request_envelope_sha256"],
    }


def _equal_values(left: Any, right: Any) -> bool:
    if isinstance(left, list) and not isinstance(right, list):
        return bool(left) and all(_equal_values(item, right) for item in left)
    if isinstance(right, list) and not isinstance(left, list):
        return bool(right) and all(_equal_values(left, item) for item in right)
    return left == right


def _execution_rows(root: dict[str, Any], rows: list[tuple[str, str, str, str]],
                    specials: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    special = specials or {}
    result: list[dict[str, Any]] = []
    for order, (descriptor, left, right, comparison) in enumerate(rows, 1):
        left_value = special[left] if left in special else _pointer_value(root, left)
        right_value = special[right] if right in special else _pointer_value(root, right)
        if comparison == "UTC_LESS_THAN_OR_EQUAL":
            passed = _utc(left_value) <= _utc(right_value)
        elif comparison == "INTEGER_SUM_EQUAL":
            passed = isinstance(left_value, list) and sum(left_value) == right_value
        elif comparison == "BYTE_COUNT_OF_RFC8785_CANONICAL_COMPLETE_JSON_EQUAL":
            passed = len(canonical_bytes(left_value)) == right_value
        elif comparison == "SHA256_OF_RFC8785_CANONICAL_COMPLETE_JSON_EQUAL":
            passed = digest(canonical_bytes(left_value)) == right_value
        elif "NOT_EQUAL" in comparison:
            passed = left_value != right_value
        else:
            passed = _equal_values(left_value, right_value)
        result.append(_execution_receipt(order, descriptor, left, right, comparison,
                                         left_value, right_value, comparison_result=passed))
    return result


def _pairwise_key_receipt(controller_key: str, carrier_key: str,
                          finalizer_key: str) -> dict[str, Any]:
    domain = "AWS_C0_THREE_COORDINATE_CAPTURE_CHANNEL_KEY_PAIR_V1_NUL"
    formula = "SHA256(DOMAIN_UTF8_CONCAT_LEFT_POINTER_UTF8_CONCAT_RIGHT_POINTER_UTF8_CONCAT_UTF8_BYTEWISE_NOT_EQUAL)"
    pairs = [
        ("/controller_journal_key", "/controller_journal_handoff_key", controller_key, carrier_key),
        ("/controller_journal_key", "/finalizer_journal_key", controller_key, finalizer_key),
        ("/controller_journal_handoff_key", "/finalizer_journal_key", carrier_key, finalizer_key),
    ]
    receipts = []
    for left, right, left_value, right_value in pairs:
        if left_value == right_value:
            raise Refusal("capture aggregate keys are not pairwise distinct")
        receipts.append({"left_pointer": left, "right_pointer": right,
                         "comparison": "UTF8_BYTEWISE_NOT_EQUAL", "hash_domain": domain,
                         "hash_formula": formula,
                         "receipt_sha256": digest(domain.encode() + b"\0" + left.encode() + right.encode() + b"\x01")})
    aggregate_domain = "AWS_C0_THREE_COORDINATE_CAPTURE_CHANNEL_KEY_DISTINCTNESS_V2_NUL"
    return {"comparison_receipts_in_order": receipts, "aggregate_hash_domain": aggregate_domain,
            "aggregate_hash_formula": "SHA256(DOMAIN_UTF8_CONCAT_EXACT_ORDERED_TYPED_THREE_PAIR_RECEIPTS)",
            "receipt_sha256": digest(aggregate_domain.encode() + b"\0" + canonical_bytes(receipts))}


def _build_accepted_capture_aggregate(*, attempt_identity: dict[str, str],
                                      handoff: dict[str, Any], carrier_observation: dict[str, Any],
                                      finalizer_journal_identity: dict[str, str],
                                      finalizer_readback: dict[str, Any],
                                      finalizer_projection: dict[str, Any],
                                      finalizer_journal: CaptureJournal,
                                      final_manifest_identity: dict[str, str],
                                      final_manifest_receipt: dict[str, Any],
                                      final_manifest_put_response: dict[str, Any],
                                      final_manifest_preimage: dict[str, Any],
                                      publication_observation: dict[str, Any],
                                      publication_observation_identity: dict[str, str],
                                      retrieval_identity: dict[str, str],
                                      retrieval_receipt: dict[str, Any]) -> dict[str, Any]:
    if handoff.get("attempt_identity") != attempt_identity:
        raise Refusal("capture aggregate attempt mismatch")
    if finalizer_projection != finalizer_journal.aggregate():
        raise Refusal("capture aggregate finalizer projection mismatch")
    controller_object = handoff["controller_journal_object"]
    controller_journal = carrier_observation["controller_journal"]
    controller_envelopes = controller_journal["envelopes"]
    finalizer_envelopes = finalizer_journal.envelopes
    publication = finalizer_readback["publication_receipt"]
    readback = finalizer_readback["readback_receipt"]
    if any(publication[name] != readback[name] for name in
           ("key", "version_id", "etag", "bytes", "sha256", "checksum_sha256_base64")):
        raise Refusal("capture aggregate finalizer coordinates mismatch")
    if (finalizer_journal_identity != identity(
            "aws_c0_finalizer_capture_journal/v1", publication["sha256"]) or
            finalizer_readback["content_chain_sha256"] != finalizer_journal._previous):
        raise Refusal("capture aggregate finalizer journal identity mismatch")
    manifest_raw = canonical_bytes(final_manifest_preimage)
    if (final_manifest_identity != identity("aws_c0_final_manifest/v4", _root_digest(final_manifest_preimage)) or
            final_manifest_receipt["bytes"] != len(manifest_raw) or
            final_manifest_receipt["sha256"] != digest(manifest_raw) or
            any(final_manifest_put_response[name] != final_manifest_receipt[name] for name in
                ("key", "version_id", "bytes", "sha256", "checksum_sha256_base64"))):
        raise Refusal("capture aggregate final manifest publication mismatch")
    carrier_key = carrier_observation["key"]
    finalizer_key = publication["key"]
    if len({controller_object["key"], carrier_key, finalizer_key}) != 3:
        raise Refusal("capture aggregate keys are not pairwise distinct")
    controller_terminal_sequence = next((index for index, envelope in enumerate(controller_envelopes, 1)
        if str(envelope.get("operation_capture_preimage", {}).get("key", "")).startswith(
            controller_object["key"].rsplit("evidence/", 1)[0] + "evidence/terminal-")), 0)
    if controller_terminal_sequence != len(controller_envelopes):
        raise Refusal("controller terminal result Put is not the final journal envelope")
    finalizer_terminal_sequence = next((index for index, envelope in enumerate(finalizer_envelopes, 1)
        if envelope.get("operation_capture_preimage", {}).get("path") == "/" + final_manifest_receipt["key"]), 0)
    if finalizer_terminal_sequence != len(finalizer_envelopes):
        raise Refusal("final manifest Put is not the final substantive finalizer operation")
    controller_terminal_capture = controller_envelopes[-1]["operation_capture_preimage"]
    finalizer_terminal_capture = finalizer_envelopes[-1]["operation_capture_preimage"]
    controller_terminal_identity = identity("aws_c0_terminal_receipt/v1",
                                            controller_terminal_capture["payload_sha256"])
    controller_terminal_membership = _membership_receipt(
        journal_role="CONTROLLER", journal_object_sha256=controller_object["object_sha256"],
        content_chain_sha256=controller_object["content_chain_sha256"],
        envelopes=controller_envelopes, sequence=controller_terminal_sequence,
        expected_operation="PUT_OBJECT", bucket=controller_object["bucket"],
        key=controller_terminal_capture["key"], expected_identity=controller_terminal_identity)
    finalizer_terminal_membership = _membership_receipt(
        journal_role="FINALIZER", journal_object_sha256=publication["sha256"],
        content_chain_sha256=finalizer_readback["content_chain_sha256"],
        envelopes=finalizer_envelopes, sequence=finalizer_terminal_sequence,
        expected_operation="PUT_OBJECT", bucket=controller_object["bucket"],
        key=final_manifest_receipt["key"], expected_identity=final_manifest_identity)
    controller_domain = "AWS_C0_CONTROLLER_CAPTURE_JOURNAL_OPERATION_AGGREGATE_V1_NUL"
    finalizer_domain = "AWS_C0_FINALIZER_CAPTURE_JOURNAL_OPERATION_AGGREGATE_V1_NUL"
    combined_domain = "AWS_C0_COMBINED_CAPTURE_JOURNAL_AGGREGATE_V1_NUL"
    controller_aggregate = _operation_aggregate(controller_envelopes, controller_domain)
    finalizer_aggregate = _operation_aggregate(finalizer_envelopes, finalizer_domain)
    total_envelopes = len(controller_envelopes) + len(finalizer_envelopes)
    combined_aggregate = digest(combined_domain.encode() + b"\0" + bytes.fromhex(controller_aggregate) +
                                bytes.fromhex(finalizer_aggregate) + total_envelopes.to_bytes(8, "big"))

    def capture_for(sequence: int) -> dict[str, Any]:
        return finalizer_envelopes[sequence - 1]["operation_capture_preimage"]
    list_sequence = carrier_observation["list_capture_sequence"]
    carrier_sequence = carrier_observation["carrier_get_capture_sequence"]
    controller_get_sequence = carrier_observation["controller_journal_get_capture_sequence"]
    list_capture = capture_for(list_sequence)
    carrier_capture = capture_for(carrier_sequence)
    controller_get_capture = capture_for(controller_get_sequence)
    list_raw = base64.b64decode(list_capture["response_body_base64"], validate=True)
    carrier_raw = canonical_bytes(handoff)
    list_projection = _capture_projection(
        list_capture, bucket=controller_object["bucket"], key=carrier_key,
        version_id=None, etag=None, checksum=None, body_byte_count=len(list_raw),
        body_sha256=digest(list_raw))
    carrier_projection = _capture_projection(
        carrier_capture, bucket=controller_object["bucket"], key=carrier_key,
        version_id=carrier_observation["version_id"], etag=carrier_observation["etag"],
        checksum=carrier_observation["checksum_sha256_base64"],
        body_byte_count=carrier_observation["bytes"], body_sha256=carrier_observation["sha256"])
    controller_get_projection = _capture_projection(
        controller_get_capture, bucket=controller_object["bucket"], key=controller_object["key"],
        version_id=controller_object["version_id"], etag=controller_object["etag"],
        checksum=controller_object["checksum_sha256_base64"],
        body_byte_count=controller_object["byte_count"], body_sha256=controller_object["object_sha256"])
    list_membership = _membership_receipt(
        journal_role="FINALIZER", journal_object_sha256=publication["sha256"],
        content_chain_sha256=finalizer_readback["content_chain_sha256"],
        envelopes=finalizer_envelopes, sequence=list_sequence,
        expected_operation="LIST_OBJECT_VERSIONS", bucket=controller_object["bucket"],
        key=carrier_key, expected_identity=identity("aws_c0_s3_list_response/v1", digest(list_raw)))
    carrier_membership = _membership_receipt(
        journal_role="FINALIZER", journal_object_sha256=publication["sha256"],
        content_chain_sha256=finalizer_readback["content_chain_sha256"],
        envelopes=finalizer_envelopes, sequence=carrier_sequence,
        expected_operation="GET_OBJECT_EXACT_VERSION", bucket=controller_object["bucket"],
        key=carrier_key, expected_identity=handoff["handoff_identity"])
    controller_get_membership = _membership_receipt(
        journal_role="FINALIZER", journal_object_sha256=publication["sha256"],
        content_chain_sha256=finalizer_readback["content_chain_sha256"],
        envelopes=finalizer_envelopes, sequence=controller_get_sequence,
        expected_operation="GET_OBJECT_EXACT_VERSION", bucket=controller_object["bucket"],
        key=controller_object["key"], expected_identity=identity(
            "aws_c0_controller_capture_journal/v1", controller_object["object_sha256"]))
    parse_body = {"bucket": controller_object["bucket"], "key": carrier_key,
                  "live_versions_in_order": [{"key": carrier_key, "version_id": carrier_observation["version_id"]}],
                  "delete_markers_in_order": [], "ambiguous": False,
                  "exact_live_version_count": 1, "delete_marker_count": 0, "ambiguity_count": 0}
    parse_raw = canonical_bytes(parse_body)
    parse_domain = "AWS_C0_EXACT_KEY_LIST_OBJECT_VERSIONS_DISCOVERY_PARSE_V1_NUL"
    discovery = {"schema": "aws_c0_exact_key_list_object_versions_discovery/v1", **parse_body,
        "disposition": "EXACT_KEY_LIST_OBJECT_VERSIONS_DISCOVERY_HAS_ONE_LIVE_VERSION_ZERO_DELETE_MARKERS_AND_ZERO_AMBIGUITY_PASS",
        "raw_authenticated_list_response_body_base64": base64.b64encode(list_raw).decode(),
        "raw_authenticated_list_response_body_byte_count": len(list_raw),
        "raw_authenticated_list_response_body_sha256": digest(list_raw),
        "canonical_parse_body_identity": identity("aws_c0_exact_key_list_parse/v1", digest(parse_domain.encode() + b"\0" + parse_raw)),
        "canonical_parse_body_byte_count": len(parse_raw),
        "canonical_parse_body_sha256": digest(parse_domain.encode() + b"\0" + parse_raw),
        "canonical_parse_body_hash_domain": parse_domain,
        "canonical_parse_body_hash_formula": "SHA256(DOMAIN_UTF8_CONCAT_RFC8785_CANONICAL_BUCKET_KEY_LIVE_VERSIONS_DELETE_MARKERS_AMBIGUOUS_AND_COUNTS_PARSED_FROM_AUTHENTICATED_LIST_RESPONSE_BODY)"}
    discovery["authenticated_response_parse_execution_receipt"] = _execution_receipt(
        1, "EXACT_KEY_LIST_RESPONSE_PARSE_001",
        "/raw_authenticated_list_response_body_base64,/raw_authenticated_list_response_body_byte_count,/raw_authenticated_list_response_body_sha256",
        "/bucket,/key,/live_versions_in_order,/delete_markers_in_order,/ambiguous,/exact_live_version_count,/delete_marker_count,/ambiguity_count,/canonical_parse_body_byte_count,/canonical_parse_body_sha256",
        "STRICT_BASE64_DECODE_BYTE_COUNT_AND_SHA256_EQUAL_AUTHENTICATED_CAPTURE_THEN_PARSE_EXACT_KEY_LIST_OBJECT_VERSIONS_XML_AND_RFC8785_RECOMPUTE_ONE_LIVE_VERSION_ZERO_DELETE_MARKERS_ZERO_AMBIGUITY",
        [discovery["raw_authenticated_list_response_body_base64"], len(list_raw), digest(list_raw)],
        [*parse_body.values(), len(parse_raw), discovery["canonical_parse_body_sha256"]], comparison_result=True)
    external_proof = {
        "schema": "controller_journal_handoff_external_observation_proof_v1",
        "finalizer_list_capture_identity": identity("aws_c0_authenticated_s3_operation_capture/v1", list_projection["capture_sha256"]),
        "finalizer_carrier_get_capture_identity": identity("aws_c0_authenticated_s3_operation_capture/v1", carrier_projection["capture_sha256"]),
        "finalizer_list_capture_preimage": list_projection,
        "finalizer_carrier_get_capture_preimage": carrier_projection,
        "finalizer_list_membership_receipt": list_membership,
        "finalizer_list_discovery_result": discovery,
        "finalizer_carrier_get_membership_receipt": carrier_membership,
        "bucket": controller_object["bucket"], "key": carrier_key,
        "version_id": carrier_observation["version_id"], "etag": carrier_observation["etag"],
        "checksum_sha256_base64": carrier_observation["checksum_sha256_base64"],
        "byte_count": carrier_observation["bytes"], "object_sha256": carrier_observation["sha256"],
        "carrier_identity": handoff["handoff_identity"], "carrier_digest": handoff["handoff_canonical_sha256"],
        "disposition": "FINALIZER_CAPTURED_CLOSED_EXACT_KEY_LIST_OBJECT_VERSIONS_DISCOVERY_ONE_LIVE_VERSION_ZERO_DELETE_MARKERS_ZERO_AMBIGUITY_THEN_DISCOVERED_EXACT_VERSION_GET_BINDS_CARRIER_PUBLICATION_OBSERVATION_EXTERNALLY;COMPLETE_RFC8785_DECODED_HANDOFF_BYTE_COUNT_AND_SHA256_EQUAL_THE_AUTHENTICATED_GET_RESPONSE_AND_DECODED_CONTROLLER_MATERIAL_BINDS_THE_ENCLOSING_AGGREGATE_BEFORE_FINALIZER_SEAL_WITH_NO_SPLICE_IN_OBJECT_POST_PUT_RECEIPT_OR_FIXED_POINT_PASS",
        "finalizer_controller_journal_get_capture_identity": identity("aws_c0_authenticated_s3_operation_capture/v1", controller_get_projection["capture_sha256"]),
        "finalizer_controller_journal_get_capture_preimage": controller_get_projection,
        "finalizer_controller_journal_get_membership_receipt": controller_get_membership,
        "decoded_controller_journal_handoff": handoff,
        "terminal_final_manifest_put_requested_utc": finalizer_terminal_membership["operation_requested_utc"],
    }
    external_rows = [
        ("CARRIER_EXTERNAL_LIST_CAPTURE_IDENTITY_SHA256_001", "/finalizer_list_capture_identity/sha256", "/finalizer_list_capture_preimage/capture_sha256", "SHA256_EQUAL"),
        ("CARRIER_EXTERNAL_LIST_CAPTURE_IDENTITY_VALUE_002", "/finalizer_list_capture_identity/value", "/finalizer_list_capture_preimage/capture_sha256", "SHA256_EQUAL"),
        ("CARRIER_EXTERNAL_GET_CAPTURE_IDENTITY_SHA256_003", "/finalizer_carrier_get_capture_identity/sha256", "/finalizer_carrier_get_capture_preimage/capture_sha256", "SHA256_EQUAL"),
        ("CARRIER_EXTERNAL_GET_CAPTURE_IDENTITY_VALUE_004", "/finalizer_carrier_get_capture_identity/value", "/finalizer_carrier_get_capture_preimage/capture_sha256", "SHA256_EQUAL"),
        ("CARRIER_EXTERNAL_LIST_MEMBERSHIP_CAPTURE_IDENTITY_005", "/finalizer_list_membership_receipt/selected_operation_capture_identity/value", "/finalizer_list_capture_identity/value", "SHA256_EQUAL"),
        ("CARRIER_EXTERNAL_LIST_MEMBERSHIP_CAPTURE_HASH_006", "/finalizer_list_membership_receipt/selected_operation_capture_preimage_sha256", "/finalizer_list_capture_preimage/capture_sha256", "SHA256_EQUAL"),
        ("CARRIER_EXTERNAL_GET_MEMBERSHIP_CAPTURE_IDENTITY_007", "/finalizer_carrier_get_membership_receipt/selected_operation_capture_identity/value", "/finalizer_carrier_get_capture_identity/value", "SHA256_EQUAL"),
        ("CARRIER_EXTERNAL_GET_MEMBERSHIP_CAPTURE_HASH_008", "/finalizer_carrier_get_membership_receipt/selected_operation_capture_preimage_sha256", "/finalizer_carrier_get_capture_preimage/capture_sha256", "SHA256_EQUAL"),
        ("CARRIER_EXTERNAL_LIST_MEMBERSHIP_ROLE_009", "/finalizer_list_membership_receipt/journal_role", "FINALIZER", "LITERAL_EQUAL"),
        ("CARRIER_EXTERNAL_GET_MEMBERSHIP_ROLE_010", "/finalizer_carrier_get_membership_receipt/journal_role", "FINALIZER", "LITERAL_EQUAL"),
        ("CARRIER_EXTERNAL_LIST_MEMBERSHIP_OPERATION_011", "/finalizer_list_membership_receipt/expected_operation", "LIST_OBJECT_VERSIONS", "LITERAL_EQUAL"),
        ("CARRIER_EXTERNAL_GET_MEMBERSHIP_OPERATION_012", "/finalizer_carrier_get_membership_receipt/expected_operation", "GET_OBJECT_EXACT_VERSION", "LITERAL_EQUAL"),
        ("CARRIER_EXTERNAL_LIST_MEMBERSHIP_KEY_013", "/finalizer_list_membership_receipt/expected_key", "/finalizer_list_discovery_result/key", "UTF8_BYTEWISE_EQUAL"),
        ("CARRIER_EXTERNAL_GET_MEMBERSHIP_KEY_014", "/finalizer_carrier_get_membership_receipt/expected_key", "/finalizer_list_discovery_result/key", "UTF8_BYTEWISE_EQUAL"),
        ("CARRIER_EXTERNAL_LIST_FINALIZER_JOURNAL_SHA256_015", "/finalizer_list_membership_receipt/journal_published_object_sha256", "/finalizer_carrier_get_membership_receipt/journal_published_object_sha256", "SHA256_EQUAL"),
        ("CARRIER_EXTERNAL_LIST_FINALIZER_CHAIN_SHA256_016", "/finalizer_list_membership_receipt/journal_content_chain_sha256", "/finalizer_carrier_get_membership_receipt/journal_content_chain_sha256", "SHA256_EQUAL"),
        ("CARRIER_EXTERNAL_LIST_FINALIZER_JOURNAL_COUNT_017", "/finalizer_list_membership_receipt/journal_envelope_count", "/finalizer_carrier_get_membership_receipt/journal_envelope_count", "INTEGER_EQUAL"),
        ("CARRIER_EXTERNAL_DISCOVERY_BUCKET_018", "/finalizer_list_discovery_result/bucket", "/finalizer_carrier_get_capture_preimage/authorization_credential_access_key_id_extraction_preimage/sanitized_request_envelope_preimage/bucket_name", "UTF8_BYTEWISE_EQUAL"),
        ("CARRIER_EXTERNAL_DISCOVERY_KEY_019", "/finalizer_list_discovery_result/key", "/finalizer_carrier_get_capture_preimage/authorization_credential_access_key_id_extraction_preimage/sanitized_request_envelope_preimage/object_key", "UTF8_BYTEWISE_EQUAL"),
        ("CARRIER_EXTERNAL_DISCOVERY_VERSION_TO_GET_020", "/finalizer_list_discovery_result/live_versions_in_order/0/version_id", "/finalizer_carrier_get_capture_preimage/authorization_credential_access_key_id_extraction_preimage/sanitized_request_envelope_preimage/version_id", "UTF8_BYTEWISE_EQUAL"),
        ("CARRIER_EXTERNAL_GET_REQUEST_BUCKET_021", "/finalizer_carrier_get_capture_preimage/authorization_credential_access_key_id_extraction_preimage/sanitized_request_envelope_preimage/bucket_name", "/bucket", "UTF8_BYTEWISE_EQUAL"),
        ("CARRIER_EXTERNAL_GET_REQUEST_KEY_022", "/finalizer_carrier_get_capture_preimage/authorization_credential_access_key_id_extraction_preimage/sanitized_request_envelope_preimage/object_key", "/key", "UTF8_BYTEWISE_EQUAL"),
        ("CARRIER_EXTERNAL_GET_RESPONSE_VERSION_023", "/finalizer_carrier_get_capture_preimage/response_envelope_preimage/version_id", "/version_id", "UTF8_BYTEWISE_EQUAL"),
        ("CARRIER_EXTERNAL_GET_RESPONSE_ETAG_024", "/finalizer_carrier_get_capture_preimage/response_envelope_preimage/etag", "/etag", "UTF8_BYTEWISE_EQUAL"),
        ("CARRIER_EXTERNAL_GET_RESPONSE_CHECKSUM_025", "/finalizer_carrier_get_capture_preimage/response_envelope_preimage/checksum_sha256_base64", "/checksum_sha256_base64", "UTF8_BYTEWISE_EQUAL"),
        ("CARRIER_EXTERNAL_GET_RESPONSE_LENGTH_026", "/finalizer_carrier_get_capture_preimage/response_envelope_preimage/content_length", "/byte_count", "INTEGER_EQUAL"),
        ("CARRIER_EXTERNAL_GET_RESPONSE_BODY_SHA256_027", "/finalizer_carrier_get_capture_preimage/response_envelope_preimage/body_sha256", "/object_sha256", "SHA256_EQUAL"),
        ("CARRIER_EXTERNAL_CARRIER_IDENTITY_SHA256_028", "/carrier_identity/sha256,/carrier_identity/value", "/decoded_controller_journal_handoff/handoff_identity/sha256,/decoded_controller_journal_handoff/handoff_identity/value", "PREFIX_ORDERED_PAIRWISE_SHA256_EQUAL"),
        ("CARRIER_EXTERNAL_CARRIER_IDENTITY_VALUE_029", "/carrier_digest", "/decoded_controller_journal_handoff/handoff_canonical_sha256", "SHA256_EQUAL"),
        ("CARRIER_EXTERNAL_LIST_BEFORE_GET_COMPLETION_030", "/finalizer_list_membership_receipt/operation_completed_utc", "/finalizer_carrier_get_membership_receipt/operation_completed_utc", "UTC_LESS_THAN_OR_EQUAL"),
        ("CARRIER_EXTERNAL_LIST_RESPONSE_BODY_TO_DISCOVERY_RAW_031", "/finalizer_list_capture_preimage/response_envelope_preimage/body_sha256", "/finalizer_list_discovery_result/raw_authenticated_list_response_body_sha256", "SHA256_EQUAL"),
        ("CARRIER_EXTERNAL_LIST_PARSE_IDENTITY_032", "/finalizer_list_discovery_result/canonical_parse_body_identity/sha256,/finalizer_list_discovery_result/canonical_parse_body_identity/value", "/finalizer_list_discovery_result/canonical_parse_body_sha256", "BOTH_SHA256_EQUAL"),
        ("CARRIER_EXTERNAL_CONTROLLER_JOURNAL_GET_CAPTURE_IDENTITY_033", "/finalizer_controller_journal_get_capture_identity/sha256,/finalizer_controller_journal_get_capture_identity/value", "/finalizer_controller_journal_get_capture_preimage/capture_sha256", "BOTH_SHA256_EQUAL"),
        ("CARRIER_EXTERNAL_CONTROLLER_JOURNAL_GET_MEMBERSHIP_IDENTITY_034", "/finalizer_controller_journal_get_membership_receipt/selected_operation_capture_identity/sha256,/finalizer_controller_journal_get_membership_receipt/selected_operation_capture_identity/value", "/finalizer_controller_journal_get_capture_identity/sha256", "BOTH_SHA256_EQUAL"),
        ("CARRIER_EXTERNAL_CONTROLLER_JOURNAL_GET_MEMBERSHIP_HASH_035", "/finalizer_controller_journal_get_membership_receipt/selected_operation_capture_preimage_sha256", "/finalizer_controller_journal_get_capture_preimage/capture_sha256", "SHA256_EQUAL"),
        ("CARRIER_EXTERNAL_CONTROLLER_JOURNAL_GET_MEMBERSHIP_ROLE_OPERATION_036", "/finalizer_controller_journal_get_membership_receipt/journal_role,/finalizer_controller_journal_get_membership_receipt/expected_operation", "FINALIZER,GET_OBJECT_EXACT_VERSION", "PREFIX_ORDERED_LITERAL_EQUAL"),
        ("CARRIER_EXTERNAL_CONTROLLER_JOURNAL_GET_MEMBERSHIP_KEY_037", "/finalizer_controller_journal_get_membership_receipt/expected_key", "/decoded_controller_journal_handoff/controller_journal_object/key", "UTF8_BYTEWISE_EQUAL"),
        ("CARRIER_EXTERNAL_CONTROLLER_JOURNAL_GET_REQUEST_BUCKET_038", "/finalizer_controller_journal_get_capture_preimage/authorization_credential_access_key_id_extraction_preimage/sanitized_request_envelope_preimage/bucket_name", "/decoded_controller_journal_handoff/controller_journal_object/bucket", "UTF8_BYTEWISE_EQUAL"),
        ("CARRIER_EXTERNAL_CONTROLLER_JOURNAL_GET_REQUEST_KEY_039", "/finalizer_controller_journal_get_capture_preimage/authorization_credential_access_key_id_extraction_preimage/sanitized_request_envelope_preimage/object_key", "/decoded_controller_journal_handoff/controller_journal_object/key", "UTF8_BYTEWISE_EQUAL"),
        ("CARRIER_EXTERNAL_CONTROLLER_JOURNAL_GET_REQUEST_VERSION_040", "/finalizer_controller_journal_get_capture_preimage/authorization_credential_access_key_id_extraction_preimage/sanitized_request_envelope_preimage/version_id", "/decoded_controller_journal_handoff/controller_journal_object/version_id", "UTF8_BYTEWISE_EQUAL"),
        ("CARRIER_EXTERNAL_CONTROLLER_JOURNAL_GET_RESPONSE_COORDINATES_041", "/finalizer_controller_journal_get_capture_preimage/response_envelope_preimage/version_id,/finalizer_controller_journal_get_capture_preimage/response_envelope_preimage/etag,/finalizer_controller_journal_get_capture_preimage/response_envelope_preimage/checksum_sha256_base64,/finalizer_controller_journal_get_capture_preimage/response_envelope_preimage/content_length,/finalizer_controller_journal_get_capture_preimage/response_envelope_preimage/body_sha256", "/decoded_controller_journal_handoff/controller_journal_object/version_id,/decoded_controller_journal_handoff/controller_journal_object/etag,/decoded_controller_journal_handoff/controller_journal_object/checksum_sha256_base64,/decoded_controller_journal_handoff/controller_journal_object/byte_count,/decoded_controller_journal_handoff/controller_journal_object/object_sha256", "PREFIX_ORDERED_CANONICAL_VALUE_EQUAL"),
        ("CARRIER_EXTERNAL_THREE_MEMBERSHIP_FINALIZER_JOURNAL_COORDINATES_042", "/finalizer_list_membership_receipt/journal_published_object_sha256,/finalizer_list_membership_receipt/journal_content_chain_sha256,/finalizer_list_membership_receipt/journal_envelope_count,/finalizer_carrier_get_membership_receipt/journal_published_object_sha256,/finalizer_carrier_get_membership_receipt/journal_content_chain_sha256,/finalizer_carrier_get_membership_receipt/journal_envelope_count", "/finalizer_controller_journal_get_membership_receipt/journal_published_object_sha256,/finalizer_controller_journal_get_membership_receipt/journal_content_chain_sha256,/finalizer_controller_journal_get_membership_receipt/journal_envelope_count,/finalizer_controller_journal_get_membership_receipt/journal_published_object_sha256,/finalizer_controller_journal_get_membership_receipt/journal_content_chain_sha256,/finalizer_controller_journal_get_membership_receipt/journal_envelope_count", "PREFIX_ORDERED_CANONICAL_VALUE_EQUAL"),
        ("CARRIER_EXTERNAL_CARRIER_GET_BEFORE_CONTROLLER_JOURNAL_GET_043", "/finalizer_carrier_get_membership_receipt/operation_completed_utc", "/finalizer_controller_journal_get_membership_receipt/operation_completed_utc", "UTC_LESS_THAN_OR_EQUAL"),
        ("CARRIER_EXTERNAL_CONTROLLER_JOURNAL_GET_BEFORE_TERMINAL_PUT_044", "/finalizer_controller_journal_get_membership_receipt/operation_completed_utc", "/terminal_final_manifest_put_requested_utc", "UTC_LESS_THAN_OR_EQUAL"),
        ("CARRIER_EXTERNAL_DECODED_HANDOFF_FULL_BODY_BYTES_045", "/decoded_controller_journal_handoff", "/byte_count", "BYTE_COUNT_OF_RFC8785_CANONICAL_COMPLETE_JSON_EQUAL"),
        ("CARRIER_EXTERNAL_DECODED_HANDOFF_FULL_BODY_SHA256_046", "/decoded_controller_journal_handoff", "/object_sha256", "SHA256_OF_RFC8785_CANONICAL_COMPLETE_JSON_EQUAL"),
    ]
    external_proof["binding_execution_receipts_in_order"] = _execution_rows(external_proof, external_rows)

    prepare_memberships = []
    for sequence in range(1, 4):
        capture = controller_envelopes[sequence - 1]["operation_capture_preimage"]
        prepare_memberships.append(_membership_receipt(
            journal_role="CONTROLLER", journal_object_sha256=controller_object["object_sha256"],
            content_chain_sha256=controller_object["content_chain_sha256"],
            envelopes=controller_envelopes, sequence=sequence,
            expected_operation="GET_OBJECT_EXACT_VERSION", bucket=controller_object["bucket"],
            key=capture["key"], expected_identity=capture["source_object_identity"]))
    prepare_domain = "AWS_C0_PREPARE_REQUEST_THREE_GET_CAPTURE_AGGREGATE_V1_NUL"
    prepare_material = [{"capture_identity": row["selected_operation_capture_identity"],
                         "preimage_sha256": row["selected_operation_capture_preimage_sha256"]}
                        for row in prepare_memberships]
    prepare_aggregate = digest(prepare_domain.encode() + b"\0" + canonical_bytes(prepare_material))
    prepare_receipt_domain = "AWS_C0_CONTROLLER_PREPARE_GET_SUBSEQUENCE_CROSS_BINDING_RECEIPT_V1_NUL"
    prepare_receipt = {
        "schema": "aws_c0_controller_prepare_get_subsequence_cross_binding_receipt/v1",
        "memberships_in_source_role_order": prepare_memberships,
        "capture_aggregate_hash_domain": prepare_domain,
        "capture_aggregate_hash_formula": "SHA256(DOMAIN_UTF8_CONCAT_THREE_PREFIX_ORDERED_OPERATION_CAPTURE_IDENTITY_VALUES_AND_COMPLETE_PREIMAGE_SHA256_VALUES)",
        "recomputed_aggregate_sha256": prepare_aggregate,
        "source_sidecar_aggregate_sha256": prepare_aggregate,
        "all_three_authenticated_gets_equal_and_prefix_ordered": True,
        "receipt_hash_domain": prepare_receipt_domain,
        "receipt_hash_formula": "SHA256(DOMAIN_UTF8_CONCAT_THREE_PREFIX_ORDERED_MEMBERSHIP_RECEIPT_SHA256_VALUES_CONCAT_RECOMPUTED_AGGREGATE_SHA256_CONCAT_SOURCE_SIDECAR_AGGREGATE_SHA256)",
    }
    prepare_receipt["receipt_sha256"] = digest(
        prepare_receipt_domain.encode() + b"\0" + canonical_bytes({name: value for name, value in prepare_receipt.items()
                                                                    if name != "receipt_sha256"}))
    finalizer_local_sha = digest(canonical_bytes({
        "publication_receipt_identity": finalizer_readback["publication_receipt_identity"],
        "readback_receipt_identity": finalizer_readback["readback_receipt_identity"],
        "finalizer_aggregate_sha256": finalizer_aggregate,
    }))
    application_release_sha = digest(canonical_bytes([
        digest(canonical_bytes(envelope["operation_capture_preimage"])) for envelope in finalizer_envelopes]))
    application_release_identity = identity("aws_c0_lambda_application_release_operation_proof/v1",
                                            application_release_sha)
    coverage_domain = "AWS_C0_LAMBDA_APPLICATION_RELEASE_OPERATION_COVERAGE_RECEIPT_V1_NUL"
    lambda_coverage = {
        "schema": "aws_c0_lambda_application_release_operation_coverage_receipt/v1",
        "finalizer_journal_published_object_sha256": publication["sha256"],
        "finalizer_journal_content_chain_sha256": finalizer_readback["content_chain_sha256"],
        "finalizer_journal_envelope_count": len(finalizer_envelopes),
        "lambda_substantive_operation_count": len(finalizer_envelopes),
        "excluded_fail_closed_envelope_count": 0,
        "application_release_proof_identity": application_release_identity,
        "application_release_proof_sha256": application_release_sha,
        "operation_binding_count": len(finalizer_envelopes),
        "terminal_request_envelope_sha256": finalizer_terminal_membership["selected_request_envelope_sha256"],
        "terminal_operation_completed_utc": finalizer_terminal_membership["operation_completed_utc"],
        "terminal_membership_receipt_sha256": finalizer_terminal_membership["membership_receipt_sha256"],
        "coverage_hash_domain": coverage_domain,
        "coverage_hash_formula": "SHA256(DOMAIN_UTF8_CONCAT_FINALIZER_JOURNAL_PUBLISHED_OBJECT_SHA256_CONCAT_CONTENT_CHAIN_SHA256_CONCAT_INT64BE_ENVELOPE_COUNT_CONCAT_INT64BE_LAMBDA_SUBSTANTIVE_OPERATION_COUNT_CONCAT_INT64BE_EXCLUDED_FAIL_CLOSED_COUNT_CONCAT_APPLICATION_RELEASE_PROOF_IDENTITY_VALUE_CONCAT_APPLICATION_RELEASE_PROOF_SHA256_CONCAT_INT64BE_OPERATION_BINDING_COUNT_CONCAT_OPERATION_BINDING_AGGREGATE_SHA256_CONCAT_JOURNAL_LAMBDA_OPERATION_PREFIX_AGGREGATE_SHA256_CONCAT_TERMINAL_REQUEST_ENVELOPE_SHA256_CONCAT_TERMINAL_COMPLETED_UTC_UTF8_CONCAT_TERMINAL_MEMBERSHIP_RECEIPT_SHA256)",
        "coverage_disposition": "TRANSIENT_EXACT_VERSION_FINALIZER_JOURNAL_VALIDATION_PROVES_OPERATION_BINDING_COUNT_EQUALS_ALL_SUBSTANTIVE_LAMBDA_AUTHENTICATED_OPERATION_ENVELOPES_IN_PREFIX_ORDER_WITH_IDENTICAL_REQUEST_HASHES_AND_COMPLETION_TIMES_EXCLUDES_ONLY_OPTIONAL_FAIL_CLOSED_ENVELOPE_AND_TERMINAL_SELECTION_EQUALS_FINAL_MANIFEST_MEMBERSHIP_PASS",
    }
    lambda_coverage["coverage_receipt_sha256"] = digest(
        coverage_domain.encode() + b"\0" + canonical_bytes({name: value for name, value in lambda_coverage.items()
                                                             if name != "coverage_receipt_sha256"}))
    proof_domain = "AWS_C0_FINAL_S3_CAPTURE_AGGREGATE_FIXED_SIZE_BODY_V1_NUL"
    observation_raw = canonical_bytes(publication_observation)
    aggregate = {
        "schema": "aws_c0_final_s3_capture_aggregate/v1", "attempt_identity": attempt_identity,
        "controller_journal_identity": identity("aws_c0_controller_capture_journal/v1", controller_object["object_sha256"]),
        "controller_journal_byte_count": controller_object["byte_count"],
        "controller_published_object_sha256": controller_object["object_sha256"],
        "controller_content_chain_sha256": controller_object["content_chain_sha256"],
        "controller_journal_version_id": controller_object["version_id"],
        "controller_journal_etag": controller_object["etag"],
        "controller_publication_receipt_identity": handoff["controller_publication_receipt_identity"],
        "controller_publication_receipt_sha256": handoff["controller_publication_receipt_identity"]["sha256"],
        "controller_readback_receipt_identity": handoff["controller_readback_receipt_identity"],
        "controller_readback_receipt_sha256": handoff["controller_readback_receipt_identity"]["sha256"],
        "controller_journal_handoff_identity": handoff["handoff_identity"],
        "controller_journal_handoff_sha256": handoff["handoff_canonical_sha256"],
        "controller_journal_handoff_key": carrier_key,
        "controller_journal_handoff_version_id": carrier_observation["version_id"],
        "controller_journal_handoff_bucket_name": controller_object["bucket"],
        "controller_journal_handoff_etag": carrier_observation["etag"],
        "controller_journal_handoff_checksum_sha256_base64": carrier_observation["checksum_sha256_base64"],
        "controller_journal_handoff_byte_count": carrier_observation["bytes"],
        "controller_journal_handoff_object_sha256": carrier_observation["sha256"],
        "controller_journal_handoff_external_publication_readback_proof": external_proof,
        "controller_journal_handoff_embedded_receipt_preimage_disposition": "CARRIER_EMBEDDED_TYPED_CONTROLLER_PUBLICATION_AND_READBACK_RECEIPT_COMPLETE_PREIMAGES_RECOMPUTE_IDENTITY_AND_HASH_BIND_TO_CONTROLLER_JOURNAL_COORDINATES_WITH_NO_SEPARATE_RECEIPT_OBJECT_GET_OR_PUT_PASS",
        "controller_envelope_count": len(controller_envelopes), "controller_aggregate_sha256": controller_aggregate,
        "finalizer_journal_identity": finalizer_journal_identity,
        "finalizer_journal_byte_count": publication["bytes"],
        "finalizer_published_object_sha256": publication["sha256"],
        "finalizer_content_chain_sha256": finalizer_readback["content_chain_sha256"],
        "finalizer_journal_version_id": publication["version_id"], "finalizer_journal_etag": publication["etag"],
        "finalizer_publication_receipt_identity": finalizer_readback["publication_receipt_identity"],
        "finalizer_publication_receipt_sha256": finalizer_readback["publication_receipt_identity"]["sha256"],
        "finalizer_readback_receipt_identity": finalizer_readback["readback_receipt_identity"],
        "finalizer_readback_receipt_sha256": finalizer_readback["readback_receipt_identity"]["sha256"],
        "finalizer_envelope_count": len(finalizer_envelopes), "finalizer_aggregate_sha256": finalizer_aggregate,
        "last_substantive_s3_operation_completed_utc": finalizer_terminal_membership["operation_completed_utc"],
        "total_envelope_count": total_envelopes, "combined_order_and_hash_chain_sha256": combined_aggregate,
        "excluded_evidence_channel_operations_in_order": ["PUT_CONTROLLER_CAPTURE_JOURNAL", "GET_EXACT_CONTROLLER_CAPTURE_JOURNAL", "PUT_CONTROLLER_JOURNAL_HANDOFF", "PUT_FINALIZER_CAPTURE_JOURNAL", "GET_EXACT_FINALIZER_CAPTURE_JOURNAL"],
        "all_substantive_s3_operations_present": True, "no_later_substantive_s3_operation": True,
        "step_functions_carried_full_history": False, "full_history_embedded_in_closure_response": False,
        "aggregate_disposition": "TWO_EXACT_VERSIONED_JOURNALS_PLUS_ONE_FIXED_KEY_CARRIER_WITH_FIVE_ENUMERATED_RECURSIVE_EXCEPTIONS_COMPLETE_SUBSTANTIVE_S3_SEQUENCE_FIXED_SIZE_FINAL_NON_S3_CLOSURE_PASS",
        "proof_body_excluded_fields_in_order": ["proof_sha256", "proof_body_byte_count", "proof_body_excluded_fields_in_order", "proof_body_projection_disposition"],
        "proof_body_projection_disposition": "VALIDATOR_RFC8785_CANONICALIZES_THE_COMPLETE_FIXED_SIZE_FINAL_S3_CAPTURE_AGGREGATE_WITH_EXACTLY_FOUR_DERIVED_BODY_FIELDS_REMOVED;THE_PROJECTION_CONTAINS_NO_JOURNAL_BYTES_ENVELOPE_ARRAYS_OR_JOURNAL_PREIMAGES_PASS",
        "proof_hash_domain": proof_domain,
        "proof_hash_formula": "SHA256(DOMAIN_UTF8_CONCAT_RFC8785_CANONICAL_COMPLETE_FINAL_S3_CAPTURE_AGGREGATE_WITH_EXACT_FOUR_DERIVED_BODY_FIELDS_REMOVED)",
        "fixed_size_identity_and_receipt_hash_binding_disposition": "EXACT_EIGHT_TYPED_IDENTITY_TO_RECEIPT_OR_PUBLISHED_OBJECT_HASH_BINDINGS_EXACT_TEN_CARRIER_EXTERNAL_PROOF_MEMBERSHIP_COORDINATE_AND_IDENTITY_BINDINGS_AND_EXACT_SIX_ANTISPLICE_BINDINGS_FOR_DECODED_HANDOFF_ATTEMPT_CONTROLLER_COORDINATES_PUBLICATION_READBACK_LOCAL_VALIDATION_AND_EXTERNAL_PROOF_TO_AGGREGATE_CARRIER_IDENTITY_AND_DIGEST_EXECUTED_WITH_NO_JOURNAL_BYTES_ENVELOPES_OR_JOURNAL_PREIMAGES_EMBEDDED_PASS",
        "prepare_request_get_capture_aggregate_sha256": prepare_aggregate,
        "controller_prepare_get_subsequence_cross_binding_receipt": prepare_receipt,
        "controller_local_journal_validation_receipt_identity": handoff["controller_local_validation_receipt_identity"],
        "controller_local_journal_validation_receipt_sha256": handoff["controller_local_validation_receipt_sha256"],
        "finalizer_local_journal_validation_receipt_identity": identity("aws_c0_finalizer_journal_local_validation_receipt/v1", finalizer_local_sha),
        "finalizer_local_journal_validation_receipt_sha256": finalizer_local_sha,
        "controller_terminal_result_put_operation_capture_identity": controller_terminal_membership["selected_operation_capture_identity"],
        "controller_terminal_result_put_completed_utc": controller_terminal_membership["operation_completed_utc"],
        "controller_terminal_result_put_membership_receipt": controller_terminal_membership,
        "controller_terminal_receipt_identity": controller_terminal_identity,
        "controller_terminal_receipt_key": controller_terminal_capture["key"],
        "finalizer_terminal_manifest_put_operation_capture_identity": finalizer_terminal_membership["selected_operation_capture_identity"],
        "finalizer_terminal_manifest_put_completed_utc": finalizer_terminal_membership["operation_completed_utc"],
        "finalizer_terminal_manifest_put_membership_receipt": finalizer_terminal_membership,
        "finalizer_terminal_manifest_identity": final_manifest_identity,
        "finalizer_terminal_manifest_key": final_manifest_receipt["key"],
        "lambda_application_release_operation_coverage_receipt": lambda_coverage,
        "controller_aggregate_hash_domain": controller_domain,
        "controller_aggregate_hash_formula": "SHA256(DOMAIN_UTF8_CONCAT_PREFIX_ORDERED_ENVELOPE_OPERATION_CAPTURE_IDENTITY_VALUES_PREIMAGE_HASHES_AND_CHAIN_LINKS)",
        "finalizer_aggregate_hash_domain": finalizer_domain,
        "finalizer_aggregate_hash_formula": "SHA256(DOMAIN_UTF8_CONCAT_PREFIX_ORDERED_ENVELOPE_OPERATION_CAPTURE_IDENTITY_VALUES_PREIMAGE_HASHES_AND_CHAIN_LINKS)",
        "combined_aggregate_hash_domain": combined_domain,
        "combined_aggregate_hash_formula": "SHA256(DOMAIN_UTF8_CONCAT_CONTROLLER_AGGREGATE_SHA256_CONCAT_FINALIZER_AGGREGATE_SHA256_CONCAT_INT64BE_TOTAL_ENVELOPE_COUNT)",
        "controller_journal_bucket_name": controller_object["bucket"], "controller_journal_key": controller_object["key"],
        "finalizer_journal_bucket_name": controller_object["bucket"], "finalizer_journal_key": finalizer_key,
        "journal_coordinate_receipt_equalities_in_order": [
            {"journal_role": "CONTROLLER", "coordinate_fields": ["bucket_name", "key", "version_id", "etag", "checksum_sha256_base64", "published_object_sha256", "content_chain_sha256"], "sources": ["CONTROLLER_PUBLICATION_RECEIPT", "CONTROLLER_READBACK_RECEIPT", "FINAL_FIXED_SIZE_AGGREGATE"]},
            {"journal_role": "CARRIER", "coordinate_fields": ["bucket_name", "key", "version_id", "etag", "checksum_sha256_base64", "byte_count", "object_sha256", "carrier_identity", "carrier_digest"], "sources": ["FINALIZER_LIST_CAPTURE", "FINALIZER_CARRIER_GET_CAPTURE", "FINAL_FIXED_SIZE_AGGREGATE"]},
            {"journal_role": "FINALIZER", "coordinate_fields": ["bucket_name", "key", "version_id", "etag", "checksum_sha256_base64", "published_object_sha256", "content_chain_sha256"], "sources": ["FINALIZER_PUBLICATION_RECEIPT", "FINALIZER_READBACK_RECEIPT", "FINAL_FIXED_SIZE_AGGREGATE"]},
        ],
        "three_key_pairwise_distinctness_execution_receipt": _pairwise_key_receipt(controller_object["key"], carrier_key, finalizer_key),
        "final_manifest_publication_observation_identity": publication_observation_identity,
        "final_manifest_publication_observation_preimage": publication_observation,
        "final_manifest_publication_observation_preimage_byte_count": len(observation_raw),
        "final_manifest_publication_observation_preimage_sha256": publication_observation_identity["sha256"],
        "final_manifest_publication_observation_hash_domain": "AWS_C0_FINAL_MANIFEST_PUBLICATION_OBSERVATION_V2_NUL",
        "final_manifest_publication_observation_hash_formula": "SHA256(DOMAIN_UTF8_CONCAT_RFC8785_CANONICAL_COMPLETE_STRUCTURED_FINAL_MANIFEST_PUBLICATION_OBSERVATION_V2_PREIMAGE)",
        "final_manifest_canonical_byte_count": final_manifest_receipt["bytes"],
        "final_manifest_put_response_etag": final_manifest_put_response["etag"],
        "final_manifest_put_response_x_amz_request_id": final_manifest_put_response["request_id"],
        "final_manifest_publication_observation_binding_disposition": "THE_FIXED_SIZE_STRUCTURED_V2_OBSERVATION_IS_DERIVED_IN_MEMORY_FROM_THE_TERMINAL_FINAL_MANIFEST_PUT_CAPTURE_AND_PRE_EXISTING_RETRIEVAL_ROOT;NO_OBSERVATION_S3_OBJECT_IS_CREATED;EXACT_TWELVE_RECEIPTS_BIND_DIRECT_STRUCTURED_COUNT_DOMAIN_HASH_IDENTITY_MANIFEST_PAYLOAD_AND_CONTENT_HASH_CANONICAL_BYTE_COUNT_VERSION_CHECKSUM_REQUEST_ID_ETAG_AND_RETRIEVAL_ROOT_PASS",
        "controller_journal_checksum_sha256_base64": controller_object["checksum_sha256_base64"],
        "finalizer_journal_checksum_sha256_base64": publication["checksum_sha256_base64"],
        "preserved_programme_count_disposition": "JOURNALS_ARE_TWO_NON_SEMANTIC_AUXILIARIES_AND_DO_NOT_CHANGE_21_PRELIVE_12_ROOT_63_READ_PLAN_352_PARENT_OR_878_AXIS_COUNTS",
    }
    fixed_rows = [
        ("FIXED_SIZE_IDENTITY_AND_RECEIPT_HASH_BINDING_RECEIPTS_IN_ORDER_001", "/controller_journal_identity/sha256,/controller_journal_identity/value", "/controller_published_object_sha256", "BOTH_SHA256_EQUAL"),
        ("FIXED_SIZE_IDENTITY_AND_RECEIPT_HASH_BINDING_RECEIPTS_IN_ORDER_002", "/finalizer_journal_identity/sha256,/finalizer_journal_identity/value", "/finalizer_published_object_sha256", "BOTH_SHA256_EQUAL"),
        ("FIXED_SIZE_IDENTITY_AND_RECEIPT_HASH_BINDING_RECEIPTS_IN_ORDER_003", "/controller_publication_receipt_identity/sha256,/controller_publication_receipt_identity/value", "/controller_publication_receipt_sha256", "BOTH_SHA256_EQUAL"),
        ("FIXED_SIZE_IDENTITY_AND_RECEIPT_HASH_BINDING_RECEIPTS_IN_ORDER_004", "/controller_readback_receipt_identity/sha256,/controller_readback_receipt_identity/value", "/controller_readback_receipt_sha256", "BOTH_SHA256_EQUAL"),
        ("FIXED_SIZE_IDENTITY_AND_RECEIPT_HASH_BINDING_RECEIPTS_IN_ORDER_005", "/finalizer_publication_receipt_identity/sha256,/finalizer_publication_receipt_identity/value", "/finalizer_publication_receipt_sha256", "BOTH_SHA256_EQUAL"),
        ("FIXED_SIZE_IDENTITY_AND_RECEIPT_HASH_BINDING_RECEIPTS_IN_ORDER_006", "/finalizer_readback_receipt_identity/sha256,/finalizer_readback_receipt_identity/value", "/finalizer_readback_receipt_sha256", "BOTH_SHA256_EQUAL"),
        ("FIXED_SIZE_IDENTITY_AND_RECEIPT_HASH_BINDING_RECEIPTS_IN_ORDER_007", "/controller_local_journal_validation_receipt_identity/sha256,/controller_local_journal_validation_receipt_identity/value", "/controller_local_journal_validation_receipt_sha256", "BOTH_SHA256_EQUAL"),
        ("FIXED_SIZE_IDENTITY_AND_RECEIPT_HASH_BINDING_RECEIPTS_IN_ORDER_008", "/finalizer_local_journal_validation_receipt_identity/sha256,/finalizer_local_journal_validation_receipt_identity/value", "/finalizer_local_journal_validation_receipt_sha256", "BOTH_SHA256_EQUAL"),
        ("FIXED_SIZE_CARRIER_EXTERNAL_PROOF_IDENTITY_DIGEST_009", "/controller_journal_handoff_external_publication_readback_proof/carrier_identity/sha256,/controller_journal_handoff_external_publication_readback_proof/carrier_identity/value", "/controller_journal_handoff_external_publication_readback_proof/carrier_digest", "BOTH_SHA256_EQUAL"),
        ("CARRIER_THREE_MEMBERSHIPS_BIND_FINALIZER_JOURNAL_010", "/controller_journal_handoff_external_publication_readback_proof/finalizer_list_membership_receipt/journal_published_object_sha256,/controller_journal_handoff_external_publication_readback_proof/finalizer_carrier_get_membership_receipt/journal_published_object_sha256,/controller_journal_handoff_external_publication_readback_proof/finalizer_controller_journal_get_membership_receipt/journal_published_object_sha256", "/finalizer_published_object_sha256", "ALL_SHA256_EQUAL"),
        ("CARRIER_CONTROLLER_JOURNAL_GET_PRECEDES_TERMINAL_PUT_011", "/controller_journal_handoff_external_publication_readback_proof/terminal_final_manifest_put_requested_utc", "/finalizer_terminal_manifest_put_membership_receipt/operation_requested_utc", "UTC_EQUAL"),
        ("CARRIER_EXTERNAL_PROOF_GET_OBJECT_SHA256_012", "/controller_journal_handoff_external_publication_readback_proof/object_sha256", "/controller_journal_handoff_object_sha256", "CANONICAL_VALUE_EQUAL"),
        ("CARRIER_EXTERNAL_PROOF_BUCKET_013", "/controller_journal_handoff_external_publication_readback_proof/bucket", "/controller_journal_handoff_bucket_name", "CANONICAL_VALUE_EQUAL"),
        ("CARRIER_EXTERNAL_PROOF_KEY_014", "/controller_journal_handoff_external_publication_readback_proof/key", "/controller_journal_handoff_key", "CANONICAL_VALUE_EQUAL"),
        ("CARRIER_EXTERNAL_PROOF_VERSION_015", "/controller_journal_handoff_external_publication_readback_proof/version_id", "/controller_journal_handoff_version_id", "CANONICAL_VALUE_EQUAL"),
        ("CARRIER_EXTERNAL_PROOF_ETAG_016", "/controller_journal_handoff_external_publication_readback_proof/etag", "/controller_journal_handoff_etag", "CANONICAL_VALUE_EQUAL"),
        ("CARRIER_EXTERNAL_PROOF_CHECKSUM_017", "/controller_journal_handoff_external_publication_readback_proof/checksum_sha256_base64", "/controller_journal_handoff_checksum_sha256_base64", "CANONICAL_VALUE_EQUAL"),
        ("CARRIER_EXTERNAL_PROOF_BYTES_018", "/controller_journal_handoff_external_publication_readback_proof/byte_count", "/controller_journal_handoff_byte_count", "INTEGER_EQUAL"),
        ("CARRIER_DECODED_HANDOFF_ATTEMPT_TO_AGGREGATE_019", "/controller_journal_handoff_external_publication_readback_proof/decoded_controller_journal_handoff/attempt_identity/sha256,/controller_journal_handoff_external_publication_readback_proof/decoded_controller_journal_handoff/attempt_identity/value", "/attempt_identity/sha256,/attempt_identity/value", "PREFIX_ORDERED_PAIRWISE_SHA256_EQUAL"),
        ("CARRIER_DECODED_HANDOFF_CONTROLLER_COORDINATES_TO_AGGREGATE_020", "/controller_journal_handoff_external_publication_readback_proof/decoded_controller_journal_handoff/controller_journal_object/bucket,/controller_journal_handoff_external_publication_readback_proof/decoded_controller_journal_handoff/controller_journal_object/key,/controller_journal_handoff_external_publication_readback_proof/decoded_controller_journal_handoff/controller_journal_object/version_id,/controller_journal_handoff_external_publication_readback_proof/decoded_controller_journal_handoff/controller_journal_object/etag,/controller_journal_handoff_external_publication_readback_proof/decoded_controller_journal_handoff/controller_journal_object/checksum_sha256_base64,/controller_journal_handoff_external_publication_readback_proof/decoded_controller_journal_handoff/controller_journal_object/byte_count,/controller_journal_handoff_external_publication_readback_proof/decoded_controller_journal_handoff/controller_journal_object/object_sha256,/controller_journal_handoff_external_publication_readback_proof/decoded_controller_journal_handoff/controller_journal_object/content_chain_sha256", "/controller_journal_bucket_name,/controller_journal_key,/controller_journal_version_id,/controller_journal_etag,/controller_journal_checksum_sha256_base64,/controller_journal_byte_count,/controller_published_object_sha256,/controller_content_chain_sha256", "PREFIX_ORDERED_CANONICAL_VALUE_EQUAL"),
        ("CARRIER_DECODED_HANDOFF_CONTROLLER_PUBLICATION_RECEIPT_TO_AGGREGATE_021", "/controller_journal_handoff_external_publication_readback_proof/decoded_controller_journal_handoff/controller_publication_receipt_identity/sha256,/controller_journal_handoff_external_publication_readback_proof/decoded_controller_journal_handoff/controller_publication_receipt_identity/value,/controller_journal_handoff_external_publication_readback_proof/decoded_controller_journal_handoff/controller_publication_receipt/receipt_sha256", "/controller_publication_receipt_identity/sha256,/controller_publication_receipt_identity/value,/controller_publication_receipt_sha256", "PREFIX_ORDERED_CANONICAL_VALUE_EQUAL"),
        ("CARRIER_DECODED_HANDOFF_CONTROLLER_READBACK_RECEIPT_TO_AGGREGATE_022", "/controller_journal_handoff_external_publication_readback_proof/decoded_controller_journal_handoff/controller_readback_receipt_identity/sha256,/controller_journal_handoff_external_publication_readback_proof/decoded_controller_journal_handoff/controller_readback_receipt_identity/value,/controller_journal_handoff_external_publication_readback_proof/decoded_controller_journal_handoff/controller_readback_receipt/receipt_sha256", "/controller_readback_receipt_identity/sha256,/controller_readback_receipt_identity/value,/controller_readback_receipt_sha256", "PREFIX_ORDERED_CANONICAL_VALUE_EQUAL"),
        ("CARRIER_DECODED_HANDOFF_CONTROLLER_LOCAL_VALIDATION_RECEIPT_TO_AGGREGATE_023", "/controller_journal_handoff_external_publication_readback_proof/decoded_controller_journal_handoff/controller_local_validation_receipt_identity/sha256,/controller_journal_handoff_external_publication_readback_proof/decoded_controller_journal_handoff/controller_local_validation_receipt_identity/value,/controller_journal_handoff_external_publication_readback_proof/decoded_controller_journal_handoff/controller_local_validation_receipt_sha256", "/controller_local_journal_validation_receipt_identity/sha256,/controller_local_journal_validation_receipt_identity/value,/controller_local_journal_validation_receipt_sha256", "PREFIX_ORDERED_CANONICAL_VALUE_EQUAL"),
        ("CARRIER_EXTERNAL_PROOF_IDENTITY_DIGEST_TO_AGGREGATE_024", "/controller_journal_handoff_external_publication_readback_proof/carrier_identity/sha256,/controller_journal_handoff_external_publication_readback_proof/carrier_identity/value,/controller_journal_handoff_external_publication_readback_proof/carrier_digest", "/controller_journal_handoff_identity/sha256,/controller_journal_handoff_identity/value,/controller_journal_handoff_sha256", "PREFIX_ORDERED_CANONICAL_VALUE_EQUAL"),
    ]
    receipt_specials = {
        fixed_rows[20][1]: [handoff["controller_publication_receipt_identity"]["sha256"]] * 3,
        fixed_rows[21][1]: [handoff["controller_readback_receipt_identity"]["sha256"]] * 3,
    }
    aggregate["fixed_size_identity_and_receipt_hash_binding_receipts_in_order"] = _execution_rows(
        aggregate, fixed_rows, receipt_specials)
    terminal_rows = [
        ("TERMINAL_OPERATION_CROSS_BINDING_RECEIPTS_IN_ORDER_001", "/controller_terminal_result_put_membership_receipt/selected_operation_capture_identity", "/controller_terminal_result_put_operation_capture_identity", "IDENTITY_EQUAL"),
        ("TERMINAL_OPERATION_CROSS_BINDING_RECEIPTS_IN_ORDER_002", "/controller_terminal_result_put_membership_receipt/operation_completed_utc", "/controller_terminal_result_put_completed_utc", "TIMESTAMP_EQUAL"),
        ("TERMINAL_OPERATION_CROSS_BINDING_RECEIPTS_IN_ORDER_003", "/controller_terminal_result_put_membership_receipt/envelope_sequence", "/controller_terminal_result_put_membership_receipt/journal_envelope_count", "INTEGER_EQUAL"),
        ("TERMINAL_OPERATION_CROSS_BINDING_RECEIPTS_IN_ORDER_004", "/controller_terminal_result_put_membership_receipt/expected_source_object_identity", "/controller_terminal_receipt_identity", "IDENTITY_EQUAL"),
        ("TERMINAL_OPERATION_CROSS_BINDING_RECEIPTS_IN_ORDER_005", "/controller_terminal_result_put_membership_receipt/expected_key", "/controller_terminal_receipt_key", "UTF8_BYTEWISE_EQUAL"),
        ("TERMINAL_OPERATION_CROSS_BINDING_RECEIPTS_IN_ORDER_006", "/finalizer_terminal_manifest_put_membership_receipt/selected_operation_capture_identity", "/finalizer_terminal_manifest_put_operation_capture_identity", "IDENTITY_EQUAL"),
        ("TERMINAL_OPERATION_CROSS_BINDING_RECEIPTS_IN_ORDER_007", "/finalizer_terminal_manifest_put_membership_receipt/operation_completed_utc", "/finalizer_terminal_manifest_put_completed_utc", "TIMESTAMP_EQUAL"),
        ("TERMINAL_OPERATION_CROSS_BINDING_RECEIPTS_IN_ORDER_008", "/finalizer_terminal_manifest_put_membership_receipt/envelope_sequence", "/finalizer_terminal_manifest_put_membership_receipt/journal_envelope_count", "INTEGER_EQUAL"),
        ("TERMINAL_OPERATION_CROSS_BINDING_RECEIPTS_IN_ORDER_009", "/finalizer_terminal_manifest_put_membership_receipt/expected_source_object_identity", "/finalizer_terminal_manifest_identity", "IDENTITY_EQUAL"),
        ("TERMINAL_OPERATION_CROSS_BINDING_RECEIPTS_IN_ORDER_010", "/finalizer_terminal_manifest_put_membership_receipt/expected_key", "/finalizer_terminal_manifest_key", "UTF8_BYTEWISE_EQUAL"),
        ("TERMINAL_OPERATION_CROSS_BINDING_RECEIPTS_IN_ORDER_011", "/last_substantive_s3_operation_completed_utc", "/finalizer_terminal_manifest_put_completed_utc", "TIMESTAMP_EQUAL"),
    ]
    aggregate["terminal_operation_cross_binding_receipts_in_order"] = _execution_rows(aggregate, terminal_rows)
    arithmetic_rows = [
        ("AGGREGATE_ARITHMETIC_TIME_AND_HASH_EXECUTION_RECEIPTS_IN_ORDER_001", "/controller_prepare_get_subsequence_cross_binding_receipt/memberships_in_source_role_order/0/journal_envelope_count", "/controller_envelope_count", "INTEGER_EQUAL"),
        ("AGGREGATE_ARITHMETIC_TIME_AND_HASH_EXECUTION_RECEIPTS_IN_ORDER_002", "/finalizer_terminal_manifest_put_membership_receipt/journal_envelope_count", "/finalizer_envelope_count", "INTEGER_EQUAL"),
        ("AGGREGATE_ARITHMETIC_TIME_AND_HASH_EXECUTION_RECEIPTS_IN_ORDER_003", "/controller_envelope_count,/finalizer_envelope_count", "/total_envelope_count", "INTEGER_SUM_EQUAL"),
        ("AGGREGATE_ARITHMETIC_TIME_AND_HASH_EXECUTION_RECEIPTS_IN_ORDER_004", "/controller_prepare_get_subsequence_cross_binding_receipt/memberships_in_source_role_order/0/journal_content_chain_sha256", "/controller_content_chain_sha256", "SHA256_EQUAL"),
        ("AGGREGATE_ARITHMETIC_TIME_AND_HASH_EXECUTION_RECEIPTS_IN_ORDER_005", "/finalizer_terminal_manifest_put_membership_receipt/journal_content_chain_sha256", "/finalizer_content_chain_sha256", "SHA256_EQUAL"),
        ("AGGREGATE_ARITHMETIC_TIME_AND_HASH_EXECUTION_RECEIPTS_IN_ORDER_006", "/lambda_application_release_operation_coverage_receipt/finalizer_journal_published_object_sha256,/lambda_application_release_operation_coverage_receipt/finalizer_journal_content_chain_sha256,/lambda_application_release_operation_coverage_receipt/finalizer_journal_envelope_count", "/finalizer_published_object_sha256,/finalizer_content_chain_sha256,/finalizer_envelope_count", "THREE_FIELDS_EQUAL"),
        ("AGGREGATE_ARITHMETIC_TIME_AND_HASH_EXECUTION_RECEIPTS_IN_ORDER_007", "/lambda_application_release_operation_coverage_receipt/terminal_request_envelope_sha256,/lambda_application_release_operation_coverage_receipt/terminal_operation_completed_utc,/lambda_application_release_operation_coverage_receipt/terminal_membership_receipt_sha256", "/finalizer_terminal_manifest_put_membership_receipt/selected_request_envelope_sha256,/finalizer_terminal_manifest_put_membership_receipt/operation_completed_utc,/finalizer_terminal_manifest_put_membership_receipt/membership_receipt_sha256", "THREE_FIELDS_EQUAL"),
        ("AGGREGATE_ARITHMETIC_TIME_AND_HASH_EXECUTION_RECEIPTS_IN_ORDER_008", "/controller_aggregate_sha256,/finalizer_aggregate_sha256,/total_envelope_count", "/combined_order_and_hash_chain_sha256", "DOMAIN_SEPARATED_COMBINED_AGGREGATE_RECOMPUTE"),
        ("AGGREGATE_ARITHMETIC_TIME_AND_HASH_EXECUTION_RECEIPTS_IN_ORDER_009", "/finalizer_terminal_manifest_put_completed_utc", "/last_substantive_s3_operation_completed_utc", "TIMESTAMP_EQUAL"),
    ]
    aggregate["aggregate_arithmetic_time_and_hash_execution_receipts_in_order"] = _execution_rows(
        aggregate, arithmetic_rows, {arithmetic_rows[7][1]: combined_aggregate})

    coordinate_configs = [
        ("CONTROLLER", "/controller_publication_receipt_identity", "/controller_publication_receipt_sha256",
         "/controller_readback_receipt_identity", "/controller_readback_receipt_sha256",
         "/controller_local_journal_validation_receipt_identity", "/controller_local_journal_validation_receipt_sha256",
         ["/controller_journal_bucket_name", "/controller_journal_key", "/controller_journal_version_id", "/controller_journal_etag", "/controller_journal_checksum_sha256_base64", "/controller_journal_byte_count", "/controller_published_object_sha256", "/controller_content_chain_sha256", "/controller_envelope_count", "/controller_aggregate_sha256"],
         "controller-capture-journal.json", "AWS_C0_FIXED_SIZE_CONTROLLER_JOURNAL_COORDINATE_VALIDATION_RECEIPT_V1_NUL",
         "SHA256(DOMAIN_UTF8_CONCAT_PUBLICATION_RECEIPT_IDENTITY_VALUE_CONCAT_PUBLICATION_RECEIPT_SHA256_CONCAT_READBACK_RECEIPT_IDENTITY_VALUE_CONCAT_READBACK_RECEIPT_SHA256_CONCAT_LOCAL_VALIDATION_RECEIPT_IDENTITY_VALUE_CONCAT_LOCAL_VALIDATION_RECEIPT_SHA256_CONCAT_PREFIX_ORDERED_ROOT_COORDINATE_VALUES)"),
        ("CARRIER", "/controller_journal_handoff_external_publication_readback_proof/finalizer_list_capture_identity", "/controller_journal_handoff_external_publication_readback_proof/finalizer_list_capture_preimage/capture_sha256",
         "/controller_journal_handoff_external_publication_readback_proof/finalizer_carrier_get_capture_identity", "/controller_journal_handoff_external_publication_readback_proof/finalizer_carrier_get_capture_preimage/capture_sha256",
         "/controller_journal_handoff_external_publication_readback_proof/carrier_identity", "/controller_journal_handoff_external_publication_readback_proof/carrier_digest",
         ["/controller_journal_handoff_bucket_name", "/controller_journal_handoff_key", "/controller_journal_handoff_version_id", "/controller_journal_handoff_etag", "/controller_journal_handoff_checksum_sha256_base64", "/controller_journal_handoff_byte_count", "/controller_journal_handoff_object_sha256", "/controller_journal_handoff_identity", "/controller_journal_handoff_sha256"],
         "controller-capture-journal-handoff.json", "AWS_C0_FIXED_SIZE_CARRIER_COORDINATE_VALIDATION_RECEIPT_V1_NUL",
         "SHA256(DOMAIN_UTF8_CONCAT_LIST_GET_MEMBERSHIP_AND_EXTERNAL_PROOF_IDENTITY_DIGEST_CONCAT_PREFIX_ORDERED_ROOT_COORDINATE_VALUES)"),
        ("FINALIZER", "/finalizer_publication_receipt_identity", "/finalizer_publication_receipt_sha256",
         "/finalizer_readback_receipt_identity", "/finalizer_readback_receipt_sha256",
         "/finalizer_local_journal_validation_receipt_identity", "/finalizer_local_journal_validation_receipt_sha256",
         ["/finalizer_journal_bucket_name", "/finalizer_journal_key", "/finalizer_journal_version_id", "/finalizer_journal_etag", "/finalizer_journal_checksum_sha256_base64", "/finalizer_journal_byte_count", "/finalizer_published_object_sha256", "/finalizer_content_chain_sha256", "/finalizer_envelope_count", "/finalizer_aggregate_sha256"],
         "finalizer-capture-journal.json", "AWS_C0_FIXED_SIZE_FINALIZER_JOURNAL_COORDINATE_VALIDATION_RECEIPT_V1_NUL",
         "SHA256(DOMAIN_UTF8_CONCAT_PUBLICATION_RECEIPT_IDENTITY_VALUE_CONCAT_PUBLICATION_RECEIPT_SHA256_CONCAT_READBACK_RECEIPT_IDENTITY_VALUE_CONCAT_READBACK_RECEIPT_SHA256_CONCAT_LOCAL_VALIDATION_RECEIPT_IDENTITY_VALUE_CONCAT_LOCAL_VALIDATION_RECEIPT_SHA256_CONCAT_PREFIX_ORDERED_ROOT_COORDINATE_VALUES)"),
    ]
    coordinate_receipts = []
    for role, pub_id, pub_sha, read_id, read_sha, local_id, local_sha, pointers, suffix, domain, formula in coordinate_configs:
        preimage = {"journal_role": role, "publication_receipt_identity_pointer": pub_id,
                    "publication_receipt_sha256_pointer": pub_sha,
                    "readback_receipt_identity_pointer": read_id,
                    "readback_receipt_sha256_pointer": read_sha,
                    "local_validation_receipt_identity_pointer": local_id,
                    "local_validation_receipt_sha256_pointer": local_sha,
                    "root_coordinate_pointers_in_order": pointers, "role_specific_key_suffix": suffix,
                    "coordinate_validation_hash_domain": domain,
                    "coordinate_validation_hash_formula": formula,
                    "all_local_receipt_coordinates_equal_root": True}
        preimage["execution_receipt_sha256"] = digest(domain.encode() + b"\0" + canonical_bytes(preimage))
        coordinate_receipts.append(preimage)
    aggregate["journal_coordinate_receipt_equality_execution_receipts_in_order"] = coordinate_receipts

    observation_rows = [
        ("FINAL_MANIFEST_PUBLICATION_OBSERVATION_BINDING_001", "RFC8785_CANONICAL_STRUCTURED_OBSERVATION_UTF8_BYTE_COUNT", "/final_manifest_publication_observation_preimage_byte_count", "INTEGER_EQUAL"),
        ("FINAL_MANIFEST_PUBLICATION_OBSERVATION_BINDING_002", "/final_manifest_publication_observation_hash_domain,/final_manifest_publication_observation_hash_formula", "/final_manifest_publication_observation_preimage_sha256", "DOMAIN_SEPARATED_DIRECT_STRUCTURED_PROJECTION_SHA256_EQUAL"),
        ("FINAL_MANIFEST_PUBLICATION_OBSERVATION_BINDING_003", "/final_manifest_publication_observation_identity/sha256,/final_manifest_publication_observation_identity/value", "/final_manifest_publication_observation_preimage_sha256", "BOTH_SHA256_EQUAL"),
        ("FINAL_MANIFEST_PUBLICATION_OBSERVATION_BINDING_004", "/final_manifest_publication_observation_preimage/attempt_identity", "/attempt_identity", "IDENTITY_VALUE_EQUAL"),
        ("FINAL_MANIFEST_PUBLICATION_OBSERVATION_BINDING_005", "/final_manifest_publication_observation_preimage/final_manifest_identity", "/finalizer_terminal_manifest_identity", "TYPED_IDENTITY_BYTEWISE_EQUAL"),
        ("FINAL_MANIFEST_PUBLICATION_OBSERVATION_BINDING_006", "/final_manifest_publication_observation_preimage/final_manifest_object/bucket_identity,/final_manifest_publication_observation_preimage/final_manifest_object/key", "RESOLVED_EXPECTED_BUCKET_IDENTITY_FOR_/finalizer_terminal_manifest_put_membership_receipt/expected_bucket_name,/finalizer_terminal_manifest_put_membership_receipt/expected_key", "TYPED_BUCKET_IDENTITY_AND_UTF8_KEY_EQUAL"),
        ("FINAL_MANIFEST_PUBLICATION_OBSERVATION_BINDING_007", "/final_manifest_publication_observation_preimage/final_manifest_object/sha256,/final_manifest_publication_observation_preimage/final_manifest_identity/value", "RESOLVED_FINALIZER_TERMINAL_SELECTED_OPERATION_CAPTURE_PREIMAGE/sigv4_capture_preimage/payload_sha256", "BOTH_SHA256_EQUAL"),
        ("FINAL_MANIFEST_PUBLICATION_OBSERVATION_BINDING_008", "/final_manifest_publication_observation_preimage/final_manifest_object/bytes", "/final_manifest_canonical_byte_count", "INTEGER_EQUAL"),
        ("FINAL_MANIFEST_PUBLICATION_OBSERVATION_BINDING_009", "/final_manifest_publication_observation_preimage/final_manifest_object/version_id,/final_manifest_publication_observation_preimage/final_manifest_object/checksum_sha256_base64", "RESOLVED_FINALIZER_TERMINAL_SELECTED_OPERATION_CAPTURE_PREIMAGE/response_envelope_preimage/version_id,/response_envelope_preimage/checksum_sha256_base64", "VERSION_ID_AND_CHECKSUM_BYTEWISE_EQUAL"),
        ("FINAL_MANIFEST_PUBLICATION_OBSERVATION_BINDING_010", "/final_manifest_put_response_x_amz_request_id", "RESOLVED_FINALIZER_TERMINAL_SELECTED_OPERATION_CAPTURE_PREIMAGE/response_envelope_preimage/x_amz_request_id", "UTF8_BYTEWISE_EQUAL"),
        ("FINAL_MANIFEST_PUBLICATION_OBSERVATION_BINDING_011", "/final_manifest_put_response_etag", "RESOLVED_FINALIZER_TERMINAL_SELECTED_OPERATION_CAPTURE_PREIMAGE/response_envelope_preimage/etag", "UTF8_BYTEWISE_EQUAL"),
        ("FINAL_MANIFEST_PUBLICATION_OBSERVATION_BINDING_012", "/final_manifest_publication_observation_preimage/retrieval_verification_identity,/final_manifest_publication_observation_preimage/retrieval_object", "RESOLVED_PRE_EXISTING_RETRIEVAL_VERIFICATION_IDENTITY_AND_OBJECT_ROOT", "TYPED_IDENTITY_AND_OBJECT_RECEIPT_BYTEWISE_EQUAL"),
    ]
    observation_specials = {
        observation_rows[0][1]: len(observation_raw),
        observation_rows[1][1]: publication_observation_identity["sha256"],
        observation_rows[5][2]: [final_manifest_receipt["bucket_identity"], final_manifest_receipt["key"]],
        observation_rows[6][1]: [final_manifest_receipt["sha256"], final_manifest_receipt["sha256"]],
        observation_rows[6][2]: final_manifest_receipt["sha256"],
        observation_rows[8][2]: [final_manifest_receipt["version_id"], final_manifest_receipt["checksum_sha256_base64"]],
        observation_rows[9][2]: final_manifest_put_response["request_id"],
        observation_rows[10][2]: final_manifest_put_response["etag"],
        observation_rows[11][2]: [retrieval_identity, retrieval_receipt],
    }
    aggregate["final_manifest_publication_observation_binding_receipts_in_order"] = _execution_rows(
        aggregate, observation_rows, observation_specials)
    proof_projection = {name: value for name, value in aggregate.items()
                        if name not in {"proof_sha256", "proof_body_byte_count",
                                        "proof_body_excluded_fields_in_order",
                                        "proof_body_projection_disposition"}}
    proof_raw = canonical_bytes(proof_projection)
    aggregate["proof_body_byte_count"] = len(proof_raw)
    aggregate["proof_sha256"] = digest(proof_domain.encode() + b"\0" + proof_raw)
    return aggregate


def _identity(record: dict[str, Any], field: str, kind: str) -> str:
    item = record.get(field)
    if not isinstance(item, dict) or set(item) != {"kind", "sha256", "value"}:
        raise Refusal(f"invalid identity object: {field}")
    if item["kind"] != kind or item["sha256"] != item["value"] or not SHA.fullmatch(item["sha256"]):
        raise Refusal(f"identity kind/digest mismatch: {field}")
    return item["sha256"]


def _utc(value: Any) -> dt.datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise Refusal("UTC timestamp required")
    try:
        parsed = dt.datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise Refusal("invalid UTC") from exc
    if parsed.tzinfo != dt.timezone.utc:
        raise Refusal("non-UTC timestamp")
    return parsed


def _root_digest(record: dict[str, Any]) -> str:
    claimed = record.get("record_sha256")
    if not isinstance(claimed, str) or not SHA.fullmatch(claimed):
        raise Refusal("root digest absent")
    preimage = dict(record)
    preimage.pop("record_sha256")
    if digest(canonical_bytes(preimage)) != claimed:
        raise Refusal("root digest mismatch")
    return claimed


def _nonroot_digest(record: dict[str, Any], raw: bytes, schema: str) -> str:
    """Bind a control record to every stored byte, never to a root preimage."""
    if record.get("schema") != schema or "record_sha256" in record:
        raise Refusal("non-root control record boundary failed")
    if canonical_bytes(record) != raw:
        raise Refusal("non-root control bytes are not canonical")
    return digest(raw)


def _root_common(record: dict[str, Any], schema: str, *, corrected: bool) -> str:
    expected = {
        "schema": schema, "authority_id": AUTHORITY_ID,
        "record_class": "NON_SCIENTIFIC_AWS_C0_EVIDENCE",
        "scientific_execution_authorized": False,
        "stage_f_readiness_claimed": False, "zero_science_counters": ZERO,
    }
    if corrected:
        expected.update({"correction_authority_id": CORRECTION_ID,
                         "stage_f_execution_authorized": False})
    for key, value in expected.items():
        if record.get(key) != value:
            raise Refusal(f"root common field mismatch:{schema}:{key}")
    _utc(record.get("observed_utc"))
    return _root_digest(record)


def _env(name: str, pattern: re.Pattern[str] | None = None) -> str:
    value = os.environ.get(name, "")
    if not value or (pattern is not None and not pattern.fullmatch(value)):
        raise Refusal(f"invalid sealed environment: {name}")
    return value


def _signing_key(secret: str, day: str, service: str) -> bytes:
    date_key = hmac.new(("AWS4" + secret).encode(), day.encode(), hashlib.sha256).digest()
    region_key = hmac.new(date_key, REGION.encode(), hashlib.sha256).digest()
    service_key = hmac.new(region_key, service.encode(), hashlib.sha256).digest()
    return hmac.new(service_key, b"aws4_request", hashlib.sha256).digest()


def _aws_request(service: str, method: str, host: str, path: str,
                 query: list[tuple[str, str]], body: bytes,
                 headers: dict[str, str] | None = None) -> tuple[bytes, dict[str, str]]:
    access = _env("AWS_ACCESS_KEY_ID")
    secret = _env("AWS_SECRET_ACCESS_KEY")
    token = _env("AWS_SESSION_TOKEN")
    now = dt.datetime.now(dt.timezone.utc)
    amzdate = now.strftime("%Y%m%dT%H%M%SZ")
    day = now.strftime("%Y%m%d")
    canonical_query = urllib.parse.urlencode(sorted(query), quote_via=urllib.parse.quote)
    canonical_uri = urllib.parse.quote(path, safe="/-_.~")
    request_headers = {"host": host, "x-amz-date": amzdate,
                       "x-amz-security-token": token,
                       "x-amz-content-sha256": digest(body)}
    for key, value in (headers or {}).items():
        request_headers[key.lower()] = value.strip()
    names = sorted(request_headers)
    canonical_headers = "".join(f"{name}:{' '.join(request_headers[name].split())}\n" for name in names)
    signed_headers = ";".join(names)
    canonical_request = "\n".join((method, canonical_uri, canonical_query,
                                      canonical_headers, signed_headers, digest(body)))
    scope = f"{day}/{REGION}/{service}/aws4_request"
    to_sign = "\n".join(("AWS4-HMAC-SHA256", amzdate, scope,
                           digest(canonical_request.encode())))
    signature = hmac.new(_signing_key(secret, day, service), to_sign.encode(), hashlib.sha256).hexdigest()
    request_headers["authorization"] = (
        f"AWS4-HMAC-SHA256 Credential={access}/{scope}, "
        f"SignedHeaders={signed_headers}, Signature={signature}"
    )
    url = f"https://{host}{canonical_uri}"
    if canonical_query:
        url += "?" + canonical_query
    operation = ("LIST_OBJECT_VERSIONS" if service == "s3" and method == "GET" and path == "/" and
                 ("versions", "") in query else
                 "GET_OBJECT_EXACT_VERSION" if service == "s3" and method == "GET" and
                 any(name == "versionId" for name, _ in query) else
                 "PUT_OBJECT" if service == "s3" and method == "PUT" else f"{service.upper()}_{method}")
    requested_utc = now.isoformat(timespec="microseconds").replace("+00:00", "Z")
    request_projection = {"service": service, "method": method, "host": host,
                          "path": canonical_uri, "query": canonical_query,
                          "payload_sha256": digest(body), "signed_headers": signed_headers}
    capture = {"service": service, "method": method, "host": host, "path": canonical_uri,
               "query_sha256": digest(canonical_query.encode()), "request_body_sha256": digest(body),
               "sigv4_algorithm": "AWS4-HMAC-SHA256", "signed_headers": signed_headers,
               "operation": operation, "operation_requested_utc": requested_utc,
               "request_envelope_sha256": digest(canonical_bytes(request_projection))}
    journal = _ACTIVE_JOURNAL
    if journal is not None:
        journal.reserve(capture)
    request = urllib.request.Request(url, data=body if method != "GET" else None,
                                     headers=request_headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            raw = response.read(MAX_BYTES + 1)
            if len(raw) > MAX_BYTES:
                raise Refusal("AWS response too large")
            observed = {key.lower(): value for key, value in response.headers.items()}
            if journal is not None:
                completed_capture = {**capture, "response_sha256": digest(raw),
                    "observed_version_id": observed.get("x-amz-version-id"),
                    "observed_etag": observed.get("etag"),
                    "observed_checksum_sha256": observed.get("x-amz-checksum-sha256"),
                    "observed_request_id": observed.get("x-amz-request-id"),
                    "source_object_identity": identity("aws_c0_s3_object/v1", digest(raw)),
                    "operation_completed_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")}
                if operation == "LIST_OBJECT_VERSIONS":
                    completed_capture["response_body_base64"] = base64.b64encode(raw).decode()
                journal.append(operation, completed_capture, "OBSERVED_COMPLETE")
            return raw, observed
    except urllib.error.HTTPError as exc:
        if journal is not None:
            journal.append(operation, {**capture, "failure_class": "HTTPError", "status": exc.code,
                           "operation_completed_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")},
                           "OBSERVED_FAILURE")
        raise Refusal(f"AWS {service} request refused:{exc.code}") from exc
    except urllib.error.URLError as exc:
        if journal is not None:
            journal.append(operation, {**capture, "failure_class": "URLError",
                           "operation_completed_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")},
                           "OBSERVED_FAILURE")
        raise Refusal(f"AWS {service} unavailable") from exc


def _finalizer_journal_publisher(bucket: str, key: str, raw: bytes) -> dict[str, Any]:
    checksum = base64.b64encode(hashlib.sha256(raw).digest()).decode()
    _, headers = _aws_request("s3", "PUT", f"{bucket}.s3.{REGION}.amazonaws.com", "/" + key, [], raw,
                              {"if-none-match": "*", "x-amz-checksum-sha256": checksum, "content-type": "application/json"})
    version = headers.get("x-amz-version-id")
    etag = headers.get("etag")
    if (not isinstance(version, str) or not VERSION.fullmatch(version) or
            not isinstance(etag, str) or not etag):
        raise Refusal("finalizer journal Put version refused")
    return {"key": key, "version_id": version, "etag": etag,
            "bytes": len(raw), "sha256": digest(raw),
            "checksum_sha256_base64": checksum}


def _finalizer_journal_readback(bucket: str, key: str, version: str) -> tuple[bytes, dict[str, Any]]:
    raw, headers = _aws_request("s3", "GET", f"{bucket}.s3.{REGION}.amazonaws.com", "/" + key,
                                [("versionId", version)], b"", {"x-amz-checksum-mode": "ENABLED"})
    checksum = base64.b64encode(hashlib.sha256(raw).digest()).decode()
    etag = headers.get("etag")
    if (headers.get("x-amz-version-id") != version or
            headers.get("x-amz-checksum-sha256") != checksum or
            not isinstance(etag, str) or not etag):
        raise Refusal("finalizer journal readback authentication refused")
    return raw, {"key": key, "version_id": version, "etag": etag,
                 "bytes": len(raw), "sha256": digest(raw),
                 "checksum_sha256_base64": checksum,
                 "request_id": headers.get("x-amz-request-id")}


def _query(service: str, action: str, parameters: dict[str, str]) -> ET.Element:
    host = "iam.amazonaws.com" if service == "iam" else f"{service}.{REGION}.amazonaws.com"
    pairs = [("Action", action), ("Version", {
        "ec2": "2016-11-15", "iam": "2010-05-08",
        "cloudformation": "2010-05-15", "sts": "2011-06-15",
    }[service]), *sorted(parameters.items())]
    body = urllib.parse.urlencode(pairs, quote_via=urllib.parse.quote).encode()
    raw, _ = _aws_request(service, "POST", host, "/", [], body,
                          {"content-type": "application/x-www-form-urlencoded; charset=utf-8"})
    try:
        return ET.fromstring(raw)
    except ET.ParseError as exc:
        raise Refusal(f"invalid {service} response") from exc


def _json_api(service: str, target: str, payload: dict[str, Any]) -> dict[str, Any]:
    body = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    raw, _ = _aws_request(service, "POST", f"{service}.{REGION}.amazonaws.com", "/", [], body,
                          {"content-type": "application/x-amz-json-1.1", "x-amz-target": target})
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise Refusal(f"invalid {service} JSON response") from exc
    if not isinstance(value, dict):
        raise Refusal(f"invalid {service} response shape")
    return value


def _xml_text(root: ET.Element, local: str) -> str | None:
    for item in root.iter():
        if item.tag.rsplit("}", 1)[-1] == local:
            return item.text
    return None


def _s3_get(bucket: str, key: str, version: str, expected: str,
            expected_bytes: int | None = None) -> bytes:
    if not VERSION.fullmatch(version) or not SHA.fullmatch(expected):
        raise Refusal("invalid object receipt")
    raw, headers = _aws_request("s3", "GET", f"{bucket}.s3.{REGION}.amazonaws.com",
                                "/" + key, [("versionId", version)], b"")
    if headers.get("x-amz-version-id") != version or digest(raw) != expected:
        raise Refusal("exact-version readback mismatch")
    if expected_bytes is not None and len(raw) != expected_bytes:
        raise Refusal("object byte count mismatch")
    return raw


def _s3_put(bucket: str, key: str, raw: bytes) -> dict[str, Any]:
    checksum = base64.b64encode(hashlib.sha256(raw).digest()).decode()
    _, headers = _aws_request("s3", "PUT", f"{bucket}.s3.{REGION}.amazonaws.com",
                              "/" + key, [], raw,
                              {"content-type": "application/json", "if-none-match": "*",
                               "x-amz-checksum-sha256": checksum})
    version = headers.get("x-amz-version-id", "")
    etag = headers.get("etag", "")
    request_id = headers.get("x-amz-request-id", "")
    if not VERSION.fullmatch(version) or not etag or not request_id:
        raise Refusal("fresh version receipt absent")
    return {"key": key, "version_id": version, "bytes": len(raw),
            "sha256": digest(raw), "checksum_sha256_base64": checksum,
            "etag": etag, "request_id": request_id}


def _s3_version_entries(bucket: str, prefix: str, max_pages: int,
                        max_items: int) -> tuple[list[dict[str, str]], dict[str, Any]]:
    """Consume bounded ListObjectVersions pages; latest-only reads are forbidden."""
    entries: list[dict[str, str]] = []; pages: list[dict[str, Any]] = []
    key_marker: str | None = None; version_marker: str | None = None
    seen_tokens: set[tuple[str | None, str | None]] = set(); delete_count = 0
    for page_index in range(max_pages):
        incoming = [key_marker, version_marker]
        query = [("versions", ""), ("prefix", prefix)]
        if key_marker is not None: query.append(("key-marker", key_marker))
        if version_marker is not None: query.append(("version-id-marker", version_marker))
        raw, _ = _aws_request("s3", "GET", f"{bucket}.s3.{REGION}.amazonaws.com", "/", query, b"")
        try: root = ET.fromstring(raw)
        except ET.ParseError as exc: raise Refusal("invalid S3 version page") from exc
        page_count = 0
        for item in root.iter():
            local = item.tag.rsplit("}", 1)[-1]
            if local not in {"Version", "DeleteMarker"}: continue
            values = {child.tag.rsplit("}", 1)[-1]: child.text for child in item}
            key = values.get("Key", ""); version = values.get("VersionId", "")
            if not key.startswith(prefix) or not VERSION.fullmatch(version): raise Refusal("version coordinate invalid")
            page_count += 1
            if local == "DeleteMarker": delete_count += 1
            else: entries.append({"key": key, "version_id": version})
        if len(entries) + delete_count > max_items: raise Refusal("S3 version item bound exceeded")
        truncated = _xml_text(root, "IsTruncated")
        next_key = _xml_text(root, "NextKeyMarker") if truncated == "true" else None
        next_version = _xml_text(root, "NextVersionIdMarker") if truncated == "true" else None
        outgoing = (next_key, next_version)
        if outgoing in seen_tokens: raise Refusal("repeated S3 pagination token")
        seen_tokens.add(outgoing)
        request_preimage = {"api_action": "s3:ListObjectVersions", "bucket_identity": _bucket_identity(),
                            "prefix": prefix, "key_marker": key_marker,
                            "version_id_marker": version_marker}
        pages.append({"page_index": page_index,
                      "request_sha256": digest(canonical_bytes(request_preimage)),
                      "response_sha256": digest(raw),
                      "incoming_token_sha256": None if incoming == [None, None] else digest(canonical_bytes(incoming)),
                      "outgoing_token_sha256": None if outgoing == (None, None) else digest(canonical_bytes(list(outgoing))),
                      "terminal": truncated == "false"})
        if truncated == "false":
            coords = {(e["key"], e["version_id"]) for e in entries}
            if len(coords) != len(entries): raise Refusal("duplicate S3 version coordinate")
            if delete_count or len({e["key"] for e in entries}) != len(entries):
                raise Refusal("delete marker or multiple versions for fresh evidence key")
            transcript_preimage = {"schema": "aws_c0_pagination_transcript/v1", "source_api": "s3:ListObjectVersions",
                "pages": pages, "page_count": len(pages), "version_count": len(entries),
                "delete_marker_count": delete_count, "duplicate_coordinate_count": 0,
                "event_count": 0, "sealed_max_pages": max_pages, "sealed_max_items": max_items,
                "sealed_max_events": max_items, "all_pages_consumed": True,
                "terminal_marker_observed": True, "repeated_token_observed": False}
            transcript = {**transcript_preimage,
                          "identity": identity("aws_c0_pagination_transcript/v1",
                                               digest(canonical_bytes(transcript_preimage)))}
            return entries, transcript
        if truncated != "true" or not next_key: raise Refusal("S3 pagination terminal state invalid")
        key_marker, version_marker = next_key, next_version
    raise Refusal("S3 version page bound exceeded")


def validate_controller_journal_handoff_v1(value: Any, *, bucket: str,
                                           key: str,
                                           attempt_identity: dict[str, str]) -> dict[str, Any]:
    """Validate the acyclic carrier before trusting its journal coordinate."""
    required = {
        "schema", "attempt_identity", "controller_journal_object",
        "controller_publication_receipt", "controller_readback_receipt",
        "controller_publication_receipt_identity", "controller_readback_receipt_identity",
        "controller_local_validation_receipt_identity", "controller_local_validation_receipt_sha256",
        "controller_receipt_coordinate_execution_receipts_in_order", "zero_science_counters",
        "handoff_canonical_body_byte_count", "handoff_body_excluded_fields_in_order",
        "handoff_body_projection_disposition", "handoff_hash_domain", "handoff_hash_formula",
        "handoff_identity", "handoff_canonical_sha256",
        "handoff_identity_recomputation_disposition",
    }
    if (not isinstance(value, dict) or set(value) != required or
            value.get("schema") != "controller_journal_handoff_v1" or
            value.get("attempt_identity") != attempt_identity or
            value.get("zero_science_counters") != ZERO or
            value.get("handoff_hash_domain") != HANDOFF_HASH_DOMAIN or
            tuple(value.get("handoff_body_excluded_fields_in_order", ())) != HANDOFF_EXCLUDED_FIELDS):
        raise Refusal("controller journal handoff fields refused")
    core = {name: item for name, item in value.items() if name not in HANDOFF_EXCLUDED_FIELDS}
    core_raw = canonical_bytes(core)
    handoff_sha = digest(HANDOFF_HASH_DOMAIN.encode() + b"\0" + core_raw)
    if (value["handoff_canonical_body_byte_count"] != len(core_raw) or
            value["handoff_canonical_sha256"] != handoff_sha or
            value["handoff_identity"] != identity("aws_c0_controller_journal_handoff/v1", handoff_sha)):
        raise Refusal("controller journal handoff identity refused")
    publication = value["controller_publication_receipt"]
    readback = value["controller_readback_receipt"]
    coordinate_fields = ("key", "version_id", "etag", "byte_count", "published_object_sha256",
                         "checksum_sha256_base64", "content_chain_sha256")
    if (not isinstance(publication, dict) or
            publication.get("schema") != "aws_c0_capture_journal_publication_receipt/v1" or
            publication.get("journal_role") != "CONTROLLER" or
            publication.get("bucket_name") != bucket or
            publication.get("attempt_identity") != attempt_identity or
            not isinstance(readback, dict) or
            readback.get("schema") != "aws_c0_capture_journal_readback_receipt/v1" or
            readback.get("journal_role") != "CONTROLLER" or readback.get("bucket_name") != bucket or
            readback.get("attempt_identity") != attempt_identity or
            any(publication.get(name) != readback.get(name) for name in coordinate_fields)):
        raise Refusal("controller journal handoff receipt preimages refused")
    publication_identity = identity("aws_c0_capture_journal_publication_receipt/v1",
                                    publication.get("receipt_sha256", ""))
    readback_identity = identity("aws_c0_capture_journal_readback_receipt/v1",
                                 readback.get("receipt_sha256", ""))
    if (value["controller_publication_receipt_identity"] != publication_identity or
            value["controller_readback_receipt_identity"] != readback_identity):
        raise Refusal("controller journal handoff receipt identity refused")
    journal_object = value["controller_journal_object"]
    object_required = {"bucket", "key", "version_id", "etag", "checksum_sha256_base64",
                       "byte_count", "object_sha256", "content_chain_sha256"}
    if (not isinstance(journal_object, dict) or set(journal_object) != object_required or
            journal_object["bucket"] != bucket or
            journal_object["key"] != publication["key"] or
            not journal_object["key"].endswith("/" + CONTROLLER_JOURNAL_SUFFIX) or
            journal_object["version_id"] != publication["version_id"] or
            journal_object["etag"] != publication["etag"] or
            journal_object["checksum_sha256_base64"] != publication["checksum_sha256_base64"] or
            journal_object["byte_count"] != publication["byte_count"] or
            journal_object["object_sha256"] != publication["published_object_sha256"] or
            journal_object["content_chain_sha256"] != publication["content_chain_sha256"] or
            not SHA.fullmatch(str(journal_object["content_chain_sha256"]))):
        raise Refusal("controller journal handoff object coordinate refused")
    receipts = value["controller_receipt_coordinate_execution_receipts_in_order"]
    if not isinstance(receipts, list) or len(receipts) != 22:
        raise Refusal("controller journal handoff coordinate receipts refused")
    comparison_root = {
        "attempt_identity": attempt_identity, "controller_journal_object": journal_object,
        "controller_publication_receipt": publication, "controller_readback_receipt": readback,
        "controller_publication_receipt_identity": publication_identity,
        "controller_readback_receipt_identity": readback_identity,
    }
    for order, (receipt, expected_row) in enumerate(
            zip(receipts, CONTROLLER_HANDOFF_COORDINATE_ROWS), 1):
        observed_row = tuple(receipt.get(name) for name in
                             ("descriptor_id", "left", "right", "comparison")) \
            if isinstance(receipt, dict) else ()
        if observed_row != expected_row:
            raise Refusal("controller journal handoff fixed coordinate row refused")
        _validate_execution_receipt(receipt, order, comparison_root)
    local_preimage = {
        **comparison_root,
        "coordinate_receipt_sha256s": [row["receipt_sha256"] for row in receipts],
    }
    local_sha = digest(canonical_bytes(local_preimage))
    if (value["controller_local_validation_receipt_sha256"] != local_sha or
            value["controller_local_validation_receipt_identity"] != identity(
                "aws_c0_controller_journal_local_validation_receipt/v1", local_sha)):
        raise Refusal("controller journal handoff local validation receipt refused")
    if not key.endswith("/" + CONTROLLER_JOURNAL_HANDOFF_SUFFIX):
        raise Refusal("controller journal handoff carrier key refused")
    return value


def _discover_controller_journal_handoff(bucket: str, prefix: str,
                                         attempt_identity: dict[str, str]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Capture List, exact carrier Get, and exact controller-journal Get."""
    if _ACTIVE_JOURNAL is None:
        raise Refusal("controller handoff discovery requires active finalizer journal")
    capture_start = len(_ACTIVE_JOURNAL.envelopes)
    key = prefix + CONTROLLER_JOURNAL_HANDOFF_SUFFIX
    entries, transcript = _s3_version_entries(bucket, key, 1, 1)
    matches = [entry for entry in entries if entry["key"] == key]
    if len(matches) != 1:
        raise Refusal("controller journal handoff has no unique listed version")
    version = matches[0]["version_id"]
    raw, headers = _aws_request(
        "s3", "GET", f"{bucket}.s3.{REGION}.amazonaws.com", "/" + key,
        [("versionId", version)], b"", {"x-amz-checksum-mode": "ENABLED"})
    checksum = base64.b64encode(hashlib.sha256(raw).digest()).decode()
    etag = headers.get("etag")
    if (headers.get("x-amz-version-id") != version or
            headers.get("x-amz-checksum-sha256") != checksum or
            not isinstance(etag, str) or not etag):
        raise Refusal("controller journal handoff exact-version Get refused")
    handoff = validate_controller_journal_handoff_v1(
        strict_json(raw), bucket=bucket, key=key, attempt_identity=attempt_identity)
    coordinate = handoff["controller_journal_object"]
    journal_raw, journal_headers = _aws_request(
        "s3", "GET", f"{bucket}.s3.{REGION}.amazonaws.com", "/" + coordinate["key"],
        [("versionId", coordinate["version_id"])], b"",
        {"x-amz-checksum-mode": "ENABLED"})
    journal_checksum = base64.b64encode(hashlib.sha256(journal_raw).digest()).decode()
    if (journal_headers.get("x-amz-version-id") != coordinate["version_id"] or
            journal_headers.get("etag") != coordinate["etag"] or
            journal_headers.get("x-amz-checksum-sha256") != journal_checksum or
            journal_checksum != coordinate["checksum_sha256_base64"] or
            len(journal_raw) != coordinate["byte_count"] or
            digest(journal_raw) != coordinate["object_sha256"]):
        raise Refusal("controller journal exact-version validation refused")
    journal = strict_json(journal_raw)
    journal_required = {"schema", "producer", "envelopes", "envelope_count",
                        "canonical_envelope_bytes", "content_chain_sha256"}
    if (not isinstance(journal, dict) or set(journal) != journal_required or
            journal.get("schema") != "aws_c0_controller_capture_journal/v1" or
            journal.get("producer") != "EC2_INSTANCE_PROFILE_CONTROLLER" or
            not isinstance(journal.get("envelopes"), list) or
            journal["envelope_count"] != len(journal["envelopes"])):
        raise Refusal("controller journal complete bytes refused")
    previous = None
    for envelope in journal["envelopes"]:
        if not isinstance(envelope, dict) or envelope.get("previous_envelope_sha256") != previous:
            raise Refusal("controller journal chain refused")
        previous = digest(canonical_bytes(envelope))
    if previous != journal["content_chain_sha256"] or previous != coordinate["content_chain_sha256"]:
        raise Refusal("controller journal terminal chain refused")
    observation = {
        "schema": "aws_c0_controller_journal_handoff_external_proof_internal/v1",
        "key": key, "version_id": version, "etag": etag,
        "checksum_sha256_base64": checksum, "bytes": len(raw), "sha256": digest(raw),
        "list_transcript_identity": transcript["identity"],
        "handoff_identity": handoff["handoff_identity"],
        "handoff_canonical_sha256": handoff["handoff_canonical_sha256"],
        "controller_journal_version_id": coordinate["version_id"],
        "controller_publication_receipt_identity": handoff["controller_publication_receipt_identity"],
        "controller_envelope_count": journal["envelope_count"],
        "list_capture_sequence": capture_start + 1,
        "carrier_get_capture_sequence": capture_start + 2,
        "controller_journal_get_capture_sequence": capture_start + 3,
        "controller_journal": journal,
    }
    if len(_ACTIVE_JOURNAL.envelopes) != capture_start + 3:
        raise Refusal("controller handoff discovery capture count refused")
    return handoff, observation


def _s3_unique_version(bucket: str, key: str) -> str:
    """Resolve one content-addressed key to exactly one immutable VersionId.

    Evidence roots cannot carry their own S3 receipt without a circular root
    preimage. ListObjectVersions is therefore the accepted discovery step.
    More than one version or any delete marker refuses instead of choosing the
    mutable latest version.
    """
    versions: list[str] = []
    delete_marker = False
    key_marker: str | None = None
    version_marker: str | None = None
    for _page in range(20):
        query = [("versions", ""), ("prefix", key)]
        if key_marker is not None:
            query.append(("key-marker", key_marker))
        if version_marker is not None:
            query.append(("version-id-marker", version_marker))
        raw, _ = _aws_request("s3", "GET", f"{bucket}.s3.{REGION}.amazonaws.com",
                              "/", query, b"")
        try:
            root = ET.fromstring(raw)
        except ET.ParseError as exc:
            raise Refusal("invalid S3 version listing") from exc
        for item in root.iter():
            local = item.tag.rsplit("}", 1)[-1]
            if local not in {"Version", "DeleteMarker"}:
                continue
            values = {child.tag.rsplit("}", 1)[-1]: child.text for child in item}
            if values.get("Key") != key:
                continue
            if local == "DeleteMarker":
                delete_marker = True
                continue
            version = values.get("VersionId", "")
            if not VERSION.fullmatch(version):
                raise Refusal("S3 evidence VersionId invalid")
            versions.append(version)
        truncated = _xml_text(root, "IsTruncated")
        if truncated == "false":
            if delete_marker or len(versions) != 1:
                raise Refusal("evidence key does not have one immutable version")
            return versions[0]
        if truncated != "true":
            raise Refusal("S3 version truncation state absent")
        next_key = _xml_text(root, "NextKeyMarker")
        next_version = _xml_text(root, "NextVersionIdMarker")
        if not next_key or (next_key, next_version) == (key_marker, version_marker):
            raise Refusal("S3 version continuation is invalid")
        key_marker, version_marker = next_key, next_version
    raise Refusal("S3 version listing exceeds sealed twenty-request maximum")


def _s3_exact_key(bucket: str, key: str) -> tuple[bytes, str]:
    """Read a uniquely discovered exact version and verify all stored bytes."""
    version = _s3_unique_version(bucket, key)
    raw, headers = _aws_request("s3", "GET", f"{bucket}.s3.{REGION}.amazonaws.com",
                                "/" + key, [("versionId", version)], b"",
                                {"x-amz-checksum-mode": "ENABLED"})
    expected = headers.get("x-amz-checksum-sha256", "")
    if headers.get("x-amz-version-id") != version or not expected:
        raise Refusal("exact evidence version/checksum absent")
    actual = base64.b64encode(hashlib.sha256(raw).digest()).decode()
    if actual != expected:
        raise Refusal("exact evidence checksum mismatch")
    return raw, version


def _observed_receipt(key: str, version: str, raw: bytes) -> dict[str, Any]:
    """Create a receipt only after an exact-version, checksum-verified read."""
    return {"key": key, "version_id": version, "bytes": len(raw), "sha256": digest(raw)}


def _evidence_receipt(value: dict[str, Any]) -> dict[str, Any]:
    """Project an S3 Put response to the frozen original four-field receipt."""
    return {key: value[key] for key in ("key", "version_id", "bytes", "sha256")}


def _receipt(value: Any) -> dict[str, Any]:
    required = {"bucket_identity", "key", "version_id", "bytes", "sha256", "checksum_sha256_base64"}
    if not isinstance(value, dict) or set(value) != required:
        raise Refusal("object receipt is not closed")
    _identity(value, "bucket_identity", "aws_s3_bucket/v1")
    if type(value["bytes"]) is not int or value["bytes"] < 1:
        raise Refusal("invalid receipt bytes")
    if not SHA.fullmatch(value["sha256"]) or not VERSION.fullmatch(value["version_id"]):
        raise Refusal("invalid receipt hashes")
    if value["checksum_sha256_base64"] != base64.b64encode(bytes.fromhex(value["sha256"])).decode():
        raise Refusal("receipt checksum/digest mismatch")
    return value


def _bucket_from_receipt(receipt: dict[str, Any]) -> str:
    bucket = _env("AWS_C0_ARTIFACT_BUCKET", BUCKET)
    expected = _env("AWS_C0_BUCKET_IDENTITY_SHA256", SHA)
    if _identity(receipt, "bucket_identity", "aws_s3_bucket/v1") != expected:
        raise Refusal("bucket identity mismatch")
    return bucket

DIMENSIONS = (
    "instance_running_seconds", "public_ipv4_seconds", "nat_gateway_seconds", "vpc_endpoint_seconds",
    "s3_put_requests", "s3_get_requests", "s3_head_requests", "s3_list_requests",
    "step_functions_transitions", "lambda_invocations", "lambda_duration_milliseconds", "kms_requests",
    "kms_key_seconds", "data_transfer_bytes", "cloudwatch_ingested_bytes", "ebs_volume_gib_seconds",
    "ebs_provisioned_iops_seconds", "ebs_provisioned_throughput_mibps_seconds",
    "s3_version_byte_seconds", "cloudwatch_log_byte_seconds", "ecr_byte_seconds", "snapshot_gib_seconds",
)
UNITS = dict(zip(DIMENSIONS, (
    "SECOND", "SECOND", "SECOND", "SECOND", "REQUEST", "REQUEST", "REQUEST", "REQUEST",
    "TRANSITION", "INVOCATION", "MILLISECOND", "REQUEST", "SECOND", "BYTE", "BYTE",
    "GIB_SECOND", "IOPS_SECOND", "MIBPS_SECOND", "BYTE_SECOND", "BYTE_SECOND",
    "BYTE_SECOND", "GIB_SECOND",
)))
ROOT_KINDS = (
    "aws_c0_cost_runtime_closure_authority_audit/v1",
    "aws_c0_cost_runtime_closure_static_validation/v1",
    "aws_c0_private_infrastructure_snapshot/v1",
    "aws_c0_launch_request/v4", "aws_c0_start_receipt/v5", "aws_c0_heartbeat/v1",
    "aws_c0_checkpoint/v1", "aws_c0_terminal_receipt/v1", "aws_c0_finalizer_receipt/v2",
    "aws_c0_retrieval_verification/v4", "aws_c0_cost_closure/v2", "aws_c0_final_manifest/v4",
)
COMMON_FIELDS = {"schema", "authority_id", "correction_authority_id", "closure_correction_authority_id",
    "record_class", "scientific_execution_authorized", "stage_f_execution_authorized", "stage_f_readiness_claimed",
    "zero_science_counters", "observed_utc"}
LIVE_PACKET_V2_FIELDS = COMMON_FIELDS | {"packet_disposition", "preparation_closure_identity", "preparation_closure_object",
    "launch_request_identity", "launch_request_object", "pre_live_predecessor_object_receipts", "live_authorization_key_target",
    "runtime_control_preimages", "change_set_identity", "change_set_observation_identity", "effect_api_set_identity",
    "effect_resource_set_identity", "live_session_assumer_identity", "execution_operator_role_identity",
    "execution_session_policy_identity", "execution_session_policy_canonical_json_base64",
    "execution_session_policy_ceiling_identity", "execution_session_policy_ceiling_canonical_json_base64",
    "execution_session_policy_subset_proof_identity", "execution_session_policy_subset_proof_canonical_json_base64",
    "pass_role_scope_proof_identity", "pass_role_scope_proof_canonical_json_base64", "execution_session_max_duration_seconds",
    "live_session_assumer_expires_utc", "iam_pagination_bounds", "final_preflight_observed_utc", "final_instance_state",
    "pre_live_object_count"}
LIVE_AUTH_V2_FIELDS = COMMON_FIELDS | {"statement_sha256", "authenticated_source_identity", "live_packet_identity",
    "live_packet_object", "live_authorization_key", "account_identity", "attempt_identity", "change_set_identity",
    "live_session_assumer_identity", "execution_operator_role_identity", "execution_session_policy_identity",
    "execution_session_policy_canonical_json_base64", "execution_session_policy_ceiling_identity",
    "execution_session_policy_ceiling_canonical_json_base64", "execution_session_policy_subset_proof_identity",
    "execution_session_policy_subset_proof_canonical_json_base64", "pass_role_scope_proof_identity",
    "pass_role_scope_proof_canonical_json_base64", "execution_session_max_duration_seconds", "execution_session_identity",
    "execution_session_derivation_proof_identity", "execution_session_derivation_proof_canonical_json_base64",
    "execution_session_expires_utc", "authorized_actions", "denied_actions"}
LAUNCH_V3_FIELDS = COMMON_FIELDS | {"record_sha256", "rehearsal_id", "attempt_id", "attempt_identity", "region",
    "instance_id", "required_initial_instance_state", "artifact_prefix", "preparation_packet_identity",
    "preparation_packet_object", "preparation_authorization_identity", "preparation_authorization_object",
    "authority_audit_identity", "authority_audit_object", "static_validation_identity", "static_validation_object",
    "private_infrastructure_snapshot_identity", "private_infrastructure_snapshot_object", "cost_model_identity",
    "cost_model_object", "closure_seed_identity", "closure_seed_object", "artifact_version_receipts",
    "phase_timeouts_seconds", "deployed_lambda_timeout_seconds", "state_machine_timeout_seconds",
    "heartbeat_interval_seconds", "checkpoint_interval_seconds", "attempt_deadline_utc", "cleanup_deadline_utc",
    "iam_pagination_bounds", "cost_envelope", "retry_attempts", "cleanup_path"}
CATEGORY = {
    ROOT_KINDS[0]: "AUTHORITY_AUDIT", ROOT_KINDS[1]: "STATIC_VALIDATION",
    ROOT_KINDS[2]: "SNAPSHOT", ROOT_KINDS[3]: "LAUNCH", ROOT_KINDS[4]: "START",
    ROOT_KINDS[5]: "HEARTBEAT", ROOT_KINDS[6]: "CHECKPOINT", ROOT_KINDS[7]: "TERMINAL",
    ROOT_KINDS[8]: "FINALIZER", ROOT_KINDS[9]: "RETRIEVAL", ROOT_KINDS[10]: "COST",
    ROOT_KINDS[11]: "FINAL_MANIFEST",
}


def _common(record: dict[str, Any], schema: str, *, root: bool) -> str:
    expected = {
        "schema": schema, "authority_id": AUTHORITY_ID, "correction_authority_id": CORRECTION_ID,
        "closure_correction_authority_id": CLOSURE_ID,
        "scientific_execution_authorized": False, "stage_f_execution_authorized": False,
        "stage_f_readiness_claimed": False, "zero_science_counters": ZERO,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            raise Refusal(f"common field mismatch:{schema}:{field}")
    _utc(record.get("observed_utc"))
    return _root_digest(record) if root else digest(canonical_bytes(record))


def _bucket_identity() -> dict[str, str]:
    return identity("aws_s3_bucket/v1", _env("AWS_C0_BUCKET_IDENTITY_SHA256", SHA))


def _full_receipt(value: dict[str, Any]) -> dict[str, Any]:
    return {"bucket_identity": _bucket_identity(), **value}


def _put_record(bucket: str, prefix: str, category: str, record: dict[str, Any],
                *, root: bool, include_response: bool = False) -> Any:
    raw = canonical_bytes(record)
    record_id = _root_digest(record) if root else digest(raw)
    key = f"{prefix}{category}-{record_id}.json"
    response = _s3_put(bucket, key, raw)
    receipt = _full_receipt({name: response[name] for name in
                             ("key", "version_id", "bytes", "sha256", "checksum_sha256_base64")})
    pair = (identity(record["schema"], record_id), receipt)
    return (*pair, response) if include_response else pair


def _root_record(schema: str, fields: dict[str, Any]) -> dict[str, Any]:
    record = {
        "schema": schema, "authority_id": AUTHORITY_ID, "correction_authority_id": CORRECTION_ID,
        "closure_correction_authority_id": CLOSURE_ID,
        "record_class": "NON_SCIENTIFIC_AWS_C0_EVIDENCE",
        "scientific_execution_authorized": False, "stage_f_execution_authorized": False,
        "stage_f_readiness_claimed": False, "zero_science_counters": ZERO,
        "observed_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        **fields,
    }
    record["record_sha256"] = digest(canonical_bytes(record))
    return record


def _control_record(schema: str, fields: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": schema, "authority_id": AUTHORITY_ID, "correction_authority_id": CORRECTION_ID,
        "closure_correction_authority_id": CLOSURE_ID,
        "record_class": "NON_SCIENTIFIC_AWS_C0_CONTROL_EVIDENCE",
        "scientific_execution_authorized": False, "stage_f_execution_authorized": False,
        "stage_f_readiness_claimed": False, "zero_science_counters": ZERO,
        "observed_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        **fields,
    }


def _fetch_receipt(receipt: Any, expected_schema: str, *, root: bool) -> tuple[dict[str, Any], bytes, str]:
    value = _receipt(receipt)
    bucket = _bucket_from_receipt(value)
    raw = _s3_get(bucket, value["key"], value["version_id"], value["sha256"], value["bytes"])
    record = strict_json(raw)
    if not isinstance(record, dict) or record.get("schema") != expected_schema:
        raise Refusal(f"wrong exact record schema:{expected_schema}")
    record_id = _root_digest(record) if root else _nonroot_digest(record, raw, expected_schema)
    return record, raw, record_id


def _validate_launch_v3(record: Any) -> dict[str, Any]:
    if not isinstance(record, dict) or set(record) != LAUNCH_V3_FIELDS:
        raise Refusal("launch-v3 field closure failed")
    _common(record, "aws_c0_launch_request/v4", root=True)
    if record.get("region") != REGION or record.get("instance_id") != INSTANCE_ID:
        raise Refusal("launch target mismatch")
    if record.get("required_initial_instance_state") != "stopped" or record.get("retry_attempts") != 1:
        raise Refusal("launch replay/initial state mismatch")
    if record.get("cleanup_path") != "STEP_FUNCTIONS_SINGLE_STOP_THEN_FINALIZER_VERIFY":
        raise Refusal("launch cleanup path mismatch")
    attempt = record.get("attempt_id", "")
    if not re.fullmatch(r"ATTEMPT-[A-Z0-9-]{1,64}-(SUCCESS|FAIL-AFTER-CHECKPOINT|TIMEOUT)", attempt):
        raise Refusal("launch attempt suffix invalid")
    if record.get("artifact_prefix") != f"rehearsal/aws-c0/{record.get('rehearsal_id')}/{attempt}/":
        raise Refusal("launch prefix mismatch")
    _identity(record, "attempt_identity", "aws_c0_attempt/v1")
    _identity(record, "cost_model_identity", "aws_c0_cost_model/v2")
    _identity(record, "closure_seed_identity", "aws_c0_closure_seed/v1")
    if len(record.get("artifact_version_receipts", [])) != 8:
        raise Refusal("launch artifact receipt arithmetic")
    timeouts = record.get("phase_timeouts_seconds", {})
    if set(timeouts) != {"boot", "ssm_online", "ssm_start_delivery", "heartbeat_stale", "worker_runtime", "finalizer", "instance_stop", "overall"}:
        raise Refusal("launch timeout closure")
    if timeouts["finalizer"] > record.get("deployed_lambda_timeout_seconds", 0) or timeouts["overall"] > record.get("state_machine_timeout_seconds", 0):
        raise Refusal("launch timeout deployment mismatch")
    if record.get("heartbeat_interval_seconds", 0) > timeouts["heartbeat_stale"]:
        raise Refusal("heartbeat stale budget unreachable")
    if not _utc(record["observed_utc"]) < _utc(record["attempt_deadline_utc"]) < _utc(record["cleanup_deadline_utc"]):
        raise Refusal("launch deadlines invalid")
    envelope = record.get("cost_envelope", {})
    if envelope.get("cost_model_identity") != record["cost_model_identity"] or envelope.get("cost_model_object") != record.get("cost_model_object"):
        raise Refusal("launch cost model mismatch")
    if envelope.get("iam_pagination_bounds") != record.get("iam_pagination_bounds"):
        raise Refusal("launch IAM bounds mismatch")
    if set(envelope.get("resource_limits", {})) != set(DIMENSIONS):
        raise Refusal("launch 22 resource dimensions absent")
    return record


def _validate_cost_model(model: Any, model_id: str, launch: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(model, dict) or model.get("schema") != "aws_c0_cost_model/v2" or "record_sha256" in model:
        raise Refusal("cost-model-v2 boundary invalid")
    _common(model, "aws_c0_cost_model/v2", root=False)
    if model.get("currency") != "USD" or model.get("rounding_rule") != "CEIL_EACH_DIMENSION_THEN_SUM_FIXED" or model.get("list_price_bound_not_invoice") is not True:
        raise Refusal("cost model fixed fields invalid")
    if [row.get("dimension") for row in model.get("rates", [])] != list(DIMENSIONS):
        raise Refusal("cost model 22 dimensions/order invalid")
    window = launch["cost_envelope"]["accounting_window"]
    if _utc(model["valid_from_utc"]) > _utc(window["start_inclusive_utc"]) or _utc(model["valid_until_utc"]) < _utc(window["end_exclusive_utc"]):
        raise Refusal("cost model validity does not cover accounting horizon")
    if launch["cost_model_identity"] != identity("aws_c0_cost_model/v2", model_id):
        raise Refusal("cost model identity mismatch")
    for row in model["rates"]:
        if row.get("unit") != UNITS[row["dimension"]] or len(row.get("pricing_observations", [])) < 1:
            raise Refusal("cost rate unit/provenance missing")
        proof = base64.b64decode(row["selected_rate_upper_bound_proof_canonical_json_base64"], validate=True)
        strict_json(proof)
        if row.get("selected_rate_upper_bound_proof_identity") != identity("aws_c0_rate_upper_bound_proof/v1", digest(proof)):
            raise Refusal("rate upper-bound proof mismatch")
        observations = row["pricing_observations"]
        identities = row["pricing_observation_identities"]
        if len(observations) != len(identities):
            raise Refusal("pricing observation identity arithmetic")
        for observation, observed_identity in zip(observations, identities):
            if set(observation) == set() or observation.get("schema") != "aws_c0_pricing_observation/v1":
                raise Refusal("pricing observation invalid")
            request = base64.b64decode(observation["request_canonical_json_base64"], validate=True)
            response = base64.b64decode(observation["response_canonical_json_base64"], validate=True)
            strict_json(request); strict_json(response)
            if digest(request) != observation["request_sha256"] or digest(response) != observation["response_sha256"]:
                raise Refusal("pricing request/response digest mismatch")
            preimage = dict(observation); embedded = preimage.pop("identity")
            observation_id = digest(canonical_bytes(preimage))
            if embedded != identity("aws_c0_pricing_observation/v1", observation_id) or observed_identity != embedded:
                raise Refusal("pricing observation identity mismatch")
            if observation["selected_rate_upper_bound_proof_identity"] != row["selected_rate_upper_bound_proof_identity"]:
                raise Refusal("pricing proof binding mismatch")
    return model


def _exact_environment_record(prefix: str, schema: str, *, root: bool) -> tuple[dict[str, Any], dict[str, Any], str]:
    receipt = {
        "bucket_identity": _bucket_identity(),
        "key": _env(f"AWS_C0_{prefix}_KEY"),
        "version_id": _env(f"AWS_C0_{prefix}_VERSION_ID", VERSION),
        "bytes": int(_env(f"AWS_C0_{prefix}_BYTES")),
        "sha256": _env(f"AWS_C0_{prefix}_SHA256", SHA),
        "checksum_sha256_base64": base64.b64encode(bytes.fromhex(_env(f"AWS_C0_{prefix}_SHA256", SHA))).decode(),
    }
    record, _, record_id = _fetch_receipt(receipt, schema, root=root)
    return record, receipt, record_id


def _workflow_identity(arn: str) -> dict[str, str]:
    if not EXECUTION.fullmatch(arn):
        raise Refusal("workflow ARN invalid")
    return identity("aws_step_functions_standard_execution/v1",
                    digest(canonical_bytes({"schema": "aws_c0_workflow_execution/v1", "execution_arn": arn})))


def _instance_state() -> str:
    root = _query("ec2", "DescribeInstances", {"InstanceId.1": INSTANCE_ID})
    state = _xml_text(root, "name")
    if state not in {"pending", "running", "stopping", "stopped"}:
        raise Refusal("instance state unavailable")
    return state


def _runtime_preflight(packet: dict[str, Any], launch: dict[str, Any],
                       execution_arn: str) -> None:
    preimages = packet.get("runtime_control_preimages")
    kinds = ["ACCOUNT_REGION", "INSTANCE_PROFILE_SOLE_ROLE", "IAM_POLICY_SET", "BUCKET_CONTROLS_KMS",
             "VPC_NETWORK_PATH", "SERVICE_QUOTA", "STANDARD_WORKFLOW", "SSM_DOCUMENT",
             "SOFTWARE_AND_IMAGE_SET", "CHANGE_SET_AND_EFFECTS", "ARTIFACT_VERSION_SET"]
    if not isinstance(preimages, list) or [item.get("control_kind") for item in preimages] != kinds:
        raise Refusal("fresh eleven runtime control preimages absent")
    for item in preimages:
        if set(item) != {"control_kind", "identity", "canonical_json_base64", "observed_utc", "authenticated_source_identity"}:
            raise Refusal("runtime preimage not closed")
        raw = base64.b64decode(item["canonical_json_base64"], validate=True)
        strict_json(raw)
        if item["identity"]["sha256"] != digest(raw):
            raise Refusal("runtime preimage identity mismatch")
        if _utc(item["observed_utc"]) > _utc(packet["observed_utc"]):
            raise Refusal("runtime preimage occurs after packet")
    sts = _query("sts", "GetCallerIdentity", {})
    if _xml_text(sts, "Account") != _env("AWS_C0_EXPECTED_ACCOUNT_ID", re.compile(r"[0-9]{12}")):
        raise Refusal("current account mismatch")
    if _instance_state() != "stopped":
        raise Refusal("instance must still be stopped")
    # The authenticated preimages bind the complete 63-row API/resource read set;
    # these direct reads make the target, workflow and document freshness current.
    state_machine = _env("AWS_C0_STATE_MACHINE_ARN")
    described = _json_api("states", "AWSStepFunctions.DescribeStateMachine", {"stateMachineArn": state_machine})
    if described.get("type") != "STANDARD":
        raise Refusal("workflow is not STANDARD")
    document = _json_api("ssm", "AmazonSSM.GetDocument", {
        "Name": _env("AWS_C0_SSM_DOCUMENT_NAME"), "DocumentVersion": _env("AWS_C0_SSM_DOCUMENT_VERSION"),
        "DocumentFormat": "JSON",
    })
    content = document.get("Content", "")
    if digest(content.encode()) != _env("AWS_C0_SSM_DOCUMENT_SHA256", SHA):
        raise Refusal("SSM document content mismatch")
    if packet.get("iam_pagination_bounds") != launch.get("iam_pagination_bounds"):
        raise Refusal("IAM pagination bounds drift")
    if not execution_arn.endswith(":" + launch["attempt_id"]):
        raise Refusal("execution name is not exact attempt")


def _bound_base64(record: dict[str, Any], identity_field: str, bytes_field: str,
                  kind: str) -> bytes:
    try: raw = base64.b64decode(record[bytes_field], validate=True)
    except (KeyError, ValueError) as exc: raise Refusal(f"invalid canonical binding:{bytes_field}") from exc
    strict_json(raw)
    if record[identity_field] != identity(kind, digest(raw)):
        raise Refusal(f"canonical binding identity mismatch:{identity_field}")
    return raw


def _validate_live_packet_v2(packet: dict[str, Any]) -> None:
    if set(packet) != LIVE_PACKET_V2_FIELDS or packet.get("schema") != "aws_c0_live_packet/v4":
        raise Refusal("live-packet-v2 field closure failed")
    _common(packet, "aws_c0_live_packet/v4", root=False)
    if packet["packet_disposition"] != "AWS_C0_LIVE_PACKET_COMPLETE_UNAUTHORIZED" or packet["final_instance_state"] != "stopped" or packet["pre_live_object_count"] != 21:
        raise Refusal("live packet disposition/count/state mismatch")
    if len(packet["pre_live_predecessor_object_receipts"]) != 20:
        raise Refusal("live packet predecessor receipt count mismatch")
    for identity_field, bytes_field, kind in (
        ("execution_session_policy_identity", "execution_session_policy_canonical_json_base64", "aws_iam_session_policy/v1"),
        ("execution_session_policy_ceiling_identity", "execution_session_policy_ceiling_canonical_json_base64", "aws_iam_policy_ceiling/v1"),
        ("execution_session_policy_subset_proof_identity", "execution_session_policy_subset_proof_canonical_json_base64", "aws_iam_policy_subset_proof/v1"),
        ("pass_role_scope_proof_identity", "pass_role_scope_proof_canonical_json_base64", "aws_iam_passrole_scope_proof/v1"),
    ): _bound_base64(packet, identity_field, bytes_field, kind)
    if _utc(packet["live_session_assumer_expires_utc"]) <= _utc(packet["observed_utc"]):
        raise Refusal("packet assumer already expired")


def _live_statement(auth: dict[str, Any]) -> str:
    return (
        "AUTHORIZE_AWS_C0_LIVE_V2 "
        f"live_packet_sha256={auth['live_packet_identity']['sha256']} live_packet_key={auth['live_packet_object']['key']} "
        f"live_packet_version_id={auth['live_packet_object']['version_id']} change_set_identity_sha256={auth['change_set_identity']['sha256']} "
        f"account_identity_sha256={auth['account_identity']['sha256']} region=us-east-1 instance_id=i-048bac00bdb540a4e "
        f"attempt_identity_sha256={auth['attempt_identity']['sha256']} live_session_assumer_identity_sha256={auth['live_session_assumer_identity']['sha256']} "
        f"execution_operator_role_identity_sha256={auth['execution_operator_role_identity']['sha256']} "
        f"execution_session_policy_identity_sha256={auth['execution_session_policy_identity']['sha256']} "
        f"execution_session_policy_ceiling_identity_sha256={auth['execution_session_policy_ceiling_identity']['sha256']} "
        f"execution_session_policy_subset_proof_identity_sha256={auth['execution_session_policy_subset_proof_identity']['sha256']} "
        f"pass_role_scope_proof_identity_sha256={auth['pass_role_scope_proof_identity']['sha256']} "
        f"execution_session_max_duration_seconds={auth['execution_session_max_duration_seconds']} "
        f"live_session_assumer_expires_utc={auth['execution_session_expires_utc']} "
        "allow=ASSUME_EXACT_LIVE_SESSION,PUBLISH_EXACT_LIVE_AUTHORIZATION,EXECUTE_EXACT_CHANGE_SET,START_ONE_EXACT_EXECUTION "
        "deny=REPLAY,OTHER_CHANGE_SET,OTHER_ATTEMPT,SCIENTIFIC_EXECUTION"
    )


def _validate_live_authorization_v2(auth: dict[str, Any]) -> None:
    if set(auth) != LIVE_AUTH_V2_FIELDS or auth.get("schema") != "aws_c0_live_authorization/v4":
        raise Refusal("live-authorization-v2 field closure failed")
    _common(auth, "aws_c0_live_authorization/v4", root=False)
    for identity_field, bytes_field, kind in (
        ("execution_session_policy_identity", "execution_session_policy_canonical_json_base64", "aws_iam_session_policy/v1"),
        ("execution_session_policy_ceiling_identity", "execution_session_policy_ceiling_canonical_json_base64", "aws_iam_policy_ceiling/v1"),
        ("execution_session_policy_subset_proof_identity", "execution_session_policy_subset_proof_canonical_json_base64", "aws_iam_policy_subset_proof/v1"),
        ("pass_role_scope_proof_identity", "pass_role_scope_proof_canonical_json_base64", "aws_iam_passrole_scope_proof/v1"),
        ("execution_session_derivation_proof_identity", "execution_session_derivation_proof_canonical_json_base64", "aws_sts_session_derivation_proof/v1"),
    ): _bound_base64(auth, identity_field, bytes_field, kind)
    _identity(auth, "execution_session_identity", "aws_sts_role_session/v1")
    if auth["statement_sha256"] != digest(_live_statement(auth).encode()):
        raise Refusal("live authorization statement digest mismatch")
    if not _utc(auth["observed_utc"]) < _utc(auth["execution_session_expires_utc"]):
        raise Refusal("live session expiry ordering invalid")


def preflight(event: dict[str, Any]) -> dict[str, Any]:
    if set(event) != {"action", "live_authorization", "workflow_execution_arn"} or event["action"] != "preflight":
        raise Refusal("preflight event not closed")
    execution_arn = event["workflow_execution_arn"]
    auth, _, auth_id = _fetch_receipt(event["live_authorization"], "aws_c0_live_authorization/v2", root=False)
    _validate_live_authorization_v2(auth)
    if auth["live_authorization_key"] != event["live_authorization"]["key"]:
        raise Refusal("live authorization key mismatch")
    if auth.get("authorized_actions") != ["ASSUME_EXACT_LIVE_SESSION", "PUBLISH_EXACT_LIVE_AUTHORIZATION",
                                          "EXECUTE_EXACT_CHANGE_SET", "START_ONE_EXACT_EXECUTION"]:
        raise Refusal("live action set mismatch")
    if auth.get("denied_actions") != ["REPLAY", "OTHER_CHANGE_SET", "OTHER_ATTEMPT", "SCIENTIFIC_EXECUTION"]:
        raise Refusal("live denial set mismatch")
    if _utc(auth["execution_session_expires_utc"]) <= dt.datetime.now(dt.timezone.utc):
        raise Refusal("live session expired")
    packet, _, packet_id = _fetch_receipt(auth["live_packet_object"], "aws_c0_live_packet/v2", root=False)
    _validate_live_packet_v2(packet)
    if auth.get("live_packet_identity") != identity("aws_c0_live_packet/v2", packet_id):
        raise Refusal("live authorization packet identity mismatch")
    for field in ("change_set_identity", "live_session_assumer_identity", "execution_operator_role_identity",
                  "execution_session_policy_identity", "execution_session_policy_ceiling_identity",
                  "execution_session_policy_subset_proof_identity", "pass_role_scope_proof_identity"):
        if auth.get(field) != packet.get(field): raise Refusal(f"live authorization packet mismatch:{field}")
    if auth["execution_session_max_duration_seconds"] != packet["execution_session_max_duration_seconds"]:
        raise Refusal("live session duration mismatch")
    if _utc(auth["execution_session_expires_utc"]) > _utc(packet["live_session_assumer_expires_utc"]):
        raise Refusal("derived live session exceeds assumer expiry")
    launch, launch_receipt, launch_id = _fetch_receipt(packet["launch_request_object"], "aws_c0_launch_request/v3", root=True)
    _validate_launch_v3(launch)
    if packet.get("launch_request_identity") != identity("aws_c0_launch_request/v3", launch_id):
        raise Refusal("packet launch identity mismatch")
    seed, seed_receipt, seed_id = _exact_environment_record("CLOSURE_SEED", "aws_c0_closure_seed/v1", root=False)
    if launch.get("closure_seed_identity") != identity("aws_c0_closure_seed/v1", seed_id) or launch.get("closure_seed_object") != seed_receipt:
        raise Refusal("launch seed binding mismatch")
    model, model_receipt, model_id = _exact_environment_record("COST_MODEL", "aws_c0_cost_model/v2", root=False)
    if launch.get("cost_model_identity") != identity("aws_c0_cost_model/v2", model_id) or launch.get("cost_model_object") != model_receipt:
        raise Refusal("launch cost-model binding mismatch")
    _validate_cost_model(model, model_id, launch)
    if len(packet.get("pre_live_predecessor_object_receipts", [])) != 20 or packet.get("pre_live_object_count") != 21:
        raise Refusal("prelive 21-object arithmetic mismatch")
    _runtime_preflight(packet, launch, execution_arn)
    return {
        "preflight_disposition": "AWS_C0_PREFLIGHT_PASS", "launch": launch,
        "launch_request_identity": identity("aws_c0_launch_request/v3", launch_id),
        "launch_request_object": launch_receipt,
        "live_packet_identity": identity("aws_c0_live_packet/v2", packet_id),
        "live_packet_object": auth["live_packet_object"],
        "live_authorization_identity": identity("aws_c0_live_authorization/v2", auth_id),
        "live_authorization_object": event["live_authorization"],
        "closure_seed_identity": identity("aws_c0_closure_seed/v1", seed_id),
        "closure_seed_object": seed_receipt,
        "cost_model_identity": identity("aws_c0_cost_model/v2", model_id),
        "cost_model_object": model_receipt,
        "attempt_identity": launch["attempt_identity"], "artifact_prefix": launch["artifact_prefix"],
        "workflow_execution_identity": _workflow_identity(execution_arn),
        "workflow_execution_arn": execution_arn,
        "attempt_deadline_utc": launch["attempt_deadline_utc"], "cleanup_deadline_utc": launch["cleanup_deadline_utc"],
        "phase_timeouts_seconds": launch["phase_timeouts_seconds"],
        "heartbeat_interval_seconds": launch["heartbeat_interval_seconds"],
        "checkpoint_interval_seconds": launch["checkpoint_interval_seconds"],
    }


def _read_root_coordinate(bucket: str, coordinate: dict[str, str], schema: str) -> tuple[dict[str, Any], dict[str, Any], str]:
    raw = _s3_get(bucket, coordinate["key"], coordinate["version_id"], coordinate["sha256"])
    record = strict_json(raw)
    record_id = _root_digest(record)
    if record.get("schema") != schema:
        raise Refusal("root schema mismatch")
    return record, _full_receipt({**coordinate, "bytes": len(raw),
                                  "checksum_sha256_base64": base64.b64encode(hashlib.sha256(raw).digest()).decode()}), record_id


def _find_roots(bucket: str, prefix: str, max_pages: int, max_items: int) -> tuple[list[tuple[dict[str, Any], dict[str, Any], str]], dict[str, Any], list[dict[str, str]]]:
    entries, transcript = _s3_version_entries(bucket, prefix, max_pages, max_items)
    roots: list[tuple[dict[str, Any], dict[str, Any], str]] = []
    for coordinate in entries:
        # Exact key/version is authoritative; checksum-enabled GET supplies the
        # complete bytes, and no mutable latest selection is used.
        got, headers = _aws_request("s3", "GET", f"{bucket}.s3.{REGION}.amazonaws.com",
                                    "/" + coordinate["key"], [("versionId", coordinate["version_id"])], b"",
                                    {"x-amz-checksum-mode": "ENABLED"})
        checksum = headers.get("x-amz-checksum-sha256", "")
        if headers.get("x-amz-version-id") != coordinate["version_id"] or checksum != base64.b64encode(hashlib.sha256(got).digest()).decode():
            raise Refusal("listed exact-version read mismatch")
        try:
            record = strict_json(got)
        except Refusal:
            continue
        schema = record.get("schema")
        if schema in ROOT_KINDS or schema == "aws_c0_safe_close_receipt/v1":
            record_id = _root_digest(record) if schema in ROOT_KINDS else digest(got)
            receipt = _full_receipt({"key": coordinate["key"], "version_id": coordinate["version_id"],
                                     "bytes": len(got), "sha256": digest(got), "checksum_sha256_base64": checksum})
            roots.append((record, receipt, record_id))
    return roots, transcript, entries


def poll(event: dict[str, Any]) -> dict[str, Any]:
    required = {"action", "artifact_prefix", "attempt_identity", "heartbeat_stale_seconds", "workflow_execution_arn"}
    if set(event) != required or event["action"] != "poll":
        raise Refusal("poll event not closed")
    _identity(event, "attempt_identity", "aws_c0_attempt/v1")
    bucket = _env("AWS_C0_ARTIFACT_BUCKET", BUCKET)
    max_pages = int(_env("AWS_C0_S3_VERSION_MAX_PAGES")); max_items = int(_env("AWS_C0_S3_VERSION_MAX_ITEMS"))
    roots, _, _ = _find_roots(bucket, event["artifact_prefix"], max_pages, max_items)
    terminal = [(r, i) for r, _, i in roots if r["schema"] == "aws_c0_terminal_receipt/v1"]
    if len(terminal) > 1:
        raise Refusal("multiple terminal roots")
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    if terminal:
        return {"state": "TERMINAL", "terminal_receipt_identity": identity("aws_c0_terminal_receipt/v1", terminal[0][1]), "observed_utc": now}
    heartbeats = [r for r, _, _ in roots if r["schema"] == "aws_c0_heartbeat/v1"]
    if not heartbeats:
        return {"state": "WAITING_FIRST_HEARTBEAT", "observed_utc": now, "terminal_receipt_identity": None}
    newest = max(heartbeats, key=lambda r: r["sequence"])
    age = (dt.datetime.now(dt.timezone.utc) - _utc(newest["observed_utc"])).total_seconds()
    starts = [(r, i) for r, _, i in roots if r["schema"] == "aws_c0_start_receipt/v3"]
    heartbeat_zero = [(r, i) for r, _, i in roots if r["schema"] == "aws_c0_heartbeat/v1" and r.get("sequence") == 0]
    if len(starts) != 1 or len(heartbeat_zero) != 1:
        raise Refusal("start/heartbeat-zero identity ambiguity")
    return {"state": "HEARTBEAT_FRESH" if age <= event["heartbeat_stale_seconds"] else "HEARTBEAT_STALE",
            "last_heartbeat_sequence": newest["sequence"], "observed_utc": now,
            "terminal_receipt_identity": None,
            "start_receipt_identity": identity("aws_c0_start_receipt/v3", starts[0][1]),
            "heartbeat_zero_identity": identity("aws_c0_heartbeat/v1", heartbeat_zero[0][1])}


def safe_close(event: dict[str, Any]) -> dict[str, Any]:
    required = {"action", "artifact_prefix", "attempt_identity", "workflow_execution_arn",
                "start_receipt_identity", "heartbeat_zero_identity"}
    if set(event) != required or event["action"] != "safe_close":
        raise Refusal("safe-close event not closed")
    bucket = _env("AWS_C0_ARTIFACT_BUCKET", BUCKET)
    roots, _, _ = _find_roots(bucket, event["artifact_prefix"], int(_env("AWS_C0_S3_VERSION_MAX_PAGES")),
                              int(_env("AWS_C0_S3_VERSION_MAX_ITEMS")))
    by_id = {root_id: (record, receipt) for record, receipt, root_id in roots}
    start_id = _identity(event, "start_receipt_identity", "aws_c0_start_receipt/v3")
    heartbeat_id = _identity(event, "heartbeat_zero_identity", "aws_c0_heartbeat/v1")
    if start_id not in by_id or heartbeat_id not in by_id or by_id[heartbeat_id][0].get("sequence") != 0:
        raise Refusal("safe-close start/heartbeat-zero missing")
    execution = _json_api("states", "AWSStepFunctions.DescribeExecution", {"executionArn": event["workflow_execution_arn"]})
    if execution.get("status") != "RUNNING":
        raise Refusal("safe-close execution is not RUNNING")
    seed, seed_receipt, seed_id = _exact_environment_record("CLOSURE_SEED", "aws_c0_closure_seed/v1", root=False)
    record = _control_record("aws_c0_safe_close_receipt/v1", {
        "attempt_identity": event["attempt_identity"], "workflow_execution_identity": _workflow_identity(event["workflow_execution_arn"]),
        "workflow_execution_arn": event["workflow_execution_arn"], "workflow_execution_status": "RUNNING",
        "start_receipt_identity": event["start_receipt_identity"], "start_object": by_id[start_id][1],
        "heartbeat_zero_identity": event["heartbeat_zero_identity"], "heartbeat_zero_object": by_id[heartbeat_id][1],
        "safe_close_disposition": "AWS_C0_SAFE_CLOSE_READY",
    })
    safe_id, safe_receipt = _put_record(bucket, event["artifact_prefix"], "control/safe-close", record, root=False)
    return {"safe_close_receipt_identity": safe_id, "safe_close_object": safe_receipt,
            "closure_seed_identity": identity("aws_c0_closure_seed/v1", seed_id), "closure_seed_object": seed_receipt}


def _resource_use(launch: dict[str, Any], seed_id: str, seed_receipt: dict[str, Any],
                  launch_id: str) -> dict[str, Any]:
    limits = launch["cost_envelope"]["resource_limits"]
    rows = [{"dimension": name, "unit": UNITS[name], "observation_disposition": "SEALED_MAXIMUM_SUBSTITUTION",
             "observed_units": None, "charged_units": limits[name], "limit_units": limits[name],
             "usage_observation_identity": None, "usage_observation": None, "usage_observation_object": None,
             "maximum_substitution_source_identity": identity("aws_c0_launch_request/v3", launch_id)}
            for name in DIMENSIONS]
    return _control_record("aws_c0_resource_use_closure/v1", {
        "attempt_identity": launch["attempt_identity"], "closure_seed_identity": identity("aws_c0_closure_seed/v1", seed_id),
        "closure_seed_object": seed_receipt, "launch_request_identity": identity("aws_c0_launch_request/v3", launch_id),
        "cost_model_identity": launch["cost_model_identity"], "accounting_window": launch["cost_envelope"]["accounting_window"],
        "dimensions": rows, "all_limits_respected": True, "resource_use_disposition": "AWS_C0_RESOURCE_USE_CLOSED",
        "failure_phase": None, "failure_code": None,
    })


def compute_cost(model: dict[str, Any], resource_use: dict[str, Any]) -> tuple[list[int], int]:
    if [r.get("dimension") for r in model.get("rates", [])] != list(DIMENSIONS):
        raise Refusal("cost rate dimensions/order invalid")
    if [r.get("dimension") for r in resource_use.get("dimensions", [])] != list(DIMENSIONS):
        raise Refusal("resource-use dimensions/order invalid")
    if model.get("integer_maximum") != 9007199254740991:
        raise Refusal("cost integer maximum invalid")
    charges: list[int] = []
    for rate, use in zip(model["rates"], resource_use["dimensions"]):
        if rate["unit"] != use["unit"] or rate["unit"] != UNITS[rate["dimension"]]:
            raise Refusal("cost unit mismatch")
        charged, limit = use["charged_units"], use["limit_units"]
        if type(charged) is not int or not 0 <= charged <= limit:
            raise Refusal("cost charged units exceed limit")
        product = charged * rate["numerator_minor_units"]
        if product > model["product_maximum"] or product > model["integer_maximum"]:
            raise Refusal("cost product overflow")
        charges.append((product + rate["denominator_units"] - 1) // rate["denominator_units"])
    total = model["fixed_minor_units"] + sum(charges)
    if total > model["total_maximum"] or total > model["integer_maximum"]:
        raise Refusal("cost total overflow")
    return charges, total


def _semantic_roots(launch: dict[str, Any], launch_receipt: dict[str, Any], launch_id: str,
                    dynamic: list[tuple[dict[str, Any], dict[str, Any], str]]) -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
    roots: list[tuple[dict[str, str], dict[str, Any]]] = []
    for identity_field, object_field, schema in (
        ("authority_audit_identity", "authority_audit_object", "aws_c0_cost_runtime_closure_authority_audit/v1"),
        ("static_validation_identity", "static_validation_object", "aws_c0_cost_runtime_closure_static_validation/v1"),
        ("private_infrastructure_snapshot_identity", "private_infrastructure_snapshot_object", "aws_c0_private_infrastructure_snapshot/v1"),
    ):
        _, _, record_id = _fetch_receipt(launch[object_field], schema, root=True)
        expected = identity(schema, record_id)
        if launch[identity_field] != expected:
            raise Refusal(f"launch predecessor identity mismatch:{schema}")
        roots.append((expected, launch[object_field]))
    roots.append((identity("aws_c0_launch_request/v3", launch_id), launch_receipt))
    for schema in ("aws_c0_start_receipt/v3", "aws_c0_heartbeat/v1", "aws_c0_checkpoint/v1", "aws_c0_terminal_receipt/v1"):
        rows = [(record, receipt, item_id) for record, receipt, item_id in dynamic if record["schema"] == schema]
        if not rows or (schema in {"aws_c0_start_receipt/v3", "aws_c0_terminal_receipt/v1"} and len(rows) != 1):
            raise Refusal(f"missing/ambiguous predecessor root:{schema}")
        if schema in {"aws_c0_heartbeat/v1", "aws_c0_checkpoint/v1"}:
            rows.sort(key=lambda row: row[0].get("sequence", -1))
            previous_field = "previous_heartbeat_identity" if schema == "aws_c0_heartbeat/v1" else "previous_checkpoint_identity"
            previous: dict[str, str] | None = None
            for expected_sequence, (record, _, item_id) in enumerate(rows):
                if record.get("sequence") != expected_sequence or record.get(previous_field) != previous:
                    raise Refusal(f"noncontiguous predecessor chain:{schema}")
                previous = identity(schema, item_id)
        roots.extend((identity(schema, item_id), receipt) for _, receipt, item_id in rows)
    return [pair[0] for pair in roots], [pair[1] for pair in roots]


def _verify_prelive_objects(packet_receipt: dict[str, Any], auth_receipt: dict[str, Any],
                            launch: dict[str, Any]) -> list[dict[str, Any]]:
    """Exact-version-read the closed 21-object pre-live set and later live auth."""
    packet, _, packet_id = _fetch_receipt(packet_receipt, "aws_c0_live_packet/v2", root=False)
    auth, _, auth_id = _fetch_receipt(auth_receipt, "aws_c0_live_authorization/v2", root=False)
    _validate_live_packet_v2(packet); _validate_live_authorization_v2(auth)
    if auth["live_packet_identity"] != identity("aws_c0_live_packet/v2", packet_id):
        raise Refusal("retrieval live-packet authorization binding mismatch")
    predecessors = packet["pre_live_predecessor_object_receipts"]
    if len(predecessors) != 20 or len({canonical_bytes(item) for item in predecessors}) != 20:
        raise Refusal("retrieval pre-live predecessor set is not exact 20")
    artifact_coordinates = {canonical_bytes(item) for item in launch["artifact_version_receipts"]}
    if not artifact_coordinates.issubset({canonical_bytes(item) for item in predecessors}):
        raise Refusal("retrieval pre-live set omits an implementation artifact")
    verified: list[dict[str, Any]] = []
    allowed = {
        "aws_c0_operator_bootstrap_packet/v1", "aws_c0_operator_bootstrap_authorization/v1",
        "aws_c0_operator_bootstrap_closure/v1", "aws_c0_preparation_packet/v2",
        "aws_c0_preparation_authorization/v2", "aws_c0_private_infrastructure_snapshot/v1",
        "aws_c0_cost_runtime_closure_authority_audit/v1",
        "aws_c0_cost_runtime_closure_static_validation/v1", "aws_c0_cost_model/v2",
        "aws_c0_closure_seed/v1", "aws_c0_launch_request/v3", "aws_c0_preparation_closure/v2",
    }
    for receipt_value in predecessors:
        receipt = _receipt(receipt_value)
        raw = _s3_get(_bucket_from_receipt(receipt), receipt["key"], receipt["version_id"],
                      receipt["sha256"], receipt["bytes"])
        try: record = strict_json(raw)
        except Refusal: continue  # immutable implementation artifact bytes
        schema = record.get("schema") if isinstance(record, dict) else None
        if schema not in allowed: continue
        item_id = _root_digest(record) if schema in ROOT_KINDS else _nonroot_digest(record, raw, schema)
        verified.append({"record_or_object_identity": identity(schema, item_id), "object": receipt,
                         "verification_disposition": "EXACT_VERSION_COMPLETE_BYTES_PASS"})
    verified.extend([
        {"record_or_object_identity": identity("aws_c0_live_packet/v2", packet_id), "object": packet_receipt,
         "verification_disposition": "EXACT_VERSION_COMPLETE_BYTES_PASS"},
        {"record_or_object_identity": identity("aws_c0_live_authorization/v2", auth_id), "object": auth_receipt,
         "verification_disposition": "EXACT_VERSION_COMPLETE_BYTES_PASS"},
    ])
    return verified


def _listed_payload(bucket: str, entries: list[dict[str, str]], key: str,
                    expected_sha256: str) -> tuple[dict[str, Any], bytes]:
    """Read exactly one listed content-addressed payload version and its checksum."""
    matches = [item for item in entries if item["key"] == key]
    if len(matches) != 1:
        raise Refusal("synthetic manifest does not have one listed exact version")
    coordinate = matches[0]
    raw, headers = _aws_request("s3", "GET", f"{bucket}.s3.{REGION}.amazonaws.com",
                                "/" + key, [("versionId", coordinate["version_id"])], b"",
                                {"x-amz-checksum-mode": "ENABLED"})
    checksum = base64.b64encode(hashlib.sha256(raw).digest()).decode()
    if (headers.get("x-amz-version-id") != coordinate["version_id"] or
            headers.get("x-amz-checksum-sha256") != checksum or digest(raw) != expected_sha256):
        raise Refusal("synthetic manifest exact-version verification failed")
    receipt = _full_receipt({"key": key, "version_id": coordinate["version_id"],
                             "bytes": len(raw), "sha256": expected_sha256,
                             "checksum_sha256_base64": checksum})
    return receipt, raw


def closure(event: dict[str, Any]) -> dict[str, Any]:
    global _ACTIVE_JOURNAL
    required = {"action", "workflow_execution_arn", "attempt_identity", "artifact_prefix",
                "live_packet_object", "live_authorization_object",
                "finalizer_execution_disposition", "finalizer_failure_code", "cleanup_disposition",
                "observed_instance_state", "stop_failure_code", "supervisor_failure_phase",
                "supervisor_failure_code", "terminal_receipt_identity"}
    if set(event) != required or event["action"] != "closure":
        raise Refusal("closure event not closed")
    if _ACTIVE_JOURNAL is not None:
        raise Refusal("nested closure journal")
    _ACTIVE_JOURNAL = CaptureJournal()
    bucket = _env("AWS_C0_ARTIFACT_BUCKET", BUCKET); prefix = event["artifact_prefix"]
    seed, seed_receipt, seed_id = _exact_environment_record("CLOSURE_SEED", "aws_c0_closure_seed/v1", root=False)
    model, model_receipt, model_id = _exact_environment_record("COST_MODEL", "aws_c0_cost_model/v2", root=False)
    launch, launch_receipt, launch_id = _exact_environment_record("LAUNCH", "aws_c0_launch_request/v3", root=True)
    _validate_launch_v3(launch)
    _validate_cost_model(model, model_id, launch)
    prelive_verified = _verify_prelive_objects(event["live_packet_object"], event["live_authorization_object"], launch)
    if event["attempt_identity"] != launch["attempt_identity"]:
        raise Refusal("closure attempt mismatch")
    controller_handoff, carrier_observation = _discover_controller_journal_handoff(
        bucket, prefix, launch["attempt_identity"])
    state = _instance_state()
    if state != "stopped" or event["observed_instance_state"] != "stopped":
        raise Refusal("closure requires stopped instance")
    max_pages = int(_env("AWS_C0_S3_VERSION_MAX_PAGES"))
    max_items = int(_env("AWS_C0_S3_VERSION_MAX_ITEMS"))
    dynamic, _, _ = _find_roots(bucket, prefix, max_pages, max_items)
    resource_use = _resource_use(launch, seed_id, seed_receipt, launch_id)
    use_id, use_receipt = _put_record(bucket, prefix, "control/resource-use", resource_use, root=False)
    terminal = [record for record, _, _ in dynamic if record["schema"] == "aws_c0_terminal_receipt/v1"]
    if len(terminal) != 1:
        raise Refusal("terminal root missing or ambiguous")
    heartbeat_count = sum(1 for record, _, _ in dynamic if record["schema"] == "aws_c0_heartbeat/v1")
    checkpoint_count = sum(1 for record, _, _ in dynamic if record["schema"] == "aws_c0_checkpoint/v1")
    if (terminal[0].get("last_heartbeat_sequence") != heartbeat_count - 1 or
            terminal[0].get("last_checkpoint_sequence") != checkpoint_count - 1):
        raise Refusal("terminal sequence closure mismatch")
    terminal_identity = identity("aws_c0_terminal_receipt/v1", _root_digest(terminal[0]))
    finalizer_pass = event["cleanup_disposition"] == "STOPPED_VERIFIED" and event["finalizer_execution_disposition"] == "PASS"
    finalizer_record = _root_record("aws_c0_finalizer_receipt/v2", {
        "attempt_identity": launch["attempt_identity"], "closure_seed_identity": identity("aws_c0_closure_seed/v1", seed_id),
        "closure_seed_object": seed_receipt, "terminal_receipt_identity": terminal_identity,
        "resource_use_closure_identity": use_id, "resource_use_object": use_receipt,
        "cleanup_requested": True, "cleanup_disposition": "AWS_C0_STOPPED",
        "observed_instance_state": state, "stop_failure_code": event["stop_failure_code"],
        "finalizer_started_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "finalizer_completed_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "finalizer_disposition": "AWS_C0_FINALIZER_PASS" if finalizer_pass else "AWS_C0_FINALIZER_FAIL",
        "failure_phase": None if finalizer_pass else "FINALIZER",
        "failure_code": None if finalizer_pass else (event["finalizer_failure_code"] or "FINALIZER_FAILURE"),
    })
    finalizer_id, finalizer_receipt = _put_record(bucket, prefix, "evidence/finalizer", finalizer_record, root=True)
    charges, total = compute_cost(model, resource_use)
    within = total <= launch["cost_envelope"]["ceiling_minor_units"]
    cost_record = _root_record("aws_c0_cost_closure/v2", {
        "attempt_identity": launch["attempt_identity"], "closure_seed_identity": identity("aws_c0_closure_seed/v1", seed_id),
        "closure_seed_object": seed_receipt, "launch_request_identity": identity("aws_c0_launch_request/v3", launch_id),
        "finalizer_receipt_identity": finalizer_id, "cost_model_identity": identity("aws_c0_cost_model/v2", model_id),
        "cost_model_object": model_receipt, "resource_use_closure_identity": use_id, "resource_use_object": use_receipt,
        "currency": "USD", "accounting_window": launch["cost_envelope"]["accounting_window"],
        "ceiling_minor_units": launch["cost_envelope"]["ceiling_minor_units"], "fixed_minor_units": model["fixed_minor_units"],
        "dimension_charges_minor_units": charges, "recomputed_upper_bound_minor_units": total, "within_ceiling": within,
        "observed_instance_state": state, "evidence_completeness": "COMPLETE", "missing_root_categories": [],
        "list_price_bound_not_invoice": True,
        "cost_disposition": "AWS_C0_COST_PASS" if within else "AWS_C0_COST_OUTSIDE_CEILING",
        "failure_phase": None if within else "COST", "failure_code": None if within else "COST_CEILING_EXCEEDED",
    })
    cost_id, cost_receipt = _put_record(bucket, prefix, "evidence/cost", cost_record, root=True)
    # Retrieval occurs only after cost publication.  Re-list to terminal state,
    # exact-version-read every root again, and use this final token transcript.
    dynamic, s3_transcript, entries = _find_roots(bucket, prefix, max_pages, max_items)
    predecessor_ids, predecessor_receipts = _semantic_roots(launch, launch_receipt, launch_id, dynamic)
    refreshed = {record_id: (record, receipt) for record, receipt, record_id in dynamic}
    if finalizer_id["sha256"] not in refreshed or cost_id["sha256"] not in refreshed:
        raise Refusal("published finalizer/cost root absent from exact-version refresh")
    if refreshed[finalizer_id["sha256"]][1] != finalizer_receipt or refreshed[cost_id["sha256"]][1] != cost_receipt:
        raise Refusal("published finalizer/cost receipt readback mismatch")
    publication_ids = predecessor_ids + [finalizer_id, cost_id]
    publication_receipts = predecessor_receipts + [finalizer_receipt, cost_receipt]
    verified = [{"record_or_object_identity": item_id, "object": item_receipt,
                 "verification_disposition": "EXACT_VERSION_COMPLETE_BYTES_PASS"}
                for item_id, item_receipt in zip(publication_ids, publication_receipts)]
    for item in prelive_verified:
        if item not in verified: verified.append(item)
    safe_rows = [(record, receipt, item_id) for record, receipt, item_id in dynamic
                 if record["schema"] == "aws_c0_safe_close_receipt/v1"]
    if len(safe_rows) != 1:
        raise Refusal("safe-close receipt missing or ambiguous")
    safe_record, safe_receipt, safe_digest = safe_rows[0]
    verified.append({"record_or_object_identity": identity("aws_c0_safe_close_receipt/v1", safe_digest),
                     "object": safe_receipt,
                     "verification_disposition": "EXACT_VERSION_COMPLETE_BYTES_PASS"})
    _, _, verified_use_id = _fetch_receipt(use_receipt, "aws_c0_resource_use_closure/v1", root=False)
    if identity("aws_c0_resource_use_closure/v1", verified_use_id) != use_id:
        raise Refusal("resource-use readback identity mismatch")
    verified.append({"record_or_object_identity": use_id, "object": use_receipt,
                     "verification_disposition": "EXACT_VERSION_COMPLETE_BYTES_PASS"})
    manifest_identity = terminal[0].get("synthetic_manifest_identity")
    if manifest_identity is not None:
        manifest_sha = _identity(terminal[0], "synthetic_manifest_identity", "aws_c0_synthetic_manifest/v1")
        manifest_key = f"{prefix}payload/synthetic-manifest-{manifest_sha}.json"
        manifest_receipt, manifest_raw = _listed_payload(bucket, entries, manifest_key, manifest_sha)
        manifest_payload = strict_json(manifest_raw)
        expected_payload = {
            "attempt_id": launch["attempt_id"],
            "checkpoint_count": sum(1 for record, _, _ in dynamic if record["schema"] == "aws_c0_checkpoint/v1"),
            "heartbeat_count": sum(1 for record, _, _ in dynamic if record["schema"] == "aws_c0_heartbeat/v1"),
            "mode": "SUCCESS", "schema": "aws_c0_synthetic_manifest_payload/v1",
            "synthetic_progress_units": sum(1 for record, _, _ in dynamic if record["schema"] == "aws_c0_checkpoint/v1"),
        }
        if manifest_payload != expected_payload:
            raise Refusal("synthetic manifest payload mismatch")
        verified.append({"record_or_object_identity": manifest_identity, "object": manifest_receipt,
                         "verification_disposition": "EXACT_VERSION_COMPLETE_BYTES_PASS"})
    s3_transcript_id = s3_transcript["identity"]
    terminal_pass = terminal[0].get("disposition") == "AWS_C0_SYNTHETIC_PASS"
    retrieval_record = _root_record("aws_c0_retrieval_verification/v4", {
        "attempt_identity": launch["attempt_identity"], "closure_seed_identity": identity("aws_c0_closure_seed/v1", seed_id),
        "closure_seed_object": seed_receipt,
        "semantic_category_order": ["AUTHORITY_AUDIT", "STATIC_VALIDATION", "SNAPSHOT", "LAUNCH", "START",
                                    "HEARTBEAT", "CHECKPOINT", "TERMINAL", "FINALIZER", "RETRIEVAL", "COST"],
        "predecessor_root_identities": publication_ids, "publication_order": publication_ids,
        "verified_objects": verified, "verified_object_count": len(verified), "expected_object_count": FROZEN_PRELIVE_OBJECT_COUNT,
        "s3_pagination_transcript_identity": s3_transcript_id, "s3_pagination_transcript": s3_transcript,
        "history_pagination_transcript_identity": None, "history_pagination_transcript": None,
        "all_pages_consumed": True, "latest_reads_used": False, "all_hashes_match": True,
        "evidence_completeness": "COMPLETE", "missing_root_categories": [],
        "retrieval_disposition": "AWS_C0_RETRIEVAL_PASS",
        "failure_phase": None, "failure_code": None,
    })
    retrieval_id, retrieval_receipt = _put_record(bucket, prefix, "evidence/retrieval", retrieval_record, root=True)
    # Semantic order places retrieval before cost although immutable publication chronology places cost first.
    ordered = predecessor_ids + [finalizer_id, retrieval_id, cost_id]
    offsets = {"authority_audit": 0, "static_validation": 1, "snapshot": 2, "launch": 3, "start": 4}
    start_index = 5
    heartbeats = sum(1 for item in ordered if item["kind"] == "aws_c0_heartbeat/v1")
    checkpoints = sum(1 for item in ordered if item["kind"] == "aws_c0_checkpoint/v1")
    offsets.update({"heartbeats": start_index, "checkpoints": start_index + heartbeats,
                    "terminal": start_index + heartbeats + checkpoints,
                    "finalizer": start_index + heartbeats + checkpoints + 1,
                    "retrieval": start_index + heartbeats + checkpoints + 2,
                    "cost": start_index + heartbeats + checkpoints + 3})
    final_pass = terminal_pass and finalizer_pass and within
    final_status = "AWS_C0_FINAL_PASS" if final_pass else "AWS_C0_FINAL_FAIL"
    failure_codes = [] if final_pass else [code for code in (
        None if terminal_pass else terminal[0].get("failure_code", "TERMINAL_FAIL"),
        None if finalizer_pass else finalizer_record["failure_code"],
        None if within else "COST_CEILING_EXCEEDED") if code]
    safe_identity = identity("aws_c0_safe_close_receipt/v1", safe_digest)
    manifest_record = _root_record("aws_c0_final_manifest/v4", {
        "attempt_identity": launch["attempt_identity"], "closure_seed_identity": identity("aws_c0_closure_seed/v1", seed_id),
        "closure_seed_object": seed_receipt, "ordered_record_identities": ordered, "category_offsets": offsets,
        "record_count": len(ordered), "terminal_receipt_identity": terminal_identity,
        "finalizer_receipt_identity": finalizer_id, "retrieval_verification_identity": retrieval_id,
        "cost_closure_identity": cost_id, "safe_close_receipt_identity": safe_identity,
        "evidence_completeness": "COMPLETE", "missing_root_categories": [], "final_status": final_status,
        "all_success_conditions_met": final_pass, "failure_phase": None if final_pass else "OUTCOME",
        "failure_codes": failure_codes,
    })
    manifest_id, manifest_receipt, manifest_put_response = _put_record(
        bucket, prefix, "evidence/final-manifest", manifest_record, root=True,
        include_response=True)
    # The v2 observation is derived in memory from the terminal Put response;
    # it is not another S3 object and therefore cannot follow the terminal Put.
    observation = _control_record("aws_c0_final_manifest_publication_observation/v2", {
        "attempt_identity": launch["attempt_identity"], "workflow_execution_identity": _workflow_identity(event["workflow_execution_arn"]),
        "closure_seed_identity": identity("aws_c0_closure_seed/v1", seed_id), "closure_seed_object": seed_receipt,
        "final_manifest_identity": manifest_id, "final_manifest_object": manifest_receipt,
        "retrieval_verification_identity": retrieval_id, "retrieval_object": retrieval_receipt,
        "publication_disposition": "AWS_C0_FINAL_MANIFEST_PUBLISHED", "failure_phase": None, "failure_code": None,
    })
    observation_raw = canonical_bytes(observation)
    observation_id = identity("aws_c0_final_manifest_publication_observation/v2",
                              digest(b"AWS_C0_FINAL_MANIFEST_PUBLICATION_OBSERVATION_V2_NUL\0" + observation_raw))
    # Journal publication and its exact-version readback are the only finite
    # recursion exclusions: the sealed journal never captures its own Put/Get.
    sealed_journal = _ACTIVE_JOURNAL
    if sealed_journal is None:
        raise Refusal("finalizer journal absent before seal")
    finalizer_projection = sealed_journal.aggregate()
    _ACTIVE_JOURNAL = None
    try:
        finalizer_journal_identity, finalizer_journal_readback = publish_and_readback_finalizer_journal(
            journal=sealed_journal, bucket=bucket,
            key=prefix + FINALIZER_JOURNAL_SUFFIX,
            publisher=_finalizer_journal_publisher, readback=_finalizer_journal_readback)
    finally:
        _ACTIVE_JOURNAL = sealed_journal
    capture_aggregate = build_three_coordinate_capture_aggregate(
        attempt_identity=launch["attempt_identity"], handoff=controller_handoff,
        carrier_observation=carrier_observation,
        finalizer_journal_identity=finalizer_journal_identity,
        finalizer_readback=finalizer_journal_readback,
        finalizer_projection=finalizer_projection,
        finalizer_journal=sealed_journal,
        final_manifest_identity=manifest_id,
        final_manifest_receipt=manifest_receipt,
        final_manifest_put_response=manifest_put_response,
        final_manifest_preimage=manifest_record,
        publication_observation=observation,
        publication_observation_identity=observation_id,
        retrieval_identity=retrieval_id,
        retrieval_receipt=retrieval_receipt)
    response = {
        "schema": "aws_c0_closure_response/v3",
        "action": "closure", "response_variant": "FULL", "artifact_bucket_identity": _bucket_identity(),
        "final_status": final_status, "evidence_completeness": "COMPLETE",
        "workflow_execution_identity": _workflow_identity(event["workflow_execution_arn"]),
        "closure_seed_identity": identity("aws_c0_closure_seed/v1", seed_id), "closure_seed_object": seed_receipt,
        "history_retrieval_contract_identity": seed["history_retrieval_contract_identity"],
        "final_manifest_identity": manifest_id, "final_manifest_object": manifest_receipt,
        "retrieval_verification_identity": retrieval_id, "retrieval_object": retrieval_receipt,
        "final_manifest_publication_observation_identity": observation_id,
        "final_manifest_publication_observation_object": None,
        "history_pagination_transcript_identity": None, "history_pagination_transcript": None,
        "missing_root_categories": [], "failure_phase": None if final_pass else "OUTCOME",
        "failure_code": None if final_pass else failure_codes[0],
    }
    response["finalizer_journal_aggregate"] = capture_aggregate
    validate_closure_response_v3(response)
    _ACTIVE_JOURNAL = None
    return response


def validate_closure_response_v3(record: Any) -> dict[str, Any]:
    """Validate the fixed-size closure response without embedding journal history."""
    required = {"schema", "action", "response_variant", "artifact_bucket_identity", "final_status",
                "evidence_completeness", "workflow_execution_identity", "closure_seed_identity",
                "closure_seed_object", "history_retrieval_contract_identity", "final_manifest_identity",
                "final_manifest_object", "retrieval_verification_identity", "retrieval_object",
                "final_manifest_publication_observation_identity", "final_manifest_publication_observation_object",
                "history_pagination_transcript_identity", "history_pagination_transcript", "missing_root_categories",
                "failure_phase", "failure_code", "finalizer_journal_aggregate"}
    if not isinstance(record, dict) or set(record) != required or record.get("schema") != "aws_c0_closure_response/v3":
        raise Refusal("closure response v3 fields refused")
    aggregate = record["finalizer_journal_aggregate"]
    if record["action"] != "closure" or record["response_variant"] != "FULL" or not isinstance(aggregate, dict):
        raise Refusal("closure response v3 content refused")
    if set(aggregate) != FINAL_CAPTURE_AGGREGATE_FIELDS or aggregate["schema"] != "aws_c0_final_s3_capture_aggregate/v1":
        raise Refusal("closure response journal aggregate refused")
    excluded = ["proof_sha256", "proof_body_byte_count", "proof_body_excluded_fields_in_order",
                "proof_body_projection_disposition"]
    proof_preimage = {name: value for name, value in aggregate.items() if name not in excluded}
    proof_raw = canonical_bytes(proof_preimage)
    external_proof = aggregate["controller_journal_handoff_external_publication_readback_proof"]
    if (aggregate["proof_body_excluded_fields_in_order"] != excluded or
            aggregate["proof_body_byte_count"] != len(proof_raw) or
            aggregate["proof_sha256"] != digest(aggregate["proof_hash_domain"].encode() + b"\0" + proof_raw) or
            aggregate["total_envelope_count"] != aggregate["controller_envelope_count"] + aggregate["finalizer_envelope_count"] or
            not isinstance(external_proof, dict) or
            len(external_proof.get("binding_execution_receipts_in_order", [])) != 46 or
            len(aggregate["fixed_size_identity_and_receipt_hash_binding_receipts_in_order"]) != 24 or
            len(aggregate["terminal_operation_cross_binding_receipts_in_order"]) != 11 or
            len(aggregate["aggregate_arithmetic_time_and_hash_execution_receipts_in_order"]) != 9 or
            len(aggregate["journal_coordinate_receipt_equality_execution_receipts_in_order"]) != 3 or
            len(aggregate["final_manifest_publication_observation_binding_receipts_in_order"]) != 12 or
            aggregate["excluded_evidence_channel_operations_in_order"] != [
                "PUT_CONTROLLER_CAPTURE_JOURNAL", "GET_EXACT_CONTROLLER_CAPTURE_JOURNAL",
                "PUT_CONTROLLER_JOURNAL_HANDOFF", "PUT_FINALIZER_CAPTURE_JOURNAL",
                "GET_EXACT_FINALIZER_CAPTURE_JOURNAL"] or
            not aggregate["all_substantive_s3_operations_present"] or
            not aggregate["no_later_substantive_s3_operation"] or
            aggregate["step_functions_carried_full_history"] or
            aggregate["full_history_embedded_in_closure_response"] or
            record["final_manifest_publication_observation_object"] is not None):
        raise Refusal("closure response journal aggregate proof refused")
    return record


def build_publication_binding_v4(*, final_manifest_identity: dict[str, str], final_manifest_object: dict[str, Any],
                                 readback_identity: dict[str, str]) -> dict[str, Any]:
    record = {"schema": "aws_c0_publication_upgrade_binding/v4",
              "final_manifest_identity": final_manifest_identity,
              "final_manifest_object": final_manifest_object,
              "authenticated_readback_identity": readback_identity,
              "zero_science_counters": ZERO}
    return validate_publication_binding_v4(record)


def validate_publication_binding_v4(record: Any) -> dict[str, Any]:
    required = {"schema", "final_manifest_identity", "final_manifest_object", "authenticated_readback_identity", "zero_science_counters"}
    if not isinstance(record, dict) or set(record) != required or record["schema"] != "aws_c0_publication_upgrade_binding/v4":
        raise Refusal("publication binding v4 fields refused")
    _identity(record, "final_manifest_identity", "aws_c0_final_manifest/v4")
    if not isinstance(record["final_manifest_object"], dict) or record["zero_science_counters"] != ZERO:
        raise Refusal("publication binding v4 content refused")
    return record


def _history_fallback(execution_arn: str, phase: str, code: str,
                      missing: list[str]) -> dict[str, Any]:
    seed, receipt, seed_id = _exact_environment_record("CLOSURE_SEED", "aws_c0_closure_seed/v1", root=False)
    return {
        "action": "closure", "response_variant": "HISTORY_FALLBACK",
        "artifact_bucket_identity": _bucket_identity(), "final_status": "AWS_C0_FINAL_INCONCLUSIVE",
        "evidence_completeness": "INCOMPLETE", "workflow_execution_identity": _workflow_identity(execution_arn),
        "closure_seed_identity": identity("aws_c0_closure_seed/v1", seed_id), "closure_seed_object": receipt,
        "history_retrieval_contract_identity": seed["history_retrieval_contract_identity"],
        "final_manifest_identity": None, "final_manifest_object": None,
        "retrieval_verification_identity": None, "retrieval_object": None,
        "final_manifest_publication_observation_identity": None,
        "final_manifest_publication_observation_object": None,
        "history_pagination_transcript_identity": None, "history_pagination_transcript": None,
        "missing_root_categories": missing,
        "failure_phase": phase, "failure_code": code,
    }


def preflight_failure(event: dict[str, Any]) -> dict[str, Any]:
    if set(event) != {"action", "workflow_execution_arn"} or event["action"] != "preflight_failure":
        raise Refusal("preflight-failure event not closed")
    return _history_fallback(event["workflow_execution_arn"], "PREFLIGHT", "MALFORMED_OR_REFUSED_INPUT",
        ["LAUNCH", "START", "HEARTBEAT", "CHECKPOINT", "TERMINAL", "FINALIZER", "RETRIEVAL",
         "COST", "FINAL_MANIFEST", "FINAL_MANIFEST_PUBLICATION"])


def normalize_execution_history(execution_arn: str) -> tuple[dict[str, Any], dict[str, Any]]:
    """Fully paginate Standard history and locate one closed closure payload."""
    max_pages = int(_env("AWS_C0_HISTORY_MAX_PAGES")); max_events = int(_env("AWS_C0_HISTORY_MAX_EVENTS"))
    token: str | None = None; seen: set[str] = set(); pages: list[dict[str, Any]] = []; events: list[dict[str, Any]] = []
    for page_index in range(max_pages):
        request = {"executionArn": execution_arn, "includeExecutionData": True, "reverseOrder": False}
        if token is not None: request["nextToken"] = token
        response = _json_api("states", "AWSStepFunctions.GetExecutionHistory", request)
        page_events = response.get("events")
        if not isinstance(page_events, list): raise Refusal("history events absent")
        events.extend(page_events)
        if len(events) > max_events: raise Refusal("history event bound exceeded")
        outgoing = response.get("nextToken")
        if outgoing is not None and (not isinstance(outgoing, str) or outgoing in seen):
            raise Refusal("history pagination token invalid/repeated")
        pages.append({"page_index": page_index,
                      "request_sha256": digest(canonical_bytes(request)),
                      "response_sha256": digest(canonical_bytes(response)),
                      "incoming_token_sha256": None if token is None else digest(token.encode()),
                      "outgoing_token_sha256": None if outgoing is None else digest(outgoing.encode()),
                      "terminal": outgoing is None})
        if outgoing is None: break
        seen.add(outgoing); token = outgoing
    else: raise Refusal("history page bound exceeded")
    candidates: list[dict[str, Any]] = []
    for event in events:
        if event.get("type") != "TaskSucceeded": continue
        output = event.get("taskSucceededEventDetails", {}).get("output")
        if not isinstance(output, str): continue
        try: parsed = json.loads(output)
        except json.JSONDecodeError: continue
        payload = parsed.get("Payload", parsed) if isinstance(parsed, dict) else None
        if isinstance(payload, dict) and payload.get("action") == "closure": candidates.append(payload)
    if len(candidates) != 1: raise Refusal("history has zero/multiple closure TaskSucceeded payloads")
    transcript_preimage = {"schema": "aws_c0_pagination_transcript/v1", "source_api": "states:GetExecutionHistory",
        "pages": pages, "page_count": len(pages), "version_count": 0, "delete_marker_count": 0,
        "duplicate_coordinate_count": 0, "event_count": len(events), "sealed_max_pages": max_pages,
        "sealed_max_items": max_events, "sealed_max_events": max_events, "all_pages_consumed": True,
        "terminal_marker_observed": True,
        "repeated_token_observed": False}
    transcript = {**transcript_preimage,
                  "identity": identity("aws_c0_pagination_transcript/v1",
                                       digest(canonical_bytes(transcript_preimage)))}
    return candidates[0], transcript


def lambda_handler(event: Any, _context: Any) -> dict[str, Any]:
    global _ACTIVE_JOURNAL
    if not isinstance(event, dict) or not isinstance(event.get("action"), str):
        raise Refusal("event/action invalid")
    action = event["action"]
    if action == "preflight": return preflight(event)
    if action == "preflight_failure": return preflight_failure(event)
    if action == "poll": return poll(event)
    if action == "safe_close": return safe_close(event)
    if action == "closure":
        try:
            return closure(event)
        except Refusal as exc:
            return _history_fallback(event.get("workflow_execution_arn", ""), "CLOSURE",
                                     "CLOSURE_INCOMPLETE:" + str(exc),
                                     ["START", "HEARTBEAT", "CHECKPOINT", "TERMINAL", "FINALIZER",
                                      "RETRIEVAL", "COST", "FINAL_MANIFEST", "FINAL_MANIFEST_PUBLICATION"])
        finally:
            _ACTIVE_JOURNAL = None
    raise Refusal("unknown action")
