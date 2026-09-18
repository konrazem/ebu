"""Authority-coordinate validation; static, pure-function and read-only only.

This suite MUST NOT call a model step, a runner, a simulation, a trajectory, a
multi-tick loop, or any tick function, and must not write any file.  Every
check below is a pure-function evaluation, a static source/AST inspection, or a
READ-ONLY Git object query.

The read-only Git queries exist for one reason: the registry in
``authority_coordinate`` asserts which authorities the active branch carries,
and an assertion about the repository that is never checked against the
repository will drift.  These checks make drift a test failure.
"""
from __future__ import annotations

import ast
import inspect
import os
import subprocess

import authority_coordinate as ac

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


def _git(*args: str) -> tuple:
    """Read-only Git query. Returns (ok, stdout)."""
    done = subprocess.run(("git",) + args, capture_output=True, text=True)
    return done.returncode == 0, done.stdout.strip()


# --------------------------------------------------------------------------
def test_execution_safety_and_import_purity():
    group("execution safety: the module cannot run science or write files")
    source = inspect.getsource(ac)
    tree = ast.parse(source)

    banned_calls = {
        "p1c_step", "bounded_step", "step", "run", "run_l0_smoke",
        "simulate", "trajectory", "main", "check_output", "Popen", "system",
        "urlopen", "request", "connect",
    }
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            target = node.func
            name = (target.attr if isinstance(target, ast.Attribute)
                    else target.id if isinstance(target, ast.Name) else None)
            if name in banned_calls:
                found.add(name)
    check(not found, f"no model/runner/subprocess/network call ({found or 'none'})")

    # `open` must not appear at all: this module reads no file and writes none.
    opens = {n.func.id for n in ast.walk(tree)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
             and n.func.id == "open"}
    check(not opens, "the module never calls open()")

    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    science = {"d0_v29", "p1c_v29", "ebu_quote_v30", "service_v30",
               "longhorizon_v30", "sd03_exact_oracle"}
    check(not (imported & science),
          f"imports no science module ({imported & science or 'none'})")
    check(imported <= {"__future__", "importlib", "os", "dataclasses",
                       "typing"},
          f"standard library only ({sorted(imported)})")


def test_status_vocabulary_is_not_collapsed():
    group("status vocabulary: seven categories, never collapsed")
    check(len(ac.STATUS_VOCABULARY) == 7, "exactly seven statuses")
    check(len(set(ac.STATUS_VOCABULARY)) == 7, "all distinct")
    for s in ("THEOREM", "IMPLEMENTATION", "CANDIDATE", "EVIDENCE",
              "INFRASTRUCTURE", "MISSING", "RULEBOOK"):
        check(s in ac.STATUS_VOCABULARY, f"{s} is in the vocabulary")

    # A typo in a status must refuse, never silently fail to match.
    rejects(lambda: ac.require_status("quote_law", "THEORM"),
            "a mistyped status refuses rather than silently missing",
            "unknown status")

    # The load-bearing separation: the quote law is implemented but is NOT a
    # theorem and is NOT evidence.
    law = ac.authority("quote_law")
    check(ac.IMPLEMENTATION in law.statuses, "quote_law is IMPLEMENTATION")
    check(ac.CANDIDATE in law.statuses, "quote_law is CANDIDATE")
    check(ac.THEOREM not in law.statuses, "quote_law is NOT a THEOREM")
    check(ac.EVIDENCE not in law.statuses, "quote_law is NOT EVIDENCE")
    rejects(lambda: ac.require_status("quote_law", ac.THEOREM),
            "asking the quote law for THEOREM status refuses",
            "does not carry status")

    # D5 is infrastructure, never evidence.
    d5 = ac.authority("d5_benchmark")
    check(ac.EVIDENCE not in d5.statuses,
          "the D5 benchmark is NOT scientific EVIDENCE")
    rejects(lambda: ac.require_status("d5_benchmark", ac.EVIDENCE),
            "asking D5 for EVIDENCE status refuses")

    # Gate 1D-C is the one EVIDENCE row on the active branch.
    evidence = [n for n, a in ac.AUTHORITIES.items()
                if ac.EVIDENCE in a.statuses]
    check(evidence == ["gate1dc"],
          f"gate1dc is the only EVIDENCE authority ({evidence})")


