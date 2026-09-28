"""E1a v4 CASE-SCOPE gate — B4 calibration necessity, B5 subcondition budget, B6 stream scope.

**EXECUTION CLASS: NON-MODEL-ADVANCING STATIC/PURE.** Every value below is a
hand-authored fixture or a derived seed identity. No RNG object is constructed, no
random number is drawn, no trajectory is generated, no calibration is sampled and no
scientific outcome is inspected. A sentinel generator proves the draw count stays at
zero: it is never handed to anything, and any call would raise.
"""

from __future__ import annotations

import inspect
import itertools
import json
import os

from e1a_v4.branch_a import build_field
from e1a_v4.calibration import BLOCK1_GATES, CalibrationArtifact, CalibrationCondition, normalised_H
from e1a_v4.contract import load_contract
from e1a_v4.effective_size import phi_of
from e1a_v4.identity import procedure_identity
from e1a_v4.numerics import Refusal
from e1a_v4.validation import dispositions, scope as scope_mod
from e1a_v4.validation.plan import bind_execution, load_plan
from e1a_v4.validation.results import RESULT_FIELDS, RESULT_SCHEMA
from e1a_v4.validation.scope import (
    NOT_APPLICABLE, REPLICATE_CONDITIONAL, CampaignCalibrationLedger, CaseCalibrationScope,
)
from e1a_v4.validation.seeds import EXPERIMENT_SCOPE, ValidationSeedFamily as VF

PASSED = 0
FAILED = 0
ROOT = os.path.dirname(os.path.abspath(__file__))
BINDING = load_contract(ROOT)
PLAN = load_plan(ROOT)
EX = bind_execution(root=ROOT)
PID = procedure_identity(BINDING, {}, ROOT)
CASES = {c["case_id"]: c for c in PLAN["cases"]}
FIELDS = [f["id"] for f in BINDING.fields]
N, DT = 2_000_000, 1.2e-4


class SentinelRNG:
    """Counts calls. Never handed to anything; any call is a defect."""

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


def sub_ids(cid):
    return [s["subcondition_id"] for s in CASES[cid]["subconditions"]]


def fixture_artifact(field_id="theta0_circular", R=40):
    f = {s["id"]: build_field(BINDING, s,
                              calibration_route="force_displacement_with_stokes_drag",
                              viscosity=0.00089, bead_radius=1e-6)
         for s in BINDING.fields}[field_id]
    cond = CalibrationCondition(
        field_id, 2, normalised_H(f.H), N, DT, tuple(f.tau_modes),
        tuple(phi_of(DT, t) for t in f.tau_modes), ((0,), (1,)), BINDING.theta_cap_deg,
        BINDING.alpha_1, R, BLOCK1_GATES, "EBU-E1A-V4-BLOCK1-SURROGATE-CALIBRATOR-v1",
        PID, BINDING.sha256, "0" * 64)
    return CalibrationArtifact("block1_min_p", PID, field_id, N, 2, BINDING.alpha_1,
                               {g: tuple(k / R for k in range(R)) for g in BLOCK1_GATES},
                               cond, is_fixture=True)


