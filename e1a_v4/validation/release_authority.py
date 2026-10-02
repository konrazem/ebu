"""Frozen release authority -> validation-plan conformance, before any RNG.

WHY THIS MODULE EXISTS
    `contract_plan.py` bound the GENERATING model: fields, stiffnesses,
    temperatures, orientations, the relaxation rule, the true-bridge beta. It did
    not bind the RELEASE rules. An independent audit then showed that a plan could
    stay internally coherent -- Markdown and JSON agreeing, every derived boundary
    recomputing -- while changing release-bearing statistics:

        C1 complete-pipeline target   0.90 -> 0.80     ACCEPTED
        C1 replicates                  300 -> 301      ACCEPTED
        C3 replicates                  400 -> 401      ACCEPTED
        C8 replicates                  200 -> 201      ACCEPTED

    Coherence between two renderings of a plan cannot amend the frozen authority
    upstream of it. The missing edge was

        FROZEN DESIGN / VALIDATION AUTHORITY
                |
        CASE RELEASE SPECIFICATION      <- this module
                |
        MACHINE PLAN  ->  MARKDOWN PLAN  ->  CLASSIFIER / REPORTER

    The plan may not redefine a replicate count, confidence rule, confidence
    level, target probability, integer boundary, denominator rule, release
    endpoint or mandatory contract diagnostic merely because both plan formats
    agree about the new value.

WHAT A RELATIONSHIP MEANS
    EXACT                  the frozen authority states this value literally
    DERIVED                mechanically recomputed from frozen inputs; never a
                           second independent source of truth
    IMPLIED_STRONGER       the adopted release rule is strictly stronger than an
                           older frozen requirement, which is NOT thereby erased
    CASE_SPECIFIC          no upstream value exists; the value was frozen with the
                           adopted validation package and is pinned HERE, in a
                           module whose hash is part of the execution identity
    REPORT_ONLY_MANDATORY  frozen authority requires it to be REPORTED; it is not
                           itself the release gate
    NOT_APPLICABLE         an explicitly justified non-binding, never a default

WHY CASE_SPECIFIC IS NOT A LOOPHOLE
    C4's R = 2000 and C5's R = 400 have no upstream contract value: design section
    15 items 5 and 6 freeze what must be validated, not how many replicates. Those
    counts were frozen with the package at 475633c and have never changed. Pinning
    them here keeps them fail-closed and moves the execution identity if they are
    ever edited, which editing the plan alone would not do.

NO RNG. Parsing, arithmetic and comparison only. No model state is advanced.
"""

from __future__ import annotations

import functools
import os
import re
import dataclasses
from dataclasses import dataclass, fields as dataclass_fields
from typing import Any

from ..numerics import Refusal
from .classification import (
    ESTIMATED_STATUS, GROSS_INFLATION_TOLERANCE,
    INCOMPLETE_EVIDENCE_CLASSIFICATION, NON_FAIL_CLOSED_STATUSES,
    PER_FIELD_SIZE_CASES, REFUSAL_AUTHORISING_STATUSES, REQUIRED_SIZE_FIELDS,
    SIZE_FAILURE, SIZE_INTERPRETATION, SIZE_NOT_EVALUABLE, SIZE_NO_INFLATION,
    RECORD_ESTIMATED, RECORD_NO_P1_GROUP, CampaignCounts, FieldSizeOutcome,
    authorises_undefined_block_decision, classify_campaign, classify_record,
    complete_pass_from_components, composite_p1_from_blocks,
    false_acceptance_from_components, record_consistency_failure,
    scale_recovery_failure, size_boundary,
)
from .dispositions import cp_lower, cp_upper, g1_success_threshold, g2_max_false_acceptances
from .refusals import (
    ContractMandatoryDiagnosticMismatch, ContractMandatoryDiagnosticMissing,
    ContractReleaseBindingUnclassified, ContractReleaseBoundDirectionMismatch,
    ContractReleaseConfidenceRuleMismatch, ContractReleaseDerivedThresholdMismatch,
    ContractReleaseEndpointMismatch, ContractReleaseImplicationBroken,
    ContractReleaseReplicateCountMismatch, ContractReleaseTargetMismatch,
    ImplementationAuthorityLag,
    NormativeSurfaceUnclassified, ProspectiveAmendmentMismatch,
    ResultSchemaInvalid,
)

EXACT = "EXACT"
DERIVED = "DERIVED"
IMPLIED_STRONGER = "IMPLIED_STRONGER"
CASE_SPECIFIC = "CASE_SPECIFIC"
REPORT_ONLY_MANDATORY = "REPORT_ONLY_MANDATORY"
NOT_APPLICABLE = "NOT_APPLICABLE"

RELATIONSHIPS = (EXACT, DERIVED, IMPLIED_STRONGER, CASE_SPECIFIC,
                 REPORT_ONLY_MANDATORY, NOT_APPLICABLE)

#: How a normative C3/C4 statement is held to the canonical rule. Every statement
#: inside a controlled container must carry exactly one of these.
CANONICAL_SOURCE = "CANONICAL_SOURCE"
GENERATED_FROM_CANONICAL = "GENERATED_FROM_CANONICAL"
STRICTLY_VERIFIED_DUPLICATE = "STRICTLY_VERIFIED_DUPLICATE"
NON_NORMATIVE_EXPLANATION = "NON_NORMATIVE_EXPLANATION"

#: Leaf-level classes for the nested authority subtree. A parent classification
#: does NOT authorise its descendants, so every leaf carries its own.
STRICTLY_PINNED_NON_RULE_TEXT = "STRICTLY_PINNED_NON_RULE_TEXT"
STRUCTURAL_VALUE_WITH_EXPLICIT_SCHEMA = "STRUCTURAL_VALUE_WITH_EXPLICIT_SCHEMA"
#: Enumerated and classified, deliberately NOT bound. Used only where binding
#: would silently close a defect that is tracked as separate authorised work.
DEFERRED_OUT_OF_SCOPE = "DEFERRED_OUT_OF_SCOPE"

VERIFICATION_MODES = (CANONICAL_SOURCE, GENERATED_FROM_CANONICAL,
                      STRICTLY_VERIFIED_DUPLICATE, NON_NORMATIVE_EXPLANATION,
                      STRICTLY_PINNED_NON_RULE_TEXT,
                      STRUCTURAL_VALUE_WITH_EXPLICIT_SCHEMA, DEFERRED_OUT_OF_SCOPE)

#: Authority sources, most authoritative first.
CONTRACT = "design_contract"
DESIGN = "prospective_design"
PACKAGE = "adopted_validation_package"

DESIGN_DOCUMENT = "docs/e1a/E1A_V4_PROSPECTIVE_DESIGN.md"

LOWER = "LOWER"
UPPER = "UPPER"
REPORT_ONLY = "REPORT_ONLY"
ONE_SIDED = "one-sided"
CLOPPER_PEARSON = "Clopper-Pearson"

#: C8's declared pairing semantics, pinned in full. The contract fixes the
#: replicate RULE; this sentence is the package's operational statement of it, and
#: it determines that the two blinded branches share one replicate's randomness.
C8_PAIRING = ("INTENTIONAL: both factors act on the SAME underlying synthetic "
              "replicate by the frozen deterministic Branch-A scale transform. They "
              "are NOT independent random subconditions and must not be given "
              "separate streams.")

#: How an integer pass boundary is derived, chosen mechanically from
#: (bound_direction, comparison). A hand-entered threshold is never trusted.
BOUNDARY_RULES = {
    (LOWER, ">="): ("smallest k with cp_lower(k, R) >= target", g1_success_threshold),
    (LOWER, "<="): ("largest k with cp_lower(k, R) <= target", size_boundary),
    (UPPER, "<="): ("largest k with cp_upper(k, R) <= target", g2_max_false_acceptances),
}


@dataclass(frozen=True)
class ReleaseBinding:
    """One release-bearing quantity, its authority and its plan restatement."""

    item: str
    case_id: str | None
    authority_source: str
    authority_path: str
    plan_path: str
    relationship: str
    reason: str
    expected: Any
    actual: Any
    refusal: type


@dataclass(frozen=True)
class MandatoryDiagnostic:
    """A frozen requirement to REPORT something that is not the release gate."""

    diagnostic_id: str
    case_id: str | None
    authority_source: str
    authority_path: str
    requirement: str
    aggregate_key: str
    required_keys: tuple[str, ...]


# --------------------------------------------------------------- authority text
#: Frozen requirement strings, parsed once. Any edit upstream refuses rather than
#: being silently reinterpreted by a regex that happens to still match.
_REQ_2 = ("achieved joint gate size: Clopper-Pearson one-sided 95% UPPER bound "
          "<= 3%, R = 400, at every declared geometry")
_REQ_3 = ("joint equivalence power: one-sided 95% LOWER bound >= 0.90, R = 300, "
          "design target pi >= 0.95")
_REQ_4 = ("surrogate calibration law validated at the operating quantile against "
          "directly generated trajectories")
_REQ_5 = ("plug-in conditioning validated over sigma_k in {0, 0.5%, 1%} x "
          "sigma_psi in {0, 0.2, 0.5, 1.0} deg")
_REQ_6 = "theta_cap size AND power demonstrated at rho = boundary +/- 20%"
_REQ_7 = "G5 block delta-method error quantified"
_REQ_8 = "every declared job reconciled by status"
_REQ_9 = "complete-pipeline success reported UNCONDITIONALLY"

FROZEN_REQUIREMENT_TEXT = {2: _REQ_2, 3: _REQ_3, 4: _REQ_4, 5: _REQ_5,
                           6: _REQ_6, 7: _REQ_7, 8: _REQ_8, 9: _REQ_9}

#: Design section 15 item 4 supplies the interval METHOD for the power
#: demonstration, which the contract JSON renders more tersely.
DESIGN_ITEM_4_METHOD_PHRASE = ("joint equivalence power demonstrated: one-sided 95% "
                               "**lower** bound ≥ 0.90, R = 300")


@dataclass(frozen=True)
class ParsedRequirement:
    """A frozen statistical requirement, read out of its authority text."""

    method: str | None
    sided: str
    level: float
    direction: str
    comparison: str
    target: float
    replicates: int


def _require_frozen_text(contract: dict[str, Any], index: int) -> str:
    """The frozen requirement string, refused if it is not the adopted one."""
    items = contract["synthetic_validation_requirements"]
    if index >= len(items) or items[index] != FROZEN_REQUIREMENT_TEXT[index]:
        raise ContractReleaseBindingUnclassified(
            f"synthetic_validation_requirements[{index}] is not the adopted text; "
            "its release derivation requires review rather than a silent re-parse")
    return items[index]


_REQ_PATTERN = re.compile(
    r"(?:(?P<method>Clopper-Pearson) )?(?P<sided>one-sided) (?P<level>\d+)% "
    r"(?P<direction>LOWER|UPPER) bound (?P<comparison><=|>=) (?P<target>[\d.]+)(?P<pct>%)?"
    r", R = (?P<replicates>\d+)")


def parse_requirement(text: str, what: str) -> ParsedRequirement:
    """Read the statistical structure out of a frozen requirement string."""
    match = _REQ_PATTERN.search(text)
    if match is None:
        raise ContractReleaseBindingUnclassified(
            f"{what}: the frozen requirement text no longer states a parseable "
            f"one-sided confidence rule: {text!r}")
    target = float(match.group("target"))
    if match.group("pct"):
        target /= 100.0
    return ParsedRequirement(
        method=match.group("method"), sided=match.group("sided"),
        level=float(match.group("level")) / 100.0, direction=match.group("direction"),
        comparison=match.group("comparison"), target=target,
        replicates=int(match.group("replicates")))


def design_declares_clopper_pearson_power(root: str) -> bool:
    """Design section 15 item 4 names the interval method the contract omits."""
    path = os.path.join(root, DESIGN_DOCUMENT)
    with open(path, encoding="utf-8") as handle:
        text = handle.read()
    return DESIGN_ITEM_4_METHOD_PHRASE in text and "Clopper–Pearson" in text


# ------------------------------------------------------- the case specification
@dataclass(frozen=True)
class CaseRelease:
    """The frozen release rule for one case, with an authority for every part."""

    case_id: str
    assurance_index: int
    unit: str
    endpoint: str
    #: (value, relationship, authority_source, authority_path, reason)
    replicates: tuple
    method: tuple
    sided: tuple
    level: tuple
    direction: tuple
    comparison: tuple
    target: tuple
    pooling: tuple


def _c(value, relationship, source, path, reason):
    return (value, relationship, source, path, reason)


CP_LEVEL_REASON = ("the frozen authority fixes a 95% level for both the size and the "
                   "power demonstration; no case may quietly adopt another level")
INFLATION_DIRECTION_REASON = (
    "the adopted inflation test is H0: p <= nominal alpha vs H1: p > nominal alpha at "
    "one-sided 5%, whose rejection region is exactly CP_lower(k, R) > alpha, so the "
    "bound direction is LOWER by construction rather than by choice")
JOINT_GATE_R_REASON = (
    "P1 is the two-block union declared in endpoints.P1_geometry.procedure; this case "
    "demonstrates one block of that same joint gate at the same declared geometries, so "
    "it inherits the frozen R of the joint-gate size requirement")
#: Cases whose resolved field structure is carried in a per-case semantics block
#: as well as in the assurance row. Both are authority; binding them is what stops
#: a coherent edit to one of them alone from changing the measured size.
FIELD_STRUCTURE_CASES = {
    "C3_g5_block": "c3_semantics",
    "C4_surrogate_validity": "c4_semantics",
}

FIELD_REDUCTION_REASON = (
    "the elementary size event is PER FIELD under the prospective amendment recorded as "
    "authority_gaps G4: each declared field keeps its own R-replicate rejection sequence, "
    "so there is nothing to pool and no within-replicate field reduction exists. The case "
    "contributes one required condition per field to the conjunctive final classification, "
    "exactly as C2 does")
PACKAGE_R_REASON = (
    "the frozen authority states WHAT must be validated but no replicate count; this "
    "count was frozen with the adopted package at 475633c, has never changed, and is "
    "pinned here so that editing it moves the execution identity")


# ============================================================================
# THE CANONICAL C3/C4 PER-FIELD AMENDMENT
# ============================================================================
#: ONE source for the approved prospective amendment (plan disposition G4).
#:
#: WHY THIS EXISTS. The amendment was first written as structured plan fields
#: PLUS four separate pieces of normative English -- the G4 resolution, the two
#: formal pass/fail criteria, and the per-case semantics prose. An independent
#: audit then showed that all four could be edited to say ANY-FIELD reduction or
#: pooling while the structured fields still said PER_FIELD, with Markdown and
#: JSON mutually coherent, and the whole package still passed preflight. Four
#: hand-maintained descriptions of one decision is the defect; this is the fix.
#:
#: The rule lives HERE, in the case-release-specification layer that already sits
#: above the machine plan, so the expected semantics are NOT read from the text
#: being checked. Every normative rendering in the plan is generated from this
#: object and compared byte-exactly, so a contradicting edit cannot be coherent.
FIELD_SIZE_DISPOSITION_ID = "G4"
FIELD_SIZE_DISPOSITION_TYPE = "C3_C4_PER_FIELD_SIZE"
FIELD_SIZE_DISPOSITION_STATUS = "CLOSED PROSPECTIVELY"
FIELD_SIZE_DISPOSITION_AFFECTS = "C3, C4"

EVALUATION_SCOPE_PER_FIELD = "PER_FIELD"
FIELD_REDUCTION_NONE = "NONE"
POOLING_FORBIDDEN = "FORBIDDEN"
FINAL_RELEASE_REPRESENTATION = "FIELD_CONDITION_VECTOR"
FINAL_RELEASE_COMPENSATION = "FORBIDDEN"

#: The final campaign rule, the derived-boundary pooling sentence and the
#: assurance confidence vocabulary. The second independent audit found the first
#: two could be edited to contradict the rule above while Markdown and JSON still
#: agreed, so they are canonical here and GENERATED into the plan.
FINAL_RELEASE_CONJUNCTION = "CONJUNCTIVE"
FINAL_RELEASE_VERDICT = "VALIDATION_PASS"
FINAL_RELEASE_IMPLEMENTATION = "e1a_v4.validation.classification.classify_campaign"
FINAL_RELEASE_INDEPENDENT_FACTS = (
    "complete-pipeline achievement and component size cleanliness are REPORTED "
    "SEPARATELY and never collapsed. A campaign may fail because complete-pipeline "
    "success < target even with no significant size-inflation diagnostic: a valid "
    "scientific failure. Conversely C1 may reach >= 0.90 while a component case "
    "detects significant size inflation: also a validation failure, because the "
    "implemented calibration is not behaving according to its declared nominal "
    "structure. Both facts are reported.")
FIELD_SIZE_ESTIMATOR = "rejection proportion"
FIELD_SIZE_COMPARISON = "<="
FIELD_SIZE_CONFIDENCE_LEVEL = 0.95
FIELD_SIZE_SIDED = "one-sided"
FIELD_SIZE_METHOD = "Clopper-Pearson"
FIELD_SIZE_BOUND_DIRECTION = "LOWER"
FIELD_SIZE_BOUNDARY_DERIVATION = "largest k with cp_lower(k, R) <= target"

#: The declared physical fields, in declaration order. Order, membership and
#: multiplicity are all load-bearing: a removed, duplicated, replaced or extra
#: field changes which conditions the conjunction requires.
FIELD_SIZE_REQUIRED_FIELDS = ("theta0_circular", "theta1_power", "theta2_ellipse",
                              "theta3_temperature")


@dataclass(frozen=True)
class FieldSizeRule:
    """The approved per-field size semantics for one case."""

    case_id: str
    semantics_key: str
    evaluation_scope: str
    field_reduction: str
    pooling: str
    required_fields: tuple[str, ...]
    primary_endpoint: str
    replicates: int
    nominal_alpha: float
    alpha_name: str
    boundary: int
    decision: str
    #: Case-specific sentence the frozen authority already required, carried
    #: verbatim so the whole criterion can be generated rather than hand-kept.
    trailing_requirement: str
    #: Exact per-field false size-inflation probability at the nominal null, and
    #: the dependence-free bounds on all four fields being clean. Disclosure, not
    #: thresholds; rendered into the disposition so the numbers cannot drift.
    false_flag_probability: str
    all_clean_lower: str
    all_clean_upper: str
    #: Which semantics key carries the field-structure status sentence. C3's own
    #: `status` already records an EARLIER disposition (Block-1 versus G5), so its
    #: field-structure status lives beside it rather than overwriting it.
    status_key: str = "status"
    secondary_diagnostic: str | None = None
    secondary_feeds_primary_release: bool | None = None
    #: The assurance row's confidence-bound sentence. C4 additionally names the
    #: two-sided interval as a mandatory diagnostic rather than the release gate.
    bound_statement: str = "Clopper-Pearson one-sided LOWER (inflation test)"
    #: Section 12a's retention sentence, where the case has one.
    retention_statement: str | None = None
    #: Where a case's `status` key records an EARLIER disposition, that status.
    #: C3's does (Block-1 versus G5); C4's carries the field-structure status.
    earlier_status: str | None = None


FIELD_SIZE_RULES = (
    FieldSizeRule(
        case_id="C3_g5_block", semantics_key="c3_semantics",
        evaluation_scope=EVALUATION_SCOPE_PER_FIELD,
        field_reduction=FIELD_REDUCTION_NONE, pooling=POOLING_FORBIDDEN,
        required_fields=FIELD_SIZE_REQUIRED_FIELDS,
        primary_endpoint="G5_BLOCK_SIZE", replicates=400, nominal_alpha=0.001,
        alpha_name="alpha_2", boundary=2, decision="G5",
        trailing_requirement=("Also report the measured sd(g2) against the "
                              "leading-order 24 A4 / n prediction."),
        false_flag_probability="0.00788343125882217",
        all_clean_lower="0.9684663", all_clean_upper="0.9921166",
        status_key="field_structure_status",
        secondary_diagnostic="SECONDARY_PREDECLARED_INTERACTION_DIAGNOSTIC",
        secondary_feeds_primary_release=False,
        earlier_status=("AMBIGUITY RESOLVED PROSPECTIVELY, before any random outcome "
                        "exists")),
    FieldSizeRule(
        case_id="C4_surrogate_validity", semantics_key="c4_semantics",
        evaluation_scope=EVALUATION_SCOPE_PER_FIELD,
        field_reduction=FIELD_REDUCTION_NONE, pooling=POOLING_FORBIDDEN,
        required_fields=FIELD_SIZE_REQUIRED_FIELDS,
        primary_endpoint="BLOCK1_ACHIEVED_SIZE", replicates=2000,
        nominal_alpha=0.004, alpha_name="alpha_1", boundary=13,
        decision="Block-1",
        trailing_requirement=("RETAIN the full two-sided interval and the observed "
                              "operating-quantile discrepancy; the binary diagnostic "
                              "does not replace the discrepancy report."),
        false_flag_probability="0.033884449548367356",
        all_clean_lower="0.8644622", all_clean_upper="0.9661156",
        bound_statement=("Clopper-Pearson one-sided LOWER (inflation test); the "
                         "two-sided interval is a MANDATORY CONTRACT DIAGNOSTIC, not "
                         "the release gate"),
        retention_statement=("the full two-sided interval and the observed "
                             "operating-quantile discrepancy are STILL reported; this "
                             "binary diagnostic does not replace them")),
)


# ---- STRUCTURED REFUSAL: the G5 prospective amendment -----------------------
#: A VALID STRUCTURED REFUSAL can leave a C3 or C4 PRIMARY endpoint decision
#: undefined. Frozen authority defined what a refusal means for complete-pipeline
#: success (C1) and said nothing about what it means for a COMPONENT SIZE TEST.
#: The author closed that gap prospectively, before any outcome existed.
REFUSAL_DISPOSITION_ID = "G5"
REFUSAL_DISPOSITION_STATUS = "CLOSED PROSPECTIVELY"
REFUSAL_DISPOSITION_AFFECTS = "C3, C4"

#: The THIRD primary field-level state. It is neither of the two statistical
#: verdicts: it says the preregistered evidence was not fully observed.
NOT_EVALUABLE = "NOT_EVALUABLE"
#: How an undefined primary endpoint is encoded. The whole point of the amendment.
REFUSAL_ENCODING = "NEITHER_REJECTION_NOR_NONREJECTION"
#: The primary denominator does not shrink to the surviving replicates.
REFUSAL_DENOMINATOR_RULE = "PLANNED_R_PRESERVED"
#: What a required field must be for the campaign to pass.
REFUSAL_RELEASE_REQUIREMENT = "EVALUABLE_AND_CLEAN"
#: The campaign-level failure reason. Deliberately NOT STATISTICAL_SIZE_FAILURE,
#: which would assert a rejection that never happened, and deliberately NOT
#: STRUCTURED_REFUSAL_EXCESS, whose name implies a tolerated fraction that this
#: amendment does not create. VALIDATION_INCONCLUSIVE is already frozen in
#: `failure_classifications` and carried no declared trigger; this supplies one.
REFUSAL_CAMPAIGN_CLASSIFICATION = "VALIDATION_INCONCLUSIVE"
#: There is NO tolerated-refusal fraction. One refusal is enough.
REFUSAL_TOLERATED_FRACTION = "NONE"
#: The per-field terminal information the amendment requires, so a reader can tell
#: "the size test rejected" from "the size test could not be validly evaluated".
REFUSAL_REQUIRED_TERMINAL_COUNTS = (
    "planned_R",
    "evaluable_primary_endpoint_count",
    "structured_refusal_count",
    "defined_rejection_count",
    "primary_size_status",
    "refusal_reasons",
)
#: A survivor-conditioned figure is permitted only in the role design section 14
#: and `complete_pass_denominator.conditional_diagnostics` already allow.
REFUSAL_SURVIVOR_ROLE = "SECONDARY_DIAGNOSTIC_ONLY"

#: Whether a valid structured refusal can leave the case's PRIMARY endpoint
#: undefined, and why. C2 releases on the COMPOSITE P1 decision, which FAILS
#: CLOSED, so its elementary event exists for every replicate including a refusal;
#: C3 and C4 release on ONE BLOCK of that gate, and a refusal that produced no
#: p-values leaves that block's decision undefined. This is why the amendment
#: reaches C3 and C4 and does not reach C2.
PRIMARY_ENDPOINT_UNDEFINABLE = {
    "C2": (False,
           "the composite P1 decision FAILS CLOSED, so this case's elementary "
           "event is defined for every replicate including a structured refusal"),
    "C3": (True,
           "the primary endpoint is ONE BLOCK of the two-block gate; a structured "
           "refusal that produced no p-values leaves the G5 decision undefined"),
    "C4": (True,
           "the primary endpoint is ONE BLOCK of the two-block gate; a structured "
           "refusal that produced no p-values leaves the Block-1 decision undefined"),
}


