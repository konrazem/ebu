"""Preregistered V-stage validation case list.

Every case is declared here, before any outcome is inspected.  The required
replicate counts are the T-stage section 20.3 values; the smoke-sample counts
used when the full campaign is computationally infeasible are recorded
separately and are never substituted silently.
"""

from __future__ import annotations

from ..packets import ValidationCase
from ..seeds import CALIBRATION, CONTROL, DIAGNOSTIC, POWER, SIZE

#: T-stage required replicate counts.
REQUIRED_SIZE_REPLICATES = 5000
REQUIRED_DIAGNOSTIC_REPLICATES = 5000
REQUIRED_POWER_REPLICATES = 2000
#: Release criteria.
SIZE_TARGET = 0.025
DIAGNOSTIC_TARGET = 0.005
POWER_TARGET = 0.90


def _c(case_id, purpose, family, ns, reps, expectation, **detail):
    return ValidationCase(case_id, purpose, family, ns, reps, expectation, detail)


#: Finite-N critical-value calibration.
CALIBRATION_CASES = (
    _c("CAL-SCALE-01", "Calibrate c_minus/c_plus for the absolute log-beta interval",
       "calibration", CALIBRATION, 4000, "c_minus, c_plus <= 2.10", statistic="studentised log beta"),
    _c("CAL-CONTRAST-01", "Calibrate the within-block contrast critical values",
       "calibration", CALIBRATION, 4000, "c_minus, c_plus <= 2.10", statistic="contrast"),
    _c("CAL-SHAPE-01", "Calibrate the T4 geometry upper-limit radius",
       "calibration", CALIBRATION, 4000, "radius finite at the zero-distance boundary", statistic="G"),
    _c("CAL-CENTRE-01", "Calibrate the centre upper-limit radius",
       "calibration", CALIBRATION, 4000, "radius finite", statistic="m"),
    _c("CAL-STAT-01", "Calibrate the four-quarter stationarity upper limit",
       "calibration", CALIBRATION, 4000, "radius finite", statistic="stationarity max"),
    _c("CAL-CURRENT-01", "Calibrate the r_irr upper-limit radius at omega = 0",
       "calibration", CALIBRATION, 4000, "radius finite at the nonregular boundary", statistic="r_irr"),
    _c("CAL-DIAG-01", "Calibrate the joint diagnostic maximum and its null scales",
       "calibration", CALIBRATION, 4000, "all four null scales strictly positive", statistic="diagnostic max"),
)

#: False-equivalence size validation at the required boundary nulls.
SIZE_CASES = (
    _c("SIZE-ABS-LO", "Absolute equivalence at the lower boundary b = -log(1.05)",
       "size", SIZE, REQUIRED_SIZE_REPLICATES, "CP upper <= 0.025", b_true=-0.04879016416943205),
    _c("SIZE-ABS-HI", "Absolute equivalence at the upper boundary b = +log(1.05)",
       "size", SIZE, REQUIRED_SIZE_REPLICATES, "CP upper <= 0.025", b_true=0.04879016416943205),
    _c("SIZE-CON-LO", "Cross-field contrast at the lower boundary -log(1.02)",
       "size", SIZE, REQUIRED_SIZE_REPLICATES, "CP upper <= 0.025", contrast=-0.01980262729617973),
    _c("SIZE-CON-HI", "Cross-field contrast at the upper boundary +log(1.02)",
       "size", SIZE, REQUIRED_SIZE_REPLICATES, "CP upper <= 0.025", contrast=0.01980262729617973),
    _c("SIZE-SHAPE-BD", "Geometry upper limit at the shape boundary G = log(1.05)",
       "size", SIZE, REQUIRED_SIZE_REPLICATES, "CP upper <= 0.025", g_true=0.04879016416943205),
    _c("SIZE-CENTRE-BD", "Centre upper limit at the boundary m = 0.10",
       "size", SIZE, REQUIRED_SIZE_REPLICATES, "CP upper <= 0.025", m_true=0.10),
    _c("SIZE-CURRENT-BD", "Current upper limit at the boundary r_irr = 0.02",
       "size", SIZE, REQUIRED_SIZE_REPLICATES, "CP upper <= 0.025", r_irr_true=0.02),
    _c("SIZE-NUIS-NOISE", "Absolute boundary at the top of the qualified noise range",
       "size", SIZE, REQUIRED_SIZE_REPLICATES, "CP upper <= 0.025", noise_ratio=0.05),
    _c("SIZE-NUIS-EXP", "Absolute boundary at the exposure ceiling",
       "size", SIZE, REQUIRED_SIZE_REPLICATES, "CP upper <= 0.025", exposure_fraction=0.1),
    _c("SIZE-NUIS-COND", "Absolute boundary near the conditioning limit kappa_2 = 100",
       "size", SIZE, REQUIRED_SIZE_REPLICATES, "CP upper <= 0.025", condition=100.0),
    _c("SIZE-NUIS-CAL", "Absolute boundary with the full qualified calibration covariance",
       "size", SIZE, REQUIRED_SIZE_REPLICATES, "CP upper <= 0.025", sigma_cal=0.009),
)

