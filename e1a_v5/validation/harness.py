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

from .. import certified as cert
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
from ..generate import (
    AxialMemorySpec, GeneratorSpec, ResponseSpec, axial_memory_dynamics,
    generate_axial_memory_record, generate_record,
    generate_response_record, markov_closure_residual,
)
from ..numerics import NumericalFailure, clopper_pearson_lower, clopper_pearson_upper
from ..optimize import OptimizerFailure
from ..estimate import fit_record
from ..packets import ValidationResult
from ..observation import (
    BANDWIDTH_CEILING, ObservationEnvelope, ObservationQualification,
    bandwidth_product, build_state_space, effective_noise_to_signal,
    generalized_relaxation_rates, localization_ratio, model_lag_covariance,
    observed_signal_covariance, qualify_observation_envelope,
)
from ..calibration import (
    AnalysisModel,
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
    RemainderSet,
    normalise_remainder,
    reduce_axial,
    remainder_impacts,
    remainder_set_effects,
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
    achieved = localization_ratio(sigma, probe, nm.eye(2))
    if achieved <= 0.0:
        raise NumericalFailure("probe localisation ratio is not positive")
    return nm.scale(probe, target / achieved)


def design_evidence(k3, temperature: float) -> AxialEvidence:
    """Axial evidence for a world being CONSTRUCTED, temporal item derived.

    The remainder set comes from the joint 99.9% calibration region and the
    temporal item from the constructed world's own exact semigroup residual.
    Nothing here is a literal.
    """
    return AxialEvidence.fully_qualified(
        plan.remainder_set(k3),
        temporal_qualified=plan.construction_temporal_qualified(
            schur_complement(k3), temperature),
    )


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
    #: Explicit T 15.2 / T.23 observation-domain qualification for this record.
    observation: "ObservationQualification | None" = None
    #: Optimiser outcome, or NOT_APPLICABLE where no fit was attempted.
    optimizer_status: str = "NOT_APPLICABLE"

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
    envelope: "ObservationEnvelope | None" = None,
    analysis_spec: "GeneratorSpec | None" = None,
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
                             f"generator: {exc}", tuple(reasons),
                             optimizer_status="NOT_ATTEMPTED")
    return _analyse_record(y, analysis_spec or spec, h_locked, x_star,
                           want_free, envelope, reasons)


