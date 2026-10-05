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
from typing import Callable, Sequence

from .. import numerics as nm
from ..confidence import (
    CriticalValues,
    DELTA_A,
    DELTA_C,
    Interval,
    build_interval,
    calibrated_upper_limit,
)
from ..diagnostics import DiagnosticComponents, NullScales, diagnostic_components
from ..gates import (
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
from ..observation import build_state_space, effective_noise_to_signal, localization_ratio
from ..reduction import reduce_axial
from ..rng import Stream
from ..seeds import SeedMap
from . import plan


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
    """Everything one synthetic record contributes to the verdict."""

    log_beta: float | None
    se: float | None
    geometry: float | None
    centre: float | None
    stationarity: float | None
    r_irr: float | None
    diagnostic: DiagnosticComponents | None
    evaluable: bool
    reason: str = ""


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
    """Generate and analyse one synthetic record end to end."""
    try:
        y = generate_record(spec, stream)
    except NumericalFailure as exc:
        return RecordOutcome(None, None, None, None, None, None, None, False, f"generator: {exc}")
    try:
        fit = fit_record(
            y, h_locked, spec.p_matrix, spec.r_obs, list(spec.b_det), spec.dt, spec.t_exp,
            want_free=want_free,
        )
    except (OptimizerFailure, NumericalFailure) as exc:
        return RecordOutcome(None, None, None, None, None, None, None, False, f"fit: {exc}")

    try:
        g = geometry_statistic(fit.sigma_free, h_locked)
        m = centre_statistic(fit.mu_free, x_star, h_locked)
    except NumericalFailure as exc:
        return RecordOutcome(
            fit.log_beta, fit.log_beta_se, None, None, None, fit.r_irr, None, False,
            f"geometry: {exc}",
        )

    pinv = nm.general_inverse(spec.p_matrix)
    xs = [
        [sum(pinv[i][j] * (row[j] - spec.b_det[j]) for j in range(2)) for i in range(2)]
        for row in y
    ]
    try:
        stat = stationarity_statistic(*_quarter_moments(xs), h_locked).statistic
    except NumericalFailure as exc:
        stat = None

    diag = None
    if fit.innovations:
        try:
            diag = diagnostic_components(fit.innovations, fit.innovation_cov)
        except NumericalFailure:
            diag = None

    return RecordOutcome(
        fit.log_beta, fit.log_beta_se, g, m, stat, fit.r_irr, diag, True
    )


def design_specs(
    beta_by_field: Sequence[float] = (1.0, 1.0, 1.0, 1.0),
    n_frames: int = plan.SMOKE_FRAMES,
    omega: float = 0.0,
    localization_ratio_target: float = plan.LOCALIZATION_RATIO_NOMINAL,
    noise_model: str = "gaussian",
    coupling: float = plan.AXIAL_COUPLING,
    drift_rate: tuple[float, float] = (0.0, 0.0),
    generate_t_exp: float | None = None,
    h_override=None,
) -> list[tuple[GeneratorSpec, list[list[float]]]]:
    """Build the eight (spec, locked H) pairs of one complete experiment."""
    out = []
    for block in range(2):
        for fidx in range(4):
            k3 = plan.nominal_k3(fidx, coupling)
            temp = plan.nominal_temperature(fidx)
            red = reduce_axial(k3, temp)
            if not red.ok:
                raise NumericalFailure(f"design point refused: {red.refusals}")
            h_eff = red.h_eff
            h_locked = h_eff if h_override is None else h_override(fidx, h_eff)
            dt, t_exp = plan.timing(red.k_eff)
            sigma = nm.spd_inverse(h_eff)
            # Overdamped Langevin: A = K_eff / gamma, so D = (A Sigma + Sigma A^T)/2.
            a_drift = nm.scale(red.k_eff, 1.0 / plan.drag_coefficient())
            asig = nm.matmul(a_drift, sigma)
            d_true = nm.symmetrise(nm.scale(nm.add(asig, nm.transpose(asig)), 0.5))
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
                generate_t_exp=generate_t_exp,
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
