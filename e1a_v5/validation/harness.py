"""V-stage validation harness: Layers N and O.

Runs generation, estimation, gating and verdict for single records and for
complete eight-record experiments, and aggregates Clopper-Pearson bounds.

The harness carries an explicit ``mode``: ``"full"`` uses the T-stage required
replicate counts, ``"smoke"`` uses the reduced engineering counts in
:mod:`plan`.  A smoke run is labelled in every artefact it produces and can
never yield RELEASE.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable, Mapping, Sequence

from .. import numerics as nm
from ..confidence import (
    CriticalValues,
    DELTA_A,
    DELTA_C,
    Interval,
    build_interval,
    calibrated_upper_limit,
)
from ..diagnostics import (
    DiagnosticComponents, DiagnosticNotEvaluable, NullScales,
    diagnostic_components, required_antisymmetry_lags,
)
from ..gates import (
    lag_covariance,
    DELTA_G,
    DELTA_M,
    DELTA_R_IRR,
    N_QUARTERS,
    centre_statistic,
    geometry_statistic,
    stationarity_statistic,
)
from ..generate import GeneratorSpec, generate_record
from ..numerics import NumericalFailure, clopper_pearson_lower, clopper_pearson_upper
from ..optimize import OptimizerFailure
from ..estimate import fit_record
from ..packets import ValidationResult
from ..observation import (
    BANDWIDTH_CEILING, bandwidth_product, build_state_space,
    effective_noise_to_signal, localization_ratio, model_lag_covariance,
)
from ..calibration import (
    ExperimentCalibration,
    FieldModel,
    Primitive,
    PrimitiveVector,
    Scope,
    build_experiment_calibration,
)
from ..packets import RECORDS
from ..reduction import (
    AxialEvidence,
    normalise_remainder,
    reduce_axial,
    remainder_impacts,
    schur_complement,
    schur_nonlinear_remainder,
    split_3d,
)
from ..units import K_B
from ..refusals import (
    COMPUTATION_NOT_EVALUABLE, INSUFFICIENT_GEOMETRY_CALIBRATION,
    NUMERICAL_REPRESENTATION_FAILURE, OBSERVATION_MODEL_UNQUALIFIED,
    Refusal, refuse,
)
from ..rng import Stream
from ..seeds import SeedMap
from . import plan


def current_control_drift(d_mat, sigma, r_target: float) -> float:
    """Antisymmetric coefficient ``omega`` achieving a target ``r_irr``.

    Constructed from the DIMENSIONLESS target, not from a hard-coded angular
    rate.  With ``A = (D + Q) Sigma^{-1}`` and ``Q = omega J`` the whitened
    parts are ``S = Sigma^{-1/2} D Sigma^{-1/2}`` and
    ``Omega = omega Sigma^{-1/2} J Sigma^{-1/2}``, so

        r_irr = |omega| * ||Sigma^{-1/2} J Sigma^{-1/2}||_op / lambda_min(S)

    and ``omega`` follows exactly.  It therefore scales with the actual
    dissipative rate: supplying a literal ``omega = 0.05`` against a physical
    relaxation rate of order 1e4 s^-1, as V2 did, produced ``r_irr ~ 1e11``
    and a bandwidth product of ~1.5e10.
    """
    if r_target == 0.0:
        return 0.0
    if r_target < 0.0:
        raise NumericalFailure("r_irr target must be nonnegative")
    w = nm.inv_sqrtm_spd(sigma)
    s_mat = nm.symmetrise(nm.matmul(nm.matmul(w, d_mat), w))
    vals, _ = nm.eigh(s_mat)
    lam_min = min(vals)
    if lam_min <= 0.0:
        raise NumericalFailure("whitened dissipative part is not positive definite")
    j_mat = nm.mat([[0.0, -1.0], [1.0, 0.0]])
    unit = nm.matmul(nm.matmul(w, j_mat), w)
    scale_op = nm.op_norm(unit)
    if scale_op <= 0.0:
        raise NumericalFailure("whitened antisymmetric generator has zero norm")
    return r_target * lam_min / scale_op


def solve_r_obs(a_drift, sigma, dt, t_exp, target):
    """Isotropic ``R_obs`` achieving a given instantaneous localisation ratio.

    For isotropic ``R_obs = c I`` the whitened ratio is
    ``c * lambda_max(Sigma^{-1})``, exactly linear in ``c``, so one probe
    determines the scale with no iteration.
    """
    probe = nm.scale(nm.eye(2), sigma[0][0])
    achieved = localization_ratio(sigma, probe)
    if achieved <= 0.0:
        raise NumericalFailure("probe localisation ratio is not positive")
    return nm.scale(probe, target / achieved)


@dataclass(frozen=True)
class RecordOutcome:
    """Everything one synthetic record contributes to the verdict.

    ``reasons`` carries machine-readable refusals; ``reason`` is the short
    human string. Both are retained so a later audit never has to infer why a
    replicate was non-evaluable from an aggregate count.
    """

    log_beta: float | None
    se: float | None
    geometry: float | None
    centre: float | None
    stationarity: float | None
    r_irr: float | None
    diagnostic: DiagnosticComponents | None
    evaluable: bool
    reason: str = ""
    reasons: tuple[Refusal, ...] = ()
    bandwidth_product: float | None = None

    def reason_codes(self) -> list[str]:
        return [r.code for r in self.reasons]


def _quarter_moments(xs: Sequence[Sequence[float]]):
    n = len(xs)
    q = n // N_QUARTERS
    means, covs = [], []
    for k in range(N_QUARTERS):
        seg = xs[k * q : (k + 1) * q]
        m = [sum(r[i] for r in seg) / len(seg) for i in range(2)]
        c = nm.zeros(2, 2)
        for r in seg:
            d0, d1 = r[0] - m[0], r[1] - m[1]
            c[0][0] += d0 * d0
            c[0][1] += d0 * d1
            c[1][1] += d1 * d1
        denom = len(seg) - 1
        c[0][0] /= denom
        c[0][1] /= denom
        c[1][0] = c[0][1]
        c[1][1] /= denom
        means.append(m)
        covs.append(nm.symmetrise(c))
    return means, covs


def run_record(
    spec: GeneratorSpec,
    h_locked,
    stream: Stream,
    x_star: Sequence[float] = (0.0, 0.0),
    want_free: bool = True,
) -> RecordOutcome:
    """Generate and analyse one synthetic record end to end.

    Every failure path records a structured reason, so a later audit can tell
    a bandwidth refusal from an optimiser non-convergence without re-running
    anything.  The lag-antisymmetry inputs required by the diagnostic family
    are computed and supplied here; they are never allowed to default.
    """
    reasons: list[Refusal] = []
    try:
        y = generate_record(spec, stream)
    except NumericalFailure as exc:
        reasons.append(refuse(NUMERICAL_REPRESENTATION_FAILURE,
                              "synthetic generation succeeds", str(exc)))
        return RecordOutcome(None, None, None, None, None, None, None, False,
                             f"generator: {exc}", tuple(reasons))
    try:
        fit = fit_record(
            y, h_locked, spec.p_matrix, spec.r_obs, list(spec.b_det), spec.dt, spec.t_exp,
            want_free=want_free,
        )
    except OptimizerFailure as exc:
        reasons.append(refuse(COMPUTATION_NOT_EVALUABLE,
                              "unique usable maximum established", str(exc)))
        return RecordOutcome(None, None, None, None, None, None, None, False,
                             f"fit: {exc}", tuple(reasons))
    except NumericalFailure as exc:
        reasons.append(refuse(NUMERICAL_REPRESENTATION_FAILURE,
                              "likelihood evaluable", str(exc)))
        return RecordOutcome(None, None, None, None, None, None, None, False,
                             f"fit: {exc}", tuple(reasons))

    try:
        g = geometry_statistic(fit.sigma_free, h_locked)
        m = centre_statistic(fit.mu_free, x_star, h_locked)
    except NumericalFailure as exc:
        reasons.append(refuse(INSUFFICIENT_GEOMETRY_CALIBRATION,
                              "geometry statistics computable", str(exc)))
        return RecordOutcome(fit.log_beta, fit.log_beta_se, None, None, None,
                             fit.r_irr, None, False, f"geometry: {exc}", tuple(reasons))

    pinv = nm.general_inverse(spec.p_matrix)
    xs = [
        [sum(pinv[i][j] * (row[j] - spec.b_det[j]) for j in range(2)) for i in range(2)]
        for row in y
    ]
    stat = None
    try:
        stat = stationarity_statistic(*_quarter_moments(xs), h_locked).statistic
    except NumericalFailure as exc:
        reasons.append(refuse(INSUFFICIENT_GEOMETRY_CALIBRATION,
                              "stationarity statistic computable", str(exc)))

    # --- bandwidth qualification, recorded as its own reason ---------------
    bandwidth = None
    try:
        bandwidth = bandwidth_product(fit.a_free, fit.sigma_free, spec.dt)
        if bandwidth > BANDWIDTH_CEILING:
            reasons.append(refuse(
                OBSERVATION_MODEL_UNQUALIFIED,
                f"||B||_2 dt <= {BANDWIDTH_CEILING}",
                "fitted generator exceeds the non-aliasing bandwidth",
                bandwidth_product=bandwidth,
            ))
    except NumericalFailure as exc:
        reasons.append(refuse(NUMERICAL_REPRESENTATION_FAILURE,
                              "bandwidth product computable", str(exc)))

    # --- the REQUIRED lag-antisymmetry inputs ------------------------------
    diag = None
    diag_reason = None
    try:
        vals, _ = nm.eigh(fit.sigma_free)
        rate_slow = nm.op_norm(fit.a_free)
        slow_vals, _ = nm.eigh(nm.symmetrise(
            nm.scale(nm.add(fit.a_free, nm.transpose(fit.a_free)), 0.5)))
        lam_slow = min(v for v in slow_vals if v > 0.0)
        tau_slow = 1.0 / lam_slow
        lags = required_antisymmetry_lags(tau_slow, spec.dt)
        model_ss = build_state_space(
            fit.a_free, fit.sigma_free, list(fit.mu_free), spec.p_matrix,
            spec.r_obs, list(spec.b_det), spec.dt, spec.t_exp,
        )
        observed = [lag_covariance(y, k) for k in lags]
        fitted = [model_lag_covariance(model_ss, k) for k in lags]
        diag = diagnostic_components(fit.innovations, fit.innovation_cov, observed, fitted)
    except (DiagnosticNotEvaluable, NumericalFailure, ValueError) as exc:
        diag_reason = str(exc)
        reasons.append(refuse(
            COMPUTATION_NOT_EVALUABLE,
            "diagnostic family evaluable",
            f"required lag-antisymmetry inputs unavailable: {exc}",
        ))

    return RecordOutcome(
        fit.log_beta, fit.log_beta_se, g, m, stat, fit.r_irr, diag, True,
        diag_reason or "", tuple(reasons), bandwidth,
    )


def design_specs(
    beta_by_field: Sequence[float] = (1.0, 1.0, 1.0, 1.0),
    n_frames: int = plan.SMOKE_FRAMES,
    r_irr_target: float = 0.0,
    localization_ratio_target: float = plan.LOCALIZATION_RATIO_NOMINAL,
    noise_model: str = "gaussian",
    coupling: float = plan.AXIAL_COUPLING,
    drift_rate: tuple[float, float] = (0.0, 0.0),
    generate_t_exp: float | None = None,
    condition_target: float | None = None,
    exposure_fraction: float = plan.EXPOSURE_FRACTION,
    blur_mismatch: float | None = None,
    h_override=None,
) -> list[tuple[GeneratorSpec, list[list[float]]]]:
    """Build the eight (spec, locked H) pairs of one complete experiment.

    Every non-nominal argument changes the generated world, not merely a
    label: ``condition_target`` reshapes the lateral stiffness before the
    axial reduction, ``exposure_fraction`` moves the shutter, and
    ``localization_ratio_target`` sets the observation covariance.  V3 had
    cases that declared these and generated nominal records anyway.
    """
    out = []
    for block in range(2):
        for fidx in range(4):
            if condition_target is None:
                k3 = plan.nominal_k3(fidx, coupling)
            else:
                k3 = plan.k3_from_lateral(
                    plan.conditioned_stiffness(
                        plan.nominal_stiffness(fidx), condition_target
                    ),
                    coupling,
                )
            temp = plan.nominal_temperature(fidx)
            red = reduce_axial(
                k3, temp,
                evidence=AxialEvidence.fully_qualified(),
                c_v=nm.scale(nm.eye(6), (1e-3 * plan.K_REF) ** 2),
            )
            if not red.ok:
                raise NumericalFailure(f"design point refused: {red.refusals}")
            h_eff = red.h_eff
            h_locked = h_eff if h_override is None else h_override(fidx, h_eff)
            dt, t_exp = plan.timing(red.k_eff, exposure_fraction)
            sigma = nm.spd_inverse(h_eff)
            # Overdamped Langevin: A = K_eff / gamma, so D = (A Sigma + Sigma A^T)/2.
            a_drift = nm.scale(red.k_eff, 1.0 / plan.drag_coefficient())
            asig = nm.matmul(a_drift, sigma)
            d_true = nm.symmetrise(nm.scale(nm.add(asig, nm.transpose(asig)), 0.5))
            omega = current_control_drift(d_true, sigma, r_irr_target)
            r_obs = solve_r_obs(a_drift, sigma, dt, t_exp, localization_ratio_target)
            spec = GeneratorSpec(
                h_true=h_eff,
                beta_true=beta_by_field[fidx],
                mu_true=(0.0, 0.0),
                d_true=d_true,
                omega_true=omega,
                p_matrix=nm.eye(2),
                r_obs=r_obs,
                b_det=(0.0, 0.0),
                dt=dt,
                t_exp=t_exp,
                n_frames=n_frames,
                noise_model=noise_model,
                drift_rate=drift_rate,
                generate_t_exp=(
                    generate_t_exp if blur_mismatch is None
                    else blur_mismatch * dt
                ),
            )
            out.append((spec, h_locked))
    return out


@dataclass
class Aggregator:
    """Counts events and reports an exact Clopper-Pearson bound."""

    case_id: str
    family: str
    bound_kind: str
    required: float
    events: int = 0
    trials: int = 0
    notes: list[str] = field(default_factory=list)

    def add(self, event: bool) -> None:
        self.trials += 1
        if event:
            self.events += 1

    def result(self, detail: dict | None = None) -> ValidationResult:
        if self.trials == 0:
            return ValidationResult(
                self.case_id, self.family, 0, 0, float("nan"), float("nan"),
                self.bound_kind, self.required, False,
                {"reason": "no trials run", **(detail or {})},
            )
        p = self.events / self.trials
        if self.bound_kind == "cp_upper":
            bound = clopper_pearson_upper(self.events, self.trials, 0.95)
            passed = bound <= self.required
        else:
            bound = clopper_pearson_lower(self.events, self.trials, 0.95)
            passed = bound >= self.required
        return ValidationResult(
            self.case_id, self.family, self.trials, self.events, p, bound,
            self.bound_kind, self.required, passed, detail or {},
        )


# ---------------------------------------------------------------------------
# The design point's calibration primitive model
# ---------------------------------------------------------------------------

#: Primitive names of the synthetic design-point calibration model.
PRIMITIVE_K_STANDARD = "log_k_standard"
PRIMITIVE_T_STANDARD = "log_T_standard"
PRIMITIVE_K_FIELD = "log_k_field"

#: Standard uncertainty of the shared temperature standard, in log K.
SIGMA_LOG_T_STANDARD = 1.0e-3

_CALIBRATION_CACHE: dict[tuple, "ExperimentCalibration"] = {}


def _field_model_builder(
    k3, temperature: float, dt: float, t_exp: float, r_obs,
    idx_shared: int, idx_temp: int, idx_field: int,
):
    """``phi -> FieldModel`` for one record of the design point.

    The shared standard and the field-specific primitive both act on the
    MEASURED stiffness, so two records sharing the standard move together.
    The truth is whatever the unperturbed primitives describe.
    """
    red = reduce_axial(
        k3, temperature,
        evidence=AxialEvidence.fully_qualified(),
        c_v=nm.scale(nm.eye(6), (1e-3 * plan.K_REF) ** 2),
    )
    if not red.ok:
        raise NumericalFailure(f"calibration design point refused: {red.refusals}")
    k_true = red.k_eff
    sigma_true = nm.spd_inverse(red.h_eff)
    a_true = nm.scale(k_true, 1.0 / plan.drag_coefficient())

    def build(phi: Sequence[float]) -> FieldModel:
        log_k = float(phi[idx_shared]) + float(phi[idx_field])
        t_meas = temperature * math.exp(float(phi[idx_temp]))
        k_meas = nm.scale(k_true, math.exp(log_k))
        h_meas = nm.symmetrise(nm.scale(k_meas, 1.0 / (K_B * t_meas)))
        return FieldModel(
            h_eff=h_meas, k_eff=k_meas, temperature=t_meas,
            a_drift=a_true, sigma=sigma_true, p_matrix=nm.eye(2),
            r_obs=r_obs, b_det=(0.0, 0.0), dt=dt, t_exp=t_exp,
        )

    return build


def experiment_calibration(
    spec_kwargs: Mapping[str, object] | None = None,
) -> "ExperimentCalibration":
    """The joint ``C_b,cal`` of the eight endpoints at this design point.

    Cached on the design configuration: the calibration covariance is a
    property of the apparatus, not of a random draw, so it is computed once
    per world and reused across replicates.  This is the object the official
    interval builder consumes; V3 left the assembler exercised only by tests.
    """
    kw = dict(spec_kwargs or {})
    key = tuple(sorted((k, repr(v)) for k, v in kw.items()))
    if key in _CALIBRATION_CACHE:
        return _CALIBRATION_CACHE[key]

    condition_target = kw.get("condition_target")
    coupling = float(kw.get("coupling", plan.AXIAL_COUPLING))  # type: ignore[arg-type]
    exposure_fraction = float(kw.get("exposure_fraction", plan.EXPOSURE_FRACTION))  # type: ignore[arg-type]
    noise_target = float(
        kw.get("localization_ratio_target", plan.LOCALIZATION_RATIO_NOMINAL)  # type: ignore[arg-type]
    )

    vector = PrimitiveVector()
    vector.add(Primitive(PRIMITIVE_K_STANDARD, Scope.GLOBAL, 0.0, plan.SIGMA_CAL_ABSOLUTE))
    vector.add(Primitive(PRIMITIVE_T_STANDARD, Scope.GLOBAL, 0.0, SIGMA_LOG_T_STANDARD))
    for blk, fld in RECORDS:
        vector.add(Primitive(PRIMITIVE_K_FIELD, Scope.FIELD, 0.0, plan.SIGMA_CAL_CELL, blk, fld))
    idx_shared = vector.index_of(PRIMITIVE_K_STANDARD)
    idx_temp = vector.index_of(PRIMITIVE_T_STANDARD)

    builders: list[tuple[str, object]] = []
    for blk, fld in RECORDS:
        fidx = fld.index
        if condition_target is None:
            k3 = plan.nominal_k3(fidx, coupling)
        else:
            k3 = plan.k3_from_lateral(
                plan.conditioned_stiffness(
                    plan.nominal_stiffness(fidx), float(condition_target)
                ),
                coupling,
            )
        temperature = plan.nominal_temperature(fidx)
        red = reduce_axial(
            k3, temperature, evidence=AxialEvidence.fully_qualified(),
            c_v=nm.scale(nm.eye(6), (1e-3 * plan.K_REF) ** 2),
        )
        dt, t_exp = plan.timing(red.k_eff, exposure_fraction)
        sigma = nm.spd_inverse(red.h_eff)
        a_drift = nm.scale(red.k_eff, 1.0 / plan.drag_coefficient())
        r_obs = solve_r_obs(a_drift, sigma, dt, t_exp, noise_target)
        idx_field = vector.index_of(
            Primitive(PRIMITIVE_K_FIELD, Scope.FIELD, 0.0, plan.SIGMA_CAL_CELL, blk, fld).key
        )
        builders.append((
            f"{blk.value}/{fld.value}",
            _field_model_builder(k3, temperature, dt, t_exp, r_obs,
                                 idx_shared, idx_temp, idx_field),
        ))
    cal = build_experiment_calibration(vector, builders)
    _CALIBRATION_CACHE[key] = cal
    return cal


def axial_remainder_bias(
    fidx: int, coupling: float = plan.AXIAL_COUPLING
) -> float:
    """This record's certified axial remainder contribution to its bias budget.

    The design point certifies the remainder at a 5% axial perturbation; it is
    normalised against ``K_eff`` and enters the EXISTING per-record bounded
    bias rather than carrying an allowance of its own.
    """
    k3 = plan.nominal_k3(fidx, coupling)
    _, b, kappa = split_3d(nm.symmetrise(k3))
    rem = schur_nonlinear_remainder(
        [b[0][0], b[1][0]], kappa,
        [0.05 * b[0][0], 0.05 * b[1][0]], 0.05 * kappa,
    )
    impacts = remainder_impacts(normalise_remainder(rem, schur_complement(k3)))
    return impacts.log_beta_bias
