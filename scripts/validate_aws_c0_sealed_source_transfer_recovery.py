#!/usr/bin/env python3
"""Validate the local-only AWS-C0 sealed-source transfer recovery proposal."""
from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROPOSAL = ROOT / "aws_c0_sealed_source_transfer_recovery_proposal.json"
EXPECTED_CLASSES = [
    "STATE_MACHINE_DEFINITION",
    "SSM_DOCUMENT",
    "CONTROLLER",
    "SYSTEMD_UNIT",
    "FINALIZER_ZIP",
    "SYNTHETIC_IMAGE_ARCHIVE",
    "CONTAINER_RUNTIME_POLICY",
    "CLOUDFORMATION_TEMPLATE",
]
SOURCE_PATHS = {
    "STATE_MACHINE_DEFINITION": ROOT / "aws/c0/state-machine/aws-c0.asl.json",
    "SSM_DOCUMENT": ROOT / "aws/c0/ssm/EBU-C0-Start-v1.yaml",
    "CONTROLLER": ROOT / "aws/c0/controller/ebu_c0_controller.py",
    "SYSTEMD_UNIT": ROOT / "aws/c0/controller/ebu-c0@.service",
    "CONTAINER_RUNTIME_POLICY": ROOT / "aws/c0/container/Dockerfile",
    "CLOUDFORMATION_TEMPLATE": ROOT / "aws/c0/cloudformation/aws-c0-unattended-synthetic.yaml",
}


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def verify_bytes(item: dict, raw: bytes) -> None:
    if len(raw) != item["bytes"] or sha(raw) != item["sha256"]:
        raise RuntimeError("source byte mismatch: " + item["artifact_class"])
    expected_checksum = base64.b64encode(bytes.fromhex(item["sha256"])).decode()
    if item["checksum_sha256_base64"] != expected_checksum:
        raise RuntimeError("checksum encoding mismatch: " + item["artifact_class"])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image-archive", type=Path, required=True)
    parser.add_argument("--prior-publication-progress", type=Path, required=True)
    args = parser.parse_args()

    proposal = json.loads(PROPOSAL.read_bytes())
    if proposal["proposal_status"] != "PROSPECTIVE_NOT_EXECUTION_AUTHORITY":
        raise RuntimeError("proposal cannot grant execution authority")
    if proposal["permitted_api_operations"] != ["GetObject"]:
        raise RuntimeError("only exact-version read API operations are permitted")
    if proposal["permitted_iam_actions"] != ["s3:GetObjectVersion"]:
        raise RuntimeError("only the version-specific read IAM action is permitted")
    if proposal["transfer_operation"] != {
        "api_operation": "GetObject",
        "iam_action": "s3:GetObjectVersion",
        "source_selector": "EXACT_BOUND_BUCKET_KEY_AND_VERSION_ID_ONLY",
        "destination": "EPHEMERAL_LOCAL_VALIDATION_PATH_ONLY",
        "required_response_readback": "RETURNED_VERSION_ID_MUST_EQUAL_BOUND_VERSION_ID",
        "required_content_verification": "DOWNLOADED_BYTES_SHA256_AND_LENGTH_MUST_EQUAL_BOUND_VALUES",
        "retention": "DISPOSE_AFTER_VALIDATION",
    }:
        raise RuntimeError("bounded transfer operation changed")
    if set(proposal["prohibited_api_operations"]) != {
        "PutObject", "CopyObject", "DeleteObject", "DeleteObjects", "ListObjectsV2",
        "ListObjectVersions",
    }:
        raise RuntimeError("closed prohibited API-operation set changed")
    if set(proposal["prohibited_iam_actions"]) != {
        "s3:GetObject", "s3:PutObject", "s3:DeleteObject", "s3:DeleteObjectVersion",
        "s3:ListBucket", "s3:ListBucketVersions",
    }:
        raise RuntimeError("closed prohibited IAM-action set changed")
    artifacts = proposal["artifacts"]
    if [item["artifact_class"] for item in artifacts] != EXPECTED_CLASSES:
        raise RuntimeError("artifact order or membership changed")
    if len({(item["key"], item["version_id"]) for item in artifacts}) != 8:
        raise RuntimeError("eight unique exact-version objects required")
    if sum(item["bytes"] for item in artifacts) != proposal["aggregate_bytes"]:
        raise RuntimeError("aggregate byte count mismatch")
    for item in artifacts:
        if not item["key"].startswith(proposal["source_prefix"]):
            raise RuntimeError("object outside exact source prefix")
        if not item["version_id"] or item["version_id"] == "null":
            raise RuntimeError("non-null exact VersionId required")
        if item["artifact_class"] in SOURCE_PATHS:
            verify_bytes(item, SOURCE_PATHS[item["artifact_class"]].read_bytes())

    policy = proposal["exact_transfer_iam_policy"]
    if policy.get("Version") != "2012-10-17" or len(policy.get("Statement", [])) != 8:
        raise RuntimeError("eight-statement exact transfer policy required")
    expected_resources = {
        "arn:aws:s3:::" + proposal["bucket"] + "/" + item["key"]: item["version_id"]
        for item in artifacts
    }
    actual_resources = {}
    for statement in policy["Statement"]:
        if statement.get("Effect") != "Allow" or statement.get("Action") != "s3:GetObjectVersion":
            raise RuntimeError("transfer policy action is not exact-version read only")
        resource = statement.get("Resource")
        version_id = statement.get("Condition", {}).get("StringEquals", {}).get("s3:VersionId")
        resource_account = statement.get("Condition", {}).get("StringEquals", {}).get("s3:ResourceAccount")
        if resource in actual_resources or resource_account != proposal["aws_account_id"]:
            raise RuntimeError("transfer policy resource binding is not one-to-one")
        actual_resources[resource] = version_id
    if actual_resources != expected_resources:
        raise RuntimeError("transfer policy does not bind every exact object version")

    spec = importlib.util.spec_from_file_location(
        "deployment_manifest", ROOT / "scripts/build_aws_c0_deployment_manifest.py"
    )
    builder = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(builder)
    finalizer = next(item for item in artifacts if item["artifact_class"] == "FINALIZER_ZIP")
    finalizer_raw = builder.finalizer_zip_bytes((ROOT / "aws/c0/finalizer/finalizer.py").read_bytes())
    verify_bytes(finalizer, finalizer_raw)
    image = next(item for item in artifacts if item["artifact_class"] == "SYNTHETIC_IMAGE_ARCHIVE")
    verify_bytes(image, args.image_archive.read_bytes())

    prior_raw = args.prior_publication_progress.read_bytes()
    if sha(prior_raw) != proposal["prior_publication_progress_sha256"]:
        raise RuntimeError("prior publication evidence hash mismatch")
    prior = json.loads(prior_raw)
    receipts = prior["receipts_in_order"]
    by_class = {item["artifact_class"]: item for item in receipts}
    for item in artifacts:
        receipt = by_class.get(item["artifact_class"])
        for field in ("key", "version_id", "sha256", "bytes", "checksum_sha256_base64", "etag"):
            if receipt is None or receipt.get(field) != item[field]:
                raise RuntimeError("prior exact-version receipt mismatch: " + item["artifact_class"])

    if not all(proposal["explicit_exclusions"].values()):
        raise RuntimeError("every excluded scope must remain excluded")
    if proposal["current_contract_blocker"] != {
        "contract": "aws_c0_live_preparation_choreography_correction_contract.json",
        "rule": "C0-LPC-N34",
        "rule_text": "EXISTING_OBJECT_KEY_REUSE_REFUSES",
        "required_narrow_amendment": "DISTINGUISH_EXACT_READ_ONLY_IMMUTABLE_VERSION_REUSE_FROM_OBJECT_CREATION_OVERWRITE_OR_DELETE",
        "amendment_scope_limit": "THE_FRESH_KEY_RULE_REMAINS_MANDATORY_FOR_EVERY_NEW_PREPARATION_RECORD_AND_ALL_WRITES",
    }:
        raise RuntimeError("current contract blocker is not closed")
    subprocess.run(["git", "diff", "--check"], cwd=ROOT, check=True)
    print(json.dumps({
        "disposition": "LOCAL_TRANSFER_RECOVERY_PROPOSAL_PASS",
        "proposal_sha256": sha(PROPOSAL.read_bytes()),
        "artifact_count": len(artifacts),
        "aggregate_bytes": proposal["aggregate_bytes"],
        "aws_calls": 0,
        "scientific_executions": 0,
    }, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
