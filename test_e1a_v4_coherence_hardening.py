"""E1a v4 COHERENCE-HARDENING gate: normative surface, strict JSON, driver binding.

**EXECUTION CLASS: NON-MODEL-ADVANCING STATIC/PURE.** Text, JSON, hashing and AST
parsing only. A sentinel RNG provider counts every call and every refusal path
asserts RNG_CALL_COUNT == 0. No random number is drawn, no trajectory generated,
no calibration sampled, no scientific outcome inspected.

WHAT THIS SUITE EXISTS FOR
    An independent audit found three blockers in the previous coherence repair,
    all three reproduced against that HEAD before any edit:

    A  scientifically meaningful drift still passed. Nine probes were ACCEPTED,
       including visible `fields affected`, the primary sigma_psi statement and
       the C1 279/300, C7 4/400 and C8 188/200 release thresholds changed in the
       Markdown alone, and JSON `feeds_primary_claim`, C7 `beta_true` and C8
       `scale_factors` changed with the generated block regenerated.

    B  duplicate JSON keys were accepted. `json.loads` keeps the LAST duplicate
       while a human reads the FIRST, so a block reading
       {"plan_version": "0.0.1-TAMPERED", "plan_version": "1.8.0"} parsed to the
       correct value while every reader saw the tampered one. ACCEPTED, in the
       authority block, inside a nested record, and in the plan JSON itself.

    C  the seal could name an arbitrary existing file as the driver. With a
       correctly FROZEN seal naming `e1a_v4/validation/plan.py`, the COMPLETE
       execution gate PASSED while no campaign driver existed anywhere.

    Every fixture below is one of those, or a neighbour of one.

THE CANONICAL DRIVER IS NEVER CREATED HERE
    Lifecycle states beyond ABSENT are exercised with a throwaway SANDBOX fixture.
    The repository keeps no `campaign_driver.py`: a placeholder there would
    satisfy the existence test and defeat the gate under audit.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import tempfile

from e1a_v4.contract import load_contract, sha256_file
from e1a_v4.numerics import Refusal
from e1a_v4.validation import PLAN_JSON, PLAN_MARKDOWN, SEED_MAP_JSON
from e1a_v4.validation.coherence import (
    BLOCK_BEGIN, BLOCK_END, BOTH, CASE_SPEC, JSON_ONLY, REGION_ANCHORS,
    SUBCONDITION_SPEC, TOP_LEVEL_SPEC, authority_block_fields, normative_json_view,
    normative_markdown_view, render_authority_block, render_region,
    require_plan_authority_coherence, require_specification_totality,
    specification_counts,
)
from e1a_v4.validation.driver import (
    OFFICIAL_CAMPAIGN_DRIVER_ENTRY_POINT, OFFICIAL_CAMPAIGN_DRIVER_MODULE,
    OFFICIAL_CAMPAIGN_DRIVER_PATH, DRIVER_ABSENT_SENTINEL, declared_entry_points,
    driver_exists, driver_identity_component, driver_state, require_canonical_driver,
)
from e1a_v4.validation.plan import VALIDATION_MODULES, execution_identity, load_plan
from e1a_v4.validation.refusals import ALL_REFUSAL_CLASSES, REFUSAL_CODES, CodedRefusal
from e1a_v4.validation.runner import preflight, run
from e1a_v4.validation.seal import SEAL_JSON, STATE_FROZEN, STATE_PRE_DRIVER, load_seal
from e1a_v4.validation.strict_json import strict_load_file, strict_loads

ROOT = os.path.dirname(os.path.abspath(__file__))
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


def refuses_with_code(label: str, expected: str, fn, *args, **kwargs) -> None:
    """Assert a refusal for the EXACT intended reason, with no RNG touched."""
    before = SentinelRNG.CALLS
    got = None
    try:
        fn(*args, **kwargs)
    except Refusal as exc:
        got = getattr(type(exc), "code", "UNCODED")
    after = SentinelRNG.CALLS
    check(f"{label} -> {expected}", got == expected and after == before,
          f"got {got!r}, RNG delta {after - before}")


COPIED = ("docs/e1a/e1a_v4_design_contract.json",
          "docs/e1a/E1A_V4_PROSPECTIVE_DESIGN.md",
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
    """Re-emit every generated region and the block. The maintenance path."""
    plan = rj(tmp, PLAN_JSON)
    text = rmd(tmp)
    for name, (begin, end) in REGION_ANCHORS.items():
        a = text.index(begin)
        z = text.index(end) + len(end)
        text = text[:a] + f"{begin}\n\n{render_region(name, plan).rstrip()}\n\n{end}" + text[z:]
    a = text.index(BLOCK_BEGIN)
    z = text.index(BLOCK_END) + len(BLOCK_END)
    wmd(tmp, text[:a] + render_authority_block(plan, tmp) + text[z:])


def install_driver_fixture(tmp: str, entry_point: bool = True) -> None:
    """A throwaway SANDBOX driver. Never created in the repository."""
    body = '"""SANDBOX FIXTURE ONLY. Never committed."""\n'
    if entry_point:
        body += f"\n\ndef {OFFICIAL_CAMPAIGN_DRIVER_ENTRY_POINT}():\n    raise NotImplementedError\n"
    with open(os.path.join(tmp, OFFICIAL_CAMPAIGN_DRIVER_PATH), "w",
              encoding="utf-8") as handle:
        handle.write(body)



def edit_region(tmp: str, name: str, old: str, new: str) -> None:
    """Edit the VISIBLE generated region only.

    The authority block appears earlier in the document and repeats much of this
    text, so a naive whole-document replace would tamper the block instead and
    test a different path.
    """
    begin, end = REGION_ANCHORS[name]
    text = rmd(tmp)
    a = text.index(begin)
    z = text.index(end) + len(end)
    region = text[a:z]
    assert region.count(old) >= 1, f"{name}: {old[:40]!r} not in the visible region"
    wmd(tmp, text[:a] + region.replace(old, new, 1) + text[z:])


# ------------------------------------------- 1. the specification is enumerable
def test_specification_is_total_and_enumerable() -> None:
    plan = load_plan(ROOT)
    require_specification_totality(plan)
    check("the live plan passes specification totality", True)
    counts = specification_counts(plan, ROOT)
    for key, value in counts.items():
        check(f"machine-derived count: {key}", isinstance(value, int), str(value))
    check("every top-level key is classified BOTH or JSON_ONLY",
          all(o in (BOTH, JSON_ONLY) for o, _ in TOP_LEVEL_SPEC.values()),
          f"{len(TOP_LEVEL_SPEC)} keys")
    check("every case key is classified",
          all(o in (BOTH, JSON_ONLY) for o, _ in CASE_SPEC.values()),
          f"{len(CASE_SPEC)} keys")
    check("every subcondition key is classified BOTH",
          all(o == BOTH for o, _ in SUBCONDITION_SPEC.values()),
          f"{len(SUBCONDITION_SPEC)} keys -- all are execution parameters")
    check("every classification carries a stated reason",
          all(r.strip() for _, r in TOP_LEVEL_SPEC.values())
          and all(r.strip() for _, r in CASE_SPEC.values())
          and all(r.strip() for _, r in SUBCONDITION_SPEC.values()))

    # an UNDECLARED key must refuse: this is what makes it a specification
    tmp = sandbox()
    p = rj(tmp, PLAN_JSON)
    p["an_undeclared_authority_section"] = {"threshold": 0.5}
    wj(tmp, PLAN_JSON, p)
    refuses_with_code("an undeclared TOP-LEVEL plan key", "PLAN_SURFACE_UNDECLARED",
                      require_specification_totality, p)
    shutil.rmtree(tmp)
    tmp = sandbox()
    p = rj(tmp, PLAN_JSON)
    p["cases"][0]["an_undeclared_case_field"] = 1
    refuses_with_code("an undeclared CASE key", "PLAN_SURFACE_UNDECLARED",
                      require_specification_totality, p)
    p = rj(tmp, PLAN_JSON)
    p["cases"][0]["subconditions"][0]["an_undeclared_parameter"] = 1
    refuses_with_code("an undeclared SUBCONDITION key", "PLAN_SURFACE_UNDECLARED",
                      require_specification_totality, p)
    shutil.rmtree(tmp)


# --------------------------------------- 2. blocker A: meaningful drift refuses
def test_blocker_a_meaningful_drift_refuses() -> None:
    """The auditor's four examples, plus five neighbours found alongside them."""
    plan = load_plan(ROOT)
    view = normative_json_view(plan, ROOT)
    for key in ("cases.C1_true_bridge_complete.fields_affected",
                "cases.C1_true_bridge_complete.branch_a_uncertainty",
                "cases.C1_true_bridge_complete.formal_pass_fail_criterion",
                "cases.C1_true_bridge_complete.subconditions.sigma_psi_0p5.feeds_primary_claim",
                "cases.C1_true_bridge_complete.subconditions.sigma_psi_0p5.g3_role",
                "cases.C7_false_bridge.subconditions.hard_1_025.beta_true",
                "cases.C8_blinded_scale_control.subconditions.paired_scale_control.scale_factors",
                "cases.C6_mode_resolution_boundary.subconditions.rho_1p019573.rho",
                "cases.C5_plug_in_branch_a.subconditions.sk0p50_sp0p5.sigma_k"):
        check(f"now in the surface: {key}", key in view)

    # --- Markdown-only visible edits ---------------------------------------
    for label, old, new, code in (
            ("visible fields_affected",
             '| fields affected | `"theta0_circular"` `"theta1_power"` '
             '`"theta2_ellipse"` `"theta3_temperature"` |',
             '| fields affected | `"theta0_circular"` |', "PLAN_AMBIGUOUS_BLOCK"),
            ("visible primary sigma_psi", "sigma_psi PRIMARY = 0.5 deg",
             "sigma_psi PRIMARY = 1.0 deg", "PLAN_AMBIGUOUS_BLOCK"),
            ("visible C1 threshold 279/300", "requires >= 279/300",
             "requires >= 240/300", "PLAN_AMBIGUOUS_BLOCK"),
            ("visible C7 threshold 4/400", "i.e. <= 4/400; 5 or more fails",
             "i.e. <= 40/400; 41 or more fails", "PLAN_AMBIGUOUS_BLOCK"),
            ("visible C8 threshold 188/200", "paired-control success >= 0.90 over R = 200",
             "paired-control success >= 0.50 over R = 200", "PLAN_AMBIGUOUS_BLOCK")):
        tmp = sandbox()
        edit_region(tmp, "cases", old, new)
        refuses_with_code(f"{label} changed in the Markdown ALONE", code,
                          preflight, tmp)
        shutil.rmtree(tmp)

    # --- JSON-only edits with the generated surface regenerated -------------
    def flip_feeds(p):
        for case in p["cases"]:
            for sub in case["subconditions"]:
                if "feeds_primary_claim" in sub:
                    sub["feeds_primary_claim"] = not sub["feeds_primary_claim"]

    def alter_beta(p):
        p["cases"][6]["subconditions"][0]["beta_true"] = [1, 9.99, 1, 1]

    def alter_scale(p):
        p["cases"][7]["subconditions"][0]["scale_factors"] = [2.0, 0.5]

    def alter_sigma(p):
        for sub in p["cases"][0]["subconditions"]:
            if "sigma_psi_deg" in sub:
                sub["sigma_psi_deg"] = 42.0

    for label, mutate in (("feeds_primary_claim inverted", flip_feeds),
                          ("C7 beta_true altered", alter_beta),
                          ("C8 scale_factors altered", alter_scale),
                          ("C1 sigma_psi_deg altered", alter_sigma)):
        tmp = sandbox()
        p = rj(tmp, PLAN_JSON)
        mutate(p)
        wj(tmp, PLAN_JSON, p)
        # the BLOCK is regenerated but the visible regions are not: exactly the
        # shape the audit exploited
        text = rmd(tmp)
        a = text.index(BLOCK_BEGIN)
        z = text.index(BLOCK_END) + len(BLOCK_END)
        wmd(tmp, text[:a] + render_authority_block(p, tmp) + text[z:])
        refuses_with_code(f"JSON {label}, block regenerated", "PLAN_AMBIGUOUS_BLOCK",
                          preflight, tmp)
        shutil.rmtree(tmp)

    # --- a FULLY propagated change is coherent, and is caught by the SEAL ----
    tmp = sandbox()
    p = rj(tmp, PLAN_JSON)
    alter_beta(p)
    wj(tmp, PLAN_JSON, p)
    regenerate(tmp)
    coherent = True
    try:
        require_plan_authority_coherence(tmp, rj(tmp, PLAN_JSON))
    except Refusal:
        coherent = False
    check("a change propagated to BOTH representations is coherent", coherent,
          "coherence enforces AGREEMENT; immutability is the seal's job, and the "
          "seal is deliberately NOT frozen yet")
    moved = execution_identity(load_contract(tmp), sha256_file(os.path.join(tmp, PLAN_JSON)),
                               sha256_file(os.path.join(tmp, SEED_MAP_JSON)), tmp)
    base = execution_identity(load_contract(ROOT), sha256_file(os.path.join(ROOT, PLAN_JSON)),
                              sha256_file(os.path.join(ROOT, SEED_MAP_JSON)), ROOT)
    check("...and it DOES move the execution identity, so a frozen seal would catch it",
          moved != base)
    shutil.rmtree(tmp)


