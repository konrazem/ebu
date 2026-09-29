"""Static contract/plan conformance regression. No RNG or model transitions.

Every probe changes in-memory plan values or temporary plan copies only.  A
fully propagated mutation must first pass Markdown/JSON coherence, then fail
the separate upstream contract check for its own reason.
"""

from __future__ import annotations

import copy
import math
import re
import shutil

from e1a_v4.numerics import Refusal
from e1a_v4.branch_a import build_field
from e1a_v4.contract import load_contract
from e1a_v4.validation import PLAN_JSON
from e1a_v4.validation.coherence import derived_n_samples, require_plan_authority_coherence
from e1a_v4.validation.contract_plan import (
    EXACT, DERIVED, CASE_SPECIFIC_ALLOWED_OVERRIDE, binding_inventory,
    binding_specification, require_contract_plan_conformance,
)
from e1a_v4.validation.plan import bind_execution
from test_e1a_v4_generating_model import ROOT, rj, wj, regenerate, sandbox

PASSED = 0
FAILED = 0


def check(label: str, yes: bool, detail: str = "") -> None:
    global PASSED, FAILED
    if yes:
        PASSED += 1
        print(f"  [PASS] {label}" + (f" -- {detail}" if detail else ""))
    else:
        FAILED += 1
        print(f"  [FAIL] {label}" + (f" -- {detail}" if detail else ""))


def code(fn, *args):
    try:
        fn(*args)
    except Refusal as exc:
        return getattr(type(exc), "code", "UNCODED")
    return "ACCEPTED"


def mutate(value):
    if isinstance(value, bool):
        return not value
    if isinstance(value, (int, float)):
        return value + 1
    if isinstance(value, str):
        return value + " MUTATED"
    if isinstance(value, list):
        out = copy.deepcopy(value)
        out[0] = mutate(out[0])
        return out
    if isinstance(value, dict):
        out = copy.deepcopy(value)
        key = next(iter(out))
        out[key] = mutate(out[key])
        return out
    raise AssertionError(f"no valid-looking mutation for {value!r}")


def access(obj, path):
    bits = re.findall(r"[^.\[\]]+|\[\d+\]", path)
    for bit in bits:
        obj = obj[int(bit[1:-1])] if bit.startswith("[") else obj[bit]
    return obj


def set_path(obj, path, value):
    bits = re.findall(r"[^.\[\]]+|\[\d+\]", path)
    parent = obj
    for bit in bits[:-1]:
        parent = parent[int(bit[1:-1])] if bit.startswith("[") else parent[bit]
    last = bits[-1]
    if last.startswith("["):
        parent[int(last[1:-1])] = value
    else:
        parent[last] = value


def propagated(contract, change, _expected_code):
    tmp = sandbox()
    try:
        plan = rj(tmp, PLAN_JSON)
        change(plan)
        branch_b = plan["generating_model"]["branch_b"]
        branch_b["n_samples"] = derived_n_samples(branch_b)
        wj(tmp, PLAN_JSON, plan)
        regenerate(tmp)
        coherent = code(require_plan_authority_coherence, tmp, plan)
        conformance = code(require_contract_plan_conformance, contract, plan)
        preflight = code(bind_execution, tmp)
        return coherent, conformance, preflight
    finally:
        shutil.rmtree(tmp)


def test_original_four(contract):
    targets = (
        ("remove theta3", lambda p: p["generating_model"]["per_field"].pop(),
         "CONTRACT_FIELD_SET_MISMATCH"),
        ("replace theta3 with duplicate theta0",
         lambda p: p["generating_model"]["per_field"].__setitem__(3,
             copy.deepcopy(p["generating_model"]["per_field"][0])),
         "CONTRACT_FIELD_DUPLICATE"),
        ("change tau rule", lambda p: p["generating_model"]["per_field"][0].__setitem__(
             "tau_rule", "constant tau for every mode"),
         "CONTRACT_RELAXATION_RULE_MISMATCH"),
        ("change theta1 beta", lambda p: p["generating_model"]["per_field"][1].__setitem__(
             "beta_true", 2.0), "CONTRACT_TRUE_BRIDGE_BETA_MISMATCH"),
    )
    for label, change, expected in targets:
        coherent, actual, preflight = propagated(contract, change, expected)
        check(label, coherent == "ACCEPTED" and actual == expected and preflight == expected,
              f"coherence={coherent}, conformance={actual}, preflight={preflight}")


def test_field_set(contract):
    n = len(contract["fields"])
    for i in range(n):
        for label, change, expected in (
            ("missing", lambda p, i=i: p["generating_model"]["per_field"].pop(i),
             "CONTRACT_FIELD_SET_MISMATCH"),
            ("duplicate", lambda p, i=i: p["generating_model"]["per_field"].__setitem__(i,
                copy.deepcopy(p["generating_model"]["per_field"][(i+1)%n])),
             "CONTRACT_FIELD_DUPLICATE"),
            ("renamed", lambda p, i=i: p["generating_model"]["per_field"][i].__setitem__(
                "id", "renamed_field"), "CONTRACT_FIELD_SET_MISMATCH"),
        ):
            coherent, actual, _ = propagated(contract, change, expected)
            check(f"field {i} {label}", coherent == "ACCEPTED" and actual == expected,
                  f"{coherent} / {actual}")
    coherent, actual, _ = propagated(contract,
        lambda p: p["generating_model"]["per_field"].append(
            dict(p["generating_model"]["per_field"][0], id="extra_field", reference=False)),
        "CONTRACT_FIELD_SET_MISMATCH")
    check("extra field", coherent == "ACCEPTED" and actual == "CONTRACT_FIELD_SET_MISMATCH",
          f"{coherent} / {actual}")
    for label, change in (
        ("missing reference", lambda p: p["generating_model"]["per_field"][0].__setitem__(
            "reference", False)),
        ("multiple references", lambda p: p["generating_model"]["per_field"][1].__setitem__(
            "reference", True)),
    ):
        coherent, actual, _ = propagated(contract, change, "CONTRACT_REFERENCE_FIELD_MISMATCH")
        check(label, coherent == "ACCEPTED" and actual == "CONTRACT_REFERENCE_FIELD_MISMATCH",
              f"{coherent} / {actual}")