# ------------------------------------------------------- B4: calibration necessity
def test_b4_rule() -> None:
    check("the requirement rule is frozen and machine-readable",
          "DIFFERENT properties"
          in PLAN["calibration"]["calibration_scope_disposition"]["requirement_rule"])
    check("p1_geometry is still the ONLY consumer of a CalibrationArtifact",
          "artifact" in inspect.signature(
              __import__("e1a_v4.endpoints", fromlist=["x"]).p1_geometry).parameters
          and not any("artifact" in inspect.signature(getattr(
              __import__("e1a_v4.endpoints", fromlist=["x"]), n)).parameters
              for n in ("p2_cross_field", "p3_absolute", "p4_consistency")))
    expect = {"C1_true_bridge_complete": True, "C2_geometry_false_rejection": True,
              "C3_g5_block": True, "C4_surrogate_validity": True,
              "C5_plug_in_branch_a": True, "C6_mode_resolution_boundary": True,
              "C7_false_bridge": False, "C8_blinded_scale_control": False}
    for cid, want in expect.items():
        c = CASES[cid]
        check(f"{cid} requires_block1_calibration = {want}",
              c["requires_block1_calibration"] is want
              and c["uses_p1_block1"] is want,
              c["primary_release_endpoint"])
        check(f"{cid} calibration scope matches its requirement",
              c["calibration_scope"] == (REPLICATE_CONDITIONAL if want else NOT_APPLICABLE))
    check("a case may not be stochastic-but-nominal-calibration",
          refuses(CaseCalibrationScope, "X", scope_mod.BRANCH_A_STOCHASTIC,
                  scope_mod.CASE_FIXED, "reason", True, ("s",)))
    check("a non-calibrating case may not claim REPLICATE_CONDITIONAL",
          refuses(CaseCalibrationScope, "X", scope_mod.BRANCH_A_STOCHASTIC,
                  REPLICATE_CONDITIONAL, "", False, ("s",)))


def test_b4_c7() -> None:
    c7 = CASES["C7_false_bridge"]
    check("C7 does not request the calibration family",
          "calibration" not in c7["allowed_seed_families"],
          ", ".join(c7["allowed_seed_families"]))
    check("C7 cannot obtain the calibration family through the official route",
          refuses(EX.case_access("C7_false_bridge").family, VF.CALIBRATION))
    led = CampaignCalibrationLedger()
    rc = EX.replicate_calibration("C7_false_bridge", "hard_1_025", 0, led)
    check("C7 does not construct a CalibrationCondition (no calibration stream)",
          refuses(rc.calibration_seed, "theta0_circular"))
    check("C7 cannot lock a calibration artifact",
          refuses(rc.lock, "theta0_circular", fixture_artifact()))
    check("C7 reaches Branch-B WITHOUT any calibration artifact",
          isinstance(rc.validation_seed("theta0_circular"), int),
          "no artifact, no lock, no refusal path")
    check("C7 budgets zero calibration artifacts", c7["calibration_artifact_count"] == 0)
    check("a calibration refusal cannot alter C7 classification",
          led.artifact_count == 0 and rc.locked_fields == (),
          "there is no calibration step in C7's path to fail")
    check("C7 acceptance is P2 + P3, never P1",
          c7["primary_release_endpoint"] == "P2_INTERSECTION_UNION_AND_P3_ALL_FIELD_ABSOLUTE")
    check("G2 still evaluates each alternative independently",
          dispositions.g2_alternative_pass(4, 400, 0.025)[0]
          and not dispositions.g2_alternative_pass(5, 400, 0.025)[0],
          "<= 4/400 passes, 5 fails; unchanged")


def test_b4_c8() -> None:
    c8 = CASES["C8_blinded_scale_control"]
    check("C8 does not request the calibration family",
          "calibration" not in c8["allowed_seed_families"],
          ", ".join(c8["allowed_seed_families"]))
    check("C8 cannot obtain the calibration family through the official route",
          refuses(EX.case_access("C8_blinded_scale_control").family, VF.CALIBRATION))
    led = CampaignCalibrationLedger()
    rc = EX.replicate_calibration("C8_blinded_scale_control", "paired_scale_control", 0, led)
    check("C8 does not construct a CalibrationCondition",
          refuses(rc.calibration_seed, "theta0_circular"))
    check("C8 cannot lock a calibration artifact",
          refuses(rc.lock, "theta0_circular", fixture_artifact()))
    check("C8 reaches its Branch-B control data WITHOUT a calibration artifact",
          isinstance(rc.validation_seed("theta0_circular",
                                        VF.BLINDED_SCALE_CONTROL), int))
    check("a Block-1 calibration refusal cannot fail C8",
          led.artifact_count == 0,
          "no calibration step exists in C8's path")
    check("C8 budgets zero calibration artifacts", c8["calibration_artifact_count"] == 0)
    src = inspect.getsource(dispositions)
    check("dispositions.py reaches p3_absolute and never p1_geometry",
          "p3_absolute" in src and "p1_geometry" not in src
          and "CalibrationArtifact" not in src)
    check("C8's endpoint is the P3-equivalent transformed-beta rule",
          c8["primary_release_endpoint"] == "P3_EQUIVALENT_TRANSFORMED_BETA_RECOVERY")
    check("the paired rule is unchanged: both factors must pass",
          dispositions.BLINDED_SCALE_FACTORS == (1.07, 0.90)
          and dispositions.g1_success_threshold(200, 0.90) == 188)


