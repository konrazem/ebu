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

Every stochastic case goes through the same three objects and no others:
:func:`~e1a_v5.validation.dispatch.instantiate` builds the declared world,
:func:`~e1a_v5.pipeline.complete_pipeline_result` judges it, and
:func:`~e1a_v5.validation.events.evaluate_event` decides whether the
replicate counted.  No raw statistic is compared against a tolerance here.
"""

from __future__ import annotations

import json
import math
import time
from dataclasses import dataclass
from typing import Any, Callable, Mapping, Sequence

from .. import numerics as nm
from .. import realization as rf
from ..calibration import (
    REQUIRED_PRIMITIVE_CATEGORIES,
    combined_contrast_standard_error,
    combined_standard_error,
)
from ..confidence import (
    BIAS_ABS_MAX,
    BIAS_CONTRAST_MAX,
    DELTA_A,
    DELTA_C,
    CEILING_PASS,
    CriticalValues,
    Interval,
    NORMAL_CRITICAL,
    build_interval,
    synthetic_calibrated,
)
from ..diagnostics import (
    DiagnosticFamilyResult,
    NullScales,
    RecordDiagnostic,
    evaluate_diagnostic_family,
)
from ..evidence import (
    BiasEvidence,
    ContrastKey,
    GateCalibrationReceipt,
    GateExpectations,
    GateFamily,
    GateLimit,
    RecordKey,
    SyntheticGateFixture,
    synthetic_calibrated_gate_fixture,
)
from ..gates import DELTA_G, DELTA_M, DELTA_R_IRR
from ..numerics import NumericalFailure, clopper_pearson_lower, clopper_pearson_upper
from ..optimize import OptimizerFailure, minimise
from ..observation import LOCALIZATION_RATIO_CEILING, localization_ratio
from ..packets import CONTRASTS, RECORDS, BlockId, FieldId
from ..pipeline import (
    ContrastResultV4,
    DELTA_STATIONARITY,
    RecordResultV4,
    complete_pipeline_result,
)
from ..realization import FIELD_REALIZATION_VALID
from ..generate import axial_memory_dynamics
from ..reduction import (
    AxialEvidence, FiniteRemainderEffects, axial_ratio, schur_complement,
    normalise_covariance_to_h, plane_block_bias,
    propagate_schur_covariance, reduce_axial,
)
from ..refusals import (
    CALIBRATION_UNCERTAINTY_EXCESS, INCOMPLETE_INPUT, TEMPORAL_MODEL_UNQUALIFIED,
    Refusal, refuse,
)
from ..rng import Stream, derive_seed
from ..units import K_B
from ..seeds import CALIBRATION, CONTROL, DIAGNOSTIC, ENGINEERING, POWER, SIZE, SeedMap
from . import plan
from .cases import ALL_CASES, CASES_BY_ID, ExpectedEvent, ValidationCaseV4
from .dispatch import (
    CaseInstantiation,
    InvalidValidationPlan,
    apply_geometry,
    apply_selection,
    instantiate,
)
from .events import (
    EVENT_EVALUATOR_VERSION,
    EventNotEvaluable,
    ReasonAggregate,
    ReplicateOutcome,
    evaluate_event,
)
from .harness import (
    Aggregator,
    TEMPORAL_QUALIFIED,
    auxiliary_measurement,
    axial_effects,
    design_evidence,
    measured_analysis_spec,
    observation_envelope,
    temporal_qualification,
    true_system,
    axial_memory_specs,
    axial_memory_witness,
    current_control_drift,
    design_specs,
    experiment_calibration,
    run_axial_memory_record,
    run_record,
)

SMOKE = "smoke"
FULL = "full"

#: Label stamped on every artefact that used an injected synthetic calibrated
#: critical value to exercise verdict code.  Such a result is an engineering
#: check and can never be a validation outcome.
SYNTHETIC_CALIBRATION_LABEL = (
    "SYNTHETIC CALIBRATED CRITICAL VALUES INJECTED - ENGINEERING CHECK ONLY"
)


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
    """Run every control whose expected outcome is exact.

    Keyed by the dispatcher's ``deterministic_key``, so the registry and this
    battery cannot drift apart: :func:`deterministic_coverage` checks that
    every case routed here has a handler.
    """
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
    inst = instantiate("CTL-AXIAL-COUPLE")
    coupling = float(inst.spec_kwargs["coupling"])
    k3 = plan.nominal_k3(0, coupling=coupling)
    r = axial_ratio(k3)
    lb, gp = plane_block_bias(r)
    k_qq = [[k3[0][0], k3[0][1]], [k3[1][0], k3[1][1]]]
    red = reduce_axial(
        k3, plan.T_REF,
        evidence=design_evidence(k3, plan.T_REF),
        c_v=nm.scale(nm.eye(6), (plan.PRIMITIVE_RELATIVE_SIGMA * plan.K_REF) ** 2))
    used_schur = nm.max_abs(nm.sub(red.k_eff, k_qq)) > 0.0
    rec("CTL-AXIAL-COUPLE", "pipeline uses H_eff; K_qq bias quantified",
        f"r={r:.6f} log_beta_plane={lb:.6f} G_plane={gp:.6f}",
        used_schur and red.ok and abs(lb) > DELTA_A,
        declared_coupling=coupling,
        axial_ratio=r, plane_log_beta_bias=lb, plane_geometry_bias=gp,
        exceeds_absolute_margin=bool(abs(lb) > DELTA_A),
        exceeds_shape_margin=bool(gp > DELTA_G))

    # --- Branch-A temporal-model qualification, DERIVED --------------------
    # V5 set ``temporal_reduction_qualified=False`` by hand here, which
    # exercises the refusal path and not the physics.  The flag is gone: the
    # ordinary qualification machinery now MEASURES a driven response and
    # derives the answer, and this reference shows it deriving both answers
    # from the two worlds.
    from .harness import (
        axial_memory_specs, axial_memory_witness, temporal_qualification,
        true_system, TEMPORAL_QUALIFIED, TEMPORAL_UNQUALIFIED,
    )
    from ..generate import axial_memory_dynamics as _amd
    nominal_spec, nominal_h = design_specs(n_frames=16)[0]
    a_nom, sigma_nom = true_system(nominal_spec)
    q_nom = temporal_qualification(
        a_nom, sigma_nom,
        nm.scale(nominal_spec.h_true, K_B * plan.T_REF),
        nominal_spec.p_matrix, nominal_spec.r_obs, nominal_spec.b_det,
        Stream(derive_seed(ENGINEERING, "REF-TEMPORAL", "nominal"),
               label="ref/temporal/nominal"),
    )
    mem_spec = axial_memory_specs(n_frames=16)[0][0]
    a_mem, sigma_mem = _amd(mem_spec)
    q_mem = temporal_qualification(
        a_mem, sigma_mem, schur_complement(mem_spec.k3),
        mem_spec.p_matrix, mem_spec.r_obs, mem_spec.b_det,
        Stream(derive_seed(ENGINEERING, "REF-TEMPORAL", "memory"),
               label="ref/temporal/memory"),
    )
    rec("REF-TEMPORAL-QUALIFICATION",
        "the measured response qualifies a 2D world and excludes a 3D one",
        {"nominal": q_nom, "hidden_memory": q_mem},
        q_nom["status"] == TEMPORAL_QUALIFIED
        and q_mem["status"] == TEMPORAL_UNQUALIFIED,
        note="no flag is supplied anywhere. For EVERY 2D linear generator the "
             "mean response is a semigroup, R(2t) = R(t)^2, so a measured "
             "violation beyond the measurement's own 5-sigma error excludes "
             "the whole admissible 2D class without fitting anything.")

    # --- the axial-memory WITNESS, established before any replicate ---------
    w = axial_memory_witness(axial_memory_specs(n_frames=16)[0][0])
    rec("REF-AXIAL-MEMORY-WITNESS",
        "lateral density matches Schur while the 2D Markov closure fails",
        w,
        bool(w["k3_spd"]) and bool(w["schur_spd"])
        and w["lateral_marginal_relative_error"] < 1e-12
        and w["worst_markov_closure_residual"] > 1e-3,
        note="the Chapman-Kolmogorov identity C(2t) = C(t) Sigma^-1 C(t) holds "
             "for EVERY 2D Markov generator, so a nonzero residual proves no "
             "admissible 2D temporal model reproduces this lateral path")

    # --- observation comparison is in DETECTOR coordinates ------------------
    # The auditor's case.  The latent covariance is the identity, the detector
    # map shrinks it a hundredfold, and the localisation noise is 1% of the
    # LATENT scale -- which is 100% of what the detector actually sees.
    sig_i, p_small = nm.eye(2), nm.scale(nm.eye(2), 0.1)
    r_small = nm.scale(nm.eye(2), 0.01)
    detector_ratio = localization_ratio(sig_i, r_small, p_small)
    latent_only = localization_ratio(sig_i, r_small, nm.eye(2))
    rec("REF-OBS-DETECTOR-COORDS",
        "P enters the localisation ratio; the P = 0.1 I case FAILS",
        {"detector_coordinate_ratio": detector_ratio,
         "latent_only_ratio_v5_would_report": latent_only,
         "ceiling": LOCALIZATION_RATIO_CEILING},
        abs(detector_ratio - 1.0) < 1e-12
        and detector_ratio > LOCALIZATION_RATIO_CEILING
        and latent_only <= LOCALIZATION_RATIO_CEILING,
        note="S_y = P Sigma P^T, so r_loc = lambda_max(S_y^-1/2 R S_y^-1/2) = 1.0. "
             "V5 compared against the latent Sigma and reported 0.01, which "
             "passes. Both the P = I and the nontrivial P cases are regressed.")

    # --- the joint 99.9% physical calibration region ------------------------
    region = plan.default_joint_region()
    rec("REF-JOINT-REGION",
        "a joint region with a GUARANTEED coverage, not a marginal 3 sigma",
        region.as_dict(),
        region.joint_coverage >= 0.999
        and abs(region.total_noncoverage - 0.001) < 1e-12
        and len(region.categories) == len(REQUIRED_PRIMITIVE_CATEGORIES),
        note="allocated noncoverage per primitive, intersected; the union "
             "bound makes the joint coverage valid for ANY dependence "
             "structure, so the declared shared thermometry latent is "
             "retained rather than being assumed away")

    # --- omitted eta/T covariance control ----------------------------------
    # Exact: the same primitive uncertainties propagate to two different
    # C_vech(H_eff) depending on whether the shared temperature covariance is
    # carried.  Dropping it does not merely change a number, it removes a
    # negative cross term, so the omitted version UNDERSTATES the uncertainty
    # and its intervals undercover.
    k3_eta = plan.nominal_k3(0)
    c_v_eta = nm.scale(nm.eye(6), (1e-3 * plan.K_REF) ** 2)
    var_log_t = (1.0e-3) ** 2
    c_s, _ = propagate_schur_covariance(k3_eta, c_v_eta)
    k_eff_eta = schur_complement(k3_eta)
    kbt = K_B * plan.T_REF
    h_vech = [k_eff_eta[0][0] / kbt, k_eff_eta[0][1] / kbt, k_eff_eta[1][1] / kbt]
    # The shared part: dS and dlogT both move with the same temperature.
    cov_s_logt = [0.9 * math.sqrt(max(c_s[i][i], 0.0) * var_log_t) for i in range(3)]
    with_cov = normalise_covariance_to_h(
        k_eff_eta, c_s, plan.T_REF, var_log_t, cov_s_logt)
    without = normalise_covariance_to_h(
        k_eff_eta, c_s, plan.T_REF, var_log_t, None)
    ratio = [
        math.sqrt(with_cov[i][i]) / math.sqrt(without[i][i]) for i in range(3)
    ]
    rec("REF-ETA-T-COV-ALGEBRA", "the two propagations differ",
        {"sigma_ratio_with_over_without": ratio},
        all(r != 1.0 for r in ratio),
        note="SUPPLEMENTARY exact reference, not the CTL-ETA-T-COV control. "
             "It shows only that the two covariance propagations differ. V4 "
             "additionally asserted a universal SIGN for the effect of "
             "omitting the covariance; its own ratios (0.327, 1.005, 0.317) "
             "contradict any universal sign, so no such claim is made.")

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


def deterministic_coverage() -> tuple[set[str], set[str]]:
    """``(routed_to_deterministic, handled_by_the_battery)``."""
    routed = {
        c.case_id for c in ALL_CASES
        if instantiate(c.case_id).driver == "deterministic"
    }
    handled = {r["case_id"] for r in deterministic_controls()}
    return routed, handled


# ---------------------------------------------------------------------------
# Building one record's typed result
# ---------------------------------------------------------------------------

#: The V-stage procedure version this build implements.  A calibration
#: receipt from another version does not apply to these records.
PROCEDURE_VERSION = 6
#: Identity of the nuisance/domain envelope these records are qualified in.
DOMAIN_IDENTITY = "e1a_v5_candidate_2026-10-06/nominal-envelope"

#: Live V6 state: finite-N calibration has NOT run, so NO production
#: GateCalibrationReceipt exists for any family and every gate is
#: UNCALIBRATED.  That is the expected state, not a defect.  Complete support
#: is therefore unavailable outside explicitly marked test fixtures.
NO_GATE_RECEIPTS: Mapping[GateFamily, GateCalibrationReceipt] = {}


def gate_expectations(
    domain_identity: str = DOMAIN_IDENTITY,
    coverage_target: float = 0.975,
) -> GateExpectations:
    """The CURRENT frozen identities a production gate receipt must match."""
    from ..identity import compute_identities
    from ..seeds import CALIBRATION
    from .contract import plan_identity
    ids = compute_identities(plan.IDENTITY_CONFIGURATION)
    return GateExpectations(
        procedure_version=PROCEDURE_VERSION,
        analysis_identity=ids.analysis,
        validation_identity=ids.validation,
        plan_identity=plan_identity(),
        seed_map_identity=ids.seed_map,
        domain_identity=domain_identity,
        coverage_target=coverage_target,
        calibration_seed_namespace=CALIBRATION,
    )


def build_record_result(
    block: BlockId,
    fld: FieldId,
    out,
    calibration,
    critical: CriticalValues = NORMAL_CRITICAL,
    gate_receipts: Mapping[GateFamily, GateCalibrationReceipt] | None = None,
    axial: FiniteRemainderEffects | None = None,
    gate_fixtures: Mapping[GateFamily, SyntheticGateFixture] | None = None,
    domain_identity: str = DOMAIN_IDENTITY,
    temporal: Mapping[str, object] | None = None,
) -> RecordResultV4:
    """Translate a harness RecordOutcome into the typed pipeline result.

    Three V5 repairs land here.

    *Observation validity is evaluated, not asserted.*  It comes from
    :func:`~e1a_v5.observation.qualify_observation`, which checks the T 15.2 /
    T.23 localisation ceiling, the exposure and bandwidth envelopes, the noise
    model and the invertibility of the detector map.  V4 passed
    ``observation_valid=True`` unconditionally.

    *Gate limits come from a VERIFIED calibration receipt.*  Each is built by
    :meth:`GateLimit.from_receipt`, which recomputes the receipt's digest and
    compares the gate family, the procedure version and the analysis,
    validation, plan, seed-map and domain identities against the running
    procedure's own.  Test fixtures are a different TYPE with a different
    constructor, so no production call can be made to accept one.  There is no
    constructor that accepts a limit, so a raw statistic cannot become one.

    *The axial remainder's EXACT finite effects are routed into the existing
    budgets.*  The scale effect enlarges the per-record bounded bias, the
    geometry effect enlarges the T4 shape limit, the centre effect multiplies
    the centre limit, and the rate effect already enlarged the observation
    envelope inside the harness.  No budget of its own.
    """
    key = RecordKey(block, fld)
    name = str(key)
    reasons: list[Refusal] = list(out.reasons)
    receipts = NO_GATE_RECEIPTS if gate_receipts is None else gate_receipts
    fixtures = gate_fixtures or {}
    expected = gate_expectations(domain_identity)

    obs = out.observation
    observation_valid = None if obs is None else bool(obs.valid)

    # Branch-A temporal-model qualification, DERIVED from the independently
    # measured response.  V5 had no production path that measured it at all:
    # the only place the flag was ever set was one deterministic control that
    # set it by hand.  A record with no measurement is unqualified, because a
    # missing qualification is not a qualification.
    if temporal is None or temporal.get("status") != TEMPORAL_QUALIFIED:
        reasons.append(refuse(
            TEMPORAL_MODEL_UNQUALIFIED,
            "a 2D temporal model represents the measured response",
            "the independently measured response is not reproduced by any "
            "admissible 2D generator within the measurement's own error"
            if temporal is not None else
            "no independent response measurement was made for this record",
            record=name,
            **({} if temporal is None else {
                "temporal_status": temporal.get("status"),
                "semigroup_residual": temporal.get("semigroup_residual"),
                "band": temporal.get("band"),
                "response_lag": temporal.get("tau"),
            }),
        ))

    if not out.evaluable or out.log_beta is None or out.se is None:
        return RecordResultV4(
            key=key, embedded_key=key, evaluable=False,
            observation_valid=observation_valid, reasons=tuple(reasons),
        )

    cal_sigma = calibration.absolute_sigma(name)
    if calibration.absolute_qualification(name) != CEILING_PASS:
        reasons.append(refuse(
            CALIBRATION_UNCERTAINTY_EXCESS,
            "absolute calibration standard uncertainty <= 0.009",
            "the certified enclosure does not establish the endpoint is "
            "inside its U.23 ceiling",
            record=name, sigma=cal_sigma.point,
            classification=calibration.absolute_qualification(name),
        ))
    se_total = combined_standard_error(out.se, cal_sigma.point)

    axial_bias = 0.0 if axial is None else axial.log_beta_bias
    axial_geometry = 0.0 if axial is None else axial.geometry
    axial_centre = 1.0 if axial is None else axial.centre_factor
    if axial is None:
        reasons.append(refuse(
            INCOMPLETE_INPUT, "certified axial remainder effects supplied",
            "no exact finite axial-remainder effects were established for "
            "this record; a missing bound is not a bound of zero",
            record=name,
        ))
        bias = BiasEvidence.missing("no certified axial remainder effects")
    else:
        bias = BiasEvidence.qualified(
            plan.BIAS_PER_CELL + axial_bias,
            source="design-point T.18 budget plus the EXACT finite effect of "
                   "the certified axial remainder set",
        )
    # T.18 / U.22: the absolute bounded log-beta bias ceiling is 0.0005, and
    # it is a QUALIFICATION PREDICATE, not a figure to report.  V5 computed
    # the bound, carried it into the interval and never compared it against
    # anything, so a design point whose bounded bias exceeded the ceiling was
    # labelled qualified.  Comparison is inclusive, as everywhere else.
    if bias.usable and not (abs(bias.require()) <= BIAS_ABS_MAX):
        reasons.append(refuse(
            CALIBRATION_UNCERTAINTY_EXCESS,
            f"absolute bounded log-beta bias <= {BIAS_ABS_MAX}",
            "the record's certified bounded bias exceeds its T.18 / U.22 "
            "ceiling",
            record=name, bias_bound=bias.require(), ceiling=BIAS_ABS_MAX,
            design_point_budget=plan.BIAS_PER_CELL,
            axial_remainder_contribution=axial_bias,
        ))
    interval = (
        build_interval(out.log_beta, se_total, critical, bias.require())
        if bias.usable else None
    )

    from ..evidence import ScientificInterval
    sci = None if interval is None else ScientificInterval(
        interval=interval, estimate=out.log_beta, standard_error=se_total,
        critical=critical, bias_bound=bias.require(),
    )

    def limit(stat: float | None, family: GateFamily) -> GateLimit:
        # Production first.  A fixture is only reachable through the separate
        # TYPE and the separate constructor, so no production call can be
        # talked into accepting one.
        if family in receipts:
            return GateLimit.from_receipt(stat, receipts[family], family, expected)
        if family in fixtures:
            return GateLimit.from_fixture(stat, fixtures[family], family)
        return GateLimit.uncalibrated(stat)

    return RecordResultV4(
        key=key, embedded_key=key,
        branch_a_valid=True,           # synthetic packet, qualified by construction
        observation_valid=observation_valid,
        realization_status=FIELD_REALIZATION_VALID,
        log_beta=out.log_beta, log_beta_se=se_total, absolute=sci,
        absolute_bias=bias,
        shape=limit(out.geometry, GateFamily.SHAPE).enlarged(axial_geometry),
        centre=limit(out.centre, GateFamily.CENTRE).scaled(axial_centre),
        stationarity=limit(out.stationarity, GateFamily.STATIONARITY),
        current=limit(out.r_irr, GateFamily.CURRENT),
        evaluable=True,
        reasons=tuple(reasons),
    )


def build_contrast_results(
    records: Sequence[RecordResultV4],
    calibration,
    critical: CriticalValues = NORMAL_CRITICAL,
) -> list[ContrastResultV4]:
    """The six within-block contrasts, from the SAME joint covariance.

    ``C_d = D C_b D^T`` is formed by differencing the sensitivity rows before
    contracting with ``C_phi``, which is algebraically identical and keeps
    every shared-primitive cancellation exact.  Recomputing a contrast from
    two independent absolute uncertainties would discard the off-diagonal
    blocks and inflate it by up to sqrt(2).
    """
    # Collected as a LIST per identity, not a map: a duplicate record must not
    # disappear behind its twin here either, even though the evidence layer
    # already refuses the experiment.
    grouped: dict[RecordKey, list[RecordResultV4]] = {}
    for r in records:
        grouped.setdefault(r.key, []).append(r)

    def unique(key: RecordKey) -> RecordResultV4 | None:
        got = grouped.get(key, [])
        return got[0] if len(got) == 1 else None

    out: list[ContrastResultV4] = []
    from ..evidence import ScientificInterval
    for blk, fld in CONTRASTS:
        key = ContrastKey(blk, fld)
        a = unique(RecordKey(blk, fld))
        b = unique(RecordKey(blk, FieldId.THETA0))
        if a is None or b is None or a.log_beta is None or b.log_beta is None:
            out.append(ContrastResultV4(key=key))
            continue
        name_a, name_b = str(a.key), str(b.key)
        cal_sigma = calibration.contrast_sigma(name_a, name_b)
        reasons: list[Refusal] = []
        if calibration.contrast_qualification(name_a, name_b) != CEILING_PASS:
            reasons.append(refuse(
                CALIBRATION_UNCERTAINTY_EXCESS,
                "contrast calibration standard uncertainty <= 0.003",
                "the certified enclosure does not establish the contrast is "
                "inside its U.24 ceiling",
                contrast=str(key), sigma=cal_sigma.point,
            ))
        cond_a = a.absolute.standard_error if a.absolute else None
        cond_b = b.absolute.standard_error if b.absolute else None
        if cond_a is None or cond_b is None:
            out.append(ContrastResultV4(key=key, reasons=tuple(reasons)))
            continue
        se = combined_contrast_standard_error(cond_a, cond_b, cal_sigma.point)
        # Jointly computed: the two records' certified remainder sets are
        # independent certifications, so the contrast carries the sum of their
        # EXACT finite contrast effects.  Never inferred from two absolute
        # bounds.
        bias = BiasEvidence.qualified(
            2.0 * plan.BIAS_PER_CELL
            + axial_effects(fld.index).contrast_bias
            + axial_effects(0).contrast_bias,
            source="jointly computed contrast bias, from the exact finite "
                   "effects of both records' certified remainder sets",
        )
        # The within-block contrast ceiling is its own predicate on its own
        # jointly computed bound, never inferred from two absolute bounds.
        if bias.usable and not (abs(bias.require()) <= BIAS_CONTRAST_MAX):
            reasons.append(refuse(
                CALIBRATION_UNCERTAINTY_EXCESS,
                f"within-block contrast bounded bias <= {BIAS_CONTRAST_MAX}",
                "the contrast's jointly computed bounded bias exceeds its "
                "T.18 / U.22 ceiling",
                contrast=str(key), bias_bound=bias.require(),
                ceiling=BIAS_CONTRAST_MAX,
            ))
        est = a.log_beta - b.log_beta
        iv = build_interval(est, se, critical, bias.require())
        out.append(ContrastResultV4(
            key=key,
            interval=ScientificInterval(
                interval=iv, estimate=est, standard_error=se,
                critical=critical, bias_bound=bias.require(),
            ),
            bias=bias,
            reasons=tuple(reasons),
        ))
    return out


#: Frozen null scales injected ONLY by the deterministic fixture path, so the
#: verdict code past the uncalibrated gate can be exercised.  These are not a
#: calibration and are labelled as such in every artefact that uses them.
SYNTHETIC_NULL_SCALES = NullScales(1.0, 1.0, 1.0, 1.0)
SYNTHETIC_DIAGNOSTIC_CRITICAL = 1.0e9
SYNTHETIC_DIAGNOSTIC_IDENTITY = "SYNTHETIC FIXTURE - not a calibration"


def build_diagnostic_family(
    per_record: Sequence[tuple[str, object, str]],
    fixture: bool = False,
) -> DiagnosticFamilyResult:
    """Derive the ONE authoritative family result from the record components.

    No finite-N diagnostic calibration exists for V4, so this returns
    UNCALIBRATED whenever the components are complete, and NOT_EVALUABLE when
    any is missing.  Neither can take part in a supported verdict, which is
    the correct state of the procedure: raw components existing is not a
    family that passed.
    """
    diags = [
        RecordDiagnostic(record=name, components=comp, rejected=None, reason=reason)
        for name, comp, reason in per_record
    ]
    expected = [f"{b.value}/{f.value}" for b, f in RECORDS]
    if fixture:
        return evaluate_diagnostic_family(
            diags, expected, scales=SYNTHETIC_NULL_SCALES,
            critical_value=SYNTHETIC_DIAGNOSTIC_CRITICAL,
            critical_identity=SYNTHETIC_DIAGNOSTIC_IDENTITY,
        )
    return evaluate_diagnostic_family(
        diags, expected, scales=None, critical_value=None, critical_identity="",
    )


# ---------------------------------------------------------------------------
# Complete eight-record experiments
# ---------------------------------------------------------------------------

def run_complete_experiment(
    seed_map: SeedMap,
    case: ValidationCaseV4,
    inst: CaseInstantiation,
    rep: int,
    frames: int,
    namespace: str | None = None,
    critical: CriticalValues = NORMAL_CRITICAL,
    gate_receipts: Mapping[GateFamily, GateCalibrationReceipt] | None = None,
    gate_fixtures: Mapping[GateFamily, SyntheticGateFixture] | None = None,
    fixture: bool = False,
):
    """Run one complete eight-record experiment through the ONE path.

    This function does NOT decide success.  It assembles typed results and
    hands them to :func:`complete_pipeline_result`, which is the single
    authoritative predicate.
    """
    ns = namespace or case.seed_namespace
    calibration = experiment_calibration(
        inst.spec_kwargs, omit_eta_t_covariance=inst.omit_eta_t_covariance,
    )
    if inst.axial_memory:
        specs = axial_memory_specs(
            n_frames=frames,
            localization_ratio_target=float(inst.spec_kwargs.get(
                "localization_ratio_target", plan.LOCALIZATION_RATIO_NOMINAL)),
        )
    else:
        specs = design_specs(n_frames=frames, **inst.spec_kwargs)
    # CTL-ETA-T-COV draws FRESH auxiliary measurements from the declared
    # generating law, shared thermometry latent included, and the analyst
    # locks in exactly what those measurements say.  The misspecification is
    # that the analyser's C_phi omits the shared latent; the data do not.
    measured = None
    aux_phi: list[float] = []
    if inst.omit_eta_t_covariance:
        aux_stream = Stream(
            seed_map.replicate_seed(ns, case.case_id + "/auxiliary", rep),
            label=f"{ns}/{case.case_id}/{rep}/auxiliary",
        )
        _vec, aux_phi, measured = auxiliary_measurement(inst.spec_kwargs, aux_stream)
    records: list[RecordResultV4] = []
    diag_inputs: list[tuple[str, object, str]] = []
    temporal_records: list[dict] = []
    seeds: list[int] = []
    for idx, (pair, (block, fld)) in enumerate(zip(specs, RECORDS)):
        spec, h_locked = pair
        axial = axial_effects(
            fld.index,
            coupling=float(inst.spec_kwargs.get("coupling", plan.AXIAL_COUPLING)),
            condition_target=inst.spec_kwargs.get("condition_target"),
        ) if not inst.axial_memory else axial_effects(fld.index)
        if inst.geometry is not None and not inst.axial_memory:
            spec, h_locked = apply_geometry(inst.geometry, spec, h_locked)
        if inst.blind_scale is not None:
            h_locked = nm.scale(h_locked, inst.blind_scale)
        seed = seed_map.replicate_seed(ns, case.case_id, rep * 100 + idx)
        seeds.append(seed)
        stream = Stream(seed, label=f"{ns}/{case.case_id}/{rep}/{idx}")
        analysis_spec = spec
        if measured is not None:
            fm = measured[idx][1]
            h_locked = fm.h_eff
            analysis_spec = measured_analysis_spec(spec, fm)
        envelope = observation_envelope(
            h_locked, plan.nominal_temperature(fld.index), analysis_spec,
            axial.rho)
        # The Branch-A response measurement is independent of the Branch-B
        # record: its own prepared releases, its own stream, and the TRUE
        # physical system -- three modes where a hidden axial mode exists.
        response_stream = stream.spawn("branch-a-response")
        if inst.axial_memory:
            a_full, sigma_full = axial_memory_dynamics(spec)
            k_for_tau = schur_complement(spec.k3)
        else:
            a_full, sigma_full = true_system(spec)
            k_for_tau = nm.scale(
                spec.h_true, K_B * plan.nominal_temperature(fld.index))
        try:
            temporal = temporal_qualification(
                a_full, sigma_full, k_for_tau, spec.p_matrix, spec.r_obs,
                spec.b_det, response_stream,
            )
        except NumericalFailure as exc:
            temporal = {"status": "MEASUREMENT_FAILED", "error": str(exc)}
        if inst.axial_memory:
            out = run_axial_memory_record(
                spec, h_locked, stream, envelope=envelope,
                analysis_spec=analysis_spec)
        else:
            out = run_record(spec, h_locked, stream, envelope=envelope,
                             analysis_spec=analysis_spec)
        records.append(build_record_result(
            block, fld, out, calibration, critical, gate_receipts, axial,
            gate_fixtures=gate_fixtures, temporal=temporal,
        ))
        temporal_records.append({"record": f"{block.value}/{fld.value}", **temporal})
        diag_inputs.append((
            f"{block.value}/{fld.value}", out.diagnostic, out.reason,
        ))
    contrasts = build_contrast_results(records, calibration, critical)
    family = build_diagnostic_family(diag_inputs, fixture=fixture)
    result = complete_pipeline_result(records, contrasts, family)
    digest = inst.digest(specs if not inst.axial_memory else None)
    digest["temporal_qualification"] = temporal_records
    if inst.axial_memory:
        digest["axial_memory_witness"] = axial_memory_witness(specs[0][0])
    if inst.omit_eta_t_covariance:
        correct = experiment_calibration(inst.spec_kwargs)
        k = calibration.keys[0]
        ref = correct.keys[1]
        s_cor = correct.absolute_sigma(k).point
        s_mis = calibration.absolute_sigma(k).point
        c_cor = correct.contrast_sigma(ref, k).point
        c_mis = calibration.contrast_sigma(ref, k).point
        widths = [
            r.absolute.interval.width
            for r in result.records if r.absolute is not None
        ]
        digest["eta_t_covariance_consequence"] = {
            "sigma_abs_correct_shared_model": s_cor,
            "sigma_abs_omitted_covariance": s_mis,
            "sigma_abs_difference": s_mis - s_cor,
            "ratio_omitted_over_correct": s_mis / s_cor if s_cor else None,
            "sigma_contrast_correct_shared_model": c_cor,
            "sigma_contrast_omitted_covariance": c_mis,
            "sigma_contrast_difference": c_mis - c_cor,
            "absolute_interval_width_max": max(widths) if widths else None,
            "absolute_interval_width_min": min(widths) if widths else None,
            "classification": result.verdict.classification,
            "declared_correlation": plan.ETA_T_CORRELATION,
            "auxiliary_draw": {
                "drawn": True,
                "shared_latent": plan.LATENT_THERMOMETRY,
                "log_k_standard": aux_phi[0] if aux_phi else None,
                "log_T_standard": aux_phi[1] if len(aux_phi) > 1 else None,
            },
            "note": "the DIRECTION of the consequence is a property of this "
                    "primitive map, not a general rule; no universal claim is "
                    "made about the SIGN of the effect. This is MANDATORY "
                    "recorded output and is not the release criterion, which "
                    "is false complete support.",
        }
    return result, digest, seeds


def run_power_case(
    seed_map: SeedMap, case: ValidationCaseV4, reps: int, frames: int,
    critical: CriticalValues = NORMAL_CRITICAL,
    gate_receipts: Mapping[GateFamily, GateCalibrationReceipt] | None = None,
    gate_fixtures: Mapping[GateFamily, SyntheticGateFixture] | None = None,
    fixture: bool = False,
) -> dict:
    """Complete eight-record experiments, counted by the authoritative verdict."""
    inst = instantiate(case.case_id)
    if not inst.runnable:
        return _not_run(case, inst)
    agg = Aggregator(case.case_id, "power", "cp_lower", 0.90)
    reasons = ReasonAggregate(case.case_id)
    t0 = time.time()
    digest: dict = {}
    for rep in range(reps):
        result, digest, seeds = run_complete_experiment(
            seed_map, case, inst, rep, frames, critical=critical,
            gate_receipts=gate_receipts, gate_fixtures=gate_fixtures,
            fixture=fixture,
        )
        outcome = ReplicateOutcome.from_complete(
            case.case_id, rep, seeds[0], result, configuration=digest,
            optimizer_status=_worst_optimizer_status(result),
            realization_status=_realization_status(result),
            bandwidth_product=_bandwidth(digest),
        )
        reasons.add(outcome)
        agg.add(evaluate_event(case, outcome))
    res = agg.result({
        **reasons.as_dict(),
        "expected_event": case.expected_event.value,
        "configuration": digest,
        "note": "refusals remain in the denominator; success requires the "
                "authoritative verdict SUPPORTED_WITHIN_DECLARED_TOLERANCES",
        "seconds": round(time.time() - t0, 1),
    })
    return res.as_dict()


def run_control_case(
    seed_map: SeedMap, case: ValidationCaseV4, reps: int, frames: int,
    critical: CriticalValues = NORMAL_CRITICAL,
    gate_receipts: Mapping[GateFamily, GateCalibrationReceipt] | None = None,
    gate_fixtures: Mapping[GateFamily, SyntheticGateFixture] | None = None,
    fixture: bool = False,
) -> dict:
    """Stochastic negative controls, judged by the authoritative verdict.

    V3 computed "support" here from four raw statistics and discarded every
    structured reason.  Both are repaired: the event comes from
    :func:`evaluate_event`, and :class:`ReasonAggregate` keeps every
    per-replicate refusal alongside the histograms.
    """
    inst = instantiate(case.case_id)
    if not inst.runnable:
        return _not_run(case, inst)
    reasons = ReasonAggregate(case.case_id)
    t0 = time.time()
    events = 0
    digest: dict = {}
    for rep in range(reps):
        result, digest, seeds = run_complete_experiment(
            seed_map, case, inst, rep, frames, critical=critical,
            gate_receipts=gate_receipts, gate_fixtures=gate_fixtures,
            fixture=fixture,
        )
        extra: dict = {
            "optimizer_status": _worst_optimizer_status(result),
            "realization_status": _realization_status(result),
            "bandwidth_product": _bandwidth(digest),
        }
        if inst.blind_scale is not None:
            lb = next((r.log_beta for r in result.records if r.log_beta is not None), None)
            extra["blinded_error"] = (
                None if lb is None else lb + math.log(inst.blind_scale)
            )
        outcome = ReplicateOutcome.from_complete(
            case.case_id, rep, seeds[0], result, configuration=digest, **extra,
        )
        reasons.add(outcome)
        try:
            if evaluate_event(case, outcome):
                events += 1
        except EventNotEvaluable:
            pass
    evaluated = len(reasons.replicates)
    detail: dict = {
        "case_id": case.case_id, "family": "control",
        "expectation": case.expectation,
        "expected_event": case.expected_event.value,
        "events": events,
        "configuration": digest,
        "seconds": round(time.time() - t0, 1),
        **reasons.as_dict(),
    }
    if evaluated > 0 and case.expected_event is ExpectedEvent.COMPLETE_SUPPORT:
        detail["false_support_cp_upper"] = clopper_pearson_upper(events, evaluated)
    return detail


def _not_run(case: ValidationCaseV4, inst: CaseInstantiation) -> dict:
    return {
        "case_id": case.case_id,
        "family": case.family,
        "status": "NOT RUN",
        "driver": inst.driver,
        "reason": inst.not_run_reason,
        "replicates_run": 0,
        "required": case.replicates,
        "expected_event": case.expected_event.value,
        "configuration": inst.digest(),
    }


# ---------------------------------------------------------------------------
# Single-record size driver
# ---------------------------------------------------------------------------

def run_size_case(
    seed_map: SeedMap, case: ValidationCaseV4, reps: int, frames: int,
    critical: CriticalValues = NORMAL_CRITICAL,
) -> dict:
    """False-equivalence size at a boundary null, single-record driver."""
    inst = instantiate(case.case_id)
    if not inst.runnable or inst.b_true is None:
        return _not_run(case, inst)
    agg = Aggregator(case.case_id, "size", "cp_upper", 0.025)
    reasons = ReasonAggregate(case.case_id)
    t0 = time.time()
    calibration = experiment_calibration(inst.spec_kwargs)
    for rep in range(reps):
        specs = design_specs(n_frames=frames, **inst.spec_kwargs)
        spec, h_locked = specs[0]
        spec = type(spec)(**{**spec.__dict__, "beta_true": math.exp(inst.b_true)})
        seed = seed_map.replicate_seed(case.seed_namespace, case.case_id, rep)
        envelope = observation_envelope(
            h_locked, plan.nominal_temperature(0), spec,
            axial_effects(0, coupling=float(inst.spec_kwargs.get(
                "coupling", plan.AXIAL_COUPLING))).rho)
        out = run_record(spec, h_locked, Stream(seed, label=case.case_id),
                         envelope=envelope)
        rec = build_record_result(
            BlockId.BLOCK1, FieldId.THETA0, out, calibration, critical,
        )
        contained = (
            None if rec.absolute is None else rec.absolute.strictly_inside(DELTA_A)
        )
        outcome = ReplicateOutcome(
            case_id=case.case_id, replicate=rep, seed=seed,
            reason_codes=tuple(r.code for r in rec.reasons),
            reason_predicates=tuple(f"{r.code}:{r.predicate}" for r in rec.reasons),
            absolute_contained=contained,
            bandwidth_product=out.bandwidth_product,
            evaluable=rec.evaluable,
            configuration=inst.digest(specs),
        )
        reasons.add(outcome)
        agg.add(evaluate_event(case, outcome))
    res = agg.result({
        **reasons.as_dict(),
        "b_true": inst.b_true,
        "expected_event": case.expected_event.value,
        "seconds": round(time.time() - t0, 1),
    })
    return res.as_dict()


# ---------------------------------------------------------------------------
# Per-replicate metadata (V5 brief section 49)
# ---------------------------------------------------------------------------
#
# The V4 audit noted these fields were left blank.  They are populated
# wherever the underlying result exists, and carry NOT_APPLICABLE rather than
# a blank where the quantity is not defined for that replicate.  Nothing is
# fabricated.

NOT_APPLICABLE = "NOT_APPLICABLE"


def _worst_optimizer_status(result) -> str:
    """The least successful optimiser outcome across the eight records."""
    order = ["NOT_ATTEMPTED", "OPTIMIZER_FAILURE", "NUMERICAL_FAILURE",
             "NOT_CONVERGED", "CONVERGED"]
    seen = [r for r in result.records if r.evaluable]
    if not seen:
        return "NOT_ATTEMPTED"
    statuses = [
        "NOT_CONVERGED" if r.log_beta is None else "CONVERGED" for r in seen
    ]
    if len(seen) != len(result.records):
        statuses.append("OPTIMIZER_FAILURE")
    return min(statuses, key=order.index)


def _realization_status(result) -> str:
    statuses = {r.realization_status for r in result.records
                if r.realization_status is not None}
    if not statuses:
        return NOT_APPLICABLE
    if len(statuses) == 1:
        return next(iter(statuses))
    return "MIXED:" + ",".join(sorted(statuses))


def _bandwidth(digest: Mapping[str, object]) -> float | None:
    measured = digest.get("measured") if isinstance(digest, dict) else None
    if isinstance(measured, dict):
        v = measured.get("bandwidth_product")
        if isinstance(v, float):
            return v
    return None
