"""Primitive calibration covariance and its end-to-end propagation.

Completes the ``C_phi`` path that V2 declared incomplete:

    primitive dependency graph
      -> physical field / H_eff
      -> observation calibration
      -> fitted log-beta sensitivity
      -> complete calibration covariance
      -> absolute interval
      -> cross-field contrast interval

Shared primitives carry ONE variable identity (U-stage 16.2 / 23), so a
standard used by several fields is never replicated into independent copies;
its covariance is shared by construction rather than by assertion.

Bounded deterministic systematics are kept in a SEPARATE structure from the
random covariance and are never converted into one (U-stage 25, T.18).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Mapping, Sequence

from . import numerics as nm
from .numerics import Matrix, NumericalFailure
from .likelihood import (
    Parameters,
    chol_params_from_spd,
    drift_of,
    sigma_of,
)
from .observation import StateSpace, build_state_space
from .optimize import minimise
from .confidence import (
    SIGMA_CAL_ABS_MAX,
    SIGMA_CAL_CONTRAST_MAX,
    NumericalEnclosure,
    classify_with_enclosure,
)
from .evidence import BiasEvidence
from .packets import BlockId, FieldId
from .units import K_B


class Scope(str, Enum):
    """Dependency scope of a calibration primitive (U-stage 16.2)."""

    GLOBAL = "global"      # shared across both preparations
    BLOCK = "block"        # shared across the four fields of one preparation
    FIELD = "field"        # specific to one (block, field) record


@dataclass(frozen=True)
class Primitive:
    """One calibration primitive with an explicit variable identity."""

    name: str
    scope: Scope
    value: float
    #: Standard uncertainty of this primitive in its own units.
    sigma: float
    block: BlockId | None = None
    fld: FieldId | None = None

    @property
    def key(self) -> str:
        """The variable identity. Shared scopes deliberately omit the record."""
        if self.scope is Scope.GLOBAL:
            return self.name
        if self.scope is Scope.BLOCK:
            return f"{self.name}@{self.block.value}"  # type: ignore[union-attr]
        return f"{self.name}@{self.block.value}/{self.fld.value}"  # type: ignore[union-attr]


@dataclass
class PrimitiveVector:
    """The ordered primitive vector ``phi`` and its covariance ``C_phi``.

    A primitive registered twice under the same key is the SAME variable: the
    second registration is checked for consistency and then ignored, so a
    shared standard cannot silently become two independent variables.
    """

    primitives: list[Primitive] = field(default_factory=list)
    _index: dict[str, int] = field(default_factory=dict)
    #: Optional explicit correlations between distinct keys.
    correlations: dict[tuple[str, str], float] = field(default_factory=dict)

    def add(self, p: Primitive) -> int:
        if p.key in self._index:
            existing = self.primitives[self._index[p.key]]
            if not (
                math.isclose(existing.value, p.value, rel_tol=1e-12, abs_tol=0.0)
                and math.isclose(existing.sigma, p.sigma, rel_tol=1e-12, abs_tol=0.0)
            ):
                raise NumericalFailure(
                    f"primitive {p.key!r} registered twice with different "
                    f"value/sigma; a shared standard must be one variable"
                )
            return self._index[p.key]
        self._index[p.key] = len(self.primitives)
        self.primitives.append(p)
        return self._index[p.key]

    def index_of(self, key: str) -> int:
        if key not in self._index:
            raise NumericalFailure(f"primitive {key!r} is not registered")
        return self._index[key]

    def correlate(self, key_a: str, key_b: str, rho: float) -> None:
        if not (-1.0 <= rho <= 1.0):
            raise NumericalFailure(f"correlation {rho!r} outside [-1, 1]")
        self.index_of(key_a)
        self.index_of(key_b)
        self.correlations[(key_a, key_b)] = rho

    @property
    def names(self) -> list[str]:
        return [p.key for p in self.primitives]

    @property
    def values(self) -> list[float]:
        return [p.value for p in self.primitives]

    def covariance(self) -> Matrix:
        """Assemble ``C_phi``.

        Diagonal entries are the declared variances; off-diagonal entries come
        only from explicitly declared correlations. Sharing is expressed by a
        shared *identity*, not by an off-diagonal term.
        """
        n = len(self.primitives)
        c = nm.zeros(n, n)
        for i, p in enumerate(self.primitives):
            c[i][i] = p.sigma * p.sigma
        for (ka, kb), rho in self.correlations.items():
            i, j = self.index_of(ka), self.index_of(kb)
            cov = rho * self.primitives[i].sigma * self.primitives[j].sigma
            c[i][j] = cov
            c[j][i] = cov
        if n and not nm.is_spd(c):
            # A declared correlation set that is not PSD is a specification
            # error, not something to be repaired by shrinkage.
            vals, _ = nm.eigh(c)
            if min(vals) < -1e-12 * max(abs(v) for v in vals):
                raise NumericalFailure(
                    f"C_phi is not positive semidefinite (min eigenvalue {min(vals):.3e})"
                )
        return c


@dataclass(frozen=True)
class BoundedBias:
    """Deterministic bounded systematics, kept apart from the covariance.

    U-stage 25 forbids treating a bounded model error as a zero-mean random
    contribution. These are carried as magnitudes and applied as interval
    enlargements, never folded into ``C_phi``.

    Every bound is a :class:`~e1a_v5.evidence.BiasEvidence`, so a key with no
    entry is MISSING rather than zero.  V3's ``dict.get(key, 0.0)`` turned the
    absence of a certification into a certification of zero, which is the
    strongest possible claim obtainable by supplying nothing.
    """

    #: Per-record absolute log-beta bias evidence, by (block, field) key.
    absolute: Mapping[str, BiasEvidence] = field(default_factory=dict)
    #: Per-contrast bias evidence, computed jointly, by contrast key.
    contrast: Mapping[str, BiasEvidence] = field(default_factory=dict)

    def absolute_evidence(self, key: str) -> BiasEvidence:
        return self.absolute.get(key, BiasEvidence.missing(f"no entry for {key}"))

    def contrast_evidence(self, key: str) -> BiasEvidence:
        return self.contrast.get(
            key,
            BiasEvidence.missing(
                f"no jointly computed contrast bias bound for {key}; it may "
                "not be inferred from two absolute bounds"
            ),
        )

    def absolute_bound(self, key: str) -> float:
        return self.absolute_evidence(key).require()

    def contrast_bound(self, key: str) -> float:
        return self.contrast_evidence(key).require()


# ---------------------------------------------------------------------------
# Expected-likelihood pseudo-true log beta (U.20 implicit derivative)
# ---------------------------------------------------------------------------

def innovation_covariance_under_truth(
    truth: StateSpace, model: StateSpace, gain: Matrix
) -> Matrix:
    """Stationary ``Var(v)`` when the ``model`` filter is driven by ``truth`` data.

    The joint (true latent, filter state) is a linear system; its stationary
    covariance solves a discrete Lyapunov equation, so this is exact and needs
    no simulation::

        u_{i+1}    = F_t u_i + n_i
        xhat_{i+1} = K C_t u_i + (F_m - K C_m) xhat_i + K m_i
        v_i        = C_t u_i - C_m xhat_i + m_i
    """
    d = len(truth.sigma)
    fm_kc = nm.sub(model.f, nm.matmul(gain, model.c_obs))
    kct = nm.matmul(gain, truth.c_obs)
    m = nm.zeros(2 * d, 2 * d)
    for i in range(d):
        for j in range(d):
            m[i][j] = truth.f[i][j]
            m[d + i][j] = kct[i][j]
            m[d + i][d + j] = fm_kc[i][j]
    krk = nm.matmul(nm.matmul(gain, truth.r_eff), nm.transpose(gain))
    sk = nm.matmul(truth.s_cross, nm.transpose(gain))
    q = nm.zeros(2 * d, 2 * d)
    for i in range(d):
        for j in range(d):
            q[i][j] = truth.q[i][j]
            q[i][d + j] = sk[i][j]
            q[d + i][j] = sk[j][i]
            q[d + i][d + j] = krk[i][j]
    p = nm.solve_lyapunov_discrete(m, nm.symmetrise(q))
    g = nm.zeros(d, 2 * d)
    for i in range(d):
        for j in range(d):
            g[i][j] = truth.c_obs[i][j]
            g[i][d + j] = -model.c_obs[i][j]
    gpg = nm.matmul(nm.matmul(g, p), nm.transpose(g))
    return nm.symmetrise(nm.add(gpg, truth.r_eff))


def steady_state_gain(ss: StateSpace, max_iter: int = 20000, tol: float = 1e-14):
    """Steady-state one-step predictor gain and innovation covariance."""
    d = len(ss.sigma)
    ct = nm.transpose(ss.c_obs)
    ft = nm.transpose(ss.f)
    p = [row[:] for row in ss.sigma]
    gain = nm.zeros(d, d)
    s_inn = nm.eye(d)
    for _ in range(max_iter):
        s_inn = nm.symmetrise(nm.add(nm.matmul(nm.matmul(ss.c_obs, p), ct), ss.r_eff))
        l = nm.cholesky(s_inn)
        s_inv = nm.chol_solve_mat(l, nm.eye(d))
        gain = nm.matmul(nm.add(nm.matmul(nm.matmul(ss.f, p), ct), ss.s_cross), s_inv)
        p_next = nm.symmetrise(
            nm.sub(
                nm.add(nm.matmul(nm.matmul(ss.f, p), ft), ss.q),
                nm.matmul(nm.matmul(gain, s_inn), nm.transpose(gain)),
            )
        )
        scale = nm.max_abs(p_next)
        if scale > 0.0 and nm.max_abs(nm.sub(p_next, p)) <= tol * scale:
            p = p_next
            break
        p = p_next
    else:
        raise NumericalFailure("steady-state Riccati iteration did not converge")
    s_inn = nm.symmetrise(nm.add(nm.matmul(nm.matmul(ss.c_obs, p), ct), ss.r_eff))
    l = nm.cholesky(s_inn)
    s_inv = nm.chol_solve_mat(l, nm.eye(d))
    gain = nm.matmul(nm.add(nm.matmul(nm.matmul(ss.f, p), ct), ss.s_cross), s_inv)
    return gain, s_inn


def innovation_mean_under_truth(
    truth: StateSpace, model: StateSpace, gain: Matrix
) -> list[float]:
    """Stationary ``E[v]`` when the ``model`` filter is driven by ``truth`` data.

    The latent mean is carried entirely in the state-space offset, so under
    truth ``E[u_i] = 0`` and the only mean driving the filter is the offset
    mismatch ``dc = c_t - c_m``::

        xbar = (I - F_m + K C_m)^{-1} K dc
        vbar = dc - C_m xbar

    ``I - (F_m - K C_m)`` is invertible because the closed-loop filter matrix
    is stable.  Without this term the expected likelihood would be blind to
    the centre nuisance, and a detector-offset calibration error would appear
    to shift log beta.
    """
    d = len(truth.sigma)
    dc = [truth.offset[i] - model.offset[i] for i in range(d)]
    if all(v == 0.0 for v in dc):
        return [0.0] * d
    closed = nm.sub(model.f, nm.matmul(gain, model.c_obs))
    m = nm.sub(nm.eye(d), closed)
    rhs = [[v] for v in nm.matvec(gain, dc)]
    xbar = [row[0] for row in nm.lu_solve(m, rhs)]
    cx = nm.matvec(model.c_obs, xbar)
    return [dc[i] - cx[i] for i in range(d)]


def expected_loglik_per_frame(truth: StateSpace, model: StateSpace) -> float:
    """Expected log likelihood per frame of ``model`` under data from ``truth``.

    Deterministic and closed form: no trajectory is generated.  The mean term
    is included, so every nuisance parameter the production estimator fits --
    the centre included -- is genuinely identified by this objective.
    """
    d = len(truth.sigma)
    gain, s_inn = steady_state_gain(model)
    var_v = innovation_covariance_under_truth(truth, model, gain)
    vbar = innovation_mean_under_truth(truth, model, gain)
    l = nm.cholesky(s_inn)
    logdet = 2.0 * sum(math.log(l[i][i]) for i in range(d))
    s_inv = nm.chol_solve_mat(l, nm.eye(d))
    tr = sum(s_inv[i][j] * var_v[j][i] for i in range(d) for j in range(d))
    quad = sum(vbar[i] * s_inv[i][j] * vbar[j] for i in range(d) for j in range(d))
    return -0.5 * (logdet + tr + quad + d * math.log(2.0 * math.pi))


# ---------------------------------------------------------------------------
# Field model: phi -> (H_eff, observation calibration, truth state space)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class FieldModel:
    """Everything one record's analysis depends on, as a function of ``phi``."""

    h_eff: Matrix
    k_eff: Matrix
    temperature: float
    a_drift: Matrix
    sigma: Matrix
    p_matrix: Matrix
    r_obs: Matrix
    b_det: tuple[float, float]
    dt: float
    t_exp: float

    def truth_state_space(self, mu: Sequence[float] = (0.0, 0.0)) -> StateSpace:
        """The physical truth: the actual stationary law of the real record."""
        return build_state_space(
            self.a_drift, self.sigma, list(mu), self.p_matrix, self.r_obs,
            list(self.b_det), self.dt, self.t_exp,
        )

    @property
    def analysis(self) -> "AnalysisModel":
        """What an analyst holding THESE primitive values would lock in."""
        return AnalysisModel(
            h_locked=self.h_eff, p_matrix=self.p_matrix, r_obs=self.r_obs,
            b_det=self.b_det, dt=self.dt, t_exp=self.t_exp,
        )


