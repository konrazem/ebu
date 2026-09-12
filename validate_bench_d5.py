#!/usr/bin/env python3
"""Static validator for the D5 micro-benchmark harness and its brief.

Reads `bench_d5_kernel.py` and the D5 brief as TEXT and analyses the harness
with `ast`. It never imports the harness, never executes it, and never runs a
benchmark cell. Syntax is checked with `compile(..., "exec")`, which compiles
without executing and writes no bytecode file.

Exit code 0 means every static boundary check passed.
"""
from __future__ import annotations

import ast
import os
import sys

HARNESS = "bench_d5_kernel.py"
BRIEF = "V3.0_D5_MICROBENCHMARK_AUTHORIZATION_BRIEF.md"

ALLOWED_STDLIB = {
    "__future__", "argparse", "ast", "hashlib", "json", "os", "platform",
    "statistics", "subprocess", "sys", "time", "zlib", "tracemalloc",
    "resource",
}
ALLOWED_KERNEL = {"d0_v29", "ebu_quote_v30"}
DENY_MODULES = {"gate1dc_v30", "exp_v30_gate1dc", "finalize_v30_gate1dc",
                "service_v30", "p1c_v29"}
DENY_FUNCTIONS = {
    "bounded_step", "classify_outcome", "p1c_step", "classify_state",
    "robust_budget", "build_world", "load_plan", "validate_plan",
    "world_certificates", "demand_rate_for_tick", "candidate_menu",
    "screen_budget", "select_arm_B", "select_arm_D", "select_arm_S",
    "gate1dc_tick", "run_arm", "group_quote_diagnostic",
    "threshold_diagnostics", "discriminator_v2_channels",
    "per_destination_alignment_predicate", "linear_diagnostic", "World",
}
CONST_HOLDERS = {"DENY_MODULES", "DENY_FUNCTIONS", "FORBIDDEN_ROOT",
                 "FORBIDDEN_OUTPUT_KEYS", "CREDENTIAL_MARKERS",
                 "HOME_PREFIXES"}
TIMED_FUNCTIONS = {"_time_body", "_cell_time_unit", "_cell_time_record"}
INSTRUMENTATION = {"tracemalloc", "resource", "setprofile", "settrace",
                   "addaudithook"}
ALLOWED_OUTPUT_ROOT = "results/benchmarks/d5"
FORBIDDEN_ROOT = "results/v3.0"

CHECKS = []
FAILURES = []


def record(ok, label, detail=""):
    CHECKS.append((bool(ok), label, detail))
    if not ok:
        FAILURES.append(label)


def protected_const_ids(tree):
    protected = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            names = {t.id for t in node.targets if isinstance(t, ast.Name)}
            if names & CONST_HOLDERS:
                for sub in ast.walk(node.value):
                    protected.add(id(sub))
    return protected


def enclosing_functions(tree, predicate):
    """Names of FunctionDefs whose subtree contains a node matching predicate."""
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for sub in ast.walk(node):
                if predicate(sub):
                    found.add(node.name)
                    break
    return found


