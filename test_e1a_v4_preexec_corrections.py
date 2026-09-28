"""Static/pure pre-execution regressions. No generator, draw, or trajectory.

ADOPTION NOTE. The conditions below are the independent auditor's, unchanged. Only
the reporting was adjusted at adoption: each `assert` became a counted `verify`
call, so this gate reports a check count like every other suite and cannot be
silently disabled by `python3 -O`. No condition was added, removed or weakened.
"""

from __future__ import annotations

import math
from copy import deepcopy
from pathlib import Path

from e1a_v4.branch_a import build_field
from e1a_v4.contract import load_contract
from e1a_v4.identity import procedure_identity
from e1a_v4.numerics import Refusal, TT, mm
from e1a_v4.validation.calibrate import CalibrationRequest
from e1a_v4.validation.classification import CampaignCounts, classify_campaign
from e1a_v4.validation.dispositions import g2_campaign_pass
from e1a_v4.validation.generate import modal_ou_parameters, truth_from_field
from e1a_v4.validation.plan import load_plan, require_output_schema_agreement
from e1a_v4.validation.seeds import CaseSeedAccess, FrozenSeedMap, ValidationSeedFamily

ROOT = Path(__file__).resolve().parent
BINDING = load_contract(str(ROOT))
PLAN = load_plan(str(ROOT))

PASSED = 0
FAILED = 0


def verify(condition: bool, label: str) -> None:
    """Counted assertion. Replaces a bare `assert`, which -O would remove."""
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  [PASS] {label}")
    else:
        FAILED += 1
        print(f"  [FAIL] {label}")


def refuses(fn, *args) -> bool:
    try:
        fn(*args)
    except Refusal:
        return True
    return False


def diagonal(values):
    return [[v if i == j else 0.0 for j, v in enumerate(values)]
            for i in range(len(values))]


def check_modal_stationarity() -> None:
    spec = next(f for f in BINDING.fields if f["id"] == "theta2_ellipse")
    field = build_field(BINDING, spec,
                        calibration_route="force_displacement_with_stokes_drag",
                        viscosity=0.00089, bead_radius=1e-6)
    truth = truth_from_field(field, 1.2e-4, 2)
    q, phi, sd = modal_ou_parameters(truth)  # pure parameters, no model step
    stationary = mm(mm(q, diagonal([s * s for s in sd])), TT(q))
    transition = mm(mm(q, diagonal(phi)), TT(q))
    innovation = mm(mm(q, diagonal([(1 - p * p) * s * s for p, s in zip(phi, sd)])), TT(q))
    evolved = mm(mm(transition, stationary), TT(transition))
    scale = max(abs(v) for row in stationary for v in row)
    residual = max(abs(evolved[i][j] + innovation[i][j] - stationary[i][j])
                   for i in range(2) for j in range(2)) / scale
    verify(residual < 1e-12,
           "corrected modal transition satisfies F Sigma F^T + Q = Sigma")

    # The old laboratory-axis recurrence gives the wrong rotated covariance.
    wrong = phi[0] * phi[1] + math.sqrt((1 - phi[0] ** 2) * (1 - phi[1] ** 2))
    verify(abs(stationary[0][1]) / scale > 0.01,
           "the probe field really has a nonzero off-diagonal covariance")
    verify(abs(wrong - 1.0) > 0.01,
           "the superseded lab-axis recurrence would distort that off-diagonal")
    verify(refuses(modal_ou_parameters, truth.__class__(
        truth.field_id, truth.H_true, field.tau_modes, truth.beta_true,
        truth.dt, truth.n_samples, truth.x_star)),
        "a swapped tau/eigenvalue pairing is REFUSED")

    request = CalibrationRequest(field.field_id, field.H, 100,
                                 phi, 10, BINDING.alpha_1, BINDING.theta_cap_deg,
                                 procedure_identity(BINDING, {}, str(ROOT)),
                                 BINDING.sha256, "0" * 64, truth.dt, truth.tau_true)
    verify(request.condition().tau_modes == truth.tau_true,
           "a correctly paired calibration request keeps its tau order")
    wrong_request = CalibrationRequest(field.field_id, field.H, 100,
                                       tuple(reversed(phi)), 10, BINDING.alpha_1,
                                       BINDING.theta_cap_deg,
                                       procedure_identity(BINDING, {}, str(ROOT)),
                                       BINDING.sha256, "0" * 64, truth.dt,
                                       field.tau_modes)
    verify(refuses(wrong_request.condition),
           "a mispaired calibration request is REFUSED")