def test_registry_matches_the_repository():
    group("registry integrity: on_active_branch is checked against Git")
    ok, head_branch = _git("rev-parse", "--abbrev-ref", "HEAD")
    check(ok and head_branch == ac.ACTIVE_BRANCH,
          f"active branch is {ac.ACTIVE_BRANCH} (git says {head_branch!r})")

    for name, a in sorted(ac.AUTHORITIES.items()):
        path = a.path.rstrip("/")
        present, _ = _git("cat-file", "-e", f"HEAD:{path}")
        if not present:
            # A directory path is present iff it has tracked files at HEAD.
            listed, out = _git("ls-tree", "--name-only", f"HEAD:{path}")
            present = listed and bool(out)
        check(present == a.on_active_branch,
              f"{name}: on_active_branch={a.on_active_branch} matches Git "
              f"(found={present})")


def test_absent_authorities_fail_closed():
    group("fail closed: absent authorities refuse rather than default")
    missing = ac.missing_authorities()
    check(len(missing) >= 9, f"at least nine authorities are absent ({len(missing)})")
    for name in ("stage_d_matrix", "stage_d_authority", "stage_e_authority",
                 "stage_e_harness", "stage_f_binding", "atomic_generator",
                 "atomic_interaction", "aws_c0", "sd01_aws_preparation"):
        check(name in missing, f"{name} is recorded absent")
        rejects(lambda n=name: ac.require_authority(n),
                f"require_authority({name!r}) refuses",
                "NOT carried by the active branch")

    # The refusal must say where the authority actually lives.
    try:
        ac.require_authority("stage_d_matrix")
    except ac.AuthorityUnavailable as e:
        msg = str(e)
        check("codex/sd01-stage-f-implementation" in msg,
              "the refusal names the home branch")
        check("8856d23" in msg, "the refusal names the commit")
        check(ac.COORDINATE_DOCUMENT in msg,
              "the refusal points at the coordinate document")

    # Present authorities must NOT refuse.
    for name in ("agents", "quote_law", "gate1dc", "conservation"):
        try:
            ac.require_authority(name)
            check(True, f"require_authority({name!r}) succeeds")
        except ac.AuthorityError as e:
            check(False, f"require_authority({name!r}) unexpectedly refused: {e}")

    rejects(lambda: ac.require_authority("no_such_authority"),
            "an unregistered name refuses")


def test_excluded_material_is_visible_not_deleted():
    group("N/H/X: excluded, visible, preserved")
    check("nhx_long_horizon" in ac.EXCLUDED, "N/H/X is recorded as excluded")
    rejects(lambda: ac.require_not_excluded("nhx_long_horizon"),
            "requesting N/H/X refuses", "excluded from the active programme")
    e = ac.EXCLUDED["nhx_long_horizon"]
    check(len(e.preserved_at) == 3, "three preserving commits are named")
    for sha in e.preserved_at:
        ok, _ = _git("cat-file", "-e", f"{sha}^{{commit}}")
        check(ok, f"preserved commit {sha} still exists (not rewritten)")
    check("not rewritten" in e.reopen_requires.lower()
          and "deleted" in e.reopen_requires.lower(),
          "the exclusion records that history is not rewritten")
    ac.require_not_excluded("quote_law")  # a non-excluded name must pass
    check(True, "a non-excluded name passes through")


