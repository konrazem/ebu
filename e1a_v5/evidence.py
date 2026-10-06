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

import hashlib
import json
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

class GateFamily(str, Enum):
    """The four precision gates, as a closed set of typed families."""

    SHAPE = "shape"
    CENTRE = "centre"
    STATIONARITY = "stationarity"
    CURRENT = "current"


#: Identity namespace reserved for test-only calibration artifacts.
FIXTURE_NAMESPACE = "SYNTHETIC-FIXTURE"


@dataclass(frozen=True)
class GateExpectations:
    """What a production gate calibration must match to be applicable here.

    These are the CURRENT frozen identities of the running procedure.  A
    receipt that does not reproduce every one of them was produced by a
    different procedure, a different plan, a different seed architecture or a
    different nuisance domain, and does not apply to these records.
    """

    procedure_version: int
    analysis_identity: str
    validation_identity: str
    plan_identity: str
    seed_map_identity: str
    domain_identity: str
    coverage_target: float
    calibration_seed_namespace: str


@dataclass(frozen=True)
class GateCalibrationReceipt:
    """A VERIFIABLE record that a gate's critical value was actually calibrated.

    V5 replaced V4's bare identity string with a typed artifact, which the
    audit still rejected -- and rightly.  Typing the fields does not make them
    evidence: an ordinary caller could still construct the type and fill every
    field with whatever strings it liked, so a nonempty identity remained the
    whole of the trust model.

    A receipt is different in kind.  It binds the calibration to the exact
    frozen identities of the procedure that produced it, to the plan and seed
    architecture it was drawn under, to the case domain it covers and to the
    digest of the calibration result itself; and it carries a digest OF ALL OF
    THAT, which the production builder recomputes.  A caller who invents field
    values gets a receipt whose digest does not recompute; a caller who copies
    a real receipt and alters one field gets the same; a caller who supplies a
    genuine receipt from another procedure version, another plan or another
    domain is refused on the identity comparison.
    """

    family: GateFamily
    procedure_version: int
    analysis_identity: str
    validation_identity: str
    plan_identity: str
    seed_map_identity: str
    calibration_seed_namespace: str
    calibration_identity: str
    domain_identity: str
    replicates: int
    radius: float
    coverage_target: float
    #: Digest of the calibration result the radius was read from.
    result_digest: str
    #: Digest of every field above.  Recomputed on use.
    receipt_digest: str = ""
    #: Whether the calibration run is complete and released.
    released: bool = False

    def payload(self) -> str:
        """The canonical preimage of :attr:`receipt_digest`."""
        return json.dumps(
            {
                "family": self.family.value if isinstance(self.family, GateFamily)
                else str(self.family),
                "procedure_version": self.procedure_version,
                "analysis_identity": self.analysis_identity,
                "validation_identity": self.validation_identity,
                "plan_identity": self.plan_identity,
                "seed_map_identity": self.seed_map_identity,
                "calibration_seed_namespace": self.calibration_seed_namespace,
                "calibration_identity": self.calibration_identity,
                "domain_identity": self.domain_identity,
                "replicates": self.replicates,
                "radius": self.radius,
                "coverage_target": self.coverage_target,
                "result_digest": self.result_digest,
                "released": bool(self.released),
            },
            sort_keys=True, separators=(",", ":"),
        )

    def recomputed_digest(self) -> str:
        return hashlib.sha256(self.payload().encode("utf-8")).hexdigest()

    def sealed(self) -> "GateCalibrationReceipt":
        """The same receipt with its digest computed.  Used by the issuer."""
        return GateCalibrationReceipt(
            **{**self.__dict__, "receipt_digest": self.recomputed_digest()}
        )

    def defects(self, expected: GateExpectations, family: GateFamily) -> list[str]:
        bad: list[str] = []
        if not isinstance(self.family, GateFamily):
            bad.append("gate_family_untyped")
        elif self.family is not family:
            bad.append(GATE_WRONG_FAMILY)
        if not self.released:
            bad.append(GATE_NOT_RELEASED)
        if self.procedure_version != expected.procedure_version:
            bad.append(GATE_WRONG_VERSION)
        for got, want, code in (
            (self.analysis_identity, expected.analysis_identity, GATE_WRONG_ANALYSIS),
            (self.validation_identity, expected.validation_identity,
             GATE_WRONG_VALIDATION),
            (self.plan_identity, expected.plan_identity, GATE_WRONG_PLAN),
            (self.seed_map_identity, expected.seed_map_identity, GATE_WRONG_SEED_MAP),
            (self.domain_identity, expected.domain_identity, GATE_WRONG_DOMAIN),
            (self.calibration_seed_namespace, expected.calibration_seed_namespace,
             GATE_WRONG_SEED_NAMESPACE),
        ):
            if not got or got != want:
                bad.append(code)
        if self.coverage_target != expected.coverage_target:
            bad.append(GATE_WRONG_COVERAGE)
        if not self.calibration_identity:
            bad.append("calibration_identity_missing")
        if not self.result_digest:
            bad.append(GATE_RESULT_DIGEST_MISSING)
        if not isinstance(self.replicates, int) or self.replicates <= 0:
            bad.append(GATE_REPLICATES_INVALID)
        if not (isinstance(self.radius, float) and math.isfinite(self.radius)
                and self.radius >= 0.0):
            bad.append("radius_invalid")
        if not self.receipt_digest or self.receipt_digest != self.recomputed_digest():
            bad.append(GATE_DIGEST_MISMATCH)
        return bad

    def upper_limit(self, statistic: float) -> float:
        """``statistic + radius``.  There is no path that returns the statistic."""
        return float(statistic) + float(self.radius)


