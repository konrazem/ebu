"""The approved E1a passive-drag primitive input domain, and its bindings.

WHY THIS MODULE EXISTS
    `E1A_V4_PROSPECTIVE_DESIGN.md` section 14 already declares the admissible
    domain of the measured STIFFNESS -- "H not symmetric / not positive definite
    / dimension mismatch" refuses as REFUSED_BRANCH_A_INVALID -- and section 3
    already fixes the FORM of the drag coefficient, `gamma = 6 pi eta(T) a`.
    Neither stated the admissible domain of the two measured quantities that
    relation consumes. The F2 authority reconstruction
    (`docs/e1a/E1A_V4_NEGATIVE_STIFFNESS_GAMMA_AUTHORITY_RECONSTRUCTION.md`)
    established that gap and showed it could not be closed by derivation: the
    repository had already recorded it twice, as the driver's coded
    UNDECLARED_FIELD_INPUTS refusal and as the relaxation-domain report's
    "SHARED-DRAG DOMAIN AUTHORITY REQUIRED" section.

    The author then made the prospective decision this module carries.

WHERE THE RULE LIVES
    FROZEN DESIGN AUTHORITY   docs/e1a/E1A_V4_PROSPECTIVE_DESIGN.md  section 3.1
                              docs/e1a/e1a_v4_design_contract.json
                                  branch_a_measured_input_domain
            |
    THIS MODULE               the APPROVED RULE, pinned, with the expected
                              rendering of every representation above and below
            |
    MACHINE PLAN  ->  MARKDOWN PLAN

WHY THE EXPECTATION IS PINNED HERE
    The contract is the machine authority for E1a decision rules, and the design
    document is its normative human rendering. If the checker read the expected
    domain out of the document it is checking, a contract edited to `eta >= 0`
    would validate itself, and a contract edited together with its Markdown pair
    would be coherently wrong. The approved values are therefore held HERE, in a
    module whose own hash is part of the execution identity, and EVERY normative
    representation is GENERATED from them and compared exactly. That is the same
    construction the C3/C4 per-field amendment uses in `release_authority.py`,
    for the same reason.

WHAT THIS MODULE IS NOT
    It is NOT the runtime. Nothing here is called by `e1a_v4.branch_a`, by
    Branch-A production, by recovery, by calibration locking or by Branch-B
    launch. The runtime is knowingly BEHIND this authority and reconciling it is
    separate authorised work (F2e). `classify_drag_inputs` below is the pure
    statement of the approved disposition, available to authority checks and to
    that later reconciliation; wiring it into production here would be
    implementing F2e without its independent audit.

    It also does NOT choose the actual viscosity or bead-radius values, a
    viscosity model, a bead specification or any measurement uncertainty for
    them. Those are F4 -- field construction / absolute drag inputs -- and they
    remain OPEN. A test asserts that no such value can enter this authority.

NO RNG. Parsing, arithmetic and comparison only. No model state is advanced.
"""

from __future__ import annotations

import math
import os
from dataclasses import dataclass
from typing import Any, Mapping

from .refusals import (
    BranchADomainAuthorityMismatch, BranchADomainScopeViolation,
    BranchADomainUnclassified,
)

DESIGN_DOCUMENT = "docs/e1a/E1A_V4_PROSPECTIVE_DESIGN.md"

#: The contract section this amendment owns.
CONTRACT_SECTION = "branch_a_measured_input_domain"
#: The plan key that restates it for the execution-facing rendering.
PLAN_PATH = "generating_model.branch_a.measured_input_domain"

#: The prospective disposition identifier, continuing the plan's G1..G5 sequence.
DISPOSITION_ID = "G6"
DISPOSITION_STATUS = "CLOSED PROSPECTIVELY"
DISPOSITION_AFFECTS = "Branch-A field construction, every case"
DISPOSITION_NOTE = "G6, closed prospectively before execution"

#: ---------------------------------------------------------------------------
#: THE APPROVED DOMAIN. Strictly positive, finite, and REQUIRED, for each
#: primitive INDIVIDUALLY. These four facts are the whole scientific decision;
#: every string below renders them and every check compares against them.
#: ---------------------------------------------------------------------------
LOWER_BOUND = 0
LOWER_BOUND_INCLUSIVE = False
UPPER_BOUND = None
REQUIRE_FINITE = True
REQUIRED = True

#: Verdicts. Each is an EXISTING repository spelling, not a new category.
MISSING_VERDICT = "UNDECLARED_FIELD_INPUTS"
PRESENT_INVALID_VERDICT = "REFUSED_BRANCH_A_INVALID"
REPRESENTABILITY_VERDICT = "BRANCH_A_MEASUREMENT_INVALID"
ADMISSIBLE = "ADMISSIBLE"

