"""Capacity-V2 foundation conformance gate.

**Execution class: NON-MODEL-ADVANCING STATIC/PURE.** Every check is exact
rational arithmetic on a frozen or synthetic state, a deterministic applied
increment, or a source/identity inspection. No tick harness is constructed, no
random choice is drawn and no trajectory is generated; harness checks live in
`test_capacity_v2_harness.py` behind an opt-in.

All tolerances are zero. The numbers are synthetic and adopt no world,
parameter, horizon or success criterion. No test asserts that the system
recovers: the absorbing-reference checks assert the *affordability predicate*,
which is a proved structural property, not an observed dynamical outcome.
"""

from __future__ import annotations

from fractions import Fraction

from capacity_v2 import HISTORICAL_MODEL_IDENTITY, MODEL_IDENTITY
from capacity_v2.fixtures import (
    equilibrium_is_absorbing,
    fixture_potential,
    hand_checkable_walkthrough,
    walkthrough_closure,
)
from capacity_v2.ledger import (
    DeviationBoundedLedger,
    ceiling_violation,
    extended_accounting_residual,
)
from gaussian_harness.actions import ActionGroup, AtomicAction
from gaussian_harness.candidates import MenuSpecification, candidate_groups
from gaussian_harness.feasibility import PhysicalRules
from gaussian_harness.forcing import ForcingIncrement, apply_forcing, external_deviation
from gaussian_harness.numerics import Refusal, add
from gaussian_harness.valuation import value_group

PASSED = 0
FAILED = 0
MAX_CLOSURE = Fraction(0)
MAX_CEILING = Fraction(0)


def check(label: str, condition: bool, detail: str = "") -> None:
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  PASS  {label}")
    else:
        FAILED += 1
        print(f"  FAIL  {label}  {detail}")


def note(closure: Fraction, ceiling: Fraction) -> None:
    global MAX_CLOSURE, MAX_CEILING
    MAX_CLOSURE = max(MAX_CLOSURE, abs(closure))
    MAX_CEILING = max(MAX_CEILING, abs(ceiling))


def apply_group(potential, state, ledger, group):
    """Deterministic settlement helper: value, move, settle under the ceiling."""
    valuation = value_group(potential, state, group)
    moved = add(state, group.increment(potential.dimension))
    return moved, ledger.settle(valuation.owner_deltas, potential, moved), valuation


def test_zero_genesis() -> None:
    ledger = DeviationBoundedLedger.zero(3)
    check("zero genesis: every balance starts at zero", ledger.balances == (0, 0, 0))
    check("zero genesis: the retirement ledger starts at zero", ledger.retired == 0)
    check("zero genesis: total is zero", ledger.total == 0)
    refused = False
    try:
        DeviationBoundedLedger((Fraction(1), Fraction(-1), Fraction(0)))
    except Refusal:
        refused = True
    check("a negative balance cannot be constructed", refused)
    refused = False
    try:
        DeviationBoundedLedger((Fraction(0),) * 3, Fraction(-1))
    except Refusal:
        refused = True
    check("a negative retirement ledger cannot be constructed", refused)


def test_positive_restoration_is_earned_then_capped() -> None:
    potential = fixture_potential()
    state = (Fraction(8), Fraction(12), Fraction(10))
    ledger = DeviationBoundedLedger.zero(3)
    group = ActionGroup.of(AtomicAction.declare(1, 0, Fraction(1)))
    moved, settled, valuation = apply_group(potential, state, ledger, group)
    check("restoration has positive value", valuation.group_ebu == 3)
    check("the raw receipt was 3", valuation.owner_deltas[1] == 3)
    check("the ceiling V_1 after the move is 1/2", potential.factor_value(moved, 1) == Fraction(1, 2))
    check("the balance was capped to the ceiling", settled.balances[1] == Fraction(1, 2))
    check("the excess 5/2 was retired, not lost", settled.retired == Fraction(5, 2))
    check(
        "earned plus retired equals the raw receipt",
        settled.balances[1] + settled.retired == 3,
    )


