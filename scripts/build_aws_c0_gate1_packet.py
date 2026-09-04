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