@dataclass(frozen=True)
class StructuredRefusalRule:
    """The approved treatment of a valid structured refusal in a size case."""

    disposition_id: str
    encoding: str
    verdict: str
    denominator_rule: str
    release_requirement: str
    campaign_classification: str
    tolerated_fraction: str
    survivor_role: str
    required_terminal_counts: tuple[str, ...]
    terminal_report_required: bool = True
    is_statistical_rejection: bool = False
    is_statistical_non_rejection: bool = False


STRUCTURED_REFUSAL_RULE = StructuredRefusalRule(
    disposition_id=REFUSAL_DISPOSITION_ID,
    encoding=REFUSAL_ENCODING,
    verdict=NOT_EVALUABLE,
    denominator_rule=REFUSAL_DENOMINATOR_RULE,
    release_requirement=REFUSAL_RELEASE_REQUIREMENT,
    campaign_classification=REFUSAL_CAMPAIGN_CLASSIFICATION,
    tolerated_fraction=REFUSAL_TOLERATED_FRACTION,
    survivor_role=REFUSAL_SURVIVOR_ROLE,
    required_terminal_counts=REFUSAL_REQUIRED_TERMINAL_COUNTS)


def render_refusal_gap_statement(rule: StructuredRefusalRule = STRUCTURED_REFUSAL_RULE
                                 ) -> str:
    """G5's gap sentence. GENERATED from the canonical rule."""
    return (
        "a VALID STRUCTURED REFUSAL can leave a C3 or C4 PRIMARY endpoint decision "
        "undefined: C3 releases on the actual G5 / Block-2 decision and C4 on the "
        "actual Block-1 decision, and when the two-block gate produced no p-values "
        "at all neither decision exists. Frozen authority defined the treatment of "
        "structured refusals for COMPLETE-PIPELINE success only -- the contract "
        "states it inside complete_pipeline, synthetic_validation_requirements[9] "
        "names complete-pipeline success, and the mandatory diagnostic carrying the "
        "denominator_rule aggregate key is bound to C1_true_bridge_complete -- and "
        "said nothing about what an undefined primary endpoint means for a "
        "COMPONENT SIZE TEST. C1 could not absorb it either, because C1 and C3/C4 "
        "are disjoint job sets. The frozen size vocabulary offered only two "
        "verdicts, so applying the detector to an incomplete primary sequence would "
        "have reported NO_SIGNIFICANT_SIZE_INFLATION_DETECTED on evidence that was "
        "never obtained.")


def render_refusal_disposition(rule: StructuredRefusalRule = STRUCTURED_REFUSAL_RULE
                               ) -> str:
    """G5's resolution. GENERATED from the canonical rule."""
    counts = ", ".join(rule.required_terminal_counts)
    cases = " or ".join(r.case_id[:2] for r in FIELD_SIZE_RULES)
    return (
        f"A valid structured refusal that leaves a {cases} PRIMARY endpoint decision "
        f"undefined is encoded {rule.encoding}: it is NOT a statistical rejection "
        "and it is NOT a statistical non-rejection. The prospectively declared "
        f"primary denominator is {rule.denominator_rule} -- R stays at its planned "
        "value per field and is never silently reduced to the surviving replicates. "
        f"If a required field carries one or more structured refusals affecting its "
        f"primary endpoint, that field's PRIMARY size assessment is {rule.verdict}, "
        "and the frozen two-way detector is NOT run on the incomplete sequence. "
        f"{rule.verdict} is neither {SIZE_FAILURE} nor {SIZE_NO_INFLATION}: missing "
        "evidence neither establishes excess size nor establishes nominal size "
        f"behaviour. Because C3 and C4 are mandatory validation conditions, release "
        f"requires every required field to be {rule.release_requirement}, so a "
        f"{rule.verdict} field prevents the campaign from passing; the campaign "
        f"failure is classified {rule.campaign_classification} and names incomplete "
        "required validation evidence, never statistical size inflation. The "
        f"tolerated structured-refusal fraction is {rule.tolerated_fraction}: one "
        "refusal affecting a required primary endpoint is sufficient, and no "
        "refusal threshold, Bonferroni correction, familywise correction, new alpha "
        "or new integer boundary is introduced. The terminal campaign report MUST "
        "still be produced when one, some or every C3/C4 job is a valid structured "
        "refusal, as the contract's refusal reconciliation already requires. Each "
        f"required field must separately retain {counts}. A survivor-conditioned "
        f"rejection rate or confidence bound is {rule.survivor_role} and SHALL NEVER "
        "substitute for the frozen primary planned-R assessment. Per-field scope, "
        "pooling FORBIDDEN and within-replicate cross-field reduction NONE are "
        "unchanged, NOT_EVALUABLE applies independently by field and one field's "
        "evaluability never rescues another's, and the C3/C4 primary endpoint "
        "definitions, the nominal alphas and the integer boundaries are unchanged. "
        "C2 is NOT affected: its composite P1 endpoint fails closed, so its "
        "elementary event is defined even under a structured refusal. Decided "
        "before any official campaign job, trajectory or outcome existed.")


def render_refusal_verdict_order(rule: StructuredRefusalRule = STRUCTURED_REFUSAL_RULE
                                 ) -> str:
    """How the three verdicts are resolved. GENERATED.

    Stated as an ORDER because the two statistical verdicts partition every
    (rejections, R) pair between them: without an explicit precedence the
    `otherwise` branch would silently claim a clean field from an incomplete
    primary sequence, which is the pathology the amendment exists to prevent.
    """
    return (
        "resolved in order: if any required PRIMARY endpoint decision for the field "
        f"is undefined because of a valid structured refusal the verdict is "
        f"{rule.verdict} and the detector is NOT run; only on a COMPLETE primary "
        "sequence, with structured_refusal_count = 0, do on_detection and otherwise "
        "apply")


def render_refusal_semantics(field_rule: FieldSizeRule,
                             rule: StructuredRefusalRule = STRUCTURED_REFUSAL_RULE
                             ) -> dict[str, Any]:
    """The GENERATED structured-refusal members of a case's semantics block."""
    short = field_rule.case_id[:2]
    undefinable, reason = PRIMARY_ENDPOINT_UNDEFINABLE[short]
    return {
        "structured_refusal_status": (
            "STRUCTURED-REFUSAL SEMANTICS RESOLVED PROSPECTIVELY, before any random "
            f"outcome exists; see authority_gaps {rule.disposition_id}"),
        "undefined_primary_endpoint_possible": undefinable,
        "undefined_primary_endpoint_reason": reason,
        "undefined_primary_endpoint_encoding": rule.encoding,
        "refusal_is_statistical_rejection": rule.is_statistical_rejection,
        "refusal_is_statistical_non_rejection": rule.is_statistical_non_rejection,
        "primary_denominator_under_refusal": rule.denominator_rule,
        "primary_verdict_on_structured_refusal": rule.verdict,
        "release_requires": rule.release_requirement,
        "campaign_failure_classification_when_not_evaluable": (
            rule.campaign_classification),
        "tolerated_structured_refusal_fraction": rule.tolerated_fraction,
        "survivor_conditioned_rate_role": rule.survivor_role,
        "required_terminal_counts": list(rule.required_terminal_counts),
    }


def render_refusal_boundary_leaves(short: str,
                                   rule: StructuredRefusalRule = STRUCTURED_REFUSAL_RULE
                                   ) -> dict[str, Any]:
    """The GENERATED structured-refusal leaves of one derived-boundary row.

    Declared for C2 as well as C3 and C4, with C2's value recording that its
    primary endpoint cannot be undefined. Stating the scope-out explicitly is what
    stops the amendment from being read as silently applying to C2.
    """
    undefinable, reason = PRIMARY_ENDPOINT_UNDEFINABLE[short]
    if not undefinable:
        return {
            "undefined_primary_endpoint_possible": False,
            "verdict_on_structured_refusal": "NOT_APPLICABLE",
            "structured_refusal_note": reason,
        }
    return {
        "undefined_primary_endpoint_possible": True,
        "verdict_on_structured_refusal": rule.verdict,
        "structured_refusal_note": reason,
    }


def render_structured_refusal_block(
        rule: StructuredRefusalRule = STRUCTURED_REFUSAL_RULE) -> dict[str, Any]:
    """The GENERATED `size_validation_semantics.structured_refusal` block."""
    return {
        "status": ("AMENDED PROSPECTIVELY, before any random outcome exists; see "
                   f"authority_gaps {rule.disposition_id}"),
        "applies_to": REFUSAL_DISPOSITION_AFFECTS,
        "encoding": rule.encoding,
        "refusal_is_statistical_rejection": rule.is_statistical_rejection,
        "refusal_is_statistical_non_rejection": rule.is_statistical_non_rejection,
        "primary_denominator": rule.denominator_rule,
        "primary_verdict_on_any_structured_refusal": rule.verdict,
        "release_requires": rule.release_requirement,
        "campaign_failure_classification": rule.campaign_classification,
        "tolerated_structured_refusal_fraction": rule.tolerated_fraction,
        "survivor_conditioned_rate_role": rule.survivor_role,
        "terminal_report_required_under_all_refusals": rule.terminal_report_required,
        "required_terminal_counts": list(rule.required_terminal_counts),
    }

FIELD_SIZE_RULES_BY_CASE = {rule.case_id: rule for rule in FIELD_SIZE_RULES}

#: The one sentence that states the field structure. Every normative rendering
#: embeds exactly this, so there is one place the scope can be read.
_SCOPE_SENTENCE = (
    "Each declared field keeps its OWN R-replicate sequence of decisions: there is "
    "NO within-replicate reduction across fields, NO any-field event, NO "
    "every-field event, NO reference-field-only event and NO pooling of counts.")
_CASE_LEVEL_SENTENCE = (
    "The case contributes one required condition PER FIELD to the final conjunctive "
    "campaign classification and is clean only when all four are clean. That "
    "conjunction happens at CLASSIFICATION level; it must NEVER be reimplemented as "
    "a replicate-wide 'any field rejects' event, which is a different statistical "
    "object with a different null rate.")


def render_field_size_criterion(rule: FieldSizeRule) -> str:
    """The case's complete formal pass/fail criterion. GENERATED, not kept."""
    return (
        f"PER FIELD, never pooled, R = {rule.replicates} per field, nominal "
        f"{rule.alpha_name} = {rule.nominal_alpha}. {_SCOPE_SENTENCE} Inflation is "
        f"detected in a field iff CP_lower(that field's {rule.decision} rejections, "
        f"{rule.replicates}) > {rule.nominal_alpha}, i.e. {rule.boundary + 1} or more "
        f"-> STATISTICAL_SIZE_FAILURE for that field; 0-{rule.boundary} -> "
        "NO_SIGNIFICANT_SIZE_INFLATION_DETECTED for that field, which means this "
        "experiment did not establish excess size at that field, NOT that nominal "
        f"size is proved. {_CASE_LEVEL_SENTENCE} {rule.trailing_requirement}")


def render_field_size_semantics(rule: FieldSizeRule) -> dict[str, Any]:
    """The GENERATED members of the case's semantics block."""
    fields = ", ".join(rule.required_fields)
    generated = {
        "field_structure": rule.evaluation_scope,
        "field_reduction": rule.field_reduction,
        "pooling": rule.pooling,
        "field_structure_rule": (
            f"four field-specific {rule.decision} size assessments, one per declared "
            f"field ({fields}), each with its own rejection count, rate, "
            "Clopper-Pearson bound and size classification"),
        "case_level_rule": (
            "the four field conditions enter the final conjunctive classification "
            "separately and the case is clean iff all four are clean; no new scalar "
            "statistical event is created and no compensation between fields is "
            "permitted"),
        "what_is_forbidden": (
            "pooling the four fields' rejection counts, reducing the four field "
            "decisions of a replicate to one replicate-level event, and releasing on "
            "the reference field alone"),
    }
    generated["release_criterion"] = (
        f"UNCHANGED, stated per field: R = {rule.replicates} per field, nominal "
        f"{rule.alpha_name} = {rule.nominal_alpha}, CP_lower(rejections, "
        f"{rule.replicates}) > {rule.nominal_alpha} detects inflation; "
        f"0-{rule.boundary} clean, {rule.boundary + 1}+ STATISTICAL_SIZE_FAILURE")
    generated["primary_release_endpoint"] = rule.primary_endpoint
    generated[rule.status_key] = (
        "FIELD STRUCTURE RESOLVED PROSPECTIVELY, before any random outcome exists; "
        f"see authority_gaps {FIELD_SIZE_DISPOSITION_ID}")
    if rule.secondary_diagnostic is not None:
        generated["block1_role"] = rule.secondary_diagnostic
    # The G5 structured-refusal amendment. Merged here, not registered separately,
    # so the surface registry and the recursive leaf walk pick it up by the same
    # route as every other generated semantics member.
    generated.update(render_refusal_semantics(rule))
    return generated


def render_field_size_assurance(rule: FieldSizeRule) -> dict[str, Any]:
    """The GENERATED members of the case's assurance row."""
    return {
        "quantity": (f"block-2 (G5) rejection rate, per field"
                     if rule.decision == "G5"
                     else "Block-1 achieved size under the surrogate, per field"),
        "unit": "per_field",
        "pooling": rule.pooling,
        "acceptance_rule": (
            f"no inflation detected: CP_lower <= {rule.nominal_alpha}, i.e. <= "
            f"{rule.boundary}/{rule.replicates}, PER FIELD; every declared field is "
            "assessed and reported separately and counts are never pooled"),
    }


def render_field_size_boundary_rule(rule: FieldSizeRule) -> str:
    """The GENERATED section-12a boundary prose for the case."""
    return (f"0-{rule.boundary} {rule.decision} rejections PER FIELD: no significant "
            f"inflation detected; {rule.boundary + 1}+ in any field: "
            "STATISTICAL_SIZE_FAILURE for that field")


def render_field_size_gap_statement() -> str:
    """The GENERATED statement of what the disposition closes."""
    return (
        "C3 and C4 each declare four physical fields while the two-block P1 gate "
        "decides PER FIELD, so one replicate yields four Block-2 (C3) or four "
        "Block-1 (C4) decisions; no frozen document stated how those four field "
        "decisions produce the one event each case's replicate denominator counts. "
        "C2 carried 'at every declared geometry' from the contract and was "
        "explicitly per field; C3 and C4 carried no field-structure statement at "
        "all, and C3's records were mutually contradictory - its R was derived from "
        "the contract clause that says 'at every declared geometry' while its unit "
        "and pooling asserted one campaign-level count.")


def render_field_size_disposition() -> str:
    """The G4 resolution text. GENERATED from the canonical rule."""
    parts = [
        "The elementary size event for BOTH C3 and C4 is PER FIELD. "
        + _SCOPE_SENTENCE
        + " Each declared field carries its own rejection count, rejection rate, "
        "Clopper-Pearson bound and size classification over the declared fields "
        f"{', '.join(FIELD_SIZE_REQUIRED_FIELDS)}."]
    for rule in FIELD_SIZE_RULES:
        parts.append(
            f"{rule.case_id}: evaluation scope {rule.evaluation_scope}, "
            f"within-replicate field reduction {rule.field_reduction}, pooling "
            f"{rule.pooling}, primary endpoint {rule.primary_endpoint}, R = "
            f"{rule.replicates} per field at {rule.alpha_name} = "
            f"{rule.nominal_alpha} with integer boundary {rule.boundary} "
            f"(clean 0-{rule.boundary}).")
    parts.append(
        "R, the nominal alphas, the confidence method and level and the integer "
        "boundaries are UNCHANGED by this amendment and now apply per field.")
    parts.append(
        "Case-level semantics are DERIVED, not a new statistical event: each case "
        f"contributes four required field-level conditions to the existing "
        f"conjunctive final classification as a {FINAL_RELEASE_REPRESENTATION}, "
        f"exactly as C2 already does, so the case is clean iff all four fields are "
        f"clean, with compensation {FINAL_RELEASE_COMPENSATION} and the failing "
        "field identity preserved. " + _CASE_LEVEL_SENTENCE)
    parts.append(
        "C3's primary release endpoint remains the G5 block; the full two-block P1 "
        "result remains the SECONDARY_PREDECLARED_INTERACTION_DIAGNOSTIC and does "
        "NOT feed the C3 primary release verdict.")
    parts.append(
        "OPERATING CHARACTERISTIC, disclosed and not a threshold: at the exact "
        "nominal per-field null the probability of a false size-inflation flag is "
        + " and ".join(
            f"{rule.false_flag_probability} for a {rule.case_id[:2]} field"
            for rule in FIELD_SIZE_RULES)
        + ", so the dependence-free probability that all four fields are clean lies "
        + " and ".join(
            f"in [{rule.all_clean_lower}, {rule.all_clean_upper}] for {rule.case_id[:2]}"
            for rule in FIELD_SIZE_RULES)
        + ". The C4 union bound therefore admits a family-level false-failure "
        "probability of about 13.55%. That is a CONSERVATIVE VALIDATION FAILURE -- a "
        "spurious block on release -- and NOT a false scientific pass, and no size "
        "rule was altered to reduce it.")
    parts.append(
        "DEPENDENCE: the frozen generating model intentionally shares one Branch-A "
        "common-mode draw across the fields of a replicate, so probabilistic "
        "independence of field-level gate outcomes must not simply be assumed; the "
        "direction and magnitude of the resulting dependence are NOT established by "
        "current authority or analysis, and the bounds above rely on no association "
        "assumption.")
    parts.append(
        "The complete-pipeline target >= 0.90 remains C1-only and is NOT a C3 or C4 "
        "familywise target. Decided before any official campaign job, trajectory or "
        "outcome existed.")
    return " ".join(parts)


def final_campaign_requirements() -> tuple[str, ...]:
    """The COMPLETE canonical requirement sequence, in order.

    Checking only the lines that mention C3 or C4 was the r8 blocker: a twelfth
    requirement permitting one clean field to offset a failed one named neither
    case and was accepted. For an authoritative list, MEMBERSHIP IS AUTHORITY, so
    the whole sequence is compared -- length, order, every element -- against this
    canonical one, which is never derived from the candidate.
    """
    out: list[str] = []
    generated = {slot: rule for slot, rule in
                 zip(_GENERATED_REQUIREMENT_SLOTS[1:], FIELD_SIZE_RULES)}
    size = len(FINAL_CAMPAIGN_REQUIREMENT_PINS) + len(_GENERATED_REQUIREMENT_SLOTS)
    for position in range(size):
        if position == _GENERATED_REQUIREMENT_SLOTS[0]:
            out.append(render_c2_requirement(index=position + 1))
            continue
        rule = generated.get(position)
        if rule is not None:
            out.append(render_field_size_requirement(rule, position + 1))
        else:
            out.append(FINAL_CAMPAIGN_REQUIREMENT_PINS[position])
    return tuple(out)


def render_field_size_requirement(rule: FieldSizeRule, index: int) -> str:
    """The case's numbered line in the final-campaign requirement list.

    Since the G5 amendment the line demands EVALUABILITY as well as cleanliness: a
    field whose primary assessment is NOT_EVALUABLE has not satisfied the
    condition, and saying only "no STATISTICAL_SIZE_FAILURE" would have let an
    unevaluated field pass by silence.
    """
    return (f"{index}. {rule.case_id[:2]} is "
            f"{STRUCTURED_REFUSAL_RULE.release_requirement} in every required "
            f"field: no {SIZE_FAILURE} and no {NOT_EVALUABLE} field")


def render_field_size_pooling_statement(rule: FieldSizeRule) -> str:
    """Section 12a's derived-boundary pooling sentence. GENERATED.

    The second independent audit changed this one string to "pool all four field
    counts" in a fully coherent Markdown+JSON copy and full static preflight still
    accepted it, because the derived-boundary rows bound `per_field`,
    `replicate_reduction` and the boundary prose but not this sentence.
    """
    return f"{rule.pooling} - every field is reported separately"


def render_final_campaign_rule() -> str:
    """The final campaign rule. GENERATED from the canonical per-field amendment.

    The same audit changed this to "C3/C4 pass when any one field is clean" and
    preflight accepted it: the requirement LINES were generated but the rule that
    governs how they combine was free text bound to nothing.
    """
    cases = " and ".join(rule.case_id[:2] for rule in FIELD_SIZE_RULES)
    count = len(FIELD_SIZE_REQUIRED_FIELDS)
    return (
        f"{FINAL_RELEASE_CONJUNCTION}. Every required case must pass on its own "
        f"terms. {cases} each contribute {count} required field-level conditions, one "
        f"per declared field; a case is clean only when all {count} are clean, NO "
        "required condition may fail, a single clean field is NEVER sufficient, and "
        f"compensation is {FINAL_RELEASE_COMPENSATION} both between fields and "
        f"between cases. A required field satisfies its condition only when it is "
        f"{STRUCTURED_REFUSAL_RULE.release_requirement}: a field whose primary size "
        f"assessment is {NOT_EVALUABLE} has NOT satisfied it, and prevents the "
        f"campaign from passing under {STRUCTURED_REFUSAL_RULE.campaign_classification} "
        f"rather than under {SIZE_FAILURE}.")


def render_field_size_target(rule: FieldSizeRule) -> str:
    """The assurance row's human target statement. GENERATED."""
    return f"{rule.alpha_name} = {rule.nominal_alpha}"


def render_field_size_block1_role(rule: FieldSizeRule) -> str:
    """What Block-1 IS for this case. DERIVED from the canonical primary endpoint.

    C4's primary release endpoint is the Block-1 achieved size, so Block-1 is its
    PRIMARY_RELEASE_ENDPOINT. C3 releases on the G5 block, so Block-1 is its
    secondary predeclared diagnostic. This audit found C4's declaration carried no
    binding at all -- a primary/secondary status statement that nothing checked.
    """
    if rule.primary_endpoint == "BLOCK1_ACHIEVED_SIZE":
        return "PRIMARY_RELEASE_ENDPOINT"
    if rule.secondary_diagnostic is None:
        raise ValueError(f"{rule.case_id} declares no Block-1 role")
    return rule.secondary_diagnostic


def render_field_size_calibration_rationale(rule: FieldSizeRule) -> str:
    """Why Block-1 calibration is retained, and what it does NOT decide. GENERATED.

    The fourth independent audit replaced this field -- the last semantically free
    statement inside a controlled container -- with "The full P1 verdict is the
    deciding condition for C3." and full static preflight ACCEPTED it. The text was
    classified NON_NORMATIVE_EXPLANATION and guarded only by a short list of
    suspicious words, which that sentence avoids entirely.

    No vocabulary list can decide whether free prose has become rule-bearing:
    natural language states the same rule without the listed words. So the field is
    GENERATED instead, and every semantic claim in it is read off the canonical
    rule -- including the verb, which is derived from
    `secondary_feeds_primary_release` rather than written. A package whose
    explanation contradicts the rule can no longer be built.
    """
    if rule.secondary_diagnostic is None:
        raise ValueError(f"{rule.case_id} declares no secondary diagnostic")
    decides = ("does NOT determine" if rule.secondary_feeds_primary_release is False
               else "determines")
    return (
        "the frozen scientific purpose requires reporting the two-mode max "
        "statistic's INTERACTION WITH THE TWO-BLOCK GATE. That interaction is a P1 "
        "quantity and needs a CalibrationArtifact, so calibration is retained as a "
        f"diagnostic input. The full P1 result is the {rule.secondary_diagnostic} "
        f"and {decides} the {rule.case_id[:2]} primary release verdict, which "
        f"remains the {rule.evaluation_scope} {rule.primary_endpoint} assessment "
        f"over {', '.join(rule.required_fields)}.")


