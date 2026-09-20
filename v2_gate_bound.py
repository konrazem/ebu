"""Exact bound on how far Capacity V2 can lose the affordability gate.

Mission section 21: determine precisely how capacity changes restoring
behaviour, and state the exact hypothesis a future V1-vs-V2 experiment should
test. This is a small local exact analysis, not registered execution: pure
function evaluations on individual frozen states, no tick, no trajectory.

Neither mechanism is modified.

The argument
------------

Under Capacity V1, `B` is unbounded, so the gate provably ends inactive:
`exact_state_drift.py` shows the affordable set equals the feasible set at
every lattice state once `B_i >= 29`, and Stage B measured median `min_i B_i`
above 300.

Under Capacity V2 (`EBU-CAPACITY-V2-DEVIATION-BOUNDED-LOCAL-v1`) the ceiling
is `B_i <= V_i(x_i)` at every observation point. So at a given state the most
permissive capacity V2 can ever present is exactly `B_i = V_i(x_i)`. Evaluating
the drift there is therefore an **upper bound on how much restoring tendency V2
can lose**, at that state, under any history.

This bounds V2 without running it, and without modifying it.
"""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

from capacity_v2 import MODEL_IDENTITY
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

OUTPUT = Path("results/exploratory/V2_GATE_BOUND.json")
POLICIES = (POLICY_CONTROL_RANDOM, POLICY_EBU_RANDOM,
            POLICY_EBU_ALIGNED, POLICY_EBU_HOSTILE)
HIGH_DEVIATION = 50


def ceiling_vector(pot, state) -> tuple[Fraction, ...]:
    """V2's per-cell ceiling B_i <= V_i(x_i), exactly."""
    return tuple(pot.factor_value(state, index) for index in range(len(state)))


def admissible(analysis, balances, policy: str) -> tuple[int, ...]:
    if policy == POLICY_CONTROL_RANDOM:
        return tuple(range(len(analysis.feasible)))
    return tuple(
        index for index, deltas in enumerate(analysis.owner_deltas)
        if all(balances[owner] + value >= 0 for owner, value in deltas.items())
    )


def actor_drift_at(analysis, balances, policy: str) -> Fraction | None:
    if not analysis.feasible:
        return None
    chosen = admissible(analysis, balances, policy)
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


def build() -> dict:
    pot = potential()
    rules = PhysicalRules.complete_graph(3)
    groups = menu_groups(MENU_WITH_NET_ZERO)
    states = lattice()
    index_of = {state: position for position, state in enumerate(states)}
    analyses = [analyse_state(pot, rules, groups, s) for s in states]

    zero = (Fraction(0),) * 3
    saturated = (Fraction(10**6),) * 3     # far past the threshold of 29

    regimes = {
        "v1_zero": [zero] * len(states),
        "v1_saturated": [saturated] * len(states),
        "v2_ceiling": [ceiling_vector(pot, s) for s in states],
    }

    # How often can V2's ceiling even reach the gate-inactivity threshold?
    reachable = 0
    per_cell_reachable = 0
    for position, analysis in enumerate(analyses):
        cap = regimes["v2_ceiling"][position]
        if all(cap[i] >= analysis.threshold[i] for i in range(3)):
            reachable += 1
        per_cell_reachable += sum(1 for i in range(3) if cap[i] >= analysis.threshold[i])

    result: dict = {
        "analysis_class": "EXACT_FINITE_STATE_NOT_A_TRAJECTORY",
        "execution_class": "NON-MODEL-ADVANCING STATIC/PURE",
        "v2_model_identity": MODEL_IDENTITY,
        "states": len(states),
        "states_where_v2_ceiling_can_fully_open_the_gate": reachable,
        "cell_slots_where_v2_ceiling_reaches_threshold": per_cell_reachable,
        "cell_slots_total": 3 * len(states),
        "regimes": {},
    }

    for name, balance_list in regimes.items():
        entry: dict = {}
        for policy in POLICIES:
            drift = {}
            for position, analysis in enumerate(analyses):
                value = actor_drift_at(analysis, balance_list[position], policy)
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
            everywhere = list(totals.values())
            high = [v for p, v in totals.items()
                    if analyses[p].potential_value >= HIGH_DEVIATION]
            entry[policy] = {
                "fraction_states_restoring": sum(1 for v in everywhere if v < 0) / len(everywhere),
                "mean_g_total_high_deviation": float(
                    sum(high, Fraction(0)) / len(high)) if high else None,
                "states_with_gate_binding": sum(
                    1 for position, analysis in enumerate(analyses)
                    if len(admissible(analysis, balance_list[position], policy))
                    < len(analysis.feasible)),
            }
        result["regimes"][name] = entry
    return result


if __name__ == "__main__":
    report = build()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print("EXACT BOUND ON CAPACITY V2 GATE EROSION\n")
    print(f"  V2 model: {report['v2_model_identity']}")
    print(f"  lattice states: {report['states']}")
    print(f"  states where the V2 ceiling can fully open the gate: "
          f"{report['states_where_v2_ceiling_can_fully_open_the_gate']}")
    print(f"  per-cell slots where the ceiling reaches the threshold: "
          f"{report['cell_slots_where_v2_ceiling_reaches_threshold']}"
          f" / {report['cell_slots_total']}")
    print()
    print(f"  {'regime':<16} | {'policy':<16} | {'restoring frac':>14} | "
          f"{'g_T (V>=50)':>12} | {'gated states':>12}")
    for name, entry in report["regimes"].items():
        for policy in POLICIES:
            row = entry[policy]
            value = row["mean_g_total_high_deviation"]
            print(f"  {name:<16} | {policy:<16} | {row['fraction_states_restoring']:>14.3f} | "
                  f"{value:>+12.3f} | {row['states_with_gate_binding']:>12}")
    print(f"\nwritten: {OUTPUT}")
