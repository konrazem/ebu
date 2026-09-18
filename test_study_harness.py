"""Harness-architecture validation; static, pure-function and synthetic only.

This suite MUST NOT call a model step, a runner, a simulation, a trajectory, a
multi-tick loop or any tick function, and must not write a file.  Every check
is a pure-function evaluation on a FROZEN or SYNTHETIC individual state, or a
static/AST inspection of the module source.

The synthetic states below are deliberately meaningless numbers.  They exercise
mechanism only: no world, potential, parameter, metric value, threshold or
outcome interpretation is asserted anywhere in this file, and none may be added
to it - that is what makes these tests safe to run before any science exists.
"""
from __future__ import annotations

import ast
import inspect

import authority_coordinate as ac
import study_harness as sh

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


# --- synthetic fixtures; no scientific meaning whatsoever ------------------
def _profile(**over):
    base = dict(
        profile_id="SYNTHETIC-PROFILE", profile_version="0",
        account_level=2, boundary_id="SYNTHETIC-BOUNDARY",
        boundary_hierarchy=("outer", "inner"), quantity_id="q",
        units="synthetic-unit", state_coordinates=("a", "b"),
        internal_transformation="declared-invariant",
        boundary_channels=("in", "out"), sign_convention="inflow-positive",
        observability="observable", residual_policy="exact",
        non_claims=("no isolation claimed", "no completeness claimed"))
    base.update(over)
    return sh.ConservationProfile(**base)


def _state(**over):
    base = {"a": 1.0, "b": 2.0, "hidden": 9.0}
    base.update(over)
    return sh.State(base)


# --------------------------------------------------------------------------
def test_execution_safety():
    group("execution safety: the harness cannot run science or write files")
    source = inspect.getsource(sh)
    tree = ast.parse(source)

    banned = {"p1c_step", "bounded_step", "step", "run", "run_l0_smoke",
              "simulate", "trajectory", "tick", "advance", "check_output",
              "Popen", "system", "urlopen", "request", "connect", "open"}
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            target = node.func
            name = (target.attr if isinstance(target, ast.Attribute)
                    else target.id if isinstance(target, ast.Name) else None)
            if name in banned:
                found.add(name)
    check(not found, f"no model/runner/subprocess/network/open call ({found or 'none'})")

    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    science = {"d0_v29", "p1c_v29", "ebu_quote_v30", "service_v30",
               "longhorizon_v30", "sd03_exact_oracle", "gate1dc_v30"}
    check(not (imported & science), f"imports no science module ({imported & science or 'none'})")
    check(imported <= {"__future__", "hashlib", "json", "dataclasses",
                       "typing", "authority_coordinate"},
          f"standard library plus the coordinate only ({sorted(imported)})")

    # The harness must not become executable by accident.
    check(sh.harness_is_executable() is False,
          "the harness reports itself NOT executable")
    check(len(ac.OPEN_ESCALATIONS) == 4, "because E2-E5 stand")


def test_conservation_is_declared_never_assumed():
    group("physical conservation: declared profile, fail-closed closure")
    p = _profile()
    check(len(sh.CONSERVATION_PROFILE_FIELDS) == 14,
          "the 14.2 field list is carried explicitly")
    check(sh.ACCOUNT_LEVELS == (1, 2, 3), "levels 1-3 are all permitted")
    check(p.account_level == 2, "a Level 2 account is accepted as-is")

    # A closing ledger returns its residual.
    closing = sh.Ledger("q", 10.0, 12.0, {"in": 3.0, "out": -1.0})
    check(sh.check_closure(p, closing) == 0.0, "an exactly closing ledger passes")

    # A non-closing ledger refuses under an exact policy.
    open_ledger = sh.Ledger("q", 10.0, 12.0, {"in": 3.0, "out": -0.5})
    rejects(lambda: sh.check_closure(p, open_ledger),
            "a non-closing ledger refuses under an 'exact' policy",
            "exceeds the limit")

    # An undeclared channel is an unaccounted flow.
    leaky = sh.Ledger("q", 10.0, 12.0, {"in": 3.0, "out": -1.0, "secret": 0.0})
    rejects(lambda: sh.check_closure(p, leaky),
            "an undeclared boundary channel refuses",
            "undeclared boundary channel")

    # Quantity mismatch refuses rather than silently comparing two quantities.
    rejects(lambda: sh.check_closure(p, sh.Ledger("other", 0.0, 0.0, {})),
            "a quantity mismatch refuses")

    # An uncertainty-aware policy may carry a tolerance; 'exact' may not.
    tolerant = _profile(residual_policy="uncertainty_aware", tolerance=1.0)
    check(sh.check_closure(tolerant, open_ledger) != 0.0,
          "an uncertainty-aware policy admits a residual within tolerance")
    rejects(lambda: _profile(residual_policy="exact", tolerance=1.0),
            "'exact' cannot carry a tolerance",
            "cannot carry a non-zero")
    rejects(lambda: sh.check_closure(_profile(residual_policy="uncertainty_aware",
                                              tolerance=0.1), open_ledger),
            "a residual beyond the declared tolerance still refuses")

    # Every required declaration refuses when missing - never defaults.
    rejects(lambda: _profile(profile_id=""), "an empty profile_id refuses")
    rejects(lambda: _profile(account_level=4), "an unknown account level refuses")
    rejects(lambda: _profile(residual_policy="lenient"),
            "an unknown residual policy refuses")
    rejects(lambda: _profile(state_coordinates=()),
            "empty state_coordinates refuse")
    rejects(lambda: _profile(boundary_channels=()),
            "empty boundary_channels refuse")
    rejects(lambda: _profile(non_claims=()),
            "missing non_claims refuse", "non_claims")


