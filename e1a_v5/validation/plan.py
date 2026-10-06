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

#: The declared configuration that enters every procedure identity.  It is
#: the same object the frozen plan records, kept in code so the gate
#: calibration receipt can be checked against the running procedure's own
#: identities rather than against a transcription.
IDENTITY_CONFIGURATION = {
    "design_point": "e1a_v5_candidate_2026-10-06",
    "domain_identity": "e1a_v5_candidate_2026-10-06/nominal-envelope",
    "policy_version": "E1A-T11a-RF-v1",
    "procedure_version": 6,
    "supersedes": "procedure version 5 (audit: NOT CLEARED)",
}

#: Information target per cell (T.23).
N_STAR = 450000
I_STAR = 408164

#: Calibration standard uncertainties used by the synthetic auxiliary law.
SIGMA_CAL_ABSOLUTE = 0.0060
SIGMA_CAL_CELL = 0.0015
#: Certified bounded systematic log-beta contribution per cell.
BIAS_PER_CELL = 0.00025
#: Relative standard uncertainty of each axial primitive in the declared
#: Branch-A covariance.  The coverage FACTOR is no longer a free constant: the
#: certified remainder set is built over the joint 99.9% calibration region,
#: whose per-primitive factor comes from the region's own noncoverage
#: allocation.  V5's informal 3 sigma is gone.
PRIMITIVE_RELATIVE_SIGMA = 1.0e-3

# ---------------------------------------------------------------------------
# The complete declared auxiliary primitive model (U)
# ---------------------------------------------------------------------------
#
# V5's production C_phi varied a stiffness standard, a temperature standard
# and one per-field stiffness primitive.  Independent audit found that
# incomplete, correctly: U requires every load-bearing auxiliary category to
# be accounted for, and absence must never mean zero uncertainty.
#
# Every value below is a SYNTHETIC PROSPECTIVE declaration consistent with the
# T/U domains.  None is a measured apparatus performance and none is a real
# calibration.

#: Shared standards.
SIGMA_LOG_T_STANDARD = 1.0e-3
#: Viscosity / eta(T).
SIGMA_LOG_ETA_REF = 2.0e-3
SIGMA_LOG_ETA_DT = 5.0e-3
#: Bead radius / material transfer, as a log.
SIGMA_LOG_BEAD_RADIUS = 1.0e-3
#: 3D force / displacement calibration transfer.
SIGMA_LOG_FORCE_CAL = 1.5e-3
#: Axial stiffness and lateral-axial coupling, as logs of the nominal.
SIGMA_LOG_AXIAL_STIFFNESS = 2.0e-2
SIGMA_LOG_AXIAL_COUPLING = 5.0e-2
#: Coordinate transform P: isotropic gain and off-diagonal shear.
SIGMA_LOG_P_GAIN = 1.0e-3
SIGMA_P_SHEAR = 5.0e-4
#: Localisation covariance scale, as a log.
SIGMA_LOG_R_OBS = 2.0e-2
#: Detector offset and centre/fiducial transfer, in metres.
SIGMA_B_DET = 2.0e-9
SIGMA_FIDUCIAL = 2.0e-9
#: Shutter / exposure and timing / synchronisation, as logs.
SIGMA_LOG_T_EXP = 1.0e-3
SIGMA_LOG_DT = 1.0e-4
#: Block-scoped transfers.
SIGMA_LOG_K_BLOCK = 1.0e-3
SIGMA_LOG_T_BLOCK = 5.0e-4
#: Deterministic bounded wall / hydrodynamic resistance correction, as a
#: fractional bound on the drag.  A bounded model error, never a Gaussian.
BOUND_WALL_HYDRODYNAMIC = 5.0e-3

