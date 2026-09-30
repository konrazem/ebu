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
from dataclasses import dataclass
from typing import Any

from .classification import GROSS_INFLATION_TOLERANCE, size_boundary
from .dispositions import cp_lower, cp_upper, g1_success_threshold, g2_max_false_acceptances
from .refusals import (
    ContractMandatoryDiagnosticMismatch, ContractMandatoryDiagnosticMissing,
    ContractReleaseBindingUnclassified, ContractReleaseBoundDirectionMismatch,
    ContractReleaseConfidenceRuleMismatch, ContractReleaseDerivedThresholdMismatch,
    ContractReleaseEndpointMismatch, ContractReleaseImplicationBroken,
    ContractReleaseReplicateCountMismatch, ContractReleaseTargetMismatch,
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
            pooling=_c(no_pool, EXACT, CONTRACT, r2,
                       "'at every declared geometry' requires a per-field figure"),
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
