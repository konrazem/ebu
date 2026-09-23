"""Finite atomic actions, simultaneous groups and ownership.

Decision packet B: an atomic action moves a declared nonnegative rational
quantity from a source cell to a destination cell, and `owner(a) = src(a)` --
exactly one owner per action, declared here and never inferred from framework
`requesting_actor_ref` / `responsible_provider_ref` fields.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from .numerics import Refusal, Vector, exact, zeros

GROUP_RULE_ID = "EBU-GAUSSIAN-GROUP-v1"


@dataclass(frozen=True, order=True)
class AtomicAction:
    """A finite transfer of one homogeneous conserved scalar.

    The increment is exactly mass-conserving by construction: it removes `q`
    from `src` and adds `q` to `dst`, so `sum_i delta_i = 0`.
    """

    source: int
    destination: int
    quantity: Fraction

    def __post_init__(self) -> None:
        if self.source == self.destination:
            raise Refusal("action source and destination must differ")
        if self.quantity <= 0:
            raise Refusal("action quantity must be positive")

    @classmethod
    def declare(cls, source: int, destination: int, quantity) -> "AtomicAction":
        return cls(source, destination, exact(quantity, "quantity"))

    @property
    def action_id(self) -> str:
        return f"a:{self.source}->{self.destination}:{self.quantity.numerator}/{self.quantity.denominator}"

    @property
    def owner(self) -> int:
        """The cell that moves its own stock. Declared, not inferred."""
        return self.source

    def increment(self, dimension: int) -> Vector:
        values = list(zeros(dimension))
        values[self.source] -= self.quantity
        values[self.destination] += self.quantity
        return tuple(values)

    @property
    def support(self) -> frozenset[int]:
        return frozenset({self.source, self.destination})


@dataclass(frozen=True)
class ActionGroup:
    """An immutable simultaneous group evaluated from one frozen baseline.

    Group membership is not net change: a nonempty group whose increments
    cancel has `delta_G = 0`.
    """

    actions: tuple[AtomicAction, ...]

    def __post_init__(self) -> None:
        pairs = [(action.source, action.destination) for action in self.actions]
        if len(set(pairs)) != len(pairs):
            raise Refusal("group contains duplicate source/destination pairs")
        if tuple(sorted(self.actions)) != self.actions:
            raise Refusal("group actions must be in canonical order")

    @classmethod
    def of(cls, *actions: AtomicAction) -> "ActionGroup":
        return cls(tuple(sorted(actions)))

    @property
    def is_empty(self) -> bool:
        return not self.actions

    @property
    def group_id(self) -> str:
        return "g:[" + ",".join(action.action_id for action in self.actions) + "]"

    @property
    def size(self) -> int:
        return len(self.actions)

    def increment(self, dimension: int) -> Vector:
        """delta_G = sum_a delta_a, on one frozen pre-action baseline."""
        values = list(zeros(dimension))
        for action in self.actions:
            values[action.source] -= action.quantity
            values[action.destination] += action.quantity
        return tuple(values)

    @property
    def support(self) -> frozenset[int]:
        """Union of member supports, before cancellation.

        Deliberately not the support of the summed increment: a factor whose
        net change cancels is still touched by the group and must be included
        when the group is valued, even though its contribution is zero.
        """
        touched: set[int] = set()
        for action in self.actions:
            touched |= action.support
        return frozenset(touched)

    @property
    def owners(self) -> frozenset[int]:
        return frozenset(action.owner for action in self.actions)


EMPTY_GROUP = ActionGroup(())