def test_state_is_immutable():
    group("immutable state: enforced, not documented")
    s = _state()
    original = s.digest

    rejects(lambda: s.__setitem__("a", 99.0), "__setitem__ refuses",
            "immutable")
    rejects(lambda: setattr(s, "a", 99.0), "attribute assignment refuses")
    rejects(lambda: delattr(s, "_data"), "attribute deletion refuses")
    check(s.digest == original, "the state is unchanged after the attempts")

    # evolve() derives a new state and leaves the original byte-identical.
    t = s.evolve(a=5.0)
    check(t["a"] == 5.0 and s["a"] == 1.0, "evolve() does not touch the original")
    check(s.digest == original, "the original digest is unchanged")
    check(t.digest != original, "the derived state has a different digest")

    # A typo must not silently add a field.
    rejects(lambda: s.evolve(typo=1.0), "evolve() refuses an unknown field",
            "cannot introduce new field")

    # Mutable containers cannot be smuggled into a state.
    rejects(lambda: sh.State({"x": [1, 2]}), "a list field refuses", "mutable")
    rejects(lambda: sh.State({"x": {"k": 1}}), "a dict field refuses")
    rejects(lambda: sh.State({1: "a"}), "a non-string key refuses")

    # Digests are content-addressed and order-independent.
    check(sh.State({"a": 1.0, "b": 2.0}).digest
          == sh.State({"b": 2.0, "a": 1.0}).digest,
          "key order does not change the digest")
    check(sh.State({"a": 1.0}) == sh.State({"a": 1.0}), "equality is by content")
    check(len({sh.State({"a": 1.0}), sh.State({"a": 1.0})}) == 1,
          "equal states hash equal")
    rejects(lambda: s["nope"], "an unknown field read refuses with the field list",
            "not a field of this state")


def test_demand_replay_is_deterministic():
    group("deterministic demand replay: exact, random-access, seed-addressed")
    a = sh.DemandStream("seed-1", "demand", 0.0, 10.0)
    b = sh.DemandStream("seed-1", "demand", 0.0, 10.0)
    c = sh.DemandStream("seed-2", "demand", 0.0, 10.0)
    d = sh.DemandStream("seed-1", "other-stream", 0.0, 10.0)

    check(a.replay(16) == b.replay(16), "same seed replays identically")
    check(a.replay(16) != c.replay(16), "a different seed differs")
    check(a.replay(16) != d.replay(16),
          "a different stream_id differs under the same seed")

    # Random access: order of calls cannot shift the stream.
    check(a.value(7) == b.replay(8)[7], "index 7 matches the 8th replayed value")
    check([a.value(i) for i in (5, 1, 9)] == [a.value(5), a.value(1), a.value(9)],
          "out-of-order access is stable")
    check(all(0.0 <= v < 10.0 for v in a.replay(64)), "values stay in bounds")
    check(len(set(a.replay(64))) > 1, "the stream is not constant")

    # The identity fully reproduces the stream.
    ident = a.identity()
    check(set(ident) == {"seed", "stream_id", "low", "high", "construction"},
          "identity carries everything needed to rebuild the stream")
    rebuilt = sh.DemandStream(ident["seed"], ident["stream_id"],
                              ident["low"], ident["high"])
    check(rebuilt.replay(32) == a.replay(32), "a rebuilt stream replays identically")

    rejects(lambda: sh.DemandStream("", "d", 0.0, 1.0), "an empty seed refuses")
    rejects(lambda: sh.DemandStream("s", "", 0.0, 1.0), "an empty stream_id refuses")
    rejects(lambda: sh.DemandStream("s", "d", 1.0, 1.0),
            "non-increasing bounds refuse")
    rejects(lambda: a.value(-1), "a negative index refuses")
    rejects(lambda: a.value(True), "a bool index refuses")


