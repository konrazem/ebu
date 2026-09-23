"""Level-1 Gaussian potential over a world with partly unvalued coordinates.

The valuation geometry is unchanged from the registered programme:

    V(x) = sum_{i in P} 1/2 ((x_i - x*_i)/sigma_i)^2,
    mu_i = (x_i - x*_i)/sigma_i^2,  H_ii = 1/sigma_i^2,

but the coordinate set is now larger than the set `P` that carries potential.
A loss sink may be declared either *inside* `V`, where the waste it accumulates
is a real deviation that EBU charges for, or *audit-only outside* `V`, where it
exists purely so that conservation closes and nothing disappears into nowhere.
An audit-only coordinate has no reference, no scale, no marginal and no
curvature, and contributes exactly zero to every EBU quantity.

That distinction is load-bearing rather than cosmetic: contract section 23
forbids pretending an audit-only sink creates a homeostatic demand, so the
absence of a reference here is what makes the P-demand derivation refuse to
invent one.

`LocalGaussianPotential` from the pinned `gaussian_harness` package is not
subclassed or wrapped, because it requires every coordinate to be valued. It is
instead used by the conformance suite as an independent oracle: on a world
whose coordinates are all valued, this potential must agree with it exactly,
coordinate by coordinate, on value, marginal and curvature.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from gaussian_harness.numerics import Refusal, Vector

FAMILY_DEMAND_GAUSSIAN = "EBU-POTENTIAL-LOCAL-GAUSSIAN-L1-DEMAND-v1"


@dataclass(frozen=True)
class DemandPotential:
    """Separable Level-1 geometry with an explicit unvalued coordinate set.

    This is an evaluation geometry only. It exerts no force, applies no drift
    and moves no stock: nothing in this package adds a `-grad V` term or any
    automatic regeneration toward the reference.
    """

    reference: tuple[Fraction | None, ...]
    scale: tuple[Fraction | None, ...]
    family: str = FAMILY_DEMAND_GAUSSIAN

    def __post_init__(self) -> None:
        if len(self.reference) != len(self.scale):
            raise Refusal("reference and scale dimensions differ")
        if not self.reference:
            raise Refusal("potential needs at least one coordinate")
        for index, (mean, sigma) in enumerate(zip(self.reference, self.scale)):
            if (mean is None) != (sigma is None):
                raise Refusal(f"coordinate {index} declares only half of (reference, scale)")
            if sigma is not None and sigma <= 0:
                raise Refusal(f"scale[{index}] must be finite and positive")
        if not any(mean is not None for mean in self.reference):
            raise Refusal("at least one coordinate must carry potential")

    @property
    def dimension(self) -> int:
        return len(self.reference)

    @property
    def valued(self) -> tuple[int, ...]:
        """Coordinates that carry potential, in canonical index order."""
        return tuple(
            index for index, mean in enumerate(self.reference) if mean is not None
        )

    def carries_potential(self, index: int) -> bool:
        if not 0 <= index < self.dimension:
            raise Refusal(f"coordinate {index} out of range")
        return self.reference[index] is not None

    def factor_value(self, state: Vector, index: int) -> Fraction:
        if not self.carries_potential(index):
            return Fraction(0)
        deviation = state[index] - self.reference[index]
        sigma = self.scale[index]
        return deviation * deviation / (2 * sigma * sigma)

    def value_on(self, state: Vector, indices: frozenset[int]) -> Fraction:
        """Partial potential over the given coordinates only.

        Candidate valuation calls this with the plan's touched coordinates,
        never the whole world. Unchanged coordinates cancel identically, so the
        restriction is exact rather than an approximation.
        """
        result = Fraction(0)
        for index in sorted(indices):
            result += self.factor_value(state, index)
        return result

    def value_total(self, state: Vector) -> Fraction:
        """Whole-world V. For independent audit, not for candidate valuation."""
        if len(state) != self.dimension:
            raise Refusal("state dimension mismatch")
        return self.value_on(state, frozenset(range(self.dimension)))

    def marginal(self, state: Vector, index: int) -> Fraction:
        if not self.carries_potential(index):
            return Fraction(0)
        sigma = self.scale[index]
        return (state[index] - self.reference[index]) / (sigma * sigma)

    def hessian_diagonal(self, index: int) -> Fraction:
        if not self.carries_potential(index):
            return Fraction(0)
        sigma = self.scale[index]
        return Fraction(1) / (sigma * sigma)

    def deficit(self, state: Vector, index: int) -> Fraction:
        """x*_i - x_i when positive, else zero. The P-demand quantity."""
        if not self.carries_potential(index):
            return Fraction(0)
        shortfall = self.reference[index] - state[index]
        return shortfall if shortfall > 0 else Fraction(0)