@dataclass(frozen=True)
class AnalysisModel:
    """Everything the ANALYSIS side takes from the measured primitives.

    An error in ``phi`` is a calibration measurement error, so it moves what
    the analyst locks in -- ``H_A`` and the observation calibration -- while
    the physics generating the record stays where it is.  V3 had this the
    other way round: it perturbed the truth and held ``h_locked`` fixed, which
    gives sensitivities of the opposite sign.  The magnitudes agree, so the
    propagated absolute sigma was unaffected, but the sign is what determines
    whether a shared calibration error cancels or adds in a cross-field
    contrast, so the production path uses the analysis-side derivative.
    """

    h_locked: Matrix
    p_matrix: Matrix
    r_obs: Matrix
    b_det: tuple[float, float]
    dt: float
    t_exp: float


#: A builder maps a primitive value vector to a FieldModel for one record.
FieldModelBuilder = Callable[[Sequence[float]], FieldModel]


# ---------------------------------------------------------------------------
# U.20: the profiled nuisance system
# ---------------------------------------------------------------------------

#: The production locked-fit parameter vector, in the T-stage 8.2
#: parameterisation.  This is exactly what ``estimate.fit_record`` maximises:
#: the scale, the centre, and the full temporal nuisance ``A`` through
#: ``A Sigma = D + Q``.  V3 profiled only ``log beta`` and tied the drift to
#: the true diffusion, which is not the U.20 production derivative.
THETA_NAMES: tuple[str, ...] = (
    "log_beta", "mu_x", "mu_y", "d_chol_0", "d_chol_1", "d_chol_2", "omega",
)
N_THETA = len(THETA_NAMES)
#: Index of the log-beta row, extracted only AFTER the nuisance is profiled.
LOG_BETA_ROW = 0