def test_controller_information_boundary():
    group("controller boundaries: a controller sees only what it was granted")
    s = _state()
    local = sh.InformationBoundary("local-controller", ("a", "b"))

    view = local.project(s)
    check(set(view) == {"a", "b"}, "the projection carries only granted fields")
    check("hidden" not in view, "an ungranted field is absent from the view")
    rejects(lambda: view["hidden"], "reading it from the view refuses")
    rejects(lambda: local.require_readable("hidden"),
            "require_readable refuses an ungranted field", "may not read")
    check(local.require_readable("a") == "a", "a granted field is readable")

    # A granted-but-absent field must refuse, not silently shorten the view.
    wide = sh.InformationBoundary("wide", ("a", "absent"))
    rejects(lambda: wide.project(s),
            "a granted field missing from the state refuses",
            "does not carry")

    rejects(lambda: sh.InformationBoundary("c", ()),
            "an empty boundary refuses rather than meaning 'everything'",
            "empty boundary is refused")
    rejects(lambda: sh.InformationBoundary("c", ("a", "a")),
            "duplicate readable fields refuse")
    rejects(lambda: local.project({"a": 1}), "projection requires a frozen State")


def test_receipts_and_event_log():
    group("receipts and event logs: hash-chained and tamper-evident")
    log = sh.EventLog()
    check(log.head == sh.Receipt.GENESIS, "an empty log heads at GENESIS")
    check(sh.receipt_chain(()) == sh.Receipt.GENESIS, "an empty chain verifies")

    r1 = log.append("declaration", {"profile": "SYNTHETIC-PROFILE"})
    r2 = log.append("closure_check", {"residual": 0.0})
    check(len(log) == 2, "both events were recorded")
    check(r2.previous == r1.seal, "each receipt links to its predecessor")
    check(log.verify() == r2.seal, "the log verifies to its head")
    check(log.head == r2.seal, "head matches the last seal")

    # Reordering breaks the chain.
    rejects(lambda: sh.receipt_chain([r2, r1]),
            "a reordered chain refuses", "chain broken at position")
    # Dropping a middle entry breaks the chain.
    r3 = log.append("third", {"n": 3})
    rejects(lambda: sh.receipt_chain([r1, r3]),
            "a chain with a dropped entry refuses")
    # Replacing an entry's payload changes its seal.
    forged = sh.Receipt("closure_check", {"residual": 999.0}, r1.seal)
    check(forged.seal != r2.seal, "an altered payload yields a different seal")
    rejects(lambda: sh.receipt_chain([r1, forged, r3]),
            "a forged entry breaks the following link")

    # A declared seal that disagrees with the content is refused outright.
    rejects(lambda: sh.Receipt("k", {"v": 1}, sh.Receipt.GENESIS, "0" * 64),
            "a receipt is never re-sealed to make it agree", "seal mismatch")
    rejects(lambda: sh.Receipt("k", {"v": 1}, "short"),
            "a malformed previous digest refuses")
    rejects(lambda: sh.Receipt("", {}, sh.Receipt.GENESIS),
            "a receipt without a kind refuses")

    # The log is append-only from the outside.
    check(isinstance(log.entries, tuple), "entries() hands back an immutable tuple")
    rejects(lambda: setattr(log, "_receipts", []),
            "the log's storage cannot be reassigned")
    check(not hasattr(log, "delete") and not hasattr(log, "update"),
          "the log offers no delete or update")


