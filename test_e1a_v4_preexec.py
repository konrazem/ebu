"""E1a v4 synthetic-validation PRE-EXECUTION conformance gate.

**EXECUTION CLASS: NON-MODEL-ADVANCING STATIC/PURE.** This suite proves, among other
things, that the official runner refuses BEFORE it can obtain a generator. A sentinel
RNG provider counts every call, and each failed-preflight check asserts

    RNG_CALL_COUNT == 0

No random number is drawn, no trajectory is generated, no calibration is sampled and
no scientific outcome is inspected anywhere in this file.
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile

from e1a_v4.contract import load_contract, sha256_file
from e1a_v4.identity import SCIENTIFIC_MODULES, procedure_identity
from e1a_v4.numerics import Refusal
from e1a_v4.validation import PLAN_JSON, SEED_MAP_JSON
from e1a_v4.validation.calibrate import GENERATOR_IDENTITY
from e1a_v4.validation.plan import (
    VALIDATION_MODULES, bind_execution, execution_identity, load_plan, load_seed_map,
)
from e1a_v4.validation.results import (
    FAILURE_CLASSIFICATIONS, RESULT_FIELDS, aggregate_skeleton,
)
from e1a_v4.validation.runner import ExecutionNotAuthorised, main, preflight, run
from e1a_v4.validation.seeds import (
    ANALYSIS_FAMILIES, FrozenSeedMap, ValidationSeedFamily, family_seed, master_seed,
    replicate_seed,
)

PASSED = 0
FAILED = 0
ROOT = os.path.dirname(os.path.abspath(__file__))


class SentinelRNG:
    """Counts every draw. Any call during a preflight is a defect."""

    CALLS = 0

    def normal(self, count: int) -> list[float]:
        type(self).CALLS += 1
        raise AssertionError("SENTINEL: an RNG draw was attempted during preflight")


def rng_factory(seed: int) -> SentinelRNG:
    SentinelRNG.CALLS += 1
    return SentinelRNG()


def check(label: str, condition: bool, detail: str = "") -> None:
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  [PASS] {label}" + (f"  -- {detail}" if detail else ""))
    else:
        FAILED += 1
        print(f"  [FAIL] {label}" + (f"  -- {detail}" if detail else ""))


def refuses_without_rng(label: str, fn, *args, **kwargs) -> None:
    """Assert a refusal AND that the sentinel RNG was never touched."""
    before = SentinelRNG.CALLS
    refused = False
    try:
        fn(*args, **kwargs)
    except Refusal:
        refused = True
    after = SentinelRNG.CALLS
    check(label, refused and after == before, f"RNG_CALL_COUNT delta = {after - before}")


PLAN = load_plan(ROOT)
SEEDMAP = load_seed_map(ROOT)
BINDING = load_contract(ROOT)


def sandbox() -> str:
    tmp = tempfile.mkdtemp()
    for rel in ("docs/e1a/e1a_v4_design_contract.json",
                "docs/e1a/E1A_V4_PROSPECTIVE_DESIGN.md",
                "docs/theory/EBU_THEORY_BASELINE.md",
                "docs/physical_foundation/EBU_PHYSICAL_FOUNDATION_CANONICAL.md",
                PLAN_JSON, SEED_MAP_JSON,
                "docs/e1a/E1A_V4_SYNTHETIC_VALIDATION_PLAN.md"):
        dst = os.path.join(tmp, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy(os.path.join(ROOT, rel), dst)
    shutil.copytree(os.path.join(ROOT, "e1a_v4"), os.path.join(tmp, "e1a_v4"),
                    ignore=shutil.ignore_patterns("__pycache__"))
    return tmp


def write(tmp: str, rel: str, obj) -> None:
    with open(os.path.join(tmp, rel), "w", encoding="utf-8") as handle:
        json.dump(obj, handle, indent=2)
        handle.write("\n")


# ------------------------------------------------------- preflight refuses first
def test_preflight_refuses_before_rng() -> None:
    check("clean tree preflights successfully", preflight(ROOT) is not None)
    start = SentinelRNG.CALLS

    tmp = sandbox()
    c = json.load(open(os.path.join(tmp, "docs/e1a/e1a_v4_design_contract.json")))
    c["endpoints"]["P2_cross_field"]["delta_cross"] = 0.05
    write(tmp, "docs/e1a/e1a_v4_design_contract.json", c)
    refuses_without_rng("FROZEN contract mismatch refuses before RNG", preflight, tmp)
    shutil.rmtree(tmp)

    tmp = sandbox()
    p = json.load(open(os.path.join(tmp, PLAN_JSON)))
    p["cases"][0]["replicate_count"] = 7
    p["frozen_identities"]["execution_identity"] = "f" * 64
    write(tmp, PLAN_JSON, p)
    refuses_without_rng("plan hash mismatch refuses before RNG", preflight, tmp)
    shutil.rmtree(tmp)

    tmp = sandbox()
    p = json.load(open(os.path.join(tmp, PLAN_JSON)))
    p["frozen_identities"]["analysis_procedure_identity"] = "a" * 64
    write(tmp, PLAN_JSON, p)
    refuses_without_rng("analysis procedure mismatch refuses before RNG", preflight, tmp)
    shutil.rmtree(tmp)

    tmp = sandbox()
    p = json.load(open(os.path.join(tmp, PLAN_JSON)))
    key = sorted(p["frozen_identities"]["implementation_file_hashes"])[0]
    p["frozen_identities"]["implementation_file_hashes"][key] = "b" * 64
    write(tmp, PLAN_JSON, p)
    refuses_without_rng("implementation file hash mismatch refuses before RNG", preflight, tmp)
    shutil.rmtree(tmp)

    tmp = sandbox()
    s = json.load(open(os.path.join(tmp, SEED_MAP_JSON)))
    s["families"]["validation"] = 123456789
    write(tmp, SEED_MAP_JSON, s)
    refuses_without_rng("hand-edited seed map refuses before RNG", preflight, tmp)
    shutil.rmtree(tmp)

    tmp = sandbox()
    s = json.load(open(os.path.join(tmp, SEED_MAP_JSON)))
    s["master_seed"] = s["master_seed"] + 1
    write(tmp, SEED_MAP_JSON, s)
    refuses_without_rng("master seed mismatch refuses before RNG", preflight, tmp)
    shutil.rmtree(tmp)

    tmp = sandbox()
    out = os.path.join(tmp, PLAN["output_schema"]["directory"])
    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, "existing_result.json"), "w").write("{}")
    refuses_without_rng("output collision refuses before RNG", preflight, tmp)
    shutil.rmtree(tmp)

    tmp = sandbox()
    p = json.load(open(os.path.join(tmp, PLAN_JSON)))
    p["execution_stage"] = "something_else"
    write(tmp, PLAN_JSON, p)
    refuses_without_rng("unexpected execution stage refuses before RNG", preflight, tmp)
    shutil.rmtree(tmp)

    check("no RNG was created by ANY failed preflight",
          SentinelRNG.CALLS == start, f"RNG_CALL_COUNT = {SentinelRNG.CALLS}")


def test_execution_is_not_authorised() -> None:
    before = SentinelRNG.CALLS
    check("frozen plan has execution_authorised = false",
          PLAN.get("execution_authorised") is False)
    raised = False
    try:
        run(ROOT, rng_factory=rng_factory, execute=True)
    except ExecutionNotAuthorised:
        raised = True
    check("run(execute=True) refuses on the frozen plan", raised)
    check("the RNG factory was never called", SentinelRNG.CALLS == before,
          f"RNG_CALL_COUNT = {SentinelRNG.CALLS}")
    check("preflight-only CLI returns 0", main(["--root", ROOT, "--preflight-only"]) == 0)
    check("--execute without the authorisation flag returns 2",
          main(["--root", ROOT, "--execute"]) == 2)
    check("CLI never drew a random number", SentinelRNG.CALLS == before,
          f"RNG_CALL_COUNT = {SentinelRNG.CALLS}")


# ------------------------------------------------------- seeds
def test_seeds() -> None:
    sm = FrozenSeedMap.derive(BINDING.sha256, SEEDMAP["campaign"])
    check("committed seed map rederives exactly", sm.as_json()["families"] == SEEDMAP["families"]
          and sm.master == SEEDMAP["master_seed"])
    vals = list(SEEDMAP["families"].values())
    check("no seed overlap between families", len(set(vals)) == len(vals), f"{len(vals)} families")
    check("calibration and validation families are distinct",
          SEEDMAP["families"]["calibration"] != SEEDMAP["families"]["validation"])
    check("branch_a_measurement has its own family, not Branch-B's",
          SEEDMAP["families"]["branch_a_measurement"] not in
          (SEEDMAP["families"]["validation"], SEEDMAP["families"]["calibration"]))
    check("analysis-layer families are a strict subset",
          set(ANALYSIS_FAMILIES) < set(SEEDMAP["families"]))
    check("seed values are not hand-picked",
          SEEDMAP["derivation"]["hand_picked_values"] is False)
    a = replicate_seed(sm.families["validation"], "C1_true_bridge_complete", 17)
    b = replicate_seed(sm.families["validation"], "C1_true_bridge_complete", 17)
    c = replicate_seed(sm.families["validation"], "C1_true_bridge_complete", 18)
    d = replicate_seed(sm.families["calibration"], "C1_true_bridge_complete", 17)
    check("replicate IDs deterministic", a == b, f"{a}")
    check("different replicate index -> different seed", a != c)
    check("same index in a different family -> different seed", a != d)
    check("a consumer cannot read another family's stream",
          _refuses(sm.stream, ValidationSeedFamily.VALIDATION, ValidationSeedFamily.CALIBRATION))
    check("a family may read its own stream",
          sm.stream(ValidationSeedFamily.VALIDATION, ValidationSeedFamily.VALIDATION)
          == SEEDMAP["families"]["validation"])
    check("master seed derives from the contract identity, not a chosen number",
          master_seed(BINDING.sha256, SEEDMAP["campaign"]) == SEEDMAP["master_seed"])
    check("a different contract gives a different master seed",
          master_seed("0" * 64, SEEDMAP["campaign"]) != SEEDMAP["master_seed"])


def _refuses(fn, *args, **kwargs) -> bool:
    try:
        fn(*args, **kwargs)
    except Refusal:
        return True
    return False


# ------------------------------------------------------- plan determinism + agreement
def test_plan() -> None:
    check("plan declares exactly 8 cases", len(PLAN["cases"]) == 8,
          ", ".join(c["case_id"] for c in PLAN["cases"]))
    check("every case carries all 14 required descriptors",
          all(all(k in c for k in ("case_id", "scientific_purpose", "v4_classification",
                                   "authority", "truth_model", "fields_affected", "beta_truth",
                                   "geometry_truth", "branch_a_uncertainty", "branch_b_process",
                                   "expected_qualitative_outcome", "formal_pass_fail_criterion",
                                   "seed_family", "replicate_count", "role"))
              for c in PLAN["cases"]))
    allowed = ("RETAINED UNCHANGED", "RETAINED BUT UPDATED FOR V4", "SUPERSEDED",
               "NEWLY REQUIRED BY AN ADOPTED V4 CORRECTION")
    check("every case carries an EXACT v4 classification enum",
          all(c["v4_classification"] in allowed for c in PLAN["cases"]),
          "; ".join(f"{c['case_id'].split('_')[0]}={c['v4_classification'][:12]}" for c in PLAN["cases"]))
    check("explanatory detail lives in a separate note field, not in the enum",
          all("v4_classification_note" in c for c in PLAN["cases"]))
    check("markdown renders the enum and the note separately",
          all(f"| v4 classification | **{c['v4_classification']}** |" in
              open(os.path.join(ROOT, "docs/e1a/E1A_V4_SYNTHETIC_VALIDATION_PLAN.md"),
                   encoding="utf-8").read() for c in PLAN["cases"]))
    check("case plan deterministic: loading twice gives identical content",
          load_plan(ROOT) == PLAN)
    check("adopted rules in the plan match the contract exactly",
          PLAN["adopted_rules_unchanged"]["delta_cross"] == BINDING.delta_cross
          and PLAN["adopted_rules_unchanged"]["delta_abs"] == BINDING.delta_abs
          and PLAN["adopted_rules_unchanged"]["alpha_geom"] == BINDING.alpha_geom
          and PLAN["adopted_rules_unchanged"]["alpha_1"] == BINDING.alpha_1
          and PLAN["adopted_rules_unchanged"]["alpha_2"] == BINDING.alpha_2
          and PLAN["adopted_rules_unchanged"]["theta_cap_deg"] == BINDING.theta_cap_deg
          and PLAN["adopted_rules_unchanged"]["rank_tol"] == BINDING.rank_tol
          and PLAN["adopted_rules_unchanged"]["pipeline_target"] == BINDING.pipeline_target)
    check("no Bonferroni and no fixed-B0 may return",
          "Bonferroni correction" in PLAN["adopted_rules_unchanged"]["forbidden"]
          and "fixed-B0 normalisation" in PLAN["adopted_rules_unchanged"]["forbidden"])
    check("three author dispositions are recorded",
          [g["id"] for g in PLAN["authority_gaps"]] == ["G1", "G2", "G3"])
    check("all three are CLOSED PROSPECTIVELY",
          all(g["status"] == "CLOSED PROSPECTIVELY" for g in PLAN["authority_gaps"]))
    check("no assurance row still says the criterion is undeclared",
          not any("NOT DECLARED IN ADOPTED AUTHORITY" in a["acceptance_rule"]
                  for a in PLAN["assurance"]))
    check("the superseded package is recorded, not erased",
          PLAN["superseded_package"]["work_commit"].startswith("475633c")
          and "preserved" in PLAN["superseded_package"])
    check("execution_authorised is still false after the dispositions",
          PLAN["execution_authorised"] is False)
    md = open(os.path.join(ROOT, "docs/e1a/E1A_V4_SYNTHETIC_VALIDATION_PLAN.md"),
              encoding="utf-8").read()
    for c in PLAN["cases"]:
        check(f"markdown carries case {c['case_id']}",
              c["case_id"] in md and str(c["replicate_count"]) in md
              and c["seed_family"] in md)
    check("markdown carries the exact frozen execution command",
          PLAN["execution_command"] in md)
    check("markdown states the command was NOT run", "NOT RUN" in md)
    for fam, seed in SEEDMAP["families"].items():
        check(f"markdown carries the frozen seed for {fam}", str(seed) in md)
    check("markdown and JSON agree on the contract identity",
          PLAN["frozen_identities"]["contract_sha256"] in md)


def test_output_schema() -> None:
    check("result schema freezes all 25 fields", len(RESULT_FIELDS) == 25,
          "schema 2 adds subcondition_id")
    check("plan and code agree on the record fields",
          list(PLAN["output_schema"]["per_record_fields"]) == list(RESULT_FIELDS))
    check("11 failure classifications frozen", len(FAILURE_CLASSIFICATIONS) == 11)
    check("plan and code agree on the classifications",
          list(PLAN["failure_classifications"]) == list(FAILURE_CLASSIFICATIONS))
    sk = aggregate_skeleton("C1_true_bridge_complete")
    check("manifest reproducible and identical across calls",
          sk == aggregate_skeleton("C1_true_bridge_complete"))
    check("aggregate carries the unconditional denominator rule",
          "every declared validation replicate" in sk["denominator_rule"]
          and "refusals count as failures" in sk["denominator_rule"])
    check("conditional diagnostics are labelled SECONDARY",
          "SECONDARY" in sk["conditional_diagnostic_secondary"]["label"])
    check("calibration generator identity recorded in the plan",
          PLAN["calibration"]["generator_identity"] == GENERATOR_IDENTITY)
    check("G5 is excluded from calibration by design",
          "not a function of the covariance" in PLAN["calibration"]["g5_excluded"])


def test_identities() -> None:
    a = procedure_identity(BINDING, {}, ROOT)
    check("adding the validation package did NOT move the analysis identity",
          a == PLAN["frozen_identities"]["analysis_procedure_identity"], a[:16] + "...")
    plan_sha = sha256_file(os.path.join(ROOT, PLAN_JSON))
    seed_sha = sha256_file(os.path.join(ROOT, SEED_MAP_JSON))
    e1 = execution_identity(BINDING, plan_sha, seed_sha, ROOT)
    e2 = execution_identity(BINDING, plan_sha, seed_sha, ROOT)
    check("execution identity deterministic", e1 == e2, e1[:16] + "...")
    check("execution identity differs from the analysis identity", e1 != a)
    check("a changed plan changes the execution identity",
          execution_identity(BINDING, "0" * 64, seed_sha, ROOT) != e1)
    check("every validation module enters the execution identity",
          len(VALIDATION_MODULES) == 10
          and "e1a_v4/validation/dispositions.py" in VALIDATION_MODULES
          and "e1a_v4/validation/classification.py" in VALIDATION_MODULES
          and "e1a_v4/validation/scope.py" in VALIDATION_MODULES,
          f"{len(VALIDATION_MODULES)} modules")
    for p in VALIDATION_MODULES:
        check(f"validation module present on disk: {p}",
              os.path.exists(os.path.join(ROOT, p)))
    for p in SCIENTIFIC_MODULES:
        check(f"frozen hash matches on disk: {p}",
              PLAN["frozen_identities"]["implementation_file_hashes"][p]
              == sha256_file(os.path.join(ROOT, p)))


def main_suite() -> int:
    groups = (
        ("preflight refuses before RNG", test_preflight_refuses_before_rng),
        ("execution not authorised", test_execution_is_not_authorised),
        ("seed separation", test_seeds),
        ("plan determinism and MD/JSON agreement", test_plan),
        ("output schema", test_output_schema),
        ("identities", test_identities),
    )
    for label, fn in groups:
        print(f"\n{label}")
        fn()
    print(f"\nE1a v4 pre-execution gate: {PASSED} passed, {FAILED} failed, {len(groups)} groups")
    print("Execution class: NON-MODEL-ADVANCING STATIC/PURE (this suite only)")
    print(f"  RNG_CALL_COUNT        : {SentinelRNG.CALLS}")
    print("  RANDOM DRAWS          : 0")
    print("  TRAJECTORIES          : 0")
    print("  CALIBRATION EXECUTION : NOT RUN")
    print("  VALIDATION CAMPAIGN   : NOT RUN")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main_suite())