#: Diagnostic-family false-rejection validation.
DIAGNOSTIC_CASES = (
    _c("DIAG-NULL-NOM", "Diagnostic familywise size at the nominal true benchmark",
       "diagnostic", DIAGNOSTIC, REQUIRED_DIAGNOSTIC_REPLICATES, "CP upper <= 0.005"),
    _c("DIAG-NULL-EXP", "Diagnostic familywise size at the exposure ceiling",
       "diagnostic", DIAGNOSTIC, REQUIRED_DIAGNOSTIC_REPLICATES, "CP upper <= 0.005",
       exposure_fraction=0.1),
    _c("DIAG-NULL-COND", "Diagnostic familywise size near the conditioning limit",
       "diagnostic", DIAGNOSTIC, REQUIRED_DIAGNOSTIC_REPLICATES, "CP upper <= 0.005",
       condition=100.0),
)

#: Complete true-bridge power.
POWER_CASES = (
    _c("POWER-NOMINAL", "Complete eight-record success at the nominal true benchmark",
       "power", POWER, REQUIRED_POWER_REPLICATES, "CP lower >= 0.90"),
    _c("POWER-CONDLIM", "Complete success near the conditioning limit",
       "power", POWER, REQUIRED_POWER_REPLICATES, "CP lower >= 0.90", condition=100.0),
    _c("POWER-NOISEHI", "Complete success at the top of the qualified noise range",
       "power", POWER, REQUIRED_POWER_REPLICATES, "CP lower >= 0.90", noise_ratio=0.05),
)

