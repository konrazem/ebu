"""Frozen model-diagnostic family: Layer J.

T-stage section 18 fixes the statistic as the maximum of three components,
each scaled by its frozen null standard deviation and calibrated jointly so
the dependence between components is preserved:

1. Cramer-von Mises distance of squared innovation radii from ``chi2_2``;
2. summed squared sine/cosine sample means at angular harmonics 1 through 4;
3. squared Frobenius norms of innovation lag covariances at lags 1 through 10,
   together with the three observed-minus-fitted lag-antisymmetry checks.

The lags and harmonics are fixed here, before any calibration; no search for a
favourable subset is permitted.  A zero or undefined null scale is a validation
failure, not a dropped component.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence

from . import numerics as nm
from .numerics import Matrix, NumericalFailure

#: Frozen diagnostic constants.
ANGULAR_HARMONICS = (1, 2, 3, 4)
INNOVATION_LAGS = tuple(range(1, 11))
#: Familywise false-rejection target across all eight records.
FAMILYWISE_TARGET = 0.005


def standardise_innovations(
    innovations: Sequence[Sequence[float]], inn_cov: Matrix
) -> list[list[float]]:
    """Whiten innovations by the steady-state innovation covariance."""
    w = nm.inv_sqrtm_spd(inn_cov)
    d = len(inn_cov)
    return [
        [sum(w[i][j] * v[j] for j in range(d)) for i in range(d)] for v in innovations
    ]


def cvm_chi2_2(z: Sequence[Sequence[float]]) -> float:
    """Cramer-von Mises distance of squared radii from ``chi2_2``.

    Under the null ``|z|^2 ~ chi2_2``, so ``U = 1 - exp(-|z|^2/2)`` is uniform.
    """
    n = len(z)
    if n == 0:
        raise NumericalFailure("empty innovation sequence")
    u = sorted(1.0 - math.exp(-0.5 * (v[0] * v[0] + v[1] * v[1])) for v in z)
    acc = 1.0 / (12.0 * n)
    for i, ui in enumerate(u, start=1):
        acc += (ui - (2.0 * i - 1.0) / (2.0 * n)) ** 2
    return acc


def angular_harmonic_statistic(z: Sequence[Sequence[float]]) -> float:
    """Summed squared circular means at the frozen harmonics 1..4."""
    n = len(z)
    if n == 0:
        raise NumericalFailure("empty innovation sequence")
    total = 0.0
    angles = [math.atan2(v[1], v[0]) for v in z]
    for k in ANGULAR_HARMONICS:
        c = sum(math.cos(k * a) for a in angles) / n
        s = sum(math.sin(k * a) for a in angles) / n
        total += c * c + s * s
    return total


def lag_covariance_statistic(z: Sequence[Sequence[float]]) -> float:
    """Summed squared Frobenius norms of innovation lag covariances, lags 1..10."""
    n = len(z)
    d = 2
    total = 0.0
    for lag in INNOVATION_LAGS:
        if lag >= n:
            raise NumericalFailure("record too short for the frozen diagnostic lags")
        count = n - lag
        acc = nm.zeros(d, d)
        for t in range(count):
            a, b = z[t], z[t + lag]
            for i in range(d):
                for j in range(d):
                    acc[i][j] += a[i] * b[j]
        total += sum((acc[i][j] / count) ** 2 for i in range(d) for j in range(d))
    return total


def lag_antisymmetry_residuals(
    observed: Sequence[Matrix], fitted: Sequence[Matrix]
) -> float:
    """Observed-minus-fitted lag-antisymmetry residual, summed in squares.

    The free model may contain a current, so a nonzero *raw* lag asymmetry is
    not by itself a goodness-of-fit failure; only the residual against the
    fitted model enters the diagnostic family.
    """
    if len(observed) != len(fitted):
        raise NumericalFailure("observed and fitted lag sets must align")
    total = 0.0
    for o, f in zip(observed, fitted):
        diff = nm.sub(o, f)
        anti = nm.scale(nm.sub(diff, nm.transpose(diff)), 0.5)
        total += sum(v * v for row in anti for v in row)
    return total


@dataclass(frozen=True)
class NullScales:
    """Frozen null standard deviations for each diagnostic component."""

    cvm: float
    angular: float
    lagcov: float
    antisym: float
    cvm_mean: float = 0.0
    angular_mean: float = 0.0
    lagcov_mean: float = 0.0
    antisym_mean: float = 0.0

    def validate(self) -> None:
        for name in ("cvm", "angular", "lagcov", "antisym"):
            v = getattr(self, name)
            if not math.isfinite(v) or v <= 0.0:
                raise NumericalFailure(
                    f"diagnostic component {name!r} has a zero or undefined null scale; "
                    "this is a validation failure, not a dropped component"
                )


@dataclass(frozen=True)
class DiagnosticComponents:
    cvm: float
    angular: float
    lagcov: float
    antisym: float

    def scaled_max(self, scales: NullScales) -> float:
        scales.validate()
        return max(
            (self.cvm - scales.cvm_mean) / scales.cvm,
            (self.angular - scales.angular_mean) / scales.angular,
            (self.lagcov - scales.lagcov_mean) / scales.lagcov,
            (self.antisym - scales.antisym_mean) / scales.antisym,
        )


def diagnostic_components(
    innovations: Sequence[Sequence[float]],
    inn_cov: Matrix,
    observed_lags: Sequence[Matrix] | None = None,
    fitted_lags: Sequence[Matrix] | None = None,
) -> DiagnosticComponents:
    """Compute the four frozen diagnostic components for one record."""
    z = standardise_innovations(innovations, inn_cov)
    anti = 0.0
    if observed_lags is not None and fitted_lags is not None:
        anti = lag_antisymmetry_residuals(observed_lags, fitted_lags)
    return DiagnosticComponents(
        cvm=cvm_chi2_2(z),
        angular=angular_harmonic_statistic(z),
        lagcov=lag_covariance_statistic(z),
        antisym=anti,
    )
