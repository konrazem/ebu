"""Registered Stage-A executor. Produces the per-event artifacts the frozen
analysis consumes.

Implements sections 6, 8 and 14 of `STAGE_A_PREREGISTRATION.md`.

This module generates data. It draws no conclusion, computes no endpoint and
applies no test: interpretation lives entirely in `stage_a_analysis.py`, whose
behaviour was frozen before any result existed.

Execution is all-or-nothing over the registered replicate set. There is no
interim inspection, no early stopping and no result-dependent exclusion.
"""

from __future__ import annotations

import gzip
import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import stage_a_registry as registry
from gaussian_harness.harness import ARM_CONTROL, ARM_EBU
from gaussian_harness.numerics import Refusal

OUTPUT = Path("results/stage_a/ticks")


def _rational(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _sign(value: Fraction) -> int:
    return (value > 0) - (value < 0)


def serialize_replicate(run, replicate: int, preregistration_sha: str) -> dict:
    """Full post-shock event series plus the shock record for one arm."""
    records = run.records
    shock_record = records[0]
    shock_deviation = shock_record.audit_ledger
    ticks = []
    for record in records[1:]:
        chosen_value = dict(record.ebu_values).get(record.chosen_id)
        ticks.append(
            {
                "t": record.tick,
                "x": [_rational(value) for value in record.state_after],
                "V": _rational(record.audit_potential),
                "B": [_rational(value) for value in record.balances],
                "sumB": _rational(record.balance_total),
                "min_balance": _rational(min(record.balances)),
                "J": _rational(record.audit_ledger),
                "status": record.status,
                "chosen": record.chosen_id,
                "receipts": [[aid, _rational(value)] for aid, value in record.receipts],
                "ebu_sign": _sign(chosen_value) if chosen_value is not None else 0,
                "ebu_value": _rational(chosen_value) if chosen_value is not None else None,
                "n_feasible": len(record.feasible_ids),
                "n_affordable": len(record.affordable_ids),
                "accounting_residual": _rational(record.accounting_residual),
                "conservation_residual": _rational(record.conservation_residual),
                "nonnegativity_residual": _rational(record.nonnegativity_residual),
                "actor_rng_provenance": record.actor_provenance,
            }
        )
    return {
        "protocol_id": registry.PROTOCOL_ID,
        "preregistration_commit": preregistration_sha,
        "replicate": replicate,
        "arm": run.configuration.arm,
        "run_id": run.run_id,
        "code_id": shock_record.code_id,
        "configuration_id": shock_record.configuration_id,
        "configuration_identity": registry.configuration_identity(),
        "forcing_seed": run.forcing_seed,
        "actor_seed": run.actor_seed,
        "horizon": registry.HORIZON,
        "shock": shock_record.forcing,
        "shock_status": shock_record.status,
        "shock_rng_provenance": shock_record.forcing_provenance,
        "D": _rational(shock_deviation),
        "shock_tick": {
            "t": shock_record.tick,
            "x": [_rational(value) for value in shock_record.state_after],
            "V": _rational(shock_record.audit_potential),
            "sumB": _rational(shock_record.balance_total),
            "J": _rational(shock_record.audit_ledger),
        },
        "ticks": ticks,
    }


def execute(limit: int | None = None) -> dict:
    preregistration_sha = subprocess.run(
        ["git", "rev-parse", registry.PROTOCOL_ID_COMMIT_REF],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    registry.assert_registered_code_identity()
    manifest = registry.derive_seed_manifest(preregistration_sha)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    count = registry.REPLICATES if limit is None else limit
    written = 0
    for pair in manifest[:count]:
        for arm in (ARM_EBU, ARM_CONTROL):
            run = registry.run_registered_replicate(arm, pair, preregistration_sha)
            payload = serialize_replicate(run, pair.replicate, preregistration_sha)
            path = OUTPUT / f"replicate_{pair.replicate:03d}_{arm}.json.gz"
            text = json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n"
            # mtime=0 keeps the archive byte-stable for a given payload.
            path.write_bytes(gzip.compress(text.encode("utf-8"), mtime=0))
            written += 1
            del run
        if (pair.replicate + 1) % 16 == 0:
            print(f"  ... {pair.replicate + 1}/{count} replicates", flush=True)
    return {
        "preregistration_commit": preregistration_sha,
        "replicates": count,
        "files_written": written,
    }


if __name__ == "__main__":
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
    summary = execute(limit)
    print(json.dumps(summary, indent=2))