#: Negative and architecture controls (T-stage section 20.4, V brief 62-75).
CONTROL_CASES = (
    _c("CTL-BLIND-107", "Hidden A scale c = 1.07; expect beta_blinded = beta/c",
       "control", CONTROL, 200, "recovered log beta matches after multiplying by c", c=1.07),
    _c("CTL-BLIND-090", "Hidden A scale c = 0.90; expect beta_blinded = beta/c",
       "control", CONTROL, 200, "recovered log beta matches after multiplying by c", c=0.90),
    _c("CTL-COMMON-07", "Common wrong scale beta = 0.7 in every field",
       "control", CONTROL, 200, "cross-field contrasts may pass; absolute must fail", beta=0.7),
    _c("CTL-FIELD-106", "Field-specific alternative (1, 1.06, 1, 1)",
       "control", CONTROL, 200, "false support bounded", betas=(1.0, 1.06, 1.0, 1.0)),
    _c("CTL-FIELD-MIX", "Field-specific alternative (1, 0.93, 1.05, 1)",
       "control", CONTROL, 200, "false support bounded", betas=(1.0, 0.93, 1.05, 1.0)),
    _c("CTL-FIELD-110", "Field-specific alternative (1, 1, 1, 1.10)",
       "control", CONTROL, 200, "false support bounded", betas=(1.0, 1.0, 1.0, 1.10)),
    _c("CTL-HARD-025", "Hard 2.5% single-field contrast",
       "control", CONTROL, 200, "false support bounded", contrast=0.025),
    _c("CTL-GEOM-TRACE", "Trace-preserving wrong geometry",
       "control", CONTROL, 200, "scalar beta plausible; T4 geometry rejects"),
    _c("CTL-GEOM-ROT", "Correct eigenvalues, wrong orientation",
       "control", CONTROL, 200, "geometry detects the rotation"),
    _c("CTL-CURRENT", "Current-preserving Gaussian, A = I + omega J",
       "control", CONTROL, 200, "density/geometry pass; current gate blocks support", omega=0.05),
    _c("CTL-ETA-T-COV", "Omitted eta/T covariance versus the correct shared covariance",
       "control", CONTROL, 200, "coverage consequence detected"),
    _c("CTL-NOISE-HI", "Localisation noise above the qualified ratio",
       "control", CONTROL, 200, "diagnose, refuse or lose support", noise_model="inflated"),
    _c("CTL-NOISE-HEAVY", "Non-Gaussian heavy-tailed localisation noise",
       "control", CONTROL, 200, "diagnose, refuse or lose support", noise_model="heavy"),
    _c("CTL-NOISE-COLOR", "Coloured localisation noise",
       "control", CONTROL, 200, "diagnose, refuse or lose support", noise_model="colored"),
    _c("CTL-NOISE-STATE", "State-dependent localisation noise",
       "control", CONTROL, 200, "diagnose, refuse or lose support", noise_model="state_dependent"),
    _c("CTL-BLUR-MISMATCH", "Generator exposure differs from the analysed shutter model",
       "control", CONTROL, 200, "diagnose, refuse or lose support"),
    _c("CTL-DRIFT", "Slow centre drift during the record",
       "control", CONTROL, 200, "stationarity or diagnostics prevent full support"),
    _c("CTL-SELECTION", "Clipping / tracking selection of observations",
       "control", CONTROL, 200, "invalid measurement or model, not a reconditioned pass"),
    _c("CTL-AXIAL-COUPLE", "3D stiffness with K_qz != 0; plane block would bias",
       "control", CONTROL, 1, "pipeline uses H_eff; K_qq bias quantified"),
    _c("CTL-AXIAL-MEMORY", "Lateral density matches Schur but the 2D temporal model fails",
       "control", CONTROL, 200, "TEMPORAL_MODEL_UNQUALIFIED or model failure"),
    _c("CTL-RF-TEMP-304", "Realized temperature 304 K",
       "control", CONTROL, 1, "FIELD_REALIZATION_OUT_OF_SPEC"),
    _c("CTL-RF-STIFF-1021", "Realized stiffness 1.021-fold",
       "control", CONTROL, 1, "FIELD_REALIZATION_OUT_OF_SPEC"),
    _c("CTL-RF-MODES", "One weak and one strong stiffness mode",
       "control", CONTROL, 1, "FIELD_REALIZATION_OUT_OF_SPEC"),
    _c("CTL-RF-ELLIPSE", "Unrotated target-eigenvalue ellipse",
       "control", CONTROL, 1, "FIELD_REALIZATION_OUT_OF_SPEC"),
    _c("CTL-RF-STRADDLE", "Uncertainty region straddling a realization boundary",
       "control", CONTROL, 1, "FIELD_REALIZATION_UNRESOLVED"),
    _c("CTL-RF-VALID", "Nominal-like realized field",
       "control", CONTROL, 1, "FIELD_REALIZATION_VALID (synthetic)"),
    _c("CTL-OPT-FAIL", "Forced optimiser failure modes",
       "control", CONTROL, 1, "COMPUTATION_NOT_EVALUABLE; beta never fabricated"),
)

ALL_CASES = (
    CALIBRATION_CASES + SIZE_CASES + DIAGNOSTIC_CASES + POWER_CASES + CONTROL_CASES
)


def required_replicate_total() -> int:
    return sum(c.replicates for c in ALL_CASES)