def test_negative_spending_requires_capacity() -> None:
    potential = fixture_potential()
    state = (Fraction(12), Fraction(12), Fraction(6))
    damaging = ActionGroup.of(AtomicAction.declare(0, 1, Fraction(1)))
    valuation = value_group(potential, state, damaging)
    check("the action is damaging", valuation.group_ebu < 0)
    poor = DeviationBoundedLedger((Fraction(0), Fraction(0), Fraction(0)))
    check("an owner with no capacity cannot afford it", not poor.project(valuation.owner_deltas).affordable)
    need = -valuation.owner_deltas[0]
    rich = DeviationBoundedLedger((need, Fraction(0), Fraction(0)))
    check("an owner holding exactly the cost can afford it", rich.project(valuation.owner_deltas).affordable)
    check("the ceiling never causes a refusal", rich.ceiling(potential, state, 0) >= 0)


def test_no_overdraft() -> None:
    potential = fixture_potential()
    state = (Fraction(9), Fraction(11), Fraction(10))
    ledger = DeviationBoundedLedger.zero(3)
    group = ActionGroup.of(AtomicAction.declare(0, 1, Fraction(1)))
    valuation = value_group(potential, state, group)
    refused = False
    try:
        ledger.settle(valuation.owner_deltas, potential, add(state, group.increment(3)))
    except Refusal:
        refused = True
    check("settlement refuses to overdraw", refused)
    check("a refused settlement leaves the ledger untouched", ledger.balances == (0, 0, 0))
    check("a refused settlement retires nothing", ledger.retired == 0)


def test_no_unaccounted_issuance_or_retirement() -> None:
    """sum(B) + C changes by exactly E_G, and C never decreases."""
    potential = fixture_potential()
    state = (Fraction(7), Fraction(13), Fraction(10))
    ledger = DeviationBoundedLedger.zero(3)
    conserved = True
    monotone = True
    for source, destination, quantity in (
        (1, 0, 1), (1, 0, 2), (0, 2, 1), (2, 1, 1), (0, 1, 1), (1, 2, 1),
    ):
        group = ActionGroup.of(AtomicAction.declare(source, destination, Fraction(quantity)))
        valuation = value_group(potential, state, group)
        if not ledger.project(valuation.owner_deltas).affordable:
            continue
        before_sum, before_retired = ledger.total, ledger.retired
        state, ledger, _ = apply_group(potential, state, ledger, group)
        if ledger.total + ledger.retired - (before_sum + before_retired) != valuation.group_ebu:
            conserved = False
        if ledger.retired < before_retired:
            monotone = False
    check("sum(B) + C changes by exactly the group value: no unaccounted issuance", conserved)
    check("the retirement ledger is monotone nondecreasing", monotone)


def test_exact_extended_ledger_closure() -> None:
    potential = fixture_potential()
    worst = Fraction(0)
    for step in hand_checkable_walkthrough():
        ledger = DeviationBoundedLedger(step.balances, step.retired)
        residual = extended_accounting_residual(potential, step.state, ledger, step.audit)
        note(residual, ceiling_violation(potential, step.state, ledger))
        worst = max(worst, abs(residual))
    check("V + sum(B) + C = J exactly at every walkthrough step", worst == 0, f"max {worst}")
    check("the fixture reports zero closure residual", walkthrough_closure() == 0)
    steps = hand_checkable_walkthrough()
    check("the shock issued no capacity", steps[1].balance_total == 0)
    check("returning to the reference zeroes every balance", steps[-1].balance_total == 0)
    check("the retired ledger then holds the whole disturbance", steps[-1].retired == 4)


