"""Passive-drag primitive input domain regression (disposition G6).

STATIC AND PURE. No RNG, no trajectory, no campaign job, no model transition.
Every probe either calls a pure predicate, mutates an in-memory authority object,
or edits a temporary COPY of the authority documents in a sandbox directory.

WHAT THIS SUITE IS FOR
    The approved rule is: eta and a are each finite and strictly greater than
    zero, REQUIRED, and bound INDIVIDUALLY. Three things could silently undo it:

      1. weakening the pinned rule object (`>= 0`, unbounded, nonfinite allowed,
         one primitive dropped);
      2. weakening the authority DOCUMENTS so that they coherently agree with
         each other on a different rule;
      3. restating it as a rule on the DERIVED gamma or tau, which looks
         equivalent and is not: eta < 0 together with a < 0 gives gamma > 0.

    Every class below is a coherent, plausible wrong version of the rule. Each
    must REFUSE with a stable code. The double-negative case is demonstrated by
    executing the gamma-only predicate, not by asserting that it is wrong.
"""

from __future__ import annotations

import copy
import dataclasses
import json
import math
import os
import shutil

from e1a_v4.numerics import Refusal
from e1a_v4.contract import load_contract
from e1a_v4.validation import PLAN_JSON
from e1a_v4.validation import drag_domain as dd
from e1a_v4.validation.contract_plan import require_contract_plan_conformance
from e1a_v4.validation.drag_domain import (
    ADMISSIBLE, DISPOSITION_RECORD_KEYS, PASSIVE_DRAG_DOMAIN_RULE,
    classify_drag_inputs, gamma_of, gamma_only_admits, is_admissible_primitive,
    render_contract_block, require_approved_rule, require_benchmark_scope,
    require_domain_specification_totality, require_f4_remains_open,
    require_passive_drag_domain_authority,
)
from e1a_v4.validation.plan import bind_execution
from test_e1a_v4_generating_model import ROOT, rj, wj, regenerate, sandbox

PASSED = 0
FAILED = 0

CONTRACT_PATH = "docs/e1a/e1a_v4_design_contract.json"
DESIGN_PATH = "docs/e1a/E1A_V4_PROSPECTIVE_DESIGN.md"
SECTION = dd.CONTRACT_SECTION

AUTHORITY = "BRANCH_A_DOMAIN_AUTHORITY_MISMATCH"
UNCLASSIFIED = "BRANCH_A_DOMAIN_UNCLASSIFIED"
SCOPE = "BRANCH_A_DOMAIN_SCOPE_VIOLATION"


def check(label: str, condition: bool, detail: str = "") -> None:
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  [PASS] {label}" + (f"  -- {detail}" if detail else ""))
    else:
        FAILED += 1
        print(f"  [FAIL] {label}" + (f"  -- {detail}" if detail else ""))


def code(fn, *args, **kwargs) -> str:
    try:
        fn(*args, **kwargs)
    except Refusal as exc:
        return getattr(type(exc), "code", "UNCODED")
    return "ACCEPTED"


def refuses(label: str, expected: str, fn, *args, **kwargs) -> None:
    got = code(fn, *args, **kwargs)
    check(f"{label} -> {expected}", got == expected, f"got {got}")


# --------------------------------------------------------------- the baseline
def test_baseline() -> None:
    contract = load_contract(ROOT).data
    plan = rj(ROOT, PLAN_JSON)
    check("the committed authority states the approved domain",
          code(require_passive_drag_domain_authority, contract, plan, ROOT) == "ACCEPTED")
    check("the pinned rule is the approved one",
          code(require_approved_rule) == "ACCEPTED")
    check("the contract block is exactly what the pinned rule generates",
          contract[SECTION] == render_contract_block())
    check("the plan restates it verbatim",
          plan["generating_model"]["branch_a"]["measured_input_domain"]
          == contract[SECTION]["plan_rendering"])
    gaps = {g["id"]: g for g in plan["authority_gaps"]}
    check("G6 is recorded as a prospective disposition",
          "G6" in gaps and gaps["G6"]["status"] == "CLOSED PROSPECTIVELY")
    check("G6 records that it was decided before any outcome existed",
          "before any official campaign job, trajectory or outcome existed"
          in gaps["G6"]["resolution"])
    check("the full preflight accepts the committed authority",
          code(bind_execution, ROOT) == "ACCEPTED")