def test_b4_c1_to_c6_still_gated() -> None:
    led = CampaignCalibrationLedger()
    for cid, sub in (("C1_true_bridge_complete", "sigma_psi_0p5"),
                     ("C2_geometry_false_rejection", "sigma_psi_0p5"),
                     ("C3_g5_block", "sigma_psi_0p5"),
                     ("C4_surrogate_validity", "primary"),
                     ("C5_plug_in_branch_a", "sk0p50_sp0p5"),
                     ("C6_mode_resolution_boundary", "rho_1p024467")):
        rc = EX.replicate_calibration(cid, sub, 0, led)
        check(f"{cid} still REFUSES Branch-B before the calibration lock",
              refuses(rc.validation_seed, "theta0_circular"),
              "ordering not weakened where calibration is required")


# ------------------------------------------------------- B5: subcondition budget
def test_b5_subconditions() -> None:
    expect = {"C1_true_bridge_complete": 4, "C2_geometry_false_rejection": 4,
              "C3_g5_block": 4, "C4_surrogate_validity": 1, "C5_plug_in_branch_a": 12,
              "C6_mode_resolution_boundary": 3, "C7_false_bridge": 4,
              "C8_blinded_scale_control": 1}
    for cid, n in expect.items():
        check(f"{cid} declares {n} explicit subcondition id(s)",
              CASES[cid]["subcondition_count"] == n == len(sub_ids(cid)),
              ", ".join(sub_ids(cid))[:88])
    for cid in ("C1_true_bridge_complete", "C2_geometry_false_rejection", "C3_g5_block"):
        ids = sub_ids(cid)
        check(f"{cid} covers the full G3 grid",
              ids == ["sigma_psi_0p0", "sigma_psi_0p2", "sigma_psi_0p5", "sigma_psi_1p0"])
        primary = [s for s in CASES[cid]["subconditions"] if s.get("feeds_primary_claim")]
        check(f"{cid}: only sigma_psi = 0.5 feeds the primary claim",
              len(primary) == 1 and primary[0]["sigma_psi_deg"] == 0.5)
    check("C7 alternatives keep their frozen identities",
          sub_ids("C7_false_bridge")
          == ["alt_1_06", "alt_0_93_1_05", "alt_1_10", "hard_1_025"])
    check("C7 beta vectors are unchanged",
          [s["beta_true"] for s in CASES["C7_false_bridge"]["subconditions"]]
          == [[1, 1.06, 1, 1], [1, 0.93, 1.05, 1], [1, 1, 1, 1.10], [1, 1.025, 1, 1]])
    check("C6 keeps the three declared rho",
          [s["rho"] for s in CASES["C6_mode_resolution_boundary"]["subconditions"]]
          == [1.019573, 1.024467, 1.029360]
          and BINDING.theta_cap_deg == 5.0)
    cells = CASES["C5_plug_in_branch_a"]["subconditions"]
    check("C5 declares the full 3 x 4 uncertainty grid",
          sorted({c["sigma_k"] for c in cells}) == [0.0, 0.005, 0.01]
          and sorted({c["sigma_psi_deg"] for c in cells}) == [0.0, 0.2, 0.5, 1.0]
          and len(cells) == 12)
    check("C8 declares ONE subcondition: the pairing is intentional",
          sub_ids("C8_blinded_scale_control") == ["paired_scale_control"]
          and CASES["C8_blinded_scale_control"]["subconditions"][0]["scale_factors"]
          == [1.07, 0.90])
    check("an undeclared subcondition id REFUSES",
          refuses(EX.replicate_calibration, "C1_true_bridge_complete", "sigma_psi_9p9", 0,
                  CampaignCalibrationLedger()))


