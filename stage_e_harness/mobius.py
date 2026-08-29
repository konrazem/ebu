"""Exact direct and optimized Boolean Möbius conformance algorithms."""

from __future__ import annotations

import hashlib
import resource
import sys
import time
from dataclasses import dataclass
from fractions import Fraction
from typing import Callable, Iterable, Sequence, TypeVar

from .canonical import Refusal, canonical_digest

Exact = TypeVar("Exact", int, Fraction)


@dataclass(frozen=True)
class MobiusCounters:
    n: int
    subset_count: int
    table_acquisitions: int
    direct_subset_visits: int
    butterfly_subtractions: int
    reconstruction_additions: int
    maximum_live_table_slots: int


@dataclass(frozen=True)
class MobiusCaseResult:
    n: int
    coefficient_digest: str
    reconstruction_digest: str
    counters: MobiusCounters


def _check_table(values: Sequence[Exact], n: int) -> None:
    if not isinstance(n, int) or isinstance(n, bool) or n < 0 or n > 18:
        raise Refusal("exact Möbius n outside frozen 0..18 range")
    if len(values) != 1 << n:
        raise Refusal("Möbius table size does not equal 2^n")
    if any(not isinstance(value, (int, Fraction)) or isinstance(value, bool) for value in values):
        raise Refusal("Möbius arithmetic must be exact integer or Fraction")


def direct_coefficients(values: Sequence[Exact], n: int) -> tuple[list[Exact], int]:
    """Normative readable subset enumeration.

    I(S)=sum_{T subseteq S}(-1)^(|S|-|T|)E(T), including I(empty)=E(empty).
    """

    _check_table(values, n)
    coefficients: list[Exact] = []
    visits = 0
    for subset in range(1 << n):
        total: Exact = 0  # type: ignore[assignment]
        contained = subset
        while True:
            sign = -1 if ((subset.bit_count() - contained.bit_count()) & 1) else 1
            total = total + sign * values[contained]  # type: ignore[operator]
            visits += 1
            if contained == 0:
                break
            contained = (contained - 1) & subset
        coefficients.append(total)
    return coefficients, visits


def fast_coefficients(values: Sequence[Exact], n: int) -> tuple[list[Exact], int]:
    _check_table(values, n)
    coefficients = list(values)
    operations = 0
    for bit in range(n):
        bit_mask = 1 << bit
        for subset in range(1 << n):
            if subset & bit_mask:
                coefficients[subset] = coefficients[subset] - coefficients[subset ^ bit_mask]  # type: ignore[operator]
                operations += 1
    expected = n * (1 << (n - 1)) if n else 0
    if operations != expected:
        raise AssertionError("butterfly accounting defect")
    return coefficients, operations


def reconstruct(coefficients: Sequence[Exact], n: int) -> tuple[list[Exact], int]:
    _check_table(coefficients, n)
    values = list(coefficients)
    operations = 0
    for bit in range(n):
        bit_mask = 1 << bit
        for subset in range(1 << n):
            if subset & bit_mask:
                values[subset] = values[subset] + values[subset ^ bit_mask]  # type: ignore[operator]
                operations += 1
    return values, operations


def exact_case(values: Sequence[Exact], n: int) -> MobiusCaseResult:
    direct, visits = direct_coefficients(values, n)
    optimized, butterflies = fast_coefficients(values, n)
    if direct != optimized:
        raise Refusal("optimized Möbius coefficients disagree with direct oracle")
    rebuilt, additions = reconstruct(optimized, n)
    if rebuilt != list(values):
        raise Refusal("optimized Möbius reconstruction mismatch")
    if optimized[0] != values[0]:
        raise Refusal("empty-set coefficient lost E(empty)")
    return MobiusCaseResult(
        n=n,
        coefficient_digest=_exact_sequence_digest(optimized),
        reconstruction_digest=_exact_sequence_digest(rebuilt),
        counters=MobiusCounters(
            n=n,
            subset_count=1 << n,
            table_acquisitions=1 << n,
            direct_subset_visits=visits,
            butterfly_subtractions=butterflies,
            reconstruction_additions=additions,
            maximum_live_table_slots=1 << n,
        ),
    )


