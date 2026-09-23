"""Potential families for the Local Gaussian programme.

Level 1 is the separable Local Gaussian field

    V(x) = sum_i V_i(x_i),  V_i(x_i) = 1/2 ((x_i - x*_i)/sigma_i)^2,
    mu_i = (x_i - x*_i)/sigma_i^2.

No full-system covariance matrix and no automatic multivariate factor discovery
are used. The abstraction is nevertheless factor-based so a later local factor
potential over coordinate groups can be registered without changing valuation.

The historical threshold/hinge family in `d0_v29.py` is preserved untouched and
is deliberately not imported here; the two families stay separately registered.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from .numerics import Refusal, Vector, exact_vector

FAMILY_LOCAL_GAUSSIAN = "EBU-POTENTIAL-LOCAL-GAUSSIAN-L1-v1"


@dataclass(frozen=True)
class LocalGaussianPotential:
    """Separable Level-1 Gaussian evaluation geometry.

    This is an evaluation geometry only. It exerts no force and moves no
    plant: there is no -gamma (x - x*) term, no -grad V drift and no automatic
    regeneration toward the reference anywhere in this package.
    """

    reference: Vector
    scale: Vector
    family: str = FAMILY_LOCAL_GAUSSIAN

    def __post_init__(self) -> None:
        if len(self.reference) != len(self.scale):
            raise Refusal("reference and scale dimensions differ")
        if not self.reference:
            raise Refusal("potential needs at least one factor")
        for index, sigma in enumerate(self.scale):
            if sigma <= 0:
                raise Refusal(f"scale[{index}] must be finite and positive")

    @classmethod
    def declare(cls, reference, scale) -> "LocalGaussianPotential":
        return cls(exact_vector(reference, "reference"), exact_vector(scale, "scale"))

    @property
    def dimension(self) -> int:
        return len(self.reference)

    def factor_of(self, index: int) -> frozenset[int]:
        """Coordinates sharing a potential term with `index`.

        Level 1 is separable, so each coordinate is its own factor. A later
        local factor potential returns the whole factor here and the rest of
        the valuation code is unchanged.
        """
        if not 0 <= index < self.dimension:
            raise Refusal(f"coordinate {index} out of range")
        return frozenset({index})

    def affected_factors(self, support: frozenset[int]) -> frozenset[int]:
        affected: set[int] = set()
        for index in support:
            affected |= self.factor_of(index)
        return frozenset(affected)

    def factor_value(self, state: Vector, index: int) -> Fraction:
        deviation = state[index] - self.reference[index]
        return deviation * deviation / (2 * self.scale[index] * self.scale[index])

    def value_on(self, state: Vector, indices: frozenset[int]) -> Fraction:
        """Partial potential over the given factors only.

        Ordinary candidate valuation calls this with the candidate's affected
        factors, never the whole world.
        """
        result = Fraction(0)
        for index in sorted(indices):
            result += self.factor_value(state, index)
        return result

    def value_total(self, state: Vector) -> Fraction:
        """Whole-world V. Permitted for independent audit, not for valuation."""
        if len(state) != self.dimension:
            raise Refusal("state dimension mismatch")
        return self.value_on(state, frozenset(range(self.dimension)))

    def marginal(self, state: Vector, index: int) -> Fraction:
        return (state[index] - self.reference[index]) / (self.scale[index] * self.scale[index])

    def gradient_on(self, state: Vector, indices: frozenset[int]) -> dict[int, Fraction]:
        return {index: self.marginal(state, index) for index in sorted(indices)}

    def hessian_diagonal(self, index: int) -> Fraction:
        """H_ii = 1/sigma_i^2. The Hessian is diagonal and state-independent."""
        return Fraction(1) / (self.scale[index] * self.scale[index])
