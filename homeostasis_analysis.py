"""Frozen analysis implementation for the homeostasis registered study.

Implements sections 7 and 8 of `HOMEOSTASIS_STUDY_PREREGISTRATION_CANDIDATE.md`.
Written before any registered result exists, so that interpretation cannot be
shaped by the data.

Effect sizes are reported first. Three contrasts per load, each load answered
separately, Holm within a load, nine tests in total -- not dozens. No load is
pooled and no combined "EBU score" is produced.

The sign test and the distribution-free median interval reproduce the frozen
Stage-B definitions exactly rather than importing them, so the registered
Stage-B analysis module stays untouched; `test_homeostasis_analysis` asserts
the two agree numerically on shared inputs.
"""

from __future__ import annotations

import gzip
import json
from dataclasses import dataclass
from fractions import Fraction
from math import comb
from pathlib import Path
from typing import Mapping, Sequence

from gaussian_harness.numerics import Refusal
from homeostasis.metrics import exact_median
from homeostasis.policies import (
    POLICY_CONTROL_RANDOM,
    POLICY_EBU_ALIGNED,
    POLICY_EBU_HOSTILE,
    POLICY_EBU_RANDOM,
)

ANALYSIS_ID = "EBU-HOMEOSTASIS-ANALYSIS-v1"
ALPHA = Fraction(5, 100)
DELTA_MEANINGFUL = Fraction(5, 100)

# Registered contrasts, in the frozen order. Each is (treatment, reference).
CONTRASTS = (
    ("incentive_validity", POLICY_EBU_ALIGNED, POLICY_EBU_RANDOM),
    ("stupid_proofing", POLICY_EBU_RANDOM, POLICY_CONTROL_RANDOM),
    ("hostile_safety", POLICY_EBU_HOSTILE, POLICY_EBU_RANDOM),
)

BAND_LOCALIZED = Fraction(1, 2)
BAND_PARTIAL = Fraction(1, 5)
BAND_NOT_LOCALIZED = Fraction(5, 100)


def exact_sign_test(differences: Sequence[Fraction]) -> dict:
    """Exact two-sided paired sign test from integer binomial counts."""
    negative = sum(1 for value in differences if value < 0)
    positive = sum(1 for value in differences if value > 0)
    tied = sum(1 for value in differences if value == 0)
    trials = negative + positive
    if trials == 0:
        return {"negative": negative, "positive": positive, "tied": tied,
                "trials": 0, "p_value": Fraction(1), "significant": False}
    smaller = min(negative, positive)
    tail = sum(comb(trials, index) for index in range(smaller + 1))
    p_value = Fraction(2 * tail, 2 ** trials)
    if p_value > 1:
        p_value = Fraction(1)
    return {"negative": negative, "positive": positive, "tied": tied,
            "trials": trials, "p_value": p_value, "significant": p_value < ALPHA}


