"""Author dispositions G1-G3, closed prospectively before execution.

These are SYNTHETIC-VALIDATION RELEASE CRITERIA. They change no primary-data
analysis rule: P1, P2, P3, P4, the margins, coverage factors, alpha allocations,
theta_cap, rank_tol, the four physical fields, the complete-pipeline target and the
anti-circularity rules are all untouched.

    G1  blinded scale control  -- reuses the P3 absolute-equivalence construction on
        beta_tilde = c * beta_hat_blinded. NO new tolerance is introduced.
    G2  false-bridge discrimination -- a maximum false-acceptance probability of 0.025,
        tied to the equivalence test's one-sided nominal level at z = 1.959963985, and
        applied to EACH declared alternative independently.
    G3  sigma_psi = 0.5 degrees as the PRIMARY release scenario, with 0.0 / 0.2 as
        secondary sensitivity and 1.0 as stress.

CLASSIFICATION
    cp_lower, cp_upper, the integer thresholds ... EXACT (exact binomial, bisected)
    the blinded and false-bridge rules ........... EXACT (the adopted inequalities)

NO RNG. Nothing here draws, and nothing here is executed by the pre-execution stage.
"""

from __future__ import annotations

import math
from dataclasses import replace
from typing import Mapping, Sequence

from ..contract import ContractBinding
from ..endpoints import EndpointResult, UncertaintyModel, p3_absolute
from ..geometry import FieldAnalysis
from ..numerics import Refusal
from ..status import AnalysisStatus

BLINDED_SCALE_FACTORS = (1.07, 0.90)


# --------------------------------------------------------------- exact binomial
def _binom_cdf(k: int, n: int, p: float) -> float:
    if k < 0:
        return 0.0
    if k >= n:
        return 1.0
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))


def cp_lower(k: int, n: int, alpha: float = 0.05) -> float:
    """One-sided lower Clopper-Pearson bound. EXACT, by bisection on the binomial CDF."""
    if k == 0:
        return 0.0
    lo, hi = 0.0, 1.0
    for _ in range(300):
        mid = (lo + hi) / 2
        if 1 - _binom_cdf(k - 1, n, mid) < alpha:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def cp_upper(k: int, n: int, alpha: float = 0.05) -> float:
    """One-sided upper Clopper-Pearson bound. EXACT, by bisection on the binomial CDF."""
    lo, hi = 0.0, 1.0
    for _ in range(300):
        mid = (lo + hi) / 2
        if _binom_cdf(k, n, mid) > alpha:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def g1_success_threshold(n: int = 200, target: float = 0.90, alpha: float = 0.05) -> int:
    """Smallest success count whose one-sided CP LOWER bound reaches `target`.

    DERIVED, never copied: the frozen plan records 188 for (n=200, target=0.90) and a
    static test recomputes it here.
    """
    best = None
    for k in range(n, -1, -1):
        if cp_lower(k, n, alpha) >= target:
            best = k
        else:
            break
    if best is None:
        raise Refusal(f"no success count at n={n} reaches a CP lower bound of {target}")
    return best


def g2_max_false_acceptances(n: int = 400, target: float = 0.025, alpha: float = 0.05) -> int:
    """Largest false-acceptance count whose one-sided CP UPPER bound stays within `target`."""
    best = None
    for k in range(0, n + 1):
        if cp_upper(k, n, alpha) <= target:
            best = k
        else:
            break
    if best is None:
        raise Refusal(f"even 0/{n} exceeds an upper bound of {target}")
    return best


# --------------------------------------------------------------- G1
def scaled_analyses(analyses: Mapping[str, FieldAnalysis], c: float) -> dict[str, FieldAnalysis]:
    """beta_tilde = c * beta_hat. A non-ESTIMATED field stays non-ESTIMATED."""
    if c <= 0.0:
        raise Refusal("blinding factor must be positive")
    out: dict[str, FieldAnalysis] = {}
    for fid, a in analyses.items():
        if not a.is_estimated or a.beta_hat is None:
            out[fid] = a
        else:
            out[fid] = replace(a, beta_hat=c * a.beta_hat)
    return out