@dataclass(frozen=True)
class SyntheticGateFixture:
    """A TEST-ONLY calibrated gate artifact, of a DIFFERENT TYPE.

    V5 marked fixtures with a ``fixture_only`` boolean on the same class the
    production builder trusted, so an ordinary caller could forge a production
    artifact by leaving the flag False.  Separation is by type instead: no
    production API accepts this class, and the separation cannot be defeated
    by setting a field.
    """

    family: GateFamily
    radius: float
    coverage_target: float = 0.975
    namespace: str = FIXTURE_NAMESPACE

    def upper_limit(self, statistic: float) -> float:
        return float(statistic) + float(self.radius)


def synthetic_calibrated_gate_fixture(
    family: GateFamily, radius: float, coverage_target: float = 0.975,
) -> SyntheticGateFixture:
    """A TEST-ONLY calibrated gate artifact.  Production APIs refuse the type."""
    return SyntheticGateFixture(family, float(radius), coverage_target)


GATE_UNCALIBRATED = "uncalibrated"
GATE_NO_PROCEDURE = "no_calibration_receipt"
GATE_NOT_A_RECEIPT = "artifact_is_not_a_calibration_receipt"
GATE_NOT_RELEASED = "calibration_result_not_released"
GATE_WRONG_FAMILY = "receipt_is_for_a_different_gate"
GATE_WRONG_VERSION = "receipt_is_for_a_different_procedure_version"
GATE_WRONG_DOMAIN = "receipt_domain_does_not_cover_this_record"
GATE_WRONG_ANALYSIS = "receipt_analysis_identity_mismatch"
GATE_WRONG_VALIDATION = "receipt_validation_identity_mismatch"
GATE_WRONG_PLAN = "receipt_validation_plan_identity_mismatch"
GATE_WRONG_SEED_MAP = "receipt_seed_map_identity_mismatch"
GATE_WRONG_SEED_NAMESPACE = "receipt_calibration_seed_namespace_mismatch"
GATE_WRONG_COVERAGE = "receipt_coverage_target_mismatch"
GATE_DIGEST_MISMATCH = "receipt_digest_does_not_recompute"
GATE_RESULT_DIGEST_MISSING = "calibration_result_digest_missing"
GATE_REPLICATES_INVALID = "calibration_replicate_count_invalid"
GATE_FIXTURE_IN_PRODUCTION = "test_only_fixture_used_in_production"
GATE_STATISTIC_NONFINITE = "statistic_nonfinite"


