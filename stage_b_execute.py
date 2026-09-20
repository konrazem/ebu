"""Registered Stage-B executor. Generates data only; draws no conclusion.

Implements sections 4, 5 and 17 of `STAGE_B_PREREGISTRATION.md`. Interpretation
lives entirely in `stage_b_analysis.py`, frozen before any result existed.

Execution is all-or-nothing over the registered replicate set: no interim
inspection, no early stopping, no result-dependent exclusion.
"""

from __future__ import annotations

import gzip
import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import stage_b_registry as registry
from gaussian_harness.harness import ARM_CONTROL, ARM_EBU

OUTPUT = Path("results/stage_b/ticks")


def _rational(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def serialize(result: dict, replicate: int, arm: str, pair, preregistration_sha: str) -> dict:
    columns = result["columns"]
    encoded = {}
    for key, values in columns.items():
        if key in ("status", "raw_forcing", "applied", "null_forcing",
                   "n_feasible", "n_affordable", "n_rejected", "ebu_sign"):
            encoded[key] = values
        else:
            encoded[key] = [_rational(value) for value in values]
    return {
        "protocol_id": registry.PROTOCOL_ID,
        "preregistration_commit": preregistration_sha,
        "replicate": replicate,
        "arm": arm,
        "run_id": result["run_id"],
        "code_id": registry.REGISTERED_CODE_IDENTITY,
        "configuration_id": registry.CONFIGURATION_ID,
        "configuration_identity": registry.configuration_identity(),
        "forcing_seed": pair.forcing_seed,
        "actor_seed": pair.actor_seed,
        "horizon": registry.HORIZON,
        "burn_in": registry.BURN_IN,
        "block": registry.BLOCK,
        "v_max": _rational(registry.V_MAX),
        "forcing_quantum": _rational(registry.FORCING_QUANTUM),
        "balances_end": [_rational(value) for value in result["balances_end"]],
        "max_accounting_residual": _rational(result["max_accounting_residual"]),
        "max_conservation_residual": _rational(result["max_conservation_residual"]),
        "max_nonnegativity_residual": _rational(result["max_nonnegativity_residual"]),
        "negative_capacity_ticks": result["negative_capacity_ticks"],
        "columns": encoded,
    }


def execute(limit: int | None = None) -> dict:
    preregistration_sha = subprocess.run(
        ["git", "rev-parse", registry.PREREGISTRATION_REF],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    registry.assert_registered_code_identity()
    if registry.exact_v_max() != registry.V_MAX:
        raise RuntimeError("V_max drifted from the frozen constant")
    manifest = registry.derive_seed_manifest(preregistration_sha)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    count = registry.REPLICATES if limit is None else limit
    written = 0
    for pair in manifest[:count]:
        for arm in (ARM_EBU, ARM_CONTROL):
            result = registry.run_registered_replicate(arm, pair, preregistration_sha)
            payload = serialize(result, pair.replicate, arm, pair, preregistration_sha)
            path = OUTPUT / f"replicate_{pair.replicate:03d}_{arm}.json.gz"
            text = json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n"
            path.write_bytes(gzip.compress(text.encode("utf-8"), mtime=0))
            written += 1
            del result
        print(f"  replicate {pair.replicate + 1}/{count} complete", flush=True)
    return {"preregistration_commit": preregistration_sha,
            "replicates": count, "files_written": written}


if __name__ == "__main__":
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
    print(json.dumps(execute(limit), indent=2))
