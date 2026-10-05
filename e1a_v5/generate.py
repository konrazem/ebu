"""Synthetic latent and observation generator: Layer E.

Deliberately built on an **independent formula path** from the estimator
(V-stage brief section 24).  The estimator obtains its exposure blocks from
Van Loan's block-exponential identity; this generator obtains the same blocks
by Gauss-Legendre quadrature of the analytic OU covariance kernel

    Cov(U_s, U_t) = Q(min(s,t)) exp(-A^T |t - s|)^T ,   Q(s) = Sigma - e^{-As} Sigma e^{-A^T s}

so that agreement between the two is a genuine cross-check rather than a
tautology.  :func:`crosscheck_exposure_blocks` reports that agreement.

RNG is permitted in V-stage.  Every draw comes from an explicit stream.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence

from . import numerics as nm
from .numerics import Matrix, NumericalFailure
from .observation import augmented_generator, van_loan
from .rng import Stream, mvn_sample

#: Gauss-Legendre nodes/weights on [-1, 1], 24 points (symmetric half stored).
_GL24_HALF = [
    (0.0640568928626056260850430826247450385909, 0.1279381953467521569740561652246953718517),
    (0.1911188674736163091586398207570696318404, 0.1258374563468282961213753825111836887264),
    (0.3150426796961633743867932913198102407864, 0.1216704729278033912044631534762624256070),
    (0.4337935076260451384870842319133497124524, 0.1155056680537256013533444839067835598622),
    (0.5454214713888395356583756172183723700107, 0.1074442701159656347825773424466062227946),
    (0.6480936519369755692524957869107476266696, 0.0976186521041138882698806644642471544279),
    (0.7401241915785543642438281030999784255232, 0.0861901615319532759171852029837426671850),
    (0.8200019859739029219539498726697452080761, 0.0733464814110803057340336152531165181193),
    (0.8864155270044010342131543419821967550873, 0.0592985849154367807463677585001085845412),
    (0.9382745520027327585236490017087214496548, 0.0442774388174198061686027482113382288593),
    (0.9747285559713094981983919930081690617411, 0.0285313886289336631813078159518782864491),
    (0.9951872199970213601799974097007368118745, 0.0123412297999871995468056670700372915759),
]
_GL24 = [(-x, w) for x, w in reversed(_GL24_HALF)] + [(x, w) for x, w in _GL24_HALF]


def _gl_nodes(a: float, b: float) -> list[tuple[float, float]]:
    half = 0.5 * (b - a)
    mid = 0.5 * (a + b)
    return [(mid + half * x, half * w) for x, w in _GL24]


def _q_of(a_drift: Matrix, sigma: Matrix, s: float) -> Matrix:
    """``Q(s) = Sigma - e^{-As} Sigma e^{-A^T s}``, the zero-start OU covariance."""
    e = nm.expm(nm.scale(a_drift, -s))
    return nm.symmetrise(nm.sub(sigma, nm.matmul(nm.matmul(e, sigma), nm.transpose(e))))


def exposure_blocks_quadrature(
    a_drift: Matrix, sigma: Matrix, t_exp: float
) -> tuple[Matrix, Matrix, Matrix]:
    """Return ``(Q_UU, Q_UJ, Q_JJ)`` by quadrature of the analytic kernel.

    ``Q_UU = Q(t_exp)``,
    ``Q_UJ = int_0^{te} e^{-A(te-t)} Q(t) dt``,
    ``Q_JJ = int_0^{te} int_0^{te} Cov(U_s, U_t) ds dt``.
    """
    d = len(sigma)
    q_uu = _q_of(a_drift, sigma, t_exp)
    nodes = _gl_nodes(0.0, t_exp)

    q_uj = nm.zeros(d, d)
    for t, w in nodes:
        e = nm.expm(nm.scale(a_drift, -(t_exp - t)))
        blk = nm.matmul(e, _q_of(a_drift, sigma, t))
        for i in range(d):
            for j in range(d):
                q_uj[i][j] += w * blk[i][j]

    # Q_JJ = W + W^T with W = int_{0<=s<t<=te} Cov(U_s, U_t) ds dt.
    # Splitting at the diagonal removes the |t - s| kink, restoring spectral
    # accuracy; integrating over the full square directly does not.
    w_mat = nm.zeros(d, d)
    for t, wt in nodes:
        inner = _gl_nodes(0.0, t)
        acc = nm.zeros(d, d)
        for s, ws in inner:
            qs = _q_of(a_drift, sigma, s)
            e = nm.expm(nm.scale(nm.transpose(a_drift), -(t - s)))
            blk = nm.matmul(qs, e)
            for i in range(d):
                for j in range(d):
                    acc[i][j] += ws * blk[i][j]
        for i in range(d):
            for j in range(d):
                w_mat[i][j] += wt * acc[i][j]
    q_jj = nm.add(w_mat, nm.transpose(w_mat))
    return q_uu, q_uj, nm.symmetrise(q_jj)


def crosscheck_exposure_blocks(
    a_drift: Matrix, sigma: Matrix, t_exp: float
) -> dict[str, float]:
    """Compare the quadrature blocks with the estimator's Van Loan blocks."""
    d = len(sigma)
    asig = nm.matmul(a_drift, sigma)
    ll = nm.symmetrise(nm.add(asig, nm.transpose(asig)))
    g = augmented_generator(a_drift)
    diff = nm.zeros(2 * d)
    for i in range(d):
        for j in range(d):
            diff[i][j] = ll[i][j]
    _, q_exp = van_loan(g, diff, t_exp)
    vl_uu = [[q_exp[i][j] for j in range(d)] for i in range(d)]
    vl_uj = [[q_exp[i][d + j] for j in range(d)] for i in range(d)]
    vl_jj = [[q_exp[d + i][d + j] for j in range(d)] for i in range(d)]
    qd_uu, qd_uj, qd_jj = exposure_blocks_quadrature(a_drift, sigma, t_exp)
    ref = max(nm.max_abs(vl_uu), nm.max_abs(vl_jj), 1e-300)
    return {
        "q_uu_rel": nm.max_abs(nm.sub(vl_uu, qd_uu)) / ref,
        "q_uj_rel": nm.max_abs(nm.sub(vl_uj, qd_uj)) / ref,
        "q_jj_rel": nm.max_abs(nm.sub(vl_jj, qd_jj)) / ref,
    }


