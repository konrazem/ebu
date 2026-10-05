"""Realized-field qualification, policy ``E1A-T11a-RF-v1``: Layer K.

Implements T-stage section 22.6 exactly.  These predicates judge whether the
*realized* physical field retained enough of its preregistered challenge; they
are entirely separate from the 5% absolute and 2% cross-field beta bands,
which judge bridge agreement.  A target miss is an experimental-role
invalidity, never evidence against beta = 1.

Every predicate is evaluated over a certified enclosure of the joint 99.9%
physical calibration region, not at a nominal point: containment gives VALID,
certified disjointness gives OUT_OF_SPEC, and a straddling enclosure gives
UNRESOLVED.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence

from . import numerics as nm
from .numerics import Matrix, NumericalFailure
from .refusals import (
    FIELD_REALIZATION_OUT_OF_SPEC,
    FIELD_REALIZATION_SPECIFICATION_MISSING,
    FIELD_REALIZATION_UNRESOLVED,
    FIELD_REALIZATION_VALID,
    Refusal,
    refuse,
)

#: The only realisation-policy version this module implements.
POLICY_VERSION = "E1A-T11a-RF-v1"

# --- fixed constants, T-stage section 22.6 --------------------------------
#: Nominal temperature log challenge, log(318/298).
C_T_STAR = math.log(318.0 / 298.0)
#: Retention band multipliers.
RETENTION_LO = 0.90
RETENTION_HI = 1.10
#: Nominal stiffness log challenge, log(2.1).
LOG_K_STAR = math.log(2.1)
#: Cross-field margin and fixed residual allowance used by the planning screen.
DELTA_C = math.log(1.02)
RESIDUAL_ALLOWANCE = 0.001
#: Fixed worst-case cross-field planning standard error at N_* = 450000.
S_C = math.sqrt(0.003 ** 2 + 2.205 / 450000.0)
#: The 47-test first-step critical value, fixed by T.
Z_FIRST_STEP = 3.273078364
#: Required minimum planning detection probability.
PLAN_POWER_MIN = 0.90
#: Nominal reference and ellipse stiffness matrices, micro N/m (T.R7).
K0_STAR_UNM = [[100.0, 0.0], [0.0, 100.0]]
_R30 = [
    [math.cos(math.pi / 6.0), -math.sin(math.pi / 6.0)],
    [math.sin(math.pi / 6.0), math.cos(math.pi / 6.0)],
]
K2_STAR_UNM = nm.symmetrise(
    nm.matmul(nm.matmul(_R30, [[150.0, 0.0], [0.0, 60.0]]), nm.transpose(_R30))
)
#: ``L_2^* = log[(K_0^*)^{-1/2} K_2^* (K_0^*)^{-1/2}]``.
L2_STAR = nm.log_generalized_contrast(K2_STAR_UNM, K0_STAR_UNM)
#: Ellipse tolerance: the 10%-of-nominal-challenge ball, 0.10 * |log 0.6|.
EPSILON_2 = 0.10 * abs(math.log(0.6))

# Realisation statuses.
VALID = FIELD_REALIZATION_VALID
UNRESOLVED = FIELD_REALIZATION_UNRESOLVED
OUT_OF_SPEC = FIELD_REALIZATION_OUT_OF_SPEC
SPECIFICATION_MISSING = FIELD_REALIZATION_SPECIFICATION_MISSING


@dataclass(frozen=True)
class Enclosure:
    """A certified scalar enclosure ``[lo, hi]`` over the joint region."""

    lo: float
    hi: float
    #: How the enclosure was certified; a bare grid is not a certificate.
    certificate: str = "unspecified"

    def __post_init__(self) -> None:
        if not (math.isfinite(self.lo) and math.isfinite(self.hi)):
            raise NumericalFailure("enclosure bounds must be finite")
        if self.lo > self.hi:
            raise NumericalFailure(f"enclosure lo {self.lo!r} exceeds hi {self.hi!r}")

    @property
    def certified(self) -> bool:
        return self.certificate not in ("unspecified", "grid")

    def inside(self, lo: float, hi: float) -> bool:
        """Whole enclosure within the inclusive band."""
        return lo <= self.lo and self.hi <= hi

    def disjoint(self, lo: float, hi: float) -> bool:
        """Whole enclosure certified outside the inclusive band."""
        return self.hi < lo or self.lo > hi

    @staticmethod
    def point(x: float, certificate: str = "exact_point") -> "Enclosure":
        return Enclosure(x, x, certificate)


def classify(encl: Enclosure, lo: float, hi: float) -> str:
    """Classify an enclosure against an inclusive band.

    Boundaries are inclusive (T-stage 22.6.1).  An uncertified enclosure can
    never produce VALID: certified containment is required.
    """
    if not encl.certified:
        return UNRESOLVED
    if encl.inside(lo, hi):
        return VALID
    if encl.disjoint(lo, hi):
        return OUT_OF_SPEC
    return UNRESOLVED


# ---------------------------------------------------------------------------
# Planning detection screen, T.R3 / T.R4
# ---------------------------------------------------------------------------

def planning_detection(h: float) -> float:
    """``P(h) = Phi[(h - log 1.02 - 0.001)/s_c - 3.273078364]`` (T.R3)."""
    return nm.norm_cdf((h - DELTA_C - RESIDUAL_ALLOWANCE) / S_C - Z_FIRST_STEP)


def planning_detection_threshold() -> float:
    """``h_90`` from (T.R4); the scalar planning boundary."""
    return DELTA_C + RESIDUAL_ALLOWANCE + S_C * (Z_FIRST_STEP + nm.norm_ppf(PLAN_POWER_MIN))


H90 = planning_detection_threshold()


# ---------------------------------------------------------------------------
# T.R2 temperature challenge
# ---------------------------------------------------------------------------

def temperature_log_challenge(t_hot: float, t_ref: float) -> float:
    """``c_T = log(T_hot / T_ref)`` with fixed field labels, never an absolute value."""
    if t_hot <= 0.0 or t_ref <= 0.0:
        raise NumericalFailure("temperatures must be strictly positive")
    return math.log(t_hot / t_ref)


def temperature_band() -> tuple[float, float]:
    return RETENTION_LO * C_T_STAR, RETENTION_HI * C_T_STAR


@dataclass(frozen=True)
class RealizationOutcome:
    status: str
    retained_fraction: float | None
    worst_case_challenge: float | None
    worst_case_planning_detection: float | None
    detail: dict
    refusal: Refusal | None = None


def qualify_temperature_field(
    challenge: Enclosure, policy_version: str = POLICY_VERSION
) -> RealizationOutcome:
    """Qualify theta3 under (T.R2) retention and (T.R3)/(T.R6) planning power."""
    if policy_version != POLICY_VERSION:
        return RealizationOutcome(
            SPECIFICATION_MISSING, None, None, None,
            {"expected": POLICY_VERSION, "received": policy_version},
            refuse(
                FIELD_REALIZATION_SPECIFICATION_MISSING,
                f"policy_version == {POLICY_VERSION}",
                "realisation policy version absent or mismatched",
                received=policy_version,
            ),
        )
    lo, hi = temperature_band()
    status = classify(challenge, lo, hi)
    # Worst case over the enclosure: the challenge closest to zero effect.
    worst = min(abs(challenge.lo), abs(challenge.hi)) if challenge.lo * challenge.hi > 0 else 0.0
    worst_signed = challenge.lo if challenge.lo >= 0 else challenge.hi
    worst_eff = worst if challenge.lo > 0 else worst_signed
    power = planning_detection(challenge.lo if challenge.lo > 0 else worst_eff)
    if status == VALID and power < PLAN_POWER_MIN:
        status = OUT_OF_SPEC
    detail = {
        "band": [lo, hi],
        "enclosure": [challenge.lo, challenge.hi],
        "certificate": challenge.certificate,
        "nominal_log_challenge": C_T_STAR,
        "h90": H90,
    }
    retained = (challenge.lo / C_T_STAR) if C_T_STAR != 0 else None
    refusal = None
    if status != VALID:
        code = {
            UNRESOLVED: FIELD_REALIZATION_UNRESOLVED,
            OUT_OF_SPEC: FIELD_REALIZATION_OUT_OF_SPEC,
        }[status]
        refusal = refuse(
            code,
            f"{lo} <= c_T <= {hi} and P_plan >= {PLAN_POWER_MIN}",
            "realized temperature challenge failed (T.R2)/(T.R3)",
            **detail,
        )
    return RealizationOutcome(status, retained, challenge.lo, power, detail, refusal)


# ---------------------------------------------------------------------------
# T.R5 / T.R6 stiffness challenge: both generalized modes
# ---------------------------------------------------------------------------

def stiffness_log_modes(k1: Matrix, k0: Matrix) -> tuple[float, float]:
    """``c_k,r = log lambda_r(K_0^{-1/2} K_1 K_0^{-1/2})`` for both modes."""
    lam = nm.generalized_eigvals_spd(nm.symmetrise(k1), nm.symmetrise(k0))
    if any((not math.isfinite(v)) or v <= 0.0 for v in lam):
        raise NumericalFailure("generalised stiffness eigenvalues must be positive")
    return tuple(math.log(v) for v in lam)  # type: ignore[return-value]


def stiffness_band() -> tuple[float, float]:
    return RETENTION_LO * LOG_K_STAR, RETENTION_HI * LOG_K_STAR


def qualify_stiffness_field(
    mode_enclosures: Sequence[Enclosure], policy_version: str = POLICY_VERSION
) -> RealizationOutcome:
    """Qualify theta1: BOTH generalized modes must satisfy (T.R5); no scalar average."""
    if policy_version != POLICY_VERSION:
        return RealizationOutcome(
            SPECIFICATION_MISSING, None, None, None,
            {"expected": POLICY_VERSION, "received": policy_version},
            refuse(
                FIELD_REALIZATION_SPECIFICATION_MISSING,
                f"policy_version == {POLICY_VERSION}",
                "realisation policy version absent or mismatched",
                received=policy_version,
            ),
        )
    if len(mode_enclosures) != 2:
        return RealizationOutcome(
            UNRESOLVED, None, None, None, {"n_modes": len(mode_enclosures)},
            refuse(
                FIELD_REALIZATION_UNRESOLVED,
                "two generalized modes supplied",
                "both generalized modes are required; a scalar average cannot replace either",
            ),
        )
    lo, hi = stiffness_band()
    statuses = [classify(e, lo, hi) for e in mode_enclosures]
    if OUT_OF_SPEC in statuses:
        status = OUT_OF_SPEC
    elif UNRESOLVED in statuses:
        status = UNRESOLVED
    else:
        status = VALID
    # (T.R6): conservative scalar strength is the LEAST mode effect.
    h_k = min(e.lo for e in mode_enclosures)
    power = planning_detection(h_k)
    if status == VALID and power < PLAN_POWER_MIN:
        status = OUT_OF_SPEC
    detail = {
        "band": [lo, hi],
        "mode_enclosures": [[e.lo, e.hi] for e in mode_enclosures],
        "mode_statuses": statuses,
        "least_mode_effect": h_k,
        "nominal_log_challenge": LOG_K_STAR,
    }
    refusal = None
    if status != VALID:
        code = {
            UNRESOLVED: FIELD_REALIZATION_UNRESOLVED,
            OUT_OF_SPEC: FIELD_REALIZATION_OUT_OF_SPEC,
        }[status]
        refusal = refuse(
            code,
            f"{lo} <= c_k,r <= {hi} for BOTH modes and P_plan >= {PLAN_POWER_MIN}",
            "realized stiffness challenge failed (T.R5)/(T.R6)",
            **detail,
        )
    retained = h_k / LOG_K_STAR if LOG_K_STAR != 0 else None
    return RealizationOutcome(status, retained, h_k, power, detail, refusal)


# ---------------------------------------------------------------------------
# T.R7 / T.R8 ellipse: full-matrix target conformity
# ---------------------------------------------------------------------------

def ellipse_log_contrast(k2: Matrix, k0: Matrix) -> Matrix:
    """``L_2 = log[K_0^{-1/2} K_2 K_0^{-1/2}]``, the symmetric whitened log contrast."""
    return nm.log_generalized_contrast(nm.symmetrise(k2), nm.symmetrise(k0))


def ellipse_distance(k2: Matrix, k0: Matrix, l2_star: Matrix | None = None) -> float:
    """``||L_2 - L_2^*||_op``, the full-matrix target departure."""
    target = L2_STAR if l2_star is None else l2_star
    return nm.op_norm_sym(nm.sub(ellipse_log_contrast(k2, k0), target))


def qualify_ellipse_field(
    distance: Enclosure, policy_version: str = POLICY_VERSION
) -> RealizationOutcome:
    """Qualify theta2 under (T.R8): ``sup ||L_2 - L_2^*||_op <= epsilon_2``."""
    if policy_version != POLICY_VERSION:
        return RealizationOutcome(
            SPECIFICATION_MISSING, None, None, None,
            {"expected": POLICY_VERSION, "received": policy_version},
            refuse(
                FIELD_REALIZATION_SPECIFICATION_MISSING,
                f"policy_version == {POLICY_VERSION}",
                "realisation policy version absent or mismatched",
                received=policy_version,
            ),
        )
    status = classify(distance, 0.0, EPSILON_2)
    detail = {
        "epsilon_2": EPSILON_2,
        "enclosure": [distance.lo, distance.hi],
        "certificate": distance.certificate,
    }
    refusal = None
    if status != VALID:
        code = {
            UNRESOLVED: FIELD_REALIZATION_UNRESOLVED,
            OUT_OF_SPEC: FIELD_REALIZATION_OUT_OF_SPEC,
        }[status]
        refusal = refuse(
            code,
            f"||L_2 - L_2*||_op <= {EPSILON_2}",
            "realized ellipse target conformity failed (T.R8)",
            **detail,
        )
    # theta2 carries no scalar 0.90 detection screen (T-stage 22.6.4).
    return RealizationOutcome(status, None, distance.hi, None, detail, refusal)