def test_every_exact_binding(contract, plan):
    rows = [row for row in binding_specification(contract, plan) if row.relationship == EXACT]
    checked = 0
    for row in rows:
        if "[*]" in row.plan_path:
            # Field-set membership is exhaustively mutated in test_field_set.
            checked += 1
            continue
        old = access(plan, row.plan_path)
        assert old == row.actual, row.plan_path
        new = mutate(old)
        assert new != old, row.plan_path
        def change(p, path=row.plan_path, replacement=new):
            set_path(p, path, replacement)
            assert access(p, path) == replacement, path
        expected = ("CONTRACT_REFERENCE_FIELD_MISMATCH"
                    if row.plan_path.endswith(".reference") else
                    "CONTRACT_GENERATING_PARAMETER_MISMATCH")
        coherent, actual, _ = propagated(contract, change, expected)
        good = coherent == "ACCEPTED" and actual == expected
        check(f"EXACT {row.plan_path}", good, f"{old!r} -> {new!r}; {coherent}/{actual}")
        checked += good
    check("all EXACT mappings changed coherently then refused by contract",
          checked == len(rows), f"{checked}/{len(rows)}")


def test_beta_exceptions(contract, plan):
    rows = [r for r in binding_specification(contract, plan)
            if r.relationship == CASE_SPECIFIC_ALLOWED_OVERRIDE]
    check("C7 is the only authorised beta override",
          len(rows) == 5 and all("cases[6]" in r.plan_path for r in rows))
    for row in rows:
        coherent, actual, _ = propagated(contract,
            lambda p, path=row.plan_path, value=mutate(row.actual): set_path(p, path, value),
            "CONTRACT_TRUE_BRIDGE_BETA_MISMATCH")
        check(f"frozen C7 value {row.plan_path}",
              coherent == "ACCEPTED" and actual == "CONTRACT_TRUE_BRIDGE_BETA_MISMATCH",
              f"{coherent}/{actual}")


def test_relaxation_implementation(contract):
    binding = load_contract(ROOT)
    field = build_field(binding, contract["fields"][2],
                        calibration_route="force_displacement_with_stokes_drag",
                        viscosity=0.001, bead_radius=0.5e-6)
    expected_gamma = 6.0 * math.pi * field.viscosity * field.bead_radius
    check("OU drag is 6 pi eta(T) a",
          field.gamma == expected_gamma, f"gamma={field.gamma!r}")
    check("OU relaxation is per mode, gamma(T)/k_r",
          len(field.tau_modes) == 2 and field.tau_modes[0] != field.tau_modes[1]
          and field.tau_modes == tuple(field.gamma / k for k in field.k_modes),
          f"tau={field.tau_modes!r}")


def test_registry_fails_closed(contract, plan):
    changed = copy.deepcopy(contract)
    changed["hypothetical_uncertainty_scenario"]["new_execution_parameter"] = 17
    check("new contract authority cannot inherit NOT_APPLICABLE by default",
          code(require_contract_plan_conformance, changed, plan)
          == "CONTRACT_BINDING_UNCLASSIFIED")


def test_every_derived_binding(contract, plan):
    rows = [row for row in binding_specification(contract, plan)
            if row.relationship == DERIVED]
    good = 0
    for row in rows:
        new = mutate(row.actual)
        expected = ("CONTRACT_TRUE_BRIDGE_BETA_MISMATCH"
                    if row.plan_path.endswith((".beta_true", ".beta_truth")) else
                    "CONTRACT_RELAXATION_RULE_MISMATCH"
                    if row.plan_path.endswith(".tau_rule") else
                    "CONTRACT_GENERATING_PARAMETER_MISMATCH")
        coherent, actual, _ = propagated(contract,
            lambda p, path=row.plan_path, value=new: set_path(p, path, value), expected)
        if coherent != "ACCEPTED" or actual != expected:
            check(f"DERIVED {row.plan_path}", False,
                  f"{row.actual!r} -> {new!r}; {coherent}/{actual}")
        else:
            good += 1
    check("all DERIVED mappings changed coherently then refused by contract",
          good == len(rows), f"{good}/{len(rows)}")


def main():
    contract = rj(ROOT, "docs/e1a/e1a_v4_design_contract.json")
    plan = rj(ROOT, PLAN_JSON)
    check("unmodified plan conforms", code(require_contract_plan_conformance, contract, plan) == "ACCEPTED")
    inventory = binding_inventory(contract, plan)
    check("contract inventory is measured and complete",
          inventory["execution_relevant_contract_leaves"] > 0
          and inventory["unclassified_execution_relevant"] == 0, str(inventory))
    test_original_four(contract)
    test_field_set(contract)
    test_every_exact_binding(contract, plan)
    test_every_derived_binding(contract, plan)
    test_beta_exceptions(contract, plan)
    test_relaxation_implementation(contract)
    test_registry_fails_closed(contract, plan)
    print(f"RESULT: {PASSED} passed, {FAILED} failed")
    return 0 if FAILED == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