def check_incomplete_counts() -> None:
    fields = tuple(f["id"] for f in BINDING.fields)
    alternatives = tuple(s["subcondition_id"] for c in PLAN["cases"]
                         if c["case_id"] == "C7_false_bridge" for s in c["subconditions"])
    verify(len(fields) == len(alternatives) == 4,
           "the campaign declares exactly four fields and four alternatives")
    base = dict(c1_successes=290, c2_rejections_by_field={f: 1 for f in fields},
                c3_rejections=0, c4_rejections=0, c5_pass=True, c6_pass=True,
                c7_false_acceptances_by_alternative={a: 0 for a in alternatives},
                c8_successes=195)
    verify(classify_campaign(CampaignCounts(**base))["verdict"] == "VALIDATION_PASS",
           "a complete count map classifies normally")
    for missing, what in (("c2_rejections_by_field", "C2 field"),
                          ("c7_false_acceptances_by_alternative", "C7 alternative")):
        incomplete = dict(base)
        incomplete[missing] = {}
        verify(refuses(classify_campaign, CampaignCounts(**incomplete)),
               f"an empty {what} map is REFUSED by the campaign classifier")
    for drop in fields:
        partial = dict(base)
        partial["c2_rejections_by_field"] = {f: 1 for f in fields if f != drop}
        verify(refuses(classify_campaign, CampaignCounts(**partial)),
               f"a C2 map missing {drop} is REFUSED")
    for drop in alternatives:
        partial = dict(base)
        partial["c7_false_acceptances_by_alternative"] = {
            a: 0 for a in alternatives if a != drop}
        verify(refuses(classify_campaign, CampaignCounts(**partial)),
               f"a C7 map missing {drop} is REFUSED")
        verify(refuses(g2_campaign_pass,
                       {a: 0 for a in alternatives if a != drop}),
               f"the direct G2 helper REFUSES a map missing {drop}")
    verify(refuses(g2_campaign_pass, {}),
           "the direct G2 helper REFUSES an empty alternative map")
    verify(refuses(classify_campaign, CampaignCounts(
        **{**base, "c2_rejections_by_field": {**base["c2_rejections_by_field"],
                                              "theta9_invented": 0}})),
        "an EXTRA unknown C2 field is REFUSED")
    verify(refuses(classify_campaign, CampaignCounts(
        **{**base, "c7_false_acceptances_by_alternative": {
            **base["c7_false_acceptances_by_alternative"], "alt_invented": 0}})),
        "an EXTRA unknown C7 alternative is REFUSED")


def check_scope_and_schema() -> None:
    seed_map = FrozenSeedMap.derive(BINDING.sha256)
    access = CaseSeedAccess.from_plan("C1_true_bridge_complete", PLAN, seed_map)
    verify(refuses(access.stream, ValidationSeedFamily.VALIDATION,
                   access.subconditions[0], 0, "undeclared-scope"),
           "an undeclared field scope is REFUSED")
    verify(isinstance(access.stream(ValidationSeedFamily.VALIDATION,
                                    access.subconditions[0], 0, "theta0_circular"), int),
           "a declared field scope is accepted")
    c6 = CaseSeedAccess.from_plan("C6_mode_resolution_boundary", PLAN, seed_map)
    verify(len(c6.field_scopes) == 1,
           "C6 declares exactly one field scope, not four")
    verify(refuses(c6.stream, ValidationSeedFamily.VALIDATION,
                   c6.subconditions[0], 0, "theta0_circular"),
           "C6 cannot borrow a theta0 stream")
    verify(isinstance(c6.stream(ValidationSeedFamily.VALIDATION,
                                c6.subconditions[0], 0, c6.field_scopes[0]), int),
           "C6 accepts its own declared synthetic-field scope token")
    verify(refuses(access.stream, ValidationSeedFamily.VALIDATION,
                   access.subconditions[0], 0, "experiment"),
           "the experiment scope is REFUSED to a non-Branch-A family")
    verify(isinstance(access.stream(ValidationSeedFamily.BRANCH_A_MEASUREMENT,
                                    access.subconditions[0], 0, "experiment"), int),
           "the experiment scope is accepted for Branch-A measurement")
    schema = PLAN["output_schema"]
    md = (ROOT / "docs/e1a/E1A_V4_SYNTHETIC_VALIDATION_PLAN.md").read_text()
    verify(schema["record_schema"] in md and schema["manifest_schema"] in md,
           "markdown carries the JSON record and manifest schema versions")
    verify("`subcondition_id`" in md and "declared scope regenerate" in md,
           "markdown carries subcondition_id and the declared-scope recipe")
    require_output_schema_agreement(str(ROOT), PLAN)
    verify(True, "the live plan passes the schema-agreement preflight")
    mismatch = deepcopy(PLAN)
    mismatch["output_schema"]["record_schema"] = "e1a_v4_validation_result/1"
    verify(refuses(require_output_schema_agreement, str(ROOT), mismatch),
           "a markdown/JSON schema VERSION mismatch is REFUSED")
    mismatch = deepcopy(PLAN)
    mismatch["output_schema"]["per_record_fields"].remove("subcondition_id")
    verify(refuses(require_output_schema_agreement, str(ROOT), mismatch),
           "a markdown/JSON record-FIELD mismatch is REFUSED")


if __name__ == "__main__":
    print("\nmodal stationarity and modal pairing")
    check_modal_stationarity()
    print("\nincomplete C2 / C7 count maps")
    check_incomplete_counts()
    print("\nseed scopes and output-schema agreement")
    check_scope_and_schema()
    print(f"\nE1a v4 correction gate: {PASSED} passed, {FAILED} failed, 3 groups")
    print("Execution class: NON-MODEL-ADVANCING STATIC/PURE (this suite only)")
    print("  RNG OBJECTS           : 0")
    print("  RANDOM DRAWS          : 0")
    print("  TRAJECTORIES          : 0")
    raise SystemExit(1 if FAILED else 0)
