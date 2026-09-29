"""E1a v4 GENERATING-MODEL coherence, section coverage and seal ordering.

**EXECUTION CLASS: NON-MODEL-ADVANCING STATIC/PURE.** Text, JSON, hashing and
arithmetic only. A sentinel RNG provider counts every call and every refusal path
asserts RNG_CALL_COUNT == 0. No random number is drawn, no trajectory generated,
no calibration sampled, no scientific outcome inspected.

WHAT THIS SUITE EXISTS FOR
    `generating_model` was classified JSON_ONLY with a single subtree-level
    shortcut, although section 4 visibly renders its scientific settings. Every
    descendant was therefore outside the checked surface. Reproduced at addd704:

        visible n_samples  2000000 -> 2000001      ACCEPTED
        visible dt         0.00012 -> 0.00013      ACCEPTED
        visible theta1_power k [210,210] -> [200,200]   ACCEPTED

    plus six more Markdown-only probes, six JSON-only probes, and a plan that
    contradicted the FROZEN DESIGN CONTRACT about a field's stiffness. All
    ACCEPTED.

    The auditor named three. Hand-patching three would have left the class open,
    so the mutation audit below is GENERATED from the specification: every
    primitive classified BOTH under the generating-model surface is mutated on the
    Markdown side and on the JSON side, and both must refuse.
"""

from __future__ import annotations

import copy
import json
import os
import re
import shutil
import tempfile

from e1a_v4.contract import load_contract, sha256_file
from e1a_v4.numerics import Refusal
from e1a_v4.validation import PLAN_JSON, PLAN_MARKDOWN, SEED_MAP_JSON
from e1a_v4.validation.classification import size_boundary
from e1a_v4.validation.coherence import (
    BLOCK_BEGIN, BLOCK_END, BOTH, CONTRACT_MIRRORED_FIELD_KEYS, DERIVED,
    DERIVED_SECTION, GENERATED, GENERATING_MODEL_SPEC, NON_NORMATIVE, PARSED,
    REGION_ANCHORS, SECTION_REGISTRY, TOP_LEVEL_SPEC, canonical_generating_model,
    canonical_generating_model_from_markdown, derived_n_samples, markdown_sections,
    normative_json_view, normative_markdown_view, render_authority_block,
    render_region, require_derived_boundaries, require_generating_model_coherence,
    require_plan_authority_coherence, require_section_registry_totality,
    specification_counts,
)
from e1a_v4.validation.dispositions import cp_lower
from e1a_v4.validation.plan import execution_identity, load_plan
from e1a_v4.validation.runner import preflight, run
from e1a_v4.validation.seal import (
    SEAL_JSON, STATE_FROZEN, STATE_PRE_DRIVER, load_seal, seal_exists,
)
from e1a_v4.validation.driver import OFFICIAL_CAMPAIGN_DRIVER_ENTRY_POINT, OFFICIAL_CAMPAIGN_DRIVER_PATH
from e1a_v4.validation.strict_json import strict_load_file

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
    plan = rj(tmp, PLAN_JSON)
    text = rmd(tmp)
    for name, (begin, end) in REGION_ANCHORS.items():
        a = text.index(begin)
        z = text.index(end) + len(end)
        text = text[:a] + f"{begin}\n\n{render_region(name, plan).rstrip()}\n\n{end}" + text[z:]
    a = text.index(BLOCK_BEGIN)
    z = text.index(BLOCK_END) + len(BLOCK_END)
    wmd(tmp, text[:a] + render_authority_block(plan, tmp) + text[z:])


