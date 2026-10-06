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

import hashlib
import json
import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Mapping, Sequence

from . import certified as cert
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
    CEILING_UNRESOLVED,
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


class PrimitiveClass(str, Enum):
    """How a required calibration primitive category is accounted for.

    U requires every load-bearing category to be *declared*.  Absence must
    never mean zero uncertainty, which is the strongest possible claim
    obtainable by supplying nothing, so a category that is not stochastic must
    say which of the other four it is and why.
    """

    UNCERTAIN = "uncertain"
    EXACT_CONSTANT = "exact_constant"
    FIXED_BY_VALIDATION_CASE = "fixed_by_validation_case"
    BOUNDED_SYSTEMATIC = "bounded_systematic"
    NOT_APPLICABLE = "not_applicable"


#: Every auxiliary primitive category U requires the packet to account for.
#: A declaration set missing any of these is refused.
REQUIRED_PRIMITIVE_CATEGORIES: tuple[str, ...] = (
    "viscosity_eta_of_T",
    "temperature_calibration",
    "bead_radius_material_transfer",
    "force_displacement_calibration_3d",
    "axial_stiffness_coupling",
    "wall_hydrodynamic_resistance",
    "coordinate_transform_P",
    "centre_fiducial_transfer",
    "localization_covariance_R_obs",
    "detector_offset",
    "shutter_exposure",
    "timing_synchronization",
    "shared_standards",
    "block_specific",
    "field_specific",
)


@dataclass(frozen=True)
class CategoryDeclaration:
    """How one required category is accounted for in this packet."""

    category: str
    classification: PrimitiveClass
    #: Primitive NAMES (not keys) carrying this category, when UNCERTAIN.
    members: tuple[str, ...] = ()
    #: Deterministic magnitude, when BOUNDED_SYSTEMATIC.
    bound: float | None = None
    justification: str = ""

    def validate(self) -> list[str]:
        bad: list[str] = []
        if self.category not in REQUIRED_PRIMITIVE_CATEGORIES:
            bad.append(f"{self.category}: not a required category")
        if self.classification is PrimitiveClass.UNCERTAIN and not self.members:
            bad.append(f"{self.category}: UNCERTAIN with no primitive members")
        if self.classification is PrimitiveClass.BOUNDED_SYSTEMATIC and not (
            self.bound is not None and math.isfinite(self.bound)
            and self.bound >= 0.0
        ):
            bad.append(f"{self.category}: BOUNDED_SYSTEMATIC with no finite bound")
        if self.classification in (
            PrimitiveClass.EXACT_CONSTANT,
            PrimitiveClass.FIXED_BY_VALIDATION_CASE,
            PrimitiveClass.NOT_APPLICABLE,
        ) and not self.justification:
            bad.append(f"{self.category}: {self.classification.value} with no justification")
        return bad


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
    #: Loadings on declared independent latent standards, as fractions of
    #: ``sigma``.  ``phi_i = sum_l a_il sigma_i z_l + sqrt(1 - sum a^2) sigma_i e_i``
    #: with ``z`` and ``e`` independent standard normals, so a standard shared
    #: by two primitives is ONE latent variable rather than an asserted
    #: off-diagonal entry.
    loadings: tuple[tuple[str, float], ...] = ()

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
    #: Declared independent latent standard variables, in fixed order.
    latents: list[str] = field(default_factory=list)

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

    def declare_latent(self, name: str) -> None:
        """Declare an independent unit-variance latent standard variable."""
        if name not in self.latents:
            self.latents.append(name)

    def load_on_latent(self, key: str, latent: str, fraction: float) -> None:
        """Make primitive ``key`` load on ``latent`` with the given fraction.

        ``fraction`` is a coefficient on ``sigma`` of a unit-variance latent,
        so two primitives loading ``sqrt(rho)`` on the same latent acquire
        correlation exactly ``rho`` while keeping their declared variances.
        The sharing is then a STRUCTURAL property of the generating law and
        survives into the draw, rather than an off-diagonal number asserted
        only in the analyser's matrix.
        """
        self.declare_latent(latent)
        i = self.index_of(key)
        p = self.primitives[i]
        loadings = dict(p.loadings)
        loadings[latent] = float(fraction)
        total = sum(v * v for v in loadings.values())
        if total > 1.0 + 1e-12:
            raise NumericalFailure(
                f"latent loadings on {key!r} sum to {total!r} > 1; the "
                "declared standard uncertainty cannot be exceeded by its own "
                "shared part"
            )
        self.primitives[i] = Primitive(
            p.name, p.scope, p.value, p.sigma, p.block, p.fld,
            tuple(sorted(loadings.items())),
        )

    def loading_matrix(self) -> Matrix:
        """``Lambda`` with ``Lambda[i][l] = a_il * sigma_i``."""
        n, m = len(self.primitives), len(self.latents)
        lam = nm.zeros(n, m) if m else []
        for i, p in enumerate(self.primitives):
            for name, frac in p.loadings:
                lam[i][self.latents.index(name)] = frac * p.sigma
        return lam

    def residual_sigma(self) -> list[float]:
        """Independent part of each primitive's standard uncertainty."""
        out = []
        for p in self.primitives:
            shared = sum(f * f for _, f in p.loadings)
            out.append(p.sigma * math.sqrt(max(0.0, 1.0 - shared)))
        return out

    def draw(self, stream) -> list[float]:
        """One draw of ``phi = Lambda z + e`` from the declared law.

        The latent standards are drawn ONCE and enter every primitive that
        loads on them, so a control that misspecifies the analyser's
        covariance still faces data generated with the true shared structure.
        """
        z = dict(zip(self.latents, stream.normals(len(self.latents))))
        res = self.residual_sigma()
        e = stream.normals(len(self.primitives))
        return [
            p.value
            + sum(frac * p.sigma * z[name] for name, frac in p.loadings)
            + res[i] * e[i]
            for i, p in enumerate(self.primitives)
        ]

    def covariance(self) -> Matrix:
        """Assemble ``C_phi``.

        Diagonal entries are the declared variances.  Off-diagonal entries
        come from declared latent loadings -- ``Lambda Lambda^T`` -- and from
        any explicitly declared correlation.  Sharing is expressed by a shared
        *identity* and by a shared latent, never by an asserted number alone.
        """
        n = len(self.primitives)
        c = nm.zeros(n, n)
        for i, p in enumerate(self.primitives):
            c[i][i] = p.sigma * p.sigma
        lam = self.loading_matrix()
        if self.latents:
            for i in range(n):
                for j in range(n):
                    if i == j:
                        continue
                    c[i][j] += sum(lam[i][l] * lam[j][l]
                                   for l in range(len(self.latents)))
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


