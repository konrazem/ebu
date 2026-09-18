"""Study-protocol schema validation; static and pure-function only.

This suite MUST NOT call a model step, a runner, a simulation, a trajectory or
any tick function, and must not write any file.  It exercises refusal paths on
synthetic protocol mappings only.  No world, parameter, hypothesis, metric or
falsifier is proposed by this file: the synthetic values below are deliberately
meaningless placeholder strings whose only purpose is to make a slot non-empty
so that a refusal path can be reached.
"""
from __future__ import annotations

import ast
import inspect

import authority_coordinate as ac
import study_protocol_schema as sp

PASSED = 0
FAILED = 0
GROUPS = 0


def group(title: str) -> None:
    global GROUPS
    GROUPS += 1
    print(f"\n[{GROUPS:02d}] {title}")


def check(condition: bool, label: str) -> None:
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  PASS {label}")
    else:
        FAILED += 1
        print(f"  FAIL {label}")


def rejects(function, label: str, contains: str = "") -> None:
    try:
        function()
    except Exception as error:
        check(not contains or contains in str(error), label)
    else:
        check(False, label)


# A structurally complete protocol built from PLACEHOLDERS.  These are not
# proposed values; they are non-empty tokens that let refusal paths downstream
# of completeness be reached at all.
def _placeholder_protocol() -> dict:
    return {slot: f"PLACEHOLDER-NOT-A-PROPOSAL::{slot}" for slot in sp.SLOTS}


def test_execution_safety():
    group("execution safety: the schema cannot run or write")
    source = inspect.getsource(sp)
    tree = ast.parse(source)
    banned = {"p1c_step", "bounded_step", "run", "run_l0_smoke", "simulate",
              "trajectory", "Popen", "system", "check_output", "urlopen"}
    found = {n.func.attr if isinstance(n.func, ast.Attribute)
             else n.func.id if isinstance(n.func, ast.Name) else None
             for n in ast.walk(tree) if isinstance(n, ast.Call)} & banned
    check(not found, f"no model/runner/subprocess call ({found or 'none'})")
    opens = {n.func.id for n in ast.walk(tree)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
             and n.func.id == "open"}
    check(not opens, "the schema never calls open()")


def test_no_defaults_exist():
    group("the schema proposes nothing: every slot is declared, none defaulted")
    check(len(sp.SLOTS) == 13, f"thirteen slots are declared ({len(sp.SLOTS)})")
    # An empty protocol must name every slot as unfilled - none may be supplied.
    check(sp.unfilled_slots({}) == tuple(sp.SLOTS),
          "an empty protocol leaves every slot unfilled (no defaults)")
    rejects(lambda: sp.validate_protocol({}),
            "an empty protocol refuses", "unfilled slot")
    # The scientific slots are a declared subset, and S-H is among them.
    check(set(sp.SCIENTIFIC_SLOTS) <= set(sp.SLOTS),
          "the scientific slots are a subset of the declared slots")
    check("S-H" in sp.SCIENTIFIC_SLOTS,
          "S-H (hypotheses/metrics/falsifiers) is a scientific slot")


def test_incompleteness_refuses():
    group("incomplete and malformed protocols refuse")
    rejects(lambda: sp.validate_protocol("not a mapping"),
            "a non-mapping refuses", "must be a mapping")
    rejects(lambda: sp.validate_protocol([]),
            "a list refuses")

    for bad in (None, "", "   ", [], {}, ()):
        p = _placeholder_protocol()
        p["S-H"] = bad
        rejects(lambda q=p: sp.validate_protocol(q),
                f"an empty S-H value ({bad!r}) refuses", "S-H")

    # Every single slot must be individually required.
    for slot in sp.SLOTS:
        p = _placeholder_protocol()
        del p[slot]
        rejects(lambda q=p: sp.validate_protocol(q),
                f"a protocol missing {slot} refuses", slot)

    # An undeclared slot must refuse rather than be ignored.
    p = _placeholder_protocol()
    p["S-ZZ"] = "smuggled"
    rejects(lambda: sp.validate_protocol(p),
            "an unknown slot refuses rather than being ignored", "unknown slot")

    # A complete placeholder protocol passes completeness only.
    check(sp.validate_protocol(_placeholder_protocol()) is not None,
          "a structurally complete protocol passes the completeness check")


