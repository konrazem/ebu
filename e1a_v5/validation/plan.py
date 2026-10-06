"""Frozen V-stage design point and validation-procedure configuration.

The physical design point below is a *synthetic prospective* configuration
consistent with the T/U domains.  It is not measured apparatus performance and
no value here is a real calibration.
"""

from __future__ import annotations

import math

from .. import numerics as nm
from ..units import K_B

#: Reference temperature, K.
T_REF = 298.0
#: Hot-field nominal temperature, K.
T_HOT = 318.0
#: Nominal reference stiffness, N/m (100 micro N/m).
K_REF = 1.0e-4
#: Nominal stiffness-challenge factor.
K_FACTOR = 2.1
#: Nominal ellipse eigenvalues, N/m, and orientation.
K_ELLIPSE = (1.5e-4, 0.6e-4)
ELLIPSE_ANGLE = math.pi / 6.0
#: Synthetic bead radius, m, and buffer viscosity at T_REF, Pa.s.
BEAD_RADIUS = 0.5e-6
VISCOSITY_REF = 0.89e-3
#: Axial stiffness as a fraction of the lateral reference (synthetic).
AXIAL_FRACTION = 0.2
#: Synthetic lateral-axial coupling as a fraction of the lateral reference.
AXIAL_COUPLING = 0.05
#: Instantaneous localisation variance ratio in whitened directions
#: (T.23 / T-stage 15.2).  Ceiling 0.05; nominal sits inside it.
LOCALIZATION_RATIO_NOMINAL = 0.02
#: Exposure as a fraction of the fast relaxation time (ceiling is 0.1).
EXPOSURE_FRACTION = 0.05
#: Frame interval as a fraction of the non-aliasing bandwidth ceiling.
#: dt = BANDWIDTH_FRACTION * 0.2 * tau_fast, so the bandwidth product is
#: 0.2 * BANDWIDTH_FRACTION, inside the T-stage 12.2 ceiling, and dt exceeds
#: t_exp = EXPOSURE_FRACTION * tau_fast by construction.
BANDWIDTH_FRACTION = 0.75
#: Relative inward placement for a world designed to sit AT a qualification
#: limit; see :func:`conditioned_stiffness`.  Numerical placement only.
CONDITION_PLACEMENT_MARGIN = 1.0e-11

#: Information target per cell (T.23).
N_STAR = 450000
I_STAR = 408164

#: Calibration standard uncertainties used by the synthetic auxiliary law.
SIGMA_CAL_ABSOLUTE = 0.0060
SIGMA_CAL_CELL = 0.0015
#: Certified bounded systematic log-beta contribution per cell.
BIAS_PER_CELL = 0.00025
#: Relative standard uncertainty of each axial primitive in the declared
#: Branch-A covariance, and the coverage factor the certified remainder set is
#: constructed at.
PRIMITIVE_RELATIVE_SIGMA = 1.0e-3
REMAINDER_COVERAGE_K = 3.0


def rotation(theta: float) -> list[list[float]]:
    c, s = math.cos(theta), math.sin(theta)
    return [[c, -s], [s, c]]


def nominal_stiffness(field_index: int) -> list[list[float]]:
    """Nominal lateral stiffness matrix for each field, N/m."""
    if field_index == 0 or field_index == 3:
        return [[K_REF, 0.0], [0.0, K_REF]]
    if field_index == 1:
        return [[K_FACTOR * K_REF, 0.0], [0.0, K_FACTOR * K_REF]]
    r = rotation(ELLIPSE_ANGLE)
    return nm.symmetrise(
        nm.matmul(nm.matmul(r, [[K_ELLIPSE[0], 0.0], [0.0, K_ELLIPSE[1]]]), nm.transpose(r))
    )


def nominal_temperature(field_index: int) -> float:
    return T_HOT if field_index == 3 else T_REF


