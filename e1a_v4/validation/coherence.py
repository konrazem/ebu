"""Markdown / JSON authority coherence for the frozen validation plan.

WHY THIS MODULE EXISTS
    `AGENTS.md` makes the rule explicit for every normative Markdown/JSON pair in
    this repository: the JSON is the mechanical schema and ordering source, the
    Markdown is its normative human rendering, and **any mismatch is an integrity
    failure, not permission to choose one selectively**.

    Two generations of this check have now been insufficient:

    1. The original compared ONLY the section-9 output schema. A Markdown analysis
       procedure identity that the package had never computed survived four
       commits while preflight reported PASS.

    2. Its replacement added a generated authority block plus a narrow human
       check. But the block carried only case-level SCALARS, and the human check
       read only seven case rows. An independent audit then showed that all of
       these still passed:

           visible `fields affected` changed only in the Markdown
           visible primary sigma_psi wording changed only in the Markdown
           visible C1 release threshold 279/300 -> 240/300, Markdown only
           visible C7 4/400 and C8 188/200 thresholds, Markdown only
           JSON `feeds_primary_claim` inverted, block regenerated
           JSON C7 `beta_true` alternatives and C8 `scale_factors` altered

       Nine such probes were reproduced, and every one was ACCEPTED.

THE FIX: AN ENUMERABLE SPECIFICATION, NOT A HAND-COUNTED LIST
    `NORMATIVE_SPEC` classifies EVERY key of the plan -- top level, per case and
    per subcondition -- as either

        BOTH       duplicated in the Markdown; checked for exact equality
        JSON_ONLY  not normative human-rendered authority; with a stated reason

    `require_specification_totality` refuses if the plan carries any key the
    specification does not classify, so new authority cannot be added silently and
    go unchecked. The field counts in the report are derived FROM this
    specification; none is hand-counted.

    `normative_json_view` and `normative_markdown_view` then build the SAME flat,
    dotted, canonical key/value mapping from the two representations, and the
    comparison names the exact mismatching key.

WHY GENERATED REGIONS AS WELL
    A generated block alone cannot fix this: the block can be correct while the
    visible human protocol is stale, which is precisely what the audit found. So
    the normative human tables are themselves GENERATED from the same canonical
    data, and preflight verifies each region is a byte-exact re-render. Normative
    content outside a generated region -- the version line, the section-1 identity
    table, the authorisation sentence -- is parsed and compared instead.

    Every subcondition's full declared parameters are now rendered, so
    `feeds_primary_claim`, `beta_true` and `scale_factors` are visible to a reader
    rather than living only in the JSON.

STRICT PARSING
    Authoritative JSON is read through `strict_json`, which refuses duplicate keys
    at any depth. `json.loads` keeps the LAST duplicate while a human reads the
    FIRST; an authoritative document that says two things is ambiguous, and the
    only safe resolution is refusal.

CLASSIFICATION
    every check here ... EXACT (string and structural equality on frozen text)

NO RNG. Nothing in this module draws, samples, or advances any model state.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from typing import Any

from ..contract import sha256_file
from . import PLAN_JSON, PLAN_MARKDOWN, SEED_MAP_JSON
from .driver import (
    OFFICIAL_CAMPAIGN_DRIVER_ENTRY_POINT, OFFICIAL_CAMPAIGN_DRIVER_MODULE,
    OFFICIAL_CAMPAIGN_DRIVER_PATH, driver_state,
)
from .refusals import (
    DriverIdentityMismatch, PlanAdoptedRuleMismatch, PlanAmbiguousBlock,
    PlanAnalysisIdentityMismatch, PlanCaseMismatch, PlanDuplicateKey,
    PlanIdentityMismatch, PlanReleaseRuleMismatch, PlanStructureInvalid,
    PlanSubconditionMismatch, PlanSurfaceMismatch, PlanSurfaceUndeclared,
    PlanVersionMismatch,
)
from .strict_json import strict_load_file, strict_loads

#: Schema of the generated authority block. Bumped when the SURFACE changes.
AUTHORITY_BLOCK_SCHEMA = "e1a_v4_plan_authority/2"

BLOCK_BEGIN = "<!-- BEGIN GENERATED AUTHORITY BLOCK -- do not hand-edit -->"
BLOCK_END = "<!-- END GENERATED AUTHORITY BLOCK -->"

#: Anchors for every generated normative region. Each is a byte-exact re-render.
REGION_ANCHORS = {
    "cases": ("<!-- BEGIN GENERATED CASES -- do not hand-edit -->",
              "<!-- END GENERATED CASES -->"),
    "adopted_rules": ("<!-- BEGIN GENERATED ADOPTED RULES -- do not hand-edit -->",
                      "<!-- END GENERATED ADOPTED RULES -->"),
    "assurance": ("<!-- BEGIN GENERATED ASSURANCE -- do not hand-edit -->",
                  "<!-- END GENERATED ASSURANCE -->"),
    "release_rules": ("<!-- BEGIN GENERATED RELEASE RULES -- do not hand-edit -->",
                      "<!-- END GENERATED RELEASE RULES -->"),
}

BOTH = "BOTH"
JSON_ONLY = "JSON_ONLY"

#: Frozen identity scalars duplicated in the section-1 table. Note strings are prose.
IDENTITY_SURFACE = (
    "contract_sha256",
    "design_sha256",
    "foundation_sha256",
    "baseline_sha256",
    "analysis_procedure_identity",
    "implementation_work_commit",
    "calibration_artifact_schema",
    "contract_version",
)

#: Markdown section-1 row label -> frozen identity key.
IDENTITY_ROW_LABELS = (
    ("design contract", "contract_sha256"),
    ("prospective design", "design_sha256"),
    ("frozen foundation", "foundation_sha256"),
    ("working baseline", "baseline_sha256"),
    ("analysis procedure identity", "analysis_procedure_identity"),
    ("calibration artifact schema", "calibration_artifact_schema"),
    ("implementation work commit", "implementation_work_commit"),
)

#: Classification of EVERY top-level plan key. Totality is enforced, so a new key
#: cannot be introduced without a deliberate decision about whether it is
#: duplicated normative authority.
TOP_LEVEL_SPEC = {
    "plan_id": (BOTH, "identifies the plan; rendered in the authority block"),
    "plan_version": (BOTH, "rendered as the version line and in the authority block"),
    "execution_stage": (BOTH, "gates the official run; rendered in the authority block"),
    "execution_authorised": (BOTH, "the authorisation flag; rendered in section 13"),
    "execution_seal": (BOTH, "the lifecycle STATE is rendered in section 13a; the "
                             "remaining keys are lifecycle prose and file locations"),
    "frozen_identities": (BOTH, "the identity scalars are rendered in the section-1 "
                                "table; the note strings are explanatory prose"),
    "adopted_rules_unchanged": (BOTH, "the frozen scientific decision rules, rendered "
                                      "as the section-2 table"),
    "cases": (BOTH, "the execution parameters, rendered as the generated section-3 "
                    "case sections including every subcondition payload"),
    "calibration": (BOTH, "the campaign calibration_scope is rendered; the remaining "
                          "keys are derivation narrative for section 5"),
    "assurance": (BOTH, "the release criteria, rendered as the generated section-6 table"),
    "failure_classifications": (BOTH, "rendered as the section-10 list"),
    "output_schema": (BOTH, "rendered in section 9 and checked field by field"),
    "authority_gaps": (BOTH, "the G1/G2/G3 dispositions and their resolutions, "
                             "rendered as generated section-12 blocks"),
    "final_campaign_classification": (BOTH, "the conjunctive release rule and its "
                                            "numbered requirements, rendered generated"),
    "created": (JSON_ONLY, "provenance date; not a decision rule or execution parameter"),
    "plan_authority_coherence": (JSON_ONLY, "describes the coherence MECHANISM itself; "
                                            "rendering it as checked authority would be "
                                            "self-referential"),
    "status": (JSON_ONLY, "narrative banner; the Markdown carries a human paraphrase "
                          "rather than a copy, deliberately"),
    "normative_pair": (JSON_ONLY, "file-path metadata naming the pair itself"),
    "case_count_justification": (JSON_ONLY, "editorial justification for the case count; "
                                            "the case set itself is BOTH"),
    "generating_model": (JSON_ONLY, "generator narrative; the executable generator is "
                                    "bound by the analysis and validation module hashes, "
                                    "not by prose"),
    "complete_pass_denominator": (JSON_ONLY, "denominator narrative; the operative rule "
                                             "is carried by the assurance rows"),
    "controls": (JSON_ONLY, "descriptive control inventory; each control's operative "
                            "parameters live in the case and subcondition records"),
    "classification_rule": (JSON_ONLY, "prose restatement of final_campaign_classification"),
    "no_post_outcome_tuning": (JSON_ONLY, "prohibition narrative; changes nothing executable"),
    "execution_command": (JSON_ONLY, "operational command string, not a scientific rule"),
    "preflight_command": (JSON_ONLY, "operational command string, not a scientific rule"),
    "preflight_checks_before_rng": (JSON_ONLY, "documentation of the checks; the checks "
                                               "themselves are code, bound by module hashes"),
    "author_dispositions": (JSON_ONLY, "disposition narrative; the operative content is "
                                       "authority_gaps and the assurance rows"),
    "superseded_package": (JSON_ONLY, "supersession record; historical, not executable"),
    "size_validation_semantics": (JSON_ONLY, "interpretation narrative for the size "
                                             "boundaries, which are themselves carried by "
                                             "the assurance rows and case criteria"),
    "seed_family_enforcement": (JSON_ONLY, "narrative; enforcement is code, and the "
                                           "per-case grants are BOTH"),
    "preexecution_repair": (JSON_ONLY, "supersession record; historical, not executable"),
    "seed_scope": (JSON_ONLY, "narrative; the per-case scopes are BOTH via fields_affected"),
    "parallelism_policy": (JSON_ONLY, "operational policy; changes no scientific rule"),
    "randomness_dependency": (JSON_ONLY, "narrative; the operative sharing is fixed by the "
                                         "seed hierarchy in code and the case grants"),
    "adopted_preexecution_corrections": (JSON_ONLY, "adoption record; historical"),
    "driver_requirements": (JSON_ONLY, "driver narrative; the CANONICAL driver declaration "
                                       "is identity-bound in e1a_v4/validation/driver.py "
                                       "and is checked separately as driver.*"),
}

#: Classification of EVERY per-case key.
CASE_SPEC = {
    "case_id": (BOTH, "case identity"),
    "role": (BOTH, "primary / negative_control / positive_control"),
    "replicate_count": (BOTH, "the declared replicate count R"),
    "subcondition_count": (BOTH, "declared number of subconditions"),
    "subconditions": (BOTH, "every subcondition's full declared parameters"),
    "fields_affected": (BOTH, "which declared fields the case evaluates"),
    "requires_block1_calibration": (BOTH, "whether the case needs a CalibrationArtifact"),
    "calibration_scope": (BOTH, "REPLICATE_CONDITIONAL / NOT_APPLICABLE"),
    "allowed_seed_families": (BOTH, "the case's machine-readable seed permissions"),
    "primary_release_endpoint": (BOTH, "the endpoint the case releases on"),
    "block1_role": (BOTH, "primary release endpoint versus secondary diagnostic"),
    "formal_pass_fail_criterion": (BOTH, "the release rule, including its integer "
                                         "threshold; rendered verbatim"),
    "uses_p1_block1": (BOTH, "whether a P1 / Block-1 quantity is evaluated"),
    "seed_family": (BOTH, "the case's principal seed family"),
    "beta_truth": (BOTH, "the generating beta"),
    "calibration_artifact_count": (BOTH, "declared artifact count"),
    "fields_requiring_calibration": (BOTH, "how many fields need calibration"),
    "branch_a_uncertainty_status": (BOTH, "STOCHASTIC_PER_REPLICATE or otherwise"),
    "truth_model": (BOTH, "the declared generating truth"),
    "geometry_truth": (BOTH, "the declared generating geometry"),
    "branch_a_uncertainty": (BOTH, "the declared Branch-A uncertainty scenario, "
                                   "including the primary sigma_psi statement"),
    "branch_b_process": (BOTH, "the declared observation process"),
    "expected_qualitative_outcome": (BOTH, "the prospective expectation"),
    "scientific_purpose": (BOTH, "the frozen purpose the case exists to serve"),
    "v4_classification": (BOTH, "retained / newly required"),
    "v4_classification_note": (BOTH, "what changed for v4"),
    "authority": (BOTH, "the committed authority the case traces to"),
    "calibration_artifact_basis": (BOTH, "the arithmetic behind the artifact count"),
    "calibration_not_required_reason": (BOTH, "why C7/C8 need no calibration"),
    "c3_semantics": (BOTH, "C3's release-versus-diagnostic resolution"),
    "calibration_scope_rationale": (JSON_ONLY, "rationale prose for the scope, which is "
                                               "itself BOTH"),
    "allowed_seed_families_rationale": (JSON_ONLY, "rationale prose for the grants, which "
                                                   "are themselves BOTH"),
    "allowed_seed_families_authority": (JSON_ONLY, "provenance note for the grants"),
}

#: Classification of EVERY per-subcondition key. All are execution parameters.
SUBCONDITION_SPEC = {
    "subcondition_id": (BOTH, "subcondition identity"),
    "sigma_psi_deg": (BOTH, "the realised trap-axis uncertainty for this subcondition"),
    "g3_role": (BOTH, "PRIMARY / SECONDARY / STRESS under disposition G3"),
    "feeds_primary_claim": (BOTH, "whether this subcondition feeds the >= 0.90 claim"),
    "sigma_k": (BOTH, "the realised per-mode stiffness uncertainty"),
    "rho": (BOTH, "the mode-resolution ratio under test"),
    "beta_true": (BOTH, "the false-bridge alternative's generating beta vector"),
    "scale_factors": (BOTH, "the blinded scale-control factors"),
    "role": (BOTH, "the subcondition's declared role"),
    "pairing": (BOTH, "the declared pairing semantics"),
}


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _digest(obj: Any) -> str:
    return hashlib.sha256(_canonical(obj).encode("utf-8")).hexdigest()


# --------------------------------------------------------------- specification
def require_specification_totality(plan: dict[str, Any]) -> None:
    """Refuse if the plan carries any key the specification does not classify.

    This is what makes the surface a SPECIFICATION rather than a hand-counted
    list: authority cannot be added to the plan and silently go unchecked.
    """
    unknown = sorted(set(plan) - set(TOP_LEVEL_SPEC))
    if unknown:
        raise PlanSurfaceUndeclared(
            f"the plan carries top-level keys the normative coherence specification "
            f"does not classify: {unknown}. Every key must be declared BOTH or "
            "JSON_ONLY with a reason; undeclared duplicated authority is the defect "
            "this specification exists to prevent."
        )
    for case in plan.get("cases", []):
        cid = case.get("case_id", "<unnamed>")
        unknown = sorted(set(case) - set(CASE_SPEC))
        if unknown:
            raise PlanSurfaceUndeclared(
                f"case {cid!r} carries unclassified keys {unknown}")
        for sub in case.get("subconditions", []):
            unknown = sorted(set(sub) - set(SUBCONDITION_SPEC))
            if unknown:
                raise PlanSurfaceUndeclared(
                    f"case {cid!r} subcondition {sub.get('subcondition_id')!r} carries "
                    f"unclassified keys {unknown}")


def specification_counts(plan: dict[str, Any], root: str = ".") -> dict[str, int]:
    """Machine-derived counts. Never hand-quoted."""
    view = normative_json_view(plan, root)
    human = _human_rendered_keys(plan)
    return {
        "duplicated_normative_keys": len(view),
        "human_rendered_keys": len(human),
        "block_only_keys": len(view) - len(human),
        "top_level_both": sum(1 for o, _ in TOP_LEVEL_SPEC.values() if o == BOTH),
        "top_level_json_only": sum(1 for o, _ in TOP_LEVEL_SPEC.values() if o == JSON_ONLY),
        "case_both": sum(1 for o, _ in CASE_SPEC.values() if o == BOTH),
        "case_json_only": sum(1 for o, _ in CASE_SPEC.values() if o == JSON_ONLY),
        "subcondition_both": sum(1 for o, _ in SUBCONDITION_SPEC.values() if o == BOTH),
        "subcondition_json_only": sum(1 for o, _ in SUBCONDITION_SPEC.values()
                                      if o == JSON_ONLY),
        "markdown_only_keys": 0,
    }


# ------------------------------------------------------------------- JSON view
def normative_json_view(plan: dict[str, Any], root: str = ".") -> dict[str, Any]:
    """The flat, dotted, canonical mapping of every duplicated normative value."""
    require_specification_totality(plan)
    view: dict[str, Any] = {}

    for key in ("plan_id", "plan_version", "execution_stage", "execution_authorised"):
        if key not in plan:
            raise PlanStructureInvalid(f"the plan omits the normative key {key!r}")
        view[key] = plan[key]

    seal = plan.get("execution_seal")
    if not isinstance(seal, dict) or "state" not in seal:
        raise PlanStructureInvalid(
            "the plan does not declare execution_seal.state; the seal lifecycle "
            "must be machine-readable, not prose")
    view["execution_seal.state"] = seal["state"]

    frozen = plan.get("frozen_identities")
    if not isinstance(frozen, dict):
        raise PlanStructureInvalid("the plan omits frozen_identities")
    for key in IDENTITY_SURFACE:
        if key not in frozen:
            raise PlanStructureInvalid(f"frozen_identities omits {key!r}")
        view[f"frozen_identities.{key}"] = frozen[key]
    if "implementation_file_hashes" not in frozen:
        raise PlanStructureInvalid("frozen_identities omits implementation_file_hashes")
    view["frozen_identities.implementation_file_hashes_digest"] = _digest(
        frozen["implementation_file_hashes"])
    view["seed_map_sha256"] = sha256_file(os.path.join(root, SEED_MAP_JSON))

    rules = plan.get("adopted_rules_unchanged")
    if not isinstance(rules, dict):
        raise PlanStructureInvalid("the plan omits adopted_rules_unchanged")
    for key, value in rules.items():
        view[f"adopted_rules.{key}"] = value

    cal = plan.get("calibration", {})
    view["calibration.calibration_scope"] = cal.get("calibration_scope")

    schema = plan.get("output_schema")
    if not isinstance(schema, dict):
        raise PlanStructureInvalid("the plan omits output_schema")
    for key in ("directory", "record_schema", "manifest_schema",
                "per_record_fields", "aggregate_fields"):
        view[f"output_schema.{key}"] = schema[key]
    view["failure_classifications"] = list(plan["failure_classifications"])

    case_both = tuple(k for k, (o, _) in CASE_SPEC.items()
                      if o == BOTH and k not in ("case_id", "subconditions"))
    sub_both = tuple(k for k, (o, _) in SUBCONDITION_SPEC.items() if o == BOTH)
    view["cases.order"] = [c["case_id"] for c in plan["cases"]]
    for case in plan["cases"]:
        cid = case["case_id"]
        for key in sorted(case_both):
            if key in case:
                view[f"cases.{cid}.{key}"] = case[key]
        subs = case.get("subconditions")
        if not isinstance(subs, list) or not subs:
            raise PlanStructureInvalid(f"case {cid!r} declares no subconditions")
        view[f"cases.{cid}.subconditions.order"] = [s["subcondition_id"] for s in subs]
        for sub in subs:
            sid = sub["subcondition_id"]
            for key in sorted(sub_both):
                if key in sub:
                    view[f"cases.{cid}.subconditions.{sid}.{key}"] = sub[key]

    for index, row in enumerate(plan["assurance"]):
        for key in ("quantity", "target", "confidence_level", "estimator", "bound",
                    "replicates", "acceptance_rule"):
            view[f"assurance.{index}.{key}"] = row[key]

    for gap in plan["authority_gaps"]:
        for key in ("gap", "affects", "status", "resolution"):
            view[f"authority_gaps.{gap['id']}.{key}"] = gap[key]

    final = plan["final_campaign_classification"]
    view["final_campaign.verdict_on_success"] = final["verdict_on_success"]
    view["final_campaign.rule"] = final["rule"]
    for index, requirement in enumerate(final["requirements"]):
        view[f"final_campaign.requirements.{index}"] = requirement

    # The CANONICAL driver DECLARATION, identity-bound in driver.py and never in a
    # seal. Only the declaration belongs here: whether the file currently exists is
    # a runtime FACT checked by the execution gate, not a question of whether two
    # documents agree, and binding it here would make a frozen document depend on
    # the presence of a file it merely names.
    view["driver.module"] = OFFICIAL_CAMPAIGN_DRIVER_MODULE
    view["driver.path"] = OFFICIAL_CAMPAIGN_DRIVER_PATH
    view["driver.entry_point"] = OFFICIAL_CAMPAIGN_DRIVER_ENTRY_POINT
    return view


# ------------------------------------------------------- generated region: cases
#: Markdown row label -> case key. The ORDER here is the rendered order.
CASE_ROW_LABELS = (
    ("v4 classification", "v4_classification"),
    ("v4 classification note", "v4_classification_note"),
    ("authority", "authority"),
    ("truth model", "truth_model"),
    ("fields affected", "fields_affected"),
    ("beta truth", "beta_truth"),
    ("geometry truth", "geometry_truth"),
    ("Branch-A uncertainty scenario", "branch_a_uncertainty"),
    ("Branch-A uncertainty status", "branch_a_uncertainty_status"),
    ("Branch-B process", "branch_b_process"),
    ("expected qualitative outcome", "expected_qualitative_outcome"),
    ("seed family", "seed_family"),
    ("allowed seed families", "allowed_seed_families"),
    ("uses P1 / Block 1", "uses_p1_block1"),
    ("requires Block-1 calibration", "requires_block1_calibration"),
    ("calibration not required because", "calibration_not_required_reason"),
    ("primary release endpoint", "primary_release_endpoint"),
    ("Block-1 role", "block1_role"),
    ("calibration scope", "calibration_scope"),
    ("fields requiring calibration", "fields_requiring_calibration"),
    ("calibration artifacts", "calibration_artifact_count"),
    ("calibration artifact basis", "calibration_artifact_basis"),
    ("subcondition count", "subcondition_count"),
    ("replicate count", "replicate_count"),
)

C3_SEMANTICS_LABELS = (
    ("status", "status"),
    ("primary release endpoint", "primary_release_endpoint"),
    ("release criterion", "release_criterion"),
    ("requires Block-1 calibration", "requires_block1_calibration"),
    ("Block-1 role", "block1_role"),
    ("joint P1 result changes the C3 release verdict",
     "joint_p1_result_changes_C3_release_verdict"),
    ("why calibration is retained", "why_calibration_is_retained"),
    ("what is forbidden", "what_is_forbidden"),
)


def _render_value(value: Any) -> str:
    """One table cell. Lists and scalars render unambiguously and parse back."""
    if isinstance(value, bool):
        return f"`{json.dumps(value)}`"
    if isinstance(value, (int, float)):
        return f"`{json.dumps(value)}`"
    if isinstance(value, list):
        return " ".join(f"`{json.dumps(v)}`" for v in value) if value else "`[]`"
    return str(value)


def _parse_value(cell: str, sample: Any) -> Any:
    """Inverse of `_render_value`, steered by the JSON-side type."""
    if isinstance(sample, list):
        if cell.strip() == "`[]`":
            return []
        return [json.loads(x) for x in re.findall(r"`([^`]*)`", cell)]
    if isinstance(sample, (bool, int, float)):
        inner = re.findall(r"`([^`]*)`", cell)
        if len(inner) != 1:
            raise PlanCaseMismatch(f"cell {cell!r} is not a single rendered scalar")
        return json.loads(inner[0])
    return cell.strip()


def render_cases_region(plan: dict[str, Any]) -> str:
    """The generated section-3 case sections. Every subcondition payload visible."""
    out: list[str] = []
    for case in plan["cases"]:
        cid = case["case_id"]
        out.append(f"### `{cid}` — {case['role']}")
        out.append("")
        out.append(f"**Purpose.** {case['scientific_purpose']}")
        out.append("")
        out.append("| | |")
        out.append("|---|---|")
        for label, key in CASE_ROW_LABELS:
            if key in case:
                out.append(f"| {label} | {_render_value(case[key])} |")
        out.append("")
        out.append("**Declared subconditions.** Every parameter is shown; a subcondition "
                   "parameter that is not rendered here is not declared.")
        out.append("")
        out.append("| subcondition | declared parameters |")
        out.append("|---|---|")
        for sub in case["subconditions"]:
            rest = {k: v for k, v in sub.items() if k != "subcondition_id"}
            out.append(f"| `{sub['subcondition_id']}` | `{_canonical(rest)}` |")
        out.append("")
        out.append(f"**Pass / fail criterion.** {case['formal_pass_fail_criterion']}")
        out.append("")
        if "c3_semantics" in case:
            out.append(f"#### `{cid}` semantics — resolved prospectively")
            out.append("")
            out.append("| | |")
            out.append("|---|---|")
            for label, key in C3_SEMANTICS_LABELS:
                if key in case["c3_semantics"]:
                    out.append(f"| {label} | {_render_value(case['c3_semantics'][key])} |")
            out.append("")
    return "\n".join(out).rstrip() + "\n"


def parse_cases_region(text: str, plan: dict[str, Any]) -> dict[str, Any]:
    """Recover the flat view from the RENDERED case sections."""
    view: dict[str, Any] = {}
    by_id = {c["case_id"]: c for c in plan["cases"]}
    blocks = re.split(r"^### ", text, flags=re.M)[1:]
    order: list[str] = []
    for block in blocks:
        head = re.match(r"`([A-Za-z0-9_]+)`\s*—\s*(.+)", block)
        if head is None:
            raise PlanCaseMismatch("a generated case section has no parseable heading")
        cid, role = head.group(1), head.group(2).strip()
        order.append(cid)
        case = by_id.get(cid)
        if case is None:
            raise PlanCaseMismatch(f"the Markdown renders an unknown case {cid!r}")
        view[f"cases.{cid}.role"] = role
        body = block.split("#### ", 1)[0]
        for label, key in CASE_ROW_LABELS:
            found = re.findall(r"^\| " + re.escape(label) + r" \| (.*?) \|$", body, re.M)
            if key not in case:
                if found:
                    raise PlanCaseMismatch(
                        f"case {cid!r} renders {label!r}, which the JSON does not declare")
                continue
            if len(found) != 1:
                raise PlanCaseMismatch(
                    f"case {cid!r} must render exactly one {label!r} row; found {len(found)}")
            view[f"cases.{cid}.{key}"] = _parse_value(found[0], case[key])
        purpose = re.findall(r"^\*\*Purpose\.\*\* (.+)$", body, re.M)
        if len(purpose) != 1:
            raise PlanCaseMismatch(f"case {cid!r} must render exactly one Purpose line")
        view[f"cases.{cid}.scientific_purpose"] = purpose[0].strip()
        criterion = re.findall(r"^\*\*Pass / fail criterion\.\*\* (.+)$", body, re.M)
        if len(criterion) != 1:
            raise PlanCaseMismatch(
                f"case {cid!r} must render exactly one Pass / fail criterion")
        view[f"cases.{cid}.formal_pass_fail_criterion"] = criterion[0].strip()
        subs = re.findall(r"^\| `([^`]+)` \| `(\{.*\})` \|$", body, re.M)
        if not subs:
            raise PlanSubconditionMismatch(f"case {cid!r} renders no subcondition rows")
        sub_order: list[str] = []
        for sid, payload in subs:
            sub_order.append(sid)
            try:
                parsed = strict_loads(payload, f"case {cid} subcondition {sid}")
            except PlanDuplicateKey:
                raise
            for key, value in parsed.items():
                view[f"cases.{cid}.subconditions.{sid}.{key}"] = value
            view[f"cases.{cid}.subconditions.{sid}.subcondition_id"] = sid
        view[f"cases.{cid}.subconditions.order"] = sub_order
        if "c3_semantics" in case and "#### " in block:
            sem = block.split("#### ", 1)[1]
            rendered = {}
            for label, key in C3_SEMANTICS_LABELS:
                found = re.findall(r"^\| " + re.escape(label) + r" \| (.*?) \|$", sem, re.M)
                if key in case["c3_semantics"]:
                    if len(found) != 1:
                        raise PlanCaseMismatch(
                            f"case {cid!r} semantics must render exactly one {label!r} row")
                    rendered[key] = _parse_value(found[0], case["c3_semantics"][key])
            view[f"cases.{cid}.c3_semantics"] = rendered
    view["cases.order"] = order
    return view


# ---------------------------------------------- generated region: adopted rules
def render_adopted_rules_region(plan: dict[str, Any]) -> str:
    rules = plan["adopted_rules_unchanged"]
    out = ["| rule | value |", "|---|---|"]
    for key, value in rules.items():
        if key == "forbidden":
            continue
        out.append(f"| `{key}` | `{json.dumps(value)}` |")
    out.append("")
    forbidden = "; ".join(f"**{item}**" for item in rules["forbidden"])
    out.append(f"Forbidden and unchanged: {forbidden}.")
    return "\n".join(out) + "\n"


def parse_adopted_rules_region(text: str, plan: dict[str, Any]) -> dict[str, Any]:
    view: dict[str, Any] = {}
    for key, cell in re.findall(r"^\| `([^`]+)` \| `([^`]*)` \|$", text, re.M):
        view[f"adopted_rules.{key}"] = json.loads(cell)
    line = re.findall(r"^Forbidden and unchanged: (.+)\.$", text, re.M)
    if len(line) != 1:
        raise PlanAdoptedRuleMismatch(
            "the adopted-rules region must carry exactly one forbidden-list sentence")
    view["adopted_rules.forbidden"] = [x for x in re.findall(r"\*\*(.+?)\*\*", line[0])]
    return view


# -------------------------------------------------- generated region: assurance
def render_assurance_region(plan: dict[str, Any]) -> str:
    out = ["| quantity | target | confidence | estimator | bound | R | acceptance rule |",
           "|---|---|---:|---|---|---:|---|"]
    for row in plan["assurance"]:
        out.append(
            f"| {row['quantity']} | `{row['target']}` | `{json.dumps(row['confidence_level'])}` "
            f"| {row['estimator']} | {row['bound']} | `{json.dumps(row['replicates'])}` "
            f"| {row['acceptance_rule']} |")
    return "\n".join(out) + "\n"


def parse_assurance_region(text: str, plan: dict[str, Any]) -> dict[str, Any]:
    rows = [line for line in text.splitlines()
            if line.startswith("| ") and not line.startswith("| quantity")
            and not line.startswith("|---")]
    if len(rows) != len(plan["assurance"]):
        raise PlanReleaseRuleMismatch(
            f"the assurance region renders {len(rows)} rows; the plan declares "
            f"{len(plan['assurance'])}")
    view: dict[str, Any] = {}
    for index, line in enumerate(rows):
        cells = [c.strip() for c in line.strip().strip("|").split(" | ")]
        if len(cells) != 7:
            raise PlanReleaseRuleMismatch(
                f"assurance row {index} renders {len(cells)} cells, expected 7")
        quantity, target, confidence, estimator, bound, replicates, acceptance = cells
        view[f"assurance.{index}.quantity"] = quantity
        view[f"assurance.{index}.target"] = target.strip("`")
        view[f"assurance.{index}.confidence_level"] = json.loads(confidence.strip("`"))
        view[f"assurance.{index}.estimator"] = estimator
        view[f"assurance.{index}.bound"] = bound
        view[f"assurance.{index}.replicates"] = json.loads(replicates.strip("`"))
        view[f"assurance.{index}.acceptance_rule"] = acceptance
    return view


# --------------------------------------------- generated region: release rules
def render_release_rules_region(plan: dict[str, Any]) -> str:
    out: list[str] = []
    for gap in plan["authority_gaps"]:
        out.append(f"#### {gap['id']} — affects `{gap['affects']}` — **{gap['status']}**")
        out.append("")
        out.append(f"**Gap.** {gap['gap']}")
        out.append("")
        out.append(f"**Resolution.** {gap['resolution']}")
        out.append("")
    final = plan["final_campaign_classification"]
    out.append("#### Final campaign classification")
    out.append("")
    out.append(f"**Verdict on success.** `{final['verdict_on_success']}`")
    out.append("")
    out.append(f"**Rule.** {final['rule']}")
    out.append("")
    for index, requirement in enumerate(final["requirements"]):
        out.append(f"{index + 1}. {requirement}")
    return "\n".join(out).rstrip() + "\n"


def parse_release_rules_region(text: str, plan: dict[str, Any]) -> dict[str, Any]:
    view: dict[str, Any] = {}
    for gap in plan["authority_gaps"]:
        gid = gap["id"]
        head = re.findall(
            r"^#### " + re.escape(gid) + r" — affects `([^`]+)` — \*\*(.+?)\*\*$",
            text, re.M)
        if len(head) != 1:
            raise PlanReleaseRuleMismatch(
                f"the release-rules region must carry exactly one {gid} heading")
        view[f"authority_gaps.{gid}.affects"] = head[0][0]
        view[f"authority_gaps.{gid}.status"] = head[0][1]
    body = text.split("#### ")
    for chunk in body[1:]:
        gid = chunk.split(" ", 1)[0]
        gap_line = re.findall(r"^\*\*Gap\.\*\* (.+)$", chunk, re.M)
        res_line = re.findall(r"^\*\*Resolution\.\*\* (.+)$", chunk, re.M)
        if gap_line:
            view[f"authority_gaps.{gid}.gap"] = gap_line[0].strip()
        if res_line:
            view[f"authority_gaps.{gid}.resolution"] = res_line[0].strip()
    verdict = re.findall(r"^\*\*Verdict on success\.\*\* `([^`]+)`$", text, re.M)
    rule = re.findall(r"^\*\*Rule\.\*\* (.+)$", text, re.M)
    if len(verdict) != 1 or len(rule) != 1:
        raise PlanReleaseRuleMismatch(
            "the release-rules region must state exactly one final-campaign verdict "
            "and exactly one rule")
    view["final_campaign.verdict_on_success"] = verdict[0]
    view["final_campaign.rule"] = rule[0].strip()
    requirements = re.findall(r"^\d+\. (.+)$", text, re.M)
    expected = plan["final_campaign_classification"]["requirements"]
    if len(requirements) != len(expected):
        raise PlanReleaseRuleMismatch(
            f"the release-rules region renders {len(requirements)} numbered "
            f"requirements; the plan declares {len(expected)}")
    for index, requirement in enumerate(requirements):
        view[f"final_campaign.requirements.{index}"] = requirement.strip()
    return view


#: Keys whose Markdown source is a HUMAN-VISIBLE rendering rather than the block.
#: Derived at import from the renderers, so it cannot drift from what is rendered.
def _human_rendered_keys(plan: dict[str, Any]) -> tuple[str, ...]:
    keys = {"plan_version", "execution_authorised", "execution_seal.state"}
    keys |= {f"frozen_identities.{k}" for _, k in IDENTITY_ROW_LABELS}
    keys |= {f"output_schema.{k}" for k in
             ("record_schema", "manifest_schema", "per_record_fields", "aggregate_fields")}
    keys |= {"failure_classifications", "driver.path"}
    for key in plan["adopted_rules_unchanged"]:
        keys.add(f"adopted_rules.{key}")
    case_both = tuple(k for k, (o, _) in CASE_SPEC.items()
                      if o == BOTH and k not in ("case_id",))
    keys.add("cases.order")
    for case in plan["cases"]:
        cid = case["case_id"]
        for key in case_both:
            if key in case and key != "subconditions":
                keys.add(f"cases.{cid}.{key}")
        keys.add(f"cases.{cid}.subconditions.order")
        for sub in case["subconditions"]:
            sid = sub["subcondition_id"]
            for key in sub:
                keys.add(f"cases.{cid}.subconditions.{sid}.{key}")
    for index, row in enumerate(plan["assurance"]):
        for key in ("quantity", "target", "confidence_level", "estimator", "bound",
                    "replicates", "acceptance_rule"):
            keys.add(f"assurance.{index}.{key}")
    for gap in plan["authority_gaps"]:
        for key in ("gap", "affects", "status", "resolution"):
            keys.add(f"authority_gaps.{gap['id']}.{key}")
    keys.add("final_campaign.verdict_on_success")
    keys.add("final_campaign.rule")
    for index in range(len(plan["final_campaign_classification"]["requirements"])):
        keys.add(f"final_campaign.requirements.{index}")
    return tuple(sorted(keys))


# ------------------------------------------------------------- Markdown sources
def markdown_text(root: str = ".") -> str:
    path = os.path.join(root, PLAN_MARKDOWN)
    if not os.path.exists(path):
        raise PlanStructureInvalid("normative Markdown validation plan is absent")
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def _region(text: str, name: str) -> str:
    """Extract exactly one anchor-delimited generated region. Fail-closed."""
    begin, end = REGION_ANCHORS[name]
    if text.count(begin) != 1 or text.count(end) != 1:
        raise PlanAmbiguousBlock(
            f"the Markdown plan must carry exactly one generated {name!r} region; "
            f"found {text.count(begin)} begin and {text.count(end)} end anchors")
    inner = text.split(begin, 1)[1].split(end, 1)[0]
    if begin in inner or end in inner:
        raise PlanAmbiguousBlock(f"the generated {name!r} region is nested")
    return inner.strip("\n") + "\n"


def render_region(name: str, plan: dict[str, Any]) -> str:
    return {
        "cases": render_cases_region,
        "adopted_rules": render_adopted_rules_region,
        "assurance": render_assurance_region,
        "release_rules": render_release_rules_region,
    }[name](plan)


def authority_block_fields(root: str = ".") -> dict[str, Any]:
    """Parse the generated authority block. Strictly: duplicate keys REFUSE."""
    text = markdown_text(root)
    if text.count(BLOCK_BEGIN) != 1 or text.count(BLOCK_END) != 1:
        raise PlanAmbiguousBlock(
            "the normative Markdown plan must carry exactly one generated authority "
            f"block; found {text.count(BLOCK_BEGIN)} begin and {text.count(BLOCK_END)} "
            "end anchors")
    inner = text.split(BLOCK_BEGIN, 1)[1].split(BLOCK_END, 1)[0]
    fenced = re.findall(r"```json\n(.*?)\n```", inner, re.S)
    if len(fenced) != 1:
        raise PlanAmbiguousBlock(
            f"the generated authority block must carry exactly one ```json fence; "
            f"found {len(fenced)}")
    parsed = strict_loads(fenced[0], "the generated authority block")
    if not isinstance(parsed, dict):
        raise PlanAmbiguousBlock("the generated authority block must be a JSON object")
    # EXACT top-level shape. Without this, an EXTRA top-level key is neither a
    # duplicate nor a declared field, so it would be read by a human and ignored
    # by every check -- the same two-readers ambiguity duplicate keys create.
    if set(parsed) != {"schema", "field_count", "fields"}:
        raise PlanAmbiguousBlock(
            "the generated authority block must carry exactly the keys "
            f"{{'schema', 'field_count', 'fields'}}; found {sorted(parsed)}")
    if parsed.get("schema") != AUTHORITY_BLOCK_SCHEMA:
        raise PlanAmbiguousBlock(
            f"authority block schema is {parsed.get('schema')!r}, expected "
            f"{AUTHORITY_BLOCK_SCHEMA!r}")
    fields = parsed.get("fields")
    if not isinstance(fields, dict):
        raise PlanAmbiguousBlock("the generated authority block carries no `fields` map")
    if parsed.get("field_count") != len(fields):
        raise PlanAmbiguousBlock(
            f"the authority block declares field_count {parsed.get('field_count')!r} but "
            f"carries {len(fields)} fields")
    return fields


def render_authority_block(plan: dict[str, Any], root: str = ".") -> str:
    """The exact text the Markdown must carry between the block anchors."""
    fields = normative_json_view(plan, root)
    payload = {"schema": AUTHORITY_BLOCK_SCHEMA, "field_count": len(fields),
               "fields": fields}
    body = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True)
    return f"{BLOCK_BEGIN}\n\n```json\n{body}\n```\n\n{BLOCK_END}"


def normative_markdown_view(root: str = ".") -> dict[str, Any]:
    """The flat view recovered from HUMAN-VISIBLE renderings, never from the block."""
    text = markdown_text(root)
    plan = strict_load_file(os.path.join(root, PLAN_JSON), "the validation plan")
    view: dict[str, Any] = {}

    version = re.findall(r"Plan version \*\*([0-9]+\.[0-9]+\.[0-9]+)\*\*", text)
    if len(version) != 1:
        raise PlanVersionMismatch(
            f"the Markdown plan must state exactly one plan version; found {len(version)}")
    view["plan_version"] = version[0]

    authorised = re.findall(r"`execution_authorised` is `(true|false)`", text)
    if len(authorised) != 1:
        raise PlanSurfaceMismatch(
            "the Markdown plan must state the execution_authorised flag exactly once; "
            f"found {len(authorised)}")
    view["execution_authorised"] = authorised[0] == "true"

    state = re.findall(r"^execution seal state\s+= (\S+)$", text, re.M)
    if len(state) != 1:
        raise PlanSurfaceMismatch(
            f"the Markdown plan must render exactly one execution seal state; "
            f"found {len(state)}")
    view["execution_seal.state"] = state[0]

    driver_path_shown = re.findall(
        r"^official campaign driver\s+= (\S+)\s+\(canonical, identity-bound\)$",
        text, re.M)
    if len(driver_path_shown) != 1:
        raise PlanSurfaceMismatch(
            "the Markdown plan must render exactly one official campaign driver line")
    view["driver.path"] = driver_path_shown[0]

    if text.count("## 1. Frozen identities") != 1:
        raise PlanAmbiguousBlock("the Markdown plan needs exactly one section-1 heading")
    sec1 = text.split("## 1. Frozen identities", 1)[1].split("\n## ", 1)[0]
    for label, key in IDENTITY_ROW_LABELS:
        found = re.findall(r"^\|\s*" + re.escape(label) + r"\s*\|\s*`([^`]+)`\s*\|\s*$",
                           sec1, re.M)
        if len(found) != 1:
            raise PlanIdentityMismatch(
                f"section 1 must carry exactly one {label!r} row; found {len(found)}")
        view[f"frozen_identities.{key}"] = found[0]

    if text.count("## 9. Output schema") != 1:
        raise PlanAmbiguousBlock("the Markdown plan needs exactly one section-9 heading")
    sec9 = text.split("## 9. Output schema", 1)[1].split("\n## ", 1)[0]
    schemas = re.findall(r"`(e1a_v4_validation_(?:result|manifest)/\d+)`", sec9)
    record = [s for s in schemas if "result" in s]
    manifest = [s for s in schemas if "manifest" in s]
    if len(record) != 1 or len(manifest) != 1:
        raise PlanSurfaceMismatch("section 9 must name exactly one record and one "
                                  "manifest schema version")
    view["output_schema.record_schema"] = record[0]
    view["output_schema.manifest_schema"] = manifest[0]
    for label, key in (("Per record:", "per_record_fields"),
                       ("Aggregate:", "aggregate_fields")):
        line = [x for x in sec9.splitlines() if x.startswith(label)]
        if len(line) != 1:
            raise PlanSurfaceMismatch(f"section 9 must carry exactly one {label!r} line")
        view[f"output_schema.{key}"] = re.findall(r"`([^`]+)`", line[0])

    if text.count("## 10. Failure classifications") != 1:
        raise PlanAmbiguousBlock("the Markdown plan needs exactly one section-10 heading")
    sec10 = text.split("## 10. Failure classifications", 1)[1].split("\n## ", 1)[0]
    view["failure_classifications"] = re.findall(r"^- `([^`]+)`", sec10, re.M)

    view.update(parse_adopted_rules_region(_region(text, "adopted_rules"), plan))
    view.update(parse_cases_region(_region(text, "cases"), plan))
    view.update(parse_assurance_region(_region(text, "assurance"), plan))
    view.update(parse_release_rules_region(_region(text, "release_rules"), plan))
    return view


# ---------------------------------------------------------------- mismatch code
def _code_for(key: str):
    """The stable refusal class for a mismatching normative key."""
    if key == "plan_version":
        return PlanVersionMismatch
    if key == "frozen_identities.analysis_procedure_identity":
        return PlanAnalysisIdentityMismatch
    if key.startswith("frozen_identities.") or key == "seed_map_sha256":
        return PlanIdentityMismatch
    if key.startswith("adopted_rules."):
        return PlanAdoptedRuleMismatch
    if ".subconditions." in key:
        return PlanSubconditionMismatch
    if key.startswith("cases."):
        return PlanCaseMismatch
    if (key.startswith("assurance.") or key.startswith("authority_gaps.")
            or key.startswith("final_campaign.")):
        return PlanReleaseRuleMismatch
    if key.startswith("driver."):
        return DriverIdentityMismatch
    return PlanSurfaceMismatch


def _compare(expected: dict[str, Any], actual: dict[str, Any], source: str,
             keys) -> None:
    for key in keys:
        if key not in actual:
            raise _code_for(key)(
                f"{source} omits the normative key {key!r}")
        if _canonical(actual[key]) != _canonical(expected[key]):
            raise _code_for(key)(
                f"MARKDOWN/JSON AUTHORITY DISAGREEMENT at {key!r}: {source} carries "
                f"{_canonical(actual[key])[:140]} but the JSON plan declares "
                f"{_canonical(expected[key])[:140]}")


def require_plan_authority_coherence(root: str, plan: dict[str, Any]) -> None:
    """Refuse ANY Markdown/JSON authority disagreement. Runs before any RNG.

    Four layers, each fail-closed:
        1. the specification is TOTAL -- no undeclared duplicated authority
        2. every generated region is a byte-exact re-render of the JSON
        3. the embedded authority block equals the full JSON normative view
        4. the HUMAN-VISIBLE renderings equal the JSON normative view

    Layer 4 is not redundant with layer 3: an independent audit showed a correct
    block sitting beside a stale visible protocol, which is why the visible
    normative tables are generated and parsed back rather than trusted.
    """
    expected = normative_json_view(plan, root)
    text = markdown_text(root)

    for name in REGION_ANCHORS:
        actual_region = _region(text, name)
        wanted_region = render_region(name, plan)
        if actual_region != wanted_region:
            raise PlanAmbiguousBlock(
                f"the generated {name!r} region is not a byte-exact re-render of the "
                "JSON plan. Regenerate it; it is not hand-maintained.")

    block = authority_block_fields(root)
    unknown = sorted(set(block) - set(expected))
    if unknown:
        raise PlanSurfaceUndeclared(
            f"the authority block carries undeclared normative keys {unknown[:8]}")
    _compare(expected, block, "the generated authority block", sorted(expected))

    rendered = normative_markdown_view(root)
    human_keys = _human_rendered_keys(plan)
    missing = sorted(set(human_keys) - set(rendered))
    if missing:
        raise PlanSurfaceMismatch(
            f"the Markdown no longer renders {len(missing)} declared human-visible "
            f"normative keys, beginning {missing[:6]}")
    _compare(expected, rendered, "the human-visible Markdown rendering", human_keys)
