"""Restoring-tendency foundation conformance gate.

Covers mission sections 3 (canonical tick decomposition), 4 and 5 (actor and
total drift), 13 (exact finite-state analysis) and 18 levels 0-2.

**Execution class: NON-MODEL-ADVANCING STATIC/PURE.** Every check is a pure
function evaluation on synthetic or enumerated individual states, or an exact
rational identity. No tick is advanced and no trajectory is generated; an AST
check over this file asserts it calls no transition entry point.

All arithmetic is exact rational with tolerance zero.

**No science is adopted here.** No check asserts that any policy restores, and
no drift sign is required of any arm. The signs that appear are computed, not
demanded.
"""

from __future__ import annotations

import ast
from fractions import Fraction

from exact_state_drift import (
    REGIME_POOR,
    REGIME_RICH,
    StateAnalysis,
    actor_drift,
    analyse_state,
    forcing_successors,
    lattice,
    menu_groups,
    potential,
)
from gaussian_harness.actions import ActionGroup, AtomicAction
from gaussian_harness.feasibility import PhysicalRules
from gaussian_harness.forcing import ForcingIncrement, apply_forcing, external_deviation
from gaussian_harness.numerics import add
from gaussian_harness.valuation import value_group
from homeostasis.harness import MENU_STRICT_PHYSICAL, MENU_WITH_NET_ZERO
from homeostasis.policies import (
    POLICY_CONTROL_RANDOM,
    POLICY_EBU_ALIGNED,
    POLICY_EBU_HOSTILE,
    POLICY_EBU_RANDOM,
)

PASSED = 0
FAILED = 0


def check(label: str, condition: bool, detail: str = "") -> None:
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  PASS  {label}")
    else:
        FAILED += 1
        print(f"  FAIL  {label}{(' -- ' + detail) if detail else ''}")


def _state(*values) -> tuple[Fraction, ...]:
    return tuple(Fraction(v) for v in values)


# --------------------------------------------------------------------------
# Section 3 -- the canonical tick decomposition
# --------------------------------------------------------------------------


def test_tick_decomposition_is_exact() -> None:
    """x_t -> z_t -> x_{t+1}, with dV_actor = -E and dV_total = dV_ext + dV_actor."""
    pot = potential()
    rules = PhysicalRules.complete_graph(3)
    groups = menu_groups(MENU_WITH_NET_ZERO)
    worst = Fraction(0)
    checked = 0
    for start in (_state(10, 10, 10), _state(12, 9, 9), _state(20, 5, 5), _state(6, 12, 12)):
        for forcing in (ForcingIncrement(0, 1, Fraction(1)),
                        ForcingIncrement(2, 0, Fraction(1)),
                        ForcingIncrement(1, 2, Fraction(1))):
            if start[forcing.source] < forcing.magnitude:
                continue
            frozen = apply_forcing(start, forcing)
            d_ext = external_deviation(pot, start, frozen)
            check_ext = pot.value_total(frozen) - pot.value_total(start)
            worst = max(worst, abs(d_ext - check_ext))
            for group in groups:
                from gaussian_harness.feasibility import assess
                if not assess(rules, frozen, group).feasible:
                    continue
                valuation = value_group(pot, frozen, group)
                after = add(frozen, group.increment(3))
                d_actor = pot.value_total(after) - pot.value_total(frozen)
                d_total = pot.value_total(after) - pot.value_total(start)
                checked += 1
                if d_actor != -valuation.group_ebu:
                    worst = max(worst, abs(d_actor + valuation.group_ebu))
                if d_total != d_ext + d_actor:
                    worst = max(worst, abs(d_total - d_ext - d_actor))
    check(f"dV_actor = -E_G on {checked} state/group pairs", worst == 0, str(worst))
    check("the decomposition was exercised on many pairs", checked > 200, str(checked))