def test_freeze_is_enforced():
    group("freeze: canonical hash mismatch refuses")
    p = _placeholder_protocol()
    digest = sp.protocol_hash(p)
    check(len(digest) == 64, "the protocol hash is a 64-char digest")
    check(sp.require_frozen(p, digest) == digest, "a matching freeze passes")
    check(sp.require_frozen(p, digest.upper()) == digest,
          "the declared hash is case-insensitive")
    check(sp.canonical_bytes(p) == sp.canonical_bytes(dict(reversed(list(p.items())))),
          "canonical encoding is key-order independent")

    rejects(lambda: sp.require_frozen(p, "0" * 64),
            "a mismatched freeze refuses", "hash mismatch")
    rejects(lambda: sp.require_frozen(p, "abc"),
            "a malformed hash refuses", "64-character")
    # Altering one slot must change the hash: a frozen protocol cannot drift.
    q = dict(p)
    q["S-T"] = q["S-T"] + "-altered"
    check(sp.protocol_hash(q) != digest, "altering a slot changes the hash")
    rejects(lambda: sp.require_frozen(q, digest),
            "an altered protocol fails its original freeze",
            "never altered to make")


def test_execution_is_refused_while_blockers_stand():
    group("execution: refused while any escalation stands")
    p = _placeholder_protocol()
    digest = sp.protocol_hash(p)
    # E1 was resolved by the author's 2026-09-16 decision; E2-E5 stand. The
    # resolution must NOT create a success path here - adopting a rulebook is
    # not permission to execute, so the refusal must survive it.
    check(len(ac.OPEN_ESCALATIONS) == 4, "four escalations stand today")
    check("E1" in ac.RESOLVED_ESCALATIONS, "E1 is resolved, not forgotten")
    rejects(lambda: sp.require_executable(p, digest),
            "a complete, correctly frozen protocol is STILL refused",
            "standing escalation")
    # The refusal must enumerate the blockers, not merely say no.
    try:
        sp.require_executable(p, digest)
    except sp.ProtocolNotExecutable as e:
        msg = str(e)
        for code in ("E2", "E3", "E4", "E5"):
            check(code in msg, f"the refusal names {code}")
        check("E1" not in msg,
              "the refusal does NOT cite the resolved E1 as a blocker")
        check(ac.COORDINATE_DOCUMENT in msg,
              "the refusal points at the coordinate document")
    # Incompleteness is reported as incompleteness, not masked by the blocker.
    incomplete = _placeholder_protocol()
    del incomplete["S-W"]
    rejects(lambda: sp.require_executable(incomplete, digest),
            "an incomplete protocol reports incompleteness first", "S-W")


def test_framework_document_agrees_with_schema():
    group("the framework document and the schema declare the same slots")
    path = "V3.0_LONG_RUN_STUDY_FRAMEWORK.md"
    with open(path, encoding="utf-8") as handle:
        doc = handle.read()
    check("PROSPECTIVE ARCHITECTURE" in doc, "the document declares itself architecture")
    check("No scientific execution occurred" in doc, "it states its non-claim")
    check("not N/H/X" in doc or "is *not* N/H/X" in doc,
          "it records that it is not N/H/X")
    for slot in sp.SLOTS:
        check(f"| {slot} |" in doc, f"{slot} appears in the document slot table")
    # The decision order and the diagnostic-only rule must be stated there.
    check("diagnostic" in doc.lower() and "G-4" in doc,
          "the escalation trigger rule G-4 is recorded")
    check("Thm 8.2" in doc or "Theorem 8.2" in doc,
          "the m = 1 scope of the telescoping theorem is recorded")
    # Sentence-level: these documents wrap prose, so a raw substring scan
    # splits the phrase across two lines and reports a false negative.
    flat = " ".join(doc.split())
    check("not made admissible by a favourable EBU value" in flat,
          "the decision order's load-bearing consequence is stated")
    check("value that is ranked must be the value of the vector that" in flat,
          "the rank-what-executes rule is stated")


def main() -> int:
    test_execution_safety()
    test_no_defaults_exist()
    test_incompleteness_refuses()
    test_freeze_is_enforced()
    test_execution_is_refused_while_blockers_stand()
    test_framework_document_agrees_with_schema()
    print(f"\nStudy protocol schema: {PASSED} passed, {FAILED} failed, "
          f"{GROUPS} groups")
    print("Model-state advancement: NONE; registered runs generated: 0")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())
