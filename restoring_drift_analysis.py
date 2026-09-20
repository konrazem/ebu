"""EXPLORATORY POST-REGISTERED RESTORING-DRIFT ANALYSIS.

Mission section 12. Re-reads the immutable registered homeostasis artifacts
(1,536 jobs, 12,582,912 arm-ticks) under the restoring-tendency definition.

**Exploratory and post-registered.** The drift decomposition did not exist when
the homeostasis study was frozen, executed or reported. Nothing here is
confirmatory, no hypothesis is tested, no p-value is computed, and
`HOMEOSTASIS_REGISTERED_REPORT.md` is not modified or reinterpreted.

Canonical tick decomposition (mission section 3)
------------------------------------------------

    x_t --[external forcing]--> z_t --[actor action]--> x_{t+1}

    dV_ext(t)   = V(z_t)     - V(x_t)
    dV_actor(t) = V(x_{t+1}) - V(z_t)      = -E_t
    dV_total(t) = V(x_{t+1}) - V(x_t)      = dV_ext + dV_actor

Every one of these is recovered **exactly** from the registered artifacts:
`dV_ext` is the per-tick increment of the deviation ledger `J`, `dV_total` is
the per-tick increment of `R^2/2`, and `dV_actor` is their difference. All four
identities including `dV_actor = -E_t` were verified tick for tick against an
independent re-execution before this analysis was written.

On this lattice `R^2` is always an even integer, so every `V` and every
increment above is an **integer**. The arithmetic here is therefore exact by
construction, with no rational reduction and no floating point anywhere in the
accumulation.

What this is and is not
-----------------------

Mission section 6 forbids treating `V` as the state. The rigorous conditioning
variable is the complete Markov state `(x, B)`; the artifacts carry `x` only
through `R^2` and `B` only through its sum and minimum, so **the curves here
are the explanatory projections of section 6, not the rigorous state object**.
The exact full-state calculation is done separately by enumeration in
`exact_state_drift.py`, which does not depend on trajectories at all.
"""

from __future__ import annotations

import gzip
import json
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction
from pathlib import Path

import homeostasis_registry as registry

JOBS = Path("results/homeostasis/jobs")
OUTPUT = Path("results/exploratory/RESTORING_DRIFT_ANALYSIS.json")

WINDOW_START = registry.BURN_IN
WINDOW_STOP = registry.BURN_IN + registry.WINDOW
BLOCK = registry.BLOCK
BLOCKS = registry.BLOCKS

# High-deviation shells for return-time analysis, in V units.
HIGH_SHELLS = (50, 100, 150, 200)
RETURN_TARGET = 25