# ===================================================== the DERIVED C2 release rule
#: C2's per-field release semantics, resolved by the D6a reconstruction
#: (`docs/e1a/E1A_V4_C2_POOLING_AUTHORITY_RECONSTRUCTION.md`, report commit 91b21fa)
#: and independently cleared. The rule is DERIVED, not EXACT: no controlling
#: document states "pooling forbidden" literally. It is forced by three controlling
#: facts, all predating the C3/C4 amendment:
#:
#:   1. contract `synthetic_validation_requirements[2]` requires the achieved joint
#:      gate size AT EVERY DECLARED GEOMETRY, with R = 400;
#:   2. prospective design section 12 makes `gate_pass` a PER-FIELD predicate inside
#:      `AND over 4 fields`, so P1's elementary outcome is per field and its achieved
#:      size is a per-field quantity;
#:   3. that section's budget allocates `4 x alpha_geom = 0.02`, four separate
#:      per-field P1 size events.
#:
#: A pooled assessment would still constrain an aggregate rejection rate. What it
#: would NOT do is establish the contract's condition AT EVERY declared geometry:
#: pooled over 4 x 400, the contract's own coarse ceiling admits 36 rejections while
#: one declared geometry sits at 36/400 = 9.00%.
#:
#: "Four separate field-level rejection-count processes" is a bookkeeping statement.
#: It asserts NO probabilistic independence between field outcomes, and the
#: derivation needs none.
C2_CASE_ID = "C2_geometry_false_rejection"
C2_ELEMENTARY_EVENT = "P1_REJECTION_ONE_DECLARED_FIELD"
C2_FINAL_COMBINATION = "ALL_REQUIRED_FIELD_CONDITIONS"
C2_PRIMARY_ENDPOINT = "P1_FALSE_REJECTION_RATE_PER_FIELD"

C2_DERIVATION_REASON = (
    "DERIVED, not stated literally: contract synthetic_validation_requirements[2] "
    "requires the achieved joint gate size AT EVERY DECLARED GEOMETRY with R = 400, "
    "prospective design section 12 makes gate_pass a per-field predicate inside AND "
    "over 4 fields, and that section's budget allocates 4 x alpha_geom. Together "
    "these force four separate per-field release assessments; a pooled count would "
    "constrain an aggregate rate but would not establish the required condition at "
    "every declared geometry")

#: The contract-facing trailing sentence C2's criterion has always carried.
C2_CONTRACT_DIAGNOSTIC_SENTENCE = (
    "MANDATORY CONTRACT DIAGNOSTIC [synthetic_validation_requirements[2]]: the "
    "coarse one-sided 95% Clopper-Pearson UPPER bound MUST be reported per required "
    "field and compared with the contract threshold 0.03, with an explicit PASS/FAIL. "
    "It is not validation of alpha_geom and it is not the release gate; its absence "
    "from a campaign result is RESULT_SCHEMA_INVALID.")

C2_PURPOSE_COVERAGE = ("covering G1-G5, the two-block combination, mode resolution "
                       "and structured refusals")


@dataclass(frozen=True)
class C2ReleaseRule:
    """The complete C2 release semantics, in one canonical object."""

    case_id: str
    elementary_event: str
    evaluation_scope: str
    required_fields: tuple[str, ...]
    replicates_per_field: int
    nominal_alpha: float
    alpha_name: str
    boundary: int
    field_reduction: str
    pooling: str
    final_combination: str
    primary_endpoint: str
    authority_relationship: str


#: The declared-field roster is NOT duplicated here: per-field cases share one
#: roster, and `require_c2_release_binding` checks it against the contract's own
#: `fields` declaration, in declaration order.
C2_RELEASE_RULE = C2ReleaseRule(
    case_id=C2_CASE_ID,
    elementary_event=C2_ELEMENTARY_EVENT,
    evaluation_scope=EVALUATION_SCOPE_PER_FIELD,
    required_fields=FIELD_SIZE_REQUIRED_FIELDS,
    replicates_per_field=400,
    nominal_alpha=0.005,
    alpha_name="alpha_geom",
    boundary=size_boundary(400, 0.005),
    field_reduction=FIELD_REDUCTION_NONE,
    pooling=POOLING_FORBIDDEN,
    final_combination=C2_FINAL_COMBINATION,
    primary_endpoint=C2_PRIMARY_ENDPOINT,
    authority_relationship=DERIVED,
)


def render_c2_scientific_purpose(rule: C2ReleaseRule = C2_RELEASE_RULE) -> str:
    """C2's purpose. GENERATED: the scope phrase comes from the canonical rule."""
    scope = ("per declared field" if rule.evaluation_scope == EVALUATION_SCOPE_PER_FIELD
             else rule.evaluation_scope)
    return f"Achieved P1 false-rejection rate {scope}, {C2_PURPOSE_COVERAGE}"


def render_c2_criterion(rule: C2ReleaseRule = C2_RELEASE_RULE) -> str:
    """C2's complete formal pass/fail criterion. GENERATED, not hand-kept."""
    pooled = "never pooled" if rule.pooling == POOLING_FORBIDDEN else "pooled"
    return (
        f"PER FIELD, {pooled}, R = {rule.replicates_per_field}, nominal "
        f"{rule.alpha_name} = {rule.nominal_alpha}. Inflation is detected iff "
        f"CP_lower(rejections, {rule.replicates_per_field}) > {rule.nominal_alpha}, "
        f"i.e. {rule.boundary + 1} or more rejections -> STATISTICAL_SIZE_FAILURE. "
        f"0-{rule.boundary} -> NO_SIGNIFICANT_SIZE_INFLATION_DETECTED, which means "
        "this experiment did not establish excess size, NOT that nominal size is "
        f"proved. {C2_CONTRACT_DIAGNOSTIC_SENTENCE}")


def render_c2_assurance(rule: C2ReleaseRule = C2_RELEASE_RULE) -> dict[str, Any]:
    """The GENERATED members of C2's assurance row."""
    return {
        "quantity": "P1 false-rejection rate, per field",
        "unit": "per_field",
        "pooling": rule.pooling,
        "acceptance_rule": (
            f"no inflation detected: CP_lower <= {rule.nominal_alpha}, i.e. <= "
            f"{rule.boundary}/{rule.replicates_per_field}, per field"),
    }


def render_c2_boundary_rule(rule: C2ReleaseRule = C2_RELEASE_RULE) -> str:
    """C2's section-12a derived-boundary prose. GENERATED."""
    return (f"0-{rule.boundary} rejections: no significant inflation detected; "
            f"{rule.boundary + 1}+ : STATISTICAL_SIZE_FAILURE")


def render_c2_pooling_statement(rule: C2ReleaseRule = C2_RELEASE_RULE) -> str:
    """C2's section-12a pooling sentence. GENERATED from the canonical rule."""
    return f"{rule.pooling} - every field is reported separately"


def render_c2_requirement(rule: C2ReleaseRule = C2_RELEASE_RULE,
                          index: int = 2) -> str:
    """C2's line in the final-campaign requirement list. GENERATED.

    C2 contributes FOUR required field-level conditions to the conjunctive final
    classification. That conjunction happens at CLASSIFICATION level and is NOT a
    replicate-wide EVERY_FIELD event: the four field assessments stay separate.
    """
    return (f"{index}. {rule.case_id[:2]} produces no STATISTICAL_SIZE_FAILURE in any "
            "required field")


def case_release_specification(contract: dict[str, Any], root: str) -> tuple[CaseRelease, ...]:
    """Build the frozen per-case release rules from authoritative records only."""
    req2 = parse_requirement(_require_frozen_text(contract, 2),
                             "synthetic_validation_requirements[2]")
    req3 = parse_requirement(_require_frozen_text(contract, 3),
                             "synthetic_validation_requirements[3]")
    _require_frozen_text(contract, 4)
    _require_frozen_text(contract, 5)
    _require_frozen_text(contract, 6)
    _require_frozen_text(contract, 7)
    if not design_declares_clopper_pearson_power(root):
        raise ContractReleaseBindingUnclassified(
            "prospective design section 15 item 4 no longer names Clopper-Pearson for "
            "the joint equivalence-power demonstration; C1's interval method has no "
            "authority source")
    p1 = contract["endpoints"]["P1_geometry"]
    criteria = contract["synthetic_validation_release_criteria"]
    g1 = criteria["G1_blinded_scale_control"]["campaign_criterion"]
    g2 = criteria["G2_false_bridge_discrimination"]["campaign_criterion"]
    g1_rule = parse_campaign_criterion(g1["bound"], "G1 campaign_criterion.bound")
    g2_rule = parse_campaign_criterion(g2["bound"], "G2 campaign_criterion.bound")
    r2, r3 = "synthetic_validation_requirements[2]", "synthetic_validation_requirements[3]"
    g1p = "synthetic_validation_release_criteria.G1_blinded_scale_control.campaign_criterion"
    g2p = "synthetic_validation_release_criteria.G2_false_bridge_discrimination.campaign_criterion"
    reporting = ("hypothetical_uncertainty_scenario.sigma_psi_deg_classification"
                 ".reporting_rule")
    no_pool = "FORBIDDEN"
    return (
        CaseRelease(
            "C1_true_bridge_complete", 0, "campaign",
            "COMPLETE_PIPELINE_P1_AND_P2_AND_P3_AND_P4",
            replicates=_c(req3.replicates, EXACT, CONTRACT, r3,
                          "the contract states R = 300 for the power demonstration"),
            method=_c(CLOPPER_PEARSON, EXACT, DESIGN, "section 15 item 4",
                      "the design names Clopper-Pearson where the contract JSON is terser"),
            sided=_c(req3.sided, EXACT, CONTRACT, r3, "stated literally"),
            level=_c(req3.level, EXACT, CONTRACT, r3, "stated literally"),
            direction=_c(req3.direction, EXACT, CONTRACT, r3, "stated literally"),
            comparison=_c(req3.comparison, EXACT, CONTRACT, r3, "stated literally"),
            target=_c(contract["complete_pipeline"]["target_true_bridge_success"], EXACT,
                      CONTRACT, "complete_pipeline.target_true_bridge_success",
                      "the adopted complete-pipeline release target"),
            pooling=_c(no_pool, EXACT, CONTRACT, reporting,
                       "G3 forbids pooling the secondary and stress orientation levels "
                       "into the primary >= 0.90 result"),
        ),
        CaseRelease(
            "C2_geometry_false_rejection", 1, "per_field",
            "P1_FALSE_REJECTION_RATE_PER_FIELD",
            replicates=_c(req2.replicates, EXACT, CONTRACT, r2,
                          "the contract states R = 400 for achieved joint gate size"),
            method=_c(req2.method, EXACT, CONTRACT, r2, "stated literally"),
            sided=_c(req2.sided, EXACT, CONTRACT, r2, "stated literally"),
            level=_c(req2.level, EXACT, CONTRACT, r2, "stated literally"),
            direction=_c(LOWER, DERIVED, CONTRACT, r2, INFLATION_DIRECTION_REASON),
            comparison=_c("<=", DERIVED, CONTRACT, r2,
                          "an inflation test accepts while the bound stays within alpha"),
            target=_c(p1["alpha_geom"], EXACT, CONTRACT, "endpoints.P1_geometry.alpha_geom",
                      "the nominal geometry-gate size the test is about"),
            # DERIVED, not EXACT. This repository defines EXACT as "the frozen
            # authority states this value literally", and no controlling document
            # states "pooling forbidden" for C2 -- the earlier validation plan does,
            # but that is the MACHINE PLAN layer, below the contract, and cannot be
            # the reason the rule derives from the contract. See
            # docs/e1a/E1A_V4_C2_POOLING_AUTHORITY_RECONSTRUCTION.md.
            pooling=_c(no_pool, DERIVED, CONTRACT, r2, C2_DERIVATION_REASON),
        ),
        CaseRelease(
            "C3_g5_block", 2, "per_field", "G5_BLOCK_SIZE",
            replicates=_c(req2.replicates, DERIVED, CONTRACT, r2, JOINT_GATE_R_REASON),
            method=_c(req2.method, DERIVED, CONTRACT, r2, JOINT_GATE_R_REASON),
            sided=_c(req2.sided, DERIVED, CONTRACT, r2, JOINT_GATE_R_REASON),
            level=_c(req2.level, DERIVED, CONTRACT, r2, CP_LEVEL_REASON),
            direction=_c(LOWER, DERIVED, CONTRACT, r2, INFLATION_DIRECTION_REASON),
            comparison=_c("<=", DERIVED, CONTRACT, r2,
                          "an inflation test accepts while the bound stays within alpha"),
            target=_c(p1["alpha_2"], EXACT, CONTRACT, "endpoints.P1_geometry.alpha_2",
                      "Block-2's nominal allocation in the two-block union rule"),
            pooling=_c(no_pool, CASE_SPECIFIC, PACKAGE, "authority_gaps.G4",
                       FIELD_REDUCTION_REASON),
        ),
        CaseRelease(
            "C4_surrogate_validity", 3, "per_field", "BLOCK1_ACHIEVED_SIZE",
            replicates=_c(2000, CASE_SPECIFIC, PACKAGE,
                          "synthetic_validation_requirements[4]", PACKAGE_R_REASON),
            method=_c(req2.method, DERIVED, CONTRACT, r2, CP_LEVEL_REASON),
            sided=_c(req2.sided, DERIVED, CONTRACT, r2, CP_LEVEL_REASON),
            level=_c(req2.level, DERIVED, CONTRACT, r2, CP_LEVEL_REASON),
            direction=_c(LOWER, DERIVED, CONTRACT, r2, INFLATION_DIRECTION_REASON),
            comparison=_c("<=", DERIVED, CONTRACT, r2,
                          "an inflation test accepts while the bound stays within alpha"),
            target=_c(p1["alpha_1"], EXACT, CONTRACT, "endpoints.P1_geometry.alpha_1",
                      "Block-1's nominal allocation, which the surrogate must not inflate"),
            pooling=_c(no_pool, CASE_SPECIFIC, PACKAGE, "authority_gaps.G4",
                       FIELD_REDUCTION_REASON),
        ),
        CaseRelease(
            "C5_plug_in_branch_a", 4, "per_cell", "P1_REJECTION_RATE_PER_CELL",
            replicates=_c(400, CASE_SPECIFIC, PACKAGE,
                          "synthetic_validation_requirements[5]", PACKAGE_R_REASON),
            method=_c(req2.method, DERIVED, CONTRACT, r2, CP_LEVEL_REASON),
            sided=_c(req2.sided, DERIVED, CONTRACT, r2, CP_LEVEL_REASON),
            level=_c(req2.level, DERIVED, CONTRACT, r2, CP_LEVEL_REASON),
            direction=_c(UPPER, DERIVED, CONTRACT, r2,
                         "the frozen achieved-size reporting form is a one-sided upper bound"),
            comparison=_c(REPORT_ONLY, EXACT, CONTRACT,
                          "synthetic_validation_requirements[5]",
                          "the contract requires the sweep to be VALIDATED and reported and "
                          "states no threshold; inventing one would be a new release rule"),
            target=_c(None, EXACT, CONTRACT, "synthetic_validation_requirements[5]",
                      "no frozen threshold exists for the plug-in sweep"),
            pooling=_c(no_pool, EXACT, CONTRACT, "synthetic_validation_requirements[5]",
                       "every one of the twelve declared cells is reported separately"),
        ),
        CaseRelease(
            "C6_mode_resolution_boundary", 5, "per_rho", "P1_REJECTION_RATE_PER_RHO",
            replicates=_c(req2.replicates, EXACT, CONTRACT, r2,
                          "the three declared rho are declared geometries"),
            method=_c(req2.method, EXACT, CONTRACT, r2, "stated literally"),
            sided=_c(req2.sided, EXACT, CONTRACT, r2, "stated literally"),
            level=_c(req2.level, EXACT, CONTRACT, r2, "stated literally"),
            direction=_c(req2.direction, EXACT, CONTRACT, r2, "stated literally"),
            comparison=_c(req2.comparison, EXACT, CONTRACT, r2, "stated literally"),
            target=_c(req2.target, EXACT, CONTRACT, r2, "stated literally as <= 3%"),
            pooling=_c(no_pool, EXACT, CONTRACT, "synthetic_validation_requirements[6]",
                       "size and power are demonstrated AT each declared rho"),
        ),
        CaseRelease(
            "C7_false_bridge", 6, "per_alternative",
            "P2_INTERSECTION_UNION_AND_P3_ALL_FIELD_ABSOLUTE",
            replicates=_c(g2["replicates_per_alternative"], EXACT, CONTRACT,
                          f"{g2p}.replicates_per_alternative", "stated literally"),
            method=_c(g2_rule.method, EXACT, CONTRACT, f"{g2p}.bound", "stated literally"),
            sided=_c(g2_rule.sided, EXACT, CONTRACT, f"{g2p}.bound", "stated literally"),
            level=_c(g2_rule.level, EXACT, CONTRACT, f"{g2p}.bound", "stated literally"),
            direction=_c(g2_rule.direction, EXACT, CONTRACT, f"{g2p}.bound",
                         "stated literally"),
            comparison=_c("<=", EXACT, CONTRACT, f"{g2p}.target",
                          "a false-acceptance ceiling is an upper limit"),
            target=_c(g2["target"], EXACT, CONTRACT, f"{g2p}.target", "stated literally"),
            pooling=_c(no_pool, EXACT, CONTRACT,
                       "synthetic_validation_release_criteria."
                       "G2_false_bridge_discrimination.independence",
                       "each declared alternative must INDEPENDENTLY satisfy the rule"),
        ),
        CaseRelease(
            "C8_blinded_scale_control", 7, "campaign",
            "P3_EQUIVALENT_TRANSFORMED_BETA_RECOVERY",
            replicates=_c(g1["replicates"], EXACT, CONTRACT, f"{g1p}.replicates",
                          "stated literally"),
            method=_c(g1_rule.method, EXACT, CONTRACT, f"{g1p}.bound", "stated literally"),
            sided=_c(g1_rule.sided, EXACT, CONTRACT, f"{g1p}.bound", "stated literally"),
            level=_c(g1_rule.level, EXACT, CONTRACT, f"{g1p}.bound", "stated literally"),
            direction=_c(g1_rule.direction, EXACT, CONTRACT, f"{g1p}.bound",
                         "stated literally"),
            comparison=_c(">=", EXACT, CONTRACT, f"{g1p}.target",
                          "a paired-control success target is a lower limit"),
            target=_c(g1["target"], EXACT, CONTRACT, f"{g1p}.target", "stated literally"),
            pooling=_c("NOT_APPLICABLE", NOT_APPLICABLE, CONTRACT, f"{g1p}.replicates",
                       "C8 reports one paired-control success count"),
        ),
    )


_CRITERION_PATTERN = re.compile(
    r"^(?P<sided>one-sided) (?P<level>\d+)% (?P<method>Clopper-Pearson) "
    r"(?P<direction>LOWER|UPPER)$")


def parse_campaign_criterion(text: str, what: str) -> ParsedRequirement:
    """Read the G1/G2 `bound` sentence, refusing anything it does not state."""
    match = _CRITERION_PATTERN.match(text)
    if match is None:
        raise ContractReleaseBindingUnclassified(
            f"{what}: {text!r} is not a parseable one-sided Clopper-Pearson rule")
    return ParsedRequirement(
        method=match.group("method"), sided=match.group("sided"),
        level=float(match.group("level")) / 100.0, direction=match.group("direction"),
        comparison="", target=float("nan"), replicates=0)


# --------------------------------------------------- derived integer boundaries
@functools.lru_cache(maxsize=None)
def derived_boundary(direction: str, comparison: str, replicates: int,
                     target: float | None) -> tuple[int | None, str]:
    """Recompute an integer pass boundary from its frozen statistical inputs.

    Memoised because it is PURE: the same frozen inputs always derive the same
    integer. Caching a derivation is not caching an authority -- the inputs are
    re-read from the contract on every call, so a changed input is a cache MISS
    and is recomputed.
    """
    if comparison == REPORT_ONLY or target is None:
        return None, "no frozen threshold: the requirement is to REPORT, not to gate"
    key = (direction, comparison)
    if key not in BOUNDARY_RULES:
        raise ContractReleaseDerivedThresholdMismatch(
            f"no derivation rule for a {direction} bound compared {comparison}")
    description, fn = BOUNDARY_RULES[key]
    return fn(replicates, target), description


# --------------------------------------------------------- mandatory reporting
def mandatory_diagnostics(contract: dict[str, Any]) -> tuple[MandatoryDiagnostic, ...]:
    """Everything frozen authority requires a completed campaign to REPORT.

    Derived from the contract's own requirements, not hand-picked: each row names
    the authority path that makes it mandatory.
    """
    for index in (4, 5, 6, 7, 8, 9):
        _require_frozen_text(contract, index)
    return (
        MandatoryDiagnostic(
            "C2_CONTRACT_COARSE_UPPER_BOUND", "C2_geometry_false_rejection", CONTRACT,
            "synthetic_validation_requirements[2]",
            "one-sided 95% Clopper-Pearson UPPER bound on the P1 rejection rate, per "
            "required field, compared with the contract threshold 0.03",
            "contract_diagnostics", ("per_field",)),
        MandatoryDiagnostic(
            "C3_G5_DELTA_METHOD_ERROR", "C3_g5_block", CONTRACT,
            "synthetic_validation_requirements[7]",
            "measured sd(g2) against the leading-order 24 A4 / n prediction",
            "g5_diagnostics", ("measured_sd_g2", "leading_order_prediction")),
        MandatoryDiagnostic(
            "C4_OPERATING_QUANTILE_DISCREPANCY", "C4_surrogate_validity", CONTRACT,
            "synthetic_validation_requirements[4]",
            "the observed operating-quantile discrepancy and the full two-sided "
            "interval, which the binary inflation diagnostic does not replace",
            "contract_diagnostics", ("operating_quantile_discrepancy", "two_sided_interval")),
        MandatoryDiagnostic(
            "C5_PER_CELL_UPPER_BOUND", "C5_plug_in_branch_a", CONTRACT,
            "synthetic_validation_requirements[5]",
            "the one-sided 95% Clopper-Pearson UPPER bound in EVERY one of the twelve "
            "declared cells; no cell may be dropped after inspection",
            "contract_diagnostics", ("per_cell",)),
        MandatoryDiagnostic(
            "C6_MERGE_SPLIT_DECISION_RATE", "C6_mode_resolution_boundary", CONTRACT,
            "synthetic_validation_requirements[6]",
            "the merge/split decision rate at each declared rho -- the POWER half of "
            "the theta_cap requirement, which the size criterion does not cover",
            "mode_resolution_behaviour", ("per_rho",)),
        MandatoryDiagnostic(
            "JOB_STATUS_RECONCILIATION", None, CONTRACT,
            "synthetic_validation_requirements[8]",
            "jobs declared = jobs completed + jobs refused, with a per-status count",
            "refusals_by_reason", ()),
        MandatoryDiagnostic(
            "UNCONDITIONAL_COMPLETE_PIPELINE_SUCCESS", "C1_true_bridge_complete", CONTRACT,
            "synthetic_validation_requirements[9]",
            "complete-pipeline success reported UNCONDITIONALLY, with structured "
            "refusals counted as failures",
            "denominator_rule", ()),
    )


def require_c2_contract_diagnostic(diagnostic: Any, replicates: int,
                                   fields: tuple[str, ...]) -> None:
    """Validate the C2 coarse upper-bound diagnostic against its raw counts.

    A present-but-wrong diagnostic is as bad as a missing one, so every bound is
    RECOMPUTED from the count the same record carries.
    """
    if not isinstance(diagnostic, dict) or "per_field" not in diagnostic:
        raise ContractMandatoryDiagnosticMissing(
            "C2_CONTRACT_COARSE_UPPER_BOUND: the aggregate carries no per-field "
            "coarse upper-bound diagnostic, which "
            "synthetic_validation_requirements[2] requires")
    per_field = diagnostic["per_field"]
    if not isinstance(per_field, dict) or set(per_field) != set(fields):
        raise ContractMandatoryDiagnosticMissing(
            f"C2_CONTRACT_COARSE_UPPER_BOUND: per-field rows {sorted(per_field) if isinstance(per_field, dict) else per_field!r} "
            f"!= required fields {sorted(fields)}")
    for field_id, row in sorted(per_field.items()):
        for key in ("rejections", "replicates", "cp_upper", "threshold", "direction",
                    "confidence_level", "pass"):
            if key not in row:
                raise ContractMandatoryDiagnosticMissing(
                    f"C2_CONTRACT_COARSE_UPPER_BOUND[{field_id}]: missing {key!r}")
        if row["replicates"] != replicates:
            raise ContractMandatoryDiagnosticMismatch(
                f"C2_CONTRACT_COARSE_UPPER_BOUND[{field_id}]: diagnostic R "
                f"{row['replicates']} != declared R {replicates}")
        if row["direction"] != UPPER:
            raise ContractMandatoryDiagnosticMismatch(
                f"C2_CONTRACT_COARSE_UPPER_BOUND[{field_id}]: the contract requires an "
                f"UPPER bound, the diagnostic reports {row['direction']!r}")
        if row["confidence_level"] != 0.95:
            raise ContractMandatoryDiagnosticMismatch(
                f"C2_CONTRACT_COARSE_UPPER_BOUND[{field_id}]: the contract requires a "
                f"95% level, the diagnostic reports {row['confidence_level']!r}")
        if row["threshold"] != GROSS_INFLATION_TOLERANCE:
            raise ContractMandatoryDiagnosticMismatch(
                f"C2_CONTRACT_COARSE_UPPER_BOUND[{field_id}]: threshold "
                f"{row['threshold']!r} != the contract's {GROSS_INFLATION_TOLERANCE}")
        recomputed = cp_upper(row["rejections"], row["replicates"])
        if abs(row["cp_upper"] - recomputed) > 1e-12:
            raise ContractMandatoryDiagnosticMismatch(
                f"C2_CONTRACT_COARSE_UPPER_BOUND[{field_id}]: reported bound "
                f"{row['cp_upper']!r} is not cp_upper({row['rejections']}, "
                f"{row['replicates']}) = {recomputed!r}")
        if row["pass"] is not (recomputed <= GROSS_INFLATION_TOLERANCE):
            raise ContractMandatoryDiagnosticMismatch(
                f"C2_CONTRACT_COARSE_UPPER_BOUND[{field_id}]: PASS/FAIL {row['pass']!r} "
                f"disagrees with {recomputed!r} <= {GROSS_INFLATION_TOLERANCE}")


