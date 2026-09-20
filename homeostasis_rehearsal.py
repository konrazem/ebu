"""Local scientific rehearsal for the homeostasis mission.

Mission section 19. **REHEARSAL / NON-CONFIRMATORY.**

Purpose, exactly as the mission states it: artifact generation, analysis
validation, runtime estimation, replay and failure recovery. Its outcomes must
not be used to choose a winning policy, tune a parameter, or select a horizon,
load, seed or threshold. No hypothesis is tested here and no result from this
file may be cited as evidence about EBU.

Two things it is legitimately used for, because both are design questions
rather than outcome selection:

  * runtime and artifact sizing for the registered matrix;
  * measuring the **null-action rate** under both declared menu rules, so the
    open decision in `NET_ZERO_GROUPS_FINDING.md` is put to the author with
    data rather than as an abstraction.

Seeds are derived mechanically from the current commit, never hand-picked.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import subprocess
import time
from fractions import Fraction
from pathlib import Path

from homeostasis.harness import (
    DECLARED_LOADS,
    DECLARED_MENU_RULES,
    MENU_STRICT_PHYSICAL,
    MENU_WITH_NET_ZERO,
    STATUS_AFFORDABILITY_BLOCKED,
    STATUS_EXECUTED,
    STATUS_PHYSICAL_NO_ACTION,
    PolicyRun,
    PolicyWorld,
    code_identity,
    rehearsal_budget,
)
from homeostasis.metrics import exact_median, summarize
from homeostasis.policies import CORE_POLICIES

OUTPUT = Path("results/rehearsal")
REHEARSAL_ID = "EBU-HOMEOSTASIS-REHEARSAL-v1"
STUDY_ID = "ebu-homeostasis-rehearsal"
CONFIGURATION_ID = "cfg-3cell-rehearsal"

HORIZON = 2048
BURN_IN = 512
BLOCK = 512
BLOCKS = 3
SEEDS = 8

REFERENCE = (10, 10, 10)
SCALES = (1, 1, 1)
QUANTA = (1,)


def _commit() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
    ).stdout.strip()


def derive_seed(commit: str, replicate: int, stream: str) -> int:
    """Mechanical seed derivation. No seed is selected or excluded by hand."""
    text = "|".join((REHEARSAL_ID, commit, f"{replicate:03d}", stream))
    return int.from_bytes(hashlib.sha256(text.encode("ascii")).digest()[:8], "big")


def run_one(policy: str, load, menu_rule: str, forcing_seed: int, actor_seed: int) -> dict:
    world = PolicyWorld.declare(
        STUDY_ID, CONFIGURATION_ID, list(REFERENCE), list(SCALES), list(QUANTA),
        policy, menu_rule=menu_rule,
    )
    run = PolicyRun(world, forcing_seed, actor_seed, rehearsal_budget(HORIZON))
    radial: list[Fraction] = []
    in95: list[bool] = []
    in99: list[bool] = []
    statuses: dict[str, int] = {}
    null_actions = 0
    executed = 0
    worst_accounting = Fraction(0)
    worst_conservation = Fraction(0)
    worst_nonnegativity = Fraction(0)
    null_forcing = 0
    applied_forcing = 0
    tie_total = 0

    started = time.time()
    for _ in range(HORIZON):
        record = run.run_tick(load)
        radial.append(record.radial_square)
        in95.append(record.in_h95)
        in99.append(record.in_h99)
        statuses[record.status] = statuses.get(record.status, 0) + 1
        if record.status == STATUS_EXECUTED:
            executed += 1
            tie_total += record.tie_size
            if record.null_action:
                null_actions += 1
        if record.forcing_status == "NULL_FORCING":
            null_forcing += 1
        if record.forcing_status == "APPLIED":
            applied_forcing += 1
        worst_accounting = max(worst_accounting, abs(record.accounting_residual))
        worst_conservation = max(worst_conservation, abs(record.conservation_residual))
        worst_nonnegativity = max(worst_nonnegativity, abs(record.nonnegativity_residual))
        run.records.clear()
    elapsed = time.time() - started

    window = slice(BURN_IN, BURN_IN + BLOCK * BLOCKS)
    summary = summarize(radial[window], in95[window], in99[window], BLOCK, BLOCKS)
    return {
        "policy": policy,
        "load": load.load_id,
        "menu_rule": menu_rule,
        "forcing_seed": forcing_seed,
        "actor_seed": actor_seed,
        "run_id": run.run_id,
        "seconds": round(elapsed, 3),
        "O95": summary.occupancy_95,
        "O99": summary.occupancy_99,
        "mean_V": summary.mean_potential,
        "median_R2": summary.median_radial_square,
        "max_R2": summary.max_radial_square_exact,
        "exits": summary.exits_95,
        "time_outside_95": summary.time_outside_95,
        "excursion_duration_max": summary.excursion_duration_max,
        "return_time_median": summary.return_time_median,
        "block_O95": [block.occupancy_95 for block in summary.blocks],
        "drift_occupancy": summary.drift.occupancy_change,
        "executed": executed,
        "null_actions": null_actions,
        "null_action_rate": Fraction(null_actions, executed) if executed else Fraction(0),
        "mean_tie_size": Fraction(tie_total, executed) if executed else Fraction(0),
        "statuses": statuses,
        "null_forcing": null_forcing,
        "applied_forcing": applied_forcing,
        "max_accounting_residual": worst_accounting,
        "max_conservation_residual": worst_conservation,
        "max_nonnegativity_residual": worst_nonnegativity,
    }


def _encode(value):
    if isinstance(value, Fraction):
        return f"{value.numerator}/{value.denominator}"
    if isinstance(value, dict):
        return {k: _encode(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_encode(v) for v in value]
    return value


def execute() -> dict:
    commit = _commit()
    rows: list[dict] = []
    total = len(CORE_POLICIES) * len(DECLARED_LOADS) * len(DECLARED_MENU_RULES) * SEEDS
    done = 0
    started = time.time()
    for menu_rule in DECLARED_MENU_RULES:
        for load in DECLARED_LOADS:
            for policy in CORE_POLICIES:
                for replicate in range(SEEDS):
                    rows.append(run_one(
                        policy, load, menu_rule,
                        derive_seed(commit, replicate, "FORCING"),
                        derive_seed(commit, replicate, "ACTOR"),
                    ))
                    done += 1
            print(f"  {menu_rule} {load.load_id}: {done}/{total} runs", flush=True)
    wall = time.time() - started

    # Replay check: one configuration re-run must be bit-identical.
    probe = rows[0]
    replay = run_one(probe["policy"], DECLARED_LOADS[0], probe["menu_rule"],
                     probe["forcing_seed"], probe["actor_seed"])
    deterministic = all(
        _encode(replay[key]) == _encode(probe[key])
        for key in ("run_id", "O95", "O99", "median_R2", "max_R2", "executed",
                    "null_actions", "exits", "block_O95")
    )

    payload = {
        "rehearsal_id": REHEARSAL_ID,
        "class": "REHEARSAL / NON-CONFIRMATORY",
        "commit": commit,
        "code_identity": code_identity(),
        "horizon": HORIZON,
        "burn_in": BURN_IN,
        "block": BLOCK,
        "blocks": BLOCKS,
        "seeds": SEEDS,
        "runs": total,
        "wall_seconds": round(wall, 1),
        "ticks": total * HORIZON,
        "replay_deterministic": deterministic,
        "rows": [_encode(row) for row in rows],
        "non_claims": [
            "rehearsal only; not confirmatory evidence about any policy",
            "no outcome here selects a policy, horizon, load, seed or threshold",
        ],
    }
    OUTPUT.mkdir(parents=True, exist_ok=True)
    path = OUTPUT / "HOMEOSTASIS_REHEARSAL.json.gz"
    path.write_bytes(gzip.compress(
        (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode(), mtime=0))

    # Console summary, aggregated over seeds.
    print(f"\nreplay deterministic: {deterministic}")
    print(f"wall: {wall:.0f}s for {total} runs ({total*HORIZON} ticks)")
    worst = max(max(row["max_accounting_residual"], row["max_conservation_residual"],
                    row["max_nonnegativity_residual"]) for row in rows)
    print(f"worst residual across every run: {worst}")
    for menu_rule in DECLARED_MENU_RULES:
        print(f"\n=== menu: {menu_rule} ===")
        print(f"{'load':<14}{'policy':<17}{'O95':>9}{'O99':>9}{'medR2':>8}{'maxR2':>7}"
              f"{'null%':>8}{'exits':>7}{'block O95 trend':>26}")
        for load in DECLARED_LOADS:
            for policy in CORE_POLICIES:
                group = [r for r in rows if r["menu_rule"] == menu_rule
                         and r["load"] == load.load_id and r["policy"] == policy]
                o95 = exact_median([r["O95"] for r in group])
                o99 = exact_median([r["O99"] for r in group])
                med = exact_median([r["median_R2"] for r in group])
                mx = exact_median([r["max_R2"] for r in group])
                nr = exact_median([r["null_action_rate"] for r in group])
                ex = exact_median([Fraction(r["exits"]) for r in group])
                trend = [float(exact_median([r["block_O95"][i] for r in group])) for i in range(BLOCKS)]
                print(f"{load.load_id:<14}{policy:<17}{float(o95):>9.4f}{float(o99):>9.4f}"
                      f"{float(med):>8.1f}{float(mx):>7.0f}{float(nr)*100:>7.1f}%{float(ex):>7.0f}"
                      f"   {trend[0]:.4f} {trend[1]:.4f} {trend[2]:.4f}")
    print(f"\nwritten: {path}")
    print("CLASS: REHEARSAL / NON-CONFIRMATORY")
    return payload


if __name__ == "__main__":
    execute()