def nominal_k3(field_index: int, coupling: float = AXIAL_COUPLING) -> list[list[float]]:
    """Full 3D stiffness with a declared lateral-axial coupling."""
    k = nominal_stiffness(field_index)
    kz = AXIAL_FRACTION * K_REF
    b = coupling * K_REF
    return [
        [k[0][0], k[0][1], b],
        [k[1][0], k[1][1], 0.5 * b],
        [b, 0.5 * b, kz],
    ]


def thermal_hessian(k_eff: list[list[float]], temperature: float) -> list[list[float]]:
    return nm.symmetrise(nm.scale(k_eff, 1.0 / (K_B * temperature)))


def drag_coefficient() -> float:
    return 6.0 * math.pi * VISCOSITY_REF * BEAD_RADIUS


def conditioned_stiffness(
    k_lateral: list[list[float]], condition_target: float
) -> list[list[float]]:
    """Reshape a lateral stiffness to an exact spectral condition number.

    The geometric mean of the eigenvalues -- equivalently the determinant, and
    so the overall scale of the trap -- is preserved, and only their ratio
    moves.  That isolates the conditioning as the single thing the case
    changes: a conditioning case that also moved the scale would confound the
    two.

    The world is placed a few ulps INSIDE the requested ratio.  A case
    designed to sit at the qualification limit must not have its outcome
    decided by the rounding of the limit's own evaluation: the symmetric
    eigensolver reports ``cond2`` with a relative backward error of order
    ``n * eps * cond2``, which at a target of 100 is about 4e-13 and is
    exactly what pushed a world constructed AT the limit over a strict
    ``cond2 <= 100`` test.  ``CONDITION_PLACEMENT_MARGIN`` is a numerical
    placement far below any physical resolution; it does not widen the
    scientific limit, which stays where T/U put it.
    """
    if not (condition_target >= 1.0 and math.isfinite(condition_target)):
        raise nm.NumericalFailure(
            f"condition target {condition_target!r} must be finite and at least 1"
        )
    vals, q = nm.eigh(nm.symmetrise(k_lateral))
    g = math.sqrt(max(vals[0], 1e-300) * max(vals[1], 1e-300))
    root = math.sqrt(condition_target * (1.0 - CONDITION_PLACEMENT_MARGIN))
    lam = [g * root, g / root]
    return nm.symmetrise(
        nm.matmul(nm.matmul(q, [[lam[0], 0.0], [0.0, lam[1]]]), nm.transpose(q))
    )


def k3_from_lateral(
    k_lateral: list[list[float]], coupling: float = AXIAL_COUPLING,
    axial_fraction: float = AXIAL_FRACTION,
) -> list[list[float]]:
    """Build a 3D stiffness whose SCHUR COMPLEMENT is exactly ``k_lateral``.

    ``K_qq = S + b kappa^{-1} b^T`` inverts the Schur complement exactly, so a
    conditioning target set on the lateral matrix survives the axial reduction
    instead of being perturbed by the coupling.
    """
    kz = axial_fraction * K_REF
    b = [coupling * K_REF, 0.6 * coupling * K_REF]
    k_qq = [
        [k_lateral[i][j] + b[i] * b[j] / kz for j in range(2)] for i in range(2)
    ]
    return [
        [k_qq[0][0], k_qq[0][1], b[0]],
        [k_qq[1][0], k_qq[1][1], b[1]],
        [b[0], b[1], kz],
    ]


def timing(
    k_eff: list[list[float]], exposure_fraction: float = EXPOSURE_FRACTION
) -> tuple[float, float]:
    """Return ``(dt, t_exp)`` from the bandwidth and exposure ceilings."""
    gamma = drag_coefficient()
    vals, _ = nm.eigh(k_eff)
    k_fast = max(vals)
    k_slow = min(vals)
    tau_fast = gamma / k_fast
    rate_fast = 1.0 / tau_fast
    dt = BANDWIDTH_FRACTION * 0.2 / rate_fast
    t_exp = exposure_fraction * tau_fast
    if not (0.0 <= t_exp <= dt):
        raise nm.NumericalFailure(
            f"design point inconsistent: exposure {t_exp!r} exceeds frame interval {dt!r}"
        )
    return dt, t_exp


