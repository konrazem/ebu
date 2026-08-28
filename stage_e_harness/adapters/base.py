"""Closed adapter binding from one accepted Stage D matrix row."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..canonical import Refusal, canonical_digest
from ..execution import guard_registered_configuration
from ..registry import continuation_class


@dataclass(frozen=True)
class AdapterBinding:
    study_id: str
    order: int
    title: str
    status: str
    dependencies: tuple[str, ...]
    question: str
    equations: tuple[str, ...]
    authority_sources: tuple[str, ...]
    implementation_interfaces: tuple[str, ...]
    schemas: tuple[str, ...]
    exact_or_approximate_label: str
    continuation_class: str
    row_identity: str

    def refuse_registered_route(self, configuration_id: str) -> None:
        guard_registered_configuration(configuration_id)


def from_matrix(expected_study_id: str, row: dict[str, Any]) -> AdapterBinding:
    required = {
        "study_id", "order", "title", "status", "dependencies", "question", "prospective_claim",
        "evidence", "owners", "model_domain", "configuration", "computational_feasibility", "falsifiers",
        "conservation_accounting", "schemas", "acceptance", "inconclusive", "independent_result_audit",
        "book_destination", "prohibited_interpretations", "mandatory_computational_control_refs",
    }
    if set(row) != required or row.get("study_id") != expected_study_id:
        raise Refusal(f"adapter authority gap for {expected_study_id}")
    owners = row["owners"]
    return AdapterBinding(
        study_id=expected_study_id,
        order=row["order"],
        title=row["title"],
        status=row["status"],
        dependencies=tuple(row["dependencies"]),
        question=row["question"],
        equations=tuple(owners["equations"]),
        authority_sources=tuple(owners["authority_sources"]),
        implementation_interfaces=tuple(owners["implementation_interfaces"]),
        schemas=tuple(row["schemas"]),
        exact_or_approximate_label=row["computational_feasibility"]["exact_or_approximate_label"],
        continuation_class=continuation_class(expected_study_id),
        row_identity=canonical_digest(row),
    )
