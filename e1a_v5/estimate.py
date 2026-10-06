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

#: Target log-likelihood drop for the profile curvature step.  Choosing the
#: step so the drop is of order one keeps the second difference far above the
#: optimiser's own noise floor; a fixed small step suffers catastrophic
#: cancellation because the log likelihood itself is O(N).
SE_TARGET_DROP = 0.5
#: Admissible window for the achieved drop before the step is rescaled.
SE_DROP_MIN = 0.02
SE_DROP_MAX = 8.0
#: Maximum step rescalings.
SE_MAX_ROUNDS = 6
#: Initial step, used only to measure the local curvature scale.
SE_INITIAL_STEP = 0.02
#: Inner-optimiser evaluation budget for each profile point.
SE_INNER_EVALUATIONS = 1500


@dataclass(frozen=True)
class RecordFit:
    log_beta: float
    #: Standard error, present ONLY when ``profile.usable`` is true.
    log_beta_se: float | None
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
    profile: "ProfileFit | None" = None

    @property
    def inferential(self) -> bool:
        """True only when a confidence interval may be published from this fit."""
        return (
            self.converged
            and self.profile is not None
            and self.profile.usable
            and self.log_beta_se is not None
        )


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


@dataclass(frozen=True)
class Scaling:
    """Affine map from dimensionless optimiser coordinates to model parameters.

    The raw parameters are badly scaled for a simplex method: ``mu`` is a
    physical length of order 1e-8 m, while ``d_chol`` holds logarithms of
    Cholesky entries whose magnitude is of order 40.  One relative step size
    cannot serve both, and a 5 percent relative step on a logarithm of
    magnitude 40 is a factor-of-seven jump that destroys the simplex.  Every
    optimiser coordinate here is dimensionless and of order one, measured
    against the frozen initialisation.
    """

    mu_scale: float
    l11_init: float
    l21_init: float
    l22_init: float
    omega_scale: float
    s11_init: float = 1.0
    s21_init: float = 0.0
    s22_init: float = 1.0

    def to_parameters(self, u: Sequence[float], free_sigma: bool) -> Parameters:
        if free_sigma:
            sigma_chol = (
                math.log(self.s11_init) + u[0],
                self.s21_init + u[1] * self.s11_init,
                math.log(self.s22_init) + u[2],
            )
            rest = list(u[3:])
            log_beta = 0.0
        else:
            sigma_chol = None
            log_beta = u[0]
            rest = list(u[1:])
        return Parameters(
            log_beta=log_beta,
            mu=(rest[0] * self.mu_scale, rest[1] * self.mu_scale),
            d_chol=(
                math.log(self.l11_init) + rest[2],
                self.l21_init + rest[3] * self.l11_init,
                math.log(self.l22_init) + rest[4],
            ),
            omega=rest[5] * self.omega_scale,
            sigma_chol=sigma_chol,
        )

    def from_parameters(self, p: Parameters, free_sigma: bool) -> list[float]:
        rest = [
            p.mu[0] / self.mu_scale,
            p.mu[1] / self.mu_scale,
            p.d_chol[0] - math.log(self.l11_init),
            (p.d_chol[1] - self.l21_init) / self.l11_init,
            p.d_chol[2] - math.log(self.l22_init),
            p.omega / self.omega_scale,
        ]
        if free_sigma:
            if p.sigma_chol is None:
                raise NumericalFailure("free-sigma scaling requires sigma_chol")
            return [
                p.sigma_chol[0] - math.log(self.s11_init),
                (p.sigma_chol[1] - self.s21_init) / self.s11_init,
                p.sigma_chol[2] - math.log(self.s22_init),
                *rest,
            ]
        return [p.log_beta, *rest]