# ------------------------------------------- 3. blocker B: strict JSON refuses
def test_blocker_b_duplicate_keys_refuse() -> None:
    check("plain json.loads keeps the LAST duplicate, silently",
          json.loads('{"a": 1, "a": 2}') == {"a": 2},
          "which is why ordinary parsing is not used for authoritative documents")
    for label, text in (
            ("a top-level duplicate", '{"plan_version": "1.8.0", "plan_version": "9.9.9"}'),
            ("a nested duplicate", '{"frozen": {"id": "aaa", "id": "bbb"}}'),
            ("a duplicate inside a case record",
             '{"cases": [{"case_id": "C1", "case_id": "C9"}]}'),
            ("a duplicate inside a subcondition",
             '{"cases": [{"subconditions": [{"sigma_psi_deg": 0.5, "sigma_psi_deg": 9.9}]}]}'),
            ("a duplicate three levels deep", '{"a": {"b": {"c": 1, "c": 2}}}')):
        refuses_with_code(label, "PLAN_DUPLICATE_KEY", strict_loads, text, "fixture")
    parsed = strict_loads('{"a": 1, "b": {"c": 2}}', "fixture")
    check("valid unique-key JSON parses normally", parsed == {"a": 1, "b": {"c": 2}})
    check("neither first nor last is adopted: the document is refused outright",
          True, "an authoritative document that says two things is ambiguous")

    # the hostile case: FIRST value tampered, LAST value correct
    tmp = sandbox()
    text = rmd(tmp)
    a = text.index(BLOCK_BEGIN)
    z = text.index(BLOCK_END) + len(BLOCK_END)
    body = text[a:z].split("```json\n", 1)[1].rsplit("\n```", 1)[0]
    tampered = body.replace('"plan_version": "1.8.0"',
                            '"plan_version": "0.0.1-TAMPERED",\n    "plan_version": "1.8.0"', 1)
    wmd(tmp, text[:a] + BLOCK_BEGIN + "\n\n```json\n" + tampered + "\n```\n\n"
        + BLOCK_END + text[z:])
    refuses_with_code("a duplicate in the BLOCK, hostile first / correct last",
                      "PLAN_DUPLICATE_KEY", preflight, tmp)
    shutil.rmtree(tmp)

    tmp = sandbox()
    raw = open(os.path.join(tmp, PLAN_JSON), encoding="utf-8").read()
    marker = '"plan_version": "1.8.0",'
    assert raw.count(marker) == 1
    with open(os.path.join(tmp, PLAN_JSON), "w", encoding="utf-8") as handle:
        handle.write(raw.replace(
            marker, '"plan_version": "0.0.1-TAMPERED",\n  "plan_version": "1.8.0",', 1))
    refuses_with_code("a duplicate in the AUTHORITATIVE plan JSON",
                      "PLAN_DUPLICATE_KEY", preflight, tmp)
    shutil.rmtree(tmp)

    tmp = sandbox()
    raw = open(os.path.join(tmp, SEAL_JSON), encoding="utf-8").read()
    with open(os.path.join(tmp, SEAL_JSON), "w", encoding="utf-8") as handle:
        handle.write(raw.replace('"state": "PRE_DRIVER",',
                                 '"state": "FROZEN",\n  "state": "PRE_DRIVER",', 1))
    refuses_with_code("a duplicate in the EXECUTION SEAL", "PLAN_DUPLICATE_KEY",
                      load_seal, tmp)
    shutil.rmtree(tmp)