@dataclass(frozen=True)
class GeneratorSpec:
    """Ground truth for one synthetic record."""

    h_true: Matrix
    beta_true: float
    mu_true: tuple[float, float]
    d_true: Matrix
    omega_true: float
    p_matrix: Matrix
    r_obs: Matrix
    b_det: tuple[float, float]
    dt: float
    t_exp: float
    n_frames: int
    #: Optional non-Gaussian / colored / state-dependent noise control.
    noise_model: str = "gaussian"
    noise_scale: float = 1.0
    #: Optional slow drift of the trap centre, m per second, for the drift control.
    drift_rate: tuple[float, float] = (0.0, 0.0)
    #: Optional generator exposure override to create a blur mismatch control.
    generate_t_exp: float | None = None


def generate_record(spec: GeneratorSpec, stream: Stream) -> list[list[float]]:
    """Generate one synthetic Branch-B observation record.

    The latent path is produced from the exact stationary transition law and
    the exposure average is produced from the *quadrature* blocks, keeping the
    generation path independent of the estimator's Van Loan construction.
    """
    d = 2
    sigma = nm.symmetrise(nm.scale(nm.spd_inverse(spec.h_true), 1.0 / spec.beta_true))
    q_mat = [[0.0, -spec.omega_true], [spec.omega_true, 0.0]]
    a_drift = nm.matmul(nm.add(spec.d_true, q_mat), nm.spd_inverse(sigma))

    te = spec.t_exp if spec.generate_t_exp is None else spec.generate_t_exp
    gap = spec.dt - te
    if gap < 0.0:
        raise NumericalFailure("generator exposure exceeds the frame interval")

    if te > 0.0:
        q_uu, q_uj, q_jj = exposure_blocks_quadrature(a_drift, sigma, te)
        phi_exp = nm.expm(nm.scale(a_drift, -te))
        # Joint covariance of (U_te, J) given U_0 = 0, built from quadrature blocks.
        joint = nm.zeros(2 * d)
        for i in range(d):
            for j in range(d):
                joint[i][j] = q_uu[i][j]
                joint[i][d + j] = q_uj[i][j]
                joint[d + i][j] = q_uj[j][i]
                joint[d + i][d + j] = q_jj[i][j]
        joint = nm.symmetrise(joint)
        # Jitter-free Cholesky; a failure here is a generator specification error.
        joint_chol = nm.cholesky(joint)
        # Integral of the deterministic part: int_0^te e^{-A t} dt  applied to U_0.
        nodes = _gl_nodes(0.0, te)
        int_phi = nm.zeros(d, d)
        for t, w in nodes:
            e = nm.expm(nm.scale(a_drift, -t))
            for i in range(d):
                for j in range(d):
                    int_phi[i][j] += w * e[i][j]
    else:
        phi_exp = nm.eye(d)
        joint_chol = None
        int_phi = nm.zeros(d, d)

    phi_gap = nm.expm(nm.scale(a_drift, -gap)) if gap > 0.0 else nm.eye(d)
    q_gap = (
        nm.symmetrise(nm.sub(sigma, nm.matmul(nm.matmul(phi_gap, sigma), nm.transpose(phi_gap))))
        if gap > 0.0
        else nm.zeros(d, d)
    )
    gap_chol = nm.cholesky(q_gap) if gap > 0.0 and nm.max_abs(q_gap) > 0.0 else None

    sigma_chol = nm.cholesky(sigma)
    r_chol = nm.cholesky(spec.r_obs)

    u = mvn_sample(stream, [0.0, 0.0], sigma_chol)  # centred latent state
    out: list[list[float]] = []
    colored_prev = [0.0, 0.0]

    for i in range(spec.n_frames):
        t_now = i * spec.dt
        if te > 0.0:
            w = mvn_sample(stream, [0.0] * (2 * d), joint_chol)
            u_end = [sum(phi_exp[k][j] * u[j] for j in range(d)) + w[k] for k in range(d)]
            j_int = [
                sum(int_phi[k][j] * u[j] for j in range(d)) + w[d + k] for k in range(d)
            ]
            z = [j_int[k] / te for k in range(d)]
        else:
            u_end = u[:]
            z = u[:]

        # Detector noise, with the declared mismatch controls.
        if spec.noise_model == "gaussian":
            eps = mvn_sample(stream, [0.0, 0.0], r_chol)
        elif spec.noise_model == "heavy":
            base = mvn_sample(stream, [0.0, 0.0], r_chol)
            # Scale mixture: Gaussian variance inflated on a fixed-probability branch.
            eps = [v * (3.0 if stream.uniform() < 0.05 else 1.0) for v in base]
        elif spec.noise_model == "colored":
            base = mvn_sample(stream, [0.0, 0.0], r_chol)
            eps = [0.7 * colored_prev[k] + math.sqrt(1 - 0.49) * base[k] for k in range(d)]
            colored_prev = eps
        elif spec.noise_model == "state_dependent":
            base = mvn_sample(stream, [0.0, 0.0], r_chol)
            amp = 1.0 + 2.0 * min(1.0, abs(z[0]) / max(1e-30, math.sqrt(sigma[0][0])))
            eps = [v * amp for v in base]
        elif spec.noise_model == "inflated":
            base = mvn_sample(stream, [0.0, 0.0], r_chol)
            eps = [v * spec.noise_scale for v in base]
        else:
            raise NumericalFailure(f"unknown noise model {spec.noise_model!r}")

        centre = [
            spec.mu_true[k] + spec.drift_rate[k] * t_now for k in range(d)
        ]
        pos = [z[k] + centre[k] for k in range(d)]
        y = [
            spec.b_det[k]
            + sum(spec.p_matrix[k][j] * pos[j] for j in range(d))
            + eps[k]
            for k in range(d)
        ]
        out.append(y)

        if gap > 0.0:
            noise = mvn_sample(stream, [0.0, 0.0], gap_chol) if gap_chol else [0.0, 0.0]
            u = [sum(phi_gap[k][j] * u_end[j] for j in range(d)) + noise[k] for k in range(d)]
        else:
            u = u_end
    return out