def test_allocation_guard_is_diagnostic_only():
    group("simultaneous groups: representable, allocation diagnostic-only")
    # Singletons need no split - any role is vacuously fine.
    for role in ("diagnostic", "settlement", "shapley_allocation"):
        check(ac.require_diagnostic_only(role, group_size=1) == role,
              f"group_size=1 permits role {role!r} (nothing to split)")
    check(ac.require_diagnostic_only("diagnostic", group_size=0) == "diagnostic",
          "group_size=0 permits a diagnostic role")

    # At m >= 2 every unlicensed role must refuse.
    for role in ac.UNLICENSED_ROLES:
        rejects(lambda r=role: ac.require_diagnostic_only(r, group_size=2),
                f"group_size=2 refuses role {role!r}",
                "no committed authority grants")
    # ... and the diagnostic roles must pass.
    for role in ac.DIAGNOSTIC_ROLES:
        check(ac.require_diagnostic_only(role, group_size=2) == role,
              f"group_size=2 permits diagnostic role {role!r}")
    # An unrecognized role fails closed rather than being assumed diagnostic.
    rejects(lambda: ac.require_diagnostic_only("something_new", group_size=2),
            "an unrecognized role fails closed at m >= 2",
            "must declare one")
    rejects(lambda: ac.require_diagnostic_only("diagnostic", group_size=-1),
            "a negative group size refuses")
    rejects(lambda: ac.require_diagnostic_only("", group_size=2),
            "an empty role refuses")

    # The refusal must cite why, not merely say no.
    try:
        ac.require_diagnostic_only("settlement", group_size=2)
    except ac.UnlicensedAllocation as e:
        msg = str(e)
        check("O3" in msg, "the refusal cites O3")
        check("Thm 8.2" in msg and "m = 1" in msg,
              "the refusal cites the m = 1 scope of Thm 8.2")


def test_namespace_package_trap_is_closed():
    group("stale lineage directories cannot masquerade as present packages")
    traps = ac.namespace_package_traps(".")
    check("stage_e_harness" in traps,
          f"stage_e_harness is detected as a namespace trap ({traps})")
    rejects(lambda: ac.require_no_namespace_trap("stage_e_harness"),
            "require_no_namespace_trap refuses for stage_e_harness",
            "EMPTY namespace package")

    # The directories are present on disk but carry no tracked source.
    for name in traps:
        check(os.path.isdir(name), f"{name}/ exists on disk (not deleted)")
        listed, out = _git("ls-files", name)
        check(listed and not out, f"{name}/ has zero tracked files at HEAD")
        non_pyc = [p for _, _, fs in os.walk(name) for p in fs
                   if not p.endswith(".pyc")]
        check(not non_pyc, f"{name}/ holds only .pyc bytecode")

    # A real package on the active branch must NOT be flagged.
    check(not ac._is_namespace_trap("results", "."),
          "a tracked data directory is not reported as an import trap")
    check(not ac._is_namespace_trap("figures", "."),
          "a second tracked data directory is not reported either")

    # No sourceless-import risk anywhere: no .pyc outside __pycache__.
    stray = [os.path.join(r, f)
             for r, _, fs in os.walk(".")
             for f in fs
             if f.endswith(".pyc") and "__pycache__" not in r
             and not r.startswith("./venv") and not r.startswith("./.git")]
    check(not stray, f"no .pyc outside __pycache__ ({stray[:2]})")


