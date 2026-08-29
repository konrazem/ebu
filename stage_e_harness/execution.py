"""Pre-import Stage F guard and pure synthetic conformance routing."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .canonical import canonical_digest


GUARD_ID = "EBU-STAGE-E-NO-SCIENCE-v2"
REGISTERED_ROUTE_IDS = ("SD-01", "SD-01-GROWTH-v1", *(f"SD-{index:02d}" for index in range(2, 15)))
REGISTERED_PREFIXES = tuple(f"{route}/" for route in REGISTERED_ROUTE_IDS)
BLOCKED_PROJECT_RUNNERS = (
    "exp_v30_gate1dc",
    "exp_v30_o14",
    "exp_v30_service",
    "exp_v30_service_attempt2",
    "exp_v30_adversary",
    "gate1dc_v30",
    "finalize_v30_gate1dc",
)


@dataclass(frozen=True)
class RefusalReceipt:
    guard_id: str
    configuration_id: str
    reason: str
    stage_f_authorization_present: bool
    project_runner_import_count: int
    model_state_advance_count: int

    def value(self) -> dict[str, Any]:
        value = {
            "guard_id": self.guard_id,
            "configuration_id": self.configuration_id,
            "reason": self.reason,
            "stage_f_authorization_present": self.stage_f_authorization_present,
            "project_runner_import_count": self.project_runner_import_count,
            "model_state_advance_count": self.model_state_advance_count,
        }
        value["receipt_sha256"] = canonical_digest(value)
        return value


class StageEExecutionRefusal(RuntimeError):
    def __init__(self, receipt: RefusalReceipt) -> None:
        super().__init__(receipt.reason)
        self.receipt = receipt.value()


def guard_registered_configuration(configuration_id: str, stage_f_authorization: dict[str, Any] | None = None) -> None:
    registered = configuration_id in REGISTERED_ROUTE_IDS or any(configuration_id.startswith(prefix) for prefix in REGISTERED_PREFIXES)
    if not registered:
        return
    # The Stage E build does not contain a recognized campaign authorization
    # verifier.  Refusal therefore occurs before any import or adapter dispatch.
    reason = "registered Stage F configuration refused before project runner import"
    receipt = RefusalReceipt(GUARD_ID, configuration_id, reason, stage_f_authorization is not None, 0, 0)
    raise StageEExecutionRefusal(receipt)


def assert_runner_name_blocked(module_name: str) -> None:
    if module_name in BLOCKED_PROJECT_RUNNERS:
        receipt = RefusalReceipt(GUARD_ID, f"runner:{module_name}", "project runner blocked in Stage E", False, 0, 0)
        raise StageEExecutionRefusal(receipt)


def synthetic_configuration_id(study_id: str, fixture: str) -> str:
    if not study_id.startswith("SD-") or not fixture:
        raise ValueError("invalid synthetic configuration label")
    return f"SYNTHETIC-STAGE-E/{study_id}/{fixture}"
