"""Exact finite-state restoring-drift calculation.

Mission sections 13 and 14. The physical world has only 496 admissible lattice
states, so the drift objects of sections 4 and 5 can be computed **exactly by
enumeration** rather than estimated from trajectories. This is the rigorous
object; `restoring_drift_analysis.py` produces the section 6 projection.

No trajectory is run and no model state is advanced. Every quantity is a pure
function evaluation on an individual frozen state, in exact rational
arithmetic. This is a NON-MODEL-ADVANCING STATIC/PURE computation.

Conditioning on the complete state
----------------------------------

The Markov state of the runtime is `(x, B)`: `x` fixes the feasible menu and
every exact EBU value, `B` fixes which of those the affordability gate admits.
The deviation ledger `J` is a pure audit and never feeds back, and the RNG is
counter-addressed and state-independent, so `(x, B)` is Markov-sufficient.

`B` is unbounded, so it is reduced to finitely many regimes rather than
enumerated. For a fixed `x` the affordability of a group depends on `B` only
through the finitely many thresholds `-Delta B_i(G)`, so the gate's behaviour
is piecewise constant in `B`. Two regimes bracket every other:

    POOR    B = 0                  the gate is maximally active
    RICH    B_i >= T(x)_i for all i the gate is entirely inactive

with `T(x)_i = max over feasible G of max(0, -Delta B_i(G))`.

The RICH regime is not a hypothetical: Stage B established that `B` grows
without bound under V1, so it is the regime V1 converges to.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from pathlib import Path

from gaussian_harness.actions import ActionGroup
from gaussian_harness.candidates import MenuSpecification, candidate_groups
from gaussian_harness.feasibility import PhysicalRules, assess
from gaussian_harness.potential import LocalGaussianPotential
from gaussian_harness.valuation import value_group
from homeostasis.harness import MENU_STRICT_PHYSICAL, MENU_WITH_NET_ZERO
from homeostasis.policies import (
    POLICY_CONTROL_RANDOM,
    POLICY_EBU_ALIGNED,
    POLICY_EBU_HOSTILE,
    POLICY_EBU_RANDOM,
)

OUTPUT = Path("results/exploratory/EXACT_STATE_DRIFT.json")

REFERENCE = (10, 10, 10)
SCALES = (1, 1, 1)
MASS = 30
QUANTUM = Fraction(1)

REGIME_POOR = "poor_B_zero"
REGIME_RICH = "rich_gate_inactive"
REGIMES = (REGIME_POOR, REGIME_RICH)


def potential() -> LocalGaussianPotential:
    return LocalGaussianPotential.declare(list(REFERENCE), list(SCALES))


def lattice() -> tuple[tuple[Fraction, ...], ...]:
    """All 496 admissible integer states on the conserved simplex."""
    states = []
    for first in range(MASS + 1):
        for second in range(MASS + 1 - first):
            states.append((Fraction(first), Fraction(second),
                           Fraction(MASS - first - second)))
    return tuple(states)


def menu_groups(menu_rule: str) -> tuple[ActionGroup, ...]:
    rules = PhysicalRules.complete_graph(3)
    groups = candidate_groups(rules, MenuSpecification.declare([QUANTUM], 2))
    if menu_rule == MENU_WITH_NET_ZERO:
        return groups
    return tuple(g for g in groups if any(v != 0 for v in g.increment(3)))


@dataclass(frozen=True)
class StateAnalysis:
    """Exact per-state menu facts, independent of any policy."""

    state: tuple[Fraction, ...]
    potential_value: Fraction
    feasible: tuple[ActionGroup, ...]
    ebu: tuple[Fraction, ...]
    owner_deltas: tuple[dict[int, Fraction], ...]
    threshold: tuple[Fraction, Fraction, Fraction]

    @property
    def affordable_poor(self) -> tuple[int, ...]:
        """Indices affordable from B = 0: every owner delta nonnegative."""
        return tuple(
            index for index, deltas in enumerate(self.owner_deltas)
            if all(value >= 0 for value in deltas.values())
        )

    @property
    def affordable_rich(self) -> tuple[int, ...]:
        return tuple(range(len(self.feasible)))


def analyse_state(pot: LocalGaussianPotential, rules: PhysicalRules,
                  groups: tuple[ActionGroup, ...],
                  state: tuple[Fraction, ...]) -> StateAnalysis:
    feasible, ebu, deltas = [], [], []
    threshold = [Fraction(0), Fraction(0), Fraction(0)]
    for group in groups:
        if not assess(rules, state, group).feasible:
            continue
        valuation = value_group(pot, state, group)
        feasible.append(group)
        ebu.append(valuation.group_ebu)
        owner = valuation.owner_deltas
        deltas.append(owner)
        for index, value in owner.items():
            if value < 0 and -value > threshold[index]:
                threshold[index] = -value
    return StateAnalysis(state, pot.value_total(state), tuple(feasible),
                         tuple(ebu), tuple(deltas), tuple(threshold))


def actor_drift(analysis: StateAnalysis, policy: str, regime: str) -> Fraction | None:
    """D_A(S) = E[V(x') - V(z) | S] = E[-E_G], exactly.

    Returns None when no group is admissible, which is an affordability outcome
    and not a drift value.
    """
    if not analysis.feasible:
        return None
    if policy == POLICY_CONTROL_RANDOM:
        admissible = analysis.affordable_rich          # control applies no gate
    elif regime == REGIME_RICH:
        admissible = analysis.affordable_rich
    else:
        admissible = analysis.affordable_poor
    if not admissible:
        return None
    values = [analysis.ebu[index] for index in admissible]
    if policy == POLICY_EBU_ALIGNED:
        return -max(values)
    if policy == POLICY_EBU_HOSTILE:
        return -min(values)
    total = Fraction(0)
    for value in values:
        total -= value
    return total / len(values)


def forcing_successors(state: tuple[Fraction, ...]) -> tuple[tuple[Fraction, ...], ...]:
    """The six equiprobable raw disturbance outcomes, with NULL_FORCING applied.

    An inadmissible draw leaves the state unchanged, exactly as the registered
    NULL_FORCING rule specifies: recorded, not resampled.
    """
    out = []
    for source in range(3):
        for destination in range(3):
            if source == destination:
                continue
            if state[source] >= QUANTUM:
                moved = list(state)
                moved[source] -= QUANTUM
                moved[destination] += QUANTUM
                out.append(tuple(moved))
            else:
                out.append(state)
    return tuple(out)


def build(menu_rule: str) -> dict:
    pot = potential()
    rules = PhysicalRules.complete_graph(3)
    groups = menu_groups(menu_rule)
    states = lattice()
    index_of = {state: position for position, state in enumerate(states)}
    analyses = [analyse_state(pot, rules, groups, state) for state in states]

    global_threshold = [Fraction(0)] * 3
    for analysis in analyses:
        for index in range(3):
            global_threshold[index] = max(global_threshold[index], analysis.threshold[index])

    policies = (POLICY_CONTROL_RANDOM, POLICY_EBU_RANDOM,
                POLICY_EBU_ALIGNED, POLICY_EBU_HOSTILE)
    result: dict = {
        "menu_rule": menu_rule,
        "states": len(states),
        "groups_in_menu": len(groups),
        "gate_inactive_threshold_per_cell": [str(v) for v in global_threshold],
        "regimes": {},
    }

    for regime in REGIMES:
        # D_A per state, and blocked-state counts.
        per_policy_actor: dict[str, dict[int, Fraction]] = {}
        blocked: dict[str, int] = {}
        for policy in policies:
            drift: dict[int, Fraction] = {}
            count = 0
            for position, analysis in enumerate(analyses):
                value = actor_drift(analysis, policy, regime)
                if value is None:
                    count += 1
                else:
                    drift[position] = value
            per_policy_actor[policy] = drift
            blocked[policy] = count

        # D_T(x) = E_forcing[ dV_ext + D_A(z) ], with the six draws equiprobable.
        per_policy_total: dict[str, dict[int, Fraction]] = {}
        for policy in policies:
            drift = per_policy_actor[policy]
            totals: dict[int, Fraction] = {}
            for position, state in enumerate(states):
                accumulated = Fraction(0)
                usable = 0
                for successor in forcing_successors(state):
                    target = index_of[successor]
                    if target not in drift:
                        continue
                    usable += 1
                    accumulated += (
                        analyses[target].potential_value - analyses[position].potential_value
                        + drift[target]
                    )
                if usable:
                    totals[position] = accumulated / usable
            per_policy_total[policy] = totals

        def summarise(per_state: dict[int, Fraction]) -> list[dict]:
            by_v: dict[int, list[Fraction | int]] = {}
            for position, value in per_state.items():
                key = int(analyses[position].potential_value)
                row = by_v.setdefault(key, [Fraction(0), 0, 0])
                row[0] += value
                row[1] += 1
                row[2] += 1 if value < 0 else 0
            return [
                {"V": key, "states": row[1],
                 "mean": str(row[0] / row[1]),
                 "mean_float": float(row[0] / row[1]),
                 "fraction_restoring": row[2] / row[1]}
                for key, row in sorted(by_v.items())
            ]

        result["regimes"][regime] = {
            "blocked_states": blocked,
            "g_actor": {p: summarise(per_policy_actor[p]) for p in policies},
            "g_total": {p: summarise(per_policy_total[p]) for p in policies},
            "identical_processes": {
                "ebu_random_equals_control": (
                    per_policy_actor[POLICY_EBU_RANDOM] == per_policy_actor[POLICY_CONTROL_RANDOM]
                ),
            },
        }
    return result


if __name__ == "__main__":
    report = {
        "analysis_class": "EXACT_FINITE_STATE_NOT_A_TRAJECTORY",
        "execution_class": "NON-MODEL-ADVANCING STATIC/PURE",
        "menus": {rule: build(rule) for rule in (MENU_WITH_NET_ZERO, MENU_STRICT_PHYSICAL)},
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")

    for rule, block in report["menus"].items():
        print(f"\n===== menu {rule} =====")
        print(f"  lattice states {block['states']}   menu groups {block['groups_in_menu']}")
        print(f"  gate-inactive threshold per cell: {block['gate_inactive_threshold_per_cell']}")
        for regime, data in block["regimes"].items():
            print(f"\n  -- regime {regime} --")
            print(f"     EBU-random identical to control: "
                  f"{data['identical_processes']['ebu_random_equals_control']}")
            print(f"     states with no admissible group: {data['blocked_states']}")
            print(f"     {'V':>4} | " + " | ".join(f"{p[:14]:>14}" for p in
                                                   ("control_random", "ebu_random",
                                                    "ebu_aligned", "ebu_hostile")))
            curves = {p: {r["V"]: r for r in data["g_total"][p]} for p in
                      ("control_random", "ebu_random", "ebu_aligned", "ebu_hostile")}
            for v in (0, 1, 4, 9, 16, 25, 49, 81, 121, 169, 225, 289):
                cells = []
                for p in ("control_random", "ebu_random", "ebu_aligned", "ebu_hostile"):
                    row = curves[p].get(v)
                    cells.append(f"{row['mean_float']:>+14.4f}" if row else f"{'--':>14}")
                print(f"     {v:>4} | " + " | ".join(cells))
    print(f"\nwritten: {OUTPUT}")
