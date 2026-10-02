"""E1a v4 RELEASE-AUTHORITY conformance. Static and pure; nothing is executed.

**EXECUTION CLASS: NON-MODEL-ADVANCING STATIC/PURE.** Text, JSON, hashing and
arithmetic only. A sentinel RNG provider counts every construction and every
refusal path asserts the count did not move. No random number is drawn, no
trajectory generated, no calibration sampled, no scientific outcome inspected.

WHAT THIS SUITE EXISTS FOR
    The release rules lived only as prose inside each case's
    `formal_pass_fail_criterion` and the section-6 table, with nothing comparing
    them to the frozen design contract. An independent auditor demonstrated, at
    ceda2b5, that a plan could stay internally coherent -- Markdown and JSON
    agreeing, every derived boundary recomputing -- while changing:

        C1 complete-pipeline target   0.90 -> 0.80     ACCEPTED
        C1 replicates                  300 -> 301      ACCEPTED
        C3 replicates                  400 -> 401      ACCEPTED
        C8 replicates                  200 -> 201      ACCEPTED

    All four are reproduced below as permanent regressions. C3 additionally
    required its derived boundary and its section-12a row to be recomputed before
    it escaped; the fully coherent form is the one tested, because that is the one
    the audit is about.

    Hand-patching four values would have left the class open, so the mutation
    audit is GENERATED from the binding specification: every EXACT release binding
    is mutated in the JSON, the Markdown is regenerated so coherence still passes,
    and release conformance must still refuse.
"""

from __future__ import annotations

import copy
import dataclasses
import json
import os
import re
import shutil
import tempfile

from e1a_v4.numerics import Refusal
from e1a_v4.validation import PLAN_JSON, PLAN_MARKDOWN, SEED_MAP_JSON
from e1a_v4.validation.classification import (
    GROSS_INFLATION_LABEL, GROSS_INFLATION_TOLERANCE,
    INCOMPLETE_EVIDENCE_CLASSIFICATION, PER_FIELD_SIZE_CASES, REQUIRED_SIZE_FIELDS,
    SIZE_FAILURE, SIZE_INTERPRETATION, SIZE_NO_INFLATION, classify_field_size,
    size_boundary,
)
from e1a_v4.validation.coherence import (
    BLOCK_BEGIN, BLOCK_END, REGION_ANCHORS, SECTION_REGISTRY,
    render_authority_block, render_region, require_plan_authority_coherence,
)
from e1a_v4.validation.contract_plan import (
    DELEGATED_TO_RELEASE_AUTHORITY, NOT_REPEATED_CONTRACT_LEAVES, binding_inventory,
)
from e1a_v4.validation.dispositions import cp_lower, cp_upper
from e1a_v4.validation.campaign_driver import (
    per_field_primary_outcomes, per_field_rejections, replicate_level_rejections,
)
from e1a_v4.validation.plan import load_plan
from e1a_v4.validation import classification, release_authority
from e1a_v4.validation.release_authority import (
    REFUSAL_AWARE_DRIVER_SURFACE, _driver_declares,
    require_per_field_implementation_conformance,
    NOT_EVALUABLE, PRIMARY_ENDPOINT_UNDEFINABLE, REFUSAL_DISPOSITION_AFFECTS,
    REFUSAL_DISPOSITION_ID, STRUCTURED_REFUSAL_RULE, render_refusal_disposition,
    render_refusal_gap_statement, render_refusal_semantics,
    render_refusal_verdict_order, render_structured_refusal_block,
    CASE_PROSE_PINS, CASE_SPECIFIC, CONTRACT, DERIVED, EXACT, IMPLIED_STRONGER,
    NON_NORMATIVE_EXPLANATION, NOT_APPLICABLE, SHARED_SIZE_SEMANTICS_PINS,
    FIELD_SIZE_RULES, FIELD_SIZE_RULES_BY_CASE, VERIFICATION_MODES,
    C2_CASE_LIST_PINS, C2_CASE_PROSE_PINS, C2_RELEASE_RULE,
    CASE_LIST_PINS, DEFERRED_C2_LEAF_PATHS, DEFERRED_OUT_OF_SCOPE,
    render_c2_assurance, render_c2_boundary_rule, render_c2_criterion,
    render_c2_pooling_statement, render_c2_requirement,
    render_c2_scientific_purpose, require_c2_release_binding,
    C2_DERIVATION_REASON, FIELD_SIZE_DISPOSITION_AFFECTS,
    FIELD_SIZE_REQUIRED_FIELDS, GENERATED_FROM_CANONICAL,
    STRICTLY_VERIFIED_DUPLICATE,
    FINAL_CAMPAIGN_REQUIREMENT_PINS, TWO_QUESTIONS_COMPLETE_PIPELINE_PIN,
    final_campaign_requirements,
    render_component_size_question, render_field_size_block1_role,
    render_field_size_requirement,
    render_field_size_calibration_rationale, require_field_size_amendment,
    require_size_semantics_leaf_totality, size_semantics_leaf_counts,
    size_semantics_leaves, field_size_amendment_counts,
    normative_surface_registry, render_field_size_criterion,
    render_field_size_disposition, render_field_size_pooling_statement,
    render_field_size_semantics, render_final_campaign_rule,
    require_field_size_surface_totality,
    RELEASE_AUTHORITY_SECTIONS, RELEASE_NOT_APPLICABLE, REPORT_ONLY_MANDATORY,
    c2_implication_range, case_release_specification, derived_boundary,
    mandatory_diagnostics, release_binding_specification, release_inventory,
    require_c2_implies_contract_diagnostic, require_mandatory_diagnostics,
    require_release_authority_conformance,
)
from e1a_v4.validation.results import MANIFEST_SCHEMA, aggregate_skeleton
from e1a_v4.validation.runner import preflight
from e1a_v4.validation.seal import SEAL_JSON
from e1a_v4.validation.strict_json import strict_load_file

ROOT = os.path.dirname(os.path.abspath(__file__))
CONTRACT_JSON = "docs/e1a/e1a_v4_design_contract.json"
PASSED = 0
FAILED = 0


class SentinelRNG:
    CALLS = 0

    def normal(self, count: int) -> list[float]:
        type(self).CALLS += 1
        raise AssertionError("SENTINEL: an RNG draw was attempted")


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


def refusal_code(fn, *args, **kwargs) -> str | None:
    """The refusal code raised, or None if the call was accepted."""
    try:
        fn(*args, **kwargs)
    except Refusal as exc:
        return getattr(type(exc), "code", "UNCODED")
    return None


def refuses_with_code(label: str, expected: str, fn, *args, **kwargs) -> None:
    before = SentinelRNG.CALLS
    got = refusal_code(fn, *args, **kwargs)
    after = SentinelRNG.CALLS
    check(f"{label} -> {expected}", got == expected and after == before,
          f"got {got!r}, RNG delta {after - before}")


COPIED = (CONTRACT_JSON, "docs/e1a/E1A_V4_PROSPECTIVE_DESIGN.md",
          "docs/theory/EBU_THEORY_BASELINE.md",
          "docs/physical_foundation/EBU_PHYSICAL_FOUNDATION_CANONICAL.md",
          PLAN_JSON, SEED_MAP_JSON, PLAN_MARKDOWN, SEAL_JSON)