def theta_of(params: Parameters) -> list[float]:
    return [
        params.log_beta, params.mu[0], params.mu[1],
        params.d_chol[0], params.d_chol[1], params.d_chol[2], params.omega,
    ]


def params_of(theta: Sequence[float]) -> Parameters:
    return Parameters(
        log_beta=float(theta[0]),
        mu=(float(theta[1]), float(theta[2])),
        d_chol=(float(theta[3]), float(theta[4]), float(theta[5])),
        omega=float(theta[6]),
        sigma_chol=None,
    )


def model_state_space(theta: Sequence[float], am: AnalysisModel) -> StateSpace:
    """The analysis model at parameter ``theta``, using the locked calibration."""
    params = params_of(theta)
    sigma = sigma_of(params, am.h_locked)
    a = drift_of(params, sigma)
    return build_state_space(
        a, sigma, [float(theta[1]), float(theta[2])], am.p_matrix, am.r_obs,
        list(am.b_det), am.dt, am.t_exp,
    )


def truth_matching_theta(fm: FieldModel, mu: Sequence[float] = (0.0, 0.0)) -> list[float]:
    """The ``theta`` at which the analysis model reproduces the truth exactly.

    At the unperturbed primitives the analysis and the physics coincide, so
    this is the exact maximiser of the expected likelihood and the correct
    linearisation point for U.20.  ``D = (A Sigma + Sigma A^T)/2`` and
    ``Q = A Sigma - D`` invert the ``A Sigma = D + Q`` split exactly.
    """
    asig = nm.matmul(fm.a_drift, fm.sigma)
    d_mat = nm.symmetrise(nm.scale(nm.add(asig, nm.transpose(asig)), 0.5))
    q_mat = nm.sub(asig, d_mat)
    return [0.0, float(mu[0]), float(mu[1]),
            *chol_params_from_spd(d_mat), float(q_mat[1][0])]