#: Primitive names.  The variable IDENTITY is the name plus its scope, so a
#: standard shared by several records is one variable by construction.
PRIMITIVE_K_STANDARD = "log_k_standard"
PRIMITIVE_T_STANDARD = "log_T_standard"
PRIMITIVE_ETA_REF = "log_eta_ref"
PRIMITIVE_ETA_DT = "log_eta_dT"
PRIMITIVE_BEAD_RADIUS = "log_bead_radius"
PRIMITIVE_FORCE_CAL = "log_force_displacement_cal"
PRIMITIVE_AXIAL_STIFFNESS = "log_axial_stiffness"
PRIMITIVE_AXIAL_COUPLING = "log_axial_coupling"
PRIMITIVE_P_GAIN = "log_p_gain"
PRIMITIVE_P_SHEAR = "p_shear"
PRIMITIVE_R_OBS = "log_r_obs_scale"
PRIMITIVE_B_DET_X = "b_det_x"
PRIMITIVE_B_DET_Y = "b_det_y"
PRIMITIVE_FIDUCIAL_X = "fiducial_x"
PRIMITIVE_FIDUCIAL_Y = "fiducial_y"
PRIMITIVE_T_EXP = "log_t_exp"
PRIMITIVE_DT = "log_dt"
PRIMITIVE_K_BLOCK = "log_k_block"
PRIMITIVE_T_BLOCK = "log_T_block"
PRIMITIVE_K_FIELD = "log_k_field"

#: The shared thermometry standard.  The stiffness standard is realised by
#: equipartition against a measured temperature, so an error in the
#: temperature standard enters the reported stiffness as well as the explicit
#: ``-H dT/T`` term.  One LATENT variable carries that sharing, so it is a
#: structural property of the generating law rather than an off-diagonal entry
#: asserted only in the analyser's matrix.
LATENT_THERMOMETRY = "thermometry_standard"
ETA_T_CORRELATION = 0.7


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


# ---------------------------------------------------------------------------
# The declared independent response-measurement architecture
# ---------------------------------------------------------------------------
#
# Branch A qualifies the retained 2D temporal model against a measured
# response.  These are SYNTHETIC PROSPECTIVE declarations of that measurement,
# chosen before any outcome was inspected and sized so the measurement can
# resolve a semigroup violation of the declared size.  They are properties of
# the measurement, not scientific tolerances on the bridge.

#: Response lag, as a multiple of the lateral slow relaxation time.  A longer
#: lag separates a projected three-mode response from a 2D semigroup more
#: strongly, while shrinking the response itself; this is where the two meet.
RESPONSE_LAG_FRACTION = 1.5
#: Independent prepared releases per lateral direction and per lag.
RESPONSE_TRIALS = 6000
#: Initial lateral displacement, in units of the stationary lateral sd.
RESPONSE_DISPLACEMENT_SD = 6.0
#: Coverage factor on the measurement's own standard error.  A residual inside
#: this band does not exclude the 2D class.
RESPONSE_BAND_SIGMA = 5.0
#: Required resolution of the response measurement.  If the band is wider than
#: this, the measurement cannot exclude anything and the temporal model is
#: UNRESOLVED rather than qualified -- the fail-closed direction.
RESPONSE_RESOLUTION = 0.20

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


# ---------------------------------------------------------------------------
# The declared auxiliary primitive vector and its joint region
# ---------------------------------------------------------------------------

def primitive_vector(share_thermometry: bool = True):
    """The COMPLETE declared auxiliary primitive vector of the packet.

    ``share_thermometry`` is the only switch: with it the stiffness and
    temperature standards load on one latent thermometry variable, which is
    the declared physics; without it they are independent, which is the
    CTL-ETA-T-COV misspecification.  The switch changes the ANALYSER's model.
    The generating law always uses the shared version.
    """
    from ..calibration import Primitive, PrimitiveVector, Scope
    from ..packets import RECORDS

    v = PrimitiveVector()
    g = Scope.GLOBAL

    def add(name, sigma, scope=g, block=None, fld=None):
        v.add(Primitive(name, scope, 0.0, sigma, block, fld))

    add(PRIMITIVE_K_STANDARD, SIGMA_CAL_ABSOLUTE)
    add(PRIMITIVE_T_STANDARD, SIGMA_LOG_T_STANDARD)
    add(PRIMITIVE_ETA_REF, SIGMA_LOG_ETA_REF)
    add(PRIMITIVE_ETA_DT, SIGMA_LOG_ETA_DT)
    add(PRIMITIVE_BEAD_RADIUS, SIGMA_LOG_BEAD_RADIUS)
    add(PRIMITIVE_FORCE_CAL, SIGMA_LOG_FORCE_CAL)
    add(PRIMITIVE_AXIAL_STIFFNESS, SIGMA_LOG_AXIAL_STIFFNESS)
    add(PRIMITIVE_AXIAL_COUPLING, SIGMA_LOG_AXIAL_COUPLING)
    add(PRIMITIVE_P_GAIN, SIGMA_LOG_P_GAIN)
    add(PRIMITIVE_P_SHEAR, SIGMA_P_SHEAR)
    add(PRIMITIVE_R_OBS, SIGMA_LOG_R_OBS)
    add(PRIMITIVE_B_DET_X, SIGMA_B_DET)
    add(PRIMITIVE_B_DET_Y, SIGMA_B_DET)
    add(PRIMITIVE_FIDUCIAL_X, SIGMA_FIDUCIAL)
    add(PRIMITIVE_FIDUCIAL_Y, SIGMA_FIDUCIAL)
    add(PRIMITIVE_T_EXP, SIGMA_LOG_T_EXP)
    add(PRIMITIVE_DT, SIGMA_LOG_DT)
    seen_blocks = []
    for blk, fld in RECORDS:
        if blk not in seen_blocks:
            seen_blocks.append(blk)
            add(PRIMITIVE_K_BLOCK, SIGMA_LOG_K_BLOCK, Scope.BLOCK, blk, fld)
            add(PRIMITIVE_T_BLOCK, SIGMA_LOG_T_BLOCK, Scope.BLOCK, blk, fld)
        add(PRIMITIVE_K_FIELD, SIGMA_CAL_CELL, Scope.FIELD, blk, fld)
    if share_thermometry:
        root = math.sqrt(ETA_T_CORRELATION)
        v.load_on_latent(PRIMITIVE_K_STANDARD, LATENT_THERMOMETRY, root)
        v.load_on_latent(PRIMITIVE_T_STANDARD, LATENT_THERMOMETRY, root)
    return v