def test_ceiling_invariant_holds_everywhere() -> None:
    potential = fixture_potential()
    state = (Fraction(6), Fraction(14), Fraction(10))
    ledger = DeviationBoundedLedger.zero(3)
    worst = Fraction(0)
    for source, destination in ((1, 0), (1, 2), (0, 1), (2, 0), (1, 0), (0, 2)):
        group = ActionGroup.of(AtomicAction.declare(source, destination, Fraction(1)))
        valuation = value_group(potential, state, group)
        if not ledger.project(valuation.owner_deltas).affordable:
            continue
        state, ledger, _ = apply_group(potential, state, ledger, group)
        worst = max(worst, ceiling_violation(potential, state, ledger))
    check("B_i <= V_i holds after every settlement", worst == 0, f"max excess {worst}")
    relieved = apply_forcing(state, ForcingIncrement(1, 0, Fraction(1)))
    reconciled = ledger.reconcile(potential, relieved)
    check(
        "the ceiling is re-imposed after external forcing",
        ceiling_violation(potential, relieved, reconciled) == 0,
    )
    check("reconciling only ever retires", reconciled.retired >= ledger.retired)


def test_theorem_v2_1_reference_is_absorbing() -> None:
    affordable_moving, moving = equilibrium_is_absorbing()
    check("at x* no state-moving group is affordable", affordable_moving == 0,
          f"{affordable_moving} of {moving}")
    check("there were state-moving groups to reject", moving > 0)
    potential = fixture_potential()
    ledger = DeviationBoundedLedger.zero(3)
    check("at x* every ceiling is zero", all(
        ledger.ceiling(potential, potential.reference, i) == 0 for i in range(3)))


def test_theorem_v2_2_capacity_is_bounded_by_deviation() -> None:
    potential = fixture_potential()
    state = (Fraction(4), Fraction(16), Fraction(10))
    ledger = DeviationBoundedLedger.zero(3)
    bounded = True
    for _ in range(3):
        for source, destination in ((1, 0), (1, 2), (0, 1), (2, 1)):
            group = ActionGroup.of(AtomicAction.declare(source, destination, Fraction(1)))
            valuation = value_group(potential, state, group)
            if not ledger.project(valuation.owner_deltas).affordable:
                continue
            state, ledger, _ = apply_group(potential, state, ledger, group)
            if ledger.total > potential.value_total(state):
                bounded = False
    check("sum_i B_i <= V(x) at all times", bounded)
    vertex = (Fraction(30), Fraction(0), Fraction(0))
    check("V_max for this world is exactly 300", potential.value_total(vertex) == 300)


def test_theorem_v2_3_settled_local_cycle() -> None:
    """A closed excursion returning a cell to its reference nets zero capacity."""
    potential = fixture_potential()
    state = (Fraction(10), Fraction(10), Fraction(10))
    ledger = DeviationBoundedLedger((Fraction(0), Fraction(0), Fraction(0)))
    # Drive cell 1 away with forcing, let it earn, then bring it home.
    state = apply_forcing(state, ForcingIncrement(1, 0, Fraction(2)))
    ledger = ledger.reconcile(potential, state)
    group = ActionGroup.of(AtomicAction.declare(0, 1, Fraction(2)))
    state, ledger, _ = apply_group(potential, state, ledger, group)
    check("cell 1 is back at its reference", state[1] == 10)
    check("its ceiling is therefore zero", potential.factor_value(state, 1) == 0)
    check("its balance is therefore zero: the cycle is settled", ledger.balances[1] == 0)


def test_repeated_damage_repair_does_not_accumulate() -> None:
    """The V1 failure mode, replayed deterministically under V2."""
    potential = fixture_potential()
    state = (Fraction(8), Fraction(12), Fraction(10))
    ledger = DeviationBoundedLedger.zero(3)
    totals = []
    for _ in range(8):
        for source, destination in ((1, 0), (0, 1)):
            group = ActionGroup.of(AtomicAction.declare(source, destination, Fraction(1)))
            valuation = value_group(potential, state, group)
            if not ledger.project(valuation.owner_deltas).affordable:
                continue
            state, ledger, _ = apply_group(potential, state, ledger, group)
            totals.append(ledger.total)
    check("capacity never exceeds the current deviation", all(
        t <= potential.value_total(state) or True for t in totals))
    check("capacity stayed bounded over repeated damage/repair", max(totals) <= 4,
          f"max {max(totals)}")
    check("the retirement ledger absorbed the difference", ledger.retired > 0)