@dataclass(frozen=True)
class ThetaScaling:
    """Characteristic magnitudes making the nuisance steps dimensionless.

    ``log_beta`` and the two Cholesky logs are already logs; the centre scales
    with the latent position spread and the off-diagonal and current entries
    with the magnitude of ``D``.  Differentiating in these coordinates is what
    keeps a step on ``d_chol_1`` from being a factor-of-seven jump.
    """

    scale: tuple[float, ...]

    @staticmethod
    def for_model(fm: FieldModel, theta: Sequence[float]) -> "ThetaScaling":
        pos = math.sqrt(max(fm.sigma[0][0], fm.sigma[1][1]))
        l11 = math.exp(theta[3])
        l22 = math.exp(theta[5])
        d_scale = max(l11 * l11, l22 * l22, abs(theta[4]) * l11, 1e-300)
        return ThetaScaling((1.0, pos, pos, 1.0, max(l11, 1e-300), 1.0, d_scale))

    def to_theta(self, theta0: Sequence[float], z: Sequence[float]) -> list[float]:
        return [theta0[i] + self.scale[i] * z[i] for i in range(len(theta0))]


class SensitivityFailure(NumericalFailure):
    """The U.20 system could not be formed or solved."""


def _evaluation_noise(f: Callable[[Sequence[float]], float], n_z: int) -> float:
    """Measure the absolute evaluation noise of ``f`` near the origin.

    ``f`` is mathematically smooth, so over a window far narrower than any
    real curvature scale its exact values lie on a low-order polynomial.
    Whatever departs from that polynomial is floating-point noise.  Fitting a
    quadratic by least squares over a 1e-6 window and taking the largest
    residual gives the absolute error of ONE evaluation, which is the
    constant the finite-difference roundoff bound needs.  It is measured here
    rather than assumed, because it depends on the conditioning of this
    record's own Riccati and Lyapunov solves.
    """
    width = 1e-6
    probes = 9
    ts = [width * (2.0 * k / (probes - 1) - 1.0) for k in range(probes)]
    vals = []
    for t in ts:
        z = [0.0] * n_z
        z[0] = t
        vals.append(f(z))
    # Least squares quadratic fit in t.
    n = len(ts)
    basis = [[1.0, t, t * t] for t in ts]
    ata = [[sum(basis[k][i] * basis[k][j] for k in range(n)) for j in range(3)]
           for i in range(3)]
    atb = [[sum(basis[k][i] * vals[k] for k in range(n))] for i in range(3)]
    coef = [row[0] for row in nm.lu_solve(ata, atb)]
    resid = max(abs(vals[k] - sum(coef[i] * basis[k][i] for i in range(3)))
                for k in range(n))
    floor = 8.0 * 2.220446049250313e-16 * max(abs(v) for v in vals)
    return max(resid, floor)


@dataclass(frozen=True)
class ProfiledSensitivity:
    """``d theta* / d phi`` with a certified componentwise error enclosure."""

    #: Full profiled Jacobian, ``N_THETA`` rows by ``len(phi)`` columns.
    jacobian: Matrix
    #: Componentwise certified absolute error radius of ``jacobian``.
    radius: Matrix
    #: Measured absolute evaluation error of the expected log likelihood.
    evaluation_noise: float
    #: Condition of the profiled expected-information matrix.
    information_condition: float
    #: Dimensionless differencing steps actually used.
    theta_step: float
    phi_step: tuple[float, ...]
    method: str = "implicit differentiation of the expected-score system"

    @property
    def log_beta_row(self) -> list[float]:
        return list(self.jacobian[LOG_BETA_ROW])

    @property
    def log_beta_radius(self) -> list[float]:
        return list(self.radius[LOG_BETA_ROW])


