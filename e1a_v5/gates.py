"""Geometry, centre, stationarity and reversibility gates: Layers H and I.

All four are positive precision requirements evaluated as calibrated one-sided
97.5% upper confidence limits, not failures to reject an exact equality.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence

from . import numerics as nm
from .numerics import Matrix, NumericalFailure

#: T-stage T.9 tolerances.
DELTA_G = math.log(1.05)
DELTA_M = 0.10
#: T-stage T.10 reversibility tolerance.
DELTA_R_IRR = 0.02
#: T-stage 12.1 stationarity component scales.
STATIONARITY_CENTRE_SCALE = 0.10
STATIONARITY_COV_SCALE = math.log(1.05)
#: Number of fixed equal-duration quarters.
N_QUARTERS = 4
#: Relative tolerance for cancellation noise in the centre quadratic form.
QUADRATIC_RTOL = 1e-12


def geometry_statistic(sigma_b: Matrix, h_a: Matrix) -> float:
    """``G = || log M - (log|M|/d) I ||_op`` with ``M = R Sigma_B R^T``, ``H_A = R^T R``.

    ``G = 0`` exactly when ``Sigma_B`` is a positive scalar multiple of
    ``H_A^{-1}``; the statistic is scale-free by construction.
    """
    d = len(h_a)
    L = nm.cholesky(h_a)           # H_A = L L^T, so R = L^T
    r = nm.transpose(L)
    m = nm.symmetrise(nm.matmul(nm.matmul(r, sigma_b), nm.transpose(r)))
    logm = nm.logm_spd(m)
    tr = sum(logm[i][i] for i in range(d))
    dev = [[logm[i][j] - (tr / d if i == j else 0.0) for j in range(d)] for i in range(d)]
    return nm.op_norm_sym(nm.symmetrise(dev))


def centre_statistic(mu_b: Sequence[float], x_star: Sequence[float], h_a: Matrix) -> float:
    """``m = sqrt((mu_B - x_A*)^T H_A (mu_B - x_A*))`` in thermal coordinate units."""
    d = len(h_a)
    delta = [mu_b[i] - x_star[i] for i in range(d)]
    terms = [delta[i] * h_a[i][j] * delta[j] for i in range(d) for j in range(d)]
    q = sum(terms)
    if q < 0.0:
        # Scale by the magnitude of the summands, which is what cancellation
        # noise is proportional to.  Scaling by |q| itself is meaningless when
        # q is near zero, and a max(1.0, .) floor makes this an absolute test.
        scale = sum(abs(t) for t in terms)
        if scale > 0.0 and q > -QUADRATIC_RTOL * scale:
            q = 0.0
        else:
            raise NumericalFailure(
                f"centre quadratic form {q:.3e} is negative beyond cancellation "
                f"noise (summand scale {scale:.3e}); H_A is not SPD"
            )
    return math.sqrt(q)


def covariance_log_distance(sigma_u: Matrix, sigma_v: Matrix) -> float:
    """Affine-invariant distance: max |log generalised eigenvalue| of the pair."""
    lam = nm.generalized_eigvals_spd(sigma_u, sigma_v)
    if any(v <= 0.0 or not math.isfinite(v) for v in lam):
        raise NumericalFailure("generalised eigenvalues must be positive")
    return max(abs(math.log(v)) for v in lam)


@dataclass(frozen=True)
class StationarityOutcome:
    statistic: float
    worst_pair: tuple[int, int]
    centre_component: float
    covariance_component: float


def stationarity_statistic(
    quarter_means: Sequence[Sequence[float]],
    quarter_covs: Sequence[Matrix],
    h_a: Matrix,
) -> StationarityOutcome:
    """Maximum over all six quarter-pair contrasts of the two scaled components.

    Component (i) is the thermal centre separation divided by 0.10; component
    (ii) is the affine-invariant covariance log distance divided by log(1.05).
    No drift is estimated from the bead path and subtracted.
    """
    if len(quarter_means) != N_QUARTERS or len(quarter_covs) != N_QUARTERS:
        raise NumericalFailure(f"stationarity gate requires exactly {N_QUARTERS} quarters")
    best = -math.inf
    pair = (0, 0)
    c_comp = cov_comp = 0.0
    for u in range(N_QUARTERS):
        for v in range(u + 1, N_QUARTERS):
            sep = centre_statistic(quarter_means[u], quarter_means[v], h_a)
            c1 = sep / STATIONARITY_CENTRE_SCALE
            c2 = covariance_log_distance(quarter_covs[u], quarter_covs[v]) / STATIONARITY_COV_SCALE
            local = max(c1, c2)
            if local > best:
                best, pair, c_comp, cov_comp = local, (u, v), c1, c2
    return StationarityOutcome(best, pair, c_comp, cov_comp)


def irreversibility_from_matrices(a_drift: Matrix, sigma: Matrix) -> float:
    """``r_irr = ||Omega||_op / lambda_min(S)`` with ``B = Sigma^{-1/2} A Sigma^{1/2}``."""
    w = nm.inv_sqrtm_spd(sigma)
    wi = nm.sqrtm_spd(sigma)
    b = nm.matmul(nm.matmul(w, a_drift), wi)
    bt = nm.transpose(b)
    s_mat = nm.symmetrise(nm.scale(nm.add(b, bt), 0.5))
    omega = nm.scale(nm.sub(b, bt), 0.5)
    vals, _ = nm.eigh(s_mat)
    lam_min = min(vals)
    if lam_min <= 0.0:
        raise NumericalFailure("symmetric part of the whitened drift is not positive definite")
    return nm.op_norm(omega) / lam_min


def lag_covariance(
    series: Sequence[Sequence[float]], lag: int, mean: Sequence[float] | None = None
) -> Matrix:
    """Sample lag covariance ``E[(x_t - m)(x_{t+lag} - m)^T]``."""
    n = len(series)
    d = len(series[0])
    if lag >= n:
        raise NumericalFailure("lag exceeds the record length")
    if mean is None:
        mean = [sum(row[k] for row in series) / n for k in range(d)]
    out = nm.zeros(d, d)
    count = n - lag
    for t in range(count):
        a = series[t]
        b = series[t + lag]
        for i in range(d):
            ai = a[i] - mean[i]
            for j in range(d):
                out[i][j] += ai * (b[j] - mean[j])
    return [[out[i][j] / count for j in range(d)] for i in range(d)]


def lag_antisymmetry(series: Sequence[Sequence[float]], lag: int) -> float:
    """Raw lag-covariance antisymmetry, a current diagnostic (T-stage 12.2)."""
    c = lag_covariance(series, lag)
    return nm.max_abs(nm.scale(nm.sub(c, nm.transpose(c)), 0.5))
