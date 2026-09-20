"""EXPLORATORY POST-REGISTERED HOMEOSTASIS ANALYSIS of the Stage-B trajectories.

Mission section 16. Applies the frozen homeostasis metrics of
`GAUSSIAN_HOMEOSTASIS_REFERENCE_REGION.md` and `homeostasis/metrics.py` to the
immutable Stage-B artifacts in `results/stage_b/ticks/`.

**This is exploratory and post-registered.** The metrics did not exist when
Stage B was frozen, executed or reported. Nothing here is confirmatory, no
p-value is computed, and `STAGE_B_REGISTERED_REPORT.md` is not rewritten,
reinterpreted or superseded.

Its purpose is narrow and stated in the mission: to understand how severe the
Stage-B continuous forcing actually was relative to the reference region the
new study will measure against. It reads artifacts and writes one new results
file. It advances no model state and runs no trajectory.
"""

from __future__ import annotations

import gzip
import json
from fractions import Fraction
from pathlib import Path

from gaussian_harness.harness import ARM_CONTROL, ARM_EBU
from homeostasis.metrics import exact_median, summarize
from homeostasis.region import ConservationLaw, ReferenceRegion
from gaussian_harness.potential import LocalGaussianPotential

SOURCE = Path("results/stage_b/ticks")
OUTPUT = Path("results/exploratory/STAGE_B_HOMEOSTASIS_REANALYSIS.json")

ANALYSIS_CLASS = "EXPLORATORY_POST_REGISTERED"
BURN_IN = 2048
BLOCK = 2048
BLOCKS = 3


def _region() -> ReferenceRegion:
    potential = LocalGaussianPotential.declare([10, 10, 10], [1, 1, 1])
    return ReferenceRegion.derive(potential, [ConservationLaw.total_mass(3, 30)])


def analyse() -> dict:
    region = _region()
    per_arm: dict[str, list[dict]] = {ARM_EBU: [], ARM_CONTROL: []}

    for path in sorted(SOURCE.glob("*.json.gz")):
        payload = json.loads(gzip.decompress(path.read_bytes()))
        arm = payload["arm"]
        potentials = [Fraction(value) for value in payload["columns"]["V"]]
        window = potentials[BURN_IN:BURN_IN + BLOCK * BLOCKS]
        radial = [2 * value for value in window]
        in95 = [region.contains_radial_square(value, "H95") for value in radial]
        in99 = [region.contains_radial_square(value, "H99") for value in radial]
        summary = summarize(radial, in95, in99, block=BLOCK, blocks=BLOCKS)
        per_arm[arm].append(
            {
                "replicate": payload["replicate"],
                "O95": summary.occupancy_95,
                "O99": summary.occupancy_99,
                "mean_V": summary.mean_potential,
                "median_R2": summary.median_radial_square,
                "p95_R2": summary.p95_radial_square_exact,
                "max_R2": summary.max_radial_square_exact,
                "radius_mean": summary.radius_mean,
                "exits": summary.exits_95,
                "excursions": summary.excursion_count,
                "time_outside_95": summary.time_outside_95,
                "excursion_duration_max": summary.excursion_duration_max,
                "return_time_median": summary.return_time_median,
                "block_O95": [block.occupancy_95 for block in summary.blocks],
                "block_median_R2": [block.median_radial_square for block in summary.blocks],
                "drift_occupancy": summary.drift.occupancy_change,
                "drift_median": summary.drift.median_change,
            }
        )

    report: dict = {
        "analysis_class": ANALYSIS_CLASS,
        "source": str(SOURCE),
        "burn_in": BURN_IN,
        "block": BLOCK,
        "blocks": BLOCKS,
        "window": BLOCK * BLOCKS,
        "region_rule": "EBU-GAUSSIAN-HOMEOSTATIC-REGION-v1",
        "h95_shells": "R^2 in {0, 2}",
        "h99_shells": "R^2 in {0, 2, 6, 8}",
        "arms": {},
        "non_claims": [
            "post-registered and exploratory; not confirmatory evidence",
            "does not modify, reinterpret or supersede the Stage-B registered report",
            "no hypothesis test is performed and no p-value is reported",
        ],
    }

    for arm, rows in per_arm.items():
        if not rows:
            continue
        def med(key):
            return exact_median([row[key] for row in rows])
        report["arms"][arm] = {
            "replicates": len(rows),
            "median_O95": str(med("O95")),
            "median_O95_float": float(med("O95")),
            "median_O99": str(med("O99")),
            "median_O99_float": float(med("O99")),
            "median_mean_V": str(med("mean_V")),
            "median_mean_V_float": float(med("mean_V")),
            "median_median_R2": str(med("median_R2")),
            "median_p95_R2": str(med("p95_R2")),
            "median_max_R2": str(med("max_R2")),
            "max_max_R2": str(max(row["max_R2"] for row in rows)),
            "median_radius_mean": sorted(row["radius_mean"] for row in rows)[len(rows) // 2],
            "median_exits": str(med("exits")),
            "median_excursions": str(med("excursions")),
            "median_time_outside_95": str(med("time_outside_95")),
            "median_excursion_duration_max": str(
                exact_median([Fraction(row["excursion_duration_max"] or 0) for row in rows])
            ),
            "replicates_never_in_H95": sum(1 for row in rows if row["O95"] == 0),
            "replicates_never_in_H99": sum(1 for row in rows if row["O99"] == 0),
            "block_median_O95": [
                str(exact_median([row["block_O95"][index] for row in rows]))
                for index in range(BLOCKS)
            ],
            "block_median_O95_float": [
                float(exact_median([row["block_O95"][index] for row in rows]))
                for index in range(BLOCKS)
            ],
            "block_median_R2": [
                str(exact_median([row["block_median_R2"][index] for row in rows]))
                for index in range(BLOCKS)
            ],
            "replicates_with_falling_occupancy": sum(
                1 for row in rows if row["drift_occupancy"] < 0
            ),
            "replicates_with_rising_median_R2": sum(
                1 for row in rows if row["drift_median"] > 0
            ),
        }
    return report


if __name__ == "__main__":
    result = analyse()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    for arm, summary in result["arms"].items():
        print(f"\n{arm}  (n={summary['replicates']})")
        print(f"  median O95            {summary['median_O95']}  = {summary['median_O95_float']:.4f}")
        print(f"  median O99            {summary['median_O99']}  = {summary['median_O99_float']:.4f}")
        print(f"  median mean V         {summary['median_mean_V_float']:.3f}")
        print(f"  median median R^2     {summary['median_median_R2']}")
        print(f"  median p95 R^2        {summary['median_p95_R2']}")
        print(f"  median max R^2        {summary['median_max_R2']}   worst {summary['max_max_R2']}")
        print(f"  median mean R         {summary['median_radius_mean']:.4f}")
        print(f"  median exits from H95 {summary['median_exits']}")
        print(f"  median time outside   {summary['median_time_outside_95']} / {result['window']}")
        print(f"  longest excursion     {summary['median_excursion_duration_max']} (median over replicates)")
        print(f"  never in H95          {summary['replicates_never_in_H95']} replicates")
        print(f"  never in H99          {summary['replicates_never_in_H99']} replicates")
        print(f"  block median O95      {summary['block_median_O95_float']}")
        print(f"  block median R^2      {summary['block_median_R2']}")
        print(f"  falling occupancy     {summary['replicates_with_falling_occupancy']} replicates")
        print(f"  rising median R^2     {summary['replicates_with_rising_median_R2']} replicates")
    print(f"\nwritten: {OUTPUT}")
    print("CLASS: EXPLORATORY POST-REGISTERED -- not confirmatory evidence")