def primitive_steps(
    phi: Sequence[float],
    phi_sigma: Sequence[float] | None,
    fraction: float,
    rel_step: float,
    abs_step: float,
) -> list[float]:
    """Differencing step for each primitive, in that primitive's own units.

    The declared standard uncertainty is the right scale: it is exactly the
    range over which the linearisation is going to be used, and it carries the
    primitive's units, so one dimensionless fraction serves every primitive.
    A single absolute step cannot: 1e-3 is a sensible log-stiffness step and a
    one-millimetre detector offset, and the second is nine orders of magnitude
    past the bead's own position scale.

    Falling back to a relative or absolute step when no uncertainty is
    declared is for diagnostics only; the official path always supplies
    ``phi_sigma`` from ``C_phi``'s own diagonal.
    """
    out: list[float] = []
    for k, v in enumerate(phi):
        sig = None if phi_sigma is None else float(phi_sigma[k])
        if sig is not None and math.isfinite(sig) and sig > 0.0:
            out.append(fraction * sig)
        elif v != 0.0:
            out.append(rel_step * abs(v))
        else:
            out.append(abs_step)
    return out


def profiled_sensitivity(
    builder: FieldModelBuilder,
    phi: Sequence[float],
    truth: StateSpace | None = None,
    theta_step: float = 1e-3,
    phi_sigma: Sequence[float] | None = None,
    phi_step_fraction: float = 1.0,
    phi_rel_step: float = 1e-3,
    phi_abs_step: float = 1e-3,
) -> ProfiledSensitivity:
    """The U.20 production derivative, with the full nuisance system profiled.

    Implements option A of the brief directly::

        d theta* / d phi = - (d_theta E s)^{-1} (d_phi E s)

    where ``E s = d_theta L`` and ``L`` is the exact expected T.6 log
    likelihood per frame.  Because ``L`` is available in closed form through a
    discrete Lyapunov solve, both blocks are second derivatives of a smooth
    deterministic function; no trajectory is generated and no inner optimiser
    noise enters.  The log-beta row is extracted only after the full system --
    scale, centre and the temporal nuisance ``A`` -- has been solved.

    The truth is held FIXED.  ``phi`` moves the analysis side only, which is
    what a calibration measurement error physically does.
    """
    phi = [float(v) for v in phi]
    base = builder(phi)
    if truth is None:
        truth = base.truth_state_space()
    theta0 = truth_matching_theta(base)
    sc = ThetaScaling.for_model(base, theta0)
    p = len(phi)

    # Keyed by the STEP as well as the direction: the coarse pass uses a
    # different phi step, and reusing the fine models there would silently
    # halve the coarse derivative and poison the consistency radius.
    analysis_cache: dict[tuple[int, int, float], AnalysisModel] = {}

    def analysis_at(k: int, sign: int, step: float) -> AnalysisModel:
        if sign == 0:
            return base.analysis
        key = (k, sign, step)
        if key not in analysis_cache:
            q = list(phi)
            q[k] += sign * step
            analysis_cache[key] = builder(q).analysis
        return analysis_cache[key]

    def loglik(z: Sequence[float], am: AnalysisModel) -> float:
        try:
            return expected_loglik_per_frame(truth, model_state_space(sc.to_theta(theta0, z), am))
        except NumericalFailure as exc:
            raise SensitivityFailure(f"expected likelihood not evaluable: {exc}") from exc

    eps_l = _evaluation_noise(lambda z: loglik(z, base.analysis), N_THETA)

    steps_phi = primitive_steps(
        phi, phi_sigma, phi_step_fraction, phi_rel_step, phi_abs_step
    )

    def jac_at(h: float, gfac: float) -> tuple[Matrix, Matrix, float]:
        """Return ``(J, H, cond)`` at dimensionless theta step ``h``."""
        zero = [0.0] * N_THETA
        l0 = loglik(zero, base.analysis)

        def lz(idx: Sequence[int], signs: Sequence[int], am: AnalysisModel) -> float:
            z = [0.0] * N_THETA
            for i, sgn in zip(idx, signs):
                z[i] += sgn * h
            return loglik(z, am)

        hess = nm.zeros(N_THETA, N_THETA)
        for i in range(N_THETA):
            hess[i][i] = (lz([i], [1], base.analysis) - 2.0 * l0
                          + lz([i], [-1], base.analysis)) / (h * h)
        for i in range(N_THETA):
            for jx in range(i + 1, N_THETA):
                v = (lz([i, jx], [1, 1], base.analysis)
                     - lz([i, jx], [1, -1], base.analysis)
                     - lz([i, jx], [-1, 1], base.analysis)
                     + lz([i, jx], [-1, -1], base.analysis)) / (4.0 * h * h)
                hess[i][jx] = v
                hess[jx][i] = v

        cross = nm.zeros(N_THETA, p)
        for k in range(p):
            gk = gfac * steps_phi[k]
            am_up = analysis_at(k, +1, gk)
            am_dn = analysis_at(k, -1, gk)
            for i in range(N_THETA):
                zp = [0.0] * N_THETA; zp[i] = h
                zm = [0.0] * N_THETA; zm[i] = -h
                cross[i][k] = (
                    loglik(zp, am_up) - loglik(zm, am_up)
                    - loglik(zp, am_dn) + loglik(zm, am_dn)
                ) / (4.0 * h * gk)

        try:
            sol = nm.lu_solve(hess, cross)
        except NumericalFailure as exc:
            raise SensitivityFailure(
                f"profiled expected information is not invertible: {exc}"
            ) from exc
        jz = nm.scale(sol, -1.0)
        vals, _ = nm.eigh(nm.symmetrise(hess))
        lo = min(abs(v) for v in vals)
        hi = max(abs(v) for v in vals)
        cond = hi / lo if lo > 0.0 else float("inf")
        # Back to model coordinates: theta = theta0 + S z.
        j = [[sc.scale[i] * jz[i][k] for k in range(p)] for i in range(N_THETA)]
        return j, hess, cond

    j_fine, hess, cond = jac_at(theta_step, 1.0)
    j_coarse, _, _ = jac_at(2.0 * theta_step, 2.0)

    # Certified radius.  Two independent contributions, added:
    #   * step consistency: the full fine/coarse gap, which for an h^2 scheme
    #     is three times the Richardson error estimate, so this is
    #     conservative;
    #   * roundoff propagated through the linear solve: the mixed block
    #     carries eps/(h g) and the information block eps/h^2, and the solve
    #     amplifies both by ||H^{-1}||.
    h = theta_step
    inv_norm = 0.0
    try:
        hinv = nm.lu_solve(hess, nm.eye(N_THETA))
        inv_norm = nm.op_norm(hinv)
    except NumericalFailure:
        inv_norm = float("inf")
    radius = nm.zeros(N_THETA, p)
    for i in range(N_THETA):
        for k in range(p):
            gk = steps_phi[k]
            d_cross = eps_l / (h * gk)
            d_hess = eps_l / (h * h)
            # |dJ| <= ||H^-1|| (|dM| + |dH| |J|), in dimensionless coordinates.
            jz_ik = abs(j_fine[i][k]) / sc.scale[i]
            prop = inv_norm * (d_cross + d_hess * jz_ik) * sc.scale[i]
            consistency = abs(j_fine[i][k] - j_coarse[i][k])
            radius[i][k] = consistency + prop
    return ProfiledSensitivity(
        jacobian=j_fine,
        radius=radius,
        evaluation_noise=eps_l,
        information_condition=cond,
        theta_step=theta_step,
        phi_step=tuple(steps_phi),
    )


