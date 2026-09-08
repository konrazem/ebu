#!/usr/bin/env python3
"""Validate only deterministic, non-executable Stage F route packet evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def verify_digest(record: dict[str, Any], field: str) -> None:
    actual = record.pop(field)
    try:
        if actual != digest(record): raise ValueError(f"invalid {field}")
    finally:
        record[field] = actual


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw)
    if raw != canonical_bytes(value):
        raise ValueError(f"noncanonical evidence: {path.name}")
    return value


def committed_bytes(name: str, revision: str = "HEAD") -> bytes:
    result = subprocess.run(["git", "show", f"{revision}:{name}"], cwd=ROOT, capture_output=True, check=False)
    if result.returncode:
        raise ValueError(f"committed authority unavailable: {revision}:{name}")
    working = (ROOT / name).read_bytes()
    if working != result.stdout:
        raise ValueError(f"working authority differs from committed bytes: {name}")
    return result.stdout


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--evidence-dir", type=Path, required=True); args = parser.parse_args()
    ledger = load_canonical(args.evidence_dir / "programme_ledger.json")
    verify_digest(ledger, "ledger_sha256")
    routes = ledger["routes"]
    contract = json.loads(committed_bytes("stage_f_route_level_binding_correction_contract.json"))
    registry = json.loads(committed_bytes("stage_f_route_registry.json"))
    inherited_bytes = committed_bytes("stage_f_local_execution_binding_contract.json", contract["required_target_commit"])
    inherited = json.loads(inherited_bytes)
    expected = inherited["accepted_base_readiness"]["gap_registry"]
    source_hashes = {"stage_f_route_registry.json": "sha256:" + hashlib.sha256(committed_bytes("stage_f_route_registry.json")).hexdigest(),
                     "stage_f_route_level_binding_correction_contract.json": "sha256:" + hashlib.sha256(committed_bytes("stage_f_route_level_binding_correction_contract.json")).hexdigest(),
                     "stage_f_local_execution_binding_contract.json": "sha256:" + hashlib.sha256(inherited_bytes).hexdigest()}
    if ledger["schema"] != "programme_ledger/v1" or ledger["authority_source_sha256"] != source_hashes:
        raise ValueError("ledger schema or committed-authority provenance invalid")
    if registry["schema"] != "route_registry/v1" or registry["source_commit"] != contract["required_target_commit"]:
        raise ValueError("registry provenance invalid")
    if [row["route_id"] for row in registry["routes"]] != contract["campaign_order"] or len(routes) != 15 or ledger["completed_routes"] or ledger["costs"]["incurred"] != "0": raise ValueError("ledger completion, order, or cost claim invalid")
    if registry["routes"][1]["parent_route_id"] != contract["nested_route"]["parent_study_id"] or registry["routes"][1]["predecessors"] != ["SD-01"] or registry["routes"][-1]["predecessors"] != contract["last_route"]["must_follow_accepted_dispositions"]:
        raise ValueError("nested or final-route dependency invalid")
    if ledger["registry_sha256"] != digest(registry):
        raise ValueError("registry identity mismatch")
    for packet, gap in zip(routes, expected, strict=True):
        verify_digest(packet, "packet_sha256")
        if packet["schema"] != "sealed_route_packet/v1" or packet["frozen_packet"] or packet["deterministic_validation"] != "NOT_RUN_AUTHORITY_GAP" or packet["independent_binding_status"] != "NOT_REQUESTED_AUTHORITY_GAP" or packet["protocol_execution_permission"]:
            raise ValueError("packet schema or unsealed state invalid")
        if packet["route_id"] != gap["route_id"] or packet["authority_gaps"] != gap["gap_ids"]:
            raise ValueError("packet does not reproduce inherited authority gap")
        if load_canonical(args.evidence_dir / f"{packet['route_id']}.packet.json") != packet:
            raise ValueError("packet file differs from ledger projection")
        if packet["disposition"] != "BLOCKED_AUTHORITY_GAP" or not packet["authority_gaps"] or packet["execution_permitted"]: raise ValueError("route is not safely blocked")
        if packet["route_cost_cap"] is not None or packet["result_s3_layout"] is not None: raise ValueError("unsealed route carries launch material")
    expected_blocked = [{"route_id": packet["route_id"], "gap_ids": packet["authority_gaps"]} for packet in routes]
    if ledger["blocked_routes"] != expected_blocked or ledger["next_route"] is not None or ledger["next_required_action"] != "supply exact missing authority for SD-01":
        raise ValueError("ledger route projection or next-action claim invalid")
    print(json.dumps({"status": "STAGE_F_ROUTE_LEVEL_BINDING_VALIDATION_PASS", "routes": len(routes), "scientific_execution_count": 0}, sort_keys=True))


if __name__ == "__main__": main()
