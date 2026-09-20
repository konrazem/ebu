"""Deviation-bounded local capacity with an explicit retirement ledger."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Mapping

from gaussian_harness.capacity import AffordabilityDecision
from gaussian_harness.numerics import Refusal, Vector
from gaussian_harness.potential import LocalGaussianPotential

CAPACITY_RULE_ID = "EBU-GAUSSIAN-CAPACITY-V2-DBLC-v1"


@dataclass(frozen=True)
class DeviationBoundedLedger:
    """Per-owner capacity capped by the owner's own local potential.

    `retired` is a monotone nondecreasing sink. It exists so that capacity which
    stops being spendable is still accounted for: nothing disappears
    unaccounted, which is the requirement the V1 identity was standing in for.
    """

    balances: tuple[Fraction, ...]
    retired: Fraction = Fraction(0)

    def __post_init__(self) -> None:
        for owner, balance in enumerate(self.balances):
            if balance < 0:
                raise Refusal(f"owner {owner} holds a negative balance")
        if self.retired < 0:
            raise Refusal("retired capacity must be nonnegative")

    @classmethod
    def zero(cls, cells: int) -> "DeviationBoundedLedger":
        if cells <= 0:
            raise Refusal("cell count must be positive")
        return cls(tuple(Fraction(0) for _ in range(cells)), Fraction(0))

    @property
    def total(self) -> Fraction:
        result = Fraction(0)
        for balance in self.balances:
            result += balance
        return result

    def project(self, owner_deltas: Mapping[int, Fraction]) -> AffordabilityDecision:
        """Affordability is unchanged from V1: no owner may go into debt.

        The ceiling is deliberately NOT part of affordability. It applies after
        settlement, so it can never cause a refusal and can never make an
        otherwise legal action illegal.
        """
        projected: list[tuple[int, Fraction]] = []
        deficient: list[int] = []
        for owner in sorted(owner_deltas):
            if not 0 <= owner < len(self.balances):
                raise Refusal(f"owner {owner} is not a declared cell")
            balance = self.balances[owner] + owner_deltas[owner]
            projected.append((owner, balance))
            if balance < 0:
                deficient.append(owner)
        return AffordabilityDecision(not deficient, tuple(projected), tuple(deficient))

    def is_affordable(self, valuation) -> AffordabilityDecision:
        return self.project(valuation.owner_deltas)

    def ceiling(self, potential: LocalGaussianPotential, state: Vector, owner: int) -> Fraction:
        """Phi_i = V_i(x_i): the deviation this cell is currently carrying."""
        return potential.factor_value(state, owner)

    def reconcile(
        self, potential: LocalGaussianPotential, state: Vector
    ) -> "DeviationBoundedLedger":
        """Re-impose `B_i <= V_i(x_i)`, retiring any excess.

        Called after every state change, including external forcing, because
        forcing moves `x` and therefore moves each ceiling.
        """
        balances = list(self.balances)
        retired = self.retired
        for owner, balance in enumerate(balances):
            limit = self.ceiling(potential, state, owner)
            if balance > limit:
                retired += balance - limit
                balances[owner] = limit
        return DeviationBoundedLedger(tuple(balances), retired)

    def settle(
        self,
        owner_deltas: Mapping[int, Fraction],
        potential: LocalGaussianPotential,
        state_after: Vector,
    ) -> "DeviationBoundedLedger":
        """Atomic all-or-nothing settlement, then the ceiling.

        The affordability decision is taken before any value is written, so a
        refused group leaves the ledger untouched.
        """
        decision = self.project(owner_deltas)
        if not decision.affordable:
            raise Refusal(
                f"AFFORDABILITY_REFUSED: owners {decision.deficient_owners} would go into debt"
            )
        balances = list(self.balances)
        for owner, balance in decision.projected:
            balances[owner] = balance
        return DeviationBoundedLedger(tuple(balances), self.retired).reconcile(
            potential, state_after
        )


def extended_accounting_residual(
    potential: LocalGaussianPotential,
    state: Vector,
    ledger: DeviationBoundedLedger,
    audit: Fraction,
    constant: Fraction = Fraction(0),
) -> Fraction:
    """V(x) + sum_i B_i + C - J - K. Zero under the declared update rules."""
    return potential.value_total(state) + ledger.total + ledger.retired - audit - constant


def ceiling_violation(
    potential: LocalGaussianPotential,
    state: Vector,
    ledger: DeviationBoundedLedger,
) -> Fraction:
    """Largest amount by which the invariant B_i <= V_i is exceeded, or zero."""
    worst = Fraction(0)
    for owner, balance in enumerate(ledger.balances):
        excess = balance - potential.factor_value(state, owner)
        if excess > worst:
            worst = excess
    return worst


@dataclass(frozen=True)
class SignedShadowLedgerV2:
    """Signed shadow accounting for the physical-random control arm.

    The control applies no affordability gate, so its owner accounts are not a
    capacity constraint and may go negative. Settlement therefore never refuses.

    The deviation ceiling is still applied on the positive side, so the control
    is measured under the same state law as the treatment and the extended
    identity `V + sum(B) + C = J` closes in both arms. A negative balance is
    below every ceiling and passes through untouched.

    This is a scientific control's measurement ledger, not an inferior capacity
    engine. Nothing here refuses and nothing here is spent.
    """

    balances: tuple[Fraction, ...]
    retired: Fraction = Fraction(0)

    @classmethod
    def zero(cls, cells: int) -> "SignedShadowLedgerV2":
        if cells <= 0:
            raise Refusal("cell count must be positive")
        return cls(tuple(Fraction(0) for _ in range(cells)), Fraction(0))

    @property
    def total(self) -> Fraction:
        result = Fraction(0)
        for balance in self.balances:
            result += balance
        return result

    def project(self, owner_deltas: Mapping[int, Fraction]) -> AffordabilityDecision:
        """Reported for comparison only; the control never filters on it."""
        projected: list[tuple[int, Fraction]] = []
        deficient: list[int] = []
        for owner in sorted(owner_deltas):
            if not 0 <= owner < len(self.balances):
                raise Refusal(f"owner {owner} is not a declared cell")
            balance = self.balances[owner] + owner_deltas[owner]
            projected.append((owner, balance))
            if balance < 0:
                deficient.append(owner)
        return AffordabilityDecision(not deficient, tuple(projected), tuple(deficient))

    def ceiling(self, potential: LocalGaussianPotential, state: Vector, owner: int) -> Fraction:
        return potential.factor_value(state, owner)

    def reconcile(
        self, potential: LocalGaussianPotential, state: Vector
    ) -> "SignedShadowLedgerV2":
        balances = list(self.balances)
        retired = self.retired
        for owner, balance in enumerate(balances):
            limit = self.ceiling(potential, state, owner)
            if balance > limit:
                retired += balance - limit
                balances[owner] = limit
        return SignedShadowLedgerV2(tuple(balances), retired)

    def settle(
        self,
        owner_deltas: Mapping[int, Fraction],
        potential: LocalGaussianPotential,
        state_after: Vector,
    ) -> "SignedShadowLedgerV2":
        """Settle unconditionally. No refusal; balances may go negative."""
        balances = list(self.balances)
        for owner, balance in self.project(owner_deltas).projected:
            balances[owner] = balance
        return SignedShadowLedgerV2(tuple(balances), self.retired).reconcile(
            potential, state_after
        )
