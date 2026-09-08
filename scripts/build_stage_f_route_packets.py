#!/usr/bin/env python3
"""Build outcome-blind Stage F route packets from committed authority gaps."""
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


def committed_bytes(name: str, revision: str = "HEAD") -> bytes:
    result = subprocess.run(["git", "show", f"{revision}:{name}"], cwd=ROOT, capture_output=True, check=False)
    if result.returncode:
        raise ValueError(f"committed authority unavailable: {revision}:{name}")
    working = (ROOT / name).read_bytes()
    if working != result.stdout:
        raise ValueError(f"working authority differs from committed bytes: {name}")
    return result.stdout


def load(name: str, revision: str = "HEAD") -> dict[str, Any]:
    return json.loads(committed_bytes(name, revision))


def build(output_dir: Path) -> dict[str, Any]:
    registry = load("stage_f_route_registry.json")
    contract = load("stage_f_route_level_binding_correction_contract.json")
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
    packets = []
    for route in registry["routes"]:
        packet = {
            "schema": "sealed_route_packet/v1", "route_id": route["route_id"],
            "authority_gaps": route["gap_ids"], "disposition": "BLOCKED_AUTHORITY_GAP",
            "frozen_packet": False, "deterministic_validation": "NOT_RUN_AUTHORITY_GAP",
            "independent_binding_status": "NOT_REQUESTED_AUTHORITY_GAP",
            "route_cost_cap": None, "result_s3_layout": None,
            "protocol_execution_permission": False, "execution_permitted": False,
        }
        packet["packet_sha256"] = digest(packet)
        packets.append(packet)
        (output_dir / f"{route['route_id']}.packet.json").write_bytes(canonical_bytes(packet))
    sources = {name: "sha256:" + hashlib.sha256(committed_bytes(name)).hexdigest() for name in (
        "stage_f_route_registry.json", "stage_f_route_level_binding_correction_contract.json")}
    sources["stage_f_local_execution_binding_contract.json"] = "sha256:" + hashlib.sha256(
        committed_bytes("stage_f_local_execution_binding_contract.json", contract["required_target_commit"])).hexdigest()
    ledger = {"schema": "programme_ledger/v1", "registry_sha256": digest(registry), "authority_source_sha256": sources, "routes": packets,
              "completed_routes": [], "blocked_routes": [{"route_id": p["route_id"], "gap_ids": p["authority_gaps"]} for p in packets],
              "costs": {"currency": "USD", "incurred": "0", "reason": "no route sealed or executed"},
              "next_route": None, "next_required_action": "supply exact missing authority for SD-01"}
    ledger["ledger_sha256"] = digest(ledger)
    (output_dir / "programme_ledger.json").write_bytes(canonical_bytes(ledger))
    return ledger


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    ledger = build(args.output_dir)
    print(json.dumps({"status": "STAGE_F_ROUTE_PACKETS_BUILT", "ledger_sha256": ledger["ledger_sha256"], "blocked": len(ledger["blocked_routes"])}, sort_keys=True))


if __name__ == "__main__":
    main()
