"""Verify the registered load-coupling design held in the executed artifacts.

Section 6 of `HOMEOSTASIS_STUDY_PREREGISTRATION.md` registers that one
counter-addressed raw forcing process is shared across all three loads, that
each load is realized by thresholding the same per-tick variate, and that on a
tick shared by two loads the raw edge and orientation proposal is identical.

This is **implementation verification, not analysis.** It checks a declared
design property against the data actually produced. It computes no endpoint, no
contrast and no p-value, and it changes nothing. It is deliberately separate
from the frozen `homeostasis_report.py`.

It also confirms the third registered clause: that arm-specific `NULL_FORCING`
is preserved as an observed consequence of arms occupying different states,
rather than being suppressed into a common applied stream.
"""

from __future__ import annotations

import gzip
import json
from collections import defaultdict
from pathlib import Path

import homeostasis_registry as registry

JOBS = Path("results/homeostasis/jobs")
OUTPUT = Path("results/homeostasis/FORCING_COUPLING_VERIFICATION.json")


def verify() -> dict:
    # (menu, policy, replicate) -> load -> {tick: raw_forcing_id}
    schedules: dict[tuple[str, str, int], dict[str, dict[int, str]]] = defaultdict(dict)
    null_forcing: dict[tuple[str, str, int], dict[str, int]] = defaultdict(dict)

    for path in sorted(JOBS.glob("*.json.gz")):
        document = json.loads(gzip.decompress(path.read_bytes()))
        identity = document["identity"]
        columns = document["payload"]["columns"]
        key = (identity["menu_rule"], identity["policy_id"], identity["replicate"])
        schedules[key][identity["load_id"]] = {
            tick: value
            for tick, value in enumerate(columns["raw_forcing"])
            if value is not None
        }
        null_forcing[key][identity["load_id"]] = sum(
            1 for status in columns["forcing_status"] if status == "NULL_FORCING"
        )

    mild, medium, full = registry.LOADS
    nesting_failures: list[str] = []
    edge_mismatches: list[str] = []
    checked = 0
    for key, by_load in schedules.items():
        if not {mild, medium, full} <= set(by_load):
            continue
        checked += 1
        a, b, c = by_load[mild], by_load[medium], by_load[full]
        if not set(a) <= set(b):
            nesting_failures.append(f"{key}: 1/4 not a subset of 1/2")
        if not set(b) <= set(c):
            nesting_failures.append(f"{key}: 1/2 not a subset of 1")
        for tick in a:
            if tick in b and a[tick] != b[tick]:
                edge_mismatches.append(f"{key}@{tick}: 1/4 vs 1/2 edge differs")
            if tick in c and a[tick] != c[tick]:
                edge_mismatches.append(f"{key}@{tick}: 1/4 vs 1 edge differs")
        for tick in b:
            if tick in c and b[tick] != c[tick]:
                edge_mismatches.append(f"{key}@{tick}: 1/2 vs 1 edge differs")

    # Arm-specific NULL_FORCING: at a given load and replicate, do arms differ?
    by_cell: dict[tuple[str, str, int], dict[str, int]] = defaultdict(dict)
    for (menu_rule, policy_id, replicate), loads in null_forcing.items():
        for load_id, count in loads.items():
            by_cell[(menu_rule, load_id, replicate)][policy_id] = count
    arms_differ = sum(1 for counts in by_cell.values() if len(set(counts.values())) > 1)

    # Realized frequencies, to confirm thresholding rather than independence.
    sizes = {load_id: [] for load_id in registry.LOADS}
    for by_load in schedules.values():
        for load_id, ticks in by_load.items():
            sizes[load_id].append(len(ticks))

    return {
        "verification_class": "IMPLEMENTATION_VERIFICATION_NOT_ANALYSIS",
        "cells_checked": checked,
        "nesting_failures": len(nesting_failures),
        "nesting_examples": nesting_failures[:5],
        "shared_tick_edge_mismatches": len(edge_mismatches),
        "edge_examples": edge_mismatches[:5],
        "nesting_holds": not nesting_failures,
        "shared_edges_identical": not edge_mismatches,
        "mean_forced_ticks": {
            load_id: (sum(values) / len(values) if values else 0)
            for load_id, values in sizes.items()
        },
        "horizon": registry.HORIZON,
        "cells_where_arms_differ_in_null_forcing": arms_differ,
        "cells_compared_for_null_forcing": len(by_cell),
    }


if __name__ == "__main__":
    result = verify()
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("REGISTERED LOAD-COUPLING VERIFICATION")
    print(f"  cells checked                    {result['cells_checked']}")
    print(f"  1/4 subset 1/2 subset 1          {result['nesting_holds']}"
          f"  (failures: {result['nesting_failures']})")
    print(f"  shared-tick edges identical      {result['shared_edges_identical']}"
          f"  (mismatches: {result['shared_tick_edge_mismatches']})")
    print(f"  mean forced ticks of {result['horizon']}:")
    for load_id, mean in result["mean_forced_ticks"].items():
        print(f"    {load_id:<14} {mean:>9.1f}   ({mean/result['horizon']:.4f})")
    print(f"  cells where arms differ in NULL_FORCING: "
          f"{result['cells_where_arms_differ_in_null_forcing']}"
          f" / {result['cells_compared_for_null_forcing']}")
    print(f"\nwritten: {OUTPUT}")
