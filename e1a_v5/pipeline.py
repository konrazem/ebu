"""The single authoritative complete-experiment path.

V2 let the power runner reconstruct its own, weaker, success predicate.  V3
centralised the conjunction here but still judged whatever evidence it was
handed: the independent audit showed that duplicate records, a ninth record,
reversed interval endpoints and a record/family diagnostic contradiction all
still reached ``SUPPORTED_WITHIN_DECLARED_TOLERANCES``.

V4 splits the judgement in two, in this order:

1. :mod:`e1a_v5.evidence` establishes that the evidence *is* the preregistered
   experiment -- exactly the eight canonical records, exactly the six
   within-block contrasts, every interval well formed, every critical value
   and bias bound present and calibrated;
2. only then is the T-stage conjunction evaluated.

``counts_as_complete_success`` remains the ONLY success predicate.  Runners
must call it; they must never rebuild it.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Mapping, Sequence

from .confidence import DELTA_A, DELTA_C, CriticalValueStatus
from .diagnostics import (
    DIAG_CALIBRATED,
    DIAG_CONTRADICTORY,
    DIAG_NOT_EVALUABLE,
    DIAG_UNCALIBRATED,
    DiagnosticFamilyResult,
)
from .evidence import (
    BiasEvidence,
    ContrastKey,
    GateLimit,
    RecordKey,
    ScientificInterval,
    cardinality_refusals,
    check_contrast_cardinality,
    check_record_cardinality,
)
from .gates import DELTA_G, DELTA_M, DELTA_R_IRR
from .packets import CONTRASTS, RECORDS, BlockId, FieldId
from .realization import FIELD_REALIZATION_VALID
from .refusals import (
    CALIBRATION_UNCERTAINTY_EXCESS,
    COMPUTATION_NOT_EVALUABLE,
    INCOMPLETE_INPUT,
    INVALID_RECORD_MONITOR,
    Refusal,
    refuse,
)
from .verdict import ComponentTally, SUPPORTED, Verdict, decide

#: Stationarity tolerance: the combined statistic is scaled to 1.0 (T 12.1).
DELTA_STATIONARITY = 1.0


def record_key(block: BlockId, fld: FieldId) -> str:
    return f"{block.value}/{fld.value}"


def contrast_key(block: BlockId, fld: FieldId) -> str:
    return str(ContrastKey(block, fld))


@dataclass(frozen=True)
class RecordResultV4:
    """One record's complete, explicitly typed result.

    Every inferential field is absent-by-default.  There is no sentinel that
    reads as a pass, and ``embedded_key`` lets a record filed under the wrong
    identity be detected rather than silently accepted.
    """

    key: RecordKey
    embedded_key: RecordKey | None = None
    branch_a_valid: bool | None = None
    observation_valid: bool | None = None
    realization_status: str | None = None
    log_beta: float | None = None
    log_beta_se: float | None = None
    absolute: ScientificInterval | None = None
    absolute_bias: BiasEvidence = field(default_factory=BiasEvidence.missing)
    shape: GateLimit = field(default_factory=GateLimit.uncalibrated)
    centre: GateLimit = field(default_factory=GateLimit.uncalibrated)
    stationarity: GateLimit = field(default_factory=GateLimit.uncalibrated)
    current: GateLimit = field(default_factory=GateLimit.uncalibrated)
    evaluable: bool = True
    reasons: tuple[Refusal, ...] = ()

    @property
    def identity(self) -> str:
        return str(self.key)


@dataclass(frozen=True)
class ContrastResultV4:
    """One within-block contrast's result."""

    key: ContrastKey
    interval: ScientificInterval | None = None
    bias: BiasEvidence = field(default_factory=BiasEvidence.missing)
    reasons: tuple[Refusal, ...] = ()

    @property
    def identity(self) -> str:
        return str(self.key)