# ------------------------------------------- 1. section 4 is now in the surface
def test_generating_model_is_in_the_surface() -> None:
    plan = load_plan(ROOT)
    origin, reason = TOP_LEVEL_SPEC["generating_model"]
    check("generating_model is no longer JSON_ONLY", origin == BOTH, origin)
    check("its classification states why", "section 4" in reason)
    check("every descendant primitive is classified individually",
          all(o in (BOTH, DERIVED) for o, _ in GENERATING_MODEL_SPEC.values()),
          f"{len(GENERATING_MODEL_SPEC)} primitives")
    check("every descendant classification carries a reason",
          all(r.strip() for _, r in GENERATING_MODEL_SPEC.values()))

    view = normative_json_view(plan, ROOT)
    for key in ("generating_model.branch_b.dt_s", "generating_model.branch_b.T_total_s",
                "generating_model.branch_b.n_samples",
                "generating_model.per_field.theta1_power.k_uN_per_m",
                "generating_model.per_field.theta3_temperature.T_K",
                "generating_model.per_field.theta2_ellipse.rot_deg",
                "generating_model.per_field.theta0_circular.reference",
                "generating_model.per_field.theta1_power.beta_true",
                "generating_model.branch_b.initialisation",
                "generating_model.truth_visibility"):
        check(f"surface now covers {key}", key in view)

    # every declared field, every physical parameter
    for field in plan["generating_model"]["per_field"]:
        for key in ("k_uN_per_m", "T_K", "rot_deg", "reference", "beta_true", "tau_rule"):
            check(f"{field['id']}.{key} is covered",
                  f"generating_model.per_field.{field['id']}.{key}" in view)

    # a subtree shortcut can no longer hide a descendant
    tmp = sandbox()
    p = rj(tmp, PLAN_JSON)
    p["generating_model"]["branch_b"]["an_undeclared_setting"] = 1
    refuses_with_code("an undeclared generating-model setting",
                      "PLAN_SURFACE_UNDECLARED", canonical_generating_model, p)
    p = rj(tmp, PLAN_JSON)
    p["generating_model"]["per_field"][0]["an_undeclared_parameter"] = 1
    refuses_with_code("an undeclared per-field parameter",
                      "PLAN_SURFACE_UNDECLARED", canonical_generating_model, p)
    p = rj(tmp, PLAN_JSON)
    p["generating_model"]["an_undeclared_section"] = {}
    refuses_with_code("an undeclared generating-model section",
                      "PLAN_SURFACE_UNDECLARED", canonical_generating_model, p)
    shutil.rmtree(tmp)


# ----------------------------------------- 2. the auditor's three named probes
def test_named_regression_probes() -> None:
    """The exact probes the auditor demonstrated, on both sides."""
    for label, old, new in (
            ("visible n_samples 2000000 -> 2000001",
             "| n_samples *(derived: T_total / dt)* | `2000000` |",
             "| n_samples *(derived: T_total / dt)* | `2000001` |"),
            ("visible dt 0.00012 -> 0.00013", "| dt | `0.00012` |", "| dt | `0.00013` |"),
            ("visible theta1_power k [210,210] -> [200,200]",
             "| `theta1_power` | `[210, 210]` |", "| `theta1_power` | `[200, 200]` |")):
        tmp = sandbox()
        text = rmd(tmp)
        assert text.count(old) == 1, label
        wmd(tmp, text.replace(old, new, 1))
        # the generating-model check runs before the byte-exactness check, so the
        # reported code is the MORE specific one
        refuses_with_code(label, "PLAN_GENERATING_MODEL_MISMATCH", preflight, tmp)
        shutil.rmtree(tmp)

    for label, mutate in (
            ("JSON n_samples 2000000 -> 2000001",
             lambda p: p["generating_model"]["branch_b"].__setitem__("n_samples", 2000001)),
            ("JSON dt_s 0.00012 -> 0.00013",
             lambda p: p["generating_model"]["branch_b"].__setitem__("dt_s", 0.00013)),
            ("JSON theta1_power k [210,210] -> [200,200]",
             lambda p: p["generating_model"]["per_field"][1].__setitem__(
                 "k_uN_per_m", [200, 200]))):
        tmp = sandbox()
        p = rj(tmp, PLAN_JSON)
        mutate(p)
        wj(tmp, PLAN_JSON, p)
        regenerate(tmp)          # the JSON change IS propagated; it must still refuse
        refused = None
        try:
            preflight(tmp)
        except Refusal as exc:
            refused = getattr(type(exc), "code", "UNCODED")
        check(f"{label} -> refuses even fully propagated", refused is not None,
              f"code {refused}")
        shutil.rmtree(tmp)


# ------------------------------- 3. AUTOMATIC mutation of EVERY BOTH primitive
def _mutate(value):
    """A deterministic, type-appropriate, still-well-formed mutation."""
    if isinstance(value, bool):
        return not value
    if isinstance(value, int):
        return value + 1
    if isinstance(value, float):
        return value + 1.0 if value == 0.0 else value * 2.0
    if isinstance(value, str):
        return value + " MUTATED"
    if isinstance(value, list) and value:
        head = copy.deepcopy(value)
        head[0] = _mutate(head[0])
        return head
    raise AssertionError(f"no declared mutation for {value!r}")


