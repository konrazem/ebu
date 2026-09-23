"""Four independent counter-addressed random streams.

Contract section 32. The model needs four separate sources of randomness:

    NATURAL    exogenous physical disturbance
    ARRIVAL    exogenous economic demand arrivals
    ADMISSION  random compatible-subset admission
    ACTOR      random actor plan choice, and aligned/hostile tie-breaking

Every draw is a pure function of its address

    (model_id, world_id, seed, stream_id, epoch, event_index, draw_index,
     attempt_index)

so there is no shared mutable generator state that one stream could advance on
behalf of another. Two consequences are then structural rather than hoped for,
and are asserted by the conformance suite: changing the actor policy cannot
change the economic-demand arrival sequence, and changing an EBU parameter
cannot change it either, because neither appears anywhere in a draw address.

The exact-residue rejection arithmetic is adopted unchanged in behaviour from
`gaussian_harness.rng` (rule `EBU-GAUSSIAN-RNG-v1`) under a new rule id, so the
registered package keeps its own identity, streams and provenance. It is not
imported for its `Counter`, whose declared stream set is deliberately closed
over the two streams the registered studies used.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Sequence

from gaussian_harness.numerics import Refusal

RULE_ID = "EBU-DEMAND-RNG-v1"
PREIMAGE_PREFIX = RULE_ID

STREAM_NATURAL = "natural_disturbance"
STREAM_ARRIVAL = "economic_arrival"
STREAM_ADMISSION = "economic_admission"
STREAM_ACTOR = "actor_choice"
DECLARED_STREAMS = (STREAM_NATURAL, STREAM_ARRIVAL, STREAM_ADMISSION, STREAM_ACTOR)

ATTEMPT_CAP = 1_000_000
U64_MODULUS = 1 << 64


@dataclass(frozen=True)
class Counter:
    """Exact draw address. Two draws collide only if every coordinate matches."""

    model_id: str
    world_id: str
    seed: int
    stream_id: str
    epoch: int
    event_index: int
    draw_index: int

    def __post_init__(self) -> None:
        if self.stream_id not in DECLARED_STREAMS:
            raise Refusal(f"undeclared stream {self.stream_id!r}")
        for name in ("seed", "epoch", "event_index", "draw_index"):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise Refusal(f"counter field {name} must be a nonnegative integer")

    def preimage(self, attempt_index: int) -> bytes:
        if not isinstance(attempt_index, int) or isinstance(attempt_index, bool) or attempt_index < 0:
            raise Refusal("attempt index must be a nonnegative integer")
        fields = (
            PREIMAGE_PREFIX,
            self.model_id,
            self.world_id,
            str(self.seed),
            self.stream_id,
            str(self.epoch),
            str(self.event_index),
            str(self.draw_index),
            str(attempt_index),
        )
        if any("|" in field or not field for field in fields[1:3]):
            raise Refusal("invalid counter-hash text field")
        return "|".join(fields).encode("utf-8")

    def at(
        self,
        *,
        epoch: int | None = None,
        event_index: int | None = None,
        draw_index: int | None = None,
    ) -> "Counter":
        return Counter(
            self.model_id,
            self.world_id,
            self.seed,
            self.stream_id,
            self.epoch if epoch is None else epoch,
            self.event_index if event_index is None else event_index,
            self.draw_index if draw_index is None else draw_index,
        )

    @property
    def provenance(self) -> str:
        return (
            f"{RULE_ID}|{self.stream_id}|seed={self.seed}"
            f"|t={self.epoch}|e={self.event_index}|d={self.draw_index}"
        )


@dataclass(frozen=True)
class RationalDraw:
    residue: int | None
    denominator: int
    accepted_attempt_index: int
    rejected_attempts: int
    draw_status: str


def u64(counter: Counter, attempt_index: int) -> int:
    return int.from_bytes(hashlib.sha256(counter.preimage(attempt_index)).digest()[:8], "big")


def exact_residue(counter: Counter, denominator: int) -> RationalDraw:
    """Uniform residue modulo `denominator`, rejecting the biased tail."""
    if not isinstance(denominator, int) or isinstance(denominator, bool) or denominator <= 0:
        raise Refusal("denominator must be a positive integer")
    limit = U64_MODULUS - (U64_MODULUS % denominator)
    for attempt_index in range(ATTEMPT_CAP):
        value = u64(counter, attempt_index)
        if value < limit:
            return RationalDraw(
                value % denominator, denominator, attempt_index, attempt_index, "READY"
            )
    return RationalDraw(None, denominator, ATTEMPT_CAP, ATTEMPT_CAP, "TERMINAL_REJECTION_CAP")


def uniform_index(counter: Counter, count: int) -> tuple[int, RationalDraw]:
    """Uniform index into a canonically ordered list of `count` items.

    The caller passes a count and nothing else. No EBU value, sign, potential,
    deviation, balance or demand quantity is visible here, so a choice taken
    through this function cannot encode a preference over any of them.
    """
    if count <= 0:
        raise Refusal("uniform_index needs a nonempty candidate list")
    draw = exact_residue(counter, count)
    if draw.draw_status != "READY" or draw.residue is None:
        raise Refusal("TERMINAL_REJECTION_CAP: COMPUTATIONALLY_INCONCLUSIVE")
    return draw.residue, draw


def uniform_choice(counter: Counter, items: Sequence[object]) -> tuple[object, RationalDraw]:
    index, draw = uniform_index(counter, len(items))
    return items[index], draw


def bernoulli(counter: Counter, numerator: int, denominator: int) -> tuple[bool, RationalDraw]:
    """Exact rational Bernoulli draw with probability `numerator/denominator`."""
    if not 0 <= numerator <= denominator:
        raise Refusal("bernoulli numerator must lie in [0, denominator]")
    residue, draw = uniform_index(counter, denominator)
    return residue < numerator, draw
