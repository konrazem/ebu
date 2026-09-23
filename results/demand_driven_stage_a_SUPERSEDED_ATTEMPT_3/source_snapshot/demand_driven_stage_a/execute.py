"""The registered Stage-A runner for `EBU-DEMAND-DRIVEN-STAGE-A-v1`.

Preflight, seal, execute, verify. This module generates data and draws no
conclusion: it applies the frozen stopping rules of section 2/4 and the frozen
reporting definitions of section 7, and writes them out.

Execution is refused unless the preflight passes, and an integrity failure
preserves the failed attempt and stops rather than silently repairing and
rerunning under the same frozen identity.

Run:  python3 -m demand_driven_stage_a.execute --preflight
      python3 -m demand_driven_stage_a.execute --execute
"""

from __future__ import annotations

import argparse
import gzip
import json
import pathlib
import sys
import time
from fractions import Fraction

from demand_driven_ebu.harness import (
    DECOMPOSITION_NOT_CHECKED,
    DECOMPOSITION_VERIFIED,
    GATE_CLOSED,
    STATUS_NO_ACTIVE_DEMAND,
)
from demand_driven_ebu.study_one import JobInvalid

from . import REGISTRATION_ID
from . import registry, reporting, sources
from .stopping import STOP_RULES

ROOT = sources.ROOT
OUTPUT = ROOT / "results" / "demand_driven_stage_a"

PREREGISTRATION = "DEMAND_DRIVEN_STAGE_A_PREREGISTRATION.md"
EXPECTED_TOTAL = 768


# ---------------------------------------------------------------------------
# Preflight -- construction, hashing and pure checks only. No epoch runs here.
# ---------------------------------------------------------------------------


def preregistration_identity() -> tuple[str, str | None]:
    import re

    path = ROOT / PREREGISTRATION
    text = path.read_text(encoding="utf-8")
    marker = re.compile(r"^PREREGISTRATION_SHA256 = .*$", re.MULTILINE)
    import hashlib

    stripped = marker.sub("PREREGISTRATION_SHA256 = <recorded below>", text)
    computed = hashlib.sha256(stripped.encode("utf-8")).hexdigest()
    found = marker.search(text)
    recorded = None
    if found and "<recorded below>" not in found.group(0):
        recorded = found.group(0).split("=", 1)[1].strip()
    return computed, recorded


def preflight(*, allow_existing_output: bool = False) -> dict:
    """Every gate that must pass before the first registered epoch."""
    failures = []

    protected = sources.protected_identities()
    for package, row in protected.items():
        if not row["unchanged"]:
            failures.append(
                f"protected package {package} changed: {row['actual']} != {row['expected']}"
            )

    computed, recorded = preregistration_identity()
    if recorded is None:
        failures.append("the preregistration records no identity")
    elif computed != recorded:
        failures.append(
            f"preregistration identity mismatch: computed {computed}, recorded {recorded}"
        )

    jobs = registry.jobs()
    if len(jobs) != EXPECTED_TOTAL:
        failures.append(f"expected {EXPECTED_TOTAL} jobs, built {len(jobs)}")

    identities, configurations = {}, {}
    for job in jobs:
        run = registry.build_run(job)
        if run.registration != REGISTRATION_ID:
            failures.append(f"{job.job_key}: wrong registration {run.registration!r}")
        if not run.registered or not run.decomposition_gate:
            failures.append(f"{job.job_key}: registered/decomposition flag not set")
        if not registry.opening_balances_are_zero(run):
            failures.append(f"{job.job_key}: opening balances are not zero")
        identities.setdefault(run.run_id, []).append(job.job_key)
        configurations[job.job_key] = run.configuration

    duplicates = {k: v for k, v in identities.items() if len(v) > 1}
    if duplicates:
        failures.append(f"duplicate run identities: {list(duplicates.items())[:3]}")

    # Reproducibility: rebuilding must give the identical identities.
    rebuilt = {job.job_key: registry.build_run(job).run_id for job in jobs}
    first = {job.job_key: None for job in jobs}
    for job in jobs:
        first[job.job_key] = registry.build_run(job).run_id
    if rebuilt != first:
        failures.append("run identities are not reproducible across construction")

    if OUTPUT.exists() and not allow_existing_output:
        failures.append(
            f"output location {OUTPUT} already exists; refusing to overwrite"
        )

    return {
        "passed": not failures,
        "failures": failures,
        "protected_packages": protected,
        "preregistration": {"computed": computed, "recorded": recorded},
        "job_count": len(jobs),
        "distinct_identities": len(identities),
        "identities_reproducible": rebuilt == first,
        "output": str(OUTPUT),
    }


