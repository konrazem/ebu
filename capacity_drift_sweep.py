"""Exact restoring drift as a function of accumulated capacity.

Mission section 21. The affordability gate is the only channel through which
capacity can change behaviour, and `exact_state_drift.py` shows the gate is
entirely inactive once every cell holds 29 units. This sweeps the intervening
regimes exactly, at uniform `B_i = b`, to show how the restoring drift decays
as `B` accumulates under Capacity V1.

NON-MODEL-ADVANCING STATIC/PURE: pure function evaluations on frozen individual
states. No trajectory, no tick, no model-state advance.
"""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

from exact_state_drift import (
    MENU_WITH_NET_ZERO,
    analyse_state,
    forcing_successors,
    lattice,
    menu_groups,
    potential,
)
from gaussian_harness.feasibility import PhysicalRules
from homeostasis.policies import (
    POLICY_CONTROL_RANDOM,
    POLICY_EBU_ALIGNED,
    POLICY_EBU_HOSTILE,
    POLICY_EBU_RANDOM,
)

OUTPUT = Path("results/exploratory/CAPACITY_DRIFT_SWEEP.json")
POLICIES = (POLICY_CONTROL_RANDOM, POLICY_EBU_RANDOM,
            POLICY_EBU_ALIGNED, POLICY_EBU_HOSTILE)
LEVELS = (0, 1, 2, 3, 5, 8, 12, 16, 20, 24, 28, 29, 30, 40)
HIGH_DEVIATION = 50     # V threshold for the "large deviation" summary


def admissible(analysis, balance: Fraction, policy: str) -> tuple[int, ...]:
    if policy == POLICY_CONTROL_RANDOM:
        return tuple(range(len(analysis.feasible)))
    return tuple(
        index for index, deltas in enumerate(analysis.owner_deltas)
        if all(balance + value >= 0 for value in deltas.values())
    )


def actor_drift_at(analysis, balance: Fraction, policy: str) -> Fraction | None:
    if not analysis.feasible:
        return None
    chosen = admissible(analysis, balance, policy)
    if not chosen:
        return None
    values = [analysis.ebu[index] for index in chosen]
    if policy == POLICY_EBU_ALIGNED:
        return -max(values)
    if policy == POLICY_EBU_HOSTILE:
        return -min(values)
    total = Fraction(0)
    for value in values:
        total -= value
    return total / len(values)


def sweep() -> dict:
    pot = potential()
    rules = PhysicalRules.complete_graph(3)
    groups = menu_groups(MENU_WITH_NET_ZERO)
    states = lattice()
    index_of = {state: position for position, state in enumerate(states)}
    analyses = [analyse_state(pot, rules, groups, state) for state in states]

    rows = []
    for level in LEVELS:
        balance = Fraction(level)
        entry = {"B_per_cell": level, "policies": {}}
        for policy in POLICIES:
            drift = {}
            for position, analysis in enumerate(analyses):
                value = actor_drift_at(analysis, balance, policy)
                if value is not None:
                    drift[position] = value
            totals = {}
            for position, state in enumerate(states):
                accumulated, usable = Fraction(0), 0
                for successor in forcing_successors(state):
                    target = index_of[successor]
                    if target not in drift:
                        continue
                    usable += 1
                    accumulated += (analyses[target].potential_value
                                    - analyses[position].potential_value
                                    + drift[target])
                if usable:
                    totals[position] = accumulated / usable
            high = [v for p, v in totals.items()
                    if analyses[p].potential_value >= HIGH_DEVIATION]
            everywhere = list(totals.values())
            gated = sum(
                1 for position, analysis in enumerate(analyses)
                if len(admissible(analysis, balance, policy)) < len(analysis.feasible)
            )
            entry["policies"][policy] = {
                "mean_g_total_all_states": float(
                    sum(everywhere, Fraction(0)) / len(everywhere)),
                "mean_g_total_high_deviation": float(
                    sum(high, Fraction(0)) / len(high)) if high else None,
                "fraction_states_restoring": sum(1 for v in everywhere if v < 0) / len(everywhere),
                "states_with_gate_binding": gated,
            }
        rows.append(entry)
    return {
        "analysis_class": "EXACT_FINITE_STATE_NOT_A_TRAJECTORY",
        "execution_class": "NON-MODEL-ADVANCING STATIC/PURE",
        "menu_rule": MENU_WITH_NET_ZERO,
        "high_deviation_threshold_V": HIGH_DEVIATION,
        "levels": rows,
    }


if __name__ == "__main__":
    result = sweep()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("EXACT RESTORING DRIFT versus ACCUMULATED CAPACITY (uniform B per cell)\n")
    print(f"  mean g_T over states with V >= {result['high_deviation_threshold_V']}"
          f"   (negative = restoring)\n")
    print(f"  {'B':>4} | {'control':>10} | {'ebu_random':>11} | {'aligned':>10} | "
          f"{'hostile':>10} | {'gated states (R)':>17}")
    for row in result["levels"]:
        cells = []
        for policy in POLICIES:
            value = row["policies"][policy]["mean_g_total_high_deviation"]
            cells.append(f"{value:>+10.3f}" if value is not None else f"{'--':>10}")
        gated = row["policies"][POLICY_EBU_RANDOM]["states_with_gate_binding"]
        print(f"  {row['B_per_cell']:>4} | {cells[0]:>10} | {cells[1]:>11} | "
              f"{cells[2]:>10} | {cells[3]:>10} | {gated:>17}")
    print(f"\nwritten: {OUTPUT}")
