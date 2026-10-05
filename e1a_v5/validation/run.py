"""V-stage validation runner.

Two execution modes:

``full``
    the T-stage required replicate counts (5000 size, 5000 diagnostic,
    2000 complete eight-record power experiments) at the full information
    target.  This is the only mode whose results can support RELEASE.

``smoke``
    the reduced engineering counts in :mod:`plan`, used when the full campaign
    is computationally infeasible.  Every artefact produced in this mode is
    labelled, and the release verdict is forced to NON-RELEASE: a partial
    validation cannot produce RELEASE.

Deterministic controls (T11a predicates, axial reduction, optimiser failure
handling) are exact and are run at full fidelity in both modes.
"""

from __future__ import annotations

import json
import math
import time
from dataclasses import dataclass
from typing import Callable

from .. import numerics as nm
from .. import realization as rf
from ..confidence import DELTA_A, DELTA_C, Interval, NORMAL_CRITICAL, build_interval
from ..gates import DELTA_G, DELTA_M, DELTA_R_IRR
from ..numerics import clopper_pearson_lower, clopper_pearson_upper
from ..optimize import OptimizerFailure, minimise
from ..reduction import axial_ratio, plane_block_bias, reduce_axial, schur_complement
from ..rng import Stream
from ..seeds import CALIBRATION, CONTROL, DIAGNOSTIC, POWER, SIZE, SeedMap
from . import plan
from .cases import ALL_CASES
from .harness import Aggregator, design_specs, run_record

SMOKE = "smoke"
FULL = "full"


@dataclass
class RunConfig:
    mode: str = SMOKE
    frames: int = plan.SMOKE_FRAMES
    size_replicates: int = plan.SMOKE_SIZE_REPLICATES
    diagnostic_replicates: int = plan.SMOKE_DIAGNOSTIC_REPLICATES
    power_replicates: int = plan.SMOKE_POWER_REPLICATES
    control_replicates: int = plan.SMOKE_CONTROL_REPLICATES

    @property
    def is_full(self) -> bool:
        return self.mode == FULL


# ---------------------------------------------------------------------------
# Deterministic controls -- exact, complete in both modes
# ---------------------------------------------------------------------------

def deterministic_controls() -> list[dict]:
    """Run every control whose expected outcome is exact."""
    out: list[dict] = []
    K0 = nm.mat([[100.0, 0.0], [0.0, 100.0]])

    def rec(case_id, expected, observed, passed, **extra):
        out.append({
            "case_id": case_id, "expected": expected, "observed": observed,
            "passed": bool(passed), **extra,
        })

    # --- T11a realized-field controls -------------------------------------
    o = rf.qualify_temperature_field(rf.Enclosure.point(math.log(304.0 / 298.0)))
    rec("CTL-RF-TEMP-304", rf.OUT_OF_SPEC, o.status, o.status == rf.OUT_OF_SPEC,
        retained_fraction=o.retained_fraction,
        planning_detection=o.worst_case_planning_detection)

    m = rf.stiffness_log_modes(nm.scale(K0, 1.021), K0)
    o = rf.qualify_stiffness_field([rf.Enclosure.point(v) for v in m])
    rec("CTL-RF-STIFF-1021", rf.OUT_OF_SPEC, o.status, o.status == rf.OUT_OF_SPEC,
        retained_fraction=o.retained_fraction,
        planning_detection=o.worst_case_planning_detection)

    mm = rf.stiffness_log_modes(nm.mat([[190.0, 0.0], [0.0, 225.0]]), K0)
    o = rf.qualify_stiffness_field([rf.Enclosure.point(v) for v in mm])
    harmonic = 2.0 / (1.0 / 1.9 + 1.0 / 2.25)
    klo, khi = rf.stiffness_band()
    rec("CTL-RF-MODES", rf.OUT_OF_SPEC, o.status, o.status == rf.OUT_OF_SPEC,
        modes=[math.exp(v) for v in mm], harmonic_scalar=harmonic,
        harmonic_would_have_passed=bool(klo <= math.log(harmonic) <= khi))

    d = rf.ellipse_distance(nm.mat([[150.0, 0.0], [0.0, 60.0]]), K0)
    o = rf.qualify_ellipse_field(rf.Enclosure.point(d))
    rec("CTL-RF-ELLIPSE", rf.OUT_OF_SPEC, o.status, o.status == rf.OUT_OF_SPEC,
        distance=d, epsilon_2=rf.EPSILON_2)

    lo, hi = rf.temperature_band()
    o = rf.qualify_temperature_field(rf.Enclosure(lo * 0.99, hi * 1.01, "interval"))
    rec("CTL-RF-STRADDLE", rf.UNRESOLVED, o.status, o.status == rf.UNRESOLVED)

    o = rf.qualify_temperature_field(rf.Enclosure.point(rf.C_T_STAR))
    rec("CTL-RF-VALID", rf.VALID, o.status, o.status == rf.VALID,
        note="synthetic qualification only; no physical packet is asserted VALID")

    # --- axial coupling control -------------------------------------------
    k3 = plan.nominal_k3(0, coupling=0.30)
    red = reduce_axial(k3, plan.T_REF)
    r = axial_ratio(k3)
    lb, gp = plane_block_bias(r)
    k_qq = [[k3[0][0], k3[0][1]], [k3[1][0], k3[1][1]]]
    used_schur = nm.max_abs(nm.sub(red.k_eff, k_qq)) > 0.0
    rec("CTL-AXIAL-COUPLE", "pipeline uses H_eff; K_qq bias quantified",
        f"r={r:.6f} log_beta_plane={lb:.6f} G_plane={gp:.6f}",
        used_schur and red.ok and abs(lb) > DELTA_A,
        axial_ratio=r, plane_log_beta_bias=lb, plane_geometry_bias=gp,
        exceeds_absolute_margin=bool(abs(lb) > DELTA_A),
        exceeds_shape_margin=bool(gp > DELTA_G))

    # --- axial temporal-memory control ------------------------------------
    red2 = reduce_axial(plan.nominal_k3(0), plan.T_REF, temporal_qualified=False)
    codes = {x.predicate for x in red2.refusals}
    rec("CTL-AXIAL-MEMORY", "TEMPORAL_MODEL_UNQUALIFIED or linked axial refusal",
        sorted(codes), "lateral temporal reduction qualified" in codes,
        note="no 3D hidden-state model is silently substituted")

    # --- optimiser failure control ----------------------------------------
    observed = []
    for label, fn, x0 in [
        ("NaN objective", lambda x: float("nan"), [0.0, 0.0]),
        ("inadmissible start", lambda x: float("inf"), [0.0, 0.0]),
        ("singular factorisation", lambda x: nm.cholesky(nm.mat([[1.0, 2.0], [2.0, 1.0]]))[0][0], [0.0]),
    ]:
        try:
            minimise(fn, x0)
            observed.append(f"{label}: NO REFUSAL")
        except OptimizerFailure:
            observed.append(f"{label}: OptimizerFailure")
    res = minimise(lambda x: sum(v * v for v in x), [0.0] * 3, max_evaluations=5)
    observed.append(f"budget exhausted: converged={res.converged}")
    rec("CTL-OPT-FAIL", "COMPUTATION_NOT_EVALUABLE; beta never fabricated", observed,
        all("OptimizerFailure" in o for o in observed[:3]) and not res.converged)

    return out