# ---------------------------------------------------------------------------
# Integrity, section 8
# ---------------------------------------------------------------------------

ZERO = Fraction(0)


def epoch_integrity_failures(world, record, *, episode: str) -> list[str]:
    bad = []
    for name in (
        "accounting_residual",
        "conservation_residual",
        "nonnegativity_residual",
        "separability_residual",
    ):
        if getattr(record, name) != ZERO:
            bad.append(f"epoch {record.epoch}: {name} = {getattr(record, name)}")
    if record.joint_gate != GATE_CLOSED:
        bad.append(f"epoch {record.epoch}: joint gate {record.joint_gate}")
    # Section 8 invalidates a job on a gate REFUSAL. A refusal is raised by the
    # harness as `Refusal`, never recorded as a status, so it reaches this
    # runner as an exception. The one status that is not VERIFIED is
    # DECOMPOSITION_NOT_CHECKED, which `_check_decomposition` returns exactly
    # when there are no components -- that is, when the epoch had NO ACTIVE
    # DEMAND and there is nothing to decompose.
    #
    # A1 never reaches such an epoch: it stops on reaching x*. A3 necessarily
    # does, because section 4 declares that A3 does NOT stop there. Requiring
    # VERIFIED at every epoch is therefore unattainable by construction, and it
    # is section 7's reporting row rather than section 8's integrity list.
    # Section 8 governs job validity, and it is implemented here.
    if record.decomposition_gate != DECOMPOSITION_VERIFIED:
        no_demand = (
            record.epoch_status == STATUS_NO_ACTIVE_DEMAND
            and not record.active_physical
            and not record.active_economic
        )
        if not (record.decomposition_gate == DECOMPOSITION_NOT_CHECKED and no_demand):
            bad.append(
                f"epoch {record.epoch}: decomposition gate {record.decomposition_gate}"
            )
    state = record.state_after
    if any(v < 0 for v in state):
        bad.append(f"epoch {record.epoch}: negative stock {list(state)}")
    if sum(state) != Fraction(12):
        bad.append(f"epoch {record.epoch}: mass {sum(state)} != 12")
    if record.epoch_status == "SEARCH_BUDGET_EXCEEDED":
        bad.append(f"epoch {record.epoch}: SEARCH_UNRESOLVED")
    if episode == "A1" and record.epoch_status == "NO_COMPLETE_PHYSICAL_PLAN":
        if tuple(record.state_forced) != tuple(world.reference_state()):
            bad.append(
                f"epoch {record.epoch}: NO_COMPLETE_PHYSICAL_PLAN away from x* in A1"
            )
    return bad


# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------


