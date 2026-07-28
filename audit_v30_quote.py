"""
V3.0 Gate 1B read-only audit of the quote implementation and its
preregistration conformance. Runs NO behavioral trajectory and NO Q22
adversary; mutates nothing.

Checks: plan hash lock (canonical + raw); implementation/test independence;
forbidden imports and forbidden global-information identifiers; strict JSON
fail-closed serialization; equation-version consistency between module and
locked plan; committed-schedule reproducibility; event-identifier
determinism; plan-to-test group coverage (Q1-Q21 implemented, Q22 registered
but NOT executed); absence of actor/health/wallet modules; released V2.9
files unchanged relative to v2.9.0.

Directly executable: python3 audit_v30_quote.py  (exit 0 iff all checks pass)
"""
from __future__ import annotations
import ast
import hashlib
import json
import os
import subprocess
import sys

PLAN_PATH = "v30_quote_validation_plan.json"
PLAN_CANONICAL = "a1916e8ecf366cee93a5284a0d8fcb68a3e1a429f49ce62b9f5914df87f94061"
PLAN_RAW = "5f01a1fd554bfb2f5e684dc318a805f2887d51274e456c98d1a1d5788d1a6f4f"
V29_TAG = "v2.9.0"
V29_PEELED = "e1c6000f7b050e56e6fd0aa4b23e56c5d9e641d0"
RELEASED_V29 = ["d0_v29.py", "p1c_v29.py", "serialization_v29.py",
                "test_v29.py", "test_v29_behavior.py", "test_v29_p1c.py",
                "test_v29_d9_d10.py", "test_v29_serialization.py",
                "exp_v29.py", "exp_v29_d9_d10.py",
                "v29_deterministic_plan.json", "v29_d9_d10_plan.json"]

ALLOWED_MODULE_IMPORTS = {"__future__", "hashlib", "json", "math",
                          "dataclasses", "typing", "d0_v29"}
FORBIDDEN_IDENTIFIERS = {"V_total", "viability", "wallet", "wallets",
                         "health", "price", "prices", "rollout", "debt",
                         "needs", "transfer", "transfers", "phase_map"}

PASS = FAIL = 0


def check(cond: bool, label: str) -> None:
    global PASS, FAIL
    mark = "ok " if cond else "FAIL"
    print(f"  [{mark}] {label}")
    if cond:
        PASS += 1
    else:
        FAIL += 1


def module_ast(path):
    with open(path) as f:
        return ast.parse(f.read())


def imports_and_names(tree):
    imports, names = set(), set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom):
            imports.add((node.module or "").split(".")[0])
        elif isinstance(node, ast.Attribute):
            names.add(node.attr)
        elif isinstance(node, ast.Name):
            names.add(node.id)
    return imports, names


