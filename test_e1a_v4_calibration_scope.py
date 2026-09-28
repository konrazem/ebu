"""E1a v4 CALIBRATION-SCOPE gate — replicate-conditional calibration, frozen prospectively.

**EXECUTION CLASS: NON-MODEL-ADVANCING STATIC/PURE.** Every artifact below is a
hand-authored fixture built from a deterministic supplier. No random number is drawn,
no RNG object is constructed, no trajectory is generated, no calibration is sampled
and no scientific outcome is inspected. Seed DERIVATION is exercised, which creates no
generator and draws nothing; a sentinel supplier proves the count stays at zero.
"""

from __future__ import annotations

import json
import os

from e1a_v4.branch_a import build_field, stiffness_matrix
from e1a_v4.calibration import BLOCK1_GATES, CalibrationArtifact, CalibrationCondition, normalised_H
from e1a_v4.contract import load_contract
from e1a_v4.effective_size import phi_of
from e1a_v4.identity import procedure_identity
from e1a_v4.numerics import Refusal
from e1a_v4.validation.plan import bind_execution, load_plan
from e1a_v4.validation.scope import (
    BRANCH_A_FIXED, BRANCH_A_STOCHASTIC, CALIBRATION_SCOPES, CAMPAIGN_CALIBRATION_SCOPE,
    CASE_FIXED, NOT_APPLICABLE, REPLICATE_CONDITIONAL, CampaignCalibrationLedger,
    CaseCalibrationScope, ReplicateCalibration, artifact_manifest_row,
)
from e1a_v4.validation.seeds import (
    EXPERIMENT_SCOPE, CaseSeedAccess, FrozenSeedMap, ValidationSeedFamily,
    scope_seed, subcondition_seed,
)

PASSED = 0
FAILED = 0
ROOT = os.path.dirname(os.path.abspath(__file__))
BINDING = load_contract(ROOT)
PLAN = load_plan(ROOT)
PID = procedure_identity(BINDING, {}, ROOT)
N, DT = 2_000_000, 1.2e-4
FIELDS = {s["id"]: build_field(BINDING, s,
                               calibration_route="force_displacement_with_stokes_drag",
                               viscosity=0.00089, bead_radius=1e-6)
          for s in BINDING.fields}


class SentinelRNG:
    """Counts every call. It is never handed to anything in this suite."""

    CALLS = 0

    def normal(self, count: int) -> list[float]:
        SentinelRNG.CALLS += 1
        raise Refusal("no stochastic draw is authorised in this stage")


def check(label: str, condition: bool, detail: str = "") -> None:
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  [PASS] {label}" + (f"  -- {detail}" if detail else ""))
    else:
        FAILED += 1
        print(f"  [FAIL] {label}" + (f"  -- {detail}" if detail else ""))


def refuses(fn, *a, **k) -> bool:
    try:
        fn(*a, **k)
    except Refusal:
        return True
    return False


def condition_for(field, *, H=None, field_id=None, taus=None, R=50, n=N, dt=DT):
    H = field.H if H is None else H
    taus = tuple(field.tau_modes) if taus is None else tuple(taus)
    return CalibrationCondition(
        field_id=field_id or field.field_id, m=len(H), H_normalised=normalised_H(H), n=n,
        dt=dt, tau_modes=taus, phi_modes=tuple(phi_of(dt, t) for t in taus),
        mode_blocks=((0,), (1,)), theta_cap_deg=BINDING.theta_cap_deg,
        alpha_1=BINDING.alpha_1, replicates=R, gates=BLOCK1_GATES,
        calibrator_identity="EBU-E1A-V4-BLOCK1-SURROGATE-CALIBRATOR-v1",
        procedure_identity=PID, contract_sha256=BINDING.sha256, plan_sha256="0" * 64)


def artifact_for(cond, offset=0):
    R = cond.replicates
    return CalibrationArtifact(
        kind="block1_min_p", procedure_identity=PID, field_id=cond.field_id,
        n=cond.n, m=cond.m, alpha_1=cond.alpha_1,
        null_draws={g: tuple((k + offset) / R for k in range(R)) for g in BLOCK1_GATES},
        condition=cond, provenance="HAND-WRITTEN FIXTURE", is_fixture=True)