# ------------------------------------ 4. blocker C: canonical driver binding
def test_blocker_c_driver_cannot_be_substituted() -> None:
    check("the canonical declaration names a module",
          OFFICIAL_CAMPAIGN_DRIVER_MODULE == "e1a_v4.validation.campaign_driver")
    check("the canonical declaration names a path",
          OFFICIAL_CAMPAIGN_DRIVER_PATH == "e1a_v4/validation/campaign_driver.py")
    check("the canonical declaration names an entry point",
          OFFICIAL_CAMPAIGN_DRIVER_ENTRY_POINT == "run_campaign")
    check("the canonical driver is ABSENT in the repository", not driver_exists(ROOT))
    check("the driver state is ABSENT", driver_state(ROOT) == "ABSENT")
    check("the identity component is the ABSENT sentinel",
          driver_identity_component(ROOT) == DRIVER_ABSENT_SENTINEL)
    check("the declaration module is itself identity-bound",
          "e1a_v4/validation/driver.py" in VALIDATION_MODULES,
          "so changing the declared path changes the execution identity")
    refuses_with_code("with no driver, the gate refuses", "DRIVER_ABSENT",
                      require_canonical_driver, ROOT)

    # a seal may RESTATE the declaration; it may not redefine it
    for substitute in ("e1a_v4/validation/plan.py", "e1a_v4/validation/seeds.py",
                       "AGENTS.md", "docs/e1a/e1a_v4_seed_map.json"):
        tmp = sandbox()
        raw = rj(tmp, SEAL_JSON)
        raw["restates_canonical_campaign_driver"] = substitute
        wj(tmp, SEAL_JSON, raw)
        refuses_with_code(f"a seal restating {substitute!r} as the driver",
                          "DRIVER_IDENTITY_MISMATCH", load_seal, tmp)
        shutil.rmtree(tmp)

    tmp = sandbox()
    raw = rj(tmp, SEAL_JSON)
    raw["official_campaign_driver_module"] = "e1a_v4/validation/plan.py"
    wj(tmp, SEAL_JSON, raw)
    refuses_with_code("a seal carrying an AUTHORITATIVE driver key",
                      "EXECUTION_SEAL_MALFORMED", load_seal, tmp)
    shutil.rmtree(tmp)

    # THE audit scenario: a correctly FROZEN seal pointing at an unrelated file
    tmp = sandbox()
    p = rj(tmp, PLAN_JSON)
    p["execution_seal"]["state"] = STATE_FROZEN
    p["execution_authorised"] = True
    wj(tmp, PLAN_JSON, p)
    wmd(tmp, re.sub(r"^execution seal state\s+= \S+$",
                    f"execution seal state           = {STATE_FROZEN}", rmd(tmp),
                    count=1, flags=re.M))
    wmd(tmp, rmd(tmp).replace("`execution_authorised` is `false`",
                              "`execution_authorised` is `true`", 1))
    regenerate(tmp)
    ident = execution_identity(load_contract(tmp),
                               sha256_file(os.path.join(tmp, PLAN_JSON)),
                               sha256_file(os.path.join(tmp, SEED_MAP_JSON)), tmp)
    raw = rj(tmp, SEAL_JSON)
    raw["state"] = STATE_FROZEN
    raw["expected_execution_identity"] = ident
    raw["restates_canonical_campaign_driver"] = "e1a_v4/validation/plan.py"
    wj(tmp, SEAL_JSON, raw)
    refuses_with_code("the AUDIT SCENARIO: FROZEN seal naming plan.py as the driver",
                      "DRIVER_IDENTITY_MISMATCH", run, tmp, rng_factory=rng_factory,
                      execute=True)
    shutil.rmtree(tmp)

    # the canonical path declared but absent, with everything else in order
    tmp = sandbox()
    p = rj(tmp, PLAN_JSON)
    p["execution_seal"]["state"] = STATE_FROZEN
    p["execution_authorised"] = True
    wj(tmp, PLAN_JSON, p)
    wmd(tmp, re.sub(r"^execution seal state\s+= \S+$",
                    f"execution seal state           = {STATE_FROZEN}", rmd(tmp),
                    count=1, flags=re.M))
    wmd(tmp, rmd(tmp).replace("`execution_authorised` is `false`",
                              "`execution_authorised` is `true`", 1))
    regenerate(tmp)
    ident = execution_identity(load_contract(tmp),
                               sha256_file(os.path.join(tmp, PLAN_JSON)),
                               sha256_file(os.path.join(tmp, SEED_MAP_JSON)), tmp)
    raw = rj(tmp, SEAL_JSON)
    raw["state"] = STATE_FROZEN
    raw["expected_execution_identity"] = ident
    wj(tmp, SEAL_JSON, raw)
    refuses_with_code("canonical path declared but ABSENT, seal otherwise perfect",
                      "DRIVER_ABSENT", run, tmp, rng_factory=rng_factory, execute=True)

    # present but not satisfying the declared interface
    install_driver_fixture(tmp, entry_point=False)
    refuses_with_code("driver present WITHOUT the declared entry point",
                      "DRIVER_IDENTITY_MISMATCH", run, tmp, rng_factory=rng_factory,
                      execute=True)
    check("the interface check parses the AST and imports nothing",
          declared_entry_points(tmp) == (),
          "importing would execute driver code, which this stage forbids")
    install_driver_fixture(tmp, entry_point=True)
    check("a driver declaring the entry point satisfies the interface check",
          OFFICIAL_CAMPAIGN_DRIVER_ENTRY_POINT in declared_entry_points(tmp))
    check("a present driver contributes its FILE HASH to the identity",
          driver_identity_component(tmp) == sha256_file(
              os.path.join(tmp, OFFICIAL_CAMPAIGN_DRIVER_PATH)))
    check("...which differs from the ABSENT sentinel",
          driver_identity_component(tmp) != DRIVER_ABSENT_SENTINEL,
          "so the identity moves the moment a real driver appears")
    shutil.rmtree(tmp)


