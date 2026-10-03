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
from ..numerics import Refusal
from . import PLAN_JSON, PLAN_MARKDOWN, SEED_MAP_JSON
from .driver import (
    OFFICIAL_CAMPAIGN_DRIVER_ENTRY_POINT, OFFICIAL_CAMPAIGN_DRIVER_MODULE,
    OFFICIAL_CAMPAIGN_DRIVER_PATH, driver_state,
)
from .refusals import (
    DriverIdentityMismatch, PlanAdoptedRuleMismatch, PlanAmbiguousBlock,
    PlanAnalysisIdentityMismatch, PlanCaseMismatch, PlanDerivedValueMismatch,
    PlanDuplicateKey, PlanGeneratingModelMismatch, PlanIdentityMismatch,
    PlanReleaseRuleMismatch, PlanSectionUnregistered, PlanStructureInvalid,
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
    "release_authority": ("<!-- BEGIN GENERATED RELEASE AUTHORITY -- do not hand-edit -->",
                          "<!-- END GENERATED RELEASE AUTHORITY -->"),
    "generating_model": ("<!-- BEGIN GENERATED GENERATING MODEL -- do not hand-edit -->",
                         "<!-- END GENERATED GENERATING MODEL -->"),
    "controls": ("<!-- BEGIN GENERATED CONTROLS -- do not hand-edit -->",
                 "<!-- END GENERATED CONTROLS -->"),
}

BOTH = "BOTH"
JSON_ONLY = "JSON_ONLY"
#: Rendered in the Markdown but NOT an independent source of truth: mechanically
#: derived from JSON primitives and checked by RECOMPUTATION, so it can never
#: become a second authority that silently disagrees with the primitives.
DERIVED = "DERIVED_RENDERING"

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
    "assurance": (BOTH, "the release criteria, rendered as the generated section-6 "
                        "tables: the human summary AND the structured release binding "
                        "whose every field is bound to frozen authority"),
    "release_authority": (BOTH, "the CASE RELEASE SPECIFICATION layer -- the frozen "
                                "complete-pass event, the IMPLIED_STRONGER relationships "
                                "and the mandatory contract diagnostics. Section 6a "
                                "renders it; release-bearing authority may never be "
                                "JSON-only"),
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
    "generating_model": (BOTH, "section 4 visibly renders its scientific settings -- dt, "
                               "T_total, n_samples and every field's stiffness, temperature, "
                               "orientation, reference flag and beta_true. Every descendant "
                               "primitive is classified individually in "
                               "GENERATING_MODEL_SPEC; no subtree shortcut may hide a "
                               "duplicated descendant"),
    "complete_pass_denominator": (JSON_ONLY, "denominator narrative; the operative rule "
                                             "is carried by the assurance rows"),
    "controls": (BOTH, "section 8 renders the control-to-case mapping as a table; which "
                       "control belongs to which case is execution authority, not decoration"),
    "classification_rule": (JSON_ONLY, "prose restatement of final_campaign_classification"),
    "no_post_outcome_tuning": (JSON_ONLY, "prohibition narrative; changes nothing executable"),
    "execution_command": (JSON_ONLY, "operational command string, not a scientific rule"),
    "preflight_command": (JSON_ONLY, "operational command string, not a scientific rule"),
    "preflight_checks_before_rng": (JSON_ONLY, "documentation of the checks; the checks "
                                               "themselves are code, bound by module hashes"),
    "author_dispositions": (JSON_ONLY, "disposition narrative; the operative content is "
                                       "authority_gaps and the assurance rows"),
    "superseded_package": (JSON_ONLY, "supersession record; historical, not executable"),
    "size_validation_semantics": (DERIVED, "section 12a renders the derived size "
                                           "boundaries. They are recomputed by "
                                           "`size_boundary(R, nominal)` from primitives the "
                                           "plan already carries, so they are checked by "
                                           "RECOMPUTATION rather than trusted as a second "
                                           "independent source of truth"),
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

#: Classification of EVERY primitive beneath `generating_model`. No subtree-level
#: shortcut is permitted: an auditor found that classifying the whole object
#: JSON_ONLY hid dt, n_samples and every field's stiffness, temperature,
#: orientation, reference flag and beta_true, all of which section 4 renders.
GENERATING_MODEL_SPEC = {
    "branch_b.process": (BOTH, "the declared observation process"),
    "branch_b.transition": (BOTH, "the exact modal transition law"),
    "branch_b.phi": (BOTH, "the modal decay definition"),
    "branch_b.initialisation": (BOTH, "stationary initialisation and burn-in"),
    "branch_b.superseded": (BOTH, "the FORBIDDEN v3 convention, rendered as a warning"),
    "branch_b.dt_s": (BOTH, "the sampling interval, seconds -- PRIMITIVE"),
    "branch_b.T_total_s": (BOTH, "the record length, seconds -- PRIMITIVE"),
    "branch_b.n_samples": (DERIVED, "DERIVED: e1a_v4.world.World.n_samples is "
                                    "int(round(T_total / dt)). Checked by recomputation "
                                    "from the two primitives, never trusted as a third "
                                    "independent authority"),
    "branch_a.model": (BOTH, "the Branch-A measurement model"),
    "branch_a.common_mode": (BOTH, "one draw per experiment, shared across fields"),
    "branch_a.per_mode_stiffness": (BOTH, "independent per mode"),
    "branch_a.orientation": (BOTH, "trap-axis psi"),
    "branch_a.thermometry": (BOTH, "temperature measurement"),
    "branch_a.independence": (BOTH, "Branch-A randomness is exogenous"),
    "branch_a.measured_input_domain": (
        BOTH, "the approved admissible domain of the MEASURED primitives eta and a "
              "(disposition G6), restated from the frozen design contract. It decides "
              "which Branch-A field constructions are admissible at all, so it is "
              "normative and is rendered in section 4"),
    "truth_visibility": (BOTH, "what the analysis layer may see"),
    "per_field.id": (BOTH, "field identifier"),
    "per_field.k_uN_per_m": (BOTH, "modal stiffnesses, micronewton per metre -- defines H"),
    "per_field.T_K": (BOTH, "temperature, kelvin -- defines the stationary covariance"),
    "per_field.rot_deg": (BOTH, "trap-axis orientation, degrees -- defines the rotation"),
    "per_field.reference": (BOTH, "whether this is the P2 reference field"),
    "per_field.beta_true": (BOTH, "the generating beta for this field"),
    "per_field.tau_rule": (BOTH, "the relaxation-time rule"),
}

