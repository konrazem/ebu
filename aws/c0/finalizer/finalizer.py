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
                    "sequence": len(self.envelopes), "operation": operation,
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
                                             finalizer_projection: dict[str, Any]) -> dict[str, Any]:
    """Bind controller journal, fixed-key carrier, and finalizer journal."""
    if handoff.get("attempt_identity") != attempt_identity:
        raise Refusal("capture aggregate attempt mismatch")
    if (not isinstance(finalizer_journal_identity, dict) or
            finalizer_journal_identity.get("kind") != "aws_c0_finalizer_capture_journal/v1" or
            finalizer_journal_identity.get("value") != finalizer_journal_identity.get("sha256") or
            not SHA.fullmatch(str(finalizer_journal_identity.get("sha256", "")))):
        raise Refusal("capture aggregate finalizer identity refused")
    finalizer_readback_fields = {
        "schema", "content_chain_sha256", "publication_receipt",
        "publication_receipt_identity", "readback_receipt", "readback_receipt_identity",
    }
    if (not isinstance(finalizer_readback, dict) or
            set(finalizer_readback) != finalizer_readback_fields or
            finalizer_readback.get("schema") != "aws_c0_journal_authenticated_readback/v1"):
        raise Refusal("capture aggregate finalizer readback refused")
    publication = finalizer_readback["publication_receipt"]
    readback = finalizer_readback["readback_receipt"]
    if any(publication[name] != readback[name] for name in
           ("key", "version_id", "etag", "bytes", "sha256", "checksum_sha256_base64")):
        raise Refusal("capture aggregate finalizer coordinates mismatch")
    controller_object = handoff["controller_journal_object"]
    carrier_key = carrier_observation["key"]
    carrier_fields = {
        "schema", "key", "version_id", "etag", "checksum_sha256_base64",
        "bytes", "sha256", "list_transcript_identity", "handoff_identity",
        "handoff_canonical_sha256", "controller_journal_version_id",
        "controller_publication_receipt_identity", "controller_envelope_count",
    }
    if (set(carrier_observation) != carrier_fields or
            carrier_observation["schema"] != "aws_c0_controller_journal_handoff_external_proof/v1" or
            not carrier_key.endswith("/" + CONTROLLER_JOURNAL_HANDOFF_SUFFIX) or
            not VERSION.fullmatch(str(carrier_observation["version_id"])) or
            not SHA.fullmatch(str(carrier_observation["sha256"])) or
            carrier_observation["handoff_identity"] != handoff["handoff_identity"] or
            carrier_observation["handoff_canonical_sha256"] != handoff["handoff_canonical_sha256"] or
            carrier_observation["controller_journal_version_id"] != controller_object["version_id"] or
            carrier_observation["controller_publication_receipt_identity"] != handoff["controller_publication_receipt_identity"]):
        raise Refusal("capture aggregate carrier observation refused")
    expected_publication_identity = identity(
        "aws_c0_capture_journal_publication_receipt/v1",
        digest(canonical_bytes({"bucket_name": controller_object["bucket"], **publication})),
    )
    expected_readback_identity = identity(
        "aws_c0_capture_journal_readback_receipt/v1",
        digest(canonical_bytes({"bucket_name": controller_object["bucket"], **readback})),
    )
    if (finalizer_readback["publication_receipt_identity"] != expected_publication_identity or
            finalizer_readback["readback_receipt_identity"] != expected_readback_identity or
            not SHA.fullmatch(str(finalizer_readback["content_chain_sha256"]))):
        raise Refusal("capture aggregate finalizer receipt references refused")
    if len({controller_object["key"], carrier_key, publication["key"]}) != 3:
        raise Refusal("capture aggregate keys are not pairwise distinct")
    aggregate = {
        "schema": "aws_c0_final_s3_capture_aggregate/v1",
        "attempt_identity": attempt_identity,
        "controller_journal_identity": identity(
            "aws_c0_controller_capture_journal/v1", controller_object["object_sha256"]),
        "controller_journal_bucket_name": controller_object["bucket"],
        "controller_journal_byte_count": controller_object["byte_count"],
        "controller_published_object_sha256": controller_object["object_sha256"],
        "controller_content_chain_sha256": controller_object["content_chain_sha256"],
        "controller_journal_version_id": controller_object["version_id"],
        "controller_journal_etag": controller_object["etag"],
        "controller_journal_checksum_sha256_base64": controller_object["checksum_sha256_base64"],
        "controller_publication_receipt_identity": handoff["controller_publication_receipt_identity"],
        "controller_publication_receipt_sha256": handoff["controller_publication_receipt_identity"]["sha256"],
        "controller_readback_receipt_identity": handoff["controller_readback_receipt_identity"],
        "controller_readback_receipt_sha256": handoff["controller_readback_receipt_identity"]["sha256"],
        "controller_local_journal_validation_receipt_identity": handoff["controller_local_validation_receipt_identity"],
        "controller_local_journal_validation_receipt_sha256": handoff["controller_local_validation_receipt_sha256"],
        "controller_journal_key": controller_object["key"],
        "controller_journal_handoff_identity": handoff["handoff_identity"],
        "controller_journal_handoff_sha256": handoff["handoff_canonical_sha256"],
        "controller_journal_handoff_bucket_name": controller_object["bucket"],
        "controller_journal_handoff_key": carrier_key,
        "controller_journal_handoff_version_id": carrier_observation["version_id"],
        "controller_journal_handoff_etag": carrier_observation["etag"],
        "controller_journal_handoff_checksum_sha256_base64": carrier_observation["checksum_sha256_base64"],
        "controller_journal_handoff_byte_count": carrier_observation["bytes"],
        "controller_journal_handoff_object_sha256": carrier_observation["sha256"],
        "controller_journal_handoff_list_transcript_identity": carrier_observation["list_transcript_identity"],
        "finalizer_journal_identity": finalizer_journal_identity,
        "finalizer_journal_bucket_name": controller_object["bucket"],
        "finalizer_journal_key": publication["key"],
        "finalizer_journal_version_id": publication["version_id"],
        "finalizer_journal_etag": publication["etag"],
        "finalizer_journal_checksum_sha256_base64": publication["checksum_sha256_base64"],
        "finalizer_journal_byte_count": publication["bytes"],
        "finalizer_published_object_sha256": publication["sha256"],
        "finalizer_content_chain_sha256": finalizer_readback["content_chain_sha256"],
        "finalizer_publication_receipt_identity": finalizer_readback["publication_receipt_identity"],
        "finalizer_publication_receipt_sha256": finalizer_readback["publication_receipt_identity"]["sha256"],
        "finalizer_readback_receipt_identity": finalizer_readback["readback_receipt_identity"],
        "finalizer_readback_receipt_sha256": finalizer_readback["readback_receipt_identity"]["sha256"],
        "controller_envelope_count": carrier_observation["controller_envelope_count"],
        "finalizer_envelope_count": finalizer_projection["envelope_count"],
        "total_envelope_count": carrier_observation["controller_envelope_count"] + finalizer_projection["envelope_count"],
        "excluded_evidence_channel_operations_in_order": [
            "PUT_CONTROLLER_CAPTURE_JOURNAL", "GET_EXACT_CONTROLLER_CAPTURE_JOURNAL",
            "PUT_CONTROLLER_JOURNAL_HANDOFF", "PUT_FINALIZER_CAPTURE_JOURNAL",
            "GET_EXACT_FINALIZER_CAPTURE_JOURNAL",
        ],
        "all_substantive_s3_operations_present": True,
        "no_later_substantive_s3_operation": True,
        "step_functions_carried_full_history": False,
        "full_history_embedded_in_closure_response": False,
        "aggregate_disposition": "EXACT_TWO_JOURNALS_PLUS_ONE_FIXED_CARRIER_VALIDATED_PASS",
    }
    aggregate["proof_sha256"] = digest(canonical_bytes(aggregate))
    return aggregate


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
    capture = {"service": service, "method": method, "host": host, "path": canonical_uri,
               "query_sha256": digest(canonical_query.encode()), "request_body_sha256": digest(body),
               "sigv4_algorithm": "AWS4-HMAC-SHA256", "signed_headers": signed_headers}
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
                journal.append(f"{service.upper()}_{method}", {**capture, "response_sha256": digest(raw),
                               "observed_version_id": observed.get("x-amz-version-id"),
                               "observed_checksum_sha256": observed.get("x-amz-checksum-sha256"),
                               "observed_request_id": observed.get("x-amz-request-id")}, "OBSERVED_COMPLETE")
            return raw, observed
    except urllib.error.HTTPError as exc:
        if journal is not None:
            journal.append(f"{service.upper()}_{method}", {**capture, "failure_class": "HTTPError", "status": exc.code}, "OBSERVED_FAILURE")
        raise Refusal(f"AWS {service} request refused:{exc.code}") from exc
    except urllib.error.URLError as exc:
        if journal is not None:
            journal.append(f"{service.upper()}_{method}", {**capture, "failure_class": "URLError"}, "OBSERVED_FAILURE")
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
    if not VERSION.fullmatch(version):
        raise Refusal("fresh version receipt absent")
    return {"key": key, "version_id": version, "bytes": len(raw),
            "sha256": digest(raw), "checksum_sha256_base64": checksum}


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
    publication_required = {"key", "version_id", "etag", "bytes", "sha256", "checksum_sha256_base64"}
    if (not isinstance(publication, dict) or set(publication) != publication_required or
            not isinstance(readback, dict) or set(readback) != publication_required | {"request_id"} or
            any(publication[name] != readback[name] for name in publication_required)):
        raise Refusal("controller journal handoff receipt preimages refused")
    publication_identity = identity(
        "aws_c0_capture_journal_publication_receipt/v1",
        digest(canonical_bytes({"bucket_name": bucket, **publication})),
    )
    readback_identity = identity(
        "aws_c0_capture_journal_readback_receipt/v1",
        digest(canonical_bytes({"bucket_name": bucket, **readback})),
    )
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
            journal_object["byte_count"] != publication["bytes"] or
            journal_object["object_sha256"] != publication["sha256"] or
            not SHA.fullmatch(str(journal_object["content_chain_sha256"]))):
        raise Refusal("controller journal handoff object coordinate refused")
    receipts = value["controller_receipt_coordinate_execution_receipts_in_order"]
    if not isinstance(receipts, list) or len(receipts) != 22:
        raise Refusal("controller journal handoff coordinate receipts refused")
    for order, receipt in enumerate(receipts, 1):
        if (not isinstance(receipt, dict) or set(receipt) != {
                "order", "descriptor_id", "left", "right", "comparison", "receipt_sha256"} or
                receipt["order"] != order):
            raise Refusal("controller journal handoff receipt order refused")
        preimage = {name: receipt[name] for name in
                    ("order", "descriptor_id", "left", "right", "comparison")}
        if receipt["receipt_sha256"] != digest(canonical_bytes(preimage)):
            raise Refusal("controller journal handoff receipt digest refused")
    if ([receipts[-2]["descriptor_id"], receipts[-1]["descriptor_id"]] !=
            ["HANDOFF_PUBLICATION_IDENTITY_021", "HANDOFF_READBACK_IDENTITY_022"]):
        raise Refusal("controller journal handoff receipt tail refused")
    local_preimage = {
        "attempt_identity": attempt_identity, "controller_journal_object": journal_object,
        "controller_publication_receipt_identity": publication_identity,
        "controller_readback_receipt_identity": readback_identity,
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
        "schema": "aws_c0_controller_journal_handoff_external_proof/v1",
        "key": key, "version_id": version, "etag": etag,
        "checksum_sha256_base64": checksum, "bytes": len(raw), "sha256": digest(raw),
        "list_transcript_identity": transcript["identity"],
        "handoff_identity": handoff["handoff_identity"],
        "handoff_canonical_sha256": handoff["handoff_canonical_sha256"],
        "controller_journal_version_id": coordinate["version_id"],
        "controller_publication_receipt_identity": handoff["controller_publication_receipt_identity"],
        "controller_envelope_count": journal["envelope_count"],
    }
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
                *, root: bool) -> tuple[dict[str, Any], dict[str, Any]]:
    raw = canonical_bytes(record)
    record_id = _root_digest(record) if root else digest(raw)
    key = f"{prefix}{category}-{record_id}.json"
    return identity(record["schema"], record_id), _full_receipt(_s3_put(bucket, key, raw))


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
    manifest_id, manifest_receipt = _put_record(bucket, prefix, "evidence/final-manifest", manifest_record, root=True)
    observation = _control_record("aws_c0_final_manifest_publication_observation/v1", {
        "attempt_identity": launch["attempt_identity"], "workflow_execution_identity": _workflow_identity(event["workflow_execution_arn"]),
        "closure_seed_identity": identity("aws_c0_closure_seed/v1", seed_id), "closure_seed_object": seed_receipt,
        "final_manifest_identity": manifest_id, "final_manifest_object": manifest_receipt,
        "retrieval_verification_identity": retrieval_id, "retrieval_object": retrieval_receipt,
        "publication_disposition": "AWS_C0_FINAL_MANIFEST_PUBLISHED", "failure_phase": None, "failure_code": None,
    })
    observation_id, observation_receipt = _put_record(bucket, prefix, "control/final-manifest-publication", observation, root=False)
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
        finalizer_projection=finalizer_projection)
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
        "final_manifest_publication_observation_object": observation_receipt,
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
    aggregate_fields = {
        "schema", "attempt_identity", "controller_journal_identity",
        "controller_journal_bucket_name", "controller_journal_byte_count",
        "controller_published_object_sha256", "controller_content_chain_sha256",
        "controller_journal_version_id", "controller_journal_etag",
        "controller_journal_checksum_sha256_base64",
        "controller_publication_receipt_identity", "controller_readback_receipt_identity",
        "controller_publication_receipt_sha256", "controller_readback_receipt_sha256",
        "controller_local_journal_validation_receipt_identity",
        "controller_local_journal_validation_receipt_sha256", "controller_journal_key",
        "controller_journal_handoff_identity", "controller_journal_handoff_key",
        "controller_journal_handoff_sha256", "controller_journal_handoff_bucket_name",
        "controller_journal_handoff_version_id", "controller_journal_handoff_etag",
        "controller_journal_handoff_checksum_sha256_base64",
        "controller_journal_handoff_byte_count", "controller_journal_handoff_object_sha256",
        "controller_journal_handoff_list_transcript_identity", "finalizer_journal_identity",
        "finalizer_journal_bucket_name", "finalizer_journal_key", "finalizer_journal_version_id",
        "finalizer_journal_etag", "finalizer_journal_checksum_sha256_base64",
        "finalizer_journal_byte_count", "finalizer_published_object_sha256",
        "finalizer_content_chain_sha256", "finalizer_publication_receipt_identity",
        "finalizer_publication_receipt_sha256", "finalizer_readback_receipt_identity",
        "finalizer_readback_receipt_sha256", "controller_envelope_count",
        "finalizer_envelope_count", "total_envelope_count",
        "excluded_evidence_channel_operations_in_order", "all_substantive_s3_operations_present",
        "no_later_substantive_s3_operation", "step_functions_carried_full_history",
        "full_history_embedded_in_closure_response", "aggregate_disposition", "proof_sha256",
    }
    if set(aggregate) != aggregate_fields or aggregate["schema"] != "aws_c0_final_s3_capture_aggregate/v1":
        raise Refusal("closure response journal aggregate refused")
    proof_preimage = {name: value for name, value in aggregate.items() if name != "proof_sha256"}
    if (aggregate["proof_sha256"] != digest(canonical_bytes(proof_preimage)) or
            aggregate["total_envelope_count"] != aggregate["controller_envelope_count"] + aggregate["finalizer_envelope_count"] or
            aggregate["excluded_evidence_channel_operations_in_order"] != [
                "PUT_CONTROLLER_CAPTURE_JOURNAL", "GET_EXACT_CONTROLLER_CAPTURE_JOURNAL",
                "PUT_CONTROLLER_JOURNAL_HANDOFF", "PUT_FINALIZER_CAPTURE_JOURNAL",
                "GET_EXACT_FINALIZER_CAPTURE_JOURNAL"] or
            not aggregate["all_substantive_s3_operations_present"] or
            not aggregate["no_later_substantive_s3_operation"] or
            aggregate["step_functions_carried_full_history"] or
            aggregate["full_history_embedded_in_closure_response"]):
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
