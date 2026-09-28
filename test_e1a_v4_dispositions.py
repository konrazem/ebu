"""E1a v4 author-disposition conformance gate (G1, G2, G3).

**EXECUTION CLASS: NON-MODEL-ADVANCING STATIC/PURE.** Every input is hand-authored.
No random number is drawn, no RNG object is constructed, no trajectory is generated.
Both Clopper-Pearson integer thresholds are RECOMPUTED here, never copied from the plan.
"""

from __future__ import annotations

import json
import os

from e1a_v4.contract import load_contract, sha256_file
from e1a_v4.endpoints import UncertaintyModel, p3_absolute
from e1a_v4.geometry import FieldAnalysis
from e1a_v4.identity import procedure_identity
from e1a_v4.numerics import Refusal
from e1a_v4.status import AnalysisStatus
from e1a_v4.validation.dispositions import (
    BLINDED_SCALE_FACTORS, cp_lower, cp_upper, g1_blinded_branch, g1_campaign_pass,
    g1_paired_replicate, g1_success_threshold, g2_alternative_pass, g2_campaign_pass,
    g2_max_false_acceptances, g3_classification, g3_primary_claim_inputs,
    g3_primary_sigma_psi, g3_role, scaled_analyses,
)
from e1a_v4.validation.plan import execution_identity, load_plan, load_seed_map
from e1a_v4.validation.seeds import FrozenSeedMap

PASSED = 0
FAILED = 0
ROOT = os.path.dirname(os.path.abspath(__file__))
BINDING = load_contract(ROOT)
PLAN = load_plan(ROOT)
SEEDMAP = load_seed_map(ROOT)
IDS = [f["id"] for f in BINDING.fields]
TIGHT = UncertaintyModel(sigma_cm=1e-9, sigma_fs=1e-9, sigma_stat={i: 1e-9 for i in IDS})
REAL = UncertaintyModel(sigma_cm=0.0115, sigma_fs=0.00242747,
                        sigma_stat={i: 0.002 for i in IDS})


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


def analyses(betas: dict[str, float | None]) -> dict[str, FieldAnalysis]:
    out = {}
    for fid, b in betas.items():
        out[fid] = (FieldAnalysis(fid, AnalysisStatus.RANK_GUARD_FAIL, "fixture") if b is None
                    else FieldAnalysis(fid, AnalysisStatus.ESTIMATED, "", beta_hat=b))
    return out


# ------------------------------------------------------------------ G1
def test_g1() -> None:
    c = 1.07
    blinded = analyses({i: 1.0 / c for i in IDS})
    scaled = scaled_analyses(blinded, c)
    check("transformed blinded beta is exactly c * beta_hat",
          all(abs(scaled[i].require_beta() - 1.0) < 1e-12 for i in IDS),
          f"c = {c}, beta_hat = 1/c")
    direct = p3_absolute(scaled, BINDING, TIGHT)
    branch = g1_blinded_branch(blinded, BINDING, TIGHT, c)
    check("the SAME P3 rule is reused, not a new tolerance",
          branch.passed == direct.passed and branch.rows == direct.rows)
    check("G1 uses the adopted P3 margin and coverage factor, read from the contract",
          BINDING.delta_abs == 0.05 and BINDING.z_abs == 1.959963985)
    check("G1 branch passes when recovery is exact", branch.passed)
    off = dict(blinded)
    off[IDS[2]] = FieldAnalysis(IDS[2], AnalysisStatus.ESTIMATED, "", beta_hat=(1.0 / c) * 1.12)
    check("one field outside the 5% band fails the branch",
          not g1_blinded_branch(off, BINDING, TIGHT, c).passed)
    miss = dict(blinded)
    miss[IDS[3]] = FieldAnalysis(IDS[3], AnalysisStatus.RANK_GUARD_FAIL, "fixture")
    check("a non-ESTIMATED field fails the branch",
          not g1_blinded_branch(miss, BINDING, TIGHT, c).passed)
    check("all four fields are evaluated", len(branch.rows) == 4)
    check("the declared factors are exactly 1.07 and 0.90",
          BLINDED_SCALE_FACTORS == (1.07, 0.90))
    both = {f: analyses({i: 1.0 / f for i in IDS}) for f in BLINDED_SCALE_FACTORS}
    check("a replicate passes only when BOTH factors pass",
          g1_paired_replicate(both, BINDING, TIGHT).passed)
    one_bad = dict(both)
    one_bad[0.90] = analyses({**{i: 1.0 / 0.90 for i in IDS}, IDS[1]: (1.0 / 0.90) * 1.15})
    check("failing the c = 0.90 branch fails the replicate",
          not g1_paired_replicate(one_bad, BINDING, TIGHT).passed)
    absent = {1.07: both[1.07]}
    check("a missing branch fails the replicate",
          not g1_paired_replicate(absent, BINDING, TIGHT).passed)
    thr = g1_success_threshold(200, 0.90)
    check("CP lower threshold RECOMPUTED for R = 200, target 0.90", thr == 188,
          f"cp_lower({thr},200) = {cp_lower(thr,200):.6f}")
    check("one count below the threshold fails",
          cp_lower(thr - 1, 200) < 0.90, f"cp_lower({thr-1},200) = {cp_lower(thr-1,200):.6f}")
    ok, bound, t = g1_campaign_pass(188, 200, 0.90)
    check("188/200 passes the campaign criterion", ok and t == 188, f"CP lower = {bound:.6f}")
    ok2, bound2, _ = g1_campaign_pass(187, 200, 0.90)
    check("187/200 fails the campaign criterion", not ok2, f"CP lower = {bound2:.6f}")
    check("plan records the derived threshold, and it matches the recomputation",
          PLAN["author_dispositions"]["G1"]["campaign_criterion"]["integer_threshold"] == thr)
    check("G1 does not alter P3 itself",
          p3_absolute(analyses({i: 1.0 for i in IDS}), BINDING, TIGHT).passed)