@dataclass(frozen=True)
class CompleteResult:
    """The outcome of one complete eight-record experiment."""

    verdict: Verdict
    tally: ComponentTally
    records: tuple[RecordResultV4, ...]
    contrasts: tuple[ContrastResultV4, ...]
    diagnostic: DiagnosticFamilyResult | None
    reasons: tuple[Refusal, ...]
    evidence_ok: bool

    @property
    def counts_as_complete_success(self) -> bool:
        """The ONLY success predicate. Runners must call this, not rebuild it."""
        return self.verdict.classification == SUPPORTED

    @property
    def classification(self) -> str:
        return self.verdict.classification

    def reason_codes(self) -> list[str]:
        return [r.code for r in self.reasons]

    def reason_predicates(self) -> list[str]:
        return [f"{r.code}:{r.predicate}" for r in self.reasons]

    def as_dict(self) -> dict:
        return {
            "classification": self.verdict.classification,
            "qualifier": self.verdict.qualifier,
            "success": self.counts_as_complete_success,
            "evidence_ok": self.evidence_ok,
            "diagnostic": None if self.diagnostic is None else self.diagnostic.as_dict(),
            "reasons": [r.as_dict() for r in self.reasons],
            "tally": {
                "absolute_pass": self.tally.absolute_pass,
                "contrast_pass": self.tally.contrast_pass,
                "shape_pass": self.tally.shape_pass,
                "centre_pass": self.tally.centre_pass,
                "stationarity_pass": self.tally.stationarity_pass,
                "current_pass": self.tally.current_pass,
                "realization_valid": self.tally.realization_valid,
                "branch_a_valid": self.tally.branch_a_valid,
                "observation_valid": self.tally.observation_valid,
                "diagnostic_rejected": self.tally.diagnostic_rejected,
            },
        }


# ---------------------------------------------------------------------------
# Stage 1: evidence validation
# ---------------------------------------------------------------------------

def validate_evidence(
    records: Sequence[RecordResultV4],
    contrasts: Sequence[ContrastResultV4],
    diagnostic: DiagnosticFamilyResult | None,
) -> list[Refusal]:
    """Structural preconditions, evaluated BEFORE any conjunction.

    Returns every reason the supplied evidence does not describe the
    preregistered experiment.  A non-empty result means no verdict beyond a
    fail-closed classification is available, whatever the numbers say.
    """
    reasons: list[Refusal] = []

    reasons.extend(cardinality_refusals(
        check_record_cardinality(
            [r.key for r in records],
            [r.embedded_key if r.embedded_key is not None else r.key for r in records],
        ),
        "record",
    ))
    reasons.extend(cardinality_refusals(
        check_contrast_cardinality([c.key for c in contrasts]), "contrast",
    ))

    for rec in records:
        if not rec.evaluable:
            continue
        if rec.absolute is None:
            reasons.append(refuse(
                INCOMPLETE_INPUT, "absolute interval established",
                "no absolute equivalence interval was produced",
                record=rec.identity,
            ))
        else:
            for code in rec.absolute.validate():
                reasons.append(_interval_refusal(code, record=rec.identity))
        if not rec.absolute_bias.usable:
            reasons.append(refuse(
                INCOMPLETE_INPUT, "bounded-bias evidence present",
                f"absolute bounded bias is {rec.absolute_bias.status.value}; "
                "missing bias evidence is not a bound of zero",
                record=rec.identity,
            ))

    for con in contrasts:
        if con.interval is None:
            reasons.append(refuse(
                INCOMPLETE_INPUT, "contrast interval established",
                "no within-block contrast interval was produced",
                contrast=con.identity,
            ))
        else:
            for code in con.interval.validate():
                reasons.append(_interval_refusal(code, contrast=con.identity))
        if not con.bias.usable:
            reasons.append(refuse(
                INCOMPLETE_INPUT, "contrast bounded-bias evidence present",
                f"contrast bounded bias is {con.bias.status.value}; it may not "
                "be inferred from two absolute bounds",
                contrast=con.identity,
            ))

    if diagnostic is None:
        reasons.append(refuse(
            COMPUTATION_NOT_EVALUABLE, "diagnostic family evaluated",
            "no diagnostic-family result was supplied; a diagnostic that was "
            "not computed is not a diagnostic that passed",
        ))
    elif diagnostic.status != DIAG_CALIBRATED:
        code = {
            DIAG_NOT_EVALUABLE: COMPUTATION_NOT_EVALUABLE,
            DIAG_UNCALIBRATED: INCOMPLETE_INPUT,
            DIAG_CONTRADICTORY: INVALID_RECORD_MONITOR,
        }.get(diagnostic.status, COMPUTATION_NOT_EVALUABLE)
        reasons.append(refuse(
            code, "diagnostic family calibrated and coherent",
            f"diagnostic family status {diagnostic.status}: "
            + "; ".join(diagnostic.reason_codes[:4]),
            status=diagnostic.status,
        ))
    return reasons


