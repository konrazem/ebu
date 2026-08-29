"""Exact non-scientific recursive Möbius, poset, and transport oracles."""

from __future__ import annotations

from fractions import Fraction
from typing import Any, Callable

from .canonical import Refusal, canonical_bytes, sha256_bytes


def _q(value: Fraction | int) -> dict[str, str]:
    fraction = Fraction(value)
    return {"numerator": str(fraction.numerator), "denominator": str(fraction.denominator)}


def _identity(data: bytes) -> dict[str, Any]:
    return {"byte_count": len(data), "sha256": sha256_bytes(data)}


def _case(ordinal: int, case_id: str, inputs: Any, outputs: Any, relation: Any, disposition: str = "PASS") -> dict[str, Any]:
    input_bytes = canonical_bytes(inputs)
    output_bytes = canonical_bytes(outputs)
    relation_bytes = canonical_bytes(relation)
    return {
        "ordinal": ordinal,
        "case_id": case_id,
        "canonical_input": input_bytes.decode("utf-8"),
        "input_identity": _identity(input_bytes),
        "canonical_output": output_bytes.decode("utf-8"),
        "output_identity": _identity(output_bytes),
        "canonical_relation": relation_bytes.decode("utf-8"),
        "relation_identity": _identity(relation_bytes),
        "disposition": disposition,
    }


def _fib(n: int) -> int:
    if n < 0:
        raise Refusal("negative Fibonacci index")
    left, right = 0, 1
    for _ in range(n):
        left, right = right, left + right
    return left


def _j(family: str, level: int) -> int:
    functions: dict[str, Callable[[int], int]] = {
        "ZERO": lambda _: 0,
        "POSITIVE": lambda n: n,
        "NEGATIVE": lambda n: -n,
        "ALTERNATING": lambda n: n if n % 2 else -n,
        "PULSED": lambda n: 3 if n in {3, 8, 13} else 0,
        "SIGNED_QUADRATIC": lambda n: (-1 if n % 3 == 0 else 1) * n * n,
    }
    try:
        return functions[family](level)
    except KeyError as exc:
        raise Refusal(f"unknown recursive fixture family: {family}") from exc


def recursive_macro_cases() -> list[dict[str, Any]]:
    families = ("ZERO", "POSITIVE", "NEGATIVE", "ALTERNATING", "PULSED", "SIGNED_QUADRATIC")
    baselines = (0, 5, -3)
    cases: list[dict[str, Any]] = []
    ordinal = 0
    for family in families:
        for baseline in baselines:
            r = [baseline, baseline + 1]
            for level in range(1, 16):
                r.append(r[level] + r[level - 1] + _j(family, level))
            for level in range(1, 16):
                empty = baseline
                ex = r[level] + empty
                ey = r[level - 1] + empty
                exy = r[level + 1] + empty
                interaction = exy - ex - ey + empty
                projection = _fib(level + 1) * r[1] + _fib(level) * r[0]
                projection += sum(_fib(level + 1 - k) * _j(family, k) for k in range(1, level + 1))
                homogeneous = _fib(level + 1) * r[1] + _fib(level) * r[0]
                error = r[level + 1] - homogeneous
                expected_error = sum(_fib(level + 1 - k) * _j(family, k) for k in range(1, level + 1))
                if interaction != _j(family, level) or exy - empty != r[level] + r[level - 1] + interaction:
                    raise Refusal("recursive Möbius macro identity mismatch")
                if projection != r[level + 1] or error != expected_error:
                    raise Refusal("forced Fibonacci projection mismatch")
                inputs = {
                    "family": family,
                    "baseline": baseline,
                    "level": level,
                    "e_empty": empty,
                    "e_x": ex,
                    "e_y": ey,
                    "e_xy": exy,
                }
                outputs = {
                    "direct_interaction": interaction,
                    "declared_J": _j(family, level),
                    "inverse_surplus": exy - empty,
                    "forced_projection": projection,
                    "missing_interaction_error": error,
                    "correction_multiplier_for_J1": _fib(level),
                }
                relation = {
                    "identity": "I({x,y})=J and R(n+1)=R(n)+R(n-1)+J(n)",
                    "forced_projection": "R(n)=F(n)R(1)+F(n-1)R(0)+sum(F(n-k)J(k))",
                    "universal_population_or_wave_claim": False,
                }
                cases.append(_case(ordinal, f"RECURSIVE-{family}-{baseline}-{level:02d}", inputs, outputs, relation))
                ordinal += 1
    if len(cases) != 270:
        raise AssertionError("recursive macro case count defect")
    return cases


def _poset_closures() -> tuple[tuple[tuple[int, ...], ...], ...]:
    return (
        ((0,), (0, 1), (0, 1, 2), (0, 1, 2, 3)),
        ((0,), (1,), (0, 1, 2), (0, 1, 2, 3)),
        ((0,), (0, 1), (0, 2), (0, 1, 2, 3)),
        ((0,), (1,), (2,), (0, 1, 2, 3)),
    )


def _poset_transform(values: list[int], lower_sets: tuple[tuple[int, ...], ...]) -> list[int]:
    coefficients: list[int] = []
    for x, lower in enumerate(lower_sets):
        coefficients.append(values[x] - sum(coefficients[y] for y in lower if y != x))
    rebuilt = [sum(coefficients[y] for y in lower) for lower in lower_sets]
    if rebuilt != values:
        raise Refusal("feasible-poset inversion mismatch")
    return coefficients