@dataclass(frozen=True)
class GateLimit:
    """A one-sided upper confidence limit, with the artifact that produced it.

    The raw statistic and the upper limit are separate fields and the limit is
    always ``statistic + radius``.  There is no constructor that accepts a
    limit, so ``upper_limit = raw_statistic`` cannot be expressed.
    """

    statistic: float | None = None
    limit: float | None = None
    receipt: GateCalibrationReceipt | None = None
    defects: tuple[str, ...] = (GATE_NO_PROCEDURE,)
    #: True when the limit came from a TEST-ONLY fixture.
    fixture: bool = False

    @staticmethod
    def uncalibrated(statistic: float | None = None) -> "GateLimit":
        """A measured statistic with no calibration behind it."""
        return GateLimit(statistic, None, None, (GATE_NO_PROCEDURE,))

    @staticmethod
    def from_receipt(
        statistic: float | None,
        receipt: object,
        family: GateFamily,
        expected: GateExpectations,
    ) -> "GateLimit":
        """Build a limit from a VERIFIED production calibration receipt.

        Everything is checked: the artifact's type, the gate family, the
        procedure version, the analysis / validation / plan / seed-map
        identities, the calibration seed namespace, the coverage target, the
        release state, the replicate count, the result digest and the
        receipt's own digest.  Nothing is taken on the strength of a field
        being nonempty.
        """
        bad: list[str] = []
        if statistic is None or not math.isfinite(statistic):
            bad.append(GATE_STATISTIC_NONFINITE)
        if receipt is None:
            bad.append(GATE_NO_PROCEDURE)
            return GateLimit(statistic, None, None, tuple(bad))
        if isinstance(receipt, SyntheticGateFixture):
            bad.append(GATE_FIXTURE_IN_PRODUCTION)
            return GateLimit(statistic, None, None, tuple(bad))
        if not isinstance(receipt, GateCalibrationReceipt):
            bad.append(GATE_NOT_A_RECEIPT)
            return GateLimit(statistic, None, None, tuple(bad))
        bad.extend(receipt.defects(expected, family))
        if bad:
            return GateLimit(statistic, None, receipt, tuple(bad))
        return GateLimit(statistic, receipt.upper_limit(statistic), receipt, ())

    @staticmethod
    def from_fixture(
        statistic: float | None, fixture: object, family: GateFamily,
    ) -> "GateLimit":
        """TEST-ONLY.  Accepts the fixture type and nothing else."""
        bad: list[str] = []
        if statistic is None or not math.isfinite(statistic):
            bad.append(GATE_STATISTIC_NONFINITE)
        if not isinstance(fixture, SyntheticGateFixture):
            return GateLimit(statistic, None, None, (GATE_NOT_A_RECEIPT,), True)
        if fixture.family is not family:
            bad.append(GATE_WRONG_FAMILY)
        if not (math.isfinite(fixture.radius) and fixture.radius >= 0.0):
            bad.append("radius_invalid")
        if bad:
            return GateLimit(statistic, None, None, tuple(bad), True)
        return GateLimit(statistic, fixture.upper_limit(statistic), None, (), True)

    @property
    def usable(self) -> bool:
        return (
            not self.defects
            and self.limit is not None
            and math.isfinite(self.limit)
        )

    def passes(self, tolerance: float) -> bool | None:
        """``limit < tolerance``, or ``None`` when no calibrated limit exists."""
        if not self.usable:
            return None
        return self.limit < tolerance  # type: ignore[operator]

    def enlarged(self, systematic: float) -> "GateLimit":
        """Add a certified systematic shift to the limit.

        Used to route the exact finite axial-remainder effect into the gate's
        EXISTING budget rather than giving it an allowance of its own.
        """
        if not self.usable:
            return self
        return GateLimit(self.statistic, self.limit + float(systematic),
                         self.receipt, (), self.fixture)

    def scaled(self, factor: float) -> "GateLimit":
        """Multiply the limit by a certified factor (a purely multiplicative effect)."""
        if not self.usable:
            return self
        return GateLimit(self.statistic, self.limit * float(factor),
                         self.receipt, (), self.fixture)
