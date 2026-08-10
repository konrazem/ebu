"""Official fail-closed runner for the frozen V3.0 Gate 1D-C study.

Importing this module is side-effect free: it does not inspect Git, create a
directory, write a file, print, advance model state, or execute a run.  The
single future execution must use the frozen shell command from the protocol::

    mkdir -p results/v3.0/gate1dc; set -o noclobber; \
      python3 exp_v30_gate1dc.py \
      > results/v3.0/gate1dc/v30_gate1dc_stdout.txt

The shell-created stdout file is the single-execution lock.  Preflight proves
that it is the empty regular file attached to fd 1 and that it is the only
entry in the result directory.  All integrity checks complete before
``execute_registered_study`` can call ``gate1dc_v30.run_arm``.  There is no
retry, replacement, subsetting, outcome-based rerun, or scientific option.

The runner publishes the deterministic trace first and the summary last (the
completion sentinel), both without overwrite.  It never writes MANIFEST.md:
the frozen protocol assigns manifest creation to the separately authorized
post-execution validation/finalization stage, after hashes and byte counts of
all three runner-produced artifacts can be verified.
"""
from __future__ import annotations

import ast
import gzip
import hashlib
import io
import json
import math
import os
import platform
import stat
import subprocess
import sys
import tempfile

import ebu_quote_v30 as eq
import gate1dc_v30 as dc
import service_v30 as sv


BRANCH = "v3.0-local-ebu-foundation"
PLAN_CANONICAL = "f9dd4b804a83744268bffe48d2d3861825cbc96d90aa871f348251e4108ef287"
PLAN_RAW = "91a2c42558c09051988bfebe6f0d11c0fab440340d161171afc4442c86fa30fe"
PROTOCOL_SHA256 = "3122aa673f47290bbee866feb56d16afc4540f552ed7c7b458f097ef4e44d04f"

OUTDIR = "results/v3.0/gate1dc"
MANIFEST = f"{OUTDIR}/MANIFEST.md"       # post-execution stage only
SUMMARY = f"{OUTDIR}/v30_gate1dc_summary.json"
TRACE = f"{OUTDIR}/v30_gate1dc_trace.jsonl.gz"
STDOUT = f"{OUTDIR}/v30_gate1dc_stdout.txt"

ARM_A, ARM_B, ARM_C, ARM_D, ARM_S = dc.EXEC_ARMS
PRIMARY_BASELINE_ARM = ARM_B

# Frozen identities of every authoritative and scientific source used here.
REQUIRED_SOURCE_HASHES = {
    "AGENTS.md": "ff0a468251fabfc74a5d6d705310d6d824d57f7f669adacc9785e2ca871cb635",
    "V3.0_GATE1D_C_OUTCOME_DISCRIMINATION_PROTOCOL.md": PROTOCOL_SHA256,
    "v30_gate1dc_outcome_discrimination_plan.json": PLAN_RAW,
    "gate1dc_v30.py": "6f5e86b99ae44cd13603bcb44d317cbac976dd5d2528de3732b72614b66e2ec7",
    "test_v30_gate1dc.py": "47c70e64b5793738c1beaff18cdaac045e4598edccf7b98c9f39f0c464b1e706",
    "d0_v29.py": "f7fdce8d946b44b4e0bfab9338fcd5c378796f9d14cd80323c53732e08a3bfe9",
    "p1c_v29.py": "a30c869000080b4b0235a9ba1daa517a5b0fe734ba55ac423ae3042da5940729",
    "ebu_quote_v30.py": "44a2ea282837f7613198a06a7037fb89f2f9fd99f05cedde65e0b1ba726e1b79",
    "service_v30.py": "a83bcd5e449b8804f44607e56326ec392324cdfed71260e28fdc4c48899d44e0",
}

REQUIRED_TICK_FIELDS = tuple(dict.fromkeys(
    dc.TICK_RECORD_FIELDS + (
        "x_before", "x_after", "menus", "candidate_exact_quotes",
        "request_shaping_identity", "rested", "pulse_tick",
        "transport_loss", "negative_corrections", "domain_failure",
        "reserve_crossings", "allee_crossings", "dead_sources",
        "physical_overuse", "p1c_rejections", "quote_sign_counts",
        "group_diagnostic", "ebu_pos", "ebu_neg", "quoted",
    )))

# Physical fields compared for H1/F1.  Quote/EBU accounting and the arm label
# are observational differences, not physical differences.
PHYS_TICK_FIELDS = (
    "tick", "dt", "x_before", "x_after", "u", "available",
    "active_out_edges", "menus", "selected", "threshold_diagnostics",
    "rested", "request_shaping_identity", "executed_q_acc", "delivered",
    "sigma", "budget_utilization", "service", "unmet", "demand_amount",
    "pulse_tick", "transport_loss", "negative_corrections",
    "ledger_residual", "domain_failure", "reserve_crossings",
    "allee_crossings", "dead_sources", "physical_overuse",
    "p1c_rejections", "min_source", "burden", "viability",
    "recomputation_residuals", "group_diagnostic",
)

_RANDOMNESS_MODULES = frozenset(("random", "secrets"))
_RANDOMNESS_GUARDED_SOURCES = ("gate1dc_v30.py", "exp_v30_gate1dc.py")


def _fatal(message: str):
    raise SystemExit(f"FATAL: {message}")


def _sha256(path: str) -> str:
    try:
        with open(path, "rb") as handle:
            return hashlib.sha256(handle.read()).hexdigest()
    except OSError as error:
        _fatal(f"cannot hash required source {path}: {error}")