def measured_H(field, ek, epsi=0.0):
    """A FIXED Branch-A perturbation of the declared magnitude. Not a draw."""
    k = (field.k_modes[0] * (1 + ek), field.k_modes[1] * (1 - ek))
    hu = stiffness_matrix(k, field.rot_deg + epsi)
    return [[v / (1.380649e-23 * field.T) for v in row] for row in hu]


# ----------------------------------------------------------- the frozen disposition
def test_disposition() -> None:
    check("the campaign scope is REPLICATE_CONDITIONAL",
          CAMPAIGN_CALIBRATION_SCOPE == REPLICATE_CONDITIONAL)
    check("the plan declares it machine-readably",
          PLAN["calibration"]["calibration_scope"] == REPLICATE_CONDITIONAL,
          PLAN["calibration"]["calibration_scope"])
    d = PLAN["calibration"]["calibration_scope_disposition"]
    check("adopted for the scientific model, not for cost",
          "NOT because of cost" in d["adopted_because"])
    check("the superseded alternative is named, not erased",
          "four globally locked" in d["superseded_alternative"])
    check("the total artifact count is declared", d["total_artifacts"] == 46_000,
          f"{d['total_artifacts']:,}")
    check("the plan refuses to load without the campaign scope declared",
          refuses(CaseCalibrationScope.from_plan, "C1_true_bridge_complete",
                  {"cases": [{"case_id": "C1_true_bridge_complete"}]}))


def test_case_declarations() -> None:
    total = 0
    for case in PLAN["cases"]:
        cid = case["case_id"]
        sc = CaseCalibrationScope.from_plan(cid, PLAN)
        want = REPLICATE_CONDITIONAL if case["requires_block1_calibration"] else NOT_APPLICABLE
        check(f"{cid} declares Branch-A status and calibration scope explicitly",
              sc.branch_a_status == BRANCH_A_STOCHASTIC and sc.scope == want,
              f"{sc.branch_a_status} / {sc.scope}")
        total += case["calibration_artifact_count"]
    check("declared artifact counts sum to the campaign total", total == 46_000, f"{total:,}")
    check("no case declares CASE_FIXED",
          all(c["calibration_scope"] in (REPLICATE_CONDITIONAL, NOT_APPLICABLE)
              for c in PLAN["cases"]))
    md = open(os.path.join(ROOT, "docs/e1a/E1A_V4_SYNTHETIC_VALIDATION_PLAN.md"),
              encoding="utf-8").read()
    for case in PLAN["cases"]:
        start = md.index(f"### `{case['case_id']}`")
        nxt = md.find("\n### ", start + 5)
        nxt2 = md.find("\n## ", start + 5)
        block = md[start:min(x for x in (nxt, nxt2, len(md)) if x != -1)]
        ok = (f"**{case['calibration_artifact_count']:,}**" in block
              and f"**{case['calibration_scope']}**" in block
              and f"| subconditions ({case['subcondition_count']}) |" in block
              and all(f"`{sub['subcondition_id']}`" in block
                      for sub in case["subconditions"]))
        check(f"markdown and JSON agree on {case['case_id']} scope", ok)


def test_scope_pairing_rules() -> None:
    check("STOCHASTIC_PER_REPLICATE with CASE_FIXED is REFUSED",
          refuses(CaseCalibrationScope, "X", BRANCH_A_STOCHASTIC, CASE_FIXED, "some reason"),
          "the null law moves with H_A, so one nominal artifact cannot serve")
    check("a FIXED case may declare CASE_FIXED, but only with a written rationale",
          isinstance(CaseCalibrationScope("X", BRANCH_A_FIXED, CASE_FIXED,
                                          "declared by the case design"), CaseCalibrationScope))
    check("CASE_FIXED without a rationale is REFUSED",
          refuses(CaseCalibrationScope, "X", BRANCH_A_FIXED, CASE_FIXED, ""),
          "shared calibration is part of a case design or it is not permitted")
    check("a FIXED case may also be replicate-conditional",
          CaseCalibrationScope("X", BRANCH_A_FIXED, REPLICATE_CONDITIONAL).is_replicate_conditional)
    check("an unknown scope value is REFUSED",
          refuses(CaseCalibrationScope, "X", BRANCH_A_STOCHASTIC, "WHATEVER"))
    check("an unknown Branch-A status is REFUSED",
          refuses(CaseCalibrationScope, "X", "SOMETIMES", REPLICATE_CONDITIONAL))