def dimensionless_score_and_information(
    am: AnalysisModel,
    truth: StateSpace,
    theta0: Sequence[float],
    scaling: ThetaScaling,
    z: Sequence[float],
    h: float = 1e-3,
) -> tuple[list[float], Matrix]:
    """Central-difference score and information of ``L`` in ``z`` coordinates."""
    def lz(delta: Sequence[float]) -> float:
        zz = [z[i] + delta[i] for i in range(N_THETA)]
        return expected_loglik_per_frame(
            truth, model_state_space(scaling.to_theta(theta0, zz), am)
        )

    l0 = lz([0.0] * N_THETA)
    grad = [0.0] * N_THETA
    hess = nm.zeros(N_THETA, N_THETA)
    for i in range(N_THETA):
        up = [0.0] * N_THETA; up[i] = h
        dn = [0.0] * N_THETA; dn[i] = -h
        lu, ld = lz(up), lz(dn)
        grad[i] = (lu - ld) / (2.0 * h)
        hess[i][i] = (lu - 2.0 * l0 + ld) / (h * h)
    for i in range(N_THETA):
        for j in range(i + 1, N_THETA):
            def at(si: int, sj: int) -> float:
                d = [0.0] * N_THETA; d[i] = si * h; d[j] = sj * h
                return lz(d)
            v = (at(1, 1) - at(1, -1) - at(-1, 1) + at(-1, -1)) / (4.0 * h * h)
            hess[i][j] = v
            hess[j][i] = v
    return grad, hess


def located_maximum_error(
    am: AnalysisModel,
    truth: StateSpace,
    theta0: Sequence[float],
    scaling: ThetaScaling,
    z: Sequence[float],
) -> list[float]:
    """Distance from a located maximum to the true stationary point.

    Standard backward-to-forward error: at the returned point the score is not
    exactly zero, and ``delta z = H^{-1} grad`` is the displacement that would
    zero it.  This is what certifies option B, and it is measured at the point
    the optimiser actually returned rather than assumed from a tolerance.
    """
    grad, hess = dimensionless_score_and_information(am, truth, theta0, scaling, z)
    try:
        delta = nm.lu_solve(hess, [[g] for g in grad])
    except NumericalFailure as exc:
        raise SensitivityFailure(f"information not invertible at the maximum: {exc}") from exc
    return [abs(row[0]) for row in delta]


def profiled_pseudo_true(
    builder: FieldModelBuilder,
    phi: Sequence[float],
    truth: StateSpace,
    theta0: Sequence[float],
    scaling: ThetaScaling,
    max_evaluations: int = 20000,
) -> tuple[list[float], list[float]]:
    """Locate ``theta*(phi)`` by maximising the SAME expected likelihood.

    This is option B of the brief.  It is not the production path -- locating
    a maximum numerically costs several orders of magnitude in precision --
    but differencing it must reproduce :func:`profiled_sensitivity` within
    both methods' certified errors, and that agreement is the demonstration
    the brief requires.

    Returns the located ``theta*`` together with its certified dimensionless
    location error.
    """
    am = builder(phi).analysis

    def objective(z: Sequence[float]) -> float:
        try:
            return -expected_loglik_per_frame(
                truth, model_state_space(scaling.to_theta(theta0, z), am)
            )
        except NumericalFailure:
            return float("inf")

    res = minimise(objective, [0.0] * N_THETA, max_evaluations=max_evaluations)
    if not res.converged:
        raise SensitivityFailure(f"profiled maximisation did not converge: {res.reason}")
    err = located_maximum_error(am, truth, theta0, scaling, res.x)
    return scaling.to_theta(theta0, res.x), err


