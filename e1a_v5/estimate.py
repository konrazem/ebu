"""Record-level estimation driver.

Fits one record twice, as the design requires:

* the **locked** fit, with the physical ``H_A`` fixed from Branch A, which
  yields ``b = log beta``;
* the **free** fit, with an unrestricted SPD latent covariance, which supplies
  the geometry, centre and reversibility statistics.

``H_A`` is never refitted from Branch B.  The moment estimator is provided
only as a diagnostic reference (:func:`moment_log_beta`); the primary
estimator is always the actual likelihood maximiser.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence

from . import numerics as nm
from .likelihood import (
    N_PARAMS_FREE,
    N_PARAMS_LOCKED,
    Parameters,
    chol_params_from_spd,
    drift_of,
    irreversibility_ratio,
    log_likelihood,
    pack,
    sigma_of,
    spd_from_chol,
    unpack,
)
from .numerics import Matrix, NumericalFailure
from .optimize import OptimizerFailure, minimise

#: Frozen finite-difference step for the profile curvature of ``log beta``.
SE_STEP = 1e-3
#: Frozen fallback ladder of steps if the first curvature is not positive.
SE_STEP_LADDER = (1e-3, 3e-3, 1e-2)


@dataclass(frozen=True)
class RecordFit:
    log_beta: float
    log_beta_se: float
    mu: tuple[float, float]
    sigma_free: Matrix
    mu_free: tuple[float, float]
    a_free: Matrix
    r_irr: float
    loglik_locked: float
    loglik_free: float
    innovations: list[list[float]]
    innovation_cov: Matrix
    evaluations: int
    converged: bool


def moment_log_beta(sample_cov: Matrix, h_a: Matrix) -> float:
    """Diagnostic moment estimator ``log[d / tr(H_A S)]`` (T-stage 13.2).

    This is a reference quantity only.  It ignores observation noise, exposure
    blur and temporal correlation, so it differs from the likelihood maximiser
    whenever any of those is present.
    """
    d = len(h_a)
    tr = sum(h_a[i][j] * sample_cov[j][i] for i in range(d) for j in range(d))
    if tr <= 0.0 or not math.isfinite(tr):
        raise NumericalFailure("moment estimator trace is not positive")
    return math.log(d / tr)


def _sample_moments(
    y: Sequence[Sequence[float]], p_matrix: Matrix, b_det: Sequence[float]
) -> tuple[list[float], Matrix]:
    """Detector-space moments mapped back to physical coordinates."""
    n = len(y)
    d = len(p_matrix)
    pinv = nm.general_inverse(p_matrix)
    xs = [
        [sum(pinv[i][j] * (y[t][j] - b_det[j]) for j in range(d)) for i in range(d)]
        for t in range(n)
    ]
    mean = [sum(row[i] for row in xs) / n for i in range(d)]
    cov = nm.zeros(d, d)
    for row in xs:
        for i in range(d):
            di = row[i] - mean[i]
            for j in range(d):
                cov[i][j] += di * (row[j] - mean[j])
    cov = [[cov[i][j] / (n - 1) for j in range(d)] for i in range(d)]
    return mean, nm.symmetrise(cov)


def _initial_parameters(
    y: Sequence[Sequence[float]],
    h_a: Matrix,
    p_matrix: Matrix,
    b_det: Sequence[float],
    dt: float,
    free_sigma: bool,
) -> Parameters:
    """Frozen initialisation rule: moments for scale and centre, lag-1 for dynamics."""
    mean, cov = _sample_moments(y, p_matrix, b_det)
    d = len(h_a)
    if free_sigma:
        sigma0 = cov
        sigma_chol = chol_params_from_spd(sigma0)
        log_beta0 = 0.0
    else:
        sigma_chol = None
        log_beta0 = moment_log_beta(cov, h_a)
        sigma0 = nm.scale(nm.spd_inverse(h_a), math.exp(-log_beta0))

    # Lag-1 autocovariance gives F ~ exp(-A dt), hence an A initialisation.
    n = len(y)
    lag1 = nm.zeros(d, d)
    pinv = nm.general_inverse(p_matrix)
    xs = [
        [sum(pinv[i][j] * (y[t][j] - b_det[j]) for j in range(d)) for i in range(d)]
        for t in range(n)
    ]
    for t in range(n - 1):
        for i in range(d):
            di = xs[t][i] - mean[i]
            for j in range(d):
                lag1[i][j] += di * (xs[t + 1][j] - mean[j])
    lag1 = [[lag1[i][j] / (n - 1) for j in range(d)] for i in range(d)]
    try:
        f_est = nm.transpose(nm.lu_solve(nm.symmetrise(cov), nm.transpose(lag1)))
        rate = nm.scale(nm.logm_spd(nm.symmetrise(nm.matmul(f_est, nm.transpose(f_est)))), -0.5 / dt)
        a0 = nm.symmetrise(rate)
        vals, _ = nm.eigh(a0)
        if min(vals) <= 0.0:
            raise NumericalFailure("non-positive initial relaxation rate")
    except NumericalFailure:
        a0 = nm.scale(nm.eye(d), 1.0 / (10.0 * dt))
    asig = nm.matmul(a0, sigma0)
    d_init = nm.symmetrise(nm.scale(nm.add(asig, nm.transpose(asig)), 0.5))
    try:
        d_chol = chol_params_from_spd(d_init)
    except NumericalFailure:
        d_chol = chol_params_from_spd(nm.scale(sigma0, 1.0 / (10.0 * dt)))

    return Parameters(
        log_beta=log_beta0,
        mu=(mean[0], mean[1]),
        d_chol=d_chol,
        omega=0.0,
        sigma_chol=sigma_chol,
    )


def _fit(
    y: Sequence[Sequence[float]],
    h_a: Matrix | None,
    p_matrix: Matrix,
    r_obs: Matrix,
    b_det: Sequence[float],
    dt: float,
    t_exp: float,
    free_sigma: bool,
) -> tuple[Parameters, float, int, bool]:
    init = _initial_parameters(y, h_a if h_a is not None else nm.eye(2), p_matrix, b_det, dt, free_sigma)

    def objective(x: Sequence[float]) -> float:
        params = unpack(x, free_sigma)
        return -log_likelihood(
            params, h_a, y, p_matrix, r_obs, b_det, dt, t_exp
        ).loglik

    res = minimise(objective, pack(init, free_sigma))
    if not res.converged:
        raise OptimizerFailure(f"locked={not free_sigma}: {res.reason or 'did not converge'}")
    return unpack(res.x, free_sigma), -res.fun, res.evaluations, res.converged


def _profile_se(
    best: Parameters,
    h_a: Matrix,
    y: Sequence[Sequence[float]],
    p_matrix: Matrix,
    r_obs: Matrix,
    b_det: Sequence[float],
    dt: float,
    t_exp: float,
    ll_hat: float,
) -> float:
    """Standard error of ``log beta`` from the profile curvature at the maximum."""
    for step in SE_STEP_LADDER:
        vals = []
        ok = True
        for sign in (-1.0, 1.0):
            trial = Parameters(
                log_beta=best.log_beta + sign * step,
                mu=best.mu,
                d_chol=best.d_chol,
                omega=best.omega,
                sigma_chol=None,
            )

            def obj(x: Sequence[float], lb=trial.log_beta) -> float:
                p = Parameters(
                    log_beta=lb,
                    mu=(x[0], x[1]),
                    d_chol=(x[2], x[3], x[4]),
                    omega=x[5],
                    sigma_chol=None,
                )
                return -log_likelihood(p, h_a, y, p_matrix, r_obs, b_det, dt, t_exp).loglik

            try:
                res = minimise(
                    obj,
                    [best.mu[0], best.mu[1], *best.d_chol, best.omega],
                    max_evaluations=1200,
                )
            except OptimizerFailure:
                ok = False
                break
            vals.append(-res.fun)
        if not ok or len(vals) != 2:
            continue
        curv = (2.0 * ll_hat - vals[0] - vals[1]) / (step * step)
        if curv > 0.0 and math.isfinite(curv):
            return 1.0 / math.sqrt(curv)
    raise OptimizerFailure("profile curvature for log beta is not positive")


def fit_record(
    y: Sequence[Sequence[float]],
    h_a: Matrix,
    p_matrix: Matrix,
    r_obs: Matrix,
    b_det: Sequence[float],
    dt: float,
    t_exp: float,
    want_free: bool = True,
) -> RecordFit:
    """Fit one record: locked scale fit plus the unrestricted characterisation."""
    locked, ll_locked, ev1, conv1 = _fit(
        y, h_a, p_matrix, r_obs, b_det, dt, t_exp, free_sigma=False
    )
    se = _profile_se(locked, h_a, y, p_matrix, r_obs, b_det, dt, t_exp, ll_locked)

    if want_free:
        free, ll_free, ev2, conv2 = _fit(
            y, None, p_matrix, r_obs, b_det, dt, t_exp, free_sigma=True
        )
        sigma_free = spd_from_chol(free.sigma_chol)  # type: ignore[arg-type]
        a_free = drift_of(free, sigma_free)
        r_irr = irreversibility_ratio(free, sigma_free)
        mu_free = free.mu
        fit_for_innov = free
        h_for_innov = None
    else:
        free = locked
        ll_free, ev2, conv2 = ll_locked, 0, True
        sigma_free = sigma_of(locked, h_a)
        a_free = drift_of(locked, sigma_free)
        r_irr = irreversibility_ratio(locked, sigma_free)
        mu_free = locked.mu
        fit_for_innov = locked
        h_for_innov = h_a

    out = log_likelihood(
        fit_for_innov, h_for_innov, y, p_matrix, r_obs, b_det, dt, t_exp,
        collect_innovations=True,
    )

    return RecordFit(
        log_beta=locked.log_beta,
        log_beta_se=se,
        mu=locked.mu,
        sigma_free=sigma_free,
        mu_free=mu_free,
        a_free=a_free,
        r_irr=r_irr,
        loglik_locked=ll_locked,
        loglik_free=ll_free,
        innovations=out.innovations,
        innovation_cov=out.innovation_cov,
        evaluations=ev1 + ev2,
        converged=conv1 and conv2,
    )