def test_escalations_are_recorded():
    group("open escalations are enumerated and refuse unknown codes")
    for code in ("E2", "E3", "E4", "E5"):
        check(code in ac.OPEN_ESCALATIONS, f"{code} is recorded")
    # E1 was resolved by the author's decision. It must no longer be reachable
    # as a blocker, and asking for it must refuse rather than quietly return a
    # stale blocker - a resolved escalation that still blocks is a bug.
    check("E1" not in ac.OPEN_ESCALATIONS, "E1 is no longer an open blocker")
    rejects(lambda: ac.escalations_blocking("E1"),
            "E1 refuses as a blocker now that it is resolved",
            "unknown escalation")
    rejects(lambda: ac.escalations_blocking("E9"),
            "an unknown escalation code refuses")
    got = ac.escalations_blocking("E2", "E3")
    check(len(got) == 2 and got[0][0] == "E2", "known codes return in order")
    check("m >= 2" in ac.OPEN_ESCALATIONS["E2"],
          "E2 states the m >= 2 scope")
    check("not block" in ac.OPEN_ESCALATIONS["E2"].lower()
          and "diagnostic" in ac.OPEN_ESCALATIONS["E2"].lower(),
          "E2 records that diagnostics remain permitted")


def test_author_decision_and_rulebooks():
    group("the author's decision: prospective rules, not merge, not evidence")

    # The three source-locked commits must exist AND lie on the named branch.
    expected = {
        "stage_d": ("research/stage-d-scientific-validation-authority",
                    "8936bb4"),
        "stage_e": ("research/stage-e-scientific-harness-authority",
                    "0b1d58a"),
        "stage_f": ("codex/sd01-stage-f-implementation", "cc5581c"),
    }
    check(set(ac.RULEBOOKS) == set(expected), "exactly three rulebooks")
    for name, (branch, commit) in expected.items():
        book = ac.rulebook(name)
        check(book.branch == branch, f"{name} names branch {branch}")
        check(book.commit == commit, f"{name} is locked at {commit}")
        exists, _ = _git("cat-file", "-e", f"{commit}^{{commit}}")
        check(exists, f"{name}: {commit} exists in the object database")
        on_branch, _ = _git("merge-base", "--is-ancestor", commit, branch)
        check(on_branch, f"{name}: {commit} lies on {branch}")

        # The decision must NOT be readable as a merge.
        merged, _ = _git("merge-base", "--is-ancestor", commit, "HEAD")
        check(not merged,
              f"{name}: {commit} is NOT merged into HEAD (adoption != merge)")

    # Adopted as rules, still absent from the active branch: both at once.
    for name in ("stage_d_authority", "stage_e_authority", "stage_f_binding",
                 "stage_e_harness", "stage_d_matrix"):
        a = ac.AUTHORITIES[name]
        check(ac.RULEBOOK in a.statuses, f"{name} carries RULEBOOK")
        check(ac.MISSING in a.statuses,
              f"{name} is still MISSING from the active branch")
        rejects(lambda n=name: ac.require_authority(n),
                f"require_authority({name!r}) still refuses",
                "NOT carried by the active branch")

    # RULEBOOK is never EVIDENCE, and never execution permission.
    for name in ac.RULEBOOKS:
        check(ac.rulebook_is_evidence(name) is False,
              f"{name} is not evidence")
        rejects(lambda n=name: ac.require_execution_permission(n),
                f"{name} grants no execution permission",
                "NO execution permission")
    rulebook_rows = [n for n, a in ac.AUTHORITIES.items()
                     if ac.RULEBOOK in a.statuses]
    for name in rulebook_rows:
        check(ac.EVIDENCE not in ac.AUTHORITIES[name].statuses,
              f"{name} carries RULEBOOK but NOT EVIDENCE")

    # The dataclass invariant must forbid the collapse outright.
    rejects(lambda: ac.Authority("x", "x", "b", "c", False,
                                 (ac.RULEBOOK, ac.EVIDENCE)),
            "RULEBOOK + EVIDENCE is rejected by construction",
            "mutually exclusive")

    # The six-point coordinate and the three non-claims are recorded.
    check(len(ac.PROGRAMME_COORDINATE) == 6, "six coordinate points")
    check(len(ac.DECISION_NON_CLAIMS) == 3, "three explicit non-claims")
    check(ac.COORDINATE_ID == "W-2", "the coordinate advanced to W-2")
    check(ac.SUPERSEDED_COORDINATE_ID == "W-1", "W-1 is retained, not voided")

    # E1 is resolved and recorded; the rest still stand.
    check("E1" in ac.RESOLVED_ESCALATIONS, "E1 is recorded resolved")
    check("E1" not in ac.OPEN_ESCALATIONS, "E1 is no longer open")
    check(set(ac.OPEN_ESCALATIONS) == {"E2", "E3", "E4", "E5"},
          "E2-E5 remain open")

    # The name collisions must not be read as an adopted allocation rule.
    check(len(ac.NOT_VALUE_ALLOCATION) == 3, "three name collisions recorded")
    joined = " ".join(ac.NOT_VALUE_ALLOCATION)
    check("mobius.py" in joined, "the Mobius conformance module is named")
    check("allocation.py" in joined, "the worker-allocation module is named")
    check("E2" in ac.OPEN_ESCALATIONS,
          "E2 stays open despite those names")


