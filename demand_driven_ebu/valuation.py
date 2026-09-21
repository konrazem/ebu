"""Exact finite EBU for demand-serving plans, and common-path receipts.

Valuation comes *after* demand and physics, and measures only one thing: the
physical consequence of a service plan that has already been shown to be a
complete, executable answer to an existing obligation.

    E_G = V(x_pre) - V(x_pre + delta_G)

For the separable quadratic geometry this equals the closed form

    E_G = -mu(z)^T delta_G - 1/2 delta_G^T H delta_G

exactly, not to first order. Initial force times finite quantity is not an
exact substitute and appears only as a diagnostic.

Simultaneous plans are valued from one frozen baseline along the common path
`x(s) = z + s delta_G`, giving

    R_a = -mu(z)^T delta_a - 1/2 delta_a^T H delta_G,   sum_a R_a = E_G.

Children of a simultaneous group are never settled from same-baseline singleton
quotes. Loss sinks participate exactly like any other coordinate: one inside
`V` contributes its own deviation term and so makes a lossy plan cost EBU,
while an audit-only sink has no marginal and no curvature and contributes
exactly zero.

Exact closure of this decomposition establishes arithmetic only. It is not
causal identification, fairness, desert, ownership or a spending entitlement;
those remain separately declared model rules.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from gaussian_harness.numerics import Refusal, Vector, add

from .physical import PhysicalAction, PlanGroup
from .potential import DemandPotential
from .world import DemandWorld

QUADRATURE_RULES = ("trapezoid", "midpoint", "simpson")


def finite_ebu(
    potential: DemandPotential,
    baseline: Vector,
    increment: Vector,
    indices: frozenset[int] | None = None,
) -> Fraction:
    """E = V_loc(z) - V_loc(z + delta) over the touched coordinates only."""
    if indices is None:
        indices = frozenset(i for i, value in enumerate(increment) if value != 0)
    moved = add(baseline, increment)
    return potential.value_on(baseline, indices) - potential.value_on(moved, indices)


def quadratic_ebu(
    potential: DemandPotential,
    baseline: Vector,
    increment: Vector,
    indices: frozenset[int] | None = None,
) -> Fraction:
    """The analytic form of `finite_ebu`, for an independent exact cross-check."""
    if indices is None:
        indices = frozenset(i for i, value in enumerate(increment) if value != 0)
    result = Fraction(0)
    for index in sorted(indices):
        delta = increment[index]
        if delta == 0:
            continue
        result -= potential.marginal(baseline, index) * delta
        result -= potential.hessian_diagonal(index) * delta * delta / 2
    return result


def linear_estimate(
    potential: DemandPotential, baseline: Vector, increment: Vector
) -> Fraction:
    """-mu^T delta. Diagnostic only: never settled, credited or made affordable."""
    result = Fraction(0)
    for index, delta in enumerate(increment):
        if delta != 0:
            result -= potential.marginal(baseline, index) * delta
    return result


def group_ebu(potential: DemandPotential, baseline: Vector, group: PlanGroup) -> Fraction:
    increment = group.increment(potential.dimension)
    return finite_ebu(potential, baseline, increment, group.support)


def receipt_closed_form(
    potential: DemandPotential,
    baseline: Vector,
    group_increment: Vector,
    action_increment: Vector,
) -> Fraction:
    result = Fraction(0)
    for index, delta_a in enumerate(action_increment):
        if delta_a == 0:
            continue
        result -= potential.marginal(baseline, index) * delta_a
        result -= potential.hessian_diagonal(index) * delta_a * group_increment[index] / 2
    return result


def _path_integrand(
    potential: DemandPotential,
    baseline: Vector,
    group_increment: Vector,
    action_increment: Vector,
    parameter: Fraction,
) -> Fraction:
    result = Fraction(0)
    for index, delta_a in enumerate(action_increment):
        if delta_a == 0:
            continue
        gradient = potential.marginal(baseline, index) + (
            potential.hessian_diagonal(index) * group_increment[index] * parameter
        )
        result -= gradient * delta_a
    return result


def receipt_quadrature(
    potential: DemandPotential,
    baseline: Vector,
    group_increment: Vector,
    action_increment: Vector,
    rule: str = "simpson",
) -> Fraction:
    """The receipt integral evaluated numerically.

    The integrand is affine in `s` for a quadratic geometry, so every rule here
    returns the exact integral in rational arithmetic. Integration tolerance is
    zero rather than small, and closure against the closed form is an exact
    identity rather than an approximation that happens to be close.
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
    return (f(zero) + 4 * f(half) + f(one)) / 6


@dataclass(frozen=True)
class GroupValuation:
    """Exact valuation of one plan from one frozen baseline. Side-effect free."""

    group: PlanGroup
    group_ebu: Fraction
    receipts: tuple[tuple[PhysicalAction, Fraction], ...]
    residual: Fraction
    owner_deltas: tuple[tuple[str, Fraction], ...]

    @property
    def owner_map(self) -> dict[str, Fraction]:
        return dict(self.owner_deltas)


def value_group(world: DemandWorld, baseline: Vector, group: PlanGroup) -> GroupValuation:
    """Value a plan and decompose it along the common path.

    `baseline` is never mutated, and no physical state, balance or ledger is
    touched: computing what a plan would be worth is not executing it.
    """
    potential = world.potential
    dimension = world.dimension
    group_increment = group.increment(dimension)
    total = finite_ebu(potential, baseline, group_increment, group.support)

    receipts = tuple(
        (
            action,
            receipt_closed_form(
                potential, baseline, group_increment, action.increment(dimension)
            ),
        )
        for action in group.actions
    )
    summed = Fraction(0)
    deltas: dict[str, Fraction] = {}
    for action, receipt in receipts:
        summed += receipt
        owner = action.owner(world)
        deltas[owner] = deltas.get(owner, Fraction(0)) + receipt

    return GroupValuation(
        group,
        total,
        receipts,
        total - summed,
        tuple(sorted(deltas.items())),
    )