#: The two rules that would be INSUFFICIENT on their own. Named in authority so
#: that proposing either is a recorded regression rather than a plausible edit.
INSUFFICIENT_RULES = (
    "gamma > 0 alone, with the primitive eta and a domains unrestricted",
    "tau_r > 0 alone, with the primitive eta and a domains unrestricted",
)

#: F4 inputs this amendment deliberately does NOT supply. A value for any of
#: them appearing inside this authority is a scope violation, not an upgrade.
F4_NOT_DECLARED_HERE = (
    "the actual dynamic viscosity values",
    "the viscosity model eta(T)",
    "the actual bead radius",
    "measurement uncertainty for eta",
    "measurement uncertainty for a",
    "hardware provenance for those values",
)
F4_OPEN_ITEM = "F4 - field construction / absolute drag inputs"
F4_STATUS = "OPEN"

FINITE_REAL_MEANING = (
    "of the declared real numeric representation, and not NaN, not +infinity and not "
    "-infinity. A truthy or non-numeric representation is not a number and is never "
    "admissible.")

BENCHMARK_SCOPE = (
    "the declared E1a passive equilibrium optical-trap benchmark ONLY. This is NOT a "
    "universal physical assertion: negative effective viscosity, negative effective "
    "transport coefficients and active-matter effective parameters are OUTSIDE this "
    "benchmark, not denied by it.")

INDIVIDUALLY_BINDING = (
    "eta and a are each authoritative domain objects and are validated INDIVIDUALLY. A "
    "rule stated only on the product gamma is INSUFFICIENT: eta < 0 together with a < 0 "
    "gives gamma = 6 pi eta a > 0 and would masquerade as an admissible passive-drag "
    "construction. Neither eta nor a is persisted in the Branch-A publication preimage, "
    "so no downstream check can recover them.")

PRECEDENCE = (
    "the PHYSICAL-DOMAIN check on eta and a PRECEDES the numerical representability "
    "checks on the derived gamma and tau. The two are never conflated and neither is "
    "ever substituted for the other.")

BRANCH_A_CONSEQUENCE = (
    "A present but inadmissible primitive drag input can NEVER yield a VALID Branch-A "
    "status, a valid Branch-A publication, a valid calibration condition, a valid "
    "calibration lock or a valid Branch-B input. This is DERIVED from the existing "
    "REFUSED_BRANCH_A_INVALID lifecycle and introduces no second lifecycle.")

PLACEHOLDER_SUBSTITUTION = (
    "A neutral placeholder value MAY NOT substitute for the actual required measured "
    "field-construction input in any path that can produce an official valid Branch-A "
    "package. The existing UNDECLARED_FIELD_INPUTS lifecycle is preserved.")

#: The stiffness clause is QUOTED from design section 14 and is UNCHANGED. It is
#: restated only because the derived tau domain depends on it.
STIFFNESS_SOURCE = (
    "docs/e1a/E1A_V4_PROSPECTIVE_DESIGN.md section 14, UNCHANGED BY THIS AMENDMENT")
STIFFNESS_REQUIREMENT = (
    "H not symmetric / not positive definite / dimension mismatch -> "
    "REFUSED_BRANCH_A_INVALID")
STIFFNESS_CONSEQUENCE = (
    "Every retained mode satisfies lambda_r > 0; lambda_r < 0 and lambda_r = 0 were "
    "already invalid and are NOT reopened by this amendment.")

#: The frozen Stokes relation, quoted. This amendment does not alter it.
GAMMA_RELATION = "gamma(T_theta) = 6 pi eta(T_theta) a"
TAU_RELATION = "tau_r = gamma(T_theta)/k_r"


@dataclass(frozen=True)
class PrimitiveInput:
    """One Branch-A MEASURED primitive and its admissible domain."""

    key: str
    symbol: str
    meaning: str
    unit: str
    required: bool
    finite: bool
    lower_bound: int | float
    lower_bound_inclusive: bool
    upper_bound: None

    def admits(self, value: Any) -> bool:
        """Is `value` inside this declared domain? Strict about what a number is."""
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return False
        number = float(value)
        if self.finite and not math.isfinite(number):
            return False
        if self.lower_bound_inclusive:
            return number >= self.lower_bound
        return number > self.lower_bound

    def as_contract(self) -> dict[str, Any]:
        return {
            "symbol": self.symbol,
            "meaning": self.meaning,
            "unit": self.unit,
            "role": "BRANCH_A_MEASURED_PRIMITIVE",
            "required": self.required,
            "domain": {
                "finite": self.finite,
                "lower_bound": self.lower_bound,
                "lower_bound_inclusive": self.lower_bound_inclusive,
                "upper_bound": self.upper_bound,
            },
        }