def require_mandatory_diagnostics(aggregate: dict[str, Any], plan: dict[str, Any],
                                  fields: tuple[str, ...]) -> None:
    """A completed campaign result is not structurally valid without these.

    Deterministic fixtures only: this validates a RESULT DOCUMENT's shape and
    internal arithmetic. It executes nothing.
    """
    case_id = aggregate.get("case_id")
    required = [d for d in mandatory_diagnostics_for(plan, case_id)]
    if not required:
        return
    for diagnostic in required:
        value = aggregate.get(diagnostic.aggregate_key)
        if value in (None, {}, []):
            raise ResultSchemaInvalid(
                f"RESULT_SCHEMA_INVALID: {case_id} omits {diagnostic.aggregate_key!r}, "
                f"required by {diagnostic.authority_path} "
                f"({diagnostic.diagnostic_id})")
        for key in diagnostic.required_keys:
            if not isinstance(value, dict) or key not in value:
                raise ResultSchemaInvalid(
                    f"RESULT_SCHEMA_INVALID: {case_id} {diagnostic.aggregate_key}"
                    f".{key} is required by {diagnostic.authority_path} "
                    f"({diagnostic.diagnostic_id})")
    if case_id == "C2_geometry_false_rejection":
        replicates = next(c["replicate_count"] for c in plan["cases"]
                          if c["case_id"] == case_id)
        require_c2_contract_diagnostic(aggregate["contract_diagnostics"],
                                       replicates, fields)


def mandatory_diagnostics_for(plan: dict[str, Any],
                              case_id: str | None) -> tuple[MandatoryDiagnostic, ...]:
    """The mandatory diagnostics a given case's aggregate must carry."""
    declared = plan["release_authority"]["mandatory_diagnostics"]
    return tuple(MandatoryDiagnostic(
        row["diagnostic_id"], row["case_id"], row["authority_source"],
        row["authority_path"], row["requirement"], row["aggregate_key"],
        tuple(row["required_keys"]))
        for row in declared if row["case_id"] == case_id)


# ------------------------------------------------------- IMPLIED_STRONGER proof
def c2_implication_range(contract: dict[str, Any]) -> tuple[int, ...]:
    """Every count the adopted C2 rule ACCEPTS. Finite and enumerable."""
    req2 = parse_requirement(_require_frozen_text(contract, 2),
                             "synthetic_validation_requirements[2]")
    alpha = contract["endpoints"]["P1_geometry"]["alpha_geom"]
    return tuple(range(size_boundary(req2.replicates, alpha) + 1))


def require_c2_implies_contract_diagnostic(contract: dict[str, Any]) -> None:
    """Prove the adopted C2 rule is strictly stronger than the contract's.

    Two independent arguments, both required:

    1. ENUMERATION over the frozen accepting range 0..5 -- six counts, checked.
    2. MONOTONICITY: cp_upper(k, n) is strictly increasing in k, so establishing
       the implication at the largest accepted count establishes it for all
       smaller ones. The monotonicity itself is checked over the accepting range
       plus one, which is where it is relied upon.

    Passing the adopted rule therefore IMPLIES the older contract requirement. The
    older requirement is NOT thereby erased: it remains a MANDATORY DIAGNOSTIC.
    """
    req2 = parse_requirement(_require_frozen_text(contract, 2),
                             "synthetic_validation_requirements[2]")
    accepted = c2_implication_range(contract)
    for k in accepted:
        bound = cp_upper(k, req2.replicates)
        if bound > req2.target:
            raise ContractReleaseImplicationBroken(
                f"the adopted C2 rule accepts {k}/{req2.replicates}, whose one-sided "
                f"95% CP upper bound {bound!r} exceeds the contract's {req2.target!r}: "
                "the adopted rule is NOT stronger and the contract requirement would "
                "be silently weakened")
    for k in accepted:
        if not cp_upper(k, req2.replicates) < cp_upper(k + 1, req2.replicates):
            raise ContractReleaseImplicationBroken(
                f"cp_upper is not strictly increasing at k={k}, so the implication "
                "cannot be extended from the boundary count by monotonicity")


# ------------------------------------------------------------ the binding rows
def _leaf_items(value, prefix: str) -> list[tuple[str, Any]]:
    """Every leaf of a frozen subtree, as (dotted suffix, value)."""
    if isinstance(value, dict):
        return [item for key, child in value.items()
                for item in _leaf_items(child, f"{prefix}.{key}")]
    return [(prefix, value)]


def _at(obj: Any, path: str) -> Any:
    for part in path.split(".")[1:]:
        if not isinstance(obj, dict) or part not in obj:
            return None
        obj = obj[part]
    return obj


def _numbers_in(text: str) -> list[float]:
    return [float(t) for t in re.findall(r"\d+(?:\.\d+)?", text)]



#: EXACT approved text of every remaining string-valued field in the two C3/C4
#: case records that no renderer generates.
#:
#: Free prose is the whole attack surface. The fourth audit showed that a field
#: classified "explanatory" and guarded by a keyword list is not guarded at all,
#: because natural language states a release rule without the listed words. The
#: guarantee therefore cannot be "the text avoids suspicious vocabulary"; it has
#: to be "there is no free text". Every string in a controlled C3/C4 record is now
#: either GENERATED from the canonical rule or pinned here and compared exactly.
#:
#: Several of these strings belong to OTHER dispositions -- the frozen scientific
#: purpose, G3 seed-family grants, calibration scope. Pinning them does not move
#: their authority here: the pin is a TRIPWIRE asserting the text this stage was
#: built against. A later authorised amendment to one of those dispositions must
#: update its pin deliberately, which is the intended behaviour, not a conflict.
CASE_PROSE_PINS = {
    "C3_g5_block": {
        "case_id": 'C3_g5_block',
        "scientific_purpose": (
            'Validate the actual G5 block from full generated observations: '
            'sample-mean centring, A4-based leading-order variance, finite-sample '
            'behaviour, correlation, the two-mode max statistic and its '
            'interaction with the two-block gate'
        ),
        "v4_classification": 'NEWLY REQUIRED BY AN ADOPTED V4 CORRECTION',
        "authority": 'design section 15 item 8',
        "truth_model": (
            'true null; G5 computed from generated trajectories, never as an '
            'independent companion variable'
        ),
        "geometry_truth": 'as declared per field',
        "branch_a_uncertainty": (
            'frozen candidate scenario: sigma_k = 0.34%, sigma_cm = 1.15%, '
            'sigma_T = 0.1 K; sigma_psi PRIMARY = 0.5 deg, with 0.0/0.2 deg '
            'secondary and 1.0 deg stress, reported separately and never pooled '
            '[disposition G3]'
        ),
        "branch_b_process": (
            'declared correlated OU, exact transition, stationary initialisation '
            'x0 ~ N(x*, Sigma_theta)'
        ),
        "expected_qualitative_outcome": (
            'block-2 achieved size consistent with alpha_2 = 0.1%; delta-method '
            'error quantified'
        ),
        "seed_family": 'validation',
        "role": 'primary',
        "v4_classification_note": '',
        "allowed_seed_families_rationale": (
            'REPLICATE-CONDITIONAL CALIBRATION: this case evaluates a P1 / '
            'Block-1 quantity and builds its own artifact per subcondition, '
            'replicate and field. Branch-A measurement is realised per replicate '
            'from its own family.'
        ),
        "allowed_seed_families_authority": (
            'derived from the frozen generator design (generating_model.branch_a, '
            'truth_visibility) and disposition G3; not invented for this repair'
        ),
        "branch_a_uncertainty_status": 'STOCHASTIC_PER_REPLICATE',
        "calibration_scope": 'REPLICATE_CONDITIONAL',
        "calibration_artifact_basis": (
            '400 replicates x 4 subconditions x 4 fields requiring calibration = '
            '6,400'
        ),
        "calibration_scope_rationale": (
            'the declared Branch-A uncertainty scenario is REALISED per replicate '
            'from the branch_a_measurement family, so H_A and therefore the '
            'Block-1 null law differ between replicates. One nominal per-field '
            'artifact would analyse independently realised conditions against a '
            'null that belongs to none of them.'
        ),
    },
    "C4_surrogate_validity": {
        "case_id": 'C4_surrogate_validity',
        "scientific_purpose": (
            'Achieved Block-1 size when calibration uses the covariance-matched '
            'surrogate but validation data come from the declared actual '
            'correlated process; measure the OPERATING-QUANTILE discrepancy, not '
            'covariance agreement'
        ),
        "v4_classification": 'NEWLY REQUIRED BY AN ADOPTED V4 CORRECTION',
        "authority": (
            'design section 15 item 5; design Appendix classification of the '
            'surrogate as an APPROXIMATION'
        ),
        "truth_model": (
            'calibration from the surrogate, validation from the declared OU '
            'process'
        ),
        "geometry_truth": 'as declared per field',
        "branch_a_uncertainty": (
            'frozen candidate scenario: sigma_k = 0.34%, sigma_cm = 1.15%, '
            'sigma_T = 0.1 K'
        ),
        "branch_b_process": (
            'declared correlated OU, exact transition, stationary initialisation '
            'x0 ~ N(x*, Sigma_theta)'
        ),
        "expected_qualitative_outcome": 'achieved Block-1 rejection rate close to alpha_1 = 0.4%',
        "seed_family": 'calibration + validation',
        "role": 'primary',
        "v4_classification_note": '',
        "allowed_seed_families_rationale": (
            'REPLICATE-CONDITIONAL CALIBRATION: this case evaluates a P1 / '
            'Block-1 quantity and builds its own artifact per subcondition, '
            'replicate and field. Branch-A measurement is realised per replicate '
            'from its own family.'
        ),
        "allowed_seed_families_authority": (
            'derived from the frozen generator design (generating_model.branch_a, '
            'truth_visibility) and disposition G3; not invented for this repair'
        ),
        "branch_a_uncertainty_status": 'STOCHASTIC_PER_REPLICATE',
        "calibration_scope": 'REPLICATE_CONDITIONAL',
        "calibration_artifact_basis": (
            '2000 replicates x 1 subconditions x 4 fields requiring calibration = '
            '8,000'
        ),
        "calibration_scope_rationale": (
            'the declared Branch-A uncertainty scenario is REALISED per replicate '
            'from the branch_a_measurement family, so H_A and therefore the '
            'Block-1 null law differ between replicates. One nominal per-field '
            'artifact would analyse independently realised conditions against a '
            'null that belongs to none of them.'
        ),
    },
}


#: Top-level `size_validation_semantics` prose. These two strings are SHARED by
#: C2, C3 and C4, and `detector` states the size-detection rule itself, so leaving
#: them editable would leave a rule-bearing free string reachable from the C3/C4
#: surface.
#:
#: Pinning them is a tripwire on the text, nothing more. It changes no C2 science
#: and it does NOT repair or mask the confirmed C2 residual, which is a different
#: defect: `derived_boundaries.C2.pooling` carries no binding to a canonical
#: pooling rule. That remains open and deferred to its own bounded task.
SHARED_SIZE_SEMANTICS_PINS = {
    "status": "FROZEN PROSPECTIVELY, before any random outcome exists",
    "detector": ("STATISTICAL SIZE INFLATION is detected iff CP_lower(rejections, "
                 "R) > nominal alpha"),
}


#: The COMPLETE final-campaign requirement sequence. ORDER IS NORMATIVE:
#: every line carries its own ordinal, and the Markdown renders them as a
#: numbered list, so position is part of the statement. Slots 3 and 4 are
#: GENERATED from the canonical C3/C4 rule; the rest are exact pins of other
#: cases' approved text, held here as tripwires so the LIST ITSELF -- its
#: length, membership and order -- is authority rather than a bag the
#: candidate may add to.
_GENERATED_REQUIREMENT_SLOTS = (1, 2, 3)

FINAL_CAMPAIGN_REQUIREMENT_PINS = {
    0: (
        '1. C1 complete-pipeline success: CP lower >= 0.90 over R = 300 '
        '(>= 279/300)'
    ),
    # 1: GENERATED from C2_RELEASE_RULE (render_c2_requirement)
    # 2: GENERATED from FIELD_SIZE_RULES (render_field_size_requirement)
    # 3: GENERATED from FIELD_SIZE_RULES (render_field_size_requirement)
    4: '5. C5 satisfies its already-frozen plug-in Branch-A criterion',
    5: '6. C6 satisfies its already-frozen mode-resolution criterion',
    6: (
        '7. EVERY C7 false-bridge alternative satisfies G2: CP upper <= '
        '0.025 (<= 4/400)'
    ),
    7: '8. C8 satisfies G1: CP lower >= 0.90 over R = 200 (>= 188/200)',
    8: (
        '9. no SOFTWARE_OR_INVARIANT_FAILURE, CALIBRATION_FAILURE, '
        'NUMERICAL_OR_PRECISION_FAILURE occurs'
    ),
    9: (
        '10. structured refusals counted exactly per the already-frozen '
        'unconditional denominator rule'
    ),
    10: (
        '11. every MANDATORY CONTRACT DIAGNOSTIC declared in '
        'release_authority.mandatory_diagnostics is present in the '
        'campaign result and consistent with its own raw counts; an '
        'absent or inconsistent mandatory diagnostic is '
        'RESULT_SCHEMA_INVALID'
    ),
}

#: Membership-bearing lists in the C3/C4 case records that no renderer
#: generates. Owned by other dispositions (G3 seed grants, the declared
#: subcondition set); pinned as tripwires so elements cannot be added,
#: removed or reordered without an explicit authorised update here.
CASE_LIST_PINS = {
    "C3_g5_block": {
        "allowed_seed_families": ['calibration', 'validation', 'branch_a_measurement'],
        "subconditions": [
            {'subcondition_id': 'sigma_psi_0p0', 'sigma_psi_deg': 0.0, 'g3_role': 'SECONDARY', 'feeds_primary_claim': False},
            {'subcondition_id': 'sigma_psi_0p2', 'sigma_psi_deg': 0.2, 'g3_role': 'SECONDARY', 'feeds_primary_claim': False},
            {'subcondition_id': 'sigma_psi_0p5', 'sigma_psi_deg': 0.5, 'g3_role': 'PRIMARY', 'feeds_primary_claim': True},
            {'subcondition_id': 'sigma_psi_1p0', 'sigma_psi_deg': 1.0, 'g3_role': 'STRESS', 'feeds_primary_claim': False},
        ],
    },
    "C4_surrogate_validity": {
        "allowed_seed_families": ['calibration', 'validation', 'branch_a_measurement'],
        "subconditions": [
            {'subcondition_id': 'primary'},
        ],
    },
}




#: C2's remaining case strings and membership-bearing lists. Exact pins, the same
#: tripwire treatment the C3/C4 records carry: they belong to other dispositions
#: (the frozen purpose, G3 seed grants, calibration scope) and are frozen here so
#: none can quietly acquire release semantics.
C2_CASE_PROSE_PINS = {
    "v4_classification": 'RETAINED BUT UPDATED FOR V4',
    "authority": 'design section 15 item 3',
    "truth_model": 'true null K_theta = H_theta',
    "geometry_truth": 'as declared per field',
    "branch_a_uncertainty": (
        'frozen candidate scenario: sigma_k = 0.34%, sigma_cm = 1.15%, '
        'sigma_T = 0.1 K; sigma_psi PRIMARY = 0.5 deg, with 0.0/0.2 deg '
        'secondary and 1.0 deg stress, reported separately and never '
        'pooled [disposition G3]'
    ),
    "branch_b_process": (
        'declared correlated OU, exact transition, stationary '
        'initialisation x0 ~ N(x*, Sigma_theta)'
    ),
    "expected_qualitative_outcome": 'false rejection at or below alpha_geom = 0.5%',
    "seed_family": 'validation',
    "role": 'primary',
    "v4_classification_note": 'alpha_geom 1% -> 0.5%, two-block union rule',
    "allowed_seed_families_rationale": (
        'REPLICATE-CONDITIONAL CALIBRATION: this case evaluates a P1 / '
        'Block-1 quantity and builds its own artifact per subcondition, '
        'replicate and field. Branch-A measurement is realised per '
        'replicate from its own family.'
    ),
    "allowed_seed_families_authority": (
        'derived from the frozen generator design '
        '(generating_model.branch_a, truth_visibility) and disposition '
        'G3; not invented for this repair'
    ),
    "branch_a_uncertainty_status": 'STOCHASTIC_PER_REPLICATE',
    "calibration_scope": 'REPLICATE_CONDITIONAL',
    "calibration_artifact_basis": (
        '400 replicates x 4 subconditions x 4 fields requiring '
        'calibration = 6,400'
    ),
    "calibration_scope_rationale": (
        'the declared Branch-A uncertainty scenario is REALISED per '
        'replicate from the branch_a_measurement family, so H_A and '
        'therefore the Block-1 null law differ between replicates. One '
        'nominal per-field artifact would analyse independently realised '
        'conditions against a null that belongs to none of them.'
    ),
}

C2_CASE_LIST_PINS = {
    "allowed_seed_families": ['calibration', 'validation', 'branch_a_measurement'],
    "subconditions": [
        {'subcondition_id': 'sigma_psi_0p0', 'sigma_psi_deg': 0.0, 'g3_role': 'SECONDARY', 'feeds_primary_claim': False},
        {'subcondition_id': 'sigma_psi_0p2', 'sigma_psi_deg': 0.2, 'g3_role': 'SECONDARY', 'feeds_primary_claim': False},
        {'subcondition_id': 'sigma_psi_0p5', 'sigma_psi_deg': 0.5, 'g3_role': 'PRIMARY', 'feeds_primary_claim': True},
        {'subcondition_id': 'sigma_psi_1p0', 'sigma_psi_deg': 1.0, 'g3_role': 'STRESS', 'feeds_primary_claim': False},
    ],
}


@dataclass(frozen=True)
class NormativeSurface:
    """ONE authoritative C3/C4 statement and how it is held to the canonical rule.

    The registry of these is TOTAL over the controlled containers: every key the
    plan carries inside one of them must appear here with a classification, so a
    new authoritative field cannot be added silently and go unchecked. That
    totality is the actual repair; binding individual strings as each audit names
    them has now failed twice.
    """

    case: str
    component: str
    container: str
    key: str
    mode: str
    #: Where the Markdown renders it. Every region listed here is a byte-exact
    #: re-render of the JSON, so a contradicting edit must appear in both.
    markdown: str
    expected: Any = None
    actual: Any = None

    @property
    def path(self) -> str:
        return f"{self.container}.{self.key}"


#: Key-name fragments that mark a field-structure RULE rather than some other
#: declaration. A key carrying one of these inside a C3/C4 case must be
#: registered: this is what stops a future `field_reduction` or `pooling`
#: attribute from appearing beside the registry instead of inside it.
FIELD_RULE_KEY_TOKENS = ("pool", "compensat", "reduction", "field_structure",
                         "any_field", "every_field", "elementary_event",
                         "release_rule", "field_condition")

#: SECONDARY DIAGNOSTIC ONLY -- NOT the safety guarantee.
#:
#: This list was once the guard on the single explanatory location, and the fourth
#: independent audit defeated it in one sentence: "The full P1 verdict is the
#: deciding condition for C3." states the rule and contains none of these words. No
#: finite vocabulary can decide whether free prose has become rule-bearing, and
#: lengthening the list only moves the boundary.
#:
#: The guarantee is now structural instead: no semantically free text exists in the
#: controlled C3/C4 surface at all (`require_field_size_surface_totality`), so
#: there is nothing left for a vocabulary check to protect. It is retained only as
#: a cheap tripwire that would fire if some future entry were ever classified
#: NON_NORMATIVE_EXPLANATION again.
FIELD_RULE_PROSE_TOKENS = ("pool", "compensat", "reduction", "field",
                           "any one", "every one", "reference-field")


def _surface(case, component, container, key, mode, markdown, expected, holder):
    return NormativeSurface(case, component, container, key, mode, markdown,
                            expected, (holder or {}).get(key))


