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
    assert "scientific_execution_count\": 0" in result.stdout