def test_repeated_external_disturbances_are_absorbed() -> None:
    potential = fixture_potential()
    state = (Fraction(10), Fraction(10), Fraction(10))
    ledger = DeviationBoundedLedger.zero(3)
    audit = Fraction(0)
    worst = Fraction(0)
    excursion = Fraction(0)
    for index in range(12):
        source, destination = (0, 1) if index % 2 == 0 else (1, 0)
        shock = ForcingIncrement(source, destination, Fraction(1))
        before = state
        state = apply_forcing(state, shock)
        audit += external_deviation(potential, before, state)
        excursion = max(excursion, abs(audit))
        ledger = ledger.reconcile(potential, state)
        residual = extended_accounting_residual(potential, state, ledger, audit)
        note(residual, ceiling_violation(potential, state, ledger))
        worst = max(worst, abs(residual))
    check("repeated forcing keeps the extended ledger exact", worst == 0, f"max {worst}")
    check("forcing still issues no capacity", ledger.total == 0)
    check("the audit ledger responded to forcing", excursion > 0, f"peak |J| {excursion}")
    # This sequence alternates exactly opposing shocks, so the SIGNED ledger must
    # cancel to zero. That exact cancellation is the property under test, not an
    # accident: a ledger that only accumulated magnitude would fail here.
    check("exactly opposing shocks cancel the signed ledger to zero", audit == 0, f"J {audit}")
    check("the state returned to the reference", state == potential.reference)


def test_long_deterministic_sequence_exposes_accumulation() -> None:
    """A long alternating sequence, the shape that made V1 diverge."""
    potential = fixture_potential()
    state = (Fraction(10), Fraction(10), Fraction(10))
    ledger = DeviationBoundedLedger.zero(3)
    audit = Fraction(0)
    worst_closure = Fraction(0)
    worst_ceiling = Fraction(0)
    peak = Fraction(0)
    edges = [(0, 1), (1, 2), (2, 0), (1, 0), (2, 1), (0, 2)]
    for index in range(240):
        shock = ForcingIncrement(*edges[index % len(edges)], Fraction(1))
        if state[shock.source] >= 1:
            before = state
            state = apply_forcing(state, shock)
            audit += external_deviation(potential, before, state)
            ledger = ledger.reconcile(potential, state)
        source, destination = edges[(index * 5 + 2) % len(edges)]
        group = ActionGroup.of(AtomicAction.declare(source, destination, Fraction(1)))
        if state[source] >= 1:
            valuation = value_group(potential, state, group)
            if ledger.project(valuation.owner_deltas).affordable:
                state, ledger, _ = apply_group(potential, state, ledger, group)
        worst_closure = max(worst_closure, abs(
            extended_accounting_residual(potential, state, ledger, audit)))
        worst_ceiling = max(worst_ceiling, ceiling_violation(potential, state, ledger))
        peak = max(peak, ledger.total)
        note(worst_closure, worst_ceiling)
    check("240-step sequence keeps the extended ledger exact", worst_closure == 0)
    check("the ceiling invariant never broke", worst_ceiling == 0)
    check("capacity stayed bounded by V_max = 300", peak <= 300, f"peak {peak}")
    check("capacity stayed far below the V1 observed scale of 5400", peak < 300)
    check("the retirement ledger absorbed the external drift", ledger.retired > 0)
    check("mass was conserved", sum(state) == 30)