def sandbox() -> str:
    tmp = tempfile.mkdtemp()
    for rel in COPIED:
        dst = os.path.join(tmp, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy(os.path.join(ROOT, rel), dst)
    shutil.copytree(os.path.join(ROOT, "e1a_v4"), os.path.join(tmp, "e1a_v4"),
                    ignore=shutil.ignore_patterns("__pycache__"))
    return tmp


def rj(tmp, rel):
    return strict_load_file(os.path.join(tmp, rel), rel)


def wj(tmp, rel, obj):
    with open(os.path.join(tmp, rel), "w", encoding="utf-8") as handle:
        json.dump(obj, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def rmd(tmp):
    with open(os.path.join(tmp, PLAN_MARKDOWN), encoding="utf-8") as handle:
        return handle.read()


def wmd(tmp, text):
    with open(os.path.join(tmp, PLAN_MARKDOWN), "w", encoding="utf-8") as handle:
        handle.write(text)


def regenerate(tmp) -> None:
    """Propagate a JSON change into every generated Markdown region."""
    plan = rj(tmp, PLAN_JSON)
    text = rmd(tmp)
    for name, (begin, end) in REGION_ANCHORS.items():
        a = text.index(begin)
        z = text.index(end) + len(end)
        text = text[:a] + f"{begin}\n\n{render_region(name, plan).rstrip()}\n\n{end}" + text[z:]
    a = text.index(BLOCK_BEGIN)
    z = text.index(BLOCK_END) + len(BLOCK_END)
    wmd(tmp, text[:a] + render_authority_block(plan, tmp) + text[z:])


# ------------------------------------------------------------- path addressing
_STEP = re.compile(r"([^.\[\]]+)|\[(\d+)\]")


def path_steps(path: str) -> list:
    steps: list = []
    for name, index in _STEP.findall(path):
        steps.append(int(index) if index else name)
    return steps


def path_get(obj, path: str):
    for step in path_steps(path):
        obj = obj[step]
    return obj


def path_set(obj, path: str, value) -> None:
    steps = path_steps(path)
    for step in steps[:-1]:
        obj = obj[step]
    obj[steps[-1]] = value


def mutated_value(value):
    """A valid-LOOKING different value of the same kind."""
    if isinstance(value, bool):
        return not value
    if isinstance(value, int):
        return value + 1
    if isinstance(value, float):
        return round(value * 0.8, 10) if value else 0.5
    if isinstance(value, str):
        return value + " [MUTATED]"
    if isinstance(value, list):
        return value + ["MUTATED"] if value else ["MUTATED"]
    if isinstance(value, dict):
        return {**value, "MUTATED": True}
    return "MUTATED"


def load_pair(tmp):
    return rj(tmp, CONTRACT_JSON), rj(tmp, PLAN_JSON)


# ------------------------------------- 1. the auditor's four named escape routes
def c(plan, case_id):
    return next(x for x in plan["cases"] if x["case_id"] == case_id)


def probe_c1_target(plan) -> None:
    """C1 complete-pipeline target 0.90 -> 0.80, everywhere it is stated."""
    case = c(plan, "C1_true_bridge_complete")
    case["formal_pass_fail_criterion"] = case["formal_pass_fail_criterion"].replace(
        "0.90", "0.80")
    row = plan["assurance"][0]
    row["target"] = ">= 0.80"
    row["target_value"] = 0.80
    sem = plan["size_validation_semantics"]["two_questions"]
    sem["A_complete_practical_performance"] = sem[
        "A_complete_practical_performance"].replace("0.90", "0.80")
    reqs = plan["final_campaign_classification"]["requirements"]
    reqs[0] = reqs[0].replace("0.90", "0.80")


def probe_c1_replicates(plan) -> None:
    """C1 R = 300 -> 301, propagated to every dependent statement."""
    case = c(plan, "C1_true_bridge_complete")
    case["replicate_count"] = 301
    case["calibration_artifact_count"] = 301 * 4 * 4
    case["calibration_artifact_basis"] = (
        "301 replicates x 4 subconditions x 4 fields requiring calibration = 4,816")
    case["formal_pass_fail_criterion"] = case["formal_pass_fail_criterion"].replace(
        "279/300", "280/301")
    row = plan["assurance"][0]
    row["replicates"] = 301
    row["integer_boundary"] = 280
    row["acceptance_rule"] = ">= 280 / 301 complete passes"
    sem = plan["size_validation_semantics"]["two_questions"]
    sem["A_complete_practical_performance"] = sem[
        "A_complete_practical_performance"].replace("R = 300", "R = 301").replace(
        "279/300", "280/301")
    reqs = plan["final_campaign_classification"]["requirements"]
    reqs[0] = reqs[0].replace("R = 300", "R = 301").replace("279/300", "280/301")


def probe_c3_replicates(plan) -> None:
    """C3 R = 400 -> 401, with the derived boundary recomputed consistently."""
    case = c(plan, "C3_g5_block")
    case["replicate_count"] = 401
    case["calibration_artifact_count"] = 401 * 4 * 4
    case["calibration_artifact_basis"] = (
        "401 replicates x 4 subconditions x 4 fields requiring calibration = 6,416")
    bound = size_boundary(401, 0.001)
    case["formal_pass_fail_criterion"] = case["formal_pass_fail_criterion"].replace(
        "R = 400", "R = 401").replace(", 400)", ", 401)").replace(
        "i.e. 3 or more", f"i.e. {bound + 1} or more")
    case["c3_semantics"]["release_criterion"] = case["c3_semantics"][
        "release_criterion"].replace("R = 400", "R = 401").replace(", 400)", ", 401)")
    row = plan["assurance"][2]
    row["replicates"] = 401
    row["integer_boundary"] = bound
    row["acceptance_rule"] = (
        f"no inflation detected: CP_lower <= 0.001, i.e. <= {bound}/401")
    declared = plan["size_validation_semantics"]["derived_boundaries"]["C3"]
    declared["replicates"] = 401
    declared["boundary"] = bound
    declared["cp_lower_at_boundary"] = cp_lower(bound, 401)
    declared["cp_lower_at_boundary_plus_1"] = cp_lower(bound + 1, 401)
    declared["rule"] = (f"0-{bound} G5 rejections: no significant inflation detected; "
                        f"{bound + 1}+ : STATISTICAL_SIZE_FAILURE")


def probe_c8_replicates(plan) -> None:
    """C8 R = 200 -> 201, propagated to every dependent statement."""
    case = c(plan, "C8_blinded_scale_control")
    case["replicate_count"] = 201
    case["formal_pass_fail_criterion"] = case["formal_pass_fail_criterion"].replace(
        "R = 200", "R = 201").replace("188/200", "189/201")
    row = plan["assurance"][7]
    row["replicates"] = 201
    row["integer_boundary"] = 189
    row["acceptance_rule"] = ">= 189 / 201 paired-control successes"
    reqs = plan["final_campaign_classification"]["requirements"]
    reqs[7] = reqs[7].replace("R = 200", "R = 201").replace("188/200", "189/201")
    # `author_dispositions.G1` is deliberately NOT touched: that block was already
    # bound to the contract wholesale, which is exactly why the auditor's escape
    # route ran through the case record and the section-6 table instead.


def fix_c3_markdown(text: str) -> str:
    """Section 12a is DERIVED, not generated, so the probe recomputes it too."""
    bound = size_boundary(401, 0.001)
    row = (f"| **C3** | 401 | `0.001` | 0\u2013{bound} | {bound + 1}+ | "
           f"`{cp_lower(bound, 401):.10f}` | `{cp_lower(bound + 1, 401):.10f}` |")
    return re.sub(r"\| \*\*C3\*\* \| 400 \|[^\n]*", row, text)


NAMED_PROBES = (
    # Probes A and B deliberately rewrite C1's statement in
    # `size_validation_semantics.two_questions.A_complete_practical_performance`
    # so the mutation is coherent everywhere the target is stated. That leaf is
    # now exact-pinned by the semantic-leaf registry, which therefore refuses
    # BEFORE the contract-release binding is reached. Both refusals are correct;
    # the earlier one is accepted.
    ("A. C1 complete-pipeline target 0.90 -> 0.80", probe_c1_target,
     ("PROSPECTIVE_AMENDMENT_MISMATCH", "CONTRACT_RELEASE_TARGET_MISMATCH")),
    ("B. C1 R = 300 -> 301", probe_c1_replicates,
     ("PROSPECTIVE_AMENDMENT_MISMATCH",
      "CONTRACT_RELEASE_REPLICATE_COUNT_MISMATCH")),
    # C3's criterion is GENERATED from the canonical amendment, which carries
    # R = 400, so moving R now contradicts the amendment before the replicate-count
    # binding is reached. Both refusals are correct; the earlier one is accepted.
    ("C. C3 R = 400 -> 401, derived boundary recomputed", probe_c3_replicates,
     ("PROSPECTIVE_AMENDMENT_MISMATCH",
      "CONTRACT_RELEASE_REPLICATE_COUNT_MISMATCH")),
    # Probe D recomputes C8's final-campaign requirement line, which the complete
    # canonical requirement sequence now pins, so the list check refuses before
    # the replicate-count binding is reached. Both refusals are correct.
    ("D. C8 R = 200 -> 201", probe_c8_replicates,
     ("PROSPECTIVE_AMENDMENT_MISMATCH",
      "CONTRACT_RELEASE_REPLICATE_COUNT_MISMATCH")),
)

MARKDOWN_FIXUPS = {"C. C3 R = 400 -> 401, derived boundary recomputed": fix_c3_markdown}


def test_named_release_probes() -> None:
    """Every probe the auditor demonstrated, through the WHOLE static preflight."""
    for label, mutate, expected in NAMED_PROBES:
        tmp = sandbox()
        plan = rj(tmp, PLAN_JSON)
        mutate(plan)
        wj(tmp, PLAN_JSON, plan)
        regenerate(tmp)
        if label in MARKDOWN_FIXUPS:
            wmd(tmp, MARKDOWN_FIXUPS[label](rmd(tmp)))
        # the mutation is internally coherent: the two renderings agree
        coherence = refusal_code(require_plan_authority_coherence, tmp,
                                 rj(tmp, PLAN_JSON))
        check(f"{label}: Markdown/JSON coherence still PASSES", coherence is None,
              f"coherence said {coherence!r}")
        if isinstance(expected, tuple):
            got = refusal_code(preflight, tmp)
            check(f"{label}: preflight refuses, one of {expected}",
                  got in expected, f"got {got!r}")
        else:
            refuses_with_code(f"{label}: preflight", expected, preflight, tmp)
        shutil.rmtree(tmp)


# --------------------------------------- 2. every EXACT binding, machine-derived
def writable_rows(contract, plan, root, relationship):
    """Binding rows whose plan path is a single addressable JSON location."""
    out = []
    for row in release_binding_specification(contract, plan, root):
        if row.relationship != relationship:
            continue
        if row.plan_path.startswith("release_authority.mandatory_diagnostics."):
            continue
        try:
            path_get(plan, row.plan_path)
        except (KeyError, IndexError, TypeError):
            continue
        out.append(row)
    return out


def test_exact_mutation_audit() -> None:
    """Mutate EVERY exact release binding. Expected unexpected passes: 0."""
    contract = strict_load_file(os.path.join(ROOT, CONTRACT_JSON), "the contract")
    plan = load_plan(ROOT)
    rows = writable_rows(contract, plan, ROOT, EXACT)
    seen: set[str] = set()
    tested = 0
    unexpected: list[str] = []
    coherence_checked = 0
    for row in rows:
        if row.plan_path in seen:
            continue
        seen.add(row.plan_path)
        mutant = copy.deepcopy(plan)
        original = path_get(mutant, row.plan_path)
        path_set(mutant, row.plan_path, mutated_value(original))
        tested += 1
        if refusal_code(require_release_authority_conformance, contract, mutant,
                        ROOT) is None:
            unexpected.append(row.plan_path)
    check(f"every EXACT release binding refuses when mutated ({tested} tested)",
          not unexpected, f"unexpected passes: {unexpected}")
    check("the audit covered every distinct EXACT plan path",
          tested == len(seen) and tested >= 90, f"{tested} paths")

    # A representative sample additionally goes through the FULL stack with the
    # Markdown regenerated, proving the refusal is not an artefact of a malformed
    # document that coherence would have caught first.
    for path in ("assurance[0].replicates", "assurance[6].target_value",
                 "cases[7].primary_release_endpoint",
                 "release_authority.complete_pass_event"):
        tmp = sandbox()
        mutant = rj(tmp, PLAN_JSON)
        path_set(mutant, path, mutated_value(path_get(mutant, path)))
        wj(tmp, PLAN_JSON, mutant)
        regenerate(tmp)
        coherence = refusal_code(require_plan_authority_coherence, tmp,
                                 rj(tmp, PLAN_JSON))
        check(f"{path}: coherence passes after regeneration", coherence is None,
              f"coherence said {coherence!r}")
        coherence_checked += 1
        got = refusal_code(preflight, tmp)
        check(f"{path}: preflight refuses on release authority",
              got is not None and got.startswith("CONTRACT_RELEASE"), f"got {got!r}")
        shutil.rmtree(tmp)
    check("the full-stack sample ran", coherence_checked == 4, str(coherence_checked))


def test_case_specific_bindings_refuse() -> None:
    """CASE_SPECIFIC is a PIN, not permission to differ."""
    contract = strict_load_file(os.path.join(ROOT, CONTRACT_JSON), "the contract")
    plan = load_plan(ROOT)
    rows = writable_rows(contract, plan, ROOT, CASE_SPECIFIC)
    unexpected = []
    for row in rows:
        mutant = copy.deepcopy(plan)
        path_set(mutant, row.plan_path, mutated_value(path_get(mutant, row.plan_path)))
        if refusal_code(require_release_authority_conformance, contract, mutant,
                        ROOT) is None:
            unexpected.append(row.plan_path)
    check(f"every CASE_SPECIFIC pin refuses when mutated ({len(rows)} tested)",
          not unexpected, f"unexpected passes: {unexpected}")
    check("C4 R = 2000 and C5 R = 400 are pinned, not free",
          {r.plan_path for r in release_binding_specification(contract, plan, ROOT)
           if r.relationship == CASE_SPECIFIC} >= {"assurance[3].replicates",
                                                   "assurance[4].replicates"})


# ------------------------------------------------ 3. DERIVED, tested separately
def test_derived_bindings() -> None:
    """A derived quantity may never become an independent source of truth."""
    contract = strict_load_file(os.path.join(ROOT, CONTRACT_JSON), "the contract")
    plan = load_plan(ROOT)
    rows = writable_rows(contract, plan, ROOT, DERIVED)
    seen: set[str] = set()
    unexpected = []
    for row in rows:
        if row.plan_path in seen:
            continue
        seen.add(row.plan_path)
        # 1. authoritative inputs fixed, the STORED derived result altered
        mutant = copy.deepcopy(plan)
        path_set(mutant, row.plan_path, mutated_value(path_get(mutant, row.plan_path)))
        if refusal_code(require_release_authority_conformance, contract, mutant,
                        ROOT) is None:
            unexpected.append(row.plan_path)
    check(f"every DERIVED release value refuses when altered ({len(seen)} tested)",
          not unexpected, f"unexpected passes: {unexpected}")

    # 2. the authoritative SOURCE altered in a fixture, the derived result
    #    recomputed consistently -> still refused, because the source is frozen
    for case_id, index, target_key in (("C1_true_bridge_complete", 0, 0.80),
                                       ("C8_blinded_scale_control", 7, 0.80)):
        mutant = copy.deepcopy(plan)
        row = mutant["assurance"][index]
        row["target_value"] = target_key
        row["target"] = f">= {target_key}"
        boundary, _ = derived_boundary(row["bound_direction"], row["comparison"],
                                       row["replicates"], target_key)
        row["integer_boundary"] = boundary
        row["acceptance_rule"] = f">= {boundary} / {row['replicates']} successes"
        got = refusal_code(require_release_authority_conformance, contract, mutant, ROOT)
        check(f"{case_id}: a consistently recomputed derived boundary still refuses "
              "because its SOURCE is frozen", got == "CONTRACT_RELEASE_TARGET_MISMATCH",
              f"got {got!r}")

    # 3. the integer boundaries themselves are the ones the inputs derive
    for index, expected in ((0, 279), (1, 5), (2, 2), (3, 13), (5, 6), (6, 4), (7, 188)):
        row = plan["assurance"][index]
        boundary, derivation = derived_boundary(row["bound_direction"],
                                                row["comparison"], row["replicates"],
                                                row["target_value"])
        check(f"{row['case_id']}: boundary {expected} is recomputed, not copied",
              boundary == expected == row["integer_boundary"],
              f"recomputed {boundary}, stored {row['integer_boundary']}")
        check(f"{row['case_id']}: the derivation is recorded",
              row["boundary_derivation"] == derivation, derivation)
    check("C5 declares no integer boundary, because no threshold is frozen",
          plan["assurance"][4]["integer_boundary"] is None
          and plan["assurance"][4]["comparison"] == "REPORT_ONLY")


# ------------------------------------------------ 4. the IMPLIED_STRONGER proof
def test_implied_stronger() -> None:
    """Passing the adopted C2 rule must IMPLY the older contract requirement."""
    contract = strict_load_file(os.path.join(ROOT, CONTRACT_JSON), "the contract")
    accepted = c2_implication_range(contract)
    check("the adopted C2 rule's accepting range is finite and enumerable",
          accepted == (0, 1, 2, 3, 4, 5), str(accepted))
    for k in accepted:
        bound = cp_upper(k, 400)
        check(f"C2 accepts {k}/400 and its one-sided 95% CP upper bound "
              f"{bound:.8f} <= 0.03", bound <= GROSS_INFLATION_TOLERANCE)
    check("the boundary count 5/400 gives 0.0261 < 0.03, as the auditor reported",
          abs(cp_upper(5, 400) - 0.02610179906691329) < 1e-15,
          f"{cp_upper(5, 400):.17f}")
    check("cp_upper is strictly increasing over the accepting range, so the "
          "implication extends from the boundary by monotonicity",
          all(cp_upper(k, 400) < cp_upper(k + 1, 400) for k in accepted))
    check("6/400 already FAILS the adopted rule, so it is outside the range",
          size_boundary(400, 0.005) == 5)
    check("the implication check passes on the frozen contract",
          refusal_code(require_c2_implies_contract_diagnostic, contract) is None)

    # a fixture where the implication genuinely breaks must refuse
    broken = copy.deepcopy(contract)
    broken["endpoints"]["P1_geometry"]["alpha_geom"] = 0.02
    got = refusal_code(require_c2_implies_contract_diagnostic, broken)
    check("a loosened alpha_geom breaks the implication and REFUSES",
          got == "CONTRACT_RELEASE_IMPLICATION_BROKEN", f"got {got!r}")

    plan = load_plan(ROOT)
    rows = [r for r in release_binding_specification(contract, plan, ROOT)
            if r.relationship == IMPLIED_STRONGER]
    check("the IMPLIED_STRONGER relationship is recorded as a binding row",
          len(rows) == 1 and rows[0].expected == GROSS_INFLATION_TOLERANCE)
    block = plan["release_authority"]["implied_stronger"]["C2"]
    check("the older requirement is preserved, not erased",
          block["preserved_as"] == "MANDATORY_CONTRACT_DIAGNOSTIC"
          and "NOT removed" in block["not_erased"])


# ----------------------------------------- 5. mandatory diagnostics, and wording
def c2_aggregate(rejections_by_field=None, **overrides):
    fields = ("theta0_circular", "theta1_power", "theta2_ellipse", "theta3_temperature")
    counts = rejections_by_field or {f: 2 for f in fields}
    aggregate = aggregate_skeleton("C2_geometry_false_rejection", "sigma_psi_0p5")
    aggregate["contract_diagnostics"] = {
        "per_field": {
            field: {
                "rejections": counts[field], "replicates": 400,
                "cp_upper": cp_upper(counts[field], 400),
                "threshold": GROSS_INFLATION_TOLERANCE, "direction": "UPPER",
                "confidence_level": 0.95,
                "pass": cp_upper(counts[field], 400) <= GROSS_INFLATION_TOLERANCE,
            } for field in fields
        }
    }
    aggregate.update(overrides)
    return aggregate


def test_mandatory_diagnostics() -> None:
    """Frozen authority requires these; the reporting layer cannot omit them."""
    plan = load_plan(ROOT)
    contract = strict_load_file(os.path.join(ROOT, CONTRACT_JSON), "the contract")
    fields = ("theta0_circular", "theta1_power", "theta2_ellipse", "theta3_temperature")

    declared = mandatory_diagnostics(contract)
    check("the mandatory-diagnostic inventory is derived from the contract",
          len(declared) == 7, f"{len(declared)} rows")
    check("every mandatory diagnostic names the authority that makes it mandatory",
          all(d.authority_path and d.authority_source == CONTRACT for d in declared))
    check("the C2 contract diagnostic is among them",
          any(d.diagnostic_id == "C2_CONTRACT_COARSE_UPPER_BOUND" for d in declared))
    for case_id in ("C3_g5_block", "C4_surrogate_validity", "C5_plug_in_branch_a",
                    "C6_mode_resolution_boundary"):
        check(f"{case_id} also has a release rule / mandatory diagnostic split",
              any(d.case_id == case_id for d in declared))

    # present and internally consistent -> valid
    check("a complete, consistent C2 aggregate is schema-VALID",
          refusal_code(require_mandatory_diagnostics, c2_aggregate(), plan,
                       fields) is None)

    # absent -> refuse
    missing = c2_aggregate()
    missing["contract_diagnostics"] = {}
    refuses_with_code("C2 contract diagnostic ABSENT", "RESULT_SCHEMA_INVALID",
                      require_mandatory_diagnostics, missing, plan, fields)
    partial = c2_aggregate()
    del partial["contract_diagnostics"]["per_field"]["theta1_power"]
    refuses_with_code("C2 contract diagnostic missing one required field",
                      "CONTRACT_MANDATORY_DIAGNOSTIC_MISSING",
                      require_mandatory_diagnostics, partial, plan, fields)
    for key in ("rejections", "cp_upper", "threshold", "direction", "pass"):
        stripped = c2_aggregate()
        del stripped["contract_diagnostics"]["per_field"]["theta0_circular"][key]
        refuses_with_code(f"C2 contract diagnostic missing {key!r}",
                          "CONTRACT_MANDATORY_DIAGNOSTIC_MISSING",
                          require_mandatory_diagnostics, stripped, plan, fields)

    # present but inconsistent with the raw count -> refuse
    wrong = c2_aggregate()
    wrong["contract_diagnostics"]["per_field"]["theta2_ellipse"]["cp_upper"] = 0.001
    refuses_with_code("C2 diagnostic bound inconsistent with its own raw count",
                      "CONTRACT_MANDATORY_DIAGNOSTIC_MISMATCH",
                      require_mandatory_diagnostics, wrong, plan, fields)
    for key, value, label in (("direction", "LOWER", "wrong confidence DIRECTION"),
                              ("confidence_level", 0.9, "wrong confidence LEVEL"),
                              ("threshold", 0.05, "wrong contract threshold"),
                              ("replicates", 401, "wrong replicate count"),
                              ("pass", False, "PASS/FAIL disagreeing with the bound")):
        bad = c2_aggregate()
        bad["contract_diagnostics"]["per_field"]["theta0_circular"][key] = value
        refuses_with_code(f"C2 diagnostic with {label}",
                          "CONTRACT_MANDATORY_DIAGNOSTIC_MISMATCH",
                          require_mandatory_diagnostics, bad, plan, fields)

    # a genuine contract FAILURE is reported, not suppressed
    failing = c2_aggregate({f: 20 for f in fields})
    check("a C2 diagnostic that FAILS the contract threshold is still schema-valid: "
          "the schema requires it to be reported, not to pass",
          refusal_code(require_mandatory_diagnostics, failing, plan, fields) is None
          and not failing["contract_diagnostics"]["per_field"]["theta0_circular"]["pass"])


def test_mandatory_wording() -> None:
    """'may be reported' was the wrong word for a frozen contract requirement."""
    plan = load_plan(ROOT)
    text = open(os.path.join(ROOT, PLAN_MARKDOWN), encoding="utf-8").read()
    case = c(plan, "C2_geometry_false_rejection")
    criterion = case["formal_pass_fail_criterion"]
    check("the C2 criterion no longer says the contract diagnostic 'may be reported'",
          "may be reported" not in criterion, criterion[-120:])
    check("it says MANDATORY CONTRACT DIAGNOSTIC instead",
          "MANDATORY CONTRACT DIAGNOSTIC" in criterion)
    check("it names the authority that makes it mandatory",
          "synthetic_validation_requirements[2]" in criterion)
    check("it states the contract threshold 0.03", "0.03" in criterion)
    check("it states that absence is RESULT_SCHEMA_INVALID",
          "RESULT_SCHEMA_INVALID" in criterion)
    check("it still says the diagnostic is NOT the release gate",
          "not the release gate" in criterion)
    check("the stricter nominal-inflation rule remains the release classifier",
          "CP_lower(rejections, 400) > 0.005" in criterion
          and "6 or more rejections -> STATISTICAL_SIZE_FAILURE" in criterion)
    operative = text.split("## 20. Release authority", 1)[0]
    check("no operative section of the Markdown plan still says 'may be reported'",
          "may be reported" not in operative)
    check("the phrase survives only as a QUOTATION in the supersession record, which "
          "is preserved rather than rewritten",
          text.count("may be reported") == 1
          and 'diagnostic *"may be reported"*' in text)
    check("the runtime label is mandatory too",
          GROSS_INFLATION_LABEL.startswith("MANDATORY CONTRACT DIAGNOSTIC"),
          GROSS_INFLATION_LABEL)
    superseded = plan["size_validation_semantics"]["superseded_criterion"]
    check("the superseded record says SUPERSEDED AS THE CLASSIFIER, not discarded",
          "RETAINED as a mandatory reported diagnostic" in superseded["status"])
    check("the result schema version records the break",
          MANIFEST_SCHEMA == "e1a_v4_validation_manifest/3"
          and plan["output_schema"]["manifest_schema"] == MANIFEST_SCHEMA)
    check("the aggregate skeleton carries contract_diagnostics",
          "contract_diagnostics" in aggregate_skeleton("C2_geometry_false_rejection"))
    check("the plan's aggregate field list carries it too",
          "contract_diagnostics" in plan["output_schema"]["aggregate_fields"])
    check("the final campaign classification makes the diagnostics a requirement",
          any("MANDATORY CONTRACT DIAGNOSTIC" in r
              for r in plan["final_campaign_classification"]["requirements"]))


# ---------------------------------------------- 6. the three independent layers
def test_independent_layers() -> None:
    """Markdown-only, JSON-only, and coherent-but-off-authority are distinct."""
    # 1. Markdown-only release drift -> COHERENCE refusal
    tmp = sandbox()
    text = rmd(tmp)
    old = "| C1_true_bridge_complete | complete true-bridge pipeline success | >= 0.90 |"
    check("the section-6 summary renders C1's target verbatim", text.count(old) == 1)
    wmd(tmp, text.replace(old, old.replace(">= 0.90", ">= 0.80"), 1))
    got = refusal_code(preflight, tmp)
    # a generated region is checked for BYTE-EXACTNESS before it is parsed, so the
    # refusal names the stale rendering rather than the field inside it
    check("Markdown-ONLY release drift -> coherence refusal",
          got == "PLAN_AMBIGUOUS_BLOCK", f"got {got!r}")
    shutil.rmtree(tmp)

    # 1b. a Markdown-only drift OUTSIDE a generated region, where byte-exactness
    #     cannot catch it, must still be caught by the parsed/derived surface
    tmp = sandbox()
    text = rmd(tmp)
    old_row = "| **C2** | 400 | `0.005` | 0\u20135 | 6+ |"
    check("section 12a renders the derived C2 boundary row", text.count(old_row) == 1)
    wmd(tmp, text.replace(old_row, "| **C2** | 400 | `0.005` | 0\u20137 | 8+ |", 1))
    got = refusal_code(preflight, tmp)
    check("Markdown-only drift in the DERIVED section-12a table -> refusal",
          got == "PLAN_DERIVED_VALUE_MISMATCH", f"got {got!r}")
    shutil.rmtree(tmp)

    # 2. JSON-only release drift -> COHERENCE refusal (Markdown not regenerated)
    tmp = sandbox()
    plan = rj(tmp, PLAN_JSON)
    plan["assurance"][0]["replicates"] = 301
    wj(tmp, PLAN_JSON, plan)
    got = refusal_code(preflight, tmp)
    check("JSON-ONLY release drift -> coherence refusal",
          got == "PLAN_AMBIGUOUS_BLOCK", f"got {got!r}")
    shutil.rmtree(tmp)

    # 3. both drift coherently -> RELEASE-AUTHORITY refusal, and coherence passes
    tmp = sandbox()
    plan = rj(tmp, PLAN_JSON)
    plan["assurance"][0]["replicates"] = 301
    plan["assurance"][0]["integer_boundary"] = 280
    plan["assurance"][0]["acceptance_rule"] = ">= 280 / 301 complete passes"
    c(plan, "C1_true_bridge_complete")["replicate_count"] = 301
    wj(tmp, PLAN_JSON, plan)
    regenerate(tmp)
    check("the coherently drifted plan PASSES Markdown/JSON coherence",
          refusal_code(require_plan_authority_coherence, tmp,
                       rj(tmp, PLAN_JSON)) is None)
    refuses_with_code("coherent drift from frozen release authority",
                      "CONTRACT_RELEASE_REPLICATE_COUNT_MISMATCH", preflight, tmp)
    shutil.rmtree(tmp)


# ------------------------------------- 7. the complete C1-C8 release inventory
def test_case_release_table() -> None:
    """Every release-bearing case has a bound, machine-readable release rule."""
    contract = strict_load_file(os.path.join(ROOT, CONTRACT_JSON), "the contract")
    plan = load_plan(ROOT)
    specs = case_release_specification(contract, ROOT)
    check("all eight cases carry a frozen release specification", len(specs) == 8)
    check("the specification is in frozen C1-C8 order",
          [s.case_id for s in specs] == [x["case_id"] for x in plan["cases"]])
    check("the assurance table now has one row per case",
          len(plan["assurance"]) == 8)
    check("C5 and C6 gained the assurance rows they never had",
          {plan["assurance"][4]["case_id"], plan["assurance"][5]["case_id"]}
          == {"C5_plug_in_branch_a", "C6_mode_resolution_boundary"})
    expected_r = {"C1_true_bridge_complete": 300, "C2_geometry_false_rejection": 400,
                  "C3_g5_block": 400, "C4_surrogate_validity": 2000,
                  "C5_plug_in_branch_a": 400, "C6_mode_resolution_boundary": 400,
                  "C7_false_bridge": 400, "C8_blinded_scale_control": 200}
    for spec in specs:
        case = c(plan, spec.case_id)
        row = plan["assurance"][spec.assurance_index]
        check(f"{spec.case_id}: R = {expected_r[spec.case_id]} in the specification, "
              "the case record and the assurance row",
              spec.replicates[0] == case["replicate_count"] == row["replicates"]
              == expected_r[spec.case_id])
        check(f"{spec.case_id}: the R binding names an authority path",
              bool(spec.replicates[3]) and bool(spec.replicates[4]),
              f"{spec.replicates[1]} <- {spec.replicates[3]}")
        check(f"{spec.case_id}: release endpoint bound",
              spec.endpoint == case["primary_release_endpoint"], spec.endpoint)
        check(f"{spec.case_id}: confidence level is 95%", row["confidence_level"] == 0.95)
        check(f"{spec.case_id}: the interval method is Clopper-Pearson",
              row["method"] == "Clopper-Pearson")
        check(f"{spec.case_id}: the test is one-sided", row["sided"] == "one-sided")

    # the semantics a replicate change must not be able to move
    c3 = c(plan, "C3_g5_block")
    check("C3 keeps G5/Block-2 size as its PRIMARY release endpoint",
          c3["primary_release_endpoint"] == "G5_BLOCK_SIZE"
          and c3["c3_semantics"]["primary_release_endpoint"] == "G5_BLOCK_SIZE")
    check("C3 keeps the full two-block P1 as a SECONDARY diagnostic",
          c3["block1_role"] == "SECONDARY_PREDECLARED_INTERACTION_DIAGNOSTIC")
    c6 = c(plan, "C6_mode_resolution_boundary")
    check("C6 still evaluates ONE synthetic field, not four",
          c6["fields_affected"] == ["synthetic two-mode field at the declared rho"]
          and c6["fields_requiring_calibration"] == 1)
    check("C6 still declares exactly three rho", c6["subcondition_count"] == 3)
    c7 = c(plan, "C7_false_bridge")
    check("C7 still declares exactly four alternatives",
          len(c7["subconditions"]) == 4 and plan["assurance"][6]["unit"]
          == "per_alternative")
    check("C7 pooling remains FORBIDDEN", plan["assurance"][6]["pooling"] == "FORBIDDEN")
    c8 = c(plan, "C8_blinded_scale_control")
    check("C8 keeps its paired scale factors and paired semantics",
          c8["subconditions"][0]["scale_factors"] == [1.07, 0.9]
          and c8["subconditions"][0]["pairing"].startswith("INTENTIONAL:"))


# ------------------------------------------------ 8. measured completeness
def test_release_inventory_counts() -> None:
    """Machine-derived, never asserted."""
    contract = strict_load_file(os.path.join(ROOT, CONTRACT_JSON), "the contract")
    plan = load_plan(ROOT)
    inventory = release_inventory(contract, plan, ROOT)
    for name in (EXACT, DERIVED, IMPLIED_STRONGER, CASE_SPECIFIC,
                 REPORT_ONLY_MANDATORY, NOT_APPLICABLE):
        check(f"the inventory measures {name}", name in inventory,
              str(inventory.get(name)))
    check("UNCLASSIFIED release-relevant authority items = 0",
          inventory["unclassified"] == 0, str(inventory["unclassified"]))
    check("the count is MEASURED over actual contract leaves, not asserted",
          inventory["release_relevant_contract_leaves"] > 100,
          f"{inventory['release_relevant_contract_leaves']} leaves")
    check("every relationship name the inventory reports is a declared one",
          set(inventory) >= set(
              (EXACT, DERIVED, IMPLIED_STRONGER, CASE_SPECIFIC,
               REPORT_ONLY_MANDATORY, NOT_APPLICABLE)))
    rows = release_binding_specification(contract, plan, ROOT)
    check("every binding row names an authority source, path and reason",
          all(r.authority_source and r.authority_path and r.reason for r in rows))
    check("every binding row names the refusal it raises",
          all(isinstance(r.refusal, type) for r in rows))
    print(f"  ... release inventory: {json.dumps(inventory, sort_keys=True)}")


def test_not_applicable_audit() -> None:
    """A release rule may never hide under NOT_APPLICABLE."""
    contract = strict_load_file(os.path.join(ROOT, CONTRACT_JSON), "the contract")
    plan = load_plan(ROOT)
    check("every justified non-binding carries a stated reason",
          all(reason.strip() for reason in RELEASE_NOT_APPLICABLE.values()),
          f"{len(RELEASE_NOT_APPLICABLE)} leaves")
    forbidden = ("replicate", "R = ", "Clopper", "bound >=", "bound <=")
    offenders = [leaf for leaf in RELEASE_NOT_APPLICABLE
                 if leaf.startswith("synthetic_validation_requirements[")
                 and any(word in contract["synthetic_validation_requirements"][
                     int(leaf.split("[")[1].rstrip("]"))] for word in forbidden)]
    check("no frozen requirement that states a replicate count or a confidence rule "
          "is classified NOT_APPLICABLE", not offenders, str(offenders))

    # the auditor's specific finding: C1's contract requirement was excused
    check("synthetic_validation_requirements[3] is no longer excused in the "
          "contract-plan layer",
          "synthetic_validation_requirements[3]" not in NOT_REPEATED_CONTRACT_LEAVES)
    for index in (2, 3, 4, 5, 6, 7, 8, 9):
        check(f"synthetic_validation_requirements[{index}] is bound, not excused",
              f"synthetic_validation_requirements[{index}]"
              not in NOT_REPEATED_CONTRACT_LEAVES)
    inventory = binding_inventory(contract, plan, ROOT)
    check("the contract-plan layer has no unclassified execution-relevant leaves",
          inventory["unclassified_execution_relevant"] == 0,
          str(inventory["unclassified_execution_relevant"]))
    check("release-bearing leaves are marked DELEGATED, never NOT_APPLICABLE",
          inventory[DELEGATED_TO_RELEASE_AUTHORITY] >= 6,
          str(inventory[DELEGATED_TO_RELEASE_AUTHORITY]))

    rows = release_binding_specification(contract, plan, ROOT)
    bound_paths = {r.authority_path for r in rows}
    for path in ("synthetic_validation_requirements[2]",
                 "synthetic_validation_requirements[3]",
                 "complete_pipeline.target_true_bridge_success",
                 "complete_pipeline.denominator",
                 "complete_pipeline.complete_pass_event",
                 "refusal_semantics.reconciliation",
                 "endpoints.P1_geometry.alpha_geom", "endpoints.P1_geometry.alpha_1",
                 "endpoints.P1_geometry.alpha_2"):
        check(f"{path} is bound by the release layer", path in bound_paths)


# ---------------------------------------------- 9. nothing scientific changed
def test_no_scientific_rule_changed() -> None:
    contract = strict_load_file(os.path.join(ROOT, CONTRACT_JSON), "the contract")
    plan = load_plan(ROOT)
    rules = plan["adopted_rules_unchanged"]
    for key, expected in (("delta_cross", 0.02), ("delta_abs", 0.05),
                          ("z_cross", 1.959963985), ("z_abs", 1.959963985),
                          ("alpha_geom", 0.005), ("alpha_1", 0.004),
                          ("alpha_2", 0.001), ("theta_cap_deg", 5.0),
                          ("rank_tol", 1e-12), ("pipeline_target", 0.9)):
        check(f"{key} is unchanged at {expected}", rules[key] == expected,
              repr(rules[key]))
    check("the complete true-bridge target is still 0.90",
          contract["complete_pipeline"]["target_true_bridge_success"] == 0.9)
    check("the primary sigma_psi is still 0.5 degrees",
          contract["hypothetical_uncertainty_scenario"]["sigma_psi_deg"] == 0.5
          and plan["author_dispositions"]["G3"]["primary_release_scenario"] == 0.5)
    check("the case count is still eight", len(plan["cases"]) == 8)
    gm = plan["generating_model"]
    check("the corrected OU generator is untouched",
          gm["branch_b"]["dt_s"] == 0.00012 and gm["branch_b"]["T_total_s"] == 240.0
          and gm["branch_b"]["n_samples"] == 2000000)
    check("the four declared fields are untouched",
          [f["id"] for f in gm["per_field"]]
          == [f["id"] for f in contract["fields"]])
    for source, target in zip(contract["fields"], gm["per_field"]):
        check(f"{source['id']}: stiffness, temperature and orientation unchanged",
              source["k_uN_per_m"] == target["k_uN_per_m"]
              and source["T_K"] == target["T_K"]
              and source["rot_deg"] == target["rot_deg"])
    check("C7's four alternatives are unchanged",
          [s["beta_true"] for s in c(plan, "C7_false_bridge")["subconditions"]]
          == [[1, 1.06, 1, 1], [1, 0.93, 1.05, 1], [1, 1, 1, 1.10], [1, 1.025, 1, 1]])
    check("C8's paired scale factors are unchanged",
          c(plan, "C8_blinded_scale_control")["subconditions"][0]["scale_factors"]
          == [1.07, 0.9])
    check("the frozen design contract itself is untouched",
          contract["contract_version"] == "1.1.0")


def test_prior_conformance_preserved() -> None:
    """Every earlier propagated mutation must still refuse."""
    for label, mutate, expected in (
            ("field removal",
             lambda p: p["generating_model"]["per_field"].pop(1),
             "CONTRACT_FIELD_SET_MISMATCH"),
            ("field duplication",
             lambda p: p["generating_model"]["per_field"].__setitem__(
                 1, dict(p["generating_model"]["per_field"][0])),
             "CONTRACT_FIELD_DUPLICATE"),
            ("field parameter drift",
             lambda p: p["generating_model"]["per_field"][1].__setitem__(
                 "k_uN_per_m", [200, 200]),
             "CONTRACT_GENERATING_PARAMETER_MISMATCH"),
            ("relaxation-rule drift",
             lambda p: p["generating_model"]["per_field"][0].__setitem__(
                 "tau_rule", "a single tau_c for all fields"),
             "CONTRACT_RELAXATION_RULE_MISMATCH"),
            ("true-bridge beta drift",
             lambda p: p["generating_model"]["per_field"][2].__setitem__(
                 "beta_true", 1.05),
             "CONTRACT_TRUE_BRIDGE_BETA_MISMATCH"),
            ("reference-field drift",
             lambda p: p["generating_model"]["per_field"][0].__setitem__(
                 "reference", False),
             "CONTRACT_REFERENCE_FIELD_MISMATCH"),
            ("dt drift", lambda p: p["generating_model"]["branch_b"].__setitem__(
                "dt_s", 0.00013), "CONTRACT_GENERATING_PARAMETER_MISMATCH")):
        tmp = sandbox()
        plan = rj(tmp, PLAN_JSON)
        mutate(plan)
        wj(tmp, PLAN_JSON, plan)
        try:
            regenerate(tmp)
        except Refusal:
            pass          # a structurally invalid plan cannot even be re-rendered
        got = refusal_code(preflight, tmp)
        check(f"{label} still refuses", got is not None, f"got {got!r}")
        if got != expected:
            print(f"        (refused earlier, as {got}, which is also correct)")
        shutil.rmtree(tmp)


def test_execution_boundary_unchanged() -> None:
    """The package is still pre-driver, unsealed and unauthorised."""
    plan = load_plan(ROOT)
    check("execution_authorised is still false",
          plan["execution_authorised"] is False)
    check("the final execution identity is still deliberately not frozen",
          plan["frozen_identities"]["final_expected_execution_identity"] is None)
    # The driver was implemented after this suite was written. What this suite
    # guards is the RELEASE boundary, and that is unchanged: a present driver is
    # not an authorisation, and the seal is still not frozen.
    check("the official campaign driver is now present",
          os.path.exists(os.path.join(
              ROOT, "e1a_v4/validation/campaign_driver.py")))
    check("a present driver is still not an execution authorisation",
          plan["execution_authorised"] is False
          and plan["execution_seal"]["state"] == "PRE_DRIVER")
    check("no results directory exists",
          not os.path.exists(os.path.join(ROOT, "results/e1a_v4_validation")))
    check("section 6a is registered as a normative section",
          any(name.startswith("6a. Release authority") for name in SECTION_REGISTRY))
    check("NO RNG OBJECT WAS CONSTRUCTED BY THIS SUITE", SentinelRNG.CALLS == 0,
          str(SentinelRNG.CALLS))



def _case(plan, case_id):
    return next(c for c in plan["cases"] if c["case_id"] == case_id)


def _row(plan, case_id):
    return next(r for r in plan["assurance"] if r["case_id"] == case_id)


def test_c3_c4_per_field_authority() -> None:
    """The PROSPECTIVE C3/C4 per-field amendment, authority_gaps G4.

    Every mutation below is COHERENT -- the Markdown is regenerated from the
    mutated JSON, so nothing is caught merely by a rendering mismatch. Each one
    is a scientifically different rule than the amended authority, and each must
    refuse before any RNG exists.
    """
    plan = load_plan(ROOT)
    # --- the amendment is present and says one thing only -------------------
    for case_id, semantics_key, endpoint in (
            ("C3_g5_block", "c3_semantics", "G5_BLOCK_SIZE"),
            ("C4_surrogate_validity", "c4_semantics", "BLOCK1_ACHIEVED_SIZE")):
        case = _case(plan, case_id)
        row = _row(plan, case_id)
        semantics = case[semantics_key]
        check(f"{case_id} declares the elementary event PER FIELD",
              semantics["field_structure"] == "PER_FIELD", str(semantics["field_structure"]))
        check(f"{case_id} declares NO within-replicate field reduction",
              semantics["field_reduction"] == "NONE")
        check(f"{case_id} forbids pooling in the semantics block",
              semantics["pooling"] == "FORBIDDEN")
        check(f"{case_id} assurance unit is per_field", row["unit"] == "per_field",
              str(row["unit"]))
        check(f"{case_id} assurance pooling is FORBIDDEN",
              row["pooling"] == "FORBIDDEN", str(row["pooling"]))
        check(f"{case_id} still declares all four fields",
              case["fields_affected"] == ["theta0_circular", "theta1_power",
                                          "theta2_ellipse", "theta3_temperature"],
              str(case["fields_affected"]))
        check(f"{case_id} criterion states PER FIELD and never pooled",
              "PER FIELD" in case["formal_pass_fail_criterion"]
              and "never pooled" in case["formal_pass_fail_criterion"])
        check(f"{case_id} release endpoint is unchanged at {endpoint}",
              case["primary_release_endpoint"] == endpoint)
        check(f"{case_id} derived boundary row records per_field",
              plan["size_validation_semantics"]["derived_boundaries"][
                  case_id[:2]]["per_field"] is True)
        check(f"{case_id} derived boundary row records no replicate reduction",
              plan["size_validation_semantics"]["derived_boundaries"][
                  case_id[:2]]["replicate_reduction"] == "NONE")

    # --- R, alpha and the integer boundaries are UNCHANGED by the amendment --
    for cid, replicates, alpha, boundary in (("C3", 400, 0.001, 2),
                                             ("C4", 2000, 0.004, 13)):
        row = plan["size_validation_semantics"]["derived_boundaries"][cid]
        check(f"{cid} R, nominal alpha and boundary are unchanged",
              (row["replicates"], row["nominal_alpha"], row["boundary"])
              == (replicates, alpha, boundary), str(row))

    # --- G4 is recorded as a PROSPECTIVE closure ----------------------------
    gap = next(g for g in plan["authority_gaps"] if g["id"] == "G4")
    check("G4 affects C3 and C4", gap["affects"] == "C3, C4")
    check("G4 is CLOSED PROSPECTIVELY", gap["status"] == "CLOSED PROSPECTIVELY")
    for phrase in ("PER FIELD", "NO pooling of counts", "pooling FORBIDDEN",
                   "must not simply be assumed", "C1-only"):
        check(f"G4 records {phrase!r}", phrase in gap["resolution"])
    check("G4 discloses the operating characteristic without making it a threshold",
          "0.00788343125882217" in gap["resolution"]
          and "0.033884449548367356" in gap["resolution"]
          and "CONSERVATIVE VALIDATION FAILURE" in gap["resolution"])
    check("G4 does NOT claim a dependence direction",
          "positively associated" not in gap["resolution"]
          and "not established" in gap["resolution"].lower())

    # --- COHERENT BUT WRONG: every one must refuse --------------------------
    def unit(case_id, value):
        return lambda p: _row(p, case_id).__setitem__("unit", value)

    def pooling(case_id, value):
        return lambda p: _row(p, case_id).__setitem__("pooling", value)

    def semantics(case_id, key, field, value):
        return lambda p: _case(p, case_id)[key].__setitem__(field, value)

    def fields(case_id, value):
        return lambda p: _case(p, case_id).__setitem__("fields_affected", value)

    reference_only = ["theta0_circular"]
    three_only = ["theta0_circular", "theta1_power", "theta2_ellipse"]
    for label, mutate in (
            ("C3 unit per_field -> campaign", unit("C3_g5_block", "campaign")),
            ("C3 pooling FORBIDDEN -> ALLOWED", pooling("C3_g5_block", "ALLOWED")),
            ("C3 field_structure PER_FIELD -> ANY_FIELD",
             semantics("C3_g5_block", "c3_semantics", "field_structure", "ANY_FIELD")),
            ("C3 field_reduction NONE -> ANY_FIELD",
             semantics("C3_g5_block", "c3_semantics", "field_reduction", "ANY_FIELD")),
            ("C3 four fields -> reference field only",
             fields("C3_g5_block", reference_only)),
            ("C4 unit per_field -> campaign", unit("C4_surrogate_validity", "campaign")),
            ("C4 pooling FORBIDDEN -> ALLOWED",
             pooling("C4_surrogate_validity", "ALLOWED")),
            ("C4 field_structure PER_FIELD -> ANY_FIELD",
             semantics("C4_surrogate_validity", "c4_semantics", "field_structure",
                       "ANY_FIELD")),
            ("C4 field_reduction NONE -> EVERY_FIELD",
             semantics("C4_surrogate_validity", "c4_semantics", "field_reduction",
                       "EVERY_FIELD")),
            ("C4 field list missing one field",
             fields("C4_surrogate_validity", three_only)),
            ("C4 four fields -> reference field only",
             fields("C4_surrogate_validity", reference_only)),
            ("G4 disposition deleted",
             lambda p: p["authority_gaps"].pop()),
            ("G4 status flipped to OPEN",
             lambda p: p["authority_gaps"][-1].__setitem__("status", "OPEN")),
    ):
        tmp = sandbox()
        mutant = rj(tmp, PLAN_JSON)
        mutate(mutant)
        wj(tmp, PLAN_JSON, mutant)
        try:
            regenerate(tmp)
        except Refusal:
            pass          # a structurally invalid plan cannot even be re-rendered
        got = refusal_code(preflight, tmp)
        check(f"COHERENT BUT WRONG: {label} refuses", got is not None, f"got {got!r}")
        shutil.rmtree(tmp)

    # --- the C3 secondary diagnostic is untouched by the amendment ----------
    c3 = _case(plan, "C3_g5_block")["c3_semantics"]
    check("C3 primary release endpoint is still the G5 block",
          c3["primary_release_endpoint"] == "G5_BLOCK_SIZE")
    check("C3 Block-1 role is still the SECONDARY predeclared diagnostic",
          c3["block1_role"] == "SECONDARY_PREDECLARED_INTERACTION_DIAGNOSTIC")
    check("the joint P1 result still does NOT change the C3 release verdict",
          c3["joint_p1_result_changes_C3_release_verdict"] is False)

    # --- F1f: the implementation now EXPRESSES the amendment -----------------
    # It used to refuse because authority was silent. Authority spoke, and the
    # refusal became the stronger one: there is no replicate-level event at all.
    for case_id, event in (("C3_g5_block", "g5_rejected"),
                           ("C4_surrogate_validity", "block1_rejected")):
        check(f"reducing {case_id[:2]} across fields is now FORBIDDEN, not merely "
              "undeclared",
              refusal_code(replicate_level_rejections, plan, {}, case_id, event)
              == "CROSS_FIELD_REDUCTION_FORBIDDEN")
    check("execution is still not authorised", plan["execution_authorised"] is False)



def _gap_index(plan, gid="G4"):
    return next(i for i, g in enumerate(plan["authority_gaps"]) if g["id"] == gid)


def _case_index(plan, case_id):
    return next(i for i, c in enumerate(plan["cases"]) if c["case_id"] == case_id)


def _text_swap(old, a, b):
    """Replace a token INSIDE ONE named field's value. Never document-wide."""
    assert a in old, f"token {a!r} absent from the targeted field"
    return old.replace(a, b)


def semantic_mutations(plan):
    """Every load-bearing semantic component of the approved amendment.

    Each entry names the component, the EXACT normative path it edits, and the
    token swap, so the mutation provably lands where it is meant to.
    """
    g4 = f"authority_gaps[{_gap_index(plan)}]"
    out = []

    def add(component, path, old_token, new_token):
        out.append((component, path, old_token, new_token))

    # ---- G4 resolution -----------------------------------------------------
    add("G4 resolution scope", f"{g4}.resolution", "PER FIELD", "ANY FIELD")
    add("G4 resolution reduction", f"{g4}.resolution",
        "within-replicate field reduction NONE",
        "within-replicate field reduction ANY_FIELD")
    add("G4 resolution pooling", f"{g4}.resolution", "pooling FORBIDDEN",
        "pooling ALLOWED")
    add("G4 resolution final-release compensation", f"{g4}.resolution",
        "compensation FORBIDDEN", "compensation PERMITTED")
    add("G4 resolution C3 secondary role", f"{g4}.resolution",
        "does NOT feed the C3 primary release verdict",
        "DOES feed the C3 primary release verdict")
    add("G4 resolution dependence wording", f"{g4}.resolution",
        "must not simply be assumed",
        "is established: the shared common mode makes the gates positively associated")
    add("G4 resolution 0.90 scope", f"{g4}.resolution",
        "remains C1-only", "now also applies to C3 and C4")

    # ---- the two formal criteria -------------------------------------------
    for case_id in ("C3_g5_block", "C4_surrogate_validity"):
        short = case_id[:2]
        path = f"cases[{_case_index(plan, case_id)}].formal_pass_fail_criterion"
        add(f"{short} criterion scope -> ANY_FIELD", path,
            "PER FIELD, never pooled", "ANY FIELD within a replicate, counts pooled")
        add(f"{short} criterion scope -> REFERENCE_ONLY", path,
            "PER FIELD, never pooled",
            "on the reference field theta0_circular only")
        add(f"{short} criterion reduction -> EVERY_FIELD", path,
            "NO within-replicate reduction across fields",
            "an EVERY-field within-replicate reduction")
        add(f"{short} criterion pooling -> pooled", path,
            "NO pooling of counts", "counts POOLED across the four fields")
        add(f"{short} criterion case-level -> compensating", path,
            "is clean only when all four are clean",
            "is clean when at least three of four are clean")

    # ---- per-case semantics blocks -----------------------------------------
    for case_id, key in (("C3_g5_block", "c3_semantics"),
                         ("C4_surrogate_validity", "c4_semantics")):
        short = case_id[:2]
        base = f"cases[{_case_index(plan, case_id)}].{key}"
        add(f"{short} semantics field_structure", f"{base}.field_structure",
            "PER_FIELD", "ANY_FIELD")
        add(f"{short} semantics field_reduction", f"{base}.field_reduction",
            "NONE", "EVERY_FIELD")
        add(f"{short} semantics pooling", f"{base}.pooling", "FORBIDDEN", "ALLOWED")
        add(f"{short} semantics field_structure_rule", f"{base}.field_structure_rule",
            "four field-specific", "one pooled four-field")
        add(f"{short} semantics case_level_rule", f"{base}.case_level_rule",
            "iff all four are clean", "if at least three are clean")
        add(f"{short} semantics what_is_forbidden", f"{base}.what_is_forbidden",
            "pooling the four fields", "nothing in particular, including pooling")

    # ---- assurance rows and derived boundaries -----------------------------
    for case_id in ("C3_g5_block", "C4_surrogate_validity"):
        short = case_id[:2]
        index = next(i for i, r in enumerate(plan["assurance"])
                     if r["case_id"] == case_id)
        add(f"{short} assurance unit", f"assurance[{index}].unit",
            "per_field", "campaign")
        add(f"{short} assurance pooling", f"assurance[{index}].pooling",
            "FORBIDDEN", "NOT_APPLICABLE")
        add(f"{short} derived boundary replicate_reduction",
            f"size_validation_semantics.derived_boundaries.{short}.replicate_reduction",
            "NONE", "ANY_FIELD")

    # ---- newly guarded normative prose -------------------------------------
    for case_id in ("C3_g5_block", "C4_surrogate_validity"):
        short = case_id[:2]
        index = next(i for i, r in enumerate(plan["assurance"])
                     if r["case_id"] == case_id)
        add(f"{short} assurance acceptance_rule",
            f"assurance[{index}].acceptance_rule",
            "PER FIELD; every declared field is assessed",
            "POOLED across fields; the campaign is assessed")
        add(f"{short} assurance quantity", f"assurance[{index}].quantity",
            ", per field", ", pooled over the four fields")
        add(f"{short} derived boundary rule prose",
            f"size_validation_semantics.derived_boundaries.{short}.rule",
            "PER FIELD", "over the pooled four-field count")
        key = "c3_semantics" if short == "C3" else "c4_semantics"
        add(f"{short} semantics release_criterion",
            f"cases[{_case_index(plan, case_id)}].{key}.release_criterion",
            "stated per field", "stated over one pooled campaign count")
    add("G4 gap statement", f"{g4}.gap", "decides PER FIELD",
        "decides once per replicate")

    # ---- C3 secondary diagnostic becomes release-bearing -------------------
    c3 = f"cases[{_case_index(plan, 'C3_g5_block')}].c3_semantics"
    add("C3 secondary diagnostic role", f"{c3}.block1_role",
        "SECONDARY_PREDECLARED_INTERACTION_DIAGNOSTIC", "PRIMARY_RELEASE_ENDPOINT")

    # ---- final release representation --------------------------------------
    add("final release requirement C3",
        "final_campaign_classification.requirements[2]",
        "in every required field", "in the reference field")
    add("final release requirement C4",
        "final_campaign_classification.requirements[3]",
        "in every required field", "in at least three required fields")

    # ---- SECOND AUDIT: the two surfaces that were bound to nothing ---------
    for case_id in ("C3_g5_block", "C4_surrogate_validity"):
        short = case_id[:2]
        bp = f"size_validation_semantics.derived_boundaries.{short}"
        add(f"{short} derived boundary pooling -> ALLOWED", f"{bp}.pooling",
            "FORBIDDEN", "ALLOWED")
        add(f"{short} derived boundary pooling -> POOL_ALL_FIELDS", f"{bp}.pooling",
            "FORBIDDEN - every field is reported separately",
            "POOLED - pool all four field counts into one campaign count")
        add(f"{short} derived boundary per-field counts -> pooled", f"{bp}.rule",
            "PER FIELD", "over the POOLED four-field count")
        add(f"{short} derived boundary per_field flag",
            f"{bp}.per_field", True, False)
        index = next(i for i, r in enumerate(plan["assurance"])
                     if r["case_id"] == case_id)
        add(f"{short} assurance target", f"assurance[{index}].target", "=", ">=")
        add(f"{short} assurance estimator", f"assurance[{index}].estimator",
            "rejection proportion", "pooled rejection proportion")
        add(f"{short} assurance bound statement", f"assurance[{index}].bound",
            "one-sided LOWER", "one-sided UPPER")
    add("C4 derived boundary retention dropped",
        "size_validation_semantics.derived_boundaries.C4.retains",
        "are STILL reported", "need NOT be reported")
    add("C3 earlier disposition status",
        f"cases[{_case_index(plan, 'C3_g5_block')}].c3_semantics.status",
        "AMBIGUITY RESOLVED PROSPECTIVELY", "AMBIGUITY STILL OPEN")

    # ---- the final campaign rule itself ------------------------------------
    rule_path = "final_campaign_classification.rule"
    add("final campaign rule -> any one field is enough", rule_path,
        "a case is clean only when all 4 are clean",
        "a case is clean when ANY ONE field is clean")
    add("final campaign rule -> three of four", rule_path,
        "all 4 are clean", "at least 3 of 4 are clean")
    add("final campaign rule -> compensation permitted", rule_path,
        "compensation is FORBIDDEN", "compensation is PERMITTED")
    add("final campaign rule -> one clean field sufficient", rule_path,
        "a single clean field is NEVER sufficient",
        "a single clean field is sufficient")
    add("final campaign rule -> disjunctive", rule_path,
        "CONJUNCTIVE", "DISJUNCTIVE")
    add("final campaign rule -> condition may fail", rule_path,
        "NO required condition may fail", "a required condition MAY fail")
    add("final campaign facts collapsed",
        "final_campaign_classification.independent_facts_rule",
        "REPORTED SEPARATELY and never collapsed",
        "COLLAPSED into a single weighted score")
    add("final campaign >= 0.90 extended to C3/C4",
        "final_campaign_classification.independent_facts_rule",
        "Conversely C1 may reach >= 0.90",
        "C3 and C4 carry the same >= 0.90 familywise target. Conversely C1 may "
        "reach >= 0.90")
    add("final campaign verdict", "final_campaign_classification.verdict_on_success",
        "VALIDATION_PASS", "VALIDATION_PASS_WITH_RESERVATION")
    return out


def test_c3_c4_amendment_semantic_mutations() -> None:
    """AUDIT BLOCKER. Normative TEXT could contradict the structured rule.

    Three coherent Markdown+JSON mutations passed full static preflight: the G4
    resolution could require ANY-FIELD reduction and pooling, and either formal
    criterion could define a replicate-wide or pooled event, while every
    structured field still said PER_FIELD. Representation coherence cannot catch
    that, because both renderings agree -- with each other, and not with the
    approved amendment.
    """
    plan = load_plan(ROOT)

    # --- the canonical object is the ONE source -----------------------------
    counts = field_size_amendment_counts(plan)
    check("the amendment declares canonical rule fields",
          counts["canonical_rule_fields"] > 0, str(counts))
    check("every normative amendment field is classified and checked",
          counts["unclassified_normative_amendment_fields"] == 0, str(counts))
    check("generated and strictly-verified fields account for the whole check set",
          counts["generated_normative_fields"]
          + counts["strictly_verified_duplicate_fields"] == counts["checked_total"],
          str(counts))
    check("the canonical rule says PER_FIELD for both cases",
          all(r.evaluation_scope == "PER_FIELD" for r in FIELD_SIZE_RULES))
    check("the canonical rule says NO within-replicate reduction",
          all(r.field_reduction == "NONE" for r in FIELD_SIZE_RULES))
    check("the canonical rule forbids pooling",
          all(r.pooling == "FORBIDDEN" for r in FIELD_SIZE_RULES))
    check("the canonical rule declares exactly the four fields, in order",
          all(r.required_fields == ("theta0_circular", "theta1_power",
                                    "theta2_ellipse", "theta3_temperature")
              for r in FIELD_SIZE_RULES))

    # --- normative renderings ARE the canonical rule ------------------------
    gap = plan["authority_gaps"][_gap_index(plan)]
    check("the G4 resolution is the generated canonical text",
          gap["resolution"] == render_field_size_disposition())
    for rule in FIELD_SIZE_RULES:
        case = next(c for c in plan["cases"] if c["case_id"] == rule.case_id)
        check(f"{rule.case_id} criterion is the generated canonical text",
              case["formal_pass_fail_criterion"]
              == render_field_size_criterion(rule))
        for key, value in render_field_size_semantics(rule).items():
            check(f"{rule.case_id} semantics {key} is generated",
                  case[rule.semantics_key][key] == value)

    # --- SEMANTIC MUTATION AUDIT -------------------------------------------
    mutations = semantic_mutations(plan)
    unexpected = []
    for component, path, old_token, new_token in mutations:
        tmp = sandbox()
        mutant = rj(tmp, PLAN_JSON)
        before = path_get(mutant, path)
        after = (_text_swap(before, old_token, new_token)
                 if isinstance(before, str) else new_token)
        assert after != before, f"{component}: mutation did not change {path}"
        path_set(mutant, path, after)
        check(f"MUTATION LANDS: {component} at {path}",
              path_get(mutant, path) == after and after != before)
        wj(tmp, PLAN_JSON, mutant)
        try:
            regenerate(tmp)       # Markdown made COHERENT with the mutated JSON
        except Refusal:
            pass
        got = refusal_code(preflight, tmp)
        if got is None:
            unexpected.append(f"{component} @ {path}")
        check(f"COHERENT BUT WRONG: {component} refuses", got is not None,
              f"got {got!r}")
        shutil.rmtree(tmp)
    check(f"semantic mutation audit: {len(mutations)} tested, 0 unexpected passes",
          not unexpected, str(unexpected))

    # --- field-list mutations: remove / duplicate / replace / extra ---------
    base = ["theta0_circular", "theta1_power", "theta2_ellipse", "theta3_temperature"]
    list_mutations = (
        ("remove a field", base[:3]),
        ("duplicate a field", [base[0], base[0], base[2], base[3]]),
        ("replace a field", [base[0], base[1], base[2], "theta4_invented"]),
        ("extra field", base + ["theta4_invented"]),
        ("reorder fields", [base[1], base[0], base[2], base[3]]),
    )
    for case_id in ("C3_g5_block", "C4_surrogate_validity"):
        path = f"cases[{_case_index(plan, case_id)}].fields_affected"
        for label, value in list_mutations:
            tmp = sandbox()
            mutant = rj(tmp, PLAN_JSON)
            path_set(mutant, path, value)
            wj(tmp, PLAN_JSON, mutant)
            try:
                regenerate(tmp)
            except Refusal:
                pass
            got = refusal_code(preflight, tmp)
            check(f"COHERENT BUT WRONG: {case_id[:2]} required field list, "
                  f"{label} refuses", got is not None, f"got {got!r}")
            shutil.rmtree(tmp)

    # --- the amendment did NOT move the per-field size rules ----------------
    for rule in FIELD_SIZE_RULES:
        short = rule.case_id[:2]
        row = plan["size_validation_semantics"]["derived_boundaries"][short]
        check(f"{short} R, alpha and boundary are untouched by this repair",
              (row["replicates"], row["nominal_alpha"], row["boundary"])
              == (rule.replicates, rule.nominal_alpha, rule.boundary), str(row))
    check("the >= 0.90 target is still C1-only",
          "remains C1-only" in gap["resolution"]
          and plan["assurance"][0]["case_id"] == "C1_true_bridge_complete"
          and plan["assurance"][0]["target_value"] == 0.9)
    check("the dependence wording claims no direction",
          "not simply be assumed" in gap["resolution"]
          and "positively associated" not in gap["resolution"])
    for case_id, event in (("C3_g5_block", "g5_rejected"),
                           ("C4_surrogate_validity", "block1_rejected")):
        check(f"a cross-field reduction of {case_id[:2]} is refused as FORBIDDEN",
              refusal_code(replicate_level_rejections, plan, {}, case_id, event)
              == "CROSS_FIELD_REDUCTION_FORBIDDEN")


# ----------------------------------------- 16. normative-surface TOTALITY (F1e-r3)
def known_escape_classes(plan):
    """EVERY coherent-but-wrong escape any audit has demonstrated, in order.

    Each entry is (audit, label, [(path, old_token, new_token), ...]). The token
    swaps name the exact authoritative location, so a mutation that silently fails
    to land is an assertion error rather than a false pass.
    """
    g4 = f"authority_gaps[{_gap_index(plan)}]"
    c3 = _case_index(plan, "C3_g5_block")
    c4 = _case_index(plan, "C4_surrogate_validity")
    a3 = next(i for i, r in enumerate(plan["assurance"])
              if r["case_id"] == "C3_g5_block")
    return (
        ("first audit", "1. G4 resolution declares ANY_FIELD and pooling",
         [(f"{g4}.resolution", "PER FIELD", "ANY FIELD"),
          (f"{g4}.resolution", "pooling FORBIDDEN", "pooling ALLOWED")]),
        ("first audit", "2. C3 formal criterion defines a replicate-wide event",
         [(f"cases[{c3}].formal_pass_fail_criterion", "PER FIELD, never pooled",
           "ANY FIELD within a replicate, counts pooled")]),
        ("first audit", "3. C4 formal criterion pools the four field counts",
         [(f"cases[{c4}].formal_pass_fail_criterion", "NO pooling of counts",
           "counts POOLED across the four fields")]),
        ("first repair inventory", "4. assurance acceptance_rule contradicts",
         [(f"assurance[{a3}].acceptance_rule",
           "PER FIELD; every declared field is assessed",
           "POOLED across fields; the campaign is assessed")]),
        ("first repair inventory", "4b. assurance quantity contradicts",
         [(f"assurance[{a3}].quantity", ", per field",
           ", pooled over the four fields")]),
        ("first repair inventory", "5. section-12a boundary prose contradicts",
         [("size_validation_semantics.derived_boundaries.C3.rule", "PER FIELD",
           "over the POOLED four-field count")]),
        ("first repair inventory", "6. semantics release_criterion contradicts",
         [(f"cases[{c3}].c3_semantics.release_criterion", "stated per field",
           "stated over one pooled campaign count")]),
        ("first repair inventory", "7. G4 gap statement contradicts",
         [(f"{g4}.gap", "decides PER FIELD", "decides once per replicate")]),
        ("second audit", "8. derived-boundary pooling says pool all four counts",
         [("size_validation_semantics.derived_boundaries.C3.pooling",
           "FORBIDDEN - every field is reported separately",
           "POOLED - pool all four field counts into one campaign count")]),
        ("second audit", "9. final campaign rule: one clean field is enough",
         [("final_campaign_classification.rule",
           "a case is clean only when all 4 are clean",
           "a case is clean when ANY ONE field is clean")]),
        ("fourth audit",
         "10. C3 explanatory text makes full P1 the release condition",
         [(f"cases[{c3}].c3_semantics.why_calibration_is_retained",
           path_get(load_plan(ROOT),
                    f"cases[{c3}].c3_semantics.why_calibration_is_retained"),
           "The full P1 verdict is the deciding condition for C3.")]),
        ("fourth audit", "11. C4 Block-1 role demoted to secondary",
         [(f"cases[{c4}].block1_role", "PRIMARY_RELEASE_ENDPOINT",
           "SECONDARY_PREDECLARED_INTERACTION_DIAGNOSTIC")]),
        ("fifth audit",
         "12. nested interpretation.detector pools the four fields",
         [("size_validation_semantics.interpretation.detector",
           "CP_lower(rejections, R)",
           "CP_lower(pooled rejections across the four fields, 4R)")]),
        ("fifth audit",
         "13. nested two_questions.B becomes a pooled familywise test",
         [("size_validation_semantics.two_questions.B_component_size_inflation",
           "COMPONENT size test and never a familywise or pooled test",
           "FAMILYWISE test over the pooled four-field count, in which one clean "
           "field suffices")]),
        ("sixth audit",
         "14. an extra final-campaign requirement permitting compensation",
         [("final_campaign_classification.requirements[10]",
           "11. every MANDATORY CONTRACT DIAGNOSTIC",
           "11. a failed field-level size condition may be offset by a clean size "
           "condition in another field; every MANDATORY CONTRACT DIAGNOSTIC")]),
        ("sixth audit",
         "15. a new rule smuggled through a dynamically deferred C2 child",
         [("size_validation_semantics.derived_boundaries.C2.pooling",
           "FORBIDDEN - every field is reported separately",
           "FORBIDDEN - every field is reported separately; C3 may pool its "
           "field counts")]),
    )


def apply_swaps(mutant, swaps):
    """Apply each token swap to its own named field. Never document-wide."""
    for path, old_token, new_token in swaps:
        before = path_get(mutant, path)
        after = (_text_swap(before, old_token, new_token)
                 if isinstance(before, str) else new_token)
        assert after != before, f"{path}: swap did not change the value"
        path_set(mutant, path, after)
    for path, _old, new_token in swaps:
        assert str(new_token) in str(path_get(mutant, path)), \
            f"{path}: the intended authoritative representation was not changed"


def test_c3_c4_normative_surface_totality() -> None:
    """SECOND AUDIT BLOCKER. Two more normative surfaces were bound to nothing.

    A derived-boundary pooling sentence and the final campaign rule could each be
    edited to contradict the approved per-field amendment while Markdown and JSON
    agreed and full static preflight still ACCEPTED the package. Binding the two
    named strings would leave the class open a third time, so the registry of
    normative surfaces is made TOTAL instead: every key inside a controlled C3/C4
    container carries an explicit classification, and an unregistered one refuses.
    """
    plan = load_plan(ROOT)

    # --- the registry is well-formed and total ------------------------------
    registry = normative_surface_registry(plan)
    check("every normative surface carries a declared verification mode",
          all(s.mode in VERIFICATION_MODES for s in registry), str(len(registry)))
    check("every normative surface names a machine path and a Markdown rendering",
          all(s.path and s.container and s.markdown for s in registry))
    check("no normative surface is registered twice",
          len({s.path for s in registry}) == len(registry), str(len(registry)))
    counts = field_size_amendment_counts(plan)
    check("UNCLASSIFIED NORMATIVE C3/C4 LOCATIONS = 0",
          counts["unclassified_normative_amendment_fields"] == 0, str(counts))
    # 11 since F1f-d: the G5 structured-refusal disposition record is swept too.
    check("the registry covers every controlled container",
          counts["controlled_containers"] == 11, str(counts))
    check("the mode counts account for every registered location",
          counts["generated_normative_fields"]
          + counts["strictly_verified_duplicate_fields"]
          + counts["non_normative_explanatory_fields"]
          == counts["normative_surface_locations"], str(counts))
    check("generated plus strictly-verified is exactly the checked set",
          counts["generated_normative_fields"]
          + counts["strictly_verified_duplicate_fields"]
          == counts["checked_total"], str(counts))
    check("the live plan satisfies surface totality",
          refusal_code(require_field_size_surface_totality, plan) is None)

    # --- the two newly bound surfaces ARE the canonical text ----------------
    final = plan["final_campaign_classification"]
    check("the final campaign rule is the generated canonical text",
          final["rule"] == render_final_campaign_rule(), repr(final["rule"]))
    check("the final campaign rule states the per-field conjunction",
          "all 4 are clean" in final["rule"]
          and "a single clean field is NEVER sufficient" in final["rule"]
          and "compensation is FORBIDDEN" in final["rule"])
    for rule in FIELD_SIZE_RULES:
        short = rule.case_id[:2]
        row = plan["size_validation_semantics"]["derived_boundaries"][short]
        check(f"{short} derived-boundary pooling is the generated canonical text",
              row["pooling"] == render_field_size_pooling_statement(rule),
              repr(row["pooling"]))
        check(f"{short} derived-boundary pooling states FORBIDDEN",
              row["pooling"].startswith("FORBIDDEN"))

    # --- NO SELF-VALIDATION: expectations do not come from the plan ---------
    for path, surface_path, token, replacement in (
            ("final_campaign_classification.rule",
             "final_campaign_classification.rule", "all 4 are clean",
             "ANY ONE field is clean"),
            ("size_validation_semantics.derived_boundaries.C3.pooling",
             "derived_boundaries.C3.pooling", "FORBIDDEN", "ALLOWED")):
        mutant = copy.deepcopy(plan)
        path_set(mutant, path,
                 _text_swap(path_get(mutant, path), token, replacement))
        honest = {s.path: s.expected for s in registry}
        corrupt = {s.path: s.expected for s in normative_surface_registry(mutant)}
        check(f"the expected value for {path} is INDEPENDENT of the plan text",
              honest == corrupt
              and honest[surface_path] != path_get(mutant, path),
              f"expected stayed {honest[surface_path]!r}")

    # --- EVERY known escape class, through the WHOLE static preflight -------
    escapes = known_escape_classes(plan)
    survived = []
    for audit, label, swaps in escapes:
        tmp = sandbox()
        mutant = rj(tmp, PLAN_JSON)
        apply_swaps(mutant, swaps)
        check(f"MUTATION LANDS [{audit}]: {label}", True,
              f"{len(swaps)} authoritative location(s)")
        wj(tmp, PLAN_JSON, mutant)
        coherent = True
        try:
            regenerate(tmp)          # Markdown made COHERENT with the mutated JSON
        except Refusal:
            coherent = False
        if coherent:
            said = refusal_code(require_plan_authority_coherence, tmp,
                                rj(tmp, PLAN_JSON))
            check(f"COHERENT [{audit}]: {label}: Markdown and JSON still agree",
                  said is None, f"coherence said {said!r}")
        got = refusal_code(preflight, tmp)
        if got is None:
            survived.append(label)
        check(f"REFUSED [{audit}]: {label}", got is not None, f"got {got!r}")
        shutil.rmtree(tmp)
    check(f"known escape regression set: {len(escapes)} classes, 0 survive",
          not survived, str(survived))

    # --- a NEW authoritative field cannot appear silently -------------------
    injections = (
        ("cases[C3].c3_semantics.field_compensation",
         lambda p: p["cases"][_case_index(p, "C3_g5_block")]["c3_semantics"]
         .__setitem__("field_compensation", "ALLOWED")),
        ("cases[C4].c4_semantics.elementary_event",
         lambda p: p["cases"][_case_index(p, "C4_surrogate_validity")]["c4_semantics"]
         .__setitem__("elementary_event", "ANY_FIELD")),
        ("derived_boundaries.C3.pooling_override",
         lambda p: p["size_validation_semantics"]["derived_boundaries"]["C3"]
         .__setitem__("pooling_override", "POOL_ALL_FIELDS")),
        ("derived_boundaries.C4.field_reduction",
         lambda p: p["size_validation_semantics"]["derived_boundaries"]["C4"]
         .__setitem__("field_reduction", "ANY_FIELD")),
        ("final_campaign_classification.field_compensation_rule",
         lambda p: p["final_campaign_classification"]
         .__setitem__("field_compensation_rule", "three of four fields suffice")),
        ("assurance[C3].field_reduction",
         lambda p: next(r for r in p["assurance"]
                        if r["case_id"] == "C3_g5_block")
         .__setitem__("field_reduction", "ANY_FIELD")),
        ("assurance[C4].pooling_rule",
         lambda p: next(r for r in p["assurance"]
                        if r["case_id"] == "C4_surrogate_validity")
         .__setitem__("pooling_rule", "POOL_ALL")),
        ("authority_gaps.G4.pooling",
         lambda p: p["authority_gaps"][_gap_index(p)]
         .__setitem__("pooling", "ALLOWED")),
        ("cases[C3].field_reduction (key-vocabulary sweep)",
         lambda p: p["cases"][_case_index(p, "C3_g5_block")]
         .__setitem__("field_reduction", "EVERY_FIELD")),
        ("cases[C4].pooling (key-vocabulary sweep)",
         lambda p: p["cases"][_case_index(p, "C4_surrogate_validity")]
         .__setitem__("pooling", "ALLOWED")),
        ("size_validation_semantics.field_compensation (key-vocabulary sweep)",
         lambda p: p["size_validation_semantics"]
         .__setitem__("field_compensation", "ALLOWED")),
        ("a 12th requirement weakening C3",
         lambda p: p["final_campaign_classification"]["requirements"].append(
             "12. C3 alternatively passes when any one declared field is clean")),
        ("an EXPLANATORY field that starts stating a field rule",
         lambda p: p["cases"][_case_index(p, "C3_g5_block")]["c3_semantics"]
         .__setitem__("why_calibration_is_retained",
                      "calibration is a diagnostic input; releasing on the "
                      "reference field alone is permitted")),
    )
    unguarded = []
    for label, inject in injections:
        mutant = copy.deepcopy(plan)
        before = json.dumps(mutant, sort_keys=True)
        inject(mutant)
        assert json.dumps(mutant, sort_keys=True) != before, f"{label}: no change"
        tmp = sandbox()
        wj(tmp, PLAN_JSON, mutant)
        try:
            regenerate(tmp)
            got = refusal_code(preflight, tmp)
        except Refusal as exc:
            got = getattr(type(exc), "code", "UNCODED")
        if got is None:
            unguarded.append(label)
        check(f"NEW AUTHORITATIVE FIELD REFUSED: {label}", got is not None,
              f"got {got!r}")
        shutil.rmtree(tmp)
    check(f"new-normative-field audit: {len(injections)} injected, 0 accepted",
          not unguarded, str(unguarded))

    # --- and the approved SCIENCE is untouched by this repair ---------------
    for rule in FIELD_SIZE_RULES:
        short = rule.case_id[:2]
        row = plan["size_validation_semantics"]["derived_boundaries"][short]
        check(f"{short} R, nominal alpha and integer boundary are unchanged",
              (row["replicates"], row["nominal_alpha"], row["boundary"])
              == (rule.replicates, rule.nominal_alpha, rule.boundary), str(row))
        check(f"{short} Clopper-Pearson rule is unchanged",
              abs(row["cp_lower_at_boundary"]
                  - cp_lower(rule.boundary, rule.replicates)) < 1e-15
              and abs(row["cp_lower_at_boundary_plus_1"]
                      - cp_lower(rule.boundary + 1, rule.replicates)) < 1e-15)
    check("C3 R = 400 at alpha_2 = 0.001, clean 0-2",
          (FIELD_SIZE_RULES[0].replicates, FIELD_SIZE_RULES[0].nominal_alpha,
           FIELD_SIZE_RULES[0].boundary) == (400, 0.001, 2))
    check("C4 R = 2000 at alpha_1 = 0.004, clean 0-13",
          (FIELD_SIZE_RULES[1].replicates, FIELD_SIZE_RULES[1].nominal_alpha,
           FIELD_SIZE_RULES[1].boundary) == (2000, 0.004, 13))
    check("C3's primary endpoint is still the G5 block",
          FIELD_SIZE_RULES[0].primary_endpoint == "G5_BLOCK_SIZE")
    check("C3's full P1 result is still the SECONDARY diagnostic and does not "
          "feed primary release",
          FIELD_SIZE_RULES[0].secondary_diagnostic
          == "SECONDARY_PREDECLARED_INTERACTION_DIAGNOSTIC"
          and FIELD_SIZE_RULES[0].secondary_feeds_primary_release is False)
    check("C4's primary endpoint is still the Block-1 achieved size",
          FIELD_SIZE_RULES[1].primary_endpoint == "BLOCK1_ACHIEVED_SIZE")
    gap = plan["authority_gaps"][_gap_index(plan)]
    check("the >= 0.90 target is still C1-only and not a C3/C4 familywise target",
          "remains C1-only" in gap["resolution"]
          and "familywise" not in final["rule"]
          and "0.90" not in final["rule"])
    check("the dependence wording still claims no direction",
          "not simply be assumed" in gap["resolution"]
          and "positively associated" not in gap["resolution"]
          and "positive association" not in gap["resolution"])
    for case_id in ("C3_g5_block", "C4_surrogate_validity"):
        event = "g5_rejected" if case_id.startswith("C3") else "block1_rejected"
        check(f"the driver implements {case_id[:2]} per field and forbids the "
              "reduction (F1f)",
              refusal_code(replicate_level_rejections, plan, {}, case_id, event)
              == "CROSS_FIELD_REDUCTION_FORBIDDEN")


# ------------------------------------- 18. C3 explanatory semantics (F1e-r5)
#: Coherent rewrites of the C3 calibration rationale. The first is the fourth
#: audit's verbatim attack; the rest are paraphrases that state the same wrong
#: rule while avoiding anything a keyword guard could plausibly list. The last is
#: SEMANTICALLY CORRECT and must refuse anyway -- see the docstring.
EXPLANATORY_ATTACKS = (
    ("the auditor's exact attack",
     "The full P1 verdict is the deciding condition for C3.", False),
    ("paraphrase: outcome determines success",
     "The outcome of the complete P1 procedure determines whether C3 succeeds.",
     False),
    ("paraphrase: succeeds according to",
     "C3 succeeds according to the full P1 result.", False),
    ("paraphrase: G5 merely informative",
     "The G5 result is informative, while the complete P1 result governs C3.",
     False),
    ("paraphrase: only a successful P1 permits acceptance",
     "Only a successful full P1 outcome permits C3 acceptance.", False),
    ("paraphrase: follows the combined verdict",
     "C3 follows the combined P1 verdict.", False),
    ("paraphrase: secondary becomes primary without rule words",
     "For C3 the complete two-block result carries the release; the block-2 "
     "number is reported alongside it.", False),
    ("SEMANTICALLY CORRECT manual paraphrase",
     "Block-1 calibration is kept only as a diagnostic input; the full P1 result "
     "is a secondary predeclared interaction diagnostic and does not decide C3, "
     "whose primary release stays the per-field G5 block size assessment.", True),
)


def test_c3_explanatory_semantics() -> None:
    """F1e-r4 BLOCKER. The last free sentence inside a controlled container.

    `cases[2].c3_semantics.why_calibration_is_retained` was classified
    NON_NORMATIVE_EXPLANATION and guarded by a seven-token vocabulary list. The
    fourth independent audit rewrote it as

        "The full P1 verdict is the deciding condition for C3."

    which states the opposite of the approved science -- C3's primary release is
    the per-field G5 / Block-2 size, full P1 is a SECONDARY predeclared
    interaction diagnostic that does NOT feed primary release -- and full static
    preflight ACCEPTED it, because that sentence contains none of the listed
    words.

    No finite vocabulary can decide whether prose has become rule-bearing. The
    field is therefore GENERATED from the canonical rule, and the controlled
    C3/C4 surface now permits no semantically free text at all. The consequence,
    recorded deliberately: even a semantically CORRECT hand-paraphrase refuses.
    For this surface canonical semantics outrank free editorial paraphrasing;
    scientific authority does not need unrestricted prose editing.
    """
    plan = load_plan(ROOT)
    c3 = FIELD_SIZE_RULES_BY_CASE["C3_g5_block"]
    c4 = FIELD_SIZE_RULES_BY_CASE["C4_surrogate_validity"]
    path = f"cases[{_case_index(plan, 'C3_g5_block')}].c3_semantics." \
           "why_calibration_is_retained"

    # --- the location is GENERATED, and says the approved thing --------------
    live = path_get(plan, path)
    check("the C3 calibration rationale is the generated canonical text",
          live == render_field_size_calibration_rationale(c3), repr(live))
    check("it names full P1 as the SECONDARY predeclared interaction diagnostic",
          "SECONDARY_PREDECLARED_INTERACTION_DIAGNOSTIC" in live)
    check("it states that full P1 does NOT determine C3 primary release",
          "does NOT determine the C3 primary release verdict" in live)
    check("it states C3 primary release is the per-field G5 block size",
          "PER_FIELD G5_BLOCK_SIZE assessment" in live)
    check("no registered surface is classified explanatory any more",
          not [s for s in normative_surface_registry(plan)
               if s.mode == NON_NORMATIVE_EXPLANATION])

    # --- the verb itself is derived, so the text cannot contradict the flag --
    flipped = dataclasses.replace(c3, secondary_feeds_primary_release=True)
    check("the rationale's verb is DERIVED from secondary_feeds_primary_release",
          "does NOT determine" in render_field_size_calibration_rationale(c3)
          and "does NOT determine"
          not in render_field_size_calibration_rationale(flipped))

    # --- every attack, through the WHOLE static preflight --------------------
    survived = []
    for label, text, correct in EXPLANATORY_ATTACKS:
        tmp = sandbox()
        mutant = rj(tmp, PLAN_JSON)
        before = path_get(mutant, path)
        assert text != before, f"{label}: attack text equals the approved text"
        path_set(mutant, path, text)
        check(f"MUTATION LANDS: {label} at {path}",
              path_get(mutant, path) == text)
        wj(tmp, PLAN_JSON, mutant)
        coherent = True
        try:
            regenerate(tmp)
        except Refusal:
            coherent = False
        if coherent:
            said = refusal_code(require_plan_authority_coherence, tmp,
                                rj(tmp, PLAN_JSON))
            check(f"COHERENT: {label}: Markdown and JSON still agree",
                  said is None, f"coherence said {said!r}")
        got = refusal_code(preflight, tmp)
        if got is None:
            survived.append(label)
        tag = "CORRECT BUT NOT CANONICAL" if correct else "COHERENT BUT WRONG"
        check(f"{tag}: {label} refuses", got == "PROSPECTIVE_AMENDMENT_MISMATCH",
              f"got {got!r}")
        shutil.rmtree(tmp)
    check(f"explanatory attack set: {len(EXPLANATORY_ATTACKS)} tested, 0 survive",
          not survived, str(survived))

    # --- THE REFUSAL IS NOT THE KEYWORD GUARD -------------------------------
    # Proved two ways: the attacks contain no listed token at all, and the
    # refusals persist with the list emptied.
    for label, text, _c in EXPLANATORY_ATTACKS[:7]:
        hits = [t for t in release_authority.FIELD_RULE_PROSE_TOKENS
                if t in text.lower()]
        check(f"the old keyword guard would NOT have fired on: {label}",
              not hits, f"tokens {hits}")
    saved = release_authority.FIELD_RULE_PROSE_TOKENS
    try:
        release_authority.FIELD_RULE_PROSE_TOKENS = ()
        for label, text, _c in EXPLANATORY_ATTACKS:
            mutant = copy.deepcopy(plan)
            path_set(mutant, path, text)
            check(f"with the keyword list EMPTIED, {label} still refuses",
                  refusal_code(require_field_size_amendment, mutant)
                  == "PROSPECTIVE_AMENDMENT_MISMATCH")
    finally:
        release_authority.FIELD_RULE_PROSE_TOKENS = saved
    check("the keyword list was restored",
          release_authority.FIELD_RULE_PROSE_TOKENS == saved)

    # --- NO FREE TEXT anywhere in the controlled C3/C4 surface --------------
    counts = field_size_amendment_counts(plan)
    check("SEMANTICALLY FREE RULE-BEARING TEXT = 0",
          counts["semantically_free_rule_bearing_locations"] == 0, str(counts))
    check("UNCLASSIFIED NORMATIVE C3/C4 LOCATIONS = 0",
          counts["unclassified_normative_amendment_fields"] == 0, str(counts))
    check("every controlled string location is generated or pinned",
          counts["controlled_string_locations"] > 0
          and counts["non_normative_explanatory_fields"] == 0, str(counts))

    # no explanatory-SHAPED key survives unbound inside the controlled surface
    shaped = re.compile(r"why|rationale|explan|note|comment|descript|interpret"
                        r"|purpose|basis|reason", re.I)
    registered = {(s.container, s.key) for s in normative_surface_registry(plan)}
    unbound = []
    for i in (_case_index(plan, "C3_g5_block"),
              _case_index(plan, "C4_surrogate_validity")):
        for key, value in plan["cases"][i].items():
            if (isinstance(value, str) and shaped.search(key)
                    and (f"cases[{i}]", key) not in registered):
                unbound.append(f"cases[{i}].{key}")
    check("no explanatory-shaped C3/C4 field is left unbound", not unbound,
          str(unbound))

    # --- a NEW free-text field cannot be added to a controlled case ---------
    for key, text in (("release_note", "C3 releases on the full P1 verdict."),
                      ("interpretation", "a single clean field suffices for C4."),
                      ("c3_commentary", "G5 is advisory only.")):
        for case_id in ("C3_g5_block", "C4_surrogate_validity"):
            mutant = copy.deepcopy(plan)
            mutant["cases"][_case_index(plan, case_id)][key] = text
            check(f"new free text cases[{case_id[:2]}].{key} refuses",
                  refusal_code(require_field_size_surface_totality, mutant)
                  == "NORMATIVE_SURFACE_UNCLASSIFIED")

    # --- C4's Block-1 role was UNBOUND before this repair -------------------
    c4_path = f"cases[{_case_index(plan, 'C4_surrogate_validity')}].block1_role"
    check("C4 declares Block-1 as its PRIMARY_RELEASE_ENDPOINT",
          path_get(plan, c4_path) == "PRIMARY_RELEASE_ENDPOINT")
    check("C4's Block-1 role is the generated canonical value",
          path_get(plan, c4_path) == render_field_size_block1_role(c4))
    check("C3's Block-1 role is the secondary diagnostic",
          render_field_size_block1_role(c3)
          == "SECONDARY_PREDECLARED_INTERACTION_DIAGNOSTIC")
    for case_id, wrong in (("C4_surrogate_validity",
                            "SECONDARY_PREDECLARED_INTERACTION_DIAGNOSTIC"),
                           ("C3_g5_block", "PRIMARY_RELEASE_ENDPOINT")):
        mutant = copy.deepcopy(plan)
        mutant["cases"][_case_index(plan, case_id)]["block1_role"] = wrong
        check(f"{case_id[:2]} Block-1 role -> {wrong} refuses",
              refusal_code(require_field_size_amendment, mutant)
              == "PROSPECTIVE_AMENDMENT_MISMATCH")

    # --- pinned prose cannot drift -----------------------------------------
    pinned = 0
    for case_id, pins in CASE_PROSE_PINS.items():
        index = _case_index(plan, case_id)
        for key, expected in pins.items():
            check(f"pin holds: cases[{case_id[:2]}].{key}",
                  plan["cases"][index][key] == expected)
            pinned += 1
    check(f"every pinned C3/C4 case string matches the plan ({pinned} pins)",
          pinned == sum(len(v) for v in CASE_PROSE_PINS.values()))
    for case_id, key in (("C3_g5_block", "scientific_purpose"),
                         ("C3_g5_block", "calibration_scope_rationale"),
                         ("C4_surrogate_validity", "scientific_purpose"),
                         ("C4_surrogate_validity", "allowed_seed_families_rationale")):
        mutant = copy.deepcopy(plan)
        index = _case_index(plan, case_id)
        mutant["cases"][index][key] = (
            "C3 and C4 release on the full P1 verdict; a single clean field is "
            "sufficient.")
        check(f"smuggled rule in cases[{case_id[:2]}].{key} refuses",
              refusal_code(require_field_size_amendment, mutant)
              == "PROSPECTIVE_AMENDMENT_MISMATCH")
    for key in SHARED_SIZE_SEMANTICS_PINS:
        mutant = copy.deepcopy(plan)
        mutant["size_validation_semantics"][key] = (
            "size inflation is detected only when all four fields pool above "
            "nominal alpha")
        check(f"smuggled rule in size_validation_semantics.{key} refuses",
              refusal_code(require_field_size_amendment, mutant)
              == "PROSPECTIVE_AMENDMENT_MISMATCH")

    # --- the approved C3/C4 science is untouched ----------------------------
    check("C3 primary release endpoint is still the G5 block",
          c3.primary_endpoint == "G5_BLOCK_SIZE")
    check("C3 secondary is still the full P1 interaction diagnostic, not release-"
          "bearing",
          c3.secondary_diagnostic == "SECONDARY_PREDECLARED_INTERACTION_DIAGNOSTIC"
          and c3.secondary_feeds_primary_release is False)
    check("C4 primary release endpoint is still the Block-1 achieved size",
          c4.primary_endpoint == "BLOCK1_ACHIEVED_SIZE")
    for rule in FIELD_SIZE_RULES:
        check(f"{rule.case_id[:2]} scope/reduction/pooling unchanged",
              (rule.evaluation_scope, rule.field_reduction, rule.pooling)
              == ("PER_FIELD", "NONE", "FORBIDDEN"))
    check("C3 R/alpha/boundary unchanged",
          (c3.replicates, c3.nominal_alpha, c3.boundary) == (400, 0.001, 2))
    check("C4 R/alpha/boundary unchanged",
          (c4.replicates, c4.nominal_alpha, c4.boundary) == (2000, 0.004, 13))


# ------------------------------- 19. nested semantic-leaf totality (F1e-r7)
#: Coherent contrary rewrites of nested authority leaves. The first two are the
#: fifth audit's verbatim blockers; the rest exercise every string-leaf class in
#: the controlled subtree, per the mutation classes the brief requires.
NESTED_LEAF_MUTATIONS = (
    ("AUDIT: interpretation.detector pools four fields",
     "size_validation_semantics.interpretation.detector",
     "inflation detected iff CP_lower(pooled rejections across the four fields, "
     "4R) > nominal alpha; C3 and C4 pool their four fields into one count"),
    ("AUDIT: two_questions.B becomes familywise over a pooled count",
     "size_validation_semantics.two_questions.B_component_size_inflation",
     "C2, C3 and C4. These are FAMILYWISE component tests over the pooled "
     "four-field count: a case is flagged only if the pooled rate exceeds "
     "nominal alpha, and a single clean field is sufficient."),
    ("two_questions.B: per-field -> any-field",
     "size_validation_semantics.two_questions.B_component_size_inflation",
     "C2, C3 and C4 are evaluated ANY_FIELD within a replicate."),
    ("two_questions.B: component -> familywise",
     "size_validation_semantics.two_questions.B_component_size_inflation",
     "C3 and C4 carry a familywise size target across their four fields."),
    ("two_questions.A: C1 target 0.90 -> 0.80",
     "size_validation_semantics.two_questions.A_complete_practical_performance",
     "C1, UNCHANGED. One-sided 95% Clopper-Pearson LOWER bound on "
     "complete-pipeline success >= 0.80 over R = 300, i.e. >= 279/300."),
    ("two_questions.A: >= 0.90 extended to C3/C4",
     "size_validation_semantics.two_questions.A_complete_practical_performance",
     "C1, C3 and C4 each carry the >= 0.90 familywise target over R = 300."),
    ("interpretation.verdict_on_pass flipped to failure",
     "size_validation_semantics.interpretation.verdict_on_pass",
     "STATISTICAL_SIZE_FAILURE"),
    ("interpretation.means: did-not-establish -> proved",
     "size_validation_semantics.interpretation.means",
     "this experiment proved the achieved size is at or below nominal alpha"),
    ("interpretation.does_not_mean weakened",
     "size_validation_semantics.interpretation.does_not_mean",
     "nothing in particular; the nominal rate may be treated as proved"),
    ("interpretation.test: one-sided 5% -> 50%",
     "size_validation_semantics.interpretation.test",
     "H0: p <= nominal alpha  vs  H1: p > nominal alpha, one-sided 50%"),
    ("verdicts.on_detection relabelled",
     "size_validation_semantics.verdicts.on_detection",
     "POOLED_SIZE_ADVISORY"),
    ("verdicts.otherwise relabelled to a proof claim",
     "size_validation_semantics.verdicts.otherwise", "NOMINAL_SIZE_PROVED"),
    ("detector: per-replicate -> pooled",
     "size_validation_semantics.detector",
     "STATISTICAL SIZE INFLATION is detected iff CP_lower(pooled rejections over "
     "all four fields, 4R) > nominal alpha"),
    ("superseded_criterion.status: superseded -> live classifier",
     "size_validation_semantics.superseded_criterion.status",
     "LIVE RELEASE CLASSIFIER for C3 and C4, replacing the nominal-inflation "
     "tests"),
    ("superseded_criterion.why_insufficient.C3 rewritten",
     "size_validation_semantics.superseded_criterion.why_insufficient.C3",
     "would have been entirely adequate for C3 at the pooled four-field rate"),
    ("superseded_criterion.rule tolerance restated",
     "size_validation_semantics.superseded_criterion.rule",
     "one-sided 95% Clopper-Pearson UPPER bound <= 0.30"),
)

#: Unregistered children injected at depth 1, 2 and 3 of the controlled subtree.
NESTED_UNKNOWN_CHILDREN = (
    ("depth 1: size_validation_semantics.pooling_override",
     ("size_validation_semantics",), "pooling_override", "POOL_ALL_FIELDS"),
    ("depth 2: interpretation.pooling_override",
     ("size_validation_semantics", "interpretation"), "pooling_override", "POOL_ALL"),
    ("depth 2: interpretation.release_rule",
     ("size_validation_semantics", "interpretation"), "release_rule",
     "the full P1 verdict decides C3"),
    ("depth 2: two_questions.C3_global_pooling",
     ("size_validation_semantics", "two_questions"), "C3_global_pooling",
     "C3 pools its four fields"),
    ("depth 2: two_questions.release_override",
     ("size_validation_semantics", "two_questions"), "release_override",
     "any one clean field is sufficient"),
    ("depth 2: verdicts.on_pooled_detection",
     ("size_validation_semantics", "verdicts"), "on_pooled_detection",
     "POOLED_SIZE_FAILURE"),
    ("depth 2: superseded_criterion.new_rule",
     ("size_validation_semantics", "superseded_criterion"), "new_rule",
     "C3 passes when any one field is clean"),
    ("depth 3: derived_boundaries.C3.pooling_override",
     ("size_validation_semantics", "derived_boundaries", "C3"), "pooling_override",
     "POOLED"),
    ("depth 3: derived_boundaries.C4.field_reduction",
     ("size_validation_semantics", "derived_boundaries", "C4"), "field_reduction",
     "ANY_FIELD"),
    ("depth 3: superseded_criterion.why_insufficient.C5",
     ("size_validation_semantics", "superseded_criterion", "why_insufficient"),
     "C5", "pools its fields"),
)


def test_nested_semantic_leaf_totality() -> None:
    """F1e-r6 BLOCKER. Classified parent, unclassified nested children.

    The fifth independent audit changed two leaves BELOW a registered parent --

        size_validation_semantics.interpretation.detector
        size_validation_semantics.two_questions.B_component_size_inflation

    -- to say that C3 and C4 pool their four fields. Plan coherence, the
    prospective-amendment checker, the normative-surface totality checker and
    full static preflight all ACCEPTED it, and the reported free/unclassified
    counts stayed at zero, because those counts only ever looked at top-level
    strings. Neither leaf is rendered into the Markdown, so representation
    coherence could not have seen them either.

    Registering the two audited paths would have repeated the enumeration defect
    one level deeper. The subtree is therefore walked RECURSIVELY from the plan's
    own structure: every leaf at any depth must carry its own classification, and
    a classified parent authorises nothing below it.
    """
    plan = load_plan(ROOT)

    # --- recursive coverage, machine-derived --------------------------------
    counts = size_semantics_leaf_counts(plan)
    check("UNCLASSIFIED size_validation_semantics LEAVES = 0",
          counts["unclassified_leaves"] == 0, str(counts))
    check("UNKNOWN NESTED AUTHORITY KEYS = 0",
          counts["unknown_child_keys"] == 0, str(counts))
    check("no declared authority leaf is missing from the plan",
          counts["missing_declared_leaves"] == 0, str(counts))
    check("every actual leaf is declared",
          counts["declared_leaves"] == counts["total_leaves"], str(counts))
    check("the class counts account for every declared leaf",
          counts["generated_leaves"] + counts["strictly_verified_leaves"]
          + counts["exact_pinned_leaves"] + counts["structural_schema_leaves"]
          + counts["deferred_out_of_scope_leaves"] == counts["declared_leaves"],
          str(counts))
    check("the subtree is walked recursively, not at one level",
          counts["controlled_nested_objects"] >= 8, str(counts))
    check("the live plan satisfies recursive leaf totality",
          refusal_code(require_size_semantics_leaf_totality, plan) is None)
    for leaf in size_semantics_leaves(plan):
        check(f"leaf classified: {leaf.path}", leaf.mode in VERIFICATION_MODES,
              leaf.mode)

    # --- the interpretation block IS the canonical one in code --------------
    check("the plan's interpretation block equals classification.SIZE_INTERPRETATION",
          plan["size_validation_semantics"]["interpretation"] == SIZE_INTERPRETATION)
    # THREE verdicts since the G5 amendment, plus the precedence that stops the
    # `otherwise` branch claiming a clean field from an incomplete sequence.
    check("the verdict labels equal the canonical ones",
          plan["size_validation_semantics"]["verdicts"]
          == {"on_detection": SIZE_FAILURE, "otherwise": SIZE_NO_INFLATION,
              "on_undefined_primary_endpoint": NOT_EVALUABLE,
              "evaluation_order": render_refusal_verdict_order()})
    check("the two statistical verdicts are unchanged by the amendment",
          plan["size_validation_semantics"]["verdicts"]["on_detection"] == SIZE_FAILURE
          and plan["size_validation_semantics"]["verdicts"]["otherwise"]
          == SIZE_NO_INFLATION)
    check("two_questions.B is the generated canonical text",
          plan["size_validation_semantics"]["two_questions"]
          ["B_component_size_inflation"] == render_component_size_question())
    check("two_questions.B states the per-field component scope",
          "PER_FIELD" in render_component_size_question()
          and "pooling FORBIDDEN" in render_component_size_question()
          and "never a familywise or pooled test"
          in render_component_size_question())

    # --- every contrary leaf mutation, through the WHOLE preflight ----------
    survived = []
    for label, path, value in NESTED_LEAF_MUTATIONS:
        tmp = sandbox()
        mutant = rj(tmp, PLAN_JSON)
        before = path_get(mutant, path)
        assert before != value, f"{label}: mutation equals the approved value"
        path_set(mutant, path, value)
        check(f"MUTATION LANDS: {label} at {path}",
              path_get(mutant, path) == value)
        wj(tmp, PLAN_JSON, mutant)
        coherent = True
        try:
            regenerate(tmp)
        except Refusal:
            coherent = False
        if coherent:
            said = refusal_code(require_plan_authority_coherence, tmp,
                                rj(tmp, PLAN_JSON))
            check(f"COHERENT: {label}: Markdown and JSON still agree",
                  said is None, f"coherence said {said!r}")
        got = refusal_code(preflight, tmp)
        if got is None:
            survived.append(label)
        check(f"COHERENT BUT WRONG: {label} refuses", got is not None,
              f"got {got!r}")
        shutil.rmtree(tmp)
    check(f"nested leaf mutation audit: {len(NESTED_LEAF_MUTATIONS)} tested, "
          "0 unexpected passes", not survived, str(survived))

    # --- unregistered nested children at depths 1, 2 and 3 ------------------
    accepted = []
    for label, parents, key, value in NESTED_UNKNOWN_CHILDREN:
        mutant = copy.deepcopy(plan)
        node = mutant
        for step in parents:
            node = node[step]
        assert key not in node, f"{label}: key already present"
        node[key] = value
        got = refusal_code(require_size_semantics_leaf_totality, mutant)
        if got is None:
            accepted.append(label)
        check(f"UNKNOWN NESTED CHILD REFUSED: {label}",
              got == "NORMATIVE_SURFACE_UNCLASSIFIED", f"got {got!r}")
    check(f"nested unknown-child audit: {len(NESTED_UNKNOWN_CHILDREN)} injected, "
          "0 accepted", not accepted, str(accepted))

    # a classified PARENT does not authorise its children
    mutant = copy.deepcopy(plan)
    mutant["size_validation_semantics"]["interpretation"]["whatever"] = "anything"
    check("a classified parent does NOT authorise an unregistered child",
          refusal_code(require_size_semantics_leaf_totality, mutant)
          == "NORMATIVE_SURFACE_UNCLASSIFIED")
    # and a declared leaf may not be silently dropped
    mutant = copy.deepcopy(plan)
    del mutant["size_validation_semantics"]["interpretation"]["detector"]
    check("a declared authority leaf may not be deleted",
          refusal_code(require_size_semantics_leaf_totality, mutant)
          == "NORMATIVE_SURFACE_UNCLASSIFIED")

    # --- NO SELF-VALIDATION: expectations ignore the candidate subtree ------
    for path, value in (
            ("size_validation_semantics.interpretation.detector",
             "inflation detected iff the pooled four-field count exceeds alpha"),
            ("size_validation_semantics.two_questions.B_component_size_inflation",
             "C3 and C4 are familywise tests.")):
        mutant = copy.deepcopy(plan)
        path_set(mutant, path, value)
        honest = {l.path: l.expected for l in size_semantics_leaves(plan)}
        corrupt = {l.path: l.expected for l in size_semantics_leaves(mutant)}
        check(f"the expected value for {path} is INDEPENDENT of the plan text",
              honest == corrupt and honest[path] != value,
              f"expected stayed {str(honest[path])[:70]!r}")

    # --- the refusal is structural, not keyword matching --------------------
    saved = release_authority.FIELD_RULE_PROSE_TOKENS
    try:
        release_authority.FIELD_RULE_PROSE_TOKENS = ()
        for label, path, value in NESTED_LEAF_MUTATIONS[:2]:
            mutant = copy.deepcopy(plan)
            path_set(mutant, path, value)
            check(f"with the keyword list EMPTIED, {label} still refuses",
                  refusal_code(require_size_semantics_leaf_totality, mutant)
                  == "PROSPECTIVE_AMENDMENT_MISMATCH")
    finally:
        release_authority.FIELD_RULE_PROSE_TOKENS = saved

    # --- D6a3 REPLACES THE QUARANTINE WITH REAL AUTHORITY -------------------
    # F1e-r9 byte-quarantined C2's nine leaves while their science was unresolved
    # and asserted, correctly for that stage, that this was NOT a clearance. D6a
    # resolved the science (DERIVED from the contract's "at every declared
    # geometry" plus design section 12), so the leaves now carry real
    # classifications and the quarantine is retired.
    check("no leaf remains DEFERRED: the C2 quarantine is retired",
          not [l for l in size_semantics_leaves(plan)
               if l.mode == DEFERRED_OUT_OF_SCOPE])
    check("the deferred path registry is empty and still candidate-independent",
          DEFERRED_C2_LEAF_PATHS == ())
    c2_leaves = [l for l in size_semantics_leaves(plan)
                 if ".derived_boundaries.C2." in l.path]
    # Twelve since F1f-d: the three leaves recording that C2's primary endpoint
    # cannot be undefined, so its scope-out from G5 is stated rather than implied.
    check("C2's twelve derived-boundary leaves are generated or strictly verified",
          len(c2_leaves) == 12
          and all(l.mode in (GENERATED_FROM_CANONICAL, STRICTLY_VERIFIED_DUPLICATE)
                  for l in c2_leaves),
          str(sorted({l.mode for l in c2_leaves})))
    c2 = copy.deepcopy(plan)
    c2["size_validation_semantics"]["derived_boundaries"]["C2"]["pooling"] = (
        "POOLED - all four field counts summed")
    check("the C2 pooling rewrite refuses against the DERIVED canonical rule",
          refusal_code(require_size_semantics_leaf_totality, c2)
          == "PROSPECTIVE_AMENDMENT_MISMATCH")
    check("C2 is bound by its OWN rule, not by the C3/C4 amendment",
          not any(key.startswith("C2") for key in FIELD_SIZE_RULES_BY_CASE)
          and C2_RELEASE_RULE.case_id == "C2_geometry_false_rejection",
          str(sorted(FIELD_SIZE_RULES_BY_CASE)))
    check("C2's authority relationship is DERIVED, not EXACT",
          C2_RELEASE_RULE.authority_relationship == DERIVED)

    # --- the earlier repairs still hold -------------------------------------
    c3_path = (f"cases[{_case_index(plan, 'C3_g5_block')}].c3_semantics."
               "why_calibration_is_retained")
    for text in ("The full P1 verdict is the deciding condition for C3.",
                 "C3 follows the combined P1 verdict.",
                 "Only a successful full P1 outcome permits C3 acceptance."):
        mutant = copy.deepcopy(plan)
        path_set(mutant, c3_path, text)
        check(f"F1e-r5 still holds: {text[:46]!r} refuses",
              refusal_code(require_field_size_amendment, mutant)
              == "PROSPECTIVE_AMENDMENT_MISMATCH")
    counts2 = field_size_amendment_counts(plan)
    check("the surface registry is still total",
          counts2["unclassified_normative_amendment_fields"] == 0
          and counts2["semantically_free_rule_bearing_locations"] == 0,
          str(counts2))

    # --- approved science untouched -----------------------------------------
    for rule in FIELD_SIZE_RULES:
        short = rule.case_id[:2]
        row = plan["size_validation_semantics"]["derived_boundaries"][short]
        check(f"{short} R, alpha and integer boundary unchanged",
              (row["replicates"], row["nominal_alpha"], row["boundary"])
              == (rule.replicates, rule.nominal_alpha, rule.boundary), str(row))
    check("C3 is still per field, G5 primary, full P1 secondary and non-release",
          FIELD_SIZE_RULES_BY_CASE["C3_g5_block"].primary_endpoint == "G5_BLOCK_SIZE"
          and FIELD_SIZE_RULES_BY_CASE["C3_g5_block"]
          .secondary_feeds_primary_release is False)
    check("C4 is still per field with Block-1 primary",
          FIELD_SIZE_RULES_BY_CASE["C4_surrogate_validity"].primary_endpoint
          == "BLOCK1_ACHIEVED_SIZE")
    gap = plan["authority_gaps"][_gap_index(plan)]
    check("the >= 0.90 target is still C1-only",
          "remains C1-only" in gap["resolution"]
          and "0.90" in TWO_QUESTIONS_COMPLETE_PIPELINE_PIN
          and "C1, UNCHANGED" in TWO_QUESTIONS_COMPLETE_PIPELINE_PIN)
    check("the dependence wording still claims no direction",
          "not simply be assumed" in gap["resolution"]
          and "positively associated" not in gap["resolution"])


# ------------------- 20. list totality and fixed deferred scope (F1e-r9)
REQUIREMENT_LIST_MUTATIONS = (
    ("AUDIT: append cross-field compensation requirement",
     lambda l: l.append("12. A failed field-level size condition may be offset by "
                        "a clean size condition in another field.")),
    ("append a harmless-looking requirement",
     lambda l: l.append("12. the campaign report is archived after sign-off.")),
    ("append a line naming no C3, C4, pooling or field",
     lambda l: l.append("12. results are signed off by the release owner.")),
    ("prepend a requirement", lambda l: l.insert(0, "0. preliminary check passes")),
    ("insert a requirement in the middle",
     lambda l: l.insert(5, "5b. an extra gate applies")),
    ("remove a requirement", lambda l: l.pop(6)),
    ("duplicate a requirement", lambda l: l.insert(3, l[3])),
    ("replace a requirement",
     lambda l: l.__setitem__(4, "5. C5 may be skipped this campaign")),
    ("swap two requirements (order is normative)",
     lambda l: (l.__setitem__(0, l[1]), l.__setitem__(1, l[0]))),
    ("add a compensation rule",
     lambda l: l.append("12. compensation between fields is allowed.")),
    ("add a partial-pass rule",
     lambda l: l.append("12. three of four clean fields suffice.")),
)

OTHER_CONTROLLED_LISTS = (
    ("cases[C3].allowed_seed_families: add element",
     lambda m: m["cases"][2]["allowed_seed_families"].append("branch_b_process")),
    ("cases[C3].allowed_seed_families: remove element",
     lambda m: m["cases"][2]["allowed_seed_families"].pop()),
    ("cases[C4].allowed_seed_families: reorder",
     lambda m: m["cases"][3]["allowed_seed_families"].reverse()),
    ("cases[C3].subconditions: add element",
     lambda m: m["cases"][2]["subconditions"].append({"subcondition_id": "x"})),
    ("cases[C4].subconditions: add element",
     lambda m: m["cases"][3]["subconditions"].append({"subcondition_id": "x"})),
    ("cases[C3].subconditions: edit an element's feeds_primary_claim",
     lambda m: m["cases"][2]["subconditions"][2]
     .__setitem__("feeds_primary_claim", False)),
    ("cases[C3].fields_affected: add element",
     lambda m: m["cases"][2]["fields_affected"].append("theta4_invented")),
    ("interpretation.forbidden_wording: remove element",
     lambda m: m["size_validation_semantics"]["interpretation"]
     ["forbidden_wording"].pop()),
)


def _c2_branch(plan):
    return plan["size_validation_semantics"]["derived_boundaries"]["C2"]


DEFERRED_PATH_ATTACKS = (
    ("AUDIT: add a new deferred C2 leaf",
     lambda m: _c2_branch(m).__setitem__("release_override",
                                         "C3 may pool its field counts")),
    ("add a nested child object under the deferred C2 branch",
     lambda m: _c2_branch(m).__setitem__("nested", {"rule": "C3 pools its fields"})),
    ("rename a deferred leaf",
     lambda m: _c2_branch(m).__setitem__("pooling_rule",
                                         _c2_branch(m).pop("pooling"))),
    ("delete a deferred leaf", lambda m: _c2_branch(m).pop("pooling")),
    ("change a deferred leaf's type to a list",
     lambda m: _c2_branch(m).__setitem__("pooling", ["FORBIDDEN"])),
    ("replace a deferred leaf with an object",
     lambda m: _c2_branch(m).__setitem__("pooling", {"v": "FORBIDDEN"})),
    ("mutate a quarantined deferred value",
     lambda m: _c2_branch(m).__setitem__("pooling",
                                         "POOLED - all four counts summed")),
    ("smuggle a C3 rule through a new C2 child",
     lambda m: _c2_branch(m).__setitem__("c3_note", "C3 pools its four fields")),
)


def _authority_code(mutant):
    """The first refusal any C3/C4 authority checker raises, or None."""
    for fn in (require_field_size_surface_totality,
               require_size_semantics_leaf_totality, require_field_size_amendment):
        got = refusal_code(fn, mutant)
        if got is not None:
            return got
    return None


def test_list_and_deferred_scope_totality() -> None:
    """F1e-r8 BLOCKERS. A list checked selectively, and a self-expanding exception.

    **A.** `final_campaign_classification.requirements` was secured by pinning the
    two generated C3/C4 lines and counting how many lines mentioned C3 or C4. The
    audit appended

        "12. A failed field-level size condition may be offset by a clean size
             condition in another field."

    which names neither case, left the count at two, rendered into the Markdown,
    and was ACCEPTED by coherence, release authority and full static preflight.
    For an authoritative list MEMBERSHIP IS AUTHORITY, so the complete ordered
    sequence is now compared against a canonical one.

    **B.** The deferred C2 exception set was built by reading whichever keys the
    candidate carried under `derived_boundaries.C2`. Adding
    `release_override = "C3 may pool its field counts"` moved the deferred count
    from 9 to 10, was classified DEFERRED_OUT_OF_SCOPE, still reported
    `unknown_child_keys = 0`, and preflight accepted it. A candidate was
    authorising its own exception. The deferred path set is now fixed
    independently of the candidate.
    """
    plan = load_plan(ROOT)
    reqs = plan["final_campaign_classification"]["requirements"]

    # --- the canonical complete list ----------------------------------------
    canonical = final_campaign_requirements()
    check("the canonical requirement sequence matches the plan exactly",
          list(canonical) == reqs, f"{len(canonical)} vs {len(reqs)}")
    check("ORDER is normative: every line carries its own ordinal",
          all(line.startswith(f"{i + 1}. ") for i, line in enumerate(canonical)))
    check("the canonical list is built from pins plus the generated C2/C3/C4 slots",
          len(canonical) == len(FINAL_CAMPAIGN_REQUIREMENT_PINS)
          + len(FIELD_SIZE_RULES) + 1)
    check("the C2, C3 and C4 slots are GENERATED, not pinned",
          not {1, 2, 3} & set(FINAL_CAMPAIGN_REQUIREMENT_PINS))
    check("slot 2 is the generated C2 line",
          canonical[1] == render_c2_requirement(index=2))
    for rule in FIELD_SIZE_RULES:
        position = 3 if rule.case_id.startswith("C3") else 4
        check(f"slot {position} is the generated {rule.case_id[:2]} line",
              canonical[position - 1] == render_field_size_requirement(rule, position))

    # --- NO SELF-VALIDATION: the canonical list ignores the candidate -------
    mutant = copy.deepcopy(plan)
    mutant["final_campaign_classification"]["requirements"].append("12. anything")
    check("the canonical requirement list is INDEPENDENT of the candidate",
          final_campaign_requirements() == canonical
          and len(canonical) != len(
              mutant["final_campaign_classification"]["requirements"]))

    # --- every list mutation, through the WHOLE static preflight ------------
    survived = []
    for label, mutate in REQUIREMENT_LIST_MUTATIONS:
        tmp = sandbox()
        mutant = rj(tmp, PLAN_JSON)
        before = list(mutant["final_campaign_classification"]["requirements"])
        mutate(mutant["final_campaign_classification"]["requirements"])
        after = mutant["final_campaign_classification"]["requirements"]
        assert after != before, f"{label}: list unchanged"
        check(f"MUTATION LANDS: {label} ({len(before)} -> {len(after)} items)", True)
        wj(tmp, PLAN_JSON, mutant)
        coherent = True
        try:
            regenerate(tmp)
        except Refusal:
            coherent = False
        if coherent:
            said = refusal_code(require_plan_authority_coherence, tmp,
                                rj(tmp, PLAN_JSON))
            check(f"COHERENT: {label}: Markdown and JSON still agree",
                  said is None, f"coherence said {said!r}")
        got = refusal_code(preflight, tmp)
        if got is None:
            survived.append(label)
        check(f"UNAUTHORIZED LIST MUTATION REFUSED: {label}",
              got == "PROSPECTIVE_AMENDMENT_MISMATCH", f"got {got!r}")
        shutil.rmtree(tmp)
    check(f"requirement-list audit: {len(REQUIREMENT_LIST_MUTATIONS)} tested, "
          "0 unexpected passes", not survived, str(survived))

    # --- every OTHER controlled list ---------------------------------------
    loose = []
    for label, mutate in OTHER_CONTROLLED_LISTS:
        mutant = copy.deepcopy(plan)
        mutate(mutant)
        got = _authority_code(mutant)
        if got is None:
            loose.append(label)
        check(f"CONTROLLED LIST REFUSED: {label}",
              got == "PROSPECTIVE_AMENDMENT_MISMATCH", f"got {got!r}")
    check(f"controlled-list audit: {len(OTHER_CONTROLLED_LISTS)} tested, "
          "0 unexpected passes", not loose, str(loose))

    # --- the deferred exception set is FIXED --------------------------------
    # D6a3 retired the quarantine: the registry is empty, and the mechanism is
    # kept so a future exception still could not be created by the candidate.
    check("the deferred C2 path set is retired and declared independently",
          DEFERRED_C2_LEAF_PATHS == (), str(DEFERRED_C2_LEAF_PATHS))
    observed = {leaf.path for leaf in size_semantics_leaves(plan)
                if leaf.mode == DEFERRED_OUT_OF_SCOPE}
    check("the observed deferred set equals the fixed expected set",
          observed == set(DEFERRED_C2_LEAF_PATHS), str(sorted(observed)))
    for label, mutate in (("add a C2 child",
                           lambda m: _c2_branch(m).__setitem__("extra", "x")),
                          ("remove a C2 child",
                           lambda m: _c2_branch(m).pop("per_field")),
                          ("replace the whole C2 branch",
                           lambda m: m["size_validation_semantics"]
                           ["derived_boundaries"].__setitem__("C2", {"x": "y"}))):
        mutant = copy.deepcopy(plan)
        mutate(mutant)
        rebuilt = {leaf.path for leaf in size_semantics_leaves(mutant)
                   if leaf.mode == DEFERRED_OUT_OF_SCOPE}
        check(f"the expected deferred set is UNCHANGED when the candidate does: "
              f"{label}", rebuilt == set(DEFERRED_C2_LEAF_PATHS),
              f"{len(rebuilt)} paths")

    # --- every deferred-path structural attack ------------------------------
    escaped = []
    for label, mutate in DEFERRED_PATH_ATTACKS:
        mutant = copy.deepcopy(plan)
        mutate(mutant)
        got = _authority_code(mutant)
        if got is None:
            escaped.append(label)
        check(f"DEFERRED-SCOPE ATTACK REFUSED: {label}", got is not None,
              f"got {got!r}")
    check(f"deferred-scope audit: {len(DEFERRED_PATH_ATTACKS)} tested, "
          "0 unexpected passes", not escaped, str(escaped))

    # a deferred ancestor authorises no descendants
    mutant = copy.deepcopy(plan)
    _c2_branch(mutant)["pooling"] = {"nested": "anything at all"}
    check("a deferred ancestor does NOT authorise arbitrary descendants",
          _authority_code(mutant) is not None)

    # --- declared keys must EXIST, not just be absent-and-ignored -----------
    for label, mutate in (
            ("c3_semantics.requires_block1_calibration",
             lambda m: m["cases"][2]["c3_semantics"]
             .pop("requires_block1_calibration")),
            ("c3_semantics.why_calibration_is_retained",
             lambda m: m["cases"][2]["c3_semantics"]
             .pop("why_calibration_is_retained")),
            ("cases[C3].allowed_seed_families",
             lambda m: m["cases"][2].pop("allowed_seed_families"))):
        mutant = copy.deepcopy(plan)
        mutate(mutant)
        check(f"DELETING a declared authority key refuses: {label}",
              _authority_code(mutant) == "NORMATIVE_SURFACE_UNCLASSIFIED")

    # --- machine-derived coverage -------------------------------------------
    counts = field_size_amendment_counts(plan)
    for key in ("unexpected_list_elements", "missing_list_elements",
                "unexpected_deferred_paths", "missing_deferred_paths",
                "unclassified_normative_amendment_fields",
                "semantically_free_rule_bearing_locations"):
        check(f"{key} = 0", counts[key] == 0, str(counts))
    check("controlled normative lists are counted, not hand-listed",
          counts["controlled_normative_lists"] >= 7
          and counts["canonical_list_elements"] >= 30, str(counts))
    check("deferred expected equals deferred observed, both now zero",
          counts["deferred_exception_paths_expected"]
          == counts["deferred_exception_paths_observed"] == 0, str(counts))

    # --- C2: quarantine CLOSED, science still OPEN --------------------------
    # D6a3: the quarantine is replaced by a real DERIVED binding.
    quarantined = copy.deepcopy(plan)
    _c2_branch(quarantined)["pooling"] = "POOLED - all four counts summed"
    check("the C2 pooling rewrite refuses against the canonical DERIVED rule",
          _authority_code(quarantined) == "PROSPECTIVE_AMENDMENT_MISMATCH")
    check("C2's pooling text is GENERATED from the canonical rule",
          next(l for l in size_semantics_leaves(plan)
               if l.path.endswith("derived_boundaries.C2.pooling")).mode
          == GENERATED_FROM_CANONICAL)
    check("no C2 leaf is deferred any more",
          not [l for l in size_semantics_leaves(plan)
               if ".derived_boundaries.C2." in l.path
               and l.mode == DEFERRED_OUT_OF_SCOPE])
    check("C2's pooling binding is now DERIVED with a derivation reason",
          C2_RELEASE_RULE.authority_relationship == DERIVED
          and "at every declared geometry" in C2_DERIVATION_REASON.lower()
          .replace("AT EVERY DECLARED GEOMETRY".lower(), "at every declared geometry"))

    # --- earlier repairs still hold ----------------------------------------
    c3_path = (f"cases[{_case_index(plan, 'C3_g5_block')}].c3_semantics."
               "why_calibration_is_retained")
    for text in ("The full P1 verdict is the deciding condition for C3.",
                 "C3 follows the combined P1 verdict."):
        mutant = copy.deepcopy(plan)
        path_set(mutant, c3_path, text)
        check(f"F1e-r5 still holds: {text[:40]!r} refuses",
              _authority_code(mutant) == "PROSPECTIVE_AMENDMENT_MISMATCH")
    for path, value in (
            ("size_validation_semantics.interpretation.detector",
             "inflation detected iff CP_lower(pooled rejections, 4R) > alpha"),
            ("size_validation_semantics.two_questions.B_component_size_inflation",
             "C3 and C4 are familywise tests over a pooled count.")):
        mutant = copy.deepcopy(plan)
        path_set(mutant, path, value)
        check(f"F1e-r7 still holds: {path.split('.')[-1]} refuses",
              _authority_code(mutant) == "PROSPECTIVE_AMENDMENT_MISMATCH")
    for token, replacement in (("all 4 are clean", "ANY ONE field is clean"),
                               ("all 4 are clean", "at least 3 of 4 are clean"),
                               ("compensation is FORBIDDEN",
                                "compensation is PERMITTED")):
        mutant = copy.deepcopy(plan)
        path_set(mutant, "final_campaign_classification.rule",
                 _text_swap(path_get(mutant, "final_campaign_classification.rule"),
                            token, replacement))
        check(f"final rule {token!r} -> {replacement!r} refuses",
              _authority_code(mutant) == "PROSPECTIVE_AMENDMENT_MISMATCH")

    # --- approved science untouched -----------------------------------------
    for rule in FIELD_SIZE_RULES:
        short = rule.case_id[:2]
        row = plan["size_validation_semantics"]["derived_boundaries"][short]
        check(f"{short} R, alpha and integer boundary unchanged",
              (row["replicates"], row["nominal_alpha"], row["boundary"])
              == (rule.replicates, rule.nominal_alpha, rule.boundary), str(row))
        check(f"{short} scope/reduction/pooling unchanged",
              (rule.evaluation_scope, rule.field_reduction, rule.pooling)
              == ("PER_FIELD", "NONE", "FORBIDDEN"))
    gap = plan["authority_gaps"][_gap_index(plan)]
    check("the >= 0.90 target is still C1-only",
          "remains C1-only" in gap["resolution"]
          and FINAL_CAMPAIGN_REQUIREMENT_PINS[0].startswith("1. C1 ")
          and "0.90" in FINAL_CAMPAIGN_REQUIREMENT_PINS[0])
    check("the dependence wording still claims no direction",
          "not simply be assumed" in gap["resolution"]
          and "positively associated" not in gap["resolution"])


# ------------------------- 21. C2 DERIVED per-field authority binding (D6a3)
#: Wrong C2 semantics, in the five shapes the D6a reconstruction ruled out.
C2_CONTRARY_TEXTS = (
    ("pool all fields", "POOLED across all four fields into one count"),
    ("ANY_FIELD event", "ANY_FIELD replicate event over the four fields"),
    ("EVERY_FIELD event", "EVERY_FIELD replicate event over the four fields"),
    ("reference-field-only",
     "assessed on the reference field theta0_circular alone"),
    ("single pooled 1600", "one pooled count over 1600 field observations"),
)

#: The four surfaces the D6a1 audit confirmed were unguarded.
C2_PROSE_SURFACES = (
    ("cases[C2].scientific_purpose", "cases", "scientific_purpose"),
    ("cases[C2].formal_pass_fail_criterion", "cases", "formal_pass_fail_criterion"),
    ("assurance[C2].quantity", "assurance", "quantity"),
    ("assurance[C2].acceptance_rule", "assurance", "acceptance_rule"),
)


def _c2_case(plan):
    return plan["cases"][_case_index(plan, "C2_geometry_false_rejection")]


def _c2_assurance(plan):
    return next(r for r in plan["assurance"]
                if r["case_id"] == "C2_geometry_false_rejection")


def _c2_boundary(plan):
    return plan["size_validation_semantics"]["derived_boundaries"]["C2"]


def test_c2_derived_authority_binding() -> None:
    """D6a3. C2's per-field release rule, bound to the authority it derives from.

    The D6a reconstruction established -- and an independent audit cleared -- that
    C2's elementary event is a P1 rejection for ONE declared field, that the case
    is four separate R = 400 rejection-count processes, that pooling is FORBIDDEN
    and within-replicate field reduction is NONE, and that this is **DERIVED** from
    higher authority rather than stated literally by it.

    Before this repair four C2 normative surfaces were semantically free, and the
    nine `derived_boundaries.C2.*` leaves were protected only by a byte quarantine
    that explicitly did not validate their science. Both are now replaced by
    generation from one canonical rule.

    "Four separate field-level rejection-count processes" is bookkeeping. It
    asserts no probabilistic independence between field outcomes, and the
    derivation needs none.
    """
    plan = load_plan(ROOT)
    contract = strict_load_file(os.path.join(ROOT, CONTRACT_JSON), "the contract")
    rule = C2_RELEASE_RULE

    # --- the canonical rule says what D6a derived ---------------------------
    check("C2 elementary event is a P1 rejection for one declared field",
          rule.elementary_event == "P1_REJECTION_ONE_DECLARED_FIELD")
    check("C2 evaluation scope is PER_FIELD", rule.evaluation_scope == "PER_FIELD")
    check("C2 within-replicate field reduction is NONE",
          rule.field_reduction == "NONE")
    check("C2 pooling is FORBIDDEN", rule.pooling == "FORBIDDEN")
    check("C2 contributes ALL required field conditions to the final conjunction",
          rule.final_combination == "ALL_REQUIRED_FIELD_CONDITIONS")
    check("C2 authority relationship is DERIVED, not EXACT",
          rule.authority_relationship == DERIVED)
    check("the derivation reason names the controlling clause and the design budget",
          "AT EVERY DECLARED GEOMETRY" in C2_DERIVATION_REASON
          and "4 x alpha_geom" in C2_DERIVATION_REASON
          and "per-field predicate" in C2_DERIVATION_REASON)
    check("the reason states what a pooled count WOULD still do",
          "constrain an aggregate rate" in C2_DERIVATION_REASON)
    check("the live plan satisfies the C2 release binding",
          refusal_code(require_c2_release_binding, contract, plan) is None)

    # --- the numeric size rule is unchanged and DERIVED ----------------------
    check("C2 R = 400 per field", rule.replicates_per_field == 400)
    check("C2 nominal alpha_geom = 0.005",
          rule.nominal_alpha == 0.005 and rule.alpha_name == "alpha_geom")
    check("C2 integer boundary is RECOMPUTED as 5, never copied",
          rule.boundary == size_boundary(400, 0.005) == 5)
    check("CP lower at 5/400 and 6/400 are unchanged",
          abs(cp_lower(5, 400) - 0.004937934174346348) < 1e-15
          and abs(cp_lower(6, 400) - 0.006552145786997754) < 1e-15,
          f"{cp_lower(5, 400):.8f} / {cp_lower(6, 400):.8f}")
    check("5/400 is clean and 6/400 detects inflation",
          cp_lower(5, 400) <= 0.005 < cp_lower(6, 400))

    # --- the roster comes from the contract, not a private copy -------------
    declared = tuple(f["id"] for f in contract["fields"])
    check("the C2 roster IS the contract's declared field list, in order",
          rule.required_fields == declared, str(declared))
    check("the roster is the shared per-field roster, not a duplicate",
          rule.required_fields is FIELD_SIZE_REQUIRED_FIELDS)

    # --- every C2 surface is generated or strictly verified ------------------
    case, row, boundary = _c2_case(plan), _c2_assurance(plan), _c2_boundary(plan)
    check("scientific_purpose is the generated canonical text",
          case["scientific_purpose"] == render_c2_scientific_purpose())
    check("formal_pass_fail_criterion is the generated canonical text",
          case["formal_pass_fail_criterion"] == render_c2_criterion())
    for key, expected in render_c2_assurance().items():
        check(f"assurance[C2].{key} is generated", row[key] == expected)
    check("derived boundary rule is generated",
          boundary["rule"] == render_c2_boundary_rule())
    check("derived boundary pooling is generated and says FORBIDDEN",
          boundary["pooling"] == render_c2_pooling_statement()
          and boundary["pooling"].startswith("FORBIDDEN"))
    check("derived boundary per_field is generated true", boundary["per_field"] is True)
    check("derived boundary replicate_reduction is generated NONE",
          boundary["replicate_reduction"] == "NONE")
    check("the C2 final-campaign line is generated",
          plan["final_campaign_classification"]["requirements"][1]
          == render_c2_requirement(index=2))

    surfaces = [s for s in normative_surface_registry(plan) if s.case == "C2"]
    check("C2's whole normative surface is registered",
          len(surfaces) >= 45, str(len(surfaces)))
    check("UNBOUND C2 RULE-BEARING LOCATIONS = 0",
          all(s.mode in (GENERATED_FROM_CANONICAL, STRICTLY_VERIFIED_DUPLICATE)
              for s in surfaces),
          str(sorted({s.mode for s in surfaces})))
    check("no C2 surface is semantically free",
          not [s for s in surfaces if s.mode == NON_NORMATIVE_EXPLANATION])

    # --- NO SELF-VALIDATION -------------------------------------------------
    for path, token, replacement in (
            (f"cases[{_case_index(plan, 'C2_geometry_false_rejection')}]"
             ".formal_pass_fail_criterion", "PER FIELD, never pooled", "POOLED"),
            ("size_validation_semantics.derived_boundaries.C2.pooling",
             "FORBIDDEN", "ALLOWED")):
        mutant = copy.deepcopy(plan)
        path_set(mutant, path, _text_swap(path_get(mutant, path), token, replacement))
        honest = {s.path: s.expected for s in normative_surface_registry(plan)}
        corrupt = {s.path: s.expected for s in normative_surface_registry(mutant)}
        check(f"the expected value for {path.split('.')[-1]} is INDEPENDENT of the "
              "plan text", honest == corrupt)

    # --- the five alternative interpretations -------------------------------
    alternatives = (
        ("A. PER_FIELD / no pooling (canonical)", None, None),
        ("B. ANY_FIELD replicate event",
         "size_validation_semantics.derived_boundaries.C2.replicate_reduction",
         "ANY_FIELD"),
        ("C. EVERY_FIELD replicate event",
         "size_validation_semantics.derived_boundaries.C2.replicate_reduction",
         "EVERY_FIELD"),
        ("D. pooled 1600 field observations",
         "size_validation_semantics.derived_boundaries.C2.pooling",
         "POOLED - all four field counts summed over 1600 observations"),
        ("E. reference-field-only",
         f"cases[{_case_index(plan, 'C2_geometry_false_rejection')}].fields_affected",
         ["theta0_circular"]),
    )
    for label, path, value in alternatives:
        mutant = copy.deepcopy(plan)
        if path is None:
            check(f"{label} is ACCEPTED",
                  refusal_code(require_release_authority_conformance, contract,
                               mutant, ROOT) is None)
            continue
        before = path_get(mutant, path)
        assert before != value, f"{label}: mutation equals the approved value"
        path_set(mutant, path, value)
        check(f"{label} REFUSES",
              refusal_code(require_release_authority_conformance, contract, mutant,
                           ROOT) == "PROSPECTIVE_AMENDMENT_MISMATCH")

    # --- the four formerly unguarded prose surfaces -------------------------
    survived = []
    for label, where, field in C2_PROSE_SURFACES:
        for shape, text in C2_CONTRARY_TEXTS:
            mutant = copy.deepcopy(plan)
            holder = (_c2_case(mutant) if where == "cases"
                      else _c2_assurance(mutant))
            before = holder[field]
            holder[field] = text
            assert holder[field] != before, f"{label}: no change"
            got = refusal_code(require_release_authority_conformance, contract,
                               mutant, ROOT)
            if got is None:
                survived.append(f"{label} / {shape}")
            check(f"COHERENT BUT WRONG: {label} -> {shape} refuses",
                  got == "PROSPECTIVE_AMENDMENT_MISMATCH", f"got {got!r}")
    check(f"C2 prose audit: {len(C2_PROSE_SURFACES) * len(C2_CONTRARY_TEXTS)} "
          "tested, 0 unexpected passes", not survived, str(survived))

    # --- the rest of the C2 normative surface --------------------------------
    other = (
        ("per_field true -> false",
         lambda m: _c2_boundary(m).__setitem__("per_field", False)),
        ("derived boundary prose -> pooled",
         lambda m: _c2_boundary(m).__setitem__(
             "rule", "0-36 pooled rejections: no significant inflation detected")),
        ("assurance unit -> campaign",
         lambda m: _c2_assurance(m).__setitem__("unit", "campaign")),
        ("assurance pooling -> ALLOWED",
         lambda m: _c2_assurance(m).__setitem__("pooling", "ALLOWED")),
        ("R 400 -> 1600",
         lambda m: (_c2_assurance(m).__setitem__("replicates", 1600),
                    _c2_boundary(m).__setitem__("replicates", 1600))),
        ("alpha 0.005 -> 0.02",
         lambda m: _c2_assurance(m).__setitem__("target_value", 0.02)),
        ("boundary 5 -> 36",
         lambda m: _c2_assurance(m).__setitem__("integer_boundary", 36)),
        ("bound direction LOWER -> UPPER",
         lambda m: _c2_assurance(m).__setitem__("bound_direction", "UPPER")),
        ("primary endpoint -> POOLED",
         lambda m: _c2_case(m).__setitem__("primary_release_endpoint",
                                           "P1_FALSE_REJECTION_RATE_POOLED")),
        ("fields: remove",
         lambda m: _c2_case(m).__setitem__("fields_affected",
                                           ["theta0_circular", "theta1_power",
                                            "theta2_ellipse"])),
        ("fields: duplicate",
         lambda m: _c2_case(m).__setitem__("fields_affected",
                                           ["theta0_circular", "theta0_circular",
                                            "theta2_ellipse", "theta3_temperature"])),
        ("fields: replace",
         lambda m: _c2_case(m).__setitem__("fields_affected",
                                           ["theta0_circular", "theta1_power",
                                            "theta2_ellipse", "theta9_invented"])),
        ("fields: add",
         lambda m: _c2_case(m).__setitem__(
             "fields_affected", ["theta0_circular", "theta1_power", "theta2_ellipse",
                                 "theta3_temperature", "theta4_extra"])),
        ("final line -> reference field only",
         lambda m: m["final_campaign_classification"]["requirements"].__setitem__(
             1, "2. C2 produces no STATISTICAL_SIZE_FAILURE in the reference field")),
        ("final line -> three of four",
         lambda m: m["final_campaign_classification"]["requirements"].__setitem__(
             1, "2. C2 produces no STATISTICAL_SIZE_FAILURE in at least three "
                "required fields")),
        ("block1_role demoted",
         lambda m: _c2_case(m).__setitem__("block1_role", "SECONDARY_DIAGNOSTIC")),
    )
    loose = []
    for label, mutate in other:
        mutant = copy.deepcopy(plan)
        mutate(mutant)
        got = refusal_code(require_release_authority_conformance, contract, mutant,
                           ROOT)
        if got is None:
            loose.append(label)
        check(f"C2 SURFACE REFUSED: {label}", got is not None, f"got {got!r}")
    check(f"C2 surface audit: {len(other)} tested, 0 unexpected passes",
          not loose, str(loose))

    # --- the canonical rule itself cannot drift ------------------------------
    for name, wrong in (("pooling", "ALLOWED"), ("field_reduction", "ANY_FIELD"),
                        ("evaluation_scope", "CAMPAIGN"),
                        ("authority_relationship", EXACT),
                        ("replicates_per_field", 1600), ("nominal_alpha", 0.02)):
        broken = dataclasses.replace(rule, **{name: wrong})
        saved = release_authority.C2_RELEASE_RULE
        try:
            release_authority.C2_RELEASE_RULE = broken
            check(f"a drifted canonical rule refuses: {name} -> {wrong!r}",
                  refusal_code(require_c2_release_binding, contract, plan)
                  == "PROSPECTIVE_AMENDMENT_MISMATCH")
        finally:
            release_authority.C2_RELEASE_RULE = saved

    # --- C3/C4 authority is untouched ---------------------------------------
    for rule34 in FIELD_SIZE_RULES:
        short = rule34.case_id[:2]
        row34 = plan["size_validation_semantics"]["derived_boundaries"][short]
        check(f"{short} R, alpha and boundary unchanged by the C2 repair",
              (row34["replicates"], row34["nominal_alpha"], row34["boundary"])
              == (rule34.replicates, rule34.nominal_alpha, rule34.boundary))
        check(f"{short} scope/reduction/pooling unchanged by the C2 repair",
              (rule34.evaluation_scope, rule34.field_reduction, rule34.pooling)
              == ("PER_FIELD", "NONE", "FORBIDDEN"))
    check("C3's secondary diagnostic is still non-release-bearing",
          FIELD_SIZE_RULES_BY_CASE["C3_g5_block"]
          .secondary_feeds_primary_release is False)
    check("the C3/C4 G4 disposition still affects only C3 and C4",
          FIELD_SIZE_DISPOSITION_AFFECTS == "C3, C4")


# ------------------------ 22. F1f implementation conformance (runtime vs authority)
#: Implementation shapes that would LAG the cleared authority. Each is a complete
#: statement of how the runtime could still express the pre-amendment rule, and
#: each must be REFUSED by preflight rather than tolerated. The names are the ones
#: the amendment rules out by name.
IMPLEMENTATION_LAGS = (
    # the exact pre-F1f shape: one scalar case count instead of four field counts
    ("C3 scalar case count restored",
     {"c3_rejections_by_field": None, "c3_rejections": 0}),
    ("C4 scalar case count restored",
     {"c4_rejections_by_field": None, "c4_rejections": 0}),
    ("C2 scalar case count restored",
     {"c2_rejections_by_field": None, "c2_rejections": 0}),
    # the per-field counts simply missing
    ("C3 per-field counts dropped entirely", {"c3_rejections_by_field": None}),
    ("C4 per-field counts dropped entirely", {"c4_rejections_by_field": None}),
    # and the "harmless convenience" form: the scalar kept BESIDE the field map,
    # which is the ambiguity the amendment removed rather than a second opinion
    ("C3 scalar kept alongside the per-field map", {"c3_rejections": 0}),
    ("C4 scalar kept alongside the per-field map", {"c4_rejections": 0}),
    ("C2 scalar kept alongside the per-field map", {"c2_rejections": 0}),
)


def _counts_class(changes):
    """A CampaignCounts-shaped class with fields added or removed. TEST ONLY."""
    base = [(f.name, f.type)
            for f in dataclasses.fields(release_authority.CampaignCounts)]
    kept = [(name, typ) for name, typ in base if changes.get(name, "keep") is not None]
    added = [(name, int) for name, value in changes.items()
             if value is not None and name not in dict(base)]
    return dataclasses.make_dataclass("ProbeCounts", kept + added, frozen=True)


def _drifting_classifier(real, key, wrong):
    """The real classifier with ONE reported semantic value changed. TEST ONLY."""
    def drifted(counts):
        result = real(counts)
        result["endpoint_semantics"]["C3"][key] = wrong
        return result
    return drifted


def test_f1f_implementation_conformance() -> None:
    """The obsolete refusal was replaced by a POSITIVE proof, and it bites.

    F1f removed the driver's `ENDPOINT_EVENT_REDUCTION_UNDECLARED` placeholder for
    C3 and C4. Deleting a refusal is only half a repair: preflight must now REFUSE
    an implementation that still carries the scalar, replicate-level shape, so the
    runtime is held to authority rather than authority drifting to the runtime.
    """
    plan = load_plan(ROOT)
    check("the cleared per-field implementation is ACCEPTED",
          refusal_code(release_authority
                       .require_per_field_implementation_conformance, plan) is None)

    # --- the runtime SHAPE, mutated back to each lagging form ------------------
    saved = release_authority.CampaignCounts
    try:
        for label, changes in IMPLEMENTATION_LAGS:
            release_authority.CampaignCounts = _counts_class(changes)
            check(f"implementation lag REFUSED: {label}",
                  refusal_code(release_authority
                               .require_per_field_implementation_conformance, plan)
                  == "IMPLEMENTATION_AUTHORITY_LAG")
    finally:
        release_authority.CampaignCounts = saved
    check("the real counts class is restored",
          refusal_code(release_authority
                       .require_per_field_implementation_conformance, plan) is None)

    # --- the runtime PARAMETERS, drifted from the frozen boundary table --------
    saved_rules = dict(release_authority.PER_FIELD_SIZE_CASES)
    drifts = (("C2", (400, 0.01)), ("C3", (300, 0.001)), ("C4", (2000, 0.005)))
    try:
        for case, wrong in drifts:
            release_authority.PER_FIELD_SIZE_CASES[case] = wrong
            check(f"{case} runtime R/alpha drift REFUSED: {wrong}",
                  refusal_code(release_authority
                               .require_per_field_implementation_conformance, plan)
                  == "IMPLEMENTATION_AUTHORITY_LAG")
            release_authority.PER_FIELD_SIZE_CASES[case] = saved_rules[case]
    finally:
        release_authority.PER_FIELD_SIZE_CASES.clear()
        release_authority.PER_FIELD_SIZE_CASES.update(saved_rules)
    check("the frozen R/alpha table is restored and accepted",
          refusal_code(release_authority
                       .require_per_field_implementation_conformance, plan) is None)

    # --- the C3 SECONDARY diagnostic may not be promoted to release-bearing ---
    # Authority states that the joint P1 result does not change the C3 release
    # verdict. An implementation that reported it as release-bearing would be
    # asserting a second C3 release condition that no frozen document declares.
    # `classify_campaign` reads this table from its own module globals, so the
    # mutation must land there rather than in the release_authority namespace.
    endpoints = classification.PER_FIELD_ENDPOINTS
    saved_secondary = dict(endpoints["C3"]["secondary_diagnostic"])
    try:
        endpoints["C3"]["secondary_diagnostic"]["release_bearing"] = True
        check("promoting the C3 full-P1 diagnostic to release-bearing is REFUSED",
              refusal_code(release_authority
                           .require_per_field_implementation_conformance, plan)
              == "IMPLEMENTATION_AUTHORITY_LAG")
    finally:
        endpoints["C3"]["secondary_diagnostic"].clear()
        endpoints["C3"]["secondary_diagnostic"].update(saved_secondary)
    check("the C3 secondary diagnostic is restored to non-release-bearing",
          refusal_code(release_authority
                       .require_per_field_implementation_conformance, plan) is None)
    check("frozen authority still says the joint P1 result does not change the "
          "C3 verdict",
          _case(plan, "C3_g5_block")["c3_semantics"]
          ["joint_p1_result_changes_C3_release_verdict"] is False)

    # --- the reported scope/reduction/pooling may not drift from authority ----
    for key, wrong in (("field_scope", "PER_REPLICATE"),
                       ("pooling", "PERMITTED"),
                       ("within_replicate_field_reduction", "ANY_FIELD")):
        saved_rule = classification.classify_campaign
        try:
            classification.classify_campaign = _drifting_classifier(saved_rule,
                                                                    key, wrong)
            release_authority.classify_campaign = classification.classify_campaign
            check(f"a classifier reporting {key} = {wrong!r} is REFUSED",
                  refusal_code(release_authority
                               .require_per_field_implementation_conformance, plan)
                  == "IMPLEMENTATION_AUTHORITY_LAG")
        finally:
            classification.classify_campaign = saved_rule
            release_authority.classify_campaign = saved_rule

    # --- the conformance check reaches the FULL preflight ---------------------
    check("full preflight runs the per-field implementation conformance check",
          "require_per_field_implementation_conformance" in
          release_authority.require_release_authority_conformance.__code__.co_names)

    # --- the boundaries it enforces are RECOMPUTED, never copied --------------
    boundaries = plan["size_validation_semantics"]["derived_boundaries"]
    for case, (replicates, nominal) in PER_FIELD_SIZE_CASES.items():
        check(f"{case} boundary recomputed from the runtime parameters matches "
              "frozen authority",
              size_boundary(replicates, nominal) == boundaries[case]["boundary"],
              str(size_boundary(replicates, nominal)))

    # --- the driver counts per field and refuses every reduction --------------
    for case_id, event in (("C2_geometry_false_rejection", "p1_rejected"),
                           ("C3_g5_block", "g5_rejected"),
                           ("C4_surrogate_validity", "block1_rejected")):
        check(f"{case_id[:2]}: a cross-field reduction is FORBIDDEN",
              refusal_code(replicate_level_rejections, plan, {}, case_id, event)
              == "CROSS_FIELD_REDUCTION_FORBIDDEN")
        check(f"{case_id[:2]}: the per-field counter derives its roster from the "
              "frozen plan",
              set(_case(plan, case_id)["fields_affected"]) == REQUIRED_SIZE_FIELDS)
    check("the per-field counter exists and is what the driver calls",
          callable(per_field_rejections))


# ------------------------- 23. G5 structured-refusal authority (F1f-d)
def structured_refusal_mutations(plan):
    """Every coherent-but-wrong reading of the approved structured-refusal rule.

    Each entry names the exact authoritative location, so a mutation that fails to
    land is an assertion error rather than a false pass. All of them must REFUSE.
    """
    sr = "size_validation_semantics.structured_refusal"
    vd = "size_validation_semantics.verdicts"
    g5 = f"authority_gaps[{_gap_index(plan, REFUSAL_DISPOSITION_ID)}]"
    c3 = f"cases[{_case_index(plan, 'C3_g5_block')}].c3_semantics"
    c4 = f"cases[{_case_index(plan, 'C4_surrogate_validity')}].c4_semantics"
    b = "size_validation_semantics.derived_boundaries"
    return (
        # ---- the two readings the amendment exists to forbid ----------------
        ("None -> rejection (block)", f"{sr}.refusal_is_statistical_rejection",
         False, True),
        ("None -> rejection (C3)", f"{c3}.refusal_is_statistical_rejection",
         False, True),
        ("None -> rejection (C4)", f"{c4}.refusal_is_statistical_rejection",
         False, True),
        ("None -> non-rejection (block)",
         f"{sr}.refusal_is_statistical_non_rejection", False, True),
        ("None -> non-rejection (C3)",
         f"{c3}.refusal_is_statistical_non_rejection", False, True),
        ("None -> non-rejection (C4)",
         f"{c4}.refusal_is_statistical_non_rejection", False, True),
        # ---- the denominator shrinks to the survivors -----------------------
        ("evaluable_N becomes the primary denominator (block)",
         f"{sr}.primary_denominator", "PLANNED_R_PRESERVED", "EVALUABLE_N"),
        ("evaluable_N becomes the primary denominator (C3)",
         f"{c3}.primary_denominator_under_refusal", "PLANNED_R_PRESERVED",
         "EVALUABLE_N"),
        ("planned R dropped from the G5 resolution", f"{g5}.resolution",
         "PLANNED_R_PRESERVED -- R stays at its planned",
         "EVALUABLE_N -- R shrinks from its planned"),
        # ---- a refusal resolved into one of the two statistical verdicts ----
        ("refusal -> ordinary clean verdict", f"{vd}.on_undefined_primary_endpoint",
         NOT_EVALUABLE, "NO_SIGNIFICANT_SIZE_INFLATION_DETECTED"),
        ("refusal -> statistical size failure",
         f"{vd}.on_undefined_primary_endpoint", NOT_EVALUABLE,
         "STATISTICAL_SIZE_FAILURE"),
        ("refusal -> clean verdict (C3)",
         f"{c3}.primary_verdict_on_structured_refusal", NOT_EVALUABLE,
         "NO_SIGNIFICANT_SIZE_INFLATION_DETECTED"),
        ("refusal -> size failure (C4)",
         f"{c4}.primary_verdict_on_structured_refusal", NOT_EVALUABLE,
         "STATISTICAL_SIZE_FAILURE"),
        # ---- all-refused silently becomes clean -----------------------------
        ("the detector runs on an incomplete sequence", f"{vd}.evaluation_order",
         "the detector is NOT run", "the detector is run on the surviving replicates"),
        ("the precedence is inverted", f"{vd}.evaluation_order",
         "resolved in order: if any required PRIMARY endpoint decision",
         "resolved in order: if the detector fires first, and only then if any "
         "required PRIMARY endpoint decision"),
        # ---- NOT_EVALUABLE allowed to pass release --------------------------
        ("NOT_EVALUABLE may pass release (block)", f"{sr}.release_requires",
         "EVALUABLE_AND_CLEAN", "CLEAN_OR_NOT_EVALUABLE"),
        ("NOT_EVALUABLE may pass release (C3)", f"{c3}.release_requires",
         "EVALUABLE_AND_CLEAN", "CLEAN_OR_NOT_EVALUABLE"),
        ("NOT_EVALUABLE may pass release (final rule)",
         "final_campaign_classification.rule",
         "has NOT satisfied it, and prevents the campaign from passing",
         "has satisfied it, and does not prevent the campaign from passing"),
        ("NOT_EVALUABLE dropped from the C3 requirement line",
         "final_campaign_classification.requirements[2]",
         f"and no {NOT_EVALUABLE} field", "and NOT_EVALUABLE fields are tolerated"),
        ("NOT_EVALUABLE dropped from the C4 requirement line",
         "final_campaign_classification.requirements[3]",
         f"and no {NOT_EVALUABLE} field", "and NOT_EVALUABLE fields are tolerated"),
        # ---- the terminal report stops being mandatory ----------------------
        ("terminal report not required under all-refused",
         f"{sr}.terminal_report_required_under_all_refusals", True, False),
        ("the G5 resolution drops the terminal-report duty", f"{g5}.resolution",
         "The terminal campaign report MUST still be produced",
         "The terminal campaign report need NOT be produced"),
        # ---- a survivor-conditioned figure promoted to release-bearing ------
        ("survivor-conditioned rate becomes primary (block)",
         f"{sr}.survivor_conditioned_rate_role", "SECONDARY_DIAGNOSTIC_ONLY",
         "PRIMARY_RELEASE_BEARING"),
        ("survivor-conditioned rate becomes primary (C3)",
         f"{c3}.survivor_conditioned_rate_role", "SECONDARY_DIAGNOSTIC_ONLY",
         "PRIMARY_RELEASE_BEARING"),
        # ---- a tolerated-refusal threshold is invented ----------------------
        ("a tolerated-refusal fraction is introduced (block)",
         f"{sr}.tolerated_structured_refusal_fraction", "NONE", "0.01"),
        ("a tolerated-refusal fraction is introduced (C4)",
         f"{c4}.tolerated_structured_refusal_fraction", "NONE", "0.01"),
        ("the G5 resolution tolerates some refusals", f"{g5}.resolution",
         f"The tolerated structured-refusal fraction is "
         f"{STRUCTURED_REFUSAL_RULE.tolerated_fraction}",
         "The tolerated structured-refusal fraction is 1 percent"),
        # ---- full P1 substituted for the undefined block decision -----------
        ("C3: the G5 decision is claimed always defined",
         f"{c3}.undefined_primary_endpoint_possible", True, False),
        ("C4: the Block-1 decision is claimed always defined",
         f"{c4}.undefined_primary_endpoint_possible", True, False),
        ("C3 boundary row claims the decision is always defined",
         f"{b}.C3.undefined_primary_endpoint_possible", True, False),
        ("C4 boundary row claims the decision is always defined",
         f"{b}.C4.undefined_primary_endpoint_possible", True, False),
        # ---- C2 dragged into the amendment ----------------------------------
        ("C2 is claimed to have an undefined primary endpoint",
         f"{b}.C2.undefined_primary_endpoint_possible", False, True),
        ("C2 is given a NOT_EVALUABLE path", f"{b}.C2.verdict_on_structured_refusal",
         "NOT_APPLICABLE", NOT_EVALUABLE),
        # ---- the campaign failure reason becomes a statistical rejection ----
        ("the failure reason becomes a size failure (block)",
         f"{sr}.campaign_failure_classification", "VALIDATION_INCONCLUSIVE",
         "STATISTICAL_SIZE_FAILURE"),
        ("the failure reason becomes a size failure (C3)",
         f"{c3}.campaign_failure_classification_when_not_evaluable",
         "VALIDATION_INCONCLUSIVE", "STATISTICAL_SIZE_FAILURE"),
        # ---- the disposition record itself ----------------------------------
        ("G5 affects is widened to C2", f"{g5}.affects", "C3, C4", "C2, C3, C4"),
        ("G5 status is downgraded", f"{g5}.status", "CLOSED PROSPECTIVELY", "OPEN"),
        ("the G5 gap statement denies the gap", f"{g5}.gap",
         "can leave a C3 or C4 PRIMARY endpoint decision undefined",
         "never leaves a C3 or C4 PRIMARY endpoint decision undefined"),
        ("the encoding stops being neither/nor", f"{sr}.encoding",
         "NEITHER_REJECTION_NOR_NONREJECTION", "TREATED_AS_REJECTION"),
    )


def test_structured_refusal_authority() -> None:
    """F1f-d. The G5 amendment is bound to a canonical rule, not to prose.

    A valid structured refusal can leave a C3 G5 / C4 Block-1 decision undefined.
    Frozen authority defined refusal treatment for complete-pipeline success only,
    so the author decided prospectively: an undefined primary endpoint is NEITHER a
    rejection NOR a non-rejection, planned R is preserved, and the field's primary
    size assessment is NOT_EVALUABLE, which blocks release.
    """
    plan = load_plan(ROOT)

    # --- the canonical rule says exactly what was approved -------------------
    rule = STRUCTURED_REFUSAL_RULE
    check("an undefined primary endpoint is NOT a statistical rejection",
          rule.is_statistical_rejection is False)
    check("an undefined primary endpoint is NOT a statistical non-rejection",
          rule.is_statistical_non_rejection is False)
    check("the encoding is NEITHER_REJECTION_NOR_NONREJECTION",
          rule.encoding == "NEITHER_REJECTION_NOR_NONREJECTION")
    check("the planned denominator is preserved",
          rule.denominator_rule == "PLANNED_R_PRESERVED")
    check("the primary verdict on any structured refusal is NOT_EVALUABLE",
          rule.verdict == NOT_EVALUABLE)
    check("NOT_EVALUABLE is neither of the two statistical verdicts",
          rule.verdict != SIZE_FAILURE and rule.verdict != SIZE_NO_INFLATION)
    check("release requires EVALUABLE_AND_CLEAN",
          rule.release_requirement == "EVALUABLE_AND_CLEAN")
    check("the campaign failure reason is not a size failure",
          rule.campaign_classification == "VALIDATION_INCONCLUSIVE"
          and rule.campaign_classification != SIZE_FAILURE)
    check("the failure reason is a DECLARED frozen classification",
          rule.campaign_classification in plan["failure_classifications"])
    check("no tolerated-refusal fraction is introduced",
          rule.tolerated_fraction == "NONE")
    check("a survivor-conditioned rate is SECONDARY only",
          rule.survivor_role == "SECONDARY_DIAGNOSTIC_ONLY")
    check("the terminal report is required under all refusals",
          rule.terminal_report_required is True)
    check("the required terminal counts distinguish the three states",
          set(rule.required_terminal_counts) >= {
              "planned_R", "evaluable_primary_endpoint_count",
              "structured_refusal_count", "defined_rejection_count",
              "primary_size_status"})

    # --- the amendment reaches C3 and C4 and NOT C2 -------------------------
    check("C2's primary endpoint cannot be undefined",
          PRIMARY_ENDPOINT_UNDEFINABLE["C2"][0] is False)
    check("C3's and C4's primary endpoints can be undefined",
          PRIMARY_ENDPOINT_UNDEFINABLE["C3"][0] is True
          and PRIMARY_ENDPOINT_UNDEFINABLE["C4"][0] is True)
    check("the disposition declares it affects C3 and C4 only",
          REFUSAL_DISPOSITION_AFFECTS == "C3, C4")
    boundaries = plan["size_validation_semantics"]["derived_boundaries"]
    check("C2's boundary row records the scope-out explicitly",
          boundaries["C2"]["undefined_primary_endpoint_possible"] is False
          and boundaries["C2"]["verdict_on_structured_refusal"] == "NOT_APPLICABLE")
    check("C2's own release rule is untouched by the amendment",
          boundaries["C2"]["replicates"] == 400
          and boundaries["C2"]["nominal_alpha"] == 0.005
          and boundaries["C2"]["boundary"] == 5)

    # --- every normative rendering IS the canonical rule --------------------
    gap = plan["authority_gaps"][_gap_index(plan, REFUSAL_DISPOSITION_ID)]
    check("the G5 gap statement is the generated canonical text",
          gap["gap"] == render_refusal_gap_statement())
    check("the G5 resolution is the generated canonical text",
          gap["resolution"] == render_refusal_disposition())
    svs = plan["size_validation_semantics"]
    for key, value in render_structured_refusal_block().items():
        check(f"structured_refusal.{key} is generated",
              svs["structured_refusal"][key] == value)
    check("the third verdict is generated",
          svs["verdicts"]["on_undefined_primary_endpoint"] == rule.verdict)
    check("the verdict precedence is generated",
          svs["verdicts"]["evaluation_order"] == render_refusal_verdict_order())
    for field_rule in FIELD_SIZE_RULES:
        case = next(c for c in plan["cases"] if c["case_id"] == field_rule.case_id)
        for key, value in render_refusal_semantics(field_rule).items():
            check(f"{field_rule.case_id[:2]} semantics {key} is generated",
                  case[field_rule.semantics_key][key] == value)

    # --- the numeric size rules are UNCHANGED when evaluable ----------------
    for field_rule in FIELD_SIZE_RULES:
        short = field_rule.case_id[:2]
        row = boundaries[short]
        check(f"{short} R, alpha and boundary are untouched by the amendment",
              (row["replicates"], row["nominal_alpha"], row["boundary"])
              == (field_rule.replicates, field_rule.nominal_alpha,
                  field_rule.boundary))
        check(f"{short} scope, reduction and pooling are untouched",
              (field_rule.evaluation_scope, field_rule.field_reduction,
               field_rule.pooling) == ("PER_FIELD", "NONE", "FORBIDDEN"))
    check("C3's secondary P1 diagnostic is still non-release-bearing",
          FIELD_SIZE_RULES_BY_CASE["C3_g5_block"]
          .secondary_feeds_primary_release is False)
    check("the disposition FORBIDS multiplicity corrections rather than adding one",
          "no refusal threshold, Bonferroni correction, familywise correction, "
          "new alpha or new integer boundary is introduced"
          in render_refusal_disposition())

    # --- MUTATION AUDIT: every coherent wrong reading REFUSES ---------------
    mutations = structured_refusal_mutations(plan)
    unexpected = []
    for component, path, old_token, new_token in mutations:
        tmp = sandbox()
        mutant = rj(tmp, PLAN_JSON)
        before = path_get(mutant, path)
        after = (_text_swap(before, old_token, new_token)
                 if isinstance(before, str) else new_token)
        assert after != before, f"{component}: mutation did not change {path}"
        path_set(mutant, path, after)
        wj(tmp, PLAN_JSON, mutant)
        try:
            regenerate(tmp)       # Markdown made COHERENT with the mutated JSON
        except Refusal:
            pass
        got = refusal_code(preflight, tmp)
        if got is None:
            unexpected.append(f"{component} @ {path}")
        check(f"COHERENT BUT WRONG: {component} refuses", got is not None,
              f"got {got!r}")
        shutil.rmtree(tmp)
    check(f"structured-refusal mutation audit: {len(mutations)} tested, "
          "0 unexpected passes", not unexpected, str(unexpected))

    # --- the RUNTIME now implements this authority (closed by F1f-e) --------
    # When the amendment landed, `per_field_rejections` still raised
    # ENDPOINT_EVENT_MISSING on a refused record and the lag was recorded here.
    # F1f-e closed it; the assertions below are the repaired behaviour.
    refused = {"job": {"coordinates": {"case_id": "C3_g5_block",
                                       "subcondition_id": "sigma_psi_0p5",
                                       "replicate_id": 0,
                                       "scope": "theta0_circular"},
                       "result": {"analysis_status": "RANK_GUARD_FAIL",
                                  "P1": False, "p1_rejected": True,
                                  "block1_rejected": None, "g5_rejected": None}}}
    small = copy.deepcopy(plan)
    for case in small["cases"]:
        if case["case_id"] == "C3_g5_block":
            case["replicate_count"] = 1
            case["fields_affected"] = ["theta0_circular"]
    # F1f-e CLOSED the lag this assertion used to record. The aggregator now has a
    # defined path for a valid structured refusal and returns three-state evidence
    # instead of raising, so the terminal report the contract requires is produced.
    outcome = per_field_primary_outcomes(small, refused, "C3_g5_block",
                                         "g5_rejected")["theta0_circular"]
    check("the runtime now AGGREGATES a valid structured refusal (F1f-e)",
          outcome.structured_refusals == 1 and outcome.evaluable == 0
          and outcome.planned_replicates == 1, str(outcome))
    check("and resolves it to the authority verdict, not to a boolean",
          classify_field_size(outcome, 0.001)["verdict"] == NOT_EVALUABLE)
    check("authority now REQUIRES the terminal report under all refusals",
          svs["structured_refusal"]["terminal_report_required_under_all_refusals"]
          is True)
    check("execution is still not authorised", plan["execution_authorised"] is False)


# ------------------- 24. F1f-e refusal-aware RUNTIME conformance
def _patched_classifier(real, mutate):
    """The real classifier with one reported row rewritten. TEST ONLY."""
    def patched(counts):
        result = real(counts)
        mutate(result)
        return patched_fix(result)
    def patched_fix(result):
        # the failures list is rebuilt from the mutated detail, so the probe sees
        # a self-consistent -- and wrong -- implementation rather than a mismatch
        rebuilt = [f for f in result["failures"]
                   if not f.startswith(INCOMPLETE_EVIDENCE_CLASSIFICATION)]
        result["failures"] = rebuilt
        result["verdict"] = ("VALIDATION_PASS" if not rebuilt
                             else "VALIDATION_FAILURE")
        return result
    return patched


def test_f1f_e_runtime_conformance() -> None:
    """F1f-e. Preflight now REFUSES a runtime that is not refusal-aware.

    The G5 amendment deliberately left the runtime behind, and the lag was carried
    as a known-failing assertion. The runtime has now been repaired, so preflight
    asserts the three-state behaviour instead: a structured refusal resolved first,
    the planned denominator preserved, and NOT_EVALUABLE blocking release under a
    reason that is not a statistical rejection.
    """
    plan = load_plan(ROOT)
    check("the repaired runtime is ACCEPTED",
          refusal_code(require_per_field_implementation_conformance, plan, ROOT)
          is None)

    # --- the per-field evidence SHAPE --------------------------------------
    saved_outcome = release_authority.FieldSizeOutcome
    required = ("evaluable", "structured_refusals", "planned_replicates",
                "refusal_reasons")
    try:
        for dropped in required:
            kept = [(f.name, f.type) for f in dataclasses.fields(saved_outcome)
                    if f.name != dropped]
            release_authority.FieldSizeOutcome = dataclasses.make_dataclass(
                "ProbeOutcome", kept, frozen=True)
            check(f"evidence without {dropped!r} is REFUSED",
                  refusal_code(require_per_field_implementation_conformance,
                               plan, ROOT) == "IMPLEMENTATION_AUTHORITY_LAG")
    finally:
        release_authority.FieldSizeOutcome = saved_outcome
    check("the real evidence class is restored",
          refusal_code(require_per_field_implementation_conformance, plan, ROOT)
          is None)

    # --- the three-state BEHAVIOUR -----------------------------------------
    def to_clean(result):
        for case in ("C3", "C4"):
            for row in result["detail"][case].values():
                if row["verdict"] == NOT_EVALUABLE:
                    row["verdict"] = SIZE_NO_INFLATION

    def to_size_failure(result):
        for case in ("C3", "C4"):
            for row in result["detail"][case].values():
                if row["verdict"] == NOT_EVALUABLE:
                    row["verdict"] = SIZE_FAILURE

    def shrink_denominator(result):
        for case in ("C3", "C4"):
            for row in result["detail"][case].values():
                if row["verdict"] == NOT_EVALUABLE:
                    row["planned_replicates"] = row["evaluable"]

    saved_classifier = release_authority.classify_campaign
    probes = (
        ("a structured refusal resolved to an ordinary CLEAN verdict", to_clean),
        ("a structured refusal resolved to a STATISTICAL size failure",
         to_size_failure),
        ("the planned denominator replaced by the evaluable count",
         shrink_denominator),
    )
    try:
        for label, mutate in probes:
            release_authority.classify_campaign = _patched_classifier(
                saved_classifier, mutate)
            check(f"REFUSED: {label}",
                  refusal_code(require_per_field_implementation_conformance,
                               plan, ROOT) == "IMPLEMENTATION_AUTHORITY_LAG")
        # NOT_EVALUABLE allowed to pass: drop the incomplete-evidence failures
        release_authority.classify_campaign = _patched_classifier(
            saved_classifier, lambda result: None)
        check("REFUSED: a NOT_EVALUABLE field allowed to pass release",
              refusal_code(require_per_field_implementation_conformance,
                           plan, ROOT) == "IMPLEMENTATION_AUTHORITY_LAG")
    finally:
        release_authority.classify_campaign = saved_classifier
    check("the real classifier is restored and accepted",
          refusal_code(require_per_field_implementation_conformance, plan, ROOT)
          is None)

    # --- the DRIVER must have a defined aggregation path -------------------
    check("the canonical driver declares the refusal-aware surface",
          set(REFUSAL_AWARE_DRIVER_SURFACE) <= _driver_declares(ROOT),
          str(sorted(set(REFUSAL_AWARE_DRIVER_SURFACE) - _driver_declares(ROOT))))
    for dropped in REFUSAL_AWARE_DRIVER_SURFACE:
        tmp = sandbox()
        path = os.path.join(tmp, "e1a_v4/validation/campaign_driver.py")
        with open(path, encoding="utf-8") as handle:
            source = handle.read()
        # remove ONE top-level definition, leaving the file parseable
        source = source.replace(f"\ndef {dropped}(", f"\ndef _removed_{dropped}(", 1)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(source)
        check(f"REFUSED: a driver declaring no {dropped!r}",
              refusal_code(require_per_field_implementation_conformance, plan, tmp)
              == "IMPLEMENTATION_AUTHORITY_LAG")
        shutil.rmtree(tmp)

    # --- the authority this conformance check is held to --------------------
    refusal = plan["size_validation_semantics"]["structured_refusal"]
    check("the check compares against the FROZEN authority, not its own opinion",
          refusal["primary_verdict_on_any_structured_refusal"] == NOT_EVALUABLE
          and refusal["primary_denominator"] == "PLANNED_R_PRESERVED"
          and refusal["release_requires"] == "EVALUABLE_AND_CLEAN"
          and refusal["campaign_failure_classification"]
          == INCOMPLETE_EVIDENCE_CLASSIFICATION)
    check("the amendment is still C3/C4 only and C2 keeps its scope-out",
          refusal["applies_to"] == "C3, C4"
          and plan["size_validation_semantics"]["derived_boundaries"]["C2"]
          ["undefined_primary_endpoint_possible"] is False)
    check("execution is still not authorised", plan["execution_authorised"] is False)


GROUPS = (
    ("the auditor's four named release escape routes", test_named_release_probes),
    ("C3/C4 per-field authority (G4)", test_c3_c4_per_field_authority),
    ("C3/C4 amendment semantic mutations",
     test_c3_c4_amendment_semantic_mutations),
    ("C3/C4 normative-surface totality",
     test_c3_c4_normative_surface_totality),
    ("C3 explanatory semantics bound to canonical authority",
     test_c3_explanatory_semantics),
    ("nested size-validation semantic-leaf totality",
     test_nested_semantic_leaf_totality),
    ("final-list totality and fixed deferred scope",
     test_list_and_deferred_scope_totality),
    ("F1f runtime implementation conformance",
     test_f1f_implementation_conformance),
    ("F1f-d G5 structured-refusal authority", test_structured_refusal_authority),
    ("F1f-e refusal-aware runtime conformance", test_f1f_e_runtime_conformance),
    ("C2 DERIVED per-field authority binding",
     test_c2_derived_authority_binding),
    ("EXACT release bindings: complete mutation audit", test_exact_mutation_audit),
    ("CASE_SPECIFIC pins", test_case_specific_bindings_refuse),
    ("DERIVED release quantities", test_derived_bindings),
    ("IMPLIED_STRONGER: the C2 implication proof", test_implied_stronger),
    ("mandatory contract diagnostics", test_mandatory_diagnostics),
    ("mandatory reporting wording and result schema", test_mandatory_wording),
    ("the three independent layers", test_independent_layers),
    ("the complete C1-C8 release table", test_case_release_table),
    ("measured release-authority completeness", test_release_inventory_counts),
    ("NOT_APPLICABLE audit", test_not_applicable_audit),
    ("no E1a scientific decision rule changed", test_no_scientific_rule_changed),
    ("earlier contract-plan conformance preserved", test_prior_conformance_preserved),
    ("execution boundary", test_execution_boundary_unchanged),
)


if __name__ == "__main__":
    for title, fn in GROUPS:
        print(f"\n{title}")
        fn()
    print(f"\nE1a v4 release-authority gate: {PASSED} passed, {FAILED} failed, "
          f"{len(GROUPS)} groups")
    print("Execution class: NON-MODEL-ADVANCING STATIC/PURE (this suite only)")
    print(f"  RNG OBJECTS           : {SentinelRNG.CALLS}")
    print("  RANDOM DRAWS          : 0")
    print("  TRAJECTORIES          : 0")
    raise SystemExit(1 if FAILED else 0)
