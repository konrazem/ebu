"""The Gaussian homeostatic reference region, derived on the actual manifold.

Mission sections 2 and 3. Nothing here is copied from a chi-square table: the
effective dimension is derived from the physical state manifold and the
potential metric, and the quantiles are derived in closed form and enclosed in
exact rational bounds.

Standardized coordinates and the radial statistic
------------------------------------------------

    z_i = (x_i - x*_i) / sigma_i,      R^2(x) = 2 V(x) = sum_i z_i^2.

Effective dimension
-------------------

The physical state carries a declared conservation law `w^T x = M`. In
standardized coordinates that reads `(w_i sigma_i)^T z = w~^T z = M - w^T x*`.
When the reference itself satisfies the conservation law the right-hand side is
zero, so the admissible set is a *linear* subspace `S = {z : w~^T z = 0}` of
dimension `d = n - rank(w~)`, passing through `z = 0`.

That last clause is load-bearing and is checked, not assumed. If the reference
did not satisfy the conservation law, `S` would be an affine subspace missing
the origin, `R^2` restricted to `S` would be *noncentral* chi-square, and every
quantile below would be wrong. `effective_dimension` refuses that world rather
than reporting a dimension that silently means something else.

Reference distribution
----------------------

Under the declared Gaussian reference measure `exp(-V) = exp(-|z|^2/2)`
conditioned on `S`, the coordinates in any orthonormal basis of `S` are i.i.d.
standard normal, so

    R^2 ~ chi^2_d.

This is a property of the *declared model geometry*. It is not a claim that the
driven process visits states with that distribution -- that is the empirical
question the mission asks. The region defines geometry; an occupancy criterion
would be a separate registered pass rule (mission section 15).

Exact quantiles for d = 2
-------------------------

For two degrees of freedom the chi-square CDF has the closed form
`F(r) = 1 - exp(-r/2)`, so

    r_p = -2 ln(1 - p),      r_0.95 = 2 ln 20,   r_0.99 = 2 ln 100.

These are irrational, and `R^2` is rational, so membership is decided against
certified rational *enclosures* rather than a float. A comparison that lands
inside an enclosure is refused, never guessed. Other dimensions have no such
elementary closed form and are refused here rather than approximated.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from typing import Sequence

from gaussian_harness.numerics import Refusal, Vector, exact, exact_vector
from gaussian_harness.potential import LocalGaussianPotential

REGION_RULE_ID = "EBU-GAUSSIAN-HOMEOSTATIC-REGION-v1"
LEVEL_95 = "H95"
LEVEL_99 = "H99"
DECLARED_LEVELS = (LEVEL_95, LEVEL_99)

# Series depth for the rational logarithm enclosures. At y = 1/3 the tail after
# 64 terms is below 3^-129, which is ~1e-62: far finer than any rational R^2
# this world can produce, so no comparison is ever left undecided in practice.
_SERIES_TERMS = 64


@dataclass(frozen=True)
class ConservationLaw:
    """A declared linear conservation law `w^T x = total` on physical state."""

    weights: Vector
    total: Fraction

    @classmethod
    def declare(cls, weights: Sequence, total) -> "ConservationLaw":
        vector = exact_vector(weights, "weights")
        if all(weight == 0 for weight in vector):
            raise Refusal("a conservation law needs a nonzero weight vector")
        return cls(vector, exact(total, "total"))

    @classmethod
    def total_mass(cls, cells: int, total) -> "ConservationLaw":
        """The scalar-mass law `sum_i x_i = M` used by the Gaussian worlds."""
        return cls.declare([1] * cells, total)

    def residual(self, state: Vector) -> Fraction:
        result = Fraction(0)
        for weight, value in zip(self.weights, state):
            result += weight * value
        return result - self.total


def standardized(potential: LocalGaussianPotential, state: Vector) -> Vector:
    """z_i = (x_i - x*_i)/sigma_i, exactly."""
    if len(state) != potential.dimension:
        raise Refusal("state dimension does not match the potential")
    return tuple(
        (value - reference) / scale
        for value, reference, scale in zip(state, potential.reference, potential.scale)
    )


def radial_square(potential: LocalGaussianPotential, state: Vector) -> Fraction:
    """R^2 = 2V = sum_i z_i^2, exactly.

    Computed from the potential rather than from `z` so that the identity
    `R^2 = 2V` is the definition in code as well as on paper.
    """
    return 2 * potential.value_total(state)


def effective_dimension(
    potential: LocalGaussianPotential, laws: Sequence[ConservationLaw]
) -> int:
    """d = n - rank of the standardized constraint normals.

    Refuses any law the reference does not satisfy, because the central
    chi-square reading depends on the admissible set containing `z = 0`.
    """
    n = potential.dimension
    normals: list[list[Fraction]] = []
    for position, law in enumerate(laws):
        if len(law.weights) != n:
            raise Refusal(f"conservation law {position} has the wrong width")
        if law.residual(potential.reference) != 0:
            raise Refusal(
                f"REFERENCE_OFF_CONSTRAINT: law {position} is violated by the reference, "
                "so the admissible set misses the origin and R^2 is noncentral"
            )
        normals.append(
            [weight * scale for weight, scale in zip(law.weights, potential.scale)]
        )
    return n - _rank(normals)


def _rank(rows: list[list[Fraction]]) -> int:
    """Exact rational Gaussian elimination. No pivoting tolerance exists."""
    rows = [list(row) for row in rows]
    rank = 0
    columns = len(rows[0]) if rows else 0
    for column in range(columns):
        pivot = next(
            (index for index in range(rank, len(rows)) if rows[index][column] != 0), None
        )
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        head = rows[rank]
        for index in range(len(rows)):
            if index != rank and rows[index][column] != 0:
                factor = rows[index][column] / head[column]
                rows[index] = [a - factor * b for a, b in zip(rows[index], head)]
        rank += 1
    return rank


@lru_cache(maxsize=None)
def _atanh_enclosure(y: Fraction, terms: int = _SERIES_TERMS) -> tuple[Fraction, Fraction]:
    """Rational bounds on atanh(y) for 0 < y < 1.

    Memoised because the partial sums carry very large numerators: recomputing
    the 64-term series on every membership test dominated the cost of a whole
    trajectory analysis. The result is a pure function of its arguments, so the
    cache changes performance and nothing else.

    Every term is positive, so the partial sum is a lower bound and the
    geometric majorant of the tail gives the upper bound:

        sum_{k>=N} y^(2k+1)/(2k+1) <= y^(2N+1) / ((2N+1)(1 - y^2)).
    """
    if not 0 < y < 1:
        raise Refusal("atanh series needs 0 < y < 1")
    square = y * y
    power = y
    partial = Fraction(0)
    for k in range(terms):
        partial += power / (2 * k + 1)
        power *= square
    tail = power / ((2 * terms + 1) * (1 - square))
    return partial, partial + tail


def _scaled(bounds: tuple[Fraction, Fraction], factor: int) -> tuple[Fraction, Fraction]:
    low, high = bounds
    return low * factor, high * factor


def _sum_bounds(*parts: tuple[Fraction, Fraction]) -> tuple[Fraction, Fraction]:
    low = Fraction(0)
    high = Fraction(0)
    for part_low, part_high in parts:
        low += part_low
        high += part_high
    return low, high


@lru_cache(maxsize=None)
def ln2_enclosure(terms: int = _SERIES_TERMS) -> tuple[Fraction, Fraction]:
    """ln 2 = 2 atanh(1/3)."""
    return _scaled(_atanh_enclosure(Fraction(1, 3), terms), 2)


@lru_cache(maxsize=None)
def ln_five_quarters_enclosure(terms: int = _SERIES_TERMS) -> tuple[Fraction, Fraction]:
    """ln(5/4) = 2 atanh(1/9)."""
    return _scaled(_atanh_enclosure(Fraction(1, 9), terms), 2)


@lru_cache(maxsize=None)
def chi2_two_quantile_enclosure(
    numerator: int, denominator: int, terms: int = _SERIES_TERMS
) -> tuple[Fraction, Fraction]:
    """Enclose r_p = -2 ln(1 - p) for chi^2_2 at the rational level p.

    Only the two declared levels are supported, each reduced to logarithms of 2
    and 5/4 so that one fast-converging series covers both:

        r_0.95 = 2 ln 20  = 8 ln 2 + 4 atanh(1/9) * ... = 2(4 ln 2 + ln(5/4))
        r_0.99 = 2 ln 100 = 2(6 ln 2 + 2 ln(5/4))
    """
    level = Fraction(numerator, denominator)
    ln2 = ln2_enclosure(terms)
    ln54 = ln_five_quarters_enclosure(terms)
    if level == Fraction(95, 100):
        # ln 20 = ln(16 * 5/4) = 4 ln 2 + ln(5/4)
        inner = _sum_bounds(_scaled(ln2, 4), ln54)
    elif level == Fraction(99, 100):
        # ln 100 = ln(64 * (5/4)^2) = 6 ln 2 + 2 ln(5/4)
        inner = _sum_bounds(_scaled(ln2, 6), _scaled(ln54, 2))
    else:
        raise Refusal(
            f"QUANTILE_NOT_DERIVED: level {level} has no derivation in this module; "
            "add its exact reduction rather than a table lookup"
        )
    return _scaled(inner, 2)


@lru_cache(maxsize=None)
def threshold_enclosure(level: str, terms: int = _SERIES_TERMS) -> tuple[Fraction, Fraction]:
    if level == LEVEL_95:
        return chi2_two_quantile_enclosure(95, 100, terms)
    if level == LEVEL_99:
        return chi2_two_quantile_enclosure(99, 100, terms)
    raise Refusal(f"undeclared homeostatic level {level!r}")


@dataclass(frozen=True)
class ReferenceRegion:
    """The declared homeostatic region for one world.

    `dimension` is derived from the manifold, never supplied. Construction
    refuses a world whose derived dimension is not two, because the exact
    quantile reduction above is specific to the two-degree-of-freedom closed
    form and there is no honest way to reuse it elsewhere.
    """

    potential: LocalGaussianPotential
    dimension: int
    laws: tuple[ConservationLaw, ...]

    @classmethod
    def derive(
        cls, potential: LocalGaussianPotential, laws: Sequence[ConservationLaw]
    ) -> "ReferenceRegion":
        dimension = effective_dimension(potential, laws)
        if dimension != 2:
            raise Refusal(
                f"UNSUPPORTED_EFFECTIVE_DIMENSION: derived d = {dimension}; the exact "
                "chi-square reduction in this module covers d = 2 only"
            )
        return cls(potential, dimension, tuple(laws))

    def radial_square(self, state: Vector) -> Fraction:
        return radial_square(self.potential, state)

    def contains(self, state: Vector, level: str) -> bool:
        """Exact membership. An undecidable comparison refuses; it never guesses."""
        value = self.radial_square(state)
        low, high = threshold_enclosure(level)
        if value < low:
            return True
        if value > high:
            return False
        raise Refusal(
            f"THRESHOLD_ENCLOSURE_TOO_COARSE: R^2 = {value} lies inside the certified "
            f"bracket [{low}, {high}] for {level}; widen the series before deciding"
        )

    def contains_radial_square(self, value: Fraction, level: str) -> bool:
        low, high = threshold_enclosure(level)
        if value < low:
            return True
        if value > high:
            return False
        raise Refusal(
            f"THRESHOLD_ENCLOSURE_TOO_COARSE: R^2 = {value} lies inside the certified "
            f"bracket [{low}, {high}] for {level}"
        )

    def boundary_radial_square(self) -> Fraction:
        """The largest `R^2` whose ball is entirely physically admissible.

        The physical constraint `x_i >= 0` is the half-space `z_i >= -c_i` with
        `c_i = x*_i / sigma_i`. Inside the subspace `S` the distance from the
        origin to that boundary is `c_i / |P_S e_i|`, so the inscribed radius is
        the smallest such distance over the cells, and this returns its square.
        """
        normals = [
            [weight * scale for weight, scale in zip(law.weights, self.potential.scale)]
            for law in self.laws
        ]
        best: Fraction | None = None
        for index in range(self.potential.dimension):
            projected_square = _projected_axis_norm_square(normals, index, self.potential.dimension)
            if projected_square == 0:
                continue
            offset = self.potential.reference[index] / self.potential.scale[index]
            candidate = offset * offset / projected_square
            if best is None or candidate < best:
                best = candidate
        if best is None:
            raise Refusal("no physical boundary is reachable inside the subspace")
        return best


def _projected_axis_norm_square(
    normals: list[list[Fraction]], index: int, dimension: int
) -> Fraction:
    """|P_S e_index|^2 where S is the orthogonal complement of `normals`.

    Computed by Gram-Schmidt on the constraint normals, which is exact in
    rational arithmetic; `P_S e = e - sum_k <e, u_k> u_k` over the orthonormal
    constraint basis, and only the squared norm is needed.
    """
    basis: list[list[Fraction]] = []
    for normal in normals:
        vector = list(normal)
        for previous in basis:
            inner = sum((a * b for a, b in zip(vector, previous)), Fraction(0))
            norm = sum((b * b for b in previous), Fraction(0))
            if norm == 0:
                continue
            factor = inner / norm
            vector = [a - factor * b for a, b in zip(vector, previous)]
        if any(component != 0 for component in vector):
            basis.append(vector)
    result = Fraction(1)
    for previous in basis:
        norm = sum((b * b for b in previous), Fraction(0))
        if norm == 0:
            continue
        component = previous[index]
        result -= component * component / norm
    return result