# ------------------------------------------------------- the pure domain test
def test_pure_domain() -> None:
    eta = PASSIVE_DRAG_DOMAIN_RULE.primitive("viscosity")
    admissible = [8.9e-4, 1.0, 1e-300, 1e300, 2 ** -1074]
    for value in admissible:
        check(f"admissible primitive {value!r}", is_admissible_primitive(value, eta))
    for value in (0.0, -0.0, -1e-9, -8.9e-4, math.inf, -math.inf, math.nan):
        check(f"inadmissible primitive {value!r}", not is_admissible_primitive(value, eta))
    # bool subclasses int; a flag is not a measurement.
    for value in (True, False, "0.00089", None, [8.9e-4], {"v": 8.9e-4}, 1 + 0j):
        check(f"non-numeric {value!r} is not a measured value",
              not is_admissible_primitive(value, eta))
    check("an integer measurement is accepted as a real number",
          is_admissible_primitive(1, eta) and not is_admissible_primitive(0, eta))


# ------------------------------- missing vs present-invalid, the two verdicts
def test_missing_is_not_invalid() -> None:
    good = {"viscosity": 8.9e-4, "bead_radius": 1e-6}
    check("admissible inputs classify ADMISSIBLE",
          classify_drag_inputs(good) == ADMISSIBLE)
    for absent in ("viscosity", "bead_radius"):
        missing = {k: v for k, v in good.items() if k != absent}
        check(f"absent {absent} -> UNDECLARED_FIELD_INPUTS",
              classify_drag_inputs(missing) == "UNDECLARED_FIELD_INPUTS")
        nulled = dict(good, **{absent: None})
        check(f"null {absent} -> UNDECLARED_FIELD_INPUTS",
              classify_drag_inputs(nulled) == "UNDECLARED_FIELD_INPUTS")
    check("both absent -> UNDECLARED_FIELD_INPUTS",
          classify_drag_inputs({}) == "UNDECLARED_FIELD_INPUTS")
    for bad in (0.0, -1.0, math.inf, -math.inf, math.nan):
        for key in ("viscosity", "bead_radius"):
            check(f"present {key}={bad!r} -> REFUSED_BRANCH_A_INVALID",
                  classify_drag_inputs(dict(good, **{key: bad}))
                  == "REFUSED_BRANCH_A_INVALID")
    check("missing resolves BEFORE present-invalid, never the other way",
          classify_drag_inputs({"viscosity": -1.0}) == "UNDECLARED_FIELD_INPUTS",
          "an input we do not possess has no value to be outside a domain")
    check("the two verdicts are different strings",
          PASSIVE_DRAG_DOMAIN_RULE.missing_verdict
          != PASSIVE_DRAG_DOMAIN_RULE.present_invalid_verdict)
    check("neither is the numerical-representability verdict",
          PASSIVE_DRAG_DOMAIN_RULE.representability_verdict
          not in (PASSIVE_DRAG_DOMAIN_RULE.missing_verdict,
                  PASSIVE_DRAG_DOMAIN_RULE.present_invalid_verdict))


# -------------------------------------------- THE DOUBLE-NEGATIVE ESCAPE
def test_double_negative_escape() -> None:
    """A gamma-only rule admits eta < 0 AND a < 0. Reproduced, not asserted."""
    eta, a = -8.9e-4, -1e-6
    gamma = gamma_of(eta, a)
    check("eta < 0 and a < 0 give a POSITIVE gamma",
          gamma > 0.0 and math.isfinite(gamma), f"gamma = {gamma!r}")
    check("a gamma-only rule ADMITS the double-negative pair",
          gamma_only_admits(eta, a), "this is the loophole, executed")
    check("a gamma-only rule admits the legitimate pair too",
          gamma_only_admits(8.9e-4, 1e-6),
          "so it cannot be told apart from the approved rule by its accepts")
    check("the APPROVED rule refuses the double-negative pair",
          classify_drag_inputs({"viscosity": eta, "bead_radius": a})
          == "REFUSED_BRANCH_A_INVALID")
    check("and accepts the legitimate pair",
          classify_drag_inputs({"viscosity": 8.9e-4, "bead_radius": 1e-6}) == ADMISSIBLE)
    tau = gamma / 1e-4
    check("the double-negative pair also gives a POSITIVE relaxation time",
          tau > 0.0, f"tau = {tau!r}; a tau-only rule admits it as well")
    check("authority NAMES the gamma-only rule as insufficient",
          "gamma > 0 alone, with the primitive eta and a domains unrestricted"
          in PASSIVE_DRAG_DOMAIN_RULE.insufficient_rules)
    check("authority NAMES the tau-only rule as insufficient",
          "tau_r > 0 alone, with the primitive eta and a domains unrestricted"
          in PASSIVE_DRAG_DOMAIN_RULE.insufficient_rules)