def poset_cases() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    base_cases: list[dict[str, Any]] = []
    correction_cases: list[dict[str, Any]] = []
    for poset_index, lower_sets in enumerate(_poset_closures()):
        for seed in range(8):
            values = [((seed + 3) * (x + 2) + poset_index * 5) % 19 - 9 for x in range(4)]
            coefficients = _poset_transform(values, lower_sets)
            base_cases.append(
                _case(
                    len(base_cases),
                    f"POSET-{poset_index}-{seed}",
                    {"lower_sets": [list(lower) for lower in lower_sets], "values": values},
                    {"coefficients": coefficients, "reconstruction": values},
                    {"relation": "I(x)=E(x)-sum(y<x)I(y); E(x)=sum(y<=x)I(y)", "boolean_infeasible_values_invented": False},
                )
            )
            for correction_index in range(7):
                q = correction_index % 4
                delta = correction_index - 3 or 1
                changed = list(values)
                changed[q] += delta
                changed_coefficients = _poset_transform(changed, lower_sets)
                delta_coefficients = [right - left for left, right in zip(coefficients, changed_coefficients)]
                correction_cases.append(
                    _case(
                        len(correction_cases),
                        f"POSET-CORRECTION-{poset_index}-{seed}-{correction_index}",
                        {"q": q, "delta_E": delta, "before": values, "after": changed, "lower_sets": [list(lower) for lower in lower_sets]},
                        {"delta_I": delta_coefficients},
                        {"relation": "delta I(x)=sum(q<=x)mu(q,x)delta E(q)", "feasible_elements_only": True},
                    )
                )
    if (len(base_cases), len(correction_cases)) != (32, 224):
        raise AssertionError("poset conformance count defect")
    return base_cases, correction_cases


def transport_cases() -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    families = (
        ("INVARIANT-INTENSIVE", Fraction(1)),
        ("OCCURRENCE-EXTENSIVE", Fraction(3, 2)),
        ("BOUNDARY-EXTENSIVE", Fraction(4, 3)),
        ("DEGREE-HOMOGENEOUS", Fraction(9, 4)),
        ("SCALE-DEPENDENT-RESIDUAL", Fraction(5, 3)),
        ("DECLARED-PROVIDER-SCALAR", Fraction(7, 5)),
    )
    scalar: list[dict[str, Any]] = []
    direct: list[dict[str, Any]] = []
    corrections: list[dict[str, Any]] = []
    refusals: list[dict[str, Any]] = []
    for family, factor in families:
        for level in range(1, 16):
            source = Fraction(level * 7 - 5, 3)
            residual = Fraction((level % 5) - 2, 7)
            target = factor * source + residual
            scalar.append(
                _case(
                    len(scalar), f"TRANSPORT-{family}-{level:02d}",
                    {"level": level, "coordinate_map": f"iota-{level}", "source": _q(source), "factor": _q(factor), "residual": _q(residual)},
                    {"direct_target": _q(target)},
                    {"relation": "I_target(iota S)=lambda I_source(S)+K_target(iota S)", "units_query_boundary_equal": True},
                )
            )
            for delta_index, delta_source in enumerate((Fraction(1, 11), Fraction(-2, 13))):
                delta_residual = Fraction(delta_index + 1, 17)
                delta_target = factor * delta_source + delta_residual
                corrections.append(
                    _case(
                        len(corrections), f"TRANSPORT-CORRECTION-{family}-{level:02d}-{delta_index}",
                        {"factor": _q(factor), "delta_source": _q(delta_source), "delta_residual": _q(delta_residual)},
                        {"delta_target": _q(delta_target)},
                        {"relation": "delta I_target=lambda delta I_source+delta K"},
                    )
                )
    for level in range(1, 16):
        direct_value = Fraction(level * level + 1, level + 2)
        direct.append(
            _case(
                len(direct), f"TRANSPORT-NONSCALABLE-{level:02d}",
                {"level": level, "scaling_class": "NON-SCALABLE-DIRECT", "factor": None},
                {"direct_target": _q(direct_value)},
                {"scaled_reuse": "FORBIDDEN", "direct_recomputation": True},
            )
        )
        for refusal_index in range(10):
            refusals.append(
                _case(
                    len(refusals), f"TRANSPORT-REFUSAL-{level:02d}-{refusal_index}",
                    {"level": level, "missing_or_changed_dimension": refusal_index},
                    {"scaled_reuse": "REFUSED_BEFORE_TRAJECTORY"},
                    {"required_map_factor_units_query_boundary_authority_residual": True},
                    "REFUSED",
                )
            )
    if (len(scalar), len(direct), len(corrections), len(refusals)) != (90, 15, 180, 150):
        raise AssertionError("transport conformance count defect")
    return scalar, direct, corrections, refusals


def recursive_conformance() -> dict[str, Any]:
    macro = recursive_macro_cases()
    poset_base, poset_corrections = poset_cases()
    scalar, direct, transport_corrections, refusals = transport_cases()
    return {
        "macro_cases": macro,
        "poset_base_cases": poset_base,
        "poset_correction_cases": poset_corrections,
        "transport_scalar_cases": scalar,
        "transport_direct_cases": direct,
        "transport_correction_cases": transport_corrections,
        "transport_refusal_cases": refusals,
        "mismatch_count": 0,
    }
