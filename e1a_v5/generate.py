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
from .units import K_B
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


# ---------------------------------------------------------------------------
# Three-dimensional hidden-memory world (CTL-AXIAL-MEMORY)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AxialMemorySpec:
    """A full 3D Gaussian world observed only in its lateral coordinates.

    The lateral MARGINAL density is exactly the Schur one the bridge expects,
    ``Sigma_qq = k_B T K_eff^{-1}``, because the ``qq`` block of a block
    matrix's inverse is the inverse of its Schur complement.  The lateral
    PATH, however, is a projection of a three-mode Ornstein-Uhlenbeck process,
    so its lag structure carries the axial mode's memory and no single 2D
    Markov generator reproduces it.

    That is the scientific content of the control: density agreement is not
    temporal-model qualification.  V4 reduced it to setting a qualification
    flag to False, which tests the refusal path and not the physics.
    """

    #: Full 3D stiffness, N/m, ordered (x, y, z).
    k3: Matrix
    temperature: float
    #: Isotropic drag coefficient, N s/m.
    gamma: float
    p_matrix: Matrix
    r_obs: Matrix
    b_det: tuple[float, float]
    dt: float
    t_exp: float
    n_frames: int


def axial_memory_dynamics(spec: AxialMemorySpec):
    """``(A3, Sigma3)`` of the declared 3D world."""
    k3 = nm.symmetrise(spec.k3)
    if not nm.is_spd(k3):
        raise NumericalFailure("3D stiffness must be positive definite")
    a3 = nm.scale(k3, 1.0 / spec.gamma)
    sigma3 = nm.symmetrise(nm.scale(nm.spd_inverse(k3), K_B * spec.temperature))
    return a3, sigma3


def lateral_lag_covariance(a3: Matrix, sigma3: Matrix, tau: float) -> Matrix:
    """``[e^{-A3 tau} Sigma3]_qq``: the exact lateral lag covariance."""
    full = nm.matmul(nm.expm(nm.scale(a3, -tau)), sigma3)
    return [[full[i][j] for j in range(2)] for i in range(2)]


def markov_closure_residual(a3: Matrix, sigma3: Matrix, tau: float) -> float:
    """Relative Chapman-Kolmogorov residual of the lateral marginal.

    A stationary 2D Ornstein-Uhlenbeck process satisfies
    ``C(tau) = e^{-A tau} Sigma`` exactly, hence

        C(2 tau) = C(tau) Sigma^{-1} C(tau)

    for every ``tau`` and every admissible ``A``.  The identity is a property
    of the process, not of a particular fit, so a nonzero residual proves that
    NO 2D Markov generator reproduces the observed lag structure -- without
    fitting anything.  That is the witness underlying the control.
    """
    sig_q = [[sigma3[i][j] for j in range(2)] for i in range(2)]
    c1 = lateral_lag_covariance(a3, sigma3, tau)
    c2 = lateral_lag_covariance(a3, sigma3, 2.0 * tau)
    pred = nm.matmul(nm.matmul(c1, nm.spd_inverse(sig_q)), c1)
    return nm.max_abs(nm.sub(c2, pred)) / max(nm.max_abs(sig_q), 1e-300)


def generate_axial_memory_record(
    spec: AxialMemorySpec, stream: Stream
) -> list[list[float]]:
    """Generate lateral observations of the full 3D process.

    The latent path is advanced in three dimensions through the exact
    stationary transition law, the shutter average is taken in three
    dimensions, and only the lateral components are observed.  Nothing about
    the generation assumes a 2D model.
    """
    d = 3
    a3, sigma3 = axial_memory_dynamics(spec)
    te = spec.t_exp
    gap = spec.dt - te
    if gap < 0.0:
        raise NumericalFailure("generator exposure exceeds the frame interval")

    asig = nm.matmul(a3, sigma3)
    ll = nm.symmetrise(nm.add(asig, nm.transpose(asig)))
    nm.cholesky(ll)

    if te > 0.0:
        g = augmented_generator(a3)
        diff = nm.zeros(2 * d, 2 * d)
        for i in range(d):
            for j in range(d):
                diff[i][j] = ll[i][j]
        phi_exp, q_exp = van_loan(g, diff, te)
        phi_uu = [[phi_exp[i][j] for j in range(d)] for i in range(d)]
        phi_ju = [[phi_exp[d + i][j] for j in range(d)] for i in range(d)]
        joint_chol = nm.cholesky(nm.symmetrise(q_exp))
    else:
        phi_uu = nm.eye(d)
        phi_ju = nm.zeros(d, d)
        joint_chol = None

    phi_gap = nm.expm(nm.scale(a3, -gap)) if gap > 0.0 else nm.eye(d)
    q_gap = (
        nm.symmetrise(nm.sub(sigma3, nm.matmul(nm.matmul(phi_gap, sigma3),
                                               nm.transpose(phi_gap))))
        if gap > 0.0 else nm.zeros(d, d)
    )
    gap_chol = nm.cholesky(q_gap) if gap > 0.0 and nm.max_abs(q_gap) > 0.0 else None
    r_chol = nm.cholesky(spec.r_obs)

    u = mvn_sample(stream, [0.0] * d, nm.cholesky(sigma3))
    out: list[list[float]] = []
    for _ in range(spec.n_frames):
        if te > 0.0:
            w = mvn_sample(stream, [0.0] * (2 * d), joint_chol)
            u_end = [sum(phi_uu[k][j] * u[j] for j in range(d)) + w[k] for k in range(d)]
            j_int = [sum(phi_ju[k][j] * u[j] for j in range(d)) + w[d + k]
                     for k in range(d)]
            z = [j_int[k] / te for k in range(2)]
            u = u_end
        else:
            z = [u[k] for k in range(2)]
        eps = mvn_sample(stream, [0.0, 0.0], r_chol)
        out.append([
            spec.b_det[i]
            + sum(spec.p_matrix[i][j] * z[j] for j in range(2))
            + eps[i]
            for i in range(2)
        ])
        if gap > 0.0:
            n = mvn_sample(stream, [0.0] * d, gap_chol) if gap_chol else [0.0] * d
            u = [sum(phi_gap[k][j] * u[j] for j in range(d)) + n[k] for k in range(d)]
    return out