# ------------------------------------------- mutations of the PINNED rule
def mutated_primitive(key: str, **changes) -> dd.PassiveDragDomainRule:
    rule = PASSIVE_DRAG_DOMAIN_RULE
    primitives = tuple(dataclasses.replace(p, **changes) if p.key == key else p
                       for p in rule.primitives)
    return dataclasses.replace(rule, primitives=primitives)


def test_pinned_rule_mutations() -> None:
    contract = load_contract(ROOT).data
    plan = rj(ROOT, PLAN_JSON)

    def probe(label, rule, expected=AUTHORITY):
        refuses(label, expected, require_passive_drag_domain_authority,
                contract, plan, ROOT, rule)

    for key, symbol in (("viscosity", "eta"), ("bead_radius", "a")):
        probe(f"{symbol} positive -> {symbol} >= 0",
              mutated_primitive(key, lower_bound_inclusive=True))
        probe(f"{symbol} positive -> {symbol} unrestricted",
              mutated_primitive(key, lower_bound=float("-inf")))
        probe(f"{symbol} finite required -> nonfinite allowed",
              mutated_primitive(key, finite=False))
        probe(f"{symbol} required -> optional",
              mutated_primitive(key, required=False))
        probe(f"{symbol} gains an upper bound this amendment does not set",
              mutated_primitive(key, upper_bound=1.0))
        dropped = dataclasses.replace(
            PASSIVE_DRAG_DOMAIN_RULE,
            primitives=tuple(p for p in PASSIVE_DRAG_DOMAIN_RULE.primitives
                             if p.key != key))
        probe(f"the {symbol} rule is removed entirely", dropped)

    gamma_only = dataclasses.replace(PASSIVE_DRAG_DOMAIN_RULE, primitives=())
    probe("gamma-only validation: both primitive rules removed", gamma_only)

    tau_only = dataclasses.replace(
        PASSIVE_DRAG_DOMAIN_RULE, primitives=(),
        insufficient_rules=("none -- a positive tau_r is sufficient",))
    probe("tau-only validation: only a positive relaxation time is required", tau_only)

    for key in ("gamma", "tau"):
        independent = dataclasses.replace(
            PASSIVE_DRAG_DOMAIN_RULE,
            derived=tuple(dataclasses.replace(d, independent_rule=True)
                          if d.key == key else d
                          for d in PASSIVE_DRAG_DOMAIN_RULE.derived))
        probe(f"{key} positivity made an INDEPENDENT rule rather than derived",
              independent)

    probe("missing input relabelled as a physical-domain failure",
          dataclasses.replace(PASSIVE_DRAG_DOMAIN_RULE,
                              missing_verdict="REFUSED_BRANCH_A_INVALID"))
    probe("invalid input relabelled as a missing input",
          dataclasses.replace(PASSIVE_DRAG_DOMAIN_RULE,
                              present_invalid_verdict="UNDECLARED_FIELD_INPUTS"))
    probe("invalid input declared VALID",
          dataclasses.replace(PASSIVE_DRAG_DOMAIN_RULE,
                              present_invalid_verdict="VALID"))
    probe("invalid input given an invented refusal category",
          dataclasses.replace(PASSIVE_DRAG_DOMAIN_RULE,
                              present_invalid_verdict="REFUSED_DRAG_DOMAIN"))
    probe("a representability failure relabelled as an eta/a physical invalidity",
          dataclasses.replace(PASSIVE_DRAG_DOMAIN_RULE,
                              representability_verdict="REFUSED_BRANCH_A_INVALID"))
    probe("the insufficient-rule record is dropped",
          dataclasses.replace(PASSIVE_DRAG_DOMAIN_RULE, insufficient_rules=()))
    probe("the benchmark scope is replaced by a universal claim",
          dataclasses.replace(PASSIVE_DRAG_DOMAIN_RULE,
                              scope="this applies to all physical systems"))
    probe("the approved rule text is reworded",
          dataclasses.replace(PASSIVE_DRAG_DOMAIN_RULE,
                              rule="eta and a must be non-negative"))
    probe("the frozen Stokes relation is altered inside the amendment",
          dataclasses.replace(
              PASSIVE_DRAG_DOMAIN_RULE,
              derived=(dataclasses.replace(PASSIVE_DRAG_DOMAIN_RULE.derived[0],
                                           relation="gamma = 4 pi eta a"),
                       PASSIVE_DRAG_DOMAIN_RULE.derived[1])))