def g1_blinded_branch(analyses: Mapping[str, FieldAnalysis], binding: ContractBinding,
                      unc: UncertaintyModel, c: float) -> EndpointResult:
    """One blinded branch. Reuses `p3_absolute` verbatim on the transformed betas.

    That reuse is the point of the disposition: the recovery criterion is the SAME
    absolute-equivalence construction already adopted for P3, not a new tolerance.
    """
    res = p3_absolute(scaled_analyses(analyses, c), binding, unc)
    return EndpointResult(f"G1_blinded_c={c}", res.passed,
                          f"beta_tilde = {c} * beta_hat; " + res.detail, res.rows)


def g1_paired_replicate(analyses_by_c: Mapping[float, Mapping[str, FieldAnalysis]],
                        binding: ContractBinding, unc: UncertaintyModel,
                        factors: Sequence[float] = BLINDED_SCALE_FACTORS) -> EndpointResult:
    """One C8 replicate: EVERY declared factor must pass at EVERY tested field."""
    rows, passed = [], True
    for c in factors:
        if c not in analyses_by_c:
            rows.append((c, False, "branch absent"))
            passed = False
            continue
        r = g1_blinded_branch(analyses_by_c[c], binding, unc, c)
        rows.append((c, r.passed, r.detail))
        passed = passed and r.passed
    return EndpointResult("G1_paired_replicate", passed,
                          f"paired control over factors {tuple(factors)}; all must pass",
                          tuple(rows))


def g1_campaign_pass(successes: int, replicates: int = 200, target: float = 0.90) -> tuple[bool, float, int]:
    thr = g1_success_threshold(replicates, target)
    bound = cp_lower(successes, replicates)
    return (successes >= thr, bound, thr)


# --------------------------------------------------------------- G2
def g2_alternative_pass(false_acceptances: int, replicates: int = 400,
                        target: float = 0.025) -> tuple[bool, float, int]:
    """ONE declared alternative. Counts are never pooled across alternatives."""
    thr = g2_max_false_acceptances(replicates, target)
    bound = cp_upper(false_acceptances, replicates)
    return (false_acceptances <= thr, bound, thr)


def g2_campaign_pass(counts: Mapping[str, int], replicates: int = 400,
                     target: float = 0.025) -> EndpointResult:
    """EVERY declared alternative must independently satisfy the rule."""
    required = {"alt_1_06", "alt_0_93_1_05", "alt_1_10", "hard_1_025"}
    if set(counts) != required:
        raise Refusal("G2 requires exactly the four declared false-bridge alternatives")
    rows, passed = [], True
    for name, k in counts.items():
        ok, bound, thr = g2_alternative_pass(k, replicates, target)
        rows.append((name, k, bound, thr, ok))
        passed = passed and ok
    return EndpointResult("G2_false_bridge", passed,
                          f"per-alternative CP upper <= {target}; counts never pooled",
                          tuple(rows))


# --------------------------------------------------------------- G3
def g3_classification(binding: ContractBinding) -> dict:
    return dict(binding.data["hypothetical_uncertainty_scenario"]["sigma_psi_deg_classification"])


def g3_primary_sigma_psi(binding: ContractBinding) -> float:
    return float(binding.data["hypothetical_uncertainty_scenario"]["sigma_psi_deg"])


def g3_role(binding: ContractBinding, sigma_psi_deg: float) -> str:
    cls = g3_classification(binding)
    if sigma_psi_deg == cls["primary_release_scenario"]:
        return "PRIMARY"
    if sigma_psi_deg in cls["secondary_lower_uncertainty_sensitivity"]:
        return "SECONDARY"
    if sigma_psi_deg in cls["stress_robustness"]:
        return "STRESS"
    raise Refusal(f"sigma_psi = {sigma_psi_deg} is not on the declared grid")


def g3_primary_claim_inputs(binding: ContractBinding, results_by_sigma_psi: Mapping[float, int]) -> dict:
    """Only the PRIMARY scenario feeds the >= 0.90 claim. Stress never overwrites it."""
    primary = g3_primary_sigma_psi(binding)
    if primary not in results_by_sigma_psi:
        raise Refusal(f"primary scenario sigma_psi = {primary} is missing from the results")
    return {"primary_sigma_psi_deg": primary,
            "primary_successes": results_by_sigma_psi[primary],
            "excluded_from_primary": {k: v for k, v in results_by_sigma_psi.items() if k != primary},
            "pooling_prohibited": True}
