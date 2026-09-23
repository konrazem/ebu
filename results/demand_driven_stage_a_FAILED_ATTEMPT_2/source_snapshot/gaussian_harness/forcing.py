"""External forcing, the deviation ledger and independent audits.

Nature is independent of actors. For the first conservative scalar world the
forcing increment satisfies `1^T u_ext = 0` exactly, so it moves physical state
without creating or destroying mass.

    D_ext,t = V(z_t) - V(x_t),     J_{t+1} = J_t + D_ext,t

Forcing changes `x`. It never credits any `B_i`.

Under the ideal first model the driven accounting invariant is

    V(x_t) + sum_i B_i(t) - J_t = K

with `K = 0` for the zero initialization x_0 = x*, V_0 = 0, B_i(0) = 0, J_0 = 0.
This is an independent audit invariant. Its value is never read to choose a
runtime action.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from .capacity import CapacityLedger
from .numerics import Refusal, Vector, add, total
from .potential import LocalGaussianPotential

FORCING_RULE_ID = "EBU-GAUSSIAN-FORCING-v1"


@dataclass(frozen=True)
class ForcingIncrement:
    """A conservative external disturbance u_ext = s (e_p - e_q)."""

    source: int
    destination: int
    magnitude: Fraction

    def __post_init__(self) -> None:
        if self.source == self.destination:
            raise Refusal("forcing source and destination must differ")
        if self.magnitude <= 0:
            raise Refusal("forcing magnitude must be positive")

    def vector(self, dimension: int) -> Vector:
        values = [Fraction(0)] * dimension
        values[self.source] -= self.magnitude
        values[self.destination] += self.magnitude
        return tuple(values)

    @property
    def forcing_id(self) -> str:
        return (
            f"u:{self.source}->{self.destination}:"
            f"{self.magnitude.numerator}/{self.magnitude.denominator}"
        )


def apply_forcing(state: Vector, increment: ForcingIncrement) -> Vector:
    """Nature mutates physical state only. No balance is touched here."""
    return add(state, increment.vector(len(state)))


def external_deviation(
    potential: LocalGaussianPotential, before: Vector, after: Vector
) -> Fraction:
    """D_ext = V(z) - V(x), signed.

    A disturbance that lowers deviation gives a negative D_ext. That is a
    signed ledger entry, not an accounting error.
    """
    return potential.value_total(after) - potential.value_total(before)


def conservation_residual(state: Vector, declared_mass: Fraction) -> Fraction:
    """sum_i x_i - M. Audited separately from EBU accounting."""
    return total(state) - declared_mass


def accounting_residual(
    potential: LocalGaussianPotential,
    state: Vector,
    ledger: CapacityLedger,
    audit: Fraction,
    constant: Fraction = Fraction(0),
) -> Fraction:
    """V(x) + sum_i B_i - J - K. Zero under the declared update rules."""
    return potential.value_total(state) + ledger.total - audit - constant


def nonnegative_state_residual(state: Vector) -> Fraction:
    """Most negative coordinate, or zero. Physical stock must stay nonnegative."""
    worst = Fraction(0)
    for value in state:
        if value < worst:
            worst = value
    return worst