@dataclass(frozen=True)
class DerivedQuantity:
    """A quantity whose domain FOLLOWS; never an independent sign convention."""

    key: str
    relation: str
    physical_domain: str
    independent_rule: bool

    def as_contract(self) -> dict[str, Any]:
        return {
            "relation": self.relation,
            "status": "DERIVED",
            "physical_domain": self.physical_domain,
            "independent_rule": self.independent_rule,
        }


@dataclass(frozen=True)
class PassiveDragDomainRule:
    """The complete approved amendment. One object; every rendering derives."""

    rule: str
    primitives: tuple[PrimitiveInput, ...]
    derived: tuple[DerivedQuantity, ...]
    missing_verdict: str
    present_invalid_verdict: str
    representability_verdict: str
    insufficient_rules: tuple[str, ...]
    scope: str

    def primitive(self, key: str) -> PrimitiveInput:
        for item in self.primitives:
            if item.key == key:
                return item
        raise BranchADomainAuthorityMismatch(
            f"the approved rule declares no primitive input {key!r}")


VISCOSITY = PrimitiveInput(
    key="viscosity",
    symbol="eta(T_theta)",
    meaning="dynamic viscosity of the suspending medium at the field temperature",
    unit="Pa s",
    required=REQUIRED,
    finite=REQUIRE_FINITE,
    lower_bound=LOWER_BOUND,
    lower_bound_inclusive=LOWER_BOUND_INCLUSIVE,
    upper_bound=UPPER_BOUND,
)

BEAD_RADIUS = PrimitiveInput(
    key="bead_radius",
    symbol="a",
    meaning="radius of the trapped bead",
    unit="m",
    required=REQUIRED,
    finite=REQUIRE_FINITE,
    lower_bound=LOWER_BOUND,
    lower_bound_inclusive=LOWER_BOUND_INCLUSIVE,
    upper_bound=UPPER_BOUND,
)

GAMMA = DerivedQuantity(
    key="gamma",
    relation=GAMMA_RELATION,
    physical_domain=(
        "finite and strictly positive FOR ADMISSIBLE PRIMITIVES. This positivity is a "
        "mathematical CONSEQUENCE of the primitive domains and the frozen Stokes "
        "relation, not an independent physical sign convention."),
    independent_rule=False,
)

TAU = DerivedQuantity(
    key="tau",
    relation=TAU_RELATION,
    physical_domain=(
        "finite and strictly positive FOR ADMISSIBLE PRIMITIVES AND ADMISSIBLE "
        "STIFFNESS. It follows from gamma > 0 together with the already-explicit "
        "lambda_r > 0 requirement, and is not an independent free scientific choice."),
    independent_rule=False,
)

APPROVED_RULE_TEXT = (
    "For every E1a field, the Branch-A dynamic-viscosity input eta(T_theta) must be a "
    "finite real number strictly greater than zero. The bead-radius input a must be a "
    "finite real number strictly greater than zero.")

#: THE approved rule. One instance; nothing else in the package constructs one for
#: official use.
PASSIVE_DRAG_DOMAIN_RULE = PassiveDragDomainRule(
    rule=APPROVED_RULE_TEXT,
    primitives=(VISCOSITY, BEAD_RADIUS),
    derived=(GAMMA, TAU),
    missing_verdict=MISSING_VERDICT,
    present_invalid_verdict=PRESENT_INVALID_VERDICT,
    representability_verdict=REPRESENTABILITY_VERDICT,
    insufficient_rules=INSUFFICIENT_RULES,
    scope=BENCHMARK_SCOPE,
)