def main():
    path = os.path.abspath(HARNESS)
    if not os.path.exists(path):
        record(False, "harness file exists", path)
        return report()
    source = open(path, "r", encoding="utf-8").read()

    try:
        compile(source, path, "exec")
        record(True, "syntax compiles (compile(), not exec)")
    except SyntaxError as err:
        record(False, "syntax compiles", str(err))
        return report()

    tree = ast.parse(source, filename=path)
    protected = protected_const_ids(tree)
    names = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}

    # ---- import boundary --------------------------------------------------
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    unexpected = imported - ALLOWED_STDLIB - ALLOWED_KERNEL
    record(not unexpected, "imports restricted to stdlib + kernel",
           "unexpected: %s" % sorted(unexpected) if unexpected
           else "imports: %s" % sorted(imported))
    record(not (imported & DENY_MODULES), "no deny-listed module imported")

    # ---- deny-listed symbols ---------------------------------------------
    hits = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr in DENY_FUNCTIONS:
            hits.add("attribute %s" % node.attr)
        elif isinstance(node, ast.Name) and node.id in DENY_FUNCTIONS:
            hits.add("name %s" % node.id)
    record(not hits, "no deny-listed function or class referenced",
           "; ".join(sorted(hits)))

    record(not [n for n in ast.walk(tree)
                if isinstance(n, (ast.Global, ast.Nonlocal))],
           "no global/nonlocal declaration (P5 support)")

    world_calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
                   and ((isinstance(n.func, ast.Attribute)
                         and n.func.attr in ("World", "Cell", "Edge"))
                        or (isinstance(n.func, ast.Name)
                            and n.func.id in ("World", "Cell", "Edge")))]
    record(not world_calls, "no World/Cell/Edge constructed (P4)")

    # ---- path literals ----------------------------------------------------
    bad = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if "results/" in node.value and id(node) not in protected \
                    and not node.value.startswith(ALLOWED_OUTPUT_ROOT):
                bad.append(node.value)
    record(not bad, "output path literals only below %s (P3)"
           % ALLOWED_OUTPUT_ROOT, "bad: %s" % bad)

    # ---- C4: no monkey-patching anywhere; profiler only in the audit cell --
    patchers = enclosing_functions(
        tree, lambda s: isinstance(s, ast.Assign)
        and any(isinstance(t, ast.Attribute) for t in s.targets))
    record(not patchers, "no monkey-patching anywhere in the harness (C4)",
           "sites: %s" % sorted(patchers))
    profilers = enclosing_functions(
        tree, lambda s: isinstance(s, ast.Attribute)
        and s.attr in ("setprofile", "settrace", "addaudithook"))
    record(profilers <= {"_cell_audit"},
           "profiler confined to the untimed audit cell (C4)",
           "sites: %s" % sorted(profilers))
    timed_hits = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in TIMED_FUNCTIONS:
            for sub in ast.walk(node):
                if isinstance(sub, ast.Name) and sub.id in INSTRUMENTATION:
                    timed_hits.add("%s->%s" % (node.name, sub.id))
                if isinstance(sub, ast.Attribute) and sub.attr in INSTRUMENTATION:
                    timed_hits.add("%s->.%s" % (node.name, sub.attr))
    record(not timed_hits, "timed cells remain entirely uninstrumented",
           "; ".join(sorted(timed_hits)))
    for key in ("calls_commitment_hash", "calls_canonical_json_total",
                "calls_canonical_json_nested_in_commitment_hash",
                "calls_canonical_json_direct"):
        record(key in source, "audit reports %s" % key)

    # ---- C1: interpreter identity, never an absolute path -----------------
    record("interpreter_basename" in source and "interpreter_sha256" in source,
           "environment records interpreter basename + SHA-256 (C1)")
    record("executable_realpath" not in source
           and "REDACTED_INTERPRETER" not in source,
           "no executable realpath field anywhere (C1)")
    record("os.path.basename(path)" in source,
           "interpreter path reduced to a basename before output (C1)")

    # ---- C2: explicit launcher mode ---------------------------------------
    record("_require_launcher_mode" in names,
           "explicit launcher-mode guard present (C2)")
    record("len(os.environ)" not in source,
           "no environment-size inference of launcher mode (C2)")
    record('LAUNCHER_MODES = ("minimal-env", "normal-shell")' in source,
           "launcher modes are exactly minimal-env / normal-shell (C2)")
    record("required=True" in source and "--launcher-mode" in source,
           "harness refuses to run without --launcher-mode (C2)")
    spawn_prop = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_spawn":
            for sub in ast.walk(node):
                if isinstance(sub, ast.Constant) and sub.value == "--launcher-mode":
                    spawn_prop = True
    record(spawn_prop, "declared label propagated into every subprocess (C2)")

    # ---- C3: E-settled at m = 1 -------------------------------------------
    record('JOINT_NOT_APPLICABLE = "NOT_APPLICABLE_M_EQUALS_1"' in source,
           "joint interaction marker defined (C3)")
    record("record[\"joint_interaction\"] = JOINT_NOT_APPLICABLE" in source,
           "m = 1 record marked NOT_APPLICABLE, not zero-filled (C3)")
    zero_triple = ('record["group_quote"] = 0.0' in source
                   or 'record["naive_sum"] = 0.0' in source
                   or 'record["double_count"] = 0.0' in source)
    record(not zero_triple, "no invented zero-valued triple (C3)")

    # ---- C5: settlement preflight -----------------------------------------
    record("_preflight_settlement" in names, "settlement preflight present (C5)")
    record('status != "settled"' in source,
           "preflight requires a settled status (C5)")
    order_ok = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_cell_time_record":
            pre = [s.lineno for s in ast.walk(node) if isinstance(s, ast.Call)
                   and isinstance(s.func, ast.Name)
                   and s.func.id == "_preflight_settlement"]
            tim = [s.lineno for s in ast.walk(node) if isinstance(s, ast.Call)
                   and isinstance(s.func, ast.Name) and s.func.id == "_time_body"]
            order_ok = bool(pre) and bool(tim) and min(pre) < min(tim)
    record(order_ok, "preflight runs before timing in the E-settled cell (C5)")
    mem_order = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_cell_memory":
            pre = [c.lineno for c in ast.walk(node) if isinstance(c, ast.Call)
                   and isinstance(c.func, ast.Name)
                   and c.func.id == "_preflight_settlement"]
            rec = [c.lineno for c in ast.walk(node) if isinstance(c, ast.Call)
                   and isinstance(c.func, ast.Name)
                   and c.func.id == "_build_record"]
            trc = [a.lineno for a in ast.walk(node) if isinstance(a, ast.Attribute)
                   and a.attr == "start"]
            mem_order = (bool(pre) and bool(rec) and min(pre) < min(rec)
                         and (not trc or min(pre) < min(trc)))
    record(mem_order, "memory cell preflights before tracemalloc and before "
                      "the first record (C1-final)")
    record("no timing result" not in source
           and "no measurement result" in source,
           "failure wording covers time and memory (C2-final)")

    # ---- C6: declared measurement controls --------------------------------
    record("WARMUP_BODIES = 3" in source and "REPETITIONS = 15" in source
           and "INNER_OPS = 1000" in source,
           "controls declared: warm-up 3, reps 15, inner 1000 (C6)")
    record("not future-study parameters" in source,
           "controls declared non-scientific in the harness (C6)")

    # ---- boundaries and grid ----------------------------------------------
    required = ["_p1_module_table", "_p2_self_scan", "_p3_guard_output",
                "_p4_no_world", "_p5_spec_unchanged", "_p6_no_ebu",
                "_p7_schema", "_p8_environment"]
    missing = [r for r in required if r not in names]
    record(not missing, "boundaries P1-P8 implemented", "missing: %s" % missing)
    record("BoundaryFailure" in source and "return 2" in source,
           "P9: boundary failure exits non-zero without a summary")
    record("(1, 2, 4, 8, 16, 32)" in source and "GRID_M = (1, 2)" in source
           and '"E-none", "E-full", "E-settled"' in source,
           "grid K/m/policy unchanged")
    # ---- retention correction: run directories, raw samples, binding ------
    record("LEGACY_SUMMARY" in source
           and "preserved predecessor summary is never a write target" in source,
           "root-level predecessor is guarded, never a write target (R1)")
    record("root-level output is forbidden" in source,
           "root-level output forbidden; writes go beneath a run dir (R1)")
    record("_validate_run_id" in names and "_guard_run_directory" in names,
           "run-id validation and run-directory guard present (R2)")
    traversal = all(token in source for token in
                    ('".." in run_id', "os.sep in run_id", "isascii()",
                     "RUN_ID_MAX_LENGTH", "run_id[0] in \"-.\""))
    record(traversal, "run identifier checked against traversal (R2)")
    record("run directory already exists" in source
           and "os.path.dirname(target) != root" in source,
           "existing run directory refused; no escape from the root (R2)")
    record('SUMMARY_BASENAME = "d5_summary.json"' in source
           and 'RAW_BASENAME = "d5_raw_samples.jsonl"' in source,
           "both output basenames declared (R3)")
    record("both the raw-sample file and the summary are required" in source,
           "run fails unless both files exist (R3)")
    writes = [c for c in ast.walk(tree) if isinstance(c, ast.Call)
              and isinstance(c.func, ast.Name) and c.func.id == "open"
              and any(isinstance(a, ast.Constant) and a.value == "w"
                      for a in c.args)]
    record(len(writes) >= 2, "harness opens both outputs for writing (R3)",
           "write-mode open() calls: %d" % len(writes))
    record("RAW_KEYS" in source and "FORBIDDEN_RAW_KEYS" in source
           and "_p10_raw_schema" in names,
           "raw schema allow-list and P10 present (R4)")
    for banned in ("group_quote", "naive_sum", "double_count", "settlement",
                   "outcome_class", "world"):
        record('"%s"' % banned in source.split("FORBIDDEN_RAW_KEYS")[1]
               .split(")")[0],
               "raw schema excludes %s (R4)" % banned)
    record("must be scalar" in source,
           "raw values restricted to scalars (R4)")
    record("_p11_raw_binding" in names and "raw_samples_sha256" in source
           and "raw_samples_file" in source,
           "summary binds the raw file by SHA-256 (R5)")
    binding_ok = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_orchestrate":
            keys = [c.value for c in ast.walk(node)
                    if isinstance(c, ast.Constant) and isinstance(c.value, str)]
            binding_ok = ("raw_samples_sha256" in keys
                          and "raw_samples_file" in keys
                          and "raw_samples_records" in keys)
    record(binding_ok, "orchestrator writes the binding fields (R5)")

    # ---- brief / harness agreement (text inspection only) -----------------
    if os.path.exists(BRIEF):
        brief = open(BRIEF, "r", encoding="utf-8").read()
        record("Interpreter basename" in brief and "Interpreter SHA-256" in brief
               and "Executable realpath" not in brief,
               "brief C1: interpreter identity replaces realpath")
        record("`--launcher-mode`" in brief and "Never inferred" in brief,
               "brief C2: explicit launcher mode required")
        record("NOT_APPLICABLE_M_EQUALS_1" in brief,
               "brief C3: m = 1 marker specified")
        record("non-invasive" in brief and "counting shim" not in brief,
               "brief C4: profiler replaces the counting shim")
        record("Settlement-path preflight" in brief,
               "brief C5: settlement preflight specified")
        record("Warm-up: 3 bodies" in brief and "Repetitions: 15" in brief
               and "Inner operations: 1,000" in brief
               and "non-scientific measurement controls" in brief,
               "brief C6: controls declared non-scientific")
        record("timing and memory cells" in brief.replace("\n", " ")
               or "timing **and memory** cells" in brief,
               "brief: preflight covers timing AND memory cells (C1-final)")
        start = brief.index("## 11.")
        end = brief.index("\n---", start)
        lines = [ln[2:] if ln.startswith("> ") else ln
                 for ln in brief[start:end].splitlines()]
        block = " ".join(" ".join(lines).split())
        required = [
            "--launcher-mode minimal-env", "--launcher-mode normal-shell",
            "fresh subprocess", "entirely uninstrumented",
            "non-invasive profiler", "never monkey-patching",
            "settlement preflight before every", "timing or memory cell",
            "no measurement result", "restricted non-sensitive environment",
            "no world", "no trajectory", "no state progression",
            "no scientific output", "no AWS action", "no Docker action",
            "no commit or push",
        ]
        absent = [phrase for phrase in required if phrase not in block]
        record(not absent, "brief section 11 authorization sentence complete "
                           "(C3-final)", "missing: %s" % absent)
        flat = " ".join(brief.split())
        record("preserved byte-identically as a nonconforming predecessor" in flat
               and "summary statistics only" in flat,
               "brief: predecessor preserved, summary-only (R6)")
        record("d5_raw_samples.jsonl" in flat
               and "every raw non-scientific observation" in flat,
               "brief: future runs retain raw observations (R6)")
        record("non-scientific and permitted" in flat
               and "new run identifier" in flat
               and "never overwrite prior output" in flat,
               "brief: rerun permitted, new run-id, no overwrite (R6)")
        record("| P10 |" in brief and "| P11 |" in brief,
               "brief: P10 and P11 boundaries documented (R6)")
        record("--run-id" in block and "d5_raw_samples.jsonl" in block,
               "brief section 11 requires run-id and both files (R6)")
    else:
        record(False, "brief present", BRIEF)

    # ---- validator self-proof: never imports the harness or an EBU module --
    self_source = open(os.path.abspath(__file__), "r", encoding="utf-8").read()
    self_tree = ast.parse(self_source)
    self_imports = set()
    for node in ast.walk(self_tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                self_imports.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            self_imports.add(node.module.split(".")[0])
    record(self_imports <= {"__future__", "ast", "os", "sys"},
           "validator imports only ast/os/sys",
           "imports: %s" % sorted(self_imports))
    record(not (self_imports & (ALLOWED_KERNEL | DENY_MODULES
                                | {"bench_d5_kernel"})),
           "validator never imports the harness or any EBU module")
    record(not [c for c in ast.walk(self_tree) if isinstance(c, ast.Call)
                and isinstance(c.func, ast.Name)
                and c.func.id in ("exec", "eval", "__import__")],
           "validator never exec/eval/__import__s anything")
    return report()


def report():
    width = max(len(label) for _ok, label, _d in CHECKS)
    for ok, label, detail in CHECKS:
        sys.stdout.write("  %-4s %-*s  %s\n"
                         % ("PASS" if ok else "FAIL", width, label, detail))
    sys.stdout.write("\n%d checks, %d failures\n" % (len(CHECKS), len(FAILURES)))
    return 1 if FAILURES else 0


if __name__ == "__main__":
    raise SystemExit(main())
