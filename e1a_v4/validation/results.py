"""Frozen output schema and manifest. Written before execution, by design."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any

RESULT_SCHEMA = "e1a_v4_validation_result/2"
MANIFEST_SCHEMA = "e1a_v4_validation_manifest/3"
#: Record schema 2 adds `subcondition_id`. A record is reproducible from
#: (case_id, subcondition_id, replicate_id, field/scope, seed family, seed identity).
#: Manifest schema 3 adds `contract_diagnostics`: an aggregate that omits a
#: MANDATORY CONTRACT DIAGNOSTIC is RESULT_SCHEMA_INVALID, so the reporting layer
#: cannot drop a requirement frozen authority makes mandatory. No official result
#: data exists, so both breaks are free to make explicit now.

#: Every field a scientific result record must carry. Frozen before execution.
RESULT_FIELDS = (
    "case_id", "subcondition_id", "replicate_id", "seed_family", "seed_identity", "field_id",
    "truth_parameters", "branch_a_observed", "analysis_status",
    "G1", "G2", "G3", "G4", "G5", "P1", "beta_hat", "P2", "P3", "P4",
    "complete_pass", "refusal_reason", "procedure_identity", "contract_sha256",
    "plan_sha256", "implementation_commit",
)

FAILURE_CLASSIFICATIONS = (
    "SOFTWARE_OR_INVARIANT_FAILURE",
    "CALIBRATION_FAILURE",
    "STATISTICAL_SIZE_FAILURE",
    "TRUE_BRIDGE_POWER_FAILURE",
    "FALSE_BRIDGE_DISCRIMINATION_FAILURE",
    "STRUCTURED_REFUSAL_EXCESS",
    "MODE_RESOLUTION_FAILURE",
    "BLINDED_SCALE_CONTROL_FAILURE",
    "NUMERICAL_OR_PRECISION_FAILURE",
    "VALIDATION_INCONCLUSIVE",
    "VALIDATION_PASS",
)


@dataclass
class ResultRecord:
    case_id: str
    subcondition_id: str
    replicate_id: int
    seed_family: str
    seed_identity: int
    field_id: str
    truth_parameters: dict[str, Any]
    branch_a_observed: dict[str, Any]
    analysis_status: str
    procedure_identity: str
    contract_sha256: str
    plan_sha256: str
    implementation_commit: str
    G1: float | None = None
    G2: float | None = None
    G3: list[float] | None = None
    G4: float | None = None
    G5: float | None = None
    P1: bool | None = None
    beta_hat: float | None = None
    P2: bool | None = None
    P3: bool | None = None
    P4: bool | None = None
    complete_pass: bool | None = None
    refusal_reason: str | None = None

    def to_json(self) -> dict[str, Any]:
        d = asdict(self)
        d["schema"] = RESULT_SCHEMA
        missing = [f for f in RESULT_FIELDS if f not in d]
        if missing:
            raise ValueError(f"result record missing frozen fields {missing}")
        return d


def aggregate_skeleton(case_id: str, subcondition_id: str | None = None) -> dict[str, Any]:
    """The frozen shape of an aggregate report. Counts filled at execution."""
    return {
        "schema": MANIFEST_SCHEMA,
        "case_id": case_id,
        "subcondition_id": subcondition_id,
        "declared_replicates": None,
        "completed": None,
        "success_count": None,
        "failure_count": None,
        "refusal_count": None,
        "refusals_by_reason": {},
        "denominator_rule": "every declared validation replicate; refusals count as failures",
        "confidence_bound": {"method": None, "level": 0.95, "side": None, "value": None},
        "false_bridge_acceptance": None,
        "per_field_geometry_rates": {},
        "mode_resolution_behaviour": {},
        "g5_diagnostics": {},
        "scale_control_recovery": {},
        # MANDATORY CONTRACT DIAGNOSTICS. Frozen authority requires these to be
        # REPORTED even where a stricter adopted rule is the actual release gate.
        # `require_mandatory_diagnostics` refuses an aggregate that leaves one out.
        "contract_diagnostics": {},
        "classification": None,
        "conditional_diagnostic_secondary": {
            "label": "SECONDARY, conditional on estimable runs only",
            "value": None,
        },
    }