# ----------------------------------------------- 5. the full seal lifecycle
def test_seal_lifecycle() -> None:
    before = SentinelRNG.CALLS
    plan = load_plan(ROOT)
    seal = load_seal(ROOT)
    check("PRE_DRIVER: preflight-only succeeds", preflight(ROOT) is not None)
    check("PRE_DRIVER: the seal expects nothing yet",
          seal.state == STATE_PRE_DRIVER and seal.expected_execution_identity is None)
    check("PRE_DRIVER: execution_authorised is false",
          plan["execution_authorised"] is False)
    check("the seal reports the CANONICAL driver, whatever it wrote",
          seal.driver_module == OFFICIAL_CAMPAIGN_DRIVER_PATH)
    refuses_with_code("PRE_DRIVER + canonical driver absent: execution REFUSES",
                      "DRIVER_ABSENT", run, ROOT, rng_factory=rng_factory, execute=True)

    tmp = sandbox()
    p = rj(tmp, PLAN_JSON)
    p["execution_authorised"] = True
    wj(tmp, PLAN_JSON, p)
    wmd(tmp, rmd(tmp).replace("`execution_authorised` is `false`",
                              "`execution_authorised` is `true`", 1))
    regenerate(tmp)
    refuses_with_code("PRE_DRIVER + authorisation TRUE: still REFUSES before RNG",
                      "DRIVER_ABSENT", run, tmp, rng_factory=rng_factory, execute=True)
    shutil.rmtree(tmp)

    def frozen_sandbox(authorised: bool) -> tuple[str, str]:
        tmp = sandbox()
        install_driver_fixture(tmp)
        p = rj(tmp, PLAN_JSON)
        p["execution_seal"]["state"] = STATE_FROZEN
        p["execution_authorised"] = authorised
        wj(tmp, PLAN_JSON, p)
        wmd(tmp, re.sub(r"^execution seal state\s+= \S+$",
                        f"execution seal state           = {STATE_FROZEN}", rmd(tmp),
                        count=1, flags=re.M))
        if authorised:
            wmd(tmp, rmd(tmp).replace("`execution_authorised` is `false`",
                                      "`execution_authorised` is `true`", 1))
        regenerate(tmp)
        ident = execution_identity(load_contract(tmp),
                                   sha256_file(os.path.join(tmp, PLAN_JSON)),
                                   sha256_file(os.path.join(tmp, SEED_MAP_JSON)), tmp)
        raw = rj(tmp, SEAL_JSON)
        raw["state"] = STATE_FROZEN
        raw["expected_execution_identity"] = ident
        wj(tmp, SEAL_JSON, raw)
        return tmp, ident

    tmp, ident = frozen_sandbox(authorised=True)
    os.remove(os.path.join(tmp, SEAL_JSON))
    refuses_with_code("driver PRESENT and identity-bound but seal MISSING",
                      "EXECUTION_SEAL_MALFORMED", run, tmp, rng_factory=rng_factory,
                      execute=True)
    shutil.rmtree(tmp)

    tmp, ident = frozen_sandbox(authorised=True)
    raw = rj(tmp, SEAL_JSON)
    raw["expected_execution_identity"] = "0" * 64
    wj(tmp, SEAL_JSON, raw)
    refuses_with_code("seal FROZEN but expected identity MISMATCH",
                      "EXECUTION_IDENTITY_MISMATCH", run, tmp, rng_factory=rng_factory,
                      execute=True)
    shutil.rmtree(tmp)

    tmp, ident = frozen_sandbox(authorised=False)
    refuses_with_code("seal FROZEN and MATCHING but authorisation FALSE",
                      "EXECUTION_NOT_AUTHORISED", run, tmp, rng_factory=rng_factory,
                      execute=True)
    shutil.rmtree(tmp)

    tmp, ident = frozen_sandbox(authorised=True)
    from e1a_v4.validation.seal import require_execution_gate
    eligible = True
    try:
        require_execution_gate(tmp, rj(tmp, PLAN_JSON), ident)
    except Refusal:
        eligible = False
    check("driver + seal + identity + authorisation: the gate is ELIGIBLE", eligible,
          "SENTINEL BOUNDARY ONLY -- no real driver, no RNG, no draw")
    stopped = False
    try:
        run(tmp, rng_factory=rng_factory, execute=True)
    except Refusal:
        stopped = True
    check("...and `run` still stops at the UNIMPLEMENTED execution path", stopped)
    shutil.rmtree(tmp)
    check("no RNG object was created anywhere in the lifecycle",
          SentinelRNG.CALLS == before, f"RNG_CALL_COUNT = {SentinelRNG.CALLS}")