def _analyse_record(y, spec, h_locked, x_star, want_free, envelope, reasons):
    """The production analysis of one observed record, generator-agnostic."""
    try:
        fit = fit_record(
            y, h_locked, spec.p_matrix, spec.r_obs, list(spec.b_det), spec.dt, spec.t_exp,
            want_free=want_free,
        )
    except OptimizerFailure as exc:
        reasons.append(refuse(COMPUTATION_NOT_EVALUABLE,
                              "unique usable maximum established", str(exc)))
        return RecordOutcome(None, None, None, None, None, None, None, False,
                             f"fit: {exc}", tuple(reasons),
                             optimizer_status="OPTIMIZER_FAILURE")
    except NumericalFailure as exc:
        reasons.append(refuse(NUMERICAL_REPRESENTATION_FAILURE,
                              "likelihood evaluable", str(exc)))
        return RecordOutcome(None, None, None, None, None, None, None, False,
                             f"fit: {exc}", tuple(reasons),
                             optimizer_status="NUMERICAL_FAILURE")

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

    # --- T 15.2 / T.23 observation-domain qualification ---------------------
    # Evaluated over the INDEPENDENT pre-Branch-B envelope, never from the
    # fitted free model: the apparatus is qualified before a fit exists, and a
    # fit must not be able to qualify the apparatus that produced it.  The
    # fitted bandwidth check above keeps its separate Branch-B role.
    if envelope is None:
        obs = ObservationQualification(
            valid=False,
            refusals=(refuse(
                OBSERVATION_MODEL_UNQUALIFIED,
                "independent observation envelope supplied",
                "no pre-Branch-B observation envelope was established for "
                "this record; a missing qualification is not a qualification",
            ),),
        )
    else:
        try:
            obs = qualify_observation_envelope(envelope)
        except NumericalFailure as exc:
            obs = ObservationQualification(
                valid=False,
                refusals=(refuse(NUMERICAL_REPRESENTATION_FAILURE,
                                 "observation qualification computable", str(exc)),),
            )
        try:
            model_ss_obs = build_state_space(
                fit.a_free, fit.sigma_free, list(fit.mu_free), spec.p_matrix,
                spec.r_obs, list(spec.b_det), spec.dt, spec.t_exp,
            )
            obs = type(obs)(
                **{**obs.__dict__,
                   "exposure_averaged_ratio": effective_noise_to_signal(model_ss_obs)}
            )
        except NumericalFailure:
            pass
    reasons.extend(obs.refusals)

    return RecordOutcome(
        fit.log_beta, fit.log_beta_se, g, m, stat, fit.r_irr, diag, True,
        diag_reason or "", tuple(reasons), bandwidth, obs,
        optimizer_status="CONVERGED" if fit.converged else "NOT_CONVERGED",
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
            c_v = nm.scale(nm.eye(6), (plan.PRIMITIVE_RELATIVE_SIGMA * plan.K_REF) ** 2)
            red = reduce_axial(
                k3, temp,
                evidence=design_evidence(k3, temp),
                c_v=c_v,
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

_CALIBRATION_CACHE: dict[tuple, "ExperimentCalibration"] = {}


def _p_index(vector, name, blk=None, fld=None):
    from ..calibration import Primitive, Scope
    scope = Scope.GLOBAL if blk is None else (
        Scope.BLOCK if fld is None else Scope.FIELD)
    return vector.index_of(Primitive(name, scope, 0.0, 0.0, blk, fld).key)


def _record_indices(vector, blk, fld):
    """Every primitive index this record's analysis model reads."""
    P = plan
    return {
        "k_std": _p_index(vector, P.PRIMITIVE_K_STANDARD),
        "t_std": _p_index(vector, P.PRIMITIVE_T_STANDARD),
        "force": _p_index(vector, P.PRIMITIVE_FORCE_CAL),
        "axial_k": _p_index(vector, P.PRIMITIVE_AXIAL_STIFFNESS),
        "axial_c": _p_index(vector, P.PRIMITIVE_AXIAL_COUPLING),
        "p_gain": _p_index(vector, P.PRIMITIVE_P_GAIN),
        "p_shear": _p_index(vector, P.PRIMITIVE_P_SHEAR),
        "bead": _p_index(vector, P.PRIMITIVE_BEAD_RADIUS),
        "r_obs": _p_index(vector, P.PRIMITIVE_R_OBS),
        "b_x": _p_index(vector, P.PRIMITIVE_B_DET_X),
        "b_y": _p_index(vector, P.PRIMITIVE_B_DET_Y),
        "t_exp": _p_index(vector, P.PRIMITIVE_T_EXP),
        "dt": _p_index(vector, P.PRIMITIVE_DT),
        "k_block": _p_index(vector, P.PRIMITIVE_K_BLOCK, blk, None),
        "t_block": _p_index(vector, P.PRIMITIVE_T_BLOCK, blk, None),
        "k_field": _p_index(vector, P.PRIMITIVE_K_FIELD, blk, fld),
    }


def _field_model_builders(k3, temperature: float, dt: float, t_exp: float,
                          r_obs, idx: Mapping[str, int]):
    """``(float builder, generic builder)`` for one record of the design point.

    Two builders over the SAME map: the float one supplies the fixed truth and
    the linearisation point, the generic one accepts interval hyper-dual
    primitives so the certified sensitivity can differentiate through it.

    Every declared stochastic primitive that physically reaches the analysis
    side reaches it here.  V5 moved only an overall stiffness scale and a
    temperature, so ten of the categories U requires had no route into
    ``J_beta`` at all.  The chain is now:

    * the stiffness standard, the block transfer, the field primitive and the
      3D force/displacement transfer scale the WHOLE 3D stiffness, so the
      reduction's own axial term scales with it and the exact reference
      ``d log beta*/d log k_A = -1`` survives;
    * the axial stiffness and the lateral-axial coupling move ``kappa`` and
      ``b`` separately, and the Schur complement is formed generically from
      them, so the reduction is differentiated rather than assumed;
    * the temperature standard and its block transfer move ``T``;
    * the coordinate transform's gain and shear, and the bead-radius transfer
      that the displacement calibration rides on, move ``P``;
    * the localisation covariance scale moves ``R_obs``, the detector offsets
      move ``b_det``, the shutter calibration moves ``t_exp`` and the timing
      standard moves ``dt``.

    The viscosity parameters and the centre/fiducial transfer are deliberately
    absent from this map: the estimator profiles the full drift ``A`` freely,
    so the drag cannot bias the fitted scale, and the fiducial enters only the
    centre statistic.  Their ``J_beta`` rows are therefore structurally zero,
    which :func:`~e1a_v5.calibration.certified_profiled_sensitivity` detects
    and records rather than assumes.
    """
    red = reduce_axial(
        k3, temperature,
        evidence=design_evidence(k3, temperature),
        c_v=nm.scale(nm.eye(6), (plan.PRIMITIVE_RELATIVE_SIGMA * plan.K_REF) ** 2),
    )
    if not red.ok:
        raise NumericalFailure(f"calibration design point refused: {red.refusals}")
    k_true = red.k_eff
    sigma_true = nm.spd_inverse(red.h_eff)
    a_true = nm.scale(k_true, 1.0 / plan.drag_coefficient())
    k3s = nm.symmetrise(k3)
    k_qq = [[k3s[0][0], k3s[0][1]], [k3s[1][0], k3s[1][1]]]
    b_nom = [k3s[0][2], k3s[1][2]]
    kappa_nom = k3s[2][2]

    def _schur(scale_k, axial_k, axial_c, gexp):
        """``K_qq - b b^T / kappa`` with each piece carrying its primitives."""
        s_k = gexp(scale_k)
        f_c = gexp(axial_c)
        kappa = gexp(axial_k) * (kappa_nom * s_k)
        bv = [(b_nom[i] * s_k) * f_c for i in range(2)]
        qq = [[k_qq[i][j] * s_k for j in range(2)] for i in range(2)]
        return [[qq[i][j] - bv[i] * bv[j] / kappa for j in range(2)]
                for i in range(2)]

    def build_float(phi: Sequence[float]) -> FieldModel:
        f = [float(v) for v in phi]
        scale_k = f[idx["k_std"]] + f[idx["k_block"]] + f[idx["k_field"]] + f[idx["force"]]
        k_meas = nm.symmetrise(
            _schur(scale_k, f[idx["axial_k"]], f[idx["axial_c"]], math.exp))
        t_meas = temperature * math.exp(f[idx["t_std"]] + f[idx["t_block"]])
        gain = math.exp(f[idx["p_gain"]] + f[idx["bead"]])
        sh = f[idx["p_shear"]]
        p_meas = [[gain, gain * sh], [gain * sh, gain]]
        return FieldModel(
            h_eff=nm.symmetrise(nm.scale(k_meas, 1.0 / (K_B * t_meas))),
            k_eff=k_meas, temperature=t_meas,
            a_drift=a_true, sigma=sigma_true, p_matrix=p_meas,
            r_obs=nm.scale(r_obs, math.exp(f[idx["r_obs"]])),
            b_det=(f[idx["b_x"]], f[idx["b_y"]]),
            dt=dt * math.exp(f[idx["dt"]]),
            t_exp=t_exp * math.exp(f[idx["t_exp"]]),
        )

    def build_generic(phi: Sequence) -> AnalysisModel:
        scale_k = phi[idx["k_std"]] + phi[idx["k_block"]] + phi[idx["k_field"]] + phi[idx["force"]]
        k_meas = cert.gsym(
            _schur(scale_k, phi[idx["axial_k"]], phi[idx["axial_c"]], cert.gexp))
        inv_kt = cert.gexp(-(phi[idx["t_std"]] + phi[idx["t_block"]])) * (
            1.0 / (K_B * temperature))
        gain = cert.gexp(phi[idx["p_gain"]] + phi[idx["bead"]])
        sh = phi[idx["p_shear"]]
        return AnalysisModel(
            h_locked=cert.gsym(cert.gscale(k_meas, inv_kt)),
            p_matrix=[[gain, gain * sh], [gain * sh, gain]],
            r_obs=cert.gscale(r_obs, cert.gexp(phi[idx["r_obs"]])),
            b_det=(phi[idx["b_x"]], phi[idx["b_y"]]),
            dt=cert.gexp(phi[idx["dt"]]) * dt,
            t_exp=cert.gexp(phi[idx["t_exp"]]) * t_exp,
        )

    return build_float, build_generic


def record_world(fidx: int, coupling: float, condition_target, exposure_fraction,
                 noise_target):
    """The nominal 3D stiffness, timing and observation covariance of a record."""
    if condition_target is None:
        k3 = plan.nominal_k3(fidx, coupling)
    else:
        k3 = plan.k3_from_lateral(
            plan.conditioned_stiffness(
                plan.nominal_stiffness(fidx), float(condition_target)),
            coupling,
        )
    temperature = plan.nominal_temperature(fidx)
    red = reduce_axial(
        k3, temperature,
        evidence=design_evidence(k3, temperature),
        c_v=nm.scale(nm.eye(6), (plan.PRIMITIVE_RELATIVE_SIGMA * plan.K_REF) ** 2),
    )
    dt, t_exp = plan.timing(red.k_eff, exposure_fraction)
    sigma = nm.spd_inverse(red.h_eff)
    a_drift = nm.scale(red.k_eff, 1.0 / plan.drag_coefficient())
    r_obs = solve_r_obs(a_drift, sigma, dt, t_exp, noise_target)
    return k3, temperature, red, dt, t_exp, sigma, a_drift, r_obs


def calibration_inputs(
    spec_kwargs: Mapping[str, object] | None = None,
    share_thermometry: bool = True,
):
    """``(primitive vector, record builders)`` for one world configuration."""
    kw = dict(spec_kwargs or {})
    condition_target = kw.get("condition_target")
    coupling = float(kw.get("coupling", plan.AXIAL_COUPLING))  # type: ignore[arg-type]
    exposure_fraction = float(kw.get("exposure_fraction", plan.EXPOSURE_FRACTION))  # type: ignore[arg-type]
    noise_target = float(
        kw.get("localization_ratio_target", plan.LOCALIZATION_RATIO_NOMINAL)  # type: ignore[arg-type]
    )
    vector = plan.primitive_vector(share_thermometry=share_thermometry)
    builders: list[tuple[str, object, object]] = []
    for blk, fld in RECORDS:
        k3, temperature, _red, dt, t_exp, _sigma, _a, r_obs = record_world(
            fld.index, coupling, condition_target, exposure_fraction, noise_target)
        bf, bg = _field_model_builders(
            k3, temperature, dt, t_exp, r_obs, _record_indices(vector, blk, fld))
        builders.append((f"{blk.value}/{fld.value}", bf, bg))
    return vector, builders


def experiment_calibration(
    spec_kwargs: Mapping[str, object] | None = None,
    omit_eta_t_covariance: bool = False,
) -> "ExperimentCalibration":
    """The joint ``C_b,cal`` of the eight endpoints at this design point.

    Cached on the design configuration: the calibration covariance is a
    property of the apparatus, not of a random draw, so it is computed once
    per world and reused across replicates.  This is the object the official
    interval builder consumes.

    ``omit_eta_t_covariance`` is the CTL-ETA-T-COV misspecification: the
    ANALYSER drops the shared thermometry latent and treats the stiffness and
    temperature standards as independent.  The generating law is unaffected.
    """
    kw = dict(spec_kwargs or {})
    key = tuple(sorted((k, repr(v)) for k, v in kw.items())) + (
        ("omit_eta_t_covariance", repr(bool(omit_eta_t_covariance))),
    )
    if key in _CALIBRATION_CACHE:
        return _CALIBRATION_CACHE[key]
    vector, builders = calibration_inputs(
        kw, share_thermometry=not omit_eta_t_covariance)
    cal = build_experiment_calibration(vector, builders)
    _CALIBRATION_CACHE[key] = cal
    return cal


# ---------------------------------------------------------------------------
# Branch-A temporal-model qualification, from a measured response
# ---------------------------------------------------------------------------

TEMPORAL_QUALIFIED = "QUALIFIED"
TEMPORAL_UNQUALIFIED = "UNQUALIFIED"
TEMPORAL_UNRESOLVED = "UNRESOLVED"


def true_system(spec: GeneratorSpec):
    """``(A, Sigma)`` of the TRUE 2D physical system behind a generator spec.

    The same algebra the generator itself uses, so the response measurement is
    a measurement of the world that produced the record and not of a model of
    it.
    """
    sigma = nm.symmetrise(nm.scale(nm.spd_inverse(spec.h_true), 1.0 / spec.beta_true))
    q = [[0.0, -spec.omega_true], [spec.omega_true, 0.0]]
    return nm.matmul(nm.add(spec.d_true, q), nm.spd_inverse(sigma)), sigma


def temporal_qualification(
    a_full, sigma_full, k_eff, p_matrix, r_obs, b_det, stream: Stream,
) -> dict:
    """Qualify the retained 2D temporal model against a MEASURED response.

    No flag is supplied and nothing is fitted.  The measurement asks the one
    question that separates the admissible class from everything else: does
    the system's mean lateral response satisfy the semigroup identity
    ``R(2 tau) = R(tau)^2`` that EVERY 2D linear generator satisfies?  A
    violation beyond the measurement's own 5-sigma standard error excludes the
    whole class at once; a band too wide to exclude anything returns
    UNRESOLVED, which does not qualify.
    """
    vals, _ = nm.eigh(nm.symmetrise(k_eff))
    tau_slow = plan.drag_coefficient() / min(vals)
    spec = ResponseSpec(
        a_drift=a_full, sigma=sigma_full, p_matrix=p_matrix, r_obs=r_obs,
        b_det=tuple(b_det), tau=plan.RESPONSE_LAG_FRACTION * tau_slow,
        trials=plan.RESPONSE_TRIALS,
        displacement_sd=plan.RESPONSE_DISPLACEMENT_SD,
    )
    out = generate_response_record(spec, stream)
    band = plan.RESPONSE_BAND_SIGMA * out["residual_standard_error"]
    if not (band <= plan.RESPONSE_RESOLUTION):
        status = TEMPORAL_UNRESOLVED
    elif out["semigroup_residual"] <= band:
        status = TEMPORAL_QUALIFIED
    else:
        status = TEMPORAL_UNQUALIFIED
    return {
        **{k: v for k, v in out.items() if k not in ("r_tau", "r_2tau")},
        "band": band,
        "resolution_required": plan.RESPONSE_RESOLUTION,
        "status": status,
        "qualified": status == TEMPORAL_QUALIFIED,
    }


# ---------------------------------------------------------------------------
# The independent pre-Branch-B observation envelope
# ---------------------------------------------------------------------------

def _relative(half_width: float) -> float:
    """Relative excursion of a log primitive over its region half-width."""
    return math.expm1(abs(half_width))


def design_log_beta_range() -> tuple[float, float]:
    """T's declared design / power range of ``log beta``, from the frozen plan.

    Taken as the hull of every true scale the preregistered cases declare --
    the size-boundary nulls, the power alternatives and the blinded-recovery
    scale factors -- widened by the T.7 equivalence margin.  It is derived
    from the plan rather than chosen here, so the observation envelope cannot
    be narrowed by picking a convenient range.
    """
    from .cases import ALL_CASES
    lo = hi = 0.0
    for c in ALL_CASES:
        cfg = c.config
        vals: list[float] = []
        if cfg.b_true is not None:
            vals.append(float(cfg.b_true))
        if cfg.beta_common is not None:
            vals.append(math.log(float(cfg.beta_common)))
        if cfg.betas is not None:
            vals.extend(math.log(float(b)) for b in cfg.betas)
        if cfg.blind_scale is not None:
            # the analysis sees H_A * c, so the fitted scale shifts by -log c
            vals.append(-math.log(float(cfg.blind_scale)))
        for v in vals:
            lo, hi = min(lo, v), max(hi, v)
    return (lo - DELTA_A, hi + DELTA_A)


def observation_envelope(
    h_locked, temperature: float, spec, rho: float,
    noise_model: str | None = None,
) -> ObservationEnvelope:
    """Build the record's independent pre-Branch-B qualification envelope.

    Every input is Branch-A physics or instrument calibration: the locked
    thermal Hessian, the calibrated drag, the instrument's detector map,
    localisation covariance and timing, the certified axial-remainder radius
    and the plan's own scale range.  The instrument uncertainties are the
    joint 99.9% region's half-widths for the corresponding primitives, plus
    the declared bounded wall/hydrodynamic systematic on the drag.
    """
    region = plan.default_joint_region()
    k_eff = nm.scale(nm.symmetrise(h_locked), K_B * temperature)
    gamma = nm.scale(nm.eye(2), plan.drag_coefficient())
    p_rel = _relative(
        region.half_width_of_name(plan.PRIMITIVE_P_GAIN)
        + region.half_width_of_name(plan.PRIMITIVE_BEAD_RADIUS)
    ) + region.half_width_of_name(plan.PRIMITIVE_P_SHEAR)
    drag_rel = _relative(
        region.half_width_of_name(plan.PRIMITIVE_ETA_REF)
        + region.half_width_of_name(plan.PRIMITIVE_ETA_DT)
        + region.half_width_of_name(plan.PRIMITIVE_BEAD_RADIUS)
    ) + region.bounded_systematic("wall_hydrodynamic_resistance")
    return ObservationEnvelope(
        h_eff=nm.symmetrise(h_locked),
        k_eff=k_eff,
        gamma=gamma,
        p_matrix=spec.p_matrix,
        r_obs=spec.r_obs,
        dt=spec.dt,
        t_exp=spec.t_exp,
        log_beta_range=design_log_beta_range(),
        remainder_rho=rho,
        p_relative=p_rel,
        r_relative=_relative(region.half_width_of_name(plan.PRIMITIVE_R_OBS)),
        drag_relative=drag_rel,
        t_exp_relative=_relative(region.half_width_of_name(plan.PRIMITIVE_T_EXP)),
        dt_relative=_relative(region.half_width_of_name(plan.PRIMITIVE_DT)),
        noise_model=(getattr(spec, "noise_model", "gaussian")
                     if noise_model is None else noise_model),
    )


def auxiliary_measurement(spec_kwargs, stream: Stream):
    """One FRESH draw of the auxiliary calibration measurements.

    The draw comes from the declared generating law -- shared latent
    thermometry included -- so the data a misspecification control analyses
    really do carry the dependency the analyser is about to drop.  V5 altered
    only the analyser's covariance matrix and never drew an auxiliary
    measurement at all, which the audit rejected: nothing in the pipeline was
    exposed to the shared error.

    Returns ``(vector, phi, [(key, FieldModel), ...])``: the primitive vector,
    the drawn primitive values, and what an analyst holding exactly those
    measurements would lock in for each record.
    """
    vector, builders = calibration_inputs(spec_kwargs, share_thermometry=True)
    phi = vector.draw(stream)
    return vector, phi, [(key, bf(phi)) for key, bf, _ in builders]


def measured_analysis_spec(spec: GeneratorSpec, fm) -> GeneratorSpec:
    """The generator spec with the analyst's MEASURED calibration substituted.

    A calibration measurement error moves what the analyst locks in -- the
    detector map, the localisation covariance, the offset and the timing --
    while the physics that produced the record stays where it is.
    """
    return type(spec)(**{
        **spec.__dict__,
        "p_matrix": fm.p_matrix,
        "r_obs": fm.r_obs,
        "b_det": tuple(fm.b_det),
        "dt": fm.dt,
        "t_exp": fm.t_exp,
    })


def axial_effects(fidx: int, coupling: float = plan.AXIAL_COUPLING,
                  condition_target: float | None = None):
    """Exact finite effects of this record's CERTIFIED REMAINDER SET.

    V4's ``axial_remainder_bias`` evaluated one proportional 5 percent
    perturbation whose trace nearly cancelled and used its first-order scale
    effect as the qualification.  That qualifies one member of the set, not
    the set, and the first-order quantity is not the finite effect.  This
    returns the exact suprema over the whole declared set.
    """
    if condition_target is None:
        k3 = plan.nominal_k3(fidx, coupling)
    else:
        k3 = plan.k3_from_lateral(
            plan.conditioned_stiffness(plan.nominal_stiffness(fidx), condition_target),
            coupling,
        )
    return remainder_set_effects(plan.remainder_set(k3), d=2)


# ---------------------------------------------------------------------------
# CTL-AXIAL-MEMORY: full-pipeline records from the 3D hidden-memory world
# ---------------------------------------------------------------------------

def axial_memory_specs(
    n_frames: int = plan.SMOKE_FRAMES,
    localization_ratio_target: float = plan.LOCALIZATION_RATIO_NOMINAL,
) -> list[tuple[AxialMemorySpec, list[list[float]]]]:
    """The eight (3D spec, locked H) pairs of one hidden-memory experiment.

    ``h_locked`` is built from the Schur complement, so Branch A reports
    exactly the field whose density the 3D world realises.  The analysis then
    fits the retained 2D temporal model to a path that no 2D generator
    produces.
    """
    out: list[tuple[AxialMemorySpec, list[list[float]]]] = []
    for _block in range(2):
        for fidx in range(4):
            k3 = plan.axial_memory_k3(fidx)
            temp = plan.nominal_temperature(fidx)
            # The locked field is taken straight from the Schur complement,
            # NOT through the qualified reduction.  That is the control's
            # whole point: Branch A reports the field whose density the 3D
            # world really has, and the reduction's temporal item is exactly
            # what this world does not satisfy.  Routing it through
            # ``reduce_axial`` would either refuse the world -- leaving the
            # control with nothing to run -- or, worse, qualify it by
            # construction.  The refusal happens where it belongs: in the
            # per-replicate measured temporal qualification.
            k_eff = schur_complement(k3)
            h_eff = plan.thermal_hessian(k_eff, temp)
            dt, t_exp = plan.timing(k_eff)
            sigma = nm.spd_inverse(h_eff)
            a_eff = nm.scale(k_eff, 1.0 / plan.drag_coefficient())
            r_obs = solve_r_obs(a_eff, sigma, dt, t_exp, localization_ratio_target)
            out.append((
                AxialMemorySpec(
                    k3=k3, temperature=temp, gamma=plan.drag_coefficient(),
                    p_matrix=nm.eye(2), r_obs=r_obs, b_det=(0.0, 0.0),
                    dt=dt, t_exp=t_exp, n_frames=n_frames,
                ),
                h_eff,
            ))
    return out


def axial_memory_witness(spec: AxialMemorySpec) -> dict:
    """Deterministic proof that this world is the one the control declares.

    Established before any replicate is generated:

    * ``K3`` is positive definite and its Schur complement is valid;
    * the stationary 3D covariance is the canonical ``k_B T K3^{-1}``;
    * the lateral MARGINAL covariance equals ``k_B T K_eff^{-1}`` exactly;
    * the lateral LAG structure violates the Chapman-Kolmogorov identity that
      every 2D Markov process satisfies, so no admissible 2D generator
      reproduces it.
    """
    a3, sigma3 = axial_memory_dynamics(spec)
    k_eff = schur_complement(spec.k3)
    sigma_q = [[sigma3[i][j] for j in range(2)] for i in range(2)]
    expected = nm.scale(nm.spd_inverse(k_eff), K_B * spec.temperature)
    marginal_error = (
        nm.max_abs(nm.sub(sigma_q, expected)) / max(nm.max_abs(expected), 1e-300)
    )
    vals, _ = nm.eigh(nm.symmetrise(spec.k3))
    tau_slow = spec.gamma / min(vals)
    residuals = {
        f"tau_slow_x{m}": markov_closure_residual(a3, sigma3, m * tau_slow)
        for m in (0.25, 0.5, 1.0)
    }
    return {
        "k3_spd": nm.is_spd(spec.k3),
        "schur_spd": nm.is_spd(k_eff),
        "lateral_marginal_relative_error": marginal_error,
        "markov_closure_residual": residuals,
        "worst_markov_closure_residual": max(residuals.values()),
        "condition_k_eff": nm.cond2_spd(k_eff),
    }


def run_axial_memory_record(
    spec: AxialMemorySpec, h_locked, stream: Stream,
    x_star: Sequence[float] = (0.0, 0.0),
    envelope: "ObservationEnvelope | None" = None,
    analysis_spec: "GeneratorSpec | None" = None,
) -> RecordOutcome:
    """Generate from the 3D world, then analyse with the ordinary 2D pipeline.

    Only the generator changes.  The estimator, the gates and the diagnostics
    are exactly the production ones, which is what makes this a full-pipeline
    control rather than a flag flip.
    """
    reasons: list[Refusal] = []
    try:
        y = generate_axial_memory_record(spec, stream)
    except NumericalFailure as exc:
        reasons.append(refuse(NUMERICAL_REPRESENTATION_FAILURE,
                              "3D synthetic generation succeeds", str(exc)))
        return RecordOutcome(None, None, None, None, None, None, None, False,
                             f"generator: {exc}", tuple(reasons),
                             optimizer_status="NOT_ATTEMPTED")
    proxy = GeneratorSpec(
        h_true=h_locked, beta_true=1.0, mu_true=(0.0, 0.0),
        d_true=nm.scale(nm.eye(2), 1.0), omega_true=0.0,
        p_matrix=spec.p_matrix, r_obs=spec.r_obs, b_det=spec.b_det,
        dt=spec.dt, t_exp=spec.t_exp, n_frames=spec.n_frames,
    )
    return _analyse_record(y, analysis_spec or proxy, h_locked, x_star, True,
                           envelope, reasons)
