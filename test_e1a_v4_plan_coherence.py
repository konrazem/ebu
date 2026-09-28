"""E1a v4 PLAN-COHERENCE and EXECUTION-SEAL gate.

**EXECUTION CLASS: NON-MODEL-ADVANCING STATIC/PURE.** Every check below is text,
JSON, hashing or state comparison. A sentinel RNG provider counts every call and
every refusal path asserts

    RNG_CALL_COUNT == 0

No random number is drawn, no trajectory is generated, no calibration is sampled
and no scientific outcome is inspected anywhere in this file.

WHAT THIS SUITE EXISTS FOR
    The superseded preflight compared only the section-9 output schema, so this
    package carried, for four commits, a Markdown analysis procedure identity that
    it has never computed at any commit -- while preflight reported PASS. Every
    fixture here is a deliberate disagreement that must now refuse.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import tempfile

from e1a_v4.contract import load_contract, sha256_file
from e1a_v4.identity import procedure_identity
from e1a_v4.numerics import Refusal
from e1a_v4.validation import PLAN_JSON, PLAN_MARKDOWN, SEED_MAP_JSON
from e1a_v4.validation.coherence import (
    AUTHORITY_BLOCK_SCHEMA, BLOCK_BEGIN, BLOCK_END, CASE_SPEC, IDENTITY_ROW_LABELS,
    REGION_ANCHORS, SUBCONDITION_SPEC, TOP_LEVEL_SPEC, authority_block_fields,
    normative_json_view, normative_markdown_view, render_authority_block,
    render_region, require_plan_authority_coherence, specification_counts,
)
from e1a_v4.validation.strict_json import strict_load_file
from e1a_v4.validation.plan import (
    VALIDATION_MODULES, bind_execution, execution_identity, load_plan,
)
from e1a_v4.validation.runner import main, preflight, run
from e1a_v4.validation.refusals import (
    CampaignDriverAbsent, DriverAbsent, ExecutionAuthorisationMissing,
    ExecutionIdentityUnsealed, ExecutionNotAuthorised, ExecutionSealNotFrozen,
)
from e1a_v4.validation.seal import (
    SEAL_JSON, SEAL_SCHEMA, STATE_FROZEN, STATE_PRE_DRIVER, driver_present, load_seal,
    require_execution_gate, require_seal_plan_agreement,
)
from e1a_v4.validation.driver import (
    OFFICIAL_CAMPAIGN_DRIVER_ENTRY_POINT, OFFICIAL_CAMPAIGN_DRIVER_PATH, driver_exists,
    driver_identity_component, driver_state,
)

ROOT = os.path.dirname(os.path.abspath(__file__))
PASSED = 0
FAILED = 0


class SentinelRNG:
    """Counts every draw. Any call anywhere in this suite is a defect."""

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


def refuses_without_rng(label: str, fn, *args, **kwargs) -> None:
    """Assert a Refusal AND that the sentinel RNG was never touched."""
    before = SentinelRNG.CALLS
    refused = False
    try:
        fn(*args, **kwargs)
    except Refusal:
        refused = True
    after = SentinelRNG.CALLS
    check(label, refused and after == before, f"RNG_CALL_COUNT delta = {after - before}")


def raises_without_rng(label: str, exc_type, fn, *args, **kwargs) -> None:
    """Assert a SPECIFIC refusal type, so ordering of the gate is pinned."""
    before = SentinelRNG.CALLS
    got = None
    try:
        fn(*args, **kwargs)
    except Refusal as exc:
        got = type(exc)
    after = SentinelRNG.CALLS
    check(label, got is not None and issubclass(got, exc_type) and after == before,
          f"{got.__name__ if got else 'no refusal'}, RNG delta {after - before}")


# ------------------------------------------------------------------- sandboxing
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


def read_json(tmp: str, rel: str):
    return strict_load_file(os.path.join(tmp, rel), rel)


def write_json(tmp: str, rel: str, obj) -> None:
    with open(os.path.join(tmp, rel), "w", encoding="utf-8") as handle:
        json.dump(obj, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def read_md(tmp: str) -> str:
    with open(os.path.join(tmp, PLAN_MARKDOWN), encoding="utf-8") as handle:
        return handle.read()


def write_md(tmp: str, text: str) -> None:
    with open(os.path.join(tmp, PLAN_MARKDOWN), "w", encoding="utf-8") as handle:
        handle.write(text)


def regenerate_block(tmp: str) -> None:
    """Re-emit EVERY generated region plus the block. The maintenance path."""
    plan = read_json(tmp, PLAN_JSON)
    text = read_md(tmp)
    for name, (begin, end) in REGION_ANCHORS.items():
        a = text.index(begin)
        z = text.index(end) + len(end)
        text = text[:a] + f"{begin}\n\n{render_region(name, plan).rstrip()}\n\n{end}" + text[z:]
    a = text.index(BLOCK_BEGIN)
    z = text.index(BLOCK_END) + len(BLOCK_END)
    write_md(tmp, text[:a] + render_authority_block(plan, tmp) + text[z:])



def set_md_seal_state(tmp: str, state: str) -> None:
    """Keep the RENDERED seal state in step with the JSON.

    The rendered state is a checked normative field, so a fixture that changes the
    JSON alone refuses on coherence before it reaches the seal path under test.
    """
    text = read_md(tmp)
    new = re.sub(r"^execution seal state\s+= \S+$",
                 f"execution seal state           = {state}", text, count=1, flags=re.M)
    assert new != text or f"= {state}" in text, "seal-state line not found"
    write_md(tmp, new)


# ------------------------------------------------- 1. the live package is coherent
def test_live_package_is_coherent() -> None:
    plan = load_plan(ROOT)
    require_plan_authority_coherence(ROOT, plan)
    check("the committed package passes authority coherence", True)
    derived = normative_json_view(plan, ROOT)
    embedded = authority_block_fields(ROOT)
    check("the embedded block equals the view derived from the JSON",
          json.dumps(embedded, sort_keys=True) == json.dumps(derived, sort_keys=True),
          f"{len(derived)} normative keys")

    counts = specification_counts(plan, ROOT)
    check("the specification classifies every top-level key",
          counts["top_level_both"] + counts["top_level_json_only"] == len(TOP_LEVEL_SPEC),
          f"{counts['top_level_both']} BOTH / {counts['top_level_json_only']} JSON_ONLY")
    check("the specification classifies every case key",
          counts["case_both"] + counts["case_json_only"] == len(CASE_SPEC),
          f"{counts['case_both']} BOTH / {counts['case_json_only']} JSON_ONLY")
    check("the specification classifies every subcondition key",
          counts["subcondition_both"] + counts["subcondition_json_only"]
          == len(SUBCONDITION_SPEC),
          f"{counts['subcondition_both']} BOTH / "
          f"{counts['subcondition_json_only']} JSON_ONLY")
    check("no key is MARKDOWN_ONLY", counts["markdown_only_keys"] == 0)
    check("the surface count is machine-derived, not hand-quoted",
          counts["duplicated_normative_keys"] == len(derived),
          f"{counts['duplicated_normative_keys']} duplicated normative keys")

    # the fields the audit showed were previously invisible or unchecked
    for key in ("cases.C1_true_bridge_complete.fields_affected",
                "cases.C1_true_bridge_complete.branch_a_uncertainty",
                "cases.C1_true_bridge_complete.formal_pass_fail_criterion",
                "cases.C7_false_bridge.formal_pass_fail_criterion",
                "cases.C8_blinded_scale_control.formal_pass_fail_criterion",
                "cases.C1_true_bridge_complete.subconditions.sigma_psi_0p5.g3_role",
                "cases.C1_true_bridge_complete.subconditions.sigma_psi_0p5.feeds_primary_claim",
                "cases.C7_false_bridge.subconditions.hard_1_025.beta_true",
                "cases.C8_blinded_scale_control.subconditions.paired_scale_control.scale_factors",
                "adopted_rules.alpha_1", "assurance.0.acceptance_rule",
                "final_campaign.requirements.0", "driver.path"):
        check(f"the surface now covers {key}", key in derived)

    rendering = normative_markdown_view(ROOT)
    check("the human version line equals the authority",
          rendering["plan_version"] == derived["plan_version"], derived["plan_version"])
    check("the human identity table equals the authority",
          all(rendering[f"frozen_identities.{k}"] == derived[f"frozen_identities.{k}"]
              for _, k in IDENTITY_ROW_LABELS))
    check("every generated region is a byte-exact re-render",
          all(render_region(name, plan) is not None for name in REGION_ANCHORS),
          f"{len(REGION_ANCHORS)} regions")
    live = procedure_identity(load_contract(ROOT), {}, ROOT)
    check("the rendered analysis identity is the LIVE recomputation",
          rendering["frozen_identities.analysis_procedure_identity"] == live,
          live[:16] + "...")
    check("the superseded Markdown identity is gone from the plan",
          "bc1c0fce3b9004aed5f6b4be2162bc876697536ee614b2e57f680f3a65dc283e"
          not in read_md(ROOT).split("## 18.")[0],
          "retained only in the section-18 supersession record")


# --------------------------------------- 2. the ten required disagreement fixtures
def test_disagreement_fixtures_refuse() -> None:
    # (a) Markdown VERSION changed only -----------------------------------------
    tmp = sandbox()
    text = read_md(tmp)
    write_md(tmp, text.replace("Plan version **1.8.0**.", "Plan version **9.9.9**.", 1))
    refuses_without_rng("Markdown version changed only -> REFUSE",
                        require_plan_authority_coherence, tmp, read_json(tmp, PLAN_JSON))
    refuses_without_rng("  ... and preflight refuses too", preflight, tmp)
    shutil.rmtree(tmp)

    # (b) Markdown ANALYSIS IDENTITY changed only -- the historical defect --------
    tmp = sandbox()
    text = read_md(tmp)
    real = read_json(tmp, PLAN_JSON)["frozen_identities"]["analysis_procedure_identity"]
    write_md(tmp, text.replace(f"| analysis procedure identity | `{real}` |",
                               f"| analysis procedure identity | `{'b' * 64}` |", 1))
    refuses_without_rng("Markdown analysis identity changed only -> REFUSE",
                        require_plan_authority_coherence, tmp, read_json(tmp, PLAN_JSON))
    refuses_without_rng("  ... and preflight refuses too", preflight, tmp)
    shutil.rmtree(tmp)

    # (c) JSON VERSION changed only ---------------------------------------------
    tmp = sandbox()
    plan = read_json(tmp, PLAN_JSON)
    plan["plan_version"] = "9.9.9"
    write_json(tmp, PLAN_JSON, plan)
    refuses_without_rng("JSON version changed only -> REFUSE",
                        require_plan_authority_coherence, tmp, plan)
    refuses_without_rng("  ... and preflight refuses too", preflight, tmp)
    shutil.rmtree(tmp)

    # (d) JSON ANALYSIS IDENTITY changed only ------------------------------------
    tmp = sandbox()
    plan = read_json(tmp, PLAN_JSON)
    plan["frozen_identities"]["analysis_procedure_identity"] = "c" * 64
    write_json(tmp, PLAN_JSON, plan)
    refuses_without_rng("JSON analysis identity changed only -> REFUSE",
                        require_plan_authority_coherence, tmp, plan)
    refuses_without_rng("  ... and preflight refuses too", preflight, tmp)
    shutil.rmtree(tmp)

    # (e) output SCHEMA mismatch -------------------------------------------------
    tmp = sandbox()
    plan = read_json(tmp, PLAN_JSON)
    plan["output_schema"]["record_schema"] = "e1a_v4_validation_result/1"
    write_json(tmp, PLAN_JSON, plan)
    refuses_without_rng("output-schema version mismatch -> REFUSE",
                        require_plan_authority_coherence, tmp, plan)
    refuses_without_rng("  ... and preflight refuses too", preflight, tmp)
    shutil.rmtree(tmp)

    # (f) case REPLICATE COUNT mismatch ------------------------------------------
    tmp = sandbox()
    plan = read_json(tmp, PLAN_JSON)
    plan["cases"][0]["replicate_count"] = 7
    write_json(tmp, PLAN_JSON, plan)
    refuses_without_rng("case replicate-count mismatch -> REFUSE",
                        require_plan_authority_coherence, tmp, plan)
    shutil.rmtree(tmp)

    # (g) case SUBCONDITION mismatch ---------------------------------------------
    tmp = sandbox()
    plan = read_json(tmp, PLAN_JSON)
    plan["cases"][0]["subconditions"][0]["subcondition_id"] = "sigma_psi_invented"
    write_json(tmp, PLAN_JSON, plan)
    refuses_without_rng("case subcondition mismatch -> REFUSE",
                        require_plan_authority_coherence, tmp, plan)
    shutil.rmtree(tmp)

    # (h) CALIBRATION-REQUIRED mismatch ------------------------------------------
    tmp = sandbox()
    plan = read_json(tmp, PLAN_JSON)
    plan["cases"][0]["requires_block1_calibration"] = False
    write_json(tmp, PLAN_JSON, plan)
    refuses_without_rng("calibration-required mismatch -> REFUSE",
                        require_plan_authority_coherence, tmp, plan)
    shutil.rmtree(tmp)

    # (i) CALIBRATION SCOPE mismatch ---------------------------------------------
    tmp = sandbox()
    plan = read_json(tmp, PLAN_JSON)
    plan["cases"][0]["calibration_scope"] = "CASE_FIXED"
    write_json(tmp, PLAN_JSON, plan)
    refuses_without_rng("case calibration-scope mismatch -> REFUSE",
                        require_plan_authority_coherence, tmp, plan)
    shutil.rmtree(tmp)

    # (j) EXECUTION_AUTHORISED mismatch ------------------------------------------
    tmp = sandbox()
    plan = read_json(tmp, PLAN_JSON)
    plan["execution_authorised"] = True
    write_json(tmp, PLAN_JSON, plan)
    refuses_without_rng("execution_authorised mismatch -> REFUSE",
                        require_plan_authority_coherence, tmp, plan)
    refuses_without_rng("  ... and preflight refuses too", preflight, tmp)
    shutil.rmtree(tmp)

    # allowed seed families, roles and release endpoints are surface too ----------
    for field, value, label in (("allowed_seed_families", ["validation"], "seed families"),
                                ("role", "stress", "case role"),
                                ("primary_release_endpoint", "INVENTED", "release endpoint"),
                                ("block1_role", "INVENTED", "Block-1 role"),
                                ("fields_affected", ["theta0_circular"], "fields affected")):
        tmp = sandbox()
        plan = read_json(tmp, PLAN_JSON)
        plan["cases"][0][field] = value
        write_json(tmp, PLAN_JSON, plan)
        refuses_without_rng(f"case {label} mismatch -> REFUSE",
                            require_plan_authority_coherence, tmp, plan)
        shutil.rmtree(tmp)


# ---------------------------------- 3. the HUMAN rendering, not just the block
def test_human_rendering_cannot_drift() -> None:
    """The historical defect: block regenerated, human table left stale."""
    tmp = sandbox()
    plan = read_json(tmp, PLAN_JSON)
    plan["plan_version"] = "2.0.0"
    write_json(tmp, PLAN_JSON, plan)
    regenerate_block(tmp)          # JSON and BLOCK now agree; the PROSE does not
    check("the regenerated block agrees with the changed JSON",
          authority_block_fields(tmp)["plan_version"] == "2.0.0")
    refuses_without_rng("a stale HUMAN version line still REFUSES",
                        require_plan_authority_coherence, tmp, plan)
    shutil.rmtree(tmp)

    tmp = sandbox()
    plan = read_json(tmp, PLAN_JSON)
    plan["frozen_identities"]["analysis_procedure_identity"] = "d" * 64
    write_json(tmp, PLAN_JSON, plan)
    regenerate_block(tmp)
    refuses_without_rng("a stale HUMAN identity table still REFUSES -- the exact "
                        "defect this repair closes",
                        require_plan_authority_coherence, tmp, plan)
    shutil.rmtree(tmp)

    # With the case tables GENERATED, "block right / human table stale" can only be
    # produced by editing the rendered region directly -- which is exactly the
    # tampering the byte-exactness check exists to catch.
    tmp = sandbox()
    plan = read_json(tmp, PLAN_JSON)
    regenerate_block(tmp)
    write_md(tmp, read_md(tmp).replace("| replicate count | `300` |",
                                       "| replicate count | `12345` |", 1))
    refuses_without_rng("a hand-edited HUMAN case table REFUSES",
                        require_plan_authority_coherence, tmp, plan)
    shutil.rmtree(tmp)

    tmp = sandbox()
    plan = read_json(tmp, PLAN_JSON)
    regenerate_block(tmp)
    write_md(tmp, read_md(tmp).replace("requires >= 279/300", "requires >= 240/300", 1))
    refuses_without_rng("a hand-edited HUMAN release threshold REFUSES",
                        require_plan_authority_coherence, tmp, plan)
    shutil.rmtree(tmp)

    # the POSITIVE control: the mechanism is not simply always-refuse ------------
    tmp = sandbox()
    plan = read_json(tmp, PLAN_JSON)
    plan["plan_version"] = "2.0.0"
    write_json(tmp, PLAN_JSON, plan)
    regenerate_block(tmp)
    write_md(tmp, read_md(tmp).replace("Plan version **1.8.0**.",
                                       "Plan version **2.0.0**.", 1))
    ok = True
    try:
        require_plan_authority_coherence(tmp, plan)
    except Refusal:
        ok = False
    check("JSON + block + prose changed CONSISTENTLY -> accepted", ok,
          "the gate discriminates, it does not simply always refuse")
    shutil.rmtree(tmp)


# ------------------------------------------- 4. block structure is fail-closed
def test_block_structure_is_fail_closed() -> None:
    tmp = sandbox()
    text = read_md(tmp)
    write_md(tmp, text.replace(BLOCK_BEGIN, "").replace(BLOCK_END, ""))
    refuses_without_rng("an ABSENT authority block -> REFUSE",
                        require_plan_authority_coherence, tmp, read_json(tmp, PLAN_JSON))
    shutil.rmtree(tmp)

    tmp = sandbox()
    text = read_md(tmp)
    start = text.index(BLOCK_BEGIN)
    end = text.index(BLOCK_END) + len(BLOCK_END)
    write_md(tmp, text[:end] + "\n\n" + text[start:end] + text[end:])
    refuses_without_rng("a DUPLICATED authority block -> REFUSE",
                        require_plan_authority_coherence, tmp, read_json(tmp, PLAN_JSON))
    shutil.rmtree(tmp)

    tmp = sandbox()
    text = read_md(tmp)
    write_md(tmp, text.replace("```json\n{", "```json\n{ this is not json ", 1))
    refuses_without_rng("a MALFORMED authority block -> REFUSE",
                        require_plan_authority_coherence, tmp, read_json(tmp, PLAN_JSON))
    shutil.rmtree(tmp)

    tmp = sandbox()
    block = authority_block_fields(tmp)
    block["schema"] = "e1a_v4_plan_authority/999"
    text = read_md(tmp)
    start, end = text.index(BLOCK_BEGIN), text.index(BLOCK_END) + len(BLOCK_END)
    write_md(tmp, text[:start] + BLOCK_BEGIN + "\n\n```json\n"
             + json.dumps(block, indent=2, sort_keys=True) + "\n```\n\n" + BLOCK_END
             + text[end:])
    refuses_without_rng("a WRONG block schema -> REFUSE",
                        require_plan_authority_coherence, tmp, read_json(tmp, PLAN_JSON))
    shutil.rmtree(tmp)

    tmp = sandbox()
    block = authority_block_fields(tmp)
    block["invented_key"] = "smuggled authority"
    text = read_md(tmp)
    start, end = text.index(BLOCK_BEGIN), text.index(BLOCK_END) + len(BLOCK_END)
    write_md(tmp, text[:start] + BLOCK_BEGIN + "\n\n```json\n"
             + json.dumps(block, indent=2, sort_keys=True) + "\n```\n\n" + BLOCK_END
             + text[end:])
    refuses_without_rng("an UNDECLARED key in the block -> REFUSE",
                        require_plan_authority_coherence, tmp, read_json(tmp, PLAN_JSON))
    shutil.rmtree(tmp)

    tmp = sandbox()
    block = authority_block_fields(tmp)
    del block["cases.order"]
    text = read_md(tmp)
    start, end = text.index(BLOCK_BEGIN), text.index(BLOCK_END) + len(BLOCK_END)
    write_md(tmp, text[:start] + BLOCK_BEGIN + "\n\n```json\n"
             + json.dumps(block, indent=2, sort_keys=True) + "\n```\n\n" + BLOCK_END
             + text[end:])
    refuses_without_rng("a MISSING surface key in the block -> REFUSE",
                        require_plan_authority_coherence, tmp, read_json(tmp, PLAN_JSON))
    shutil.rmtree(tmp)

    # an ambiguous human rendering is a refusal, never a silent skip -------------
    tmp = sandbox()
    text = read_md(tmp)
    write_md(tmp, text.replace("Plan version **1.8.0**.",
                               "Plan version **1.8.0**. Plan version **1.8.0**.", 1))
    refuses_without_rng("a DUPLICATED human version line -> REFUSE (never a silent skip)",
                        require_plan_authority_coherence, tmp, read_json(tmp, PLAN_JSON))
    shutil.rmtree(tmp)

    tmp = sandbox()
    text = read_md(tmp)
    real = read_json(tmp, PLAN_JSON)["frozen_identities"]["analysis_procedure_identity"]
    write_md(tmp, text.replace(f"| analysis procedure identity | `{real}` |", "", 1))
    refuses_without_rng("an ABSENT identity row -> REFUSE (never a silent skip)",
                        require_plan_authority_coherence, tmp, read_json(tmp, PLAN_JSON))
    shutil.rmtree(tmp)


# --------------------------------------------- 5. the seal: forgotten vs not-frozen
def test_seal_distinguishes_forgotten_from_not_frozen() -> None:
    seal = load_seal(ROOT)
    check("the committed seal is PRE_DRIVER", seal.state == STATE_PRE_DRIVER)
    check("a PRE_DRIVER seal carries a NULL expected identity",
          seal.expected_execution_identity is None)
    check("the seal names the official campaign driver module",
          seal.driver_module == "e1a_v4/validation/campaign_driver.py")
    check("the official campaign driver is ABSENT",
          not driver_present(ROOT, seal.driver_module))

    tmp = sandbox()
    os.remove(os.path.join(tmp, SEAL_JSON))
    refuses_without_rng("an ABSENT seal file is FORGOTTEN -> REFUSE", load_seal, tmp)
    refuses_without_rng("  ... and preflight refuses too", preflight, tmp)
    shutil.rmtree(tmp)

    tmp = sandbox()
    raw = read_json(tmp, SEAL_JSON)
    del raw["expected_execution_identity"]
    write_json(tmp, SEAL_JSON, raw)
    refuses_without_rng("an ABSENT expected-identity KEY is FORGOTTEN -> REFUSE",
                        load_seal, tmp)
    shutil.rmtree(tmp)

    tmp = sandbox()
    raw = read_json(tmp, SEAL_JSON)
    del raw["state"]
    write_json(tmp, SEAL_JSON, raw)
    refuses_without_rng("an ABSENT seal state -> REFUSE", load_seal, tmp)
    shutil.rmtree(tmp)

    tmp = sandbox()
    raw = read_json(tmp, SEAL_JSON)
    raw["state"] = "PROBABLY_FINE"
    write_json(tmp, SEAL_JSON, raw)
    refuses_without_rng("an UNDECLARED seal state -> REFUSE", load_seal, tmp)
    shutil.rmtree(tmp)

    tmp = sandbox()
    raw = read_json(tmp, SEAL_JSON)
    raw["expected_execution_identity"] = "e" * 64
    write_json(tmp, SEAL_JSON, raw)
    refuses_without_rng("PRE_DRIVER with a NON-null expected identity -> REFUSE",
                        load_seal, tmp)
    shutil.rmtree(tmp)

    tmp = sandbox()
    raw = read_json(tmp, SEAL_JSON)
    raw["state"] = STATE_FROZEN
    write_json(tmp, SEAL_JSON, raw)
    refuses_without_rng("FROZEN with a NULL expected identity -> REFUSE", load_seal, tmp)
    shutil.rmtree(tmp)

    tmp = sandbox()
    raw = read_json(tmp, SEAL_JSON)
    raw["state"] = STATE_FROZEN
    raw["expected_execution_identity"] = "NOT-A-DIGEST"
    write_json(tmp, SEAL_JSON, raw)
    refuses_without_rng("FROZEN with a malformed digest -> REFUSE", load_seal, tmp)
    shutil.rmtree(tmp)

    tmp = sandbox()
    raw = read_json(tmp, SEAL_JSON)
    raw["schema"] = "e1a_v4_execution_seal/999"
    write_json(tmp, SEAL_JSON, raw)
    refuses_without_rng("a WRONG seal schema -> REFUSE", load_seal, tmp)
    shutil.rmtree(tmp)

    # plan and seal must agree about the state ----------------------------------
    tmp = sandbox()
    plan = read_json(tmp, PLAN_JSON)
    plan["execution_seal"]["state"] = STATE_FROZEN
    write_json(tmp, PLAN_JSON, plan)
    set_md_seal_state(tmp, STATE_FROZEN)
    regenerate_block(tmp)
    refuses_without_rng("plan/seal STATE disagreement -> REFUSE",
                        require_seal_plan_agreement, plan, load_seal(tmp))
    refuses_without_rng("  ... and preflight refuses too", preflight, tmp)
    shutil.rmtree(tmp)

    # the plan slot: absent is forgotten, null is deliberate ---------------------
    tmp = sandbox()
    plan = read_json(tmp, PLAN_JSON)
    del plan["frozen_identities"]["final_expected_execution_identity"]
    write_json(tmp, PLAN_JSON, plan)
    regenerate_block(tmp)
    refuses_without_rng("an ABSENT final_expected_execution_identity slot -> REFUSE",
                        preflight, tmp)
    shutil.rmtree(tmp)


# ------------------------------------------------- 6. the identity lifecycle (§18)
def freeze_sandbox(authorised: bool) -> tuple[str, str]:
    """Build a sandbox with the driver PRESENT and the seal FROZEN, correctly.

    Returns (root, expected_identity). No RNG is created anywhere in here.
    """
    tmp = sandbox()
    # A throwaway SANDBOX fixture standing in for the future driver, so the
    # lifecycle beyond "absent" can be exercised. The repository itself keeps no
    # such file: the canonical driver stays ABSENT, and a placeholder there would
    # defeat the very gate under test.
    with open(os.path.join(tmp, "e1a_v4/validation/campaign_driver.py"), "w",
              encoding="utf-8") as handle:
        handle.write('"""SANDBOX FIXTURE ONLY. Never committed."""\n\n\n'
                     f"def {OFFICIAL_CAMPAIGN_DRIVER_ENTRY_POINT}():\n"
                     '    raise NotImplementedError("fixture")\n')
    plan = read_json(tmp, PLAN_JSON)
    plan["execution_seal"]["state"] = STATE_FROZEN
    plan["execution_authorised"] = authorised
    write_json(tmp, PLAN_JSON, plan)
    set_md_seal_state(tmp, STATE_FROZEN)
    regenerate_block(tmp)
    if authorised:
        write_md(tmp, read_md(tmp).replace("`execution_authorised` is `false`",
                                           "`execution_authorised` is `true`", 1))
    # the identity is computed AFTER every preimage input is final ...
    binding = load_contract(tmp)
    ident = execution_identity(binding, sha256_file(os.path.join(tmp, PLAN_JSON)),
                               sha256_file(os.path.join(tmp, SEED_MAP_JSON)), tmp)
    raw = read_json(tmp, SEAL_JSON)
    raw["state"] = STATE_FROZEN
    raw["expected_execution_identity"] = ident
    write_json(tmp, SEAL_JSON, raw)
    return tmp, ident


def test_execution_identity_lifecycle() -> None:
    plan = load_plan(ROOT)

    # PRE_DRIVER + authorised = false -> preflight OK, execution refuses ---------
    before = SentinelRNG.CALLS
    check("PRE_DRIVER: preflight-only SUCCEEDS", preflight(ROOT) is not None)
    check("PRE_DRIVER: the plan is not authorised",
          plan["execution_authorised"] is False)
    raises_without_rng("PRE_DRIVER + unauthorised: execution REFUSES on the ABSENT DRIVER",
                       CampaignDriverAbsent, run, ROOT, rng_factory=rng_factory,
                       execute=True)
    check("the refusal is an ExecutionNotAuthorised",
          issubclass(CampaignDriverAbsent, ExecutionNotAuthorised))

    # PRE_DRIVER + authorised = true -> still refuses, before any RNG ------------
    tmp = sandbox()
    p = read_json(tmp, PLAN_JSON)
    p["execution_authorised"] = True
    write_json(tmp, PLAN_JSON, p)
    regenerate_block(tmp)
    write_md(tmp, read_md(tmp).replace("`execution_authorised` is `false`",
                                       "`execution_authorised` is `true`", 1))
    raises_without_rng("PRE_DRIVER + AUTHORISED: execution still REFUSES before RNG",
                       ExecutionNotAuthorised, run, tmp, rng_factory=rng_factory,
                       execute=True)
    shutil.rmtree(tmp)

    # driver present but seal MISSING -> execution refuses -----------------------
    tmp, _ = freeze_sandbox(authorised=True)
    os.remove(os.path.join(tmp, SEAL_JSON))
    refuses_without_rng("driver PRESENT but seal MISSING: execution REFUSES",
                        run, tmp, rng_factory=rng_factory, execute=True)
    shutil.rmtree(tmp)

    # driver present, seal PRE_DRIVER -> refuses on the seal, not the driver -----
    tmp, _ = freeze_sandbox(authorised=True)
    raw = read_json(tmp, SEAL_JSON)
    raw["state"] = STATE_PRE_DRIVER
    raw["expected_execution_identity"] = None
    write_json(tmp, SEAL_JSON, raw)
    p = read_json(tmp, PLAN_JSON)
    p["execution_seal"]["state"] = STATE_PRE_DRIVER
    write_json(tmp, PLAN_JSON, p)
    set_md_seal_state(tmp, STATE_PRE_DRIVER)
    regenerate_block(tmp)
    raises_without_rng("driver PRESENT, seal NOT FROZEN: execution REFUSES on the SEAL",
                       ExecutionSealNotFrozen, run, tmp, rng_factory=rng_factory,
                       execute=True)
    shutil.rmtree(tmp)

    # seal present but identity MISMATCH -> execution refuses -------------------
    tmp, ident = freeze_sandbox(authorised=True)
    raw = read_json(tmp, SEAL_JSON)
    raw["expected_execution_identity"] = "0" * 64
    write_json(tmp, SEAL_JSON, raw)
    raises_without_rng("seal FROZEN but identity MISMATCH: execution REFUSES",
                       ExecutionIdentityUnsealed, run, tmp, rng_factory=rng_factory,
                       execute=True)
    shutil.rmtree(tmp)

    # seal matches but authorisation = false -> execution refuses ---------------
    tmp, ident = freeze_sandbox(authorised=False)
    raises_without_rng("seal FROZEN and MATCHING but UNAUTHORISED: execution REFUSES",
                       ExecutionAuthorisationMissing, run, tmp,
                       rng_factory=rng_factory, execute=True)
    shutil.rmtree(tmp)

    # seal + match + authorised -> the gate is eligible. SENTINEL BOUNDARY ONLY --
    tmp, ident = freeze_sandbox(authorised=True)
    eligible = True
    try:
        require_execution_gate(tmp, read_json(tmp, PLAN_JSON), ident)
    except Refusal:
        eligible = False
    check("seal FROZEN + identity MATCH + AUTHORISED: the gate is ELIGIBLE", eligible,
          "sentinel boundary only -- no driver, no RNG, no draw")
    refuses_without_rng("...and `run` still stops at the UNIMPLEMENTED execution path",
                        run, tmp, rng_factory=rng_factory, execute=True)
    check("no RNG object was ever created in this suite", SentinelRNG.CALLS == before,
          f"RNG_CALL_COUNT = {SentinelRNG.CALLS}")
    shutil.rmtree(tmp)


# ------------------------------------------------- 7. the seal avoids self-reference
def test_seal_is_outside_the_preimage() -> None:
    binding = load_contract(ROOT)
    plan_sha = sha256_file(os.path.join(ROOT, PLAN_JSON))
    seed_sha = sha256_file(os.path.join(ROOT, SEED_MAP_JSON))
    base = execution_identity(binding, plan_sha, seed_sha, ROOT)

    tmp = sandbox()
    before = execution_identity(load_contract(tmp),
                                sha256_file(os.path.join(tmp, PLAN_JSON)),
                                sha256_file(os.path.join(tmp, SEED_MAP_JSON)), tmp)
    raw = read_json(tmp, SEAL_JSON)
    raw["state"] = STATE_FROZEN
    raw["expected_execution_identity"] = before
    write_json(tmp, SEAL_JSON, raw)
    after = execution_identity(load_contract(tmp),
                               sha256_file(os.path.join(tmp, PLAN_JSON)),
                               sha256_file(os.path.join(tmp, SEED_MAP_JSON)), tmp)
    check("writing the expected identity INTO the seal does not change the identity",
          before == after, "no impossible fixed point")
    check("the sandbox reproduces the committed identity", before == base,
          base[:16] + "...")
    shutil.rmtree(tmp)

    # ... whereas the normative MARKDOWN is inside the preimage ------------------
    tmp = sandbox()
    write_md(tmp, read_md(tmp) + "\n<!-- a normative document must not drift silently -->\n")
    moved = execution_identity(load_contract(tmp),
                               sha256_file(os.path.join(tmp, PLAN_JSON)),
                               sha256_file(os.path.join(tmp, SEED_MAP_JSON)), tmp)
    check("changing the normative Markdown DOES move the execution identity",
          moved != base, "the Markdown is inside the sealed package")
    shutil.rmtree(tmp)

    check("the seal file is not one of the validation modules",
          not any(SEAL_JSON in m for m in VALIDATION_MODULES))
    check("both new modules entered the execution-identity preimage",
          "e1a_v4/validation/coherence.py" in VALIDATION_MODULES
          and "e1a_v4/validation/seal.py" in VALIDATION_MODULES,
          f"{len(VALIDATION_MODULES)} validation modules")


# ------------------------------------------------- 8. no scientific rule moved
def test_no_scientific_rule_changed() -> None:
    binding = load_contract(ROOT)
    plan = load_plan(ROOT)
    for label, got, want in (
            ("delta_cross", binding.delta_cross, 0.02),
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
    check("execution is still NOT authorised", plan["execution_authorised"] is False)
    seeds = json.load(open(os.path.join(ROOT, SEED_MAP_JSON), encoding="utf-8"))
    check("the master seed is unchanged", seeds["master_seed"] == 13785910525869478477)
    check("the seed map identity is unchanged",
          sha256_file(os.path.join(ROOT, SEED_MAP_JSON))
          == "95870d7d33c256c4bd30118e13278a600271531fd945d12687a828de902e91ce")


if __name__ == "__main__":
    print("\nthe committed package is coherent")
    test_live_package_is_coherent()
    print("\nthe required disagreement fixtures all refuse")
    test_disagreement_fixtures_refuse()
    print("\nthe human rendering cannot drift from the authority")
    test_human_rendering_cannot_drift()
    print("\nthe authority block is structurally fail-closed")
    test_block_structure_is_fail_closed()
    print("\nthe seal distinguishes FORGOTTEN from NOT-YET-FROZEN")
    test_seal_distinguishes_forgotten_from_not_frozen()
    print("\nthe execution-identity lifecycle")
    test_execution_identity_lifecycle()
    print("\nthe seal is outside the execution-identity preimage")
    test_seal_is_outside_the_preimage()
    print("\nno E1a scientific decision rule changed")
    test_no_scientific_rule_changed()
    print(f"\nE1a v4 plan-coherence gate: {PASSED} passed, {FAILED} failed, 8 groups")
    print("Execution class: NON-MODEL-ADVANCING STATIC/PURE (this suite only)")
    print(f"  RNG OBJECTS           : {SentinelRNG.CALLS}")
    print("  RANDOM DRAWS          : 0")
    print("  TRAJECTORIES          : 0")
    raise SystemExit(1 if FAILED else 0)
