"""Stationary Gaussian state-space likelihood and estimator: Layer F.

Evaluates the exact log likelihood (T.6) of the stacked observations through an
innovations recursion with correlated process and measurement noise -- the
computational factorisation of the same Gaussian law, not an approximation.

Parameterisation (T-stage section 8.2)
--------------------------------------
``A Sigma`` is split as ``D + Q`` with ``D`` symmetric positive definite and
``Q`` antisymmetric, so ``A = (D + Q) Sigma^{-1}`` and ``L L^T = 2 D`` is
positive definite by construction.  This permits currents: ``A Sigma = Sigma
A^T`` is deliberately NOT imposed in the primary density fit.

``beta`` is carried internally as ``b = log beta``, which enforces ``beta > 0``
without a boundary constraint.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence

from . import numerics as nm
from .numerics import Matrix, NumericalFailure
from .observation import StateSpace, build_state_space

#: Riccati convergence tolerance for the steady-state innovation covariance.
RICCATI_TOL = 1e-13
#: Maximum Riccati iterations before the recursion is declared non-convergent.
RICCATI_MAX = 5000


@dataclass(frozen=True)
class Parameters:
    """Model parameters for one record."""

    log_beta: float
    mu: tuple[float, float]
    #: Cholesky parameters of D: (log l11, l21, log l22).
    d_chol: tuple[float, float, float]
    #: Antisymmetric generator strength.
    omega: float
    #: Free covariance Cholesky (log s11, s21, log s22); None locks Sigma to beta^-1 H^-1.
    sigma_chol: tuple[float, float, float] | None = None


def _chol_from_params(p: Sequence[float]) -> Matrix:
    l11 = math.exp(p[0])
    l22 = math.exp(p[2])
    return [[l11, 0.0], [float(p[1]), l22]]


def spd_from_chol(p: Sequence[float]) -> Matrix:
    L = _chol_from_params(p)
    return nm.symmetrise(nm.matmul(L, nm.transpose(L)))


def chol_params_from_spd(m: Matrix) -> tuple[float, float, float]:
    L = nm.cholesky(m)
    return (math.log(L[0][0]), L[1][0], math.log(L[1][1]))


def sigma_of(params: Parameters, h_locked: Matrix | None) -> Matrix:
    """Return the latent stationary covariance implied by ``params``."""
    if params.sigma_chol is not None:
        return spd_from_chol(params.sigma_chol)
    if h_locked is None:
        raise NumericalFailure("locked H is required when sigma_chol is absent")
    beta = math.exp(params.log_beta)
    return nm.symmetrise(nm.scale(nm.spd_inverse(h_locked), 1.0 / beta))


def drift_of(params: Parameters, sigma: Matrix) -> Matrix:
    """``A = (D + Q) Sigma^{-1}`` with ``D`` SPD and ``Q`` antisymmetric."""
    d = spd_from_chol(params.d_chol)
    q = [[0.0, -params.omega], [params.omega, 0.0]]
    return nm.matmul(nm.add(d, q), nm.spd_inverse(sigma))


def irreversibility_ratio(params: Parameters, sigma: Matrix) -> float:
    """``r_irr = ||Omega||_op / lambda_min(S)`` in whitened coordinates (T.10).

    With the chosen parameterisation ``S = Sigma^{-1/2} D Sigma^{-1/2}`` and
    ``Omega = Sigma^{-1/2} Q Sigma^{-1/2}`` exactly.
    """
    w = nm.inv_sqrtm_spd(sigma)
    d = spd_from_chol(params.d_chol)
    q = [[0.0, -params.omega], [params.omega, 0.0]]
    s_mat = nm.symmetrise(nm.matmul(nm.matmul(w, d), w))
    om = nm.matmul(nm.matmul(w, q), w)
    vals, _ = nm.eigh(s_mat)
    lam_min = min(vals)
    if lam_min <= 0.0:
        raise NumericalFailure("whitened symmetric drift part is not positive definite")
    return nm.op_norm(om) / lam_min


@dataclass(frozen=True)
class FilterOutput:
    loglik: float
    innovations: list[list[float]]
    innovation_cov: Matrix
    steady_after: int


def run_filter(
    ss: StateSpace,
    y: Sequence[Sequence[float]],
    collect_innovations: bool = False,
) -> FilterOutput:
    """Innovations recursion with correlated noise; returns the exact log likelihood.

    The recursion is the standard one-step predictor for
    ``Cov(n_i, m_i) = S != 0``::

        v_i   = y_i - c - C xhat_i
        S_i   = C P_i C^T + R
        K_i   = (F P_i C^T + S) S_i^{-1}
        xhat  = F xhat_i + K_i v_i
        P_i+1 = F P_i F^T + Q - K_i S_i K_i^T
    """
    d = len(ss.sigma)
    n = len(y)
    if n == 0:
        raise NumericalFailure("empty observation record")
    F, Q, C, R, S = ss.f, ss.q, ss.c_obs, ss.r_eff, ss.s_cross
    Ft, Ct = nm.transpose(F), nm.transpose(C)

    P = [row[:] for row in ss.sigma]
    xhat = [0.0] * d
    ll = 0.0
    const = d * math.log(2.0 * math.pi)
    innovations: list[list[float]] = []

    steady_K: Matrix | None = None
    steady_Sinv: Matrix | None = None
    steady_logdet = 0.0
    steady_after = n

    for i in range(n):
        if steady_K is None:
            CP = nm.matmul(C, P)
            S_inn = nm.symmetrise(nm.add(nm.matmul(CP, Ct), R))
            try:
                L_inn = nm.cholesky(S_inn)
            except NumericalFailure as exc:
                raise NumericalFailure(f"innovation covariance not SPD at step {i}: {exc}") from exc
            logdet = 2.0 * sum(math.log(L_inn[k][k]) for k in range(d))
            S_inv = nm.chol_solve_mat(L_inn, nm.eye(d))
            K = nm.matmul(nm.add(nm.matmul(nm.matmul(F, P), Ct), S), S_inv)
            P_next = nm.symmetrise(
                nm.sub(
                    nm.add(nm.matmul(nm.matmul(F, P), Ft), Q),
                    nm.matmul(nm.matmul(K, S_inn), nm.transpose(K)),
                )
            )
            if nm.max_abs(nm.sub(P_next, P)) <= RICCATI_TOL * max(1.0, nm.max_abs(P_next)):
                steady_K, steady_Sinv, steady_logdet = K, S_inv, logdet
                steady_after = i
            P = P_next
            Kuse, Sinv_use, logdet_use = K, S_inv, logdet
            if i > RICCATI_MAX:
                raise NumericalFailure("Riccati recursion did not reach steady state")
        else:
            # Steady state reached: switch to the unrolled d=2 scalar recursion.
            # The arithmetic is identical; only the loop overhead is removed.
            if d == 2 and not collect_innovations:
                K, Si = steady_K, steady_Sinv
                m00 = F[0][0] - K[0][0] * C[0][0] - K[0][1] * C[1][0]
                m01 = F[0][1] - K[0][0] * C[0][1] - K[0][1] * C[1][1]
                m10 = F[1][0] - K[1][0] * C[0][0] - K[1][1] * C[1][0]
                m11 = F[1][1] - K[1][0] * C[0][1] - K[1][1] * C[1][1]
                k00, k01, k10, k11 = K[0][0], K[0][1], K[1][0], K[1][1]
                c00, c01, c10, c11 = C[0][0], C[0][1], C[1][0], C[1][1]
                s00, s01, s11 = Si[0][0], 0.5 * (Si[0][1] + Si[1][0]), Si[1][1]
                o0, o1 = ss.offset[0], ss.offset[1]
                x0, x1 = xhat[0], xhat[1]
                acc = 0.0
                for row in y[i:]:
                    r0 = row[0] - o0
                    r1 = row[1] - o1
                    v0 = r0 - c00 * x0 - c01 * x1
                    v1 = r1 - c10 * x0 - c11 * x1
                    acc += s00 * v0 * v0 + 2.0 * s01 * v0 * v1 + s11 * v1 * v1
                    x0, x1 = (
                        m00 * x0 + m01 * x1 + k00 * r0 + k01 * r1,
                        m10 * x0 + m11 * x1 + k10 * r0 + k11 * r1,
                    )
                ll -= 0.5 * (len(y) - i) * (steady_logdet + const) + 0.5 * acc
                xhat = [x0, x1]
                inn_cov_fast = nm.general_inverse(steady_Sinv)
                return FilterOutput(ll, innovations, inn_cov_fast, steady_after)
            Kuse, Sinv_use, logdet_use = steady_K, steady_Sinv, steady_logdet

        yi = y[i]
        v = [yi[k] - ss.offset[k] - sum(C[k][j] * xhat[j] for j in range(d)) for k in range(d)]
        quad = 0.0
        for k in range(d):
            sk = Sinv_use[k]
            quad += v[k] * sum(sk[j] * v[j] for j in range(d))
        ll -= 0.5 * (logdet_use + quad + const)
        if collect_innovations:
            innovations.append(v)
        xhat = [
            sum(F[k][j] * xhat[j] for j in range(d)) + sum(Kuse[k][j] * v[j] for j in range(d))
            for k in range(d)
        ]

    S_final = steady_Sinv if steady_Sinv is not None else None
    inn_cov = nm.general_inverse(S_final) if S_final is not None else nm.eye(d)
    return FilterOutput(ll, innovations, inn_cov, steady_after)


def log_likelihood(
    params: Parameters,
    h_locked: Matrix | None,
    y: Sequence[Sequence[float]],
    p_matrix: Matrix,
    r_obs: Matrix,
    b_det: Sequence[float],
    dt: float,
    t_exp: float,
    collect_innovations: bool = False,
) -> FilterOutput:
    """Exact log likelihood (T.6) at ``params``."""
    sigma = sigma_of(params, h_locked)
    a = drift_of(params, sigma)
    ss = build_state_space(
        a, sigma, list(params.mu), p_matrix, r_obs, list(b_det), dt, t_exp
    )
    return run_filter(ss, y, collect_innovations)


# ---------------------------------------------------------------------------
# Vector <-> Parameters packing for the optimiser
# ---------------------------------------------------------------------------

def pack(params: Parameters, free_sigma: bool) -> list[float]:
    v = [params.mu[0], params.mu[1], *params.d_chol, params.omega]
    if free_sigma:
        if params.sigma_chol is None:
            raise NumericalFailure("free_sigma packing requires sigma_chol")
        return [*params.sigma_chol, *v]
    return [params.log_beta, *v]


def unpack(x: Sequence[float], free_sigma: bool) -> Parameters:
    if free_sigma:
        return Parameters(
            log_beta=0.0,
            mu=(x[3], x[4]),
            d_chol=(x[5], x[6], x[7]),
            omega=x[8],
            sigma_chol=(x[0], x[1], x[2]),
        )
    return Parameters(
        log_beta=x[0],
        mu=(x[1], x[2]),
        d_chol=(x[3], x[4], x[5]),
        omega=x[6],
        sigma_chol=None,
    )


#: Number of free parameters in each fit.
N_PARAMS_LOCKED = 7
N_PARAMS_FREE = 9