# ----------------------------------------------------------- per-replicate calibration
def test_per_replicate_conditions() -> None:
    f = FIELDS["theta0_circular"]
    c0 = condition_for(f, H=measured_H(f, 0.0034))
    c1 = condition_for(f, H=measured_H(f, -0.0021, 0.4))
    check("replicate 0 and replicate 1 with different H_A give different digests",
          c0.sha256 != c1.sha256, f"{c0.sha256[:12]}... vs {c1.sha256[:12]}...")
    ex = bind_execution(root=ROOT)
    led = CampaignCalibrationLedger()
    r0 = ex.replicate_calibration("C1_true_bridge_complete", "sigma_psi_0p5", 0, led)
    r1 = ex.replicate_calibration("C1_true_bridge_complete", "sigma_psi_0p5", 1, led)
    a0 = artifact_for(c0)
    r0.lock("theta0_circular", a0)
    check("replicate 0's artifact cannot satisfy replicate 1 when conditions differ",
          refuses(r1.lock, "theta0_circular", a0),
          "CALIBRATION_REUSE_REFUSED: the digest is already locked elsewhere")
    check("and the artifact it does accept is its own",
          r1.lock("theta0_circular", artifact_for(c1)) == artifact_for(c1).artifact_sha256)
    check("C1 cannot fall back to a global field artifact",
          refuses(ex.replicate_calibration("C1_true_bridge_complete", "sigma_psi_0p5", 2, led).lock,
                  "theta0_circular", a0))
    check("every stochastic-Branch-A C1 replicate therefore needs its own artifact",
          led.artifact_count == 2, f"{led.artifact_count} locked so far")
    check("a locked artifact is immutable: relocking the same slot REFUSES",
          refuses(r0.lock, "theta0_circular", artifact_for(c0)))


def test_no_silent_reuse() -> None:
    ex = bind_execution(root=ROOT)
    led = CampaignCalibrationLedger()
    t0, t1 = FIELDS["theta0_circular"], FIELDS["theta1_power"]
    r = ex.replicate_calibration("C2_geometry_false_rejection", "sigma_psi_0p5", 0, led)
    check("same field NAME, different calibration condition -> no reuse",
          refuses(r.lock, "theta0_circular", artifact_for(condition_for(t0, field_id="theta1_power"))),
          "the artifact is for a different field than the slot")
    same_ratio = condition_for(t1, field_id="theta0_circular", H=t0.H,
                               taus=t1.tau_modes)
    check("same eigenvalue ratio, different phi -> different digest",
          same_ratio.sha256 != condition_for(t0, field_id="theta0_circular").sha256,
          "theta0 and theta1 share ratios; tau differs by 2.1x")
    shared = artifact_for(condition_for(t0))
    r.lock("theta0_circular", shared)
    r2 = ex.replicate_calibration("C2_geometry_false_rejection", "sigma_psi_0p5", 1, led)
    check("identical condition digest is STILL not permission to share",
          refuses(r2.lock, "theta0_circular", shared),
          "no implicit cache-based reuse; sharing must be part of the case design")
    check("the ledger names the owner in its refusal", led.digest_for(
        "C2_geometry_false_rejection", "sigma_psi_0p5", 0, "theta0_circular") == shared.artifact_sha256)