def test_every_generating_primitive_is_checked() -> None:
    """Enumerated from the specification, not hand-picked.

    For each primitive classified BOTH: mutate the JSON alone, require refusal;
    restore; mutate the Markdown alone, require refusal. Mutations stay
    well-formed, so what is proven is SEMANTIC mismatch detection, never
    malformed-input rejection.
    """
    plan = load_plan(ROOT)
    canonical = canonical_generating_model(plan)
    derived_paths = {k for k, (o, _) in GENERATING_MODEL_SPEC.items() if o == DERIVED}

    targets = []
    for path, value in canonical.items():
        if path == "per_field.order":
            continue
        spec_key = path
        if path.startswith("per_field."):
            spec_key = "per_field." + path.rsplit(".", 1)[1]
        if spec_key in derived_paths:
            continue
        targets.append((path, spec_key, value))
    check("the mutation audit is enumerated from the specification",
          len(targets) > 0, f"{len(targets)} BOTH primitives under generating_model")

    json_refused = md_refused = 0
    for path, spec_key, value in targets:
        # ---- JSON side ----------------------------------------------------
        tmp = sandbox()
        p = rj(tmp, PLAN_JSON)
        gm = p["generating_model"]
        if path.startswith("per_field."):
            _, fid, key = path.split(".", 2)
            field = next(f for f in gm["per_field"] if f["id"] == fid)
            field[key] = _mutate(field[key])
        elif path == "truth_visibility":
            gm["truth_visibility"] = _mutate(gm["truth_visibility"])
        else:
            section, key = path.split(".", 1)
            gm[section][key] = _mutate(gm[section][key])
        assert canonical_generating_model(p)[path] == _mutate(value), path
        wj(tmp, PLAN_JSON, p)
        refused = False
        try:
            require_plan_authority_coherence(tmp, rj(tmp, PLAN_JSON))
        except Refusal:
            refused = True
        json_refused += refused
        if not refused:
            check(f"JSON-only mutation of {path} REFUSES", False)
        shutil.rmtree(tmp)

        # ---- Markdown side ------------------------------------------------
        tmp = sandbox()
        text = rmd(tmp)
        altered = copy.deepcopy(plan)
        gm = altered["generating_model"]
        if path.startswith("per_field."):
            _, fid, key = path.split(".", 2)
            field = next(f for f in gm["per_field"] if f["id"] == fid)
            field[key] = _mutate(field[key])
        elif path == "truth_visibility":
            gm["truth_visibility"] = _mutate(gm["truth_visibility"])
        else:
            section, key = path.split(".", 1)
            gm[section][key] = _mutate(gm[section][key])
        begin, end = REGION_ANCHORS["generating_model"]
        a = text.index(begin) + len(begin)
        z = text.index(end)
        region = render_region("generating_model", altered)
        assert canonical_generating_model_from_markdown(region, altered)[path] == _mutate(value), path
        assert canonical_generating_model_from_markdown(region, altered)[path] != value, path
        wmd(tmp, text[:a] + "\n\n" + region.rstrip() + "\n\n" + text[z:])
        refused = False
        try:
            require_plan_authority_coherence(tmp, rj(tmp, PLAN_JSON))
        except Refusal:
            refused = True
        md_refused += refused
        if not refused:
            check(f"Markdown-only mutation of {path} REFUSES", False)
        shutil.rmtree(tmp)

    check("EVERY generating-model primitive refuses a JSON-only mutation",
          json_refused == len(targets), f"{json_refused}/{len(targets)}")
    check("EVERY generating-model primitive refuses a Markdown-only mutation",
          md_refused == len(targets), f"{md_refused}/{len(targets)}")


