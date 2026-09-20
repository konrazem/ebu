"""Registered homeostasis report: integrity gate, metrics, frozen contrasts.

Implements sections 8, 9 and 10 of `HOMEOSTASIS_STUDY_PREREGISTRATION.md`.
Frozen before any registered result exists.

Reads artifacts and writes one analysis file. It advances no model state and
runs no trajectory. It draws no conclusion beyond the registered categories:
verdicts are computed by the frozen rules in `homeostasis_analysis.py`, not
authored here.

The integrity gate runs first. If it fails, partial results are not analysed
and no contrast is reported (mission section 28).
"""

from __future__ import annotations

import gzip
import json
from fractions import Fraction
from pathlib import Path

import homeostasis_analysis as analysis
import homeostasis_registry as registry
from homeostasis.harness import (
    STATUS_AFFORDABILITY_BLOCKED,
    STATUS_EXECUTED,
    STATUS_PHYSICAL_NO_ACTION,
)
from homeostasis.metrics import exact_median, summarize
from homeostasis.policies import POLICY_CONTROL_RANDOM
from homeostasis.region import ConservationLaw, ReferenceRegion
from gaussian_harness.potential import LocalGaussianPotential

SOURCE = Path("results/homeostasis")
JOBS = SOURCE / "jobs"
OUTPUT = SOURCE / "ANALYSIS_RESULTS.json"

WINDOW = slice(registry.BURN_IN, registry.BURN_IN + registry.WINDOW)
ALLOWED_STATUSES = {STATUS_EXECUTED, STATUS_AFFORDABILITY_BLOCKED,
                    STATUS_PHYSICAL_NO_ACTION}


def _region() -> ReferenceRegion:
    potential = LocalGaussianPotential.declare(list(registry.REFERENCE), list(registry.SCALES))
    return ReferenceRegion.derive(
        potential, [ConservationLaw.total_mass(len(registry.REFERENCE), registry.DECLARED_MASS)]
    )


def _rational(value) -> str | None:
    if value is None:
        return None
    return f"{value.numerator}/{value.denominator}"


