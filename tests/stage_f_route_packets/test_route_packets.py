import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_registry_builds_only_blocked_packets(tmp_path):
    output = tmp_path / "evidence"
    subprocess.run([sys.executable, "scripts/build_stage_f_route_packets.py", "--output-dir", str(output)], cwd=ROOT, check=True)
    result = subprocess.run([sys.executable, "scripts/validate_stage_f_route_packets.py", "--evidence-dir", str(output)], cwd=ROOT, check=True, text=True, capture_output=True)
    ledger = json.loads((output / "programme_ledger.json").read_text())
    assert len(ledger["blocked_routes"]) == 15
    assert ledger["completed_routes"] == []
    assert ledger["next_required_action"] == "supply exact missing authority for SD-01"
    assert ledger["first_execution_candidate"] is None
    assert ledger["candidate_evaluation_order"][:2] == ["SD-01", "SD-01-GROWTH-v1"]
    sd01 = json.loads((output / "SD-01.packet.json").read_text())
    assert sd01["not_sealable_receipt"]["missing_authorities"][0]["gap_id"] == "STAGE_F_SD01_ADAPTER_AND_RUN_ID_CLOSURE"
    assert sd01["execution_bindings"] == {
        "code_identity": None, "input_identities": None, "compute_and_cost_cap": None,
        "result_path": None, "rng": None, "checkpoint_and_recovery": None,
        "controls": None, "output_and_evidence_requirements": None,
    }
    sd14 = json.loads((output / "SD-14.packet.json").read_text())
    assert sd14["dependency_status"] == "BLOCKED_BY_PREDECESSOR_DISPOSITIONS"
    assert "scientific_execution_count\": 0" in result.stdout
