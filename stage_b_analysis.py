"""Frozen Stage-B analysis. Behaviour fixed BEFORE any registered result exists.

Implements sections 7, 9, 10, 11 and 13 of `STAGE_B_PREREGISTRATION.md`.

The primary endpoint, paired differences, sign test and its confidence interval
are exact rational / exact integer computations. Float64 appears only in the
autocorrelation diagnostic, which the preregistration explicitly declares as a
descriptive statistic where exact rationals are impractical, and at print time.

This module is not edited because a result looks surprising.
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
ALPHA = Fraction(5, 100)
DELTA_MEANINGFUL = Fraction(5, 100)
AUTOCORRELATION_LAGS = (1, 2, 4, 8, 16, 32, 64, 128, 256)
UNDEFINED = "undefined"
CENSORED = "censored"


def rational(text: str) -> Fraction:
    numerator, denominator = text.split("/")
    return Fraction(int(numerator), int(denominator))


@dataclass(frozen=True)
class ArmRun:
    replicate: int
    arm: str
    deviation: tuple[Fraction, ...]
    balance_total: tuple[Fraction, ...]
    min_balance: tuple[Fraction, ...]
    audit: tuple[Fraction, ...]
    d_ext: tuple[Fraction, ...]
    x_min: tuple[Fraction, ...]
    status: tuple[str, ...]
    null_forcing: tuple[bool, ...]
    n_feasible: tuple[int, ...]
    n_affordable: tuple[int, ...]
    n_rejected: tuple[int, ...]
    ebu_sign: tuple[int, ...]
    balances_end: tuple[Fraction, ...]
    v_max: Fraction
    horizon: int
    burn_in: int
    block: int
    run_id: str
    code_id: str
    configuration_identity: str
    forcing_seed: int
    actor_seed: int
    max_accounting_residual: Fraction
    max_conservation_residual: Fraction
    max_nonnegativity_residual: Fraction
    negative_capacity_ticks: int


def read_payload(path: Path) -> dict:
    if path.suffix == ".gz":
        return json.loads(gzip.decompress(path.read_bytes()).decode("utf-8"))
    return json.loads(path.read_text())


def load_arm(path: Path) -> ArmRun:
    payload = read_payload(path)
    columns = payload["columns"]

    def frac(key):
        return tuple(rational(value) for value in columns[key])

    return ArmRun(
        replicate=payload["replicate"],
        arm=payload["arm"],
        deviation=frac("V"),
        balance_total=frac("sumB"),
        min_balance=frac("minB"),
        audit=frac("J"),
        d_ext=frac("d_ext"),
        x_min=frac("x_min"),
        status=tuple(columns["status"]),
        null_forcing=tuple(bool(value) for value in columns["null_forcing"]),
        n_feasible=tuple(columns["n_feasible"]),
        n_affordable=tuple(columns["n_affordable"]),
        n_rejected=tuple(columns["n_rejected"]),
        ebu_sign=tuple(columns["ebu_sign"]),
        balances_end=tuple(rational(v) for v in payload["balances_end"]),
        v_max=rational(payload["v_max"]),
        horizon=payload["horizon"],
        burn_in=payload["burn_in"],
        block=payload["block"],
        run_id=payload["run_id"],
        code_id=payload["code_id"],
        configuration_identity=payload["configuration_identity"],
        forcing_seed=payload["forcing_seed"],
        actor_seed=payload["actor_seed"],
        max_accounting_residual=rational(payload["max_accounting_residual"]),
        max_conservation_residual=rational(payload["max_conservation_residual"]),
        max_nonnegativity_residual=rational(payload["max_nonnegativity_residual"]),
        negative_capacity_ticks=payload["negative_capacity_ticks"],
    )


def window_slice(run: ArmRun) -> slice:
    return slice(run.burn_in, run.horizon)


def block_slices(run: ArmRun) -> list[slice]:
    return [
        slice(run.burn_in + index * run.block, run.burn_in + (index + 1) * run.block)
        for index in range((run.horizon - run.burn_in) // run.block)
    ]


def primary_endpoint(run: ArmRun, region: slice | None = None) -> Fraction:
    """L_r = (1/T) sum V(t)/V_max over the analysis window. Exact."""
    region = window_slice(run) if region is None else region
    values = run.deviation[region]
    total = Fraction(0)
    for value in values:
        total += value
    return total / (len(values) * run.v_max)


def exact_sign_test(differences: list[Fraction]) -> dict:
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


def sign_confidence_interval(differences: list[Fraction]) -> dict:
    """Distribution-free sign-based CI for the paired median.

    k is the largest integer with P(Bin(N,1/2) <= k) <= alpha/2; the interval is
    the (k+1)-th and (N-k)-th order statistics.
    """
    ordered = sorted(differences)
    count = len(ordered)
    if count == 0:
        return {"lower": None, "upper": None, "k": None, "coverage_note": "empty"}
    half_alpha = ALPHA / 2
    chosen = None
    for k in range(count // 2 + 1):
        tail = Fraction(sum(comb(count, index) for index in range(k + 1)), 2 ** count)
        if tail <= half_alpha:
            chosen = k
        else:
            break
    if chosen is None:
        return {"lower": ordered[0], "upper": ordered[-1], "k": None,
                "coverage_note": "no k satisfies the level; full order-statistic range reported"}
    return {"lower": ordered[chosen], "upper": ordered[count - 1 - chosen],
            "k": chosen, "coverage_note": f"order statistics {chosen + 1} and {count - chosen}"}


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


def quantile(values: list[Fraction], fraction: Fraction) -> Fraction:
    ordered = sorted(values)
    if not ordered:
        return Fraction(0)
    index = int(fraction * (len(ordered) - 1))
    return ordered[index]


def autocorrelation(values: tuple[Fraction, ...]) -> dict:
    """Frozen estimator, float64, on the exact rational series."""
    series = [float(value) for value in values]
    count = len(series)
    if count == 0:
        return {lag: UNDEFINED for lag in AUTOCORRELATION_LAGS} | {"relaxation_lag": UNDEFINED}
    average = sum(series) / count
    denominator = sum((value - average) ** 2 for value in series)
    if denominator == 0:
        return {lag: UNDEFINED for lag in AUTOCORRELATION_LAGS} | {"relaxation_lag": UNDEFINED}
    result: dict = {}
    threshold = 1.0 / 2.718281828459045
    relaxation = CENSORED
    for lag in AUTOCORRELATION_LAGS:
        if lag >= count:
            result[lag] = UNDEFINED
            continue
        numerator = sum(
            (series[index] - average) * (series[index + lag] - average)
            for index in range(count - lag)
        )
        value = numerator / denominator
        result[lag] = value
        if relaxation == CENSORED and value < threshold:
            relaxation = lag
    result["relaxation_lag"] = relaxation
    return result


def block_diagnostics(run: ArmRun, region: slice) -> dict:
    deviation = run.deviation[region]
    normalized = [value / run.v_max for value in deviation]
    balances = run.balance_total[region]
    statuses = run.status[region]
    count = len(deviation)

    feasible_total = sum(run.n_feasible[region])
    rejected_total = sum(run.n_rejected[region])
    undefined_ticks = sum(1 for value in run.n_feasible[region] if value == 0)
    rho = UNDEFINED if feasible_total == 0 else Fraction(rejected_total, feasible_total)

    positive_injection = Fraction(0)
    negative_relief = Fraction(0)
    for value in run.d_ext[region]:
        if value > 0:
            positive_injection += value
        elif value < 0:
            negative_relief += -value

    growth = (balances[-1] - balances[0]) / count if count else Fraction(0)
    ending = balances[-1] if count else Fraction(0)
    average = mean(list(normalized))
    variance = mean([(value - average) ** 2 for value in normalized])

    return {
        "ticks": count,
        "mean_V_over_Vmax": average,
        "variance_V_over_Vmax": variance,
        "median_V_over_Vmax": median(list(normalized)),
        "q90_V_over_Vmax": quantile(list(normalized), Fraction(9, 10)),
        "q99_V_over_Vmax": quantile(list(normalized), Fraction(99, 100)),
        "equilibrium_occupancy": Fraction(sum(1 for v in deviation if v == 0), count),
        "boundary_occupancy": Fraction(sum(1 for v in run.x_min[region] if v == 0), count),
        "deadlock_fraction": Fraction(sum(1 for s in statuses if s == "DEADLOCK"), count),
        "no_execution_fraction": Fraction(sum(1 for s in statuses if s != "EXECUTED"), count),
        "null_forcing_fraction": Fraction(sum(1 for f in run.null_forcing[region] if f), count),
        "applied_forcing_count": sum(1 for f in run.null_forcing[region] if not f),
        "raw_forcing_count": count,
        "positive_injection": positive_injection,
        "negative_relief": negative_relief,
        "signed_J_end": run.audit[region][-1] if count else Fraction(0),
        "mean_B_total": mean(list(balances)),
        "ending_B_total": ending,
        "B_growth_per_tick": growth,
        "rho_reject": rho,
        "rho_undefined_ticks": undefined_ticks,
        "mean_feasible": Fraction(feasible_total, count),
        "mean_rejected": Fraction(rejected_total, count),
        "executed_positive_ebu": sum(1 for s in run.ebu_sign[region] if s > 0),
        "executed_negative_ebu": sum(1 for s in run.ebu_sign[region] if s < 0),
        "autocorrelation": autocorrelation(deviation),
    }


def concentration(balances: tuple[Fraction, ...]) -> Fraction:
    total = Fraction(0)
    for value in balances:
        total += value
    if total == 0:
        return Fraction(0)
    return max(balances) / total


def integrity_report(pairs: dict[int, dict[str, ArmRun]], expected: int, horizon: int) -> dict:
    problems: list[str] = []
    missing = [r for r in range(expected) if r not in pairs]
    if missing:
        problems.append(f"missing replicates: {missing[:8]}")
    for replicate, arms in sorted(pairs.items()):
        for arm in (ARM_EBU, ARM_CONTROL):
            if arm not in arms:
                problems.append(f"replicate {replicate} missing arm {arm}")
    worst_a = worst_c = worst_n = Fraction(0)
    negative_capacity = 0
    for arms in pairs.values():
        for arm, run in arms.items():
            worst_a = max(worst_a, run.max_accounting_residual)
            worst_c = max(worst_c, run.max_conservation_residual)
            worst_n = max(worst_n, run.max_nonnegativity_residual)
            if arm == ARM_EBU:
                negative_capacity += run.negative_capacity_ticks
            if len(run.deviation) != horizon:
                problems.append(f"replicate {run.replicate} {arm} horizon {len(run.deviation)}")
    if worst_a != 0:
        problems.append(f"nonzero accounting residual {worst_a}")
    if worst_c != 0:
        problems.append(f"nonzero conservation residual {worst_c}")
    if worst_n != 0:
        problems.append(f"negative physical stock {worst_n}")
    if negative_capacity:
        problems.append(f"negative EBU capacity in {negative_capacity} ticks")
    codes = {r.code_id for a in pairs.values() for r in a.values()}
    configs = {r.configuration_identity for a in pairs.values() for r in a.values()}
    if len(codes) > 1:
        problems.append(f"code identity not unique: {codes}")
    if len(configs) > 1:
        problems.append(f"configuration identity not unique: {configs}")
    for replicate, arms in sorted(pairs.items()):
        if len(arms) == 2:
            left, right = arms[ARM_EBU], arms[ARM_CONTROL]
            if (left.forcing_seed, left.actor_seed) != (right.forcing_seed, right.actor_seed):
                problems.append(f"replicate {replicate} arms used unmatched seeds")
    return {
        "passed": not problems, "problems": problems,
        "replicates_observed": len(pairs), "replicates_expected": expected,
        "max_accounting_residual": worst_a, "max_conservation_residual": worst_c,
        "max_nonnegativity_residual": worst_n, "ebu_capacity_violations": negative_capacity,
        "code_identity": sorted(codes)[0] if codes else None,
        "configuration_identity": sorted(configs)[0] if configs else None,
    }


def load_study(directory: Path) -> dict[int, dict[str, ArmRun]]:
    pairs: dict[int, dict[str, ArmRun]] = {}
    for path in sorted(directory.glob("replicate_*.json.gz")):
        run = load_arm(path)
        pairs.setdefault(run.replicate, {})[run.arm] = run
    return pairs


def analyse(directory: Path, expected: int, horizon: int) -> dict:
    pairs = load_study(directory)
    integrity = integrity_report(pairs, expected, horizon)
    endpoints, differences, per_replicate = [], [], []
    block_differences: list[list[Fraction]] = []
    for replicate, arms in sorted(pairs.items()):
        if len(arms) != 2:
            continue
        ebu, control = arms[ARM_EBU], arms[ARM_CONTROL]
        left, right = primary_endpoint(ebu), primary_endpoint(control)
        endpoints.append({"replicate": replicate, "ebu": left, "control": right})
        differences.append(left - right)
        blocks_e = [block_diagnostics(ebu, region) for region in block_slices(ebu)]
        blocks_c = [block_diagnostics(control, region) for region in block_slices(control)]
        deltas = [
            primary_endpoint(ebu, region) - primary_endpoint(control, other)
            for region, other in zip(block_slices(ebu), block_slices(control))
        ]
        while len(block_differences) < len(deltas):
            block_differences.append([])
        for index, value in enumerate(deltas):
            block_differences[index].append(value)
        per_replicate.append({
            "replicate": replicate,
            "blocks": {ARM_EBU: blocks_e, ARM_CONTROL: blocks_c},
            "block_deltas": deltas,
            "concentration": {ARM_EBU: concentration(ebu.balances_end),
                              ARM_CONTROL: concentration(control.balances_end)},
            "balances_end": {ARM_EBU: ebu.balances_end, ARM_CONTROL: control.balances_end},
        })
    return {
        "integrity": integrity,
        "endpoints": endpoints,
        "differences": differences,
        "sign_test": exact_sign_test(differences),
        "confidence_interval": sign_confidence_interval(differences),
        "median_difference": median(differences),
        "mean_difference": mean(differences),
        "median_L_ebu": median([row["ebu"] for row in endpoints]),
        "median_L_control": median([row["control"] for row in endpoints]),
        "practically_meaningful": abs(median(differences)) >= DELTA_MEANINGFUL,
        "block_differences": block_differences,
        "per_replicate": per_replicate,
    }
