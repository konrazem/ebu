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
from .observation import StateSpace, build_state_space
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
    """

    #: Per-record absolute log-beta bias magnitudes, by (block, field) key.
    absolute: Mapping[str, float] = field(default_factory=dict)
    #: Per-contrast bias magnitudes, computed jointly, by contrast key.
    contrast: Mapping[str, float] = field(default_factory=dict)

    def absolute_bound(self, key: str) -> float:
        return float(self.absolute.get(key, 0.0))

    def contrast_bound(self, key: str) -> float:
        if key not in self.contrast:
            raise NumericalFailure(
                f"no jointly computed contrast bias bound for {key!r}; it may "
                "not be inferred from two absolute bounds"
            )
        return float(self.contrast[key])


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


def expected_loglik_per_frame(truth: StateSpace, model: StateSpace) -> float:
    """Expected log likelihood per frame of ``model`` under data from ``truth``.

    Deterministic and closed form: no trajectory is generated.
    """
    d = len(truth.sigma)
    gain, s_inn = steady_state_gain(model)
    var_v = innovation_covariance_under_truth(truth, model, gain)
    l = nm.cholesky(s_inn)
    logdet = 2.0 * sum(math.log(l[i][i]) for i in range(d))
    s_inv = nm.chol_solve_mat(l, nm.eye(d))
    tr = sum(s_inv[i][j] * var_v[j][i] for i in range(d) for j in range(d))
    return -0.5 * (logdet + tr + d * math.log(2.0 * math.pi))


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

    def state_space(self, h_locked: Matrix | None = None, log_beta: float = 0.0) -> StateSpace:
        """State space of the declared model.

        With ``h_locked`` supplied the latent covariance is
        ``exp(-log_beta) * h_locked^{-1}``, which is what the analysis fits;
        with it absent the true physical covariance is used.
        """
        if h_locked is None:
            sigma = self.sigma
            a = self.a_drift
        else:
            sigma = nm.scale(nm.spd_inverse(h_locked), math.exp(-log_beta))
            # Preserve the physical dissipation D = (A Sigma + Sigma A^T)/2.
            asig = nm.matmul(self.a_drift, self.sigma)
            d_mat = nm.symmetrise(nm.scale(nm.add(asig, nm.transpose(asig)), 0.5))
            a = nm.matmul(d_mat, nm.spd_inverse(sigma))
        return build_state_space(
            a, sigma, [0.0, 0.0], self.p_matrix, self.r_obs, list(self.b_det),
            self.dt, self.t_exp,
        )


#: A builder maps a primitive value vector to a FieldModel for one record.
FieldModelBuilder = Callable[[Sequence[float]], FieldModel]


def pseudo_true_log_beta(
    builder: FieldModelBuilder,
    phi: Sequence[float],
    h_locked: Matrix,
    bracket: float = 0.35,
    tol: float = 1e-12,
) -> float:
    """Pseudo-true ``log beta`` maximising the expected likelihood at ``phi``.

    This is the U.20 implicit derivative evaluated by its definition rather
    than through the ideal trace formula, which T/U forbid as the production
    sensitivity once the noisy temporal likelihood is active: it uses the
    actual exposure-integrated, noise-bearing state-space likelihood.

    Golden-section maximisation on a bracket; deterministic and reproducible.
    """
    truth = builder(phi).state_space()
    model_field = builder(phi)

    def objective(b: float) -> float:
        return expected_loglik_per_frame(truth, model_field.state_space(h_locked, b))

    inv_phi_ratio = (math.sqrt(5.0) - 1.0) / 2.0
    lo, hi = -bracket, bracket
    c = hi - inv_phi_ratio * (hi - lo)
    d = lo + inv_phi_ratio * (hi - lo)
    fc, fd = objective(c), objective(d)
    for _ in range(200):
        if hi - lo <= tol:
            break
        if fc > fd:
            hi, d, fd = d, c, fc
            c = hi - inv_phi_ratio * (hi - lo)
            fc = objective(c)
        else:
            lo, c, fc = c, d, fd
            d = lo + inv_phi_ratio * (hi - lo)
            fd = objective(d)
    return 0.5 * (lo + hi)


def log_beta_sensitivity(
    builder: FieldModelBuilder,
    phi: Sequence[float],
    h_locked: Matrix,
    rel_step: float = 1e-2,
    abs_step: float = 1e-2,
) -> list[float]:
    """``J_beta = d log beta* / d phi`` by central differences on the pseudo-true value.

    ``h_locked`` is held FIXED while ``phi`` moves: that is exactly the
    experimental situation, where Branch A's locked calibration is used to
    analyse data generated by the true physics.

    The differencing step must stay well above the maximiser's own resolution.
    The pseudo-true value is located by maximising a numerically evaluated
    expected likelihood, so its position carries noise of order
    ``sqrt(2 eps / curvature)``; a small step differentiates that noise rather
    than the pseudo-true value.  The regime here is noise-limited, not
    truncation-limited: measured against the exact analytic answer for a common
    log-scale error, the error FALLS with increasing step (6.7e-5 at 1e-3,
    6.2e-7 at 1e-2), which is the opposite of truncation behaviour.
    """
    j: list[float] = []
    for k in range(len(phi)):
        h = rel_step * abs(phi[k]) if phi[k] != 0.0 else abs_step
        up = list(phi); up[k] += h
        dn = list(phi); dn[k] -= h
        b_up = pseudo_true_log_beta(builder, up, h_locked)
        b_dn = pseudo_true_log_beta(builder, dn, h_locked)
        j.append((b_up - b_dn) / (2.0 * h))
    return j


# ---------------------------------------------------------------------------
# End-to-end covariance assembly
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CalibrationCovariance:
    """The complete calibration covariance of the eight log-beta endpoints."""

    #: Record keys in fixed order.
    keys: tuple[str, ...]
    #: ``C_b,cal = J_beta C_phi J_beta^T`` over all eight records jointly.
    c_b_cal: Matrix
    #: Per-record sensitivity rows, retained for audit.
    jacobian: Matrix
    #: The primitive names, in the order of the Jacobian columns.
    phi_names: tuple[str, ...]

    def absolute_sigma(self, index: int) -> float:
        v = self.c_b_cal[index][index]
        if v < 0.0:
            raise NumericalFailure("negative calibration variance")
        return math.sqrt(v)

    def contrast_variance(self, j: int, ref: int) -> float:
        v = self.c_b_cal[j][j] + self.c_b_cal[ref][ref] - 2.0 * self.c_b_cal[j][ref]
        if v < 0.0:
            scale = max(abs(self.c_b_cal[j][j]), abs(self.c_b_cal[ref][ref]), 1e-300)
            if v > -1e-12 * scale:
                return 0.0
            raise NumericalFailure(
                f"contrast variance {v:.3e} is negative beyond rounding"
            )
        return v

    def contrast_sigma(self, j: int, ref: int) -> float:
        return math.sqrt(self.contrast_variance(j, ref))


def assemble_calibration_covariance(
    vector: PrimitiveVector,
    builders: Sequence[tuple[str, FieldModelBuilder, Matrix]],
    rel_step: float = 1e-2,
) -> CalibrationCovariance:
    """Propagate ``C_phi`` through every record to the joint log-beta covariance.

    ``builders`` supplies, per record, its key, its ``phi -> FieldModel`` map
    and its locked ``H_A``.  Because shared primitives occupy one column of
    ``phi``, a standard common to several records produces correlated rows of
    ``J_beta`` automatically, and the off-diagonal blocks of ``C_b,cal`` follow
    without any independence assumption.
    """
    phi = vector.values
    c_phi = vector.covariance()
    rows: list[list[float]] = []
    keys: list[str] = []
    for key, builder, h_locked in builders:
        keys.append(key)
        rows.append(log_beta_sensitivity(builder, phi, h_locked, rel_step=rel_step))
    j = rows
    c_b = nm.matmul(nm.matmul(j, c_phi), nm.transpose(j))
    return CalibrationCovariance(
        keys=tuple(keys),
        c_b_cal=nm.symmetrise(c_b),
        jacobian=j,
        phi_names=tuple(vector.names),
    )
