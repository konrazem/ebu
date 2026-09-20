"""Frozen Stage-A analysis. Behaviour fixed BEFORE any registered result exists.

Implements sections 9, 10, 11 and 14 of `STAGE_A_PREREGISTRATION.md`.

Everything that can stay exact stays exact: V, capacities, D, cumulative V, the
normalized endpoint A_r, paired differences, and the sign-test p-value, which is
computed from integer binomial counts rather than a normal approximation.
Floating point appears only where a value is printed.

This module is not edited because a result looks surprising. Any post-hoc
analysis belongs in a separate file labelled EXPLORATORY / POST-REGISTERED.
"""

from __future__ import annotations

import gzip
import json
from dataclasses import dataclass
from fractions import Fraction
from math import comb
from pathlib import Path

ARM_EBU = "ebu_affordability_random_actor"
ARM_CONTROL = "physical_feasibility_random_actor"
CENSORED = "censored"
ALPHA = Fraction(5, 100)

CLASS_DEADLOCKED = "DEADLOCKED_AWAY_FROM_EQUILIBRIUM"
CLASS_STAYED = "REACHED_AND_STAYED"
CLASS_CYCLING = "REPEATED_CYCLING"
CLASS_LEFT = "REACHED_AND_LEFT"
CLASS_PARTIAL = "PARTIAL_RECOVERY"
CLASS_NEVER = "NEVER_REACHED_EQUILIBRIUM"
CLASS_OTHER = "OTHER_REGISTERED_PATTERN"


def rational(text: str) -> Fraction:
    numerator, denominator = text.split("/")
    return Fraction(int(numerator), int(denominator))


@dataclass(frozen=True)
class ArmSeries:
    """One arm of one replicate, as exact rationals."""

    replicate: int
    arm: str
    deviation: tuple[Fraction, ...]          # V(1..H)
    balance_total: tuple[Fraction, ...]      # sum_i B_i(1..H)
    min_balance: tuple[Fraction, ...]
    status: tuple[str, ...]
    ebu_sign: tuple[int, ...]                # sign of E_G of the executed group
    shock_deviation: Fraction                # D_r
    horizon: int
    accounting_residual: tuple[Fraction, ...]
    conservation_residual: tuple[Fraction, ...]
    nonnegativity_residual: tuple[Fraction, ...]
    run_id: str
    code_id: str
    configuration_id: str
    forcing_seed: int
    actor_seed: int
    shock: str


def read_payload(path: Path) -> dict:
    """Artifacts are gzipped JSON; plain JSON is accepted for inspection."""
    if path.suffix == ".gz":
        return json.loads(gzip.decompress(path.read_bytes()).decode("utf-8"))
    return json.loads(path.read_text())


def load_arm(path: Path) -> ArmSeries:
    payload = read_payload(path)
    ticks = payload["ticks"]
    return ArmSeries(
        replicate=payload["replicate"],
        arm=payload["arm"],
        deviation=tuple(rational(row["V"]) for row in ticks),
        balance_total=tuple(rational(row["sumB"]) for row in ticks),
        min_balance=tuple(rational(row["min_balance"]) for row in ticks),
        status=tuple(row["status"] for row in ticks),
        ebu_sign=tuple(row["ebu_sign"] for row in ticks),
        shock_deviation=rational(payload["D"]),
        horizon=payload["horizon"],
        accounting_residual=tuple(rational(row["accounting_residual"]) for row in ticks),
        conservation_residual=tuple(rational(row["conservation_residual"]) for row in ticks),
        nonnegativity_residual=tuple(rational(row["nonnegativity_residual"]) for row in ticks),
        run_id=payload["run_id"],
        code_id=payload["code_id"],
        configuration_id=payload["configuration_id"],
        forcing_seed=payload["forcing_seed"],
        actor_seed=payload["actor_seed"],
        shock=payload["shock"],
    )


def primary_endpoint(series: ArmSeries) -> Fraction:
    """A_r = (1/(H*D_r)) * sum_{t=1}^{H} V(t), exact."""
    cumulative = Fraction(0)
    for value in series.deviation:
        cumulative += value
    return cumulative / (series.horizon * series.shock_deviation)