def _assert_finite(value, path: str) -> None:
    if isinstance(value, float):
        if not math.isfinite(value):
            _fatal(f"non-finite numeric value at {path}")
    elif isinstance(value, dict):
        for key, item in value.items():
            _assert_finite(item, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            _assert_finite(item, f"{path}[{index}]")


def strict_dumps(value, **kwargs) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=True,
                      allow_nan=False, **kwargs)


def _git(*arguments: str) -> str:
    try:
        completed = subprocess.run(
            ("git",) + arguments, check=True, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except (OSError, subprocess.CalledProcessError) as error:
        detail = getattr(error, "stderr", "") or str(error)
        _fatal(f"Git check failed for {' '.join(arguments)}: {detail.strip()}")
    return completed.stdout.strip()


def _randomness_imports(path: str) -> list:
    try:
        source = open(path, "rb").read()
        tree = ast.parse(source, filename=path)
    except (OSError, SyntaxError, ValueError) as error:
        _fatal(f"cannot inspect {path} for randomness imports: {error}")
    hits = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            hits.extend(alias.name for alias in node.names
                        if alias.name.split(".")[0] in _RANDOMNESS_MODULES)
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            if root in _RANDOMNESS_MODULES:
                hits.append(node.module)
    return hits


def _validate_information_boundary() -> None:
    """Re-run the frozen decision-path AST guard inside official preflight."""
    forbidden = {
        "V_total", "service", "unmet", "demand_schedule", "pulse_ticks",
        "future", "rollout", "classification", "result", "wallet",
        "health", "price", "market", "gate1dc_tick", "run_arm",
        "bounded_step", "p1c_step",
    }
    try:
        source = open("gate1dc_v30.py", "rb").read()
        tree = ast.parse(source, filename="gate1dc_v30.py")
    except (OSError, SyntaxError, ValueError) as error:
        _fatal(f"cannot inspect the decision path: {error}")
    definitions = {node.name: node for node in tree.body
                   if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
    expected = [function.__name__ for function in dc.DECISION_PATH_FUNCS]
    if set(definitions) < set(expected):
        _fatal("decision-path function is missing from gate1dc_v30.py")
    for name in expected:
        node = definitions[name]
        names = {item.id for item in ast.walk(node)
                 if isinstance(item, ast.Name)}
        names |= {item.attr for item in ast.walk(node)
                  if isinstance(item, ast.Attribute)}
        hits = sorted(names & forbidden)
        if hits:
            _fatal(f"decision-path information-boundary violation in "
                   f"{name}: {hits}")
    selector = definitions["select_arm_S"]
    arguments = {argument.arg for argument in selector.args.args}
    if "current_demand_rate" not in arguments or "tick" in arguments:
        _fatal("arm S does not expose exactly the current-demand boundary")


def _validate_output_start(stdout_fd: int | None = None) -> None:
    """Verify the shell's exclusive stdout capture and refuse prior output."""
    if not os.path.isdir(OUTDIR):
        _fatal(f"{OUTDIR} does not exist; use the exact frozen command")
    try:
        entries = sorted(os.listdir(OUTDIR))
    except OSError as error:
        _fatal(f"cannot inspect {OUTDIR}: {error}")
    if entries != [os.path.basename(STDOUT)]:
        _fatal(f"existing result directory is not a fresh stdout capture: {entries}")
    try:
        path_stat = os.lstat(STDOUT)
    except OSError as error:
        _fatal(f"cannot inspect registered stdout artifact: {error}")
    if not stat.S_ISREG(path_stat.st_mode) or path_stat.st_nlink != 1:
        _fatal("registered stdout capture must be one regular, non-linked file")
    if path_stat.st_size != 0:
        _fatal("registered stdout artifact already contains data; refusing reuse")
    fd = sys.stdout.fileno() if stdout_fd is None else stdout_fd
    try:
        fd_stat = os.fstat(fd)
    except OSError as error:
        _fatal(f"cannot inspect stdout file descriptor: {error}")
    if (fd_stat.st_dev, fd_stat.st_ino) != (path_stat.st_dev, path_stat.st_ino):
        _fatal("fd 1 is not the registered empty stdout capture")
    for artifact in (SUMMARY, TRACE, MANIFEST):
        if os.path.lexists(artifact):
            _fatal(f"registered output artifact already exists: {artifact}")


def _validate_repository() -> dict:
    root = os.path.dirname(os.path.realpath(__file__))
    if os.path.realpath(os.getcwd()) != root:
        _fatal(f"runner must execute from repository root {root}")
    if _git("rev-parse", "--show-toplevel") != root:
        _fatal("Git top-level does not equal the runner directory")
    branch = _git("symbolic-ref", "--quiet", "--short", "HEAD")
    if branch != BRANCH:
        _fatal(f"branch {branch!r} != registered {BRANCH!r}")
    head = _git("rev-parse", "HEAD")
    remote = _git("rev-parse", f"refs/remotes/origin/{BRANCH}")
    if head != remote:
        _fatal(f"local HEAD {head} != origin/{BRANCH} {remote}")
    status_lines = [line for line in _git(
        "status", "--porcelain=v1", "--untracked-files=all").splitlines()
                    if line]
    allowed_stdout = f"?? {STDOUT}"
    unexpected = [line for line in status_lines if line != allowed_stdout]
    if unexpected or status_lines.count(allowed_stdout) != 1:
        _fatal(f"repository is not clean apart from active stdout: {status_lines}")
    for path, expected in REQUIRED_SOURCE_HASHES.items():
        tracked = _git("ls-files", "--error-unmatch", "--", path)
        if tracked != path:
            _fatal(f"required source is not tracked exactly: {path}")
        actual = _sha256(path)
        if actual != expected:
            _fatal(f"required source SHA-256 mismatch for {path}: {actual}")
    runner_hash = _sha256("exp_v30_gate1dc.py")
    tracked_runner = _git("ls-files", "--error-unmatch", "--",
                          "exp_v30_gate1dc.py")
    if tracked_runner != "exp_v30_gate1dc.py":
        _fatal("official runner is not tracked")
    return {
        "branch": branch, "execution_sha": head,
        "remote_tracking_sha": remote,
        "required_source_sha256": dict(REQUIRED_SOURCE_HASHES),
        "runner_sha256": runner_hash,
    }


def preflight() -> tuple[list, dict]:
    """Complete every integrity check before any execution function is called."""
    if len(sys.argv) != 1:
        _fatal("this runner takes no command-line options or overrides")
    _validate_output_start()
    raw = open(dc.PLAN_PATH, "rb").read()
    if hashlib.sha256(raw).hexdigest() != PLAN_RAW:
        _fatal("raw Gate 1D-C plan SHA-256 mismatch")
    plan = json.loads(raw.decode("utf-8"), parse_constant=dc._reject_nonfinite)
    if dc.plan_canonical_hash(plan) != PLAN_CANONICAL:
        _fatal("canonical Gate 1D-C plan SHA-256 mismatch")
    if dc.PLAN_RAW != PLAN_RAW or dc.PLAN_CANONICAL != PLAN_CANONICAL:
        _fatal("implementation and runner plan-lock constants disagree")
    dc.validate_plan(plan)
    dc.validate_output_contract()
    for source in _RANDOMNESS_GUARDED_SOURCES:
        hits = _randomness_imports(source)
        if hits:
            _fatal(f"{source} imports randomness: {sorted(hits)}")
    _validate_information_boundary()
    specs = dc.build_run_specs()
    expected = [
        dc.run_id(world, arm, label)
        for world in dc.WORLD_NAMES for label in dc.DT_LABELS
        for arm in dc.EXEC_ARMS
    ]
    if [spec["run_id"] for spec in specs] != expected:
        _fatal("30-run inventory or frozen ordering mismatch")
    if len(specs) != 30 or len(set(expected)) != 30:
        _fatal("run inventory is not exactly 30 unique runs")
    if dc.RUN_TICKS != 200 or len(specs) * dc.RUN_TICKS != 6000:
        _fatal("200-tick / 6000-row contract mismatch")
    if (dc.BURN_IN_TICKS, dc.MEASUREMENT_TICKS,
            dc.PERSISTENCE_WINDOW) != (50, 150, 20):
        _fatal("burn-in, measurement, or persistence window mismatch")
    for world in dc.WORLD_NAMES:
        certificate = dc.world_certificates(world)
        dts = dc.world_dts(world)
        for label, expected_r in (("conservative", 0.5),
                                  ("near_certificate", 0.9)):
            r_dt = dts[label] / certificate["binding_certificate"]
            if abs(r_dt - expected_r) > 1e-12 or r_dt > 1.0:
                _fatal(f"{world}/{label}: registered r_dt mismatch")
    repository = _validate_repository()
    return specs, repository


def _validate_tick_record(record: dict, spec: dict, tick: int) -> None:
    missing = [field for field in REQUIRED_TICK_FIELDS if field not in record]
    if missing:
        _fatal(f"{spec['run_id']} tick {tick}: missing fields {missing}")
    if record["tick"] != tick or record["arm"] != spec["arm"]:
        _fatal(f"{spec['run_id']} tick {tick}: identity/order mismatch")
    if not record["request_shaping_identity"]:
        _fatal(f"{spec['run_id']} tick {tick}: request-shaping violation")
    if spec["arm"] != ARM_A:
        for menu in record["menus"].values():
            if menu.get("menu_contract_hash") != dc.MENU_CONTRACT_HASH:
                _fatal(f"{spec['run_id']} tick {tick}: menu contract mismatch")
    if spec["arm"] == ARM_A and (record["ebu"] != 0.0
                                  or record["quoted"] != 0):
        _fatal(f"{spec['run_id']} tick {tick}: arm A settled or allocated EBU")
    _assert_finite(record, f"{spec['run_id']}[{tick}]")


def validate_run(run, spec: dict) -> None:
    if run.run_id != spec["run_id"]:
        _fatal(f"returned run_id {run.run_id!r} != {spec['run_id']!r}")
    if (run.world, run.dt_label, run.arm) != (
            spec["world"], spec["dt_label"], spec["arm"]):
        _fatal(f"{spec['run_id']}: returned identity differs from specification")
    locked = dc.PLAN["timestep"]["per_world"][run.world]
    dt_field = dc._DT_FIELD[run.dt_label]
    if run.dt != locked[dt_field]:
        _fatal(f"{run.run_id}: timestep differs from frozen plan")
    if (run.dt_certificate != locked["binding_certificate"]
            or run.certificate_kind != locked["binding_kind"]
            or run.r_dt > 1.0):
        _fatal(f"{run.run_id}: certificate identity/r_dt mismatch")
    records = run.series.get("tick_records", [])
    if len(records) != dc.RUN_TICKS:
        _fatal(f"{run.run_id}: {len(records)} records != {dc.RUN_TICKS}")
    for tick, record in enumerate(records, 1):
        _validate_tick_record(record, spec, tick)
    if run.arm == ARM_A and (run.totals["ebu"] != 0.0
                             or run.totals["quoted"] != 0):
        _fatal(f"{run.run_id}: arm A EBU/quote total is not zero")
    for key in ("service", "unmet", "demand", "ebu"):
        recomputed = math.fsum(run.series[key])
        if abs(recomputed - run.totals[key]) > sv.tol(run.totals[key]):
            _fatal(f"{run.run_id}: {key} total is not reconstructible")
    _assert_finite(run.totals, f"{run.run_id}.totals")
    _assert_finite(run.final, f"{run.run_id}.final")


def execute_registered_study(specs: list) -> list:
    """Call each frozen run exactly once and only in its registered order."""
    runs, called = [], set()
    for index, spec in enumerate(specs):
        run_identifier = spec["run_id"]
        if run_identifier in called:
            _fatal(f"duplicate execution request at index {index}: {run_identifier}")
        called.add(run_identifier)  # mark before the call: never retry on failure
        run = dc.run_arm(spec["world"], spec["arm"], spec["dt_label"],
                         ticks=dc.RUN_TICKS)
        validate_run(run, spec)
        runs.append(run)
        print(f"  {index + 1:02d}/30 {run.run_id:76s} "
              f"service {run.totals['service']:10.4f} "
              f"unmet {run.totals['unmet']:10.4f} "
              f"EBU {run.totals['ebu']:+11.4f} r_dt {run.r_dt:.1f}")
    if [run.run_id for run in runs] != [spec["run_id"] for spec in specs]:
        _fatal("executed runs differ from the frozen inventory/order")
    return runs


def _by_id(runs: list) -> dict:
    result = {run.run_id: run for run in runs}
    if len(result) != len(runs):
        _fatal("duplicate run identifiers in returned results")
    return result


def _get(by_id: dict, world: str, arm: str, label: str):
    return by_id[dc.run_id(world, arm, label)]


def _pbi_destination_totals(run, key: str) -> list:
    rows = run.series[f"{key}_by_dest"][dc.BURN_IN_TICKS:]
    n = len(run.final["x"])
    return [math.fsum(row[index] for row in rows) for index in range(n)]


def _all_destination_totals(run, key: str) -> list:
    rows = run.series[f"{key}_by_dest"]
    n = len(run.final["x"])
    return [math.fsum(row[index] for row in rows) for index in range(n)]


def _edge_switches(run) -> int:
    selected = [edge for edge in run.series["selected_edge"] if edge is not None]
    return sum(left != right for left, right in zip(selected, selected[1:]))


def _min_sigma(run):
    values = [value for record in run.series["tick_records"]
              for value in record["sigma"].values()]
    return min(values) if values else None


def _max_simultaneous_actions(run) -> int:
    return max((sum(quantity > 0.0 for quantity in record["executed_q_acc"])
                for record in run.series["tick_records"]), default=0)


def compare_bc(run_b, run_c) -> dict:
    first = None
    for tick, (left, right) in enumerate(zip(
            run_b.series["tick_records"], run_c.series["tick_records"]), 1):
        for field in PHYS_TICK_FIELDS:
            if left[field] != right[field]:
                first = f"tick {tick} field {field}"
                break
        if first:
            break
    return {
        "identical": first is None,
        "first_difference": first,
        "max_state_difference": max((
            max(abs(a - b) for a, b in zip(left["x_after"], right["x_after"]))
            for left, right in zip(run_b.series["tick_records"],
                                   run_c.series["tick_records"])), default=0.0),
    }


def run_record(run, baseline, alignment) -> dict:
    series, totals, final = run.series, run.totals, run.final
    return {
        "run_id": run.run_id, "world": run.world, "arm": run.arm,
        "dt_label": run.dt_label, "dt": run.dt,
        "dt_certificate": run.dt_certificate,
        "certificate_kind": run.certificate_kind, "r_dt": run.r_dt,
        "total_service": totals["service"], "total_unmet": totals["unmet"],
        "total_demand": totals["demand"], "ebu_total": totals["ebu"],
        "ebu_positive": totals["ebu_pos"], "ebu_negative": totals["ebu_neg"],
        "pbi_service": sv.pbi_sum(series["service"]),
        "pbi_unmet": sv.pbi_sum(series["unmet"]),
        "pbi_service_by_destination": _pbi_destination_totals(run, "service"),
        "pbi_unmet_by_destination": _pbi_destination_totals(run, "unmet"),
        "service_by_destination": _all_destination_totals(run, "service"),
        "unmet_by_destination": _all_destination_totals(run, "unmet"),
        "accepted_actions": totals["accepted"],
        "voluntary_rests": totals["rests"],
        "p1c_rejections": totals["p1c_rejected"],
        "reserve_crossings": totals["reserve_crossings"],
        "allee_crossings": totals["allee_crossings"],
        "physical_overuse": totals["overuse"],
        "negative_corrections": totals["corrections"],
        "max_ledger_residual": totals["max_ledger_residual"],
        "selected_edge_switches": _edge_switches(run),
        "max_simultaneous_actions": _max_simultaneous_actions(run),
        "min_sigma": _min_sigma(run), "final_state": list(final["x"]),
        "final_burden": final["burden"], "final_viability": final["viability"],
        "domain_failure_tick": final["domain_failure_tick"],
        "negative_state": bool(final["negative_state"]),
        "feasible_world": bool(final["feasible_world"]),
        "service_alignment_predicate": alignment,
        "per_destination_alignment": (
            dc.per_destination_alignment_predicate(run, baseline)
            if run.arm == ARM_D else None),
        "outcome_class": sv.classify_outcome(run, baseline, alignment),
    }


def _pulse_pbi_unmet(run, destination: int) -> float:
    return math.fsum(
        row[destination]
        for tick, (row, pulse) in enumerate(zip(
            run.series["unmet_by_dest"], run.series["pulse_tick"]), 1)
        if tick > dc.BURN_IN_TICKS and pulse)


def _selected_signature(run) -> list:
    return [None if record["selected"] is None else (
        record["selected"]["edge"], record["selected"]["quant_index"],
        record["selected"]["q_acc"])
            for record in run.series["tick_records"]]


def _d_total_ranking_violations(run) -> list:
    violations = []
    for record in run.series["tick_records"]:
        selected = record["selected"]
        candidates = [candidate for menu in record["menus"].values()
                      for candidate in menu["candidates"]]
        quotes = [quote for values in record["candidate_exact_quotes"].values()
                  for quote in values]
        expected_index = dc.select_arm_D(candidates, quotes)
        expected = candidates[expected_index] if expected_index is not None else None
        if selected != expected:
            violations.append(record["tick"])
    return violations


def build_summary(runs: list, repository: dict) -> dict:
    by_id = _by_id(runs)
    records = {}
    for run in runs:
        baseline = _get(by_id, run.world, ARM_B, run.dt_label)
        alignment = (sv.service_alignment_predicate(run, baseline)
                     if run.arm == ARM_D else None)
        records[run.run_id] = run_record(run, baseline, alignment)

    a_vs_b, b_vs_c, b_vs_d, s_vs, timestep = {}, {}, {}, {}, {}
    discriminator = {}
    controls = {}
    for world in dc.WORLD_NAMES:
        for label in dc.DT_LABELS:
            key = f"{world}|{label}"
            run_a, run_b, run_c, run_d, run_s = (
                _get(by_id, world, arm, label) for arm in dc.EXEC_ARMS)
            rec_a, rec_b, rec_d, rec_s = (
                records[run.run_id] for run in (run_a, run_b, run_d, run_s))
            capability = rec_a["pbi_service"] - rec_b["pbi_service"]
            a_vs_b[key] = {
                "pbi_service_A": rec_a["pbi_service"],
                "pbi_service_B": rec_b["pbi_service"],
                "capability_cost_absolute": capability,
                "capability_cost_relative": (capability / rec_a["pbi_service"]
                                             if rec_a["pbi_service"] else 0.0),
                "max_simultaneous_actions_A": rec_a["max_simultaneous_actions"],
            }
            b_vs_c[key] = compare_bc(run_b, run_c)
            b_vs_d[key] = {
                "pbi_service_B": rec_b["pbi_service"],
                "pbi_service_D": rec_d["pbi_service"],
                "service_ratio_D_over_B": (
                    rec_d["pbi_service"] / rec_b["pbi_service"]
                    if rec_b["pbi_service"] else None),
                "pbi_unmet_B_by_destination": rec_b[
                    "pbi_unmet_by_destination"],
                "pbi_unmet_D_by_destination": rec_d[
                    "pbi_unmet_by_destination"],
                "total_predicate": rec_d["service_alignment_predicate"],
                "per_destination_predicate": rec_d[
                    "per_destination_alignment"],
            }
            s_vs[key] = {
                "pbi_service_S": rec_s["pbi_service"],
                "pbi_service_B": rec_b["pbi_service"],
                "pbi_service_D": rec_d["pbi_service"],
                "pbi_unmet_S_by_destination": rec_s[
                    "pbi_unmet_by_destination"],
                "pbi_unmet_B_by_destination": rec_b[
                    "pbi_unmet_by_destination"],
                "pbi_unmet_D_by_destination": rec_d[
                    "pbi_unmet_by_destination"],
            }
            discriminator[key] = dc.discriminator_v2_channels(
                run_a, run_b, run_d)

    control_values = {
        "PC1_DC1_S_starves_dst2": lambda label: (
            records[dc.run_id("DC1_flux_lock", ARM_S, label)]
            ["pbi_unmet_by_destination"][2]
            - records[dc.run_id("DC1_flux_lock", ARM_B, label)]
            ["pbi_unmet_by_destination"][2]),
        "PC2_DC3_S_misses_pulses": lambda label: (
            _pulse_pbi_unmet(_get(by_id, "DC3_demand_pulse", ARM_S, label), 2)
            - _pulse_pbi_unmet(_get(by_id, "DC3_demand_pulse", ARM_B, label), 2)),
        "PC3_DC1_A_vs_B_capability_cost": lambda label: a_vs_b[
            f"DC1_flux_lock|{label}"]["capability_cost_absolute"],
        "PC4_DC2_A_vs_B_capacity_gap": lambda label: a_vs_b[
            f"DC2_capacity_split|{label}"]["capability_cost_absolute"],
    }
    for control, value_fn in control_values.items():
        controls[control] = {
            label: dc.positive_control_result(control, label, value_fn(label))
            for label in dc.DT_LABELS
        }

    for world in dc.WORLD_NAMES:
        cons = b_vs_d[f"{world}|conservative"]
        near = b_vs_d[f"{world}|near_certificate"]
        timestep[world] = {
            "total_alignment_failure_conservative": cons["total_predicate"][
                "is_service_alignment_failure"],
            "total_alignment_failure_near_certificate": near[
                "total_predicate"]["is_service_alignment_failure"],
            "consistent": cons["total_predicate"]["is_service_alignment_failure"]
                          == near["total_predicate"]["is_service_alignment_failure"],
        }

    comparisons = {
        "A_vs_B_capability_cost": a_vs_b,
        "B_vs_C_observational_identity": b_vs_c,
        "B_vs_D_primary_alignment": b_vs_d,
        "S_vs_B_and_D_secondary": s_vs,
        "timestep_sensitivity": timestep,
        "primary_baseline_arm": PRIMARY_BASELINE_ARM,
        "forbidden_baseline_arm": ARM_A,
    }

    group_rows = [record["group_diagnostic"] for run in runs if run.arm == ARM_A
                  for record in run.series["tick_records"]
                  if record["group_diagnostic"] is not None]
    o3 = {
        "arm_A_ticks": len(group_rows),
        "multi_action_ticks": sum(row["n_actions"] >= 2 for row in group_rows),
        "total_group_quote": math.fsum(row["group_quote"] for row in group_rows),
        "total_naive_independent_sum": math.fsum(
            row["naive_independent_sum"] for row in group_rows),
        "total_double_count": math.fsum(row["double_count"] for row in group_rows),
        "nothing_settled_or_allocated": all(
            run.totals["ebu"] == 0.0 for run in runs if run.arm == ARM_A),
        "note": "settlement-free diagnostic only; O3 remains open",
    }

    bc_bad = [key for key, value in b_vs_c.items() if not value["identical"]]
    controls_bad = [f"{control}|{label}" for control, labels in controls.items()
                    for label, value in labels.items() if value["f4_fired"]]
    multi_by_world = {world: max(
        records[dc.run_id(world, ARM_A, label)]["max_simultaneous_actions"]
        for label in dc.DT_LABELS) for world in dc.WORLD_NAMES}
    d_runs = [run for run in runs if run.arm == ARM_D]
    d_harm = [run.run_id for run in d_runs
              if run.totals["reserve_crossings"] or run.totals["allee_crossings"]
              or run.totals["overuse"] > sv.tol(0.0)]
    all_harm = [run.run_id for run in runs
                if run.totals["reserve_crossings"]
                or run.totals["allee_crossings"]
                or run.totals["overuse"] > sv.tol(0.0)]
    divergence = {f"{world}|{label}": _selected_signature(
        _get(by_id, world, ARM_B, label)) != _selected_signature(
            _get(by_id, world, ARM_D, label))
        for world in dc.WORLD_NAMES for label in dc.DT_LABELS}
    dc2_t0_divergence = {label: (
        _selected_signature(_get(by_id, "DC2_capacity_split", ARM_B, label))[0]
        != _selected_signature(_get(by_id, "DC2_capacity_split", ARM_D, label))[0])
        for label in dc.DT_LABELS}
    pinning_bad = [
        f"{run.run_id}|tick-{record['tick']}"
        for run in runs if run.world in ("DC1_flux_lock", "DC3_demand_pulse")
        for record in run.series["tick_records"] if record["x_after"][1] != 0.0]
    rank_bad = {run.run_id: _d_total_ranking_violations(run) for run in d_runs}
    rank_bad = {key: value for key, value in rank_bad.items() if value}
    plateau_pairs = []
    for world in ("DC1_flux_lock", "DC3_demand_pulse"):
        for label in dc.DT_LABELS:
            relevant = [_get(by_id, world, arm, label) for arm in dc.EXEC_ARMS]
            plateau = all(
                all(abs(service - demand) <= sv.tol(demand)
                    for record in run.series["tick_records"][dc.BURN_IN_TICKS:]
                    for service, demand in zip(record["service"],
                                               record["demand_amount"]))
                for run in relevant)
            if plateau:
                plateau_pairs.append(f"{world}|{label}")
    invariant_bad = [f"{run.run_id}|tick-{record['tick']}"
                     for run in runs for record in run.series["tick_records"]
                     if not record["request_shaping_identity"]]
    rdt_bad = [run.run_id for run in runs if run.r_dt > 1.0]
    alignment_failures = [run.run_id for run in d_runs
                          if records[run.run_id]["service_alignment_predicate"]
                          ["is_service_alignment_failure"]]
    discriminating = [key for key, value in discriminator.items()
                      if value["world_discriminating"]]

    hypotheses = {
        "H1": {"status": "supported" if not bc_bad else "not_supported",
               "evidence": {"non_identical_pairs": bc_bad}},
        "H2": {"status": "supported" if (
            discriminator["DC1_flux_lock|conservative"]["world_discriminating"]
            and discriminator["DC1_flux_lock|near_certificate"]
            ["world_discriminating"]
            and discriminator["DC2_capacity_split|conservative"]
            ["world_discriminating"]
            and discriminator["DC2_capacity_split|near_certificate"]
            ["world_discriminating"]
            and not controls["PC2_DC3_S_misses_pulses"]["conservative"]
            ["f4_fired"]
            and not controls["PC2_DC3_S_misses_pulses"]["near_certificate"]
            ["f4_fired"]) else "not_supported",
               "evidence": {"discriminating_world_timestep_pairs": discriminating,
                            "PC2": controls["PC2_DC3_S_misses_pulses"]}},
        "H3": {"status": "supported" if not controls_bad else "not_supported",
               "evidence": {"failed_positive_controls": controls_bad}},
        "H4": {"status": "supported" if (
            all(value >= 2 for value in multi_by_world.values())
            and all(not value["f4_fired"] for control in (
                "PC3_DC1_A_vs_B_capability_cost",
                "PC4_DC2_A_vs_B_capacity_gap")
                    for value in controls[control].values()))
               else "not_supported", "evidence": {
                   "max_simultaneous_actions_A": multi_by_world,
                   "PC3": controls["PC3_DC1_A_vs_B_capability_cost"],
                   "PC4": controls["PC4_DC2_A_vs_B_capacity_gap"]}},
        "H5": {"status": "open_outcome", "evidence": {
            key: {"service_D_minus_B": value["pbi_service_D"]
                  - value["pbi_service_B"],
                  "unmet_D_minus_B_by_destination": [d - b for b, d in zip(
                      value["pbi_unmet_B_by_destination"],
                      value["pbi_unmet_D_by_destination"])]}
            for key, value in b_vs_d.items()}},
        "H6": {"status": "supported" if not d_harm else "not_supported",
               "evidence": {"D_harm_runs": d_harm}},
        "H7": {"status": "supported" if all(value["consistent"]
                                                for value in timestep.values())
               else "not_supported", "evidence": timestep},
        "H8": {"status": "supported" if (
            all(dc2_t0_divergence.values()) and all(divergence.values()))
               else "partially_supported" if any(divergence.values())
               else "not_supported", "evidence": {
                   "pair_divergence": divergence,
                   "DC2_t0_divergence": dc2_t0_divergence}},
        "H9": {"status": "supported" if all(
            run.totals["unmet"] >= 0.0 and run.totals["corrections"] == 0.0
            for run in runs) else "not_supported",
               "evidence": {"total_unmet": math.fsum(
                   run.totals["unmet"] for run in runs),
                   "negative_corrections": math.fsum(
                       run.totals["corrections"] for run in runs)}},
        "H10": {"status": "supported" if not pinning_bad else "not_supported",
                "evidence": {"pinning_violations": pinning_bad[:100]}},
    }

    falsifiers = {
        "F1": {"fired": bool(bc_bad), "evidence": bc_bad},
        "F2": {"fired": bool(invariant_bad), "evidence": invariant_bad[:100]},
        "F3": {"fired": not discriminating,
               "evidence": {"discriminating_world_timestep_pairs": discriminating}},
        "F4": {"fired": bool(controls_bad), "evidence": controls_bad},
        "F5": {"fired": bool(plateau_pairs), "evidence": plateau_pairs},
        "F6": {"fired": all(value < 2 for value in multi_by_world.values()),
               "evidence": multi_by_world},
        "F7": {"fired": not any(divergence.values()), "evidence": divergence},
        "F8": {"fired": bool(all_harm), "evidence": all_harm},
        "F9": {"fired": bool(rank_bad), "evidence": rank_bad},
        "F10": {"fired": False, "evidence": {
            "note": "decision-path AST and current-demand poison probes are "
                    "mandatory pre-execution validation; locked test/source hashes "
                    "were enforced before execution"}},
        "F11": {"fired": bool(rdt_bad), "evidence": rdt_bad},
        "F12": {"fired": False, "evidence": {
            "note": "frozen plan/protocol/implementation/test hashes enforced "
                    "before execution; no runtime scientific options exist"}},
        "F13": {"fired": False, "evidence": {
            "note": "preregistration provenance is locked by protocol and Git "
                    "history; this runner is the later authorized execution layer"}},
        "F14": {"fired": bool(alignment_failures),
                "evidence": alignment_failures},
        "F15": {"fired": False, "evidence": {
            "note": "quote domains and current-tick epochs are asserted by the "
                    "locked implementation; a violation aborts before finalization"}},
        "F16": {"fired": False, "evidence": {
            "note": "all worlds are reconstructed static graphs from the locked plan"}},
    }

    counts = {}
    for record in records.values():
        outcome = record["outcome_class"]
        counts[outcome] = counts.get(outcome, 0) + 1
    return {
        "gate": "V3.0 Gate 1D-C outcome-discrimination study",
        "plan_id": dc.PLAN["plan_id"], "plan_version": dc.PLAN["plan_version"],
        "plan_canonical_hash": PLAN_CANONICAL, "plan_raw_sha256": PLAN_RAW,
        "equation_version": eq.EQUATION_VERSION,
        "implementation_sha256": {
            **repository["required_source_sha256"],
            "exp_v30_gate1dc.py": repository["runner_sha256"]},
        "execution_sha": repository["execution_sha"],
        "branch": repository["branch"], "python": platform.python_version(),
        "platform": platform.platform(),
        "registered": {
            "worlds": list(dc.WORLD_NAMES), "arms": list(dc.EXEC_ARMS),
            "dt_labels": list(dc.DT_LABELS), "total_runs": 30,
            "run_length_ticks": 200, "trace_rows": 6000,
            "burn_in_ticks": 50, "measurement_ticks": 150,
            "persistence_window_ticks": 20, "deterministic": True,
            "seed": None, "frozen_order": [run.run_id for run in runs],
        },
        "n_runs": len(runs), "runs": records, "comparisons": comparisons,
        "discriminator_v2": discriminator, "positive_controls": controls,
        "hypotheses": hypotheses, "falsifiers": falsifiers,
        "o3_aggregate_diagnostic": o3, "outcome_class_counts": counts,
        "manifest_finalization": {
            "written_by_runner": False, "path": MANIFEST,
            "required_sections": list(dc.MANIFEST_REQUIRED_SECTIONS),
            "instruction": "Create only in the separately authorized "
                           "post-execution validation stage after recomputing "
                           "SHA-256 and byte counts for summary, trace, and stdout; "
                           "do not invoke this runner again."},
        "non_claims": list(dc.PLAN["non_claims"]),
    }


def trace_rows(runs: list, repository: dict):
    for run in runs:
        for record in run.series["tick_records"]:
            yield {
                "plan_canonical_hash": PLAN_CANONICAL,
                "plan_raw_sha256": PLAN_RAW,
                "equation_version": eq.EQUATION_VERSION,
                "implementation_sha256": repository["runner_sha256"],
                "execution_sha": repository["execution_sha"],
                "run_id": run.run_id, "world": run.world, "arm": run.arm,
                "dt_label": run.dt_label, "dt": run.dt,
                "dt_certificate": run.dt_certificate,
                "certificate_kind": run.certificate_kind, "r_dt": run.r_dt,
                "tick": record["tick"], "record": record,
            }


def render_trace(rows: list) -> bytes:
    buffer = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=buffer, mtime=0) as gz:
        for row in rows:
            gz.write((strict_dumps(row, separators=(",", ":")) + "\n").encode())
    return buffer.getvalue()


def render_summary(summary: dict) -> bytes:
    return (strict_dumps(summary, indent=2) + "\n").encode()


def validate_complete_outputs_in_memory(runs: list, summary: dict,
                                        rows: list, trace_bytes: bytes,
                                        summary_bytes: bytes) -> None:
    expected_ids = [spec["run_id"] for spec in dc.build_run_specs()]
    if [run.run_id for run in runs] != expected_ids:
        _fatal("final run order differs from the frozen inventory")
    if len(rows) != 6000:
        _fatal(f"trace has {len(rows)} rows, expected 6000")
    position = 0
    for run in runs:
        for tick in range(1, dc.RUN_TICKS + 1):
            row = rows[position]
            if row["run_id"] != run.run_id or row["tick"] != tick:
                _fatal(f"trace ordering mismatch at row {position}")
            missing = [field for field in dc.TRACE_PROVENANCE_FIELDS
                       if field not in row]
            if missing:
                _fatal(f"trace row {position} missing provenance {missing}")
            position += 1
    if list(summary["runs"]) != expected_ids or summary["n_runs"] != 30:
        _fatal("summary run inventory/order mismatch")
    for block in dc.SUMMARY_REQUIRED_BLOCKS:
        if block not in summary:
            _fatal(f"summary missing required block {block}")
    if list(summary["hypotheses"]) != [f"H{i}" for i in range(1, 11)]:
        _fatal("summary H1-H10 ordering mismatch")
    if list(summary["falsifiers"]) != [f"F{i}" for i in range(1, 17)]:
        _fatal("summary F1-F16 ordering mismatch")
    if list(summary["positive_controls"]) != list(dc._PC_BOUNDS):
        _fatal("summary PC1-PC4 ordering mismatch")
    per_run = {}
    for row in rows:
        aggregate = per_run.setdefault(row["run_id"],
                                       {"service": 0.0, "unmet": 0.0,
                                        "ebu": 0.0, "ticks": 0})
        aggregate["service"] += math.fsum(row["record"]["service"])
        aggregate["unmet"] += math.fsum(row["record"]["unmet"])
        aggregate["ebu"] += row["record"]["ebu"]
        aggregate["ticks"] += 1
    for run in runs:
        aggregate = per_run[run.run_id]
        if aggregate["ticks"] != 200:
            _fatal(f"{run.run_id}: trace does not contain 200 rows")
        for key in ("service", "unmet", "ebu"):
            if abs(aggregate[key] - run.totals[key]) > sv.tol(run.totals[key]):
                _fatal(f"{run.run_id}: {key} not reconstructible from trace")
    _assert_finite(summary, "summary")
    for index, row in enumerate(rows):
        _assert_finite(row, f"trace[{index}]")
    if not trace_bytes.startswith(b"\x1f\x8b"):
        _fatal("rendered trace is not gzip")
    json.loads(summary_bytes.decode("utf-8"), parse_constant=dc._reject_nonfinite)


def _publish_new(path: str, payload: bytes) -> None:
    """Atomically publish a new file; hard-link creation refuses overwrite."""
    directory = os.path.dirname(path)
    fd, temporary = tempfile.mkstemp(dir=directory, prefix=".gate1dc_tmp_")
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temporary, path)  # atomic and fails if path already exists
        os.unlink(temporary)
    except BaseException:
        if os.path.exists(temporary):
            os.unlink(temporary)
        raise


