"""Local document/identity checks only; imports no project or scientific code."""

import hashlib
import json
from pathlib import Path
import re
import subprocess


BASE = "dfbc3285781de156f41db86933500cccda95bebf"
ROOT = Path(__file__).resolve().parent
ADDITIONS = {
    "ACTC_STATIC_DECISION_DERIVATION_AMENDMENT.md",
    "ACTC_STATIC_DECISION_DERIVATION_VALIDATION.md",
    "actc_static_decision_derivation_check.py",
}


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def require(condition, description):
    if not condition:
        raise ValueError(description)


def pairs(items):
    result = {}
    for key, value in items:
        require(key not in result, "duplicate JSON key: " + key)
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError("nonfinite JSON constant: " + value)


def strict_json(raw):
    return json.loads(raw.decode("utf-8"), object_pairs_hook=pairs,
                      parse_constant=reject_constant)


def main():
    require(git("rev-parse", BASE + "^{tree}").decode().strip() ==
            "3d9a6d3e476239efb74c23a21d2be90070012879", "base tree mismatch")
    paths = git("ls-tree", "-r", "--name-only", "-z", BASE).split(b"\0")
    require(not (ADDITIONS & {p.decode() for p in paths if p}),
            "increment must be additive")
    changed = git("diff", "--name-status", BASE, "--").decode().splitlines()
    for change in changed:
        require(change.startswith("A\t") and change[2:] in ADDITIONS,
                "pre-existing or unexpected tracked change: " + change)
    untracked = git("ls-files", "--others", "--exclude-standard", "-z")
    require({p.decode() for p in untracked.split(b"\0") if p} <= ADDITIONS,
            "unexpected untracked work")
    git("diff", "--check", BASE, "--")

    contract_path = "adaptive_calibration_and_topology_control_contract.json"
    approval_path = "sd01_static_analysis_approval.json"
    contract = strict_json((ROOT / contract_path).read_bytes())
    approval = strict_json((ROOT / approval_path).read_bytes())
    records = contract["source_manifest"] + approval["records"]
    for record in records:
        committed = git("show", record["commit"] + ":" + record["path"])
        current = (ROOT / record["path"]).read_bytes()
        require(current == committed, "source bytes changed: " + record["path"])
        require(len(committed) == record["bytes"], "source byte count mismatch")
        require(hashlib.sha256(committed).hexdigest() == record["sha256"],
                "source hash mismatch")
        if record["path"].endswith(".json"):
            strict_json(committed)
    for path, digest in {
        "ADAPTIVE_CALIBRATION_AND_TOPOLOGY_CONTROL_AUTHORITY.md":
        "6c347858e89a91557391b893f6a64573b4fa9fc8e0c07ee9aac0dec8154e71ff",
        contract_path:
        "546f906a77fedf649dfd5651d3cd5e7fab97588ef0f58d08e1cf01b655b414ef",
    }.items():
        raw = (ROOT / path).read_bytes()
        require(raw == git("show", BASE + ":" + path), "base bytes changed")
        require(hashlib.sha256(raw).hexdigest() == digest, "base hash mismatch")

    require(all(contract[key] is False for key in (
        "execution_authorized", "preregistration_complete", "binding_packet_sealed"
    )), "ACTC boundary changed")
    require(approval["readiness_gap"]["status"] == "OPEN", "SD-01 gap changed")
    require(all(approval[key] is False for key in (
        "scientific_control_tuples_adopted", "scientific_assertion_mapping_adopted",
        "frozen_predicates_changed", "scientific_execution_authorized"
    )), "SD-01 boundary changed")

    amendment = (ROOT / "ACTC_STATIC_DECISION_DERIVATION_AMENDMENT.md").read_text()
    rows = [line for line in amendment.splitlines() if line.startswith("| ACTC-D")]
    decisions = contract["required_preregistration"]
    require(len(rows) == len(decisions) == 25, "decision count mismatch")
    expected_ids = [f"ACTC-D{i:02d}" for i in range(1, 26)]
    require([d["decision_id"] for d in decisions] == expected_ids,
            "decision IDs/order mismatch")
    require(len({d["slot"] for d in decisions}) == 25, "duplicate slot")
    source_ids = {record["source_id"] for record in contract["source_manifest"]}
    for row, decision in zip(rows, decisions):
        cells = [cell.strip() for cell in row.strip("|").split("|")]
        require(len(cells) == 6 and all(cells), "incomplete decision row")
        require(cells[0] == decision["decision_id"] + " / `" + decision["slot"] + "`",
                "row/slot mismatch")
        require(cells[1] == "C", "whole-slot classification mismatch")
        require(decision["value"] is None and decision["status"] == "UNRESOLVED",
                "scientific value or disposition changed")
        require(set(decision["source_refs"]) <= source_ids, "unknown source ref")
    require(re.findall(r"^### (ACTC-PB\d+) — ([AB]):", amendment, re.M) ==
            [("ACTC-PB01", "B"), ("ACTC-PB02", "B"), ("ACTC-PB03", "A")],
            "partial-binding inventory mismatch")
    for path in ADDITIONS:
        raw = (ROOT / path).read_bytes()
        text = raw.decode("utf-8")
        require(raw.endswith(b"\n") and b"\r" not in raw, "invalid line endings")
        require(all(line == line.rstrip() for line in text.splitlines()),
                "trailing whitespace")
        if path.endswith(".md"):
            for target in re.findall(r"\]\(([^)]+)\)", text):
                require((ROOT / target).is_file(), "missing local link: " + target)
    print(json.dumps({
        "disposition": "STATIC_DOCUMENT_CONSISTENCY_PASS",
        "base_commit": BASE,
        "locked_source_and_approval_records_verified": len(records),
        "complete_slot_classifications": {"A": 0, "B": 0, "C": len(rows)},
        "conditional_partial_bindings": {"A": 1, "B": 2},
        "all_preexisting_tracked_files_unchanged": True,
        "preregistration_complete": False,
        "scientific_execution_performed": False,
        "independent_review_performed": False,
    }, indent=2))


if __name__ == "__main__":
    main()
