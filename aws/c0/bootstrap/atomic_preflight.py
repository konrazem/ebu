"""Fail-closed AWS-C0 sealed-source atomic preflight executor.

The caller injects an already constrained S3 client.  This module never creates
credentials, mutates IAM, starts an instance, deploys, or executes science.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
from pathlib import Path

ACCOUNT = "623609441658"
REGION = "us-east-1"
SESSION = "AWS-C0-PREP-492a4f1"
PROPOSAL_PATH = "aws_c0_sealed_source_transfer_recovery_proposal.json"
CONTRACT_PATH = "aws_c0_sealed_source_transfer_reuse_contract.json"
SHA64 = re.compile(r"[0-9a-f]{64}")
SHA40 = re.compile(r"[0-9a-f]{40}")


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _load(root, name):
    return json.loads((Path(root) / name).read_bytes())


def plan(root, implementation_commit, implementation_tree, attempt_identity_sha256):
    if not SHA40.fullmatch(implementation_commit) or not SHA40.fullmatch(implementation_tree):
        raise ValueError("exact implementation commit and tree required")
    if not SHA64.fullmatch(attempt_identity_sha256):
        raise ValueError("fresh attempt identity SHA-256 required")
    proposal = _load(root, PROPOSAL_PATH)
    contract = _load(root, CONTRACT_PATH)
    if contract.get("proposal_sha256") != sha((Path(root) / PROPOSAL_PATH).read_bytes()):
        raise ValueError("reuse contract proposal binding mismatch")
    if contract.get("required_source_binding") != {
        "bucket": proposal["bucket"], "account_id": ACCOUNT, "region": REGION,
        "artifact_count": 8, "aggregate_bytes": 415108495, "only_api_operation": "GetObject",
        "only_iam_action": "s3:GetObjectVersion",
        "requires_exact_key_version_id_returned_version_id_byte_length_and_sha256": True,
    }:
        raise ValueError("exact reuse source contract required")
    requests = [{
        "artifact_class": item["artifact_class"], "bucket": proposal["bucket"], "key": item["key"],
        "version_id": item["version_id"], "expected_bytes": item["bytes"],
        "expected_sha256": item["sha256"], "expected_checksum_sha256_base64": item["checksum_sha256_base64"],
        "expected_etag": item["etag"], "expected_bucket_owner": ACCOUNT, "checksum_mode": "ENABLED",
    } for item in proposal["artifacts"]]
    value = {
        "schema": "aws_c0_sealed_source_atomic_preflight_plan/v1",
        "record_class": "NON_SCIENTIFIC_AWS_C0_OPERATIONAL_PLAN",
        "implementation_commit": implementation_commit, "implementation_tree": implementation_tree,
        "attempt_identity_sha256": attempt_identity_sha256, "session_name": SESSION,
        "account_id": ACCOUNT, "region": REGION,
        "proposal_sha256": sha((Path(root) / PROPOSAL_PATH).read_bytes()),
        "reuse_contract_sha256": sha((Path(root) / CONTRACT_PATH).read_bytes()),
        "transfer_policy_sha256": sha(canonical(proposal["exact_transfer_iam_policy"])),
        "requests_in_order": requests, "maximum_get_object_calls": 8,
        "maximum_transfer_bytes": proposal["aggregate_bytes"], "freshness_max_seconds": 300,
        "new_object_puts": 0, "iam_mutations": 0, "instance_starts": 0,
        "platform_smokes": 0, "scientific_executions": 0,
    }
    return value


def validate_plan(root, value):
    if not isinstance(value, dict):
        raise ValueError("atomic preflight plan object required")
    embedded = copy.deepcopy(value)
    expected = plan(root, embedded["implementation_commit"], embedded["implementation_tree"],
                    embedded["attempt_identity_sha256"])
    if value != expected:
        raise ValueError("atomic preflight plan differs from exact sealed inputs")
    return value


def read_one(client, request):
    response = client.get_object(Bucket=request["bucket"], Key=request["key"], VersionId=request["version_id"],
                                 ChecksumMode="ENABLED", ExpectedBucketOwner=request["expected_bucket_owner"])
    body = response.get("Body")
    if body is None or not hasattr(body, "read"):
        raise ValueError("streaming response body required")
    digest = hashlib.sha256(); count = 0
    try:
        while True:
            chunk = body.read(1048576)
            if not chunk:
                break
            if not isinstance(chunk, bytes):
                raise ValueError("binary response chunks required")
            digest.update(chunk); count += len(chunk)
            if count > request["expected_bytes"]:
                raise ValueError("response exceeds exact byte bound")
    finally:
        close = getattr(body, "close", None)
        if close:
            close()
    metadata = response.get("ResponseMetadata", {})
    request_id = metadata.get("RequestId")
    if (response.get("VersionId") != request["version_id"] or response.get("ContentLength") != count
            or count != request["expected_bytes"] or digest.hexdigest() != request["expected_sha256"]
            or response.get("ChecksumSHA256") != request["expected_checksum_sha256_base64"]
            or response.get("ETag") != request["expected_etag"] or not isinstance(request_id, str) or not request_id):
        raise ValueError("exact-version response binding mismatch")
    return {
        "artifact_class": request["artifact_class"], "bucket": request["bucket"], "key": request["key"],
        "version_id": response["VersionId"], "bytes": count, "sha256": digest.hexdigest(),
        "checksum_sha256_base64": response["ChecksumSHA256"], "etag": response.get("ETag"),
        "request_id": request_id,
    }


def execute(client, root, value):
    validate_plan(root, value)
    receipts = [read_one(client, request) for request in value["requests_in_order"]]
    result = {
        "schema": "aws_c0_sealed_source_atomic_preflight_result/v1",
        "plan_sha256": sha(canonical(value)), "attempt_identity_sha256": value["attempt_identity_sha256"],
        "receipts_in_order": receipts, "get_object_calls": len(receipts),
        "transferred_bytes": sum(item["bytes"] for item in receipts),
        "new_object_puts": 0, "iam_mutations": 0, "instance_starts": 0,
        "platform_smokes": 0, "scientific_executions": 0,
        "disposition": "SEALED_SOURCE_ATOMIC_PREFLIGHT_PASS",
    }
    if result["get_object_calls"] != 8 or result["transferred_bytes"] != value["maximum_transfer_bytes"]:
        raise ValueError("complete eight-object atomic receipt set required")
    return result
