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
#: Declared numerical precision of the propagated calibration sensitivity.
#: The log-beta sensitivity is obtained by differencing a numerically located
#: pseudo-true maximum, so it carries about this relative error; a comparison
#: against a ceiling cannot be sharper than its own inputs.
CALIBRATION_NUMERICAL_RTOL = 1e-5

CEILING_PASS = "PASS"
CEILING_FAIL = "FAIL"
CEILING_UNRESOLVED = "UNRESOLVED_AT_NUMERICAL_PRECISION"


def classify_against_ceiling(
    value: float, ceiling: float, rtol: float = CALIBRATION_NUMERICAL_RTOL
) -> str:
    """Three-way comparison of a propagated quantity against a declared ceiling.

    A value within the sensitivity's own numerical precision of the ceiling is
    UNRESOLVED, not a pass: the enclosure straddles the boundary, exactly as
    the realized-field predicates treat a straddling region.
    """
    if not math.isfinite(value):
        return CEILING_FAIL
    band = rtol * ceiling
    if value <= ceiling - band:
        return CEILING_PASS
    if value > ceiling + band:
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
    """Frozen finite-N calibrated critical values."""

    c_minus: float
    c_plus: float
    #: Provenance: which calibration stream and how many draws produced these.
    provenance: str = ""

    def within_ceiling(self) -> bool:
        return self.c_minus <= CRITICAL_VALUE_CEILING and self.c_plus <= CRITICAL_VALUE_CEILING


NORMAL_CRITICAL = CriticalValues(NORMAL_START, NORMAL_START, "normal starting value")


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
    sds = [math.sqrt(max(0.0, c_cal[i][i])) for i in range(len(c_cal))]
    return all(s <= SIGMA_CAL_ABS_MAX for s in sds), sds


def contrast_qualification(
    c_cal: Matrix, pairs: Sequence[tuple[int, int]]
) -> tuple[bool, list[float]]:
    """Check every within-block contrast standard uncertainty against 0.003 (U.24)."""
    sds = [math.sqrt(contrast_variance(c_cal, j, ref)) for j, ref in pairs]
    return all(s <= SIGMA_CAL_CONTRAST_MAX for s in sds), sds


def bias_qualification(
    abs_bias: Sequence[float], contrast_bias: Sequence[float]
) -> tuple[bool, bool]:
    """Check (U.22): absolute and contrast bounded bias, each against 0.0005.

    The contrast bound is checked on its own correlated calculation; it is
    never inferred from two absolute bounds, which would give only 0.001.
    """
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
