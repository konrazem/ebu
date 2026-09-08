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
    if proposal["permitted_api_operations"] != ["HeadObject", "GetObject"]:
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