# --------------------------------------------------------- the approved values
def require_approved_rule(rule: PassiveDragDomainRule = PASSIVE_DRAG_DOMAIN_RULE) -> None:
    """Refuse a rule object that is not the one the author approved.

    Pinning the rule in code stops a document from validating itself. This stops
    the PIN from being quietly weakened: the approved decision is strictly
    positive, finite, required, and binding on each primitive INDIVIDUALLY, and
    each of those four facts is asserted here against a literal rather than
    against whatever the object happens to carry.
    """
    if rule.rule != APPROVED_RULE_TEXT:
        raise BranchADomainAuthorityMismatch(
            "the pinned rule text is not the approved prospective decision")
    keys = tuple(item.key for item in rule.primitives)
    if keys != ("viscosity", "bead_radius"):
        raise BranchADomainAuthorityMismatch(
            f"the approved rule binds eta and a INDIVIDUALLY; this object binds {keys}. "
            "A rule stated only on the derived gamma or tau is insufficient: eta < 0 "
            "with a < 0 gives gamma > 0 and is indistinguishable downstream.")
    for item in rule.primitives:
        if not item.required:
            raise BranchADomainAuthorityMismatch(
                f"{item.key}: the approved domain REQUIRES the input; an optional "
                "primitive drag input is not the approved rule")
        if not item.finite:
            raise BranchADomainAuthorityMismatch(
                f"{item.key}: the approved domain requires a FINITE value; admitting "
                "NaN or an infinity is not the approved rule")
        if item.lower_bound != LOWER_BOUND:
            raise BranchADomainAuthorityMismatch(
                f"{item.key}: the approved lower bound is {LOWER_BOUND!r}, not "
                f"{item.lower_bound!r}")
        if item.lower_bound_inclusive:
            raise BranchADomainAuthorityMismatch(
                f"{item.key}: the approved domain is STRICTLY greater than zero; "
                "an inclusive lower bound admits a zero measurement and is a different "
                "scientific decision")
        if item.upper_bound is not None:
            raise BranchADomainAuthorityMismatch(
                f"{item.key}: the approved domain declares no upper bound; "
                f"{item.upper_bound!r} is a value this amendment does not set")
    derived = tuple(item.key for item in rule.derived)
    if derived != ("gamma", "tau"):
        raise BranchADomainAuthorityMismatch(
            f"the approved rule derives gamma and tau; this object derives {derived}")
    for item in rule.derived:
        if item.independent_rule:
            raise BranchADomainAuthorityMismatch(
                f"{item.key}: its positivity is DERIVED from the primitive domains and "
                "the frozen relations. Declaring it an independent rule would make four "
                "unrelated positivity choices out of one decision and two consequences.")
    if rule.derived[0].relation != GAMMA_RELATION or rule.derived[1].relation != TAU_RELATION:
        raise BranchADomainAuthorityMismatch(
            "the frozen Stokes and relaxation relations are not altered by this "
            "amendment; the pinned relations no longer quote them")
    if rule.missing_verdict != MISSING_VERDICT:
        raise BranchADomainAuthorityMismatch(
            f"a missing or undeclared input is {MISSING_VERDICT}, not "
            f"{rule.missing_verdict!r}: absence means the input is not possessed, not "
            "that a possessed value is outside the physical domain")
    if rule.present_invalid_verdict != PRESENT_INVALID_VERDICT:
        raise BranchADomainAuthorityMismatch(
            f"a present but inadmissible input is {PRESENT_INVALID_VERDICT}, not "
            f"{rule.present_invalid_verdict!r}")
    if rule.representability_verdict != REPRESENTABILITY_VERDICT:
        raise BranchADomainAuthorityMismatch(
            f"a numerical representability failure keeps the existing "
            f"{REPRESENTABILITY_VERDICT} semantics, not {rule.representability_verdict!r}")
    if rule.missing_verdict == rule.present_invalid_verdict:
        raise BranchADomainAuthorityMismatch(
            "missing input and present-invalid input are DIFFERENT states and may not "
            "share one scientific verdict")
    if rule.present_invalid_verdict == rule.representability_verdict:
        raise BranchADomainAuthorityMismatch(
            "a physical-domain failure and a numerical representability failure are "
            "DIFFERENT states and may not share one scientific verdict")
    if tuple(rule.insufficient_rules) != INSUFFICIENT_RULES:
        raise BranchADomainAuthorityMismatch(
            "the authority must name the gamma-only and tau-only rules as INSUFFICIENT; "
            f"this object names {tuple(rule.insufficient_rules)}")
    if rule.scope != BENCHMARK_SCOPE:
        raise BranchADomainAuthorityMismatch(
            "the approved scope is the E1a passive equilibrium optical-trap benchmark; "
            "a broader or narrower scope is a different decision")


# -------------------------------------------------------------- pure semantics
def is_admissible_primitive(value: Any,
                            primitive: PrimitiveInput = VISCOSITY) -> bool:
    """The approved domain test for one primitive input value."""
    return primitive.admits(value)


def classify_drag_inputs(inputs: Mapping[str, Any],
                         rule: PassiveDragDomainRule = PASSIVE_DRAG_DOMAIN_RULE
                         ) -> str:
    """The approved disposition for one field's primitive drag inputs.

    MISSING is resolved FIRST and is NEVER relabelled as a physical-domain
    failure: an input we do not possess has no value to be outside a domain.
    Returns the approved verdict string; it does not raise, because the caller
    that will eventually act on it (F2e) must distinguish the three outcomes.
    """
    absent = [item.key for item in rule.primitives
              if item.required and (item.key not in inputs or inputs[item.key] is None)]
    if absent:
        return rule.missing_verdict
    outside = [item.key for item in rule.primitives
               if not item.admits(inputs[item.key])]
    if outside:
        return rule.present_invalid_verdict
    return ADMISSIBLE


