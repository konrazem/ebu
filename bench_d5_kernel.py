#!/usr/bin/env python3
"""D5 micro-benchmark harness - NON-SCIENTIFIC SOFTWARE MEASUREMENT.

Implements the design frozen in V3.0_D5_MICROBENCHMARK_AUTHORIZATION_BRIEF.md.

THIS HARNESS IS NOT AUTHORIZED TO RUN. Execution requires the exact
authorization sentence in section 11 of that brief.

It measures software overhead only: arithmetic, canonical serialization,
SHA-256 commitment cost, record bytes, and retained memory. It never measures
or reports EBU quality, alignment, homeostasis, reserves, service, recovery,
robustness, or scientific success. It constructs no world, advances no state,
selects no action, and runs no trajectory.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import platform
import statistics
import subprocess
import sys
import time

# ---------------------------------------------------------------------------
# boundary constants (P1-P9). The deny-list strings live ONLY here.
# ---------------------------------------------------------------------------
DENY_MODULES = (
    "gate1dc_v30", "exp_v30_gate1dc", "finalize_v30_gate1dc",
    "service_v30", "p1c_v29",
)
DENY_FUNCTIONS = (
    "bounded_step", "classify_outcome", "p1c_step", "classify_state",
    "robust_budget", "build_world", "load_plan", "validate_plan",
    "world_certificates", "demand_rate_for_tick", "candidate_menu",
    "screen_budget", "select_arm_B", "select_arm_D", "select_arm_S",
    "gate1dc_tick", "run_arm", "group_quote_diagnostic",
    "threshold_diagnostics", "discriminator_v2_channels",
    "per_destination_alignment_predicate", "linear_diagnostic", "World",
)
ALLOWED_KERNEL_MODULES = ("d0_v29", "ebu_quote_v30")
OUTPUT_ROOT = "results/benchmarks/d5"
FORBIDDEN_ROOT = "results/v3.0"
# The first D5 run wrote a summary-only file at the output root. It is a
# preserved, nonconforming predecessor and is never a write target again.
LEGACY_SUMMARY = "results/benchmarks/d5/d5_summary.json"
SUMMARY_BASENAME = "d5_summary.json"
RAW_BASENAME = "d5_raw_samples.jsonl"
RUN_ID_MAX_LENGTH = 64

# ---------------------------------------------------------------------------
# frozen synthetic inputs (brief section 2)
#
# Arbitrary round numbers chosen for BRANCH COVERAGE of penalty() and cost().
# beta=0.25, U=16.0 and K=32.0 appear in no registered V3 cell, so no synthetic
# view can correspond to a registered one. No value was chosen by inspecting a
# Gate 1D-C outcome. None of these numbers carries physical meaning.
# ---------------------------------------------------------------------------
SYNTH_VIEWS = (
    ("below_L", {"x": 1.0, "alpha": 2.0, "beta": 0.25, "chi": 0.0,
                 "L": 4.0, "U": 16.0, "R": 0.0, "K": 32.0}),
    ("flat", {"x": 9.0, "alpha": 2.0, "beta": 0.25, "chi": 0.0,
              "L": 4.0, "U": 16.0, "R": 0.0, "K": 32.0}),
    ("above_U", {"x": 20.0, "alpha": 2.0, "beta": 0.25, "chi": 0.0,
                 "L": 4.0, "U": 16.0, "R": 0.0, "K": 32.0}),
    ("below_R", {"x": 1.0, "alpha": 2.0, "beta": 0.25, "chi": 3.0,
                 "L": 4.0, "U": 16.0, "R": 2.0, "K": 32.0}),
)
SYNTH_DT = 0.25
SYNTH_ETA = 0.8
SYNTH_Q_LADDER = (0.0, 0.125, 0.5, 1.0, 2.0)
SYNTH_Q_REQ = 2.0
SYNTH_Q_ACC = 2.0
SYNTH_COST = {"c0": 0.5, "c1": 0.25, "c2": 0.125}
SYNTH_CONFIG_ID = "synthetic-benchmark-config"
SYNTH_PASS_ID = "synthetic-benchmark-pass"

GRID_K = (1, 2, 4, 8, 16, 32)
GRID_M = (1, 2)
GRID_POLICY = ("E-none", "E-full", "E-settled")
LAUNCHER_MODES = ("minimal-env", "normal-shell")
JOINT_NOT_APPLICABLE = "NOT_APPLICABLE_M_EQUALS_1"
UNIT_OPS = ("exact", "state_difference", "build_quote",
            "canonical_json", "commitment_hash")

# Non-scientific MEASUREMENT CONTROLS. They govern only how the overhead
# measurement is taken. They are not future-study parameters and select no
# scientific quantity.
WARMUP_BODIES = 3
REPETITIONS = 15
INNER_OPS = 1000
MEM_BASE_RECORDS = 64
MEM_DELTA_RECORDS = 64

# ---------------------------------------------------------------------------
# restricted environment allow-list (brief section 8)
# ---------------------------------------------------------------------------
ENV_FIELDS = ("os_name", "kernel_version", "cpu_model", "architecture",
              "python_version", "interpreter_basename", "interpreter_sha256",
              "zlib_version", "launcher_mode", "pythonhashseed",
              "omission_declaration")
OMISSION_DECLARATION = (
    "The absolute interpreter path is intentionally omitted to prevent "
    "home-directory disclosure; the interpreter is identified by basename "
    "and the SHA-256 of its bytes. All other environment values were "
    "intentionally omitted to prevent credential leakage.")
CREDENTIAL_MARKERS = ("AWS", "GITHUB", "SSO", "TOKEN", "KEY", "SECRET",
                      "CREDENTIAL", "PROXY", "PASSWORD")
HOME_PREFIXES = ("/Users/", "/home/", "/root/")

CELL_KEYS = (
    "kind", "op", "K", "m", "policy", "order",
    "ns_per_op_median", "ns_per_op_iqr", "ns_per_op_min", "ns_per_op_max",
    "ops_per_sec_median", "serialized_bytes_per_record", "candidate_count",
    "python_alloc_bytes_per_record", "python_alloc_bytes_per_candidate",
    "process_peak_rss_bytes", "rss_note", "joint_interaction",
    "calls_commitment_hash", "calls_canonical_json_total",
    "calls_canonical_json_nested_in_commitment_hash",
    "calls_canonical_json_direct", "audit_note",
)
RAW_KEYS = (
    "cell", "kind", "order", "op", "K", "m", "policy",
    "repetition", "duration_ns", "inner_ops",
    "traced_before_bytes", "traced_after_bytes", "base_records",
    "delta_records", "retained_bytes_per_record", "process_peak_rss_bytes",
    "calls_commitment_hash", "calls_canonical_json_total",
    "calls_canonical_json_nested_in_commitment_hash",
    "calls_canonical_json_direct",
)
FORBIDDEN_RAW_KEYS = (
    "ebu", "ebu_total", "quote_value", "exact_value", "group_quote",
    "naive_sum", "double_count", "settlement", "issued", "outcome_class",
    "world", "arm", "service", "unmet", "x_before", "x_after", "dt_label",
    "tick", "trajectory",
)
FORBIDDEN_OUTPUT_KEYS = (
    "ebu", "ebu_total", "quote_value", "exact_value", "group_quote",
    "naive_sum", "double_count", "settlement", "issued", "outcome_class",
)


class BoundaryFailure(RuntimeError):
    """Raised when any of P1-P8 fails. P9 turns this into a non-zero exit."""


# ---------------------------------------------------------------------------
# kernel access - the ONLY repository modules this harness may import
# ---------------------------------------------------------------------------
def _load_kernel():
    import d0_v29
    import ebu_quote_v30
    return d0_v29, ebu_quote_v30


def _spec_fingerprint():
    payload = {
        "views": [[name, params] for name, params in SYNTH_VIEWS],
        "dt": SYNTH_DT, "eta": SYNTH_ETA,
        "q_ladder": list(SYNTH_Q_LADDER),
        "q_req": SYNTH_Q_REQ, "q_acc": SYNTH_Q_ACC, "cost": SYNTH_COST,
    }
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _build_views(d0):
    return [d0.LocalView(**params) for _name, params in SYNTH_VIEWS]


def _build_cost(eq):
    return eq.ProcessCost(category=eq.ALLOWED_COST_CATEGORY, **SYNTH_COST)


def _build_inputs(eq, views):
    inputs = []
    for index in range(len(views)):
        inputs.append(eq.LocalQuoteInput(
            src=views[index], dst=views[(index + 1) % len(views)],
            u_src=0.0, u_dst=0.0, dt=SYNTH_DT, eta=SYNTH_ETA,
            q_req=SYNTH_Q_REQ, q_acc=SYNTH_Q_ACC,
            source_id=0, dest_id=index + 1, config_id=SYNTH_CONFIG_ID))
    return inputs


def _build_schedules(eq, inputs, cost):
    return [eq.build_quote(inp, cost, SYNTH_PASS_ID, 0, 0) for inp in inputs]


def _synthetic_candidates(k):
    return [{"edge": index % 4, "quant_index": index, "frac": 0.25,
             "f": 1.0, "J": 1.0, "q_req": SYNTH_Q_REQ,
             "q_e_max": SYNTH_Q_ACC, "q_acc": SYNTH_Q_ACC}
            for index in range(k)]


def _joint_record_replica(d0, views, schedules, m):
    """DECLARED CALL-PATTERN REPLICA of the joint-record computation.

    This is NOT the registered joint-quote function, which lives in a module
    this harness may not import. It reproduces only the primitive composition:
    one `before` sum and one `after` sum of penalties over the involved
    synthetic views, plus the individual exact evaluations that would form a
    naive sum. Every value it returns is discarded by the caller.
    """
    involved = views[:m + 1]
    before = 0.0
    for view in involved:
        before += d0.penalty(view.alpha, view.beta, view.chi,
                             view.L, view.U, view.R, view.x)
    after = 0.0
    for index, view in enumerate(involved):
        if index == 0:
            shifted = view.x - SYNTH_DT * SYNTH_Q_ACC
        else:
            shifted = view.x + SYNTH_DT * SYNTH_ETA * SYNTH_Q_ACC
        after += d0.penalty(view.alpha, view.beta, view.chi,
                            view.L, view.U, view.R, shifted)
    process = SYNTH_COST["c1"] * SYNTH_Q_ACC * m
    group = before - after - process
    naive = 0.0
    for index in range(m):
        naive += schedules[index % len(schedules)].exact(SYNTH_Q_ACC)
    return group, naive, naive - group


def _build_record(eq, d0, views, schedules, cost, k, m, policy):
    """Build one synthetic evidence record and return it.

    Record shape follows `m`: per-cell arrays have length m+1 and per-edge
    arrays length m. These are RECORD-SHAPE lengths implied by the selected
    maximum record shape; they are not a node count, an edge count, or any
    topology.
    """
    cells = m + 1
    edges = m
    record = {
        "provenance": {
            "plan_canonical_hash": "0" * 64, "plan_raw_sha256": "0" * 64,
            "equation_version": "synthetic", "implementation_sha256": "0" * 64,
            "execution_sha": "0" * 40, "run_id": "synthetic-cell",
            "world": "synthetic", "arm": "synthetic", "dt_label": "synthetic",
        },
        "tick": 0,
        "x_before": [0.0] * cells,
        "x_after": [0.0] * cells,
        "u": [0.0] * cells,
        "available": [0.0] * cells,
        "service": [0.0] * cells,
        "unmet": [0.0] * cells,
        "demand_amount": [0.0] * cells,
        "negative_corrections": [0.0] * cells,
        "executed_q_acc": [0.0] * edges,
        "delivered": [0.0] * edges,
        "active_out_edges": [0] * edges,
        "menus": {"0": {"candidates": _synthetic_candidates(k)}},
    }
    if policy == "E-full":
        record["candidate_commitments"] = [
            eq.build_quote(schedules[index % len(schedules)].inp, cost,
                           SYNTH_PASS_ID, 0, 0).epoch.epoch_id
            for index in range(k)]
    elif policy == "E-settled":
        settled = []
        for index in range(m):
            schedule = schedules[index % len(schedules)]
            registry = eq.EpochRegistry()
            registry.register(schedule)
            registry.settle(schedule, SYNTH_Q_ACC, 0, 0)
            settled.append(schedule.epoch.epoch_id)
            del registry
        record["settled_commitments"] = settled
        if m < 2:
            record["joint_interaction"] = JOINT_NOT_APPLICABLE
        else:
            group, naive, double = _joint_record_replica(
                d0, views, schedules, m)
            record["group_quote"] = float(group)
            record["naive_sum"] = float(naive)
            record["double_count"] = float(double)
    return record


def _preflight_settlement(eq, schedule):
    """Isolated, UNTIMED settlement-path preflight for E-settled cells.

    Uses a fresh in-memory registry, requires a `settled` status, and discards
    the registry immediately. Its contents are never written. If the synthetic
    inputs take any violation or rejection path the cell fails and produces no
    measurement result, neither timing nor memory.
    """
    registry = eq.EpochRegistry()
    registry.register(schedule)
    outcome = registry.settle(schedule, SYNTH_Q_ACC, 0, 0)
    status = getattr(outcome, "status", None)
    del registry
    if status != "settled":
        raise BoundaryFailure(
            "settlement preflight: synthetic inputs took a %r path; this "
            "E-settled cell produces no measurement result" % (status,))
    return status


# ---------------------------------------------------------------------------
# timed cells - UNINSTRUMENTED. No counters, tracing, patching, or hooks here.
# ---------------------------------------------------------------------------
def _time_body(body):
    for _ in range(WARMUP_BODIES):
        body()
    samples = []
    for _ in range(REPETITIONS):
        start = time.perf_counter_ns()
        body()
        samples.append(time.perf_counter_ns() - start)
    return samples


def _cell_identity(kind, op=None, k=None, m=None, policy=None):
    parts = [kind]
    if op is not None:
        parts.append("op=%s" % op)
    if k is not None:
        parts.append("K=%d" % k)
    if m is not None:
        parts.append("m=%d" % m)
    if policy is not None:
        parts.append("policy=%s" % policy)
    return "|".join(parts)


def _raw_timing_rows(identity, kind, samples, inner, fields):
    """One raw row per repetition; enough to recompute every summary."""
    rows = []
    for index, duration in enumerate(samples):
        row = {"cell": identity, "kind": kind, "repetition": index,
               "duration_ns": duration, "inner_ops": inner}
        row.update(fields)
        rows.append(row)
    return rows


def _timing_stats(samples, inner):
    per_op = sorted(sample / float(inner) for sample in samples)
    median = statistics.median(per_op)
    if len(per_op) >= 4:
        low = statistics.median(per_op[:len(per_op) // 2])
        high = statistics.median(per_op[(len(per_op) + 1) // 2:])
        iqr = high - low
    else:
        iqr = 0.0
    return {
        "ns_per_op_median": median,
        "ns_per_op_iqr": iqr,
        "ns_per_op_min": per_op[0],
        "ns_per_op_max": per_op[-1],
        "ops_per_sec_median": (1e9 / median) if median > 0 else 0.0,
    }


def _cell_time_unit(op):
    d0, eq = _load_kernel()
    views = _build_views(d0)
    cost = _build_cost(eq)
    inputs = _build_inputs(eq, views)
    schedules = _build_schedules(eq, inputs, cost)
    work = []
    for index in range(INNER_OPS):
        schedule = schedules[index % len(schedules)]
        work.append((schedule, schedule.inp, SYNTH_Q_LADDER[
            index % len(SYNTH_Q_LADDER)]))
    payload = {"kind": "synthetic", "a": 1.0, "b": "x" * 32, "c": [1, 2, 3]}

    if op == "exact":
        def body():
            for schedule, _inp, q in work:
                schedule.exact(q)
    elif op == "state_difference":
        def body():
            for schedule, _inp, q in work:
                schedule.state_difference(q)
    elif op == "build_quote":
        def body():
            for _schedule, inp, _q in work:
                eq.build_quote(inp, cost, SYNTH_PASS_ID, 0, 0)
    elif op == "canonical_json":
        def body():
            for _ in range(INNER_OPS):
                eq.canonical_json(payload)
    elif op == "commitment_hash":
        def body():
            for _ in range(INNER_OPS):
                eq.commitment_hash(payload)
    else:
        raise BoundaryFailure("unknown unit op %r" % (op,))

    samples = _time_body(body)
    identity = _cell_identity("time-unit", op=op)
    result = {"kind": "time-unit", "op": op}
    result.update(_timing_stats(samples, INNER_OPS))
    result["raw"] = _raw_timing_rows(identity, "time-unit", samples,
                                     INNER_OPS, {"op": op})
    return result


def _cell_time_record(k, m, policy):
    d0, eq = _load_kernel()
    views = _build_views(d0)
    cost = _build_cost(eq)
    inputs = _build_inputs(eq, views)
    schedules = _build_schedules(eq, inputs, cost)
    inner = max(1, INNER_OPS // max(1, k))
    if policy == "E-settled":
        _preflight_settlement(eq, schedules[0])

    def body():
        for _ in range(inner):
            _build_record(eq, d0, views, schedules, cost, k, m, policy)

    samples = _time_body(body)
    probe = _build_record(eq, d0, views, schedules, cost, k, m, policy)
    serialized = len(eq.canonical_json(probe).encode("utf-8"))
    del probe
    result = {"kind": "time-record", "K": k, "m": m, "policy": policy,
              "serialized_bytes_per_record": serialized,
              "candidate_count": k}
    if policy == "E-settled" and m < 2:
        result["joint_interaction"] = JOINT_NOT_APPLICABLE
    result.update(_timing_stats(samples, inner))
    result["raw"] = _raw_timing_rows(
        _cell_identity("time-record", k=k, m=m, policy=policy),
        "time-record", samples, inner, {"K": k, "m": m, "policy": policy})
    return result


# ---------------------------------------------------------------------------
# memory cell - UNTIMED, instrumented, and always in its own fresh process
# ---------------------------------------------------------------------------
def _cell_memory(k, m, policy):
    import resource
    import tracemalloc

    d0, eq = _load_kernel()
    views = _build_views(d0)
    cost = _build_cost(eq)
    inputs = _build_inputs(eq, views)
    schedules = _build_schedules(eq, inputs, cost)
    if policy == "E-settled":
        _preflight_settlement(eq, schedules[0])

    tracemalloc.start()
    base = [_build_record(eq, d0, views, schedules, cost, k, m, policy)
            for _ in range(MEM_BASE_RECORDS)]
    before = tracemalloc.get_traced_memory()[0]
    extra = [_build_record(eq, d0, views, schedules, cost, k, m, policy)
             for _ in range(MEM_DELTA_RECORDS)]
    after = tracemalloc.get_traced_memory()[0]
    tracemalloc.stop()
    retained = (after - before) / float(MEM_DELTA_RECORDS)
    del base, extra

    usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    rss_bytes = usage if sys.platform == "darwin" else usage * 1024
    result = {
        "kind": "memory", "K": k, "m": m, "policy": policy,
        "candidate_count": k,
        "python_alloc_bytes_per_record": retained,
        "python_alloc_bytes_per_candidate": (retained / k) if k else 0.0,
        "process_peak_rss_bytes": rss_bytes,
        "rss_note": ("process-level ceiling including interpreter, imported "
                     "modules, runtime arenas and allocator fragmentation; "
                     "never a per-record figure and never divided by record "
                     "count"),
    }
    if policy == "E-settled" and m < 2:
        result["joint_interaction"] = JOINT_NOT_APPLICABLE
    result["raw"] = [{
        "cell": _cell_identity("memory", k=k, m=m, policy=policy),
        "kind": "memory", "K": k, "m": m, "policy": policy,
        "traced_before_bytes": before, "traced_after_bytes": after,
        "base_records": MEM_BASE_RECORDS, "delta_records": MEM_DELTA_RECORDS,
        "retained_bytes_per_record": retained,
        "process_peak_rss_bytes": rss_bytes,
    }]
    return result


# ---------------------------------------------------------------------------
# audit cell - UNTIMED call-pattern audit, isolated in its own fresh process.
# It never shares a code path with a timed cell.
# ---------------------------------------------------------------------------
def _cell_audit():
    """UNTIMED call-pattern audit, isolated in its own fresh process.

    Uses a non-invasive profiler installed only here and removed before
    returning. No function is replaced, wrapped, or monkey-patched. Counts are
    Python-level function entries, never throughput.
    """
    d0, eq = _load_kernel()
    views = _build_views(d0)
    cost = _build_cost(eq)
    inputs = _build_inputs(eq, views)

    hash_code = eq.commitment_hash.__code__
    json_code = eq.canonical_json.__code__
    counts = {"hash": 0, "json_total": 0, "json_nested": 0}

    def profiler(frame, event, _arg):
        if event != "call":
            return
        code = frame.f_code
        if code is hash_code:
            counts["hash"] += 1
        elif code is json_code:
            counts["json_total"] += 1
            caller = frame.f_back
            if caller is not None and caller.f_code is hash_code:
                counts["json_nested"] += 1

    sys.setprofile(profiler)
    try:
        schedule = eq.build_quote(inputs[0], cost, SYNTH_PASS_ID, 0, 0)
        registry = eq.EpochRegistry()
        registry.register(schedule)
        registry.settle(schedule, SYNTH_Q_ACC, 0, 0)
        del registry
    finally:
        sys.setprofile(None)

    identity = _cell_identity("audit")
    counted = {
        "calls_commitment_hash": counts["hash"],
        "calls_canonical_json_total": counts["json_total"],
        "calls_canonical_json_nested_in_commitment_hash": counts["json_nested"],
        "calls_canonical_json_direct": (counts["json_total"]
                                        - counts["json_nested"]),
    }
    raw = [dict(counted, cell=identity, kind="audit")]
    return {
        "raw": raw,
        "kind": "audit",
        "calls_commitment_hash": counts["hash"],
        "calls_canonical_json_total": counts["json_total"],
        "calls_canonical_json_nested_in_commitment_hash": counts["json_nested"],
        "calls_canonical_json_direct": (counts["json_total"]
                                        - counts["json_nested"]),
        "audit_note": ("untimed Python-level call counts over one build_quote "
                       "plus one register and one settle. Each function entry "
                       "is counted exactly once. canonical_json entries whose "
                       "immediate caller is commitment_hash are reported as "
                       "their own partition, so nested calls are never double "
                       "counted and never ambiguous. Call counts, never "
                       "throughput."),
    }


# ---------------------------------------------------------------------------
# boundaries
# ---------------------------------------------------------------------------
def _p1_module_table():
    for name in DENY_MODULES:
        if name in sys.modules:
            raise BoundaryFailure("P1: forbidden module imported: %s" % name)
    return "P1 ok: no deny-listed module in the module table"


def _p2_self_scan(path=None):
    source_path = path or os.path.abspath(__file__)
    with open(source_path, "r", encoding="utf-8") as handle:
        source = handle.read()
    tree = ast.parse(source, filename=source_path)
    allowed_const_parents = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
            if set(targets) & {"DENY_MODULES", "DENY_FUNCTIONS",
                               "FORBIDDEN_ROOT", "FORBIDDEN_OUTPUT_KEYS",
                               "CREDENTIAL_MARKERS", "HOME_PREFIXES"}:
                for sub in ast.walk(node.value):
                    allowed_const_parents.add(id(sub))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root in DENY_MODULES:
                    raise BoundaryFailure("P2: import of %s" % root)
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            if root in DENY_MODULES:
                raise BoundaryFailure("P2: import from %s" % root)
        elif isinstance(node, ast.Attribute):
            if node.attr in DENY_FUNCTIONS:
                raise BoundaryFailure("P2: attribute %s" % node.attr)
        elif isinstance(node, ast.Name):
            if node.id in DENY_FUNCTIONS:
                raise BoundaryFailure("P2: name %s" % node.id)
        elif isinstance(node, (ast.Global, ast.Nonlocal)):
            raise BoundaryFailure(
                "P2/P5: global/nonlocal declaration present")
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            if id(node) in allowed_const_parents:
                continue
            if FORBIDDEN_ROOT in node.value:
                raise BoundaryFailure("P3: literal referencing %s"
                                      % FORBIDDEN_ROOT)
    return "P2 ok: no deny-listed import, name, attribute, or forbidden path"


def _p3_guard_output(path):
    root = os.path.abspath(OUTPUT_ROOT)
    frozen = os.path.abspath(FORBIDDEN_ROOT)
    target = os.path.abspath(path)
    if target == frozen or target.startswith(frozen + os.sep):
        raise BoundaryFailure("P3: target under the frozen results root")
    if target != root and not target.startswith(root + os.sep):
        raise BoundaryFailure("P3: target outside %s" % OUTPUT_ROOT)
    if target == os.path.abspath(LEGACY_SUMMARY):
        raise BoundaryFailure(
            "P3: the preserved predecessor summary is never a write target")
    if os.path.dirname(target) == root:
        raise BoundaryFailure(
            "P3: root-level output is forbidden; write beneath a run "
            "directory")
    return target


def _validate_run_id(run_id):
    """Validate an explicit benchmark run identifier against traversal."""
    if not isinstance(run_id, str) or not run_id:
        raise BoundaryFailure(
            "a benchmark run identifier is required and must be explicit")
    if len(run_id) > RUN_ID_MAX_LENGTH:
        raise BoundaryFailure("run identifier exceeds %d characters"
                              % RUN_ID_MAX_LENGTH)
    if not run_id.isascii():
        raise BoundaryFailure("run identifier must be ASCII")
    if run_id in (".", ".."):
        raise BoundaryFailure("run identifier must not be a path element")
    if run_id[0] in "-.":
        raise BoundaryFailure("run identifier must not start with '-' or '.'")
    if ".." in run_id or "/" in run_id or "\\" in run_id or os.sep in run_id:
        raise BoundaryFailure(
            "run identifier must not contain a path separator or '..'")
    for character in run_id:
        if not (character.isalnum() or character in "._-"):
            raise BoundaryFailure("run identifier has an illegal character")
    return run_id


def _guard_run_directory(run_id):
    """Resolve and guard the per-run output directory; never overwrite."""
    _validate_run_id(run_id)
    root = os.path.abspath(OUTPUT_ROOT)
    target = os.path.abspath(os.path.join(root, run_id))
    if os.path.dirname(target) != root:
        raise BoundaryFailure("P3: run directory escapes the output root")
    if target == root:
        raise BoundaryFailure("P3: run identifier resolves to the output root")
    if os.path.exists(target):
        raise BoundaryFailure(
            "P3: run directory already exists; prior output is never "
            "overwritten - choose a new run identifier")
    return target


def _p10_raw_schema(rows):
    for row in rows:
        for key, value in row.items():
            if key in FORBIDDEN_RAW_KEYS:
                raise BoundaryFailure("P10: forbidden raw key %r" % key)
            if key not in RAW_KEYS:
                raise BoundaryFailure("P10: raw key %r not in allow-list"
                                      % key)
            if isinstance(value, (dict, list, tuple)):
                raise BoundaryFailure(
                    "P10: raw value for %r must be scalar" % key)
    return "P10 ok: %d raw rows, allow-listed scalar keys only" % len(rows)


def _p11_raw_binding(summary, raw_path):
    with open(raw_path, "rb") as handle:
        digest = hashlib.sha256(handle.read()).hexdigest()
    if summary.get("raw_samples_file") != os.path.basename(raw_path):
        raise BoundaryFailure("P11: raw-sample file name is not bound")
    if summary.get("raw_samples_sha256") != digest:
        raise BoundaryFailure("P11: summary does not bind the raw-sample "
                              "file by SHA-256")
    return "P11 ok: summary binds %s by SHA-256" % os.path.basename(raw_path)


def _p4_no_world(path=None):
    """Prove by AST that no world object is ever constructed."""
    source_path = path or os.path.abspath(__file__)
    with open(source_path, "r", encoding="utf-8") as handle:
        tree = ast.parse(handle.read(), filename=source_path)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        name = (func.attr if isinstance(func, ast.Attribute)
                else func.id if isinstance(func, ast.Name) else "")
        if name in ("World", "Cell", "Edge"):
            raise BoundaryFailure("P4: %s() constructed" % name)
    return "P4 ok: no World/Cell/Edge constructor call in the harness"


def _p5_spec_unchanged(fingerprint):
    if _spec_fingerprint() != fingerprint:
        raise BoundaryFailure("P5: synthetic input spec changed during the run")
    return "P5 ok: synthetic spec fingerprint unchanged; no state carried"


def _p6_no_ebu(summary):
    def walk(node):
        if isinstance(node, dict):
            for key, value in node.items():
                if key.lower() in FORBIDDEN_OUTPUT_KEYS:
                    raise BoundaryFailure("P6: EBU-valued key %r in output"
                                          % key)
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)
    walk(summary)
    return "P6 ok: no EBU-valued field in output"


def _p7_schema(cells):
    for cell in cells:
        for key in cell:
            if key not in CELL_KEYS:
                raise BoundaryFailure("P7: output key %r not in allow-list"
                                      % key)
    return "P7 ok: every cell key is in the allow-list"


def _p8_environment(environment):
    if set(environment) != set(ENV_FIELDS):
        raise BoundaryFailure("P8: environment block is not exactly the "
                              "allow-list")
    for name, value in environment.items():
        if name == "omission_declaration":
            continue
        text = str(value)
        upper = text.upper()
        for marker in CREDENTIAL_MARKERS:
            if marker in upper:
                raise BoundaryFailure("P8: %s contains %r" % (name, marker))
        for prefix in HOME_PREFIXES:
            if text.startswith(prefix):
                raise BoundaryFailure("P8: %s looks like a home path" % name)
    return "P8 ok: environment block is the restricted allow-list only"


# ---------------------------------------------------------------------------
# environment identity (restricted allow-list only; brief section 8)
# ---------------------------------------------------------------------------
def _cpu_model():
    try:
        system = platform.system()
        if system == "Darwin":
            done = subprocess.run(
                ["/usr/sbin/sysctl", "-n", "machdep.cpu.brand_string"],
                capture_output=True, text=True, timeout=5, check=False)
            if done.returncode == 0 and done.stdout.strip():
                return done.stdout.strip()[:128]
        elif system == "Linux":
            with open("/proc/cpuinfo", "r", encoding="utf-8") as handle:
                for line in handle:
                    if line.startswith("model name"):
                        return line.split(":", 1)[1].strip()[:128]
    except Exception:
        pass
    return platform.processor() or "unavailable"


def _interpreter_identity():
    """Non-sensitive executable identity: basename plus SHA-256 of its bytes.

    The absolute path is read locally to hash the file and is never returned,
    logged, or written, so no home-directory location can be disclosed.
    """
    path = os.path.realpath(sys.executable)
    basename = os.path.basename(path)
    try:
        digest = hashlib.sha256()
        with open(path, "rb") as handle:
            while True:
                chunk = handle.read(1 << 20)
                if not chunk:
                    break
                digest.update(chunk)
        return basename, digest.hexdigest()
    except OSError:
        return basename, "unavailable"


def _require_launcher_mode(value):
    """Refuse to run unless the launcher mode was declared explicitly."""
    if value not in LAUNCHER_MODES:
        raise BoundaryFailure(
            "launcher mode must be declared explicitly as one of %s; it is "
            "never inferred from environment size or contents"
            % (LAUNCHER_MODES,))
    return value


def _environment_identity(launcher_mode):
    import zlib
    _require_launcher_mode(launcher_mode)
    basename, digest = _interpreter_identity()
    seed = os.environ.get("PYTHONHASHSEED")
    return {
        "os_name": platform.system(),
        "kernel_version": platform.release(),
        "cpu_model": _cpu_model(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "interpreter_basename": basename,
        "interpreter_sha256": digest,
        "zlib_version": zlib.ZLIB_VERSION,
        "launcher_mode": launcher_mode,
        "pythonhashseed": seed if seed is not None else "not explicitly set",
        "omission_declaration": OMISSION_DECLARATION,
    }


# ---------------------------------------------------------------------------
# grid and orchestration
# ---------------------------------------------------------------------------
def _grid():
    cells = [{"kind": "time-unit", "op": op} for op in UNIT_OPS]
    for k in GRID_K:
        for m in GRID_M:
            for policy in GRID_POLICY:
                cells.append({"kind": "time-record", "K": k, "m": m,
                              "policy": policy})
                cells.append({"kind": "memory", "K": k, "m": m,
                              "policy": policy})
    cells.append({"kind": "audit"})
    return cells


def _spawn(cell, launcher_mode):
    _require_launcher_mode(launcher_mode)
    argv = [sys.executable, "-B", os.path.abspath(__file__),
            "--mode", "cell", "--kind", cell["kind"],
            "--launcher-mode", launcher_mode]
    if "op" in cell:
        argv += ["--op", cell["op"]]
    if "K" in cell:
        argv += ["--K", str(cell["K"]), "--m", str(cell["m"]),
                 "--policy", cell["policy"]]
    done = subprocess.run(argv, capture_output=True, text=True, check=False)
    if done.returncode != 0:
        raise BoundaryFailure("cell %r failed: %s"
                              % (cell, done.stderr.strip()[:400]))
    return json.loads(done.stdout)


def _run_cell(args):
    _require_launcher_mode(args.launcher_mode)
    fingerprint = _spec_fingerprint()
    if args.kind == "time-unit":
        result = _cell_time_unit(args.op)
    elif args.kind == "time-record":
        result = _cell_time_record(args.K, args.m, args.policy)
    elif args.kind == "memory":
        result = _cell_memory(args.K, args.m, args.policy)
    elif args.kind == "audit":
        result = _cell_audit()
    else:
        raise BoundaryFailure("unknown cell kind %r" % (args.kind,))
    _p1_module_table()
    _p2_self_scan()
    _p4_no_world()
    _p5_spec_unchanged(fingerprint)
    sys.stdout.write(json.dumps(result))
    return 0


def _orchestrate(args):
    _require_launcher_mode(args.launcher_mode)
    run_directory = _guard_run_directory(args.run_id)
    checks = [_p1_module_table(), _p2_self_scan(), _p4_no_world()]
    fingerprint = _spec_fingerprint()
    cells = []
    raw_rows = []
    forward = _grid()
    for order, sequence in (("forward", forward),
                            ("reversed", list(reversed(forward)))):
        for cell in sequence:
            result = _spawn(cell, args.launcher_mode)
            for row in result.pop("raw", []):
                row["order"] = order
                raw_rows.append(row)
            result["order"] = order
            cells.append(result)
    checks.append(_p5_spec_unchanged(fingerprint))
    environment = _environment_identity(args.launcher_mode)
    checks.append(_p7_schema(cells))
    checks.append(_p8_environment(environment))
    checks.append(_p10_raw_schema(raw_rows))

    os.makedirs(run_directory, exist_ok=False)
    raw_path = _p3_guard_output(os.path.join(run_directory, RAW_BASENAME))
    with open(raw_path, "w", encoding="utf-8") as handle:
        for row in raw_rows:
            handle.write(json.dumps(row, sort_keys=True,
                                    separators=(",", ":")))
            handle.write("\n")
    with open(raw_path, "rb") as handle:
        raw_digest = hashlib.sha256(handle.read()).hexdigest()

    summary = {
        "label": "NON-SCIENTIFIC SOFTWARE MEASUREMENT",
        "statement": ("software overhead only; never EBU quality, "
                      "homeostasis, service, recovery or scientific success"),
        "run_id": args.run_id,
        "environment": environment,
        "boundaries": checks,
        "raw_samples_file": RAW_BASENAME,
        "raw_samples_sha256": raw_digest,
        "raw_samples_records": len(raw_rows),
        "cells": cells,
    }
    checks.append(_p6_no_ebu(summary))
    checks.append(_p11_raw_binding(summary, raw_path))

    summary_path = _p3_guard_output(
        os.path.join(run_directory, SUMMARY_BASENAME))
    with open(summary_path, "w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=1, sort_keys=True)
        handle.write("\n")
    if not (os.path.exists(raw_path) and os.path.exists(summary_path)):
        raise BoundaryFailure(
            "both the raw-sample file and the summary are required")
    sys.stderr.write("wrote %s\nwrote %s\n" % (raw_path, summary_path))
    return 0


def _selfcheck(_args):
    _require_launcher_mode(_args.launcher_mode)
    for line in (_p1_module_table(), _p2_self_scan(), _p4_no_world(),
                 _p5_spec_unchanged(_spec_fingerprint()),
                 _p8_environment(_environment_identity(
                     _args.launcher_mode))):
        sys.stdout.write(line + "\n")
    sys.stdout.write("P3 ok: output guard rejects any path outside %s\n"
                     % OUTPUT_ROOT)
    sys.stdout.write("P9 ok: any boundary failure raises and exits non-zero\n")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="D5 micro-benchmark harness (NON-SCIENTIFIC).")
    parser.add_argument("--mode", choices=("orchestrate", "cell", "selfcheck"),
                        default="selfcheck")
    parser.add_argument("--kind", choices=("time-unit", "time-record",
                                           "memory", "audit"))
    parser.add_argument("--op", choices=UNIT_OPS)
    parser.add_argument("--K", type=int, choices=GRID_K)
    parser.add_argument("--m", type=int, choices=GRID_M)
    parser.add_argument("--policy", choices=GRID_POLICY)
    parser.add_argument("--run-id", dest="run_id", default=None,
                        help="explicit run identifier; a new run directory "
                             "is created beneath the output root and prior "
                             "output is never overwritten")
    parser.add_argument("--launcher-mode", dest="launcher_mode",
                        choices=LAUNCHER_MODES, required=True,
                        help="explicit launcher label; never inferred")
    args = parser.parse_args(argv)
    try:
        if args.mode == "cell":
            return _run_cell(args)
        if args.mode == "orchestrate":
            return _orchestrate(args)
        return _selfcheck(args)
    except BoundaryFailure as failure:
        sys.stderr.write("BOUNDARY FAILURE: %s\n" % failure)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