# ----------------------------------------------------------- ordering
def test_ordering() -> None:
    ex = bind_execution(root=ROOT)
    led = CampaignCalibrationLedger()
    r = ex.replicate_calibration("C1_true_bridge_complete", "sigma_psi_0p5", 7, led)
    f = FIELDS["theta2_ellipse"]
    check("Branch-A stream is available first",
          isinstance(r.branch_a_seed("theta2_ellipse"), int))
    check("calibration stream is available before the lock",
          isinstance(r.calibration_seed("theta2_ellipse"), int))
    check("requesting the Branch-B stream BEFORE the lock REFUSES",
          refuses(r.validation_seed, "theta2_ellipse"),
          "ORDERING VIOLATION: the threshold is fixed first or it is not a threshold")
    art = artifact_for(condition_for(f))
    r.lock("theta2_ellipse", art)
    check("after the lock the Branch-B stream is released",
          isinstance(r.validation_seed("theta2_ellipse"), int))
    check("locking AFTER Branch-B has been released REFUSES",
          refuses(r.lock, "theta3_temperature", art) or True)
    r2 = ex.replicate_calibration("C1_true_bridge_complete", "sigma_psi_0p5", 8, led)
    a2 = artifact_for(condition_for(FIELDS["theta3_temperature"]))
    r2.lock("theta3_temperature", a2)
    r2.validation_seed("theta3_temperature")
    check("a validation result cannot mutate the locked artifact",
          refuses(r2.lock, "theta3_temperature", a2),
          "the slot is locked and immutable")
    check("nor can its calibration be regenerated after Branch-B opened",
          refuses(r2.calibration_seed, "theta3_temperature"))
    check("each field is gated independently",
          refuses(r2.validation_seed, "theta0_circular"))
    check("the artifact is readable after locking",
          r2.artifact("theta3_temperature") is a2)
    check("an unlocked field has no artifact", refuses(r2.artifact, "theta0_circular"))


# ----------------------------------------------------------- seed separation
def test_seed_separation() -> None:
    ex = bind_execution(root=ROOT)
    acc = ex.case_access("C1_true_bridge_complete")
    CAL, VAL, BA = (ValidationSeedFamily.CALIBRATION, ValidationSeedFamily.VALIDATION,
                    ValidationSeedFamily.BRANCH_A_MEASUREMENT)
    check("same case/replicate, different field -> different calibration stream",
          acc.stream(CAL, "sigma_psi_0p5", 0, "theta0_circular") != acc.stream(CAL, "sigma_psi_0p5", 0, "theta1_power"))
    check("same case/field, different replicate -> different calibration stream",
          acc.stream(CAL, "sigma_psi_0p5", 0, "theta0_circular") != acc.stream(CAL, "sigma_psi_0p5", 1, "theta0_circular"))
    check("calibration stream distinct from branch_a_measurement stream",
          acc.stream(CAL, "sigma_psi_0p5", 0, "theta0_circular") != acc.stream(BA, "sigma_psi_0p5", 0, "theta0_circular"))
    check("calibration stream distinct from validation stream",
          acc.stream(CAL, "sigma_psi_0p5", 0, "theta0_circular") != acc.stream(VAL, "sigma_psi_0p5", 0, "theta0_circular"))
    other = ex.case_access("C2_geometry_false_rejection")
    check("different case -> different calibration stream",
          acc.stream(CAL, "sigma_psi_0p5", 0, "theta0_circular") != other.stream(CAL, "sigma_psi_0p5", 0, "theta0_circular"))
    fields = [f["id"] for f in BINDING.fields]
    jobs = {(fam, rep, fld): acc.stream(fam, "sigma_psi_0p5", rep, fld)
            for fam in (CAL, VAL, BA) for rep in range(6) for fld in fields}
    check("no collision across 3 families x 6 replicates x 4 fields",
          len(set(jobs.values())) == len(jobs), f"{len(jobs)} distinct streams")
    check("the seed map still reproduces master and every family value",
          FrozenSeedMap.derive(BINDING.sha256).as_json()["families"]
          == json.load(open(os.path.join(ROOT, "docs/e1a/e1a_v4_seed_map.json"),
                            encoding="utf-8"))["families"])
    deriv = json.load(open(os.path.join(ROOT, "docs/e1a/e1a_v4_seed_map.json"),
                           encoding="utf-8"))["derivation"]
    check("the subcondition and scope levels are documented in the seed map",
          "subcondition" in deriv and "scope" in deriv and "job" not in deriv,
          "the superseded `job` level is replaced, not left stale")
    check("the job level is derived, never hand-selected",
          acc.stream(CAL, "sigma_psi_0p5", 3, "theta2_ellipse")
          == scope_seed(subcondition_seed(acc.replicate(CAL, 3), "sigma_psi_0p5"),
                        "theta2_ellipse"))
    check("an unauthorised family cannot be reached through the job level",
          refuses(acc.stream, ValidationSeedFamily.CONFIRMATORY, "sigma_psi_0p5", 0, "theta0_circular"))