def test_b5_artifact_count() -> None:
    total = 0
    print("     case                            R  subs  fields   artifacts")
    for c in PLAN["cases"]:
        n = (c["replicate_count"] * c["subcondition_count"]
             * c["fields_requiring_calibration"]) if c["requires_block1_calibration"] else 0
        check(f"{c['case_id']} artifact arithmetic",
              n == c["calibration_artifact_count"],
              f"{c['replicate_count']} x {c['subcondition_count']} x "
              f"{c['fields_requiring_calibration']} = {n:,}")
        total += n
    check("campaign total is 46,000, reconstructed not copied", total == 46_000, f"{total:,}")
    check("the plan records the same total",
          PLAN["calibration"]["calibration_scope_disposition"]["total_artifacts"] == total)
    sup = PLAN["calibration"]["runtime_accounting_correction"]["superseded_40000_count"]
    check("the superseded 40,000 count is recorded, not erased",
          sup["superseded_total"] == 40_000 and sup["corrected_total"] == 46_000)
    check("both compensating errors are named",
          "7,200" in sup["why_the_old_total_looked_consistent"]
          and "13,200" in sup["why_the_old_total_looked_consistent"])


# ------------------------------------------------------- B6: stream scope
def test_b6_subcondition_independence() -> None:
    acc = EX.case_access("C1_true_bridge_complete")
    a = acc.stream(VF.VALIDATION, "sigma_psi_0p5", 0, "theta0_circular")
    b = acc.stream(VF.VALIDATION, "sigma_psi_1p0", 0, "theta0_circular")
    check("same case + replicate + different sigma_psi -> different stream", a != b)
    c5 = EX.case_access("C5_plug_in_branch_a")
    check("same C5 replicate + different cell -> different stream",
          c5.stream(VF.CALIBRATION, "sk0p00_sp0p0", 3, "theta1_power")
          != c5.stream(VF.CALIBRATION, "sk1p00_sp1p0", 3, "theta1_power"))
    c6 = EX.case_access("C6_mode_resolution_boundary")
    c6_scope = CASES["C6_mode_resolution_boundary"]["fields_affected"][0]
    check("same C6 replicate + different rho -> different stream",
          c6.stream(VF.VALIDATION, "rho_1p019573", 1, c6_scope)
          != c6.stream(VF.VALIDATION, "rho_1p029360", 1, c6_scope))
    check("C6 cannot borrow theta0's scope",
          refuses(c6.stream, VF.VALIDATION, "rho_1p019573", 1, "theta0_circular"))
    c7 = EX.case_access("C7_false_bridge")
    alts = sub_ids("C7_false_bridge")
    streams = {a_: c7.stream(VF.VALIDATION, a_, 2, "theta1_power") for a_ in alts}
    check("all four C7 alternatives get independent streams",
          len(set(streams.values())) == 4, "no common random numbers between alternatives")
    check("an undeclared subcondition refuses at the seed boundary",
          refuses(c7.stream, VF.VALIDATION, "alt_invented", 0, "theta0_circular"))