# ---------------------------------------------------------------------------
# Independent driven-response measurement (Branch-A temporal qualification)
# ---------------------------------------------------------------------------
#
# T/U require the retained 2D temporal model to be QUALIFIED against an
# independently measured response, not assumed.  V5 left that qualification as
# a flag a caller set, so CTL-AXIAL-MEMORY exercised the refusal path and not
# the physics: nothing in the pipeline ever measured whether a 2D generator
# could reproduce the system's response.
#
# The measurement used here is the one property that separates the admissible
# class from everything else, with no fitting at all.  For ANY 2D linear
# system the mean response to a prepared displacement is a semigroup,
#
#     R(t) = e^{-A t} ,   hence   R(2 tau) = R(tau)^2
#
# for every tau and every admissible A.  A lateral projection of a
# three-mode system is not a semigroup, because the hidden mode's state at
# time tau is not a function of the lateral state alone.  So a measured
# violation of R(2 tau) = R(tau)^2, beyond the measurement's own standard
# error, excludes the WHOLE admissible 2D class at once.


@dataclass(frozen=True)
class ResponseSpec:
    """The declared independent response-measurement architecture.

    ``a_drift`` and ``sigma`` are the FULL physical system -- two modes for a
    qualified world, three when a hidden axial mode is present.  The
    measurement sees only the lateral coordinates, through the same declared
    camera model as Branch B.
    """

    a_drift: Matrix
    sigma: Matrix
    p_matrix: Matrix
    r_obs: Matrix
    b_det: tuple[float, float]
    #: Response lag; the measurement compares ``R(tau)`` with ``R(2 tau)``.
    tau: float
    #: Independent prepared releases per lateral direction.
    trials: int
    #: Initial lateral displacement, in units of the stationary lateral sd.
    displacement_sd: float


def _conditional_start(sigma: Matrix, direction: int, magnitude: float) -> list[float]:
    """Prepared state: a lateral displacement with hidden modes equilibrated.

    Holding the bead at a displaced lateral position lets any hidden mode
    relax to its conditional equilibrium ``E[z | q] = Sigma_zq Sigma_qq^{-1} q``
    before release.  That is the physical preparation, and it is also the one
    that makes the measurement a property of the system rather than of an
    arbitrary initial condition.
    """
    n = len(sigma)
    q = [magnitude if i == direction else 0.0 for i in range(2)]
    s_qq = [[sigma[i][j] for j in range(2)] for i in range(2)]
    w = nm.matvec(nm.spd_inverse(s_qq), q)
    out = list(q)
    for i in range(2, n):
        out.append(sum(sigma[i][j] * w[j] for j in range(2)))
    return out