def collect() -> tuple[dict, dict]:
    """Read every artifact once, returning per-cell metrics and integrity facts."""
    region = _region()
    manifest = json.loads((SOURCE / "EXECUTION_MANIFEST.json").read_text())
    expected = {row["job_id"]: row for row in manifest["rows"]}

    cells: dict[tuple[str, str, str], dict[int, dict]] = {}
    seen: dict[str, set[str]] = {}
    problems: list[str] = []
    worst = {"accounting": Fraction(0), "conservation": Fraction(0), "nonnegativity": Fraction(0)}
    negative_capacity_jobs = 0
    unknown_status_jobs = 0
    no_action_ticks = 0
    blocked_ticks = 0

    for path in sorted(JOBS.glob("*.json.gz")):
        document = json.loads(gzip.decompress(path.read_bytes()))
        identity = document["identity"]
        payload = document["payload"]
        job_id = identity["job_id"]
        seen.setdefault(job_id, set()).add(document["payload_sha256"])

        if identity["code_identity"] != registry.REGISTERED_CODE_IDENTITY:
            problems.append(f"{job_id}: code identity mismatch")
        if identity["configuration_identity"] != registry.configuration_identity():
            problems.append(f"{job_id}: configuration identity mismatch")
        if job_id not in expected:
            problems.append(f"{job_id}: artifact not in the execution manifest")
        elif expected[job_id]["payload_sha256"] != document["payload_sha256"]:
            problems.append(f"{job_id}: payload hash differs from the manifest")

        columns = payload["columns"]
        for key, name in (("max_accounting_residual", "accounting"),
                          ("max_conservation_residual", "conservation"),
                          ("max_nonnegativity_residual", "nonnegativity")):
            worst[name] = max(worst[name], abs(Fraction(payload[key])))

        statuses = set(columns["status"])
        if not statuses <= ALLOWED_STATUSES:
            unknown_status_jobs += 1
            problems.append(f"{job_id}: unregistered status {statuses - ALLOWED_STATUSES}")
        no_action_ticks += sum(1 for s in columns["status"] if s == STATUS_PHYSICAL_NO_ACTION)
        blocked_ticks += sum(1 for s in columns["status"] if s == STATUS_AFFORDABILITY_BLOCKED)

        min_balances = [Fraction(v) for v in columns["minB"]]
        if identity["policy_id"] != POLICY_CONTROL_RANDOM and min(min_balances) < 0:
            negative_capacity_jobs += 1
            problems.append(f"{job_id}: negative capacity in an affordability arm")

        radial = [Fraction(v) for v in columns["R2"]][WINDOW]
        in95 = [region.contains_radial_square(v, "H95") for v in radial]
        in99 = [region.contains_radial_square(v, "H99") for v in radial]
        summary = summarize(radial, in95, in99, registry.BLOCK, registry.BLOCKS)
        executed = sum(1 for s in columns["status"] if s == STATUS_EXECUTED)
        nulls = sum(1 for flag in columns["null_action"] if flag)

        key = (identity["menu_rule"], identity["load_id"], identity["policy_id"])
        cells.setdefault(key, {})[identity["replicate"]] = {
            "O95": summary.occupancy_95,
            "O99": summary.occupancy_99,
            "mean_V": summary.mean_potential,
            "median_R2": summary.median_radial_square,
            "p95_R2": summary.p95_radial_square_exact,
            "max_R2": summary.max_radial_square_exact,
            "radius_mean": summary.radius_mean,
            "exits": summary.exits_95,
            "time_outside_95": summary.time_outside_95,
            "excursion_duration_max": summary.excursion_duration_max,
            "excursion_severity_max": summary.excursion_severity_max,
            "return_time_median": summary.return_time_median,
            "block_O95": [b.occupancy_95 for b in summary.blocks],
            "block_median_R2": [b.median_radial_square for b in summary.blocks],
            "divergence": analysis.divergence_flag(
                [b.occupancy_95 for b in summary.blocks],
                [b.median_radial_square for b in summary.blocks]),
            "null_action_rate": Fraction(nulls, executed) if executed else Fraction(0),
            "null_forcing": sum(1 for s in columns["forcing_status"] if s == "NULL_FORCING"),
            "mean_n_affordable": Fraction(sum(columns["n_affordable"]), len(columns["n_affordable"])),
        }

    conflicts = sorted(job for job, hashes in seen.items() if len(hashes) > 1)
    missing = sorted(set(expected) - set(seen))
    if missing:
        problems.append(f"{len(missing)} expected jobs are missing")
    if conflicts:
        problems.append(f"{len(conflicts)} jobs have conflicting payload hashes")

    integrity = {
        "jobs_expected": len(expected),
        "jobs_observed": len(seen),
        "missing_jobs": len(missing),
        "conflicting_payloads": len(conflicts),
        "max_accounting_residual": _rational(worst["accounting"]),
        "max_conservation_residual": _rational(worst["conservation"]),
        "max_nonnegativity_residual": _rational(worst["nonnegativity"]),
        "negative_capacity_jobs": negative_capacity_jobs,
        "unregistered_status_jobs": unknown_status_jobs,
        "physical_no_action_ticks": no_action_ticks,
        "affordability_blocked_ticks": blocked_ticks,
        "problems": problems,
        "passed": not problems
        and worst["accounting"] == 0
        and worst["conservation"] == 0
        and worst["nonnegativity"] == 0,
    }
    return cells, integrity


