"""Frozen design-contract to validation-plan conformance, before any RNG.

This is a separate authority edge from Markdown/JSON coherence.  The rows below
are enumerable: each names both authority paths, its relation and its reason.
The contract is upstream; agreement between two plan renderings cannot amend it.
No model state is advanced here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .classification import size_boundary
from .dispositions import cp_upper
from .release_authority import CONTRACT as RELEASE_CONTRACT
from .release_authority import release_binding_specification
from .drag_domain import CONTRACT_SECTION as DRAG_DOMAIN_SECTION
from .refusals import (
    BranchADomainAuthorityMismatch,
    ContractBindingUnclassified, ContractFieldDuplicate, ContractFieldSetMismatch,
    ContractGeneratingParameterMismatch, ContractReferenceFieldMismatch,
    ContractRelaxationRuleMismatch, ContractTrueBridgeBetaMismatch,
)

EXACT = "EXACT"
DERIVED = "DERIVED"
CASE_SPECIFIC_ALLOWED_OVERRIDE = "CASE_SPECIFIC_ALLOWED_OVERRIDE"
NOT_APPLICABLE = "NOT_APPLICABLE"
#: Bound, but by the RELEASE-AUTHORITY layer rather than here. Named
#: explicitly so a release-bearing leaf can never read as "not applicable".
DELEGATED_TO_RELEASE_AUTHORITY = "DELEGATED_TO_RELEASE_AUTHORITY"
#: Bound, but by the DRAG-DOMAIN layer. Same reasoning: the Branch-A measured
#: input domain is checked leaf by leaf against a rule pinned ABOVE this contract,
#: so its leaves are bound authority, never unbound text.
DELEGATED_TO_DRAG_DOMAIN_AUTHORITY = "DELEGATED_TO_DRAG_DOMAIN_AUTHORITY"

DRAG_DOMAIN_DELEGATION = (
    "Branch-A measured-input-domain authority. Every leaf is compared against the "
    "approved rule pinned in e1a_v4.validation.drag_domain, which is upstream of this "
    "contract, so the contract cannot define its own expected eta/a domain. The plan "
    "restates one derived rendering, bound EXACTly by its own row.")


@dataclass(frozen=True)
class ContractPlanBinding:
    contract_path: str
    plan_path: str
    relationship: str
    reason: str
    expected: Any
    actual: Any


def _case_map(plan: dict[str, Any]) -> dict[str, tuple[int, dict[str, Any]]]:
    cases = plan["cases"]
    ids = [case["case_id"] for case in cases]
    if len(ids) != len(set(ids)):
        raise ContractGeneratingParameterMismatch("cases: duplicate case_id")
    expected = (
        "C1_true_bridge_complete", "C2_geometry_false_rejection", "C3_g5_block",
        "C4_surrogate_validity", "C5_plug_in_branch_a",
        "C6_mode_resolution_boundary", "C7_false_bridge",
        "C8_blinded_scale_control",
    )
    if tuple(ids) != expected:
        raise ContractGeneratingParameterMismatch(
            f"cases: expected exact frozen C1-C8 order {expected}, got {tuple(ids)}")
    return {case["case_id"]: (i, case) for i, case in enumerate(cases)}


def _contract_beta(contract: dict[str, Any]) -> float:
    prediction = contract["scientific_target"]["prediction"]
    if not prediction.startswith("beta = 1 and kappa = kB at every tested field;"):
        raise ContractTrueBridgeBetaMismatch(
            "scientific_target.prediction does not state the E1a beta=1 benchmark")
    return 1.0


def _contract_tau(contract: dict[str, Any]) -> str:
    rule = contract["relaxation_time_rule"]
    prefix = "tau_r = gamma(T)/k_r with gamma = 6 pi eta(T) a;"
    if not rule.startswith(prefix) or "single tau_c for all fields is WRONG" not in rule:
        raise ContractRelaxationRuleMismatch(
            "relaxation_time_rule no longer states the per-mode Stokes-drag rule")
    # The plan renders the first clause more compactly; the rejected single-tau
    # clause remains mandatory in the contract and is checked above.
    return prefix[:-1].replace(" with ", ", ")


def binding_specification(contract: dict[str, Any], plan: dict[str, Any],
                          root: str = ".") -> tuple[ContractPlanBinding, ...]:
    """Construct all currently represented contract->plan relations from sources.

    An absent/misnamed field is checked before this expansion.  A binding is a
    path-and-reason record, not merely a comparison made somewhere in code.
    """
    rows: list[ContractPlanBinding] = []

    def add(cp: str, pp: str, relation: str, reason: str,
            expected: Any, actual: Any) -> None:
        rows.append(ContractPlanBinding(cp, pp, relation, reason, expected, actual))

    cfields = contract["fields"]
    pfields = plan["generating_model"]["per_field"]
    add("fields[*].id", "generating_model.per_field[*].id", EXACT,
        "The contract JSON supplies the complete ordered field set.",
        [f["id"] for f in cfields], [f["id"] for f in pfields])
    beta = _contract_beta(contract)
    tau = _contract_tau(contract)
    for i, (source, target) in enumerate(zip(cfields, pfields)):
        for key in ("k_uN_per_m", "T_K", "rot_deg", "reference"):
            add(f"fields[{i}].{key}", f"generating_model.per_field[{i}].{key}",
                EXACT, "The plan restates a physical field primitive.",
                source[key], target.get(key))
        add("scientific_target.prediction", f"generating_model.per_field[{i}].beta_true",
            DERIVED, "Ordinary true-bridge field beta is the contract's benchmark prediction.",
            beta, target.get("beta_true"))
        add("relaxation_time_rule", f"generating_model.per_field[{i}].tau_rule",
            DERIVED, "Compact rendering of the same per-mode Stokes-drag law.",
            tau, target.get("tau_rule"))

    domain = contract.get(DRAG_DOMAIN_SECTION)
    if not isinstance(domain, dict) or "plan_rendering" not in domain:
        raise BranchADomainAuthorityMismatch(
            f"the design contract carries no usable {DRAG_DOMAIN_SECTION}.plan_rendering; "
            "the plan's restatement of the Branch-A measured input domain would then "
            "have no upstream authority to conform to")
    add(f"{DRAG_DOMAIN_SECTION}.plan_rendering",
        "generating_model.branch_a.measured_input_domain", EXACT,
        "The execution-facing plan restates the approved admissible domain of the "
        "Branch-A measured primitives eta and a verbatim. The contract is upstream: a "
        "plan rendering may restate the domain, never weaken it.",
        domain["plan_rendering"],
        plan["generating_model"]["branch_a"].get("measured_input_domain"))

    direct = (
        ("hypothetical_uncertainty_scenario.dt_s", "generating_model.branch_b.dt_s"),
        ("hypothetical_uncertainty_scenario.T_total_s", "generating_model.branch_b.T_total_s"),
        ("endpoints.P1_geometry.alpha_geom", "adopted_rules_unchanged.alpha_geom"),
        ("endpoints.P1_geometry.alpha_1", "adopted_rules_unchanged.alpha_1"),
        ("endpoints.P1_geometry.alpha_2", "adopted_rules_unchanged.alpha_2"),
        ("endpoints.P2_cross_field.delta_cross", "adopted_rules_unchanged.delta_cross"),
        ("endpoints.P2_cross_field.z_cross", "adopted_rules_unchanged.z_cross"),
        ("endpoints.P2_cross_field.multiplicity_correction", "adopted_rules_unchanged.multiplicity_correction"),
        ("endpoints.P3_absolute.delta_abs", "adopted_rules_unchanged.delta_abs"),
        ("endpoints.P3_absolute.z_abs", "adopted_rules_unchanged.z_abs"),
        ("endpoints.P3_absolute.applies_to", "adopted_rules_unchanged.P3_applies_to"),
        ("endpoints.P4_entropy.classification", "adopted_rules_unchanged.P4_classification"),
        ("mode_resolution.theta_cap_deg", "adopted_rules_unchanged.theta_cap_deg"),
        ("refusal_semantics.rank_tol", "adopted_rules_unchanged.rank_tol"),
        ("complete_pipeline.target_true_bridge_success", "adopted_rules_unchanged.pipeline_target"),
    )

    def at(obj: dict[str, Any], path: str) -> Any:
        for part in path.split("."):
            obj = obj[part]
        return obj

    for cp, pp in direct:
        add(cp, pp, EXACT, "Exact contract value restated by the validation plan.",
            at(contract, cp), at(plan, pp))

    p1_gates = contract["endpoints"]["P1_geometry"]["gates"]
    if p1_gates != ["G1_trace_normalised_shape", "G2_whitened_spectral_spread",
                    "G3_principal_angles", "G4_eigenvalue_ratios",
                    "G5_fourth_moment_max_abs_excess_kurtosis"]:
        raise ContractBindingUnclassified(
            "endpoints.P1_geometry.gates: calibration-block derivation requires review")
    add("endpoints.P1_geometry.gates", "calibration.gates", DERIVED,
        "Block-1 calibrates G1-G4; G5 is the separate fourth-moment block.",
        ["G1", "G2", "G3", "G4"], plan["calibration"].get("gates"))

    scenario = contract["hypothetical_uncertainty_scenario"]
    add("hypothetical_uncertainty_scenario.sigma_psi_deg",
        "author_dispositions.G3.primary_release_scenario", EXACT,
        "The primary orientation uncertainty equals the scenario's declared value.",
        scenario["sigma_psi_deg"],
        plan["author_dispositions"]["G3"].get("primary_release_scenario"))
    uncertainty = ("frozen candidate scenario: sigma_k = "
                   f"{scenario['sigma_k'] * 100:g}%, sigma_cm = "
                   f"{scenario['sigma_cm'] * 100:g}%, sigma_T = "
                   f"{scenario['sigma_T_K']:g} K")

    cases = _case_map(plan)
    size_requirement = contract["synthetic_validation_requirements"][2]
    if size_requirement != ("achieved joint gate size: Clopper-Pearson one-sided "
                            "95% UPPER bound <= 3%, R = 400, at every declared geometry"):
        raise ContractBindingUnclassified(
            "synthetic_validation_requirements[2]: size implication requires review")
    c2_i, c2 = cases["C2_geometry_false_rejection"]
    c2_alpha = contract["endpoints"]["P1_geometry"]["alpha_geom"]
    c2_limit = size_boundary(400, c2_alpha)
    if cp_upper(c2_limit, 400) > 0.03:
        raise ContractGeneratingParameterMismatch(
            "C2 nominal-inflation acceptance no longer entails the contract's "
            "one-sided 95% CP upper <= 3% requirement")
    add("synthetic_validation_requirements[2]", f"cases[{c2_i}].replicate_count",
        DERIVED, "Contract's achieved-size check declares R=400.",
        400, c2.get("replicate_count"))
    c2_derived = plan["size_validation_semantics"]["derived_boundaries"]["C2"]
    if (c2_derived.get("boundary") != c2_limit or
            c2_derived.get("nominal_alpha") != c2_alpha):
        raise ContractGeneratingParameterMismatch(
            "C2 derived boundary or nominal alpha disagrees with the contract")
    g3_source = scenario["sigma_psi_deg_classification"]
    orientation_rows = (
        ("sigma_psi_0p0", g3_source["secondary_lower_uncertainty_sensitivity"][0], "SECONDARY", False),
        ("sigma_psi_0p2", g3_source["secondary_lower_uncertainty_sensitivity"][1], "SECONDARY", False),
        ("sigma_psi_0p5", g3_source["primary_release_scenario"], "PRIMARY", True),
        ("sigma_psi_1p0", g3_source["stress_robustness"][0], "STRESS", False),
    )
    for cid, (i, case) in cases.items():
        if cid in ("C1_true_bridge_complete", "C2_geometry_false_rejection",
                   "C3_g5_block", "C4_surrogate_validity"):
            suffix = ("; sigma_psi PRIMARY = 0.5 deg, with 0.0/0.2 deg secondary "
                      "and 1.0 deg stress, reported separately and never pooled "
                      "[disposition G3]") if cid != "C4_surrogate_validity" else ""
            add("hypothetical_uncertainty_scenario.sigma_k/sigma_cm/sigma_T_K",
                f"cases[{i}].branch_a_uncertainty", DERIVED,
                "Human uncertainty rendering derived from three contract primitives and G3.",
                uncertainty + suffix, case.get("branch_a_uncertainty"))
        if cid in ("C1_true_bridge_complete", "C2_geometry_false_rejection",
                   "C3_g5_block"):
            subs = case["subconditions"]
            if len(subs) != len(orientation_rows):
                raise ContractGeneratingParameterMismatch(
                    f"cases[{i}].subconditions: G3 needs four separately reported levels")
            for j, (sid, sigma, role, feeds) in enumerate(orientation_rows):
                for key, value in (("subcondition_id", sid), ("sigma_psi_deg", sigma),
                                   ("g3_role", role), ("feeds_primary_claim", feeds)):
                    add("hypothetical_uncertainty_scenario.sigma_psi_deg_classification",
                        f"cases[{i}].subconditions[{j}].{key}", DERIVED,
                        "G3 has one primary, two sensitivity and one stress level; no pooling.",
                        value, subs[j].get(key))
        if cid != "C6_mode_resolution_boundary":
            add("fields[*].id", f"cases[{i}].fields_affected", DERIVED,
                "The case uses all four declared physical fields.",
                [f["id"] for f in cfields], case.get("fields_affected"))
        if cid not in ("C7_false_bridge", "C8_blinded_scale_control"):
            add("scientific_target.prediction", f"cases[{i}].beta_truth", DERIVED,
                "C1-C6 retain the true-bridge beta; C6 is a geometry sensitivity.",
                beta, case.get("beta_truth"))

    grid_source = contract["synthetic_validation_requirements"][5]
    if grid_source != ("plug-in conditioning validated over sigma_k in {0, 0.5%, 1%} "
                       "x sigma_psi in {0, 0.2, 0.5, 1.0} deg"):
        raise ContractBindingUnclassified(
            "synthetic_validation_requirements[5]: C5 grid derivation requires review")
    c5_i, c5 = cases["C5_plug_in_branch_a"]
    c5_grid = [(k, psi) for k in (0.0, 0.005, 0.01)
               for psi in (0.0, 0.2, 0.5, 1.0)]
    if len(c5["subconditions"]) != len(c5_grid):
        raise ContractGeneratingParameterMismatch(
            f"cases[{c5_i}].subconditions: C5 grid must contain 12 cells")
    for j, (k, psi) in enumerate(c5_grid):
        for key, value in (("sigma_k", k), ("sigma_psi_deg", psi)):
            add("synthetic_validation_requirements[5]",
                f"cases[{c5_i}].subconditions[{j}].{key}", DERIVED,
                "C5 grid derives from the contract's declared 3x4 sensitivity set.",
                value, c5["subconditions"][j].get(key))

    # C7 values are the contract's declared false-bridge controls.  The text is
    # checked verbatim so these numbers cannot become free-standing code policy.
    source = contract["false_bridge_controls"]["controls"][3]
    frozen = ("non-commensurable alternatives (1,1.06,1,1), "
              "(1,0.93,1.05,1), (1,1,1,1.10), and a hard 2.5% single-field case")
    if source != frozen:
        raise ContractBindingUnclassified(
            "false_bridge_controls.controls[3]: C7 vector derivation requires review")
    c7_i, c7 = cases["C7_false_bridge"]
    add("false_bridge_controls.controls[3]", f"cases[{c7_i}].beta_truth",
        CASE_SPECIFIC_ALLOWED_OVERRIDE, "C7 alone declares deliberate false bridges.",
        "per alternative", c7.get("beta_truth"))
    vectors = (
        ("alt_1_06", [1, 1.06, 1, 1]),
        ("alt_0_93_1_05", [1, 0.93, 1.05, 1]),
        ("alt_1_10", [1, 1, 1, 1.10]),
        ("hard_1_025", [1, 1.025, 1, 1]),
    )
    sub = c7["subconditions"]
    if [s.get("subcondition_id") for s in sub] != [v[0] for v in vectors]:
        raise ContractTrueBridgeBetaMismatch("C7 subcondition IDs/order differ from declared alternatives")
    for j, (name, value) in enumerate(vectors):
        add("false_bridge_controls.controls[3]", f"cases[{c7_i}].subconditions[{j}].beta_true",
            CASE_SPECIFIC_ALLOWED_OVERRIDE, f"Frozen C7 alternative {name}; not a true-bridge field.",
            value, sub[j].get("beta_true"))

    c8_i, c8 = cases["C8_blinded_scale_control"]
    g1 = contract["synthetic_validation_release_criteria"]["G1_blinded_scale_control"]
    add("synthetic_validation_release_criteria.G1_blinded_scale_control.scientific_target",
        f"cases[{c8_i}].beta_truth", DERIVED,
        "C8's 1/c is a blinded Branch-A scale reading; underlying beta remains one.",
        "1/c on the blinded branch", c8.get("beta_truth"))
    add("synthetic_validation_release_criteria.G1_blinded_scale_control.scale_factors",
        f"cases[{c8_i}].subconditions[0].scale_factors", EXACT,
        "The paired C8 factors are contract-bound measurement transforms, not beta overrides.",
        g1["scale_factors"], c8["subconditions"][0].get("scale_factors"))
    for disposition, source in (("G1", "G1_blinded_scale_control"),
                                ("G2", "G2_false_bridge_discrimination")):
        add(f"synthetic_validation_release_criteria.{source}",
            f"author_dispositions.{disposition}", EXACT,
            "The complete adopted release disposition is restated, not selectively copied.",
            contract["synthetic_validation_release_criteria"][source],
            plan["author_dispositions"].get(disposition))
    g3 = contract["hypothetical_uncertainty_scenario"]["sigma_psi_deg_classification"]
    for key in ("primary_release_scenario", "secondary_lower_uncertainty_sensitivity",
                "stress_robustness", "grid_source", "primary_claim", "reporting_rule",
                "status", "disposition"):
        add(f"hypothetical_uncertainty_scenario.sigma_psi_deg_classification.{key}",
            f"author_dispositions.G3.{key}", EXACT,
            "G3 orientation scenario is frozen by the design contract.",
            g3[key], plan["author_dispositions"]["G3"].get(key))
    # Rows bound by the RELEASE-AUTHORITY layer count as covered here. An auditor
    # found requirements[3] -- the contract's own R = 300 and >= 0.90 for the
    # complete pipeline -- classified NOT_APPLICABLE while the plan restated it.
    # A release-bearing leaf must be BOUND somewhere, never merely excused.
    represented = tuple(rows)
    for row in release_binding_specification(contract, plan, root):
        if row.authority_source != RELEASE_CONTRACT:
            continue
        if _covered(row.authority_path, represented):
            continue
        add(row.authority_path, row.plan_path, DELEGATED_TO_RELEASE_AUTHORITY,
            f"bound by e1a_v4.validation.release_authority as {row.relationship}: "
            f"{row.reason}", None, None)
        represented = tuple(rows)   # the new row now covers its own leaf
    for section in EXECUTION_CONTRACT_SECTIONS:
        for path in _leaf_paths(contract[section], section):
            if _covered(path, represented):
                continue
            if path.split(".", 1)[0] == DRAG_DOMAIN_SECTION:
                add(path, "(bound by e1a_v4.validation.drag_domain)",
                    DELEGATED_TO_DRAG_DOMAIN_AUTHORITY, DRAG_DOMAIN_DELEGATION,
                    None, None)
                continue
            reason = _not_repeated_reason(path)
            if reason is None:
                raise ContractBindingUnclassified(
                    f"execution-relevant contract leaf {path!r} has no binding or "
                    "explicit NOT_APPLICABLE classification")
            add(path, "(not independently restated in validation plan)",
                NOT_APPLICABLE, reason, None, None)
    return tuple(rows)


EXECUTION_CONTRACT_SECTIONS = (
    "scientific_target", "information_separation", "fields",
    "relaxation_time_rule", "branch_a_measured_input_domain",
    "endpoints", "entropy_semantics", "mode_resolution",
    "hypothetical_uncertainty_scenario", "complete_pipeline",
    "false_bridge_controls", "refusal_semantics",
    "synthetic_validation_requirements", "synthetic_validation_release_criteria",
    "forbidden_mechanisms", "authorization_boundaries",
)


def _leaf_paths(value: Any, prefix: str) -> list[str]:
    if isinstance(value, dict):
        return [path for key, child in value.items()
                for path in _leaf_paths(child, f"{prefix}.{key}")]
    if prefix == "fields" and isinstance(value, list):
        return [path for i, child in enumerate(value)
                for path in _leaf_paths(child, f"fields[{i}]")]
    if prefix in ("false_bridge_controls.controls", "synthetic_validation_requirements") \
            and isinstance(value, list):
        return [path for i, child in enumerate(value)
                for path in _leaf_paths(child, f"{prefix}[{i}]")]
    return [prefix]


def _covered(path: str, rows: tuple[ContractPlanBinding, ...]) -> bool:
    for row in rows:
        cp = row.contract_path
        if cp == path or path.startswith(cp + "."):
            return True
        if cp == "fields[*].id" and path.startswith("fields[") and path.endswith("].id"):
            return True
        if cp == "hypothetical_uncertainty_scenario.sigma_k/sigma_cm/sigma_T_K" and path in (
            "hypothetical_uncertainty_scenario.sigma_k",
            "hypothetical_uncertainty_scenario.sigma_cm",
            "hypothetical_uncertainty_scenario.sigma_T_K",
        ):
            return True
    return False


NOT_REPEATED_CONTRACT_LEAVES = frozenset((
    "complete_pipeline.budget_terms.3x_mode_resolution_crossing_5deg",
    "complete_pipeline.budget_terms.4x_alpha_geom",
    "complete_pipeline.budget_terms.4x_eps_cal",
    "complete_pipeline.budget_terms.4x_rank_neff_refusal",
    "complete_pipeline.budget_terms.P4_failure",
    "complete_pipeline.budget_terms.one_minus_pi_P2_and_P3",
    "complete_pipeline.complete_pass_event",
    "complete_pipeline.denominator",
    "complete_pipeline.input_labels.alpha_geom",
    "complete_pipeline.input_labels.eps_cal",
    "complete_pipeline.input_labels.mode_resolution_crossing",
    "complete_pipeline.input_labels.pi_P2_and_P3",
    "complete_pipeline.input_labels.rank_neff_bound",
    "complete_pipeline.input_labels.union_inequality",
    "complete_pipeline.is_demonstrated_empirical_power",
    "complete_pipeline.is_unconditional_lower_bound_on_implemented_pipeline",
    "complete_pipeline.raw_union_expression",
    "complete_pipeline.reported_lower_bound",
    "complete_pipeline.required_interpretation",
    "complete_pipeline.standing_qualifications",
    "complete_pipeline.supporting.integration",
    "complete_pipeline.supporting.pi_P2",
    "complete_pipeline.supporting.pi_P2_and_P3",
    "complete_pipeline.supporting.pi_P3_all_four_fields",
    "complete_pipeline.union_inequality",
    "complete_pipeline.union_inequality_label",
    "endpoints.P1_geometry.independence_between_blocks",
    "endpoints.P1_geometry.mandatory",
    "endpoints.P1_geometry.procedure",
    "endpoints.P1_geometry.type",
    "endpoints.P2_cross_field.comparisons",
    "endpoints.P2_cross_field.forbidden_reinterpretations",
    "endpoints.P2_cross_field.half_width",
    "endpoints.P2_cross_field.mandatory",
    "endpoints.P2_cross_field.ratio",
    "endpoints.P2_cross_field.rule",
    "endpoints.P2_cross_field.sigma_cm_treatment",
    "endpoints.P2_cross_field.status",
    "endpoints.P2_cross_field.test_type",
    "endpoints.P2_cross_field.type",
    "endpoints.P3_absolute.half_width",
    "endpoints.P3_absolute.mandatory",
    "endpoints.P3_absolute.multiplicity_correction",
    "endpoints.P3_absolute.non_estimated_field",
    "endpoints.P3_absolute.provenance.adopted",
    "endpoints.P3_absolute.provenance.adopted_before",
    "endpoints.P3_absolute.provenance.historically_committed",
    "endpoints.P3_absolute.provenance.supersedes",
    "endpoints.P3_absolute.rule",
    "endpoints.P3_absolute.test_type",
    "endpoints.P3_absolute.type",
    "endpoints.P4_entropy.checks",
    "endpoints.P4_entropy.mandatory",
    "endpoints.P4_entropy.not_experimental_evidence",
    "endpoints.P4_entropy.reads_branch_B_data",
    "endpoints.P4_entropy.stochastic_failure_probability_after_passing",
    "false_bridge_controls.alpha_geom_sensitivity",
    "false_bridge_controls.defined_separately_from_true_bridge_target",
    "false_bridge_controls.no_post_hoc_tuning",
    "false_bridge_controls.controls[0]",
    "false_bridge_controls.controls[1]",
    "false_bridge_controls.controls[2]",
    "false_bridge_controls.controls[4]",
    "false_bridge_controls.controls[5]",
    "hypothetical_uncertainty_scenario.label",
    "hypothetical_uncertainty_scenario.sigma_fs_derived",
    "hypothetical_uncertainty_scenario.sigma_fs_formula",
    "hypothetical_uncertainty_scenario.sufficiency",
    "information_separation.accessible_directions",
    "information_separation.authorised_branch_A_routes",
    "information_separation.branch_A",
    "information_separation.branch_B",
    "information_separation.forbidden_branch_A_routes",
    "information_separation.unblinding",
    "mode_resolution.basis",
    "mode_resolution.rule",
    "mode_resolution.split_probability_truly_circular_at_sigma_k_0p34pct.10_deg",
    "mode_resolution.split_probability_truly_circular_at_sigma_k_0p34pct.20_deg",
    "mode_resolution.split_probability_truly_circular_at_sigma_k_0p34pct.5_deg",
    "mode_resolution.status",
    "refusal_semantics.reconciliation",
    "refusal_semantics.statuses",
    "scientific_target.H_theta",
    "scientific_target.V_theta",
    "scientific_target.beta",
    "scientific_target.central_endpoint",
    "scientific_target.estimator",
    "scientific_target.estimator_constraint",
    "synthetic_validation_release_criteria.note",
    "synthetic_validation_requirements[0]",
    "synthetic_validation_requirements[1]",
    "authorization_boundaries.E1b",
    "authorization_boundaries.analytical_design",
    "authorization_boundaries.bounded_implementation",
    "authorization_boundaries.physical_execution",
    "authorization_boundaries.pre_execution_validation",
    "authorization_boundaries.preregistration",
    "authorization_boundaries.stage_B",
    "authorization_boundaries.synthetic_validation_campaign",
    "entropy_semantics.delta_S_constr",
    "entropy_semantics.delta_s_med",
    "entropy_semantics.delta_s_sys",
    "entropy_semantics.delta_s_tot",
    "entropy_semantics.finite_bath_remainder.any_decision_rule_depends_on_it",
    "entropy_semantics.finite_bath_remainder.authoritative_form",
    "entropy_semantics.finite_bath_remainder.ensemble_and_boundary",
    "entropy_semantics.finite_bath_remainder.heat_capacity",
    "entropy_semantics.finite_bath_remainder.is_statistical_endpoint",
    "entropy_semantics.finite_bath_remainder.non_normative_illustration",
    "entropy_semantics.finite_bath_remainder.numerical_value_in_design",
    "entropy_semantics.finite_bath_remainder.relative_leading_correction",
    "entropy_semantics.finite_bath_remainder.result",
    "entropy_semantics.four_objects_never_equated",
    "entropy_semantics.no_generalisation_to",
    "entropy_semantics.prohibited",
    "entropy_semantics.required_conditions",
    "forbidden_mechanisms",
))


def _not_repeated_reason(path: str) -> str | None:
    """Explicit scope classification, not a default acceptance of unknown keys.

    These leaves remain authoritative in the frozen contract or analysis code;
    NOT_APPLICABLE means only that no independent plan scalar restates them.
    """
    roots = {
        "scientific_target": "Formula/interpretation fixed in the analysis contract, not repeated as a plan primitive.",
        "information_separation": "Analysis information boundary, not a generating-plan parameter.",
        "endpoints": "Endpoint rule read from the contract by analysis code; no separate plan primitive for this leaf.",
        "entropy_semantics": "P4 physical entropy meaning is fixed in the contract and analysis; not a generator primitive.",
        "mode_resolution": "Mode-resolution rationale or derived diagnostic, not a separate plan primitive.",
        "hypothetical_uncertainty_scenario": "Scenario derivation or interpretation, not independently entered in the plan.",
        "complete_pipeline": "Analytic power-budget explanation, not an independent plan parameter.",
        "false_bridge_controls": "Control description; C7 alternatives and C8 scales are bound separately.",
        "refusal_semantics": "Runtime status vocabulary fixed in contract and implementation, not repeated as a plan scalar.",
        "synthetic_validation_requirements": "Normative release requirements specialised into the frozen cases; no literal one-to-one plan scalar.",
        "synthetic_validation_release_criteria": "Release explanation; G1/G2 dispositions and primary G3 settings are bound separately.",
        "forbidden_mechanisms": "Contract prohibition implemented by analysis; not a plan choice.",
        "authorization_boundaries": "Operational authorization gate, not a scientific generating parameter.",
    }
    root = path.split(".", 1)[0].split("[", 1)[0]
    return roots.get(root) if path in NOT_REPEATED_CONTRACT_LEAVES else None


def binding_inventory(contract: dict[str, Any], plan: dict[str, Any],
                      root: str = ".") -> dict[str, int]:
    """Measure coverage over actual contract leaves, not just the authored rows."""
    rows = binding_specification(contract, plan, root)
    result = {name: sum(row.relationship == name for row in rows)
              for name in (EXACT, DERIVED, CASE_SPECIFIC_ALLOWED_OVERRIDE,
                           DELEGATED_TO_RELEASE_AUTHORITY,
                           DELEGATED_TO_DRAG_DOMAIN_AUTHORITY, NOT_APPLICABLE)}
    result["execution_relevant_contract_bindings"] = len(rows)
    result["plan_bound_bindings"] = sum(
        row.relationship not in (NOT_APPLICABLE, DELEGATED_TO_RELEASE_AUTHORITY,
                                 DELEGATED_TO_DRAG_DOMAIN_AUTHORITY)
        for row in rows)
    leaves = [path for section in EXECUTION_CONTRACT_SECTIONS
              for path in _leaf_paths(contract[section], section)]
    result["execution_relevant_contract_leaves"] = len(leaves)
    result["unclassified_execution_relevant"] = sum(
        row.relationship not in result or not row.reason or not row.contract_path
        or not row.plan_path for row in rows) + sum(
            not _covered(path, rows) for path in leaves)
    return result


def require_contract_plan_conformance(contract: dict[str, Any],
                                      plan: dict[str, Any],
                                      root: str = ".") -> None:
    cfields = contract["fields"]
    pfields = plan["generating_model"]["per_field"]
    cids, pids = [f["id"] for f in cfields], [f["id"] for f in pfields]
    if len(cids) != len(set(cids)):
        raise ContractFieldDuplicate("contract.fields itself repeats a field ID")
    if len(pids) != len(set(pids)):
        raise ContractFieldDuplicate(f"generating_model.per_field repeats a field ID: {pids}")
    if pids != cids:
        raise ContractFieldSetMismatch(
            f"generating_model.per_field IDs/order {pids} != contract.fields {cids}")
    cref = [f["id"] for f in cfields if f["reference"] is True]
    pref = [f["id"] for f in pfields if f.get("reference") is True]
    if len(cref) != 1 or pref != cref:
        raise ContractReferenceFieldMismatch(
            f"reference fields: plan {pref}, contract {cref}; exactly one is required")
    rows = binding_specification(contract, plan, root)
    if binding_inventory(contract, plan, root)["unclassified_execution_relevant"]:
        raise ContractBindingUnclassified("contract->plan binding specification is incomplete")
    for row in rows:
        if row.relationship in (NOT_APPLICABLE, DELEGATED_TO_RELEASE_AUTHORITY,
                                DELEGATED_TO_DRAG_DOMAIN_AUTHORITY):
            continue
        if row.expected != row.actual or type(row.expected) is not type(row.actual):
            detail = (f"{row.plan_path} != {row.contract_path}: "
                      f"plan {row.actual!r}, contract-derived {row.expected!r}")
            if row.plan_path.endswith(".beta_true") or row.plan_path.endswith(".beta_truth"):
                raise ContractTrueBridgeBetaMismatch(detail)
            if row.plan_path.endswith(".tau_rule"):
                raise ContractRelaxationRuleMismatch(detail)
            if row.plan_path.endswith(".measured_input_domain"):
                raise BranchADomainAuthorityMismatch(detail)
            raise ContractGeneratingParameterMismatch(detail)