def departures(series: ArmSeries) -> int:
    """Count of t in 1..H-1 with V(t) = 0 and V(t+1) > 0."""
    return sum(
        1
        for index in range(len(series.deviation) - 1)
        if series.deviation[index] == 0 and series.deviation[index + 1] > 0
    )


def classify(series: ArmSeries) -> str:
    """Deterministic trajectory classification, first match wins."""
    deviation = series.deviation
    horizon = len(deviation)
    tail = series.status[-8:] if horizon >= 8 else series.status
    if deviation[-1] > 0 and tail and all(state == "DEADLOCK" for state in tail):
        return CLASS_DEADLOCKED
    hits = [index for index, value in enumerate(deviation) if value == 0]
    if hits:
        first = hits[0]
        if all(value == 0 for value in deviation[first:]):
            return CLASS_STAYED
        count = departures(series)
        if count >= 4:
            return CLASS_CYCLING
        if 1 <= count <= 3:
            return CLASS_LEFT
        return CLASS_OTHER
    if deviation[-1] < series.shock_deviation:
        return CLASS_PARTIAL
    return CLASS_NEVER


def secondary_diagnostics(series: ArmSeries) -> dict:
    deviation = series.deviation
    horizon = len(deviation)
    hits = [index + 1 for index, value in enumerate(deviation) if value == 0]
    deadlocks = [index + 1 for index, state in enumerate(series.status) if state == "DEADLOCK"]
    positive = sum(1 for sign in series.ebu_sign if sign > 0)
    negative = sum(1 for sign in series.ebu_sign if sign < 0)
    occupancy = Fraction(len(hits), horizon)
    minimum = min(deviation)
    return {
        "first_hitting_time": hits[0] if hits else CENSORED,
        "equilibrium_occupancy": occupancy,
        "terminal_normalized_deviation": deviation[-1] / series.shock_deviation,
        "minimum_normalized_deviation": minimum / series.shock_deviation,
        "deadlock_count": len(deadlocks),
        "first_deadlock_time": deadlocks[0] if deadlocks else CENSORED,
        "executed_positive_ebu": positive,
        "executed_negative_ebu": negative,
        "executed_total": positive + negative,
        "departures": departures(series),
        "terminal_total_capacity": series.balance_total[-1],
        "max_total_capacity": max(series.balance_total),
        "min_total_capacity": min(series.balance_total),
        "class": classify(series),
    }


def exact_sign_test(differences: list[Fraction]) -> dict:
    """Exact two-sided paired sign test from integer binomial counts."""
    negative = sum(1 for value in differences if value < 0)
    positive = sum(1 for value in differences if value > 0)
    tied = sum(1 for value in differences if value == 0)
    trials = negative + positive
    if trials == 0:
        return {
            "negative": negative,
            "positive": positive,
            "tied": tied,
            "trials": 0,
            "p_value": Fraction(1),
            "significant": False,
        }
    smaller = min(negative, positive)
    tail = sum(comb(trials, index) for index in range(smaller + 1))
    p_value = Fraction(2 * tail, 2 ** trials)
    if p_value > 1:
        p_value = Fraction(1)
    return {
        "negative": negative,
        "positive": positive,
        "tied": tied,
        "trials": trials,
        "p_value": p_value,
        "significant": p_value < ALPHA,
    }


def median(values: list[Fraction]) -> Fraction:
    ordered = sorted(values)
    count = len(ordered)
    if count == 0:
        return Fraction(0)
    middle = count // 2
    if count % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2


def mean(values: list[Fraction]) -> Fraction:
    if not values:
        return Fraction(0)
    total = Fraction(0)
    for value in values:
        total += value
    return total / len(values)