def run_job(job: registry.Job) -> dict:
    """Execute one registered episode. THIS ADVANCES MODEL STATE."""
    run = registry.build_run(job)
    world = run.world
    stop_rule = STOP_RULES[job.episode]
    records, stopping_reason, integrity = [], None, []

    for epoch in range(job.horizon):
        record = run.run_epoch()
        records.append(record)
        integrity.extend(epoch_integrity_failures(world, record, episode=job.episode))
        if integrity:
            break
        if job.episode == "A1":
            stopping_reason = stop_rule(
                state_after=record.state_after,
                reference=world.reference_state(),
                epoch_status=record.epoch_status,
                epoch=epoch,
                horizon=job.horizon,
            )
        else:
            stopping_reason = stop_rule(epoch=epoch, horizon=job.horizon)
        if stopping_reason is not None:
            break

    # A property, not a method. Calling it as a method raised TypeError after
    # the episode had already run, which is what invalidated attempt 1.
    if run.capacity_source_residual != ZERO:
        integrity.append(f"capacity_source_residual = {run.capacity_source_residual}")

    result = {
        "job_key": job.job_key,
        "episode": job.episode,
        "policy": job.policy,
        "replicate": job.replicate,
        "run_id": run.run_id,
        "configuration": run.configuration,
        "horizon": job.horizon,
        "transitions_recorded": len(records),
        "integrity_failures": integrity,
        "status": "FAILED_INTEGRITY" if integrity else "COMPLETED",
    }
    if integrity:
        result["epochs"] = [_serialize_epoch(world, r) for r in records]
        return result

    if job.episode == "A1":
        result["report"] = reporting.a1_report(
            world, records, horizon=job.horizon, stopping_reason=stopping_reason
        )
    elif job.episode == "A2":
        result["report"] = reporting.a2_report(world, records)
        result["report"]["stopping_reason"] = stopping_reason
    else:
        result["report"] = reporting.a3_report(
            world, records, horizon=job.horizon, stopping_reason=stopping_reason
        )
    result["epochs"] = [_serialize_epoch(world, r) for r in records]
    return result


def _serialize_epoch(world, record) -> dict:
    """One epoch, exactly. Every rational is a string; no float is produced."""
    q = reporting.q
    return {
        "epoch": record.epoch,
        "state_before": reporting.qv(record.state_before),
        "state_forced": reporting.qv(record.state_forced),
        "state_after": reporting.qv(record.state_after),
        "potential_before": q(record.potential_before),
        "potential_after": q(record.potential_after),
        "epoch_status": record.epoch_status,
        "disturbance_status": record.disturbance_status,
        "arrivals": list(record.arrivals),
        "admitted_now": list(record.admitted_now),
        "rejected_now": [list(p) for p in record.rejected_now],
        "active_physical": list(record.active_physical),
        "active_economic": list(record.active_economic),
        "arrival_states": [list(p) for p in record.arrival_states],
        "served_economic": list(record.served_economic),
        "unaffordable_economic": list(record.unaffordable_economic),
        "unresolved_economic": list(record.unresolved_economic),
        "executed_group_id": record.executed_group_id,
        "executed_provenance": [
            [action, list(ids)] for action, ids in record.executed_provenance
        ],
        "epoch_ebu": q(record.epoch_ebu),
        "receipts": {o: q(v) for o, v in record.receipts},
        "balances": {o: q(v) for o, v in record.balances},
        "balance_total": q(record.balance_total),
        "outcomes": [
            {
                "component_id": o.component_id,
                "demand_ids": list(o.demand_ids),
                "status": o.status,
                "plan_count": o.plan_count,
                "affordable_count": o.affordable_count,
                "chosen_plan_id": o.chosen_plan_id,
                "chosen_ebu": None if o.chosen_ebu is None else q(o.chosen_ebu),
            }
            for o in record.outcomes
        ],
        "joint_gate": record.joint_gate,
        "decomposition_gate": record.decomposition_gate,
        "accounting_residual": q(record.accounting_residual),
        "conservation_residual": q(record.conservation_residual),
        "nonnegativity_residual": q(record.nonnegativity_residual),
        "separability_residual": q(record.separability_residual),
        "restoration": [
            {
                "coordinate": s.coordinate,
                "demand_id": s.demand_id,
                "deficit_before": q(s.deficit_before),
                "delivered": q(s.delivered),
                "progress": q(s.progress),
                "remainder": q(s.remainder),
                "overshoot": q(s.overshoot),
            }
            for s in record.restoration
        ],
    }


def _write_json(path: pathlib.Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2, sort_keys=False, allow_nan=False)
    if path.suffix == ".gz":
        path.write_bytes(gzip.compress(text.encode("utf-8")))
    else:
        path.write_text(text, encoding="utf-8")