def gamma_of(viscosity: float, bead_radius: float) -> float:
    """The frozen Stokes relation, quoted. Used only to DEMONSTRATE the gap."""
    return 6.0 * math.pi * viscosity * bead_radius


def gamma_only_admits(viscosity: Any, bead_radius: Any) -> bool:
    """Would a gamma-only rule admit these primitives? The loophole, executable.

    Not an approved rule -- the opposite. It exists so the double-negative escape
    is closed by a reproduced behaviour rather than by an assertion about one.
    """
    if (isinstance(viscosity, bool) or isinstance(bead_radius, bool)
            or not isinstance(viscosity, (int, float))
            or not isinstance(bead_radius, (int, float))):
        return False
    gamma = gamma_of(float(viscosity), float(bead_radius))
    return math.isfinite(gamma) and gamma > 0.0


# ------------------------------------------------------- generated renderings
def render_contract_block(rule: PassiveDragDomainRule = PASSIVE_DRAG_DOMAIN_RULE
                          ) -> dict[str, Any]:
    """The EXACT object the design contract must carry. Generated, not read."""
    return {
        "disposition": DISPOSITION_NOTE,
        "scope": rule.scope,
        "rule": rule.rule,
        "finite_real_meaning": FINITE_REAL_MEANING,
        "primitive_inputs": {item.key: item.as_contract() for item in rule.primitives},
        "individually_binding": INDIVIDUALLY_BINDING,
        "insufficient_rules": list(rule.insufficient_rules),
        "derived_quantities": {item.key: item.as_contract() for item in rule.derived},
        "stiffness_precondition": {
            "source": STIFFNESS_SOURCE,
            "requirement": STIFFNESS_REQUIREMENT,
            "consequence": STIFFNESS_CONSEQUENCE,
        },
        "dispositions": {
            "missing_or_undeclared_input": {
                "meaning": "we do not possess the required physical input",
                "trigger": ("eta or a absent, undeclared, or not supplied through the "
                            "authorised field-construction source"),
                "verdict": rule.missing_verdict,
                "is_not": rule.present_invalid_verdict,
                "lifecycle": ("the existing input-availability refusal: the Branch-A "
                              "field construction inputs must be declared in frozen "
                              "authority, and thereby enter the execution identity, "
                              "BEFORE the seal is frozen"),
            },
            "present_but_inadmissible_input": {
                "meaning": ("we possess a value, but the value is outside the "
                            "admissible physical domain"),
                "trigger": "eta or a present and nonfinite, zero or negative",
                "verdict": rule.present_invalid_verdict,
                "is_not": rule.missing_verdict,
                "lifecycle": ("the existing Branch-A-invalid refusal; no new refusal "
                              "category is created"),
            },
            "numerical_representability_failure": {
                "meaning": ("the primitive inputs are physically admissible but the "
                            "required binary64 representation of a derived quantity is "
                            "not obtainable"),
                "trigger": ("underflow, overflow or any already-cleared representability "
                            "failure of the computed gamma or tau"),
                "verdict": rule.representability_verdict,
                "is_not": rule.present_invalid_verdict,
                "lifecycle": ("the existing Branch-A numerical and representability "
                              "rules, UNCHANGED by this amendment"),
            },
        },
        "precedence": PRECEDENCE,
        "branch_a_consequence": BRANCH_A_CONSEQUENCE,
        "placeholder_substitution": PLACEHOLDER_SUBSTITUTION,
        "values_not_set": {
            "declared_here": "the ADMISSIBLE DOMAIN only",
            "not_declared_here": list(F4_NOT_DECLARED_HERE),
            "remaining_open_item": F4_OPEN_ITEM,
            "status": F4_STATUS,
        },
        "timing": {
            "decided": "prospectively, before execution",
            "official_campaign_results_observed": False,
            "final_execution_seal_frozen": False,
            "execution_authorised": False,
        },
        "plan_rendering": render_plan_rendering(rule),
    }