def build() -> dict:
    cells, integrity = collect()
    report: dict = {
        "analysis_id": analysis.ANALYSIS_ID,
        "protocol_id": registry.PROTOCOL_ID,
        "primary_endpoint": "O95",
        "integrity": integrity,
        "menus": {},
    }
    if not integrity["passed"]:
        report["contrasts_suppressed"] = (
            "INTEGRITY GATE FAILED: partial results are not interpreted (mission 28)"
        )
        return report

    for menu_rule in registry.MENUS:
        per_load: dict[str, dict[str, dict[int, Fraction]]] = {}
        descriptive: dict[str, dict[str, dict]] = {}
        for load_id in registry.LOADS:
            occupancy: dict[str, dict[int, Fraction]] = {}
            rows: dict[str, dict] = {}
            for policy_id in registry.POLICIES:
                cell = cells.get((menu_rule, load_id, policy_id), {})
                if not cell:
                    continue
                occupancy[policy_id] = {r: v["O95"] for r, v in cell.items()}
                values = list(cell.values())
                def med(key):
                    return exact_median([v[key] for v in values])
                rows[policy_id] = {
                    "replicates": len(values),
                    "median_O95": _rational(med("O95")),
                    "median_O95_float": float(med("O95")),
                    "band": analysis.band(med("O95")),
                    "median_O99": _rational(med("O99")),
                    "median_O99_float": float(med("O99")),
                    "median_mean_V_float": float(med("mean_V")),
                    "median_median_R2": _rational(med("median_R2")),
                    "median_p95_R2": _rational(med("p95_R2")),
                    "median_max_R2": _rational(med("max_R2")),
                    "median_radius_mean": sorted(v["radius_mean"] for v in values)[len(values)//2],
                    "median_exits": _rational(med("exits")),
                    "median_time_outside_95": _rational(med("time_outside_95")),
                    "median_excursion_duration_max": _rational(
                        exact_median([Fraction(v["excursion_duration_max"] or 0) for v in values])),
                    "median_excursion_severity_max": _rational(
                        exact_median([v["excursion_severity_max"] or Fraction(0) for v in values])),
                    "median_return_time": _rational(
                        exact_median([v["return_time_median"] or Fraction(0) for v in values])),
                    "block_median_O95_float": [
                        float(exact_median([v["block_O95"][i] for v in values]))
                        for i in range(registry.BLOCKS)],
                    "block_median_R2": [
                        _rational(exact_median([v["block_median_R2"][i] for v in values]))
                        for i in range(registry.BLOCKS)],
                    "divergence_replicates": sum(1 for v in values if v["divergence"]),
                    "median_null_action_rate_float": float(med("null_action_rate")),
                    "median_null_forcing": _rational(med("null_forcing")),
                    "median_mean_n_affordable_float": float(med("mean_n_affordable")),
                }
            per_load[load_id] = occupancy
            descriptive[load_id] = rows
        contrasts = analysis.report(per_load)
        report["menus"][menu_rule] = {
            "descriptive": descriptive,
            "contrasts": contrasts["loads"],
        }
    return report


if __name__ == "__main__":
    result = build()
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    integrity = result["integrity"]
    print("INTEGRITY:", "PASSED" if integrity["passed"] else "FAILED")
    for key in ("jobs_expected", "jobs_observed", "missing_jobs", "conflicting_payloads",
                "max_accounting_residual", "max_conservation_residual",
                "max_nonnegativity_residual", "negative_capacity_jobs",
                "unregistered_status_jobs", "physical_no_action_ticks",
                "affordability_blocked_ticks"):
        print(f"  {key}: {integrity[key]}")
    if integrity["problems"]:
        for problem in integrity["problems"][:10]:
            print("  PROBLEM:", problem)
    if not integrity["passed"]:
        raise SystemExit(1)
    for menu_rule, menu in result["menus"].items():
        print(f"\n=== menu: {menu_rule} ===")
        for load_id in registry.LOADS:
            print(f"\n  load {load_id}")
            print(f"    {'policy':<17}{'O95':>9}{'O99':>9}{'medR2':>8}{'maxR2':>8}"
                  f"{'null%':>8}{'exits':>7}{'div':>5}  band")
            for policy_id in registry.POLICIES:
                row = menu["descriptive"][load_id].get(policy_id)
                if not row:
                    continue
                print(f"    {policy_id:<17}{row['median_O95_float']:>9.4f}"
                      f"{row['median_O99_float']:>9.4f}"
                      f"{float(Fraction(row['median_median_R2'])):>8.1f}"
                      f"{float(Fraction(row['median_max_R2'])):>8.0f}"
                      f"{row['median_null_action_rate_float']*100:>7.1f}%"
                      f"{float(Fraction(row['median_exits'])):>7.0f}"
                      f"{row['divergence_replicates']:>5}  {row['band']}")
            for contrast in menu["contrasts"][load_id]["contrasts"]:
                print(f"      {contrast['name']:<20} median d = {contrast['median_difference_float']:+.4f}"
                      f"  p = {contrast['p_value_float']:.3e}"
                      f"  holm={contrast['holm_significant']}"
                      f"  delta={contrast['exceeds_delta']}  -> {contrast['verdict']}")
    print(f"\nwritten: {OUTPUT}")
