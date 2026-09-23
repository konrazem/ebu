"""Two independent counter-addressed random streams.

Decision packet J. The forcing stream and the actor-choice stream are
mandatory and separate, with separate seeds. Draws are **stateless**: a draw is
a pure function of its coordinates

    (study_id, configuration_id, seed, stream_id, tick, event_index,
     draw_index, attempt_index)

so there is no shared mutable generator state to leak between them. The forcing
stream therefore cannot read B, EBU, V or the actor stream's position: it is a
hash of its own coordinates and nothing else.

The exact-residue rejection arithmetic is adopted from the Stage E harness
sampler (`stage_e_harness/rng.py` at `a4af44a`) under a new Gaussian rule id.
That module is not modified, imported or re-executed here, so Stage E keeps its
own semantics and provenance.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from fractions import Fraction
from typing import Sequence

from .numerics import Refusal

RULE_ID = "EBU-GAUSSIAN-RNG-v1"
PREIMAGE_PREFIX = "EBU-GAUSSIAN-RNG-v1"
STREAM_FORCING = "forcing"
STREAM_ACTOR = "actor_choice"
DECLARED_STREAMS = (STREAM_FORCING, STREAM_ACTOR)
ATTEMPT_CAP = 1_000_000
U64_MODULUS = 1 << 64


@dataclass(frozen=True)
class Counter:
    """Exact draw address. Two draws collide only if every coordinate matches."""

    study_id: str
    configuration_id: str
    seed: int
    stream_id: str
    tick: int
    event_index: int
    draw_index: int

    def __post_init__(self) -> None:
        if self.stream_id not in DECLARED_STREAMS:
            raise Refusal(f"undeclared stream {self.stream_id!r}")

    def preimage(self, attempt_index: int) -> bytes:
        values = (self.seed, self.tick, self.event_index, self.draw_index, attempt_index)
        if any(
            not isinstance(value, int) or isinstance(value, bool) or value < 0
            for value in values
        ):
            raise Refusal("counter values must be nonnegative integers")
        fields = (
            PREIMAGE_PREFIX,
            self.study_id,
            self.configuration_id,
            str(self.seed),
            self.stream_id,
            str(self.tick),
            str(self.event_index),
            str(self.draw_index),
            str(attempt_index),
        )
        if any("|" in field or not field for field in fields[1:5]):
            raise Refusal("invalid counter-hash text field")
        return "|".join(fields).encode("utf-8")

    def at(self, *, tick: int | None = None, event_index: int | None = None,
           draw_index: int | None = None) -> "Counter":
        return Counter(
            self.study_id,
            self.configuration_id,
            self.seed,
            self.stream_id,
            self.tick if tick is None else tick,
            self.event_index if event_index is None else event_index,
            self.draw_index if draw_index is None else draw_index,
        )

    @property
    def provenance(self) -> str:
        return (
            f"{RULE_ID}|{self.stream_id}|seed={self.seed}"
            f"|t={self.tick}|e={self.event_index}|d={self.draw_index}"
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
    """Uniform residue modulo `denominator`, rejecting the biased tail.

    Rejection keeps the draw exactly uniform rather than nearly uniform, which
    matters because the study is meant to be replayed exactly.
    """
    if not isinstance(denominator, int) or isinstance(denominator, bool) or denominator <= 0:
        raise Refusal("denominator must be a positive integer")
    limit = U64_MODULUS - (U64_MODULUS % denominator)
    for attempt_index in range(ATTEMPT_CAP):
        value = u64(counter, attempt_index)
        if value < limit:
            return RationalDraw(value % denominator, denominator, attempt_index, attempt_index, "READY")
    return RationalDraw(None, denominator, ATTEMPT_CAP, ATTEMPT_CAP, "TERMINAL_REJECTION_CAP")


def uniform_index(counter: Counter, count: int) -> tuple[int, RationalDraw]:
    """Uniform index into a canonically ordered list of `count` items.

    The caller passes only a count. No value, sign, potential or balance is
    visible to this function, so the choice cannot encode a preference.
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


def uniform_rational(counter: Counter, options: Sequence[Fraction]) -> tuple[Fraction, RationalDraw]:
    if not options:
        raise Refusal("uniform_rational needs a nonempty option list")
    index, draw = uniform_index(counter, len(options))
    return options[index], draw