def _accumulate(path: Path) -> dict:
    document = json.loads(gzip.decompress(path.read_bytes()))
    identity = document["identity"]
    columns = document["payload"]["columns"]

    radial = [int(Fraction(v)) for v in columns["R2"]]
    ledger = [int(Fraction(v)) for v in columns["J"]]
    ebu_sign_source = columns["null_action"]

    horizon = len(radial)
    # V(x_t) for t = 0..H-1 ; V(x_0) = 0 because the world starts at x*.
    v_start = [0] + [radial[t] // 2 for t in range(horizon - 1)]
    v_end = [radial[t] // 2 for t in range(horizon)]
    d_ext = [ledger[0]] + [ledger[t] - ledger[t - 1] for t in range(1, horizon)]

    # Per-bin accumulators. Keys are integer V values.
    actor_by_z: dict[int, list[int]] = defaultdict(lambda: [0, 0, 0])   # n, sum, n_negative
    total_by_x: dict[int, list[int]] = defaultdict(lambda: [0, 0, 0])
    ext_by_x: dict[int, list[int]] = defaultdict(lambda: [0, 0, 0])
    ebu_by_z: dict[int, list[int]] = defaultdict(lambda: [0, 0, 0, 0])  # n, sum, n_pos, n_neg

    for t in range(WINDOW_START, WINDOW_STOP):
        vx = v_start[t]
        vz = vx + d_ext[t]
        dv_total = v_end[t] - vx
        dv_actor = v_end[t] - vz

        row = actor_by_z[vz]
        row[0] += 1
        row[1] += dv_actor
        row[2] += 1 if dv_actor < 0 else 0

        row = total_by_x[vx]
        row[0] += 1
        row[1] += dv_total
        row[2] += 1 if dv_total < 0 else 0

        row = ext_by_x[vx]
        row[0] += 1
        row[1] += d_ext[t]
        row[2] += 1 if d_ext[t] < 0 else 0

        # E_t = -dV_actor, signed EBU of the executed group.
        e = -dv_actor
        row = ebu_by_z[vz]
        row[0] += 1
        row[1] += e
        row[2] += 1 if e > 0 else 0
        row[3] += 1 if e < 0 else 0

    # Return-time from high-deviation shells, measured on V(x_t).
    returns: dict[int, list[int]] = {shell: [0, 0, 0] for shell in HIGH_SHELLS}
    for shell in HIGH_SHELLS:
        pending = None
        for t in range(WINDOW_START, WINDOW_STOP):
            value = v_start[t]
            if pending is None:
                if value >= shell:
                    pending = t
            elif value <= RETURN_TARGET:
                returns[shell][0] += 1
                returns[shell][1] += t - pending
                pending = None
        if pending is not None:
            returns[shell][2] += 1      # censored: never returned

    # Late-window movement of the V distribution, by block.
    block_mean_v: list[Fraction] = []
    for index in range(BLOCKS):
        start = WINDOW_START + index * BLOCK
        chunk = v_end[start:start + BLOCK]
        block_mean_v.append(Fraction(sum(chunk), len(chunk)))

    # Occupation of the maximum-deviation shell (boundary attraction, section 9C).
    vertex_ticks = sum(1 for t in range(WINDOW_START, WINDOW_STOP) if v_end[t] >= 250)

    return {
        "key": (identity["menu_rule"], identity["load_id"], identity["policy_id"]),
        "actor_by_z": {k: v for k, v in actor_by_z.items()},
        "total_by_x": {k: v for k, v in total_by_x.items()},
        "ext_by_x": {k: v for k, v in ext_by_x.items()},
        "ebu_by_z": {k: v for k, v in ebu_by_z.items()},
        "returns": returns,
        "block_mean_v": [(v.numerator, v.denominator) for v in block_mean_v],
        "vertex_ticks": vertex_ticks,
    }


def _merge(into: dict, row: dict) -> None:
    for name in ("actor_by_z", "total_by_x", "ext_by_x"):
        target = into[name]
        for key, value in row[name].items():
            slot = target.setdefault(key, [0, 0, 0])
            for index in range(3):
                slot[index] += value[index]
    target = into["ebu_by_z"]
    for key, value in row["ebu_by_z"].items():
        slot = target.setdefault(key, [0, 0, 0, 0])
        for index in range(4):
            slot[index] += value[index]
    for shell, value in row["returns"].items():
        slot = into["returns"].setdefault(shell, [0, 0, 0])
        for index in range(3):
            slot[index] += value[index]
    into["block_mean_v"].append(row["block_mean_v"])
    into["vertex_ticks"] += row["vertex_ticks"]
    into["jobs"] += 1


def _curve(bins: dict[int, list[int]]) -> list[dict]:
    """Exact mean and negative-fraction per V bin, ordered by V."""
    out = []
    for value in sorted(bins):
        count, total, negative = bins[value][0], bins[value][1], bins[value][2]
        if count == 0:
            continue
        out.append({
            "V": value,
            "n": count,
            "mean": [Fraction(total, count).numerator, Fraction(total, count).denominator],
            "mean_float": total / count,
            "p_negative": negative / count,
        })
    return out


def zero_crossing(curve: list[dict]) -> dict | None:
    """Largest V at which the drift curve changes sign from >= 0 to < 0.

    Reported as an empirical operating level only. No crossing is forced: if
    the curve never changes sign, None is returned and that is the finding.
    """
    supported = [row for row in curve if row["n"] >= 200]
    crossing = None
    for earlier, later in zip(supported, supported[1:]):
        if earlier["mean_float"] >= 0 > later["mean_float"]:
            crossing = {"below_V": earlier["V"], "above_V": later["V"],
                        "below_mean": earlier["mean_float"],
                        "above_mean": later["mean_float"]}
    return crossing


def analyse(workers: int = 12) -> dict:
    paths = sorted(JOBS.glob("*.json.gz"))
    cells: dict[tuple, dict] = {}
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for row in pool.map(_accumulate, paths, chunksize=8):
            key = tuple(row["key"])
            cell = cells.setdefault(key, {
                "actor_by_z": {}, "total_by_x": {}, "ext_by_x": {}, "ebu_by_z": {},
                "returns": {}, "block_mean_v": [], "vertex_ticks": 0, "jobs": 0,
            })
            _merge(cell, row)

    report: dict = {
        "analysis_class": "EXPLORATORY_POST_REGISTERED_RESTORING_DRIFT",
        "source": "results/homeostasis/jobs (registered, immutable)",
        "window": [WINDOW_START, WINDOW_STOP],
        "identities": {
            "dV_ext": "J[t] - J[t-1]",
            "dV_total": "(R2[t] - R2[t-1]) / 2",
            "dV_actor": "dV_total - dV_ext = -E_t",
        },
        "arithmetic": "exact integer; V and every increment are integers on this lattice",
        "non_claims": [
            "post-registered and exploratory; not confirmatory evidence",
            "does not modify or reinterpret the registered homeostasis report",
            "curves are the section 6 explanatory projection, not the rigorous state object",
        ],
        "cells": {},
    }

    for key, cell in sorted(cells.items()):
        menu_rule, load_id, policy_id = key
        actor = _curve(cell["actor_by_z"])
        total = _curve(cell["total_by_x"])
        ext = _curve(cell["ext_by_x"])
        blocks = [
            sum(Fraction(n, d) for n, d in (job[index] for job in cell["block_mean_v"]))
            / len(cell["block_mean_v"])
            for index in range(BLOCKS)
        ]
        ebu_rows = []
        for value in sorted(cell["ebu_by_z"]):
            count, total_e, positive, negative = cell["ebu_by_z"][value]
            if count < 200:
                continue
            ebu_rows.append({"V": value, "n": count, "mean_E": total_e / count,
                             "p_positive": positive / count, "p_negative": negative / count})
        report["cells"][f"{menu_rule}|{load_id}|{policy_id}"] = {
            "jobs": cell["jobs"],
            "g_actor": actor,
            "g_total": total,
            "g_ext": ext,
            "ebu_by_V": ebu_rows,
            "zero_crossing_total": zero_crossing(total),
            "zero_crossing_actor": zero_crossing(actor),
            "returns": {
                str(shell): {
                    "episodes_returned": value[0],
                    "mean_return_ticks": (value[1] / value[0]) if value[0] else None,
                    "episodes_censored": value[2],
                }
                for shell, value in sorted(cell["returns"].items())
            },
            "block_mean_V": [float(b) for b in blocks],
            "late_window_movement": float(blocks[-1] - blocks[0]),
            "vertex_shell_ticks": cell["vertex_ticks"],
            "vertex_shell_fraction": cell["vertex_ticks"] / (cell["jobs"] * registry.WINDOW),
        }
    return report


if __name__ == "__main__":
    result = analyse()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("EXPLORATORY POST-REGISTERED RESTORING-DRIFT ANALYSIS\n")
    for name, cell in result["cells"].items():
        menu, load, policy = name.split("|")
        if menu != "with_net_zero_groups":
            continue
        crossing = cell["zero_crossing_total"]
        if crossing is None:
            where = "none"
        else:
            where = (f"V={crossing['below_V']} ({crossing['below_mean']:+.4f}) -> "
                     f"V={crossing['above_V']} ({crossing['above_mean']:+.4f})")
        print(f"{load:<14}{policy:<17} late dV={cell['late_window_movement']:+8.3f}  "
              f"blockV={[round(b, 1) for b in cell['block_mean_V']]}  "
              f"vertex={cell['vertex_shell_fraction']:.4f}")
        print(f"    g_T zero crossing: {where}")
    print(f"\nwritten: {OUTPUT}")