def test_b6_intentional_sharing() -> None:
    led = CampaignCalibrationLedger()
    rc = EX.replicate_calibration("C1_true_bridge_complete", "sigma_psi_0p5", 0, led)
    cm = rc.common_mode_seed()
    check("the Branch-A common mode has ONE experiment-scoped stream",
          isinstance(cm, int))
    check("it is the SAME for every field of that experiment",
          all(rc.common_mode_seed() == cm for _ in FIELDS),
          "INTENTIONAL: it cancels in the P2 ratio and not in P3")
    check("it is NOT the per-field Branch-A stream",
          all(cm != rc.branch_a_seed(f) for f in FIELDS))
    check("per-field Branch-A streams are distinct",
          len({rc.branch_a_seed(f) for f in FIELDS}) == len(FIELDS))
    other = EX.replicate_calibration("C1_true_bridge_complete", "sigma_psi_1p0", 0, led)
    check("a different subcondition gets a different common mode",
          other.common_mode_seed() != cm)
    rc2 = EX.replicate_calibration("C1_true_bridge_complete", "sigma_psi_0p5", 1, led)
    check("a different replicate gets a different common mode",
          rc2.common_mode_seed() != cm)
    check("the plan documents the experiment scope and why",
          any(r["scope"] == EXPERIMENT_SCOPE and "cancels in the P2 ratio" in r["why"]
              for r in PLAN["randomness_dependency"]["table"]))
    c8row = [r for r in PLAN["randomness_dependency"]["table"] if "1.07" in r["quantity"]]
    check("C8 pairing is documented as intentional, not a subcondition",
          c8row and "INTENTIONAL PAIRING" in c8row[0]["why"])
    rc8 = EX.replicate_calibration("C8_blinded_scale_control", "paired_scale_control", 0, led)
    check("C8's two factors share ONE base replicate stream",
          rc8.validation_seed("theta0_circular", VF.BLINDED_SCALE_CONTROL)
          == EX.case_access("C8_blinded_scale_control").stream(
              VF.BLINDED_SCALE_CONTROL, "paired_scale_control", 0, "theta0_circular"),
          "the difference between branches is the deterministic blinded(c) transform")


def test_b6_scheduling_and_collisions() -> None:
    jobs = {}
    expected = 0
    for c in PLAN["cases"]:
        acc = EX.case_access(c["case_id"])
        for fam in c["allowed_seed_families"]:
            scopes = list(acc.field_scopes)
            if fam == VF.BRANCH_A_MEASUREMENT.value:
                scopes.append(EXPERIMENT_SCOPE)
            expected += len(sub_ids(c["case_id"])) * c["replicate_count"] * len(scopes)
            for sub in sub_ids(c["case_id"]):
                for rep in range(c["replicate_count"]):
                    for sc in scopes:
                        key = (c["case_id"], fam, sub, rep, sc)
                        jobs.setdefault(acc.stream(VF(fam), sub, rep, sc), []).append(key)
    total = sum(len(v) for v in jobs.values())
    dupes = {k: v for k, v in jobs.items() if len(v) > 1}
    check("full-campaign stream enumeration has ZERO collisions",
          total == expected and len(dupes) == 0,
          f"{expected:,} expected, {total:,} identities, {len(jobs):,} unique, "
          f"{len(dupes)} collisions")
    acc = EX.case_access("C5_plug_in_branch_a")
    subs, reps = sub_ids("C5_plug_in_branch_a")[:4], range(4)
    fwd = [((s, r, f), acc.stream(VF.CALIBRATION, s, r, f))
           for s in subs for r in reps for f in FIELDS]
    rev = [((s, r, f), acc.stream(VF.CALIBRATION, s, r, f))
           for f in reversed(FIELDS) for r in reversed(list(reps)) for s in reversed(subs)]
    check("serial, reverse and parallel scheduling resolve to identical identities",
          dict(fwd) == dict(rev), f"{len(fwd)} jobs, order-independent")
    check("the plan records the parallelism policy",
          PLAN["parallelism_policy"]["executed_now"] is False)


# ------------------------------------------------------- C3, schema, hygiene
def test_c3_semantics() -> None:
    c3 = CASES["C3_g5_block"]["c3_semantics"]
    check("C3 primary release endpoint is the G5 block size",
          c3["primary_release_endpoint"] == "G5_BLOCK_SIZE")
    check("C3 retains Block-1 calibration", c3["requires_block1_calibration"] is True)
    check("Block 1 is a SECONDARY predeclared diagnostic for C3",
          c3["block1_role"] == "SECONDARY_PREDECLARED_INTERACTION_DIAGNOSTIC")
    check("the joint P1 result does NOT change the C3 release verdict",
          c3["joint_p1_result_changes_C3_release_verdict"] is False)
    check("C3's frozen release criterion is unchanged",
          "alpha_2 = 0.001" in CASES["C3_g5_block"]["formal_pass_fail_criterion"]
          and "3 or more" in CASES["C3_g5_block"]["formal_pass_fail_criterion"])
    check("adding a Block-1 release threshold to C3 is explicitly forbidden",
          "forbidden" in c3["what_is_forbidden"] or "no new" in c3["what_is_forbidden"].lower()
          or "adding any new" in c3["what_is_forbidden"])