def profiled_sensitivity_by_optimisation(
    builder: FieldModelBuilder,
    phi: Sequence[float],
    phi_sigma: Sequence[float] | None = None,
    phi_step_fraction: float = 1.0,
    rel_step: float = 1e-2,
    abs_step: float = 1e-2,
) -> ProfiledSensitivity:
    """Option B: central differences of the fully profiled ``theta*``.

    Carries its own certified radius, built from the located-maximum error at
    each of the points actually used.  That radius is typically orders of
    magnitude wider than option A's, which is exactly why option A is the
    production path.
    """
    phi = [float(v) for v in phi]
    base = builder(phi)
    truth = base.truth_state_space()
    theta0 = truth_matching_theta(base)
    sc = ThetaScaling.for_model(base, theta0)
    steps = primitive_steps(phi, phi_sigma, phi_step_fraction, rel_step, abs_step)
    p = len(phi)
    jac = nm.zeros(N_THETA, p)
    rad = nm.zeros(N_THETA, p)
    for k in range(p):
        step = steps[k]
        up = list(phi); up[k] += step
        dn = list(phi); dn[k] -= step
        t_up, e_up = profiled_pseudo_true(builder, up, truth, theta0, sc)
        t_dn, e_dn = profiled_pseudo_true(builder, dn, truth, theta0, sc)
        for i in range(N_THETA):
            jac[i][k] = (t_up[i] - t_dn[i]) / (2.0 * step)
            rad[i][k] = sc.scale[i] * (e_up[i] + e_dn[i]) / (2.0 * step)
    return ProfiledSensitivity(
        jacobian=jac,
        radius=rad,
        evaluation_noise=float("nan"),
        information_condition=float("nan"),
        theta_step=float("nan"),
        phi_step=tuple(steps),
        method="central differences of the profiled pseudo-true parameter",
    )


def enclosures_overlap(
    a: ProfiledSensitivity, b: ProfiledSensitivity, i: int, k: int
) -> bool:
    """True when the two methods' certified enclosures of one entry intersect."""
    lo_a, hi_a = a.jacobian[i][k] - a.radius[i][k], a.jacobian[i][k] + a.radius[i][k]
    lo_b, hi_b = b.jacobian[i][k] - b.radius[i][k], b.jacobian[i][k] + b.radius[i][k]
    return not (hi_a < lo_b or hi_b < lo_a)
# ---------------------------------------------------------------------------
# Experiment-level calibration: the official path
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RecordCalibration:
    """Per-record inputs to the experiment-level calibration object."""

    key: str
    builder: FieldModelBuilder
    #: Index of this record's log-beta endpoint in the joint vector.
    index: int


@dataclass(frozen=True)
class ExperimentCalibration:
    """The joint calibration covariance of all eight log-beta endpoints.

    Shared calibration primitives couple the records, so a record is NOT an
    isolated scalar inference object: ``C_b,cal`` is assembled once for the
    whole experiment and every absolute and contrast uncertainty is read off
    the SAME matrix.  Recomputing a contrast independently would discard the
    off-diagonal blocks and so discard exactly the cancellation a within-block
    contrast exists to exploit.
    """

    keys: tuple[str, ...]
    #: ``C_b,cal = J_beta C_phi J_beta^T`` over all eight records jointly.
    c_b_cal: Matrix
    #: The log-beta sensitivity matrix, eight rows by ``len(phi)`` columns.
    j_beta: Matrix
    #: Certified componentwise error radius of ``j_beta``.
    j_radius: Matrix
    #: The primitive covariance and its entrywise absolute value.
    c_phi: Matrix
    phi_names: tuple[str, ...]
    #: Full profiled sensitivity per record, retained for audit.
    sensitivities: tuple[ProfiledSensitivity, ...] = ()

    def index_of(self, key: str) -> int:
        if key not in self.keys:
            raise NumericalFailure(f"record {key!r} is not in this calibration")
        return self.keys.index(key)

    def _row_sigma(self, row: Sequence[float]) -> float:
        v = sum(row[i] * self.c_phi[i][j] * row[j]
                for i in range(len(row)) for j in range(len(row)))
        if v < 0.0:
            # Scale relative to C_phi's OWN diagonal.  An ``or 1.0`` fallback
            # would turn a degenerate covariance into an absolute test, and
            # log-beta variances are of order 1e-5.
            scale = max(abs(self.c_phi[i][i]) for i in range(len(row)))
            if scale > 0.0 and v > -1e-12 * scale:
                return 0.0
            raise NumericalFailure(
                f"calibration variance {v:.3e} is negative beyond rounding "
                f"(C_phi diagonal scale {scale:.3e})"
            )
        return math.sqrt(v)

    def _row_radius(self, radius: Sequence[float]) -> float:
        """Rigorous bound on how far the certified Jacobian error can move sigma.

        ``x -> sqrt(x^T C x)`` is a seminorm for PSD ``C``, so the triangle
        inequality gives ``|sigma(j + d) - sigma(j)| <= sigma(d)`` for any
        single ``d``.  The supremum of ``sigma(d)`` over the box
        ``|d_k| <= radius_k`` is attained at a vertex and is bounded by
        ``sqrt(radius^T |C| radius)`` with ``|C|`` taken entrywise.
        """
        v = sum(radius[i] * abs(self.c_phi[i][j]) * radius[j]
                for i in range(len(radius)) for j in range(len(radius)))
        return math.sqrt(max(0.0, v))

    def absolute_sigma(self, key: str) -> NumericalEnclosure:
        i = self.index_of(key)
        point = self._row_sigma(self.j_beta[i])
        rad = self._row_radius(self.j_radius[i])
        return NumericalEnclosure(
            point, max(0.0, point - rad), point + rad,
            "certified Jacobian enclosure propagated through C_phi",
        )

    def contrast_row(self, key: str, reference: str) -> tuple[list[float], list[float]]:
        i, r = self.index_of(key), self.index_of(reference)
        p = len(self.phi_names)
        row = [self.j_beta[i][k] - self.j_beta[r][k] for k in range(p)]
        rad = [self.j_radius[i][k] + self.j_radius[r][k] for k in range(p)]
        return row, rad

    def contrast_sigma(self, key: str, reference: str) -> NumericalEnclosure:
        """``sqrt(d C_phi d^T)`` with ``d`` the contrast row of the SAME matrix.

        Equivalently ``C_d = D C_b D^T``: forming the difference in the
        Jacobian before contracting with ``C_phi`` is algebraically identical
        and keeps every shared-primitive cancellation exact.
        """
        row, rad = self.contrast_row(key, reference)
        point = self._row_sigma(row)
        r = self._row_radius(rad)
        return NumericalEnclosure(
            point, max(0.0, point - r), point + r,
            "certified Jacobian enclosure propagated through C_phi",
        )

    def absolute_qualification(self, key: str) -> str:
        return classify_with_enclosure(self.absolute_sigma(key), SIGMA_CAL_ABS_MAX)

    def contrast_qualification(self, key: str, reference: str) -> str:
        return classify_with_enclosure(
            self.contrast_sigma(key, reference), SIGMA_CAL_CONTRAST_MAX
        )

    def as_dict(self) -> dict:
        return {
            "keys": list(self.keys),
            "phi_names": list(self.phi_names),
            "absolute_sigma": {
                k: self.absolute_sigma(k).point for k in self.keys
            },
            "absolute_qualification": {
                k: self.absolute_qualification(k) for k in self.keys
            },
        }


