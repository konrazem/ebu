"""Unit safety for the E1a v5 candidate implementation.

Every externally supplied physical primitive carries an explicit unit string.
Values are converted once, at the boundary, into a canonical SI internal
representation.  A unit that is unknown, dimensionally wrong, or absent is a
closed failure (:class:`UnitError`), never a silent pass-through.

This exists to prevent the three specific confusions named in the authorising
brief: micrometre/metre, mPa*s / Pa*s, and microN/m / N/m.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

#: Boltzmann constant, exact SI definition (2019 redefinition), J/K.
K_B = 1.380649e-23


class UnitError(Exception):
    """A unit was unknown, absent, or dimensionally inconsistent."""


# dimension vector: (length, mass, time, temperature)
Dimension = tuple[int, int, int, int]

LENGTH: Dimension = (1, 0, 0, 0)
MASS: Dimension = (0, 1, 0, 0)
TIME: Dimension = (0, 0, 1, 0)
TEMPERATURE: Dimension = (0, 0, 0, 1)
VELOCITY: Dimension = (1, 0, -1, 0)
FORCE: Dimension = (1, 1, -2, 0)
STIFFNESS: Dimension = (0, 1, -2, 0)
VISCOSITY: Dimension = (-1, 1, -1, 0)
DIMENSIONLESS: Dimension = (0, 0, 0, 0)

DIMENSION_NAMES: dict[Dimension, str] = {
    LENGTH: "length",
    MASS: "mass",
    TIME: "time",
    TEMPERATURE: "temperature",
    VELOCITY: "velocity",
    FORCE: "force",
    STIFFNESS: "stiffness",
    VISCOSITY: "viscosity",
    DIMENSIONLESS: "dimensionless",
}

#: Unit string -> (SI factor, dimension).  Deliberately explicit and closed.
UNIT_TABLE: dict[str, tuple[float, Dimension]] = {
    # length
    "m": (1.0, LENGTH),
    "mm": (1e-3, LENGTH),
    "um": (1e-6, LENGTH),
    "micrometre": (1e-6, LENGTH),
    "nm": (1e-9, LENGTH),
    # time
    "s": (1.0, TIME),
    "ms": (1e-3, TIME),
    "us": (1e-6, TIME),
    # temperature
    "K": (1.0, TEMPERATURE),
    # velocity
    "m/s": (1.0, VELOCITY),
    "um/s": (1e-6, VELOCITY),
    "mm/s": (1e-3, VELOCITY),
    # force
    "N": (1.0, FORCE),
    "mN": (1e-3, FORCE),
    "uN": (1e-6, FORCE),
    "nN": (1e-9, FORCE),
    "pN": (1e-12, FORCE),
    # stiffness
    "N/m": (1.0, STIFFNESS),
    "mN/m": (1e-3, STIFFNESS),
    "uN/m": (1e-6, STIFFNESS),
    "pN/um": (1e-6, STIFFNESS),
    "pN/nm": (1e-3, STIFFNESS),
    # dynamic viscosity
    "Pa.s": (1.0, VISCOSITY),
    "Pa*s": (1.0, VISCOSITY),
    "mPa.s": (1e-3, VISCOSITY),
    "mPa*s": (1e-3, VISCOSITY),
    "uPa.s": (1e-6, VISCOSITY),
    # dimensionless
    "1": (1.0, DIMENSIONLESS),
    "": (1.0, DIMENSIONLESS),
}


@dataclass(frozen=True)
class Quantity:
    """A value in canonical SI with its dimension recorded."""

    value: float
    dimension: Dimension
    source_unit: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, float):
            object.__setattr__(self, "value", float(self.value))

    @property
    def dimension_name(self) -> str:
        return DIMENSION_NAMES.get(self.dimension, str(self.dimension))

    def require(self, dimension: Dimension) -> float:
        if self.dimension != dimension:
            raise UnitError(
                f"expected {DIMENSION_NAMES.get(dimension, dimension)}, "
                f"got {self.dimension_name} (from unit {self.source_unit!r})"
            )
        return self.value


def to_si(value: float, unit: str, expected: Dimension | None = None) -> float:
    """Convert ``value`` given in ``unit`` into canonical SI.

    Fails closed on a non-finite value, an unknown unit string, or a dimension
    that does not match ``expected``.
    """
    if unit is None:
        raise UnitError("unit is required; an absent unit is not assumed SI")
    if unit not in UNIT_TABLE:
        raise UnitError(f"unknown unit {unit!r}; units must be declared explicitly")
    try:
        v = float(value)
    except (TypeError, ValueError) as exc:
        raise UnitError(f"value {value!r} is not numeric") from exc
    if not math.isfinite(v):
        raise UnitError(f"value {value!r} is not finite")
    factor, dim = UNIT_TABLE[unit]
    if expected is not None and dim != expected:
        raise UnitError(
            f"unit {unit!r} has dimension {DIMENSION_NAMES.get(dim, dim)}, "
            f"expected {DIMENSION_NAMES.get(expected, expected)}"
        )
    return v * factor


def quantity(value: float, unit: str, expected: Dimension | None = None) -> Quantity:
    si = to_si(value, unit, expected)
    return Quantity(si, UNIT_TABLE[unit][1], unit)


def to_si_matrix(
    rows: list[list[float]], unit: str, expected: Dimension | None = None
) -> list[list[float]]:
    """Convert a matrix of values in a common unit into canonical SI."""
    return [[to_si(v, unit, expected) for v in row] for row in rows]


def thermal_energy(temperature_K: float) -> float:
    """Return ``k_B T`` in joules for a strictly positive temperature."""
    if not math.isfinite(temperature_K) or temperature_K <= 0.0:
        raise UnitError(f"temperature must be finite and strictly positive, got {temperature_K!r}")
    return K_B * temperature_K
