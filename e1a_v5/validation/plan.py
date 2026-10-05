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

#: Information target per cell (T.23).
N_STAR = 450000
I_STAR = 408164

#: Calibration standard uncertainties used by the synthetic auxiliary law.
SIGMA_CAL_ABSOLUTE = 0.0060
SIGMA_CAL_CELL = 0.0015
#: Certified bounded systematic log-beta contribution per cell.
BIAS_PER_CELL = 0.00025


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


def timing(k_eff: list[list[float]]) -> tuple[float, float]:
    """Return ``(dt, t_exp)`` from the bandwidth and exposure ceilings."""
    gamma = drag_coefficient()
    vals, _ = nm.eigh(k_eff)
    k_fast = max(vals)
    k_slow = min(vals)
    tau_fast = gamma / k_fast
    rate_fast = 1.0 / tau_fast
    dt = BANDWIDTH_FRACTION * 0.2 / rate_fast
    t_exp = EXPOSURE_FRACTION * tau_fast
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
