"""The ONE versioned validation-event evaluator.

V3's control runner decided "support" from four raw statistics -- the absolute
interval, the geometry, centre and current statistics -- compared directly
against their tolerances.  That predicate skipped the cross-field contrasts,
stationarity, the diagnostic family, the realized-field statuses and packet
validity, it compared raw statistics where calibrated upper limits are
required, and it never called the verdict engine.  It could therefore count a
"support" the authoritative pipeline would have refused.

Here every case declares its expected event as a typed
:class:`~e1a_v5.validation.cases.ExpectedEvent`, and exactly one function maps
(declared event, replicate outcome) to a boolean.  Nothing else in the
validation layer is permitted to decide whether a replicate counted.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from ..pipeline import CompleteResult
from ..verdict import DISCREPANCY, INVALID, NOT_EVALUABLE, SUPPORTED
from .cases import ExpectedEvent, ValidationCaseV4

#: Identity of this evaluator.  It enters the V4 validation identity, so a
#: change to how any event is counted moves that identity.
EVENT_EVALUATOR_VERSION = "e1a-v5-event-evaluator-v4"


class EventNotEvaluable(Exception):
    """The replicate produced nothing the declared event can be read from."""


@dataclass(frozen=True)
class ReplicateOutcome:
    """Everything one stochastic replicate retains.

    The per-replicate structured reasons live here and are never discarded by
    aggregation: V3 returned ``nonevaluable = 11`` and nothing else, so an
    audit could not tell a bandwidth refusal from an optimiser failure without
    re-running the campaign.
    """

    case_id: str
    replicate: int
    seed: int
    #: The authoritative verdict classification, when a complete experiment ran.
    classification: str | None = None
    #: Full structured refusal codes, in order of occurrence.
    reason_codes: tuple[str, ...] = ()
    #: ``CODE:predicate`` pairs, so two refusals with one code stay distinct.
    reason_predicates: tuple[str, ...] = ()
    #: Which record or contrast each refusal is attached to, where applicable.
    affected: tuple[str, ...] = ()
    optimizer_status: str | None = None
    diagnostic_status: str | None = None
    realization_status: str | None = None
    bandwidth_product: float | None = None
    bandwidth_ok: bool | None = None
    #: Single-record drivers: whether the absolute interval was contained.
    absolute_contained: bool | None = None
    #: Blinded-recovery controls: recovered log beta minus its true value.
    blinded_error: float | None = None
    #: What the dispatcher actually instantiated, for the configuration check.
    configuration: Mapping[str, Any] = field(default_factory=dict)
    evaluable: bool = True

    @staticmethod
    def from_complete(
        case_id: str, replicate: int, seed: int, result: CompleteResult, **extra
    ) -> "ReplicateOutcome":
        affected: list[str] = []
        for r in result.reasons:
            tag = r.detail.get("record") or r.detail.get("contrast") or r.detail.get("identity")
            affected.append(str(tag) if tag is not None else "")
        return ReplicateOutcome(
            case_id=case_id,
            replicate=replicate,
            seed=seed,
            classification=result.verdict.classification,
            reason_codes=tuple(result.reason_codes()),
            reason_predicates=tuple(result.reason_predicates()),
            affected=tuple(affected),
            diagnostic_status=(
                None if result.diagnostic is None else result.diagnostic.status
            ),
            **extra,
        )

    def as_dict(self) -> dict:
        return {
            "case_id": self.case_id,
            "replicate": self.replicate,
            "seed": self.seed,
            "classification": self.classification,
            "reason_codes": list(self.reason_codes),
            "reason_predicates": list(self.reason_predicates),
            "affected": list(self.affected),
            "optimizer_status": self.optimizer_status,
            "diagnostic_status": self.diagnostic_status,
            "realization_status": self.realization_status,
            "bandwidth_product": self.bandwidth_product,
            "bandwidth_ok": self.bandwidth_ok,
            "absolute_contained": self.absolute_contained,
            "blinded_error": self.blinded_error,
            "evaluable": self.evaluable,
            "configuration": dict(self.configuration),
        }


#: Tolerance on a blinded-recovery control: the recovered scale must return
#: to truth well inside the T.7 margin once the hidden factor is removed.
BLINDED_RECOVERY_TOLERANCE = 0.01


def evaluate_event(case: ValidationCaseV4, outcome: ReplicateOutcome) -> bool:
    """Did this replicate realise the case's declared event?

    Every branch that could stand in for a verdict reads
    ``outcome.classification``, which comes from
    ``CompleteResult.counts_as_complete_success``'s own verdict and nowhere
    else.  No raw statistic appears anywhere in this function.
    """
    ev = case.expected_event
    if ev is ExpectedEvent.COMPLETE_SUPPORT:
        if outcome.classification is None:
            return False
        return outcome.classification == SUPPORTED
    if ev is ExpectedEvent.DISCREPANCY:
        return outcome.classification == DISCREPANCY
    if ev is ExpectedEvent.INVALID:
        return outcome.classification == INVALID
    if ev is ExpectedEvent.NOT_EVALUABLE:
        return outcome.classification == NOT_EVALUABLE
    if ev is ExpectedEvent.FALSE_EQUIVALENCE:
        if outcome.absolute_contained is None:
            return False
        return bool(outcome.absolute_contained)
    if ev is ExpectedEvent.DIAGNOSTIC_REJECTION:
        if outcome.diagnostic_status is None:
            return False
        return outcome.diagnostic_status == "REJECTED"
    if ev is ExpectedEvent.REFUSAL_CODE:
        if case.event_target is None:
            raise EventNotEvaluable(f"{case.case_id} declares no target refusal code")
        return case.event_target in outcome.reason_codes
    if ev is ExpectedEvent.REALIZATION_STATUS:
        if case.event_target is None:
            raise EventNotEvaluable(f"{case.case_id} declares no target status")
        return outcome.realization_status == case.event_target
    if ev is ExpectedEvent.BLINDED_RECOVERY:
        if outcome.blinded_error is None:
            return False
        return abs(outcome.blinded_error) <= BLINDED_RECOVERY_TOLERANCE
    if ev is ExpectedEvent.CALIBRATION_OUTPUT:
        raise EventNotEvaluable(
            f"{case.case_id} is a calibration case; it has no pass/fail event"
        )
    if ev is ExpectedEvent.DETERMINISTIC:
        raise EventNotEvaluable(
            f"{case.case_id} is exercised by the deterministic battery, not by sampling"
        )
    raise EventNotEvaluable(f"no evaluator for expected event {ev!r}")


# ---------------------------------------------------------------------------
# Aggregation that keeps the detail
# ---------------------------------------------------------------------------

@dataclass
class ReasonAggregate:
    """Counts plus the full per-replicate record.

    The summary is a convenience; ``replicates`` is the evidence.  Dropping it
    was defect 7.
    """

    case_id: str
    replicates: list[ReplicateOutcome] = field(default_factory=list)

    def add(self, outcome: ReplicateOutcome) -> None:
        self.replicates.append(outcome)

    def classification_counts(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for r in self.replicates:
            key = r.classification or "NO_CLASSIFICATION"
            out[key] = out.get(key, 0) + 1
        return out

    def reason_code_histogram(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for r in self.replicates:
            for code in set(r.reason_codes):
                out[code] = out.get(code, 0) + 1
        return out

    def reason_predicate_histogram(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for r in self.replicates:
            for p in set(r.reason_predicates):
                out[p] = out.get(p, 0) + 1
        return out

    def joint_reason_histogram(self) -> dict[str, int]:
        """Counts of the exact SET of reason codes seen together."""
        out: dict[str, int] = {}
        for r in self.replicates:
            key = "+".join(sorted(set(r.reason_codes))) or "(none)"
            out[key] = out.get(key, 0) + 1
        return out

    def affected_histogram(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for r in self.replicates:
            for a in set(r.affected):
                if a:
                    out[a] = out.get(a, 0) + 1
        return out

    def as_dict(self) -> dict:
        return {
            "case_id": self.case_id,
            "evaluator_version": EVENT_EVALUATOR_VERSION,
            "replicates_run": len(self.replicates),
            "classifications": self.classification_counts(),
            "reason_codes": self.reason_code_histogram(),
            "reason_predicates": self.reason_predicate_histogram(),
            "joint_reason_combinations": self.joint_reason_histogram(),
            "affected": self.affected_histogram(),
            "per_replicate": [r.as_dict() for r in self.replicates],
        }