def write_outputs(runs: list, summary: dict, rows: list) -> dict:
    """Validate fully in memory, then trace first and summary sentinel last."""
    trace_bytes = render_trace(rows)
    summary["registered_artifacts"] = {
        "trace": {"path": TRACE, "bytes": len(trace_bytes),
                  "sha256": hashlib.sha256(trace_bytes).hexdigest()},
        "summary": {"path": SUMMARY,
                    "self_hash_deferred_to_manifest": True},
        "stdout": {"path": STDOUT,
                   "hash_and_bytes_deferred_to_manifest": True},
        "manifest": {"path": MANIFEST, "written_by_runner": False},
    }
    summary_bytes = render_summary(summary)
    validate_complete_outputs_in_memory(runs, summary, rows, trace_bytes,
                                        summary_bytes)
    for path in (TRACE, SUMMARY, MANIFEST):
        if os.path.lexists(path):
            _fatal(f"refusing to overwrite registered artifact {path}")
    _publish_new(TRACE, trace_bytes)
    _publish_new(SUMMARY, summary_bytes)
    return {
        TRACE: {"sha256": hashlib.sha256(trace_bytes).hexdigest(),
                "bytes": len(trace_bytes)},
        SUMMARY: {"sha256": hashlib.sha256(summary_bytes).hexdigest(),
                  "bytes": len(summary_bytes)},
    }


