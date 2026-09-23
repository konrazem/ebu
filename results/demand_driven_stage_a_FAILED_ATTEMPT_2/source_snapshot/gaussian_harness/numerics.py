"""Frozen numerical policy for the Local Gaussian Stage-A environment.

Decision packet H: exact rational arithmetic, zero tolerance. Every declared
quantity is a `fractions.Fraction`, so the potential, marginals, finite values,
receipts, balances and audit ledger are exactly representable and every
invariant is an exact equality rather than a tolerance test.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Iterable, Mapping, Sequence

POLICY_ID = "EBU-GAUSSIAN-NUMERIC-POLICY-v1"
DTYPE = "fractions.Fraction"
COMPARISON_TOLERANCE = Fraction(0)
INVARIANT_TOLERANCE = Fraction(0)
INTEGRATION_TOLERANCE = Fraction(0)


class Refusal(Exception):
    """Fail-closed refusal. Never caught to substitute a convenient default."""


Vector = tuple[Fraction, ...]


def exact(value: object, field: str = "value") -> Fraction:
    """Coerce an exactly-representable input to Fraction, refusing floats.

    A float is refused rather than converted because binary64 literals such as
    0.1 are not the decimal the author wrote, and silently adopting the binary
    value would make an "exact" identity depend on representation error.
    """
    if isinstance(value, bool):
        raise Refusal(f"{field} must not be a bool")
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value)
    if isinstance(value, str):
        return Fraction(value)
    if isinstance(value, tuple) and len(value) == 2:
        numerator, denominator = value
        if not all(isinstance(part, int) and not isinstance(part, bool) for part in (numerator, denominator)):
            raise Refusal(f"{field} rational pair must be integers")
        if denominator == 0:
            raise Refusal(f"{field} has zero denominator")
        return Fraction(numerator, denominator)
    raise Refusal(f"{field} must be an exact rational, not {type(value).__name__}")


def exact_vector(values: Iterable[object], field: str = "vector") -> Vector:
    return tuple(exact(value, f"{field}[{index}]") for index, value in enumerate(values))


def zeros(dimension: int) -> Vector:
    if dimension <= 0:
        raise Refusal("dimension must be positive")
    return tuple(Fraction(0) for _ in range(dimension))


def add(left: Vector, right: Vector) -> Vector:
    if len(left) != len(right):
        raise Refusal("vector dimension mismatch")
    return tuple(a + b for a, b in zip(left, right))


def scale(vector: Vector, factor: Fraction) -> Vector:
    return tuple(component * factor for component in vector)


def support(vector: Vector) -> frozenset[int]:
    """Indices where the increment is nonzero; the locality unit of valuation."""
    return frozenset(index for index, component in enumerate(vector) if component != 0)


def sparse_add(base: Vector, increment: Mapping[int, Fraction]) -> Vector:
    values = list(base)
    for index, delta in increment.items():
        values[index] += delta
    return tuple(values)


def total(values: Sequence[Fraction]) -> Fraction:
    result = Fraction(0)
    for value in values:
        result += value
    return result
