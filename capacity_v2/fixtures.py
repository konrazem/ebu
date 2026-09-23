"""Hand-checkable three-cell fixture for Capacity V2.

Same world as the V1 fixture: x* = (10,10,10), sigma = (1,1,1), M = 30, so
V(x) = (1/2) sum_i (x_i - 10)^2. Every number below can be checked by hand.

The walkthrough demonstrates the property V1 could not produce: after the
disturbance is repaired, every ceiling is zero, so every balance is zero, and
no damaging action is affordable. The reference is absorbing.

These numbers are synthetic and adopt no world, parameter or success criterion.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from gaussian_harness.actions import ActionGroup, AtomicAction
from gaussian_harness.forcing import ForcingIncrement, apply_forcing, external_deviation
from gaussian_harness.numerics import Vector, add
from gaussian_harness.potential import LocalGaussianPotential
from gaussian_harness.valuation import value_group

from .ledger import DeviationBoundedLedger, extended_accounting_residual

DECLARED_MASS = Fraction(30)


def fixture_potential() -> LocalGaussianPotential:
    return LocalGaussianPotential.declare([10, 10, 10], [1, 1, 1])


@dataclass(frozen=True)
class WalkStep:
    label: str
    state: Vector
    potential_value: Fraction
    balances: tuple[Fraction, ...]
    retired: Fraction
    audit: Fraction
    note: str

    @property
    def balance_total(self) -> Fraction:
        result = Fraction(0)
        for balance in self.balances:
            result += balance
        return result

    @property
    def closure(self) -> Fraction:
        """V + sum(B) + C - J, which must be exactly zero."""
        return self.potential_value + self.balance_total + self.retired - self.audit


def hand_checkable_walkthrough() -> list[WalkStep]:
    """Replay the demonstration points as pure arithmetic. No tick harness."""
    potential = fixture_potential()
    steps: list[WalkStep] = []
    state: Vector = (Fraction(10), Fraction(10), Fraction(10))
    ledger = DeviationBoundedLedger.zero(3)
    audit = Fraction(0)

    def record(label: str, note: str) -> None:
        steps.append(
            WalkStep(label, state, potential.value_total(state),
                     ledger.balances, ledger.retired, audit, note)
        )

    record("equilibrium", "x = x*, V = 0, every balance and the retirement ledger zero")

    shock = ForcingIncrement(0, 1, Fraction(2))
    before = state
    state = apply_forcing(state, shock)
    audit += external_deviation(potential, before, state)
    ledger = ledger.reconcile(potential, state)
    record("shock", "nature moved 2 from cell 0 to cell 1; J = 4, no capacity issued")

    group = ActionGroup.of(AtomicAction.declare(1, 0, Fraction(1)))
    valuation = value_group(potential, state, group)
    state = add(state, group.increment(3))
    ledger = ledger.settle(valuation.owner_deltas, potential, state)
    record("restore-1", "owner 1 earned E = 3 but its ceiling V_1 fell to 1/2, retiring 5/2")

    group = ActionGroup.of(AtomicAction.declare(1, 0, Fraction(1)))
    valuation = value_group(potential, state, group)
    state = add(state, group.increment(3))
    ledger = ledger.settle(valuation.owner_deltas, potential, state)
    record("restore-2", "back at x*: every ceiling is 0, so every balance is 0 and C = 4")

    return steps


def equilibrium_is_absorbing() -> tuple[int, int]:
    """At x* with zero balances, count affordable groups that actually move x.

    Returns (groups moving x that are affordable, total groups moving x).
    The first number is zero: that is Theorem V2-1.
    """
    from gaussian_harness.candidates import MenuSpecification, candidate_groups
    from gaussian_harness.feasibility import PhysicalRules

    potential = fixture_potential()
    rules = PhysicalRules.complete_graph(3)
    menu = MenuSpecification.declare([1], 2)
    state = potential.reference
    ledger = DeviationBoundedLedger.zero(3)

    moving = affordable_moving = 0
    for group in candidate_groups(rules, menu):
        if group.increment(3) == (Fraction(0), Fraction(0), Fraction(0)):
            continue
        moving += 1
        valuation = value_group(potential, state, group)
        if ledger.project(valuation.owner_deltas).affordable:
            affordable_moving += 1
    return affordable_moving, moving


def walkthrough_closure() -> Fraction:
    """Maximum absolute extended-ledger residual over the walk."""
    potential = fixture_potential()
    worst = Fraction(0)
    for step in hand_checkable_walkthrough():
        ledger = DeviationBoundedLedger(step.balances, step.retired)
        worst = max(
            worst,
            abs(extended_accounting_residual(potential, step.state, ledger, step.audit)),
        )
    return worst
