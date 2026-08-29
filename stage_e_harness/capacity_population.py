"""Exact rational semantic relations for non-evidence Stage E fixtures."""

from __future__ import annotations

import hashlib
import math
from fractions import Fraction
from typing import Any

from .canonical import Refusal, canonical_digest


def rational(value: dict[str, str]) -> Fraction:
    if not isinstance(value, dict) or set(value) != {"numerator", "denominator"}:
        raise Refusal("malformed reduced rational")
    numerator_text = value["numerator"]
    denominator_text = value["denominator"]
    if not isinstance(numerator_text, str) or not isinstance(denominator_text, str):
        raise Refusal("rational components must be decimal strings")
    if numerator_text == "-0" or numerator_text.startswith("+") or denominator_text.startswith(("+", "-")):
        raise Refusal("noncanonical rational sign")
    try:
        numerator = int(numerator_text)
        denominator = int(denominator_text)
    except ValueError as exc:
        raise Refusal("noninteger rational component") from exc
    if str(numerator) != numerator_text or str(denominator) != denominator_text or denominator <= 0:
        raise Refusal("noncanonical rational decimal encoding")
    if numerator == 0 and denominator != 1:
        raise Refusal("canonical zero must be 0/1")
    if math.gcd(abs(numerator), denominator) != 1:
        raise Refusal("rational is not in lowest terms")
    return Fraction(numerator, denominator)


def _direct_capacity(target: int) -> Fraction:
    if target not in range(2, 17):
        raise Refusal("direct nonrecursive target outside 2..16")
    first = hashlib.sha256(f"EBU-SD01-GROWTH-NONRECURSIVE-CAPACITY-v1|{target}".encode("utf-8")).digest()[0]
    return Fraction(2) + Fraction(first % 33, 16)


def _burden_valid(row: dict[str, Any]) -> bool:
    target = row["target_level_m"]
    scenario = row["scenario_id"]
    expected = {
        "construction_burden": Fraction(1, 16),
        "maintenance_burden": Fraction(target, 256),
        "resource_burden": Fraction(1, 32),
        "correction_burden": Fraction(1, 64) if target in {10, 16} else Fraction(0),
        "delay_burden": Fraction(1, 64) + (Fraction(1, 16) if scenario == "CP-RESPONSE-DELAY" else 0),
        "loss_burden": Fraction(1, 64) + (Fraction(2) if scenario == "CP-CAPACITY-SHOCK" and target == 8 else 0),
    }
    actual = {name: rational(row[name]) for name in expected}
    return actual == expected and rational(row["total_expansion_burden_X_n_plus_1"]) == sum(expected.values(), Fraction(0))


def _demographic_valid(row: dict[str, Any]) -> bool:
    current = rational(row["population_P_n"])
    target = rational(row["population_P_n_plus_1"])
    delta = target - current
    births = rational(row["births"])
    deaths = rational(row["deaths"])
    migration = rational(row["migration"])
    return births == max(delta, Fraction(0)) and deaths == max(-delta, Fraction(0)) and migration == 0 and min(births, deaths, migration) >= 0


def _allocation_valid(row: dict[str, Any]) -> bool:
    reserve = Fraction(3, 8) if row["scenario_id"] == "CP-RESERVE-ALLOCATION" else Fraction(0)
    quality = Fraction(3, 8) if row["scenario_id"] == "CP-QUALITY-ALLOCATION" else Fraction(0)
    return (
        rational(row["reserve_allocation_increment"]) == reserve
        and rational(row["quality_allocation_increment"]) == quality
        and rational(row["cumulative_reserve_allocation"]) == reserve
        and rational(row["cumulative_quality_allocation"]) == quality
        and rational(row["demographic_response_capacity"]) == rational(row["capacity_C_n_plus_1"]) - reserve - quality
        and rational(row["demographic_response_capacity"]) >= 0
    )


def _resource_valid(row: dict[str, Any]) -> bool:
    available = rational(row["demographic_response_capacity"])
    previous = rational(row["resource_state_previous"])
    demand = rational(row["demand"])
    regeneration = max(Fraction(0), (available - previous) / 4)
    resource_pre = min(available, previous + regeneration)
    served = min(demand, available, max(Fraction(0), resource_pre))
    unmet = demand - served
    post = resource_pre - served
    return (
        rational(row["regeneration"]) == regeneration
        and rational(row["boundary_exchange"]) == 0
        and rational(row["resource_pre"]) == resource_pre
        and rational(row["served"]) == served
        and rational(row["unmet"]) == unmet
        and rational(row["resource_post"]) == post
    )


