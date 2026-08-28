"""Exact 14-study registry derived from the embedded accepted Stage D matrix."""

from __future__ import annotations

import importlib
import importlib.resources
from typing import Any

from .canonical import Refusal, strict_loads


STUDY_IDS = tuple(f"SD-{index:02d}" for index in range(1, 15))
WITHIN_RUN = ("SD-01", "SD-08", "SD-09", "SD-10", "SD-11", "SD-12", "SD-13", "SD-14")
CONDITIONAL_INHERITED = ("SD-02",)
BETWEEN_ATOMIC_CASE = ("SD-03", "SD-04", "SD-05", "SD-06", "SD-07")


def load_embedded_json(name: str) -> dict[str, Any]:
    resource = importlib.resources.files("stage_e_harness").joinpath("authority", name)
    try:
        data = resource.read_bytes()
    except (FileNotFoundError, ModuleNotFoundError) as exc:
        raise Refusal(f"embedded authority input missing: {name}") from exc
    value = strict_loads(data)
    if not isinstance(value, dict):
        raise Refusal(f"embedded authority input is not an object: {name}")
    return value


def continuation_class(study_id: str) -> str:
    if study_id in WITHIN_RUN:
        return "within_run_checkpoint_continuation"
    if study_id in CONDITIONAL_INHERITED:
        return "conditional_inherited_continuation"
    if study_id in BETWEEN_ATOMIC_CASE:
        return "between_atomic_case_continuation_only"
    raise Refusal(f"unknown study: {study_id}")


def load_bindings(matrix: dict[str, Any] | None = None) -> tuple[Any, ...]:
    from .adapters.base import AdapterBinding

    if matrix is None:
        matrix = load_embedded_json("stage_d_scientific_validation_master_matrix.json")
    studies = matrix.get("studies")
    if not isinstance(studies, list) or tuple(row.get("study_id") for row in studies) != STUDY_IDS:
        raise Refusal("Stage D study order or closure mismatch")
    bindings: list[AdapterBinding] = []
    for index, study_id in enumerate(STUDY_IDS, 1):
        module = importlib.import_module(f"stage_e_harness.adapters.sd{index:02d}")
        if getattr(module, "STUDY_ID", None) != study_id:
            raise Refusal("adapter module/study bijection mismatch")
        binding = module.bind(studies[index - 1])
        if binding.study_id != study_id or binding.order != index:
            raise Refusal("adapter binding order mismatch")
        bindings.append(binding)
    return tuple(bindings)


def validate_partition() -> None:
    sets = [set(WITHIN_RUN), set(CONDITIONAL_INHERITED), set(BETWEEN_ATOMIC_CASE)]
    if any(left & right for index, left in enumerate(sets) for right in sets[index + 1 :]):
        raise Refusal("continuation partition overlaps")
    if set.union(*sets) != set(STUDY_IDS) or tuple(STUDY_IDS)[0] != "SD-01":
        raise Refusal("continuation partition is not a complete 14-study closure")