# ------------------------------------- mutations of the CONTRACT document
def with_block(mutate) -> tuple[dict, dict]:
    contract = copy.deepcopy(load_contract(ROOT).data)
    mutate(contract[SECTION])
    return contract, rj(ROOT, PLAN_JSON)


def contract_probe(label, mutate, expected=AUTHORITY) -> None:
    contract, plan = with_block(mutate)
    refuses(label, expected, require_passive_drag_domain_authority,
            contract, plan, ROOT)


def test_contract_mutations() -> None:
    for key, symbol in (("viscosity", "eta"), ("bead_radius", "a")):
        contract_probe(
            f"contract: {symbol} lower bound becomes inclusive",
            lambda b, k=key: b["primitive_inputs"][k]["domain"].__setitem__(
                "lower_bound_inclusive", True))
        contract_probe(
            f"contract: {symbol} lower bound removed",
            lambda b, k=key: b["primitive_inputs"][k]["domain"].__setitem__(
                "lower_bound", None))
        contract_probe(
            f"contract: {symbol} no longer required to be finite",
            lambda b, k=key: b["primitive_inputs"][k]["domain"].__setitem__(
                "finite", False))
        contract_probe(
            f"contract: {symbol} becomes optional",
            lambda b, k=key: b["primitive_inputs"][k].__setitem__("required", False))
        contract_probe(
            f"contract: the {symbol} primitive is deleted",
            lambda b, k=key: b["primitive_inputs"].pop(k))

    contract_probe("contract: both primitives deleted, gamma-only remains",
                   lambda b: b.__setitem__("primitive_inputs", {}))
    contract_probe("contract: gamma declared an independent rule",
                   lambda b: b["derived_quantities"]["gamma"].__setitem__(
                       "independent_rule", True))
    contract_probe("contract: tau declared an independent rule",
                   lambda b: b["derived_quantities"]["tau"].__setitem__(
                       "independent_rule", True))
    contract_probe("contract: gamma promoted to a measured primitive",
                   lambda b: b["derived_quantities"]["gamma"].__setitem__(
                       "status", "BRANCH_A_MEASURED_PRIMITIVE"))
    contract_probe("contract: missing input merged into the invalid verdict",
                   lambda b: b["dispositions"]["missing_or_undeclared_input"].__setitem__(
                       "verdict", "REFUSED_BRANCH_A_INVALID"))
    contract_probe("contract: invalid input merged into the missing verdict",
                   lambda b: b["dispositions"]["present_but_inadmissible_input"].__setitem__(
                       "verdict", "UNDECLARED_FIELD_INPUTS"))
    contract_probe("contract: invalid input declared VALID",
                   lambda b: b["dispositions"]["present_but_inadmissible_input"].__setitem__(
                       "verdict", "VALID"))
    contract_probe("contract: representability failure relabelled an eta/a invalidity",
                   lambda b: b["dispositions"]["numerical_representability_failure"]
                   .__setitem__("verdict", "REFUSED_BRANCH_A_INVALID"))
    contract_probe("contract: physical-domain precedence removed",
                   lambda b: b.__setitem__(
                       "precedence", "representability is checked first"))
    contract_probe("contract: the Branch-A consequence is weakened",
                   lambda b: b.__setitem__(
                       "branch_a_consequence",
                       "an inadmissible input is reported but does not block publication"))
    contract_probe("contract: placeholders allowed to stand in for a measured input",
                   lambda b: b.__setitem__(
                       "placeholder_substitution",
                       "a neutral placeholder MAY be used when the measurement is absent"))
    contract_probe("contract: the stiffness precondition is reopened",
                   lambda b: b["stiffness_precondition"].__setitem__(
                       "requirement", "a negative stiffness is a valid unstable trap"))
    contract_probe("contract: the stiffness consequence admits lambda = 0",
                   lambda b: b["stiffness_precondition"].__setitem__(
                       "consequence", "lambda_r = 0 is admissible"))
    contract_probe("contract: a key the specification does not classify is added",
                   lambda b: b.__setitem__("eta_override", "anything"), UNCLASSIFIED)
    contract_probe("contract: a required key is removed",
                   lambda b: b.pop("individually_binding"), UNCLASSIFIED)
    contract_probe("contract: scope broadened to all physical systems",
                   lambda b: b.__setitem__(
                       "scope", "every physical system with a viscous medium"), SCOPE)
    contract_probe("contract: the non-universality disclaimer is dropped",
                   lambda b: b.__setitem__(
                       "scope", "the declared E1a passive equilibrium optical-trap "
                                "benchmark and comparable systems."), SCOPE)

    # A NESTED addition escapes the top-level totality check; the exact comparison
    # against the generated block is what catches it, at every depth.
    contract_probe("contract: an unclassified key is added inside a primitive",
                   lambda b: b["primitive_inputs"]["viscosity"].__setitem__(
                       "note", "see the lab notebook"))
    contract_probe("contract: an unclassified key is added inside a domain",
                   lambda b: b["primitive_inputs"]["bead_radius"]["domain"].__setitem__(
                       "tolerance", "loose"))
    contract_probe("contract: an unclassified key is added inside a disposition",
                   lambda b: b["dispositions"]["present_but_inadmissible_input"]
                   .__setitem__("override", "permitted in development"))

    contract = copy.deepcopy(load_contract(ROOT).data)
    contract.pop(SECTION)
    refuses("contract: the whole domain section is removed", AUTHORITY,
            require_passive_drag_domain_authority, contract, rj(ROOT, PLAN_JSON), ROOT)


