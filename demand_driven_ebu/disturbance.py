"""Exogenous natural physical disturbance.

Nature moves stock. It is not an actor, it serves no demand, it is not valued
and it earns nobody anything: contract section 24 is explicit that only
verified actor receipts change actor capacity, and nothing in this module can
reach a ledger. What a disturbance can do is create physical demand, by pushing
a coordinate below its reference.

The declared baseline disturbance is conservative: one quantum of one resource
moves between two stocks of that resource, so the resource total is unchanged
and the world stays closed. The deviation it injects is recorded in an external
ledger, because the capacity-source identity in `cycles` needs to separate
capacity that actors created by restoring the system from capacity that nature
paid for by disturbing it.

When the drawn source does not hold the quantum the disturbance is null for
that epoch. It is not resampled, clipped, reversed, redirected or reduced in
magnitude: an arm-specific null is an observed consequence of that arm's state,
and repairing it would make the disturbance process depend on the state it is
supposed to be independent of.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from gaussian_harness.numerics import Refusal, Vector, exact

from .rng import STREAM_NATURAL, Counter, bernoulli, uniform_index
from .world import ROLE_STOCK, DemandWorld

EVENT_DISTURBANCE = 0

STATUS_APPLIED = "DISTURBANCE_APPLIED"
STATUS_NULL_UNAVAILABLE = "DISTURBANCE_NULL_SOURCE_SHORT"
STATUS_NOT_SCHEDULED = "DISTURBANCE_NOT_SCHEDULED"


@dataclass(frozen=True)
class DisturbanceEvent:
    status: str
    source: int | None
    destination: int | None
    quantity: Fraction


@dataclass(frozen=True)
class DisturbanceProcess:
    """A conservative redistribution law with a declared frequency and quantum."""

    pairs: tuple[tuple[int, int], ...]
    quantum: Fraction
    numerator: int
    denominator: int

    def __post_init__(self) -> None:
        if not self.pairs:
            raise Refusal("the disturbance needs at least one declared pair")
        if tuple(sorted(self.pairs)) != self.pairs or len(set(self.pairs)) != len(self.pairs):
            raise Refusal("disturbance pairs must be distinct and canonically ordered")
        if self.quantum <= 0:
            raise Refusal("the disturbance quantum must be positive")
        if not 0 <= self.numerator <= self.denominator or self.denominator <= 0:
            raise Refusal("disturbance frequency must be a rational in [0, 1]")

    @classmethod
    def declare(cls, world: DemandWorld, pairs, quantum, numerator: int, denominator: int):
        ordered = tuple(sorted({(int(a), int(b)) for a, b in pairs}))
        for source, destination in ordered:
            if source == destination:
                raise Refusal("a disturbance pair must move stock between two coordinates")
            for index in (source, destination):
                if not 0 <= index < world.dimension:
                    raise Refusal("disturbance pair leaves the world")
                if world.coordinates[index].role != ROLE_STOCK:
                    raise Refusal("nature redistributes stocks, not sinks")
            if world.coordinates[source].resource != world.coordinates[destination].resource:
                raise Refusal("a conservative disturbance stays within one resource")
        return cls(ordered, exact(quantum, "quantum"), numerator, denominator)

    def draw(self, world: DemandWorld, state: Vector, seed: int, epoch: int) -> DisturbanceEvent:
        base = Counter(
            "EBU-DEMAND-DRIVEN-ECONOMY-v1",
            world.world_id,
            seed,
            STREAM_NATURAL,
            epoch,
            EVENT_DISTURBANCE,
            0,
        )
        scheduled, _ = bernoulli(base.at(draw_index=0), self.numerator, self.denominator)
        if not scheduled:
            return DisturbanceEvent(STATUS_NOT_SCHEDULED, None, None, Fraction(0))
        index, _ = uniform_index(base.at(draw_index=1), len(self.pairs))
        source, destination = self.pairs[index]
        if state[source] < self.quantum:
            return DisturbanceEvent(STATUS_NULL_UNAVAILABLE, source, destination, Fraction(0))
        return DisturbanceEvent(STATUS_APPLIED, source, destination, self.quantum)


def apply_disturbance(
    world: DemandWorld, state: Vector, event: DisturbanceEvent
) -> Vector:
    if event.status != STATUS_APPLIED:
        return state
    values = list(state)
    values[event.source] -= event.quantity
    values[event.destination] += event.quantity
    return tuple(values)
