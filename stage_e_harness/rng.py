"""Exact counter-hash rational sampler frozen for future Stage F use."""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from typing import Iterable

from .canonical import Refusal


RULE_ID = "EBU-STAGE-F-COUNTER-HASH-DRAWS-v1"
PREIMAGE_PREFIX = "EBU-STAGE-F-RNG-v1"
ATTEMPT_CAP = 1_000_000
U64_MODULUS = 1 << 64


@dataclass(frozen=True)
class Counter:
    study_id: str
    configuration_id: str
    seed: int
    stream_id: str
    tick: int
    event_index: int
    draw_index: int

    def preimage(self, attempt_index: int) -> bytes:
        values = (self.seed, self.tick, self.event_index, self.draw_index, attempt_index)
        if any(not isinstance(value, int) or isinstance(value, bool) or value < 0 for value in values):
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


@dataclass(frozen=True)
class RationalDraw:
    residue: int | None
    denominator: int
    accepted_attempt_index: int
    rejected_attempts: int
    draw_status: str


def u64(counter: Counter, attempt_index: int) -> int:
    return int.from_bytes(hashlib.sha256(counter.preimage(attempt_index)).digest()[:8], "big")


def exact_residue(counter: Counter, denominator: int, *, attempt_cap: int = ATTEMPT_CAP) -> RationalDraw:
    if not isinstance(denominator, int) or isinstance(denominator, bool) or denominator <= 0:
        raise Refusal("rational denominator must be a positive integer")
    if attempt_cap != ATTEMPT_CAP:
        raise Refusal("terminal rejection cap is immutable")
    limit = U64_MODULUS - (U64_MODULUS % denominator)
    for attempt_index in range(ATTEMPT_CAP):
        value = u64(counter, attempt_index)
        if value < limit:
            return RationalDraw(value % denominator, denominator, attempt_index, attempt_index, "READY")
    return RationalDraw(None, denominator, ATTEMPT_CAP, ATTEMPT_CAP, "TERMINAL_REJECTION_CAP")


def bernoulli(counter: Counter, numerator: int, denominator: int) -> tuple[bool, RationalDraw]:
    if not all(isinstance(value, int) and not isinstance(value, bool) for value in (numerator, denominator)):
        raise Refusal("Bernoulli probability must use integers")
    if denominator <= 0 or numerator < 0 or numerator > denominator:
        raise Refusal("invalid Bernoulli probability")
    divisor = math.gcd(numerator, denominator)
    numerator //= divisor
    denominator //= divisor
    draw = exact_residue(counter, denominator)
    if draw.draw_status != "READY" or draw.residue is None:
        raise Refusal("TERMINAL_REJECTION_CAP: COMPUTATIONALLY_INCONCLUSIVE")
    return draw.residue < numerator, draw


def categorical(counter: Counter, masses: Iterable[tuple[str, int]], denominator: int) -> tuple[str, RationalDraw]:
    rows = list(masses)
    if not rows or denominator <= 0:
        raise Refusal("invalid categorical masses")
    if any(not name or not isinstance(weight, int) or isinstance(weight, bool) or weight < 0 for name, weight in rows):
        raise Refusal("invalid categorical category")
    if sum(weight for _, weight in rows) != denominator:
        raise Refusal("categorical masses do not exactly sum to denominator")
    draw = exact_residue(counter, denominator)
    if draw.draw_status != "READY" or draw.residue is None:
        raise Refusal("TERMINAL_REJECTION_CAP: COMPUTATIONALLY_INCONCLUSIVE")
    lower = 0
    for name, weight in rows:
        upper = lower + weight
        if lower <= draw.residue < upper:
            return name, draw
        lower = upper
    raise AssertionError("exact categorical partition did not select a category")