def _scaling_for(init: Parameters, sigma0: Matrix, free_sigma: bool) -> Scaling:
    l11 = math.exp(init.d_chol[0])
    l22 = math.exp(init.d_chol[2])
    omega_scale = max(l11 * l11, 1e-300)
    mu_scale = math.sqrt(sigma0[0][0]) if sigma0[0][0] > 0.0 else 1.0
    if free_sigma:
        if init.sigma_chol is None:
            raise NumericalFailure("free-sigma scaling requires sigma_chol")
        return Scaling(
            mu_scale, l11, init.d_chol[1], l22, omega_scale,
            math.exp(init.sigma_chol[0]), init.sigma_chol[1], math.exp(init.sigma_chol[2]),
        )
    return Scaling(mu_scale, l11, init.d_chol[1], l22, omega_scale)


def _fit(
    y: Sequence[Sequence[float]],
    h_a: Matrix | None,
    p_matrix: Matrix,
    r_obs: Matrix,
    b_det: Sequence[float],
    dt: float,
    t_exp: float,
    free_sigma: bool,
) -> tuple[Parameters, float, int, bool, Scaling]:
    """Maximise the exact likelihood in dimensionless optimiser coordinates."""
    href = h_a if h_a is not None else nm.eye(2)
    init = _initial_parameters(y, href, p_matrix, b_det, dt, free_sigma)
    sigma0 = sigma_of(init, href)
    scaling = _scaling_for(init, sigma0, free_sigma)
    u0 = scaling.from_parameters(init, free_sigma)
    # Offset the objective so the optimiser's relative tolerance acts on an
    # O(1) quantity rather than on a log likelihood of order N.
    ll0 = log_likelihood(init, h_a, y, p_matrix, r_obs, b_det, dt, t_exp).loglik

    def objective(u: Sequence[float]) -> float:
        params = scaling.to_parameters(u, free_sigma)
        return -(
            log_likelihood(params, h_a, y, p_matrix, r_obs, b_det, dt, t_exp).loglik - ll0
        )

    res = minimise(objective, u0)
    if not res.converged:
        raise OptimizerFailure(f"locked={not free_sigma}: {res.reason or 'did not converge'}")
    return (
        scaling.to_parameters(res.x, free_sigma),
        ll0 - res.fun,
        res.evaluations,
        res.converged,
        scaling,
    )


#: Reason codes for an unusable profile standard error.
SE_OK = "valid"
SE_PROFILE_NOT_CONVERGED = "profile_optimisation_not_converged"
SE_PROFILE_EXCEEDS_INCUMBENT = "profile_exceeds_incumbent_maximum"
SE_CURVATURE_NONPOSITIVE = "profile_curvature_nonpositive"
SE_NONFINITE = "profile_value_nonfinite"
SE_STEP_SEARCH_EXHAUSTED = "step_rescaling_exhausted"


@dataclass(frozen=True)
class ProfileFit:
    """Status of the profile standard-error calculation for ``log beta``.

    No inferential quantity may be published from a fit that is not a valid
    usable maximum, so the standard error is carried here together with the
    explicit status that licenses it.  ``value`` is ``None`` whenever
    ``status != SE_OK``; there is deliberately no way to read a number out of
    a failed profile.
    """

    status: str
    value: float | None = None
    step: float | None = None
    drop: float | None = None
    evaluations: int = 0
    #: Optimiser reason codes from the two profile points, for audit.
    point_reasons: tuple[str, ...] = ()

    @property
    def usable(self) -> bool:
        return self.status == SE_OK and self.value is not None and math.isfinite(self.value)

    def require(self) -> float:
        """Return the standard error, or raise if the profile was not usable."""
        if not self.usable:
            raise OptimizerFailure(f"standard error unavailable: {self.status}")
        return float(self.value)  # type: ignore[arg-type]