def sign_confidence_interval(differences: Sequence[Fraction]) -> dict:
    """Distribution-free sign-based interval for the paired median."""
    ordered = sorted(differences)
    count = len(ordered)
    if count == 0:
        return {"lower": None, "upper": None, "k": None}
    half_alpha = ALPHA / 2
    chosen = None
    for k in range(count // 2 + 1):
        tail = Fraction(sum(comb(count, index) for index in range(k + 1)), 2 ** count)
        if tail <= half_alpha:
            chosen = k
        else:
            break
    if chosen is None:
        return {"lower": ordered[0], "upper": ordered[-1], "k": None}
    return {"lower": ordered[chosen], "upper": ordered[count - chosen - 1], "k": chosen}


def holm(p_values: Mapping[str, Fraction], alpha: Fraction = ALPHA) -> dict[str, bool]:
    """Holm step-down within one family. Exact rational comparison."""
    ordered = sorted(p_values.items(), key=lambda item: (item[1], item[0]))
    total = len(ordered)
    decisions: dict[str, bool] = {}
    rejected_so_far = True
    for position, (label, value) in enumerate(ordered):
        threshold = alpha / (total - position)
        if rejected_so_far and value < threshold:
            decisions[label] = True
        else:
            rejected_so_far = False
            decisions[label] = False
    return decisions


def band(occupancy: Fraction) -> str:
    """Descriptive band. Never a pass or fail verdict."""
    if occupancy >= BAND_LOCALIZED:
        return "localized"
    if occupancy >= BAND_PARTIAL:
        return "partially_localized"
    if occupancy < BAND_NOT_LOCALIZED:
        return "not_localized"
    return "weakly_localized"


def divergence_flag(block_occupancies: Sequence[Fraction],
                    block_medians: Sequence[Fraction]) -> bool:
    """Registered divergence predicate: falling occupancy AND rising radius."""
    if len(block_occupancies) < 2 or len(block_medians) < 2:
        raise Refusal("divergence needs at least two blocks")
    falling = all(b < a for a, b in zip(block_occupancies, block_occupancies[1:]))
    rising = all(b > a for a, b in zip(block_medians, block_medians[1:]))
    return falling and rising


@dataclass(frozen=True)
class ContrastResult:
    load_id: str
    name: str
    treatment: str
    reference: str
    replicates: int
    median_difference: Fraction
    ci_lower: Fraction | None
    ci_upper: Fraction | None
    p_value: Fraction
    holm_significant: bool
    exceeds_delta: bool

    @property
    def verdict(self) -> str:
        if self.holm_significant and self.exceeds_delta:
            return "RELATIVE_REGULATION_DIFFERENCE"
        if self.holm_significant:
            return "SIGNIFICANT_BUT_BELOW_DELTA"
        return "NO_REGISTERED_DIFFERENCE"


def analyse_load(load_id: str, occupancy: Mapping[str, Mapping[int, Fraction]]) -> list[ContrastResult]:
    """Three contrasts for one load, Holm-corrected within the load."""
    raw: dict[str, dict] = {}
    for name, treatment, reference in CONTRASTS:
        if treatment not in occupancy or reference not in occupancy:
            raise Refusal(f"load {load_id} is missing an arm for contrast {name}")
        shared = sorted(set(occupancy[treatment]) & set(occupancy[reference]))
        if not shared:
            raise Refusal(f"load {load_id} contrast {name} has no paired replicates")
        differences = [occupancy[treatment][r] - occupancy[reference][r] for r in shared]
        raw[name] = {
            "treatment": treatment, "reference": reference,
            "replicates": len(shared), "differences": differences,
            "median": exact_median(differences),
            "test": exact_sign_test(differences),
            "ci": sign_confidence_interval(differences),
        }
    decisions = holm({name: row["test"]["p_value"] for name, row in raw.items()})
    results = []
    for name, _, _ in CONTRASTS:
        row = raw[name]
        results.append(ContrastResult(
            load_id=load_id, name=name,
            treatment=row["treatment"], reference=row["reference"],
            replicates=row["replicates"],
            median_difference=row["median"],
            ci_lower=row["ci"]["lower"], ci_upper=row["ci"]["upper"],
            p_value=row["test"]["p_value"],
            holm_significant=decisions[name],
            exceeds_delta=abs(row["median"]) >= DELTA_MEANINGFUL,
        ))
    return results


def _rational(value) -> str | None:
    if value is None:
        return None
    return f"{value.numerator}/{value.denominator}"


def report(per_load: Mapping[str, Mapping[str, Mapping[int, Fraction]]]) -> dict:
    """Full registered report. Effect sizes precede every test result."""
    out: dict = {"analysis_id": ANALYSIS_ID,
                 "alpha": _rational(ALPHA),
                 "delta_meaningful": _rational(DELTA_MEANINGFUL),
                 "multiplicity": "Holm within each load over its three contrasts",
                 "loads_pooled": False,
                 "loads": {}}
    for load_id in sorted(per_load):
        occupancy = per_load[load_id]
        arms = {}
        for policy in sorted(occupancy):
            values = list(occupancy[policy].values())
            median = exact_median(values)
            arms[policy] = {
                "replicates": len(values),
                "median_O95": _rational(median),
                "median_O95_float": float(median),
                "band": band(median),
            }
        contrasts = analyse_load(load_id, occupancy)
        out["loads"][load_id] = {
            "arms": arms,
            "contrasts": [
                {
                    "name": c.name, "treatment": c.treatment, "reference": c.reference,
                    "replicates": c.replicates,
                    "median_difference": _rational(c.median_difference),
                    "median_difference_float": float(c.median_difference),
                    "ci_lower": _rational(c.ci_lower), "ci_upper": _rational(c.ci_upper),
                    "p_value": _rational(c.p_value),
                    "p_value_float": float(c.p_value),
                    "holm_significant": c.holm_significant,
                    "exceeds_delta": c.exceeds_delta,
                    "verdict": c.verdict,
                }
                for c in contrasts
            ],
        }
    return out
