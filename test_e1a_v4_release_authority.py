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
import json
import os
import re
import shutil
import tempfile

from e1a_v4.numerics import Refusal
from e1a_v4.validation import PLAN_JSON, PLAN_MARKDOWN, SEED_MAP_JSON
from e1a_v4.validation.classification import (
    GROSS_INFLATION_LABEL, GROSS_INFLATION_TOLERANCE, size_boundary,
)
from e1a_v4.validation.coherence import (
    BLOCK_BEGIN, BLOCK_END, REGION_ANCHORS, SECTION_REGISTRY,
    render_authority_block, render_region, require_plan_authority_coherence,
)
from e1a_v4.validation.contract_plan import (
    DELEGATED_TO_RELEASE_AUTHORITY, NOT_REPEATED_CONTRACT_LEAVES, binding_inventory,
)
from e1a_v4.validation.dispositions import cp_lower, cp_upper
from e1a_v4.validation.campaign_driver import replicate_level_rejections
from e1a_v4.validation.plan import load_plan
from e1a_v4.validation.release_authority import (
    CASE_SPECIFIC, CONTRACT, DERIVED, EXACT, IMPLIED_STRONGER, NOT_APPLICABLE,
    FIELD_SIZE_RULES, VERIFICATION_MODES, field_size_amendment_counts,
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
    ("A. C1 complete-pipeline target 0.90 -> 0.80", probe_c1_target,
     "CONTRACT_RELEASE_TARGET_MISMATCH"),
    ("B. C1 R = 300 -> 301", probe_c1_replicates,
     "CONTRACT_RELEASE_REPLICATE_COUNT_MISMATCH"),
    # C3's criterion is GENERATED from the canonical amendment, which carries
    # R = 400, so moving R now contradicts the amendment before the replicate-count
    # binding is reached. Both refusals are correct; the earlier one is accepted.
    ("C. C3 R = 400 -> 401, derived boundary recomputed", probe_c3_replicates,
     ("PROSPECTIVE_AMENDMENT_MISMATCH",
      "CONTRACT_RELEASE_REPLICATE_COUNT_MISMATCH")),
    ("D. C8 R = 200 -> 201", probe_c8_replicates,
     "CONTRACT_RELEASE_REPLICATE_COUNT_MISMATCH"),
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

    # --- implementation is deliberately BEHIND authority --------------------
    for case_id, event in (("C3_g5_block", "g5_rejected"),
                           ("C4_surrogate_validity", "block1_rejected")):
        check(f"the driver still REFUSES to reduce {case_id[:2]} across fields, "
              "which is now authority-correct rather than a guess",
              refusal_code(replicate_level_rejections, plan, {}, case_id, event)
              == "ENDPOINT_EVENT_REDUCTION_UNDECLARED")
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
        "in any required field", "in the reference field")
    add("final release requirement C4",
        "final_campaign_classification.requirements[3]",
        "in any required field", "in at least three required fields")

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
        check(f"the driver is STILL behind authority and still refuses for "
              f"{case_id[:2]}",
              refusal_code(replicate_level_rejections, plan, {}, case_id, event)
              == "ENDPOINT_EVENT_REDUCTION_UNDECLARED")


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
    check("the registry covers every controlled container",
          counts["controlled_containers"] == 8, str(counts))
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
        check(f"the driver is STILL behind authority for {case_id[:2]} (pre-F1f)",
              refusal_code(replicate_level_rejections, plan, {}, case_id, event)
              == "ENDPOINT_EVENT_REDUCTION_UNDECLARED")


GROUPS = (
    ("the auditor's four named release escape routes", test_named_release_probes),
    ("C3/C4 per-field authority (G4)", test_c3_c4_per_field_authority),
    ("C3/C4 amendment semantic mutations",
     test_c3_c4_amendment_semantic_mutations),
    ("C3/C4 normative-surface totality",
     test_c3_c4_normative_surface_totality),
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