def test_external_and_actor_contributions_separate() -> None:
    """A tick with no forcing has dV_ext = 0; an inert group has dV_actor = 0."""
    pot = potential()
    start = _state(12, 9, 9)
    check("no forcing gives zero external contribution",
          external_deviation(pot, start, start) == 0)
    inert = ActionGroup.of(AtomicAction.declare(0, 1, 1), AtomicAction.declare(1, 0, 1))
    valuation = value_group(pot, start, inert)
    after = add(start, inert.increment(3))
    check("a net-zero group has zero actor contribution",
          pot.value_total(after) - pot.value_total(start) == 0)
    check("and zero EBU", valuation.group_ebu == 0)
    check("so dV_actor = -E holds trivially there",
          pot.value_total(after) - pot.value_total(start) == -valuation.group_ebu)


# --------------------------------------------------------------------------
# Section 18 level 1 -- signal validity
# --------------------------------------------------------------------------


def test_aligned_minimises_post_action_potential() -> None:
    """arg max E_G equals arg min V_post on one frozen candidate set."""
    pot = potential()
    rules = PhysicalRules.complete_graph(3)
    groups = menu_groups(MENU_WITH_NET_ZERO)
    mismatches = 0
    states_checked = 0
    for state in lattice()[::7]:
        analysis = analyse_state(pot, rules, groups, state)
        if not analysis.feasible:
            continue
        states_checked += 1
        best_ebu = max(analysis.ebu)
        posts = [pot.value_total(add(state, g.increment(3))) for g in analysis.feasible]
        least_post = min(posts)
        by_ebu = {i for i, e in enumerate(analysis.ebu) if e == best_ebu}
        by_post = {i for i, p in enumerate(posts) if p == least_post}
        if by_ebu != by_post:
            mismatches += 1
    check(f"arg max E = arg min V_post on {states_checked} states", mismatches == 0,
          str(mismatches))


def test_aligned_acts_even_when_every_candidate_is_damaging() -> None:
    pot = potential()
    rules = PhysicalRules.complete_graph(3)
    groups = menu_groups(MENU_STRICT_PHYSICAL)
    reference = _state(10, 10, 10)
    analysis = analyse_state(pot, rules, groups, reference)
    check("every strict-menu candidate at the reference is damaging",
          all(value < 0 for value in analysis.ebu), str(sorted(set(analysis.ebu))))
    drift = actor_drift(analysis, POLICY_EBU_ALIGNED, REGIME_RICH)
    check("aligned still acts and takes the least damaging", drift == -max(analysis.ebu))
    check("which is a strictly positive outward move, not a no-op", drift > 0)


# --------------------------------------------------------------------------
# Sections 4, 5, 13, 14 -- exact drift objects
# --------------------------------------------------------------------------


def test_random_drift_is_the_exact_menu_average() -> None:
    """D_A^R(S) = (1/|A|) sum_G [V(T_G S) - V(S)], computed exactly."""
    pot = potential()
    rules = PhysicalRules.complete_graph(3)
    groups = menu_groups(MENU_WITH_NET_ZERO)
    state = _state(14, 8, 8)
    analysis = analyse_state(pot, rules, groups, state)
    direct = Fraction(0)
    for group in analysis.feasible:
        direct += pot.value_total(add(state, group.increment(3))) - pot.value_total(state)
    direct /= len(analysis.feasible)
    check("control drift equals the direct menu average of V changes",
          actor_drift(analysis, POLICY_CONTROL_RANDOM, REGIME_RICH) == direct, str(direct))
    check("and equals minus the mean EBU",
          direct == -sum(analysis.ebu, Fraction(0)) / len(analysis.ebu))


def test_gate_inactivity_threshold_and_process_identity() -> None:
    """Above the threshold the gate never binds, so EBU-random *is* control."""
    pot = potential()
    rules = PhysicalRules.complete_graph(3)
    for menu_rule in (MENU_WITH_NET_ZERO, MENU_STRICT_PHYSICAL):
        groups = menu_groups(menu_rule)
        analyses = [analyse_state(pot, rules, groups, s) for s in lattice()]
        threshold = max(max(a.threshold) for a in analyses)
        check(f"{menu_rule}: gate-inactive threshold is 29", threshold == 29, str(threshold))
        rich_random = {i: actor_drift(a, POLICY_EBU_RANDOM, REGIME_RICH)
                       for i, a in enumerate(analyses)}
        rich_control = {i: actor_drift(a, POLICY_CONTROL_RANDOM, REGIME_RICH)
                        for i, a in enumerate(analyses)}
        check(f"{menu_rule}: with the gate inactive EBU-random equals control",
              rich_random == rich_control)
        poor_random = {i: actor_drift(a, POLICY_EBU_RANDOM, REGIME_POOR)
                       for i, a in enumerate(analyses)}
        check(f"{menu_rule}: with B = 0 they differ", poor_random != rich_random)


