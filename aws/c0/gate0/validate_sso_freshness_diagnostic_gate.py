#!/usr/bin/env python3
"""Offline gate for the AWS-C0 SSO replay prerequisites.

This program never invokes AWS.  It validates a caller-supplied local evidence
record before an attempt state may be created or an AWS mutation considered.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
MATERIAL = HERE / "sso-operator-bootstrap-v3.template.json"
ZERO_COUNTERS = {
    "ebu_framework_import_count": 0,
    "model_state_advance_count": 0,
    "outcome_inspection_count": 0,
    "project_runner_import_count": 0,
    "registered_configuration_count": 0,
    "scientific_output_count": 0,
    "scientific_rng_draw_count": 0,
    "simulation_or_gate_count": 0,
    "stage_e_harness_import_count": 0,
    "trajectory_count": 0,
}


class GateError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise GateError(message)


def load_json_with_bytes(path: Path) -> tuple[bytes, dict[str, Any]]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        raise GateError(f"invalid JSON: {path}") from exc
    require(type(value) is dict, "JSON root must be an object")
    return raw, value


def load_json(path: Path) -> dict[str, Any]:
    return load_json_with_bytes(path)[1]


def utc(value: Any, field: str) -> datetime:
    require(type(value) is str and value.endswith("Z"), f"{field} must be a UTC Z timestamp")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise GateError(f"{field} is invalid") from exc
    require(parsed.tzinfo == timezone.utc, f"{field} is not UTC")
    return parsed


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def validate_equivalence_record(material: dict[str, Any], raw: bytes, record: dict[str, Any]) -> None:
    sealed = material["sealed_effective_permissions_equivalence"]
    require(hashlib.sha256(raw).hexdigest() == sealed["sha256"],
            "effective-permissions equivalence record digest mismatch")
    for field, expected in sealed.items():
        if field not in {"sha256", "comparison_count"}:
            require(record.get(field) == expected, f"equivalence record {field} mismatch")
    comparison = record.get("comparison")
    require(type(comparison) is list and len(comparison) == sealed["comparison_count"],
            "equivalence comparison coverage mismatch")
    for row in comparison:
        require(type(row) is dict and type(row.get("action")) is str,
                "equivalence comparison row is invalid")
        require(type(row.get("v4_effective_allow")) is bool and
                type(row.get("v5_effective_allow")) is bool and
                row["v4_effective_allow"] == row["v5_effective_allow"],
                "effective permission broadening or narrowing detected")


def validate(material: dict[str, Any], evidence: dict[str, Any], equivalence_raw: bytes,
             equivalence_record: dict[str, Any]) -> dict[str, Any]:
    gate = material["freshness_diagnostic_gate"]
    requirements = material["preparation_session_policy_requirements"]
    expected_caller = material["exact_sso_caller"]

    require(evidence.get("schema") == "aws_c0_gate0_freshness_diagnostic_evidence/v1", "wrong evidence schema")
    require(evidence.get("caller") == expected_caller, "caller does not match sealed SSO identity")
    require(evidence.get("source_identity") == material["sessions"]["source_identity"], "source identity mismatch")
    require(evidence.get("credential_provider_type") == gate["provider_type"], "credential provider must be sso")
    require(utc(evidence.get("credential_cache_mtime_utc"), "credential_cache_mtime_utc") >=
            utc(evidence.get("login_completed_utc"), "login_completed_utc"),
            "cached SSO credential predates login completion")

    diagnosis = evidence.get("prior_denial")
    require(type(diagnosis) is dict, "prior_denial must be an object")
    require(diagnosis.get("causal_trust_condition_mismatch_proven") is False,
            "unproven trust diagnosis required for this replay gate")
    require(diagnosis.get("disposition") ==
            gate["prior_denial_disposition_when_causal_trust_mismatch_unproven"],
            "prior denial disposition mismatch")
    require(diagnosis.get("packed_policy_rejection_percent") ==
            requirements["v4_rejected_packed_policy_percent"],
            "sealed packed-policy diagnosis mismatch")

    wait_seconds = (utc(evidence.get("assume_not_before_utc"), "assume_not_before_utc") -
                    utc(evidence.get("role_created_utc"), "role_created_utc")).total_seconds()
    require(wait_seconds >= gate["minimum_iam_to_sts_propagation_wait_seconds"],
            "IAM-to-STS propagation hold is too short")

    candidate_policy = evidence.get("candidate_preparation_session_policy")
    require(candidate_policy == requirements["policy"], "candidate policy differs from sealed compact ceiling")
    require(len(canonical_bytes(candidate_policy)) <= requirements["canonical_maximum_bytes"],
            "candidate policy exceeds compact canonical-byte ceiling")
    require(hashlib.sha256(canonical_bytes(candidate_policy)).hexdigest() ==
            material["sealed_effective_permissions_equivalence"]["v5_preparation_session_policy_sha256"],
            "candidate policy digest differs from sealed equivalence target")
    require(evidence.get("effective_permissions_equivalence_sha256") ==
            material["sealed_effective_permissions_equivalence"]["sha256"],
            "effective-permissions equivalence identity mismatch")
    validate_equivalence_record(material, equivalence_raw, equivalence_record)
    require(evidence.get("trust_policy_changed") is False,
            "new trust-policy change is not permitted by this gate")
    require(evidence.get("attempt_state_exists") is False,
            "attempt state must not exist before gate success")
    require(evidence.get("zero_science_counters") == ZERO_COUNTERS,
            "zero-science counters mismatch")

    return {
        "candidate_policy_bytes": len(canonical_bytes(candidate_policy)),
        "iam_to_sts_propagation_wait_seconds": int(wait_seconds),
        "result": "SSO_FRESHNESS_DIAGNOSTIC_GATE_PASS",
        "trust_policy_changed": False,
    }


def example_evidence(material: dict[str, Any]) -> dict[str, Any]:
    return {
        "assume_not_before_utc": "2026-09-04T12:04:00Z",
        "attempt_state_exists": False,
        "caller": material["exact_sso_caller"],
        "candidate_preparation_session_policy": material["preparation_session_policy_requirements"]["policy"],
        "credential_cache_mtime_utc": "2026-09-04T12:00:00Z",
        "credential_provider_type": "sso",
        "effective_permissions_equivalence_sha256": material["sealed_effective_permissions_equivalence"]["sha256"],
        "login_completed_utc": "2026-09-04T12:00:00Z",
        "prior_denial": {
            "causal_trust_condition_mismatch_proven": False,
            "disposition": "PRESERVE_REVIEWED_TRUST_AND_REQUIRE_FRESHNESS_PROPAGATION_AND_PACKED_POLICY_GATE",
            "packed_policy_rejection_percent": 153,
        },
        "role_created_utc": "2026-09-04T12:00:00Z",
        "schema": "aws_c0_gate0_freshness_diagnostic_evidence/v1",
        "source_identity": "konrad",
        "trust_policy_changed": False,
        "zero_science_counters": dict(ZERO_COUNTERS),
    }


def self_test(material: dict[str, Any], equivalence_raw: bytes,
              equivalence_record: dict[str, Any]) -> dict[str, Any]:
    baseline = example_evidence(material)
    result = validate(material, baseline, equivalence_raw, equivalence_record)
    mutations = [
        ("stale-cache", lambda value: value.update({"credential_cache_mtime_utc": "2026-09-04T11:59:59Z"})),
        ("short-wait", lambda value: value.update({"assume_not_before_utc": "2026-09-04T12:03:59Z"})),
        ("trust-change", lambda value: value.update({"trust_policy_changed": True})),
        ("attempt-present", lambda value: value.update({"attempt_state_exists": True})),
        ("policy-change", lambda value: value["candidate_preparation_session_policy"]["Statement"][0].update({"Action": "*"})),
        ("equivalence-identity-change", lambda value: value.update({"effective_permissions_equivalence_sha256": "0" * 64})),
        ("science-counter", lambda value: value["zero_science_counters"].update({"trajectory_count": 1})),
    ]
    rejected: list[str] = []
    for name, mutate in mutations:
        candidate = copy.deepcopy(baseline)
        mutate(candidate)
        try:
            validate(material, candidate, equivalence_raw, equivalence_record)
        except GateError:
            rejected.append(name)
    require(rejected == [name for name, _ in mutations], "negative self-test unexpectedly passed")
    return {**result, "negative_cases_rejected": len(rejected), "self_test": "PASS"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="offline AWS-C0 SSO freshness and diagnostic gate")
    parser.add_argument("--evidence", type=Path)
    parser.add_argument("--equivalence-record", type=Path, required=True)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    require(args.self_test != (args.evidence is not None), "choose exactly one of --self-test or --evidence")
    try:
        material = load_json(MATERIAL)
        equivalence_raw, equivalence_record = load_json_with_bytes(args.equivalence_record)
        result = (self_test(material, equivalence_raw, equivalence_record) if args.self_test else
                  validate(material, load_json(args.evidence), equivalence_raw, equivalence_record))
    except GateError as exc:
        print(f"SSO_FRESHNESS_DIAGNOSTIC_GATE_FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