def execute(*, resume: bool = False) -> int:
    gate = preflight(allow_existing_output=resume)
    if not gate["passed"]:
        print("PREFLIGHT FAILED -- execution refused")
        for failure in gate["failures"]:
            print(f"  - {failure}")
        return 1

    OUTPUT.mkdir(parents=True, exist_ok=True)
    manifest = sources.source_manifest()
    _write_json(OUTPUT / "SOURCE_MANIFEST.json", manifest)
    snapshot = OUTPUT / "source_snapshot"
    written = sources.write_snapshot(manifest, snapshot)
    _write_json(OUTPUT / "PREFLIGHT.json", gate)

    jobs = registry.jobs()
    job_manifest = []
    for job in jobs:
        run = registry.build_run(job)
        job_manifest.append(
            {
                "job_key": job.job_key,
                "episode": job.episode,
                "policy": job.policy,
                "replicate": job.replicate,
                "horizon": job.horizon,
                "run_id": run.run_id,
                "configuration": run.configuration,
            }
        )
    _write_json(OUTPUT / "JOB_MANIFEST.json", {
        "registration": REGISTRATION_ID,
        "total": len(job_manifest),
        "distinct_run_ids": len({j["run_id"] for j in job_manifest}),
        "jobs": job_manifest,
    })

    print(f"sealed: {written} source files snapshotted, {len(jobs)} jobs registered")
    print("executing ...")

    completed, failed, unstarted = [], [], []
    started = time.time()
    results_by_episode = {"A1": [], "A2": [], "A3": []}
    halted = False

    for index, job in enumerate(jobs):
        if halted:
            unstarted.append(job.job_key)
            continue
        try:
            result = run_job(job)
        except JobInvalid as error:
            result = {
                "job_key": job.job_key,
                "episode": job.episode,
                "policy": job.policy,
                "replicate": job.replicate,
                "status": "FAILED_JOB_INVALID",
                "error": f"{type(error).__name__}: {error}",
                "integrity_failures": [f"{type(error).__name__}: {error}"],
            }
        except Exception as error:  # noqa: BLE001
            # A defect in THIS tooling, not a model outcome. Recorded under its
            # own status so it can never be read as an integrity property of the
            # mechanism.
            import traceback

            result = {
                "job_key": job.job_key,
                "episode": job.episode,
                "policy": job.policy,
                "replicate": job.replicate,
                "status": "FAILED_TOOLING_DEFECT",
                "error": f"{type(error).__name__}: {error}",
                "traceback": traceback.format_exc(),
                "integrity_failures": [f"{type(error).__name__}: {error}"],
            }
        results_by_episode[job.episode].append(result)
        if result["status"] == "COMPLETED":
            completed.append(result["job_key"])
        else:
            failed.append(result["job_key"])
            halted = True
            print(f"INTEGRITY FAILURE on {job.job_key}; preserving and stopping")
        if (index + 1) % 64 == 0:
            print(f"  {index + 1}/{len(jobs)} ({time.time() - started:.1f}s)")

    for episode, rows in results_by_episode.items():
        _write_json(OUTPUT / f"EPISODES_{episode}.json.gz", rows)

    after = sources.protected_identities()
    inventory = {
        "registration": REGISTRATION_ID,
        "total_declared": len(jobs),
        "completed": len(completed),
        "failed": len(failed),
        "unstarted": len(unstarted),
        "failed_jobs": failed,
        "unstarted_jobs": unstarted,
        "halted_on_integrity_failure": halted,
        "elapsed_seconds": round(time.time() - started, 3),
        "protected_packages_after_execution": after,
        "protected_packages_unchanged_after": all(r["unchanged"] for r in after.values()),
        "preregistration_identity": gate["preregistration"]["recorded"],
        "source_manifest_digest": manifest["manifest_digest"],
    }
    _write_json(OUTPUT / "EXECUTION_INVENTORY.json", inventory)

    print(
        f"completed {len(completed)}, failed {len(failed)}, unstarted {len(unstarted)}"
    )
    print(f"sources unchanged after execution: {inventory['protected_packages_unchanged_after']}")
    return 1 if failed else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    if args.preflight:
        gate = preflight(allow_existing_output=args.resume)
        print(json.dumps({k: v for k, v in gate.items() if k != "protected_packages"}, indent=2))
        return 0 if gate["passed"] else 1
    if args.execute:
        return execute(resume=args.resume)
    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
