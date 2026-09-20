"""Registered homeostasis executor. Generates data only; draws no conclusion.

Implements section 10 of `HOMEOSTASIS_STUDY_PREREGISTRATION.md`. Interpretation
lives entirely in `homeostasis_analysis.py`, frozen before any result existed.

Execution is all-or-nothing over the registered job set: no interim inspection,
no early stopping, no result-dependent exclusion.

Jobs are executed in parallel. That is safe by construction rather than by
hope: every payload is a pure function of its job identity, and the conformance
suite asserts that reversed execution order and a different executor, host,
attempt and start time leave every payload hash unchanged. Scheduling order
cannot influence results.
"""

from __future__ import annotations

import gzip
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import homeostasis_registry as registry
from homeostasis.harness import rehearsal_budget
from homeostasis.jobs import ExecutionEnvelope, JobIdentity, run_job

OUTPUT = Path("results/homeostasis")
JOBS = OUTPUT / "jobs"


def _artifact_path(job: JobIdentity) -> Path:
    return JOBS / f"{job.job_id[:24]}.json.gz"


def execute_one(job: JobIdentity, attempt: int = 0) -> dict:
    """Run one registered job and write its immutable artifact."""
    from gaussian_harness.harness import TickBudget
    budget = TickBudget.registered_study(job.horizon, job.preregistration_id)
    result = run_job(
        job,
        list(registry.REFERENCE), list(registry.SCALES), list(registry.QUANTA),
        registry.STUDY_ID, registry.CONFIGURATION_ID,
        envelope=ExecutionEnvelope("local-parallel", attempt),
        budget=budget,
    )
    document = result.envelope_document()
    text = json.dumps(document, sort_keys=True, separators=(",", ":")) + "\n"
    _artifact_path(job).write_bytes(gzip.compress(text.encode("utf-8"), mtime=0))
    return {
        "job_id": job.job_id,
        "payload_sha256": result.payload_hash,
        "menu_rule": job.menu_rule,
        "load_id": job.load_id,
        "policy_id": job.policy_id,
        "replicate": job.replicate,
        "max_accounting_residual": result.payload["max_accounting_residual"],
        "max_conservation_residual": result.payload["max_conservation_residual"],
        "max_nonnegativity_residual": result.payload["max_nonnegativity_residual"],
    }


def _worker(job: JobIdentity) -> dict:
    return execute_one(job)


def execute(workers: int | None = None) -> dict:
    preregistration_sha = subprocess.run(
        ["git", "rev-parse", registry.PREREGISTRATION_REF],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    code, gaussian = registry.assert_registered_identities()
    configuration = registry.configuration_identity()

    jobs = registry.job_set(preregistration_sha)
    JOBS.mkdir(parents=True, exist_ok=True)

    seeds = registry.derive_seed_manifest(preregistration_sha)
    (OUTPUT / "SEED_MANIFEST.json").write_text(json.dumps({
        "protocol_id": registry.PROTOCOL_ID,
        "preregistration_commit": preregistration_sha,
        "load_in_preimage": False,
        "preimage_rule": "EBU-HOMEOSTASIS-v1|<commit>|<replicate:03d>|<STREAM>",
        "seeds": [
            {"replicate": p.replicate, "forcing_seed": p.forcing_seed,
             "actor_seed": p.actor_seed} for p in seeds
        ],
    }, indent=2) + "\n")

    count = workers or max(1, (os.cpu_count() or 4) - 2)
    started = time.time()
    rows: list[dict] = []
    with ProcessPoolExecutor(max_workers=count) as pool:
        futures = {pool.submit(_worker, job): job for job in jobs}
        for done, future in enumerate(as_completed(futures), start=1):
            rows.append(future.result())
            if done % 64 == 0 or done == len(jobs):
                rate = done / (time.time() - started)
                remaining = (len(jobs) - done) / rate if rate else 0
                print(f"  {done}/{len(jobs)} jobs  ({remaining/60:.1f} min left)", flush=True)
    wall = time.time() - started

    rows.sort(key=lambda row: row["job_id"])
    manifest = {
        "protocol_id": registry.PROTOCOL_ID,
        "preregistration_commit": preregistration_sha,
        "configuration_identity": configuration,
        "homeostasis_code_identity": code,
        "gaussian_code_identity": gaussian,
        "jobs_expected": len(jobs),
        "jobs_written": len(rows),
        "wall_seconds": round(wall, 1),
        "workers": count,
        "ticks": len(jobs) * registry.HORIZON,
        "rows": rows,
    }
    (OUTPUT / "EXECUTION_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(f"\n{len(rows)} jobs in {wall/60:.1f} min on {count} workers")
    worst = {key: max(row[key] for row in rows) for key in (
        "max_accounting_residual", "max_conservation_residual",
        "max_nonnegativity_residual")}
    print(f"worst residuals across all jobs: {worst}")
    return manifest


if __name__ == "__main__":
    execute(int(sys.argv[1]) if len(sys.argv) > 1 else None)