#: Descendants of `generating_model` that are UPSTREAM contract authority. The
#: plan restates them; it may not contradict the frozen design contract.
CONTRACT_MIRRORED_FIELD_KEYS = ("id", "k_uN_per_m", "T_K", "rot_deg", "reference")

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
    "c3_semantics": (BOTH, "C3's release-versus-diagnostic resolution and its resolved PER-FIELD size structure"),
    "c4_semantics": (BOTH, "C4's resolved PER-FIELD size structure"),
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
    """Machine-derived counts. Never hand-quoted, and never asserted.

    `markdown_only_keys` and `unclassified_normative_candidates` are MEASURED, not
    declared: claiming "0 Markdown-only keys" without measuring is precisely the
    kind of unearned completeness claim that let the generating model sit outside
    the surface while the package reported full coherence.
    """
    view = normative_json_view(plan, root)
    human = _human_rendered_keys(plan)
    try:
        rendered = set(normative_markdown_view(root))
    except Refusal:
        rendered = set()
    markdown_only = sorted(rendered - set(view))
    present = markdown_sections(markdown_text(root))
    unregistered = [h for h in present if h not in SECTION_REGISTRY]
    unclassified = (len(unregistered)
                    + len(set(plan) - set(TOP_LEVEL_SPEC))
                    + sum(len(set(c) - set(CASE_SPEC)) for c in plan["cases"])
                    + sum(len(set(x) - set(SUBCONDITION_SPEC))
                          for c in plan["cases"] for x in c["subconditions"]))
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
        "markdown_only_keys": len(markdown_only),
        "generating_model_primitives": len(GENERATING_MODEL_SPEC),
        "generating_model_both": sum(1 for o, _ in GENERATING_MODEL_SPEC.values()
                                     if o == BOTH),
        "derived_rendering_keys": sum(1 for o, _ in GENERATING_MODEL_SPEC.values()
                                      if o == DERIVED)
                                 + sum(1 for o, _ in TOP_LEVEL_SPEC.values()
                                       if o == DERIVED),
        "registered_normative_sections": len(SECTION_REGISTRY),
        "generated_sections": sum(1 for o, _ in SECTION_REGISTRY.values()
                                  if o == GENERATED),
        "parsed_sections": sum(1 for o, _ in SECTION_REGISTRY.values() if o == PARSED),
        "derived_sections": sum(1 for o, _ in SECTION_REGISTRY.values()
                                if o == DERIVED_SECTION),
        "non_normative_sections": sum(1 for o, _ in SECTION_REGISTRY.values()
                                      if o == NON_NORMATIVE),
        "unregistered_sections": len(unregistered),
        "unclassified_normative_candidates": unclassified,
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
        for key in ASSURANCE_KEYS:
            view[f"assurance.{index}.{key}"] = row[key]

    release = plan["release_authority"]
    view["release_authority.complete_pass_event"] = release["complete_pass_event"]
    for key in RELEASE_AUTHORITY_PROSE:
        view[f"release_authority.{key}"] = release[key]
    for cid, block in release["implied_stronger"].items():
        for key in sorted(block):
            view[f"release_authority.implied_stronger.{cid}.{key}"] = block[key]
    for row in release["mandatory_diagnostics"]:
        for key in MANDATORY_DIAGNOSTIC_KEYS:
            view[f"release_authority.mandatory_diagnostics."
                 f"{row['diagnostic_id']}.{key}"] = row[key]

    for gap in plan["authority_gaps"]:
        for key in ("gap", "affects", "status", "resolution"):
            view[f"authority_gaps.{gap['id']}.{key}"] = gap[key]

    final = plan["final_campaign_classification"]
    view["final_campaign.verdict_on_success"] = final["verdict_on_success"]
    view["final_campaign.rule"] = final["rule"]
    for index, requirement in enumerate(final["requirements"]):
        view[f"final_campaign.requirements.{index}"] = requirement

    for key, value in canonical_generating_model(plan).items():
        view[f"generating_model.{key}"] = value
    for index, row in enumerate(plan["controls"]):
        for key in ("control", "purpose", "case"):
            view[f"controls.{index}.{key}"] = row[key]

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

#: Per-case keys carrying a resolved-semantics block. Each is rendered as its own
#: visible table and parsed back, so an unlabelled member below cannot survive: the
#: recovered dict would differ from the JSON and the comparison refuses.
SEMANTICS_CASE_KEYS = ("c3_semantics", "c4_semantics")