def _predicate_oracle_valid(value: dict[str, Any]) -> bool:
    inputs = value["ordered_level_inputs"]
    fixture = value["fixture_id"]
    if fixture == "CP-RECOVERY-ORACLE-v1":
        target = None
        for index in range(len(inputs) - 1):
            pair = inputs[index : index + 2]
            if all(item["viability_pass"] and rational(item["service_fraction"]) >= Fraction(19, 20) and rational(item["service_reserve_margin"]) >= 1 for item in pair):
                target = pair[0]["target_level_m"]
                break
        return target == value["expected_recovery_target_level"]
    if fixture == "CP-COLLAPSE-ORACLE-v1":
        target = None
        for index in range(len(inputs) - 1):
            pair = inputs[index : index + 2]
            if all(rational(item["service_fraction"]) < Fraction(1, 2) for item in pair):
                target = pair[0]["target_level_m"]
                break
        return target == value["expected_collapse_target_level"]
    if fixture == "CP-TERMINAL-HOMEOSTASIS-ORACLE-v1":
        terminal = [item["target_level_m"] for item in inputs] == [13, 14, 15, 16] and all(
            item["viability_pass"] and rational(item["service_fraction"]) >= Fraction(19, 20) and rational(item["service_reserve_margin"]) >= 1
            for item in inputs
        )
        return terminal == value["terminal_homeostasis_member"]
    raise Refusal("unknown capacity predicate oracle fixture")


def _summary_valid(value: dict[str, Any]) -> bool:
    bindings = value["run_evidence_bindings"]
    if len(bindings) != 60 or [row["binding_ordinal"] for row in bindings] != list(range(60)):
        return False
    cumulative = [row["study_cumulative_primary_evaluations"] for row in bindings]
    if cumulative != [10_000 * (index + 1) for index in range(60)]:
        return False
    if value["study_cumulative_primary_evaluations"] != cumulative[-1] or value["recovery_event_count"] != 216:
        return False
    computations = value["computation_record_identities"]
    limits = value["limit_decision_identities"]
    if len(computations) != 60 or len(limits) != 60:
        return False
    for index, row in enumerate(bindings):
        if row["computation_record_identity"] != computations[index] or row["limit_decision_identity"] != limits[index]:
            return False
        if row["run_cumulative_primary_evaluations"] != 10_000:
            return False
    return value["visible_scientific_run_count"] == 60 and value["visible_triplet_count"] == 20 and value["stalled_run_count"] == 0


def _continuation_counter_valid(value: dict[str, Any]) -> bool:
    attempt = value["attempt_primary_evaluations"]
    run = value["run_cumulative_primary_evaluations"]
    study = value["study_cumulative_primary_evaluations"]
    projection = value["inherited_continuation_counter_projection"]
    return attempt <= run <= study and run == projection["run_cumulative_primary_evaluations"] and study == projection["campaign_cumulative_primary_evaluations"]