# ---------------------------------------------------------------------------
# Stochastic families
# ---------------------------------------------------------------------------

def _single_record_event(
    seed_map: SeedMap, family: str, case_id: str, rep: int, b_true: float,
    frames: int, **spec_kw,
) -> tuple[bool, bool, dict]:
    """Return ``(false_equivalence_event, evaluable, detail)`` for one outer experiment."""
    specs = design_specs(n_frames=frames, **spec_kw)
    spec, h_locked = specs[0]
    spec = type(spec)(**{**spec.__dict__, "beta_true": math.exp(b_true)})
    stream = seed_map.stream(family, case_id, rep)
    out = run_record(spec, h_locked, stream)
    if not out.evaluable or out.log_beta is None or out.se is None:
        return False, False, {"reason": out.reason}
    interval = build_interval(out.log_beta, out.se, NORMAL_CRITICAL, plan.BIAS_PER_CELL)
    return interval.strictly_inside(DELTA_A), True, {
        "b_hat": out.log_beta, "se": out.se, "lo": interval.lo, "hi": interval.hi,
    }


def run_size_case(seed_map: SeedMap, case, reps: int, frames: int) -> dict:
    agg = Aggregator(case.case_id, "size", "cp_upper", 0.025)
    refused = 0
    t0 = time.time()
    b_true = case.detail.get("b_true")
    spec_kw: dict = {}
    if "noise_ratio" in case.detail:
        spec_kw["localization_ratio_target"] = case.detail["noise_ratio"]
    if b_true is None:
        # contrast and gate-boundary cases are not exercised by the single-record
        # size driver; they are declared NOT RUN rather than silently skipped.
        return {
            "case_id": case.case_id, "family": "size", "status": "NOT RUN",
            "reason": "requires the multi-record contrast or gate-boundary driver",
            "replicates_run": 0, "required": case.replicates,
        }
    for rep in range(reps):
        event, evaluable, _ = _single_record_event(
            seed_map, SIZE, case.case_id, rep, b_true, frames, **spec_kw
        )
        if not evaluable:
            refused += 1
        agg.add(event)
    res = agg.result({
        "b_true": b_true, "refused_or_nonevaluable": refused,
        "seconds": round(time.time() - t0, 1),
    })
    return res.as_dict()


