"""Preregistered V-stage validation case list, typed.

Every case is declared here, before any outcome is inspected.  The required
replicate counts are the T-stage section 20.3 values; the smoke-sample counts
used when the full campaign is computationally infeasible are recorded
separately and are never substituted silently.

V4 types the case detail.  Under V3 a case carried a free-form
``detail`` dictionary, and the runner read whichever keys it happened to know
about: ``POWER-CONDLIM``'s ``condition`` and ``POWER-NOISEHI``'s
``noise_ratio`` were never read at all, so both ran the nominal world under a
non-nominal name, and ``CTL-CURRENT`` still carried the obsolete dimensional
``omega`` that the repaired constructor no longer accepts.  Here the detail is
a :class:`CaseConfig` whose fields the dispatcher must consume explicitly, and
:func:`declared_fields` makes an unconsumed declaration detectable.
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from enum import Enum
from typing import Any, Mapping, Sequence

from ..seeds import CALIBRATION, CONTROL, DIAGNOSTIC, POWER, SIZE

#: T-stage required replicate counts.
REQUIRED_SIZE_REPLICATES = 5000
REQUIRED_DIAGNOSTIC_REPLICATES = 5000
REQUIRED_POWER_REPLICATES = 2000
#: Release criteria.
SIZE_TARGET = 0.025
DIAGNOSTIC_TARGET = 0.005
POWER_TARGET = 0.90


class ExpectedEvent(str, Enum):
    """What a case's declared outcome actually is.

    Each is evaluated by the ONE versioned event evaluator in
    :mod:`e1a_v5.validation.events`.  A case whose outcome is complete
    scientific support uses the authoritative pipeline verdict and nothing
    else; V3's control runner rebuilt a four-statistic predicate of its own.
    """

    #: The authoritative verdict is SUPPORTED_WITHIN_DECLARED_TOLERANCES.
    COMPLETE_SUPPORT = "complete_support"
    #: A false equivalence at a boundary null: the absolute interval is
    #: contained when the truth sits exactly on the margin.
    FALSE_EQUIVALENCE = "false_equivalence"
    #: The diagnostic family rejects at least one record.
    DIAGNOSTIC_REJECTION = "diagnostic_family_rejection"
    #: The authoritative verdict is DISCREPANCY_ESTABLISHED.
    DISCREPANCY = "discrepancy_established"
    #: The authoritative verdict is INVALID_MEASUREMENT_OR_MODEL.
    INVALID = "invalid_measurement_or_model"
    #: The authoritative verdict is COMPUTATION_NOT_EVALUABLE.
    NOT_EVALUABLE = "computation_not_evaluable"
    #: A specific structured refusal code appears.
    REFUSAL_CODE = "specific_refusal_code"
    #: A specific realized-field qualification status.
    REALIZATION_STATUS = "realized_field_status"
    #: A recovery check: the blinded estimate returns to truth when unblinded.
    BLINDED_RECOVERY = "blinded_recovery"
    #: A calibration quantity is produced; there is no pass/fail event.
    CALIBRATION_OUTPUT = "calibration_output"
    #: Exercised by the exact deterministic control battery, not by sampling.
    DETERMINISTIC = "deterministic_control"


@dataclass(frozen=True)
class CaseConfig:
    """The typed world a validation case declares.

    Every field that is not ``None`` is a declaration the dispatcher MUST
    consume.  :func:`declared_fields` lists them, and the meta-test in the
    V4 suite fails if the generated configuration does not record every one.
    """

    #: True absolute log beta for a single-record size driver.
    b_true: float | None = None
    #: True within-block contrast for a contrast size driver.
    contrast_true: float | None = None
    #: True common beta applied to every field.
    beta_common: float | None = None
    #: True per-field betas, in field order (theta0..theta3).
    betas: tuple[float, float, float, float] | None = None
    #: Hidden Branch-A scale factor c; the analysis sees H_A * c.
    blind_scale: float | None = None
    #: Target instantaneous localisation variance ratio (T.23 ceiling 0.05).
    noise_ratio: float | None = None
    #: Exposure as a fraction of the fast relaxation time (ceiling 0.1).
    exposure_fraction: float | None = None
    #: Target spectral condition number of H_eff.
    condition: float | None = None
    #: Target dimensionless irreversibility ratio r_irr.
    r_irr_target: float | None = None
    #: Lateral-axial coupling as a fraction of the lateral reference.
    axial_coupling: float | None = None
    #: Geometry perturbation: "trace_preserving" or "rotation".
    geometry: str | None = None
    #: Non-Gaussian / coloured / state-dependent observation noise.
    noise_model: str | None = None
    #: Generator exposure differs from the analysed shutter model.
    blur_mismatch: float | None = None
    #: Slow centre drift, m/s, during the record.
    drift_rate: tuple[float, float] | None = None
    #: Clipping / tracking selection of observations.
    selection: str | None = None
    #: Declared calibration standard uncertainty for the absolute endpoint.
    sigma_cal: float | None = None
    #: True geometry / centre / current values for gate-boundary size cases.
    g_true: float | None = None
    m_true: float | None = None
    r_irr_true: float | None = None
    #: Realized-field control target, for the deterministic T11a battery.
    realization: str | None = None
    #: Forced optimiser failure mode.
    optimiser_failure: str | None = None
    #: Omitted eta/T covariance control.
    omit_eta_t_covariance: bool | None = None
    #: Statistic being calibrated, for the calibration family.
    statistic: str | None = None

    def declared_fields(self) -> tuple[str, ...]:
        """Names of every field this case actually sets."""
        return tuple(
            f.name for f in fields(self) if getattr(self, f.name) is not None
        )

    def as_dict(self) -> dict[str, Any]:
        return {n: getattr(self, n) for n in self.declared_fields()}


@dataclass(frozen=True)
class ValidationCaseV4:
    """A preregistered V-stage validation case with a typed world and event."""

    case_id: str
    purpose: str
    #: "calibration", "size", "diagnostic", "power", "control".
    family: str
    seed_namespace: str
    replicates: int
    expectation: str
    expected_event: ExpectedEvent
    config: CaseConfig = field(default_factory=CaseConfig)
    #: For REFUSAL_CODE / REALIZATION_STATUS events, the exact value required.
    event_target: str | None = None

    @property
    def detail(self) -> dict[str, Any]:
        return self.config.as_dict()


def _c(case_id, purpose, family, ns, reps, expectation, event, target=None, **cfg):
    return ValidationCaseV4(
        case_id, purpose, family, ns, reps, expectation, event,
        CaseConfig(**cfg), target,
    )


E = ExpectedEvent

#: Finite-N critical-value calibration.
CALIBRATION_CASES = (
    _c("CAL-SCALE-01", "Calibrate c_minus/c_plus for the absolute log-beta interval",
       "calibration", CALIBRATION, 4000, "c_minus, c_plus <= 2.10",
       E.CALIBRATION_OUTPUT, statistic="studentised log beta"),
    _c("CAL-CONTRAST-01", "Calibrate the within-block contrast critical values",
       "calibration", CALIBRATION, 4000, "c_minus, c_plus <= 2.10",
       E.CALIBRATION_OUTPUT, statistic="contrast"),
    _c("CAL-SHAPE-01", "Calibrate the T4 geometry upper-limit radius",
       "calibration", CALIBRATION, 4000, "radius finite at the zero-distance boundary",
       E.CALIBRATION_OUTPUT, statistic="G"),
    _c("CAL-CENTRE-01", "Calibrate the centre upper-limit radius",
       "calibration", CALIBRATION, 4000, "radius finite",
       E.CALIBRATION_OUTPUT, statistic="m"),
    _c("CAL-STAT-01", "Calibrate the four-quarter stationarity upper limit",
       "calibration", CALIBRATION, 4000, "radius finite",
       E.CALIBRATION_OUTPUT, statistic="stationarity max"),
    _c("CAL-CURRENT-01", "Calibrate the r_irr upper-limit radius at omega = 0",
       "calibration", CALIBRATION, 4000, "radius finite at the nonregular boundary",
       E.CALIBRATION_OUTPUT, statistic="r_irr"),
    _c("CAL-DIAG-01", "Calibrate the joint diagnostic maximum and its null scales",
       "calibration", CALIBRATION, 4000, "all four null scales strictly positive",
       E.CALIBRATION_OUTPUT, statistic="diagnostic max"),
)

#: False-equivalence size validation at the required boundary nulls.
SIZE_CASES = (
    _c("SIZE-ABS-LO", "Absolute equivalence at the lower boundary b = -log(1.05)",
       "size", SIZE, REQUIRED_SIZE_REPLICATES, "CP upper <= 0.025",
       E.FALSE_EQUIVALENCE, b_true=-0.04879016416943205),
    _c("SIZE-ABS-HI", "Absolute equivalence at the upper boundary b = +log(1.05)",
       "size", SIZE, REQUIRED_SIZE_REPLICATES, "CP upper <= 0.025",
       E.FALSE_EQUIVALENCE, b_true=0.04879016416943205),
    _c("SIZE-CON-LO", "Cross-field contrast at the lower boundary -log(1.02)",
       "size", SIZE, REQUIRED_SIZE_REPLICATES, "CP upper <= 0.025",
       E.FALSE_EQUIVALENCE, contrast_true=-0.01980262729617973),
    _c("SIZE-CON-HI", "Cross-field contrast at the upper boundary +log(1.02)",
       "size", SIZE, REQUIRED_SIZE_REPLICATES, "CP upper <= 0.025",
       E.FALSE_EQUIVALENCE, contrast_true=0.01980262729617973),
    _c("SIZE-SHAPE-BD", "Geometry upper limit at the shape boundary G = log(1.05)",
       "size", SIZE, REQUIRED_SIZE_REPLICATES, "CP upper <= 0.025",
       E.FALSE_EQUIVALENCE, g_true=0.04879016416943205),
    _c("SIZE-CENTRE-BD", "Centre upper limit at the boundary m = 0.10",
       "size", SIZE, REQUIRED_SIZE_REPLICATES, "CP upper <= 0.025",
       E.FALSE_EQUIVALENCE, m_true=0.10),
    _c("SIZE-CURRENT-BD", "Current upper limit at the boundary r_irr = 0.02",
       "size", SIZE, REQUIRED_SIZE_REPLICATES, "CP upper <= 0.025",
       E.FALSE_EQUIVALENCE, r_irr_true=0.02),
    _c("SIZE-NUIS-NOISE", "Absolute boundary at the top of the qualified noise range",
       "size", SIZE, REQUIRED_SIZE_REPLICATES, "CP upper <= 0.025",
       E.FALSE_EQUIVALENCE, b_true=0.04879016416943205, noise_ratio=0.05),
    _c("SIZE-NUIS-EXP", "Absolute boundary at the exposure ceiling",
       "size", SIZE, REQUIRED_SIZE_REPLICATES, "CP upper <= 0.025",
       E.FALSE_EQUIVALENCE, b_true=0.04879016416943205, exposure_fraction=0.1),
    _c("SIZE-NUIS-COND", "Absolute boundary near the conditioning limit kappa_2 = 100",
       "size", SIZE, REQUIRED_SIZE_REPLICATES, "CP upper <= 0.025",
       E.FALSE_EQUIVALENCE, b_true=0.04879016416943205, condition=100.0),
    _c("SIZE-NUIS-CAL", "Absolute boundary with the full qualified calibration covariance",
       "size", SIZE, REQUIRED_SIZE_REPLICATES, "CP upper <= 0.025",
       E.FALSE_EQUIVALENCE, b_true=0.04879016416943205, sigma_cal=0.009),
)

#: Diagnostic-family false-rejection validation.
DIAGNOSTIC_CASES = (
    _c("DIAG-NULL-NOM", "Diagnostic familywise size at the nominal true benchmark",
       "diagnostic", DIAGNOSTIC, REQUIRED_DIAGNOSTIC_REPLICATES, "CP upper <= 0.005",
       E.DIAGNOSTIC_REJECTION),
    _c("DIAG-NULL-EXP", "Diagnostic familywise size at the exposure ceiling",
       "diagnostic", DIAGNOSTIC, REQUIRED_DIAGNOSTIC_REPLICATES, "CP upper <= 0.005",
       E.DIAGNOSTIC_REJECTION, exposure_fraction=0.1),
    _c("DIAG-NULL-COND", "Diagnostic familywise size near the conditioning limit",
       "diagnostic", DIAGNOSTIC, REQUIRED_DIAGNOSTIC_REPLICATES, "CP upper <= 0.005",
       E.DIAGNOSTIC_REJECTION, condition=100.0),
)

#: Complete true-bridge power.
POWER_CASES = (
    _c("POWER-NOMINAL", "Complete eight-record success at the nominal true benchmark",
       "power", POWER, REQUIRED_POWER_REPLICATES, "CP lower >= 0.90",
       E.COMPLETE_SUPPORT),
    _c("POWER-CONDLIM", "Complete success near the conditioning limit",
       "power", POWER, REQUIRED_POWER_REPLICATES, "CP lower >= 0.90",
       E.COMPLETE_SUPPORT, condition=100.0),
    _c("POWER-NOISEHI", "Complete success at the top of the qualified noise range",
       "power", POWER, REQUIRED_POWER_REPLICATES, "CP lower >= 0.90",
       E.COMPLETE_SUPPORT, noise_ratio=0.05),
)

#: Negative and architecture controls (T-stage section 20.4, V brief 62-75).
CONTROL_CASES = (
    _c("CTL-BLIND-107", "Hidden A scale c = 1.07; expect beta_blinded = beta/c",
       "control", CONTROL, 200, "recovered log beta matches after multiplying by c",
       E.BLINDED_RECOVERY, blind_scale=1.07),
    _c("CTL-BLIND-090", "Hidden A scale c = 0.90; expect beta_blinded = beta/c",
       "control", CONTROL, 200, "recovered log beta matches after multiplying by c",
       E.BLINDED_RECOVERY, blind_scale=0.90),
    _c("CTL-COMMON-07", "Common wrong scale beta = 0.7 in every field",
       "control", CONTROL, 200, "cross-field contrasts may pass; absolute must fail",
       E.COMPLETE_SUPPORT, beta_common=0.7),
    _c("CTL-FIELD-106", "Field-specific alternative (1, 1.06, 1, 1)",
       "control", CONTROL, 200, "false support bounded",
       E.COMPLETE_SUPPORT, betas=(1.0, 1.06, 1.0, 1.0)),
    _c("CTL-FIELD-MIX", "Field-specific alternative (1, 0.93, 1.05, 1)",
       "control", CONTROL, 200, "false support bounded",
       E.COMPLETE_SUPPORT, betas=(1.0, 0.93, 1.05, 1.0)),
    _c("CTL-FIELD-110", "Field-specific alternative (1, 1, 1, 1.10)",
       "control", CONTROL, 200, "false support bounded",
       E.COMPLETE_SUPPORT, betas=(1.0, 1.0, 1.0, 1.10)),
    _c("CTL-HARD-025", "Hard 2.5% single-field contrast",
       "control", CONTROL, 200, "false support bounded",
       E.COMPLETE_SUPPORT, betas=(1.0, 1.025, 1.0, 1.0)),
    _c("CTL-GEOM-TRACE", "Trace-preserving wrong geometry",
       "control", CONTROL, 200, "scalar beta plausible; T4 geometry rejects",
       E.COMPLETE_SUPPORT, geometry="trace_preserving"),
    _c("CTL-GEOM-ROT", "Correct eigenvalues, wrong orientation",
       "control", CONTROL, 200, "geometry detects the rotation",
       E.COMPLETE_SUPPORT, geometry="rotation"),
    _c("CTL-CURRENT", "Current-preserving Gaussian, A Sigma = D + omega J",
       "control", CONTROL, 200, "density/geometry pass; current gate blocks support",
       E.COMPLETE_SUPPORT, r_irr_target=0.05),
    # Exact, not sampled: this control compares two COVARIANCE PROPAGATIONS of
    # the same primitives, so no generated world distinguishes them.  Declaring
    # it as a stochastic support case made it a no-op that ran nominal records
    # under a non-nominal name -- the defect-6 pattern.
    _c("CTL-ETA-T-COV", "Omitted eta/T covariance versus the correct shared covariance",
       "control", CONTROL, 1, "coverage consequence detected",
       E.DETERMINISTIC, omit_eta_t_covariance=True),
    _c("CTL-NOISE-HI", "Localisation noise above the qualified ratio",
       "control", CONTROL, 200, "diagnose, refuse or lose support",
       E.COMPLETE_SUPPORT, noise_ratio=0.25),
    _c("CTL-NOISE-HEAVY", "Non-Gaussian heavy-tailed localisation noise",
       "control", CONTROL, 200, "diagnose, refuse or lose support",
       E.COMPLETE_SUPPORT, noise_model="heavy"),
    _c("CTL-NOISE-COLOR", "Coloured localisation noise",
       "control", CONTROL, 200, "diagnose, refuse or lose support",
       E.COMPLETE_SUPPORT, noise_model="colored"),
    _c("CTL-NOISE-STATE", "State-dependent localisation noise",
       "control", CONTROL, 200, "diagnose, refuse or lose support",
       E.COMPLETE_SUPPORT, noise_model="state_dependent"),
    _c("CTL-BLUR-MISMATCH", "Generator exposure differs from the analysed shutter model",
       "control", CONTROL, 200, "diagnose, refuse or lose support",
       E.COMPLETE_SUPPORT, blur_mismatch=0.9),
    _c("CTL-DRIFT", "Slow centre drift during the record",
       "control", CONTROL, 200, "stationarity or diagnostics prevent full support",
       E.COMPLETE_SUPPORT, drift_rate=(2.0e-7, 0.0)),
    _c("CTL-SELECTION", "Clipping / tracking selection of observations",
       "control", CONTROL, 200, "invalid measurement or model, not a reconditioned pass",
       E.COMPLETE_SUPPORT, selection="clipping"),
    _c("CTL-AXIAL-COUPLE", "3D stiffness with K_qz != 0; plane block would bias",
       "control", CONTROL, 1, "pipeline uses H_eff; K_qq bias quantified",
       E.DETERMINISTIC, axial_coupling=0.30),
    _c("CTL-AXIAL-MEMORY", "Lateral density matches Schur but the 2D temporal model fails",
       "control", CONTROL, 1, "TEMPORAL_MODEL_UNQUALIFIED or model failure",
       E.DETERMINISTIC, realization="axial_temporal_unqualified"),
    _c("CTL-RF-TEMP-304", "Realized temperature 304 K",
       "control", CONTROL, 1, "FIELD_REALIZATION_OUT_OF_SPEC",
       E.REALIZATION_STATUS, "OUT_OF_SPEC", realization="temperature_304"),
    _c("CTL-RF-STIFF-1021", "Realized stiffness 1.021-fold",
       "control", CONTROL, 1, "FIELD_REALIZATION_OUT_OF_SPEC",
       E.REALIZATION_STATUS, "OUT_OF_SPEC", realization="stiffness_1021"),
    _c("CTL-RF-MODES", "One weak and one strong stiffness mode",
       "control", CONTROL, 1, "FIELD_REALIZATION_OUT_OF_SPEC",
       E.REALIZATION_STATUS, "OUT_OF_SPEC", realization="split_modes"),
    _c("CTL-RF-ELLIPSE", "Unrotated target-eigenvalue ellipse",
       "control", CONTROL, 1, "FIELD_REALIZATION_OUT_OF_SPEC",
       E.REALIZATION_STATUS, "OUT_OF_SPEC", realization="unrotated_ellipse"),
    _c("CTL-RF-STRADDLE", "Uncertainty region straddling a realization boundary",
       "control", CONTROL, 1, "FIELD_REALIZATION_UNRESOLVED",
       E.REALIZATION_STATUS, "UNRESOLVED", realization="straddle"),
    _c("CTL-RF-VALID", "Nominal-like realized field",
       "control", CONTROL, 1, "FIELD_REALIZATION_VALID (synthetic)",
       E.REALIZATION_STATUS, "VALID", realization="nominal"),
    _c("CTL-OPT-FAIL", "Forced optimiser failure modes",
       "control", CONTROL, 1, "COMPUTATION_NOT_EVALUABLE; beta never fabricated",
       E.DETERMINISTIC, optimiser_failure="nan_inf_singular_budget"),
)

ALL_CASES: tuple[ValidationCaseV4, ...] = (
    CALIBRATION_CASES + SIZE_CASES + DIAGNOSTIC_CASES + POWER_CASES + CONTROL_CASES
)

CASES_BY_ID: Mapping[str, ValidationCaseV4] = {c.case_id: c for c in ALL_CASES}


def case(case_id: str) -> ValidationCaseV4:
    if case_id not in CASES_BY_ID:
        raise KeyError(f"unknown validation case {case_id!r}")
    return CASES_BY_ID[case_id]


def required_replicate_total() -> int:
    return sum(c.replicates for c in ALL_CASES)