def _profile_se(
    best: Parameters,
    scaling: Scaling,
    h_a: Matrix,
    y: Sequence[Sequence[float]],
    p_matrix: Matrix,
    r_obs: Matrix,
    b_det: Sequence[float],
    dt: float,
    t_exp: float,
    ll_hat: float,
) -> ProfileFit:
    """Standard error of ``log beta`` from the profile curvature at the maximum.

    Both profile points must themselves be converged, usable optimisations.  A
    non-converged profile point, a non-finite value, a profile that beats the
    incumbent, or a non-positive curvature each yields an UNUSABLE result with
    its reason; none of them yields a number.  The step is chosen adaptively so
    the profile drop is of order one, because the log likelihood is ``O(N)``
    and a fixed small step makes the second difference a difference of nearly
    equal large numbers.
    """
    u_best = scaling.from_parameters(best, False)
    total_evals = 0

    def profile_at(log_beta: float) -> tuple[float | None, str, int]:
        """Maximised log likelihood with ``log beta`` fixed, offset by ``ll_hat``."""

        def obj(u: Sequence[float]) -> float:
            p = scaling.to_parameters([log_beta, *u], False)
            return -(
                log_likelihood(p, h_a, y, p_matrix, r_obs, b_det, dt, t_exp).loglik - ll_hat
            )

        try:
            res = minimise(obj, u_best[1:], max_evaluations=SE_INNER_EVALUATIONS)
        except OptimizerFailure as exc:
            return None, f"optimiser_failure:{exc}", 0
        if not res.usable:
            return None, res.reason or SE_PROFILE_NOT_CONVERGED, res.evaluations
        return -res.fun, res.reason, res.evaluations

    step = SE_INITIAL_STEP
    reasons: list[str] = []
    for _ in range(SE_MAX_ROUNDS):
        lo, lo_reason, lo_ev = profile_at(best.log_beta - step)
        hi, hi_reason, hi_ev = profile_at(best.log_beta + step)
        total_evals += lo_ev + hi_ev
        reasons = [lo_reason, hi_reason]
        if lo is None or hi is None:
            # A non-converged profile point is NOT a licence to shrink the step
            # and try again with a number taken from the final iterate.
            return ProfileFit(SE_PROFILE_NOT_CONVERGED, None, step, None,
                              total_evals, tuple(reasons))
        drop = -0.5 * (lo + hi)
        if not math.isfinite(drop):
            return ProfileFit(SE_NONFINITE, None, step, None, total_evals, tuple(reasons))
        if drop <= 0.0:
            return ProfileFit(SE_PROFILE_EXCEEDS_INCUMBENT, None, step, drop,
                              total_evals, tuple(reasons))
        if SE_DROP_MIN <= drop <= SE_DROP_MAX:
            curv = 2.0 * drop / (step * step)
            if curv > 0.0 and math.isfinite(curv):
                se = 1.0 / math.sqrt(curv)
                if not math.isfinite(se) or se <= 0.0:
                    return ProfileFit(SE_NONFINITE, None, step, drop,
                                      total_evals, tuple(reasons))
                return ProfileFit(SE_OK, se, step, drop, total_evals, tuple(reasons))
            return ProfileFit(SE_CURVATURE_NONPOSITIVE, None, step, drop,
                              total_evals, tuple(reasons))
        step *= math.sqrt(SE_TARGET_DROP / drop)
        if not math.isfinite(step) or step <= 0.0:
            break
    return ProfileFit(SE_STEP_SEARCH_EXHAUSTED, None, step, None,
                      total_evals, tuple(reasons))


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
    locked, ll_locked, ev1, conv1, scaling = _fit(
        y, h_a, p_matrix, r_obs, b_det, dt, t_exp, free_sigma=False
    )
    profile = _profile_se(
        locked, scaling, h_a, y, p_matrix, r_obs, b_det, dt, t_exp, ll_locked
    )
    if not profile.usable:
        # No inferential quantity is published from a fit that did not
        # establish a valid usable maximum.
        raise OptimizerFailure(
            f"profile standard error unavailable: {profile.status} "
            f"(points {profile.point_reasons})"
        )
    se = profile.value

    if want_free:
        free, ll_free, ev2, conv2, _ = _fit(
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
        profile=profile,
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
