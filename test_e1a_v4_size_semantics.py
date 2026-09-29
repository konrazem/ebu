"""E1a v4 size-validation semantics conformance gate.

**EXECUTION CLASS: NON-MODEL-ADVANCING STATIC/PURE.** Every count below is a
hand-authored fixture. No random number is drawn, no RNG object is constructed, no
trajectory is generated. All three Clopper-Pearson boundaries are RECOMPUTED here,
never copied from the plan.
"""

from __future__ import annotations

import json
import os

from e1a_v4.contract import load_contract, sha256_file
from e1a_v4.numerics import Refusal
from e1a_v4.validation.classification import (
    GROSS_INFLATION_TOLERANCE, RELEASE_FAILING_CLASSIFICATIONS, SIZE_FAILURE,
    SIZE_INTERPRETATION, SIZE_NO_INFLATION, CampaignCounts, classify_campaign,
    classify_size, size_boundary, size_inflation_detected,
)
from e1a_v4.validation.dispositions import cp_lower, cp_upper
from e1a_v4.validation.plan import VALIDATION_MODULES, load_plan

PASSED = 0
FAILED = 0
ROOT = os.path.dirname(os.path.abspath(__file__))
BINDING = load_contract(ROOT)
PLAN = load_plan(ROOT)
FIELDS = [f["id"] for f in BINDING.fields]
ALTS = ("alt_1_06", "alt_0_93_1_05", "alt_1_10", "hard_1_025")


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


def boundary_case(label: str, n: int, nominal: float, expected: int) -> None:
    derived = size_boundary(n, nominal)
    check(f"{label}: boundary RECOMPUTED, not copied", derived == expected,
          f"size_boundary({n}, {nominal}) = {derived}")
    check(f"{label}: CP_lower({derived},{n}) <= {nominal}", cp_lower(derived, n) <= nominal,
          f"{cp_lower(derived, n):.10f}")
    check(f"{label}: CP_lower({derived+1},{n}) > {nominal}", cp_lower(derived + 1, n) > nominal,
          f"{cp_lower(derived + 1, n):.10f}")
    check(f"{label}: {derived} does NOT trigger inflation",
          not size_inflation_detected(derived, n, nominal)
          and classify_size(derived, n, nominal)["verdict"] == SIZE_NO_INFLATION)
    check(f"{label}: {derived+1} DOES trigger inflation",
          size_inflation_detected(derived + 1, n, nominal)
          and classify_size(derived + 1, n, nominal)["verdict"] == SIZE_FAILURE)
    check(f"{label}: 0 rejections never triggers",
          not size_inflation_detected(0, n, nominal))
    plan_b = PLAN["size_validation_semantics"]["derived_boundaries"][label]["boundary"]
    check(f"{label}: plan records the same boundary", plan_b == derived, f"plan says {plan_b}")


def test_c2() -> None:
    boundary_case("C2", 400, 0.005, 5)
    check("C2 nominal alpha is alpha_geom from the contract",
          PLAN["size_validation_semantics"]["derived_boundaries"]["C2"]["nominal_alpha"]
          == BINDING.alpha_geom == 0.005)
    check("C2 is per field and pooling is forbidden",
          PLAN["size_validation_semantics"]["derived_boundaries"]["C2"]["per_field"] is True
          and "FORBIDDEN" in PLAN["size_validation_semantics"]["derived_boundaries"]["C2"]["pooling"])


def test_c3() -> None:
    boundary_case("C3", 400, 0.001, 2)
    check("C3 nominal alpha is alpha_2 from the contract",
          PLAN["size_validation_semantics"]["derived_boundaries"]["C3"]["nominal_alpha"]
          == BINDING.alpha_2 == 0.001)


def test_c4() -> None:
    boundary_case("C4", 2000, 0.004, 13)
    check("C4 nominal alpha is alpha_1 from the contract",
          PLAN["size_validation_semantics"]["derived_boundaries"]["C4"]["nominal_alpha"]
          == BINDING.alpha_1 == 0.004)
    check("C4 still retains its discrepancy report",
          "does not replace" in PLAN["size_validation_semantics"]["derived_boundaries"]["C4"]["retains"])
    res = classify_size(13, 2000, 0.004)
    check("C4 diagnostic reports BOTH bounds, not just the binary verdict",
          "cp_lower" in res and "cp_upper" in res and "observed_rate" in res)