SEMANTICS_LABELS = (
    ("status", "status"),
    ("primary release endpoint", "primary_release_endpoint"),
    ("release criterion", "release_criterion"),
    ("requires Block-1 calibration", "requires_block1_calibration"),
    ("Block-1 role", "block1_role"),
    ("joint P1 result changes the C3 release verdict",
     "joint_p1_result_changes_C3_release_verdict"),
    ("why calibration is retained", "why_calibration_is_retained"),
    ("field structure", "field_structure"),
    ("within-replicate field reduction", "field_reduction"),
    ("pooling", "pooling"),
    ("field structure status", "field_structure_status"),
    ("field structure rule", "field_structure_rule"),
    ("case-level rule", "case_level_rule"),
    ("what is forbidden", "what_is_forbidden"),
    # ---- the G5 structured-refusal amendment --------------------------------
    ("structured-refusal status", "structured_refusal_status"),
    ("primary endpoint can be undefined", "undefined_primary_endpoint_possible"),
    ("why the primary endpoint can be undefined",
     "undefined_primary_endpoint_reason"),
    ("undefined primary endpoint is encoded as",
     "undefined_primary_endpoint_encoding"),
    ("a structured refusal is a statistical rejection",
     "refusal_is_statistical_rejection"),
    ("a structured refusal is a statistical non-rejection",
     "refusal_is_statistical_non_rejection"),
    ("primary denominator under refusal", "primary_denominator_under_refusal"),
    ("primary verdict on any structured refusal",
     "primary_verdict_on_structured_refusal"),
    ("release requires", "release_requires"),
    ("campaign failure classification when not evaluable",
     "campaign_failure_classification_when_not_evaluable"),
    ("tolerated structured-refusal fraction",
     "tolerated_structured_refusal_fraction"),
    ("survivor-conditioned rate role", "survivor_conditioned_rate_role"),
    ("required terminal counts", "required_terminal_counts"),
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
        for semantics_key in SEMANTICS_CASE_KEYS:
            if semantics_key in case:
                out.append(f"#### `{cid}` semantics — resolved prospectively")
                out.append("")
                out.append("| | |")
                out.append("|---|---|")
                for label, key in SEMANTICS_LABELS:
                    if key in case[semantics_key]:
                        out.append(
                            f"| {label} | {_render_value(case[semantics_key][key])} |")
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
        for semantics_key in SEMANTICS_CASE_KEYS:
            if semantics_key in case and "#### " in block:
                sem = block.split("#### ", 1)[1]
                rendered = {}
                for label, key in SEMANTICS_LABELS:
                    found = re.findall(r"^\| " + re.escape(label) + r" \| (.*?) \|$",
                                       sem, re.M)
                    if key in case[semantics_key]:
                        if len(found) != 1:
                            raise PlanCaseMismatch(
                                f"case {cid!r} semantics must render exactly one "
                                f"{label!r} row")
                        rendered[key] = _parse_value(found[0], case[semantics_key][key])
                view[f"cases.{cid}.{semantics_key}"] = rendered
    view["cases.order"] = order
    return view


# ------------------------------------------ generated region: generating model
#: Rendered Branch-B row label -> JSON key, plus the unit column. The unit is a
#: separate cell and the VALUE is rendered as exact JSON, so "0.00012 s",
#: "1.2e-4 s" and "0.12 ms" can never be confused: one canonical representation
#: is rendered and parsed, and equality is exact. No tolerance is applied, so
#: 0.00012 -> 0.00013 always refuses.
BRANCH_B_ROWS = (
    ("process", "process", ""),
    ("transition", "transition", ""),
    ("phi", "phi", ""),
    ("initialisation", "initialisation", ""),
    ("superseded convention", "superseded", ""),
    ("dt", "dt_s", "s"),
    ("T_total", "T_total_s", "s"),
)

BRANCH_A_ROWS = (
    ("model", "model"),
    ("common mode", "common_mode"),
    ("per mode stiffness", "per_mode_stiffness"),
    ("orientation", "orientation"),
    ("thermometry", "thermometry"),
    ("independence", "independence"),
    ("measured input domain", "measured_input_domain"),
)

FIELD_ROWS = (
    ("k (uN/m)", "k_uN_per_m"),
    ("T (K)", "T_K"),
    ("rotation (deg)", "rot_deg"),
    ("reference", "reference"),
    ("beta_true", "beta_true"),
)


def derived_n_samples(branch_b: dict[str, Any]) -> int:
    """n_samples is DERIVED, exactly as `e1a_v4.world.World.n_samples` derives it."""
    return int(round(branch_b["T_total_s"] / branch_b["dt_s"]))


def canonical_generating_model(plan: dict[str, Any]) -> dict[str, Any]:
    """The canonical generating-model tree, from the JSON plan."""
    gm = plan.get("generating_model")
    if not isinstance(gm, dict):
        raise PlanStructureInvalid("the plan omits generating_model")
    unknown = sorted(set(gm) - {"branch_b", "branch_a", "truth_visibility", "per_field"})
    if unknown:
        raise PlanSurfaceUndeclared(
            f"generating_model carries unclassified sections {unknown}")
    out: dict[str, Any] = {}
    for section, rows in (("branch_b", [k for _, k, _ in BRANCH_B_ROWS]),
                          ("branch_a", [k for _, k in BRANCH_A_ROWS])):
        body = gm.get(section)
        if not isinstance(body, dict):
            raise PlanStructureInvalid(f"generating_model.{section} is missing")
        declared = set(rows) | ({"n_samples"} if section == "branch_b" else set())
        missing = sorted(declared - set(body))
        extra = sorted(set(body) - declared)
        if missing or extra:
            raise PlanSurfaceUndeclared(
                f"generating_model.{section}: unclassified {extra}, missing {missing}")
        for key in rows:
            out[f"{section}.{key}"] = body[key]
    out["branch_b.n_samples"] = gm["branch_b"]["n_samples"]
    out["truth_visibility"] = gm["truth_visibility"]
    fields = gm.get("per_field")
    if not isinstance(fields, list) or not fields:
        raise PlanStructureInvalid("generating_model.per_field is missing or empty")
    declared_field_keys = {k.split(".", 1)[1] for k in GENERATING_MODEL_SPEC
                           if k.startswith("per_field.")}
    out["per_field.order"] = [f["id"] for f in fields]
    for field in fields:
        extra = sorted(set(field) - declared_field_keys)
        if extra:
            raise PlanSurfaceUndeclared(
                f"field {field.get('id')!r} carries unclassified generating keys {extra}")
        for key in sorted(declared_field_keys - {"id"}):
            if key not in field:
                raise PlanStructureInvalid(
                    f"field {field.get('id')!r} omits generating key {key!r}")
            out[f"per_field.{field['id']}.{key}"] = field[key]
    return out


def render_generating_model_region(plan: dict[str, Any]) -> str:
    """Section 4's NORMATIVE tables, rendered from the canonical view.

    Explanatory prose stays OUTSIDE this region: only declared values participate
    in equality checking, and every value that defines the synthetic experiment is
    inside it.
    """
    gm = plan["generating_model"]
    view = canonical_generating_model(plan)
    out = ["**Branch B — the declared observation process.**", "",
           "| setting | value | unit |", "|---|---|---|"]
    for label, key, unit in BRANCH_B_ROWS:
        out.append(f"| {label} | `{json.dumps(view[f'branch_b.{key}'])}` | {unit} |")
    out.append(f"| n_samples *(derived: T_total / dt)* | "
               f"`{json.dumps(view['branch_b.n_samples'])}` | samples |")
    out += ["", "**Branch A — the measurement-error model.**", "",
            "| setting | value |", "|---|---|"]
    for label, key in BRANCH_A_ROWS:
        out.append(f"| {label} | `{json.dumps(view[f'branch_a.{key}'])}` |")
    out += ["", f"**Truth visibility.** `{json.dumps(view['truth_visibility'])}`", "",
            "**Per-field generating parameters.** Every declared parameter is shown; a "
            "parameter not rendered here is not declared.", "",
            "| field | " + " | ".join(label for label, _ in FIELD_ROWS) + " | tau rule |",
            "|---|" + "---|" * (len(FIELD_ROWS) + 1)]
    for field in gm["per_field"]:
        cells = " | ".join(f"`{json.dumps(field[key])}`" for _, key in FIELD_ROWS)
        out.append(f"| `{field['id']}` | {cells} | `{json.dumps(field['tau_rule'])}` |")
    return "\n".join(out) + "\n"


def canonical_generating_model_from_markdown(text: str,
                                             plan: dict[str, Any]) -> dict[str, Any]:
    """The same canonical tree, recovered from the RENDERED section-4 region."""
    out: dict[str, Any] = {}
    for label, key, _ in BRANCH_B_ROWS:
        found = re.findall(r"^\| " + re.escape(label) + r" \| `(.*?)` \| .*\|$", text, re.M)
        if len(found) != 1:
            raise PlanGeneratingModelMismatch(
                f"section 4 must render exactly one {label!r} row; found {len(found)}")
        out[f"branch_b.{key}"] = json.loads(found[0])
    found = re.findall(r"^\| n_samples \*\(derived: T_total / dt\)\* \| `(.*?)` \| .*\|$",
                       text, re.M)
    if len(found) != 1:
        raise PlanGeneratingModelMismatch("section 4 must render exactly one n_samples row")
    out["branch_b.n_samples"] = json.loads(found[0])
    for label, key in BRANCH_A_ROWS:
        found = re.findall(r"^\| " + re.escape(label) + r" \| `(.*?)` \|$", text, re.M)
        if len(found) != 1:
            raise PlanGeneratingModelMismatch(
                f"section 4 must render exactly one Branch-A {label!r} row")
        out[f"branch_a.{key}"] = json.loads(found[0])
    found = re.findall(r"^\*\*Truth visibility\.\*\* `(.*?)`$", text, re.M)
    if len(found) != 1:
        raise PlanGeneratingModelMismatch("section 4 must render one truth-visibility line")
    out["truth_visibility"] = json.loads(found[0])
    rows = re.findall(r"^\| `([A-Za-z0-9_]+)` \| (`.*`) \|$", text, re.M)
    if not rows:
        raise PlanGeneratingModelMismatch("section 4 renders no per-field rows")
    out["per_field.order"] = [fid for fid, _ in rows]
    for fid, cells in rows:
        values = re.findall(r"`([^`]*)`", cells)
        if len(values) != len(FIELD_ROWS) + 1:
            raise PlanGeneratingModelMismatch(
                f"field {fid!r} renders {len(values)} cells, expected {len(FIELD_ROWS) + 1}")
        for (_, key), raw in zip(FIELD_ROWS, values):
            out[f"per_field.{fid}.{key}"] = json.loads(raw)
        out[f"per_field.{fid}.tau_rule"] = json.loads(values[-1])
    return out


def require_generating_model_coherence(root: str, plan: dict[str, Any],
                                       text: str) -> None:
    """Markdown section 4 must equal the JSON generating model, path by path.

    Also checks DERIVED n_samples by recomputation.  The separate
    contract_plan layer checks the superior frozen contract after both plan
    representations have been shown to agree.
    """
    expected = canonical_generating_model(plan)
    actual = canonical_generating_model_from_markdown(_region(text, "generating_model"),
                                                      plan)
    for key in sorted(expected):
        if key not in actual:
            raise PlanGeneratingModelMismatch(
                f"section 4 omits the generating-model path {key!r}")
        if _canonical(actual[key]) != _canonical(expected[key]):
            raise PlanGeneratingModelMismatch(
                f"GENERATING-MODEL DISAGREEMENT at {key!r}: section 4 renders "
                f"{_canonical(actual[key])[:120]} but the JSON plan declares "
                f"{_canonical(expected[key])[:120]}")
    extra = sorted(set(actual) - set(expected))
    if extra:
        raise PlanSurfaceUndeclared(f"section 4 renders undeclared paths {extra}")

    # DERIVED, not a third authority: recomputed from the two primitives
    derived = derived_n_samples(plan["generating_model"]["branch_b"])
    if expected["branch_b.n_samples"] != derived:
        raise PlanDerivedValueMismatch(
            f"n_samples is DERIVED as int(round(T_total / dt)) = {derived}, but the "
            f"plan declares {expected['branch_b.n_samples']}. It is not an "
            "independent input and may not disagree with its primitives.")

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
#: EVERY assurance key, in rendered order. Derived once so the renderer, the
#: parser and the JSON view cannot drift apart.
ASSURANCE_SUMMARY_KEYS = ("case_id", "quantity", "target", "confidence_level",
                          "estimator", "bound", "replicates", "acceptance_rule")
ASSURANCE_BINDING_KEYS = ("case_id", "unit", "method", "sided", "bound_direction",
                          "target_value", "comparison", "integer_boundary",
                          "boundary_derivation", "pooling")
ASSURANCE_KEYS = tuple(dict.fromkeys(
    ASSURANCE_SUMMARY_KEYS + ASSURANCE_BINDING_KEYS + ("assurance_at_design_target",)))

RELEASE_AUTHORITY_PROSE = ("status", "authority_rule", "implementation",
                           "absent_diagnostic_is")
MANDATORY_DIAGNOSTIC_KEYS = ("diagnostic_id", "case_id", "authority_source",
                             "authority_path", "requirement", "aggregate_key",
                             "required_keys")


def _cell(value: Any) -> str:
    """One table cell. `None` renders as an explicit dash, never as blank."""
    if value is None:
        return "\u2014"
    if isinstance(value, str):
        return value
    return f"`{json.dumps(value)}`"


def _uncell(cell: str, key: str, sample: Any) -> Any:
    if cell == "\u2014":
        return None
    if isinstance(sample, str) or (sample is None and not cell.startswith("`")):
        return cell
    return json.loads(cell.strip("`"))


def render_assurance_region(plan: dict[str, Any]) -> str:
    """Two tables: the human summary, then the structured release binding.

    The second table exists because an audit showed that a release rule carried
    only as prose -- "R = 300", ">= 279/300" -- cannot be bound to frozen
    authority without parsing sentences. Every field below is machine-readable and
    every one is checked against the design contract before the first draw.
    """
    out = ["| case | quantity | target | confidence | estimator | bound | R "
           "| acceptance rule |",
           "|---|---|---|---:|---|---|---:|---|"]
    for row in plan["assurance"]:
        out.append("| " + " | ".join(
            _cell(row[k]) for k in ASSURANCE_SUMMARY_KEYS) + " |")
    out.append("")
    out.append("Structured release binding \u2014 every field below is bound to frozen "
               "authority by `e1a_v4.validation.release_authority`:")
    out.append("")
    out.append("| case | unit | method | sided | direction | target | cmp "
               "| boundary | derivation | pooling |")
    out.append("|---|---|---|---|---|---|---|---:|---|---|")
    for row in plan["assurance"]:
        out.append("| " + " | ".join(
            _cell(row[k]) for k in ASSURANCE_BINDING_KEYS) + " |")
    extra = [r for r in plan["assurance"] if r["assurance_at_design_target"] is not None]
    if extra:
        out.append("")
        for row in extra:
            out.append(f"- Assurance at design target \u2014 `{row['case_id']}`: "
                       f"{row['assurance_at_design_target']}")
    return "\n".join(out) + "\n"


def parse_assurance_region(text: str, plan: dict[str, Any]) -> dict[str, Any]:
    tables = _split_tables(text, 2, "assurance", PlanReleaseRuleMismatch)
    view: dict[str, Any] = {}
    for keys, rows in zip((ASSURANCE_SUMMARY_KEYS, ASSURANCE_BINDING_KEYS), tables):
        if len(rows) != len(plan["assurance"]):
            raise PlanReleaseRuleMismatch(
                f"an assurance table renders {len(rows)} rows; the plan declares "
                f"{len(plan['assurance'])}")
        for index, cells in enumerate(rows):
            if len(cells) != len(keys):
                raise PlanReleaseRuleMismatch(
                    f"assurance row {index} renders {len(cells)} cells, expected "
                    f"{len(keys)}")
            for key, cell in zip(keys, cells):
                view[f"assurance.{index}.{key}"] = _uncell(
                    cell, key, plan["assurance"][index][key])
    shown = dict(re.findall(
        r"^- Assurance at design target \u2014 `([^`]+)`: (.+)$", text, re.M))
    for index, row in enumerate(plan["assurance"]):
        view[f"assurance.{index}.assurance_at_design_target"] = shown.get(row["case_id"])
    return view


def _split_tables(text: str, expected: int, what: str, refusal) -> list[list[list[str]]]:
    """Split a region into its Markdown tables, as lists of stripped cells."""
    tables: list[list[list[str]]] = []
    current: list[list[str]] | None = None
    for line in text.splitlines():
        if line.startswith("|---") or line.startswith("|:-"):
            continue
        if line.startswith("| "):
            cells = [c.strip() for c in line.strip().strip("|").split(" | ")]
            if current is None:
                current = []
                tables.append(current)
                continue          # the header row
            current.append(cells)
        else:
            current = None
    if len(tables) != expected:
        raise refusal(f"the {what} region renders {len(tables)} tables, expected "
                      f"{expected}")
    return tables


# ------------------------------------- generated region: the release authority
def render_release_authority_region(plan: dict[str, Any]) -> str:
    """Section 6a. The CASE RELEASE SPECIFICATION, visible to a human reader."""
    release = plan["release_authority"]
    out = [f"**Status.** {release['status']}", "",
           f"**Authority rule.** {release['authority_rule']}", "",
           f"**Implementation.** `{release['implementation']}`", "",
           f"**Complete-pass event.** {release['complete_pass_event']}", "",
           f"**Absent mandatory diagnostic.** `{release['absent_diagnostic_is']}`", ""]
    for cid, block in release["implied_stronger"].items():
        out.append(f"#### IMPLIED_STRONGER \u2014 {cid}")
        out.append("")
        for key in sorted(block):
            out.append(f"- `{key}`: {_cell(block[key])}")
        out.append("")
    out.append("#### Mandatory contract diagnostics")
    out.append("")
    out.append("| diagnostic | case | authority | requirement | aggregate key "
               "| required keys |")
    out.append("|---|---|---|---|---|---|")
    for row in release["mandatory_diagnostics"]:
        keys = ", ".join(f"`{k}`" for k in row["required_keys"]) or "\u2014"
        out.append(f"| `{row['diagnostic_id']}` | `{row['case_id']}` | "
                   f"`{row['authority_source']}` `{row['authority_path']}` | "
                   f"{row['requirement']} | `{row['aggregate_key']}` | {keys} |")
    return "\n".join(out).rstrip() + "\n"


def parse_release_authority_region(text: str, plan: dict[str, Any]) -> dict[str, Any]:
    view: dict[str, Any] = {}
    labels = (("Status", "status"), ("Authority rule", "authority_rule"),
              ("Implementation", "implementation"),
              ("Complete-pass event", "complete_pass_event"),
              ("Absent mandatory diagnostic", "absent_diagnostic_is"))
    for label, key in labels:
        found = re.findall(r"^\*\*" + re.escape(label) + r"\.\*\* (.+)$", text, re.M)
        if len(found) != 1:
            raise PlanReleaseRuleMismatch(
                f"section 6a must state exactly one {label!r} line; found {len(found)}")
        value = found[0].strip()
        if key in ("implementation", "absent_diagnostic_is"):
            value = value.strip("`")
        view[f"release_authority.{key}"] = value
    for cid, block in plan["release_authority"]["implied_stronger"].items():
        head = f"#### IMPLIED_STRONGER \u2014 {cid}"
        if text.count(head) != 1:
            raise PlanReleaseRuleMismatch(
                f"section 6a must carry exactly one {cid} IMPLIED_STRONGER block")
        chunk = text.split(head, 1)[1].split("\n#### ", 1)[0]
        shown = re.findall(r"^- `([^`]+)`: (.+)$", chunk, re.M)
        if len(shown) != len(block):
            raise PlanReleaseRuleMismatch(
                f"the {cid} IMPLIED_STRONGER block renders {len(shown)} fields; the "
                f"plan declares {len(block)}")
        for key, cell in shown:
            if key not in block:
                raise PlanReleaseRuleMismatch(
                    f"section 6a renders an undeclared {cid} field {key!r}")
            view[f"release_authority.implied_stronger.{cid}.{key}"] = _uncell(
                cell.strip(), key, block[key])
    rows = _split_tables(text.split("#### Mandatory contract diagnostics", 1)[-1],
                         1, "mandatory-diagnostic", PlanReleaseRuleMismatch)[0]
    declared = plan["release_authority"]["mandatory_diagnostics"]
    if len(rows) != len(declared):
        raise PlanReleaseRuleMismatch(
            f"section 6a renders {len(rows)} mandatory diagnostics; the plan declares "
            f"{len(declared)}")
    for index, cells in enumerate(rows):
        if len(cells) != 6:
            raise PlanReleaseRuleMismatch(
                f"mandatory-diagnostic row {index} renders {len(cells)} cells, "
                "expected 6")
        did, case_id, authority, requirement, aggregate, keys = cells
        did = did.strip("`")
        parts = re.findall(r"`([^`]+)`", authority)
        if len(parts) != 2:
            raise PlanReleaseRuleMismatch(
                f"mandatory diagnostic {did}: the authority cell must name a source "
                "and a path")
        view[f"release_authority.mandatory_diagnostics.{did}.diagnostic_id"] = did
        view[f"release_authority.mandatory_diagnostics.{did}.case_id"] = (
            None if case_id.strip("`") == "None" else case_id.strip("`"))
        view[f"release_authority.mandatory_diagnostics.{did}.authority_source"] = parts[0]
        view[f"release_authority.mandatory_diagnostics.{did}.authority_path"] = parts[1]
        view[f"release_authority.mandatory_diagnostics.{did}.requirement"] = requirement
        view[f"release_authority.mandatory_diagnostics.{did}.aggregate_key"] = (
            aggregate.strip("`"))
        view[f"release_authority.mandatory_diagnostics.{did}.required_keys"] = (
            [] if keys == "\u2014" else re.findall(r"`([^`]+)`", keys))
    return view


# ------------------------------------------------- generated region: controls
def render_controls_region(plan: dict[str, Any]) -> str:
    out = ["| control | purpose | case |", "|---|---|---|"]
    for row in plan["controls"]:
        out.append(f"| {row['control']} | {row['purpose']} | `{row['case']}` |")
    return "\n".join(out) + "\n"


def parse_controls_region(text: str, plan: dict[str, Any]) -> dict[str, Any]:
    rows = [line for line in text.splitlines()
            if line.startswith("| ") and not line.startswith("| control")
            and not line.startswith("|---")]
    if len(rows) != len(plan["controls"]):
        raise PlanSurfaceMismatch(
            f"the controls region renders {len(rows)} rows; the plan declares "
            f"{len(plan['controls'])}")
    view: dict[str, Any] = {}
    for index, line in enumerate(rows):
        cells = [c.strip() for c in line.strip().strip("|").split(" | ")]
        if len(cells) != 3:
            raise PlanSurfaceMismatch(
                f"controls row {index} renders {len(cells)} cells, expected 3")
        view[f"controls.{index}.control"] = cells[0]
        view[f"controls.{index}.purpose"] = cells[1]
        view[f"controls.{index}.case"] = cells[2].strip("`")
    return view


# ------------------------------------------- DERIVED: the size boundaries
def require_derived_boundaries(plan: dict[str, Any], text: str) -> None:
    """Section 12a renders boundaries that are RECOMPUTED, never copied.

    They are `DERIVED_RENDERING`: the plan's own primitives (R, nominal alpha)
    determine them through `size_boundary`, so a displayed boundary that differs
    from its recomputation is a defect rather than a second opinion.
    """
    from .classification import size_boundary
    from .dispositions import cp_lower
    declared = plan["size_validation_semantics"]["derived_boundaries"]
    for case_id, row in declared.items():
        recomputed = size_boundary(row["replicates"], row["nominal_alpha"])
        if row["boundary"] != recomputed:
            raise PlanDerivedValueMismatch(
                f"{case_id} boundary is DERIVED as size_boundary("
                f"{row['replicates']}, {row['nominal_alpha']}) = {recomputed}, but the "
                f"plan declares {row['boundary']}")
        for key, count in (("cp_lower_at_boundary", row["boundary"]),
                           ("cp_lower_at_boundary_plus_1", row["boundary"] + 1)):
            bound = cp_lower(count, row["replicates"])
            if abs(row[key] - bound) > 1e-12:
                raise PlanDerivedValueMismatch(
                    f"{case_id} {key} is DERIVED as cp_lower({count}, "
                    f"{row['replicates']}) = {bound!r}, but the plan declares "
                    f"{row[key]!r}")
        shown = (f"| **{case_id}** | {row['replicates']} | `{row['nominal_alpha']}` | "
                 f"0\u2013{row['boundary']} | {row['boundary'] + 1}+ |")
        if shown not in text:
            raise PlanDerivedValueMismatch(
                f"section 12a does not render the derived {case_id} boundary row "
                f"exactly as recomputed; expected to find {shown!r}")


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
    for key in canonical_generating_model(plan):
        keys.add(f"generating_model.{key}")
    for index in range(len(plan["controls"])):
        for key in ("control", "purpose", "case"):
            keys.add(f"controls.{index}.{key}")
    for index, row in enumerate(plan["assurance"]):
        for key in ASSURANCE_KEYS:
            keys.add(f"assurance.{index}.{key}")
    release = plan["release_authority"]
    keys.add("release_authority.complete_pass_event")
    for key in RELEASE_AUTHORITY_PROSE:
        keys.add(f"release_authority.{key}")
    for cid, block in release["implied_stronger"].items():
        for key in block:
            keys.add(f"release_authority.implied_stronger.{cid}.{key}")
    for row in release["mandatory_diagnostics"]:
        for key in MANDATORY_DIAGNOSTIC_KEYS:
            keys.add(f"release_authority.mandatory_diagnostics."
                     f"{row['diagnostic_id']}.{key}")
    for gap in plan["authority_gaps"]:
        for key in ("gap", "affects", "status", "resolution"):
            keys.add(f"authority_gaps.{gap['id']}.{key}")
    keys.add("final_campaign.verdict_on_success")
    keys.add("final_campaign.rule")
    for index in range(len(plan["final_campaign_classification"]["requirements"])):
        keys.add(f"final_campaign.requirements.{index}")
    return tuple(sorted(keys))


# ------------------------------------------------- normative-section registry
GENERATED = "GENERATED"          # covered by an anchor-delimited generated region
PARSED = "PARSED"                # normative values extracted and compared
DERIVED_SECTION = "DERIVED"      # displays values recomputed from JSON primitives
NON_NORMATIVE = "NON_NORMATIVE"  # explanatory, historical or operational only

#: EVERY `## ` section of the normative Markdown plan, with how its normative
#: content is covered. An auditor has now twice found duplicated normative
#: material outside the registered surface -- first the identity table, then the
#: generating model -- so the registry is checked for TOTALITY: a section the
#: document carries and the registry does not classify is a conformance failure.
SECTION_REGISTRY = {
    "1. Frozen identities": (PARSED, "the seven identity rows are parsed and compared"),
    "1a. Machine-readable authority block": (
        GENERATED, "the authority block itself"),
    "2. Adopted rules, unchanged": (GENERATED, "adopted_rules region"),
    "3. The eight cases": (GENERATED, "cases region, including subcondition payloads"),
    "4. Generating model": (GENERATED, "generating_model region"),
    "5. Calibration": (
        NON_NORMATIVE, "derivation narrative for the adopted calibration architecture. "
                       "Its operative values -- calibration_scope, per-case artifact "
                       "counts and the per-case calibration flags -- are carried by the "
                       "cases region and the authority block, not by this prose"),
    "6. Statistical assurance": (
        GENERATED, "assurance region: the human summary table AND the structured "
                   "release-binding table"),
    "6a. Release authority \u2014 FROZEN PROSPECTIVELY": (
        GENERATED, "release_authority region: the complete-pass event, the "
                   "IMPLIED_STRONGER relationships and the mandatory contract "
                   "diagnostics"),
    "7. Seed separation": (
        NON_NORMATIVE, "narrative. The operative seed authority is each case's "
                       "allowed_seed_families and fields_affected, both in the cases "
                       "region, and the derivation itself is code bound by module hashes"),
    "8. Controls": (GENERATED, "controls region"),
    "9. Output schema": (PARSED, "schema versions and both field lists are parsed"),
    "10. Failure classifications": (PARSED, "the eleven classifications are parsed"),
    "11. No post-outcome tuning": (
        NON_NORMATIVE, "prohibition narrative; changes nothing executable"),
    "12. Author dispositions — CLOSED PROSPECTIVELY": (
        GENERATED, "release_rules region"),
    "12a. Size-validation semantics — FROZEN PROSPECTIVELY": (
        DERIVED_SECTION, "the derived boundaries are recomputed by size_boundary and "
                         "cp_lower and compared to the rendered table"),
    "12b. Final campaign classification — FROZEN PROSPECTIVELY": (
        NON_NORMATIVE, "points at the generated release-rules region; it no longer "
                       "restates the requirements"),
    "13. Execution": (PARSED, "the execution_authorised sentence is parsed"),
    "13a. Execution-seal architecture — FROZEN PROSPECTIVELY": (
        PARSED, "the seal state and the canonical driver path are parsed"),
    "14. Pre-execution repair — SUPERSESSION RECORD": (
        NON_NORMATIVE, "historical supersession record; preserved, not executable"),
    "15. Parallelism policy": (
        NON_NORMATIVE, "operational policy; changes no scientific rule"),
    "16. What the cost figures actually contain": (
        NON_NORMATIVE, "benchmark provenance and projections; measurements about the "
                       "package, not parameters of the experiment"),
    "17. Correction — the superseded 40,000 artifact count": (
        NON_NORMATIVE, "historical correction record"),
    "18. Plan-coherence and execution-seal repair — SUPERSESSION RECORD": (
        NON_NORMATIVE, "historical supersession record"),
    "19. Generating-model coherence — SUPERSESSION RECORD": (
        NON_NORMATIVE, "historical supersession record"),
    "20. Release authority — SUPERSESSION RECORD": (
        NON_NORMATIVE, "historical supersession record. Its operative content -- the "
                       "structured release rules and the mandatory contract diagnostics "
                       "-- lives in the generated sections 6 and 6a"),
}


def markdown_sections(text: str) -> list[str]:
    """Every `## ` heading, in document order."""
    return [m.group(1).strip() for m in re.finditer(r"^## (.+)$", text, re.M)]


def require_section_registry_totality(text: str) -> None:
    """Refuse a normative Markdown section the registry does not classify.

    This is the whole-document guard: a future section added without a registry
    entry fails here rather than quietly becoming unchecked authority.
    """
    present = markdown_sections(text)
    duplicated = sorted({h for h in present if present.count(h) > 1})
    if duplicated:
        raise PlanAmbiguousBlock(
            f"the Markdown plan carries duplicated section headings {duplicated}")
    unregistered = [h for h in present if h not in SECTION_REGISTRY]
    if unregistered:
        raise PlanSectionUnregistered(
            f"the Markdown plan carries sections the normative-section registry does "
            f"not classify: {unregistered}. Every section must be registered as "
            f"{GENERATED}, {PARSED}, {DERIVED_SECTION} or {NON_NORMATIVE} with a "
            "reason, so its normative status is decided rather than assumed.")
    absent = [h for h in SECTION_REGISTRY if h not in present]
    if absent:
        raise PlanSectionUnregistered(
            f"the registry classifies sections the Markdown plan no longer carries: "
            f"{absent}")


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
        "release_authority": render_release_authority_region,
        "generating_model": render_generating_model_region,
        "controls": render_controls_region,
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
    view.update(parse_release_authority_region(
        _region(text, "release_authority"), plan))
    view.update(parse_controls_region(_region(text, "controls"), plan))
    for key, value in canonical_generating_model_from_markdown(
            _region(text, "generating_model"), plan).items():
        view[f"generating_model.{key}"] = value
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
    if key.startswith("generating_model."):
        return PlanGeneratingModelMismatch
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

    # whole-document guard FIRST: an unregistered section is unchecked authority
    require_section_registry_totality(text)
    require_generating_model_coherence(root, plan, text)
    require_derived_boundaries(plan, text)

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