def main() -> int:
    specs, repository = preflight()
    print("EBP V3.0 Gate 1D-C - outcome-discrimination study")
    print(f"  execution SHA: {repository['execution_sha']}")
    print(f"  plan canonical hash: {PLAN_CANONICAL}")
    print("  registered: 3 worlds x 2 timesteps x 5 arms = 30 runs; "
          "200 ticks each; burn-in 50; measurement 150; no seed")
    print("\n=== 30 registered runs in frozen order ===")
    runs = execute_registered_study(specs)
    summary = build_summary(runs, repository)
    rows = list(trace_rows(runs, repository))
    artifacts = write_outputs(runs, summary, rows)
    print("\n=== outcome classes ===")
    for name, count in sorted(summary["outcome_class_counts"].items()):
        print(f"  {name:42s} {count:2d}")
    print("\n=== reported falsifiers fired ===")
    fired = [key for key, value in summary["falsifiers"].items()
             if value["fired"]]
    print("  " + (", ".join(fired) if fired else "none"))
    for path, descriptor in artifacts.items():
        print(f"  wrote {path}: {descriptor['bytes']} bytes, "
              f"sha256 {descriptor['sha256']}")
    print("MANIFEST.md was not written; post-execution validation/finalization "
          "is a separate authorization boundary.")
    print("Every registered run executed exactly once; no run was retried, "
          "replaced, skipped, duplicated, filtered, or rerun.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