def test_negative_controls_must_fail():
    group("negative controls: a control that passes is a harness failure")
    control = sh.NegativeControl(
        "NC-undeclared-channel",
        "an undeclared boundary channel must never be accepted silently",
        sh.ConservationRefusal)

    p = _profile()
    leaky = sh.Ledger("q", 10.0, 12.0, {"in": 3.0, "out": -1.0, "secret": 1.0})
    refusal = sh.run_negative_control(control, lambda: sh.check_closure(p, leaky))
    check(isinstance(refusal, sh.ConservationRefusal),
          "the control captured the expected refusal")

    # A probe that succeeds must be reported as a harness failure.
    rejects(lambda: sh.run_negative_control(control, lambda: 42),
            "a probe that does NOT fail raises NegativeControlPassed",
            "must fail")
    # A probe that fails for the wrong reason must not count as satisfied.
    def wrong_reason():
        raise ValueError("unrelated")
    rejects(lambda: sh.run_negative_control(control, wrong_reason),
            "a probe failing with the wrong exception is refused",
            "but must fail with")

    rejects(lambda: sh.NegativeControl("x", "", sh.HarnessError),
            "a control without a declared reason refuses")
    rejects(lambda: sh.NegativeControl("x", "why", "not-a-type"),
            "a non-exception expected_refusal refuses")

    # Three more standing controls over the other mechanisms.
    s = _state()
    more = (
        (sh.NegativeControl("NC-immutability", "states must not be mutable",
                            sh.ImmutabilityViolation),
         lambda: s.evolve(unknown_field=1.0)),
        (sh.NegativeControl("NC-information-leak",
                            "a controller must not read ungranted fields",
                            sh.InformationLeak),
         lambda: sh.InformationBoundary("c", ("a",)).require_readable("hidden")),
        (sh.NegativeControl("NC-audit-chain", "a broken chain must not verify",
                            sh.AuditChainBroken),
         lambda: sh.receipt_chain([sh.Receipt("k", {}, "1" * 64)])),
    )
    for ctl, probe in more:
        got = sh.run_negative_control(ctl, probe)
        check(isinstance(got, ctl.expected_refusal), f"{ctl.control_id} refuses")


def test_reproducibility_stamp():
    group("reproducibility: one digest over inputs, code and declarations")
    s = _state()
    stream = sh.DemandStream("seed-1", "demand", 0.0, 10.0)
    args = dict(inputs={"state": s.digest},
                code_digests={"study_harness": "0" * 64},
                declarations={"demand": stream.identity()})
    one = sh.reproducibility_stamp(**args)
    two = sh.reproducibility_stamp(**args)
    check(one["stamp"] == two["stamp"], "identical parts give an identical stamp")
    check(len(one["stamp"]) == 64, "the stamp is a SHA-256 digest")

    changed = dict(args, inputs={"state": "f" * 64})
    check(sh.reproducibility_stamp(**changed)["stamp"] != one["stamp"],
          "a changed input changes the stamp")
    changed = dict(args, code_digests={"study_harness": "1" * 64})
    check(sh.reproducibility_stamp(**changed)["stamp"] != one["stamp"],
          "changed code changes the stamp")
    changed = dict(args, declarations={"demand": {"seed": "other"}})
    check(sh.reproducibility_stamp(**changed)["stamp"] != one["stamp"],
          "a changed declaration changes the stamp")

    for empty in ("inputs", "code_digests", "declarations"):
        rejects(lambda e=empty: sh.reproducibility_stamp(**dict(args, **{e: {}})),
                f"an empty {empty} refuses")

    # No live environment is captured: the stamp must be process-independent.
    # Checked on the AST, not the text, so the docstring's prose about NOT
    # reading the clock cannot itself trip the check.
    fn = ast.parse(inspect.getsource(sh.reproducibility_stamp))
    names = {n.id for n in ast.walk(fn) if isinstance(n, ast.Name)}
    names |= {n.attr for n in ast.walk(fn) if isinstance(n, ast.Attribute)}
    environmental = names & {"time", "platform", "sys", "os", "getenv",
                             "uname", "version", "now", "today"}
    check(not environmental,
          f"the stamp reads no interpreter, platform or clock ({environmental or 'none'})")