def generate_response_record(spec: ResponseSpec, stream: Stream) -> dict:
    """Measure ``R(tau)`` and ``R(2 tau)`` from prepared releases.

    Each trial releases the prepared state and observes the lateral position
    once, through ``P`` and the localisation noise.  The response matrices are
    the per-direction sample means, divided by the displacement and mapped
    back to physical coordinates.  Nothing is fitted.
    """
    n = len(spec.sigma)
    if n < 2 or len(spec.a_drift) != n:
        raise NumericalFailure("response measurement needs a square full system")
    if spec.trials < 2:
        raise NumericalFailure("a response measurement needs at least two trials")
    f1 = nm.expm(nm.scale(spec.a_drift, -spec.tau))
    f2 = nm.expm(nm.scale(spec.a_drift, -2.0 * spec.tau))
    q1 = nm.symmetrise(nm.sub(spec.sigma,
                              nm.matmul(nm.matmul(f1, spec.sigma), nm.transpose(f1))))
    q2 = nm.symmetrise(nm.sub(spec.sigma,
                              nm.matmul(nm.matmul(f2, spec.sigma), nm.transpose(f2))))
    l1, l2 = nm.cholesky(q1), nm.cholesky(q2)
    lr = nm.cholesky(nm.symmetrise(spec.r_obs))
    pinv = nm.general_inverse(spec.p_matrix)
    zero = [0.0] * n

    cols1: list[list[float]] = []
    cols2: list[list[float]] = []
    for k in range(2):
        d = spec.displacement_sd * math.sqrt(spec.sigma[k][k])
        x0 = _conditional_start(spec.sigma, k, d)
        acc = [[0.0, 0.0], [0.0, 0.0]]
        for which, (f, l) in enumerate(((f1, l1), (f2, l2))):
            mean = nm.matvec(f, x0)
            for _ in range(spec.trials):
                x = [mean[i] + v for i, v in enumerate(mvn_sample(stream, zero, l))]
                y = [
                    spec.b_det[i]
                    + sum(spec.p_matrix[i][j] * x[j] for j in range(2))
                    + sum(lr[i][j] * g for j, g in enumerate(stream.normals(2)))
                    for i in range(2)
                ]
                for i in range(2):
                    acc[which][i] += y[i]
        for which, cols in ((0, cols1), (1, cols2)):
            mean_y = [acc[which][i] / spec.trials - spec.b_det[i] for i in range(2)]
            cols.append([v / d for v in nm.matvec(pinv, mean_y)])

    r_tau = [[cols1[j][i] for j in range(2)] for i in range(2)]
    r_2tau = [[cols2[j][i] for j in range(2)] for i in range(2)]

    # Standard error of one entry of a response matrix: the per-trial lateral
    # spread, seen through P^{-1}, divided by the displacement and sqrt(M).
    per_trial = nm.symmetrise(nm.add(
        nm.matmul(nm.matmul(spec.p_matrix,
                            [[spec.sigma[i][j] for j in range(2)] for i in range(2)]),
                  nm.transpose(spec.p_matrix)),
        spec.r_obs,
    ))
    back = nm.symmetrise(nm.matmul(nm.matmul(pinv, per_trial), nm.transpose(pinv)))
    d_min = spec.displacement_sd * math.sqrt(
        min(spec.sigma[0][0], spec.sigma[1][1]))
    entry_se = math.sqrt(max(back[0][0], back[1][1])) / (
        d_min * math.sqrt(spec.trials))

    predicted = nm.matmul(r_tau, r_tau)
    scale = max(nm.max_abs(r_tau), 1e-300)
    residual = nm.max_abs(nm.sub(r_2tau, predicted)) / scale
    # |R(2t) - R(t)^2| picks up one entry error from R(2t) and, through the
    # product, at most 2 ||R(t)|| more from R(t); the ratio adds one more.
    residual_se = entry_se * (1.0 + 2.0 * scale) / scale + residual * entry_se / scale
    return {
        "r_tau": r_tau,
        "r_2tau": r_2tau,
        "tau": spec.tau,
        "trials": spec.trials,
        "semigroup_residual": residual,
        "residual_standard_error": residual_se,
        "entry_standard_error": entry_se,
        "response_scale": scale,
    }


def exact_semigroup_residual(a_drift: Matrix, sigma: Matrix) -> float:
    """Noise-free ``||R(2 tau) - R(tau)^2|| / ||R(tau)||`` of a system.

    The deterministic counterpart of :func:`generate_response_record`, used at
    CONSTRUCTION time so no design path has to assert that its own world is
    temporally qualified.  For a 2D system it is zero to rounding, because the
    lateral response IS the semigroup; for a system with a hidden mode it is
    not.  ``tau`` is the system's own slow relaxation time, so the quantity is
    a property of the system and takes no tuning.
    """
    n = len(sigma)
    sym = nm.symmetrise(nm.scale(nm.add(a_drift, nm.transpose(a_drift)), 0.5))
    vals, _ = nm.eigh(sym)
    positive = [v for v in vals if v > 0.0]
    if not positive:
        raise NumericalFailure("the system has no positive relaxation rate")
    tau = 1.0 / min(positive)
    f1 = nm.expm(nm.scale(a_drift, -tau))
    f2 = nm.expm(nm.scale(a_drift, -2.0 * tau))
    c1, c2 = [], []
    for k in range(2):
        x0 = _conditional_start(sigma, k, 1.0)
        c1.append(nm.matvec(f1, x0)[:2])
        c2.append(nm.matvec(f2, x0)[:2])
    r1 = [[c1[j][i] for j in range(2)] for i in range(2)]
    r2 = [[c2[j][i] for j in range(2)] for i in range(2)]
    scale = max(nm.max_abs(r1), 1e-300)
    return nm.max_abs(nm.sub(r2, nm.matmul(r1, r1))) / scale