# ---------------------------------------------- 4. primitive versus derived
def test_derived_values_are_recomputed() -> None:
    plan = load_plan(ROOT)
    branch_b = plan["generating_model"]["branch_b"]
    check("n_samples is classified DERIVED, not an independent input",
          GENERATING_MODEL_SPEC["branch_b.n_samples"][0] == DERIVED)
    check("n_samples equals int(round(T_total / dt))",
          branch_b["n_samples"] == derived_n_samples(branch_b),
          f"{branch_b['T_total_s']} / {branch_b['dt_s']} = {derived_n_samples(branch_b)}")
    check("dt and T_total are the PRIMITIVES",
          GENERATING_MODEL_SPEC["branch_b.dt_s"][0] == BOTH
          and GENERATING_MODEL_SPEC["branch_b.T_total_s"][0] == BOTH)

    tmp = sandbox()
    p = rj(tmp, PLAN_JSON)
    p["generating_model"]["branch_b"]["n_samples"] = 1999999
    wj(tmp, PLAN_JSON, p)
    regenerate(tmp)
    refuses_with_code("a derived n_samples that contradicts its primitives",
                      "PLAN_DERIVED_VALUE_MISMATCH", preflight, tmp)
    shutil.rmtree(tmp)

    # the section-12a boundaries are derived too
    for case_id, row in plan["size_validation_semantics"]["derived_boundaries"].items():
        check(f"{case_id} boundary recomputes exactly",
              row["boundary"] == size_boundary(row["replicates"], row["nominal_alpha"]),
              f"R={row['replicates']} alpha={row['nominal_alpha']} -> {row['boundary']}")
        check(f"{case_id} CP_lower at the boundary recomputes",
              abs(row["cp_lower_at_boundary"]
                  - cp_lower(row["boundary"], row["replicates"])) <= 1e-12)
    tmp = sandbox()
    p = rj(tmp, PLAN_JSON)
    p["size_validation_semantics"]["derived_boundaries"]["C2"]["boundary"] = 9
    wj(tmp, PLAN_JSON, p)
    regenerate(tmp)
    refuses_with_code("a derived size boundary that contradicts its recomputation",
                      "PLAN_DERIVED_VALUE_MISMATCH", preflight, tmp)
    shutil.rmtree(tmp)


# ------------------------------------ 5. the plan may not outrank the contract
def test_plan_cannot_contradict_the_contract() -> None:
    plan = load_plan(ROOT)
    contract = strict_load_file(
        os.path.join(ROOT, "docs/e1a/e1a_v4_design_contract.json"), "contract")
    by_id = {f["id"]: f for f in contract["fields"]}
    for field in plan["generating_model"]["per_field"]:
        check(f"{field['id']} matches the frozen contract",
              all(field[k] == by_id[field["id"]][k] for k in CONTRACT_MIRRORED_FIELD_KEYS))
    scenario = contract["hypothetical_uncertainty_scenario"]
    check("dt matches the frozen contract",
          plan["generating_model"]["branch_b"]["dt_s"] == scenario["dt_s"])
    check("T_total matches the frozen contract",
          plan["generating_model"]["branch_b"]["T_total_s"] == scenario["T_total_s"])

    for label, mutate in (
            ("stiffness", lambda p: p["generating_model"]["per_field"][1].__setitem__(
                "k_uN_per_m", [999, 999])),
            ("temperature", lambda p: p["generating_model"]["per_field"][3].__setitem__(
                "T_K", 999)),
            ("orientation", lambda p: p["generating_model"]["per_field"][2].__setitem__(
                "rot_deg", 99)),
            ("reference flag", lambda p: p["generating_model"]["per_field"][0].__setitem__(
                "reference", False)),
            ("dt", lambda p: p["generating_model"]["branch_b"].__setitem__("dt_s", 0.00013)),
            ("T_total", lambda p: p["generating_model"]["branch_b"].__setitem__(
                "T_total_s", 480.0))):
        tmp = sandbox()
        p = rj(tmp, PLAN_JSON)
        mutate(p)
        if label == "T_total":
            p["generating_model"]["branch_b"]["n_samples"] = 4000000
        if label == "dt":
            p["generating_model"]["branch_b"]["n_samples"] = derived_n_samples(
                p["generating_model"]["branch_b"])
        wj(tmp, PLAN_JSON, p)
        regenerate(tmp)
        expected = ("CONTRACT_REFERENCE_FIELD_MISMATCH" if label == "reference flag"
                    else "CONTRACT_GENERATING_PARAMETER_MISMATCH")
        refuses_with_code(f"a plan contradicting the CONTRACT on {label}",
                          expected, preflight, tmp)
        shutil.rmtree(tmp)