def normative_surface_registry(plan: dict[str, Any]) -> tuple[NormativeSurface, ...]:
    """EVERY authoritative C3/C4 statement, each bound to the canonical rule.

    Built from `FIELD_SIZE_RULES` and the renderers above -- never from the plan
    text being checked -- so a contradicting edit cannot justify itself.
    """
    out: list[NormativeSurface] = []
    add = out.append

    # ------------------------------------------------- the G4 disposition record
    gaps = {gap.get("id"): gap for gap in plan.get("authority_gaps", [])}
    gap = gaps.get(FIELD_SIZE_DISPOSITION_ID) or {}
    gid = f"authority_gaps.{FIELD_SIZE_DISPOSITION_ID}"
    for key, mode, expected in (
            ("id", STRICTLY_VERIFIED_DUPLICATE, FIELD_SIZE_DISPOSITION_ID),
            ("status", STRICTLY_VERIFIED_DUPLICATE, FIELD_SIZE_DISPOSITION_STATUS),
            ("affects", STRICTLY_VERIFIED_DUPLICATE, FIELD_SIZE_DISPOSITION_AFFECTS),
            ("gap", GENERATED_FROM_CANONICAL, render_field_size_gap_statement()),
            ("resolution", GENERATED_FROM_CANONICAL, render_field_size_disposition())):
        add(_surface("G4", f"disposition {key}", gid, key, mode,
                     "generated release-rules region", expected, gap))

    # ------------------------------------------------- the G5 disposition record
    refusal_gap = gaps.get(REFUSAL_DISPOSITION_ID) or {}
    rid = f"authority_gaps.{REFUSAL_DISPOSITION_ID}"
    for key, mode, expected in (
            ("id", STRICTLY_VERIFIED_DUPLICATE, REFUSAL_DISPOSITION_ID),
            ("status", STRICTLY_VERIFIED_DUPLICATE, REFUSAL_DISPOSITION_STATUS),
            ("affects", STRICTLY_VERIFIED_DUPLICATE, REFUSAL_DISPOSITION_AFFECTS),
            ("gap", GENERATED_FROM_CANONICAL, render_refusal_gap_statement()),
            ("resolution", GENERATED_FROM_CANONICAL, render_refusal_disposition())):
        add(_surface("G5", f"disposition {key}", rid, key, mode,
                     "generated release-rules region", expected, refusal_gap))

    cases = {case.get("case_id"): (i, case) for i, case in enumerate(plan["cases"])}
    assurance = {row.get("case_id"): row for row in plan["assurance"]}
    boundaries = plan["size_validation_semantics"]["derived_boundaries"]

    for rule in FIELD_SIZE_RULES:
        short = rule.case_id[:2]
        index, case = cases.get(rule.case_id, (None, {}))

        # --------------------------------------- case-level field-size statements
        cp = f"cases[{index}]"
        for key, mode, expected in (
                ("fields_affected", GENERATED_FROM_CANONICAL,
                 list(rule.required_fields)),
                ("primary_release_endpoint", GENERATED_FROM_CANONICAL,
                 rule.primary_endpoint),
                ("formal_pass_fail_criterion", GENERATED_FROM_CANONICAL,
                 render_field_size_criterion(rule)),
                ("replicate_count", STRICTLY_VERIFIED_DUPLICATE, rule.replicates)):
            add(_surface(short, key, cp, key, mode, "generated cases region",
                         expected, case))
        add(_surface(short, "block-1 role", cp, "block1_role",
                     GENERATED_FROM_CANONICAL, "generated cases region",
                     render_field_size_block1_role(rule), case))
        for key, expected in CASE_PROSE_PINS.get(rule.case_id, {}).items():
            add(_surface(short, f"pinned case prose {key}", cp, key,
                         STRICTLY_VERIFIED_DUPLICATE, "generated cases region",
                         expected, case))

        # ------------------------------------------------- the semantics container
        sp = f"{cp}.{rule.semantics_key}"
        semantics = case.get(rule.semantics_key) or {}
        for key, expected in render_field_size_semantics(rule).items():
            add(_surface(short, key, sp, key, GENERATED_FROM_CANONICAL,
                         "generated cases region", expected, semantics))
        if rule.secondary_feeds_primary_release is not None:
            add(_surface(short, "secondary feeds primary release", sp,
                         "joint_p1_result_changes_C3_release_verdict",
                         GENERATED_FROM_CANONICAL, "generated cases region",
                         rule.secondary_feeds_primary_release, semantics))
        if rule.earlier_status is not None:
            add(_surface(short, "earlier disposition status", sp, "status",
                         STRICTLY_VERIFIED_DUPLICATE, "generated cases region",
                         rule.earlier_status, semantics))
        # Driven by the CANONICAL rule, not by which keys the candidate happens
        # to carry. Registering only what is present means deleting a key also
        # deletes its check -- the mirror of the r8 deferred-scope escape.
        if rule.secondary_diagnostic is not None:
            add(_surface(short, "block-1 calibration retained", sp,
                         "requires_block1_calibration", STRICTLY_VERIFIED_DUPLICATE,
                         "generated cases region", True, semantics))
            # GENERATED, not explanatory. See
            # render_field_size_calibration_rationale for why free prose here was
            # an escape and why a keyword guard could not have closed it.
            add(_surface(short, "calibration rationale", sp,
                         "why_calibration_is_retained", GENERATED_FROM_CANONICAL,
                         "generated cases region",
                         render_field_size_calibration_rationale(rule), semantics))
        for key, expected in CASE_LIST_PINS.get(rule.case_id, {}).items():
            add(_surface(short, f"pinned case list {key}", cp, key,
                         STRICTLY_VERIFIED_DUPLICATE, "generated cases region",
                         expected, case))

        # ------------------------------------------------ the assurance container
        ap = f"assurance[{rule.case_id}]"
        row = assurance.get(rule.case_id) or {}
        for key, expected in render_field_size_assurance(rule).items():
            add(_surface(short, f"assurance {key}", ap, key,
                         GENERATED_FROM_CANONICAL, "generated assurance region",
                         expected, row))
        for key, mode, expected in (
                ("case_id", STRICTLY_VERIFIED_DUPLICATE, rule.case_id),
                ("target", GENERATED_FROM_CANONICAL, render_field_size_target(rule)),
                ("target_value", STRICTLY_VERIFIED_DUPLICATE, rule.nominal_alpha),
                ("comparison", STRICTLY_VERIFIED_DUPLICATE, FIELD_SIZE_COMPARISON),
                ("confidence_level", STRICTLY_VERIFIED_DUPLICATE,
                 FIELD_SIZE_CONFIDENCE_LEVEL),
                ("sided", STRICTLY_VERIFIED_DUPLICATE, FIELD_SIZE_SIDED),
                ("method", STRICTLY_VERIFIED_DUPLICATE, FIELD_SIZE_METHOD),
                ("bound_direction", STRICTLY_VERIFIED_DUPLICATE,
                 FIELD_SIZE_BOUND_DIRECTION),
                ("estimator", STRICTLY_VERIFIED_DUPLICATE, FIELD_SIZE_ESTIMATOR),
                ("bound", STRICTLY_VERIFIED_DUPLICATE, rule.bound_statement),
                ("replicates", STRICTLY_VERIFIED_DUPLICATE, rule.replicates),
                ("integer_boundary", STRICTLY_VERIFIED_DUPLICATE, rule.boundary),
                ("boundary_derivation", STRICTLY_VERIFIED_DUPLICATE,
                 FIELD_SIZE_BOUNDARY_DERIVATION),
                ("assurance_at_design_target", STRICTLY_VERIFIED_DUPLICATE, None)):
            add(_surface(short, f"assurance {key}", ap, key, mode,
                         "generated assurance region", expected, row))

        # ----------------------------------------- the derived-boundary container
        bp = f"derived_boundaries.{short}"
        declared = boundaries.get(short) or {}
        for key, mode, expected in (
                ("replicates", STRICTLY_VERIFIED_DUPLICATE, rule.replicates),
                ("nominal_alpha", STRICTLY_VERIFIED_DUPLICATE, rule.nominal_alpha),
                ("boundary", STRICTLY_VERIFIED_DUPLICATE, rule.boundary),
                ("cp_lower_at_boundary", STRICTLY_VERIFIED_DUPLICATE,
                 cp_lower(rule.boundary, rule.replicates)),
                ("cp_lower_at_boundary_plus_1", STRICTLY_VERIFIED_DUPLICATE,
                 cp_lower(rule.boundary + 1, rule.replicates)),
                ("rule", GENERATED_FROM_CANONICAL,
                 render_field_size_boundary_rule(rule)),
                ("per_field", GENERATED_FROM_CANONICAL,
                 rule.evaluation_scope == EVALUATION_SCOPE_PER_FIELD),
                ("pooling", GENERATED_FROM_CANONICAL,
                 render_field_size_pooling_statement(rule)),
                ("replicate_reduction", GENERATED_FROM_CANONICAL,
                 rule.field_reduction)):
            add(_surface(short, f"derived boundary {key}", bp, key, mode,
                         "section 12a boundary table", expected, declared))
        if rule.retention_statement is not None:
            add(_surface(short, "derived boundary retention", bp, "retains",
                         GENERATED_FROM_CANONICAL, "section 12a boundary table",
                         rule.retention_statement, declared))
        for key, expected in render_refusal_boundary_leaves(short).items():
            add(_surface(short, f"structured refusal {key}", bp, key,
                         GENERATED_FROM_CANONICAL, "section 12a boundary table",
                         expected, declared))

    # ------------------------------------------- C2, bound to its DERIVED rule
    c2 = C2_RELEASE_RULE
    c2_index, c2_case = cases.get(c2.case_id, (None, {}))
    c2p = f"cases[{c2_index}]"
    c2_row = assurance.get(c2.case_id) or {}
    for key, mode, expected in (
            ("case_id", STRICTLY_VERIFIED_DUPLICATE, c2.case_id),
            ("scientific_purpose", GENERATED_FROM_CANONICAL,
             render_c2_scientific_purpose()),
            ("formal_pass_fail_criterion", GENERATED_FROM_CANONICAL,
             render_c2_criterion()),
            ("fields_affected", GENERATED_FROM_CANONICAL, list(c2.required_fields)),
            ("primary_release_endpoint", GENERATED_FROM_CANONICAL,
             c2.primary_endpoint),
            ("replicate_count", STRICTLY_VERIFIED_DUPLICATE, c2.replicates_per_field),
            ("block1_role", STRICTLY_VERIFIED_DUPLICATE, "PRIMARY_RELEASE_ENDPOINT")):
        add(_surface("C2", key, c2p, key, mode, "generated cases region", expected,
                     c2_case))
    for key, expected in {**C2_CASE_PROSE_PINS, **C2_CASE_LIST_PINS}.items():
        add(_surface("C2", f"pinned case {key}", c2p, key,
                     STRICTLY_VERIFIED_DUPLICATE, "generated cases region", expected,
                     c2_case))
    c2a = f"assurance[{c2.case_id}]"
    for key, expected in render_c2_assurance().items():
        add(_surface("C2", f"assurance {key}", c2a, key, GENERATED_FROM_CANONICAL,
                     "generated assurance region", expected, c2_row))
    for key, mode, expected in (
            ("case_id", STRICTLY_VERIFIED_DUPLICATE, c2.case_id),
            ("target", GENERATED_FROM_CANONICAL,
             f"{c2.alpha_name} = {c2.nominal_alpha}"),
            ("target_value", STRICTLY_VERIFIED_DUPLICATE, c2.nominal_alpha),
            ("comparison", STRICTLY_VERIFIED_DUPLICATE, FIELD_SIZE_COMPARISON),
            ("confidence_level", STRICTLY_VERIFIED_DUPLICATE,
             FIELD_SIZE_CONFIDENCE_LEVEL),
            ("sided", STRICTLY_VERIFIED_DUPLICATE, FIELD_SIZE_SIDED),
            ("method", STRICTLY_VERIFIED_DUPLICATE, FIELD_SIZE_METHOD),
            ("bound_direction", STRICTLY_VERIFIED_DUPLICATE,
             FIELD_SIZE_BOUND_DIRECTION),
            ("estimator", STRICTLY_VERIFIED_DUPLICATE, FIELD_SIZE_ESTIMATOR),
            ("bound", STRICTLY_VERIFIED_DUPLICATE,
             "Clopper-Pearson one-sided LOWER (inflation test)"),
            ("replicates", STRICTLY_VERIFIED_DUPLICATE, c2.replicates_per_field),
            ("integer_boundary", STRICTLY_VERIFIED_DUPLICATE, c2.boundary),
            ("boundary_derivation", STRICTLY_VERIFIED_DUPLICATE,
             FIELD_SIZE_BOUNDARY_DERIVATION),
            ("assurance_at_design_target", STRICTLY_VERIFIED_DUPLICATE,
             "0.996 if the true rate is 0.005")):
        add(_surface("C2", f"assurance {key}", c2a, key, mode,
                     "generated assurance region", expected, c2_row))
    c2b = "derived_boundaries.C2"
    c2_declared = boundaries.get("C2") or {}
    for key, mode, expected in (
            ("replicates", STRICTLY_VERIFIED_DUPLICATE, c2.replicates_per_field),
            ("nominal_alpha", STRICTLY_VERIFIED_DUPLICATE, c2.nominal_alpha),
            ("boundary", STRICTLY_VERIFIED_DUPLICATE, c2.boundary),
            ("cp_lower_at_boundary", STRICTLY_VERIFIED_DUPLICATE,
             cp_lower(c2.boundary, c2.replicates_per_field)),
            ("cp_lower_at_boundary_plus_1", STRICTLY_VERIFIED_DUPLICATE,
             cp_lower(c2.boundary + 1, c2.replicates_per_field)),
            ("rule", GENERATED_FROM_CANONICAL, render_c2_boundary_rule()),
            ("per_field", GENERATED_FROM_CANONICAL,
             c2.evaluation_scope == EVALUATION_SCOPE_PER_FIELD),
            ("pooling", GENERATED_FROM_CANONICAL, render_c2_pooling_statement()),
            ("replicate_reduction", GENERATED_FROM_CANONICAL, c2.field_reduction)):
        add(_surface("C2", f"derived boundary {key}", c2b, key, mode,
                     "section 12a boundary table", expected, c2_declared))
    # C2's scope-out from the G5 amendment is STATED, not left to silence: its
    # composite P1 endpoint cannot be undefined, so it has no NOT_EVALUABLE path.
    for key, expected in render_refusal_boundary_leaves("C2").items():
        add(_surface("C2", f"structured refusal {key}", c2b, key,
                     GENERATED_FROM_CANONICAL, "section 12a boundary table",
                     expected, c2_declared))

    # ------------------------------- shared size-validation semantics (C2/C3/C4)
    svs = plan["size_validation_semantics"]
    for key, expected in SHARED_SIZE_SEMANTICS_PINS.items():
        add(_surface("SHARED", f"size semantics {key}", "size_validation_semantics",
                     key, STRICTLY_VERIFIED_DUPLICATE, "section 12 size semantics",
                     expected, svs))

    # ------------------------------------------------ the final campaign container
    final = plan["final_campaign_classification"]
    fp = "final_campaign_classification"
    requirements = final.get("requirements") or []
    for key, mode, expected in (
            ("verdict_on_success", STRICTLY_VERIFIED_DUPLICATE,
             FINAL_RELEASE_VERDICT),
            ("rule", GENERATED_FROM_CANONICAL, render_final_campaign_rule()),
            ("no_weighted_score", STRICTLY_VERIFIED_DUPLICATE, True),
            ("no_compensation_between_cases", STRICTLY_VERIFIED_DUPLICATE, True),
            ("independent_facts_rule", STRICTLY_VERIFIED_DUPLICATE,
             FINAL_RELEASE_INDEPENDENT_FACTS),
            ("implementation", STRICTLY_VERIFIED_DUPLICATE,
             FINAL_RELEASE_IMPLEMENTATION)):
        add(_surface("FINAL", key, fp, key, mode, "generated release-rules region",
                     expected, final))
    # MEMBERSHIP IS AUTHORITY. The COMPLETE ordered sequence is compared, so an
    # appended, inserted, removed, duplicated or reordered requirement refuses --
    # including one that names neither C3 nor C4. The previous check counted only
    # the lines mentioning those cases, which is how the r8 audit appended a
    # cross-field compensation rule and was accepted.
    add(NormativeSurface(
        "FINAL", "the complete requirement sequence", fp, "requirements",
        STRICTLY_VERIFIED_DUPLICATE, "generated release-rules region",
        list(final_campaign_requirements()), requirements))
    for rule in FIELD_SIZE_RULES:
        position = 3 if rule.case_id.startswith("C3") else 4
        add(NormativeSurface(
            rule.case_id[:2], "final campaign requirement line", fp,
            f"requirements[{position - 1}]", GENERATED_FROM_CANONICAL,
            "generated release-rules region",
            render_field_size_requirement(rule, position),
            requirements[position - 1] if len(requirements) >= position else None))
    return tuple(out)