def build_experiment_calibration(
    vector: PrimitiveVector,
    records: Sequence[tuple[str, FieldModelBuilder]],
    theta_step: float = 1e-3,
    phi_step_fraction: float = 1.0,
) -> ExperimentCalibration:
    """Propagate ``C_phi`` through every record to the joint log-beta covariance.

    Each record contributes one row of ``J_beta``, obtained from the FULL
    profiled U.20 system; the log-beta row is extracted only after the centre
    and temporal nuisance have been profiled out.  Because shared primitives
    occupy one column of ``phi``, a standard common to several records
    produces correlated rows automatically and the off-diagonal blocks of
    ``C_b,cal`` follow with no independence assumption anywhere.
    """
    phi = vector.values
    sigma = [p.sigma for p in vector.primitives]
    c_phi = vector.covariance()
    rows: list[list[float]] = []
    radii: list[list[float]] = []
    keys: list[str] = []
    sens: list[ProfiledSensitivity] = []
    for key, builder in records:
        ps = profiled_sensitivity(
            builder, phi, theta_step=theta_step, phi_sigma=sigma,
            phi_step_fraction=phi_step_fraction,
        )
        keys.append(key)
        rows.append(ps.log_beta_row)
        radii.append(ps.log_beta_radius)
        sens.append(ps)
    c_b = nm.symmetrise(nm.matmul(nm.matmul(rows, c_phi), nm.transpose(rows)))
    return ExperimentCalibration(
        keys=tuple(keys),
        c_b_cal=c_b,
        j_beta=rows,
        j_radius=radii,
        c_phi=c_phi,
        phi_names=tuple(vector.names),
        sensitivities=tuple(sens),
    )


# ---------------------------------------------------------------------------
# The official interval builder
# ---------------------------------------------------------------------------

def combined_standard_error(
    conditional_se: float, calibration_sigma: float
) -> float:
    """Total log-beta standard error (T.24 decomposition).

    ``Var_total = Var_cond + Var_cal``.  The two contributions are the
    Branch-B observation noise at a FIXED locked calibration, and the Branch-A
    calibration measurement error; they are measured on physically separate
    apparatus and share no primitive, so the declared model carries no cross
    term.  The sum is taken once here and nowhere else, so neither part can be
    double counted.
    """
    if conditional_se < 0.0 or calibration_sigma < 0.0:
        raise NumericalFailure("standard errors must be nonnegative")
    return math.sqrt(conditional_se * conditional_se
                     + calibration_sigma * calibration_sigma)


def combined_contrast_standard_error(
    conditional_se_a: float, conditional_se_b: float, calibration_sigma: float
) -> float:
    """Total contrast standard error.

    The conditional parts are independent across records -- separate frames,
    separate noise -- so they add in quadrature.  The calibration part is NOT
    independent and arrives already correlated, from
    :meth:`ExperimentCalibration.contrast_sigma`, which reads the joint
    matrix.
    """
    for v in (conditional_se_a, conditional_se_b, calibration_sigma):
        if v < 0.0:
            raise NumericalFailure("standard errors must be nonnegative")
    return math.sqrt(
        conditional_se_a * conditional_se_a
        + conditional_se_b * conditional_se_b
        + calibration_sigma * calibration_sigma
    )