def test_metrics_and_classifications():
    group("metrics and classifications: declared, exhaustive, exclusive")
    s = _state()
    m = sh.MetricSpec("sum_ab", "synthetic-unit", True,
                      lambda st: st["a"] + st["b"])
    out = sh.evaluate_metrics([m], s)
    check(out == {"sum_ab": 3.0}, "a declared metric evaluates on one state")

    rejects(lambda: sh.MetricSpec("m", "", True, lambda st: 0),
            "a metric without units refuses", "must declare units")
    rejects(lambda: sh.MetricSpec("m", "u", "yes", lambda st: 0),
            "a non-bool direction refuses")
    rejects(lambda: sh.MetricSpec("m", "u", True, None),
            "a non-callable compute refuses")
    rejects(lambda: sh.evaluate_metrics([m, m], s),
            "a duplicate metric_id refuses", "duplicate metric_id")
    rejects(lambda: sh.evaluate_metrics([m], {"a": 1}),
            "metrics require a frozen State")

    # A well-formed scheme classifies to exactly one class.
    scheme = sh.ClassificationScheme(
        "SYNTHETIC-SCHEME", ("low", "high"),
        {"low": lambda st: st["a"] < 3.0, "high": lambda st: st["a"] >= 3.0})
    check(scheme.classify(s) == "low", "the single matching class is returned")
    check(scheme.classify(s.evolve(a=7.0)) == "high", "the other class matches")

    # Non-exhaustive: nothing matches.
    gap = sh.ClassificationScheme(
        "GAP", ("a", "b"),
        {"a": lambda st: False, "b": lambda st: False})
    rejects(lambda: gap.classify(s),
            "a non-exhaustive scheme refuses instead of dropping the outcome",
            "NOT exhaustive")
    # Overlapping: more than one matches, and the first is NOT taken.
    overlap = sh.ClassificationScheme(
        "OVERLAP", ("a", "b"),
        {"a": lambda st: True, "b": lambda st: True})
    rejects(lambda: overlap.classify(s),
            "an overlapping scheme refuses instead of taking the first match",
            "NOT mutually exclusive")

    rejects(lambda: sh.ClassificationScheme("x", ("only",), {"only": lambda st: True}),
            "a one-class scheme refuses")
    rejects(lambda: sh.ClassificationScheme("x", ("a", "b"), {"a": lambda st: True}),
            "a class without a predicate refuses")
    rejects(lambda: sh.ClassificationScheme(
                "x", ("a", "b"),
                {"a": lambda st: True, "b": lambda st: False,
                 "c": lambda st: True}),
            "a predicate naming no class refuses")


def test_no_science_is_defined_here():
    group("the harness defines no science and carries no default")
    source = inspect.getsource(sh)

    # No world, potential, parameter, threshold or outcome class may be named.
    forbidden = ("preserve_and_serve", "safe_rationing", "physical_impossibility",
                 "DC1_flux_lock", "DC2_capacity_split", "DC3_demand_pulse",
                 "near_certificate")
    present = tuple(name for name in forbidden if name in source)
    check(not present, f"no committed outcome class or world is named ({present or 'none'})")

    # N/H/X must not be revived here.
    check("nhx" not in source.lower().replace("n/h/x", "nhx")
          or "excluded" in source.lower(),
          "N/H/X is not revived in the harness")
    check("nhx_long_horizon" in ac.EXCLUDED, "N/H/X remains excluded in the coordinate")

    # Every scientific slot stays the author's: the harness fills none of them.
    import study_protocol_schema as sp
    check(len(sp.SCIENTIFIC_SLOTS) == 9, "nine scientific slots remain the author's")
    for slot in sp.SCIENTIFIC_SLOTS:
        check(slot in sp.SLOTS, f"{slot} is still an unfilled slot, not a default")

    # The harness must not be able to declare itself executable.
    check(sh.harness_is_executable() is False, "the harness is not executable")
    tree = ast.parse(inspect.getsource(sh.harness_is_executable))
    returns_constant_true = any(
        isinstance(n, ast.Return) and isinstance(n.value, ast.Constant)
        and n.value.value is True for n in ast.walk(tree))
    check(not returns_constant_true,
          "executability is derived from the open escalations, never hard-coded")


def main() -> int:
    test_execution_safety()
    test_conservation_is_declared_never_assumed()
    test_state_is_immutable()
    test_demand_replay_is_deterministic()
    test_controller_information_boundary()
    test_receipts_and_event_log()
    test_negative_controls_must_fail()
    test_reproducibility_stamp()
    test_metrics_and_classifications()
    test_no_science_is_defined_here()
    print(f"\nStudy harness: {PASSED} passed, {FAILED} failed, {GROUPS} groups")
    print("Model-state advancement: NONE; registered runs generated: 0")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())