def category_declarations():
    """How every required U primitive category is accounted for.

    Four categories carry primitives whose sensitivity to the fitted log beta
    is STRUCTURALLY zero rather than merely small: the viscosity parameters
    and the centre/fiducial transfer never enter the analysis model at all,
    because the estimator profiles the full drift ``A`` freely and the
    fiducial moves only the centre statistic.  They are declared UNCERTAIN
    anyway -- their uncertainty is real and U requires it accounted for -- and
    the zero rows they produce are demonstrated, not assumed.
    """
    from ..calibration import CategoryDeclaration as D, PrimitiveClass as C

    return (
        D("viscosity_eta_of_T", C.UNCERTAIN,
          (PRIMITIVE_ETA_REF, PRIMITIVE_ETA_DT),
          justification="buffer viscosity and its temperature coefficient; "
                        "they set the drag, which the estimator profiles"),
        D("temperature_calibration", C.UNCERTAIN,
          (PRIMITIVE_T_STANDARD, PRIMITIVE_T_BLOCK)),
        D("bead_radius_material_transfer", C.UNCERTAIN,
          (PRIMITIVE_BEAD_RADIUS,)),
        D("force_displacement_calibration_3d", C.UNCERTAIN,
          (PRIMITIVE_FORCE_CAL,)),
        D("axial_stiffness_coupling", C.UNCERTAIN,
          (PRIMITIVE_AXIAL_STIFFNESS, PRIMITIVE_AXIAL_COUPLING)),
        D("wall_hydrodynamic_resistance", C.BOUNDED_SYSTEMATIC,
          bound=BOUND_WALL_HYDRODYNAMIC,
          justification="a deterministic near-surface drag correction with a "
                        "stated fractional bound; U forbids converting a "
                        "bounded model error into a Gaussian variable"),
        D("coordinate_transform_P", C.UNCERTAIN,
          (PRIMITIVE_P_GAIN, PRIMITIVE_P_SHEAR)),
        D("centre_fiducial_transfer", C.UNCERTAIN,
          (PRIMITIVE_FIDUCIAL_X, PRIMITIVE_FIDUCIAL_Y),
          justification="the fiducial enters the centre statistic, not the "
                        "scale; its log-beta row is a demonstrated zero"),
        D("localization_covariance_R_obs", C.UNCERTAIN, (PRIMITIVE_R_OBS,)),
        D("detector_offset", C.UNCERTAIN,
          (PRIMITIVE_B_DET_X, PRIMITIVE_B_DET_Y)),
        D("shutter_exposure", C.UNCERTAIN, (PRIMITIVE_T_EXP,)),
        D("timing_synchronization", C.UNCERTAIN, (PRIMITIVE_DT,)),
        D("shared_standards", C.UNCERTAIN, (PRIMITIVE_K_STANDARD,)),
        D("block_specific", C.UNCERTAIN, (PRIMITIVE_K_BLOCK,)),
        D("field_specific", C.UNCERTAIN, (PRIMITIVE_K_FIELD,)),
    )