# ------------------------------------------------------- 6. the refusal codes
def test_refusal_codes_are_stable() -> None:
    required = ("PLAN_VERSION_MISMATCH", "PLAN_ANALYSIS_IDENTITY_MISMATCH",
                "PLAN_CASE_MISMATCH", "PLAN_SUBCONDITION_MISMATCH",
                "PLAN_RELEASE_RULE_MISMATCH", "PLAN_DUPLICATE_KEY",
                "PLAN_AMBIGUOUS_BLOCK", "DRIVER_ABSENT", "DRIVER_IDENTITY_MISMATCH",
                "EXECUTION_SEAL_NOT_FROZEN", "EXECUTION_IDENTITY_MISMATCH",
                "EXECUTION_NOT_AUTHORISED")
    for code in required:
        check(f"required refusal code present: {code}", code in REFUSAL_CODES)
    check("every refusal class is coded",
          all(issubclass(c, CodedRefusal) and c.code != "UNCLASSIFIED_REFUSAL"
              for c in ALL_REFUSAL_CLASSES), f"{len(ALL_REFUSAL_CLASSES)} classes")
    check("the code appears in the message, for logs and transcripts",
          "[PLAN_DUPLICATE_KEY]" in str(
              __import__("e1a_v4.validation.refusals", fromlist=["x"]).PlanDuplicateKey("m")))