def render_plan_rendering(rule: PassiveDragDomainRule = PASSIVE_DRAG_DOMAIN_RULE
                          ) -> str:
    """The EXACT string the validation plan's generating model must restate."""
    return (
        f"{rule.rule} The rule binds eta and a INDIVIDUALLY, never only their product: "
        f"eta < 0 with a < 0 gives gamma > 0 and would otherwise masquerade as an "
        f"admissible passive-drag construction. A MISSING or undeclared input is "
        f"{rule.missing_verdict}; a PRESENT but nonfinite, zero or negative input is "
        f"{rule.present_invalid_verdict}; a physically admissible input whose derived "
        f"gamma or tau is not representable keeps the existing "
        f"{rule.representability_verdict} semantics. gamma and tau are DERIVED and their "
        f"positivity follows; it is not an independent rule. "
        f"Domain only -- actual eta and a values remain OPEN ({F4_OPEN_ITEM}).")


def render_disposition_gap() -> str:
    """The EXACT `gap` text the plan's G6 disposition entry must carry."""
    return (
        "the frozen design fixed the FORM of the Branch-A drag coefficient -- "
        "tau_r = gamma(T)/k_r with gamma = 6 pi eta(T) a -- and the admissible domain of "
        "the measured STIFFNESS, but never the admissible domain of the two measured "
        "quantities that relation consumes. eta and a could therefore be nonfinite, zero "
        "or negative with no declared verdict, and because neither is persisted in the "
        "Branch-A publication preimage, eta < 0 together with a < 0 yields gamma > 0, "
        "positive relaxation times and a record byte-identical to a legitimate "
        "measurement. The gap was recorded twice by the implementation -- as the driver's "
        "coded UNDECLARED_FIELD_INPUTS refusal and as the relaxation-domain report's "
        "SHARED-DRAG DOMAIN AUTHORITY REQUIRED section -- and the F2 authority "
        "reconstruction established that no existing authority closed it.")


def render_disposition_resolution(
        rule: PassiveDragDomainRule = PASSIVE_DRAG_DOMAIN_RULE) -> str:
    """The EXACT `resolution` text the plan's G6 disposition entry must carry."""
    return (
        f"{rule.rule} Formally, for every declared field: eta(T_theta) in R with "
        f"0 < eta(T_theta) < infinity, and a in R with 0 < a < infinity. Finite real "
        f"means {FINITE_REAL_MEANING} {INDIVIDUALLY_BINDING} MISSING INPUT AND INVALID "
        f"INPUT ARE DIFFERENT STATES: an absent, undeclared or unsourced eta or a means "
        f"we do not possess the required physical input and keeps the existing "
        f"{rule.missing_verdict} lifecycle, while a present nonfinite, zero or negative "
        f"eta or a means we possess a value outside the admissible physical domain and "
        f"is {rule.present_invalid_verdict}. The two are never conflated and a "
        f"placeholder may not substitute for a required measured input in any path that "
        f"can produce an official valid Branch-A package. DERIVED, NOT INDEPENDENT: "
        f"{GAMMA_RELATION} and {TAU_RELATION}, so for admissible primitives gamma is "
        f"finite and strictly positive, and together with the already-explicit "
        f"lambda_r > 0 requirement of design section 14 every tau_r is finite and "
        f"strictly positive. These are consequences of one decision and one existing "
        f"rule, not four unrelated positivity choices. PHYSICAL DOMAIN AND NUMERICAL "
        f"REPRESENTABILITY REMAIN DISTINCT: physically admissible primitives whose "
        f"computed gamma or tau underflows, overflows or is otherwise unrepresentable "
        f"keep the existing {rule.representability_verdict} semantics and are NEVER "
        f"relabelled as an invalid eta or a; {PRECEDENCE} CONSEQUENCE: "
        f"{BRANCH_A_CONSEQUENCE} STIFFNESS IS UNCHANGED: {STIFFNESS_REQUIREMENT} remains "
        f"exactly as design section 14 states it. {STIFFNESS_CONSEQUENCE} SCOPE: "
        f"{rule.scope} WHAT THIS DOES NOT DECLARE: the actual viscosity values, the "
        f"viscosity model eta(T), the actual bead radius, measurement uncertainty for "
        f"either, and their hardware provenance. Those remain {F4_OPEN_ITEM}, which is "
        f"{F4_STATUS}. Decided before any official campaign job, trajectory or outcome "
        f"existed.")


#: The exact sentences the normative human design document must carry. A design
#: edited to say anything else stops matching and refuses.
def design_required_sentences(
        rule: PassiveDragDomainRule = PASSIVE_DRAG_DOMAIN_RULE) -> tuple[str, ...]:
    return (
        rule.rule,
        INDIVIDUALLY_BINDING,
        BRANCH_A_CONSEQUENCE,
        PLACEHOLDER_SUBSTITUTION,
        PRECEDENCE,
        rule.scope,
        STIFFNESS_CONSEQUENCE,
    )