_INTERVAL_CODE_FAMILY = {
    "interval_absent": INCOMPLETE_INPUT,
    "interval_endpoint_nonfinite": COMPUTATION_NOT_EVALUABLE,
    "interval_endpoints_reversed": INVALID_RECORD_MONITOR,
    "estimate_nonfinite": COMPUTATION_NOT_EVALUABLE,
    "standard_error_nonfinite": COMPUTATION_NOT_EVALUABLE,
    "standard_error_negative": INVALID_RECORD_MONITOR,
    "standard_error_zero": INVALID_RECORD_MONITOR,
    "critical_value_uncalibrated": INCOMPLETE_INPUT,
    "critical_value_invalid": INVALID_RECORD_MONITOR,
    "critical_value_provenance_missing": INCOMPLETE_INPUT,
    "bounded_bias_evidence_missing": INCOMPLETE_INPUT,
    "bounded_bias_invalid": INVALID_RECORD_MONITOR,
    "endpoint_identity_mismatch": INVALID_RECORD_MONITOR,
}


def _interval_refusal(code: str, **detail) -> Refusal:
    return refuse(
        _INTERVAL_CODE_FAMILY.get(code, COMPUTATION_NOT_EVALUABLE),
        f"interval {code}",
        f"interval evidence is not usable for inference: {code}",
        interval_defect=code,
        **detail,
    )


# ---------------------------------------------------------------------------
# Stage 2: the T-stage conjunction
# ---------------------------------------------------------------------------

