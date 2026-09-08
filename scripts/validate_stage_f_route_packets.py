#!/usr/bin/env python3
"""Validate only deterministic, non-executable Stage F route packet evidence."""
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
    "zero_inherited_authority_gaps", "frozen_route_packet", "deterministic_validation_pass",
    "independent_binding_pass", "hard_route_cost_cap", "result_s3_layout", "protocol_execution_permission",
)
EXECUTION_BINDINGS = (
    "code_identity", "input_identities", "compute_and_cost_cap", "result_path", "rng",
    "checkpoint_and_recovery", "controls", "output_and_evidence_requirements",
)


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


def immutable_commit(revision: str) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--verify", f"{revision}^{{commit}}"],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    resolved = result.stdout.strip()
    if result.returncode or not re.fullmatch(r"[0-9a-f]{40}", resolved):
        raise ValueError(f"authority revision is not an immutable commit: {revision}")
    return resolved


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--evidence-dir", type=Path, required=True); parser.add_argument("--authority-revision", default=BASE_AUTHORITY_REVISION); args = parser.parse_args()
    authority_revision = immutable_commit(args.authority_revision)
    ledger = load_canonical(args.evidence_dir / "programme_ledger.json")
    verify_digest(ledger, "ledger_sha256")
    routes = ledger["routes"]
    contract = json.loads(committed_bytes("stage_f_route_level_binding_correction_contract.json", authority_revision))
    registry = json.loads(committed_bytes("stage_f_route_registry.json", authority_revision))
    inherited_bytes = committed_bytes("stage_f_local_execution_binding_contract.json", contract["required_target_commit"])
    inherited = json.loads(inherited_bytes)
    expected = inherited["accepted_base_readiness"]["gap_registry"]
    source_hashes = {"stage_f_route_registry.json": "sha256:" + hashlib.sha256(committed_bytes("stage_f_route_registry.json", authority_revision)).hexdigest(),
                     "stage_f_route_level_binding_correction_contract.json": "sha256:" + hashlib.sha256(committed_bytes("stage_f_route_level_binding_correction_contract.json", authority_revision)).hexdigest(),
                     "stage_f_local_execution_binding_contract.json": "sha256:" + hashlib.sha256(inherited_bytes).hexdigest()}
    if ledger["schema"] != "programme_ledger/v1" or ledger["authority_revision"] != authority_revision or ledger["authority_source_sha256"] != source_hashes:
        raise ValueError("ledger schema or committed-authority provenance invalid")
    expected_sources = {
        name: {"path": name, "revision": revision, "sha256": source_hashes[name]}
        for name, revision in (("stage_f_route_registry.json", authority_revision),
                               ("stage_f_route_level_binding_correction_contract.json", authority_revision),
                               ("stage_f_local_execution_binding_contract.json", contract["required_target_commit"]))
    }
    if ledger["authority_sources"] != expected_sources:
        raise ValueError("ledger detailed committed-authority provenance invalid")
    if registry["schema"] != "route_registry/v1" or registry["source_commit"] != contract["required_target_commit"]:
        raise ValueError("registry provenance invalid")
    if [row["route_id"] for row in registry["routes"]] != contract["campaign_order"] or len(routes) != 15 or ledger["completed_routes"] or ledger["costs"]["incurred"] != "0": raise ValueError("ledger completion, order, or cost claim invalid")
    if registry["routes"][1]["parent_route_id"] != contract["nested_route"]["parent_study_id"] or registry["routes"][1]["predecessors"] != ["SD-01"] or registry["routes"][-1]["predecessors"] != contract["last_route"]["must_follow_accepted_dispositions"]:
        raise ValueError("nested or final-route dependency invalid")
    if ledger["registry_sha256"] != digest(registry):
        raise ValueError("registry identity mismatch")
    for index, (packet, gap) in enumerate(zip(routes, expected, strict=True)):
        verify_digest(packet, "packet_sha256")
        if packet["schema"] != "sealed_route_packet/v1" or packet["frozen_packet"] or packet["deterministic_validation"] != "NOT_RUN_AUTHORITY_GAP" or packet["independent_binding_status"] != "NOT_REQUESTED_AUTHORITY_GAP" or packet["protocol_execution_permission"]:
            raise ValueError("packet schema or unsealed state invalid")
        if packet["route_id"] != gap["route_id"] or packet["authority_gaps"] != gap["gap_ids"]:
            raise ValueError("packet does not reproduce inherited authority gap")
        if load_canonical(args.evidence_dir / f"{packet['route_id']}.packet.json") != packet:
            raise ValueError("packet file differs from ledger projection")
        if packet["disposition"] != "BLOCKED_AUTHORITY_GAP" or not packet["authority_gaps"] or packet["execution_permitted"]: raise ValueError("route is not safely blocked")
        if packet["route_cost_cap"] is not None or packet["result_s3_layout"] is not None: raise ValueError("unsealed route carries launch material")
        receipt = packet["not_sealable_receipt"].copy()
        verify_digest(receipt, "receipt_sha256")
        if receipt["schema"] != "route_not_sealable_receipt/v1" or receipt["route_id"] != packet["route_id"] or receipt["disposition"] != "NOT_SEALABLE" or not receipt["execution_prohibited"]:
            raise ValueError("not-sealable receipt identity or prohibition invalid")
        expected_source = {**expected_sources["stage_f_local_execution_binding_contract.json"], "json_pointer": f"/accepted_base_readiness/gap_registry/{index}"}
        if receipt["inherited_gap_source"] != expected_source or receipt["predecessor_routes"] != registry["routes"][index]["predecessors"]:
            raise ValueError("not-sealable receipt provenance or dependency invalid")
        expected_missing = [{"gap_id": gap_id, "gap_class": registry["routes"][index]["gap_class"], "committed_file": None,
                             "authority_revision": contract["required_target_commit"],
                             "reason": "The committed gap registry names this missing authority but supplies no derivable authority file."}
                            for gap_id in packet["authority_gaps"]]
        if receipt["missing_authorities"] != expected_missing:
            raise ValueError("not-sealable receipt does not state the exact committed authority gap")
        expected_provenance = {"registry": expected_sources["stage_f_route_registry.json"],
                               "route_level_contract": expected_sources["stage_f_route_level_binding_correction_contract.json"],
                               "inherited_gap_registry": expected_source}
        if packet["authority_provenance"] != expected_provenance:
            raise ValueError("packet authority provenance invalid")
        if packet["seal_requirement_status"] != {requirement: "MISSING_AUTHORITY_GAP" for requirement in SEAL_REQUIREMENTS}:
            raise ValueError("packet seal prerequisite state invalid")
        if packet["execution_bindings"] != {binding: None for binding in EXECUTION_BINDINGS}:
            raise ValueError("unsealed packet carries execution bindings")
        expected_dependency = "BLOCKED_BY_PREDECESSOR_DISPOSITIONS" if registry["routes"][index]["predecessors"] else "NO_ROUTE_PREDECESSOR"
        if packet["dependency_status"] != expected_dependency:
            raise ValueError("packet dependency status invalid")
    expected_blocked = [{"route_id": packet["route_id"], "gap_ids": packet["authority_gaps"]} for packet in routes]
    if ledger["blocked_routes"] != expected_blocked or ledger["next_route"] is not None or ledger["first_execution_candidate"] is not None or ledger["candidate_evaluation_order"] != contract["campaign_order"] or ledger["next_required_action"] != "supply exact missing authority for SD-01":
        raise ValueError("ledger route projection or next-action claim invalid")
    expected_names = {"programme_ledger.json", *[f"{packet['route_id']}.packet.json" for packet in routes]}
    if {path.name for path in args.evidence_dir.iterdir()} != expected_names:
        raise ValueError("evidence directory has missing or extra files")
    print(json.dumps({"status": "STAGE_F_ROUTE_LEVEL_BINDING_VALIDATION_PASS", "routes": len(routes), "scientific_execution_count": 0}, sort_keys=True))


if __name__ == "__main__": main()
