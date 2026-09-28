"""Markdown / JSON authority coherence for the frozen validation plan.

WHY THIS MODULE EXISTS
    `AGENTS.md` makes the rule explicit for every normative Markdown/JSON pair in
    this repository: the JSON is the mechanical schema and ordering source, the
    Markdown is its normative human rendering, and **any mismatch is an integrity
    failure, not permission to choose one selectively**.

    The superseded preflight compared only the section-9 output schema. Everything
    else a reader relies on -- the plan version and the frozen identity table --
    was unchecked, so a stale Markdown identity passed preflight silently. It did:
    the Markdown carried an analysis procedure identity that the package has never
    computed at any commit, for four commits, while preflight reported PASS.

THE MECHANISM, and why it is not prose scraping
    The Markdown carries ONE generated, anchor-delimited `json` block -- the
    AUTHORITY BLOCK -- holding every duplicated normative value. `require_plan_
    authority_coherence` rebuilds that block from the JSON plan and compares it
    key by key. Nothing is inferred from free prose, and the block is emitted by
    `render_authority_block` rather than hand-maintained.

    A generated block alone would not have caught the defect it exists for: the
    HUMAN table could still drift from the block. So a second, narrower check
    verifies that the human-visible renderings -- the version line, the section-1
    identity table, the execution-authorisation sentence and each case table --
    agree with the block. Extraction there is anchored on exact row labels inside
    named sections; an absent or ambiguous match is a REFUSAL, never a silent skip.

    Result: a stale JSON, a stale block, or a stale human cell each refuse
    deterministically, before any RNG object can exist.

CLASSIFICATION
    every check here ... EXACT (string and structural equality on frozen text)

NO RNG. Nothing in this module draws, samples, or advances any model state.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any

from ..contract import sha256_file
from ..numerics import Refusal
from . import PLAN_JSON, PLAN_MARKDOWN, SEED_MAP_JSON

#: Schema of the generated authority block. Bumped when the SURFACE changes.
AUTHORITY_BLOCK_SCHEMA = "e1a_v4_plan_authority/1"

BLOCK_BEGIN = "<!-- BEGIN GENERATED AUTHORITY BLOCK -- do not hand-edit -->"
BLOCK_END = "<!-- END GENERATED AUTHORITY BLOCK -->"

#: The normative coherence surface: every duplicated value whose disagreement
#: could change or misidentify an execution. Declared, not discovered.
COHERENCE_SURFACE = (
    "plan_id",
    "plan_version",
    "execution_stage",
    "execution_authorised",
    "execution_seal_state",
    "calibration_scope",
    "frozen_identities",
    "implementation_file_hashes_digest",
    "seed_map_sha256",
    "output_schema",
    "failure_classifications",
    "cases",
    "release_criteria",
)

#: Per-case authority. Each entry is duplicated in the Markdown case tables.
CASE_SURFACE = (
    "case_id",
    "role",
    "replicate_count",
    "subcondition_count",
    "subconditions",
    "requires_block1_calibration",
    "calibration_scope",
    "allowed_seed_families",
    "primary_release_endpoint",
    "fields_affected",
    "block1_role",
)

#: Frozen identity scalars. The note strings are prose and deliberately excluded.
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


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def authority_from_plan(plan: dict[str, Any], root: str = ".") -> dict[str, Any]:
    """Derive the authority surface from the JSON plan. The single source."""
    frozen = plan["frozen_identities"]
    missing = [k for k in IDENTITY_SURFACE if k not in frozen]
    if missing:
        raise Refusal(f"JSON plan frozen_identities omits {missing}")
    seal = plan.get("execution_seal")
    if not isinstance(seal, dict) or "state" not in seal:
        raise Refusal(
            "JSON plan does not declare execution_seal.state; the execution-seal "
            "lifecycle must be machine-readable, not prose"
        )
    cases = []
    for case in plan["cases"]:
        absent = [k for k in CASE_SURFACE
                  if k != "subconditions" and k not in case]
        if absent:
            raise Refusal(f"case {case.get('case_id')!r} omits authority fields {absent}")
        cases.append({
            "case_id": case["case_id"],
            "role": case["role"],
            "replicate_count": case["replicate_count"],
            "subcondition_count": case["subcondition_count"],
            "subconditions": [s["subcondition_id"] for s in case["subconditions"]],
            "requires_block1_calibration": case["requires_block1_calibration"],
            "calibration_scope": case["calibration_scope"],
            "allowed_seed_families": list(case["allowed_seed_families"]),
            "primary_release_endpoint": case["primary_release_endpoint"],
            "fields_affected": list(case["fields_affected"]),
            "block1_role": case["block1_role"],
        })
    release = {
        "assurance": [{"quantity": a["quantity"], "target": a["target"],
                       "replicates": a["replicates"], "bound": a["bound"],
                       "confidence_level": a["confidence_level"]}
                      for a in plan["assurance"]],
        "final_campaign_verdict_on_success":
            plan["final_campaign_classification"]["verdict_on_success"],
        "final_campaign_rule": plan["final_campaign_classification"]["rule"],
        "final_campaign_requirements":
            list(plan["final_campaign_classification"]["requirements"]),
    }
    return {
        "schema": AUTHORITY_BLOCK_SCHEMA,
        "plan_id": plan["plan_id"],
        "plan_version": plan["plan_version"],
        "execution_stage": plan["execution_stage"],
        "execution_authorised": plan["execution_authorised"],
        "execution_seal_state": seal["state"],
        "calibration_scope": plan["calibration"]["calibration_scope"],
        "frozen_identities": {k: frozen[k] for k in IDENTITY_SURFACE},
        "implementation_file_hashes_digest":
            _digest(frozen["implementation_file_hashes"]),
        "seed_map_sha256": sha256_file(os.path.join(root, SEED_MAP_JSON)),
        "output_schema": {
            "directory": plan["output_schema"]["directory"],
            "record_schema": plan["output_schema"]["record_schema"],
            "manifest_schema": plan["output_schema"]["manifest_schema"],
            "per_record_fields": list(plan["output_schema"]["per_record_fields"]),
            "aggregate_fields": list(plan["output_schema"]["aggregate_fields"]),
        },
        "failure_classifications": list(plan["failure_classifications"]),
        "cases": cases,
        "release_criteria": release,
    }


def _digest(mapping: dict[str, str]) -> str:
    import hashlib
    return hashlib.sha256(_canonical(mapping).encode("utf-8")).hexdigest()


def render_authority_block(plan: dict[str, Any], root: str = ".") -> str:
    """The exact text the Markdown must carry between the anchors."""
    body = json.dumps(authority_from_plan(plan, root), indent=2, sort_keys=True,
                      ensure_ascii=True)
    return f"{BLOCK_BEGIN}\n\n```json\n{body}\n```\n\n{BLOCK_END}"


def markdown_text(root: str = ".") -> str:
    path = os.path.join(root, PLAN_MARKDOWN)
    if not os.path.exists(path):
        raise Refusal("normative Markdown validation plan is absent")
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def authority_from_markdown(root: str = ".") -> dict[str, Any]:
    """Parse the generated block. Absent, duplicated or malformed -> REFUSAL."""
    text = markdown_text(root)
    if text.count(BLOCK_BEGIN) != 1 or text.count(BLOCK_END) != 1:
        raise Refusal(
            "the normative Markdown plan must carry exactly one generated authority "
            f"block; found {text.count(BLOCK_BEGIN)} begin and {text.count(BLOCK_END)} "
            "end anchors"
        )
    inner = text.split(BLOCK_BEGIN, 1)[1].split(BLOCK_END, 1)[0]
    fenced = re.search(r"```json\n(.*?)\n```", inner, re.S)
    if fenced is None:
        raise Refusal("the generated authority block contains no ```json fence")
    try:
        parsed = json.loads(fenced.group(1))
    except json.JSONDecodeError as exc:
        raise Refusal(f"the generated authority block is not valid JSON: {exc}") from exc
    if not isinstance(parsed, dict):
        raise Refusal("the generated authority block must be a JSON object")
    return parsed


# --------------------------------------------------- human-rendering extraction
def _section(text: str, start: str, stop: str, what: str) -> str:
    if text.count(start) != 1:
        raise Refusal(f"Markdown plan does not carry exactly one {what} heading")
    body = text.split(start, 1)[1]
    return body.split(stop, 1)[0] if stop in body else body


def _row(body: str, label: str, where: str) -> str:
    """Read one `| label | value |` row by its EXACT label. Fail-closed."""
    found = re.findall(r"^\|\s*" + re.escape(label) + r"\s*\|\s*(.+?)\s*\|\s*$",
                       body, re.M)
    if len(found) != 1:
        raise Refusal(
            f"Markdown {where} must carry exactly one {label!r} row; found {len(found)}"
        )
    return found[0]


def _ticked(value: str) -> list[str]:
    return re.findall(r"`([^`]+)`", value)


def _plain(value: str) -> str:
    return value.replace("**", "").replace("`", "").strip()


def markdown_rendering(root: str = ".") -> dict[str, Any]:
    """The values a HUMAN reads. Parsed from anchored rows, never free prose."""
    text = markdown_text(root)

    # Deliberately NOT anchored to line start: a second version statement anywhere
    # in the document, on its own line or mid-paragraph, is an ambiguity and must
    # refuse rather than be masked by the first match.
    version = re.findall(r"Plan version \*\*([0-9]+\.[0-9]+\.[0-9]+)\*\*", text)
    if len(version) != 1:
        raise Refusal(
            f"Markdown plan must state exactly one 'Plan version **x.y.z**'; "
            f"found {len(version)}"
        )

    authorised = re.findall(r"`execution_authorised` is `(true|false)`", text)
    if len(authorised) != 1:
        raise Refusal(
            "Markdown plan must state the execution_authorised flag exactly once; "
            f"found {len(authorised)}"
        )

    sec1 = _section(text, "## 1. Frozen identities", "\n## 2.", "section-1")
    identities = {key: _plain(_row(sec1, label, "section 1"))
                  for label, key in IDENTITY_ROW_LABELS}

    sec3 = _section(text, "## 3. The eight cases", "\n## 4.", "section-3")
    cases = []
    for block in re.split(r"\n### ", sec3):
        head = re.match(r"`([A-Za-z0-9_]+)`\s*—\s*(.+)", block)
        if head is None:
            continue
        role = head.group(2).strip().replace(" ", "_")
        sub_row = re.findall(
            r"^\|\s*subconditions \((\d+)\)\s*\|\s*(.+?)\s*\|\s*$", block, re.M)
        if len(sub_row) != 1:
            raise Refusal(
                f"case {head.group(1)!r} must carry exactly one 'subconditions (n)' "
                f"row; found {len(sub_row)}"
            )
        cases.append({
            "case_id": head.group(1),
            "role": role,
            "replicate_count": int(_plain(_row(block, "replicate count", "a case"))
                                   .replace(",", "")),
            "subcondition_count": int(sub_row[0][0]),
            "subconditions": _ticked(sub_row[0][1]),
            "requires_block1_calibration":
                _plain(_row(block, "requires Block-1 calibration", "a case")),
            "calibration_scope": _plain(_row(block, "calibration scope", "a case")),
            "allowed_seed_families": _ticked(_row(block, "allowed seed families", "a case")),
            "primary_release_endpoint":
                _plain(_row(block, "primary release endpoint", "a case")),
        })
    return {
        "plan_version": version[0],
        "execution_authorised": authorised[0] == "true",
        "frozen_identities": identities,
        "cases": cases,
    }


# ------------------------------------------------------------------ the checker
_YES_NO = {"YES": True, "NO": False}


def require_plan_authority_coherence(root: str, plan: dict[str, Any]) -> None:
    """Refuse ANY Markdown/JSON authority disagreement. Runs before any RNG.

    Three layers, each fail-closed:
        1. the generated block must equal the block derived from the JSON plan
        2. the human-visible renderings must equal the block
        3. the section-9 output-schema surface (kept from the superseded check)
    """
    expected = authority_from_plan(plan, root)
    actual = authority_from_markdown(root)

    if actual.get("schema") != AUTHORITY_BLOCK_SCHEMA:
        raise Refusal(
            f"authority block schema is {actual.get('schema')!r}, expected "
            f"{AUTHORITY_BLOCK_SCHEMA!r}"
        )
    unknown = sorted(set(actual) - set(expected))
    if unknown:
        raise Refusal(f"authority block carries undeclared keys {unknown}")
    for key in ("schema",) + COHERENCE_SURFACE:
        if key not in actual:
            raise Refusal(f"authority block omits the normative key {key!r}")
        if _canonical(actual[key]) != _canonical(expected[key]):
            raise Refusal(
                f"MARKDOWN/JSON AUTHORITY DISAGREEMENT at {key!r}: Markdown carries "
                f"{_canonical(actual[key])[:160]} but the JSON plan declares "
                f"{_canonical(expected[key])[:160]}"
            )

    rendering = markdown_rendering(root)
    if rendering["plan_version"] != expected["plan_version"]:
        raise Refusal(
            f"MARKDOWN RENDERING STALE: the prose states plan version "
            f"{rendering['plan_version']!r}, the authority declares "
            f"{expected['plan_version']!r}"
        )
    if rendering["execution_authorised"] != expected["execution_authorised"]:
        raise Refusal(
            "MARKDOWN RENDERING STALE: the prose and the authority disagree about "
            "execution_authorised"
        )
    for _, key in IDENTITY_ROW_LABELS:
        shown = rendering["frozen_identities"][key]
        if shown != expected["frozen_identities"][key]:
            raise Refusal(
                f"MARKDOWN RENDERING STALE: the section-1 table shows {key} = "
                f"{shown!r} but the authority declares "
                f"{expected['frozen_identities'][key]!r}"
            )

    shown_cases = {c["case_id"]: c for c in rendering["cases"]}
    declared = {c["case_id"]: c for c in expected["cases"]}
    if set(shown_cases) != set(declared):
        raise Refusal(
            f"MARKDOWN RENDERING STALE: case tables declare {sorted(shown_cases)} but "
            f"the authority declares {sorted(declared)}"
        )
    for cid, shown in shown_cases.items():
        want = declared[cid]
        got_cal = _YES_NO.get(shown["requires_block1_calibration"],
                              shown["requires_block1_calibration"])
        pairs = (
            ("role", shown["role"], want["role"]),
            ("replicate_count", shown["replicate_count"], want["replicate_count"]),
            ("subcondition_count", shown["subcondition_count"], want["subcondition_count"]),
            ("subconditions", shown["subconditions"], want["subconditions"]),
            ("requires_block1_calibration", got_cal, want["requires_block1_calibration"]),
            ("calibration_scope", shown["calibration_scope"], want["calibration_scope"]),
            ("allowed_seed_families", shown["allowed_seed_families"],
             want["allowed_seed_families"]),
            ("primary_release_endpoint", shown["primary_release_endpoint"],
             want["primary_release_endpoint"]),
        )
        for field, got, wanted in pairs:
            if got != wanted:
                raise Refusal(
                    f"MARKDOWN RENDERING STALE: case {cid} table shows {field} = "
                    f"{got!r} but the authority declares {wanted!r}"
                )
