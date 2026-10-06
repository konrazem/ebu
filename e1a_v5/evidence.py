"""Evidence validation before any verdict is evaluated: Layer K.

V3 judged whatever dictionary it was handed.  The independent audit showed
three ways malformed evidence still reached
``SUPPORTED_WITHIN_DECLARED_TOLERANCES``:

* records were collected into a ``{key: record}`` map, so a duplicate silently
  overwrote its predecessor and an invalid record could disappear behind a
  valid one carrying the same identity;
* a ninth record was ignored rather than refused;
* :class:`~e1a_v5.confidence.Interval` had no validity notion at all, so a
  reversed pair such as ``(+0.9, -0.9)`` satisfied ``-margin < lo`` and
  ``hi < margin`` and was reported as contained.

This module is the gate that runs *before* the conjunction.  It establishes
that the evidence describes the preregistered experiment -- exactly eight
records on the canonical ``(block, field)`` keys, exactly six within-block
contrasts against the correct reference field -- and that every interval,
critical value and bias bound presented for inference is well formed.

Nothing here is a scientific tolerance.  These are structural preconditions:
failing one means the evidence is not a measurement of the planned experiment,
which is ``INCOMPLETE_INPUT`` or ``INVALID``, never a quiet pass.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Mapping, Sequence

from .confidence import CriticalValueStatus, CriticalValues, Interval
from .packets import CONTRASTS, RECORDS, BlockId, FieldId
from .refusals import (
    INCOMPLETE_INPUT,
    INVALID_RECORD_MONITOR,
    MISSING_COVARIANCE,
    NUMERICAL_REPRESENTATION_FAILURE,
    Refusal,
    refuse,
)

#: The reference field every within-block contrast is taken against (T.10).
CONTRAST_REFERENCE = FieldId.THETA0


# ---------------------------------------------------------------------------
# Canonical identities
# ---------------------------------------------------------------------------

@dataclass(frozen=True, order=True)
class RecordKey:
    """The canonical identity of one record: ``(block_id, field_id)``.

    Typed, hashable and total-ordered so the eight expected keys form a fixed
    set that can be compared exactly against what was supplied.
    """

    block: BlockId
    fld: FieldId

    def __str__(self) -> str:
        return f"{self.block.value}/{self.fld.value}"

    @staticmethod
    def expected() -> tuple["RecordKey", ...]:
        return tuple(RecordKey(b, f) for b, f in RECORDS)


@dataclass(frozen=True, order=True)
class ContrastKey:
    """The canonical identity of one within-block contrast.

    ``field`` is the challenge field and ``reference`` is always theta0 in the
    SAME block.  Carrying the reference explicitly is what makes a contrast
    against the wrong field, or a cross-block contrast, detectable.
    """

    block: BlockId
    fld: FieldId
    reference: FieldId = CONTRAST_REFERENCE
    reference_block: BlockId | None = None

    def __post_init__(self) -> None:
        if self.reference_block is None:
            object.__setattr__(self, "reference_block", self.block)

    def __str__(self) -> str:
        return (
            f"{self.block.value}/{self.fld.value}"
            f"-{self.reference_block.value}/{self.reference.value}"  # type: ignore[union-attr]
        )

    @property
    def well_formed(self) -> bool:
        """Within-block, against theta0, and not theta0 against itself."""
        return (
            self.reference is CONTRAST_REFERENCE
            and self.reference_block == self.block
            and self.fld is not CONTRAST_REFERENCE
        )

    @staticmethod
    def expected() -> tuple["ContrastKey", ...]:
        return tuple(ContrastKey(b, f) for b, f in CONTRASTS)


# ---------------------------------------------------------------------------
# Interval validity
# ---------------------------------------------------------------------------

IV_OK = "valid"
IV_MISSING = "interval_absent"
IV_NONFINITE = "interval_endpoint_nonfinite"
IV_REVERSED = "interval_endpoints_reversed"
IV_ESTIMATE_NONFINITE = "estimate_nonfinite"
IV_SE_NONFINITE = "standard_error_nonfinite"
IV_SE_NEGATIVE = "standard_error_negative"
IV_SE_ZERO = "standard_error_zero"
IV_CRITICAL_UNCALIBRATED = "critical_value_uncalibrated"
IV_CRITICAL_INVALID = "critical_value_invalid"
IV_CRITICAL_MISSING = "critical_value_provenance_missing"
IV_BIAS_MISSING = "bounded_bias_evidence_missing"
IV_BIAS_INVALID = "bounded_bias_invalid"
IV_ENDPOINT_MISMATCH = "endpoint_identity_mismatch"


@dataclass(frozen=True)
class ScientificInterval:
    """An interval that carries the evidence entitling it to be tested.

    A bare ``(lo, hi)`` pair cannot be checked for anything, so the pieces that
    produced it travel with it: the estimate, its standard error, the
    calibrated critical values and their status, and the bounded-bias
    enlargement actually applied.  :meth:`validate` re-derives the endpoints
    from those pieces, which is what makes an endpoint identity mismatch --
    an interval whose numbers do not follow from its own inputs -- detectable.
    """

    interval: Interval | None
    estimate: float | None = None
    standard_error: float | None = None
    critical: CriticalValues | None = None
    bias_bound: float | None = None
    #: Whether a strictly positive SE is scientifically required here.
    requires_positive_se: bool = True
    #: Relative tolerance for the endpoint re-derivation check.
    endpoint_rtol: float = 1e-9

    def validate(self) -> list[str]:
        """Return every reason this interval may not enter inference."""
        bad: list[str] = []
        iv = self.interval
        if iv is None:
            return [IV_MISSING]
        if not (math.isfinite(iv.lo) and math.isfinite(iv.hi)):
            bad.append(IV_NONFINITE)
        elif iv.lo > iv.hi:
            bad.append(IV_REVERSED)

        if self.estimate is not None and not math.isfinite(self.estimate):
            bad.append(IV_ESTIMATE_NONFINITE)
        se = self.standard_error
        if se is not None:
            if not math.isfinite(se):
                bad.append(IV_SE_NONFINITE)
            elif se < 0.0:
                bad.append(IV_SE_NEGATIVE)
            elif se == 0.0 and self.requires_positive_se:
                bad.append(IV_SE_ZERO)

        crit = self.critical
        if crit is None:
            bad.append(IV_CRITICAL_MISSING)
        else:
            if crit.status is CriticalValueStatus.UNCALIBRATED:
                bad.append(IV_CRITICAL_UNCALIBRATED)
            elif crit.status is CriticalValueStatus.INVALID:
                bad.append(IV_CRITICAL_INVALID)
            if not crit.provenance:
                bad.append(IV_CRITICAL_MISSING)

        if self.bias_bound is None:
            bad.append(IV_BIAS_MISSING)
        elif not math.isfinite(self.bias_bound) or self.bias_bound < 0.0:
            bad.append(IV_BIAS_INVALID)

        if (
            not bad
            and self.estimate is not None
            and se is not None
            and crit is not None
            and self.bias_bound is not None
        ):
            lo = self.estimate - crit.c_minus * se - self.bias_bound
            hi = self.estimate + crit.c_plus * se + self.bias_bound
            scale = max(abs(lo), abs(hi), abs(self.estimate), 1e-300)
            if (
                abs(lo - iv.lo) > self.endpoint_rtol * scale
                or abs(hi - iv.hi) > self.endpoint_rtol * scale
            ):
                bad.append(IV_ENDPOINT_MISMATCH)
        return bad

    @property
    def usable(self) -> bool:
        return not self.validate()

    def strictly_inside(self, margin: float) -> bool | None:
        """Containment, or ``None`` when the interval may not be tested at all.

        ``None`` is deliberately not ``False``: an unusable interval has no
        containment answer, and the caller must classify it as missing
        evidence rather than as a failed equivalence test.
        """
        if not self.usable or self.interval is None:
            return None
        return self.interval.strictly_inside(margin)


# ---------------------------------------------------------------------------
# Bounded-bias evidence (missing is not zero)
# ---------------------------------------------------------------------------

class BiasStatus(str, Enum):
    QUALIFIED = "qualified"
    MISSING = "missing"
    INVALID = "invalid"


@dataclass(frozen=True)
class BiasEvidence:
    """A bounded systematic magnitude that distinguishes zero from absent.

    ``BiasEvidence.qualified(0.0)`` is a certified claim that the bound is
    zero.  ``BiasEvidence.missing()`` is the absence of any claim.  V3 let the
    second become the first through ``dict.get(key, 0.0)``.
    """

    status: BiasStatus
    bound: float | None = None
    source: str = ""

    @staticmethod
    def qualified(bound: float, source: str = "") -> "BiasEvidence":
        if not math.isfinite(bound) or bound < 0.0:
            return BiasEvidence(BiasStatus.INVALID, bound, source)
        return BiasEvidence(BiasStatus.QUALIFIED, float(bound), source)

    @staticmethod
    def missing(source: str = "") -> "BiasEvidence":
        return BiasEvidence(BiasStatus.MISSING, None, source)

    @property
    def usable(self) -> bool:
        return self.status is BiasStatus.QUALIFIED and self.bound is not None

    def require(self) -> float:
        if not self.usable:
            raise ValueError(f"bounded bias unavailable: {self.status.value}")
        return float(self.bound)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Experiment cardinality
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CardinalityReport:
    """What a supplied collection of identities is, against what was planned."""

    duplicates: tuple[str, ...] = ()
    extras: tuple[str, ...] = ()
    missing: tuple[str, ...] = ()
    malformed: tuple[str, ...] = ()
    inconsistent: tuple[str, ...] = ()

    @property
    def ok(self) -> bool:
        return not (
            self.duplicates or self.extras or self.missing
            or self.malformed or self.inconsistent
        )


def _tally(keys: Sequence[object]) -> dict[object, int]:
    counts: dict[object, int] = {}
    for k in keys:
        counts[k] = counts.get(k, 0) + 1
    return counts


def check_record_cardinality(
    supplied: Sequence[RecordKey],
    embedded: Sequence[RecordKey] | None = None,
) -> CardinalityReport:
    """Exactly one record per expected ``(block, field)``.

    ``embedded`` is each record's own metadata identity, checked against the
    identity it was filed under: a record whose contents disagree with its key
    is inconsistent evidence, not a record to be re-filed.
    """
    expected = set(RecordKey.expected())
    counts = _tally(list(supplied))
    duplicates = sorted(str(k) for k, n in counts.items() if n > 1)
    extras = sorted(str(k) for k in counts if k not in expected)
    missing = sorted(str(k) for k in expected if k not in counts)
    inconsistent: list[str] = []
    if embedded is not None:
        if len(embedded) != len(supplied):
            inconsistent.append("embedded identity count differs from record count")
        else:
            for filed, own in zip(supplied, embedded):
                if filed != own:
                    inconsistent.append(f"{filed} filed under identity of {own}")
    return CardinalityReport(
        duplicates=tuple(duplicates),
        extras=tuple(extras),
        missing=tuple(missing),
        inconsistent=tuple(sorted(inconsistent)),
    )


def check_contrast_cardinality(supplied: Sequence[ContrastKey]) -> CardinalityReport:
    """Exactly the six preregistered within-block contrasts, each once."""
    expected = set(ContrastKey.expected())
    counts = _tally(list(supplied))
    duplicates = sorted(str(k) for k, n in counts.items() if n > 1)
    malformed = sorted(str(k) for k in counts if not k.well_formed)
    extras = sorted(str(k) for k in counts if k.well_formed and k not in expected)
    missing = sorted(str(k) for k in expected if k not in counts)
    return CardinalityReport(
        duplicates=tuple(duplicates),
        extras=tuple(extras),
        missing=tuple(missing),
        malformed=tuple(malformed),
    )


def cardinality_refusals(report: CardinalityReport, what: str) -> list[Refusal]:
    """Translate a cardinality report into structured refusals."""
    out: list[Refusal] = []
    for key in report.duplicates:
        out.append(refuse(
            INVALID_RECORD_MONITOR,
            f"exactly one {what} per identity",
            f"duplicate {what} identity {key}; no selection rule (first, last, "
            "best or valid) is permitted",
            identity=key,
        ))
    for key in report.extras:
        out.append(refuse(
            INVALID_RECORD_MONITOR,
            f"{what} identity is one of the preregistered set",
            f"unplanned {what} {key} supplied",
            identity=key,
        ))
    for key in report.malformed:
        out.append(refuse(
            INVALID_RECORD_MONITOR,
            f"{what} identity well formed",
            f"{what} {key} is not a within-block contrast against theta0",
            identity=key,
        ))
    for key in report.missing:
        out.append(refuse(
            INCOMPLETE_INPUT,
            f"{what} present",
            f"required {what} {key} is absent",
            identity=key,
        ))
    for note in report.inconsistent:
        out.append(refuse(
            INVALID_RECORD_MONITOR,
            "record identity matches its embedded metadata",
            note,
        ))
    return out


# ---------------------------------------------------------------------------
# Calibrated gate limits
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class GateLimit:
    """A one-sided upper confidence limit with its calibration status.

    The four precision gates (shape, centre, stationarity, current) are
    calibrated one-sided upper limits, not raw statistics.  An uncalibrated
    limit cannot pass: comparing the raw statistic against the tolerance is
    exactly the shortcut the audit found in the control runner.
    """

    statistic: float | None = None
    limit: float | None = None
    status: CriticalValueStatus = CriticalValueStatus.UNCALIBRATED
    identity: str = ""

    @staticmethod
    def uncalibrated(statistic: float | None = None) -> "GateLimit":
        return GateLimit(statistic, None, CriticalValueStatus.UNCALIBRATED, "")

    @staticmethod
    def calibrated(statistic: float, limit: float, identity: str) -> "GateLimit":
        if not identity:
            return GateLimit(statistic, limit, CriticalValueStatus.INVALID, "")
        if not (math.isfinite(limit) and math.isfinite(statistic)):
            return GateLimit(statistic, limit, CriticalValueStatus.INVALID, identity)
        return GateLimit(statistic, limit, CriticalValueStatus.CALIBRATED, identity)

    @property
    def usable(self) -> bool:
        return (
            self.status is CriticalValueStatus.CALIBRATED
            and self.limit is not None
            and math.isfinite(self.limit)
        )

    def passes(self, tolerance: float) -> bool | None:
        """``limit < tolerance``, or ``None`` when no calibrated limit exists."""
        if not self.usable:
            return None
        return self.limit < tolerance  # type: ignore[operator]