def main() -> int:
    print("V3.0 Gate 1B quote audit (read-only)")

    print("[1] plan hash lock")
    raw = open(PLAN_PATH, "rb").read()
    check(hashlib.sha256(raw).hexdigest() == PLAN_RAW, "raw plan SHA-256")
    plan = json.loads(raw)
    canon = hashlib.sha256(json.dumps(plan, sort_keys=True,
                                      separators=(",", ":"),
                                      ensure_ascii=True).encode()).hexdigest()
    check(canon == PLAN_CANONICAL, "canonical plan hash")

    print("[2] implementation/test independence and information boundary")
    mtree = module_ast("ebu_quote_v30.py")
    mimports, mnames = imports_and_names(mtree)
    check(mimports <= ALLOWED_MODULE_IMPORTS,
          f"module imports within allowlist ({sorted(mimports)})")
    check(not any(m.startswith("test_") or m.startswith("exp_")
                  or m.startswith("audit_") for m in mimports),
          "module never imports test/exp/audit modules")
    hits = mnames & FORBIDDEN_IDENTIFIERS
    check(not hits, f"no forbidden global-information identifiers (hits: {sorted(hits)})")
    ttree = module_ast("test_v30_quote.py")
    timports, _ = imports_and_names(ttree)
    check("ebu_v26" not in timports and "exp_v26" not in timports,
          "test suite does not import the V2.6 adversary (Q22 not executed)")

    print("[3] strict serialization (fail closed)")
    sys.path.insert(0, os.getcwd())
    import ebu_quote_v30 as eqm
    try:
        eqm.canonical_json(float("nan"))
        check(False, "canonical_json rejects NaN")
    except ValueError:
        check(True, "canonical_json rejects NaN")
    try:
        eqm.canonical_json(float("inf"))
        check(False, "canonical_json rejects Infinity")
    except ValueError:
        check(True, "canonical_json rejects Infinity")

    print("[4] equation-version consistency")
    check(eqm.EQUATION_VERSION == plan["quote_law"]["version"],
          f"module EQUATION_VERSION == plan quote_law.version "
          f"({eqm.EQUATION_VERSION})")

    print("[5] committed-schedule reproducibility and event-id determinism")
    import d0_v29 as d0m

    def build():
        inp = eqm.LocalQuoteInput(
            src=d0m.LocalView(x=18.0, alpha=1.0, beta=1.0, chi=0.0, L=4.0,
                              U=16.0, R=0.0, K=24.0),
            dst=d0m.LocalView(x=2.0, alpha=1.0, beta=1.0, chi=0.0, L=4.0,
                              U=16.0, R=0.0, K=24.0),
            u_src=0.0, u_dst=0.0, dt=1.0, eta=0.9, q_req=2.0, q_acc=2.0,
            source_id=0, dest_id=1, config_id="cfg:audit")
        cost = eqm.ProcessCost(category=eqm.ALLOWED_COST_CATEGORY, c1=0.01)
        return eqm.build_quote(inp, cost, "audit-pass", 0, 0)
    s1, s2 = build(), build()
    check(s1.epoch.epoch_id == s2.epoch.epoch_id,
          "event/epoch identifier deterministic")
    check(all(s1.exact(q) == s2.exact(q) for q in (0.0, 0.5, 1.0, 2.0)),
          "schedule reproducible from committed parameters")
    check(eqm.epoch_identifier(s1.epoch) == s1.epoch.epoch_id,
          "epoch id re-derivable from bound fields")
    check(abs(s1.exact(2.0) - 7.94) <= 1e-9 * (1 + 7.94),
          "E1 committed value reproduced (+7.94)")

    print("[6] plan-to-test group coverage")
    tsrc = open("test_v30_quote.py").read()
    missing = [g for g in plan["groups"] if g != "Q22"
               and f"def test_{g.lower()}" not in tsrc]
    check(not missing, f"all conformance groups implemented (missing: {missing})")
    check("Q22" in plan["groups"], "Q22 registered in the locked plan")
    check("NOT RUN" in tsrc or "NOT run" in tsrc,
          "test suite states Q22 is not executed")

    print("[7] actor/health/wallet modules absent")
    offenders = [f for f in os.listdir(".")
                 if f.endswith(".py") and any(k in f.lower() for k in
                 ("actor", "wallet", "health", "market", "price"))]
    check(not offenders, f"no actor-economy modules exist ({offenders})")

    print("[8] released V2.9 files unchanged relative to v2.9.0")
    r = subprocess.run(["git", "diff", "--name-only", V29_PEELED, "HEAD",
                        "--"] + RELEASED_V29,
                       capture_output=True, text=True)
    changed = [ln for ln in r.stdout.splitlines() if ln.strip()]
    check(r.returncode == 0 and not changed,
          f"released V2.9 files unchanged (changed: {changed})")
    t = subprocess.run(["git", "rev-parse", V29_TAG + "^{}"],
                       capture_output=True, text=True)
    check(t.stdout.strip() == V29_PEELED, "v2.9.0 still peels to the baseline")

    print(f"\naudit totals: {PASS} passed, {FAIL} failed")
    print("This audit is read-only validation; it proves nothing and runs "
          "no behavioral trajectory or adversary.")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
