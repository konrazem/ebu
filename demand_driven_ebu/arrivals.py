"""The exogenous economic-demand arrival process.

Arrivals are a pure function of `(seed, epoch)` and the declared alphabet, and
of nothing else. No physical stock, potential, capacity balance, EBU value,
actor policy or admission outcome appears anywhere in a draw address, so three
properties hold structurally rather than by convention, and the conformance
suite asserts all three: changing the actor policy cannot move the arrival
sequence, changing an EBU parameter cannot move it, and the process can and
will ask for more than physically exists.

That last property is the point of contract section 3. A request for 1000 t of
sand in a world holding 560 t is a valid arrival, and it is not truncated to
560, regenerated smaller, or quietly supplied with the missing 440. It is meant
to reveal scarcity.

The alphabet here is deliberately tiny and transparent. It is a conformance
device, not a scientific load: the real quantity, frequency, destination and
multiplicity distributions are unresolved study parameters and are recorded as
such in the decision packet rather than chosen silently.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from gaussian_harness.numerics import Refusal, exact

from .demand import EconomicDemand
from .rng import STREAM_ARRIVAL, Counter, bernoulli, uniform_index
from .world import DemandWorld

EVENT_ARRIVAL = 0


@dataclass(frozen=True)
class ArrivalKind:
    """One entry of the declared finite demand alphabet."""

    resource: str
    node: str
    quantity: Fraction

    @property
    def kind_id(self) -> str:
        return f"{self.resource}|{self.node}|{self.quantity}"


@dataclass(frozen=True)
class ArrivalProcess:
    """Declared arrival law: a Bernoulli slot count over a finite alphabet."""

    alphabet: tuple[ArrivalKind, ...]
    numerator: int
    denominator: int
    slots: int

    def __post_init__(self) -> None:
        if not self.alphabet:
            raise Refusal("the arrival alphabet must be nonempty")
        identifiers = [kind.kind_id for kind in self.alphabet]
        if list(identifiers) != sorted(identifiers):
            raise Refusal("arrival alphabet must be in canonical order")
        if not 0 <= self.numerator <= self.denominator or self.denominator <= 0:
            raise Refusal("arrival probability must be a rational in [0, 1]")
        if self.slots < 0:
            raise Refusal("slot count must be nonnegative")

    @classmethod
    def declare(cls, alphabet, numerator: int, denominator: int, slots: int) -> "ArrivalProcess":
        entries = tuple(
            sorted(
                (
                    ArrivalKind(resource, node, exact(quantity, "quantity"))
                    for resource, node, quantity in alphabet
                ),
                key=lambda kind: kind.kind_id,
            )
        )
        return cls(entries, numerator, denominator, slots)

    @property
    def probability(self) -> Fraction:
        return Fraction(self.numerator, self.denominator)

    def arrivals(
        self, world: DemandWorld, seed: int, epoch: int
    ) -> tuple[EconomicDemand, ...]:
        """Draw this epoch's arrivals. Depends on `(seed, epoch)` and nothing else."""
        base = Counter(
            "EBU-DEMAND-DRIVEN-ECONOMY-v1",
            world.world_id,
            seed,
            STREAM_ARRIVAL,
            epoch,
            EVENT_ARRIVAL,
            0,
        )
        drawn = []
        for slot in range(self.slots):
            fires, _ = bernoulli(base.at(draw_index=2 * slot), self.numerator, self.denominator)
            if not fires:
                continue
            index, _ = uniform_index(base.at(draw_index=2 * slot + 1), len(self.alphabet))
            kind = self.alphabet[index]
            drawn.append(
                EconomicDemand.declare(
                    world, kind.resource, kind.quantity, kind.node, epoch, slot
                )
            )
        return tuple(drawn)
