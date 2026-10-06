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

#: Maximum admissible relative second-order Schur remainder (U-stage 5.4).
NONLINEAR_REMAINDER_CEILING = 1.0e-3

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
    #: U section 5.4: certified bound on the second-order Schur remainder.
    nonlinear_remainder: float | None = None
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
    def fully_qualified(nonlinear_remainder: float = 0.0) -> "AxialEvidence":
        """Construct complete passing evidence, for synthetic fixtures only."""
        return AxialEvidence(
            conservativity_qualified=True,
            harmonic_domain_qualified=True,
            support_qualified=True,
            temporal_reduction_qualified=True,
            observation_transfer_qualified=True,
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


def schur_nonlinear_remainder(
    b: Sequence[float], kappa: float, db: Sequence[float], dkappa: float
) -> float:
    """Exact minus linearised Schur correction magnitude for a given perturbation.

    Near ``b = 0`` the leading Jacobian in ``b`` vanishes, so the quadratic term
    must be propagated explicitly rather than linearised to zero variance
    (U-stage section 5.4).
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
    return max(abs(exact[i] - lin[i]) for i in range(3))


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

    # --- nonlinear remainder must be certified, not merely small ------------
    if evidence.nonlinear_remainder is None:
        refusals.append(
            refuse(
                AXIAL_REDUCTION_UNQUALIFIED,
                "nonlinear remainder bound supplied",
                "no certified second-order Schur remainder bound",
            )
        )
    elif not math.isfinite(evidence.nonlinear_remainder) or (
        evidence.nonlinear_remainder > NONLINEAR_REMAINDER_CEILING
    ):
        refusals.append(
            refuse(
                AXIAL_REDUCTION_UNQUALIFIED,
                f"nonlinear remainder <= {NONLINEAR_REMAINDER_CEILING}",
                "second-order Schur remainder exceeds its enclosure ceiling",
                remainder=evidence.nonlinear_remainder,
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
        refusals=tuple(refusals),
    )