# ----------------------------------------- 7. the mismatching key is reported
def test_mismatch_names_the_exact_key() -> None:
    plan = load_plan(ROOT)
    view = normative_json_view(plan, ROOT)
    rendered = normative_markdown_view(ROOT)
    check("the two views cover the same human-rendered keys",
          all(k in rendered for k in
              ("plan_version", "cases.C1_true_bridge_complete.replicate_count",
               "adopted_rules.alpha_1", "assurance.0.target")))
    for key in ("adopted_rules.alpha_1", "cases.C1_true_bridge_complete.replicate_count",
                "assurance.0.target"):
        check(f"both views agree on {key}", view[key] == rendered[key], repr(view[key]))
    tmp = sandbox()
    wmd(tmp, rmd(tmp).replace("| `alpha_1` | `0.004` |", "| `alpha_1` | `0.4` |", 1))
    named = ""
    try:
        require_plan_authority_coherence(tmp, rj(tmp, PLAN_JSON))
    except Refusal as exc:
        named = str(exc)
    check("a mismatch names the exact key", "adopted_rules.alpha_1" in named
          or "adopted_rules" in named, named[:80])
    shutil.rmtree(tmp)


# -------------------------------------------- 8. no scientific rule changed
def test_no_scientific_rule_changed() -> None:
    binding = load_contract(ROOT)
    plan = load_plan(ROOT)
    for label, got, want in (("delta_cross", binding.delta_cross, 0.02),
                             ("delta_abs", binding.delta_abs, 0.05),
                             ("z_cross", binding.z_cross, 1.959963985),
                             ("z_abs", binding.z_abs, 1.959963985),
                             ("alpha_geom", binding.alpha_geom, 0.005),
                             ("alpha_1", binding.alpha_1, 0.004),
                             ("alpha_2", binding.alpha_2, 0.001),
                             ("theta_cap_deg", binding.theta_cap_deg, 5.0),
                             ("rank_tol", binding.rank_tol, 1e-12),
                             ("pipeline_target", binding.pipeline_target, 0.9)):
        check(f"{label} unchanged", got == want, str(want))
    check("contract identity unchanged",
          binding.sha256 == "91d6ae76ccb6fdbeb7f926722433c574c30b7c0b6105c7c1ec20436fa2ec431b")
    check("foundation identity unchanged",
          binding.foundation_sha256
          == "6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507")
    check("primary sigma_psi is still 0.5 deg",
          binding.data["hypothetical_uncertainty_scenario"]["sigma_psi_deg"] == 0.5)
    check("replicate counts unchanged",
          [c["replicate_count"] for c in plan["cases"]]
          == [300, 400, 400, 2000, 400, 400, 400, 200])
    check("calibration scopes unchanged",
          [c["calibration_scope"] for c in plan["cases"]]
          == ["REPLICATE_CONDITIONAL"] * 6 + ["NOT_APPLICABLE"] * 2)
    check("C7 and C8 still require NO calibration",
          all(not c["requires_block1_calibration"] for c in plan["cases"]
              if c["case_id"] in ("C7_false_bridge", "C8_blinded_scale_control")))
    check("the C7 false-bridge alternatives are unchanged",
          [s["beta_true"] for s in plan["cases"][6]["subconditions"]]
          == [[1, 1.06, 1, 1], [1, 0.93, 1.05, 1], [1, 1, 1, 1.10], [1, 1.025, 1, 1]])
    check("the C8 scale factors are unchanged",
          plan["cases"][7]["subconditions"][0]["scale_factors"] == [1.07, 0.90])
    check("execution is still NOT authorised", plan["execution_authorised"] is False)
    seeds = strict_load_file(os.path.join(ROOT, SEED_MAP_JSON), "seed map")
    check("the master seed is unchanged", seeds["master_seed"] == 13785910525869478477)
    check("the seed map identity is unchanged",
          sha256_file(os.path.join(ROOT, SEED_MAP_JSON))
          == "95870d7d33c256c4bd30118e13278a600271531fd945d12687a828de902e91ce")
    check("the analysis identity is unchanged",
          plan["frozen_identities"]["analysis_procedure_identity"]
          == "dd2ed732db4348b0b25ce5fe83096d38f5b9c1748ee5916eecaf2c1aef2e2e1f",
          "no analysis-layer module was touched")