# ------------------------------------------------ F4 must remain untouched
def test_f4_remains_open() -> None:
    # A NESTED value escapes the top-level totality check, so the numeric-leaf
    # scan is what catches it. That is the stronger of the two: it fires on any
    # number anywhere in the amendment except the declared bound itself.
    contract_probe("F4: an actual viscosity value is inserted",
                   lambda b: b["primitive_inputs"]["viscosity"].__setitem__(
                       "measured_value", 0.00089), SCOPE)
    contract_probe("F4: an actual bead radius is inserted as a domain bound",
                   lambda b: b["primitive_inputs"]["bead_radius"]["domain"].__setitem__(
                       "upper_bound", 1e-05), SCOPE)
    contract_probe("F4: a viscosity model is declared",
                   lambda b: b.__setitem__("eta_model", "water, Vogel-Fulcher"),
                   UNCLASSIFIED)
    contract_probe("F4: the open-item record is erased",
                   lambda b: b["values_not_set"].__setitem__("status", "CLOSED"), SCOPE)
    contract_probe("F4: the open item is renamed to something else",
                   lambda b: b["values_not_set"].__setitem__(
                       "remaining_open_item", "none"), SCOPE)
    contract_probe("F4: the list of undeclared inputs is trimmed",
                   lambda b: b["values_not_set"]["not_declared_here"].pop(0), SCOPE)
    block = render_contract_block()
    check("the approved authority contains no number but the declared bound",
          code(require_f4_remains_open, block) == "ACCEPTED")
    numbers = dd._numeric_leaves(block, SECTION)
    check("exactly two numbers appear in the whole amendment",
          len(numbers) == 2 and all(v == 0 for _, v in numbers),
          f"{[p.split('.')[-3] + '.' + p.split('.')[-1] for p, _ in numbers]}")
    check("no actual eta or bead-radius value is anywhere in the authority",
          not any(token in json.dumps(block).lower()
                  for token in ("0.00089", "1e-06", "1e-6", "8.9e-4")))


# ------------------------------------- the design document and the plan
def test_document_mutations() -> None:
    contract = load_contract(ROOT).data
    plan = rj(ROOT, PLAN_JSON)
    for index, sentence in enumerate(dd.design_required_sentences()):
        tmp = sandbox()
        try:
            path = os.path.join(tmp, DESIGN_PATH)
            text = open(path, encoding="utf-8").read()
            assert sentence in text
            open(path, "w", encoding="utf-8").write(text.replace(sentence, "", 1))
            refuses(f"design: approved clause {index} deleted", AUTHORITY,
                    require_passive_drag_domain_authority, contract, plan, tmp)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    mutations = {
        "the plan restatement is weakened to >= 0":
            lambda p: p["generating_model"]["branch_a"].__setitem__(
                "measured_input_domain",
                p["generating_model"]["branch_a"]["measured_input_domain"]
                .replace("strictly greater than zero", "greater than or equal to zero")),
        "the plan restatement is deleted":
            lambda p: p["generating_model"]["branch_a"].pop("measured_input_domain"),
        "the G6 disposition is deleted":
            lambda p: p.__setitem__(
                "authority_gaps", [g for g in p["authority_gaps"] if g["id"] != "G6"]),
        "the G6 resolution is reworded":
            lambda p: [g for g in p["authority_gaps"] if g["id"] == "G6"][0]
            .__setitem__("resolution", "eta and a must be non-negative."),
        "the G6 status is downgraded":
            lambda p: [g for g in p["authority_gaps"] if g["id"] == "G6"][0]
            .__setitem__("status", "OPEN"),
        "the G6 gap statement is erased":
            lambda p: [g for g in p["authority_gaps"] if g["id"] == "G6"][0]
            .__setitem__("gap", "none"),
    }
    for label, mutate in mutations.items():
        mutated = copy.deepcopy(plan)
        mutate(mutated)
        refuses(f"plan: {label}", AUTHORITY,
                require_passive_drag_domain_authority, contract, mutated, ROOT)


