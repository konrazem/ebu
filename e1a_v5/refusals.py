"""Structured refusal codes for the E1a v5 candidate pipeline.

Every failure path returns a :class:`Refusal` carrying a code, the failing
predicate, and the dependency reason.  A bare boolean is never sufficient
(U-stage section 28).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

# ---------------------------------------------------------------------------
# U-stage section 28 reason families, verbatim code names.
# ---------------------------------------------------------------------------
INCOMPLETE_INPUT = "INCOMPLETE_INPUT"
MISSING_PROVENANCE = "MISSING_PROVENANCE"
MISSING_COVARIANCE = "MISSING_COVARIANCE"
PRIMITIVE_PHYSICALLY_INVALID = "PRIMITIVE_PHYSICALLY_INVALID"
NUMERICAL_REPRESENTATION_FAILURE = "NUMERICAL_REPRESENTATION_FAILURE"
HYDRODYNAMIC_MODEL_UNQUALIFIED = "HYDRODYNAMIC_MODEL_UNQUALIFIED"
TEMPORAL_MODEL_UNQUALIFIED = "TEMPORAL_MODEL_UNQUALIFIED"
THERMOMETRY_UNQUALIFIED = "THERMOMETRY_UNQUALIFIED"
RESERVOIR_UNQUALIFIED = "RESERVOIR_UNQUALIFIED"
HARMONIC_DOMAIN_UNQUALIFIED = "HARMONIC_DOMAIN_UNQUALIFIED"
NONCONSERVATIVE_FORCE = "NONCONSERVATIVE_FORCE"
INSUFFICIENT_GEOMETRY_CALIBRATION = "INSUFFICIENT_GEOMETRY_CALIBRATION"
OBSERVATION_MODEL_UNQUALIFIED = "OBSERVATION_MODEL_UNQUALIFIED"
CALIBRATION_UNCERTAINTY_EXCESS = "CALIBRATION_UNCERTAINTY_EXCESS"
AXIAL_REDUCTION_UNQUALIFIED = "AXIAL_REDUCTION_UNQUALIFIED"
FIELD_REALIZATION_SPECIFICATION_MISSING = "FIELD_REALIZATION_SPECIFICATION_MISSING"
FIELD_REALIZATION_UNRESOLVED = "FIELD_REALIZATION_UNRESOLVED"
FIELD_REALIZATION_OUT_OF_SPEC = "FIELD_REALIZATION_OUT_OF_SPEC"
FIELD_REALIZATION_VALID = "FIELD_REALIZATION_VALID"
T11_UNQUALIFIED = "T11_UNQUALIFIED"
INVALID_RECORD_MONITOR = "INVALID_RECORD_MONITOR"
VALID = "VALID"

# Computation outcome used by the verdict engine (T-stage section 21).
COMPUTATION_NOT_EVALUABLE = "COMPUTATION_NOT_EVALUABLE"
UNIT_INCONSISTENT = "UNIT_INCONSISTENT"

ALL_CODES = frozenset(
    {
        INCOMPLETE_INPUT,
        MISSING_PROVENANCE,
        MISSING_COVARIANCE,
        PRIMITIVE_PHYSICALLY_INVALID,
        NUMERICAL_REPRESENTATION_FAILURE,
        HYDRODYNAMIC_MODEL_UNQUALIFIED,
        TEMPORAL_MODEL_UNQUALIFIED,
        THERMOMETRY_UNQUALIFIED,
        RESERVOIR_UNQUALIFIED,
        HARMONIC_DOMAIN_UNQUALIFIED,
        NONCONSERVATIVE_FORCE,
        INSUFFICIENT_GEOMETRY_CALIBRATION,
        OBSERVATION_MODEL_UNQUALIFIED,
        CALIBRATION_UNCERTAINTY_EXCESS,
        AXIAL_REDUCTION_UNQUALIFIED,
        FIELD_REALIZATION_SPECIFICATION_MISSING,
        FIELD_REALIZATION_UNRESOLVED,
        FIELD_REALIZATION_OUT_OF_SPEC,
        FIELD_REALIZATION_VALID,
        T11_UNQUALIFIED,
        INVALID_RECORD_MONITOR,
        VALID,
        COMPUTATION_NOT_EVALUABLE,
        UNIT_INCONSISTENT,
    }
)

#: Codes that classify as a demonstrated model/domain breach.
INVALID_FAMILY = frozenset(
    {
        PRIMITIVE_PHYSICALLY_INVALID,
        HYDRODYNAMIC_MODEL_UNQUALIFIED,
        TEMPORAL_MODEL_UNQUALIFIED,
        THERMOMETRY_UNQUALIFIED,
        RESERVOIR_UNQUALIFIED,
        HARMONIC_DOMAIN_UNQUALIFIED,
        NONCONSERVATIVE_FORCE,
        OBSERVATION_MODEL_UNQUALIFIED,
        FIELD_REALIZATION_OUT_OF_SPEC,
        INVALID_RECORD_MONITOR,
        UNIT_INCONSISTENT,
    }
)

#: Codes that classify as insufficient precision / unresolved certificate.
INCONCLUSIVE_FAMILY = frozenset(
    {
        INSUFFICIENT_GEOMETRY_CALIBRATION,
        CALIBRATION_UNCERTAINTY_EXCESS,
        FIELD_REALIZATION_UNRESOLVED,
        T11_UNQUALIFIED,
    }
)

#: Codes that classify as absent inputs.
INCOMPLETE_FAMILY = frozenset(
    {
        INCOMPLETE_INPUT,
        MISSING_PROVENANCE,
        MISSING_COVARIANCE,
        FIELD_REALIZATION_SPECIFICATION_MISSING,
    }
)

#: Codes that classify as a numerical / computational failure.
NUMERICAL_FAMILY = frozenset(
    {NUMERICAL_REPRESENTATION_FAILURE, COMPUTATION_NOT_EVALUABLE}
)


class RefusalError(Exception):
    """Raised only where a caller explicitly opts into exception control flow."""

    def __init__(self, refusal: "Refusal") -> None:
        super().__init__(f"{refusal.code}: {refusal.predicate}")
        self.refusal = refusal


@dataclass(frozen=True)
class Refusal:
    """A structured refusal.

    Attributes
    ----------
    code:
        One of the U-stage section 28 reason families.
    predicate:
        The exact failing predicate, as a short machine-stable string.
    reason:
        Human-readable dependency reason.
    detail:
        Measured value, allowed domain, affected fields and references.
    """

    code: str
    predicate: str
    reason: str = ""
    detail: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.code not in ALL_CODES:
            raise ValueError(f"unknown refusal code {self.code!r}")

    @property
    def family(self) -> str:
        if self.code in INVALID_FAMILY:
            return "INVALID"
        if self.code in INCONCLUSIVE_FAMILY:
            return "INCONCLUSIVE"
        if self.code in INCOMPLETE_FAMILY:
            return "INCOMPLETE"
        if self.code in NUMERICAL_FAMILY:
            return "NUMERICAL"
        return "VALID"

    def as_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "predicate": self.predicate,
            "reason": self.reason,
            "family": self.family,
            "detail": dict(self.detail),
        }

    def __str__(self) -> str:  # pragma: no cover - display only
        return f"{self.code}({self.predicate})"


def refuse(code: str, predicate: str, reason: str = "", **detail: Any) -> Refusal:
    """Convenience constructor."""
    return Refusal(code=code, predicate=predicate, reason=reason, detail=detail)