def complete_pipeline_result(
    records: Sequence[RecordResultV4],
    contrasts: Sequence[ContrastResultV4],
    diagnostic: DiagnosticFamilyResult | None,
    extra_reasons: Sequence[Refusal] = (),
) -> CompleteResult:
    """Judge one complete eight-record experiment. The single source of truth.

    Required, each fail-closed on absence:

    * exactly eight records on the canonical ``(block, field)`` keys;
    * eight Branch-A and eight observation/support packets valid;
    * eight field-realization statuses VALID;
    * eight well-formed absolute equivalence intervals inside the margin;
    * exactly six well-formed within-block contrast intervals inside theirs;
    * eight calibrated shape, centre, stationarity and current upper limits;
    * one calibrated, coherent diagnostic-family result that does not reject;
    * bounded-bias evidence everywhere an interval is enlarged by it.
    """
    reasons: list[Refusal] = list(extra_reasons)
    evidence_reasons = validate_evidence(records, contrasts, diagnostic)
    reasons.extend(evidence_reasons)
    evidence_ok = not evidence_reasons

    n_total = len(RECORDS)
    by_key: dict[RecordKey, RecordResultV4] = {}
    conflicted: set[RecordKey] = set()
    for rec in records:
        if rec.key in by_key:
            conflicted.add(rec.key)
        by_key[rec.key] = rec

    absolute_pass = contrast_pass = 0
    shape_pass = centre_pass = stationarity_pass = current_pass = 0
    realization_valid = branch_a_valid = observation_valid = 0
    current_inconclusive = 0
    not_evaluable = False

    for key in RecordKey.expected():
        rec = by_key.get(key)
        if rec is None or key in conflicted:
            # Absent, or supplied more than once: either way there is no single
            # result for this identity, so nothing here may count as a pass.
            continue
        ident = rec.identity
        if not rec.evaluable:
            not_evaluable = True
            reasons.append(refuse(
                COMPUTATION_NOT_EVALUABLE, "record evaluable",
                "record did not produce a usable result", record=ident,
            ))
            reasons.extend(rec.reasons)
            continue
        reasons.extend(rec.reasons)

        if rec.branch_a_valid is True:
            branch_a_valid += 1
        else:
            reasons.append(refuse(
                INCOMPLETE_INPUT if rec.branch_a_valid is None
                else COMPUTATION_NOT_EVALUABLE,
                "Branch-A packet valid",
                "Branch-A validity absent" if rec.branch_a_valid is None
                else "Branch-A packet is not valid",
                record=ident,
            ))
        if rec.observation_valid is True:
            observation_valid += 1
        else:
            reasons.append(refuse(
                INCOMPLETE_INPUT if rec.observation_valid is None
                else COMPUTATION_NOT_EVALUABLE,
                "observation/support packet valid",
                "observation validity absent" if rec.observation_valid is None
                else "observation/support packet is not valid",
                record=ident,
            ))
        if rec.realization_status == FIELD_REALIZATION_VALID:
            realization_valid += 1
        else:
            reasons.append(refuse(
                INCOMPLETE_INPUT if rec.realization_status is None
                else COMPUTATION_NOT_EVALUABLE,
                "field realization VALID",
                "realization status absent" if rec.realization_status is None
                else f"realization status is {rec.realization_status}",
                record=ident,
            ))

        if rec.absolute is not None and rec.absolute.strictly_inside(DELTA_A) is True:
            absolute_pass += 1

        for limit, tol, name, counter in (
            (rec.shape, DELTA_G, "shape", "shape"),
            (rec.centre, DELTA_M, "centre", "centre"),
            (rec.stationarity, DELTA_STATIONARITY, "stationarity", "stationarity"),
            (rec.current, DELTA_R_IRR, "current", "current"),
        ):
            ok = limit.passes(tol)
            if ok is True:
                if name == "shape":
                    shape_pass += 1
                elif name == "centre":
                    centre_pass += 1
                elif name == "stationarity":
                    stationarity_pass += 1
                else:
                    current_pass += 1
            elif ok is None:
                reasons.append(refuse(
                    INCOMPLETE_INPUT, f"{name} upper limit calibrated",
                    f"no calibrated {name} upper limit "
                    f"({'; '.join(limit.defects) or 'unavailable'}); the raw "
                    "statistic may not be compared against the tolerance in "
                    "its place",
                    record=ident, defects=list(limit.defects),
                ))
            elif name == "current" and limit.statistic is not None and (
                math.isfinite(limit.statistic) and limit.statistic < tol
            ):
                current_inconclusive += 1

    for key in ContrastKey.expected():
        matches = [c for c in contrasts if c.key == key]
        if len(matches) != 1:
            continue
        con = matches[0]
        reasons.extend(con.reasons)
        if con.interval is not None and con.interval.strictly_inside(DELTA_C) is True:
            contrast_pass += 1

    if diagnostic is None or diagnostic.status != DIAG_CALIBRATED:
        not_evaluable = not_evaluable or (
            diagnostic is None or diagnostic.status == DIAG_NOT_EVALUABLE
        )
        diagnostic_rejected = False
    else:
        diagnostic_rejected = bool(diagnostic.rejected)

    tally = ComponentTally(
        absolute_pass=absolute_pass,
        absolute_total=n_total,
        contrast_pass=contrast_pass,
        contrast_total=len(CONTRASTS),
        shape_pass=shape_pass,
        centre_pass=centre_pass,
        stationarity_pass=stationarity_pass,
        current_pass=current_pass,
        current_inconclusive=current_inconclusive,
        record_total=n_total,
        diagnostic_rejected=diagnostic_rejected,
        realization_valid=realization_valid,
        branch_a_valid=branch_a_valid,
        observation_valid=observation_valid,
    )
    verdict = decide(tally, reasons, not_evaluable=not_evaluable)
    return CompleteResult(
        verdict=verdict,
        tally=tally,
        records=tuple(records),
        contrasts=tuple(contrasts),
        diagnostic=diagnostic,
        reasons=tuple(reasons),
        evidence_ok=evidence_ok,
    )
