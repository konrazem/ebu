"""Hand-checkable three-cell fixture.

Every number below can be verified manually with pencil and paper. The world
has three cells, reference x* = (10, 10, 10), scales sigma = (1, 1, 1) and
declared mass M = 30, so

    V(x) = 1/2 * sum_i (x_i - 10)^2.

The walkthrough demonstrates, in order: equilibrium; a conservative external
shock; positive deviation; no capacity issuance from the shock; a restorative
action earning capacity; a later damaging action spending it; overdraft
rejection; and exact V + sum(B) = J closure at every step.

These numbers are synthetic. They exercise arithmetic and mechanism only and
adopt no world, parameter, horizon or success criterion.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from .actions import ActionGroup, AtomicAction
from .capacity import CapacityLedger
from .forcing import (
    ForcingIncrement,
    accounting_residual,
    apply_forcing,
    conservation_residual,
    external_deviation,
)
from .numerics import Refusal, Vector, add
from .potential import LocalGaussianPotential
from .valuation import value_group

DECLARED_MASS = Fraction(30)


def fixture_potential() -> LocalGaussianPotential:
    return LocalGaussianPotential.declare([10, 10, 10], [1, 1, 1])


@dataclass(frozen=True)
class WalkStep:
    label: str
    state: Vector
    potential_value: Fraction
    balances: tuple[Fraction, ...]
    audit: Fraction
    note: str

    @property
    def balance_total(self) -> Fraction:
        result = Fraction(0)
        for balance in self.balances:
            result += balance
        return result


def hand_checkable_walkthrough() -> list[WalkStep]:
    """Replay the eight demonstration points as pure arithmetic.

    No tick harness, runner or trajectory is involved: each step applies a
    declared increment and evaluates the declared identities.
    """
    potential = fixture_potential()
    steps: list[WalkStep] = []

    state: Vector = (Fraction(10), Fraction(10), Fraction(10))
    ledger = CapacityLedger.zero(3)
    audit = Fraction(0)

    def record(label: str, note: str) -> None:
        steps.append(
            WalkStep(
                label,
                state,
                potential.value_total(state),
                ledger.balances,
                audit,
                note,
            )
        )

    # 1. Equilibrium: x = x*, V = 0, B = 0, J = 0.
    record("equilibrium", "x = x*, V = 0, all balances zero, audit zero")

    # 2/3/4. One conservative shock moves 2 from cell 0 to cell 1.
    # It raises deviation to 4 and credits no balance.
    shock = ForcingIncrement(0, 1, Fraction(2))
    before = state
    state = apply_forcing(state, shock)
    audit += external_deviation(potential, before, state)
    record("shock", "nature moved 2 from cell 0 to cell 1; J = 4, every B still 0")

    # 5. Cell 1 restores 1 unit to cell 0 and earns capacity.
    group = ActionGroup.of(AtomicAction.declare(1, 0, Fraction(1)))
    valuation = value_group(potential, state, group)
    ledger = ledger.settle(valuation.owner_deltas)
    state = add(state, group.increment(3))
    record("restore-1", "cell 1 moved 1 to cell 0; E = +3 earned by owner 1")

    # A second restoration returns the world exactly to the reference.
    group = ActionGroup.of(AtomicAction.declare(1, 0, Fraction(1)))
    valuation = value_group(potential, state, group)
    ledger = ledger.settle(valuation.owner_deltas)
    state = add(state, group.increment(3))
    record("restore-2", "cell 1 moved 1 more; V = 0, owner 1 holds the whole audit")

    # 6. Cell 1 now spends earned capacity on a damaging action.
    group = ActionGroup.of(AtomicAction.declare(1, 2, Fraction(1)))
    valuation = value_group(potential, state, group)
    ledger = ledger.settle(valuation.owner_deltas)
    state = add(state, group.increment(3))
    record("spend", "cell 1 moved 1 to cell 2; E = -1 financed by earned capacity")

    return steps


def overdraft_attempt() -> tuple[Fraction, tuple[int, ...]]:
    """7. An owner with zero capacity cannot afford a damaging action.

    Returns the refused group's value and the deficient owners. The ledger is
    not mutated, so no partial debit occurs.
    """
    potential = fixture_potential()
    state = (Fraction(9), Fraction(11), Fraction(10))
    ledger = CapacityLedger.zero(3)
    group = ActionGroup.of(AtomicAction.declare(0, 1, Fraction(1)))
    valuation = value_group(potential, state, group)
    decision = ledger.is_affordable(valuation)
    if decision.affordable:
        raise Refusal("fixture expected the overdraft to be refused")
    return valuation.group_ebu, decision.deficient_owners


def walkthrough_residuals() -> tuple[Fraction, Fraction]:
    """8. Maximum absolute accounting and conservation residuals over the walk."""
    potential = fixture_potential()
    worst_accounting = Fraction(0)
    worst_conservation = Fraction(0)
    for step in hand_checkable_walkthrough():
        ledger = CapacityLedger(step.balances)
        accounting = abs(
            accounting_residual(potential, step.state, ledger, step.audit)
        )
        conservation = abs(conservation_residual(step.state, DECLARED_MASS))
        worst_accounting = max(worst_accounting, accounting)
        worst_conservation = max(worst_conservation, conservation)
    return worst_accounting, worst_conservation
