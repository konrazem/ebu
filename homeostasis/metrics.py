"""Physical-state homeostasis metrics.

Mission sections 4 and 5. Every metric here is a function of the physical state
trajectory alone. No capacity balance, receipt, settlement quantity or
deviation-ledger value enters any definition -- that separation is the point of
the mission's homeostasis concept, and it is enforced here by the fact that
these functions are given `R^2` and nothing else.

Exactness
---------

`R^2 = 2V` is an exact rational, so occupancy, exit counts, excursion
durations, return times and every order statistic of `R` are computed exactly:
order statistics of `R` are taken on `R^2` and square-rooted only for display,
which is valid because the square root is monotone. Mean `R` is genuinely
irrational and is the one reported quantity that is a float; it is labelled as
such. This follows the frozen numeric policy: exact arithmetic for invariants
and structure, floating point only where an empirical statistic genuinely
requires it.

Failure concept
---------------

The central failure concept is *not* `V != 0` (mission section 15). It is
persistent or secular movement away from the reference, or very low occupancy
under the declared disturbance load. `drift_diagnostics` therefore compares
late blocks rather than testing any single tick against zero.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from fractions import Fraction
from typing import Sequence

from gaussian_harness.numerics import Refusal

METRIC_RULE_ID = "EBU-GAUSSIAN-HOMEOSTASIS-METRICS-v1"

# Frozen percentile convention: nearest-rank on the sorted sample, so every
# reported percentile is an observed value and no interpolation convention has
# to be defended later.
PERCENTILE_RULE = "nearest_rank_ceiling"


def _nearest_rank(sorted_values: Sequence[Fraction], level: Fraction) -> Fraction:
    if not sorted_values:
        raise Refusal("percentile of an empty sample")
    if not 0 < level <= 1:
        raise Refusal("percentile level must lie in (0, 1]")
    count = len(sorted_values)
    rank = -(-(level * count).numerator // (level * count).denominator)  # ceil, exact
    rank = max(1, min(count, int(rank)))
    return sorted_values[rank - 1]


def exact_median(values: Sequence[Fraction]) -> Fraction:
    """Exact median: the mean of the two central order statistics when even."""
    if not values:
        raise Refusal("median of an empty sample")
    ordered = sorted(values)
    count = len(ordered)
    middle = count // 2
    if count % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2


def exact_mean(values: Sequence[Fraction]) -> Fraction:
    if not values:
        raise Refusal("mean of an empty sample")
    accumulated = Fraction(0)
    for value in values:
        accumulated += value
    return accumulated / len(values)


def occupancy(flags: Sequence[bool]) -> Fraction:
    """O = (1/T) sum_t 1[x_t in region]. Exact rational, never a float ratio."""
    if not flags:
        raise Refusal("occupancy of an empty window")
    return Fraction(sum(1 for flag in flags if flag), len(flags))


@dataclass(frozen=True)
class Excursion:
    """One maximal run of consecutive ticks outside the region."""

    start: int
    length: int
    peak_radial_square: Fraction
    returned: bool

    @property
    def end(self) -> int:
        return self.start + self.length - 1


def excursions(flags: Sequence[bool], radial_squares: Sequence[Fraction]) -> tuple[Excursion, ...]:
    """Maximal outside-runs, with the final run flagged if it never returns.

    A run still in progress when the window ends is `returned=False`. Its
    duration is right-censored, so it is excluded from return-time statistics
    and reported separately rather than silently treated as a completed return.
    """
    if len(flags) != len(radial_squares):
        raise Refusal("flag and radius sequences differ in length")
    found: list[Excursion] = []
    start: int | None = None
    peak = Fraction(0)
    for index, inside in enumerate(flags):
        if not inside:
            if start is None:
                start = index
                peak = radial_squares[index]
            else:
                peak = max(peak, radial_squares[index])
        elif start is not None:
            found.append(Excursion(start, index - start, peak, True))
            start = None
    if start is not None:
        found.append(Excursion(start, len(flags) - start, peak, False))
    return tuple(found)


def exit_count(flags: Sequence[bool]) -> int:
    """Transitions from inside to outside the region.

    A trajectory that begins outside has not *exited*; that opening excursion
    is counted by `excursions` but not here, so the two numbers can legitimately
    differ by one.
    """
    return sum(
        1 for index in range(1, len(flags)) if flags[index - 1] and not flags[index]
    )


@dataclass(frozen=True)
class BlockSummary:
    """One analysis block. `mean_potential` is exact; `mean_radius` is not."""

    index: int
    start: int
    length: int
    occupancy_95: Fraction
    occupancy_99: Fraction
    mean_potential: Fraction
    median_radial_square: Fraction
    mean_radius: float


def block_summaries(
    radial_squares: Sequence[Fraction],
    in_95: Sequence[bool],
    in_99: Sequence[bool],
    block: int,
    blocks: int,
) -> tuple[BlockSummary, ...]:
    if block < 1 or blocks < 1:
        raise Refusal("block size and count must be positive")
    if len(radial_squares) < block * blocks:
        raise Refusal("window is shorter than the declared block structure")
    summaries: list[BlockSummary] = []
    for position in range(blocks):
        start = position * block
        stop = start + block
        window = radial_squares[start:stop]
        summaries.append(
            BlockSummary(
                index=position,
                start=start,
                length=block,
                occupancy_95=occupancy(in_95[start:stop]),
                occupancy_99=occupancy(in_99[start:stop]),
                mean_potential=exact_mean(window) / 2,
                median_radial_square=exact_median(window),
                mean_radius=sum(math.sqrt(float(value)) for value in window) / block,
            )
        )
    return tuple(summaries)


@dataclass(frozen=True)
class DriftDiagnostic:
    """Late-window movement of the physical state distribution.

    Both quantities are exact differences between the last and the first
    analysis block. Positive `occupancy_change` means the process spent more
    time inside the region later; positive `median_change` means it sat further
    out. Divergence is the combination of falling occupancy and rising radius,
    sustained across blocks -- not any single tick with `V > 0`.
    """

    occupancy_change: Fraction
    median_change: Fraction
    monotone_occupancy_decline: bool
    monotone_radius_growth: bool


def drift_diagnostics(summaries: Sequence[BlockSummary]) -> DriftDiagnostic:
    if len(summaries) < 2:
        raise Refusal("drift needs at least two blocks")
    first, last = summaries[0], summaries[-1]
    occupancies = [summary.occupancy_95 for summary in summaries]
    medians = [summary.median_radial_square for summary in summaries]
    return DriftDiagnostic(
        occupancy_change=last.occupancy_95 - first.occupancy_95,
        median_change=last.median_radial_square - first.median_radial_square,
        monotone_occupancy_decline=all(
            later < earlier for earlier, later in zip(occupancies, occupancies[1:])
        ),
        monotone_radius_growth=all(
            later > earlier for earlier, later in zip(medians, medians[1:])
        ),
    )


@dataclass(frozen=True)
class HomeostasisSummary:
    """The complete predefined metric battery for one analysis window."""

    ticks: int
    occupancy_95: Fraction
    occupancy_99: Fraction
    outside_99_fraction: Fraction
    mean_potential: Fraction
    median_radial_square: Fraction
    radius_mean: float
    radius_median: float
    radius_p90: float
    radius_p95: float
    radius_p99: float
    radius_max: float
    median_radial_square_exact: Fraction
    p90_radial_square_exact: Fraction
    p95_radial_square_exact: Fraction
    p99_radial_square_exact: Fraction
    max_radial_square_exact: Fraction
    exits_95: int
    excursion_count: int
    time_outside_95: int
    excursion_duration_median: Fraction | None
    excursion_duration_max: int | None
    excursion_severity_max: Fraction | None
    return_time_median: Fraction | None
    censored_excursions: int
    blocks: tuple[BlockSummary, ...]
    drift: DriftDiagnostic | None


def summarize(
    radial_squares: Sequence[Fraction],
    in_95: Sequence[bool],
    in_99: Sequence[bool],
    block: int = 0,
    blocks: int = 0,
) -> HomeostasisSummary:
    """Compute the frozen metric battery over one analysis window."""
    if not radial_squares:
        raise Refusal("summary of an empty window")
    if not (len(radial_squares) == len(in_95) == len(in_99)):
        raise Refusal("window columns differ in length")

    ordered = sorted(radial_squares)
    runs = excursions(in_95, radial_squares)
    completed = [run for run in runs if run.returned]
    durations = [Fraction(run.length) for run in runs]

    median_r2 = exact_median(radial_squares)
    p90 = _nearest_rank(ordered, Fraction(90, 100))
    p95 = _nearest_rank(ordered, Fraction(95, 100))
    p99 = _nearest_rank(ordered, Fraction(99, 100))
    peak = ordered[-1]

    summaries: tuple[BlockSummary, ...] = ()
    drift: DriftDiagnostic | None = None
    if block and blocks:
        summaries = block_summaries(radial_squares, in_95, in_99, block, blocks)
        if len(summaries) >= 2:
            drift = drift_diagnostics(summaries)

    return HomeostasisSummary(
        ticks=len(radial_squares),
        occupancy_95=occupancy(in_95),
        occupancy_99=occupancy(in_99),
        outside_99_fraction=1 - occupancy(in_99),
        mean_potential=exact_mean(radial_squares) / 2,
        median_radial_square=median_r2,
        radius_mean=sum(math.sqrt(float(value)) for value in radial_squares) / len(radial_squares),
        radius_median=math.sqrt(float(median_r2)),
        radius_p90=math.sqrt(float(p90)),
        radius_p95=math.sqrt(float(p95)),
        radius_p99=math.sqrt(float(p99)),
        radius_max=math.sqrt(float(peak)),
        median_radial_square_exact=median_r2,
        p90_radial_square_exact=p90,
        p95_radial_square_exact=p95,
        p99_radial_square_exact=p99,
        max_radial_square_exact=peak,
        exits_95=exit_count(in_95),
        excursion_count=len(runs),
        time_outside_95=sum(1 for flag in in_95 if not flag),
        excursion_duration_median=exact_median(durations) if durations else None,
        excursion_duration_max=max((run.length for run in runs), default=None),
        excursion_severity_max=max((run.peak_radial_square for run in runs), default=None),
        return_time_median=(
            exact_median([Fraction(run.length) for run in completed]) if completed else None
        ),
        censored_excursions=sum(1 for run in runs if not run.returned),
        blocks=summaries,
        drift=drift,
    )
