"""Closed Stage E evidence-record construction and manifest binding."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Iterable

from .canonical import Refusal, canonical_bytes, canonical_digest, sha256_bytes


SCIENTIFIC_ZERO_COUNTERS = {
    "registered_configuration_count": 0,
    "registered_study_run_count": 0,
    "model_state_advance_count": 0,
    "trajectory_count": 0,
    "simulation_count": 0,
    "gate_execution_count": 0,
    "registered_transform_count": 0,
    "scientific_outcome_inspection_count": 0,
    "scientific_result_count": 0,
    "figure_count": 0,
    "book_count": 0,
}

RELEASE_ZERO_COUNTERS = {
    "main_merge_count": 0,
    "tag_count": 0,
    "release_count": 0,
    "upload_count": 0,
    "package_index_count": 0,
    "publication_count": 0,
}

EVIDENCE_ORDER = [
    "authority.json",
    "schema.json",
    "identity-continuation.json",
    "mobius.json",
    "dag-cache.json",
    "adapter-guard.json",
    "installed-isolation.json",
    "complexity.json",
    "regression.json",
]


def common_record(
    *,
    record_type: str,
    status: str,
    evidence_class: str,
    head_commit: str,
    head_tree: str,
    environment: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "record_type": record_type,
        "status": status,
        "evidence_class": evidence_class,
        "head_commit": head_commit,
        "head_tree": head_tree,
        "environment": deepcopy(environment),
        "scientific_counters": deepcopy(SCIENTIFIC_ZERO_COUNTERS),
        "release_counters": deepcopy(RELEASE_ZERO_COUNTERS),
    }


def seal_record(record: dict[str, Any], *, path: str) -> tuple[bytes, dict[str, Any]]:
    data = canonical_bytes(record)
    digest = sha256_bytes(data)
    return data, {
        "identity": {"path": path, "byte_count": len(data), "sha256": digest},
        "status": record["status"],
        "evidence_class": record["evidence_class"],
    }


def write_record(directory: str | Path, name: str, record: dict[str, Any]) -> dict[str, Any]:
    if name not in EVIDENCE_ORDER:
        raise Refusal(f"unknown evidence record: {name}")
    output = Path(directory) / name
    output.parent.mkdir(parents=True, exist_ok=True)
    data, entry = seal_record(record, path=name)
    output.write_bytes(data)
    return {"name": name, **entry}


def assert_zero_boundaries(record: dict[str, Any]) -> None:
    if record.get("scientific_counters") != SCIENTIFIC_ZERO_COUNTERS:
        raise Refusal("scientific counter boundary drift")
    if record.get("release_counters") != RELEASE_ZERO_COUNTERS:
        raise Refusal("release counter boundary drift")


def build_final_manifest(
    records: Iterable[tuple[str, dict[str, Any]]],
    *,
    head_commit: str,
    head_tree: str,
    environment: dict[str, Any],
    completed_lanes: list[str],
) -> dict[str, Any]:
    ordered = list(records)
    if [name for name, _ in ordered] != EVIDENCE_ORDER:
        raise Refusal("final manifest evidence order mismatch")
    entries: list[dict[str, Any]] = []
    for name, record in ordered:
        assert_zero_boundaries(record)
        if record.get("head_commit") != head_commit or record.get("head_tree") != head_tree:
            raise Refusal("cross-coordinate evidence record")
        if record.get("environment") != environment:
            raise Refusal("cross-environment evidence record")
        if record.get("status") != "PASS":
            raise Refusal("non-PASS evidence cannot be promoted")
        _, sealed = seal_record(record, path=name)
        entries.append({"name": name, **sealed})
    expected_lanes = [
        "SE-AUTH",
        "SE-SCHEMA",
        "SE-ID-CONT",
        "SE-MOBIUS",
        "SE-DAG-CACHE",
        "SE-ADAPTER-GUARD",
        "SE-INSTALL",
        "SE-REGRESSION",
    ]
    if completed_lanes != expected_lanes:
        raise Refusal("validation lane closure mismatch")
    manifest = common_record(
        record_type="FINAL_MANIFEST",
        status="STAGE_E_SCIENTIFIC_HARNESS_VALIDATION_PASS",
        evidence_class="STATIC_OR_SYNTHETIC_IMPLEMENTATION_TEST",
        head_commit=head_commit,
        head_tree=head_tree,
        environment=environment,
    )
    manifest.update(
        {
            "records": entries,
            "record_count": 9,
            "all_required_lanes_completed": True,
            "bound_supported": True,
            "stage_f_execution_authorized": False,
        }
    )
    return manifest


def read_canonical_record(path: str | Path) -> dict[str, Any]:
    from .canonical import strict_loads

    data = Path(path).read_bytes()
    value = strict_loads(data)
    if canonical_bytes(value) != data:
        raise Refusal(f"noncanonical evidence record: {path}")
    if not isinstance(value, dict):
        raise Refusal("evidence record must be an object")
    return value