def test_interpretation() -> None:
    check("a pass is worded as 'no significant inflation detected'",
          SIZE_INTERPRETATION["verdict_on_pass"] == SIZE_NO_INFLATION)
    check("the machine-readable record states what a pass does NOT mean",
          "mathematically proved" in SIZE_INTERPRETATION["does_not_mean"])
    check("'nominal size proved' is explicitly forbidden wording",
          "NOMINAL SIZE PROVED" in SIZE_INTERPRETATION["forbidden_wording"])
    blob = json.dumps(PLAN["size_validation_semantics"])
    check("the frozen plan carries the same distinction",
          "did not establish excess size" in blob and "mathematically proved" in blob)
    for bad in SIZE_INTERPRETATION["forbidden_wording"]:
        check(f"no verdict string asserts {bad!r}", bad not in (SIZE_NO_INFLATION, SIZE_FAILURE))
    md = open(os.path.join(ROOT, "docs/e1a/E1A_V4_SYNTHETIC_VALIDATION_PLAN.md"),
              encoding="utf-8").read()
    check("the Markdown plan states what a pass does not mean",
          "does **not** mean" in md and "Forbidden wording" in md)
    sup = PLAN["size_validation_semantics"]["superseded_criterion"]
    check("the 3% rule is recorded as superseded, not erased",
          sup["status"].startswith("SUPERSEDED") and sup["tolerance"] == GROSS_INFLATION_TOLERANCE)
    check("its provenance is preserved",
          "475633c" in sup["preserved_in"] and "rewritten" in sup["preserved_in"],
          sup["preserved_in"])
    check("the 15x G5 discrepancy is recorded",
          "15x" in sup["why_insufficient"]["C3"])
    check("the secondary diagnostic is labelled, not called validation",
          "NOT validation of the nominal alpha" in classify_size(1, 400, 0.005)
          ["secondary_gross_diagnostic"]["label"])


# ------------------------------------------------------------------ campaign
def counts(**over) -> CampaignCounts:
    base = dict(c1_successes=290,
                c2_rejections_by_field={f: 2 for f in FIELDS},
                c3_rejections=1, c4_rejections=8,
                c5_pass=True, c6_pass=True,
                c7_false_acceptances_by_alternative={a: 1 for a in ALTS},
                c8_successes=195, hard_failures=(), refusal_accounting_ok=True)
    base.update(over)
    return CampaignCounts(**base)


def test_campaign() -> None:
    ok = classify_campaign(counts())
    check("all required cases pass -> VALIDATION_PASS",
          ok["verdict"] == "VALIDATION_PASS" and ok["failures"] == [],
          f"C1 cp_lower = {ok['detail']['C1']['cp_lower']:.6f}")
    check("C1 threshold is 279/300 and 290 clears it",
          ok["detail"]["C1"]["threshold"] == 279 and ok["detail"]["C1"]["passed"])

    for label, over, expect in (
        ("C1 fails alone", dict(c1_successes=278), "TRUE_BRIDGE_POWER_FAILURE"),
        ("C2 fails alone", dict(c2_rejections_by_field={**{f: 2 for f in FIELDS}, FIELDS[2]: 6}),
         "STATISTICAL_SIZE_FAILURE"),
        ("C3 fails alone", dict(c3_rejections=3), "STATISTICAL_SIZE_FAILURE"),
        ("C4 fails alone", dict(c4_rejections=14), "STATISTICAL_SIZE_FAILURE"),
        ("C5 fails alone", dict(c5_pass=False), "STATISTICAL_SIZE_FAILURE"),
        ("C6 fails alone", dict(c6_pass=False), "MODE_RESOLUTION_FAILURE"),
        ("C7 hard alternative fails alone",
         dict(c7_false_acceptances_by_alternative={**{a: 1 for a in ALTS}, "hard_1_025": 5}),
         "FALSE_BRIDGE_DISCRIMINATION_FAILURE"),
        ("C8 fails alone", dict(c8_successes=187), "BLINDED_SCALE_CONTROL_FAILURE"),
        ("a software failure alone", dict(hard_failures=("SOFTWARE_OR_INVARIANT_FAILURE",)),
         "SOFTWARE_OR_INVARIANT_FAILURE"),
        ("refusal accounting broken alone", dict(refusal_accounting_ok=False),
         "STRUCTURED_REFUSAL_EXCESS"),
    ):
        res = classify_campaign(counts(**over))
        check(f"{label} -> failure",
              res["verdict"] == "VALIDATION_FAILURE"
              and any(expect in f for f in res["failures"]),
              "; ".join(res["failures"])[:70])

    check("C1 at exactly 279 passes", classify_campaign(counts(c1_successes=279))["verdict"]
          == "VALIDATION_PASS")
    check("C2 at exactly 5 per field passes",
          classify_campaign(counts(c2_rejections_by_field={f: 5 for f in FIELDS}))["verdict"]
          == "VALIDATION_PASS")
    check("C3 at exactly 2 passes", classify_campaign(counts(c3_rejections=2))["verdict"]
          == "VALIDATION_PASS")
    check("C4 at exactly 13 passes", classify_campaign(counts(c4_rejections=13))["verdict"]
          == "VALIDATION_PASS")
    check("C7 at exactly 4 per alternative passes",
          classify_campaign(counts(c7_false_acceptances_by_alternative={a: 4 for a in ALTS}))
          ["verdict"] == "VALIDATION_PASS")
    check("C8 at exactly 188 passes", classify_campaign(counts(c8_successes=188))["verdict"]
          == "VALIDATION_PASS")

    mixed = classify_campaign(counts(c1_successes=295, c3_rejections=3))
    check("C1 meeting the target does NOT rescue a size failure",
          mixed["verdict"] == "VALIDATION_FAILURE"
          and mixed["independent_facts"]["complete_pipeline_met"] is True
          and mixed["independent_facts"]["component_size_clean"] is False,
          "both facts reported separately, never collapsed")
    other = classify_campaign(counts(c1_successes=270))
    check("a size-clean campaign can still fail on complete-pipeline success",
          other["verdict"] == "VALIDATION_FAILURE"
          and other["independent_facts"]["complete_pipeline_met"] is False
          and other["independent_facts"]["component_size_clean"] is True)
    check("no weighted score and no compensation",
          "no weighted" in classify_campaign(counts())["rule"]
          and "no compensation" in classify_campaign(counts())["rule"])
    multi = classify_campaign(counts(c1_successes=270, c3_rejections=3, c8_successes=180))
    check("multiple failures are all listed, none swallowed", len(multi["failures"]) == 3,
          "; ".join(multi["failures"])[:80])
    check("C2 is evaluated per field, all four reported",
          len(classify_campaign(counts())["detail"]["C2"]) == 4)
    check("release-failing classifications are exactly the three declared",
          RELEASE_FAILING_CLASSIFICATIONS ==
          ("SOFTWARE_OR_INVARIANT_FAILURE", "CALIBRATION_FAILURE", "NUMERICAL_OR_PRECISION_FAILURE"))
    check("a non-release-failing classification does not fail the campaign",
          classify_campaign(counts(hard_failures=("VALIDATION_INCONCLUSIVE",)))["verdict"]
          == "VALIDATION_PASS")
    # Eleven since the release-authority repair: requirement 11 makes the MANDATORY
    # CONTRACT DIAGNOSTICS part of the conjunctive release rule rather than prose.
    check("plan and code agree on the eleven requirements",
          len(PLAN["final_campaign_classification"]["requirements"]) == 11)
    check("the eleventh requirement is the mandatory-diagnostic rule",
          "MANDATORY CONTRACT DIAGNOSTIC"
          in PLAN["final_campaign_classification"]["requirements"][10]
          and "RESULT_SCHEMA_INVALID"
          in PLAN["final_campaign_classification"]["requirements"][10])
    check("out-of-range counts are refused", refuses(size_inflation_detected, 401, 400, 0.005))