def _controlled_containers(plan: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Containers whose EVERY key must be registered.

    These are the plan regions that exist to state C3/C4 size semantics, so an
    unregistered key in one of them is an unbound authoritative statement by
    construction -- which is exactly what both audits found.
    """
    cases = {case.get("case_id"): (i, case) for i, case in enumerate(plan["cases"])}
    boundaries = plan["size_validation_semantics"]["derived_boundaries"]
    assurance = {row.get("case_id"): row for row in plan["assurance"]}
    out: dict[str, dict[str, Any]] = {}
    for gap in plan.get("authority_gaps", []):
        if gap.get("id") in (FIELD_SIZE_DISPOSITION_ID, REFUSAL_DISPOSITION_ID):
            out[f"authority_gaps.{gap['id']}"] = gap
    for rule in FIELD_SIZE_RULES:
        index, case = cases.get(rule.case_id, (None, {}))
        out[f"cases[{index}].{rule.semantics_key}"] = case.get(rule.semantics_key) or {}
        out[f"assurance[{rule.case_id}]"] = assurance.get(rule.case_id) or {}
        out[f"derived_boundaries.{rule.case_id[:2]}"] = boundaries.get(
            rule.case_id[:2]) or {}
    # C2 joins the exhaustively swept set now that its rule is bound: its assurance
    # row and derived-boundary block are release semantics end to end.
    out[f"assurance[{C2_RELEASE_RULE.case_id}]"] = assurance.get(
        C2_RELEASE_RULE.case_id) or {}
    out["derived_boundaries.C2"] = boundaries.get("C2") or {}
    out["final_campaign_classification"] = plan["final_campaign_classification"]
    return out


def _prose_controlled_records(plan: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Records where every STRING is controlled, and non-strings are swept by key.

    A C3/C4 case record declares many things that are not field-size rules -- seed
    families, subconditions, calibration scope -- each governed by its own
    authority. Claiming all of their structure would claim authority this stage
    does not have, so numbers, flags and nested structures are only swept by
    field-rule key vocabulary.

    Their PROSE is different. Free text can state any rule whatever, which is
    exactly how the fourth audit turned an explanatory sentence into a release
    condition, so every string here must be generated or pinned.
    """
    controlled = set(FIELD_SIZE_RULES_BY_CASE) | {C2_RELEASE_RULE.case_id}
    out = {f"cases[{i}]": case for i, case in enumerate(plan["cases"])
           if case.get("case_id") in controlled}
    out["size_validation_semantics"] = plan["size_validation_semantics"]
    return out


def _container_of(plan: dict[str, Any], container: str) -> dict[str, Any]:
    """The live dict a container name addresses, across both sweep kinds."""
    both = {**_controlled_containers(plan), **_prose_controlled_records(plan)}
    return both.get(container, {})


def require_field_size_surface_totality(plan: dict[str, Any]) -> None:
    """No authoritative C3/C4 statement may exist outside the registry.

    Three audits in a row found a DIFFERENT unbound rendering of the same approved
    decision, so the registry is total rather than enumerated:

    1. every key inside a controlled container must be classified;
    2. every STRING inside a controlled C3/C4 record must be generated or pinned,
       because free prose can state any rule at all;
    3. no entry inside that surface may be classified NON_NORMATIVE_EXPLANATION,
       since that classification is what bought the fourth audit's sentence its
       freedom;
    4. non-string keys are additionally swept by field-rule key vocabulary.

    Rule 2 is the guarantee. The prose vocabulary check that follows is a
    secondary tripwire and is deliberately NOT relied upon.
    """
    registry = normative_surface_registry(plan)
    for surface in registry:
        if surface.mode not in VERIFICATION_MODES:
            raise NormativeSurfaceUnclassified(
                f"{surface.path} carries verification mode {surface.mode!r}, which is "
                f"not one of {VERIFICATION_MODES}")
    registered: dict[str, set[str]] = {}
    for surface in registry:
        registered.setdefault(surface.container, set()).add(surface.key)
    # A DECLARED key must also EXIST. Registering only what the candidate carries
    # means deleting a key deletes its check, which is the same self-authorising
    # shape as a candidate-derived exception set.
    swept = {**_controlled_containers(plan), **_prose_controlled_records(plan)}
    for surface in registry:
        if "[" in surface.key or surface.container not in swept:
            continue
        if surface.key not in swept[surface.container]:
            raise NormativeSurfaceUnclassified(
                f"{surface.path} is declared in the normative-surface registry but "
                "absent from the plan; an authority statement may not be deleted to "
                "escape its binding")
    for container, holder in _controlled_containers(plan).items():
        known = registered.get(container, set())
        for key in holder:
            if key not in known:
                raise NormativeSurfaceUnclassified(
                    f"{container}.{key} is an authoritative C3/C4 statement with no "
                    "entry in the normative-surface registry: it is bound to nothing "
                    "and could contradict the approved per-field rule while Markdown "
                    "and JSON still agree")
    # NO FREE PROSE. Every string inside a controlled C3/C4 record must be
    # generated or pinned. This, not a vocabulary list, is the guarantee: a
    # sentence cannot smuggle a release rule into a location that has no editable
    # text. Non-string keys stay vocabulary-swept below -- a number or a flag
    # cannot state a rule in prose.
    for container, holder in _prose_controlled_records(plan).items():
        known = registered.get(container, set())
        for key, value in holder.items():
            if key in known:
                continue
            if isinstance(value, str):
                raise NormativeSurfaceUnclassified(
                    f"{container}.{key} is free text inside a controlled C3/C4 "
                    "record with no entry in the normative-surface registry: it "
                    "could state a release, gating, pooling, reduction, field "
                    "membership, primary/secondary or final-classification rule "
                    "that nothing checks")
            if any(token in key.lower() for token in FIELD_RULE_KEY_TOKENS):
                raise NormativeSurfaceUnclassified(
                    f"{container}.{key} names a field-structure rule but has no entry "
                    "in the normative-surface registry")
    # An explanatory classification is not permitted inside the controlled
    # surface at all. Marking text "explanatory" was precisely how the fourth
    # audit's sentence escaped: the classification bought it freedom that no
    # checker could then take away.
    controlled = set(_controlled_containers(plan)) | set(_prose_controlled_records(plan))
    for surface in registry:
        if (surface.mode == NON_NORMATIVE_EXPLANATION
                and surface.container in controlled):
            raise NormativeSurfaceUnclassified(
                f"{surface.path} is classified {NON_NORMATIVE_EXPLANATION} inside a "
                "controlled C3/C4 container; semantically free text is not permitted "
                "there -- generate it from the canonical rule or pin it exactly")
    # Retained as a SECONDARY diagnostic only (see FIELD_RULE_PROSE_TOKENS).
    for surface in registry:
        if surface.mode != NON_NORMATIVE_EXPLANATION:
            continue
        text = str(surface.actual or "").lower()
        hit = [token for token in FIELD_RULE_PROSE_TOKENS if token in text]
        if hit:
            raise NormativeSurfaceUnclassified(
                f"{surface.path} is classified {NON_NORMATIVE_EXPLANATION} but states "
                f"field-structure rule vocabulary {hit}; an explanatory field may not "
                "carry a normative field rule")


def _amendment_rows(plan: dict[str, Any]) -> list[tuple[str, Any, Any]]:
    """Every (path, expected, actual) the canonical amendment determines."""
    return [(s.path, s.expected, s.actual) for s in normative_surface_registry(plan)
            if s.mode != NON_NORMATIVE_EXPLANATION]


def field_size_amendment_counts(plan: dict[str, Any]) -> dict[str, int]:
    """Machine-derived totality counts for the amendment. Nothing hand-counted."""
    registry = normative_surface_registry(plan)
    by_mode = {mode: sum(1 for s in registry if s.mode == mode)
               for mode in VERIFICATION_MODES}
    # Derived from the dataclass itself plus the module-level canonical constants,
    # so the figure cannot drift from the object it describes.
    canonical = len(FIELD_SIZE_RULES) * len(dataclasses.fields(FieldSizeRule)) + len(
        (FIELD_SIZE_DISPOSITION_ID, FIELD_SIZE_DISPOSITION_TYPE,
         FIELD_SIZE_DISPOSITION_STATUS, FIELD_SIZE_DISPOSITION_AFFECTS,
         FIELD_SIZE_REQUIRED_FIELDS, FINAL_RELEASE_REPRESENTATION,
         FINAL_RELEASE_COMPENSATION, FINAL_RELEASE_CONJUNCTION,
         FINAL_RELEASE_VERDICT, FINAL_RELEASE_IMPLEMENTATION,
         FINAL_RELEASE_INDEPENDENT_FACTS, FIELD_SIZE_ESTIMATOR,
         FIELD_SIZE_COMPARISON, FIELD_SIZE_CONFIDENCE_LEVEL, FIELD_SIZE_SIDED,
         FIELD_SIZE_METHOD, FIELD_SIZE_BOUND_DIRECTION,
         FIELD_SIZE_BOUNDARY_DERIVATION))
    registered: dict[str, set[str]] = {}
    for surface in registry:
        registered.setdefault(surface.container, set()).add(surface.key)
    unclassified = sum(
        1 for container, holder in _controlled_containers(plan).items()
        for key in holder if key not in registered.get(container, set()))
    unclassified += sum(
        1 for container, holder in _prose_controlled_records(plan).items()
        for key in holder
        if key not in registered.get(container, set())
        and any(token in key.lower() for token in FIELD_RULE_KEY_TOKENS))
    # The F1e-r5 metric: text inside the controlled surface that a person could
    # rewrite into a different scientific rule. Counted, not asserted by eye --
    # a string is free iff no registry entry generates or pins it.
    controlled = set(_controlled_containers(plan)) | set(_prose_controlled_records(plan))
    free_text = sum(
        1 for container in controlled
        for key, value in _container_of(plan, container).items()
        if isinstance(value, str) and key not in registered.get(container, set()))
    free_text += sum(1 for s in registry
                     if s.mode == NON_NORMATIVE_EXPLANATION
                     and s.container in controlled)
    # Controlled normative LISTS: membership is authority, so each is compared
    # whole. Counted from the registry rather than hand-listed.
    list_rows = [s for s in registry if isinstance(s.expected, list)]
    unexpected_items = sum(
        max(0, len(s.actual) - len(s.expected))
        for s in list_rows if isinstance(s.actual, list))
    missing_items = sum(
        max(0, len(s.expected) - len(s.actual))
        for s in list_rows if isinstance(s.actual, list))
    deferred_expected = set(DEFERRED_C2_LEAF_PATHS)
    deferred_observed = {leaf.path for leaf in size_semantics_leaves(plan)
                         if leaf.mode == DEFERRED_OUT_OF_SCOPE}
    return {
        "canonical_rule_fields": canonical,
        "controlled_normative_lists": len(list_rows),
        "canonical_list_elements": sum(len(s.expected) for s in list_rows),
        "unexpected_list_elements": unexpected_items,
        "missing_list_elements": missing_items,
        "deferred_exception_paths_expected": len(deferred_expected),
        "deferred_exception_paths_observed": len(deferred_observed),
        "unexpected_deferred_paths": len(deferred_observed - deferred_expected),
        "missing_deferred_paths": len(deferred_expected - deferred_observed),
        "semantically_free_rule_bearing_locations": free_text,
        "controlled_string_locations": sum(
            1 for container in controlled
            for value in _container_of(plan, container).values()
            if isinstance(value, str)),
        "normative_surface_locations": len(registry),
        "generated_normative_fields": by_mode[GENERATED_FROM_CANONICAL],
        "strictly_verified_duplicate_fields": by_mode[STRICTLY_VERIFIED_DUPLICATE],
        "non_normative_explanatory_fields": by_mode[NON_NORMATIVE_EXPLANATION],
        "controlled_containers": len(_controlled_containers(plan)),
        "checked_total": len(_amendment_rows(plan)),
        "unclassified_normative_amendment_fields": unclassified,
    }


#: C1's half of the `two_questions` block. It states the complete-pipeline
#: target, which is C1-only authority: pinned here as a tripwire so the C3/C4
#: repair cannot leave it free, without taking custody of the C1 decision.
TWO_QUESTIONS_COMPLETE_PIPELINE_PIN = (
    'C1, UNCHANGED. One-sided 95% Clopper-Pearson LOWER bound on '
    'complete-pipeline success >= 0.90 over R = 300, i.e. >= 279/300. '
    'This is the direct prospective validation of whether the whole '
    'implemented pipeline meets the release target.'
)

#: The superseded coarse gross-inflation criterion. Historical record rather
#: than a live rule -- but it names C2, C3 and C4 nominal alphas, so it is
#: pinned exactly rather than left as free prose.
SUPERSEDED_CRITERION_PINS = {
    "rule": 'one-sided 95% Clopper-Pearson UPPER bound <= 0.03',
    "origin": (
        'coarse assurance / gross-inflation tolerance inherited from '
        'development analysis'
    ),
    "status": (
        'SUPERSEDED as the RELEASE CLASSIFIER by the nominal-inflation '
        'tests above, which are strictly stronger; RETAINED as a mandatory '
        'reported diagnostic'
    ),
    "retained_as": (
        'MANDATORY CONTRACT DIAGNOSTIC '
        '[synthetic_validation_requirements[2]], inherited from development '
        'analysis and still required to be reported; NOT validation of the '
        'nominal alpha and NOT the release classifier'
    ),
    "tolerance": 0.03,
    "why_insufficient": {
        "C2": (
            'would have tolerated 6/400 = 0.0150, 3x the nominal alpha_geom = '
            '0.005'
        ),
        "C3": (
            'would have tolerated 6/400 = 0.0150, 15x the nominal alpha_2 = '
            '0.001'
        ),
        "C4": (
            'would have tolerated 47/2000 = 0.0235, 6x the nominal alpha_1 = '
            '0.004'
        ),
        "conclusion": (
            'a rule that passes fifteen times the nominal rate cannot be called '
            'validation of it'
        ),
    },
    "preserved_in": (
        'docs/e1a/E1A_V4_SYNTHETIC_PREEXEC_REPORT.md and commit 475633c, '
        'neither rewritten'
    ),
}


# ======================================================================== leaves
#: `size_validation_semantics` is a controlled scientific-authority SUBTREE, not a
#: flat container. The F1e-r6 audit changed two of its NESTED string leaves --
#: `interpretation.detector` and `two_questions.B_component_size_inflation` -- to
#: say that C3/C4 pool their four fields, and every checker accepted it, because
#: classification stopped at the registered parent. Neither leaf is rendered into
#: Markdown, so representation coherence could not see them either.
#:
#: The repair is leaf-level totality: the subtree is walked RECURSIVELY and every
#: leaf, at any depth, must carry its own classification. A classified parent
#: authorises nothing below it.
SIZE_SEMANTICS_ROOT = "size_validation_semantics"

#: RETIRED BY D6a3. C2's nine derived-boundary leaves were byte-quarantined while
#: their science was unresolved; the D6a reconstruction resolved it, so they are now
#: generated or strictly verified from `C2_RELEASE_RULE` like any other bound leaf.
#:
#: The mechanism itself is kept, empty: the deferred set must stay declared
#: independently of the candidate, so that a future exception cannot be created by
#: the document that would benefit from it. An empty expected set means every leaf
#: under the controlled subtree must now carry a real classification.
DEFERRED_C2_LEAF_PATHS: tuple[str, ...] = ()


@dataclass(frozen=True)
class SemanticLeaf:
    """ONE leaf of a controlled authority subtree and how it is held."""

    path: str
    mode: str
    expected: Any = None
    source: str = ""
    deferred_to: str | None = None


def render_component_size_question() -> str:
    """The `two_questions` statement of what the component size tests ARE.

    GENERATED. The audit rewrote this leaf into a familywise test over a pooled
    four-field count; the scope sentence is now read off the canonical rule, so
    that rewrite cannot be stated here any more.
    """
    cases = " and ".join(rule.case_id[:2] for rule in FIELD_SIZE_RULES)
    return (
        "C2, C3 and C4. At the feasible replicate counts these are NOT positive "
        "proofs that the achieved rate is at or below a tiny nominal alpha. They "
        "prospectively TEST FOR EVIDENCE OF INFLATION: "
        f"{SIZE_INTERPRETATION['test']}. The {cases} component tests are evaluated "
        f"{EVALUATION_SCOPE_PER_FIELD}, with within-replicate field reduction "
        f"{FIELD_REDUCTION_NONE} and pooling {POOLING_FORBIDDEN}; each is a "
        "COMPONENT size test and never a familywise or pooled test.")


def size_semantics_leaves(plan: dict[str, Any]) -> tuple[SemanticLeaf, ...]:
    """EVERY leaf of the controlled subtree, each with its own classification.

    Built from canonical sources that sit ABOVE the plan -- `FIELD_SIZE_RULES`,
    `classification.SIZE_INTERPRETATION`, the verdict labels and the pins -- never
    from the subtree being checked.
    """
    out: list[SemanticLeaf] = []
    add = out.append
    root = SIZE_SEMANTICS_ROOT

    for key, expected in SHARED_SIZE_SEMANTICS_PINS.items():
        add(SemanticLeaf(f"{root}.{key}", STRICTLY_PINNED_NON_RULE_TEXT, expected,
                         "SHARED_SIZE_SEMANTICS_PINS"))

    # --- the two_questions block ------------------------------------------
    add(SemanticLeaf(f"{root}.two_questions.A_complete_practical_performance",
                     STRICTLY_PINNED_NON_RULE_TEXT,
                     TWO_QUESTIONS_COMPLETE_PIPELINE_PIN,
                     "TWO_QUESTIONS_COMPLETE_PIPELINE_PIN (C1 authority)"))
    add(SemanticLeaf(f"{root}.two_questions.B_component_size_inflation",
                     GENERATED_FROM_CANONICAL, render_component_size_question(),
                     "FIELD_SIZE_RULES + SIZE_INTERPRETATION"))

    # --- the verdict labels -------------------------------------------------
    for key, expected in (("on_detection", SIZE_FAILURE),
                          ("otherwise", SIZE_NO_INFLATION)):
        add(SemanticLeaf(f"{root}.verdicts.{key}", STRICTLY_VERIFIED_DUPLICATE,
                         expected, "e1a_v4.validation.classification"))
    # The THIRD verdict and its precedence, from the G5 amendment. The order is
    # itself normative: without it the `otherwise` branch claims a clean field
    # from an incomplete primary sequence.
    add(SemanticLeaf(f"{root}.verdicts.on_undefined_primary_endpoint",
                     GENERATED_FROM_CANONICAL, STRUCTURED_REFUSAL_RULE.verdict,
                     "STRUCTURED_REFUSAL_RULE"))
    add(SemanticLeaf(f"{root}.verdicts.evaluation_order", GENERATED_FROM_CANONICAL,
                     render_refusal_verdict_order(), "STRUCTURED_REFUSAL_RULE"))

    # --- the structured-refusal block (G5) ----------------------------------
    for key, expected in render_structured_refusal_block().items():
        mode = (STRUCTURAL_VALUE_WITH_EXPLICIT_SCHEMA if isinstance(expected, list)
                else GENERATED_FROM_CANONICAL)
        add(SemanticLeaf(f"{root}.structured_refusal.{key}", mode, expected,
                         "STRUCTURED_REFUSAL_RULE"))

    # --- the whole interpretation block -------------------------------------
    # `classification.SIZE_INTERPRETATION` is the machine-readable statement of
    # what a size pass does and does not mean. The plan restates it; nothing
    # compared them, which is how `interpretation.detector` became free.
    for key, expected in SIZE_INTERPRETATION.items():
        mode = (STRUCTURAL_VALUE_WITH_EXPLICIT_SCHEMA if isinstance(expected, list)
                else STRICTLY_VERIFIED_DUPLICATE)
        value = list(expected) if isinstance(expected, list) else expected
        add(SemanticLeaf(f"{root}.interpretation.{key}", mode, value,
                         "e1a_v4.validation.classification.SIZE_INTERPRETATION"))

    # --- the superseded coarse criterion ------------------------------------
    for key, expected in SUPERSEDED_CRITERION_PINS.items():
        if isinstance(expected, dict):
            for sub, text in expected.items():
                add(SemanticLeaf(f"{root}.superseded_criterion.{key}.{sub}",
                                 STRICTLY_PINNED_NON_RULE_TEXT, text,
                                 "SUPERSEDED_CRITERION_PINS"))
            continue
        mode = (STRUCTURAL_VALUE_WITH_EXPLICIT_SCHEMA
                if not isinstance(expected, str) else STRICTLY_PINNED_NON_RULE_TEXT)
        add(SemanticLeaf(f"{root}.superseded_criterion.{key}", mode, expected,
                         "SUPERSEDED_CRITERION_PINS"))

    # --- derived boundaries --------------------------------------------------
    # C3 and C4 are already generated/verified by the normative-surface registry;
    # their leaves are declared here so the recursive walk is TOTAL, and point at
    # that registry rather than restating it.
    # Driven by the canonical surface registry, not by the candidate's keys.
    for entry in normative_surface_registry(plan):
        if not entry.container.startswith("derived_boundaries."):
            continue
        add(SemanticLeaf(f"{root}.{entry.path}", entry.mode, entry.expected,
                         "normative_surface_registry"))
    # C2's nine leaves were byte-quarantined by F1e because their science was
    # unresolved. D6a resolved it, so they are carried by the loop above like C3's
    # and C4's -- generated or strictly verified from the canonical rule -- and the
    # quarantine is retired.
    return tuple(out)


def _subtree_leaf_paths(node: Any, prefix: str):
    """Every leaf path in a nested plan object. Lists of scalars are one leaf."""
    if isinstance(node, dict):
        for key, value in node.items():
            yield from _subtree_leaf_paths(value, f"{prefix}.{key}")
    elif isinstance(node, list) and any(isinstance(x, (dict, list)) for x in node):
        for index, value in enumerate(node):
            yield from _subtree_leaf_paths(value, f"{prefix}[{index}]")
    else:
        yield prefix, node


def size_semantics_leaf_counts(plan: dict[str, Any]) -> dict[str, int]:
    """Machine-derived recursive coverage. Nothing hand-counted."""
    leaves = size_semantics_leaves(plan)
    declared = {leaf.path for leaf in leaves}
    actual = dict(_subtree_leaf_paths(plan[SIZE_SEMANTICS_ROOT], SIZE_SEMANTICS_ROOT))
    objects = 0
    stack = [plan[SIZE_SEMANTICS_ROOT]]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            objects += 1
            stack.extend(node.values())
    by_mode = {mode: sum(1 for leaf in leaves if leaf.mode == mode)
               for mode in VERIFICATION_MODES}
    return {
        "controlled_subtrees": 1,
        "controlled_nested_objects": objects,
        "total_leaves": len(actual),
        "declared_leaves": len(declared),
        "generated_leaves": by_mode[GENERATED_FROM_CANONICAL],
        "strictly_verified_leaves": by_mode[STRICTLY_VERIFIED_DUPLICATE],
        "exact_pinned_leaves": by_mode[STRICTLY_PINNED_NON_RULE_TEXT],
        "structural_schema_leaves": by_mode[STRUCTURAL_VALUE_WITH_EXPLICIT_SCHEMA],
        "deferred_out_of_scope_leaves": by_mode[DEFERRED_OUT_OF_SCOPE],
        "unclassified_leaves": len(set(actual) - declared),
        "unknown_child_keys": len(set(actual) - declared),
        "missing_declared_leaves": len(declared - set(actual)),
    }


def require_size_semantics_leaf_totality(plan: dict[str, Any]) -> None:
    """Every leaf of the controlled authority subtree, at ANY depth, is bound.

    A classified parent authorises nothing below it. The walk is over the plan's
    OWN structure, so a new nested child at any depth appears as an undeclared
    leaf and is refused -- that is what makes this recursive rather than a longer
    list of known paths.
    """
    if SIZE_SEMANTICS_ROOT not in plan:
        raise NormativeSurfaceUnclassified(
            f"the plan carries no {SIZE_SEMANTICS_ROOT} block")
    leaves = {leaf.path: leaf for leaf in size_semantics_leaves(plan)}
    for leaf in leaves.values():
        if leaf.mode not in VERIFICATION_MODES:
            raise NormativeSurfaceUnclassified(
                f"{leaf.path} carries verification mode {leaf.mode!r}")
    actual = dict(_subtree_leaf_paths(plan[SIZE_SEMANTICS_ROOT], SIZE_SEMANTICS_ROOT))
    for path in actual:
        if path not in leaves:
            raise NormativeSurfaceUnclassified(
                f"{path} is a nested authority leaf under {SIZE_SEMANTICS_ROOT} with "
                "no entry in the semantic-leaf registry: a classified parent does "
                "not authorise its descendants, and this leaf could state a "
                "contrary C3/C4 rule that nothing checks")
    for path, leaf in leaves.items():
        if path not in actual:
            raise NormativeSurfaceUnclassified(
                f"{path} is declared in the semantic-leaf registry but absent from "
                "the plan; an authority leaf may not be silently dropped")
        value = actual[path]
        if leaf.expected != value or type(leaf.expected) is not type(value):
            raise ProspectiveAmendmentMismatch(
                f"{path} does not express the approved authority: plan {value!r}, "
                f"canonical {leaf.expected!r} (source: {leaf.source})")



def require_c2_release_binding(contract: dict[str, Any],
                               plan: dict[str, Any]) -> None:
    """C2's per-field release rule, bound to the authority it is DERIVED from.

    Two things are checked that the surface registry alone cannot:

    1. the declared-field ROSTER the rule quantifies over is the contract's own
       `fields` declaration, in declaration order -- the rule does not carry its
       own copy of the field list;
    2. the rule still says what the D6a reconstruction derived, so a later edit to
       the canonical object itself is caught rather than silently re-generating a
       different plan.
    """
    declared = tuple(field["id"] for field in contract["fields"])
    if C2_RELEASE_RULE.required_fields != declared:
        raise ProspectiveAmendmentMismatch(
            "the C2 release rule quantifies over "
            f"{C2_RELEASE_RULE.required_fields}, but the contract declares "
            f"{declared}; the roster must be the contract's own field declaration")
    for name, expected in (
            ("elementary_event", C2_ELEMENTARY_EVENT),
            ("evaluation_scope", EVALUATION_SCOPE_PER_FIELD),
            ("field_reduction", FIELD_REDUCTION_NONE),
            ("pooling", POOLING_FORBIDDEN),
            ("final_combination", C2_FINAL_COMBINATION),
            ("primary_endpoint", C2_PRIMARY_ENDPOINT),
            ("authority_relationship", DERIVED),
            ("replicates_per_field", 400),
            ("nominal_alpha", 0.005)):
        if getattr(C2_RELEASE_RULE, name) != expected:
            raise ProspectiveAmendmentMismatch(
                f"the canonical C2 release rule's {name} is "
                f"{getattr(C2_RELEASE_RULE, name)!r}, not the derived {expected!r}")
    # The integer boundary is DERIVED, never copied.
    recomputed = size_boundary(C2_RELEASE_RULE.replicates_per_field,
                               C2_RELEASE_RULE.nominal_alpha)
    if C2_RELEASE_RULE.boundary != recomputed:
        raise ProspectiveAmendmentMismatch(
            f"the C2 integer boundary is DERIVED as {recomputed}, but the canonical "
            f"rule carries {C2_RELEASE_RULE.boundary}")


def require_field_size_amendment(plan: dict[str, Any]) -> None:
    """Every normative rendering of the C3/C4 amendment must BE the canonical rule.

    Markdown/JSON coherence cannot catch a package whose two renderings agree with
    each other and both contradict the approved amendment. This compares each
    rendering against the canonical object instead.
    """
    if FIELD_SIZE_DISPOSITION_ID not in {gap.get("id")
                                         for gap in plan.get("authority_gaps", [])}:
        raise ProspectiveAmendmentMismatch(
            f"the plan carries no {FIELD_SIZE_DISPOSITION_ID} disposition; the C3/C4 "
            "per-field amendment has no recorded prospective authority")
    for path, expected, actual in _amendment_rows(plan):
        if expected != actual or type(expected) is not type(actual):
            raise ProspectiveAmendmentMismatch(
                f"{path} does not express the approved {FIELD_SIZE_DISPOSITION_TYPE} "
                f"amendment: plan {actual!r}, canonical {expected!r}")


#: The cases whose RUNTIME implementation is held to the per-field rule. Nothing
#: here is a threshold: every R, alpha and boundary the check compares against is
#: read from `size_validation_semantics.derived_boundaries`, so a runtime table
#: that drifted from frozen authority refuses instead of being believed.
PER_FIELD_IMPLEMENTATION_CASES = ("C2", "C3", "C4")
#: The counts attribute each case must supply, and the scalar it must NOT supply.
PER_FIELD_COUNTS_ATTRIBUTES = {
    "C2": ("c2_rejections_by_field", "c2_rejections"),
    "C3": ("c3_rejections_by_field", "c3_rejections"),
    "C4": ("c4_rejections_by_field", "c4_rejections"),
}


def _field_evidence(case: str, rejections: dict[str, int],
                    refusals: dict[str, int] | None = None
                    ) -> dict[str, FieldSizeOutcome]:
    """Three-state evidence for one case, from plain per-field numbers. Pure."""
    planned, _nominal = PER_FIELD_SIZE_CASES[case]
    refused = refusals or {}
    return {
        field_id: FieldSizeOutcome(
            field_id=field_id, planned_replicates=planned,
            evaluable=planned - refused.get(field_id, 0),
            structured_refusals=refused.get(field_id, 0),
            rejections=rejections.get(field_id, 0),
            refusal_reasons=({"REFUSED_ACCESSIBLE_SPACE": refused[field_id]}
                             if refused.get(field_id) else {}))
        for field_id in sorted(REQUIRED_SIZE_FIELDS)}


def _clean_counts(per_case: dict[str, dict[str, int]],
                  refusals: dict[str, dict[str, int]] | None = None
                  ) -> CampaignCounts:
    """A campaign that passes everything except what the caller sets. Pure."""
    refused = refusals or {}
    return CampaignCounts(
        c1_successes=300,
        c2_rejections_by_field=per_case["C2"],
        c3_rejections_by_field=_field_evidence("C3", per_case["C3"],
                                               refused.get("C3")),
        c4_rejections_by_field=_field_evidence("C4", per_case["C4"],
                                               refused.get("C4")),
        c5_pass=True, c6_pass=True,
        c7_false_acceptances_by_alternative={
            "alt_1_06": 0, "alt_0_93_1_05": 0, "alt_1_10": 0, "hard_1_025": 0},
        c8_successes=200)


#: The refusal-aware aggregation surface the canonical driver must declare. Checked
#: by PARSING the driver's AST, never by importing it: importing would execute
#: driver code, which this stage forbids and which `e1a_v4/validation/driver.py`
#: avoids for the same reason. A driver that still answers "how many times did this
#: event occur" for C3/C4 declares none of these.
REFUSAL_AWARE_DRIVER_SURFACE = (
    "is_structured_refusal",
    "require_consistent_record",
    "endpoint_decision",
    "structured_refusal_reason",
    "field_primary_outcome",
    "per_field_primary_outcomes",
)


@functools.lru_cache(maxsize=None)
def _parse_driver_names(path: str, _mtime_ns: int, _size: int) -> frozenset[str]:
    """Parse one driver file's top-level names. MEMOISED on file IDENTITY.

    The canonical driver is a large module and preflight runs on every bind, so
    re-parsing it for each call is pure waste. The cache key carries the file's
    mtime and size, so an edited or substituted driver -- which is exactly what the
    negative tests install -- is re-parsed rather than served from the cache.
    """
    import ast
    with open(path, encoding="utf-8") as handle:
        tree = ast.parse(handle.read(), filename=path)
    return frozenset(node.name for node in tree.body
                     if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                                          ast.ClassDef)))


def _driver_declares(root: str) -> frozenset[str]:
    """Top-level names the canonical driver defines. Parsed; nothing is executed."""
    from .driver import OFFICIAL_CAMPAIGN_DRIVER_PATH
    path = os.path.join(root, OFFICIAL_CAMPAIGN_DRIVER_PATH)
    if not os.path.isfile(path):
        return frozenset()
    stat = os.stat(path)
    return _parse_driver_names(path, stat.st_mtime_ns, stat.st_size)


