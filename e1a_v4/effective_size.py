"""Finite-sampling correlation sums and per-element effective sample sizes.

For a stationary OU coordinate sampled at spacing dt with relaxation time tau,
phi = exp(-dt/tau) and

    A_p = 1 + 2 sum_{k=1}^{n-1} (1 - k/n) phi^{p k}

The EXACT finite-n closed form is used; `A_from_sum` recomputes the same
quantity by explicit summation so the two can be compared in a test.

Which A applies to which statistic:
    second moments  (S, K, beta, G1-G4)  ->  A over x = phi_a * phi_b
    fourth moment   (G5's g2)            ->  A over x = phi_r^4

There is NO single scalar n_eff for an anisotropic field: tau_r = gamma(T)/k_r
differ per mode, so the effective size is per ELEMENT of S.

CLASSIFICATION
    A_closed_form, N_ab, N_g2 ......... EXACT UNDER STATED ASSUMPTIONS
        (exact for the stationary discrete-time AR(1) model; the continuous-time
         form N_ab = (T/2)(1/tau_a + 1/tau_b) is its large-n limit and is 0.1-1%
         ANTI-conservative at the declared dt, so it is not used)
    var_g2 ............................ APPROXIMATION (leading-order delta method)
"""

from __future__ import annotations

import math

from .numerics import Refusal


def phi_of(dt: float, tau: float) -> float:
    if dt <= 0.0 or tau <= 0.0:
        raise Refusal("dt and tau must be positive")
    return math.exp(-dt / tau)


def A_closed_form(x: float, n: int) -> float:
    """EXACT finite-n value of 1 + 2 sum_{k=1}^{n-1} (1-k/n) x^k, for 0 <= x < 1."""
    if not (0.0 <= x < 1.0):
        raise Refusal(f"A_closed_form needs 0 <= x < 1, got {x!r}")
    if n < 1:
        raise Refusal("n must be a positive integer")
    if n == 1 or x == 0.0:
        return 1.0
    one_minus = 1.0 - x
    geometric = (x - x ** n) / one_minus
    weighted = x * (1.0 - n * x ** (n - 1) + (n - 1) * x ** n) / (n * one_minus * one_minus)
    return 1.0 + 2.0 * (geometric - weighted)


def A_from_sum(x: float, n: int) -> float:
    """The same quantity by explicit summation. Reference for the closed form."""
    if not (0.0 <= x < 1.0):
        raise Refusal(f"A_from_sum needs 0 <= x < 1, got {x!r}")
    return 1.0 + 2.0 * sum((1.0 - k / n) * x ** k for k in range(1, n))


def N_element(phi_a: float, phi_b: float, n: int) -> float:
    """Effective size for the (a,b) element of the sample covariance."""
    return n / A_closed_form(phi_a * phi_b, n)


def N_matrix(phis: list[float], n: int) -> list[list[float]]:
    """Per-element effective sizes N_ab. Never collapsed to one scalar."""
    return [[N_element(pa, pb, n) for pb in phis] for pa in phis]


def N_g2(phi: float, n: int) -> float:
    """Effective size for the sample-kurtosis estimator on one whitened mode."""
    return n / A_closed_form(phi ** 4, n)


def var_g2(phi: float, n: int) -> float:
    """APPROXIMATION: leading-order delta-method variance of g2 = m4/m2^2 - 3.

    The second-moment (A2) contributions cancel exactly INSIDE the delta-method
    calculation, leaving 24 A4 / n. That cancellation is exact algebra; the
    delta method itself is an asymptotic approximation, so this is NOT an exact
    finite-sample distribution result.
    """
    return 24.0 / N_g2(phi, n)


def bias_g2(phi: float, n: int) -> float:
    """APPROXIMATION: leading-order mean of g2 from centring at the sample mean."""
    return -6.0 / (n / A_closed_form(phi * phi, n))


def sigma_stat(phis: list[float], n: int) -> float:
    """Relative statistical sd of beta_hat: sqrt(2 sum_r 1/N_rr) / m. APPROXIMATION."""
    m = len(phis)
    return math.sqrt(2.0 * sum(1.0 / N_element(p, p, n) for p in phis)) / m