#: Smoke-sample configuration, used ONLY when the full campaign is infeasible.
#: Every artefact produced under it is labelled ENGINEERING SMOKE SAMPLE and
#: can never contribute to a RELEASE verdict.
SMOKE_FRAMES = 1500
SMOKE_SIZE_REPLICATES = 120
SMOKE_DIAGNOSTIC_REPLICATES = 120
SMOKE_POWER_REPLICATES = 12
SMOKE_CONTROL_REPLICATES = 20
SMOKE_CALIBRATION_REPLICATES = 240
SMOKE_LABEL = "ENGINEERING SMOKE SAMPLE - NOT A VALIDATION RESULT"


def remainder_set(k3: list[list[float]], coverage_k: float = REMAINDER_COVERAGE_K):
    """The certified admissible remainder set for one record's reduction.

    Built from the declared primitive covariance by the closed-form bound in
    :func:`~e1a_v5.reduction.certified_remainder_radius`, at a stated coverage
    factor.  Every step of that bound is an inequality, so the resulting set
    covers the whole primitive uncertainty region rather than one sampled
    perturbation.
    """
    from ..reduction import RemainderSet, certified_remainder_radius, schur_complement, split_3d
    _, b, kappa = split_3d(nm.symmetrise(k3))
    sd = PRIMITIVE_RELATIVE_SIGMA * K_REF
    rho = certified_remainder_radius(
        [b[0][0], b[1][0]], kappa, schur_complement(k3),
        db_norm=coverage_k * sd * math.sqrt(2.0),
        dkappa=coverage_k * sd,
    )
    return RemainderSet(
        rho,
        f"closed-form Schur remainder bound at {coverage_k} sigma of the "
        f"declared primitive covariance",
    )


# ---------------------------------------------------------------------------
# CTL-AXIAL-MEMORY: the prospective 3D hidden-memory world
# ---------------------------------------------------------------------------
#
# Chosen prospectively, before any outcome is inspected: the largest coupling
# that keeps K3 positive definite and the lateral Schur complement comfortably
# inside the conditioning limit while leaving a clearly non-Markov lateral lag
# structure.  The axial mode is deliberately SOFT, so it relaxes slowly and its
# memory survives at the sampled lags.
AXIAL_MEMORY_COUPLING = 0.15
AXIAL_MEMORY_AXIAL_FRACTION = 0.08


def axial_memory_k3(field_index: int) -> list[list[float]]:
    """3D stiffness whose SCHUR COMPLEMENT is the nominal lateral field.

    The lateral marginal density is therefore exactly the one the bridge
    expects, ``Sigma_qq = k_B T K_eff^{-1}``, and only the lateral PATH
    differs.  That isolates the control on temporal-model qualification rather
    than confounding it with a density mismatch.
    """
    return k3_from_lateral(
        nominal_stiffness(field_index),
        coupling=AXIAL_MEMORY_COUPLING,
        axial_fraction=AXIAL_MEMORY_AXIAL_FRACTION,
    )


# ---------------------------------------------------------------------------
# CTL-ETA-T-COV: the shared thermometry dependency
# ---------------------------------------------------------------------------
#
# The stiffness standard is realised by equipartition against a measured
# temperature, so an error in the temperature standard enters the reported
# stiffness as well as the explicit ``-H dT/T`` term.  The two therefore share
# one variable and are POSITIVELY correlated.
#
# The misspecified alternative treats them as independent.  Because
# ``d log beta*/d log k_A = -1`` and ``d log beta*/d log T_A = +1``, the
# correct variance carries ``-2 rho sigma_k sigma_T`` and the omission
# OVERSTATES the uncertainty at this design point.  That direction is a
# property of this primitive map, not a general rule: V4 asserted that
# omitting the covariance always understates, which the V4 exact check itself
# contradicted, and the assertion is removed.
ETA_T_CORRELATION = 0.7
