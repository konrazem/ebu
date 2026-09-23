"""Exact finite EBU, common-path receipts and interaction diagnostics.

Definitional form (task section 7), for a physical increment `delta` applied to
a frozen pre-action baseline `z`:

    E = V(z) - V(z + delta)

For the quadratic Level-1 model this equals the closed form

    E = -mu(z)^T delta - 1/2 delta^T H delta

exactly, not to first order. Initial force times finite quantity is **not** an
exact substitute and is provided only as `linear_estimate` for diagnostics.

Simultaneous groups use one frozen baseline and the common path
`x(s) = z + s delta_G`, giving

    R_a = -integral_0^1 grad V(z + s delta_G)^T delta_a ds
        = -mu(z)^T delta_a - 1/2 delta_a^T H delta_G,   sum_a R_a = E_G.

Simultaneous children are never settled from same-baseline singleton quotes.

Exact closure of the decomposition establishes the arithmetic only. It is not
causal identification, physical observation, fairness, ownership or spending
entitlement; those remain separately declared model rules.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from typing import Iterable, Mapping, Sequence

from .actions import ActionGroup, AtomicAction
from .numerics import Refusal, Vector, add
from .potential import LocalGaussianPotential

QUADRATURE_RULES = ("trapezoid", "midpoint", "simpson", "composite_trapezoid")


def finite_ebu(
    potential: LocalGaussianPotential,
    baseline: Vector,
    increment: Vector,
    indices: frozenset[int] | None = None,
) -> Fraction:
    """E = V_loc(z) - V_loc(z + delta) over affected factors only.

    This is the definition. Unchanged factors cancel identically, so the local
    restriction is exact rather than an approximation, and an unrelated
    coordinate outside the affected factors cannot influence the result.
    """
    if indices is None:
        indices = potential.affected_factors(
            frozenset(i for i, value in enumerate(increment) if value != 0)
        )
    moved = add(baseline, increment)
    return potential.value_on(baseline, indices) - potential.value_on(moved, indices)


def quadratic_ebu(
    potential: LocalGaussianPotential,
    baseline: Vector,
    increment: Vector,
    indices: frozenset[int] | None = None,
) -> Fraction:
    """E = -mu^T delta - 1/2 delta^T H delta, the analytic form of `finite_ebu`."""
    if indices is None:
        indices = potential.affected_factors(
            frozenset(i for i, value in enumerate(increment) if value != 0)
        )
    result = Fraction(0)
    for index in sorted(indices):
        delta = increment[index]
        if delta == 0:
            continue
        result -= potential.marginal(baseline, index) * delta
        result -= potential.hessian_diagonal(index) * delta * delta / 2
    return result


def linear_estimate(
    potential: LocalGaussianPotential, baseline: Vector, increment: Vector
) -> Fraction:
    """-mu^T delta: initial force times finite quantity.

    Diagnostic only. It is NOT the exact finite value and must never be
    settled, credited or used for affordability. It ignores the curvature term
    and so mis-signs overshoot.
    """
    result = Fraction(0)
    for index, delta in enumerate(increment):
        if delta != 0:
            result -= potential.marginal(baseline, index) * delta
    return result


def group_ebu(
    potential: LocalGaussianPotential, baseline: Vector, group: ActionGroup
) -> Fraction:
    """E_G = V(z) - V(z + delta_G) for the simultaneous group."""
    increment = group.increment(potential.dimension)
    indices = potential.affected_factors(group.support)
    return finite_ebu(potential, baseline, increment, indices)


def _path_integrand(
    potential: LocalGaussianPotential,
    baseline: Vector,
    group_increment: Vector,
    action_increment: Vector,
    parameter: Fraction,
) -> Fraction:
    """-grad V(z + s delta_G)^T delta_a, affine in `s` for quadratic V."""
    result = Fraction(0)
    for index, delta_a in enumerate(action_increment):
        if delta_a == 0:
            continue
        gradient = potential.marginal(baseline, index) + (
            potential.hessian_diagonal(index) * group_increment[index] * parameter
        )
        result -= gradient * delta_a
    return result


def path_receipt_quadrature(
    potential: LocalGaussianPotential,
    baseline: Vector,
    group_increment: Vector,
    action_increment: Vector,
    rule: str = "simpson",
    panels: int = 4,
) -> Fraction:
    """Numerical evaluation of the common-path receipt integral.

    For the quadratic model the integrand is affine in `s`, so every rule here
    returns the exact integral in rational arithmetic. Integration tolerance is
    therefore zero rather than a small float, and closure against the closed
    form is an exact identity.
    """
    if rule not in QUADRATURE_RULES:
        raise Refusal(f"unknown quadrature rule {rule!r}")

    def f(parameter: Fraction) -> Fraction:
        return _path_integrand(potential, baseline, group_increment, action_increment, parameter)

    zero, half, one = Fraction(0), Fraction(1, 2), Fraction(1)
    if rule == "trapezoid":
        return (f(zero) + f(one)) / 2
    if rule == "midpoint":
        return f(half)
    if rule == "simpson":
        return (f(zero) + 4 * f(half) + f(one)) / 6
    if panels <= 0:
        raise Refusal("composite quadrature needs a positive panel count")
    width = Fraction(1, panels)
    result = Fraction(0)
    for panel in range(panels):
        left = width * panel
        right = width * (panel + 1)
        result += (f(left) + f(right)) * width / 2
    return result


def path_receipt_closed_form(
    potential: LocalGaussianPotential,
    baseline: Vector,
    group_increment: Vector,
    action_increment: Vector,
) -> Fraction:
    """R_a = -mu(z)^T delta_a - 1/2 delta_a^T H delta_G."""
    result = Fraction(0)
    for index, delta_a in enumerate(action_increment):
        if delta_a == 0:
            continue
        result -= potential.marginal(baseline, index) * delta_a
        result -= potential.hessian_diagonal(index) * delta_a * group_increment[index] / 2
    return result


@dataclass(frozen=True)
class GroupValuation:
    """Exact valuation of one candidate group from one frozen baseline."""

    group: ActionGroup
    group_ebu: Fraction
    receipts: tuple[tuple[AtomicAction, Fraction], ...]
    residual: Fraction

    @property
    def owner_deltas(self) -> dict[int, Fraction]:
        """Same-event signed netting of owned receipts (decision packet B)."""
        deltas: dict[int, Fraction] = {}
        for action, receipt in self.receipts:
            deltas[action.owner] = deltas.get(action.owner, Fraction(0)) + receipt
        return deltas


def value_group(
    potential: LocalGaussianPotential, baseline: Vector, group: ActionGroup
) -> GroupValuation:
    """Value a group and decompose it along the common path.

    Evaluation is side-effect free: `baseline` is never mutated and no physical
    state, balance or ledger is touched.
    """
    dimension = potential.dimension
    group_increment = group.increment(dimension)
    total = group_ebu(potential, baseline, group)
    receipts = tuple(
        (
            action,
            path_receipt_closed_form(
                potential, baseline, group_increment, action.increment(dimension)
            ),
        )
        for action in group.actions
    )
    summed = Fraction(0)
    for _, receipt in receipts:
        summed += receipt
    return GroupValuation(group, total, receipts, total - summed)


def pair_mobius_term(
    potential: LocalGaussianPotential,
    baseline: Vector,
    first: Vector,
    second: Vector,
) -> Fraction:
    """m_ab = -delta_a^T H delta_b for the quadratic set function.

    Optional research diagnostic. It is not a settlement mechanism and issues
    no capacity.
    """
    result = Fraction(0)
    for index, delta_a in enumerate(first):
        if delta_a != 0 and second[index] != 0:
            result -= potential.hessian_diagonal(index) * delta_a * second[index]
    return result


def mobius_term(
    potential: LocalGaussianPotential,
    baseline: Vector,
    increments: Sequence[Vector],
) -> Fraction:
    """Moebius coefficient m(A) = sum_{B subset A} (-1)^{|A|-|B|} F(B).

    Requires every relevant subset to share this baseline, potential and the
    same fixed increments; that is what makes the degree argument apply.
    """
    size = len(increments)
    if size == 0:
        raise Refusal("Moebius term needs a nonempty subset")
    result = Fraction(0)
    for count in range(size + 1):
        sign = -1 if (size - count) % 2 else 1
        for chosen in combinations(range(size), count):
            combined = tuple(Fraction(0) for _ in range(potential.dimension))
            for position in chosen:
                combined = add(combined, increments[position])
            result += sign * finite_ebu(
                potential,
                baseline,
                combined,
                potential.affected_factors(
                    frozenset(
                        index
                        for increment in increments
                        for index, value in enumerate(increment)
                        if value != 0
                    )
                ),
            )
    return result
