"""Axial (3D-to-lateral) Schur reduction and its covariance: Layer C.

Implements the repaired U-stage construction (sections 5.3-5.8).  The official
physical lateral matrix is always the Schur complement

    K_eff = K_qq - K_qz K_zz^{-1} K_zq,            H_eff = K_eff / (k_B T)

and never the plane block ``K_qq``.  Substituting ``K_qq`` is a named defect
whose exact scale and shape impact are reported by :func:`plane_block_bias`.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import ClassVar
from typing import Sequence

from . import numerics as nm
from .numerics import Matrix, NumericalFailure
from .refusals import (
    AXIAL_REDUCTION_UNQUALIFIED,
    INSUFFICIENT_GEOMETRY_CALIBRATION,
    MISSING_COVARIANCE,
    NUMERICAL_REPRESENTATION_FAILURE,
    Refusal,
    refuse,
)
from .units import K_B

#: Domain guard on the DIMENSIONLESS normalised remainder.
#:
#: This is not a tolerance and not a budget.  ``E_K`` with operator norm >= 1
#: means ``K_eff + Delta K`` need not remain positive definite, so the
#: linearisation whose remainder is being bounded has no meaning at all; the
#: reduction is outside its own domain of definition.  The V3 constant 1e-3
#: was applied to a DIMENSIONAL quantity in N/m and is removed as a release
#: predicate: see :func:`remainder_impacts`, which routes the certified
#: remainder into the already-cleared log-beta bias, cross-field bias,
#: geometry and centre budgets instead of giving it an allowance of its own.
REMAINDER_DOMAIN_LIMIT = 1.0

#: Relative numerical-skew ceiling used as a SUPPORTING diagnostic only.  The
#: scientific conservativity pass comes from U's own qualification evidence;
#: this metric exists so a numerically asymmetric matrix cannot slip through
#: on a dimensional absolute tolerance.
SKEW_RTOL = 1.0e-9


@dataclass(frozen=True)
class AxialEvidence:
    """Explicit U-required evidence for one axial reduction.

    Every field is ``None`` by default, meaning NO EVIDENCE SUPPLIED.  Missing
    evidence fails closed: it is never read as qualified.  This reverses the
    previous boolean-default-True behaviour, under which a packet with no
    conservativity, support, temporal or covariance evidence qualified.
    """

    #: U section 12: curl/conservativity qualification of the 3D response.
    conservativity_qualified: bool | None = None
    #: U section 5.6: 3D harmonic / model-domain qualification.
    harmonic_domain_qualified: bool | None = None
    #: U section 5.6: product-support and tail bounds.
    support_qualified: bool | None = None
    #: U section 5.7: the retained 2D lateral temporal reduction.
    temporal_reduction_qualified: bool | None = None
    #: U section 19: lateral observation / defocus transfer.
    observation_transfer_qualified: bool | None = None
    #: U section 5.4: the CERTIFIED SET of admissible normalised remainders.
    #: Qualification is a supremum over this whole set.  A single evaluated
    #: witness does not qualify it (V-stage V5 brief section 21).
    remainder_set: "RemainderSet | None" = None
    #: Optional typed residual witness, in N/m.  Illustration only: it names
    #: one member of the set and never stands in for the set.
    nonlinear_remainder: "NonlinearRemainder | None" = None
    #: U sections 26-27: projected absolute and contrast uncertainty budgets.
    uncertainty_budget_qualified: bool | None = None
    #: T.29: geometry and centre qualification availability.
    geometry_centre_qualified: bool | None = None
    #: Complete provenance chain for every primitive entering the reduction.
    provenance_complete: bool | None = None

    #: Names of every load-bearing field, in refusal-report order.
    REQUIRED: ClassVar[tuple[str, ...]] = (
        "conservativity_qualified",
        "harmonic_domain_qualified",
        "support_qualified",
        "temporal_reduction_qualified",
        "observation_transfer_qualified",
        "uncertainty_budget_qualified",
        "geometry_centre_qualified",
        "provenance_complete",
    )

    def missing(self) -> list[str]:
        """Fields with no evidence supplied at all."""
        return [n for n in self.REQUIRED if getattr(self, n) is None]

    def failed(self) -> list[str]:
        """Fields with evidence that explicitly does not qualify."""
        return [n for n in self.REQUIRED if getattr(self, n) is False]

    @staticmethod
    def fully_qualified(
        remainder_set: "RemainderSet | None" = None,
        nonlinear_remainder: "NonlinearRemainder | None" = None,
        *,
        temporal_qualified: bool = True,
    ) -> "AxialEvidence":
        """Complete passing evidence, for synthetic fixtures only.

        ``temporal_qualified`` is keyword-only and has no literal default on
        any production path: every caller in the package derives it, either
        from the construction-time semigroup residual of the world being built
        or, per replicate, from the measured response.  V5 had this item set
        to a literal True in every design builder and to a literal False in
        one deterministic control, and nothing anywhere derived it.
        """
        return AxialEvidence(
            conservativity_qualified=True,
            harmonic_domain_qualified=True,
            support_qualified=True,
            temporal_reduction_qualified=bool(temporal_qualified),
            observation_transfer_qualified=True,
            remainder_set=(
                RemainderSet(0.0, "synthetic fixture: certified zero remainder")
                if remainder_set is None else remainder_set
            ),
            nonlinear_remainder=nonlinear_remainder,
            uncertainty_budget_qualified=True,
            geometry_centre_qualified=True,
            provenance_complete=True,
        )


@dataclass(frozen=True)
class SchurReduction:
    """Result of the 3D-to-lateral reduction."""

    k_eff: Matrix
    h_eff: Matrix
    #: Diagnostic omitted correction ``Delta K_axial = -b kappa^{-1} b^T``.
    delta_k_axial: Matrix
    #: ``r = b^T A^{-1} b / kappa`` in ``[0, 1)``.
    r: float
    #: Covariance of ``vech(K_eff)`` in order (S11, S12, S22), if propagated.
    c_vech_s: Matrix | None = None
    #: Covariance of ``vech(H_eff)``, including the ``-H dT/T`` term.
    c_vech_h: Matrix | None = None
    #: Exact finite effects of the certified remainder SET, routed into the
    #: existing budgets.  ``None`` means never established, which fails
    #: closed downstream.
    remainder_impacts: "FiniteRemainderEffects | None" = None
    refusals: tuple[Refusal, ...] = ()

    @property
    def ok(self) -> bool:
        return not self.refusals


def split_3d(k3: Matrix) -> tuple[Matrix, Matrix, float]:
    """Split a 3-by-3 stiffness into ``(A = K_qq, b = K_qz, kappa = K_zz)``."""
    a = [[k3[0][0], k3[0][1]], [k3[1][0], k3[1][1]]]
    b = [[k3[0][2]], [k3[1][2]]]
    kappa = k3[2][2]
    return a, b, kappa


def relative_skew(k3: Matrix) -> float:
    """Dimensionless numerical skew ``||K - K^T|| / ||(K + K^T)/2||``.

    Scale invariant by construction, so a stiffness of order ``1e-4 N/m`` is
    never compared against a tolerance implicitly anchored at ``1 N/m``.
    Raises if the symmetric physical scale is zero: that case is refused, not
    rescued by substituting a unit denominator.
    """
    sym = nm.symmetrise(k3)
    denom = nm.max_abs(sym)
    if denom <= 0.0 or not math.isfinite(denom):
        raise NumericalFailure(
            "relative skew is undefined: the symmetric physical scale is zero "
            "or unqualified"
        )
    return nm.asymmetry(k3) / denom


def validate_3d_stiffness(
    k3: Matrix | None,
    evidence: AxialEvidence,
    skew_rtol: float = SKEW_RTOL,
) -> tuple[Refusal, ...]:
    """Validate the full 3D stiffness packet (V-stage brief section 12).

    Conservativity must be qualified by U evidence; the scale-invariant skew
    metric is a supporting numerical check, not a substitute scientific
    tolerance.
    """
    if k3 is None:
        return (
            refuse(
                AXIAL_REDUCTION_UNQUALIFIED,
                "K3 present",
                "full 3D stiffness block is absent; no plane-only fallback exists",
            ),
        )
    if nm.shape(k3) != (3, 3):
        return (
            refuse(
                AXIAL_REDUCTION_UNQUALIFIED,
                "K3 is 3-by-3",
                "full 3D stiffness must be 3-by-3",
                shape=list(nm.shape(k3)),
            ),
        )
    if not nm.is_finite_matrix(k3):
        return (
            refuse(
                NUMERICAL_REPRESENTATION_FAILURE,
                "K3 entries finite",
                "full 3D stiffness contains a non-finite entry",
            ),
        )
    if evidence.conservativity_qualified is None:
        return (
            refuse(
                AXIAL_REDUCTION_UNQUALIFIED,
                "conservativity evidence supplied",
                "no curl/conservativity evidence; missing evidence fails closed",
            ),
        )
    if not evidence.conservativity_qualified:
        return (
            refuse(
                AXIAL_REDUCTION_UNQUALIFIED,
                "conservativity qualified",
                "symmetry may be imposed only after curl/conservativity qualification",
            ),
        )
    try:
        skew = relative_skew(k3)
    except NumericalFailure as exc:
        return (
            refuse(
                AXIAL_REDUCTION_UNQUALIFIED,
                "symmetric physical scale qualified positive",
                str(exc),
            ),
        )
    if skew > skew_rtol:
        return (
            refuse(
                AXIAL_REDUCTION_UNQUALIFIED,
                "K3 numerically symmetric after conservativity qualification",
                "relative stiffness skew exceeds the scale-invariant ceiling",
                relative_skew=skew,
                ceiling=skew_rtol,
            ),
        )
    ks = nm.symmetrise(k3)
    kappa = ks[2][2]
    if not math.isfinite(kappa) or kappa <= 0.0:
        return (
            refuse(
                AXIAL_REDUCTION_UNQUALIFIED,
                "kappa > 0",
                "axial stiffness K_zz is not strictly positive",
                kappa=kappa,
            ),
        )
    try:
        nm.cholesky(ks)
    except NumericalFailure as exc:
        return (
            refuse(
                AXIAL_REDUCTION_UNQUALIFIED,
                "K3 SPD",
                f"full 3D stiffness is not positive definite: {exc}",
            ),
        )
    return ()


def schur_complement(k3: Matrix) -> Matrix:
    """``K_eff = A - b kappa^{-1} b^T`` using a stable solve, no explicit inverse."""
    a, b, kappa = split_3d(nm.symmetrise(k3))
    if kappa <= 0.0 or not math.isfinite(kappa):
        raise NumericalFailure(f"axial stiffness kappa must be positive, got {kappa!r}")
    # Solve kappa * w = b^T  (scalar axial block: a single division, no inverse matrix).
    w = [b[0][0] / kappa, b[1][0] / kappa]
    corr = [[b[0][0] * w[0], b[0][0] * w[1]], [b[1][0] * w[0], b[1][0] * w[1]]]
    return nm.symmetrise(nm.sub(a, corr))


def axial_ratio(k3: Matrix) -> float:
    """``r = b^T A^{-1} b / kappa``, the omitted-correction strength."""
    a, b, kappa = split_3d(nm.symmetrise(k3))
    bb = [b[0][0], b[1][0]]
    quad = nm.spd_quadform(a, bb)
    return quad / kappa


def plane_block_bias(r: float) -> tuple[float, float]:
    """Return ``(log beta_plane, G_plane)`` for the omitted axial correction.

    From U-stage (U.A13)::

        beta_plane = 2(1-r)/(2-r),  |log beta_plane| = log[(2-r)/(2(1-r))],
        G_plane    = -(1/2) log(1-r)

    These quantify what substituting ``K_qq`` for ``K_eff`` would do.  They are
    diagnostics of the omitted correction, never a permitted axial tolerance.
    """
    if not (0.0 <= r < 1.0):
        raise NumericalFailure(f"axial ratio must lie in [0, 1), got {r!r}")
    beta_plane = 2.0 * (1.0 - r) / (2.0 - r)
    return math.log(beta_plane), -0.5 * math.log1p(-r)


def schur_jacobian(b: Sequence[float], kappa: float) -> Matrix:
    """Jacobian (U.A10) of ``(S11, S12, S22)`` w.r.t. ``(A11, A12, A22, b1, b2, kappa)``."""
    b1, b2 = float(b[0]), float(b[1])
    k = float(kappa)
    return [
        [1.0, 0.0, 0.0, -2.0 * b1 / k, 0.0, b1 * b1 / (k * k)],
        [0.0, 1.0, 0.0, -b2 / k, -b1 / k, b1 * b2 / (k * k)],
        [0.0, 0.0, 1.0, 0.0, -2.0 * b2 / k, b2 * b2 / (k * k)],
    ]


class RemainderKind(str, Enum):
    """What a stored axial remainder physically is.

    V3 stored a bare float and compared it against a number documented as
    relative.  The quantity is a STIFFNESS residual in N/m, so that comparison
    was dimensionally invalid: it passed or failed purely on the SI magnitude
    of the stiffness, and at 1e-4 N/m every physically possible remainder
    passed by nineteen orders of magnitude.
    """

    #: Second-order residual of the Schur complement, in N/m.
    STIFFNESS_RESIDUAL = "stiffness_residual_N_per_m"
    #: Already normalised by K_eff; dimensionless.
    NORMALISED = "dimensionless_normalised_residual"


@dataclass(frozen=True)
class NonlinearRemainder:
    """A certified bound on the second-order Schur remainder, with its units.

    ``matrix`` is the symmetric 2-by-2 residual in the units declared by
    ``kind``.  A raw unlabelled float is no longer accepted anywhere.
    """

    matrix: Matrix
    kind: RemainderKind = RemainderKind.STIFFNESS_RESIDUAL
    unit: str = "N/m"
    source: str = ""

    def __post_init__(self) -> None:
        if nm.shape(self.matrix) != (2, 2):
            raise NumericalFailure("axial remainder must be a 2-by-2 residual matrix")
        if self.kind is RemainderKind.NORMALISED and self.unit not in ("", "1"):
            raise NumericalFailure("a normalised remainder is dimensionless")
        if self.kind is RemainderKind.STIFFNESS_RESIDUAL and self.unit != "N/m":
            raise NumericalFailure("a stiffness residual must be declared in N/m")

    @staticmethod
    def stiffness(vech: Sequence[float], source: str = "") -> "NonlinearRemainder":
        """From ``(Delta11, Delta12, Delta22)`` in N/m."""
        d11, d12, d22 = (float(v) for v in vech)
        return NonlinearRemainder([[d11, d12], [d12, d22]], source=source)

    @staticmethod
    def zero(source: str = "certified zero") -> "NonlinearRemainder":
        return NonlinearRemainder([[0.0, 0.0], [0.0, 0.0]], source=source)

    @property
    def finite(self) -> bool:
        return nm.is_finite_matrix(self.matrix)


def normalise_remainder(remainder: NonlinearRemainder, k_eff: Matrix) -> Matrix:
    """``E_K = K_eff^{-1/2} Delta K K_eff^{-1/2}`` (U-stage 5.4, 5.8).

    This is the U-consistent dimensionless relative operator.  Because
    ``H_eff = K_eff / (k_B T)`` and ``Delta H = Delta K / (k_B T)`` share the
    same scalar, ``E_K`` is identically the normalised thermal-Hessian
    residual ``H_eff^{-1/2} Delta H H_eff^{-1/2}``; the normalisation is the
    same object in either coordinate, which is why no separate thermal form
    is carried.

    Its spectrum is the set of generalised eigenvalues of
    ``(Delta K, K_eff)``, so it is invariant under any congruence
    ``K -> M K M^T``, ``Delta K -> M Delta K M^T``: a coordinate change or an
    overall rescaling of the stiffness cannot change the classification.
    """
    if remainder.kind is RemainderKind.NORMALISED:
        return nm.symmetrise(remainder.matrix)
    if not remainder.finite:
        raise NumericalFailure("axial remainder contains a non-finite entry")
    w = nm.inv_sqrtm_spd(nm.symmetrise(k_eff))
    return nm.symmetrise(nm.matmul(nm.matmul(w, nm.symmetrise(remainder.matrix)), w))


@dataclass(frozen=True)
class RemainderSet:
    """The certified set of admissible normalised remainders.

    Declared as a spectral ball ``E in {E = E^T : ||E||_op <= rho}``.  Every
    downstream effect is qualified by its **supremum over this whole set**, not
    by evaluating one convenient member: V4's ``axial_remainder_bias`` used a
    single proportional 5 percent perturbation whose trace nearly cancelled,
    which qualifies nothing.
    """

    rho: float
    source: str = ""

    def __post_init__(self) -> None:
        if not math.isfinite(self.rho) or self.rho < 0.0:
            raise NumericalFailure("remainder set radius must be finite and nonnegative")

    @property
    def within_domain(self) -> bool:
        """``I + E`` is positive definite for every member of the set."""
        return self.rho < REMAINDER_DOMAIN_LIMIT


@dataclass(frozen=True)
class FiniteRemainderEffects:
    """EXACT finite effects of a remainder, never first-order surrogates.

    V4 reported ``|tr E| / d`` and ``||E - (tr E / d) I||_op``.  Both are the
    leading terms of the exact effects, and the audit's counterexamples show
    the difference is decisive at the budget boundary: at ``E = -0.0004999 I``
    the first-order scale effect is 0.0004999 and passes the 0.0005 budget,
    while the exact effect is 0.00050002499 and fails it.

    Every field below is a supremum over the whole declared remainder set.
    """

    rho: float
    #: sup |b*| over the set, from the exact population pseudo-true relation.
    log_beta_bias: float
    #: This record's contribution to a within-block contrast bias.
    contrast_bias: float
    #: sup of the exact T4 geometry statistic induced by the set.
    geometry: float
    #: sup multiplicative factor on the centre statistic m.
    centre_factor: float
    #: sup multiplicative factor on every relaxation rate, hence on the
    #: exposure fraction, the bandwidth product and the localisation ratio.
    rate_factor: float
    within_domain: bool

    def as_dict(self) -> dict:
        return {
            "remainder_set_radius": self.rho,
            "log_beta_bias": self.log_beta_bias,
            "contrast_bias": self.contrast_bias,
            "geometry": self.geometry,
            "centre_factor": self.centre_factor,
            "rate_factor": self.rate_factor,
            "within_domain": self.within_domain,
            "basis": "exact finite effects, supremum over the declared set",
        }


def exact_log_beta_bias(e_k: Matrix) -> float:
    """EXACT population log-beta shift induced by one normalised remainder.

    The locked analysis fixes the shape of the latent covariance to
    ``H_A^{-1}`` and fits only the scale, so the pseudo-true ``b`` maximises

        E[l] = -1/2 ( -d b + log det M + e^b tr(M^{-1} Sigma_true) + ... )

    with ``M = H_A^{-1}``.  Setting the derivative to zero gives

        b* = log d - log tr(H_A Sigma_true) .

    With ``H_A = K_eff/(k_B T)``, ``Sigma_true = k_B T K_true^{-1}`` and
    ``K_true = K_eff^{1/2}(I + E) K_eff^{1/2}``, cyclicity collapses the trace:

        tr(H_A Sigma_true) = tr(K_eff K_true^{-1}) = tr((I + E)^{-1}) ,

    so the exact finite effect is

        b* = log d - log tr((I + E)^{-1}) .

    The orientation is the experimental one: ``K_eff`` is what Branch A
    reports and locks, ``K_true`` is the physical field, and ``E`` is the
    certified residual by which the reported Schur complement misses it.
    First order this is ``tr(E)/d``, which is what V4 used.
    """
    d = len(e_k)
    vals, _ = nm.eigh(nm.symmetrise(e_k))
    if min(vals) <= -1.0:
        raise NumericalFailure("I + E is not positive definite; the effect is undefined")
    tr_inv = sum(1.0 / (1.0 + v) for v in vals)
    return math.log(d) - math.log(tr_inv)


def exact_geometry_effect(e_k: Matrix) -> float:
    """EXACT T4 geometry statistic induced by one normalised remainder.

    T4 evaluates ``G = ||log M - (log det M / d) I||_op`` with ``M`` similar to
    ``H_A Sigma_B``.  Under the remainder, ``H_A Sigma_true = K_eff K_true^{-1}``
    is similar to ``(I + E)^{-1}``, whose logarithm has eigenvalues
    ``-log(1 + lambda_i(E))``.  The deviatoric part therefore has

        G = max_i | log(1 + lambda_i) - mean_j log(1 + lambda_j) | .

    This is the actual downstream T4 object, evaluated through the matrix
    logarithm, not the first-order surrogate ``||E - (tr E/d) I||_op``.
    """
    d = len(e_k)
    vals, _ = nm.eigh(nm.symmetrise(e_k))
    if min(vals) <= -1.0:
        raise NumericalFailure("I + E is not positive definite; the effect is undefined")
    g = [math.log(1.0 + v) for v in vals]
    mean = sum(g) / d
    return max(abs(x - mean) for x in g)


def remainder_set_effects(rs: RemainderSet, d: int = 2) -> FiniteRemainderEffects:
    """Exact suprema of every downstream effect over the whole declared set.

    Each supremum is in closed form, so the qualification covers the entire
    admissible set rather than one evaluated witness.

    ``log beta``
        ``b*(E) = log d - log sum_i 1/(1+lambda_i)`` is strictly increasing in
        every ``lambda_i``, so over ``lambda_i in [-rho, rho]`` its range is
        ``[log(1-rho), log(1+rho)]`` and ``sup |b*| = -log(1-rho)``.

    ``geometry``
        ``G = max_i |g_i - mean g|`` with ``g_i = log(1+lambda_i)`` monotone in
        ``lambda_i``.  Over the box the spread is maximised with one
        eigenvalue at ``+rho`` and the rest at ``-rho``, giving
        ``(d-1)/d * log((1+rho)/(1-rho))``; for ``d = 2`` that is
        ``artanh(rho)``.

    ``centre``
        ``m = sqrt(delta^T H_A delta)``.  The remainder perturbs ``H_A`` but
        does NOT translate the trap, so ``delta`` is unchanged and the only
        effect is the multiplicative factor ``sqrt(1 + lambda)``, bounded by
        ``sqrt(1 + rho)``.  A first-order additive enlargement, as V4 applied,
        misrepresents a purely multiplicative effect.

    ``rates``
        ``A = K/gamma``, so every relaxation rate carries a factor
        ``1 + lambda``, bounded by ``1 + rho``.  That propagates to the
        exposure fraction ``t_exp/tau_fast``, the bandwidth product
        ``||B|| dt`` and the localisation ratio, each of which has its own
        declared ceiling.
    """
    rho = rs.rho
    if not rs.within_domain:
        return FiniteRemainderEffects(
            rho, float("inf"), float("inf"), float("inf"),
            float("inf"), float("inf"), False,
        )
    scale = -math.log1p(-rho)
    geometry = (d - 1) / d * (math.log1p(rho) - math.log1p(-rho))
    return FiniteRemainderEffects(
        rho=rho,
        log_beta_bias=scale,
        contrast_bias=scale,
        geometry=geometry,
        centre_factor=math.sqrt(1.0 + rho),
        rate_factor=1.0 + rho,
        within_domain=True,
    )


def certified_remainder_radius(
    b: Sequence[float], kappa: float, k_eff: Matrix,
    db_norm: float, dkappa: float,
) -> float:
    """A certified bound on ``||E||_op`` over a primitive uncertainty region.

    The exact second-order Schur remainder has the closed form

        R = ( -u^2 S + u T - D ) / (kappa (1 + u)) ,
        S = b b^T,  T = b db^T + db b^T,  D = db db^T,  u = dkappa / kappa ,

    obtained by subtracting the (U.A10) linearisation from
    ``-(b+db)(b+db)^T/(kappa+dkappa)`` and collecting terms.  Submultiplicativity
    and the triangle inequality then give, for ``|dkappa| <= dkappa`` and
    ``||db|| <= db_norm``,

        ||R|| <= ( u^2 ||b||^2 + 2 u ||b|| db_norm + db_norm^2 )
                 / ( kappa (1 - u) ) ,     u = dkappa / kappa ,

    and normalising, ``rho = ||R|| / lambda_min(K_eff)``.  Every step is an
    inequality, so this bounds the whole region rather than sampling it.
    """
    if kappa <= 0.0:
        raise NumericalFailure("axial stiffness must be positive")
    u = abs(dkappa) / kappa
    if u >= 1.0:
        raise NumericalFailure("axial stiffness uncertainty reaches zero stiffness")
    bn = math.sqrt(sum(float(v) * float(v) for v in b))
    num = u * u * bn * bn + 2.0 * u * bn * db_norm + db_norm * db_norm
    r_bound = num / (kappa * (1.0 - u))
    vals, _ = nm.eigh(nm.symmetrise(k_eff))
    lam_min = min(vals)
    if lam_min <= 0.0:
        raise NumericalFailure("K_eff is not positive definite")
    return r_bound / lam_min


def remainder_impacts(e_k: Matrix) -> FiniteRemainderEffects:
    """Exact finite effects of ONE normalised remainder, as a set of radius ``||E||``.

    Retained as an illustration and for the auditor's counterexamples.  The
    scale and geometry entries are the exact effects of this specific ``E``;
    the remaining entries are suprema over the ball of the same radius.
    """
    rho = nm.op_norm_sym(nm.symmetrise(e_k))
    if rho >= REMAINDER_DOMAIN_LIMIT:
        return FiniteRemainderEffects(
            rho, float("inf"), float("inf"), float("inf"),
            float("inf"), float("inf"), False,
        )
    scale = abs(exact_log_beta_bias(e_k))
    return FiniteRemainderEffects(
        rho=rho,
        log_beta_bias=scale,
        contrast_bias=scale,
        geometry=exact_geometry_effect(e_k),
        centre_factor=math.sqrt(1.0 + rho),
        rate_factor=1.0 + rho,
        within_domain=True,
    )


def schur_nonlinear_remainder(
    b: Sequence[float], kappa: float, db: Sequence[float], dkappa: float
) -> NonlinearRemainder:
    """Exact minus linearised Schur correction for a given perturbation.

    Near ``b = 0`` the leading Jacobian in ``b`` vanishes, so the quadratic term
    must be propagated explicitly rather than linearised to zero variance
    (U-stage section 5.4).

    Returns the residual as a TYPED stiffness matrix in N/m.  It is only
    meaningful after :func:`normalise_remainder`.
    """
    b1, b2 = float(b[0]), float(b[1])
    k = float(kappa)
    nb1, nb2 = b1 + float(db[0]), b2 + float(db[1])
    nk = k + float(dkappa)
    if nk <= 0.0:
        raise NumericalFailure("perturbed axial stiffness is not positive")

    def corr(x1: float, x2: float, kk: float) -> tuple[float, float, float]:
        return (x1 * x1 / kk, x1 * x2 / kk, x2 * x2 / kk)

    c0 = corr(b1, b2, k)
    c1 = corr(nb1, nb2, nk)
    exact = tuple(-(c1[i] - c0[i]) for i in range(3))
    J = schur_jacobian(b, kappa)
    dv = [0.0, 0.0, 0.0, float(db[0]), float(db[1]), float(dkappa)]
    lin = tuple(sum(J[i][j] * dv[j] for j in range(6)) for i in range(3))
    return NonlinearRemainder.stiffness(
        [exact[i] - lin[i] for i in range(3)],
        source="exact minus linearised Schur correction",
    )


def propagate_schur_covariance(
    k3: Matrix, c_v: Matrix
) -> tuple[Matrix, tuple[Refusal, ...]]:
    """``C_vech(S) = J_S C_v J_S^T`` for ``v = (A11, A12, A22, b1, b2, kappa)``."""
    if c_v is None:
        return [], (
            refuse(
                MISSING_COVARIANCE,
                "C_v present",
                "axial primitive covariance is absent; missing evidence is not zero error",
            ),
        )
    if nm.shape(c_v) != (6, 6):
        return [], (
            refuse(
                MISSING_COVARIANCE,
                "C_v is 6-by-6",
                "axial primitive covariance must cover (A11, A12, A22, b1, b2, kappa)",
                shape=list(nm.shape(c_v)),
            ),
        )
    if not nm.is_finite_matrix(c_v):
        return [], (
            refuse(
                NUMERICAL_REPRESENTATION_FAILURE,
                "C_v entries finite",
                "axial primitive covariance contains a non-finite entry",
            ),
        )
    _, b, kappa = split_3d(nm.symmetrise(k3))
    J = schur_jacobian([b[0][0], b[1][0]], kappa)
    cs = nm.matmul(nm.matmul(J, c_v), nm.transpose(J))
    return nm.symmetrise(cs), ()


def normalise_covariance_to_h(
    k_eff: Matrix,
    c_vech_s: Matrix,
    temperature: float,
    var_log_t: float,
    cov_s_logt: Sequence[float] | None = None,
) -> Matrix:
    """Propagate ``dH_eff = dS/(k_B T) - H_eff dT/T`` into ``C_vech(H_eff)``.

    The same temperature error must not be counted twice: it enters once here
    through ``-H dT/T`` and separately inside ``eta(T)``; the caller supplies
    their covariance through ``cov_s_logt`` rather than assuming independence.
    """
    kbt = K_B * temperature
    h = nm.scale(k_eff, 1.0 / kbt)
    hv = [h[0][0], h[0][1], h[1][1]]
    inv = 1.0 / kbt
    # d vech(H) = inv * d vech(S) - hv * dlogT
    c = nm.zeros(3)
    for i in range(3):
        for j in range(3):
            c[i][j] = inv * inv * c_vech_s[i][j] + hv[i] * hv[j] * var_log_t
    if cov_s_logt is not None:
        for i in range(3):
            for j in range(3):
                c[i][j] -= inv * (hv[j] * cov_s_logt[i] + hv[i] * cov_s_logt[j])
    return nm.symmetrise(c)


def reduce_axial(
    k3: Matrix | None,
    temperature: float,
    evidence: AxialEvidence | None = None,
    c_v: Matrix | None = None,
    var_log_t: float = 0.0,
    cov_s_logt: Sequence[float] | None = None,
    condition_limit: float = 100.0,
    skew_rtol: float = SKEW_RTOL,
) -> SchurReduction:
    """Full axial reduction with its qualification predicate (U-stage 5.8).

    **Fail-closed.** Every U-required component must carry explicit evidence.
    Absent evidence is refused, never read as qualified, and the covariance is
    mandatory: a point Schur matrix without uncertainty is not a valid
    Branch-A comparison field. Any failing dependency yields
    ``AXIAL_REDUCTION_UNQUALIFIED`` with its precise reason, and there is no
    fallback to a plane-only calibration.
    """
    if evidence is None:
        return SchurReduction(
            [], [], [], float("nan"),
            refusals=(
                refuse(
                    AXIAL_REDUCTION_UNQUALIFIED,
                    "axial evidence supplied",
                    "no axial qualification evidence was supplied; "
                    "missing evidence fails closed",
                ),
            ),
        )

    refusals: list[Refusal] = list(validate_3d_stiffness(k3, evidence, skew_rtol))
    if refusals:
        return SchurReduction([], [], [], float("nan"), refusals=tuple(refusals))
    assert k3 is not None

    # --- every remaining U-required evidence item, fail-closed --------------
    for name in evidence.missing():
        if name == "conservativity_qualified":
            continue  # already handled above
        refusals.append(
            refuse(
                AXIAL_REDUCTION_UNQUALIFIED,
                f"{name} evidence supplied",
                f"no evidence for {name}; missing evidence fails closed",
                component=name,
            )
        )
    for name in evidence.failed():
        if name == "conservativity_qualified":
            continue
        refusals.append(
            refuse(
                AXIAL_REDUCTION_UNQUALIFIED,
                f"{name} qualified",
                f"{name} is explicitly not qualified",
                component=name,
            )
        )

    # --- covariance is mandatory -------------------------------------------
    if c_v is None:
        refusals.append(
            refuse(
                MISSING_COVARIANCE,
                "axial primitive covariance supplied",
                "a point Schur matrix without uncertainty is not a valid "
                "Branch-A comparison field",
            )
        )

    # --- the certified remainder SET, not one evaluated witness -------------
    remainder_set = evidence.remainder_set
    if remainder_set is None:
        refusals.append(
            refuse(
                AXIAL_REDUCTION_UNQUALIFIED,
                "certified remainder set supplied",
                "no certified set of admissible second-order Schur remainders; "
                "a single evaluated perturbation does not qualify the set",
            )
        )
    elif not remainder_set.within_domain:
        refusals.append(
            refuse(
                AXIAL_REDUCTION_UNQUALIFIED,
                f"||E_K||_op < {REMAINDER_DOMAIN_LIMIT}",
                "the certified remainder set leaves the domain where the "
                "linearisation it bounds is defined; K_eff + Delta K need not "
                "be positive definite",
                remainder_set_radius=remainder_set.rho,
            )
        )
    if evidence.nonlinear_remainder is not None and not evidence.nonlinear_remainder.finite:
        refusals.append(
            refuse(
                NUMERICAL_REPRESENTATION_FAILURE,
                "remainder witness entries finite",
                "the supplied remainder witness is not finite",
            )
        )

    try:
        k_eff = schur_complement(k3)
        r = axial_ratio(k3)
    except NumericalFailure as exc:
        refusals.append(
            refuse(AXIAL_REDUCTION_UNQUALIFIED, "Schur complement computable", str(exc))
        )
        return SchurReduction([], [], [], float("nan"), refusals=tuple(refusals))

    if not nm.is_spd(k_eff):
        refusals.append(
            refuse(
                AXIAL_REDUCTION_UNQUALIFIED,
                "S SPD",
                "Schur complement is not positive definite; no SPD projection is applied",
            )
        )
    if not (0.0 <= r < 1.0):
        refusals.append(
            refuse(
                AXIAL_REDUCTION_UNQUALIFIED,
                "0 <= r < 1",
                "axial ratio outside its admissible range",
                r=r,
            )
        )

    _, b, kappa = split_3d(nm.symmetrise(k3))
    delta_k = nm.scale(
        [[b[0][0] * b[0][0], b[0][0] * b[1][0]], [b[1][0] * b[0][0], b[1][0] * b[1][0]]],
        -1.0 / kappa,
    )

    kbt = K_B * temperature
    if not math.isfinite(kbt) or kbt <= 0.0:
        refusals.append(
            refuse(
                AXIAL_REDUCTION_UNQUALIFIED,
                "k_B T > 0",
                "thermal energy is not finite and positive",
                temperature=temperature,
            )
        )
        return SchurReduction([], [], delta_k, r, refusals=tuple(refusals))

    h_eff = nm.symmetrise(nm.scale(k_eff, 1.0 / kbt))
    if not nm.is_finite_matrix(h_eff):
        refusals.append(
            refuse(
                NUMERICAL_REPRESENTATION_FAILURE,
                "H_eff finite",
                "normalised effective Hessian is not finite",
            )
        )
        return SchurReduction(k_eff, [], delta_k, r, refusals=tuple(refusals))
    if nm.is_spd(h_eff):
        kappa2 = nm.cond2_spd(h_eff)
        if kappa2 > condition_limit:
            refusals.append(
                refuse(
                    INSUFFICIENT_GEOMETRY_CALIBRATION,
                    f"cond2(H_eff) <= {condition_limit}",
                    "effective Hessian exceeds the conditioning limit",
                    condition_number=kappa2,
                )
            )

    # --- exact finite effects of the whole set, into the existing budgets ---
    impacts: FiniteRemainderEffects | None = None
    if remainder_set is not None:
        impacts = remainder_set_effects(remainder_set, d=len(k_eff))

    c_vech_s: Matrix | None = None
    c_vech_h: Matrix | None = None
    if c_v is not None:
        c_vech_s, cov_ref = propagate_schur_covariance(k3, c_v)
        if cov_ref:
            refusals.extend(cov_ref)
        else:
            c_vech_h = normalise_covariance_to_h(
                k_eff, c_vech_s, temperature, var_log_t, cov_s_logt
            )

    return SchurReduction(
        k_eff=k_eff,
        h_eff=h_eff,
        delta_k_axial=delta_k,
        r=r,
        c_vech_s=c_vech_s,
        c_vech_h=c_vech_h,
        remainder_impacts=impacts,
        refusals=tuple(refusals),
    )