def test_forcing_successors_respect_null_forcing() -> None:
    """An inadmissible draw leaves the state unchanged; it is not resampled."""
    starved = _state(0, 15, 15)
    successors = forcing_successors(starved)
    check("six equiprobable raw outcomes are always produced", len(successors) == 6)
    unchanged = sum(1 for s in successors if s == starved)
    check("the two draws out of the empty cell are null", unchanged == 2, str(unchanged))
    healthy = _state(10, 10, 10)
    check("no draw is null when every cell is stocked",
          all(s != healthy for s in forcing_successors(healthy)))


def test_lattice_and_menu_are_the_registered_world() -> None:
    check("the lattice has 496 admissible states", len(lattice()) == 496)
    check("the registered menu has 21 groups", len(menu_groups(MENU_WITH_NET_ZERO)) == 21)
    check("the strict menu has 18", len(menu_groups(MENU_STRICT_PHYSICAL)) == 18)


# --------------------------------------------------------------------------
# Guards
# --------------------------------------------------------------------------


def test_no_transition_is_called() -> None:
    tree = ast.parse(open(__file__, encoding="utf-8").read())
    called = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            target = node.func
            called.add(target.attr if isinstance(target, ast.Attribute)
                       else getattr(target, "id", ""))
    banned = {"run_tick", "run_trajectory", "recovery_trial", "run_job", "PolicyRun", "Run"}
    leaked = called & banned
    check("no transition entry point is called in this suite", not leaked, str(leaked))


def test_no_restoring_outcome_is_required() -> None:
    """This suite must not assert that any policy restores.

    Scanned by AST rather than by text search, and with this function's own
    body excluded -- a guard that greps for its own subject matter always
    trips on itself.
    """
    tree = ast.parse(open(__file__, encoding="utf-8").read())
    guard = "test_no_restoring_outcome_is_required"
    demands: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == guard:
            continue
        if not isinstance(node, ast.FunctionDef):
            continue
        for inner in ast.walk(node):
            if not isinstance(inner, ast.Compare) or len(inner.ops) != 1:
                continue
            if not isinstance(inner.ops[0], ast.Lt):
                continue
            right = inner.comparators[0]
            if not (isinstance(right, ast.Constant) and right.value == 0):
                continue
            rendered = ast.unparse(inner.left)
            if any(word in rendered for word in ("drift", "g_total", "g_actor")):
                demands.append(f"{node.name}: {ast.unparse(inner)}")
    check("no check demands a negative drift from any policy", not demands, str(demands))


def main() -> int:
    groups = (
        ("tick decomposition is exact", test_tick_decomposition_is_exact),
        ("external and actor contributions separate",
         test_external_and_actor_contributions_separate),
        ("aligned minimises post-action potential",
         test_aligned_minimises_post_action_potential),
        ("aligned acts when every candidate is damaging",
         test_aligned_acts_even_when_every_candidate_is_damaging),
        ("random drift is the exact menu average",
         test_random_drift_is_the_exact_menu_average),
        ("gate inactivity threshold and process identity",
         test_gate_inactivity_threshold_and_process_identity),
        ("forcing successors respect NULL_FORCING",
         test_forcing_successors_respect_null_forcing),
        ("lattice and menu are the registered world",
         test_lattice_and_menu_are_the_registered_world),
        ("no transition is called", test_no_transition_is_called),
        ("no restoring outcome is required", test_no_restoring_outcome_is_required),
    )
    for label, test in groups:
        print(f"\n{label}")
        test()
    print(f"\nRestoring-tendency gate: {PASSED} passed, {FAILED} failed, {len(groups)} groups")
    print("Execution class: NON-MODEL-ADVANCING STATIC/PURE (this suite only)")
    print("  numeric policy: exact rational, tolerance 0")
    print("  scientific trajectories generated: 0")
    print("  scientific evidence generated: NONE")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())
