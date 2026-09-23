"""EBU-blind exhaustive candidate generation.

Task section 12. For the small test world the entire finite candidate set is
enumerated deterministically, so no proposal heuristic can contaminate the
experiment and **no third RNG stream is introduced**.

Generation reads the declared topology and quantum set only. It never reads
EBU, potential, marginals or balances, and it does not seek a target.

A finite menu is an experimental restriction, not a claim that every physically
divisible quantity has been enumerated.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations

from .actions import ActionGroup, AtomicAction
from .feasibility import PhysicalRules
from .numerics import Refusal, exact_vector

MENU_RULE_ID = "EBU-GAUSSIAN-EXHAUSTIVE-MENU-v1"


@dataclass(frozen=True)
class MenuSpecification:
    """Declared finite action menu."""

    quanta: tuple[Fraction, ...]
    max_group_size: int = 2

    def __post_init__(self) -> None:
        if not self.quanta:
            raise Refusal("menu needs at least one quantum")
        if any(quantum <= 0 for quantum in self.quanta):
            raise Refusal("every quantum must be positive")
        if len(set(self.quanta)) != len(self.quanta):
            raise Refusal("duplicate quanta in menu specification")
        if self.max_group_size < 1:
            raise Refusal("max group size must be at least one")

    @classmethod
    def declare(cls, quanta, max_group_size: int = 2) -> "MenuSpecification":
        return cls(exact_vector(quanta, "quanta"), max_group_size)


def atomic_menu(rules: PhysicalRules, menu: MenuSpecification) -> tuple[AtomicAction, ...]:
    """Every declared atomic action, in canonical (source, destination, q) order."""
    actions = [
        AtomicAction(source, destination, quantum)
        for source, destination in rules.edges
        for quantum in menu.quanta
    ]
    return tuple(sorted(actions))


def candidate_groups(
    rules: PhysicalRules, menu: MenuSpecification
) -> tuple[ActionGroup, ...]:
    """All nonempty groups up to the declared size, in canonical order.

    The empty group is deliberately absent: decision packet I keeps it out of
    the sampling menu so that deadlock stays observable rather than being
    masked by an always-available do-nothing option.
    """
    actions = atomic_menu(rules, menu)
    groups: list[ActionGroup] = []
    for size in range(1, menu.max_group_size + 1):
        for chosen in combinations(actions, size):
            pairs = [(action.source, action.destination) for action in chosen]
            if len(set(pairs)) != len(pairs):
                continue
            groups.append(ActionGroup(tuple(sorted(chosen))))
    groups.sort(key=lambda group: group.group_id)
    identities = [group.group_id for group in groups]
    if len(set(identities)) != len(identities):
        raise Refusal("duplicate candidate group identities")
    return tuple(groups)