def integrity_report(pairs: dict[int, dict[str, ArmSeries]], expected: int) -> dict:
    """Mechanical integrity gate. Run before any scientific interpretation."""
    problems: list[str] = []
    missing = [r for r in range(expected) if r not in pairs]
    if missing:
        problems.append(f"missing replicates: {missing[:8]}")
    for replicate, arms in sorted(pairs.items()):
        for arm in (ARM_EBU, ARM_CONTROL):
            if arm not in arms:
                problems.append(f"replicate {replicate} missing arm {arm}")
    worst_accounting = Fraction(0)
    worst_conservation = Fraction(0)
    worst_nonnegativity = Fraction(0)
    capacity_violations = 0
    for replicate, arms in sorted(pairs.items()):
        for arm, series in sorted(arms.items()):
            for value in series.accounting_residual:
                worst_accounting = max(worst_accounting, abs(value))
            for value in series.conservation_residual:
                worst_conservation = max(worst_conservation, abs(value))
            for value in series.nonnegativity_residual:
                worst_nonnegativity = max(worst_nonnegativity, abs(value))
            if arm == ARM_EBU:
                for value in series.min_balance:
                    if value < 0:
                        capacity_violations += 1
    if worst_accounting != 0:
        problems.append(f"nonzero accounting residual {worst_accounting}")
    if worst_conservation != 0:
        problems.append(f"nonzero conservation residual {worst_conservation}")
    if worst_nonnegativity != 0:
        problems.append(f"negative physical stock {worst_nonnegativity}")
    if capacity_violations:
        problems.append(f"negative EBU capacity in {capacity_violations} ticks")
    codes = {series.code_id for arms in pairs.values() for series in arms.values()}
    configurations = {series.configuration_id for arms in pairs.values() for series in arms.values()}
    if len(codes) > 1:
        problems.append(f"code identity not unique: {codes}")
    if len(configurations) > 1:
        problems.append(f"configuration identity not unique: {configurations}")
    for replicate, arms in sorted(pairs.items()):
        if ARM_EBU in arms and ARM_CONTROL in arms:
            left, right = arms[ARM_EBU], arms[ARM_CONTROL]
            if left.shock != right.shock:
                problems.append(f"replicate {replicate} arms saw different shocks")
            if left.shock_deviation != right.shock_deviation:
                problems.append(f"replicate {replicate} arms saw different D")
            if (left.forcing_seed, left.actor_seed) != (right.forcing_seed, right.actor_seed):
                problems.append(f"replicate {replicate} arms used unmatched seeds")
    return {
        "passed": not problems,
        "problems": problems,
        "replicates_observed": len(pairs),
        "replicates_expected": expected,
        "max_accounting_residual": worst_accounting,
        "max_conservation_residual": worst_conservation,
        "max_nonnegativity_residual": worst_nonnegativity,
        "ebu_capacity_violations": capacity_violations,
        "code_identity": sorted(codes)[0] if codes else None,
        "configuration_identity": sorted(configurations)[0] if configurations else None,
    }


def load_study(directory: Path) -> dict[int, dict[str, ArmSeries]]:
    pairs: dict[int, dict[str, ArmSeries]] = {}
    for path in sorted(directory.glob("replicate_*.json.gz")):
        series = load_arm(path)
        pairs.setdefault(series.replicate, {})[series.arm] = series
    return pairs


def analyse(directory: Path, expected: int) -> dict:
    pairs = load_study(directory)
    integrity = integrity_report(pairs, expected)
    endpoints = []
    differences = []
    diagnostics = []
    for replicate, arms in sorted(pairs.items()):
        if ARM_EBU not in arms or ARM_CONTROL not in arms:
            continue
        ebu = primary_endpoint(arms[ARM_EBU])
        control = primary_endpoint(arms[ARM_CONTROL])
        endpoints.append({"replicate": replicate, "ebu": ebu, "control": control})
        differences.append(ebu - control)
        diagnostics.append(
            {
                "replicate": replicate,
                ARM_EBU: secondary_diagnostics(arms[ARM_EBU]),
                ARM_CONTROL: secondary_diagnostics(arms[ARM_CONTROL]),
            }
        )
    return {
        "integrity": integrity,
        "endpoints": endpoints,
        "differences": differences,
        "sign_test": exact_sign_test(differences),
        "median_difference": median(differences),
        "mean_difference": mean(differences),
        "median_ebu": median([row["ebu"] for row in endpoints]),
        "median_control": median([row["control"] for row in endpoints]),
        "diagnostics": diagnostics,
    }