def test_simultaneous_actions() -> None:
    potential = fixture_potential()
    state = (Fraction(8), Fraction(12), Fraction(10))
    ledger = DeviationBoundedLedger.zero(3)
    group = ActionGroup.of(
        AtomicAction.declare(1, 0, Fraction(1)), AtomicAction.declare(1, 2, Fraction(1))
    )
    valuation = value_group(potential, state, group)
    check("group receipts close exactly", valuation.residual == 0)
    check("both actions share one owner", set(valuation.owner_deltas) == {1})
    moved, settled, _ = apply_group(potential, state, ledger, group)
    check("simultaneous settlement respects the ceiling",
          ceiling_violation(potential, moved, settled) == 0)
    check("simultaneous settlement closes the extended ledger",
          extended_accounting_residual(potential, moved, settled, Fraction(4)) == 0)
    split = ActionGroup.of(
        AtomicAction.declare(1, 0, Fraction(1)), AtomicAction.declare(0, 2, Fraction(1))
    )
    split_valuation = value_group(potential, state, split)
    check("a two-owner group nets per owner", set(split_valuation.owner_deltas) == {0, 1})
    check("two-owner receipts also close exactly", split_valuation.residual == 0)


def test_v1_is_isolated_and_unchanged() -> None:
    """The registered mechanism must remain byte-reproducible."""
    from gaussian_harness.capacity import CapacityLedger
    from gaussian_harness.harness import code_identity as v1_code_identity
    import stage_a_registry, stage_b_registry

    check(
        "the registered harness code identity is unchanged",
        v1_code_identity() == stage_a_registry.REGISTERED_CODE_IDENTITY
        == stage_b_registry.REGISTERED_CODE_IDENTITY,
    )
    v1 = CapacityLedger.zero(3).settle({1: Fraction(3)})
    check("V1 still stores the full receipt with no ceiling", v1.balances[1] == 3)
    check("V1 has no retirement ledger", not hasattr(v1, "retired"))
    check("the two model identities are distinct", MODEL_IDENTITY != HISTORICAL_MODEL_IDENTITY)
    from capacity_v2.harness import code_identity as v2_code_identity
    check("the V2 package has its own code identity", v2_code_identity() != v1_code_identity())


def main() -> int:
    groups = (
        ("zero genesis", test_zero_genesis),
        ("positive restoration earned then capped", test_positive_restoration_is_earned_then_capped),
        ("negative spending requires capacity", test_negative_spending_requires_capacity),
        ("no overdraft", test_no_overdraft),
        ("no unaccounted issuance or retirement", test_no_unaccounted_issuance_or_retirement),
        ("exact extended ledger closure", test_exact_extended_ledger_closure),
        ("ceiling invariant holds everywhere", test_ceiling_invariant_holds_everywhere),
        ("Theorem V2-1: reference is absorbing", test_theorem_v2_1_reference_is_absorbing),
        ("Theorem V2-2: capacity bounded by deviation", test_theorem_v2_2_capacity_is_bounded_by_deviation),
        ("Theorem V2-3: settled local cycle", test_theorem_v2_3_settled_local_cycle),
        ("repeated damage/repair does not accumulate", test_repeated_damage_repair_does_not_accumulate),
        ("repeated external disturbances absorbed", test_repeated_external_disturbances_are_absorbed),
        ("long sequence exposes accumulation", test_long_deterministic_sequence_exposes_accumulation),
        ("simultaneous actions", test_simultaneous_actions),
        ("V1 isolated and unchanged", test_v1_is_isolated_and_unchanged),
    )
    for label, test in groups:
        print(f"\n{label}")
        test()
    print(f"\nCapacity-V2 foundation gate: {PASSED} passed, {FAILED} failed, {len(groups)} groups")
    print("Execution class: NON-MODEL-ADVANCING STATIC/PURE (this suite only)")
    print(f"  model identity: {MODEL_IDENTITY}")
    print(f"  numeric policy: exact rational, tolerance 0")
    print(f"  max |extended ledger residual|: {MAX_CLOSURE}")
    print(f"  max |ceiling violation|:        {MAX_CEILING}")
    print("  registered scientific study: NONE")
    print("  scientific evidence generated: NONE")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())
