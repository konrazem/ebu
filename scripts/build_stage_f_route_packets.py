#!/usr/bin/env python3
"""Build outcome-blind Stage F route packets from committed authority gaps.

This builder never imports a runner or resolves an execution environment.  Its
only output is either a route packet with an inherited authority gap or (when
future authority permits it) a packet shape which a later, separately
authorized sealer can complete.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BASE_AUTHORITY_REVISION = "d5597153bdd65ea2eff1ab31ed8f27807bb2e915"
SEAL_REQUIREMENTS = (
    "zero_inherited_authority_gaps",
    "frozen_route_packet",
    "deterministic_validation_pass",
    "independent_binding_pass",
    "hard_route_cost_cap",
    "result_s3_layout",
    "protocol_execution_permission",
)
EXECUTION_BINDINGS = (
    "code_identity",
    "input_identities",
    "compute_and_cost_cap",
    "result_path",
    "rng",
    "checkpoint_and_recovery",
    "controls",
    "output_and_evidence_requirements",
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def committed_bytes(name: str, revision: str = "HEAD") -> bytes:
    result = subprocess.run(["git", "show", f"{revision}:{name}"], cwd=ROOT, capture_output=True, check=False)
    if result.returncode:
        raise ValueError(f"committed authority unavailable: {revision}:{name}")
    working = (ROOT / name).read_bytes()
    if working != result.stdout:
        raise ValueError(f"working authority differs from committed bytes: {name}")
    return result.stdout


def immutable_commit(revision: str) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--verify", f"{revision}^{{commit}}"],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    resolved = result.stdout.strip()
    if result.returncode or not re.fullmatch(r"[0-9a-f]{40}", resolved):
        raise ValueError(f"authority revision is not an immutable commit: {revision}")
    return resolved


def load(name: str, revision: str = "HEAD") -> dict[str, Any]:
    return json.loads(committed_bytes(name, revision))


def source_identity(name: str, revision: str) -> dict[str, str]:
    return {
        "path": name,
        "revision": revision,
        "sha256": "sha256:" + hashlib.sha256(committed_bytes(name, revision)).hexdigest(),
    }


def not_sealable_receipt(
    route: dict[str, Any], index: int, inherited_revision: str, inherited_source: dict[str, str],
) -> dict[str, Any]:
    """Return a compact, source-addressed receipt without inventing a file."""
    receipt = {
        "schema": "route_not_sealable_receipt/v1",
        "route_id": route["route_id"],
        "disposition": "NOT_SEALABLE",
        "inherited_gap_source": {
            **inherited_source,
            "json_pointer": f"/accepted_base_readiness/gap_registry/{index}",
        },
        "missing_authorities": [
            {
                "gap_id": gap_id,
                "gap_class": route["gap_class"],
                "committed_file": None,
                "authority_revision": inherited_revision,
                "reason": "The committed gap registry names this missing authority but supplies no derivable authority file.",
            }
            for gap_id in route["gap_ids"]
        ],
        "predecessor_routes": route["predecessors"],
        "execution_prohibited": True,
    }
    receipt["receipt_sha256"] = digest(receipt)
    return receipt


def build(output_dir: Path, authority_revision: str = BASE_AUTHORITY_REVISION) -> dict[str, Any]:
    authority_revision = immutable_commit(authority_revision)
    registry = load("stage_f_route_registry.json", authority_revision)
    contract = load("stage_f_route_level_binding_correction_contract.json", authority_revision)
    inherited = load("stage_f_local_execution_binding_contract.json", contract["required_target_commit"])
    expected_gaps = inherited["accepted_base_readiness"]["gap_registry"]
    if registry["routes"] != [
        {**row, "ordinal": index + 1, "parent_route_id": "SD-01" if row["route_id"] == "SD-01-GROWTH-v1" else None,
         "predecessors": (["SD-01"] if row["route_id"] == "SD-01-GROWTH-v1" else (contract["last_route"]["must_follow_accepted_dispositions"] if row["route_id"] == "SD-14" else []))}
        for index, row in enumerate(expected_gaps)
    ]:
        raise ValueError("registry does not exactly reconstruct inherited route gaps")
    if [row["route_id"] for row in registry["routes"]] != contract["campaign_order"]:
        raise ValueError("registry route order differs from correction contract")

    output_dir.mkdir(parents=True, exist_ok=True)
    if any(output_dir.iterdir()):
        raise ValueError("output directory must be empty")
    authority_sources = {
        "stage_f_route_registry.json": source_identity("stage_f_route_registry.json", authority_revision),
        "stage_f_route_level_binding_correction_contract.json": source_identity(
            "stage_f_route_level_binding_correction_contract.json", authority_revision),
        "stage_f_local_execution_binding_contract.json": source_identity(
            "stage_f_local_execution_binding_contract.json", contract["required_target_commit"]),
    }
    packets = []
    for index, route in enumerate(registry["routes"]):
        receipt = not_sealable_receipt(
            route, index, contract["required_target_commit"],
            authority_sources["stage_f_local_execution_binding_contract.json"],
        )
        packet = {
            "schema": "sealed_route_packet/v1", "route_id": route["route_id"],
            "authority_gaps": route["gap_ids"], "disposition": "BLOCKED_AUTHORITY_GAP",
            "frozen_packet": False, "deterministic_validation": "NOT_RUN_AUTHORITY_GAP",
            "independent_binding_status": "NOT_REQUESTED_AUTHORITY_GAP",
            "route_cost_cap": None, "result_s3_layout": None,
            "protocol_execution_permission": False, "execution_permitted": False,
            "authority_provenance": {
                "registry": authority_sources["stage_f_route_registry.json"],
                "route_level_contract": authority_sources["stage_f_route_level_binding_correction_contract.json"],
                "inherited_gap_registry": receipt["inherited_gap_source"],
            },
            "not_sealable_receipt": receipt,
            "seal_requirement_status": {requirement: "MISSING_AUTHORITY_GAP" for requirement in SEAL_REQUIREMENTS},
            "execution_bindings": {binding: None for binding in EXECUTION_BINDINGS},
            "dependency_status": "BLOCKED_BY_PREDECESSOR_DISPOSITIONS" if route["predecessors"] else "NO_ROUTE_PREDECESSOR",
        }
        packet["packet_sha256"] = digest(packet)
        packets.append(packet)
        (output_dir / f"{route['route_id']}.packet.json").write_bytes(canonical_bytes(packet))
    sources = {name: source["sha256"] for name, source in authority_sources.items()}
    ledger = {"schema": "programme_ledger/v1", "authority_revision": authority_revision, "registry_sha256": digest(registry), "authority_source_sha256": sources, "authority_sources": authority_sources, "routes": packets,
              "completed_routes": [], "blocked_routes": [{"route_id": p["route_id"], "gap_ids": p["authority_gaps"]} for p in packets],
              "costs": {"currency": "USD", "incurred": "0", "reason": "no route sealed or executed"},
              "next_route": None, "first_execution_candidate": None,
              "candidate_evaluation_order": [route["route_id"] for route in registry["routes"]],
              "next_required_action": "supply exact missing authority for SD-01"}
    ledger["ledger_sha256"] = digest(ledger)
    (output_dir / "programme_ledger.json").write_bytes(canonical_bytes(ledger))
    return ledger


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--authority-revision", default=BASE_AUTHORITY_REVISION)
    args = parser.parse_args()
    ledger = build(args.output_dir, args.authority_revision)
    print(json.dumps({"status": "STAGE_F_ROUTE_PACKETS_BUILT", "ledger_sha256": ledger["ledger_sha256"], "blocked": len(ledger["blocked_routes"])}, sort_keys=True))


if __name__ == "__main__":
    main()