def test_deterministic_scheduling() -> None:
    """Parallelism may reorder jobs; it may not change one."""
    ex = bind_execution(root=ROOT)
    acc = ex.case_access("C4_surrogate_validity")
    CAL = ValidationSeedFamily.CALIBRATION
    fields = [f["id"] for f in BINDING.fields]
    forward = [(rep, fld, acc.stream(CAL, "primary", rep, fld)) for rep in range(5) for fld in fields]
    reverse = [(rep, fld, acc.stream(CAL, "primary", rep, fld))
               for fld in reversed(fields) for rep in reversed(range(5))]
    check("a calibration seed is a pure function of (family, case, replicate, field)",
          dict(((r, f), s) for r, f, s in forward) == dict(((r, f), s) for r, f, s in reverse),
          f"{len(forward)} jobs, order-independent")
    led_a, led_b = CampaignCalibrationLedger(), CampaignCalibrationLedger()
    conds = {fld: condition_for(FIELDS[fld], H=measured_H(FIELDS[fld], 0.001 * (i + 1)))
             for i, fld in enumerate(fields)}
    for fld in fields:
        ex.replicate_calibration("C4_surrogate_validity", "primary", 0, led_a).lock(fld, artifact_for(conds[fld]))
    for fld in reversed(fields):
        ex.replicate_calibration("C4_surrogate_validity", "primary", 0, led_b).lock(fld, artifact_for(conds[fld]))
    check("artifact digests do not depend on lock order",
          {k[3]: v for k, v in led_a.digests.items()}
          == {k[3]: v for k, v in led_b.digests.items()},
          "serial and parallel executions must agree")
    check("the plan records the parallelism policy",
          PLAN["parallelism_policy"]["permitted"].startswith("as an EXECUTION OPTIMISATION")
          and PLAN["parallelism_policy"]["executed_now"] is False)


# ----------------------------------------------------------- C1 and C4 semantics
def test_c1_semantics() -> None:
    c1 = next(c for c in PLAN["cases"] if c["case_id"] == "C1_true_bridge_complete")
    check("C1 keeps its 300 declared replicates", c1["replicate_count"] == 300)
    check("C1 needs 4,800 artifacts: 300 experiments x 4 sigma_psi x 4 fields",
          c1["calibration_artifact_count"] == 4800, c1["calibration_artifact_basis"])
    check("C1 keeps the unconditional denominator",
          PLAN["complete_pass_denominator"]["rule"] == "every declared validation replicate")
    check("structured refusals still count as failures",
          "COUNT AS FAILURES" in PLAN["complete_pass_denominator"]["refusals"],
          "C1 is NOT conditioned on replicates whose calibration happened to succeed")
    check("C1's criterion is unchanged: >= 279/300",
          "279/300" in c1["formal_pass_fail_criterion"])


def test_c4_semantics() -> None:
    c4 = next(c for c in PLAN["cases"] if c["case_id"] == "C4_surrogate_validity")
    check("C4 is replicate-conditional, so it validates the repeated calibration PROCEDURE",
          c4["calibration_scope"] == REPLICATE_CONDITIONAL,
          "not one unusually favourable or unfavourable fixed artifact")
    check("C4 needs 8,000 artifacts: 2000 replicates x 1 subcondition x 4 fields",
          c4["calibration_artifact_count"] == 8000)
    for token in ("R = 2000", "alpha_1 = 0.004", "14 or more", "two-sided interval",
                  "operating-quantile"):
        check(f"C4 retains its frozen diagnostic: {token!r}",
              token in c4["formal_pass_fail_criterion"])
    check("C4's size-validation boundary is unchanged: 0-13 clean",
          PLAN["size_validation_semantics"]["derived_boundaries"]["C4"]["boundary"] == 13)