def require_per_field_implementation_conformance(plan: dict[str, Any],
                                                 root: str = ".") -> None:
    """POSITIVE PROOF that the runtime release classifier implements the per-field rule.

    This replaces a refusal rather than merely deleting one. Before the C3/C4
    amendment the driver refused to count C3 and C4 at all, because frozen
    authority had not declared how four per-field decisions become one
    replicate-level event. The amendment declared the answer -- PER FIELD,
    `replicate_reduction: NONE`, `pooling: FORBIDDEN` -- so the placeholder refusal
    is obsolete, and what takes its place has to be an assertion that the
    implementation now expresses that rule, not silence.

    Three independent things are checked, and all three are required:

        SHAPE       the classifier's input declares four field counts for each of
                    C2, C3 and C4, and declares no scalar case count that could
                    carry a pooled or any-field total instead
        PARAMETERS  the R and nominal alpha the runtime uses for each case equal
                    the frozen `derived_boundaries` values, and the integer
                    boundary RECOMPUTED from them equals the frozen one
        BEHAVIOUR   one field over its boundary fails that case, names that field
                    and leaves the case's other three conditions clean; and every
                    field of every case sitting at EXACTLY its boundary is clean.
                    A pooled or any-field implementation cannot do both.

    Pure arithmetic over synthetic counts. No RNG, no records, no execution.
    """
    boundaries = plan["size_validation_semantics"]["derived_boundaries"]
    roster = sorted(REQUIRED_SIZE_FIELDS)
    declared = {f.name for f in dataclass_fields(CampaignCounts)}
    for case in PER_FIELD_IMPLEMENTATION_CASES:
        per_field_attribute, scalar_attribute = PER_FIELD_COUNTS_ATTRIBUTES[case]
        if per_field_attribute not in declared:
            raise ImplementationAuthorityLag(
                f"the campaign classifier input declares no {per_field_attribute!r}. "
                f"{case} is scored PER FIELD and its four field counts are the "
                "scientific result; a case-level total cannot say which field "
                "inflated")
        if scalar_attribute in declared:
            raise ImplementationAuthorityLag(
                f"the campaign classifier input still declares the scalar "
                f"{scalar_attribute!r}. {case} declares replicate_reduction "
                f"{boundaries[case]['replicate_reduction']!r} and pooling "
                f"{boundaries[case]['pooling']!r}, so a single case count is a "
                "statistic the release rule does not contain")
        replicates, nominal = PER_FIELD_SIZE_CASES[case]
        row = boundaries[case]
        if (replicates, nominal) != (row["replicates"], row["nominal_alpha"]):
            raise ImplementationAuthorityLag(
                f"the runtime scores {case} at R = {replicates}, alpha = {nominal} "
                f"while frozen authority declares R = {row['replicates']}, alpha = "
                f"{row['nominal_alpha']}")
        recomputed = size_boundary(replicates, nominal)
        if recomputed != row["boundary"]:
            raise ImplementationAuthorityLag(
                f"{case}: the boundary recomputed from the runtime parameters is "
                f"{recomputed}, but frozen authority declares {row['boundary']}")

    # --- THE G5 STRUCTURED-REFUSAL RULE, as the runtime actually implements it --
    refusal = plan["size_validation_semantics"]["structured_refusal"]
    declared = {f.name for f in dataclass_fields(FieldSizeOutcome)}
    required_shape = {"field_id", "planned_replicates", "evaluable",
                      "structured_refusals", "rejections", "refusal_reasons"}
    missing_shape = sorted(required_shape - declared)
    if missing_shape:
        raise ImplementationAuthorityLag(
            f"the per-field primary evidence declares no {missing_shape}; frozen "
            f"authority requires {refusal['required_terminal_counts']} to be "
            "retained per field, and a bare rejection count cannot distinguish a "
            "defined non-rejection from an undefined primary endpoint")

    # --- RECORD INTEGRITY: only AFFIRMATIVE, consistent evidence authorises ---
    # F1f-g. The verdict machinery above is only as good as the records it is fed.
    # These probes are pure dictionary and dataclass work -- no Clopper-Pearson, no
    # records on disk -- so they are cheap enough to run on every bind, and they
    # test observable BEHAVIOUR of the one authorisation rule rather than the
    # driver's source text. The driver cannot be imported here (that would execute
    # driver code this stage forbids), which is precisely why the rule lives in the
    # classifier and the driver delegates to it.
    authorised_status = sorted(REFUSAL_AUTHORISING_STATUSES)[0]
    valid = {"analysis_status": authorised_status, "P1": False, "p1_rejected": True}
    if not authorises_undefined_block_decision(valid):
        raise ImplementationAuthorityLag(
            f"a terminal record carrying the declared status {authorised_status!r} "
            "with a fail-closed composite P1 is a VALID structured refusal, but the "
            "runtime rule rejects it; the terminal report frozen authority requires "
            f"({refusal['required_terminal_counts']}) could then never be produced")
    malformed = (
        ("an analysis status outside the declared roster",
         dict(valid, analysis_status="NOT_A_REAL_STATUS")),
        ("no analysis status at all",
         {k: v for k, v in valid.items() if k != "analysis_status"}),
        ("a non-string analysis status", dict(valid, analysis_status=None)),
        ("an ESTIMATED analysis status", dict(valid, analysis_status=ESTIMATED_STATUS)),
        ("a status the frozen gate does not fail closed on",
         dict(valid, analysis_status=sorted(NON_FAIL_CLOSED_STATUSES)[0])),
        ("a composite P1 that did NOT fail closed",
         dict(valid, P1=True, p1_rejected=False)),
        ("a composite P1 absent from the record",
         {k: v for k, v in valid.items() if k != "P1"}),
    )
    for label, record in malformed:
        if authorises_undefined_block_decision(record):
            raise ImplementationAuthorityLag(
                f"a terminal record with {label} was accepted as authorising an "
                "undefined C3/C4 primary endpoint. Validity is never inferred from "
                "the absence or malformation of data: an undefined block decision "
                "is authorised only by an explicit, recognised status whose record "
                "also expresses the frozen fail-closed composite P1 state")

    # The WHOLE-RECORD rule. The per-event rule above is asked only when a decision
    # is null, so on its own it cannot see a record that contradicts itself ACROSS
    # the two block decisions, nor an undeclared status on a record whose decisions
    # all happen to be defined.
    sound = (
        ("a valid structured refusal, both decisions undefined",
         dict(valid, block1_rejected=None, g5_rejected=None)),
        ("a fully estimated record, both decisions defined",
         {"analysis_status": ESTIMATED_STATUS, "P1": True, "p1_rejected": False,
          "block1_rejected": False, "g5_rejected": False}),
        ("a record from a case that carries no block decisions at all",
         {"analysis_status": ESTIMATED_STATUS}),
    )
    for label, record in sound:
        why = record_consistency_failure(record)
        if why is not None:
            raise ImplementationAuthorityLag(
                f"{label} is a record the frozen pipeline produces, but the runtime "
                f"whole-record rule rejects it: {why}")
    impossible = (
        ("block-1 undefined while G5 is defined",
         dict(valid, block1_rejected=None, g5_rejected=False)),
        ("G5 undefined while block-1 is defined",
         dict(valid, block1_rejected=False, g5_rejected=None)),
        ("an undeclared analysis status with BOTH decisions defined",
         {"analysis_status": "NOT_A_REAL_STATUS", "P1": True, "p1_rejected": False,
          "block1_rejected": False, "g5_rejected": False}),
        ("a fail-closed status with BOTH decisions defined",
         dict(valid, block1_rejected=False, g5_rejected=False)),
        ("an ESTIMATED status with BOTH decisions undefined",
         {"analysis_status": ESTIMATED_STATUS, "P1": False, "p1_rejected": True,
          "block1_rejected": None, "g5_rejected": None}),
        ("a refusal whose composite P1 did not fail closed",
         dict(valid, P1=True, p1_rejected=False, block1_rejected=None,
              g5_rejected=None)),
    )
    for label, record in impossible:
        if record_consistency_failure(record) is None:
            raise ImplementationAuthorityLag(
                f"a terminal record with {label} was accepted as internally "
                "consistent. The two-block gate decides BOTH blocks from the same "
                "p-value rows, so they are undefined together or defined together, "
                "and every terminal record states a DECLARED analysis status")

    # The DECISION DOMAIN and the composite P1 truth table (F1f-i). The rules above
    # say which records may leave an endpoint undefined; these say what a DEFINED
    # endpoint may be, and that the composite follows from its own blocks.
    estimated = {"analysis_status": ESTIMATED_STATUS, "block1_rejected": False,
                 "g5_rejected": False, "P1": True, "p1_rejected": False}
    for block1 in (False, True):
        for g5 in (False, True):
            composite = composite_p1_from_blocks(block1, g5)
            if composite["P1"] is not (not (block1 or g5)):
                raise ImplementationAuthorityLag(
                    f"the runtime composes P1 from block1={block1}, g5={g5} as "
                    f"{composite}; the frozen gate passes P1 only when NEITHER "
                    "block rejects")
            row = dict(estimated, block1_rejected=block1, g5_rejected=g5, **composite)
            state, failure = classify_record(row)
            if state != RECORD_ESTIMATED or failure is not None:
                raise ImplementationAuthorityLag(
                    f"a correctly composed estimated record with block1={block1} "
                    f"and g5={g5} was not accepted as an estimated record: {failure}")
            contradiction = dict(row, P1=not composite["P1"],
                                 p1_rejected=not composite["p1_rejected"])
            if record_consistency_failure(contradiction) is None:
                raise ImplementationAuthorityLag(
                    f"an estimated record whose composite P1 contradicts "
                    f"block1={block1}, g5={g5} was accepted; the two block "
                    "decisions determine the composite under the frozen union bound")
    domain_violations = [
        (f"{name}={value!r}", dict(estimated, **{name: value}))
        for name in ("block1_rejected", "g5_rejected", "P1", "p1_rejected")
        for value in ("false", 1, 0, 1.0, [])]
    domain_violations += [
        ("one block decision omitted",
         {k: v for k, v in estimated.items() if k != "block1_rejected"}),
        ("both block decisions omitted under an estimated status",
         {k: v for k, v in estimated.items()
          if k not in ("block1_rejected", "g5_rejected")}),
        ("the composite P1 fields omitted",
         {k: v for k, v in estimated.items() if k not in ("P1", "p1_rejected")}),
    ]
    for label, record in domain_violations:
        if record_consistency_failure(record) is None:
            raise ImplementationAuthorityLag(
                f"a terminal record with {label} was accepted. A defined endpoint "
                "decision is a strict boolean and the composite-P1 group is written "
                "whole or not at all; a truthy value counted as a rejection, and an "
                "absent block decision was read as a clean non-rejection")
    if classify_record({"analysis_status": ESTIMATED_STATUS})[0] != RECORD_NO_P1_GROUP:
        raise ImplementationAuthorityLag(
            "a record from a field the driver gave no calibration condition, and so "
            "carries no composite-P1 group at all, must remain a recognised state")

    # The REPLICATE-LEVEL derived decisions (F1f-k). Same defect class as above,
    # one level up: the producer writes the components AND a derived boolean, and
    # the consumer trusted the boolean. C1 counted an impossible complete-pipeline
    # success and C7 counted zero false acceptances against its own P2/P3.
    for p2 in (False, True):
        for p3 in (False, True):
            if false_acceptance_from_components(p2, p3) is not (p2 and p3):
                raise ImplementationAuthorityLag(
                    f"the runtime composes false_acceptance from P2={p2}, P3={p3} "
                    "as something other than their conjunction; C7 releases on that "
                    "event")
            sound = dict(estimated, P2=p2, P3=p3,
                         false_acceptance=false_acceptance_from_components(p2, p3),
                         complete_pass=complete_pass_from_components(True, p2, p3, True),
                         P4=True)
            if record_consistency_failure(sound) is not None:
                raise ImplementationAuthorityLag(
                    f"a correctly composed record with P2={p2}, P3={p3} was refused: "
                    f"{record_consistency_failure(sound)}")
            if record_consistency_failure(
                    dict(sound, false_acceptance=not sound["false_acceptance"])) is None:
                raise ImplementationAuthorityLag(
                    f"a record whose false_acceptance contradicts P2={p2}, P3={p3} "
                    "was accepted; C7 counts the recorded event, so a contradictory "
                    "value silently changes the false-acceptance rate")
    for p1_all in (False, True, None):
        expected = complete_pass_from_components(p1_all, True, True, True)
        if expected is not (None if p1_all is None else bool(p1_all)):
            raise ImplementationAuthorityLag(
                f"the runtime composes complete_pass from p1_all={p1_all} as "
                f"{expected!r}; the complete-pipeline event is the conjunction of "
                "P1 over every field with P2, P3 and P4")
    impossible_replicate = (
        ("complete_pass TRUE while the record's own P1 failed",
         dict(estimated, block1_rejected=True, g5_rejected=False, P1=False,
              p1_rejected=True, P2=True, P3=True, P4=True, false_acceptance=True,
              complete_pass=True)),
        ("complete_pass TRUE while P4 failed",
         dict(estimated, P2=True, P3=True, P4=False, false_acceptance=True,
              complete_pass=True)),
        ("a non-boolean complete_pass",
         dict(estimated, P2=True, P3=True, P4=True, false_acceptance=True,
              complete_pass="true")),
        ("a non-boolean false_acceptance",
         dict(estimated, P2=True, P3=True, P4=True, false_acceptance="true")),
        ("false_acceptance without its constituents",
         dict(estimated, false_acceptance=True)),
    )
    for label, record in impossible_replicate:
        if record_consistency_failure(record) is None:
            raise ImplementationAuthorityLag(
                f"a terminal record with {label} was accepted. A derived replicate "
                "decision is counted as recorded, so it must follow from the "
                "components recorded beside it")

    # C8's factor roster is available only with the frozen plan. Probe the SAME
    # pure rule the endpoint validator calls with those factors; generic record
    # consistency alone cannot tell that the second paired branch is missing.
    c8 = next((case for case in plan.get("cases", ())
               if isinstance(case, dict)
               and case.get("case_id") == "C8_blinded_scale_control"), None)
    subconditions = c8.get("subconditions") if c8 is not None else None
    if (not isinstance(subconditions, list) or len(subconditions) != 1
            or not isinstance(subconditions[0], dict)):
        raise ImplementationAuthorityLag(
            "C8 has no single paired subcondition with declared scale factors")
    declared_factors = subconditions[0].get("scale_factors")
    if (not isinstance(declared_factors, list) or len(declared_factors) != 2
            or any(type(factor) is not float for factor in declared_factors)):
        raise ImplementationAuthorityLag(
            "C8's paired scale factors must be the two plan-declared numbers")
    factors = tuple(declared_factors)
    keys = tuple(repr(factor) for factor in factors)
    branches = {key: {"c": factor, "p3_passed": True}
                for key, factor in zip(keys, factors)}
    recovered = {"scale_recovered": True, "scale_factors": list(factors),
                 "scale_control": {"branches": branches}}
    if scale_recovery_failure(recovered, factors) is not None:
        raise ImplementationAuthorityLag(
            "the C8 rule rejects a paired control whose declared factors both pass")
    one_failed = dict(recovered, scale_recovered=False,
                      scale_control={"branches": {
                          **branches, keys[-1]: {"c": factors[-1],
                                                 "p3_passed": False}}})
    if scale_recovery_failure(one_failed, factors) is not None:
        raise ImplementationAuthorityLag(
            "the C8 rule rejects a paired control whose recorded failure follows "
            "from one failed factor")
    malformed_scale = (
        ("no scale control", dict(recovered, scale_control=None)),
        ("no factor branches", dict(recovered, scale_control={"branches": {}})),
        ("one paired factor missing",
         dict(recovered, scale_control={"branches": {keys[0]: branches[keys[0]]}})),
        ("one factor decision missing",
         dict(recovered, scale_control={"branches": {
             **branches, keys[-1]: {"c": factors[-1]}}})),
        ("a non-boolean factor decision",
         dict(recovered, scale_control={"branches": {
             **branches, keys[-1]: {"c": factors[-1], "p3_passed": "true"}}})),
        ("a missing factor in the recorded list",
         dict(recovered, scale_factors=list(factors[:-1]))),
        ("the recorded factors in the wrong order",
         dict(recovered, scale_factors=list(reversed(factors)))),
        ("a branch labeled with the wrong factor",
         dict(recovered, scale_control={"branches": {
             **branches, keys[0]: {"c": factors[-1], "p3_passed": True}}})),
        ("a recovered claim despite a failed factor",
         dict(one_failed, scale_recovered=True)),
    )
    for label, record in malformed_scale:
        if scale_recovery_failure(record, factors) is None:
            raise ImplementationAuthorityLag(
                f"the C8 rule accepts {label}; a paired-control success requires "
                "the complete plan-declared factor evidence")

    # Refusal-reason accounting. A field reported NOT_EVALUABLE must be able to say
    # WHY, and the arithmetic that says so must be sound.
    planned, _nominal = PER_FIELD_SIZE_CASES["C3"]
    probe_field = sorted(REQUIRED_SIZE_FIELDS)[0]

    def _evidence(**over: Any) -> dict[str, Any]:
        base = dict(field_id=probe_field, planned_replicates=planned,
                    evaluable=planned - 1, structured_refusals=1, rejections=0,
                    refusal_reasons={"REFUSED_ACCESSIBLE_SPACE": 1})
        base.update(over)
        return base

    FieldSizeOutcome(**_evidence())            # the canonical valid shape
    FieldSizeOutcome(**_evidence(evaluable=planned, structured_refusals=0,
                                 refusal_reasons={}))
    unsound = (
        ("a refusal with no reason attributed", _evidence(refusal_reasons={})),
        ("reason counts that sum by cancelling a negative one",
         _evidence(refusal_reasons={"A": 2, "B": -1})),
        ("a reason attributed where nothing refused",
         _evidence(evaluable=planned, structured_refusals=0,
                   refusal_reasons={"A": 1})),
        ("a zero-valued reason key in place of the canonical empty mapping",
         _evidence(evaluable=planned, structured_refusals=0,
                   refusal_reasons={"A": 0})),
        ("a non-integer reason count", _evidence(refusal_reasons={"A": 1.0})),
        ("a boolean reason count", _evidence(refusal_reasons={"A": True})),
        ("an unnameable reason key", _evidence(refusal_reasons={"": 1})),
    )
    for label, kwargs in unsound:
        try:
            FieldSizeOutcome(**kwargs)
        except Refusal:
            continue
        raise ImplementationAuthorityLag(
            f"per-field primary evidence with {label} was constructed without "
            "refusing. Frozen authority requires the structured-refusal count and "
            "its reason attribution to be retained per field, which a count that "
            "does not balance cannot do")

    # --- BEHAVIOUR. Two classifications decide it, and the exhaustive
    # field-by-field enumeration lives in the test suites rather than here: this
    # runs inside every preflight, and a Clopper-Pearson bound is not cheap.
    #
    # PROBE 1. A DIFFERENT field is pushed one over its boundary in each of the
    # three cases at once. Exactly three size failures must come back, each naming
    # its own case and its own field, with the other nine field conditions clean.
    # A pooled or reduced implementation cannot produce that.
    probe_field = {case: roster[index] for index, case
                   in enumerate(PER_FIELD_IMPLEMENTATION_CASES)}
    over = {case: {f: 0 for f in REQUIRED_SIZE_FIELDS}
            for case in PER_FIELD_IMPLEMENTATION_CASES}
    for case, field_id in probe_field.items():
        over[case][field_id] = boundaries[case]["boundary"] + 1
    result = classify_campaign(_clean_counts(over))
    size_failures = [f for f in result["failures"] if SIZE_FAILURE in f]
    if result["verdict"] != "VALIDATION_FAILURE" or len(size_failures) != 3:
        raise ImplementationAuthorityLag(
            "one field over its boundary in each of C2, C3 and C4 must produce "
            f"exactly three field-identified release failures; got {size_failures}")
    for case, field_id in probe_field.items():
        named = [f for f in size_failures if field_id in f and f"({case} " in f]
        if len(named) != 1:
            raise ImplementationAuthorityLag(
                f"{case} field {field_id} over its boundary produced no uniquely "
                f"identified failure naming that case and that field: {size_failures}")
        contaminated = sorted(
            f for f in REQUIRED_SIZE_FIELDS
            if f != field_id
            and result["detail"][case][f]["verdict"] != SIZE_NO_INFLATION)
        if contaminated:
            raise ImplementationAuthorityLag(
                f"{case} field {field_id} over its boundary also failed "
                f"{contaminated}; a field's condition is its own")

    # PROBE 2. Every field of every case sits at EXACTLY its boundary. Under the
    # declared per-field rule that is clean; any pooled or any-field reduction of
    # the same counts is not. This is the difference the amendment preserved.
    spread = {case: {f: boundaries[case]["boundary"] for f in REQUIRED_SIZE_FIELDS}
              for case in PER_FIELD_IMPLEMENTATION_CASES}
    clean = classify_campaign(_clean_counts(spread))
    if any(SIZE_FAILURE in f for f in clean["failures"]):
        raise ImplementationAuthorityLag(
            "every field at exactly its boundary is clean under the declared "
            f"per-field rule, but the implementation reported {clean['failures']}; "
            "that is a pooled or reduced count")

    # --- the result says which endpoint released, and which did not -----------
    semantics = clean["endpoint_semantics"]
    for case in PER_FIELD_IMPLEMENTATION_CASES:
        row, stated = boundaries[case], semantics[case]
        if (stated["pooling"] != "FORBIDDEN"
                or stated["within_replicate_field_reduction"] != row["replicate_reduction"]
                or stated["field_scope"] != "PER_FIELD"):
            raise ImplementationAuthorityLag(
                f"{case}: the classifier reports field scope "
                f"{stated['field_scope']!r}, reduction "
                f"{stated['within_replicate_field_reduction']!r} and pooling "
                f"{stated['pooling']!r}, which does not restate frozen authority")
    c3_secondary = semantics["C3"]["secondary_diagnostic"]
    if c3_secondary["release_bearing"] is not False:
        raise ImplementationAuthorityLag(
            "the C3 full-P1 interaction diagnostic is reported as release-bearing; "
            "frozen authority declares it SECONDARY and states that the joint P1 "
            "result does not change the C3 release verdict")

    # ONE refused classification and ONE fully evaluable classification decide it
    # for both cases at once. Each is a Clopper-Pearson sweep over twelve fields,
    # and this runs on every bind, so the probes are combined deliberately.
    probe = roster[0]
    at_boundary = {c: {f: 0 for f in REQUIRED_SIZE_FIELDS}
                   for c in PER_FIELD_IMPLEMENTATION_CASES}
    for case in ("C3", "C4"):
        at_boundary[case][probe] = boundaries[case]["boundary"]
    refused = classify_campaign(
        _clean_counts(at_boundary, {case: {probe: 1} for case in ("C3", "C4")}))
    for case in ("C3", "C4"):
        planned, _nominal = PER_FIELD_SIZE_CASES[case]
        row = refused["detail"][case][probe]
        if row["verdict"] != SIZE_NOT_EVALUABLE:
            raise ImplementationAuthorityLag(
                f"{case} field {probe} with 1 structured refusal reported "
                f"{row['verdict']!r}; frozen authority declares "
                f"{refusal['primary_verdict_on_any_structured_refusal']!r} and "
                "the detector is NOT run on an incomplete primary sequence")
        if row["planned_replicates"] != planned:
            raise ImplementationAuthorityLag(
                f"{case} field {probe} reports a planned denominator of "
                f"{row['planned_replicates']}; frozen authority declares "
                f"{refusal['primary_denominator']} at {planned}")
        named = [f for f in refused["failures"]
                 if f.startswith(INCOMPLETE_EVIDENCE_CLASSIFICATION)
                 and probe in f and f"({case} " in f]
        if len(named) != 1:
            raise ImplementationAuthorityLag(
                f"{case} field {probe} produced no uniquely identified "
                f"{INCOMPLETE_EVIDENCE_CLASSIFICATION} failure: "
                f"{refused['failures']}")
    if refused["verdict"] != "VALIDATION_FAILURE":
        raise ImplementationAuthorityLag(
            f"a {SIZE_NOT_EVALUABLE} field did not prevent the campaign from "
            f"passing; frozen authority requires {refusal['release_requires']}")
    if any(f.startswith(SIZE_FAILURE) for f in refused["failures"]):
        raise ImplementationAuthorityLag(
            f"a structured refusal was reported as a statistical size failure: "
            f"{refused['failures']}. A refusal is neither a rejection nor a "
            "non-rejection")
    # The SAME counts with nothing refused must reach the ordinary verdict, so the
    # precedence is doing the work rather than a blanket override.
    evaluable = classify_campaign(_clean_counts(at_boundary))
    for case in ("C3", "C4"):
        if evaluable["detail"][case][probe]["verdict"] != SIZE_NO_INFLATION:
            raise ImplementationAuthorityLag(
                f"{case} field {probe} at exactly its boundary with NO refusals "
                f"reported {evaluable['detail'][case][probe]['verdict']!r}; the "
                "ordinary frozen rules must be unchanged when fully evaluable")

    # --- the aggregator must have a defined path for a valid refusal ----------
    absent = sorted(set(REFUSAL_AWARE_DRIVER_SURFACE) - _driver_declares(root))
    if absent and _driver_declares(root):
        raise ImplementationAuthorityLag(
            f"the canonical campaign driver declares no {absent}. A driver that "
            "only counts occurrences of a per-field event has no defined "
            "aggregation path for a valid structured refusal, so it raises "
            "ENDPOINT_EVENT_MISSING and the terminal report frozen authority "
            "requires is never produced")