_JOINT_REGION = None


def default_joint_region():
    """The packet's joint 99.9% physical calibration region, built once."""
    global _JOINT_REGION
    if _JOINT_REGION is None:
        from ..calibration import build_joint_region
        _JOINT_REGION = build_joint_region(
            primitive_vector(), category_declarations(),
        )
    return _JOINT_REGION


#: A construction-time semigroup residual at or below this is zero to
#: rounding: a 2D world's lateral response IS the semigroup, so the residual
#: is exactly zero in exact arithmetic and only matrix-exponential rounding
#: separates it from zero.
CONSTRUCTION_SEMIGROUP_TOLERANCE = 1.0e-10


def construction_temporal_qualified(k_eff, temperature: float) -> bool:
    """Derive -- never assert -- the temporal qualification of a built world.

    The design builders construct a 2D overdamped world from ``K_eff``, so
    there is no hidden mode and the exact semigroup residual is zero.  That is
    COMPUTED here rather than written down as ``True``: a builder handed a
    world with a hidden mode gets False and the reduction refuses it.
    """
    from ..generate import exact_semigroup_residual
    sigma = nm.scale(nm.spd_inverse(nm.symmetrise(k_eff)), K_B * temperature)
    a = nm.scale(nm.symmetrise(k_eff), 1.0 / drag_coefficient())
    return exact_semigroup_residual(a, sigma) <= CONSTRUCTION_SEMIGROUP_TOLERANCE


def remainder_set(k3: list[list[float]], region=None):
    """The certified admissible remainder set for one record's reduction.

    Built by the closed-form bound in
    :func:`~e1a_v5.reduction.certified_remainder_radius` over the **joint
    99.9% physical calibration region**, not over a marginal multiple of one
    primitive's standard uncertainty.  Every step of that bound is an
    inequality, so the resulting set covers the whole region rather than one
    sampled perturbation or one convenient corner.

    The axial half-extents come from the region itself.  Two primitives move
    the Schur remainder: the axial stiffness ``kappa`` and the lateral-axial
    coupling ``b``.  Their region half-widths are relative, so they are
    applied to the nominal magnitudes of this record's own ``K3``, and the
    bounded wall/hydrodynamic systematic is added to the coupling extent
    rather than being folded into a variance.
    """
    from ..reduction import (
        RemainderSet, certified_remainder_radius, schur_complement, split_3d,
    )
    if region is None:
        region = default_joint_region()
    _, b, kappa = split_3d(nm.symmetrise(k3))
    bvec = [b[0][0], b[1][0]]
    b_norm = math.sqrt(sum(v * v for v in bvec))
    rel_kappa = region.half_width_of_name(PRIMITIVE_AXIAL_STIFFNESS)
    rel_coupling = region.half_width_of_name(PRIMITIVE_AXIAL_COUPLING)
    rel_coupling += region.bounded_systematic("wall_hydrodynamic_resistance")
    # exp(x) - 1 <= x e^x bounds the relative excursion of a log primitive
    # over its own half-width, with no linearisation.
    def _rel(x: float) -> float:
        return math.expm1(abs(x)) if x >= 0.0 else abs(math.expm1(-abs(x)))

    rho = certified_remainder_radius(
        bvec, kappa, schur_complement(k3),
        db_norm=_rel(rel_coupling) * b_norm,
        dkappa=_rel(rel_kappa) * kappa,
    )
    return RemainderSet(
        rho,
        "closed-form Schur remainder bound over the joint "
        f"{region.joint_coverage:.4f} physical calibration region "
        f"(identity {region.identity()[:16]})",
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
# The sharing is declared as a LATENT standard (see LATENT_THERMOMETRY), so
# the control's generating law draws the shared thermometry error once and
# feeds it to both primitives.  The misspecified analyser omits the latent and
# treats the two as independent; the data it analyses still carry the true
# shared structure.  V5 changed only the analyser's matrix and left the
# auxiliary draws absent, which the audit rejected.
#
# No direction is claimed.  V4 asserted that omitting the covariance always
# understates the uncertainty; its own ratios contradicted that, and the
# assertion is removed.