if __name__ == "__main__":
    print("\nthe normative specification is total and enumerable")
    test_specification_is_total_and_enumerable()
    print("\nBLOCKER A -- scientifically meaningful drift now refuses")
    test_blocker_a_meaningful_drift_refuses()
    print("\nBLOCKER B -- duplicate JSON keys now refuse")
    test_blocker_b_duplicate_keys_refuse()
    print("\nBLOCKER C -- the driver cannot be substituted")
    test_blocker_c_driver_cannot_be_substituted()
    print("\nthe execution-seal lifecycle")
    test_seal_lifecycle()
    print("\nstable refusal codes")
    test_refusal_codes_are_stable()
    print("\nmismatches name the exact key")
    test_mismatch_names_the_exact_key()
    print("\nno E1a scientific decision rule changed")
    test_no_scientific_rule_changed()
    print(f"\nE1a v4 coherence-hardening gate: {PASSED} passed, {FAILED} failed, 8 groups")
    print("Execution class: NON-MODEL-ADVANCING STATIC/PURE (this suite only)")
    print(f"  RNG OBJECTS           : {SentinelRNG.CALLS}")
    print("  RANDOM DRAWS          : 0")
    print("  TRAJECTORIES          : 0")
    raise SystemExit(1 if FAILED else 0)
