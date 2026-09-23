"""Physical feasibility, decided before and independently of EBU.

Task section 11. Feasibility may read current physical state, action topology,
resource availability, hard physical bounds and group constraints. It must not
read EBU value, capacity balance, global V or actor preference, and no function
here is given access to any of those.

Simultaneity is source-funded: every source must already hold, at the frozen
pre-action baseline, the total quantity it sends in the group. A cell may not
fund an outflow with stock arriving in the same instant from another member of
the same group. This is a declared physical assumption. Endpoint nonnegativity
alone would be weaker, because it permits exactly that unspecified intermediate
physics, and it is implied by the source-funded rule rather than replacing it.

The exact group that is valued here is the group that is later executed. No
proposal is valued and then rescaled or resolved into something else.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from .actions import ActionGroup
from .numerics import Refusal, Vector

FEASIBILITY_RULE_ID = "EBU-GAUSSIAN-FEASIBILITY-SOURCE-FUNDED-v1"


@dataclass(frozen=True)
class FeasibilityVerdict:
    feasible: bool
    reason: str
    violating_cells: tuple[int, ...] = ()


@dataclass(frozen=True)
class PhysicalRules:
    """Declared hard physical bounds and topology."""

    cells: int
    edges: frozenset[tuple[int, int]]
    upper_bound: Fraction | None = None

    def __post_init__(self) -> None:
        if self.cells <= 0:
            raise Refusal("cell count must be positive")
        for source, destination in self.edges:
            if not (0 <= source < self.cells and 0 <= destination < self.cells):
                raise Refusal(f"edge ({source},{destination}) leaves the world")
            if source == destination:
                raise Refusal("self-edges are not physical transfers")

    @classmethod
    def complete_graph(cls, cells: int, upper_bound: Fraction | None = None) -> "PhysicalRules":
        edges = frozenset(
            (source, destination)
            for source in range(cells)
            for destination in range(cells)
            if source != destination
        )
        return cls(cells, edges, upper_bound)


def assess(rules: PhysicalRules, state: Vector, group: ActionGroup) -> FeasibilityVerdict:
    """Decide joint physical feasibility of a group at a frozen baseline."""
    if group.is_empty:
        return FeasibilityVerdict(True, "EMPTY_GROUP_IS_ALWAYS_FEASIBLE")

    for action in group.actions:
        if (action.source, action.destination) not in rules.edges:
            return FeasibilityVerdict(
                False,
                "EDGE_NOT_IN_TOPOLOGY",
                (action.source, action.destination),
            )

    outflow: dict[int, Fraction] = {}
    for action in group.actions:
        outflow[action.source] = outflow.get(action.source, Fraction(0)) + action.quantity

    short = tuple(
        sorted(cell for cell, sent in outflow.items() if sent > state[cell])
    )
    if short:
        return FeasibilityVerdict(False, "SOURCE_STOCK_INSUFFICIENT", short)

    increment = group.increment(rules.cells)
    negative = tuple(
        index for index, value in enumerate(increment) if state[index] + value < 0
    )
    if negative:
        return FeasibilityVerdict(False, "ENDPOINT_STOCK_NEGATIVE", negative)

    if rules.upper_bound is not None:
        over = tuple(
            index
            for index, value in enumerate(increment)
            if state[index] + value > rules.upper_bound
        )
        if over:
            return FeasibilityVerdict(False, "ENDPOINT_EXCEEDS_UPPER_BOUND", over)

    return FeasibilityVerdict(True, "FEASIBLE")