def run_power_case(seed_map: SeedMap, case, reps: int, frames: int) -> dict:
    """Complete eight-record experiment: every record must pass every gate."""
    agg = Aggregator(case.case_id, "power", "cp_lower", 0.90)
    t0 = time.time()
    refused = 0
    for rep in range(reps):
        specs = design_specs(n_frames=frames)
        ok = True
        for idx, (spec, h_locked) in enumerate(specs):
            stream = seed_map.stream(POWER, case.case_id, rep * 100 + idx)
            out = run_record(spec, h_locked, stream)
            if not out.evaluable or out.log_beta is None:
                refused += 1
                ok = False
                break
            iv = build_interval(out.log_beta, out.se, NORMAL_CRITICAL, plan.BIAS_PER_CELL)
            if not iv.strictly_inside(DELTA_A):
                ok = False
                break
            if out.geometry is None or out.geometry >= DELTA_G:
                ok = False
                break
            if out.centre is None or out.centre >= DELTA_M:
                ok = False
                break
            if out.r_irr is None or out.r_irr >= DELTA_R_IRR:
                ok = False
                break
        agg.add(ok)
    res = agg.result({
        "refused_or_nonevaluable": refused,
        "note": "refusals remain in the denominator",
        "seconds": round(time.time() - t0, 1),
    })
    return res.as_dict()


def run_control_case(seed_map: SeedMap, case, reps: int, frames: int) -> dict:
    """Stochastic negative controls: record what the pipeline actually does."""
    t0 = time.time()
    kw: dict = {}
    beta = 1.0
    if case.case_id == "CTL-COMMON-07":
        beta = 0.7
    if case.case_id == "CTL-CURRENT":
        kw["omega"] = case.detail.get("omega", 0.05)
    if case.case_id == "CTL-DRIFT":
        kw["drift_rate"] = (2.0e-7, 0.0)
    if case.case_id in ("CTL-NOISE-HEAVY", "CTL-NOISE-COLOR", "CTL-NOISE-STATE"):
        kw["noise_model"] = {"CTL-NOISE-HEAVY": "heavy", "CTL-NOISE-COLOR": "colored",
                             "CTL-NOISE-STATE": "state_dependent"}[case.case_id]
    if case.case_id == "CTL-NOISE-HI":
        kw["localization_ratio_target"] = 0.25
    counts = {"support": 0, "absolute_fail": 0, "geometry_fail": 0, "centre_fail": 0,
              "current_fail": 0, "nonevaluable": 0}
    blind_err: list[float] = []
    for rep in range(reps):
        specs = design_specs(n_frames=frames, **kw)
        spec, h_locked = specs[0]
        if beta != 1.0:
            spec = type(spec)(**{**spec.__dict__, "beta_true": beta})
        if case.case_id == "CTL-GEOM-TRACE":
            vals, Q = nm.eigh(h_locked)
            h_locked = nm.symmetrise(nm.matmul(nm.matmul(
                Q, [[vals[0] * 1.6, 0.0], [0.0, vals[1] / 1.6]]), nm.transpose(Q)))
        if case.case_id == "CTL-GEOM-ROT":
            theta = math.pi / 5.0
            R = nm.mat([[math.cos(theta), -math.sin(theta)], [math.sin(theta), math.cos(theta)]])
            base = nm.mat([[spec.h_true[0][0] * 1.5, 0.0], [0.0, spec.h_true[1][1] / 1.5]])
            spec = type(spec)(**{**spec.__dict__, "h_true": nm.symmetrise(
                nm.matmul(nm.matmul(R, base), nm.transpose(R)))})
            h_locked = base
        if case.case_id == "CTL-BLUR-MISMATCH":
            spec = type(spec)(**{**spec.__dict__, "generate_t_exp": spec.dt * 0.9})
        c = case.detail.get("c")
        if c is not None:
            h_locked = nm.scale(h_locked, c)
        stream = seed_map.stream(CONTROL, case.case_id, rep)
        out = run_record(spec, h_locked, stream)
        if not out.evaluable or out.log_beta is None:
            counts["nonevaluable"] += 1
            continue
        if c is not None:
            blind_err.append(out.log_beta + math.log(c))
        iv = build_interval(out.log_beta, out.se, NORMAL_CRITICAL, plan.BIAS_PER_CELL)
        abs_ok = iv.strictly_inside(DELTA_A)
        geo_ok = out.geometry is not None and out.geometry < DELTA_G
        cen_ok = out.centre is not None and out.centre < DELTA_M
        cur_ok = out.r_irr is not None and out.r_irr < DELTA_R_IRR
        if not abs_ok:
            counts["absolute_fail"] += 1
        if not geo_ok:
            counts["geometry_fail"] += 1
        if not cen_ok:
            counts["centre_fail"] += 1
        if not cur_ok:
            counts["current_fail"] += 1
        if abs_ok and geo_ok and cen_ok and cur_ok:
            counts["support"] += 1
    detail: dict = {"counts": counts, "replicates": reps,
                    "seconds": round(time.time() - t0, 1)}
    evaluated = reps - counts["nonevaluable"]
    if evaluated > 0:
        detail["false_support_cp_upper"] = clopper_pearson_upper(counts["support"], evaluated)
    if blind_err:
        detail["blinded_recovery_mean_error"] = sum(blind_err) / len(blind_err)
        detail["blinded_recovery_max_abs_error"] = max(abs(v) for v in blind_err)
    return {"case_id": case.case_id, "family": "control",
            "expectation": case.expectation, **detail}