#: Every key the contract's domain block may carry, with why it is there. A key
#: the specification does not classify REFUSES: authority cannot be added to this
#: block and go unchecked, which is the same totality guarantee the plan has.
CONTRACT_BLOCK_SPEC = {
    "disposition": "the prospective disposition identifier and its timing",
    "scope": "the benchmark-domain scope statement",
    "rule": "the approved rule, in the author's words",
    "finite_real_meaning": "what finite real means for this repository",
    "primitive_inputs": "the machine-readable per-primitive domains",
    "individually_binding": "why the rule binds eta and a and not only gamma",
    "insufficient_rules": "the gamma-only and tau-only rules, named as insufficient",
    "derived_quantities": "gamma and tau, their relations and their derived status",
    "stiffness_precondition": "the quoted, unchanged design section 14 stiffness rule",
    "dispositions": "the three distinct verdicts and what each one means",
    "precedence": "physical domain before numerical representability",
    "branch_a_consequence": "what an inadmissible primitive input can never produce",
    "placeholder_substitution": "a placeholder may not stand in for a measured input",
    "values_not_set": "the F4 boundary this amendment does not cross",
    "timing": "prospective adoption, with no outcome inspected",
    "plan_rendering": "the exact execution-facing restatement the plan must carry",
}


def require_domain_specification_totality(block: Mapping[str, Any]) -> None:
    """Refuse a domain block carrying a key the specification does not classify."""
    unknown = sorted(set(block) - set(CONTRACT_BLOCK_SPEC))
    if unknown:
        raise BranchADomainUnclassified(
            f"the Branch-A input-domain authority carries unclassified key(s) {unknown}. "
            "Authority may not be added to this block without a deliberate decision "
            "about what it means, or it becomes normative text nothing checks.")
    absent = sorted(set(CONTRACT_BLOCK_SPEC) - set(block))
    if absent:
        raise BranchADomainUnclassified(
            f"the Branch-A input-domain authority omits required key(s) {absent}")


#: Tokens that would mean an F4 value had been smuggled into F2 authority.
_F4_VALUE_KEYS = ("value", "values", "eta_value", "bead_radius_value", "viscosity_value",
                  "eta_model", "viscosity_model", "radius_m", "pa_s", "measured_value",
                  "nominal", "default")


def _numeric_leaves(node: Any, prefix: str) -> list[tuple[str, Any]]:
    if isinstance(node, dict):
        return [item for key, child in node.items()
                for item in _numeric_leaves(child, f"{prefix}.{key}")]
    if isinstance(node, list):
        return [item for index, child in enumerate(node)
                for item in _numeric_leaves(child, f"{prefix}[{index}]")]
    if isinstance(node, bool) or not isinstance(node, (int, float)):
        return []
    return [(prefix, node)]


#: The only numbers this authority may contain are the declared bound itself.
_ALLOWED_NUMERIC_PATHS = frozenset({
    f"{CONTRACT_SECTION}.primitive_inputs.viscosity.domain.lower_bound",
    f"{CONTRACT_SECTION}.primitive_inputs.bead_radius.domain.lower_bound",
})


def require_f4_remains_open(block: Mapping[str, Any]) -> None:
    """Refuse an F2 authority block that has started to supply F4's values.

    This amendment declares a DOMAIN. The moment it also carries a viscosity, a
    bead radius, a temperature model or an uncertainty for either, it has closed
    F4 without F4's authorisation. The check is mechanical: the only number this
    block may contain is the declared lower bound.
    """
    for path, value in _numeric_leaves(block, CONTRACT_SECTION):
        if path in _ALLOWED_NUMERIC_PATHS:
            continue
        raise BranchADomainScopeViolation(
            f"{path} = {value!r}: this amendment declares the admissible DOMAIN of eta "
            f"and a and nothing else. Actual field-construction values belong to "
            f"{F4_OPEN_ITEM}, which remains {F4_STATUS}.")
    declared = block.get("values_not_set", {})
    if declared.get("remaining_open_item") != F4_OPEN_ITEM or declared.get("status") != F4_STATUS:
        raise BranchADomainScopeViolation(
            f"the authority must record {F4_OPEN_ITEM} as {F4_STATUS}; it records "
            f"{declared.get('remaining_open_item')!r} as {declared.get('status')!r}")
    if list(declared.get("not_declared_here", ())) != list(F4_NOT_DECLARED_HERE):
        raise BranchADomainScopeViolation(
            "the authority must enumerate exactly the F4 inputs it does NOT declare")