def test_nothing_else_moved() -> None:
    check("alpha allocations unchanged",
          (BINDING.alpha_geom, BINDING.alpha_1, BINDING.alpha_2) == (0.005, 0.004, 0.001))
    check("margins unchanged", (BINDING.delta_cross, BINDING.delta_abs) == (0.02, 0.05))
    check("theta_cap and rank_tol unchanged",
          BINDING.theta_cap_deg == 5.0 and BINDING.rank_tol == 1e-12)
    check("primary sigma_psi unchanged at 0.5 degrees",
          BINDING.data["hypothetical_uncertainty_scenario"]["sigma_psi_deg"] == 0.5)
    check("complete-pipeline target unchanged", BINDING.pipeline_target == 0.90)
    check("C1 criterion unchanged: 279/300",
          classify_campaign(counts())["detail"]["C1"]["threshold"] == 279)
    check("G1 threshold unchanged: 188/200",
          classify_campaign(counts())["detail"]["C8"]["threshold"] == 188)
    check("G2 threshold unchanged: 4/400",
          classify_campaign(counts())["detail"]["C7"][ALTS[0]]["threshold"] == 4)
    check("the design contract was NOT changed by this task",
          PLAN["frozen_identities"]["contract_sha256"] == BINDING.sha256
          and BINDING.data["contract_version"] == "1.1.0",
          f"contract still {BINDING.sha256[:12]}, version 1.1.0")
    check("classification.py is registered in the execution identity",
          "e1a_v4/validation/classification.py" in VALIDATION_MODULES)
    check("execution remains unauthorised", PLAN["execution_authorised"] is False)


def main() -> int:
    groups = (("C2 whole P1 geometry gate", test_c2),
              ("C3 G5 block", test_c3),
              ("C4 Block-1 surrogate", test_c4),
              ("interpretation of a pass", test_interpretation),
              ("final campaign classification", test_campaign),
              ("nothing else moved", test_nothing_else_moved))
    for label, fn in groups:
        print(f"\n{label}")
        fn()
    print(f"\nE1a v4 size-semantics gate: {PASSED} passed, {FAILED} failed, {len(groups)} groups")
    print("Execution class: NON-MODEL-ADVANCING STATIC/PURE (this suite only)")
    print("  RANDOM DRAWS          : 0")
    print("  TRAJECTORIES          : 0")
    print("  CALIBRATION EXECUTION : NOT RUN")
    print("  VALIDATION CAMPAIGN   : NOT RUN")
    print(f"  C2 boundary (derived) : 0-{size_boundary(400, 0.005)} of 400 at alpha 0.005")
    print(f"  C3 boundary (derived) : 0-{size_boundary(400, 0.001)} of 400 at alpha 0.001")
    print(f"  C4 boundary (derived) : 0-{size_boundary(2000, 0.004)} of 2000 at alpha 0.004")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())
