"""Branch-A calibration packet validation: Layer B of the V-stage pipeline.

Implements the cleared positive-primitive rule separately for ``eta``, ``a``
and ``T`` (old F2 closure, U-stage section 16.1 / section 32), then validates
the derived drag, relaxation and curvature quantities separately.

A positive *product* never rescues invalid primitives: two negative primitives
whose product is positive are refused at the primitive stage.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence

from . import numerics as nm
from .numerics import Matrix, NumericalFailure
from .refusals import (
    HYDRODYNAMIC_MODEL_UNQUALIFIED,
    INSUFFICIENT_GEOMETRY_CALIBRATION,
    NUMERICAL_REPRESENTATION_FAILURE,
    PRIMITIVE_PHYSICALLY_INVALID,
    THERMOMETRY_UNQUALIFIED,
    Refusal,
    refuse,
)
from .units import K_B

# ---------------------------------------------------------------------------
# Declared physical calibration domains (prospective, V-stage candidate).
# These are domain declarations, not measured apparatus capabilities.
# ---------------------------------------------------------------------------

#: Dynamic viscosity domain for the qualified aqueous buffer, Pa.s.
ETA_DOMAIN = (1.0e-5, 1.0e0)
#: Bead radius domain, m.
RADIUS_DOMAIN = (1.0e-8, 1.0e-4)
#: Local reservoir temperature domain, K.
TEMPERATURE_DOMAIN = (2.0e2, 4.0e2)
#: Derived lateral stiffness domain, N/m.
STIFFNESS_DOMAIN = (1.0e-9, 1.0e-1)
#: Derived relaxation-time domain, s.
TAU_DOMAIN = (1.0e-9, 1.0e2)
#: T-stage section 11 conditioning limit on the normalised Hessian.
CONDITION_LIMIT = 100.0


@dataclass(frozen=True)
class PrimitiveCheck:
    """Outcome of validating one scalar primitive."""

    name: str
    value: float
    ok: bool
    refusal: Refusal | None = None


def check_positive_primitive(
    name: str,
    value: object,
    domain: tuple[float, float],
    code: str = PRIMITIVE_PHYSICALLY_INVALID,
) -> PrimitiveCheck:
    """Validate one primitive as numeric, finite, strictly positive and in domain.

    Each condition is checked and reported separately: a missing value, an
    inadmissible value and a numerical representation failure retain distinct
    meanings (U-stage section 16.1).
    """
    if value is None:
        return PrimitiveCheck(
            name,
            float("nan"),
            False,
            refuse(code, f"{name} present", f"{name} is absent", primitive=name),
        )
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return PrimitiveCheck(
            name,
            float("nan"),
            False,
            refuse(
                code,
                f"{name} numeric",
                f"{name} is not a real number",
                primitive=name,
                received=repr(value),
            ),
        )
    v = float(value)
    if math.isnan(v):
        return PrimitiveCheck(
            name, v, False,
            refuse(code, f"{name} not NaN", f"{name} is NaN", primitive=name),
        )
    if math.isinf(v):
        return PrimitiveCheck(
            name, v, False,
            refuse(code, f"{name} finite", f"{name} is infinite", primitive=name, value=v),
        )
    if v <= 0.0:
        return PrimitiveCheck(
            name, v, False,
            refuse(
                code,
                f"{name} > 0",
                f"{name} is not strictly positive",
                primitive=name,
                value=v,
            ),
        )
    lo, hi = domain
    if not (lo <= v <= hi):
        return PrimitiveCheck(
            name, v, False,
            refuse(
                code,
                f"{lo} <= {name} <= {hi}",
                f"{name} outside the declared physical calibration domain",
                primitive=name,
                value=v,
                domain=[lo, hi],
            ),
        )
    return PrimitiveCheck(name, v, True)


@dataclass(frozen=True)
class DerivedDrag:
    """Derived hydrodynamic and relaxation quantities."""

    gamma_scalar: float
    gamma_tensor: Matrix
    tau: tuple[float, ...]
    refusals: tuple[Refusal, ...] = ()

    @property
    def ok(self) -> bool:
        return not self.refusals


def validate_primitives(
    eta: object, radius: object, temperature: object
) -> tuple[tuple[PrimitiveCheck, ...], tuple[Refusal, ...]]:
    """Validate ``eta``, ``a`` and ``T`` separately (old F2 rule).

    Returns every check so a caller can report all failing primitives, not only
    the first.
    """
    checks = (
        check_positive_primitive("eta", eta, ETA_DOMAIN),
        check_positive_primitive("a", radius, RADIUS_DOMAIN),
        check_positive_primitive(
            "T", temperature, TEMPERATURE_DOMAIN, code=THERMOMETRY_UNQUALIFIED
        ),
    )
    refusals = tuple(c.refusal for c in checks if c.refusal is not None)
    return checks, refusals


def stokes_drag(
    eta: float, radius: float, wall_correction: float = 1.0
) -> tuple[float, tuple[Refusal, ...]]:
    """Scalar Stokes drag ``6 pi eta a`` with an optional wall correction.

    Underflow of the product to zero, overflow to infinity, or a non-finite
    wall correction are structured refusals, never silently clipped.
    """
    refusals: list[Refusal] = []
    if not math.isfinite(wall_correction) or wall_correction <= 0.0:
        refusals.append(
            refuse(
                HYDRODYNAMIC_MODEL_UNQUALIFIED,
                "wall_correction > 0 and finite",
                "wall/chamber correction is not a positive finite factor",
                value=wall_correction,
            )
        )
        return float("nan"), tuple(refusals)
    product = eta * radius
    if product == 0.0:
        refusals.append(
            refuse(
                NUMERICAL_REPRESENTATION_FAILURE,
                "eta * a != 0",
                "eta * a underflowed to zero in double precision",
                eta=eta,
                radius=radius,
            )
        )
        return float("nan"), tuple(refusals)
    gamma = 6.0 * math.pi * product * wall_correction
    if not math.isfinite(gamma):
        refusals.append(
            refuse(
                NUMERICAL_REPRESENTATION_FAILURE,
                "gamma finite",
                "derived drag coefficient is not finite",
                eta=eta,
                radius=radius,
                gamma=gamma,
            )
        )
        return float("nan"), tuple(refusals)
    if gamma <= 0.0:
        refusals.append(
            refuse(
                NUMERICAL_REPRESENTATION_FAILURE,
                "gamma > 0",
                "derived drag coefficient is not strictly positive",
                gamma=gamma,
            )
        )
        return float("nan"), tuple(refusals)
    return gamma, ()


def resistance_tensor(
    gamma_scalar: float, anisotropy: Sequence[float] | None = None
) -> tuple[Matrix, tuple[Refusal, ...]]:
    """Build the full 3-by-3 resistance tensor from the scalar drag.

    ``anisotropy`` supplies per-axis multipliers (for example a wall-induced
    axial enhancement).  Every entry must be finite and strictly positive.
    """
    f = [1.0, 1.0, 1.0] if anisotropy is None else [float(v) for v in anisotropy]
    if len(f) != 3:
        return [], (
            refuse(
                HYDRODYNAMIC_MODEL_UNQUALIFIED,
                "len(anisotropy) == 3",
                "resistance anisotropy must have three axis factors",
            ),
        )
    for i, v in enumerate(f):
        if not math.isfinite(v) or v <= 0.0:
            return [], (
                refuse(
                    HYDRODYNAMIC_MODEL_UNQUALIFIED,
                    "anisotropy > 0 and finite",
                    "resistance anisotropy factor is invalid",
                    axis=i,
                    value=v,
                ),
            )
    g = nm.zeros(3)
    for i in range(3):
        g[i][i] = gamma_scalar * f[i]
        if not math.isfinite(g[i][i]) or g[i][i] <= 0.0:
            return [], (
                refuse(
                    NUMERICAL_REPRESENTATION_FAILURE,
                    "Gamma entries finite and positive",
                    "resistance tensor entry is not finite and positive",
                    axis=i,
                    value=g[i][i],
                ),
            )
    return g, ()


def relaxation_times(
    gamma_tensor: Matrix, stiffness: Matrix
) -> tuple[tuple[float, ...], tuple[Refusal, ...]]:
    """Relaxation times from the generalised pencil ``(Gamma, K)``.

    ``tau_r`` are the reciprocals of the generalised eigenvalues of
    ``(K, Gamma)``; zero or infinite values are refused.
    """
    try:
        lam = nm.generalized_eigvals_spd(nm.symmetrise(stiffness), nm.symmetrise(gamma_tensor))
    except NumericalFailure as exc:
        return (), (
            refuse(
                NUMERICAL_REPRESENTATION_FAILURE,
                "generalised eigenvalues of (K, Gamma) computable",
                str(exc),
            ),
        )
    taus: list[float] = []
    for i, v in enumerate(lam):
        if not math.isfinite(v) or v <= 0.0:
            return (), (
                refuse(
                    NUMERICAL_REPRESENTATION_FAILURE,
                    "generalised eigenvalue > 0",
                    "relaxation rate is not finite and positive",
                    mode=i,
                    value=v,
                ),
            )
        t = 1.0 / v
        if not math.isfinite(t) or t <= 0.0:
            return (), (
                refuse(
                    NUMERICAL_REPRESENTATION_FAILURE,
                    "tau finite and positive",
                    "relaxation time is zero, infinite or non-finite",
                    mode=i,
                    value=t,
                ),
            )
        lo, hi = TAU_DOMAIN
        if not (lo <= t <= hi):
            return (), (
                refuse(
                    HYDRODYNAMIC_MODEL_UNQUALIFIED,
                    f"{lo} <= tau <= {hi}",
                    "relaxation time outside the declared domain",
                    mode=i,
                    value=t,
                    domain=[lo, hi],
                ),
            )
        taus.append(t)
    return tuple(sorted(taus)), ()


def normalised_hessian(
    stiffness: Matrix, temperature: float
) -> tuple[Matrix, tuple[Refusal, ...]]:
    """Return ``H = K / (k_B T)`` with overflow and conditioning defence."""
    kbt = K_B * temperature
    if not math.isfinite(kbt) or kbt <= 0.0:
        return [], (
            refuse(
                THERMOMETRY_UNQUALIFIED,
                "k_B T > 0 and finite",
                "thermal energy is not finite and positive",
                temperature=temperature,
            ),
        )
    n = len(stiffness)
    h = nm.zeros(n)
    for i in range(n):
        for j in range(n):
            v = stiffness[i][j] / kbt
            if not math.isfinite(v):
                return [], (
                    refuse(
                        NUMERICAL_REPRESENTATION_FAILURE,
                        "H entries finite",
                        "normalised Hessian entry overflowed or is not finite",
                        row=i,
                        col=j,
                        value=v,
                    ),
                )
            h[i][j] = v
    h = nm.symmetrise(h)
    try:
        nm.cholesky(h)
    except NumericalFailure as exc:
        return [], (
            refuse(
                INSUFFICIENT_GEOMETRY_CALIBRATION,
                "H SPD",
                f"normalised Hessian is not positive definite: {exc}",
            ),
        )
    try:
        kappa = nm.cond2_spd(h)
    except NumericalFailure as exc:
        return [], (
            refuse(NUMERICAL_REPRESENTATION_FAILURE, "cond2(H) computable", str(exc)),
        )
    if not math.isfinite(kappa) or kappa > CONDITION_LIMIT:
        return [], (
            refuse(
                INSUFFICIENT_GEOMETRY_CALIBRATION,
                f"cond2(H) <= {CONDITION_LIMIT}",
                "normalised Hessian exceeds the conditioning limit",
                condition_number=kappa,
            ),
        )
    return h, ()


def validate_branch_a_primitives(
    eta: object,
    radius: object,
    temperature: object,
    stiffness_3d: Matrix | None = None,
    wall_correction: float = 1.0,
    anisotropy: Sequence[float] | None = None,
) -> tuple[DerivedDrag | None, tuple[Refusal, ...]]:
    """Full primitive-then-derived validation chain.

    Primitives are validated first and independently; derived quantities are
    computed only once every primitive has passed, so a derived value can never
    mask an invalid primitive.
    """
    _, prim_refusals = validate_primitives(eta, radius, temperature)
    if prim_refusals:
        return None, prim_refusals

    eta_f, a_f, t_f = float(eta), float(radius), float(temperature)  # type: ignore[arg-type]
    gamma, g_ref = stokes_drag(eta_f, a_f, wall_correction)
    if g_ref:
        return None, g_ref
    tensor, t_ref = resistance_tensor(gamma, anisotropy)
    if t_ref:
        return None, t_ref

    taus: tuple[float, ...] = ()
    if stiffness_3d is not None:
        taus, tau_ref = relaxation_times(tensor, stiffness_3d)
        if tau_ref:
            return None, tau_ref

    return DerivedDrag(gamma_scalar=gamma, gamma_tensor=tensor, tau=taus), ()