# ------------------------------------------------------------------ G2
def test_g2() -> None:
    declared = BINDING.data["false_bridge_controls"]["controls"]
    check("declared alternatives unchanged",
          any("(1,1.06,1,1)" in x and "(1,0.93,1.05,1)" in x and "(1,1,1,1.10)" in x
              and "hard 2.5%" in x for x in declared))
    thr = g2_max_false_acceptances(400, 0.025)
    check("CP upper threshold RECOMPUTED for R = 400, target 0.025", thr == 4,
          f"cp_upper({thr},400) = {cp_upper(thr,400):.6f}")
    check("the next count fails", cp_upper(thr + 1, 400) > 0.025,
          f"cp_upper({thr+1},400) = {cp_upper(thr+1,400):.6f}")
    ok, bound, t = g2_alternative_pass(4, 400, 0.025)
    check("4/400 passes", ok and t == 4, f"CP upper = {bound:.6f}")
    ok5, bound5, _ = g2_alternative_pass(5, 400, 0.025)
    check("5/400 fails", not ok5, f"CP upper = {bound5:.6f}")
    check("target is exactly 0.025",
          BINDING.data["synthetic_validation_release_criteria"]
                      ["G2_false_bridge_discrimination"]["max_false_acceptance_probability"] == 0.025)
    check("0.025 is tied to the equivalence z, not to an observed outcome",
          "NOT derived from observed validation outcomes" in
          BINDING.data["synthetic_validation_release_criteria"]
                      ["G2_false_bridge_discrimination"]["tie"])
    res = g2_campaign_pass({"alt_1_06": 0, "alt_0_93_1_05": 1, "alt_1_10": 0, "hard_1_025": 4})
    check("every alternative satisfying the rule passes", res.passed)
    res2 = g2_campaign_pass({"alt_1_06": 0, "alt_0_93_1_05": 0, "alt_1_10": 0, "hard_1_025": 5})
    check("ONE alternative at 5/400 fails the whole campaign", not res2.passed,
          "counts are never pooled; the hard case cannot be rescued by easy ones")
    pooled = (0 + 0 + 0 + 5)
    check("pooling would have hidden the failure",
          g2_alternative_pass(pooled // 4, 400, 0.025)[0] and not res2.passed,
          f"mean {pooled/4:.2f}/400 would pass, but the rule is per alternative")
    check("each alternative is evaluated independently", len(res2.rows) == 4)
    check("plan records the derived threshold, and it matches the recomputation",
          PLAN["author_dispositions"]["G2"]["campaign_criterion"]["integer_threshold"] == thr)


# ------------------------------------------------------------------ G3
def test_g3() -> None:
    check("primary sigma_psi is exactly 0.5 degrees", g3_primary_sigma_psi(BINDING) == 0.5)
    cls = g3_classification(BINDING)
    check("0.0 and 0.2 are secondary", cls["secondary_lower_uncertainty_sensitivity"] == [0.0, 0.2])
    check("1.0 is stress", cls["stress_robustness"] == [1.0])
    check("roles resolve correctly",
          g3_role(BINDING, 0.5) == "PRIMARY" and g3_role(BINDING, 0.0) == "SECONDARY"
          and g3_role(BINDING, 0.2) == "SECONDARY" and g3_role(BINDING, 1.0) == "STRESS")
    check("a value off the declared grid is refused", refuses(g3_role, BINDING, 0.7))
    check("the >= 0.90 claim is asserted at the primary value",
          "0.5 degrees" in cls["primary_claim"] and ">= 0.90" in cls["primary_claim"])
    got = g3_primary_claim_inputs(BINDING, {0.0: 296, 0.2: 294, 0.5: 285, 1.0: 240})
    check("only the primary scenario feeds the primary claim",
          got["primary_sigma_psi_deg"] == 0.5 and got["primary_successes"] == 285)
    check("the stress result cannot overwrite the primary classification",
          got["excluded_from_primary"] == {0.0: 296, 0.2: 294, 1.0: 240}
          and got["pooling_prohibited"] is True)
    check("a missing primary scenario is refused",
          refuses(g3_primary_claim_inputs, BINDING, {0.0: 296, 1.0: 240}))
    check("the stress case is not removed for performing poorly",
          "not removed if it performs poorly" in cls["reporting_rule"])
    check("it remains a hypothetical scenario, not a measured capability",
          "HYPOTHETICAL" in cls["status"] and "Not a claim" in cls["status"])


# ------------------------------------------------------------------ identities
def test_identities_and_seeds() -> None:
    old = PLAN["superseded_package"]["old_identities"]
    new = PLAN["frozen_identities"]
    check("the contract hash changed", old["contract"] != new["contract_sha256"])
    check("the design hash changed", old["design"] != new["design_sha256"])
    check("the analysis identity changed with the contract",
          old["analysis_identity"] != new["analysis_procedure_identity"])
    check("the frozen analysis identity matches a live recomputation",
          procedure_identity(BINDING, {}, ROOT) == new["analysis_procedure_identity"])
    plan_sha = sha256_file(os.path.join(ROOT, "docs/e1a/e1a_v4_synthetic_validation_plan.json"))
    seed_sha = sha256_file(os.path.join(ROOT, "docs/e1a/e1a_v4_seed_map.json"))
    check("the plan hash changed", old["plan_json"] != plan_sha)
    check("the seed-map hash changed", old["seed_map"] != seed_sha)
    exec_id = execution_identity(BINDING, plan_sha, seed_sha, ROOT)
    check("the execution identity changed", old["execution_identity"] != exec_id, exec_id[:16] + "...")
    derived = FrozenSeedMap.derive(BINDING.sha256, SEEDMAP["campaign"])
    check("the seed map mechanically rederives under the NEW authority",
          derived.as_json()["families"] == SEEDMAP["families"]
          and derived.master == SEEDMAP["master_seed"])
    check("every seed actually changed",
          all(SEEDMAP["families"][k] != old["families"][k] for k in old["families"]))
    vals = list(SEEDMAP["families"].values())
    check("no seed overlap", len(set(vals)) == len(vals), f"{len(vals)} families")
    check("seeds are still derived, never hand-picked",
          SEEDMAP["derivation"]["hand_picked_values"] is False)
    import ast
    tree = ast.parse(open(os.path.join(ROOT, "e1a_v4/validation/dispositions.py"),
                          encoding="utf-8").read())
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            imported.add(node.module.split(".")[0])
    check("the disposition module imports no RNG source",
          not ({"random", "secrets", "os", "numpy"} & imported), f"imports {sorted(imported)}")
    calls = {n.func.attr for n in ast.walk(tree)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
    check("the disposition module contains no draw call site",
          not ({"normal", "gauss", "random", "uniform", "shuffle", "sample"} & calls),
          f"{len(calls)} attribute call sites, none a draw")


def test_nothing_else_moved() -> None:
    check("P2 margin unchanged", BINDING.delta_cross == 0.02)
    check("P3 margin unchanged", BINDING.delta_abs == 0.05)
    check("z factors unchanged", BINDING.z_cross == 1.959963985 and BINDING.z_abs == 1.959963985)
    check("alpha allocations unchanged",
          (BINDING.alpha_geom, BINDING.alpha_1, BINDING.alpha_2) == (0.005, 0.004, 0.001))
    check("theta_cap unchanged", BINDING.theta_cap_deg == 5.0)
    check("rank_tol unchanged", BINDING.rank_tol == 1e-12)
    check("four physical fields unchanged",
          [f["id"] for f in BINDING.fields] ==
          ["theta0_circular", "theta1_power", "theta2_ellipse", "theta3_temperature"])
    check("complete-pipeline target unchanged", BINDING.pipeline_target == 0.90)
    check("anti-circularity rules unchanged",
          set(BINDING.authorised_branch_a_routes) ==
          {"force_displacement_with_stokes_drag", "independent_calibrated_thermometry"})
    check("P4 classification unchanged",
          BINDING.data["endpoints"]["P4_entropy"]["classification"]
          == "DETERMINISTIC PHYSICAL/THEORETICAL CONSISTENCY CHECK")
    check("execution remains unauthorised", PLAN["execution_authorised"] is False)


def main() -> int:
    groups = (("G1 blinded scale control", test_g1),
              ("G2 false-bridge discrimination", test_g2),
              ("G3 primary sigma_psi", test_g3),
              ("rebound identities and seeds", test_identities_and_seeds),
              ("nothing else moved", test_nothing_else_moved))
    for label, fn in groups:
        print(f"\n{label}")
        fn()
    print(f"\nE1a v4 disposition gate: {PASSED} passed, {FAILED} failed, {len(groups)} groups")
    print("Execution class: NON-MODEL-ADVANCING STATIC/PURE (this suite only)")
    print("  RANDOM DRAWS          : 0")
    print("  TRAJECTORIES          : 0")
    print("  CALIBRATION EXECUTION : NOT RUN")
    print("  VALIDATION CAMPAIGN   : NOT RUN")
    print(f"  G1 threshold (derived): >= {g1_success_threshold(200, 0.90)} / 200")
    print(f"  G2 threshold (derived): <= {g2_max_false_acceptances(400, 0.025)} / 400")
    print(f"  primary sigma_psi     : {g3_primary_sigma_psi(BINDING)} degrees")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())