def semantic_valid(rule: str, value: dict[str, Any], *, base: dict[str, Any] | None = None) -> bool:
    if rule == "REFUSE_PARTIAL_ATOMIC_CASE_CONTINUATION":
        return not value["continuation_permitted"] or value["atomic_case_complete"]
    if rule == "NEW_CAMPAIGN_REQUIRED":
        return base is None or value["campaign_id"] != base["campaign_id"] or all(
            value[field] == base[field]
            for field in (
                "parallelization_boundary_identity", "worker_allocation_policy_identity", "storage_location_identity",
                "durability_policy_identity", "restart_policy_identity",
            )
        )
    if rule == "REFUSE_OUT_OF_POLICY_PROCESS_ALLOCATION":
        workers = value["ordered_worker_allocations"]
        return value["worker_count"] == len(workers) and [row["worker_ordinal"] for row in workers] == list(range(len(workers)))
    if rule == "REFUSE_POLICY_CONFORMANCE_RECEIPT_MISMATCH":
        return value["policy_conformance_receipt_identity"] == value["process_allocation"]["policy_conformance_receipt_identity"]
    if rule == "DG-SEM-CANONICAL-REDUCED-RATIONAL":
        try:
            rational(value)
        except Refusal:
            return False
        return True
    if rule == "DG-SEM-LEVEL-INDEX":
        return value["level_n"] in range(1, 16) and value["target_level_m"] == value["level_n"] + 1
    if rule == "DG-SEM-BURDEN-TARGET-INDEX":
        return _burden_valid(value)
    if rule == "DG-SEM-CANONICAL-DEMOGRAPHIC-LEDGER":
        return _demographic_valid(value)
    if rule == "DG-SEM-CP-DEMAND":
        return rational(value["demand"]) == rational(value["population_P_n_plus_1"]) / 64
    if rule == "DG-SEM-ALLOCATION-ACCUMULATOR":
        return _allocation_valid(value)
    if rule == "DG-SEM-RESOURCE-SERVICE-STATE":
        return _resource_valid(value)
    if rule == "DG-SEM-VIABILITY-PREDICATE":
        expected = _resource_valid(value) and rational(value["resource_pre"]) >= 0 and rational(value["resource_post"]) >= 0 and rational(value["unmet"]) >= 0
        return value["viability_pass"] == expected
    if rule == "DG-SEM-HOMEOSTASIS-WINDOW":
        return value["homeostasis_window_disposition"] != "PASS" or value["target_level_m"] >= 5
    if rule == "DG-SEM-EXPANSION-RHO":
        rho = rational(value["effective_rho"])
        capacity = rational(value["capacity_C_n"])
        population = rational(value["population_P_n"])
        required = population / rho + Fraction(1, 16)
        return rho > 0 and rho == population / capacity and rational(value["required_capacity"]) == required == capacity + Fraction(1, 16) and value["expansion_request_issued"] and value["expansion_request_receipt_identity"] is not None
    if rule == "DG-SEM-RECOMPUTATION-DISPOSITION":
        equal = value["all_scientific_outputs_equal"] and value["full_projection_identity"] == value["incremental_projection_identity"] == value["reuse_projection_identity"]
        reduced = value["reuse_operations"]["coefficient_evaluations"] < value["incremental_operations"]["coefficient_evaluations"] < value["full_operations"]["coefficient_evaluations"]
        return equal and (value["recomputation_disposition"] != "REUSE_STRICTLY_LOWER" or reduced and value["zero_stale_hits"] and bool(value["invalidation_receipt_identities"]))
    if rule == "DG-SEM-DIRECT-NONRECURSIVE-CAPACITY":
        target = value["target_level_m"]
        return (
            value["scenario_id"] == "CP-NONRECURSIVE"
            and value["capacity_reconstruction_branch"] == "DIRECT_HASHED_TARGET_CAPACITY"
            and value["raw_residual_J_n"] is None
            and value["capacity_compatible_residual_JC_n"] is None
            and rational(value["capacity_C_n_plus_1"]) == _direct_capacity(target)
            and rational(value["capacity_C_n"]) == (Fraction(3) if target == 2 else _direct_capacity(target - 1))
            and rational(value["capacity_C_n_minus_1"]) == (Fraction(2) if target == 2 else Fraction(3) if target == 3 else _direct_capacity(target - 2))
        )
    if rule == "DG-SEM-STALL-TERMINAL":
        return (
            value["proposed_target_level_m"] == value["source_level_n"] + 1
            and value["last_visible_level_n"] == value["source_level_n"]
            and value["later_level_row_count"] == 0
            and value["terminal_disposition"] == "STALLED_NO_LATER_ROWS"
            and value["stall_receipt_identity"] is not None
            and value["expansion_request_receipt_identity"] is None
        )
    if rule == "DG-SEM-PREDICATE-ORACLE":
        return _predicate_oracle_valid(value)
    if rule == "DG-SEM-SCENARIO-RESPONSE":
        return value["scenario_id"] == "CP-RESPONSE-DELAY" and _demographic_valid(value) and rational(value["population_P_n_plus_1"]) == rational(value["population_P_n"]) + rational(value["births"]) - rational(value["deaths"])
    if rule == "DG-SEM-RUN-EVIDENCE-COVERAGE":
        return _summary_valid(value)
    if rule == "DG-SEM-CONTINUATION-COUNTER-BINDING":
        return _continuation_counter_valid(value)
    raise Refusal(f"unknown frozen semantic relation: {rule}")


def require_semantic_pass(rule: str, value: dict[str, Any], *, base: dict[str, Any] | None = None) -> None:
    if not semantic_valid(rule, value, base=base):
        raise Refusal(rule)


def capacity_fixture_conformance(fixtures: list[dict[str, Any]]) -> dict[str, Any]:
    rational_count = 0
    for fixture in fixtures:
        instance = fixture["instance"]
        if fixture["definition"] == "reduced_rational":
            rational(instance)
            rational_count += 1
    return {
        "fixture_count": len(fixtures),
        "reduced_rational_fixture_count": rational_count,
        "fixture_registry_identity": canonical_digest(fixtures),
        "scientific_rows_populated": 0,
        "registered_campaign_runs_executed": 0,
    }