def test_coordinate_document_agrees_with_code():
    group("the coordinate document and this module say the same thing")
    path = ac.COORDINATE_DOCUMENT
    check(os.path.isfile(path), f"{path} exists")
    with open(path, encoding="utf-8") as handle:
        doc = handle.read()
    check("RECONCILIATION DOCUMENT" in doc, "it declares itself derived")
    check("Not an authority" in doc, "it declares itself not an authority")
    check("No scientific execution occurred" in doc, "it states its non-claim")
    for code in ac.OPEN_ESCALATIONS:
        check(f"### {code} " in doc, f"{code} is escalated in the document")
    for name in ("stage_d_matrix", "stage_e_harness", "atomic_generator"):
        a = ac.AUTHORITIES[name]
        check(a.home_branch in doc,
              f"the document records {name}'s home branch")
    check(ac.COORDINATE_ID in doc, "the working coordinate id appears")
    check(ac.SUPERSEDED_COORDINATE_ID in doc, "W-1 is retained in the document")

    # The decision, its locks and its non-claims must be in the document too,
    # not only in code: the document is what a human reads.
    check(ac.AUTHOR_DECISION_DATE in doc, "the decision date appears")
    for name, book in sorted(ac.RULEBOOKS.items()):
        check(book.commit in doc, f"{name}'s locked commit {book.commit} appears")
        check(book.branch in doc, f"{name}'s branch appears")
    check("not merged" in doc.lower() or "NOT merged" in doc,
          "the document states the branches were not merged")
    check("not authorize execution" in doc.lower()
          or "does **not** authorize execution" in doc,
          "the document states execution is not authorized")
    # E1 must be visibly resolved rather than silently dropped.
    check("E1" in doc and "RESOLVED" in doc,
          "E1 is shown resolved, not deleted")
    # Distinctive fragments, because the document may abbreviate a long path.
    for marker in ("mobius.py", "allocation.py",
                   "I3C_SETTLEMENT_CAUSALITY_REPAIR"):
        check(marker in doc, f"the {marker} name-collision is documented")
    check(len(ac.NOT_VALUE_ALLOCATION) == 3,
          "all three collisions are carried in code as well")
    # The exclusion must be visible in the document, not only in code.
    check("EXCLUDED" in doc and "N/H/X" in doc,
          "N/H/X is visibly excluded in the document")


def main() -> int:
    test_execution_safety_and_import_purity()
    test_status_vocabulary_is_not_collapsed()
    test_registry_matches_the_repository()
    test_absent_authorities_fail_closed()
    test_excluded_material_is_visible_not_deleted()
    test_allocation_guard_is_diagnostic_only()
    test_namespace_package_trap_is_closed()
    test_escalations_are_recorded()
    test_author_decision_and_rulebooks()
    test_coordinate_document_agrees_with_code()
    print(f"\nAuthority coordinate: {PASSED} passed, {FAILED} failed, "
          f"{GROUPS} groups")
    print("Model-state advancement: NONE; registered runs generated: 0")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())
