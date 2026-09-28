"""Prospective size-validation semantics and the final campaign classification.

WHY THE INHERITED 3% RULE WAS INSUFFICIENT
------------------------------------------
The earlier frozen plan validated the geometry gates with "one-sided 95% CP UPPER
bound <= 0.03". That is a COARSE GROSS-INFLATION TOLERANCE inherited from development
analysis, not validation of the nominal alpha allocations. At the declared nominal
levels it would have tolerated

    C2  up to  6/400  = 0.0150    ->   3x the nominal alpha_geom = 0.005
    C3  up to  6/400  = 0.0150    ->  15x the nominal alpha_2    = 0.001
    C4  up to 47/2000 = 0.0235    ->   6x the nominal alpha_1    = 0.004

A rule that passes fifteen times the nominal rate cannot be described as validating it.

WHAT REPLACES IT
----------------
Two DIFFERENT questions, never merged:

    QUESTION A  complete practical performance.  C1, unchanged: one-sided 95% CP LOWER
                bound on complete-pipeline success >= 0.90, R = 300, i.e. >= 279/300.

    QUESTION B  component size inflation.  C2, C3, C4 test prospectively

                    H0: p <= nominal alpha        H1: p > nominal alpha

                at one-sided 5%. Inflation is DETECTED iff the one-sided 95% CP LOWER
                bound on the rejection probability EXCEEDS the nominal alpha.

At the feasible replicate counts these are NOT positive proofs that the achieved rate
sits at or below a tiny nominal alpha. Passing means exactly:

    NO_SIGNIFICANT_SIZE_INFLATION_DETECTED

and never "nominal size proved". That distinction is asserted by a test.

CLASSIFICATION
    cp_lower / cp_upper, the derived boundaries ... EXACT (exact binomial, bisected)
    the campaign rule ............................. EXACT (the frozen conjunction)

NO RNG. Nothing here draws.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Sequence

from ..numerics import Refusal
from .dispositions import cp_lower, cp_upper

#: The only two verdicts a size diagnostic may produce.
SIZE_FAILURE = "STATISTICAL_SIZE_FAILURE"
SIZE_NO_INFLATION = "NO_SIGNIFICANT_SIZE_INFLATION_DETECTED"

#: Machine-readable statement of what a pass does and does not mean.
SIZE_INTERPRETATION = {
    "verdict_on_pass": SIZE_NO_INFLATION,
    "means": "this experiment did not establish excess size at the chosen confidence level",
    "does_not_mean": "that the achieved rate is mathematically proved to be at or below the nominal alpha",
    "forbidden_wording": ["NOMINAL SIZE PROVED", "nominal size proved", "size proved",
                          "exact size established"],
    "test": "H0: p <= nominal alpha  vs  H1: p > nominal alpha, one-sided 5%",
    "detector": "inflation detected iff CP_lower(rejections, R) > nominal alpha",
}

#: Inherited coarse rule, retained ONLY as a labelled secondary diagnostic.
GROSS_INFLATION_TOLERANCE = 0.03
GROSS_INFLATION_LABEL = ("SECONDARY GROSS-INFLATION DIAGNOSTIC, inherited from development "
                         "analysis; NOT validation of the nominal alpha")


def size_boundary(n: int, nominal: float) -> int:
    """Largest rejection count whose one-sided 95% CP LOWER bound stays <= nominal.

    DERIVED, never copied. The frozen plan records 5 (C2), 2 (C3) and 13 (C4); the
    test suite recomputes each of them here.
    """
    if n < 1 or not 0.0 < nominal < 1.0:
        raise Refusal("size_boundary needs n >= 1 and 0 < nominal < 1")
    k = 0
    while k <= n and cp_lower(k, n) <= nominal:
        k += 1
    return k - 1


def size_inflation_detected(rejections: int, n: int, nominal: float) -> bool:
    """True iff the one-sided 95% CP LOWER bound EXCEEDS the nominal alpha."""
    if not 0 <= rejections <= n:
        raise Refusal(f"rejections must lie in [0, {n}]")
    return cp_lower(rejections, n) > nominal


def classify_size(rejections: int, n: int, nominal: float) -> dict:
    """One size diagnostic. Returns the verdict plus both bounds, primary and secondary."""
    detected = size_inflation_detected(rejections, n, nominal)
    lower = cp_lower(rejections, n)
    upper = cp_upper(rejections, n)
    return {
        "rejections": rejections, "replicates": n, "nominal_alpha": nominal,
        "observed_rate": rejections / n,
        "cp_lower": lower, "cp_upper": upper,
        "boundary": size_boundary(n, nominal),
        "verdict": SIZE_FAILURE if detected else SIZE_NO_INFLATION,
        "primary_rule": "inflation detected iff CP_lower > nominal alpha",
        "secondary_gross_diagnostic": {
            "label": GROSS_INFLATION_LABEL,
            "tolerance": GROSS_INFLATION_TOLERANCE,
            "within_tolerance": upper <= GROSS_INFLATION_TOLERANCE,
        },
        "interpretation": SIZE_INTERPRETATION["means"] if not detected else
                          "excess size established at the chosen confidence level",
    }


# ------------------------------------------------------------------ campaign
RELEASE_FAILING_CLASSIFICATIONS = (
    "SOFTWARE_OR_INVARIANT_FAILURE",
    "CALIBRATION_FAILURE",
    "NUMERICAL_OR_PRECISION_FAILURE",
)


@dataclass(frozen=True)
class CampaignCounts:
    """Frozen shape of the counts the campaign will produce. No values are supplied here."""

    c1_successes: int                              # of 300
    c2_rejections_by_field: Mapping[str, int]      # of 400 each
    c3_rejections: int                             # of 400
    c4_rejections: int                             # of 2000
    c5_pass: bool
    c6_pass: bool
    c7_false_acceptances_by_alternative: Mapping[str, int]   # of 400 each
    c8_successes: int                              # of 200
    hard_failures: Sequence[str] = ()
    refusal_accounting_ok: bool = True


def classify_campaign(counts: CampaignCounts) -> dict:
    """The frozen conjunctive release rule.

    Every required case must pass on its own terms. There is NO weighted score and NO
    compensation: one case cannot make up for another's failure.
    """
    failures: list[str] = []
    detail: dict[str, object] = {}

    # 1. C1 complete-pipeline success, unchanged
    c1_bound = cp_lower(counts.c1_successes, 300)
    c1_ok = c1_bound >= 0.90
    detail["C1"] = {"successes": counts.c1_successes, "replicates": 300,
                    "cp_lower": c1_bound, "target": 0.90, "passed": c1_ok,
                    "threshold": 279}
    if not c1_ok:
        failures.append("TRUE_BRIDGE_POWER_FAILURE (C1 complete-pipeline success)")

    # 2. C2 per field, never pooled
    detail["C2"] = {}
    for fid, k in counts.c2_rejections_by_field.items():
        res = classify_size(k, 400, 0.005)
        detail["C2"][fid] = res
        if res["verdict"] == SIZE_FAILURE:
            failures.append(f"STATISTICAL_SIZE_FAILURE (C2 field {fid})")

    # 3. C3 G5 block
    detail["C3"] = classify_size(counts.c3_rejections, 400, 0.001)
    if detail["C3"]["verdict"] == SIZE_FAILURE:
        failures.append("STATISTICAL_SIZE_FAILURE (C3 G5 block)")

    # 4. C4 Block-1 under the surrogate
    detail["C4"] = classify_size(counts.c4_rejections, 2000, 0.004)
    if detail["C4"]["verdict"] == SIZE_FAILURE:
        failures.append("STATISTICAL_SIZE_FAILURE (C4 Block-1 surrogate)")

    # 5, 6. already-frozen criteria
    detail["C5"] = {"passed": counts.c5_pass}
    if not counts.c5_pass:
        failures.append("STATISTICAL_SIZE_FAILURE (C5 plug-in Branch-A)")
    detail["C6"] = {"passed": counts.c6_pass}
    if not counts.c6_pass:
        failures.append("MODE_RESOLUTION_FAILURE (C6 theta_cap boundary)")

    # 7. C7 per alternative, never pooled, G2 disposition
    detail["C7"] = {}
    for alt, k in counts.c7_false_acceptances_by_alternative.items():
        bound = cp_upper(k, 400)
        ok = bound <= 0.025
        detail["C7"][alt] = {"false_acceptances": k, "cp_upper": bound,
                             "target": 0.025, "passed": ok, "threshold": 4}
        if not ok:
            failures.append(f"FALSE_BRIDGE_DISCRIMINATION_FAILURE (C7 {alt})")

    # 8. C8 blinded scale control, G1 disposition
    c8_bound = cp_lower(counts.c8_successes, 200)
    c8_ok = c8_bound >= 0.90
    detail["C8"] = {"successes": counts.c8_successes, "replicates": 200,
                    "cp_lower": c8_bound, "target": 0.90, "passed": c8_ok,
                    "threshold": 188}
    if not c8_ok:
        failures.append("BLINDED_SCALE_CONTROL_FAILURE (C8)")

    # 9, 10. hard failures and refusal accounting
    for name in counts.hard_failures:
        if name in RELEASE_FAILING_CLASSIFICATIONS:
            failures.append(name)
    if not counts.refusal_accounting_ok:
        failures.append("STRUCTURED_REFUSAL_EXCESS (denominator accounting)")

    verdict = "VALIDATION_PASS" if not failures else "VALIDATION_FAILURE"
    return {
        "verdict": verdict,
        "failures": failures,
        "detail": detail,
        "rule": ("conjunctive: every required case must pass on its own terms; no weighted "
                 "score, no compensation between cases"),
        "independent_facts": {
            "complete_pipeline_met": c1_ok,
            "component_size_clean": not any(f.startswith("STATISTICAL_SIZE_FAILURE") for f in failures),
            "note": ("these are reported separately and never collapsed. C1 may meet >= 0.90 while a "
                     "component case detects significant size inflation; that is still a validation "
                     "failure, because the implemented calibration is not behaving according to its "
                     "declared nominal structure. The converse is also a valid scientific failure."),
        },
    }