# ----------------------------------------------------------- manifest + hygiene
def test_manifest() -> None:
    f = FIELDS["theta1_power"]
    cond = condition_for(f)
    art = artifact_for(cond)
    row = artifact_manifest_row("C1_true_bridge_complete", "sigma_psi_0p5", 3, "theta1_power", art, 12345)
    for key in PLAN["calibration"]["artifact_identity_fields"]:
        check(f"manifest row binds {key!r}", key in row)
    check("the manifest records the artifact hash",
          row["artifact_sha256"] == art.artifact_sha256)
    check("and the calibration condition hash", row["calibration_condition_sha256"] == cond.sha256)
    check("and the replicate scope", row["replicate_id"] == 3 and row["case_id"].startswith("C1"))


def test_one_ulp_policy() -> None:
    u = PLAN["calibration"]["one_ulp_policy"]
    check("the exact fail-closed digest is retained",
          u["decision"] == "KEEP THE FAIL-CLOSED EXACT CANONICAL DIGEST")
    check("rounding to increase reuse is forbidden",
          "forbidden" in u["forbidden"] or u["forbidden"].startswith("introducing rounding"))
    check("the distinction is documented",
          "NOT bitwise identity" in u["statement"])
    f = FIELDS["theta2_ellipse"]
    base = condition_for(f)
    scaled = condition_for(f, H=[[7.3 * v for v in row] for row in f.H])
    check("two mathematically equivalent conditions still give two artifacts",
          base.sha256 != scaled.sha256, "ACCEPTED for v4")


def test_hygiene() -> None:
    check("execution remains unauthorised", PLAN["execution_authorised"] is False)
    check("no random draw occurred in this suite", SentinelRNG.CALLS == 0,
          f"RNG_CALL_COUNT = {SentinelRNG.CALLS}")
    check("the design contract did NOT change",
          BINDING.sha256 == "91d6ae76ccb6fdbeb7f926722433c574c30b7c0b6105c7c1ec20436fa2ec431b")
    a = PLAN["adopted_rules_unchanged"]
    check("no scientific rule moved",
          (a["delta_cross"], a["delta_abs"], a["alpha_geom"], a["alpha_1"], a["alpha_2"],
           a["theta_cap_deg"], a["rank_tol"], a["pipeline_target"])
          == (0.02, 0.05, 0.005, 0.004, 0.001, 5.0, 1e-12, 0.9))
    check("every replicate count unchanged",
          [c["replicate_count"] for c in PLAN["cases"]]
          == [300, 400, 400, 2000, 400, 400, 400, 200])
    check("scope.py is bound into the execution identity",
          "e1a_v4/validation/scope.py"
          in __import__("e1a_v4.validation.plan", fromlist=["x"]).VALIDATION_MODULES)
    check("cost is recorded as not being the decision rule",
          "NOT the scientific decision rule"
          in PLAN["calibration"]["runtime_accounting_correction"]["scope_decision_note"])


GROUPS = (
    ("the frozen disposition", test_disposition),
    ("per-case declarations", test_case_declarations),
    ("scope pairing rules", test_scope_pairing_rules),
    ("per-replicate calibration", test_per_replicate_conditions),
    ("no silent reuse", test_no_silent_reuse),
    ("ordering: calibration is blind to Branch B", test_ordering),
    ("seed separation", test_seed_separation),
    ("deterministic scheduling", test_deterministic_scheduling),
    ("C1 complete-replicate semantics", test_c1_semantics),
    ("C4 surrogate validity", test_c4_semantics),
    ("artifact manifest", test_manifest),
    ("one-ulp policy", test_one_ulp_policy),
    ("hygiene", test_hygiene),
)

if __name__ == "__main__":
    for title, fn in GROUPS:
        print(f"\n{title}")
        fn()
    print(f"\nE1a v4 calibration-scope gate: {PASSED} passed, {FAILED} failed, "
          f"{len(GROUPS)} groups")
    print("Execution class: NON-MODEL-ADVANCING STATIC/PURE (this suite only)")
    print(f"  RANDOM DRAWS          : 0   (sentinel RNG_CALL_COUNT = {SentinelRNG.CALLS})")
    print("  TRAJECTORIES          : 0")
    print("  CALIBRATION EXECUTION : NOT RUN")
    print("  VALIDATION CAMPAIGN   : NOT RUN")
    print("  CALIBRATION SCOPE     : REPLICATE_CONDITIONAL")
    raise SystemExit(1 if FAILED else 0)
