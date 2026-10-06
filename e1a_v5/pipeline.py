"""The single authoritative complete-experiment path.

V2 let the power runner reconstruct its own, weaker, success predicate: it
checked four per-record gates and never the cross-field contrasts,
stationarity, the diagnostic family, the realized-field statuses or packet
validity, and it never called the verdict engine at all.  A complete success
could therefore be counted while required conditions were unchecked.

Here there is exactly ONE place a complete experiment is judged:

    complete_pipeline_result(...)  ->  decide(...)  ->  Verdict

and ``counts_as_complete_success`` is true only when the verdict is
``SUPPORTED_WITHIN_DECLARED_TOLERANCES``.  Runners must not re-implement it.

Every required result is fail-closed: missing, ``None``, ``NaN``, not
evaluated, optimiser-failed and qualification-unavailable all prevent success
and are classified under T/U semantics rather than defaulted to a pass.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Mapping, Sequence

from .confidence import (
    DELTA_A,
    DELTA_C,
    CriticalValues,
    Interval,
    build_interval,
)
from .gates import DELTA_G, DELTA_M, DELTA_R_IRR
from .packets import CONTRASTS, RECORDS, BlockId, FieldId
from .realization import FIELD_REALIZATION_VALID
from .refusals import (
    COMPUTATION_NOT_EVALUABLE,
    INCOMPLETE_INPUT,
    Refusal,
    refuse,
)
from .verdict import ComponentTally, SUPPORTED, Verdict, decide


def record_key(block: BlockId, fld: FieldId) -> str:
    return f"{block.value}/{fld.value}"


def contrast_key(block: BlockId, fld: FieldId) -> str:
    return f"{block.value}/{fld.value}-{FieldId.THETA0.value}"


@dataclass(frozen=True)
class RecordResultV3:
    """One record's complete, explicitly-typed result.

    Every inferential field is ``None`` when it was not established.  There is
    no sentinel that reads as a pass.
    """

    block: BlockId
    fld: FieldId
    branch_a_valid: bool | None = None
    observation_valid: bool | None = None
    realization_status: str | None = None
    log_beta: float | None = None
    log_beta_se: float | None = None
    absolute_interval: Interval | None = None
    geometry: float | None = None
    geometry_limit: float | None = None
    centre: float | None = None
    centre_limit: float | None = None
    stationarity: float | None = None
    stationarity_limit: float | None = None
    r_irr: float | None = None
    r_irr_limit: float | None = None
    diagnostic_max: float | None = None
    diagnostic_rejected: bool | None = None
    evaluable: bool = True
    reasons: tuple[Refusal, ...] = ()

    @property
    def key(self) -> str:
        return record_key(self.block, self.fld)


def _finite(x: float | None) -> bool:
    return x is not None and isinstance(x, float) and math.isfinite(x)


@dataclass(frozen=True)
class CompleteResult:
    """The outcome of one complete eight-record synthetic experiment."""

    verdict: Verdict
    tally: ComponentTally
    records: tuple[RecordResultV3, ...]
    contrast_intervals: Mapping[str, Interval | None]
    reasons: tuple[Refusal, ...]

    @property
    def counts_as_complete_success(self) -> bool:
        """The ONLY success predicate. Runners must call this, not rebuild it."""
        return self.verdict.classification == SUPPORTED

    def reason_codes(self) -> list[str]:
        return [r.code for r in self.reasons]

    def as_dict(self) -> dict:
        return {
            "classification": self.verdict.classification,
            "qualifier": self.verdict.qualifier,
            "success": self.counts_as_complete_success,
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


def complete_pipeline_result(
    records: Sequence[RecordResultV3],
    contrast_intervals: Mapping[str, Interval | None],
    diagnostic_family_rejected: bool | None,
    extra_reasons: Sequence[Refusal] = (),
) -> CompleteResult:
    """Judge one complete eight-record experiment. The single source of truth.

    Required, and each fail-closed on absence:

    * eight Branch-A / calibration packets valid;
    * eight observation / support packets valid;
    * eight field-realization statuses VALID;
    * eight absolute equivalence intervals strictly inside the margin;
    * six within-block contrast intervals strictly inside the margin;
    * eight shape, centre, stationarity and current upper limits below tolerance;
    * the diagnostic family evaluated and not rejecting;
    * every required numerical / optimiser evaluation succeeded.
    """
    reasons: list[Refusal] = list(extra_reasons)
    by_key = {r.key: r for r in records}

    missing = [record_key(b, f) for b, f in RECORDS if record_key(b, f) not in by_key]
    for key in missing:
        reasons.append(
            refuse(
                INCOMPLETE_INPUT,
                "record present",
                "a required record is absent from the experiment",
                record=key,
            )
        )

    n_total = len(RECORDS)
    absolute_pass = contrast_pass = 0
    shape_pass = centre_pass = stationarity_pass = current_pass = 0
    realization_valid = branch_a_valid = observation_valid = 0
    current_inconclusive = 0
    not_evaluable = False

    for b, f in RECORDS:
        key = record_key(b, f)
        rec = by_key.get(key)
        if rec is None:
            continue
        if not rec.evaluable:
            not_evaluable = True
            reasons.append(
                refuse(
                    COMPUTATION_NOT_EVALUABLE,
                    "record evaluable",
                    "record did not produce a usable result",
                    record=key,
                )
            )
            reasons.extend(rec.reasons)
            continue
        reasons.extend(rec.reasons)

        if rec.branch_a_valid is True:
            branch_a_valid += 1
        else:
            reasons.append(
                refuse(
                    INCOMPLETE_INPUT if rec.branch_a_valid is None else COMPUTATION_NOT_EVALUABLE,
                    "Branch-A packet valid",
                    "Branch-A validity absent" if rec.branch_a_valid is None
                    else "Branch-A packet is not valid",
                    record=key,
                )
            )
        if rec.observation_valid is True:
            observation_valid += 1
        else:
            reasons.append(
                refuse(
                    INCOMPLETE_INPUT if rec.observation_valid is None else COMPUTATION_NOT_EVALUABLE,
                    "observation/support packet valid",
                    "observation validity absent" if rec.observation_valid is None
                    else "observation/support packet is not valid",
                    record=key,
                )
            )
        if rec.realization_status == FIELD_REALIZATION_VALID:
            realization_valid += 1
        else:
            reasons.append(
                refuse(
                    INCOMPLETE_INPUT if rec.realization_status is None else COMPUTATION_NOT_EVALUABLE,
                    "field realization VALID",
                    "realization status absent" if rec.realization_status is None
                    else f"realization status is {rec.realization_status}",
                    record=key,
                )
            )

        iv = rec.absolute_interval
        if iv is not None and _finite(iv.lo) and _finite(iv.hi) and iv.strictly_inside(DELTA_A):
            absolute_pass += 1
        elif iv is None:
            reasons.append(
                refuse(INCOMPLETE_INPUT, "absolute interval established",
                       "no absolute equivalence interval", record=key)
            )

        if _finite(rec.geometry_limit) and rec.geometry_limit < DELTA_G:  # type: ignore[operator]
            shape_pass += 1
        elif rec.geometry_limit is None:
            reasons.append(
                refuse(INCOMPLETE_INPUT, "shape upper limit established",
                       "no calibrated geometry upper limit", record=key)
            )
        if _finite(rec.centre_limit) and rec.centre_limit < DELTA_M:  # type: ignore[operator]
            centre_pass += 1
        elif rec.centre_limit is None:
            reasons.append(
                refuse(INCOMPLETE_INPUT, "centre upper limit established",
                       "no calibrated centre upper limit", record=key)
            )
        if _finite(rec.stationarity_limit) and rec.stationarity_limit < 1.0:  # type: ignore[operator]
            stationarity_pass += 1
        elif rec.stationarity_limit is None:
            reasons.append(
                refuse(INCOMPLETE_INPUT, "stationarity upper limit established",
                       "no calibrated stationarity upper limit", record=key)
            )
        if _finite(rec.r_irr_limit) and rec.r_irr_limit < DELTA_R_IRR:  # type: ignore[operator]
            current_pass += 1
        else:
            if rec.r_irr_limit is None:
                reasons.append(
                    refuse(INCOMPLETE_INPUT, "current upper limit established",
                           "no calibrated reversibility upper limit", record=key)
                )
            elif _finite(rec.r_irr) and rec.r_irr < DELTA_R_IRR:  # type: ignore[operator]
                current_inconclusive += 1

    for b, f in CONTRASTS:
        key = contrast_key(b, f)
        iv = contrast_intervals.get(key)
        if iv is not None and _finite(iv.lo) and _finite(iv.hi) and iv.strictly_inside(DELTA_C):
            contrast_pass += 1
        elif iv is None:
            reasons.append(
                refuse(INCOMPLETE_INPUT, "contrast interval established",
                       "no within-block contrast interval", contrast=key)
            )

    if diagnostic_family_rejected is None:
        not_evaluable = True
        reasons.append(
            refuse(
                COMPUTATION_NOT_EVALUABLE,
                "diagnostic family evaluated",
                "the diagnostic family was not evaluated; a diagnostic that was "
                "not computed is not a diagnostic that passed",
            )
        )

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
        diagnostic_rejected=bool(diagnostic_family_rejected),
        realization_valid=realization_valid,
        branch_a_valid=branch_a_valid,
        observation_valid=observation_valid,
    )
    verdict = decide(tally, reasons, not_evaluable=not_evaluable)
    return CompleteResult(
        verdict=verdict,
        tally=tally,
        records=tuple(records),
        contrast_intervals=dict(contrast_intervals),
        reasons=tuple(reasons),
    )
