"""Frozen model-diagnostic family: Layer J.

T-stage section 18 fixes the statistic as the maximum of three components,
each scaled by its frozen null standard deviation and calibrated jointly so
the dependence between components is preserved:

1. Cramer-von Mises distance of squared innovation radii from ``chi2_2``;
2. summed squared sine/cosine sample means at angular harmonics 1 through 4;
3. squared Frobenius norms of innovation lag covariances at lags 1 through 10,
   together with the three observed-minus-fitted lag-antisymmetry checks.

The lags and harmonics are fixed here, before any calibration; no search for a
favourable subset is permitted.  A zero or undefined null scale is a validation
failure, not a dropped component.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence

from . import numerics as nm
from .numerics import Matrix, NumericalFailure

#: Frozen diagnostic constants.
ANGULAR_HARMONICS = (1, 2, 3, 4)
INNOVATION_LAGS = tuple(range(1, 11))
#: Familywise false-rejection target across all eight records.
FAMILYWISE_TARGET = 0.005

#: T-stage 12.2 fixes three antisymmetry lags at tau_slow/2, tau_slow and
#: 2 tau_slow; these multipliers are frozen here before any calibration.
ANTISYMMETRY_TAU_MULTIPLIERS = (0.5, 1.0, 2.0)


class DiagnosticNotEvaluable(Exception):
    """Required diagnostic inputs were absent; the family is non-evaluable."""


def required_antisymmetry_lags(tau_slow: float, dt: float) -> tuple[int, int, int]:
    """Integer frame lags nearest ``tau_slow/2``, ``tau_slow`` and ``2 tau_slow``.

    Actual timestamps are preserved by working in frame units of the real
    sampling interval rather than assuming a nominal one.
    """
    if not (math.isfinite(tau_slow) and tau_slow > 0.0):
        raise DiagnosticNotEvaluable("tau_slow is not finite and positive")
    if not (math.isfinite(dt) and dt > 0.0):
        raise DiagnosticNotEvaluable("sampling interval is not finite and positive")
    lags = []
    for m in ANTISYMMETRY_TAU_MULTIPLIERS:
        k = int(round(m * tau_slow / dt))
        if k < 1:
            raise DiagnosticNotEvaluable(
                f"antisymmetry lag for multiplier {m} rounds to {k}; "
                "the sampling interval does not resolve it"
            )
        lags.append(k)
    return tuple(lags)  # type: ignore[return-value]


def standardise_innovations(
    innovations: Sequence[Sequence[float]], inn_cov: Matrix
) -> list[list[float]]:
    """Whiten innovations by the steady-state innovation covariance."""
    w = nm.inv_sqrtm_spd(inn_cov)
    d = len(inn_cov)
    return [
        [sum(w[i][j] * v[j] for j in range(d)) for i in range(d)] for v in innovations
    ]


def cvm_chi2_2(z: Sequence[Sequence[float]]) -> float:
    """Cramer-von Mises distance of squared radii from ``chi2_2``.

    Under the null ``|z|^2 ~ chi2_2``, so ``U = 1 - exp(-|z|^2/2)`` is uniform.
    """
    n = len(z)
    if n == 0:
        raise NumericalFailure("empty innovation sequence")
    u = sorted(1.0 - math.exp(-0.5 * (v[0] * v[0] + v[1] * v[1])) for v in z)
    acc = 1.0 / (12.0 * n)
    for i, ui in enumerate(u, start=1):
        acc += (ui - (2.0 * i - 1.0) / (2.0 * n)) ** 2
    return acc


def angular_harmonic_statistic(z: Sequence[Sequence[float]]) -> float:
    """Summed squared circular means at the frozen harmonics 1..4."""
    n = len(z)
    if n == 0:
        raise NumericalFailure("empty innovation sequence")
    total = 0.0
    angles = [math.atan2(v[1], v[0]) for v in z]
    for k in ANGULAR_HARMONICS:
        c = sum(math.cos(k * a) for a in angles) / n
        s = sum(math.sin(k * a) for a in angles) / n
        total += c * c + s * s
    return total


def lag_covariance_statistic(z: Sequence[Sequence[float]]) -> float:
    """Summed squared Frobenius norms of innovation lag covariances, lags 1..10."""
    n = len(z)
    d = 2
    total = 0.0
    for lag in INNOVATION_LAGS:
        if lag >= n:
            raise NumericalFailure("record too short for the frozen diagnostic lags")
        count = n - lag
        acc = nm.zeros(d, d)
        for t in range(count):
            a, b = z[t], z[t + lag]
            for i in range(d):
                for j in range(d):
                    acc[i][j] += a[i] * b[j]
        total += sum((acc[i][j] / count) ** 2 for i in range(d) for j in range(d))
    return total


def lag_antisymmetry_residuals(
    observed: Sequence[Matrix], fitted: Sequence[Matrix]
) -> float:
    """Observed-minus-fitted lag-antisymmetry residual, summed in squares.

    The free model may contain a current, so a nonzero *raw* lag asymmetry is
    not by itself a goodness-of-fit failure; only the residual against the
    fitted model enters the diagnostic family.
    """
    if len(observed) != len(fitted):
        raise NumericalFailure("observed and fitted lag sets must align")
    total = 0.0
    for o, f in zip(observed, fitted):
        diff = nm.sub(o, f)
        anti = nm.scale(nm.sub(diff, nm.transpose(diff)), 0.5)
        total += sum(v * v for row in anti for v in row)
    return total


@dataclass(frozen=True)
class NullScales:
    """Frozen null standard deviations for each diagnostic component."""

    cvm: float
    angular: float
    lagcov: float
    antisym: float
    cvm_mean: float = 0.0
    angular_mean: float = 0.0
    lagcov_mean: float = 0.0
    antisym_mean: float = 0.0

    def validate(self) -> None:
        for name in ("cvm", "angular", "lagcov", "antisym"):
            v = getattr(self, name)
            if not math.isfinite(v) or v <= 0.0:
                raise NumericalFailure(
                    f"diagnostic component {name!r} has a zero or undefined null scale; "
                    "this is a validation failure, not a dropped component"
                )


@dataclass(frozen=True)
class DiagnosticComponents:
    cvm: float
    angular: float
    lagcov: float
    antisym: float

    def scaled_max(self, scales: NullScales) -> float:
        scales.validate()
        return max(
            (self.cvm - scales.cvm_mean) / scales.cvm,
            (self.angular - scales.angular_mean) / scales.angular,
            (self.lagcov - scales.lagcov_mean) / scales.lagcov,
            (self.antisym - scales.antisym_mean) / scales.antisym,
        )


def diagnostic_components(
    innovations: Sequence[Sequence[float]],
    inn_cov: Matrix,
    observed_lags: Sequence[Matrix],
    fitted_lags: Sequence[Matrix],
) -> DiagnosticComponents:
    """Compute the four frozen diagnostic components for one record.

    The lag-antisymmetry inputs are **required**.  Previously they defaulted to
    ``None``, which silently set that component to zero and removed a frozen
    member of the family from the maximum.  Absent lag data now makes the whole
    family non-evaluable, which is the scientifically correct outcome: a
    diagnostic that was not computed is not a diagnostic that passed.
    """
    if observed_lags is None or fitted_lags is None:
        raise DiagnosticNotEvaluable(
            "observed and fitted lag matrices are required; the antisymmetry "
            "component may not default to zero"
        )
    if len(observed_lags) == 0 or len(fitted_lags) == 0:
        raise DiagnosticNotEvaluable("lag matrix sets are empty")
    if len(observed_lags) != len(fitted_lags):
        raise DiagnosticNotEvaluable(
            f"observed ({len(observed_lags)}) and fitted ({len(fitted_lags)}) "
            "lag sets do not align"
        )
    z = standardise_innovations(innovations, inn_cov)
    return DiagnosticComponents(
        cvm=cvm_chi2_2(z),
        angular=angular_harmonic_statistic(z),
        lagcov=lag_covariance_statistic(z),
        antisym=lag_antisymmetry_residuals(observed_lags, fitted_lags),
    )


# ---------------------------------------------------------------------------
# The single authoritative diagnostic-family result
# ---------------------------------------------------------------------------

DIAG_UNCALIBRATED = "UNCALIBRATED"
DIAG_CALIBRATED = "CALIBRATED"
DIAG_NOT_EVALUABLE = "NOT_EVALUABLE"
DIAG_CONTRADICTORY = "CONTRADICTORY"

#: Every component of the frozen family, in fixed order.  A family result that
#: does not account for all of them is not a family result.
REQUIRED_COMPONENTS: tuple[str, ...] = ("cvm", "angular", "lagcov", "antisym")


@dataclass(frozen=True)
class RecordDiagnostic:
    """One record's contribution to the family.

    ``rejected`` is ``None`` when the record's diagnostic was not evaluated.
    That is not ``False``: a diagnostic that was not computed is not a
    diagnostic that passed.
    """

    record: str
    components: DiagnosticComponents | None = None
    scaled_max: float | None = None
    rejected: bool | None = None
    reason: str = ""

    @property
    def evaluated(self) -> bool:
        return self.components is not None and self.rejected is not None


@dataclass(frozen=True)
class DiagnosticFamilyResult:
    """The ONE authoritative diagnostic-family decision for an experiment.

    V3 accepted a caller-supplied boolean and never compared it against the
    per-record diagnostics, so ``record.diagnostic_rejected = True`` could sit
    beside a family argument of ``False`` and still produce support.  Here the
    family decision is DERIVED from the per-record components and a calibrated
    familywise critical value; a caller-supplied claim is only ever checked
    for consistency against that derivation, never substituted for it.
    """

    status: str
    #: Familywise statistic: the maximum scaled component over all records.
    statistic: float | None = None
    #: The calibrated familywise critical value, when one exists.
    critical_value: float | None = None
    #: Identity of the calibration stream that produced the critical value.
    critical_identity: str = ""
    rejected: bool | None = None
    records: tuple[RecordDiagnostic, ...] = ()
    reason_codes: tuple[str, ...] = ()

    @property
    def usable(self) -> bool:
        """True only for a calibrated, coherent, fully populated family."""
        return self.status == DIAG_CALIBRATED and self.rejected is not None

    def as_dict(self) -> dict:
        return {
            "status": self.status,
            "statistic": self.statistic,
            "critical_value": self.critical_value,
            "critical_identity": self.critical_identity,
            "rejected": self.rejected,
            "reason_codes": list(self.reason_codes),
            "records": [
                {"record": r.record, "scaled_max": r.scaled_max,
                 "rejected": r.rejected, "reason": r.reason}
                for r in self.records
            ],
        }


def evaluate_diagnostic_family(
    records: Sequence[RecordDiagnostic],
    expected_records: Sequence[str],
    scales: NullScales | None = None,
    critical_value: float | None = None,
    critical_identity: str = "",
    claimed_rejected: bool | None = None,
) -> DiagnosticFamilyResult:
    """Derive the family decision from its required inputs.

    Order of refusal, each fail-closed:

    1. a required record contributes no diagnostic at all  -> NOT_EVALUABLE;
    2. a required component is absent or non-finite        -> NOT_EVALUABLE;
    3. no frozen null scales, or no calibrated familywise
       critical value                                      -> UNCALIBRATED;
    4. a record's own rejection disagrees with the family  -> CONTRADICTORY;
    5. otherwise                                           -> CALIBRATED.

    Only outcome 5 can take part in a supported verdict.
    """
    reasons: list[str] = []
    if not expected_records:
        return DiagnosticFamilyResult(
            DIAG_NOT_EVALUABLE, None, critical_value, critical_identity, None, (),
            ("no records were expected; any(()) is False and would read as "
             "a family that did not reject",),
        )
    by_record = {r.record: r for r in records}
    duplicates = sorted({r.record for r in records if
                         sum(1 for x in records if x.record == r.record) > 1})
    for key in duplicates:
        reasons.append(f"duplicate record diagnostic {key}")
    for key in expected_records:
        if key not in by_record:
            reasons.append(f"missing record diagnostic {key}")
    extras = sorted(k for k in by_record if k not in set(expected_records))
    for key in extras:
        reasons.append(f"unplanned record diagnostic {key}")

    ordered: list[RecordDiagnostic] = []
    for key in expected_records:
        rd = by_record.get(key)
        if rd is None:
            continue
        ordered.append(rd)
        if rd.components is None:
            reasons.append(f"record {key} supplied no diagnostic components")
            continue
        for name in REQUIRED_COMPONENTS:
            v = getattr(rd.components, name, None)
            if v is None or not math.isfinite(v):
                reasons.append(f"record {key} component {name} is absent or non-finite")

    if reasons:
        return DiagnosticFamilyResult(
            DIAG_NOT_EVALUABLE, None, critical_value, critical_identity,
            None, tuple(ordered), tuple(reasons),
        )

    if scales is None:
        reasons.append("no frozen null scales; the family statistic is not defined")
    else:
        try:
            scales.validate()
        except NumericalFailure as exc:
            reasons.append(f"null scales invalid: {exc}")
    if critical_value is None or not math.isfinite(critical_value):
        reasons.append(
            "no calibrated familywise critical value; raw components existing "
            "is not a family that passed"
        )
    if not critical_identity:
        reasons.append("familywise critical value carries no calibration identity")
    if reasons:
        return DiagnosticFamilyResult(
            DIAG_UNCALIBRATED, None, critical_value, critical_identity,
            None, tuple(ordered), tuple(reasons),
        )

    assert scales is not None and critical_value is not None
    per_record: list[RecordDiagnostic] = []
    stat = -math.inf
    for rd in ordered:
        assert rd.components is not None
        sm = rd.components.scaled_max(scales)
        if not math.isfinite(sm):
            return DiagnosticFamilyResult(
                DIAG_NOT_EVALUABLE, None, critical_value, critical_identity,
                None, tuple(ordered),
                (f"record {rd.record} scaled maximum is not finite",),
            )
        stat = max(stat, sm)
        derived = sm > critical_value
        if rd.rejected is not None and rd.rejected != derived:
            reasons.append(
                f"record {rd.record} claims rejected={rd.rejected} but its "
                f"components give {derived}"
            )
        per_record.append(RecordDiagnostic(rd.record, rd.components, sm, derived, rd.reason))

    if not per_record:
        return DiagnosticFamilyResult(
            DIAG_NOT_EVALUABLE, None, critical_value, critical_identity, None, (),
            ("no record contributed a component to the family",),
        )
    family_rejected = any(r.rejected for r in per_record)
    if claimed_rejected is not None and claimed_rejected != family_rejected:
        reasons.append(
            f"caller claims family_rejected={claimed_rejected} but the record "
            f"components give {family_rejected}"
        )
    if reasons:
        return DiagnosticFamilyResult(
            DIAG_CONTRADICTORY, stat, critical_value, critical_identity,
            None, tuple(per_record), tuple(reasons),
        )
    return DiagnosticFamilyResult(
        DIAG_CALIBRATED, stat, critical_value, critical_identity,
        family_rejected, tuple(per_record), (),
    )
