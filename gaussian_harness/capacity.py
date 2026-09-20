"""Persistent per-owner EBU capacity and affordability.

Decision packet B. Each cell owns a nonnegative balance `B_i >= 0` initialized
at zero. Capacity is earned and spent: the rule is **no debt / no overdraft**,
not "no debit".

    B_i' = B_i + sum_{a : owner(a) = i} R_a
    affordable(G)  iff  B_i' >= 0 for every owner i

There is no borrowing, arbitrary issuance, periodic refill, global pool,
genesis grant or direct capacity transfer between owners. This is a declared
prospective model rule, not a consequence of the group closure identity.

`B` is not `ebu_framework.commitments.CapacityRecord`: that record holds
installed/available/reserved physical service quantities and keeps its own
meaning (framework decision F2-E). It is deliberately not reused here.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Mapping

from .numerics import Refusal
from .valuation import GroupValuation

CAPACITY_RULE_ID = "EBU-GAUSSIAN-CAPACITY-v1"


@dataclass(frozen=True)
class AffordabilityDecision:
    """Result of projecting owned receipts onto balances. Side-effect free."""

    affordable: bool
    projected: tuple[tuple[int, Fraction], ...]
    deficient_owners: tuple[int, ...]

    @property
    def projected_map(self) -> dict[int, Fraction]:
        return dict(self.projected)


@dataclass(frozen=True)
class CapacityLedger:
    """Immutable per-owner balance vector with zero genesis."""

    balances: tuple[Fraction, ...]

    def __post_init__(self) -> None:
        for owner, balance in enumerate(self.balances):
            if balance < 0:
                raise Refusal(f"owner {owner} holds a negative balance")

    @classmethod
    def zero(cls, cells: int) -> "CapacityLedger":
        if cells <= 0:
            raise Refusal("cell count must be positive")
        return cls(tuple(Fraction(0) for _ in range(cells)))

    @property
    def total(self) -> Fraction:
        result = Fraction(0)
        for balance in self.balances:
            result += balance
        return result

    def project(self, owner_deltas: Mapping[int, Fraction]) -> AffordabilityDecision:
        """Project owned receipts without mutating anything.

        Computing projected affordability is evaluation, not execution: no
        balance, physical state or ledger changes here.
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

    def is_affordable(self, valuation: GroupValuation) -> AffordabilityDecision:
        return self.project(valuation.owner_deltas)

    def settle(self, owner_deltas: Mapping[int, Fraction]) -> "CapacityLedger":
        """Atomic all-or-nothing settlement.

        Every owner's balance moves together or the ledger is unchanged and the
        attempt is refused. A partial credit followed by a failed debit would
        create spendable capacity without an authorized event, so the decision
        is taken before any value is written.
        """
        decision = self.project(owner_deltas)
        if not decision.affordable:
            raise Refusal(
                f"AFFORDABILITY_REFUSED: owners {decision.deficient_owners} would go into debt"
            )
        balances = list(self.balances)
        for owner, balance in decision.projected:
            balances[owner] = balance
        return CapacityLedger(tuple(balances))
