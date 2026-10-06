"""Deterministic optimiser with a frozen configuration: supports Layer F.

Everything that could be tuned after seeing an outcome is frozen here:
parameterisation, initialisation rule, bounds, convergence tolerances,
restart policy and failure classification.  An optimiser failure is a declared
non-evaluable outcome; a beta value is never fabricated to avoid one.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Sequence

from .numerics import NumericalFailure

# --- frozen optimiser configuration ---------------------------------------
OPTIMIZER = "Nelder-Mead simplex, fixed reflection/expansion/contraction/shrink"
ALPHA, GAMMA, RHO, SIGMA = 1.0, 2.0, 0.5, 0.5
#: Relative simplex spread at which the fit is declared converged.
X_TOL = 1e-8
#: Absolute objective spread at which the fit is declared converged.
F_TOL = 1e-9
#: Hard evaluation budget; exceeding it is a failure, never a partial answer.
MAX_EVALUATIONS = 4000
#: Deterministic initial simplex step, relative for nonzero coordinates.
INIT_STEP_REL = 0.05
INIT_STEP_ABS = 0.05
#: Number of deterministic restarts from the incumbent optimum.
RESTARTS = 2


class OptimizerFailure(Exception):
    """The optimiser did not establish a unique usable maximum."""


#: Reason codes recorded on every optimiser outcome.
REASON_CONVERGED = "converged"
REASON_BUDGET = "evaluation_budget_exhausted"
REASON_RESTARTS = "restarts_exhausted_without_convergence"
REASON_NONFINITE = "objective_nonfinite_at_optimum"


@dataclass(frozen=True)
class OptimizeResult:
    x: list[float]
    fun: float
    evaluations: int
    converged: bool
    reason: str = ""

    @property
    def usable(self) -> bool:
        """True only for a converged result with a finite objective and point."""
        return (
            self.converged
            and math.isfinite(self.fun)
            and all(math.isfinite(v) for v in self.x)
        )


def _initial_simplex(x0: Sequence[float]) -> list[list[float]]:
    n = len(x0)
    simplex = [list(x0)]
    for i in range(n):
        pt = list(x0)
        step = INIT_STEP_REL * abs(pt[i]) if pt[i] != 0.0 else INIT_STEP_ABS
        pt[i] += step
        simplex.append(pt)
    return simplex


def minimise(
    func: Callable[[Sequence[float]], float],
    x0: Sequence[float],
    max_evaluations: int = MAX_EVALUATIONS,
) -> OptimizeResult:
    """Deterministic Nelder-Mead minimisation with frozen constants.

    The objective may return ``inf`` to mark an inadmissible point (for example
    a non-SPD diffusion); the simplex then contracts away from it rather than
    the caller silently clipping parameters into the admissible set.
    """
    n = len(x0)
    evals = 0

    def safe(x: Sequence[float]) -> float:
        nonlocal evals
        evals += 1
        try:
            v = func(x)
        except (NumericalFailure, ValueError, OverflowError, ZeroDivisionError):
            return math.inf
        if v is None or (isinstance(v, float) and math.isnan(v)):
            return math.inf
        return v

    best_x = list(x0)
    best_f = safe(best_x)
    if not math.isfinite(best_f):
        raise OptimizerFailure("initial point is inadmissible under the declared model")

    for attempt in range(RESTARTS + 1):
        simplex = _initial_simplex(best_x)
        fvals = [safe(p) for p in simplex]
        if not any(math.isfinite(v) for v in fvals):
            raise OptimizerFailure("entire initial simplex is inadmissible")
        converged = False
        while evals < max_evaluations:
            order = sorted(range(n + 1), key=lambda i: fvals[i])
            simplex = [simplex[i] for i in order]
            fvals = [fvals[i] for i in order]
            spread_x = max(
                max(abs(simplex[i][j] - simplex[0][j]) for i in range(1, n + 1))
                for j in range(n)
            )
            scale_x = max(1.0, max(abs(v) for v in simplex[0]))
            spread_f = abs(fvals[-1] - fvals[0])
            if spread_x <= X_TOL * scale_x and spread_f <= F_TOL * max(1.0, abs(fvals[0])):
                converged = True
                break
            centroid = [sum(simplex[i][j] for i in range(n)) / n for j in range(n)]
            xr = [centroid[j] + ALPHA * (centroid[j] - simplex[-1][j]) for j in range(n)]
            fr = safe(xr)
            if fr < fvals[0]:
                xe = [centroid[j] + GAMMA * (xr[j] - centroid[j]) for j in range(n)]
                fe = safe(xe)
                simplex[-1], fvals[-1] = (xe, fe) if fe < fr else (xr, fr)
            elif fr < fvals[-2]:
                simplex[-1], fvals[-1] = xr, fr
            else:
                if fr < fvals[-1]:
                    xc = [centroid[j] + RHO * (xr[j] - centroid[j]) for j in range(n)]
                else:
                    xc = [centroid[j] + RHO * (simplex[-1][j] - centroid[j]) for j in range(n)]
                fc = safe(xc)
                if fc < min(fr, fvals[-1]):
                    simplex[-1], fvals[-1] = xc, fc
                else:
                    for i in range(1, n + 1):
                        simplex[i] = [
                            simplex[0][j] + SIGMA * (simplex[i][j] - simplex[0][j])
                            for j in range(n)
                        ]
                        fvals[i] = safe(simplex[i])
        idx = min(range(n + 1), key=lambda i: fvals[i])
        if fvals[idx] < best_f:
            best_f, best_x = fvals[idx], list(simplex[idx])
        if converged and attempt >= 1:
            if not (math.isfinite(best_f) and all(math.isfinite(v) for v in best_x)):
                return OptimizeResult(best_x, best_f, evals, False, REASON_NONFINITE)
            return OptimizeResult(best_x, best_f, evals, True, REASON_CONVERGED)
        if evals >= max_evaluations:
            return OptimizeResult(best_x, best_f, evals, False, REASON_BUDGET)
    # Restarts exhausted without a converged attempt.  This is NOT success:
    # returning converged=True here would let a non-maximum reach inference.
    return OptimizeResult(best_x, best_f, evals, False, REASON_RESTARTS)