# --------------------------------------- 6. whole-document section coverage
def test_section_registry_covers_the_document() -> None:
    text = open(os.path.join(ROOT, PLAN_MARKDOWN), encoding="utf-8").read()
    require_section_registry_totality(text)
    present = markdown_sections(text)
    check("every document section is registered",
          all(h in SECTION_REGISTRY for h in present), f"{len(present)} sections")
    check("every registry entry exists in the document",
          all(h in present for h in SECTION_REGISTRY), f"{len(SECTION_REGISTRY)} entries")
    check("every registry entry has a classification and a reason",
          all(o in (GENERATED, PARSED, DERIVED_SECTION, NON_NORMATIVE) and r.strip()
              for o, r in SECTION_REGISTRY.values()))
    counts = specification_counts(load_plan(ROOT), ROOT)
    check("unclassified normative candidates is zero",
          counts["unclassified_normative_candidates"] == 0)
    check("section 4 is GENERATED", SECTION_REGISTRY["4. Generating model"][0] == GENERATED)
    check("section 8 is GENERATED", SECTION_REGISTRY["8. Controls"][0] == GENERATED)
    check("section 12a is DERIVED",
          SECTION_REGISTRY["12a. Size-validation semantics — FROZEN PROSPECTIVELY"][0]
          == DERIVED_SECTION)

    tmp = sandbox()
    wmd(tmp, rmd(tmp) + "\n\n## 20. An unregistered normative section\n\nreplicate count 999\n")
    refuses_with_code("a NEW unregistered section", "PLAN_SECTION_UNREGISTERED",
                      preflight, tmp)
    shutil.rmtree(tmp)

    tmp = sandbox()
    wmd(tmp, rmd(tmp).replace("## 15. Parallelism policy",
                              "## 15. Parallelism policy RENAMED", 1))
    refuses_with_code("a RENAMED section", "PLAN_SECTION_UNREGISTERED", preflight, tmp)
    shutil.rmtree(tmp)

    tmp = sandbox()
    wmd(tmp, rmd(tmp) + "\n\n## 15. Parallelism policy\n\nduplicate heading\n")
    refuses_with_code("a DUPLICATED section heading", "PLAN_AMBIGUOUS_BLOCK",
                      preflight, tmp)
    shutil.rmtree(tmp)


# ----------------------------------------------- 7. the seal ordering repair
def install_driver_fixture(tmp: str) -> None:
    """A throwaway SANDBOX driver. Never created in the repository."""
    with open(os.path.join(tmp, OFFICIAL_CAMPAIGN_DRIVER_PATH), "w",
              encoding="utf-8") as handle:
        handle.write('"""SANDBOX FIXTURE ONLY. Never committed."""\n\n\n'
                     f"def {OFFICIAL_CAMPAIGN_DRIVER_ENTRY_POINT}():\n"
                     "    raise NotImplementedError\n")


def test_seal_ordering() -> None:
    before = SentinelRNG.CALLS
    check("the canonical driver is PRESENT in the repository",
          os.path.exists(os.path.join(ROOT, OFFICIAL_CAMPAIGN_DRIVER_PATH)))
    check("the seal file DOES exist", seal_exists(ROOT))

    # The declared order is driver -> seal -> identity -> authorisation. The driver
    # is now implemented, so the LIVE package stops at the seal; the ordering
    # guarantee is unchanged and is tested below with the driver removed.
    refuses_with_code("with the driver present, execution refuses on the SEAL",
                      "EXECUTION_SEAL_NOT_FROZEN", run, ROOT,
                      rng_factory=rng_factory, execute=True)

    tmp = sandbox()
    os.remove(os.path.join(tmp, OFFICIAL_CAMPAIGN_DRIVER_PATH))
    refuses_with_code("with the driver absent, execution refuses on the DRIVER",
                      "DRIVER_ABSENT", run, tmp, rng_factory=rng_factory, execute=True)
    shutil.rmtree(tmp)

    # ... and it still refuses on the DRIVER even with NO seal at all
    tmp = sandbox()
    os.remove(os.path.join(tmp, OFFICIAL_CAMPAIGN_DRIVER_PATH))
    os.remove(os.path.join(tmp, SEAL_JSON))
    refuses_with_code("driver absent AND seal absent: the DRIVER is reported first",
                      "DRIVER_ABSENT", run, tmp, rng_factory=rng_factory, execute=True)
    shutil.rmtree(tmp)

    tmp = sandbox()
    os.remove(os.path.join(tmp, OFFICIAL_CAMPAIGN_DRIVER_PATH))
    with open(os.path.join(tmp, SEAL_JSON), "w", encoding="utf-8") as handle:
        handle.write("{ not json ")
    refuses_with_code("driver absent AND seal malformed: the DRIVER is still first",
                      "DRIVER_ABSENT", run, tmp, rng_factory=rng_factory, execute=True)
    shutil.rmtree(tmp)

    # once a driver exists, the seal distinctions become visible
    tmp = sandbox()
    install_driver_fixture(tmp)
    os.remove(os.path.join(tmp, SEAL_JSON))
    refuses_with_code("driver present, seal file ABSENT", "EXECUTION_SEAL_NOT_FROZEN",
                      run, tmp, rng_factory=rng_factory, execute=True)
    shutil.rmtree(tmp)

    tmp = sandbox()
    install_driver_fixture(tmp)
    with open(os.path.join(tmp, SEAL_JSON), "w", encoding="utf-8") as handle:
        handle.write("{ not json ")
    refuses_with_code("driver present, seal exists but MALFORMED",
                      "EXECUTION_SEAL_MALFORMED", run, tmp, rng_factory=rng_factory,
                      execute=True)
    shutil.rmtree(tmp)

    tmp = sandbox()
    install_driver_fixture(tmp)
    refuses_with_code("driver present, seal valid but PRE_DRIVER",
                      "EXECUTION_SEAL_NOT_FROZEN", run, tmp, rng_factory=rng_factory,
                      execute=True)
    shutil.rmtree(tmp)

    tmp = sandbox()
    install_driver_fixture(tmp)
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
    raw = rj(tmp, SEAL_JSON)
    raw["state"] = STATE_FROZEN
    raw["expected_execution_identity"] = "0" * 64
    wj(tmp, SEAL_JSON, raw)
    refuses_with_code("driver present, seal FROZEN but identity differs",
                      "EXECUTION_IDENTITY_MISMATCH", run, tmp, rng_factory=rng_factory,
                      execute=True)
    shutil.rmtree(tmp)
    check("no RNG object was created anywhere in the ordering audit",
          SentinelRNG.CALLS == before, f"RNG_CALL_COUNT = {SentinelRNG.CALLS}")