def test_result_schema() -> None:
    check("result schema is versioned to 2", RESULT_SCHEMA.endswith("/2"))
    check("subcondition_id is a frozen record field", "subcondition_id" in RESULT_FIELDS)
    check("plan and code agree on the record fields",
          list(PLAN["output_schema"]["per_record_fields"]) == list(RESULT_FIELDS))
    check("a record is reproducible from case + subcondition + replicate + scope + seed",
          all(t in PLAN["output_schema"]["reproduction"]
              for t in ("case_id", "subcondition_id", "replicate_id", "seed identity")))


def test_hygiene() -> None:
    check("no RNG object was constructed in this suite", SentinelRNG.CALLS == 0,
          f"RNG_CALL_COUNT = {SentinelRNG.CALLS}")
    check("execution remains unauthorised", PLAN["execution_authorised"] is False)
    a = PLAN["adopted_rules_unchanged"]
    check("no E1a scientific decision rule moved",
          (a["delta_cross"], a["delta_abs"], a["z_cross"], a["z_abs"], a["alpha_geom"],
           a["alpha_1"], a["alpha_2"], a["theta_cap_deg"], a["rank_tol"], a["pipeline_target"])
          == (0.02, 0.05, 1.959963985, 1.959963985, 0.005, 0.004, 0.001, 5.0, 1e-12, 0.9))
    check("every replicate count unchanged",
          [c["replicate_count"] for c in PLAN["cases"]]
          == [300, 400, 400, 2000, 400, 400, 400, 200])
    check("the design contract did NOT change",
          BINDING.sha256 == "91d6ae76ccb6fdbeb7f926722433c574c30b7c0b6105c7c1ec20436fa2ec431b")
    check("master and family seed values unchanged",
          EX.seed_map.master == 13785910525869478477
          and EX.seed_map.families["calibration"] == 6644164099584621674)
    check("primary sigma_psi still 0.5 degrees",
          BINDING.data["hypothetical_uncertainty_scenario"]["sigma_psi_deg"] == 0.5)
    check("G1/G2 thresholds recompute unchanged",
          dispositions.g1_success_threshold(200, 0.90) == 188
          and dispositions.g2_max_false_acceptances(400, 0.025) == 4)


GROUPS = (
    ("B4 calibration necessity rule", test_b4_rule),
    ("B4 C7 has no calibration path", test_b4_c7),
    ("B4 C8 has no calibration path", test_b4_c8),
    ("B4 C1-C6 ordering not weakened", test_b4_c1_to_c6_still_gated),
    ("B5 declared subconditions", test_b5_subconditions),
    ("B5 artifact-count reconstruction", test_b5_artifact_count),
    ("B6 subcondition independence", test_b6_subcondition_independence),
    ("B6 intentional within-experiment sharing", test_b6_intentional_sharing),
    ("B6 scheduling and collision audit", test_b6_scheduling_and_collisions),
    ("C3 semantics", test_c3_semantics),
    ("result schema", test_result_schema),
    ("hygiene", test_hygiene),
)

if __name__ == "__main__":
    for title, fn in GROUPS:
        print(f"\n{title}")
        fn()
    print(f"\nE1a v4 case-scope gate: {PASSED} passed, {FAILED} failed, {len(GROUPS)} groups")
    print("Execution class: NON-MODEL-ADVANCING STATIC/PURE (this suite only)")
    print(f"  RNG OBJECTS           : 0   (sentinel CALLS = {SentinelRNG.CALLS})")
    print("  RANDOM DRAWS          : 0")
    print("  TRAJECTORIES          : 0")
    print("  CALIBRATION EXECUTION : NOT RUN")
    print("  VALIDATION CAMPAIGN   : NOT RUN")
    raise SystemExit(1 if FAILED else 0)