def test_coherent_document_drift_still_refuses() -> None:
    """Markdown and JSON agreeing on a weaker rule is still refused."""
    tmp = sandbox()
    try:
        plan = rj(tmp, PLAN_JSON)
        weakened = (plan["generating_model"]["branch_a"]["measured_input_domain"]
                    .replace("strictly greater than zero",
                             "greater than or equal to zero"))
        plan["generating_model"]["branch_a"]["measured_input_domain"] = weakened
        for gap in plan["authority_gaps"]:
            if gap["id"] == "G6":
                gap["resolution"] = gap["resolution"].replace(
                    "strictly greater than zero", "greater than or equal to zero")
        wj(tmp, PLAN_JSON, plan)
        regenerate(tmp)
        check("the weakened plan is internally COHERENT after regeneration",
              code(bind_execution, tmp) != "ACCEPTED",
              "it must still refuse upstream, not pass")
        refuses("Markdown and JSON agree on >= 0; the pinned rule still refuses",
                AUTHORITY, require_passive_drag_domain_authority,
                load_contract(tmp).data, plan, tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_fully_propagated_contract_weakening() -> None:
    """Contract AND plan AND design all edited to >= 0, then regenerated."""
    tmp = sandbox()
    try:
        old = "strictly greater than zero"
        new = "greater than or equal to zero"
        contract = rj(tmp, CONTRACT_PATH)
        block = contract[SECTION]
        block["rule"] = block["rule"].replace(old, new)
        block["plan_rendering"] = block["plan_rendering"].replace(old, new)
        for name in ("viscosity", "bead_radius"):
            block["primitive_inputs"][name]["domain"]["lower_bound_inclusive"] = True
        wj(tmp, CONTRACT_PATH, contract)

        design_path = os.path.join(tmp, DESIGN_PATH)
        text = open(design_path, encoding="utf-8").read()
        open(design_path, "w", encoding="utf-8").write(text.replace(old, new))

        plan = rj(tmp, PLAN_JSON)
        plan["generating_model"]["branch_a"]["measured_input_domain"] = \
            block["plan_rendering"]
        for gap in plan["authority_gaps"]:
            if gap["id"] == "G6":
                gap["resolution"] = gap["resolution"].replace(old, new)
        wj(tmp, PLAN_JSON, plan)
        regenerate(tmp)

        check("the weakened package is coherent contract-to-plan",
              code(require_contract_plan_conformance, contract, plan, tmp) == "ACCEPTED",
              "every representation agrees; only the pinned rule disagrees")
        refuses("a fully propagated eta/a >= 0 weakening still refuses", AUTHORITY,
                require_passive_drag_domain_authority, contract, plan, tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------- stiffness is not reopened here
def test_stiffness_unchanged() -> None:
    from e1a_v4.branch_a import BranchAField
    def status(k):
        return BranchAField(
            field_id="probe", H_U=[[k[0], 0.0], [0.0, k[1]]], T=298.0,
            x_star=[0.0, 0.0], k_modes=tuple(k), rot_deg=0.0,
            viscosity=8.9e-4, bead_radius=1e-6,
            calibration_route="force_displacement_with_stokes_drag").status
    check("a negative stiffness is still BRANCH_A_INVALID",
          status((-1e-4, 1e-4)) == "BRANCH_A_INVALID")
    check("a zero stiffness is still BRANCH_A_INVALID",
          status((0.0, 1e-4)) == "BRANCH_A_INVALID")
    check("a positive-definite stiffness is still VALID",
          status((1e-4, 1e-4)) == "VALID")
    block = load_contract(ROOT).data[SECTION]
    check("authority quotes design section 14 as its stiffness source",
          "section 14" in block["stiffness_precondition"]["source"]
          and "UNCHANGED" in block["stiffness_precondition"]["source"])
    check("authority states lambda < 0 and lambda = 0 are NOT reopened",
          "NOT reopened" in block["stiffness_precondition"]["consequence"])


# ------------------------------------- the runtime is knowingly behind this
def test_runtime_lag_is_disclosed_not_hidden() -> None:
    """F2e is NOT implemented here. This records exactly how far behind it is."""
    from e1a_v4.branch_a import BranchAField
    def built(eta, a):
        return BranchAField(
            field_id="probe", H_U=[[1e-4, 0.0], [0.0, 1e-4]], T=298.0,
            x_star=[0.0, 0.0], k_modes=(1e-4, 1e-4), rot_deg=0.0,
            viscosity=eta, bead_radius=a,
            calibration_route="force_displacement_with_stokes_drag")
    lagging = []
    for label, eta, a in (("eta < 0", -8.9e-4, 1e-6), ("a < 0", 8.9e-4, -1e-6),
                          ("eta < 0 and a < 0", -8.9e-4, -1e-6),
                          ("eta = 0", 0.0, 1e-6), ("a = 0", 8.9e-4, 0.0),
                          ("eta = inf", math.inf, 1e-6),
                          ("eta = nan", math.nan, 1e-6)):
        field = built(eta, a)
        authority = classify_drag_inputs({"viscosity": eta, "bead_radius": a})
        if field.status == "VALID" and authority != ADMISSIBLE:
            lagging.append(label)
    check("production still accepts EVERY inadmissible drag input as VALID",
          len(lagging) == 7, f"{len(lagging)}/7 behind authority: {lagging}")
    check("the authority refuses all seven",
          all(classify_drag_inputs({"viscosity": e, "bead_radius": a})
              == "REFUSED_BRANCH_A_INVALID"
              for e, a in ((-8.9e-4, 1e-6), (8.9e-4, -1e-6), (-8.9e-4, -1e-6),
                           (0.0, 1e-6), (8.9e-4, 0.0), (math.inf, 1e-6),
                           (math.nan, 1e-6))))
    source = open(os.path.join(ROOT, "e1a_v4/branch_a.py"), encoding="utf-8").read()
    check("branch_a.py still applies NO validation to viscosity or bead_radius",
          "viscosity" not in source.split("def __post_init__")[1].split("@property")[0]
          and "bead_radius" not in source.split("def __post_init__")[1].split("@property")[0],
          "F2e is the authorised stage that closes this; it is NOT done here")
    check("no production or recovery module imports the new authority module",
          all("drag_domain" not in open(os.path.join(ROOT, p), encoding="utf-8").read()
              for p in ("e1a_v4/branch_a.py", "e1a_v4/validation/campaign_driver.py",
                        "e1a_v4/validation/calibrate.py",
                        "e1a_v4/validation/generate.py")))



# ------------------------------ the G6 record's own shape, independently bound
#: The F2d audit's blocker. The five legitimate G6 fields still matched their
#: approved text EXACTLY, so every value comparison in this module passed; the
#: sixth field was simply never looked at. Key-set equality is what refuses it,
#: and this layer is independent of the generic totality in `coherence` so that
#: neither check is load-bearing alone.
F2D_ATTACK = ("passive_drag_exception", "Zero viscosity is permitted for this field.")


def g6_probe(label, mutate, expected=AUTHORITY) -> None:
    contract = load_contract(ROOT).data
    plan = copy.deepcopy(rj(ROOT, PLAN_JSON))
    record = [g for g in plan["authority_gaps"] if g["id"] == "G6"][0]
    mutate(record, plan)
    refuses(label, expected, require_passive_drag_domain_authority,
            contract, plan, ROOT)


def test_g6_record_totality() -> None:
    plan = rj(ROOT, PLAN_JSON)
    record = [g for g in plan["authority_gaps"] if g["id"] == "G6"][0]
    check("the committed G6 record carries exactly the approved key set",
          tuple(sorted(record)) == DISPOSITION_RECORD_KEYS,
          str(DISPOSITION_RECORD_KEYS))
    check("every G6 clause is text",
          all(type(v) is str for v in record.values()))

    key, value = F2D_ATTACK
    g6_probe("THE F2d ATTACK: G6 + passive_drag_exception",
             lambda r, p: r.__setitem__(key, value))
    g6_probe("G6 + a benign-looking extra key",
             lambda r, p: r.__setitem__("note2", "additional information"))
    g6_probe("G6 + an unknown nested child object",
             lambda r, p: r.__setitem__("exceptions", {"eta": "zero permitted"}))
    g6_probe("G6 + an unknown list value",
             lambda r, p: r.__setitem__("exceptions", ["zero eta permitted"]))
    g6_probe("G6 missing a required key",
             lambda r, p: r.pop("affects"))
    g6_probe("G6 key renamed",
             lambda r, p: r.__setitem__("ruling", r.pop("resolution")))
    g6_probe("G6 clause given a non-text type",
             lambda r, p: r.__setitem__("status", ["CLOSED PROSPECTIVELY"]))
    g6_probe("G6 record replaced by a bare string",
             lambda r, p: p["authority_gaps"].__setitem__(
                 p["authority_gaps"].index(r), "G6: eta > 0"))
    g6_probe("authority_gaps replaced by a mapping",
             lambda r, p: p.__setitem__("authority_gaps", {"G6": r}))

    # Contrary clauses, each refused because the FIELD is unapproved -- no checker
    # reads the English, and a benign key above refuses identically.
    for label, text in (
            ("zero viscosity permitted", "Zero viscosity is permitted for this field."),
            ("negative bead radius permitted", "A negative bead radius is admissible."),
            ("gamma-only suffices", "gamma > 0 alone is sufficient."),
            ("tau-only suffices", "tau_r > 0 alone is sufficient."),
            ("missing eta treated as zero", "An absent eta is taken to be 0."),
            ("invalid eta treated as undeclared",
             "A negative eta is UNDECLARED_FIELD_INPUTS."),
            ("overflow makes eta invalid",
             "An overflowing gamma means eta was physically invalid.")):
        g6_probe(f"G6 + contrary clause -- {label}",
                 lambda r, p, t=text: r.__setitem__("clarification", t))

    check("the approved key set is pinned, not read from the candidate",
          key not in DISPOSITION_RECORD_KEYS
          and DISPOSITION_RECORD_KEYS == ("affects", "gap", "id", "resolution", "status"))


def test_hygiene() -> None:
    plan = rj(ROOT, PLAN_JSON)
    check("execution remains unauthorised", plan["execution_authorised"] is False)
    check("the expected final execution identity is still null",
          plan["frozen_identities"]["final_expected_execution_identity"] is None)
    check("no results directory exists",
          not os.path.exists(os.path.join(ROOT, "results/e1a_v4_validation")))
    rules = plan["adopted_rules_unchanged"]
    check("no E1a statistical decision rule moved",
          (rules["delta_cross"], rules["delta_abs"], rules["z_cross"], rules["z_abs"],
           rules["alpha_geom"], rules["alpha_1"], rules["alpha_2"],
           rules["theta_cap_deg"], rules["rank_tol"], rules["pipeline_target"])
          == (0.02, 0.05, 1.959963985, 1.959963985, 0.005, 0.004, 0.001, 5.0,
              1e-12, 0.9))
    check("every replicate count unchanged",
          [c["replicate_count"] for c in plan["cases"]]
          == [300, 400, 400, 2000, 400, 400, 400, 200])
    check("the frozen relaxation rule itself is unaltered",
          load_contract(ROOT).data["relaxation_time_rule"]
          == "tau_r = gamma(T)/k_r with gamma = 6 pi eta(T) a; a single tau_c for "
             "all fields is WRONG and is not used")


def main() -> int:
    print("\nbaseline")
    test_baseline()
    print("\npure domain predicate")
    test_pure_domain()
    print("\nmissing input is not invalid input")
    test_missing_is_not_invalid()
    print("\nthe double-negative escape")
    test_double_negative_escape()
    print("\nmutations of the pinned rule")
    test_pinned_rule_mutations()
    print("\nmutations of the contract")
    test_contract_mutations()
    print("\nF4 remains open")
    test_f4_remains_open()
    print("\nmutations of the design document and the plan")
    test_document_mutations()
    print("\ncoherent drift")
    test_coherent_document_drift_still_refuses()
    test_fully_propagated_contract_weakening()
    print("\nstiffness is not reopened")
    test_stiffness_unchanged()
    print("\nthe G6 record's own shape")
    test_g6_record_totality()
    print("\nthe runtime lag, disclosed")
    test_runtime_lag_is_disclosed_not_hidden()
    print("\nhygiene")
    test_hygiene()
    print(f"\nRESULT: {PASSED} passed, {FAILED} failed")
    return 0 if FAILED == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