#: Two clauses the scope statement must carry. Deliberately STRUCTURAL rather
#: than a scan for universality wording: a sentence that DENIES universality
#: necessarily contains the same words as one that asserts it, so a token scan
#: cannot tell them apart and would reject the correct text. Requiring the
#: benchmark name and the explicit disclaimer is enough -- a scope rewritten to
#: "applies to all physical systems" carries neither.
SCOPE_BENCHMARK_CLAUSE = "E1a passive equilibrium optical-trap benchmark"
SCOPE_DISCLAIMER_CLAUSE = "NOT a universal physical assertion"


def require_benchmark_scope(block: Mapping[str, Any]) -> None:
    """Refuse a scope statement that has stopped being a benchmark-domain one."""
    scope = block.get("scope", "")
    if not isinstance(scope, str):
        raise BranchADomainScopeViolation("the scope statement must be text")
    if SCOPE_BENCHMARK_CLAUSE not in scope:
        raise BranchADomainScopeViolation(
            f"the scope must name the {SCOPE_BENCHMARK_CLAUSE}; an unscoped rule reads "
            "as a universal physical assertion this design does not make")
    if SCOPE_DISCLAIMER_CLAUSE not in scope:
        raise BranchADomainScopeViolation(
            f"the scope must state explicitly that this is {SCOPE_DISCLAIMER_CLAUSE}. "
            "Systems with negative effective transport coefficients are OUTSIDE this "
            "benchmark; E1a does not deny that they exist.")


# ----------------------------------------------------------- the entry point
def require_passive_drag_domain_authority(
        contract: Mapping[str, Any],
        plan: Mapping[str, Any],
        root: str = ".",
        rule: PassiveDragDomainRule = PASSIVE_DRAG_DOMAIN_RULE) -> None:
    """Bind every representation of the approved domain. Fails closed.

    Order matters. The PIN is validated first, because every comparison below is
    against what it generates; then the contract, which is the machine authority;
    then the normative human design document; then the plan's restatement and its
    recorded prospective disposition.
    """
    require_approved_rule(rule)

    if CONTRACT_SECTION not in contract:
        raise BranchADomainAuthorityMismatch(
            f"the design contract carries no {CONTRACT_SECTION!r} section. The Branch-A "
            "measured input domain would then be undeclared authority again, which is "
            "the gap this amendment closes.")
    block = contract[CONTRACT_SECTION]
    if not isinstance(block, dict):
        raise BranchADomainAuthorityMismatch(
            f"{CONTRACT_SECTION} must be a structured object, not {type(block).__name__}")
    require_domain_specification_totality(block)
    require_benchmark_scope(block)
    require_f4_remains_open(block)

    expected = render_contract_block(rule)
    for key in CONTRACT_BLOCK_SPEC:
        if block[key] != expected[key]:
            raise BranchADomainAuthorityMismatch(
                f"{CONTRACT_SECTION}.{key} is not the approved prospective rule: "
                f"contract {block[key]!r}, approved {expected[key]!r}")

    path = os.path.join(root, DESIGN_DOCUMENT)
    if not os.path.exists(path):
        raise BranchADomainAuthorityMismatch(
            "the normative prospective design document is absent")
    with open(path, encoding="utf-8") as handle:
        design = handle.read()
    for sentence in design_required_sentences(rule):
        if sentence not in design:
            raise BranchADomainAuthorityMismatch(
                "the normative design document no longer states an approved clause of "
                f"the Branch-A input domain: {sentence[:90]!r}...")
    branch_a = plan.get("generating_model", {}).get("branch_a", {})
    actual = branch_a.get("measured_input_domain")
    if actual != expected["plan_rendering"]:
        raise BranchADomainAuthorityMismatch(
            f"{PLAN_PATH} does not restate the approved domain: plan {actual!r}, "
            f"frozen authority {expected['plan_rendering']!r}")

    gaps = {gap.get("id"): gap for gap in plan.get("authority_gaps", ())}
    if DISPOSITION_ID not in gaps:
        raise BranchADomainAuthorityMismatch(
            f"the validation plan records no {DISPOSITION_ID} disposition for the "
            "Branch-A measured input domain; a prospective decision that is not "
            "recorded as one cannot be audited as one")
    gap = gaps[DISPOSITION_ID]
    for key, want in (("affects", DISPOSITION_AFFECTS),
                      ("status", DISPOSITION_STATUS),
                      ("gap", render_disposition_gap()),
                      ("resolution", render_disposition_resolution(rule))):
        if gap.get(key) != want:
            raise BranchADomainAuthorityMismatch(
                f"authority_gaps.{DISPOSITION_ID}.{key} is not the approved text: "
                f"plan {gap.get(key)!r}, frozen authority {want!r}")