def _exact_sequence_digest(values: Iterable[int | Fraction]) -> str:
    rows = []
    for value in values:
        fraction = Fraction(value)
        rows.append([fraction.numerator, fraction.denominator])
    return canonical_digest(rows)


def adversarial_table(n: int, family: str) -> list[int]:
    size = 1 << n
    rows: list[int] = []
    for subset in range(size):
        cardinality = subset.bit_count()
        indices = [index for index in range(n) if subset & (1 << index)]
        if family == "ZERO":
            value = 0
        elif family == "CONSTANT_SEVEN":
            value = 7
        elif family == "CARDINALITY":
            value = cardinality
        elif family == "WEIGHTED_ADDITIVE":
            value = sum(index + 1 for index in indices)
        elif family == "WEIGHTED_PAIRWISE":
            value = sum((left + 1) * (right + 1) for pos, left in enumerate(indices) for right in indices[pos + 1 :])
        elif family == "FULL_SET_SPIKE":
            value = int(subset == size - 1)
        elif family == "EMPTY_SET_SPIKE":
            value = 7 if subset == 0 else 0
        elif family == "SIGNED_CARDINALITY_CUBE":
            value = (-1 if cardinality & 1 else 1) * (1 + cardinality**3)
        else:
            raise Refusal(f"unknown Möbius adversarial family: {family}")
        rows.append(value)
    return rows


def pseudorandom_integer_table(n: int, seed: int) -> list[int]:
    if n < 1 or n > 12 or seed not in range(32):
        raise Refusal("pseudorandom oracle vector outside frozen domain")
    return [
        int.from_bytes(hashlib.sha256(f"EBU-SD06-MOBIUS-v1|{n}|{seed}|{mask}".encode()).digest()[:8], "big") % 2001 - 1000
        for mask in range(1 << n)
    ]


def agreement_suite() -> dict[str, int]:
    families = (
        "ZERO",
        "CONSTANT_SEVEN",
        "CARDINALITY",
        "WEIGHTED_ADDITIVE",
        "WEIGHTED_PAIRWISE",
        "FULL_SET_SPIKE",
        "EMPTY_SET_SPIKE",
        "SIGNED_CARDINALITY_CUBE",
    )
    deterministic = randomized = 0
    direct_visits = butterflies = reconstructions = acquisitions = 0
    for n in range(13):
        for family in families:
            result = exact_case(adversarial_table(n, family), n)
            deterministic += 1
            direct_visits += result.counters.direct_subset_visits
            butterflies += result.counters.butterfly_subtractions
            reconstructions += result.counters.reconstruction_additions
            acquisitions += result.counters.table_acquisitions
    for n in range(1, 13):
        for seed in range(32):
            result = exact_case(pseudorandom_integer_table(n, seed), n)
            randomized += 1
            direct_visits += result.counters.direct_subset_visits
            butterflies += result.counters.butterfly_subtractions
            reconstructions += result.counters.reconstruction_additions
            acquisitions += result.counters.table_acquisitions
    if (deterministic, randomized) != (104, 384):
        raise AssertionError("Möbius agreement-domain arithmetic defect")
    return {
        "deterministic_cases": deterministic,
        "randomized_cases": randomized,
        "total_cases": deterministic + randomized,
        "table_acquisitions": acquisitions,
        "direct_subset_visits": direct_visits,
        "butterfly_subtractions": butterflies,
        "reconstruction_additions": reconstructions,
    }


def complexity_cell(n: int, repetition: int) -> dict[str, int | str]:
    if n not in range(8, 19) or repetition not in range(5):
        raise Refusal("Möbius complexity cell outside frozen grid")
    values = adversarial_table(n, "WEIGHTED_PAIRWISE")
    started = time.monotonic_ns()
    coefficients, operations = fast_coefficients(values, n)
    elapsed = time.monotonic_ns() - started
    if operations != n * (1 << (n - 1)):
        raise Refusal("Möbius complexity operation count mismatch")
    return {
        "n": n,
        "repetition": repetition,
        "elapsed_ns": elapsed,
        "primary_operations": operations,
        "logical_storage_slots": len(coefficients),
        "peak_process_tree_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * (1024 if sys.platform.startswith("linux") else 1),
        "output_digest": _exact_sequence_digest(coefficients),
    }
