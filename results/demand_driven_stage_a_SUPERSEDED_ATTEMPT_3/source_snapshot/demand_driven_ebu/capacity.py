"""Persistent earned capacity, held by nodes, spendable only through demand.

Capacity semantics are Capacity V1, carried over unchanged and deliberately not
redesigned here:

    B_i >= 0,  B_i' = B_i + sum_{a : owner(a) = i} R_a,
    affordable(G)  iff  B_i' >= 0 for every owner i

No overdraft, no borrowing, no genesis grant, no refill, no pooling and no
direct transfer of capacity between owners. What the demand model adds is a
restriction on *where* a spend may occur, not on how it is measured: capacity
may only be spent through an action belonging to a valid current
demand-serving plan. An actor cannot pay to move stock that no demand asked for,
because such a plan never reaches a menu in the first place.

Capacity never changes what EBU measures. Given the same physical pre-state,
the same demand and the same plan, `V_pre`, `V_post`, `E_G` and every receipt
are identical whatever the balances are; the only thing balances decide is
whether the plan is affordable. That separation is enforced structurally --
`valuation` is not given a ledger -- and asserted metamorphically by the
conformance suite.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Mapping

from gaussian_harness.numerics import Refusal

from .valuation import GroupValuation

CAPACITY_RULE_ID = "EBU-DEMAND-CAPACITY-V1-v1"


@dataclass(frozen=True)
class AffordabilityDecision:
    affordable: bool
    projected: tuple[tuple[str, Fraction], ...]
    deficient_owners: tuple[str, ...]

    @property
    def projected_map(self) -> dict[str, Fraction]:
        return dict(self.projected)


@dataclass(frozen=True)
class CapacityLedger:
    """Immutable per-node balance vector with zero genesis."""

    balances: tuple[tuple[str, Fraction], ...]
    constrained: bool = True

    def __post_init__(self) -> None:
        names = [name for name, _ in self.balances]
        if list(names) != sorted(names):
            raise Refusal("ledger owners must be in canonical order")
        if len(set(names)) != len(names):
            raise Refusal("duplicate owner in the ledger")
        if self.constrained:
            for name, balance in self.balances:
                if balance < 0:
                    raise Refusal(f"owner {name} holds a negative balance")

    @classmethod
    def zero(cls, nodes, constrained: bool = True) -> "CapacityLedger":
        ordered = tuple(sorted(nodes))
        if not ordered:
            raise Refusal("a ledger needs at least one owner")
        return cls(tuple((name, Fraction(0)) for name in ordered), constrained)

    @classmethod
    def shadow(cls, nodes) -> "CapacityLedger":
        """The control arm's signed account: recorded, never binding.

        The comparator applies no affordability filter, so its accounts are not
        a constraint and may go negative. Recording them anyway keeps the same
        accounting identity auditable in both arms and shows exactly what the
        constraint would have bound, which is what the comparison needs.
        """
        return cls.zero(nodes, constrained=False)

    @property
    def balance_map(self) -> dict[str, Fraction]:
        return dict(self.balances)

    @property
    def total(self) -> Fraction:
        result = Fraction(0)
        for _, balance in self.balances:
            result += balance
        return result

    def project(self, owner_deltas: Mapping[str, Fraction]) -> AffordabilityDecision:
        """Project owned receipts without mutating anything."""
        current = self.balance_map
        projected: list[tuple[str, Fraction]] = []
        deficient: list[str] = []
        for owner in sorted(owner_deltas):
            if owner not in current:
                raise Refusal(f"owner {owner!r} is not a declared node")
            balance = current[owner] + owner_deltas[owner]
            projected.append((owner, balance))
            if balance < 0:
                deficient.append(owner)
        return AffordabilityDecision(not deficient, tuple(projected), tuple(deficient))

    def is_affordable(self, valuation: GroupValuation) -> AffordabilityDecision:
        decision = self.project(valuation.owner_map)
        if not self.constrained:
            return AffordabilityDecision(True, decision.projected, decision.deficient_owners)
        return decision

    def settle(self, owner_deltas: Mapping[str, Fraction]) -> "CapacityLedger":
        """Atomic all-or-nothing settlement.

        Every owner's balance moves together or the ledger is unchanged. A
        partial credit followed by a failed debit would create spendable
        capacity without an authorized event, so the decision is taken before
        any value is written.
        """
        decision = self.project(owner_deltas)
        if self.constrained and not decision.affordable:
            raise Refusal(
                f"AFFORDABILITY_REFUSED: owners {decision.deficient_owners} would go into debt"
            )
        balances = self.balance_map
        for owner, balance in decision.projected:
            balances[owner] = balance
        return CapacityLedger(tuple(sorted(balances.items())), self.constrained)
