"""Observation-model construction: Layer D.

Implements the cleared detector model (T-stage T.17)::

    y_i = b_det + P * (1/t_exp) * int_{t_i}^{t_i+t_exp} X_s ds + eps_i

with ``eps_i ~ N(0, R_obs)`` independent between frames.  Exposure averaging is
carried out exactly, by augmenting the latent state with its running integral.

The exposure average makes the effective observation noise and the effective
transition noise *correlated*: the same Brownian increments inside the shutter
window appear in both.  A filter that drops that cross-covariance is not this
likelihood (T-stage section 8.2), so it is constructed and carried explicitly.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from . import numerics as nm
from .numerics import Matrix, NumericalFailure

#: Prospective exposure ceiling, T-stage section 15.2: t_exp <= 0.1 tau_fast.
EXPOSURE_CEILING_FRACTION = 0.1
#: Maximum admissible instantaneous localisation variance ratio, T-stage 15.2/T.23.
LOCALIZATION_RATIO_CEILING = 0.05
#: Non-aliasing bandwidth requirement, T-stage 12.2: ||B||_2 * dt <= 0.2.
BANDWIDTH_CEILING = 0.2


def augmented_generator(a: Matrix) -> Matrix:
    """``G = [[-A, 0], [I, 0]]`` on the state ``[U; J]`` with ``J = int U``."""
    d = len(a)
    g = nm.zeros(2 * d)
    for i in range(d):
        for j in range(d):
            g[i][j] = -a[i][j]
        g[d + i][i] = 1.0
    return g


def van_loan(g: Matrix, diffusion: Matrix, h: float) -> tuple[Matrix, Matrix]:
    """Return ``(expm(G h), Q(h))`` with ``Q(h) = int_0^h e^{Gs} D e^{G^T s} ds``.

    Uses Van Loan's block construction, which gives both quantities from a
    single matrix exponential and avoids any quadrature.
    """
    n = len(g)
    big = nm.zeros(2 * n)
    for i in range(n):
        for j in range(n):
            big[i][j] = -g[i][j]
            big[i][n + j] = diffusion[i][j]
            big[n + i][n + j] = g[j][i]  # G^T
    big = nm.scale(big, h)
    e = nm.expm(big)
    b12 = [[e[i][n + j] for j in range(n)] for i in range(n)]
    b22 = [[e[n + i][n + j] for j in range(n)] for i in range(n)]
    f = nm.transpose(b22)  # expm(G h)
    q = nm.symmetrise(nm.matmul(f, b12))
    return f, q


@dataclass(frozen=True)
class StateSpace:
    """Discrete-time state-space realisation of the observed record.

    Attributes
    ----------
    f:
        State transition ``U_{i+1} = F U_i + n_i``, ``F = expm(-A dt)``.
    q:
        ``Cov(n_i)``.
    c_obs:
        Observation loading ``y_i = c + C U_i + m_i``.
    r_eff:
        ``Cov(m_i)``, including the exposure-averaged latent contribution.
    s_cross:
        ``Cov(n_i, m_i)`` -- nonzero whenever ``t_exp > 0``.
    offset:
        The constant ``c = b_det + P mu``.
    sigma:
        Stationary latent covariance.
    """

    f: Matrix
    q: Matrix
    c_obs: Matrix
    r_eff: Matrix
    s_cross: Matrix
    offset: list[float]
    sigma: Matrix


def build_state_space(
    a_drift: Matrix,
    sigma: Matrix,
    mu: list[float],
    p_matrix: Matrix,
    r_obs: Matrix,
    b_det: list[float],
    dt: float,
    t_exp: float,
) -> StateSpace:
    """Construct the exact discrete-time realisation for uniform sampling.

    ``t_exp = 0`` reduces to instantaneous observations, where ``C = P``,
    ``R_eff = R_obs`` and the cross-covariance vanishes.
    """
    d = len(sigma)
    if not (0.0 <= t_exp <= dt):
        raise NumericalFailure(f"exposure {t_exp!r} must satisfy 0 <= t_exp <= dt ({dt!r})")
    # LL^T = A Sigma + Sigma A^T
    asig = nm.matmul(a_drift, sigma)
    ll = nm.symmetrise(nm.add(asig, nm.transpose(asig)))
    try:
        nm.cholesky(ll)
    except NumericalFailure as exc:
        raise NumericalFailure(f"diffusion LL^T is not positive definite: {exc}") from exc

    f_full = nm.expm(nm.scale(a_drift, -dt))

    if t_exp == 0.0:
        q_trans = nm.symmetrise(nm.sub(sigma, nm.matmul(nm.matmul(f_full, sigma), nm.transpose(f_full))))
        return StateSpace(
            f=f_full,
            q=q_trans,
            c_obs=[row[:] for row in p_matrix],
            r_eff=[row[:] for row in r_obs],
            s_cross=nm.zeros(d, d),
            offset=[b_det[i] + sum(p_matrix[i][j] * mu[j] for j in range(d)) for i in range(d)],
            sigma=sigma,
        )

    g = augmented_generator(a_drift)
    diff = nm.zeros(2 * d)
    for i in range(d):
        for j in range(d):
            diff[i][j] = ll[i][j]
    phi_exp, q_exp = van_loan(g, diff, t_exp)

    phi_uu = [[phi_exp[i][j] for j in range(d)] for i in range(d)]
    phi_ju = [[phi_exp[d + i][j] for j in range(d)] for i in range(d)]
    q_uu = [[q_exp[i][j] for j in range(d)] for i in range(d)]
    q_jj = [[q_exp[d + i][d + j] for j in range(d)] for i in range(d)]
    q_uj = [[q_exp[i][d + j] for j in range(d)] for i in range(d)]

    gap = dt - t_exp
    if gap > 0.0:
        phi_gap = nm.expm(nm.scale(a_drift, -gap))
        q_gap = nm.symmetrise(
            nm.sub(sigma, nm.matmul(nm.matmul(phi_gap, sigma), nm.transpose(phi_gap)))
        )
    else:
        phi_gap = nm.eye(d)
        q_gap = nm.zeros(d, d)

    scale_p = nm.scale(p_matrix, 1.0 / t_exp)
    c_obs = nm.matmul(scale_p, phi_ju)
    r_eff = nm.symmetrise(
        nm.add(nm.matmul(nm.matmul(scale_p, q_jj), nm.transpose(scale_p)), r_obs)
    )
    q_trans = nm.symmetrise(
        nm.add(nm.matmul(nm.matmul(phi_gap, q_uu), nm.transpose(phi_gap)), q_gap)
    )
    # Cov(n_i, m_i) = Phi_gap Q_UJ (P/t_exp)^T
    s_cross = nm.matmul(nm.matmul(phi_gap, q_uj), nm.transpose(scale_p))

    return StateSpace(
        f=nm.matmul(phi_gap, phi_uu),
        q=q_trans,
        c_obs=c_obs,
        r_eff=r_eff,
        s_cross=s_cross,
        offset=[b_det[i] + sum(p_matrix[i][j] * mu[j] for j in range(d)) for i in range(d)],
        sigma=sigma,
    )


def observed_mean_covariance(ss: StateSpace) -> Matrix:
    """Marginal covariance of one observation under the stationary law."""
    return nm.symmetrise(
        nm.add(nm.matmul(nm.matmul(ss.c_obs, ss.sigma), nm.transpose(ss.c_obs)), ss.r_eff)
    )


def localization_ratio(sigma: Matrix, r_obs: Matrix) -> float:
    """Largest instantaneous localisation variance ratio in whitened directions.

    This is the quantity the T-stage qualification limits actually constrain:
    T.23 reads "at most 5% independent *instantaneous localisation* variance in
    each whitened direction", and the 15.2 ceiling is its companion.  It is
    ``lambda_max(Sigma^{-1/2} R_obs Sigma^{-1/2})`` and deliberately excludes
    the exposure-averaging self-term, which is a separate effect with its own
    exposure ceiling.
    """
    w = nm.inv_sqrtm_spd(sigma)
    m = nm.symmetrise(nm.matmul(nm.matmul(w, r_obs), w))
    vals, _ = nm.eigh(m)
    return max(vals)


def effective_noise_to_signal(ss: StateSpace) -> float:
    """Blur-inclusive effective noise-to-signal ratio (diagnostic only)."""
    latent = nm.symmetrise(
        nm.matmul(nm.matmul(ss.c_obs, ss.sigma), nm.transpose(ss.c_obs))
    )
    try:
        w = nm.inv_sqrtm_spd(latent)
    except NumericalFailure as exc:
        raise NumericalFailure(f"latent observation covariance not SPD: {exc}") from exc
    m = nm.symmetrise(nm.matmul(nm.matmul(w, ss.r_eff), w))
    vals, _ = nm.eigh(m)
    return max(vals)


def model_lag_covariance(ss: StateSpace, lag: int) -> Matrix:
    """Model observation autocovariance ``Cov(y_i, y_{i+lag})`` for ``lag >= 0``.

    With correlated noises the exposure cross-covariance enters at every lag::

        lag = 0 : C Sigma C^T + R_eff
        lag = k : C Sigma (F^k)^T C^T + S^T (F^{k-1})^T C^T

    The second term is the one a filter that ignores exposure correlation
    would omit, so it is carried explicitly here too.
    """
    if lag < 0:
        raise NumericalFailure("lag must be nonnegative")
    d = len(ss.sigma)
    base = nm.matmul(nm.matmul(ss.c_obs, ss.sigma), nm.transpose(ss.c_obs))
    if lag == 0:
        return nm.symmetrise(nm.add(base, ss.r_eff))
    fk = nm.eye(d)
    for _ in range(lag):
        fk = nm.matmul(fk, ss.f)
    fkm1 = nm.eye(d)
    for _ in range(lag - 1):
        fkm1 = nm.matmul(fkm1, ss.f)
    term1 = nm.matmul(nm.matmul(ss.c_obs, ss.sigma), nm.transpose(fk))
    term1 = nm.matmul(term1, nm.transpose(ss.c_obs))
    term2 = nm.matmul(nm.matmul(nm.transpose(ss.s_cross), nm.transpose(fkm1)),
                      nm.transpose(ss.c_obs))
    return nm.add(term1, term2)


def bandwidth_product(a_drift: Matrix, sigma: Matrix, dt: float) -> float:
    """``||B||_2 * dt`` with ``B = Sigma^{-1/2} A Sigma^{1/2}`` (T-stage 12.2)."""
    w = nm.inv_sqrtm_spd(sigma)
    wi = nm.sqrtm_spd(sigma)
    b = nm.matmul(nm.matmul(w, a_drift), wi)
    return nm.op_norm(b) * dt


# ---------------------------------------------------------------------------
# Record-level observation qualification (T 15.2 / T.23)
# ---------------------------------------------------------------------------

from .refusals import (  # noqa: E402  (kept local to this section)
    OBSERVATION_MODEL_UNQUALIFIED,
    NUMERICAL_REPRESENTATION_FAILURE,
    Refusal,
    refuse,
)

#: Observation noise models the declared T/U domain admits.
QUALIFIED_NOISE_MODELS = frozenset({"gaussian"})


@dataclass(frozen=True)
class ObservationQualification:
    """Whether one record's observation model lies inside the declared domain.

    V4 set ``observation_valid=True`` unconditionally for every synthetic
    record, so ``CTL-NOISE-HI`` generated a localisation ratio of 0.25 --
    five times the T.23 ceiling -- and was still marked observation-valid.
    The control's whole scientific purpose is that such a record must not
    enter complete support, so the flag defeated the control.

    Every required predicate is evaluated here, and each failure carries its
    own structured refusal.  ``valid`` is the conjunction; there is no caller
    override.
    """

    valid: bool
    refusals: tuple[Refusal, ...] = ()
    localization_ratio: float | None = None
    #: Upper end of the ratio's enclosure, after the certified axial
    #: remainder's multiplicative effect on the latent covariance.
    localization_ratio_upper: float | None = None
    exposure_fraction: float | None = None
    exposure_fraction_upper: float | None = None
    bandwidth_product: float | None = None
    bandwidth_product_upper: float | None = None
    noise_model: str = "gaussian"

    def as_dict(self) -> dict:
        return {
            "valid": self.valid,
            "localization_ratio": self.localization_ratio,
            "localization_ratio_upper": self.localization_ratio_upper,
            "exposure_fraction": self.exposure_fraction,
            "exposure_fraction_upper": self.exposure_fraction_upper,
            "bandwidth_product": self.bandwidth_product,
            "bandwidth_product_upper": self.bandwidth_product_upper,
            "noise_model": self.noise_model,
            "refusals": [r.code for r in self.refusals],
        }


def qualify_observation(
    sigma: Matrix,
    r_obs: Matrix,
    p_matrix: Matrix,
    a_drift: Matrix,
    dt: float,
    t_exp: float,
    noise_model: str = "gaussian",
    rate_factor: float = 1.0,
) -> ObservationQualification:
    """Evaluate every T/U observation requirement for one record.

    ``rate_factor`` is the certified multiplicative bound by which the axial
    remainder set can inflate the true relaxation rates and shrink the latent
    covariance.  It enlarges the localisation ratio, the exposure fraction and
    the bandwidth product, each of which is then compared against its own
    declared ceiling with T's INCLUSIVE semantics.  A quantity whose enclosure
    straddles its ceiling does not pass: the record is not demonstrated to lie
    inside the qualified envelope.
    """
    reasons: list[Refusal] = []
    ratio = ratio_up = None
    exposure = exposure_up = None
    bandwidth = bandwidth_up = None

    if not nm.is_spd(r_obs):
        reasons.append(refuse(
            OBSERVATION_MODEL_UNQUALIFIED, "R_obs positive definite",
            "the localisation noise covariance is not positive definite",
        ))
    try:
        nm.general_inverse(p_matrix)
    except NumericalFailure as exc:
        reasons.append(refuse(
            OBSERVATION_MODEL_UNQUALIFIED, "P invertible",
            f"the physical-to-detector map is not invertible: {exc}",
        ))
    if noise_model not in QUALIFIED_NOISE_MODELS:
        reasons.append(refuse(
            OBSERVATION_MODEL_UNQUALIFIED, "noise model qualified",
            f"observation noise model {noise_model!r} is outside the declared "
            "Gaussian domain",
            noise_model=noise_model,
        ))
    if not (0.0 <= t_exp <= dt):
        reasons.append(refuse(
            OBSERVATION_MODEL_UNQUALIFIED, "0 <= t_exp <= dt",
            "the shutter does not fit inside the frame interval",
            t_exp=t_exp, dt=dt,
        ))

    try:
        ratio = localization_ratio(sigma, r_obs)
        ratio_up = ratio * rate_factor
        if not (ratio_up <= LOCALIZATION_RATIO_CEILING):
            reasons.append(refuse(
                OBSERVATION_MODEL_UNQUALIFIED,
                f"instantaneous localisation ratio <= {LOCALIZATION_RATIO_CEILING}",
                "the record lies outside the declared T 15.2 / T.23 "
                "localisation-noise envelope",
                ratio=ratio, ratio_upper=ratio_up,
                ceiling=LOCALIZATION_RATIO_CEILING,
            ))
    except NumericalFailure as exc:
        reasons.append(refuse(
            NUMERICAL_REPRESENTATION_FAILURE, "localisation ratio computable", str(exc),
        ))

    try:
        vals, _ = nm.eigh(nm.symmetrise(
            nm.scale(nm.add(a_drift, nm.transpose(a_drift)), 0.5)))
        rate_fast = max(vals)
        if rate_fast <= 0.0:
            raise NumericalFailure("fast relaxation rate is not positive")
        exposure = t_exp * rate_fast
        exposure_up = exposure * rate_factor
        if not (exposure_up <= EXPOSURE_CEILING_FRACTION):
            reasons.append(refuse(
                OBSERVATION_MODEL_UNQUALIFIED,
                f"t_exp / tau_fast <= {EXPOSURE_CEILING_FRACTION}",
                "the exposure exceeds the declared blur envelope",
                exposure_fraction=exposure, exposure_upper=exposure_up,
            ))
    except NumericalFailure as exc:
        reasons.append(refuse(
            NUMERICAL_REPRESENTATION_FAILURE, "exposure fraction computable", str(exc),
        ))

    try:
        bandwidth = bandwidth_product(a_drift, sigma, dt)
        bandwidth_up = bandwidth * rate_factor
        if not (bandwidth_up <= BANDWIDTH_CEILING):
            reasons.append(refuse(
                OBSERVATION_MODEL_UNQUALIFIED,
                f"||B||_2 dt <= {BANDWIDTH_CEILING}",
                "the record exceeds the non-aliasing bandwidth envelope",
                bandwidth_product=bandwidth, bandwidth_upper=bandwidth_up,
            ))
    except NumericalFailure as exc:
        reasons.append(refuse(
            NUMERICAL_REPRESENTATION_FAILURE, "bandwidth product computable", str(exc),
        ))

    return ObservationQualification(
        valid=not reasons,
        refusals=tuple(reasons),
        localization_ratio=ratio,
        localization_ratio_upper=ratio_up,
        exposure_fraction=exposure,
        exposure_fraction_upper=exposure_up,
        bandwidth_product=bandwidth,
        bandwidth_product_upper=bandwidth_up,
        noise_model=noise_model,
    )
