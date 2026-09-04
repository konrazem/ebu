#!/usr/bin/env python3
"""Build an offline Gate 1 preparation-packet draft from sealed observations.

This never calls AWS and deliberately refuses absent, placeholder, or malformed
observation fields.  The resulting draft is an input to—not a substitute for—
the later exact Gate 1 authorization record.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


REQUIRED = (
    "account_identity", "artifact_bucket_controls", "instance_preimage",
    "network_path", "cost_model", "change_set_plan",
)
PLANNED_ACTIONS = (
    "RECHECK_READ_ONLY_PREFLIGHT", "APPLY_EXACT_IAM_REMEDIATION",
    "STAGE_EXACT_PRE_LIVE_OBJECTS", "BOOTSTRAP_EXACT_STOPPED_INSTANCE",
    "CREATE_ONE_UNEXECUTED_CHANGE_SET", "FINALIZE_EXACT_LIVE_PACKET",
)
DENIED_ACTIONS = ("LIVE_EXECUTION", "REPLAY", "DELETE", "TERMINATE", "SCIENTIFIC_EXECUTION")
COST_DIMENSIONS = (
    "instance_running_seconds", "public_ipv4_seconds", "nat_gateway_seconds", "vpc_endpoint_seconds",
    "s3_put_requests", "s3_get_requests", "s3_head_requests", "s3_list_requests", "step_functions_transitions",
    "lambda_invocations", "lambda_duration_milliseconds", "kms_requests", "kms_key_seconds", "data_transfer_bytes",
    "cloudwatch_ingested_bytes", "ebs_volume_gib_seconds", "ebs_provisioned_iops_seconds",
    "ebs_provisioned_throughput_mibps_seconds", "s3_version_byte_seconds", "cloudwatch_log_byte_seconds",
    "ecr_byte_seconds", "snapshot_gib_seconds",
)


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()


def load(path: Path) -> dict:
    raw = path.read_bytes()
    if raw.endswith(b"\n"):
        raw = raw[:-1]
    value = json.loads(raw)
    if canonical(value) != raw:
        raise ValueError(f"{path} is not canonical JSON")
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def build(manifest: dict, observations: dict) -> dict:
    missing = [field for field in REQUIRED if not observations.get(field)]
    if missing:
        raise ValueError("missing required authenticated observations: " + ", ".join(missing))
    if observations.get("instance_preimage", {}).get("state") != "stopped":
        raise ValueError("initial instance state must be stopped")
    if observations.get("cost_model", {}).get("ceiling_minor_units") != 5000:
        raise ValueError("cost ceiling must equal 5000 minor units")
    cost_model = observations["cost_model"]
    dimensions = cost_model.get("dimensions")
    if not isinstance(dimensions, list) or tuple(row.get("dimension") for row in dimensions if isinstance(row, dict)) != COST_DIMENSIONS:
        raise ValueError("cost model must contain the exact ordered 22-dimension set")
    if any(not isinstance(row.get("rate_observation_sha256"), str) or len(row["rate_observation_sha256"]) != 64
           for row in dimensions):
        raise ValueError("every cost dimension needs an exact rate-observation digest")
    pages = cost_model.get("pagination_receipts")
    if not isinstance(pages, list) or not pages or pages[-1].get("next_token") is not None:
        raise ValueError("cost evidence pagination must be complete with a terminal null token")
    if any(not isinstance(page, dict) or not isinstance(page.get("response_sha256"), str) or len(page["response_sha256"]) != 64
           for page in pages):
        raise ValueError("each price page needs an exact response digest")
    if observations.get("change_set_plan", {}).get("change_set_type") != "CREATE":
        raise ValueError("change-set plan must be CREATE only")
    return {
        "schema": "aws_c0_gate1_preparation_packet_draft/v1",
        "record_class": "NON_SCIENTIFIC_AWS_C0_CONTROL_EVIDENCE",
        "local_material_manifest_sha256": hashlib.sha256(canonical(manifest)).hexdigest(),
        "repository_commit": manifest["repository_commit"],
        "repository_tree": manifest["repository_tree"],
        "observations": observations,
        "planned_actions": list(PLANNED_ACTIONS),
        "denied_actions": list(DENIED_ACTIONS),
        "disposition": "DRAFT_REQUIRES_FRESH_EXACT_GATE1_AUTHORIZATION",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--observations", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.write_bytes(canonical(build(load(args.manifest), load(args.observations))) + b"\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