# ---------------------------------------------------------------------------
# The joint 99.9% physical calibration region (U)
# ---------------------------------------------------------------------------

#: Total noncoverage the joint physical calibration region is allowed.  This
#: is U's declared auxiliary confidence-set allowance, also carried as a line
#: of the one-sided error budget in the validation plan.  It is not a new
#: scientific threshold.
JOINT_REGION_NONCOVERAGE = 0.001


@dataclass(frozen=True)
class JointCalibrationRegion:
    """The joint 99.9% physical calibration region of the complete packet.

    V5 qualified the axial reduction over an informal "3 sigma" marginal
    shorthand.  That is not U's object: U requires a region with a *stated
    joint* coverage for the whole packet, and a marginal multiple of a single
    primitive's standard uncertainty has none.

    The construction here is deliberately conservative and, crucially, valid
    **regardless of the dependence structure**.  Each stochastic primitive is
    given its own noncoverage allocation ``alpha_i`` with
    ``sum_i alpha_i <= 0.001``; the region is the intersection of the
    individually calibrated marginal regions

        R = { phi : |phi_i - phi_i^| <= k_i sigma_i for every i } ,
        k_i = Phi^{-1}(1 - alpha_i / 2) ,

    and the union bound gives ``P(phi not in R) <= sum_i alpha_i <= 0.001``
    whatever the correlations are.  No independence is assumed anywhere, and
    the correlated primitives are NOT redrawn as if independent: the declared
    latent structure stays in ``C_phi`` and in the generating law, and is
    recorded here alongside the region.

    The deterministic bounded systematics are a SEPARATE set.  They are never
    converted into Gaussian random variables; the total physical
    qualification domain is the combined enlargement of this statistical
    region by that bounded set.
    """

    version: int
    #: Stochastic primitive keys, in the vector's own order.
    primitives: tuple[str, ...]
    sigma: tuple[float, ...]
    alpha: tuple[float, ...]
    coverage_factor: tuple[float, ...]
    #: Declared independent latent standards and the loading matrix, retained
    #: so the dependency structure the region was built over is inspectable.
    latent_basis: tuple[str, ...]
    loadings: tuple[tuple[float, ...], ...]
    #: Deterministic bounded systematics, by category, kept apart.
    bounded_systematics: tuple[tuple[str, float], ...]
    categories: tuple[CategoryDeclaration, ...]

    def __post_init__(self) -> None:
        if not self.primitives:
            raise NumericalFailure("a joint calibration region needs primitives")
        total = sum(self.alpha)
        if not (total <= JOINT_REGION_NONCOVERAGE * (1.0 + 1e-12)):
            raise NumericalFailure(
                f"allocated noncoverage {total!r} exceeds the declared "
                f"{JOINT_REGION_NONCOVERAGE!r}"
            )

    @property
    def total_noncoverage(self) -> float:
        return sum(self.alpha)

    @property
    def joint_coverage(self) -> float:
        """The region's GUARANTEED joint coverage, by the union bound."""
        return 1.0 - self.total_noncoverage

    def index_of(self, key: str) -> int:
        if key not in self.primitives:
            raise NumericalFailure(f"{key!r} is not in the joint region")
        return self.primitives.index(key)

    def half_width(self, key: str) -> float:
        """``k_i sigma_i``: the region's half-extent along one primitive."""
        i = self.index_of(key)
        return self.coverage_factor[i] * self.sigma[i]

    def half_width_of_name(self, name: str) -> float:
        """Largest half-width over every key sharing a primitive NAME.

        Field- and block-scoped primitives appear once per record; a bound
        that must cover the packet takes the widest of them.
        """
        got = [
            self.coverage_factor[i] * self.sigma[i]
            for i, k in enumerate(self.primitives)
            if k == name or k.startswith(name + "@")
        ]
        if not got:
            raise NumericalFailure(f"no primitive named {name!r} in the region")
        return max(got)

    def bounded_systematic(self, category: str) -> float:
        for name, value in self.bounded_systematics:
            if name == category:
                return value
        raise NumericalFailure(
            f"no bounded systematic declared for {category!r}; absence is not "
            "a bound of zero"
        )

    def as_dict(self) -> dict:
        return {
            "version": self.version,
            "construction": (
                "intersection of individually calibrated marginal primitive "
                "regions with allocated noncoverage; valid for any dependence "
                "structure by the union bound"
            ),
            "primitive_count": len(self.primitives),
            "allocated_noncoverage": self.total_noncoverage,
            "guaranteed_joint_coverage": self.joint_coverage,
            "coverage_factor_min": min(self.coverage_factor),
            "coverage_factor_max": max(self.coverage_factor),
            "latent_basis": list(self.latent_basis),
            "bounded_systematics": {k: v for k, v in self.bounded_systematics},
            "categories": [
                {
                    "category": c.category,
                    "classification": c.classification.value,
                    "members": list(c.members),
                    "bound": c.bound,
                    "justification": c.justification,
                }
                for c in self.categories
            ],
            "identity": self.identity(),
        }

    def identity(self) -> str:
        """SHA-256 over the region's complete canonical construction record."""
        payload = json.dumps(
            {
                "version": self.version,
                "primitives": list(self.primitives),
                "sigma": list(self.sigma),
                "alpha": list(self.alpha),
                "coverage_factor": list(self.coverage_factor),
                "latent_basis": list(self.latent_basis),
                "loadings": [list(r) for r in self.loadings],
                "bounded_systematics": [list(b) for b in self.bounded_systematics],
                "categories": [
                    [c.category, c.classification.value, list(c.members),
                     c.bound, c.justification]
                    for c in self.categories
                ],
            },
            sort_keys=True, separators=(",", ":"),
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


#: Version of the joint-region construction rule itself.
JOINT_REGION_VERSION = 1


def build_joint_region(
    vector: PrimitiveVector,
    categories: Sequence[CategoryDeclaration],
    noncoverage: float = JOINT_REGION_NONCOVERAGE,
) -> JointCalibrationRegion:
    """Build the joint region and check the category declarations are complete.

    Every required category must be declared exactly once, every UNCERTAIN
    category's members must exist in the vector, and every stochastic
    primitive in the vector must belong to some UNCERTAIN category.  A
    primitive that no declaration claims would be carrying uncertainty that
    the packet never accounted for; a category with no declaration would be
    carrying zero uncertainty by default.  Both are refused.
    """
    defects: list[str] = []
    for c in categories:
        defects.extend(c.validate())
    declared = [c.category for c in categories]
    for required in REQUIRED_PRIMITIVE_CATEGORIES:
        n = declared.count(required)
        if n == 0:
            defects.append(f"{required}: not declared; absence is not zero uncertainty")
        elif n > 1:
            defects.append(f"{required}: declared {n} times")
    claimed: set[str] = set()
    for c in categories:
        if c.classification is not PrimitiveClass.UNCERTAIN:
            continue
        for name in c.members:
            hits = [p for p in vector.primitives if p.name == name]
            if not hits:
                defects.append(f"{c.category}: member {name!r} is not registered")
            claimed.add(name)
    for p in vector.primitives:
        if p.sigma > 0.0 and p.name not in claimed:
            defects.append(
                f"primitive {p.name!r} carries uncertainty but no category claims it"
            )
    if defects:
        raise NumericalFailure(
            "incomplete calibration primitive declaration:\n  " + "\n  ".join(defects)
        )

    keys = [p.key for p in vector.primitives]
    sig = [p.sigma for p in vector.primitives]
    n = len(keys)
    alpha_i = noncoverage / n
    k_i = nm.norm_ppf(1.0 - alpha_i / 2.0)
    lam = vector.loading_matrix()
    return JointCalibrationRegion(
        version=JOINT_REGION_VERSION,
        primitives=tuple(keys),
        sigma=tuple(sig),
        alpha=tuple(alpha_i for _ in range(n)),
        coverage_factor=tuple(k_i for _ in range(n)),
        latent_basis=tuple(vector.latents),
        loadings=tuple(tuple(row) for row in lam),
        bounded_systematics=tuple(
            (c.category, float(c.bound))
            for c in categories
            if c.classification is PrimitiveClass.BOUNDED_SYSTEMATIC
            and c.bound is not None
        ),
        categories=tuple(categories),
    )


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


def primitive_steps(
    phi: Sequence[float],
    phi_sigma: Sequence[float] | None,
    fraction: float,
    rel_step: float,
    abs_step: float,
) -> list[float]:
    """Step for each primitive, in that primitive's own units.

    Used only by the non-certified optimisation cross-check.  The declared
    standard uncertainty carries the primitive's units, so one dimensionless
    fraction serves every primitive; a single absolute step cannot, since 1e-3
    is a sensible log-stiffness step and a one-millimetre detector offset.
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


@dataclass(frozen=True)
class ProfiledSensitivity:
    """A NON-CERTIFIED profiled sensitivity, retained only as a cross-check.

    V4 produced this by central differences and attached a "certified"
    enclosure built from fine/coarse agreement plus a least-squares smoothness
    residual.  Independent audit rejected that, correctly: agreement between
    two finite-difference steps constrains the difference of their truncation
    remainders, not either remainder, and a fitted residual at sampled points
    bounds nothing between them.

    The finite-difference route is gone from the production path.  What
    remains here is the profiled-optimisation cross-check, whose radius comes
    from a genuine backward-error bound on the located maximum -- but which is
    still not a bound on truncation, so ``certified`` is False and no
    qualification may be taken from it.
    """

    jacobian: Matrix
    radius: Matrix
    phi_step: tuple[float, ...] = ()
    certified: bool = False
    method: str = "central differences of the profiled pseudo-true parameter"

    @property
    def log_beta_row(self) -> list[float]:
        return list(self.jacobian[LOG_BETA_ROW])

    @property
    def log_beta_radius(self) -> list[float]:
        return list(self.radius[LOG_BETA_ROW])


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
        jacobian=jac, radius=rad, phi_step=tuple(steps), certified=False,
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
    sensitivities: tuple["CertifiedSensitivity", ...] = ()

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

    @property
    def fully_certified(self) -> bool:
        """Every record's sensitivity carries a certified enclosure.

        Without this the three-way rule would be applied to an uncertified
        number, which is exactly what the V4 audit rejected.  A single
        uncertified row makes every qualification UNRESOLVED, which is
        fail-closed.
        """
        return bool(self.sensitivities) and all(
            s.certified for s in self.sensitivities
        )

    def absolute_qualification(self, key: str) -> str:
        if not self.fully_certified:
            return CEILING_UNRESOLVED
        return classify_with_enclosure(self.absolute_sigma(key), SIGMA_CAL_ABS_MAX)

    def contrast_qualification(self, key: str, reference: str) -> str:
        if not self.fully_certified:
            return CEILING_UNRESOLVED
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
    records: Sequence[tuple[str, FieldModelBuilder, GenericAnalysisBuilder]],
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
    sens: list[CertifiedSensitivity] = []
    for key, float_builder, generic_builder in records:
        # Fail-closed (V6 brief section 16).  If the transcendental enclosure,
        # the Riccati or tangent enclosure, the nonsingularity certificate or
        # the roundoff bound cannot be established, the record carries an
        # UNCERTIFIED sensitivity and every qualification taken from this
        # calibration becomes UNRESOLVED.  There is no heuristic fallback and
        # no partially certified result.
        try:
            ps = certified_profiled_sensitivity(
                generic_builder, float_builder, phi, phi_sigma=sigma,
            )
        except (SensitivityFailure, cert.CertificationFailure,
                NumericalFailure) as exc:
            ps = CertifiedSensitivity.uncertified(len(phi), f"{key}: {exc}")
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


# ---------------------------------------------------------------------------
# Certified U.20 sensitivity: interval hyper-dual, no finite differences
# ---------------------------------------------------------------------------

def _spd_from_chol_generic(p):
    """``L L^T`` from ``(log l11, l21, log l22)``, generically."""
    l11 = cert.gexp(p[0])
    l22 = cert.gexp(p[2])
    L = [[l11, 0.0], [p[1], l22]]
    return cert.gsym(cert.gmatmul(L, cert.gtranspose(L)))


def model_state_space_generic(theta: Sequence, am: AnalysisModel):
    """The analysis model at ``theta``, over float or interval hyper-dual.

    Identical algebra to :func:`model_state_space`; the only difference is
    that it runs on the generic kernel so a hyper-dual seed propagates through
    it.  ``dt`` and ``t_exp`` must stay plain floats: they index the shutter
    geometry, are compared against each other, and no calibration primitive in
    the declared model moves them.
    """
    b = theta[0]
    sigma = cert.gscale(cert.gspd_inverse(am.h_locked), cert.gexp(-b))
    d_mat = _spd_from_chol_generic(theta[3:6])
    om = theta[6]
    q_mat = [[0.0, -om], [om, 0.0]]
    a = cert.gmatmul(cert.gadd(d_mat, q_mat), cert.gspd_inverse(sigma))
    return cert.gbuild_state_space(
        a, sigma, [theta[1], theta[2]], am.p_matrix, am.r_obs,
        list(am.b_det), am.dt, am.t_exp,
    )


#: A generic analysis builder maps a (possibly hyper-dual) primitive vector to
#: an AnalysisModel whose matrices carry the same scalar type.
GenericAnalysisBuilder = Callable[[Sequence], AnalysisModel]


@dataclass(frozen=True)
class CertifiedSensitivity:
    """``d theta* / d phi`` with a rigorous enclosure of every component.

    The enclosure covers, with nothing estimated:

    ``truncation``
        exactly zero.  Hyper-dual arithmetic evaluates the chain rule; there
        is no step size and therefore no remainder term.

    ``floating point``
        interval arithmetic with outward rounding after every operation, so
        the reported interval encloses the exact real result of the algorithm.

    ``Riccati fixed point``
        the one-step residual at the stopping point, divided by
        ``1 - ||F_cl||^2``, the contraction factor of the Riccati map.

    ``linear solve``
        residual of the computed solution enclosed in interval arithmetic --
        every product and every accumulation outward rounded, with the matrix
        entries entering as the intervals they are -- amplified by a lower
        bound on the smallest eigenvalue of the symmetric expected
        information that an interval Cholesky of the shifted matrix PROVES
        rather than estimates.

    Every one of these is folded into :attr:`radius`.  A failure to establish
    any of them sets :attr:`certified` to False, which makes the 0.009 / 0.003
    qualification UNRESOLVED; there is no fallback.
    """

    jacobian: Matrix
    radius: Matrix
    #: Symmetric expected-information matrix and its certified inverse norm.
    information: Matrix
    information_inverse_norm: float
    information_min_eigenvalue: float
    #: Largest Riccati fixed-point bound over every evaluation, relative to
    #: the latent covariance scale: the VALUE component ``P - P*``.
    riccati_bound: float
    #: Largest bound on the Riccati TANGENT fixed points -- ``dP/dtheta``,
    #: ``dP/dphi`` and the mixed second derivative -- over every evaluation,
    #: relative to the same scale.  V5 bounded only the value.
    riccati_derivative_bound: float
    #: Largest bound on the truncated discrete Lyapunov tail, same scale.
    lyapunov_bound: float
    #: Largest enclosure half-width over the second-derivative blocks,
    #: relative to the largest entry of those blocks.
    worst_second_derivative_radius: float
    linear_solve_residual: float
    #: Columns of ``phi`` the analysis model provably does not read, so their
    #: sensitivity is exactly zero.  U permits a zero row only when the zero
    #: is demonstrated; this is the demonstration, and the suite re-derives it
    #: numerically.
    structural_zeros: tuple[int, ...] = ()
    certified: bool = True
    #: Why certification failed, when it did.  Empty on the certified path.
    failure: str = ""
    method: str = (
        "interval-arithmetic hyper-dual differentiation of the expected-score "
        "system; no finite differences"
    )

    @staticmethod
    def uncertified(p: int, reason: str) -> "CertifiedSensitivity":
        """A sensitivity that could NOT be certified.

        The Jacobian is zero and every radius infinite, so any qualification
        taken from it is UNRESOLVED and no interval built from it can be
        narrow enough to support anything.  That is the required outcome:
        ``UNRESOLVED_AT_NUMERICAL_PRECISION`` is preferable to a false PASS.
        """
        inf = float("inf")
        return CertifiedSensitivity(
            jacobian=[[0.0] * p for _ in range(N_THETA)],
            radius=[[inf] * p for _ in range(N_THETA)],
            information=[[0.0] * N_THETA for _ in range(N_THETA)],
            information_inverse_norm=inf,
            information_min_eigenvalue=0.0,
            riccati_bound=inf,
            riccati_derivative_bound=inf,
            lyapunov_bound=inf,
            worst_second_derivative_radius=inf,
            linear_solve_residual=inf,
            certified=False,
            failure=reason,
        )

    @property
    def log_beta_row(self) -> list[float]:
        return list(self.jacobian[LOG_BETA_ROW])

    @property
    def log_beta_radius(self) -> list[float]:
        return list(self.radius[LOG_BETA_ROW])


def _second_partial(
    builder: GenericAnalysisBuilder,
    truth,
    theta0: Sequence[float],
    scaling: "ThetaScaling",
    phi: Sequence[float],
    i_theta: int,
    j_theta: int | None,
    k_phi: int | None,
    phi_scale: Sequence[float],
):
    """One exact mixed second partial of ``L``, with its enclosure.

    ``e1`` is seeded on a dimensionless theta coordinate; ``e2`` on either a
    second theta coordinate or a scaled primitive coordinate.
    """
    theta = []
    for n in range(N_THETA):
        s1 = scaling.scale[n] if n == i_theta else 0.0
        s2 = scaling.scale[n] if (j_theta is not None and n == j_theta) else 0.0
        if s1 == 0.0 and s2 == 0.0:
            theta.append(float(theta0[n]))
        else:
            theta.append(cert.IHD.seed(float(theta0[n]), s1, s2))
    if k_phi is None:
        phi_g = [float(v) for v in phi]
    else:
        phi_g = [
            cert.IHD.seed(float(v), 0.0, phi_scale[n] if n == k_phi else 0.0)
            for n, v in enumerate(phi)
        ]
    am = builder(phi_g)
    model = model_state_space_generic(theta, am)
    res = cert.gexpected_loglik(truth, model)
    return res


def _seeded(x) -> bool:
    """True when ``x`` carries a nonzero second-direction infinitesimal."""
    return isinstance(x, cert.IHD) and (x.d2[0] != 0.0 or x.d2[1] != 0.0)


def _primitive_enters(
    builder: GenericAnalysisBuilder, phi: Sequence[float], k: int,
    phi_scale: Sequence[float],
) -> bool:
    """Does primitive ``k`` reach the analysis model at all?

    Builds the model with a seed on that primitive alone and asks whether the
    seed survives into any object the likelihood reads.  ``H_A``, ``P``,
    ``R_obs``, ``b_det``, ``dt`` and ``t_exp`` are the complete set; the
    analysis uses nothing else from ``phi``.
    """
    phi_g = [
        cert.IHD.seed(float(v), 0.0, phi_scale[n] if n == k else 0.0)
        for n, v in enumerate(phi)
    ]
    am = builder(phi_g)
    for m in (am.h_locked, am.p_matrix, am.r_obs):
        for row in m:
            for x in row:
                if _seeded(x):
                    return True
    for x in tuple(am.b_det) + (am.dt, am.t_exp):
        if _seeded(x):
            return True
    return False


def certified_profiled_sensitivity(
    builder: GenericAnalysisBuilder,
    float_builder: FieldModelBuilder,
    phi: Sequence[float],
    phi_sigma: Sequence[float] | None = None,
) -> CertifiedSensitivity:
    """The U.20 production derivative, certified.

    Solves the expected-score system ``F(theta, phi) = 0`` by implicit
    differentiation::

        d theta* / d phi = - F_theta^{-1} F_phi
        F_theta = d^2 L / d theta d theta
        F_phi   = d^2 L / d theta d phi

    Both blocks are exact second derivatives of the expected T.6 log
    likelihood, obtained by hyper-dual arithmetic rather than by differencing.
    The log-beta row is extracted only after the full nuisance system is
    solved.
    """
    phi = [float(v) for v in phi]
    base = float_builder(phi)
    truth_ss = base.truth_state_space()
    truth = cert.gbuild_state_space(
        base.a_drift, base.sigma, [0.0, 0.0], base.p_matrix, base.r_obs,
        list(base.b_det), base.dt, base.t_exp,
    )
    theta0 = truth_matching_theta(base)
    sc = ThetaScaling.for_model(base, theta0)
    p = len(phi)
    phi_scale = [
        float(phi_sigma[k]) if phi_sigma is not None and phi_sigma[k] > 0.0
        else (abs(phi[k]) if phi[k] != 0.0 else 1.0)
        for k in range(p)
    ]

    sigma_scale = nm.max_abs(base.sigma)
    riccati_bound = 0.0
    riccati_derivative_bound = 0.0
    lyapunov_bound = 0.0
    worst_rel = 0.0
    block_scale = 0.0

    def mixed(i, j=None, k=None):
        nonlocal riccati_bound, worst_rel
        nonlocal riccati_derivative_bound, lyapunov_bound
        res = _second_partial(builder, truth, theta0, sc, phi, i, j, k, phi_scale)
        val = res.value
        riccati_bound = max(riccati_bound, res.riccati_fixed_point_bound / sigma_scale)
        riccati_derivative_bound = max(
            riccati_derivative_bound,
            max(res.riccati_derivative_bound, res.riccati_mixed_bound) / sigma_scale,
        )
        lyapunov_bound = max(lyapunov_bound, res.lyapunov_bound / sigma_scale)
        lo, hi = val.d12
        mid = 0.5 * (lo + hi)
        rad = 0.5 * (hi - lo)
        # Width relative to the BLOCK's scale, not the entry's own value: a
        # structurally zero entry has no meaningful relative width.
        worst_rel = max(worst_rel, rad)
        return mid, rad

    # Symmetric expected information in dimensionless theta coordinates.
    info = nm.zeros(N_THETA, N_THETA)
    info_rad = nm.zeros(N_THETA, N_THETA)
    for i in range(N_THETA):
        for j in range(i, N_THETA):
            m, r = mixed(i, j=j)
            info[i][j] = info[j][i] = m
            info_rad[i][j] = info_rad[j][i] = r

    cross = nm.zeros(N_THETA, p)
    cross_rad = nm.zeros(N_THETA, p)
    structural_zeros: list[int] = []
    for k in range(p):
        if not _primitive_enters(builder, phi, k, phi_scale):
            # A variable the analysis model does not read cannot change what
            # the analysis model computes, so this column is EXACTLY zero with
            # zero radius.  That is a proof, not a shortcut: the seeded
            # infinitesimal is absent from every matrix the likelihood is
            # built from.  It is recorded so the zero is inspectable, and the
            # deterministic suite also evaluates these columns numerically and
            # confirms they come back zero.
            structural_zeros.append(k)
            continue
        for i in range(N_THETA):
            m, r = mixed(i, k=k)
            cross[i][k] = m
            cross_rad[i][k] = r
    block_scale = max(nm.max_abs(info), nm.max_abs(cross), 1e-300)
    worst_rel = worst_rel / block_scale

    inv_norm, lam_min = certified_inverse_norm(info, info_rad)

    try:
        jz = nm.scale(nm.lu_solve(info, cross), -1.0)
    except NumericalFailure as exc:
        raise SensitivityFailure(f"expected-information solve failed: {exc}") from exc

    # Residual of the computed solution, per column, in INTERVAL arithmetic.
    # V5 accumulated it in ordinary floating point and then called the result
    # certified; the audit was right that an unbounded accumulation cannot
    # underwrite a bound on itself.  Here every product and every addition is
    # outward rounded, and the matrix entries enter as the intervals they
    # actually are, so the returned number encloses the exact residual of the
    # computed solution against the exact interval system.  Per column, not
    # globally: a single residual would charge every column the worst one.
    resid_by_col: list[float] = []
    for k in range(p):
        worst = 0.0
        for i in range(N_THETA):
            acc = cert._out(cross[i][k] - cross_rad[i][k],
                            cross[i][k] + cross_rad[i][k])
            for t in range(N_THETA):
                acc = cert.iadd(acc, cert.imul(
                    cert._out(info[i][t] - info_rad[i][t],
                              info[i][t] + info_rad[i][t]),
                    cert.iv(jz[t][k]),
                ))
            worst = max(worst, cert.imag(acc))
        resid_by_col.append(worst)
    resid = max(resid_by_col)

    jac = nm.zeros(N_THETA, p)
    rad = nm.zeros(N_THETA, p)
    for i in range(N_THETA):
        for k in range(p):
            scale = sc.scale[i] / phi_scale[k]
            jac[i][k] = scale * jz[i][k]
            # The two roundings in forming this entry from the solved
            # dimensionless one are widened by two ulps each, so the reported
            # radius also covers the rescaling itself.
            r = scale * inv_norm * resid_by_col[k]
            rad[i][k] = r + 4.0 * cert.EPS * abs(jac[i][k])
    return CertifiedSensitivity(
        jacobian=jac,
        radius=rad,
        information=info,
        information_inverse_norm=inv_norm,
        information_min_eigenvalue=lam_min,
        riccati_bound=riccati_bound,
        riccati_derivative_bound=riccati_derivative_bound,
        lyapunov_bound=lyapunov_bound,
        worst_second_derivative_radius=worst_rel,
        linear_solve_residual=resid,
        structural_zeros=tuple(structural_zeros),
    )


def certified_inverse_norm(info: Matrix, info_rad: Matrix) -> tuple[float, float]:
    """``(||A^{-1}||_2 bound, certified lambda_min)`` for a symmetric interval matrix.

    V5 bounded this by Weyl plus the eigensolver's reconstruction residual.
    Two things were wrong with that: the residual was returned RELATIVE to the
    matrix scale and then subtracted as if it were absolute, and the
    reconstruction was computed in ordinary floating point with no account of
    the eigenvector matrix's own loss of orthogonality.

    The replacement needs no eigensolver.  ``lambda_min(S) >= mu`` is
    equivalent to ``S - mu I`` being positive definite, and an interval
    Cholesky that completes with every pivot's LOWER endpoint positive proves
    positive definiteness for **every** member of the interval matrix: the
    interval intermediates enclose each member's own Cholesky quantities, so
    each member's pivots are at least those positive lower bounds.  The
    float eigenvalues are used only to propose candidate shifts; nothing in
    the certificate depends on their accuracy.
    """
    n = len(info)
    vals, _ = nm.eigh(nm.symmetrise(info))
    if min(vals) > 0.0:
        sgn = 1.0
    elif max(vals) < 0.0:
        sgn = -1.0
    else:
        raise SensitivityFailure(
            "the expected information is indefinite at the linearisation "
            f"point; eigenvalues {['%.3e' % v for v in vals]}"
        )
    lam0 = min(abs(v) for v in vals)
    for frac in (0.98, 0.9, 0.75, 0.5, 0.25, 0.1, 0.01):
        mu = frac * lam0
        if mu <= 0.0:
            break
        shifted = [
            [
                cert.IHD(cert._out(
                    sgn * info[i][j] - info_rad[i][j] - (mu if i == j else 0.0),
                    sgn * info[i][j] + info_rad[i][j] - (mu if i == j else 0.0),
                ))
                for j in range(n)
            ]
            for i in range(n)
        ]
        try:
            cert.gcholesky(shifted)
        except cert.CertificationFailure:
            continue
        return 1.0 / mu, mu
    raise SensitivityFailure(
        "the expected information is not certifiably nonsingular: no shift "
        f"below |lambda|_min {lam0:.3e} passes an interval Cholesky with the "
        "declared second-derivative enclosure"
    )
