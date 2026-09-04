#!/usr/bin/env python3
"""Build an offline Gate 1 preparation-packet draft from sealed observations.

This never calls AWS and deliberately refuses absent, placeholder, or malformed
observation fields.  The resulting draft is an input to—not a substitute for—
the later exact Gate 1 authorization record.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

_spec = importlib.util.spec_from_file_location('aws_c0_pricing_collector', Path(__file__).with_name('collect_aws_c0_pricing.py'))
_pricing = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_pricing)
validate_model, maximum_cost = _pricing.validate_model, _pricing.maximum_cost


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
    if observations.get("cost_ceiling_minor_units") != 5000:
        raise ValueError("cost ceiling must equal 5000 minor units")
    cost_model = observations["cost_model"]
    evidence = observations.get("pricing_evidence", {})
    # Canonical JSON orders object keys lexically; restore the frozen dimension
    # order explicitly while rejecting missing or extra evidence dimensions.
    if set(evidence) != set(COST_DIMENSIONS):
        raise ValueError("complete 22-dimension pricing evidence required")
    validate_model(cost_model, {d: evidence[d] for d in COST_DIMENSIONS})
    cost_bound = maximum_cost(cost_model, observations.get("resource_limits", {}))
    if observations.get("change_set_plan", {}).get("change_set_type") != "CREATE":
        raise ValueError("change-set plan must be CREATE only")
    return {
        "schema": "aws_c0_gate1_preparation_packet_draft/v1",
        "record_class": "NON_SCIENTIFIC_AWS_C0_CONTROL_EVIDENCE",
        "local_material_manifest_sha256": hashlib.sha256(canonical(manifest)).hexdigest(),
        "repository_commit": manifest["repository_commit"],
        "repository_tree": manifest["repository_tree"],
        "observations": observations,
        "computed_cost_bound_minor_units": cost_bound,
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
    raw = canonical(build(load(args.manifest), load(args.observations)))
    with args.output.open('xb') as stream:
        stream.write(raw)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
