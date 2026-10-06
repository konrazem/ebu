"""Confidence procedures and equivalence endpoints: Layer G.

Absolute scale intervals (T-stage section 9) and within-block contrast
intervals (section 10) are built as

    [bhat - c_minus * s - b_bound,  bhat + c_plus * s + b_bound]

with finite-N calibrated critical values and an explicit bounded-bias
enlargement.  Equality at a tolerance boundary is NOT a pass.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Sequence

from . import numerics as nm
from .numerics import Matrix, NumericalFailure

#: T-stage T.7 / T.8 margins.
DELTA_A = math.log(1.05)
DELTA_C = math.log(1.02)
#: Nominal one-sided level and its normal starting critical value.
NOMINAL_ONE_SIDED = 0.025
NORMAL_START = nm.norm_ppf(1.0 - NOMINAL_ONE_SIDED)
#: T-stage 20.2 design qualification ceiling on calibrated critical values.
CRITICAL_VALUE_CEILING = 2.10
#: T-stage T.24 calibration-uncertainty and bias envelope.
SIGMA_CAL_ABS_MAX = 0.009
SIGMA_CAL_CONTRAST_MAX = 0.003
BIAS_ABS_MAX = 0.0005
BIAS_CONTRAST_MAX = 0.0005
#: Relative tolerance for clamping a rounding-level negative variance to zero.
PSD_RTOL = 1e-12

CEILING_PASS = "PASS"
CEILING_FAIL = "FAIL"
CEILING_UNRESOLVED = "UNRESOLVED_AT_NUMERICAL_PRECISION"


class CriticalValueStatus(str, Enum):
    """Whether a critical value has actually been calibrated at finite N.

    The nominal normal quantile 1.959963985... is a STARTING value for the
    calibration search, not an achieved finite-N calibration.  Carrying the
    distinction in the type is what stops an uncalibrated interval being
    presented as a final result.
    """

    #: No finite-N calibration has been performed for this statistic.
    UNCALIBRATED = "UNCALIBRATED"
    #: Produced by a completed, identified finite-N calibration stream.
    CALIBRATED = "CALIBRATED"
    #: A calibration was attempted and its output is not usable.
    INVALID = "INVALID"


@dataclass(frozen=True)
class NumericalEnclosure:
    """A certified two-sided enclosure ``[lo, hi]`` of a computed quantity.

    The *point* value is what the floating-point computation returned; ``lo``
    and ``hi`` bound where the exact value lies given the certified error of
    the computation that produced it.  A quantity with no certified error
    bound has no enclosure and therefore cannot pass a threshold test.
    """

    point: float
    lo: float
    hi: float
    #: How the bound was established, for audit.
    method: str = ""

    def __post_init__(self) -> None:
        if not (math.isfinite(self.lo) and math.isfinite(self.hi)):
            return
        if self.lo > self.hi:
            raise NumericalFailure("enclosure endpoints are reversed")

    @property
    def radius(self) -> float:
        return 0.5 * (self.hi - self.lo)

    @staticmethod
    def exact(value: float, method: str = "exact") -> "NumericalEnclosure":
        return NumericalEnclosure(value, value, value, method)

    @staticmethod
    def symmetric(value: float, radius: float, method: str) -> "NumericalEnclosure":
        if not math.isfinite(radius) or radius < 0.0:
            raise NumericalFailure("enclosure radius must be finite and nonnegative")
        return NumericalEnclosure(value, value - radius, value + radius, method)


def classify_with_enclosure(
    enclosure: NumericalEnclosure | None, ceiling: float
) -> str:
    """Three-way comparison of a certified enclosure against a scientific ceiling.

    T/U ceiling semantics are inclusive, so the exact value is admissible at
    ``u == c``::

        PASS       iff u_+ <= c
        FAIL       iff u_- >  c
        UNRESOLVED otherwise

    The unresolved band is the width of THIS quantity's own certified
    numerical error.  It is not a fixed tolerance around the ceiling, and the
    ceiling is never widened.  No enclosure at all is UNRESOLVED, which is
    fail-closed: an uncertified number cannot establish which side of a
    threshold it lies on.
    """
    if enclosure is None:
        return CEILING_UNRESOLVED
    if not (math.isfinite(enclosure.lo) and math.isfinite(enclosure.hi)):
        return CEILING_FAIL
    if enclosure.hi <= ceiling:
        return CEILING_PASS
    if enclosure.lo > ceiling:
        return CEILING_FAIL
    return CEILING_UNRESOLVED


#: T-stage 20.3 error budget decomposition for the scale procedures.
BUDGET_MODEL_TAIL = 0.020
BUDGET_AUXILIARY_SET = 0.001
BUDGET_SELECTION = 0.0001
BUDGET_TOTAL = 0.025
BUDGET_RESIDUAL = BUDGET_TOTAL - BUDGET_MODEL_TAIL - BUDGET_AUXILIARY_SET - BUDGET_SELECTION


@dataclass(frozen=True)
class CriticalValues:
    """Finite-N critical values together with their calibration status."""

    c_minus: float
    c_plus: float
    #: Provenance: which calibration stream and how many draws produced these.
    provenance: str = ""
    #: Whether these values came from a completed finite-N calibration.
    status: CriticalValueStatus = CriticalValueStatus.UNCALIBRATED

    def within_ceiling(self) -> bool:
        return self.c_minus <= CRITICAL_VALUE_CEILING and self.c_plus <= CRITICAL_VALUE_CEILING

    @property
    def calibrated(self) -> bool:
        return self.status is CriticalValueStatus.CALIBRATED


#: The normal quantile, explicitly marked as NOT a finite-N calibration.  It
#: is the starting point of the calibration search and nothing more.
NORMAL_CRITICAL = CriticalValues(
    NORMAL_START, NORMAL_START,
    "normal starting value; no finite-N calibration performed",
    CriticalValueStatus.UNCALIBRATED,
)


def synthetic_calibrated(
    c_minus: float = NORMAL_START, c_plus: float = NORMAL_START,
) -> CriticalValues:
    """A clearly typed synthetic calibrated value, for unit fixtures ONLY.

    Deterministic verdict tests need a CALIBRATED critical value to exercise
    the code past the uncalibrated gate.  Its provenance says exactly what it
    is so it can never be mistaken for a campaign result.
    """
    return CriticalValues(
        c_minus, c_plus,
        "SYNTHETIC FIXTURE - not a validation calibration",
        CriticalValueStatus.CALIBRATED,
    )


@dataclass(frozen=True)
class Interval:
    lo: float
    hi: float

    def strictly_inside(self, margin: float) -> bool:
        """Strict containment in ``(-margin, margin)``; boundary equality fails."""
        return (-margin < self.lo) and (self.hi < margin)

    @property
    def width(self) -> float:
        return self.hi - self.lo


def build_interval(
    b_hat: float, se: float, crit: CriticalValues, bias_bound: float
) -> Interval:
    """``[bhat - c_- s - b, bhat + c_+ s + b]`` (T-stage 20.2)."""
    if not math.isfinite(b_hat) or not math.isfinite(se) or se < 0.0:
        raise NumericalFailure("interval requires a finite estimate and a nonnegative SE")
    if bias_bound < 0.0:
        raise NumericalFailure("bias bound must be nonnegative")
    return Interval(b_hat - crit.c_minus * se - bias_bound, b_hat + crit.c_plus * se + bias_bound)


def contrast_variance(c_b: Matrix, j: int, ref: int) -> float:
    """``Var(b_j - b_0) = C[j,j] + C[0,0] - 2 C[j,0]`` (T-stage section 10)."""
    v = c_b[j][j] + c_b[ref][ref] - 2.0 * c_b[j][ref]
    if v < 0.0:
        # Relative to the covariance's OWN diagonal scale.  A max(1.0, .) floor
        # would make this an absolute test, and log-beta variances are of order
        # 1e-5, so it would mask a genuine PSD violation.
        scale = max(abs(c_b[j][j]), abs(c_b[ref][ref]))
        if scale > 0.0 and v > -PSD_RTOL * scale:
            return 0.0
        raise NumericalFailure(
            f"contrast variance {v:.3e} is negative beyond rounding "
            f"(diagonal scale {scale:.3e}); the covariance is not PSD"
        )
    return v


def absolute_qualification(c_cal: Matrix) -> tuple[bool, list[float]]:
    """Check every diagonal calibration standard uncertainty against 0.009 (U.23).

    The comparison uses the standard uncertainty itself, never an expanded
    confidence half-width.
    """
    if not c_cal:
        # all(()) is True.  An empty calibration covariance is the ABSENCE of
        # a qualification, so returning a pass from it would make supplying
        # nothing the strongest possible evidence.
        raise NumericalFailure(
            "no calibration covariance supplied; an empty qualification is "
            "not a passed qualification"
        )
    sds = [math.sqrt(max(0.0, c_cal[i][i])) for i in range(len(c_cal))]
    return all(s <= SIGMA_CAL_ABS_MAX for s in sds), sds


def contrast_qualification(
    c_cal: Matrix, pairs: Sequence[tuple[int, int]]
) -> tuple[bool, list[float]]:
    """Check every within-block contrast standard uncertainty against 0.003 (U.24)."""
    if not pairs:
        raise NumericalFailure(
            "no contrast pairs supplied; an empty qualification is not a "
            "passed qualification"
        )
    sds = [math.sqrt(contrast_variance(c_cal, j, ref)) for j, ref in pairs]
    return all(s <= SIGMA_CAL_CONTRAST_MAX for s in sds), sds


def bias_qualification(
    abs_bias: Sequence[float], contrast_bias: Sequence[float]
) -> tuple[bool, bool]:
    """Check (U.22): absolute and contrast bounded bias, each against 0.0005.

    The contrast bound is checked on its own correlated calculation; it is
    never inferred from two absolute bounds, which would give only 0.001.
    """
    if not abs_bias or not contrast_bias:
        raise NumericalFailure(
            "bias qualification requires at least one absolute and one "
            "contrast bound; an empty set is not a qualified set"
        )
    ok_abs = all(abs(b) <= BIAS_ABS_MAX for b in abs_bias)
    ok_con = all(abs(b) <= BIAS_CONTRAST_MAX for b in contrast_bias)
    return ok_abs, ok_con


def contrast_bias_from_absolute(abs_bias: Sequence[float]) -> float:
    """The *only* bound two absolute bias bounds imply for a contrast: their sum."""
    if len(abs_bias) != 2:
        raise NumericalFailure("contrast bias implication needs exactly two absolute bounds")
    return abs(abs_bias[0]) + abs(abs_bias[1])


@dataclass(frozen=True)
class UpperLimit:
    """A calibrated one-sided upper confidence limit for a nonnegative statistic."""

    statistic: float
    limit: float
    tolerance: float

    @property
    def passes(self) -> bool:
        return self.limit < self.tolerance


def calibrated_upper_limit(
    statistic: float, radius: float, tolerance: float
) -> UpperLimit:
    """Upper limit from a calibrated confidence radius.

    The radius comes from V-stage calibration of the statistic's finite-N law,
    including its nonregular behaviour at the zero-distance boundary.  A zero
    Wald error at that boundary is explicitly not used.
    """
    if radius < 0.0:
        raise NumericalFailure("calibration radius must be nonnegative")
    return UpperLimit(statistic, statistic + radius, tolerance)