def release_binding_specification(contract: dict[str, Any], plan: dict[str, Any],
                                  root: str = ".") -> tuple[ReleaseBinding, ...]:
    """Every release-bearing frozen quantity and the plan value that restates it."""
    rows: list[ReleaseBinding] = []

    def add(item, case_id, source, path, plan_path, relationship, reason,
            expected, actual, refusal=ContractReleaseTargetMismatch):
        rows.append(ReleaseBinding(item, case_id, source, path, plan_path,
                                   relationship, reason, expected, actual, refusal))

    cases = {case["case_id"]: (i, case) for i, case in enumerate(plan["cases"])}
    assurance = plan["assurance"]
    specification = case_release_specification(contract, root)
    for spec in specification:
        index, case = cases[spec.case_id]
        if spec.assurance_index >= len(assurance):
            raise ContractReleaseBindingUnclassified(
                f"{spec.case_id} has no assurance row at index {spec.assurance_index}; "
                "every release-bearing case needs a machine-readable release rule")
        row = assurance[spec.assurance_index]
        ap = f"assurance[{spec.assurance_index}]"
        add("case_id", spec.case_id, PACKAGE, "case release specification",
            f"{ap}.case_id", EXACT,
            "the assurance row names the case whose release rule it carries",
            spec.case_id, row.get("case_id"), ContractReleaseEndpointMismatch)
        add("release endpoint", spec.case_id, PACKAGE, "case release specification",
            f"cases[{index}].primary_release_endpoint", EXACT,
            "the endpoint the case releases on is frozen, not chosen at report time",
            spec.endpoint, case.get("primary_release_endpoint"),
            ContractReleaseEndpointMismatch)
        add("unit", spec.case_id, PACKAGE, "case release specification",
            f"{ap}.unit", EXACT,
            "per-field / per-alternative / per-cell / per-rho / joint semantics",
            spec.unit, row.get("unit"), ContractReleaseEndpointMismatch)
        # The resolved field structure is stated TWICE -- in the assurance row and
        # in the case's own semantics block -- because both are read by humans as
        # authority. Bind them to the same specification so a coherent edit to
        # either one alone refuses instead of quietly changing the measured size.
        semantics_key = FIELD_STRUCTURE_CASES.get(spec.case_id)
        if semantics_key is not None:
            semantics = case.get(semantics_key) or {}
            sp = f"cases[{index}].{semantics_key}"
            add("field structure", spec.case_id, PACKAGE, "case release specification",
                f"{sp}.field_structure", EXACT,
                "the elementary size event's scope, which must agree with the "
                "assurance unit that restates it",
                "PER_FIELD" if spec.unit == "per_field" else spec.unit.upper(),
                semantics.get("field_structure"), ContractReleaseEndpointMismatch)
            add("within-replicate field reduction", spec.case_id, PACKAGE,
                "case release specification", f"{sp}.field_reduction", EXACT,
                "a PER-FIELD elementary event leaves NO within-replicate reduction; "
                "any other value names a different statistical object with a "
                "different null rate",
                "NONE", semantics.get("field_reduction"),
                ContractReleaseEndpointMismatch)
            add("semantics pooling", spec.case_id, PACKAGE,
                "case release specification", f"{sp}.pooling", EXACT,
                "the semantics block restates the pooling rule and may not disagree "
                "with the assurance row",
                spec.pooling[0], semantics.get("pooling"),
                ContractReleaseTargetMismatch)

        for name, value, plan_key, refusal in (
                ("replicate count R", spec.replicates, "replicates",
                 ContractReleaseReplicateCountMismatch),
                ("interval method", spec.method, "method",
                 ContractReleaseConfidenceRuleMismatch),
                ("sidedness", spec.sided, "sided",
                 ContractReleaseConfidenceRuleMismatch),
                ("confidence level", spec.level, "confidence_level",
                 ContractReleaseConfidenceRuleMismatch),
                ("bound direction", spec.direction, "bound_direction",
                 ContractReleaseBoundDirectionMismatch),
                ("comparison", spec.comparison, "comparison",
                 ContractReleaseTargetMismatch),
                ("target probability", spec.target, "target_value",
                 ContractReleaseTargetMismatch),
                ("pooling", spec.pooling, "pooling", ContractReleaseTargetMismatch)):
            expected, relationship, source, path, reason = value
            add(name, spec.case_id, source, path, f"{ap}.{plan_key}", relationship,
                reason, expected, row.get(plan_key), refusal)

        # The SAME R also appears on the case record. Both are bound to the frozen
        # authority, so the two plan sites cannot agree on a value it never stated.
        expected_r = spec.replicates[0]
        add("replicate count R", spec.case_id, spec.replicates[2], spec.replicates[3],
            f"cases[{index}].replicate_count", spec.replicates[1], spec.replicates[4],
            expected_r, case.get("replicate_count"),
            ContractReleaseReplicateCountMismatch)

        # DERIVED: the integer boundary is recomputed from the frozen inputs above.
        boundary, derivation = derived_boundary(spec.direction[0], spec.comparison[0],
                                                expected_r, spec.target[0])
        add("integer pass boundary", spec.case_id, CONTRACT,
            f"{spec.direction[3]} + {spec.target[3]}", f"{ap}.integer_boundary", DERIVED,
            f"DERIVED: {derivation}. A hand-entered threshold could drift from the "
            "inputs it claims to summarise and is never trusted.",
            boundary, row.get("integer_boundary"),
            ContractReleaseDerivedThresholdMismatch)
        add("boundary derivation", spec.case_id, CONTRACT, "derivation rule",
            f"{ap}.boundary_derivation", DERIVED,
            "the derivation itself is recorded so a reader can recompute it",
            derivation, row.get("boundary_derivation"),
            ContractReleaseDerivedThresholdMismatch)

    # -------------------------------------------------- campaign-level authority
    pipeline = contract["complete_pipeline"]
    denom = plan["complete_pass_denominator"]
    add("complete-pass denominator", None, CONTRACT, "complete_pipeline.denominator",
        "complete_pass_denominator.rule", DERIVED,
        "the unconditional denominator: every declared experiment, no conditioning "
        "on survivors",
        "every declared validation replicate", denom.get("rule"))
    add("structured-refusal treatment", None, CONTRACT, "complete_pipeline.denominator",
        "complete_pass_denominator.refusals", DERIVED,
        "refusals count as failures; the contract's denominator says so literally",
        "structured refusals COUNT AS FAILURES for complete-pipeline success",
        denom.get("refusals"))
    add("complete-pass event", None, CONTRACT, "complete_pipeline.complete_pass_event",
        "release_authority.complete_pass_event", EXACT,
        "what counts as one complete-pipeline success is frozen upstream",
        pipeline["complete_pass_event"],
        plan["release_authority"].get("complete_pass_event"),
        ContractReleaseEndpointMismatch)

    # ------------------------------ case-specific release STRUCTURE, kept frozen
    # Changing a replicate count must not be able to alter what a case measures.
    c3 = cases["C3_g5_block"][1]
    add("C3 block-1 role", "C3_g5_block", CONTRACT, "endpoints.P1_geometry.procedure",
        "cases[2].block1_role", CASE_SPECIFIC,
        "C3's PRIMARY release endpoint is Block-2 / G5 size; the full two-block P1 "
        "result is a SECONDARY predeclared interaction diagnostic and does not change "
        "the C3 release verdict",
        "SECONDARY_PREDECLARED_INTERACTION_DIAGNOSTIC", c3.get("block1_role"),
        ContractReleaseEndpointMismatch)
    add("C3 semantics", "C3_g5_block", CONTRACT, "endpoints.P1_geometry.procedure",
        "cases[2].c3_semantics.primary_release_endpoint", CASE_SPECIFIC,
        "the prospectively resolved ambiguity: G5 block size is the release endpoint",
        "G5_BLOCK_SIZE", c3.get("c3_semantics", {}).get("primary_release_endpoint"),
        ContractReleaseEndpointMismatch)
    add("C3 forbidden threshold", "C3_g5_block", CONTRACT,
        "endpoints.P1_geometry.procedure",
        "cases[2].c3_semantics.joint_p1_result_changes_C3_release_verdict",
        CASE_SPECIFIC,
        "no new C3 release threshold may be added on Block 1 or the joint P1 result",
        False, c3.get("c3_semantics", {}).get(
            "joint_p1_result_changes_C3_release_verdict"),
        ContractReleaseEndpointMismatch)

    c6 = cases["C6_mode_resolution_boundary"][1]
    add("C6 field structure", "C6_mode_resolution_boundary", CONTRACT,
        "mode_resolution.basis", "cases[5].fields_affected", CASE_SPECIFIC,
        "C6 evaluates ONE synthetic two-mode field at the declared rho. Expanding it "
        "to the four physical fields would silently quadruple the experiment.",
        ["synthetic two-mode field at the declared rho"], c6.get("fields_affected"),
        ContractReleaseEndpointMismatch)
    add("C6 calibrated fields", "C6_mode_resolution_boundary", CONTRACT,
        "mode_resolution.basis", "cases[5].fields_requiring_calibration", CASE_SPECIFIC,
        "one synthetic field means one calibrated field", 1,
        c6.get("fields_requiring_calibration"), ContractReleaseEndpointMismatch)
    add("C6 declared rho count", "C6_mode_resolution_boundary", CONTRACT,
        "synthetic_validation_requirements[6]", "cases[5].subcondition_count",
        DERIVED, "boundary, boundary -20% and boundary +20% are three declared rho",
        3, c6.get("subcondition_count"), ContractReleaseEndpointMismatch)

    c8 = cases["C8_blinded_scale_control"][1]
    c8_sub = c8["subconditions"][0]
    g1_block = contract["synthetic_validation_release_criteria"]["G1_blinded_scale_control"]
    add("C8 scale factors", "C8_blinded_scale_control", CONTRACT,
        "synthetic_validation_release_criteria.G1_blinded_scale_control.scale_factors",
        "cases[7].subconditions[0].scale_factors", EXACT,
        "the paired blinded factors are frozen measurement transforms",
        g1_block["scale_factors"], c8_sub.get("scale_factors"))
    add("C8 paired semantics", "C8_blinded_scale_control", CONTRACT,
        "synthetic_validation_release_criteria.G1_blinded_scale_control.replicate_rule",
        "cases[7].subconditions[0].pairing", CASE_SPECIFIC,
        "the contract's replicate_rule makes one C8 replicate succeed only if BOTH "
        "branches pass, so the two factors act on the same underlying replicate. The "
        "declared pairing sentence is pinned in full: a weakened prefix check would "
        "accept a sentence that still began 'INTENTIONAL:' while saying the opposite.",
        C8_PAIRING, c8_sub.get("pairing"), ContractReleaseEndpointMismatch)

    # ------------------------- the complete G1/G2 release dispositions, leaf by leaf
    # The plan restates both dispositions in full. Every leaf is bound, so a
    # release-bearing value cannot hide inside a subtree that "looks copied".
    criteria = contract["synthetic_validation_release_criteria"]
    for disposition, source in (("G1", "G1_blinded_scale_control"),
                                ("G2", "G2_false_bridge_discrimination")):
        block = criteria[source]
        declared = plan["author_dispositions"][disposition]
        case_id = "C8_blinded_scale_control" if disposition == "G1" else "C7_false_bridge"
        for path, value in sorted(_leaf_items(block, "")):
            authority = f"synthetic_validation_release_criteria.{source}{path}"
            plan_path = f"author_dispositions.{disposition}{path}"
            if path.endswith(".integer_threshold"):
                spec = next(s for s in specification if s.case_id == case_id)
                recomputed, derivation = derived_boundary(
                    spec.direction[0], spec.comparison[0], spec.replicates[0],
                    spec.target[0])
                if value != recomputed:
                    raise ContractReleaseDerivedThresholdMismatch(
                        f"{authority} records {value!r}, but its own frozen inputs "
                        f"derive {recomputed!r}")
                add("frozen integer threshold", case_id, CONTRACT, authority,
                    plan_path, DERIVED,
                    f"DERIVED: {derivation}. The contract records the threshold and "
                    "says 'verified, not copied'; it is recomputed here rather than "
                    "trusted, so it can never become independent authority.",
                    recomputed, _at(declared, path),
                    ContractReleaseDerivedThresholdMismatch)
                continue
            add(f"{disposition} release disposition{path}", case_id, CONTRACT, authority,
                plan_path, EXACT,
                "the adopted release disposition is restated in full; no leaf of it "
                "may be selectively changed",
                value, _at(declared, path))

    add("job status reconciliation", None, CONTRACT, "refusal_semantics.reconciliation",
        "complete_pass_denominator.reporting", REPORT_ONLY_MANDATORY,
        "jobs declared = jobs completed + jobs refused, with a per-status count; the "
        "report must finish even when every job refuses",
        "refusal counts AND reasons are reported",
        plan["complete_pass_denominator"].get("reporting"),
        ContractMandatoryDiagnosticMissing)

    # A release rule may rest on a prospective disposition only while that
    # disposition is actually recorded and closed. Deleting or reopening it must
    # not leave the rule it justifies standing unsupported.
    gaps = {gap["id"]: gap for gap in plan.get("authority_gaps", [])}
    for cited in sorted({str(s.pooling[3]) for s in specification
                         if str(s.pooling[3]).startswith("authority_gaps.")}):
        gid = cited.split(".", 1)[1]
        add("cited prospective disposition", None, PACKAGE, cited,
            f"authority_gaps.{gid}.status", EXACT,
            "a release rule citing a prospective disposition requires that "
            "disposition to be recorded and CLOSED PROSPECTIVELY",
            "CLOSED PROSPECTIVELY", (gaps.get(gid) or {}).get("status"),
            ContractReleaseBindingUnclassified)

    # --------------------------------------------------------- IMPLIED_STRONGER
    req2 = parse_requirement(_require_frozen_text(contract, 2),
                             "synthetic_validation_requirements[2]")
    add("coarse gross-inflation ceiling", "C2_geometry_false_rejection", CONTRACT,
        "synthetic_validation_requirements[2]",
        "release_authority.implied_stronger.C2.contract_threshold", IMPLIED_STRONGER,
        "the adopted nominal-inflation rule is STRICTLY STRONGER than this older "
        "requirement over its entire accepting range; the older requirement is "
        "preserved as a MANDATORY CONTRACT DIAGNOSTIC rather than erased",
        req2.target,
        plan["release_authority"]["implied_stronger"]["C2"].get("contract_threshold"))

    # -------------------------------------------------- REPORT_ONLY_MANDATORY
    declared = {row["diagnostic_id"]: row
                for row in plan["release_authority"]["mandatory_diagnostics"]}
    for diagnostic in mandatory_diagnostics(contract):
        actual = declared.get(diagnostic.diagnostic_id)
        add(f"mandatory diagnostic {diagnostic.diagnostic_id}", diagnostic.case_id,
            diagnostic.authority_source, diagnostic.authority_path,
            f"release_authority.mandatory_diagnostics.{diagnostic.diagnostic_id}",
            REPORT_ONLY_MANDATORY, diagnostic.requirement,
            {"diagnostic_id": diagnostic.diagnostic_id, "case_id": diagnostic.case_id,
             "authority_source": diagnostic.authority_source,
             "authority_path": diagnostic.authority_path,
             "requirement": diagnostic.requirement,
             "aggregate_key": diagnostic.aggregate_key,
             "required_keys": list(diagnostic.required_keys)},
            actual, ContractMandatoryDiagnosticMissing)
    return tuple(rows)


# -------------------------------------------------- release-authority totality
#: Frozen contract sections whose leaves are RELEASE-RELEVANT. Every leaf under
#: these must be classified by a binding row or an explicit NOT_APPLICABLE reason.
RELEASE_AUTHORITY_SECTIONS = (
    "synthetic_validation_requirements",
    "synthetic_validation_release_criteria",
    "complete_pipeline",
    "endpoints",
    "mode_resolution",
    "refusal_semantics",
)


def _leaf_paths(value: Any, prefix: str) -> list[str]:
    if isinstance(value, dict):
        return [p for key, child in value.items()
                for p in _leaf_paths(child, f"{prefix}.{key}")]
    if prefix == "synthetic_validation_requirements" and isinstance(value, list):
        return [p for i, child in enumerate(value)
                for p in _leaf_paths(child, f"{prefix}[{i}]")]
    return [prefix]


#: Release-relevant leaves with NO plan restatement, each with a stated reason.
#: Per the standing rule, a leaf that affects sample size, a release decision, a
#: confidence rule or mandatory reporting must NOT appear here.
RELEASE_NOT_APPLICABLE = {
    "complete_pipeline.union_inequality": "analytic power-budget identity, not a release rule",
    "complete_pipeline.union_inequality_label": "label on that identity",
    "complete_pipeline.raw_union_expression": "the analytic pre-estimate, explicitly not demonstrated power",
    "complete_pipeline.reported_lower_bound": "rounded analytic pre-estimate; the release gate is C1's measured rate",
    "complete_pipeline.required_interpretation": "interpretation guard on that pre-estimate",
    "complete_pipeline.is_demonstrated_empirical_power": "states that the budget is NOT the release evidence",
    "complete_pipeline.is_unconditional_lower_bound_on_implemented_pipeline": "same guard, other direction",
    "complete_pipeline.standing_qualifications": "qualifications on the analytic budget",
    "endpoints.P1_geometry.mandatory": "endpoint mandatoriness, fixed in analysis code",
    "endpoints.P1_geometry.type": "endpoint taxonomy",
    "endpoints.P1_geometry.gates": "gate roster, bound by contract_plan.py",
    "endpoints.P1_geometry.independence_between_blocks": "validity statement for the union bound",
    "endpoints.P2_cross_field.comparisons": "structural count of the IUT comparisons",
    "endpoints.P2_cross_field.forbidden_reinterpretations": "prohibition implemented in analysis code",
    "endpoints.P2_cross_field.half_width": "estimator formula, implemented in analysis code",
    "endpoints.P2_cross_field.mandatory": "endpoint mandatoriness",
    "endpoints.P2_cross_field.multiplicity_correction": "bound by contract_plan.py",
    "endpoints.P2_cross_field.ratio": "estimator formula",
    "endpoints.P2_cross_field.rule": "acceptance formula, implemented in analysis code",
    "endpoints.P2_cross_field.sigma_cm_treatment": "algebraic cancellation statement",
    "endpoints.P2_cross_field.status": "endpoint precedence label",
    "endpoints.P2_cross_field.test_type": "test taxonomy",
    "endpoints.P2_cross_field.type": "endpoint taxonomy",
    "endpoints.P2_cross_field.delta_cross": "bound by contract_plan.py",
    "endpoints.P2_cross_field.z_cross": "bound by contract_plan.py",
    "endpoints.P3_absolute.applies_to": "bound by contract_plan.py",
    "endpoints.P3_absolute.delta_abs": "bound by contract_plan.py",
    "endpoints.P3_absolute.z_abs": "bound by contract_plan.py",
    "endpoints.P3_absolute.half_width": "estimator formula",
    "endpoints.P3_absolute.mandatory": "endpoint mandatoriness",
    "endpoints.P3_absolute.multiplicity_correction": "IUT needs none",
    "endpoints.P3_absolute.non_estimated_field": "fail-closed rule in analysis code",
    "endpoints.P3_absolute.provenance.adopted": "provenance note",
    "endpoints.P3_absolute.provenance.adopted_before": "provenance note",
    "endpoints.P3_absolute.provenance.historically_committed": "provenance note",
    "endpoints.P3_absolute.provenance.supersedes": "provenance note",
    "endpoints.P3_absolute.rule": "acceptance formula",
    "endpoints.P3_absolute.test_type": "test taxonomy",
    "endpoints.P3_absolute.type": "endpoint taxonomy",
    "endpoints.P4_entropy.checks": "deterministic algebraic check, no replicate count",
    "endpoints.P4_entropy.classification": "bound by contract_plan.py",
    "endpoints.P4_entropy.mandatory": "endpoint mandatoriness",
    "endpoints.P4_entropy.not_experimental_evidence": "interpretation guard",
    "endpoints.P4_entropy.reads_branch_B_data": "information-separation statement",
    "endpoints.P4_entropy.stochastic_failure_probability_after_passing": "deterministic check has none",
    "endpoints.P1_geometry.procedure": "the two-block union rule; used as a DERIVATION input above",
    "mode_resolution.rule": "merge/split formula, implemented in analysis code",
    "mode_resolution.basis": "information-separation statement",
    "mode_resolution.status": "prospective-setting label",
    "mode_resolution.theta_cap_deg": "bound by contract_plan.py",
    "refusal_semantics.rank_tol": "bound by contract_plan.py",
    "refusal_semantics.statuses": "runtime status vocabulary, fixed in implementation",
    "synthetic_validation_requirements[0]": "procedure-freeze mechanic, bound by the execution identity",
    "synthetic_validation_requirements[1]": "seed-family disjointness, enforced by seeds.py",
    "synthetic_validation_release_criteria.note": "scope note on G1/G2",
    "complete_pipeline.budget_terms.4x_alpha_geom": "analytic budget term; the operative alpha_geom is bound as C2's target",
    "complete_pipeline.budget_terms.4x_eps_cal": "analytic budget term, explicitly labelled APPROXIMATE",
    "complete_pipeline.budget_terms.4x_rank_neff_refusal": "analytic budget term",
    "complete_pipeline.budget_terms.3x_mode_resolution_crossing_5deg": "analytic budget term",
    "complete_pipeline.budget_terms.one_minus_pi_P2_and_P3": "analytic budget term",
    "complete_pipeline.budget_terms.P4_failure": "analytic budget term for a deterministic check",
    "complete_pipeline.supporting.pi_P2": "supporting analytic probability, not a release threshold",
    "complete_pipeline.supporting.pi_P3_all_four_fields": "supporting analytic probability",
    "complete_pipeline.supporting.pi_P2_and_P3": "supporting analytic probability",
    "complete_pipeline.supporting.integration": "the numerical method behind those probabilities",
    "complete_pipeline.input_labels.union_inequality": "epistemic label on a budget input",
    "complete_pipeline.input_labels.pi_P2_and_P3": "epistemic label on a budget input",
    "complete_pipeline.input_labels.alpha_geom": "epistemic label: a NOMINAL allocation whose achieved size must be DEMONSTRATED -- which is exactly what C2 does, under a binding of its own",
    "complete_pipeline.input_labels.eps_cal": "epistemic label on a budget input",
    "complete_pipeline.input_labels.rank_neff_bound": "epistemic label on a budget input",
    "complete_pipeline.input_labels.mode_resolution_crossing": "epistemic label on a budget input",
    "mode_resolution.split_probability_truly_circular_at_sigma_k_0p34pct.5_deg": "design-time probability used to CHOOSE theta_cap; no campaign figure reports it",
    "mode_resolution.split_probability_truly_circular_at_sigma_k_0p34pct.10_deg": "design-time probability at a theta_cap that was not adopted",
    "mode_resolution.split_probability_truly_circular_at_sigma_k_0p34pct.20_deg": "design-time probability at a theta_cap that was not adopted",
}


def release_inventory(contract: dict[str, Any], plan: dict[str, Any],
                      root: str = ".", rows=None) -> dict[str, int]:
    """Machine-derived counts. Nothing here is asserted or hand-entered."""
    if rows is None:
        rows = release_binding_specification(contract, plan, root)
    result = {name: sum(r.relationship == name for r in rows) for name in RELATIONSHIPS}
    result["release_relevant_authority_items"] = len(rows)
    leaves = [p for section in RELEASE_AUTHORITY_SECTIONS
              for p in _leaf_paths(contract[section], section)]
    result["release_relevant_contract_leaves"] = len(leaves)
    covered = {r.authority_path for r in rows}
    unclassified = 0
    for leaf in leaves:
        if leaf in RELEASE_NOT_APPLICABLE:
            continue
        if any(leaf == c or leaf.startswith(c + ".") or c.startswith(leaf + ".")
               for c in covered):
            continue
        unclassified += 1
    result[NOT_APPLICABLE] += sum(1 for leaf in leaves if leaf in RELEASE_NOT_APPLICABLE)
    result["unclassified"] = unclassified + sum(
        1 for r in rows
        if r.relationship not in RELATIONSHIPS or not r.reason or not r.authority_path)
    result["mandatory_diagnostics"] = len(mandatory_diagnostics(contract))
    result["exact_release_bindings"] = result[EXACT]
    return result


def require_release_authority_conformance(contract: dict[str, Any], plan: dict[str, Any],
                                          root: str = ".") -> None:
    """The entry point. Fails closed on any release-bearing disagreement."""
    if "release_authority" not in plan:
        raise ContractReleaseBindingUnclassified(
            "the plan carries no release_authority block; release-bearing statistics "
            "would have no machine-readable binding to frozen authority")
    require_c2_implies_contract_diagnostic(contract)
    require_c2_release_binding(contract, plan)
    require_field_size_surface_totality(plan)
    require_size_semantics_leaf_totality(plan)
    require_field_size_amendment(plan)
    require_per_field_implementation_conformance(plan, root)
    rows = release_binding_specification(contract, plan, root)
    inventory = release_inventory(contract, plan, root, rows)
    if inventory["unclassified"]:
        raise ContractReleaseBindingUnclassified(
            f"{inventory['unclassified']} release-relevant frozen authority leaves "
            "carry no binding and no explicit NOT_APPLICABLE justification")
    for row in rows:
        if row.relationship == NOT_APPLICABLE:
            continue
        if row.expected != row.actual or type(row.expected) is not type(row.actual):
            raise row.refusal(
                f"{row.plan_path} != {row.authority_path} [{row.relationship}]: plan "
                f"{row.actual!r}, frozen authority {row.expected!r} "
                f"({row.authority_source})")

    # The human prose must not contradict the structured rule it summarises.
    for spec in case_release_specification(contract, root):
        row = plan["assurance"][spec.assurance_index]
        if row["target_value"] is not None:
            if not any(abs(n - row["target_value"]) < 1e-12
                       for n in _numbers_in(row["target"])):
                raise ContractReleaseTargetMismatch(
                    f"assurance[{spec.assurance_index}].target {row['target']!r} does "
                    f"not state the frozen target {row['target_value']!r}")
        if row["integer_boundary"] is not None:
            numbers = _numbers_in(row["acceptance_rule"])
            if float(row["integer_boundary"]) not in numbers:
                raise ContractReleaseDerivedThresholdMismatch(
                    f"assurance[{spec.assurance_index}].acceptance_rule "
                    f"{row['acceptance_rule']!r} does not state the derived boundary "
                    f"{row['integer_boundary']}")
            if float(row["replicates"]) not in numbers:
                raise ContractReleaseDerivedThresholdMismatch(
                    f"assurance[{spec.assurance_index}].acceptance_rule "
                    f"{row['acceptance_rule']!r} does not state R = {row['replicates']}")
        for part in (row["method"], row["sided"], row["bound_direction"]):
            if part.lower() not in row["bound"].lower():
                raise ContractReleaseConfidenceRuleMismatch(
                    f"assurance[{spec.assurance_index}].bound {row['bound']!r} does not "
                    f"state {part!r}, which the structured rule declares")