# --------------------------------------------- 8. no scientific rule changed
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
    check("primary sigma_psi is still 0.5 deg",
          binding.data["hypothetical_uncertainty_scenario"]["sigma_psi_deg"] == 0.5)
    check("contract identity unchanged",
          binding.sha256 == "91d6ae76ccb6fdbeb7f926722433c574c30b7c0b6105c7c1ec20436fa2ec431b")
    check("foundation identity unchanged",
          binding.foundation_sha256
          == "6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507")
    check("the analysis identity is unchanged",
          plan["frozen_identities"]["analysis_procedure_identity"]
          == "dd2ed732db4348b0b25ce5fe83096d38f5b9c1748ee5916eecaf2c1aef2e2e1f")
    check("the seed map identity is unchanged",
          sha256_file(os.path.join(ROOT, SEED_MAP_JSON))
          == "95870d7d33c256c4bd30118e13278a600271531fd945d12687a828de902e91ce")
    check("the generating model itself is unchanged",
          plan["generating_model"]["branch_b"]["dt_s"] == 0.00012
          and plan["generating_model"]["branch_b"]["T_total_s"] == 240.0
          and plan["generating_model"]["branch_b"]["n_samples"] == 2000000)
    check("every field's physical parameters are unchanged",
          [(f["id"], f["k_uN_per_m"], f["T_K"], f["rot_deg"])
           for f in plan["generating_model"]["per_field"]]
          == [("theta0_circular", [100, 100], 298, 0),
              ("theta1_power", [210, 210], 298, 0),
              ("theta2_ellipse", [150, 60], 298, 30),
              ("theta3_temperature", [100, 100], 318, 0)])
    check("G1/G2/C2/C3/C4 boundaries unchanged",
          [plan["size_validation_semantics"]["derived_boundaries"][c]["boundary"]
           for c in ("C2", "C3", "C4")] == [5, 2, 13])
    check("execution is still NOT authorised", plan["execution_authorised"] is False)


if __name__ == "__main__":
    print("\nsection 4 is inside the normative surface")
    test_generating_model_is_in_the_surface()
    print("\nthe auditor's three named probes, both sides")
    test_named_regression_probes()
    print("\nAUTOMATIC mutation of every generating-model primitive")
    test_every_generating_primitive_is_checked()
    print("\nprimitive versus derived")
    test_derived_values_are_recomputed()
    print("\nthe plan may not contradict the frozen contract")
    test_plan_cannot_contradict_the_contract()
    print("\nwhole-document normative section coverage")
    test_section_registry_covers_the_document()
    print("\nexecution-gate ordering")
    test_seal_ordering()
    print("\nno E1a scientific decision rule changed")
    test_no_scientific_rule_changed()
    print(f"\nE1a v4 generating-model gate: {PASSED} passed, {FAILED} failed, 8 groups")
    print("Execution class: NON-MODEL-ADVANCING STATIC/PURE (this suite only)")
    print(f"  RNG OBJECTS           : {SentinelRNG.CALLS}")
    print("  RANDOM DRAWS          : 0")
    print("  TRAJECTORIES          : 0")
    raise SystemExit(1 if FAILED else 0)
